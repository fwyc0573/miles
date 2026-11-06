## Modification History

| Date | Change |
| --- | --- |
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

Pending. Admission is verified; real optimizer outcomes, memory, monitoring, export and reload have not yet been measured. Retain original native failures and actual partial progress if the attempt ends early. Do not extend the100-position budget automatically.

At06:43 local, a bounded read of B's actual cloud business log showed the formal run's initial monitoring progressing through18/24 samples with successful generation responses. This confirms business progress, not an optimizer update. Source: `.../first-round/student/B/exp-1107-062459-796906.log`, read through the authorized `/mnt/ws-jfs/ycfeng` mapping.

## C launch and admission

C's full27B/397B initial baseline `exp-1107-044223-241566` independently passes. Formal job **`exp-1107-064200-013666`** was submitted from `2991eb55` with the same command, changing only `--pair C`. [API receipt](evidence/platform-exp-1107-064200-013666-training.json) verifies personal identity, current-host mount, pinned image, one8-GPU student and two8-GPU teacher replicas, inherited gang-start ConfigMap references and teacher RDMA resources. Observed **Pending** at2026-11-06T22:43:55Z, with20 H800 quota remaining against24 requested. The existing launcher remains alive; no duplicate submission is needed.

Cloud run root: `.../first-round/student/C/exp-1107-064200-013666/`; final intended HF destination `hf/step_99`. All three formal attempts now use the approved100-position budget and unchanged qualified topology. Actual successful updates, post-update numerical acceptance, learning conclusions and HF reload are outstanding for each pair.
