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

Teacher diagnostics use the original reward.teacher_response input-logprob
array: native eval is dumped before reward post-processing fills teacher_log_probs.
--teacher-ready binds startup identity to its sibling native student-launch.json.
The pinned input-probability semantic argument is explicitly source/launch-derived,
not a sampled request, model revision, or runtime-kernel receipt.
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
from miles.rollout.on_policy_distillation import _score_payload, _trim_input_field
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


def _token_metrics(train, infer, *, sample, mask, threshold, missing_positions=None):
    _require(len(infer) == len(mask), "inference_shape_mismatch", "Inference scores differ from original response length")
    positions = torch.nonzero(mask).flatten()
    missing = torch.zeros_like(mask) if missing_positions is None else missing_positions
    finite = torch.isfinite(train) & torch.isfinite(infer) & ~missing
    nonfinite = (~torch.isfinite(train) & ~missing) | ~torch.isfinite(infer)
    invalid = int((mask & nonfinite).sum())
    missing_valid = int((mask & missing).sum())
    unavailable = int((mask & (nonfinite | missing)).sum())
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
    if missing_valid:
        issues.append({"code": "missing_valid_token", "detail": str(missing_valid)})
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
    result = _aggregate_metrics(records, expected_tokens=len(positions), missing_tokens=unavailable + subtraction_nonfinite,
                                zero_target_samples=int(not len(positions)), threshold=threshold, issues=issues)
    result.update(nonfinite_valid_tokens=invalid, missing_valid_tokens=missing_valid, nonfinite_unclamped_k3=derived_nonfinite,
                  nonfinite_logprob_differences=subtraction_nonfinite,
                  nonfinite_masked_positions=int((~mask & nonfinite).sum()),
                  missing_masked_positions=int((~mask & missing).sum()))
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


def _argv_value(argv, option):
    _require(isinstance(argv, list) and argv.count(option) == 1, "teacher_launch_argument_missing_or_duplicate", option)
    index = argv.index(option) + 1
    _require(index < len(argv) and isinstance(argv[index], str) and not argv[index].startswith("--"),
             "teacher_launch_argument_missing_or_duplicate", option)
    return argv[index]


def _teacher_contract(run_dir, teacher_ready):
    result = {"status": "incomplete", "issues": [], "teacher_ready": str(teacher_ready) if teacher_ready else None,
              "probability_definition": {"definition": "full_vocabulary_log_softmax",
                  "basis": "source_and_launch_contract_derived", "sample_recorded": False,
                  "source_commit": "056f871a7ee8b4573832049011f0fdf52589cfd8",
                  "source_url": "https://raw.githubusercontent.com/sgl-project/sglang/056f871a7ee8b4573832049011f0fdf52589cfd8/python/sglang/srt/layers/logprob_processor.py",
                  "producer": "qwen_alignment.score_teacher -> on_policy_distillation._score_payload",
                  "explanation": "The task-pinned deterministic SGLang input-logprob processor applies log_softmax to raw logits; temperature=0 selects decoding and does not scale input logprobs."},
              "evidence_limits": ["Request fields and probability semantics are source/launch-contract-derived, not sample-recorded receipts.",
                                  "Teacher identity is startup model_info plus the frozen-teacher launch contract; no per-response model revision or consumed teacher weight version is recorded."]}
    try:
        _require(teacher_ready is not None, "teacher_identity_unbound", "Provide the native teacher-ready.json rendezvous")
        ready = json.loads(teacher_ready.read_text())
        launch_path = teacher_ready.parent / "student-launch.json"
        launch = json.loads(launch_path.read_text())
        result["student_launch"] = str(launch_path)
        _require(ready["status"] == "ready" and ready["role"] == "teacher" and ready["rank"] == 0,
                 "teacher_readiness_invalid", "Need the head teacher's successful native readiness receipt")
        _require(launch["role"] == "student" and launch["rank"] == 0 and ready["image"]
                 and (ready["job"], ready["pair"], ready["image"]) == (launch["job"], launch["pair"], launch["image"]),
                 "teacher_launch_identity_mismatch", "Student and teacher receipts belong to different jobs, pairs or images")
        server, student = ready["argv"], launch["argv"]
        _require(server[1:4] == ["-B", "-m", "sglang.launch_server"]
                 and student[1:4] == ["-B", "-m", "tests.manual.agent_opd.run_qwen35_opd"],
                 "teacher_launch_contract_unknown", "Receipts do not name the supported native teacher/student producers")
        expected = _argv_value(student, "--teacher")
        _require(expected == ready["model_info"]["model_path"] == ready["model_path"] == _argv_value(server, "--model-path")
                 and expected != _argv_value(student, "--student") == launch["model_path"],
                 "teacher_model_identity_mismatch", "Startup model_info/server argv do not match the student's expected distinct teacher asset")
        _require(ready["url"] == launch["teacher_url"] == _argv_value(student, "--teacher-url")
                 == f"http://{ready['ip']}:{_argv_value(server, '--port')}/generate",
                 "teacher_endpoint_identity_mismatch", "Readiness and student launch do not identify the same native teacher endpoint")
        expected_run = Path(_argv_value(student, "--output-root")) / ready["pair"] / ready["job"]
        _require(expected_run == run_dir.absolute() and _argv_value(student, "--pair") == ready["pair"],
                 "teacher_launch_run_mismatch", "Provided run is not the recorded student output-root/pair/job; relocated copies lack a run-origin receipt")
        _require(server.count("--enable-deterministic-inference") == 1 and _argv_value(server, "--node-rank") == "0",
                 "teacher_probability_contract_unestablished", "The pinned input-logprob semantic argument requires the native deterministic head-server launch")
        request = _score_payload([])
        _require(request == {"input_ids": [], "sampling_params": {"temperature": 0, "max_new_tokens": 0, "skip_special_tokens": False},
                             "return_logprob": True, "logprob_start_len": 0},
                 "teacher_request_contract_changed", "The task producer's input-scoring request shape changed")
        request.pop("input_ids")
        result.update(status="established", endpoint=ready["url"], expected_model_path=expected,
                      startup_model_path=ready["model_info"]["model_path"], job=ready["job"], pair=ready["pair"], image=ready["image"])
        result["probability_definition"]["request_shape_from_source"] = request
        result["probability_definition"]["input_ids_from_source"] = "Exact sample.tokens, without re-tokenization; the request itself is not recorded"
    except FileNotFoundError as error:
        result["issues"].append({"code": "teacher_identity_evidence_missing", "detail": str(error)})
    except Exception as error:
        result["issues"].append(_issue(error))
    return result


def _teacher_diagnostic(sample, mask, contract, threshold):
    measured = _aggregate_metrics([], expected_tokens=int(mask.sum()), missing_tokens=int(mask.sum()),
                                  zero_target_samples=int(not mask.any()), threshold=threshold, issues=[])
    measured.update(verdict="INCOMPLETE", delta_definition="teacher_logprob - student_decode_logprob",
                    missing_valid_tokens=None, nonfinite_valid_tokens=None, nonfinite_masked_positions=None,
                    missing_masked_positions=None, score_source="reward.teacher_response.meta_info.input_token_logprobs",
                    expected_input_score_entries=len(sample["tokens"]), input_score_entries=None)
    try:
        response = (sample.get("reward") or {}).get("teacher_response")
        _require(isinstance(response, dict), "teacher_response_missing", "Native eval precedes reward post-processing; use its preserved raw teacher response, not teacher_log_probs")
        raw = response["meta_info"].get("input_token_logprobs")
        _require(isinstance(raw, list), "teacher_scores_missing", "Raw input-token logprobs are absent")
        measured["input_score_entries"] = len(raw)
        _require(len(raw) == len(sample["tokens"]), "teacher_input_score_coverage_mismatch", "Native logprob_start_len=0 must retain one entry per input token, including its first placeholder")
        _require(all(isinstance(item, (list, tuple)) and len(item) >= 2 for item in raw),
                 "teacher_input_score_shape_mismatch", "Raw input entries must preserve their token IDs, including the first logprob placeholder")
        ids = [item[1] for item in raw]
        _require(all(type(value) is int for value in ids) and ids == sample["tokens"],
                 "teacher_input_token_mismatch", "Rechecked raw teacher input IDs differ from the exact student prefix or completion")
        scores = _trim_input_field(response["meta_info"], "input_token_logprobs", sample["response_length"])
        values = [item[0] for item in scores]
        _require(all(value is None or type(value) in (int, float) for value in values), "teacher_score_value_invalid", "Raw scores must be numeric or explicitly missing")
        missing = torch.tensor([value is None for value in values], dtype=torch.bool)
        # An internal NaN marks an absent value; its separate missing mask excludes
        # it before math and preserves the original denominator and missing count.
        teacher = torch.tensor([math.nan if value is None else value for value in values], dtype=torch.float64)
        measured.update(missing_valid_tokens=int((mask & missing).sum()),
                        nonfinite_valid_tokens=int((mask & ~missing & ~torch.isfinite(teacher)).sum()),
                        missing_masked_positions=int((~mask & missing).sum()),
                        nonfinite_masked_positions=int((~mask & ~missing & ~torch.isfinite(teacher)).sum()))
        receipt = sample["metadata"].get("teacher_scoring", {})
        _require(receipt.get("token_ids_match") is True and receipt.get("scored_tokens") == len(mask),
                 "teacher_token_receipt_missing", "Native score_teacher completion receipt is absent or inconsistent")
        _require(contract and contract["status"] == "established",
                 contract["issues"][0]["code"] if contract and contract["issues"] else "teacher_identity_unbound",
                 contract["issues"][0]["detail"] if contract and contract["issues"] else "Native teacher identity/semantic contract is unbound")
        _require(receipt.get("endpoint") == contract["endpoint"], "teacher_sample_endpoint_mismatch", "Sample's actual score endpoint differs from the bound teacher readiness/launch endpoint")
        definition = sample["metadata"].get("probability_definition", {})
        _require(definition.get("decode") == "full_vocabulary_log_softmax" and definition.get("sampling_distribution") == "student_decode"
                 and all(definition.get("sampling_params", {}).get(name) == value for name, value in (("temperature", 1), ("top_p", 1), ("top_k", -1))),
                 "teacher_student_sampling_definition_unestablished", "Student sampling/probability receipt is missing or transformed")
        decode = _vector(sample["rollout_log_probs"], "decode scores")
        measured, records = _token_metrics(teacher, decode, sample=sample, mask=mask, threshold=threshold, missing_positions=missing)
        if measured["missing_masked_positions"] or measured["nonfinite_masked_positions"]:
            # Native score_teacher validates every completion score, not just
            # target positions. Corrupt masked values cannot be a complete native
            # receipt, although the original mask still owns all metric math.
            measured["issues"].append({"code": "masked_probability_evidence_invalid",
                                       "detail": "Retained masked scores are missing/nonfinite; eligible metrics retain their original mask and denominator"})
            measured["verdict"] = "INCOMPLETE"
        for token in records:
            token["teacher_logprob"] = token.pop("train_logprob")
            token.pop("tis_retained")
        measured.update(verdict="INCOMPLETE" if measured["verdict"] == "INCOMPLETE" else "DIAGNOSTIC",
                        delta_definition="teacher_logprob - student_decode_logprob",
                        score_source="reward.teacher_response.meta_info.input_token_logprobs",
                        teacher_identity={"endpoint": contract["endpoint"], "model_path": contract["startup_model_path"]},
                        probability_basis="source_and_launch_contract_derived",
                        expected_input_score_entries=len(sample["tokens"]), input_score_entries=len(raw))
        return measured, records
    except Exception as error:
        measured["issues"].append(_issue(error))
        return measured, []


def _sample_summary(sample, frozen, slices, population, threshold, teacher_contract=None):
    summary = {"source_uid": frozen["uid"], "stratum": frozen["stratum"], "sample_index": sample.get("index"),
               "response_tokens": sample.get("response_length"), "expected_valid_tokens": None,
               "zero_target": None, "issues": [], "comparisons": {}}
    records = {name: [] for name in ("decode", "prefill")}
    try:
        mask = _mask(sample)
        summary.update(expected_valid_tokens=int(mask.sum()), zero_target=not bool(mask.any()))
        _source_check(sample, frozen, population)
        version = _decode_version(sample, frozen["prompt_token_count"])
    except Exception as error:
        summary["issues"].append(_issue(error))
        summary["comparisons"]["teacher_student"] = {"verdict": "INCOMPLETE", "issues": [_issue(error)]}
        return summary, records
    summary["comparisons"]["teacher_student"], records["teacher_student"] = _teacher_diagnostic(sample, mask, teacher_contract, threshold)
    try:
        train, meta = _assemble_scores(slices, sample, mask)
        _require(str(meta["weight_version"]) == version, "trainer_decode_version_mismatch",
                 f"Trainer {meta['weight_version']} versus consumed {version}; never inferred from rollout index")
        summary["consumed_weight_version"] = version
    except Exception as error:
        summary["issues"].append(_issue(error))
        return summary, records
    for name in ("decode", "prefill"):
        try:
            _probability_check(sample, meta, name)
            infer = _vector(sample["rollout_log_probs"], "decode scores") if name == "decode" else _prefill(sample, version)
            summary["comparisons"][name], records[name] = _token_metrics(train, infer, sample=sample, mask=mask, threshold=threshold)
        except Exception as error:
            summary["comparisons"][name] = {"verdict": "INCOMPLETE", "issues": [_issue(error)]}
    return summary, records


def _comparison_summary(samples, records, name, threshold, issues):
    result = {}
    for stratum in ("overall", *(name for name, _, _ in LENGTH_STRATA)):
        rows = [row for row in samples if stratum == "overall" or row["stratum"] == stratum]
        chosen = [token for row in rows for token in records.get(row["source_uid"], {}).get(name, [])]
        faults = list(issues)
        if name != "teacher_student":
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
        for field in ("nonfinite_valid_tokens", "nonfinite_unclamped_k3", "nonfinite_logprob_differences", "nonfinite_masked_positions", "missing_valid_tokens", "missing_masked_positions"):
            values = [row["comparisons"].get(name, {}).get(field, None if name == "teacher_student" else 0) for row in rows]
            result[stratum][field] = sum(values) if all(value is not None for value in values) else None
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


def _checkpoint(run_dir, population, frozen, rollout_id, dataset, threshold, teacher_contract=None):
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
        summary, tokens = _sample_summary(sample, row, slices.get(sample["index"], []), population, threshold, teacher_contract)
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
        checkpoint["teacher_student_sampled_divergence"] = _teacher_summary(summaries, records, threshold, [issue for issue in issues if issue.get("path") == str(raw_path)])
    return checkpoint, records


def _publication_receipts(events):
    """Classify the unnamed actor's complete native receipt chain.

    train.py's initial sync and eval weight restoration both call update_weights
    without a rollout ID. placement_group.py stamps both checksums as -1; only
    the publication ID, counter, ordered train receipts and full snapshots
    distinguish them. This classifier does not require a completed training run.
    """
    _require(events, "native_update_receipts_missing", "No native update/publication events")
    publications = sorted((event for event in events if isinstance(event, WeightUpdateResultEvent)
                           and isinstance(event.source, TrainerControllerProcessIdentity)
                           and event.source.trainer_id == "actor" and event.source.model_id is None),
                          key=lambda event: event.timestamp)
    _require(publications, "native_publication_receipts_missing", "No unnamed actor publisher receipts")
    baseline = publications[0]
    source = baseline.source
    _require(baseline.rollout_id is None, "baseline_publication_missing_or_duplicate",
             "The first actor receipt must be the out-of-loop initial publication")
    _require(all(event.source == source for event in publications), "publisher_identity_mismatch", "Publisher identity changed")
    _require(all(event.debug_trainer_load_state_timestamp == baseline.debug_trainer_load_state_timestamp for event in publications),
             "trainer_load_epoch_changed", "Counter deltas cannot cross a trainer reload")
    ids = {event.debug_weight_update_id for event in publications}
    _require(len(ids) == len(publications) and all(ids), "duplicate_publication_receipt", "Publication IDs are empty or repeat")
    _require(all(event.published_version is not None and event.published_version >= 0
                 and event.published_version == event.candidate_version and not event.failed_cell_ids
                 and event.updated_cell_ids and len(event.updated_cell_ids) == len(set(event.updated_cell_ids))
                 and set(event.updated_cell_ids) == set(event.snapshot_cell_id_to_hashes) for event in publications),
             "publication_failed_or_partial", "Actor candidate was not fully published to its snapshot")
    records = [event for event in events if isinstance(event, (
        InferenceEngineWeightChecksumEvent, InferenceEngineChecksumCollectionFailedEvent,
    )) and (event.trainer_model_id is None or event.debug_weight_update_id in ids)]
    _require({event.debug_weight_update_id for event in records} == ids,
             "native_publication_checksum_incomplete", "Checksum/publication IDs do not form one complete chain")
    coverage = inference_engine_weight_checksum_coverage.check([*publications, *records], include_latest=True)
    _require(not coverage, "native_publication_checksum_incomplete", "; ".join(issue.description for issue in coverage))
    _require(not inference_engine_weight_checksum_consistency.check(records),
             "native_engine_checksum_mismatch", "Engines of a publication have different full model tensors")
    checksums = {event.debug_weight_update_id: event for event in records}
    steps = sorted((event for event in events if isinstance(event, TrainGroupStepEndEvent)
                    and event.role == "actor" and event.source == source), key=lambda event: event.timestamp)
    planned, restorations, deltas = [], [], {}
    previous = None
    for index, event in enumerate(publications):
        checksum = checksums[event.debug_weight_update_id]
        _require(checksum.rollout_id == (-1 if event.rollout_id is None else event.rollout_id)
                 and checksum.source == checksums[baseline.debug_weight_update_id].source
                 and checksum.source.component == "main" and event.timestamp < checksum.timestamp,
                 "native_publication_checksum_origin_mismatch", "Checksum role/position/time does not match its publisher")
        _require(all(snapshot.tensor_checksums for snapshot in checksum.engine_snapshots),
                 "native_publication_checksum_empty", "Full eligible tensor dictionaries are required")
        if index + 1 < len(publications):
            _require(checksum.timestamp < publications[index + 1].timestamp,
                     "native_publication_order_ambiguous", "A subsequent publication precedes this checksum observation")
        if previous is None:
            _require(not any(step.timestamp <= checksum.timestamp for step in steps),
                     "baseline_publication_after_train_attempt", "Initial checksum is not a pre-training observation")
        else:
            pending = [step for step in steps if previous.timestamp < step.timestamp <= checksum.timestamp]
            delta = event.published_version - previous.weight_version
            if event.rollout_id is None:
                _require(delta == 0, "restoration_version_mismatch", "Out-of-loop restoration must preserve the published counter")
                _require(not pending, "restoration_has_unpublished_train_attempt", "A restore cannot stand in for an optimizer publication")
                restorations.append(event)
            else:
                _require(event.rollout_id == len(planned), "native_publication_coverage_incomplete",
                         "Planned rollout receipts must occur exactly once in native order")
                _require(pending and all(step.rollout_id == event.rollout_id and step.timestamp < event.timestamp for step in pending)
                         and len({step.attempt for step in pending}) == len(pending)
                         and [step.attempt for step in pending] == sorted(step.attempt for step in pending)
                         and pending[-1].cell_outcomes and all(
                             isinstance(outcomes, list) and outcomes and all(outcome == "normal" for outcome in outcomes)
                             for outcomes in pending[-1].cell_outcomes.values()),
                         "native_train_attempt_unsettled", "Planned publication lacks its settled, ordered actor attempt")
                _require(delta in (0, 1), "native_update_counter_invalid", "D9's one-step batch advances the counter by zero or one")
                planned.append(event)
                deltas[event.debug_weight_update_id] = delta
            if delta == 0:
                _require(checksum.engine_snapshots[0].tensor_checksums == previous.engine_snapshots[0].tensor_checksums,
                         "same_version_engine_checksum_mismatch", "Repeated native version has different full eligible tensor bytes")
        previous = checksum
    _require(not any(step.timestamp > previous.timestamp for step in steps),
             "native_train_attempt_unpublished", "Actor completion after the last receipt has no planned publication")
    return {"baseline": baseline, "planned": planned, "restorations": restorations,
            "checksums": checksums, "deltas": deltas}


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
               "updated_monitoring_positions": [], "publications": [], "restorations": [],
               "baseline_publication_id": None, "final_planned_publication_id": None,
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
        receipts = _publication_receipts(events)
        baseline, publications, checksums = receipts["baseline"], receipts["planned"], receipts["checksums"]
        result["baseline_weight_version"] = baseline.published_version
        result["baseline_publication_id"] = baseline.debug_weight_update_id
        result["final_published_weight_version"] = publications[-1].published_version if publications else baseline.published_version
        result["restorations"] = [{"rollout_id": None, "published_version": event.published_version,
                                   "debug_weight_update_id": event.debug_weight_update_id} for event in receipts["restorations"]]
        positions = [event.rollout_id for event in publications]
        expected_positions = list(range(checkpoints[-1]["rollout_id"] + 1))
        _require(positions == expected_positions, "native_publication_coverage_incomplete",
                 "Need each planned native publication through the final position, not a version inferred from that position")
        result["final_planned_publication_id"] = publications[-1].debug_weight_update_id
        for event in publications:
            delta = receipts["deltas"][event.debug_weight_update_id]
            result["publications"].append({"rollout_id": event.rollout_id, "candidate_version": event.candidate_version,
                                           "published_version": event.published_version, "optimizer_counter_delta": delta,
                                           "debug_weight_update_id": event.debug_weight_update_id})
        result["successful_optimizer_updates"] = sum(row["optimizer_counter_delta"] for row in result["publications"])
        result["skipped_optimizer_updates"] = len(expected_positions) - result["successful_optimizer_updates"]
        _require(result["successful_optimizer_updates"] > 0, "successful_updated_version_missing",
                 "NORMAL attempts or repeated baseline publications do not prove any successful optimizer update")
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


def inspect(run_dir, population_report, *, dataset="monitor", checkpoints=(0, 19, 39, 59, 79, 99), threshold=0.03, teacher_ready=None):
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
    result["teacher_contract"] = _teacher_contract(run_dir, teacher_ready)
    all_samples, all_records = [], {}
    for rollout_id in checkpoints:
        checkpoint, records = _checkpoint(run_dir, population, frozen, rollout_id, dataset, threshold, result["teacher_contract"])
        result["checkpoints"].append(checkpoint)
        for row in checkpoint["samples"]:
            key = f"{rollout_id}:{row['source_uid']}"
            all_samples.append({**row, "source_uid": key})
            all_records[key] = records.get(row["source_uid"], {})
    faults = [issue for checkpoint in result["checkpoints"] for issue in checkpoint["issues"]]
    result["aggregate"] = {name: _comparison_summary(all_samples, all_records, name, threshold, faults) for name in ("decode", "prefill")}
    if any("teacher_student" in row["comparisons"] for row in all_samples):
        teacher_faults = [issue for checkpoint in result["checkpoints"] for issue in checkpoint["issues"]
                         if issue.get("path") == checkpoint["raw_artifacts"]["samples"]]
        result["aggregate"]["teacher_student_sampled_divergence"] = _teacher_summary(all_samples, all_records, threshold, teacher_faults)
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
    parser.add_argument("--teacher-ready", type=Path, help="Native pair-worker teacher-ready.json; its sibling student-launch.json binds the expected teacher and run")
    args = parser.parse_args()
    report = inspect(args.run_dir, args.population_report, dataset=args.dataset, threshold=args.threshold, teacher_ready=args.teacher_ready)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print("QWEN35_NUMERICAL_ACCEPTANCE", report["verdict"], str(args.report), flush=True)
    # This is a reporting soft gate. An INCOMPLETE/FAIL verdict is not training control.


if __name__ == "__main__":
    main()
