"""Replay accounting, immutable targets, finite collection and native subset scheduling."""

import asyncio
import argparse
import ast
import os
import weakref
from pathlib import Path
from types import SimpleNamespace

import pytest

from miles.backends.training_utils.types import TrainStepOutcome, TrainStepOutput
from miles.rollout.base_types import RolloutFnConstructorInput, RolloutFnTrainInput
from miles.ray.rollout.rollout_data_conversion import postprocess_rollout_data
from miles.ray.rollout.train_data_conversion import split_train_data_by_dp_scheduled_raw
from miles.utils.dp_schedule import TrainParallelConfig
from miles.utils.args.custom_function import (
    CustomFunctionConfig, add_user_provided_function_arguments, resolve_custom_function_configs,
)
from miles.utils.args.schema import BaseConfig
from miles.utils.types import Sample
from miles.utils.misc import should_run_periodic_action
from tests.manual.agent_opd.swe_replay import (
    AcquisitionFailed, BankPosition, CanonicalTrajectory, ReplaySchedule, SuccessfulUpdateDriver, SweReplay,
    SweReplayConfig, acquire_bank,
    score_teacher,
)


def _typed_swe_config(protocol, *, pair="A", run_kind="formal"):
    from miles.utils.args.runtime import AllConfig
    from tests.fast.fixtures.args_fixtures import ConfigNamespace, parser_defaults, resolve_parse_boundary_configs

    # The CPU fixture validates the real post-parse schemas and transport; it does
    # not substitute a CPU parser for Megatron's GPU-dependent validation.
    smoke = run_kind == "smoke"
    budget, slots = (3, 8) if smoke else (200, 256)
    replay = SweReplayConfig(swe_cell=f"{pair}/{protocol}", swe_attempt="typed-native", swe_protocol=protocol,
                             swe_teacher_identity=pair, swe_evidence_dir="/data/ycfeng/tmp/swe-typed-native",
                             swe_run_kind=run_kind, swe_successful_updates=budget, swe_bank_slots=slots,
                             swe_bank_uses=2 if smoke else 50)
    values = parser_defaults() | {
        "requested_load": None, "raw_fsdp": None, "raw_torchtitan": None,
        "ci_enable_metrics_capture": False, "sglang_model_routers": None,
        "lora_B_init_method": "zero", "lora_sync_sends_base": False, "eval_datasets": [],
        "data_source_path": CustomFunctionConfig(path="miles.rollout.data_source.RolloutDataSource"),
        "num_rollout": budget, "rollout_batch_size": slots, "global_batch_size": slots,
        "use_dynamic_batch_size": True, "use_dynamic_global_batch_size": True, "allow_partial_train_step": True,
        "use_tis": True, "use_opd": True, "opd_type": "sglang", "opd_log_prob_top_k": 0, "opd_kl_coef": 1.0,
        "loss_type": "policy_loss", "advantage_estimator": "grpo", "normalize_advantages": False,
        "eps_clip": 0.2, "eps_clip_high": 0.28, "eps_clip_c": None, "kl_coef": 0.0,
        "use_kl_loss": False, "entropy_coef": 0.0, "use_opsm": False, "true_on_policy_mode": False,
        "calculate_per_token_loss": True, "optimizer": "adam", "adam_beta1": 0.9, "adam_beta2": 0.98,
        "adam_eps": 1e-8, "weight_decay": 0.1, "lr": 2e-6, "lr_decay_style": "constant", "lr_warmup_iters": 0,
        "custom_megatron_optimizer_step_hook_path": CustomFunctionConfig(
            path="tests.manual.agent_opd.swe_training.optimizer_step", config=replay),
        "rollout_function_path": CustomFunctionConfig(path="tests.manual.agent_opd.swe_replay.SweReplay", config=replay),
        "custom_rm_path": CustomFunctionConfig(path="tests.manual.agent_opd.swe_replay.score_teacher", config=replay),
        "custom_reward_post_process_path": CustomFunctionConfig(path="tests.manual.agent_opd.swe_replay.post_process_rewards"),
        "rm_url": "http://teacher/generate",
    }
    from tests.manual.agent_opd.swe_tis import SweTISConfig

    values["custom_tis_function_path"] = CustomFunctionConfig(path="tests.manual.agent_opd.swe_tis.apply_tis", config=SweTISConfig())
    parsed = resolve_parse_boundary_configs(ConfigNamespace(**values))
    payload = {name: value for name, value in vars(parsed).items() if name in AllConfig.model_fields}
    backend = {name: value for name, value in values.items() if name not in AllConfig.model_fields}
    payload["raw_megatron"] = parsed.raw_megatron.model_copy(update={"base_args": backend})
    return AllConfig.model_validate(payload)


@pytest.mark.parametrize("protocol", ["full", "r256"])
@pytest.mark.parametrize("pair", ["A", "B"])
@pytest.mark.parametrize("run_kind", ["formal", "smoke"])
def test_actual_typed_orchestrator_slice_preserves_training_contract(protocol, pair, run_kind):
    from miles.utils.args.custom_view import compute_custom_function_config
    from miles.utils.args.runtime import OrchestratorConfig
    from miles.utils.function_registry import load_function

    parsed = _typed_swe_config(protocol, pair=pair, run_kind=run_kind)
    orchestrator = OrchestratorConfig.slice_from(parsed)
    orchestrator = OrchestratorConfig.model_validate_json(orchestrator.model_dump_json())
    hook = orchestrator.custom_megatron_optimizer_step_hook_path
    merged = compute_custom_function_config(orchestrator, hook)
    driver = load_function(hook).training_protocol(merged)
    assert merged.custom_reward_post_process_path == parsed.custom_reward_post_process_path
    assert driver.budget == (3 if run_kind == "smoke" else 200)


def _configuration_reads(path, *names):
    tree = ast.parse(path.read_text())
    fields = set()
    selected = set()
    for definition in tree.body:
        if not isinstance(definition, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) or definition.name not in names:
            continue
        selected.add(definition.name)
        for node in ast.walk(definition):
            if isinstance(node, ast.Attribute):
                root = node.value
                if (isinstance(root, ast.Name) and root.id in {"args", "config"}) or (
                    isinstance(root, ast.Attribute) and root.attr == "args" and isinstance(root.value, ast.Name) and root.value.id == "self"
                ):
                    fields.add(node.attr)
            if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id == "name" and isinstance(node.iter, ast.Tuple):
                fields.update(value.value for value in node.iter.elts if isinstance(value, ast.Constant) and isinstance(value.value, str))
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "contract" for target in node.targets):
                fields.update(key.value for key in node.value.keys)
    assert selected == set(names), (str(path), set(names) - selected)
    return fields - {"model_copy"}


def test_all_native_swe_lifecycle_configuration_reads_have_typed_owners():
    from miles.ray.rollout.rollout_executor import _compute_rollout_function_config
    from miles.utils.args.custom_view import compute_custom_function_config
    from miles.utils.args.runtime import OrchestratorConfig, RolloutConfig, TrainerConfig
    from miles.utils.args.trainer_utils import compute_trainer_config

    root = Path(__file__).resolve().parents[2]
    parsed = _typed_swe_config("r256")
    rollout = RolloutConfig.slice_from(parsed)
    trainer = compute_trainer_config(parsed, parsed.raw_megatron.trainers[0])
    assert isinstance(trainer, TrainerConfig)
    cases = [
        (OrchestratorConfig.slice_from(parsed), parsed.custom_megatron_optimizer_step_hook_path,
         [("tests/manual/agent_opd/swe_replay.py", ("training_protocol",))]),
        (rollout, parsed.rollout_function_path,
         [("tests/manual/agent_opd/swe_replay.py", ("SweReplay", "post_process_rewards")),
          ("miles/rollout/base_types.py", ("compute_kv_cache_namespace",)),
          ("miles/rollout/inference_rollout/inference_rollout_common.py", ("GenerateState", "generate_and_rm", "compute_sampling_params"))]),
        (rollout, parsed.custom_rm_path, [("tests/manual/agent_opd/swe_replay.py", ("score_teacher", "_teacher_stage"))]),
        (rollout, parsed.custom_reward_post_process_path,
         [("tests/manual/agent_opd/swe_replay.py", ("post_process_rewards",)), ("miles/rollout/on_policy_distillation.py", ("post_process_rewards",))]),
        (trainer, parsed.custom_megatron_optimizer_step_hook_path, [("tests/manual/agent_opd/swe_training.py", ("optimizer_step",))]),
        (trainer, parsed.custom_tis_function_path, [("tests/manual/agent_opd/swe_tis.py", ("compute_tis", "apply_tis"))]),
    ]
    missing = {}
    for component, hook, sources in cases:
        restored = type(component).model_validate_json(component.model_dump_json())
        merged = (_compute_rollout_function_config(restored, hook) if isinstance(restored, RolloutConfig)
                  else compute_custom_function_config(restored, hook))
        fields = set().union(*(_configuration_reads(root / path, *names) for path, names in sources))
        absent = fields - set(dict(merged))
        if absent:
            missing[(type(component).__name__, hook.path)] = sorted(absent)
    assert not missing, missing


@pytest.mark.parametrize("name", ["rollout_function_path", "custom_rm_path", "custom_reward_post_process_path"])
@pytest.mark.parametrize("configured", [None, CustomFunctionConfig(path="wrong.native.function")])
def test_typed_protocol_rejects_missing_or_wrong_required_rollout_reward_hook(name, configured):
    from miles.utils.args.custom_view import compute_custom_function_config
    from miles.utils.args.runtime import AllConfig, OrchestratorConfig
    from miles.utils.function_registry import load_function

    parsed = _typed_swe_config("r256")
    parsed = AllConfig.model_validate(parsed.model_dump(mode="python") | {name: configured})
    sliced = OrchestratorConfig.slice_from(parsed)
    hook = sliced.custom_megatron_optimizer_step_hook_path
    with pytest.raises(ValueError, match="SWE replay requires"):
        load_function(hook).training_protocol(compute_custom_function_config(sliced, hook))


def test_typed_protocol_never_admits_shortened_budget_as_formal():
    from miles.utils.args.custom_view import compute_custom_function_config
    from miles.utils.args.runtime import AllConfig, OrchestratorConfig
    from miles.utils.function_registry import load_function

    parsed = _typed_swe_config("r256", run_kind="smoke")
    hooks = {}
    for name in ("rollout_function_path", "custom_rm_path", "custom_megatron_optimizer_step_hook_path"):
        hook = getattr(parsed, name)
        hooks[name] = hook.model_copy(update={"config": hook.config.model_copy(update={"swe_run_kind": "formal"})})
    parsed = AllConfig.model_validate(parsed.model_dump(mode="python") | hooks)
    sliced = OrchestratorConfig.slice_from(parsed)
    hook = sliced.custom_megatron_optimizer_step_hook_path
    with pytest.raises(ValueError, match="Formal SWE runs require the frozen budget"):
        load_function(hook).training_protocol(compute_custom_function_config(sliced, hook))


def sample(index):
    return Sample(index=index, prompt="prompt", tokens=[10, 20, 30], response_length=2,
                  rollout_log_probs=[-1.0, -2.0], teacher_log_probs=[-0.9, -1.8], loss_mask=[1, 0],
                  status=Sample.Status.COMPLETED, metadata={"source": {"uid": f"uid-{index}"}})


@pytest.mark.parametrize("protocol,uses,banks", [("full", 1, 200), ("r256", 50, 4)])
def test_complete_schedule_with_skips(protocol, uses, banks):
    schedule = ReplaySchedule(protocol, bank_uses=50, updates=200)
    driver = SuccessfulUpdateDriver(200)
    visits = []
    for attempted in driver.rollout_ids(0):
        before = schedule.position
        success = attempted % 7 != 0
        record = {"attempted_rollout_id": attempted, "update_successful": success,
                  "successful_updates": schedule.successful + int(success)}
        driver.accept([TrainStepOutput(TrainStepOutcome.NORMAL, optimizer_step=record)] * 2)
        schedule.commit(attempted_rollout_id=attempted, successful=success)
        if success:
            visits.append((before.bank, before.visit))
        else:
            assert schedule.position == before
    assert visits == [(bank, visit) for bank in range(banks) for visit in range(1, uses + 1)]
    assert driver.successful == schedule.successful == 200
    with pytest.raises(ValueError, match="Repeated|exhausted"):
        schedule.commit(attempted_rollout_id=attempted, successful=True)


def test_canonical_materialization_is_private_and_teacher_scoped():
    original = sample(0)
    canonical = CanonicalTrajectory.seal(0, original, "teacher-A")
    original.tokens[0] = 99
    position = BankPosition(0, 0, 1)
    first = canonical.materialize(teacher_identity="teacher-A", position=position, rollout_id=0, cell="A/r256", attempt="x")
    first.tokens[0] = 98
    first.loss_mask[0] = 0
    first.teacher_log_probs[0] = 42
    second = canonical.materialize(teacher_identity="teacher-A", position=position, rollout_id=1, cell="A/r256", attempt="x")
    assert second.tokens == [10, 20, 30]
    assert second.loss_mask == [1, 0]
    assert second.teacher_log_probs == [-0.9, -1.8]
    assert second.opd_reverse_kl is None
    with pytest.raises(ValueError, match="cross teacher"):
        canonical.materialize(teacher_identity="teacher-B", position=position, rollout_id=0, cell="B/r256", attempt="x")


@pytest.mark.parametrize("failure", [ValueError, asyncio.CancelledError])
def test_hung_late_invalid_collection_is_finite_and_slot_ordered(failure):
    async def run():
        records, late_finished = [], asyncio.Event()

        async def generate(value):
            if value.index == 0:
                try:
                    await asyncio.sleep(10)
                except asyncio.CancelledError:
                    await asyncio.sleep(0.04)
                    late_finished.set()
                    return value
            if value.index == 1:
                raise failure("invalid slot")
            await asyncio.sleep((5 - value.index) * 0.001)
            return value

        bank = await acquire_bank([[sample(i)] for i in range(6)], generate, teacher_identity="A",
                                  seconds=0.02, minimum=4, persist=records.append)
        assert [value.slot for value in bank] == [2, 3, 4, 5]
        finish_order = [value["slot"] for value in records if value["event"] == "slot_finished" and value["status"] == "completed"]
        assert finish_order == [5, 4, 3, 2]
        assert records[-1]["missing_slots"] == [0, 1]
        sealed = len(records)
        await asyncio.wait_for(late_finished.wait(), timeout=1)
        assert len(records) == sealed
        assert len(bank) == 4
        with pytest.raises(AcquisitionFailed):
            await acquire_bank([[sample(1)]], generate, teacher_identity="A", seconds=0.01, minimum=1, persist=records.append)

    asyncio.run(run())


@pytest.mark.parametrize("count", [231, 255, 256])
def test_partial_native_dp_schedule_preserves_every_uid(count):
    config = TrainParallelConfig(dp_size=4, cp_size=1, vpp_size=1, microbatch_group_size_per_vp_stage=None,
                                 independent_dp=False, supports_precomputed_schedule=True)
    args = SimpleNamespace(global_batch_size=256, use_dynamic_global_batch_size=True, use_dynamic_batch_size=True,
                           allow_partial_train_step=True, disable_rollout_trim_samples=False, max_tokens_per_gpu=32,
                           balance_by_flops=False, balance_data=True, enable_sample_ownership_checker=False,
                           multi_lora=False)
    values, metadata = postprocess_rollout_data(args, [[sample(i)] for i in range(count)], config)
    assert metadata["dynamic_global_batch_size"] == count
    data = {"tokens": [s.tokens for s in values], "sample_indices": [s.index for s in values],
            "rollout_ids": [s.index for s in values], "metadata": [{"uid": s.metadata["source"]["uid"]} for s in values],
            **metadata}
    shards = split_train_data_by_dp_scheduled_raw(args, data, train_parallel_config=config)
    consumed = [shard["metadata"][i]["uid"] for shard in shards for batch in shard["micro_batch_indices"] for i in batch]
    assert len(consumed) == count
    assert set(consumed) == {f"uid-{i}" for i in range(count)}
    assert all(shard["num_rollouts"] == [count] for shard in shards)


def test_missing_optimizer_result_is_not_success():
    with pytest.raises(ValueError, match="missing"):
        SuccessfulUpdateDriver(200).accept([TrainStepOutput(TrainStepOutcome.NORMAL)])


def test_acquisition_evidence_failure_is_soft(monkeypatch):
    from tests.manual.agent_opd import swe_replay

    async def generate(value):
        return value

    def unavailable(value):
        raise OSError("evidence disk unavailable")

    monkeypatch.setattr(swe_replay.logger, "exception", unavailable)
    bank = asyncio.run(acquire_bank([[sample(0)], [sample(1)]], generate, teacher_identity="A",
                                   seconds=1, minimum=2, persist=unavailable))
    assert [value.slot for value in bank] == [0, 1]


@pytest.mark.parametrize("protocol", ["full", "r256"])
def test_native_rollout_plugin_bank_transitions_and_success_ack(tmp_path, protocol):
    plugin = None

    class Source:
        def __init__(self):
            self.calls = 0

        def get_samples(self, count):
            assert plugin.bank == () and plugin.bank_id is None and plugin.bank_tokens == 0
            start = self.calls * count
            self.calls += 1
            return [[sample(i)] for i in range(start, start + count)]

    async def run():
        nonlocal plugin
        source = Source()
        config = SweReplayConfig(swe_cell="A/r256", swe_attempt="cpu", swe_protocol=protocol,
                                 swe_teacher_identity="A", swe_evidence_dir=str(tmp_path), swe_run_kind="smoke",
                                 swe_bank_slots=3, swe_acquisition_seconds=1)
        plugin = SweReplay(RolloutFnConstructorInput(
            args=SimpleNamespace(**config.model_dump(), namespaced_radix_cache=False), data_source=source,
        ))

        async def generate(value):
            return value

        plugin._generate = generate
        seen = {}
        attempted = 0
        while plugin.schedule.successful < 200:
            output = await plugin(RolloutFnTrainInput(rollout_id=attempted, weight_version=plugin.schedule.successful))
            index = plugin.schedule.position.bank
            membership = [group[0].metadata["source"]["uid"] for group in output.samples]
            assert membership == seen.setdefault(index, membership)
            output.samples[0][0].teacher_log_probs[0] = 88.0
            successful = attempted % 11 != 0
            previous_bank = plugin.bank
            released_payload = weakref.ref(plugin.bank[0])
            plugin.on_train_result(attempted, {"cell": "A/r256", "attempt": "cpu", "attempted_rollout_id": attempted,
                                               "update_successful": successful,
                                               "successful_updates": plugin.schedule.successful + int(successful)})
            if plugin.schedule.successful == 200 or plugin.schedule.position.bank != index:
                assert plugin.bank == () and plugin.bank_id is None and plugin.bank_tokens == 0
                del previous_bank
                assert released_payload() is None
            else:
                assert plugin.bank is previous_bank
            attempted += 1
        assert source.calls == len(seen) == (200 if protocol == "full" else 4)
        with pytest.raises(StopAsyncIteration):
            await plugin(RolloutFnTrainInput(rollout_id=attempted))

    asyncio.run(run())


@pytest.mark.parametrize("outcome", [
    "success", "request_error", "validation_error", "missing_first_score", "missing_field", "nonfinite_score", "cancelled",
])
@pytest.mark.parametrize("sink_failure", [False, True])
def test_teacher_request_and_validation_stage_receipts(tmp_path, monkeypatch, outcome, sink_failure):
    from miles.rollout import on_policy_distillation as opd
    from tests.manual.agent_opd import swe_replay

    entered = asyncio.Event()
    calls = []

    async def post(url, payload, timeout_secs):
        calls.append(payload)
        entered.set()
        if outcome == "request_error":
            raise OSError("teacher transport failed")
        if outcome == "cancelled":
            await asyncio.Event().wait()
        if outcome == "missing_field":
            return {"meta_info": {}}
        if outcome == "missing_first_score":
            return {"meta_info": {"input_token_logprobs": [[None, 20], [-2, 30]]}}
        if outcome == "nonfinite_score":
            return {"meta_info": {"input_token_logprobs": [[None, 12], [float("nan"), 20], [-2, 30]]}}
        return {"meta_info": {"input_token_logprobs": [[None, 12], [-1, 20], [-2, 99 if outcome == "validation_error" else 30]]}}

    monkeypatch.setattr(opd, "_post_json", post)
    if sink_failure:
        def unavailable(*args, **kwargs):
            raise OSError("teacher receipt disk unavailable")

        monkeypatch.setattr(swe_replay, "append_record", unavailable)
    value = sample(0)
    value.tokens = [10, 11, 12, 20, 30]
    value.metadata["swe_acquisition"] = {"deadline_at": 2e10, "slot": 0, "bank": 0}
    config = SimpleNamespace(rm_url="http://teacher/generate", sglang_router_request_timeout_secs=2,
                             swe_cell="A/r256", swe_attempt=outcome, swe_teacher_identity="A", swe_evidence_dir=str(tmp_path))

    async def run():
        task = asyncio.create_task(score_teacher(config, value))
        await entered.wait()
        if outcome == "cancelled":
            task.cancel()
        if outcome == "success":
            await task
        else:
            error = {"request_error": OSError, "cancelled": asyncio.CancelledError}.get(outcome, ValueError)
            with pytest.raises(error):
                await task

    asyncio.run(run())
    import json

    assert len(calls) == 1
    assert calls[0] == {
        "input_ids": [10, 11, 12, 20, 30],
        "sampling_params": {"temperature": 0, "max_new_tokens": 0, "skip_special_tokens": False},
        "return_logprob": True,
        "logprob_start_len": 2,
    }
    if sink_failure:
        assert not (tmp_path / "teacher_stages.jsonl").exists()
        return
    records = [json.loads(line) for line in (tmp_path / "teacher_stages.jsonl").read_text().splitlines()]
    stages = ["teacher_request"] if outcome in ("request_error", "cancelled") else ["teacher_request", "teacher_validation"]
    assert [(record["stage"], record["event"]) for record in records] == [(stage, event) for stage in stages for event in ("start", "end")]
    assert records[-1]["status"] == {"success": "success", "cancelled": "cancelled"}.get(outcome, "error")
    assert all(record["source_uid"] == "uid-0" and "deadline_at" in record for record in records)


@pytest.mark.parametrize("tokens,response_length,start,scored_items", [
    ([10, 20], 1, 0, [[None, 10], [-1.0, 20]]),
    ([10, 20, 30], 2, 0, [[None, 10], [-1.0, 20], [-2.0, 30]]),
    ([10, 11, 12, 20], 1, 2, [[None, 12], [-1.0, 20]]),
    ([10, 11, 12, 20, 30], 2, 2, [[None, 12], [-1.0, 20], [-2.0, 30]]),
])
def test_teacher_scoring_preserves_canonical_response_scores(tmp_path, monkeypatch, tokens, response_length, start, scored_items):
    from miles.rollout import on_policy_distillation as opd

    value = sample(0)
    value.tokens = tokens
    value.response_length = response_length
    value.rollout_log_probs = [-0.5] * response_length
    value.teacher_log_probs = None
    value.loss_mask = [1] * response_length
    value.kv_cache_namespace = "student-only"
    response = {"meta_info": {"input_token_logprobs": scored_items}}
    calls = []

    async def post(url, payload, timeout_secs):
        calls.append((url, payload, timeout_secs))
        return response

    monkeypatch.setattr(opd, "_post_json", post)
    args = SimpleNamespace(rm_url="http://teacher/generate", sglang_router_request_timeout_secs=2,
                           swe_cell="A/full", swe_attempt="scope", swe_teacher_identity="A", swe_evidence_dir=str(tmp_path))
    value.reward = asyncio.run(score_teacher(args, value))
    opd.post_process_rewards(SimpleNamespace(reward_key="teacher_response", opd_log_prob_top_k=0), [value])

    assert calls == [("http://teacher/generate", {
        "input_ids": tokens,
        "sampling_params": {"temperature": 0, "max_new_tokens": 0, "skip_special_tokens": False},
        "return_logprob": True,
        "logprob_start_len": start,
    }, 2)]
    assert value.reward["teacher_response"] is response
    assert len(scored_items) == response_length + 1
    expected_scores = [-1.0] if response_length == 1 else [-1.0, -2.0]
    assert value.teacher_log_probs.tolist() == expected_scores
    assert value.metadata["teacher_scoring"] == {
        "endpoint": "http://teacher/generate", "identity": "A", "scored_tokens": response_length, "token_ids_match": True,
    }
    canonical = CanonicalTrajectory.seal(0, value, "A")
    assert canonical.tokens == tuple(tokens)
    assert canonical.teacher_log_probs == tuple(expected_scores)


def test_teacher_input_field_keeps_empty_response_trim_semantics():
    from miles.rollout import on_policy_distillation as opd

    assert opd._trim_input_field({"input_token_logprobs": [[None, 10], [-1.0, 20]]}, "input_token_logprobs", 0) == []


def test_native_custom_schema_resolution_and_transport(monkeypatch):
    class Hooks(BaseConfig):
        rollout_function_path: CustomFunctionConfig
        custom_rm_path: CustomFunctionConfig
        custom_megatron_optimizer_step_hook_path: CustomFunctionConfig
        custom_tis_function_path: CustomFunctionConfig

    parser = argparse.ArgumentParser()
    for name, path in (
        ("rollout-function-path", "tests.manual.agent_opd.swe_replay.SweReplay"),
        ("custom-rm-path", "tests.manual.agent_opd.swe_replay.score_teacher"),
        ("custom-megatron-optimizer-step-hook-path", "tests.manual.agent_opd.swe_training.optimizer_step"),
        ("custom-tis-function-path", "tests.manual.agent_opd.swe_tis.apply_tis"),
    ):
        parser.add_argument(f"--{name}", default=path)
    arguments = ["--swe-cell", "A/r256", "--swe-attempt", "typed", "--swe-protocol", "r256",
                 "--swe-evidence-dir", "/data/ycfeng/tmp/swe-typed", "--swe-teacher-identity", "A"]
    monkeypatch.setattr("sys.argv", ["test", *arguments])
    add_user_provided_function_arguments(parser, config_class=Hooks)
    values = parser.parse_args(arguments)
    resolve_custom_function_configs(values, config_class=Hooks)
    hooks = Hooks.model_validate(vars(values))
    assert hooks.rollout_function_path.config == hooks.custom_rm_path.config == hooks.custom_megatron_optimizer_step_hook_path.config
    assert hooks.rollout_function_path.config.swe_successful_updates == 200
    assert Hooks.model_validate_json(hooks.model_dump_json()) == hooks


@pytest.mark.parametrize("custom", [True, False])
def test_actual_native_driver_loop_uses_success_for_cadence_and_termination(custom):
    # Execute the unchanged AST of the actual native loop with fault-injected
    # controller/Ray dependencies. This checks driver control, not GPU training.
    tree = ast.parse((Path(__file__).resolve().parents[2] / "train.py").read_text())
    loop = next(node for node in ast.walk(tree) if isinstance(node, ast.For)
                and isinstance(node.target, ast.Name) and node.target.id == "rollout_id")
    function = ast.AsyncFunctionDef(name="run", args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[],
                                    kw_defaults=[], defaults=[]), body=[loop], decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    protocol, saves, evaluations, acknowledgements = SuccessfulUpdateDriver(200), [], [], []
    native_successful = 0

    async def actor_train(rollout_id, payload):
        nonlocal native_successful
        success = rollout_id not in {0, 49, 99, 150, 202}
        native_successful += int(success)
        return [TrainStepOutput(TrainStepOutcome.NORMAL, optimizer_step={"update_successful": success,
                               "successful_updates": native_successful, "attempted_rollout_id": rollout_id})]

    async def noop(*args, **kwargs):
        pass

    async def acknowledge(rollout_id, result):
        assert result["attempted_rollout_id"] == rollout_id
        acknowledgements.append(result)

    async def save(index, **kwargs):
        saves.append(index + 1)

    async def evaluate(index, **kwargs):
        evaluations.append(index + 1)

    args = SimpleNamespace(start_rollout_id=0, num_rollout=200, use_critic=False, offload_rollout=False,
                           save_trigger_sentinel=None, save_interval=100, eval_interval=50,
                           colocate_memory_peak_device="cpu", debug_exit_after_rollout=None)
    namespace = {"args": args, "training_protocol": protocol if custom else None,
                 "rollout_ids": protocol.rollout_ids(0) if custom else range(200),
                 "inference_controller": SimpleNamespace(prepare_rollout=noop, prepare_eval=noop),
                 "rollout_executor": SimpleNamespace(get=noop, notify_train_result=acknowledge, release=noop),
                 "actor_model": SimpleNamespace(train=actor_train), "remove_rollout_data_refs": lambda *args: None,
                 "save": save, "offload_train": noop, "update_weights": noop, "num_rollout_per_epoch": None,
                 "eval_dispatcher": SimpleNamespace(dispatch=evaluate), "should_run_periodic_action": should_run_periodic_action,
                 "os": os}
    exec(compile(module, "native-train-loop", "exec"), namespace)
    asyncio.run(namespace["run"]())
    assert saves == [100, 200]
    assert evaluations == [50, 100, 150, 200]
    if custom:
        assert len(acknowledgements) == 205 and protocol.successful == native_successful == 200
    else:
        assert not acknowledgements and native_successful == 196
