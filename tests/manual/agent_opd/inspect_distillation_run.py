"""Read-only inspection of one full-mode attempt's native ACKs and retained profile.

Only a paired prefix with native counts, canonical bank UIDs/masks and reproducible
profile summaries is queryable. A bad update never exposes its partly applied state.
This is an offline receipt writer, not a training gate; incomplete inspection exits
normally and cannot control a worker. Run with ``python -m`` from the repository:

    python -m tests.manual.agent_opd.inspect_distillation_run \
        --training-dir /path/to/attempt --job exp-id --expected-updates 200 \
        --terminal /path/to/terminal.json --output /path/to/inspection.json
"""

import argparse
import json
import math
import tempfile
from pathlib import Path

from tests.manual.agent_opd.distillation_profile import (
    OBSERVATIONS_FILE,
    UPDATES_FILE,
    DistillationProfile,
    TurnSums,
)


def _jsonl_rows(path: Path, limit: int):
    """Read complete lines only, with a bound on the retained record count."""
    with path.open("rb") as stream:
        for number in range(1, limit + 2):
            line = stream.readline()
            if not line:
                return
            if number > limit:
                raise ValueError(f"{path}: more than {limit} records; inspection bound exceeded")
            if not line.endswith(b"\n"):
                raise ValueError(f"{path}: partial line {number}; no terminating newline")
            try:
                row = json.loads(line)
            except (ValueError, UnicodeError) as error:
                raise ValueError(f"{path}: invalid JSON at line {number}: {error}") from error
            if not isinstance(row, dict):
                raise ValueError(f"{path}: line {number} is not an object")
            yield row


def _read_rows(path: Path, limit: int) -> tuple[list[dict], str | None]:
    rows = []
    try:
        rows.extend(_jsonl_rows(path, limit))
    except (OSError, ValueError) as error:
        return rows, f"{type(error).__name__}: {error}"
    return rows, None


def _terminal(path: Path | None, job: str) -> tuple[dict | None, str | None]:
    if path is None:
        return None, "No terminal receipt supplied; native completion is unverified"
    try:
        row = json.loads(path.read_bytes())
        if row["job"] != job:
            raise ValueError(f"Terminal job {row['job']!r} differs from requested {job!r}")
        if not isinstance(row["status"]["phase"], str):
            raise ValueError("Terminal status.phase is not a string")
        return row, None
    except (OSError, ValueError, KeyError, TypeError) as error:
        return None, f"{type(error).__name__}: {error}"


def _native_prefix(rows: list[dict], job: str) -> tuple[list[dict], str | None]:
    """Successful update IDs are dense; attempted IDs include skipped ACKs."""
    prefix = []
    identity = None
    previous_attempt = 0
    for update_id, row in enumerate(rows, 1):
        try:
            for name, value in (("update", update_id), ("successful_updates", update_id),
                                ("bank", update_id - 1), ("bank_visit", 1)):
                if type(row[name]) is not int or row[name] != value:
                    raise ValueError(f"Native {name}={row[name]!r}; expected {value}")
            if row["update_successful"] is not True:
                raise ValueError("updates.jsonl contains an unsuccessful ACK")
            attempted, skipped, rollout = (row[name] for name in
                                            ("native_attempted_count", "native_skipped_count", "attempted_rollout_id"))
            if any(type(value) is not int for value in (attempted, skipped, rollout)):
                raise ValueError("Native attempted/skipped/rollout counters must be integers")
            if attempted <= previous_attempt or skipped != attempted - update_id or skipped < 0 or rollout != attempted - 1:
                raise ValueError("Native attempted/skipped counters disagree with successful ACK sequence")
            current = tuple(row[name] for name in ("cell", "attempt", "protocol", "teacher_identity", "run_kind"))
            if any(not isinstance(value, str) or not value for value in current) or row["protocol"] != "full":
                raise ValueError("Native full-mode attempt identity is missing or invalid")
            if row["attempt"] != job:
                raise ValueError(f"Native attempt {row['attempt']!r} differs from requested job {job!r}")
            if identity is not None and current != identity:
                raise ValueError("Native ACKs cross attempt/cell/protocol/teacher/run-kind identity")
            identity, previous_attempt = current, attempted
            prefix.append(row)
        except (ValueError, KeyError, TypeError) as error:
            return prefix, f"Native update {update_id}: {type(error).__name__}: {error}"
    return prefix, None


def _canonical_bank(path: Path) -> tuple[dict, dict]:
    """Extract source identity and mask counts without retaining large token payloads."""
    slots, completed, sealed = None, {}, None
    # The first native record declares the candidate slots and therefore the bound.
    with path.open("rb") as stream:
        first = stream.readline()
    if not first.endswith(b"\n"):
        raise ValueError(f"{path}: missing complete acquisition_start")
    start = json.loads(first)
    if start["event"] != "acquisition_start":
        raise ValueError(f"{path}: first record is not acquisition_start")
    entries = start["slots"]
    slots = {entry["slot"]: entry["source_uid"] for entry in entries}
    if not slots or len(slots) != len(entries) or any(type(slot) is not int or slot < 0 for slot in slots):
        raise ValueError(f"{path}: invalid or duplicate candidate slots")
    if set(slots) != set(range(len(slots))) or len(set(slots.values())) != len(slots):
        raise ValueError(f"{path}: noncanonical slots or duplicate source UIDs")
    ended_slots = set()
    for index, row in enumerate(_jsonl_rows(path, len(slots) + 2)):
        if index == 0:
            if row != start:
                raise ValueError(f"{path}: acquisition_start changed during inspection")
            continue
        if sealed is not None:
            raise ValueError(f"{path}: records follow acquisition_sealed")
        if row["event"] == "acquisition_sealed":
            sealed = row
            continue
        if row["event"] != "slot_finished":
            raise ValueError(f"{path}: bank did not seal successfully")
        slot = row["slot"]
        if type(slot) is not int or slot not in slots or slot in ended_slots or row["source_uid"] != slots[slot]:
            raise ValueError(f"{path}: duplicate or mismatching finished slot/UID")
        ended_slots.add(slot)
        if row["status"] == "invalid":
            continue
        if row["status"] != "completed" or row["error"] is not None:
            raise ValueError(f"{path}: invalid slot status")
        sample = row["sample"]
        source = sample["metadata"]["source"]
        if source["uid"] != slots[slot]:
            raise ValueError(f"{path}: sample UID differs from canonical slot UID")
        mask = sample["loss_mask"]
        if not isinstance(mask, list) or len(mask) != sample["response_length"] or not mask:
            raise ValueError(f"{path}: canonical original mask/response lengths disagree")
        if any(type(value) is not int or value not in (0, 1) for value in mask) or not any(mask):
            raise ValueError(f"{path}: canonical original mask is not nonempty binary targets")
        completed[slot] = (source["uid"], source["group_id"], source["assistant_turn_ordinal"], sum(mask))
    if sealed is None:
        raise ValueError(f"{path}: no acquisition_sealed membership retained")
    membership = sealed["membership"]
    if (membership != sorted(completed) or any(type(slot) is not int for slot in membership)
            or type(sealed["actual_turns"]) is not int or sealed["actual_turns"] != len(completed)
            or sealed["missing_slots"] != sorted(set(slots) - completed.keys())):
        raise ValueError(f"{path}: sealed membership differs from canonical completed slots")
    bank = {uid: (source_conversation_id, turn)
            for uid, source_conversation_id, turn, _ in (completed[slot] for slot in membership)}
    counts = {uid: tokens for uid, _, _, tokens in (completed[slot] for slot in membership)}
    return bank, counts


def _verify_update(profile: DistillationProfile, native: dict, summary: dict, observations: dict,
                   bank: dict, counts: dict) -> None:
    update_id = native["successful_updates"]
    if any(type(row["update_id"]) is not int or row["update_id"] != update_id for row in (summary, observations)):
        raise ValueError("Paired profile update IDs do not match the native successful ACK")
    rows = observations["rows"]
    if any(type(value) is not int for row in rows for value in row[1:4]):
        raise ValueError("Profile conversation/turn/replay identities must be integers")
    sums = [TurnSums(uid, rkl, nll, tokens) for uid, _, _, _, rkl, nll, tokens in rows]
    old_count = profile.conversation_count
    source_conversation_ids = [profile.conversation(c_id).group_id for c_id in range(old_count)]
    for c_id, source_conversation_id in observations["new_conversations"]:
        if (type(c_id) is not int or c_id != len(source_conversation_ids)
                or source_conversation_id in source_conversation_ids):
            raise ValueError("Invalid new conversation mapping")
        source_conversation_ids.append(source_conversation_id)
    finished = observations["finished"]
    if any(type(c_id) is not int or not 0 <= c_id < len(source_conversation_ids) for c_id in finished):
        raise ValueError("Invalid finished conversation identity")
    offset = sum(profile.update(u).turns for u in range(1, profile.latest_update + 1))
    profile.record_update(update_id, sums, bank, [source_conversation_ids[c_id] for c_id in finished],
                          native_record=native, bank_token_counts=counts)
    if profile.unverified_from is not None:
        raise ValueError(profile.unverified_reason)
    expected_rows = []
    for index in range(offset, offset + len(sums)):
        turn = profile.observation(index)
        expected_rows.append([turn.uid, turn.c_id, turn.t_id, turn.replay_num,
                              turn.rkl_sum, turn.nll_sum, turn.tokens])
    expected_new = [[c_id, profile.conversation(c_id).group_id]
                    for c_id in range(old_count, profile.conversation_count)]
    if rows != expected_rows or observations["new_conversations"] != expected_new or finished != sorted(set(finished)):
        raise ValueError("Profile observation identity/order/replay differs from canonical record semantics")
    if any(turn[3] != 0 for turn in expected_rows):
        raise ValueError("Full-mode profile contains replayed training turns")
    if profile.summary() != summary:
        raise ValueError("Profile update summary does not reproduce native/canonical observations")
    update = profile.update(update_id)
    for name, expected in (("kl_before_tis_numerator", update.rkl_sum),
                           ("nll_before_tis_numerator", update.nll_sum),
                           ("kl_before_tis_denominator", update.tokens),
                           ("nll_before_tis_denominator", update.tokens)):
        value = native[name]
        if type(value) not in (int, float) or not math.isfinite(value) or not math.isclose(value, expected):
            raise ValueError(f"Native {name}={value!r} differs from verified profile {expected}")


def _profile_prefix(training_dir: Path, native: list[dict], summaries: list[dict], observations: list[dict]):
    verified, error = 0, None
    if not native or not summaries or not observations:
        return 0, None, "No complete native/profile pair available; values and UID identity are unverified"
    # A first pass uses record_update validation. Only accepted original pairs enter
    # a temporary prefix; rebuild performs the second pass and returns clean state.
    try:
        with tempfile.TemporaryDirectory(prefix="distillation-inspection-") as temporary:
            directory = Path(temporary)
            first = summaries[0]
            profile = DistillationProfile(estimator=first["estimator"], trend_window=first["trend_window"],
                                          baseline_updates=first["baseline_updates"],
                                          baseline_turns=first["baseline_turns"], directory=None)
            for row, summary, observation in zip(native, summaries, observations, strict=False):
                try:
                    bank, counts = _canonical_bank(training_dir / f"bank_{row['bank']}.jsonl")
                    _verify_update(profile, row, summary, observation, bank, counts)
                except (OSError, ValueError, KeyError, TypeError, IndexError, OverflowError) as failure:
                    error = f"Profile update {verified + 1}: {type(failure).__name__}: {failure}"
                    break
                for name, value in ((UPDATES_FILE, summary), (OBSERVATIONS_FILE, observation)):
                    with (directory / name).open("a", encoding="utf-8") as stream:
                        stream.write(json.dumps(value, allow_nan=False) + "\n")
                verified += 1
            rebuilt = DistillationProfile.rebuild(directory) if verified else None
            return verified, rebuilt, error
    except (OSError, ValueError, KeyError, TypeError, IndexError, OverflowError) as failure:
        return 0, None, f"Prefix rebuild unavailable: {type(failure).__name__}: {failure}"


def _missing_pairs(summaries: list[dict], observations: list[dict], horizon: int) -> list[list[int]]:
    summary_ids = {row.get("update_id") for row in summaries if type(row.get("update_id")) is int}
    observation_ids = {row.get("update_id") for row in observations if type(row.get("update_id")) is int}
    ranges = []
    for update_id in range(1, horizon + 1):
        if update_id in summary_ids and update_id in observation_ids:
            continue
        if ranges and ranges[-1][1] == update_id - 1:
            ranges[-1][1] = update_id
        else:
            ranges.append([update_id, update_id])
    return ranges


def inspect_run(training_dir: Path, *, job: str, expected_updates: int,
                terminal_path: Path | None = None) -> tuple[dict, DistillationProfile | None]:
    """Inspect one snapshot; never infer zero actual updates from missing receipts.

    ``verified_updates`` requires canonical UID/mask evidence as well as paired
    mathematical consistency. Ranges are inclusive, extending to the supplied
    expected budget (200 for final formal acceptance). Missing terminal evidence
    leaves native completion unverified but does not invalidate a live prefix.
    Job identity is checked against the terminal, not inferred from ACK filenames.
    """
    if type(expected_updates) is not int or expected_updates < 1 or not isinstance(job, str) or not job:
        raise ValueError("job must be nonempty and expected_updates must be a positive integer")
    training_dir = Path(training_dir)
    terminal_path = Path(terminal_path) if terminal_path is not None else None
    profile_dir = training_dir / "distillation_profile"
    rows, read_error = _read_rows(training_dir / UPDATES_FILE, expected_updates + 1)
    native_rows, sequence_error = _native_prefix(rows, job)
    native_error = sequence_error or read_error
    observed = sum(row.get("update_successful") is True for row in rows)
    observed_ids = [row["update"] for row in rows if row.get("update_successful") is True
                    and type(row.get("update")) is int and row["update"] > 0]
    successful = len(native_rows) if native_rows and native_error is None else None
    if len(rows) > expected_updates:
        native_error = native_error or "Native ACK count exceeds expected update budget"
        successful = None
    terminal, terminal_error = _terminal(terminal_path, job)
    phase = terminal["status"]["phase"] if terminal is not None else None
    if not rows:
        native_error = native_error or "No native successful ACKs retained; actual update count is unverified"
    native_complete = (native_error is None and successful == expected_updates and phase == "Succeeded"
                       and terminal.get("native_execution_succeeded") is True)
    if phase is not None and phase != "Succeeded":
        terminal_error = f"Native terminal phase is {phase}: {terminal['status'].get('message', '')}"
    elif phase == "Succeeded" and terminal.get("native_execution_succeeded") is not True:
        terminal_error = "Succeeded terminal lacks native_execution_succeeded=true"
    elif phase == "Succeeded" and successful != expected_updates:
        terminal_error = f"Retained successful ACK count {successful!r} does not establish expected {expected_updates} updates"
    summaries, summaries_error = _read_rows(profile_dir / UPDATES_FILE, expected_updates + 1)
    observations, observations_error = _read_rows(profile_dir / OBSERVATIONS_FILE, expected_updates + 1)
    verified, profile, profile_error = _profile_prefix(training_dir, native_rows[:expected_updates], summaries, observations)
    if profile_error is None and verified < len(native_rows):
        next_ack = native_rows[verified]
        if next_ack.get("turn_sums_verified") is False and next_ack.get("unverified_turn_sums"):
            profile_error = (f"Profile update {next_ack['successful_updates']}: "
                             f"Native turn sums unverified: {next_ack['unverified_turn_sums']}")
    profile_error = profile_error or native_error or summaries_error or observations_error
    if not profile_error and (len(summaries) != verified or len(observations) != verified):
        profile_error = "Unpaired or extra profile records beyond the verified native prefix"
    if not profile_error and verified < expected_updates:
        profile_error = f"Verified profile prefix ends at {verified}; expected {expected_updates} updates"
    horizon = max(expected_updates, len(rows), len(summaries), len(observations))
    first_unverified = verified + 1 if verified < horizon else None
    complete = verified == expected_updates and first_unverified is None and profile_error is None
    receipt = {
        "job": job, "expected_updates": expected_updates,
        "paths": {"training_dir": str(training_dir), "profile_dir": str(profile_dir),
                  "terminal": str(terminal_path) if terminal_path is not None else None},
        "native": {"observed_successful_updates": observed, "observed_successful_update_ids": observed_ids,
                   "successful_updates": successful,
                   "terminal_phase": phase, "complete": native_complete,
                   "error": native_error or terminal_error,
                   "terminal_error": terminal_error,
                   "terminal_job_verified": terminal is not None,
                   "terminal_uid": terminal.get("uid") if terminal is not None else None,
                   "ack_identity": {name: native_rows[0][name] for name in
                                    ("cell", "attempt", "protocol", "teacher_identity", "run_kind")} if native_rows else None,
                   "count_scope": "retained_successful_ack_sequence" if successful is not None else "unverified"},
        "profile": {"verified_updates": verified, "first_unverified_update": first_unverified,
                    "unverified_ranges": [[first_unverified, horizon]] if first_unverified is not None else [],
                    "complete": complete, "error": profile_error,
                    "canonical_uid_verified_updates": verified,
                    "identity_scope": "sealed_bank_source_uid_group_turn_and_original_mask",
                    "missing_pair_ranges": _missing_pairs(summaries, observations, horizon),
                    "read_errors": {"native_updates": read_error, "profile_updates": summaries_error,
                                    "profile_observations": observations_error},
                    "retained_update_rows": len(summaries), "retained_observation_rows": len(observations)},
    }
    return receipt, profile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-dir", type=Path, required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--expected-updates", type=int, required=True)
    parser.add_argument("--terminal", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is not None:
        output = args.output.resolve()
        if output.is_relative_to(args.training_dir.resolve()) or (args.terminal is not None and output == args.terminal.resolve()):
            parser.error("output must not overwrite retained training/profile/bank or terminal evidence")
    receipt, _ = inspect_run(args.training_dir, job=args.job, expected_updates=args.expected_updates,
                             terminal_path=args.terminal)
    text = json.dumps(receipt, indent=2, allow_nan=False) + "\n"
    if args.output is None:
        print(text, end="")
    else:
        args.output.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
