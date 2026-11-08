"""Submit a SWE pair with serialized GPU admission, then keep it alive.

Use the local StepMind Python environment and handbook authentication. Run from
the configured local mount root with both repositories on PYTHONPATH:

    python -m tests.manual.agent_opd.submit_swe_opd --config "$CONFIG" \
        --pair A --protocol full --receipt "$NEW_RECEIPT"

Exit 2 means admission was denied without creating a job. The advisory lock
covers the fresh API read and submission, not the lifetime of the GPU workload.
"""

import argparse
import fcntl
import json
import os
import socket
from pathlib import Path

from tests.manual.agent_opd.rjob_budget import policy_admission_snapshot
from tests.manual.agent_opd.submit_qwen35 import _task_specs, _worker_command


def _validate_paths(config: dict, config_path: Path) -> None:
    mount = Path(config["local_mount"])
    if not mount.is_absolute() or mount.resolve().is_relative_to("/mnt"):
        raise ValueError("local_mount must be an absolute local workspace path")
    for path in (config_path, Path(config["repo"]), Path(config["shared_dir"]), Path(config["admission_lock"]),
                 Path(config["gpu_policy"])):
        if (not path.is_absolute() or path.resolve().is_relative_to("/mnt")
                or not path.resolve().is_relative_to(mount.resolve())):
            raise ValueError("Config, repo, shared_dir, admission_lock and gpu_policy must resolve under local_mount")
    temporary = Path(config["worker_local_root"])
    if not temporary.is_absolute() or temporary.resolve().is_relative_to("/mnt"):
        raise ValueError("worker_local_root must be local temporary storage, not a cloud path")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--pair", choices=("A", "B"), required=True)
    parser.add_argument("--protocol", choices=("full", "r256"), required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    path = args.config.resolve(strict=True)
    config = json.loads(path.read_text())
    _validate_paths(config, path)
    policy = json.loads(Path(config["gpu_policy"]).read_text())
    tasks = _task_specs(config, args.pair)
    requested = sum(task["gpu"] * task["replica"] for task in tasks.values())
    command = _worker_command(config, path, args.pair, worker_module="tests.manual.agent_opd.run_swe_opd",
                              extra_args=("--protocol", args.protocol))
    if args.dry_run:
        print(json.dumps({"submitted": False, "pair": args.pair, "protocol": args.protocol,
                          "requested_gpus": requested, "tasks": tasks, "command": command,
                          "gpu_policy": policy}, indent=2))
        return 0
    if Path.cwd() != Path(config["local_mount"]):
        raise ValueError(f"Submit from the local mount source: {config['local_mount']}")
    if os.environ.get("STEPMIND_BACKEND") != "rjob":
        raise ValueError("Initialize the handbook's STEPMIND_BACKEND=rjob environment")
    if not os.environ.get("BRAINPP_ACCESS_KEY") or not os.environ.get("BRAINPP_SECRET_KEY"):
        raise ValueError("Personal authentication must be initialized before submission")

    # These dependencies are installed only in the local StepMind environment.
    from steptron.exp.base_exp import ResourceConfig
    from steptron.utils.stepmind import get_rjob_client
    from steptron.utils.stepmind_control import RJobBackend

    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    lock_path = Path(config["admission_lock"])
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with args.receipt.open("x") as receipt, lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        snapshot = policy_admission_snapshot(
            get_rjob_client(), creator=config["creator"], gpu_tag=config["gpu_tag"],
            requested_gpus=requested, policy=policy, timeout=config["api_timeout_seconds"],
        )
        snapshot.update(config=str(path), pair=args.pair, protocol=args.protocol, submitted=False)
        if not snapshot["admitted"]:
            json.dump(snapshot, receipt, indent=2)
            receipt.write("\n")
            print("SWE_ADMISSION_WAIT", json.dumps(snapshot), flush=True)
            return 2
        os.environ["EXP_ID"] = f"qwen35-swe-{args.pair.lower()}-{args.protocol}-{config['phase']}"
        mount = f"{socket.gethostbyname(socket.gethostname())}:{Path.cwd()}:{config['local_mount']}"
        resource = ResourceConfig(
            image=config["image"], positive_tags=[config["gpu_tag"]], extra_requirements=[],
            mounts=config["mounts"], envs={"PYTHONPATH": config["local_mount"]},
            annotations={"kubebrain.brainpp.cn/filestore-volume": mount,
                         policy["task_annotation"]: policy["task_id"]}, pull_code=False,
            command="{COMMAND}", task_specs=tasks, preemptible=snapshot["preemptible"],
        )
        resource.exp_name = os.environ["EXP_ID"]
        resource.charged_group = config["charged_group"]
        workers = RJobBackend().submit(resource, command=command, code_mount_point=config["local_mount"])
        snapshot.update(submitted=True, job=workers.rjob.meta.name, source_mount=mount)
        json.dump(snapshot, receipt, indent=2)
        receipt.write("\n")
        receipt.flush()
        fcntl.flock(lock, fcntl.LOCK_UN)
    print("SWE_PAIR_SUBMITTED", workers.rjob.meta.name, flush=True)
    workers.wait()
    status = workers.poll()
    print("SWE_PAIR_FINISHED", workers.rjob.meta.name, status, flush=True)
    return int(status != "succeeded")


if __name__ == "__main__":
    raise SystemExit(main())
