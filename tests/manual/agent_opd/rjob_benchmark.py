"""Evaluate original and post-update GLM weights with the native SWE benchmark.

Each four-GPU replica serves one TP4 engine. Four native SWE pipelines use the
frozen seeds and execute the original tools and unit-test grader. Original-model
evaluation can run while training prepares the post-update model. All outputs
are disposable and remain on the personal cloud.
"""

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from safetensors import safe_open

from tests.manual.agent_opd.rjob_warmup import _worker_environment


def _save(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n")


def _weights(path: Path) -> dict:
    tensors = {}
    for shard in sorted(path.glob("*.safetensors")):
        with safe_open(shard, framework="pt", device="cpu") as weights:
            for name in weights.keys():
                if name in tensors:
                    raise ValueError(f"Duplicate tensor in checkpoint: {name}")
                value = weights.get_slice(name)
                shape = value.get_shape()
                selection = tuple(slice(0, min(size, 4)) for size in shape)
                sample = value[selection].contiguous().view(-1).float().numpy().tobytes()
                tensors[name] = {"shape": shape, "sample_sha256": hashlib.sha256(sample).hexdigest()}
    if not tensors:
        raise ValueError("Checkpoint contains no safetensor weights")
    return tensors


def _check_export(original: Path, updated: Path) -> dict:
    identity = json.loads((updated / "learning_identity.json").read_text())
    if identity["completed_optimizer_updates"] != 20 or identity["rollout_id"] != 19:
        raise ValueError("Benchmark must consume weights saved after update20")
    if not (updated / ".complete").is_file():
        raise ValueError("Native checkpoint export is incomplete")
    before, after = _weights(original), _weights(updated)
    if {key: value["shape"] for key, value in before.items()} != {key: value["shape"] for key, value in after.items()}:
        raise ValueError("Exported model tensor names/shapes differ from the original student")
    changed = sum(before[key]["sample_sha256"] != value["sample_sha256"] for key, value in after.items())
    if not changed:
        raise ValueError("No sampled exported tensor values changed after learning")
    return {
        "identity": identity,
        "tensor_count": len(after),
        "changed_tensor_samples": changed,
        "comparison_scope": "Names/shapes of every tensor; at most four values per dimension for value comparison",
    }


def _start_server(path: Path, original: Path, version: int, args, output: Path):
    url = f"http://127.0.0.1:{os.environ['PORT_AUTO0']}"
    model = f"agent-opd-step{version}"
    command = [
        sys.executable,
        "-m",
        "sglang.launch_server",
        "--model-path",
        str(path),
        "--tokenizer-path",
        str(original),
        "--served-model-name",
        model,
        "--weight-version",
        str(version),
        "--host",
        "0.0.0.0",
        "--port",
        os.environ["PORT_AUTO0"],
        "--tp-size",
        str(args.engine_gpus),
        "--dtype",
        "bfloat16",
        "--load-format",
        "safetensors",
        "--context-length",
        str(args.context_tokens),
        "--mem-fraction-static",
        str(args.memory_fraction),
        "--max-running-requests",
        str(args.seed_concurrency),
        "--chunked-prefill-size",
        str(args.prefill_tokens),
        "--disable-cuda-graph",
        "--enable-deterministic-inference",
        "--attention-backend",
        "fa3",
        "--moe-runner-backend",
        "triton",
        "--reasoning-parser",
        "glm45",
        "--tool-call-parser",
        "glm47",
        "--log-requests",
        "--log-requests-level",
        "1",
        "--log-requests-format",
        "json",
    ]
    environment = dict(os.environ, CUDA_VISIBLE_DEVICES=",".join(map(str, range(args.engine_gpus))))
    log = (output / f"server-{version}.log").open("w")
    process = subprocess.Popen(command, env=environment, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    return {
        "process": process,
        "log": log,
        "url": url,
        "model": model,
        "version": version,
        "checkpoint": str(path),
        "command": command,
    }


def _wait_server(server: dict, timeout: int) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if server["process"].poll() is not None:
            raise RuntimeError(f"SGLang step{server['version']} exited before readiness")
        try:
            response = requests.get(server["url"] + "/model_info", timeout=5)
            response.raise_for_status()
            info = response.json()
            if info["model_path"] != server["checkpoint"] or str(info["weight_version"]) != str(server["version"]):
                raise ValueError("Actual engine checkpoint/version differs from the benchmark identity")
            return info
        except requests.RequestException:
            time.sleep(2)
    raise TimeoutError("SGLang benchmark server readiness deadline")


def _run_seed(server: dict, seed: int, args, output: Path) -> int:
    environment = dict(os.environ, PYTHONPATH=args.native_pythonpath)
    command = [
        str(args.native_python),
        "-B",
        str(Path(__file__).with_name("native_benchmark.py")),
        "--membership",
        str(args.membership),
        "--url",
        server["url"],
        "--model",
        server["model"],
        "--version",
        str(server["version"]),
        "--seed",
        str(seed),
        "--sandbox-backend",
        args.sandbox_backend,
        "--output",
        str(output / f"step{server['version']}" / f"seed-{seed}"),
        "--server-log",
        str(output / f"server-{server['version']}.log"),
    ]
    if args.task_index is not None:
        command.extend(["--task-index", str(args.task_index)])
    with (output / f"native-{server['version']}-{seed}.log").open("w") as log:
        return subprocess.run(
            command, env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=args.benchmark_timeout
        ).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--student", type=Path, required=True)
    parser.add_argument("--updated", type=Path)
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--native-python", type=Path, required=True)
    parser.add_argument("--native-pythonpath", required=True)
    parser.add_argument("--task-index", type=int)
    parser.add_argument("--sandbox-backend", choices=("acs", "basemind"), default="acs")
    parser.add_argument("--seeds", nargs="+", type=int)
    parser.add_argument("--engine-gpus", type=int, default=4)
    parser.add_argument("--context-tokens", type=int, default=131072)
    parser.add_argument("--memory-fraction", type=float, default=0.75)
    parser.add_argument("--prefill-tokens", type=int, default=8192)
    parser.add_argument("--seed-concurrency", type=int, default=4)
    parser.add_argument("--startup-timeout", type=int, default=600)
    parser.add_argument("--benchmark-timeout", type=int, default=21600)
    args = parser.parse_args()
    for path in (args.student, args.membership, args.output_root):
        path.relative_to("/mnt/codesign-exp/ycfeng")
    if args.updated is not None:
        args.updated.relative_to("/mnt/codesign-exp/ycfeng")
    output = args.output_root / os.environ["KUBEBRAIN_RJOB_NAME"]
    output.mkdir(parents=True, exist_ok=False)
    local = Path("/var/tmp") / f"ao-bench-{os.environ['KUBEBRAIN_RJOB_NAME']}"
    _worker_environment(local)
    servers = []
    try:
        if args.updated is not None:
            _save(output / "export-validation.json", _check_export(args.student, args.updated))
        subprocess.run(["nvidia-smi", "-L"], check=True)
        path, version = (args.student, 0) if args.updated is None else (args.updated, 20)
        servers.append(_start_server(path, args.student, version, args, output))
        for server in servers:
            _save(output / f"engine-{server['version']}.json", _wait_server(server, args.startup_timeout))
        membership = json.loads(args.membership.read_text())
        seeds = membership["seeds"] if args.seeds is None else args.seeds
        if not seeds or len(set(seeds)) != len(seeds) or any(seed not in membership["seeds"] for seed in seeds):
            raise ValueError("Benchmark seeds differ from the frozen membership")
        with ThreadPoolExecutor(max_workers=args.seed_concurrency) as pool:
            futures = [pool.submit(_run_seed, server, seed, args, output) for server in servers for seed in seeds]
            exits = [future.result() for future in futures]
        _save(output / "pipeline-exits.json", {"exit_codes": exits})
        print("AGENT_OPD_BENCHMARK_FINISHED", str(output), exits, flush=True)
    finally:
        for server in servers:
            if server["process"].poll() is None:
                os.killpg(server["process"].pid, signal.SIGTERM)
                try:
                    server["process"].wait(timeout=45)
                except subprocess.TimeoutExpired:
                    os.killpg(server["process"].pid, signal.SIGKILL)
                    server["process"].wait(timeout=10)
            server["log"].close()
        shutil.rmtree(local)


if __name__ == "__main__":
    main()
