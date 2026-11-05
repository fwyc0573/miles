"""Summarize two complete twenty-question, four-seed native SWE benchmarks.

Missing or invalid attempts never become model failures. The paired interval
resamples questions, retaining all four attempts for each selected question.
"""

import argparse
import json
import random
from pathlib import Path


def _read_model(roots: Path | list[Path], membership: dict, version: int) -> dict:
    if isinstance(roots, Path):
        roots = [roots]
    attempts = {}
    missing = []
    for task in membership["task_ids"]:
        for seed in membership["seeds"]:
            valid = []
            errors = []
            for root in roots:
                directory = root / f"step{version}" / f"seed-{seed}" / "outcomes"
                generation = directory / f"{task}.generation.json"
                grading = directory / f"{task}.grading.json"
                if not generation.exists() and not grading.exists():
                    continue
                try:
                    generated, graded = json.loads(generation.read_text()), json.loads(grading.read_text())
                    for row in (generated, graded):
                        if (row["task_id"], row["seed"], row["completed_updates"]) != (task, seed, version):
                            raise ValueError("Native attempt identity differs")
                    if generated.get("seed_verified") is not True:
                        raise ValueError("Actual inference seed/sampling is unverified")
                    if graded["status"] not in ("resolved", "unresolved") or type(graded.get("resolved")) is not bool:
                        raise ValueError("Native grader did not return a valid model outcome")
                    if graded["resolved"] != (graded["status"] == "resolved"):
                        raise ValueError("Native grader status and score disagree")
                    valid.append(int(graded["resolved"]))
                except (OSError, ValueError, KeyError, TypeError) as error:
                    errors.append({"error_type": type(error).__name__, "reason": str(error)})
            if len(valid) > 1:
                raise ValueError(f"Duplicate valid benchmark attempt: step{version}/{task}/seed{seed}")
            if valid:
                attempts[(task, seed)] = valid[0]
            else:
                missing.append({"task_id": task, "seed": seed, "errors": errors})
    expected = len(membership["task_ids"]) * len(membership["seeds"])
    complete = len(attempts) == expected
    return {
        "completed_updates": version,
        "valid_attempts": len(attempts),
        "expected_attempts": expected,
        "resolved_attempts": sum(attempts.values()),
        "missing_attempts": missing,
        "avg_at_4": sum(attempts.values()) / expected if complete else None,
        "per_question": {
            task: sum(attempts[(task, seed)] for seed in membership["seeds"]) / len(membership["seeds"])
            for task in membership["task_ids"]
            if all((task, seed) in attempts for seed in membership["seeds"])
        },
    }


def summarize(original: Path, updated: Path, membership: dict, *, bootstrap_samples: int, bootstrap_seed: int) -> dict:
    if len(membership["task_ids"]) != 20 or len(set(membership["task_ids"])) != 20 or len(membership["seeds"]) != 4:
        raise ValueError("This test requires twenty unique questions and four seeds")
    before, after = _read_model(original, membership, 0), _read_model(updated, membership, 20)
    result = {
        "models": [before, after],
        "avg_at_4_definition": "Mean of the four binary grader outcomes, averaged over twenty questions",
        "difference": None,
        "paired_question_differences": None,
        "paired_bootstrap_95_percent": None,
    }
    if before["avg_at_4"] is None or after["avg_at_4"] is None:
        result["status"] = "incomplete"
        return result
    differences = {task: after["per_question"][task] - before["per_question"][task] for task in membership["task_ids"]}
    values = list(differences.values())
    rng = random.Random(bootstrap_seed)
    boot = sorted(sum(rng.choices(values, k=len(values))) / len(values) for _ in range(bootstrap_samples))
    result.update(
        status="complete",
        difference=after["avg_at_4"] - before["avg_at_4"],
        paired_question_differences=differences,
        paired_bootstrap_95_percent=[boot[int(0.025 * bootstrap_samples)], boot[int(0.975 * bootstrap_samples)]],
        bootstrap_samples=bootstrap_samples,
        bootstrap_seed=bootstrap_seed,
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", nargs="+", type=Path, required=True)
    parser.add_argument("--updated", nargs="+", type=Path, required=True)
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20261105)
    args = parser.parse_args()
    for path in [*args.original, *args.updated, args.membership]:
        path.relative_to("/mnt/codesign-exp/ycfeng")
    result = summarize(
        args.original,
        args.updated,
        json.loads(args.membership.read_text()),
        bootstrap_samples=args.bootstrap_samples,
        bootstrap_seed=args.bootstrap_seed,
    )
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print("AGENT_OPD_BENCHMARK_SUMMARY", json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
