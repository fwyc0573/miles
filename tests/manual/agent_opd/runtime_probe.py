"""Inspect the pinned worker runtime and execute small kernels on requested GPUs."""

import argparse
import ctypes
import importlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path


def _cuda_checks(torch, count: int) -> dict:
    if not torch.cuda.is_available():
        raise RuntimeError(f"CUDA {torch.version.cuda} could not initialize on this worker")
    driver = ctypes.CDLL("libcuda.so.1")
    driver_version = ctypes.c_int()
    if driver.cuDriverGetVersion(ctypes.byref(driver_version)) != 0:
        raise RuntimeError("The CUDA driver API version query failed")
    kernels = []
    for index in range(count):
        device = f"cuda:{index}"
        values = torch.arange(32, device=device, dtype=torch.float32)
        squared_sum = values.square().sum().item()
        matrix = torch.ones((16, 16), device=device, dtype=torch.bfloat16)
        product = matrix @ matrix
        if squared_sum != sum(i * i for i in range(32)) or not (product == 16).all().item():
            raise ValueError(f"CUDA arithmetic differs from the expected result on GPU {index}")
        torch.cuda.synchronize(index)
        kernels.append({"gpu": index, "squared_sum": squared_sum, "bf16_matmul": "passed"})
    libraries = sorted(
        {
            line.split()[-1]
            for line in Path("/proc/self/maps").read_text().splitlines()
            if "libcuda.so" in line or "libnvidia-ptxjitcompiler.so" in line
        }
    )
    return {"driver_api_version": driver_version.value, "loaded_libraries": libraries, "kernels": kernels}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--require-gpus", type=int, default=0)
    args = parser.parse_args()
    versions = {}
    import torch

    if args.require_gpus and torch.cuda.device_count() != args.require_gpus:
        raise RuntimeError(f"Expected {args.require_gpus} GPUs, got {torch.cuda.device_count()}")
    cuda_checks = _cuda_checks(torch, args.require_gpus) if args.require_gpus else None
    modules = ["torch", "transformers", "ray", "sglang"]
    if args.require_gpus:
        modules.extend(("transformer_engine.pytorch", "megatron.core"))
    for module in modules:
        imported = importlib.import_module(module)
        versions[module] = {"version": getattr(imported, "__version__", None), "path": imported.__file__}
    from sglang.srt.parser.reasoning_parser import ReasoningParser
    from miles.rollout.generate_utils.tool_call_utils import create_tool_call_parser

    tool_parser = create_tool_call_parser(
        [{"type": "function", "function": {"name": "submit", "parameters": {"type": "object", "properties": {}}}}],
        "glm47",
    )
    repository = Path(__file__).resolve().parents[3]
    git = ["git", "-c", f"safe.directory={repository}", "-C", str(repository)]
    revision = subprocess.check_output([*git, "rev-parse", "HEAD"], text=True).strip()
    source_status = subprocess.check_output(
        [
            *git,
            "status",
            "--short",
            "--",
            "examples/agentic_opd",
            "scripts/run_glm47_flash_agent_opd.py",
            "tests/manual/agent_opd",
        ],
        text=True,
    ).splitlines()
    report = {
        "source_revision": revision,
        "source_status": source_status,
        "python": platform.python_version(),
        "executable": sys.executable,
        "versions": versions,
        "package_versions": {
            name: importlib.metadata.version(name)
            for name in ("torch", "transformers", "ray", "sglang", "polars", "safetensors")
        },
        "cuda_build": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
        "cuda_checks": cuda_checks,
        "node_environment": {
            key: os.environ.get(key)
            for key in (
                "RANK",
                "WORLD_SIZE",
                "MASTER_ADDR",
                "MASTER_PORT",
                "NODE_RANK",
                "NODE_COUNT",
                "PROC_PER_NODE",
                "RLAUNCH_REPLICA",
                "RLAUNCH_REPLICA_TOTAL",
                "RJOB_REPLICA_INDEX",
                "DISTRIBUTED_JOB",
                "PORT_AUTO0",
                "PORT_AUTO1",
                "KUBEBRAIN_REPLICA",
                "KUBEBRAIN_REPLICA_TOTAL",
                "KUBEBRAIN_REPLICA_NAME",
                "KUBEBRAIN_RJOB_NAME",
            )
        },
        "reasoning_probe": ReasoningParser(model_type="glm45", force_reasoning=False).parse_non_stream(
            "<think>reasoning</think>ordinary body"
        ),
        "tool_parser_class": type(tool_parser).__name__,
        "imports_passed": True,
        "gpu_module_imports_verified": bool(args.require_gpus),
        "gpu_devices": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print("AGENT_OPD_RUNTIME_PROBE", json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
