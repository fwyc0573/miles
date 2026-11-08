"""Retain the 2026-11-08 baseline mutations without changing their text replacements.

Provenance: /data/ycfeng/tmp/agent-opd-image/inject_profile_bugs_baselines.py (preserved).
Use the shared sandbox runner, never edit the repository's profile module.
Run from the repository root:
  python -m tests.manual.agent_opd.inject_profile_bugs_baselines --temporary-root <existing-temp-directory>
Stale replacements are reported separately from pytest failures; logs stay in the sandbox.
"""

from tests.manual.agent_opd.inject_profile_bugs import main

MUTATIONS = {
    "unpatched": None,
    "tie_moves_best": ("        if rkl < self.rkl[self.best]:", "        if rkl <= self.rkl[self.best]:"),
    "token_weighted_conversation_mean": (
        "            turn_rkl = [self._rkl_sum[r] / self._tokens[r] for r in rows]",
        "            turn_rkl = [sum(self._rkl_sum[r] for r in rows) / sum(self._tokens[r] for r in rows)]",
    ),
    "macro_trend_off_by_one": ("self._updates[latest - k - 1].rkl", "self._updates[latest - k].rkl"),
    "conversation_trend_sign_flipped": (
        "        return _ratio(conversation.rkl[reference] - conversation.rkl[-1], conversation.baseline)",
        "        return _ratio(conversation.rkl[-1] - conversation.rkl[reference], conversation.baseline)",
    ),
    "run_baseline_window_off_by_one": (
        "        if self._baseline is None and len(self._updates) == self.baseline_updates:",
        "        if self._baseline is None and len(self._updates) == self.baseline_updates + 1:",
    ),
    "nonpositive_baseline_divides": (
        "    return None if baseline is None or baseline <= 0 else value / baseline",
        "    return None if baseline is None else value / baseline",
    ),
    "conversation_baseline_takes_every_turn": (
        "            taken = turn_rkl[: self.baseline_turns - self.baseline_count]",
        "            taken = turn_rkl",
    ),
    "run_relative_gap_uses_own_baseline": (
        "        return _ratio(self.latest.rkl, self.run_baseline)",
        "        return _ratio(self.latest.rkl, self.baseline)",
    ),
}


if __name__ == "__main__":
    main(MUTATIONS, "profile-baseline-mutations-")
