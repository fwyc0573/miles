"""Coordinate separately allocated frozen-teacher and colocated-student tasks.

The parent owns the pinned image, RJob task allocations and mounted model assets.
Run with that image's /opt/sglang/bin/python3 and its existing CUDA environment:
    python3 -B -m tests.manual.agent_opd.qwen35_pair_worker \
        --config /data/ycfeng/task/pair.json --pair A --role teacher
Use the same config/pair with --role student on the critical student task.
Teacher replicas use native SGLang distributed initialization, not student Ray.
This CUDA/H800-only worker never installs packages or controls platform jobs.
"""

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import requests
from scripts.run_glm47_flash_agent_opd import _training_env
from tests.manual.agent_opd.prepare_qwen35 import CONTEXT_TOKENS
from tests.manual.agent_opd.rjob_warmup import _wait_file, _worker_environment, _write_json
from tests.manual.agent_opd.run_qwen35_opd import _PAIRS, _PERSONAL_ROOT, _READ_ONLY_MODELS, _record_receipt

from miles.utils.external_utils import command_utils as U


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--pair", choices=tuple(_PAIRS), required=True)
    parser.add_argument("--role", choices=("teacher", "student"), required=True)
    return parser


def _load_config(path: Path, pair: str) -> dict:
    config = json.loads(path.read_text())
    allocation = config["pairs"][pair]
    # Only the selected pair is inspected. Source paths need not be opened here.
    for model in (allocation["student"], allocation["teacher"]):
        source = Path(model["path"])
        if not source.is_absolute() or ".." in source.parts:
            raise ValueError("Model paths must be absolute without parent traversal")
        if not source.is_relative_to(_PERSONAL_ROOT) and source not in _READ_ONLY_MODELS:
            raise ValueError("Model path must be personal or an exactly approved read-only source")
        resolved = source.resolve()
        if not resolved.is_relative_to(_PERSONAL_ROOT) and resolved not in _READ_ONLY_MODELS:
            raise ValueError("Resolved model path leaves the authorized source roots")
        for key in ("gpus_per_node", "tp_size", "max_running_requests", "chunked_prefill_size"):
            if model[key] <= 0:
                raise ValueError(f"{key} must be positive")
        if not 0 < model["mem_fraction_static"] < 1:
            raise ValueError("mem_fraction_static must be in (0, 1)")
    for key in ("population_dir", "run_root"):
        directory = Path(config[key])
        if ".." in directory.parts or not directory.resolve().is_relative_to(_PERSONAL_ROOT):
            raise ValueError(f"{key} must stay under {_PERSONAL_ROOT}")
    mount = Path(config["local_mount"])
    for directory in (mount, path.absolute(), Path(config["repo"]), Path(config["shared_dir"])):
        if not directory.is_absolute() or ".." in directory.parts or directory.is_relative_to("/mnt"):
            raise ValueError("Config, repo and rendezvous must use mounted local paths, not cloud paths")
        if not directory.is_relative_to(mount):
            raise ValueError("Config, repo and rendezvous must stay in local_mount")
    if not config["image"] or config["context_tokens"] != CONTEXT_TOKENS or config["num_rollout"] not in (0, 100):
        raise ValueError("A pinned image, accepted 131072-token context and 0/100 rollouts are required")
    for key in ("startup_timeout", "request_timeout"):
        if config[key] <= 0:
            raise ValueError(f"{key} must be positive")
    for key in ("teacher_port", "teacher_dist_port"):
        if not 0 < config[key] < 65536:
            raise ValueError(f"{key} must be a TCP port")
    student, teacher = allocation["student"], allocation["teacher"]
    if student["path"] == teacher["path"]:
        raise ValueError("Student and teacher must use distinct model assets")
    if student["engine_gpus"] <= 0 or student["max_tokens_per_gpu"] <= 0:
        raise ValueError("The student requires positive engine/token capacity")
    if student["gpus_per_node"] % student["tp_size"] or student["gpus_per_node"] % student["engine_gpus"]:
        raise ValueError("Student GPUs must divide into complete trainer TP ranks and rollout engines")
    if teacher["nodes"] <= 0:
        raise ValueError("Teacher node count must be positive")
    if teacher["tp_size"] != teacher["nodes"] * teacher["gpus_per_node"]:
        raise ValueError("Teacher TP must span exactly its separately allocated GPUs")
    return config


def _allocation(rank: int, role: str, config: dict, pair: str) -> dict:
    model = config["pairs"][pair][role]
    nodes = model["nodes"] if role == "teacher" else 1
    if int(os.environ["KUBEBRAIN_REPLICA_TOTAL"]) != nodes or not 0 <= rank < nodes:
        raise ValueError(f"Platform replica rank/count differs from the {role} allocation")
    rows = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], text=True
    ).splitlines()
    if len(rows) != model["gpus_per_node"] or any("H800" not in row.split(",")[0] for row in rows):
        raise ValueError(f"{role} allocation does not match its requested H800 GPU count: {rows}")
    return {
        "job": os.environ["KUBEBRAIN_RJOB_NAME"], "pair": pair, "role": role, "rank": rank,
        "nodes": nodes, "hostname": socket.gethostname(), "ip": os.environ["MILES_NODE_EXTERNAL_IP"],
        "gpu_devices": rows, "model_path": model["path"], "image": config["image"],
    }


def _teacher_command(config: dict, pair: str, rank: int, head: dict) -> list[str]:
    teacher = config["pairs"][pair]["teacher"]
    return [
        sys.executable, "-B", "-m", "sglang.launch_server", "--model-path", teacher["path"],
        "--host", "0.0.0.0", "--port", str(config["teacher_port"]),
        "--nnodes", str(teacher["nodes"]), "--node-rank", str(rank),
        "--dist-init-addr", f"{head['ip']}:{config['teacher_dist_port']}", "--tp-size", str(teacher["tp_size"]),
        "--dtype", "bfloat16", "--context-length", str(config["context_tokens"]),
        "--mem-fraction-static", str(teacher["mem_fraction_static"]),
        "--max-running-requests", str(teacher["max_running_requests"]),
        "--chunked-prefill-size", str(teacher["chunked_prefill_size"]),
        "--disable-cuda-graph", "--enable-deterministic-inference", "--attention-backend", "fa3",
        "--linear-attn-prefill-backend", "triton",
    ]


def _student_command(config: dict, pair: str, ready: dict, local: Path) -> list[str]:
    student, teacher = config["pairs"][pair]["student"], config["pairs"][pair]["teacher"]
    # The native CLI owns job scoping; another job directory exceeds Ray's Unix socket path limit.
    return [
        sys.executable, "-B", "-m", "tests.manual.agent_opd.run_qwen35_opd", "--pair", pair,
        "--student", student["path"], "--teacher", teacher["path"], "--teacher-url", ready["url"],
        "--population-dir", config["population_dir"], "--output-root", str(Path(config["run_root"]) / "student"),
        "--shared-dir", str(Path(config["shared_dir"]) / "student"), "--local-root", str(local.parent),
        "--gpus-per-node", str(student["gpus_per_node"]), "--student-engine-gpus", str(student["engine_gpus"]),
        "--tensor-model-parallel-size", str(student["tp_size"]),
        "--max-tokens-per-gpu", str(student["max_tokens_per_gpu"]),
        "--sglang-mem-fraction-static", str(student["mem_fraction_static"]),
        "--sglang-max-running-requests", str(student["max_running_requests"]),
        "--sglang-chunked-prefill-size", str(student["chunked_prefill_size"]),
        "--sglang-router-request-timeout-secs", str(config["request_timeout"]),
        "--startup-timeout", str(config["startup_timeout"]), "--num-rollout", str(config["num_rollout"]),
    ]


def _check_server(process: subprocess.Popen) -> None:
    code = process.poll()
    if code is not None:
        if code:
            raise subprocess.CalledProcessError(code, process.args)
        raise RuntimeError("Frozen teacher server exited unexpectedly with returncode=0")


def _teacher_head(directory: Path, rank: int, evidence: dict, timeout: int) -> dict | None:
    address = directory / "teacher-head.json"
    finished = directory / "student-finished.json"
    if rank == 0:
        if finished.exists():
            return None
        # Publish before SGLang launch: peer nodes must join native distributed initialization.
        head = {key: evidence[key] for key in ("job", "pair", "ip")}
        _write_json(address, head)
        return head
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if finished.exists():
            return None
        if address.exists():
            head = _wait_file(address, deadline)
            if head["job"] != evidence["job"] or head["pair"] != evidence["pair"]:
                raise ValueError("Teacher head rendezvous belongs to a different job/pair")
            return head
        time.sleep(1)
    raise TimeoutError("Teacher head did not publish its native distributed address")


def _wait_teacher_ready(process: subprocess.Popen, url: str, model_path: str, finished: Path, timeout: int):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        _check_server(process)
        if finished.exists():
            return None
        try:
            health = requests.get(url + "/health", timeout=5)
            health.raise_for_status()
            response = requests.get(url + "/model_info", timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            time.sleep(1)
            continue
        info = response.json()
        if info["model_path"] != model_path:
            raise ValueError("Actual frozen teacher model_info path differs from the configured source")
        _check_server(process)
        return info
    raise TimeoutError("Frozen teacher did not pass /health and /model_info before the startup deadline")


def _stop_child(process: subprocess.Popen) -> None:
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            process.wait()
            return
        try:
            process.wait(timeout=60)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def _log_tail(source: Path, destination: Path) -> None:
    try:
        with source.open("rb") as stream:
            stream.seek(max(0, source.stat().st_size - 8192))
            destination.write_bytes(stream.read())
    except OSError as error:
        print("QWEN35_LOG_TAIL_UNVERIFIED", str(destination), type(error).__name__, str(error), flush=True)


def _run_teacher(config: dict, pair: str, rank: int, directory: Path, local: Path) -> int:
    process = None
    log_path = Path(config["run_root"]) / "teacher" / pair / directory.parent.name / f"rank-{rank}.log"
    result = {"status": "failed", "job": directory.parent.name, "pair": pair, "rank": rank, "returncode": None}
    try:
        _worker_environment(local)
        os.environ.update(_training_env(U.ExecuteTrainConfig(num_nodes=config["pairs"][pair]["teacher"]["nodes"])))
        evidence = _allocation(rank, "teacher", config, pair)
        _record_receipt(directory / f"teacher-node-{rank}.json", evidence)
        head = _teacher_head(directory, rank, evidence, config["startup_timeout"])
        if head is None:
            result.update(status="student_finished_before_launch")
            return 0
        command = _teacher_command(config, pair, rank, head)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("x") as log:
            # Inherit EVERY platform NCCL_*/RDMA/CUDA value; only local caches/proxies were prepared above.
            process = subprocess.Popen(command, cwd=config["repo"], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            if rank == 0:
                url = f"http://{head['ip']}:{config['teacher_port']}"
                info = _wait_teacher_ready(
                    process, url, config["pairs"][pair]["teacher"]["path"],
                    directory / "student-finished.json", config["startup_timeout"],
                )
                if info is not None:
                    # This file is required rendezvous; auxiliary receipts below remain soft gates.
                    _write_json(directory / "teacher-ready.json", {
                        **evidence, "status": "ready", "url": url + "/generate", "model_info": info,
                        "argv": command,
                    })
            while True:
                _check_server(process)
                if (directory / "student-finished.json").exists():
                    result.update(status="student_finished")
                    break
                time.sleep(1)
        return 0
    except BaseException as error:
        result.update(error_type=type(error).__name__, reason=str(error))
        raise
    finally:
        try:
            if process is not None:
                result["returncode"] = process.poll()
                _stop_child(process)
        finally:
            if process is not None:
                result["shutdown_returncode"] = process.poll()
            _record_receipt(directory / f"teacher-status-{rank}.json", result)
            if process is not None:
                _log_tail(log_path, directory / f"teacher-tail-{rank}.log")


def _run_student(config: dict, pair: str, rank: int, directory: Path, local: Path) -> int:
    process = None
    log_path = Path(config["run_root"]) / "student" / pair / f"{directory.parent.name}.log"
    result = {"status": "failed", "job": directory.parent.name, "pair": pair, "returncode": None}
    try:
        _worker_environment(local)
        evidence = _allocation(rank, "student", config, pair)
        _record_receipt(directory / "student-node.json", evidence)
        ready = _wait_file(directory / "teacher-ready.json", time.monotonic() + config["startup_timeout"])
        if (ready["status"], ready["job"], ready["pair"], ready["model_info"]["model_path"]) != (
            "ready", result["job"], pair, config["pairs"][pair]["teacher"]["path"],
        ) or ready["url"] != f"http://{ready['ip']}:{config['teacher_port']}/generate":
            raise ValueError("Teacher readiness identity/endpoint differs from the current job/pair/source")
        command = _student_command(config, pair, ready, local)
        _record_receipt(directory / "student-launch.json", {**evidence, "argv": command, "teacher_url": ready["url"]})
        # Do not create the job directory: the native CLI owns its exist_ok=False output creation.
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("x") as log:
            process = subprocess.Popen(command, cwd=config["repo"], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            result["returncode"] = process.wait()
        result["status"] = "native_execution_succeeded" if result["returncode"] == 0 else "failed"
        return result["returncode"]
    except BaseException as error:
        result.update(error_type=type(error).__name__, reason=str(error))
        raise
    finally:
        try:
            if process is not None:
                _stop_child(process)
                result["returncode"] = process.returncode
        finally:
            # Required lifecycle marker, including validation, readiness and native execution errors.
            _write_json(directory / "student-finished.json", result)
        if process is not None:
            _log_tail(log_path, directory / "student-tail.log")


def _terminate(signum, frame) -> None:
    raise SystemExit(128 + signum)


def main() -> int:
    args = _parser().parse_args()
    config = _load_config(args.config, args.pair)
    job = os.environ["KUBEBRAIN_RJOB_NAME"]
    if Path(job).name != job or job in ("", ".", ".."):
        raise ValueError("Platform job name must be one directory component")
    rank = int(os.environ["KUBEBRAIN_REPLICA"])
    directory = Path(config["shared_dir"]) / job / args.pair
    directory.mkdir(parents=True, exist_ok=True)
    local = Path("/var/tmp") / f"qp-{job}-{args.pair}-{args.role}-{rank}"
    signal.signal(signal.SIGTERM, _terminate)
    try:
        if args.role == "student":
            code = _run_student(config, args.pair, rank, directory, local)
        else:
            code = _run_teacher(config, args.pair, rank, directory, local)
    except subprocess.CalledProcessError as error:
        print("QWEN35_NATIVE_CHILD_FAILED", error.returncode, str(error), flush=True)
        code = error.returncode
    # Retain raw subprocess returncodes in records; expose conventional signal exit status to the shell.
    return 128 - code if code < 0 else code


if __name__ == "__main__":
    sys.exit(main())
