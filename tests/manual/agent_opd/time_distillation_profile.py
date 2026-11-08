"""Time the Distillation profile on a synthetic run of interleaved banks.

Example:
    python -m tests.manual.agent_opd.time_distillation_profile --updates 200 --bank-turns 256 \
        --open-conversations 32 --block-turns 8 --min-turns 19 --max-turns 464 --max-tokens 4000 \
        --trend-window 10 --baseline-updates 10 --baseline-turns 8 \
        --seed 1234 --temporary-root /data/ycfeng/tmp/agent-opd-image/profile-timing \
        --output task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/profile-timing.json
"""

import argparse
import gc
import hashlib
import json
import random
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

from tests.manual.agent_opd.distillation_profile import (
    OBSERVATIONS_FILE, UPDATES_FILE, DistillationProfile, TurnSums,
)


def _turn_order(rng, *, open_conversations, block_turns, min_turns, max_turns):
    """Yield (group_id, t_id, remaining) in round-robin blocks over the open conversations."""
    # Real group_ids are file_sha256:source_item_index, so string sizes match a real run.
    file_sha256 = hashlib.sha256(b"synthetic source file").hexdigest()
    opened = 0

    def open_conversation():
        nonlocal opened
        opened += 1
        return [f"{file_sha256}:{opened - 1}", rng.randint(min_turns, max_turns), 0]

    slots = [open_conversation() for _ in range(open_conversations)]
    while True:
        for index, conversation in enumerate(slots):
            for _ in range(block_turns):
                conversation[2] += 1
                yield conversation[0], conversation[2], conversation[1] - conversation[2]
                if conversation[2] == conversation[1]:
                    slots[index] = open_conversation()
                    break


def _banks(args):
    rng = random.Random(args.seed)
    order = _turn_order(rng, open_conversations=args.open_conversations, block_turns=args.block_turns,
                        min_turns=args.min_turns, max_turns=args.max_turns)
    banks = []
    for _ in range(args.updates):
        drawn = [next(order) for _ in range(args.bank_turns)]
        bank_turns = {f"{group_id}:{2 * t_id}": (group_id, t_id) for group_id, t_id, _ in drawn}
        sums = []
        for uid in bank_turns:
            tokens = rng.randint(1, args.max_tokens)
            sums.append(TurnSums(uid, tokens * rng.uniform(0.0, 1.0), tokens * rng.uniform(0.0, 2.0), tokens))
        banks.append((sums, bank_turns, [group_id for group_id, _, remaining in drawn if remaining == 0]))
    return banks


def _stats(seconds):
    milliseconds = sorted(x * 1000 for x in seconds)
    return {"mean_ms": statistics.fmean(milliseconds), "median_ms": statistics.median(milliseconds),
            "p95_ms": milliseconds[int(0.95 * (len(milliseconds) - 1))], "max_ms": milliseconds[-1],
            "total_s": sum(seconds)}


def main():
    parser = argparse.ArgumentParser()
    for name in ("updates", "bank-turns", "open-conversations", "block-turns", "min-turns", "max-turns",
                 "max-tokens", "trend-window", "baseline-updates", "baseline-turns", "seed"):
        parser.add_argument(f"--{name}", type=int, required=True)
    parser.add_argument("--temporary-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    banks = _banks(args)
    directory = args.temporary_root / "distillation_profile"
    if directory.exists():
        raise SystemExit(f"{directory} already exists; choose an empty temporary root")

    profile = DistillationProfile(estimator="sampled_token", trend_window=args.trend_window,
                                  baseline_updates=args.baseline_updates, baseline_turns=args.baseline_turns,
                                  directory=directory)
    record_seconds, states_seconds = [], []
    for update_id, (sums, bank_turns, finished) in enumerate(banks, start=1):
        started = time.perf_counter()
        profile.record_update(update_id, sums, bank_turns, finished)
        record_seconds.append(time.perf_counter() - started)
        started = time.perf_counter()
        profile.conversation_states(args.trend_window)
        states_seconds.append(time.perf_counter() - started)
    started = time.perf_counter()
    rebuilt = DistillationProfile.rebuild(directory)
    rebuild_seconds = time.perf_counter() - started

    # Build the inputs inside the traced window, then drop them: what stays is the profile's own memory,
    # including the uid and group_id strings it keeps.
    del banks
    gc.collect()
    tracemalloc.start()
    in_memory = DistillationProfile(estimator="sampled_token", trend_window=args.trend_window,
                                    baseline_updates=args.baseline_updates,
                                    baseline_turns=args.baseline_turns, directory=None)
    for update_id, (sums, bank_turns, finished) in enumerate(_banks(args), start=1):
        in_memory.record_update(update_id, sums, bank_turns, finished)
    del sums, bank_turns, finished
    gc.collect()
    memory_bytes = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()

    states = profile.conversation_states(args.trend_window)
    summary = profile.summary()
    report = {
        "status": "PASS" if profile.unverified_from is None and rebuilt.summary() == summary else "FAIL",
        "python": sys.version.split()[0], "argv": sys.argv, "updates": profile.latest_update,
        "observations": sum(profile.update(u).turns for u in range(1, profile.latest_update + 1)),
        "conversations": profile.conversation_count, "conversations_alive": sum(states.alive),
        "conversations_with_trend": sum(t is not None for t in states.rkl_trend),
        "baseline": profile.baseline, "remaining_gap": profile.remaining_gap(profile.latest_update),
        "conversations_with_baseline": summary["conversations_with_baseline"],
        "conversations_with_nonpositive_baseline": summary["conversations_with_nonpositive_baseline"],
        "record_update_per_update": _stats(record_seconds),
        "conversation_states_per_query": _stats(states_seconds),
        "rebuild_seconds": rebuild_seconds,
        "profile_memory_mb": memory_bytes / 2**20,
        "file_bytes": {name: (directory / name).stat().st_size for name in (UPDATES_FILE, OBSERVATIONS_FILE)},
        "unverified_from": profile.unverified_from,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ("status", "updates", "observations", "conversations")}))


if __name__ == "__main__":
    main()
