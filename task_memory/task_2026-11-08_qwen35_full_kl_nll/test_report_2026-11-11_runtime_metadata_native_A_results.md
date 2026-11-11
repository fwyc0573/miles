## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Name the JSON reader before calling it in the replay command so the documentation checker does not treat indexed Python calls as Markdown links. Affected replay PASS with unchanged measurements; doc checker retains60 known frozen-copy link errors,0 maintained-document errors and global exit1. |
| 2026-11-11 | Pin scoring-caller replay to immutable4f1139b0 Git blobs; reference primary terminal container/source-annotation evidence without another platform call or measurement change. |
| 2026-11-11 | Independently verify retained A-only native metadata, source identity and all first-four vectors on local CPU; retain warm FAIL and measurement limits. |

# Runtime metadata native A verification

TaskID: `profile-runtime-metadata-native-verification-A-20261111`.

## Outcome

**A reproduces the original selected-FP32 first-four run exactly: 16/16 completion vectors match. Cold parity is 4/4 exact; warm parity is 1/4 exact, so warm numerical acceptance remains FAIL.** This is successful minimized/instrumented reproduction, not a root-cause conclusion, race exclusion, performance acceptance or release of the formal04/05 hold.

Retained terminal receipt: `evidence/teacher-scoring-runtime-metadata-probe-20261111/admission-A-r1.terminal.json`, job `exp-1111-073826-369716`, creator `i-fengyicheng`, Succeeded at `2026-11-10T23:48:55Z`, `native_execution_succeeded=true`. Authoritative probe-end `native/A/admission-A-r1/result.json` records `measurements_completed`, native measurements and cleanup completed, metadata collected, `numerical_acceptance=null`, `performance_accepted=false`. `preload.json`'s initial `status=failed` is the initialization default, not terminal failure. Server shutdown `-9` follows completed measurements; it is not a missing scoring result.

Owned machine-readable result: [native-verification-A.json](evidence/teacher-scoring-runtime-metadata-probe-20261111/native-verification-A.json). Raw inputs remain unchanged; the B/generic report is not edited.

## Acceptance checks

| Check / expected result | Actual result | Verdict |
| --- | --- | --- |
| Actual four H800 and recorded versions | 4 NVIDIA H800, 81559 MiB each, driver570.124.06; worker Python3.12.16 `/opt/sglang/bin/python3`, torch2.14.1+cu130, SGLang0.5.24.dev80+g056f871 | PASS within receipt scope |
| Pinned selected-FP32 math, then metadata overlay | All six selected source before/after hashes and all16 overlay before/after hashes match archived bytes and receipts; math kernel hashes remain unchanged by overlay | PASS, source identity only |
| Original first4, one repetition,16 requests,10 flushes | 16 distinct scored HTTP200 requests/native response IDs,8 comparisons,16 complete finite vectors;10 HTTP200 flushes and10 server flush confirmations | PASS |
| Response identity and zero generation | Original UID/index/token tails retained; placeholder null and correct start ID; full N vs response-only R+1 entries; completion IDs exact, no nonfinite values, output length0 | PASS |
| Original FP32 rep0/first4 reference | Reference-listed path/SHA256 checked, then join on `(pair,phase,mode,source_uid,sample_index,repetition)`;16/16 exact | PASS, minimized reproduction |
| Own cold full-vs-response parity | 4/4 exact; maximum absolute/defined relative error0;6 zero-reference elements have undefined relative error | PASS |
| Own warm correctness against independently flushed cold | Only sample0 exact; sample1 small nonzero differences, sample2/3 substantial nonzero differences below | FAIL |
| Typed metadata and RID coverage | Collected HTTP200; DP1/TP4/PP1, raw `dp_rank=null` legally retained only for DP1; one responding TP0 process339; all16 `(A,native_request_id)` identities have explicit RID-bearing metadata | PASS, DP responder only |

Teacher argv retains TP4/BF16/context131072/concurrency1/chunk8192/fa3/Triton/deterministic/no CUDA graph; all argv values equal old FP32 A except distributed address. Teacher source path is `/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-27B/model`; model-manifest hashes are unchanged. Configured image digest `165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805` is an allocation input, not an independent container-image measurement. Mounted model manifests do not establish whole-weight checksums. `SGLANG_FORCE_COARSE_WAR_BARRIER` remains unset.

Scoring-caller source reference: [native-code-commit.json](evidence/teacher-scoring-runtime-metadata-probe-20261111/native-code-commit.json), SHA256 `2e4eff2caab44d2b6e1505cc0e50be039f7210acef008e9d8d1bbce365819cc5`, commit `4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff`. All six A caller/module byte lengths and hashes match that commit's Git blobs and the native result map's relative-path keys. Replay checks and the in-memory existing probe module use those immutable blobs, never later working-tree caller bytes.

Independent primary evidence: [terminal-platform-containers.json](evidence/teacher-scoring-runtime-metadata-probe-20261111/terminal-platform-containers.json), SHA256 `63f62b487f44b34a0bf9900b5816c0b756f75cc2dd368dd4d600ee1c776ea4ee`, observed `2026-11-10T23:56:25.694462+00:00` through the primary's read-only personal SDK inspection. It records both containers Completed/exit0/restart0; the A receipt confirms the imageID above, requested4 GPUs and source annotation `100.96.128.195:/data/ycfeng:/data/ycfeng`. This independently recorded imageID supplements the worker's allocation-input-only image field; this verifier made no platform call. Empty direct NFS volumes in replicaSpec are not evidence that the annotated source mount was absent. Whole-weight checksums remain unmeasured.

## Exact numerical observations

All identities use UID prefix `00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6`. Errors are raw logprob errors, not probability-space errors. Each cell is **maximum absolute / maximum defined relative error**; relative error is undefined on every zero reference, including0 vs0. No tolerance is introduced. First vector is the reference; own warm comparisons use independently flushed cold vectors, never warm-full as a cold oracle.

| Position / UID suffix / index / N,R | Warm full-vs-response | Cold full-vs-warm full | Cold response-vs-warm response | Zero-reference entries per comparison |
| --- | --- | --- | --- | --- |
| 0 / `:5:123` /1693 /97365,734 | `0 /0` | `0 /0` | `0 /0` | 1 |
| 1 / `:5:125` /1694 /98312,246 | `7.152048056013882e-7 /0.14285706500614642` | `2.3841676011215895e-7 /0.04545451786888886` | `7.152048056013882e-7 /0.14285706500614642` | 1 |
| 2 / `:5:127` /1695 /98942,431 | `0.19622063636779785 /0.6111100632456284` | `0.17278575897216797 /0.2727263348137287` | `0.1781916618347168 /0.9333317481132808` | 1 |
| 3 / `:5:129` /1696 /99074,290 | `0.24439287185668945 /1.3806473175677756` | `0.12412643432617188 /0.6187940669273067` | `0.1765437126159668 /1.0611983494486865` | 3 |

Every old-to-new vector has absolute error0 and defined relative error0, with zero-reference counts1/1/1/3 per sample per phase/mode (24 across16 vectors). The reference manifest precisely lists the16 old A paths and SHA256 values; it is checked rather than assuming file order or inferring omitted vectors. Both sample2/3 warm mode vectors and all own cold-to-warm comparison fields reproduce the original FP32 values exactly. One repetition does not balance both first-mode positions per individual sample; dropped samples4–6 and their1024-hit groups remain unverified by this run.

## Runtime metadata scope

Rows are typed process-local receipts, joined only using explicit `rid`/`rids` and `(pair,native_request_id)`. Request identity, vector identity and metadata coverage are checked independently; count/order matching does not create an association. Sequence is checked only as schema, not treated as GPU execution or cross-request chronology.

The25387 typed rows contain15 event kinds. Temporal-state descriptors are `torch.float32` (24144 appearances); track-state descriptors are `torch.float32` (1872 appearances); index descriptors are `torch.int32`/`torch.int64`. Event-kind/dtype counts and per-RID row coverage are retained in the JSON result, describing this responding process only. `gdn_extend_dispatch`, release/allocator-return and skipped-COW rows lack RID and remain aggregate; no attribution is manufactured from nearby rows or node equality. Physical slot values, tensor contents/storage equality, device store completion and all-TP coverage are **UNMEASURED by design**. Host-enqueue receipts and matching vectors do not establish a producer/consumer/WAR execution chain or historical cause. This report does not duplicate the separate analyzer's RCA.

## Exact local CPU verification

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Verifier: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, `CONDA_DEFAULT_ENV` unset. Standard library plus the pinned probe module loaded in memory from its Git blob; no dependency/environment change, GPU/native execution, platform/auth/SSH/network operation, code/config/science/README edit or separate test script.

The inspected existing helper is named `_comparison`, not `_compare`; `_compare` below aliases that actual helper without reimplementing its math. Exact command:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'from pathlib import Path; p=Path("task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_runtime_metadata_native_A_results.md"); exec(compile(p.read_text().split("```python\n",1)[1].split("\n```",1)[0],str(p)+":verifier","exec"))'
```

```python
import hashlib, json, math, subprocess, sys, types
from collections import Counter, defaultdict
from pathlib import Path
task = Path("task_memory/task_2026-11-08_qwen35_full_kl_nll")
base = task / "evidence/teacher-scoring-runtime-metadata-probe-20261111"
run = base / "native/A/admission-A-r1"
read = lambda p: json.loads(p.read_text())
lines = lambda p: [json.loads(x) for x in p.read_text().splitlines()]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
native_code_receipt_path = base / "native-code-commit.json"
native_code_receipt = read(native_code_receipt_path)
native_code_commit = native_code_receipt["native_code_commit"]
assert native_code_commit == "4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff"
platform_receipt_path = base / "terminal-platform-containers.json"
result, preload, terminal = read(run / "result.json"), read(run / "preload.json"), read(base / "admission-A-r1.terminal.json")
assert result["job"] == terminal["job"] == "exp-1111-073826-369716"
assert terminal["status"]["phase"] == "Succeeded" and terminal["native_execution_succeeded"] is True
assert result["status"] == "measurements_completed" and result["native_measurements_completed"] and result["cleanup_completed"]
assert preload["status"] == "failed" and result["performance_accepted"] is False and result["numerical_acceptance"] is None
assert result["runtime"] == preload["runtime"] and len(result["runtime"]["gpu_devices"]) == 4
assert result["runtime"]["gpu_devices"] == ["NVIDIA H800, 81559 MiB, 570.124.06"] * 4
assert (result["runtime"]["python"], result["runtime"]["sglang"], result["runtime"]["torch"]) == ("3.12.16", "0.5.24.dev80+g056f871", "2.14.1+cu130")
source_counts = {}
for name in ("source_preflight", "runtime_metadata_source_preflight"):
    receipt = result[name]
    assert receipt == preload[name] == lines(run / name / "preflight.jsonl")[0]
    assert read(run / name / "source_manifest.json")["files"] == receipt["files"]
    for relative, info in receipt["files"].items():
        for stage in ("before", "after"):
            assert receipt[f"observed_{stage}_sha256"][relative] == info[f"{stage}_sha256"] == sha(run / name / stage / relative)
    source_counts[name] = len(receipt["files"])
assert source_counts == {"source_preflight": 6, "runtime_metadata_source_preflight": 16}
for relative, identity in result["runtime"]["sglang_sources"].items():
    if relative in result["runtime_metadata_source_preflight"]["observed_after_sha256"]:
        assert identity["sha256"] == result["runtime_metadata_source_preflight"]["observed_after_sha256"][relative]
scoring_reference = next(p for p in native_code_receipt["pairs"] if p["pair"] == "A")
expected_scoring = {f["path"]: f for f in scoring_reference["files"]}
assert scoring_reference["job"] == result["job"] and len(expected_scoring) == 6
assert set(expected_scoring) == set(result["native_scoring_sources"])
scoring_blobs = {}
for relative, identity in result["native_scoring_sources"].items():
    blob = subprocess.check_output(["git", "show", f"{native_code_commit}:{relative}"])
    assert hashlib.sha256(blob).hexdigest() == identity["sha256"] == expected_scoring[relative]["sha256"]
    assert len(blob) == identity["bytes"] == expected_scoring[relative]["bytes"]
    scoring_blobs[relative] = blob
existing_probe = types.ModuleType("pinned_native_teacher_scoring_probe")
exec(compile(scoring_blobs["tests/manual/agent_opd/probe_teacher_scoring.py"], native_code_commit + ":probe_teacher_scoring.py", "exec"), existing_probe.__dict__)
_compare = existing_probe._comparison
native_code_identity = {"receipt": str(native_code_receipt_path), "sha256": sha(native_code_receipt_path), "commit": native_code_commit, "files_verified": 6, "method": "Immutable Git blobs; native result keys are relative paths, not future working-tree bytes"}
platform_receipt = read(platform_receipt_path)
platform_a = next(j for j in platform_receipt["jobs"] if j["pair"] == "A")
container = platform_a["replica_status"]["containerStatuses"][0]
assert platform_a["job"] == result["job"] and platform_a["creator"] == "i-fengyicheng"
assert container["state"]["terminated"]["reason"] == "Completed" and container["state"]["terminated"]["exitCode"] == 0 and container["restartCount"] == 0
assert container["imageID"] == result["runtime"]["configured_image"]
assert platform_a["containers"][0]["resources"]["requests"]["nvidia.com/gpu"] == "4"
assert platform_a["source_annotation"] == "100.96.128.195:/data/ycfeng:/data/ycfeng"
primary_platform_evidence = {"receipt": str(platform_receipt_path), "sha256": sha(platform_receipt_path), "observed_at": platform_receipt["observed_at"], "owner": "Primary read-only personal SDK inspection; no platform call by this verifier", "pair": "A", "container_reason": "Completed", "container_exit_code": 0, "restart_count": 0, "image_id": container["imageID"], "requested_gpus": 4, "source_annotation": platform_a["source_annotation"], "mount_limit": "Empty direct NFS volumes in replicaSpec do not prove the annotated source mount was absent"}
for relative in ("kernels/ops/attention/fla/chunk.py", "srt/layers/attention/linear/kernels/gdn_triton.py"):
    assert result["source_preflight"]["observed_after_sha256"][relative] == result["runtime_metadata_source_preflight"]["observed_before_sha256"][relative] == result["runtime_metadata_source_preflight"]["observed_after_sha256"][relative]
for field in ("fixture", "config"):
    assert result[field] == preload[field] and sha(Path(result[field]["path"])) == result[field]["sha256"]
fixture = Path(result["sample_manifest"]["source_fixture"]["path"])
assert sha(fixture) == result["sample_manifest"]["source_fixture"]["sha256"] == "c45424e8106c2beb7500acacb68aa0939da0088c926af8012dd9fbd780f0ffc9"
samples = read(fixture)["samples"][:4]
requests, cache, comparisons = (lines(run / p) for p in ("requests.jsonl", "cache.jsonl", "comparisons.jsonl"))
assert len(requests) == len({r["request_id"] for r in requests}) == len({r["native_request_id"] for r in requests}) == 16
assert len(cache) == 10 and len(comparisons) == 8 and len(list((run / "completion_scores").glob("*.json"))) == 16
assert all(c["status"] == "flushed" and c["http_status"] == 200 for c in cache)
assert (run / "server.log").read_text().count("Cache flushed successfully!") == 10
vectors, records = {}, {}
key = lambda r: tuple(r[k] for k in ("pair", "phase", "mode", "source_uid", "sample_index", "repetition"))
for r in requests:
    s = samples[r["sample_position"]]; n, length = len(s["tokens"]), s["response_length"]
    start = 0 if r["mode"] == "full_input" else n-length-1
    assert (r["source_uid"], r["sample_index"]) == (s["source_uid"], s["sample_index"])
    assert r["status"] == "scored" and r["http_status"] == 200 and r["native_request_id"] == r["meta_info"]["id"]
    assert (r["input_count"], r["prompt_count"], r["response_count"], r["logprob_start_len"]) == (n, n-length, length, start)
    assert r["input_token_logprobs_count"] == r["expected_input_token_logprobs_count"] == n-start
    assert r["first_input_token_logprob"] is None and r["first_input_token_id"] == r["first_requested_input_token_id"] == s["tokens"][start]
    assert r["returned_completion_count"] == length and r["token_ids_match"] and r["finite_log_probs"]
    assert r["completion_token_id_mismatches"] == r["nonfinite_log_prob_positions"] == []
    assert r["meta_info"]["completion_tokens"] == r["meta_info"]["output_token_logprobs_length"] == 0
    v = read(Path(r["completion_scores"])); assert key(v) == key(r) and v["request_id"] == r["request_id"] and v["native_request_id"] == r["native_request_id"]
    assert v["token_ids"] == s["tokens"][-length:] and len(v["log_probs"]) == length and all(math.isfinite(x) for x in v["log_probs"])
    assert key(r) not in vectors; vectors[key(r)], records[key(r)] = v, r
assert Counter((k[0],k[1],k[2],k[-1]) for k in vectors) == Counter({("A",p,m,0): 4 for p in ("cold","warm_stream") for m in ("full_input","response_only")})
reference_path = base / "original-fp32-first4-reference.json"
reference = next(r for r in read(reference_path)["reference"] if r["pair"] == "A")
assert sha(Path(reference["comparisons_path"])) == reference["comparisons_sha256"]
matched = []
for item in reference["score_files"]:
    p = Path(item["path"]); assert sha(p) == item["sha256"]
    old = read(p); k = ("A",item["phase"],item["mode"],item["source_uid"],item["sample_index"],item["repetition"])
    assert key({"pair": reference["pair"], **old}) == k and item["response_tokens"] == len(old["log_probs"])
    comparison = _compare(old, vectors[k]); assert comparison["values_exact"]
    matched.append({"request_id": records[k]["request_id"], "reference_path": item["path"], "comparison": comparison})
assert len(matched) == 16 and sum(x["comparison"]["relative_error_undefined_count"] for x in matched) == 24
old_result = read(Path(reference["comparisons_path"]).parent / "result.json")
assert result["source_preflight"]["observed_after_sha256"] == old_result["source_preflight"]["observed_after_sha256"]
without_address = lambda a: [v for i,v in enumerate(a) if i == 0 or a[i-1] != "--dist-init-addr"]
assert without_address(result["argv"]) == without_address(old_result["argv"])
assert result["runtime"]["model_manifest_identity"] == old_result["runtime"]["model_manifest_identity"]
own = []
for c in comparisons:
    fk = ("A",c["phase"],"full_input",c["source_uid"],c["sample_index"],0); rk = (fk[0],fk[1],"response_only",*fk[3:])
    assert c["full_request_id"] == records[fk]["request_id"] and c["response_request_id"] == records[rk]["request_id"]
    assert c["full_vs_response_only"] == _compare(vectors[fk],vectors[rk])
    row = {"phase": c["phase"], "sample_index": c["sample_index"], "parity": c["full_vs_response_only"]}
    if c["phase"] == "warm_stream":
        cf, cr = (fk[0],"cold",*fk[2:]), (rk[0],"cold",*rk[2:])
        assert c["cold_reference"]["full_request_id"] == records[cf]["request_id"] and c["cold_reference"]["response_request_id"] == records[cr]["request_id"]
        for label,a,b in (("cold_full_vs_warm_full",cf,fk),("cold_full_vs_warm_response_only",cf,rk),("cold_response_only_vs_warm_full",cr,fk),("cold_response_only_vs_warm_response_only",cr,rk)):
            assert c["cold_reference"][label] == _compare(vectors[a],vectors[b])
        row["full_vs_own_cold"] = c["cold_reference"]["cold_full_vs_warm_full"]
        row["response_vs_own_cold"] = c["cold_reference"]["cold_response_only_vs_warm_response_only"]
    own.append(row)
assert sum(x["parity"]["values_exact"] for x in own if x["phase"] == "cold") == 4
assert sum(x["parity"]["values_exact"] for x in own if x["phase"] == "warm_stream") == 1
metadata = read(run / "runtime_metadata.json")
assert metadata["status"] == result["runtime_metadata"]["status"] == "collected" and metadata["http"]["http_status"] == 200
assert metadata["dp_responses"] == existing_probe._runtime_metadata_states(metadata["server_info"])
assert (metadata["dp_size"],metadata["tp_size"],metadata["pp_size"]) == (1,4,1)
m = metadata["server_info"]["internal_states"][0]["mamba_runtime_metadata"]
assert m["rank"] == {"dp_rank":None,"tp_rank":0,"pp_rank":0,"attn_dp_rank":0,"attn_tp_rank":0}
events, descriptors, coverage = Counter(), Counter(), defaultdict(Counter)
def tensor(v):
    return isinstance(v,list) and len(v)==5 and type(v[0]) is int and isinstance(v[1],str) and v[1].startswith("torch.") and isinstance(v[2],list) and isinstance(v[3],list) and isinstance(v[4],str)
for sequence,event,fields in m["rows"]:
    events[event] += 1; d = dict(fields); assert len(d) == len(fields)
    rids = [d["rid"]] if "rid" in d else d.get("rids",[]) or []
    assert all(isinstance(rid,str) and rid for rid in rids)
    for rid in rids: coverage[("A",rid)][event] += 1
    for field,value in fields:
        if tensor(value):
            assert len(value[2]) == len(value[3]) and all(type(x) is int and x>=0 for x in value[2]+value[3])
            descriptors[(field,value[1])] += 1
assert set(coverage) == {(r["pair"],r["native_request_id"]) for r in requests}
errors = lambda c: [c["max_absolute_error"],c["max_relative_error"],c["relative_error_undefined_count"]]
summary = {"task_id":"profile-runtime-metadata-native-verification-A-20261111","pair":"A","job":result["job"],
    "verification":"PASS: retained evidence consistency and exact first4 reproduction only", "warm_numerical_acceptance":"FAIL", "formal_hold_released":False,
    "cpu_environment":{"executable":sys.executable,"python":sys.version.split()[0]},
    "source_file_counts":source_counts,
    "native_code_identity":native_code_identity,"primary_platform_evidence":primary_platform_evidence,
    "input_sha256":{str(p):sha(p) for p in [reference_path,base/"admission-A-r1.terminal.json",run/"result.json",run/"preload.json",run/"requests.jsonl",run/"cache.jsonl",run/"comparisons.jsonl",run/"runtime_metadata.json",run/"source_preflight/source_manifest.json",run/"runtime_metadata_source_preflight/source_manifest.json"]},
    "checks":{"requests":16,"unique_native_response_ids":16,"flushes":10,"comparisons":8,"finite_complete_vectors":16,"reference_paths_and_hashes_checked":16,"exact_old_to_new_vectors":16,"cold_parity_exact":4,"cold_parity_total":4,"warm_parity_exact":1,"warm_parity_total":4,"rid_covered":16,"reference_zero_relative_errors_undefined":24},
    "reference_join":["pair","phase","mode","source_uid","sample_index","repetition"],
    "reference":"original-fp32-first4-reference.json lists exact score paths/SHA256; old pair identity comes from its A entry",
    "response_identities":[{"request_id":r["request_id"],"native_request_id":r["native_request_id"],"pair":"A","phase":r["phase"],"mode":r["mode"],"source_uid":r["source_uid"],"sample_index":r["sample_index"],"repetition":0,"response_tokens":r["response_count"]} for r in requests],
    "error_columns":["maximum_absolute_logprob_error","maximum_defined_relative_error","undefined_zero_reference_count"],
    "matched_vector_errors":{x["request_id"]:errors(x["comparison"]) for x in matched},
    "own_comparisons":[{"phase":x["phase"],"sample_index":x["sample_index"],**{k:errors(v) for k,v in x.items() if isinstance(v,dict)}} for x in own],
    "metadata":{"process_id":m["process_id"],"rank":m["rank"],"dp_size":1,"tp_size":4,"pp_size":1,"row_count":len(m["rows"]),"event_counts":dict(events),
        "tensor_dtype_counts":[{"field":k[0],"dtype":k[1],"count":v} for k,v in sorted(descriptors.items())],
        "rid_coverage_key":["pair","native_request_id"],"rid_coverage":{rid:{"pair":pair,"row_count":sum(c.values()),"event_kinds":sorted(c)} for (pair,rid),c in coverage.items()},
        "physical_slot_values":"UNMEASURED","device_completion":"UNMEASURED: host enqueue receipts only","all_tp_coverage":"UNMEASURED: one responding TP0 process only"},
    "limits":["No whole-weight checksum; imageID is independent primary SDK evidence, not this verifier's platform call","One repetition; dropped samples4-6/1024-hit groups unverified","No historical cause, WAR execution chain, race exclusion or performance acceptance"]}
assert summary == read(base / "native-verification-A.json")
print("ARTIFACT_MATCH_PASS",len(m["rows"]),"typed rows;",len(coverage),"RID-covered identities;",source_counts)
print("LOCAL_A_EVIDENCE_VERIFICATION_PASS",sys.version.split()[0],"16/16 exact reproduction; warm correctness remains FAIL")
```

Expected: assertions pass,16/16 old-to-new vectors exact, cold4/4 exact, warm1/4 exact, explicit RID coverage16/16; warm acceptance still FAIL. Actual final command: exit0, `ARTIFACT_MATCH_PASS 25387 typed rows; 16 RID-covered identities; {'source_preflight': 6, 'runtime_metadata_source_preflight': 16}` and `LOCAL_A_EVIDENCE_VERIFICATION_PASS 3.12.13 16/16 exact reproduction; warm correctness remains FAIL`. Initial local verifier attempt failed with `KeyError: 'pair'` because original FP32 score files omit that field. The verifier now takes old pair identity from the A reference manifest explicitly; no source file was changed. The JSON artifact is checked for exact equality against the independently recomputed result.

### Provenance follow-up: affected replay only

The full verification above passed before this provenance follow-up. Only its affected caller-source/primary-receipt section was replayed after replacing working-tree caller reads with pinned Git blobs; unaffected vectors, source archives and metadata statistics were not broadly rerun. Expected and actual: exit0, six immutable blobs and A primary-receipt fields match, measurement values unchanged, both owned files pass whitespace checks. Output: `AFFECTED_PINNED_CALLER_REPLAY_PASS 4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff 6 immutable blobs; A primary receipt matches; measurement values unchanged; whitespace PASS`. No stage/commit or platform operation was performed.

Exact affected command:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
from pathlib import Path
p=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_runtime_metadata_native_A_results.md')
code=p.read_text().split('```python\n',1)[1].split('\n```',1)[0]
ns={};exec(compile(code.split('result, preload, terminal =',1)[0],str(p)+':affected-setup','exec'),ns)
read_json=ns['read']
ns['result']=read_json(ns['run']/'result.json')
affected='scoring_reference ='+code.split('scoring_reference =',1)[1].split('for relative in ("kernels/ops/attention/fla/chunk.py"',1)[0]
exec(compile(affected,str(p)+':affected-caller-source','exec'),ns)
a=read_json(ns['base']/'native-verification-A.json')
assert a['native_code_identity']==ns['native_code_identity'] and a['primary_platform_evidence']==ns['primary_platform_evidence']
keys=['checks','response_identities','error_columns','matched_vector_errors','own_comparisons','metadata']
signature=ns['hashlib'].sha256(ns['json'].dumps({k:a[k] for k in keys},sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert signature=='06797cffa7fb51248006bc9e91a69d010c5c800478db4a34347f8c98e1a5c554'
for f in [p,ns['base']/'native-verification-A.json']:
 assert all(s==s.rstrip() for s in f.read_text().splitlines()) and f.read_bytes().endswith(b'\n')
print('AFFECTED_PINNED_CALLER_REPLAY_PASS',ns['native_code_commit'],'6 immutable blobs; A primary receipt matches; measurement values unchanged; whitespace PASS')
PY
```

## Checkpoint

### 1. Planned completion

PASS5, BLOCKED1 within this delegated slice; no platform/GPU action or separate code change.

| Subtask | Status | Evidence |
| --- | --- | --- |
| A source/runtime identity | PASS | Six math and16 overlay archive hashes; recorded four H800/versions. |
| Request integrity | PASS | 16 complete finite vectors/native IDs;10 verified flushes. |
| Original first-four equivalence | PASS | 16 exact vectors and sample2/3 original warm drift. |
| Metadata schema/RID coverage | PASS | 25387 typed rows;16 explicit pair/RID associations. |
| A-only artifacts | PASS | Final CPU recomputation exactly matches JSON. |
| Formal04/05 warm correctness | BLOCKED | Warm1/4 exact; root correction remains with primary/RCA owner. |

### 2. Drift detection

Window: this delegated A-only verification and provenance-only follow-up. Frontier: return A artifacts with immutable caller identity and independently retained primary evidence. Follow-up PASS: six pinned blobs, receipt references and unchanged measurement values; no new verification machinery or broader rerun.

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 Tooling polish | CLEAR | Reused existing CPU helper; no new test machinery. |
| D2 Retry loop | CLEAR | Verification reads retained data; no native reruns or behavior fixes. |
| D3 Side quest | CLEAR | Only assigned A evidence and two owned artifacts. |
| D4 Stalled frontier | CLEAR | B verification and RCA have separate owners; no duplicated work. |
| D5 Gold-plating | CLEAR | No code/config/scientific change or new recorder. |
| D6 Analysis sprawl | CLEAR | Delivered bounded verification; historical interpretation left to analyzer. |
| D7 Off-route | CLEAR | Local CPU only; formal hold and measurement limits retained. |

S1–S4/S6: no scoped defect found. **S5 status refresh:** `requirements.md:74`, `plan.md:52,115` and `tickets/04-a-full.md:42` still describe A GPU/vector evidence as pending; the retained terminal receipt and this completed verification are newer. Primary owns those status updates, not this A-only slice. No execution drift is attributed to this historical snapshot.

### 3. Route correction

Branch B, status-only correction: primary incorporates A's terminal/source/vector/RID results into the current-status sections above while preserving all criteria, decisions, raw receipts and formal hold; no user scope confirmation is needed. This slice leaves those files untouched under exclusive ownership. Stop behavior: none. Return A artifacts; primary integrates independent B/RCA findings before a next authorized diagnostic or formal-admission decision. No formal lift follows.

### 4. Three priorities

1. Original FP32 sample2/3 drift is exactly reproduced despite instrumentation/minimization.
2. Metadata is explicit RID-bound for16 requests but only one responding TP0 process; physical values/device completion/all-TP remain unmeasured.
3. Formal04/05 stay blocked; no root fix or historical race conclusion is claimed.
