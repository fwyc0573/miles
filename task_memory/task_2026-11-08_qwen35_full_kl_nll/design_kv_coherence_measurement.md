## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Accept zero-GPU Rust source/provenance retention and identical candidate inputs; separate the completed source dependency from pending original-tensor observer, producer and runtime qualification. |
| 2026-11-11 | Consume accepted A/B native CPP witnesses; specify RID-bound two-bank payload/index captures, exact budgets, post-loop drain, physical alignment checks and bounded CPU/native qualification. |
| 2026-11-11 | Correct the executable OLD seam: both native runs use RustUnifiedTreeCore, not the Python insert walker. Mark original pre-split OLD capture BLOCKED on the version-matched Rust implementation/observer, without changing backend or substituting a post-insert measurement. |
| 2026-11-11 | Bind A's partial-overlap target independently from its original native RID and unique checkpoint receipt keys. |
| 2026-11-11 | Correct the nonexistent forward-batch accessor; authorize minimal diagnostic context publication and distinguish CPP from Triton prefix-valid witnesses. |
| 2026-11-11 | Qualify the selected allocator and both FFI stream-source branches; select witness-only preparation before numerical capture. |
| 2026-11-11 | Record complete installed allocator/Cython source and independently verified live CPU host-field carry; payload capture remains blocked on final qualification. |
| 2026-11-11 | Record the proposed two-stage KV capture, three unresolved review prerequisites, complete source retention and diagnostic limits. |

# KV coherence measurement proposal

Status: **A/B bounded CPP witnesses and retained Rust source/provenance ACCEPTED; selection/budget/FRESH/readback protocol specified; executable original pre-split OLD capture BLOCKED on the actual Rust observer, producer and runtime qualification. Payload capture and formal 04/05 remain unaccepted.**

TaskID: `profile-kv-recurrent-coherence-measurement-design-20261111`. This design consumes primary acceptance of the bounded native witnesses and retained Rust source/provenance, not authorization to run a numerical collector. Shared requirements/plan are maintained by their existing owner; older running-witness entries remain history.

This is D40 correctness RCA, not a new training/evaluation population, cache fallback or science change. Rank the remaining candidates as: (1) canonical KV payload versus the current recurrent trajectory; (2) erroneous live varlen checkpoint values despite the selected-FP32 path; (3) slot lifetime or GPU ordering. Index-storage ownership is not KV-payload truth. This revision does not re-audit or change the earlier H_index disposition.

## Accepted evidence and its limits

Paths are relative to this task directory. `S` below means `evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source/`; `M=S/srt/mem_cache`, `R=S/srt/model_executor`. `W_B` means `evidence/teacher-scoring-kv-stream-witness-probe-20261111/native/B/admission-B-r1/kv_store_stream_source_preflight/after/`. `C_B` is the retained CPU-metadata cache/boundary overlay at `evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1/runtime_metadata_source_preflight/after/`; it is used for instrumentation-site references, not as a substitute for the accepted final WIT context.

| Witness | A | B |
| --- | --- | --- |
| Native job | `exp-1111-113511-067358` | `exp-1111-113511-669312` |
| Business reproduction | 16/16 vectors exact, 6,804 values | 16/16 vectors exact, 6,804 values |
| Workload / terminal | 16 requests / 10 flushes; four actual H800; Completed0/restart0 | Same |
| Actual allocator | `TokenToKVPoolAllocator`, page1/CP1 | Same |
| Responding-process CPP/terminal joins | 2,704 unique joins / 169 chunks / 16 FULL layers | 1,690 / 169 / 10 FULL layers |
| Global FULL layers | 3,7,...,63 | 3,7,...,39 |
| Recorded in-call native stream = Torch F | PID391: `1266433792` | PID335: `655895424` |
| CUDA Triton prefix-valid KV terminals | 0 startup and business | 0 startup and business |

Sources: [A report](test_report_2026-11-11_kv_stream_witness_native_A_results.md):27-44,77-94; [B report](test_report_2026-11-11_kv_stream_witness_native_B_results.md):50-68,94-116; [A JSON](evidence/teacher-scoring-kv-stream-witness-probe-20261111/native-verification-A.json); [B JSON](evidence/teacher-scoring-kv-stream-witness-probe-20261111/native-verification-B.json). Primary accepts the bounded WIT result even where the report's original acceptance text predates that decision.

The fixed source composition is caller `26664e81`, witness helper `79dba51b`, 35 qualified final paths / five witness edits; six attention-math identities remain unchanged. Raw `native_compilation=UNVERIFIED` stays truthful: successful integer-return ABI and nonempty CPP specialization were observed, not a fresh-build/binary hash or CAPI-versus-fallback classification. Those missing classifications do not negate the observed actual resolved scalar. Stream equality is not completion, PDL readiness, global TP or numerical-coherence evidence. Do not hard-code these run-specific stream IDs into the next collector.

The final WIT `ForwardContext.forward_batch` is real, published through the existing `replace`/restore scope (`W_B/srt/model_executor/forward_context.py:39-48,86-101`). It was not exposed by the original pre-WIT manager. Use this owner; add no global eager getter. Triton stream remains UNVERIFIED if a later path actually selects it.

## Controlled workload and target identity

Keep the original unsalted first four fixtures, repetition0, sequential order, 16 scoring requests and 10 flushes per pair. Do not add salt, explicit native RID, seed, warmup, namespace, or scoring payload fields. Cache, dtype, grid/interval, sampling, concurrency, PDL flag and native dependencies remain unchanged.

Target fixture: sample1695, opaque UID `00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6:5:127`, original input98942, FULL scoring start0. Window parameters from the accepted fixture/receipts are `P=90112`, `E=98304`, capacity `R=E-P=8192`. The original shared target has returned end `Q=98067`, hence 7955 old rows and237 new-suffix rows. Q is recorded dynamically, not used to choose a request or manufacture a join.

- A original target proof: [JSON](evidence/kv-coherence-target-A-20261111.json), RID `4b0a4f32c0a4431a964188b979fd3719`, rows21138/21141/21142. Its accepted WIT counterpart has RID `c1745ed1548e4b12885700dc3d5c0617`, scheduler25695 and layer3 CPP25707/terminal25708. Old/new RIDs are not interchangeable.
- B accepted WIT target RID `ea2093c6cc3f4c1e98b42fa0b9ef4e92`; begin16557, returned16560 and rebind16561 independently supply P/E/Q. Row numbers are evidence references, never pairing rules.

### Selection before the OLD decision

The writer has no Req, and native RID is unknown before send. Register candidates from the actual CPU Req beside the existing `scheduler_track_boundary` emission, before forward submission: `return_logprob`, `logprob_start_len==0`, and `len(req.origin_input_ids)==98942`; preserve `req.rid`. Req's actual field is `origin_input_ids`, not an invented `original_input_ids` (`S/srt/managers/schedule_batch.py:1091-1095`). The instrumented prepare method is `_mamba_radix_cache_v2_req_prepare_for_extend`, with boundary emission at `C_B/srt/managers/schedule_batch.py:3142,3239-3260`.

Exactly two distinct RIDs satisfy this predicate in the fixed16 loop: cold-full and warm-full sample1695. Allocate two opaque banks and bind a free bank to each RID once. Allocation order is not phase identity: never label bank0 cold, infer warm from Q, or overwrite a bank. Store only CPU keys, not a retained Req/InsertParams object. Arm its FRESH window only on the matching `(RID,prefix=P,extend=R)` chunk.

After all responses, map each bank RID through `requests.jsonl.native_request_id == meta_info.id == completion_scores.native_request_id`, then through `(pair, source_uid, sample_index, repetition, phase, mode)`. The actual request schema uses `input_count`, `logprob_start_len`, global `sample_index=1695`, local `sample_position=2`, and phases `cold` / `warm_stream` (not `cold_request`). Offline inspection finds two eligible full-input RIDs per pair: A cold `39d26b2d48454ea4820b92cb70d7dc13` / warm `c1745ed1548e4b12885700dc3d5c0617`; B cold `84fff0a5acdb465bb4653a1aed484a33` / warm `ea2093c6cc3f4c1e98b42fa0b9ef4e92`. These are historical checks, not next-run constants. Require exactly the two expected logical full-input cases, zero retractions and unchanged input/scoring descriptors. Unexpected/missing candidates make diagnostic evidence insufficient; do not alter or retry serving to force them.

## Pool topology and writer binding

The allocator's live root is `HybridLinearKVPool`; the writer is its distinct inner `MHATokenToKVPool`. Equality of their object IDs is wrong. Source ownership is explicit: `S/srt/mem_cache/memory_pool.py:4281-4306` assigns/constructs `root.full_kv_pool`; `4352-4357` publishes `model_layer_ids` and `full_attention_layer_id_mapping`.

At the proposed collector initialization, after native backing finalization and before requests, record one CPU topology receipt from simultaneous live objects: actual allocator/module/page/config, `allocator.get_kvcache()` root, `root.full_kv_pool`, global-to-dense mapping, and each inner K/V shape/stride/dtype/backing pointer. Verify each later writer `self` is that same live child and uses the mapped buffers. This closes the historical absence of an explicit runtime parent link without treating recycled IDs as permanent keys.

Consume the existing scoped batch's `rids`, `extend_prefix_lens_cpu`, `extend_seq_lens_cpu`. For row i, let `offset=sum(extend_lens[:i])`, `lo=max(P,prefix_i)`, `hi=min(E,prefix_i+extend_i)`. Writer rows are `[offset+lo-prefix_i, offset+hi-prefix_i)`. Keep CPU row index tied to its actual RID array. Accepted native batches each have one RID; verify, do not infer identity from that count.

Reuse the accepted complete CPP/terminal key `(rids,prefix_lens,extend_lens,Kptr,Vptr,writer_loc_ptr)` plus writer descriptor within a live process/call. A small target-only CPU map can carry the existing CPP scalar to the matching class terminal; duplicate or absent keys do not authorize capture. Do not read the FFI context after return, use a sequence-adjacent CPP row, or scan the entire receipt history on every store.

## FRESH and index capture specification

Use only the currently exercised ordinary CPP/NHD class-owned post-store terminal: `W_B/srt/mem_cache/memory_pool.py:2993-3014`, after the unchanged `_store_kv_layer` call (`3016-3063`). Immediately gather physical rows from `self.k_buffer[dense]` / `self.v_buffer[dense]` using the same writer `loc` slice; copy writer locations into that layer's int64 receipt. Perform both on the original F stream, using preallocated output slices. Require the matching existing in-call CPP scalar to equal the current Torch F stream and indicate a nonempty launch before adding gathers. Native store has already launched; this is an observer/arming check, not launch-before preflight or stream correction.

Freeze all R rows for both candidates before Q is known, all measured FULL layers and local heads. Fresh payload must never be gathered after `insert()` returns or at rebind: duplicate slots may already be released. The earlier loop may already have queued a later chunk; immediate producer capture is essential.

At the cache bridge, materialize the existing inline InsertParams constructor as a local `insert_params` without changing its arguments, then before `self.insert(insert_params)` copy the actual FULL `insert_params.value[P:E]` into its preallocated receipt on S (`M/unified_radix_cache.py:1230-1238`; `C_B/srt/mem_cache/unified_radix_cache.py:1239-1249`). This tensor is the real int64 copy. Metadata field `insert_value` refers to `mamba_value` and cannot substitute for it.

At the native rebind site, copy `new_indices[P:E]` on S alongside the unchanged mapping write (`M/unified_radix_cache.py:1284-1298`; `C_B/srt/mem_cache/unified_radix_cache.py:1304-1326`). Record the dynamically returned Q, rotation status and direct RID. These are index-byte copies, not post-free fresh-payload reads.

Carry `(collector,RID,P,E)` with the exact insert invocation, independently of Q/node/result: the Python InsertParams dataclass is nonslotted (`M/base_prefix_cache.py:75-108`), so a diagnostic-only transient attribute is possible without modifying key/value semantics. However, the actual Rust adapter reconstructs a native binding with enumerated fields; it does not forward that attribute. Any future qualified OLD native observer must receive the same plain context explicitly. Do not pretend the attribute alone reaches Rust.

CUDA prefix-valid KV terminals are not selected in WIT and are excluded from the first numeric collector. Unexpected selection is unsupported/insufficient, not a reason to implement a generic Triton path or force a CPP fallback. A separately authorized future path would need its own stream witness and per-row CUDA `commit_lens` receipt; CPU `num_rows` is capacity, not proof of valid rows. No such value capture is part of this revision.

## OLD specification and the newly identified executable blocker

The required observation is the original, live FULL index tensor before the native walker splits/retains the node. For each live matched fragment, derive its absolute interval from the native walk's total-prefix position and matched prefix length, intersect with `[P,E)`, and gather all FULL-layer K/V into the corresponding OLD output rows on S. Copy the exact same original index slice into the OLD int64 receipt. No collected path tensor, fresh value, post-insert rebind tensor, new split clone or Mamba value is an original-node substitute. Do not fill uncovered rows and call them equal.

The pure-Python candidate would be after `prefix_len` calculation and before `_split_node` (`M/unified_cache/unified_tree_core.py:1282-1294`); its FULL value is `node.component(BASE_COMPONENT_TYPE).value` (`159-172`, `component_type.py:31`), not an assumed `node.value` property. **That is not the executed backend in these runs.**

Decisive actual-path evidence:

- B WIT `server.log:120-121` and A `server.log:126` identify TP0 `RustUnifiedTreeCore` with FULL+MAMBA; neither switches to the Python core for this diagnostic.
- `M/unified_cache/tree_core_registry.py:153-168` constructs Python and Rust separately.
- `M/rust_tree_core/adapter.py:308` implements `UnifiedTreeCoreInterface`, not Python `UnifiedTreeCore`; `801-829` calls the native binding's begin/resume directly. Therefore a Python `_insert_walk_step` patch produces no valid OLD evidence.
- `adapter.py:524-531` raises `NotImplementedError` for `node_by_id`/`root_node`; `796-799` exposes collected path indices, not a demonstrated original pre-split per-node tensor.
- `M/rust_tree_core/extension.py:11-29,33-39` loads `sglang.srt.mem_cache.rust_tree_core.mem_cache`; the corresponding crate is repository `rust/sglang-radix-tree`. The original 5,501-file Python-package archive excluded `.rs`; that selection never proved absence on the worker.
- Zero-GPU `exp-1111-124522-553024` now retains the Rust workspace under `evidence/native-rust-source-20261111/exp-1111-124522-553024/checkout/rust/`. Primary accepted 621/621 retained hash/size checks, the original 5,501 unchanged files and the filtered GPU0/Completed0/restart0 platform proof. Checkout and both Git candidates (`056f871a7ee8b4573832049011f0fdf52589cfd8`, `297e54fd105e974cdf401e5b4d20253a22c16f90`) have identical 206 selected inputs; the isolated radix crate has 22 files/19 Rust files with no concrete missing source input. See [source report](test_report_2026-11-11_rust_binding_source.md) and [verification](evidence/native-rust-source-20261111/source-verification.json).
- The production bundled `.so` was actually loaded without CUDA initialization: 3,399,272 bytes, SHA-256 `2c1e54965c8139358df1ef2a7751620c339ad1ff4988cee54cc35467a8b90f6c`, GNU build ID `849599cc340045a6ed34eb52de0fdc2a3ff9a236`. Binary source commit remains **UNVERIFIED**: paths/compiler strings and differing checkout/base labels do not identify it. `SGLANG_RUST_BUILD_MODE=never` trusts the bundled module; Rust source edits alone would not execute. Source retention and successful import are not observer/runtime acceptance.

**Remaining dependency:** qualify the retained native insert/FULL implementation and an existing or purpose-specific production observer that supplies the original FULL tensor, absolute range and insert context before split/free. Establish the original index tensor's producer/dependency and execution on the scheduler's S thread; a callback location or held tensor reference alone does not prove readiness of a native clone on an unknown stream. Any new native ABI requires its own compile and behavior checks. Do not invent a getter, substitute a concatenated path for the original tensor, or use the test-only inspection extension as a backend replacement. No further source collector is indicated by the selected radix inputs.

Primary choices, neither performed here:

1. Use the retained native sources to qualify an inline observer on the same S thread before the original split/actions, without changing key decisions, locks, waits or cache policy. Then validate the unchanged native outputs after installing the diagnostic overlay.
2. Explicitly approve a different measurement question using post-insert actually adopted canonical slots through existing collected indices. That is not the required original pre-split measurement; provenance/lifetime would need its own qualification. Do not silently substitute it.

Until choice1 is qualified or the question is explicitly revised, the two-sided native numerical arm is **BLOCKED**. The completed zero-GPU source read did not perform a payload probe, observer implementation or backend change.

## Existing dependency and slot-lifetime argument

The intended observer adds work only at the original producer/dependency join:

```text
F.wait(S) -> native forward/store -> immediate FRESH(F)
S.wait(F) -> result callback -> original-node OLD(S)
S: native split/free/index bookkeeping
next F.wait(S) -> subsequent physical payload writes
```

C2 scheduler:2023-2025 establishes callback S;2032-2038/2122-2135 provides the native coarse dependency for normal EAGER EXTEND;4696-4697 supplies next-F's native S gate. Preserve the original PDL flag. An ordinary non-PDL gather remains behind completion of its same-stream store; a PDL trigger is not permission to read early.

Actual WIT allocator/config now supports applying `M/allocator/base.py:284-293`, `M/allocator/token.py:42-75`, `M/allocator/base.py:217-233`: free/clear/alloc/group/sort manipulate indices, not KV payload or another-stream compaction. CPU ID release can precede gather completion without a physical overwrite because future writers wait on S. Native backing remains alive; memory-saver/unified/hicache/sharding are off. Startup finalization (`R/model_runner_components/kv_pool_runtime.py:151-155`) is not student TrainTMS or per-request payload freeing.

Retain original index references through gather enqueue; they protect index storage, not slots. Add no lock, CUDA event, wait, query, synchronization, `record_stream`, forced FFI context or cache-policy branch. The argument requires the actual native OLD seam to be at the stated frontier; it cannot turn an unreachable Python hook into a qualified observation.

## Preallocation: two opaque banks, actual A and B budgets

Allocate after native KV capacity/backing is finalized, before any scoring request. Do not reduce that capacity or allocate transient gather results. Use `index_select(...,out=preallocated_view)` or equivalent ordinary same-stream copies. Derive R from the retained target window; layer counts, row shapes/bytes and mapping from the actual pool, not a fixed ten-layer assumption.

Each bank holds FRESH K/V and OLD K/V for every FULL layer and all R rows. Accepted descriptors are BF16, one local head, dimension256; each K row and V row is512 bytes. Two banks avoid discarding a candidate based on inferred phase/chronology. The cold bank's unwritten OLD region is never read as numeric data.

| Pair | FULL layers | Payload per bank: `2*R*L*(512+512)` | Two-bank payload | Int64 receipts: `2*(L+3)*R*8` | Explicit allocated total |
| --- | --- | --- | --- | --- | --- |
| A | 16 | 268,435,456 bytes =256 MiB | 512 MiB | 2.375 MiB | **514.375 MiB** |
| B | 10 | 167,772,160 bytes =160 MiB | 320 MiB | 1.625 MiB | **321.625 MiB** |

The int64 allocation includes writer locations per layer plus one OLD, FULL-insert and rebind vector per bank. CPU coverage intervals, layer-presence masks and keys are small metadata. Keep only needed source index references through enqueue, not whole Req/InsertParams/Mamba-state objects until drain; avoid additional persistent native index-storage retention. Pool tensor objects themselves remain natively owned. Runtime shapes/dtypes must agree before using these estimates; insufficient memory is a readiness issue, not permission to shrink coverage silently.

## Post-loop readback and physical qualification

All capture-time operations are GPU stores into the preallocated receipts or CPU metadata. No CUDA `.item()`, `.cpu()`, `.tolist()`, explicit synchronization, new event/wait, or critical-path file logging. No SSM pre/post sample: the callback may already follow a later submitted forward and does not establish equal token boundaries.

Use the existing post-loop `/server_info` route and internal-state RPC, with a proposed diagnostic-only `kv_coherence_drain` request marker defaulting false. Startup/normal getters remain CPU-only. Only the caller after all16 successful scoring responses requests the one-shot numeric drain; record that lifecycle and the distinct completed RIDs in CPU metadata. Completion bookkeeping is not request identity or device-completion proof. Reject an early/incomplete drain without CUDA readback.

This marker is a small extension of the existing readback path, not a new endpoint, compute/cache flag or generic framework: `http_server.py:854-879` -> `tokenizer_control_mixin.py:1122-1129` -> currently empty `GetInternalStateReq` (`io_struct.py:2442-2450`) -> `scheduler_components/internal_state.py:45-63`. Its API plumbing is a required future implementation detail; the existing empty request cannot already carry it. Keep inherited/formal diagnostics opt-out and all scoring payloads unchanged.

Selected captures occur before multiple later forwards in the fixed loop. Those native F.wait(S) dependencies and completed subsequent scoring responses establish the target S work has ended; immediate FRESH work is before its producer's native scoring completion. The post-loop controller performs permitted D2H only then, on S, without adding an explicit wait. Compute metrics layer-by-layer on CPU and return compact scalar metadata through the existing dict response; do not serialize hundreds of millions of payload elements into JSON or add a large raw archive. Cache the drained summary for later CPU-only reads.

First qualify physical rows, without selecting a pairing using the equations being tested:

1. Within each RID, bind begin/rebind by their independently emitted page-aligned end when unique; bind returned/rebind by RID/node/result-prefix signature when unique. Node IDs are not request identities. Never choose begin because Q equals P. Require the selected `(RID,P,E)` invocation and dynamic Q to be complete/unambiguous.
2. Per FULL layer, frozen writer locations equal frozen real FULL `InsertParams.value[P:E]` exactly.
3. OLD fragment intervals cover `[P,Q)` once per layer, with no gaps/duplicates/restored-from-fresh substitution; for the warm target expect7955 rows dynamically confirmed, not zero-initialized evidence.
4. Frozen original OLD indices equal frozen actual rebind indices on `[P,Q)` exactly; rebind's new suffix equals frozen insert indices on `[Q,E)`.
5. Validate bounds/dtypes and the mapped physical buffer topology. A mismatch disqualifies the proposed same-row old/fresh interpretation; it is not automatically a diagnosed historical corruption.

Then compare K and V separately for every warm FULL layer, all7955 rows, all local heads/dimensions. Report numeric exact equality, mismatch count, maximum absolute error, maximum relative error using OLD as reference, undefined count where OLD is zero, and nonfinite counts. No epsilon, scale correction or new tolerance. Preserve layer/token/head/dimension and values for extrema. With two banks, cold-FRESH versus warm-FRESH at the same coordinates is an optional descriptive comparison using already captured data, not an additional run or SSM oracle. Cold OLD with no actual overlap remains absent.

## Expected falsifiable interpretation

- All16 completion vectors/token IDs and original comparison records must reproduce the accepted WIT/baseline exactly, including existing warm errors. If not, the instrumented run is not equivalent and cannot exclude ordering/races. Exact reproduction is necessary, not sufficient to exclude a race.
- Qualified nonzero OLD/FRESH K or V differences establish a local physical difference at actual adoption. They support candidate1 but do not prove an invalid SSM state, warm causality, earliest divergence or a fix. Existing shape/chunk-dependent arithmetic may contribute.
- Complete local equality narrows candidate1 only for this checkpoint/TP0/full-layer span. It does not exclude earlier adoption, live checkpoint-value errors, later slot/order failures or other TP ranks.
- Missing OLD native observer, stream mismatch, unsupported terminal, incomplete topology/index alignment or changed geometry means insufficient evidence, not numerical equality. Do not force a stream, add a wait/lock, widen tolerance, change cache policy, or stop native training through an auxiliary verdict.

This first measurement is KV-only. No active SSM, fresh independent200 acceptance, formal cache-off/salt fallback, science changes or mandatory original56 gate. Formal04/05 remain HOLD; cold/startup source checks, CPP ABI execution and zero-restart platform success do not lift it.

## Minimal future patch and qualification plan

No files below are edited by this task; this is the proposed ownership list, contingent on the OLD source blocker/primary decision.

- One purpose-specific manual helper/preparer, `tests/manual/agent_opd/sglang_kv_coherence.py`, plus focused CPU tests and the existing probe's isolated numeric configuration. Reuse selected-FP32 -> CPU metadata -> accepted WIT composition; archive reversible before/after identities and keep six attention-math hashes and original CPP kernel/PDL launch unchanged.
- Native initialization/topology and FRESH: existing `model_runner.py` finalization and `memory_pool.py` ordinary class terminal. Reuse WIT's published ForwardContext and in-call scalar; a small target-only note at `kvcache.py` can pass the existing scalar without another bridge/native ABI change.
- Candidate registration: existing `schedule_batch.py` boundary. FULL insert/rebind bytes and direct invocation context: `unified_radix_cache.py`. The Python `unified_tree_core.py` is **not** an executable OLD patch for Rust; actual OLD requires the version-matched native seam identified above.
- After-all readback only: the existing HTTP, tokenizer-control, IO request and scheduler internal-state files carry the manual marker and compact summary. No separate endpoint, runtime cache switch, training gate or per-critical-path file writer.

CPU tests should cover: two candidate RIDs allocated in either order; response-only exclusion; RID-to-logical-case binding; bank exhaustion/missing cases without serving modification; flattened row offsets; 16-layer A versus10-layer B budgets; unique independent checkpoint/CPP joins with negative mismatches; fragment coverage and dynamic-Q clipping; pre-free FRESH ordering; original OLD source and before-split ordering on the actual backend; scoped batch restoration; early drain performs no CUDA content operation; all16-before-readback; strict opt-out; and zero-reference/nonfinite metric rules. Fake Python walkers cannot claim Rust-native coverage. Reuse existing tests; add no generalized framework.

Native arm conditions: OLD seam/source and same-S call path qualified; prepared source pins/composition reviewed; CPU tests pass; actual allocator/config/topology and CPP stream witnesses match; bounded banks allocated after native capacity selection; primary authorizes the one original16/10 H800 diagnostic. Native adequacy additionally requires all16 original vectors exact, all target layer/index/7955-row coverage complete, and post-loop-only D2H. None are claimed completed by this design revision.

## Readiness, records and scope checkpoint

Completed prerequisites: primary-accepted WIT A/B, actual selected allocator/CPP streams, published host context, source-level root/child topology and retained Rust source/provenance. Specified deliverables: selection, two-bank budgets, FRESH/indices, desired OLD range, physical checks, after-all transport/readout and falsifiable interpretations. Remaining observer qualification and implementation work are not acceptance evidence.

**Critical blocker:** the actual Rust original-node/pre-split observer and producer/thread/lifetime contract remain unqualified. The Rust source dependency is now retained and accepted; do not repeat launcher/FFI/source-fragment investigations, switch backends or reset accepted CPP witnesses. Qualify the required original-tensor observer from these sources, or obtain an explicit revised measurement decision. Shared records must distinguish completed source retention from pending observer/API/readiness; their existing owner handles that synchronization.

The original design-only validation checked source references, candidate cardinality and budget arithmetic offline without Torch/SGLang imports or numerical suites. The later zero-GPU source report/archive and primary replay establish retained-source/provenance acceptance only. Self-check frontier remains D40's original-tensor diagnostic; no payload capture or formal correctness acceptance follows from either check. Earlier progress checkpoints remain history.

### Offline verification of this revision

Environment: local host, workspace worktree, Python3.10.6; standard-library-only script from stdin. Expected: existing evidence links/source paths, two distinct candidate RIDs in each16-row request file, phases cold/warm_stream, sample1695/position2, integer retraction0, and the stated memory arithmetic. Actual: **PASS**, originally five evidence links; the updated design includes two source-verification links. Both pair candidate checks pass; A total514.375 MiB, B321.625 MiB. The original 5,501-file archive still excludes Rust; the new native archive is independently verified by the linked report. This is not collector CPU/native qualification or vector re-verification.

Initial audit assumptions failed with `KeyError: 'input_token_count'` and a phase `AssertionError` from assuming `cold_request`. Raw-field inspection established the actual `input_count` and phase `cold`; the corrected audit passes. These were offline checker/schema corrections, not teacher/runtime fixes.

The final command was `set -e; python3 - <<'PY'` with the following body, followed by the two scoped Git commands below:

```python
import json, platform, re
from pathlib import Path
T = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
text = (T / 'design_kv_coherence_measurement.md').read_text()
assert text.startswith('## Modification History\n')
links = re.findall(r'\]\(([^)]+)\)', text)
for link in links:
    assert (T / link).is_file(), link
S = T / 'evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source'
for rel in ['srt/mem_cache/rust_tree_core/adapter.py',
            'srt/mem_cache/rust_tree_core/extension.py',
            'srt/mem_cache/unified_cache/unified_tree_core.py',
            'srt/mem_cache/base_prefix_cache.py',
            'srt/mem_cache/allocator/token.py']:
    assert (S / rel).is_file(), rel
assert not list(S.rglob('*.rs'))
W = T / 'evidence/teacher-scoring-kv-stream-witness-probe-20261111/native/B/admission-B-r1/kv_store_stream_source_preflight/after'
assert (W / 'srt/model_executor/forward_context.py').is_file()
assert (W / 'srt/mem_cache/memory_pool.py').is_file()
for pair, layers in [('A', 16), ('B', 10)]:
    P = T / f'evidence/teacher-scoring-kv-stream-witness-probe-20261111/native/{pair}/admission-{pair}-r1'
    rows = [json.loads(line) for line in (P / 'requests.jsonl').read_text().splitlines() if line]
    candidates = [r for r in rows if r['mode'] == 'full_input'
                  and r['input_count'] == 98942 and r['logprob_start_len'] == 0]
    assert len(rows) == 16 and len(candidates) == 2
    assert len({r['native_request_id'] for r in candidates}) == 2
    assert {r['phase'] for r in candidates} == {'cold', 'warm_stream'}
    for r in candidates:
        assert r['native_request_id'] == r['meta_info']['id']
        assert (r['sample_index'], r['sample_position']) == (1695, 2)
        assert type(r['meta_info']['num_retractions']) is int
        assert r['meta_info']['num_retractions'] == 0
    payload = 2 * 2 * 8192 * layers * (512 + 512)
    indices = 2 * (layers + 3) * 8192 * 8
    print(pair, payload / 2**20, indices / 2**20, (payload + indices) / 2**20)
print('PASS', len(links), platform.python_version())
```

```bash
git diff --check -- task_memory/task_2026-11-08_qwen35_full_kl_nll/design_kv_coherence_measurement.md
git diff --numstat -- task_memory/task_2026-11-08_qwen35_full_kl_nll/design_kv_coherence_measurement.md
```

The scoped whitespace check passed. No unrelated working-file content was inspected; the only written artifact is this owned design.
