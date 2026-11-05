"""Qualify two actual FrogNano -> Qwen3.5 OPD updates on one eight-H800 worker.

Uses the existing Qwen3.5 raw HF load, hybrid-attention model and native OPD loss.
The eight distinct source turns inherit Ticket07 exclusions. Their histories are
rendered with Qwen's own tokenizer/template; GLM token IDs are never reused as
Qwen input. All datasets, dumps, logs and worker caches are disposable.
"""

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from threading import Event, Thread

import yaml
from examples.agentic_opd.glm_turns import normalize_tool_arguments, token_hash
from scripts.run_glm47_flash_agent_opd import _training_env
from scripts.run_qwen3_dense import ScriptArgs as DenseArgs
from tests.manual.agent_opd.rjob_warmup import (
    _check_tokenizers,
    _memory_receipt,
    _record_memory,
    _retain_failure_diagnostics,
    _worker_environment,
    _write_json,
)
from transformers import AutoTokenizer

from miles.utils.external_utils import command_utils as U


def _prepare(args, cloud: Path, records: Path) -> Path:
    temporary = cloud / "glm-source-turns.jsonl"
    subprocess.run(
        [
            sys.executable,
            "-B",
            str(Path(__file__).with_name("prepare_glm5_2.py")),
            "--manifest",
            str(args.manifest),
            "--tokenizer",
            str(args.glm_tokenizer),
            "--output",
            str(temporary),
            "--report",
            str(records / "glm-source.json"),
            "--turns-per-category",
            "2",
            "--max-prompt-tokens",
            str(args.context_tokens - args.response_tokens),
        ],
        check=True,
        timeout=args.startup_timeout,
    )
    tokenizer = AutoTokenizer.from_pretrained(args.student, local_files_only=True)
    dataset = cloud / "qwen-glm5.2-turns.jsonl"
    evidence = []
    with dataset.open("x") as stream:
        for line in temporary.read_text().splitlines():
            row = json.loads(line)
            metadata = row["metadata"]
            thinking = metadata["original_completion"]["has_thinking"]
            prompt = tokenizer.apply_chat_template(
                normalize_tool_arguments(metadata["history"]),
                tools=metadata["tools"],
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=thinking,
            )
            ids = tokenizer.encode(prompt, add_special_tokens=False)
            if len(ids) + args.response_tokens > args.context_tokens:
                raise ValueError("Qwen-rendered source exceeds the qualification context budget")
            glm_source = metadata["source"]
            metadata["source"] = {
                "uid": glm_source["uid"],
                "category": glm_source["category"],
                "glm_source": glm_source,
                "prompt_token_count": len(ids),
                "prompt_sha256": token_hash(ids),
            }
            metadata["thinking_enabled"] = thinking
            evidence.append(
                {
                    "source_uid": glm_source["uid"],
                    "category": glm_source["category"],
                    "prompt_tokens": len(ids),
                    "prompt_sha256": token_hash(ids),
                    "thinking_enabled": thinking,
                }
            )
            stream.write(json.dumps({"prompt": prompt, "metadata": metadata}, ensure_ascii=False) + "\n")
    temporary.unlink()
    _write_json(
        records / "dataset.json",
        {
            "dataset": str(dataset),
            "turns": evidence,
            "history_template_policy": "Pinned Qwen template; original history remains in sample metadata",
        },
    )
    return dataset


def _training_args(args, dataset: Path, run: Path) -> str:
    recipe = DenseArgs(model_name="Qwen3.5-4B").recipe
    inference = {
        "models": [
            {
                "name": name,
                "model_path": str(path),
                "update_weights": update,
                "server_groups": [{"worker_type": "regular", "num_gpus": 2, "num_gpus_per_engine": 2}],
            }
            for name, path, update in (("default", args.student, True), ("teacher", args.teacher, False))
        ]
    }
    checkpoint = f"--hf-checkpoint {shlex.quote(str(args.student))} --ref-load {shlex.quote(str(args.student))} --megatron-to-hf-mode raw"
    rollout = (
        f"--prompt-data {shlex.quote(str(dataset))} --input-key prompt --metadata-key metadata "
        "--custom-generate-function-path tests.manual.agent_opd.qwen_alignment.generate "
        "--custom-rm-path tests.manual.agent_opd.qwen_alignment.score_teacher --reward-key reward "
        "--custom-reward-post-process-path examples.agentic_opd.rollout.post_process_rewards "
        "--num-rollout 2 --rollout-batch-size 4 --n-samples-per-prompt 1 --global-batch-size 4 "
        f"--rollout-max-response-len {args.response_tokens} --rollout-max-context-len {args.context_tokens} "
        "--rollout-temperature 1 --rollout-top-p 1 --rollout-top-k -1 --rollout-seed 42"
    )
    parallel = (
        f"--tensor-model-parallel-size {recipe.tensor_model_parallel_size} --sequence-parallel "
        "--pipeline-model-parallel-size 1 --context-parallel-size 1 --expert-model-parallel-size 1 --expert-tensor-parallel-size 1 "
        "--recompute-granularity full --recompute-method uniform --recompute-num-layers 1 "
        f"--use-dynamic-batch-size --max-tokens-per-gpu {recipe.max_tokens_per_gpu} --seq-length {args.context_tokens} "
        "--linear-attention-backend fla --linear-attention-input-norm te"
    )
    algorithm = (
        "--use-opd --opd-type sglang --opd-log-prob-top-k 0 --opd-kl-coef 1 "
        "--advantage-estimator grpo --calculate-per-token-loss --get-mismatch-metrics --use-tis "
        "--custom-tis-function-path examples.infra_features.train_infer_mismatch_helper.mis.compute_mis_weights_with_cp "
        "--tis-mode mask --tis-lower-bound 0.5 --tis-upper-bound 2 --eps-clip 0.2 --eps-clip-high 0.28 --entropy-coef 0"
    )
    optimizer = "--optimizer adam --lr 2e-6 --lr-decay-style constant --lr-warmup-iters 0 --weight-decay 0 --adam-beta1 0.9 --adam-beta2 0.98"
    sglang = (
        f"--rollout-num-gpus 4 --rollout-num-gpus-per-engine 2 --sglang-config {U.encode_pseudo_file(yaml.safe_dump(inference))} "
        f"--sglang-context-length {args.context_tokens} --sglang-mem-fraction-static {recipe.sglang_mem_fraction_static} "
        "--sglang-max-running-requests 4 --sglang-chunked-prefill-size 8192 --sglang-disable-cuda-graph "
        "--sglang-enable-deterministic-inference --sglang-attention-backend fa3 --sglang-linear-attn-prefill-backend triton --sglang-dtype bfloat16"
    )
    verification = (
        f"--dump-details {shlex.quote(str(run))} --check-weight-update-equal --check-weight-update-skip-list visual "
        "--log-inference-engine-weight-checksums --actor-num-nodes 1 --actor-num-gpus-per-node 4 --num-gpus-per-node 8 "
        "--attention-dropout 0 --hidden-dropout 0 --accumulate-allreduce-grads-in-fp32 --attention-softmax-in-fp32 --attention-backend flash"
    )
    return " ".join((checkpoint, rollout, parallel, algorithm, optimizer, sglang, verification))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--student", type=Path, required=True)
    parser.add_argument("--teacher", type=Path, required=True)
    parser.add_argument("--glm-tokenizer", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--shared-dir", type=Path, required=True)
    parser.add_argument("--context-tokens", type=int, default=32768)
    parser.add_argument("--response-tokens", type=int, default=1024)
    parser.add_argument("--startup-timeout", type=int, default=600)
    args = parser.parse_args()
    for path in (args.student, args.teacher, args.glm_tokenizer, args.output_root):
        path.relative_to("/mnt/codesign-exp/ycfeng")
    if int(os.environ["KUBEBRAIN_REPLICA_TOTAL"]) != 1:
        raise ValueError("The bounded Qwen qualification requires one eight-GPU replica")
    job = os.environ["KUBEBRAIN_RJOB_NAME"]
    cloud = args.output_root / job
    cloud.mkdir(parents=True, exist_ok=False)
    records = args.shared_dir / job
    records.mkdir(parents=True, exist_ok=False)
    local = Path("/var/tmp") / f"ao-qwen-{job.removeprefix('exp-')}"
    _worker_environment(local)
    stopped = Event()
    observer = Thread(target=_record_memory, args=(local / "memory.jsonl", stopped), daemon=True)
    observer.start()
    succeeded = False
    try:
        gpus = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True
        ).splitlines()
        if len(gpus) != 8 or any("H800" not in name for name in gpus):
            raise ValueError(f"Qwen worker GPU allocation differs: {gpus}")
        _check_tokenizers(args.student, args.teacher)
        dataset = _prepare(args, cloud, records)
        run = cloud / "training"
        train_args = _training_args(args, dataset, run)
        _write_json(
            records / "launch.json",
            {
                "training_args": train_args,
                "source_commit": subprocess.check_output(
                    [
                        "git",
                        "-c",
                        f"safe.directory={U.repo_base_dir}",
                        "-C",
                        str(U.repo_base_dir),
                        "rev-parse",
                        "HEAD",
                    ],
                    text=True,
                ).strip(),
                "gpu_names": gpus,
                "python": sys.version.split()[0],
            },
        )
        backend = U.default_config().create_backend()
        backend.execute_train(
            train_args=train_args,
            num_gpus_per_node=8,
            megatron_model_type="qwen3.5-4B",
            extra_env_vars={
                **_training_env(DenseArgs(model_name="Qwen3.5-4B")),
                "no_proxy": "*",
                "NO_PROXY": "*",
                "LD_LIBRARY_PATH": os.environ["LD_LIBRARY_PATH"],
            },
        )
        inspected = subprocess.run(
            [
                sys.executable,
                "-B",
                str(Path(__file__).with_name("inspect_warmup.py")),
                "--run-dir",
                str(run),
                "--report",
                str(records / "validation.md"),
                "--expected-rollouts",
                "2",
                "--without-routing-replay",
            ],
            timeout=args.startup_timeout,
        )
        _write_json(
            records / "training.json",
            {"status": "succeeded", "run_dir": str(run), "inspection_exit_code": inspected.returncode},
        )
        succeeded = True
        print("AGENT_OPD_QWEN_TRAINING_FINISHED", str(run), inspected.returncode, flush=True)
    finally:
        stopped.set()
        observer.join(timeout=5)
        memory = _memory_receipt(local / "memory.jsonl")
        _write_json(records / "memory.json", memory)
        print("AGENT_OPD_QWEN_MEMORY", json.dumps(memory), flush=True)
        if not succeeded:
            _retain_failure_diagnostics(local, cloud, 0)
        subprocess.run([sys.executable, "-m", "ray.scripts.scripts", "stop", "--force"], timeout=60, check=False)
        shutil.rmtree(local)


if __name__ == "__main__":
    main()
