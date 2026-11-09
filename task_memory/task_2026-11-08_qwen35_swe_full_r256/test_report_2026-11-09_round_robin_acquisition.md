## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Reconstruct the sole approved routing-only A/r256 attempt, test existing serving hypotheses and record the unresolved capacity gate without changing science or submitting another run. |
| 2026-11-09 | Incremental full retained-log follow-up: recover all512 lifecycle payloads, native endpoint/GPU/TP maps and registrations; prove teacher131066 input guard and retain causal/memory/numerical limits. |

# Routing-only acquisition RCA

TaskID: **T02-ROUND-ROBIN-RCA**. Attempt:`exp-1109-010244-280221`. Local evidence verification: **PASS**. Acquisition: **FAIL227<231**. Fresh scoring/backward/optimizer/next-scoring: **NOT RUN /UNVERIFIED**. SessionID is not exposed in this child's available local evidence/tools; the primary retains the native subagent sessionID.

**Latest incremental evidence is in Section7.** It resolves the original packet's lifecycle/map/teacher-diagnostic gaps without rerunning packet analysis. The old measured-versus-causal limits and227/231 failure remain; per-slot engine latency and cap2 safety are still unverified.

Only this report and`evidence/deepswe-round-robin-rca.json` are written under the task directory. Temporary standard-library CPU calculations are under`/data/ycfeng/tmp/T02-ROUND-ROBIN-RCA`. No network, SSH, API, auth, platform, GPU, cloud, config, production or resource operation was performed. D12 authorized exactly one experiment, now consumed; this analysis authorizes no retry or changed parameter.

## 1. Gates and complete slot accounting

| Gate | Verdict | Actual evidence /limit |
| --- | --- | --- |
| Same256 candidate UIDs, slots and sample indexes | **PASS** | Every new identity matches the prior RCA's256 rows and the old raw generation receipts'256 sample_index/source_uid pairs. No added/removed/reordered source UID. |
| Routing-only profile isolation | **PASS** | Exact JSON comparison changes only`router_policy`, `phase`, `run_root`, `shared_dir`.128K,n1,min231,1800s,models/seeds/math,TP2/DP4/CP1,8+2H200,max1 and graph-disabled remain fixed. |
| Resolved policy/startup chain | **PASS** | Selected log L131 is the final native router launch-args dictionary with`policy=round_robin`, not just launcher argv; L132 child exec agrees; L133–135 say router ready at20142. Per-request routing ledger/child internal policy dump is not retained. |
| Absolute deadline/accounting rule | **PASS** |1800.000047s between recorded start/deadline; freeze9.702ms after deadline; all229 finished slots ended before it. Late cancellation/server observations do not add membership. |
| Minimum acquisition membership | **FAIL** |227valid,29missing=`27generation-pending+2teacherHTTP400`; **shortfall4**. |
| Teacher target/validation boundary | **PASS for227 recorded successes** |229 request starts/ends:227success,2error,0pending.227 validation starts/ends, all success,0pending. This is native receipt evidence, not an independent reconstruction of reduced tensor payloads. |
| Sourcepatch preflight | **PASS, preflight only** | Live snapshot's`megatron_scoring_lifetime/source/preflight.jsonl` records observed before/after hashes and`patch_applied=true`; native scoring did not reach it. |
| Large-bank scoring/backward/optimizer/next scoring | **UNVERIFIED /NOT RUN** |0 successful updates; acquisition raises before these gates. No GPU-capacity or patch-effect PASS. |
| Platform terminal lifecycle | **Parent verified; locally unqueried** | Parent reports student`Failed`, teacher system-stopped with`Some critical tasks failed`, no manual-stop annotation. Student log independently shows native AcquisitionFailed and subsequent actor cleanup; no platform query here. |

All256 slots are individually enumerated in the JSON. The old raw bank's initial`slots` list is reduced to`{"length":256}`; it cannot itself establish identity. The actual old generation receipts cover every sample index, so the UID comparison is grounded rather than assumed. Both actual valid memberships are also checked against the old full membership list/new bank receipt. **Candidate membership is identical; valid membership is not.**

Missing generation slots:

```text
94,100,104,105,107,113,125,128,140,147,158,160,162,168,169,181,192,195,197,200,201,211,214,215,218,222,246
```

Each has an original`QWEN35_SAMPLE_ATTEMPT` cancelled end receipt with`phase=student_request`, a start before the deadline, an end after it and no teacher start. Thus all27 are **confirmed generation-pending**, not teacher-pending or validation failure. Other missing classes: teacher pending0, validation/error2, other0. The original scoped packet retains only3generation starts and5success/27cancelled ends (32 distinct invocations). Full retained logs now resolve all256 paired attempts and the full successful **adapter** timing quantiles (Section7); the packet-only limitation was a selection gap, not missing native instrumentation.

| Teacher error slot | Prompt /completion /total tokens | Teacher request duration | Request start /error finish elapsed seconds |
| --- | --- | ---: | --- |
|58 |130,983 /87 /131,070 |0.659s |653.163 /653.821 |
|150 |130,723 /347 /131,070 |206.301s |1501.623 /1707.923 |

Both are HTTP400. The packet omitted the rejection diagnostic; full teacher logs now prove`131070input>131066allowed` (Section7). Raw HTTPJSON response bytes are not recorded. Restoring only these outcomes with all else fixed yields229<231, so it cannot alone close the gate.

## 2. Exact chronology and teacher timing

Numeric event clocks map to UTC on2026-11-08 despite the attempt/report's local2026-11-09 date:

- Start:`17:12:16.686939Z` (`1794157936.6869392`).
- Deadline:`17:42:16.686986Z` (`1794159736.6869864`).
- Failed freeze:`17:42:16.696689Z` (`1794159736.6966887`), **+0.009702s**.
-27 cancelled adapter ends: elapsed**1800.076–1800.149s**, after membership freeze. Their student-request elapsed lower bounds at the deadline are**1657.229–1697.526s**.
- First captured business serving observation: elapsed**154.313s** (`17:14:51`), versus oldA's144.137s. These are first **selected observations**, not actual first admission or a measured preprocessing duration.
- First/last valid bank finish: elapsed**171.293 /1797.790s**; the last is about2.21s before cutoff. Validation occurs before that membership receipt.

488 captured adapter/teacher/validation terminal intervals have process wall-minus-monotonic differences between−27.14µs and+1.07µs. This does **not** measure cross-host/server clock offsets. Printed serving seconds are `[t,t+1)`; strict summaries include only intervals wholly before the deadline. There are563 selected engine observations:3before acquisition,554strictly before deadline and6after it. Ray repeat markers are not expanded. Source indexes below are **one-based selected packet log indexes**, not original full-log filesystem line numbers.

Teacher success request durations are queue-inclusive: **p50=68.038s,p95=250.449s,max265.711s**, versus oldA35.783/87.492/100.178s. Client in-flight peak is**37**, versus16; it is not teacher engine concurrency. All started requests finish before cutoff. Teacher validation p50/p95 is**0.022333/0.033834s**. Thus teacher waiting grew, but **none of the27 missing slots reached teacher**. Faster student admission can increase teacher backlog; no throughput guarantee follows from changing concurrency.

| Elapsed minute end | OldA valid cumulative | New valid cumulative | New valid finished that minute | New teacher in-flight |
| --- | ---: | ---: | ---: | ---: |
|26 |198 |194 |8 |26 |
|27 |200 |203 |9 |24 |
|28 |203 |211 |8 |17 |
|29 |204 |218 |7 |9 |
|30 |206 |227 |9 |0 |

The JSON retains all30 minute bins. Pending prompt length remains unavailable for slots94/100; all pending completion lengths are unobservable. Completed generation populations differ: new229 requests have prompt p50=81,309 and completion p50/p95/max=201/2360.4/5182; old207 have79,308 and242/2483.5/5150. These are **completion-conditioned populations**, not all256 candidates.

The new valid curve is still194versus198old at26minutes and overtakes it at27minutes; final+21does not mean uniformly earlier completion. New valid-finish p50=980.090s versus old722.838s, also conditional on different successful populations.

## 3. Router, PID streams and per-engine observations

Native launch dictionary L131 includes`policy=round_robin`, `prefill_policy/decode_policy=None`, `pd_disaggregation=False`, empty initial`worker_urls` and host/port20142. Child exec L132 maps router actor7172→router20142; ready is confirmed by three components at L133–135. This exceeds evidence from argv alone. Full-log registration/controller mappings are now resolved in Section7; child-internal post-parse policy/final registration payload and per-request policy ledger are not retained.

The initial capture has four distinct TP0 engine streams, matching the fixed8student GPUs /2GPU-per-engine layout. Its freeze-GC errors were insufficient GPU/endpoint evidence alone. **Full native controller/manager state now resolves all four mappings** (Section7). Startup `/freeze_gc` ConnectionRefused stacks are followed by business serving and229 completed generation boundaries; they are not the observed terminal failure. Terminal cause is explicit at selected L816–818:`AcquisitionFailed: Only227 valid trajectories; need231`; later actor cleanup is not a manual stop annotation.

| Actor PID | Strict selected business interval UTC | First/max/last queue | First observed business queue0 | Decode n;p50/p95 tokens/s |
| --- | --- | --- | --- | --- |
|7176 |17:14:51–17:32:15 |63/63/0 |17:32:15 |59;26.58/27.062 |
|7177 |17:14:58–17:42:15 |63/63/26 |not observed |114;26.28/27.2235 |
|7178 |17:15:02–17:35:22 |62/62/0 |17:35:00 |53;26.15/27.138 |
|7179 |17:14:56–17:40:11 |63/63/0 |17:39:18 |76;26.12/26.8025 |

All302strictly predeadline decode observations have`running=1`; all252prefill observations have`new_seq=1`,`running=0`,`new_token<=8192`. Prefill's running0 means a newly scheduled prefill sequence, **not idle**. All563 engine observations report graphFalse.

**Late reconciliation:** L739 at`17:42:15` has26queued+1running on7177, 0.687–1.687s before cutoff under the printed-second convention; this matches27collector pending. Three other streams previously record queue0, but exact idle time/simultaneous fleet state is unobservable. Six postdeadline observations include queue-dropping prefill/decoder records during cancellation/cleanup; none is newly accepted membership.

Per-stream **sample median native decode rates** by exact acquisition-elapsed windows, not fleet aggregates or time-weighted averages:

| PID |[0,300)s |[300,600)s |[600,900)s |[900,1200)s |[1200,1500)s |[1500,1800)s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|7176 |26.76 |26.79 |26.165 |26.58 |— |— |
|7177 |27.10 |26.50 |26.28 |26.30 |26.215 |26.02 |
|7178 |26.285 |26.54 |25.95 |26.10 |26.10 |— |
|7179 |26.57 |26.215 |26.50 |26.25 |25.97 |25.93 |

Each bin's exact selected first/last UTC/count and queue/token distributions are in`serving.streams[].elapsed_five_minute_bins`. `—` is no selected evidence, not proved idle. Rate denominator intervals are not provided; adjacent selected timestamps are not rate denominators. No summed8-GPU throughput or integrated prefill/decode time is claimed.

| PID | Prefill n | New-token field p50 | Cached-token field p50/max | Observed8192 chunks | Nonzero-cache observations |
| --- | ---: | ---: | --- | ---: | ---: |
|7176 |71 |3536 |43,712/129,152 |18 |48 |
|7177 |36 |4812 |34,528/123,392 |11 |22 |
|7178 |77 |4802 |27,200/129,280 |28 |45 |
|7179 |68 |4310.5 |61,504/128,128 |17 |42 |

New selected full8192-chunk observations are74/252, versus old36/210; cached-token medians are lower than oldA45,952–83,136. This is **consistent with reduced cache locality**, not an actual total chunk count, cache hit rate or causal prefill-time estimate. Cache/chunk continuation fields and Ray dedup prevent physically meaningful sums across observations. JSON quantile`sum` fields are arithmetic sums of selected values, not integrated serving work. Reported full-token-pool usage≤0.04 is not total VRAM/compute utilization or proof that two running requests fit.

## 4. Hypothesis tests and227 versus206

| Ranked existing hypothesis | Verdict | Decisive observation /limit |
| --- | --- | --- |
|H1 queued student work /single-request serving | **SUPPORTED; RR-only insufficient** |Initial observed queues63/63/62/63 are substantially more balanced than old46/45/110/50. Yet27generation-pending remain, matching26queued+1running on one stream. Count balance does not ensure balanced service cost. |
|H2 long decode causes head-of-line waiting | **SUPPORTED at sampled late boundary; pathological tail UNVERIFIED** |7177 has23 consecutive selected decode observations at queue26/running1 over17:39:13–17:42:15 (182nominal seconds), full-token field91,941→96,621, rate p50=25.93. Active progress continues while waiting count does not drain. No request ID proves one request identity; field delta is not asserted as exact completion tokens. |
|H1 prefill/cache cost dominates | **UNVERIFIED** |Long prompts/chunks and changed cached-token fields are observed. Actual admission/prefill/TTFT/decode split is absent; no primary prefill attribution or chunk/memory tuning recommendation is justified. |

The native generation-permit mechanism previously proposed in H3 remains excluded by the unchanged call path (`inference_rollout_common.py:102–124,128–150`): reward/teacher scoring begins after generation semaphore release. New teacher backlog is real, but direct teacher-pending0 cannot explain the27 generation-pending slots. Other CPU/HTTP/resource contention is unmeasured.

**Delta:** old207 completed generation boundaries−1error=206valid; new229−2=227valid. Thus **+22 generated−1 additional error=+21valid**, +8.203125percentage points of256, +10.194%relative valid count. Shortfall falls25→4; pending49→27. These are actual outcomes, not causal estimates.

43previously nonvalid slots become valid and22old valid slots become pending, leaving184shared valid slots. Their prompt hashes all match; only70completion hashes match and114differ. Named seeds/config equality do not make the executed decode workload identical. Sampling definition/weight/tensor details are reduced in the new metadata summary; **do not diagnose a math bug or claim numerical equivalence from these hashes**. With one unreplicated comparison, the entire+21cannot be assigned to routing, cache effects or any one timing component.

Current slack remains **4valid trajectories**. Fixing only the2HTTP400 errors yields229 and still requires2additional pending completions, with all other outcomes fixed. No defensible “add X seconds” or guaranteed throughput multiplier is identifiable. Threshold/deadline/length/math changes are **UNAPPROVED and not recommended**.

## 5. Minimum next action and any approval-dependent proposal

**Initial collection request — completed by the authorized parent read-only download. Do not repeat it.** The original requested scope was:

1. Full student log:`/mnt/ws-jfs/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/capacity-round-robin/r256/student/A/exp-1109-010244-280221.log` (worker-side alias starts`/mnt/codesign-exp/ycfeng`). Retain every`QWEN35_SAMPLE_ATTEMPT` start/end/status/phase, attempt_id/source_uid/sample_index and timing; current selection contains only35of the expected lifecycle lines.
2. Same log's engine `process_trampoline`/launch/registered-worker fields: PIDs7176–7179→serving endpoint/GPU visibility/TP ranks; router child resolved policy if already retained. Do not use the freeze-GC refused port as a verified serving endpoint.
3. Only already-retained request telemetry: rid→worker URL, enqueue/admission/prefill/decode/finish and prompt/output counts. If absent, mark unavailable rather than fabricate per-slot latency.
4. Paired teacher stdout selected by its existing readiness/launch receipt: real Prefill/Decode/queue metrics and exact HTTP400 body/context-validation message for58/150. **Teacher job ID/exact log path is absent from this supplied packet**; primary must identify it from the existing paired receipt. No guessed teacher path is offered.

The retained new full bank at`/mnt/ws-jfs/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/capacity-round-robin/r256/student/A/exp-1109-010244-280221/training/bank_0.jsonl` has the original sample payload before reduction. **Parent independently owns the requested sampling/weight/probability metadata collection; this child did not duplicate it.** It is needed for any matched-workload/numerical claim, not a proposed seed/math change.

The approved RR-only run genuinely exercised that policy and still failed; do not automatically repeat it. **Conditional next experiment, UNAPPROVED:** after reviewing the above and obtaining fresh user approval, one isolated A/r256 trial changing only existing`pairs.A.student.max_running_requests:1→2`, retaininground_robin,teacher cap1,graphFalse and every scientific/deadline/resource constraint. Existing task JSON/CLI transport supports this option (`run_swe_opd.py:111–114`); current logs do **not** certify its memory,numerical or offload safety. Do not bundle CUDA graphs, memory/prefill settings or teacher resources. Increased producer concurrency may worsen the measured teacher queue.

If approved, acceptance is actual≥231valid within the same1800s with the same256candidate identities/no refill/drop/cap, native canonical/finite-score/probability/weight/numerical checks and no native OOM. Fresh scoring/backward/optimizer ACK, next scoring and source-lifetime gates must then be reached and independently verified; acquisition alone is not capacity acceptance. **Cost:** one10-H200 allocation, acquisition≤5GPU-hours, plus startup/cleanup and unmeasured scoring/two-update costs. D12's one-run approval is consumed; this report performs or authorizes none of those actions. The formal200-update profile remains separate and has no router override.

## 6. CPU commands, actual verification and limits

Exact calculation command, local`/usr/bin/python3`3.10.6, standard library only; no framework/GPU imports:

These are historical packet-stage commands. They were not repeated in the incremental follow-up; use Section7's append/verify commands for the new evidence.

```bash
timeout 60s /usr/bin/python3 /data/ycfeng/tmp/T02-ROUND-ROBIN-RCA/analyze_round_robin.py > /data/ycfeng/tmp/T02-ROUND-ROBIN-RCA/calculation-output.txt
timeout 60s /usr/bin/python3 /data/ycfeng/tmp/T02-ROUND-ROBIN-RCA/verify_round_robin.py
```

The calculator reuses the prior temporary Stage1 quantile/overlap definitions. It checks actual old/new UID identity,229slot/teacher joins,227validation/member joins,27cancelled phases/timing, the exact4profile differences,1800s boundary and original input size/mtime preservation; it writes all256slot rows and563selected metric observations. Expected and actualCPU consistency: **PASS**; acquisition/native optimizer capacity remains **FAIL/UNVERIFIED**, regardless of parser success. Generated evidence serialization, internal assertions and independent final verification passed:

```text
PASS256ordered UID matches;227valid+2HTTP400+27cancelled student-request=256;0teacher pending; absolute1800s boundary.
PASS563selected metric lines, per-stream median rates independently matched, Ray repeats unexpanded, actual resolved router launch/ready chain.
PASS43new-valid/22lost/184shared valid;70shared completion hashes match; original7inputs including formal config size/mtime unchanged.
PASSowned JSON/report present and parseable/history-tagged; native acquisition remains FAIL, scoring/optimizer capacity UNVERIFIED.
```

Initial analysis stopped at a full old-slot-list equality assertion. Inspection established that this old list is reduced to a length dictionary (a subsequent list-index probe raised`KeyError:0`); the raw generation receipts and prior RCA retain every UID, so they were used as two exact identity witnesses. No original evidence or runtime behavior was modified to suppress this failure. The corrected identity assertion passed.

Current limits after full-log inspection: no source_uid→rid→engine stage ledger, exact active response length, prefill time share/rate denominator or peak cap2 memory; raw HTTPJSON bytes and source formula for the teacher's131066 input guard are not retained. Bank mathematical metadata remains parent-owned; platform terminal status is parent-verified, not queried here. No capacity PASS, implemented fix or new authorization is claimed.

## 7. Incremental full retained-log findings

Local inputs are`/data/ycfeng/tmp/T02-ROUND-ROBIN-RCA/native-full-20261109/student.log` (4,435 LF-delimited lines) and`teacher.log` (2,652). **S/T line references below are literal full-file LF ordinals**, not the earlier selected packet indexes. Python universal-newline reading would incorrectly add13 teacher progress-bar CR updates; the corrected reader matches ripgrep line numbers.

### 7.1 Complete adapter lifecycle — PASS

The logs actually contain512marker lines and512JSON payloads, **256unique matching start/end attempts**, not an expected-count assumption. Two multiargument print records split marker/payload: S3631→3634 and3656→3657. All256source UIDs match the already accepted candidate identities. End status/phase:229`succeeded/completion_validation`,27`cancelled/student_request`,0failed/timeout. Sample status:227completed,2truncated (slots58/150),27pending.

- Start receipts span S2830–3092, elapsed**83.814–145.102s**; first-to-last start spread**61.288s**. These are adapter/pre-dispatch envelopes, not isolated preprocessing or engine admission.
- Successful generation receipts span S3104–4093, end elapsed**162.129–1678.701s**. Complete229adapter duration p50/p95/max is**793.604/1408.674/1564.244s**, queue-inclusive; actual GPU execution time is not retained.
- Cancelled end elapsed remains1800.076–1800.149s; no generation validation failure is hidden among the missing slots.
- All27unique server disconnection/abort RIDs occur on **actor7177**, S4146–4178. They do not match adapter attempt_ids; exact individual slot↔rid identity is absent. This locates the stranded group on that engine without inventing which slot was actively decoding.
- All563prior student batch observations exactly match the full retained log. Prior serving statistics were **not recomputed**. The23late decode observations are now anchored at S4076–4117.

### 7.2 Native endpoint/GPU/TP maps and registration — PASS

All student engine endpoints share host`10.204.4.55`; GPU numbers are assigned host-local ordinals, not device UUIDs. Actual TP0andTP1log headers are present for each actor. `base_gpu_id=0` inside an engine process is remapped through its visible devices; it is not physical GPU0 for every engine.

| Actor/cell | Serving port | Host-local GPUs | Full-log evidence |
| --- | ---: | --- | --- |
|7177/cell0 |20073 |0,1 |CLI S2065; cell S2213; manager state`local_gpu_ids=[0,1]` S4220 |
|7176/cell1 |20037 |2,3 |Resolved server args S2106; cell S2215; manager state S4277 |
|7178/cell2 |20000 |4,5 |PID-tagged endpoint S2439 plus healthy endpoint/cell S2217,2513; manager state S4219 |
|7179/cell3 |20072 |6,7 |CLI S2080; cell S2219; manager state S4221 |

Router resolved policy remainsround_robin at S2062/2064. S2638/2641/2642/2643 retain four`POST router:20142/workers` **202Accepted** events. Corresponding controller cells mark serving at S2640/2645/2647/2649, before acquisition. Final worker-list/registration bodies and request-routing ledger are not logged; do not infer per-slot engine service time from these maps.

### 7.3 Source-derived teacher and exact400 rejection — PROVEN

`qwen35_pair_worker.py:218` constructs`run_root/teacher/pair/job/rank-0.log`; runtime adds`r256`. The inspected`evidence/deepswe-capacity-round-robin/r256/exp-1109-010244-280221/A/teacher-ready.json:2–16` binds **same job,pairA,rank0,2actualH200,100.101.128.251:30000,approved27B/model image**. Original source is`/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/capacity-round-robin/r256/teacher/A/exp-1109-010244-280221/rank-0.log`; parent downloaded its read-only`/mnt/ws-jfs/ycfeng` alias. This is a source-derived identity, not a guessed teacher job/path.

Exact diagnostic:

```text
Input length (131070 tokens) exceeds the maximum allowed length (131066 tokens). Use a shorter input or enable --allow-auto-truncate.
```

| Slot | Native guard/RID | Error completion | Observed delay |
| --- | --- | --- | --- |
|58 |T566,17:23:10,RID5988ab94aa924cfa82b6a7a06b380d1e |One-token prefill T569; server error T570; HTTP400 T573,17:23:10 |Client0.659s |
|150 |T2107,17:37:18,RID006a0341ec7b47e1b96ad47796cf23ef |One-token prefill T2475; server error T2476; HTTP400 T2477,17:40:44 |206nominal seconds guard→HTTP; client206.301s |

The HTTPemission second uniquely matches the existing58/150terminal receipts; there is no direct source_uid/RID tag in teacher stdout. **Both inputs are four tokens over the observed admission maximum**, despite configured context131072. Why the native guard reserves six versus configured context requires source inspection; it is not a GPU-memory estimate. Raw HTTPJSON response bytes remain **not recorded**.

The two one-token prefills immediately precede the400emissions. This is consistent with queued error-placeholder handling, but the internal source mechanism is **not proven** by logs. In particular,150's206s must not be called actual GPU scoring time for its131070-token invalid input. Do **not** follow the diagnostic's auto-truncate suggestion: shortening canonical history/outputs remains unapproved. Correcting only these two outcomes still leaves229<231.

### 7.4 Teacher queue/timing and conserved token counters

There are2,247teacher prefill observations,2before acquisition and**2,245inside** it; no decode batch observations. Every business prefill has`new_seq=1,running=0` (active prefill, not idle) and`cached_token=0`. Source window:T167at17:15:07 throughT2645at17:42:14. Peak observed queue is**36**, first seenT1777at17:34:17; maximum pending-token field3,510,670. Queue0atT231/17:15:38 means no waiting request, not no active chunk.

| Acquisition-elapsed bin | Exact selected first–last UTC | Queue first→last/max | Input-rate sample p50 tokens/s |
| --- | --- | --- | ---: |
|[0,300)s |17:15:07–17:17:16 |6→0/7 |15306.43 |
|[300,600)s |17:17:25–17:22:16 |0→0/3 |14717.16 |
|[600,900)s |17:22:25–17:27:16 |0→13/13 |13721.815 |
|[900,1200)s |17:27:17–17:32:16 |13→29/29 |13653.44 |
|[1200,1500)s |17:32:17–17:37:16 |29→27/36 |13496.61 |
|[1500,1800)s |17:37:17–17:42:14 |27→0/29 |13591.45 |

Binning uses printed-second lower bounds; exact`[t,t+1)`intervals/counts are in JSON, with<1sedge uncertainty. Input-rate denominator windows are absent; sample p50=**13671.78** is not a time-integrated GPU rate. The first sample is10.34tokens/s and therefore cannot be interpreted as a standalone kernel benchmark.

Unlike the selected/deduplicated student tape, teacher stdout has no Ray repeat coalescing. Its logged new-token counter conserves **17,524,816**: already measured valid canonical inputs total**17,524,814**, plus the two1-token events tied temporally to400emission. Business access logs contain exactly227POST/generate200and2POST400. This establishes counted uncached prefill volume, **not** request-level kernel time or guaranteed capacity headroom. All started teacher requests finish before cutoff; none of the27missing generation slots enters teacher.

### 7.5 Safety-relevant limits and next action

Actual student settings at S2092/2106: singletoncap1,ctx131072,chunk8192,max_prefill_tokens16384,FCFS,bfloat16,memory-saver and deterministic inference enabled,CUDAgraphs disabled. Startup reports:

- S2286/2396:KVcapacity3,161,377tokens and available GPU memory41.13/41.11GB. S2276/2277:K24.12GB andV24.12GB **per TP rank**.
- S2271/2272/2388:Mamba cache1808slots,conv0.99GB andSSM42.40GB **per TP rank**.
- Teacher T55–60/69:KV1,590,165tokens,Mamba607slots,startup available memory20.80GB; teachercap1 remains fixed.
- Router health warnings S4003(port20072,17:36:52) andS4112(port20073,17:41:52) occur while later serving progress continues. They do not prove a dead worker or explain the shortfall; retry/down effects are unmeasured.

**None qualifies max-running2 safety.** Startupfree memory/cache slots/token-pool usage are not cap2peak activation allocations, numerical correctness, offload/restore or fresh large-bank scoring. Onlycap1executed,0updates/no scoring remain. Existing logs have no linked source_uid→rid→admission/prefill/TTFT/decode ledger, no active pending-response length and no raw HTTPJSON bodies; repeating the same collection cannot recover those fields.

**Next:** parent completes its independent bank metadata work and prepares a source-derived teacher-boundary compatibility proposal that retains every canonical token. Any teacher serving-envelope correction or materially different studentmax1→2comparison needs **new explicit approval**, with separate variables and no automatic rerun. Keep128K,n1,min231/256,1800s,TP2/DP4/CP1,8+2H200,science/formal profile fixed unless separately approved. A proposedcap2smoke retains graphFalse/teachercap1; acquisition≤5GPU-hours plus startup/cleanup/unmeasured two-update cost. It is not safe or guaranteed to close the4slotgap merely because current pools are lightly used.

### 7.6 Incremental CPU verification

Exact commands,`/usr/bin/python3`3.10.6, standard library only; no packet rerun or GPU/framework imports:

```bash
timeout 60s /usr/bin/python3 /data/ycfeng/tmp/T02-ROUND-ROBIN-RCA/analyze_native_full.py --write > /data/ycfeng/tmp/T02-ROUND-ROBIN-RCA/native-full-calculation-output.txt
timeout 60s /usr/bin/python3 /data/ycfeng/tmp/T02-ROUND-ROBIN-RCA/verify_native_full.py
```

Expected checks:actual512payloads/256paired UID attempts;229success+27cancel;four nativeGPU/TPmaps/registrations;27abortRIDs on7177; exact131070>131066diagnostics at literalLFline ordinals;2245prefill rows and17,524,816conserved counter; preserved old metrics and original3new input sizes/mtimes. **Actual: independent final checker PASS all assertions**, including2truncated slots58/150, unchanged3new inputs, retained227/231FAIL and0updates. Appended JSON is parseable; internal reconstruction/conservation assertions alsoPASS. OnlyCPU evidence consistency passes; max2memory/numerics and native scoring/backward remainUNVERIFIED.

Reader corrections are evidence-specific: two marker/payload splits were found after a`ValueError:substring not found`; universal-newline reading was corrected to LF-only after13CRprogress updates shifted teacher source ordinals. No native behavior, captured input or configuration was changed to accommodate the analysis.

## Scope checkpoint — check-progress

### 1. 规划完成情况

**汇总：** packet-stage RCA及本次full-log补充均完成；512lifecycle、4engine映射/注册、teacher guard/queue和交付核对PASS。实验acquisitionFAILED；scoring/optimizerBLOCKED。PASS只表示分析交付完成，不表示capacity通过。

### 2. 偏离检测

**结论：** 未偏移。检测窗口为本次full-native-log follow-up；当前前沿是Ticket02的captured-evidence RCA收束，04–07仍受native capacity阻塞。已用现有logs解决可解决的缺口；未记录的per-request字段不继续重复索取同一文件。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
|D1工具打磨 |CLEAR |临时CPU计算用于要求的256slot/日志核对，不增加可复用harness。 |
|D2细节反复重试 |CLEAR |检查实际split JSONpayload及CRprogress格式后修正CPUreader；无native参数/实验重试。 |
|D3支线修补 |CLEAR |仅分析授权的acquisition，不修复新发现的生产问题。 |
|D4并行停滞 |CLEAR |本scope按用户要求Stage1→Stage2；独立08由primary继续。 |
|D5超范围镀金 |CLEAR |只交付两个指定文件与必要数据，不增加功能。 |
|D6分析空转 |CLEAR |full logs收敛到late queue、teacher131066guard与明确观测限；停止已完成的日志收集。 |
|D7路线违背 |CLEAR |保留D12参数；无GPU/config/resource动作。 |

**文档检查：** 本次scope要求与D12一致，未发现需改spec的缺陷。旧packet-stage检查曾记录S5：`progress.md:42/145`当时仍为pending/launcher-alive；本次不重复审计primary拥有的最新状态，也不声称它现在仍陈旧。一次4slot不足不证明D6不可达。

### 3. 纠正建议

**分支：A，本scope无需路线调整。** 旧S5状态建议由primary处理，不编辑其文件。full-log补充现已完成；primary独立完成bank metadata，再决定是否提交新批准请求。不得自动重跑routing-only、重复已完成的collection或把低pool usage当作max2安全证明。下一路线是RCA收束→source-derived边界/容量提案→如需materially different实验先新批准；不改spec/science。

### 4. 最值得关注的3点

1. RR初始queue更均衡，但最后一个stream仍有26queued+1running；门槛仍差4。
2.184共同valid中114completion hashes不同，不能把+21全部归因routing；prefill时间占比未知。
3. 完整student/teacher证据已收集；下一步是D13范围内的rollout资源选择。cap2及teacher包络改变仍未批准；不重复索取缺失的per-request字段。
