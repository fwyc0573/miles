"""Boundary and subprocess-status regressions for the SWE paired entrypoint."""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from tests.manual.agent_opd import run_swe_opd
from tests.manual.agent_opd.submit_swe_opd import _job_succeeded, _validate_paths


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


@pytest.mark.parametrize(
    "phase,reason,student,expected",
    [
        ("Succeeded", None, {"succeeded": 1}, True),
        ("Stopped", "All critical tasks are finished.", {"succeeded": 1}, True),
        ("Stopped", "All critical tasks are finished.", {"failed": 1}, False),
        ("Stopped", "All critical tasks are finished.", {"running": 1}, False),
        ("Stopped", "Some critical tasks failed.", {"failed": 1}, False),
        ("Stopped", None, {"succeeded": 1}, False),
        ("Failed", "All critical tasks are finished.", {"succeeded": 1}, False),
    ],
)
def test_platform_critical_completion_is_not_a_training_failure(phase, reason, student, expected):
    job = {
        "metadata": {"annotations": {"rjob.brainpp.cn/system-stop-reason": reason}},
        "status": {"phase": phase, "taskStatuses": {"student": student, "teacher": {"stopped": 1}}},
    }
    tasks = {"student": {"is_critical": True, "replica": 1}, "teacher": {"is_critical": False, "replica": 1}}
    assert _job_succeeded(job, tasks) is expected


def test_partial_critical_replica_completion_remains_failed():
    job = {
        "metadata": {"annotations": {"rjob.brainpp.cn/system-stop-reason": "All critical tasks are finished."}},
        "status": {"phase": "Stopped", "taskStatuses": {"student": {"succeeded": 1, "stopped": 1}}},
    }
    assert not _job_succeeded(job, {"student": {"is_critical": True, "replica": 2}})


@pytest.mark.parametrize("masked", [False, True])
def test_native_input_policy_reaches_registered_source_config(tmp_path, monkeypatch, masked):
    from miles.utils.args import custom_function
    from miles.utils.args.runtime import AllConfig

    task = Path(__file__).resolve().parents[2] / "task_memory/task_2026-11-08_qwen35_swe_full_r256"
    config = json.loads((task / "integration_config.json").read_text())
    config["protocol"] = "r256"
    receipt = str(tmp_path / "native visual receipt.json")
    if masked:
        config["inputs"].update(skip_masked_assistant_turns=True, visual_filter_receipt=receipt)
    argv = shlex.split(run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "input-policy"))
    parser = argparse.ArgumentParser(add_help=False)
    AllConfig.add_arguments(parser)
    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    custom_function.add_user_provided_function_arguments(parser, config_class=AllConfig)
    parsed, unknown = parser.parse_known_args(argv)
    assert not any(value.startswith("--swe-") for value in unknown)
    custom_function.resolve_custom_function_configs(parsed, config_class=AllConfig)
    source = parsed.data_source_path.config
    assert source.swe_skip_masked_assistant_turns is masked
    assert source.swe_visual_filter_receipt == (receipt if masked else None)
    assert source.swe_source_manifest == config["inputs"]["source_manifest"]


@pytest.mark.parametrize("policy", [None, "round_robin"])
def test_native_router_policy_preserves_default_and_typed_transport(tmp_path, monkeypatch, policy):
    from tests.fast.test_swe_replay import _typed_swe_config

    from miles.backends.sglang_utils.router_args_utils import (
        compute_sglang_router_args,
        parse_router_args_argv,
        router_args_to_argv,
    )
    from miles.utils.args import custom_function
    from miles.utils.args.configs.router import RouterConfig
    from miles.utils.args.runtime import AllConfig, OrchestratorConfig
    from miles.utils.arguments import get_miles_extra_args_provider

    task = Path(__file__).resolve().parents[2] / "task_memory/task_2026-11-08_qwen35_swe_full_r256"
    config = json.loads((task / "deepswe_capacity_smoke_config.json").read_text())
    config["protocol"] = "r256"
    baseline = shlex.split(
        run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "router-policy")
    )
    assert "--router-policy" not in baseline
    assert "--sglang-router-policy" not in baseline
    config["router_policy"] = policy
    argv = shlex.split(run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "router-policy"))
    if policy is None:
        assert argv == baseline
    else:
        assert argv.count("--router-policy") == 1
        index = argv.index("--router-policy")
        assert argv[index + 1] == policy
        assert argv[:index] + argv[index + 2 :] == baseline
    assert "--sglang-router-policy" not in argv

    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    parser = argparse.ArgumentParser()
    get_miles_extra_args_provider()(parser)
    parsed, unknown = parser.parse_known_args(argv)
    assert not any(value.startswith(("--router-", "--swe-", "--scoring-lifetime-", "--tis-")) for value in unknown)
    custom_function.resolve_custom_function_configs(parsed)
    monkeypatch.setattr(sys, "argv", ["test"])
    typed = _typed_swe_config("r256", run_kind="smoke")
    typed = AllConfig.model_validate(
        typed.model_dump(mode="python")
        | RouterConfig.from_args(parsed)
        | {
            "sglang_router_policy": parsed.sglang_router_policy,
        }
    )
    orchestrator = OrchestratorConfig.slice_from(typed)
    restored = OrchestratorConfig.model_validate_json(orchestrator.model_dump_json())
    expected = "cache_aware" if policy is None else policy
    assert restored.router_args["policy"] == expected
    assert restored.sglang_router_policy is None
    router = compute_sglang_router_args(
        restored,
        host="127.0.0.1",
        port=30000,
        prometheus_port=30001,
        has_pd_disaggregation=False,
    )
    assert parse_router_args_argv(router_args_to_argv(router)).policy == expected
