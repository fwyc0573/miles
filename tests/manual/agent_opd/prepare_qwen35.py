"""Freeze the full pinned GLM-history population for fresh Qwen3.5 OPD.

Prepare once and reuse train.jsonl, monitor.jsonl and population.json across all
pairs with verified compatible tokenizers. Existing Qwen generation consumes the
rendered prompt and validates its token count/hash; historical targets are only
provenance. Native Dataset shuffle/cycling owns the training order (seed 42).

Example:
    python -m tests.manual.agent_opd.prepare_qwen35 --manifest MANIFEST \
        --glm-tokenizer GLM_TOKENIZER --qwen-tokenizer QWEN_TOKENIZER \
        --output-root NEW_DIRECTORY

Use --chat-template-path and --apply-chat-template-kwargs for the existing
single-turn template controls. Defaults preserve all historical reasoning and
enable new thinking; an explicit preserve_thinking=false keeps the native
last-real-user omission behavior. --source-root scopes local fixture reads;
production source reads default to the personal codesign namespace.
"""

import argparse
import hashlib
import json
import platform
import random
from collections import Counter
from pathlib import Path

from examples.agentic_opd.glm_turns import normalize_tool_arguments, token_hash
from tests.manual.agent_opd.prepare_glm5_2 import (
    _make_row,
    _read_conversation,
    _verify_manifest_references,
    _verify_tokenizer_assets,
)
from transformers import AutoTokenizer

from miles.utils.chat_template_utils import resolve_fixed_chat_template

CONTEXT_TOKENS = 131072
RESPONSE_TOKENS = 8192
PREFIX_TOKENS = CONTEXT_TOKENS - RESPONSE_TOKENS
MONITOR_PER_STRATUM = 8
SEED = 42
LENGTH_STRATA = (("short", 0, 32768), ("medium", 32768, 65536), ("long", 65536, PREFIX_TOKENS))


def _template_settings(path: Path | None, kwargs: dict) -> tuple[Path, str, dict]:
    default_path, defaults = resolve_fixed_chat_template("qwen35")
    # Single-turn preparation allows caller overrides; TITO's append-only
    # required-kwargs invariant is unchanged.
    settings = {**defaults, "enable_thinking": True, **kwargs}
    for name in ("preserve_thinking", "enable_thinking"):
        if not isinstance(settings[name], bool):
            raise ValueError(f"{name} must be a JSON boolean")
    reserved = {"tools", "chat_template", "tokenize", "add_generation_prompt", "return_dict"} & settings.keys()
    if reserved:
        raise ValueError(f"Template rendering arguments are owned by preparation: {sorted(reserved)}")
    path = path if path is not None else Path(default_path)
    return path, path.read_text(), settings


def _verify_population_membership(manifest: dict, references: dict) -> set[str]:
    """Require every source turn to retain its pinned parent training membership."""
    excluded = set()
    for category, bank in manifest["categories"].items():
        parent = references["parents"][category]
        pool, selection = parent["pool"], parent["selection"]
        if selection["membership"]["sha256"] != manifest["membership"]["sha256"]:
            raise ValueError(f"{category}: inherited benchmark membership differs")
        selected = {
            (row["file"], row["source_item_index"], row["group_id"])
            for row in selection["selected_conversations"]
        }
        excluded.update(row["group_id"] for row in pool["probe"])
        for row in bank["train"]:
            original = pool["train"][row["parent_row"]]
            fields = ("source_item_index", "assistant_turn_index", "item_start", "item_end", "group_id")
            if any(row[field] != original[field] for field in fields):
                raise ValueError(f"{category}: source turn/group differs from pinned parent training membership")
            file, original_file = manifest["files"][row["file"]], pool["files"][original["file"]]
            if any(file[field] != original_file[field] for field in ("path", "sha256")):
                raise ValueError(f"{category}: source file differs from pinned parent training membership")
            if (original["file"], row["source_item_index"], row["group_id"]) not in selected:
                raise ValueError(f"{category}: task group is absent from pinned parent selection")
    return excluded


def _stratum(length: int) -> str | None:
    return next((name for name, lower, upper in LENGTH_STRATA if lower < length <= upper), None)


def _render_row(row: dict, tokenizer, template: str, kwargs: dict) -> tuple[dict, dict]:
    metadata = row["metadata"]
    prompt = tokenizer.apply_chat_template(
        normalize_tool_arguments(metadata["history"]),
        tools=metadata["tools"],
        chat_template=template,
        tokenize=False,
        add_generation_prompt=True,
        **kwargs,
    )
    ids = tokenizer.encode(prompt, add_special_tokens=False)
    source = metadata["source"]
    qwen_source = {
        "uid": source["uid"],
        "category": source["category"],
        "group_id": source["group_id"],
        "glm_source": source,
        "prompt_token_count": len(ids),
        "prompt_sha256": token_hash(ids),
    }
    metadata = {
        **metadata,
        "source": qwen_source,
        "thinking_enabled": kwargs["enable_thinking"],
        "chat_template_kwargs": dict(kwargs),
    }
    evidence = {
        **{key: qwen_source[key] for key in ("uid", "category", "group_id", "prompt_token_count", "prompt_sha256")},
        "glm_prompt_token_count": source["prompt_token_count"],
        "conversation_sha256": source["conversation_sha256"],
        "file_sha256": source["file_sha256"],
        "stratum": _stratum(len(ids)),
        "exclusions": [],
    }
    return {"prompt": prompt, "metadata": metadata}, evidence


def _prepare_population(manifest: dict, glm_tokenizer, qwen_tokenizer, template: str, kwargs: dict, source_root: Path):
    rows, population = {}, []
    for category, bank in manifest["categories"].items():
        for source in bank["train"]:
            file = manifest["files"][source["file"]]
            conversation = _read_conversation(file, source, source_root=source_root)
            row, _ = _make_row(glm_tokenizer, conversation, file, source, category)
            row, evidence = _render_row(row, qwen_tokenizer, template, kwargs)
            uid = evidence["uid"]
            if uid in rows:
                raise ValueError(f"The manifest repeats a source turn: {uid}")
            rows[uid] = row
            population.append(evidence)
    return rows, population


def _select_monitoring(eligible: list[dict]) -> list[dict]:
    banks = {name: [row for row in eligible if row["stratum"] == name] for name, _, _ in LENGTH_STRATA}
    shortages = {name: len(rows) for name, rows in banks.items() if len(rows) < MONITOR_PER_STRATUM}
    if shortages:
        raise ValueError(f"Monitoring coverage is INCOMPLETE: need {MONITOR_PER_STRATUM} prefixes per stratum; {shortages}")
    # At least one whole task group must remain for optimization. A possible
    # training group leaves all three monitoring banks with eight prefixes.
    counts = {name: Counter(row["group_id"] for row in rows) for name, rows in banks.items()}
    groups = sorted({row["group_id"] for row in eligible})
    training_candidates = [
        group for group in groups
        if all(len(banks[name]) - counts[name][group] >= MONITOR_PER_STRATUM for name in banks)
    ]
    if not training_candidates:
        raise ValueError("Monitoring coverage is INCOMPLETE: no whole task group can remain for training")
    rng = random.Random(SEED)
    training_group = rng.choice(training_candidates)
    monitoring, used_groups = [], set()
    for name, _, _ in LENGTH_STRATA:
        candidates = sorted((row for row in banks[name] if row["group_id"] != training_group), key=lambda row: row["uid"])
        rng.shuffle(candidates)
        for _ in range(MONITOR_PER_STRATUM):
            index = next((i for i, row in enumerate(candidates) if row["group_id"] not in used_groups), 0)
            row = candidates.pop(index)
            monitoring.append(row)
            used_groups.add(row["group_id"])
    return monitoring


def _partition_population(population: list[dict], inherited_excluded_groups: set[str]) -> tuple[list[str], list[str], dict]:
    for row in population:
        if row["group_id"] in inherited_excluded_groups:
            row["exclusions"].append("inherited_evaluation_task_group")
        if row["prompt_token_count"] > PREFIX_TOKENS:
            row["exclusions"].append("qwen_prefix_over_budget")
        elif row["prompt_token_count"] <= 0:
            row["exclusions"].append("empty_qwen_prefix")
    eligible = [row for row in population if not row["exclusions"]]
    monitoring = _select_monitoring(eligible)
    monitor_uids = [row["uid"] for row in monitoring]
    monitor_groups = {row["group_id"] for row in monitoring}
    for row in population:
        if row["group_id"] in monitor_groups and row["uid"] not in monitor_uids:
            row["exclusions"].append("monitoring_task_group")
        row["split"] = "monitor" if row["uid"] in monitor_uids else "excluded" if row["exclusions"] else "train"
    training = [row for row in population if row["split"] == "train"]
    train_uids = [row["uid"] for row in training]
    train_groups = {row["group_id"] for row in training}
    checks = {
        "train_monitor_source_overlap": sorted(set(train_uids) & set(monitor_uids)),
        "train_monitor_group_overlap": sorted(train_groups & monitor_groups),
        "train_inherited_group_overlap": sorted(train_groups & inherited_excluded_groups),
        "monitor_inherited_group_overlap": sorted(monitor_groups & inherited_excluded_groups),
    }
    if any(checks.values()):
        raise ValueError(f"Frozen population isolation failed: {checks}")
    return train_uids, monitor_uids, {
        "training_uids": train_uids,
        "monitoring_uids": monitor_uids,
        "training_groups": sorted(train_groups),
        "monitoring_groups": sorted(monitor_groups),
        "monitoring_stratum_counts": dict(Counter(row["stratum"] for row in monitoring)),
        "eligible_stratum_counts": dict(Counter(row["stratum"] for row in eligible)),
        "monitoring_stratum_group_counts": {
            name: len({row["group_id"] for row in monitoring if row["stratum"] == name}) for name, _, _ in LENGTH_STRATA
        },
        "exclusion_counts": dict(Counter(reason for row in population for reason in row["exclusions"])),
        "checks": checks,
    }


def _tokenizer_identity(path: Path, tokenizer) -> dict:
    names = {"tokenizer.json", "tokenizer_config.json", "chat_template.jinja", "special_tokens_map.json"}
    return {
        "path": str(path),
        "class": type(tokenizer).__name__,
        "assets": {name: hashlib.sha256((path / name).read_bytes()).hexdigest() for name in sorted(names) if (path / name).is_file()},
    }


def _write_datasets(output_root: Path, rows: dict, training: list[str], monitoring: list[str]) -> dict:
    datasets = {}
    for name, uids in (("train", training), ("monitor", monitoring)):
        path = output_root / f"{name}.jsonl"
        digest = hashlib.sha256()
        with path.open("xb") as stream:
            for uid in uids:
                raw = (json.dumps(rows[uid], ensure_ascii=False, separators=(",", ":")) + "\n").encode()
                stream.write(raw)
                digest.update(raw)
        datasets[name] = {"path": str(path), "sha256": digest.hexdigest(), "rows": len(uids)}
    return datasets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--glm-tokenizer", type=Path, required=True)
    parser.add_argument("--qwen-tokenizer", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, default=Path("/mnt/codesign-exp/ycfeng"))
    parser.add_argument("--chat-template-path", type=Path)
    parser.add_argument("--apply-chat-template-kwargs", type=json.loads, default={})
    args = parser.parse_args()
    if not isinstance(args.apply_chat_template_kwargs, dict):
        parser.error("--apply-chat-template-kwargs must be a JSON object")
    if args.output_root.exists():
        raise FileExistsError(f"Use a new population directory: {args.output_root}")
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    references = _verify_manifest_references(manifest)
    inherited_excluded = _verify_population_membership(manifest, references)
    _verify_tokenizer_assets(args.glm_tokenizer, manifest["tokenizer"]["assets"])
    glm_tokenizer = AutoTokenizer.from_pretrained(args.glm_tokenizer, local_files_only=True)
    qwen_tokenizer = AutoTokenizer.from_pretrained(args.qwen_tokenizer, local_files_only=True)
    template_path, template, kwargs = _template_settings(args.chat_template_path, args.apply_chat_template_kwargs)
    rows, population = _prepare_population(manifest, glm_tokenizer, qwen_tokenizer, template, kwargs, args.source_root)
    report = {
        "status": "preparing",
        "python": platform.python_version(),
        "manifest": {"path": str(args.manifest), "sha256": hashlib.sha256(manifest_bytes).hexdigest()},
        "source_files": manifest["files"],
        "source_root": str(args.source_root),
        "source_validation": "Source size and every selected conversation SHA256 plus original GLM token hashes; whole-file hashes inherited",
        "training_exclusion": manifest["membership"],
        "parents": manifest["parents"],
        "isolation": manifest["isolation"],
        "group_membership_validation": "Verified pinned parent pool and selected_conversations membership",
        "glm_tokenizer": _tokenizer_identity(args.glm_tokenizer, glm_tokenizer),
        "qwen_tokenizer": _tokenizer_identity(args.qwen_tokenizer, qwen_tokenizer),
        "chat_template": {"path": str(template_path), "sha256": hashlib.sha256(template.encode()).hexdigest(), "kwargs": kwargs},
        "limits": {"context_tokens": CONTEXT_TOKENS, "response_tokens": RESPONSE_TOKENS, "prefix_tokens": PREFIX_TOKENS},
        "length_strata": [{"name": name, "lower_exclusive": lower, "upper_inclusive": upper} for name, lower, upper in LENGTH_STRATA],
        "monitoring_per_stratum": MONITOR_PER_STRATUM,
        "selection_seed": SEED,
        "selection_rule": "Seeded source-UID order; prefer unused monitoring task groups, permit repeated groups, retain at least one whole training group",
        "training_order": {"owner": "Miles Dataset.shuffle and native rollout cycling", "seed": SEED, "emitted_order": "manifest source order"},
        "historical_targets": "Provenance only; generate a fresh completion on every training/monitoring use",
        "population_count": len(population),
        "population": population,
    }
    try:
        training, monitoring, split = _partition_population(population, inherited_excluded)
    except ValueError as error:
        report.update(status="incomplete", error=str(error))
        args.output_root.mkdir(parents=True, exist_ok=False)
        (args.output_root / "population.json").write_text(json.dumps(report, indent=2) + "\n")
        raise
    args.output_root.mkdir(parents=True, exist_ok=False)
    report.update(status="passed", split=split, datasets=_write_datasets(args.output_root, rows, training, monitoring))
    (args.output_root / "population.json").write_text(json.dumps(report, indent=2) + "\n")
    print("QWEN35_POPULATION_PREPARED", len(training), len(monitoring), flush=True)


if __name__ == "__main__":
    main()
