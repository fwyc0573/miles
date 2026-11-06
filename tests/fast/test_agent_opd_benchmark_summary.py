"""Keep native grading errors distinct from proven model failures in avg@4."""

import hashlib
import json
from pathlib import Path

import pytest

from tests.manual.agent_opd.summarize_benchmark import summarize


def _write(path: Path, value: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")


def _scenario(tmp_path):
    membership = {"task_ids": [f"question-{index}" for index in range(20)], "seeds": [1729, 1730, 1731, 1732]}
    before, after = tmp_path / "exp-original", tmp_path / "exp-updated"
    for root, version in ((before, 0), (after, 20)):
        for task in membership["task_ids"]:
            for seed in membership["seeds"]:
                directory = root / f"step{version}" / f"seed-{seed}" / "outcomes"
                identity = {"task_id": task, "seed": seed, "completed_updates": version}
                _write(directory / f"{task}.generation.json", {**identity, "status": "returned", "seed_verified": True})
                _write(directory / f"{task}.grading.json", {**identity, "status": "resolved", "resolved": True})
    directory = after / "step20" / "seed-1731" / "outcomes"
    generation = directory / "question-0.generation.json"
    grading = directory / "question-0.grading.json"
    identity = {"task_id": "question-0", "seed": 1731, "completed_updates": 20}
    _write(grading, {**identity, "status": "invalid", "error_type": "ValueError"})
    generation_hash = hashlib.sha256(generation.read_bytes()).hexdigest()
    grading_hash = hashlib.sha256(grading.read_bytes()).hexdigest()
    trajectory_hash = hashlib.sha256(b"original trajectory").hexdigest()
    patch_hash = hashlib.sha256(b"submitted patch").hexdigest()
    diagnosis = {
        **identity,
        "status": "confirmed_model_failure",
        "failure_type": "grading_timeout",
        "source_job": after.name,
        "source_uid": "source-uid",
        "generation_reran": False,
        "generation_sha256": generation_hash,
        "grading_sha256": grading_hash,
        "trajectory_sha256": trajectory_hash,
        "patch_sha256": patch_hash,
        "native_timeout_seconds": 1200,
        "native_checks": [{"status": "timeout", "timeout_seconds": 1200}] * 2,
        "baseline_control": {
            **identity,
            "status": "passed",
            "native_status": "resolved",
            "source_job": after.name,
            "source_uid": "source-uid",
            "generation_reran": False,
            "original_generation_sha256": generation_hash,
            "original_trajectory_sha256": trajectory_hash,
            "tests_status_counts": {"FAIL_TO_PASS": {"success": 1, "failure": 0}},
            "tests_status_allcases_count": 1,
            "native_time_consumed": 300,
        },
        "native_differential": {
            "status": "passed",
            "patch_sha256": patch_hash,
            "executable": "/opt/miniconda3/envs/testbed/bin/python",
            "results": [
                {"test_patch_url_index": 0, "regex": "original", "status": "returned"},
                {"test_patch_url_index": 0, "regex": "submitted_patch", "status": "timeout"},
            ],
        },
    }
    failure = directory / "question-0.model_failure.json"
    _write(failure, diagnosis)
    return before, after, membership, generation, grading, failure


def _summarize(before, after, membership):
    return summarize(before, after, membership, bootstrap_samples=1000, bootstrap_seed=20261105)


def test_confirmed_timeout_keeps_original_receipt_and_fixed_denominator(tmp_path):
    before, after, membership, _, grading, _ = _scenario(tmp_path)
    original = grading.read_bytes()
    result = _summarize(before, after, membership)
    updated = result["models"][1]
    assert result["status"] == "complete"
    assert updated["valid_attempts"] == updated["expected_attempts"] == 80
    assert updated["native_valid_attempts"] == 79
    assert len(updated["confirmed_model_failures"]) == 1
    assert updated["avg_at_4"] == 79 / 80
    assert updated["per_question"]["question-0"] == 0.75
    assert grading.read_bytes() == original
    assert json.loads(original)["status"] == "invalid"


def test_unknown_grader_error_remains_missing(tmp_path):
    before, after, membership, _, _, failure = _scenario(tmp_path)
    failure.unlink()
    result = _summarize(before, after, membership)
    updated = result["models"][1]
    assert result["status"] == "incomplete"
    assert updated["avg_at_4"] is None
    assert updated["valid_attempts"] == updated["native_valid_attempts"] == 79
    assert updated["confirmed_model_failures"] == []
    assert len(updated["missing_attempts"]) == 1


@pytest.mark.parametrize("file_index", [3, 4])
def test_changed_original_receipt_invalidates_diagnosis(tmp_path, file_index):
    scenario = _scenario(tmp_path)
    path = scenario[file_index]
    value = json.loads(path.read_text())
    value["changed_after_diagnosis"] = True
    _write(path, value)
    result = _summarize(*scenario[:3])
    assert result["status"] == "incomplete"
    assert result["models"][1]["confirmed_model_failures"] == []


@pytest.mark.parametrize("evidence", ["baseline_control", "native_differential"])
def test_failed_causal_control_cannot_be_scored(tmp_path, evidence):
    before, after, membership, _, _, failure = _scenario(tmp_path)
    value = json.loads(failure.read_text())
    value[evidence]["status"] = "failed"
    _write(failure, value)
    result = _summarize(before, after, membership)
    assert result["status"] == "incomplete"
    assert result["models"][1]["avg_at_4"] is None


def test_model_timeout_cannot_be_replaced_by_duplicate_native_success(tmp_path):
    before, after, membership, generation, grading, _ = _scenario(tmp_path)
    replacement = tmp_path / "exp-replacement"
    directory = replacement / "step20" / "seed-1731" / "outcomes"
    _write(directory / generation.name, json.loads(generation.read_text()))
    _write(directory / grading.name, {"task_id": "question-0", "seed": 1731, "completed_updates": 20, "status": "resolved", "resolved": True})
    with pytest.raises(ValueError, match="Duplicate valid benchmark attempt"):
        _summarize(before, [after, replacement], membership)
