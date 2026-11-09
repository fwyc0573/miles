"""Run the pinned native audits against the configured in-place SWE sources.

This CPU preparation publishes genuine native baseline, visual and exclusion
receipts. It does not copy source data or measure Qwen prompt lengths.
"""

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
import sys
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-repo", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, required=True)
    parser.add_argument("--max-prompt-length", type=int, required=True)
    args = parser.parse_args()
    manifest_bytes = args.source_manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest["status"] != "COMPLETE" or manifest["read_in_place"] is not True:
        raise ValueError("The source manifest must describe a completed in-place audit")
    paths = [item["path"] for item in manifest["files"]]
    for item in manifest["files"]:
        stat = Path(item["path"]).stat()
        if (stat.st_size, stat.st_mtime_ns) != (item["bytes"], item["mtime_ns"]):
            raise ValueError(f"Source metadata differs from its accepted audit: {item['path']}")

    sys.path.insert(0, str(args.native_repo.resolve()))
    modules = {
        name: importlib.import_module(f"playground.users.cj.opd.s4_swe_{name}_1001")
        for name in ("data_audit", "visual_audit", "visual_filter", "source_manifest")
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    baseline = args.output_dir / "baseline.json"
    visual = args.output_dir / "visual.json"
    filtered = args.output_dir / "filter.json"
    started = time.monotonic()
    modules["data_audit"].audit_sources(
        data_files=paths,
        output_path=str(baseline),
        workers=args.workers,
        tokenizer_dir=str(args.native_repo / modules["source_manifest"].TOKENIZER_PATH),
        max_prompt_length=args.max_prompt_length,
    )
    modules["visual_audit"].audit_sources(
        data_files=paths,
        output_path=str(visual),
        baseline_audit_path=str(baseline),
        workers=args.workers,
    )
    modules["visual_filter"].filter_sources(
        data_files=paths,
        output_path=str(filtered),
        baseline_audit_path=str(baseline),
        visual_audit_path=str(visual),
        workers=args.workers,
    )
    for receipt in (baseline, visual, filtered):
        receipt.chmod(0o644)
    filter_result = json.loads(filtered.read_text())
    if not filter_result["complete"]:
        raise RuntimeError(f"Native visual filter is incomplete: {filter_result['failure_codes']}")
    result = {
        "job": os.environ.get("KUBEBRAIN_RJOB_NAME"),
        "python": sys.version,
        "versions": {name: importlib.metadata.version(name) for name in ("transformers", "ijson", "loguru")},
        "source_manifest": str(args.source_manifest),
        "source_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "native_modules": {
            name: {"path": module.__file__, "sha256": hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()}
            for name, module in modules.items()
        },
        "workers": args.workers,
        "elapsed_seconds": time.monotonic() - started,
        "filter_receipt": str(filtered),
        "totals": filter_result["totals"],
    }
    with (args.output_dir / "runtime.json").open("x") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    print("SWE_NATIVE_VISUAL_FILTER_COMPLETE", str(filtered), flush=True)


if __name__ == "__main__":
    main()
