## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Incorporate primary075e75ca r2 TP0-only isolation/chunk acceptance, preserve initial false-gate FAIL evidence and numerical values, and record automatic-seed/RNG limits with affected replay on `/usr/bin/python3`3.10.6. |
| 2026-11-11 | Verify A-only native namespace controls, immutable sources and same-run cold references on CPU; leave isolation/decomposition and formal acceptance pending. |

# Cache-salt native A controls

TaskID: `profile-cache-salt-native-controls-A-20261111`.

## Outcome

**Controls PASS: 8/8 unsalted response-only vectors and 4/4 salted cold-full vectors exactly match the qualified baseline. All4 salted warm-full vectors exactly match their own same-run cold-full reference.** Maximum absolute and maximum defined relative errors are0 for every required comparison. No tolerance or full-versus-response acceptance gate is added.

**Primary r2 now accepts ordinary-checkpoint isolation and complete chunk/tracking scope for the responding TP0 process only:**165 conditionally unique bindings PASS;8/8 salted full-input RIDs cover100 isolation joins, all PASS;169 complete chunks and16/16 initial-prefix/chunk-tracking baseline comparisons PASS. Formal04/05 remain held.

With those scoped checks qualified, exact salted warm-full results and unchanged unsalted controls support the bounded namespace observation. They do not establish numerical KV–SSM state/coherence, physical values, all-TP behavior, race exclusion, historical causality, a root fix or performance/formal acceptance. Do not claim identical RNG across runs: the primary reports automatic resolved-seed changes and prefill-only sampler bypass; unretained resolver/worker-chain source collection remains pending. Any actual target-control/isolation failure remains inconclusive without a new tolerance or allowance.

New A: `evidence/teacher-scoring-cache-salt-probe-20261111/native/A/admission-A-r1`, job `exp-1111-083634-351665`. Baseline: `evidence/teacher-scoring-runtime-metadata-probe-20261111/native/A/admission-A-r1`, job `exp-1111-073826-369716`, previously verified against original FP32 first4/rep0. Baseline caller is immutable `4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff`; new caller is immutable `0c6069678032930c79d5ed0f248164d3bdf78c06`. Replay uses Git blobs, not developing working-tree caller files. Owned machine result: [native-verification-A-controls.json](evidence/teacher-scoring-cache-salt-probe-20261111/native-verification-A-controls.json).

## Acceptance checks

| Expected check | Observed result | Verdict |
| --- | --- | --- |
| Native completion, actual4 H800, recorded versions/image | Probe-end `measurements_completed`, measurements/cleanup completed;4 NVIDIA H800,81559 MiB each, driver570.124.06; Python3.12.16 `/opt/sglang/bin/python3`, SGLang0.5.24.dev80+g056f871, torch2.14.1+cu130; pinned image below | PASS within retained receipt scope |
| Immutable source identity | New6 caller files match0c606967 Git blobs; baseline6 match4f1139b0;6 selected-FP32 and16 overlay before/after hashes match their archives and baseline; recorded SGLang sources identical | PASS, source identity only |
| Only full-input namespace intervention | Core caller/5 other files unchanged; probe `_payload` and `_comparison` unchanged;8 distinct salts exactly `A:` + pre-send request ID,8 response-only salts null | PASS |
| Original first4/rep0 and complete request structure | Original UID/index/input token tails retained;16 HTTP200 scored requests,16 unique native response IDs,16 finite complete vectors,10 HTTP200 flushes/10 server confirmations; full N entries and response-only R+1, correct placeholder/start IDs, generation0 | PASS |
| Cache ON and unchanged engine | Same argv except distributed address; BF16,TP4,chunk8192,max-running1,deterministic/no CUDA graph; actual server-info agrees and `disable_radix_cache=false` | PASS |
|8 unsalted response-only controls |8/8 exactly baseline, including the original warm drift | PASS |
|4 salted cold-full controls |4/4 exactly baseline | PASS |
|4 salted warm-full vs own cold-full |4/4 exact; errors0/0, zero-reference relative errors undefined as below | Observed exact under qualified TP0 scope, not causality/formal PASS |
| `num_retractions` | All16 new and16 baseline values are typed nonnegative integers, not bool; all0 and changed-count0 | PASS type check; no unchanged-value gate |
| Metadata availability/raw scope | Collected file;DP1/TP4/PP1, one TP0 process341, raw `dp_rank=null`; explicit RID/rids presence covers16 native IDs | TP0-only receipt scope |
| Primary corrected isolation/chunk inspection |165 bindings PASS; target8 full-input RIDs/100 geometry joins PASS;169 complete chunks and16/16 initial-prefix/chunk-tracking matches | PASS, primary CPU receipt only |

Original source UID prefix: `00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6`.

| Position / UID suffix / index / N,R | Salted warm-full vs own cold-full: max absolute / max defined relative / undefined-zero count | Unsalted warm response vs own cold response: max absolute / max defined relative / undefined-zero count |
| --- | --- | --- |
|0 / `:5:123` /1693 /97365,734 |0 /0 /1 |0 /0 /1 |
|1 / `:5:125` /1694 /98312,246 |0 /0 /1 |7.152048056013882e-7 /0.14285706500614642 /1 |
|2 / `:5:127` /1695 /98942,431 |0 /0 /1 |0.1781916618347168 /0.9333317481132808 /1 |
|3 / `:5:129` /1696 /99074,290 |0 /0 /3 |0.1765437126159668 /1.0611983494486865 /3 |

Errors are raw logprob errors, not probability-space errors. Relative error is undefined whenever the reference is0, including0 vs0. The12 baseline controls contain18 such elements; the4 own-cold warm-full comparisons contain6. Unsalted response warm drift is retained, not treated as failure of its baseline-control gate. Baseline vector identity joins use `(pair,source_uid,sample_index,repetition,phase,mode)`; own-cold references use the same identity with phase=`cold`. Full-versus-response results are not an expected gate for this intervention.

## Independent primary platform evidence and limits

The primary's [initial-platform-verification.json](evidence/teacher-scoring-cache-salt-probe-20261111/initial-platform-verification.json), SHA256 `eaa11a7e4d9b4deab41716f1a7e2e7ddbd9311a3e96f8fea1d779281a3c9c830`, observed `2026-11-11T00:41:12.535123+00:00`, records A creator `i-fengyicheng`,4 requested H800-class GPUs, nonpreemptible allocation, source annotation `100.96.128.195:/data/ycfeng:/data/ycfeng` and configured image `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`. Image identity is the requested/pinned image plus worker runtime receipt, not an independently inspected container imageID or content checksum.

The primary's [admission-A-r1.terminal.json](evidence/teacher-scoring-cache-salt-probe-20261111/admission-A-r1.terminal.json), SHA256 `1b9a1b9288d98a5305f3215c6fccdc6db02f9db7074d11652f112dced6e57d42`, records Succeeded at `2026-11-11T00:40:58Z`, `native_execution_succeeded=true`. This verifier made no GPU/auth/platform/query/poll/SSH/network operation. Probe-end `result.json` is authoritative; preload's initial failed status is not terminal failure, and server shutdown-9 follows complete measurements.

The initial verification here checked only metadata availability, raw rank and explicit RID presence. This follow-up consumes the primary's corrected CPU inspector result; it does not rerun the inspector or recreate native event joins. No physical-slot values, numerical KV state, device completion, all-TP coherence, race exclusion or historical/numerical KV–SSM causality is established. One repetition and the original first4 only leave dropped samples4–6/1024-hit groups unverified. All raw source and measurement files are unchanged; B, other owned reports, code/config/science/README and the inspector implementation were not edited. No stage/commit was performed.

## Corrected primary CPU inspection and RNG observations

Accepted receipt: [native-inspection-A-r2.json](evidence/teacher-scoring-cache-salt-probe-20261111/native-inspection-A-r2.json), SHA256 `612f95ae32e5ca908d332f016fed8a3d548b6c9ecb933c68863f72cdf1e3923f`. Primary ran corrected inspector commit `075e75ca52a613dcbd28ff40686f00d390771bf7` using `/usr/bin/python3`3.10.6; `cpu_verdict=PASS`, source/protocol PASS and12 vector controls PASS. This is independent primary CPU evidence, not this verifier's inspector/platform call.

`scopes[0].isolation.binding_status=PASS` covers165 conditionally unique checkpoint bindings. Its `full_input_isolation` target is8 full-input RIDs, coverage8/8 and100 joins/0 failed. The65 unsalted response-only joins are non-isolated controls:62 geometry PASS and3 FAIL_GEOMETRY observations, all with valid bindings. Their raw `control_observations.status=FAIL` and the raw aggregate `isolation.status=FAIL` remain descriptive, not target gates; only the explicitly targeted full-input scope is accepted. No all-joins geometry PASS is claimed. `chunks.status=PASS` covers169 complete chunks across16 requests; all16 `initial_prefix_equal` and all16 `chunk_tracking_equal` comparisons match baseline.

Initial [native-inspection-A.json](evidence/teacher-scoring-cache-salt-probe-20261111/native-inspection-A.json), SHA256 `cc76e426ab3ad838a4fb460420de39f7815ac03f18f06470354c9ba5ff672730`, remains retained with CPU FAIL as false-gate evidence. Primary reports46 inspector-correction regression checks and36 existing checks PASS; this verifier did not rerun them. Neither receipt is overwritten or relabeled. The inspector correction is not a numerical/root source fix.

Primary-reported retained-source RNG audit: prefill-only scoring bypasses the sampler; automatic seed resolution changes between runs, with A resolved seed observed as474918945 in that audit. This is an attributed source observation, not independent same-RNG verification. Unretained resolver/worker-chain evidence is still pending0-GPU source collection by primary. It introduces no additional hard gate, tolerance, policy allowance or formal acceptance.

## Exact local CPU replay

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Current replay executable is `/usr/bin/python3`, Python3.10.6, not a `python` alias; the original numerical replay used `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`3.12.13. Standard library only, with immutable caller Git blobs for any full replay. This follow-up runs affected receipt/JSON/syntax/whitespace checks only; original finite comparison values stay unchanged. No new test script, environment change or inspector/platform call. A failed target control makes the experiment INCONCLUSIVE; it never relaxes the comparison.

```bash
/usr/bin/python3 -B -c 'from pathlib import Path; p=Path("task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_cache_salt_native_A_results.md"); code=p.read_text().split("```python\n",1)[1].split("\n```",1)[0]; compile(code,str(p)+":replay","exec"); exec(compile(code,str(p)+":replay","exec"))'
```

```python
import ast, hashlib, json, math, subprocess, sys, types
from collections import Counter
from pathlib import Path
task = Path("task_memory/task_2026-11-08_qwen35_full_kl_nll")
base = task / "evidence/teacher-scoring-cache-salt-probe-20261111"
new = base / "native/A/admission-A-r1"
old = task / "evidence/teacher-scoring-runtime-metadata-probe-20261111/native/A/admission-A-r1"
read = lambda p: json.loads(p.read_text())
rows = lambda p: [json.loads(x) for x in p.read_text().splitlines()]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = lambda b: hashlib.sha256(b).hexdigest()
commit = "0c6069678032930c79d5ed0f248164d3bdf78c06"
baseline_commit = "4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff"
git_blob = lambda c,p: subprocess.check_output(["git","show",f"{c}:{p}"])
result, preload, baseline = read(new/"result.json"), read(new/"preload.json"), read(old/"result.json")
terminal = read(base/"admission-A-r1.terminal.json")
platform_path = base/"initial-platform-verification.json"
platform = next(j for j in read(platform_path)["jobs"] if j["pair"] == "A")
assert result["job"] == terminal["job"] == platform["job"] == "exp-1111-083634-351665"
assert terminal["creator"] == platform["creator"] == "i-fengyicheng"
assert terminal["status"]["phase"] == "Succeeded" and terminal["native_execution_succeeded"] is True
assert result["status"] == "measurements_completed" and result["native_measurements_completed"] and result["cleanup_completed"]
assert result["runtime"] == preload["runtime"] and preload["status"] == "failed"
runtime = result["runtime"]
assert runtime["gpu_devices"] == ["NVIDIA H800, 81559 MiB, 570.124.06"]*4
assert (runtime["python"],runtime["sglang"],runtime["torch"]) == ("3.12.16","0.5.24.dev80+g056f871","2.14.1+cu130")
assert runtime["configured_image"] == platform["containers"][0]["image"] == baseline["runtime"]["configured_image"]
assert platform["containers"][0]["limits"]["nvidia.com/gpu"] == "4" and platform["preemptible"] == "no"
assert runtime["model_manifest_identity"] == baseline["runtime"]["model_manifest_identity"]
assert runtime["sglang_sources"] == baseline["runtime"]["sglang_sources"]
assert result["source_preflight"]["selected_fp32"] is True and result["source_preflight"]["snapshot_dtype"] == "float32"
assert result["runtime_metadata_source_preflight"]["selected_fp32_precondition"] is True
sources = {}
for name,count in (("source_preflight",6),("runtime_metadata_source_preflight",16)):
    receipt = result[name]
    assert receipt == preload[name] == rows(new/name/"preflight.jsonl")[0]
    assert read(new/name/"source_manifest.json")["files"] == receipt["files"] and len(receipt["files"]) == count
    for stage in ("before","after"):
        assert receipt[f"observed_{stage}_sha256"] == baseline[name][f"observed_{stage}_sha256"]
        for relative,identity in receipt["files"].items():
            assert sha(new/name/stage/relative) == identity[f"{stage}_sha256"] == receipt[f"observed_{stage}_sha256"][relative]
    sources[name] = count
blobs, caller_identity = {}, {}
for label,c,r in (("new",commit,result),("baseline",baseline_commit,baseline)):
    assert len(r["native_scoring_sources"]) == 6
    blobs[label],caller_identity[label] = {},{}
    for relative,identity in r["native_scoring_sources"].items():
        blob = git_blob(c,relative)
        assert digest(blob) == identity["sha256"] and len(blob) == identity["bytes"]
        blobs[label][relative] = blob
        caller_identity[label][relative] = identity["sha256"]
probe_path = "tests/manual/agent_opd/probe_teacher_scoring.py"
assert {p for p in blobs["new"] if blobs["new"][p] != blobs["baseline"][p]} == {probe_path}
definitions = lambda b: {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(b).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
assert all(definitions(blobs["new"][probe_path])[n] == definitions(blobs["baseline"][probe_path])[n] for n in ("_payload","_comparison"))
probe = types.ModuleType("pinned_cache_salt_probe")
exec(compile(blobs["new"][probe_path],commit+":"+probe_path,"exec"),probe.__dict__)
for name in ("config","fixture"):
    relative = str(Path(result[name]["path"]).relative_to(Path.cwd()))
    blob = git_blob(commit,relative)
    assert digest(blob) == result[name]["sha256"] == preload[name]["sha256"]
    if name == "config": config = json.loads(blob)
    else: manifest = json.loads(blob)
assert config["cache_salt_full_input"] is True and config["selected_fp32_snapshots"] is True and config["mamba_runtime_metadata"] is True
assert config["repeats"] == result["repeats"] == 1 and manifest["sample_count"] == result["sample_count"] == 4
fixture_path = Path(result["sample_manifest"]["source_fixture"]["path"])
assert sha(fixture_path) == result["sample_manifest"]["source_fixture"]["sha256"] == baseline["sample_manifest"]["source_fixture"]["sha256"] == "c45424e8106c2beb7500acacb68aa0939da0088c926af8012dd9fbd780f0ffc9"
samples = read(fixture_path)["samples"][:4]
without_address = lambda a: [v for i,v in enumerate(a) if i == 0 or a[i-1] != "--dist-init-addr"]
assert without_address(result["argv"]) == without_address(baseline["argv"])
info = read(new/"server_info.json")["get_server_info"]
assert (info["dtype"],info["chunked_prefill_size"],info["max_running_requests"],info["disable_radix_cache"]) == ("bfloat16",8192,1,False)
assert info["disable_cuda_graph"] is True and info["enable_deterministic_inference"] is True
requests, baseline_requests = rows(new/"requests.jsonl"), rows(old/"requests.jsonl")
key = lambda r: tuple(r[k] for k in ("pair","source_uid","sample_index","repetition","phase","mode"))
baseline_by_key = {key(r):r for r in baseline_requests}
assert len(requests) == len(baseline_requests) == len(baseline_by_key) == 16
assert len({r["request_id"] for r in requests}) == len({r["native_request_id"] for r in requests}) == 16
assert {key(r) for r in requests} == set(baseline_by_key)
assert Counter((r["phase"],r["mode"],r["repetition"]) for r in requests) == Counter({(p,m,0):4 for p in ("cold","warm_stream") for m in ("full_input","response_only")})
cache = rows(new/"cache.jsonl")
assert len(cache) == 10 and all(c["status"] == "flushed" and c["http_status"] == 200 for c in cache)
assert (new/"server.log").read_text().count("Cache flushed successfully!") == 10
vectors, baseline_vectors, identities, retractions = {},{},{},[]
for r in requests:
    k = key(r); old_request = baseline_by_key[k]; sample = samples[r["sample_position"]]
    n,length = len(sample["tokens"]),sample["response_length"]
    start = 0 if r["mode"] == "full_input" else n-length-1
    assert (r["source_uid"],r["sample_index"]) == (sample["source_uid"],sample["sample_index"])
    assert r["status"] == "scored" and r["http_status"] == 200 and r["native_request_id"] == r["meta_info"]["id"]
    assert (r["input_count"],r["prompt_count"],r["response_count"],r["logprob_start_len"]) == (n,n-length,length,start)
    assert r["input_token_logprobs_count"] == r["expected_input_token_logprobs_count"] == n-start
    assert r["first_input_token_logprob"] is None and r["first_input_token_id"] == r["first_requested_input_token_id"] == sample["tokens"][start]
    assert r["returned_completion_count"] == length and r["token_ids_match"] and r["finite_log_probs"]
    assert r["completion_token_id_mismatches"] == r["nonfinite_log_prob_positions"] == []
    assert r["meta_info"]["completion_tokens"] == r["meta_info"]["output_token_logprobs_length"] == 0
    assert r["request_id"] == f"{r['phase']}-r0-s{r['sample_position']}-{r['mode']}"
    assert r["cache_salt"] == ("A:"+r["request_id"] if r["mode"] == "full_input" else None)
    v,old_v = read(Path(r["completion_scores"])),read(Path(old_request["completion_scores"]))
    assert key(v) == key(old_v) == k and v["native_request_id"] == r["native_request_id"] and v["request_id"] == r["request_id"]
    assert v["token_ids"] == old_v["token_ids"] == sample["tokens"][-length:]
    assert len(v["log_probs"]) == length and all(math.isfinite(x) for x in v["log_probs"])
    vectors[k],baseline_vectors[k] = v,old_v
    identities[r["request_id"]] = {"source_uid":r["source_uid"],"sample_index":r["sample_index"],"phase":r["phase"],"mode":r["mode"],"cache_salt":r["cache_salt"],"native_request_id":r["native_request_id"]}
    a,b = r["meta_info"]["num_retractions"],old_request["meta_info"]["num_retractions"]
    assert type(a) is int and a >= 0 and type(b) is int and b >= 0
    retractions.append({"request_id":r["request_id"],"new":a,"baseline":b,"changed":a != b})
salts = [r["cache_salt"] for r in requests if r["mode"] == "full_input"]
assert len(salts) == len(set(salts)) == 8 and all(type(s) is str and s for s in salts)
assert len(list((new/"completion_scores").glob("*.json"))) == 16
controls, warm, response_drift = {},{},{}
for k,v in vectors.items():
    request_id = v["request_id"]
    if k[-1] == "response_only" or k[-2] == "cold":
        controls[request_id] = probe._comparison(baseline_vectors[k],v)
    if k[-2] == "warm_stream":
        cold = (*k[:4],"cold",k[-1])
        comparison = probe._comparison(vectors[cold],v)
        (warm if k[-1] == "full_input" else response_drift)[request_id] = comparison
response_exact = sum(c["values_exact"] for r,c in controls.items() if r.endswith("response_only"))
cold_exact = sum(c["values_exact"] for r,c in controls.items() if r.endswith("full_input"))
control_pass = response_exact == 8 and cold_exact == 4
metadata_path = new/"runtime_metadata.json"
metadata = read(metadata_path)
assert metadata["status"] == "collected" and (metadata["dp_size"],metadata["tp_size"],metadata["pp_size"]) == (1,4,1)
m = metadata["server_info"]["internal_states"][0]["mamba_runtime_metadata"]
assert m["rank"] == {"dp_rank":None,"tp_rank":0,"pp_rank":0,"attn_dp_rank":0,"attn_tp_rank":0}
present_rids = set()
for _,_,fields in m["rows"]:
    d = dict(fields)
    present_rids.update([d["rid"]] if d.get("rid") else d.get("rids") or [])
inspection_path = base/"native-inspection-A-r2.json"
inspection = read(inspection_path)
assert inspection["pair"] == "A" and inspection["output_dir"] == str(new) and inspection["baseline_dir"] == str(old)
assert inspection["cpu_verdict"] == inspection["source_controls"]["status"] == inspection["protocol"]["status"] == inspection["vector_controls"]["status"] == "PASS"
assert len(inspection["vector_controls"]["cases"]) == 12
scope = inspection["scopes"][0]
isolation = scope["isolation"]
target = isolation["full_input_isolation"]
control_geometry = isolation["control_observations"]
assert len(inspection["scopes"]) == 1 and scope["rank"]["tp_rank"] == 0
assert isolation["binding_status"] == target["status"] == target["coverage_status"] == scope["chunks"]["status"] == "PASS"
assert isolation["ordinary_joined"] == 165 and (target["target_rid_count"],target["covered_rid_count"],target["ordinary_joined"],target["failed_joins"]) == (8,8,100,0)
assert (control_geometry["ordinary_joined"],control_geometry["failed_joins"]) == (65,3)
chunk_count = sum(q["chunk_count"] for q in scope["chunks"]["requests"])
observations = inspection["chunk_tracking_observations"]
assert chunk_count == 169 and len(observations) == 16 and all(o["initial_prefix_equal"] and o["chunk_tracking_equal"] for o in observations)
inspection_evidence = {"path":str(inspection_path),"sha256":sha(inspection_path),"inspector_commit":"075e75ca52a613dcbd28ff40686f00d390771bf7","owner":"Primary corrected inspector call; not this verifier's inspector/platform call","executable":"/usr/bin/python3","python":"3.10.6","cpu_verdict":inspection["cpu_verdict"],"source_controls":inspection["source_controls"]["status"],"protocol":inspection["protocol"]["status"],"vector_controls":12,"checkpoint_binding_status":isolation["binding_status"],"conditionally_unique_checkpoint_bindings":isolation["ordinary_joined"],"full_input_isolation":target,"raw_aggregate_geometry_status":isolation["status"],"control_geometry_status":control_geometry["status"],"control_geometry_role":control_geometry["role"],"control_geometry_joined":65,"control_geometry_passed":62,"control_geometry_failed":3,"complete_chunks":chunk_count,"initial_prefix_matches":sum(o["initial_prefix_equal"] for o in observations),"chunk_tracking_matches":sum(o["chunk_tracking_equal"] for o in observations),"scope":"Responding TP0 CPU receipts only; no physical/numerical state/device/all-TP coherence/race/causality/performance/formal proof","initial_false_gate_evidence":{"path":str(base/"native-inspection-A.json"),"sha256":sha(base/"native-inspection-A.json"),"retained_cpu_verdict":"FAIL"},"primary_reported_tests":{"source_fix_regressions_passed":46,"existing_checks_passed":36,"rerun_by_this_verifier":False}}
rng_observations = {"owner":"Primary-reported retained-source audit; not independently reproduced here","prefill_only_sampler":"Bypassed according to the retained-source audit","source_audit_resolved_seed":474918945,"automatic_resolved_seed_changes":True,"same_rng_claim":False,"unretained_resolver_worker_chain":"PENDING primary 0-GPU source collection","additional_gate_or_tolerance":False}
summary = {"task_id":"profile-cache-salt-native-controls-A-20261111","pair":"A","job":result["job"],"baseline_job":baseline["job"],
    "control_status":"PASS" if control_pass else "FAIL: experiment INCONCLUSIVE", "experiment_interpretation":"TP0-only isolation and complete chunk/tracking scope accepted through primary r2; no same-RNG, root-cause or formal acceptance", "formal_hold_released":False,
    "cpu_environment":{"executable":sys.executable,"python":sys.version.split()[0]},"new_run":str(new),"baseline_run":str(old),
    "source_identity":{"new_commit":commit,"baseline_commit":baseline_commit,"caller_sha256":caller_identity,"archive_file_counts":sources,"baseline_hashes_unchanged":True,"working_tree_caller_read":False},
    "runtime":{"gpu_devices":runtime["gpu_devices"],"python":runtime["python"],"sglang":runtime["sglang"],"torch":runtime["torch"],"configured_image":runtime["configured_image"],"cache_on":True,"dtype":info["dtype"],"chunked_prefill_size":8192,"max_running_requests":1,"argv_matches_baseline_except_distributed_address":True},
    "checks":{"requests":16,"finite_complete_vectors":16,"unique_native_response_ids":16,"flushes":10,"unique_full_input_salts":8,"unsalted_response_controls_exact":response_exact,"unsalted_response_controls_total":8,"salted_cold_controls_exact":cold_exact,"salted_cold_controls_total":4,"salted_warm_own_cold_exact":sum(c["values_exact"] for c in warm.values()),"salted_warm_own_cold_total":4},
    "reference_join":["pair","source_uid","sample_index","repetition","phase","mode"],"request_identities":identities,"baseline_control_comparisons":controls,"salted_warm_full_vs_own_cold_full":warm,"unsalted_response_warm_vs_own_cold_response":response_drift,
    "retractions":{"typed_nonnegative_integer_not_bool":True,"changed_count":sum(r["changed"] for r in retractions),"rows":retractions,"unchanged_value_gate":False},
    "metadata":{"receipt":str(metadata_path),"sha256":sha(metadata_path),"status":"collected","process_id":m["process_id"],"rank":m["rank"],"dp_size":1,"tp_size":4,"pp_size":1,"native_rid_presence":sum(r["native_request_id"] in present_rids for r in requests),"scope":"TP0-only accepted primary r2 isolation/chunk receipt; no native joins rerun by this verifier","ordinary_checkpoint_isolation":"PASS: targeted eight salted full-input RIDs only","full_chunk_decomposition":"PASS: 169 complete chunks and16/16 baseline initial-prefix/chunk-tracking matches","physical_slot_values":"UNMEASURED","device_completion":"UNMEASURED","all_tp_coverage":"UNMEASURED"},
    "primary_inspection":inspection_evidence,"rng_observations":rng_observations,
    "primary_evidence":{"owner":"Primary platform calls, not this verifier","initial":{"path":str(platform_path),"sha256":sha(platform_path)},"terminal":{"path":str(base/"admission-A-r1.terminal.json"),"sha256":sha(base/"admission-A-r1.terminal.json"),"phase":"Succeeded","finish_time":terminal["status"]["finishTime"]}},
    "input_sha256":{label:{name:sha(p/name) for name in ("result.json","preload.json","requests.jsonl","cache.jsonl","server_info.json")} for label,p in (("new",new),("baseline",old))},
    "limits":["Target control/isolation failures are inconclusive; unsalted response geometry FAIL observations are not a target gate","Isolation/chunk acceptance covers responding TP0 CPU receipts only; no numerical KV state or coherence proof","No physical values, device completion, all-TP, race exclusion, causality, source fix, performance or formal PASS","No same-RNG claim; unretained resolver/worker-chain evidence remains pending primary 0-GPU source collection","Image is requested/pinned receipt identity, not independent container-image content checksum; no whole-weight checksum","One repetition, first4 only; dropped samples4-6/1024-hit groups unverified"]}
print("A_CONTROLS_REPLAY",summary["control_status"],summary["checks"],"TP0-only primary r2 isolation/chunk scope PASS")
assert summary == read(base/"native-verification-A-controls.json")
print("A_ARTIFACT_MATCH_PASS")
```

Original full replay before this follow-up: exit0 on Python3.12.13; `A_CONTROLS_REPLAY PASS` with requests16,finite vectors16,native IDs16,flushes10,salts8,response controls8/8,cold controls4/4,warm own-cold4/4, followed by `A_ARTIFACT_MATCH_PASS`. The current full replay above uses explicit `/usr/bin/python3`; it is retained for replay, not broadly rerun in this receipt-only follow-up. Original comparison values and raw-input hashes are unchanged. Syntax/JSON/whitespace check command:

```bash
/usr/bin/python3 -B - <<'PY'
import json
from pathlib import Path
task=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
report=task/'test_report_2026-11-11_cache_salt_native_A_results.md'
artifact=task/'evidence/teacher-scoring-cache-salt-probe-20261111/native-verification-A-controls.json'
code=report.read_text().split('```python\n',1)[1].split('\n```',1)[0]
compile(code,str(report)+':syntax','exec')
json.loads(artifact.read_text())
for p in (report,artifact):
 assert all(line==line.rstrip() for line in p.read_text().splitlines()) and p.read_bytes().endswith(b'\n')
print('A_CONTROLS_SYNTAX_JSON_WHITESPACE_PASS')
PY
```

Expected and actual: exit0, `A_CONTROLS_SYNTAX_JSON_WHITESPACE_PASS`. Neither command writes raw inputs or runs native/platform work.

### Affected r2 receipt replay

Only the new primary-receipt section is executed below. Existing vector/structure/source analysis is not broadly rerun. The signature covers all original finite comparisons,12 controls,4 warm observations, request identities, retractions, raw-input hashes and source/runtime identity. Expected: receipt-derived JSON fields match, numerical fields unchanged, compile/JSON/whitespace PASS. Actual: exit0, `A_R2_AFFECTED_REPLAY_PASS 165 bindings;8 RIDs/100 target joins;169 chunks;16 prefix/tracking matches;unchanged numerical fields`.

```bash
/usr/bin/python3 -B - <<'PY'
from pathlib import Path
report=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_cache_salt_native_A_results.md')
code=report.read_text().split('```python\n',1)[1].split('\n```',1)[0]
compile(code,str(report)+':syntax','exec')
ns={};exec(compile(code.split('result, preload, baseline =',1)[0],str(report)+':affected-setup','exec'),ns)
affected='inspection_path ='+code.split('inspection_path =',1)[1].split('\nsummary =',1)[0]
exec(compile(affected,str(report)+':affected-r2','exec'),ns)
artifact=ns['base']/'native-verification-A-controls.json';a=ns['read'](artifact)
assert a['primary_inspection']==ns['inspection_evidence'] and a['rng_observations']==ns['rng_observations']
assert a['cpu_environment']=={'executable':'/usr/bin/python3','python':'3.10.6'}
assert a['metadata']['ordinary_checkpoint_isolation']=='PASS: targeted eight salted full-input RIDs only'
assert a['metadata']['full_chunk_decomposition']=='PASS: 169 complete chunks and16/16 baseline initial-prefix/chunk-tracking matches'
ids={('A',v['source_uid'],v['sample_index'],0,v['phase'],v['mode']):k for k,v in a['request_identities'].items()}
for c in ns['inspection']['vector_controls']['cases']:
 assert c['comparison']==a['baseline_control_comparisons'][ids[tuple(c['logical_key'])]]
for c in ns['inspection']['warm_full_vs_own_cold']:
 assert c['comparison']==a['salted_warm_full_vs_own_cold_full'][ids[tuple(c['logical_key'])]]
keys=['checks','request_identities','baseline_control_comparisons','salted_warm_full_vs_own_cold_full','unsalted_response_warm_vs_own_cold_response','retractions','input_sha256','runtime','source_identity']
assert ns['digest'](ns['json'].dumps({k:a[k] for k in keys},sort_keys=True,separators=(',',':')).encode())=='e0230b2b4b998e3c53bf97c9abc93be6e9ac7e5362cfa968f4c0aa6efb36d1bf'
for p in (report,artifact):
 assert all(line==line.rstrip() for line in p.read_text().splitlines()) and p.read_bytes().endswith(b'\n')
print('A_R2_AFFECTED_REPLAY_PASS 165 bindings;8 RIDs/100 target joins;169 chunks;16 prefix/tracking matches;unchanged numerical fields')
PY
```

## Checkpoint

### 1. Planned completion

| Scoped subtask | Status | Evidence |
| --- | --- | --- |
| A source/runtime/request structure | PASS | Pinned6+6 caller hashes,6/16 archives,4 H800,16 complete salted/control requests. |
| Baseline controls and own-cold observations | PASS |8/8 response and4/4 cold controls exact;4/4 warm-full observations exact. |
| A-only artifacts/replay | PASS | Exact CPU replay retained here; no other owned file or platform operation. |
| Metadata isolation/full-chunk decomposition | PASS | Primary r2:165 bindings, target100/100 joins,169 chunks and16/16 baseline observations;TP0 only. |
| Unretained resolver/worker-chain evidence | TODO | Primary0-GPU source collection pending; no same-RNG claim or new gate. |
| Formal04/05 correctness acceptance | BLOCKED | No required root/fix acceptance or fresh formal admission. |

### 2. Drift detection

Window: this A-only native-control verification and r2 receipt follow-up. Frontier: return controls plus corrected TP0 isolation/chunk evidence; resolver/worker-chain source collection remains primary-owned.

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 Tooling polish | CLEAR | Existing comparison and bounded report replay only. |
| D2 Retry loop | CLEAR | Retained observations, no GPU reruns or behavior fixes. |
| D3 Side quest | CLEAR | Two explicitly owned A artifacts only. |
| D4 Stalled frontier | CLEAR | Primary delivered r2; this slice consumes it without waiting or delegation. |
| D5 Gold-plating | CLEAR | No code/config/scientific or acceptance expansion. |
| D6 Analysis sprawl | CLEAR | Controls delivered without root interpretation or duplicate RCA. |
| D7 Off-route | CLEAR | Sources pinned, response controls preserved, formal hold retained. |

S1–S4/S6: no scoped defect found. S5: latest `requirements.md:77` still describes local A verification/inspector preparation as in progress and numerical/control/isolation outcome as pending; completed A controls and primary r2 are newer. Primary owns the status refresh; this slice cannot edit those records.

### 3. Route correction

Branch B, status-only correction: primary incorporates A controls/source and r2 TP0-only isolation/chunk acceptance without treating response-only geometry failures as target gates. Stop behavior: none. Return the updated artifacts now; primary continues0-GPU resolver/worker-chain source collection without a same-RNG, causal or root-fix assertion. Formal work remains held.

### 4. Three priorities

1. All12 baseline controls are exact, and all4 salted warm-full observations equal their own cold reference.
2. Unsalted response-only retains original warm drift; this is not a new full-versus-response gate.
3. TP0-only isolation/chunk scope is accepted; resolver/worker evidence and formal acceptance remain unfinished, without physical/coherence or causality claims.
