"""Preserve Qwen3.5 completions and observe frozen-teacher OPD scoring."""

import copy
import json
import math
import uuid

from examples.agentic_opd.glm_turns import token_hash
from sglang.srt.parser.reasoning_parser import ReasoningParser
from sglang.srt.sampling.sampling_params import SamplingParams
from tests.manual.agent_opd.alignment import rescore_student

from miles.rollout import on_policy_distillation as opd
from miles.rollout.base_types import GenerateFnInput, GenerateFnOutput
from miles.rollout.generate_hub.single_turn import generate as generate_single_turn
from miles.rollout.generate_utils.tool_call_utils import create_tool_call_parser
from miles.rollout.sglang_rollout import get_model_url
from miles.utils.types import Sample


def _decode_probability_definition(input: GenerateFnInput) -> dict:
    params = copy.deepcopy(input.sampling_params)
    definition = {"sampling_distribution": "student_decode", "sampling_params": params}
    args = input.args
    if (
        any(params.get(name) != value for name, value in (("temperature", 1), ("top_p", 1), ("top_k", -1)))
        or not args.sglang.common_value("enable_deterministic_inference")
        or args.use_sampling_support_replay
        or args.recompute_logprobs_via_prefill
    ):
        return definition
    # Match actual request modifiers against SGLang's own neutral defaults.
    # Termination, rendering and the RNG seed do not transform token logits.
    passthrough = {
        "temperature", "top_p", "top_k", "max_new_tokens", "stop", "stop_token_ids", "stop_regex",
        "skip_special_tokens", "spaces_between_special_tokens", "no_stop_trim", "sampling_seed",
    }
    try:
        resolved, defaults = SamplingParams(**params), SamplingParams()
    except (TypeError, ValueError):
        return definition
    if any(getattr(resolved, name) != getattr(defaults, name) for name in params.keys() - passthrough):
        return definition
    # Deterministic, untransformed temperature-1 /generate returns vocabulary
    # log_softmax, not support-renormalized sampling logprobs or prefill replacements.
    definition["decode"] = "full_vocabulary_log_softmax"
    return definition


async def generate(input: GenerateFnInput) -> GenerateFnOutput:
    sample = input.sample
    source = sample.metadata["source"]
    prompt_ids = input.state.tokenizer.encode(sample.prompt, add_special_tokens=False)
    if len(prompt_ids) != source["prompt_token_count"] or token_hash(prompt_ids) != source["prompt_sha256"]:
        raise ValueError("Qwen generation prompt differs from the recorded rendered history")
    definition = _decode_probability_definition(input)
    output = await generate_single_turn(input)
    generated = output.samples
    if not isinstance(generated, Sample):
        raise TypeError("The bounded Qwen qualification expects a single native Sample")
    completion_ids = generated.tokens[len(prompt_ids) :]
    if generated.tokens[: len(prompt_ids)] != prompt_ids or len(completion_ids) != generated.response_length:
        raise ValueError("Qwen generation changed its prompt/completion token boundary")
    generated.metadata["probability_definition"] = definition
    raw = input.state.tokenizer.decode(completion_ids, skip_special_tokens=False)
    text = input.state.tokenizer.decode(completion_ids, skip_special_tokens=True)
    reasoning, body = ReasoningParser(
        model_type="qwen3", force_reasoning=generated.metadata["thinking_enabled"]
    ).parse_non_stream(text)
    body = body or ""
    calls, parse_error = [], None
    if generated.metadata["tools"]:
        try:
            body, parsed = create_tool_call_parser(generated.metadata["tools"], "qwen3_coder").parse_non_stream(body)
            calls = [
                {
                    "id": "call_" + uuid.uuid4().hex[:24],
                    "type": "function",
                    "function": {"name": call.name, "arguments": call.parameters},
                }
                for call in parsed
            ]
        except (ValueError, json.JSONDecodeError) as error:
            parse_error = f"{type(error).__name__}: {error}"
    names = [call["function"]["name"] for call in calls]
    categories = {
        (False, False): "neither",
        (False, True): "control_only",
        (True, False): "thinking_only",
        (True, True): "control_and_thinking",
    }
    generated.metadata["completion"] = {
        "raw_text": raw,
        "reasoning_content": reasoning or "",
        "content": body,
        "tool_calls": calls,
        "has_thinking": bool(reasoning),
        "has_body": bool(body),
        "has_submit": "submit" in names,
        "tool_names": names,
        "category": categories[bool(reasoning), "submit" in names],
        "tool_parse_error": parse_error,
        "token_sha256": token_hash(completion_ids),
    }
    generated.metadata["messages"] = [
        *copy.deepcopy(generated.metadata["history"]),
        {
            "role": "assistant",
            "content": body,
            "reasoning_content": reasoning or "",
            "tool_calls": calls,
            "raw_text": raw,
        },
    ]
    # Native train dumps carry train_metadata, not the full source history.
    # These identities describe the fresh completion; old targets remain metadata.
    generated.train_metadata = {
        **(generated.train_metadata or {}),
        "source_uid": source["uid"],
        "source_group_id": source.get("group_id"),
        "source_category": source["category"],
        "prompt_token_count": len(prompt_ids),
        "prompt_sha256": source["prompt_sha256"],
        "completion_token_count": len(completion_ids),
        "completion_sha256": generated.metadata["completion"]["token_sha256"],
        "sample_index": generated.index,
        "sample_group_index": generated.group_index,
    }
    return output


async def score_teacher(args, sample: Sample, **kwargs):
    # The external native RM endpoint wins when supplied. Older supported
    # recipes still use their explicitly named teacher, never the student fallback.
    endpoint = args.rm_url
    if endpoint is None:
        if not args.sglang_model_routers or "teacher" not in args.sglang_model_routers:
            raise ValueError("Qwen OPD requires --rm-url or a distinct named teacher router")
        endpoint = get_model_url(args, "teacher")
    result = await opd._post_json(
        endpoint,
        opd._score_payload(sample.tokens),
        timeout_secs=args.sglang_router_request_timeout_secs,
    )
    scores = opd._trim_input_field(result["meta_info"], "input_token_logprobs", sample.response_length)
    completion_ids = sample.tokens[len(sample.tokens) - sample.response_length :]
    if [item[1] for item in scores] != completion_ids or not all(
        math.isfinite(item[0]) for item in scores
    ):
        raise ValueError("Teacher scores differ from sampled Qwen completion token IDs")
    sample.metadata["teacher_scoring"] = {
        "endpoint": endpoint,
        "token_ids_match": True,
        "scored_tokens": len(scores),
        "mean_logprob": sum(item[0] for item in scores) / len(scores) if scores else None,
    }
    await rescore_student(args, sample)
    scored = sample.metadata.get("student_rescoring")
    if scored is not None and scored.get("status") == "measured":
        # The shared observer scores /generate input_token_logprobs with zero
        # new tokens. Its temperature=0 controls decoding, not the input-token
        # vocabulary normalizer. Keep its actual endpoint versions untouched.
        scored["probability_definition"] = "full_vocabulary_log_softmax"
        sample.metadata.setdefault("probability_definition", {})["prefill"] = scored["probability_definition"]
    return {"reward": 0.0, "teacher_response": result}
