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
                tensors[name] = {
                    "shape": shape,
                    "sample_sha256": hashlib.sha256(sample).hexdigest(),
                    "shard": shard.name,
                }
    if not tensors:
        raise ValueError("Checkpoint contains no safetensor weights")
    return tensors


def _compare_export_weights(
    original: Path, updated: Path, *, enable_mtp_training: bool, mtp_num_layers: int | None
) -> dict:
    if enable_mtp_training is not False or mtp_num_layers is not None:
        raise ValueError("This GLM decoder qualification requires native MTP training to be disabled")
    config = json.loads((original / "config.json").read_text())
    if config["model_type"] != "glm4_moe_lite":
        raise ValueError("This benchmark qualifies GLM-4.7-Flash decoder exports")
    before, after = _weights(original), _weights(updated)
    # resolve_mtp_num_layers builds no auxiliary nextn layers in this recipe.
    mtp_prefixes = tuple(
        f"model.layers.{layer}."
        for layer in range(
            config["num_hidden_layers"], config["num_hidden_layers"] + config["num_nextn_predict_layers"]
        )
    )
    decoder = {name: value for name, value in before.items() if not name.startswith(mtp_prefixes)}
    # GLM Bridge copies these shared decoder weights into its MTP namespace even
    # when no MTP layer is built. SGLang skips that namespace for decoder loading.
    aliases = {
        prefix + suffix: source
        for prefix in mtp_prefixes
        for suffix, source in (
            ("embed_tokens.weight", "model.embed_tokens.weight"),
            ("shared_head.head.weight", "lm_head.weight"),
        )
        if prefix + suffix in after
    }
    if {key: value["shape"] for key, value in decoder.items()} != {
        key: value["shape"] for key, value in after.items() if key not in aliases
    }:
        raise ValueError("Exported decoder tensor names/shapes differ from the original student")
    index = json.loads((updated / "model.safetensors.index.json").read_text())
    if index["weight_map"] != {name: value["shard"] for name, value in after.items()}:
        raise ValueError("Exported HF index does not match actual tensor shard locations")
    for alias, source in aliases.items():
        with (
            safe_open(updated / after[alias]["shard"], framework="pt", device="cpu") as alias_shard,
            safe_open(updated / after[source]["shard"], framework="pt", device="cpu") as source_shard,
        ):
            alias_tensor, source_tensor = alias_shard.get_tensor(alias), source_shard.get_tensor(source)
            if alias_tensor.dtype != source_tensor.dtype or not alias_tensor.equal(source_tensor):
                raise ValueError(f"Shared MTP alias {alias} differs from its decoder source {source}")
            del alias_tensor, source_tensor
    changed = sum(value["sample_sha256"] != after[key]["sample_sha256"] for key, value in decoder.items())
    if not changed:
        raise ValueError("No sampled exported tensor values changed after learning")
    return {
        "tensor_count": len(after),
        "decoder_tensor_count": len(decoder),
        "changed_tensor_samples": changed,
        "excluded_untrained_mtp_tensors": len(before) - len(decoder),
        "omitted_untrained_mtp_tensors": len(before.keys() - after.keys()),
        "verified_shared_mtp_aliases": sorted(aliases),
        "weight_shards": len(set(index["weight_map"].values())),
        "comparison_scope": "Every trained decoder tensor name/shape and index location; at most four values per dimension",
    }


def _check_export(original: Path, updated: Path) -> dict:
    identity = json.loads((updated / "learning_identity.json").read_text())
    if identity["completed_optimizer_updates"] != 20 or identity["rollout_id"] != 19:
        raise ValueError("Benchmark must consume weights saved after update20")
    if not (updated / ".complete").is_file():
        raise ValueError("Native checkpoint export is incomplete")
    comparison = _compare_export_weights(
        original,
        updated,
        enable_mtp_training=identity["enable_mtp_training"],
        mtp_num_layers=identity["mtp_num_layers"],
    )
    return {"identity": identity, **comparison}


def _start_server(path: Path, original: Path, version: int, args, logs: Path):
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
    log = (logs / f"server-{version}.log").open("w")
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


def _run_seed(server: dict, seed: int, args, output: Path, logs: Path) -> int:
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
        str(logs / f"server-{server['version']}.log"),
    ]
    if args.task_index is not None:
        command.extend(["--task-index", str(args.task_index)])
    if args.sandbox_registry is not None:
        command.extend(["--sandbox-registry", args.sandbox_registry])
    native_log = logs / f"native-{server['version']}-{seed}.log"
    with native_log.open("w") as log:
        exit_code = subprocess.run(
            command, env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=args.benchmark_timeout
        ).returncode
    # This pipeline has exited; its files can be archived while sibling seeds run.
    destination = output / "diagnostics"
    destination.mkdir(parents=True, exist_ok=True)
    seed_directory = logs / f"step{server['version']}" / f"seed-{seed}"
    seed_exists = seed_directory.is_dir()
    if seed_exists:
        shutil.copytree(seed_directory, destination / seed_directory.relative_to(logs))
    shutil.copy2(native_log, destination / native_log.name)
    # Preserve local evidence if either archive operation fails.
    if seed_exists:
        shutil.rmtree(seed_directory)
    native_log.unlink()
    return exit_code


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
    parser.add_argument("--sandbox-registry", help="Registry hostname for the native agent sandbox image")
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
    logs = local / "logs"
    logs.mkdir()
    servers = []
    try:
        if args.updated is not None:
            _save(output / "export-validation.json", _check_export(args.student, args.updated))
        subprocess.run(["nvidia-smi", "-L"], check=True)
        path, version = (args.student, 0) if args.updated is None else (args.updated, 20)
        servers.append(_start_server(path, args.student, version, args, logs))
        for server in servers:
            _save(output / f"engine-{server['version']}.json", _wait_server(server, args.startup_timeout))
        membership = json.loads(args.membership.read_text())
        seeds = membership["seeds"] if args.seeds is None else args.seeds
        if not seeds or len(set(seeds)) != len(seeds) or any(seed not in membership["seeds"] for seed in seeds):
            raise ValueError("Benchmark seeds differ from the frozen membership")
        with ThreadPoolExecutor(max_workers=args.seed_concurrency) as pool:
            futures = [
                pool.submit(_run_seed, server, seed, args, output, logs) for server in servers for seed in seeds
            ]
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
        try:
            # Completed seeds are already archived. The server is now closed.
            shutil.copytree(logs, output / "diagnostics", dirs_exist_ok=True)
        finally:
            shutil.rmtree(local)


if __name__ == "__main__":
    main()
