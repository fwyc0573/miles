## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Accept the source insertion-point design for CPU implementation; separate native build/staging from physical capture, retain the existing loader, and leave compilation and CUDA qualification pending. |
| 2026-11-11 | Inspect retained native Rust insert/value/binding sources; specify an original-FULL pre-split observer and bounded production-library qualification without implementing or running it. |

# Original FULL indices inside the Rust insert walk

TaskID: `profile-rust-cache-insert-observer-seam-20261111`.

**Decision:** the retained Rust source supplies a precise executable insertion point. No existing Python callback observes that point. Recommend one optional, invocation-bound inline callback at `insert_walk_step_`, after the existing match-length calculation and before its split branch. Keep the original live FULL tensor; do not replace it with concatenation, a rebind tensor, incoming indices, or a split copy. Design is ready for implementation/CPU qualification; the numerical GPU arm is not ready or authorized by this document.

Only this document is written. No native/Python implementation, compiler, Torch import, CUDA operation, GPU/platform/authentication action, delegation, or commit is performed. Requirements and plan were read; the parent KV design's accepted WIT, two-bank population, FRESH/readback protocol, and formal HOLD remain unchanged.

## Evidence boundaries and paths

All paths below are relative to this task directory unless explicitly repository-relative:

- `R = evidence/native-rust-source-20261111/exp-1111-124522-553024/checkout/rust/sglang-radix-tree`.
- `S = evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source`.
- `M = S/srt/mem_cache`.
- `W_A/W_B = evidence/teacher-scoring-kv-stream-witness-probe-20261111/native/{A,B}/admission-{A,B}-r1`.

The primary supplied the completed zero-GPU source-retention receipt and equality of the two candidate revisions' 206 source files. It also supplied bundled `mem_cache.so` size 3,399,272 bytes, SHA256 `2c1e54965c8139358df1ef2a7751620c339ad1ff4988cee54cc35467a8b90f6c`, matching rustc1.99.1, Torch2.14.1/CXX11, and a CPU load with CUDA uninitialized. These are consumed receipts, not independently repeated provenance checks. **The bundled binary's source commit remains UNVERIFIED.** Identical candidate sources and matching ABI prerequisites do not prove either candidate produced that binary.

Actual selected backend is independently visible at `W_A/server.log:126` and `W_B/server.log:120`: TP0 `RustUnifiedTreeCore`, FULL+MAMBA. The production extension is `sglang.srt.mem_cache.rust_tree_core.mem_cache`, not `mem_cache_inspection` (`M/rust_tree_core/extension.py:11-29,33-39`). All native source conclusions below apply directly to R; historical binary equivalence requires the bounded qualification below.

## Observed source contracts

| Contract | Inspected source | Consequence / limit |
| --- | --- | --- |
| FULL owns an actual Tensor | `R/src/node.rs:724-731` stores `Option<Tensor>`; `:253-259` returns `&Tensor` / `Option<&Tensor>` for the component's device slot | FULL is not a host list or a Mamba state. The observer can borrow the exact Tensor stored on this node. |
| Shape follows the node's key | `node.rs:558-586` asserts value length equals `key.atom_len()` for non-single-state components | With actual page1 and ordinary keys, node-relative row j is absolute token `cursor+j`. |
| Initial FULL index producer | `M/unified_radix_cache.py:1178-1180,1230-1238`: actual request mapping, then `.to(dtype=torch.int64, copy=True)`; `R/src/python_bindings.rs:1161-1177`: `PyTensor` extraction; `unified_tree_core.rs:1839,2163-2174,2454`: narrow, then `value.copy()` into a new FULL node | Native FULL storage is an independent index copy, not merely the request mapping's lifetime. This is index storage, not copied KV payload. |
| Other reachable FULL producers | `unified_tree_core.rs:2484-2485`: fresh restoration copy; `node.rs:612-622`: split takes old value and copies both halves | Existing matched nodes may have indices produced by earlier native insert/split calls. A restored current fragment is not OLD; a new split copy is not the required original source. |
| Python bridge | `python_bindings.rs:120-155`: `Tensor::pyobject_unpack` and `pyobject_wrap`; `:1397-1411`: getter shallow-clones before the same wrap | Crate code performs no deep copy during the bridge. Zero-copy storage/TensorImpl semantics depend on tch/torch-sys; their implementation bodies are not retained in R. Pointer/alias qualification remains required. |
| Synchronous native driver | `python_bindings.rs:1154-1196`: begin/resume use `py.detach` closures calling `self.core().try_*`; `:964-1001`: existing Mutex; `unified_tree_core.rs:1773-1781,1902-1961`: inline state-machine loop | PyO3 detach releases Python attachment on the caller thread; it is not a worker-spawn API. No crate-owned thread/stream handoff occurs on this route. Runtime thread/TLS-stream observations are still required for the diagnostic build. |
| Exact observation frontier | `unified_tree_core.rs:1965-1986`: cursor, matching child, borrowed node, prefix length, then `split_node_` | Call the observer immediately after line1984, before line1985. No extra lookup, read lock, alternate match, or changed match decision is needed. |
| Actual split mutation | `unified_tree_core.rs:2327-2348`: key/parent updates then component redistribution; `components/full.rs:80-98` → `node.rs:612-622` | The callback precedes key/value redistribution and both deep index copies. Leave the existing `touch_node_` at line1982 unchanged: recency has already been touched, but FULL storage is still the original. Do not claim observation precedes every CPU metadata mutation. |
| Duplicate release source | `unified_tree_core.rs:2073,2095-2121`: frees are narrow views of `state.value`; `cache_action.rs:140-150`: FULL free/split actions are non-barriers | These are the inserting request's duplicate indices, not a pre-split OLD carrier. FULL frees do not generally create a resume opportunity. |
| Observer persists through barriers | `unified_tree_core.rs:286-312,1903-1915,1927-1931` owns/saves/takes insert state; `M/unified_radix_cache.py:661-687` applies step actions and resumes synchronously | Invocation context belongs in the actual walk state, not a process-global current Req or a new action. Existing actions and barrier decisions remain unchanged. |

The runtime crate scan found no Rayon/thread spawning or CUDA stream/event selection in the inspected non-test Rust sources. This is a source-level negative finding, not proof about an unmatched historical binary or every internal libtorch kernel implementation. Ordinary ATen CUDA narrow/copy/gather uses current-thread stream dispatch; actual stream identity must be witnessed, not hard-coded.

### Existing getters do not solve selection

`get_component_device_value` is a real original-storage candidate: native core returns `Option<&Tensor>` (`unified_tree_core.rs:4966-4974`), binding shallow-clones that reference (`python_bindings.rs:1397-1411`), adapter exposes it (`M/rust_tree_core/adapter.py:1237-1240`). It does not supply the insert's matched-node sequence or cursors. Calling it during the held native Mutex would reacquire that Mutex and can deadlock.

The read-only FULL matcher exists (`unified_tree_core.rs:1366-1400`, binding `:1052-1063`), but returns only `(matched_len, terminal_node_id, pinned_len)`, not every matching node/span. Python `node_by_id`/`root_node` remain unsupported (`adapter.py:524-531`). A separate pre-walk would add tree-lock calls and duplicate native matching, contrary to this scope.

The previous pre-insert `req.last_node` proposal is withdrawn. A prefix boundary at P does not select the deeper Q path. Moreover `collect_full_device_indices` explicitly concatenates node shallow-clones (`unified_tree_core.rs:1676-1695`); even if enough rows existed, that result is not the original live Tensor. Component overlap hooks run after the split (`:1951-1956,2075-2091`), FULL inherits the default no-op overlap hook, and eviction actions do not identify the required insert fragments. No existing resume/component/collector API qualifies this observation.

## Proposed callback: one purpose, one insert

This is a patch contract, not an implemented API.

1. At the actual checkpoint bridge, name the existing inline Python `InsertParams` constructor without changing any argument. Capture FULL insert bytes immediately as already specified by the parent design. Attach optional `old_full_observer = (capture_callable, rid, P, E)`. The callable owns only the existing collector/bank; do not retain Req or InsertParams. P/E derive from the accepted window, not from returned Q.
2. Explicitly forward this tuple in `RustUnifiedTreeCore.begin_insert` (`adapter.py:809-824`) into a new default-None `InsertParamsBinding` field (`python_bindings.rs:541-593`). A Python transient attribute alone is insufficient. An adapter without the new native field cannot arm capture; it must not silently omit the context and report equality.
3. The binding converts a present tuple to one owned, Send+Sync callback closure. The native `InsertParams` (`unified_tree_core.rs:179-207`) and `InsertWalkState` (`:286-312`) carry an optional shared callback reference. Start clones that reference once; barrier suspension preserves it; finish/end drops it. Native component-local reconstructed params do not initiate another observation. There is no global current-context slot, new backend, feature registry, cache flag, lock, or action.
4. Immediately after the existing prefix-length calculation (`:1984`), invoke that callback with `(node.id, cursor, prefix_len, node.try_device_value(FULL))`. Pass the original borrowed full Tensor, not `state.value` and not a native narrow/copy/cat. Skip callback wrapping/GPU work when its matched interval does not intersect `[P,E)`. A missing FULL value is an observed unsupported OLD interval, never a reason to capture the fresh restoration.
5. Binding reacquires Python attachment inline on that same OS thread, wraps `original.shallow_clone()` through existing `tensor_to_py`, and calls `capture_callable(rid, P, E, node_id, cursor, prefix_len, original_indices)`. Shallow clone is only an owning reference to the original storage, not a new index producer. The callback does not call any tree method or acquire the tree Mutex. It returns no cache decision.
6. Callback validation/capture failures mark the bank invalid and are returned as diagnostic errors at drain; they must not change native key/value/actions or manufacture coverage. Preserve native panic/error handling. The exact non-throwing bridge/error-reporting implementation and Send/Sync/borrow correctness must pass CPU compilation/tests before any arm. Do not add a retry, synchronization, or serving fallback to make an observer failure disappear.

The existing Mutex remains held for the native call. Reacquiring Python attachment is not a new tree lock, but it can block if another Python thread holds the GIL while waiting for this core Mutex. **CPU qualification must check the actual call topology for such concurrent core access.** The inspected scheduler path is single-threaded and synchronous; no blanket safety claim is made for other serving modes. A deadlock or unexpected concurrent-access requirement is a blocker, not permission to add a lock or release the native Mutex.

## Absolute ranges, original storage, and readiness

Native `cursor = state.total_prefix_length` starts at0 (`:1850`) and advances by each matched `prefix_len` (`:2128-2143`). Commit sets returned Q from that cursor (`:2193`). For a callback fragment:

- Matched absolute interval is `[cursor, cursor+prefix_len)`.
- `lo=max(P,cursor)`; `hi=min(E,cursor+prefix_len)`.
- Index source is the original Tensor view `[lo-cursor:hi-cursor]`; output rows are `[lo-P:hi-P]`.
- Copy those exact indices into the OLD int64 receipt and gather each FULL layer's physical K and V into preallocated OLD rows on S. Use the same source slice for both operations. Retain its owning Python/native references through enqueue, not whole objects through drain.

The final Q is not known or used to pick a node/bank during capture. Offline qualification requires exact, nonduplicated, live-fragment coverage of `[P,Q)`. At the warm-full sample1695 target: P90112, E98304, measured Q98067 ⇒ **7955 OLD rows**, leaving237 fresh-suffix rows. For the cold counterpart Q=P ⇒ **zero OLD rows in this window**, not a fabricated zero-valued OLD tensor. A split fragment observed before its split counts once; do not revisit its newly copied parent. The native cursor progression is the interval proof; runtime receipts must confirm the actual coverage and rotation status.

Source-level readiness chain, under the selected FULL+MAMBA/page1/no-hicache path:

1. Incoming FULL int64 copy is created in the scheduler callback on S. Native new-node/restoration/split producers are ordinary `tch::Tensor` narrow/copy calls, issued inline by earlier S calls; no selected producer changes to a private stream in this crate. Auxiliary setter rejects FULL (`unified_tree_core.rs:4934-4937`); unselected SWA repoint/load-back paths are not substitutes.
2. Scheduler dispatch waits S on F before invoking the result callback on S (`S/srt/managers/scheduler.py:2023-2025,2032-2038,2122-2135`); next forward's existing F waits on S (`:4696-4697`). Existing checkpoint call is `scheduler_components/batch_result_processor.py:401` → `M/common.py:278/431` → `checkpoint_into_tree`.
3. Inline OLD(S) is queued before current native split and duplicate-release actions. Future physical writes remain behind the existing next-F gate. The already-qualified TokenAllocator free/alloc operations manipulate CPU indices, not KV payload; this document does not reopen that proof.
4. Node-owned Tensor plus shallow bridge reference protects original index storage through gather enqueue. Same-stream allocation/use/release permits the standard caching allocator to order reuse behind queued S work. This reasoning **requires** that the native original index producer used S; an owning reference alone never proves readiness. No `record_stream`, new wait, event, synchronization, or post-free FRESH read is proposed.

Qualification records must compare the scheduler's CPU OS-thread identity/current Torch S scalar before begin/resume with the callback's identity/scalar, and verify metadata-only original Tensor pointer/shape/stride/dtype/device equality across the bridge. CPU tests establish bridge aliasing; only an actual CUDA callback can establish the selected CUDA TLS/stream. No CUDA content read or per-callback file logging is allowed. The Rust source establishes the point and producers; it does not by itself satisfy these runtime witnesses.

## Smallest patch and production build path

The implementation separates native source/build/staging from physical capture. The native module owns the production ABI and compiled-library receipt; the physical collector composes that preparation once and does not implement another Rust builder. Observer behavior/preparation touches **seven files**:

| Proposed file | Bounded change |
| --- | --- |
| `rust/sglang-radix-tree/src/unified_tree_core.rs` | Optional callback in params/walk state; one pre-split invocation; retain across the unchanged driver. |
| `rust/sglang-radix-tree/src/python_bindings.rs` | Optional tuple field, conversion/ownership, inline existing Tensor wrap/Python call. |
| `srt/mem_cache/rust_tree_core/adapter.py` in the diagnostic SGLang overlay | Explicit tuple forwarding in actual begin constructor. |
| `srt/mem_cache/unified_radix_cache.py` in that overlay | Name unchanged constructor; associate direct RID/P/E and the existing FULL insert-byte capture. |
| Repository `tests/manual/agent_opd/sglang_rust_kv_observer.py` (new) | Native source preparation, isolated build through the existing loader, and verified production-library staging. |
| Repository `tests/manual/agent_opd/sglang_kv_coherence.py` (new) | Physical collector/preparer; compose native preparation once and reuse the parent design's two-bank/FRESH/drain mechanisms. |
| Repository `tests/manual/agent_opd/probe_teacher_scoring.py` | Invoke preparer only for the already-proposed isolated numerical diagnostic, after accepted overlay composition and before server spawn. |

With a field on native InsertParams, compilation also requires default-None fixture updates in **five existing Rust files**: `src/tests/unified_tree_core.rs`, `src/tests/components/{base,full,mamba,swa}.rs`. Put actual native observer ordering/alias tests in the first of these, not a fake Python walker. Add focused Python tests `tests/fast/test_sglang_rust_kv_observer.py` and `tests/fast/test_sglang_kv_coherence.py`, plus `tests/manual/agent_opd/probe_rust_kv_observer.py` for production-library CPU qualification. Thus **15 files including verification/fixture edits**, not a seven-file complete implementation. This count covers the observer slice only; the parent design's pool/FRESH/readback plumbing remains separately required. No node/component/allocator/attention kernel file needs a behavior change.

Use the existing loader, not a second builder: `S/srt/rust_extensions/loader.py:68-166` supports explicit workspace/cache/mode and builds `cargo build --release --locked --package ...` (`:397-430`). Production features stay `python-extension`; do not enable inspection or rename to `mem_cache_inspection`. The existing Torch build configuration supplies the same ABI environment.

Perform a **future, explicitly authorized CPU preparation build** in a fresh isolated process with an explicit loader build mode, before native module import; force mode after import is rejected (`loader.py:107-113`). Stage the resulting same-name production extension into a dedicated diagnostic package copy/worker installation, never the shared baseline installation. The serving process then keeps its selected `never` setting: `never` imports bundled first (`:116-121`) and cannot create a build. Merely populating a loader cache would not select the new library while the original bundle remains present. The source's global default is actually `auto` (`S/srt/environ.py:2168`); preserve both that global configuration and the diagnostic/baseline run's existing explicit `never`, rather than changing a formal backend or making a global force-build setting.

The preparer must retain original and diagnostic library paths, source composition, features/build environment, and build/load receipts in its existing isolated archive. Build the same production Rust implementation with observer absent/present, not the Python core. New-source build identity is provable prospectively; the old bundled binary's unstamped origin remains UNVERIFIED. Do not overwrite that distinction with a Python-version-derived claim.

The native module exposes `build_source(root, *, image, archive_dir)` for the isolated CPU stage and `prepare_source(root, *, image, archive_dir, build_receipt)` for verified diagnostic staging. The physical preparer calls the latter once. The diagnostic config supplies the build-receipt path; missing or mismatched inputs fail preparation before writes. These are separate stages of one production implementation, not alternative builders or a fallback to the old bundle.

## Remaining acceptance and choices

1. **CPU production-native qualification (pending):** inspect the build's pinned tch0.24/torch-sys0.24 Python wrap/unpack/shallow-copy implementation and PyO3 detach/attach implementation; compile borrow/Send+Sync/GIL/error handling; compare bundled original, retained-source rebuild, diagnostic-None, and diagnostic-enabled outputs on ordinary match/insert, partial split, missing FULL restoration, end/abort, and MAMBA barrier/resume cases. Existing native getters can obtain a pre-insert reference in the CPU test, outside the callback; callback pointer must equal it before the real split, and original source tensor length must exceed the partial match. Compare action tags/index values, returned prefix/node result topology, and post-insert indices—not exits alone. No inspection module or mocked walker can stand in for these tests.
2. **Complete collector qualification (pending):** preserve two opaque RID banks allocated after native pool backing/capacity selection. A budget remains514.375 MiB; B321.625 MiB. Preserve parent design's candidate selection, immediate CPP FRESH capture, FULL-insert/rebind byte copies, topology, accepted stream joins, and post-loop-only drain. Q cannot select banks, and FRESH cannot be read after duplicate release.
3. **Authorized bounded CUDA diagnostic (not performed):** before interpretation require callback thread/S witness, original-index bridge metadata, coverage/alignment and physical-row checks, and all original16 vectors/6804 values plus16 requests/10 flushes reproduced EXACTLY in each pair. Stream equality does not prove completion by itself; use only native S/F dependencies. Any missing proof invalidates the diagnostic, not serving behavior. Formal04/05 remain HOLD.

There is no unresolved choice about the measurement source: the inline original-node observer is selected for in-scope CPU implementation. Existing-getter-only capture cannot provide the required matched fragments without extra locks/walking; concat/rebind capture answers another question and is excluded. An isolated production rebuild is the smallest complete path (CPU build/test cost, then the separately qualified and approved original bounded GPU run). Native preparation and physical capture implementation are proceeding in parallel with separate file ownership. This acceptance does not attest a successful build, bridge/GIL safety, actual S-stream identity, numerical CUDA adequacy, or formal readiness. No GPU submission is authorized by this document.

## Local verification and scope checkpoint

Local verification is standard-library source inspection only. It checks the actual source contracts, frontier ordering, reachable getter/cat difference, producer copy sites, forwarding omission, native driver/thread/stream API absence, and decisive file/line references. It neither imports Torch nor executes Rust. **PASS:** 19 source contracts; 11 non-test Rust source files contain none of the listed thread/stream APIs; five fixture files need the new field; LF-numbered A126/B120 select TP0 Rust; window arithmetic is7955/237. Environment: local host, Python3.10.6. The scoped `git diff --check` passes.

The first scan failed only at a log-line assertion: Python `splitlines()` treated progress-log carriage returns as line breaks, unlike the cited LF-based grep numbering. Reading bytes and splitting only on LF corrected that offline checker. It did not change a source contract or the runtime. A follow-up source read also corrected the Python driver reference from unrelated lines2109-2125 to the actual lines661-687 before closing this document.

Exact successful scan command, executed from the worktree root:

```bash
python3 - <<'PY'
from pathlib import Path
import platform, re
T = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
R = T/'evidence/native-rust-source-20261111/exp-1111-124522-553024/checkout/rust/sglang-radix-tree'
S = T/'evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source'
c,n,b,f,a = [(R/x).read_text() for x in ['src/unified_tree_core.rs','src/node.rs','src/python_bindings.rs','src/components/full.rs','src/cache_action.rs']]
contracts = [(n,'pub value: Option<Tensor>'),(n,'-> Option<&Tensor>'),(n,'self.key.atom_len(),'),(c,'self.arena.set_device_value(new_node_id, FULL, value.copy());'),(c,'.set_device_value(node_id, FULL, fresh_value.copy());'),(n,'let head = value.narrow(0, 0, split_len).copy();'),(n,'let tail = value.narrow(0, split_len, len - split_len).copy();'),(f,'Node::redistribute_child_device_value(new_parent, child, FULL, split_len)'),(b,'.map(|value| value.map(|tensor| tensor.shallow_clone()))'),(b,'Tensor::pyobject_unpack(ptr)'),(b,'.pyobject_wrap()'),(b,'.detach(move || self.core().try_begin_insert(&params))'),(b,'.detach(|| self.core().try_resume_insert())'),(b,'core: Mutex<Core>'),(a,'impl_cache_action!(FreeDeviceKV, "free_device_kv", insert_barrier = false)'),(c,'component_type != BASE_COMPONENT_TYPE,\n            "set_component_device_value: auxiliary components only"')]
for text,token in contracts: assert token in text, token
w = c[c.index('    fn insert_walk_step_('):c.index('    pub(crate) fn insert_overlap_step_(')]
assert w.index('let prefix_len = state.key.match_len(cursor, &node.key, self.page_size);') < w.index('self.split_node_(node_id, prefix_len)')
assert 'Tensor::cat(&prefix_chunks, 0)' in c[c.index('    pub fn collect_full_device_indices('):c.index('    pub fn touch_node_(')]
assert 'old_full_observer' not in b and 'old_full_observer' not in (S/'srt/mem_cache/rust_tree_core/adapter.py').read_text()
runtime = [p for p in (R/'src').rglob('*.rs') if 'tests' not in p.relative_to(R/'src').parts]
pattern = re.compile(r'\brayon\b|thread::spawn|spawn_blocking|CUDAStreamGuard|CUDAEvent|record_stream|get_stream_from_pool|set_current_stream')
hits = [(str(p.relative_to(R)),i+1) for p in runtime for i,line in enumerate(p.read_text().split('\n')) if pattern.search(line)]
assert not hits, hits
fixtures = sorted(str(p.relative_to(R)) for p in (R/'src/tests').rglob('*.rs') if re.search(r'InsertParams \{', p.read_text()))
assert fixtures == ['src/tests/components/base.rs','src/tests/components/full.rs','src/tests/components/mamba.rs','src/tests/components/swa.rs','src/tests/unified_tree_core.rs'], fixtures
for pair,line in [('A',126),('B',120)]:
 path = T/f'evidence/teacher-scoring-kv-stream-witness-probe-20261111/native/{pair}/admission-{pair}-r1/server.log'
 row = path.read_bytes().split(b'\n')[line-1]
 assert b'TP0' in row and b'RustUnifiedTreeCore' in row, (pair,line,row)
assert (T/'design_rust_kv_observer.md').read_text().startswith('## Modification History\n')
assert 98067-90112 == 7955 and 98304-98067 == 237
print('PASS:', len(contracts)+3, 'source contracts;',len(runtime),'non-test Rust source files without listed thread/stream APIs;',len(fixtures),'fixture files; A126/B120 backend lines; 7955/237 rows')
print('Environment: local host; Python',platform.python_version(),'; standard-library only; no Torch/native/CUDA execution')
PY
git diff --check -- task_memory/task_2026-11-08_qwen35_full_kl_nll/design_rust_kv_observer.md
```

Scope checkpoint: source inspection and the design advance only this follow-up's Rust observer frontier. No tooling extension, retry loop, parallel-worker delay (delegation explicitly prohibited), generalized observer, or backend/measurement substitution is retained. The prior missing-crate condition is superseded by R's retained source, but the historical bundle stamp and native observer/runtime qualification remain incomplete. Shared design/requirements/report updates belong to the primary, not this file owner.
