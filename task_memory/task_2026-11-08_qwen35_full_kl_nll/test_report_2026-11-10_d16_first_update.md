## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Verify the first actual H200 update and persisted profile; preserve the subsequent native host-memory failure as a separate incomplete-run result. |

# D16 first formal update verification

## Result and scope

**D16 first-update inspection PASS; Ticket02 GPU criterion PASS.** Job `exp-1110-140032-491115`, cell `A/full`, successful update1, bank0/visit1. Native training subsequently failed during post-update offload, so the formal result remains **1/200, INCOMPLETE**. The verified first update is not combined with a future attempt.

The primary used inspector `24e8386f`, reporter `d0f67887` and the unchanged runtime `DistillationProfile.rebuild`. Evidence: [verification receipt](evidence/d16-H200-A-20261110/first-update-verification.json), [machine report](evidence/d16-H200-A-20261110/report.json), [readable report](evidence/d16-H200-A-20261110/report.md), and [exact-job terminal readback](evidence/formal-H200-A-terminal-readback-20261110.json).

## Inputs and exact entry point

Local snapshot: `/data/ycfeng/tmp/agent-opd-image/d16-exp-1110-140032-491115/`, captured `2026-11-10T06:31:16.127341Z`. Its `first-update-and-failure.tar.gz` retains native updates, optimizer attempts, teacher stages, canonical bank0, both profile files and the rank0 log. The corresponding protected cloud root is `/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/formal-h200-112k-20261110/full/student/A/exp-1110-140032-491115`. No formal cloud artifact was deleted.

Native updates and both profile JSONL files were additionally copied under `evidence/d16-H200-A-20261110/retained/`; byte comparisons with the snapshot passed. Canonical bank0 is70,951,726 bytes and remains in the raw snapshot/cloud rather than Git.

Run from the `agent-opd-image` worktree using Python3.12.13:

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.distillation_report \
  --training-dir /data/ycfeng/tmp/agent-opd-image/d16-exp-1110-140032-491115/training \
  --job exp-1110-140032-491115 --cell A/full --expected-updates 200 \
  --terminal-path task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/admission-formal-H200-A-20261110.terminal.json \
  --output-prefix task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/d16-H200-A-20261110/report
```

Observed exit0 with native/profile/overall INCOMPLETE, verified profile prefix1, and update1 milestone VERIFIED. Future milestones are NOT_OBSERVED with null values. This successful inspection command does not mean the training job succeeded.

## Acceptance observations

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Native identity/count | Same attempt/cell/full protocol/teacher; real unskipped ACK | Update1, bank0/visit1,256 turns, native attempted1/skipped0 | PASS |
| Acquisition | At least231/256 within1800s |256 valid,0 missing,0 pending;529.280799s | PASS |
| Canonical binding | Exact UID, source conversation, training-turn ordinal and original mask |256 one-to-one rows;32 conversations;37,628 original tokens | PASS |
| Length budgets | Prompt≤114688, response≤16384 | Maximum prompt55,049; maximum response8,690 | PASS |
| Teacher stages | Successful requests and token alignment |256 request successes and256 validation successes; each scored-token count matches response length | PASS |
| Pre-TIS RKL | Sum of persisted turn sums / original tokens equals ACK |3393.9780913887316 /37628 =0.09019820589424715; absolute difference0 | PASS |
| Pre-optimizer NLL | Same original-token denominator and ACK value |20000.222806594044 /37628 =0.5315250028328384; absolute difference0 | PASS |
| Persistence/rebuild | Both complete files reproduce runtime summary | One line in each file;256 observations; exact summary equality | PASS |
| Full-mode identity | First visits only | All replay numbers0;32 positive conversation baselines,32 alive | PASS |
| Incomplete run baseline | B10/k10 unavailable at update1 | Run baseline, run-relative gaps and trend remain null | PASS |

The primary independently streamed the canonical bank and compared its UID set, sealed slots0–255, source identities, teacher alignment and original mask counts with the256 persisted observation rows. The first manual assertion incorrectly used raw `assistant_turn_index` as profile `t_id`. `SweReplay._record_profile` at `swe_replay.py:368` explicitly uses `assistant_turn_ordinal`; correcting that audit assumption made the independent comparison pass. Runtime/input artifacts were unchanged. A UID may end in raw message index2 while its profile training-turn ordinal is1.

## Measured stage times

| Observation | Seconds | Interpretation |
| --- | ---: | --- |
| Initial weight sync |1.876198 | Native rank0 perf0 record |
| Acquisition |529.280799 | Sealed-bank end minus acquisition start |
| Teacher request wall span |486.135320 | Earliest start to latest finish; overlaps generation |
| Mean teacher request elapsed |34.299420 | Includes queue/network/service;256 requests overlap |
| Student scoring |81.964772 | Native `perf/log_probs_time` |
| Actor training |153.833701 | Native `perf/actor_train_time` |
| Training total |237.390344 | Native `perf/train_time` |
| Acquisition start to ACK record |778.955104 | Includes later scheduling/transfer/training work |
| ACK record to last profile-file mtime |1.497685 | Archive-preserved original mtime; includes rank completion/RPC/persistence |

Parallel stage durations are not summed into a sequential wall time. Pure profile compute overhead was not instrumented; the last interval is not a measurement of profile CPU time alone. CPU complexity/timing evidence remains in the module/integration reports.

## Subsequent native failure and remaining work

All eight trainer outcomes were NORMAL at06:27:56Z. During the following `sleep`/offload, Ray reported host-memory pressure and selected a trainer worker for termination. The diagnostic reports487.49GiB of a500GiB cgroup limit; a separate kill-scan reading was510,431,268,864 bytes against the510,027,366,400-byte95% threshold. These are separate observations, not one claimed peak. The subsequent weight-update failure ended the job at06:29:33Z. At06:39:22Z the exact personal API confirmed student Failed/Stopped and teacher Stopped, with no active replica.

The underlying allocation/retention cause is under investigation. No Ray protection setting, training parameter or memory request was changed based on this inspection. The native failure was not caused by an inspector verdict or profile stop.

[Failure/query coverage](evidence/d16-H200-A-20261110/failure-and-coverage.json) records six successful bounded RCA reads and two failed audit reads. Audited stop-request actor/time remain UNKNOWN. The selected native excerpt and complete raw log are retained; this audit gap is not claimed as closed.

B's first-A-update and completed-inspection dependency is now satisfied, but the known native failure still needs resolution and B needs fresh resource admission. Neither A nor B has completed its200-update acceptance. This report accepts only the first-update measurement/persistence criterion.
