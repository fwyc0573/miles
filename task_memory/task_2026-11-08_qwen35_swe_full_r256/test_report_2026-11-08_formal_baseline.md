## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Verify the formal baseline configuration and actual submission dry-run; record limited native evaluator readiness before admission. |

# Shared original4B formal baseline

## Preparation result

PASS for Ticket08-specific launch preparation, not for benchmark completion. Independent review is recorded in `review.md`. The fixed100 tasks, four seeds, original4B/version0 and native runtime/server/contract match the existing qualified configuration. No qualification subset is supplied. All source weights remain protected; a missing logical attempt keeps avg@4 null and recovery retains the original72h deadline.

The native Python3.10.20 builder command and configuration comparison are recorded in `test_report_2026-11-08_deepswe_configuration.md`, `evaluation_deepswe_formal_inputs.json` and `evidence/deepswe-formal-configuration-check.json`. Construction produced the new profile successfully. Observed differences from the previous formal profile are only personal output/ownership/dispatch paths and removal of the unused parser-validation label; runtime, server, evaluation contract, task IDs and allocation identity are identical.

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

Expected: submitted=false, exactly one two-GPU evaluation role, protected original source, pinned image/local mount and no qualification-attempt flags. Actual: exit0 and direct JSON assertions PASS: submitted=false,2 GPUs,1 replica,16 CPUs,128Gi request,is_critical=true, pinned image, original-source argument present and qualification flags absent. Fresh admission, worker GPU/source identity, attempted/completed/missing/failure counts, first-start/deadline and business/terminal outcomes remain pending actual execution.
