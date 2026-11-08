"""Distillation profile: RKL/NLL per successful update, source conversation and training turn.

Turn observations live column-wise in append-only arrays. Each source conversation keeps its
per-update entries with pointers to its RKL-best and latest entry, and a t_id -> latest
observation lookup, so queries read stored values and never recompute history. Every successful
update appends one line to updates.jsonl and one to observations.jsonl; the latter is enough to
rebuild the profile offline.
"""

import bisect
import itertools
import json
import logging
import math
from array import array
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

UPDATES_FILE = "updates.jsonl"
OBSERVATIONS_FILE = "observations.jsonl"


@dataclass(frozen=True)
class TurnSums:
    """One trained turn's sums from the optimizer-step record, identified by its source uid."""

    uid: str
    rkl_sum: float
    nll_sum: float
    tokens: int


@dataclass(frozen=True)
class TurnObservation:
    """One table cell: a training turn measured in one successful update."""

    update_id: int
    c_id: int
    t_id: int
    replay_num: int
    alive: bool
    rkl_sum: float
    nll_sum: float
    tokens: int
    uid: str

    @property
    def rkl(self) -> float:
        return self.rkl_sum / self.tokens

    @property
    def nll(self) -> float:
        return self.nll_sum / self.tokens


@dataclass(frozen=True)
class UpdateRow:
    """Token-weighted totals of one successful update."""

    update_id: int
    rkl_sum: float
    nll_sum: float
    tokens: int
    turns: int
    conversations: int

    @property
    def rkl(self) -> float:
        return self.rkl_sum / self.tokens

    @property
    def nll(self) -> float:
        return self.nll_sum / self.tokens


@dataclass(frozen=True)
class ConversationEntry:
    """A conversation in one update: equal-weight means over its turns there and their observation rows."""

    update_id: int
    rkl: float
    nll: float
    rows: range


@dataclass(frozen=True)
class SourceConversation:
    c_id: int
    group_id: str
    alive: bool
    latest: ConversationEntry
    best: ConversationEntry

    @property
    def recovery_gap(self) -> float:
        return self.latest.rkl - self.best.rkl


@dataclass(frozen=True)
class ConversationStates:
    """Per-conversation values indexed by c_id; a trend is None when no entry lies k updates back."""

    rkl_trend: tuple[float | None, ...]
    recovery_gap: tuple[float, ...]
    alive: tuple[bool, ...]


@dataclass(frozen=True)
class UpdateObservations:
    """Everything one successful update adds; one observations.jsonl line."""

    update_id: int
    # (uid, c_id, t_id, replay_num, rkl_sum, nll_sum, tokens), sorted by (c_id, t_id).
    rows: tuple[tuple[str, int, int, int, float, float, int], ...]
    new_conversations: tuple[tuple[int, str], ...]
    finished: tuple[int, ...]


class _Conversation:
    __slots__ = ("group_id", "alive", "updates", "rkl", "nll", "rows", "best", "cells")

    def __init__(self, group_id: str):
        self.group_id = group_id
        self.alive = True
        self.updates: list[int] = []
        self.rkl: list[float] = []
        self.nll: list[float] = []
        self.rows: list[range] = []
        self.best = 0
        self.cells: dict[int, int] = {}

    def add(self, update_id: int, rkl: float, nll: float, rows: range) -> None:
        self.updates.append(update_id)
        self.rkl.append(rkl)
        self.nll.append(nll)
        self.rows.append(rows)
        if rkl < self.rkl[self.best]:
            self.best = len(self.rkl) - 1

    def entry(self, index: int) -> ConversationEntry:
        return ConversationEntry(self.updates[index], self.rkl[index], self.nll[index], self.rows[index])


class DistillationProfile:
    def __init__(self, *, estimator: str, trend_window: int, directory: Path | None):
        self.estimator = estimator
        self.trend_window = trend_window
        self.directory = directory
        self.unverified_from: int | None = None
        self._updates: list[UpdateRow] = []
        self._best_update = 0
        self._conversations: list[_Conversation] = []
        self._c_ids: dict[str, int] = {}
        self._update_id = array("i")
        self._c_id = array("i")
        self._t_id = array("i")
        self._replay_num = array("i")
        self._rkl_sum = array("d")
        self._nll_sum = array("d")
        self._tokens = array("q")
        self._uid: list[str] = []

    def record_update(
        self,
        update_id: int,
        sums: Sequence[TurnSums],
        bank_turns: Mapping[str, tuple[str, int]],
        finished_group_ids: Iterable[str],
    ) -> None:
        """Add one successful update behind a soft gate.

        bank_turns maps each uid of the trained bank, in slot order, to its (group_id, t_id); sums
        must cover exactly those uids. finished_group_ids are the conversations whose last turn was
        drawn in that bank. An error is logged and marks the profile unverified from this update;
        later updates are ignored and the caller continues.
        """
        if self.unverified_from is not None:
            return
        try:
            observations = self._observations(update_id, sums, bank_turns, finished_group_ids)
            self._apply(observations)
            if self.directory is not None:
                self._persist(observations)
        except Exception:
            self.unverified_from = update_id
            logger.exception("Distillation profile unverified from update %d; training continues", update_id)

    def _observations(self, update_id, sums, bank_turns, finished_group_ids) -> UpdateObservations:
        if update_id != len(self._updates) + 1:
            raise ValueError(f"Successful update {update_id} does not follow {len(self._updates)}")
        by_uid = {turn.uid: turn for turn in sums}
        if not bank_turns or len(by_uid) != len(sums) or by_uid.keys() != bank_turns.keys():
            raise ValueError(f"{len(sums)} record rows do not match the {len(bank_turns)} bank turns one to one")
        new: dict[str, int] = {}
        rows = []
        for uid, (group_id, t_id) in bank_turns.items():
            c_id = self._c_ids.get(group_id)
            if c_id is None:
                c_id = new.setdefault(group_id, len(self._conversations) + len(new))
            turn = by_uid[uid]
            if turn.tokens <= 0 or not (math.isfinite(turn.rkl_sum) and math.isfinite(turn.nll_sum)):
                raise ValueError(f"Turn {uid} has no target tokens or nonfinite sums")
            previous = self._conversations[c_id].cells.get(t_id) if c_id < len(self._conversations) else None
            replay_num = 0 if previous is None else self._replay_num[previous] + 1
            rows.append((uid, c_id, t_id, replay_num, float(turn.rkl_sum), float(turn.nll_sum), int(turn.tokens)))
        rows.sort(key=lambda row: (row[1], row[2]))
        c_ids = {**self._c_ids, **new}
        finished = sorted({c_ids[group_id] for group_id in finished_group_ids if group_id in c_ids})
        return UpdateObservations(update_id, tuple(rows), tuple((c_id, g) for g, c_id in new.items()), tuple(finished))

    def _apply(self, observations: UpdateObservations) -> None:
        update_id = observations.update_id
        for c_id, group_id in observations.new_conversations:
            self._c_ids[group_id] = c_id
            self._conversations.append(_Conversation(group_id))
        start = len(self._uid)
        for uid, c_id, t_id, replay_num, rkl_sum, nll_sum, tokens in observations.rows:
            self._conversations[c_id].cells[t_id] = len(self._uid)
            self._update_id.append(update_id)
            self._c_id.append(c_id)
            self._t_id.append(t_id)
            self._replay_num.append(replay_num)
            self._rkl_sum.append(rkl_sum)
            self._nll_sum.append(nll_sum)
            self._tokens.append(tokens)
            self._uid.append(uid)
        stop = len(self._uid)
        conversations = 0
        # Rows are sorted by c_id, so each conversation's rows are contiguous.
        for c_id, group in itertools.groupby(range(start, stop), key=self._c_id.__getitem__):
            rows = list(group)
            rkl = sum(self._rkl_sum[r] / self._tokens[r] for r in rows) / len(rows)
            nll = sum(self._nll_sum[r] / self._tokens[r] for r in rows) / len(rows)
            self._conversations[c_id].add(update_id, rkl, nll, range(rows[0], rows[-1] + 1))
            conversations += 1
        row = UpdateRow(update_id, sum(self._rkl_sum[start:stop]), sum(self._nll_sum[start:stop]),
                        sum(self._tokens[start:stop]), stop - start, conversations)
        self._updates.append(row)
        if row.rkl < self._updates[self._best_update].rkl:
            self._best_update = len(self._updates) - 1
        for c_id in observations.finished:
            self._conversations[c_id].alive = False

    def _persist(self, observations: UpdateObservations) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        _append(self.directory / OBSERVATIONS_FILE, {
            "update_id": observations.update_id, "rows": observations.rows,
            "new_conversations": observations.new_conversations, "finished": observations.finished,
        })
        _append(self.directory / UPDATES_FILE, self.summary())

    @classmethod
    def rebuild(cls, directory: Path) -> "DistillationProfile":
        """Replay observations.jsonl; every replayed update must reproduce its updates.jsonl line."""
        summaries = _read_lines(directory / UPDATES_FILE)
        lines = _read_lines(directory / OBSERVATIONS_FILE)
        if not summaries or len(summaries) != len(lines):
            raise ValueError(f"{len(summaries)} update lines and {len(lines)} observation lines")
        profile = cls(estimator=summaries[0]["estimator"], trend_window=summaries[0]["trend_window"], directory=None)
        for line, summary in zip(lines, summaries, strict=True):
            profile._apply(UpdateObservations(
                line["update_id"], tuple(tuple(row) for row in line["rows"]),
                tuple(tuple(pair) for pair in line["new_conversations"]), tuple(line["finished"]),
            ))
            if profile.summary() != summary:
                raise ValueError(f"Update {line['update_id']} does not reproduce its {UPDATES_FILE} line")
        return profile

    @property
    def latest_update(self) -> int:
        return len(self._updates)

    @property
    def conversation_count(self) -> int:
        return len(self._conversations)

    def update(self, update_id: int) -> UpdateRow:
        return self._updates[update_id - 1]

    def best_update(self) -> UpdateRow:
        """Lowest macro RKL; the earliest update wins a tie."""
        return self._updates[self._best_update]

    def rkl_trend(self, k: int) -> float | None:
        """RKL of the latest update minus RKL k successful updates earlier."""
        latest = len(self._updates)
        return None if latest <= k else self._updates[-1].rkl - self._updates[latest - k - 1].rkl

    def recovery_gap(self) -> float:
        return self._updates[-1].rkl - self.best_update().rkl

    def conversation_id(self, group_id: str) -> int | None:
        return self._c_ids.get(group_id)

    def conversation(self, c_id: int) -> SourceConversation:
        conversation = self._conversations[c_id]
        return SourceConversation(c_id, conversation.group_id, conversation.alive,
                                  conversation.entry(-1), conversation.entry(conversation.best))

    def conversation_trend(self, c_id: int, k: int) -> float | None:
        """Latest entry's RKL minus that of the latest entry at least k updates before it."""
        conversation = self._conversations[c_id]
        reference = bisect.bisect_right(conversation.updates, conversation.updates[-1] - k) - 1
        return None if reference < 0 else conversation.rkl[-1] - conversation.rkl[reference]

    def conversation_states(self, k: int) -> ConversationStates:
        return ConversationStates(
            tuple(self.conversation_trend(c_id, k) for c_id in range(len(self._conversations))),
            tuple(c.rkl[-1] - c.rkl[c.best] for c in self._conversations),
            tuple(c.alive for c in self._conversations),
        )

    def observation(self, row: int) -> TurnObservation:
        c_id = self._c_id[row]
        return TurnObservation(self._update_id[row], c_id, self._t_id[row], self._replay_num[row],
                               self._conversations[c_id].alive, self._rkl_sum[row], self._nll_sum[row],
                               self._tokens[row], self._uid[row])

    def cell(self, c_id: int, t_id: int) -> TurnObservation | None:
        """Latest observation of turn t_id of conversation c_id, or None if it was never trained."""
        row = self._conversations[c_id].cells.get(t_id)
        return None if row is None else self.observation(row)

    def summary(self) -> dict:
        """The updates.jsonl line for the latest update."""
        row, best = self._updates[-1], self.best_update()
        states = self.conversation_states(self.trend_window)
        return {
            "update_id": row.update_id, "estimator": self.estimator,
            "rkl": row.rkl, "nll": row.nll, "rkl_sum": row.rkl_sum, "nll_sum": row.nll_sum,
            "tokens": row.tokens, "turns": row.turns, "conversations": row.conversations,
            "rkl_best": {"update_id": best.update_id, "rkl": best.rkl, "nll": best.nll},
            "trend_window": self.trend_window, "rkl_trend": self.rkl_trend(self.trend_window),
            "recovery_gap": self.recovery_gap(),
            "conversations_seen": len(states.alive),
            "conversations_with_trend": sum(trend is not None for trend in states.rkl_trend),
            "conversations_alive": sum(states.alive),
        }


def _append(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, allow_nan=False) + "\n")


def _read_lines(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]
