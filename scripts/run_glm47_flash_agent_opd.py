"""Warm up GLM-4.7-Flash on-policy distillation on complete glm5.2 turns.

Requires local or mounted HF student/teacher weights, a prepared glm5.2 JSONL,
and an external Ray cluster with 16 H200 GPUs. Eight GPUs train the student;
four serve the student and four serve the frozen GLM-4.7-Flash-Coder teacher.

Args:
    model_dir: Parent directory for HF checkpoints.
    student_checkpoint: Explicit HF student directory; otherwise model_dir/student_name.
    teacher_checkpoint: Explicit HF teacher directory; otherwise model_dir/teacher_name.
    prompt_data: JSONL made by tests/manual/agent_opd/prepare_glm5_2.py.
    num_rollout: Number of warmup updates (default 2).
    rollout_max_response_len: Maximum newly sampled completion tokens.
    output_dir: Root for disposable warmup trajectories, metrics and token dumps.
    extra_args: Additional native Miles arguments.

Example:
    MILES_SCRIPT_EXTERNAL_RAY=1 python scripts/run_glm47_flash_agent_opd.py \
        --model-dir /root/models --prompt-data /root/datasets/glm5.2-warmup.jsonl \
        --output-dir /root/shared_data --num-rollout 2
"""

import os
import shlex
from dataclasses import dataclass, field
from pathlib import Path

import typer
import yaml
from sglang.srt.environ import envs

from miles.utils.external_utils import command_utils as U


@dataclass
class ScriptArgs(U.ExecuteTrainConfig):
    run_id: str = field(default_factory=lambda: U.create_run_id())
    model_dir: str = "/root/models"
    data_dir: str = "/root/datasets"
    student_name: str = "GLM-4.7-Flash"
    teacher_name: str = "GLM-4.7-Flash-Coder"
    student_checkpoint: str | None = None
    teacher_checkpoint: str | None = None
    prompt_data: str | None = None
    megatron_path: str = "/root/Megatron-LM"
    num_gpus_per_node: int = 8
    num_nodes: int = 1
    student_engine_gpus: int = 4
    teacher_engine_gpus: int = 4
    num_rollout: int = 2
    rollout_batch_size: int = 4
    rollout_max_response_len: int = 1024
    max_seq_len: int = 65536
    max_tokens_per_gpu: int = 45056
    lr: float = 2e-6
    extra_args: str = ""

    @property
    def student_path(self) -> str:
        return self.student_checkpoint or str(Path(self.model_dir) / self.student_name)

    @property
    def teacher_path(self) -> str:
        return self.teacher_checkpoint or str(Path(self.model_dir) / self.teacher_name)

    @property
    def dataset_path(self) -> str:
        return self.prompt_data or str(Path(self.data_dir) / "glm5.2-warmup.jsonl")

    @property
    def run_dir(self) -> str:
        return str(Path(self.output_dir) / self.run_id)

    def __post_init__(self):
        if self.num_nodes != 1 or self.num_gpus_per_node != 8:
            raise ValueError("The GLM warmup trains on one eight-GPU node")
        if self.student_engine_gpus != 4 or self.teacher_engine_gpus != 4:
            raise ValueError("The 16-GPU warmup reserves four GPUs for each inference model")
        if self.student_path == self.teacher_path:
            raise ValueError("OPD requires distinct student and teacher checkpoints")


def _training_env(args: ScriptArgs) -> dict[str, str]:
    requested = U.resolve_extra_env_vars(
        {"NVTE_ALLOW_NONDETERMINISTIC_ALGO": "0", "CUBLAS_WORKSPACE_CONFIG": ":4096:8"}, args
    )
    effective = {**os.environ, **requested}
    channels = (
        envs.SGLANG_DETERMINISTIC_NCCL_NCHANNELS.parse(value)
        if (value := effective.get(envs.SGLANG_DETERMINISTIC_NCCL_NCHANNELS.name)) is not None
        else envs.SGLANG_DETERMINISTIC_NCCL_NCHANNELS.get()
    )
    if channels < 1:
        raise ValueError("Deterministic NCCL channels must be positive")
    requested[envs.SGLANG_DETERMINISTIC_NCCL_NCHANNELS.name] = str(channels)
    for key in ("NCCL_MIN_NCHANNELS", "NCCL_MAX_NCHANNELS"):
        value = effective.get(key, str(channels))
        if int(value) != channels:
            raise ValueError(f"{key}={value} conflicts with SGLang deterministic channels={channels}")
        # SGLang pins both bounds at engine startup; senders need the same count.
        requested[key] = value
    return requested


def execute(args: ScriptArgs):
    backend = args.create_backend()
    inference = {
        "models": [
            {
                "name": name,
                "model_path": path,
                "update_weights": update,
                "server_groups": [
                    {
                        "worker_type": "regular",
                        "num_gpus": gpus,
                        "num_gpus_per_engine": gpus,
                    }
                ],
            }
            for name, path, update, gpus in (
                ("default", args.student_path, True, args.student_engine_gpus),
                ("teacher", args.teacher_path, False, args.teacher_engine_gpus),
            )
        ],
    }
    config = U.encode_pseudo_file(yaml.safe_dump(inference))
    checkpoint = (
        f"--hf-checkpoint {shlex.quote(args.student_path)} "
        f"--ref-load {shlex.quote(args.student_path)} "
        "--megatron-to-hf-mode bridge "
    )
    rollout = (
        f"--prompt-data {shlex.quote(args.dataset_path)} --input-key prompt --metadata-key metadata "
        "--custom-generate-function-path examples.agentic_opd.rollout.generate "
        "--custom-rm-path examples.agentic_opd.rollout.score_teacher --reward-key reward "
        "--custom-reward-post-process-path examples.agentic_opd.rollout.post_process_rewards "
        f"--num-rollout {args.num_rollout} --rollout-batch-size {args.rollout_batch_size} "
        f"--n-samples-per-prompt 1 --global-batch-size {args.rollout_batch_size} "
        f"--rollout-max-response-len {args.rollout_max_response_len} "
        f"--rollout-max-context-len {args.max_seq_len} "
        "--rollout-temperature 1 --rollout-top-p 1 --rollout-top-k -1 --rollout-seed 42 "
    )
    parallel = (
        "--tensor-model-parallel-size 4 --pipeline-model-parallel-size 1 "
        "--context-parallel-size 1 --expert-model-parallel-size 8 --expert-tensor-parallel-size 1 "
        "--sequence-parallel --recompute-granularity full --recompute-method uniform --recompute-num-layers 1 "
        f"--use-dynamic-batch-size --max-tokens-per-gpu {args.max_tokens_per_gpu} "
        f"--seq-length {args.max_seq_len} "
    )
    algorithm = (
        "--use-opd --opd-type sglang --opd-log-prob-top-k 0 --opd-kl-coef 1 "
        "--advantage-estimator grpo --calculate-per-token-loss "
        "--use-rollout-routing-replay --get-mismatch-metrics --use-tis "
        "--custom-tis-function-path examples.infra_features.train_infer_mismatch_helper.mis.compute_mis_weights_with_cp "
        "--tis-mode mask --tis-lower-bound 0.5 --tis-upper-bound 2 "
        "--eps-clip 0.2 --eps-clip-high 0.28 --entropy-coef 0 "
    )
    optimizer = (
        f"--optimizer adam --lr {args.lr} --lr-decay-style constant --lr-warmup-iters 0 "
        "--weight-decay 0 --adam-beta1 0.9 --adam-beta2 0.98 "
        "--optimizer-cpu-offload --overlap-cpu-optimizer-d2h-h2d --use-precision-aware-optimizer "
    )
    sglang = (
        f"--rollout-num-gpus {args.student_engine_gpus + args.teacher_engine_gpus} "
        f"--rollout-num-gpus-per-engine {args.student_engine_gpus} --sglang-config {config} "
        f"--sglang-context-length {args.max_seq_len} "
        "--sglang-mem-fraction-static 0.75 --sglang-max-running-requests 4 "
        "--sglang-chunked-prefill-size 8192 --sglang-disable-cuda-graph "
        "--sglang-enable-deterministic-inference --sglang-attention-backend fa3 "
        "--sglang-moe-runner-backend triton --sglang-dtype bfloat16 "
    )
    verification = (
        f"--dump-details {shlex.quote(args.run_dir)} --check-weight-update-equal --log-inference-engine-weight-checksums "
        "--attention-dropout 0 --hidden-dropout 0 --accumulate-allreduce-grads-in-fp32 "
        "--attention-softmax-in-fp32 --attention-backend flash "
        f"--actor-num-nodes {args.num_nodes} --actor-num-gpus-per-node {args.num_gpus_per_node} "
        f"--num-gpus-per-node {args.num_gpus_per_node} "
    )
    backend.execute_train(
        train_args=" ".join(
            (
                checkpoint,
                rollout,
                parallel,
                algorithm,
                optimizer,
                sglang,
                verification,
                U.get_default_wandb_args(__file__, run_id=args.run_id),
                args.extra_args,
            )
        ),
        num_gpus_per_node=args.num_gpus_per_node,
        megatron_model_type="glm4.7-flash",
        megatron_path=args.megatron_path,
        extra_env_vars=_training_env(args),
    )


@U.dataclass_cli
def main(args: ScriptArgs):
    execute(args)


if __name__ == "__main__":
    typer.run(main)
