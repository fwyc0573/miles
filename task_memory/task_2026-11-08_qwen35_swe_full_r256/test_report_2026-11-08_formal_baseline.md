## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Submit the formal400-attempt point and verify actual platform creator,task annotation,local source,two-GPU request and non-preemptible admission. |
| 2026-11-08 | Verify the formal baseline configuration and actual submission dry-run; record limited native evaluator readiness before admission. |

# Shared original4B formal baseline

## Preparation result

PASS for Ticket08-specific launch preparation, not for benchmark completion. Independent review is recorded in `review.md`. The fixed100 tasks, four seeds, original4B/version0 and native runtime/server/contract match the existing qualified configuration. No qualification subset is supplied. All source weights remain protected; a missing logical attempt keeps avg@4 null and recovery retains the original72h deadline.

The native Python3.10.20 builder used the existing mounted runtime and native import paths, with offline model access and empty CUDA_VISIBLE_DEVICES. Exact module invocation:

```bash
/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/.venv/br-native-swe-py310-1008am/environment/bin/python \
  -B -m tests.manual.agent_opd.swe_evaluation_config \
  --inputs /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evaluation_deepswe_formal_inputs.json \
  --output /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evaluation_deepswe_formal_config.json
```

Construction log: `/data/ycfeng/tmp/qwen35-swe-deepswe-formal-config-20261108.log`, exit0. The configuration comparison is in `evidence/deepswe-formal-configuration-check.json`. Observed differences from the previous formal profile are only personal output/ownership/dispatch paths and removal of the unused parser-validation label; runtime, server, evaluation contract, task IDs and allocation identity are identical.

## Actual submitter dry-run

Environment: local Python3.10.6, existing `/data/ycfeng/tmp/stepmind-env`, cwd `/data/ycfeng`. No GPU allocation or external API call occurs in this dry-run.

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron TMPDIR=/data/ycfeng/tmp \
  /data/ycfeng/tmp/stepmind-env/bin/python -B -m tests.manual.agent_opd.submit_swe_evaluation \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_integration_config.json \
  --configuration /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evaluation_deepswe_formal_config.json \
  --point original4b \
  --receipt /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/admission-eval-original4b-formal-20261108.json \
  --original-source /mnt/codesign-exp/ycfeng/opd-assets/models/Qwen/Qwen3.5-4B/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a \
  --dry-run > /data/ycfeng/tmp/qwen35-swe-original4b-formal-dry-run-20261108.log 2>&1
```

Expected: submitted=false, exactly one two-GPU evaluation role, protected original source, pinned image/local mount and no qualification-attempt flags. Actual: exit0 and direct JSON assertions PASS: submitted=false,2 GPUs,1 replica,cpu=16,mem_gb=128,is_critical=true, pinned image, original-source argument present and qualification flags absent. Fresh admission, worker GPU/source identity, attempted/completed/missing/failure counts, first-start/deadline and business/terminal outcomes remain pending actual execution.

## Actual admission and platform identity

Executed the dry-run command above without `--dry-run`, under the existing handbook personal-auth/proxy environment with `STEPMIND_BACKEND=rjob`, from `/data/ycfeng`. Private router/ACS credentials were inherited only in process/worker environment. Launcher log: `/data/ycfeng/tmp/qwen35-swe-original4b-formal-20261108.log`; background shell `sh_1bb6e4947001CA6TfspqgYYhKk` keeps the native backend alive.

PASS: receipt `evidence/admission-eval-original4b-formal-20261108.json` records job `exp-1108-215214-032806`, fresh admission13:52:14UTC,0 previous task commitments+2 requested GPUs, ceiling64, admitted=true and preemptible=false. Exact-job local Python client readback13:53:27UTC verifies creator `i-fengyicheng`, task annotation, `preemptible=no`,1 replica and2 GPU requests/limits. Local NFS source is `100.96.128.195:/data/ycfeng:/data/ycfeng`. Selected evidence is in `evidence/platform-eval-original4b-formal-20261108.json`; query log `/data/ycfeng/tmp/qwen35-swe-original4b-formal-platform-20261108.log`.

Observed platform phase: Starting. This proves admission and resource identity, not worker GPU startup, model reload, sample execution or benchmark completion. Actual model/version,400-attempt counts, absolute deadline and terminal state remain pending.

Later startup inspection (`evidence/original4b-formal-worker-readback-20261108.json`) observes Running with replica `exp-1108-215214-032806-cfcd2084`; replica log API returns0 rows. The expected personal cloud point was not visible through the bounded shai-ycfeng read at that observation (`evidence/original4b-formal-startup-20261108.json`). These observations establish neither model readiness nor a failed workload, and do not justify resubmission. Native readiness and formal counts remain pending.
