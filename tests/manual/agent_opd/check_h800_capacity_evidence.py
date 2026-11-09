"""Recheck the retained, terminal H800 D34 capacity evidence without network access."""

import argparse
import json
from pathlib import Path


def check(evidence: Path) -> None:
    def read(name: str) -> dict:
        return json.loads((evidence / name).read_text())

    result = read("h800-network-fixed-native-capacity-final-20261109.json")
    terminal = read("h800-network-fixed-native-terminal-20261109.json")
    weights = read("h800-network-fixed-version-one-checksum-check-20261109.json")
    assert terminal["status"]["phase"] == "Succeeded"
    assert set(terminal["replicas"]) == {"student", "teacher"}
    assert len(terminal["replicas"]["student"]) == 4
    assert len(terminal["replicas"]["teacher"]) == 1
    assert all(row["phase"] == "Succeeded" for rows in terminal["replicas"].values() for row in rows)
    updates = result["updates"]
    assert len(updates) == 2
    assert [row["successful_updates"] for row in updates] == [1, 2]
    assert [row["bank_visit"] for row in updates] == [1, 2]
    assert [row["current_weight_version"] for row in updates] == [0, 1]
    assert all(
        row["update_successful"]
        and row["bank_membership_verified"]
        and row["actual_turns"] == 256
        and row["bank"] == 0
        and row["native_skipped_count"] == 0
        and row["diagnostics_verified"]
        and row["mask_evidence_verified"]
        for row in updates
    )
    ranks = []
    assert len(result["memory_files"]) == 8
    for file in result["memory_files"]:
        assert not file["unverified"] and len(file["groups"]) == 2
        passes = {group["scoring_pass_index"]: group for group in file["groups"]}
        assert set(passes) == {0, 1}
        for group in passes.values():
            assert group["store_prefix"] == ""
            assert group["distinct_microbatch_indices"] == 88
            assert group["microbatch_index_range"] == [0, 87]
            assert group["events"] == {
                "source_identity": 1,
                "forward_enter": 88,
                "projection_enter": 88,
                "forward_exit": 88,
            }
            assert group["source_verified"] == [True]
            assert group["prior_output_alive"] == {"False": 264}
            assert group["maximum_full_output_storage_bytes"] == 16273899520
        assert passes[1]["minimum_timestamp"] > updates[0]["timestamp"]
        assert passes[1]["maximum_timestamp"] < updates[1]["timestamp"]
        ranks.append(passes[0]["rank"])
    assert sorted(ranks) == list(range(8))
    assert weights["text_only_status"] == "PASS"
    print("PASS: retained terminal updates, bank visits, two student passes and text-only weight scope")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    check(parser.parse_args().evidence)
