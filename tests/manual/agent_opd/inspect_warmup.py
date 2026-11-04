"""Inspect native OPD dumps and write aggregate verification evidence only.

This offline check reads completed warmup artifacts. It records token alignment,
R3 arrays, finite updates, sampled-token logprob differences and published weight
versions. It neither changes training nor invents a numerical parity threshold.
"""

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import torch

from examples.agentic_opd.glm_turns import token_hash


def _tensor(value) -> torch.Tensor:
    return torch.as_tensor(value).detach().cpu()


def _sample_checks(path: Path, expected_samples: int) -> tuple[dict, dict]:
    dump = torch.load(path, map_location="cpu", weights_only=False)
    samples = dump["samples"]
    if len(samples) != expected_samples:
        raise ValueError(f"{path}: expected {expected_samples} samples, got {len(samples)}")
    indexed = {}
    observations = []
    for sample in samples:
        source = sample["metadata"]["source"]
        completion = sample["metadata"]["completion"]
        teacher = sample["metadata"]["teacher_scoring"]
        tokens = sample["tokens"]
        count = source["prompt_token_count"]
        response = tokens[count:]
        if token_hash(tokens[:count]) != source["prompt_sha256"] or len(response) != sample["response_length"]:
            raise ValueError("A generated prompt/completion boundary differs from its source")
        if token_hash(response) != completion["token_sha256"]:
            raise ValueError("Parsed completion metadata refers to different sampled tokens")
        if not teacher["token_ids_match"] or teacher["scored_tokens"] != len(response):
            raise ValueError("Teacher scoring did not cover the sampled completion")
        if not math.isfinite(teacher["mean_logprob"]):
            raise ValueError("Teacher logprobs are non-finite")
        if not torch.isfinite(_tensor(sample["rollout_log_probs"])).all():
            raise ValueError("Rollout logprobs are non-finite")
        versions = {span["version"] for call in sample["weight_versions"] for span in call["spans"]}
        if len(versions) != 1:
            raise ValueError("A synchronous completion contains missing or mixed weight versions")
        indexed[sample["index"]] = sample
        observations.append(
            {
                "source_category": source["category"],
                "completion_category": completion["category"],
                "prompt_tokens": count,
                "completion_tokens": len(response),
                "reasoning_chars": len(completion["reasoning_content"]),
                "body_chars": len(completion["content"]),
                "tool_names": completion["tool_names"],
                "status": sample["status"],
                "weight_version": next(iter(versions)),
                "teacher_mean_logprob": teacher["mean_logprob"],
            }
        )
    return indexed, {"rollout_id": dump["rollout_id"], "samples": observations}


def _train_checks(paths: list[Path], samples: dict) -> dict:
    differences, ratios = [], []
    seen = []
    route_shapes = []
    for path in paths:
        dump = torch.load(path, map_location="cpu", weights_only=False)
        batch = dump["rollout_data"]
        if dump["cp_size"] != 1:
            raise ValueError("This warmup inspector expects the configured CP1 layout")
        for i, index in enumerate(batch["sample_indices"]):
            index = int(index)
            sample = samples[index]
            tokens = _tensor(batch["tokens"][i])
            if not torch.equal(tokens, _tensor(sample["tokens"])):
                raise ValueError("Training consumed different token IDs from inference")
            old = _tensor(batch["log_probs"][i]).float()
            rollout = _tensor(batch["rollout_log_probs"][i]).float()
            teacher = _tensor(batch["teacher_log_probs"][i]).float()
            if old.shape != rollout.shape or teacher.shape != rollout.shape:
                raise ValueError("Training, rollout and teacher token logprobs differ in shape")
            if not all(torch.isfinite(value).all() for value in (old, rollout, teacher)):
                raise ValueError("A training logprob tensor is non-finite")
            replay = _tensor(batch["rollout_routed_experts"][i])
            original = _tensor(sample["rollout_routed_experts"])
            if replay.shape[0] != len(tokens) - 1 or not torch.equal(replay, original):
                raise ValueError("Training R3 arrays differ from the inference routes")
            route_shapes.append(list(replay.shape))
            differences.append((old - rollout).abs())
            ratios.append((old - rollout).exp())
            seen.append(index)
    if sorted(seen) != sorted(samples):
        raise ValueError("Training shards did not consume each sampled turn exactly once")
    difference = torch.cat(differences)
    ratio = torch.cat(ratios)
    return {
        "sample_count": len(seen),
        "scored_tokens": difference.numel(),
        "same_token_ids": True,
        "r3_arrays_equal": True,
        "r3_shapes": route_shapes,
        "logprob_abs_mean": difference.mean().item(),
        "logprob_abs_p50": difference.quantile(0.5).item(),
        "logprob_abs_p95": difference.quantile(0.95).item(),
        "logprob_abs_p99": difference.quantile(0.99).item(),
        "logprob_abs_max": difference.max().item(),
        "tis_ratio_mean": ratio.mean().item(),
        "tis_outside_0_5_to_2_fraction": ((ratio < 0.5) | (ratio > 2)).float().mean().item(),
    }


def _event_checks(directory: Path, expected_rollouts: int) -> dict:
    events = []
    for path in directory.rglob("*.jsonl"):
        events.extend(json.loads(line) for line in path.read_text().splitlines() if line.strip())
    steps = [event for event in events if event["type"] == "train_group_step_end" and event["role"] == "actor"]
    if len(steps) != expected_rollouts or any(
        not outcomes or any(outcome != "normal" for outcome in outcomes)
        for event in steps
        for outcomes in event["cell_outcomes"].values()
    ):
        raise ValueError("Native optimizer outcomes did not confirm every requested update")
    metrics = [event["metrics"] for event in events if event["type"] == "metric"]
    train_metrics = [row for row in metrics if "train/grad_norm" in row]
    if len(train_metrics) != expected_rollouts or any(
        not math.isfinite(float(value))
        for row in train_metrics
        for key, value in row.items()
        if key in ("train/grad_norm", "train/loss", "train/pg_loss")
    ):
        raise ValueError("Native training metrics are missing or non-finite")
    checksums = sorted(
        (event for event in events if event["type"] == "inference_engine_weight_checksum"),
        key=lambda event: event["weight_version"],
    )
    if len(checksums) != expected_rollouts:
        raise ValueError("Initial and intermediate published weights are missing checksum evidence")
    snapshots = [event["engine_snapshots"][0]["tensor_checksums"] for event in checksums]
    changed = sum(snapshots[0].get(name) != value for name, value in snapshots[-1].items())
    if changed == 0:
        raise ValueError("The first optimizer update did not change published inference weights")
    return {
        "event_types": dict(Counter(event["type"] for event in events)),
        "optimizer_rollouts": sorted(event["rollout_id"] for event in steps),
        "train_metrics": [
            {key: value for key, value in row.items() if key.startswith("train/")} for row in train_metrics
        ],
        "published_weight_versions": [event["weight_version"] for event in checksums],
        "changed_inference_tensors": changed,
        "final_optimizer_update_published": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected-rollouts", type=int, default=2)
    parser.add_argument("--expected-samples", type=int, default=4)
    args = parser.parse_args()
    results = []
    for rollout_id in range(args.expected_rollouts):
        samples, observations = _sample_checks(
            args.run_dir / "rollout_data" / f"{rollout_id}.pt", args.expected_samples
        )
        observations["training"] = _train_checks(
            sorted((args.run_dir / "train_data").glob(f"{rollout_id}_*.pt")), samples
        )
        results.append(observations)
    policy = [
        torch.load(path, map_location="cpu", weights_only=False)
        for path in (args.run_dir / "policy_loss_debug").glob("*.pt")
    ]
    if not policy or any(not all(dump["finite"].values()) for dump in policy):
        raise ValueError("Native policy-loss debug tensors are missing or non-finite")
    events = _event_checks(args.run_dir / "events", args.expected_rollouts)
    for observations, version in zip(results, events["published_weight_versions"], strict=True):
        if any(str(sample["weight_version"]) != str(version) for sample in observations["samples"]):
            raise ValueError("A completion was sampled from a different published policy version")
    report = {
        "structural_checks": "passed",
        "sampled_weight_versions_match_publications": True,
        "numerical_parity": "measured; no uncalibrated tolerance asserted",
        "run_dir": str(args.run_dir),
        "rollouts": results,
        "policy_loss_calls": len(policy),
        "events": events,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("# Native OPD Warmup Observations\n\n```json\n" + json.dumps(report, indent=2) + "\n```\n")
    print("AGENT_OPD_NATIVE_DUMPS_INSPECTED", str(args.report), flush=True)


if __name__ == "__main__":
    main()
