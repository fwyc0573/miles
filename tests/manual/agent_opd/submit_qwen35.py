"""Submit one independently allocated student/teacher pair through Python RJobBackend.

Run from the configured local mount root after the handbook's personal-auth setup.
Keep this process alive until spawn_tasks returns. The JSON input owns the image,
source mounts, GPU shapes and native worker arguments; --dry-run only prints them.
"""

import argparse
import json
import os
import shlex
from pathlib import Path


def _task_specs(config: dict, pair: str) -> dict:
    tasks = {}
    for role in ("student", "teacher"):
        resource = config["pairs"][pair][role]
        envs = {"QWEN35_ROLE": role}
        if resource["nodes"] > 1:
            envs["DISTRIBUTED_JOB"] = "true"
        tasks[role] = {
            "cpu": resource["cpu_per_node"],
            "gpu": resource["gpus_per_node"],
            "mem_gb": resource["memory_gb_per_node"],
            "replica": resource["nodes"],
            "host_network": resource["host_network"],
            "gang_start": resource["gang_start"],
            "envs": envs,
            "custom_resources": config["rdma_resources"] if resource["nodes"] > 1 else [],
            "is_critical": role == "student",
        }
    return tasks


def _worker_command(config: dict, config_path: Path, pair: str) -> str:
    argv = [
        config["worker_python"], "-u", "-B",
        str(Path(config["repo"]) / "tests/manual/agent_opd/qwen35_pair_worker.py"),
        "--config", str(config_path), "--pair", pair,
    ]
    script = (
        f"export PYTHONPATH={shlex.quote(config['repo'])}\n"
        f"export LD_LIBRARY_PATH={shlex.quote(config['cuda_compat_dir'])}"
        '"${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"\n'
        f"exec {shlex.join(argv)} --role \"$QWEN35_ROLE\""
    )
    return "bash -lc " + shlex.quote(script)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--pair", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config_path = args.config.resolve(strict=True)
    config = json.loads(config_path.read_text())
    tasks = _task_specs(config, args.pair)
    command = _worker_command(config, config_path, args.pair)
    requested_gpus = sum(task["gpu"] * task["replica"] for task in tasks.values())
    if requested_gpus > config["capacity_gpus"]:
        raise ValueError("The pair exceeds the configured GPU allocation ceiling")
    if args.dry_run:
        print(json.dumps({
            "pair": args.pair, "image": config["image"], "tasks": tasks,
            "requested_gpus": requested_gpus, "charged_group": config["charged_group"],
            "positive_tags": [config["gpu_tag"]], "mounts": config["mounts"],
            "preemptible": config["preemptible"], "local_mount": config["local_mount"],
            "worker_command": command, "num_rollout": config["num_rollout"],
            "submitted": False,
        }, indent=2))
        return

    if Path.cwd() != Path(config["local_mount"]):
        raise ValueError(f"Run from the local NFS source directory: {config['local_mount']}")
    if os.environ.get("STEPMIND_BACKEND") != "rjob":
        raise ValueError("Initialize STEPMIND_BACKEND=rjob and personal auth using the handbook")
    if not os.environ.get("BRAINPP_ACCESS_KEY") or not os.environ.get("BRAINPP_SECRET_KEY"):
        raise ValueError("Personal credentials must be configured before constructing the backend")

    from steptron.exp.base_exp import ResourceConfig
    from steptron.utils.stepmind import spawn_tasks

    phase = "baseline" if config["num_rollout"] == 0 else "training"
    os.environ["EXP_ID"] = f"qwen35-{args.pair.lower()}-{phase}"
    resource = ResourceConfig(
        image=config["image"], positive_tags=[config["gpu_tag"]],
        extra_requirements=[], mounts=config["mounts"], envs={},
        command="{COMMAND}", task_specs=tasks, preemptible=config["preemptible"],
    )
    resource.exp_name = os.environ["EXP_ID"]
    workers = spawn_tasks(
        resource, command=command, charged_group=config["charged_group"],
        use_image=True, code_mount_point=config["local_mount"],
    )
    print("QWEN35_PAIR_FINISHED", args.pair, workers.rjob.meta.name, workers.poll(), flush=True)


if __name__ == "__main__":
    main()
