## Modification History

| Date | Change |
| --- | --- |
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
| Upstream native gate | Actual capacity evidence, not submission/startup alone | `exp-1109-144110-764758`: Starting at07:23:41Z; teacher Running, both student replicas Starting | NOT YET MET |
| Unlimited allocation | No manufactured numeric ceiling | Candidate`gpu_policy.json` has explicitnull; old integer-only reader needs the isolated change below | PENDING |
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
