"""Submit one two-GPU SWE point locally and keep the native RJob launcher alive.

Run from integration_config.json's local_mount using the personal StepMind Python
environment with this Miles checkout first on PYTHONPATH. Supply an already built
evaluation configuration in the same local workspace:

    python -B -m tests.manual.agent_opd.submit_swe_evaluation \
        --config "$INTEGRATION" --configuration "$EVALUATION" \
        --point original-4b --receipt "$NEW_RECEIPT" --original-source "$ORIGINAL_4B"

Omit --original-source for a trainer-enqueued HF point. Qualification uses a
separate /qualification-evaluations store, qualification.<name> point and repeated explicit
--qualification-attempt TASK#attempt-N options, which go unchanged to the worker.
For an owned smoke HF, explicitly pass --qualification-checkpoint instead of
--original-source; the worker validates/enqueues its actual SMOKE_PACKAGED publication.
Optional integration evaluation_resources replaces the teacher role's CPU/memory,
host_network and gang_start sizing; this adapter always requests one two-GPU node.
Private router-token aliases and native ACS access keys are inherited only through the worker environment.
Exit 2 denotes denied admission without submission. Native wait failures remain
failures; no scheduler, recovery, retries, grading or source-weight writes occur.
"""

import argparse
import fcntl
import json
import os
import shlex
import socket
import time
from pathlib import Path

from tests.manual.agent_opd.rjob_budget import policy_admission_snapshot, validate_allocation
from tests.manual.agent_opd.submit_swe_opd import _validate_paths
from tests.manual.agent_opd.swe_evaluation import SEEDS, _label, read_json, store_from_config

# StepMind adds vendored packages to sys.path; reserve the real Miles package first.
import miles.utils  # noqa: F401


def _validate_inputs(config, evaluation, config_path, configuration, receipt, original_source):
    _validate_paths(config, config_path)
    mount = Path(config["local_mount"]).resolve()
    for path in (configuration, receipt):
        if not path.is_absolute() or path.resolve().is_relative_to("/mnt") or not path.resolve().is_relative_to(mount):
            raise ValueError("Evaluation configuration and receipt must resolve under local_mount, not a cloud path")
    expected = {
        "task_id": read_json(config["gpu_policy"])["task_id"],
        "creator": config["creator"],
        "gpu_tag": config["gpu_tag"],
    }
    if evaluation["allocation_identity"] != expected:
        raise ValueError("Evaluation and integration configurations must identify the same task and allocation")
    for field, value in {
        "python": config["worker_python"],
        "image": config["image"],
        "repo": config["repo"],
        "local_root": config["worker_local_root"],
    }.items():
        if evaluation["server"][field] != value:
            raise ValueError("Evaluation server deployment must match integration_config")
    if evaluation["server"]["startup_timeout"] <= 0:
        raise ValueError("Receipt rendezvous requires the existing positive startup timeout")
    for field in ("root", "owned_root"):
        path = Path(evaluation[field])
        if not path.is_absolute() or ".." in path.parts or not path.is_relative_to("/mnt/codesign-exp/ycfeng"):
            raise ValueError("Evaluation artifacts must stay in the personal cloud namespace")
    if original_source is not None and str(original_source) != evaluation["original_source"]:
        raise ValueError("Explicit baseline source must be the configured protected original model")


def _validate_qualification_checkpoint(config, evaluation, point, checkpoint, attempts):
    store = store_from_config(evaluation)
    if store.root.name != "qualification-evaluations" or not point.startswith("qualification."):
        raise ValueError("Owned smoke HF requires /qualification-evaluations and a qualification.<name> point")
    _label(point.removeprefix("qualification."))
    original = Path(evaluation["original_source"]).resolve()
    if original not in store.protected_sources or any(
        Path(config["pairs"][pair]["student"]["path"]).resolve() != original for pair in ("A", "B")
    ):
        raise ValueError("Qualification must identify the exact protected original student from integration_config")
    if not checkpoint.is_absolute() or ".." in checkpoint.parts:
        raise ValueError("Explicit qualification checkpoint must be an absolute owned HF path")
    checkpoint = store._owned_directory(checkpoint)
    tasks = evaluation["task_ids"]
    slots = {f"{task}#attempt-{attempt}" for task in tasks for attempt in range(len(SEEDS))}
    if (
        len(tasks) != 100
        or len(set(tasks)) != 100
        or not attempts
        or len(set(attempts)) != len(attempts)
        or not set(attempts) < slots
    ):
        raise ValueError(
            "Owned HF qualification requires distinct explicit slots from, but not all of, the frozen100x4"
        )
    return checkpoint


def _task_specs(config):
    resource = config["evaluation_resources"] if "evaluation_resources" in config else config["pairs"]["A"]["teacher"]
    for field in ("cpu_per_node", "memory_gb_per_node"):
        if type(resource[field]) is not int or resource[field] <= 0:
            raise ValueError("Evaluation CPU and memory requests must be positive integers")
    if resource.get("nodes", 1) != 1 or resource.get("gpus_per_node", 2) != 2:
        raise ValueError("Evaluation requires exactly one two-GPU node")
    return {
        "evaluation": {
            "cpu": resource["cpu_per_node"],
            "gpu": 2,
            "mem_gb": resource["memory_gb_per_node"],
            "replica": 1,
            "host_network": resource["host_network"],
            "gang_start": resource["gang_start"],
            "envs": {},
            "custom_resources": [],
            "is_critical": True,
        }
    }


def _worker_environment(config):
    envs = dict(config.get("envs", {}))
    aliases = ("SR_USER_TOKEN", "SESSION_ROUTER_USER_TOKEN")
    native_keys = ("AK_BASEMIND", "SK_BASEMIND")
    if any(name in envs for name in (*aliases, *native_keys)):
        raise ValueError("Private native credentials must be inherited, not stored in configuration")
    tokens = [os.environ.get(name) for name in aliases]
    if not any(tokens) or (all(tokens) and tokens[0] != tokens[1]):
        raise ValueError("Inherit one private router token or matching token aliases")
    envs.update({name: tokens[0] or tokens[1] for name in aliases})
    for name in native_keys:
        value = os.environ.get(name)
        if not value:
            raise ValueError(f"Native ACS evaluation requires inherited {name}")
        envs[name] = value
    envs.update(PYTHONPATH=config["repo"], PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1")
    return envs


def _worker_argv(config, configuration, point, receipt, qualification_attempts):
    return [
        config["worker_python"],
        "-u",
        "-B",
        "-m",
        "tests.manual.agent_opd.run_swe_evaluation",
        "--configuration",
        str(configuration),
        "--point",
        point,
        "--allocation",
        str(receipt),
        *[arg for uid in qualification_attempts or () for arg in ("--qualification-attempt", uid)],
    ]


def _worker_command(
    config,
    config_path,
    configuration,
    point,
    receipt,
    original_source,
    qualification_attempts,
    qualification_checkpoint,
):
    argv = [
        config["worker_python"],
        "-u",
        "-B",
        "-m",
        "tests.manual.agent_opd.submit_swe_evaluation",
        "--worker",
        "--config",
        str(config_path),
        "--configuration",
        str(configuration),
        "--point",
        point,
        "--receipt",
        str(receipt),
    ]
    if original_source is not None:
        argv.extend(("--original-source", str(original_source)))
    if qualification_checkpoint is not None:
        argv.extend(("--qualification-checkpoint", str(qualification_checkpoint)))
    argv.extend(arg for uid in qualification_attempts or () for arg in ("--qualification-attempt", uid))
    script = (
        f"cd {shlex.quote(config['repo'])}\n"
        f"export LD_LIBRARY_PATH={shlex.quote(config['cuda_compat_dir'])}"
        '"${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"\n'
        f"exec {shlex.join(argv)}"
    )
    return "bash -lc " + shlex.quote(script)


def _prepare_worker(config, evaluation, args):
    # Reuse the existing bounded rendezvous only in the pinned GPU interpreter.
    from tests.manual.agent_opd.rjob_warmup import _wait_file

    allocation = _wait_file(args.receipt, time.monotonic() + evaluation["server"]["startup_timeout"])
    if (
        allocation["job_id"] != os.environ["KUBEBRAIN_RJOB_NAME"]
        or allocation.get("eval_gpus") != 2
        or allocation["admission"]["requested_gpus"] != 2
        or allocation["point"] != args.point
    ):
        raise ValueError("Receipt must belong to this actual two-GPU worker and point")
    validate_allocation(allocation, requested_gpus=2, expected=evaluation["allocation_identity"])
    if args.qualification_checkpoint is not None:
        if (
            allocation.get("qualification_checkpoint") != str(args.qualification_checkpoint)
            or allocation.get("run_kind") != "qualification"
        ):
            raise ValueError("Receipt must identify this exact owned qualification checkpoint")
        store_from_config(evaluation).enqueue_qualification_checkpoint(
            point_id=args.point,
            checkpoint_dir=args.qualification_checkpoint,
            source=evaluation["original_source"],
            task_ids=evaluation["task_ids"],
            configuration=evaluation["evaluation_contract"],
        )
    if args.original_source is not None:
        store_from_config(evaluation).enqueue_baseline(
            point_id=args.point,
            source=args.original_source,
            task_ids=evaluation["task_ids"],
            configuration=evaluation["evaluation_contract"],
        )
    argv = _worker_argv(config, args.configuration, args.point, args.receipt, args.qualification_attempts)
    os.execv(argv[0], argv)


def _publish_receipt(stream, pending, receipt, allocation):
    json.dump(allocation, stream, indent=2, allow_nan=False)
    stream.write("\n")
    stream.flush()
    os.fsync(stream.fileno())
    # A hard link publishes complete bytes atomically and refuses any overwrite.
    os.link(pending, receipt)
    pending.unlink()
    descriptor = os.open(receipt.parent, os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _submit(config, policy, config_path, args, tasks, command):
    if Path.cwd().resolve() != Path(config["local_mount"]).resolve():
        raise ValueError(f"Submit from the local mount source: {config['local_mount']}")
    if "KUBEBRAIN_RJOB_NAME" in os.environ:
        raise ValueError("Submit only from the local workspace, never from an RJob worker")
    if os.environ.get("STEPMIND_BACKEND") != "rjob":
        raise ValueError("Initialize the handbook's STEPMIND_BACKEND=rjob environment")
    if not os.environ.get("BRAINPP_ACCESS_KEY") or not os.environ.get("BRAINPP_SECRET_KEY"):
        raise ValueError("Personal authentication must be initialized before submission")
    envs = _worker_environment(config)

    # Optional platform dependencies must not load during CPU planning or worker preparation.
    from steptron.exp.base_exp import ResourceConfig
    from steptron.utils.stepmind import get_rjob_client
    from steptron.utils.stepmind_control import RJobBackend

    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    pending = args.receipt.with_name(args.receipt.name + ".pending")
    lock_path = Path(config["admission_lock"])
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with pending.open("x") as stream, lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if args.receipt.exists():
            raise FileExistsError(f"Receipt already exists: {args.receipt}")
        snapshot = policy_admission_snapshot(
            get_rjob_client(),
            creator=config["creator"],
            gpu_tag=config["gpu_tag"],
            requested_gpus=2,
            policy=policy,
            timeout=config["api_timeout_seconds"],
        )
        snapshot.update(submitted=False)
        allocation = {
            "job_id": None,
            "eval_gpus": 2,
            "point": args.point,
            "config": str(config_path),
            "configuration": str(args.configuration),
            "admission": snapshot,
        }
        if args.qualification_checkpoint is not None:
            allocation.update(run_kind="qualification", qualification_checkpoint=str(args.qualification_checkpoint))
        if not snapshot["admitted"]:
            _publish_receipt(stream, pending, args.receipt, allocation)
            print("SWE_EVALUATION_ADMISSION_WAIT", args.point, flush=True)
            return 2
        os.environ["EXP_ID"] = f"qwen35-swe-eval-{args.point}-{config['phase']}"
        mount = f"{socket.gethostbyname(socket.gethostname())}:{Path.cwd()}:{config['local_mount']}"
        resource = ResourceConfig(
            image=config["image"],
            positive_tags=[config["gpu_tag"]],
            extra_requirements=[],
            mounts=config["mounts"],
            envs=envs,
            annotations={"kubebrain.brainpp.cn/filestore-volume": mount, policy["task_annotation"]: policy["task_id"]},
            pull_code=False,
            command="{COMMAND}",
            task_specs=tasks,
            preemptible=snapshot["preemptible"],
        )
        resource.exp_name = os.environ["EXP_ID"]
        resource.charged_group = config["charged_group"]
        workers = RJobBackend().submit(resource, command=command, code_mount_point=config["local_mount"])
        snapshot.update(submitted=True, job=workers.rjob.meta.name, source_mount=mount)
        allocation["job_id"] = workers.rjob.meta.name
        _publish_receipt(stream, pending, args.receipt, allocation)
        fcntl.flock(lock, fcntl.LOCK_UN)
    print("SWE_EVALUATION_SUBMITTED", workers.rjob.meta.name, args.point, flush=True)
    workers.wait()
    status = workers.poll()
    print("SWE_EVALUATION_FINISHED", workers.rjob.meta.name, status, flush=True)
    return int(status != "succeeded")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--configuration", type=Path, required=True)
    parser.add_argument("--point", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--original-source", type=Path, help="Explicit protected source to enqueue on the worker")
    source.add_argument(
        "--qualification-checkpoint",
        type=Path,
        help="Explicit owned SMOKE_PACKAGED HF to qualify, never a formal point",
    )
    parser.add_argument("--qualification-attempt", action="append", dest="qualification_attempts")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    config_path = args.config.resolve(strict=True)
    args.configuration = args.configuration.resolve(strict=True)
    config, evaluation = read_json(config_path), read_json(args.configuration)
    _label(args.point)
    _validate_inputs(config, evaluation, config_path, args.configuration, args.receipt, args.original_source)
    if args.qualification_checkpoint is not None:
        args.qualification_checkpoint = _validate_qualification_checkpoint(
            config, evaluation, args.point, args.qualification_checkpoint, args.qualification_attempts
        )
    if args.worker:
        _prepare_worker(config, evaluation, args)
        return 0
    if args.receipt.exists() or args.receipt.with_name(args.receipt.name + ".pending").exists():
        raise FileExistsError(f"Use a new receipt path: {args.receipt}")
    tasks = _task_specs(config)
    command = _worker_command(
        config,
        config_path,
        args.configuration,
        args.point,
        args.receipt,
        args.original_source,
        args.qualification_attempts,
        args.qualification_checkpoint,
    )
    policy = read_json(config["gpu_policy"])
    if args.dry_run:
        print(
            json.dumps(
                {
                    "submitted": False,
                    "point": args.point,
                    "requested_gpus": 2,
                    "tasks": tasks,
                    "command": command,
                    "image": config["image"],
                    "mounts": config["mounts"],
                    "gpu_policy": policy,
                },
                indent=2,
            )
        )
        return 0
    return _submit(config, policy, config_path, args, tasks, command)


if __name__ == "__main__":
    raise SystemExit(main())
