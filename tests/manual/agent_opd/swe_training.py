"""Native optimizer acknowledgement and exact distributed SWE training receipts."""

import json
import logging
import math
import time
from dataclasses import dataclass, field
from numbers import Integral
from pathlib import Path

import torch
import torch.distributed as dist

from miles.backends.training_utils.parallel import get_parallel_state
from miles.utils.retry_utils import NonRetryableError
from tests.manual.agent_opd.swe_replay import SweReplayConfig, append_record, training_protocol

logger = logging.getLogger(__name__)


class ZeroTISSurvivors(NonRetryableError):
    """Approved D7 stop: the global real training mask has no surviving token."""


@dataclass
class _TrainingReceipt:
    successful: int = 0
    attempted: int = 0
    pending: dict = field(default_factory=dict)


_receipts: dict[tuple[str, str, str], _TrainingReceipt] = {}


def reduce_training_masks(losses, *, device, contribute: bool, count_turns: bool, expected_microbatches: int):
    """All ranks join before rejecting an unavailable mandatory native signal."""
    device = torch.device(device)
    total = torch.zeros(4, dtype=torch.int64, device=device)
    if contribute:
        total[-1] = int(not isinstance(losses, list) or len(losses) != expected_microbatches)
        for item in losses if isinstance(losses, list) else []:
            counts = item.get("training_mask_counts") if isinstance(item, dict) else None
            if not isinstance(counts, torch.Tensor) or counts.shape != (3,) or counts.dtype != torch.int64 or counts.device != device:
                total[-1] += 1
                continue
            total[:2] += counts[:2]
            if count_turns:
                total[2] += counts[2]
    if dist.is_initialized():
        dist.all_reduce(total, op=dist.ReduceOp.SUM)
    if total[-1].item():
        raise RuntimeError("Native actual training-mask counts are unavailable; D7 is unknown, not zero")
    return dict(zip(("original_tokens", "surviving_tokens", "actual_turns"), total[:3].tolist(), strict=True))


def reduce_token_sums(losses, *, device, contribute: bool, expected_microbatches: int):
    """Optional additive diagnostics; an incomplete global sum remains unknown."""
    names = (
        "kl_before_tis_numerator", "nonfinite_tokens",
        "token_rejected_tokens", "answer_rejected_tokens", "loss_numerator",
    )
    device = torch.device(device)
    total = torch.zeros(2 * len(names) + 1, dtype=torch.float64, device=device)
    try:
        if contribute:
            _add_token_sums(total, losses, names, device, expected_microbatches)
    except Exception:
        # The optional payload may be malformed on just one rank. Still join
        # the same collective, making all diagnostics unknown on every rank.
        total.zero_()
        total[len(names):] = 1
    if dist.is_initialized():
        dist.all_reduce(total, op=dist.ReduceOp.SUM)
    result = {name: _finite_or_none(total[i].item()) if total[len(names) + i].item() == 0 else None
              for i, name in enumerate(names)}
    result["diagnostics_verified"] = all(result[name] is not None for name in names)
    result["unverified_diagnostics"] = [name for name in names if result[name] is None]
    result["mask_evidence_verified"] = total[-1].item() == 0
    return result


def _add_token_sums(total, losses, names, device, expected_microbatches):
    total[len(names):-1] = int(len(losses) != expected_microbatches)
    total[-1] = int(len(losses) != expected_microbatches)
    for item in losses:
        sums = item.get("token_sums")
        sums = sums if isinstance(sums, dict) else {}
        keys, values = item.get("keys", []), item.get("values")
        loss = None
        if isinstance(keys, list) and "loss" in keys and isinstance(values, torch.Tensor) and values.ndim == 1:
            index = keys.index("loss") + 1
            if index < len(values):
                loss = values[index]
        for index, name in enumerate(names):
            value = loss if name == "loss_numerator" else sums.get(name)
            if not isinstance(value, torch.Tensor) or value.numel() != 1 or value.device != device:
                total[len(names) + index] += 1
            else:
                total[index] += value.detach().double().reshape(())
        total[-1] += int(not isinstance(item.get("mask_evidence"), dict))


def _estimator_label(config):
    """The single owner of labels for estimators implemented by native OPD."""
    top_k = config["opd_log_prob_top_k"]
    if type(top_k) is not int or top_k < 0:
        raise ValueError("Unsupported native OPD top-k configuration")
    if top_k == 0:
        return "sampled_current_student_minus_frozen_teacher_on_original_behavior_tokens"
    return f"native_top{top_k}_{config['opd_top_k_strategy']}_{config['opd_reward_weight_mode']}"


def _turn_sum_payload(losses, rollout_data, *, device, expected_microbatches, cp_rank, cp_size):
    indices, metadata = rollout_data["sample_indices"], rollout_data["metadata"]
    bank = {}
    estimator = None
    for index, item in zip(indices, metadata, strict=True):
        if isinstance(index, bool) or not isinstance(index, Integral) or index in bank:
            raise ValueError("Duplicate or invalid native bank sample index")
        index = int(index)
        uid = item["source_uid"]
        if not isinstance(uid, str) or not uid:
            raise ValueError("Missing canonical source uid")
        bank[index] = uid
        label = _estimator_label(item["opd_estimator_config"])
        if estimator is not None and label != estimator:
            raise ValueError("Native bank contains inconsistent estimator configuration")
        estimator = label
    if len(losses) != expected_microbatches:
        raise ValueError("Turn sums do not cover the native microbatches")
    sample_indices, tensors = [], []
    for item in losses:
        sums = item["turn_sums"]
        if "error" in sums:
            raise ValueError(sums["error"])
        values = sums["values"]
        if (not isinstance(values, torch.Tensor) or values.ndim != 2 or values.shape[1] != 3
                or values.dtype != torch.float64 or values.device != torch.device(device)):
            raise ValueError("Turn sums require a float64 response-sum tensor on the native device")
        if len(sums["sample_indices"]) != len(values):
            raise ValueError("Turn sums sample indices and rows differ in length")
        sample_indices.extend(sums["sample_indices"])
        tensors.append(values.detach())
    partials = {}
    # One tiny device-to-host copy per update, not one synchronization per turn
    # or microbatch. No response-level tensors enter the ACK.
    for index, row in zip(sample_indices, torch.cat(tensors).cpu().tolist(), strict=True):
        if type(index) is not int or index not in bank or index in partials:
            raise ValueError("Turn sums sample indices do not match native bank membership")
        if not all(math.isfinite(value) for value in row) or row[2] < 0 or not row[2].is_integer():
            raise ValueError("Nonfinite turn sums or invalid original-token count")
        partials[index] = row
    if partials.keys() != bank.keys():
        raise ValueError("Turn sums do not cover the native bank uids")
    return {"bank": bank, "partials": partials, "cp_rank": cp_rank, "cp_size": cp_size, "estimator": estimator}


def _merge_turn_sums(payloads, counts, metadata):
    bank, values, cp_ranks, estimators = {}, {}, {}, set()
    for payload in payloads:
        if not payload:
            continue
        if "error" in payload:
            raise ValueError(payload["error"])
        estimators.add(payload["estimator"])
        for index, uid in payload["bank"].items():
            if index in bank and bank[index] != uid:
                raise ValueError("CP replicas disagree about canonical source uid")
            bank[index] = uid
            ranks = cp_ranks.setdefault(index, set())
            if payload["cp_rank"] in ranks:
                raise ValueError("Duplicate TP/PP or CP contribution for a native sample")
            ranks.add(payload["cp_rank"])
            row = values.setdefault(index, [0.0, 0.0, 0.0])
            for column, value in enumerate(payload["partials"][index]):
                row[column] += value
            if payload["cp_size"] != metadata["cp_size"]:
                raise ValueError("Inconsistent native CP size")
    if len(estimators) != 1:
        raise ValueError("Missing or inconsistent native estimator label")
    if len(set(bank.values())) != len(bank):
        raise ValueError("Native bank contains duplicate canonical source uids")
    if any(ranks != set(range(metadata["cp_size"])) for ranks in cp_ranks.values()):
        raise ValueError("Missing CP partial for a native sample")
    rows = []
    for index in sorted(bank):
        rkl, nll, tokens = values[index]
        if not all(math.isfinite(value) for value in (rkl, nll, tokens)) or tokens <= 0:
            raise ValueError("Nonfinite merged turn sums or empty original target")
        rows.append({"uid": bank[index], "rkl_sum": rkl, "nll_sum": nll, "tokens": int(tokens)})
    original_tokens = sum(row["tokens"] for row in rows)
    if len(rows) != counts["actual_turns"] or len(rows) != metadata["swe_actual_bank_turns"]:
        raise ValueError("Turn-sum row count differs from native actual turns or sealed bank")
    if original_tokens != counts["original_tokens"] or original_tokens != metadata["swe_original_bank_tokens"]:
        raise ValueError("Turn-sum token count differs from native original mask or sealed bank")
    rkl_sum, nll_sum = sum(row["rkl_sum"] for row in rows), sum(row["nll_sum"] for row in rows)
    if not math.isfinite(rkl_sum) or not math.isfinite(nll_sum):
        raise ValueError("Nonfinite macro turn sums")
    return {"turn_sums": rows, "turn_sums_verified": True, "unverified_turn_sums": [],
            "kl_estimator": estimators.pop(),
            "kl_before_tis_numerator": rkl_sum, "nll_before_tis_numerator": nll_sum}


def reduce_turn_sums(losses, rollout_data, counts, *, device, contribute, expected_microbatches, cp_rank, cp_size):
    """One update-level exchange; local auxiliary errors never skip a collective."""
    payload = None
    if contribute:
        try:
            payload = _turn_sum_payload(losses, rollout_data, device=device, expected_microbatches=expected_microbatches,
                                        cp_rank=cp_rank, cp_size=cp_size)
        except Exception as error:
            payload = {"error": f"{type(error).__name__}: {error}"}
    payloads = [payload]
    if dist.is_initialized():
        payloads = [None] * dist.get_world_size()
        dist.all_gather_object(payloads, payload)
    try:
        metadata = {**rollout_data["metadata"][0], "cp_size": cp_size}
        return _merge_turn_sums(payloads, counts, metadata)
    except Exception as error:
        return {"turn_sums": [], "turn_sums_verified": False,
                "unverified_turn_sums": [f"{type(error).__name__}: {error}"], "kl_estimator": None,
                "kl_before_tis_numerator": None, "nll_before_tis_numerator": None}


def _finite_or_none(value):
    return value if math.isfinite(value) else None


def _diagnostic_warning(message):
    try:
        logger.warning(message)
    except Exception:
        pass


def _write_update_receipts(directory, record):
    # Rows travel only in the ACK. The rollout-side profile owns durable rows.
    record = {key: value for key, value in record.items() if key != "turn_sums"}
    for name in ("optimizer_attempts.jsonl", "updates.jsonl"):
        if name == "updates.jsonl" and not record["update_successful"]:
            continue
        try:
            append_record(directory / name, {**record, "update": record["successful_updates"]} if name == "updates.jsonl" else record)
        except Exception:
            _diagnostic_warning("SWE update receipt unverified; native acknowledgement is unaffected")
    try:
        print("SWE_NATIVE_UPDATE", json.dumps(record, allow_nan=False), flush=True)
    except Exception:
        _diagnostic_warning("SWE stdout receipt unverified; native acknowledgement is unaffected")


def _write_trigger_masks(directory, rollout_id, losses):
    # Auxiliary evidence is a soft gate: failure cannot change the D7 verdict.
    try:
        rank = dist.get_rank() if dist.is_initialized() else 0
        evidence = [item["mask_evidence"] for item in losses if isinstance(item.get("mask_evidence"), dict)]
        path = directory / f"zero_tis_rollout_{rollout_id}_rank_{rank}.pt"
        directory.mkdir(parents=True, exist_ok=True)
        torch.save(evidence, path)
    except Exception:
        _diagnostic_warning("D7 mask evidence unverified; the global training-data verdict remains zero")


def optimizer_step(args, *, stage, rollout_id, step_id, data_iterator, model, optimizer, losses_reduced,
                   update_successful):
    """Called collectively at the native optimizer boundary, not by an observer timer."""
    parallel = get_parallel_state()
    if step_id != 0 or len(data_iterator[0].rollout_data["num_microbatches"]) != 1:
        raise ValueError("A SWE bank visit requires exactly one native optimizer attempt")
    if parallel.indep_dp.size != 1:
        raise ValueError("SWE replay requires the accepted native intra-DP topology")
    directory = Path(args.swe_evidence_dir)
    key = (str(directory), args.swe_cell, args.swe_attempt)
    state = _receipts.setdefault(key, _TrainingReceipt())
    device = next(model[0].parameters()).device
    metadata = data_iterator[0].rollout_data["metadata"][0]
    if metadata["swe_successful_before"] != state.successful:
        raise ValueError("The canonical bank visit and native successful count disagree")

    if stage == "before_optimizer":
        counts = reduce_training_masks(
            losses_reduced, device=device, contribute=parallel.is_pp_last_stage and parallel.tp.rank == 0,
            count_turns=parallel.cp.rank == 0, expected_microbatches=data_iterator[0].rollout_data["num_microbatches"][0],
        )
        sums = reduce_token_sums(
            losses_reduced, device=device, contribute=parallel.is_pp_last_stage and parallel.tp.rank == 0,
            expected_microbatches=data_iterator[0].rollout_data["num_microbatches"][0],
        )
        turns = reduce_turn_sums(
            losses_reduced, data_iterator[0].rollout_data, counts, device=device,
            contribute=parallel.is_pp_last_stage and parallel.tp.rank == 0,
            expected_microbatches=data_iterator[0].rollout_data["num_microbatches"][0],
            cp_rank=parallel.cp.rank, cp_size=parallel.cp.size,
        )
        original, surviving = counts["original_tokens"], counts["surviving_tokens"]
        state.pending = {
            "cell": args.swe_cell, "attempt": args.swe_attempt, "attempted_rollout_id": rollout_id,
            "run_kind": args.swe_run_kind, "protocol": args.swe_protocol,
            "bank": metadata["swe_bank"], "bank_visit": metadata["swe_bank_visit"],
            "teacher_identity": args.swe_teacher_identity,
            "generation_weight_versions": metadata["generation_weight_versions"],
            "current_weight_version": metadata["current_weight_version"],
            **turns,
            "kl_direction": "student_minus_teacher",
            "kl_before_tis_denominator": int(original),
            "kl_before_tis": turns["kl_before_tis_numerator"] / original if original and turns["turn_sums_verified"] else None,
            "nll_before_tis": turns["nll_before_tis_numerator"] / original if original and turns["turn_sums_verified"] else None,
            "nll_before_tis_denominator": int(original),
            "original_tokens": int(original), "surviving_tokens": int(surviving),
            "tis_retention": surviving / original if original else None,
            "nonfinite_tokens": sums["nonfinite_tokens"],
            "token_rejected_tokens": sums["token_rejected_tokens"],
            "answer_rejected_tokens": sums["answer_rejected_tokens"],
            "diagnostics_verified": sums["diagnostics_verified"],
            "unverified_diagnostics": sums["unverified_diagnostics"],
            "mask_evidence_verified": sums["mask_evidence_verified"],
            "retained_weight": 1, "effective_weight_sum": int(surviving),
            "loss": sums["loss_numerator"] / original if original and sums["loss_numerator"] is not None else None,
            "lr": [float(p["lr"]) for p in optimizer.param_groups] if optimizer is not None else [],
            "timestamp": time.time(), "successful_updates": state.successful,
        }
        state.pending["actual_turns"] = counts["actual_turns"]
        state.pending["expected_bank_turns"] = metadata["swe_actual_bank_turns"]
        state.pending["expected_bank_tokens"] = metadata["swe_original_bank_tokens"]
        state.pending["bank_membership_verified"] = (
            counts["actual_turns"] == metadata["swe_actual_bank_turns"] and original == metadata["swe_original_bank_tokens"]
        )
        if not state.pending["bank_membership_verified"]:
            _diagnostic_warning("Sealed bank consumption unverified; keep native training healthy and inspect the receipt")
        if not sums["diagnostics_verified"] or not sums["mask_evidence_verified"]:
            _diagnostic_warning("SWE diagnostics unverified; actual global training masks still determine D7")
        if not turns["turn_sums_verified"]:
            _diagnostic_warning(f"SWE turn sums unverified: {turns['unverified_turn_sums']}; native training continues")
        if surviving == 0:
            _write_trigger_masks(directory, rollout_id, losses_reduced)
            if not dist.is_initialized() or dist.get_rank() == 0:
                try:
                    append_record(directory / "failed_batches.jsonl", {
                        **{key: value for key, value in state.pending.items() if key != "turn_sums"},
                        "status": "D7_ZERO_SURVIVORS",
                    })
                except Exception:
                    _diagnostic_warning("D7 trigger receipt unverified; native zero-survivor stop is unchanged")
            raise ZeroTISSurvivors(f"D7: global TIS survivors=0, original_tokens={int(original)}, rollout={rollout_id}")
        return
    if stage != "after_optimizer" or not state.pending:
        raise ValueError("Unknown or unmatched native optimizer boundary")
    flags = torch.tensor([int(update_successful), -int(update_successful)], dtype=torch.int64, device=device)
    if dist.is_initialized():
        dist.all_reduce(flags, op=dist.ReduceOp.MAX)
    if flags[0] != -flags[1]:
        raise RuntimeError("Native ranks disagree about optimizer success")
    state.attempted += 1
    state.successful += int(update_successful)
    record = {**state.pending, "update_successful": bool(update_successful),
              "successful_updates": state.successful, "native_attempted_count": state.attempted,
              "native_skipped_count": state.attempted - state.successful}
    if dist.is_initialized():
        payload = [record]
        dist.broadcast_object_list(payload, src=0, device=device)
        record = payload[0]
    state.pending = {}
    if not dist.is_initialized() or dist.get_rank() == 0:
        _write_update_receipts(directory, record)
    return record


optimizer_step.config_class = SweReplayConfig
optimizer_step.training_protocol = training_protocol
