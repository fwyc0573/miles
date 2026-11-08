"""Run one full Qwen3.5 pair with colocated student training/rollout on qualified GPUs.

The frozen teacher must already serve a separate allocation's native /generate
endpoint. Prepare the population once with prepare_qwen35 and reuse that directory
for A (4B -> 27B), B (4B -> 35B-A3B), and C (27B -> 397B-A17B).
The parent launcher owns model identity, image and GPU resource qualification.
This worker reuses rjob_warmup's Ray lifecycle and native command_utils submission.

Args:
    --pair / --student / --teacher / --teacher-url: Full pair identities and assets.
    --population-dir: Frozen train.jsonl, monitor.jsonl and passed population.json.
    --output-root / --shared-dir: Personal cloud artifacts and mounted local records.
    --gpu-type / --gpus-per-node / --student-engine-gpus: Explicit student allocation.
    --max-tokens-per-gpu: Required dynamic microbatch token budget; no H200 default.
    --sglang-mem-fraction-static / --sglang-max-running-requests /
    --sglang-chunked-prefill-size / --sglang-router-request-timeout-secs:
        Required capacity/request settings, supplied after resource qualification.
    --num-rollout: 100 by default; 0 runs native baseline evaluation without updates
        or HF export. Rollout schedule positions are not successful-update counts.
    --dry-run: Print native model/training argv without GPU, asset reads or submission.

Example (shell variables denote parent-qualified inputs, not capacity defaults):
    python -B -m tests.manual.agent_opd.run_qwen35_opd --pair A \
        --student "$STUDENT" --teacher "$TEACHER" --teacher-url "$TEACHER_URL" \
        --population-dir "$POPULATION" --output-root "$OUTPUT" --shared-dir "$RECORDS" \
        --gpu-type "$GPU_TYPE" --gpus-per-node "$GPUS" --student-engine-gpus "$ENGINE_GPUS" \
        --max-tokens-per-gpu "$TOKEN_BUDGET" --sglang-mem-fraction-static "$MEM_FRACTION" \
        --sglang-max-running-requests "$REQUESTS" --sglang-chunked-prefill-size "$CHUNK" \
        --sglang-router-request-timeout-secs "$REQUEST_TIMEOUT"
"""

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from threading import Event, Thread
from types import SimpleNamespace
from urllib.parse import urlsplit

from scripts.run_glm47_flash_agent_opd import _training_env
from scripts.run_qwen3_dense import ScriptArgs as DenseArgs
from tests.manual.agent_opd.prepare_qwen35 import CONTEXT_TOKENS, MONITOR_PER_STRATUM, RESPONSE_TOKENS, SEED
from tests.manual.agent_opd.rjob_warmup import (
    _check_cluster,
    _check_tokenizers,
    _memory_receipt,
    _record_memory,
    _retain_failure_diagnostics,
    _start_ray,
    _worker_environment,
    _write_json,
)

from miles.utils.external_utils import command_utils as U
from miles.utils.external_utils.model_args_utils import shell_safe_model_args

_PAIRS = {
    "A": ("Qwen3.5-4B", "Qwen3.5-27B"),
    "B": ("Qwen3.5-4B", "Qwen3.5-35B-A3B"),
    "C": ("Qwen3.5-27B", "Qwen3.5-397B-A17B"),
}
_PERSONAL_ROOT = Path("/mnt/codesign-exp/ycfeng")
_READ_ONLY_MODELS = {
    Path("/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-27B/model"),
    Path("/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-35B-A3B/model"),
    Path("/mnt/codesign-exp/pj_dflash_edge_i-pengyajuan/models/Qwen3.5-397B-A17B"),
}
_PLANNED_ROLLOUTS = 100
_BATCH_SIZE = 8
_EVAL_INTERVAL = 20


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair", choices=tuple(_PAIRS), required=True)
    for name in ("student", "teacher", "population-dir", "output-root", "shared-dir"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--teacher-url", required=True, help="Full native teacher /generate URL")
    parser.add_argument("--gpu-type", required=True, help="Expected GPU model from the parent allocation")
    parser.add_argument("--gpus-per-node", type=int, required=True)
    parser.add_argument("--student-engine-gpus", type=int, required=True)
    parser.add_argument("--tensor-model-parallel-size", type=int, help="Defaults to the dense student recipe's TP")
    parser.add_argument("--max-tokens-per-gpu", type=int, required=True)
    parser.add_argument("--sglang-mem-fraction-static", type=float, required=True)
    parser.add_argument("--sglang-max-running-requests", type=int, required=True)
    parser.add_argument("--sglang-chunked-prefill-size", type=int, required=True)
    parser.add_argument("--sglang-router-request-timeout-secs", type=int, required=True)
    parser.add_argument("--num-rollout", type=int, choices=(0, _PLANNED_ROLLOUTS), default=_PLANNED_ROLLOUTS)
    parser.add_argument("--local-root", type=Path, default=Path("/var/tmp"))
    parser.add_argument("--megatron-path", default="/root/Megatron-LM")
    parser.add_argument("--startup-timeout", type=int, default=600)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def _validate_args(args) -> None:
    for name in ("student", "teacher", "population_dir", "output_root", "shared_dir", "local_root"):
        path = getattr(args, name).resolve()
        setattr(args, name, path)
        if name in ("student", "teacher"):
            if not path.is_relative_to(_PERSONAL_ROOT) and path not in _READ_ONLY_MODELS:
                raise ValueError(f"{name} must be personal or an exactly approved read-only model path")
        elif name in ("population_dir", "output_root"):
            if not path.is_relative_to(_PERSONAL_ROOT):
                raise ValueError(f"{name} must stay under {_PERSONAL_ROOT}")
        elif path.is_relative_to("/mnt"):
            raise ValueError(f"{name} must be a mounted local workspace or worker-local directory, not a cloud path")
    if args.student == args.teacher:
        raise ValueError("OPD requires distinct full student and teacher assets")
    endpoint = urlsplit(args.teacher_url)
    if endpoint.scheme not in ("http", "https") or not endpoint.netloc or endpoint.path != "/generate":
        raise ValueError("--teacher-url must be a full HTTP(S) native /generate endpoint")
    if endpoint.username or endpoint.password or endpoint.query or endpoint.fragment:
        raise ValueError("Teacher endpoint must not carry credentials, query parameters or a fragment")
    recipe = DenseArgs(model_name=_PAIRS[args.pair][0]).recipe
    if args.tensor_model_parallel_size is None:
        args.tensor_model_parallel_size = recipe.tensor_model_parallel_size
    for name in (
        "gpus_per_node", "student_engine_gpus", "tensor_model_parallel_size", "max_tokens_per_gpu",
        "sglang_max_running_requests", "sglang_chunked_prefill_size", "sglang_router_request_timeout_secs",
        "startup_timeout",
    ):
        if getattr(args, name) <= 0:
            raise ValueError(f"{name} must be positive")
    if args.gpus_per_node % args.tensor_model_parallel_size or args.gpus_per_node % args.student_engine_gpus:
        raise ValueError("The node GPU count must divide into complete trainer TP ranks and student engines")
    dp = args.gpus_per_node // args.tensor_model_parallel_size
    if _BATCH_SIZE % dp:
        raise ValueError("Eight fresh completions must divide equally across the trainer DP ranks")
    if not 0 < args.sglang_mem_fraction_static < 1:
        raise ValueError("--sglang-mem-fraction-static must be in (0, 1)")


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _check_population(args) -> dict:
    path = args.population_dir / "population.json"
    if path.resolve() != path:
        raise ValueError("The frozen population report must remain in its personal directory")
    report = json.loads(path.read_text())
    if report["status"] != "passed":
        raise ValueError("The frozen Qwen population must have status=passed before launching")
    if report["limits"]["context_tokens"] != CONTEXT_TOKENS or report["limits"]["response_tokens"] != RESPONSE_TOKENS:
        raise ValueError("Frozen population length limits differ from the accepted workload")
    if report["chat_template"]["kwargs"]["enable_thinking"] is not True or report["selection_seed"] != SEED:
        raise ValueError("Frozen population thinking mode or selection seed differs from the accepted workload")
    if report["split"]["monitoring_stratum_counts"] != {name: MONITOR_PER_STRATUM for name in ("short", "medium", "long")}:
        raise ValueError("The frozen monitoring population lacks the required length coverage")
    if any(report["split"]["checks"].values()):
        raise ValueError("The frozen population reports training/monitoring/evaluation overlap")
    for name, expected_rows in (("train", None), ("monitor", 3 * MONITOR_PER_STRATUM)):
        dataset = report["datasets"][name]
        actual = args.population_dir / f"{name}.jsonl"
        if actual.resolve() != actual or not actual.is_relative_to(_PERSONAL_ROOT):
            raise ValueError("Frozen datasets must remain files in the personal population directory")
        if _sha256(actual) != dataset["sha256"]:
            raise ValueError(f"The frozen {name} dataset bytes changed")
        if dataset["rows"] <= 0 or (expected_rows is not None and dataset["rows"] != expected_rows):
            raise ValueError(f"The frozen {name} dataset has an invalid row count")
    for name, digest in report["qwen_tokenizer"]["assets"].items():
        if Path(name).name != name or _sha256(args.student / name) != digest:
            raise ValueError(f"The student tokenizer differs from the frozen Qwen population: {name}")
    return {"path": str(path), "sha256": _sha256(path), "datasets": report["datasets"], "chat_template": report["chat_template"]}


def _training_args(args, run: Path) -> str:
    recipe = DenseArgs(model_name=_PAIRS[args.pair][0]).recipe
    checkpoint = shlex.join([
        "--hf-checkpoint", str(args.student), "--ref-load", str(args.student), "--megatron-to-hf-mode", "raw",
    ])
    if args.num_rollout:
        checkpoint += " " + shlex.join([
            "--save-hf", str(run / "hf" / "step_{rollout_id}"), "--save-interval", str(_PLANNED_ROLLOUTS),
            "--custom-megatron-post-save-hook-path", "tests.manual.agent_opd.qwen_export.post_save",
        ])
    rollout = shlex.join([
        "--prompt-data", str(args.population_dir / "train.jsonl"), "--input-key", "prompt", "--metadata-key", "metadata",
        "--custom-generate-function-path", "tests.manual.agent_opd.qwen_alignment.generate",
        "--custom-rm-path", "tests.manual.agent_opd.qwen_alignment.score_teacher", "--rm-url", args.teacher_url,
        "--reward-key", "reward", "--custom-reward-post-process-path", "examples.agentic_opd.rollout.post_process_rewards",
        "--num-rollout", str(args.num_rollout), "--rollout-batch-size", str(_BATCH_SIZE), "--n-samples-per-prompt", "1",
        "--global-batch-size", str(_BATCH_SIZE), "--rollout-shuffle", "--rollout-seed", str(SEED), "--seed", str(SEED),
        "--rollout-max-response-len", str(RESPONSE_TOKENS), "--rollout-max-context-len", str(CONTEXT_TOKENS),
        "--rollout-temperature", "1", "--rollout-top-p", "1", "--rollout-top-k", "-1", "--balance-data",
    ])
    evaluation = shlex.join([
        "--eval-interval", str(_EVAL_INTERVAL), "--eval-prompt-data", "monitor", str(args.population_dir / "monitor.jsonl"),
        "--n-samples-per-eval-prompt", "1", "--eval-temperature", "1", "--eval-top-p", "1", "--eval-top-k", "-1",
        "--eval-max-response-len", str(RESPONSE_TOKENS), "--eval-max-context-len", str(CONTEXT_TOKENS),
        "--eval-train-log-probs",
    ])
    parallel = (
        f"--tensor-model-parallel-size {args.tensor_model_parallel_size} --sequence-parallel "
        "--pipeline-model-parallel-size 1 --context-parallel-size 1 --expert-model-parallel-size 1 "
        "--expert-tensor-parallel-size 1 --recompute-granularity full --recompute-method uniform --recompute-num-layers 1 "
        f"--use-dynamic-batch-size --max-tokens-per-gpu {args.max_tokens_per_gpu} --seq-length {CONTEXT_TOKENS} "
        "--linear-attention-backend fla --linear-attention-input-norm te --log-probs-backend fused"
    )
    # MisConfig owns the false defaults for use_rs and tis_batch_normalize.
    # Its native parser only exposes enabling flags; neither is passed here.
    algorithm = (
        "--use-opd --opd-type sglang --opd-log-prob-top-k 0 --opd-kl-coef 1 --advantage-estimator grpo "
        "--calculate-per-token-loss --get-mismatch-metrics --use-tis "
        "--custom-tis-function-path examples.infra_features.train_infer_mismatch_helper.mis.compute_mis_weights_with_cp "
        "--tis-level token --tis-mode mask --tis-lower-bound 0.5 --tis-upper-bound 2 "
        "--eps-clip 0.2 --eps-clip-high 0.28 --entropy-coef 0"
    )
    optimizer = (
        "--optimizer adam --lr 2e-6 --lr-decay-style constant --lr-warmup-iters 0 --weight-decay 0 "
        "--adam-beta1 0.9 --adam-beta2 0.98"
    )
    if args.num_rollout == 0:
        # Native evaluation scores the model without constructing a zero-step LR scheduler.
        optimizer += " --debug-disable-optimizer"
    if recipe.optimizer_cpu_offload:
        optimizer += " --optimizer-cpu-offload --overlap-cpu-optimizer-d2h-h2d --use-precision-aware-optimizer"
    sglang = (
        f"--rollout-num-gpus-per-engine {args.student_engine_gpus} --sglang-context-length {CONTEXT_TOKENS} "
        f"--sglang-mem-fraction-static {args.sglang_mem_fraction_static} "
        f"--sglang-max-running-requests {args.sglang_max_running_requests} "
        f"--sglang-chunked-prefill-size {args.sglang_chunked_prefill_size} "
        f"--sglang-router-request-timeout-secs {args.sglang_router_request_timeout_secs} "
        "--sglang-disable-cuda-graph --sglang-enable-deterministic-inference --sglang-attention-backend fa3 "
        "--sglang-enable-prefill-weight-versions "
        "--sglang-linear-attn-prefill-backend triton --sglang-dtype bfloat16"
    )
    verification = shlex.join([
        "--dump-details", str(run), "--save-debug-rollout-data", str(run / "rollout_data" / "{rollout_id}.pt"),
        "--save-debug-train-data", str(run / "train_data" / "{rollout_id}_{rank}.pt"),
        "--save-debug-event-data", str(run / "events"), "--check-weight-update-equal",
        "--check-weight-update-skip-list", "visual", "--log-inference-engine-weight-checksums",
        "--colocate", "--offload-train", "--offload-rollout", "--actor-num-nodes", "1",
        "--actor-num-gpus-per-node", str(args.gpus_per_node), "--num-gpus-per-node", str(args.gpus_per_node),
        "--attention-dropout", "0", "--hidden-dropout", "0", "--accumulate-allreduce-grads-in-fp32",
        "--attention-softmax-in-fp32", "--attention-backend", "flash",
    ])
    return " ".join((checkpoint, rollout, evaluation, parallel, algorithm, optimizer, sglang, verification))


def _runtime_env(config) -> dict[str, str]:
    # All inherited platform NCCL values survive unchanged. The existing
    # deterministic-channel validator rejects conflicts rather than overwriting.
    inherited = {
        key: value for key, value in os.environ.items()
        if key.startswith("NCCL_") or key in {
            "TMPDIR", "TORCH_EXTENSIONS_DIR", "TORCHINDUCTOR_CACHE_DIR", "TRITON_CACHE_DIR",
            "FLASHINFER_WORKSPACE_BASE", "XDG_CACHE_HOME", "CUDA_CACHE_PATH", "RAY_TMPDIR",
            "PYTHONDONTWRITEBYTECODE", "HF_HUB_OFFLINE", "TOKENIZERS_PARALLELISM", "MILES_NODE_EXTERNAL_IP",
            "LD_LIBRARY_PATH",
        }
    }
    return {**inherited, **_training_env(config), "no_proxy": "*", "NO_PROXY": "*"}


def _launch_receipt(args, run: Path, training_args: str) -> dict:
    recipe = DenseArgs(model_name=_PAIRS[args.pair][0]).recipe
    git = ["git", "-c", f"safe.directory={U.repo_base_dir}", "-C", str(U.repo_base_dir)]
    return {
        "pair": args.pair, "student_model": _PAIRS[args.pair][0], "teacher_model": _PAIRS[args.pair][1],
        "student": str(args.student), "teacher": str(args.teacher), "teacher_url": args.teacher_url,
        "teacher_allocation": "external frozen SGLang; no teacher GPUs in the student Ray allocation",
        "population_dir": str(args.population_dir), "output_dir": str(run), "shared_dir": str(args.shared_dir),
        "training_argv": shlex.split(training_args), "model_argv": shlex.split(shell_safe_model_args(recipe.megatron_model_type)),
        "megatron_model_type": recipe.megatron_model_type, "megatron_path": args.megatron_path,
        "source_commit": subprocess.check_output([*git, "rev-parse", "HEAD"], text=True).strip(),
        "source_changes": subprocess.check_output([*git, "status", "--short"], text=True).splitlines(),
        "python": sys.version.split()[0], "planned_rollout_positions": args.num_rollout,
        "final_hf": str(run / "hf" / f"step_{args.num_rollout - 1}") if args.num_rollout else None,
        "update_accounting": "Use native optimizer outcomes and consumed/published versions in events; never infer success from rollout count",
        "native_resolved_config_and_events": str(run / "events"),
        "dynamic_microbatches": "Native length-based scheduling uses the supplied max_tokens_per_gpu; micro_batch_size is ignored",
        "student_routing_replay": "N/A: dense student has no MoE routing decisions",
        "weight_transfer": "Native colocation CUDA IPC; original NCCL-direct qualification remains deferred",
        "gpu_capacity_verified": False,
    }


def _gpu_devices(gpu_type: str, count: int) -> list[str]:
    rows = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], text=True
    ).splitlines()
    if len(rows) != count or any(gpu_type not in row.split(",")[0] for row in rows):
        raise ValueError(f"Allocation does not match the requested {gpu_type} GPU count: {rows}")
    return rows


def _record_receipt(path: Path, value: dict) -> None:
    try:
        _write_json(path, value)
    except (OSError, ValueError) as error:
        print("QWEN35_RECEIPT_UNVERIFIED", str(path), type(error).__name__, str(error), flush=True)


def _prepare_training(args, run: Path) -> tuple[str, dict]:
    population = _check_population(args)
    train_args = _training_args(args, run)
    receipt = _launch_receipt(args, run, train_args)
    receipt["population"] = population
    return train_args, receipt


def _run(args, *, prepare_training=_prepare_training) -> None:
    if int(os.environ["KUBEBRAIN_REPLICA_TOTAL"]) != 1:
        raise ValueError("This Qwen worker supports one student node; the teacher must be separately allocated")
    job = os.environ["KUBEBRAIN_RJOB_NAME"]
    cloud = args.output_root / args.pair / job
    cloud.mkdir(parents=True, exist_ok=False)
    records = args.shared_dir / args.pair / job
    records.mkdir(parents=True, exist_ok=False)
    local = args.local_root / f"qo-{job.removeprefix('exp-')}"
    _worker_environment(local)
    stopped = Event()
    observer = Thread(target=_record_memory, args=(local / "memory.jsonl", stopped), daemon=True)
    observer.start()
    outcome = {"status": "failed", "pair": args.pair, "run_dir": str(cloud)}
    try:
        train_args, receipt = prepare_training(args, cloud)
        _check_tokenizers(args.student, args.teacher)
        gpu_rows = _gpu_devices(args.gpu_type, args.gpus_per_node)
        config = U.ExecuteTrainConfig(num_nodes=1, output_dir=str(cloud), run_id=job)
        env = _runtime_env(config)
        receipt.update(gpu_devices=gpu_rows, runtime_env=env)
        _record_receipt(records / "launch.json", receipt)
        ray_args = SimpleNamespace(nodes=1, gpus_per_node=args.gpus_per_node, startup_timeout=args.startup_timeout)
        head = _start_ray(0, records, local, ray_args)
        _check_cluster(head, records, ray_args)
        os.environ["MILES_SCRIPT_EXTERNAL_RAY"] = "1"
        os.environ["MASTER_ADDR"] = head["ip"]
        os.environ["RAY_ADDRESS"] = f"http://{head['ip']}:{head['dashboard_port']}"
        config.create_backend().execute_train(
            train_args=train_args, num_gpus_per_node=args.gpus_per_node,
            megatron_model_type=receipt["megatron_model_type"], megatron_path=args.megatron_path,
            extra_env_vars=env,
        )
        outcome.update(
            status="native_execution_succeeded", actual_updates="See native events; not inferred from schedule",
            final_hf=receipt["final_hf"],
            qualification="Unverified until native alignment, updates, export and reload evidence is inspected",
        )
        print("QWEN35_NATIVE_EXECUTION_FINISHED", json.dumps(outcome), flush=True)
    except Exception as error:
        outcome.update(error_type=type(error).__name__, reason=str(error), traceback=traceback.format_exc())
        raise
    finally:
        stopped.set()
        observer.join(timeout=5)
        _record_receipt(records / "training.json", outcome)
        try:
            _record_receipt(records / "memory.json", _memory_receipt(local / "memory.jsonl"))
        except (OSError, ValueError) as error:
            print("QWEN35_MEMORY_UNVERIFIED", type(error).__name__, str(error), flush=True)
        if outcome["status"] == "failed":
            _retain_failure_diagnostics(local, cloud, 0)
        try:
            subprocess.run([sys.executable, "-m", "ray.scripts.scripts", "stop", "--force"], timeout=60, check=False)
            shutil.rmtree(local)
        except (OSError, subprocess.TimeoutExpired) as error:
            print("QWEN35_WORKER_CLEANUP_UNVERIFIED", type(error).__name__, str(error), flush=True)


def main():
    args = _parser().parse_args()
    _validate_args(args)
    if args.dry_run:
        run = args.output_root / args.pair / "DRY_RUN"
        receipt = _launch_receipt(args, run, _training_args(args, run))
        receipt.update(status="dry_run", population_verified=False, native_execution=False)
        print(json.dumps(receipt, indent=2))
        return
    _run(args)


if __name__ == "__main__":
    main()
