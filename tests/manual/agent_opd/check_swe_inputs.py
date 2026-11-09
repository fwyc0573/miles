"""Run CPU-only native SWE input parity, real Qwen rendering and cursor checks.

Example:
    python -m tests.manual.agent_opd.check_swe_inputs --source-root SOURCES \
        --source-manifest SOURCES/COPY_COMPLETE.json --native-loader LOADER.py \
        --native-loader-sha256 SHA256 --native-recipe RECIPE.py \
        --tokenizer QWEN_TOKENIZER --chat-template TEMPLATE.jinja \
        --rollout-max-context-len 131072 --rollout-max-prompt-len 114688 \
        --rollout-max-response-len 16384 --temporary-root TEMP --output-root TASK/evidence
"""

import argparse
import ast
import collections
import copy
import hashlib
import json
import logging
import platform
import sys
from pathlib import Path
from types import SimpleNamespace

import transformers
from examples.agentic_opd.glm_turns import normalize_tool_arguments, token_hash
from tests.manual.agent_opd.swe_inputs import (
    NativeSWEDataSource,
    SWESourcePopulation,
    file_sha256,
    load_swe_native_module,
    load_source_population,
    native_chat_messages,
    render_qwen_history,
)
from tests.fast.ray.rollout.conftest import make_rollout_config

from miles.utils.processing_utils import load_tokenizer
from miles.utils.args.custom_function import CustomFunctionConfig
from miles.utils.args.custom_view import compute_custom_function_config
from miles.utils.args.runtime import RolloutConfig
from miles.utils.function_registry import load_function
from miles.rollout.generate_utils.generate_endpoint_utils import (
    apply_sample_max_response_len,
    compute_request_payload,
)


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


def _source(native, filelist, masked=False, exclusions=None):
    source = native.MaskAwareSWETurnSource if masked else native.OnlineTrajectoryTurnSource
    kwargs = {"excluded_source_item_indices": exclusions} if masked else {}
    return source(
        filelist, domain="reasoning", source_group="swe",
        source_load_path=None, source_load_safetensors=None, **kwargs,
    )


def _args(args) -> SimpleNamespace:
    # Omitted response limits preserve this historical checker's remaining-context requests.
    return SimpleNamespace(
        swe_source_root=str(args.source_root), swe_source_manifest=str(args.source_manifest),
        swe_native_loader_path=str(args.native_loader), swe_native_loader_sha256=args.native_loader_sha256,
        swe_skip_masked_assistant_turns=args.skip_masked_assistant_turns,
        swe_visual_filter_receipt=str(args.visual_filter_receipt) if args.visual_filter_receipt else None,
        hf_checkpoint=str(args.tokenizer), chat_template_path=str(args.chat_template),
        apply_chat_template_kwargs={"preserve_thinking": True, "enable_thinking": True},
        rollout_max_context_len=args.rollout_max_context_len,
        rollout_max_prompt_len=args.rollout_max_prompt_len,
        rollout_max_response_len=(
            args.rollout_max_context_len if args.rollout_max_response_len is None else args.rollout_max_response_len
        ), n_samples_per_prompt=1,
    )


def _prompt_budget(config, prompt_token_count: int) -> int | None:
    if prompt_token_count >= config.rollout_max_context_len or (
        config.rollout_max_prompt_len is not None and prompt_token_count > config.rollout_max_prompt_len
    ):
        return None
    return min(config.rollout_max_response_len, config.rollout_max_context_len - prompt_token_count)


def _next_eligible(oracle, tokenizer, config, converter):
    rejected = 0
    while True:
        item = next(oracle)
        converted = converter(item["conversation"])
        tools = converted[0].get("tools")
        _, prompt_ids = render_qwen_history(tokenizer, converted[:-1], tools, config.apply_chat_template_kwargs)
        if _prompt_budget(config, len(prompt_ids)) is not None:
            return item, converted, rejected
        rejected += 1


def _cursor(native, filelist):
    base = sys.modules[native.OnlineTrajectoryTurnSource.__module__]
    return base.SequentialJsonArrayCursor(filelist)


def _positions(native, conversation, masked):
    if masked:
        return native.eligible_assistant_positions(conversation)
    return [i for i, message in enumerate(conversation) if native.message_role(message) == "assistant"]


def _adapter(args, native, population, tokenizer):
    # When the parent full-source visual receipt is pending, only deliberately
    # inspected non-visual records may be exercised by this CPU probe.
    subset = len(population.files) != len(population.manifest["files"])
    injected = args.skip_masked_assistant_turns and (args.visual_filter_receipt is None or subset)
    source = _source(native, population.filelist, True, _exclusions(args, native, population)) if injected else None
    return NativeSWEDataSource(_args(args), tokenizer=tokenizer, population=population, native_source=source)


def _exclusions(args, native, population):
    if not args.skip_masked_assistant_turns or args.visual_filter_receipt is None:
        return None
    manifest = json.loads(args.source_manifest.read_text())
    paths = [str((args.source_root / Path(entry["path"]).name).resolve()) for entry in manifest["files"]]
    rows = native.load_visual_filter_exclusions(args.visual_filter_receipt, paths)
    return tuple(rows[paths.index(path)] for path in population.filelist)


def _visual_scan(native, conversation):
    from playground.users.cj.opd import s4_swe_visual_audit_1001 as audit
    counts = collections.Counter()
    signals = {name: collections.Counter() for name in (
        "top_level_field_presence", "top_level_field_payload", "content_markers",
        "reasoning_content_markers", "nested_field_presence", "nested_field_payload", "visual_part_types",
    )}
    found = [audit._scan_message(message, counts, signals) for message in conversation]
    return any(found)


def _actual_prefix_checks(args, native, population, tokenizer, converter) -> tuple[list[dict], list[list[dict]]]:
    config = _args(args)
    cursor = _cursor(native, population.filelist)
    conversations = [cursor.next_record().value, cursor.next_record().value]
    cursor.close()
    if args.skip_masked_assistant_turns:
        assert not any(_visual_scan(native, conversation) for conversation in conversations)
    positions = _positions(native, conversations[0], args.skip_masked_assistant_turns)
    ordinals = {int(value) for value in args.turn_ordinals.split(",") if value != "last"}
    if "last" in args.turn_ordinals.split(","):
        ordinals.add(len(positions))
    assert ordinals and min(ordinals) >= 1 and max(ordinals) <= len(positions), "Probe ordinals exceed native eligible turns"
    oracle = _source(native, population.filelist, args.skip_masked_assistant_turns, _exclusions(args, native, population))
    adapter = _adapter(args, native, population, tokenizer)
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
            assert native_chat_messages(expected["conversation"]) == converted
            # Position only this test cursor using native state; the public training
            # DataSource.load intentionally remains unsupported.
            adapter.native.load_state_dict(before)
            ground_truth = expected["conversation"][-1]["ground_truth"]
            tools = converted[0].get("tools")
            prompt = tokenizer.apply_chat_template(
                normalize_tool_arguments(converted[:-1]), tools=tools,
                tokenize=False, add_generation_prompt=True,
                preserve_thinking=True, enable_thinking=True,
            )
            prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
            expected_uid = f"{population.files[0]['sha256']}:0:{positions[ordinal - 1]}"
            budget = _prompt_budget(config, len(prompt_ids))
            valid = budget is not None
            if valid:
                sample = adapter.get_samples(1)[0][0]
                assert sample.metadata["history"] == converted[:-1]
                assert sample.metadata["native_ground_truth"] == ground_truth
                assert sample.metadata["source"]["uid"] == expected_uid
                assert sample.prompt == prompt
                assert sample.metadata["source"]["prompt_sha256"] == token_hash(prompt_ids)
                assert sample.max_seq_len == config.rollout_max_context_len
                assert sample.max_response_len == budget
            next_after_reject = None
            if not valid and ordinal == len(positions):
                slot_before = adapter.sample_index
                rejected_before = adapter.skipped_overlength
                next_item, next_converted, additional_rejections = _next_eligible(oracle, tokenizer, config, converter)
                sample = adapter.get_samples(1)[0][0]
                assert sample.metadata["history"] == next_converted[:-1]
                assert sample.metadata["native_ground_truth"] == next_item["conversation"][-1]["ground_truth"]
                assert sample.index == sample.group_index == slot_before
                assert sample.max_response_len == _prompt_budget(config, sample.metadata["source"]["prompt_token_count"])
                assert adapter.skipped_overlength == rejected_before + 1 + additional_rejections
                next_after_reject = {
                    "source": sample.metadata["source"], "sample_index": sample.index,
                    "rejected_source_row_index": ground_truth["source_row_index"],
                    "overlength_turns_skipped": 1 + additional_rejections, "generation_slots_consumed_by_rejection": 0,
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
                "max_new_tokens": budget,
                "history_reasoning_messages": len(reasoning), "history_tool_calls": len(historical_calls),
                "context_masked_assistant_count": ground_truth.get("context_masked_assistant_count"),
                "source_assistant_turn_ordinal": ground_truth.get("source_assistant_turn_ordinal"),
                "target_loss_mask": ground_truth.get("target_loss_mask"),
                "history_tool_responses": sum(m["role"] == "tool" for m in converted[:-1]),
                "tools": len(tools or []), "native_prefix_and_conversion_equal": True,
                "adapter_prompt_and_uid_equal": True if valid else None,
                "next_accepted_after_real_overlength_reject": next_after_reject,
            })
    finally:
        oracle.close()
        adapter.close()
    return checks, conversations


def _fixture_population(root: Path, files: list[list[list[dict]]], masked=False) -> SWESourcePopulation:
    root.mkdir(parents=True, exist_ok=True)
    entries = []
    for index, conversations in enumerate(files):
        if masked:
            conversations = copy.deepcopy(conversations)
            for conversation in conversations:
                for message in conversation:
                    if "loss_mask" not in message:
                        message["loss_mask"] = int(message.get("role", message.get("from", "")).lower() == "assistant")
        path = root / f"part{index}.json"
        path.write_text(json.dumps(conversations, ensure_ascii=False))
        entries.append({"path": str(path), "local_path": str(path), "bytes": path.stat().st_size,
                        "sha256": file_sha256(path)})
    manifest = {"status": "COMPLETE", "files": entries, "total_bytes": sum(f["bytes"] for f in entries)}
    path = root / "COPY_COMPLETE.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    return SWESourcePopulation(tuple(entries), manifest, file_sha256(path))


def _excerpt(native, conversation: list[dict], turns: int, masked=False) -> list[dict]:
    positions = _positions(native, conversation, masked)
    return conversation[:positions[min(turns, len(positions)) - 1] + 1]


def _boundary_checks(args, native, tokenizer, converter, conversations) -> dict:
    args = copy.copy(args)
    args.visual_filter_receipt = None
    config = _args(args)
    population = _fixture_population(args.temporary_root / f"{args.evidence_prefix}-boundaries", [
        [[{"from": "human", "value": "No assistant in this conversation"}],
         _excerpt(native, conversations[0], 2, args.skip_masked_assistant_turns),
         _excerpt(native, conversations[1], 1, args.skip_masked_assistant_turns)],
        [_excerpt(native, conversations[0], 1, args.skip_masked_assistant_turns)],
    ], masked=args.skip_masked_assistant_turns)
    oracle = _source(native, population.filelist, args.skip_masked_assistant_turns)
    adapter = _adapter(args, native, population, tokenizer)
    rows = []
    try:
        for index in range(6):
            _, expected, rejected = _next_eligible(oracle, tokenizer, config, converter)
            rejected_before = adapter.skipped_overlength
            sample = adapter.get_samples(1)[0][0]
            assert sample.metadata["history"] == expected[:-1]
            assert sample.metadata["native_ground_truth"] == expected[-1]["ground_truth"]
            assert sample.index == sample.group_index == index
            assert sample.metadata["source"]["epoch"] == oracle.cursor.epoch
            assert adapter.skipped_overlength == rejected_before + rejected
            rows.append({name: sample.metadata["source"][name] for name in (
                "uid", "epoch", "source_item_index", "source_row_index", "assistant_turn_ordinal",
            )})
        if adapter.skipped_overlength == 0:
            assert [r["epoch"] for r in rows] == [0, 0, 0, 0, 1, 1]
            assert rows[0]["uid"] == rows[4]["uid"] and rows[1]["uid"] == rows[5]["uid"]
        assert adapter.native.skipped_no_assistant == oracle.skipped_no_assistant
        assert oracle.skipped_no_assistant >= 2
        adapter.save(args.temporary_root / f"{args.evidence_prefix}-audit")
        try:
            adapter.load(args.temporary_root / f"{args.evidence_prefix}-audit")
        except NotImplementedError as error:
            restore_error = str(error)
        else:
            raise AssertionError("Unsupported training restore was accepted")
        role_case = [{"from": "HUMAN", "value": "Question"}, {"from": "ASSISTANT"}]
        assert native_chat_messages(role_case) == converter(role_case)
    finally:
        oracle.close()
        adapter.close()
    return {"status": "PASS", "fixture": "small excerpts of the first two actual conversations, two files",
            "rows": rows, "empty_assistant_conversations_skipped": oracle.skipped_no_assistant,
            "overlength_turns_skipped": adapter.skipped_overlength,
            "conversation_file_and_epoch_boundaries": True, "restore_rejected": restore_error}


class _CharacterTokenizer:
    """Fault injection for exact length rejection, not a Qwen length estimate."""

    def apply_chat_template(self, messages, **kwargs):
        return json.dumps(messages)

    def encode(self, prompt, **kwargs):
        return list(range(len(prompt)))


def _length_rejection_check(args, native) -> dict:
    population = _fixture_population(args.temporary_root / f"{args.evidence_prefix}-length", [[[
        {"role": "user", "content": "short"},
        {"role": "assistant", "content": "x" * 600},
        {"role": "tool", "content": "reply", "tool_call_id": "first"},
        {"role": "assistant", "content": "next"},
        {"role": "assistant", "content": "last"},
    ], [{"role": "user", "content": "next conversation"}, {"role": "assistant", "content": "answer"}]]],
        masked=args.skip_masked_assistant_turns)
    config = _args(args)
    config.swe_visual_filter_receipt = None
    config.rollout_max_context_len = 512
    # These existing fault-injection fixtures test the context boundary independently.
    config.rollout_max_prompt_len = None
    source = _source(native, population.filelist, True) if args.skip_masked_assistant_turns else None
    adapter = NativeSWEDataSource(config, tokenizer=_CharacterTokenizer(), population=population, native_source=source)
    try:
        first, second = [row[0] for row in adapter.get_samples(2)]
        assert adapter.skipped_overlength == 2
        assert first.metadata["source"]["source_row_index"] == 0
        assert second.metadata["source"]["source_row_index"] == 3
        assert second.index == second.group_index == 1
        equality_population = _fixture_population(args.temporary_root / f"{args.evidence_prefix}-equality", [[
            [{"role": "user", "content": "equal threshold"}, {"role": "assistant", "content": "answer"}],
            [{"role": "user", "content": "x"}, {"role": "assistant", "content": "answer"}],
        ]], masked=args.skip_masked_assistant_turns)
        first_prefix = json.loads(Path(equality_population.filelist[0]).read_text())[0][:-1]
        config.rollout_max_context_len = len(json.dumps(first_prefix))
        source = _source(native, equality_population.filelist, True) if args.skip_masked_assistant_turns else None
        equality = NativeSWEDataSource(config, tokenizer=_CharacterTokenizer(), population=equality_population, native_source=source)
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
                "prompt_exactly_at_limit_rejected": True, "rejection_limit": "rollout_max_context_len"}
    finally:
        adapter.close()


def _four_cursors(args, native, population, tokenizer) -> dict:
    cursors = [_adapter(args, native, population, tokenizer) for _ in range(4)]
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


def _configuration_check(args, native, conversations) -> dict:
    args = copy.copy(args)
    scope = "actual source files"
    visual_fault_injection = args.skip_masked_assistant_turns and args.visual_filter_receipt is None
    if visual_fault_injection:
        from playground.users.cj.opd import s4_swe_visual_filter_1001 as visual_filter
        excerpt = _excerpt(native, conversations[0], 1, True)
        visual = copy.deepcopy(excerpt)
        visual[0]["content"] = "<image>"
        population = _fixture_population(args.temporary_root / f"{args.evidence_prefix}-native-receipt", [[visual, excerpt]], True)
        rows = [json.loads(Path(path).read_text()) for path in population.filelist]
        signatures = [{"path": path, "size": Path(path).stat().st_size, "mtime_ns": Path(path).stat().st_mtime_ns}
                      for path in population.filelist]
        files = []
        for index, (signature, trajectories) in enumerate(zip(signatures, rows)):
            excluded = [i for i, trajectory in enumerate(trajectories) if _visual_scan(native, trajectory)]
            files.append({"file_index": index, "source": signature, "signature_before": signature,
                          "signature_after": signature, "scan_finished": True, "error_type": None,
                          "counts": {"trajectories": len(trajectories), "trajectories_with_visual_payload": len(excluded)},
                          "excluded_source_item_indices": excluded})
        receipt = {"complete": True, "failure_codes": [],
                   "identity": {"filter_version": visual_filter.FILTER_VERSION,
                                "visual_policy_sha256": visual_filter.VISUAL_POLICY_SHA256, "sources": signatures},
                   "source_signatures_after_scan": signatures, "files": files,
                   "totals": {"trajectories": 2, "trajectories_with_visual_payload": 1}}
        args.source_root = Path(population.filelist[0]).parent
        args.source_manifest = args.source_root / "COPY_COMPLETE.json"
        args.visual_filter_receipt = args.source_root / "visual-filter.json"
        args.visual_filter_receipt.write_text(json.dumps(receipt, indent=2) + "\n")
        scope = "actual prefix excerpt plus visual fault injection; not a full-source filter receipt"
    config = vars(_args(args))
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
        sample = adapter.get_samples(1)[0][0]
        if visual_fault_injection:
            assert sample.metadata["source"]["source_item_index"] == 1
            assert adapter.native.skipped_excluded_trajectories == 1
            assert adapter.identity["visual_filter_verified"] is True
        prompt_ids = adapter.tokenizer.encode(sample.prompt, add_special_tokens=False)
        assert len(prompt_ids) == sample.metadata["source"]["prompt_token_count"]
        assert token_hash(prompt_ids) == sample.metadata["source"]["prompt_sha256"]
        assert sample.max_seq_len == rollout.rollout_max_context_len
        assert sample.max_response_len == _prompt_budget(rollout, len(prompt_ids))
        sampling = apply_sample_max_response_len({"max_new_tokens": rollout.rollout_max_response_len}, sample)
        assert sampling["max_new_tokens"] == sample.max_response_len
        payload, halt_status = compute_request_payload(rollout, prompt_ids, sampling)
        assert halt_status is None
        assert payload["input_ids"] == prompt_ids
        assert payload["sampling_params"]["max_new_tokens"] == sample.max_response_len
        return {"status": "PASS", "scope": scope, "path": hook.path, "config": hook.config.model_dump(),
                "uses_actual_custom_function_config_merge": True,
                "runtime_config_type": type(rollout).__name__,
                "runtime_config_builder": "existing make_rollout_config with real parser defaults and model_validate",
                "nonexistent_max_seq_len_launch_field_absent": True,
                "rollout_length_limits": {name: config[name] for name in (
                    "rollout_max_context_len", "rollout_max_prompt_len", "rollout_max_response_len",
                )},
                "accepted_source_uid": sample.metadata["source"]["uid"], "sample_index": sample.index,
                "native_request_prompt_tokens": len(payload["input_ids"]),
                "native_request_prompt_sha256": token_hash(payload["input_ids"]),
                "native_request_max_new_tokens": payload["sampling_params"]["max_new_tokens"],
                "native_request_payload_constructed": True, "native_request_sent": False}
    finally:
        adapter.close()


def _actual_file_boundaries(args, native, population, tokenizer) -> dict:
    config = _args(args)
    oracle = _source(native, population.filelist, args.skip_masked_assistant_turns, _exclusions(args, native, population))
    converter = _native_converter(args.native_recipe)
    adapter = _adapter(args, native, population, tokenizer)
    rows = []
    try:
        for index, path in enumerate(population.filelist):
            expected, converted, rejected = _next_eligible(oracle, tokenizer, config, converter)
            rejected_before = adapter.skipped_overlength
            sample = adapter.get_samples(1)[0][0]
            source = sample.metadata["source"]
            assert source["path"] == path
            if rejected == 0:
                assert source["source_item_index"] == 0
            assert sample.metadata["history"] == converted[:-1]
            assert sample.metadata["native_ground_truth"] == expected["conversation"][-1]["ground_truth"]
            assert adapter.skipped_overlength == rejected_before + rejected
            rows.append({"file_index": index, "uid": source["uid"], "epoch": source["epoch"],
                         "prompt_token_count": source["prompt_token_count"]})
            with Path(path).open("rb") as stream:
                stream.seek(-16, 2)
                tail = stream.read()
            closing = Path(path).stat().st_size - len(tail) + tail.rfind(b"]")
            assert closing >= 0 and tail.rfind(b"]") >= 0
            state = adapter.native.state_dict()
            state["active"] = None
            state["cursor"]["next_offset"] = closing
            adapter.native.load_state_dict(state)
            oracle.load_state_dict(state)
        wrapped = adapter.get_samples(1)[0][0].metadata["source"]
        assert wrapped["epoch"] == 1 and wrapped["uid"] == rows[0]["uid"]
        return {"status": "PASS", "scope": "native test cursor placed at each actual file's closing bracket; not a full-epoch scan",
                "ordered_files": rows, "wrapped_uid": wrapped["uid"], "wrapped_epoch": wrapped["epoch"]}
    finally:
        oracle.close()
        adapter.close()


def _representative_schema(args, native, population) -> list[dict]:
    rows = []
    for index, path in enumerate(population.filelist):
        cursor = _cursor(native, [path])
        try:
            for conversation_index in range(2):
                record = cursor.next_record()
                conversation = record.value
                positions = _positions(native, conversation, args.skip_masked_assistant_turns)
                visual = _visual_scan(native, conversation) if args.skip_masked_assistant_turns else None
                assert visual is not True, "Selected parity conversation is natively visual-excluded"
                rows.append({"file_index": index, "source_item_index": conversation_index,
                             "record_bytes": record.item_end - record.item_start,
                             "messages": len(conversation), "eligible_assistants": len(positions),
                             "all_assistants": sum(native.message_role(m) == "assistant" for m in conversation),
                             "masked_assistants": sum(native.message_role(m) == "assistant" and m.get("loss_mask") == 0
                                                      for m in conversation),
                             "nonempty_reasoning_messages": sum(bool(m.get("reasoning_content")) for m in conversation),
                             "tools": len(conversation[0].get("tools") or []), "native_visual_payload": visual,
                             "raw_conversation_sha256": _digest(conversation)})
        finally:
            cursor.close()
    return rows


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
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source-root", "source-manifest", "native-loader", "native-recipe", "tokenizer",
                 "chat-template", "temporary-root", "output-root"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--native-loader-sha256", required=True)
    parser.add_argument("--rollout-max-context-len", type=int, required=True)
    parser.add_argument("--rollout-max-prompt-len", type=int,
                        help="Native prompt limit; omitted means no prompt-specific filter")
    parser.add_argument("--rollout-max-response-len", type=int,
                        help="Native response maximum; omitted retains the historical context-sized maximum")
    parser.add_argument("--turn-ordinals", default="1,2,8,32,64,100,last")
    parser.add_argument("--model-source-receipt", type=Path)
    parser.add_argument("--skip-masked-assistant-turns", action="store_true")
    parser.add_argument("--visual-filter-receipt", type=Path)
    parser.add_argument("--evidence-prefix", default="input")
    parser.add_argument("--file-last-prefixes", default="")
    args = parser.parse_args()
    for name in ("rollout_max_context_len", "rollout_max_prompt_len", "rollout_max_response_len"):
        if vars(args)[name] is not None and vars(args)[name] <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    if args.skip_masked_assistant_turns and args.evidence_prefix == "input":
        raise ValueError("Use a separate evidence prefix for mask-aware inputs; historical input-* evidence is protected")
    logging.basicConfig(level=logging.INFO)
    population = load_source_population(args.source_root, args.source_manifest)
    native = load_swe_native_module(_args(args))
    converter = _native_converter(args.native_recipe)
    tokenizer = load_tokenizer(str(args.tokenizer), chat_template_path=str(args.chat_template), local_files_only=True)
    rows, conversations = _actual_prefix_checks(args, native, population, tokenizer, converter)
    for index in (int(value) for value in args.file_last_prefixes.split(",") if value):
        probe_args = copy.copy(args)
        probe_args.turn_ordinals = "last"
        subset = SWESourcePopulation((population.files[index],), population.manifest, population.manifest_sha256)
        extra, _ = _actual_prefix_checks(probe_args, native, subset, tokenizer, converter)
        for row in extra:
            row["file_index"] = index
        rows.extend(extra)
    report = {
        "task_id": "T01-inputs", "status": ("PASS_REPRESENTATIVE_PARITY_VISUAL_RECEIPT_PENDING"
                                             if args.skip_masked_assistant_turns and args.visual_filter_receipt is None else "PASS"),
        "python": platform.python_version(),
        "transformers": transformers.__version__, "argv": sys.argv,
        "native_recipe_sha256": file_sha256(args.native_recipe),
        "actual_prefix_checks": rows,
        "boundary_checks": _boundary_checks(args, native, tokenizer, converter, conversations),
        "length_rejection": _length_rejection_check(args, native),
        "four_cursors": _four_cursors(args, native, population, tokenizer),
        "configuration": _configuration_check(args, native, conversations),
        "actual_file_boundaries": _actual_file_boundaries(args, native, population, tokenizer),
        "representative_schema": _representative_schema(args, native, population),
        "limits": ["Only selected actual prefixes were Qwen encoded, not all raw assistant turns",
                   "Conversation/file/EOF regression fixtures use actual conversation excerpts, not a full epoch scan",
                   "No Step/Qwen token or prompt byte equality is asserted; Qwen explicitly renders system.tools",
                   "Tokenizer compatibility with teacher models and benchmark overlap are separately owned"],
    }
    if args.skip_masked_assistant_turns and args.visual_filter_receipt is None:
        report["limits"].append("Representative visual checks and a native receipt fault-injection fixture are not the full-source visual exclusion receipt")
    args.output_root.mkdir(parents=True, exist_ok=True)
    adapter = _adapter(args, native, population, tokenizer)
    try:
        model_reference = _model_receipt_reference(args.model_source_receipt, adapter.identity)
        report["parent_model_source_receipt"] = model_reference
        adapter.identity["candidate_data_source_config"] = {
            name: value for name, value in vars(_args(args)).items() if name.startswith("swe_")
        }
        (args.output_root / f"{args.evidence_prefix}-config.json").write_text(json.dumps(adapter.identity, indent=2) + "\n")
    finally:
        adapter.close()
    (args.output_root / f"{args.evidence_prefix}-source-manifest.json").write_text(json.dumps({
        "manifest": population.manifest, "manifest_sha256": population.manifest_sha256,
        "local_verified_files": list(population.files), "local_verified_bytes": population.manifest["total_bytes"],
        "manifest_reported_conversations": (sum(f["conversations"] for f in population.files)
                                             if all("conversations" in f for f in population.files) else None),
        "manifest_reported_raw_assistant_turns": (sum(f["assistant_turns"] for f in population.files)
                                                   if all("assistant_turns" in f for f in population.files) else None),
        "counts_independently_recomputed_in_this_check": False,
        "parent_model_source_receipt": model_reference,
    }, indent=2) + "\n")
    (args.output_root / f"{args.evidence_prefix}-parity.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "prefix_checks": len(rows),
                      "lengths": [row["prompt_token_count"] for row in rows],
                      "evidence": str(args.output_root / f"{args.evidence_prefix}-parity.json")}))


if __name__ == "__main__":
    main()
