"""Freeze twenty questions from the referenced Ticket06 fixed SWE bank."""

import argparse
import hashlib
import json
import random
from pathlib import Path


def _read_verified(path: Path, digest: str):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError(f"Pinned benchmark input changed: {path}")
    return json.loads(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    args.output_root.relative_to("/mnt/codesign-exp/ycfeng")
    parent_raw = args.parent.read_bytes()
    parent = json.loads(parent_raw)
    benchmark = parent["benchmark"]
    Path(benchmark["path"]).relative_to("/mnt/codesign-exp/ycfeng")
    rows = _read_verified(Path(benchmark["path"]), benchmark["sha256"])
    exclusion = parent["training_exclusion"]
    excluded = _read_verified(Path(exclusion["path"]), exclusion["sha256"])
    if len(parent["task_ids"]) != 50 or len(excluded["task_ids"]) != 175:
        raise ValueError("Expected the Ticket06 fixed50/fixed175 memberships")
    records = {row["instance_id"]: row for row in rows}
    rng = random.Random(1234)
    selected = set()
    for repository, count in (("astropy/astropy", 2), ("django/django", 18)):
        candidates = [task for task in parent["task_ids"] if records[task]["repo"] == repository]
        selected.update(rng.sample(candidates, count))
    task_ids = [task for task in parent["task_ids"] if task in selected]
    if len(task_ids) != 20 or not selected <= set(excluded["task_ids"]):
        raise ValueError("Selected questions must belong to the held-out membership")
    args.output_root.mkdir(parents=True, exist_ok=False)
    dataset = args.output_root / "questions.json"
    dataset.write_text(json.dumps([records[task] for task in task_ids], ensure_ascii=False) + "\n")
    manifest = {
        "task_ids": task_ids,
        "seeds": parent["seeds"],
        "sampling": parent["sampling"],
        "dataset": str(dataset),
        "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "parent_sha256": hashlib.sha256(parent_raw).hexdigest(),
        "training_exclusion": exclusion,
        "selection_seed": 1234,
        "repository_counts": {"astropy/astropy": 2, "django/django": 18},
        "avg_at_4_denominator": 80,
        "selection_rule": "Repository-stratified random selection from fixed50, emitted in parent order; no model outcomes read",
    }
    (args.output_root / "membership.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("AGENT_OPD_BENCHMARK_FROZEN", json.dumps(manifest), flush=True)


if __name__ == "__main__":
    main()
