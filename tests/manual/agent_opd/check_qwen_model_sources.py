"""Revalidate selected model sources against an existing Qwen asset receipt.

This CPU inspection reads metadata and shard sizes, not complete weight bytes.
Run where the approved model volumes and local repository are mounted:

    python -m tests.manual.agent_opd.check_qwen_model_sources \
        --assets-receipt "$ASSETS" --model Qwen3.5-4B --model Qwen3.5-27B \
        --model Qwen3.5-35B-A3B --report "$REPORT"
"""

import argparse
import hashlib
import json
import os
import platform
from datetime import datetime, timezone
from pathlib import Path

from tests.manual.agent_opd.inspect_qwen35_assets import _model_metadata


def check_sources(assets: dict, names: list[str]) -> tuple[dict, list[str]]:
    observed, errors = {}, []
    for name in names:
        source = Path(assets["model_sources"][name])
        expected = assets["models"][name]
        if len(expected) != 1 or expected[0]["path"] != str(source):
            raise ValueError(f"Expected one explicitly identified source for {name}")
        actual = _model_metadata(source, (source,))
        observed[name] = actual
        if not actual["config_exists"] or not actual["index_exists"]:
            errors.append(f"{name}: missing config or index")
            continue
        for field in ("metadata_sha256", "shards", "tensor_count", "all_indexed_shards_exist"):
            if actual[field] != expected[0][field]:
                errors.append(f"{name}: {field} differs from the qualified source receipt")
        if not actual["all_indexed_shards_exist"]:
            errors.append(f"{name}: indexed weight shards are missing")
    if not errors:
        for filename in ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja"):
            digests = {row["metadata_sha256"][filename] for row in observed.values()}
            if len(digests) != 1 or None in digests:
                errors.append(f"Selected models do not share the same {filename}")
    return observed, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets-receipt", type=Path, required=True)
    parser.add_argument("--model", action="append", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    raw = args.assets_receipt.read_bytes()
    observed, errors = check_sources(json.loads(raw), args.model)
    report = {
        "status": "failed" if errors else "verified",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "job": os.environ.get("KUBEBRAIN_RJOB_NAME"),
        "host": platform.node(),
        "python": platform.python_version(),
        "assets_receipt": {"path": str(args.assets_receipt), "sha256": hashlib.sha256(raw).hexdigest()},
        "models": observed,
        "errors": errors,
        "verification_limit": "Metadata hashes and indexed shard sizes; no full weight hash or model execution.",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "job": report["job"], "report": str(args.report), "errors": errors}))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
