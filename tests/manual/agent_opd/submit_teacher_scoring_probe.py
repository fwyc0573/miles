"""Submit one dedicated H800 teacher probe and retain its native allocation.

Use the authenticated local StepMind Python environment. The admission lock
covers inventory and submission, not the worker lifetime. This entry point
does not allocate student/trainer roles or change the formal configuration.
"""

import argparse
import fcntl
import json
import os
import shlex
import socket
from pathlib import Path

from tests.manual.agent_opd.rjob_budget import policy_admission_snapshot
from tests.manual.agent_opd.submit_swe_opd import _job_succeeded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--pair", choices=("A", "B"), required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    probe_path = args.config.resolve(strict=True)
    probe = json.loads(probe_path.read_text())
    selected_fp32 = probe.get("selected_fp32_snapshots", False)
    if type(selected_fp32) is not bool:
        raise ValueError("selected_fp32_snapshots must be a JSON boolean")
    formal_path = (repo / probe["formal_config"]).resolve(strict=True)
    worker_config = probe_path if selected_fp32 else formal_path
    config = json.loads(formal_path.read_text())
    if config["gpu_tag"] != "H800" or config["charged_group"] != "codesign":
        raise ValueError("The scoring probe requires H800/codesign")
    teacher = config["pairs"][args.pair]["teacher"]
    if teacher["nodes"] != 1 or teacher["gpus_per_node"] != teacher["tp_size"]:
        raise ValueError("The scoring probe requires one complete native teacher node")
    mount = Path(config["local_mount"]).resolve(strict=True)
    envs = {"PYTHONPATH": str(mount), **probe.get("envs", {})}
    samples = (repo / probe["samples"]).resolve(strict=True)
    receipt_path = args.receipt.resolve()
    output = repo / probe["output_parent"] / args.pair / receipt_path.stem
    for path in (repo, formal_path, worker_config, samples, receipt_path, output):
        if not path.is_relative_to(mount):
            raise ValueError("Probe inputs, output and receipt must be under local_mount")
    argv = [config["worker_python"], "-u", "-B", "-m", "tests.manual.agent_opd.probe_teacher_scoring",
             "--config", str(worker_config), "--pair", args.pair, "--samples", str(samples),
            "--output-dir", str(output), "--repeats", str(probe["repeats"]),
            "--request-timeout", str(probe["request_timeout_seconds"])]
    script = (
        f"export PYTHONPATH={shlex.quote(config['repo'])}\n"
        f"export LD_LIBRARY_PATH={shlex.quote(config['cuda_compat_dir'])}"
        '"${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"\n'
        f"exec timeout --signal=TERM --kill-after={probe['child_cleanup_grace_seconds']}s "
        f"{probe['worker_seconds']}s {shlex.join(argv)}"
    )
    command = "bash -lc " + shlex.quote(script)
    tasks = {"probe": {"cpu": teacher["cpu_per_node"], "gpu": teacher["gpus_per_node"],
                       "mem_gb": teacher["memory_gb_per_node"], "replica": 1,
                       "host_network": teacher["host_network"], "gang_start": teacher["gang_start"],
                       "custom_resources": [], "is_critical": True}}
    requested = teacher["gpus_per_node"]
    if args.dry_run:
        print(json.dumps({"submitted": False, "pair": args.pair, "requested_gpus": requested,
                          "gpu_tag": config["gpu_tag"], "charged_group": config["charged_group"],
                           "image": config["image"], "tasks": tasks, "mounts": config["mounts"],
                           "envs": envs,
                           "source_directory": str(mount), "output": str(output),
                          "worker_command": command}, indent=2))
        return 0
    if os.environ.get("STEPMIND_BACKEND") != "rjob":
        raise ValueError("Initialize the handbook's personal STEPMIND_BACKEND=rjob environment")
    if not all(os.environ.get(key) for key in ("BRAINPP_ACCESS_KEY", "BRAINPP_SECRET_KEY")):
        raise ValueError("Personal authentication is required before creating the client")
    from steptron.exp.base_exp import ResourceConfig
    from steptron.utils.stepmind import get_rjob_client
    from steptron.utils.stepmind_control import RJobBackend

    policy = json.loads(Path(config["gpu_policy"]).read_text())
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    os.chdir(mount)
    with receipt_path.open("x") as receipt, Path(config["admission_lock"]).open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        client = get_rjob_client()
        snapshot = policy_admission_snapshot(client, creator=config["creator"], gpu_tag=config["gpu_tag"],
                                             requested_gpus=requested, policy=policy,
                                             timeout=config["api_timeout_seconds"])
        snapshot.update(pair=args.pair, submitted=False, config=str(formal_path),
                        probe_config=str(args.config.resolve()), output=str(output), worker_command=command,
                        envs=dict(envs))
        if not snapshot["admitted"]:
            json.dump(snapshot, receipt, indent=2)
            receipt.write("\n")
            return 2
        source_mount = f"{socket.gethostbyname(socket.gethostname())}:{mount}:{mount}"
        resource = ResourceConfig(
            image=config["image"], positive_tags=[config["gpu_tag"]], extra_requirements=[],
            mounts=list(config["mounts"]), envs=envs,
            annotations={"kubebrain.brainpp.cn/filestore-volume": source_mount,
                         policy["task_annotation"]: policy["task_id"]}, pull_code=False,
            command="{COMMAND}", task_specs=tasks, preemptible=snapshot["preemptible"],
        )
        resource.exp_name = f"teacher-scoring-{args.pair.lower()}-{config['phase']}"
        resource.charged_group = config["charged_group"]
        os.environ["EXP_ID"] = resource.exp_name
        workers = RJobBackend().submit(resource, command=command, code_mount_point=str(mount))
        snapshot.update(submitted=True, job=workers.rjob.meta.name, source_mount=source_mount)
        json.dump(snapshot, receipt, indent=2)
        receipt.write("\n")
        receipt.flush()
        fcntl.flock(lock, fcntl.LOCK_UN)
    print("TEACHER_SCORING_PROBE_SUBMITTED", workers.rjob.meta.name, flush=True)
    try:
        workers.wait()
    finally:
        job = client.api.get_namespaced_custom_object(
            group=client.group, version=client.version, namespace=client.namespace, plural=client.plural,
            name=workers.rjob.meta.name, _request_timeout=config["api_timeout_seconds"])
        terminal = {"job": job["metadata"]["name"], "uid": job["metadata"]["uid"],
                    "creator": job["metadata"]["labels"]["kubebrain.brainpp.cn/creator"],
                    "status": job["status"], "native_execution_succeeded": _job_succeeded(job, tasks)}
        with receipt_path.with_suffix(".terminal.json").open("x") as stream:
            json.dump(terminal, stream, indent=2)
            stream.write("\n")
        print("TEACHER_SCORING_PROBE_FINISHED", json.dumps(terminal), flush=True)
    return int(not terminal["native_execution_succeeded"])


if __name__ == "__main__":
    raise SystemExit(main())
