"""Run CPU-only native SWE input parity, real Qwen rendering and cursor checks.

The population checks use --turn-source; the GLM-5.2 copies (all_assistants) also
need --native-recipe for the real-prefix checks. Fixture checks for both turn
sources run in every invocation.

Example:
    python -m tests.manual.agent_opd.check_swe_inputs --source-root SOURCES \
        --source-manifest SOURCES/COPY_COMPLETE.json --steptron-root STEPTRON \
        --module-sha256 '{"playground.baseline_new.mopd.online_turn_loader": "SHA256", ...}' \
        --turn-source all_assistants --native-recipe RECIPE.py \
        --tokenizer QWEN_TOKENIZER --chat-template TEMPLATE.jinja \
        --rollout-max-context-len 131072 --active-conversations 32 --block-turns 8 \
        --order-draws 2048 --parity-draws 512 --temporary-root TEMP --output-root TASK/evidence
"""

import argparse
import ast
import copy
import hashlib
import json
import logging
import platform
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import transformers
from examples.agentic_opd.glm_turns import normalize_tool_arguments, token_hash
from tests.manual.agent_opd.swe_inputs import (
    BASE_LOADER,
    TURN_DATA,
    TURN_SOURCES,
    NativeSWEDataSource,
    SWEInputConfig,
    SWESourcePopulation,
    file_sha256,
    history_tools,
    load_pinned_modules,
    load_source_population,
    recipe_chat_messages,
    render_qwen_history,
    turn_source_pins,
)
from tests.fast.ray.rollout.conftest import make_rollout_config

from miles.utils.processing_utils import load_tokenizer
from miles.utils.args.custom_function import CustomFunctionConfig
from miles.utils.args.custom_view import compute_custom_function_config
from miles.utils.args.runtime import RolloutConfig
from miles.utils.function_registry import load_function
from miles.rollout.generate_utils.generate_endpoint_utils import apply_sample_max_response_len


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _native_converter(recipe_path: Path):
    """Execute only the actual native conversion function, without GPU imports."""
    tree = ast.parse(recipe_path.read_text())
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                    and node.name == "convert_to_chatml_with_tool")
    namespace = {"copy": copy}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(recipe_path), "exec"), namespace)
    return namespace[function.name]


class _CapturingTokenizer:
    """Records what native tokenize_swe_prefix passes to the chat template."""

    def apply_chat_template(self, messages, **kwargs):
        return messages, kwargs.get("tools")


def _native_reference(modules, turn_source: str, recipe: Path | None):
    """(history, tools) as the native code prepares a drawn item's prefix for its template."""
    if turn_source == "loss_masked":
        return lambda conversation: modules[TURN_DATA].tokenize_swe_prefix(_CapturingTokenizer(), conversation[:-1])
    converter = _native_converter(recipe)

    def reference(conversation):
        history = converter(conversation)[:-1]
        # The GLM Step caller passes no tools; this is the adapter's rule before tool_schemas.
        return history, (history[0].get("tools") or None) if history else None
    return reference


def _source(modules, turn_source: str, population: SWESourcePopulation):
    """The native turn source the adapter wraps, built independently as the parity oracle."""
    common = {"domain": "reasoning", "source_group": "swe", "source_load_path": None, "source_load_safetensors": None}
    if turn_source == "loss_masked":
        return modules[TURN_DATA].MaskAwareSWETurnSource(
            population.filelist, **common,
            excluded_source_item_indices=[entry["visual_source_item_indices"] for entry in population.files],
        )
    return modules[BASE_LOADER].OnlineTrajectoryTurnSource(population.filelist, **common)


def _training_turn_counter(modules, turn_source: str, population: SWESourcePopulation):
    """A source conversation's training-turn count from its raw record; 0 when the turn source skips it."""
    if turn_source == "loss_masked":
        excluded = [set(entry["visual_source_item_indices"]) for entry in population.files]
        eligible = modules[TURN_DATA].eligible_assistant_positions
        return lambda record: 0 if record.source_item_index in excluded[record.file_idx] else len(eligible(record.value))
    role = modules[BASE_LOADER].message_role
    return lambda record: sum(role(message) == "assistant" for message in record.value)


def _args(args, **swe_fields) -> SimpleNamespace:
    """Launch fields plus SWEInputConfig defaults, overridden by swe_fields."""
    defaults = {name: field.default for name, field in SWEInputConfig.model_fields.items() if not field.is_required()}
    return SimpleNamespace(
        swe_source_root=str(args.source_root), swe_source_manifest=str(args.source_manifest),
        swe_steptron_root=str(args.steptron_root), swe_module_sha256=args.module_sha256,
        **{**defaults, "swe_turn_source": args.turn_source, **swe_fields},
        hf_checkpoint=str(args.tokenizer), chat_template_path=str(args.chat_template),
        apply_chat_template_kwargs={"preserve_thinking": True, "enable_thinking": True},
        rollout_max_context_len=args.rollout_max_context_len,
        rollout_max_response_len=args.rollout_max_context_len, n_samples_per_prompt=1,
    )


def _actual_prefix_checks(args, modules, population, tokenizer, converter) -> tuple[list[dict], list[list[dict]]]:
    native = modules[BASE_LOADER]
    cursor = native.SequentialJsonArrayCursor(population.filelist)
    conversations = [cursor.next_record().value, cursor.next_record().value]
    cursor.close()
    positions = [i for i, message in enumerate(conversations[0]) if native.message_role(message) == "assistant"]
    ordinals = {int(value) for value in args.turn_ordinals.split(",") if value != "last"}
    if "last" in args.turn_ordinals.split(","):
        ordinals.add(len(positions))
    oracle = _source(modules, "all_assistants", population)
    adapter = NativeSWEDataSource(_args(args), tokenizer=tokenizer, population=population)
    checks = []
    try:
        for ordinal in range(1, max(ordinals) + 1):
            before = oracle.state_dict()
            expected = next(oracle)
            if ordinal not in ordinals:
                continue
            actual_history = conversations[0][:positions[ordinal - 1]]
            assert expected["conversation"][:-1] == actual_history
            converted = converter(expected["conversation"])
            assert recipe_chat_messages(expected["conversation"][:-1]) == converted[:-1]
            # Position only this test cursor using native state; the public training
            # DataSource.load intentionally remains unsupported.
            adapter.sources[0].load_state_dict(before)
            ground_truth = expected["conversation"][-1]["ground_truth"]
            tools = converted[0].get("tools")
            prompt = tokenizer.apply_chat_template(
                normalize_tool_arguments(converted[:-1]), tools=tools,
                tokenize=False, add_generation_prompt=True,
                preserve_thinking=True, enable_thinking=True,
            )
            prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
            expected_uid = f"{population.files[0]['sha256']}:0:{positions[ordinal - 1]}"
            valid = len(prompt_ids) < args.rollout_max_context_len
            if valid:
                sample = adapter.get_samples(1)[0][0]
                assert sample.metadata["history"] == converted[:-1]
                assert sample.metadata["native_ground_truth"] == ground_truth
                assert sample.metadata["source"]["uid"] == expected_uid
                assert sample.prompt == prompt
                assert sample.metadata["source"]["prompt_sha256"] == token_hash(prompt_ids)
                assert sample.max_response_len == args.rollout_max_context_len - len(prompt_ids)
            next_after_reject = None
            if not valid and ordinal == len(positions):
                slot_before = adapter.sample_index
                rejected_before = adapter.skipped_overlength
                next_item = next(oracle)
                sample = adapter.get_samples(1)[0][0]
                assert sample.metadata["history"] == converter(next_item["conversation"])[:-1]
                assert sample.metadata["native_ground_truth"] == next_item["conversation"][-1]["ground_truth"]
                assert sample.index == slot_before
                assert adapter.skipped_overlength == rejected_before + 1
                assert sample.metadata["source"]["source_item_index"] == 1
                next_after_reject = {
                    "source": sample.metadata["source"], "sample_index": sample.index,
                    "rejected_source_row_index": ground_truth["source_row_index"],
                    "overlength_turns_skipped": 1, "generation_slots_consumed_by_rejection": 0,
                    "full_next_conversation_prefix_equal": True,
                }
            assert prompt.endswith("<|im_start|>assistant\n<think>\n")
            reasoning = [m["reasoning_content"].strip() for m in converted[:-1] if m.get("reasoning_content")]
            assert all(text in prompt for text in reasoning)
            historical_calls = [call for m in converted[:-1] for call in m.get("tool_calls", [])]
            assert all(f"<function={call['function']['name']}>" in prompt for call in historical_calls)
            assert not historical_calls or "<tool_response>" in prompt
            assert not tools or "<tools>" in prompt
            checks.append({
                "uid": expected_uid, "assistant_turn_index": positions[ordinal - 1],
                "assistant_turn_ordinal": ordinal, "source_message_count": len(conversations[0]),
                "context_messages": len(actual_history), "raw_history_sha256": _digest(actual_history),
                "normalized_history_sha256": _digest(converted[:-1]),
                "target_message_sha256": _digest(conversations[0][positions[ordinal - 1]]),
                "prompt_token_count": len(prompt_ids), "prompt_sha256": token_hash(prompt_ids),
                "length_eligible": valid,
                "max_new_tokens": args.rollout_max_context_len - len(prompt_ids) if valid else None,
                "history_reasoning_messages": len(reasoning), "history_tool_calls": len(historical_calls),
                "history_tool_responses": sum(m["role"] == "tool" for m in converted[:-1]),
                "tools": len(tools or []), "native_prefix_and_conversion_equal": True,
                "adapter_prompt_and_uid_equal": True if valid else None,
                "next_accepted_after_real_overlength_reject": next_after_reject,
            })
    finally:
        oracle.close()
        adapter.close()
    return checks, conversations


def _fixture_population(root: Path, files: list[list[list[dict]]],
                        visual: list[list[int]] | None = None) -> SWESourcePopulation:
    root.mkdir(parents=True, exist_ok=True)
    entries = []
    for index, conversations in enumerate(files):
        path = root / f"part{index}.json"
        path.write_text(json.dumps(conversations, ensure_ascii=False))
        entries.append({"path": str(path), "local_path": str(path), "bytes": path.stat().st_size,
                        "sha256": file_sha256(path),
                        "visual_source_item_indices": visual[index] if visual else []})
    manifest = {"status": "COMPLETE", "files": entries, "total_bytes": sum(f["bytes"] for f in entries)}
    return SWESourcePopulation(tuple(entries), manifest, _digest(manifest))


def _excerpt(native, conversation: list[dict], turns: int) -> list[dict]:
    positions = [i for i, m in enumerate(conversation) if native.message_role(m) == "assistant"]
    return conversation[:positions[min(turns, len(positions)) - 1] + 1]


def _boundary_checks(args, modules, tokenizer, converter, conversations) -> dict:
    native = modules[BASE_LOADER]
    population = _fixture_population(args.temporary_root / "input-boundaries", [
        [[{"from": "human", "value": "No assistant in this conversation"}],
         _excerpt(native, conversations[0], 2), _excerpt(native, conversations[1], 1)],
        [_excerpt(native, conversations[0], 1)],
    ])
    oracle = _source(modules, "all_assistants", population)
    adapter = NativeSWEDataSource(_args(args), tokenizer=tokenizer, population=population)
    rows = []
    try:
        for index in range(6):
            item = next(oracle)
            sample = adapter.get_samples(1)[0][0]
            expected = converter(item["conversation"])
            assert sample.metadata["history"] == expected[:-1]
            assert sample.metadata["native_ground_truth"] == expected[-1]["ground_truth"]
            assert sample.index == sample.group_index == index
            rows.append({name: sample.metadata["source"][name] for name in (
                "uid", "epoch", "source_item_index", "source_row_index", "assistant_turn_ordinal",
            )})
        assert [r["epoch"] for r in rows] == [0, 0, 0, 0, 1, 1]
        assert rows[0]["uid"] == rows[4]["uid"] and rows[1]["uid"] == rows[5]["uid"]
        assert adapter.sources[0].skipped_no_assistant == oracle.skipped_no_assistant == 2
        adapter.save(args.temporary_root / "input-audit")
        try:
            adapter.load(args.temporary_root / "input-audit")
        except NotImplementedError as error:
            restore_error = str(error)
        else:
            raise AssertionError("Unsupported training restore was accepted")
        role_case = [{"from": "HUMAN", "value": "Question"}, {"from": "ASSISTANT"}]
        assert recipe_chat_messages(role_case) == converter(role_case)
    finally:
        oracle.close()
        adapter.close()
    return {"status": "PASS", "fixture": "small excerpts of the first two actual conversations, two files",
            "rows": rows, "empty_assistant_conversations_skipped": 2,
            "conversation_file_and_epoch_boundaries": True, "restore_rejected": restore_error}


class _CharacterTokenizer:
    """Fault injection for exact length rejection, not a Qwen length estimate."""

    def apply_chat_template(self, messages, **kwargs):
        return json.dumps(messages)

    def encode(self, prompt, **kwargs):
        return list(range(len(prompt)))


def _length_rejection_check(args) -> dict:
    population = _fixture_population(args.temporary_root / "input-length", [[[
        {"role": "user", "content": "short"},
        {"role": "assistant", "content": "x" * 600},
        {"role": "tool", "content": "reply", "tool_call_id": "first"},
        {"role": "assistant", "content": "next"},
        {"role": "assistant", "content": "last"},
    ], [{"role": "user", "content": "next conversation"}, {"role": "assistant", "content": "answer"}]]])
    config = _args(args, swe_turn_source="all_assistants")
    config.rollout_max_context_len = 512
    adapter = NativeSWEDataSource(config, tokenizer=_CharacterTokenizer(), population=population)
    try:
        first, second = [row[0] for row in adapter.get_samples(2)]
        assert adapter.skipped_overlength == 2
        assert first.metadata["source"]["source_row_index"] == 0
        assert second.metadata["source"]["source_row_index"] == 3
        assert second.index == second.group_index == 1
        equality_population = _fixture_population(args.temporary_root / "input-equality", [[
            [{"role": "user", "content": "equal threshold"}, {"role": "assistant", "content": "answer"}],
            [{"role": "user", "content": "x"}, {"role": "assistant", "content": "answer"}],
        ]])
        config.rollout_max_context_len = len(json.dumps([{"role": "user", "content": "equal threshold"}]))
        equality = NativeSWEDataSource(config, tokenizer=_CharacterTokenizer(), population=equality_population)
        try:
            next_valid = equality.get_samples(1)[0][0]
            assert equality.skipped_overlength == 1
            assert next_valid.metadata["source"]["source_row_index"] == 1
            assert next_valid.index == 0
        finally:
            equality.close()
        return {"status": "PASS", "fault_injection_tokenizer": "JSON character count",
                "accepted_source_ordinals": [0, 3], "accepted_slot_indices": [0, 1],
                "overlength_turns_skipped": 2, "generation_slots_consumed_by_rejections": 0,
                "prompt_exactly_at_limit_rejected": True}
    finally:
        adapter.close()


def _four_cursors(args, population, tokenizer) -> dict:
    cursors = [NativeSWEDataSource(_args(args), tokenizer=tokenizer, population=population) for _ in range(4)]
    try:
        starts = [cursor.get_samples(1)[0][0].metadata["source"] for cursor in cursors]
        cursors[0].get_samples(1)
        assert [cursor.sample_index for cursor in cursors] == [2, 1, 1, 1]
        assert len({row["uid"] for row in starts}) == 1
        successors = [cursor.get_samples(1)[0][0].metadata["source"]["uid"] for cursor in cursors[1:]]
        assert len(set(successors)) == 1
        return {"status": "PASS", "independent_instances": 4, "start_uid": starts[0]["uid"],
                "counts_after_only_first_advanced": [2, 1, 1, 1], "other_cursors_next_uid": successors[0]}
    finally:
        for cursor in cursors:
            cursor.close()


def _conversation_key(item: dict) -> tuple[str, int]:
    ground_truth = item["conversation"][-1]["ground_truth"]
    return ground_truth["data_path"], ground_truth["source_item_index"]


def _single_source_parity(args, modules, population, tokenizer, reference) -> dict:
    """With the default single open conversation, draws equal one native source's items,
    and the adapter's prefix normalization and tools equal the native reference."""
    oracle = _source(modules, args.turn_source, population)
    adapter = NativeSWEDataSource(_args(args), tokenizer=tokenizer, population=population)
    normalize_history = TURN_SOURCES[args.turn_source].normalize_history
    try:
        conversations, tools_present = set(), 0
        started = time.perf_counter()
        for expected_index in range(args.parity_draws):
            draw_index, item, remaining_turns = adapter.draw()
            assert draw_index == expected_index and item == next(oracle)
            assert remaining_turns == oracle.active_remaining_turns
            history = normalize_history(item["conversation"][:-1])
            expected_history, expected_tools = reference(item["conversation"])
            assert history == expected_history and history_tools(history) == expected_tools
            tools_present += expected_tools is not None
            conversations.add(_conversation_key(item))
        return {"status": "PASS", "draws": args.parity_draws, "active_conversations": len(adapter.sources),
                "items_equal_single_native_source": True, "remaining_turns_equal_native_source": True,
                "history_and_tools_equal_native_normalization": True, "draws_with_tools": tools_present,
                "conversations": len(conversations),
                "skipped_by_turn_source": {name: getattr(adapter.sources[0], name) for name in (
                    "skipped_no_assistant", "skipped_excluded_trajectories") if hasattr(adapter.sources[0], name)},
                "seconds": time.perf_counter() - started}
    finally:
        oracle.close()
        adapter.close()


def _interleaved_order(args, modules, population, tokenizer) -> dict:
    """Order properties of the raw native draws for the task's open-conversation count and block."""
    training_turns = _training_turn_counter(modules, args.turn_source, population)
    fields = {"swe_active_conversations": args.active_conversations, "swe_block_turns": args.block_turns}
    started = time.perf_counter()
    adapters = [NativeSWEDataSource(_args(args, **fields), tokenizer=tokenizer, population=population)
                for _ in range(2)]
    construction_seconds = (time.perf_counter() - started) / len(adapters)
    # An independent cursor gives each conversation's training-turn count in file order.
    oracle = modules[BASE_LOADER].SequentialJsonArrayCursor(population.filelist)
    totals, drawn, open_conversations, sequences = {}, {}, set(), [[], []]
    window = args.active_conversations * args.block_turns
    open_counts = []
    try:
        started = time.perf_counter()
        for _ in range(args.order_draws):
            _, item, remaining_turns = adapters[0].draw()
            key = _conversation_key(item)
            ordinal = item["conversation"][-1]["ground_truth"]["assistant_turn_ordinal"]
            if ordinal == 1:
                assert key not in drawn
                record = oracle.next_record()
                while not training_turns(record):
                    record = oracle.next_record()
                assert key == (record.path, record.source_item_index), "conversations must open in file order"
                totals[key] = training_turns(record)
                drawn[key] = 0
                open_conversations.add(key)
            assert ordinal == drawn[key] + 1, "a conversation's turns must be drawn in ascending order without gaps"
            drawn[key] = ordinal
            assert remaining_turns == totals[key] - ordinal
            if remaining_turns == 0:
                open_conversations.remove(key)
            assert len(open_conversations) <= args.active_conversations
            if len(sequences[0]) >= window:
                open_counts.append(len(open_conversations))
            sequences[0].append((key, ordinal))
        draw_seconds = time.perf_counter() - started
        for _ in range(args.order_draws):
            _, item, _ = adapters[1].draw()
            sequences[1].append((_conversation_key(item), item["conversation"][-1]["ground_truth"]["assistant_turn_ordinal"]))
        assert sequences[0] == sequences[1], "two independent instances must draw the same sequence"
    finally:
        oracle.close()
        for adapter in adapters:
            adapter.close()
    runs, start = [], 0
    for index in range(1, len(sequences[0]) + 1):
        if index == len(sequences[0]) or sequences[0][index][0] != sequences[0][start][0]:
            runs.append((start, index - start))
            start = index
    windows = [Counter(key for key, _ in sequences[0][begin:begin + window])
               for begin in range(0, len(sequences[0]), window)]
    names = {path: Path(path).name for path, _ in totals}
    return {
        "status": "PASS", "draws": args.order_draws, "active_conversations": args.active_conversations,
        "block_turns": args.block_turns, "instances_with_equal_sequences": len(adapters),
        "ascending_without_gaps": True, "conversations_open_in_file_order": True,
        "remaining_turns_equal_independent_count": True,
        "max_open_conversations": max(open_counts), "min_open_conversations_after_first_window": min(open_counts),
        "conversations": len(totals), "finished_conversations": sum(drawn[k] == totals[k] for k in totals),
        "conversations_per_window": [len(counts) for counts in windows],
        "turns_per_conversation_per_window": [dict(sorted(Counter(counts.values()).items())) for counts in windows],
        "turns_drawn_per_conversation": {"min": min(drawn.values()), "median": statistics.median(drawn.values()),
                                         "max": max(drawn.values())},
        "run_lengths": dict(sorted(Counter(length for _, length in runs).items())),
        "longest_run": max(length for _, length in runs),
        "runs_longer_than_block": [
            {"start_draw": begin, "length": length, "file": names[sequences[0][begin][0][0]],
             "source_item_index": sequences[0][begin][0][1], "first_ordinal": sequences[0][begin][1]}
            for begin, length in runs if length > args.block_turns
        ],
        "construction_seconds_per_instance": construction_seconds,
        "draw_milliseconds_mean": draw_seconds / args.order_draws * 1000,
    }


def _finished_report_check(args) -> dict:
    """remaining_turns and the per-call finished report on a fixture with hand-derived mixer order.

    Two open conversations, blocks of two. Conversation 0 has one turn; conversation 1's
    last turn is over the length limit; conversation 3 is in the second file.
    """
    def conversation(*questions):
        return [m for q in questions for m in ({"role": "user", "content": q}, {"role": "assistant", "content": "answer"})]

    population = _fixture_population(args.temporary_root / "input-finished", [
        [conversation("single"), conversation("first", "second", "x" * 600), conversation("a", "b")],
        [conversation("c", "d")],
    ])
    config = _args(args, swe_turn_source="all_assistants", swe_active_conversations=2, swe_block_turns=2)
    config.rollout_max_context_len = 512
    adapter = NativeSWEDataSource(config, tokenizer=_CharacterTokenizer(), population=population)
    first, second = (entry["sha256"] for entry in population.files)
    c0, c1, c2, c3 = f"{first}:0", f"{first}:1", f"{first}:2", f"{second}:0"
    # (requested samples, [(group_id, ordinal, draw index, remaining turns)], finished)
    calls = [
        (2, [(c0, 1, 0, 0), (c1, 1, 1, 2)], (c0,)),
        (3, [(c1, 2, 2, 1), (c2, 1, 3, 1), (c2, 2, 4, 0)], (c2,)),
        (1, [(c3, 1, 6, 1)], (c1,)),
        (1, [(c3, 2, 7, 0)], (c3,)),
    ]
    try:
        for count, expected, finished in calls:
            samples = [group[0].metadata["source"] for group in adapter.get_samples(count)]
            assert [(s["group_id"], s["assistant_turn_ordinal"], s["draw_index"], s["remaining_turns"])
                    for s in samples] == expected
            assert adapter.finished_conversations == finished
        assert adapter.skipped_overlength == 1 and adapter.sample_index == 7 and adapter.draws == 8
        adapter.save(args.temporary_root / "input-finished-audit")
        receipt = json.loads((args.temporary_root / "input-finished-audit" / "native_swe_inputs.json").read_text())
        assert receipt["emitted_turns"] == 8 and receipt["identity"]["active_conversations"] == 2
    finally:
        adapter.close()
    return {"status": "PASS", "fault_injection_tokenizer": "JSON character count",
            "active_conversations": 2, "block_turns": 2,
            "calls": [{"requested": count, "accepted": [list(row) for row in expected], "finished": list(finished)}
                      for count, expected, finished in calls],
            "single_turn_conversation_finished": True, "last_turn_overlength_reported_finished": True,
            "rejected_draw_index": 5}


def _loss_masked_fixture(args) -> tuple[SWESourcePopulation, list[dict], dict]:
    """File 0: a visual conversation (excluded through the manifest), one without loss_mask=1
    assistants, one whose masked assistant (reasoning and a tool call) precedes two training
    turns and whose first message carries tool_schemas, and one whose last training turn is
    over the length limit. File 1: one single-turn conversation."""
    def message(role, content, mask=0, **fields):
        return {"role": role, "content": content, "loss_mask": mask, **fields}

    schema = {"type": "function", "function": {
        "name": "run_tests", "description": "Run the test suite.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    }}
    masked = [
        message("system", "You fix repositories.", tool_schemas=[schema]),
        message("user", "Fix the failing test."),
        message("assistant", "", reasoning_content="masked reasoning",
                tool_calls=[{"id": "call-0", "type": "function",
                             "function": {"name": "run_tests", "arguments": json.dumps({"path": "tests"})}}]),
        message("tool", "1 failed", tool_call_id="call-0"),
        message("assistant", "first training turn", 1, reasoning_content="trained reasoning"),
        message("user", "Explain the fix."),
        message("assistant", "second training turn", 1),
    ]
    image = [{"type": "image", "image": "data:image/png;base64,AAAA"}, {"type": "text", "text": "Describe it."}]
    population = _fixture_population(args.temporary_root / "input-loss-masked", [[
        [message("user", image), message("assistant", "visual answer", 1)],
        [message("user", "Context only."), message("assistant", "masked answer")],
        masked,
        [message("user", "first"), message("assistant", "answer", 1),
         message("user", "x" * 4000), message("assistant", "answer", 1)],
    ], [[message("user", "single"), message("assistant", "answer", 1)]]], visual=[[0], []])
    return population, masked, schema


def _loss_masked_fixture_check(args, modules, tokenizer) -> dict:
    """loss_masked training turns, exclusions, identity, remaining_turns, finished report and rendering."""
    population, masked, schema = _loss_masked_fixture(args)
    config = _args(args, swe_turn_source="loss_masked")
    config.rollout_max_context_len = config.rollout_max_response_len = 2048
    adapter = NativeSWEDataSource(config, tokenizer=_CharacterTokenizer(), population=population)
    first, second = (entry["sha256"] for entry in population.files)
    c2, c3, d0 = f"{first}:2", f"{first}:3", f"{second}:0"
    # (requested samples, [(group_id, ordinal, draw index, remaining turns, epoch)], finished)
    calls = [
        (2, [(c2, 1, 0, 1, 0), (c2, 2, 1, 0, 0)], (c2,)),
        (2, [(c3, 1, 2, 1, 0), (d0, 1, 4, 0, 0)], (c3, d0)),
        (1, [(c2, 1, 5, 1, 1)], ()),
    ]
    try:
        groups = []
        for count, expected, finished in calls:
            samples = [group[0] for group in adapter.get_samples(count)]
            assert [tuple(s.metadata["source"][name] for name in (
                "group_id", "assistant_turn_ordinal", "draw_index", "remaining_turns", "epoch",
            )) for s in samples] == expected
            assert adapter.finished_conversations == finished
            groups.append(samples)
        turn_1, turn_2 = groups[0]
        assert [s.metadata["source"]["uid"] for s in (turn_1, turn_2)] == [f"{c2}:4", f"{c2}:6"]
        identity = {name: [s.metadata["source"][name] for s in (turn_1, turn_2)] for name in (
            "source_assistant_turn_ordinal", "context_masked_assistant_count", "num_context_messages")}
        assert identity == {"source_assistant_turn_ordinal": [2, 3], "context_masked_assistant_count": [1, 1],
                            "num_context_messages": [4, 6]}
        assert {s.metadata["source"]["target_policy"] for s in (turn_1, turn_2)} == {modules[TURN_DATA].TARGET_POLICY}
        history = turn_1.metadata["history"]
        assert history[2]["role"] == "assistant" and history[2]["loss_mask"] == 0, "the masked assistant stays in the prefix"
        native_history, native_tools = modules[TURN_DATA].tokenize_swe_prefix(_CapturingTokenizer(), masked[:4])
        assert history == native_history and turn_1.metadata["tools"] == native_tools == [schema]
        source = adapter.sources[0]
        assert source.skipped_excluded_trajectories == 2 and source.skipped_no_assistant == 2
        assert adapter.skipped_overlength == 1 and adapter.sample_index == 5 and adapter.draws == 6
        assert adapter.identity["turn_source"] == "loss_masked"
        assert adapter.identity["visual_exclusion_sha256"] == source.exclusion_sha256
        assert list(adapter.identity["pinned_module_sha256"]) == [BASE_LOADER, TURN_DATA]
    finally:
        adapter.close()

    qwen = NativeSWEDataSource(_args(args, swe_turn_source="loss_masked"), tokenizer=tokenizer, population=population)
    try:
        turn_1, turn_2 = [group[0] for group in qwen.get_samples(2)]
        for sample in (turn_1, turn_2):
            assert sample.prompt.endswith("<|im_start|>assistant\n<think>\n")
            assert all(text in sample.prompt for text in ("masked reasoning", "<function=run_tests>", "<tool_response>", "<tools>"))
        assert "trained reasoning" in turn_2.prompt and "first training turn" in turn_2.prompt
        renamed = copy.deepcopy(turn_1.metadata["history"])
        renamed[0]["tools"] = renamed[0].pop("tool_schemas")
        assert render_qwen_history(tokenizer, renamed, history_tools(renamed), qwen.template_kwargs)[0] == turn_1.prompt
        prompt_tokens = [s.metadata["source"]["prompt_token_count"] for s in (turn_1, turn_2)]
    finally:
        qwen.close()
    return {"status": "PASS", "fixture_tokenizer": "JSON character count, limit 2048; Qwen for rendering",
            "calls": [{"requested": count, "accepted": [list(row) for row in expected], "finished": list(finished)}
                      for count, expected, finished in calls],
            "masked_assistant_kept_in_prefix_not_a_turn": True, "training_turn_ordinals_contiguous": True,
            "identity_fields": identity, "history_equal_native_tokenize_swe_prefix": True,
            "visual_and_no_training_turn_conversations_skipped_per_epoch": 1,
            "last_training_turn_overlength_reported_finished": True, "rejected_draw_index": 3,
            "masked_reasoning_rendered_with_preserve_thinking": True,
            "tool_schemas_renders_equal_to_tools": True, "qwen_prompt_tokens": prompt_tokens}


def _configuration_check(args) -> dict:
    config = vars(_args(args, swe_active_conversations=args.active_conversations, swe_block_turns=args.block_turns))
    custom = {name: value for name, value in config.items() if name.startswith("swe_")}
    launch = {name: value for name, value in config.items() if not name.startswith("swe_")}
    hook = CustomFunctionConfig.model_validate({
        "path": "tests.manual.agent_opd.swe_inputs.NativeSWEDataSource", "config": custom,
    })
    rollout = make_rollout_config(**launch, data_source_path=hook)
    assert isinstance(rollout, RolloutConfig)
    assert "max_seq_len" not in RolloutConfig.model_fields
    merged = compute_custom_function_config(rollout, rollout.data_source_path)
    assert "max_seq_len" not in dict(merged)
    adapter = load_function(rollout.data_source_path)(merged)
    try:
        assert len(adapter.sources) == adapter.identity["active_conversations"] == args.active_conversations
        assert adapter.mixer.trajectory_block_turns == adapter.identity["block_turns"] == args.block_turns
        sample = adapter.get_samples(1)[0][0]
        assert sample.max_response_len == args.rollout_max_context_len - sample.metadata["source"]["prompt_token_count"]
        sampling = apply_sample_max_response_len({"max_new_tokens": args.rollout_max_context_len}, sample)
        assert sampling["max_new_tokens"] == sample.max_response_len
        return {"status": "PASS", "path": hook.path, "config": hook.config.model_dump(),
                "uses_actual_custom_function_config_merge": True,
                "runtime_config_type": type(rollout).__name__,
                "runtime_config_builder": "existing make_rollout_config with real parser defaults and model_validate",
                "nonexistent_max_seq_len_launch_field_absent": True,
                "native_request_max_new_tokens": sampling["max_new_tokens"]}
    finally:
        adapter.close()


def _model_receipt_reference(path: Path | None, input_identity: dict) -> dict | None:
    if path is None:
        return None
    receipt = json.loads(path.read_text())
    assert receipt["status"] == "verified" and not receipt["errors"]
    for model in receipt["models"].values():
        hashes = model["metadata_sha256"]
        assert hashes["tokenizer.json"] == input_identity["tokenizer_json_sha256"]
        assert hashes["tokenizer_config.json"] == input_identity["tokenizer_config_json_sha256"]
    return {"path": str(path.resolve()), "sha256": file_sha256(path),
            "status": receipt["status"], "local_tokenizer_assets_match_all_models": True,
            "verification_owner": "parent; receipt read only, no duplicate model scan"}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ("source-root", "source-manifest", "steptron-root", "tokenizer",
                 "chat-template", "temporary-root", "output-root"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--module-sha256", type=json.loads, required=True,
                        help="JSON object: dotted Steptron module name -> SHA256, for every turn source")
    parser.add_argument("--turn-source", choices=sorted(TURN_SOURCES), required=True)
    parser.add_argument("--native-recipe", type=Path, help="GLM-5.2 0710 recipe; required for all_assistants")
    parser.add_argument("--rollout-max-context-len", type=int, required=True)
    parser.add_argument("--active-conversations", type=int, required=True)
    parser.add_argument("--block-turns", type=int, required=True)
    parser.add_argument("--order-draws", type=int, required=True)
    parser.add_argument("--parity-draws", type=int, required=True)
    parser.add_argument("--turn-ordinals", default="1,2,8,32,64,100,last")
    parser.add_argument("--model-source-receipt", type=Path)
    args = parser.parse_args()
    glm = args.turn_source == "all_assistants"
    if glm and args.native_recipe is None:
        parser.error("--native-recipe is required for --turn-source all_assistants")
    logging.basicConfig(level=logging.INFO)
    # Fixture checks cover every turn source, so all their modules load.
    pins = {name: sha256 for turn_source in TURN_SOURCES
            for name, sha256 in turn_source_pins(turn_source, args.module_sha256).items()}
    modules = load_pinned_modules(args.steptron_root, pins)
    population = load_source_population(args.source_root, args.source_manifest)
    tokenizer = load_tokenizer(str(args.tokenizer), chat_template_path=str(args.chat_template), local_files_only=True)
    reference = _native_reference(modules, args.turn_source, args.native_recipe)
    rows = []
    report = {
        "task_id": "T01-inputs", "status": "PASS", "python": platform.python_version(),
        "transformers": transformers.__version__, "argv": sys.argv, "turn_source": args.turn_source,
        "pinned_module_sha256": pins,
    }
    if glm:
        converter = _native_converter(args.native_recipe)
        rows, conversations = _actual_prefix_checks(args, modules, population, tokenizer, converter)
        report.update(native_recipe_sha256=file_sha256(args.native_recipe), actual_prefix_checks=rows,
                      boundary_checks=_boundary_checks(args, modules, tokenizer, converter, conversations))
    report.update({
        "length_rejection": _length_rejection_check(args),
        "finished_report": _finished_report_check(args),
        "loss_masked_fixture": _loss_masked_fixture_check(args, modules, tokenizer),
        "four_cursors": _four_cursors(args, population, tokenizer),
        "single_source_parity": _single_source_parity(args, modules, population, tokenizer, reference),
        "interleaved_order": _interleaved_order(args, modules, population, tokenizer),
        "configuration": _configuration_check(args),
        "limits": ["No Step/Qwen token or prompt byte equality is asserted",
                   "Tokenizer compatibility with teacher models and benchmark overlap are separately owned",
                   *(["Only selected actual prefixes were Qwen encoded, not all raw assistant turns",
                      "Conversation/file/EOF regression fixtures use actual conversation excerpts, not a full epoch scan",
                      "Qwen explicitly renders system.tools; the GLM Step caller omits them"] if glm else
                     ["Real prompts are Qwen encoded only in the configuration check and by the source audit; "
                      "message normalization and tools are compared with native for every parity draw",
                      "Loss-mask, exclusion and finished-report rules are checked on a synthetic fixture"]),
                   ],
    })
    args.output_root.mkdir(parents=True, exist_ok=True)
    adapter = NativeSWEDataSource(
        _args(args, swe_active_conversations=args.active_conversations, swe_block_turns=args.block_turns),
        tokenizer=tokenizer, population=population,
    )
    try:
        model_reference = _model_receipt_reference(args.model_source_receipt, adapter.identity)
        report["parent_model_source_receipt"] = model_reference
        (args.output_root / "input-config.json").write_text(json.dumps(adapter.identity, indent=2) + "\n")
    finally:
        adapter.close()
    (args.output_root / "input-source-manifest.json").write_text(json.dumps({
        "manifest": population.manifest, "manifest_sha256": population.manifest_sha256,
        "local_verified_files": list(population.files), "local_verified_bytes": population.manifest["total_bytes"],
        "manifest_reported_conversations": sum(f["conversations"] for f in population.files),
        "manifest_reported_raw_assistant_turns": sum(f["assistant_turns"] for f in population.files),
        "counts_independently_recomputed_in_this_check": False,
        "parent_model_source_receipt": model_reference,
    }, indent=2) + "\n")
    (args.output_root / "input-parity.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "prefix_checks": len(rows),
                      "lengths": [row["prompt_token_count"] for row in rows],
                      "evidence": str(args.output_root / "input-parity.json")}))


if __name__ == "__main__":
    main()
