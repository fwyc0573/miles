## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Archive completed A/B H200 qualification; retain C and the three-pair aggregate as unfinished. |

# Qwen3.5 pair qualification — A/B completion archive

## Status and scope

**A and B are complete within the approved temporary-colocation scope. The full three-pair task remains in progress because C is queued on H800.** Implementation and runtime qualification are in Miles. Dense-student routing replay is N/A under D2; the measured colocated transport is native CUDA IPC. Original NCCL-direct qualification remains deferred under D5 and is not claimed by these results.

| Pair | Student / frozen teacher | Accepted formal run | Successful / skipped updates | Numerical monitoring | Final text-HF |
| --- | --- | --- | --- | --- | --- |
| A | Qwen3.5-4B / Qwen3.5-27B | `exp-1107-173758-712234` | 100 / 0 | All six checkpoints PASS | PASS, reload`exp-1107-213721-009840` |
| B | Qwen3.5-4B / Qwen3.5-35B-A3B | `exp-1107-173758-806531` | 100 / 0 | All six checkpoints PASS | PASS, reload`exp-1107-211800-115424` |
| C | Qwen3.5-27B / Qwen3.5-397B-A17B | `exp-1107-150849-814926` | New run not started | Pending | Pending |

A uses its original100-update budget. B uses the explicit D17 fresh100 authorization; one earlier discarded successful update remains in history, giving101 historical B updates. Restorations do not count as optimizer updates. A/B training RJobs finishStopped because the critical student succeeded and the noncritical teacher was then stopped; business receipts and native counter/publication chains independently establish successful completion.

The frozen H200 manifest is `training_config_h200.json`; each formal pair uses8 student +2 teacher H200s,20 total. Final reloads each use2 H200s and do not execute optimizer steps. All allocations stay within the session/task ceiling of32 non-preemptible H200 GPUs. Actual hardware, personal creator, image, source mount and terminal states are archived.

## Observed validation results

- **D8:** every checkpoint has24 fixed monitoring completions,8 per short/medium/long stratum, using original pre-TIS valid-token denominators. Decode and same-token prefill are checked separately; all populated means meet the unchanged0.03 bound. Missing/nonfinite comparisons, tails, K3 directions and provenance remain in the full receipts.
- **Final A:**5197 finite valid tokens; decode mean absolute difference0.0086628771, native/reloaded prefill0.0084664004.
- **Final B:**4261 finite valid tokens; decode0.0068720590, native/reloaded prefill0.0068017697.
- **Each final HF:** planned rollout99/version100 binding,822 eligible decoder checksum entries exactly equal before/after inference, all24 untruncated inputs, compatible text configuration/tokenizer, real text generation, native cleanup and whole-command platformSucceeded. The package is426 tensors:402BF16/24F32, with the required A_log tensorsFP32. No native model/optimizer checkpoint is delivered.
- **Training behavior:** each pair provides100 finite, native-counter-bound loss and pre-clipping gradient-norm points plus recorded LR/clipping/TIS metrics. Comparing successful updates1–20 with81–100, mean loss changes A0.090480→0.091233 and B0.095032→0.094511. These noisy, fresh-completion observations do **not establish convergence or capability improvement**. Gradient clipping is inferred from the recorded norm/threshold, not a measured post-clipping norm. Exact per-step original-mask/post-TIS counts and independent distributed-normalization replay are not claimed.
- **Review:** B's initial missing actual-curve and terminal-receipt findings were repaired and closed; A's independent final review found no actionable issue. See `review_final_pairs.md`.

## Deliverables

Accepted, retained text-HF packages:

```text
/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/A/exp-1107-173758-712234/hf/step_99
/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/B/exp-1107-173758-806531/hf/step_99
```

Each enumerated package is8,434,495,085 bytes. Immutable packaging metadata remains`reload_verified:false`; the independent final validator receipts record`reload_verified:true` and own acceptance.

Local paths, relative to this task directory:

- `test_report_2026-11-07_training.md`: actual terminal states, budgets, numerical checkpoints and exact inspector commands.
- `test_report_2026-11-07_hf_reload.md`: exact native reload commands, content/numerical/generation/cleanup results and platform evidence.
- `test_report_2026-11-07_A_training_curves.md`, `test_report_2026-11-07_training_plot.md`, `test_report_2026-11-07_B_monitoring.md`: per-step and fixed-monitoring behavior, windows and evidence limits.
- `evidence/AB-training-curves.png`: combined four-panel actual loss/gradient plot; `evidence/{A,B}-training-curves.png` and `{A,B}-training-steps.{json,md}` retain individual plots and full records.
- `evidence/completion-inspection-A-exp-1107-173758-712234-2132.json`, `evidence/completion-inspection-B-exp-1107-173758-806531-2102.json`: complete native acceptance receipts.
- `evidence/final-hf-reload-A-exp-1107-173758-712234-exp-1107-213721-009840.json`, `evidence/final-hf-reload-B-exp-1107-173758-806531-exp-1107-211800-115424.json`: full independent final-HF receipts. Matching logs and per-pair terminal/hardware receipts are retained alongside them.

## Remaining and deferred work

1. C remainsPending: [13:58:46Z frontier receipt](evidence/C-frontier-after-AB.json) verifies H800 queue availability0 against24 requested; its owning local launcher remains alive. D15 permits the new100-step run and D16 sets the student limit to1500GiB, confirmed in the platform request/limit. Actual allocation, memory peak, restored scoring,100 updates, curves and final HF all remain unverified for C.
2. P4's three-pair aggregate cannot close before C. No additional optimizer probe, budget extension or automatic restart is authorized.
3. Scoped OSS cleanup removed15.668GiB of obsolete failed-probe shards. Post-training inventory confirms33.66GiB retained, both accepted final packages intact and no newly eligible obsolete files; this follow-up deletes0 bytes. Physical quota reclamation remains independently unverified; accepted final artifacts and irreplaceable evidence are protected. See `test_report_2026-11-07_oss_cleanup.md` and its unchanged original deletion records plus appended post-training inventory.
4. Optional pinned Megatron forward-only output-retention work and parameter-rematerialization recovery remain deferred in `future.md`; neither is represented as repaired by H200 capacity. NCCL-direct remains deferred under the current colocation decision.
