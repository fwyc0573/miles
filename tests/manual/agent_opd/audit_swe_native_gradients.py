"""Audit saved native gradient observations using independent CPU arithmetic.

No producer imports, tensor forwards, collectives or optimizer steps are run.
Missing observer rows invalidate coverage instead of becoming zero gradients.
The scale audit concerns sampled DDP main_grad values, not shard ownership.
"""

import argparse
import collections
import hashlib
import json
import math
import platform
import resource
import struct
import sys
from pathlib import Path


EVENTS = (
    "before_train", "live_loss_graph", "post_tis_backward", "live_logprob_backward",
    "finalizer_before", "parameter_gradient_scale", "finalizer_after",
    "live_graph_source_values", "optimizer_ack",
)


def _f32(value):
    return struct.unpack("f", struct.pack("f", value))[0]


def _criterion(conditions, **evidence):
    errors = [name for name, passed in conditions.items() if not passed]
    return {"status": "FAIL" if errors else "PASS", "violations": errors, **evidence}


def _load(root, ranks, updates):
    files, steps, missing, soft = [], {}, [], []
    for rank in ranks:
        path = root / f"native_gradients_rank_{rank}.jsonl"
        if not path.is_file():
            missing.append(str(path))
            continue
        raw = path.read_bytes()
        rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
        files.append({"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                      "bytes": len(raw), "rows": len(rows),
                      "events": dict(collections.Counter(row["event"] for row in rows))})
        for row in rows:
            if row["rank"] != rank:
                missing.append(f"filename/actual-rank disagreement: {path}")
            if row["event"] == "observer_unverified":
                soft.append(row)
            key = (rank, row["rollout_id"], row["step_id"])
            name = (row["event"], row.get("stage"))
            bucket = steps.setdefault(key, {})
            if name in bucket:
                missing.append(f"duplicate {key} {name}")
            bucket[name] = row
        for update in range(updates):
            key = (rank, update, 0)
            bucket = steps.get(key, {})
            for name in [(event, None) for event in EVENTS] + [
                ("optimizer_boundary", "before_optimizer"), ("optimizer_boundary", "after_optimizer")
            ]:
                if name not in bucket:
                    missing.append(f"missing {key} {name}")
    expected = {(rank, update, 0) for rank in ranks for update in range(updates)}
    missing.extend(f"unexpected step {key}" for key in steps.keys() - expected)
    return files, steps, missing, soft


def _row(bucket, event, stage=None):
    return bucket[(event, stage)]


def _detached(flags):
    return bool(flags) and all(not value["requires_grad"] and value["grad_fn"] is None for value in flags)


def _tokens(steps, training):
    conditions, calls = {}, []
    lower, upper = 1 - training["eps_clip"], 1 + training["eps_clip_high"]
    for (rank, update, step), bucket in sorted(steps.items()):
        graph = _row(bucket, "live_loss_graph")
        pg = _row(bucket, "post_tis_backward")
        backward = _row(bucket, "live_logprob_backward")
        source = _row(bucket, "live_graph_source_values")
        boundary = _row(bucket, "optimizer_boundary", "before_optimizer")
        label = f"rank{rank}/update{update}"
        conditions[label + "/event_join"] = all(
            item["call"] == graph["call"] == 1 and item["indices"] == graph["indices"]
            for item in (pg, backward, source)
        ) and source["sample_indices"] == graph["sample_indices"]
        conditions[label + "/metadata_join"] = (
            [row["sample_index"] for row in boundary["metadata"]] == boundary["sample_indices"]
            and set(graph["sample_indices"]) == set(boundary["sample_indices"])
        )
        conditions[label + "/detach"] = (
            graph["detached_baseline_edge"] and backward["baseline_input_gradient_is_none"]
            and graph["native_kl_node"] == "SubBackward0" and graph["live_logprob_node"] == "CatBackward0"
            and all(value["requires_grad"] for name in ("pg_loss_flags", "saved_native_kl_flags") for value in graph[name])
            and all(_detached(graph[name]) for name in (
                "scored_student_flags", "teacher_flags", "behavior_flags", "original_mask_flags", "survivor_mask_flags"))
            and all(_detached(flags) for flags in boundary["source_inputs"].values())
        )
        lengths = [flag["shape"][0] for flag in graph["original_mask_flags"]]
        conditions[label + "/response_domain"] = sum(lengths) == graph["pg_loss_flags"][0]["shape"][0]
        tokens = []
        for i, flat in enumerate(graph["indices"]):
            offset, sample_index, response_index = 0, None, None
            for index, length in zip(graph["sample_indices"], lengths, strict=True):
                if offset <= flat < offset + length:
                    sample_index, response_index = index, flat - offset
                    break
                offset += length
            original, retained = graph["original_masks"][i], graph["survivor_masks"][i]
            incoming = pg["d_loss_d_pre_tis_pg_loss"][i]
            observed = backward["d_loss_d_train_logprob"][i]
            native_kl = graph["actual_native_s_minus_l"][i]
            q, s, behavior = (source[name][i] for name in ("teacher_log_probs", "log_probs", "rollout_log_probs"))
            # Independently reconstruct q-s with the producer tensor's FP32 subtraction.
            advantage = _f32(q - s)
            finite = all(math.isfinite(value) for value in (q, s, behavior, native_kl, incoming, observed))
            conditions[f"{label}/position{flat}/finite_unsaturated"] = finite and abs(native_kl) < 20
            if not finite or abs(native_kl) >= 20:
                return {"status": "UNVERIFIED", "reason": f"Nonfinite/saturated PPO boundary at {label}/{flat}"}
            rho = math.exp(-native_kl)
            clipped = (advantage > 0 and rho > upper) or (advantage < 0 and rho < lower)
            derivative = 0.0 if clipped else -advantage * rho
            expected = derivative * incoming
            reference64 = (0.0 if clipped else -(q - s) * rho) * incoming
            error = abs(observed - expected)
            conditions[f"{label}/position{flat}/mask"] = (
                original in (0, 1) and retained in (0, 1) and retained <= original
                and incoming == original * retained and sample_index is not None
            )
            conditions[f"{label}/position{flat}/advantage"] = advantage == source["advantages"][i]
            conditions[f"{label}/position{flat}/derivative"] = error <= 1e-6 + 1e-5 * abs(expected)
            sign_error = abs(observed + backward["d_loss_d_native_kl"][i])
            conditions[f"{label}/position{flat}/sign"] = sign_error == 0
            if original == 1 and retained == 0:
                conditions[f"{label}/position{flat}/rejected_zero"] = observed == incoming == 0
            tokens.append({"flat_position": flat, "sample_index": sample_index, "response_index": response_index,
                           "original": original, "retained": retained, "rho": rho, "clip_active": clipped,
                           "scored_student": s, "teacher": q, "behavior": behavior,
                           "advantage_f32": advantage, "actual_native_s_minus_l": native_kl,
                           "incoming_pg_gradient": incoming, "expected_d_loss_d_l": expected,
                           "observed_d_loss_d_l": observed, "absolute_error": error,
                           "relative_error": error / abs(expected) if expected else None,
                           "float64_source_error": abs(observed - reference64), "sign_error": sign_error})
        calls.append({"rank": rank, "rollout_id": update, "step_id": step, "call": graph["call"],
                      "original_tokens": graph["original_tokens"], "surviving_tokens": graph["surviving_tokens"],
                      "response_lengths": lengths, "sample_indices": graph["sample_indices"], "positions": tokens})
    positions = [position for call in calls for position in call["positions"]]
    unique_positions = {}
    for call in calls:
        for position in call["positions"]:
            key = (call["rollout_id"], position["sample_index"], position["response_index"])
            if key in unique_positions:
                conditions[f"TP_duplicate/{key}"] = unique_positions[key] == position
            unique_positions[key] = position
    retained = [position for position in positions if position["original"] == position["retained"] == 1]
    rejected = [position for position in positions if position["original"] == 1 and position["retained"] == 0]
    conditions["run/nonzero_retained"] = any(position["observed_d_loss_d_l"] != 0 for position in retained)
    conditions["run/rejected"] = bool(rejected)
    compact_calls = []
    for call in calls:
        examples = {}
        for position in call["positions"]:
            kind = "retained" if position["retained"] else "rejected"
            examples.setdefault(kind, position)
        compact_calls.append({**{key: value for key, value in call.items() if key != "positions"},
                              "sampled_presentations": len(call["positions"]),
                              "retained_presentations": sum(p["retained"] == 1 for p in call["positions"]),
                              "max_derivative_abs_error": max(p["absolute_error"] for p in call["positions"]),
                              "examples": examples})
    return _criterion(conditions, calls=compact_calls, sampled_presentations=len(positions),
                      tp_deduplicated_presentations=len(unique_positions),
                      tp_deduplicated_retained=sum(p["retained"] == 1 for p in unique_positions.values()),
                      tp_deduplicated_rejected=sum(p["original"] == 1 and p["retained"] == 0 for p in unique_positions.values()),
                      retained_presentations=len(retained), rejected_presentations=len(rejected),
                      nonzero_retained_presentations=sum(p["observed_d_loss_d_l"] != 0 for p in retained),
                      max_derivative_abs_error=max(p["absolute_error"] for p in positions),
                      max_derivative_relative_error=max(p["relative_error"] or 0 for p in positions),
                      max_float64_source_error=max(p["float64_source_error"] for p in positions),
                      max_sign_error=max(p["sign_error"] for p in positions),
                      rho_values=sorted({p["rho"] for p in positions}),
                      clip_active_presentations=sum(p["clip_active"] for p in positions))


def _normalization(steps):
    conditions, calls, totals = {}, [], {}
    for (rank, update, _), bucket in sorted(steps.items()):
        before, after = _row(bucket, "finalizer_before"), _row(bucket, "finalizer_after")
        graph, ack = _row(bucket, "live_loss_graph"), _row(bucket, "optimizer_ack")["native_result"]
        scale = _row(bucket, "parameter_gradient_scale")
        topology, = before["topology"]
        dp, tp = topology["dp_cp"]["ranks"], topology["tp"]["ranks"]
        label = f"rank{rank}/update{update}"
        conditions[label + "/topology"] = rank in dp and rank in tp and len(dp) == topology["dp_cp"]["size"]
        conditions[label + "/original_local"] = before["native_local_num_tokens"] == graph["original_tokens"]
        original = sum(_row(steps[(peer, update, 0)], "live_loss_graph")["original_tokens"] for peer in dp)
        surviving = sum(_row(steps[(peer, update, 0)], "live_loss_graph")["surviving_tokens"] for peer in dp)
        conditions[label + "/original_global"] = original == after["native_global_num_tokens"] == scale["native_global_num_tokens"] == ack["original_tokens"]
        conditions[label + "/survivor_global"] = surviving == ack["surviving_tokens"]
        conditions[label + "/ddp_sum"] = topology["config"]["average_in_collective"] is False
        conditions[label + "/buffer_prescale"] = bool(topology["buffers"]) and all(buffer["gradient_scaling_factor"] == 1 for buffer in topology["buffers"])
        conditions[label + "/token_membership"] = len({index for peer in dp for index in _row(steps[(peer, update, 0)], "live_loss_graph")["sample_indices"]}) == ack["actual_turns"]
        for peer in tp:
            peer_graph = _row(steps[(peer, update, 0)], "live_loss_graph")
            conditions[label + f"/tp{peer}_sample_membership"] = graph["sample_indices"] == peer_graph["sample_indices"]
            conditions[label + f"/tp{peer}_token_counts"] = graph["original_tokens"] == peer_graph["original_tokens"]
        factor = scale["factor"]
        factor_error = abs(factor - 1 / original) / (1 / original)
        conditions[label + "/factor"] = factor_error <= 1e-7 and scale["factor_dtype"] == "torch.float32"
        sampled_before, sampled_after = scale["before"], scale["after"]
        conditions[label + "/main_grad_identity"] = all(sampled_before[key] == sampled_after[key] for key in (
            "parameter", "gradient_attr", "gradient_dtype", "indices")) and sampled_before["gradient_attr"] == "main_grad"
        errors, relative, fp32_errors = [], [], []
        for value, observed in zip(sampled_before["values"], sampled_after["values"], strict=True):
            expected = value * factor
            error = abs(observed - expected)
            errors.append(error)
            relative.append(error / abs(expected) if expected else None)
            fp32_errors.append(abs(observed - _f32(expected)))
            conditions[label + f"/scale_position{len(errors)}"] = (
                math.isfinite(value) and math.isfinite(observed) and error <= 1e-8 + 1e-6 * abs(expected))
        nonzero = sum(value != 0 for value in sampled_before["values"])
        calls.append({"rank": rank, "rollout_id": update, "chunk": scale["chunk"], "dp_cp_ranks": dp,
                      "tp_ranks": tp, "local_original": graph["original_tokens"], "local_surviving": graph["surviving_tokens"],
                      "global_original": original, "global_surviving": surviving, "factor": factor,
                      "factor_relative_error": factor_error, "nonzero_before_positions": nonzero,
                      "scale_positions": len(errors), "max_abs_error": max(errors),
                      "max_relative_error": max(value for value in relative if value is not None) if nonzero else None,
                      "max_fp32_reference_error": max(fp32_errors),
                      "nonzero_scale_evidence": "PASS" if nonzero else "UNVERIFIED_ZERO_ONLY_SLICE",
                      "ownership": "Not recorded: sampled full-parameter main_grad is not established as this optimizer rank's owned shard"})
        totals[(update, tuple(dp))] = {"rollout_id": update, "dp_cp_ranks": dp, "original_tokens": original,
                                       "surviving_tokens": surviving, "bank": ack["bank"], "bank_visit": ack["bank_visit"]}
    return _criterion(conditions, calls=calls, group_totals=list(totals.values()), scale_calls=len(calls),
                      sampled_scale_positions=sum(call["scale_positions"] for call in calls),
                      nonzero_scale_calls=sum(call["nonzero_before_positions"] > 0 for call in calls),
                      zero_only_scale_calls=[{key: call[key] for key in ("rank", "rollout_id", "chunk")} for call in calls if not call["nonzero_before_positions"]],
                      max_factor_relative_error=max(call["factor_relative_error"] for call in calls),
                      max_scale_abs_error=max(call["max_abs_error"] for call in calls),
                      max_scale_relative_error=max(call["max_relative_error"] for call in calls if call["max_relative_error"] is not None),
                      max_scale_fp32_reference_error=max(call["max_fp32_reference_error"] for call in calls))


def _optimizer(steps, training, job_id):
    conditions, ranks = {}, []
    for rank in sorted({key[0] for key in steps}):
        snapshots, acks = [], []
        for update in range(training["successful_updates"]):
            bucket = steps[(rank, update, 0)]
            for event, stage in (("before_train", None), ("optimizer_boundary", "before_optimizer"),
                                 ("optimizer_boundary", "after_optimizer")):
                snapshot = _row(bucket, event, stage)["optimizer"]
                label = f"rank{rank}/update{update}/{event}/{stage}"
                snapshots.append((update, event, stage, snapshot))
                conditions[label + "/wrapper"] = snapshot["wrapper_class"].endswith(".ChainedOptimizer")
                for leaf_index, leaf in enumerate(snapshot["leaves"]):
                    conditions[label + f"/leaf{leaf_index}/adamw"] = leaf["class"].endswith(".FusedAdam") and leaf["adam_w_mode"] == 1
                    conditions[label + f"/leaf{leaf_index}/decay_groups"] = sorted(group["weight_decay"] for group in leaf["param_groups"]) == [0, training["weight_decay"]]
                    for group_index, group in enumerate(leaf["param_groups"]):
                        conditions[label + f"/leaf{leaf_index}/group{group_index}/settings"] = (
                            group["lr"] == training["lr"] and group["eps"] == training["adam_eps"]
                            and group["betas"] == [training["adam_beta1"], training["adam_beta2"]])
                        if stage == "after_optimizer" or update > 0:
                            expected_step = update + 1 if stage == "after_optimizer" else update
                            conditions[label + f"/leaf{leaf_index}/group{group_index}/counter"] = group["group_step"] == expected_step
                            conditions[label + f"/leaf{leaf_index}/group{group_index}/state"] = bool(group["state_sample"])
            ack = _row(bucket, "optimizer_ack")["native_result"]
            metadata = _row(bucket, "optimizer_boundary", "after_optimizer")["metadata"]
            bank, visit = divmod(update, training["bank_uses"])
            conditions[f"rank{rank}/update{update}/ack"] = (
                ack["attempt"] == job_id and ack["run_kind"] == training["run_kind"] and ack["update_successful"]
                and ack["successful_updates"] == ack["native_attempted_count"] == update + 1
                and ack["native_skipped_count"] == 0 and ack["bank"] == bank and ack["bank_visit"] == visit + 1
                and ack["current_weight_version"] == update
                and ack["diagnostics_verified"] and not ack["unverified_diagnostics"])
            conditions[f"rank{rank}/update{update}/bank_metadata"] = all(
                row["swe_bank"] == bank and row["swe_bank_visit"] == visit + 1 and row["swe_successful_before"] == update for row in metadata)
            conditions[f"rank{rank}/update{update}/boundary_metadata"] = metadata == _row(bucket, "optimizer_boundary", "before_optimizer")["metadata"]
            acks.append({key: ack[key] for key in ("bank", "bank_visit", "successful_updates", "native_skipped_count", "current_weight_version")})
        first = snapshots[0][3]
        initialized = snapshots[2][3]
        for update, event, stage, snapshot in snapshots:
            label = f"rank{rank}/update{update}/{event}/{stage}"
            conditions[label + "/wrapper_identity"] = snapshot["wrapper_id"] == first["wrapper_id"]
            conditions[label + "/leaf_identities"] = [(leaf["id"], leaf["state_id"]) for leaf in snapshot["leaves"]] == [(leaf["id"], leaf["state_id"]) for leaf in first["leaves"]]
            conditions[label + "/group_structure"] = [
                (group["param_count"], group["weight_decay"]) for leaf in snapshot["leaves"] for group in leaf["param_groups"]
            ] == [(group["param_count"], group["weight_decay"]) for leaf in first["leaves"] for group in leaf["param_groups"]]
            if update == 0 and stage != "after_optimizer":
                continue  # Absent initial counters are uninitialized, not invented zero values.
            for leaf, initial in zip(snapshot["leaves"], initialized["leaves"], strict=True):
                conditions[label + "/sampled_state_identity"] = [group["state_sample"] for group in leaf["param_groups"]] == [group["state_sample"] for group in initial["param_groups"]]
        ranks.append({"rank": rank, "wrapper_class": first["wrapper_class"], "wrapper_id": first["wrapper_id"],
                      "initialized_leaf_states": initialized["leaves"], "native_acks": acks,
                      "post_update_group_steps": [[group["group_step"] for leaf in item[3]["leaves"] for group in leaf["param_groups"]] for item in snapshots if item[2] == "after_optimizer"]})
    return _criterion(conditions, ranks=ranks, rank_count=len(ranks),
                      sampled_state_dicts=sum(len(leaf["param_groups"]) for rank in ranks for leaf in rank["initialized_leaf_states"]))


def _provenance(steps, pinned):
    observations = collections.defaultdict(set)

    def visit(value):
        if isinstance(value, dict):
            if "source_sha256" in value:
                observations[(value["name"], value["path"])].add(value["source_sha256"])
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    for bucket in steps.values():
        visit(list(bucket.values()))
    paths = {"optimizer.py": pinned / "optimizer/optimizer.py",
             "finalize_model_grads.py": pinned / "distributed/finalize_model_grads.py",
             "distributed_data_parallel.py": pinned / "distributed/distributed_data_parallel.py",
             "model.py": Path("miles/backends/megatron_utils/model.py")}
    records = []
    for (name, runtime_path), digests in observations.items():
        local = paths[Path(runtime_path).name]
        digest = hashlib.sha256(local.read_bytes()).hexdigest()
        records.append({"name": name, "runtime_path": runtime_path, "runtime_sha256": sorted(digests),
                        "inspected_local_path": str(local), "local_sha256": digest,
                        "status": "PASS" if digests == {digest} else "FAIL"})
    return {"status": "PASS" if records and all(record["status"] == "PASS" for record in records) else "FAIL", "delegates": records,
            "unrecorded_runtime_digests": ["observer module", "TransformerEngine FusedAdam", "param_and_grad_buffer.py", "distrib_optimizer.py"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--ranks", type=int, nargs="+", required=True)
    parser.add_argument("--pinned-core", type=Path, required=True)
    parser.add_argument("--memory-gib", type=int, required=True)
    args = parser.parse_args()
    memory = args.memory_gib * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    training = json.loads(args.config.read_text())["training"]
    files, steps, missing, soft = _load(args.root, args.ranks, training["successful_updates"])
    result = {"task_id": "T02-ACTUAL-GRADIENT-AUDIT", "job_id": args.job_id,
              "command": ["timeout", "60s", sys.executable, *sys.argv], "python": platform.python_version(),
              "memory_limit_gib": args.memory_gib, "files": files, "config": str(args.config),
              "coverage": {"status": "UNVERIFIED" if missing or soft else "PASS", "missing_or_duplicate": missing,
                           "observer_soft_failures": soft, "rank_steps": len(steps), "rows": sum(file["rows"] for file in files)}}
    if not missing and not soft:
        result["tokens"] = _tokens(steps, training)
        result["normalization"] = _normalization(steps)
        result["optimizer"] = _optimizer(steps, training, args.job_id)
        result["provenance"] = _provenance(steps, args.pinned_core)
        failed = [name for name in ("tokens", "normalization", "optimizer", "provenance") if result[name]["status"] == "FAIL"]
        unverified = [name for name in ("tokens", "normalization", "optimizer", "provenance") if result[name]["status"] == "UNVERIFIED"]
        result["status"] = (
            "FAIL" if failed else "UNVERIFIED_NUMERIC_CASE" if unverified
            else "OBSERVED_MATH_PASS_WITH_UNVERIFIED_ZERO_SLICES_AND_SHARD_OWNERSHIP"
        )
        result["failed_criteria"] = failed
        result["unverified_numeric_criteria"] = unverified
        zeros = result["normalization"]["zero_only_scale_calls"]
        result["nonzero_scale_coverage"] = {
            "status": "UNVERIFIED" if zeros else "PASS",
            "calls_with_nonzero_slice": result["normalization"]["nonzero_scale_calls"],
            "total_scale_calls": result["normalization"]["scale_calls"],
            "zero_only_calls": zeros,
            "reason": "Measured zeros are genuine observations, not missing rows; zero multiplication alone cannot verify nonzero scaling at these calls",
        }
        result["optimizer_owned_gradient"] = {
            "status": "UNVERIFIED",
            "reason": "Runtime use_distributed_optimizer=True; JSONL does not record parameter-to-buffer ranges or this rank's owning shard. Only actual scale-method multiplication is audited",
        }
        result["limits"] = [
            f"{len(zeros)} zero-only scale slices verify recorded factor and zero preservation but not nonzero scaling at those calls",
            "No parameter-to-buffer shard range is recorded; no sampled full-buffer value is claimed to be an optimizer-owned gradient or a cross-rank SUM",
            "Only sampled actual gradients are saved; complete tensor/parameter gradients and full answer TIS ratios cannot be independently reconstructed from JSONL",
            "All observed PPO ratios are one; this reachable configuration does not exercise clipping branches",
            "Optimizer continuity proves observed identities/group counters and sampled initialized state dicts, not unsaved momentum values or every parameter state",
            "Only A/r256, three eight-turn smoke updates; no 256-turn capacity, formal schedule or Ticket02 completion verdict",
        ]
    else:
        result["status"] = "UNVERIFIED_MISSING_NATIVE_OBSERVATIONS"
    result["maximum_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"task_id": result["task_id"], "status": result["status"], "output": str(args.output),
                      "criteria": {name: value["status"] for name, value in result.items() if isinstance(value, dict) and "status" in value}}))
    if result["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
