"""Real SWE rollout/ACK profile integration, native typed transport and permanent soft-gate isolation."""

import argparse
import asyncio
import copy
import json
import logging
from types import SimpleNamespace

import pytest

from miles.backends.training_utils.types import TrainStepOutcome, TrainStepOutput
from miles.rollout.base_types import RolloutFnConstructorInput, RolloutFnTrainInput
from miles.utils.types import Sample
from tests.fast.test_swe_replay import _typed_swe_config
from tests.manual.agent_opd import distillation_profile, swe_replay
from tests.manual.agent_opd.distillation_profile import DistillationProfile
from tests.manual.agent_opd.swe_replay import SuccessfulUpdateDriver, SweReplay, SweReplayConfig


def _sample(index, group_id, turn, tokens=1):
    return Sample(
        index=index, prompt="prompt", tokens=[10, 20, 30], response_length=2,
        rollout_log_probs=[-1.0, -2.0], teacher_log_probs=[-0.9, -1.8], loss_mask=[1, tokens - 1],
        status=Sample.Status.COMPLETED,
        metadata={"source": {"uid": f"uid-{index}", "group_id": group_id, "assistant_turn_ordinal": turn}},
    )


class _Source:
    def __init__(self):
        self.calls = 0
        self.finished_conversations = ()

    def get_samples(self, count):
        assert count == 3
        start = self.calls * count
        self.calls += 1
        if self.calls == 1:
            # slot 1 fails natively. g0's last drawn turn and untrained gX's last turn were
            # rejected for length; only the source's bank-boundary report knows they finished.
            self.finished_conversations = ("g0", "gX")
            values = [_sample(start, "g1", 1, 2), _sample(start + 1, "failed", 1), _sample(start + 2, "g0", 1)]
        else:
            self.finished_conversations = ("g1",)
            values = [_sample(start, "g1", self.calls, 2), _sample(start + 1, "failed", self.calls),
                      _sample(start + 2, "new", self.calls)]
        return [[value] for value in values]


def _plugin(tmp_path, *, source=None, protocol="full", uses=50, enabled=True):
    config = SweReplayConfig(
        swe_cell=f"A/{protocol}", swe_attempt="cpu", swe_protocol=protocol,
        swe_evidence_dir=str(tmp_path), swe_teacher_identity="teacher", swe_run_kind="smoke",
        swe_bank_slots=3, swe_bank_min_fraction=0.5, swe_acquisition_seconds=1, swe_bank_uses=uses,
        swe_successful_updates=4, swe_profile_enabled=enabled, swe_profile_trend_window=1,
        swe_profile_baseline_updates=2, swe_profile_baseline_turns=2,
    )
    plugin = SweReplay(RolloutFnConstructorInput(
        args=SimpleNamespace(**config.model_dump(), namespaced_radix_cache=False), data_source=source or _Source(),
    ))
    generated = []

    async def generate(value):
        generated.append(value.index)
        if value.index % 3 == 1:
            raise ValueError("injected native slot failure")
        return value

    plugin._generate = generate
    plugin.generated = generated
    return plugin


def _ack(plugin, rollout_id, successful=True):
    rows = [
        {"uid": json.loads(trajectory.sample_json)["metadata"]["source"]["uid"],
         "rkl_sum": 2.0 / (plugin.schedule.successful + 1), "nll_sum": 4.0,
         "tokens": sum(trajectory.original_mask)} for trajectory in reversed(plugin.bank)
    ]
    return {
        "cell": plugin.args.swe_cell, "attempt": "cpu", "attempted_rollout_id": rollout_id,
        "update_successful": successful, "successful_updates": plugin.schedule.successful + int(successful),
        "bank": plugin.schedule.position.bank, "bank_visit": plugin.schedule.position.visit,
        "protocol": plugin.args.swe_protocol, "teacher_identity": "teacher",
        "bank_membership_verified": True, "actual_turns": len(plugin.bank), "original_tokens": plugin.bank_tokens,
        "expected_bank_turns": len(plugin.bank), "expected_bank_tokens": plugin.bank_tokens,
        "turn_sums": rows, "turn_sums_verified": True, "unverified_turn_sums": [],
        "kl_estimator": "native-test-estimator", "kl_before_tis": sum(row["rkl_sum"] for row in rows) / plugin.bank_tokens,
        "nll_before_tis": sum(row["nll_sum"] for row in rows) / plugin.bank_tokens,
    }


def _files(plugin):
    directory = plugin.directory / "distillation_profile"
    return {path.name: path.read_bytes() for path in directory.iterdir() if path.is_file()}


def test_real_skipped_ack_then_success_retains_finished_bank_and_rebuilds(tmp_path):
    plugin = _plugin(tmp_path)
    driver = SuccessfulUpdateDriver(4)

    async def run():
        await plugin(RolloutFnTrainInput(rollout_id=0, weight_version=0))
        bank = plugin.bank
        record = _ack(plugin, 0, False)
        record.update(turn_sums=[], turn_sums_verified=False, unverified_turn_sums=["skipped diagnostic failure"])
        plugin.on_train_result(0, driver.accept([TrainStepOutput(TrainStepOutcome.NORMAL, optimizer_step=record)]))
        assert plugin.bank is bank and plugin.profile_finished == ("g0", "gX")
        assert plugin.profile.latest_update == driver.successful == 0
        assert plugin.profile.unverified_from is None and _files(plugin) == {}
        # Deliberately mutate the source report: successful ACK must use the captured bank boundary.
        plugin.source.finished_conversations = ()
        await plugin(RolloutFnTrainInput(rollout_id=1, weight_version=0))
        assert plugin.bank is bank and len(plugin.generated) == 3
        record = _ack(plugin, 1)
        original = copy.deepcopy(record)
        plugin.on_train_result(1, driver.accept([TrainStepOutput(TrainStepOutcome.NORMAL, optimizer_step=record)]))
        assert record == original  # no duplicated rows or profile state in native ACKs
        assert plugin.bank == () and plugin.profile_finished == ()
        assert plugin.profile.latest_verified_update == plugin.schedule.successful == driver.successful == 1
        profile = plugin.profile
        assert profile.conversation_id("g1") == 0 and profile.conversation_id("g0") == 1
        assert profile.conversation_id("failed") is None and profile.conversation_id("gX") is None
        assert profile.conversation(0).alive is True and profile.conversation(1).alive is False
        assert profile.update(1).rkl == 4 / 3 and profile.update(1).nll == 8 / 3
        assert profile.conversation(0).latest.rkl == 1 and profile.cell(0, 1).replay_num == 0
        assert profile.rkl_trend(1) is None
        for attempted in range(2, 5):
            await plugin(RolloutFnTrainInput(rollout_id=attempted, weight_version=driver.successful))
            record = _ack(plugin, attempted)
            plugin.on_train_result(attempted, driver.accept([TrainStepOutput(TrainStepOutcome.NORMAL, optimizer_step=record)]))
        assert profile.conversation(0).alive is False
        assert profile.baseline == 1 and profile.conversation(0).baseline == 0.75
        assert profile.remaining_gap(1) == 4 / 3
        assert profile.conversation_remaining_gap(0, 1) == 1 / 0.75
        assert profile.conversation_run_relative_gap(0, 1) == 1
        rebuilt = DistillationProfile.rebuild(profile.directory)
        assert rebuilt.summary() == profile.summary()
        assert rebuilt.latest_verified_update == driver.successful == plugin.schedule.successful == 4
        assert rebuilt.conversation_states(1) == profile.conversation_states(1)
        assert rebuilt.conversation_entry(0, 1) == profile.conversation_entry(0, 1)
        observations = [json.loads(line) for line in _files(plugin)["observations.jsonl"].splitlines()]
        assert [row["update_id"] for row in observations] == [1, 2, 3, 4]
        assert sum(len(row["rows"]) for row in observations) == 8
        assert all(row[3] == 0 for update in observations for row in update["rows"])
        assert len(plugin.generated) == 12 and plugin.source.calls == 4

    asyncio.run(run())


@pytest.mark.parametrize("fault", [
    "uid", "missing_row", "duplicate_row", "turn_tokens", "native_tokens", "native_turns", "expected_tokens", "expected_turns",
    "bank_membership", "turn_sums_unverified", "estimator", "macro_rkl", "macro_nll", "bank", "visit",
    "teacher", "protocol", "missing_source_field", "invalid_turn_id", "duplicate_cell",
])
def test_real_profile_mismatch_stops_append_but_native_success_continues(tmp_path, caplog, fault):
    plugin = _plugin(tmp_path)
    driver = SuccessfulUpdateDriver(4)

    async def run():
        await plugin(RolloutFnTrainInput(rollout_id=0, weight_version=0))
        plugin.on_train_result(0, driver.accept([TrainStepOutput(TrainStepOutcome.NORMAL, optimizer_step=_ack(plugin, 0))]))
        prefix = _files(plugin)
        await plugin(RolloutFnTrainInput(rollout_id=1, weight_version=1))
        record = _ack(plugin, 1)
        if fault == "uid":
            record["turn_sums"][0]["uid"] = "not-a-bank-uid"
        elif fault == "missing_row":
            record["turn_sums"].pop()
        elif fault == "duplicate_row":
            record["turn_sums"].append(record["turn_sums"][0])
        elif fault == "turn_tokens":
            # Preserve aggregate count: per-UID counts must still identify the original mask.
            record["turn_sums"][0]["tokens"] += 1
            record["turn_sums"][1]["tokens"] -= 1
        elif fault in ("native_tokens", "native_turns", "expected_tokens", "expected_turns"):
            record[{"native_tokens": "original_tokens", "native_turns": "actual_turns",
                    "expected_tokens": "expected_bank_tokens", "expected_turns": "expected_bank_turns"}[fault]] += 1
        elif fault == "bank_membership":
            record["bank_membership_verified"] = False
        elif fault == "turn_sums_unverified":
            record.update(turn_sums=[], turn_sums_verified=False, unverified_turn_sums=["rank-local measurement failure"])
        elif fault == "estimator":
            record["kl_estimator"] = "other-native-estimator"
        elif fault in ("macro_rkl", "macro_nll"):
            record[{"macro_rkl": "kl_before_tis", "macro_nll": "nll_before_tis"}[fault]] += 1
        elif fault in ("bank", "visit"):
            record[{"bank": "bank", "visit": "bank_visit"}[fault]] += 1
        elif fault in ("teacher", "protocol"):
            record[{"teacher": "teacher_identity", "protocol": "protocol"}[fault]] = "other"
        else:
            from dataclasses import replace

            trajectory = plugin.bank[1]
            payload = json.loads(trajectory.sample_json)
            source = payload["metadata"]["source"]
            if fault == "missing_source_field":
                del source["group_id"]
            elif fault == "invalid_turn_id":
                source["assistant_turn_ordinal"] = True
            else:
                source.update(group_id="g1", assistant_turn_ordinal=2)
            plugin.bank = (plugin.bank[0], replace(trajectory, sample_json=json.dumps(payload)))
        with caplog.at_level(logging.ERROR):
            plugin.on_train_result(1, driver.accept([TrainStepOutput(TrainStepOutcome.NORMAL, optimizer_step=record)]))
        assert plugin.profile.unverified_from == 2 and plugin.profile.unverified_reason
        if fault == "turn_sums_unverified":
            assert "rank-local measurement failure" in plugin.profile.unverified_reason
        assert plugin.profile.latest_verified_update == 1
        assert "verified_through" in caplog.text
        for attempted in (2, 3):
            await plugin(RolloutFnTrainInput(rollout_id=attempted, weight_version=driver.successful))
            plugin.on_train_result(attempted, driver.accept([TrainStepOutput(TrainStepOutcome.NORMAL, optimizer_step=_ack(plugin, attempted))]))
        assert plugin.schedule.successful == driver.successful == 4 and plugin.bank == ()
        assert _files(plugin) == prefix
        assert DistillationProfile.rebuild(plugin.profile.directory).latest_update == 1
        for query in (plugin.profile.summary, plugin.profile.recovery_gap, lambda: plugin.profile.remaining_gap(1),
                      lambda: plugin.profile.conversation_states(1)):
            with pytest.raises(ValueError, match="unverified from update 2"):
                query()
        assert plugin.profile.update(1).rkl == 4 / 3
        assert plugin.profile.conversation_entry(0, 1).rkl == 1

    asyncio.run(run())


@pytest.mark.parametrize("sink", ["observations.jsonl", "updates.jsonl"])
@pytest.mark.parametrize("partial_bytes", [False, True])
def test_real_partial_sink_failure_retains_prefix_and_suppresses_later_healthy_updates(tmp_path, monkeypatch, caplog, sink, partial_bytes):
    plugin = _plugin(tmp_path)
    append = distillation_profile._append

    def fail(path, row):
        if path.name == sink and row["update_id"] == 2:
            if partial_bytes:
                with path.open("a", encoding="utf-8") as stream:
                    stream.write('{"update_id": 2, "incomplete":')
            raise OSError("injected profile filesystem failure")
        append(path, row)

    monkeypatch.setattr(distillation_profile, "_append", fail)

    async def run():
        for attempted in range(4):
            await plugin(RolloutFnTrainInput(rollout_id=attempted, weight_version=plugin.schedule.successful))
            plugin.on_train_result(attempted, _ack(plugin, attempted))
            if attempted == 1:
                retained = _files(plugin)
        assert plugin.schedule.successful == 4 and plugin.profile.unverified_from == 2
        assert plugin.profile.latest_verified_update == 1 and _files(plugin) == retained
        assert "injected profile filesystem failure" in plugin.profile.unverified_reason
        assert '"verified_through": 1' in caplog.text
        rows = {name: [json.loads(line) for line in contents.splitlines()
                       if not line.endswith(b'"incomplete":')] for name, contents in retained.items()}
        assert [row["update_id"] for row in rows["updates.jsonl"]] == [1]
        expected = [1, 2] if sink == "updates.jsonl" else [1]
        assert [row["update_id"] for row in rows["observations.jsonl"]] == expected
        if partial_bytes:
            assert retained[sink].endswith(b'{"update_id": 2, "incomplete":')
            with pytest.raises(json.JSONDecodeError):
                DistillationProfile.rebuild(plugin.profile.directory)
        elif sink == "updates.jsonl":
            with pytest.raises(ValueError, match="1 update lines and 2 observation lines"):
                DistillationProfile.rebuild(plugin.profile.directory)
        else:
            assert DistillationProfile.rebuild(plugin.profile.directory).latest_update == 1
        with pytest.raises(ValueError, match="unverified from update 2"):
            plugin.profile.summary()

    asyncio.run(run())


@pytest.mark.parametrize("fault", ["directory", "constructor", "finished_report"])
def test_real_initialization_and_bank_boundary_errors_are_soft(tmp_path, monkeypatch, caplog, fault):
    directory = tmp_path / "training"
    source = _Source()
    if fault == "directory":
        directory.mkdir()
        (directory / "distillation_profile").write_text("blocker")
    elif fault == "constructor":
        def unavailable(**kwargs):
            raise OSError("injected profile constructor error")

        monkeypatch.setattr(swe_replay, "DistillationProfile", unavailable)
    else:
        original = source.get_samples

        def missing_report(count):
            values = original(count)
            del source.finished_conversations
            return values

        source.get_samples = missing_report
    with caplog.at_level(logging.ERROR):
        plugin = _plugin(directory, source=source)

        async def run():
            for attempted in range(4):
                await plugin(RolloutFnTrainInput(rollout_id=attempted, weight_version=plugin.schedule.successful))
                plugin.on_train_result(attempted, _ack(plugin, attempted))

        asyncio.run(run())
    assert plugin.schedule.successful == 4
    if fault == "constructor":
        assert plugin.profile is None and "constructor error" in plugin.profile_initialization_error
    else:
        assert plugin.profile.unverified_from == 1 and plugin.profile.latest_verified_update == 0
    assert "unverified from update 1" in caplog.text
    assert not (directory / "distillation_profile/updates.jsonl").exists()


def test_enabled_profile_preserves_existing_r256_bank_visits(tmp_path):
    plugin = _plugin(tmp_path, protocol="r256", uses=2)

    async def run():
        for attempted in range(4):
            await plugin(RolloutFnTrainInput(rollout_id=attempted, weight_version=plugin.schedule.successful))
            assert plugin.schedule.position.bank == attempted // 2
            plugin.on_train_result(attempted, _ack(plugin, attempted))
        assert plugin.source.calls == 2 and plugin.profile.latest_verified_update == 4
        assert plugin.profile.cell(0, 1).replay_num == 1

    asyncio.run(run())


@pytest.mark.parametrize("field", ["swe_profile_trend_window", "swe_profile_baseline_updates", "swe_profile_baseline_turns"])
@pytest.mark.parametrize("value", [0, -1, True, 1.5, "2"])
def test_profile_typed_config_rejects_invalid_lengths(field, value):
    payload = SweReplayConfig(swe_cell="A/full", swe_attempt="cpu", swe_protocol="full",
                              swe_evidence_dir="/data/ycfeng/tmp/profile", swe_teacher_identity="teacher").model_dump()
    with pytest.raises(ValueError):
        SweReplayConfig.model_validate(payload | {field: value})


@pytest.mark.parametrize("enabled", [False, True])
def test_profile_native_custom_view_parse_serialization_and_real_constructor(tmp_path, enabled):
    from miles.ray.rollout.rollout_executor import _compute_rollout_function_config
    from miles.utils.args.runtime import AllConfig, RolloutConfig

    typed = _typed_swe_config("full")
    hooks = {}
    for name in ("rollout_function_path", "custom_rm_path", "custom_megatron_optimizer_step_hook_path"):
        hook = getattr(typed, name)
        config = SweReplayConfig.model_validate(hook.config.model_dump() | {
            "swe_profile_enabled": enabled, "swe_profile_trend_window": 3,
            "swe_profile_baseline_updates": 4, "swe_profile_baseline_turns": 5,
            "swe_evidence_dir": str(tmp_path),
        })
        hooks[name] = hook.model_copy(update={"config": config})
    typed = AllConfig.model_validate(typed.model_dump(mode="python") | hooks)
    rollout = RolloutConfig.slice_from(typed)
    rollout = RolloutConfig.model_validate_json(rollout.model_dump_json())
    view = _compute_rollout_function_config(rollout, rollout.rollout_function_path)
    plugin = SweReplay(RolloutFnConstructorInput(args=view, data_source=_Source()))
    assert plugin.schedule.uses == 1 and view.swe_bank_uses == 50
    if enabled:
        assert (plugin.profile.trend_window, plugin.profile.baseline_updates, plugin.profile.baseline_turns) == (3, 4, 5)
        assert plugin.profile.directory == tmp_path / "distillation_profile"
    else:
        assert plugin.profile is None and not (tmp_path / "distillation_profile").exists()


def test_profile_cli_defaults_and_positive_typed_values():
    parser = argparse.ArgumentParser()
    SweReplayConfig.add_arguments(parser)
    argv = ["--swe-cell", "A/full", "--swe-attempt", "cpu", "--swe-protocol", "full",
            "--swe-evidence-dir", "/data/ycfeng/tmp/profile", "--swe-teacher-identity", "teacher"]
    defaults = SweReplayConfig.model_validate(vars(parser.parse_args(argv)))
    assert defaults.swe_profile_enabled is False
    assert (defaults.swe_profile_trend_window, defaults.swe_profile_baseline_updates, defaults.swe_profile_baseline_turns) == (10, 10, 8)
    config = SweReplayConfig.model_validate(vars(parser.parse_args(argv + ["--swe-profile-enabled", "--swe-profile-trend-window", "2"])))
    assert config.swe_profile_enabled is True and config.swe_profile_trend_window == 2
