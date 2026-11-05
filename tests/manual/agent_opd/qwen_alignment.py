"""Preserve Qwen3.5 completions and observe actual FrogNano OPD scoring."""

import copy
import json
import math
import uuid

from examples.agentic_opd.glm_turns import token_hash
from sglang.srt.parser.reasoning_parser import ReasoningParser
from tests.manual.agent_opd.alignment import rescore_student

from miles.rollout import on_policy_distillation as opd
from miles.rollout.base_types import GenerateFnInput, GenerateFnOutput
from miles.rollout.generate_hub.single_turn import generate as generate_single_turn
from miles.rollout.generate_utils.tool_call_utils import create_tool_call_parser
from miles.rollout.sglang_rollout import get_model_url
from miles.utils.types import Sample


async def generate(input: GenerateFnInput) -> GenerateFnOutput:
    sample = input.sample
    source = sample.metadata["source"]
    prompt_ids = input.state.tokenizer.encode(sample.prompt, add_special_tokens=False)
    if len(prompt_ids) != source["prompt_token_count"] or token_hash(prompt_ids) != source["prompt_sha256"]:
        raise ValueError("Qwen generation prompt differs from the recorded rendered history")
    output = await generate_single_turn(input)
    generated = output.samples
    if not isinstance(generated, Sample):
        raise TypeError("The bounded Qwen qualification expects a single native Sample")
    completion_ids = generated.tokens[len(prompt_ids) :]
    if generated.tokens[: len(prompt_ids)] != prompt_ids or len(completion_ids) != generated.response_length:
        raise ValueError("Qwen generation changed its prompt/completion token boundary")
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
    return output


async def score_teacher(args, sample: Sample, **kwargs):
    result = await opd._post_json(
        get_model_url(args, "teacher"),
        opd._score_payload(sample.tokens),
        timeout_secs=args.sglang_router_request_timeout_secs,
    )
    scores = result["meta_info"]["input_token_logprobs"][-sample.response_length :]
    if [item[1] for item in scores] != sample.tokens[-sample.response_length :] or not all(
        math.isfinite(item[0]) for item in scores
    ):
        raise ValueError("FrogNano scores differ from sampled Qwen completion token IDs")
    sample.metadata["teacher_scoring"] = {
        "model": "FrogNano-4B-2609",
        "token_ids_match": True,
        "scored_tokens": len(scores),
        "mean_logprob": sum(item[0] for item in scores) / len(scores),
    }
    await rescore_student(args, sample)
    return {"reward": 0.0, "teacher_response": result}
