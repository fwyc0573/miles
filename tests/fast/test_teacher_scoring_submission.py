"""CPU checks for the isolated teacher-probe allocation and worker command."""

import json
import shlex
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from tests.manual.agent_opd import submit_teacher_scoring_probe as submission


def _configuration(tmp_path, monkeypatch, gpu_tag="H800"):
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(submission, "__file__", str(repo / "tests/manual/agent_opd/submit_teacher_scoring_probe.py"))
    teacher = {"nodes": 1, "gpus_per_node": 4, "tp_size": 4, "cpu_per_node": 32,
               "memory_gb_per_node": 256, "host_network": False, "gang_start": False}
    formal = {"gpu_tag": gpu_tag, "charged_group": "codesign", "pairs": {"A": {"teacher": teacher},
              "B": {"teacher": teacher}}, "local_mount": str(tmp_path), "repo": str(repo),
              "worker_python": "/opt/sglang/bin/python3", "cuda_compat_dir": "/usr/local/cuda-13.0/compat",
              "image": "pinned-image", "mounts": ["personal-volume"]}
    (repo / "formal.json").write_text(json.dumps(formal))
    (repo / "samples.json").write_text("[]")
    probe = {"formal_config": "formal.json", "samples": "samples.json", "output_parent": "outputs",
             "repeats": 2, "request_timeout_seconds": 3600, "worker_seconds": 3600,
             "child_cleanup_grace_seconds": 90}
    path = repo / "probe.json"
    path.write_text(json.dumps(probe))
    return repo, path


@pytest.mark.parametrize("pair", ["A", "B"])
def test_dry_run_allocates_only_one_native_teacher(tmp_path, monkeypatch, capsys, pair):
    repo, config = _configuration(tmp_path, monkeypatch)
    receipt = repo / f"admission-{pair}.json"
    monkeypatch.setattr(sys, "argv", ["submit", "--config", str(config), "--pair", pair,
                                     "--receipt", str(receipt), "--dry-run"])
    assert submission.main() == 0
    record = json.loads(capsys.readouterr().out)
    assert record["submitted"] is False
    assert record["requested_gpus"] == 4
    assert record["gpu_tag"] == "H800"
    assert record["charged_group"] == "codesign"
    assert record["envs"] == {"PYTHONPATH": str(tmp_path)}
    assert list(record["tasks"]) == ["probe"]
    assert record["tasks"]["probe"] == {"cpu": 32, "gpu": 4, "mem_gb": 256, "replica": 1,
                                         "host_network": False, "gang_start": False,
                                         "custom_resources": [], "is_critical": True}
    command = shlex.split(record["worker_command"])
    assert command[:2] == ["bash", "-lc"] and len(command) == 3
    argv = shlex.split(command[2].splitlines()[-1])
    assert argv[:4] == ["exec", "timeout", "--signal=TERM", "--kill-after=90s"]
    assert "--role" not in argv
    assert argv[argv.index("--pair") + 1] == pair
    assert argv[argv.index("--config") + 1] == str(repo / "formal.json")
    assert argv[argv.index("--samples") + 1] == str(repo / "samples.json")
    assert not receipt.exists()


def test_h200_config_is_rejected_before_submission(tmp_path, monkeypatch):
    repo, config = _configuration(tmp_path, monkeypatch, gpu_tag="H200")
    monkeypatch.setattr(sys, "argv", ["submit", "--config", str(config), "--pair", "A",
                                     "--receipt", str(repo / "receipt.json"), "--dry-run"])
    with pytest.raises(ValueError, match="H800/codesign"):
        submission.main()


@pytest.mark.parametrize("pair", ["A", "B"])
@pytest.mark.parametrize("selected", [None, False, True])
def test_snapshot_variant_reaches_worker_while_baseline_command_stays_unchanged(
        tmp_path, monkeypatch, capsys, pair, selected):
    repo, config = _configuration(tmp_path, monkeypatch)
    probe = json.loads(config.read_text())
    if selected is not None:
        probe["selected_fp32_snapshots"] = selected
        config.write_text(json.dumps(probe))
    monkeypatch.setattr(sys, "argv", ["submit", "--config", str(config), "--pair", pair,
                                     "--receipt", str(repo / "receipt.json"), "--dry-run"])
    assert submission.main() == 0
    record = json.loads(capsys.readouterr().out)
    argv = shlex.split(shlex.split(record["worker_command"])[2].splitlines()[-1])
    assert argv[argv.index("--config") + 1] == str(config if selected is True else repo / "formal.json")
    assert record["requested_gpus"] == 4 and list(record["tasks"]) == ["probe"]
    assert record["envs"] == {"PYTHONPATH": str(tmp_path)}
    assert not (repo / "receipt.json").exists()


@pytest.mark.parametrize("selected", [0, 1, "true", None, {}, []])
def test_invalid_snapshot_selection_is_rejected_before_submission(tmp_path, monkeypatch, selected):
    repo, config = _configuration(tmp_path, monkeypatch)
    probe = json.loads(config.read_text())
    probe["selected_fp32_snapshots"] = selected
    config.write_text(json.dumps(probe))
    monkeypatch.setattr(sys, "argv", ["submit", "--config", str(config), "--pair", "A",
                                     "--receipt", str(repo / "receipt.json"), "--dry-run"])
    with pytest.raises(ValueError, match="selected_fp32_snapshots must be a JSON boolean"):
        submission.main()
    assert not (repo / "receipt.json").exists()


@pytest.mark.parametrize("pair", ["A", "B"])
def test_probe_envs_change_only_native_environment_not_worker_command(tmp_path, monkeypatch, capsys, pair):
    repo, config = _configuration(tmp_path, monkeypatch)
    monkeypatch.setenv("SGLANG_FORCE_COARSE_WAR_BARRIER", "ambient-not-configured")
    monkeypatch.setattr(sys, "argv", ["submit", "--config", str(config), "--pair", pair,
                                     "--receipt", str(repo / "receipt.json"), "--dry-run"])
    assert submission.main() == 0
    default = json.loads(capsys.readouterr().out)
    probe = json.loads(config.read_text())
    probe["envs"] = {"SGLANG_FORCE_COARSE_WAR_BARRIER": "1"}
    config.write_text(json.dumps(probe))
    assert submission.main() == 0
    configured = json.loads(capsys.readouterr().out)
    assert default["envs"] == {"PYTHONPATH": str(tmp_path)}
    assert configured["envs"] == {"PYTHONPATH": str(tmp_path), "SGLANG_FORCE_COARSE_WAR_BARRIER": "1"}
    assert {**configured, "envs": default["envs"]} == default


@pytest.mark.parametrize("envs", [{}, {"SGLANG_FORCE_COARSE_WAR_BARRIER": "1"}])
@pytest.mark.parametrize("relative_config", [False, True])
def test_configured_envs_reach_resource_and_receipt_without_platform_calls(tmp_path, monkeypatch, envs, relative_config):
    repo, config = _configuration(tmp_path, monkeypatch)
    probe = json.loads(config.read_text())
    if envs:
        probe["envs"] = envs
        config.write_text(json.dumps(probe))
    formal_path = repo / "formal.json"
    formal = json.loads(formal_path.read_text())
    policy_path = repo / "policy.json"
    policy_path.write_text(json.dumps({"task_annotation": "task-id", "task_id": "cpu-test"}))
    formal.update(gpu_policy=str(policy_path), admission_lock=str(repo / "admission.lock"),
                  creator="i-fengyicheng", api_timeout_seconds=20, phase="cpu-test")
    formal_path.write_text(json.dumps(formal))
    monkeypatch.setenv("STEPMIND_BACKEND", "rjob")
    monkeypatch.setenv("BRAINPP_ACCESS_KEY", "fake-access-key")
    monkeypatch.setenv("BRAINPP_SECRET_KEY", "fake-secret-key")
    if relative_config:
        monkeypatch.chdir(repo)
    else:
        monkeypatch.setattr(submission.os, "chdir", lambda *args: None)
    monkeypatch.setattr(submission.socket, "gethostname", lambda: "mock-local-host")
    monkeypatch.setattr(submission.socket, "gethostbyname", lambda *args: "192.0.2.10")
    monkeypatch.setattr(submission, "policy_admission_snapshot", lambda *args, **kwargs: {
        "admitted": True, "preemptible": False})
    job = {"metadata": {"name": "mock-job", "uid": "mock-uid",
                        "labels": {"kubebrain.brainpp.cn/creator": "i-fengyicheng"}},
           "status": {"phase": "Succeeded"}}
    client = SimpleNamespace(api=SimpleNamespace(get_namespaced_custom_object=lambda **kwargs: job),
                             group="mock", version="mock", namespace="mock", plural="mock")
    resources = []

    def submit(resource, *, command, code_mount_point):
        expected = {"PYTHONPATH": str(tmp_path), **envs}
        assert resource.envs == expected
        assert resource.task_specs["probe"]["gpu"] == 4
        assert resource.pull_code is False and code_mount_point == str(tmp_path)
        resources.append((resource, command))
        # Native RJobBackend adds EXP_ID after the configured environment is captured.
        resource.envs["EXP_ID"] = "platform-owned-id"
        return SimpleNamespace(rjob=SimpleNamespace(meta=SimpleNamespace(name="mock-job")), wait=lambda: None)

    modules = {
        "steptron.exp.base_exp": {"ResourceConfig": SimpleNamespace},
        "steptron.utils.stepmind": {"get_rjob_client": lambda: client},
        "steptron.utils.stepmind_control": {"RJobBackend": lambda: SimpleNamespace(submit=submit)},
    }
    for name, attributes in modules.items():
        module = ModuleType(name)
        module.__dict__.update(attributes)
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setattr(submission, "_job_succeeded", lambda *args: True)
    receipt = repo / "receipt.json"
    monkeypatch.setattr(sys, "argv", ["submit", "--config", "probe.json" if relative_config else str(config),
                                     "--pair", "A", "--receipt", str(receipt)])
    assert submission.main() == 0
    record = json.loads(receipt.read_text())
    assert len(resources) == 1 and record["submitted"] is True
    assert record["envs"] == {"PYTHONPATH": str(tmp_path), **envs}
    assert record["worker_command"] == resources[0][1]
    assert record["probe_config"] == str(config)
    assert "fake-access-key" not in receipt.read_text() and "fake-secret-key" not in receipt.read_text()


def test_war_barrier_variant_changes_only_output_isolation_and_envs():
    task = Path(__file__).resolve().parents[2] / "task_memory/task_2026-11-08_qwen35_full_kl_nll"
    base_text = (task / "teacher_scoring_probe_config.json").read_text()
    variant_text = (task / "teacher_scoring_war_barrier_probe_config.json").read_text()
    base, variant = json.loads(base_text), json.loads(variant_text)
    assert "envs" not in base and variant["envs"] == {"SGLANG_FORCE_COARSE_WAR_BARRIER": "1"}
    assert variant["output_parent"] != base["output_parent"]
    assert {key: value for key, value in variant.items() if key != "envs"} == {
        **base, "output_parent": variant["output_parent"]}
    restored = variant_text.replace('  "envs": {"SGLANG_FORCE_COARSE_WAR_BARRIER": "1"},\n', "", 1)
    assert restored.replace(json.dumps(variant["output_parent"]), json.dumps(base["output_parent"]), 1) == base_text
    formal = json.loads((Path(__file__).resolve().parents[2] / variant["formal_config"]).read_text())
    fixture = json.loads((Path(__file__).resolve().parents[2] / variant["samples"]).read_text())
    assert variant["repeats"] == 2 and variant["pairs"] == ["A", "B"]
    assert len(fixture["samples"]) == 7
    assert 4 * len(fixture["samples"]) * variant["repeats"] == 56
    assert 2 * (len(fixture["samples"]) + 1) * variant["repeats"] == 32
    for pair in variant["pairs"]:
        assert formal["pairs"][pair]["teacher"]["chunked_prefill_size"] == 8192
