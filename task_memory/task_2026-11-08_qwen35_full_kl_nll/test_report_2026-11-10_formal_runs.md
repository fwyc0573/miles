## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Inspect first native worker receipts: rank0 eight H800 and ready teacher four H800; remaining ranks/engine startup unverified. |
| 2026-11-10 | Record A/full submission and exact platform identity/resource readback; first-update, B and terminal acceptance remain pending. |

# Formal A/B execution

## Configuration and prerequisites

The D35 consolidation is`55fba827`, per-turn CPU implementation is`6129aefe`, rollout/profile CPU integration is`15186817`, and explicit enabled formal configuration is`ec002ea8`. T02 and T03 each have Standards0/Spec0 reviews in[review.md](review.md). Launch code/config freeze HEAD:`606a9355`; no tracked changes under`miles/`, `tests/`or`scripts/`were present before submission. Task documents may progress independently.

Configuration:`formal_config.json`. Both cells use full mode,200 successful updates, H800/codesign,32 student/rollout GPUs plus4 teacher GPUs, source32×8, seq/context131072, prompt114688 inclusive and response16384. Profile is explicitly enabled with k10/B10/N8. See[the configuration and sample-lifecycle preparation report](test_report_2026-11-10_formal_configuration.md)for final dry-runs, real formal-driver/full-bank semantics and16 lifecycle checks. No additional profile GPU smoke was run.

## A/full — exp-1110-014836-849060

- Submitted2026-11-09T17:48:36Z (2026-11-10 01:48:36UTC+8). Local launcher shell handle:`sh_1c16d0f990014RQthEERNRrdWW`; kept alive for the workload. Log:`/data/ycfeng/tmp/agent-opd-image/formal-A-h800-112k-20261110.log`.
- Admission:[receipt](evidence/admission-formal-A-20261110.json). Fresh personal H800 non-preemptible inventory found0 committed GPUs for this creator before the36-GPU request; explicit ceiling isnull. This is not a claim that the shared cluster was empty or36 GPUs immediately available.
- Platform readback at17:49:29Z:[receipt](evidence/formal-A-submission-readback-20261110.json). Job UID`ccc4c4e4-3945-4159-8021-e0f0b17008f5`, creator`i-fengyicheng`, preemptible=false, task annotation matches this task, local source`100.96.128.195:/data/ycfeng:/data/ycfeng`.
- Observed status:`Starting`, reason`RJobStarting`, teacher active1 and student pending4. Platform resource requests are4×8 student GPUs plus1×4 teacher GPUs, positive tagH800. All four student replicas retain both RDMA limits. Requested placement is not yet worker`nvidia-smi`or engine readiness evidence.
- First successful optimizer ACK, actual GPU identity, per-turn/profile native consistency and terminal acceptance: **PENDING**. B is not yet submitted.
- Subsequent worker inspection: `student-node-0.json` confirms eight NVIDIA H800,81,559MiB each,driver570.124.06 on`gpu-h800-0180.host.platform.shaipower.com`; `teacher-ready.json` confirms four matching H800 and ready27B model endpoint. Both pin the configured image and model paths; selected fields are retained in[the startup receipt](evidence/formal-A-worker-startup-20261110.json). Student ranks1–3, all-engine readiness and first ACK are not yet verified. These are partial startup observations, not a claim that all36 devices or training are ready.
- A separate read-only first-update observer is running as local shell`sh_1c16ff2bb0017aVjX6GHz8NQ1s`. Once per60 seconds it reads only the first newline-complete native update and the two profile-file sizes from this exact training directory through the approved SSH cloud mount. It writes`evidence/formal-A-first-update-notification-20261110.json`and exits when a successful native record appears, prompting D16 inspection before B. Its observation window is9,000 seconds (three configured startup windows plus the configured request timeout); observer errors/timeouts do not stop or modify native training. This is a notification, not an auxiliary PASS gate or a replacement for native/profile inspection.

### Exact submission

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

## B/full

Not submitted. Waiting for A's first actual successful update plus completed D16 inspection and fresh36-H800 admission. Its TP4/EP1 Qwen3.5-35B-A3B teacher is feasibility-supported but has no native H800 acceptance yet.

## Local record verification

`python3 -B tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll`passes with31 documents,6 tickets,123 links,37 anchors and dependency order01→02→03→04→05→06. During status synchronization, the checker caught a temporary`04-a-full.md: blocked-by ['01', '02', '03'] != plan []`mismatch; the plan and ticket now both retain the satisfied CPU dependency IDs. No dependency or scientific requirement was removed. Scoped`git diff --check`passes. Admission/platform JSON identities, requested GPU sum36 and inspected worker GPU count12 were independently reconciled by the primary's Python reads.

## Completion criteria

For each cell, independently reconcile200 real successful updates and native terminal status; then validate200 paired profile updates, actual-bank observation totals, per-update consistency and complete rebuild. Preserve failed attempts separately, do not concatenate them, and do not clean live/formal evidence under the earlier smoke-only cleanup authorization.
