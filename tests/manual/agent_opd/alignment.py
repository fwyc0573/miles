"""Observe same-student prefill probabilities without changing OPD rewards."""

import math
import uuid

from examples.agentic_opd.rollout import score_teacher

from miles.rollout.generate_utils.prefill_logprobs import _build_prefill_scoring_payload, _extract_response_logprobs
from miles.rollout.on_policy_distillation import _post_json
from miles.rollout.sglang_rollout import get_model_url


async def score_glm_teacher(args, sample, **kwargs):
    reward = await score_teacher(args, sample, **kwargs)
    try:
        payload = _build_prefill_scoring_payload(args, sample, {"top_p": 1, "top_k": -1})
        # A distinct existing cache namespace makes this an independent prefill.
        payload["extra_key"] = "alignment-" + uuid.uuid4().hex
        result = await _post_json(
            get_model_url(args, "default"), payload, timeout_secs=args.sglang_router_request_timeout_secs
        )
        scores = _extract_response_logprobs(sample, result["meta_info"])
        if not all(math.isfinite(value) for value in scores):
            raise ValueError("Student prefill returned non-finite logprobs")
        meta = result["meta_info"]
        versions = {str(span["version"]) for span in meta.get("prefill_weight_versions", [])}
        if meta.get("weight_version") is not None:
            versions.add(str(meta["weight_version"]))
        sampled_versions = {str(span.version) for span in sample.all_weight_version_spans}
        sample.metadata["student_rescoring"] = {
            "status": "measured",
            "token_ids_match": True,
            "response_logprobs": scores,
            "scored_weight_versions": sorted(versions),
            "sampled_weight_versions": sorted(sampled_versions),
            "versions_match": bool(versions) and versions == sampled_versions,
            "cache_namespace": "independent",
            "training_logprobs_replaced": False,
        }
    except Exception as error:
        # This auxiliary observation never changes a healthy native OPD step.
        sample.metadata["student_rescoring"] = {
            "status": "unverified",
            "error_type": type(error).__name__,
            "reason": str(error)[:400],
        }
        print("AGENT_OPD_ALIGNMENT_UNVERIFIED", type(error).__name__, str(error)[:400], flush=True)
    return reward
