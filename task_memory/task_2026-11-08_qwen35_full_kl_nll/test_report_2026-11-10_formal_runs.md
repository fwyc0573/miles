## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Close the second pre-training A failure with five complete receipts; pause submissions at PLACEMENT_BLOCKED pending a strategy decision, without claiming complete stop-audit closure. |
| 2026-11-10 | Record first A terminal/native failure and incomplete stop audit; retain snapshots and separately document unchanged freshly admitted retry and read-only observer replacement. |
| 2026-11-10 | Diagnose partial placement from exact replica/Pod events and separate Ray startup deadline from acquisition/D19. |
| 2026-11-10 | Inspect first native worker receipts: rank0 eight H800 and ready teacher four H800; remaining ranks/engine startup unverified. |
| 2026-11-10 | Record A/full submission and exact platform identity/resource readback; first-update, B and terminal acceptance remain pending. |

# Formal A/B execution

## Configuration and prerequisites

The D35 consolidation is`55fba827`, per-turn CPU implementation is`6129aefe`, rollout/profile CPU integration is`15186817`, and explicit enabled formal configuration is`ec002ea8`. T02 and T03 each have Standards0/Spec0 reviews in[review.md](review.md). Launch code/config freeze HEAD:`606a9355`; no tracked changes under`miles/`, `tests/`or`scripts/`were present before submission. Task documents may progress independently.

Configuration:`formal_config.json`. Both cells use full mode,200 successful updates, H800/codesign,32 student/rollout GPUs plus4 teacher GPUs, source32×8, seq/context131072, prompt114688 inclusive and response16384. Profile is explicitly enabled with k10/B10/N8. See[the configuration and sample-lifecycle preparation report](test_report_2026-11-10_formal_configuration.md)for final dry-runs, real formal-driver/full-bank semantics and16 lifecycle checks. No additional profile GPU smoke was run.

## First A/full attempt — exp-1110-014836-849060 — FAILED, 0 successful updates

The startup observations below retain their original times and scope. They are superseded by the terminal/native failure evidence, not merged into the retry's results.

- Submitted2026-11-09T17:48:36Z (2026-11-10 01:48:36UTC+8). Historical local launcher shell handle:`sh_1c16d0f990014RQthEERNRrdWW`; kept alive during the workload. Log:`/data/ycfeng/tmp/agent-opd-image/formal-A-h800-112k-20261110.log`.
- Admission:[receipt](evidence/admission-formal-A-20261110.json). Fresh personal H800 non-preemptible inventory found0 committed GPUs for this creator before the36-GPU request; explicit ceiling isnull. This is not a claim that the shared cluster was empty or36 GPUs immediately available.
- Platform readback at17:49:29Z:[receipt](evidence/formal-A-submission-readback-20261110.json). Job UID`ccc4c4e4-3945-4159-8021-e0f0b17008f5`, creator`i-fengyicheng`, preemptible=false, task annotation matches this task, local source`100.96.128.195:/data/ycfeng:/data/ycfeng`.
- Observed status:`Starting`, reason`RJobStarting`, teacher active1 and student pending4. Platform resource requests are4×8 student GPUs plus1×4 teacher GPUs, positive tagH800. All four student replicas retain both RDMA limits. Requested placement is not yet worker`nvidia-smi`or engine readiness evidence.
- Final disposition: **FAILED, 0 successful updates**; training/acquisition/optimizer never started, so this attempt provides no first ACK or native profile consistency acceptance. Partial actual GPU receipts below remain startup evidence only. B was not submitted.
- Subsequent worker inspection: `student-node-0.json` confirms eight NVIDIA H800,81,559MiB each,driver570.124.06 on`gpu-h800-0180.host.platform.shaipower.com`; `teacher-ready.json` confirms four matching H800 and ready27B model endpoint. Both pin the configured image and model paths; selected fields are retained in[the startup receipt](evidence/formal-A-worker-startup-20261110.json). Student ranks1–3, all-engine readiness and first ACK are not yet verified. These are partial startup observations, not a claim that all36 devices or training are ready.
- Historical read-only first-update observer:`sh_1c16ff2bb0017aVjX6GHz8NQ1s`;60-second reads of native first-update/profile sizes,9,000-second soft observation window and output`evidence/formal-A-first-update-notification-20261110.json`. After this job was terminal, the primary positively identified its local Python PID2124241 by cmdline, cwd and17:51:41 start time matching its85-byte startup banner, then terminated that local observer. Its completed SIGTERM notification is intentional observer cleanup, not a GPU/job stop. No other job was stopped. The replacement observer belongs only to the retry below.

### Partial placement observation — 18:22Z

At18:16:21Z, A still had three active student replicas plus the active teacher and one Starting student ([readback](evidence/formal-A-startup-progress-20261110.json)). Native worker receipts additionally confirm eight H800 each for ranks1 and3, so28 actual GPUs are now evidenced. The remaining replica is`exp-1110-014836-849060-student-c81e728d`, UID`5d991bd1-2888-4dab-a3a7-55f279bd8b73`. Its18:17:46Z status is`PodScheduled=False`, `Unschedulable`, no IP, and its bounded log API response is200 with empty data ([replica evidence](evidence/formal-A-student2-startup-20261110.json)).

Exact-name Events read at18:22:21Z returned10 records with complete pagination, all`FailedScheduling`; the latest Pod/Replica events are18:21:47Z. They report167 nodes with insufficient GPU, plus CPU/memory shortages and node-affinity exclusions. These categories overlap and are not a capacity total. The actual Pod UID is`5f341f32-8467-4c1b-95af-cc730699f68d`, distinct from its owning Replica UID. Current status remains unscheduled; evidence:[events](evidence/formal-A-student2-scheduling-events-20261110.json).

The rank0 cloud log records Ray start at17:53:51Z and connection at17:53:53Z. Local`head.json`mtime is17:53:53.051Z. Read-only code investigation`profile-formal-startup-deadline-20261110`locates the independent cluster-complete1800-second wait at`rjob_warmup.py:180–206`, so its expiry is approximately18:23:53Z (monotonic clock; wall-clock estimate only). The rollout acquisition1800-second clock has not begun. This is a resource-placement/startup blocker, not D6 acquisition failure or evidence of OOM. The earlier18:22Z snapshot does not yet establish terminal failure.

Existing mechanisms tolerate a late worker only within this startup window; no live timeout/config alteration was made. If native startup times out, retain this attempt separately and perform fresh admission for any subsequent attempt. D19's specific more-GPU response to first-update rollout/teacher throughput does not apply to a worker that never starts. `gang_start` is not an established fix: the handbook records cross-task ConfigMap injection and prior single-node teacher failures, so it was not changed speculatively.

### Terminal failure and partial RCA — 18:24–18:27Z

The18:25:02Z [deadline readback](evidence/formal-A-deadline-readback-20261110.json) confirms job Failed, finishTime2026-11-09T18:24:34Z andall five replicas Failed/Stopped, withno active replica. The retained system annotation says`Some critical tasks failed.` It does not establish an audited stop-request actor or time.

The initiating native failure is retained in[the native failure chronology](evidence/formal-A-native-startup-failure-20261110.json): rank0 `training.json` and `finished.json` have mtime2026-11-09T18:23:55.179530Z andrecord TimeoutError at`rjob_warmup.py:206`. The exact literal error is:

> Ray did not register the requested two-node GPU allocation

"two-node" is a hardcoded diagnostic string, not the configured topology: this attempt configuredfour student nodes,4×8 GPUs. Rank2 `PodScheduled=False/Unschedulable` andthe10 fully paginated FailedScheduling Events remained the placement evidence through18:22Z. The native cluster-complete wait then expired before acquisition/training/update began;0 successful updates. The later rank1 failure at18:24:16Z, rank0/rank3 143 or-15 exits at18:24:21–23Z andteacher shutdown at18:24:27Z are subsequent chronology, not proof of a new initiating failure, OOM or D6/D19 throughput.

Primary RCA collector root:`/data/ycfeng/tmp/agent-opd-image/formal-A-placement-failure-20261110`. The[query coverage receipt](evidence/formal-A-rca-query-coverage-20261110.json) records6 successful queries and2 failed all-operation audit queries (`rjob-audit`, `replica-audit`, ReadTimeout after10s). Primary reports existing DeepScan0 flows. Collector exit1 means partial RCA query failure, not another GPU failure. Native initiating failure is known; `audited_stop_actor=UNKNOWN` and `audited_stop_request_time=UNKNOWN`. Full RCA/auditable stop closure is **NOT established**; the missing audit coverage stays explicit anddoes not require stopping healthy retry training.

### Exact first-attempt submission

Run from`/data/ycfeng`, using the handbook proxy/personal-auth initialization (`BRAINPP_ACCESS_KEY`/`BRAINPP_SECRET_KEY` from permission-restricted local files; values never logged). Environment:`STEPMIND_BACKEND=rjob`, `PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image:/data/ycfeng/steptron`, `PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR=/data/ycfeng/tmp`. StepMind interpreter:`/data/ycfeng/tmp/stepmind-env/bin/python` (Python3.10.6); worker interpreter is the frozen image's`/opt/sglang/bin/python3`.

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_swe_opd --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/formal_config.json --pair A --protocol full --receipt /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/admission-formal-A-20261110.json > /data/ycfeng/tmp/agent-opd-image/formal-A-h800-112k-20261110.log 2>&1
```

Submission holds the existing lock around fresh inventory and backend creation, then waits on the job; no replacement process or alternate submission route is used. Platform inspection uses`steptron.utils.stepmind.get_rjob_client().api.get_namespaced_custom_object(...)`for this exact job with a20-second request timeout and saves only selected identity/status/resources.

### Evidence locations and first-update inspection

- Worker/local receipts:`evidence/formal-h800-112k-20261110/full/exp-1110-014836-849060/A/`.
- Durable training records:`/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/formal-h800-112k-20261110/full/student/A/exp-1110-014836-849060/training/`.
- Profile:`distillation_profile/{observations,updates}.jsonl`inside the training directory. Read both files together; a paired prefix is not automatically the complete run.
- D16 checks actual successful ACK and counters first, then bank/source UID and token/turn counts, pre-TIS macros, estimator, profile pairing/rebuild and stage timings. Record auxiliary failures/unverified intervals separately while healthy native training continues. B may be admitted after this inspection and A's first real success; it does not wait for A200 or an auxiliary PASS verdict.

## Second A/full attempt — exp-1110-022844-821769 — FAILED, 0 successful updates

The admission,18:31:08Z placement readback and exact submission below are historical snapshots. Final failure evidence supersedes them; they are not a current running attempt or a result to combine with the first attempt.

- Created2026-11-09T18:28:44Z (2026-11-10 02:28:44UTC+8) under the existing formal execution authorization, after the old attempt andall five replicas were terminal. This is one fresh submission withthe **same unchanged configuration, source, image, four-node topology, lengths andtimeouts**. No code/config fix, more-GPU D19 response, business-test rerun or new scientific choice occurred; existing CPU/configuration/lifecycle readiness is reused.
- Fresh[admission receipt](evidence/admission-formal-A-r2-20261110.json): creator`i-fengyicheng`, own nonterminal H800 committed0, requested36, preemptible=false, ceilingnull, admitted/submitted=true, local source`100.96.128.195:/data/ycfeng:/data/ycfeng`. Own committed0 is not a claim that shared cluster GPUs are empty or immediately placeable.
- Direct platform[submission readback](evidence/formal-A-r2-submission-readback-20261110.json) at18:31:08.667805Z pins UID`a54101b9-6baf-4c84-a0c9-ac2897bded83`, creator/task/source andnon-preemptible4×8 student plus1×4 teacher request. StatusStarting/RJobStarting, student active2/pending2 andteacher active1. This is placement/status evidence, **not** actual`nvidia-smi`, all-engine readiness orsuccessful optimizer ACK proof. Old attempt's28 actual devices cannot verify this retry.
- Historical retry launcher:`sh_1c191cdc5001x6Xr3PoAy7Gg2n`; log:`/data/ycfeng/tmp/agent-opd-image/formal-A-r2-h800-112k-20261110.log`. Its exact submission changed only receipt/log paths to`-r2`; original environment/interpreters/config/argv stayed unchanged. This is not a claim that the now-terminal workload is still running.

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_swe_opd --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/formal_config.json --pair A --protocol full --receipt /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/admission-formal-A-r2-20261110.json > /data/ycfeng/tmp/agent-opd-image/formal-A-r2-h800-112k-20261110.log 2>&1
```

- Historical retry read-only observer:`sh_1c193b14f00106un9zmHJvU6bW`; output`evidence/formal-A-r2-first-update-notification-20261110.json`is outside this selected immutable receipt commit. Its configured9,000-second soft window checked retained native failure aswell as first successful ACK; observer errors/timeouts/verdicts do not stop orchange GPU training. Current local observer state is not independently verified here; no cleanup or GPU action is performed by this documentation slice.
- Worker/local attempt receipts:`evidence/formal-h800-112k-20261110/full/exp-1110-022844-821769/A/`. Durable native training root:`/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/formal-h800-112k-20261110/full/student/A/exp-1110-022844-821769/training/`; profile files remain`distillation_profile/{observations,updates}.jsonl`there. All formal outputs, including the failed attempt, areprotected andnot smoke-cleanup candidates.
- Final disposition: **FAILED, 0 successful updates**, before acquisition/training. No successful ACK, D16/02 GPU or200-update native/profile acceptance is supplied by this attempt. Both failed attempts remain protected and separate; the placement/startup strategy decision below is now the frontier.

### Second-attempt failure — 19:02–19:06Z

The missing student was rank3, `exp-1110-022844-821769-student-eccbc87e`, with no IP and `PodScheduled=False/Unschedulable`. Rank0/rank1 were scheduled at18:28:46Z; rank2 at18:38:11Z. The[first transitional failure readback](evidence/formal-A-r2-failure-readback-20261110.json) at19:03:11.473087Z still reports job phaseRunning/reasonRJobStopping and a teacher task active count. It must not be relabeled as final Failed or interpreted as successful native training.

The[native failure receipt](evidence/formal-A-r2-native-startup-failure-20261110.json) pins rank0 `training.json` TimeoutError at19:02:35.748Z, with full traceback at`rjob_warmup.py:206`, before peer failure/SIGTERM chronology. Preserve the literal diagnostic exactly:

> Ray did not register the requested two-node GPU allocation

Actual `expected_student_nodes=4`; "two-node" is the hardcoded error text, not the actual topology. The missing fourth rank prevented cluster startup; acquisition/training never began and successful updates=0. This is placement/native startup failure, not OOM, D6 collection throughput or D19's more-GPU response to first-update throughput.

The19:06:54.726589Z personal API[terminal readback](evidence/formal-A-r2-terminal-20261110.json) confirms job Failed/finishTime2026-11-09T19:03:12Z, student1 Failed+3 Stopped, teacher1 Stopped and all five replicas terminal. It supersedes the transitional stopping readback, not its original fields.

Rank3[selected events](evidence/formal-A-r2-student3-events-20261110.json) contain three records with continuationnull: two FailedScheduling (Pod and Replica at19:00:35Z) and one SuccessfulDelete (Replica/controller at19:02:59Z). Resource/affinity categories in scheduler messages overlap and are not an available-GPU total. The controller deletion event is not a complete audited stop-request actor/time claim.

RCA collector root:`/data/ycfeng/tmp/agent-opd-image/formal-A-r2-placement-failure-20261110`. The[coverage receipt](evidence/formal-A-r2-rca-query-coverage-20261110.json) records6 successful reads, both all-operation audits (`rjob-audit`, `replica-audit`) ReadTimeout10s andzero existing DeepScan flows. Collector exit1 is limited audit-query failure, not another GPU failure. Placement shortfall and native initiating error are established; audited stop actor/request time remain **UNKNOWN**, so no complete platform stop-audit closure is claimed.

### Current route — PLACEMENT_BLOCKED

Both formal A attempts failed before acquisition/training with0 updates. Primary has paused submission; **no third attempt, chosen placement/startup strategy or new approval is recorded**. Primary independently inspects native SDK mechanisms and authoritative Lark documentation; its SDK task is`ses_e3e4c91c2ffeH93O77e3RX5SB1`. This documentation slice does not duplicate that investigation or invent its result.

Repeated startup failures justify stopping unchanged retries. Next action is an explicit evidence-backed placement/startup strategy decision with applicable authority and unresolved choices, not GPU smoke, another unchanged submission or a throughput/science workaround. T02/T03 CPU readiness and configuration remain unchanged. D16/native profile/02 GPU, B and200-update native/profile acceptance remain pending; any future run needs its own attempt identity, fresh admission and actual startup/success evidence. Both failed attempts and all formal cloud outputs are protected, separate and outside smoke cleanup authority.

## B/full

Not submitted. Neither failed A produced an ACK or satisfies B admission. Placement/startup strategy is unresolved; B still requires a future actual A first successful update, completed D16 inspection andfresh36-H800 admission, not A200 completion orauxiliary profile PASS. Its TP4/EP1 Qwen3.5-35B-A3B teacher is feasibility-supported buthas no native H800 acceptance yet.

## Local record verification

### Historical first-submission verification

`python3 -B tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll`passes with31 documents,6 tickets,123 links,37 anchors and dependency order01→02→03→04→05→06. During status synchronization, the checker caught a temporary`04-a-full.md: blocked-by ['01', '02', '03'] != plan []`mismatch; the plan and ticket now both retain the satisfied CPU dependency IDs. No dependency or scientific requirement was removed. Scoped`git diff --check`passes. Admission/platform JSON identities, requested GPU sum36 and inspected worker GPU count12 were independently reconciled by the primary's Python reads.

### Historical first-failure/retry documentation and immutable evidence verification

System Python3.10.6; retained docchecker PASS:31 documents,6 tickets,135 links,39 anchors,zero errors andunchanged01→02→03→04→05→06 dependency order/arithmetic. Local parsing andidentity assertions PASS for exactlythe five approved JSONs linked in the failure/retry sections: oldjob/all five replicas terminal; full literal native error withfour configured nodes;6 successful queries/two ReadTimeouts/audit UNKNOWN; distinct retry job/UID/source/fresh admission and36 requested GPUs. Seven-owned-document plusfive-approved-JSON scoped whitespace PASS. Exact commands arein `progress.md`. JSON content isretained unchanged; other live/untracked evidence, Python/configs andticket05 areexcluded. No GPU/SSH/platform/network call, code/config fix orbusiness-test rerun occurred in this documentation slice. Read-only JSON/doc PASS doesnot close the RCA audit gap orprove actual retry GPU/engine/ACK/200-update acceptance.

### Second-failure documentation/evidence verification

System Python3.10.6; retained docchecker PASS:31 documents,6 tickets,139 links,40 anchors,zero errors,unchanged ticket DAG andarithmetic. Five selected new JSONs parse andidentity assertions PASS for retry job/UID,transitional versus final state,all five terminal replicas,rank3/scheduling times,literal error/four configured nodes/native timestamp,three events andRCA6/8/zero DeepScan/audit UNKNOWN. Seven-owned-document plusfive-approved-JSON scoped whitespace PASS. Exact local commands arein`progress.md`; JSON content isunchanged andother work/live/raw artifacts remain excluded. No code/config change,business-test rerun,platform/SSH/Lark/network/GPU operation,raw-cloud read oradditional delegation occurred. This documentation closure doesnot select a placement solution,approve another attempt orclose the UNKNOWN stop-audit gap.

## Completion criteria

For each cell, independently reconcile200 real successful updates and native terminal status; then validate200 paired profile updates, actual-bank observation totals, per-update consistency and complete rebuild. Preserve failed attempts separately, do not concatenate them, and do not clean live/formal evidence under the earlier smoke-only cleanup authorization.
