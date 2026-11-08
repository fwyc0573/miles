"""Run a SWE full/r256 pair using the qualified Qwen worker and Ray lifecycles.

The input JSON owns model paths, resource shapes and experiment parameters.
Run on a separately allocated teacher or student; `train` is the student's
native child entrypoint. This worker does not submit platform jobs.

    python -m tests.manual.agent_opd.run_swe_opd --config "$CONFIG" \
        --pair A --protocol r256 --role student
"""

import argparse
import json
import os
import shlex
import signal
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from scripts.run_qwen3_dense import ScriptArgs as DenseArgs
from tests.manual.agent_opd import megatron_scoring_lifetime
from tests.manual.agent_opd import qwen35_pair_worker as paired
from tests.manual.agent_opd import run_qwen35_opd as native
from tests.manual.agent_opd.submit_swe_opd import _validate_paths

from miles.utils.external_utils import command_utils as U
from miles.utils.external_utils.model_args_utils import shell_safe_model_args


def _config(path: Path, pair: str, protocol: str) -> dict:
    config = json.loads(path.read_text())
    _validate_paths(config, path.resolve())
    training = config.get("training", {})
    if "release_scoring_output" in training and type(training["release_scoring_output"]) is not bool:
        raise ValueError("release_scoring_output must be a JSON boolean")
    allocation = config["pairs"][pair]
    config["startup_timeout"] = allocation["startup_timeout"]
    config["protocol"] = protocol
    config["config_path"] = str(path.resolve())
    root = Path(config["run_root"]).resolve()
    if not root.is_relative_to(native._PERSONAL_ROOT):
        raise ValueError("SWE artifacts must stay in the personal cloud namespace")
    config["run_root"] = str(root / protocol)
    config["shared_dir"] = str(Path(config["shared_dir"]) / protocol)
    for role in ("student", "teacher"):
        source = Path(allocation[role]["path"]).resolve()
        if not source.is_relative_to(native._PERSONAL_ROOT) and source not in native._READ_ONLY_MODELS:
            raise ValueError(f"Unapproved {role} model source: {source}")
    return config


def _flags(values: dict) -> list[str]:
    result = []
    for name, value in values.items():
        if value is False or value is None:
            continue
        result.append("--" + name.replace("_", "-"))
        if value is not True:
            result.append(json.dumps(value) if isinstance(value, dict) else str(value))
    return result


def _training_args(config: dict, pair: str, teacher_url: str, run: Path, attempt: str) -> str:
    student = config["pairs"][pair]["student"]
    teacher = config["pairs"][pair]["teacher"]
    train, inputs = config["training"], config["inputs"]
    arguments = {
        "hf_checkpoint": student["path"], "ref_load": student["path"], "megatron_to_hf_mode": "raw",
        "save_hf": str(run / "hf" / "step_{rollout_id}"), "save_interval": train["save_interval"],
        "custom_megatron_post_save_hook_path": config["checkpoint"]["post_save_hook"],
        "data_source_path": "tests.manual.agent_opd.swe_inputs.NativeSWEDataSource",
        "swe_source_root": inputs["source_root"], "swe_source_manifest": inputs["source_manifest"],
        "swe_native_loader_path": inputs["native_loader_path"],
        "swe_native_loader_sha256": inputs["native_loader_sha256"],
        "chat_template_path": inputs["chat_template_path"],
        "apply_chat_template_kwargs": inputs["chat_template_kwargs"],
        "rollout_function_path": "tests.manual.agent_opd.swe_replay.SweReplay",
        "custom_generate_function_path": "tests.manual.agent_opd.qwen_alignment.generate",
        "custom_rm_path": "tests.manual.agent_opd.swe_replay.score_teacher", "rm_url": teacher_url,
        "reward_key": "reward",
        "custom_reward_post_process_path": "tests.manual.agent_opd.swe_replay.post_process_rewards",
        "num_rollout": train["successful_updates"], "rollout_batch_size": train["bank_slots"],
        "n_samples_per_prompt": 1, "global_batch_size": train["bank_slots"], "allow_partial_train_step": True,
        "rollout_seed": train["rollout_seed"], "seed": train["seed"],
        "rollout_max_response_len": config["context_tokens"], "rollout_max_context_len": config["context_tokens"],
        "rollout_temperature": train["temperature"], "rollout_top_p": train["top_p"], "rollout_top_k": train["top_k"],
        "balance_data": True,
        "swe_cell": f"{pair}/{config['protocol']}", "swe_attempt": attempt, "swe_protocol": config["protocol"],
        "swe_run_kind": train["run_kind"],
        "swe_evidence_dir": str(run / "training"), "swe_teacher_identity": teacher["path"],
        "swe_bank_slots": train["bank_slots"], "swe_bank_min_fraction": train["bank_min_fraction"],
        "swe_acquisition_seconds": train["acquisition_seconds"], "swe_bank_uses": train["bank_uses"],
        "swe_successful_updates": train["successful_updates"], "swe_context_tokens": config["context_tokens"],
        "custom_megatron_optimizer_step_hook_path": "tests.manual.agent_opd.swe_training.optimizer_step",
        "tensor_model_parallel_size": student["tp_size"], "sequence_parallel": True,
        "pipeline_model_parallel_size": 1, "context_parallel_size": 1,
        "expert_model_parallel_size": 1, "expert_tensor_parallel_size": 1,
        "recompute_granularity": "full", "recompute_method": "uniform", "recompute_num_layers": 1,
        "use_dynamic_batch_size": True, "use_dynamic_global_batch_size": True,
        "max_tokens_per_gpu": student["max_tokens_per_gpu"],
        "seq_length": config["context_tokens"], "linear_attention_backend": "fla",
        "linear_attention_input_norm": "te", "log_probs_backend": "fused",
        "use_opd": True, "opd_type": "sglang", "opd_log_prob_top_k": 0, "opd_kl_coef": 1,
        "advantage_estimator": "grpo", "calculate_per_token_loss": True, "get_mismatch_metrics": True,
        "use_tis": True, "custom_tis_function_path": "tests.manual.agent_opd.swe_tis.apply_tis",
        "eps_clip": train["eps_clip"], "eps_clip_high": train["eps_clip_high"], "entropy_coef": 0,
        "optimizer": train["optimizer"], "lr": train["lr"], "lr_decay_style": "constant", "lr_warmup_iters": 0,
        "weight_decay": train["weight_decay"], "adam_beta1": train["adam_beta1"],
        "adam_beta2": train["adam_beta2"], "adam_eps": train["adam_eps"],
        "rollout_num_gpus_per_engine": student["engine_gpus"], "sglang_context_length": config["context_tokens"],
        "sglang_mem_fraction_static": student["mem_fraction_static"],
        "sglang_max_running_requests": student["max_running_requests"],
        "sglang_chunked_prefill_size": student["chunked_prefill_size"],
        "sglang_router_request_timeout_secs": config["request_timeout"],
        "sglang_disable_cuda_graph": True, "sglang_enable_deterministic_inference": True,
        "sglang_attention_backend": "fa3", "sglang_enable_prefill_weight_versions": True,
        "sglang_linear_attn_prefill_backend": "triton", "sglang_dtype": "bfloat16",
        "dump_details": str(run), "save_debug_event_data": str(run / "events"),
        "check_weight_update_equal": True, "check_weight_update_skip_list": "visual",
        "log_inference_engine_weight_checksums": True, "colocate": True, "offload_train": True,
        "offload_rollout": True, "actor_num_nodes": 1, "actor_num_gpus_per_node": student["gpus_per_node"],
        "num_gpus_per_node": student["gpus_per_node"], "attention_dropout": 0, "hidden_dropout": 0,
        "accumulate_allreduce_grads_in_fp32": True, "attention_softmax_in_fp32": True, "attention_backend": "flash",
    }
    for name in ("skip_masked_assistant_turns", "visual_filter_receipt"):
        if name in inputs:
            arguments[f"swe_{name}"] = inputs[name]
    if "router_policy" in config:
        arguments["router_policy"] = config["router_policy"]
    if "release_scoring_output" in train:
        arguments.update(
            custom_megatron_before_log_prob_hook_path=(
                "tests.manual.agent_opd.megatron_scoring_lifetime_observer.before_log_prob"
            ),
            scoring_lifetime_dir=str(run / "megatron_scoring_lifetime" / "observations"),
            scoring_lifetime_source_sha256=megatron_scoring_lifetime.expected_source_sha256(
                train["release_scoring_output"]
            ),
        )
    arguments.update(config["tis"])
    overlap = arguments.keys() & config["checkpoint"]["hook_args"].keys()
    if overlap:
        raise ValueError(f"Checkpoint hook arguments duplicate recipe fields: {sorted(overlap)}")
    arguments.update(config["checkpoint"]["hook_args"])
    return shlex.join(_flags(arguments))


def _student_command(config: dict, pair: str, ready: dict, local: Path) -> list[str]:
    return [sys.executable, "-B", "-m", "tests.manual.agent_opd.run_swe_opd", "--config", config["config_path"], "--pair", pair,
            "--protocol", config["protocol"], "--role", "train", "--teacher-url", ready["url"]]


def _prepare_training(args, run: Path) -> tuple[str, dict]:
    config = args.swe_config
    scoring_source = None
    if "release_scoring_output" in config["training"]:
        # Patch the student dependency before the native worker starts Ray or submits its driver.
        scoring_source = megatron_scoring_lifetime.prepare_source(
            Path(args.megatron_path), image=config["image"], release=config["training"]["release_scoring_output"],
            archive_dir=run / "megatron_scoring_lifetime" / "source",
        )
    train_args = _training_args(config, args.pair, args.teacher_url, run, os.environ["KUBEBRAIN_RJOB_NAME"])
    recipe = DenseArgs(model_name=native._PAIRS[args.pair][0]).recipe
    git = ["git", "-c", f"safe.directory={U.repo_base_dir}", "-C", str(U.repo_base_dir)]
    receipt = {
        "pair": args.pair, "protocol": config["protocol"], "student": str(args.student), "teacher": str(args.teacher),
        "teacher_url": args.teacher_url, "training_argv": shlex.split(train_args),
        "model_argv": shlex.split(shell_safe_model_args(recipe.megatron_model_type)),
        "megatron_model_type": recipe.megatron_model_type, "megatron_path": args.megatron_path,
        "source_commit": subprocess.check_output([*git, "rev-parse", "HEAD"], text=True).strip(),
        "source_changes": subprocess.check_output([*git, "status", "--short"], text=True).splitlines(),
        "resolved_experiment": config, "final_hf": None,
        "update_accounting": "Native successful optimizer acknowledgements; checkpoint mapping is recorded at export.",
    }
    if scoring_source is not None:
        receipt["megatron_scoring_lifetime"] = scoring_source
    return train_args, receipt


def _train(config: dict, pair: str, teacher_url: str) -> None:
    allocation = config["pairs"][pair]
    args = SimpleNamespace(
        pair=pair, student=Path(allocation["student"]["path"]), teacher=Path(allocation["teacher"]["path"]),
        teacher_url=teacher_url, output_root=Path(config["run_root"]) / "student",
        shared_dir=Path(config["shared_dir"]) / "student", local_root=Path(config["worker_local_root"]),
        gpu_type=config["gpu_tag"], gpus_per_node=allocation["student"]["gpus_per_node"],
        startup_timeout=config["startup_timeout"], megatron_path=config["megatron_path"],
        num_rollout=config["training"]["successful_updates"], swe_config=config,
    )
    native._run(args, prepare_training=_prepare_training)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--pair", choices=("A", "B"), required=True)
    parser.add_argument("--protocol", choices=("full", "r256"), required=True)
    parser.add_argument("--role", choices=("student", "teacher", "train"), required=True)
    parser.add_argument("--teacher-url")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = _config(args.config, args.pair, args.protocol)
    if args.dry_run:
        run = Path(config["run_root"]) / "student" / args.pair / "dry-run"
        print(_training_args(config, args.pair, args.teacher_url or "http://teacher:30000/generate", run, "dry-run"))
        return 0
    if args.role == "train":
        if not args.teacher_url:
            parser.error("--role train requires --teacher-url")
        _train(config, args.pair, args.teacher_url)
        return 0
    job, rank = os.environ["KUBEBRAIN_RJOB_NAME"], int(os.environ["KUBEBRAIN_REPLICA"])
    directory = Path(config["shared_dir"]) / job / args.pair
    directory.mkdir(parents=True, exist_ok=True)
    local = Path(config["worker_local_root"]) / f"swe-{job}-{args.pair}-{args.role}-{rank}"
    signal.signal(signal.SIGTERM, paired._terminate)
    try:
        if args.role == "teacher":
            code = paired._run_teacher(config, args.pair, rank, directory, local)
        else:
            code = paired._run_student(config, args.pair, rank, directory, local, command_builder=_student_command)
    except subprocess.CalledProcessError as error:
        print("QWEN35_NATIVE_CHILD_FAILED", error.returncode, str(error), flush=True)
        code = error.returncode
    return paired._exit_code(code)


if __name__ == "__main__":
    raise SystemExit(main())
