"""CPU-only paired-worker contracts; model and HTTP evidence are local fixtures."""

import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from tests.manual.agent_opd import qwen35_pair_worker as worker


@pytest.fixture
def config(tmp_path, monkeypatch):
    personal = tmp_path / "cloud" / "ycfeng"
    sources = {name: tmp_path / "read-only" / name / "model" for name in ("27B", "35B-A3B", "397B-A17B")}
    monkeypatch.setattr(worker, "_PERSONAL_ROOT", personal)
    monkeypatch.setattr(worker, "_READ_ONLY_MODELS", set(sources.values()))
    pairs = {}
    for pair, source in zip(("A", "B", "C"), sources.values(), strict=True):
        pairs[pair] = {
            "student": {
                "path": str(personal / "models" / ("27B" if pair == "C" else "4B")), "gpus_per_node": 8,
                "tp_size": 4 if pair == "C" else 2, "engine_gpus": 4 if pair == "C" else 2,
                "max_tokens_per_gpu": 131072, "mem_fraction_static": 0.7,
                "max_running_requests": 1, "chunked_prefill_size": 8192,
            },
            "teacher": {
                "path": str(source), "nodes": 2 if pair == "C" else 1, "gpus_per_node": 8 if pair == "C" else 2,
                "tp_size": 16 if pair == "C" else 2, "mem_fraction_static": 0.85,
                "max_running_requests": 1, "chunked_prefill_size": 8192,
            },
        }
    return {
        "image": "parent-pinned-image", "repo": str(tmp_path / "repo"), "local_mount": str(tmp_path),
        "population_dir": str(personal / "population"), "run_root": str(personal / "runs"),
        "shared_dir": str(tmp_path / "records"), "num_rollout": 0, "context_tokens": 131072,
        "startup_timeout": 1800, "request_timeout": 3600, "teacher_port": 30000,
        "teacher_dist_port": 29501, "pairs": pairs,
    }


@pytest.mark.parametrize("pair", ["A", "B", "C"])
def test_selected_pair_scope_and_native_commands(config, tmp_path, pair):
    path = tmp_path / "config.json"
    selected = config["pairs"][pair]
    config["pairs"] = {pair: selected, "unselected": {"path": "/outside/never-inspected"}}
    path.write_text(json.dumps(config))
    assert worker._load_config(path, pair) == config
    head = {"ip": "10.0.0.7"}
    for rank in range(selected["teacher"]["nodes"]):
        assert worker._teacher_command(config, pair, rank, head) == [
            sys.executable, "-B", "-m", "sglang.launch_server", "--model-path", selected["teacher"]["path"],
            "--host", "0.0.0.0", "--port", "30000", "--nnodes", str(selected["teacher"]["nodes"]),
            "--node-rank", str(rank), "--dist-init-addr", "10.0.0.7:29501", "--tp-size", str(selected["teacher"]["tp_size"]),
            "--dtype", "bfloat16", "--context-length", "131072", "--mem-fraction-static", "0.85",
            "--max-running-requests", "1", "--chunked-prefill-size", "8192", "--disable-cuda-graph",
            "--enable-deterministic-inference", "--attention-backend", "fa3", "--linear-attn-prefill-backend", "triton",
        ]
    for rollouts in (0, 100):
        config["num_rollout"] = rollouts
        argv = worker._student_command(config, pair, {"url": "http://10.0.0.7:30000/generate"}, tmp_path / "local")
        assert argv[:4] == [sys.executable, "-B", "-m", "tests.manual.agent_opd.run_qwen35_opd"]
        values = dict(zip(argv[4::2], argv[5::2], strict=True))
        assert values == {
            "--pair": pair, "--student": selected["student"]["path"], "--teacher": selected["teacher"]["path"],
            "--teacher-url": "http://10.0.0.7:30000/generate", "--population-dir": config["population_dir"],
            "--output-root": str(Path(config["run_root"]) / "student"),
            "--shared-dir": str(Path(config["shared_dir"]) / "student"), "--local-root": str(tmp_path / "local"),
            "--gpus-per-node": "8", "--student-engine-gpus": str(selected["student"]["engine_gpus"]),
            "--tensor-model-parallel-size": str(selected["student"]["tp_size"]), "--max-tokens-per-gpu": "131072",
            "--sglang-mem-fraction-static": "0.7", "--sglang-max-running-requests": "1",
            "--sglang-chunked-prefill-size": "8192", "--sglang-router-request-timeout-secs": "3600",
            "--startup-timeout": "1800", "--num-rollout": str(rollouts),
        }
    selected["teacher"]["path"] = str(Path(selected["teacher"]["path"]).parent)
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="exactly approved"):
        worker._load_config(path, pair)


def test_readiness_checks_health_and_exact_model_identity(config, tmp_path, monkeypatch):
    expected = config["pairs"]["A"]["teacher"]["path"]
    calls = []
    process = SimpleNamespace(poll=lambda: None)
    def get(url, timeout):
        calls.append((url, timeout))
        return SimpleNamespace(raise_for_status=lambda: None, json=lambda: {"model_path": expected})
    monkeypatch.setattr(worker.requests, "get", get)
    assert worker._wait_teacher_ready(process, "http://teacher:30000", expected, tmp_path / "finished", 5) == {"model_path": expected}
    assert calls == [("http://teacher:30000/health", 5), ("http://teacher:30000/model_info", 5)]
    with pytest.raises(ValueError, match="configured source"):
        worker._wait_teacher_ready(process, "http://teacher:30000", expected + "/other", tmp_path / "finished", 5)
    process.poll = lambda: 23
    process.args = ["native", "server"]
    with pytest.raises(subprocess.CalledProcessError) as caught:
        worker._wait_teacher_ready(process, "http://teacher:30000", expected, tmp_path / "finished", 5)
    assert caught.value.returncode == 23


def test_peer_can_finish_before_head_without_deadlock_and_environment_preserves_platform_values(tmp_path, monkeypatch):
    platform = {"NCCL_SOCKET_IFNAME": "platform-eth", "NCCL_IB_HCA": "mlx5_0:1", "NCCL_CUSTOM": "untouched", "UCX_TLS": "rc", "CUDA_VISIBLE_DEVICES": "4,7"}
    monkeypatch.setattr(os, "environ", {**os.environ, **platform})
    worker._worker_environment(tmp_path / "cache")
    assert all(os.environ[key] == value for key, value in platform.items())
    evidence = {"job": "test-job", "pair": "C", "ip": "10.0.0.7"}
    worker._write_json(tmp_path / "student-finished.json", {"status": "failed", "returncode": 17})
    assert worker._teacher_head(tmp_path, 1, evidence, 1) is None
    assert worker._teacher_head(tmp_path, 0, evidence, 1) is None
    (tmp_path / "student-finished.json").unlink()
    assert worker._teacher_head(tmp_path, 0, evidence, 1) == evidence
    assert worker._teacher_head(tmp_path, 1, evidence, 1) == evidence


def _execution(config, tmp_path, monkeypatch, role):
    directory = Path(config["shared_dir"]) / "test-job" / "A"
    directory.mkdir(parents=True)
    monkeypatch.setattr(worker, "_worker_environment", lambda local: None)
    monkeypatch.setattr(worker, "_allocation", lambda *args: {
        "job": "test-job", "pair": "A", "ip": "10.0.0.7", "nodes": 1, "gpu_devices": ["fixture H800"],
    })
    ready = {
        "status": "ready", "job": "test-job", "pair": "A", "ip": "10.0.0.7",
        "url": "http://10.0.0.7:30000/generate", "model_info": {"model_path": config["pairs"]["A"]["teacher"]["path"]},
    }
    if role == "student":
        worker._write_json(directory / "teacher-ready.json", ready)
    return directory, ready


@pytest.mark.parametrize("returncode", [0, 17, -9])
def test_student_returncode_and_failure_finally_are_faithful(config, tmp_path, monkeypatch, returncode):
    directory, ready = _execution(config, tmp_path, monkeypatch, "student")
    process = SimpleNamespace(wait=lambda: returncode, returncode=returncode, poll=lambda: returncode)
    monkeypatch.setattr(worker.subprocess, "Popen", lambda *args, **kwargs: process)
    # Optional evidence failures must not block a healthy child or its required lifecycle marker.
    monkeypatch.setattr(worker, "_record_receipt", lambda *args: None)
    assert worker._run_student(config, "A", 0, directory, tmp_path / "local") == returncode
    finished = json.loads((directory / "student-finished.json").read_text())
    assert finished["returncode"] == returncode
    assert finished["status"] == ("native_execution_succeeded" if returncode == 0 else "failed")
    assert not (Path(config["run_root"]) / "student" / "A" / "test-job").exists()
    ready["model_info"]["model_path"] += "/wrong-model"
    worker._write_json(directory / "teacher-ready.json", ready)
    with pytest.raises(ValueError, match="identity/endpoint"):
        worker._run_student(config, "A", 0, directory, tmp_path / "other-local")
    assert json.loads((directory / "student-finished.json").read_text())["error_type"] == "ValueError"


@pytest.mark.parametrize("server_code", [None, 0, 23])
def test_teacher_publishes_head_before_launch_and_only_stops_own_child(config, tmp_path, monkeypatch, server_code):
    directory, ready = _execution(config, tmp_path, monkeypatch, "teacher")
    process = SimpleNamespace(pid=314, args=["native", "server"], poll=lambda: server_code)
    def launch(command, **kwargs):
        assert json.loads((directory / "teacher-head.json").read_text())["ip"] == "10.0.0.7"
        return process
    def ready_then_finish(*args):
        worker._write_json(directory / "student-finished.json", {"status": "failed", "returncode": 17})
        return ready["model_info"]
    stopped = []
    monkeypatch.setattr(worker.subprocess, "Popen", launch)
    monkeypatch.setattr(worker, "_wait_teacher_ready", ready_then_finish)
    monkeypatch.setattr(worker, "_stop_child", lambda child: stopped.append(child))
    if server_code is None:
        assert worker._run_teacher(config, "A", 0, directory, tmp_path / "local") == 0
        assert json.loads((directory / "teacher-ready.json").read_text())["url"] == ready["url"]
    else:
        with pytest.raises(subprocess.CalledProcessError if server_code else RuntimeError):
            worker._run_teacher(config, "A", 0, directory, tmp_path / "local")
    assert stopped == [process]
    assert json.loads((directory / "teacher-status-0.json").read_text())["returncode"] == server_code


def test_graceful_shutdown_targets_child_session_only(monkeypatch):
    signals = []
    process = SimpleNamespace(pid=314, poll=lambda: None, wait=lambda timeout: signals.append(("wait", timeout)))
    monkeypatch.setattr(worker.os, "killpg", lambda pid, signum: signals.append((pid, signum)))
    worker._stop_child(process)
    assert signals == [(314, signal.SIGTERM), ("wait", 60)]


def test_h800_allocation_is_checked_against_selected_role(config, monkeypatch):
    monkeypatch.setenv("KUBEBRAIN_REPLICA_TOTAL", "1")
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "test-job")
    monkeypatch.setenv("MILES_NODE_EXTERNAL_IP", "10.0.0.7")
    monkeypatch.setattr(worker.subprocess, "check_output", lambda *args, **kwargs: "H800, 81559 MiB, fixture\n" * 2)
    assert len(worker._allocation(0, "teacher", config, "A")["gpu_devices"]) == 2
    with pytest.raises(ValueError, match="requested H800 GPU count"):
        worker._allocation(0, "student", config, "A")
    monkeypatch.setattr(worker.subprocess, "check_output", lambda *args, **kwargs: "H200, 141000 MiB, fixture\n" * 2)
    with pytest.raises(ValueError, match="requested H800 GPU count"):
        worker._allocation(0, "teacher", config, "A")


def test_real_cpu_child_failure_is_recorded_and_auxiliary_tail_failure_is_soft(config, tmp_path, monkeypatch):
    directory, _ = _execution(config, tmp_path, monkeypatch, "student")
    monkeypatch.setattr(worker, "_student_command", lambda *args: [sys.executable, "-B", "-c", "raise SystemExit(17)"])
    Path(config["repo"]).mkdir()
    # A directory at the selected tail path forces an auxiliary write failure.
    (directory / "student-tail.log").mkdir()
    assert worker._run_student(config, "A", 0, directory, tmp_path / "local") == 17
    assert json.loads((directory / "student-finished.json").read_text())["returncode"] == 17
