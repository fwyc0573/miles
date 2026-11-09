"""Original-mask turn measurements, native ACK transport and CP replica selection."""

import copy
import json
from contextlib import nullcontext
from functools import partial
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest
import torch
import torch.distributed as dist

from miles.backends.training_utils.loss.objective import compute_advantages_and_returns, loss_function
from tests.ci.ci_register import register_cpu_ci
from tests.fast.dist_utils import init_gloo, run_multiprocess
from tests.fast.test_swe_tis import _attach_bank_identity, _native_case, _optimizer_context
from tests.manual.agent_opd import swe_tis, swe_training
from tests.manual.agent_opd.swe_tis import SweTISConfig, compute_tis, token_sums
from tests.manual.agent_opd.swe_training import optimizer_step

register_cpu_ci(est_time=60, suite="stage-b-cpu", labels=["precision"])


def test_variable_length_sums_use_native_rkl_and_original_mask():
    student = [torch.tensor([-1.0, -2.0, float("nan")], requires_grad=True),
               torch.tensor([-4.0], requires_grad=True)]
    # These are native estimator outputs, deliberately not student minus teacher.
    rkl = [torch.tensor([0.25, -0.5, float("nan")], requires_grad=True),
           torch.tensor([3.0], requires_grad=True)]
    masks = [torch.tensor([1, 1, 0]), torch.tensor([1])]
    behavior = [student[0].detach().clone(), student[1].detach() - 0.1]
    tis = compute_tis(student, behavior, masks, SweTISConfig())
    sums, turns = token_sums(student, rkl, masks, tis, [11, 28])
    assert [mask.sum().item() for mask in tis.masks] == [2, 0]
    torch.testing.assert_close(turns["values"], torch.tensor([[-0.25, 3, 2], [3, 4, 1]], dtype=torch.float64))
    assert turns["sample_indices"] == [11, 28]
    assert not turns["values"].requires_grad
    assert sums["kl_before_tis_numerator"].item() == 2.75
    assert sums["answer_rejected_tokens"].item() == 1


def test_native_ndarray_sample_indices_preserve_uid_mapping(tmp_path):
    batch, logits, _, log = _native_logs()
    indices = np.asarray(batch["sample_indices"], dtype=np.int64)
    result = compute_tis(batch["log_probs"], batch["rollout_log_probs"], batch["loss_masks"], SweTISConfig())
    _, log["turn_sums"] = token_sums(batch["log_probs"], batch["opd_reverse_kl"], batch["loss_masks"], result, indices)
    config, context = _optimizer_context(tmp_path, batch, log, attempt="ndarray-index")
    context["data_iterator"][0].rollout_data["sample_indices"] = indices
    context["optimizer"] = torch.optim.AdamW([logits], lr=2e-6)
    optimizer_step(config, stage="before_optimizer", update_successful=False, **context)
    record = optimizer_step(config, stage="after_optimizer", update_successful=False, **context)
    assert record["turn_sums_verified"]
    assert [row["uid"] for row in record["turn_sums"]] == ["source-0", "source-1", "source-2"]


@pytest.mark.parametrize("top_k", [0, 64])
def test_native_metadata_transports_rollout_only_estimator_config(top_k):
    from miles.ray.rollout.train_data_conversion import convert_samples_to_train_data
    from tests.fast.ray.rollout.conftest import make_rollout_config, make_sample

    args = make_rollout_config(rewards_normalization=False, use_opd=True, opd_type="sglang",
                              opd_log_prob_top_k=top_k, opd_top_k_strategy="intersection",
                              opd_reward_weight_mode="teacher_p")
    sample = make_sample(index=47)
    sample.train_metadata = {"source_uid": "canonical-source-47", "swe_bank": 6}
    original = dict(sample.train_metadata)
    # The native API permits absent train metadata on another sample. Preserve
    # that absence rather than making auxiliary provenance block conversion.
    without_metadata = make_sample(index=48)
    data = convert_samples_to_train_data(args, [sample, without_metadata], {}, None, None)
    assert data["sample_indices"] == [47, 48] and data["metadata"][1] is None
    assert sample.train_metadata == original
    assert data["metadata"][0] == {**original, "opd_estimator_config": {
        "opd_log_prob_top_k": top_k, "opd_top_k_strategy": "intersection", "opd_reward_weight_mode": "teacher_p"}}


def _native_logs(*, top_k=False):
    args, batch, logits, _ = _native_case()
    if top_k:
        batch["opd_reverse_kl"] = [torch.arange(len(s), dtype=torch.float32) + 0.2 for s in batch["log_probs"]]
    compute_advantages_and_returns(args, batch)
    # The gradient forward is intentionally different from the already-held
    # current-student scoring. NLL must still use that pre-optimizer scoring.
    training_logits = logits.roll(1, dims=-1)
    loss, _, log = loss_function(args, batch, 1, training_logits, num_rollouts=3, num_step_tokens=torch.tensor(7))
    return batch, logits, loss, log


@pytest.mark.parametrize("top_k", [False, True])
def test_successful_and_skipped_ack_macro_rows_and_durable_filtering(tmp_path, capsys, top_k):
    batch, logits, loss, log = _native_logs(top_k=top_k)
    config, context = _optimizer_context(tmp_path, batch, log, attempt=f"rows-{top_k}")
    data = context["data_iterator"][0].rollout_data
    if top_k:
        for item in data["metadata"]:
            item["opd_estimator_config"].update(opd_log_prob_top_k=64, opd_top_k_strategy="union")
    optimizer = torch.optim.AdamW([logits], lr=2e-6)
    context["optimizer"] = optimizer
    optimizer_step(config, stage="before_optimizer", update_successful=False, **context)
    skipped = optimizer_step(config, stage="after_optimizer", update_successful=False, **context)
    assert skipped["successful_updates"] == 0 and skipped["turn_sums_verified"]
    assert not (tmp_path / "updates.jsonl").exists()
    loss.backward()
    before = logits.detach().clone()
    optimizer_step(config, stage="before_optimizer", update_successful=False, **context)
    optimizer.step()
    record = optimizer_step(config, stage="after_optimizer", update_successful=True, **context)
    assert record["successful_updates"] == 1 and record["native_skipped_count"] == 1
    assert record["original_tokens"] == 7 and record["surviving_tokens"] == 3
    assert record["turn_sums_verified"] and record["unverified_turn_sums"] == []
    assert [row["uid"] for row in record["turn_sums"]] == ["source-0", "source-1", "source-2"]
    assert [row["tokens"] for row in record["turn_sums"]] == [2, 3, 2]
    expected_nll = sum(-s[m.bool()].double().sum().item() for s, m in zip(batch["log_probs"], batch["loss_masks"], strict=True))
    expected_rkl = sum(k[m.bool()].double().sum().item() for k, m in zip(batch["opd_reverse_kl"], batch["loss_masks"], strict=True))
    assert record["kl_before_tis"] == pytest.approx(expected_rkl / 7)
    assert record["nll_before_tis"] == pytest.approx(expected_nll / 7)
    assert sum(row["rkl_sum"] for row in record["turn_sums"]) == record["kl_before_tis_numerator"]
    assert sum(row["nll_sum"] for row in record["turn_sums"]) == record["nll_before_tis_numerator"]
    if top_k:
        assert record["kl_estimator"] == "native_top64_union_student_p"
    else:
        assert record["kl_estimator"].startswith("sampled_")
    assert optimizer.state[logits]["step"].item() == 1 and not torch.equal(logits, before)
    for name in ("updates.jsonl", "optimizer_attempts.jsonl"):
        for line in (tmp_path / name).read_text().splitlines():
            durable = json.loads(line)
            assert "turn_sums" not in durable and durable["nll_before_tis"] == record["nll_before_tis"]
    for line in capsys.readouterr().out.splitlines():
        if line.startswith("SWE_NATIVE_UPDATE "):
            assert "turn_sums" not in json.loads(line.removeprefix("SWE_NATIVE_UPDATE "))


@pytest.mark.parametrize("failure", ["missing", "nonfinite", "shape", "indices", "uid", "rows", "tokens", "estimator"])
def test_auxiliary_mismatches_do_not_interrupt_optimizer(tmp_path, failure):
    batch, logits, loss, log = _native_logs()
    config, context = _optimizer_context(tmp_path, batch, log, attempt=failure)
    data = context["data_iterator"][0].rollout_data
    if failure == "missing":
        log.pop("turn_sums")
    elif failure == "nonfinite":
        log["turn_sums"]["values"][0, 0] = float("nan")
    elif failure == "shape":
        log["turn_sums"]["values"] = torch.zeros(3, 2, dtype=torch.float64)
    elif failure == "indices":
        log["turn_sums"]["sample_indices"] = [0, 1, 400]
    elif failure == "uid":
        data["metadata"][1]["source_uid"] = data["metadata"][0]["source_uid"]
    elif failure == "rows":
        log["training_mask_counts"][2] += 1
    elif failure == "tokens":
        log["training_mask_counts"][0] += 1
    else:
        data["metadata"][0].pop("opd_estimator_config")
    loss.backward()
    optimizer = torch.optim.AdamW([logits], lr=2e-6)
    context["optimizer"] = optimizer
    optimizer_step(config, stage="before_optimizer", update_successful=False, **context)
    before = logits.detach().clone()
    optimizer.step()
    record = optimizer_step(config, stage="after_optimizer", update_successful=True, **context)
    assert record["successful_updates"] == 1 and not record["turn_sums_verified"]
    assert record["unverified_turn_sums"] and record["turn_sums"] == []
    assert record["kl_before_tis"] is None and record["nll_before_tis"] is None
    assert optimizer.state[logits]["step"].item() == 1 and not torch.equal(logits, before)


def test_tis_measurement_exception_is_soft_and_does_not_change_masks():
    from tests.fast.backends.training_utils.loss.loss_test_utils import make_parallel_state

    make_parallel_state()
    config = SimpleNamespace(qkv_format="thd", **SweTISConfig().model_dump())
    kwargs = dict(pg_loss=torch.ones(2, requires_grad=True), train_log_probs=[torch.zeros(2)],
                  rollout_log_probs=[torch.zeros(2)], teacher_log_probs=None, opd_reverse_kl=[torch.ones(2)],
                  sample_indices=[8], loss_masks=[torch.ones(2)], total_lengths=[4], response_lengths=[2])
    with patch.object(swe_tis, "token_sums", side_effect=RuntimeError("auxiliary measurement unavailable")):
        loss, masks, metrics = swe_tis.apply_tis(config, **kwargs)
    assert masks[0].tolist() == [1, 1] and loss.tolist() == [1, 1]
    assert "auxiliary measurement unavailable" in metrics["turn_sums"]["error"]


def _gloo_cp_tp_pp(rank, world_size, port, *, directory):
    init_gloo(rank, world_size, port=port)
    torch.set_num_threads(1)
    from miles.backends.training_utils.parallel import GroupInfo, ParallelState, set_parallel_state

    cp_rank, tp_rank, pp_rank = rank % 2, (rank // 2) % 2, rank // 4
    trivial = GroupInfo(rank=0, size=1, group=None)
    set_parallel_state(ParallelState(intra_dp=trivial, intra_dp_cp=trivial,
                                    cp=GroupInfo(rank=cp_rank, size=2, group=None),
                                    tp=GroupInfo(rank=tp_rank, size=2, group=None),
                                    pp=GroupInfo(rank=pp_rank, size=2, group=None),
                                    ep=trivial, etp=trivial, indep_dp=trivial, is_pp_last_stage=pp_rank == 1))
    data = {"num_microbatches": [2], "metadata": [{"swe_successful_before": 0, "swe_bank": 0, "swe_bank_visit": 1,
             "generation_weight_versions": [], "current_weight_version": 0,
             "swe_actual_bank_turns": 2, "swe_original_bank_tokens": 6}]}
    # Native scheduling can reorder a shard; output must restore source index order.
    _attach_bank_identity(data, [30, 10])
    partials = [[1, 4, 2], [3, 5, 1]] if cp_rank == 0 else [[0, 0, 0], [-1, 8, 3]]
    logs = [{"turn_sums": {"sample_indices": [index], "values": torch.tensor([row], dtype=torch.float64)},
             "training_mask_counts": torch.tensor([int(row[2]), int(row[2] > 0), 1], dtype=torch.int64)}
            for index, row in zip([10, 30], partials, strict=True)]
    model = torch.nn.Linear(2, 2)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-6)
    config = SimpleNamespace(swe_evidence_dir=directory, swe_cell="A/full", swe_attempt="cp-tp-pp",
                             swe_teacher_identity="A", swe_run_kind="cpu", swe_protocol="full")
    context = dict(rollout_id=0, step_id=0, data_iterator=[SimpleNamespace(rollout_data=data)],
                   model=[model], optimizer=optimizer, losses_reduced=logs)
    with patch.object(dist, "all_gather_object", wraps=dist.all_gather_object) as exchange:
        optimizer_step(config, stage="before_optimizer", update_successful=False, **context)
        assert exchange.call_count == 1
    model.weight.sum().backward()
    optimizer.step()
    record = optimizer_step(config, stage="after_optimizer", update_successful=True, **context)
    assert record["turn_sums_verified"] and record["original_tokens"] == 6 and record["actual_turns"] == 2
    assert record["kl_before_tis"] == 0.5 and record["nll_before_tis"] == pytest.approx(17 / 6)
    assert record["turn_sums"] == [{"uid": "source-10", "rkl_sum": 1, "nll_sum": 4, "tokens": 2},
                                   {"uid": "source-30", "rkl_sum": 2, "nll_sum": 13, "tokens": 4}]
    acknowledgements = [None] * world_size
    dist.all_gather_object(acknowledgements, record)
    assert all(item == record for item in acknowledgements)
    # A malformed auxiliary payload on only one contributing CP rank must not
    # cause rank-divergent collective order. The second real step still succeeds.
    for item in data["metadata"]:
        item["swe_successful_before"] = 1
    if rank == 4:
        logs[0]["turn_sums"] = {"error": "rank-local sum exception"}
        logs[0]["token_sums"] = {"kl_before_tis_numerator": torch.empty(0)}
    context["rollout_id"] = 1
    optimizer.zero_grad()
    with (patch.object(swe_training, "_add_token_sums", side_effect=RuntimeError("rank-local diagnostics unavailable"))
          if rank == 4 else nullcontext()):
        with patch.object(dist, "all_gather_object", wraps=dist.all_gather_object) as exchange:
            optimizer_step(config, stage="before_optimizer", update_successful=False, **context)
            assert exchange.call_count == 1
    model.weight.sum().backward()
    optimizer.step()
    record = optimizer_step(config, stage="after_optimizer", update_successful=True, **context)
    assert record["successful_updates"] == 2 and not record["turn_sums_verified"]
    assert "rank-local sum exception" in record["unverified_turn_sums"][0]
    assert optimizer.state[model.weight]["step"].item() == 2
    dist.destroy_process_group()


def test_two_cp_partials_one_tp_pp_replica_and_rank_local_failure(tmp_path):
    run_multiprocess(partial(_gloo_cp_tp_pp, directory=str(tmp_path)), world_size=8)


@pytest.mark.parametrize("failure", ["missing_cp", "duplicate_replica", "cp_uid", "nonfinite_macro"])
def test_merged_partial_consistency(failure):
    config = {"opd_log_prob_top_k": 0}
    label = swe_training._estimator_label(config)
    payload = {"bank": {0: "uid"}, "partials": {0: [1.0, 2.0, 1.0]}, "cp_rank": 0, "cp_size": 2, "estimator": label}
    second = copy.deepcopy(payload)
    second["cp_rank"] = 1
    payloads = [payload, second]
    if failure == "missing_cp":
        payloads.pop()
    elif failure == "duplicate_replica":
        second["cp_rank"] = 0
    elif failure == "cp_uid":
        second["bank"][0] = "wrong"
    else:
        payload["partials"][0][0] = second["partials"][0][0] = 1e308
    counts = {"original_tokens": 2, "actual_turns": 1}
    metadata = {"cp_size": 2, "swe_actual_bank_turns": 1, "swe_original_bank_tokens": 2}
    with pytest.raises(ValueError):
        swe_training._merge_turn_sums(payloads, counts, metadata)
