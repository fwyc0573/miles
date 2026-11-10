"""Report S9 values from the shared inspector's receipt and queryable verified profile prefix.

Example (the training directory and terminal receipt must belong to the same attempt):
    python -m tests.manual.agent_opd.distillation_report --training-dir /path/to/A/training \
        --job exp-A --cell A/full --expected-updates 200 --terminal-path /path/to/A/terminal.json \
        --output-prefix /path/to/reports/A-profile

This module neither parses native/profile evidence nor computes model losses. Configuration and
historical ratios belong to DistillationProfile; native and profile completeness belong to the
shared inspector. Quantiles give each conversation equal weight and include only defined values.
"""

import argparse
import copy
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path

from tests.manual.agent_opd.distillation_profile import DistillationProfile

S9_MILESTONES = (1, 10, 50, 100, 150, 200)
QUANTILES = {"p10": 0.10, "p25": 0.25, "p50": 0.50, "p75": 0.75, "p90": 0.90}
QUANTILE_CONVENTION = (
    "Equal weight per conversation; exclude None, never replace it with zero. Sort the n defined "
    "values; for probability p use h=(n-1)*p and linearly interpolate between floor(h) and ceil(h). "
    "One defined value supplies every quantile; no defined values gives null quantiles."
)
INTERPRETATION_LIMITS = (
    "All metrics describe the verified profile prefix, not any later unverified native updates. "
    "Unavailable milestones remain null; they are never extrapolated or filled from partial records.",
    "RKL-best is the earliest minimum RKL, with NLL at that same update. NLL has no independent "
    "best, trend or recovery statistic.",
    "Conversation distributions use each conversation's own latest entry. These entries can have "
    "different measurement updates; trend uses the latest reference at least k updates earlier.",
    "Full-mode measurements mix training progress with turn position and actual turn/token membership. "
    "Later conversations measure their own baseline on a student trained longer.",
    "Remaining gap is an RKL-to-baseline ratio, not the fraction still reducible. Model size alone "
    "does not prove a strictly positive minimum RKL.",
    "Normalized gaps establish neither causal nor rank comparisons across teachers, models or runs. "
    "This report performs no benchmark evaluation.",
    "The report does not independently verify source SWE instance/repository identity, exact-text "
    "proxy coverage or seed count. Consult the attempt's source and configuration evidence.",
)


def quantile_summary(values: Sequence[float | None]) -> dict:
    """Summarize defined values using the documented (n-1)*p linear interpolation convention."""
    defined = sorted(value for value in values if value is not None)
    if any(not math.isfinite(value) for value in defined):
        raise ValueError("Quantile values must be finite or None")
    quantiles = {}
    for name, probability in QUANTILES.items():
        if not defined:
            quantiles[name] = None
            continue
        position = (len(defined) - 1) * probability
        lower, upper = math.floor(position), math.ceil(position)
        fraction = position - lower
        quantiles[name] = (1 - fraction) * defined[lower] + fraction * defined[upper]
    return {
        "defined_count": len(defined),
        "undefined_count": len(values) - len(defined),
        "quantiles": quantiles,
    }


def _baseline_status(profile: DistillationProfile | None) -> str:
    if profile is None:
        return "UNAVAILABLE"
    if profile.baseline is None:
        return "INCOMPLETE"
    return "POSITIVE" if profile.baseline > 0 else "NONPOSITIVE"


def _milestone(profile, update_id, *, verified_updates, observed_updates):
    if update_id > verified_updates:
        return {
            "update_id": update_id,
            "status": "UNVERIFIED" if update_id <= observed_updates else "NOT_OBSERVED",
            "rkl": None, "nll": None, "remaining_gap": None,
        }
    row = profile.update(update_id)
    return {
        "update_id": update_id, "status": "VERIFIED", "rkl": row.rkl, "nll": row.nll,
        # Query the now-fixed baseline, rather than the null persisted before it was complete.
        "remaining_gap": profile.remaining_gap(update_id),
    }


def _conversation_report(profile, summary, *, verified_updates):
    counts = {
        "seen": summary["conversations_seen"],
        "alive": summary["conversations_alive"],
        "positive_baseline": summary["conversations_with_baseline"],
        "nonpositive_baseline": summary["conversations_with_nonpositive_baseline"],
        "defined_trend": summary["conversations_with_trend"],
    } if summary is not None else {
        "seen": 0, "alive": 0, "positive_baseline": 0, "nonpositive_baseline": 0, "defined_trend": 0,
    }
    counts["incomplete_baseline"] = counts["seen"] - counts["positive_baseline"] - counts["nonpositive_baseline"]
    states = profile.conversation_states(profile.trend_window) if profile is not None else None
    return {
        "scope": "VERIFIED_PREFIX",
        "profile_available": profile is not None,
        "as_of_update": verified_updates,
        "counts": counts,
        "distributions": {
            name: quantile_summary(getattr(states, name) if states is not None else ())
            for name in ("remaining_gap", "run_relative_gap", "rkl_trend", "recovery_gap")
        },
    }


def build_report(
    receipt: Mapping,
    profile: DistillationProfile | None,
    *,
    cell: str,
    milestones: Sequence[int] = S9_MILESTONES,
    limitations: Sequence[str] = (),
) -> dict:
    """Pure report computation; the receipt is authoritative for native/profile dispositions.

    The profile must be the inspector's queryable, verified prefix, not failed runtime memory.
    Hand-built CPU fixtures should identify their synthetic job/cell and pass that limitation here;
    this function never promotes input numbers to formal results or recomputes inspection verdicts.
    """
    expected = receipt["expected_updates"]
    if type(expected) is not int or expected < 1:
        raise ValueError("Expected updates must be a positive integer")
    if any(type(update) is not int or update < 1 for update in milestones) or list(milestones) != sorted(set(milestones)):
        raise ValueError("Milestones must be strictly increasing positive integers")
    verified = receipt["profile"]["verified_updates"]
    if profile is None:
        if verified != 0:
            raise ValueError("A nonempty verified prefix requires the inspector's queryable profile")
    elif profile.unverified_from is not None or profile.latest_update != verified:
        raise ValueError("Profile must contain exactly the inspector's queryable verified prefix")

    summary = profile.summary() if profile is not None and verified else None
    configuration = {
        name: getattr(profile, name) if profile is not None else None
        for name in ("estimator", "baseline_updates", "baseline_turns", "trend_window")
    }
    native_complete, profile_complete = receipt["native"]["complete"], receipt["profile"]["complete"]
    return {
        "cell": cell,
        "inspection": copy.deepcopy(dict(receipt)),
        "disposition": {
            "native_training": "COMPLETE" if native_complete else "INCOMPLETE",
            "profile": "COMPLETE" if profile_complete else "INCOMPLETE / UNVERIFIED",
            "overall": "COMPLETE" if native_complete and profile_complete else "INCOMPLETE",
        },
        "configuration": configuration,
        "macro": {
            "as_of_update": verified,
            "baseline": {
                "value": profile.baseline if profile is not None else None,
                "status": _baseline_status(profile),
            },
            "latest": {name: summary[name] for name in (
                "update_id", "rkl", "nll", "tokens", "turns", "conversations", "remaining_gap",
            )} if summary is not None else None,
            "rkl_best": summary["rkl_best"] if summary is not None else None,
            "rkl_trend": summary["rkl_trend"] if summary is not None else None,
            "recovery_gap": summary["recovery_gap"] if summary is not None else None,
            "milestones": [
                _milestone(profile, update, verified_updates=verified,
                           observed_updates=receipt["native"]["observed_successful_updates"])
                for update in milestones
            ],
        },
        "conversations": _conversation_report(profile, summary, verified_updates=verified),
        "quantile_convention": QUANTILE_CONVENTION,
        "limitations": [*limitations, *INTERPRETATION_LIMITS],
    }


def _display(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, float):
        return format(value, ".8g")
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def render_markdown(report: Mapping) -> str:
    """Render a single cell without comparing it with another teacher or attempt."""
    receipt, macro = report["inspection"], report["macro"]
    native, profile = receipt["native"], receipt["profile"]
    config, conversations = report["configuration"], report["conversations"]
    lines = [
        f"# Distillation profile report: {_display(report['cell'])}", "",
        f"- Job: `{_display(receipt['job'])}`",
        f"- Expected successful updates: {receipt['expected_updates']}",
        f"- Report disposition: **{report['disposition']['overall']}**", "",
        "## Native training and profile verification", "",
        "| Evidence | Disposition | Progress / terminal evidence | Error |",
        "| --- | --- | --- | --- |",
        f"| Native training | {report['disposition']['native_training']} | "
        f"Observed successful updates: {native['observed_successful_updates']}; "
        f"verified native counter: {_display(native['successful_updates'])}; "
        f"terminal phase: {_display(native['terminal_phase'])} | {_display(native['error'])} |",
        f"| Profile | {report['disposition']['profile']} | Verified prefix: {profile['verified_updates']}; "
        f"first unverified update: {_display(profile['first_unverified_update'])}; "
        f"unverified ranges: {_display(json.dumps(profile['unverified_ranges']))} | {_display(profile['error'])} |",
        "", "## Inspected paths", "",
    ]
    lines.extend(f"- {name}: `{_display(path)}`" for name, path in receipt["paths"].items())
    lines.extend([
        "", "## Macro values", "",
        f"Scope: verified prefix through update {macro['as_of_update']}; not any later native updates.",
        f"Estimator: `{_display(config['estimator'])}`; baseline updates B={_display(config['baseline_updates'])}; "
        f"conversation baseline turns N={_display(config['baseline_turns'])}; default k={_display(config['trend_window'])}.",
        f"Macro baseline: {_display(macro['baseline']['value'])} ({macro['baseline']['status']}). "
        "A missing or nonpositive baseline leaves dependent ratios, trend and recovery null.", "",
        "| Update | Verification | RKL | Student NLL | Remaining gap |",
        "| --- | --- | --- | --- | --- |",
    ])
    lines.extend("| " + " | ".join(_display(row[name]) for name in (
        "update_id", "status", "rkl", "nll", "remaining_gap",
    )) + " |" for row in macro["milestones"])
    best = macro["rkl_best"]
    lines.extend([
        "", f"- RKL-best (earliest tie): {_display(json.dumps(best))}",
        f"- Latest verified values: {_display(json.dumps(macro['latest']))}",
        f"- Default-k RKL trend (positive means RKL decreased): {_display(macro['rkl_trend'])}",
        f"- Recovery gap: {_display(macro['recovery_gap'])}",
        "", "## Conversation statistics", "",
        f"Scope: each conversation's latest entry within the verified prefix through update "
        f"{conversations['as_of_update']}; profile available: {conversations['profile_available']}. "
        "These are not counts for unverified later training.", "",
    ])
    lines.extend(f"- {name}: {value}" for name, value in conversations["counts"].items())
    lines.extend([
        "", report["quantile_convention"], "",
        "| Quantity | Defined | Undefined | " + " | ".join(QUANTILES) + " |",
        "| --- | --- | --- | " + " | ".join("---" for _ in QUANTILES) + " |",
    ])
    for name, distribution in conversations["distributions"].items():
        values = [name, distribution["defined_count"], distribution["undefined_count"],
                  *distribution["quantiles"].values()]
        lines.append("| " + " | ".join(_display(value) for value in values) + " |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {_display(limitation)}" for limitation in report["limitations"])
    return "\n".join(lines) + "\n"


def write_report(report: Mapping, *, output_prefix: Path) -> tuple[Path, Path]:
    """Write new per-cell JSON and Markdown artifacts; never overwrite existing evidence."""
    json_path, markdown_path = Path(f"{output_prefix}.json"), Path(f"{output_prefix}.md")
    for path in (json_path, markdown_path):
        if path.exists():
            raise FileExistsError(f"Report output already exists: {path}; choose a new output prefix")
    serialized = json.dumps(report, indent=2, allow_nan=False) + "\n"
    markdown = render_markdown(report)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("x", encoding="utf-8") as stream:
        stream.write(serialized)
    with markdown_path.open("x", encoding="utf-8") as stream:
        stream.write(markdown)
    return json_path, markdown_path


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-dir", type=Path, required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--cell", required=True)
    parser.add_argument("--expected-updates", type=int, required=True)
    parser.add_argument("--terminal-path", type=Path)
    parser.add_argument("--output-prefix", type=Path, required=True)
    args = parser.parse_args(argv)
    # The shared inspector is needed only for CLI execution, not pure CPU reporting tests.
    from tests.manual.agent_opd.inspect_distillation_run import inspect_run

    receipt, profile = inspect_run(args.training_dir, job=args.job, expected_updates=args.expected_updates,
                                  terminal_path=args.terminal_path)
    report = build_report(receipt, profile, cell=args.cell)
    paths = write_report(report, output_prefix=args.output_prefix)
    print(json.dumps({"cell": args.cell, "disposition": report["disposition"],
                      "outputs": [str(path) for path in paths]}))


if __name__ == "__main__":
    main()
