"""CUDA-only TP2/CP1/thd loss-seam diagnostic; never loads a model or an optimizer.

Run in the pinned worker image from the repository root with torchrun --standalone
--nproc-per-node=2 --module tests.manual.agent_opd.probe_qwen35_loss_memory.
Supply --rollout-data, --sample-index, --launch-receipt, --padded-vocab-size,
--data-pad-size-multiplier, --gradient-chunk-rows, and --report. The two geometry
values not present in launch.json must come from the native resolved configuration.
--geometry-only runs native packing on CPU, without CUDA or distributed startup.

The objective is the negative SUM of retained, masked response log-probs, not the
formal OPD/TIS objective. Logits are reproducible standard-normal BF16 shards, not
real model outputs. autograd.grad measures the gradient at the model-output seam:
no artificial leaf .grad buffer, model backward, optimizer, or update is measured.
The torch input is released before fused; only its BF16 gradient remains on GPU.
No full gradient is copied to CPU. An OOM reference gives numerical INCOMPLETE
(exit 2), never PASS; other failed checks give exit 1. GPU exit 0 requires both ranks.
"""

import argparse
import contextlib
import dataclasses
import gc
import json
import math
import os
import platform
import sys
from pathlib import Path

# Established native-entry tolerances, not the formal training/inference gate:
# tests/fast-gpu/test_fused_log_probs_in_losses.py:33-36,146-148 and
# tests/fast-gpu/test_fused_log_probs.py:305,309.
_LOGPROB_TOL = {"rtol": 1e-5, "atol": 2e-5}
_GRAD_TOL = {"rtol": 2e-2, "atol": 5e-3}
_TOLERANCE_SOURCE = [
    "tests/fast-gpu/test_fused_log_probs_in_losses.py:33-36,146-148",
    "tests/fast-gpu/test_fused_log_probs.py:305,309",
]


def _cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rollout-data", type=Path, required=True)
    parser.add_argument("--sample-index", type=int, required=True)
    parser.add_argument("--launch-receipt", type=Path, required=True)
    parser.add_argument("--padded-vocab-size", type=int, required=True)
    parser.add_argument("--data-pad-size-multiplier", type=int, required=True)
    parser.add_argument("--gradient-chunk-rows", type=int, required=True, help="Only bounds validation scratch, not logits")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--trace-allocations", action="store_true", help="Record large eager ATen allocations, without retaining tensors")
    parser.add_argument("--geometry-only", action="store_true")
    args = parser.parse_args()
    if args.sample_index < 0 or min(args.padded_vocab_size, args.data_pad_size_multiplier, args.gradient_chunk_rows) <= 0:
        parser.error("sample index must be nonnegative; vocabulary, padding multiplier, and chunk rows must be positive")
    return args


def _launch_args(cli, receipt):
    # Defer worker-only dependencies so --help works on the controller host.
    from miles.utils.args.configs.algo import AlgoConfig
    from miles.utils.args.configs.train import TrainConfig

    parser = argparse.ArgumentParser(add_help=False)
    for name, kind in (
        ("tensor_model_parallel_size", int), ("context_parallel_size", int),
        ("vocab_size", int), ("rollout_temperature", float), ("seed", int),
    ):
        parser.add_argument("--" + name.replace("_", "-"), type=kind, required=True)
    provenance = {}
    for config, names in (
        (TrainConfig, ("qkv_format", "allgather_cp", "true_on_policy_mode", "recompute_loss_function", "log_probs_chunk_size", "log_probs_backend")),
        (AlgoConfig, ("loss_type", "entropy_coef", "observe_training_entropy")),
    ):
        for name in names:
            value = config.model_fields[name].default
            flag = "--" + name.replace("_", "-")
            options = {"action": "store_true"} if isinstance(value, bool) else {"type": type(value)}
            parser.add_argument(flag, default=value, **options)
            provenance[name] = "launch argv" if flag in receipt["training_argv"] else f"{config.__name__}.{name} native default"
    parser.add_argument("--data-pad-size-multiplier", type=int)
    args, _ = parser.parse_known_args([*receipt["model_argv"], *receipt["training_argv"]])
    if (args.tensor_model_parallel_size, args.context_parallel_size, args.qkv_format) != (2, 1, "thd"):
        raise ValueError("This diagnostic requires the actual launch to use TP2/CP1/thd")
    if args.true_on_policy_mode or args.recompute_loss_function or args.allgather_cp or args.loss_type != "policy_loss":
        raise ValueError("This probe supports the retained native policy-loss path, with no loss recompute or all-gather CP")
    if args.entropy_coef != 0 or args.observe_training_entropy or args.log_probs_backend != "torch":
        raise ValueError("Require the original torch launch with entropy disabled, matching this diagnostic's native call")
    if cli.padded_vocab_size != args.vocab_size:
        raise ValueError("Require the recorded vocabulary without padding, so torch/fused normalize identically")
    if not math.isfinite(args.rollout_temperature) or args.rollout_temperature <= 0:
        raise ValueError("The recorded rollout temperature must be finite and positive")
    if args.data_pad_size_multiplier is not None and args.data_pad_size_multiplier != cli.data_pad_size_multiplier:
        raise ValueError("Supplied native padding multiplier differs from the actual launch receipt")
    args.data_pad_size_multiplier = cli.data_pad_size_multiplier
    return args, provenance


def _pack(cli, args, *, device):
    import torch

    from miles.backends.training_utils.data.context_parallel import iter_local_response_rows
    from miles.backends.training_utils.data.rollout import DataIterator, get_batch

    # This is a trusted native debug dump. Load on CPU, and retain only this sample's tokens/mask.
    payload = torch.load(cli.rollout_data, map_location="cpu", weights_only=False)
    sample = payload["samples"][cli.sample_index]
    tokens = torch.as_tensor(sample["tokens"], dtype=torch.long, device=device)
    response = int(sample["response_length"])
    if tokens.ndim != 1 or not 0 < response < tokens.numel():
        raise ValueError("Retained sample must contain a nonempty prefix and response")
    if tokens.min().item() < 0 or tokens.max().item() >= args.vocab_size:
        raise ValueError("Retained token IDs are outside the actual vocabulary")
    mask = sample.get("loss_mask")
    mask = torch.ones(response, device=device) if mask is None else torch.as_tensor(mask, dtype=torch.float32, device=device)
    if mask.shape != (response,) or not torch.isfinite(mask).all().item() or mask.count_nonzero().item() == 0:
        raise ValueError("Retained response loss mask is invalid or empty")
    identity = {
        "rollout_id": payload["rollout_id"], "sample_index": cli.sample_index,
        "source_uid": sample["metadata"]["source"]["uid"],
        "total_length": tokens.numel(), "response_length": response,
        "mask_nonzero": mask.count_nonzero().item(),
    }
    del sample, payload
    data = {"tokens": [tokens], "total_lengths": [tokens.numel()], "response_lengths": [response], "loss_masks": [mask]}
    batch = get_batch(
        DataIterator(data, micro_batch_size=1), list(data),
        pad_multiplier=args.data_pad_size_multiplier, qkv_format=args.qkv_format, allgather_cp=args.allgather_cp,
    )
    rows = list(iter_local_response_rows(
        batch["tokens"].size(1), unconcat_tokens=batch["unconcat_tokens"], total_lengths=batch["total_lengths"],
        response_lengths=batch["response_lengths"], qkv_format=args.qkv_format, allgather_cp=args.allgather_cp,
        include_response_indices=False,
    ))
    identity.update(padded_tokens=batch["tokens"].size(1), cu_seqlens_host=batch["cu_seqlens_host"],
                    response_row_ranges=rows[0].row_ranges)
    return batch, identity


def _write(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")


def _memory(torch):
    torch.cuda.synchronize()
    stats = torch.cuda.memory_stats()
    free, total = torch.cuda.mem_get_info()
    return {
        name: stats[key] for name, key in (
            ("allocated_bytes", "allocated_bytes.all.current"), ("reserved_bytes", "reserved_bytes.all.current"),
            ("peak_allocated_bytes", "allocated_bytes.all.peak"), ("peak_reserved_bytes", "reserved_bytes.all.peak"),
            ("inactive_split_bytes", "inactive_split_bytes.all.current"), ("peak_inactive_split_bytes", "inactive_split_bytes.all.peak"),
            ("allocation_retries", "num_alloc_retries"), ("allocator_ooms", "num_ooms"),
        )
    } | {"device_free_bytes": free, "device_total_bytes": total}


def _allocation_trace(torch, events, threshold):
    from torch.utils._python_dispatch import TorchDispatchMode

    def describe(value):
        if isinstance(value, torch.Tensor):
            return {"shape": list(value.shape), "dtype": str(value.dtype), "device": str(value.device)}
        if isinstance(value, (list, tuple)):
            return [describe(item) for item in value]
        if isinstance(value, dict):
            return {str(key): describe(item) for key, item in value.items()}
        return value if value is None or isinstance(value, (str, int, float, bool)) else str(value)

    class AllocationTrace(TorchDispatchMode):
        def __torch_dispatch__(self, func, types, args=(), kwargs=None):
            before = torch.cuda.memory_allocated()
            try:
                result = func(*args, **(kwargs or {}))
            except torch.cuda.OutOfMemoryError as error:
                events.append({"operator": str(func), "inputs": describe(args), "kwargs": describe(kwargs), "oom": str(error)})
                raise
            delta = torch.cuda.memory_allocated() - before
            if delta >= threshold:
                events.append({"operator": str(func), "inputs": describe(args), "kwargs": describe(kwargs),
                               "outputs": describe(result), "allocated_delta_bytes": delta})
            return result

    return AllocationTrace()


def _compare(torch, actual, expected, tolerance):
    if actual.shape != expected.shape:
        raise ValueError(f"Parity shape mismatch: {tuple(actual.shape)} vs {tuple(expected.shape)}")
    difference = actual.float().sub(expected.float()).abs()
    allowed = expected.float().abs().mul(tolerance["rtol"]).add(tolerance["atol"])
    nonfinite = (~torch.isfinite(actual) | ~torch.isfinite(expected)).sum().item()
    max_error, sum_error = difference.max().item(), difference.sum(dtype=torch.float64).item()
    return {
        "elements": actual.numel(), "mismatches": (difference > allowed).sum().item(),
        "nonfinite": nonfinite, "max_abs_error": max_error if math.isfinite(max_error) else None,
        "sum_abs_error": sum_error if math.isfinite(sum_error) else None,
    }


def _gradient_checks(torch, gradient, reference, rows, chunk_rows):
    flat = gradient.squeeze(0)
    expected = reference.squeeze(0) if reference is not None else None
    report = {"elements": flat.numel(), "nonfinite": 0, "max_abs": 0.0, "squared_norm": 0.0, "unscored_nonzero": 0}
    parity = {"elements": 0, "mismatches": 0, "nonfinite": 0, "max_abs_error": 0.0, "sum_abs_error": 0.0} if expected is not None else None
    unscored, previous_end = [], 0
    for start, end in rows:
        unscored.append((previous_end, start))
        previous_end = end
    unscored.append((previous_end, flat.size(0)))
    with torch.no_grad():
        for start in range(0, flat.size(0), chunk_rows):
            part = flat[start:start + chunk_rows].float()
            report["nonfinite"] += (~torch.isfinite(part)).sum().item()
            report["max_abs"] = max(report["max_abs"], part.abs().max().item())
            report["squared_norm"] += part.square().sum(dtype=torch.float64).item()
            if expected is not None:
                checked = _compare(torch, part, expected[start:start + chunk_rows], _GRAD_TOL)
                for key in ("elements", "mismatches", "nonfinite"):
                    parity[key] += checked[key]
                for key in ("max_abs_error", "sum_abs_error"):
                    if parity[key] is None or checked[key] is None:
                        parity[key] = None
                    elif key == "max_abs_error":
                        parity[key] = max(parity[key], checked[key])
                    else:
                        parity[key] += checked[key]
            del part
        for begin, end in unscored:
            for start in range(begin, end, chunk_rows):
                report["unscored_nonzero"] += flat[start:min(start + chunk_rows, end)].count_nonzero().item()
    report["unscored_row_ranges"] = unscored
    report["prefix_gradient_definition"] = "Unscored prefix logits rows are zero; the last prefix row predicts the first response token and is scored. Terminal/padding rows must also be zero."
    report["prefix_gradient_zero"] = report["unscored_nonzero"] == 0
    report["finite"] = report["nonfinite"] == 0
    # Nonfinite values must remain JSON serializable and can never pass a gate.
    for key in ("max_abs", "squared_norm"):
        if not math.isfinite(report[key]):
            report[key] = None
    if parity is not None:
        for key in ("max_abs_error", "sum_abs_error"):
            if parity[key] is not None and not math.isfinite(parity[key]):
                parity[key] = None
        parity["passed"] = parity["nonfinite"] == 0 and parity["mismatches"] == 0
    report["full_gradient_parity"] = parity
    return report


def _run_backend(torch, cli, native_args, batch, shape, rank, backend, reference, reference_lp, rows):
    from tests.fast.backends.training_utils.loss.loss_test_utils import make_args

    from miles.backends.training_utils.loss.hub.logit_processors import get_log_probs_and_entropy

    retained_bytes = reference.numel() * reference.element_size() if reference is not None else 0
    report = {"backend": backend, "status": "in-progress", "retained_reference_gradient_bytes": retained_bytes,
              "memory": {}, "large_allocation_operators": []}
    logits = outputs = log_probs = loss = gradient = None
    detached_lp = None
    args = make_args(
        true_on_policy_mode=native_args.true_on_policy_mode, log_probs_backend=backend,
        qkv_format=native_args.qkv_format, allgather_cp=native_args.allgather_cp,
        rollout_temperature=native_args.rollout_temperature, loss_type=native_args.loss_type,
        log_probs_chunk_size=native_args.log_probs_chunk_size, recompute_loss_function=native_args.recompute_loss_function,
        vocab_size=native_args.vocab_size, bf16=True,
    )
    phase = "input"
    try:
        torch.cuda.reset_peak_memory_stats()
        report["memory"]["before_input"] = _memory(torch)
        logits = torch.empty(shape, device="cuda", dtype=torch.bfloat16)
        logits.normal_(generator=torch.Generator(device="cuda").manual_seed(native_args.seed + rank))
        logits.requires_grad_(True)
        report["input_storage_bytes"] = logits.untyped_storage().nbytes()
        report["memory"]["after_input"] = _memory(torch)
        threshold = batch["response_lengths"][0] * shape[-1] * logits.element_size()
        trace = _allocation_trace(torch, report["large_allocation_operators"], threshold) if cli.trace_allocations else contextlib.nullcontext()
        report["allocation_trace"] = {"enabled": cli.trace_allocations, "threshold_bytes": threshold,
                                      "coverage": "Eager ATen allocation deltas/inputs; not Triton/NCCL internals; no tensor references retained"}
        with trace:
            for phase in ("forward", "backward"):
                torch.cuda.reset_peak_memory_stats()
                report["memory"]["before_" + phase] = _memory(torch)
                if phase == "forward":
                    outputs = get_log_probs_and_entropy(
                        logits, args=args, unconcat_tokens=batch["unconcat_tokens"], total_lengths=batch["total_lengths"],
                        response_lengths=batch["response_lengths"], with_entropy=False,
                    )
                    log_probs = outputs["log_probs"][0]
                    loss = -(log_probs * batch["loss_masks"][0]).sum()
                else:
                    gradient, = torch.autograd.grad(loss, logits)
                report["memory"]["after_" + phase] = _memory(torch)
        report["leaf_grad_allocated"] = logits.grad is not None
        report["gradient_aliases_logits"] = gradient.untyped_storage().data_ptr() == logits.untyped_storage().data_ptr()
        report["gradient_shape"] = list(gradient.shape)
        report["gradient_dtype"] = str(gradient.dtype)
        report["gradient_matches_input_geometry"] = tuple(gradient.shape) == shape and gradient.dtype == logits.dtype
        report["loss"] = loss.item() if torch.isfinite(loss).item() else None
        detached_lp = log_probs.detach().cpu()
        report["logprobs_finite"] = torch.isfinite(detached_lp).all().item()
        report["response_logprob_count"] = detached_lp.numel()
        report["logprob_parity"] = _compare(torch, detached_lp, reference_lp, _LOGPROB_TOL) if reference_lp is not None else None
        torch.cuda.reset_peak_memory_stats()
        report["gradient_checks"] = _gradient_checks(torch, gradient, reference, rows, cli.gradient_chunk_rows)
        report["memory"]["after_validation"] = _memory(torch)
        report["status"] = "completed"
    except torch.cuda.OutOfMemoryError as error:
        report.update(status="OOM", failed_phase=phase, error=str(error))
        report["memory"]["at_oom"] = _memory(torch)
        gradient = detached_lp = None
    finally:
        logits = outputs = log_probs = loss = None
    measurements = [value["peak_allocated_bytes"] for key, value in report["memory"].items() if key != "after_validation"]
    report["peak_allocated_bytes"] = max(measurements)
    report["peak_allocated_excluding_retained_reference_bytes"] = max(measurements) - retained_bytes
    report["measurement"] = "Synthetic BF16 model-output leaf -> native logprob seam -> autograd.grad; validation excluded from backend peak"
    return report, gradient.detach() if gradient is not None else None, detached_lp


def _passed(report):
    if report["status"] != "completed":
        return False
    checks = report["gradient_checks"]
    return (report["loss"] is not None and report["logprobs_finite"] and checks["finite"]
            and checks["prefix_gradient_zero"] and report["gradient_matches_input_geometry"] and not report["leaf_grad_allocated"]
            and (report["backend"] != "fused" or report["gradient_aliases_logits"]))


def main():
    cli = _cli()
    import torch
    import torch.distributed as dist
    from tests.fast.backends.training_utils.loss.loss_test_utils import make_parallel_state

    from miles.backends.training_utils.parallel import GroupInfo, set_parallel_state

    receipt = json.loads(cli.launch_receipt.read_text())
    native_args, provenance = _launch_args(cli, receipt)
    report = {"task_id": "QWEN-P3-LOSS-MEMORY-PROBE", "python": platform.python_version(), "executable": sys.executable,
              "torch": torch.__version__, "cuda_build": torch.version.cuda, "argv": sys.argv,
              "rollout_data": str(cli.rollout_data), "launch_receipt": str(cli.launch_receipt),
              "launch_source_commit": receipt["source_commit"], "resolved_args": vars(native_args),
              "native_default_provenance": provenance, "padded_vocab_size": cli.padded_vocab_size,
              "tolerances": {"logprob": _LOGPROB_TOL, "gradient": _GRAD_TOL, "source": _TOLERANCE_SOURCE},
              "scope": __doc__, "backends": []}
    if cli.geometry_only:
        from unittest.mock import patch

        from miles.platforms import current_platform

        set_parallel_state(dataclasses.replace(make_parallel_state(), tp=GroupInfo(rank=0, size=2, group=None)))
        with patch.object(current_platform, "current_device", return_value=torch.device("cpu")):
            _, identity = _pack(cli, native_args, device="cpu")
        report.update(sample=identity, shape=[1, identity["padded_tokens"], cli.padded_vocab_size // 2],
                      dtype="torch.bfloat16", status="GEOMETRY_ONLY", numerical_status="INCOMPLETE")
        _write(cli.report, report)
        return 0
    if int(os.environ["WORLD_SIZE"]) != 2:
        raise RuntimeError("Run with two torchrun ranks in the pinned image")
    rank = int(os.environ["RANK"])
    torch.cuda.set_device(int(os.environ["LOCAL_RANK"]))
    properties = torch.cuda.get_device_properties(torch.cuda.current_device())
    if properties.name != "NVIDIA H800":
        raise RuntimeError(f"This diagnostic requires H800, found {properties.name}")
    report.update(rank=rank, gpu=properties.name, gpu_total_bytes=properties.total_memory,
                   allocator_config=os.environ.get("PYTORCH_ALLOC_CONF", os.environ.get("PYTORCH_CUDA_ALLOC_CONF")),
                   allocator_backend=torch.cuda.memory.get_allocator_backend(), ld_preload=os.environ.get("LD_PRELOAD"),
                   logits_seed=native_args.seed + rank, gradient_chunk_rows=cli.gradient_chunk_rows)
    rank_path = cli.report.with_name(f"{cli.report.stem}.rank{rank}{cli.report.suffix}")
    parallel_state = make_parallel_state()
    dist.init_process_group(backend="nccl")
    try:
        set_parallel_state(dataclasses.replace(parallel_state, tp=GroupInfo(rank=rank, size=2, group=dist.group.WORLD)))
        # Initialize the communicator before either backend's memory baseline.
        status = torch.zeros((), device="cuda", dtype=torch.int)
        dist.all_reduce(status)
        batch, identity = _pack(cli, native_args, device="cuda")
        shape = (1, identity["padded_tokens"], cli.padded_vocab_size // 2)
        report.update(sample=identity, shape=shape, dtype="torch.bfloat16", numerical_status="INCOMPLETE")
        _write(rank_path, report)
        reference = reference_lp = None
        for backend in ("torch", "fused"):
            measured, gradient, lp = _run_backend(
                torch, cli, native_args, batch, shape, rank, backend, reference, reference_lp, identity["response_row_ranges"],
            )
            report["backends"].append(measured)
            status.fill_(int(not _passed(measured)))
            dist.all_reduce(status, op=dist.ReduceOp.MAX)
            if backend == "torch" and status.item() == 0:
                reference, reference_lp = gradient, lp
            elif backend == "fused" and status.item() == 0 and reference is not None:
                parity = measured["logprob_parity"]
                report["numerical_status"] = "PASS" if parity["nonfinite"] == 0 and parity["mismatches"] == 0 and measured["gradient_checks"]["full_gradient_parity"]["passed"] else "FAIL"
            elif backend == "fused" and measured["status"] != "completed":
                report["numerical_status"] = "FAIL"
            gradient = lp = None
            if backend == "fused":
                reference = reference_lp = None
            gc.collect()
            torch.cuda.empty_cache()
            measured["memory"]["after_release_and_empty_cache"] = _memory(torch)
            _write(rank_path, report)
        local_failed = any(not _passed(item) and item["status"] != "OOM" for item in report["backends"])
        torch_peak, fused_peak = [item["peak_allocated_excluding_retained_reference_bytes"] for item in report["backends"]]
        report["memory_comparison"] = {
            "torch_peak_allocated_excluding_reference_bytes": torch_peak,
            "fused_peak_allocated_excluding_reference_bytes": fused_peak,
            "reduction_bytes": torch_peak - fused_peak,
            "reduction_fraction": (torch_peak - fused_peak) / torch_peak,
            "both_backends_completed": all(item["status"] == "completed" for item in report["backends"]),
            "caveat": "Subtracts only live BF16 reference-gradient bytes from allocated peaks; raw reserved/fragmentation remain recorded. An OOM peak is not a completed torch requirement.",
        }
        # Failure dominates missing reference, which dominates PASS, on either rank.
        severity = 2 if local_failed or report["numerical_status"] == "FAIL" else (0 if report["numerical_status"] == "PASS" else 1)
        status.fill_(severity)
        dist.all_reduce(status, op=dist.ReduceOp.MAX)
        severity = status.item()
        exit_code = {0: 0, 1: 2, 2: 1}[severity]
        report["numerical_status"] = {0: "PASS", 1: "INCOMPLETE", 2: "FAIL"}[severity]
        _write(rank_path, report)
        reports = [None, None]
        dist.all_gather_object(reports, report)
        if rank == 0:
            _write(cli.report, {"task_id": report["task_id"], "numerical_status": report["numerical_status"], "ranks": reports})
            print("QWEN35_LOSS_MEMORY_PROBE", report["numerical_status"], str(cli.report), flush=True)
        return exit_code
    finally:
        dist.destroy_process_group()


if __name__ == "__main__":
    raise SystemExit(main())
