"""Offline acceptance of synthetic ACK/profile pairs and preserved incomplete evidence."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from tests.fast.test_distillation_profile import UPDATES, _bank, _profile, _sums
from tests.manual.agent_opd.distillation_profile import OBSERVATIONS_FILE, UPDATES_FILE, DistillationProfile
from tests.manual.agent_opd.inspect_distillation_run import inspect_run


JOB = "synthetic-offline-attempt"


def _write_rows(path, rows):
    path.write_text("".join(json.dumps(row, allow_nan=False) + "\n" for row in rows))


def _rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def _terminal(path, *, phase="Succeeded", job=JOB):
    path.write_text(json.dumps({"job": job, "status": {"phase": phase, "message": "synthetic terminal"},
                                "native_execution_succeeded": phase == "Succeeded"}))
    return path


def _bank_evidence(path, turns):
    # A failed candidate is not a trained/profile row. Bank slot order, not ACK
    # turn-sum order, determines the first-appearance conversation IDs.
    slots = [{"slot": index, "source_uid": turn[0]} for index, turn in enumerate(turns)]
    slots.append({"slot": len(turns), "source_uid": "failed-candidate"})
    rows = [{"event": "acquisition_start", "slots": slots}]
    for slot, (uid, source_conversation_id, turn, _, _, tokens) in enumerate(turns):
        rows.append({"event": "slot_finished", "slot": slot, "source_uid": uid, "status": "completed",
                     "error": None, "sample": {"metadata": {"source": {"uid": uid, "group_id": source_conversation_id,
                                                                            "assistant_turn_ordinal": turn}},
                                                "loss_mask": [1] * tokens, "response_length": tokens}})
    rows.append({"event": "slot_finished", "slot": len(turns), "source_uid": "failed-candidate",
                 "status": "invalid", "error": "synthetic failure", "sample": None})
    rows.append({"event": "acquisition_sealed", "actual_turns": len(turns),
                 "membership": list(range(len(turns))), "missing_slots": [len(turns)]})
    _write_rows(path, rows)


def _run(tmp_path, count=4, *, skipped=False):
    training = tmp_path / "training"
    training.mkdir()
    profile = _profile(training / "distillation_profile")
    native = []
    for update_id in range(1, count + 1):
        if count <= len(UPDATES):
            turns, finished = UPDATES[update_id - 1]
        else:
            turns, finished = [(f"g:{update_id}", "g", update_id, 2.0, 4.0, 2)], []
        profile.record_update(update_id, _sums(turns), _bank(turns), finished)
        summary = profile.summary()
        attempted = update_id + int(skipped and update_id >= 2)
        native.append({"update": update_id, "successful_updates": update_id, "update_successful": True,
                       "native_attempted_count": attempted, "native_skipped_count": attempted - update_id,
                       "attempted_rollout_id": attempted - 1, "bank": update_id - 1, "bank_visit": 1,
                       "cell": "A/full", "attempt": JOB, "protocol": "full",
                       "teacher_identity": "synthetic-teacher", "run_kind": "smoke",
                       "turn_sums_verified": True, "unverified_turn_sums": [], "bank_membership_verified": True,
                       "actual_turns": summary["turns"], "expected_bank_turns": summary["turns"],
                       "original_tokens": summary["tokens"], "expected_bank_tokens": summary["tokens"],
                       "kl_estimator": summary["estimator"], "kl_before_tis": summary["rkl"],
                       "nll_before_tis": summary["nll"], "kl_before_tis_numerator": summary["rkl_sum"],
                       "nll_before_tis_numerator": summary["nll_sum"],
                       "kl_before_tis_denominator": summary["tokens"], "nll_before_tis_denominator": summary["tokens"]})
        _bank_evidence(training / f"bank_{update_id - 1}.jsonl", turns)
    _write_rows(training / UPDATES_FILE, native)
    return training, _terminal(tmp_path / "terminal.json"), profile


def _inspect(training, terminal=None, expected=4):
    return inspect_run(training, job=JOB, expected_updates=expected, terminal_path=terminal)


def test_inspection_uses_writable_tmpdir_without_host_path(tmp_path, monkeypatch):
    training, terminal, _ = _run(tmp_path, count=1)
    temporary_root = tmp_path / "alternate-temporary-root"
    temporary_root.mkdir()
    monkeypatch.setenv("TMPDIR", str(temporary_root))
    monkeypatch.setattr(tempfile, "tempdir", None)
    create_directory = tempfile.mkdtemp

    def configured_root_only(suffix=None, prefix=None, dir=None):
        parent = Path(dir if dir is not None else tempfile.gettempdir())
        if parent != temporary_root:
            raise PermissionError("Temporary writes outside the configured root are unavailable")
        return create_directory(suffix=suffix, prefix=prefix, dir=dir)

    monkeypatch.setattr(tempfile, "mkdtemp", configured_root_only)
    receipt, profile = _inspect(training, terminal, expected=1)
    assert receipt["profile"]["complete"] and profile.latest_update == 1
    assert profile.update(1).rkl == 0.75


def test_temporary_directory_creation_error_is_an_honest_profile_verdict(tmp_path, monkeypatch):
    training, terminal, _ = _run(tmp_path, count=1)

    def unavailable_directory(*args, **kwargs):
        raise OSError("Synthetic temporary-directory creation failure")

    monkeypatch.setattr(tempfile, "mkdtemp", unavailable_directory)
    receipt, profile = _inspect(training, terminal, expected=1)
    assert receipt["native"]["complete"]
    assert not receipt["profile"]["complete"] and receipt["profile"]["verified_updates"] == 0
    assert "Synthetic temporary-directory creation failure" in receipt["profile"]["error"]
    assert receipt["profile"]["unverified_ranges"] == [[1, 1]] and profile is None


def test_hand_computed_uneven_turns_skipped_ack_and_read_only_rebuild(tmp_path):
    training, terminal, original = _run(tmp_path, skipped=True)
    before = {path: path.read_bytes() for path in training.rglob("*") if path.is_file()}
    receipt, profile = _inspect(training, terminal)
    assert receipt["native"]["complete"] is True
    assert receipt["native"]["observed_successful_updates"] == receipt["native"]["successful_updates"] == 4
    assert receipt["native"]["observed_successful_update_ids"] == [1, 2, 3, 4]
    assert receipt["profile"]["verified_updates"] == receipt["profile"]["canonical_uid_verified_updates"] == 4
    assert receipt["profile"]["complete"] is True
    assert receipt["profile"]["first_unverified_update"] is None
    assert receipt["profile"]["unverified_ranges"] == []
    assert profile.summary() == original.summary()
    assert profile.baseline == 0.59375
    assert profile.update(1).rkl == 6 / 8
    assert profile.update(1).nll == 8 / 8
    assert profile.conversation(0).baseline == (2 / 4 + 3 / 2) / 2
    assert profile.remaining_gap(1) == 0.75 / 0.59375
    assert profile.conversation_states(2) == original.conversation_states(2)
    assert profile.best_update().update_id == 2
    assert profile.latest_update == profile.latest_verified_update == 4
    assert profile.unverified_from is None and profile.directory is None
    assert all(path.read_bytes() == contents for path, contents in before.items())


def test_full_expected_200_is_distinct_from_a_four_update_fixture(tmp_path):
    training, terminal, _ = _run(tmp_path)
    receipt, profile = _inspect(training, terminal, expected=200)
    assert receipt["native"]["successful_updates"] == 4 and not receipt["native"]["complete"]
    assert not receipt["profile"]["complete"] and profile.latest_update == 4
    assert receipt["profile"]["unverified_ranges"] == [[5, 200]]


def test_synthetic_200_update_readiness(tmp_path):
    training, terminal, original = _run(tmp_path, count=200)
    receipt, profile = _inspect(training, terminal, expected=200)
    assert receipt["native"]["complete"] and receipt["profile"]["complete"]
    assert receipt["native"]["ack_identity"]["run_kind"] == "smoke"
    assert profile.summary() == original.summary() and profile.latest_update == 200


@pytest.mark.parametrize("include_terminal", [False, True])
def test_native_update_201_is_an_unverified_tail_of_a_200_update_profile(tmp_path, include_terminal):
    training, terminal, _ = _run(tmp_path, count=200)
    native_path = training / UPDATES_FILE
    native = _rows(native_path)
    native.append({**native[-1], "update": 201, "successful_updates": 201,
                   "native_attempted_count": 201, "attempted_rollout_id": 200, "bank": 200})
    _write_rows(native_path, native)
    receipt, profile = _inspect(training, terminal if include_terminal else None, expected=200)
    assert receipt["native"]["observed_successful_updates"] == 201
    assert not receipt["profile"]["complete"]
    assert receipt["profile"]["verified_updates"] == profile.latest_update == 200
    assert receipt["profile"]["first_unverified_update"] == 201
    assert receipt["profile"]["unverified_ranges"] == [[201, 201]]
    assert profile.update(200).rkl == 1.0
    with pytest.raises(IndexError):
        profile.update(201)


def test_complete_profile_does_not_require_a_terminal_receipt(tmp_path):
    training, _, _ = _run(tmp_path, count=200)
    receipt, profile = _inspect(training, expected=200)
    assert receipt["profile"]["complete"] and profile.latest_update == 200
    assert receipt["profile"]["unverified_ranges"] == []
    assert not receipt["native"]["complete"] and receipt["native"]["terminal_phase"] is None


def test_first_update_live_inspection_needs_no_terminal(tmp_path):
    training, _, _ = _run(tmp_path, count=1)
    receipt, profile = _inspect(training, expected=200)
    assert receipt["native"]["successful_updates"] == receipt["profile"]["verified_updates"] == 1
    assert receipt["native"]["terminal_phase"] is None and not receipt["native"]["complete"]
    assert "No terminal" in receipt["native"]["error"]
    assert receipt["profile"]["unverified_ranges"] == [[2, 200]]
    assert profile.update(1).rkl == 0.75 and profile.baseline is None


@pytest.mark.parametrize("sink", [UPDATES_FILE, OBSERVATIONS_FILE])
@pytest.mark.parametrize("tail", ["absent", "partial", "valid_without_newline"])
def test_native_success_with_partial_profile_returns_only_clean_prefix(tmp_path, sink, tail):
    training, terminal, _ = _run(tmp_path)
    path = training / "distillation_profile" / sink
    rows = _rows(path)
    _write_rows(path, rows[:1])
    if tail != "absent":
        with path.open("a") as stream:
            stream.write('{"update_id": 2, "incomplete":' if tail == "partial" else json.dumps(rows[1]))
    before = path.read_bytes()
    receipt, profile = _inspect(training, terminal)
    assert receipt["native"]["complete"] and not receipt["profile"]["complete"]
    assert receipt["profile"]["verified_updates"] == 1
    assert receipt["profile"]["first_unverified_update"] == 2
    assert receipt["profile"]["unverified_ranges"] == [[2, 4]]
    assert receipt["profile"]["missing_pair_ranges"] == [[2, 4]]
    assert profile.latest_update == 1 and profile.baseline is None
    assert profile.summary()["rkl"] == 0.75 and profile.unverified_from is None
    assert path.read_bytes() == before
    with pytest.raises((ValueError, json.JSONDecodeError)):
        DistillationProfile.rebuild(training / "distillation_profile")


def test_missing_profile_tail_preserves_next_native_auxiliary_error(tmp_path):
    training, terminal, _ = _run(tmp_path)
    for name in (UPDATES_FILE, OBSERVATIONS_FILE):
        path = training / "distillation_profile" / name
        _write_rows(path, _rows(path)[:1])
    native_path = training / UPDATES_FILE
    native = _rows(native_path)
    native[1].update(turn_sums_verified=False, unverified_turn_sums=["Missing CP partial for a native sample"],
                     kl_estimator=None, kl_before_tis=None, nll_before_tis=None,
                     kl_before_tis_numerator=None, nll_before_tis_numerator=None)
    _write_rows(native_path, native)
    receipt, profile = _inspect(training, terminal)
    assert receipt["native"]["complete"] and receipt["native"]["successful_updates"] == 4
    assert "Missing CP partial for a native sample" in receipt["profile"]["error"]
    assert receipt["profile"]["first_unverified_update"] == 2
    assert receipt["profile"]["unverified_ranges"] == [[2, 4]]
    assert profile.latest_update == 1 and profile.baseline is None
    assert profile.summary()["rkl"] == 0.75


@pytest.mark.parametrize("retained", ["empty", "missing", "read_errors"])
def test_unpersisted_first_profile_preserves_native_auxiliary_reason_and_read_errors(tmp_path, retained):
    training, _, _ = _run(tmp_path, count=1)
    native_path = training / UPDATES_FILE
    native = _rows(native_path)
    native[0].update(turn_sums_verified=False, unverified_turn_sums=["ACK1 missing CP partial before profile persistence"],
                     kl_estimator=None, kl_before_tis=None, nll_before_tis=None,
                     kl_before_tis_numerator=None, nll_before_tis_numerator=None)
    _write_rows(native_path, native)
    profile_dir = training / "distillation_profile"
    for name in (UPDATES_FILE, OBSERVATIONS_FILE):
        path = profile_dir / name
        if retained == "empty":
            path.write_text("")
        else:
            path.unlink()
    if retained == "read_errors":
        (profile_dir / UPDATES_FILE).mkdir()
        (profile_dir / OBSERVATIONS_FILE).write_text('{"update_id":}\n')
    receipt, profile = _inspect(training, expected=200)
    assert "ACK1 missing CP partial before profile persistence" in receipt["profile"]["error"]
    assert receipt["native"]["successful_updates"] == 1
    assert receipt["native"]["observed_successful_update_ids"] == [1]
    assert receipt["profile"]["verified_updates"] == receipt["profile"]["canonical_uid_verified_updates"] == 0
    assert not receipt["profile"]["complete"] and profile is None
    assert receipt["profile"]["unverified_ranges"] == receipt["profile"]["missing_pair_ranges"] == [[1, 200]]
    read_errors = receipt["profile"]["read_errors"]
    assert read_errors["native_updates"] is None
    if retained == "empty":
        assert read_errors["profile_updates"] is read_errors["profile_observations"] is None
    elif retained == "missing":
        assert "FileNotFoundError" in read_errors["profile_updates"]
        assert "FileNotFoundError" in read_errors["profile_observations"]
    else:
        assert "IsADirectoryError" in read_errors["profile_updates"]
        assert "invalid JSON at line 1" in read_errors["profile_observations"]


@pytest.mark.parametrize("failure", ["io", "parsing"])
def test_actual_first_validation_error_is_not_replaced_by_adjacent_native_error(tmp_path, failure):
    training, _, _ = _run(tmp_path, count=1)
    native_path = training / UPDATES_FILE
    native = _rows(native_path)
    native[0].update(turn_sums_verified=False, unverified_turn_sums=["Adjacent ACK1 auxiliary reason"])
    _write_rows(native_path, native)
    bank_path = training / "bank_0.jsonl"
    if failure == "io":
        bank_path.unlink()
        bank_path.mkdir()
    else:
        bank_path.write_text('{"event":}\n')
    receipt, profile = _inspect(training, expected=200)
    assert ("IsADirectoryError" if failure == "io" else "JSONDecodeError") in receipt["profile"]["error"]
    assert "Adjacent ACK1 auxiliary reason" not in receipt["profile"]["error"]
    assert receipt["profile"]["verified_updates"] == 0 and profile is None
    assert receipt["profile"]["unverified_ranges"] == [[1, 200]]


def test_actual_first_summary_validation_error_is_not_replaced_by_later_native_error(tmp_path):
    training, terminal, _ = _run(tmp_path)
    summary_path = training / "distillation_profile" / UPDATES_FILE
    summaries = _rows(summary_path)
    summaries[0]["rkl"] = 999
    _write_rows(summary_path, summaries)
    native_path = training / UPDATES_FILE
    native = _rows(native_path)
    native[1].update(turn_sums_verified=False, unverified_turn_sums=["Later ACK2 auxiliary reason"])
    _write_rows(native_path, native)
    receipt, profile = _inspect(training, terminal)
    assert "summary does not reproduce" in receipt["profile"]["error"]
    assert "Later ACK2 auxiliary reason" not in receipt["profile"]["error"]
    assert receipt["profile"]["verified_updates"] == 0 and profile is None


@pytest.mark.parametrize("field,value", [
    ("original_tokens", 999), ("actual_turns", 999), ("expected_bank_tokens", 999),
    ("kl_before_tis", 99.0), ("nll_before_tis", 99.0), ("kl_estimator", "wrong-estimator"),
    ("kl_before_tis_numerator", 99.0), ("nll_before_tis_denominator", 999),
    ("bank_membership_verified", False), ("turn_sums_verified", False),
])
def test_native_measurement_mismatch_bounds_profile_not_native_completion(tmp_path, field, value):
    training, terminal, _ = _run(tmp_path)
    path = training / UPDATES_FILE
    rows = _rows(path)
    rows[1][field] = value
    if field == "turn_sums_verified":
        rows[1]["unverified_turn_sums"] = ["first retained native measurement error"]
    _write_rows(path, rows)
    receipt, profile = _inspect(training, terminal)
    assert receipt["native"]["complete"] and receipt["native"]["successful_updates"] == 4
    assert receipt["profile"]["verified_updates"] == profile.latest_update == 1
    assert receipt["profile"]["unverified_ranges"] == [[2, 4]]
    assert profile.baseline is None
    if field == "turn_sums_verified":
        assert "first retained native measurement error" in receipt["profile"]["error"]


@pytest.mark.parametrize("fault", ["uid", "turn", "per_uid_tokens", "membership", "missing_bank", "missing_seal"])
def test_canonical_uid_identity_and_mask_evidence_are_required(tmp_path, fault):
    training, terminal, _ = _run(tmp_path)
    path = training / "bank_1.jsonl"
    rows = _rows(path)
    if fault == "uid":
        rows[1]["sample"]["metadata"]["source"]["uid"] = "not-canonical"
    elif fault == "turn":
        rows[1]["sample"]["metadata"]["source"]["assistant_turn_ordinal"] = 99
    elif fault == "per_uid_tokens":
        # Keep the macro count fixed while exchanging two individual masks.
        rows[1]["sample"]["loss_mask"].pop()
        rows[1]["sample"]["response_length"] -= 1
        rows[2]["sample"]["loss_mask"].append(1)
        rows[2]["sample"]["response_length"] += 1
    elif fault == "membership":
        rows[-1]["membership"].pop()
    elif fault == "missing_seal":
        rows.pop()
    if fault == "missing_bank":
        path.unlink()
    else:
        _write_rows(path, rows)
    receipt, profile = _inspect(training, terminal)
    assert receipt["native"]["complete"] and receipt["profile"]["verified_updates"] == 1
    assert receipt["profile"]["canonical_uid_verified_updates"] == 1
    assert receipt["profile"]["first_unverified_update"] == 2 and profile.latest_update == 1


@pytest.mark.parametrize("field", ["baseline", "rkl_best", "conversations_alive", "baseline_turns"])
def test_earlier_derived_summary_corruption_bounds_prefix(tmp_path, field):
    training, terminal, _ = _run(tmp_path)
    path = training / "distillation_profile" / UPDATES_FILE
    rows = _rows(path)
    rows[1][field] = 999
    _write_rows(path, rows)
    receipt, profile = _inspect(training, terminal)
    assert receipt["profile"]["verified_updates"] == 1
    assert "summary does not reproduce" in receipt["profile"]["error"]
    assert profile.latest_update == 1 and profile.baseline is None


@pytest.mark.parametrize("field,value", [("successful_updates", 3), ("native_skipped_count", 1),
                                        ("attempt", "other-attempt"), ("update_successful", False)])
def test_bad_native_sequence_keeps_observed_count_but_not_proven_total(tmp_path, field, value):
    training, terminal, _ = _run(tmp_path)
    path = training / UPDATES_FILE
    rows = _rows(path)
    rows[1][field] = value
    _write_rows(path, rows)
    receipt, profile = _inspect(training, terminal)
    assert receipt["native"]["observed_successful_updates"] == (3 if field == "update_successful" else 4)
    assert receipt["native"]["observed_successful_update_ids"] == ([1, 3, 4] if field == "update_successful" else [1, 2, 3, 4])
    assert receipt["native"]["successful_updates"] is None and not receipt["native"]["complete"]
    assert "Native update 2" in receipt["native"]["error"]
    assert receipt["profile"]["verified_updates"] == profile.latest_update == 1


def test_missing_middle_native_ack_retains_observed_update_200_identity(tmp_path):
    training, terminal, _ = _run(tmp_path, count=200)
    native_path = training / UPDATES_FILE
    native = _rows(native_path)
    native.pop(4)
    _write_rows(native_path, native)
    receipt, profile = _inspect(training, terminal, expected=200)
    observed_ids = receipt["native"]["observed_successful_update_ids"]
    assert observed_ids[:5] == [1, 2, 3, 4, 6]
    assert 5 not in observed_ids and observed_ids[-1] == 200 and len(observed_ids) == 199
    assert receipt["native"]["observed_successful_updates"] == 199
    assert receipt["native"]["successful_updates"] is None and not receipt["native"]["complete"]
    assert receipt["profile"]["verified_updates"] == profile.latest_update == 4
    assert receipt["profile"]["first_unverified_update"] == 5
    assert receipt["profile"]["unverified_ranges"] == [[5, 200]]


@pytest.mark.parametrize("update_id", [True, 1.0, "1", 0, -1])
def test_observed_successful_ids_exclude_invalid_ids_without_changing_row_count(tmp_path, update_id):
    training, terminal, _ = _run(tmp_path)
    native_path = training / UPDATES_FILE
    native = _rows(native_path)
    native[0]["update"] = update_id
    _write_rows(native_path, native)
    receipt, profile = _inspect(training, terminal)
    assert receipt["native"]["observed_successful_update_ids"] == [2, 3, 4]
    assert receipt["native"]["observed_successful_updates"] == 4
    assert receipt["native"]["successful_updates"] is None and profile is None


def test_missing_native_profile_and_failed_before_start_do_not_prove_zero(tmp_path):
    terminal = _terminal(tmp_path / "failed.json", phase="Failed")
    receipt, profile = _inspect(tmp_path / "not-retained", terminal, expected=200)
    assert receipt["native"]["observed_successful_updates"] == 0
    assert receipt["native"]["observed_successful_update_ids"] == []
    assert receipt["native"]["successful_updates"] is None
    assert receipt["native"]["terminal_phase"] == "Failed" and receipt["native"]["terminal_job_verified"]
    assert not receipt["native"]["complete"] and not receipt["profile"]["complete"]
    assert receipt["profile"]["verified_updates"] == 0 and profile is None
    assert receipt["profile"]["unverified_ranges"] == [[1, 200]]


def test_missing_first_bank_never_claims_uid_verification(tmp_path):
    training, terminal, _ = _run(tmp_path)
    (training / "bank_0.jsonl").unlink()
    receipt, profile = _inspect(training, terminal)
    assert receipt["native"]["complete"]
    assert receipt["profile"]["verified_updates"] == receipt["profile"]["canonical_uid_verified_updates"] == 0
    assert profile is None and receipt["profile"]["unverified_ranges"] == [[1, 4]]


def test_terminal_identity_mismatch_and_missing_native_success_field(tmp_path):
    training, terminal, _ = _run(tmp_path)
    _terminal(terminal, job="other-job")
    receipt, _ = _inspect(training, terminal)
    assert not receipt["native"]["complete"] and not receipt["native"]["terminal_job_verified"]
    assert "Terminal job" in receipt["native"]["error"]
    terminal.write_text(json.dumps({"job": JOB, "status": {"phase": "Succeeded"}}))
    receipt, _ = _inspect(training, terminal)
    assert not receipt["native"]["complete"]
    assert "native_execution_succeeded" in receipt["native"]["error"]


def test_partial_native_receipt_is_not_a_proven_final_count(tmp_path):
    training, terminal, _ = _run(tmp_path)
    path = training / UPDATES_FILE
    rows = _rows(path)
    _write_rows(path, rows[:1])
    with path.open("a") as stream:
        stream.write('{"update": 2, "successful_updates":')
    receipt, profile = _inspect(training, terminal)
    assert receipt["native"]["observed_successful_updates"] == 1
    assert receipt["native"]["successful_updates"] is None and not receipt["native"]["complete"]
    assert "partial line 2" in receipt["native"]["error"]
    assert receipt["profile"]["verified_updates"] == profile.latest_update == 1
    assert receipt["profile"]["missing_pair_ranges"] == []
    assert receipt["profile"]["unverified_ranges"] == [[2, 4]]


@pytest.mark.parametrize("missing", [UPDATES_FILE, OBSERVATIONS_FILE])
def test_one_profile_file_only_cannot_supply_a_verified_first_update(tmp_path, missing):
    training, terminal, _ = _run(tmp_path)
    (training / "distillation_profile" / missing).unlink()
    receipt, profile = _inspect(training, terminal)
    assert receipt["native"]["complete"] and receipt["profile"]["verified_updates"] == 0
    assert receipt["profile"]["missing_pair_ranges"] == [[1, 4]] and profile is None
    assert any(error is not None for error in receipt["profile"]["read_errors"].values())


def test_extra_records_are_unverified_not_silently_discarded(tmp_path):
    training, terminal, _ = _run(tmp_path)
    receipt, profile = _inspect(training, terminal, expected=3)
    assert receipt["native"]["observed_successful_updates"] == 4
    assert receipt["native"]["successful_updates"] is None and not receipt["native"]["complete"]
    assert receipt["profile"]["verified_updates"] == profile.latest_update == 3
    assert not receipt["profile"]["complete"] and receipt["profile"]["unverified_ranges"] == [[4, 4]]


def test_cli_writes_receipt_without_modifying_evidence(tmp_path):
    training, terminal, _ = _run(tmp_path, count=1)
    output = tmp_path / "inspection.json"
    argv = [sys.executable, "-B", "-m", "tests.manual.agent_opd.inspect_distillation_run",
            "--training-dir", str(training), "--job", JOB, "--expected-updates", "200",
            "--terminal", str(terminal), "--output", str(output)]
    result = subprocess.run(argv, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    receipt = json.loads(output.read_text())
    assert receipt["profile"]["verified_updates"] == 1 and receipt["profile"]["unverified_ranges"] == [[2, 200]]
    retained = training / UPDATES_FILE
    before = retained.read_bytes()
    result = subprocess.run([*argv[:-1], str(retained)], capture_output=True, text=True, check=False)
    assert result.returncode == 2 and retained.read_bytes() == before


@pytest.mark.parametrize("expected", [0, -1, True, 1.5])
def test_invalid_inspection_budget_is_not_a_run_verdict(tmp_path, expected):
    with pytest.raises(ValueError, match="positive integer"):
        inspect_run(tmp_path, job=JOB, expected_updates=expected)
