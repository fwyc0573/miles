"""CPU fault injection for native cache-salt joins; synthetic vectors are not GPU evidence."""

import copy
import json
from pathlib import Path

import pytest

from tests.manual.agent_opd import inspect_cache_salt_probe as inspection


def _row(seq, event, **fields):
    return [seq, event, [[name, value] for name, value in fields.items()]]


def _identity(pair="B", rid="native-rid"):
    return {(pair, rid): (pair, "source:turn", 7, 0, "warm_stream", "full_input")}


def _checkpoint(prefix=90112, returned=90112, end=98304, rid="native-rid"):
    return [
        _row(1, "checkpoint_insert_begin", rid=rid, protected_len=prefix, page_aligned_len=98304,
             insert_value=[123, "torch.int64", [1], [1], "cuda:0"]),
        _row(2, "checkpoint_insert_returned", rid=rid, prefix_len=returned, node_id=127,
             mamba_exist=False, rotation_tail_declined=False),
        _row(3, "canonical_kv_rebind_enqueued", rid=rid, prefix_len=returned, node_id=127,
             mamba_exist=False, absolute_start=prefix, absolute_end=end, page_aligned_len=98304),
    ]


def _scheduler(seq=1, rid="native-rid", prefix=0, extend=8, mask=True):
    return _row(seq, "scheduler_track_boundary", rid=rid, prefix_len=prefix, extend_len=extend,
                seq_end=prefix + extend, cache_chunk_size=4, state_chunk_size=4, checkpoint_grid=4,
                mask=mask, track_position=0, track_seqlen=prefix + extend if mask else -1,
                aligned_seqlen=prefix + extend, last_track_idx=0, next_track_idx=1,
                branching_seqlen=None, last_track_seqlen=prefix + extend if mask else None)


def _plan(seq=2, rids=None, prefixes=None, extends=None):
    rids = rids or ["native-rid"]
    prefixes, extends = prefixes or [0] * len(rids), extends or [8] * len(rids)
    size = len(rids)
    return _row(seq, "prefill_track_plan", rids=rids, chunk_size=4, mamba2=False,
                mask=[True] * size, track_lens=[p + e for p, e in zip(prefixes, extends)],
                prefix_lens=prefixes, extend_lens=extends, tracked_rows=list(range(size)),
                final_rows=list(range(size)), unaligned_rows=[], h_rows=[], h_src=[],
                recompute_rows=[], recompute_end_locs=[], chunk_indices=[-1] * size)


def _fields(row):
    return dict(row[2])


def _replace(row, **fields):
    return _row(row[0], row[1], **{**_fields(row), **fields})


def test_independent_join_then_negative_inequality_is_fail_not_unknown():
    result = inspection._checkpoint_isolation(_checkpoint(returned=98067), _identity(), "B")
    assert result["status"] == "FAIL" and result["ordinary_joined"] == 1 and not result["issues"]
    joined = result["joins"][0]
    assert joined["join_status"] == "PASS"
    assert joined["checks"] == {"returned_prefix_equals_protected": False,
                                "rebind_start_equals_protected": True, "rebind_end_equals_page_aligned": True}


@pytest.mark.parametrize("field,event", [("protected_len", 0), ("prefix_len", 1), ("absolute_start", 2), ("absolute_end", 2)])
def test_isolation_tests_each_equality_after_binding(field, event):
    rows = _checkpoint()
    rows[event] = _replace(rows[event], **{field: _fields(rows[event])[field] + 1})
    if field == "prefix_len":
        rows[2] = _replace(rows[2], prefix_len=_fields(rows[1])[field])
    result = inspection._checkpoint_isolation(rows, _identity(), "B")
    assert result["status"] == "FAIL" and result["ordinary_joined"] == 1


def test_own_protected_prefix_grows_and_rows_need_not_be_chronological():
    rows = _checkpoint()
    second = _checkpoint(prefix=98304, returned=98304, end=99072)
    second = [_replace(row, page_aligned_len=99072) if row[1] != "checkpoint_insert_returned" else row for row in second]
    second[1] = _replace(second[1], node_id=128)
    second[2] = _replace(second[2], node_id=128)
    second = [[seq + 3, event, fields] for seq, event, fields in second]
    result = inspection._checkpoint_isolation(list(reversed(rows + second)), _identity(), "B")
    assert result["status"] == "PASS" and result["ordinary_joined"] == 2


@pytest.mark.parametrize("duplicate", [0, 1, 2])
def test_duplicate_checkpoint_buckets_refused_even_identical(duplicate):
    rows = _checkpoint()
    rows.append([4, rows[duplicate][1], copy.deepcopy(rows[duplicate][2])])
    result = inspection._checkpoint_isolation(rows, _identity(), "B")
    assert result["status"] == "UNVERIFIED" and result["ordinary_joined"] == 0
    assert any("ambiguous" in item["error"] for item in result["issues"])


def test_ambiguity_not_resolved_using_equality_under_test():
    rows = _checkpoint()
    rows.append(_replace([4, *rows[0][1:]], protected_len=1))
    result = inspection._checkpoint_isolation(rows, _identity(), "B")
    assert result["ordinary_joined"] == 0 and result["status"] == "UNVERIFIED"


def test_declined_and_nonordinary_events_retained_without_fake_matching():
    rows = [_replace(_checkpoint()[0], insert_value=None),
            _replace(_checkpoint()[1], rotation_tail_declined=True)]
    result = inspection._checkpoint_isolation(rows, _identity(), "B")
    assert result["status"] == "UNVERIFIED" and result["ordinary_joined"] == 0
    assert len(result["nonordinary"]) == 2
    assert result["event_counts"] == {"checkpoint_insert_begin": 1, "checkpoint_insert_returned": 1}


@pytest.mark.parametrize("value", [None, True, False, "0", -1, 0.0])
def test_retraction_invalid_values_are_not_zero(value):
    observed = inspection._retractions({"meta_info": {"num_retractions": value}})
    assert observed == {"present": True, "value": value, "status": "UNVERIFIED"}


def test_missing_retraction_is_unverified_and_actual_integers_retained():
    assert inspection._retractions({"meta_info": {}}) == {"present": False, "value": None, "status": "UNVERIFIED"}
    for value in (0, 3):
        assert inspection._retractions({"meta_info": {"num_retractions": value}})["status"] == "PASS"


def test_mask_false_tail_is_a_chunk_not_an_allocation_or_store():
    ids = _identity()
    key = next(iter(ids.values()))
    rows = [_scheduler(), _plan(), _scheduler(seq=3, prefix=8, extend=1, mask=False),
            _row(4, "gdn_snapshot_allocation", rids=["native-rid"]),
            _row(5, "snapshot_store_enqueued", rids=["native-rid"])]
    result = inspection._chunks(rows, ids, {key: {"input_count": 9}}, "B")
    assert result["status"] == "PASS" and result["requests"][0]["chunk_count"] == 2
    assert result["requests"][0]["chunks"][1]["plan_status"] == "NOT_OBSERVED_MASK_FALSE"


def test_changed_tracking_observations_are_reported_not_an_unchanged_gate(synthetic_run):
    candidate, baseline = synthetic_run
    path = candidate / "runtime_metadata.json"
    receipt = inspection._read(path)
    rows = receipt["server_info"]["internal_states"][0]["mamba_runtime_metadata"]["rows"]
    rows[0] = _replace(rows[0], last_track_idx=1, next_track_idx=0)
    path.write_text(json.dumps(receipt))
    report = inspection.inspect_probe("B", candidate, baseline)
    assert report["cpu_verdict"] == "PASS"
    assert report["chunk_tracking_observations"][0]["chunk_tracking_equal"] is False


def test_identical_plan_dedup_and_conflict_refusal():
    ids = _identity()
    key = next(iter(ids.values()))
    plan = _plan()
    rows = [_scheduler(), plan, [3, *copy.deepcopy(plan[1:])]]
    result = inspection._chunks(rows, ids, {key: {"input_count": 8}}, "B")
    assert result["status"] == "PASS" and result["identical_plan_duplicates_deduplicated"] == 1
    rows[2] = _replace(rows[2], chunk_indices=[0])
    result = inspection._chunks(rows, ids, {key: {"input_count": 8}}, "B")
    assert result["status"] == "UNVERIFIED"
    assert result["requests"][0]["chunks"][0]["plan_status"] == "UNVERIFIED"


def test_plan_rids_index_cpu_rows_and_h_src_is_flattened():
    ids = {**_identity(), **_identity(rid="other")}
    ids["B", "other"] = ("B", "other-source", 8, 0, "cold", "full_input")
    plan = _plan(rids=["native-rid", "other"], extends=[8, 9])
    plan = _replace(plan, final_rows=[0], unaligned_rows=[1], h_rows=[1], h_src=[4], chunk_indices=[-1, 2])
    normalized = inspection._normalized_plan(_fields(plan), ids, "B")
    assert normalized["h_sources"] == [{"row": normalized["batch"][1], "flattened_source_index": 4}]
    rows = [_scheduler(), _scheduler(seq=3, rid="other", extend=9), plan]
    records = {key: {"input_count": 8 if key[1] == "source:turn" else 9} for key in ids.values()}
    result = inspection._chunks(rows, ids, records, "B")
    assert result["status"] == "PASS"
    assert [r["chunks"][0]["batch_row"] for r in result["requests"]] == [0, 1]


@pytest.mark.parametrize("fault", ["gap", "duplicate", "seq_end", "missing_plan", "bad_rid"])
def test_chunk_missing_or_ambiguous_evidence_is_unverified(fault):
    ids = _identity()
    key = next(iter(ids.values()))
    rows = [_scheduler(), _plan()]
    if fault == "gap":
        rows += [_scheduler(seq=3, prefix=9, extend=1, mask=False)]
    elif fault == "duplicate":
        rows += [[3, *copy.deepcopy(rows[0][1:])]]
    elif fault == "seq_end":
        rows[0] = _replace(rows[0], seq_end=9)
    elif fault == "missing_plan":
        rows.pop()
    else:
        rows[1] = _replace(rows[1], rids=["unrelated"])
    result = inspection._chunks(rows, ids, {key: {"input_count": 8}}, "B")
    assert result["status"] == "UNVERIFIED" and result["issues"]


@pytest.fixture
def synthetic_run(tmp_path):
    def write(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    samples = [{"source_uid": f"source:{i}", "sample_index": i, "tokens": [1, 2, 3, 4, 5, 6, 7, 8], "response_length": 2}
               for i in range(4)]
    fixture = tmp_path / "fixture.json"
    write(fixture, {"samples": samples})
    baseline, candidate = tmp_path / "baseline", tmp_path / "candidate"
    for directory in (baseline, candidate):
        directory.mkdir()
        records, cache, rows = [], [], []
        for phase in ("cold", "warm_stream"):
            for i, sample in enumerate(samples):
                for mode in ("full_input", "response_only"):
                    rid = f"{directory.name}-{phase}-{i}-{mode}"
                    request_id = f"{phase}-r0-s{i}-{mode}"
                    identity = {"pair": "B", "source_uid": sample["source_uid"], "sample_index": i, "repetition": 0,
                                "phase": phase, "mode": mode, "sample_position": i, "native_request_id": rid, "request_id": request_id}
                    start = 0 if mode == "full_input" else 5
                    request = {**identity, "input_count": 8, "prompt_count": 6, "response_count": 2, "logprob_start_len": start,
                               "status": "scored", "http_status": 200, "returned_completion_count": 2,
                               "input_token_logprobs_count": 8 - start, "expected_input_token_logprobs_count": 8 - start,
                               "first_input_token_logprob": None, "first_input_token_id": sample["tokens"][start],
                               "token_ids_match": True, "finite_log_probs": True,
                               "meta_info": {"id": rid, "completion_tokens": 0, "output_token_logprobs_length": 0, "num_retractions": 0},
                               "cache_salt": f"B:{request_id}" if directory == candidate and mode == "full_input" else None}
                    records.append(request)
                    # Preserve original response-only warm drift while salted warm-full becomes exact.
                    values = [0, -3] if phase == "warm_stream" and i and (mode == "response_only" or directory == baseline) else [0, -2]
                    write(directory / "completion_scores" / f"{request_id}.json", {**identity, "token_ids": [7, 8], "log_probs": values})
                    rows += [_scheduler(seq=len(rows) + 1, rid=rid), _plan(seq=len(rows) + 2, rids=[rid])]
                    checkpoint = _checkpoint(prefix=0, returned=0, end=8, rid=rid)
                    checkpoint[0] = _replace(checkpoint[0], page_aligned_len=8)
                    checkpoint[2] = _replace(checkpoint[2], page_aligned_len=8)
                    rows += [[len(rows) + j + 1, event, fields] for j, (_, event, fields) in enumerate(checkpoint)]
                    if phase == "cold":
                        cache.append({"phase": phase, "repetition": 0, "sample_position": i, "mode": mode, "status": "flushed", "http_status": 200})
        cache += [{"phase": "warm_stream", "repetition": 0, "mode": mode, "status": "flushed", "http_status": 200} for mode in inspection._MODES]
        for name, lines in (("requests.jsonl", records), ("cache.jsonl", cache)):
            (directory / name).write_text("".join(json.dumps(row) + "\n" for row in lines))
        result = {"pair": "B", "job": directory.name, "status": "measurements_completed", "native_measurements_completed": True,
                  "cleanup_completed": True, "sample_count": 4, "repeats": 1, "fixture": inspection._file_identity(fixture),
                  "sample_manifest": {"source_fixture": inspection._file_identity(fixture)},
                  "argv": ["server", "--dist-init-addr", directory.name],
                  "source_preflight": {"observed_after_sha256": {"math": "qualified"}},
                  "runtime_metadata_source_preflight": {"observed_after_sha256": {"metadata": "qualified"}},
                  "runtime": {"model_path": "model", "model_manifest_identity": {}, "sglang": "version", "torch": "version", "sglang_environment": {}}}
        write(directory / "result.json", result)
        write(directory / "runtime_metadata.json", {"status": "collected", "http": {"http_status": 200}, "server_info": {
            "dp_size": 1, "tp_size": 4, "pp_size": 1, "internal_states": [{"mamba_runtime_metadata": {
                "schema": "mamba-runtime-metadata-v1", "process_id": 1 if directory == baseline else 2,
                "rank": {"dp_rank": None, "tp_rank": 0, "pp_rank": 0, "attn_dp_rank": 0, "attn_tp_rank": 0}, "rows": rows}}]}})
    return candidate, baseline


def test_synthetic_namespace_controls_preserve_response_drift_without_full_vs_response_gate(synthetic_run):
    candidate, baseline = synthetic_run
    report = inspection.inspect_probe("B", candidate, baseline)
    assert report["cpu_verdict"] == "PASS", report["errors"]
    assert len(report["vector_controls"]["cases"]) == 12 and report["vector_controls"]["status"] == "PASS"
    assert len(report["warm_full_vs_own_cold"]) == 4
    assert all(row["comparison"]["values_exact"] for row in report["warm_full_vs_own_cold"])
    assert all(row["comparison"]["relative_error_undefined_count"] == 1 for row in report["warm_full_vs_own_cold"])
    assert report["scopes"][0]["rank"]["dp_rank"] is None


@pytest.mark.parametrize("fault", ["missing_retraction", "retraction_changed", "response_drift_changed", "warm_full_drift", "salt", "missing_salt", "pair", "incomplete", "missing_baseline_scope"])
def test_synthetic_end_to_end_faults(synthetic_run, fault):
    candidate, baseline = synthetic_run
    requests = inspection._lines(candidate / "requests.jsonl")
    if fault in ("missing_retraction", "retraction_changed", "salt", "missing_salt"):
        if fault == "missing_retraction":
            del requests[0]["meta_info"]["num_retractions"]
        elif fault == "retraction_changed":
            requests[0]["meta_info"]["num_retractions"] = 1
        elif fault == "missing_salt":
            del requests[0]["cache_salt"]
        else:
            requests[0]["cache_salt"] = "wrong"
        (candidate / "requests.jsonl").write_text("".join(json.dumps(row) + "\n" for row in requests))
    elif fault in ("response_drift_changed", "warm_full_drift"):
        mode = "response_only" if fault == "response_drift_changed" else "full_input"
        path = candidate / "completion_scores" / f"warm_stream-r0-s1-{mode}.json"
        vector = inspection._read(path)
        vector["log_probs"] = [0, -4]
        path.write_text(json.dumps(vector))
    elif fault == "incomplete":
        path = candidate / "result.json"
        result = inspection._read(path)
        result["native_measurements_completed"] = False
        path.write_text(json.dumps(result))
    elif fault == "missing_baseline_scope":
        path = baseline / "runtime_metadata.json"
        receipt = inspection._read(path)
        receipt["server_info"]["internal_states"][0]["mamba_runtime_metadata"]["rank"]["tp_rank"] = 1
        path.write_text(json.dumps(receipt))
    report = inspection.inspect_probe("A" if fault == "pair" else "B", candidate, baseline)
    expected = {"missing_retraction": "UNVERIFIED", "retraction_changed": "PASS", "response_drift_changed": "FAIL",
                "warm_full_drift": "PASS", "salt": "FAIL", "missing_salt": "UNVERIFIED", "pair": "UNVERIFIED",
                "incomplete": "UNVERIFIED", "missing_baseline_scope": "UNVERIFIED"}
    assert report["cpu_verdict"] == expected[fault], report
    if fault == "retraction_changed":
        assert report["retractions"][0]["values_equal"] is False
    if fault == "warm_full_drift":
        case = next(row for row in report["warm_full_vs_own_cold"] if row["logical_key"][2] == 1)
        assert case["comparison"]["max_absolute_error"] == 2 and case["comparison"]["max_relative_error"] == 1


def test_missing_archive_is_unverified(tmp_path):
    report = inspection.inspect_probe("B", tmp_path / "missing", tmp_path / "baseline")
    assert report["cpu_verdict"] == "UNVERIFIED" and report["errors"]


def test_native_rid_is_not_inferred_from_request_order(synthetic_run):
    candidate, _ = synthetic_run
    result = inspection._read(candidate / "result.json")
    samples = inspection._read(Path(result["sample_manifest"]["source_fixture"]["path"]))["samples"]
    requests = inspection._lines(candidate / "requests.jsonl")
    requests[0]["native_request_id"] = requests[1]["native_request_id"]
    (candidate / "requests.jsonl").write_text("".join(json.dumps(row) + "\n" for row in reversed(requests)))
    _, _, _, integrity = inspection._request_vectors(candidate, "B", samples)
    assert integrity["status"] == "UNVERIFIED" and integrity["errors"]


@pytest.mark.parametrize("missing", ["request", "flush"])
def test_missing_receipts_remain_unverified(synthetic_run, missing):
    candidate, baseline = synthetic_run
    path = candidate / ("requests.jsonl" if missing == "request" else "cache.jsonl")
    rows = inspection._lines(path)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows[1:]))
    report = inspection.inspect_probe("B", candidate, baseline)
    assert report["cpu_verdict"] == "UNVERIFIED"


def test_only_full_input_isolation_gates_shared_response_control_observations(synthetic_run):
    candidate, baseline = synthetic_run
    path = candidate / "runtime_metadata.json"
    receipt = inspection._read(path)
    rows = receipt["server_info"]["internal_states"][0]["mamba_runtime_metadata"]["rows"]
    control_rids = {r["native_request_id"] for r in inspection._lines(candidate / "requests.jsonl")
                    if r["mode"] == "response_only" and r["phase"] == "warm_stream" and r["sample_position"] > 0}
    for i, row in enumerate(rows):
        if _fields(row).get("rid") in control_rids and row[1] in ("checkpoint_insert_returned", "canonical_kv_rebind_enqueued"):
            rows[i] = _replace(row, prefix_len=4)
    path.write_text(json.dumps(receipt))
    report = inspection.inspect_probe("B", candidate, baseline)
    isolation = report["scopes"][0]["isolation"]
    assert isolation["status"] == "FAIL" and isolation["ordinary_joined"] == 16
    assert sum(j["status"] == "FAIL" for j in isolation["joins"]) == 3
    assert all(j["status"] == "PASS" for j in isolation["joins"] if j["logical_key"][-1] == "full_input")
    assert report["cpu_verdict"] == "PASS"
    target = isolation["full_input_isolation"]
    assert target["status"] == "PASS" and target["ordinary_joined"] == target["covered_rid_count"] == 8
    controls = isolation["control_observations"]
    assert controls["status"] == "FAIL" and controls["failed_joins"] == 3 and controls["ordinary_joined"] == 8


@pytest.mark.parametrize("fault,expected", [("target_failure", "FAIL"), ("target_ambiguity", "UNVERIFIED"),
                                           ("missing_target", "UNVERIFIED"), ("control_ambiguity", "UNVERIFIED")])
def test_full_input_scope_preserves_target_failures_and_binding_integrity(synthetic_run, fault, expected):
    candidate, baseline = synthetic_run
    requests = inspection._lines(candidate / "requests.jsonl")
    mode = "response_only" if fault == "control_ambiguity" else "full_input"
    rid = next(r["native_request_id"] for r in requests if r["mode"] == mode and r["phase"] == "cold" and r["sample_position"] == 0)
    path = candidate / "runtime_metadata.json"
    receipt = inspection._read(path)
    rows = receipt["server_info"]["internal_states"][0]["mamba_runtime_metadata"]["rows"]
    if fault == "target_failure":
        for i, row in enumerate(rows):
            if _fields(row).get("rid") == rid and row[1] in ("checkpoint_insert_returned", "canonical_kv_rebind_enqueued"):
                rows[i] = _replace(row, prefix_len=4)
    elif fault == "missing_target":
        rows[:] = [row for row in rows if not (_fields(row).get("rid") == rid and row[1] in (
            "checkpoint_insert_begin", "checkpoint_insert_returned", "canonical_kv_rebind_enqueued"))]
    else:
        begin = next(row for row in rows if _fields(row).get("rid") == rid and row[1] == "checkpoint_insert_begin")
        rows.append([rows[-1][0] + 1, begin[1], copy.deepcopy(begin[2])])
    path.write_text(json.dumps(receipt))
    report = inspection.inspect_probe("B", candidate, baseline)
    isolation = report["scopes"][0]["isolation"]
    assert report["cpu_verdict"] == expected
    assert isolation["full_input_isolation"]["status"] == expected
    if fault == "target_failure":
        failed = next(j for j in isolation["joins"] if j["native_rid"] == rid)
        assert failed["join_status"] == "PASS" and failed["status"] == "FAIL"
        assert isolation["full_input_isolation"]["failed_joins"] == 1
    elif fault == "missing_target":
        assert isolation["binding_status"] == "PASS"
        assert isolation["full_input_isolation"]["target_rid_count"] == 8
        assert isolation["full_input_isolation"]["covered_rid_count"] == 7
    else:
        assert isolation["binding_status"] == "UNVERIFIED" and isolation["issues"]
