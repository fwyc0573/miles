"""Prepare the shortest complete training turn in each pinned ticket07 category.

Only the selected JSON byte ranges are read. The original conversation hash,
GLM prompt hash and completion hash must match before a training row is written.
Historical completion tokens are recorded for replay but are not training tokens
in the OPD warmup: the student generates its own continuation.
"""

import argparse
import copy
import hashlib
import json
import platform
from pathlib import Path

from examples.agentic_opd.glm_turns import encode_glm_turn, token_hash
from transformers import AutoTokenizer


def _read_conversation(file: dict, row: dict) -> list[dict]:
    path = Path(file["path"])
    path.relative_to("/mnt/codesign-exp/ycfeng")
    if path.stat().st_size != file["size"]:
        raise ValueError(f"The selected glm5.2 source file changed size: {path}")
    with path.open("rb") as stream:
        stream.seek(row["item_start"])
        raw = stream.read(row["item_end"] - row["item_start"])
    if hashlib.sha256(raw).hexdigest() != row["conversation_sha256"]:
        raise ValueError("The selected original glm5.2 conversation bytes changed")
    return json.loads(raw)


def _make_row(tokenizer, conversation: list[dict], file: dict, row: dict, category: str) -> tuple[dict, dict]:
    messages = conversation[: row["assistant_turn_index"] + 1]
    tools = messages[0].get("tools")
    turn = encode_glm_turn(tokenizer, messages, tools)
    for field, tokens in (("prompt", turn.prompt_ids), ("completion", turn.completion_ids)):
        if len(tokens) != row[f"{field}_token_count"] or token_hash(tokens) != row[f"{field}_sha256"]:
            raise ValueError(f"The selected GLM {field} differs from ticket07")
    target = copy.deepcopy(messages[-1])
    source = {
        "path": file["path"],
        "file_sha256": file["sha256"],
        **row,
        "category": category,
        "uid": f"{file['sha256']}:{row['source_item_index']}:{row['assistant_turn_index']}",
    }
    original = {
        "message": target,
        "token_ids": turn.completion_ids,
        "raw_text": turn.completion_text,
        "has_thinking": bool(target.get("reasoning_content")),
        "has_body": bool(target.get("content")),
        "tool_names": [(call.get("function") or call)["name"] for call in target.get("tool_calls") or []],
        "sampling_logprobs": None,
    }
    dataset_row = {
        "prompt": turn.prompt,
        "metadata": {
            "source": source,
            "history": messages[:-1],
            "tools": tools,
            "original_completion": original,
        },
    }
    evidence = {
        "category": category,
        "source_uid": source["uid"],
        "prompt_tokens": len(turn.prompt_ids),
        "completion_tokens": len(turn.completion_ids),
        "prompt_sha256": row["prompt_sha256"],
        "completion_sha256": row["completion_sha256"],
        "has_thinking": original["has_thinking"],
        "has_body": original["has_body"],
        "tool_names": original["tool_names"],
        "history_reasoning_count": sum(bool(message.get("reasoning_content")) for message in messages[:-1]),
        "generation_boundary": "role_only",
        "source_unmodified": True,
        "prefix_and_completion_match": True,
    }
    return dataset_row, evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    selected = {
        category: min(
            bank["train"],
            key=lambda row: (row["prompt_token_count"], row["source_item_index"], row["assistant_turn_index"]),
        )
        for category, bank in manifest["categories"].items()
    }
    for name, expected in manifest["tokenizer"]["assets"].items():
        if hashlib.sha256((args.tokenizer / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Pinned GLM tokenizer asset changed: {name}")
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True)
    rows, evidence = [], []
    for category, row in selected.items():
        file = manifest["files"][row["file"]]
        conversation = _read_conversation(file, row)
        dataset_row, check = _make_row(tokenizer, conversation, file, row, category)
        rows.append(dataset_row)
        evidence.append(check)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(
            {
                "status": "passed",
                "python": platform.python_version(),
                "tokenizer_class": type(tokenizer).__name__,
                "parent_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "dataset": str(args.output),
                "historical_sampling_probabilities": "unavailable; no probability fabricated",
                "turns": evidence,
            },
            indent=2,
        )
        + "\n"
    )
    print("GLM5_2_DATASET_PREPARED", len(rows), flush=True)


if __name__ == "__main__":
    main()
