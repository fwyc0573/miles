"""Audit the SWE-1003 0913 source files in place for the mask-aware interleaved order.

Reads the files named by the pinned Steptron source manifest module once, in its
order, through the pinned native cursor. Training turns follow the pinned
loss-mask rule (eligible_assistant_positions); visual trajectories follow the
pinned predicate (_scan_message on every message). For every trainable
conversation it renders the prefix before the last training turn with the Qwen
template, and finds the first over-length training turn by bisection when that
prefix reaches rollout_max_context_len (prefix lengths grow with the turn
ordinal). It then drives the native mixer over MaskAwareSWETurnSource for each
open-conversations x block-turns config until the requested number of accepted
turns, rejecting over-length turns as the adapter does.

Outputs counts, distributions, key names and source item indices only; no
conversation text. The source manifest it writes is read by
swe_inputs.load_source_population with the in-place source directory as root.
"""

import argparse
import hashlib
import json
import math
import statistics
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from tests.manual.agent_opd.swe_inputs import (
    BASE_LOADER,
    TURN_DATA,
    TURN_SOURCES,
    file_sha256,
    history_tools,
    load_pinned_modules,
    render_qwen_history,
)

from miles.utils.processing_utils import load_tokenizer

SOURCE_MANIFEST = "playground.users.cj.opd.s4_swe_source_manifest_1001"
VISUAL_AUDIT = "playground.users.cj.opd.s4_swe_visual_audit_1001"
TURN_SOURCE = TURN_SOURCES["loss_masked"]
USER_ROLES = ("user", "human")
SHORT_VALUE_CHARS = 32


@dataclass
class SourceConversation:
    file_index: int
    source_item_index: int
    messages: int
    assistants: int
    eligible: int
    visual: bool
    prompt_key: str | None
    longest_prompt_tokens: int | None = None
    first_overlength_ordinal: int | None = None

    @property
    def trainable(self) -> bool:
        return not self.visual and self.eligible > 0


def distribution(values) -> dict:
    ordered = sorted(values)
    if not ordered:
        return {"count": 0}
    return {
        "count": len(ordered), "min": ordered[0], "median": statistics.median(ordered),
        "p90": ordered[math.ceil(0.9 * len(ordered)) - 1], "max": ordered[-1],
        "mean": sum(ordered) / len(ordered),
    }


def short_value(value) -> str:
    """Option values such as reasoning_effort are short labels; anything else is reported by type."""
    if isinstance(value, (str, bool, int, float)) and len(str(value)) <= SHORT_VALUE_CHARS:
        return repr(value)
    return f"<{type(value).__name__}>"


def prompt_key(messages: list) -> str | None:
    """Group exact first-user text without claiming a SWE instance identity."""
    for message in messages:
        if isinstance(message, dict) and message.get("role", message.get("from")) in USER_ROLES:
            content = message.get("content", message.get("value"))
            text = content if isinstance(content, str) else json.dumps(content, sort_keys=True)
            return hashlib.sha256(text.encode()).hexdigest()[:16]
    return None


class PromptMeter:
    """Prompt token count of the prefix before a training turn, as the adapter renders it."""

    def __init__(self, tokenizer, template_kwargs: dict, context_tokens: int):
        self.tokenizer = tokenizer
        self.template_kwargs = template_kwargs
        self.context_tokens = context_tokens
        self.renders = 0

    def tokens(self, messages: list, position: int) -> int:
        history = TURN_SOURCE.normalize_history(messages[:position])
        tools = history_tools(history)
        self.renders += 1
        return len(render_qwen_history(self.tokenizer, history, tools, self.template_kwargs)[1])

    def measure(self, conversation: SourceConversation, messages: list, eligible: list[int]) -> None:
        conversation.longest_prompt_tokens = self.tokens(messages, eligible[-1])
        if conversation.longest_prompt_tokens < self.context_tokens:
            return
        low, high = 0, len(eligible) - 1  # eligible[high] is over-length
        while low < high:
            middle = (low + high) // 2
            if self.tokens(messages, eligible[middle]) >= self.context_tokens:
                high = middle
            else:
                low = middle + 1
        conversation.first_overlength_ordinal = low + 1


def scan_sources(modules: dict, files: list[Path], meter: PromptMeter) -> tuple[list[SourceConversation], dict]:
    native, turn_data, visual = modules[BASE_LOADER], modules[TURN_DATA], modules[VISUAL_AUDIT]
    visual_counts = Counter()
    signals = defaultdict(Counter)
    first_message_keys, message_keys, meta_keys, option_values = Counter(), Counter(), Counter(), defaultdict(Counter)
    meta_values = defaultdict(set)
    conversations = []
    started = time.monotonic()
    cursor = native.SequentialJsonArrayCursor([str(path) for path in files])
    while True:
        record = cursor.next_record()
        if record.epoch:
            break
        messages = record.value
        eligible = turn_data.eligible_assistant_positions(messages)
        # A list, not any(): every message updates the predicate's counters.
        visual_messages = [visual._scan_message(message, visual_counts, signals) for message in messages]
        conversation = SourceConversation(
            file_index=record.file_idx, source_item_index=record.source_item_index, messages=len(messages),
            assistants=sum(native.message_role(message) == "assistant" for message in messages),
            eligible=len(eligible), visual=any(visual_messages), prompt_key=prompt_key(messages),
        )
        first_message_keys.update(messages[0].keys())
        for name in ("reasoning_effort", "preserve_thinking"):
            if name in messages[0]:
                option_values[name][short_value(messages[0][name])] += 1
        for message in messages:
            message_keys.update(f"{native.message_role(message)}.{key}" for key in message)
            meta = message.get("meta")
            if isinstance(meta, dict):
                for key, value in meta.items():
                    meta_keys[key] += 1
                    meta_values[key].add(hashlib.sha256(json.dumps(value, sort_keys=True).encode()).digest()[:8])
        if conversation.trainable:
            meter.measure(conversation, messages, eligible)
        conversations.append(conversation)
        if len(conversations) % 200 == 0:
            print(f"[SWE1003_AUDIT] scanned={len(conversations)} file={record.file_idx} renders={meter.renders} "
                  f"elapsed_s={time.monotonic() - started:.0f}", flush=True)
    cursor.close()
    schema = {
        "first_message_keys": dict(first_message_keys),
        "message_keys_by_role": dict(message_keys),
        "meta_keys": {key: {"messages": count, "distinct_values": len(meta_values[key])} for key, count in meta_keys.items()},
        "first_message_option_values": {name: dict(values) for name, values in option_values.items()},
        "visual_counts": dict(visual_counts),
        "visual_signals": {name: dict(counter) for name, counter in signals.items()},
        "scan_elapsed_s": time.monotonic() - started,
        "prompt_renders": meter.renders,
    }
    return conversations, schema


def prompt_adjacency(trainable: list[SourceConversation], window: int) -> dict:
    keys = [conversation.prompt_key for conversation in trainable]
    per_prompt = Counter(key for key in keys if key is not None)
    runs = []
    run = 0
    previous = None
    for current in keys:
        if current is not None and current == previous:
            run += 1
        else:
            if run:
                runs.append(run)
            run = int(current is not None)
        previous = current
    if run:
        runs.append(run)
    windows = [len({key for key in keys[start:start + window] if key is not None})
               for start in range(max(1, len(keys) - window + 1))]
    return {
        "key": "sha256 of the first user message, 16 hex",
        "conversations_without_key": keys.count(None),
        "distinct_prompt_groups": len(per_prompt),
        "conversations_per_prompt_group": distribution(per_prompt.values()),
        "same_prompt_runs_in_file_order": distribution(runs),
        f"distinct_prompt_groups_in_{window}_consecutive_conversations": distribution(windows),
    }


def simulate(modules: dict, files: list[Path], exclusions: list[list[int]], conversations: list[SourceConversation],
             active: int, block: int, updates: int, turns_per_update: int, trend_window: int) -> dict:
    native, turn_data = modules[BASE_LOADER], modules[TURN_DATA]
    by_key = {(c.file_index, c.source_item_index): c for c in conversations}
    file_index = {str(path): index for index, path in enumerate(files)}
    sources = [turn_data.MaskAwareSWETurnSource(
        [str(path) for path in files], excluded_source_item_indices=exclusions, domain="reasoning",
        source_group="swe", source_load_path=None, source_load_safetensors=None,
    ) for _ in range(active)]
    cursor = sources[0].cursor
    for source in sources:
        source.cursor = cursor
    mixer = native.TurnBalancedTrajectoryBlockMixer(sources, [1.0] * active, trajectory_block_turns=block)
    first_update, last_update, finished_update = {}, {}, {}
    per_update_conversations = [set() for _ in range(updates)]
    seen_turns = set()
    draws = accepted = rejected = repeated = 0
    started = time.monotonic()
    while accepted < updates * turns_per_update:
        ground_truth = next(mixer)["conversation"][-1]["ground_truth"]
        draws += 1
        key = (file_index[ground_truth["data_path"]], ground_truth["source_item_index"])
        conversation = by_key[key]
        ordinal = ground_truth["assistant_turn_ordinal"]
        update = accepted // turns_per_update
        repeated += (key, ordinal) in seen_turns
        seen_turns.add((key, ordinal))
        if ordinal == conversation.eligible:
            finished_update[key] = update
        if conversation.first_overlength_ordinal is not None and ordinal >= conversation.first_overlength_ordinal:
            rejected += 1
            continue
        accepted += 1
        first_update.setdefault(key, update)
        last_update[key] = update
        per_update_conversations[update].add(key)
    mixer.close()
    spans = [last_update[key] - first_update[key] + 1 for key in first_update]
    return {
        "active_conversations": active, "block_turns": block, "updates": updates,
        "turns_per_update": turns_per_update, "draws": draws, "accepted": accepted,
        "rejected_overlength": rejected, "repeated_turns": repeated, "final_cursor_epoch": cursor.epoch,
        "conversations_trained": len(first_update),
        "conversations_finished": len(finished_update),
        "update_span": distribution(spans),
        f"conversations_with_span_at_least_{trend_window + 1}": sum(span > trend_window for span in spans),
        "conversations_per_update": distribution(len(keys) for keys in per_update_conversations),
        "tasks_per_update": None,
        "prompt_groups_per_update": distribution(
            len({by_key[key].prompt_key for key in keys if by_key[key].prompt_key is not None})
            for keys in per_update_conversations),
        "mean_draw_ms": (time.monotonic() - started) * 1000 / draws,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--steptron-root", type=Path, required=True)
    parser.add_argument("--base-loader-sha256", required=True)
    parser.add_argument("--source-manifest-sha256", required=True)
    parser.add_argument("--turn-data-sha256", required=True)
    parser.add_argument("--visual-audit-sha256", required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--chat-template", type=Path, required=True)
    parser.add_argument("--chat-template-kwargs", type=json.loads, required=True)
    parser.add_argument("--rollout-max-context-len", type=int, required=True)
    parser.add_argument("--simulate", nargs="+", required=True, help="open-conversations x block-turns, e.g. 32x8")
    parser.add_argument("--updates", type=int, required=True)
    parser.add_argument("--turns-per-update", type=int, required=True)
    parser.add_argument("--trend-window", type=int, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    # Load order: turn data imports the base loader, visual audit the source manifest.
    pins = {BASE_LOADER: args.base_loader_sha256, SOURCE_MANIFEST: args.source_manifest_sha256,
            TURN_DATA: args.turn_data_sha256, VISUAL_AUDIT: args.visual_audit_sha256}
    modules = load_pinned_modules(args.steptron_root, pins)
    original_paths = list(modules[SOURCE_MANIFEST].SWE_DATA_FILES)
    files = [args.source_root / Path(path).name for path in original_paths]
    tokenizer = load_tokenizer(args.tokenizer, chat_template_path=str(args.chat_template), local_files_only=True)
    meter = PromptMeter(tokenizer, args.chat_template_kwargs, args.rollout_max_context_len)

    signatures = [{"bytes": path.stat().st_size, "mtime_ns": path.stat().st_mtime_ns} for path in files]
    conversations, schema = scan_sources(modules, files, meter)
    hashes = [file_sha256(path) for path in files]
    if [{"bytes": path.stat().st_size, "mtime_ns": path.stat().st_mtime_ns} for path in files] != signatures:
        raise ValueError("SWE source files changed during the audit")

    per_file = []
    for index, (path, original, signature, sha256) in enumerate(zip(files, original_paths, signatures, hashes)):
        rows = [c for c in conversations if c.file_index == index]
        per_file.append({
            "path": str(path), "recipe_path": original, "sha256": sha256, **signature,
            "conversations": len(rows), "assistant_turns": sum(c.assistants for c in rows),
            "eligible_turns": sum(c.eligible for c in rows),
            "visual_source_item_indices": [c.source_item_index for c in rows if c.visual],
            "eligible_turns_excluded_as_visual": sum(c.eligible for c in rows if c.visual),
            "conversations_without_eligible_turns": sum(not c.visual and c.eligible == 0 for c in rows),
            "trainable_eligible_turns": sum(c.eligible for c in rows if c.trainable),
        })
    trainable = [c for c in conversations if c.trainable]
    exclusions = [entry["visual_source_item_indices"] for entry in per_file]
    assistants = sum(c.assistants for c in conversations)
    eligible = sum(c.eligible for c in conversations)
    overlength = [c for c in trainable if c.first_overlength_ordinal is not None]
    window = max(int(spec.split("x")[0]) for spec in args.simulate)
    simulations = [simulate(modules, files, exclusions, conversations, *map(int, spec.split("x")),
                            args.updates, args.turns_per_update, args.trend_window) for spec in args.simulate]

    identity = {
        "steptron_root": str(args.steptron_root.resolve()), "pinned_module_sha256": pins,
        "source_root": str(args.source_root), "tokenizer": args.tokenizer,
        "tokenizer_json_sha256": file_sha256(Path(args.tokenizer) / "tokenizer.json"),
        "chat_template": str(args.chat_template), "chat_template_sha256": file_sha256(args.chat_template),
        "chat_template_kwargs": args.chat_template_kwargs, "tools_field": "first message tools or tool_schemas",
        "rollout_max_context_len": args.rollout_max_context_len, "python": sys.version,
        "overlength_rule": "prompt_token_count >= rollout_max_context_len; prefix length assumed non-decreasing in the turn ordinal",
    }
    audit = {
        "identity": identity, "files": per_file,
        "totals": {
            "files": len(files), "bytes": sum(s["bytes"] for s in signatures), "conversations": len(conversations),
            "assistant_turns": assistants, "eligible_turns": eligible, "masked_assistant_turns": assistants - eligible,
            "masked_assistant_share": (assistants - eligible) / assistants if assistants else None,
            "visual_conversations": sum(c.visual for c in conversations),
            "eligible_turns_excluded_as_visual": sum(c.eligible for c in conversations if c.visual),
            "conversations_without_eligible_turns": sum(not c.visual and c.eligible == 0 for c in conversations),
            "trainable_conversations": len(trainable), "trainable_eligible_turns": sum(c.eligible for c in trainable),
            "overlength_conversations": len(overlength),
            "overlength_turns": sum(c.eligible - c.first_overlength_ordinal + 1 for c in overlength),
        },
        "trainable_distributions": {
            "eligible_turns_per_conversation": distribution(c.eligible for c in trainable),
            "assistants_per_conversation": distribution(c.assistants for c in trainable),
            "masked_assistants_per_conversation": distribution(c.assistants - c.eligible for c in trainable),
            "longest_prompt_tokens": distribution(c.longest_prompt_tokens for c in trainable),
        },
        "task_identity": {"status": "UNVERIFIED", "distinct_tasks": None,
                          "reason": "No validated SWE instance/repository identity mapping; first-user text is only a proxy"},
        "prompt_adjacency": prompt_adjacency(trainable, window),
        "schema": schema,
        "simulations": simulations,
        "eligible_turns_per_conversation": [[c.eligible for c in conversations if c.file_index == index]
                                            for index in range(len(files))],
    }
    manifest = {
        "status": "COMPLETE", "source_root": str(args.source_root), "read_in_place": True,
        "files": [{name: entry[name] for name in ("path", "recipe_path", "sha256", "bytes", "mtime_ns", "conversations",
                                                  "assistant_turns", "eligible_turns", "visual_source_item_indices")}
                  for entry in per_file],
        "total_bytes": sum(s["bytes"] for s in signatures),
    }
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "swe1003-source-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    (args.output_root / "swe1003-source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "totals": audit["totals"],
                      "eligible_turns_per_conversation": audit["trainable_distributions"]["eligible_turns_per_conversation"],
                      "simulations": [{k: s[k] for k in ("active_conversations", "block_turns", "update_span",
                                                         "repeated_turns")} for s in simulations]}))


if __name__ == "__main__":
    main()
