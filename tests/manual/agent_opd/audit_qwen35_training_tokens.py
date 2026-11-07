"""Collect every-update native training-token evidence without running an optimizer.

Run inside the task-pinned, zero-GPU image with the native run directories mounted:
    python -B -m tests.manual.agent_opd.audit_qwen35_training_tokens \
        --config TASK/training_config_h200.json \
        --run A=RUN_A --run B=RUN_B \
        --launch A=LOCAL_A/launch.json --launch B=LOCAL_B/launch.json \
        --report TASK/evidence/training-token-audit.json

The native score metadata, not global-rank arithmetic or filenames, identifies
DP/TP/CP/PP ranks. Policy debug calls have no sample/rollout IDs: their payload
counter orders calls, while exact original-mask, length, old-logprob,
rollout-logprob and advantage equality binds each call to consumed train rows.
Training shards do not persist source metadata. Source identities are joined
from the original rollout only after native sample indices, full tokens,
original masks, rollout execution IDs and complete weight-version spans match.
Missing or ambiguous evidence is INCOMPLETE. No post-TIS survivor count is
invented. A complete audit is not a replay of Megatron's gradient finalizer.
"""

import argparse
import copy
import json
import sys
from collections import Counter, defaultdict
from contextlib import contextmanager
from pathlib import Path

import torch
from tests.manual.agent_opd.inspect_qwen35 import (
    _decode_version,
    _issue,
    _mask,
    _population,
    _publication_receipts,
    _require,
    _response_positions,
    _score_slices,
    _source_check,
    _vector,
)

from miles.backends.training_utils import parallel
from miles.backends.training_utils.data.context_parallel import get_local_response_loss_masks
from miles.backends.training_utils.data.rollout import _prepare_loss_masks
from miles.backends.training_utils.loss.objective import count_loss_tokens
from miles.backends.training_utils.parallel import ParallelState
from miles.utils.audit_utils.event_logger.logger import EventReader
from miles.utils.audit_utils.event_logger.models import (
    InferenceEngineChecksumCollectionFailedEvent,
    InferenceEngineWeightChecksumEvent,
    TrainGroupStepEndEvent,
    WeightUpdateResultEvent,
)
from miles.utils.ft_utils.process_group_utils import GroupInfo


@contextmanager
def _offline_parallel(meta):
    """Supply recorded dimensions to native pure mask functions; no collectives."""
    previous = parallel._parallel_state
    unit = GroupInfo(rank=0, size=1, group=None)
    cp = GroupInfo(rank=meta["cp_rank"], size=meta["cp_size"], group=None)
    state = ParallelState(
        intra_dp=unit,
        intra_dp_cp=unit,
        cp=cp,
        tp=unit,
        pp=unit,
        ep=unit,
        etp=unit,
        indep_dp=unit,
    )
    parallel.set_parallel_state(state)
    try:
        yield
    finally:
        parallel._parallel_state = previous


def _load(path):
    return torch.load(path, map_location="cpu", weights_only=False)


def _option(argv, name):
    _require(argv.count(name) == 1, "launch_option_missing_or_duplicate", name)
    index = argv.index(name) + 1
    _require(index < len(argv) and not argv[index].startswith("--"), "launch_value_missing", name)
    return argv[index]


def _contract(config, pair, run, launch):
    argv = launch["training_argv"]
    student = config["pairs"][pair]["student"]
    steps = int(_option(argv, "--num-rollout"))
    batch = int(_option(argv, "--global-batch-size"))
    _require(
        launch["pair"] == pair and Path(launch["output_dir"]) == run,
        "launch_run_mismatch",
        "Native launch must identify the exact supplied run",
    )
    _require(steps == config["num_rollout"] == 100, "step_budget_mismatch", "This task has 100 accepted positions")
    _require(
        batch == int(_option(argv, "--rollout-batch-size")) == 8 and int(_option(argv, "--n-samples-per-prompt")) == 1,
        "completion_budget_mismatch",
        "Need eight fresh completions and one update per rollout",
    )
    _require(
        "--calculate-per-token-loss" in argv and "--use-tis" in argv,
        "native_loss_contract_missing",
        "Per-token loss and TIS must be enabled",
    )
    _require(
        "--use-dynamic-global-batch-size" not in argv and "--use-rollout-logprobs" not in argv,
        "unsupported_loss_contract",
        "This collector binds the task's fixed batch and trainer-scored old policy",
    )
    tp = int(_option(argv, "--tensor-model-parallel-size"))
    cp = int(_option(argv, "--context-parallel-size"))
    pp = int(_option(argv, "--pipeline-model-parallel-size"))
    world = student["nodes"] * student["gpus_per_node"]
    _require(
        tp == student["tp_size"] and world % (tp * cp * pp) == 0,
        "launch_topology_mismatch",
        "Resolved launch and selected resource config disagree",
    )
    return {
        "steps": steps,
        "batch": batch,
        "tp_size": tp,
        "cp_size": cp,
        "pp_size": pp,
        "dp_size": world // (tp * cp * pp),
        "source_commit": launch["source_commit"],
        "training_argv": argv,
    }


def _rank_metadata(run, contract):
    # score_log_probs records explicit topology; train_dump and policy_debug
    # intentionally suppress TP replicas but do not repeat that topology.
    paths = sorted((run / "train_data").glob("eval_monitor_0_*.pt"))
    indexed, issues = _score_slices(paths, 0, "eval_monitor_0")
    _require(not issues, "rank_metadata_incomplete", json.dumps(issues))
    ranks = {}
    for slices in indexed.values():
        for batch, _, _ in slices:
            meta = batch["metadata"]
            for dimension in ("dp_size", "tp_size", "cp_size", "pp_size"):
                _require(meta[dimension] == contract[dimension], "rank_config_mismatch", dimension)
            ranks[meta["rank"]] = meta
    _require(
        len({meta["cell_index"] for meta in ranks.values()}) == 1,
        "unsupported_multiple_cells",
        "This task has one student cell",
    )
    _require(
        len(ranks) == contract["dp_size"] * contract["cp_size"],
        "rank_metadata_incomplete",
        "Every authoritative DP/CP rank must be present",
    )
    _require(
        not any(meta["allgather_cp"] for meta in ranks.values()),
        "unsupported_allgather_cp",
        "The dump lacks sufficient all-gather microbatch position metadata",
    )
    return ranks, [str(path) for path in paths]


def _publications(run, steps):
    events = EventReader(
        run / "events",
        strict=True,
        event_types=(
            WeightUpdateResultEvent,
            TrainGroupStepEndEvent,
            InferenceEngineWeightChecksumEvent,
            InferenceEngineChecksumCollectionFailedEvent,
        ),
    ).read()
    receipts = _publication_receipts(events)
    planned = receipts["planned"]
    _require(
        [event.rollout_id for event in planned] == list(range(steps)),
        "publication_step_coverage",
        "Need exactly 100 native planned publications",
    )
    rows = {}
    previous = receipts["baseline"].published_version
    for event in planned:
        attempts = [
            item
            for item in events
            if isinstance(item, TrainGroupStepEndEvent)
            and item.source == event.source
            and item.role == "actor"
            and item.rollout_id == event.rollout_id
        ]
        _require(
            len(attempts) == 1,
            "ambiguous_train_attempts",
            "Overwritten train dumps cannot bind multiple training attempts",
        )
        delta = receipts["deltas"][event.debug_weight_update_id]
        _require(delta == 1, "accepted_update_not_successful", str(event.rollout_id))
        rows[event.rollout_id] = {
            "consumed_weight_version": str(previous),
            "published_weight_version": event.published_version,
            "consumed_weight_version_basis": "previous_native_publication_counter",
            "optimizer_counter_delta": delta,
            "publication_id": event.debug_weight_update_id,
            "attempt": attempts[0].attempt,
        }
        previous = event.published_version
    return rows, {
        "baseline_version": receipts["baseline"].published_version,
        "successful_updates": sum(row["optimizer_counter_delta"] for row in rows.values()),
        "skipped_updates": 0,
        "final_version": previous,
        "restoration_publications": len(receipts["restorations"]),
    }


def _debug_inventory(run, ranks):
    indexed = defaultdict(list)
    for path in sorted((run / "policy_loss_debug").glob("*.pt")):
        dump = _load(path)
        rank, call = dump["rank"], dump["call"]
        _require(rank in ranks, "debug_rank_unbound", str(path))
        _require(type(call) is int and call >= 0, "debug_call_invalid", str(path))
        indexed[rank].append((call, path))
    _require(set(indexed) == set(ranks), "debug_rank_missing", str(set(ranks) - set(indexed)))
    for rank, calls in indexed.items():
        calls.sort(key=lambda item: item[0])
        _require(
            [call for call, _ in calls] == list(range(len(calls))),
            "debug_call_coverage",
            f"Rank {rank}: duplicate, reset or missing payload counter",
        )
    return indexed


def _equal(left, right):
    left, right = torch.as_tensor(left).float(), torch.as_tensor(right).float()
    return left.shape == right.shape and bool(((left == right) | (left.isnan() & right.isnan())).all())


def _match_debug(sample, candidates):
    matches = [
        row
        for row in candidates
        if sample["total_length"] == row["total_length"]
        and sample["response_length"] == row["response_length"]
        and _equal(sample["local_loss_mask"], row["local_mask"])
        and all(
            _equal(sample[debug], row[field])
            for debug, field in (
                ("old_log_probs", "log_probs"),
                ("rollout_log_probs", "rollout_log_probs"),
                ("advantages", "advantages"),
            )
        )
    ]
    _require(
        len(matches) == 1,
        "debug_sample_binding_ambiguous",
        f"Exact pre-TIS length/mask/old/rollout/advantage binding matched {len(matches)} train rows",
    )
    return matches[0]


def _finite_coverage(value, mask):
    value = _vector(value, "native response values")
    _require(len(value) == len(mask), "native_response_coverage", "Values do not cover the recorded CP response slice")
    invalid = ~torch.isfinite(value)
    return {
        "eligible_positions": int(mask.sum()),
        "masked_positions": int((~mask).sum()),
        "nonfinite_eligible": int((invalid & mask).sum()),
        "nonfinite_masked": int((invalid & ~mask).sum()),
    }


def _training_row(batch, index, raw, meta, local_mask):
    """Validate native consumed fields before joining original-rollout provenance."""
    identity = int(batch["sample_indices"][index])
    mask = _mask(raw)
    _require(identity == raw["index"], "consumed_sample_index_mismatch", str(identity))
    _require(
        torch.equal(
            _vector(batch["tokens"][index], "train tokens", dtype=torch.int64),
            _vector(raw["tokens"], "raw tokens", dtype=torch.int64),
        ),
        "consumed_token_mismatch",
        str(identity),
    )
    _require(_equal(batch["loss_masks"][index], mask), "consumed_original_mask_mismatch", str(identity))
    # train_data_conversion.py:121 owns this native execution-ID convention;
    # it is not the outer training schedule's rollout_id.
    execution_id = raw["rollout_id"] if raw["rollout_id"] is not None else raw["index"]
    _require(batch["rollout_ids"][index] == execution_id, "consumed_rollout_execution_id_mismatch", str(identity))
    _require(
        batch["weight_versions"][index] == raw["weight_versions"],
        "consumed_weight_version_spans_mismatch",
        str(identity),
    )
    total, response = batch["total_lengths"][index], batch["response_lengths"][index]
    _require(
        total == len(raw["tokens"]) and response == raw["response_length"], "consumed_boundary_mismatch", str(identity)
    )
    version = _decode_version(
        {"tokens": batch["tokens"][index], "weight_versions": batch["weight_versions"][index]}, total - response
    )
    _require(version == _decode_version(raw, total - response), "consumed_version_mismatch", str(identity))
    _require(
        int(batch["rollout_mask_sums"][index]) == int(mask.sum()),
        "rollout_denominator_mismatch",
        "Single-turn original mask sum differs",
    )
    maximum = batch["max_seq_lens"][index] if "max_seq_lens" in batch else None
    positions = _response_positions(meta, total, response, maximum)
    local_mask = _vector(local_mask, "native local mask").bool()
    _require(torch.equal(local_mask, mask[positions]), "native_local_mask_mismatch", str(identity))
    _require(
        _equal(
            batch["rollout_log_probs"][index], _vector(raw["rollout_log_probs"], "original decode scores")[positions]
        ),
        "consumed_decode_scores_mismatch",
        str(identity),
    )
    row = {
        "sample_index": identity,
        "total_length": total,
        "response_length": response,
        "mask": _vector(batch["loss_masks"][index], "original mask"),
        "local_mask": local_mask,
        "response_positions": positions,
        "native_rollout_execution_id": execution_id,
        "generation_consumed_weight_version": version,
        "source_identity_binding_basis": "verified_original_rollout_join",
        "native_train_source_metadata_persisted": False,
    }
    row.update({field: batch[field][index] for field in ("log_probs", "rollout_log_probs", "advantages")})
    row["input_coverage"] = {
        field: _finite_coverage(batch[field][index], local_mask)
        for field in ("log_probs", "rollout_log_probs", "teacher_log_probs", "advantages")
    }
    return row


def _training_shards(run, step, ranks, samples):
    paths = sorted((run / "train_data").glob(f"{step}_*.pt"))
    shards = {}
    for path in paths:
        dump = _load(path)
        rank = dump["rank"]
        _require(dump["rollout_id"] == step and rank in ranks and rank not in shards, "train_shard_binding", str(path))
        meta = ranks[rank]
        _require(
            all(dump[key] == meta[key] for key in ("cp_rank", "cp_size", "qkv_format")),
            "train_rank_metadata_mismatch",
            str(path),
        )
        batch = dump["rollout_data"]
        indices = [int(index) for index in batch["sample_indices"]]
        fields = (
            "tokens",
            "loss_masks",
            "total_lengths",
            "response_lengths",
            "rollout_ids",
            "weight_versions",
            "log_probs",
            "rollout_log_probs",
            "teacher_log_probs",
            "advantages",
            "rollout_mask_sums",
        )
        _require(all(len(batch[field]) == len(indices) for field in fields), "train_row_coverage", str(path))
        _require(len(indices) == len(set(indices)), "duplicate_train_sample", str(path))
        with _offline_parallel(meta):
            local_masks = get_local_response_loss_masks(
                batch["total_lengths"],
                batch["response_lengths"],
                batch["loss_masks"],
                meta["qkv_format"],
                batch.get("max_seq_lens"),
            )
        rows = []
        for index, identity in enumerate(indices):
            _require(identity in samples, "unexpected_train_sample", str(identity))
            rows.append(_training_row(batch, index, samples[identity], meta, local_masks[index]))
        schedule = [[indices[index] for index in micro] for micro in batch["micro_batch_indices"]]
        _require(
            batch["num_microbatches"] == [len(schedule)]
            and sorted(identity for micro in schedule for identity in micro) == sorted(indices),
            "native_microbatch_schedule_mismatch",
            str(path),
        )
        shards[rank] = {
            "path": str(path),
            "metadata": meta,
            "rows": rows,
            "scheduled_microbatches": schedule,
            "num_rollouts": batch["num_rollouts"],
        }
    _require(set(shards) == set(ranks), "train_rank_missing", str(set(ranks) - set(shards)))
    for identity in samples:
        owners = [
            shard["metadata"]
            for shard in shards.values()
            if identity in [row["sample_index"] for row in shard["rows"]]
        ]
        _require(
            len(owners) == next(iter(ranks.values()))["cp_size"]
            and len({owner["dp_rank"] for owner in owners}) == 1
            and {owner["cp_rank"] for owner in owners} == set(range(owners[0]["cp_size"])),
            "sample_dp_cp_ownership",
            str(identity),
        )
    return shards


def _consume_debug(shard, calls, cursor):
    candidates, consumed, microbatches = list(shard["rows"]), [], []
    while candidates:
        _require(cursor < len(calls), "debug_step_missing", shard["path"])
        call, path = calls[cursor]
        dump = _load(path)
        _require(
            dump["samples"] and [item["index"] for item in dump["samples"]] == list(range(len(dump["samples"]))),
            "debug_local_row_order",
            str(path),
        )
        matched = []
        for sample in dump["samples"]:
            row = _match_debug(sample, candidates)
            candidates = [candidate for candidate in candidates if candidate is not row]
            coverage = {
                field: _finite_coverage(sample[field], row["local_mask"])
                for field in ("train_log_probs", "old_log_probs", "rollout_log_probs", "advantages")
            }
            consumed.append(
                {
                    "sample_index": row["sample_index"],
                    "call": call,
                    "path": str(path),
                    "input_coverage": row["input_coverage"],
                    "pre_tis_coverage": coverage,
                }
            )
            matched.append(row)
        _require(
            len(microbatches) < len(shard["scheduled_microbatches"])
            and [row["sample_index"] for row in matched] == shard["scheduled_microbatches"][len(microbatches)],
            "debug_native_microbatch_schedule_mismatch",
            str(path),
        )
        local_mask = torch.cat([row["local_mask"] for row in matched])
        downstream = {field: _finite_coverage(dump[field], local_mask) for field in ("ppo_kl", "pg_loss")}
        microbatches.append(
            {
                "call": call,
                "path": str(path),
                "sample_indices": [row["sample_index"] for row in matched],
                "original_eligible_tokens_full_response": sum(int(row["mask"].sum()) for row in matched),
                "native_count_loss_tokens_full_response": int(count_loss_tokens([row["mask"] for row in matched])),
                "eligible_tokens_local_cp_slice": int(local_mask.sum()),
                "downstream_sanitized_coverage": downstream,
                "producer_finite_summary": dump["finite"],
            }
        )
        cursor += 1
    return {
        "rank": shard["metadata"]["rank"],
        "dp_rank": shard["metadata"]["dp_rank"],
        "cp_rank": shard["metadata"]["cp_rank"],
        "train_artifact": shard["path"],
        "consumed_samples": consumed,
        "microbatches": microbatches,
    }, cursor


def _sample_counts(raw, frozen, population, version):
    mask = _mask(raw)
    _source_check(raw, frozen, population)
    consumed = _decode_version(raw, frozen["prompt_token_count"])
    _require(consumed == version, "consumed_publication_mismatch", str(raw["index"]))
    total, response = len(raw["tokens"]), raw["response_length"]
    prefix = total - response
    # This checks the actual native expansion function, not a separately
    # implemented prefix-zero rule. The packed runtime mask is not dumped.
    with _offline_parallel({"cp_size": 1, "cp_rank": 0}):
        expanded = _prepare_loss_masks(
            [mask.float()], [total], [response], qkv_format="thd", max_seqlen=total, pad=0, allgather_cp=False
        ).flatten()
    _require(
        not bool(expanded[:prefix].any()) and torch.equal(expanded[prefix:].bool(), mask),
        "native_prefix_loss_mask_mismatch",
        str(raw["index"]),
    )
    return {
        "sample_index": raw["index"],
        "source_uid": frozen["uid"],
        "source_group_id": frozen["group_id"],
        "prompt_sha256": frozen["prompt_sha256"],
        "completion_sha256": raw["metadata"]["completion"]["token_sha256"],
        "consumed_weight_version": consumed,
        "prefix_tokens_excluded": prefix,
        "consumed_weight_version_basis": "original_rollout_generation_decode_and_prefill_spans",
        "response_tokens": response,
        "original_eligible_target_tokens": int(mask.sum()),
        "masked_response_tokens": int((~mask).sum()),
        "fully_masked_sample": not bool(mask.any()),
        "native_count_loss_tokens": int(count_loss_tokens([mask.float()])),
        "prefix_mask_check_basis": "native_function_reconstruction_from_consumed_full_tokens_and_original_mask",
    }


def _step(run, step, ranks, publication, population, frozen, inventory, cursors, batch_size):
    path = run / "rollout_data" / f"{step}.pt"
    dump = _load(path)
    _require(dump["rollout_id"] == step, "raw_rollout_mismatch", str(path))
    raw = dump["samples"]
    _require(
        len(raw) == batch_size and len({sample["index"] for sample in raw}) == batch_size,
        "raw_completion_coverage",
        "Need eight distinct consumed completion identities per update",
    )
    _require(
        len({sample["metadata"]["source"]["uid"] for sample in raw}) == batch_size,
        "duplicate_source_in_update",
        "One fresh completion per selected prefix",
    )
    samples = {sample["index"]: sample for sample in raw}
    counts = []
    for sample in raw:
        uid = sample["metadata"]["source"]["uid"]
        _require(uid in frozen, "consumed_nontraining_source", uid)
        counts.append(_sample_counts(sample, frozen[uid], population, publication["consumed_weight_version"]))
    shards = _training_shards(run, step, ranks, samples)
    _require(
        all(shard["num_rollouts"] == [batch_size] for shard in shards.values()),
        "native_step_rollout_count_mismatch",
        "Each native training schedule must record the eight-completion update",
    )
    joined = {row["sample_index"]: row for shard in shards.values() for row in shard["rows"]}
    for row in counts:
        row["consumed_train_mask_matches_original"] = True
        row["consumed_train_token_ids_and_identity_match_original"] = True
        row["native_rollout_execution_id"] = joined[row["sample_index"]]["native_rollout_execution_id"]
        row["source_identity_binding_basis"] = joined[row["sample_index"]]["source_identity_binding_basis"]
        row["native_train_source_metadata_persisted"] = False
    rank_rows, next_cursors = [], dict(cursors)
    for rank, shard in sorted(shards.items()):
        row, next_cursors[rank] = _consume_debug(shard, inventory[rank], cursors[rank])
        rank_rows.append(row)
    original = sum(row["original_eligible_target_tokens"] for row in counts)
    native = sum(row["native_count_loss_tokens"] for row in counts)
    cp_local = sum(micro["eligible_tokens_local_cp_slice"] for row in rank_rows for micro in row["microbatches"])
    cp0_native = sum(
        micro["native_count_loss_tokens_full_response"]
        for row in rank_rows
        if row["cp_rank"] == 0
        for micro in row["microbatches"]
    )
    _require(cp_local == original and cp0_native == native, "microbatch_token_count_mismatch", str(step))
    issues = []
    if native != original:
        issues.append(
            {
                "code": "fully_masked_count_convention",
                "detail": "Native count_loss_tokens clamps each fully masked sample to one",
            }
        )
    invalid = sum(
        coverage["nonfinite_eligible"]
        for row in rank_rows
        for sample in row["consumed_samples"]
        for source in ("input_coverage", "pre_tis_coverage")
        for coverage in sample[source].values()
    )
    invalid += sum(
        coverage["nonfinite_eligible"]
        for row in rank_rows
        for micro in row["microbatches"]
        for coverage in micro["downstream_sanitized_coverage"].values()
    )
    if invalid:
        issues.append({"code": "nonfinite_pre_tis_eligible_values", "detail": str(invalid)})
    result = {
        "rollout_id": step,
        "update_position": step + 1,
        "verdict": "FAIL" if issues else "PASS",
        "issues": issues,
        **publication,
        "completion_count": len(counts),
        "original_eligible_target_tokens": original,
        "native_count_loss_tokens": native,
        "fully_masked_samples": sum(row["fully_masked_sample"] for row in counts),
        "eligible_tokens_summed_over_distinct_cp_slices": cp_local,
        "native_count_summed_over_dp_at_cp0": cp0_native,
        "nonfinite_eligible_tensor_entries": invalid,
        "raw_artifact": str(path),
        "samples": counts,
        "ranks": rank_rows,
        "post_tis_retained_tokens": None,
        "post_tis_evidence": "Native policy debug is written before TIS; no modified-response-mask dump exists",
    }
    return result, next_cursors


def audit_run(config, pair, run, launch_path, population):
    result = {
        "pair": pair,
        "run_dir": str(run),
        "launch_receipt": str(launch_path),
        "verdict": "INCOMPLETE",
        "issues": [],
        "steps": [],
    }
    try:
        launch = json.loads(launch_path.read_text())
        contract = _contract(config, pair, run, launch)
        result["launch_contract"] = contract
        ranks, paths = _rank_metadata(run, contract)
        result["rank_metadata_artifacts"] = paths
        result["rank_metadata"] = list(ranks.values())
        publications, counters = _publications(run, contract["steps"])
        result["native_publication_counters"] = counters
        inventory = _debug_inventory(run, ranks)
        cursors = {rank: 0 for rank in ranks}
        _population(population)
        frozen = {row["uid"]: row for row in population["population"] if row["split"] == "train"}
        _require(
            frozen and all(not row["exclusions"] for row in frozen.values()),
            "frozen_training_population_invalid",
            "Need eligible frozen training rows",
        )
        for step in range(contract["steps"]):
            try:
                row, cursors = _step(
                    run, step, ranks, publications[step], population, frozen, inventory, cursors, contract["batch"]
                )
            except Exception as error:
                row = {
                    "rollout_id": step,
                    "update_position": step + 1,
                    "verdict": "INCOMPLETE",
                    "issues": [_issue(error)],
                    **publications[step],
                }
            result["steps"].append(row)
        leftovers = {
            rank: len(inventory[rank]) - cursor for rank, cursor in cursors.items() if len(inventory[rank]) != cursor
        }
        _require(not leftovers, "unconsumed_debug_calls", str(leftovers))
        verdicts = [row["verdict"] for row in result["steps"]]
        result["verdict"] = "INCOMPLETE" if "INCOMPLETE" in verdicts else "FAIL" if "FAIL" in verdicts else "PASS"
    except Exception as error:
        result["issues"].append(_issue(error))
    # Preserve all 100 schedule rows even if a required shared artifact is absent.
    present = {row["rollout_id"] for row in result["steps"]}
    for step in range(config["num_rollout"]):
        if step not in present:
            result["steps"].append(
                {"rollout_id": step, "update_position": step + 1, "verdict": "INCOMPLETE", "issues": result["issues"]}
            )
    result["step_verdict_counts"] = dict(Counter(row["verdict"] for row in result["steps"]))
    return result


def _self_test():
    masks = [torch.tensor([1.0, 1.0, 1.0]), torch.tensor([1.0, 0.0]), torch.tensor([0.0, 0.0])]
    total, response = [5, 5, 3], [3, 2, 2]
    original, native = sum(int(mask.sum()) for mask in masks), int(count_loss_tokens(masks))
    _require(
        (original, native) == (4, 5), "fixture_count_failure", "Original eligible count 4; native clamped count 5"
    )
    with _offline_parallel({"cp_size": 1, "cp_rank": 0}):
        expanded = _prepare_loss_masks(
            masks, total, response, qkv_format="thd", max_seqlen=5, pad=0, allgather_cp=False
        )
        local = get_local_response_loss_masks(total, response, masks)
    _require(
        expanded.tolist() == [[0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]],
        "fixture_prefix_mask_failure",
        "Native full-input mask differs",
    )
    _require(sum(int(mask.sum()) for mask in local) == 4, "fixture_cp1_count_failure", "Native CP1 mask count differs")
    slices = []
    for rank in range(2):
        with _offline_parallel({"cp_size": 2, "cp_rank": rank}):
            slices.append(sum(int(mask.sum()) for mask in get_local_response_loss_masks(total, response, masks)))
    _require(
        sum(slices) == original,
        "fixture_cp2_count_failure",
        "Distinct native CP slices must sum to the original count",
    )
    candidate = {
        "sample_index": 42,
        "total_length": 5,
        "response_length": 3,
        "local_mask": masks[0].bool(),
        "log_probs": torch.tensor([-1.0, float("nan"), -3.0]),
        "rollout_log_probs": torch.tensor([-1.0, -2.0, -3.0]),
        "advantages": torch.ones(3),
    }
    debug = {
        "total_length": 5,
        "response_length": 3,
        "local_loss_mask": masks[0],
        "old_log_probs": candidate["log_probs"],
        "rollout_log_probs": candidate["rollout_log_probs"],
        "advantages": candidate["advantages"],
    }
    _require(_match_debug(debug, [candidate]) is candidate, "fixture_binding_failure", "Exact tensor binding failed")
    try:
        _match_debug(debug, [candidate, dict(candidate)])
    except ValueError:
        pass
    else:
        raise AssertionError("Ambiguous debug-to-sample binding was accepted")
    coverage = _finite_coverage(candidate["log_probs"], masks[0].bool())
    _require(coverage["nonfinite_eligible"] == 1, "fixture_nonfinite_failure", "Raw NaN must not be sanitized away")
    return {
        "verdict": "PASS",
        "scope": "Tiny CPU fixture only; no formal run artifacts or optimizer steps",
        "original_eligible_tokens": original,
        "native_count_loss_tokens": native,
        "cp2_local_eligible_tokens": slices,
        "raw_nonfinite_eligible": 1,
        "ambiguous_binding_rejected": True,
        "native_prefix_expansion_checked": True,
    }


def _representative_regression(root):
    """Replay the parent's four retained native files, not a synthetic run."""
    train_path = root / "train_data" / "0_0.pt"
    score_path = root / "train_data" / "eval_monitor_0_0.pt"
    debug_path = root / "policy_loss_debug" / "rank_0_call_0.pt"
    raw_path = root / "rollout_data" / "0.pt"
    train, score, debug, raw = [_load(path) for path in (train_path, score_path, debug_path, raw_path)]
    batch, meta = train["rollout_data"], score["rollout_data"]["metadata"]
    _require(
        "metadata" not in batch, "representative_schema_changed", "The retained native train shard has no metadata"
    )
    original = {sample["index"]: sample for sample in raw["samples"]}
    # Only one of four DP shards and one of two debug calls were retained.
    # The production reader still requires every configured rank and sample.
    samples = {index: original[index] for index in batch["sample_indices"]}
    shards = _training_shards(root, train["rollout_id"], {meta["rank"]: meta}, samples)
    shard = shards[meta["rank"]]
    matched = [_match_debug(sample, shard["rows"]) for sample in debug["samples"]]
    _require(
        [row["sample_index"] for row in matched] == shard["scheduled_microbatches"][0],
        "representative_debug_schedule_mismatch",
        "First retained debug call differs from the native schedule",
    )
    first_microbatch = {**shard, "rows": matched, "scheduled_microbatches": shard["scheduled_microbatches"][:1]}
    observed, cursor = _consume_debug(first_microbatch, [(debug["call"], debug_path)], 0)
    _require(cursor == 1, "representative_debug_not_consumed", "The one retained actual debug call must bind")
    first = original[batch["sample_indices"][0]]
    rejected = {}
    for case, expected in (
        ("prefix_token", "consumed_token_mismatch"),
        ("completion_token", "consumed_token_mismatch"),
        ("original_mask", "consumed_original_mask_mismatch"),
        ("sample_index", "consumed_sample_index_mismatch"),
        ("outer_schedule_as_execution_id", "consumed_rollout_execution_id_mismatch"),
        ("version_span", "consumed_weight_version_spans_mismatch"),
    ):
        changed = copy.deepcopy(batch)
        if case in ("prefix_token", "completion_token"):
            changed["tokens"][0][0 if case == "prefix_token" else -1] += 1
        elif case == "original_mask":
            changed["loss_masks"][0][0] = 1 - changed["loss_masks"][0][0]
        elif case == "sample_index":
            changed["sample_indices"][0] = batch["sample_indices"][1]
        elif case == "outer_schedule_as_execution_id":
            changed["rollout_ids"][0] = train["rollout_id"]
        else:
            changed["weight_versions"][0][0]["prefill_spans"][0]["abs_end"] += 1
        try:
            _training_row(changed, 0, first, meta, shard["rows"][0]["local_mask"])
        except ValueError as error:
            _require(error.code == expected, "representative_wrong_rejection", f"{case}: {error}")
            rejected[case] = error.code
        else:
            raise AssertionError(f"Modified actual native {case} was accepted")
    invalid = sum(
        coverage["nonfinite_eligible"] for row in shard["rows"] for coverage in row["input_coverage"].values()
    )
    invalid += sum(
        _finite_coverage(sample[field], row["local_mask"])["nonfinite_eligible"]
        for sample, row in zip(debug["samples"], matched, strict=True)
        for field in ("train_log_probs", "old_log_probs", "rollout_log_probs", "advantages")
    )
    _require(invalid == 0, "representative_nonfinite_eligible", str(invalid))
    return {
        "verdict": "PASS",
        "scope": "Actual representative shard/debug regression, not 200-update acceptance",
        "artifacts": [str(path) for path in (train_path, score_path, debug_path, raw_path)],
        "native_training_rows": len(shard["rows"]),
        "original_rollout_samples": len(original),
        "original_eligible_shard_tokens": sum(int(row["mask"].sum()) for row in shard["rows"]),
        "native_count_loss_tokens": int(count_loss_tokens([row["mask"] for row in shard["rows"]])),
        "sample_indices": [row["sample_index"] for row in shard["rows"]],
        "native_rollout_execution_ids": [row["native_rollout_execution_id"] for row in shard["rows"]],
        "generation_consumed_weight_versions": [row["generation_consumed_weight_version"] for row in shard["rows"]],
        "debug_sample_indices": [row["sample_index"] for row in matched],
        "debug_eligible_tokens": sum(int(row["local_mask"].sum()) for row in matched),
        "native_debug_calls_consumed": cursor,
        "debug_microbatch_counts": observed["microbatches"],
        "nonfinite_eligible_tensor_entries": invalid,
        "rejected_modified_native_fields": rejected,
        "source_identity_binding_basis": "verified_original_rollout_join",
        "native_train_source_metadata_persisted": False,
    }


def _named_path(value):
    name, separator, path = value.partition("=")
    if not separator or not name or not path:
        raise argparse.ArgumentTypeError("Expected PAIR=PATH")
    return name, Path(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--run", type=_named_path, action="append")
    parser.add_argument("--launch", type=_named_path, action="append")
    parser.add_argument("--population-report", type=Path, help="Defaults to config.population_dir/population.json")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--representative-dir", type=Path, help="Parent-retained four-file native schema regression")
    args = parser.parse_args()
    report = {
        "schema_version": 1,
        "task_id": "QWEN-REVIEW-TOKEN-AUDIT",
        "verdict": "INCOMPLETE",
        "environment": {"python": sys.version, "torch": torch.__version__},
        "limits": [
            "Offline read-only collection; no platform calls, model execution or optimizer steps.",
            "Native train shards have no source metadata; provenance is joined from the original rollout only after exact native sample-index/full-token/mask/execution-ID/version-span equality.",
            "Train-shard weight_versions are copied generation receipts, not an independent trainer-version scalar; the pre-update trainer counter is derived from native publication ordering.",
            "Counts are derived through native mask/count owners, not recorded finalizer all-reduce scalars.",
            "Prefix masks are native-function reconstructions, not dumped packed masks.",
            "Policy debug has no identities: ambiguous exact tensor bindings remain INCOMPLETE.",
            "ppo_kl and pg_loss are already sanitized by the native producer; raw score/advantage coverage is separate.",
            "Post-TIS modified masks are not dumped; retained counts are unavailable, not zero.",
        ],
        "runs": [],
        "issues": [],
    }
    try:
        _require(
            not (args.self_test and args.representative_dir), "regression_mode_conflict", "Select one regression mode"
        )
        if args.self_test:
            report["self_test"] = _self_test()
            report["verdict"] = report["self_test"]["verdict"]
        elif args.representative_dir:
            report["representative_regression"] = _representative_regression(args.representative_dir)
            report["verdict"] = report["representative_regression"]["verdict"]
        else:
            if not args.config or not args.run or not args.launch:
                parser.error("Collection requires --config, --run and --launch")
            config = json.loads(args.config.read_text())
            runs, launches = dict(args.run), dict(args.launch)
            _require(
                len(runs) == len(args.run) and len(launches) == len(args.launch) and runs.keys() == launches.keys(),
                "run_launch_selection_mismatch",
                "Provide each selected pair exactly once with its launch receipt",
            )
            population_path = args.population_report or Path(config["population_dir"]) / "population.json"
            report["population_report"] = str(population_path)
            population = json.loads(population_path.read_text())
            report["runs"] = [audit_run(config, pair, run, launches[pair], population) for pair, run in runs.items()]
            report["step_rows"] = sum(len(run["steps"]) for run in report["runs"])
            verdicts = [run["verdict"] for run in report["runs"]]
            report["verdict"] = "INCOMPLETE" if "INCOMPLETE" in verdicts else "FAIL" if "FAIL" in verdicts else "PASS"
    except Exception as error:
        report["issues"].append(_issue(error))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print("QWEN35_TRAINING_TOKEN_AUDIT", report["verdict"], str(args.report), flush=True)
    # Reporting soft gate only: verdicts never control healthy training.


if __name__ == "__main__":
    main()
