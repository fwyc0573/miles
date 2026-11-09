"""CPU-only paired-worker contracts; model and HTTP evidence are local fixtures."""

import json
import os
import shlex
import signal
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from tests.manual.agent_opd import qwen35_pair_worker as worker
from tests.manual.agent_opd import rjob_warmup as rendezvous
from tests.manual.agent_opd import run_qwen35_opd as native
from tests.manual.agent_opd import submit_qwen35 as submitter


@pytest.fixture
def config(tmp_path, monkeypatch):
    personal = tmp_path / "cloud" / "ycfeng"
    sources = {name: tmp_path / "read-only" / name / "model" for name in ("27B", "35B-A3B", "397B-A17B")}
    monkeypatch.setattr(worker, "_PERSONAL_ROOT", personal)
    monkeypatch.setattr(worker, "_READ_ONLY_MODELS", set(sources.values()))
    pairs = {}
    for pair, source in zip(("A", "B", "C"), sources.values(), strict=True):
        pairs[pair] = {
            "startup_timeout": 9000 if pair == "C" else 1800,
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
        "teacher_dist_port": 29501, "pairs": pairs, "gpu_tag": "H800",
    }


@pytest.mark.parametrize("pair", ["A", "B", "C"])
@pytest.mark.parametrize("gpu_tag", ["H800", "H200"])
def test_selected_pair_scope_and_native_commands(config, tmp_path, pair, gpu_tag):
    config["gpu_tag"] = gpu_tag
    path = tmp_path / "config.json"
    selected = config["pairs"][pair]
    config["pairs"] = {pair: selected, "unselected": {"path": "/outside/never-inspected"}}
    config.pop("startup_timeout")
    path.write_text(json.dumps(config))
    resolved = worker._load_config(path, pair)
    budget = 9000 if pair == "C" else 1800
    assert resolved["startup_timeout"] == budget
    assert "startup_timeout" not in resolved["pairs"][pair]
    head = {"ip": "10.0.0.7"}
    for rank in range(selected["teacher"]["nodes"]):
        assert worker._teacher_command(resolved, pair, rank, head) == [
            sys.executable, "-B", "-m", "sglang.launch_server", "--model-path", selected["teacher"]["path"],
            "--host", "0.0.0.0", "--port", "30000", "--nnodes", str(selected["teacher"]["nodes"]),
            "--node-rank", str(rank), "--dist-init-addr", "10.0.0.7:29501", "--tp-size", str(selected["teacher"]["tp_size"]),
            "--dtype", "bfloat16", "--context-length", "131072", "--mem-fraction-static", "0.85",
            "--max-running-requests", "1", "--chunked-prefill-size", "8192", "--disable-cuda-graph",
            "--enable-deterministic-inference", "--attention-backend", "fa3", "--linear-attn-prefill-backend", "triton",
        ]
    for rollouts in (0, 100):
        resolved["num_rollout"] = rollouts
        argv = worker._student_command(resolved, pair, {"url": "http://10.0.0.7:30000/generate"}, tmp_path / "local")
        assert argv[:4] == [sys.executable, "-B", "-m", "tests.manual.agent_opd.run_qwen35_opd"]
        values = dict(zip(argv[4::2], argv[5::2], strict=True))
        assert values == {
            "--pair": pair, "--student": selected["student"]["path"], "--teacher": selected["teacher"]["path"],
            "--teacher-url": "http://10.0.0.7:30000/generate", "--population-dir": config["population_dir"],
            "--output-root": str(Path(config["run_root"]) / "student"),
            "--shared-dir": str(Path(config["shared_dir"]) / "student"), "--local-root": str(tmp_path),
            "--gpu-type": gpu_tag, "--gpus-per-node": "8", "--student-engine-gpus": str(selected["student"]["engine_gpus"]),
            "--tensor-model-parallel-size": str(selected["student"]["tp_size"]), "--max-tokens-per-gpu": "131072",
            "--sglang-mem-fraction-static": "0.7", "--sglang-max-running-requests": "1",
            "--sglang-chunked-prefill-size": "8192", "--sglang-router-request-timeout-secs": "3600",
            "--startup-timeout": str(budget), "--num-rollout": str(rollouts),
        }
        from tests.manual.agent_opd import run_qwen35_opd as student_cli
        assert student_cli._parser().parse_args(argv[4:]).gpu_type == gpu_tag
    selected["teacher"]["path"] = str(Path(selected["teacher"]["path"]).parent)
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="exactly approved"):
        worker._load_config(path, pair)


@pytest.mark.parametrize("pair", ["A", "B", "C"])
def test_startup_budget_is_not_a_submitted_role(config, pair):
    config["rdma_resources"] = ["fixture-rdma:1"]
    config["pairs"][pair]["student"]["nodes"] = 1
    for role in ("student", "teacher"):
        config["pairs"][pair][role].update(
            cpu_per_node=64, memory_gb_per_node=512, host_network=True, gang_start=True,
        )
    tasks = submitter._task_specs(config, pair)
    assert set(tasks) == {"student", "teacher"}
    assert sum(task["gpu"] * task["replica"] for task in tasks.values()) == (24 if pair == "C" else 10)
    assert tasks["student"]["is_critical"] is True
    assert tasks["teacher"]["is_critical"] is False
    assert tasks["teacher"]["custom_resources"] == (config["rdma_resources"] if pair == "C" else [])


@pytest.mark.parametrize("budget,error", [(None, KeyError), (0, ValueError)])
def test_selected_pair_startup_budget_is_required_and_positive(config, tmp_path, budget, error):
    if budget is None:
        del config["pairs"]["C"]["startup_timeout"]
    else:
        config["pairs"]["C"]["startup_timeout"] = budget
    path = tmp_path / "pair-config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(error, match="startup_timeout"):
        worker._load_config(path, "C")


def test_native_student_ray_socket_paths_fit_and_remain_job_isolated(config, monkeypatch):
    from ray._private.utils import validate_socket_filepath
    from tests.manual.agent_opd import run_qwen35_opd as student_cli

    local_directories = []

    def observe_local(local):
        local_directories.append(local)
        raise RuntimeError("Native student local directory observed before worker initialization")

    monkeypatch.setattr(student_cli, "_validate_args", lambda args: None)
    monkeypatch.setattr(student_cli, "_worker_environment", observe_local)
    monkeypatch.setenv("KUBEBRAIN_REPLICA", "0")
    monkeypatch.setenv("KUBEBRAIN_REPLICA_TOTAL", "1")
    sessions = (
        "session_2026-11-06_18-47-23_102563_1114",
        "session_2026-11-07_00-00-00_999999_4194303",
    )
    for job in ("exp-1107-021450-020231", "exp-1107-021450-020232"):
        monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", job)
        local = Path("/var/tmp") / f"qp-{job}-A-student-0"
        argv = worker._student_command(config, "A", {"url": "http://teacher:30000/generate"}, local)
        args = student_cli._parser().parse_args(argv[4:])
        with pytest.raises(RuntimeError, match="Native student local directory observed"):
            student_cli._run(args)
        # Use the native CLI's observed directory, not a copy of its composition logic.
        for session in sessions:
            filepath = str(local_directories[-1] / "ray" / session / "sockets" / "plasma_store")
            validate_socket_filepath(filepath)
        assert job.removeprefix("exp-") in local_directories[-1].name
    assert local_directories[0] != local_directories[1]


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


def _execution(config, tmp_path, monkeypatch, role, pair="A"):
    directory = Path(config["shared_dir"]) / "test-job" / pair
    directory.mkdir(parents=True)
    monkeypatch.setattr(worker, "_worker_environment", lambda local: None)
    monkeypatch.setattr(worker, "_allocation", lambda *args: {
        "job": "test-job", "pair": pair, "ip": "10.0.0.7", "nodes": config["pairs"][pair]["teacher"]["nodes"],
        "gpu_devices": ["fixture H800"],
    })
    ready = {
        "status": "ready", "job": "test-job", "pair": pair, "ip": "10.0.0.7",
        "url": "http://10.0.0.7:30000/generate", "model_info": {"model_path": config["pairs"][pair]["teacher"]["path"]},
    }
    if role == "student":
        worker._write_json(directory / "teacher-ready.json", ready)
    return directory, ready


@pytest.mark.parametrize("pair,ready_at,budget", [
    ("A", 1799, 1800), ("B", 1799, 1800), ("C", 8112, 9000), ("C", 9001, 9000),
])
def test_pair_startup_budget_waits_for_verified_teacher_before_student(config, tmp_path, monkeypatch, pair, ready_at, budget):
    path = tmp_path / "pair-config.json"
    # An old shared 1800-second value must not override the selected pair's budget.
    path.write_text(json.dumps(config))
    config = worker._load_config(path, pair)
    directory, ready = _execution(config, tmp_path, monkeypatch, "student", pair)
    (directory / "teacher-ready.json").unlink()
    clock = SimpleNamespace(now=0)
    launched_at, http_calls = [], []
    server = SimpleNamespace(poll=lambda: None)

    def get(url, timeout):
        http_calls.append((url, clock.now))
        assert clock.now >= ready_at
        return SimpleNamespace(raise_for_status=lambda: None, json=lambda: ready["model_info"])

    def sleep(seconds):
        clock.now += seconds
        if clock.now == ready_at:
            info = worker._wait_teacher_ready(
                server, "http://10.0.0.7:30000", config["pairs"][pair]["teacher"]["path"],
                directory / "student-finished.json", config["startup_timeout"],
            )
            worker._write_json(directory / "teacher-ready.json", {**ready, "model_info": info})

    def launch(command, **kwargs):
        assert (directory / "teacher-ready.json").exists()
        assert clock.now == ready_at
        assert command[command.index("--startup-timeout") + 1] == str(budget)
        launched_at.append(clock.now)
        return SimpleNamespace(wait=lambda: 0, poll=lambda: 0, returncode=0)

    monkeypatch.setattr(worker.time, "monotonic", lambda: clock.now)
    monkeypatch.setattr(worker.time, "sleep", sleep)
    monkeypatch.setattr(worker.requests, "get", get)
    monkeypatch.setattr(worker.subprocess, "Popen", launch)
    if ready_at < budget:
        assert worker._run_student(config, pair, 0, directory, tmp_path / "local") == 0
        assert launched_at == [ready_at]
        assert http_calls == [
            ("http://10.0.0.7:30000/health", ready_at), ("http://10.0.0.7:30000/model_info", ready_at),
        ]
    else:
        with pytest.raises(TimeoutError, match="RJob rendezvous did not publish"):
            worker._run_student(config, pair, 0, directory, tmp_path / "local")
        assert launched_at == http_calls == []
    assert clock.now == min(ready_at, budget)
    finished = json.loads((directory / "student-finished.json").read_text())
    assert finished["status"] == ("native_execution_succeeded" if ready_at < budget else "failed")


@pytest.mark.parametrize("outcome,stop_at", [("ready", 8113), ("error", 1000), ("timeout", 9686)])
def test_c_teacher_startup_loop_remains_bounded_and_native_errors_propagate(config, tmp_path, monkeypatch, outcome, stop_at):
    path = tmp_path / "pair-config.json"
    path.write_text(json.dumps(config))
    config = worker._load_config(path, "C")
    directory, ready = _execution(config, tmp_path, monkeypatch, "teacher", "C")
    clock = SimpleNamespace(now=686)
    server = SimpleNamespace(args=["native", "teacher"], code=None)
    server.poll = lambda: 23 if outcome == "error" and clock.now >= 1000 else server.code
    stopped, http_calls = [], []

    def get(url, timeout):
        if outcome != "ready" or clock.now < 8112:
            raise worker.requests.ConnectionError("Teacher is still loading")
        http_calls.append((url, clock.now))
        return SimpleNamespace(raise_for_status=lambda: None, json=lambda: ready["model_info"])

    def sleep(seconds):
        clock.now += seconds
        if outcome == "ready" and clock.now == 8113:
            assert (directory / "teacher-ready.json").exists()
            worker._write_json(directory / "student-finished.json", {"status": "native_execution_succeeded", "returncode": 0})

    def stop(process):
        stopped.append(process)
        if process.poll() is None:
            process.code = -15

    monkeypatch.setattr(worker.time, "monotonic", lambda: clock.now)
    monkeypatch.setattr(worker.time, "sleep", sleep)
    monkeypatch.setattr(worker.requests, "get", get)
    monkeypatch.setattr(worker.subprocess, "Popen", lambda *args, **kwargs: server)
    monkeypatch.setattr(worker, "_stop_child", stop)
    if outcome == "ready":
        assert worker._run_teacher(config, "C", 0, directory, tmp_path / "local") == 0
        assert http_calls == [
            ("http://10.0.0.7:30000/health", 8112), ("http://10.0.0.7:30000/model_info", 8112),
        ]
        published = json.loads((directory / "teacher-ready.json").read_text())
        assert published["model_info"] == ready["model_info"]
    else:
        error = subprocess.CalledProcessError if outcome == "error" else TimeoutError
        with pytest.raises(error) as caught:
            worker._run_teacher(config, "C", 0, directory, tmp_path / "local")
        if outcome == "error":
            assert caught.value.returncode == 23
        assert not (directory / "teacher-ready.json").exists()
    assert clock.now == stop_at
    assert stopped == [server]
    status = json.loads((directory / "teacher-status-0.json").read_text())
    assert status["returncode"] == (23 if outcome == "error" else None)
    assert status["status"] == ("student_finished" if outcome == "ready" else "failed")


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


@pytest.mark.parametrize("gpu_tag,wrong_gpu", [("H800", "H200"), ("H200", "H800")])
def test_allocation_is_checked_against_selected_hardware_and_role(config, monkeypatch, gpu_tag, wrong_gpu):
    config["gpu_tag"] = gpu_tag
    monkeypatch.setenv("KUBEBRAIN_REPLICA_TOTAL", "1")
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "test-job")
    monkeypatch.setenv("MILES_NODE_EXTERNAL_IP", "10.0.0.7")
    monkeypatch.setattr(worker.subprocess, "check_output", lambda *args, **kwargs: f"NVIDIA {gpu_tag}, fixture-memory, fixture-driver\n" * 2)
    assert len(worker._allocation(0, "teacher", config, "A")["gpu_devices"]) == 2
    with pytest.raises(ValueError, match=f"requested {gpu_tag} GPU count"):
        worker._allocation(0, "student", config, "A")
    monkeypatch.setattr(worker.subprocess, "check_output", lambda *args, **kwargs: f"NVIDIA {wrong_gpu}, fixture-memory, fixture-driver\n" * 2)
    with pytest.raises(ValueError, match=f"requested {gpu_tag} GPU count"):
        worker._allocation(0, "teacher", config, "A")


def test_real_cpu_child_failure_is_recorded_and_auxiliary_tail_failure_is_soft(config, tmp_path, monkeypatch):
    directory, _ = _execution(config, tmp_path, monkeypatch, "student")
    monkeypatch.setattr(worker, "_student_command", lambda *args: [sys.executable, "-B", "-c", "raise SystemExit(17)"])
    Path(config["repo"]).mkdir()
    # A directory at the selected tail path forces an auxiliary write failure.
    (directory / "student-tail.log").mkdir()
    assert worker._run_student(config, "A", 0, directory, tmp_path / "local") == 17
    assert json.loads((directory / "student-finished.json").read_text())["returncode"] == 17


@pytest.mark.parametrize("nodes,rank", [(2, 1), (4, 1), (4, 2), (4, 3)])
@pytest.mark.parametrize("returncode", [0, 17, -15])
def test_multi_node_student_peer_never_publishes_driver_completion(config, tmp_path, monkeypatch, nodes, rank, returncode):
    config["pairs"]["A"]["student"]["nodes"] = nodes
    directory, _ = _execution(config, tmp_path, monkeypatch, "student")
    monkeypatch.setattr(worker, "_allocation", lambda rank, *args: {"rank": rank, "nodes": nodes, "ip": "10.0.0.8"})
    process = SimpleNamespace(wait=lambda: returncode, poll=lambda: returncode, returncode=returncode)
    monkeypatch.setattr(worker.subprocess, "Popen", lambda *args, **kwargs: process)
    assert worker._run_student(config, "A", rank, directory, tmp_path / "local") == returncode
    assert not (directory / "student-finished.json").exists()
    status = json.loads((directory / f"student-status-{rank}.json").read_text())
    assert status["returncode"] == returncode and status["rank"] == rank


@pytest.mark.parametrize("nodes", [1, 2, 3, 4, 5])
def test_student_allocation_uses_configured_positive_replica_count(config, monkeypatch, nodes):
    config["pairs"]["A"]["student"]["nodes"] = nodes
    monkeypatch.setenv("KUBEBRAIN_REPLICA_TOTAL", str(nodes))
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "test-job")
    monkeypatch.setenv("MILES_NODE_EXTERNAL_IP", "10.0.0.8")
    monkeypatch.setattr(worker.subprocess, "check_output", lambda *args, **kwargs: "NVIDIA H800, memory, driver\n" * 8)
    for rank in range(nodes):
        evidence = worker._allocation(rank, "student", config, "A")
        assert evidence["nodes"] == nodes and evidence["rank"] == rank and len(evidence["gpu_devices"]) == 8
    with pytest.raises(ValueError, match="replica rank/count"):
        worker._allocation(nodes, "student", config, "A")
    monkeypatch.setenv("KUBEBRAIN_REPLICA_TOTAL", str(nodes + 1))
    with pytest.raises(ValueError, match="replica rank/count"):
        worker._allocation(0, "student", config, "A")


@pytest.fixture(params=[(2, "H200"), (4, "H800")], ids=["two-node-H200", "four-node-H800"])
def student_node(tmp_path, monkeypatch, request):
    nodes, gpu_tag = request.param
    args = SimpleNamespace(
        pair="A", student=tmp_path / "student", teacher=tmp_path / "teacher", student_nodes=nodes,
        output_root=tmp_path / "artifacts", shared_dir=tmp_path / "rendezvous", local_root=tmp_path / "local",
        gpu_type=gpu_tag, gpus_per_node=8, startup_timeout=3, megatron_path="/root/Megatron-LM", num_rollout=2,
    )
    records, cloud = args.shared_dir / "A" / "test-job", args.output_root / "A" / "test-job"
    events, submissions = [], []
    clock = SimpleNamespace(now=0, on_sleep=lambda: None)
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "test-job")
    monkeypatch.setenv("KUBEBRAIN_REPLICA_TOTAL", str(nodes))
    monkeypatch.setenv("KUBEBRAIN_REPLICA", "0")
    monkeypatch.setenv("PORT_AUTO0", "20000")
    monkeypatch.setenv("PORT_AUTO1", "20001")
    monkeypatch.setattr(native, "_check_tokenizers", lambda *args: events.append("tokenizers"))
    monkeypatch.setattr(native, "_record_memory", lambda path, stopped: path.write_text('{"counters": {}}\n'))
    monkeypatch.setattr(native.subprocess, "check_output", lambda *args, **kwargs: f"NVIDIA {gpu_tag}, memory, driver\n" * 8)

    def command(argv, **kwargs):
        events.append(("ray", argv))
        return SimpleNamespace(returncode=0)

    def backend(config):
        return SimpleNamespace(execute_train=lambda **kwargs: submissions.append((config.num_nodes, kwargs)))

    def sleep(seconds):
        clock.now += seconds
        clock.on_sleep()

    monkeypatch.setattr(native.subprocess, "run", command)
    monkeypatch.setattr(native.U.ExecuteTrainConfig, "create_backend", backend)
    monkeypatch.setattr(rendezvous.ray, "init", lambda **kwargs: events.append("ray-init"))
    monkeypatch.setattr(rendezvous.ray, "shutdown", lambda: events.append("ray-shutdown"))
    monkeypatch.setattr(rendezvous.ray, "nodes", lambda: [
        {"Alive": True, "Resources": {"GPU": 8}, "NodeManagerAddress": f"10.0.0.{rank + 7}", "NodeID": str(rank)}
        for rank in range(int(os.environ["KUBEBRAIN_REPLICA_TOTAL"]))
    ])
    monkeypatch.setattr(rendezvous.time, "monotonic", lambda: clock.now)
    monkeypatch.setattr(rendezvous.time, "sleep", sleep)

    def prepare(args, run):
        events.append("prepare-driver")
        return "--actor-num-nodes 1 --actor-num-gpus-per-node 8", {"megatron_model_type": "qwen3.5-4B", "final_hf": None}

    return SimpleNamespace(
        args=args, records=records, cloud=cloud, events=events, submissions=submissions, clock=clock, prepare=prepare,
    )


def test_multi_node_native_head_allocates_ray_only_not_more_trainer_nodes(student_node):
    node = student_node
    native._run(node.args, prepare_training=node.prepare)
    assert len(node.submissions) == 1 and node.submissions[0][0] == 1
    assert node.submissions[0][1]["num_gpus_per_node"] == 8
    assert "MILES_NODE_EXTERNAL_IP" not in node.submissions[0][1]["extra_env_vars"]
    cluster = json.loads((node.records / "cluster.json").read_text())["nodes"]
    assert len(cluster) == node.args.student_nodes and sum(rank["gpus"] for rank in cluster) == node.args.student_nodes * 8
    assert all(rank["gpus"] == 8 for rank in cluster)
    starts = [event[1] for event in node.events if isinstance(event, tuple) and "start" in event[1]]
    assert len(starts) == 1 and "--head" in starts[0] and starts[0][starts[0].index("--num-gpus") + 1] == "8"
    assert json.loads((node.records / "finished.json").read_text())["status"] == "native_execution_succeeded"


@pytest.mark.parametrize("status", ["native_execution_succeeded", "failed"])
def test_multi_node_native_peer_joins_until_driver_finishes_without_owning_shared_files(student_node, monkeypatch, status):
    node = student_node
    rank = node.args.student_nodes - 1
    monkeypatch.setenv("KUBEBRAIN_REPLICA", str(rank))
    node.records.mkdir(parents=True)
    node.cloud.mkdir(parents=True)
    (node.cloud / "head-owned").write_text("preserved")
    rendezvous._write_json(node.records / "run-ready.json", {"job": "test-job", "pair": "A", "run_dir": str(node.cloud)})
    rendezvous._write_json(node.records / "head.json", {"ip": "10.0.0.7", "port": 20000, "dashboard_port": 20001})
    completion = {"status": status, "rank": 0, "sentinel": "only the driver wrote this"}

    def finish():
        if node.clock.now == 2:
            rendezvous._write_json(node.records / "finished.json", completion)

    node.clock.on_sleep = finish
    if status == "failed":
        with pytest.raises(RuntimeError, match="driver replica failed"):
            native._run(node.args, prepare_training=node.prepare)
    else:
        native._run(node.args, prepare_training=node.prepare)
    assert node.clock.now == 2 and node.submissions == [] and "prepare-driver" not in node.events
    assert (node.cloud / "head-owned").read_text() == "preserved"
    assert json.loads((node.records / "finished.json").read_text()) == completion
    assert not (node.records / "training.json").exists() and not (node.records / "launch.json").exists()
    starts = [argv for name, argv in (event for event in node.events if isinstance(event, tuple)) if "start" in argv]
    assert len(starts) == 1 and "--head" not in starts[0] and "--address" in starts[0]
    assert starts[0][starts[0].index("--num-gpus") + 1] == "8"
    own = json.loads((node.records / f"training-{rank}.json").read_text())
    assert own["rank"] == rank and own["status"] == status


def test_multi_node_native_peer_missing_ray_head_times_out_before_driver(student_node, monkeypatch):
    node = student_node
    monkeypatch.setenv("KUBEBRAIN_REPLICA", "1")
    node.records.mkdir(parents=True)
    node.cloud.mkdir(parents=True)
    rendezvous._write_json(node.records / "run-ready.json", {"job": "test-job", "pair": "A", "run_dir": str(node.cloud)})
    with pytest.raises(TimeoutError, match="RJob rendezvous did not publish"):
        native._run(node.args, prepare_training=node.prepare)
    assert node.clock.now == 3 and node.submissions == []
    assert not (node.records / "finished.json").exists()


@pytest.mark.parametrize("error", [RuntimeError("driver failed"), SystemExit(143)])
def test_multi_node_native_head_failure_or_cancellation_publishes_completion(student_node, error):
    node = student_node

    def fail(*args):
        raise error

    with pytest.raises(type(error)):
        native._run(node.args, prepare_training=fail)
    assert json.loads((node.records / "finished.json").read_text())["status"] == "failed"
    assert node.submissions == []


@pytest.mark.parametrize("rank", [0, 1])
def test_multi_node_native_prepares_each_container_source_before_ray_join(student_node, monkeypatch, rank):
    node = student_node
    monkeypatch.setenv("KUBEBRAIN_REPLICA", str(rank))
    if rank:
        node.records.mkdir(parents=True)
        node.cloud.mkdir(parents=True)
        rendezvous._write_json(node.records / "run-ready.json", {"job": "test-job", "pair": "A", "run_dir": str(node.cloud)})
        rendezvous._write_json(node.records / "head.json", {"ip": "10.0.0.7", "port": 20000, "dashboard_port": 20001})
        rendezvous._write_json(node.records / "finished.json", {"status": "native_execution_succeeded"})
    prepared = []

    def prepare_node(args, run, node_rank):
        assert args.megatron_path == "/root/Megatron-LM" and run == node.cloud and node_rank == rank
        assert not any(isinstance(event, tuple) and "start" in event[1] for event in node.events)
        archive = run / "megatron_scoring_lifetime" / "source" / f"rank-{node_rank}"
        archive.mkdir(parents=True)
        (archive / "source-prepared").write_text("pinned container source prepared")
        prepared.append(archive)
        return {"archive_dir": str(archive)}

    native._run(node.args, prepare_training=node.prepare, prepare_node=prepare_node)
    assert len(prepared) == 1 and prepared[0].name == f"rank-{rank}"
    if rank:
        assert node.submissions == [] and "prepare-driver" not in node.events


def test_multi_node_native_peer_source_rejection_prevents_ray_join(student_node, monkeypatch):
    node = student_node
    monkeypatch.setenv("KUBEBRAIN_REPLICA", "1")
    node.records.mkdir(parents=True)
    node.cloud.mkdir(parents=True)
    rendezvous._write_json(node.records / "run-ready.json", {"job": "test-job", "pair": "A", "run_dir": str(node.cloud)})

    def reject(*args):
        raise ValueError("Unrecognized scoring schedule")

    with pytest.raises(ValueError, match="Unrecognized scoring schedule"):
        native._run(node.args, prepare_training=node.prepare, prepare_node=reject)
    assert node.submissions == []
    assert not any(isinstance(event, tuple) and "start" in event[1] for event in node.events)
    assert not (node.records / "finished.json").exists()


def test_multi_node_native_failed_local_initialization_preserves_preexisting_directory(student_node):
    node = student_node
    local = node.args.local_root / "qo-test-job"
    local.mkdir(parents=True)
    sentinel = local / "user-owned"
    sentinel.write_text("do not remove")
    with pytest.raises(FileExistsError):
        native._run(node.args, prepare_training=node.prepare)
    assert sentinel.read_text() == "do not remove"


@pytest.mark.parametrize("nodes,rank,failed_rank", [(2, 0, 1), (2, 1, 0), (4, 0, 1), (4, 0, 2), (4, 0, 3), (4, 1, 0), (4, 2, 0), (4, 3, 0)])
def test_multi_node_role_propagates_other_replica_failure_without_waiting_for_child(config, tmp_path, monkeypatch, nodes, rank, failed_rank):
    config["pairs"]["A"]["student"]["nodes"] = nodes
    directory, _ = _execution(config, tmp_path, monkeypatch, "student")
    monkeypatch.setattr(worker, "_allocation", lambda *args: {"rank": rank, "nodes": nodes, "ip": "10.0.0.8"})
    clock = SimpleNamespace(now=0)
    child = SimpleNamespace(returncode=None, poll=lambda: None)
    child.wait = lambda: pytest.fail("An unsupervised child wait would hang")
    stopped = []

    def sleep(seconds):
        clock.now += seconds
        marker = "student-finished.json" if rank else f"student-status-{failed_rank}.json"
        worker._write_json(directory / marker, {"status": "failed", "rank": failed_rank, "returncode": 17})

    def stop(process):
        stopped.append(process)
        process.returncode = -15

    monkeypatch.setattr(worker.time, "monotonic", lambda: clock.now)
    monkeypatch.setattr(worker.time, "sleep", sleep)
    monkeypatch.setattr(worker.subprocess, "Popen", lambda *args, **kwargs: child)
    monkeypatch.setattr(worker, "_stop_child", stop)
    with pytest.raises(RuntimeError, match="student.*replica.*failed"):
        worker._run_student(config, "A", rank, directory, tmp_path / "local")
    assert clock.now == 1 and stopped == [child]
    result = json.loads((directory / "student-finished.json").read_text())
    assert result["rank"] == 0
    if rank:
        assert result["returncode"] == 17


def test_two_node_role_peer_absent_teacher_readiness_is_bounded_without_global_completion(config, tmp_path, monkeypatch):
    config["pairs"]["A"]["student"]["nodes"] = 2
    config["startup_timeout"] = 3
    directory, _ = _execution(config, tmp_path, monkeypatch, "student")
    (directory / "teacher-ready.json").unlink()
    clock = SimpleNamespace(now=0)
    monkeypatch.setattr(worker.time, "monotonic", lambda: clock.now)
    monkeypatch.setattr(worker.time, "sleep", lambda seconds: setattr(clock, "now", clock.now + seconds))
    monkeypatch.setattr(worker.subprocess, "Popen", lambda *args, **kwargs: pytest.fail("Teacher was not ready"))
    with pytest.raises(TimeoutError, match="RJob rendezvous did not publish"):
        worker._run_student(config, "A", 1, directory, tmp_path / "local")
    assert clock.now == 3 and not (directory / "student-finished.json").exists()


@pytest.mark.parametrize("nodes", [1, 2, 3, 4, 5])
def test_student_command_transports_only_ray_node_count(config, tmp_path, nodes):
    config["pairs"]["A"]["student"].update(nodes=nodes, tp_size=4, engine_gpus=4)
    argv = worker._student_command(config, "A", {"url": "http://teacher:30000/generate"}, tmp_path / "local")
    args = native._parser().parse_args(argv[4:])
    assert args.student_nodes == nodes and args.gpus_per_node == 8 and args.tensor_model_parallel_size == 4
    train = native._training_args(args, tmp_path / "run")
    assert "--actor-num-nodes 1" in train and "--actor-num-gpus-per-node 8" in train
    assert "--tensor-model-parallel-size 4" in train and "--context-parallel-size 1" in train
    assert args.gpus_per_node // args.tensor_model_parallel_size == 2
    assert ("--student-nodes" in argv) == (nodes != 1)


def test_single_node_native_default_retains_driver_and_record_paths(student_node, monkeypatch):
    node = student_node
    del node.args.student_nodes
    monkeypatch.setenv("KUBEBRAIN_REPLICA_TOTAL", "1")
    native._run(node.args, prepare_training=node.prepare)
    assert node.submissions[0][0] == 1
    assert (node.records / "launch.json").exists() and (node.records / "training.json").exists()
    assert not (node.records / "finished.json").exists() and not (node.records / "run-ready.json").exists()


def test_multi_node_native_sigterm_stops_driver_and_publishes_failure(student_node, monkeypatch):
    node = student_node
    previous = signal.getsignal(signal.SIGTERM)
    monkeypatch.setattr(native.U.ExecuteTrainConfig, "create_backend", lambda config: SimpleNamespace(
        execute_train=lambda **kwargs: os.kill(os.getpid(), signal.SIGTERM),
    ))
    with pytest.raises(SystemExit) as caught:
        native._run(node.args, prepare_training=node.prepare)
    assert caught.value.code == 143 and signal.getsignal(signal.SIGTERM) == previous
    assert json.loads((node.records / "finished.json").read_text())["error_type"] == "SystemExit"
    assert not (node.args.local_root / "qo-test-job").exists()


@pytest.mark.parametrize("nodes,rank,failed_rank", [(2, 0, 1), (2, 1, 0), (4, 0, 2), (4, 0, 3), (4, 3, 0)])
def test_multi_node_role_real_child_is_cancelled_after_other_replica_failure(config, tmp_path, monkeypatch, nodes, rank, failed_rank):
    config["pairs"]["A"]["student"]["nodes"] = nodes
    directory, _ = _execution(config, tmp_path, monkeypatch, "student")
    Path(config["repo"]).mkdir()
    marker = "student-finished.json" if rank else f"student-status-{failed_rank}.json"
    worker._write_json(directory / marker, {"status": "failed", "rank": failed_rank, "returncode": 17})
    with pytest.raises(RuntimeError, match="student.*replica.*failed"):
        worker._run_student(
            config, "A", rank, directory, tmp_path / "local",
            command_builder=lambda *args: [sys.executable, "-B", "-c", "import time; time.sleep(60)"],
        )
    own = json.loads((directory / f"student-status-{rank}.json").read_text())
    assert own["returncode"] == -signal.SIGTERM
    assert json.loads((directory / "student-finished.json").read_text())["rank"] == 0


@pytest.mark.parametrize("nodes", [2, 4])
def test_multi_node_teacher_ignores_peer_completion_until_driver_finishes(config, tmp_path, monkeypatch, nodes):
    config["pairs"]["A"]["student"]["nodes"] = nodes
    directory, ready = _execution(config, tmp_path, monkeypatch, "teacher")
    clock = SimpleNamespace(now=0)
    process = SimpleNamespace(poll=lambda: None)
    stopped = []

    def sleep(seconds):
        clock.now += seconds
        if clock.now == 1:
            for rank in range(1, nodes):
                worker._write_json(directory / f"student-status-{rank}.json", {"status": "native_execution_succeeded", "rank": rank})
        else:
            assert not stopped and not (directory / "student-finished.json").exists()
            worker._write_json(directory / "student-finished.json", {"status": "native_execution_succeeded", "rank": 0})

    monkeypatch.setattr(worker.time, "monotonic", lambda: clock.now)
    monkeypatch.setattr(worker.time, "sleep", sleep)
    monkeypatch.setattr(worker.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(worker, "_wait_teacher_ready", lambda *args: ready["model_info"])
    monkeypatch.setattr(worker, "_stop_child", stopped.append)
    assert worker._run_teacher(config, "A", 0, directory, tmp_path / "local") == 0
    assert clock.now == 2 and stopped == [process]


def test_multi_node_native_existing_run_does_not_overwrite_driver_records(student_node):
    node = student_node
    node.records.mkdir(parents=True)
    node.cloud.mkdir(parents=True)
    original = {"status": "native_execution_succeeded", "sentinel": "another attempt owns these records"}
    for name in ("training.json", "finished.json"):
        rendezvous._write_json(node.records / name, original)
    with pytest.raises(FileExistsError):
        native._run(node.args, prepare_training=node.prepare)
    assert json.loads((node.records / "training.json").read_text()) == original
    assert json.loads((node.records / "finished.json").read_text()) == original


@pytest.mark.parametrize("nodes", [0, -1, True, 4.0, "4", None])
def test_student_node_config_requires_positive_integer(config, tmp_path, nodes):
    config["pairs"]["A"]["student"]["nodes"] = nodes
    path = tmp_path / "pair-config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="positive integer node count"):
        worker._load_config(path, "A")


@pytest.mark.parametrize("nodes", [0, -1])
def test_native_cli_rejects_nonpositive_student_nodes(config, tmp_path, monkeypatch, nodes):
    config["pairs"]["A"]["student"]["nodes"] = 1
    argv = worker._student_command(config, "A", {"url": "http://teacher:30000/generate"}, tmp_path / "local")
    args = native._parser().parse_args([*argv[4:], "--student-nodes", str(nodes)])
    monkeypatch.setattr(native, "_PERSONAL_ROOT", Path(config["population_dir"]).parent)
    monkeypatch.setattr(native, "_READ_ONLY_MODELS", {Path(config["pairs"]["A"]["teacher"]["path"])})
    with pytest.raises(ValueError, match="student_nodes must be positive"):
        native._validate_args(args)


@pytest.mark.parametrize("nodes,total,rank", [(0, 0, 0), (True, 1, 0), (4.0, 4, 0), (4, 3, 0), (4, 4, -1), (4, 4, 4)])
def test_native_allocation_rejects_invalid_count_or_rank_before_startup(student_node, monkeypatch, nodes, total, rank):
    node = student_node
    node.args.student_nodes = nodes
    monkeypatch.setenv("KUBEBRAIN_REPLICA_TOTAL", str(total))
    monkeypatch.setenv("KUBEBRAIN_REPLICA", str(rank))
    with pytest.raises(ValueError, match="replica rank/count"):
        native._run(node.args, prepare_training=node.prepare)
    assert node.events == node.submissions == [] and not node.cloud.exists()


def test_multi_node_native_each_rank_registers_eight_gpus_and_only_head_submits(student_node, monkeypatch):
    node = student_node
    prepared = []
    monkeypatch.setattr(rendezvous.socket, "gethostbyname", lambda hostname: f"10.0.0.{int(os.environ['KUBEBRAIN_REPLICA']) + 7}")
    platform = {"NCCL_SOCKET_IFNAME": "platform-nic", "NCCL_IB_HCA": "platform-hca", "UCX_TLS": "rc"}
    for key, value in platform.items():
        monkeypatch.setenv(key, value)

    def prepare_node(args, run, rank):
        assert "tokenizers" in node.events and run == node.cloud
        assert all(os.environ[key] == value for key, value in platform.items())
        assert len([event for event in node.events if isinstance(event, tuple) and "start" in event[1]]) == rank
        prepared.append(rank)
        return {"prepared_rank": rank}

    for rank in range(node.args.student_nodes):
        monkeypatch.setenv("KUBEBRAIN_REPLICA", str(rank))
        native._run(node.args, prepare_training=node.prepare, prepare_node=prepare_node)
        assert not (node.args.local_root / "qo-test-job").exists()
        own = node.records / ("training.json" if rank == 0 else f"training-{rank}.json")
        assert json.loads(own.read_text())["status"] == "native_execution_succeeded"
    assert prepared == list(range(node.args.student_nodes))
    assert len(node.submissions) == node.events.count("prepare-driver") == 1
    assert node.submissions[0][0] == 1
    starts = [event[1] for event in node.events if isinstance(event, tuple) and "start" in event[1]]
    assert len(starts) == node.args.student_nodes and sum("--head" in argv for argv in starts) == 1
    for rank, argv in enumerate(starts):
        assert argv[argv.index("--num-gpus") + 1] == "8"
        assert argv[argv.index("--node-ip-address") + 1] == f"10.0.0.{rank + 7}"
        if rank:
            assert argv[argv.index("--address") + 1] == "10.0.0.7:20000"
    assert json.loads((node.records / "finished.json").read_text())["rank"] == 0


def test_multi_node_head_waits_for_exact_node_and_gpu_totals_before_submit(student_node, monkeypatch):
    node = student_node
    snapshots = []
    for count, deficit in ((node.args.student_nodes - 1, 0), (node.args.student_nodes + 1, 0), (node.args.student_nodes, 1), (node.args.student_nodes, 0)):
        snapshots.append([
            {"Alive": True, "Resources": {"GPU": 8 - (deficit if rank == 0 else 0)},
             "NodeManagerAddress": f"10.0.0.{rank + 7}", "NodeID": str(rank)}
            for rank in range(count)
        ])
    node.args.startup_timeout = 10
    monkeypatch.setattr(rendezvous.ray, "nodes", lambda: snapshots[min(node.clock.now // 2, 3)])
    native._run(node.args, prepare_training=node.prepare)
    assert node.clock.now == 6 and len(node.submissions) == 1
    cluster = json.loads((node.records / "cluster.json").read_text())["nodes"]
    assert len(cluster) == node.args.student_nodes and sum(rank["gpus"] for rank in cluster) == node.args.student_nodes * 8


def test_multi_node_head_incomplete_cluster_times_out_without_trainer_submit(student_node, monkeypatch):
    node = student_node
    monkeypatch.setattr(rendezvous.ray, "nodes", lambda: [
        {"Alive": True, "Resources": {"GPU": 8}, "NodeManagerAddress": f"10.0.0.{rank + 7}", "NodeID": str(rank)}
        for rank in range(node.args.student_nodes - 1)
    ])
    with pytest.raises(TimeoutError, match="Ray did not register"):
        native._run(node.args, prepare_training=node.prepare)
    assert node.submissions == [] and not (node.records / "cluster.json").exists()
    assert json.loads((node.records / "finished.json").read_text())["status"] == "failed"


def test_four_node_preparation_argv_and_resource_count(config, tmp_path, monkeypatch):
    selected = config["pairs"]["A"]
    selected["student"].update(nodes=4, tp_size=4, engine_gpus=4)
    selected["teacher"].update(nodes=1, gpus_per_node=4, tp_size=4)
    config["rdma_resources"] = ["fixture-rdma:1"]
    for role in ("student", "teacher"):
        selected[role].update(cpu_per_node=64, memory_gb_per_node=512, host_network=True, gang_start=True)
    path = tmp_path / "pair-config.json"
    path.write_text(json.dumps(config))
    resolved = worker._load_config(path, "A")
    tasks = submitter._task_specs(resolved, "A")
    assert tasks["student"]["replica"] == 4 and tasks["student"]["gpu"] == 8
    assert tasks["teacher"]["replica"] == 1 and tasks["teacher"]["gpu"] == 4
    assert sum(task["replica"] * task["gpu"] for task in tasks.values()) == 36
    assert tasks["student"]["custom_resources"] == config["rdma_resources"]
    argv = worker._student_command(resolved, "A", {"url": "http://teacher:30000/generate"}, tmp_path / "local")
    args = native._parser().parse_args(argv[4:])
    monkeypatch.setattr(native, "_PERSONAL_ROOT", Path(config["population_dir"]).parent)
    monkeypatch.setattr(native, "_READ_ONLY_MODELS", {Path(selected["teacher"]["path"])})
    native._validate_args(args)
    train = shlex.split(native._training_args(args, tmp_path / "run"))
    assert args.student_nodes == 4 and args.student_engine_gpus == 4
    for flag, value in (("--actor-num-nodes", "1"), ("--actor-num-gpus-per-node", "8"),
                        ("--tensor-model-parallel-size", "4"), ("--context-parallel-size", "1")):
        assert train[train.index(flag) + 1] == value
