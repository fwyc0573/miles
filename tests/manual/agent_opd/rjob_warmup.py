"""Run the GLM agentic OPD warmup on two locally mounted RJob replicas.

Submit this entrypoint through the personal StepMind Python RJobBackend. The
platform owns replica rank and GPU allocation; this adapter joins external Ray
and invokes the existing Miles launcher. It never installs worker dependencies.
"""

import argparse
import hashlib
import json
import os
import shlex
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import ray
from scripts.run_glm47_flash_agent_opd import ScriptArgs, _training_env

from miles.utils.external_utils import command_utils as U
from miles.utils.port_range import ray_worker_port_args


def _wait_file(path: Path, deadline: float) -> dict:
    while time.monotonic() < deadline:
        if path.exists():
            return json.loads(path.read_text())
        time.sleep(1)
    raise TimeoutError(f"RJob rendezvous did not publish {path}")


def _write_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(".pending")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def _worker_environment(local: Path) -> None:
    local.mkdir(parents=True, exist_ok=False)
    for key, name in {
        "TMPDIR": "tmp",
        "TORCH_EXTENSIONS_DIR": "torch-extensions",
        "TORCHINDUCTOR_CACHE_DIR": "inductor",
        "TRITON_CACHE_DIR": "triton",
        "FLASHINFER_WORKSPACE_BASE": "flashinfer",
        "XDG_CACHE_HOME": "cache",
        "CUDA_CACHE_PATH": "cuda",
    }.items():
        path = local / name
        path.mkdir()
        os.environ[key] = str(path)
    os.environ["RAY_TMPDIR"] = str(local / "ray")
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["MILES_NODE_EXTERNAL_IP"] = socket.gethostbyname(socket.gethostname())
    # This workload reads mounted weights; all HTTP traffic stays within its Ray cluster.
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        os.environ.pop(key, None)
    os.environ["NO_PROXY"] = os.environ["no_proxy"] = "*"


def _start_ray(rank: int, directory: Path, local: Path, args) -> dict:
    address_file = directory / "head.json"
    ip = os.environ["MILES_NODE_EXTERNAL_IP"]
    command = [
        sys.executable,
        "-m",
        "ray.scripts.scripts",
        "start",
        "--node-ip-address",
        ip,
        "--num-gpus",
        str(args.gpus_per_node),
        "--disable-usage-stats",
        *shlex.split(ray_worker_port_args()),
    ]
    if rank == 0:
        head = {
            "ip": ip,
            "port": int(os.environ["PORT_AUTO0"]),
            "dashboard_port": int(os.environ["PORT_AUTO1"]),
            "run_id": U.create_run_id(),
        }
        command += [
            "--head",
            "--port",
            str(head["port"]),
            "--dashboard-host",
            "0.0.0.0",
            "--dashboard-port",
            str(head["dashboard_port"]),
            "--temp-dir",
            str(local / "ray"),
        ]
        subprocess.run(command, check=True, timeout=args.startup_timeout)
        _write_json(address_file, head)
    else:
        head = _wait_file(address_file, time.monotonic() + args.startup_timeout)
        command += ["--address", f"{head['ip']}:{head['port']}"]
        subprocess.run(command, check=True, timeout=args.startup_timeout)
    return head


def _check_cluster(head: dict, directory: Path, args) -> None:
    ray.init(address=f"{head['ip']}:{head['port']}", log_to_driver=False)
    deadline = time.monotonic() + args.startup_timeout
    while time.monotonic() < deadline:
        nodes = [node for node in ray.nodes() if node["Alive"]]
        if (
            len(nodes) == args.nodes
            and sum(node["Resources"].get("GPU", 0) for node in nodes) == args.nodes * args.gpus_per_node
        ):
            if len({node["NodeManagerAddress"] for node in nodes}) != args.nodes:
                raise ValueError("The warmup requires distinct physical GPU nodes")
            _write_json(
                directory / "cluster.json",
                {
                    "nodes": [
                        {
                            "ip": node["NodeManagerAddress"],
                            "gpus": node["Resources"].get("GPU", 0),
                            "node_id": node["NodeID"],
                        }
                        for node in nodes
                    ]
                },
            )
            print("AGENT_OPD_RAY_CLUSTER_READY", json.dumps(nodes, default=str)[:2000], flush=True)
            ray.shutdown()
            return
        time.sleep(2)
    raise TimeoutError("Ray did not register the requested two-node GPU allocation")


def _check_tokenizers(student: Path, teacher: Path) -> None:
    student_json = json.loads((student / "tokenizer.json").read_text())
    teacher_json = json.loads((teacher / "tokenizer.json").read_text())
    for field in ("model", "added_tokens", "normalizer", "pre_tokenizer", "post_processor", "decoder"):
        if student_json.get(field) != teacher_json.get(field):
            raise ValueError(f"Teacher/student tokenizer field differs: {field}")
    for name in ("tokenizer_config.json", "chat_template.jinja"):
        if (student / name).read_bytes() != (teacher / name).read_bytes():
            raise ValueError(f"Teacher/student tokenizer asset differs: {name}")
    print(
        "AGENT_OPD_TOKENIZERS_MATCH", hashlib.sha256((student / "tokenizer.json").read_bytes()).hexdigest(), flush=True
    )


def _run_training(head: dict, directory: Path, args) -> None:
    _check_cluster(head, directory, args)
    recipe = ScriptArgs()
    subprocess.run(
        [
            sys.executable,
            str(U.repo_base_dir / "tests/manual/agent_opd/weight_sync_probe.py"),
            "--address",
            f"{head['ip']}:{head['port']}",
            "--report",
            str(directory / "weight-sync.json"),
            "--trainer-gpus",
            str(recipe.num_gpus_per_node),
            "--inference-gpus",
            str(recipe.student_engine_gpus),
            "--sender-channels",
            _training_env(recipe)["NCCL_MIN_NCHANNELS"],
        ],
        check=True,
        timeout=args.startup_timeout,
    )
    _check_tokenizers(args.student, args.teacher)
    cloud = args.output_root / os.environ["KUBEBRAIN_RJOB_NAME"]
    cloud.mkdir(parents=True, exist_ok=False)
    dataset = cloud / "glm5.2-warmup.jsonl"
    subprocess.run(
        [
            sys.executable,
            str(U.repo_base_dir / "tests/manual/agent_opd/prepare_glm5_2.py"),
            "--manifest",
            str(args.manifest),
            "--tokenizer",
            str(args.student),
            "--output",
            str(dataset),
            "--report",
            str(directory / "dataset.json"),
            "--turns-per-category",
            str(args.turns_per_category),
            "--max-prompt-tokens",
            str(recipe.max_seq_len - args.response_tokens),
        ],
        check=True,
    )
    training_extra_args = args.training_extra_args
    if args.save_final_hf:
        run_dir = cloud / head["run_id"]
        training_extra_args += " " + shlex.join([
            "--save", str(run_dir / "checkpoint"),
            "--save-interval", str(args.num_rollout),
            "--save-hf", str(run_dir / "hf" / "step_{rollout_id}"),
            "--no-save-optim", "--no-save-rng",
            "--custom-megatron-post-save-hook-path",
            "tests.manual.agent_opd.checkpoint_identity.record_export",
        ])
    os.environ["MILES_SCRIPT_EXTERNAL_RAY"] = "1"
    os.environ["MASTER_ADDR"] = head["ip"]
    os.environ["RAY_ADDRESS"] = f"http://{head['ip']}:{head['dashboard_port']}"
    subprocess.run(
        [
            sys.executable,
            str(U.repo_base_dir / "scripts/run_glm47_flash_agent_opd.py"),
            "--student-checkpoint",
            str(args.student),
            "--teacher-checkpoint",
            str(args.teacher),
            "--prompt-data",
            str(dataset),
            "--output-dir",
            str(cloud),
            "--run-id",
            head["run_id"],
            "--num-rollout",
            str(args.num_rollout),
            "--rollout-max-response-len",
            str(args.response_tokens),
            "--extra-args",
            training_extra_args,
            "--extra-env-vars",
            json.dumps({"no_proxy": "*", "NO_PROXY": "*", "LD_LIBRARY_PATH": os.environ["LD_LIBRARY_PATH"]}),
        ],
        check=True,
        timeout=args.training_timeout,
    )
    inspection = subprocess.run(
        [
            sys.executable,
            str(U.repo_base_dir / "tests/manual/agent_opd/inspect_warmup.py"),
            "--run-dir",
            str(cloud / head["run_id"]),
            "--report",
            str(directory / "validation.md"),
            "--expected-rollouts",
            str(args.num_rollout),
        ],
        timeout=args.startup_timeout,
    )
    _write_json(
        directory / "training.json",
        {
            "status": "succeeded",
            "run_dir": str(cloud / head["run_id"]),
            "dataset": str(dataset),
            "final_hf": str(cloud / head["run_id"] / "hf" / f"step_{args.num_rollout - 1}")
            if args.save_final_hf else None,
            "inspection_exit_code": inspection.returncode,
        },
    )
    print("AGENT_OPD_TRAINING_FINISHED", str(cloud / head["run_id"]), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--student", type=Path, required=True)
    parser.add_argument("--teacher", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--shared-dir", type=Path, required=True)
    parser.add_argument("--local-root", type=Path, default=Path("/var/tmp"))
    parser.add_argument("--nodes", type=int, default=2)
    parser.add_argument("--gpus-per-node", type=int, default=8)
    parser.add_argument("--gpu-type", choices=("H200", "H800"), default="H200")
    parser.add_argument("--num-rollout", type=int, default=2)
    parser.add_argument("--turns-per-category", type=int, default=1)
    parser.add_argument("--response-tokens", type=int, default=1024)
    parser.add_argument("--training-extra-args", default="")
    parser.add_argument("--save-final-hf", action="store_true")
    parser.add_argument("--startup-timeout", type=int, default=600)
    parser.add_argument("--training-timeout", type=int, default=3600)
    args = parser.parse_args()
    args.output_root.relative_to("/mnt/codesign-exp/ycfeng")
    rank = int(os.environ["KUBEBRAIN_REPLICA"])
    if int(os.environ["KUBEBRAIN_REPLICA_TOTAL"]) != args.nodes or args.nodes != 2:
        raise ValueError("The 16-GPU warmup requires two platform replicas")
    if args.gpus_per_node != ScriptArgs().num_gpus_per_node:
        raise ValueError("The platform GPU allocation differs from the GLM warmup recipe")
    job = os.environ["KUBEBRAIN_RJOB_NAME"]
    directory = args.shared_dir / job
    directory.mkdir(parents=True, exist_ok=True)
    local = args.local_root / f"ao-{job.removeprefix('exp-')}"
    _worker_environment(local)
    result = {"status": "failed"}
    try:
        subprocess.run(
            [
                sys.executable,
                str(U.repo_base_dir / "tests/manual/agent_opd/runtime_probe.py"),
                "--require-gpus",
                str(args.gpus_per_node),
                "--report",
                str(directory / f"runtime-{rank}.json"),
            ],
            check=True,
        )
        runtime = json.loads((directory / f"runtime-{rank}.json").read_text())
        if any(args.gpu_type not in name for name in runtime["gpu_devices"]):
            raise ValueError(f"The allocated GPUs do not match the requested {args.gpu_type}")
        subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], check=True
        )
        head = _start_ray(rank, directory, local, args)
        if rank == 0:
            _run_training(head, directory, args)
            result = {"status": "succeeded"}
            _write_json(directory / "finished.json", result)
        else:
            result = _wait_file(
                directory / "finished.json", time.monotonic() + args.training_timeout + args.startup_timeout
            )
            if result["status"] != "succeeded":
                raise RuntimeError("The head replica failed the warmup")
    finally:
        if rank == 0 and result["status"] != "succeeded":
            _write_json(directory / "finished.json", result)
        subprocess.run([sys.executable, "-m", "ray.scripts.scripts", "stop", "--force"], timeout=45)
        shutil.rmtree(local)


if __name__ == "__main__":
    main()
