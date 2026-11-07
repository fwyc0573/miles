## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Record actual restored B baseline/preload/full-checksum/first-update evidence, second-rollout projection OOM, A's zero-update stop and D17. |
| 2026-11-07 | Record three independently submitted restored formal runs and verify admitted resource requests, source/image and personal identity; full runtime acceptance remains pending. |
| 2026-11-07 | Link confirmed C restart budget and memory allocation after preserving the original update/OOM evidence. |
| 2026-11-07 | Record raw post-eval uniform-policy corruption, actual C step0, host-memory OOM evidence and controlled A/B stops. |
| 2026-11-07 | Close attempt-accounting/client-deadline preparation with pinned76-case evidence and phase review. |
| 2026-11-07 | Preserve failed runtime-suite RCA and record native refill evidence plus the pending identity/deadline preparation gaps. |
| 2026-11-07 | Measure exact retained-input loss geometry on2 H800, close diagnostic initialization failure and record fused-launcher red/green. |
| 2026-11-07 | Record first-backward A/B failures, retained input geometry, C Running and64 passing native fused GPU checks. |
| 2026-11-07 | Submit the first ready pair B under the approved100-step budget and verify platform admission. |

# Qwen3.5 first-round training

## Scope and expected outcomes

Requirements D9–D14 own the unchanged budget, sampling, Adam/TIS settings and final text-only HF output. Each admitted pair has100 planned updates with8 fresh training completions each;24 group-isolated fixed monitoring prefixes are evaluated before training and at planned steps20/40/60/80/100. Successful/skipped updates and consumed/published versions come from native events, not schedule arithmetic. First optimizer execution establishes evidence that baseline-only scoring cannot provide. Auxiliary checks remain non-blocking for healthy native training.

Per-pair acceptance requires actual finite loss/gradient evidence, original-token global normalization, changed/published weights, unchanged D8 gates on updated/final monitoring, final HF package and actual text-inference reload. A Running job or initial baseline PASS does not satisfy these outcomes.

## B launch and admission

- Initial baseline: `exp-1107-055408-654957`, **PASS** for both same-version comparisons overall and in each stratum. See [native report](test_report_2026-11-07_native_prerequisites.md).
- Source/config commit: `4792c0e3`; [configuration](training_config.json) differs from the baseline in exactly budget and two output destinations.
- Formal job: **`exp-1107-062459-796906`**, observed **Running** at2026-11-06T22:27:27Z. Local launcher remains alive.
- [API receipt](evidence/platform-exp-1107-062459-796906-training.json): **PASS** for creator `i-fengyicheng`, current-host NFS `100.96.128.195:/data/ycfeng:/data/ycfeng`, pinned image digest, student8+teacher2 H800, correct training config in admitted commands and empty ConfigMap refs. The stale queue annotation does not override Running status.
- Image: `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`.
- Submission interpreter: `/data/ycfeng/tmp/stepmind-env/bin/python`, with personal credentials initialized from the runbook; worker selects `/opt/sglang/bin/python3` and the existing CUDA compatibility-library path.

Exact submission command after the unchanged personal-auth/proxy initialization:

```bash
# Working directory: /data/ycfeng
export STEPMIND_BACKEND=rjob PYTHONPATH=/data/ycfeng/steptron
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode
/data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/submit_qwen35.py \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/training_config.json \
  --pair B
```

Expected B native artifact root:
`/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/B/exp-1107-062459-796906/`.
Final intended HF destination is `hf/step_99` beneath that root;99 denotes the final planned rollout position, not an asserted successful-update count or model version. Local launch/terminal receipts go under `evidence/first-round/`.

## A launch and admission

A's initial baseline `exp-1107-055408-748211` passes independently. Formal job **`exp-1107-063447-691018`** was submitted from source/config commit `b9cd2442` with the same command above, changing only `--pair A`. [API admission](evidence/platform-exp-1107-063447-691018-training.json) verifies Running, personal identity, exact local source, pinned image,8+2 H800 and the correct training configuration. Its cloud run root is `.../first-round/student/A/exp-1107-063447-691018/`; final intended HF destination is `hf/step_99`. Native optimization evidence remains pending.

## Actual training results

A/B first attempts failed before their first completed optimizer update. Updated/final monitoring, export and reload are absent. Details below supersede the earlier Running admission observations. Do not extend the100-position budget automatically.

At06:43 local, a bounded read of B's actual cloud business log showed the formal run's initial monitoring progressing through18/24 samples with successful generation responses. This confirms business progress, not an optimizer update. Source: `.../first-round/student/B/exp-1107-062459-796906.log`, read through the authorized `/mnt/ws-jfs/ycfeng` mapping.

## C launch and admission

C's full27B/397B initial baseline `exp-1107-044223-241566` independently passes. Formal job **`exp-1107-064200-013666`** was submitted from `2991eb55` with the same command, changing only `--pair C`. [API receipt](evidence/platform-exp-1107-064200-013666-training.json) verifies personal identity, current-host mount, pinned image, one8-GPU student and two8-GPU teacher replicas, inherited gang-start ConfigMap references and teacher RDMA resources. Observed **Pending** at2026-11-06T22:43:55Z, with20 H800 quota remaining against24 requested. The existing launcher remains alive; no duplicate submission is needed.

Cloud run root: `.../first-round/student/C/exp-1107-064200-013666/`; final intended HF destination `hf/step_99`. All three formal attempts now use the approved100-position budget and unchanged qualified topology. Actual successful updates, post-update numerical acceptance, learning conclusions and HF reload are outstanding for each pair.

## First-backward failures and retained evidence

| Pair | Platform terminal evidence | Native observation | Outcome |
| --- | --- | --- | --- |
| A | Failed; finish2026-11-06T23:06:55Z; critical student failed, teacher stopped | First backward OOM; only publication0, no `train_group_step_end`; `0.pt` and `eval_0.pt` retained | FAIL for this attempt;0 completed updates |
| B | Failed; finish2026-11-06T22:58:31Z; same critical-task reason | First backward OOM; only publication0, no completed step; same retained artifact kinds | FAIL for this attempt;0 completed updates |
| C | Running on latest exact API readback | Independent teacher/student allocation remains active | Updated/final result pending |

API status: [readback](evidence/first-round-status-after-b-failure-20261107.json). Selected native evidence: [A](evidence/first-backward-A-exp-1107-063447-691018.json), [A/B/C first-update inspection](evidence/first-round-first-update-20261107.json). These were read through the authorized personal `/mnt/ws-jfs/ycfeng` mapping; full raw logs remain at each cloud run's sibling `.log` path.

The matched A rank0 allocation is **23077060608 bytes /21.4922 GiB**. Its exception reports21.49 GiB requested,12.81 GiB physically free,43.48 GiB allocated and19.82 GiB reserved-but-unallocated; the residual SGLang process uses1.60 GiB. Another B worker reports21.73 GiB: these are distinct allocations, not interchangeable measurements. Aggregate reserved memory is not evidence that every cached block can be released. The failure is in native backward, before any actual optimizer result or updated publication.

Exact RCA collector invocation, repeated for each bound A/B student with its incident window:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
  exp-1107-063447-691018 --replica exp-1107-063447-691018-student-cfcd2084 \
  --expected-creator i-fengyicheng \
  --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
  --start 2026-11-06T23:04:00Z --end 2026-11-06T23:08:00Z --timeout 30 \
  --output /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-first-update-exp-1107-063447-691018
```

The A collector returns all8 queries `ok`; retained A/B directories are `qwen-rca-first-update-<job>` under the approved local temporary root. Platform history records teacher cleanup after the critical student failure. Native OOM is the observed initiating application failure; no platform-first preemption is inferred.

## Native fused prerequisite checks

Job **`exp-1107-071708-069479`** succeeded on2 H800 in the pinned image. It used personal RJobBackend/local NFS,16 CPUs/64 GiB host memory, the existing CUDA compatibility path, normal pytest plugin loading and worker-local `/var/tmp/qwen-fused-$KUBEBRAIN_RJOB_NAME` caches. Runtime: Python3.12.16, torch2.14.1+cu130, Transformers5.19.0. Actual GPU identities and retained batch geometry are in [the receipt](evidence/fused-inputs-exp-1107-071708-069479.json).

```bash
MEGATRON_PATH=/root/Megatron-LM /opt/sglang/bin/python3 -B -m pytest \
  -p no:cacheprovider tests/fast-gpu/test_fused_log_probs.py \
  tests/fast-gpu/test_fused_log_probs_in_losses.py -q \
  --basetemp="$TMPDIR/pytest" --tb=short
```

Expected: existing TP/numerical/gradient/memory contracts all pass. Actual: **64 passed,19 warnings in118.16s**; full log `evidence/fused-backward-checks-exp-1107-071708-069479.log`. This is native kernel/loss verification, not full-model capacity. The retained A/B first batches each contain8 samples; total lengths are96330/97154/74497/67202/69721/71306/93862/92706, all with8192 response tokens. No input was truncated or regenerated for inspection.

The existing `--log-probs-backend fused` can reuse logits storage when `recompute_loss_function=False`. The equal-geometry H800 experiment below confirms the allocation pattern and supplies evidence for enabling this path. Full-model optimization acceptance remains outstanding.

## Equal-geometry loss-stage experiment and launcher repair

Diagnostic: `tests/manual/agent_opd/probe_qwen35_loss_memory.py`. Runtime is the same pinned image, Python3.12.16/torch2.14.1+cu130,2 H800, TP2/CP1/thd. It uses retained B sample7's actual token IDs/mask and native packing, with seeded synthetic BF16 logits. It measures negative summed response logprobs and their full gradient, not the complete OPD objective or model backward. No optimizer or update is constructed. Native resolved values are independently captured in [the geometry receipt](evidence/native-loss-geometry-B-exp-1107-062459-796906.json).

```bash
/opt/sglang/bin/python3 -B -m torch.distributed.run --standalone --nproc-per-node=2 \
  --module tests.manual.agent_opd.probe_qwen35_loss_memory \
  --rollout-data /mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/B/exp-1107-062459-796906/rollout_data/0.pt \
  --sample-index 7 \
  --launch-receipt task_memory/task_2026-11-06_qwen35_three_pairs/evidence/first-round/student/B/exp-1107-062459-796906/launch.json \
  --padded-vocab-size 248320 --data-pad-size-multiplier 128 \
  --gradient-chunk-rows 64 --trace-allocations \
  --report task_memory/task_2026-11-06_qwen35_three_pairs/evidence/loss-memory-exp-1107-074344-969435.json
```

Expected: both paths complete at identical geometry, finite scores/gradients, zero unscored gradients, native test tolerances satisfied, fused gradient aliases logits and its measured peak is lower. Actual: **PASS on both ranks**, job `exp-1107-074344-969435` Succeeded. [Full report](evidence/loss-memory-exp-1107-074344-969435.json), raw log of the same stem, and [API identity/image/mount receipt](evidence/platform-exp-1107-074344-969435-loss-stage.json) are retained.

| Per-rank measurement | torch | fused |
| --- | --- | --- |
| Padded logits shape | `[1,92928,124160]`, BF16 | identical |
| Backend peak allocated bytes | 69,229,567,488 | 23,078,271,488 |
| Peak GiB | 64.48 | 21.49 |
| In-place gradient storage | no | yes |
| Nonfinite / nonzero unscored gradient elements | 0 /0 | 0 /0 |

Fused peaks subtract only the live reference-gradient storage; validation scratch is excluded, raw allocator measurements retained. Reduction is **46,151,296,000 bytes /66.664%**. Full comparison covers11,537,940,480 gradient elements per rank with zero tolerance violations; maximum absolute gradient and logprob differences are both9.5367431640625e-7. Native large allocations identify `aten.zeros([84513,124160])` and `aten.cat(...)->[92928,124160]` on torch; no equally large eager allocation is observed on fused. This proves the loss-stage allocation reduction, not the exact original failed operator, TMS fragmentation behavior or complete model capacity.

Initial diagnostic job `exp-1107-074100-109069` failed before loss execution: the single-rank test utility used initialized WORLD as its TP group, producing `expected1, got2` / rank mismatch. Constructing the trivial state before distributed initialization fixes the cause. A real two-process Gloo test on local Python3.12.13 passed both ranks before the GPU rerun. All8 failure-collector queries are retained under `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-loss-pg-exp-1107-074100-109069`; original GPU log remains `evidence/loss-memory-exp-1107-074100-109069.log`.

Launcher change: append existing `--log-probs-backend fused` to the common performance block. Existing A/B/C × baseline0/formal100 command contracts now require it; native default parsing additionally requires `recompute_loss_function=False`. Exact local selection:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -o addopts='' \
  -p no:cacheprovider tests/fast/test_qwen35_opd_launcher.py \
  -k 'native_command_utils_composes_full_student_and_external_teacher or native_false_defaults_and_baseline_eval' --tb=short
```

Red: **7 failed /3.77s**, missing backend flag/default torch. Green: **7 passed /3.47s**. C remains Running on the latest exact API readback; its student launch receipt did not yet exist when this common-source edit was made.

Pinned0-GPU job `exp-1107-075006-580618` used the same image/CUDA compatibility path and normal pytest plugins. It ran `test_qwen35_pair_worker.py`, `test_qwen35_opd_launcher.py`, `test_qwen_reload.py`, `test_qwen_text_export.py` and the two named CP reconstruction checks. Actual: **148 passed,4 failed /19.23s**. All89 worker/launcher and40 new reload tests pass. The four failures are unchanged `test_real_hybrid_decoder_roundtrip` cases invoking installed CUDA-only convolution on CPU (`Expected x.is_cuda() to be true`). Whole-job status is **Failed**, not a clean suite PASS. These previously known incompatible CPU-forward cases were unnecessarily included; no further pinned CPU rerun or fixture workaround is required for this launcher change. Log: `evidence/fused-runtime-exp-1107-075006-580618.log`. The native text registry probe separately succeeds; its evidence is owned by the HF report.

The exact personal RCA collector subsequently completed all8 queries for this0-GPU failure (Python3.10.6/brainpp2.8.6). Original evidence: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-fused-runtime-exp-1107-075006-580618/`. RJob UID=`6eaf57b1-9614-4d29-b2a2-3ea85960dbbe`; replica UID=`043459e6-fe9c-476b-a0fb-b5e971f49a1d` owns that exact RJob. Container exit1 at23:51:31Z precedes `Some critical tasks failed.` cleanup at23:51:34Z and local launcher stop23:51:35Z. Observed container imageID equals the configured digest. The application test error is the initiating failure; no stop actor/request time is inferred from cleanup. Live replica events are empty over the returned complete query, not proof that no other event occurred. Command: `collect_failure_evidence.py exp-1107-075006-580618 --replica exp-1107-075006-580618-cfcd2084 --expected-creator i-fengyicheng --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng --start 2026-11-06T23:49:00Z --end 2026-11-06T23:53:00Z --timeout 30 --output <the directory above>`, through the established personal Python/proxy environment.

## Formal-run lifecycle preparation

Read-only owner `QWEN-P3-RUN-PREFLIGHT` confirms the active class-based rollout path. `inference_rollout_common.generate_and_rm_group` cancels and drains failed siblings and hands over output-store refs; `inference_rollout_train.generate_rollout_async` propagates `NonRetryableError` and refills recoverable/drop cases to exactly8 valid groups. Existing tests cover credits, output-store ownership, missing-reward refill, filter precedence and fatal errors. Supplied CPU results:7 passed/2.35s (`test_inference_rollout_train.py` and `test_lifecycle_attempt.py`),51 passed/3.11s (`test_sample_completion_backfill.py`, `test_filters.py`, `test_inference_rollout_common.py`), and an in-memory timeout→replacement-success check. No new GPU evidence is claimed from those checks.

The two preparation blockers are **CLOSED**. `qwen_alignment.py` now records logical adapter attempts with stable source/sample/group/rollout identities, start/end timestamps, durations, outcome, error type and native status/version spans. Its existing student await is bounded by the3600-second request setting across the native retry chain. The teacher and student observer retain their independent native aiohttp total bounds. Core retries, skip/refill and denominators are unchanged. Exact implementation/red-green evidence is in the [sample-boundaries report](test_report_2026-11-07_sample_boundaries.md); the pinned combined check passes76 tests/11.88s in [the runtime log](evidence/sample-boundaries-exp-1107-084523-486765.log).

Fused changes only loss/scoring kernels, not these lifecycle paths. Fixed monitoring's trainer scores also change backend, so the fresh fused runs must establish their own D8 baseline/updated measurements. Earlier torch-era D8 results remain historical qualification, never substitute for fused-run measurements. Native refilling may increase attempts beyond the planned800 consumed completions; reconcile attempts, failures, cancelled/filtered groups, consumed completions and successful/skipped updates separately.

### Cancellation evidence and selected correction

`QWEN-P3-RUN-PREFLIGHT` locally verified actual TCP close on cancelling httpx0.28.1/httpcore1.0.9 under Python3.12.13: request observed at0.138s, cancellation and peer EOF at1.111s. Source at the exact pinned commit [056f871](https://github.com/sgl-project/sglang/tree/056f871a7ee8b4573832049011f0fdf52589cfd8) shows non-streaming forwarding arms `AbortOnDrop` (`sgl-router/src/proxy/mod.rs:276–335`); dropping sends a bounded `/abort_request` for the router-minted rid (`proxy/abort.rs:16–47`). This workload supplies no rid, so the exception for caller-owned ids/fan-out does not apply (`server/routes/chat/preparation.rs:572–579`). The engine handles early abort through `abort_before_dispatch` (`tokenizer_manager.py:2454–2490`). The native router test covers handler drop, not an end-to-end TCP→GPU observation. Abort delivery remains best-effort if the router exits or its abort POST fails.

The selected correction is implemented and verified. Local14 lifecycle tests plus29 existing focused cases pass; pinned `exp-1107-084523-486765` runs the complete launcher and lifecycle modules with76 passing tests. Phase reviewer `QWEN-P3-RESUME-PREP` found no actionable code defect; its P3 stale-status documentation finding is resolved here and in progress/plan. This establishes preparation, not native full-model capacity,100-step completion or final result acceptance. End-to-end router disconnect-to-engine abort remains source-backed; pinned httpx0.28.1/httpcore1.0.9 match the locally verified cancellation libraries.

## Confirmed probability corruption after evaluation

Pinned0-GPU inspection `exp-1107-090605-345795` runs the existing `inspect_qwen35` CLI on `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/C/exp-1107-064200-013666`, with the frozen population report and that exact job's teacher-ready receipt. It writes `fused-baseline-inspection.json` in the run directory and the selected local [baseline receipt](evidence/fused-baseline-C-exp-1107-064200-013666.json). Expected D8 mean<=0.03; actual decode mean12.079090581084612 across7169 valid tokens: **FAIL**. Versions and required scores are present; missing-score arithmetic does not explain it.

Independent pinned0-GPU `exp-1107-092209-060993` directly loads native `rollout_data/*.pt` and `train_data/*.pt` with `torch.load(map_location="cpu", weights_only=False)`, without importing inspector arithmetic. It concatenates the original saved `rollout_log_probs`, `metadata.student_rescoring.response_logprobs`, and `rollout_data.log_probs` vectors and reports count/min/max/mean/std/unique counts. [Raw evidence](evidence/raw-score-evidence-exp-1107-092209-060993.json) and [job log](evidence/raw-score-evidence-exp-1107-092209-060993.log) retain the outputs.

| Boundary | Observed result | Interpretation |
| --- | --- | --- |
| C original baseline decode / prefill |7169 each, nonuniform, means-0.3438427470 /-0.3441828373 | Original inference was not uniform. |
| C baseline trainer |7169 values all-12.422473907470703, std0 | Actual native scorer corruption; float32(-ln248320). |
| C post-eval rollout0 decode / prefill |65536 each, all the same uniform value | Actual generation is affected, independently of the reader. |
| C post-eval completions |8×8192 tokens,8045–8078 distinct IDs each | The native workload consumed these corrupted-policy completions. |
| C ordinary training forward |Nonuniform, combined mean about-13.3506 | Ordinary training and eval scoring restore paths differ. |
| A new baseline trainer |4331 values all the same uniform value underTP2 | Not a TP4-only symptom. |
| B at inspection |No saved score artifact yet | No B numerical claim. |

The restore loop and its limits are owned by [the restore report](test_report_2026-11-07_eval_restore.md); the unchanged-input kernel comparison is owned by [the arithmetic probe report](test_report_2026-11-07_uniform_scores_probe.md). Neither CPU injection nor a kernel-only result establishes real full-model restoration.

Historical formal attempts before the fused change independently show the same symptom: B4712 andA4279 trainer tokens are uniformly-ln248320 and their native metadata explicitly records backend`torch`. The [historical receipt](evidence/historical-torch-scores-and-C-flags.json) preserves exact executed SSH argv/source and reader environment. Thus the symptom predates fused. The same read verifies C's actual offload/backing flags; these are runtime evidence, rather than assumptions based on launch options.

## C first update and host-memory OOM

Native `train_group_step_end` at2026-11-07T01:11:11.107070Z records rollout0, attempt0 and all8 ranks NORMAL. Native rank0 metrics report loss0.03943031281232834, grad_norm2.9772250652313232, LR2e-6. The next actor.sleep fails with lost Ray workers; the latest published version remains0. This is **one completed optimizer step and eight consumed completions**, not a published or numerically qualified update. No convergence claim is supported.

Exact bound objects: RJob UID `1f440b3e-d419-43ca-bf29-0d38ee777e4b`; student Replica UID `511fe1ec-eb6f-475b-9a57-dea7fff8ba60`; node `gpu-h800-0223.host.platform.shaipower.com`. Container status explicitly says `OOMKilled`, exit1, finished01:12:45Z. Critical-task cleanup starts01:12:47Z; final job finish01:12:59Z precedes launcher cleanup01:13:01Z. Thus launcher stop is subsequent cleanup.

The retained [cgroup receipt](evidence/first-round/student/C/exp-1107-064200-013666/memory.json) has4346 samples: sampled max805304623104 bytes; kernel max805305688064 bytes; limit805306368000 bytes (750GiB); oom_kill changes0→1. `memory.failcnt` remains0, so retain that counter rather than inventing an allocation count. Together with the container reason, this confirms host/container-memory OOM; it does not identify the individual allocation or prove that the earlier probability defect caused the OOM.

Read-only inspection of retained `failure-diagnostics/rank-0/memory.jsonl` and selected Ray logs is archived in [C-host-memory-window.json](evidence/C-host-memory-window.json), including exact inspection argv/source. Usage is378.1497GiB near01:07:24Z,372.7468GiB near01:08:02Z, and728.5112GiB at01:11:09.63Z; it then reaches the cgroup limit during sleep. Ray reports its0.95 memory threshold exceeded but later says no worker was selected to kill. This distinguishes Ray pressure observations from the explicit cgroup kill counter. Earlier00:21 GPU allocator OOM warnings precede the completed baseline/training and are not substituted for the terminal host-memory cause. The existing HF directory is absent, consistent with final-only save before the failed publication; no recoverable post-step artifact is established.

Collector command, through the documented personal Python/proxy environment:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
  exp-1107-064200-013666 --replica exp-1107-064200-013666-student-cfcd2084 \
  --expected-creator i-fengyicheng --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
  --start 2026-11-07T01:10:30Z --end 2026-11-07T01:13:30Z --timeout 30 \
  --output /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-sleep-exp-1107-064200-013666
```

Seven reads succeed; no existing DeepScan is returned. RJob all-operation audit fails with `Audit response contains a different resource name.` Those rows are not accepted as this job's evidence. A bounded existing-session Sherlock read also fails; detailed kernel victim/allocation remains UNKNOWN. No arbitrary memory scaling or optimizer change is accepted from these observations.

## A/B controlled stop and remaining budget

At the pre-stop event check A has baseline publication0 and no completed train step; B has neither publication nor completed train step. At09:28:07 local, the required personal `rjob_stop.sh` stops exact jobs `exp-1107-085640-136853` and `exp-1107-085640-141571`, with reason recorded in `/data/ycfeng/tmp/rjob-stop-audit.log`: confirmed native post-eval uniform-policy corruption, A reproduction, zero completed A/B updates. Both launchers then reportStopped. This action follows direct workload corruption evidence, not an automatic auxiliary D8 verdict. C's consumed optimizer step and absent post-step published state must be accounted for before any fresh100-step restart decision; no budget reset is inferred.

The subsequent explicit restart decision is recorded as D15 in [requirements](requirements.md), with the original update retained as discarded historical work. D16 selects the larger student memory allocation using the normal backup path; the exact rendered request, source-backed alternatives and remaining capacity checks are owned by [the C host-memory report](test_report_2026-11-07_C_host_memory.md). Shared restoration was still unqualified at this historical point; the later B result below supplies actual repaired preload/full-model evidence.

## Restored formal runs submitted at15:08 local

Source/config commit `db60066c`. Production restoration and receipt-consumer CPU checks remain valid; the real H800 diagnostic measured two complete native CUDA IPC transactions with exact restored bytes/scores and unchanged synthetic master/Adam/version. Its probe-only private-pool cleanup then failed, so the original artifact remains ERROR. Focused call-site inspection confirms that cleanup is unreachable in formal training. The updated plan separates this diagnostic exit repair from actual preload/full-model qualification, which is still a formal-run acceptance requirement. The [restoration report](test_report_2026-11-07_eval_restore.md) owns the detailed evidence and diagnostic limitations.

The unchanged submission command above was run independently with `--pair A`, `--pair B` and `--pair C`, all from `/data/ycfeng` through personal Python RJobBackend. All three launchers remain alive. [Exact API receipt](evidence/platform-restored-formal-admission.json) verifies creator `i-fengyicheng`, pinned image digest, current local NFS source, intended config/pair, replicas and CPU/GPU/memory requests and limits:

| Pair | RJob | Requested GPUs | Student memory limit | Initial platform state |
| --- | --- | --- | --- | --- |
| A | `exp-1107-150849-708403` |8+2 |500GiB |Pending |
| B | `exp-1107-150849-818314` |8+2 |500GiB |Pending |
| C | `exp-1107-150849-814926` |8+16 |1500GiB |Pending |

All three retain100 planned positions and8 valid training completions per position. C is the single D15-authorized fresh100-step restart; its old failed update remains discarded historical work. [Dry-run resource receipt](evidence/restored-formal-resources.json) passes; [capacity observation](evidence/restored-formal-capacity.json) records122 Starting/Running requested GPUs against the stated128 capacity before submission, which is not a measured free-device count. The platform owns scheduling and no duplicate is submitted because of queuing.

The independent1H800 diagnostic rerun `exp-1107-150925-737118` uses the pinned cleanup fix and was observedStarting in the same API inspection. Its outcome does not replace initial/restored formal receipts, first actual optimizer evidence, C's worker cgroup/peak measurement, updated/final D8 or final HF qualification. Auxiliary validation remains a soft observer of healthy training.

## Restored B: actual baseline and first update pass, next scoring forward OOM

### Execution and numerical checks

B `exp-1107-150849-818314` uses the pinned image above,8 student H800 and2 teacher H800, student TP2/DP4, fused log probabilities, the original131072 context budget, and100 planned positions. [Startup check](evidence/B-restored-startup.json) records executed source `ca4ed904974480717d43e842511fb52702b705f9`, no tracked code modifications and the separately listed uninvoked manual probe. Native actor environment reports record `LD_PRELOAD=/opt/sglang/lib/python3.12/site-packages/torch_memory_saver_hook_mode_preload_cu13.abi3.so`, `TMS_INIT_ENABLE=1` and CPU backup enabled for all8 unique actor ranks. Multiple environment reports per rank are expected and are preserved.

Read-only pinned0-GPU inspection `exp-1107-161155-640804` succeeds with Python3.12.16 using the existing inspector:

```bash
CUDA_VISIBLE_DEVICES="" /opt/sglang/bin/python3 -B -m tests.manual.agent_opd.inspect_qwen35 \
  --run-dir /mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/B/exp-1107-150849-818314 \
  --population-report /mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/population-exp-1106-233008-986003/population.json \
  --teacher-ready /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/evidence/first-round/exp-1107-150849-818314/B/teacher-ready.json \
  --report /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/evidence/baseline-inspection-B-exp-1107-150849-818314.json
```

Expected: baseline version0,24 samples, every original valid token present/finite, overall and each populated length stratum mean absolute difference<=0.03. Actual:5230 valid tokens, no missing/nonfinite tokens; all PASS. [Full inspector result](evidence/baseline-inspection-B-exp-1107-150849-818314.json), [compact summary](evidence/B-restored-baseline-summary.json).

| Stratum | Tokens | Decode mean absolute difference | Prefill mean absolute difference | Result |
| --- | ---: | ---: | ---: | --- |
| Overall |5230 |0.010410223700056861 |0.010425440819193454 |PASS |
| Short |583 |0.01118094718173426 |0.013342928339345859 |PASS |
| Medium |3118 |0.008372108608037785 |0.008326414784514166 |PASS |
| Long |1529 |0.01427255925734761 |0.013593438171633717 |PASS |

The native initial publication `195e0ef5783b4af0b20e2354d3eada45` and post-eval restore `444bd141ff0a4a50b7e469b5417fe719` both publish version0 with the same trainer epoch and no failed cells. Complete checksum dictionaries match all1416 tensors on each of4 cells, including the previously unobserved same-run vision entries. The restore consumes no optimizer position. At08:12:55.802922Z, rollout0 completes with8/8 NORMAL outcomes; at08:13:10.557444Z, planned publication `eff8fb82604445e390ea78c1bf8f1d1c` advances0→1 on all4 cells. Each updated cell changes486 tensor checksums. The normal outcomes plus actual counter increment establish **one successful update**, not merely one attempted iteration.

[Retained native events/checksums](evidence/restored-ab-runtime-receipts.json), [checked runtime summary](evidence/restored-ab-runtime-summary.json), and [native metrics](evidence/B-restored-native-metrics.json) preserve this evidence. Rollout0 has8 completions, mean response399.5 tokens, no truncation, all decode/prefill versions0. First update loss is0.06751072660405585, grad norm8.026847839355469, LR2e-6; both low/high TIS-mask fractions are0. The subsequent8 completions use version1 consistently, mean431.25 tokens and no truncation. These observations close the concrete post-eval uniform-policy symptom for this B cycle. They do not establish learning improvement, updated/final D8, sustained capacity,100-step completion or final HF acceptance; the inspector overall remains INCOMPLETE.

### Native failure and bounded diagnosis

At08:14:39Z the next `_compute_log_prob` forward fails in `GPT._postprocess -> ParallelLinearCrossEntropy.forward -> LinearWithGradAccumulationAndAsyncCommunication.forward -> torch.matmul(total_input, weight.t())`. It requests19.12GiB with18.30GiB free on GPU5 (79.19GiB total). PyTorch reports41.75GiB allocated and15.95GiB reserved-but-unallocated; the process uses59.26GiB and the other process1.59GiB. This is the output projection before the fused scoring/loss operation, distinct from the historical torch-backward allocation failure. Reserved bytes alone do not prove fragmentation.

Native memory observations show allocated14.41–14.42GiB after baseline scoring, about19.09GiB after the first optimizer step, and varied reserved footprints25.8–36.06GiB at the next wake. Investigate retained scoring storage, optimizer state and packing/allocator behavior separately. No behavior change is justified solely by these byte differences.

[Retained sample geometry](evidence/B-restored-sample-shapes.json) is read with remote Python3.12.3/torch2.5.1 on CPU, without loading a model or executing an optimizer. Rollout0 totals range59246–89434 tokens; every DP slice has two single-sample microbatches. Rollout1 totals range54440–121140, including82534 tokens at sample15. All16 samples are completed. The ordinary training dumps and eval-observer dumps have different metadata fields; the reader records native ordinary-training rank/length/microbatch fields after direct schema inspection. These are geometry observations, not proof of the OOM allocation's lifetime.

[Platform termination receipt](evidence/B-restored-platform-termination.json): RJob UID `e3b32aa5-b749-41e5-aeee-9e77f7e7bf72`, student replica UID `bcb511f3-ca3e-4ebf-9559-baa223f627a4`, node `gpu-h800-0105.host.platform.shaipower.com`: student terminates08:15:03Z with exit1/Error, critical-task cleanup starts08:15:05Z, job finishes08:15:18Z. Launcher cleanup follows at08:15:20Z. This is not a container `OOMKilled` record. All8 collector queries succeed:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
  exp-1107-150849-818314 --replica exp-1107-150849-818314-student-cfcd2084 \
  --expected-creator i-fengyicheng --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
  --start 2026-11-07T08:12:00Z --end 2026-11-07T08:16:00Z --timeout 40 \
  --output /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-B-exp-1107-150849-818314
```

The dashboard log endpoint returnsHTTP502; raw cloud log/event reads therefore use the permitted read-only `ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng 'python3 -B -'` route, confined to `/mnt/ws-jfs/ycfeng/miles-qwen35-three-pairs/first-round/student/{A,B}`. Full raw business logs remain in the cloud; selected memory/error lines and publication evidence are retained locally above.

### A stop and revised B budget

A uses the same4B TP2/GPU-optimizer capacity path and was still initializing. The exact controlled stop command is:

```bash
bash /data/ycfeng/steptron/playground/users/ycfeng/tools/rjob_stop.sh \
  --creator i-fengyicheng \
  --reason "Pause A before further updates: same Qwen4B TP2 GPU-optimizer configuration as B, which hit native output-projection CUDA OOM after publishing version1; diagnose capacity before consuming remaining budget" \
  exp-1107-150849-708403
```

It stops at16:23:33 local; the launcher reportsStopped16:23:57. Native A files contain environment reports only, without a training or publication event:0 actual updates. Both A/B HF directories are absent. B's published state therefore cannot be resumed. D17 explicitly approves one fresh100-step B run after repair, retaining its prior1 update in historical accounting; A retains its original100 budget. C's existing D15/D16 submission is independent and its runtime observations remain pending.
