"""Render complete GLM assistant turns without forcing a thinking mode.

The role-only generation boundary follows the pinned ticket07 GLM renderer.
Original source messages remain unchanged; only the template input normalizes
JSON-string tool arguments to the object form required by GLM's template.
"""

import copy
import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class GLMTurn:
    prompt: str
    prompt_ids: list[int]
    completion_ids: list[int]
    completion_text: str


def token_hash(tokens: list[int]) -> str:
    return hashlib.sha256(json.dumps(tokens, separators=(",", ":")).encode()).hexdigest()


def normalize_tool_arguments(messages: list[dict]) -> list[dict]:
    normalized = copy.deepcopy(messages)
    for message in normalized:
        for call in message.get("tool_calls") or []:
            function = call.get("function", call)
            arguments = function["arguments"]
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            if not isinstance(arguments, dict):
                raise ValueError("GLM tool arguments must be a JSON object")
            function["arguments"] = arguments
    return normalized


def render_glm_history(tokenizer, messages: list[dict], tools: list[dict] | None) -> str:
    text = tokenizer.apply_chat_template(
        normalize_tool_arguments(messages),
        tools=tools,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True,
        clear_thinking=False,
    )
    if not text.endswith("<|assistant|><think>"):
        raise ValueError("Expected the pinned GLM assistant generation suffix")
    return text.removesuffix("<think>")


def encode_glm_turn(tokenizer, messages: list[dict], tools: list[dict] | None) -> GLMTurn:
    if not messages or messages[-1]["role"] != "assistant":
        raise ValueError("A fixed GLM turn must end in the selected assistant message")
    prompt = render_glm_history(tokenizer, messages[:-1], tools)
    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
    full_text = tokenizer.apply_chat_template(
        normalize_tool_arguments(messages),
        tools=tools,
        tokenize=False,
        add_generation_prompt=False,
        clear_thinking=False,
    )
    full_ids = tokenizer.encode(full_text, add_special_tokens=False)
    if full_ids[: len(prompt_ids)] != prompt_ids:
        raise ValueError("The fixed completion changed the GLM prompt token prefix")
    completion_ids = full_ids[len(prompt_ids) :]
    if not completion_ids:
        raise ValueError("The selected assistant completion is empty")
    return GLMTurn(
        prompt=prompt,
        prompt_ids=prompt_ids,
        completion_ids=completion_ids,
        completion_text=tokenizer.decode(completion_ids, skip_special_tokens=False),
    )
