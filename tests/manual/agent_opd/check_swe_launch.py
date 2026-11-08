"""Validate real SWE/Megatron launch arguments and the native driver contract.

Run on a GPU in the pinned training image with its normal CUDA compatibility-library
path, original HF model mounts and source workspace. This calls the production
argument parsers and startup contract; it does not create actors or train.
"""

import argparse
import importlib.metadata
import json
import os
import shlex
import sys
import traceback
from pathlib import Path
from types import SimpleNamespace

from tests.manual.agent_opd.run_swe_opd import _config, _prepare_training
from tests.manual.agent_opd.run_qwen35_opd import _runtime_env

from miles.utils.args.custom_view import compute_custom_function_config
from miles.utils.args.runtime import OrchestratorConfig
from miles.utils.arguments import parse_args
from miles.utils.external_utils.command_utils.base_backend import ExecuteTrainConfig, ExecuteTrainRequest
from miles.utils.external_utils.command_utils.common import train_env_vars
from miles.utils.function_registry import load_function


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    options = parser.parse_args()
    original_argv = sys.argv
    rows = []
    for pair in ("A", "B"):
        for protocol in ("full", "r256"):
            row = {"pair": pair, "protocol": protocol, "status": "failed"}
            try:
                config = _config(options.config, pair, protocol)
                allocation = config["pairs"][pair]
                args = SimpleNamespace(
                    pair=pair, student=Path(allocation["student"]["path"]),
                    teacher=Path(allocation["teacher"]["path"]), teacher_url="http://teacher:30000/generate",
                    megatron_path=config["megatron_path"], swe_config=config,
                )
                run = Path(config["run_root"]) / "configuration-check" / pair / os.environ["KUBEBRAIN_RJOB_NAME"]
                training, receipt = _prepare_training(args, run)
                execution = ExecuteTrainConfig(num_nodes=1, output_dir=str(run), run_id=os.environ["KUBEBRAIN_RJOB_NAME"])
                request = ExecuteTrainRequest(
                    train_args=training, num_gpus_per_node=allocation["student"]["gpus_per_node"],
                    megatron_model_type=receipt["megatron_model_type"], train_script="train.py", train_backend_fsdp=False,
                    extra_env_vars=_runtime_env(execution), megatron_path=config["megatron_path"],
                    before_ray_job_submit=None, prepare_cmd={}, extra_manifests=[],
                )
                os.environ.update(train_env_vars(request, {}, config=execution))
                row["cuda_device_max_connections"] = os.environ["CUDA_DEVICE_MAX_CONNECTIONS"]
                row["argv"] = [*receipt["model_argv"], *shlex.split(training)]
                sys.argv = ["train.py", *row["argv"]]
                parsed = OrchestratorConfig.slice_from(parse_args())
                hook = parsed.custom_megatron_optimizer_step_hook_path
                merged = compute_custom_function_config(parsed, hook)
                driver = load_function(hook).training_protocol(merged)
                row.update(
                    status="passed", successful_update_budget=driver.budget,
                    run_kind=merged.swe_run_kind, bank_slots=merged.swe_bank_slots,
                    bank_uses=merged.swe_bank_uses, context_tokens=merged.swe_context_tokens,
                    partial_step=merged.allow_partial_train_step,
                    dynamic_global_batch=merged.use_dynamic_global_batch_size,
                )
            except (Exception, SystemExit) as error:
                row.update(error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc())
            finally:
                sys.argv = original_argv
            rows.append(row)
    result = {
        "status": "passed" if all(row["status"] == "passed" for row in rows) else "failed",
        "versions": {"python": sys.version, **{name: importlib.metadata.version(name) for name in ("torch", "transformers", "sglang")}},
        "cases": rows,
    }
    options.report.parent.mkdir(parents=True, exist_ok=True)
    with options.report.open("x") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    print("SWE_LAUNCH_CONFIG", result["status"], str(options.report), flush=True)
    return int(result["status"] != "passed")


if __name__ == "__main__":
    raise SystemExit(main())
