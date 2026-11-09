## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record exact upstream terminal/timeout evidence and failed audit-query coverage; synchronization diagnosis is pending. |
| 2026-11-09 | Record D33 documentation checks, live resource inspection and isolated admission preparation. |

# H800 execution preparation

## Authorization and current gate

D33 authorizes H800/codesign execution with no task GPU-count cap. Parent Ticket01 is accepted; D1/D22 still require upstream256-turn capacity acceptance before merge and Ticket02/03 integration. The already-submitted upstream job is separate from this task's H800 allocation.

## Observed checks

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Document links and dependency graph afterD33 | Existing six tickets remain coherent |21 documents,6 tickets,75 links,22 anchors; zero errors | PASS |
| Whitespace | No diff errors | `git diff --check` exits0 | PASS |
| Fresh personal H800 commitments | Query actual nonterminal non-preemptible jobs using Python API | At07:13:27Z:24 GPUs across three other jobs | RECORDED |
| Upstream native gate | Actual capacity evidence, not submission/startup alone | `exp-1109-144110-764758`: Failed at07:47:18Z; initial weight synchronization timed out after600s, before rollout collection | FAILED / GATE NOT MET |
| Unlimited allocation | No manufactured numeric ceiling | Candidate`gpu_policy.json` has explicitnull; isolated`1ae93261` passes25 budget+4 consumer checks | CPU PASS |
| H800 payload/runtime | Configuration validated, then actual H800 runtime evidence | No H800 payload accepted or job submitted yet | PENDING |

Commands:

```bash
python3 tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll
git diff --check
```

Resource queries used `/data/ycfeng/tmp/stepmind-env/bin/python` (Python3.10.6), with the authoritative runbook's personal authentication/proxy initialization, `STEPMIND_BACKEND=rjob`, `PYTHONNOUSERSITE=1` and `PYTHONDONTWRITEBYTECODE=1`. The paginated native `list_namespaced_custom_object` query used creator label`kubebrain.brainpp.cn/creator=i-fengyicheng`, page limit100 and20-second request timeout, feeding the existing `rjob_budget.committed_jobs` forH800 andH200. Exact-job queries then used `get_namespaced_custom_object`, `get_rjob_infos` and bounded replica logs. Filtered artifacts:

- `evidence/h800-resource-readback-20261109.json`
- `evidence/upstream-h200-startup-readback-20261109.json`

Importing Steptron before Miles initially raised`ModuleNotFoundError: No module named 'tests.manual'`. A focused import probe showed Steptron's initialization prepends`third_party/super_agent/tests` ahead of Miles. Importing the Miles budget reader before Steptron, matching the existing submitter's ordering, fixed the local readback. No dependency installation or worker retry occurred.

## Isolated code preparation

Worktree:`/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`, branch`agent-opd-h800-capacity`, base`c52991ac`. Local preparation record:`task_memory/task_2026-11-09_profile_h800_preparation/`. This isolates resource changes from the live upstream job and does not merge upstream into the parent branch. The completed code and records must be consolidated into the final parent branch after its gate permits integration.

No GPU capacity or formal-run acceptance is claimed by these CPU/read-only checks. A personal commitment count is not an estimate of free cluster capacity; the platform remains the scheduling authority.

## H800 sizing decision

Prepare36 H800 GPUs per pair: four student/rollout nodes of8, with the first8 also running trainerTP4/DP2/CP1;32 rollout GPUs host8 TP4 engines, two colocated and six dedicated. Teacher uses4 GPUs/TP4. Existing memory fraction0.7, max-running1,128K total context and131072 dynamic-batch token target remain unchanged. D34 separately sets112K prompt/16K completion. Native rollout layout is declared by`h800_sglang.yaml`.

Evidence: a131072-token scoring tensor at vocab248320 has bf16 logits of30.3125GiB per TP2 rank and15.15625GiB per TP4 rank; the former matches the measured H200 allocation request32,547,799,040bytes. These are individual tensor sizes, not measured H800 peak memory. `max_tokens_per_gpu` is a packing target: `seqlen_balancing.first_fit_decreasing_pack` leaves an oversized sample whole, so reducing that target cannot bound a single128K sample. The prior exploration's32768-token workaround and0.6 memory fraction were withdrawn as unsupported. No guessed throughput multiplier is used as acceptance evidence.

The existing entrypoint's two-student-node restriction blocks this layout despite native engine-group support. `profile-h800-four-node-20261109` owns the isolated lifecycle extension and CPU checks. Native36-GPU memory, mixed weight sync and throughput remain unverified. The existing scoring-lifetime observer isolates all installation and per-forward errors through its `soft` method; it is not an auxiliary hard gate for a≥32-GPU run.

The restriction has now been removed by`46e7b292` in the isolated worktree. The four-node lifecycle keeps one trainer head and supervises ranks1–3;122 affected tests PASS. The broader related run records171PASS,12SKIP and one existing local parser failure for`--sglang-enable-prefill-weight-versions`. That broader run is not an all-pass result; the pinned worker image's native path remains the relevant runtime check. Exact commands and failure are in`task_memory/task_2026-11-09_profile_h800_preparation/test_report_2026-11-09_four_node_rollout.md`in the preparation worktree.

The separate length launcher commit`8c9537bf` passes53 launcher+7 related tests, using explicit`context_tokens`, `prompt_tokens` and`response_tokens`. Its old source-input wiring still requires parentTicket02 integration afterD1/D22; neither these commits nor the36-GPU YAML is currently a complete formal-run configuration. The historical Running receipt is`evidence/upstream-h200-length-checkpoint-20261109.json`; the terminal refresh follows below.

## Upstream prerequisite failure 2026-11-09T07:56Z

The previous Running observation is superseded. Direct personal Python API read at07:56:39Z reports job`exp-1109-144110-764758` Failed, finish07:47:18Z. Exact replica`exp-1109-144110-764758-student-cfcd2084` exits1 at07:47:04Z; platform cleanup subsequently stops the other student and teacher with`Some critical tasks failed.` The collector verifies creator`i-fengyicheng` and replica ownership by RJob UID`fa85b2a7-f48c-4ac5-8a06-402113aa874f`.

The native student log records:

| UTC | Observation | Source log line |
| --- | --- | --- |
|07:34:31.721|Initial`update_weights` starts on eight trainer actors|2902–2904|
|07:34:32|A colocated`/update_weights_from_tensor` request returns200|2921|
|07:34:31|Dedicated-engine custom NCCL group initialization reports world size9|2936|
|07:44:31.736|The same`update_weights` fails with`elapsed_s=600.0`, followed by`TimeoutError`|3063–3087|
|Fatal stack|`train.py:169` initial weight synchronization, before the rollout/training loop|3205–3213|

This establishes the failed stage and zero successful optimizer updates. It does not establish why synchronization stalled, nor a GPU OOM, network fault, or manual stop. No new256-turn admission or scoring-capacity acceptance was obtained. The next prerequisite is a cause-based synchronization repair followed by the unchanged native capacity checks.

Evidence: `evidence/upstream-capacity-status-20261109T0755Z.json` and `evidence/upstream-weight-sync-timeout-20261109.json`. The latter retains16 decisive native log lines, filtered exact platform objects and query limitations. The complete native log remains at`/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/capacity-expanded/r256/student/A/exp-1109-144110-764758-rank-0.log` (6,788,149 bytes). Bounded read-only SSH extraction used the corresponding`/mnt/ws-jfs/ycfeng` path; the line-numbered local excerpt is`/data/ycfeng/tmp/agent-opd-image/d1-d22-status-20261109T0755Z/native-failure-excerpt.json`. No source or runtime parameter was changed.

Exact platform collector command, after the runbook's personal proxy/auth initialization:

```bash
timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
  exp-1109-144110-764758 \
  --replica exp-1109-144110-764758-student-cfcd2084 \
  --expected-creator i-fengyicheng \
  --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
  --start 2026-11-09T07:43:00Z --end 2026-11-09T07:48:00Z \
  --timeout 15 \
  --output /data/ycfeng/tmp/agent-opd-image/rca-exp-1109-144110-764758
```

Environment: Python3.10.6, brainpp2.8.6. Collector exit1: six event/log/DeepScan queries succeeded, while both all-operation audit queries raised`ReadTimeout` after15s. No existing DeepScan flow was returned. Failed/empty query coverage does not exclude events; manual-stop actor/request time remainUNKNOWN. The business timeout is independently present in the retained native log. Read-only diagnosis owner:`profile-initial-weight-sync-20261109` (`ses_e40a9a62effejB0VqD42HkARmR`); no replacement GPU job has been submitted.

Documentation verification uses the existing two commands above. The first check found two new links whose anchors omitted the heading's punctuation-derived hyphen; the heading was simplified before rerunning. Final result:24 files,6 tickets,76 links,23 anchors,zero errors; `git diff --check` PASS. This is a documentation correction, separate from the native job failure.
