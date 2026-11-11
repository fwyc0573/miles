## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record primary acceptance of both bounded measurement prerequisites after independent decisive scheduler-source reads and already-archived A/B controls; numerical interpretation remains pending. |
| 2026-11-11 | Close original producer/lifetime/F→S readiness from version-bound retained source, actual run options/receipts and accepted same-library R3 CPU qualification; retain intentionally excluded raw replay/paired descriptors as nonclaims rather than blockers. |
| 2026-11-11 | Independently qualify both completed r3 physical/index/coverage receipts and relevant frozen collector source; preserve unverified raw-index/producer/dependency limits and pending numerical interpretation. |

# r3 A/B physical-index qualification

TaskID: `profile-kv-coherence-r3-physical-index-qualification-20261111`.

**Current result: PRIMARY ACCEPTED for the scoped compact physical checks and original producer/lifetime/F→S readiness in both A and B. Readiness is source-backed and consumes accepted same-library R3 CPU qualification, not newly measured event/syscall/descriptor instrumentation. Both A/B all16/6804 controls are already primary-accepted and archived at `4da5c3eb`; no unmet original measurement prerequisite remains in this responding-TP0 scope. Numerical interpretation remains PENDING.** The primary additionally read the retained scheduler at2023–2038,2122–2127,3936–3944,4696–4697, base backend at195–233, and actual installed hybrid backend at1325–1328. The original follow-up's A-baseline-pending snapshot is preserved as history in JSON. No K/V metric values were examined or interpreted. No root-cause, fix, performance, race-exclusion or formal acceptance follows.

The primary supplied A `exp-1111-194637-456465` Succeeded at `11:56:55Z`, B `exp-1111-194636-897299` Succeeded at `11:54:54Z`, source `f8b6b43a` and R3 build-receipt prefix `91458e`. The follow-up supplies owner-bound Completed0/restart0, accepted source/serving `0dc763cc` library and callback S/thread controls, plus accepted R3 original-Tensor alias/inline/barrier lifetime qualification for the **same** library. These controls are consumed, not rerun. Platform terminal states were not independently queried here.

Snapshot history: the initial report passed compact physical/source/FRESH gates but left producer/dependency readiness unverified before tracing the selected scheduler path. Raw-index/hash replay and paired GPU Rust descriptors were also labeled unverified. The primary explicitly confirmed that D40 intentionally excludes those extra measurements: their absence stays recorded as a **nonclaim**, not a new blocker. The original readiness gap is now closed below; nothing was reconstructed or invented.

## Evidence locations and environment

Let `T=task_memory/task_2026-11-08_qwen35_full_kl_nll`, `N=T/evidence/teacher-scoring-kv-coherence-probe-20261111/native`, and `A/B=N/{A,B}/admission-{A,B}-r3`. Line references are LF-based. Metadata sequence numbers below identify receipts, not request selection or adjacency pairing rules.

- Local workspace: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`; Python `3.10.6`; kernel `Linux 5.10.25-nvidia-gpu`; initial local Git HEAD `b4fd2039fa6b3586e4cf744ef4ff9663131bcc8a`.
- Retained native runtime environment, not executed locally: Python `3.12.16`, Torch `2.14.1+cu130`, SGLang `0.5.24.dev80+g056f871`, executable `/opt/sglang/bin/python3`.
- Read the root `AGENTS.md`, all ten `.agents/rules/**/*.md`, `T/requirements.md` and `T/plan.md` relevant current/physical sections, and both measurement designs. `design_kv_coherence_measurement.md:47-58,70-86,139-155` and `design_rust_kv_observer.md:67-85,113-115` define this scope. Historical readiness labels in the designs do not override the latest explicit r3 assignment.
- Definitive receipt reads: A `result.json:1432-2041,2074-2230`; B `result.json:1432-1819,1852-2008`; both `requests.jsonl:5,11` and their `completion_scores/{cold,warm_stream}-r0-s2-full_input.json` identity fields only; both `runtime_metadata.json` physical projections and `server.log` exact invalidation-marker scan.
- Raw readback corroboration: A `runtime_metadata.json:2766649-2767449`; B `:1753315-1753893`. Both marker receipts are `runtime_metadata.json:16-21`. The raw `server_info.internal_states[0].kv_coherence`, normalized `runtime_metadata.kv_coherence[0]`, and `result.kv_coherence.summaries[0]` physical projections are equal. These are copies of one readback, not three independent measurements.

Machine-readable evidence: [physical-index-verification-r3.json](evidence/teacher-scoring-kv-coherence-probe-20261111/physical-index-verification-r3.json).

## Observed selection, fragments and topology

Banks were joined by `bank.rid == requests.native_request_id == requests.meta_info.id == completion_scores.native_request_id`, then by actual logical fields. Neither registration order nor Q selected phase identity. Both candidates have UID `00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6:5:127`, sample1695/position2/repetition0, `full_input`, input98942, logprob start0 and retractions0.

| Pair / phase from RID join | Actual RID | P / E / Q | OLD / suffix rows | Independent begin / returned / rebind metadata sequences |
| --- | --- | --- | --- | --- |
| A cold | `2743596029b34b6a93ede6fe881e55a4` | 90112 / 98304 / 90112 | 0 / 8192 | 11801 / 11802 / 11803 |
| A warm_stream | `d1f39efbb85546309cb149c82d6341e3` | 90112 / 98304 / 98067 | 7955 / 237 | 25875 / 25878 / 25879 |
| B cold | `011d6bcddb7140a38a4667cbcb0fbf30` | 90112 / 98304 / 90112 | 0 / 8192 | 7547 / 7548 / 7549 |
| B warm_stream | `ab9c724339da47169960dcd488c647cd` | 90112 / 98304 / 98067 | 7955 / 237 | 16557 / 16560 / 16561 |

Each target begin is unique by actual RID/page-aligned end; returned/rebind join uniquely by RID/node/prefix/rotation signature. Rotation is false. For each warm target, original node124 covers `[90112,96631)` with cursor90112/prefix6519/original tensor length6519. Original node125 covers `[96631,98067)` with cursor96631/prefix1436/**original length1673**, before the partial split. These are 6519+1436=7955 contiguous, nonoverlapping rows; the remaining `[98067,98304)` is237 rows. Cold fragments are empty, not a zero-filled OLD observation. Exact fragment descriptors and pointers are retained in the JSON artifact.

| Pair | Responding PID | FULL global layers / dense mapping | Every K/V backing descriptor | Two-bank payload / indices / total |
| --- | --- | --- | --- | --- |
| A | 333 | 3,7,…,63 / 0…15 | BF16 CUDA0 `[1833689,1,256]`, stride `[256,256,1]` | 536870912 / 2490368 / 539361280 bytes =514.375 MiB total |
| B | 350 | 3,7,…,39 / 0…9 | BF16 CUDA0 `[2752781,1,256]`, stride `[256,256,1]` | 335544320 / 1703936 / 337248256 bytes =321.625 MiB total |

Both use the live `TokenToKVPoolAllocator`, page1, `HybridLinearKVPool` root and its distinct `MHATokenToKVPool` writer child. Every target terminal's K/V backing pointers, writer object and dense layer match topology. There are exactly16 CPP/terminal joins per A bank and10 per B bank for actual `(RID,prefix90112,extend8192)`. Joins use the entire RID/lens/Kptr/Vptr/locptr key, not adjacent sequence numbers. All target CPP launch receipts are nonempty and CPP stream equals their Torch F scalar: A642383120, B531885904. This does not assert device completion.

## Prerequisite results and what the fields prove

`PASS` below means the agreed compact receipt, inspected version-bound source and explicitly consumed primary qualification establish this scoped condition. It is not raw-index replay or acceptance of A's overall baseline gate.

| Prerequisite | A / B | Decisive evidence and exact limit |
| --- | --- | --- |
| Actual two-bank RID/meta/completion selection | PASS / PASS | Request lines5/11 and completion identity fields agree; dynamic Q did not label banks. |
| Independently joined P/E/Q, no declined rotation | PASS / PASS | Unique begin end and returned/rebind RID/node/prefix signature; same 90112/98304/98067 warm geometry. |
| Original OLD once-only coverage | PASS / PASS | Two original fragments cover7955 rows; collector loops every FULL layer using the same original index slice. No per-layer OLD mask is serialized. |
| Original Rust pre-split source seam | PASS / PASS | Frozen generator inserts the borrowed-node callback before the retained core's split branch; the partial-match descriptor retains1673 rows rather than1436. This does not independently prove native-to-Python pointer aliasing. |
| Complete required FULL descriptors and two banks | PASS / PASS | Complete A16/B10 mapping, both K/V descriptors for every layer, correct two-bank budgets and target pointer joins. |
| CPP/writer independent same-call identity | PASS / PASS | Unique full key joins for both candidates/all FULL layers. CPP has metadata/pointers, **not a separately frozen index-content vector**. |
| Writer = FULL insert; original OLD = rebind; suffix = insert | PASS / PASS | All four physical booleans are true for all four banks. `_physical` compares independent device receipt copies with exact `torch.equal`; writer equality is aggregated over all layers. Cold OLD equality is the explicit vacuous `n==0` branch. |
| FRESH complete and frozen before duplicate release | PASS / PASS, source/capture-gate level | FRESH copies all8192 rows immediately after the class-owned CPP store; no later/rebind payload gather. Successful `captured` drain requires every dense fresh layer once, no bank/capture errors and no pending CPP key. Final serialization drops `fresh_layers`, so this is source-backed gate evidence, not retained per-layer completion events. |
| Index dtype/device/length and bounds | PASS / PASS | Capture validates device-local int64 vectors; exact bounds result true. Bounds are **backing-row** bounds `0 <= index < K.shape[0]`, including reserved zero, not allocator ownership/uniqueness proof. |
| Capture errors / native invalidation marker | PASS / PASS | Global errors empty, binding error null; raw marker receipt and independent LF scan of each local server log have zero `old_full_observer_invalidation_failed` matches. Not a blanket no-native-error assertion. |
| Matching callback OS thread/Torch S scalar | PASS / PASS | Insert and both warm fragments match: A thread333/S647954864; B thread350/S532178656. Scalar equality does not prove native producer readiness or device completion. |
| Post-loop completed-RID drain identity | PASS / PASS | Completed-RID set equals actual16 request RIDs; frozen consumer requests marked drain only after successful scored identities. No baseline vector values checked. |
| Raw-index/hash replay or separate CPP byte comparison | NOT CLAIMED / NOT CLAIMED | No raw writer/insert/OLD/rebind vectors or index-content hashes are serialized. These intentionally excluded measurements are not readiness blockers. Do not invent indices or hashes from pointers/flags. |
| Original owning Tensor alias and inline/barrier lifetime | PASS / PASS, consumed same-binary CPU qualification | Primary-accepted R3 `91458e` qualifies alias/inline/barrier lifetime for serving `0dc763cc`. Missing paired GPU descriptors do not reset that acceptance. |
| Original producer readiness / GPU lifetime / F→S dependency | PASS / PASS, source-backed | Actual selected options, version-bound scheduler/producer/event chain and measured callback S/thread establish the original criterion. Detailed proof below; no per-kernel event measurement is claimed. |

There is no observed failing physical boolean, coverage mismatch or surviving original readiness gap. Intentionally unmeasured stronger fields remain nonclaims, not added gates and not numerical equality. Scope remains responding TP0, not other TP ranks or other checkpoints.

## Frozen source inspection

Local files were first compared byte-for-byte with `git show f8b6b43a:<path>` before reading their relevant source. SHA256: collector generator `6be5ef8642f33512fb463f30040247750b472716289eba0c139cb65e5d005721`; consumer `19bf42be9802a9160dad9c80d4a7a2465c9af0c0c4fabf305283ce073bd812df`; native observer generator `acf89c7425ba38a0a497adfd27cf2fe71979f77922d7af5f6b66a6685175442d`. Both frozen installed `srt/kv_coherence.py` files equal the generator's actual marker-extracted output, SHA256 `7ed5b5fb56ef736afee2c9e9aefa7543a779e53f18b3cf3cf7c0943618816308`.

Decisive reads, with paths relative to the worktree unless prefixed A/T:

- `tests/manual/agent_opd/sglang_kv_coherence.py:24-31,450-529`: actual runtime text extraction and bounded hook injection. The runtime is **not** an assumed `_RUNTIME_SOURCE` AST constant.
- `A/kv_coherence_source_preflight/after/srt/kv_coherence.py:62-113,122-178,211-286,294-309,346-395`: finalized topology/preallocation; actual Req selection; CPP key and immediate FRESH; exact FULL insert bytes and transient RID/P/E native context; original index-slice copies and gathers; independent rebind bytes; exact physical comparisons; coverage/FRESH/error drain gates; post-drain payload/index release. Numeric computation source exists, but no measured K/V metric values were consulted.
- `A/kv_coherence_source_preflight/after/srt/mem_cache/memory_pool.py:2995-3017`: unchanged store then immediate FRESH hook.
- `A/kv_coherence_source_preflight/after/srt/mem_cache/unified_radix_cache.py:1185-1187,1237-1252,1307-1329`: actual request mapping/int64 copy, FULL insert field capture before native insert, then actual canonical rebind bytes. Metadata `insert_value` at1250 is **Mamba**, not FULL indices.
- Both `kv_coherence_source_preflight/coherence.diff`; A decisive hook ranges12-17,77-84,133-137,168-180,186-191. Both `native_observer/adapter.patch:3-8` explicitly forward the observer tuple.
- `tests/manual/agent_opd/sglang_rust_kv_observer.py:58-99,163-186`: invocation-owned callback, borrowed original `node.try_device_value(FULL)` immediately after match length, shallow Tensor wrapping, same inline callback, and diagnostic invalidation marker.
- `T/evidence/native-rust-source-20261111/exp-1111-124522-553024/checkout/rust/sglang-radix-tree/src/unified_tree_core.rs:1965-1986`; sibling `src/node.rs:602-622`: retained original match frontier before split; split subsequently deep-copies both index halves. The callback does not receive incoming `state.value`, concat or a new split clone.
- `tests/manual/agent_opd/probe_teacher_scoring.py:542-595,628-679`: independent native-marker scan; after-all drain; actual request/meta/completion joins and fragment/index checks. `logical_case` is derived offline from RID. The consumer keeps interpretation unverified.
- Initial snapshot: both `native_observer/preflight.json` and R3 `observer-build.json` reference fields were read to identify retained source; their older CUDA-pending labels were not acceptance. Follow-up explicitly consumes the primary's accepted same-binary CPU alias/lifetime and GPU callback S/thread receipts; no CPU semantic/build/module checks were rerun.

## Follow-up: original producer/lifetime/F→S readiness

**PASS, source-backed for both runs. No real unmet original readiness criterion remains; no additional zero-GPU collection, instrumentation, build, CPU/native or GPU run is needed.** The successful source-backed all-layer FRESH gate remains legitimate even though the compact bank deliberately does not serialize `fresh_layers`.

Let `S=T/evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source`, `R=T/evidence/native-rust-kv-observer-build-20261111/sources/observer`, and `C=T/evidence/native-rust-kv-observer-qualification-20261111-r3`.

### Version binding and actual selected route

- `S/../source.json` retains the complete installed5501 source manifest, version `0.5.24.dev80+g056f871`, from the same configured company image named by these run receipts. `runtime.sglang` in both results is that version. This is existing retained private source, not public-source substitution or new container-image attestation.
- `S/srt/managers/scheduler.py` is **283721 bytes**, SHA256 `54bbde812b4af9e01a00b62e12e95015fdb1c325b9e153706616ba59ea52b2a6`, matching both actual `runtime.sglang_sources` receipts. `srt/managers/scheduler_components/batch_result_processor.py` is72581 bytes, SHA256 `bbc670ed5b31781c43b911e5c85f2f51c2229f02e358ba14254d8169a3a755a2`, also matching both actual receipts. Eager runner SHA256 `6ac59ed3d5758e52298054b822852e877a17c75de47c3e83709a00b92967d591` matches both r3 preflight hashes. Selected hybrid SHA256 `fa1331457e307f5d172fd62730be0dd026a36a10a10319b7ec630e1d097c3d36` and token allocator hash match the same preflight.
- Transitive files `srt/managers/utils.py`, `srt/mem_cache/{allocation,common}.py`, `srt/model_executor/runner_utils/shared_read_event.py`, `srt/layers/attention/{base_attn_backend,attention_registry,flashattention_backend}.py`, `srt/model_executor/model_runner_components/attention_backend_setup.py`, and `kernels/ops/memory/common.py` were inspected and their retained bytes checked against that original manifest. Exact hashes are in JSON `dependency_qualification.source_hashes`. These transitive hashes are **version-bound retained source**, not newly measured GPU-process per-file hashes. The already-provided source controls and unchanged package composition are consumed rather than reset.
- `C/observer-build.json` hash is exactly `91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7`. Its accepted CPU qualification covers original/rebuilt/observer-none/observer-enabled, partial split, missing FULL, end/abort and Mamba barrier cases. Its observer hash equals actual A/B serving `0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba`. The three inspected R3 source files match that receipt's after-manifest: core `152aa1e579f246d5b1beca04f4a80970e470a42eb94a8ed1e378fa0e1719fb0d`, binding `1e4f7d60918e2d6f8cc110d59f2b1564c31801a73547027b22597ad3b9ecb0fe`, node `826ef0bed6c15a53e67fff3b7dd0797dc945de73fb97d2af6df3588507ce111f`. CPU alias/inline/barrier lifetime is explicitly accepted by the primary; no new CPU execution occurred here.

Both actual `runtime_metadata.json` objects resolve `disable_overlap_schedule=false` (ordinary CPU/GPU scheduler overlap), `enable_two_batch_overlap=false`, `enable_single_batch_overlap=false`, `disable_cuda_graph=true`, `attention_backend=fa3`, null speculative algorithm, `enable_mixed_chunk=false`, disaggregation `null`, PDmux off, PP1/CP1 and page1. Unified memory, memory saver, hierarchy/external linker, KV sharding and HiSparse are off. For both files decisive server-option lines are71/80/82/85/109,220,331,361,456/468/470,502/503,523/542,585; the responding-state copies include741/750/752/755/779,889,1000,1030,1125/1137/1139,1171/1172,1192/1211,1254.

`model_runner.py:1136-1141` builds the resolved backend; `attention_backend_setup.py:136-141,203-204` selects the ordinary backend, not TBO/PDmux. `attention_registry.py:238-251,426-428,460,566-574` constructs FA3 `FlashAttentionBackend` and the hybrid linear wrapper with actual FULL layers. FA3 inherits `AttentionBackend` and has no `shared_read_ends` or `_snapshot_prefill_shared_reads` override. Base `base_attn_backend.py:195-200,213-233` returns `UNKNOWN` for EXTEND; r3 hybrid `hybrid_linear_attn_backend.py:1325-1328` takes the latest child end. Thus the selected hybrid EXTEND remains `UNKNOWN` regardless of the other child. `SharedReadEnds.UNKNOWN` is the latest value (`base_attn_backend.py:24-35`). `shared_read_event.py:25-30` publishes **only** PRE_REPLAY: there is no early pre-replay event for these selected forwards. This is the decisive reason the native scheduler uses its whole-forward fence, not an inference from absent log text or F≠S.

### Exact producer/dependency chain

1. **Allocation and request indices are produced on S.** The loop is inside `StreamContext(schedule_stream)` (`S/srt/managers/scheduler.py:2023-2025`). `r3 schedule_batch.py:2854-2868,2921-2923` prepares the ordinary EXTEND. `S/srt/mem_cache/allocation.py:374-432,451-464` selects page1 token allocation and writes the actual request mapping; its `write_cache_indices:56-105` either launches the mapping writer on the current stream or uses same-stream pool writes. `kernels/ops/memory/common.py:8-56` copies actual prefix/out-cache indices, not KV payload. `allocator/token.py:42-75` owns index tensors/views and frees by index concatenation; `allocator/base.py:213-233,284-293` clones/groups/sorts/releases indices, without moving or overwriting K/V backing.
2. **F waits S, then freezes FRESH before F completion.** Existing `scheduler.py:4696-4697` selects F and makes it wait for S before forward/input copies. `eager_runner.py:180-208,280-284,349-366` loads inputs and executes the model within the scoped batch context. Actual target CPP receipts identify F=A642383120/B531885904. The class-owned store then immediately calls FRESH (`r3 memory_pool.py:2995-3017`). `r3 kv_coherence.py:168-178` validates the same CPP/F witness, independently copies writer indices and gathers full8192-row K/V before marking that layer present. These ordinary same-stream gathers precede the native forward-completion boundary; no payload gather is deferred until insert/free/rebind.
3. **F→S whole-forward readiness precedes the selected checkpoint.** In `scheduler.py:2122-2127`, immediately after `run_batch`, `_apply_war_barrier` is enqueued on S. Because selected EXTEND has no PRE_REPLAY event, `:2032-2038` executes **`schedule_stream.wait_stream(forward_stream)`**. This fence covers the forward including immediate FRESH gathers. The target is a chunk checkpoint: the next `get_next_batch_to_run` calls `stash_chunked_request` at `:3936-3944`, then `:3797-3801` → `common.py:271-278` → r3 cache `checkpoint:1166-1169` → `checkpoint_into_tree`. **It is incorrect to require that this selected chunk insert first pass through the result callback's host synchronize.** Its S GPU work is ordered by the already-enqueued whole-forward fence.
4. **Actual FULL index copy and original native producers stay on S.** r3 `unified_radix_cache.py:1185-1187,1237-1252` reads the request mapping, creates the int64 copy, assigns actual `InsertParams.value` and captures its bytes before native insert. `:668-686` synchronously drives begin/actions/resume. Accepted R3 `python_bindings.rs:1229-1240` detaches/reattaches inline on that caller thread; it does not spawn an insert worker or switch CUDA stream. Native new-node FULL copy (`R/src/unified_tree_core.rs:2466`), restoration copy (`:2497`) and split copies (`R/src/node.rs:612-622`) are therefore current-thread S producers on this selected route. Owning a tensor alone is not the proof: the producing ordinary ATen index copies and OLD consumer share S, and the prior F payload writes are fenced. Current restoration cannot substitute for OLD; the callback precedes it and missing original FULL invalidates the bank.
5. **Same original owning Tensor before split/free; future overwrite cannot overtake OLD.** R3 core `:1971-1995` borrows `node.try_device_value(FULL)` immediately before split. Binding `:149-180` uses `shallow_clone` + `pyobject_wrap`: an owning reference, not a new index producer or split clone. Accepted R3 CPU evidence establishes that alias/inline/barrier lifetime for the same serving library. Actual insert/callback OS thread and S match in each GPU run. Python original/view references remain owned through independent OLD index-copy/all-layer gather enqueue (`r3 kv_coherence.py:237-267`). Native duplicate actions occur later (`core overlap/free source`, r3 cache `:1434-1437`), only returning indices to the allocator. CPU release may precede OLD GPU completion, but does not overwrite physical K/V. Any subsequent physical writer on F waits existing S at `scheduler.py:4696-4697`, so the queued S OLD reads finish before reuse can overwrite those slots. Original index allocation/use/release is same-stream ordinary allocator ordering. No additional wait/event/record_stream or paired GPU descriptor is required.
6. **Existing result-copy event/host synchronization and later forwards support drain.** Separately, `scheduler.py:4756-4769,5043-5067` creates `copy_done`, gates copy stream on F and issues native result D2H; `managers/utils.py:170-234` records `copy_done` after the copies. `batch_result_processor.py:268-270` synchronizes it before result processing/checkpoint/release (`:394-401`). The optional existing CC worker preserves this dependency (`async_d2h_copy_worker.py:68-99`); no CC branch selection is needed for the earlier stash proof. Each selected RID actually has a later prefix98304/extend638 forward: A cold CPP11816/all16 FULL, warm25892/all16; B cold7562/all10, warm16574/all10. That later F waits the selected S work, and native result completion precedes successful scoring completion. Combined with all16 actual completed RIDs, post-loop drain follows selected OLD work without new synchronization.

The resulting selected chain is:

```text
S allocation/request mapping -> F.wait(S)
F store -> immediate all-layer FRESH(F) -> native whole-forward boundary
S.wait(F) -> next-loop chunk stash -> FULL int64 copy(S)
original native FULL producers/owning observer(S) -> OLD gathers(S)
native split/duplicate index release(S) -> next F.wait(S)
actual later same-RID F chunk -> copy-stream/F dependency -> copy_done host sync
completed scoring responses -> existing all16-only compact drain
```

### Successful captured drain and all-layer FRESH

Yes: `captured` plus the inspected unchanged source gate legitimately establishes complete all-layer FRESH. Preallocation creates one output per required dense layer. FRESH rejects duplicate layers, mismatched RID/window/child/CPP streams and unsupported terminals, and adds its layer only after both gathers and writer-index copy enqueue. Drain refuses missing insert/rebind/coverage, any capture errors or pending CPP key, and **requires exactly the full dense-layer set** (`r3 kv_coherence.py:154-178,366-376`). Consequently A16/B10 completeness follows from a successful captured drain under the version-bound source. The final compact bank drops `fresh_layers` at serialization (`:378-387`); no new field is necessary. This is a source-backed enqueue/completion-dependency argument, **not** a claim that compact metadata includes a per-layer completion timestamp or raw payload archive.

### Actually measured bounds versus source-backed bounds

- Actually recorded: resolved options and relevant direct source hashes; serving library identity; target CPP F scalars; insert/callback S scalars and OS threads; all compact physical/coverage results; actual later same-RID chunks; completed-RID set. F and S are distinctly A642383120/647954864 and B531885904/532178656, an expected fact, neither failure nor proof by itself.
- Consumed primary-accepted evidence: same-library R3 CPU original Tensor alias/inline/barrier lifetime; run source/serving/callback controls; B baseline acceptance; A verifier's exact result with primary reading.
- Source-backed conclusion: current-thread S index producers, original ownership through enqueue, whole-forward F→S fence, next-writer S→F fence and result-copy/host completion chain meet the original readiness criterion.
- Not claimed: newly measured event timestamps, paired GPU Rust syscalls/descriptors, independent raw-index/hash replay, all-TP qualification, universal race absence or numeric/model causality. These do not become new acceptance gates.

## Initial local verification commands and results

The environment/identity command was `pwd; python3 --version; uname -sr; git rev-parse HEAD`. Rule discovery used `glob("**/*.md", ".agents/rules")` and `for f in .agents/rules/**/*.md; do printf '\n--- %s ---\n' "$f"; cat "$f"; done`. File discovery was confined to the two admission directories and their preflight archives. Dedicated reads and symbol searches covered the exact paths/ranges above. Intermediate standard-library probes enumerated JSON keys and projected only physical/bank/fragment/identity/dependency fields; they did not print measured K/V metrics. No persistent script or new harness was added.

All shell inspections used a60000ms timeout. The decisive audit below ran from the workspace root using standard-library Python only. Expected: both pair audits pass all assertions; exact RID joins and7955/237 geometry; A16/B10 target joins; correct budgets; all index booleans true; marker count0. Actual: **PASS A and PASS B**. Final bank `fresh_layers` and raw `indices` presence both false, as explicitly recorded rather than silently assumed present.

One earlier local checker exited1 with `StopIteration` at stdin line8 while looking for a nonexistent `_RUNTIME_SOURCE` assignment. Source inspection showed `_runtime_source()` extracts text between existing markers. The corrected audit below reconstructs that exact output without importing or executing the runtime. This was an offline checker error, not a serving/collector failure; no native/CPU replay was launched.

```bash
python3 - <<'PY'
import hashlib, json, platform, subprocess
from pathlib import Path
T = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
G = 'tests/manual/agent_opd/sglang_kv_coherence.py'
text = subprocess.check_output(['git','show','f8b6b43a:'+G]).decode()
assert Path(G).read_text() == text
runtime = ('"""CUDA-only opt-in FULL KV observer; no cache decisions or new waits."""\n'
           'import hashlib\nimport math\nimport os\nimport threading\nfrom pathlib import Path\n\n'
           + text.split('# BEGIN INSTALLED RUNTIME\n',1)[1].split('# END INSTALLED RUNTIME',1)[0])
print('ENV',platform.python_version(),'stdlib-only; no runtime/native imports')
for pair,L in [('A',16),('B',10)]:
 p=T/f'evidence/teacher-scoring-kv-coherence-probe-20261111/native/{pair}/admission-{pair}-r3'
 assert (p/'kv_coherence_source_preflight/after/srt/kv_coherence.py').read_text()==runtime
 r=json.loads((p/'result.json').read_text());m=json.loads((p/'runtime_metadata.json').read_text());s=r['kv_coherence']['summaries'][0]
 project=lambda c:{k:c[k] for k in ('schema','process_id','status','topology','errors','native_binding','binding_error','completed_rids','coverage')} | {'banks':[{k:b[k] for k in ('rid','insert','rebind','fragments','physical','status','logical_case')} for b in c['banks']]}
 assert project(s)==project(m['server_info']['internal_states'][0]['kv_coherence'])==project(m['kv_coherence'][0])
 assert s['status']=='captured' and s['errors']==[] and s['binding_error'] is None
 req=[(i,json.loads(line)) for i,line in enumerate((p/'requests.jsonl').read_text().split('\n'),1) if line]
 candidates=[(i,a) for i,a in req if a['mode']=='full_input' and a['input_count']==98942 and a['logprob_start_len']==0]
 assert len(candidates)==2 and {a['phase'] for _,a in candidates}=={'cold','warm_stream'}
 assert len(s['completed_rids'])==16 and set(s['completed_rids'])=={a['native_request_id'] for _,a in req}
 t=s['topology'];layers=list(range(3,4*L,4));assert t['mapping']==[[layer,dense] for dense,layer in enumerate(layers)] and [b['layer_id'] for b in t['buffers']]==layers
 assert len(s['banks'])==2 and t['budget']=={'payload_bytes':4*8192*L*1024,'index_bytes':2*(L+3)*8192*8,'allocated_bytes':4*8192*L*1024+2*(L+3)*8192*8}
 for b in t['buffers']:
  for name in ('K','V'):
   d=b[name];assert d['dtype']=='torch.bfloat16' and d['device']=='cuda:0' and d['shape']==[t['capacity']+1,1,256] and d['stride']==[256,256,1] and d['data_ptr']>0
 stages={'kv_store_stream','kv_store_terminal','checkpoint_insert_begin','checkpoint_insert_returned','canonical_kv_rebind_enqueued'}
 rows=[(seq,stage,dict(fields)) for seq,stage,fields in m['server_info']['internal_states'][0]['mamba_runtime_metadata']['rows'] if stage in stages]
 result=[]
 for bank in s['banks']:
  rid=bank['rid'];i,a=next((i,a) for i,a in candidates if a['native_request_id']==rid)
  comp=json.loads(Path(a['completion_scores']).read_text());assert rid==a['meta_info']['id']==comp['native_request_id'] and a['meta_info']['num_retractions']==0
  assert (a['sample_index'],a['sample_position'],a['repetition'])==(1695,2,0)
  assert {k:a[k] for k in ('pair','phase','mode','source_uid','sample_index','repetition')}==bank['logical_case']
  ins,reb=bank['insert'],bank['rebind'];n=7955 if a['phase']=='warm_stream' else 0
  assert all(x['rid']==rid and x['P']==90112 and x['E']==98304 for x in (ins,reb)) and reb['Q']==90112+n and reb['rotation_tail_declined'] is False
  assert bank['physical']['old_rows']==n and all(bank['physical'][k] is True for k in ('writer_equals_FULL_insert_all_layers','original_OLD_equals_rebind','rebind_suffix_equals_insert','indices_in_bounds'))
  cursor=90112
  for f in sorted(bank['fragments'],key=lambda x:x['lo']):
   assert f['rid']==rid and (f['P'],f['E'])==(90112,98304) and f['lo']==cursor and f['hi']>cursor
   assert (f['lo'],f['hi'])==(max(90112,f['cursor']),min(98304,f['cursor']+f['prefix_len']))
   assert (f['thread_id'],f['torch_current_raw_stream'])==(ins['thread_id'],ins['torch_current_raw_stream'])
   d=f['original_FULL'];assert d['dtype']=='torch.int64' and d['stride']==[1] and d['device']=='cuda:0' and d['shape'][0]>=f['prefix_len'];cursor=f['hi']
  assert cursor==reb['Q']
  selected=lambda x:x[2].get('rids')==[rid] and x[2].get('prefix_lens')==[90112] and x[2].get('extend_lens')==[8192]
  cpp=[x for x in rows if x[1]=='kv_store_stream' and selected(x)];term=[x for x in rows if x[1]=='kv_store_terminal' and selected(x)]
  key=lambda d:(tuple(d['rids']),tuple(d['prefix_lens']),tuple(d['extend_lens']),d['k_cache_data_ptr'],d['v_cache_data_ptr'],d['writer_loc_data_ptr'])
  assert len(cpp)==len(term)==L;joins=[]
  for dense,layer in enumerate(layers):
   matches=[x for x in term if x[2]['layer_id']==layer];assert len(matches)==1
   tseq,_,d=matches[0];cm=[x for x in cpp if key(x[2])==key(d)];assert len(cm)==1;cseq,_,c=cm[0]
   assert d['pool_object_id']==t['writer_object_id'] and d['buffer_layer_idx']==dense
   assert all(d[f'{name.lower()}_cache_data_ptr']==t['buffers'][dense][name]['data_ptr'] for name in ('K','V'))
   assert c['launch_enqueued'] is True and c['native_stream_scalar_observed'] is True and c['store_kind']=='cpp_store_cache'
   assert c['native_actual_stream']==c['torch_current_raw_stream'] and c['native_actual_stream']!=-1 and c['writer_loc'][1:]==['torch.int64',[8192],[1],'cuda:0']
   assert (c['row_bytes'],c['v_row_bytes'])==(512,512);joins.append([layer,cseq,tseq])
  beg=[x for x in rows if x[1]=='checkpoint_insert_begin' and x[2].get('rid')==rid and x[2].get('page_aligned_len')==98304]
  rb=[x for x in rows if x[1]=='canonical_kv_rebind_enqueued' and x[2].get('rid')==rid and x[2].get('page_aligned_len')==98304]
  assert len(beg)==len(rb)==1;d=rb[0][2];assert (d['absolute_start'],d['absolute_end'],d['prefix_len'],d['node_id'])==(90112,98304,reb['Q'],reb['node_id'])
  ret=[x for x in rows if x[1]=='checkpoint_insert_returned' and x[2].get('rid')==rid and (x[2].get('node_id'),x[2].get('prefix_len'),x[2].get('rotation_tail_declined'))==(d['node_id'],d['prefix_len'],False)];assert len(ret)==1
  result.append({'phase':a['phase'],'rid':rid,'requests_line':i,'Q':reb['Q'],'old_rows':n,'suffix_rows':98304-reb['Q'],'fragments':[[f['node_id'],f['cursor'],f['prefix_len'],f['lo'],f['hi'],f['original_FULL']['shape'][0]] for f in bank['fragments']],'thread_id':ins['thread_id'],'S_callback_scalar':ins['torch_current_raw_stream'],'CPP_F_scalars':sorted({x[2]['native_actual_stream'] for x in cpp}),'layer_CPP_terminal_seq_joins':joins,'checkpoint_begin_returned_rebind_seq':[beg[0][0],ret[0][0],rb[0][0]]})
 marker=m['native_observer_errors']['marker'];lines=(p/'server.log').read_bytes().split(b'\n');hits=[i for i,line in enumerate(lines,1) if marker.encode() in line]
 assert hits==[] and m['native_observer_errors']['matches']==[]
 print('PAIR_PASS',pair,json.dumps({'process_id':s['process_id'],'layers':layers,'budget':t['budget'],'banks':result,'native_marker_lines':hits,'fresh_layers_retained':any('fresh_layers' in b for b in s['banks']),'raw_indices_retained':any('indices' in b for b in s['banks'])},sort_keys=True))
PY
```

## Follow-up local verification commands and result

Exact additional reads are the source paths/ranges in the follow-up sections and JSON `dependency_qualification.decisive_source_lines`, both run option projections, original5501 selected manifest records, R3 receipt/source-manifest fields and the selected RIDs' later CPP metadata. All commands ran from the same workspace using Python3.10.6 standard library with60000ms timeout; no Torch/SGLang/native imports or execution occurred.

One offline checker initially exited1 with `KeyError: 'sglang_version'` at stdin line26. Schema inspection showed the actual field is `runtime.sglang`; the corrected command below passed. One atomic Markdown patch failed verification because its hunks were in reverse row order; no edits from that attempt applied. Reading the actual table and applying ordered hunks resolved it. Neither error was a native/serving failure; neither caused new instrumentation or runtime reruns.

Expected: accepted R3 same-library receipt/source binding, both resolved ordinary page1 EXTEND routes, original borrowed owning seam, existing whole-forward F→S and result event/host chain, all-layer FRESH gate and actual later prefix98304/extend638 chunks all pass. Actual: **PASS_DEPENDENCY A and PASS_DEPENDENCY B**; later FULL CPP counts are16/16 and10/10, with the exact sequence/RID records already listed. No measured K/V value was accessed.

```bash
python3 - <<'PY'
import hashlib,json,platform
from pathlib import Path
T=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll');S=T/'evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source'
M=json.loads((S.parent/'source.json').read_text());C=T/'evidence/native-rust-kv-observer-qualification-20261111-r3';B=json.loads((C/'observer-build.json').read_text());R=Path(B['observer']['workspace'])
assert hashlib.sha256((C/'observer-build.json').read_bytes()).hexdigest()=='91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7'
assert B['status']==B['qualification']['status']=='PASS' and B['observer']['sha256']=='0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba'
for rel in ('src/unified_tree_core.rs','src/python_bindings.rs','src/node.rs'):
 assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==B['source_manifest']['after'][rel]['sha256']
sc=(S/'srt/managers/scheduler.py').read_text();base=(S/'srt/layers/attention/base_attn_backend.py').read_text();flash=(S/'srt/layers/attention/flashattention_backend.py').read_text()
assert 'class FlashAttentionBackend(AttentionBackend)' in flash and 'def shared_read_ends(' not in flash and 'def _snapshot_prefill_shared_reads(' not in flash
assert 'return SharedReadEnds.UNKNOWN' in base and 'if shared_read_ends is not SharedReadEnds.PRE_REPLAY:' in (S/'srt/model_executor/runner_utils/shared_read_event.py').read_text()
assert 'self.schedule_stream.wait_stream(self.forward_stream)' in sc and 'self.forward_stream.wait_stream(self.schedule_stream)' in sc
assert sc.index('self._apply_war_barrier()',sc.index('def event_loop_overlap')) < sc.index('self.result_queue.append((batch.copy(), batch_result))')
assert 'self.stash_chunked_request(self.chunked_req)' in sc and 'self.copy_stream.wait_stream(self.forward_stream)' in sc
assert 'result.copy_done.synchronize()' in (S/'srt/managers/scheduler_components/batch_result_processor.py').read_text() and 'self.copy_done.record()' in (S/'srt/managers/utils.py').read_text()
core=(R/'src/unified_tree_core.rs').read_text();walk=core[core.index('    fn insert_walk_step_('):core.index('    pub(crate) fn insert_overlap_step_(')]
assert walk.index('observer(node.id, cursor, prefix_len, node.try_device_value(FULL));') < walk.index('self.split_node_(node_id, prefix_len)')
bridge=(R/'src/python_bindings.rs').read_text();assert 'Some(tensor) => tensor_to_py(py, tensor.shallow_clone())' in bridge and '.detach(move || self.core().try_begin_insert(&params))' in bridge
for pair in 'AB':
 p=T/f'evidence/teacher-scoring-kv-coherence-probe-20261111/native/{pair}/admission-{pair}-r3';r=json.loads((p/'result.json').read_text());state=json.loads((p/'runtime_metadata.json').read_text())['server_info']['internal_states'][0]
 options={'disable_overlap_schedule':False,'enable_two_batch_overlap':False,'enable_single_batch_overlap':False,'disable_cuda_graph':True,'enable_unified_memory':False,'enable_hierarchical_cache':False,'enable_memory_saver':False,'enable_hisparse':False,'enable_pdmux':False,'disaggregation_mode':'null','attention_backend':'fa3','page_size':1,'speculative_algorithm':None,'enable_mixed_chunk':False,'enable_kv_cache_sharding':False,'enable_unified_cache_external_linker':False,'pp_size':1,'attn_cp_size':1}
 assert all(state[k]==v for k,v in options.items()) and r['runtime']['sglang']==M['sglang_version']
 for rel in ('srt/managers/scheduler.py','srt/managers/scheduler_components/batch_result_processor.py'):
  assert hashlib.sha256((S/rel).read_bytes()).hexdigest()==r['runtime']['sglang_sources'][rel]['sha256']
 assert hashlib.sha256((S/'srt/model_executor/runner/eager_runner.py').read_bytes()).hexdigest()==r['kv_coherence_source_preflight']['observed_after_sha256']['srt/model_executor/runner/eager_runner.py']
 capture=state['kv_coherence'];assert capture['status']=='captured' and capture['errors']==[] and capture['native_binding']['module_sha256']==B['observer']['sha256']
 installed=(p/'kv_coherence_source_preflight/after/srt/kv_coherence.py').read_text();assert 'bank["fresh_layers"] != set(range(len(self.layers)))' in installed
 assert installed.index('bank["indices"]["writer"][dense].copy_(selected)') < installed.index('bank["fresh_layers"].add(dense)')
 hybrid=(p/'kv_coherence_source_preflight/after/srt/layers/attention/hybrid_linear_attn_backend.py').read_text();assert 'SharedReadEnds.max_of(' in hybrid and 'def _snapshot_prefill_shared_reads(' not in hybrid
 suffix=[]
 for bank in capture['banks']:
  rid=bank['rid'];matches=[]
  for seq,stage,fields in state['mamba_runtime_metadata']['rows']:
   if stage!='kv_store_stream':continue
   d=dict(fields)
   if d.get('rids')==[rid] and d.get('prefix_lens')==[98304]:matches.append((seq,d['extend_lens']))
  assert matches and all(lens==[638] for _,lens in matches)
  suffix.append({'rid':rid,'later_F_prefix':98304,'later_extend':638,'first_CPP_seq':matches[0][0],'later_FULL_CPP_count':len(matches)})
 print('PASS_DEPENDENCY',pair,'version-bound coarse F->S/copy-event+host-sync/original S producers+owning bridge/FRESH gate/later F:',suffix)
print('ENV',platform.python_version(),'stdlib only; no native/module execution or measured K/V metric access')
PY
```

## Follow-up scope checkpoint

### 1. Spec Check

The latest explicit compact-only decision and dependency-only follow-up are sound. Initial nonclaims remain recorded, not new raw/hash/paired-descriptor gates. The source-backed argument is sufficient for the original readiness criterion, with A's overall acceptance and numerical interpretation left to the primary. Requirements were re-read before closure; its current line3 still describes the earlier submitted snapshot. That shared-record reconciliation belongs to the primary and does not supersede the newer explicit actual-run evidence supplied here.

### 2. Progress Recap

| Subtask | Status | Recorded verification |
| --- | --- | --- |
| Retained selected producer/event source and run-option qualification | completed | Both actual hash-bound scheduler/result processors, eager/hybrid preflight, original5501 transitive source and resolved options inspected. |
| Original allocation/index producer and F→S lifetime proof | completed | PASS source-backed; whole-forward stash fence, inline S producers/owning bridge, later F reuse fence and native completion chain. |
| All-layer FRESH gate without new fields | completed | PASS unchanged source gate plus actual captured drain; final omitted fields retained as nonclaims. |
| Owned artifacts and snapshot/limit reconciliation | completed | Only the two owned artifacts updated; final JSON/source-hash/status checks recorded below. |
| A overall primary baseline acceptance / numerical interpretation | pending, separately owned | No metric values inspected; A verifier result is supplied but primary acceptance was not declared at this follow-up. |

### 3. Drift Check

S1/S2/S3/S4/S6/S7/S8 CLEAR: no source edits, extra harness, remote/native operations, allocation, new gate or rootfix. S5 corrected in owned artifacts: old readiness labels are explicitly historical; raw/paired-descriptor omissions are nonclaims; current original readiness is PASS source-backed. Shared-doc snapshot mismatch is identified for its owner without editing the eight shared documents or extending this task. The two offline checker/editing errors were schema/order mistakes resolved by local inspection, not repeated serving fixes.

### 4. Course Correction

Preserve the narrowed original criteria; stop after the owned evidence update and validation. No physical-readiness next action, instrumentation or new run is needed. Primary independently completes A overall acceptance and decides any later numeric interpretation. No delegated or dependent work was launched here.

## Initial scope checkpoint (historical)

### 1. 规划完成情况

**汇总：** PASS 4｜BLOCKED/FAILED/SKIPPED 0｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| A/B identity、physical、coverage receipts | PASS | 两份实际 r3 receipts 的独立 joins 与 compact physical checks 已核对。 |
| Frozen collector/native seam source | PASS | f8b6b43a、实际 runtime generator/consumer 与 pre-split seam 已读取。 |
| 资格结论及缺证边界 | PASS | raw indices/hash、producer readiness 和其他 primary gates 均未冒充完成。 |
| 两份自有 artifacts 的最终一致性检查 | PASS | JSON physical fields 与两份实际 summaries 一致；source identities、无 metric values、LF/trailing-whitespace 与 scoped diff check 均 PASS。 |

### 2. 偏离检测

**结论：** 未偏移，正常推进。**检测窗口：** 本次只读任务开始至最终 artifacts 检查｜**当前前沿：** 回传并停止。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅标准库本地 JSON/source 检查，无持久 harness。 |
| D2 细节反复重试 | CLEAR | 一次错误的 runtime-source 假设由实际 factory 源码修正；无 native 重跑。 |
| D3 支线问题修补 | CLEAR | 没有 source/config/test 修补。 |
| D4 可并行任务停滞 | CLEAR | 明确禁止此 subagent 再委派；其他 controls 由独立 owners 负责。 |
| D5 超范围镀金 | CLEAR | 只写指定两份 artifacts。 |
| D6 分析空转 | CLEAR | 调查直接交付 physical 资格与缺证清单。 |
| D7 路线违背 | CLEAR | 没读/解释 K/V metric values，也未提前接受 controls。 |

**文档检查：** S1/S2/S3/S4/S6 在本次窄范围未见缺陷。S5：shared requirements/plan 的开头仍写 SUBMITTED，晚于此处的用户明确 terminal receipts 已完成；这是既有共享记录 owner 的更新事项，不改变本次资格标准。**归因：** 无执行偏离。

### 3. 纠正建议

**分支：** B：共享执行快照需要 routine 更新；本次不越权写入。

**文档更新（先执行）：**
1. 由 primary 更新 `requirements.md:3`、`plan.md:3,159` 的 terminal/verification 当前事实（可直接执行，但不属于本 subagent file ownership）；不得因此把未接受 controls 或 numeric 标为 PASS。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 本 subagent：回传已验证的两份 owned artifacts；完成标志已满足，随后停止。
2. Primary 并行处理既有 A/B controls 与 binding/S 资格；只有所有原定 gates 接受后才进入 numeric interpretation。

### 4. 最值得关注的 3 点

1. A/B 都实际覆盖7955 OLD rows/237 suffix，cold OLD 不存在。
2. Compact physical flags 和完整 layer/source gates 成立；raw indices、index hashes、producer readiness 不能凭空补足。
3. 未接受的 baseline/source/binding/S gates 和 numeric interpretation 仍由 primary 保持 PENDING。

## Final owned-artifact verification

Expected: both owned artifacts preserve initial missing-field/history records, keep raw/paired descriptor measurements as nonclaims, retain numeric PENDING, and match all14 Python source hashes plus3 accepted-native source hashes. Actual: **PASS_ARTIFACTS 14 Python source hashes;3 accepted-native source hashes;A/B original readiness PASS_SOURCE_BACKED;absent fields/history preserved;numeric PENDING**. Exact command, run with the same60000ms timeout and environment:

```bash
python3 - <<'PY'
import hashlib,json
from pathlib import Path
T=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll');P=T/'evidence/teacher-scoring-kv-coherence-probe-20261111/physical-index-verification-r3.json';D=T/'test_report_2026-11-11_kv_coherence_r3_physical_indices.md'
a=json.loads(P.read_text());q=a['dependency_qualification'];S=Path(q['source_archive']);M={e['path']:e for e in json.loads(Path(q['source_archive_manifest']).read_text())['files']}
assert a['scoped_compact_receipt_and_source_checks']=='PASS' and a['original_producer_lifetime_F_to_S_readiness']==q['status']=='PASS_SOURCE_BACKED'
assert a['numeric_interpretation']==q['numeric_interpretation']=='PENDING' and q['real_unmet_original_readiness_criteria']==[] and q['new_instrumentation_or_replay_required'] is False
for k in ('independent_local_replay_of_raw_indices_or_index_hashes','separately_frozen_CPP_index_bytes','independent_Rust_side_to_Python_pointer_alias_runtime_receipt'):assert a['checks'][k]=='NOT_CLAIMED'
for pair in 'AB':
 p=Path(a['pairs'][pair]['native_path']);r=json.loads((p/'result.json').read_text())
 for e in q['source_hashes']:
  f=p/'kv_coherence_source_preflight/after'/e['path'];f=f if f.is_file() else S/e['path'];assert hashlib.sha256(f.read_bytes()).hexdigest()==e['sha256']
  if e['basis']=='both actual run runtime.sglang_sources':assert r['runtime']['sglang_sources'][e['path']]['sha256']==e['sha256']
  elif 'observed_after_sha256' in e['basis']:assert r['kv_coherence_source_preflight']['observed_after_sha256'][e['path']]==e['sha256']
  else:assert M[e['path']]['sha256']==e['sha256']
for rel,h in q['native_observer_source_hashes'].items():assert hashlib.sha256((Path(q['native_observer_source_root'])/rel).read_bytes()).hexdigest()==h
text=D.read_text();assert 'No unmet original readiness criterion remains' in text and '## Initial scope checkpoint (historical)' in text and '## Follow-up scope checkpoint' in text
assert len(q['later_same_RID_F_receipts']['A'])==len(q['later_same_RID_F_receipts']['B'])==2 and len(a['receipt_fields_not_retained'])==6
print('PASS_ARTIFACTS',len(q['source_hashes']),'Python source hashes;',len(q['native_observer_source_hashes']),'accepted-native source hashes; A/B original readiness PASS_SOURCE_BACKED; absent fields/history preserved; numeric PENDING')
print('ARTIFACTS',str(D),str(P))
PY
```

## Authorization and completion boundary

Final local check: a standard-library stdin checker compared every retained bank's physical/P/E/Q/phase/fragment/thread field against its actual r3 summary, checked the three source hashes against `git show f8b6b43a`, and checked both owned files for final LF/trailing whitespace and absent metric-value keys. Actual output: `PASS: artifact physical fields equal both actual r3 summaries; frozen source identities match; metric values absent; LF/trailing-whitespace checks pass.` The exact scoped Git commands were:

```bash
git diff --check -- task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_r3_physical_indices.md task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/physical-index-verification-r3.json
git status --short -- task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_r3_physical_indices.md task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/physical-index-verification-r3.json
```

The scoped diff command passed; both files are untracked as required by the no-stage/no-commit instruction, so the explicit Python whitespace/content check supplies their validation rather than relying on tracked diffs.

Only this report and its linked JSON were written. No eight shared documents, native A/B reports, source/config/test files, GPU/API/StepMind/native module/authentication/SSH/cloud actions, staging, commits or delegation were performed. This qualification does not request a rerun, raw-KV archive, generalized harness or new acceptance criterion. Original physical/producer/lifetime readiness is complete with no further action needed here. Primary independently finishes A overall acceptance and decides whether to begin later numeric interpretation; this report does neither.
