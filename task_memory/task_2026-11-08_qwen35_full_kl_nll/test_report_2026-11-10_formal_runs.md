## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record corrected H200 A/full submission, immutable fix reviews, actual18-GPU startup and bounded initial offload observation. |
| 2026-11-10 | Accept the actual first-update D16/Ticket02 checks; record subsequent Ray host-memory failure and1/200 incomplete formal result. |
| 2026-11-10 | Confirm all18 actual H200, teacher readiness, two-node Ray registration and first-bank acquisition; retain the nonblocking startup GC exception context separately from optimizer acceptance. |
| 2026-11-10 | Submit independent D37 H200 A after clean configuration review/fresh admission; all three replicas have assigned nodes, first ACK remains pending. |
| 2026-11-10 | Record the selected D36 waiting route and fresh personal inventory; distinguish personal admission from shared resource availability. |
| 2026-11-10 | Record SDK and authenticated platform-document findings for the pending placement decision; distinguish verified mechanisms from untested options and avoid treating a waiting-time upper bound as measured GPU cost. |
| 2026-11-10 | Close the second pre-training A failure with five complete receipts; pause submissions at PLACEMENT_BLOCKED pending a strategy decision, without claiming complete stop-audit closure. |
| 2026-11-10 | Record first A terminal/native failure and incomplete stop audit; retain snapshots and separately document unchanged freshly admitted retry and read-only observer replacement. |
| 2026-11-10 | Diagnose partial placement from exact replica/Pod events and separate Ray startup deadline from acquisition/D19. |
| 2026-11-10 | Inspect first native worker receipts: rank0 eight H800 and ready teacher four H800; remaining ranks/engine startup unverified. |
| 2026-11-10 | Record A/full submission and exact platform identity/resource readback; first-update, B and terminal acceptance remain pending. |

# Formal A/B execution

## Historical H800 configuration and prerequisites

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

### Historical D36 route — PLACEMENT_BLOCKED

Both formal A attempts failed before acquisition/training with0 updates. **D36 selected keeping the accepted36-H800 configuration and waiting for improved placement conditions; D37 subsequently authorized the H200 switch below.** At the D36 snapshot there was no third attempt. The local SDK investigation `profile-placement-route-20261110` (`ses_e3e4c91c2ffeH93O77e3RX5SB1`) and authenticated document reads below are complete. These are historical route records, not the current H200 job state.

Repeated startup failures justify stopping speculative unchanged retries. Under D36, recheck resource indicators and resume with a separate attempt when conditions improve. T02/T03 CPU readiness and configuration remain unchanged. D16/native profile/02 GPU, B and200-update native/profile acceptance remain pending; any future run needs its own attempt identity, fresh admission and actual startup/success evidence. Both failed attempts and all formal cloud outputs are protected, separate and outside smoke cleanup authority.

### Placement options and verified limits

- Local SDK `brainpp/rjob/struct.py:1208,1231,1437-1438` defines `gang_group` for tasks with `gang_start=True`. The existing submission already carries the group label while both tasks disable gang start. That label alone did not prevent partial placement. The local SDK has no separately exposed all-or-none allocation field; exact PodGroup/controller behavior remains unverified.
- `Task.gang_start` is distinct from application readiness. The handbook's server-admission experiment showed that enabling it on the student can inject a teacher ConfigMap reference too, despite disabling it on the teacher. A previous job failed on the absent teacher ConfigMap. Blindly enabling it is not an accepted repair.
- Existing `RJobWorkers.get_all_ips()` delegates to a default-task helper (`stepmind_control.py:264-300,367-369`). Its default task name and root replica count do not match this two-task/four-student configuration, so it cannot be used unchanged as a placement barrier. A new launcher-side coordinator could use the existing personal client without giving credentials to workers, but its release/cancellation/waiting policy would need design and verification. Delaying application startup can avoid spending the application deadline during placement; it cannot create the missing physical resources and may prolong partial GPU occupation.
- The authenticated [scheduler guide](https://wvixbzgc0u7.feishu.cn/wiki/LvJ8wKacWi4AyakWVPYccszVnVf), document `Ppr9dqgL4o5OyBxJkHpcVYnEnic` revision3, distinguishes resource shortage and missing PodGroup from workload failure. The [multi-task investigation](https://wvixbzgc0u7.feishu.cn/wiki/NpOWwvm5NiIecnk3YExc2qhnnQg), document `MJz1dpkhaoKBmZxyhU6cYA8Hnkb` revision689, reports multi-task gang-start problems and leaves cross-task support unresolved. These documents support the diagnosis and the need to verify platform behavior; they do not prove a working atomic-placement configuration.
- Full successful JSON responses are retained at `/data/ycfeng/tmp/agent-opd-image/formal-scheduling-doc-20261110.json` and `formal-multitask-doc-20261110.json`. Exact reads used `/data/ycfeng/stepcode-codex-home/bin/lark-cli docs +fetch --as user --doc <linked-url> --scope keyword --keyword 'gang|group|调度' --context-after 1 --doc-format markdown` for the scheduler guide; the multi-task keyword was `gang|group|同时|调度`. Both returned `ok=true`; local response parsing confirmed document IDs and revisions. No external write was performed.

Options presented before D36 were: keep the accepted 36-GPU configuration and await a better placement opportunity; validate native gang-start/teacher ConfigMap behavior before another launch; or explicitly reduce to three student nodes plus the teacher (28 GPUs, six TP4 rollout engines), whose acquisition throughput is unverified. The user selected the first option. The alternatives have not been applied. The 1800-second acquisition and 600-second weight-sync deadlines remain unchanged.

Cost boundary: both attempts had staggered replica starts. Multiplying 28 GPUs by the entire job lifetime is only an upper bound, not measured allocation time or billed GPU-hours. No measured 33-GPU-hour claim is made. Any longer placement wait would retain already allocated workers until the missing resources arrive or the attempt is canceled.

Local route-record verification: `python3 -B tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll` passed with31 documents,141 links,42 anchors andzero errors. Scoped `git diff --check` passed for this report, progress and summary. No runtime code/config change or GPU test accompanied this assessment.

### D36 resource recheck — 2026-11-10T05:26Z

The user selected **保持36卡等待 (Recommended)** after the interrupted question was asked again. The exact Q/A is in requirements D36. The config remains four eight-H800 student replicas and one four-H800 teacher, non-preemptible, with gang start disabled. There is no new queue membership or application-startup evidence.

The [fresh personal inventory](evidence/formal-D36-personal-inventory-20261110.json), observed at05:26:04.168821Z, records no nonterminal H800 jobs for `i-fengyicheng`, committed0, requested36, personal ceilingnull and `admitted=true`. This was a direct read of `policy_admission_snapshot`, **not a submission**; `submitted=false`. These values establish the local personal policy allowance, not shared codesign headroom, available GPU nodes or atomic placement. Further read-only resource indicators are being checked before deciding whether conditions have improved.

Exact inspection entry: from `/data/ycfeng`, initialize the handbook personal/proxy environment, set `PYTHONPATH` to this Miles worktree followed by `/data/ycfeng/steptron`, then run `timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -B -`. Import `tests.manual.agent_opd.rjob_budget.policy_admission_snapshot` before `steptron.utils.stepmind.get_rjob_client`; load the existing formal config/policy and call `policy_admission_snapshot(client, policy=policy, creator=config['creator'], gpu_tag=config['gpu_tag'], requested_gpus=36, timeout=config['api_timeout_seconds'])`. Save only the filtered snapshot with `submitted=False`; do not call the backend submitter.

The initial one-off script imported Steptron first and failed before any API call with `ModuleNotFoundError: No module named 'tests.manual'`. A bounded `find_spec('tests')` check showed why: `steptron/__init__.py:10-17` prepends third-party trees, changing the selected package from this worktree's `tests/__init__.py` to `steptron/third_party/super_agent/tests/__init__.py`. Matching the existing submitter's Miles-first import order fixed this inspection; no repository code, config or environment installation changed. The corrected read above passed and produced the saved snapshot.

## B/full

Not submitted. B uses D37's H200 configuration,18GPUs/TP2 teacher. The actual first-A-update and completed D16 inspection requirements are now satisfied by the H200 attempt below. The subsequent native host-memory failure requires resolution before another affected run, and B still needs fresh admission. Two18-GPU cells exceed32 non-preemptible GPUs; resource sequencing does not add an A200 or profile-PASS gate. Both zero-update H800 failures remain separate.

## D37 H200 A/full — exp-1110-140032-491115 — FAILED after1 successful update

- Submitted2026-11-10T06:00:32Z (14:00:32UTC+8) through the existing local StepMind Python backend. Config/policy freeze:`d822174c`; candidate `formal_h200_config.json`. Fixed-diff prelaunch review `profile-h200-prelaunch-review-20261110` returned Standards/Spec **No findings**. Four CPU dry-runs, unchanged science, selected runtime diff and retained lifecycle evidence are recorded in[the configuration report](test_report_2026-11-10_formal_configuration.md#d37-h200-configuration-preparation).
- Fresh locked[admission](evidence/admission-formal-H200-A-20261110.json) at06:00:32.480291Z found2 committed H200, requested18, ceiling32, personal/admitted/submitted=true andpreemptible=false. Local source remains`100.96.128.195:/data/ycfeng:/data/ycfeng`. No unrelated job was stopped.
- Exact personal API[readback](evidence/formal-H200-A-submission-readback-20261110.json) at06:02:27.594704Z confirms creator`i-fengyicheng`, quota group`step_main`, non-preemptible and18 requested H200. All three replicas have `PodScheduled=True`: student0 on`gpu-h200-1192`Running, student1 on`gpu-h200-0057`Starting/ContainerCreating, teacher on`gpu-h200-0638`Running. The overall job remainsStarting. This confirms assignment for this attempt, not yet workerGPU/engine or first-update acceptance.
- Historical local launcher handle:`sh_1c40b2942001YJhTv6Bmxynsk5`; log:`/data/ycfeng/tmp/agent-opd-image/formal-H200-A-20261110.log`. It stayed alive during the workload and subsequently exited1. Exact invocation below used the same environment/interpreters/auth initialization documented above, from`/data/ycfeng`.

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_swe_opd --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/formal_h200_config.json --pair A --protocol full --receipt /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/admission-formal-H200-A-20261110.json > /data/ycfeng/tmp/agent-opd-image/formal-H200-A-20261110.log 2>&1
```

- Worker/local receipts:`evidence/formal-h200-112k-20261110/full/exp-1110-140032-491115/A/` and`full/student/A/exp-1110-140032-491115/`under that evidence root. Durable training:`/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/formal-h200-112k-20261110/full/student/A/exp-1110-140032-491115/training/`; profile remains paired`distillation_profile/{updates,observations}.jsonl`there.
- Read-only first-success/failure observer:`sh_1c40dff21001XSU7n1f5m5jH3g`, using the existing60-second check and config-derived9,000-second observation window. It checks retained native failure plus successful ACK, writes`evidence/formal-H200-A-first-update-notification-20261110.json`only on success, andcannot stop orchange the GPU job. Observer failures are auxiliary, not native failure.
- First native ACK and D16/02 GPU consistency are now **PASS**; the verified first update remains independent of both H800 failures. The attempt failed afterward, so200-update native/profile acceptance remains incomplete. See the[first-update report](test_report_2026-11-10_d16_first_update.md). Offline tools were subsequently repaired at`24e8386f`/`d0f67887`; the[combined CLI check](test_report_2026-11-10_offline_report_integration.md) includes post-repair synthetic/retained checks and separately links actual first-update evidence.

### Actual H200 startup and first bank

The[worker startup receipt](evidence/formal-H200-A-worker-startup-20261110.json) joins the two student node receipts, teacher-ready receipt and Ray cluster receipt for this exact job. It confirms18 actual H200 devices, ready27B teacher and two alive Ray nodes with16 student/rollout GPUs. These observations supersede the earlier container-creation snapshot without changing its historical status. They do not prove a successful optimizer update.

A bounded read of the rank0 cloud log at06:14:35Z retained[pre-acquisition startup context](evidence/formal-H200-A-initial-sync-20261110.json). Despite that receipt's filename, its captured engine-loading lines do not establish initial weight-sync duration. The later06:17:12Z[log and bank snapshot](evidence/formal-H200-A-startup-context-20261110.json) establishes `acquisition_start` at1794291296.7750304 (2026-11-10T06:14:56.775030Z), deadline1794293096.775094 and256 candidate slots. The same snapshot contains successful generation attempts and HTTP200 generation responses; final valid count, collection duration and first ACK remain unverified at this snapshot.

The log shows a `/freeze_gc` connection rejection in pinned SGLang `_freeze_gc_after_server_warmup`, followed by server readiness, another successful freeze-GC response, and later successful generation. Thus the captured exception did not prevent this run from entering acquisition. No GC, timeout, network or training behavior was changed, and no job was stopped over this auxiliary startup observation.

These are direct reads of the existing local worker receipts and the exact personal cloud log/bank, using `ssh shai-ycfeng` only as `i-fengyicheng`. Cloud input files were not changed. The rank0 log read was limited to its final2MiB; the bank read selected only its first complete record and candidate count. Evidence parsing uses complete newline-terminated JSON records.

### First update accepted; subsequent native host-memory failure

The[first-update verification](evidence/d16-H200-A-20261110/first-update-verification.json) confirms256 valid turns acquired in529.280799s, no missing/pending slots, one unskipped native ACK,37,628 original tokens and exact canonical UID/mask binding. The paired profile contains256 observations across32 conversations; RKL0.09019820589424715 and NLL0.5315250028328384 exactly match the native record, and offline rebuild reproduces its summary. Stage times and the manual ordinal-check correction are recorded in[the D16 report](test_report_2026-11-10_d16_first_update.md).

After the successful training outcomes, Ray's host-memory monitor killed a trainer worker during post-update offload. The job finished Failed at06:29:33Z; the[06:39:22Z terminal readback](evidence/formal-H200-A-terminal-readback-20261110.json) confirms all three replicas terminal. The formal result is1/200, not COMPLETE; no second bank was present in the captured snapshot. The underlying memory-retention cause is being diagnosed before another affected launch. Six RCA queries succeeded; both audit reads failed, leaving audited stop actor/time UNKNOWN. All formal cloud outputs remain protected.

## Corrected H200 A/full — exp-1110-165312-132926 — EXECUTING

### Preparation and exact submission

The D38 controlled diagnostic is accepted in`9b56d69a`; production correction`edd3be00`and test naming follow-up`d2b3af8c`have18 CPU PASS/20 SKIP (missing Megatron) and completed[Standards0/Spec0 review](review.md#optimizer-initialization-phase-review--2026-11-10). Corrected native formal behavior remains to be measured. The historical failed full-model allocation owner is still unknown.

The selected `formal_h200_config.json` continues to request18H200/step_main,TP2/DP4 trainer,eightTP2 rollout engines,27B TP2 teacher,full200 updates,32×8 input,D34 length budgets and profile10/10/8. The previous16-case sample-lifecycle evidence is reused: a diff from`ec002ea8`shows no selected source/replay/training/TIS/launcher changes, and the only runtime changes are the two reviewed Megatron modules. Immediately before launch, the runtime/config diff against`d2b3af8c0984cac09ca97765a8be294a8e46d9f9`passed before the submission command was reached.

Local submission used `/data/ycfeng`,Python3.10.6/brainpp2.8.6, `STEPMIND_BACKEND=rjob`, `PYTHONPATH=<repo>:/data/ycfeng/steptron`, existing personal auth and handbook proxy initialization. Exact entry:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_swe_opd --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/formal_h200_config.json --pair A --protocol full --receipt /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/admission-formal-H200-A-r2-20261110.json > /data/ycfeng/tmp/agent-opd-image/formal-H200-A-r2-20261110.log 2>&1
```

[Preflight inventory](evidence/formal-H200-A-r2-resource-preflight-20261110.json)at08:47:54Z was2+18≤32. The real[locked admission](evidence/admission-formal-H200-A-r2-20261110.json)at08:53:12.122165Z correctly re-read10 committed +18 requested≤32, non-preemptible, creator`i-fengyicheng`,submitted=true. Local source:`100.96.128.195:/data/ycfeng:/data/ycfeng`. Launcher`sh_1c4a93c91001D1z45VYtwEYn2M`remains active throughout the run.

### Startup observations

- The[08:55:43Z API snapshot](evidence/formal-H200-A-r2-startup-readback-20261110.json)was Starting, with two Running replicas and one Starting replica, all with assigned addresses.
- Subsequent[worker/API verification](evidence/formal-H200-A-r2-worker-startup-20261110.json)confirms all three Running,exact imageIDs,restart0,matching local mounts and18 actual H200 devices. Student nodes are`gpu-h200-0024`and`gpu-h200-0882`,eight cards each; the teacher has two. The teacher-ready receipt and two-node16GPU Ray cluster are present.
- The[09:09:38Z snapshot](evidence/formal-H200-A-r2-startup-context-20261110.json)retains at most the final2MiB of the exact rank0 log plus selected complete bank/native records. Initial trainer offload returned around09:08:41Z. Shown before-offload readings are17.66GiB allocated and17.71GiB reserved; after-offload driver-reported device usage is2.43GiB on the shown ranks. These readings describe initial state handling, not the former post-update failure point or a host-memory peak.
- At that snapshot,bank0 and native ACKs were not present; the controller was waiting for four remaining colocated engines. `freeze_gc`connection-refused tracebacks were followed by server-ready messages, as in the earlier H200 startup. Serving-time Triton compilation and detokenizer heartbeat warnings remain startup observations, not an accepted first-sync/acquisition result.

Durable run directory:`/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/formal-h200-112k-20261110/full/student/A/exp-1110-165312-132926`; native/profile records are under`training/`. The rank0 log is its sibling`exp-1110-165312-132926-rank-0.log`. Local worker records are under`evidence/formal-h200-112k-20261110/full/exp-1110-165312-132926/A/`, with run/cluster/preflight records under`full/student/A/exp-1110-165312-132926/`.

The read-only second-update-or-failure observer`sh_1c4b06aab001hJGPq4T0kNXC9q`uses60-second checks and the existing config-derived9000-second window, then writes`evidence/formal-H200-A-r2-second-update-notification-20261110.json`. It reads only this run through`shai-ycfeng`as`i-fengyicheng`. Its errors are auxiliary; it has no RJob control path. Pending: actual successful updates, post-update offload/weight update/next train, host-memory and native terminal evidence, plus200-update/profile completeness. The old1/200 record is not concatenated with this attempt.

## Local record verification

### Historical first-submission verification

`python3 -B tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll`passes with31 documents,6 tickets,123 links,37 anchors and dependency order01→02→03→04→05→06. During status synchronization, the checker caught a temporary`04-a-full.md: blocked-by ['01', '02', '03'] != plan []`mismatch; the plan and ticket now both retain the satisfied CPU dependency IDs. No dependency or scientific requirement was removed. Scoped`git diff --check`passes. Admission/platform JSON identities, requested GPU sum36 and inspected worker GPU count12 were independently reconciled by the primary's Python reads.

### Historical first-failure/retry documentation and immutable evidence verification

System Python3.10.6; retained docchecker PASS:31 documents,6 tickets,135 links,39 anchors,zero errors andunchanged01→02→03→04→05→06 dependency order/arithmetic. Local parsing andidentity assertions PASS for exactlythe five approved JSONs linked in the failure/retry sections: oldjob/all five replicas terminal; full literal native error withfour configured nodes;6 successful queries/two ReadTimeouts/audit UNKNOWN; distinct retry job/UID/source/fresh admission and36 requested GPUs. Seven-owned-document plusfive-approved-JSON scoped whitespace PASS. Exact commands arein `progress.md`. JSON content isretained unchanged; other live/untracked evidence, Python/configs andticket05 areexcluded. No GPU/SSH/platform/network call, code/config fix orbusiness-test rerun occurred in this documentation slice. Read-only JSON/doc PASS doesnot close the RCA audit gap orprove actual retry GPU/engine/ACK/200-update acceptance.

### Second-failure documentation/evidence verification

System Python3.10.6; retained docchecker PASS:31 documents,6 tickets,139 links,40 anchors,zero errors,unchanged ticket DAG andarithmetic. Five selected new JSONs parse andidentity assertions PASS for retry job/UID,transitional versus final state,all five terminal replicas,rank3/scheduling times,literal error/four configured nodes/native timestamp,three events andRCA6/8/zero DeepScan/audit UNKNOWN. Seven-owned-document plusfive-approved-JSON scoped whitespace PASS. Exact local commands arein`progress.md`; JSON content isunchanged andother work/live/raw artifacts remain excluded. No code/config change,business-test rerun,platform/SSH/Lark/network/GPU operation,raw-cloud read oradditional delegation occurred. This documentation closure doesnot select a placement solution,approve another attempt orclose the UNKNOWN stop-audit gap.

### Corrected H200 startup metadata verification

Primary local verification (Python3.10.6): **PASS** for10+18≤32 admission,three Running/image/mount/restart identities,18 actual H200,exact reviewed diff,current runtime/config unchanged,and13 retained files parsed/scanned with zero credential-value/private-key matches. This verifies the captured startup records, not later runtime completion. Exact command:

```bash
python3 -B - <<'PY'
import json,subprocess
from pathlib import Path
root=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll');e=root/'evidence';cfg=json.loads((root/'formal_h200_config.json').read_text());a=json.loads((e/'admission-formal-H200-A-r2-20261110.json').read_text());w=json.loads((e/'formal-H200-A-r2-worker-startup-20261110.json').read_text())
assert a['job']==w['job']=='exp-1110-165312-132926'
assert (a['committed_gpus'],a['requested_gpus'],a['ceiling_gpus'])==(10,18,32)
assert a['submitted'] and a['admitted'] and not a['preemptible'] and a['creator']=='i-fengyicheng'
assert len(w['replicas'])==3 and sum(len(v['gpu_devices']) for v in w['nodes'].values())==18
for replica in w['replicas'].values():
 assert replica['phase']=='Running' and replica['source_mount']==a['source_mount']
 for container in replica['containers']:
  assert container['imageID']==cfg['image'] and container['restartCount']==0 and 'running' in container['state']
for node in w['nodes'].values():
 assert node['job']==a['job'] and node['image']==cfg['image'] and all('H200' in value for value in node['gpu_devices'])
review=e/'optimizer-init-review-20261110';base='9b56d69ae23745a9e4a703ce50bccbf02594a13d';tip='d2b3af8c0984cac09ca97765a8be294a8e46d9f9'
assert (review/'revised.diff').read_bytes()==subprocess.check_output(['git','diff',base+'...'+tip])
assert not subprocess.check_output(['git','diff',tip,'--','miles','tests/manual/agent_opd',str(root/'formal_h200_config.json'),str(root/'h200_gpu_policy.json')])
files=list(review.iterdir())+[e/name for name in ('admission-formal-H200-A-r2-20261110.json','formal-H200-A-r2-resource-preflight-20261110.json','formal-H200-A-r2-startup-readback-20261110.json','formal-H200-A-r2-worker-startup-20261110.json','formal-H200-A-r2-startup-context-20261110.json')]
for path in files:
 content=path.read_text()
 if path.suffix=='.json':json.loads(content)
 for key in ('accesskey_id','accesskey_secret'):
  secret=(Path('/data/ycfeng/tmp/brainctl-auth-i-fengyicheng')/key).read_text().strip();assert secret not in content
 assert '-----BEGIN PRIVATE KEY-----' not in content
print('PASS: admission 10+18<=32; 3 running/image/mount/restart identities; 18 actual H200; exact immutable diff; runtime/config unchanged; '+str(len(files))+' retained files parsed/scanned.')
PY
```

Scoped whitespace check also passed:

```bash
git diff --check -- task_memory/task_2026-11-08_qwen35_full_kl_nll/progress.md task_memory/task_2026-11-08_qwen35_full_kl_nll/review.md task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-10_formal_runs.md
```

The final combined document check after`2f1df5da`and primary updates passed:39 documents,6 tickets,230 links,58 anchors,zero errors;51,200/102,400 turn arithmetic and81-turn trend threshold unchanged. Its initial run exposed an incorrect`a-full`anchor and a concurrent plan/ticket dependency-description mismatch; both were corrected before this PASS. The records agent separately verified17 unchanged acceptance checkbox rows and raw/history preservation across its five-file commit. Exact checker:

```bash
python3 -B tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll
```

## Completion criteria

For each cell, independently reconcile200 real successful updates and native terminal status; then validate200 paired profile updates, actual-bank observation totals, per-update consistency and complete rebuild. Preserve failed attempts separately, do not concatenate them, and do not clean live/formal evidence under the earlier smoke-only cleanup authorization.
