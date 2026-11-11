## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record primary acceptance of the bounded source/H800/CPP witness phase after exact command replay and review; preserve all numerical/formal limits and pending primary commit. |
| 2026-11-11 | Verify retained B business vectors, composed source identities, allocator, CPP stream/terminal joins and primary-provided terminal receipts; preserve numerical/formal HOLD. |

# B native KV stream witness results

TaskID: `profile-kv-stream-witness-native-B-20261111`.

## Outcome

**Local bounded witness checks PASS; primary accepted the bounded source/H800/CPP witness phase on 2026-11-11 after exact command replay and review. Formal 04/05 remain HOLD. No physical KV, FULL index or CUDA `commit_lens` values were captured or inspected.**

- All **16/16** completion vectors reproduce the accepted original metadata baseline exactly: **6,804 token IDs and log probabilities**, maximum absolute/defined relative error **0**, **64** zero-reference positions with undefined relative error.
- Own cold full/response-only comparisons remain **4/4 exact**; warm comparisons remain **1/4 exact, 3/4 different**. This reproduces the original drift, not a warm correctness fix.
- The selected allocator is actually `sglang.srt.mem_cache.allocator.token.TokenToKVPoolAllocator`, page size 1, with a `HybridLinearKVPool` root. Business metadata contains **1,690 CPP stream rows + 1,690 ordinary class-owned terminal rows**, with **1,690 unique one-to-one joins** covering **169 actual forward chunks**, **16 response-bound native RIDs** and **10 FULL layers** at TP0.
- Every business CPP receipt records native in-call stream **655895424**, equal to Torch current raw stream, `native_stream_scalar_observed=true`, `launch_enqueued=true`. No CUDA prefix-valid Triton terminal occurs in these retained business rows. Triton KV-store stream qualification is **NOT EXERCISED / UNVERIFIED**, not certified by the CPP receipts.
- Primary-provided local terminal proof records B RJob/one replica **Succeeded**, one container **Completed/exit 0/restart 0**, with the expected image ID. Actual **four H800 devices** come separately from the retained worker runtime, not declared GPU limits.

## Evidence and acceptance boundaries

All paths below are relative to `task_memory/task_2026-11-08_qwen35_full_kl_nll/`:

- New business root: `evidence/teacher-scoring-kv-stream-witness-probe-20261111/native/B/admission-B-r1/` (`B`).
- Accepted baseline root: `evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1/` (`O`), job `exp-1111-073825-734134`, caller pin `4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff`.
- New job: `exp-1111-113511-669312`, UID `a7bb5844-c428-465c-80f2-b62ad8e70600`, creator `i-fengyicheng`, finish `2026-11-11T03:43:09Z`.
- Local admission/terminal evidence: `evidence/teacher-scoring-kv-stream-witness-probe-20261111/admission-B-r1.json`, `admission-B-r1.terminal.json`, `initial-platform-verification.json`, `terminal-platform-containers.json`.
- Derived machine-readable checks: `evidence/teacher-scoring-kv-stream-witness-probe-20261111/native-verification-B.json`.
- Scope owners read: `requirements.md`, `plan.md`, `tickets/04-a-full.md`, `tickets/05-b-full.md`, `design_kv_coherence_measurement.md`, `test_report_2026-11-11_kv_stream_witness_source.md`, `test_report_2026-11-11_kv_stream_witness_integration.md`.

Only retained local JSON, logs, source archives and immutable Git blobs were read. No authentication, platform/StepMind/GPU API, SSH, GPU business execution, tensor value operation or further delegation occurred. No source, helper, probe, config, raw evidence, A file or shared task record was edited. The two new deliverables are uncommitted.

## Environment and terminal proof

Local verification: Linux workdir `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`, `/usr/bin/python3`, **Python 3.10.6**, `-B`, standard library only; no conda activation or dependency installation. Each large metadata read is scoped to this exact B job and wrapped in `timeout 60s`. No temporary verification script or raw-data copy is needed.

Retained worker runtime: **Python 3.12.16**, `/opt/sglang/bin/python3`, **Torch 2.14.1+cu130**, **SGLang 0.5.24.dev80+g056f871**. Witness preflight records installed **apache-tvm-ffi 0.1.11**, locating its six qualified sources beneath `/opt/sglang/lib/python3.12/site-packages/tvm_ffi/`. Runtime GPU records are four entries `NVIDIA H800, 81559 MiB, 570.124.06`.

The expected and actual container imageID is:

```text
artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805
```

`terminal-platform-containers.json:67–128` is the primary's exact SDK kapis replica receipt, queried at `2026-11-11T03:45:14.622334+00:00`. It records replica `exp-1111-113511-669312-cfcd2084`, UID `27858f7c-4eda-42e2-bcf2-850f59a6c503`, node `gpu-h800-0320.host.platform.shaipower.com`, container finish `03:42:41Z`, replica finish `03:43:08Z` and job finish `03:43:09Z`. These are different lifecycle timestamps, not inconsistent vector evidence. Declared limits are 4 GPUs, 32 CPUs, 250Gi memory. Job UID equality was checked against the B terminal receipt; replica owner-UID binding is primary-reported, not a new raw ownerReferences inspection by this verifier.

The earlier A corev1 raw-pod **ForbiddenException/403/Forbidden** remains in the separate, unchanged `terminal-platform-containers-A.json:26–30`. The later exact SDK replica receipt supplies terminal container evidence; the original 403 is a known, non-blocking access limitation. Neither replica success nor container exit 0 substitutes for the business checks below.

## Expected versus observed checks

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Business execution and cleanup | Measurements completed; server alive before cleanup; natural worker success | `native_measurements_completed=true`, `cleanup_completed=true`, pre-cleanup server return code `null`; primary container exit 0 | PASS, execution only |
| Completion vectors | Exact UID/sample/repetition/phase/mode join; identical token/probability shape and values | 16 unique keys, same order; 6,804 values; max absolute/defined relative error 0; 64 zero-reference positions undefined | PASS |
| Native response identity | Each request RID equals its retained response and completion-score RID | 16/16 new and 16/16 baseline; distinct RIDs across runs, not assumed shared | PASS |
| Scoring and flushing | 16 successful requests, 10 successful flushes, unsalted inputs | 16 scored/HTTP 200; 10 flushed/HTTP 200; salt null throughout | PASS |
| Own cold comparison | Preserve baseline cold equality | 4/4 exact, both errors 0 | PASS |
| Own warm comparison | Preserve original 1/4 equality and drift | 1/4 exact; samples 1694–1696 differ, identical metrics to O | PASS reproduction; FAIL warm correctness |
| Source composition | Same selected-FP32 six-file stage; metadata 16-file overlay before witness; final witness qualification of 35 paths | 6 + 16 + 35 before/after pairs hash-match; all35 owner-qualified/reversible; five authorized witness changes | PASS |
| Caller/helper source pins | Immutable caller26664e81/new helper79dba51b and baseline4f1139b0 | New 7/7 and baseline 6/6 retained source identities match Git blobs; helper 17,123 bytes | PASS |
| Actual allocator | Selected class/module, root pool and page-one configuration | Initial `server_info` metadata sequence 1 records TokenToKVPoolAllocator / HybridLinearKVPool / page1 / size2741556 / BF16 / CUDA | PASS, selected static index-free branch only |
| Metadata scope and continuity | DP1 responding process only; raw DP None allowed; no lost rows between drains | PID335, TP0/PP0, attnDP0; initial353 + business19713 =20066 sequences1–20066, no gaps/duplicates | PASS; no all-TP claim |
| CPP stream witness | In-call scalar, nonempty launch, exact unique terminal join | 1690/1690 same native/Torch raw stream655895424; 1690 unique joins; no empty/no-launch receipt | PASS, observed native call only |
| Writer context and FULL layers | CPU RID/prefix/extend fields join actual scheduler chunks; exactly-once all observed FULL layers | 169 chunks, 16 RIDs; 10 layers per chunk; 5070 GDN allocation rows and165 plans join by explicit chunk identity | PASS descriptors/host context, not physical content |
| CUDA prefix-valid Triton KV terminals | Report actual selection separately; never certify with CPP/Torch stream | 0 business and0 initial terminal rows selected | NOT EXERCISED / UNVERIFIED |
| Model/cache/argv/dtype | Preserve baseline scientific/runtime inputs | Same model manifest hashes, cache settings, dtype, normalized argv; only endpoint address and generated seed differ | PASS bounded equivalence; seed qualified below |
| Physical indices/KV/commit lengths, completion/PDL, numerical cause, all TP, formal200 | Not measured or accepted in this stage | No values captured/read; raw result `numerical_acceptance=null`, `performance_accepted=false` | HOLD / UNVERIFIED |

The retained shutdown code **-9** is the probe's post-measurement teacher cleanup, not the worker/container business exit. `result.json` records that cleanup finished and the server had not exited before cleanup. `server.log:10–13` has four NVML memory-affinity warnings that skip NUMA configuration; no retained Traceback/Fatal/RuntimeError was found. Serving-time compilation messages are GDN Triton kernels, not evidence that a fresh CPP build log was retained.

## Exact vectors, request shapes and preserved drift

All four fixtures have the exact source prefix `00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6:5:`:

| Sample index | UID suffix | Input tokens | Prompt tokens | Completion tokens |
| --- | --- | --- | --- | --- |
| 1693 | 123 | 97365 | 96631 | 734 |
| 1694 | 125 | 98312 | 98066 | 246 |
| 1695 | 127 | 98942 | 98511 | 431 |
| 1696 | 129 | 99074 | 98784 | 290 |

Repetition is 0 throughout. Full-input requests have `logprob_start_len=0` and return input-count log probabilities; response-only starts at prompt-count minus1 and returns completion-count plus1. Tail extraction yields exactly the completion lengths above in every phase. The complete 16-case actual/baseline RID list and business row ranges are in the JSON deliverable. Matching uses `(pair, source_uid, sample_index, repetition, phase, mode)`; actual responses establish each run's native RIDs independently.

| Warm sample | Full vs response-only max absolute error | Max relative error | Undefined zero-reference count | Exact |
| --- | --- | --- | --- | --- |
| 1693 | 0 | 0 | 3 | true |
| 1694 | 2.9801958589814603e-06 | 0.3055551434731875 | 5 | false |
| 1695 | 0.33083581924438477 | 10.83576074484674 | 4 | false |
| 1696 | 0.24397611618041992 | 2.1428543402212714 | 5 | false |

These are log-probability-vector comparisons, not physical KV comparisons. Warm full/response-only are not cold oracles. At sample1695, cold-full vs warm-full max absolute error remains **0.43444275856018066**, and cold-full vs warm-response-only **0.5321998596191406**. All eight comparison records equal the accepted baseline records, including cold-reference metrics and undefined counts.

## Stream, layer and conditional join evidence

Schema remains `rows=[sequence,event,[[key,value],...]]` under `server_info.internal_states[0].mamba_runtime_metadata`. The initial `server_info.json` drains startup rows1–353, including allocator row1 and90 startup CPP/ordinary-terminal pairs. The final `runtime_metadata.json` drains business rows354–20066. Counts must not be added from two representations of the same drain.

The business join key is the complete tuple of **RIDs, CPU prefix lengths, CPU extend lengths, K-cache pointer, V-cache pointer, writer-location pointer and writer-location descriptor**. Each CPP row and ordinary terminal row has exactly one counterpart. Pointer reuse or chronology alone is never a binding rule. The matching flattened CPP buffers have `[2741557,256]` shape; class-owned buffers have `[2741557,1,256]`, stride `[256,256,1]`, BF16, CUDA0. Both describe the same K/V backing pointers. Each observed FULL layer has one stable backing-pointer pair across this run.

Observed global→pool/dense mapping is **3→0, 7→1, 11→2, 15→3, 19→4, 23→5, 27→6, 31→7, 35→8, 39→9**, on the actual inner `MHATokenToKVPool` object139847959779264. The allocator records root `HybridLinearKVPool` object139847955872560; distinct root/inner pool identities are not a mismatch.

Independent scheduler keys `(rid,prefix_len,extend_len)` are unique for169 chunks and satisfy `seq_end=prefix_len+extend_len`. Every terminal, all5070 GDN allocation rows and165 prefill plans bind to those explicit keys. All10 FULL layers occur exactly once per chunk. Per-RID chunks have contiguous observed writer intervals ending at that request's input count; the first observed interval starts at its actual `cached_tokens`, not necessarily zero. Total newly processed writer rows across the16 requests are **1,291,508**. Cached-prefix physical contents remain unmeasured.

The warm-full target sample1695 binds through its own response RID **ea2093c6cc3f4c1e98b42fa0b9ef4e92**, not the old run's RID. For prefix90112/extend8192, CPP/terminal row pairs are:

```text
layer 3:16455/16456; 7:16466/16467; 11:16477/16478; 15:16488/16489;
19:16499/16500; 23:16510/16511; 27:16521/16522; 31:16532/16533;
35:16543/16544; 39:16554/16555.
```

Checkpoint begin **16557** records `(RID,P=90112,E=98304)`. Returned **16560** records node127/old prefix end **Q=98067**. Canonical rebind **16561** carries the same RID/node/prefix and absolute window. Across all165 cache receipts, begin keys `(RID,P,E)` and returned keys `(RID,node_id,prefix_len)` are individually unique and each canonical row joins exactly once. This qualifies conditional host identity/geometry; it does not inspect `InsertParams.value`, canonical FULL index values or payload values. The existing unsalted shared-control geometry failures are not isolated-full-input gates for this WIT run; the three expected shared-geometry violations are not reclassified as failed witnesses.

Native in-call scalar return and its1690 Python receipts support successful C++/TVM-FFI ABI execution for the observed nonempty specialization. A fresh compiler invocation/cache miss and the CAPI-versus-fallback selection were not independently retained. Raw preflight `native_compilation=UNVERIFIED` remains unchanged. Same CPP/Torch stream does **not** prove device completion, PDL readiness, race absence, physical KV coherence, or all-TP coverage. The empty-header `-1` no-launch rule and valid stream0 are source contracts; neither is an observed business case. GDN `linear_attn_prefill_backend=triton` is not a CUDA prefix-valid Triton **KV-store terminal**.

The observed page1/CP1/graphs-off allocator and disabled unified-memory/hicache/memory-saver/sharding qualify only the existing selected **static index-free rule**. They do not generalize to arbitrary allocators, model families or other TP ranks, and do not supply physical index values.

## Source composition and unchanged runtime inputs

Immutable caller pin: `26664e81099d71a995e4b91183431a7c13f2862b`. Immutable witness helper pin: `79dba51b956ab0de779f3e0d953355982091f5aa`. Helper identity: **17,123 bytes**, SHA256 **6140cdc283c457938d34f06dc8adad3657465cbc800acf08c80cede6e378e51d**. No mutable working-tree source is used as the pin.

The six selected-FP32 source identities and the16 metadata-overlay source identities exactly match O. Then the witness owner qualifies all35 **before** files against the completed metadata overlay and derives all35 **after** files through its pinned reversible `_rewrite`; all70 archived contents match recorded hashes. The five witness edits are `model_runner.py`, `forward_context.py`, `memory_pool.py`, `kvcache.py`, `kvcache.cuh`. Final runtime identification occurs after those edits. Therefore final `model_runner.py` hash **27eb08f7f3bb60b15725d0e7bfebab2a9677d38fefe46a2ecf4c015d4f0dd345** correctly differs from metadata-stage hash **5d07424971c85b63aa1ff0b7e788a6b7938f012a09c86352ccb8785817505181**. It is not an unexplained mismatch with Stage16. All35 checked paths are listed in the JSON deliverable; existing manifests remain their authoritative per-file hash owner.

Archive manifest SHA256 values:

| Archive | SHA256 |
| --- | --- |
| `B/source_preflight/source_manifest.json` | dd856add48fe221101c03b96fb018e8fc939362cc15415482cac6d5128370c6f |
| `B/runtime_metadata_source_preflight/source_manifest.json` | 22aa07e3f10b9c9d8aec6f5fdc180076613d3014f6985542f0c8ea27bafcb3e9 |
| `B/kv_store_stream_source_preflight/source_manifest.json` | 076b60a28b3c5de49154e42cdd8ede7f7f99091e4860293cbc61de2b5d4228d0 |

Model path and retained manifest hashes are unchanged: `/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-35B-A3B/model`; config hash **5e4d7f74fec2f360eb9cfbfcd6ec0c4c76e684d3a11caaed259d9fd9bfbc7944**, safetensors-index hash **d8d0b7ca4e61ae107e3e87a3ff21136b3ac7c789e64bb24267227ca804e04205**. This is mounted-path/manifest identity, not a whole-weight checksum.

Normalized teacher argv is unchanged except `--dist-init-addr`: BF16, TP4, context131072, static-memory0.85, max-running1, chunk8192, graphs disabled, deterministic inference, FA3, GDN prefill Triton. Cache source is the retained default `UnifiedRadixCache`, FULL+MAMBA/RustUnifiedTreeCore (`server.log:120–123` for TP0/TP1); `extra_buffer`, selected FP32 state snapshots and disabled stochastic rounding/Philox0 remain unchanged. `SGLANG_FORCE_COARSE_WAR_BARRIER` remains unset. Local source mount remains `100.96.128.195:/data/ycfeng:/data/ycfeng`.

**Qualified difference:** resolved generated seed is **879546281**, versus O's **596871011**; no explicit seed argv was added. All16 vectors still reproduce exactly. This does not establish same-seed or general RNG-free behavior. The first4 fixture hash remains **89519dd56ec07ce01f8ee18ff71b2ccfb3170698b29d9b5f4e0fe70c83c9a3e1**; new isolated config is its immutable caller-pinned witness selection, hash **a6bc4fdb80e397bd1c36ca8bb213853591269c6a4cea0ffd67cdc0458fe63314**.

## Exact local verification command

The following standard-library-only command reproduces the decisive assertions without writing into business/source evidence or executing GPU code. SHA256 inventories and case-level row references are retained in the companion JSON. The exact fenced command was extracted and executed through `subprocess.run(['zsh', '-c', command], capture_output=True, text=True, timeout=55)` under an outer `timeout 60s /usr/bin/python3 -B`: **exit0/PASS**, Python3.10.6, 16 exact vectors/6804 values/64 undefined relative errors, 57 source pairs,1690 unique joins/169 chunks/165 cache joins and formalHOLD. A separate local consistency check confirmed every JSON case row, all35 paths, source/business hashes, target row references, strict finite JSON and both files' whitespace. Scoped `git diff --check` returned0; no commit was made.

```bash
timeout 60s /usr/bin/python3 -B - <<'PY'
import hashlib, json, math, platform, subprocess, sys, types
from collections import Counter, defaultdict
from pathlib import Path
T = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
E = T / 'evidence/teacher-scoring-kv-stream-witness-probe-20261111'
B = E / 'native/B/admission-B-r1'
O = T / 'evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1'
load = lambda p: json.loads(p.read_text())
lines = lambda p: [json.loads(x) for x in p.read_text().splitlines()]
sha = lambda b: hashlib.sha256(b).hexdigest()
blob = lambda ref, p: subprocess.check_output(['git', 'show', f'{ref}:{p}'])
r, o = load(B / 'result.json'), load(O / 'result.json')
q, oq = lines(B / 'requests.jsonl'), lines(O / 'requests.jsonl')
key = lambda x: tuple(x[k] for k in ('pair', 'source_uid', 'sample_index', 'repetition', 'phase', 'mode'))
old = {key(x): x for x in oq}
assert len(old) == len(q) == 16 and [key(x) for x in q] == [key(x) for x in oq]
token_count = zero_count = 0
for x in q:
    y = old[key(x)]
    a = load(B / 'completion_scores' / Path(x['completion_scores']).name)
    b = load(O / 'completion_scores' / Path(y['completion_scores']).name)
    assert a['token_ids'] == b['token_ids'] and a['log_probs'] == b['log_probs']
    assert len(a['token_ids']) == len(a['log_probs']) == x['response_count'] == x['returned_completion_count']
    assert all(math.isfinite(v) for v in a['log_probs'])
    assert a['native_request_id'] == x['native_request_id'] == x['meta_info']['id']
    assert b['native_request_id'] == y['native_request_id'] == y['meta_info']['id']
    assert x['status'] == 'scored' and x['http_status'] == 200 and x['cache_salt'] is None
    for k in ('input_count', 'prompt_count', 'response_count', 'logprob_start_len', 'input_token_logprobs_count'):
        assert x[k] == y[k]
    token_count += len(a['log_probs'])
    zero_count += sum(v == 0 for v in b['log_probs'])
assert len({x['native_request_id'] for x in q}) == 16
assert not {x['native_request_id'] for x in q}.intersection(x['native_request_id'] for x in oq)
assert token_count == 6804 and zero_count == 64
cache = lines(B / 'cache.jsonl')
assert len(cache) == 10 and all(x['status'] == 'flushed' and x['http_status'] == 200 for x in cache)
c, oc = lines(B / 'comparisons.jsonl'), lines(O / 'comparisons.jsonl')
assert c == oc and len(c) == 8
assert sum(x['full_vs_response_only']['values_exact'] for x in c if x['phase'] == 'cold') == 4
assert sum(x['full_vs_response_only']['values_exact'] for x in c if x['phase'] == 'warm_stream') == 1
for result, ref in ((r, '26664e81'), (o, '4f1139b0')):
    for p, identity in result['native_scoring_sources'].items():
        raw = blob('79dba51b' if p.endswith('sglang_kv_streams.py') else ref, p)
        assert len(raw) == identity['bytes'] and sha(raw) == identity['sha256']
for short, ref in (('sglang_mamba_snapshots', '26664e81'), ('sglang_mamba_runtime_metadata', '26664e81'), ('sglang_kv_streams', '79dba51b')):
    name = 'tests.manual.agent_opd.' + short
    p = 'tests/manual/agent_opd/' + short + '.py'
    module = types.ModuleType(name)
    module.__file__ = p
    sys.modules[name] = module
    exec(compile(blob(ref, p), p, 'exec'), module.__dict__)
w = sys.modules['tests.manual.agent_opd.sglang_kv_streams']
for name, count in (('source_preflight', 6), ('runtime_metadata_source_preflight', 16), ('kv_store_stream_source_preflight', 35)):
    stage = r[name]
    assert len(stage['files']) == count and load(B / name / 'preflight.jsonl') == stage
    for p, identity in stage['files'].items():
        a, b = (B / name / 'before' / p).read_bytes(), (B / name / 'after' / p).read_bytes()
        assert sha(a) == identity['before_sha256'] == stage['observed_before_sha256'][p]
        assert sha(b) == identity['after_sha256'] == stage['observed_after_sha256'][p]
        if name == 'kv_store_stream_source_preflight':
            w._qualified_baseline(p, a, w.source_manifest()['files'][p])
            assert w._rewrite(p, a) == b and w._rewrite(p, b, reverse=True) == a
    if name != 'kv_store_stream_source_preflight':
        assert stage['files'] == o[name]['files']
stage = r['kv_store_stream_source_preflight']
assert r['runtime_metadata_source_preflight']['observed_after_sha256']['srt/model_executor/model_runner.py'] == stage['observed_before_sha256']['srt/model_executor/model_runner.py']
for p, identity in r['runtime']['sglang_sources'].items():
    assert identity['sha256'] == (stage['observed_after_sha256'][p] if p in stage['files'] else o['runtime']['sglang_sources'][p]['sha256'])
assert r['runtime']['model_manifest_identity'] == o['runtime']['model_manifest_identity']
argv = lambda a: [v if i == 0 or a[i - 1] != '--dist-init-addr' else '<endpoint>' for i, v in enumerate(a)]
assert argv(r['argv']) == argv(o['argv'])
assert sha(blob('26664e81', str(T / 'teacher_scoring_kv_stream_witness_probe_config.json'))) == r['config']['sha256']
assert r['fixture']['sha256'] == o['fixture']['sha256']
s = load(B / 'server_info.json')['get_server_info']
os = load(O / 'server_info.json')['get_server_info']
for k in ('dtype', 'kv_cache_dtype', 'mamba_radix_cache_strategy', 'uses_mamba_radix_cache', 'enable_mamba_cache_stochastic_rounding', 'mamba_cache_philox_rounds', 'page_size', 'attn_cp_size', 'dcp_size', 'enable_prefill_cp', 'enable_kv_cache_sharding', 'enable_unified_memory', 'enable_hierarchical_cache', 'enable_memory_saver', 'disable_cuda_graph', 'attention_backend', 'linear_attn_prefill_backend', 'mamba_backend', 'max_running_requests', 'chunked_prefill_size', 'context_length'):
    assert s[k] == os[k]
initial = s['internal_states'][0]['mamba_runtime_metadata']
metadata = load(B / 'runtime_metadata.json')
assert metadata['dp_size'] == 1 and metadata['tp_size'] == 4
assert len(metadata['server_info']['internal_states']) == 1
m = metadata['server_info']['internal_states'][0]['mamba_runtime_metadata']
assert initial['process_id'] == m['process_id'] == 335 and m['rank']['tp_rank'] == 0 and m['rank']['dp_rank'] is None
assert [x[0] for x in initial['rows'] + m['rows']] == list(range(1, 20067))
allocator = [dict(x[2]) for x in initial['rows'] if x[1] == 'kv_allocator_created']
assert len(allocator) == 1 and allocator[0]['allocator_class'] == ['sglang.srt.mem_cache.allocator.token', 'TokenToKVPoolAllocator']
assert allocator[0]['page_size'] == 1 and allocator[0]['pool_class'][1] == 'HybridLinearKVPool'
rows = [(seq, event, dict(fields)) for seq, event, fields in m['rows']]
events = lambda event: [x for x in rows if x[1] == event]
freeze = lambda v: tuple(freeze(x) for x in v) if isinstance(v, list) else v
bind = lambda d: tuple(freeze(d[k]) for k in ('rids', 'prefix_lens', 'extend_lens', 'k_cache_data_ptr', 'v_cache_data_ptr', 'writer_loc_data_ptr', 'writer_loc'))
streams, terminals = defaultdict(list), defaultdict(list)
for x in events('kv_store_stream'): streams[bind(x[2])].append(x)
for x in events('kv_store_terminal'): terminals[bind(x[2])].append(x)
assert len(streams) == len(terminals) == 1690 and set(streams) == set(terminals)
assert all(len(v) == 1 for v in list(streams.values()) + list(terminals.values()))
assert all(d['native_stream_scalar_observed'] and d['launch_enqueued'] and d['native_actual_stream'] == d['torch_current_raw_stream'] == 655895424 for _, _, d in events('kv_store_stream'))
assert all(d['store_kind'] == 'mha_set_kv_buffer_impl' and not d['native_stream_scalar_observed'] and d['native_actual_stream'] is None for _, _, d in events('kv_store_terminal'))
assert all(dict(x[2])['store_kind'] == 'mha_set_kv_buffer_impl' for x in initial['rows'] if x[1] == 'kv_store_terminal')
chunks = defaultdict(lambda: defaultdict(list))
for x in events('kv_store_terminal'):
    d = x[2]
    assert len(d['rids']) == len(d['prefix_lens']) == len(d['extend_lens']) == 1
    chunks[d['rids'][0]][(d['prefix_lens'][0], d['extend_lens'][0])].append(x)
assert set(chunks) == {x['native_request_id'] for x in q}
for x in q:
    ordered = sorted(chunks[x['native_request_id']])
    assert ordered[0][0] == x['meta_info']['cached_tokens']
    assert all(a + alen == b for (a, alen), (b, _) in zip(ordered, ordered[1:]))
    assert ordered[-1][0] + ordered[-1][1] == x['input_count']
    for receipts in chunks[x['native_request_id']].values():
        assert sorted((d['layer_id'], d['pool_layer_id'], d['buffer_layer_idx']) for _, _, d in receipts) == [(3 + 4 * i, i, i) for i in range(10)]
        assert all(d['k_cache'][2:4] == [[2741557, 1, 256], [256, 256, 1]] and d['v_cache'][2:4] == [[2741557, 1, 256], [256, 256, 1]] for _, _, d in receipts)
scheduler = {(d['rid'], d['prefix_len'], d['extend_len']): seq for seq, _, d in events('scheduler_track_boundary')}
assert len(scheduler) == 169 and all(d['seq_end'] == d['prefix_len'] + d['extend_len'] for _, _, d in events('scheduler_track_boundary'))
for event in ('kv_store_terminal', 'gdn_snapshot_allocation', 'prefill_track_plan'):
    assert all((d['rids'][0], d['prefix_lens'][0], d['extend_lens'][0]) in scheduler for _, _, d in events(event))
begin, returned = defaultdict(list), defaultdict(list)
for seq, _, d in events('checkpoint_insert_begin'): begin[(d['rid'], d['protected_len'], d['page_aligned_len'])].append(seq)
for seq, _, d in events('checkpoint_insert_returned'): returned[(d['rid'], d['node_id'], d['prefix_len'])].append(seq)
assert len(begin) == len(returned) == len(events('canonical_kv_rebind_enqueued')) == 165
assert all(len(v) == 1 for v in list(begin.values()) + list(returned.values()))
assert all(len(begin[(d['rid'], d['absolute_start'], d['absolute_end'])]) == len(returned[(d['rid'], d['node_id'], d['prefix_len'])]) == 1 for _, _, d in events('canonical_kv_rebind_enqueued'))
terminal = load(E / 'terminal-platform-containers.json')['jobs']['B']
assert terminal['uid'] == load(E / 'admission-B-r1.terminal.json')['uid'] == 'a7bb5844-c428-465c-80f2-b62ad8e70600'
assert terminal['job'] == r['job'] and terminal['status']['phase'] == 'Succeeded'
assert len(terminal['replicas']) == 1 and terminal['replicas'][0]['phase'] == 'Succeeded'
container = terminal['replicas'][0]['containers'][0]
assert container['state']['terminated']['exitCode'] == 0 and container['state']['terminated']['reason'] == 'Completed' and container['restartCount'] == 0
assert container['imageID'] == r['runtime']['configured_image'] == stage['image']
assert len(r['runtime']['gpu_devices']) == 4 and all('NVIDIA H800' in x for x in r['runtime']['gpu_devices'])
assert r['native_measurements_completed'] and r['cleanup_completed'] and r['server_returncode_before_cleanup'] is None
assert r['numerical_acceptance'] is None and r['performance_accepted'] is False
assert 'torch' not in sys.modules and 'sglang' not in sys.modules
print(json.dumps({'python': platform.python_version(), 'vectors_exact': 16, 'completion_values': token_count, 'relative_undefined': zero_count, 'cold_exact': 4, 'warm_exact': 1, 'source_archive_pairs': 57, 'unique_cpp_terminal_joins': len(streams), 'chunks': len(scheduler), 'cache_joins': len(begin), 'process': m['process_id'], 'business_events': dict(Counter(x[1] for x in rows)), 'generated_seed_new': s['random_seed'], 'generated_seed_baseline': os['random_seed'], 'local_checks': 'PASS', 'formal': 'HOLD', 'physical_values': 'UNMEASURED'}, indent=2))
PY
```

## 1. Progress completion

**Summary:** PASS 4 | BLOCKED/FAILED/SKIPPED 0 | TODO 0, within this assignment only.

| Subtask | Status | Evidence |
| --- | --- | --- |
| Local vectors and baseline identity | PASS | 16 exact vectors; original4f Git binding; cold4/warm1 preserved |
| Source/allocator/CPP and conditional RID-layer coverage | PASS | 35 source paths; allocator row1;1690 unique pairs/169 chunks |
| Local terminal proof and two owned deliverables | PASS | Primary filtered container exit0; report and JSON only |
| Primary bounded source/H800/CPP witness acceptance | PASS | Primary exact command replay and review complete; no formal/numeric acceptance or commit by this verifier |

## 2. Drift check

**Conclusion:** No drift observed. Window: this B local-verification assignment. Frontier: primary bounded witness acceptance recorded; primary owns commit and subsequent qualification.

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 Tooling polish | CLEAR | Standard-library checks stop at requested acceptance; no new harness/script |
| D2 Retry loop | CLEAR | Schema inspection identified startup drain; no behavior fix or repeated workaround |
| D3 Side quest | CLEAR | All reads address assigned vectors, source, allocator or native witnesses |
| D4 Stalled frontier | NO DATA | A/platform work belongs to primary; further delegation expressly prohibited |
| D5 Gold-plating | CLEAR | Exactly two owned artifacts; no feature or numeric capture |
| D6 Analysis sprawl | CLEAR | Investigation delivers exact counts, joins and explicit limits |
| D7 Off-route | CLEAR | Local-only evidence; no GPU/auth/API access or shared edits |

**Document check:** No S1–S6 defect established in the assigned scope. Earlier Running snapshots are superseded by the supplied terminal receipts, not used as latest evidence; canonical task-status updates remain primary-owned. **Attribution:** None.

## 3. Route correction

**Branch A:** Assigned scope/acceptance criteria are sound; no shared spec/ticket edit by this verifier. **Behavior to stop:** None.

1. Primary accepted the two uncommitted B artifacts against the16 vectors, actual class and CPP joins; primary will commit them with the matched review archive.
2. Retain formal HOLD and independently qualify any later numerical capture, ordering/lifetime, actual FULL indices and any selected Triton prefix-valid path. No GPU rerun or capture is authorized by this report.

## 4. Three important points

1. B's16 vectors are exactly reproduced while warm drift remains; bounded instrumentation equivalence is not warm correctness.
2. Actual selected allocator and1690 unique CPP/ordinary-terminal joins cover TP0's16 business RIDs/10 FULL layers; no prefix-valid Triton terminal was exercised.
3. Physical values, device completion/PDL, all TP, historical cause, performance and formal200 remain unverified; bounded source/H800/CPP witness acceptance is recorded and primary commit remains pending.
