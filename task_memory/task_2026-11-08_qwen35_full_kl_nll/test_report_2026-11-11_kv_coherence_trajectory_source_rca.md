## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record primary acceptance of the bounded source handoff only, distinguish common-token and own-prefix references, and prioritize the existing operator seam before new instrumentation. |
| 2026-11-11 | Created the bounded, source-backed warm-sample trajectory/handoff RCA; no runtime or source changes. |

# KV coherence: request trajectory and FULL handoff

TaskID: `profile-kv-coherence-r3-trajectory-source-rca-20261111`.

## Result

**SOURCE_BACKED:** Warm full-input sample 1695 starts with a cleared request-owned recurrent/conv slot, not a canonical cached Mamba donor. Its unfinished checkpoints adopt canonical FULL indices while retaining that request's active recurrent/conv slot. Donation changes a tracking slot, not the active slot. The next `prefix=98304, extend=638` therefore reads canonical OLD FULL history plus the fresh request's continuing recurrent/conv state.

**UNRESOLVED causality:** This establishes H1's structural handoff prediction, not numerical inequality of the recurrent states or proof that this handoff alone caused the score failure. No retained actual SSM/conv values, paired kernel inputs, or historical KV writer payloads settle H2/H3/H4. The qualified OLD/FRESH FULL differences remain accepted evidence, not a new eligibility question.

**PRIMARY ACCEPTED, bounded source stage:** The primary inspected the actual after sources at `unified_radix_cache.py:1305-1359`, `components/mamba.py:785-791`, `memory_pool.py:1813-1834`, and `gdn_backend.py:1209-1233`. This accepts the recorded control-flow separation only. Numerical state equality, the causal root, a fix, and formal execution remain unaccepted.

“Fresh request state” here means its continuously updated active state. It does **not** mean an isolated, all-fresh model trajectory: its earlier unfinished checkpoints already adopted canonical FULL history. FULL index correctness and recurrent-state trajectory coherence are distinct questions.

## Scope, identity, and evidence notation

Only this report and `evidence/kv-coherence-trajectory-rca-20261111/source-rca.json` are new. No source/config/test/raw/prior-report/task-document edits, staging, commits, delegation, model execution, GPU/CPU business execution, platform/auth/API/SSH access, or new collection occurred.

All paths below are relative to `task_memory/task_2026-11-08_qwen35_full_kl_nll/`:

| Alias | Exact retained path |
| --- | --- |
| N | `evidence/teacher-scoring-kv-coherence-probe-20261111/native` |
| A / B | `N/A/admission-A-r3` / `N/B/admission-B-r3` |
| P | `A/kv_coherence_source_preflight/after` (B has identical inspected after bytes) |
| F | `A/source_preflight/after` (selected FP32 after source; B identical) |
| S | `evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source` |
| R | `evidence/native-rust-kv-observer-build-20261111/sources/observer` |
| RB | `evidence/native-rust-kv-observer-qualification-20261111-r3/observer-build.json` |

The baseline is actual source `f8b6b43a`, qualified measurement `281e70f7`, accepted controls `4da`, R3 receipt `91458e`, and serving observer library SHA-256 `0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba`. Inspection used the actual retained **after** files, not just the checkout or Python's reference tree implementation. Seven pertinent P files and two F files were checked against both serving `result.json` after manifests. Five unchanged S files were checked against `S/../source.json`; four pertinent R files against RB's `source_manifest.after`. These are selective source-identity checks, not a new library/ABI/compiler/ownership qualification or an all-source audit.

Observed runtime options for both A/B: `chunked_prefill_size=8192`, `page_size=1`, `disable_cuda_graph=true`, `enable_unified_memory=false`, `enable_linear_replayssm=false`, `mamba_max_states_per_path=-1`, `mamba_track_interval=256`. Actual scheduler/plan rows use `state_chunk_size=cache_chunk_size=checkpoint_grid=64`; the generic interval setting is not substituted for that observed GDN grid.

OBSERVED = retained actual receipt or trace; SOURCE_BACKED = executed-source control flow plus that trace; INFERRED = consequence needing a value/counterfactual check; UNMEASURED = missing numerical evidence; FALSIFIED = a specified prediction contradicts the actual path. No global earliest token/layer, universal race absence, or causal root is claimed.

## Actual warm sample 1695 ledger

| Item | A native RID | B native RID |
| --- | --- | --- |
| Sample 1693, first warm full-input producer | `47d212ce1665413cbf65acc5cd161c5b` | `f48f6a1953bb4cac91b2babb6abb5e4d` |
| Sample 1694, second warm full-input producer | `a5212a22128749d3a1fa27623f66fa68` | `207bda6c0a97403fb7592e59f6e62119` |
| Sample 1695, inspected warm full-input request | `d1f39efbb85546309cb149c82d6341e3` | `ab9c724339da47169960dcd488c647cd` |

`requests.jsonl` records `input_count=98942`, `logprob_start_len=0`, `cache_salt=null`, `cached_tokens=0`, and `num_retractions=0` for both target RIDs. `P/srt/managers/schedule_batch.py:1726-1729,1772-1791` caps the admission match at `logprob_start_len`; zero forces recomputation from prefix zero even in a warm tree. The trace confirms prefix zero, rather than assuming “warm” implies canonical-state admission.

| Boundary/object | Actual provenance and state disposition | Evidence |
| --- | --- | --- |
| `[0,90112)` FULL, nodes 112 through 122 | First warm full-input sample 1693 publishes successive 8192-token chunks. Samples 1694/1695 deduplicate all eleven boundaries against these canonical nodes (`mamba_exist=true`). | A checkpoint-return sequences 19313–21143, 21512–23352, 23853–25693; B 12353–13523, 13760–14940, 15261–16441. |
| Sample 1693 last chunk | `prefix=90112, extend=7253`; aligned tracked state is at 97344, selected chunk 113. Finished insertion produces node 123 at that endpoint, with Mamba donor attached (`mamba_exist=false`). | A 21145/21147/21324–21326; B 13525/13527/13638–13640. |
| Canonical FULL `[90112,96631)`, observer node 124 | Sample 1694 splits node 123 at common-prefix end 96631. FULL head retains sample 1693 payload; Mamba remains on original child 123 at endpoint 97344, not new prefix 124. | Actual fragment 124 in each target bank; prior sample 1694 insert returns `prefix_len=96631`; R split semantics below. |
| Canonical FULL `[96631,98067)`, observer node 125 | Sample 1694 produces new FULL suffix `[96631,98304)` and node 125; its donor is its own active-final tracked state at 98304. Sample 1695 later splits this node at 98067. Prefix node 126 receives FULL head but no Mamba; child 125 retains sample 1694 endpoint state. | A 23533–23536; B 15055–15058; actual pre-split observer fragment 125 has length 1673 but observed overlap only 1436. |
| Incoming FULL `[90112,98304)` | Sample 1695 computes 8192 tokens using its live active slot; produces a final-state checkpoint at 98304. Its incoming duplicate FULL span `[90112,98067)` is released; source is incoming `state.value`, not the canonical node's value. | A 25695/25697/25874–25879; B 16443/16445/16556–16561; R overlap source below. |
| New FULL `[98067,98304)`, leaf 127 | The fresh suffix is 237 rows; leaf 127 receives the target request's donated tracked state at 98304 (`mamba_exist=false`). That state is not copied into the active slot by cache insertion. | Actual banks' `rebind`: `Q=98067,node_id=127`; actual checkpoint-return rows and R Mamba commit source. |
| Next `prefix=98304, extend=638` | FULL history is the canonical path ending at 127: OLD `[0,98067)` plus target suffix `[98067,98304)`. Both temporal and conv use the retained target active slot. Future unaligned tracking selects chunk 9, endpoint 98880, not an initial-state restore. | A 25880/25882; B 16562/16564; actual P kernel/metadata paths below. |

This provenance labels the request that supplied canonical FULL bytes. It does not assert every earlier byte remained historically untouched without a writer-value witness.

## Executed checkpoint and state control flow

1. **Admission seeds the target request by clearing both state types.** `P/srt/mem_cache/memory_pool.py:1603-1619` allocates an active slot only when the request does not hold Mamba and sets `mamba_needs_clear=true`; continuing chunks retain it. `P/srt/model_executor/model_runner.py:1958-1988` clears on the forward stream. `P/srt/mem_cache/memory_pool.py:1157-1171` clears conv and temporal. Actual clear rows are A sequence 23671, metadata file line 2070566; B 15145, line 1312148. Each target RID has one clear and zero `mamba_cow_enqueued` rows. The preceding root match is `cow_match_skipped/no_device_state`; it is consistent with the zero match cap, not independently RID-tagged. `P/.../components/mamba.py:201-245` shows what a real canonical COW selection would set/record; none is observed for either target.

2. **Donation does not replace active state.** `P/srt/mem_cache/unified_cache/components/mamba.py:643-746` prepares the checkpoint. Extra-buffer donation calls `P/srt/mem_cache/memory_pool.py:1813-1834`, which replaces only the donated ping-pong tracking entry. The no-extra-buffer branch instead copies active conv+temporal into a new donor (`mamba.py:728-735`; `memory_pool.py:1173-1212`), also not an active-state restore. Actual mask/track rows and `last_track_idx/next_track_idx` show the ping-pong route here. At 98304 sample 1695 uses tracked final state, not a selected partial-state buffer.

3. **The actual Rust walk preserves canonical overlapping FULL.** `P/srt/mem_cache/unified_radix_cache.py:668-694` pumps `begin_insert/resume_insert`, applying actions at each step. R's `src/unified_tree_core.rs:1989-1999` invokes the OLD observer **before** `split_node_`. `:2084-2131` obtains `value_slice` from incoming `state.value`, computes the duplicate portion, and emits the corresponding frees. `R/src/components/mod.rs:192-205` supplies the default overlap behavior; FULL and Mamba do not override it. This is not an inference from a Python insert walk.

4. **Split separates FULL location lists, not recurrent histories.** `R/src/unified_tree_core.rs:2290-2359` creates a prefix parent and redistributes components. `R/src/components/full.rs:80-98` and `R/src/node.rs:605-622` split canonical FULL lists into copied head/tail lists. `R/src/components/mamba.rs:261-276` gives the new prefix no Mamba device/host value; the original child retains its endpoint state. No mid-prefix state is manufactured at 96631 or 98067.

5. **Existing-node snapshots are kept; new-leaf snapshots are donated.** `R/src/components/mamba.rs:156-191` installs the incoming Mamba donor for a new leaf or missing-Mamba node; an existing snapshot is retained, LRU refreshed, and `mamba_exist=true` returned. Thus nodes 112–122 retain sample 1693 snapshots; node 125 retains sample 1694's endpoint snapshot after splitting; leaf 127 receives sample 1695's endpoint snapshot. `P/.../components/mamba.py:785-791` frees an unused donor for an unfinished request when `mamba_exist=true`, and resets tracking sequence bookkeeping only. It does not change `req.kv.mamba_pool_idx`, copy canonical Mamba into it, or restore conv.

6. **Canonical FULL is rebound independently of active Mamba.** `P/srt/mem_cache/unified_radix_cache.py:1305-1359` writes canonical path indices into the request row, changes locks/protected length/last node, then performs component cleanup. `S/srt/mem_cache/common.py:271-280` checkpoints and advances `req.prefix_len` to `req.extend_end`. The actual rebind is A sequence 25879 (metadata line 2265454), B 16561 (line 1435684), followed by the next scheduler boundary A 25880/B 16562. There is no canonical Mamba restore in that path. Zero Python `mamba_node_commit` metadata rows further prevents treating that reference Python hook as an actual executed Rust commit witness.

7. **Both active state types feed the next extend.** `P/srt/mem_cache/memory_pool.py:1633-1645` maps the retained active slot to the request row. `P/srt/layers/attention/hybrid_linear_attn_backend.py:193-205` obtains/translates that mapping. `P/srt/layers/attention/linear/gdn_backend.py:979-987,1035-1052,1075-1089` selects conv+temporal from the layer cache. Its `:942-953` passes the same active cache indices to conv with `has_initial_state=(prefix>0)`. Its `:1209-1233` passes active temporal and indices to GDN. `F/srt/layers/attention/linear/kernels/gdn_triton.py:187-195,213-225` passes `initial_state_indices=cache_indices`, defaults `inplace_update=true`, and passes `cu_seqlens=query_start_loc`. Actual allocation rows show `needs_state_gather=false`, excluding a hidden contiguous gather/scatter restore here. Exact physical Mamba slot IDs and contents are **UNMEASURED**; metadata object descriptors are not slot values.

## Live varlen and snapshot bounds

Actual GDN has a non-null two-element `query_start_loc`, passed as `cu_seqlens`; therefore this single-request packed extend exercises the varlen branch despite batch size one. `S/kernels/ops/attention/fla/chunk_delta_h.py:88-99` derives `bos/eos/NT/boh` from cu-seqlens and chunk offsets. `S/.../fla/index.py:29-35` produces cumulative `ceil(length/64)` offsets. `S/srt/layers/attention/mamba/prefill_track_metadata.py:34-56` selects per-row chunk and flattened source offsets; `chunk_delta_h.py:137-164,188-207` reads indexed initial state and writes the selected FP32 chunk-entry state. The observed row-zero plans are arithmetically consistent:

| Live request section | Selected state source | Actual A/B coverage | Check |
| --- | --- | --- | --- |
| Sample 1693: P90112 + 7253 | Selected FP32 `h_track_buf`, chunk 113 | 48/48 A GDN layers, 30/30 B | `90112 + 113*64 = 97344`; trailing 21 tokens are outside the donated key. |
| Sample 1694 and 1695: P90112 + 8192 | `final_state`; no selected buffer | 48/48 A, 30/30 B each | Endpoint 98304 is aligned; no partial donor read. |
| Sample 1695 next: P98304 + 638 | Selected FP32 `h_track_buf`, chunk 9 | 48/48 A, 30/30 B | `98304 + 9*64 = 98880`; trailing 62 tokens are outside the donated key. |

`P/srt/layers/attention/hybrid_linear_attn_backend.py:1047-1121` writes selected-buffer/final-state snapshots to **tracking** destinations. They are not restored into the next forward's active slot. No wrong source-row arithmetic is found for these observed row-zero plans. Source-correct offsets do not prove the actual kernel wrote the correct values.

The accepted `d7e7e301` operator evidence from `055011-398371` remains **equal-length only**: 44/44 passes, eight selected 64/128 snapshots exactly matching prefix FP32; 524283/524288 BF16-cast elements differ, maximum absolute error 0.0039055. Source/GPU operator acceptance does not establish a LIVE varlen donor. Model jobs `053300-533764`/`053259-677817` retained the same six source changes and still failed warm scoring. Neither test is repeated here. See existing `test_report_2026-11-11_mamba_fp32_snapshots.md` and `test_report_2026-11-11_snapshot_semantics.md`.

## Pre-registered hypothesis assessment

H1–H4 were supplied before inspection. They are not mutually exclusive: arithmetic divergence can precede a structurally mixed handoff, and a bad cached donor could affect a different cached-start request.

| Current priority | Hypothesis and falsifiable prediction | Assessment |
| --- | --- | --- |
| 1 | H1: FULL adopts OLD while the request continues its own active recurrent/conv state. Prediction: executed checkpoint/rebind source and target RID show that separation. | **SOURCE_BACKED structural prediction satisfied. UNMEASURED numeric/causal part.** Replacing/copying canonical active state during this unfinished checkpoint is contradicted by source/trace. Retained values cannot prove that the two state trajectories differ or that synchronizing them fixes scoring. |
| 2 | H3: correct initial state, but chunk/shape/arithmetic changes the common-prefix trajectory. Prediction: paired equal inputs and initial states yield different kernel outputs for actual competing shapes. | **OBSERVED shape difference; UNMEASURED prediction.** Original sample 1693 extends 7253 at P; samples 1694/1695 extend 8192. FULL L3 is already nonexact locally. Inputs/initial state equality and paired kernel outputs have not been retained, so no arithmetic root is established. |
| 3 | H2: LIVE varlen donor is wrong despite equal-length FP32 passes. Prediction: actual packed-cu-seqlens snapshot/index path selects or writes a wrong prefix state. | **LIVE varlen path SOURCE_BACKED; wrong values UNMEASURED.** Observed row-zero arithmetic supplies no concrete wrong-index evidence. **FALSIFIED for “sample 1695 was initially seeded from a cached partial donor”**: it starts cleared, and its checkpoint at E uses final state. Canonical node 123's partial donor can still matter for cached-start requests, not as this RID's seed. |
| 4 | H4: historic canonical payload overwrite/reuse before capture. Prediction: canonical writer-time value is changed by a later writer/reuse despite current owner validity. | **UNMEASURED, not globally falsified.** Actual overlap frees incoming duplicates, not canonical FULL. Accepted current ownership/readiness and source-correct frees are counter-evidence to that immediate overwrite mechanism, not a universal historical race proof. |

Accepted numeric archive `e2ab706a` (four primary-accepted artifacts) is consumed without reopening it: A 32/32 comparisons nonexact, 32424908/65167360 unequal elements, maxabs 59.03125 at L63 V; B 20/20 nonexact, 22514691/40729600 unequal elements, maxabs 16.3125 at L27 K. The first **locally inspected FULL layer**, L3, is already nonexact: A K/V maxabs 0.125/0.09375; B 0.359375/0.25390625. These are not earliest-global or earliest-token claims. They show the mismatch predates the observed final handoff payload comparison; structural H1 does not, alone, explain how that mismatch arose.

## Smallest necessary next proof — proposal only

Primary next-action decision: first inspect the already-working operator probe for a same-input/same-initial-state packed-varlen comparison, rather than immediately build another collector. That cheaper operator experiment can settle only its kernel prediction; actual request values and the original warm business loop remain necessary for a causal fix claim. This is ordinary preparation within existing D40 scope, not an additional user-approval gate. No new execution is recorded here.

The actual common-token range of sample1693 and sample1695 is `[90112,96631)`, **6519 rows**. The 7232-token reference ending at97344 is sample1693's **own** prefix and contains713 tokens beyond that shared range. It is valid for checking that request's selected snapshot, not for restoring or asserting equal state for sample1695. A controlled 7253/8192 shape comparison must explicitly construct identical prefix inputs and initial state; the two natural requests are not identical over7232 tokens.

**First obtain one actual live-varlen value witness at GDN layer 0 for the existing warm sample 1693/1695 P90112 boundary.** Layer 0 precedes FULL L3, and the competing 7253/8192 shapes are already observed. The missing evidence is (a) active temporal and conv at P for those requests, (b) the actual common-prefix kernel inputs `q,k,v,g,beta` (and conv input/output), and (c) sample 1693's tracked FP32 state at 97344 versus its own exact-prefix reference. Do not infer equality from descriptors or from the equal-length operator suite.

With these same-input/same-initial-state values, the minimum discriminating counterfactual is the **actual packed-varlen** call and its prefix ending after 7232 new tokens, with no dtype/compiler/backend change. Compare the selected chunk-113 state with the exact-prefix final state; also compare common-prefix outputs under the actual 7253 versus 8192 outer shapes. Wrong selected state with matching prefix recurrence supports H2. Correct selected state but changed common-prefix outputs under identical inputs/state supports H3. Different initial temporal/conv already at P requires an earlier request-state boundary comparison before attributing the difference to the P chunk. This is causal evidence only, not another prerequisite gate for the accepted KV archive.

**H1's business-effect test is conditional, not an implemented fix:** if this witness shows distinct active versus canonical state at the identical-token aligned P=90112 node 122, a single-variable comparison can synchronize **both conv and temporal** from that same-key checkpoint before continuing, keeping the already-authorized first-four unsalted protocol unchanged. A recurrent-only copy cannot test the complete state handoff. Do not copy node 125's endpoint state into sample 1695: its tokens diverge after 98067. Prefix node 126 has no Mamba, and leaf 127's donated state is already sample 1695's own endpoint state; copying 127 back would not replace the trajectory. Until a value witness exists, no source edit, cache bypass, namespace change, extra wait, tolerance, collector, or run is justified by this report.

H4 cannot be settled by the selected SSM comparison. It would require a canonical writer-time payload versus retained read comparison for exactly the disputed rows; no such historical witness is retained and this read-only delegation performed no new collection. Do not substitute current owner validity for that evidence.

The actual native feedback loop is already executed in unsalted protocol r1/r2/r3: 16 requests, ten flushes, four qualified contexts 97365/98312/98942/99074; cold 4/4, warm cold-full versus warm-full 1/4, stable. Business spans are approximately A91s/B64.8s, with model startup approximately 8–10 minutes. A seconds-only artifact checker is not the native bug driver. Further minimization is explicitly skipped at this measurement phase because the authorized first four are the qualification contract; this does not claim all four are proven irreducible. No further native execution is performed or proposed as already approved.

## Read-only verification record

Environment: Linux zsh; working directory `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`; `/usr/bin/python3` **3.10.6**, no conda/model dependencies used. HEAD observed `e2ab706aa44f87326429eea72f9c14591a6eeb14`. Python reads used `timeout 60s` and `resource.RLIMIT_AS=30 GiB`; no native libraries or model packages were imported. Relevant files were read through `read(path,offset,limit)` at the ranges cited above; `GLOSSARY.md:1-91` was read, and no `docs/adr` directory exists. Committed requirements/plan from `e2ab706a` were read; this later explicit delegation supersedes their numeric-frontier status lag without authorizing task-document edits.

Exact consolidated read-only source identity command (rerun for this report):

```bash
timeout 60s /usr/bin/python3 -B - <<'PY'
import hashlib, json, resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS, (30*1024**3, 30*1024**3))
T=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
N=T/'evidence/teacher-scoring-kv-coherence-probe-20261111/native'
R=T/'evidence/native-rust-kv-observer-build-20261111/sources/observer'
RB=json.loads((T/'evidence/native-rust-kv-observer-qualification-20261111-r3/observer-build.json').read_text())
S=T/'evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source'
SM={f['path']:f for f in json.loads((S.parent/'source.json').read_text())['files']}
rust=['src/unified_tree_core.rs','src/components/mamba.rs','src/components/mod.rs','src/components/full.rs']
unchanged=['srt/managers/scheduler.py','srt/mem_cache/common.py','srt/layers/attention/mamba/prefill_track_metadata.py','kernels/ops/attention/fla/chunk_delta_h.py','kernels/ops/attention/fla/index.py']
actual=['srt/mem_cache/unified_radix_cache.py','srt/mem_cache/unified_cache/components/mamba.py','srt/mem_cache/memory_pool.py','srt/managers/schedule_batch.py','srt/layers/attention/hybrid_linear_attn_backend.py','srt/layers/attention/linear/gdn_backend.py','srt/model_executor/model_runner.py']
fp32=['srt/layers/attention/linear/kernels/gdn_triton.py','kernels/ops/attention/fla/chunk.py']
for rel in rust:
    assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==RB['source_manifest']['after'][rel]['sha256']
for rel in unchanged:
    assert hashlib.sha256((S/rel).read_bytes()).hexdigest()==SM[rel]['sha256']
for pair in 'AB':
    p=N/f'{pair}/admission-{pair}-r3'; r=json.loads((p/'result.json').read_text())
    assert r['kv_coherence']['summaries'][0]['native_binding']['module_sha256']=='0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba'
    for label, paths in [('kv_coherence_source_preflight',actual),('source_preflight',fp32)]:
        for rel in paths:
            assert hashlib.sha256((p/label/'after'/rel).read_bytes()).hexdigest()==r[label]['observed_after_sha256'][rel]
print('PASS: 4 Rust, 5 unchanged, 7 actual-after + 2 FP32-after per pair; same retained serving library')
PY
```

Exact consolidated actual-RID/state-handoff projection (rerun for this report; contains no value or pointer audit):

```bash
timeout 60s /usr/bin/python3 -B - <<'PY'
import json, resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS, (30*1024**3, 30*1024**3))
N=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/native')
for pair in 'AB':
    p=N/f'{pair}/admission-{pair}-r3'
    requests=[json.loads(l) for l in (p/'requests.jsonl').read_text().splitlines()]
    target=next(d for d in requests if d['phase']=='warm_stream' and d['mode']=='full_input' and d['sample_index']==1695)
    rid=target['native_request_id']
    state=json.loads((p/'runtime_metadata.json').read_text())['server_info']['internal_states'][0]
    rows=[(seq,stage,dict(fields)) for seq,stage,fields in state['mamba_runtime_metadata']['rows']]
    clear=[seq for seq,stage,d in rows if stage=='mamba_clear_enqueued' and rid in d['rids']]
    cow=[seq for seq,stage,d in rows if stage=='mamba_cow_enqueued' and rid in d['rids']]
    boundaries=[(seq,d['prefix_len'],d['extend_len']) for seq,stage,d in rows if stage=='scheduler_track_boundary' and d.get('rid')==rid]
    handoff=[(seq,d['absolute_start'],d['absolute_end'],d['prefix_len'],d['node_id']) for seq,stage,d in rows if stage=='canonical_kv_rebind_enqueued' and d.get('rid')==rid and d['absolute_end']==98304]
    bank=next(b for b in json.loads((p/'result.json').read_text())['kv_coherence']['summaries'][0]['banks'] if b['rid']==rid)
    fragments=[(f['node_id'],f['lo'],f['hi']) for f in bank['fragments']]
    assert len(clear)==1 and cow==[]
    assert boundaries[0][1:]==(0,8192) and boundaries[-1][1:]==(98304,638)
    assert handoff[0][1:]==(90112,98304,98067,127)
    assert fragments==[(124,90112,96631),(125,96631,98067)]
    assert target['logprob_start_len']==0 and target['cache_salt'] is None
    assert target['meta_info']['cached_tokens']==0 and target['meta_info']['num_retractions']==0
    print(pair,'PASS','RID',rid,'clear',clear,'COW',cow,'handoff',handoff,'next',boundaries[-1],'OLD fragments',fragments,'SSM values',state['mamba_runtime_metadata']['physical_slot_values'])
PY
```

| Check | Expected / actual | Verdict and limit |
| --- | --- | --- |
| Selective source identity | All named after/unchanged/Rust files match their retained version-bound manifests; actual library receipt is the accepted 0dc library. | PASS; not a new compiler/FFI/ABI/ELF qualification. |
| Target request path | One clear, no COW, 13 extend boundaries, E98304 canonical rebind to leaf127 then 638-token next extend; exact OLD nodes124/125. | PASS for actual metadata/control flow; physical active SSM IDs/values remain UNMEASURED. |
| Donor path | Original unaligned selected state: A48/B30; target E aligned final-state copies: A48/B30; target next selected state: A48/B30; no gather. | PASS for recorded source selection and arithmetic, not donor numeric correctness. |
| Actual causal root / fix | Requires actual initial states/inputs and a single-variable counterfactual. | UNRESOLVED; not run, no fix claimed. |
| Initial exploratory projection | Requested nonexistent `result['metadata_source_preflight']`. | FAIL with `KeyError: 'metadata_source_preflight'`; corrected by inspecting actual `source_preflight` and `kv_coherence_source_preflight` keys. No runtime behavior changed. |
| Deliverable shape/scope | Two new owned paths only; JSON parses; required evidence/status bounds present. | PASS after the read-only artifact validation. |

## Scope checkpoint (check-progress self-check)

### 1. Planned subtask completion

PASS 3; BLOCKED/FAILED/SKIPPED 1; TODO 0. Source identity/control flow PASS; target-RID provenance/state ledger PASS; report plus compact JSON PASS. Additional native minimization/execution SKIPPED by explicit delegation, not a dependency for this investigation. Causal root remains outside completed acceptance.

### 2. Drift detection

Window: delegated bounded RCA inspection through these two artifacts. Frontier: source/trace-backed state handoff and smallest necessary proof. D1 tooling polish CLEAR; D2 retry loop CLEAR (one resolved JSON-key inspection error); D3 side quest CLEAR; D4 stalled frontier CLEAR (delegation expressly prohibited); D5 gold-plating CLEAR; D6 analysis sprawl CLEAR (analysis is the deliverable); D7 off-route CLEAR. S1–S4/S6: no defect in the delegated slice. S5: shared committed documents retain pre-numeric-frontier status lag, explicitly acknowledged by the later delegation; no conflicting scope change or dependent work is taken from that stale wording. Updating the eight shared documents is another owner's independent work, not a gate here.

### 3. Route correction

Branch A for the explicit delegated scope: no scope/ticket changes; no drifting behavior to stop. Finish the two owned artifacts and stop. Missing SSM/conv/kernel values are the next causal-evidence frontier only if separately authorized, not a reopened measurement prerequisite. No cleanup of unowned records, new scripts, execution, or namespace/cache-bypass proposal is needed to accept this report.

### 4. Three points to retain

1. Canonical FULL adoption does not restore either active state type; structural H1 is source-backed.
2. A cached leaf endpoint, a request's active state, and its donated tracking state are different objects with different token-prefix validity.
3. The causal gap is actual live-varlen values/equal-input counterfactuals, not another index/readiness/dtype/compiler gate.
