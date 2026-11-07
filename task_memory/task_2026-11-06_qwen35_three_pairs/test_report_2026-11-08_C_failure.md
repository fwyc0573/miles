## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Diagnose the D15/D16 C attempt's terminal CUDA OOM, qualify its actual baseline/restoration, and preserve zero-update accounting. |

# C D15/D16 attempt: failure and retained qualification

Task: `QWEN-P3-C-FAILURE`. Formal job: `exp-1107-150849-814926`, UID `bc1ea9ed-316c-40b0-8763-a65f63c4ba06`.

## Outcome

**Formal execution FAIL; baseline and same-version restoration PASS; successful optimizer updates in this attempt: 0.** The first train call fails inside the forward/backward schedule, before `optimizer.step()`. The old C attempt's one discarded update remains in history. No final HF artifact exists for this attempt. No replacement training job has been submitted.

This is a GPU output-projection allocation failure. The student host-memory request and limit were correctly increased to1500GiB; the recorded cgroup peak is408.7027702331543GiB with `oom_kill=0` and `failcnt=0`. This attempt does not reach the first optimizer step, so it cannot qualify that step's previously observed lazy host-state allocation.

## Terminal timeline and allocation

Times below are UTC; local platform display uses UTC+8.

| Event | Time / evidence |
| --- | --- |
| RJob created | 2026-11-07 07:08:49Z |
| Three replicas created | 19:32:17Z |
| Student container started | 19:39:08Z |
| Initial version0 publication | 20:04:32Z |
| Post-evaluation version0 restoration | 20:13:20Z |
| First train call, rollout0/attempt0 | 20:16:36Z |
| Train failure | 20:19:13Z |
| Student exit1 | 20:19:44Z |
| Job terminal Failed | 20:19:57Z |

The personal creator is `i-fengyicheng`, group `codesign`, non-preemptible. Student8H800 and teacher2×8H800 requests retain the pinned Miles image and local mount `100.96.128.195:/data/ycfeng:/data/ycfeng`. The student request/limit are both1500GiB. The critical student fails; the platform stops both noncritical teacher replicas with `Some critical tasks failed.` The old queue annotation still says zero quota, but it is historical scheduling metadata, not the terminal cause.

Primary receipt: [terminal platform snapshot](evidence/C-terminal-exp-1107-150849-814926-20261108.json). The monitoring shell raises when the already-running job becomes Failed; its exception is not the training failure's initiating cause. The original launcher's earlier disappearance remains unexplained.

## Direct failure evidence

The original student log is retained at:

```text
/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/C/exp-1107-150849-814926.log
/data/ycfeng/tmp/opencode-v2-tmp/opencode/C-exp-1107-150849-814926-complete.log
```

[Selected numbered trace](evidence/C-oom-trace-exp-1107-150849-814926.txt) preserves the actual traceback from original lines3913–4019:

```text
model.py:605 run_forward_backward_pass
schedules.py:790 forward_backward_no_pipelining -> forward_step
gpt_model.py:840 output_layer
linear_cross_entropy.py:41 super().forward
tensor_parallel/layers.py:514 torch.matmul(total_input, weight.t())
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 14.15 GiB.
```

The failing GPU2 has79.19GiB total and10.06GiB free. PyTorch allocated59.05GiB, including3.98MiB in private pools; reserved but unallocated is6.75GiB. The process reports67.36GiB total use and another process9925 uses1.72GiB. These are allocator error observations, not a complete live-storage attribution. Neither fragmentation nor the earlier B forward-only output-retention defect is established as this failure's cause by those numbers.

The rollout-side schedule explicitly records8 samples and3 microbatches. No exact failing tensor shape is inferred from the rounded14.15GiB request. Independent source/capacity analysis is recorded in [the capacity report](test_report_2026-11-08_C_gpu_capacity.md). The local copy of actual `rollout_data/0.pt` contains full-token lengths88244,89570,66714,60010,62063,63477,85708,85134. Its metadata does not save the consumed schedule. CPU replay of the existing scheduling/padding code predicts last microbatches `[2,5]` and `[4,3]`, with130560/122368 padded tokens; the predicted three-microbatch count matches native stdout. This is source replay, not a captured CUDA shape or independently observed rank ownership.

The same existing scheduler's fixed-singleton policy predicts four microbatches/rank and a maximum89600 padded tokens for this exact batch,31.37% lower than dynamic packing's maximum. All8 samples,600920 complete tokens and global batch8 remain. It does not reduce the allowed131072-token single-sample envelope or qualify100-step capacity. No flag has been changed. Exact inputs, schedules and limits: [first-batch geometry](evidence/C-first-batch-geometry.json).

### Optimizer budget

The sole train attempt is rollout0/attempt0. `miles/backends/megatron_utils/model.py:605–607` must finish the native forward/backward and gradient-finalization schedule before `optimizer.step()` at677–681. The observed traceback is inside that prerequisite. The native events contain only initial and restoration publications, both version0; no planned training publication or completed train-step record exists. DP gradient synchronization prevents a successful global step while this participant fails in forward/backward.

Thus this attempt adds0 successful optimizer updates, preserving the historical total of1 from the earlier discarded C attempt. The final-100-step inspector fields remain `null`: they are incomplete final-scope fields and are not rewritten as a per-attempt zero counter. [Native event summary](evidence/C-native-event-summary-exp-1107-150849-814926.json) counts every line of all13 source event files and retains the two original publication receipts. Cloud inspection finds only rollout0/eval0 artifacts, no HF directory and no completed TRAIN dump.

## Actual baseline and restoration verification

The pinned0-GPU inspector job `exp-1108-042419-168036` completed successfully; its [independent platform terminal receipt](evidence/C-failed-inspection-platform.json) confirms job and replicaSucceeded and0 requested GPUs. This is read-only inspection of saved outputs, not new model execution or an optimizer probe.

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Fixed monitoring population | 24 full samples | 24 samples,6308 original valid tokens | PASS |
| Decode mean absolute error | <=0.03 overall and all strata | Overall0.007153100504403866; all three strata pass | PASS |
| Same-token prefill mean absolute error | <=0.03 overall and all strata | Overall0.007055336848981543; all three strata pass | PASS |
| Missing/nonfinite eligible comparisons | 0 | 0 in both modes | PASS |
| Baseline TIS evidence | Original denominator retained | 6308/6308 measurable tokens retained | PASS |
| Native initial/restoration identity | Complete matching same-version receipts | Initial `09af4cbf8f0c472f8c51135a89c28de0`; restore `ba6c226b15f94b82b63778bca5c725ab`; both version0 | PASS |
| Full100-step run and final HF | Required for C completion | Missing after first train failure | INCOMPLETE |

The only publication issue is `native_publication_coverage_incomplete`; the completed initial/restoration chain has no provenance or same-version checksum issue. Full [inspector receipt](evidence/failed-inspection-C-exp-1107-150849-814926.json) is unchanged. [Compact result](evidence/C-failure-summary-exp-1107-150849-814926.json) preserves every stratum and explicitly states the update-count evidence boundary. Teacher probability semantics remain source/launch-derived, as in prior qualification.

## Commands and environment

Platform reads use personal StepMind Python on the local host, `STEPMIND_BACKEND=rjob`, `/data/ycfeng/tmp/stepmind-env/bin/python`, Python3.10.6 and brainpp2.8.6. `get_rjob_client().api.get_namespaced_custom_object(...)` reads the exact RJob/replica objects; each replica owner UID is checked. `get_rjob_infos(name)` and `logs_replica(..., tail_lines=2000)` collect selected terminal logs. Credential values are excluded from retained output.

The unchanged failure collector was run with:

```bash
timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
  exp-1107-150849-814926 \
  --replica exp-1107-150849-814926-student-cfcd2084 \
  --expected-creator i-fengyicheng \
  --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
  --start 2026-11-07T20:17:00Z --end 2026-11-07T20:20:30Z --timeout 20 \
  --output /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-C-exp-1107-150849-814926
```

Six event/log/deepscan queries succeed; both audit queries raise `ReadTimeout` after20seconds, so the collector exits1. The failure is retained rather than reported as complete audit coverage. The direct native traceback and terminal status establish the business failure independently. Empty or unavailable audit records do not establish absence of other events.

Saved-output verification used frozen `training_config.json`, the pinned image, Python3.12.16/torch2.14.1+cu130, cpu8/gpu0/mem_gb64, the configured mounts, `CUDA_VISIBLE_DEVICES=""`, `LD_LIBRARY_PATH=/usr/local/cuda-13.0/compat`, offline HF, `OMP_NUM_THREADS=1`, and worker-local `/var/tmp/qwen-c-inspect-$KUBEBRAIN_RJOB_NAME` caches. Submission cwd is `/data/ycfeng`, equal to `local_mount`. Native command:

```bash
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.inspect_qwen35 \
  --run-dir /mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/C/exp-1107-150849-814926 \
  --population-report /mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/population-exp-1106-233008-986003/population.json \
  --teacher-ready task_memory/task_2026-11-06_qwen35_three_pairs/evidence/first-round/exp-1107-150849-814926/C/teacher-ready.json \
  --report task_memory/task_2026-11-06_qwen35_three_pairs/evidence/failed-inspection-C-exp-1107-150849-814926.json
```

Expected whole-command success with an INCOMPLETE full-run verdict and independently assessed baseline; observed exit0/platformSucceeded, one PASS baseline and five missing later checkpoints. Parent recomputation of sample-weighted means matches both original overall values exactly.

## Independent failure review

Reviewer: `QWEN-P3-C-FAILURE-REVIEW`, session `ses_e484877aaffejleEfJo6PwFepQ`. Scope: this report, capacity report, plan/progress/summary/checkpoint, terminal and inspector receipts, node/student-finished records, native failure trace and optimizer/finalizer ordering. This was a read-only evidence/source review; no new runtime test or platform request was performed by the reviewer.

The reviewer supports the CUDA-vs-host diagnosis, zero-update accounting, baseline/restoration qualification and unchanged authorization boundaries. One P2 identified the old `progress.md` top-level Current state still claiming the earlier C job was Running. The parent replaces the current block with the latest status and preserves the entire previous block under an explicitly dated historical heading. A local comparison against HEAD verifies the previous block is unchanged within that historical section. Historical receipt contents are not rewritten. Exact captured CUDA geometry and GPU storage attribution remain outside this review's completed claims; the CPU schedule follow-up is separately qualified above.

Archival checks: parse all14 selected JSON files; verify Modification History and local Markdown links in all6 selected documents; compare the historical status block with `git show HEAD:task_memory/task_2026-11-06_qwen35_three_pairs/progress.md`; confirm the new Current state names the terminal job and contains no Running claim; verify the staged21-path set equals the explicitly selected task files; run `git diff --cached --check`. All checks PASS. The phase-review P2 is closed by this targeted correction; no additional runtime run is needed for a documentation-only state repair.

## Next decision and limits

The old queued-state frontier is superseded by this terminal failure. A/B qualification is unchanged. D15/D16 do not authorize an automatic further C restart, and D18's H200 migration covers A/B only. Any selected C topology/hardware change and replacement formal run need explicit authorization. Preserve the complete input population, model identities, numerical rules and historical budget while evaluating options. No production code, model math or launch flag has been changed by this diagnosis.

The source-backed choices are: retain24H800 and try the existing fixed-singleton policy, which lowers this batch's packing but leaves long-single-sample capacity unqualified; or authorize C on24H200 while retaining TP4/DP2, full inputs and1500GiB student host memory, subject to fresh quota/node-memory admission and the session's32-GPU non-preemptible ceiling. Larger GPU memory directly addresses the allocation limit without changing model math; it is still not a measured full100-step capacity guarantee. Recompute grouping and response-only projection remain separate, unselected proposals in the capacity report. No retry is implied by this list.
