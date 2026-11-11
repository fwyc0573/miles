"""Bounded local receipt inspection; retains compact counts and selected metadata."""

import collections
import json
import resource
from pathlib import Path


def main():
    resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
    task = Path(__file__).resolve().parents[2]
    findings = {}
    for pair in ("A", "B"):
        attempt = task / "evidence/teacher-scoring-kv-coherence-probe-20261111/native" / pair / f"admission-{pair}-r2"
        startup = json.loads((attempt / "server_info.json").read_text())["get_server_info"]["internal_states"][0]
        final = json.loads((attempt / "runtime_metadata.json").read_text())["server_info"]["internal_states"][0]
        before, after = startup["kv_coherence"], final["kv_coherence"]
        info = {"process_id": after["process_id"], "topology": after["topology"],
                "startup_error_count": len(before["errors"]), "final_error_count": len(after["errors"]),
                "error_arrays_exact": before["errors"] == after["errors"],
                "all_error_rids_null": all(e["rid"] is None for e in after["errors"]),
                "error_stages": dict(collections.Counter(e["stage"] for e in after["errors"])),
                "completed_rid_count": len(after["completed_rids"]), "coverage": after["coverage"],
                "status": after["status"], "numeric_acceptance": after["numeric_acceptance"],
                "banks": [{"rid": bank["rid"], "fresh_layers": bank["fresh_layers"],
                           "bank_error_count": len(bank["errors"]),
                           "original_fragments": [{key: fragment[key] for key in ("lo", "hi", "cursor", "prefix_len")}
                                                  for fragment in bank["fragments"]],
                           "insert_recorded": bank["insert"] is not None,
                           "rebind_recorded": bank["rebind"] is not None} for bank in after["banks"]]}
        selected = {}
        for phase, state in (("startup", startup), ("business", final)):
            rows = state["mamba_runtime_metadata"]["rows"]
            events = {}
            for event in ("kv_store_stream", "kv_store_terminal"):
                group = [row for row in rows if row[1] == event]
                fields = [dict(row[2]) for row in group]
                counts = collections.Counter(tuple(key for key in ("rids", "prefix_lens", "extend_lens")
                                                   if value[key] is None) for value in fields)
                events[event] = {"count": len(group), "first_seq": group[0][0], "last_seq": group[-1][0],
                                 "null_patterns": {",".join(key) or "NONE": value for key, value in counts.items()}}
                selected[phase, event] = group
            chunk_keys = {(tuple(f["rids"]), tuple(f["prefix_lens"]), tuple(f["extend_lens"]))
                          for row in selected[phase, "kv_store_stream"] for f in (dict(row[2]),)
                          if f["prefix_lens"] is not None and f["extend_lens"] is not None}
            scheduler_keys = {((f["rid"],), (f["prefix_len"],), (f["extend_len"],))
                              for row in rows if row[1] == "scheduler_track_boundary" for f in (dict(row[2]),)}
            events["unique_host_chunks"] = len(chunk_keys)
            events["scheduler_chunks"] = len(scheduler_keys)
            events["host_keys_equal_scheduler"] = chunk_keys == scheduler_keys
            info[phase] = events

        def key(row):
            f = dict(row[2])
            return (tuple(f["rids"]), tuple(f["prefix_lens"]), tuple(f["extend_lens"]),
                    f["k_cache_data_ptr"], f["v_cache_data_ptr"], f["writer_loc_data_ptr"])

        streams = selected["business", "kv_store_stream"]
        terminals = selected["business", "kv_store_terminal"]
        stream_keys = collections.Counter(key(row) for row in streams)
        terminal_keys = collections.Counter(key(row) for row in terminals)
        targets = {bank["rid"] for bank in after["banks"]}
        target_streams = [row for row in streams if dict(row[2])["rids"][0] in targets
                          and dict(row[2])["prefix_lens"] == [90112]]
        target_terminals = [row for row in terminals if dict(row[2])["rids"][0] in targets
                            and dict(row[2])["prefix_lens"] == [90112]]
        info["business_join"] = {"keys_exact": stream_keys == terminal_keys,
                                 "all_keys_one_each": set(stream_keys.values()) == {1},
                                 "native_stream_eq_torch": all(dict(row[2])["native_actual_stream"] ==
                                                               dict(row[2])["torch_current_raw_stream"] for row in streams),
                                 "target_streams": len(target_streams), "target_terminals": len(target_terminals),
                                 "target_key_counts_exact": collections.Counter(key(row) for row in target_streams) ==
                                                            collections.Counter(key(row) for row in target_terminals),
                                 "first_target_stream_seq": target_streams[0][0],
                                 "first_target_terminal_seq": target_terminals[0][0]}
        null_stream = next(row for row in selected["startup", "kv_store_stream"]
                           if dict(row[2])["prefix_lens"] is None)
        null_terminal = next(row for row in selected["startup", "kv_store_terminal"]
                             if dict(row[2])["prefix_lens"] is None)
        info["selected_rows"] = {"startup_null_stream": null_stream, "startup_null_terminal": null_terminal,
                                 "business_first_stream": streams[0], "business_first_terminal": terminals[0],
                                 "target_first_stream": target_streams[0], "target_first_terminal": target_terminals[0]}
        findings[pair] = info
        print(json.dumps({pair: {key: value for key, value in info.items()
                                if key not in ("topology", "selected_rows", "banks")}}, indent=2))
    output = Path(__file__).with_name("receipt_counts.json")
    with output.open("x") as handle:
        json.dump({"task_id": "profile-kv-coherence-batch-metadata-rca-20261111", "scope": "READ_ONLY_RECEIPT_RCA",
                   "pairs": findings}, handle, indent=2)


if __name__ == "__main__":
    main()
