"""Run CPU-only native SWE input parity, real Qwen rendering and cursor checks.

Example:
    python -m tests.manual.agent_opd.check_swe_inputs --source-root SOURCES \
        --source-manifest SOURCES/COPY_COMPLETE.json --native-loader LOADER.py \
        --native-loader-sha256 SHA256 --native-recipe RECIPE.py \
        --tokenizer QWEN_TOKENIZER --chat-template TEMPLATE.jinja \
        --rollout-max-context-len 131072 --temporary-root TEMP --output-root TASK/evidence
"""

import argparse
import ast
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
    load_native_module,
    load_source_population,
    native_chat_messages,
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


def _source(native, filelist):
    return native.OnlineTrajectoryTurnSource(
        filelist, domain="reasoning", source_group="swe",
        source_load_path=None, source_load_safetensors=None,
    )


def _args(args) -> SimpleNamespace:
    return SimpleNamespace(
        swe_source_root=str(args.source_root), swe_source_manifest=str(args.source_manifest),
        swe_native_loader_path=str(args.native_loader), swe_native_loader_sha256=args.native_loader_sha256,
        hf_checkpoint=str(args.tokenizer), chat_template_path=str(args.chat_template),
        apply_chat_template_kwargs={"preserve_thinking": True, "enable_thinking": True},
        rollout_max_context_len=args.rollout_max_context_len,
        rollout_max_response_len=args.rollout_max_context_len, n_samples_per_prompt=1,
    )


def _actual_prefix_checks(args, native, population, tokenizer, converter) -> tuple[list[dict], list[list[dict]]]:
    cursor = native.SequentialJsonArrayCursor(population.filelist)
    conversations = [cursor.next_record().value, cursor.next_record().value]
    cursor.close()
    positions = [i for i, message in enumerate(conversations[0]) if native.message_role(message) == "assistant"]
    ordinals = {int(value) for value in args.turn_ordinals.split(",") if value != "last"}
    if "last" in args.turn_ordinals.split(","):
        ordinals.add(len(positions))
    oracle = _source(native, population.filelist)
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


def _fixture_population(root: Path, files: list[list[list[dict]]]) -> SWESourcePopulation:
    root.mkdir(parents=True, exist_ok=True)
    entries = []
    for index, conversations in enumerate(files):
        path = root / f"part{index}.json"
        path.write_text(json.dumps(conversations, ensure_ascii=False))
        entries.append({"path": str(path), "local_path": str(path), "bytes": path.stat().st_size,
                        "sha256": file_sha256(path)})
    manifest = {"status": "COMPLETE", "files": entries, "total_bytes": sum(f["bytes"] for f in entries)}
    return SWESourcePopulation(tuple(entries), manifest, _digest(manifest))


def _excerpt(native, conversation: list[dict], turns: int) -> list[dict]:
    positions = [i for i, m in enumerate(conversation) if native.message_role(m) == "assistant"]
    return conversation[:positions[min(turns, len(positions)) - 1] + 1]


def _boundary_checks(args, native, tokenizer, converter, conversations) -> dict:
    population = _fixture_population(args.temporary_root / "input-boundaries", [
        [[{"from": "human", "value": "No assistant in this conversation"}],
         _excerpt(native, conversations[0], 2), _excerpt(native, conversations[1], 1)],
        [_excerpt(native, conversations[0], 1)],
    ])
    oracle = _source(native, population.filelist)
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
        assert adapter.native.skipped_no_assistant == oracle.skipped_no_assistant == 2
        adapter.save(args.temporary_root / "input-audit")
        try:
            adapter.load(args.temporary_root / "input-audit")
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
            "rows": rows, "empty_assistant_conversations_skipped": 2,
            "conversation_file_and_epoch_boundaries": True, "restore_rejected": restore_error}


class _CharacterTokenizer:
    """Fault injection for exact length rejection, not a Qwen length estimate."""

    def apply_chat_template(self, messages, **kwargs):
        return json.dumps(messages)

    def encode(self, prompt, **kwargs):
        return list(range(len(prompt)))


def _length_rejection_check(args, native) -> dict:
    population = _fixture_population(args.temporary_root / "input-length", [[[
        {"role": "user", "content": "short"},
        {"role": "assistant", "content": "x" * 600},
        {"role": "tool", "content": "reply", "tool_call_id": "first"},
        {"role": "assistant", "content": "next"},
        {"role": "assistant", "content": "last"},
    ], [{"role": "user", "content": "next conversation"}, {"role": "assistant", "content": "answer"}]]])
    config = _args(args)
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


def _configuration_check(args) -> dict:
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
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source-root", "source-manifest", "native-loader", "native-recipe", "tokenizer",
                 "chat-template", "temporary-root", "output-root"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--native-loader-sha256", required=True)
    parser.add_argument("--rollout-max-context-len", type=int, required=True)
    parser.add_argument("--turn-ordinals", default="1,2,8,32,64,100,last")
    parser.add_argument("--model-source-receipt", type=Path)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    population = load_source_population(args.source_root, args.source_manifest)
    native = load_native_module(args.native_loader, args.native_loader_sha256)
    converter = _native_converter(args.native_recipe)
    tokenizer = load_tokenizer(str(args.tokenizer), chat_template_path=str(args.chat_template), local_files_only=True)
    rows, conversations = _actual_prefix_checks(args, native, population, tokenizer, converter)
    report = {
        "task_id": "T01-inputs", "status": "PASS", "python": platform.python_version(),
        "transformers": transformers.__version__, "argv": sys.argv,
        "native_recipe_sha256": file_sha256(args.native_recipe),
        "actual_prefix_checks": rows,
        "boundary_checks": _boundary_checks(args, native, tokenizer, converter, conversations),
        "length_rejection": _length_rejection_check(args, native),
        "four_cursors": _four_cursors(args, population, tokenizer),
        "configuration": _configuration_check(args),
        "limits": ["Only selected actual prefixes were Qwen encoded, not all raw assistant turns",
                   "Conversation/file/EOF regression fixtures use actual conversation excerpts, not a full epoch scan",
                   "No Step/Qwen token or prompt byte equality is asserted; Qwen explicitly renders system.tools",
                   "Tokenizer compatibility with teacher models and benchmark overlap are separately owned"],
    }
    args.output_root.mkdir(parents=True, exist_ok=True)
    adapter = NativeSWEDataSource(_args(args), tokenizer=tokenizer, population=population)
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
