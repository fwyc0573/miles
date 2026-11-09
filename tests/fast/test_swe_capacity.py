"""Saved-bank acquisition preserves the real replay and native CLI contracts."""

import argparse
import asyncio
import copy
import json
import shlex
from pathlib import Path
from types import SimpleNamespace

import pytest

from miles.rollout.base_types import RolloutFnConstructorInput, RolloutFnTrainInput
from miles.utils.args.custom_function import resolve_custom_function_configs
from miles.utils.types import Sample, WeightVersionsPerCall, WeightVersionSpan
from tests.manual.agent_opd import probe_swe_capacity, run_swe_opd, swe_replay, swe_training


def _sample(slot):
    return Sample(index=slot, group_index=slot, prompt=f"original prompt {slot}", tokens=[11, 22, 33, 44],
                  response_length=2, loss_mask=[1, 0], rollout_log_probs=[-1.25, -2.5],
                  teacher_log_probs=[-1.0, -2.0], reward={"reward": 0.0},
                  status=Sample.Status.TRUNCATED if slot % 2 else Sample.Status.COMPLETED,
                  weight_versions=[WeightVersionsPerCall(spans=[WeightVersionSpan("0", 2, 4)],
                                                         prefill_spans=[WeightVersionSpan("0", 0, 2)],
                                                         output_start=2, prompt_tokens=2)],
                  metadata={"source": {"uid": f"original-{slot}", "prompt_token_count": 2},
                            "teacher_scoring": {"identity": "teacher-A", "endpoint": "original-teacher"},
                            "swe_sampling_seed": 1729,
                            "swe_acquisition": {"bank": 0, "slot": slot, "started_at": 100, "deadline_at": 1900}})


def _write_bank(path, count=256):
    samples = [_sample(slot) for slot in range(count)]
    records = [{"event": "acquisition_start", "started_at": 100, "deadline_at": 1900,
                "slots": [{"slot": sample.index, "source_uid": sample.metadata["source"]["uid"],
                           "sample_index": sample.index} for sample in samples]}]
    records += [{"event": "slot_finished", "slot": sample.index, "source_uid": sample.metadata["source"]["uid"],
                 "status": "completed", "error": None, "ended_at": 1450, "sample": sample.to_dict()}
                for sample in reversed(samples)]
    records += [{"event": "acquisition_sealed", "actual_turns": count, "membership": list(range(count)),
                 "missing_slots": [], "pending_slots": [], "ended_at": 1450}]
    path.write_text("".join(json.dumps(record) + "\n" for record in records))
    return samples, records


def _config(tmp_path, **updates):
    values = swe_replay.SweReplayConfig(swe_cell="A/r256", swe_attempt="saved-capacity", swe_protocol="r256",
                                       swe_evidence_dir=str(tmp_path / "new-evidence"), swe_teacher_identity="teacher-A",
                                       swe_run_kind="smoke", swe_bank_uses=2, swe_successful_updates=2).model_dump()
    return SimpleNamespace(**(values | {"swe_saved_bank_path": str(tmp_path / "original-bank.jsonl"),
                                       "namespaced_radix_cache": False} | updates))


def test_two_native_visits_and_skip_preserve_original_payload(tmp_path):
    originals, _ = _write_bank(tmp_path / "original-bank.jsonl")

    class Source:
        calls = 0

        def get_samples(self, count):
            self.calls += 1
            assert count == 256
            return [[Sample(index=s.index, prompt=s.prompt, metadata={"source": copy.deepcopy(s.metadata["source"])})]
                    for s in originals]

    async def run():
        source = Source()
        plugin = probe_swe_capacity.CapacityReplay(RolloutFnConstructorInput(args=_config(tmp_path), data_source=source))
        assert type(plugin).on_train_result is swe_replay.SweReplay.on_train_result
        assert type(plugin).load is swe_replay.SweReplay.load
        seen = []
        for attempted, success, visit in [(0, False, 1), (1, True, 1), (2, True, 2)]:
            output = await plugin(RolloutFnTrainInput(rollout_id=attempted, weight_version=attempted))
            assert plugin.native_state is None  # No GenerateState, student generation or teacher request.
            assert not plugin._saved_slots  # No second cache retains the original large payload.
            for original, (actual,) in zip(originals, output.samples, strict=True):
                for field in ("tokens", "response_length", "loss_mask", "rollout_log_probs", "teacher_log_probs", "status", "metadata"):
                    assert getattr(actual, field) == getattr(original, field)
                assert [call.to_dict() for call in actual.weight_versions] == [call.to_dict() for call in original.weight_versions]
                assert actual.train_metadata["swe_bank_visit"] == visit
                assert actual.train_metadata["current_weight_version"] == attempted
                assert actual.train_metadata["source_uid"] == original.metadata["source"]["uid"]
                assert actual.opd_reverse_kl is None
            assert not seen or output.samples[0][0] is not seen[-1]
            seen.append(output.samples[0][0])
            output.samples[0][0].tokens[0] = -99
            output.samples[0][0].loss_mask[0] = 0
            output.samples[0][0].teacher_log_probs[0] = 88
            output.samples[0][0].weight_versions[0].spans.clear()
            plugin.on_train_result(attempted, {"cell": "A/r256", "attempt": "saved-capacity", "attempted_rollout_id": attempted,
                                               "update_successful": success,
                                               "successful_updates": plugin.schedule.successful + int(success)})
        assert source.calls == 1 and plugin.schedule.successful == 2
        assert plugin.bank == () and plugin.bank_tokens == 0 and plugin.pending_rollout is None
        with pytest.raises(StopAsyncIteration):
            await plugin(RolloutFnTrainInput(rollout_id=3))

    asyncio.run(run())


@pytest.mark.parametrize("changes", [{"swe_run_kind": "formal"}, {"swe_successful_updates": 200}, {"swe_protocol": "full"}])
def test_formal_or_other_schedule_fails_before_reading_bank(tmp_path, changes):
    with pytest.raises(ValueError, match="smoke-only|one 256-turn"):
        probe_swe_capacity.CapacityReplay(RolloutFnConstructorInput(args=_config(tmp_path, **changes), data_source=None))


def test_original_bank_cannot_be_the_new_evidence_file(tmp_path):
    with pytest.raises(ValueError, match="must not append"):
        probe_swe_capacity.CapacityReplay(RolloutFnConstructorInput(
            args=_config(tmp_path, swe_evidence_dir=str(tmp_path), swe_saved_bank_path=str(tmp_path / "bank_0.jsonl")),
            data_source=None,
        ))


def test_source_mismatch_cannot_silently_train_a_255_turn_subset(tmp_path):
    originals, _ = _write_bank(tmp_path / "original-bank.jsonl")

    class Source:
        def get_samples(self, count):
            candidates = [[Sample(index=s.index, prompt=s.prompt, metadata={"source": copy.deepcopy(s.metadata["source"])})]
                          for s in originals]
            candidates[0][0].metadata["source"]["uid"] = "different-source"
            return candidates

    async def run():
        plugin = probe_swe_capacity.CapacityReplay(RolloutFnConstructorInput(args=_config(tmp_path), data_source=Source()))
        with pytest.raises(ValueError, match="complete original saved bank"):
            await plugin(RolloutFnTrainInput(rollout_id=0))
        assert plugin.schedule.successful == 0

    asyncio.run(run())


@pytest.mark.parametrize("invalid", ["teacher", "missing_seal", "membership", "mask", "source", "status"])
def test_original_teacher_identity_and_seal_are_mandatory(tmp_path, invalid):
    path = tmp_path / "bank.jsonl"
    _, records = _write_bank(path, count=2)
    if invalid == "teacher":
        records[1]["sample"]["metadata"]["teacher_scoring"]["identity"] = "teacher-B"
    elif invalid == "missing_seal":
        records.pop()
    elif invalid == "membership":
        records[-1]["membership"] = [1, 0]
    elif invalid == "mask":
        records[1]["sample"]["loss_mask"] = [0, 0]
    elif invalid == "source":
        records[0]["slots"][0]["source_uid"] = "different-source"
    else:
        records[1]["sample"]["status"] = "aborted"
    path.write_text("".join(json.dumps(record) + "\n" for record in records))
    with pytest.raises(ValueError):
        probe_swe_capacity.read_saved_bank(path, teacher_identity="teacher-A", slots=2)


def test_optimizer_hook_is_only_a_native_delegate(monkeypatch):
    calls = []
    monkeypatch.setattr(swe_training, "optimizer_step", lambda *args, **kwargs: calls.append((args, kwargs)) or "native-ack")
    assert probe_swe_capacity.optimizer_step("config", stage="after_optimizer", update_successful=False) == "native-ack"
    assert calls == [(("config",), {"stage": "after_optimizer", "update_successful": False})]


def test_combined_native_hook_registration_uses_real_generated_arguments(tmp_path, monkeypatch):
    from miles.utils.arguments import get_miles_extra_args_provider

    config = json.loads((Path(__file__).resolve().parents[2] / "task_memory/task_2026-11-08_qwen35_swe_full_r256/capacity_smoke_config.json").read_text())
    config["protocol"] = "r256"
    config.update(prompt_tokens=114688, response_tokens=16384)
    arguments = shlex.split(run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "cpu-cli"))
    for field, value in {
        "--rollout-function-path": "tests.manual.agent_opd.probe_swe_capacity.CapacityReplay",
        "--custom-megatron-optimizer-step-hook-path": "tests.manual.agent_opd.probe_swe_capacity.optimizer_step",
    }.items():
        arguments[arguments.index(field) + 1] = value
    arguments += ["--swe-saved-bank-path", str(tmp_path / "bank_0.jsonl")]
    monkeypatch.setattr("sys.argv", ["train.py", *arguments])
    parser = argparse.ArgumentParser()
    get_miles_extra_args_provider()(parser)
    parsed, backend = parser.parse_known_args(arguments)
    assert "--swe-saved-bank-path" not in backend
    resolve_custom_function_configs(parsed)
    assert parsed.rollout_function_path.config == probe_swe_capacity.SavedBankConfig(swe_saved_bank_path=str(tmp_path / "bank_0.jsonl"))
    assert parsed.custom_rm_path.config == parsed.custom_megatron_optimizer_step_hook_path.config
    assert parsed.custom_rm_path.config.swe_successful_updates == parsed.custom_rm_path.config.swe_bank_uses == 2
    assert parsed.load_debug_rollout_data is None and parsed.colocate and parsed.offload_rollout and parsed.offload_train
    assert type(parsed.rollout_function_path).model_validate_json(parsed.rollout_function_path.model_dump_json()) == parsed.rollout_function_path
    actions = [option for action in parser._actions for option in action.option_strings]
    assert len(actions) == len(set(actions))

    from miles.ray.rollout.rollout_executor import _compute_rollout_function_config
    from miles.utils.args.custom_view import compute_custom_function_config
    from miles.utils.args.runtime import AllConfig, OrchestratorConfig, RolloutConfig
    from tests.fast.test_swe_replay import _typed_swe_config

    # parser_defaults() is cached. Build that fixture with a neutral argv, not
    # this smoke's transient custom-hook flags/defaults.
    monkeypatch.setattr("sys.argv", ["test"])
    typed = _typed_swe_config("r256", run_kind="smoke")
    typed = AllConfig.model_validate(typed.model_dump(mode="python") | {
        "num_rollout": 2, "rollout_batch_size": 256, "global_batch_size": 256,
        **{name: getattr(parsed, name) for name in ("rollout_function_path", "custom_rm_path", "custom_megatron_optimizer_step_hook_path")},
    })
    rollout = RolloutConfig.slice_from(typed)
    rollout = RolloutConfig.model_validate_json(rollout.model_dump_json())
    merged = _compute_rollout_function_config(rollout, rollout.rollout_function_path)
    assert merged.swe_saved_bank_path == str(tmp_path / "bank_0.jsonl")
    assert merged.swe_bank_slots == 256 and merged.swe_successful_updates == merged.swe_bank_uses == 2
    orchestrator = OrchestratorConfig.slice_from(typed)
    hook = orchestrator.custom_megatron_optimizer_step_hook_path
    driver = probe_swe_capacity.training_protocol(compute_custom_function_config(orchestrator, hook))
    assert driver.budget == 2
