## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record primary design-only acceptance, keep implementation/native proof pending, and align planned validation and worker entry with existing project mechanisms. |
| 2026-11-11 | Design an actual-value layer-0 witness and post-all16 scratch replay for the approved D40 warm blocker; no implementation or execution. |

# Actual recurrent-state value witness

TaskID: `profile-recurrent-state-value-witness-design-20261111`.

Status: **DESIGN ONLY; root cause UNRESOLVED.** Source handoff is primary accepted at `7ae55df2`: H1 is structurally confirmed, not numerically or causally confirmed. `e2ab706a` remains an accepted scoped numeric audit, not an equality PASS. The `281e` ordering, source, stream, alias/lifetime and original experiment qualification stays CLOSED. Ordinary necessary D40 preparation is already authorized; this document adds no blanket approval gate.

**PRIMARY ACCEPTED as a preparation design only.** Existing `Collector.register(req)` already receives full-input request identity; recurrent candidates must use their own four-record selection without changing its existing two-bank FULL selector. Predicted memory sizes and source seams are accepted planning inputs, not measured peaks or capture/replay evidence. Canonical-P publication joins, replay fidelity and actual allocation/traffic remain unverified. The production-specialization packed operator preparation proceeds independently; no equal-length-only substitute run is required before this witness.

## 1. Question and fixed experiment

Measure the actual layer-0 active **temporal and conv** state before mutation, the actual conv input/output, and the actual `q,k,v,g,beta` and GDN output when a request continues from prefix `P=90112`. Determine whether the original paired trajectories first differ in these measured initial values, in inputs, or in outputs despite equal measured inputs. Reproduce each captured call on private scratch only after all16 finish. Never replace serving inputs, active state, donors, matching, rebinding, slots, locks or scheduling.

Keep the original first four requests, all16 unsalted requests and ten flushes unchanged. Capture four request candidates per teacher: cold and warm occurrences of source `1693`, and cold and warm occurrences of source `1695`. Do not call the first registered candidate cold or warm. Select provisionally by the actual RID registered for full-input teacher scoring and its observed prompt length (`97365` or `98942`), then by the actual layer-0 forward-context RID and CPU prefix/extend fields. Label occurrences only after the existing all16 original-index/source-identity/cache-event join. A surprising candidate count or missing join makes this witness incomplete; it does not invalidate or repeat the accepted experiment qualification.

The two native continuation lengths are `7253` and `8192`. Their source inputs first differ at absolute token `96631`, so only `96631 - 90112 = 6519` continuation rows are common. Compare that common interval, not all `7253` rows. Keep each request's entire actual continuation for exact same-call replay.

The selected snapshot at `97344` is after `7232` new tokens of **1693**. It includes a divergent suffix and is not a state for 1695 at its target prefix. Historical node `122/P90112` is the same-key canonical snapshot reference; `125/E98304` is not the target prefix state; leaf `127` already represents the target's own donor. Use these as historical meanings, not fixed node IDs for a future run.

## 2. Inspected evidence and reachable source seams

All paths below are relative to the repository. Abbreviations identify actual retained native files, not a proposed subset runtime:

- `T = task_memory/task_2026-11-08_qwen35_full_kl_nll`.
- `R = T/evidence/teacher-scoring-kv-coherence-probe-20261111/native/A/admission-A-r3`.
- `K = R/kv_coherence_source_preflight/after`.
- `F = R/source_preflight/after`.
- `S = T/evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source`.

Inspected task `requirements.md`, `plan.md`, current ticket `05-b-full.md`, root instructions/rules and `GLOSSARY.md`; no `docs/adr` directory was found. The retained RCA is `T/test_report_2026-11-11_kv_coherence_trajectory_source_rca.md` with `T/evidence/kv-coherence-trajectory-rca-20261111/source-rca.json`. Its H1 trace shows active state allocated/cleared, continued without a later warm-request COW, and preserved across canonical FULL rebind. Replacement donors serve rotating tracking slots, not the active state. This explains structural reachability, not the contents of those states. Historical RCA status/next-action wording is superseded where the delegated request explicitly closes qualification and authorizes ordinary preparation.

| Seam | Exact retained source | Observation and proposed use |
| --- | --- | --- |
| Actual request identity | `tests/manual/agent_opd/sglang_kv_streams.py:52-63,93-104`; `S/srt/model_executor/forward_context.py` | Reuse the already installed `get_forward_context().forward_batch`, including `rids`, CPU prefix lengths and extend lengths. No registration-order or list-position attribution. |
| State ownership and pre-mutation point | `K/srt/layers/attention/linear/gdn_backend.py:1031-1054` | Native code obtains `conv_states, ssm_states` and the indexed active slot before conv tracking assignment or conv/GDN update. Insert a read-only begin observation here. Select the active row with the existing GPU `cache_indices`; no `.item()` or serving-time CPU readback. |
| Actual conv call | same file `:932-953,1075-1089` | CUDA prefill calls `_convolve_prefill`, which invokes `causal_conv1d_fn(mixed_qkv.transpose(0,1), ..., conv_states=..., has_initial_state=..., cache_indices=..., query_start_loc=..., seq_lens_cpu=..., **conv_kwargs)`. Capture the pre-conv input at begin and the returned post-conv `mixed_qkv` after line 1089. Do not substitute a layout or another conv implementation. |
| Actual recurrence inputs | same file `:1091-1115,1177-1234`; `S/kernels/ops/attention/triton_gdn_fused_proj.py:683-736` | CUDA fused split creates native contiguous `q,k,v`; `g,beta` come from `_prefill_gates`. Capture before `self.kernel_dispatcher.extend` at line 1209. Preserve descriptors, cu-seqlens, flags and lengths. Do not call these values the internally normalized q/k. |
| Actual output and final active state | `K/srt/layers/attention/linear/gdn_backend.py:1234-1255` | Capture `core_attn_out` and indexed final active conv/temporal immediately after line 1234, before later tracking use. `needs_state_gather=False` is the observed supported path here; the initial observation is before line 1054. The native call has already mutated temporal state; a late initial-state capture would be wrong. |
| P90112 donor at publication | `K/srt/mem_cache/unified_radix_cache.py:1237-1258,1307-1329`; `K/srt/mem_cache/unified_cache/components/mamba.py:643-746,785-791` | Extend the existing `insert` observation to copy the actual incoming donor's layer-0 conv and temporal values only for page-aligned `90112`, before insertion/cleanup can free or recycle it. Extend the existing `rebind` observation with its returned node and `mamba_exist`; no new native cache hook. Translate the donor through the existing pool interface. |
| Replay kernel entry and behavior | `F/srt/layers/attention/linear/kernels/gdn_triton.py:173-226`; `F/kernels/ops/attention/fla/chunk.py:15-143,144-286` | Reuse the actual dispatcher and actual chunk implementation on private scratch, retaining `use_qk_l2norm_in_kernel=True`, scale, dtype, indexed state, cu-seqlens and update mode. The wrapper returns `o, None, h`; do not reinterpret its documentation as returning a dense FP32 final-state reference. |
| Existing collector lifecycle | `tests/manual/agent_opd/sglang_kv_coherence.py:108-191,331-373,416-472,515-531,579-597` | Extend the existing collector, installed-package edits and `get_server_info` drain. Keep its current FULL candidate selectors/receipts unchanged. Add a separate four-request recurrent record set inside that collector. |
| Existing staging and after-all16 joins | `tests/manual/agent_opd/probe_teacher_scoring.py:556-595,628-687,708-728,775-783,811-825` | Reuse whole-private-package staging and the existing post-all16 server-info readback/join. Add compact recurrent results to that response/result; do not add a request, flush or interim drain. |

The existing hybrid KV root does not own recurrent state: `K/srt/mem_cache/memory_pool.py:4444-4448` identifies `req_to_token_pool.mamba_pool` as its owner. Pass that existing request-pool reference at the collector's existing initialization seam; do not search FULL buffers for recurrent state or add a new pool abstraction.

The incoming P donor is a **writer-time value witness**. If its insert creates the canonical P node, the returned result identifies that publication. If the insert reports `mamba_exist=True`, the incoming donor is not proof of the already-existing canonical slot's current contents. Keep the producer/publication join explicit; do not silently label every incoming donor canonical. If no retained publication can be joined to the canonical P node, canonical-value comparison is unavailable, while paired active-state/input comparisons still stand.

## 3. Small interface and capture lifetime

Extend `Collector`, not a new plugin, generic capture framework, command, retention flag or archive service. Three read-only native-forward observations are sufficient:

1. `recurrent_begin(backend, layer, forward_batch, cache_indices, conv_states, ssm_states, mixed_qkv)` captures indexed initial conv/temporal and pre-conv input, retaining the existing native dispatcher for replay.
2. `recurrent_inputs(layer, forward_batch, mixed_qkv, q, k, v, g, beta, query_start_loc)` captures post-conv output and recurrence inputs.
3. `recurrent_end(layer, forward_batch, cache_indices, conv_states, ssm_states, core_attn_out)` captures recurrence output and indexed final conv/temporal.

The existing `register`, `insert`, `rebind`, `initialize` and `drain` own candidate metadata, P-donor observation, node joins, state-pool lifetime and final comparison. The small observation calls return no native replacement tensors. Eligibility is layer `0`, actual forward RID, prefix `90112`, full-input scoring identity and the observed native continuation length. Read all CPU descriptors already available in this scope; never recover RID from registration order.

Each request record owns pinned-host destinations for initial/final state, P-publication state, conv input/output, `q,k,v,g,beta`, and GDN output. Retain descriptors of the **native** tensors separately from these dense storage copies: shape, dtype, stride, device, slot-index dtype, cu-seqlens, activation, bias presence, normalization flag and scale. The actual conv weights/bias and dispatcher are read-only references to existing native objects, retained through drain; do not archive weights. Copy the small cu-seqlens/track-index values into host-owned storage in the same capture enqueue; do not retain mutable `backend.forward_metadata` as a historical call record. For these observed single-sequence calls the conv block table is source-backed `None`: `K/srt/layers/attention/linear/gdn_backend.py:599-623` declines the table for a one-length rectangular grid. Record that actual call option and replay the same conv function with the saved arguments, not the backend's later forward metadata.

Before every in-place update, enqueue capture copies on the already-current native forward stream. Use a small private GPU indexed-state staging row and a reusable dense conv-input staging slab, followed by `pinned_destination.copy_(staging_or_native_tensor, non_blocking=True)`. Reuse the same forward-stream staging only in that stream's normal enqueue order. P-donor observations run on the already-current scheduler stream and use a separate state staging row. No cross-stream reuse of that row. Neither staging buffer is passed to serving kernels as live state or input.

Capture both initial components at the begin seam, even though temporal mutation occurs later than conv mutation. A CUDA tensor reference alone is not a snapshot. Pinned host destinations are owned until drain and never returned to a pool or read by the CPU during serving. Native temporary tensors used as copy sources remain governed by their existing same-stream allocator lifetime; the reusable private staging removes the need to retain or share a native projection view.

Do not add events, waits, device synchronizations, cache locks, Rust/C++ rebuilds or new stream/index/ABI qualification. The accepted stream chain already places `S.wait(F)` before publication/stash and future `F.wait(S)` before subsequent forward work. All new serving capture copies are part of those existing streams. At the sole existing post-all16 drain, run the already-qualified FULL collector readback first; its existing blocking `.cpu()` readback on S, following the accepted S/F chain, is also the completion boundary before reading pinned capture memory. If that existing completion/readback path fails, do not read potentially unfinished host captures or add a substitute wait: return an incomplete recurrent receipt. This is local evidence availability, not a reopened experiment gate.

After all16, pinned-host captures may be copied into private GPU replay tensors on S, using the existing drain's readback synchronization. Preserve the native input layout with `empty_strided` where it matters, particularly the strided pre-conv projection view. Use only the captured initial active state or a correctly joined same-prefix writer state in private scratch. All replay outputs return to ephemeral host buffers for compact comparisons. Release host captures and scratch after producing receipts. No persistent raw KV, state or input archive, no raw-value prerequisite and no worker-local-file fallback if pinned allocation fails.

## 4. Candidate and memory budget

Dimensions come from `T/evidence/native-sglang-source-20261111/exp-1111-030539-334581/source.json:100-175`, `S/srt/models/qwen3_5.py:570-653`, and `S/srt/configs/mamba_utils.py:215-273`. A has 48 linear layers, B 30, but capture exactly layer 0 on responding TP0, not all layers. TP is 4. Both have `Hq=Hk=4`, `K=V=128`, conv kernel width 4 and conv window 3. A has `Hv=12`, B `Hv=8`; hence packed conv widths `C=2560/2048`, value widths `Dv=1536/1024`.

Retained temporal descriptors confirm FP32 `[701,12,128,128]` for A and `[1575,8,128,128]` for B (`R/runtime_metadata.json:1705-1723` and corresponding `native/B/admission-B-r3/runtime_metadata.json:1705-1723`). Capture one indexed row, not either whole pool. CUDA conv allocation follows `[slot,C,3]`; BF16 is the configured/default conv dtype (`S/srt/configs/mamba_utils.py:48-107`, `K/srt/mem_cache/memory_pool.py:664-667,731-763`). Native BF16 projections and FP32 `g,beta` follow the inspected fused gating/split allocation. **Conv dtype and activation strides have not been numerically measured by this task.** Record their actual descriptors at capture and calculate bytes from those descriptors, rather than silently relying on these predictions.

For one candidate of length T, dense captured activation bytes are:

`conv_in + conv_out + qkv + g + beta + gdn_out = T * (6*C + 8*Hv + 2*Dv)`.

An indexed conv+temporal state pair is `S = 2*C*3 + 4*Hv*128*128` bytes. Keep three pairs per candidate: initial, final and P writer donor. No selected-97344 state/input capture is required for this H1/H3 design; that operator question remains in the parallel work.

| Item | A / 27B | B / 35B-A3B |
| --- | ---: | ---: |
| Temporal row / conv row | 786,432 / 15,360 B | 524,288 / 12,288 B |
| One state pair S | 801,792 B | 536,576 B |
| Captured activations per token | 18,528 B | 14,400 B |
| Candidates / total actual continuation rows | 4 / 30,890 | 4 / 30,890 |
| Actual-used host activation + 12 state pairs | 581,951,424 B = 554.992 MiB | 451,254,912 B = 430.350 MiB |
| Preallocated pinned host, four native max-length 8192 banks | 616,747,008 B = 588.176 MiB | 478,298,112 B = 456.141 MiB |
| Serving private GPU staging: one 8192*C BF16 slab + two state pairs | 41.529 MiB | 33.023 MiB |

The exact preallocated dense value-payload budgets are `4*(8192*18528 + 3*801792) = 616747008` and `4*(8192*14400 + 3*536576) = 478298112` bytes, respectively. Small cu-seqlens/index buffers and Python receipt metadata are additional, not included in the payload formula. Actual-used rows are `2*7253 + 2*8192 = 30890`; do not size 16 full-input banks or multiply by all linear layers.

Post-all16 replay is serial, and original FULL numeric-drain buffers can be released by their existing lifecycle before replay. Native FLA scratch at `T=8192`, from `F/kernels/ops/attention/fla/chunk.py:15-100`, includes q/k normalization (16 MiB), FP32 cumsum g (0.375/0.250 MiB), BF16 w/u/v_new (24/16 MiB each), BF16 A (12/8 MiB), chunk h (48/32 MiB), and output (24/16 MiB): approximately **172.375 A / 120.250 B MiB**, excluding allocator caching and Triton implementation workspace. GDN input/state scratch adds about 41.5/33 MiB. Conv replay is a separate phase: its original strided qkvz view has row stride `C+Dv` (`S/kernels/ops/attention/triton_gdn_fused_proj.py:344-359`), predicting 64/48 MiB input backing, plus 40/32 MiB output and one state pair. Do not densify that native input for the control replay.

A practical predicted replay live-tensor envelope is **under 256 MiB A / 192 MiB B**, with serial conv and GDN phases and no retained per-candidate GPU replay bank. This is a descriptor-derived planning envelope, not a measured peak or a new memory-tuning constant. Pinned replay output needs at most one dense conv-output-sized buffer (40/32 MiB) and one state pair, giving approximately **628.940 A / 488.652 B MiB** total pinned host allocation including the four capture banks. Compare one token row or one state head at a time rather than materializing full FP64 copies. Native CUDA allocator reserved memory, Triton first-use workspace and existing server allocations are extra. Record actual peak allocated/reserved before and after capture/drain, without changing memory fraction, allocation policy or resource configuration. The roughly 555/430 MiB of native-value D2H traffic is real serving-stream overhead even without new waits; neither its latency nor its timing perturbation is measured here, and no performance acceptance follows. A memory failure marks this witness unverified; it does not trigger a larger run or cache bypass.

## 5. Post-all16 comparison and private replay

The server drain returns opaque-RID comparisons and replays; it does not know cold/warm from registration. The probe joins those four records to the original source identities **after all16 and before causal labeling**. Preserve RID, original index, source UID, source length, observed prefix/extend, P publication node, actual cache-event provenance and coverage (`responding scheduler process, TP0 only`). Missing fields are explicit, not guessed. No source-identity payload or new RPC is needed.

Produce compact tensor comparison receipts for (a) cold/warm same source, (b) 1693/1695 within each observed cache trajectory, and (c) active P state versus a successfully joined canonical-P publication witness. For conv and recurrence activations, compare only the common 6519 rows. Report dtype/shape/stride, finite counts, exact unequal element count, first unequal coordinate/absolute token, max absolute difference and RMS difference. Do not introduce a pass tolerance. State equality is a local measured fact; no score or global-state conclusion follows automatically.

Replay plans, all inside drain on independent scratch:

1. **Exact captured-call controls.** Replay each actual conv call using its own actual pre-conv input and initial conv state, preserving native layout, activation, flags and cu-seqlens; compare post-conv output and final conv state. Separately replay the actual recurrence with its own captured `q,k,v,g,beta` and initial FP32 temporal state; compare output and final active state. Do not chain a newly generated conv output into the recurrence control. Preserve the native indexed update path using a private state pool and private indices, never the live pool. Record the actual tracking-buffer presence/index and reproduce its writes into private scratch for the control, without adding snapshot comparison or raw retention to this design.
2. **Actual-value shape comparison.** For each of the two actual 8192-row captures, reuse its own exact-call control and replay its first 7253 rows with the same input values and initial private state. Keep dtype, flags and layout; change only native length/cu-seqlens demanded by truncation. Compare the first 6519 rows, which also occur in the original 1693/1695 pair. This uses captured business values, not a synthetic operator sweep or exploration of 7253/8192/7232 combinations. Report the own-input controls beside it; a failed control makes causal attribution unavailable. This is eight exact-call controls plus four shortened conv/GDN calls per teacher, serially after all16.
3. **Measured initial-state sensitivity, only if initial values differ.** The drain may compare all six unordered RID pairs' initial values without labeling their source/cache phase. With one captured input fixed, compare private scratch copies of the actually unequal same-P states, keeping pair RIDs in the receipt for the subsequent source join. Run conv and temporal sensitivity separately; do not hide conv-output differences inside a changed recurrence input. Report local sensitivity, not a serving fix. No synthetic state, live-state replacement or application of 1693/97344 to 1695. These conditional replays do not increase the serial live-memory budget.

Do not replay the whole model, rerun requests before drain, change native lengths during serving, or open a second generic replay entry point. The separate same-input operator investigation owns synthetic 7253/8192/7232 test design and snapshot reference arithmetic. Its result can be cited beside these actual-value receipts without duplicating that probe.

| Observation | Defensible interpretation | Still not established |
| --- | --- | --- |
| Initial conv/temporal differs; fixed-input state replay changes common outputs | H1 has measured local state sensitivity in addition to its structural path. | That the state is invalid, that it causes score failure, or that copying a canonical donor fixes the business run. |
| Initial state equal, common conv input equal, conv common output differs | Local conv/native-shape behavior is a candidate; inspect captured-call control and actual shape replay. | Temporal H3 alone or an earlier/global divergence. |
| Initial state and common `q,k,v,g,beta` equal, native common GDN output differs, and actual same-input shape replay reproduces it | Strong local evidence for shape-dependent arithmetic on these actual values, consistent with H3. | Why a particular score failed or whether higher layers have other differences. |
| Inputs already differ | Inputs/earlier history confound the paired output comparison. | H3 from those paired native outputs alone. |
| Exact captured-call control fails | This local witness cannot yet separate capture fidelity, replay layout and native variability. | A root cause or a justification to modify live state. |
| All measured layer-0 values and outputs equal | H1/H3 not numerically demonstrated at this layer/boundary. | Global equality; H1 at later layers, H2/H4 or the warm blocker being resolved. |

Because layer 0 precedes the first FULL layer, equal token prefixes and equal earlier chunk lengths make equal initial state/common projections a reasonable **prediction**, not an observed guarantee. A difference would be useful evidence; equality would narrow only this measured location. Do not claim earliest model divergence.

A negative synthetic operator test does not exclude actual-value arithmetic sensitivity, actual initial-state differences or conv effects. A positive synthetic operator test establishes capability, not occurrence on the approved source inputs. This witness remains necessary in either case to connect that result to actual initial state, actual inputs and the original source-paired output difference.

## 6. Error isolation and acceptance plan

Capture allocation/copy/descriptor/join/replay failures belong to the recurrent record set and return compact stage-specific `UNVERIFIED` receipts. Initialize its pinned allocations in a separate local try/catch after the existing FULL collector is constructed; a recurrent allocation failure must not disable that collector. Recurrent observation errors must use their own error list, not the existing `observe` catch's FULL-window `invalidate`. The probe must not convert an incomplete recurrent join/replay into failure of the already-completed scoring run or the existing FULL receipt. Keep the recurrent status independent of those unchanged existing statuses.

Observation methods must not return replacement values, suppress native training/serving errors, cancel the job, retry requests, block later native requests on a verdict, create alternate cache paths or raise their own validation exceptions into healthy serving. A poisoned CUDA context caused by an actual device failure may not be safely recoverable; report that limitation rather than promise isolation of native CUDA failure. B's independent run remains independent of A200 and of this diagnostic's completeness.

Smallest future changed-file list:

- `tests/manual/agent_opd/sglang_kv_coherence.py`: collector state, the three observations, P donor/publication extension, private drain replay/comparison, and exact staging anchors for `gdn_backend.py` plus the existing initialization. Generated edits remain in the private package only.
- `tests/manual/agent_opd/probe_teacher_scoring.py`: expose the four-request after-all16 recurrent join/receipt beside the existing FULL receipt; no experiment-order or server-config change.
- `tests/fast/test_sglang_kv_coherence.py`: proportional CPU-only tests for source-anchor insertion, unchanged original FULL control, eligibility/join ambiguity and soft-failure receipt paths. No synthetic native operator implementation.
- `tests/fast/test_teacher_scoring_probe.py`: affected consumer checks for the four-record post-all16 join, missing recurrent evidence and preservation of the original FULL/scoring receipts.

Planned CPU validation only; **not run in this design task**:

```bash
python -B -m pytest tests/fast/test_sglang_kv_coherence.py tests/fast/test_teacher_scoring_probe.py -q
python -B - <<'PY'
import ast
from pathlib import Path
for name in ('sglang_kv_coherence.py', 'probe_teacher_scoring.py'):
    path = Path('tests/manual/agent_opd') / name
    ast.parse(path.read_text(), filename=str(path))
PY
```

Planned native acceptance uses the existing prepared-private-package D40 probe and existing approved Python RJobBackend launcher, not a new submission script. Inside the worker, the existing business command remains:

```bash
python -B -m tests.manual.agent_opd.probe_teacher_scoring --config <existing-approved-D40-config.json> --pair <A-or-B> --samples <approved-first4-fixture.json> --output-dir <new-approved-D40-evidence-directory> --repeats 1 --request-timeout <existing-approved-timeout-seconds>
```

Resolve the concrete config/output paths from the owner's current prepared run rather than reuse or overwrite historical `admission-A-r3`/B results. No platform command is executed by this task. Acceptance: unchanged all16/ten-flush identity/order; four joined recurrent candidates per teacher or an honest incomplete receipt; initial conv and temporal captured before mutation; only existing post-all16 drain used; exact captured-call controls and common-row comparisons recorded; actual descriptor-based memory measurements; compact results only, with all failure and TP0/one-boundary limits explicit. A local equality failure or inconclusive replay does not reopen `281e`, authorize a behavior change, or release formal B/200.

Any later proposal to restore/copy live recurrent state, change rebinding or add a temporary behavioral intervention stays **pending causal evidence and the owner's applicable decision**, outside this design. Scratch replay copies above are only diagnostic inputs, not such an intervention.

## 7. Phase checkpoint

### 1. Planned completion

PASS 3; BLOCKED/FAILED/SKIPPED 1; TODO 0. This is completion accounting, not root-cause or implementation acceptance.

| Delegated subtask | Status | Evidence |
| --- | --- | --- |
| Locate reachable state/input/output and ownership seams | PASS | Section 2, actual after-source references. |
| Design smallest capture/replay lifetime and honest budgets | PASS | Sections 3–5, four candidates and descriptor-derived sizes. |
| Record implementation/validation plan in the sole owned artifact | PASS | Section 6; commands are plans only. |
| Execute or implement the diagnostic | SKIPPED | Explicit design-only delegation; no staging, commit or business/platform execution. |

### 2. Drift detection

No execution drift. Window: delegated design inspection through this artifact. Frontier: actual-value design; mainline: actual seams → capture/lifetime/budgets → acceptance plan.

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 Tooling polish | CLEAR | Only the smallest existing collector/probe extension is proposed. |
| D2 Retry loop | CLEAR | Source-reference corrections settled by actual file reads; no repeated business fixes. |
| D3 Side quest | CLEAR | No unrelated edit or operator-probe exploration. |
| D4 Stalled parallel work | CLEAR | Delegation explicitly forbids further delegation and execution. |
| D5 Gold-plating | CLEAR | One layer, one prefix, four candidates; no new framework/archive. |
| D6 Analysis sprawl | CLEAR | Design analysis is the requested deliverable. |
| D7 Off-route | CLEAR | Original protocol and CLOSED qualification retained; only the owned document changed. |

S1–S6: no defect in the delegated slice. Historical RCA authorization wording is superseded by the explicit current delegation, not a new blocking edge. Missing future conv descriptors/peak measurements and canonical publication joins are stated evidence limits. Attribution: none.

### 3. Route correction

Branch A for the explicit delegated scope; no spec/ticket update or user confirmation is required to accept this design. Stop actions: none. Finish this artifact and return to its owner. The owner may perform ordinary necessary approved preparation, then run the unchanged approved D40 experiment and inspect compact all16 receipts. Done condition is the honest capture/control/comparison acceptance in section 6, not a required equality or formal200 PASS.

### 4. Three points to retain

1. Initial conv and temporal must both be captured before mutation; metadata alone cannot establish their equality.
2. Compare only 6519 common rows; 1693's 97344 snapshot is not a valid restoration for 1695.
3. Own-input replay controls and actual-value shape comparisons remain necessary with either a positive or negative synthetic operator result; live-state intervention stays outside this design.
