"""Offline D8 acceptance of native Qwen3.5 fixed-monitoring artifacts.

Example:
    python -m tests.manual.agent_opd.inspect_qwen35 --run-dir RUN_DIRECTORY \
        --population-report FROZEN_POPULATION/population.json --report REPORT.json

Reads rollout_data/eval_{rollout_id}.pt and native train_data/
eval_{URL-escaped-dataset}_{rollout_id}_{rank}.pt. The original pre-TIS
population, not sanitized native loss metrics, owns the denominator. No platform
access, training control, synthetic replacement data, or convergence claim.

Required evidence in the native score payload: tokens and loss_masks
(full, original response masks). Missing input receipts are INCOMPLETE, not an
assumption that equal lengths imply equal tokens. Each Sample.metadata must
record probability_definition with decode/prefill='full_vocabulary_log_softmax',
sampling_distribution='student_decode', and sampling_params containing
temperature/top_p/top_k. Existing student_rescoring and weight_versions schemas
are consumed unchanged. Raw artifacts remain at their supplied paths.

Full D8 also requires the native events/ JSONL publication chain, model-companion
counter advances, and changed engine model checksums. The final monitoring
forward must consume the final actual published version. A baseline checkpoint
may pass its numerical check while the full D8 verdict remains INCOMPLETE.
"""

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

import torch

from examples.agentic_opd.glm_turns import token_hash
from examples.infra_features.train_infer_mismatch_helper.mis import MisConfig
from tests.manual.agent_opd.inspect_warmup import _tensor
from tests.manual.agent_opd.prepare_qwen35 import LENGTH_STRATA, MONITOR_PER_STRATUM

from miles.backends.training_utils.data.context_parallel import get_logits_and_tokens_offset_with_cp
from miles.utils.audit_utils.event_analyzer.rules import (
    inference_engine_weight_checksum_consistency,
    inference_engine_weight_checksum_coverage,
)
from miles.utils.audit_utils.event_logger.logger import EventReader
from miles.utils.audit_utils.event_logger.models import (
    InferenceEngineChecksumCollectionFailedEvent,
    InferenceEngineWeightChecksumEvent,
    TrainGroupStepEndEvent,
    WeightUpdateResultEvent,
)
from miles.utils.audit_utils.process_identity import TrainerControllerProcessIdentity
from miles.utils.types import WeightVersionsPerCall


class EvidenceError(ValueError):
    def __init__(self, code, detail):
        super().__init__(detail)
        self.code = code


def _require(condition, code, detail):
    if not condition:
        raise EvidenceError(code, detail)


def _issue(error):
    return {"code": error.code if isinstance(error, EvidenceError) else "corrupt_schema", "detail": str(error)}


def _vector(value, name, *, dtype=torch.float64):
    _require(value is not None, "missing_tensor", f"{name}: native values are absent")
    _require(not isinstance(value, (list, tuple)) or all(item is not None for item in value),
             "missing_tensor_values", f"{name}: native values contain missing positions")
    value = _tensor(value)
    if dtype == torch.int64:
        _require(not value.is_floating_point() and value.dtype != torch.bool,
                 "invalid_token_dtype", f"{name}: token IDs must be integers, without coercion")
    value = value.to(dtype)
    _require(value.ndim == 1, "invalid_shape", f"{name}: expected a one-dimensional tensor")
    return value


def _mask(sample):
    # None is the native single-turn convention: every response token is eligible.
    value = sample.get("loss_mask")
    mask = torch.ones(sample["response_length"], dtype=torch.float64) if value is None else _vector(value, "loss_mask")
    _require(len(mask) == sample["response_length"], "mask_length_mismatch", "Original mask differs from response length")
    _require(bool(((mask == 0) | (mask == 1)).all()), "invalid_mask", "Original target mask must contain only zero/one")
    return mask.bool()


def _population(report):
    _require(report["status"] == "passed", "population_not_frozen", "Preparation did not pass")
    expected = [{"name": name, "lower_exclusive": lower, "upper_inclusive": upper} for name, lower, upper in LENGTH_STRATA]
    _require(report["length_strata"] == expected, "stratum_definition_mismatch", "Frozen boundaries differ from preparation")
    _require(report["monitoring_per_stratum"] == MONITOR_PER_STRATUM, "monitoring_count_mismatch", "Frozen count differs")
    uids = report["split"]["monitoring_uids"]
    _require(len(uids) == len(set(uids)) == len(LENGTH_STRATA) * MONITOR_PER_STRATUM,
             "monitoring_identity_mismatch", "Expected exactly 24 distinct frozen identities")
    rows = [row for row in report["population"] if row["split"] == "monitor"]
    _require(len(rows) == len(uids) and {row["uid"] for row in rows} == set(uids),
             "monitoring_identity_mismatch", "Frozen population rows disagree with monitoring_uids")
    counts = Counter(row["stratum"] for row in rows)
    _require(dict(counts) == {name: MONITOR_PER_STRATUM for name, _, _ in LENGTH_STRATA},
             "missing_stratum", "Need eight frozen monitoring identities in each length stratum")
    _require(not any(report["split"]["checks"].values()), "population_overlap", "Frozen group isolation checks failed")
    indexed = {row["uid"]: row for row in rows}
    for row in rows:
        length = row["prompt_token_count"]
        name = next((name for name, lower, upper in LENGTH_STRATA if lower < length <= upper), None)
        _require(name == row["stratum"] and not row["exclusions"], "invalid_frozen_prefix", row["uid"])
    return indexed


def _source_check(sample, frozen, population):
    source = sample["metadata"]["source"]
    for field in ("uid", "group_id", "prompt_token_count", "prompt_sha256"):
        _require(source[field] == frozen[field], "source_identity_mismatch", f"Frozen {field} differs")
    tokens = _vector(sample["tokens"], "tokens", dtype=torch.int64)
    prefix = frozen["prompt_token_count"]
    _require(len(tokens) - prefix == sample["response_length"], "token_boundary_mismatch", "Prefix/response boundary differs")
    _require(token_hash(tokens[:prefix].tolist()) == frozen["prompt_sha256"], "prefix_token_mismatch", frozen["uid"])
    completion_hash = token_hash(tokens[prefix:].tolist())
    _require(completion_hash == sample["metadata"]["completion"]["token_sha256"],
             "completion_token_mismatch", frozen["uid"])
    _require(sample["metadata"]["chat_template_kwargs"] == population["chat_template"]["kwargs"],
             "template_mismatch", "Generation template settings differ from frozen preparation")
    train = sample.get("train_metadata") or {}
    for key, value in (("prompt_sha256", frozen["prompt_sha256"]), ("completion_sha256", completion_hash),
                       ("source_uid", frozen["uid"]), ("sample_index", sample["index"])):
        _require(train.get(key) == value, "train_identity_mismatch", f"train_metadata.{key} differs or is absent")
    _require(sample["status"] in ("completed", "truncated") and not sample.get("remove_sample", False),
             "invalid_generation_status", str(sample["status"]))
    return tokens


def _decode_version(sample, prefix):
    calls = [WeightVersionsPerCall.from_dict(call) for call in sample["weight_versions"]]
    _require(len(calls) == 1, "decode_version_missing_or_multicall", "Fixed single-turn evidence needs one complete version call")
    call = calls[0]
    call.validate(num_tokens=len(sample["tokens"]))
    _require(call.output_start == prefix and call.spans and call.spans[-1].abs_end == len(sample["tokens"]),
             "decode_version_coverage", "Consumed decode versions do not cover the full completion")
    _require(call.prefill_spans and call.prefill_spans[-1].abs_end == prefix,
             "generation_prefill_version_missing", "Consumed KV/prefix versions are absent or incomplete")
    versions = {str(span.version) for span in call.spans + call.prefill_spans}
    _require(len(versions) == 1, "mixed_consumed_versions", "Decode and generation prefill consumed different weights")
    return next(iter(versions))


def _probability_check(sample, score_metadata, comparison):
    definition = sample["metadata"].get("probability_definition")
    _require(isinstance(definition, dict), "probability_definition_missing", "Original generation probability metadata is absent")
    _require(definition.get(comparison) == "full_vocabulary_log_softmax",
             "probability_definition_mismatch", f"{comparison} is not declared full-vocabulary log-softmax")
    _require(definition.get("sampling_distribution") == "student_decode", "sampling_distribution_missing",
             "K3 sampling distribution must explicitly identify fresh student decode")
    params = definition.get("sampling_params")
    _require(isinstance(params, dict), "sampling_params_missing", "Native sampling settings are absent")
    _require(params.get("temperature") == score_metadata["rollout_temperature"] == 1
             and params.get("top_p") == 1 and params.get("top_k") == -1,
             "probability_definition_mismatch", "D14 needs temperature=1, top_p=1, top_k=-1")
    _require(score_metadata["use_rollout_sampling_mask"] is False, "probability_definition_mismatch",
             "Trainer scoring applied a sampling mask")
    if comparison == "prefill":
        scored = sample["metadata"]["student_rescoring"]
        _require(scored.get("probability_definition") == definition["prefill"],
                 "prefill_probability_definition_missing", "Prefill must record its own actual probability definition")


def _response_positions(metadata, total, response, max_seq_len):
    size, rank = metadata["cp_size"], metadata["cp_rank"]
    _require(size >= 1 and 0 <= rank < size, "invalid_cp_rank", "Invalid context-parallel identity")
    layout = metadata["response_layout"]
    if size == 1:
        _require(layout == "response", "unsupported_response_layout", layout)
        return list(range(response))
    _require(layout == "zigzag" and not metadata["allgather_cp"], "unsupported_response_layout",
             "CP all-gather/unknown layouts lack sufficient position metadata; do not flatten")
    _require(metadata["qkv_format"] in ("thd", "bshd"), "unsupported_qkv_format", metadata["qkv_format"])
    _, _, _, offsets = get_logits_and_tokens_offset_with_cp(
        total, response, metadata["qkv_format"], max_seq_len, cp_rank=rank, cp_size=size
    )
    prefix = total - response
    return [position - prefix for start, end in offsets for position in range(start, end)]


def _score_slices(paths, rollout_id, stem):
    indexed, issues, ranks, topology = defaultdict(list), [], set(), {}
    for path in paths:
        try:
            dump = torch.load(path, map_location="cpu", weights_only=False)
            batch, meta = dump["rollout_data"], dump["rollout_data"]["metadata"]
            _require(dump["rollout_id"] == stem and meta["rollout_id"] == rollout_id,
                     "score_checkpoint_mismatch", str(path))
            _require(meta["rank"] == dump["rank"] and meta["cp_rank"] == dump["cp_rank"]
                     and meta["cp_size"] == dump["cp_size"] and meta["qkv_format"] == dump["qkv_format"],
                     "rank_metadata_mismatch", str(path))
            _require(meta["tp_rank"] == 0 and meta["pp_rank"] == meta["pp_size"] - 1,
                     "unexpected_replica", "Only TP0/PP-last score records are authoritative")
            key = (meta["cell_index"], meta["dp_rank"], meta["cp_rank"])
            _require(key not in ranks, "duplicate_rank_slice", str(key))
            _require(0 <= meta["dp_rank"] < meta["dp_size"] and meta["dp_size"] >= 1,
                     "invalid_dp_rank", str(key))
            dimensions = (meta["dp_size"], meta["cp_size"], meta["tp_size"], meta["pp_size"])
            cell = meta["cell_index"]
            _require(cell not in topology or topology[cell] == dimensions,
                     "rank_topology_mismatch", str(path))
            topology[cell] = dimensions
            ranks.add(key)
            count = len(batch["sample_indices"])
            for field in ("log_probs", "total_lengths", "response_lengths"):
                _require(len(batch[field]) == count, "score_row_count_mismatch", field)
            for field in ("tokens", "loss_masks", "max_seq_lens"):
                if field in batch:
                    _require(len(batch[field]) == count, "score_row_count_mismatch", field)
            for row, index in enumerate(batch["sample_indices"]):
                indexed[int(index)].append((batch, row, str(path)))
        except Exception as error:
            issues.append({"path": str(path), **_issue(error)})
    if not paths:
        issues.append({"code": "score_artifacts_missing", "detail": stem})
    for cell, (dp_size, cp_size, _, _) in topology.items():
        expected = {(cell, dp, cp) for dp in range(dp_size) for cp in range(cp_size)}
        if expected - ranks:
            issues.append({"code": "missing_rank_slice", "detail": str(sorted(expected - ranks))})
    return indexed, issues


def _assemble_scores(slices, sample, mask):
    _require(bool(slices), "score_sample_missing", "No trainer scores for this original sample")
    first = slices[0][0]["metadata"]
    count = sample["response_length"]
    output, occupied = torch.empty(count, dtype=torch.float64), torch.zeros(count, dtype=torch.bool)
    seen = set()
    for batch, row, path in slices:
        meta = batch["metadata"]
        for field in ("weight_version", "cell_index", "dp_rank", "dp_size", "cp_size", "tp_size", "pp_size",
                      "qkv_format", "response_layout", "allgather_cp", "rollout_temperature", "log_probs_backend",
                      "true_on_policy_mode", "use_rollout_sampling_mask"):
            _require(meta[field] == first[field], "score_metadata_mismatch", f"{field}: {path}")
        _require(meta["cp_rank"] not in seen, "duplicate_sample_slice", path)
        seen.add(meta["cp_rank"])
        total, response = batch["total_lengths"][row], batch["response_lengths"][row]
        _require(total == len(sample["tokens"]) and response == count, "score_token_boundary_mismatch", path)
        _require("tokens" in batch, "trainer_input_tokens_missing", "Native score payload has no consumed token receipt")
        _require(torch.equal(_vector(batch["tokens"][row], "trainer tokens", dtype=torch.int64),
                             _vector(sample["tokens"], "sample tokens", dtype=torch.int64)),
                 "trainer_token_mismatch", path)
        _require("loss_masks" in batch, "trainer_input_mask_missing", "Native score payload has no original-mask receipt")
        trainer_mask = _vector(batch["loss_masks"][row], "trainer original mask")
        _require(len(trainer_mask) == count and torch.equal(trainer_mask, mask.to(torch.float64)),
                 "trainer_mask_mismatch", path)
        maximum = batch.get("max_seq_lens", [None] * len(batch["sample_indices"]))[row]
        positions = _response_positions(meta, total, response, maximum)
        values = _vector(batch["log_probs"][row], "trainer scores")
        _require(len(values) == len(positions), "score_position_count_mismatch", path)
        _require(not bool(occupied[positions].any()), "overlapping_cp_positions", path)
        output[positions], occupied[positions] = values, True
    _require(seen == set(range(first["cp_size"])) and bool(occupied.all()),
             "missing_cp_slice", "Every CP rank and every original response position must be present")
    _require(first["weight_version"] is not None and str(first["weight_version"]),
             "trainer_version_missing", "Trainer actual weight version is absent")
    return output, first


def _prefill(sample, version):
    scored = sample["metadata"].get("student_rescoring")
    _require(isinstance(scored, dict) and scored.get("status") == "measured", "prefill_missing", str(scored))
    _require(scored.get("token_ids_match") is True and scored.get("training_logprobs_replaced") is False,
             "prefill_token_or_role_mismatch", "Prefill must score identical tokens without replacing native training scores")
    _require(scored.get("versions_match") is True and scored.get("scored_weight_versions") == [version]
             and scored.get("sampled_weight_versions") == [version],
             "prefill_version_mismatch", "Prefill actual consumed version differs or is absent")
    values = _vector(scored["response_logprobs"], "prefill scores")
    _require(len(values) == sample["response_length"], "prefill_shape_mismatch", "Prefill response coverage differs")
    return values


def _token_metrics(train, infer, *, sample, mask, threshold):
    _require(len(infer) == len(mask), "inference_shape_mismatch", "Inference scores differ from original response length")
    positions = torch.nonzero(mask).flatten()
    finite = torch.isfinite(train) & torch.isfinite(infer)
    invalid = int((mask & ~finite).sum())
    selected = positions[finite[positions]]
    delta = train[selected] - infer[selected]
    invalid_delta = ~torch.isfinite(delta)
    # Finite native values can still overflow subtraction. Retain the original
    # denominator and report the missing comparison, never sanitize it to zero.
    subtraction_nonfinite = int(invalid_delta.sum())
    selected, delta = selected[~invalid_delta], delta[~invalid_delta]
    ratio = delta.exp()
    k3_forward, k3_reverse = ratio * delta - ratio + 1, ratio - 1 - delta
    derived_nonfinite = int((~torch.isfinite(k3_forward) | ~torch.isfinite(k3_reverse) | ~torch.isfinite(delta)).sum())
    issues = []
    if invalid:
        issues.append({"code": "nonfinite_valid_token", "detail": str(invalid)})
    if derived_nonfinite:
        issues.append({"code": "nonfinite_unclamped_k3", "detail": str(derived_nonfinite)})
    if subtraction_nonfinite:
        issues.append({"code": "nonfinite_logprob_difference", "detail": str(subtraction_nonfinite)})
    if not len(positions):
        issues.append({"code": "zero_target_denominator", "detail": "No original eligible completion tokens"})
    tis = MisConfig()
    records = []
    for row, position in enumerate(selected.tolist()):
        records.append({
            "source_uid": sample["metadata"]["source"]["uid"], "sample_index": sample["index"],
            "response_position": position, "absolute_position": len(sample["tokens"]) - len(mask) + position,
            "token_id": sample["tokens"][len(sample["tokens"]) - len(mask) + position],
            "train_logprob": float(train[position]), "inference_logprob": float(infer[position]),
            "delta": float(delta[row]), "abs_error": float(delta[row].abs()),
            "ratio": _json_number(ratio[row]), "k3_r_d_minus_r_plus_1": _json_number(k3_forward[row]),
            "k3_r_minus_1_minus_d": _json_number(k3_reverse[row]),
            "tis_retained": bool(tis.tis_lower_bound <= ratio[row] <= tis.tis_upper_bound),
        })
    result = _aggregate_metrics(records, expected_tokens=len(positions), missing_tokens=invalid + subtraction_nonfinite,
                                zero_target_samples=int(not len(positions)), threshold=threshold, issues=issues)
    result.update(nonfinite_valid_tokens=invalid, nonfinite_unclamped_k3=derived_nonfinite,
                  nonfinite_logprob_differences=subtraction_nonfinite,
                  nonfinite_masked_positions=int((~mask & ~finite).sum()))
    return result, records


def _json_number(value):
    value = float(value)
    return value if math.isfinite(value) else None


def _aggregate_metrics(records, *, expected_tokens, missing_tokens, zero_target_samples, threshold, issues):
    values = torch.tensor([record["abs_error"] for record in records], dtype=torch.float64)
    mean = math.fsum(value / len(values) for value in values.tolist()) if len(values) else None
    tails = {f"abs_p{int(q * 100)}": _json_number(values.quantile(q)) if len(values) else None for q in (0.95, 0.99)}
    worst = sorted(records, key=lambda record: record["abs_error"], reverse=True)[:5]
    verdict = "INCOMPLETE" if issues or missing_tokens or expected_tokens is None or zero_target_samples or not records else "FAIL" if mean > threshold else "PASS"
    k3 = {}
    for form in ("k3_r_d_minus_r_plus_1", "k3_r_minus_1_minus_d"):
        terms = [record[form] for record in records]
        k3[form] = {"mean": math.fsum(term / len(terms) for term in terms) if terms and all(x is not None for x in terms) else None,
                    "nonfinite_tokens": sum(x is None for x in terms)}
    return {"verdict": verdict, "issues": issues, "expected_valid_tokens": expected_tokens,
            "compared_finite_tokens": len(records), "missing_or_nonfinite_tokens": missing_tokens,
            "zero_target_samples": zero_target_samples, "abs_mean": mean, **tails,
            "abs_max": _json_number(values.max()) if len(values) else None, "worst_tokens": worst, **k3,
            "sampling_distribution": "student_decode", "delta_definition": "train_logprob - inference_logprob"}


def _sample_summary(sample, frozen, slices, population, threshold):
    summary = {"source_uid": frozen["uid"], "stratum": frozen["stratum"], "sample_index": sample.get("index"),
               "response_tokens": sample.get("response_length"), "expected_valid_tokens": None,
               "zero_target": None, "issues": [], "comparisons": {}}
    records = {name: [] for name in ("decode", "prefill")}
    try:
        mask = _mask(sample)
        summary.update(expected_valid_tokens=int(mask.sum()), zero_target=not bool(mask.any()))
        _source_check(sample, frozen, population)
        version = _decode_version(sample, frozen["prompt_token_count"])
        train, meta = _assemble_scores(slices, sample, mask)
        _require(str(meta["weight_version"]) == version, "trainer_decode_version_mismatch",
                 f"Trainer {meta['weight_version']} versus consumed {version}; never inferred from rollout index")
        summary["consumed_weight_version"] = version
    except Exception as error:
        summary["issues"].append(_issue(error))
        return summary, records
    for name in records:
        try:
            _probability_check(sample, meta, name)
            infer = _vector(sample["rollout_log_probs"], "decode scores") if name == "decode" else _prefill(sample, version)
            summary["comparisons"][name], records[name] = _token_metrics(train, infer, sample=sample, mask=mask, threshold=threshold)
        except Exception as error:
            summary["comparisons"][name] = {"verdict": "INCOMPLETE", "issues": [_issue(error)]}
    teacher = sample.get("teacher_log_probs")
    if teacher is not None:
        try:
            receipt = sample["metadata"].get("teacher_scoring", {})
            _require(receipt.get("token_ids_match") is True and receipt.get("scored_tokens") == len(mask),
                     "teacher_token_receipt_missing", "Teacher must score the exact student completion")
            _require(sample["metadata"].get("probability_definition", {}).get("teacher") == "full_vocabulary_log_softmax",
                     "teacher_probability_definition_missing", "Teacher probability definition is undeclared")
            teacher = _vector(teacher, "teacher scores")
            decode = _vector(sample["rollout_log_probs"], "decode scores")
            _require(len(teacher) == len(mask), "teacher_shape_mismatch", "Teacher response length differs")
            _require(bool(torch.isfinite(teacher[mask]).all()), "teacher_nonfinite", "Teacher eligible scores are nonfinite")
            measured, records["teacher_student"] = _token_metrics(teacher, decode, sample=sample, mask=mask, threshold=threshold)
            for token in records["teacher_student"]:
                token["teacher_logprob"] = token.pop("train_logprob")
                token.pop("tis_retained")
            # D8 is a same-student gate, not a teacher/student divergence threshold.
            measured["verdict"] = "INCOMPLETE" if measured["verdict"] == "INCOMPLETE" else "DIAGNOSTIC"
            measured["delta_definition"] = "teacher_logprob - student_decode_logprob"
            summary["comparisons"]["teacher_student"] = measured
        except Exception as error:
            summary["comparisons"]["teacher_student"] = {"verdict": "INCOMPLETE", "issues": [_issue(error)]}
    return summary, records


def _comparison_summary(samples, records, name, threshold, issues):
    result = {}
    for stratum in ("overall", *(name for name, _, _ in LENGTH_STRATA)):
        rows = [row for row in samples if stratum == "overall" or row["stratum"] == stratum]
        chosen = [token for row in rows for token in records.get(row["source_uid"], {}).get(name, [])]
        faults = list(issues)
        faults.extend(issue for row in rows for issue in row["issues"])
        faults.extend(issue for row in rows for issue in row["comparisons"].get(name, {}).get("issues", []))
        if any(name not in row["comparisons"] for row in rows):
            faults.append({"code": "comparison_missing", "detail": name})
        if not rows:
            faults.append({"code": "missing_stratum", "detail": stratum})
        expected = sum(row["expected_valid_tokens"] or 0 for row in rows)
        unknown = sum(row["expected_valid_tokens"] is None for row in rows)
        missing = expected - len(chosen)
        result[stratum] = _aggregate_metrics(chosen, expected_tokens=expected if not unknown else None,
                                             missing_tokens=missing, zero_target_samples=sum(row["zero_target"] is True for row in rows),
                                             threshold=threshold, issues=faults)
        result[stratum]["unknown_denominator_samples"] = unknown
        result[stratum]["sample_count"] = len(rows)
        for field in ("nonfinite_valid_tokens", "nonfinite_unclamped_k3", "nonfinite_logprob_differences", "nonfinite_masked_positions"):
            result[stratum][field] = sum(row["comparisons"].get(name, {}).get(field, 0) for row in rows)
    verdict = _verdict([row["verdict"] for row in result.values()])
    return {"verdict": verdict, **result}


def _teacher_summary(samples, records, threshold, issues):
    result = _comparison_summary(samples, records, "teacher_student", threshold, issues)
    for stratum in ("overall", *(name for name, _, _ in LENGTH_STRATA)):
        row = result[stratum]
        row["verdict"] = "INCOMPLETE" if row["verdict"] == "INCOMPLETE" else "DIAGNOSTIC"
        row["delta_definition"] = "teacher_logprob - student_decode_logprob"
    result["verdict"] = "INCOMPLETE" if any(result[name]["verdict"] == "INCOMPLETE" for name in ("overall", *(name for name, _, _ in LENGTH_STRATA))) else "DIAGNOSTIC"
    return result


def _verdict(values):
    return "INCOMPLETE" if not values or "INCOMPLETE" in values else "FAIL" if "FAIL" in values else "PASS"


def _checkpoint(run_dir, population, frozen, rollout_id, dataset, threshold):
    raw_path = run_dir / "rollout_data" / f"eval_{rollout_id}.pt"
    stem = f"eval_{quote(dataset, safe='')}_{rollout_id}"
    paths = sorted((run_dir / "train_data").glob(f"{stem}_*.pt"))
    slices, issues = _score_slices(paths, rollout_id, stem)
    raw_samples, seen_indices = {}, set()
    try:
        dump = torch.load(raw_path, map_location="cpu", weights_only=False)
        _require(dump["rollout_id"] == rollout_id, "checkpoint_mismatch", str(raw_path))
        names = dump["metadata"]["eval_dataset_names"]
        _require(len(names) == len(dump["samples"]), "dataset_row_count_mismatch", str(raw_path))
        for name, sample in zip(names, dump["samples"], strict=True):
            if name != dataset:
                continue
            uid = sample["metadata"]["source"]["uid"]
            _require(uid in frozen, "unexpected_monitoring_identity", uid)
            _require(uid not in raw_samples and sample["index"] not in seen_indices,
                     "duplicate_monitoring_sample", uid)
            raw_samples[uid] = sample
            seen_indices.add(sample["index"])
        _require(not (set(slices) - seen_indices), "unexpected_score_sample", str(set(slices) - seen_indices))
    except Exception as error:
        issues.append({"path": str(raw_path), **_issue(error)})
    summaries, records = [], {}
    for uid, row in frozen.items():
        if uid not in raw_samples:
            summaries.append({"source_uid": uid, "stratum": row["stratum"], "sample_index": None,
                              "response_tokens": None, "expected_valid_tokens": None, "zero_target": None,
                              "comparisons": {}, "issues": [{"code": "monitoring_sample_missing", "detail": uid}]})
            continue
        sample = raw_samples[uid]
        summary, tokens = _sample_summary(sample, row, slices.get(sample["index"], []), population, threshold)
        summaries.append(summary)
        records[uid] = tokens
    comparisons = {name: _comparison_summary(summaries, records, name, threshold, issues) for name in ("decode", "prefill")}
    decode_tokens = [token for values in records.values() for token in values["decode"]]
    tis = MisConfig()
    checkpoint = {"rollout_id": rollout_id, "verdict": _verdict([row["verdict"] for row in comparisons.values()]),
                  "issues": issues, "raw_artifacts": {"samples": str(raw_path), "scores": [str(path) for path in paths]},
                  "consumed_weight_versions": sorted({row["consumed_weight_version"] for row in summaries if "consumed_weight_version" in row}),
                  "samples": summaries, **comparisons,
                  "tis": {"bounds_inclusive": [tis.tis_lower_bound, tis.tis_upper_bound],
                          "original_valid_tokens": comparisons["decode"]["overall"]["expected_valid_tokens"],
                          "measurable_tokens": len(decode_tokens), "retained_tokens": sum(token["tis_retained"] for token in decode_tokens),
                          "retained_fraction_of_measurable": sum(token["tis_retained"] for token in decode_tokens) / len(decode_tokens) if decode_tokens else None,
                          "acceptance_uses_pre_tis_population": True}}
    if any("teacher_student" in row["comparisons"] for row in summaries):
        checkpoint["teacher_student_sampled_divergence"] = _teacher_summary(summaries, records, threshold, issues)
    return checkpoint, records


def _publication_checks(run_dir, checkpoints):
    """Bind raw forwards to native publisher receipts, never to schedule-derived versions.

    Megatron model.py increments the model-companion counter only after a
    successful optimizer.step(). actor.py publishes that same counter; the
    controller emits WeightUpdateResultEvent, then main records engine checksums.
    NORMAL alone does not imply a successful optimizer update. Counter deltas
    are valid only within one load epoch and a complete native publication chain.
    """
    directory = run_dir / "events"
    result = {"verdict": "INCOMPLETE", "issues": [], "events_directory": str(directory),
              "baseline_weight_version": None, "final_published_weight_version": None,
              "successful_optimizer_updates": None, "skipped_optimizer_updates": None,
              "updated_monitoring_positions": [], "publications": [],
              "update_count_evidence": "Megatron model-companion counter increments only after successful optimizer.step(); NORMAL is attempt completion only"}
    try:
        events = EventReader(directory, strict=True, event_types=(
            WeightUpdateResultEvent, TrainGroupStepEndEvent, InferenceEngineWeightChecksumEvent,
            InferenceEngineChecksumCollectionFailedEvent,
        )).read()
    except Exception as error:
        result["issues"].append({"code": "native_event_artifacts_corrupt", "detail": str(error)})
        return result
    try:
        _require(events, "native_update_receipts_missing", "No native update/publication events")
        publications = sorted((event for event in events if isinstance(event, WeightUpdateResultEvent)
                               and isinstance(event.source, TrainerControllerProcessIdentity)
                               and event.source.trainer_id == "actor" and event.source.model_id is None),
                              key=lambda event: event.timestamp)
        _require(publications, "native_publication_receipts_missing", "No unnamed actor publisher receipts")
        source = publications[0].source
        _require(all(event.source == source for event in publications), "publisher_identity_mismatch", "Publisher identity changed")
        startup = [event for event in publications if event.rollout_id is None]
        _require(len(startup) == 1 and publications[0] is startup[0], "baseline_publication_missing_or_duplicate",
                 "Fresh baseline requires one native out-of-loop startup publication")
        baseline = startup[0]
        _require(baseline.published_version is not None, "baseline_publication_missing", "Initial actor weights were not published")
        result["baseline_weight_version"] = baseline.published_version
        final = publications[-1]
        result["final_published_weight_version"] = final.published_version
        _require(all(event.debug_trainer_load_state_timestamp == baseline.debug_trainer_load_state_timestamp for event in publications),
                 "trainer_load_epoch_changed", "Counter deltas cannot qualify updates across a trainer reload")
        _require(len({event.debug_weight_update_id for event in publications}) == len(publications),
                 "duplicate_publication_receipt", "Native publication IDs repeat")
        _require(all(event.published_version == event.candidate_version and event.updated_cell_ids and not event.failed_cell_ids
                     for event in publications), "publication_failed_or_partial", "Actor candidate was not fully published")
        positions = [event.rollout_id for event in publications[1:]]
        expected_positions = list(range(checkpoints[-1]["rollout_id"] + 1))
        _require(positions == expected_positions, "native_publication_coverage_incomplete",
                 "Need each planned native publication through the final position, not a version inferred from that position")
        steps = [event for event in events if isinstance(event, TrainGroupStepEndEvent)
                 and event.role == "actor" and event.source == source]
        by_position = defaultdict(list)
        for event in steps:
            by_position[event.rollout_id].append(event)
        _require(set(by_position) == set(expected_positions), "native_train_attempt_coverage_incomplete",
                 "Native actor group completion receipts do not cover the planned attempts")
        previous = baseline.published_version
        for event in publications[1:]:
            step = max(by_position[event.rollout_id], key=lambda event: event.timestamp)
            _require(step.timestamp < event.timestamp and step.cell_outcomes and all(
                isinstance(outcomes, list) and outcomes and all(outcome == "normal" for outcome in outcomes)
                for outcomes in step.cell_outcomes.values()), "native_train_attempt_unsettled",
                f"No completed actor group attempt before publication {event.debug_weight_update_id}")
            delta = event.published_version - previous
            _require(delta in (0, 1), "native_update_counter_invalid",
                     "D9's one-optimizer-step batch must advance the native counter by zero or one")
            result["publications"].append({"rollout_id": event.rollout_id, "candidate_version": event.candidate_version,
                                           "published_version": event.published_version, "optimizer_counter_delta": delta,
                                           "debug_weight_update_id": event.debug_weight_update_id})
            previous = event.published_version
        result["successful_optimizer_updates"] = sum(row["optimizer_counter_delta"] for row in result["publications"])
        result["skipped_optimizer_updates"] = len(expected_positions) - result["successful_optimizer_updates"]
        _require(result["successful_optimizer_updates"] > 0, "successful_updated_version_missing",
                 "NORMAL attempts or repeated baseline publications do not prove any successful optimizer update")
        selected_events = [event for event in events if (
            isinstance(event, (WeightUpdateResultEvent, TrainGroupStepEndEvent)) and event.source == source
            or isinstance(event, (InferenceEngineWeightChecksumEvent, InferenceEngineChecksumCollectionFailedEvent))
            and event.trainer_model_id is None
        )]
        coverage = inference_engine_weight_checksum_coverage.check(selected_events, include_latest=True)
        _require(not coverage, "native_publication_checksum_incomplete", "; ".join(issue.description for issue in coverage))
        _require(not inference_engine_weight_checksum_consistency.check(selected_events),
                 "native_engine_checksum_mismatch", "Engines of a publication have different model tensors")
        checksums = {event.debug_weight_update_id: event for event in selected_events
                     if isinstance(event, InferenceEngineWeightChecksumEvent)}
        baseline_hashes = checksums[baseline.debug_weight_update_id].engine_snapshots[0].tensor_checksums
        by_publication_position = {event.rollout_id: event for event in publications}
        for checkpoint in checkpoints:
            position = checkpoint["rollout_id"]
            publication = baseline if position == 0 else by_publication_position[position]
            _require(checkpoint["consumed_weight_versions"] == [str(publication.published_version)],
                     "final_monitor_publication_version_mismatch" if checkpoint is checkpoints[-1] else "checkpoint_publication_version_mismatch",
                     f"Monitoring position {position} does not consume actual publisher version {publication.published_version}")
            if publication.published_version > baseline.published_version:
                hashes = checksums[publication.debug_weight_update_id].engine_snapshots[0].tensor_checksums
                _require(hashes.keys() == baseline_hashes.keys(), "engine_checksum_tensor_set_mismatch",
                         "Updated checksum observation has different model tensor identities")
                _require(hashes != baseline_hashes, "updated_engine_weights_unchanged",
                         "An updated monitoring version has no observed model-tensor change from baseline")
                result["updated_monitoring_positions"].append(position)
        _require(result["updated_monitoring_positions"], "updated_forward_evidence_missing",
                 "No monitoring trainer/decode/prefill forwards consumed a successfully updated model")
        result["verdict"] = "PASS"
    except Exception as error:
        result["issues"].append(_issue(error))
    return result


def inspect(run_dir, population_report, *, dataset="monitor", checkpoints=(0, 19, 39, 59, 79, 99), threshold=0.03):
    """Return JSON-compatible evidence. Corrupt/missing samples never abort later checkpoints."""
    _require(threshold == 0.03, "acceptance_threshold_changed", "D8's accepted threshold is exactly 0.03")
    _require(tuple(checkpoints) == (0, 19, 39, 59, 79, 99), "monitoring_schedule_changed", "D9 requires all six native monitoring positions")
    result = {"schema_version": 1, "task_id": "QWEN-P2-NUMERIC-REPORT", "verdict": "INCOMPLETE",
              "threshold": threshold, "run_dir": str(run_dir), "population_report": str(population_report),
              "dataset": dataset, "required_checkpoint_positions": list(checkpoints), "issues": [], "checkpoints": [],
              "learning_conclusion": "No convergence or capability-improvement claim; teacher/student values are sampled-token diagnostics",
              "verification_scope": "Offline native-artifact inspection; no platform calls or training control"}
    try:
        population = json.loads(population_report.read_text())
        frozen = _population(population)
    except Exception as error:
        result["issues"].append(_issue(error))
        return result
    result["monitoring_uids"] = list(frozen)
    all_samples, all_records = [], {}
    for rollout_id in checkpoints:
        checkpoint, records = _checkpoint(run_dir, population, frozen, rollout_id, dataset, threshold)
        result["checkpoints"].append(checkpoint)
        for row in checkpoint["samples"]:
            key = f"{rollout_id}:{row['source_uid']}"
            all_samples.append({**row, "source_uid": key})
            all_records[key] = records.get(row["source_uid"], {})
    faults = [issue for checkpoint in result["checkpoints"] for issue in checkpoint["issues"]]
    result["aggregate"] = {name: _comparison_summary(all_samples, all_records, name, threshold, faults) for name in ("decode", "prefill")}
    if any("teacher_student" in row["comparisons"] for row in all_samples):
        result["aggregate"]["teacher_student_sampled_divergence"] = _teacher_summary(all_samples, all_records, threshold, faults)
    result["weight_publication"] = _publication_checks(run_dir, result["checkpoints"])
    result["verdict"] = _verdict([checkpoint["verdict"] for checkpoint in result["checkpoints"]]
                                + [result["weight_publication"]["verdict"]])
    result["checkpoint_verdict_counts"] = dict(Counter(checkpoint["verdict"] for checkpoint in result["checkpoints"]))
    # A cross-checkpoint mean is descriptive only: every checkpoint/stratum must pass.
    result["aggregate"]["verdict"] = result["verdict"]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--population-report", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--dataset", default="monitor")
    parser.add_argument("--threshold", type=float, default=0.03)
    args = parser.parse_args()
    report = inspect(args.run_dir, args.population_report, dataset=args.dataset, threshold=args.threshold)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print("QWEN35_NUMERICAL_ACCEPTANCE", report["verdict"], str(args.report), flush=True)
    # This is a reporting soft gate. An INCOMPLETE/FAIL verdict is not training control.


if __name__ == "__main__":
    main()
