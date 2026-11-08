"""Boundary and subprocess-status regressions for the SWE paired entrypoint."""

import json
import subprocess
import sys

import pytest

from tests.manual.agent_opd import run_swe_opd
from tests.manual.agent_opd.submit_swe_opd import _validate_paths


def _config(tmp_path):
    return {
        "local_mount": str(tmp_path), "repo": str(tmp_path), "shared_dir": str(tmp_path / "shared"),
        "admission_lock": str(tmp_path / "admission.lock"), "worker_local_root": str(tmp_path / "cache"),
        "run_root": "/mnt/codesign-exp/ycfeng/swe-fixture", "gpu_policy": str(tmp_path / "gpu-policy.json"),
        "pairs": {"A": {"startup_timeout": 60,
                        "student": {"path": "/mnt/codesign-exp/ycfeng/source-student"},
                        "teacher": {"path": "/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-27B/model"}}},
    }


@pytest.mark.parametrize("field", ["shared_dir", "repo", "admission_lock", "worker_local_root", "gpu_policy"])
def test_cloud_paths_fail_before_any_submission(tmp_path, field):
    config = _config(tmp_path)
    config[field] = "/mnt/codesign-exp/another-user/receipts"
    with pytest.raises(ValueError):
        _validate_paths(config, tmp_path / "config.json")


def test_resolved_shared_path_must_stay_in_the_mount(tmp_path):
    config = _config(tmp_path)
    alias = tmp_path / "shared-alias"
    alias.symlink_to("/mnt/codesign-exp/another-user")
    config["shared_dir"] = str(alias)
    with pytest.raises(ValueError, match="resolve under"):
        _validate_paths(config, tmp_path / "config.json")


@pytest.mark.parametrize("role,expected", [("student", 137), ("teacher", 23)])
def test_cli_preserves_child_failure_status(tmp_path, monkeypatch, role, expected):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(_config(tmp_path)))
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "fixture-job")
    monkeypatch.setenv("KUBEBRAIN_REPLICA", "0")
    monkeypatch.setattr(sys, "argv", ["run_swe_opd", "--config", str(path), "--pair", "A",
                                      "--protocol", "full", "--role", role])
    monkeypatch.setattr(run_swe_opd.signal, "signal", lambda *args: None)
    monkeypatch.setattr(run_swe_opd.paired, "_run_student", lambda *args, **kwargs: -9)

    def teacher(*args):
        raise subprocess.CalledProcessError(23, "native-teacher")

    monkeypatch.setattr(run_swe_opd.paired, "_run_teacher", teacher)
    assert run_swe_opd.main() == expected
