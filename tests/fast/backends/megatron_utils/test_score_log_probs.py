import copy
import inspect
import random
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from tests.fast.backends.megatron_utils.score_rpc_fixtures import (
    ScoreStore,
    install_cpu_runtime,
    load_score_actor,
    make_actor,
    make_args,
    make_parallel,
    make_raw_data,
)
from tests.manual.agent_opd.inspect_qwen35 import _assemble_scores

from miles.backends.training_utils.data.context_parallel import assemble_log_prob_from_cp
from miles.backends.training_utils.metrics.train_dump import save_debug_train_data_for_rank
from miles.ray.rollout.train_data_conversion import ROLLOUT_DATA_VALUE_SPEC, split_train_data_by_dp
from miles.utils.object_store import _MooncakeStoreObjectRef
from miles.utils.replay_base import BaseReplayManager
from miles.utils.workers.rpc.common.metadata import collect_rpc_method_specs


@pytest.fixture
def scoring(monkeypatch, tmp_path):
    if dist.is_initialized():
        group = dist.new_group([dist.get_rank()], backend="gloo")
        owns_world = False
    else:
        dist.init_process_group("gloo", init_method=f"file://{tmp_path / 'gloo'}", rank=0, world_size=1)
        group = dist.group.WORLD
        owns_world = True
    store = ScoreStore()
    parallel = make_parallel(tp_group=group)
    install_cpu_runtime(monkeypatch, store, parallel)
    try:
        actor_cls, namespace = load_score_actor()
        yield SimpleNamespace(store=store, parallel=parallel, actor_cls=actor_cls, namespace=namespace)
    finally:
        if owns_world:
            dist.destroy_process_group()
        else:
            dist.destroy_process_group(group)


def _data_refs(store, args, raw, parallel):
    if args.delay_split_train_data_by_dp:
        return store.put(raw, ROLLOUT_DATA_VALUE_SPEC)
    shards = split_train_data_by_dp(
        args, raw, train_parallel_config=parallel.train_parallel_config(supports_precomputed_schedule=False)
    )
    return [store.put(shard, ROLLOUT_DATA_VALUE_SPEC) for shard in shards]


def _expected(actor, raw):
    expected = {}
    for index, tokens, response_length in zip(
        raw["sample_indices"], raw["tokens"], raw["response_lengths"], strict=True
    ):
        log_probs = torch.log_softmax(actor.model[0].weight[tokens[:-1]], dim=-1)
        scores = log_probs.gather(-1, torch.tensor(tokens[1:]).unsqueeze(-1)).squeeze(-1)
        expected[index] = scores[-response_length:]
    return expected


def _assert_input_receipts(batch, raw):
    source = {index: row for row, index in enumerate(raw["sample_indices"])}
    for row, index in enumerate(batch["sample_indices"]):
        original = source[index]
        assert batch["tokens"][row].tolist() == raw["tokens"][original]
        assert batch["loss_masks"][row].tolist() == raw["loss_masks"][original]
        assert len(batch["tokens"][row]) == batch["total_lengths"][row]
        assert len(batch["loss_masks"][row]) == batch["response_lengths"][row]
        assert batch["tokens"][row].device.type == batch["loss_masks"][row].device.type == "cpu"
        assert batch["tokens"][row].dtype == torch.int64
        assert batch["loss_masks"][row].dtype == torch.int32


@pytest.mark.parametrize("delayed", [False, True])
@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize("asleep", [False, True])
def test_native_scoring_is_read_only_and_retains_original_response_population(scoring, delayed, dynamic, asleep):
    args = make_args(delayed=delayed, dynamic=dynamic)
    actor = make_actor(scoring.actor_cls, args, asleep=asleep)
    raw = make_raw_data()
    refs = _data_refs(scoring.store, args, raw, scoring.parallel)
    stored_before = copy.deepcopy(scoring.store.values)
    params_before = {name: value.clone() for name, value in actor.model[0].named_parameters()}
    grads_before = actor.model[0].weight.grad.clone()
    optimizer_before = copy.deepcopy(actor.optimizer.state_dict())
    modes_before = [module.training for module in actor.model[0].modules()]
    timers_before = actor.model[0].config.timers
    version_before = actor._get_actor_weight_version()

    ref = actor.score_log_probs(9, refs)
    batch = scoring.store.values[ref.payload]

    assert batch["metadata"]["weight_version"] == version_before == 7
    assert batch["metadata"]["use_rollout_sampling_mask"] is False
    assert batch["metadata"]["response_layout"] == "response"
    assert set(batch) == {"log_probs", "tokens", "loss_masks", "metadata", "sample_indices", "total_lengths", "response_lengths"}
    assert scoring.store.specs[ref.payload]["log_probs"].codec == "typed_ragged"
    assert scoring.store.specs[ref.payload]["tokens"].dtype == "int64"
    assert scoring.store.specs[ref.payload]["loss_masks"].dtype == "int32"
    _assert_input_receipts(batch, raw)
    expected = _expected(actor, raw)
    for index, scores in zip(batch["sample_indices"], batch["log_probs"], strict=True):
        torch.testing.assert_close(scores, expected[index])
        assert scores.ndim == 1 and not scores.requires_grad
    assert sum(value.numel() for value in batch["log_probs"]) == 10  # Not the seven mask-selected tokens.
    assert scoring.store.reads == scoring.store.releases
    assert all(scoring.store.values[key] == value for key, value in stored_before.items())
    assert actor._asleep is asleep
    assert actor.lifecycle == (["heartbeat", "wake", "sleep", "heartbeat"] if asleep else ["heartbeat", "heartbeat"])
    assert actor._last_rollout_id == 2 and actor.opt_param_scheduler.num_steps == 19
    assert actor._get_actor_weight_version() == version_before
    for name, value in actor.model[0].named_parameters():
        torch.testing.assert_close(value, params_before[name], rtol=0, atol=0)
    torch.testing.assert_close(actor.model[0].weight.grad, grads_before, rtol=0, atol=0)
    for key, state in optimizer_before["state"].items():
        for field, value in state.items():
            torch.testing.assert_close(actor.optimizer.state_dict()["state"][key][field], value, rtol=0, atol=0)
    assert [module.training for module in actor.model[0].modules()] == modes_before
    assert actor.model[0].config.timers is timers_before


@pytest.mark.parametrize("failure", ["load", "forward", "store"])
@pytest.mark.parametrize("asleep", [False, True])
def test_failure_restores_residency_modes_rng_and_replay(scoring, monkeypatch, failure, asleep):
    args = make_args()
    actor = make_actor(scoring.actor_cls, args, asleep=asleep)
    refs = _data_refs(scoring.store, args, make_raw_data(), scoring.parallel)
    manager = BaseReplayManager()
    manager.enabled = True
    manager.stage = "replay_backward"
    manager.current = manager.create_replay()
    manager.current.top_indices_list = [torch.tensor([4])]
    manager.current.forward_index = 1
    current = manager.current
    scoring.namespace["all_replay_managers"] = [manager]
    modes_before = [module.training for module in actor.model[0].modules()]
    timers_before = actor.model[0].config.timers
    torch_state, python_state, numpy_state = torch.get_rng_state(), random.getstate(), np.random.get_state()

    def fail(*args, **kwargs):
        assert manager.stage == "fallthrough"
        manager.current = None
        actor.model[0].eval()
        actor.model[0].config.timers = None
        torch.rand(1)
        random.random()
        np.random.rand()
        raise RuntimeError(f"{failure} failed")

    if failure == "load":
        scoring.namespace["get_rollout_data"] = fail
    elif failure == "forward":
        monkeypatch.setattr(actor.model[0], "forward", fail)
    else:
        monkeypatch.setattr(scoring.store, "put", fail)
    with pytest.raises(RuntimeError, match=f"{failure} failed"):
        actor.score_log_probs(9, refs)
    assert actor._asleep is asleep
    assert scoring.store.reads == scoring.store.releases
    assert [module.training for module in actor.model[0].modules()] == modes_before
    assert actor.model[0].config.timers is timers_before
    assert manager.stage == "replay_backward" and manager.current is current
    assert current.forward_index == 1 and current.backward_index == 0
    assert current.top_indices_list[0].tolist() == [4]
    assert torch.equal(torch.get_rng_state(), torch_state) and random.getstate() == python_state
    restored_numpy = np.random.get_state()
    assert restored_numpy[0] == numpy_state[0] and np.array_equal(restored_numpy[1], numpy_state[1])
    assert restored_numpy[2:] == numpy_state[2:]
    assert actor._get_actor_weight_version() == 7 and actor._last_rollout_id == 2


def test_nonfinite_scores_are_not_sanitized_and_nonproducer_ranks_do_not_put(scoring):
    actor = make_actor(scoring.actor_cls, make_args())
    raw = dict(sample_indices=[1], total_lengths=[4], response_lengths=[3],
               tokens=[torch.tensor([1, 2, 3, 4])], loss_masks=[torch.tensor([1, 0, 1], dtype=torch.int32)])
    scores = {"score_log_probs": [torch.tensor([float("nan"), float("inf"), -float("inf")])]}
    ref = actor._store_log_prob_scores(9, raw, scores)
    values = scoring.store.values[ref.payload]["log_probs"][0]
    assert torch.isnan(values[0]) and torch.isposinf(values[1]) and torch.isneginf(values[2])
    scoring.parallel.is_pp_last_stage = False
    assert actor._store_log_prob_scores(9, raw, scores) is None
    scoring.parallel.is_pp_last_stage = True
    scoring.parallel.tp = SimpleNamespace(rank=1, size=2)
    assert actor._store_log_prob_scores(9, raw, scores) is None
    assert len(scoring.store.values) == 1


def test_actor_rpc_annotations_and_native_reference_roundtrip(scoring):
    spec = collect_rpc_method_specs(scoring.actor_cls)["score_log_probs"]
    refs = [_MooncakeStoreObjectRef(payload="first"), _MooncakeStoreObjectRef(payload="second")]
    for value in (refs[0], refs):
        query = dict(rollout_id=9, rollout_data_ref=value)
        assert spec.serializer.decode_query(spec.serializer.encode_query(query)) == query
    for result in (None, refs[0]):
        assert spec.serializer.decode_result(spec.serializer.encode_result(result)) == result
    assert spec.positional_parameter_names == ("rollout_id", "rollout_data_ref")
    assert inspect.signature(scoring.actor_cls.score_log_probs).return_annotation is not inspect.Signature.empty


def test_consumed_input_receipts_do_not_alias_native_scheduling_or_caller_values(scoring, monkeypatch):
    actor = make_actor(scoring.actor_cls, make_args(dynamic=True))
    raw = make_raw_data()
    original = copy.deepcopy(raw)
    refs = _data_refs(scoring.store, actor.args, raw, scoring.parallel)
    native_load = scoring.namespace["get_rollout_data"]
    loaded = {}

    def load(**kwargs):
        batch, lease = native_load(**kwargs)
        loaded.update(batch)
        return batch, lease

    scoring.namespace["get_rollout_data"] = load
    native_compute = actor._compute_log_prob

    def compute(*args, **kwargs):
        scores = native_compute(*args, **kwargs)
        # The receipt must describe the input just consumed, not tensors that a
        # later iterator/loss operation mutates before object-store emission.
        for tokens, mask in zip(loaded["tokens"], loaded["loss_masks"], strict=True):
            tokens.fill_(0)
            mask.fill_(0)
        return scores

    monkeypatch.setattr(actor, "_compute_log_prob", compute)
    captured = []
    native_put = scoring.store.put

    def put(value, value_spec=None):
        captured.append(value)
        return native_put(value, value_spec)

    monkeypatch.setattr(scoring.store, "put", put)
    ref = actor.score_log_probs(9, refs)
    for row in raw["tokens"] + raw["loss_masks"]:
        row[:] = [0] * len(row)
    _assert_input_receipts(captured[0], original)
    _assert_input_receipts(scoring.store.values[ref.payload], original)
    for field in ("tokens", "loss_masks"):
        assert all(saved.data_ptr() != live.data_ptr() for saved, live in zip(captured[0][field], loaded[field], strict=True))


@pytest.mark.parametrize("delayed", [False, True])
@pytest.mark.parametrize("dynamic", [False, True])
def test_eval_24_rows_with_training_batch_eight_are_preserved_and_use_native_dump(scoring, tmp_path, delayed, dynamic):
    args = make_args(delayed=delayed, dynamic=dynamic)
    args.global_batch_size = args.backend.global_batch_size = 8
    actor = make_actor(scoring.actor_cls, args)
    template = make_raw_data()
    raw = {
        key: [copy.deepcopy(values[index % 4]) for index in range(24)]
        for key, values in template.items()
    }
    raw["sample_indices"] = list(range(100, 124))
    # Training schedules count rollout groups; scoring must retain all eval rows
    # even when 12 groups do not fill another eight-group training update.
    raw["rollout_ids"] = [index // 2 for index in range(24)]
    refs = _data_refs(scoring.store, args, raw, scoring.parallel)
    native_load = scoring.namespace["get_rollout_data"]

    def load(**kwargs):
        assert kwargs["train_parallel_config"].supports_precomputed_schedule is False
        return native_load(**kwargs)

    scoring.namespace["get_rollout_data"] = load
    ref = actor.score_log_probs(9, refs)
    batch = scoring.store.values[ref.payload]
    assert len(batch["log_probs"]) == 24
    assert set(batch["sample_indices"]) == set(raw["sample_indices"])
    assert batch["metadata"]["rank"] == dist.get_rank()
    _assert_input_receipts(batch, raw)
    expected = _expected(actor, raw)
    for index, scores in zip(batch["sample_indices"], batch["log_probs"], strict=True):
        torch.testing.assert_close(scores, expected[index])

    metadata = batch["metadata"]
    args.save_debug_train_data = str(tmp_path / "score_{rollout_id}_{rank}.pt")
    save_debug_train_data_for_rank(
        args, rollout_id=9, rollout_data=batch,
        rank=metadata["rank"], cp_rank=metadata["cp_rank"], cp_size=metadata["cp_size"],
    )
    saved = torch.load(tmp_path / f"score_9_{metadata['rank']}.pt", weights_only=False)
    assert saved["rank"] == metadata["rank"] and saved["cp_size"] == metadata["cp_size"]
    assert saved["qkv_format"] == metadata["qkv_format"]
    assert saved["rollout_data"]["sample_indices"] == batch["sample_indices"]
    _assert_input_receipts(saved["rollout_data"], raw)
    source = {index: row for row, index in enumerate(raw["sample_indices"])}
    for row, index in enumerate(saved["rollout_data"]["sample_indices"]):
        original = source[index]
        sample = dict(tokens=raw["tokens"][original], response_length=raw["response_lengths"][original])
        mask = torch.tensor(raw["loss_masks"][original], dtype=torch.bool)
        assembled, _ = _assemble_scores([(saved["rollout_data"], row, "native-dump")], sample, mask)
        torch.testing.assert_close(assembled, expected[index].to(torch.float64))


def _distributed_score(rank, root):
    # One launch checks native TP collectives, CP redistribution and delayed/pre-split DP mapping.
    dist.init_process_group("gloo", init_method=f"file://{root}/gloo", rank=rank, world_size=2)
    singleton_groups = [dist.new_group([index], backend="gloo") for index in range(2)]
    for topology in ("tp", "cp", "cp_allgather", "cp_bshd", "cp_allgather_bshd", "dp"):
        with pytest.MonkeyPatch.context() as monkeypatch:
            if topology == "tp":
                parallel = make_parallel(tp_rank=rank, tp_size=2, tp_group=dist.group.WORLD)
            elif topology.startswith("cp"):
                parallel = make_parallel(
                    cp_rank=rank, cp_size=2, cp_group=dist.group.WORLD, tp_group=singleton_groups[rank]
                )
            else:
                parallel = make_parallel(dp_rank=rank, dp_size=2, tp_group=singleton_groups[rank])
            store = ScoreStore()
            install_cpu_runtime(monkeypatch, store, parallel)
            actor_cls, _ = load_score_actor()
            args = make_args(
                delayed=topology == "dp",
                allgather_cp="allgather" in topology,
                qkv_format="bshd" if "bshd" in topology else "thd",
            )
            actor = make_actor(actor_cls, args)
            actor._rank = rank
            raw = make_raw_data()
            expected = _expected(actor, raw)
            refs = _data_refs(store, args, raw, parallel)
            ref = actor.score_log_probs(9, refs)
            batch = store.values[ref.payload] if ref is not None else None
            if batch is not None:
                _assert_input_receipts(batch, raw)
            batches = [None, None]
            dist.all_gather_object(batches, batch)
            if rank == 0:
                if topology == "tp":
                    assert batches[1] is None and batches[0]["metadata"]["tp_size"] == 2
                elif topology.startswith("cp"):
                    assert all(batch["metadata"]["response_layout"] == "zigzag" for batch in batches)
                    for i, index in enumerate(batches[0]["sample_indices"]):
                        reconstructed = assemble_log_prob_from_cp(
                            {cp: batch["log_probs"][i] for cp, batch in enumerate(batches)},
                            batches[0]["total_lengths"][i],
                            batches[0]["response_lengths"][i],
                            cp_size=2,
                            qkv_format=args.qkv_format,
                            max_seq_len=batches[0]["max_seq_lens"][i] if args.qkv_format == "bshd" else None,
                        )
                        torch.testing.assert_close(reconstructed, expected[index])
                else:
                    assert {index for batch in batches for index in batch["sample_indices"]} == set(raw["sample_indices"])
                    assert [batch["metadata"]["dp_rank"] for batch in batches] == [0, 1]
                if not topology.startswith("cp"):
                    for batch in batches:
                        if batch is not None:
                            for index, scores in zip(batch["sample_indices"], batch["log_probs"], strict=True):
                                torch.testing.assert_close(scores, expected[index])
                torch.save(batches, Path(root) / f"{topology}.pt")
            assert actor._asleep and actor._get_actor_weight_version() == 7
            assert store.reads == store.releases
    dist.destroy_process_group()


def test_gloo_tp_cp_and_dp_payload_mapping(tmp_path):
    mp.spawn(_distributed_score, args=(str(tmp_path),), nprocs=2, join=True)
    assert {path.stem for path in tmp_path.glob("*.pt")} == {
        "tp", "cp", "cp_allgather", "cp_bshd", "cp_allgather_bshd", "dp"
    }
