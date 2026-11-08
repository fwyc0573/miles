"""Hand-computed Distillation profile values, offline rebuild and soft-gate faults.

The shared sequence below runs with a 2-update run baseline and a 2-turn conversation baseline, so
every baseline state appears: g1 completes its baseline inside its first entry, g0 and g2 complete
theirs across two updates, and g3 never does. Expected values are written as the arithmetic over
the hand-computed baselines, run baseline 0.59375 = (0.75 + 0.4375) / 2.
"""

import json
import logging

import pytest

from tests.manual.agent_opd.distillation_profile import (
    OBSERVATIONS_FILE, UPDATES_FILE, ConversationEntry, ConversationStates, DistillationProfile, SourceConversation,
    TurnObservation, TurnSums, UpdateRow,
)

# Successful updates in order: bank turns in slot order as (uid, group_id, t_id, rkl_sum, nll_sum, tokens),
# and the group_ids whose last turn was drawn in that bank. "gX" was never trained.
UPDATES = [
    ([("g1:2", "g1", 1, 2.0, 4.0, 4), ("g1:4", "g1", 2, 3.0, 1.0, 2), ("g0:2", "g0", 1, 1.0, 3.0, 2)], []),
    ([("g1:6", "g1", 3, 1.0, 1.0, 4), ("g2:2", "g2", 1, 2.0, 2.0, 2), ("g0:4", "g0", 2, 0.5, 1.0, 2)], ["g0", "gX"]),
    ([("g1:8", "g1", 4, 2.0, 2.0, 4), ("g2:4", "g2", 2, 2.0, 1.0, 4)], ["g1"]),
    ([("g2:6", "g2", 3, 2.0, 2.0, 4), ("g3:2", "g3", 1, 1.5, 1.0, 4)], []),
]


def _sums(turns):
    # The record's row order differs from the bank's slot order; rows join by uid.
    return [TurnSums(uid, rkl_sum, nll_sum, tokens) for uid, _, _, rkl_sum, nll_sum, tokens in reversed(turns)]


def _bank(turns):
    return {uid: (group_id, t_id) for uid, group_id, t_id, *_ in turns}


def _record(profile, update_id):
    turns, finished = UPDATES[update_id - 1]
    profile.record_update(update_id, _sums(turns), _bank(turns), finished)


def _profile(directory=None):
    return DistillationProfile(estimator="sampled_token", trend_window=2, baseline_updates=2, baseline_turns=2,
                               directory=directory)


def test_hand_computed_profile():
    profile = _profile()
    _record(profile, 1)
    assert profile.update(1) == UpdateRow(1, 6.0, 8.0, 8, 3, 2)
    assert (profile.update(1).rkl, profile.update(1).nll) == (0.75, 1.0)
    assert [profile.conversation_id(g) for g in ("g1", "g0")] == [0, 1]
    # Equal-weight mean over a conversation's turns, unlike the token-weighted macro value.
    assert profile.conversation(0).latest == ConversationEntry(1, 1.0, 0.75, range(0, 2))
    assert profile.conversation(1).latest == ConversationEntry(1, 0.5, 1.5, range(2, 3))
    assert profile.rkl_trend(1) is None
    # The run baseline needs two updates, so nothing is in baseline units yet.
    assert (profile.baseline, profile.remaining_gap(1), profile.recovery_gap()) == (None, None, None)
    assert profile.conversation(0).baseline == 1.0  # (0.5 + 1.5) / 2, both turns in its first entry
    assert profile.conversation(1).baseline is None  # only one turn so far

    # The attempt after update 1 is skipped: no call, and the next successful update is 2.
    _record(profile, 2)
    assert profile.update(2) == UpdateRow(2, 3.5, 4.0, 8, 3, 3)
    assert profile.best_update().update_id == 2
    assert profile.baseline == 0.59375
    # Readable for every update once the baseline exists, including the updates inside its window.
    assert profile.remaining_gap(1) == 0.75 / 0.59375
    assert profile.remaining_gap(2) == 0.4375 / 0.59375
    assert profile.rkl_trend(1) == (0.75 - 0.4375) / 0.59375  # positive: RKL went down
    assert profile.conversation(1).baseline == 0.375  # (0.5 + 0.25) / 2, one turn from each of its entries
    assert profile.conversation(1).alive is False
    assert profile.conversation_id("gX") is None
    assert profile.conversation_count == 3

    _record(profile, 3)
    assert profile.rkl_trend(2) == (0.75 - 0.5) / 0.59375  # reference update 1 sits inside the baseline window
    assert profile.recovery_gap() == (0.5 - 0.4375) / 0.59375
    assert profile.conversation(0).alive is False

    _record(profile, 4)
    assert profile.update(4) == UpdateRow(4, 3.5, 3.0, 8, 2, 2)
    assert profile.best_update() == profile.update(2)  # tied RKL: the earliest update stays best
    assert profile.rkl_trend(2) == 0.0
    assert (profile.rkl_trend(3), profile.rkl_trend(4)) == ((0.75 - 0.4375) / 0.59375, None)
    assert profile.recovery_gap() == 0.0
    alive = (False, False, True, True)
    # Latest entry over the conversation's own baseline, then over the run baseline; g3 has no baseline yet.
    remaining = (0.5 / 1.0, 0.25 / 0.375, 0.5 / 0.75, None)
    run_relative = (0.5 / 0.59375, 0.25 / 0.59375, 0.5 / 0.59375, 0.375 / 0.59375)
    recovery = (0.25 / 1.0, 0.0, 0.0, None)
    assert profile.conversation_states(2) == ConversationStates(
        remaining, run_relative, ((1.0 - 0.5) / 1.0, None, (1.0 - 0.5) / 0.75, None), recovery, alive)
    assert profile.conversation_states(1) == ConversationStates(
        remaining, run_relative, ((0.25 - 0.5) / 1.0, (0.5 - 0.25) / 0.375, 0.0, None), recovery, alive)
    assert [profile.conversation_trend(c_id, 2) for c_id in range(4)] == [0.5, None, (1.0 - 0.5) / 0.75, None]
    assert profile.conversation(2) == SourceConversation(
        2, "g2", True,
        latest=ConversationEntry(4, 0.5, 0.5, range(8, 9)), best=ConversationEntry(3, 0.5, 0.25, range(7, 8)),
        baseline=0.75, run_baseline=0.59375,
    )
    best = profile.conversation(0).best
    assert best == ConversationEntry(2, 0.25, 0.25, range(3, 4))
    assert profile.conversation(0).recovery_gap == 0.25

    # Table: rows are t_id, columns are c_id; the best entry maps straight to its cells.
    assert [profile.observation(row) for row in best.rows] == [profile.cell(0, 3)]
    assert profile.cell(0, 3) == TurnObservation(2, 0, 3, 0, False, 1.0, 1.0, 4, "g1:6")
    cell = profile.cell(0, 2)
    assert cell == TurnObservation(1, 0, 2, 0, False, 3.0, 1.0, 2, "g1:4")
    assert (cell.rkl, cell.nll) == (1.5, 0.5)
    assert profile.cell(1, 3) is None
    assert [t_id for t_id in range(1, 6) if profile.cell(0, t_id) is not None] == [1, 2, 3, 4]
    assert [t_id for t_id in range(1, 6) if profile.cell(3, t_id) is not None] == [1]

    summary = profile.summary()
    assert summary["rkl_best"] == {"update_id": 2, "rkl": 0.4375, "nll": 0.5}
    assert (summary["rkl_trend"], summary["recovery_gap"]) == (0.0, 0.0)
    assert (summary["baseline"], summary["remaining_gap"]) == (0.59375, 0.4375 / 0.59375)
    assert (summary["baseline_updates"], summary["baseline_turns"]) == (2, 2)
    counts = ("conversations_seen", "conversations_with_baseline", "conversations_with_nonpositive_baseline",
              "conversations_with_trend", "conversations_alive")
    assert tuple(summary[key] for key in counts) == (4, 3, 0, 2, 2)
    assert profile.unverified_from is None


def test_files_rebuild_the_profile(tmp_path):
    directory = tmp_path / "distillation_profile"
    profile = _profile(directory)
    for update_id in range(1, 5):
        _record(profile, update_id)
    observations = [json.loads(line) for line in (directory / OBSERVATIONS_FILE).read_text().splitlines()]
    updates = [json.loads(line) for line in (directory / UPDATES_FILE).read_text().splitlines()]
    assert len(observations) == len(updates) == 4
    assert observations[0] == {
        "update_id": 1,
        "rows": [["g1:2", 0, 1, 0, 2.0, 4.0, 4], ["g1:4", 0, 2, 0, 3.0, 1.0, 2], ["g0:2", 1, 1, 0, 1.0, 3.0, 2]],
        "new_conversations": [[0, "g1"], [1, "g0"]], "finished": [],
    }
    assert observations[1]["new_conversations"] == [[2, "g2"]] and observations[1]["finished"] == [1]
    assert updates[-1] == profile.summary()

    rebuilt = DistillationProfile.rebuild(directory)
    assert (rebuilt.estimator, rebuilt.trend_window, rebuilt.latest_update) == ("sampled_token", 2, 4)
    assert (rebuilt.baseline_updates, rebuilt.baseline_turns, rebuilt.baseline) == (2, 2, profile.baseline)
    assert [rebuilt.update(u) for u in range(1, 5)] == [profile.update(u) for u in range(1, 5)]
    assert rebuilt.best_update() == profile.best_update()
    assert [rebuilt.conversation(c) for c in range(4)] == [profile.conversation(c) for c in range(4)]
    for k in range(1, 5):
        assert rebuilt.conversation_states(k) == profile.conversation_states(k)
    assert [rebuilt.observation(r) for r in range(10)] == [profile.observation(r) for r in range(10)]

    updates[2]["rkl"] += 1.0
    (directory / UPDATES_FILE).write_text("".join(json.dumps(line) + "\n" for line in updates))
    with pytest.raises(ValueError, match="Update 3 does not reproduce"):
        DistillationProfile.rebuild(directory)


def test_write_error_marks_unverified(tmp_path, caplog):
    blocker = tmp_path / "not_a_directory"
    blocker.write_text("")
    profile = _profile(blocker / "profile")
    with caplog.at_level(logging.ERROR):
        _record(profile, 1)
        _record(profile, 2)
    assert profile.unverified_from == 1
    assert profile.latest_update == 1  # the failed write does not stop the caller; later updates are ignored
    assert "unverified from update 1" in caplog.text


@pytest.mark.parametrize("fault", ["missing_row", "duplicate_row", "attempt_id"])
def test_inconsistent_record_marks_unverified(fault, caplog):
    turns, finished = UPDATES[0]
    sums, update_id = _sums(turns), 1
    if fault == "missing_row":
        sums = sums[1:]
    elif fault == "duplicate_row":
        sums = [*sums, sums[0]]
    else:
        update_id = 2  # an attempted rollout id instead of the successful-update count
    profile = _profile()
    with caplog.at_level(logging.ERROR):
        profile.record_update(update_id, sums, _bank(turns), finished)
    assert profile.unverified_from == update_id
    assert profile.latest_update == 0
    assert f"unverified from update {update_id}" in caplog.text


def test_nonpositive_baseline_leaves_its_values_undefined():
    # A sampled-token RKL mean can come out negative on few tokens, so a baseline need not be positive.
    turns = [("p:1", "p", 1, 4.0, 2.0, 2), ("p:2", "p", 2, 2.0, 2.0, 2),
             ("n:1", "n", 1, -1.0, 2.0, 2), ("n:2", "n", 2, -1.0, 2.0, 2)]
    profile = DistillationProfile(estimator="sampled_token", trend_window=1, baseline_updates=1, baseline_turns=2,
                                  directory=None)
    profile.record_update(1, _sums(turns), _bank(turns), [])
    assert (profile.baseline, profile.remaining_gap(1)) == (0.5, 1.0)  # 4.0 / 8 tokens, macro baseline positive
    positive, negative = profile.conversation(0), profile.conversation(1)
    assert (positive.baseline, negative.baseline) == (1.5, -0.5)
    assert (positive.remaining_gap, positive.run_relative_gap) == (1.0, 1.5 / 0.5)
    # The run baseline still places this conversation, but its own baseline cannot divide anything.
    assert (negative.remaining_gap, negative.recovery_gap) == (None, None)
    assert negative.run_relative_gap == -1.0
    summary = profile.summary()
    assert (summary["conversations_with_baseline"], summary["conversations_with_nonpositive_baseline"]) == (1, 1)


def test_baseline_stops_at_its_turn_count():
    # Rejections make a conversation's first updates uneven, so an update can offer more turns than
    # the baseline still needs; the later ones belong to the measured values, not to the baseline.
    first = [("s:1", "s", 1, 2.0, 1.0, 2)]
    second = [("s:2", "s", 2, 1.0, 1.0, 2), ("s:3", "s", 3, 6.0, 1.0, 2)]
    profile = DistillationProfile(estimator="sampled_token", trend_window=1, baseline_updates=1, baseline_turns=2,
                                  directory=None)
    profile.record_update(1, _sums(first), _bank(first), [])
    profile.record_update(2, _sums(second), _bank(second), [])
    conversation = profile.conversation(0)
    assert conversation.baseline == 0.75  # (1.0 + 0.5) / 2: turn 3 arrives after the baseline is full
    assert conversation.latest == ConversationEntry(2, 1.75, 0.5, range(1, 3))
    assert conversation.remaining_gap == 1.75 / 0.75


def test_nonpositive_lengths_are_rejected():
    with pytest.raises(ValueError, match="must all be positive"):
        DistillationProfile(estimator="sampled_token", trend_window=2, baseline_updates=0, baseline_turns=2,
                            directory=None)
