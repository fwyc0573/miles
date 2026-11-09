"""Independently audit downloaded native OPD tensors without importing producers.

Only trusted, locally downloaded torch dumps are supported. CPU reconstruction
is evidence about saved values, not a reproduction of the backend's backward.
Bounds are explicit inputs taken from the experiment specification.
"""

import argparse
import json
import math
import platform
import resource
import sys
from pathlib import Path


def _same(left, right):
    import torch

    return left.shape == right.shape and torch.equal(left, right)


def _key(sample):
    meta = sample["metadata"]
    return (meta["swe_attempt"], meta["swe_bank"], meta["swe_slot"], meta["source_uid"], sample["sample_index"])


def _load_training(root, ranks):
    import torch

    steps, files = {}, []
    for path in sorted((root / "train_data").glob("*.pt")):
        dump = torch.load(path, map_location="cpu", weights_only=False)
        step, rank = dump["rollout_id"], dump["rank"]
        assert dump["cp_size"] == 1 and dump["cp_rank"] == 0, "Only complete CP1 responses are supported"
        assert rank in ranks and rank not in steps.get(step, {}), "Unexpected or duplicate rank"
        data = dump["rollout_data"]
        count = len(data["sample_indices"])
        names = (
            "tokens",
            "loss_masks",
            "log_probs",
            "teacher_log_probs",
            "rollout_log_probs",
            "advantages",
            "opd_reverse_kl",
            "returns",
            "metadata",
            "response_lengths",
            "total_lengths",
            "weight_versions",
            "rewards",
        )
        assert all(len(data[name]) == count for name in names)
        samples = []
        for i, index in enumerate(data["sample_indices"]):
            sample = {name: data[name][i] for name in names}
            sample.update(sample_index=index, rank=rank, step=step, train_file=str(path))
            meta = sample["metadata"]
            assert index == meta["sample_index"]
            assert meta["swe_attempted_rollout_id"] == step
            assert sample["tokens"].numel() == sample["total_lengths"]
            assert sample["response_lengths"] == meta["completion_token_count"]
            assert sample["total_lengths"] - sample["response_lengths"] == meta["prompt_token_count"]
            assert sample["weight_versions"] == meta["generation_weight_versions"]
            for name in (
                "loss_masks",
                "log_probs",
                "teacher_log_probs",
                "rollout_log_probs",
                "advantages",
                "opd_reverse_kl",
                "returns",
            ):
                value = sample[name]
                assert value.shape == (sample["response_lengths"],), (path, name, value.shape)
                assert not value.requires_grad and torch.isfinite(value).all()
            mask = sample["loss_masks"]
            assert ((mask == 0) | (mask == 1)).all()
            assert data["rollout_mask_sums"][i].item() == mask.sum().item()
            assert sample["rewards"] == 0 and not sample["returns"].any()
            samples.append(sample)
        steps.setdefault(step, {})[rank] = {"samples": samples, "data": data}
        files.append(str(path))
    assert steps, "No native training dumps"
    for step, shards in steps.items():
        assert set(shards) == set(ranks), (step, "Incomplete DP rank coverage")
        keys = [_key(sample) for shard in shards.values() for sample in shard["samples"]]
        assert len(keys) == len(set(keys)), "Duplicate canonical sample across ranks"
    return steps, files


def _match_debug(root, steps):
    import torch

    files, coverage = [], set()
    for path in sorted((root / "policy_loss_debug").glob("*.pt")):
        dump = torch.load(path, map_location="cpu", weights_only=False)
        rank = dump["rank"]
        offset, matched_steps = 0, set()
        for local_index, debug in enumerate(dump["samples"]):
            assert debug["index"] == local_index
            candidates = []
            for shards in steps.values():
                for sample in shards[rank]["samples"]:
                    pairs = (
                        ("log_probs", "old_log_probs"),
                        ("advantages", "advantages"),
                        ("rollout_log_probs", "rollout_log_probs"),
                        ("loss_masks", "local_loss_mask"),
                    )
                    if (
                        sample["total_lengths"] == debug["total_length"]
                        and sample["response_lengths"] == debug["response_length"]
                        and all(_same(sample[a], debug[b]) for a, b in pairs)
                    ):
                        candidates.append(sample)
            assert len(candidates) == 1, (path, local_index, "Ambiguous or absent exact tensor match")
            sample = candidates[0]
            identity = (sample["step"], _key(sample))
            assert identity not in coverage, "Duplicate policy loss sample"
            coverage.add(identity)
            matched_steps.add(sample["step"])
            length = debug["response_length"]
            sample["debug"] = debug
            sample["debug_file"] = str(path)
            sample["saved_pg_loss"] = dump["pg_loss"][offset : offset + length]
            sample["saved_ppo_kl"] = dump["ppo_kl"][offset : offset + length]
            offset += length
        assert len(matched_steps) == 1 and offset == dump["pg_loss"].numel() == dump["ppo_kl"].numel()
        files.append(str(path))
    expected = {
        (step, _key(sample))
        for step, shards in steps.items()
        for shard in shards.values()
        for sample in shard["samples"]
    }
    assert coverage == expected, "Incomplete native PPO dump coverage"
    return files


def _audit_sample(sample, args):
    import torch

    s, q, b = (sample[name] for name in ("log_probs", "teacher_log_probs", "rollout_log_probs"))
    debug = sample["debug"]
    train_logp, mask = debug["train_log_probs"], sample["loss_masks"].bool()
    delta = s.double() - b.double()
    ratio = delta.exp()
    answer_ratio = delta[mask].mean().exp()
    token_pass = (ratio >= args.token_bounds[0]) & (ratio <= args.token_bounds[1])
    answer_pass = bool(args.answer_bounds[0] <= answer_ratio.item() <= args.answer_bounds[1])
    retained = mask & token_pass & answer_pass
    advantage = q - s
    ppo_kl = s - train_logp
    rho = (train_logp - s).exp()
    raw_pg = torch.maximum(-rho * advantage, -rho.clamp(*args.ppo_bounds) * advantage)
    advantage_error = (advantage - debug["advantages"]).abs().max().item()
    kl_error = (s - q - sample["opd_reverse_kl"]).abs().max().item()
    pg_error = (raw_pg - sample["saved_pg_loss"]).abs().max().item()
    ppo_error = (ppo_kl - sample["saved_ppo_kl"]).abs().max().item()
    assert max(advantage_error, kl_error, pg_error, ppo_error) == 0, "Native OPD/PPO input mismatch"
    assert torch.isfinite(train_logp).all() and (train_logp - s).abs().max().item() < 20
    assert _same(debug["train_rollout_abs_diff"], (train_logp - b).abs())
    reference_rho = (train_logp.double() - s.double()).exp()
    reference_advantage = q.double() - s.double()
    reference_pg = torch.maximum(
        -reference_rho * reference_advantage, -reference_rho.clamp(*args.ppo_bounds) * reference_advantage
    )
    sample["retained"] = retained
    sample["token_pass"] = token_pass
    sample["answer_pass"] = answer_pass
    sample["raw_pg"] = raw_pg
    sample["native_sum"] = (raw_pg * retained.float()).sum()
    meta = sample["metadata"]
    return {
        "slot": meta["swe_slot"],
        "sample_index": sample["sample_index"],
        "source_uid": meta["source_uid"],
        "generation_versions": sorted(
            {
                span["version"]
                for version in meta["generation_weight_versions"]
                for name in ("spans", "prefill_spans")
                for span in version[name]
            }
        ),
        "rank": sample["rank"],
        "response_length": sample["response_lengths"],
        "prompt_length": meta["prompt_token_count"],
        "original_tokens": int(mask.sum()),
        "surviving_tokens": int(retained.sum()),
        "answer_ratio": answer_ratio.item(),
        "answer_pass": answer_pass,
        "token_ratio_min": ratio.min().item(),
        "token_ratio_max": ratio.max().item(),
        "token_rejected_tokens": int((mask & ~token_pass).sum()),
        "kl_numerator": (s.double() - q.double())[mask].sum().item(),
        "loss_numerator_float64": reference_pg[retained].sum().item(),
        "advantage_error": advantage_error,
        "opd_reverse_kl_error": kl_error,
        "saved_pg_loss_error": pg_error,
        "saved_ppo_kl_error": ppo_error,
        "rho_min": rho.min().item(),
        "rho_max": rho.max().item(),
        "train_minus_score_max_abs": (train_logp - s).abs().max().item(),
        "rho_clip_active_tokens": int(((rho < args.ppo_bounds[0]) | (rho > args.ppo_bounds[1])).sum()),
    }


def _audit_step(step, shards, args):
    records, rank_sums, rank_counts = [], {}, {}
    for rank, shard in sorted(shards.items()):
        samples = shard["samples"]
        records.extend(_audit_sample(sample, args) for sample in samples)
        data = shard["data"]
        consumed = [i for batch in data["micro_batch_indices"] for i in batch]
        assert sorted(consumed) == list(range(len(samples))), "Partial or duplicate native consumption"
        assert data["num_microbatches"] == [1], "Audit scope is one microbatch per rank"
        rank_sums[str(rank)] = sum(sample["native_sum"] for sample in samples).item()
        rank_counts[str(rank)] = sum(int(sample["loss_masks"].sum()) for sample in samples)
    samples = [sample for shard in shards.values() for sample in shard["samples"]]
    metadata = samples[0]["metadata"]
    for name in (
        "swe_bank",
        "swe_bank_visit",
        "swe_successful_before",
        "current_weight_version",
        "swe_actual_bank_turns",
        "swe_original_bank_tokens",
        "swe_cell",
        "swe_attempt",
    ):
        assert all(sample["metadata"][name] == metadata[name] for sample in samples)
    original = sum(record["original_tokens"] for record in records)
    surviving = sum(record["surviving_tokens"] for record in records)
    numerator = math.fsum(record["kl_numerator"] for record in records)
    loss_numerator = math.fsum(record["loss_numerator_float64"] for record in records)
    native_numerator = math.fsum(rank_sums.values())
    token_rejected = sum(record["token_rejected_tokens"] for record in records)
    answer_rejected = sum(record["original_tokens"] for record in records if not record["answer_pass"])
    overlap = sum(record["token_rejected_tokens"] for record in records if not record["answer_pass"])
    assert original - token_rejected - answer_rejected + overlap == surviving
    assert original == metadata["swe_original_bank_tokens"] and len(records) == metadata["swe_actual_bank_turns"]
    assert len(set(record["response_length"] for record in records)) > 1, "Expected nonuniform lengths"
    return {
        "attempted_rollout_id": step,
        "bank": metadata["swe_bank"],
        "bank_visit": metadata["swe_bank_visit"],
        "successful_before_from_metadata": metadata["swe_successful_before"],
        "current_weight_version_from_metadata": metadata["current_weight_version"],
        "actual_turns": len(records),
        "original_tokens": original,
        "surviving_tokens": surviving,
        "tis_retention": surviving / original,
        "kl_before_tis_numerator": numerator,
        "kl_before_tis_denominator": original,
        "kl_before_tis": numerator / original,
        "token_rejected_tokens": token_rejected,
        "answer_rejected_tokens": answer_rejected,
        "rejection_overlap_tokens": overlap,
        "nonfinite_tokens": 0,
        "loss_numerator_float64": loss_numerator,
        "loss_float64": loss_numerator / original,
        "kl_if_sample_mean": math.fsum(record["kl_numerator"] / record["original_tokens"] for record in records)
        / len(records),
        "native_fp32_rank_loss_sums": rank_sums,
        "native_original_rank_counts": rank_counts,
        "loss_reconstructed_fp32": native_numerator / original,
        "loss_if_tis_ratio_weighted": math.fsum(
            (sample["raw_pg"].double() * (sample["log_probs"].double() - sample["rollout_log_probs"].double()).exp())[
                sample["retained"]
            ]
            .sum()
            .item()
            for sample in samples
        )
        / original,
        "loss_if_survivor_normalized": native_numerator / surviving,
        "loss_if_sample_normalized": math.fsum(
            sample["native_sum"].item() / int(sample["loss_masks"].sum()) for sample in samples
        )
        / len(samples),
        "retained_weights_unique": sorted({int(value) for sample in samples for value in sample["retained"].tolist()}),
        "samples": sorted(records, key=lambda record: record["slot"]),
    }


def _replay_identity(steps):
    visits = {}
    for step, shards in sorted(steps.items()):
        samples = [sample for shard in shards.values() for sample in shard["samples"]]
        visits.setdefault(samples[0]["metadata"]["swe_bank"], []).append((step, {_key(s): s for s in samples}))
    comparisons = []
    for bank, bank_visits in visits.items():
        first_step, first = bank_visits[0]
        for step, current in bank_visits[1:]:
            assert first.keys() == current.keys(), "Replay membership changed"
            for key in sorted(first):
                old, new = first[key], current[key]
                frozen = {
                    name: _same(old[name], new[name])
                    for name in ("tokens", "loss_masks", "teacher_log_probs", "rollout_log_probs")
                }
                assert all(frozen.values())
                for name in (
                    "generation_weight_versions",
                    "swe_teacher_identity",
                    "prompt_sha256",
                    "completion_sha256",
                ):
                    assert old["metadata"][name] == new["metadata"][name]
                changed = int((new["log_probs"] != old["log_probs"]).sum())
                assert changed > 0, "No fresh student-score evidence for this sample"
                comparisons.append(
                    {
                        "bank": bank,
                        "first_step": first_step,
                        "replay_step": step,
                        "slot": key[2],
                        "source_uid": key[3],
                        "sample_index": key[4],
                        "frozen": frozen,
                        "student_changed_tokens": changed,
                        "student_max_abs_change": (new["log_probs"] - old["log_probs"]).abs().max().item(),
                        "advantage_changed_tokens": int((new["advantages"] != old["advantages"]).sum()),
                        "survivor_mask_changed_tokens": int((new["retained"] != old["retained"]).sum()),
                    }
                )
    return comparisons


def _completion_rkl_scope(steps, replay):
    """Assert the saved RKL statistic spans completion tokens only, with no weighting.

    The native response tensors are length ``response_length``; the prompt prefix
    has no saved score entries, and the numerator/denominator are taken over the
    original completion mask. Label alignment is one token: the logits row at
    absolute index ``prompt_length - 1`` predicts the first completion token.
    """
    records = []
    for step, shards in sorted(steps.items()):
        per_step = []
        for rank, shard in sorted(shards.items()):
            for sample in shard["samples"]:
                meta = sample["metadata"]
                prompt, response, total = meta["prompt_token_count"], sample["response_lengths"], sample["total_lengths"]
                mask = sample["loss_masks"].bool()
                assert prompt > 0 and total == prompt + response == len(sample["tokens"])
                assert response == meta["completion_token_count"]
                for name in ("log_probs", "teacher_log_probs", "rollout_log_probs", "advantages", "opd_reverse_kl"):
                    assert sample[name].numel() == response, (step, meta["swe_slot"], name)
                assert mask.numel() == response and mask.any()
                first = int(mask.nonzero()[0])
                delta = sample["log_probs"].double() - sample["teacher_log_probs"].double()
                masked_sum = delta[mask].sum()
                # No prompt position can contribute: there are exactly `response`
                # score entries, one per completion token, and the mask is the
                # completion's original eligible mask. The only applied weight is
                # the 0/1 mask itself; there is no behavior/student ratio factor.
                assert masked_sum.item() == (delta * mask).sum().item()
                # The loss path sums the training-forward log probs against the
                # frozen teacher; verify that exact numerator on the same mask.
                train_delta = sample["debug"]["train_log_probs"].double() - sample["teacher_log_probs"].double()
                assert train_delta[mask].sum().item() == masked_sum.item()
                assert int(mask.sum()) <= response < total
                per_step.append(
                    {
                        "rank": rank,
                        "slot": meta["swe_slot"],
                        "sample_index": sample["sample_index"],
                        "source_uid": meta["source_uid"],
                        "prompt_tokens": prompt,
                        "completion_tokens": response,
                        "total_tokens": total,
                        "original_mask_tokens": int(mask.sum()),
                        "first_masked_response_index": first,
                        "first_target_absolute_index": prompt + first,
                        "first_target_token_id": int(sample["tokens"][prompt + first]),
                        "scored_absolute_range": [prompt, total - 1],
                        "saved_response_scores": int(sample["log_probs"].numel()),
                        "prompt_tokens_scored": 0,
                        "numerator_completion_masked": masked_sum.item(),
                        "numerator_matches_train_forward": train_delta[mask].sum().item() == masked_sum.item(),
                    }
                )
        meta = shards[next(iter(shards))]["samples"][0]["metadata"]
        original = sum(item["original_mask_tokens"] for item in per_step)
        completion = sum(item["completion_tokens"] for item in per_step)
        prompt = sum(item["prompt_tokens"] for item in per_step)
        numerator = math.fsum(item["numerator_completion_masked"] for item in per_step)
        assert original == completion == sum(item["saved_response_scores"] for item in per_step)
        assert completion < prompt + completion
        records.append(
            {
                "attempted_rollout_id": step,
                "bank": meta["swe_bank"],
                "bank_visit": meta["swe_bank_visit"],
                "aggregate": {
                    "prompt_tokens_excluded": prompt,
                    "completion_tokens": completion,
                    "original_mask_tokens": original,
                    "saved_response_scores": completion,
                    "numerator_completion_masked": numerator,
                    "denominator": original,
                    "denominator_is_completion_only": True,
                    "weighting": "none: each original-mask-1 completion token contributes once; no student/behavior ratio",
                },
                "samples": sorted(per_step, key=lambda item: item["slot"]),
            }
        )
    bank0 = [item for item in replay if item["bank"] == 0 and item["first_step"] == 0 and item["replay_step"] == 1]
    assert len(bank0) == 8
    return {
        "statistic": "sampled current-student minus frozen-teacher log-prob mean over the original eligible completion mask (pre-TIS)",
        "scored_positions": "completion tokens only; absolute indices [prompt_length, total_length-1]",
        "label_alignment": "one-token autoregressive shift: logits row prompt_length-1 predicts completion token at index prompt_length",
        "fixed_completion_vs_exact_expectation": (
            "This is an empirical sampled-token statistic on each frozen completion, recomputed by the current student at every visit. "
            "It is not the full current-policy expectation over all possible continuations and not an importance-weighted correction of the behavior sample."
        ),
        "fresh_student_evidence": (
            "Saved log_probs are the per-visit actor scoring pass: they differ from generation-time rollout_log_probs on all eight bank0 samples "
            "at visit1 (same weights version) and again at visit2, while tokens, masks, teacher, behavior, teacher identity and completion SHA256 "
            "are exactly frozen. The KL numerator is the training-forward log-prob sum and equals the independently scored value here."
        ),
        "source_contract": [
            "miles/backends/training_utils/data/context_parallel.py:99-112 (_response_rows_without_cp: rows [prompt_length-1, total_length-1), tokens[-response_length:])",
            "miles/backends/training_utils/data/context_parallel.py:565-580 (slice_log_prob_with_cp asserts len == response_length; CP1 returns unchanged)",
            "miles/backends/training_utils/data/context_parallel.py:320-342 (get_local_response_loss_masks returns the response mask at CP1)",
            "miles/backends/training_utils/loss/hub/logit_processors.py:62-131 (response logits/tokens chunks; 156-232 _torch log probs)",
            "miles/rollout/on_policy_distillation.py:181-183,363-388 (_teacher_sampled_log_probs trims SGLang input_token_logprobs to the completion tail after the placeholder)",
            "tests/manual/agent_opd/swe_replay.py:82-131,273-290 (seal/materialize fix tokens+teacher+behavior+mask; teacher token-id match validation)",
            "tests/manual/agent_opd/swe_replay.py:421-422 (training protocol forbids skip_actor_forward_only/use_rollout_logprobs: fresh actor scoring each visit)",
            "miles/backends/megatron_utils/actor.py:924-940 (fresh actor log-prob pass stored as rollout_data log_probs before advantages)",
            "tests/manual/agent_opd/swe_tis.py:61-80,119 (token_sums over the local original response mask; no ratio weight)",
        ],
        "teacher_token_id_receipt_downloaded": False,
        "steps": records,
        "bank0_visit2_vs_visit1": bank0,
    }


def _rejected_examples(steps):
    examples = {}
    for step, shards in sorted(steps.items()):
        for shard in shards.values():
            for sample in shard["samples"]:
                mask = sample["loss_masks"].bool()
                reasons = {
                    "token_only": mask & ~sample["token_pass"] & sample["answer_pass"],
                    "answer_only": mask & sample["token_pass"] & (not sample["answer_pass"]),
                    "both_layers": mask & ~sample["token_pass"] & (not sample["answer_pass"]),
                }
                for reason, rejected in reasons.items():
                    if reason in examples or not rejected.any():
                        continue
                    i = int(rejected.nonzero()[0])
                    meta = sample["metadata"]
                    s, b, q = (
                        sample[name][i].item() for name in ("log_probs", "rollout_log_probs", "teacher_log_probs")
                    )
                    examples[reason] = {
                        "step": step,
                        "bank": meta["swe_bank"],
                        "visit": meta["swe_bank_visit"],
                        "rank": sample["rank"],
                        "slot": meta["swe_slot"],
                        "source_uid": meta["source_uid"],
                        "response_token_index": i,
                        "absolute_token_index": meta["prompt_token_count"] + i,
                        "token_id": int(sample["tokens"][meta["prompt_token_count"] + i]),
                        "s": s,
                        "b": b,
                        "q": q,
                        "l": sample["debug"]["train_log_probs"][i].item(),
                        "tis_token_ratio": math.exp(s - b),
                        "answer_pass": sample["answer_pass"],
                        "native_raw_pg_loss": sample["saved_pg_loss"][i].item(),
                        "binary_weight": 0,
                        "reconstructed_masked_pg_loss": 0,
                    }
    assert "token_only" in examples and "answer_only" in examples and "both_layers" in examples
    return examples


def _compare_updates(root, computed, tolerance, expected_lr):
    rows = [json.loads(line) for line in (root / "updates.jsonl").read_text().splitlines() if line.strip()]
    keyed = {row["attempted_rollout_id"]: row for row in rows}
    assert len(keyed) == len(rows) == len(computed), "Update receipt coverage mismatch"
    observed = []
    for item in computed:
        row = keyed[item["attempted_rollout_id"]]
        errors = {}
        for name in (
            "bank",
            "bank_visit",
            "actual_turns",
            "original_tokens",
            "surviving_tokens",
            "kl_before_tis_denominator",
            "token_rejected_tokens",
            "answer_rejected_tokens",
            "nonfinite_tokens",
        ):
            assert item[name] == row[name], (name, item[name], row[name])
        for name in ("kl_before_tis_numerator", "kl_before_tis", "tis_retention"):
            errors[name] = item[name] - row[name]
            assert abs(errors[name]) <= tolerance
        errors["loss_float64"] = item["loss_float64"] - row["loss"]
        errors["loss_reconstructed_fp32"] = item["loss_reconstructed_fp32"] - row["loss"]
        assert abs(errors["loss_reconstructed_fp32"]) <= tolerance
        assert row["update"] == row["successful_updates"] == item["successful_before_from_metadata"] + 1
        assert row["native_attempted_count"] == item["attempted_rollout_id"] + 1
        assert row["native_skipped_count"] == 0 and row["update_successful"]
        assert row["current_weight_version"] == item["current_weight_version_from_metadata"]
        assert row["lr"] and all(lr == expected_lr for lr in row["lr"])
        item["receipt_errors"] = errors
        item["receipt_loss"] = row["loss"]
        item["implied_denominator_from_loss"] = math.fsum(item["native_fp32_rank_loss_sums"].values()) / row["loss"]
        observed.append(
            {
                name: row[name]
                for name in (
                    "update",
                    "successful_updates",
                    "native_attempted_count",
                    "native_skipped_count",
                    "update_successful",
                    "lr",
                    "run_kind",
                    "protocol",
                    "current_weight_version",
                )
            }
        )
    return observed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ranks", required=True, type=int, nargs="+")
    parser.add_argument("--token-bounds", required=True, type=float, nargs=2)
    parser.add_argument("--answer-bounds", required=True, type=float, nargs=2)
    parser.add_argument("--ppo-bounds", required=True, type=float, nargs=2)
    parser.add_argument("--memory-gib", required=True, type=int)
    parser.add_argument("--expected-lr", required=True, type=float)
    parser.add_argument("--loss-tolerance", type=float, default=1e-8)
    args = parser.parse_args()
    memory = args.memory_gib * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    # Load torch only after the process memory limit is in place.
    import torch

    torch.set_num_threads(1)
    steps, training_files = _load_training(args.root, args.ranks)
    debug_files = _match_debug(args.root, steps)
    computed = [_audit_step(step, shards, args) for step, shards in sorted(steps.items())]
    replay = _replay_identity(steps)
    completion_scope = _completion_rkl_scope(steps, replay)
    for scope_step, computed_step in zip(completion_scope["steps"], computed, strict=True):
        assert scope_step["attempted_rollout_id"] == computed_step["attempted_rollout_id"]
        assert scope_step["aggregate"]["numerator_completion_masked"] == computed_step["kl_before_tis_numerator"]
        assert scope_step["aggregate"]["denominator"] == computed_step["kl_before_tis_denominator"]
    examples = _rejected_examples(steps)
    # Receipts are deliberately read only after all numerical reconstruction.
    observed = _compare_updates(args.root, computed, args.loss_tolerance, args.expected_lr)
    first_shard = next(iter(next(iter(steps.values())).values()))
    first_sample = first_shard["samples"][0]
    result = {
        "task_id": "T02-ACTUAL-AUDIT",
        "status": "NUMERICAL_PASS_WITH_EXPLICIT_UNVERIFIED_SEAMS",
        "data_root": str(args.root),
        "training_files": training_files,
        "policy_loss_debug_files": debug_files,
        "comparison_only_source": str(args.root / "updates.jsonl"),
        "command": [sys.executable, *sys.argv],
        "python": platform.python_version(),
        "torch": torch.__version__,
        "memory_limit_gib": args.memory_gib,
        "maximum_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "bounds": {"token": args.token_bounds, "answer": args.answer_bounds, "ppo_ratio": args.ppo_bounds},
        "loss_absolute_tolerance": args.loss_tolerance,
        "topology": {
            "dumped_global_ranks": args.ranks,
            "cp_size_from_dumps": 1,
            "tp2_dp4": "Parent-supplied topology; tensor identity and complete disjoint sample coverage verified",
        },
        "debug_alignment": "Unique exact old-score/behavior/advantage/mask/length match to metadata-indexed samples, not filename/call order",
        "native_tensor_schema": {
            "rollout_data_keys": sorted(first_shard["data"]),
            "policy_loss_debug_sample_keys": sorted(first_sample["debug"]),
            "response_tensor_dtypes": {
                name: str(first_sample[name].dtype)
                for name in ("loss_masks", "log_probs", "teacher_log_probs", "rollout_log_probs", "advantages")
            },
            "all_response_shapes_checked": "Each tensor length equals its metadata-matched response_length; original tokens exclude prompt tokens",
            "saved_training_logprob_requires_grad": first_sample["debug"]["train_log_probs"].requires_grad,
            "saved_grad_flag_limit": "The native dumper detaches before saving; this flag does not describe the original live graph",
        },
        "updates": computed,
        "replay_identity": replay,
        "completion_rkl_scope": completion_scope,
        "rejected_examples": examples,
        "observed_native_boundary_receipts": observed,
        "verified": [
            "All saved original-mask student-minus-teacher KL sums and denominators independently recomputed",
            "D4 binary token and answer layers, overlap and nonuniform-length token weighting reconstructed",
            "Saved native advantages=q-s, opd_reverse_kl=s-q, pre-TIS PPO token loss and PPO KL match exactly",
            "Masked PPO scalar divided by global original tokens matches native receipt within float32 reduction tolerance",
            "Canonical identity, tokens, masks, teacher, behavior and generation version frozen across replay; student values refreshed",
            "Completion-only RKL scope: exactly one saved score per completion token, no prompt-position entries, numerator/denominator over the original completion mask with no importance weight",
            "Metadata and native-boundary receipts agree on bank0 visits1/2 then bank1 visit1, successful1/2/3, skipped0, LR2e-6",
        ],
        "unverified_seams": [
            "No saved actual logprob/logit/parameter gradients, live autograd graph, finalizer token-count tensor or collective buffers; backend gradient scaling/detach cannot be measured from these detached dumps",
            "Healthy post-TIS native masks and final reduced loss tensors are not among downloads; masked reconstruction agrees with receipt but is not direct saved-mask/gradient observation",
            "All native training logprobs equal independent actor scores (rho=1); actual clipping branches are unexercised",
            "LR and successful/skipped counters are observed native-hook receipts, not independently verified optimizer state, betas/epsilon/weight-decay parameter groups or scheduler/optimizer continuity",
            "Only A/r256, 8 turns and three smoke updates; no 256-turn capacity, 50-visit bank, 200-update formal schedule, other cells or Ticket02 completion",
        ],
        "backend_scaling_inference": "Inspected Miles objective returns original token count and unnormalized CP1 loss to Megatron; absent backward/finalizer artifacts, effective global 1/N gradient scaling remains an inference",
    }
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": str(args.output),
                "updates": [
                    {
                        name: row[name]
                        for name in (
                            "bank",
                            "bank_visit",
                            "original_tokens",
                            "surviving_tokens",
                            "kl_before_tis",
                            "loss_reconstructed_fp32",
                        )
                    }
                    for row in computed
                ],
            }
        )
    )


if __name__ == "__main__":
    main()
