"""Summarize two complete twenty-question, four-seed native SWE benchmarks.

Unknown or infrastructure-invalid attempts remain missing. A separately
diagnosed model-caused timeout can be scored without changing its native grading
receipt. The paired interval resamples questions and retains all four attempts.
"""

import argparse
import hashlib
import json
import random
from pathlib import Path


def read_model_failure(generation: Path, grading: Path) -> dict | None:
    """Read a causal diagnosis bound to unchanged native attempt receipts."""
    path = generation.with_name(generation.name.replace(".generation.json", ".model_failure.json"))
    if not path.is_file():
        return None
    diagnosis = json.loads(path.read_text())
    generated, graded = json.loads(generation.read_text()), json.loads(grading.read_text())
    identity = tuple(generated[key] for key in ("task_id", "seed", "completed_updates"))
    if identity != tuple(diagnosis[key] for key in ("task_id", "seed", "completed_updates")):
        raise ValueError("Model-failure diagnosis belongs to a different attempt")
    if (
        diagnosis["status"] != "confirmed_model_failure"
        or diagnosis["failure_type"] != "grading_timeout"
        or diagnosis["generation_reran"] is not False
        or diagnosis["source_job"] != generation.parents[3].name
        or not diagnosis["source_uid"]
        or generated["status"] != "returned"
        or generated.get("seed_verified") is not True
        or graded["status"] != "invalid"
        or graded.get("resolved") is not None
    ):
        raise ValueError("Native attempt does not support the model-failure diagnosis")
    for file, key in ((generation, "generation_sha256"), (grading, "grading_sha256")):
        if hashlib.sha256(file.read_bytes()).hexdigest() != diagnosis[key]:
            raise ValueError("Original native receipt changed after model-failure diagnosis")
    control = diagnosis["baseline_control"]
    differential = diagnosis["native_differential"]
    checks = diagnosis["native_checks"]
    if (
        control["status"] != "passed"
        or control["native_status"] not in ("resolved", "unresolved")
        or control["generation_reran"] is not False
        or control["original_generation_sha256"] != diagnosis["generation_sha256"]
        or control["original_trajectory_sha256"] != diagnosis["trajectory_sha256"]
        or control["source_job"] != diagnosis["source_job"]
        or control["source_uid"] != diagnosis["source_uid"]
        or (control["task_id"], control["seed"]) != identity[:2]
        or not control["tests_status_counts"]
        or not control["tests_status_allcases_count"]
        or control["native_time_consumed"] >= diagnosis["native_timeout_seconds"]
        or differential["status"] != "passed"
        or differential["patch_sha256"] != diagnosis["patch_sha256"]
        or "/envs/testbed/" not in differential["executable"]
        or len(checks) < 2
        or any(
            check["status"] != "timeout" or check["timeout_seconds"] != diagnosis["native_timeout_seconds"]
            for check in checks
        )
    ):
        raise ValueError("Native causal evidence does not confirm a model-caused timeout")
    original = [row for row in differential["results"] if row["regex"] == "original"]
    submitted = [row for row in differential["results"] if row["regex"] == "submitted_patch"]
    if (
        not original
        or {row["test_patch_url_index"] for row in original} != {row["test_patch_url_index"] for row in submitted}
        or any(row["status"] != "returned" for row in original)
        or any(row["status"] != "timeout" for row in submitted)
    ):
        raise ValueError("Same-interpreter control and submitted patch do not establish the regression")
    return diagnosis


def _read_model(roots: Path | list[Path], membership: dict, version: int) -> dict:
    if isinstance(roots, Path):
        roots = [roots]
    attempts = {}
    missing = []
    model_failures = []
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
                    diagnosis = read_model_failure(generation, grading)
                    if diagnosis is not None:
                        valid.append(
                            (
                                0,
                                {
                                    key: diagnosis[key]
                                    for key in (
                                        "source_job",
                                        "source_uid",
                                        "task_id",
                                        "seed",
                                        "completed_updates",
                                        "failure_type",
                                    )
                                },
                            )
                        )
                        continue
                    if graded["status"] not in ("resolved", "unresolved") or type(graded.get("resolved")) is not bool:
                        raise ValueError("Native grader did not return a valid model outcome")
                    if graded["resolved"] != (graded["status"] == "resolved"):
                        raise ValueError("Native grader status and score disagree")
                    valid.append((int(graded["resolved"]), None))
                except (OSError, ValueError, KeyError, TypeError) as error:
                    errors.append({"error_type": type(error).__name__, "reason": str(error)})
            if len(valid) > 1:
                raise ValueError(f"Duplicate valid benchmark attempt: step{version}/{task}/seed{seed}")
            if valid:
                attempts[(task, seed)] = valid[0][0]
                if valid[0][1] is not None:
                    model_failures.append(valid[0][1])
            else:
                missing.append({"task_id": task, "seed": seed, "errors": errors})
    expected = len(membership["task_ids"]) * len(membership["seeds"])
    complete = len(attempts) == expected
    return {
        "completed_updates": version,
        "valid_attempts": len(attempts),
        "native_valid_attempts": len(attempts) - len(model_failures),
        "confirmed_model_failures": model_failures,
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
        "avg_at_4_definition": "Mean of four binary outcomes per question over twenty questions; confirmed model-caused timeouts count as failures and unknown errors remain missing",
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
