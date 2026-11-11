# r2 native batch-metadata RCA — read-only, no fix selected

## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Establish real retained context/callback RED replay, compare startup/business metadata for both r2 pairs, and propose a scoped route without changing production code. |

TaskID: `profile-kv-coherence-batch-metadata-rca-20261111` (continuation of the initial `profile-kv-coherence-r2-batch-metadata-rca-20261111` request).

## Outcome and boundary

The immediate failure is proven: `Collector._targets()` treats every published native batch as an EXTEND writer batch. A real startup request keeps a nonempty RID but has `extend_prefix_lens_cpu=None` and `extend_seq_lens_cpu=None`. `writer_windows()` evaluates `len(prefixes)` and raises `TypeError: object of type 'NoneType' has no len()`. Both `note_cpp` and `fresh` reach this path; `observe` correctly isolates serving and appends global errors with RID=null. Those startup errors persist and disqualify the final after-all16 drain before any physical comparison or CPU numeric metrics.

No production helper/test/config/report/shared document/README, old r1/r2/R3/source archive or native library was edited. No stage/commit/platform/auth/GPU operation, delegation, source collection, global rehash, new test framework or error-gate suppression occurred. The prior raw-to-resolved initializer fix worked and remains accepted. Source6119, source/static-stream and ownership acceptance are not reset. This report proposes a fix route only; primary must select/authorize a software change.

Artifacts: [replay_batch_metadata.py](replay_batch_metadata.py), [inspect_receipts.py](inspect_receipts.py), [receipt_counts.json](receipt_counts.json), and selected [A stdout](replay-A.stdout)/[stderr](replay-A.stderr), [B stdout](replay-B.stdout)/[stderr](replay-B.stderr). These contain compact CPU metadata, not raw K/V tensor data or copied native errors arrays.

## Phase1/2: actual, deterministic, seconds-long RED loop

From the repository root:

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/kv-coherence-batch-metadata-rca-20261111/replay_batch_metadata.py --pair A
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/kv-coherence-batch-metadata-rca-20261111/replay_batch_metadata.py --pair B
```

Both commands were run twice. They return exit1 at the explicit exact-symptom assertion, not at import/setup: A1.052s then0.991s; B0.681s then0.584s. Each produces exactly two global errors, stages `note_cpp` and `fresh`, RID=null, message `object of type 'NoneType' has no len()`. The final assertion is `RED: valid published native batch with missing host lens poisons global diagnostic errors`.

The script loads each **actual generated** archived `after/srt/kv_coherence.py` and the actual `forward_context.py`. It extracts the executed `_kv_batch = get_forward_context().forward_batch if has_forward_context() else None` assignment from archived CPP-store source. Actual `ForwardContext`, `forward_context`, `get_forward_context`, `has_forward_context`, save/restore and the real generated `observe`/`Collector.note_cpp`/`fresh`/`_targets`/`writer_windows` execute unchanged. It tests genuinely absent context before entering the real context manager and checks restoration after leaving it; there is no injected always-present getter.

Recorded metadata creates only an explicit CPU object exposing the three recorded batch fields. `Collector.__new__` supplies empty diagnostic state, not a real GPU allocator/model; no tensor values, kernel, CUDA API or stream query is executed. The actual business counterpart (A WIT seq566/B368) and absent context produce no errors. The recorded startup counterpart (A184/B118) produces the native symptom. Recorded raw fields are **RID nonempty, both CPU lens null**, not a guessed null batch or null RID.

Minimization: no selected bank, tensor, native stream operation or allocator is needed to reach the error. Replacing only prefix=None with `[0]` leaves the same error at `len(extends)`; replacing only extend=None with `[1]` leaves it at `len(prefixes)`; replacing both yields a clean empty window. These replacements are isolated CPU probes, not serving fallbacks. An absent context is independently clean under the existing supported branch. The actual state preserves both null fields for the red replay.

Environment: host CPU Python3.12.13 at `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`; no package/version/environment change. JSON inspection/replay applies `RLIMIT_AS=30GiB` and timeout60s. `systemd-run --user --scope -p MemoryMax=30G` could not connect to a user bus; system scope required interactive authentication. No authentication/elevation was attempted. The process address-space ceiling is **not** claimed to be cgroup MemoryMax.

## Phase3/4: hypotheses and independent decisive checks

These hypotheses were ranked and shared before their targeted receipt/source tests:

| Rank | Hypothesis/prediction | Evidence/result |
| --- | --- | --- |
| 1 | Ordinary native startup generation reaches DECODE with legitimate absent EXTEND host lens; all errors already exist before scoring, and missing-lens stores equal7 decode steps × FULL layers. | Strongly supported: all error arrays exactly equal startup; null stores112=7×16/70=7×10 share the ordinary nonempty warmup RID and single-token writer shape. Source defaults and DECODE branch leave both host mirrors None. Native warmup requests8 generated tokens. This is not a fabricated dummy or null-RID batch. Exact mode is not itself recorded in WIT; DECODE attribution is the source/event inference described below. |
| 2 | Real business eager/carry loses host RID or lens; final rows contain nulls or global errors grow after startup. | Falsified for the entire retained business window:169 chunks per pair, all2704/1690 CPP and terminal rows non-null, scheduler host keys exact; zero new global errors. |
| 3 | CPP and common terminal use a stale/wrong published batch; metadata or ptr keys disagree with scheduler chunk/current counterpart. | Falsified for the observable selected business bindings: all CPP/terminal metadata+K/V/loc ptr keys one-to-one and exact; all169 host chunk keys equal scheduler records. Actual runner publishes the passed batch within the unchanged context manager and restores it. This does not prove unobserved concurrent modes or GPU tensor values. |

Inspection command:

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/kv-coherence-batch-metadata-rca-20261111/inspect_receipts.py
```

Observed exit0; output is bounded counters plus the fresh `receipt_counts.json`. It reads only each attempt's startup `server_info.json` and final `runtime_metadata.json`, and stores selected rows/descriptors. It never prints/copies the huge errors array or auth values. `runtime_metadata.json` contains the final newly drained business rows (A starts seq552/B354), not a replay of startup rows.

| Native observation | A process340 | B process347 |
| --- | ---: | ---: |
| FULL layers / allocated bytes | 16 /539,361,280 | 10 /337,248,256 |
| Startup errors = final errors (exact arrays) |224=224 |140=140 |
| Errors `note_cpp` / `fresh`; all RID=null |112 /112 |70 /70 |
| Startup CPP/terminal rows each; null CPU prefix+extend subset |144;112 |90;70 |
| Startup non-null CPP/terminal rows each |32 |20 |
| Business CPP/terminal rows each; null subset |2704;0 |1690;0 |
| Unique business host chunks = scheduler chunks |169=169 |169=169 |
| Business CPP/terminal full metadata+ptr key match |2704 one each |1690 one each |
| Target prefix90112 CPP/terminal keys |32=32 exact |20=20 exact |
| First target CPP / terminal seq |11633 /11634 |7445 /7446 |
| Completed native scoring RIDs |16 |16 |
| Per-bank FRESH dense layers |0..15 each |0..9 each |
| Per-bank errors |0 each |0 each |
| Final numeric acceptance |null |null |

Native CPP in-call scalar equals Torch F in all business rows; terminal `native_actual_stream=None` is the deliberate terminal schema (it is not a separate in-call CPP scalar). All terminal CPU RID/lens are non-null in business. Do not confuse this expected optional stream field with the failing batch CPU lens.

Both cold banks have no OLD fragment and recorded insert/rebind; both warm banks record original OLD intervals `[90112,96631)` and `[96631,98067)`, lengths6519+1436=7955. All FULL FRESH layers are recorded, and target CPP-key bijection plus source `pending_cpp.pop()`/no bank errors closes the **metadata/source** first-target binding question. There is no direct RPC pending-map cardinality field, physical index equality or K/V metric acceptance here. Actual device payload correctness remains unverified.

## Decisive source/receipt locations

All generated references below are relative to `evidence/teacher-scoring-kv-coherence-probe-20261111/native/{A,B}/admission-{A,B}-r2/` (A line numbers shown; B runtime same relevant body):

- `kv_coherence_source_preflight/after/srt/kv_coherence.py:35`: unqualified `len(rids)==len(prefixes)==len(extends)`; `:136-139` validates lens before bank-RID filtering; `:141-152` note_cpp/fresh reach `_targets`; `:163-174` consumes target key and validates existing stream witness. `:386-392` catches this error and stores RID=null rather than altering serving. `:328-333` requires all16, then returns on `self.errors` before `:345-351` physical/metrics. `:371-381` already uses resolved_dict and initialized correctly.
- `kv_coherence_source_preflight/after/kernels/ops/kvcache/kvcache.py:122-144`: original CPP store returns the stream scalar; actual published `_kv_batch` is passed to note_cpp and then the WIT record reads **that same local batch object's** host fields. This places the recorded null pattern at the error seam, not in a different extractor snapshot.
- `kv_coherence_source_preflight/after/srt/mem_cache/memory_pool.py:2995-3017`: same producer's common poststore terminal, same ordinary getter, host receipt, then FRESH callback before free; no alternate getter.
- `kv_coherence_source_preflight/after/srt/model_executor/model_runner.py:2032-2043`: publishes the passed ForwardBatch in the real context scope; `:2085` eager prep stays inside it, `:2128-2132` eager runner dispatch; `kv_store_stream_source_preflight/after/srt/model_executor/forward_context.py:51-71,86-101` provides exact save/publish/get/restore implementation used in replay.
- Startup A WIT seq184/185, process340: ordinary RID `f4a4161dc7d34b3db69f486204a4234a`, both lens None, writer length1. B seq118/119, process347: ordinary RID `02bc86ba4f6d4b30b43a884c32a0e820`, same pattern. Selected full rows are in `receipt_counts.json`, not invented fixture data. A scoring seq566/567 and B368/369 are the valid counterpart.
- A `server.log:220-224`: native80-token prefill, successful localhost `/v1/chat/completions`, then ready; `:233-237`: separate health-check1-token prefill and startup readback; `:244` begins actual8192-token business scoring. Startup translated records show one warmup RID across eight passes, then a distinct `HEALTH_CHECK_*` RID. No business RID is substituted by the replay.

Narrow retained immutable source references, relative to `evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source/`:

- `srt/model_executor/forward_batch_info.py:670-672` defaults both EXTEND CPU mirrors to None; `:1103` constructs nonempty request RIDs independently. `:1227-1247` DECODE/target-verify position path does not populate mirrors; ordinary list-backed EXTEND populates them, while the explicitly described gpu_only EXTEND branch also leaves mirrors unset. No full runtime/model bootstrap was performed.
- `srt/entrypoints/http_server.py:2452-2457,2494,2535-2547` performs normal startup generation with max_new_tokens8 (chat VLM branch max_tokens8). Seven subsequent one-token passes agree exactly with112/70 null-layer records. Actual WIT lacks a forward_mode column, so the runtime mode attribution is source/event inference, not an observed native enum flag. Speculation is None and graphs disabled in the startup receipt; no graph/surrogate theory is required.
- `srt/model_executor/forward_batch_info.py:228-236` supplies the existing `ForwardMode.is_extend()` domain predicate; it includes MIXED/target-verify/split/dLLM categories. Do not create model-string or ad-hoc classification.

Repository AGENTS/REVIEW and relevant rules, current requirements/plan, GLOSSARY were read. No `docs/adr/*` exists. Master requirements/plan's last submitted/Starting paragraph is an earlier snapshot; the explicit primary messages reporting both terminal failures steer this diagnosis. Updating shared status docs is outside this owner scope.

## Proposed minimal route — not implemented

Primary recommendation: use the **existing authoritative ForwardBatch mode predicate** to qualify the EXTEND writer-observer scope **before** asking for EXTEND host lens. Non-EXTEND native decode is not an8192-token target writer and should not create a global capture error merely because its EXTEND-only mirrors are absent. For an actual EXTEND/scoring path, preserve strict RID/lens validation and fail-loud diagnostics (including missing/malformed values), selected bank matching, CPP pending key/stream verification, and all physical/numeric gates. Verify the recorded DECODE-compatible counterpart plus valid EXTEND and missing-field real EXTEND at the same generated/context seam before any future fix is accepted.

Alternative: no software change until primary demands direct mode evidence; existing receipts do not explicitly record forward_mode, so a strictly direct native enum claim would require a separately authorized focused observation. This option has higher verification cost; no such observation/run is performed here.

Reject a blanket None return, warmup-RID string skip, bank-not-selected prefilter that would hide malformed genuine scoring metadata, error-array clearing, disabled error gate, synthesized CPU lens, alternate getter/backend, new flags/waits/sync or serving fallback. gpu_only EXTEND, target verify, graphs, CP/other TP and concurrency remain unsupported/unqualified as before; they are not made silently valid by this proposal.

Phases1-4 diagnosis are complete; phases5-6 production fix/regression cleanup are intentionally not started because primary has not selected a fix. Original RED remains reproducible. Scoring parity/root, physical7955 index equality, K/V metrics, CUDA race/GIL/model or formal acceptance remain pending.
