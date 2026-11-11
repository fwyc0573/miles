## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Bind A's partial-overlap target independently from its original native RID and unique checkpoint receipt keys. |
| 2026-11-11 | Correct the nonexistent forward-batch accessor; authorize minimal diagnostic context publication and distinguish CPP from Triton prefix-valid witnesses. |
| 2026-11-11 | Qualify the selected allocator and both FFI stream-source branches; select witness-only preparation before numerical capture. |
| 2026-11-11 | Record complete installed allocator/Cython source and independently verified live CPU host-field carry; payload capture remains blocked on final qualification. |
| 2026-11-11 | Record the proposed two-stage KV capture, three unresolved review prerequisites, complete source retention and diagnostic limits. |

# KV coherence measurement proposal

Status: **STATIC BRANCH QUALIFIED; witness-only preparation in progress. Numerical payload capture remains unaccepted; no new GPU run submitted.**

This proposal serves the D40 correctness blocker in tickets 04 and 05. It does not change the experiment matrix, cache policy, scientific inputs, tolerances, or formal admission criteria. The earlier namespace counterfactual establishes that shared cross-request cache participates in the bounded warm-full deviation; it does not establish numerical incoherence or its cause.

## Question and controlled workload

Compare the fresh physical K/V values written by the current request with the live canonical K/V values that the cache will adopt for the same token positions. Record both actual index sets independently. A tensor reference alone does not protect the physical slots referenced by its indices.

Retain the verified selected-FP32 plus CPU-metadata baseline: first four fixtures, repetition zero, original unsalted payloads and order, 16 scoring requests and 10 flushes per pair. All 16 completion vectors must reproduce their corresponding verified baseline exactly before interpreting numerical receipts. This diagnostic adequacy condition is not a new formal gate. Native execution takes minutes because it retains the actual long inputs and teacher; CPU tests cannot certify the warm deviation.

The first proposed target is B's warm-full sample 2, with checkpoint protected prefix `P=90112`, page-aligned end `E=98304`, and old overlapping prefix end `Q=98067`. Its overlap has `Q-P=7955` rows. Bind the native request through its actual CPU input tokens and scoring range, then join cache calls by `(native_request_id, P, E)`. Verify the target against the existing response RID after all requests. Do not use request counts, node IDs, recycled addresses, or adjacency to identify it. [Independent A CPU verification](test_report_2026-11-11_kv_coherence_target_A.md) establishes the same window for A sample1695 from its own original rows21138/21141/21142, not by copying B's geometry. This identifies a bounded measurement window, not a numerical fault.

## Proposed capture boundaries

1. **Fresh payload:** immediately after each reachable physical store, freeze the selected K/V rows from the full-attention pool on the qualified producer stream, before fresh slots can be released. `_store_kv_layer` alone is insufficient: CUDA `set_kv_buffer_prefix_valid` terminals bypass it. The proposed class-owned capture boundary must also cover those terminals without double-counting the CPU path that already calls `set_kv_buffer`. Retain layer identity, pool buffers and the writer `loc` slice. Use the actual global-to-dense layer mapping and all local KV heads.
2. **Old payload:** before the tree walk splits the existing FULL node, freeze every live fragment intersecting `[P,Q)` on the schedule stream. The original node index tensor avoids reading a just-created split clone. Existing dependencies establish readiness and physical-slot lifetime for the statically selected `TokenToKVPoolAllocator` branch; the actual allocator class and store stream still need runtime confirmation before capture.
3. **Independent indices:** freeze the actual FULL `InsertParams.value[P:E]` and actual canonical rebind indices on their respective producer streams. Existing metadata named `insert_value` contains a Mamba value, not these FULL indices.

Never read fresh slots after `insert()` returns: duplicate ownership may already have been released, and neither payload preservation nor clearing is guaranteed.

## Three prerequisites from source/design review

| Prerequisite | Required proof | Current disposition |
| --- | --- | --- |
| OLD dual-input dependency and lifetime | Each fragment's index producer is covered by an existing dependency, and its physical KV rows cannot be reused before gather finishes. Post-insert locks are not pre-split protection. | Source-qualified for the recorded B configuration's inferred `TokenToKVPoolAllocator`: index bookkeeping does not overwrite KV payload, and the next forward waits on the schedule stream. Actual class receipt pending; no new wait or lock. |
| Actual store launch stream | Resolve the JIT `LaunchKernel`, TVM FFI stream bridge and PDL completion contract. A Python return alone does not prove that a subsequent physical gather is ordered after the store. | Both Cython CAPI/fallback stream-source chains are qualified. Actual in-call stream scalar remains unmeasured; witness-only preparation is selected. |
| Writer row/RID binding | Establish actual CPU forward context, native RIDs and prefix/extend lengths at the store hook. Sum preceding extend lengths to locate flattened rows, slice writer locations consistently, and verify exactly-once K/V coverage for every actual FULL layer. | GDN host-field carry qualified, but the specified global-context batch field is absent. Minimal CPU-only diagnostic publication is authorized; implementation, writer/FULL-index and prefix-valid real-row coverage remain pending. |

The store hook itself has no `Req`. Neither row identity nor stream safety may be inferred from an assumed one-request batch. Missing or duplicate captures must be reported as insufficient.

The earlier writer analysis incorrectly called `get_forward_context().forward_batch` an existing accessor. The complete pinned `forward_context.py:39–47,85–99` has a frozen/slotted context with only `attn_backend` and a MoE getter. Passing `forward_batch` at `eager_runner.py:351` publishes that getter, not the batch. Source preparer report `test_report_2026-11-11_kv_stream_witness_source.md` reproduces `AttributeError` with the real context manager. Do not substitute the graph-only `runner_utils.get_forward_batch()` or infer identity through a bound getter.

Primary authorizes a minimal diagnostic-only field in the existing `ForwardContext` and publication through its existing `dataclasses.replace` call, preserving the existing scope restoration. No second global or receiver is added. This is an in-scope D40 CPU metadata change, not an engine math or synchronization change; its RED/GREEN binding is pending. Native CPU extend lengths and RIDs follow request order, with writer offsets equal to the sum of preceding extend lengths. Actual A/B metadata still proves GDN host carry: 8,112/5,070 allocation rows and 165 prefill-plan rows each have non-null native RIDs/CPU lengths with no mismatches; 169 translated rows carry RIDs only. Those backend observations do not certify global writer-context publication, physical indices or actual store coverage.

The prefix-valid follow-up establishes that CPU calls converge through `_store_kv_layer`, whereas two CUDA terminals call a module-level implementation without a layer index. A class-owned post-store boundary is therefore needed to retain layer identity. For request `i`, compute `offset=sum(extend_lengths[:i])`, `lo=max(window_start,prefix[i])` and `hi=min(window_end,prefix[i]+extend_lengths[i])`; the corresponding writer rows are `[offset+lo-prefix[i], offset+hi-prefix[i])`. Capture both writer locations and actual FULL insert/rebind indices, then compare their values only after the requests. This direct comparison does not require inferring allocator values from source. CPU host-field preservation is qualified; actual CUDA prefix-valid rows are not. `num_rows` is capacity, whereas `commit_lens` controls actual writes. A future selected prefix-valid capture must retain per-row commit lengths on the original stream and inspect them only after all requests; neither a total count nor a critical-path CUDA value read is sufficient.

## Qualified stream join and runtime conditions

The source follow-up identifies the callback on schedule stream `S` and this candidate order using only native dependencies:

```text
F.wait(S) -> forward/store
S.wait(F) -> result callback
S: OLD gather -> split/cache actions
next F.wait(S) -> subsequent payload writes
```

OLD gather on `S` would consume the original pre-split index after its schedule producers and after the existing forward barrier. This avoids consuming a newly cloned schedule index on an earlier forward dependency. The complete source closes the allocator gap for the recorded B branch: `kv_cache_configurator.py:2795–2923` selects `TokenToKVPoolAllocator` for page size 1, CP1, graphs off and the recorded disabled unified-memory/hicache/memory-saver/sharding settings. Disabling unified memory does not disable the unified radix cache under investigation. This is an inference, not a historical class observation.

`allocator/base.py:284–293` routes `free_segment` to `free`; `allocator/token.py:42–75` and `allocator/base.py:217–233` clear, slice, concatenate, group or sort index lists without clearing, moving or deallocating KV payload. No other-stream payload compaction exists in this branch. CPU ID release can precede gather completion without overwriting payload: subsequent forward writes remain behind the existing `F.wait(S)` gate. Startup backing finalization (`model_runner_components/kv_pool_runtime.py:151–155`) is not per-request freeing. These facts do not qualify other allocators or substitute a tensor reference for a slot lock.

The retained launcher resolves a device stream through `TVMFFIEnvGetStream`; the argument context is set for the call and restored on return. Therefore reading the FFI raw stream after `module.store_cache` returns is not an actual-call witness. Complete `tvm_ffi/cython/function.pxi` source qualifies both branches: the factory selects CAPI or fallback at lines 783–799, CAPI obtains the producer's current stream at 204–219, and fallback reads the Torch current raw stream at 284–289. The helper sets/restores that context (`tvm_ffi_python_helpers.h:470–495`), and the launcher uses it (`utils.cuh:397–418,474,493`). The historically selected branch and actual launch stream remain unobserved. Do not force the context. With a qualified identical stream, ordinary non-PDL gather uses normal same-stream completion ordering; PDL early trigger does not authorize it to read before the store finishes.

The package-level source completion Succeeded as `exp-1111-102145-988437`: 5,501 files / 79,478,292 bytes, including 12 Cython files. All manifest hashes/bytes pass, with 1,805 matching prior paths and no repeated path lacking a match. Read-only qualification TaskID `profile-kv-recurrent-coherence-measurement-design-20261111` closes the source gaps above. Source retention or qualification alone does not admit payload capture; no further fragment collector is selected.

## Witness-only stage selected before payload capture

Prepare a pinned source overlay that returns the stream scalar actually used inside `CPPStore.run`, using the existing resolver/raw-stream constructor without changing the chosen stream. The Python custom-op retains its `None` return and appends only CPU tuple metadata through the existing drain. Record the actual allocator class and publish the diagnostic CPU batch field through the existing context owner. Preserve the baseline first4 workload, order, payloads and 16 requests/10 flushes; no KV copy, CUDA tensor value read, new buffer, event, wait, lock, cache/dtype change or new endpoint is part of this stage.

CUDA prefix-valid terminals are separate Triton implementations, not CPPStore calls (`memory_pool.py:3377–3390,3412–3421`). Record their actual selection with CPU terminal metadata, but do not label the Torch current stream as their native launch witness. If those terminals occur without a qualified actual-call stream receipt, coverage is insufficient for later payload arming. Witness-only does not copy CUDA `commit_lens`; the later numerical stage must validate its real per-row values if this path is selected.

Source/integration CPU verification and fixed-diff review precede any bounded H800 witness run. Its acceptance requires all 16 baseline scoring vectors to reproduce exactly and actual stream/class receipts to support the qualified branch. A native stream scalar obtained after launch is not a launch-before preflight. Missing, mismatched or incomplete evidence prevents arming a later payload capture; it must not trigger a stream correction or a fallback. Actual writer/FULL-index equality and any selected prefix-valid real-row validation remain separate numerical-stage requirements. Formal A/B remain paused.

## Buffers and readback

Allocate diagnostic buffers after the native KV pool has selected and allocated its capacity, and before the scoring requests. The maximum window is `E-P=8192` rows. Use preallocated gather outputs; avoid transient gather allocations. Compute the required bytes from actual per-layer shapes, strides, dtypes and local head counts:

`2 sides * 8192 * sum(K row bytes + V row bytes)`.

For illustration only, ten FULL layers with one local KV head, K/V dimensions 256 and BF16 storage require 160 MiB, plus index receipts. This is not an asserted runtime configuration or a replacement for measured shapes.

Startup getters remain CPU-only. Numerical D2H readback is a manual diagnostic drain after all 16 scoring responses. Return per-layer K/V coverage, exact equality, maximum absolute error, maximum relative error with old values as reference, undefined zero-reference counts and nonfinite counts. Add no epsilon or tolerance. The final design must establish producer-stream ordering for the drain as well as capture.

The first round does not sample active SSM state before/after cache callbacks: overlap may already have submitted the next chunk, so the callback does not establish that state is still at `E`.

## Interpretation and stopping rules

- Baseline vectors differ: instrumentation is not equivalent; do not use it to exclude ordering or races.
- Nonzero local KV differences: supports the local coherence candidate, not a causal fix or proof that this is the first divergence.
- All local KV values equal: narrows only this checkpoint, these FULL layers and TP0; earlier adoptions and other TP ranks remain unmeasured.
- Unproven dependencies or lifetime: leave the diagnostic BLOCKED and present a concrete proposal. Do not continue fragmented source fetches, add waits/locks, or silently replace physical capture with a writer-only measurement.

Even exact reproduction cannot exclude a race. Physical slots, all-TP coherence, warm-response correctness, original 56-request/two-repeat coverage, 1024-hit cases, historical causality and end-to-end performance remain outside this proposal's demonstrated scope. No new mandatory 56-request gate is introduced. Formal A/B remain paused.

## Retained source evidence

- `evidence/native-sglang-cache-source-20261111/exp-1111-094840-273565/source.json`: zero-GPU job Succeeded; 67 source files, including 30 store-package files; all hashes/bytes verified, nine prior matches, zero mismatches. It exposed the missing generic launch/bridge dependency.
- `evidence/native-sglang-cache-source-20261111/exp-1111-100210-790198/source.json`: zero-GPU source-closure job Succeeded; 1,537 files / 21,897,427 bytes; all hashes/bytes verified, 97 prior matches, zero mismatches; installed `apache-tvm-ffi=0.1.11`. Complete SGLang kernel and installed TVM FFI source/header retention is not itself launch-stream or runtime qualification.
- `evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source.json`: zero-GPU package-source job Succeeded; 5,501 files / 79,478,292 bytes; all hashes/bytes verified, 1,805 prior matching paths, zero paths without a matching prior copy. Full installed SGLang source and 12 TVM FFI Cython files close the earlier selection omissions; source availability is not execution qualification.
- Submission and terminal provenance remain in the adjacent `kvcache-store-stream-*.json`, `kvcache-stream-closure-*.json` and `allocator-cython-package-*.json` receipts. All three jobs used the pinned formal image, personal creator, local NFS source and zero GPUs.

Read-only design review TaskID: `profile-kv-coherence-design-review-20261111`. Progress checkpoint TaskID: `profile-kv-coherence-progress-checkpoint-20261111`; tickets 01/02/03 PASS, 04/05 BLOCKED, 06 TODO; D1-D7 CLEAR in the inspected window, no new S1-S6 defect. This records progress, not design acceptance.
