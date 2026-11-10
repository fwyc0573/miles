"""CUDA-only, one-H200 allocator-order diagnostic; no model, DDP, or training run.

Supply --launch-receipt, --native-source-receipt, --transient-mib, --moment-mib,
and --output-dir. Run under the controller's existing <=600-second worker timeout.
The stdlib-only parent runs two serial, separate subprocesses. Each subprocess
re-execs with the formal trainer environment owner before executing CUDA code.

Both cases use native Megatron's raw FusedAdam factory and init_state_fn. Only
the timing of moment initialization changes. This tests an allocation mechanism,
not whether a full-model first Adam step caused the retained formal OOM. Identical
results are a valid negative result. Failures are diagnostic, not training gates.
"""

import argparse
import hashlib
import importlib.metadata
import inspect
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path, PurePosixPath
from types import SimpleNamespace

_CASES = ("late_moments", "early_moments")
_MIB = 1024**2
_ALLOCATOR_ENV = ("PYTORCH_ALLOC_CONF", "PYTORCH_CUDA_ALLOC_CONF", "PYTORCH_NO_CUDA_MEMORY_CACHING")


def _positive_mib(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("allocation size must be positive MiB")
    return number


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launch-receipt", type=Path, required=True)
    parser.add_argument("--native-source-receipt", type=Path, required=True)
    parser.add_argument("--transient-mib", type=_positive_mib, required=True)
    parser.add_argument("--moment-mib", type=_positive_mib, required=True, help="Bytes of each of the two FP32 Adam moments")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--case", choices=_CASES, help=argparse.SUPPRESS)
    parser.add_argument("--prepared", action="store_true", help=argparse.SUPPRESS)
    return parser


def _read_json(path):
    return json.loads(path.read_text())


def _write_json(path, value, *, exclusive=False):
    destination = path if exclusive else path.with_suffix(path.suffix + ".part")
    with destination.open("x" if exclusive else "w") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")
    if not exclusive:
        os.replace(destination, path)


def _argv_value(argv, name, default):
    flag = "--" + name.replace("_", "-")
    for index, value in enumerate(argv):
        if value.startswith(flag + "="):
            return value.split("=", 1)[1]
        if value == flag:
            return argv[index + 1]
    return default


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _prepare_case(args, receipt):
    # Worker-only imports: the controller parent and --help never import torch/Ray.
    from miles.ray.specs.train import compute_trainer_env_vars
    from miles.utils.args.configs.cluster import ClusterConfig
    from miles.utils.args.configs.debug import DebugConfig
    from miles.utils.args.configs.train import TrainConfig
    from miles.utils.environ import default_fp8_block_scaling_fp32_scales

    argv = receipt["training_argv"]
    temporary = os.environ.get("TMPDIR")
    if temporary is None or not Path(temporary).resolve().is_relative_to(
        Path(receipt["resolved_experiment"]["worker_local_root"]).resolve()
    ):
        raise ValueError("TMPDIR must be explicitly set under the formal worker-local root")
    if "--offload-train" not in argv or "--no-offload-train" in argv:
        raise ValueError("Require the retained formal --offload-train launch")
    values = {"offload_train": True}
    for config, names in (
        (TrainConfig, ("train_backend", "train_env_vars")),
        (ClusterConfig, ("offload_train_target", "offload_train_disk_dir", "offload_train_disk_chunk_mb")),
        (DebugConfig, ("dumper_source_patcher_config_train",)),
    ):
        for name in names:
            values[name] = _argv_value(argv, name, config.model_fields[name].default)
    values["train_env_vars"] = json.loads(values["train_env_vars"])
    if values["train_backend"] != "megatron" or values["offload_train_target"] != "cpu":
        raise ValueError("This diagnostic supports the retained Megatron CPU-backup launch only")
    if values["dumper_source_patcher_config_train"] is not None:
        raise ValueError("This allocator diagnostic does not execute source patchers")
    for key in _ALLOCATOR_ENV:
        if key not in values["train_env_vars"] and os.environ.get(key):
            raise ValueError(f"Inherited {key} is not declared in the retained launch; do not tune allocator flags")
    env = os.environ.copy()
    env.update(compute_trainer_env_vars(
        SimpleNamespace(**values), SimpleNamespace(cell_index=0, worker_in_cell_index=0),
        fp8_scales=default_fp8_block_scaling_fp32_scales(),
    ))
    os.execve(sys.executable, [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:], "--prepared"], env)


def _cgroup_location():
    memberships = {}
    for line in Path("/proc/self/cgroup").read_text().splitlines():
        _, controllers, path = line.split(":", 2)
        if not controllers:
            memberships["cgroup2"] = path
        elif "memory" in controllers.split(","):
            memberships["cgroup"] = path
    for line in Path("/proc/self/mountinfo").read_text().splitlines():
        left, right = line.split(" - ", 1)
        mount, filesystem = left.split(), right.split()
        kind = filesystem[0]
        if kind not in memberships or (kind == "cgroup" and "memory" not in filesystem[2].split(",")):
            continue
        root, point = PurePosixPath(mount[3]), Path(mount[4])
        member = PurePosixPath(memberships[kind])
        # Host-relative and private-cgroup-namespace mount layouts are both supported.
        relative = member.relative_to(root) if member.is_relative_to(root) else member.relative_to("/")
        directory = point / str(relative)
        counter = "memory.current" if kind == "cgroup2" else "memory.usage_in_bytes"
        if (directory / counter).exists():
            return directory, counter, memberships[kind]
    raise RuntimeError("Could not resolve this process's memory cgroup")


def _host_memory():
    status = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        key, _, value = line.partition(":")
        if key in ("VmRSS", "VmLck"):
            status[key] = int(value.split()[0]) * 1024
    directory, counter, membership = _cgroup_location()
    return {
        "rss_bytes": status["VmRSS"], "locked_bytes": status["VmLck"],
        "cgroup": {
            "directory": str(directory), "membership": membership,
            "current_bytes": int((directory / counter).read_text()),
            "stat": {key: int(value) for key, value in (line.split() for line in (directory / "memory.stat").read_text().splitlines())},
        },
    }


def _segments(snapshot):
    result = []
    for segment in snapshot:
        values = {key: segment[key] for key in (
            "device", "address", "total_size", "allocated_size", "active_size", "stream", "segment_type",
        )}
        values["segment_pool_id"] = segment.get("segment_pool_id")
        values["blocks"] = [{key: block[key] for key in ("address", "size", "requested_size", "state")}
                            for block in segment["blocks"]]
        result.append(values)
    return result


def _cuda_memory(torch):
    stats = torch.cuda.memory_stats()
    free, total = torch.cuda.mem_get_info()
    return {name: stats[key] for name, key in (
        ("allocated_bytes", "allocated_bytes.all.current"),
        ("reserved_bytes", "reserved_bytes.all.current"),
        ("inactive_split_bytes", "inactive_split_bytes.all.current"),
    )} | {"device_free_bytes": free, "device_total_bytes": total}


def _capture(torch, report, path, phase, *, segments=False):
    report["phases"][phase] = {"monotonic_seconds": time.monotonic(), "cuda": _cuda_memory(torch), "host": _host_memory()}
    if segments:
        report["phases"][phase]["segments"] = _segments(torch.cuda.memory_snapshot())
    _write_json(path, report)


def _ranges(tensors):
    return {name: {
        "start": tensor.data_ptr(), "end": tensor.data_ptr() + tensor.nbytes,
        "bytes": tensor.nbytes, "dtype": str(tensor.dtype), "shape": list(tensor.shape),
    } for name, tensor in tensors.items()}


def _constant_exact(tensor, expected):
    return tensor.min().item() == expected and tensor.max().item() == expected


def _identity(args, torch, saver):
    native = _read_json(args.native_source_receipt)
    from torch_memory_saver.utils import get_binary_path_from_package

    binary = get_binary_path_from_package("torch_memory_saver_hook_mode_preload")
    expected = next(item for item in native["files"] if Path(item["installed_path"]).name == binary.name)
    entrypoint = inspect.getsourcefile(type(saver))
    expected_python = next(item for item in native["files"] if item["relative_path"] == "torch_memory_saver/entrypoint.py")
    if _sha256(binary) != expected["sha256"] or importlib.metadata.version("torch_memory_saver") != native["tms_version"]:
        raise ValueError("Installed TMS version/ELF does not match the retained native source receipt")
    if _sha256(entrypoint) != expected_python["sha256"]:
        raise ValueError("Installed TMS Python entrypoint differs from the retained native source")
    if os.environ.get("LD_PRELOAD") != str(binary):
        raise ValueError("Require the exact formal preload ELF")
    if torch.cuda.device_count() != 1 or "H200" not in torch.cuda.get_device_name(0):
        raise ValueError("Require exactly one visible H200")
    command = ["nvidia-smi", "--query-gpu=name,uuid,memory.total", "--format=csv,noheader,nounits"]
    gpu = subprocess.run(command, check=True, capture_output=True, text=True).stdout.strip().splitlines()
    if len(gpu) != 1 or "H200" not in gpu[0]:
        raise ValueError(f"nvidia-smi must report one H200, got {gpu}")
    if torch.cuda.get_allocator_backend() != "native":
        raise ValueError("This inactive-split diagnostic requires the native CUDA caching allocator")
    saver._ensure_initialized()
    native_api = saver._impl._binary_wrapper.cdll
    flags = {
        "interesting_region": native_api.tms_get_interesting_region(),
        "enable_cpu_backup": native_api.tms_get_enable_cpu_backup(),
        "enable_disk_backup": native_api.tms_get_enable_disk_backup(),
        "cpu_backup_backend": native_api.tms_get_cpu_backup_backend().decode(),
        "current_tag": native_api.tms_get_current_tag().decode(),
        "retain_cpu_backup": saver.retain_cpu_backup,
    }
    if not flags["interesting_region"] or not flags["enable_cpu_backup"] or flags["enable_disk_backup"]:
        raise ValueError(f"Native TMS flags differ from formal CPU offload: {flags}")
    if flags["cpu_backup_backend"] != "pinned" or flags["current_tag"] != "default":
        raise ValueError(f"Require the formal default-tag pinned backup: {flags}")
    return {
        "python": platform.python_version(), "torch": torch.__version__, "cuda": torch.version.cuda,
        "tms_version": native["tms_version"], "preload_elf": str(binary), "preload_sha256": expected["sha256"],
        "tms_entrypoint": entrypoint, "tms_entrypoint_sha256": expected_python["sha256"],
        "nvidia_smi_argv": command, "nvidia_smi": gpu, "tms_flags": flags,
        "allocator_env": {key: os.environ.get(key) for key in _ALLOCATOR_ENV},
        "tms_env": {key: value for key, value in os.environ.items() if key.startswith("TMS_")},
        "worker_local_caches": {key: os.environ.get(key) for key in (
            "TMPDIR", "TRITON_CACHE_DIR", "TORCHINDUCTOR_CACHE_DIR", "CUDA_CACHE_PATH", "TORCH_EXTENSIONS_DIR",
        )},
        "native_byte_counters": {"allocated_bytes": None, "backup_bytes": None,
                                 "status": "unavailable: retained CUDA Python API exposes no total-byte counter; no guessed symbols called"},
    }


def _optimizer(torch, receipt, parameter):
    from megatron.core.optimizer import OptimizerConfig, USING_PYTORCH_OPTIMIZER
    from megatron.core.optimizer import _get_megatron_optimizer_based_on_param_groups as factory

    training = receipt["resolved_experiment"]["training"]
    config = OptimizerConfig(**{name: training[name] for name in (
        "optimizer", "lr", "weight_decay", "adam_beta1", "adam_beta2", "adam_eps",
    )})
    if USING_PYTORCH_OPTIMIZER or config.optimizer != "adam" or config.use_precision_aware_optimizer:
        raise ValueError("Require native non-precision-aware FusedAdam; no generic-zeros fallback")
    optimizer, initialize = factory(config, [], [{"params": [parameter]}], skip_megatron_wrapping=True)
    if initialize is None or type(optimizer).__name__ != "FusedAdam" or optimizer.state:
        raise ValueError("Require an initially empty native FusedAdam state and its init_state_fn")
    source = inspect.getsourcefile(factory)
    return optimizer, initialize, config, {
        "class": f"{type(optimizer).__module__}.{type(optimizer).__name__}",
        "factory": factory.__qualname__, "init_state_fn": initialize.__qualname__,
        "source_path": source, "source_sha256": _sha256(source),
        "factory_first_line": inspect.getsourcelines(factory)[1],
        "initialization_first_line": inspect.getsourcelines(initialize)[1],
        "uses_precision_aware_optimizer": config.use_precision_aware_optimizer,
        "optimizer_cpu_offload": config.optimizer_cpu_offload,
    }


def _initialize_moments(optimizer, initialize, config, parameter):
    initialize(optimizer, config)
    state = optimizer.state[parameter]
    if set(state) != {"exp_avg", "exp_avg_sq"} or not all(_constant_exact(tensor, 0) for tensor in state.values()):
        raise ValueError("Native callback did not initialize exactly two zero moments")
    pointers = _ranges(state)
    initialize(optimizer, config)
    if pointers != _ranges(state):
        raise ValueError("Repeated native initialization changed state storage")


def _execute_case(args, report, path, receipt):
    import torch
    from torch_memory_saver import torch_memory_saver as saver
    from miles.utils.args.configs.train import TrainConfig
    from miles.utils.memory_utils import clear_memory

    report["identity"] = _identity(args, torch, saver)
    margin = int(_argv_value(receipt["training_argv"], "train_memory_margin_bytes",
                             TrainConfig.model_fields["train_memory_margin_bytes"].default))
    saver.memory_margin_bytes = margin
    report["identity"]["train_memory_margin_bytes"] = margin
    torch.cuda.set_device(0)
    clear_memory()
    _capture(torch, report, path, "baseline")
    # This FP32 tensor represents a master-parameter shard, not a BF16 DDP param buffer.
    parameter = torch.nn.Parameter(torch.full((args.moment_mib * _MIB // 4,), 1.0, device="cuda", dtype=torch.float32))
    optimizer, initialize, config, report["optimizer"] = _optimizer(torch, receipt, parameter)
    if args.case == "early_moments":
        _initialize_moments(optimizer, initialize, config, parameter)
    transient = torch.full((args.transient_mib * _MIB // 2,), 0.25, device="cuda", dtype=torch.bfloat16)
    torch.cuda.synchronize()
    report["transient_range"] = _ranges({"transient": transient})["transient"]
    del transient
    torch.cuda.synchronize()
    _capture(torch, report, path, "transient_released")
    if args.case == "late_moments":
        _initialize_moments(optimizer, initialize, config, parameter)
    tensors = {"master_parameter": parameter, **optimizer.state[parameter],
               "optimizer_dummy_overflow": optimizer._dummy_overflow_buf}
    expected = {"master_parameter": 1.0, "exp_avg": 0.125, "exp_avg_sq": 0.5, "optimizer_dummy_overflow": 0}
    with torch.no_grad():
        for name, tensor in tensors.items():
            tensor.fill_(expected[name])
    report["persistent_ranges"] = _ranges(tensors)
    report["moment_state_bytes"] = sum(tensor.nbytes for tensor in optimizer.state[parameter].values())
    if report["moment_state_bytes"] != 2 * args.moment_mib * _MIB:
        raise ValueError("Native moment sizes differ from the explicit input")
    report["optimizer_scratch_ranges"] = _ranges({"dummy_overflow": optimizer._dummy_overflow_buf})
    torch.cuda.synchronize()
    _capture(torch, report, path, "before_cleanup")
    clear_memory()
    _capture(torch, report, path, "before_pause", segments=True)
    saver.pause(tag=None)
    _capture(torch, report, path, "paused")
    backups = {}
    for name, tensor in tensors.items():
        view = saver.get_cpu_backup(tensor, zero_copy=True)
        backups[name] = view is not None and _constant_exact(view, expected[name])
        del view
    report["cpu_backup_exact"] = backups
    saver.resume(tag=None)
    torch.cuda.synchronize()
    _capture(torch, report, path, "after_resume")
    report["roundtrip_exact"] = {name: _constant_exact(tensor, expected[name]) for name, tensor in tensors.items()}
    report["roundtrip_pointers_unchanged"] = report["persistent_ranges"] == _ranges(tensors)
    report["gpu_release_observed"] = (
        report["phases"]["paused"]["cuda"]["device_free_bytes"]
        > report["phases"]["before_pause"]["cuda"]["device_free_bytes"]
    )
    if not all(backups.values()) or not all(report["roundtrip_exact"].values()) or not report["roundtrip_pointers_unchanged"]:
        raise ValueError("Native pause/resume did not preserve every probed persistent tensor exactly")
    if not report["gpu_release_observed"]:
        raise ValueError("Device free bytes did not increase during native pause on the isolated GPU")
    # A post-roundtrip native step checks that FusedAdam consumes the callback-created state.
    # Full gradient buffers are not modeled; this temporary gradient follows formal no-backup mode.
    with saver.region(tag="grad_buffer", enable_cpu_backup=False):
        parameter.grad = torch.ones_like(parameter)
    optimizer.step()
    torch.cuda.synchronize()
    report["native_step"] = {"step": optimizer.param_groups[0]["step"],
                             "parameter_finite": bool(torch.isfinite(parameter).all().item())}
    if report["native_step"]["step"] != 1 or not report["native_step"]["parameter_finite"]:
        raise ValueError("Native FusedAdam step failed")
    parameter.grad = None


def _case(args):
    path = args.output_dir / f"{args.case}.json"
    report = {
        "case": args.case, "pid": os.getpid(), "status": "starting", "phases": {},
        "inputs": {"transient_bytes": args.transient_mib * _MIB, "moment_bytes_each": args.moment_mib * _MIB},
        "limits": [
            "Allocation-order mechanism test, not a full-model OOM reproduction or formal root-cause proof.",
            "Moments are initialized by native init_state_fn, not lazily by a full training backward/step.",
            "FP32 master shard and moments use the formal default-tag CPU-backup context.",
            "No BF16 DDP param buffer is allocated; formal offload disables param/grad buffer backups.",
            "Native byte counters unavailable; CUDA segment sizes and host deltas are not measured TMS backup bytes.",
            "VmLck may not account for CUDA-pinned pages; cgroup readings include other processes and file cache.",
        ],
    }
    if args.prepared:
        existing = _read_json(path)
        if existing["pid"] != os.getpid() or existing["status"] != "starting":
            raise ValueError("--prepared is internal and must follow this subprocess's environment re-exec")
    else:
        _write_json(path, report, exclusive=True)
    try:
        receipt = _read_json(args.launch_receipt)
        if not args.prepared:
            _prepare_case(args, receipt)
        report["image_from_launch_receipt"] = receipt["resolved_experiment"]["image"]
        _execute_case(args, report, path, receipt)
        report["status"] = "passed"
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc())
    _write_json(path, report)
    print(json.dumps({"case": args.case, "status": report["status"], "report": str(path)}, allow_nan=False), flush=True)
    return 0 if report["status"] == "passed" else 1


def _comparison(cases):
    if any(cases[name]["status"] != "passed" for name in _CASES):
        return {"status": "incomplete", "formal_run_root_cause_proven": False}
    late, early = (cases[name] for name in _CASES)
    result = {"status": "complete", "formal_run_root_cause_proven": False, "cases": {}}
    for name, case in cases.items():
        before, paused = (case["phases"][phase] for phase in ("before_pause", "paused"))
        transient = case["transient_range"]
        reused = [name for name in ("exp_avg", "exp_avg_sq")
                  if transient["start"] <= case["persistent_ranges"][name]["start"] < transient["end"]]
        result["cases"][name] = {
            "reserved_bytes_before_pause": before["cuda"]["reserved_bytes"],
            "inactive_split_bytes_before_pause": before["cuda"]["inactive_split_bytes"],
            "moments_in_former_transient_range": reused,
            "rss_pause_delta_bytes": paused["host"]["rss_bytes"] - before["host"]["rss_bytes"],
            "cgroup_pause_delta_bytes": paused["host"]["cgroup"]["current_bytes"] - before["host"]["cgroup"]["current_bytes"],
        }
    left, right = (result["cases"][name] for name in _CASES)
    result["same_moment_state_bytes"] = late["moment_state_bytes"] == early["moment_state_bytes"]
    result["allocator_order_effect_observed"] = bool(
        result["same_moment_state_bytes"] and left["moments_in_former_transient_range"]
        and not right["moments_in_former_transient_range"]
        and left["reserved_bytes_before_pause"] > right["reserved_bytes_before_pause"]
        and left["inactive_split_bytes_before_pause"] > right["inactive_split_bytes_before_pause"]
    )
    result["late_init_rss_pause_delta_larger"] = left["rss_pause_delta_bytes"] > right["rss_pause_delta_bytes"]
    result["late_init_cgroup_pause_delta_larger"] = left["cgroup_pause_delta_bytes"] > right["cgroup_pause_delta_bytes"]
    return result


def main(argv=None):
    args = _parser().parse_args(argv)
    if args.prepared and args.case is None:
        raise ValueError("--prepared requires an internal case subprocess")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.case:
        return _case(args)
    summary_path = args.output_dir / "summary.json"
    paths = [summary_path, *(args.output_dir / f"{name}.json" for name in _CASES)]
    if any(path.exists() for path in paths):
        raise FileExistsError("Probe output files already exist; choose a new output directory")
    summary = {"status": "running", "cases": {}, "formal_run_root_cause_proven": False}
    _write_json(summary_path, summary, exclusive=True)
    for name in _CASES:
        command = [sys.executable, str(Path(__file__).resolve()),
                   "--launch-receipt", str(args.launch_receipt.resolve()),
                   "--native-source-receipt", str(args.native_source_receipt.resolve()),
                   "--transient-mib", str(args.transient_mib), "--moment-mib", str(args.moment_mib),
                   "--output-dir", str(args.output_dir.resolve()), "--case", name]
        started = time.monotonic()
        completed = subprocess.run(command, check=False)
        path = args.output_dir / f"{name}.json"
        case = _read_json(path) if path.exists() else {"status": "missing"}
        if completed.returncode != 0 or case["status"] != "passed":
            case["status"] = "failed"
        case.update(returncode=completed.returncode, elapsed_seconds=time.monotonic() - started, subprocess_argv=command)
        summary["cases"][name] = case
        _write_json(summary_path, summary)
    summary["comparison"] = _comparison(summary["cases"])
    summary["status"] = "complete" if summary["comparison"]["status"] == "complete" else "incomplete"
    _write_json(summary_path, summary)
    print(json.dumps({"status": summary["status"], "summary": str(summary_path), "comparison": summary["comparison"]}), flush=True)
    return 0 if summary["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
