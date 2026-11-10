## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Independently verify retained native FP32 A/B scoring evidence and matched R1 records on CPU; distinguish operator/source acceptance from warm probability failure. |

# FP32 teacher-scoring results

TaskID: `profile-fp32-probe-native-results-20261111`. Only this report is owned by this task. No code/configuration, original fixture, shared status record or external system is changed.

## Outcome: warm numerical acceptance FAIL

**Both native jobs Succeeded, and cold parity passed, but the selected FP32 source fix alone is insufficient. Formal04/05 remain BLOCKED.** No tolerance, cache-disable, FP32-weight/global-dtype, backend or checkpoint-interval change is accepted or proposed here. `accepted=null`, `numerical_acceptance=null` and `performance_accepted=false` are preserved observations, not PASS labels.

| Pair | Actual job | Native terminal receipt | Finish time, UTC | Raw directory under `evidence/teacher-scoring-fp32-probe-20261111/` |
| --- | --- | --- | --- | --- |
| A | `exp-1111-053300-533764` | `admission-A-r1.terminal.json`: Succeeded | 2026-11-10 22:04:57Z | `native/A/admission-A-r1/` |
| B | `exp-1111-053259-677817` | `admission-B-r1.terminal.json`: Succeeded | 2026-11-10 22:04:25Z | `native/B/admission-B-r1/` |

The actual files are named `admission-*-r1.terminal.json` and `server.log`, not the suggested `terminal-*-r1.json`/`teacher.log`. Native child cleanup records `-9` after all scoring completed; logs show SIGTERM/detokenizer SIGQUIT during cleanup, not a missing scoring result. Each log has32 successful cache flushes and no `ERROR`/`Traceback` line. This is execution completion only.

### Request and source evidence: PASS within stated scope

- Each pair has **56 unique successful HTTP200 scoring requests, 32 HTTP200 flushes, 28 comparisons, 56 actual completion-vector files**. Every phase/repetition/mode covers the same seven UID/index identities once. Both modes retain all input IDs by fixture/config and span receipts; full requested/returned logprobs=`N`, response-only=`R+1`, first placeholder probability=null and ID=`tokens[start]`, completion tail length=`R`, every completion ID equals the fixture and every retained completion probability is finite. Zero generation is recorded for all requests. Full HTTP bodies/input payload arrays were worker-local, so their omitted contents are not independently reconstructed here.
- Each pair returns **2,556,180 input-logprob entries and 92,632 completion scores** across56 requests. These counts include repeated scoring of the same11,579 fixture response tokens; they are not generated trajectories or formal-bank throughput.
- The untouched `evidence/teacher-scoring-probe-20261111/retained-cases.json` is3,703,152 bytes, SHA256 `c45424e8106c2beb7500acacb68aa0939da0088c926af8012dd9fbd780f0ffc9`, matching both new and old preload/result receipts. The seven input records were read only; no original source/input file was rewritten. Full original historical source-file contents are not newly audited.
- Preload and result prove **4 NVIDIA H800 per pair**,81559 MiB/device, driver570.124.06; Python3.12.16 `/opt/sglang/bin/python3`, torch2.14.1+cu130, SGLang0.5.24.dev80+g056f871. A uses Qwen3.5-27B; B Qwen3.5-35B-A3B. Native teacher argv equals its own old R1 except distributed address: TP4/BF16/context131072/concurrency1/chunked prefill8192/fa3/Triton/deterministic/no CUDA graph. Mounted model-manifest hashes are unchanged; no whole-weight checksum is claimed.
- `admission-config-path-correction.json` reconciles the original erroneous relative `probe_config` metadata with unchanged, correct absolute worker `--config`. Original admission SHA256 values match the correction; actual worker input hash is `32708010a8d7dc436faea058b862b0e241252ca74daca35db08c4e35850a6fa9`. No stop/resubmit or original-receipt overwrite is inferred.
- Real preflight receipt equals preload/result and archive, selected_fp32=true. **All six actual archived after-file SHA256 values match the separate operator worker's six actual files and receipt**, not only the summary boolean in `deployed-source-verification.json`. Two files changed; the other four were unchanged. The image digest remains an allocation input, not an independent container-image inspection.

| Native source relative to SGLang root | Verified after SHA256 in A, B and operator |
| --- | --- |
| `kernels/ops/attention/fla/chunk.py` | `b2c1cd76ab3558b893e082f07a8c587520e624e9988d19c0c1afa4f32a72e43c` |
| `srt/layers/attention/linear/kernels/gdn_triton.py` | `7060585d86347561a2caf36492163b584152e32efddea17b5b4cc8c33c5774bf` |
| `kernels/ops/attention/fla/chunk_delta_h.py` | `e37fa6885dd50e945fb470ef3b858573f812c2d7590ed8decc627f15f4bea1c2` |
| `srt/layers/attention/linear/kernels/kernel_backend.py` | `bb75a7e69b7c3fdc5274137f215a0118ef8f999db4c9175e871953db33bd8505` |
| `srt/layers/attention/linear/gdn_backend.py` | `04f4d78226b0c91e97fe5b1768ccba2719bcf1996faffb32e37ef580d66fab13` |
| `srt/layers/attention/hybrid_linear_attn_backend.py` | `e6f797a346bf7534026c963188e7383ec5eded10b94a75811ddb7867cc9980ef` |

The standalone H800 operator job `exp-1111-055011-398371` has **44/44 passed checks**, independently read from `evidence/snapshot-semantics-20261111/exp-1111-055011-398371/verdict.json`:192/193-token operator cases,64/128-token prefixes, exact unchanged normal output/h/state, exact native-prefix snapshots, skipped rows unchanged and524,283 elements showing FP32 stores are not a BF16 roundtrip. Its runtime tensor metadata belongs to that operator only. The earlier source-preflight `cuda_semantics=UNVERIFIED` intentionally remains unchanged: it was source-only evidence. Neither label establishes full-model warm acceptance or R1 race exclusion.

### Exact real fixture identities and numerical results

All UIDs share prefix `00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6`; table values append the displayed suffix. Every result covers both repetitions. Each cell below is `(warm full-vs-response, warm full-vs-own cold, warm response-vs-own cold)` maximum absolute logprob error; **0 alone means exact**. Small nonzero cases are retained, with no tolerance/exclusion.

| Position | UID suffix | Sample index | Input N / response R | A absolute errors | B absolute errors |
| --- | --- | --- | --- | --- | --- |
| 0 | `:5:123` | 1693 | 97365 /734 | `(0,0,0)` | `(0,0,0)` |
| 1 | `:5:125` | 1694 | 98312 /246 | `(7.152048056013882e-7,2.3841676011215895e-7,7.152048056013882e-7)` | `(2.9801958589814603e-6,4.529893885774072e-6,3.4569602576084435e-6)` |
| 2 | `:5:127` | 1695 | 98942 /431 | `(0.19622063636779785,0.17278575897216797,0.1781916618347168)` | `(0.33083581924438477,0.43444275856018066,0.5321998596191406)` |
| 3 | `:5:129` | 1696 | 99074 /290 | `(0.24439287185668945,0.12412643432617188,0.1765437126159668)` | `(0.24397611618041992,0.4388699531555176,0.3178117275238037)` |
| 4 | `:13:123` | 1569 | 113743 /8124 | `(0,0,0)` | `(0,0,0)` |
| 5 | `:19:119` | 1607 | 116053 /1687 | `(0.2263340950012207,0,0.2263340950012207)` | `(0.43827223777770996,0,0.43827223777770996)` |
| 6 | `:32:2` | 1786 | 3970 /67 | `(0.11421060562133789,0,0.11421060562133789)` | `(0.12258267402648926,0,0.12258267402648926)` |

Cold full-versus-response is **14/14 exact** for both pairs: absolute/nonzero-reference relative errors0, with52(A)/90(B) zero-reference elements where relative error is undefined. For all following distributions, minimum absolute error=0; quantiles are over14 per-vector maximum errors, not pooled tokens. Relative maximum excludes zeros, which are separately counted. Scores are raw logprobs, not probability-space errors.

| Pair / warm comparison | Exact /14 | Absolute q25 / median / q75 | Absolute maximum | Relative maximum | Zero-reference elements (undefined) |
| --- | --- | --- | --- | --- | --- |
| A full-vs-response | 4 | `1.7880120140034705e-7 /0.11421060562133789 /0.218805730342865` | **0.24439287185668945** | 1.3806473175677756 | 52 |
| A full-vs-own cold | 8 | `0 /0 /0.09309488534881893` | **0.17278575897216797** | 0.6187940669273067 | 52 |
| A response-vs-own cold | 4 | `1.7880120140034705e-7 /0.11421060562133789 /0.1777796745300293` | **0.2263340950012207** | 1.0611983494486865 | 52 |
| B full-vs-response | 4 | `7.450489647453651e-7 /0.12258267402648926 /0.30912089347839355` | **0.43827223777770996** | 10.83576074484674 | 92 |
| B full-vs-own cold | 8 | `0 /0 /0.32583320139360694` | **0.4388699531555176** | 12.818066557496891 | 90 |
| B response-vs-own cold | 4 | `8.642400644021109e-7 /0.12258267402648926 /0.4081571102142334` | **0.5321998596191406** | 12.296145876202624 | 90 |

Repetitions0 and1 agree **7/7 exactly for each pair/phase/mode**. Thus each repetition separately has2/7 warm parity,4/7 warm full-vs-cold and2/7 warm response-vs-cold. Reproducibility does not make the wrong warm result acceptable. Matching cold request IDs, both modes and all four cold-to-warm comparison fields were recomputed against actual vector files by pair/repetition/UID/index; warm-full was never the cold oracle.

### Matched untouched R1: raw vectors, no inferred scores

Baseline jobs: A `exp-1111-033133-704472`, B `exp-1111-033134-236473`, under `evidence/teacher-scoring-probe-20261111/native/{A,B}/admission-*-r1/`. All56 actual vectors per pair are present and matched by phase/mode/repetition/UID/index. **Both cold modes and warm-full are14/14 exact old-versus-new for each pair**. Warm-response is only6/14 exact; changed identities are`:5:127`,`:5:129`,`:19:119`,`:32:2`, both repetitions. No historical A score is used for B.

| Pair / warm-response old-to-new | Exact /14 | Absolute q25 / median / q75 / max | Relative maximum | Zero-reference elements |
| --- | --- | --- | --- | --- |
| A | 6 | `0 /0.11418414115905762 /0.1414662003517151 /0.18626999855041504` | 1.9999997019767584 | 52 |
| B | 6 | `0 /0.16890943050384521 /0.5154909491539001 /0.9972515106201172` | 9.833257158542827 | 92 |

R1 already had4/14 warm parity,8/14 warm-full-vs-cold and4/14 warm-response-vs-cold. A parity maximum changed0.2006068229675293→0.24439287185668945 and response-vs-cold0.19129133224487305→0.2263340950012207. B parity maximum changed1.0602149963378906→0.43827223777770996 and response-vs-cold1.0602149963378906→0.5321998596191406. Full-vs-cold maxima are unchanged. B's lower maximum is descriptive partial movement, not acceptance, proof of the original cause, or a uniformly improved result; its`:5:127` response-vs-cold error increased0.4055359363555908→0.5321998596191406.

### Sequential request latency and transferred bytes: observations only

Each row matches14 requests, including both repetitions. Times are client `elapsed_seconds`, including request encoding, headers/server work, body read, parse and tail validation; they exclude engine startup and flush time. Relative change=`(new-old)/old`. No formal256-slot bank, concurrent teacher queue, global rollout/teacher bottleneck, controlled speedup or performance PASS is inferred.

| Pair / phase / mode | Old→new total seconds | Absolute / relative change | Old→new median seconds | Old→new p95 seconds | New min–max seconds |
| --- | --- | --- | --- | --- | --- |
| A cold full | 81.735035→82.335828 | +0.600793 /+0.7350% | 5.291266→5.260955 | 12.199672→12.828948 | 0.217302–13.173319 |
| A cold response | 65.090545→65.900004 | +0.809459 /+1.2436% | 4.554808→4.674753 | 7.609397→7.966629 | 0.190560–8.358280 |
| A warm full | 67.250876→67.884565 | +0.633690 /+0.9423% | 5.281543→5.254538 | 6.298536→6.415944 | 0.220242–6.564704 |
| A warm response | 39.918204→41.462572 | +1.544367 /+3.8688% | 2.297259→2.460317 | 6.712826→6.913418 | 0.143409–9.752187 |
| B cold full | 48.671685→48.342849 | -0.328836 /-0.6756% | 2.679382→2.645477 | 8.521892→8.361958 | 0.144914–12.857103 |
| B cold response | 32.354768→31.526321 | -0.828447 /-2.5605% | 1.681279→1.670928 | 6.515514→6.403760 | 0.117915–7.175917 |
| B warm full | 31.801511→30.218744 | -1.582768 /-4.9770% | 2.558747→2.364571 | 2.929485→2.844452 | 0.145747–2.865427 |
| B warm response | 28.618856→27.501808 | -1.117048 /-3.9032% | 1.554063→1.600649 | 6.848471→6.450597 | 0.110075–7.655124 |

Latency repetitions differ despite identical vectors: new warm-response totals r0/r1 are25.384543/16.078029s(A) and21.362484/6.139324s(B). Order/initial-work effects are not isolated; neither timing variance nor cold first-call costs are assigned a cause here.

| Pair / phase / mode | Actual returned input-logprobs / completion scores | Old→new decoded body bytes | New header / body-read / JSON-parse total seconds |
| --- | --- | --- | --- |
| A cold full | 1,254,918 /23,158 | 41,009,031→41,009,039 | 81.629182 /0.021684 /0.591332 |
| A cold response | 23,172 /23,158 | 782,853→782,849 | 65.601520 /0.000646 /0.011410 |
| A warm full | 1,254,918 /23,158 | 41,009,043→41,009,038 | 67.141829 /0.023585 /0.541861 |
| A warm response | 23,172 /23,158 | 783,033→783,040 | 41.385356 /0.000846 /0.013122 |
| B cold full | 1,254,918 /23,158 | 41,068,473→41,068,473 | 47.432451 /0.018346 /0.806795 |
| B cold response | 23,172 /23,158 | 781,199→781,196 | 31.453890 /0.000724 /0.011530 |
| B warm full | 1,254,918 /23,158 | 41,068,503→41,068,508 | 29.362811 /0.019433 /0.568643 |
| B warm response | 23,172 /23,158 | 781,429→781,545 | 27.425641 /0.000751 /0.013010 |

Counts are unchanged old-to-new. Full/cold cached-token receipts are0. Warm-response cached tokens per repetition are `[0,90112,96576,96576,0,1024,1024]`, identical for old/new A/B. Cached-token counts are not donor/KV equivalence measurements; warm-full cached0 does not establish an uncontaminated canonical state.

### Missing evidence and unchanged D40 boundary

Full-model live donor/state measurements are **missing**: no retained donor row IDs/version/initial values, selected snapshot tensor dtype/shape/stride/storage identity, live kernel forwarding/store event, canonical KV/state rebind contents, actual grid selection per request, or producer/consumer/WAR runtime event chain. Operator measurements cannot be copied into these absent fields. Full HTTP bodies and compiled binaries remain worker-local/unavailable; original source preflight is source-only. The candidate therefore cannot close the warm-state root cause, model probability correctness, race exclusion or formal-bank performance requirement. D39/D34/fixed256/32×8/231/1800s/600s/200/S7 and existing teacher/protocol settings remain unchanged.

## Reproducible local verification

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Verifier environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, standard library only; no conda change, dependency install or native/GPU import. This task performs no GPU/platform/auth/SSH/network operation or delegation. The successful verification and scoped formatting checks are report acceptance only; native warm acceptance is FAIL.

Exact command (executes the first Python fence below without writing a script or modifying any evidence):

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'from pathlib import Path; p=Path("task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_fp32_teacher_scoring_results.md"); code=p.read_text().split("```python\n",1)[1].split("\n```",1)[0]; exec(compile(code,str(p)+":verifier","exec"))'
```

The following standard-library verifier reads only retained local evidence. Its successful exit verifies evidence consistency, **not warm numerical acceptance**. All probability differences use the first vector as reference: absolute error `abs(candidate-reference)` and relative error divided by `abs(reference)` only when reference is nonzero. Zero-reference relative errors are undefined, including `0` versus `0`. Quartiles use linear interpolation at `(n-1)*p`; per-case distributions summarize each completion vector's maximum error.

```python
import hashlib
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

task = Path("task_memory/task_2026-11-08_qwen35_full_kl_nll")
evidence = task / "evidence"
new = evidence / "teacher-scoring-fp32-probe-20261111"
old = evidence / "teacher-scoring-probe-20261111"
read = lambda path: json.loads(path.read_text())
lines = lambda path: [json.loads(line) for line in path.read_text().splitlines()]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
fixture_path = old / "retained-cases.json"
fixture_hash = sha(fixture_path)
assert fixture_hash == "c45424e8106c2beb7500acacb68aa0939da0088c926af8012dd9fbd780f0ffc9"
samples = read(fixture_path)["samples"]
assert len(samples) == len({(s["source_uid"], s["sample_index"]) for s in samples}) == 7
op_dir = evidence / "snapshot-semantics-20261111/exp-1111-055011-398371"
operator = read(op_dir / "verdict.json")
assert operator["status"] == operator["cuda_semantics"] == "PASS"
assert len(operator["checks"]) == 44 and all(c["passed"] is True for c in operator["checks"].values())
assert operator["failed_checks"] == []
operator_hashes = operator["source_preflight"]["observed_after_sha256"]
assert len(operator_hashes) == 6
for relative, expected in operator_hashes.items():
    assert sha(op_dir / "source_preflight/after" / relative) == expected

def quantile(values, fraction):
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    return ordered[lower] + (ordered[min(lower + 1, len(ordered) - 1)] - ordered[lower]) * (position - lower)

def difference(reference, candidate):
    assert reference["token_ids"] == candidate["token_ids"]
    a, b = reference["log_probs"], candidate["log_probs"]
    assert len(a) == len(b) and all(math.isfinite(x) for x in a + b)
    absolute = [abs(y - x) for x, y in zip(a, b)]
    relative = [error / abs(x) for error, x in zip(absolute, a) if x != 0]
    return {"exact": a == b, "abs": max(absolute), "rel": max(relative) if relative else None,
            "undefined": sum(x == 0 for x in a), "different_tokens": sum(x != y for x, y in zip(a, b))}

def distribution(items):
    absolute = [item["abs"] for item in items]
    relative = [item["rel"] for item in items if item["rel"] is not None]
    return {"exact": sum(item["exact"] for item in items), "n": len(items),
            "abs_min_q25_median_q75_max": [quantile(absolute, p) for p in (0, .25, .5, .75, 1)],
            "max_relative": max(relative) if relative else None,
            "zero_reference_elements": sum(item["undefined"] for item in items),
            "different_tokens": sum(item["different_tokens"] for item in items)}

def load_run(parent, pair):
    directory = parent / "native" / pair / f"admission-{pair}-r1"
    result, preload = read(directory / "result.json"), read(directory / "preload.json")
    requests, cache, comparisons = (lines(directory / name) for name in ("requests.jsonl", "cache.jsonl", "comparisons.jsonl"))
    assert len(requests) == len({r["request_id"] for r in requests}) == 56 and len(comparisons) == 28
    assert len(cache) == 32 and all(r["status"] == "flushed" and r["http_status"] == 200 for r in cache)
    assert (directory / "server.log").read_text().count("Cache flushed successfully!") == 32
    assert result["status"] == "measurements_completed" and result["native_measurements_completed"] is True
    assert result["performance_accepted"] is False and result["numerical_acceptance"] is None
    assert preload["fixture"]["sha256"] == result["fixture"]["sha256"] == fixture_hash
    assert preload["runtime"] == result["runtime"]
    assert result["pair"] == pair and len(result["runtime"]["gpu_devices"]) == 4
    assert all("H800" in device for device in result["runtime"]["gpu_devices"])
    vectors, records = {}, {}
    for r in requests:
        sample = samples[r["sample_position"]]
        uid = (r["source_uid"], r["sample_index"])
        assert uid == (sample["source_uid"], sample["sample_index"])
        key = (r["phase"], r["repetition"], *uid, r["mode"])
        assert key not in vectors and r["repetition"] in (0, 1)
        n, response = len(sample["tokens"]), sample["response_length"]
        start = 0 if r["mode"] == "full_input" else n - response - 1
        assert r["logprob_start_len"] == start and r["input_count"] == n
        assert r["prompt_count"] == n - response and r["response_count"] == response
        assert r["expected_input_token_logprobs_count"] == r["input_token_logprobs_count"] == n - start
        assert r["first_input_token_logprob"] is None
        assert r["first_input_token_id"] == r["first_requested_input_token_id"] == sample["tokens"][start]
        assert r["status"] == "scored" and r["http_status"] == 200
        expected_cache = "cold_flushed" if r["phase"] == "cold" else ("stream_first_after_flush" if r["sample_position"] == 0 else "ordered_stream_after_flush")
        assert r["cache_state"] == expected_cache
        assert r["token_ids_match"] is True and r["finite_log_probs"] is True
        assert r["returned_completion_count"] == response and r["completion_token_id_mismatches"] == []
        assert r["nonfinite_log_prob_positions"] == [] and int(r["content_length_header"]) == r["body_bytes"]
        assert r["meta_info"]["completion_tokens"] == r["meta_info"]["output_token_logprobs_length"] == 0
        vector = read(Path(r["completion_scores"]))
        assert all(vector[k] == r[k] for k in ("phase", "repetition", "source_uid", "sample_index", "mode", "request_id"))
        assert vector["token_ids"] == sample["tokens"][-response:] and len(vector["log_probs"]) == response
        assert all(math.isfinite(value) for value in vector["log_probs"])
        vectors[key], records[key] = vector, r
    assert Counter((key[0], key[1], key[-1]) for key in vectors) == Counter({(p, r, m): 7 for p in ("cold", "warm_stream") for r in (0, 1) for m in ("full_input", "response_only")})
    for c in comparisons:
        uid = (c["source_uid"], c["sample_index"])
        full_key = (c["phase"], c["repetition"], *uid, "full_input")
        response_key = (*full_key[:-1], "response_only")
        assert c["full_request_id"] == records[full_key]["request_id"] and c["response_request_id"] == records[response_key]["request_id"]
        measured = difference(vectors[full_key], vectors[response_key])
        stored = c["full_vs_response_only"]
        assert [stored[k] for k in ("values_exact", "max_absolute_error", "max_relative_error", "relative_error_undefined_count")] == [measured[k] for k in ("exact", "abs", "rel", "undefined")]
        assert stored["accepted"] is None and (pair == "A" or c["historical_expected"] is None)
        if parent == new and c["phase"] == "warm_stream":
            assert c["pair"] == pair
            cold = c["cold_reference"]
            cf, cr = ("cold", c["repetition"], *uid, "full_input"), ("cold", c["repetition"], *uid, "response_only")
            assert cold["full_request_id"] == records[cf]["request_id"] and cold["response_request_id"] == records[cr]["request_id"]
            for label, a, b in (("cold_full_vs_warm_full", cf, full_key), ("cold_full_vs_warm_response_only", cf, response_key), ("cold_response_only_vs_warm_full", cr, full_key), ("cold_response_only_vs_warm_response_only", cr, response_key)):
                measured, stored = difference(vectors[a], vectors[b]), cold[label]
                assert [stored[k] for k in ("values_exact", "max_absolute_error", "max_relative_error", "relative_error_undefined_count")] == [measured[k] for k in ("exact", "abs", "rel", "undefined")]
                assert stored["accepted"] is None
    return directory, result, preload, vectors, records

for pair in "AB":
    directory, result, preload, vectors, records = load_run(new, pair)
    _, baseline, _, old_vectors, old_records = load_run(old, pair)
    admission = read(new / f"admission-{pair}-r1.json")
    terminal = read(new / f"admission-{pair}-r1.terminal.json")
    assert admission["job"] == terminal["job"] == result["job"]
    assert terminal["creator"] == "i-fengyicheng" and terminal["status"]["phase"] == "Succeeded"
    correction = next(r for r in read(new / "admission-config-path-correction.json")["records"] if r["pair"] == pair)
    assert sha(new / f"admission-{pair}-r1.json") == correction["original_receipt_sha256"]
    assert preload["config"]["path"] == correction["worker_config"] and sha(Path(correction["worker_config"])) == correction["worker_config_sha256"]
    assert f"--config {correction['worker_config']} " in admission["worker_command"]
    receipt = result["source_preflight"]
    assert receipt == preload["source_preflight"] == lines(directory / "source_preflight/preflight.jsonl")[0]
    assert receipt["selected_fp32"] is True and receipt["cuda_semantics"] == "UNVERIFIED"
    assert receipt["observed_after_sha256"] == operator_hashes
    for relative, expected in operator_hashes.items():
        assert sha(directory / "source_preflight/after" / relative) == expected
    def argv_without_address(argv):
        return [value for position, value in enumerate(argv) if position == 0 or argv[position - 1] != "--dist-init-addr"]
    assert argv_without_address(result["argv"]) == argv_without_address(baseline["argv"])
    assert result["runtime"]["model_manifest_identity"] == baseline["runtime"]["model_manifest_identity"]
    print("SOURCE_SCOPE_PASS", pair, result["job"], "4H800; 56 requests; 32 flushes; six after hashes; 44 operator checks")
    for phase in ("cold", "warm_stream"):
        for metric in ("full_vs_response", "full_vs_own_cold", "response_vs_own_cold"):
            items, old_items = [], []
            for repetition in (0, 1):
                for sample in samples:
                    uid = sample["source_uid"], sample["sample_index"]
                    full, response = (phase, repetition, *uid, "full_input"), (phase, repetition, *uid, "response_only")
                    a, b = (full, response) if metric == "full_vs_response" else (("cold", repetition, *uid, full[-1] if metric.startswith("full") else response[-1]), full if metric.startswith("full") else response)
                    items.append(difference(vectors[a], vectors[b]))
                    old_items.append(difference(old_vectors[a], old_vectors[b]))
            print("NUMERICAL", pair, phase, metric, json.dumps(distribution(items)))
            if phase == "warm_stream":
                print("R1_NUMERICAL", pair, metric, json.dumps(distribution(old_items)))
                expected = {"A": {"full_vs_response": (4, 0.24439287185668945), "full_vs_own_cold": (8, 0.17278575897216797), "response_vs_own_cold": (4, 0.2263340950012207)}, "B": {"full_vs_response": (4, 0.43827223777770996), "full_vs_own_cold": (8, 0.4388699531555176), "response_vs_own_cold": (4, 0.5321998596191406)}}[pair][metric]
                assert (sum(item["exact"] for item in items), max(item["abs"] for item in items)) == expected
            elif metric == "full_vs_response":
                assert all(item["exact"] and item["abs"] == 0 for item in items)
    for mode in ("full_input", "response_only"):
        repeat_items = [difference(vectors[(phase, 0, s["source_uid"], s["sample_index"], mode)], vectors[(phase, 1, s["source_uid"], s["sample_index"], mode)]) for phase in ("cold", "warm_stream") for s in samples]
        print("REPETITIONS", pair, mode, "cold", json.dumps(distribution(repeat_items[:7])), "warm", json.dumps(distribution(repeat_items[7:])))
    assert set(old_vectors) == set(vectors)
    for phase in ("cold", "warm_stream"):
        for mode in ("full_input", "response_only"):
            keys = [key for key in vectors if key[0] == phase and key[-1] == mode]
            matched = [difference(old_vectors[key], vectors[key]) for key in keys]
            rows = [records[key] for key in keys]
            previous = [old_records[key] for key in keys]
            print("MATCHED_R1", pair, phase, mode, json.dumps(distribution(matched)))
            delta = sum(row["elapsed_seconds"] for row in rows) - sum(row["elapsed_seconds"] for row in previous)
            ratios = [records[key]["elapsed_seconds"] / old_records[key]["elapsed_seconds"] for key in keys]
            print("LATENCY_CHANGE", pair, phase, mode, "absolute_seconds", delta, "relative", delta / sum(row["elapsed_seconds"] for row in previous), "matched_ratio_min_median_max", [min(ratios), statistics.median(ratios), max(ratios)])
            print("LATENCY_REPETITIONS", pair, phase, mode, "r0_r1", [sum(row["elapsed_seconds"] for row in rows if row["repetition"] == r) for r in (0, 1)])
            for label, selection in (("old", previous), ("fp32", rows)):
                times = [row["elapsed_seconds"] for row in selection]
                print("PERFORMANCE", pair, phase, mode, label, json.dumps({"seconds_sum": sum(times), "seconds_min_p50_p95_max": [quantile(times, p) for p in (0, .5, .95, 1)], "headers_seconds_sum": sum(row["http_time_to_headers_seconds"] for row in selection), "read_seconds_sum": sum(row["body_read_seconds"] for row in selection), "parse_seconds_sum": sum(row["json_parse_seconds"] for row in selection), "returned_input_logprobs": sum(row["input_token_logprobs_count"] for row in selection), "completion_scores": sum(row["returned_completion_count"] for row in selection), "body_bytes": sum(row["body_bytes"] for row in selection), "cached_tokens": [row["meta_info"]["cached_tokens"] for row in selection]}))
assert sha(fixture_path) == fixture_hash
print("LOCAL_EVIDENCE_VERIFICATION_PASS", sys.version.split()[0], "warm acceptance remains FAIL")
```

Observed command result: exit0, `SOURCE_SCOPE_PASS` for both jobs and `LOCAL_EVIDENCE_VERIFICATION_PASS 3.12.13 warm acceptance remains FAIL`. The raw counts, independent cold references, all numerical summary fields, fixture checksum, original admission checksum, actual config identity, unchanged argv/model manifests and18 actual source-after files pass the verifier's assertions. No missing vector was filled or inferred. Initial exploratory inspection incorrectly treated the operator's `checks` mapping as a list (`KeyError: slice(None, 2, None)`); the verified command reads its actual44-entry mapping. That reader error was not a native run failure.

Additional exact scoped checks (expected and observed: PASS; AST3.10 is syntax compatibility, not Python3.10 execution):

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import ast
from pathlib import Path
p=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_fp32_teacher_scoring_results.md')
text=p.read_text()
code=text.split('```python\n',1)[1].split('\n```',1)[0]
ast.parse(code,filename=str(p)+':verifier',feature_version=(3,10))
assert all(line == line.rstrip() for line in text.splitlines())
assert text.startswith('## Modification History\n')
assert all(text.count(f'## {i}. ') == 1 for i in range(1,5))
print('PASS: verifier AST Python3.10; report whitespace, Modification History and four-section checkpoint')
PY
git diff --cached --check -- task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_fp32_teacher_scoring_results.md
```

Only this new report is committed using an explicit pathspec; unrelated staged files are not included. The scoped commit receipt is returned to PRIMARY, who owns shared status updates and any further execution.

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 2｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Native source/request证据验证 | PASS | 每pair4H800/56requests/32flushes，18after文件与独立44checks一致。 |
| Cold/warm numerical验证 | PASS | Raw vectors独立重算；cold14/14，warm验收明确FAIL。 |
| Matched R1与结果报告 | PASS | 全部真实向量匹配，latency/bytes/分布/缺失证据记录。 |
| Formal04 | BLOCKED | Warm full/response均未通过own cold验收。 |
| Formal05 | BLOCKED | 同上；不增加A200/profile gate。 |
| Live donor/runtime根因验证 | TODO | 缺实际full-model tensor/state/event证据，属于PRIMARY后续范围。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次结果报告委派开始至本地证据验证完成｜**当前前沿：** PRIMARY更新current records并处理缺失live证据；本subagent完成报告后停止。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅报告内CPU verifier和要求的scoped checks。 |
| D2 细节反复重试 | CLEAR | 一次探索性schema读取错误已纠正，无native重试。 |
| D3 支线问题修补 | CLEAR | 只写一个新报告。 |
| D4 可并行任务停滞 | CLEAR | 明确禁止delegation，平台/records另有owner。 |
| D5 超范围镀金 | CLEAR | 无代码/config/cache/tolerance/dtype/interval变更。 |
| D6 分析空转 | CLEAR | 真实raw重算已交付明确FAIL和matched R1结果。 |
| D7 路线违背 | CLEAR | 无GPU/平台操作，不把operator或null标签当full-model PASS。 |

**文档检查：** S1/S2/S3/S4/S6 CLEAR。S5：本次检查时`requirements.md:71`、`plan.md:107`、`spec.md:68,300`、`progress.md:171–174`、`tickets/04-a-full.md:37–39`与`tickets/05-b-full.md:34–36`仍写Pending placement/operator未提交；实际终态和44PASS已 supersede这些current-state描述，raw/history不应修改。
**归因：** 无执行偏离；S5为待PRIMARY/records更新的当前状态。

## 3. 纠正建议

**分支：** B：current-state记录存在S5，先由其owner更新；科学spec/tickets验收不变。

**文档更新（先执行）：**
1. PRIMARY/records更新上述current-state位置：A/B native Succeeded、actual4H800/source一致、独立operator44PASS、warm验收FAIL；formal04/05仍BLOCKED，保留全部原始receipt、历史和checkbox。（可直接执行；不在本报告owner范围）

**需停止的偏离行为：** 无。
**接下去的路线：**
1. PRIMARY接收本报告并纠正current-state记录；完成标志：不再把完成实验写作等待placement，也不把完成写作数值通过。
2. PRIMARY按已授权范围处理live donor/state/KV/store/WAR证据缺口；完成标志：真实同request冷对照验证，而非operator标签或放宽tolerance。此前不解除formal04/05 hold。

## 4. 最值得关注的 3 点

1. Operator/source已验证，但A/B warm parity仅4/14，own-cold验证同样失败；fix alone不足。
2. Full模式与R1全部exact，warm-response仅6/14旧新一致；两个repetition分数完全复现错误。
3. 缺full-model live donor/state/event测量，latency/bytes只能描述顺序probe，不能证明formal-bank吞吐或global bottleneck。
