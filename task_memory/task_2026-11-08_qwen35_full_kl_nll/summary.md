## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record the expanded upstream attempt failing before rollout at initial weight synchronization. |
| 2026-11-09 | Record D33 H800 preparation and D34 input/request budget implementation; reopen only the changed source length verification. |
| 2026-11-09 | Accept completed Ticket01 source audit/parity and refresh the remaining upstream-only integration gate. |
| 2026-11-09 | Archive the review repair milestone and ongoing, prerequisite-limited execution. |

# Review and input milestones — integration waits for upstream

The user selected `20d0b3f4` as the review base for `agent-opd-image`, initially at `0e94c522`. The draft's implementation phase, inherited contract, statistical interpretation, dependency checkpoints, and soft-gate behavior have been corrected. D33 subsequently authorizes H800/codesign without a task GPU-count cap; D34 sets112K inclusive prompts and16K completions within unchanged128K training/rollout context. Other scientific decisions and D1/D22 remain in force.

Main repair commit: `a0b0d113`. Both independent remediation reviews are complete. All original findings are closed; the final Standards P3 was resolved by retaining and verifying the unchanged document-check script. No review finding remains open.

## Deliverables

- Task contract and execution graph: `spec.md`, `requirements.md`, `plan.md`, and `tickets/01-*.md` through `tickets/06-*.md` in this directory.
- Review evidence: `review.md`, `checkpoint_2026-11-09_review.md`, and `test_report_2026-11-09_review_execution.md`.
- Input fixes: `tests/manual/agent_opd/swe_inputs.py` verifies cached native code identity; `audit_swe1003_sources.py` reports exact-prompt groups without inventing SWE task identities.
- Profile fixes: `tests/manual/agent_opd/distillation_profile.py` exposes historical conversation entries and baseline-relative values; both JSONL files are documented as necessary for rebuild.
- Reproducible checks: `tests/fast/test_swe_input_pins.py`, extended `tests/fast/test_distillation_profile.py`, and retained synthetic/mutation scripts under `tests/manual/agent_opd/`.
- CPU execution: `tests/manual/agent_opd/submit_swe1003_audit.py` and `source_audit_config.json`; inputs are read in place without copies.

## Observed validation

- Affected fast tests: 15 passed, including unknown native imports, changed pins, historical queries, baseline boundaries, and partial-write isolation.
- Synthetic audit and native parity worker commands: PASS. Updated same-prompt/different-instance fixture: PASS; task identity/counts remain unverified/null.
- Synthetic profile: 200 updates, 51,200 observations, 589 conversations; mean record cost 1.460 ms/update, all-conversation query 1.316 ms, profile memory 12.943 MiB.
- Document links, ticket DAG and arithmetic checks: 73 links, 22 anchors, zero errors using the retained `tests/manual/agent_opd/check_profile_docs.py`. See the test report for exact commands and environments.

## Execution and open work

| Ticket | Status at this milestone |
| --- | --- |
| 01 | Original source audit/parity accepted; D34 budget implementation CPU-verified, updated112K full-source audit pending. |
| 02 | Blocked by D1/D22; no implementation or upstream merge begun. |
| 03 | Pure module fixes verified on CPU; native-count checks and integration blocked by02. |
| 04 | Blocked; no A/full formal run submitted. |
| 05 | Blocked; requires launch prerequisites and actual A first-update inspection. |
| 06 | Blocked by formal-run evidence. |

At the2026-11-09T07:56Z refresh, upstream`agent-opd` is at`c52991ac` without capacity acceptance. Expanded attempt`exp-1109-144110-764758` failed at07:47:18Z after its initial trainer-to-rollout weight synchronization timed out at600s. The fatal call precedes rollout collection and optimizer updates; no256-turn acceptance follows. The synchronization stall's underlying cause remains under diagnosis. Earlier227/256 acquisition and historical partial scoring remain unaccepted. D1/D22 therefore still block merge and this task's training integration.

CPU job creator`i-fengyicheng`,0 GPUs,8 CPUs,32000 Mi memory, exact image and current-host NFS source were verified in`evidence/source-audit-admission-20261109.json`. Terminal receipt`evidence/source-audit-terminal-20261109.json` confirms job/replica Succeeded, finish00:24:08Z and the worker completion marker. Real-source output, source identities/counts,512 native parity draws and2,048 interleaved draws are accepted in`test_report_2026-11-09_source_audit.md`.

Eligible-turn median90 before length filtering retains D26's32×8. The128K audit rejects27.51% of eligible turns; the32×8 simulation has median span7 updates and17/745 conversations spanning≥11 updates. These are CPU scheduling measurements, not runtime trend coverage. All first-source messages omit`preserve_thinking`; the Qwen configuration explicitly sets it true. Native task identity remains unverified/null. No benchmark, HF checkpoint or formal training result is claimed.

Those128K prompt-filter statistics are historical afterD34. The new request/input contract passes33 affected primary fast tests, real pinned GLM512/2048 checks and synthetic SWE/audit workflow checks; see`test_report_2026-11-09_length_budgets.md`. New full-source output is isolated under`evidence/source-audit-112k-20261109/`.

H800 resource changes are isolated in`agent-opd-h800-capacity`: explicit-null admission`1ae93261`, native length argv`8c9537bf`, and four-node lifecycle`46e7b292`. Planned per-pair layout is36 GPUs, including8TP4 rollout engines and4TP4 teacher GPUs. Individual-logits size decreases underTP4, but H800 runtime memory/throughput is unverified. The upstream07:45:51Z Running snapshot is superseded by the failure above. No H800 native capacity job has been submitted by this task.

The new112K CPU audit`exp-1109-154414-275606` isRunning under input/audit implementation`438d25fc`; creator,0GPU/8CPU,image,mount and worker budget argv were verified. Outputs and terminal acceptance remain pending. Four-node affected tests pass122cases; broader related tests retain171PASS/12SKIP/one existing local SGLang parser failure, so that broader suite is not claimed all-pass. Parent/isolated preparation integration remains pending until the recorded upstream gate opens.
