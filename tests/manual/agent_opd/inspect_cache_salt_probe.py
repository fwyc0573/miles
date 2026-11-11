"""CPU inspection of the first4/rep0 cache-salt counterfactual and its qualified baseline.

Run only after native termination, with --pair, --output-dir and --baseline-dir.
JSON goes to stdout; this inspector never submits jobs or changes retained evidence.
Host receipts establish neither physical/device state nor all-TP coherence or races.
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from tests.manual.agent_opd.probe_teacher_scoring import _comparison, _file_identity, _runtime_metadata_states


_KEY = ("pair", "source_uid", "sample_index", "repetition", "phase", "mode")
_PHASES = ("cold", "warm_stream")
_MODES = ("full_input", "response_only")


def _key(record):
    return tuple(record[name] for name in _KEY)


def _read(path):
    return json.loads(path.read_text())


def _lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def _status(checks):
    if any(value is False for value in checks):
        return "FAIL"
    return "PASS" if checks and all(value is True for value in checks) else "UNVERIFIED"


def _nonnegative(value):
    return type(value) is int and value >= 0


def _retractions(request):
    meta = request.get("meta_info")
    present = isinstance(meta, dict) and "num_retractions" in meta
    value = meta.get("num_retractions") if isinstance(meta, dict) else None
    return {"present": present, "value": value, "status": "PASS" if present and _nonnegative(value) else "UNVERIFIED"}


def _request_vectors(directory, pair, samples):
    requests = _lines(directory / "requests.jsonl")
    expected = {(pair, s["source_uid"], s["sample_index"], 0, phase, mode)
                for s in samples for phase in _PHASES for mode in _MODES}
    records, vectors, by_rid, errors = {}, {}, {}, []
    for request in requests:
        try:
            key, rid, request_id = _key(request), request["native_request_id"], request["request_id"]
            position = request["sample_position"]
            if type(position) is not int or not 0 <= position < 4:
                raise ValueError("sample_position is not a first4 position")
            sample = samples[position]
            if key not in expected or key in records or (pair, rid) in by_rid:
                raise ValueError("unexpected or duplicate logical/native RID identity")
            if not isinstance(rid, str) or not rid or not isinstance(request_id, str) or not request_id:
                raise ValueError("missing native RID or pre-send request ID")
            if request_id != f"{request['phase']}-r0-s{position}-{request['mode']}":
                raise ValueError("pre-send request ID differs from the fixed probe identity")
            if (request["source_uid"], request["sample_index"]) != (sample["source_uid"], sample["sample_index"]):
                raise ValueError("request does not bind to its source sample")
            n, length = len(sample["tokens"]), sample["response_length"]
            start = 0 if request["mode"] == "full_input" else n - length - 1
            expected_fields = {"status": "scored", "http_status": 200, "input_count": n,
                               "prompt_count": n - length, "response_count": length, "logprob_start_len": start,
                               "returned_completion_count": length, "input_token_logprobs_count": n - start,
                               "expected_input_token_logprobs_count": n - start, "first_input_token_logprob": None,
                               "first_input_token_id": sample["tokens"][start], "token_ids_match": True,
                               "finite_log_probs": True}
            if any(name not in request or request[name] != value for name, value in expected_fields.items()):
                raise ValueError("request is not a successful complete source-bound scoring receipt")
            meta = request["meta_info"]
            if meta["id"] != rid or meta["completion_tokens"] != 0 or meta["output_token_logprobs_length"] != 0:
                raise ValueError("native response identity/generation contract differs")
            # Use the supplied retained directory, never a receipt's old absolute score path.
            vector = _read(directory / "completion_scores" / f"{request_id}.json")
            if _key(vector) != key or vector["native_request_id"] != rid or vector["request_id"] != request_id:
                raise ValueError("completion vector identity differs from request")
            if vector["token_ids"] != sample["tokens"][-length:] or len(vector["log_probs"]) != length:
                raise ValueError("completion vector differs from the fixed source token tail")
            if not _comparison(vector, vector)["values_exact"]:
                raise ValueError("completion vector is nonfinite or malformed")
            records[key], vectors[key], by_rid[pair, rid] = request, vector, key
        except (KeyError, TypeError, ValueError, OSError, IndexError) as error:
            errors.append({"request": request, "error": str(error)})
    complete = (len(requests) == len(records) == 16 and set(records) == expected
                and len({r["request_id"] for r in records.values()}) == 16)
    return records, vectors, by_rid, {"status": "PASS" if complete and not errors else "UNVERIFIED",
                                    "observed_requests": len(requests), "source_bound_requests": len(records), "errors": errors}


def _checkpoint_isolation(rows, by_rid, pair):
    begins, returned, rebinds = defaultdict(list), defaultdict(list), []
    counts, issues, nonordinary = Counter(), [], []
    relevant = ("checkpoint_insert_begin", "checkpoint_insert_returned", "canonical_kv_rebind_enqueued")
    for seq, event, fields in rows:
        if event not in relevant:
            continue
        counts[event] += 1
        f = dict(fields)
        try:
            if len(f) != len(fields) or (pair, f["rid"]) not in by_rid:
                raise ValueError("duplicate field or unbound native RID")
            if event == "checkpoint_insert_begin":
                if not all(_nonnegative(f[name]) for name in ("protected_len", "page_aligned_len")):
                    raise ValueError("malformed begin boundaries")
                value = f["insert_value"]
                if value is not None and not (isinstance(value, list) and len(value) == 5
                        and type(value[0]) is int and value[0] > 0 and isinstance(value[1], str)
                        and value[1].startswith("torch.") and isinstance(value[2], list) and isinstance(value[3], list)
                        and len(value[2]) == len(value[3]) and all(_nonnegative(i) for i in value[2] + value[3])
                        and isinstance(value[4], str)):
                    raise ValueError("malformed insert_value descriptor")
                begins[f["rid"], f["page_aligned_len"]].append((seq, f))
            else:
                if not all(_nonnegative(f[name]) for name in ("node_id", "prefix_len")) or type(f["mamba_exist"]) is not bool:
                    raise ValueError("malformed returned/rebind identity")
                key = tuple(f[name] for name in ("rid", "node_id", "prefix_len", "mamba_exist"))
                if event == "checkpoint_insert_returned":
                    if type(f["rotation_tail_declined"]) is not bool:
                        raise ValueError("missing/malformed rotation_tail_declined")
                    returned[key].append((seq, f))
                    if f["rotation_tail_declined"]:
                        nonordinary.append({"sequence": seq, "event": event, "fields": f})
                else:
                    if not all(_nonnegative(f[name]) for name in ("absolute_start", "absolute_end", "page_aligned_len")):
                        raise ValueError("malformed rebind boundaries")
                    rebinds.append((seq, f))
        except (KeyError, TypeError, ValueError) as error:
            issues.append({"sequence": seq, "event": event, "fields": f, "error": str(error)})
    rebind_begin = Counter((f["rid"], f["page_aligned_len"]) for _, f in rebinds)
    rebind_returned = Counter(tuple(f[name] for name in ("rid", "node_id", "prefix_len", "mamba_exist"))
                              for _, f in rebinds)
    used_begin, used_returned, joined = set(), set(), []
    for seq, f in rebinds:
        bk = (f["rid"], f["page_aligned_len"])
        rk = tuple(f[name] for name in ("rid", "node_id", "prefix_len", "mamba_exist"))
        # Bind only on independent identity fields, never the equalities being tested.
        if len(begins[bk]) != 1 or rebind_begin[bk] != 1 or len(returned[rk]) != 1 or rebind_returned[rk] != 1:
            issues.append({"sequence": seq, "fields": f, "error": "missing or ambiguous begin/returned/rebind bucket"})
            continue
        bseq, begin = begins[bk][0]
        rseq, ret = returned[rk][0]
        used_begin.add(bseq)
        used_returned.add(rseq)
        if ret["rotation_tail_declined"] or begin["insert_value"] is None:
            nonordinary.append({"sequences": [bseq, rseq, seq], "begin": begin, "returned": ret, "rebind": f})
            continue
        checks = {"returned_prefix_equals_protected": ret["prefix_len"] == begin["protected_len"],
                  "rebind_start_equals_protected": f["absolute_start"] == begin["protected_len"],
                  "rebind_end_equals_page_aligned": f["absolute_end"] == begin["page_aligned_len"]}
        joined.append({"logical_key": by_rid[pair, f["rid"]], "native_rid": f["rid"],
                       "sequences": [bseq, rseq, seq], "begin": begin, "returned": ret, "rebind": f,
                       "join_status": "PASS", "checks": checks, "status": _status(list(checks.values()))})
    for bucket in begins.values():
        for seq, f in bucket:
            if seq not in used_begin:
                target = nonordinary if f["insert_value"] is None else issues
                target.append({"sequence": seq, "event": "checkpoint_insert_begin", "fields": f,
                               "error": "unbound begin; no chronology-based attribution"})
    for bucket in returned.values():
        for seq, f in bucket:
            if seq not in used_returned and not f["rotation_tail_declined"]:
                issues.append({"sequence": seq, "event": "checkpoint_insert_returned", "fields": f,
                               "error": "unbound ordinary returned row"})
    checks = [r["status"] == "PASS" for r in joined] + ([None] if issues or not joined else [])
    return {"status": _status(checks), "event_counts": dict(counts), "ordinary_joined": len(joined),
            "declined_returned_rows": sum(f["rotation_tail_declined"] for bucket in returned.values() for _, f in bucket),
            "non_mamba_begin_rows": sum(f["insert_value"] is None for bucket in begins.values() for _, f in bucket),
            "joins": joined, "nonordinary": nonordinary, "issues": issues}


def _normalized_plan(f, by_rid, pair):
    rids = f["rids"]
    if not isinstance(rids, list):
        raise ValueError("batch rids must be the native CPU list")
    size = len(rids)
    if not size or any((pair, rid) not in by_rid for rid in rids) or len(set(rids)) != size:
        raise ValueError("missing/duplicate/unbound batch RID")
    for name in ("mask", "track_lens", "prefix_lens", "extend_lens", "chunk_indices"):
        if not isinstance(f[name], list) or len(f[name]) != size:
            raise ValueError(f"{name} does not match native batch row count")
    if any(type(x) is not bool for x in f["mask"]) or type(f["mamba2"]) is not bool:
        raise ValueError("malformed native mask/mamba2")
    if not _nonnegative(f["chunk_size"]) or f["chunk_size"] == 0:
        raise ValueError("malformed native chunk_size")
    for name in ("prefix_lens", "extend_lens"):
        if not all(_nonnegative(x) for x in f[name]):
            raise ValueError(f"malformed CPU {name}")
    for name in ("track_lens", "chunk_indices"):
        if not all(type(x) is int for x in f[name]):
            raise ValueError(f"malformed CPU {name}")
    batch = [{"logical_key": by_rid[pair, rid], "prefix_len": f["prefix_lens"][i],
              "extend_len": f["extend_lens"][i]} for i, rid in enumerate(rids)]
    result = {name: f[name] for name in ("chunk_size", "mamba2", "mask", "track_lens", "chunk_indices")}
    result["batch"] = batch
    for name in ("tracked_rows", "final_rows", "unaligned_rows", "h_rows", "recompute_rows"):
        indices = f[name]
        if not isinstance(indices, list) or any(not _nonnegative(i) or i >= size for i in indices) or len(set(indices)) != len(indices):
            raise ValueError(f"malformed CPU {name}")
        result[name] = [batch[i] for i in indices]
    if len(f["h_src"]) != len(f["h_rows"]) or not all(_nonnegative(i) for i in f["h_src"]):
        raise ValueError("h_src must map one flattened source index to each h_rows entry")
    if len(f["recompute_end_locs"]) != len(f["recompute_rows"]) or not all(_nonnegative(i) for i in f["recompute_end_locs"]):
        raise ValueError("malformed recompute_end_locs")
    result["h_sources"] = [{"row": batch[i], "flattened_source_index": source}
                           for i, source in zip(f["h_rows"], f["h_src"])]
    result["recompute_end_locs"] = f["recompute_end_locs"]
    return result


def _chunks(rows, by_rid, records, pair):
    chunks, plans, issues = defaultdict(list), defaultdict(list), []
    counts = Counter(event for _, event, _ in rows)
    for seq, event, fields in rows:
        if event not in ("scheduler_track_boundary", "prefill_track_plan"):
            continue
        f = dict(fields)
        try:
            if len(f) != len(fields):
                raise ValueError("duplicate field")
            if event == "scheduler_track_boundary":
                key = by_rid[pair, f["rid"]]
                if not all(_nonnegative(f[name]) for name in ("prefix_len", "extend_len", "seq_end")):
                    raise ValueError("malformed scheduler token positions")
                if f["seq_end"] != f["prefix_len"] + f["extend_len"] or f["extend_len"] == 0:
                    raise ValueError("seq_end != prefix_len + positive extend_len")
                if type(f["mask"]) is not bool:
                    raise ValueError("malformed scheduler mask")
                for name in ("cache_chunk_size", "state_chunk_size", "checkpoint_grid", "track_position", "track_seqlen",
                             "aligned_seqlen", "last_track_idx", "next_track_idx"):
                    if type(f[name]) is not int:
                        raise ValueError(f"malformed scheduler {name}")
                for name in ("branching_seqlen", "last_track_seqlen"):
                    if f[name] is not None and type(f[name]) is not int:
                        raise ValueError(f"malformed scheduler {name}")
                ck = (f["rid"], f["prefix_len"], f["extend_len"], f["seq_end"])
                chunks[ck].append({"sequence": seq, "logical_key": key,
                                   "scheduler": {name: value for name, value in f.items() if name != "rid"}})
            else:
                normalized = _normalized_plan(f, by_rid, pair)
                for i, rid in enumerate(f["rids"]):
                    prefix, extend = f["prefix_lens"][i], f["extend_lens"][i]
                    plans[rid, prefix, extend, prefix + extend].append((seq, i, normalized))
        except (KeyError, TypeError, ValueError) as error:
            issues.append({"sequence": seq, "event": event, "fields": f, "error": str(error)})
    observations = defaultdict(list)
    duplicates = 0
    for ck, bucket in chunks.items():
        if len(bucket) != 1:
            issues.append({"chunk_identity": ck, "error": "ambiguous scheduler chunk bucket"})
            continue
        row = bucket[0]
        bound = plans.pop(ck, [])
        unique = {json.dumps([i, plan], sort_keys=True): (i, plan) for _, i, plan in bound}
        if len(unique) > 1:
            issues.append({"chunk_identity": ck, "plan_sequences": [s for s, _, _ in bound], "error": "conflicting plan observations"})
            row.update(plan_status="UNVERIFIED", plans=[p for _, p in unique.values()])
        elif unique:
            i, plan = next(iter(unique.values()))
            duplicates += len(bound) - 1
            aligned = (plan["mask"][i] == row["scheduler"]["mask"]
                       and plan["track_lens"][i] == row["scheduler"]["track_seqlen"])
            if not aligned:
                issues.append({"chunk_identity": ck, "error": "CPU plan mask/track length differs from scheduler"})
            row.update(plan_status="PASS" if aligned else "UNVERIFIED", batch_row=i, plan=plan)
        else:
            row["plan_status"] = "UNVERIFIED" if row["scheduler"]["mask"] else "NOT_OBSERVED_MASK_FALSE"
            if row["scheduler"]["mask"]:
                issues.append({"chunk_identity": ck, "error": "missing tracked chunk plan"})
        observations[row["logical_key"]].append(row)
    for ck, bound in plans.items():
        issues.append({"chunk_identity": ck, "plan_sequences": [s for s, _, _ in bound], "error": "plan has no uniquely bound scheduler chunk"})
    per_request = []
    for key, request in records.items():
        rows_for_request = sorted(observations[key], key=lambda r: r["scheduler"]["prefix_len"])
        positions = [r["scheduler"] for r in rows_for_request]
        contiguous = bool(positions) and all(a["seq_end"] == b["prefix_len"] for a, b in zip(positions, positions[1:]))
        complete = contiguous and positions[-1]["seq_end"] == request["input_count"]
        if not complete:
            issues.append({"logical_key": key, "error": "missing/overlapping/noncontiguous token-position coverage"})
        per_request.append({"logical_key": key, "coverage_status": "PASS" if complete else "UNVERIFIED",
                            "initial_prefix_len": positions[0]["prefix_len"] if positions else None,
                            "complete_seq_end": positions[-1]["seq_end"] if positions else None,
                            "chunk_count": len(positions), "chunks": rows_for_request})
    return {"status": "PASS" if not issues and per_request else "UNVERIFIED", "requests": per_request,
            "identical_plan_duplicates_deduplicated": duplicates, "event_counts": dict(counts), "issues": issues}


def _metadata(directory, records, by_rid, pair):
    receipt = _read(directory / "runtime_metadata.json")
    observations = _runtime_metadata_states(receipt["server_info"])
    if receipt["status"] != "collected" or receipt["http"]["http_status"] != 200:
        raise ValueError("runtime metadata collection is not verified")
    scopes = []
    for observation, state in zip(observations, receipt["server_info"]["internal_states"]):
        rows = state["mamba_runtime_metadata"]["rows"]
        coverage, issues = set(), []
        for seq, event, fields in rows:
            f = dict(fields)
            if len(f) != len(fields):
                issues.append({"sequence": seq, "event": event, "error": "duplicate metadata field"})
            rids = [f["rid"]] if "rid" in f else f.get("rids") or []
            for rid in rids:
                if (pair, rid) not in by_rid:
                    issues.append({"sequence": seq, "event": event, "rid": rid, "error": "unbound explicit native RID"})
                else:
                    coverage.add(by_rid[pair, rid])
        if coverage != set(records):
            issues.append({"error": "responding scope lacks explicit coverage for every request"})
        scopes.append({**observation, "rid_coverage_status": "PASS" if not issues else "UNVERIFIED", "issues": issues,
                       "isolation": _checkpoint_isolation(rows, by_rid, pair),
                       "chunks": _chunks(rows, by_rid, records, pair)})
    return scopes


def _vector_controls(records, vectors, baseline_vectors):
    controls, warm = [], []
    for key, request in records.items():
        try:
            if request["mode"] == "response_only" or request["phase"] == "cold":
                comparison = _comparison(baseline_vectors[key], vectors[key])
                controls.append({"logical_key": key, "comparison": comparison})
            else:
                cold = (*key[:4], "cold", "full_input")
                warm.append({"logical_key": key, "cold_logical_key": cold, "comparison": _comparison(vectors[cold], vectors[key])})
        except KeyError:
            target = controls if request["mode"] == "response_only" or request["phase"] == "cold" else warm
            target.append({"logical_key": key, "comparison": None, "error": "missing qualified reference vector"})
    checks = [r["comparison"]["values_exact"] if r["comparison"] else None for r in controls]
    return {"status": _status(checks + ([None] if len(controls) != 12 else [])), "cases": controls}, warm


def _protocol(records, cache):
    salts, checks = [], []
    for request in records.values():
        if request["mode"] == "full_input":
            salt = request.get("cache_salt")
            checks.append(salt == f"{request['pair']}:{request['request_id']}" if "cache_salt" in request else None)
            salts.append(salt)
        else:
            checks.append(request["cache_salt"] is None if "cache_salt" in request else None)
    expected_flushes = Counter(("cold", 0, position, mode) for position in range(4) for mode in _MODES)
    expected_flushes.update(("warm_stream", 0, None, mode) for mode in _MODES)
    actual = Counter((r.get("phase"), r.get("repetition"), r.get("sample_position"), r.get("mode")) for r in cache)
    flush_fields_present = all(all(name in r for name in ("phase", "repetition", "mode", "status", "http_status"))
                               and (r["phase"] != "cold" or "sample_position" in r) for r in cache)
    checks += [True if len(records) == 16 else None, len(salts) == len(set(salts)),
               len(salts) == 8 if len(records) == 16 else None,
               actual == expected_flushes if len(cache) >= 10 and flush_fields_present else None,
               all(r["status"] == "flushed" and r["http_status"] == 200 for r in cache) if flush_fields_present else None]
    return {"status": _status(checks), "full_salts": salts, "response_unsalted_count": sum(
        r["mode"] == "response_only" and "cache_salt" in r and r["cache_salt"] is None for r in records.values()),
            "flush_count": len(cache), "flushes": cache}


def _source_controls(result, baseline):
    def argv_without_address(argv):
        i = argv.index("--dist-init-addr")
        return argv[:i] + argv[i + 2:]

    checks = {"same_pair": result["pair"] == baseline["pair"], "first4_rep0": all(r["sample_count"] == 4 and r["repeats"] == 1 for r in (result, baseline)),
              "same_fixture": result["fixture"] == baseline["fixture"] and result["sample_manifest"] == baseline["sample_manifest"],
              "same_native_argv": argv_without_address(result["argv"]) == argv_without_address(baseline["argv"])}
    for name in ("source_preflight", "runtime_metadata_source_preflight"):
        checks[name] = (result[name]["observed_after_sha256"] == baseline[name]["observed_after_sha256"]
                        and bool(result[name]["observed_after_sha256"]))
    for name in ("model_path", "model_manifest_identity", "sglang", "torch", "sglang_environment"):
        checks[name] = result["runtime"][name] == baseline["runtime"][name]
    return {"status": _status(list(checks.values())), "checks": checks,
            "limit": "Existing retained identities compared; no new source hashing or independent loaded/all-TP source proof"}


def inspect_probe(pair, output_dir, baseline_dir):
    """Return controls, request joins, process-scoped isolation and observational deltas."""
    output_dir, baseline_dir = Path(output_dir), Path(baseline_dir)
    report = {"pair": pair, "output_dir": str(output_dir), "baseline_dir": str(baseline_dir),
              "native_completion": None, "cpu_verdict": "UNVERIFIED", "errors": [],
              "limits": "Responding process/rank CPU receipts only; no physical/device/numerical state, all-TP coherence, race or performance proof"}
    try:
        result, baseline = _read(output_dir / "result.json"), _read(baseline_dir / "result.json")
        report["native_completion"] = {name: result.get(name) for name in ("job", "status", "native_measurements_completed", "cleanup_completed")}
        if pair not in ("A", "B") or result["pair"] != pair or baseline["pair"] != pair:
            raise ValueError("pair differs from provided run/baseline")
        if any(r.get("status") != "measurements_completed" or r.get("native_measurements_completed") is not True for r in (result, baseline)):
            raise ValueError("native measurements incomplete; CPU evidence unverified")
        fixture_path = Path(baseline["sample_manifest"]["source_fixture"]["path"])
        if _file_identity(fixture_path) != baseline["sample_manifest"]["source_fixture"]:
            raise ValueError("qualified baseline source fixture identity differs")
        samples = _read(fixture_path)["samples"][:4]
        old_records, old_vectors, old_rids, old_integrity = _request_vectors(baseline_dir, pair, samples)
        records, vectors, by_rid, integrity = _request_vectors(output_dir, pair, samples)
        report.update(request_integrity=integrity, baseline_request_integrity=old_integrity,
                      rid_joins=[{"pair": pair, "native_rid": rid, "logical_key": key} for (_, rid), key in by_rid.items()],
                      source_controls=_source_controls(result, baseline), protocol=_protocol(records, _lines(output_dir / "cache.jsonl")))
        report["vector_controls"], report["warm_full_vs_own_cold"] = _vector_controls(records, vectors, old_vectors)
        report["retractions"] = [{"logical_key": key, "baseline": _retractions(old_records[key]), "candidate": _retractions(request),
                                  "values_equal": _retractions(old_records[key])["value"] == _retractions(request)["value"]
                                  if _retractions(old_records[key])["status"] == _retractions(request)["status"] == "PASS" else None}
                                 for key, request in records.items() if key in old_records]
        report["scopes"] = _metadata(output_dir, records, by_rid, pair)
        old_scopes = _metadata(baseline_dir, old_records, old_rids, pair)
        report["baseline_scopes"] = [{name: scope[name] for name in ("process_id", "rank", "rid_coverage_status")} for scope in old_scopes]
        old_by_rank = {json.dumps(s["rank"], sort_keys=True): s for s in old_scopes}
        deltas = []
        for scope in report["scopes"]:
            old_scope = old_by_rank.get(json.dumps(scope["rank"], sort_keys=True))
            old_chunks = {tuple(r["logical_key"]): r for r in old_scope["chunks"]["requests"]} if old_scope else {}
            for row in scope["chunks"]["requests"]:
                old = old_chunks.get(tuple(row["logical_key"]))
                clean = lambda r: {name: value for name, value in r.items() if name != "sequence"}
                deltas.append({"rank": scope["rank"], "logical_key": row["logical_key"], "baseline": old, "candidate": row,
                               "initial_prefix_equal": old["initial_prefix_len"] == row["initial_prefix_len"] if old else None,
                               "chunk_tracking_equal": [clean(r) for r in old["chunks"]] == [clean(r) for r in row["chunks"]] if old else None})
        report["chunk_tracking_observations"] = deltas
        report["baseline_observation_status"] = "PASS" if (
            all(s["rid_coverage_status"] == s["chunks"]["status"] == "PASS" for s in old_scopes)
            and len(old_scopes) == len(report["scopes"])
            and all(row["baseline"] is not None for row in deltas)) else "UNVERIFIED"
        statuses = [report[name]["status"] for name in ("request_integrity", "baseline_request_integrity", "source_controls", "protocol", "vector_controls")]
        statuses += [r["candidate"]["status"] for r in report["retractions"]] + [r["baseline"]["status"] for r in report["retractions"]]
        statuses.append(report["baseline_observation_status"])
        for scope in report["scopes"]:
            statuses += [scope["rid_coverage_status"], scope["isolation"]["status"], scope["chunks"]["status"]]
        report["cpu_verdict"] = _status([True if s == "PASS" else False if s == "FAIL" else None for s in statuses])
        report["interpretation"] = ("Controls/isolation qualified; inspect each same-run cold-to-warm comparison, not a source fix"
                                    if report["cpu_verdict"] == "PASS" else "INCONCLUSIVE: failed or unverified controls/isolation/evidence")
    except (KeyError, TypeError, ValueError, OSError, IndexError) as error:
        report["errors"].append({"error_type": type(error).__name__, "error": str(error)})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair", choices=("A", "B"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--baseline-dir", type=Path, required=True)
    args = parser.parse_args()
    report = inspect_probe(args.pair, args.output_dir, args.baseline_dir)
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["cpu_verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
