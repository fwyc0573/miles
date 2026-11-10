"""Isolated H800-only native GDN snapshot semantics probe, never a training gate.

Run with the formal image's Python and environment, before attention imports:
    python3 -B -m tests.manual.agent_opd.probe_mamba_fp32_snapshots \
        --config task_memory/task_2026-11-08_qwen35_full_kl_nll/mamba_snapshot_semantics_config.json \
        --image "$IMAGE" --output-dir "$TASK_EVIDENCE/exp-name"

--validate-config and --help are stdlib-only CPU checks. Actual CUDA execution
uses the qualified candidate twice (tracking off/on), not untouched-code GPU
A/B. Native prefix forwards supply the FP32 oracle; no custom recurrence,
tolerance, fallback, or mocked CUDA verdict is used. All producer forwards end
before the single end-phase synchronization and tensor-content inspection.
"""

import argparse
import importlib.metadata
import importlib.util
import inspect
import json
import math
import os
import platform
import subprocess
import sys
import traceback
from pathlib import Path

from tests.manual.agent_opd.sglang_mamba_snapshots import prepare_source, source_manifest


_TASK_ID = "profile-native-snapshot-semantics-20261111"


def _load_config(path):
    config = json.loads(path.read_text())
    formal_path = (path.parent / config["formal_config"]).resolve(strict=True)
    formal = json.loads(formal_path.read_text())
    if formal["image"] != source_manifest()["image"] or formal["gpu_tag"] != "H800":
        raise ValueError("Require the qualified formal H800 image configuration")
    if config["backend"] != "triton" or config["layout"] != "equal_length":
        raise ValueError("This isolated native ABI probe requires Triton equal-length inputs")
    if config["qkv_dtype"] != "bfloat16" or config["state_dtype"] != "float32":
        raise ValueError("Require BF16 Q/K/V and FP32 temporal states")
    if config["gate_dtype"] != "float32" or config["index_dtype"] != "int32":
        raise ValueError("Require FP32 gates and int32 native row/chunk indices")
    for key in ("batch_size", "qk_heads", "value_heads", "key_dim", "value_dim", "state_slots",
                "kernel_chunk_size", "mamba_cache_chunk_size", "tree_page_size", "visible_gpus"):
        if type(config[key]) is not int or config[key] <= 0:
            raise ValueError(f"{key} must be a positive integer")
    if config["visible_gpus"] != 1 or config["key_dim"] > 256:
        raise ValueError("Require one visible H800 and native key_dim <= 256")
    if config["value_heads"] % config["qk_heads"]:
        raise ValueError("value_heads must be divisible by qk_heads")
    if type(config["seed"]) is not int or config["seed"] < 0:
        raise ValueError("seed must be a nonnegative integer")
    for key in ("initial_state_scale", "gate_scale"):
        if not math.isfinite(config[key]) or config[key] <= 0:
            raise ValueError(f"{key} must be finite and positive")
    if not math.isfinite(config["snapshot_sentinel"]):
        raise ValueError("snapshot_sentinel must be finite")
    indices = config["cache_indices"]
    if len(indices) != config["batch_size"] or any(
        type(row) is not int or row < -1 or row >= config["state_slots"] for row in indices
    ):
        raise ValueError("cache_indices must supply one native slot or -1 per batch row")
    valid = [row for row in indices if row >= 0]
    if len(valid) < 2 or len(set(valid)) != len(valid) or valid == sorted(valid):
        raise ValueError("Require distinct, nonsequential state slots for at least two live rows")
    boundaries = config["boundary_tokens"]
    grid = math.lcm(config["mamba_cache_chunk_size"], config["tree_page_size"])
    if len(set(boundaries)) < 2 or any(
        type(end) is not int or end <= 0 or end % grid or end % config["kernel_chunk_size"] for end in boundaries
    ):
        raise ValueError("Require at least two interior boundaries on both native chunk and prefill grids")
    if not config["sequence_lengths"] or any(
        type(length) is not int or length <= max(boundaries) for length in config["sequence_lengths"]
    ):
        raise ValueError("Every nonempty sequence must extend beyond both interior checkpoints")
    selected = set()
    for positions in config["track_chunk_indices"]:
        if len(positions) != len(indices):
            raise ValueError("track_chunk_indices must supply one chunk-entry index per batch row")
        for row, chunk in enumerate(positions):
            if type(chunk) is not int or chunk < -1:
                raise ValueError("Native tracking accepts chunk-entry indices or the -1 skip sentinel")
            if indices[row] < 0 and chunk != -1:
                raise ValueError("Padded rows must not request a temporal checkpoint")
            if chunk >= 0:
                end = chunk * config["kernel_chunk_size"]
                if end not in boundaries:
                    raise ValueError("Each selected chunk entry must have a configured native prefix oracle")
                selected.add(end)
    if selected != set(boundaries) or not config["track_chunk_indices"]:
        raise ValueError("Tracking cases must exercise every configured interior boundary")
    mount = Path(formal["local_mount"]).resolve()
    if not path.resolve().is_relative_to(mount) or not Path(formal["repo"]).resolve().is_relative_to(mount):
        raise ValueError("Config and repository must use the formal local mount")
    if Path(formal["worker_local_root"]).resolve().is_relative_to("/mnt"):
        raise ValueError("Temporary tensors and compilation caches must be worker-local")
    return config, formal, formal_path, grid


def _metadata(tensor):
    return {"dtype": str(tensor.dtype), "shape": list(tensor.shape), "stride": list(tensor.stride()),
            "device": str(tensor.device)}


def _compare(torch, actual, expected):
    actual, expected = actual.double(), expected.double()
    finite = bool(torch.isfinite(actual).all() and torch.isfinite(expected).all())
    if not finite:
        return {"exact": False, "finite": False, "elements": actual.numel(),
                "max_absolute_error": None, "max_relative_error_nonzero_reference": None,
                "numerical_errors": "Undefined for nonfinite tensors"}
    error = (actual - expected).abs()
    nonzero = expected != 0
    return {
        "exact": bool(torch.equal(actual, expected)),
        "finite": finite,
        "elements": actual.numel(), "max_absolute_error": error.max().item(),
        "max_relative_error_nonzero_reference": (error[nonzero] / expected[nonzero].abs()).max().item()
        if bool(nonzero.any()) else None,
        "relative_error_undefined_zero_reference_elements": int((~nonzero).sum().item()),
        "zero_reference_max_absolute_error": error[~nonzero].max().item() if bool((~nonzero).any()) else None,
    }


def _check(report, name, passed, **evidence):
    report["checks"][name] = {"passed": bool(passed), **evidence}
    if not passed:
        report["failed_checks"].append(name)


def _produce(torch, backend, config):
    """Enqueue native forwards only; never read tensor contents or synchronize."""
    torch.manual_seed(config["seed"])
    batch, heads = config["batch_size"], config["value_heads"]
    key_dim, value_dim = config["key_dim"], config["value_dim"]
    initial = torch.randn(config["state_slots"], heads, value_dim, key_dim,
                          device="cuda", dtype=torch.float32) * config["initial_state_scale"]
    indices = torch.tensor(config["cache_indices"], device="cuda", dtype=torch.int32)
    cases = []
    for length in config["sequence_lengths"]:
        q = torch.randn(batch, length, config["qk_heads"], key_dim, device="cuda", dtype=torch.bfloat16)
        k = torch.randn_like(q)
        v = torch.randn(batch, length, heads, value_dim, device="cuda", dtype=torch.bfloat16)
        g = -torch.rand(batch, length, heads, device="cuda", dtype=torch.float32) * config["gate_scale"]
        beta = torch.randn_like(g).sigmoid()
        inputs = dict(q=q, k=k, v=v, g=g, beta=beta)

        def forward(tokens, positions=None):
            state = initial.clone()
            arguments = {name: tensor[:, :tokens].contiguous() for name, tensor in inputs.items()}
            arguments.update(ssm_states=state, cache_indices=indices, query_start_loc=None, inplace_update=True)
            snapshot = None
            if positions is not None:
                snapshot = torch.full((batch, heads, value_dim, key_dim), config["snapshot_sentinel"],
                                      device="cuda", dtype=torch.float32)
                arguments.update(track_state=snapshot,
                                 track_chunk_idx=torch.tensor(positions, device="cuda", dtype=torch.int32))
            output, returned_final, h = backend.extend(**arguments)
            return {"output": output, "returned_final": returned_final, "h": h, "state": state,
                    "snapshot": snapshot, "arguments": arguments}

        ordinary = forward(length)
        tracked = [forward(length, positions) for positions in config["track_chunk_indices"]]
        prefixes = {end: forward(end) for end in config["boundary_tokens"]}
        cases.append({"length": length, "inputs": inputs, "indices": indices, "initial": initial,
                      "ordinary": ordinary, "tracked": tracked, "prefixes": prefixes})
    return cases


def _inspect(torch, config, cases, local, report):
    """All producers have ended; archive CPU tensors and collect numeric evidence."""
    raw = {}
    report["cases"] = []
    witnesses = 0
    for case in cases:
        length, ordinary = case["length"], case["ordinary"]
        label = f"length_{length}"
        rows = {"length": length, "input_metadata": {name: _metadata(t) for name, t in case["inputs"].items()},
                "state_metadata": _metadata(ordinary["state"]), "index_metadata": _metadata(case["indices"]),
                "output_metadata": _metadata(ordinary["output"]), "h_metadata": _metadata(ordinary["h"]),
                "native_arguments": {"query_start_loc": None, "inplace_update": True,
                                     "cache_indices": config["cache_indices"], "head_first": False,
                                     "use_qk_l2norm_in_kernel": True,
                                     "scale": config["key_dim"] ** -0.5}, "tracked": []}
        raw[label] = {name: tensor.detach().cpu() for name, tensor in case["inputs"].items()}
        raw[label].update(initial_state=case["initial"].cpu(), cache_indices=case["indices"].cpu(),
                          ordinary_output=ordinary["output"].cpu(), ordinary_h=ordinary["h"].cpu(),
                          ordinary_final_state=ordinary["state"].cpu())
        _check(report, f"{label}/ordinary_contract",
               ordinary["returned_final"] is None and ordinary["output"].dtype == torch.bfloat16
               and ordinary["h"].dtype == torch.bfloat16 and ordinary["state"].dtype == torch.float32
               and ordinary["h"].shape == (config["batch_size"], math.ceil(length / config["kernel_chunk_size"]),
                                          config["value_heads"], config["value_dim"], config["key_dim"]))
        for number, tracked in enumerate(case["tracked"]):
            positions = config["track_chunk_indices"][number]
            checks = {}
            for name in ("output", "h", "state"):
                comparison = _compare(torch, tracked[name], ordinary[name])
                checks[f"unchanged_{name}"] = comparison
                _check(report, f"{label}/tracking_{number}/unchanged_{name}",
                       comparison["exact"] and comparison["finite"], **comparison)
            _check(report, f"{label}/tracking_{number}/return_contract",
                   tracked["returned_final"] is None and tracked["snapshot"].dtype == torch.float32
                   and tracked["h"].dtype == torch.bfloat16)
            row_checks = []
            for row, (slot, chunk) in enumerate(zip(config["cache_indices"], positions)):
                snapshot = tracked["snapshot"][row]
                if chunk == -1:
                    comparison = _compare(torch, snapshot, torch.full_like(snapshot, config["snapshot_sentinel"]))
                    _check(report, f"{label}/tracking_{number}/row_{row}/skip_unchanged", comparison["exact"], **comparison)
                    row_checks.append({"batch_row": row, "state_slot": slot, "track_chunk_idx": chunk,
                                       "skip_unchanged": comparison})
                    continue
                end = chunk * config["kernel_chunk_size"]
                prefix = case["prefixes"][end]
                comparison = _compare(torch, snapshot, prefix["state"][slot])
                _check(report, f"{label}/tracking_{number}/row_{row}/native_prefix_{end}",
                       comparison["exact"] and comparison["finite"], **comparison)
                rounded = _compare(torch, snapshot.to(torch.bfloat16), tracked["h"][row, chunk])
                _check(report, f"{label}/tracking_{number}/row_{row}/ordinary_h_rounding",
                       rounded["exact"] and rounded["finite"], **rounded)
                unrounded = _compare(torch, snapshot, tracked["h"][row, chunk].float())
                count = int((snapshot != tracked["h"][row, chunk].float()).sum().item())
                witnesses += count
                row_checks.append({"batch_row": row, "state_slot": slot, "track_chunk_idx": chunk,
                                   "prefix_tokens": end, "native_prefix_final_state": comparison,
                                   "rounded_snapshot_matches_ordinary_h": rounded,
                                   "snapshot_vs_bf16_h_cast_to_fp32": unrounded,
                                   "unrounded_elements": count})
            checks.update(track_chunk_idx=positions, snapshot_metadata=_metadata(tracked["snapshot"]), rows=row_checks,
                          argument_metadata={name: _metadata(value) for name, value in tracked["arguments"].items()
                                             if isinstance(value, torch.Tensor)})
            rows["tracked"].append(checks)
            raw[label][f"tracking_{number}"] = {name: tracked[name].cpu() for name in ("output", "h", "state", "snapshot")}
        for end, prefix in case["prefixes"].items():
            raw[label][f"prefix_{end}"] = {name: prefix[name].cpu() for name in ("output", "h", "state")}
        unused = [slot for slot in range(config["state_slots"]) if slot not in config["cache_indices"]]
        if unused:
            comparison = _compare(torch, ordinary["state"][unused], case["initial"][unused])
            _check(report, f"{label}/unused_state_slots_unchanged", comparison["exact"], **comparison)
        for row, slot in enumerate(config["cache_indices"]):
            if slot < 0:
                comparison = _compare(torch, ordinary["h"][row, 0], torch.zeros_like(ordinary["h"][row, 0]))
                _check(report, f"{label}/padded_row_{row}/zero_initial_h", comparison["exact"], **comparison)
        report["cases"].append(rows)
    _check(report, "fp32_store_not_bf16_roundtrip", witnesses > 0, unrounded_elements=witnesses)
    raw_path = local / "tensors.pt"
    torch.save(raw, raw_path)
    report["raw_small_tensors_worker_local"] = str(raw_path)


def _run(args, config, formal, formal_path, grid, report):
    if Path(sys.executable).resolve() != Path(formal["worker_python"]).resolve():
        raise ValueError("Execute with the formal pinned image's worker_python, not host Python")
    if args.image != formal["image"]:
        raise ValueError("--image must be the actual qualified launch image")
    if any(name.startswith("sglang.srt.layers.attention") or name.startswith("sglang.kernels.ops.attention")
           for name in sys.modules):
        raise RuntimeError("Source preparation must precede attention imports")
    job = os.environ["KUBEBRAIN_RJOB_NAME"]
    if Path(job).name != job or job in ("", ".", ".."):
        raise ValueError("Platform job name must be a single directory component")
    if (int(os.environ["KUBEBRAIN_REPLICA"]), int(os.environ["KUBEBRAIN_REPLICA_TOTAL"])) != (0, 1):
        raise ValueError("This probe requires one dedicated worker replica")
    local = Path(formal["worker_local_root"]) / f"mamba-snapshots-{job}"
    root = Path(importlib.util.find_spec("sglang").origin).parent
    report["source_preflight"] = prepare_source(root, image=args.image, selected_fp32=True,
                                                archive_dir=args.output_dir / "source_preflight")
    # Reuse worker-local cache placement only after source qualification.
    from tests.manual.agent_opd.rjob_warmup import _worker_environment

    _worker_environment(local)
    import torch
    import triton
    from sglang.kernels.ops.attention.fla import chunk, chunk_delta_h
    from sglang.srt.layers.attention.linear.kernels.gdn_triton import TritonGDNKernel

    command = ["nvidia-smi", "--query-gpu=name,uuid,memory.total,driver_version", "--format=csv,noheader,nounits"]
    gpu = subprocess.run(command, capture_output=True, text=True, check=True)
    report["runtime"] = {
        "job": job, "python": platform.python_version(), "python_executable": sys.executable,
        "torch": torch.__version__, "triton": triton.__version__, "cuda": torch.version.cuda,
        "sglang": importlib.metadata.version("sglang"), "nvidia_smi_argv": command,
        "nvidia_smi_stdout": gpu.stdout, "nvidia_smi_stderr": gpu.stderr,
        "formal_config": str(formal_path), "formal_image": formal["image"],
        "formal_local_mount": formal["local_mount"], "formal_mounts": formal["mounts"],
        "worker_local_directory": str(local), "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "environment": {key: value for key, value in os.environ.items()
                        if key.startswith(("SGLANG_", "NCCL_")) or key in (
                            "LD_LIBRARY_PATH", "LD_PRELOAD", "TMPDIR", "TRITON_CACHE_DIR",
                            "TORCHINDUCTOR_CACHE_DIR", "CUDA_CACHE_PATH", "TORCH_EXTENSIONS_DIR")},
    }
    if torch.cuda.device_count() != config["visible_gpus"] or "H800" not in torch.cuda.get_device_name(0):
        raise ValueError("Require exactly one visible actual H800")
    if any("H800" not in line for line in gpu.stdout.strip().splitlines()) or not gpu.stdout.strip():
        raise ValueError("nvidia-smi must identify actual H800 hardware")
    torch.cuda.set_device(0)
    report["runtime"]["device_capability"] = list(torch.cuda.get_device_capability(0))
    backend = TritonGDNKernel()
    report["native_abi"] = {
        "backend": f"{type(backend).__module__}.{type(backend).__name__}",
        "supports_track_state_snapshot": backend.supports_track_state_snapshot,
        "extend_signature": str(inspect.signature(backend.extend)),
        "chunk_signature": str(inspect.signature(chunk.chunk_gated_delta_rule)),
        "fwd_h_signature": str(inspect.signature(chunk_delta_h.chunk_gated_delta_rule_fwd_h)),
        "kernel_chunk_size": chunk.CHUNK_SIZE, "prefill_checkpoint_grid": grid,
        "snapshot_semantics": "h[c] is the FP32 state before chunk c, after c*kernel_chunk_size input tokens",
    }
    if not backend.supports_track_state_snapshot or chunk.CHUNK_SIZE != config["kernel_chunk_size"]:
        raise ValueError("Qualified native CUDA capability/chunk size differs from the operator inputs")
    if chunk_delta_h.CHUNK_SIZE != chunk.CHUNK_SIZE:
        raise ValueError("Public forward and recurrence chunk sizes differ")
    with torch.no_grad():
        cases = _produce(torch, backend, config)
        report["all_producer_forwards_ended"] = True
        torch.cuda.synchronize()
        report["end_phase_synchronization_completed"] = True
        _inspect(torch, config, cases, local, report)
    compiled = sorted(str(path.relative_to(local / "triton")) for path in (local / "triton").rglob("*.cubin"))
    report["compiled_cuda_binaries_worker_local"] = compiled
    _check(report, "native_cuda_compilation", bool(compiled), fresh_worker_local_triton_cache=str(local / "triton"))
    report["cuda_semantics"] = "FAIL" if report["failed_checks"] else "PASS"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-config", action="store_true", help="CPU-only structural validation; no CUDA imports")
    parser.add_argument("--image", help="Actual primary-owned pinned worker launch image")
    parser.add_argument("--output-dir", type=Path, help="Fresh evidence directory under the mounted task path")
    args = parser.parse_args(argv)
    output_created = False
    report = {"task_id": _TASK_ID, "status": "FAIL", "cuda_semantics": "UNVERIFIED", "checks": {}, "failed_checks": [],
              "method": "Same qualified candidate, native tracking-off/on and independent native prefix forwards",
              "limitations": ["Not untouched-code GPU A/B, full-model warm parity, throughput, or race exclusion",
                              "Equal-length operator ABI only; native varlen index preparation reads GPU contents",
                              "No zero-token forward: not a reachable teacher-scoring input contract",
                              "Independent probe verdict never gates or controls training"]}
    try:
        config, formal, formal_path, grid = _load_config(args.config.resolve(strict=True))
        report["operator_inputs"] = config
        if args.validate_config:
            report.update(status="CPU_CONFIG_PASS", prefill_checkpoint_grid=grid)
        else:
            if args.output_dir is None or args.image is None:
                raise ValueError("CUDA execution requires --image and --output-dir")
            args.output_dir = args.output_dir.resolve()
            task = args.config.resolve().parent
            if not args.output_dir.is_relative_to(task / "evidence"):
                raise ValueError("Retained verdict/source receipts must stay in this mounted task's evidence directory")
            args.output_dir.mkdir(parents=True, exist_ok=False)
            output_created = True
            _run(args, config, formal, formal_path, grid, report)
            report["status"] = report["cuda_semantics"]
    except BaseException as error:
        report["failed_checks"].append("execution_exception")
        report["exception"] = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}
        if isinstance(error, subprocess.CalledProcessError):
            report["exception"].update(argv=error.cmd, returncode=error.returncode, stdout=error.stdout, stderr=error.stderr)
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if output_created:
        verdict = args.output_dir / "verdict.json"
        with verdict.open("x") as stream:
            stream.write(text)
    print(text, end="", flush=True)
    return 0 if report["status"] in ("PASS", "CPU_CONFIG_PASS") else 1


if __name__ == "__main__":
    sys.exit(main())
