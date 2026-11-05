"""Generate and record one complete GLM turn for on-policy distillation.

Student tokens, routing replay arrays, sampling logprobs and weight versions
remain on Miles' native Sample path. Parsed fields are observations; they never
replace, retokenize or filter the completion used by training.
"""

import copy
import json
import math
import uuid

from examples.agentic_opd.glm_turns import token_hash
from sglang.srt.parser.reasoning_parser import ReasoningParser

from miles.rollout import on_policy_distillation as opd
from miles.rollout.base_types import GenerateFnInput, GenerateFnOutput
from miles.rollout.generate_hub.single_turn import generate as generate_single_turn
from miles.rollout.generate_utils.tool_call_utils import create_tool_call_parser
from miles.rollout.sglang_rollout import get_model_url
from miles.utils.types import Sample


def describe_completion(tokenizer, token_ids: list[int], tools: list[dict] | None) -> dict:
    raw_text = tokenizer.decode(token_ids, skip_special_tokens=False)
    parser_text = tokenizer.decode(token_ids, skip_special_tokens=True)
    # GLM emits </think> even when the reasoning span is empty.
    reasoning, body = ReasoningParser(model_type="glm45", force_reasoning="</think>" in parser_text).parse_non_stream(
        parser_text
    )
    body = body or ""
    calls = []
    tool_parse_error = None
    if tools:
        parser = create_tool_call_parser(tools, "glm47")
        try:
            body, parsed = parser.parse_non_stream(body)
            calls = [
                {
                    "id": f"call_{uuid.uuid4().hex[:24]}",
                    "type": "function",
                    "function": {"name": call.name, "arguments": call.parameters},
                }
                for call in parsed
            ]
        except (ValueError, json.JSONDecodeError) as error:
            # A token-limited generation can stop inside an argument envelope.
            # Keep the original text and tokens; parsing is only an observation.
            tool_parse_error = f"{type(error).__name__}: {error}"
    names = [call["function"]["name"] for call in calls]
    categories = {
        (False, False): "neither",
        (False, True): "control_only",
        (True, False): "thinking_only",
        (True, True): "control_and_thinking",
    }
    return {
        "raw_text": raw_text,
        "reasoning_content": reasoning or "",
        "content": body,
        "tool_calls": calls,
        "has_thinking": bool(reasoning),
        "has_body": bool(body),
        "has_submit": "submit" in names,
        "category": categories[bool(reasoning), "submit" in names],
        "tool_names": names,
        "tool_parse_error": tool_parse_error,
        "token_sha256": token_hash(token_ids),
    }


async def generate(input: GenerateFnInput) -> GenerateFnOutput:
    sample = input.sample
    source = sample.metadata["source"]
    prompt_ids = input.state.tokenizer.encode(sample.prompt, add_special_tokens=False)
    if len(prompt_ids) != source["prompt_token_count"] or token_hash(prompt_ids) != source["prompt_sha256"]:
        raise ValueError("Generation prompt differs from the pinned glm5.2 source turn")
    if not sample.prompt.endswith("<|assistant|>"):
        raise ValueError("The GLM OPD generation prompt must use the role-only boundary")
    output = await generate_single_turn(input)
    generated = output.samples
    if not isinstance(generated, Sample):
        raise TypeError("The GLM turn recipe expects one native Sample")
    completion_ids = generated.tokens[len(prompt_ids) :]
    if generated.tokens[: len(prompt_ids)] != prompt_ids or len(completion_ids) != generated.response_length:
        raise ValueError("The actual GLM generation changed its prompt/completion boundary")
    completion = describe_completion(input.state.tokenizer, completion_ids, generated.metadata["tools"])
    completion["status"] = generated.status.value
    completion["generation_boundary"] = "role_only"
    generated.metadata["completion"] = completion
    generated.metadata["messages"] = [
        *copy.deepcopy(generated.metadata["history"]),
        {
            "role": "assistant",
            "content": completion["content"],
            "reasoning_content": completion["reasoning_content"],
            "tool_calls": completion["tool_calls"],
            "raw_text": completion["raw_text"],
        },
    ]
    return output


async def score_teacher(args, sample: Sample, **kwargs):
    if "teacher" not in args.sglang_model_routers:
        raise ValueError("The GLM OPD recipe requires a distinct named teacher router")
    reward = await opd._post_json(
        get_model_url(args, "teacher"),
        opd._score_payload(sample.tokens),
        timeout_secs=args.sglang_router_request_timeout_secs,
    )
    scores = reward["meta_info"]["input_token_logprobs"][-sample.response_length :]
    completion_ids = sample.tokens[-sample.response_length :]
    if [item[1] for item in scores] != completion_ids or not all(math.isfinite(item[0]) for item in scores):
        raise ValueError("Teacher scores do not match the sampled completion token IDs")
    sample.metadata["teacher_scoring"] = {
        "model": "GLM-4.7-Flash-Coder",
        "token_ids_match": True,
        "scored_tokens": len(scores),
        "mean_logprob": sum(item[0] for item in scores) / len(scores),
    }
    return {"reward": 0.0, "teacher_response": reward}


def post_process_rewards(args, samples: list[Sample], **kwargs):
    """Extract native teacher signals while rollout metrics read scalar rewards."""
    teacher_args = copy.copy(args)
    teacher_args.reward_key = "teacher_response"
    return opd.post_process_rewards(teacher_args, samples, **kwargs)
