"""Synthetic CPU-only S9 report values, undefined populations and partial-profile disposition.

No fixture represents a formal A/B measurement, and no native/profile evidence parser is mocked
into the pure report computation. The primary session checks the combined inspector CLI separately.
"""

import copy
import json
import math

import pytest

from tests.manual.agent_opd.distillation_profile import DistillationProfile, TurnSums
from tests.manual.agent_opd.distillation_report import (
    S9_MILESTONES, build_report, quantile_summary, render_markdown, write_report,
)


def _receipt(verified, *, expected=200, observed=None, native_complete=False, profile_complete=False):
    observed = verified if observed is None else observed
    return {
        "job": "synthetic-cpu-report-fixture",
        "expected_updates": expected,
        "paths": {
            "training_dir": "/synthetic/cell/training",
            "profile_dir": "/synthetic/cell/training/distillation_profile",
            "terminal": "/synthetic/cell/terminal.json",
        },
        "native": {
            "observed_successful_updates": observed,
            "successful_updates": observed,
            "terminal_phase": "Succeeded" if native_complete else None,
            "complete": native_complete,
            "error": None,
        },
        "profile": {
            "verified_updates": verified,
            "first_unverified_update": None if profile_complete else verified + 1,
            "unverified_ranges": [] if profile_complete else [[verified + 1, expected]],
            "complete": profile_complete,
            "error": None,
        },
    }


def _profile(*, baseline_updates=10, baseline_turns=8, trend_window=10):
    return DistillationProfile(estimator="sampled_token", trend_window=trend_window,
                               baseline_updates=baseline_updates, baseline_turns=baseline_turns, directory=None)


def _record(profile, update_id, turns, *, finished=()):
    """Turns are (group_id, t_id, RKL mean, NLL mean, tokens); only the profile computes losses' means."""
    sums, bank = [], {}
    for group_id, t_id, rkl, nll, tokens in turns:
        uid = f"{group_id}:{t_id}"
        bank[uid] = (group_id, t_id)
        sums.append(TurnSums(uid, rkl * tokens, nll * tokens, tokens))
    profile.record_update(update_id, sums, bank, finished)
    assert profile.unverified_from is None


def _milestone_profile(updates):
    profile = _profile()
    for update in range(1, updates + 1):
        rkl = float(update + 1) if update <= 10 else 4.0
        if update in (50, 100):
            rkl = 1.0
        elif update == 200:
            rkl = 3.0
        _record(profile, update, [("g", (update - 1) * 8 + turn, rkl, update + 0.25, turn)
                                  for turn in range(1, 9)])
    return profile


def test_s9_milestones_fixed_baseline_and_earliest_best():
    profile = _milestone_profile(200)
    receipt = _receipt(200, native_complete=True, profile_complete=True)
    before = copy.deepcopy(receipt)
    report = build_report(receipt, profile, cell="synthetic/full", limitations=("Synthetic CPU readiness only.",))
    assert receipt == before
    assert profile.latest_update == 200
    assert report["configuration"] == {
        "estimator": "sampled_token", "baseline_updates": 10, "baseline_turns": 8, "trend_window": 10,
    }
    macro = report["macro"]
    assert macro["baseline"] == {"value": 6.5, "status": "POSITIVE"}  # mean of 2..11, fixed at update 10
    assert [row["update_id"] for row in macro["milestones"]] == list(S9_MILESTONES)
    for row, rkl in zip(macro["milestones"], (2.0, 11.0, 1.0, 1.0, 4.0, 3.0), strict=True):
        assert row == {
            "update_id": row["update_id"], "status": "VERIFIED", "rkl": rkl,
            "nll": row["update_id"] + 0.25, "remaining_gap": rkl / 6.5,
        }
    assert macro["rkl_best"] == {"update_id": 50, "rkl": 1.0, "nll": 50.25}
    assert macro["rkl_trend"] == (4.0 - 3.0) / 6.5
    assert macro["recovery_gap"] == (3.0 - 1.0) / 6.5
    stats = report["conversations"]
    assert stats["counts"] == {
        "seen": 1, "alive": 1, "positive_baseline": 1, "nonpositive_baseline": 0,
        "defined_trend": 1, "incomplete_baseline": 0,
    }
    for name, value in {"remaining_gap": 1.5, "run_relative_gap": 3.0 / 6.5,
                        "rkl_trend": 0.5, "recovery_gap": 1.0}.items():
        distribution = stats["distributions"][name]
        assert (distribution["defined_count"], distribution["undefined_count"]) == (1, 0)
        assert all(actual == value for actual in distribution["quantiles"].values())
    assert report["disposition"] == {"native_training": "COMPLETE", "profile": "COMPLETE", "overall": "COMPLETE"}


def test_sparse_history_baseline_window_and_nonpositive_conversation_populations():
    profile = _profile(baseline_updates=2, baseline_turns=2, trend_window=3)
    _record(profile, 1, [("g", 1, 2.0, 1.0, 1), ("g", 2, 6.0, 2.0, 3)])
    _record(profile, 2, [("n", 1, -2.0, 3.0, 1), ("n", 2, -2.0, 3.0, 1),
                         ("z", 1, -1.0, 4.0, 1), ("z", 2, 1.0, 4.0, 1)], finished=("n", "z"))
    _record(profile, 3, [("g", 3, 1.0, 9.0, 2)])
    _record(profile, 4, [("s", 1, 3.0, 2.0, 1)])
    _record(profile, 5, [("g", 4, 1.0, 7.0, 1)], finished=("g",))
    report = build_report(_receipt(5), profile, cell="synthetic/sparse", milestones=(1, 2, 5, 10))
    macro, stats = report["macro"], report["conversations"]
    assert macro["baseline"] == {"value": 2.0, "status": "POSITIVE"}  # (token-weighted 5 + -1) / 2
    assert [row["remaining_gap"] for row in macro["milestones"]] == [2.5, -0.5, 0.5, None]
    assert macro["rkl_best"] == {"update_id": 2, "rkl": -1.0, "nll": 3.5}
    assert (macro["rkl_trend"], macro["recovery_gap"]) == (-1.0, 1.0)
    assert stats["counts"] == {
        "seen": 4, "alive": 1, "positive_baseline": 1, "nonpositive_baseline": 2,
        "defined_trend": 1, "incomplete_baseline": 1,
    }
    # g's latest is update 5; reference <= 2 is update 1, not the preceding appearance at 3.
    for name, value in {"remaining_gap": 0.25, "rkl_trend": 0.75, "recovery_gap": 0.0}.items():
        distribution = stats["distributions"][name]
        assert (distribution["defined_count"], distribution["undefined_count"]) == (1, 3)
        assert list(distribution["quantiles"].values()) == [value] * 5
    relative = stats["distributions"]["run_relative_gap"]
    assert (relative["defined_count"], relative["undefined_count"]) == (4, 0)
    assert relative["quantiles"] == pytest.approx({"p10": -0.7, "p25": -0.25, "p50": 0.25,
                                                  "p75": 0.75, "p90": 1.2})


@pytest.mark.parametrize("baseline", [0.0, -2.0])
def test_nonpositive_macro_baseline_does_not_hide_raw_metrics(baseline):
    profile = _profile(baseline_updates=1, baseline_turns=2, trend_window=1)
    _record(profile, 1, [("g", 1, baseline, 2.0, 1), ("g", 2, baseline, 4.0, 1)])
    _record(profile, 2, [("g", 3, 1.0, 5.0, 1)])
    report = build_report(_receipt(2), profile, cell="synthetic/nonpositive", milestones=(1, 2))
    macro = report["macro"]
    assert macro["baseline"] == {"value": baseline, "status": "NONPOSITIVE"}
    assert macro["milestones"][0]["rkl"] == baseline
    assert macro["milestones"][0]["nll"] == 3.0
    assert [row["remaining_gap"] for row in macro["milestones"]] == [None, None]
    assert (macro["rkl_trend"], macro["recovery_gap"]) == (None, None)
    assert report["conversations"]["counts"]["nonpositive_baseline"] == 1
    for distribution in report["conversations"]["distributions"].values():
        assert (distribution["defined_count"], distribution["undefined_count"]) == (0, 1)
        assert all(value is None for value in distribution["quantiles"].values())


@pytest.mark.parametrize("profile", [None, _profile()])
def test_empty_verified_prefix_never_fills_milestones(profile):
    receipt = _receipt(0)
    receipt["native"].update(successful_updates=None, terminal_phase="Failed", error="startup failed")
    receipt["profile"]["error"] = "no paired profile records"
    report = build_report(receipt, profile, cell="synthetic/empty")
    macro = report["macro"]
    assert macro["baseline"] == {"value": None, "status": "UNAVAILABLE" if profile is None else "INCOMPLETE"}
    assert macro["latest"] is macro["rkl_best"] is macro["rkl_trend"] is macro["recovery_gap"] is None
    assert all(row["status"] == "NOT_OBSERVED" and row["rkl"] is row["nll"] is row["remaining_gap"] is None
               for row in macro["milestones"])
    assert all(count == 0 for count in report["conversations"]["counts"].values())
    for distribution in report["conversations"]["distributions"].values():
        assert (distribution["defined_count"], distribution["undefined_count"]) == (0, 0)
        assert all(value is None for value in distribution["quantiles"].values())
    assert report["inspection"] == receipt


def test_native200_success_with_partial_profile_stays_incomplete():
    profile = _milestone_profile(3)
    receipt = _receipt(3, observed=200, native_complete=True)
    receipt["profile"]["error"] = "injected partial write at update 4"
    report = build_report(receipt, profile, cell="synthetic/partial")
    assert report["disposition"] == {
        "native_training": "COMPLETE", "profile": "INCOMPLETE / UNVERIFIED", "overall": "INCOMPLETE",
    }
    assert report["macro"]["baseline"] == {"value": None, "status": "INCOMPLETE"}
    assert report["macro"]["milestones"][0]["rkl"] == 2.0
    assert report["macro"]["milestones"][0]["remaining_gap"] is None
    assert all(row["status"] == "UNVERIFIED" and row["rkl"] is None for row in report["macro"]["milestones"][1:])
    assert report["conversations"]["as_of_update"] == 3
    assert report["conversations"]["counts"]["defined_trend"] == 0
    assert report["conversations"]["distributions"]["run_relative_gap"]["undefined_count"] == 1
    markdown = render_markdown(report)
    assert "Observed successful updates: 200" in markdown
    assert "Verified prefix: 3; first unverified update: 4; unverified ranges: [[4, 200]]" in markdown
    assert "injected partial write at update 4" in markdown
    assert "These are not counts for unverified later training." in markdown


def test_quantile_convention_omits_none_without_omitting_zero():
    summary = quantile_summary([None, 30.0, 0.0, None, 20.0, 10.0])
    assert (summary["defined_count"], summary["undefined_count"]) == (4, 2)
    assert summary["quantiles"] == pytest.approx({"p10": 3.0, "p25": 7.5, "p50": 15.0,
                                                  "p75": 22.5, "p90": 27.0})
    assert all(value is None for value in quantile_summary([None])["quantiles"].values())
    assert set(quantile_summary([7.0, None])["quantiles"].values()) == {7.0}
    for value in (math.inf, -math.inf, math.nan):
        with pytest.raises(ValueError, match="finite or None"):
            quantile_summary([value])


def test_json_markdown_paths_and_no_overwrite(tmp_path):
    receipt = _receipt(0)
    receipt["job"] = "synthetic|cpu"
    receipt["native"]["error"] = "line1|detail\nline2"
    report = build_report(receipt, None, cell="synthetic/full", limitations=("Synthetic CPU readiness only.",))
    prefix = tmp_path / "report" / "synthetic-profile"
    json_path, markdown_path = write_report(report, output_prefix=prefix)
    assert json.loads(json_path.read_text()) == report
    markdown = markdown_path.read_text()
    assert "Synthetic CPU readiness only." in markdown
    assert "synthetic\\|cpu" in markdown
    assert "line1\\|detail<br>line2" in markdown
    assert all(path in markdown for path in receipt["paths"].values())
    assert "h=(n-1)*p" in markdown and "exclude None" in markdown
    before = (json_path.read_bytes(), markdown_path.read_bytes())
    with pytest.raises(FileExistsError, match="already exists"):
        write_report(report, output_prefix=prefix)
    assert before == (json_path.read_bytes(), markdown_path.read_bytes())


@pytest.mark.parametrize("milestones", [(0, 1), (2, 1), (1, 1), (True,), (1.5,)])
def test_milestone_inputs_are_explicit_and_ordered(milestones):
    with pytest.raises(ValueError, match="strictly increasing positive integers"):
        build_report(_receipt(0), None, cell="synthetic", milestones=milestones)


def test_nonqueryable_or_mismatched_prefix_is_rejected():
    with pytest.raises(ValueError, match="nonempty verified prefix"):
        build_report(_receipt(1), None, cell="synthetic")
    profile = _milestone_profile(1)
    with pytest.raises(ValueError, match="exactly the inspector's"):
        build_report(_receipt(2), profile, cell="synthetic")
    profile.invalidate(2, "synthetic failure; runtime memory is not an offline verified prefix")
    with pytest.raises(ValueError, match="exactly the inspector's"):
        build_report(_receipt(1), profile, cell="synthetic")
