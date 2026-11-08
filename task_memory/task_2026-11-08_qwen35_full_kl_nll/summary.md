## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Archive the review repair milestone and ongoing, prerequisite-limited execution. |

# Review repair milestone — execution remains in progress

The user selected `20d0b3f4` as the review base for `agent-opd-image`, initially at `0e94c522`. The draft's implementation phase, inherited contract, statistical interpretation, dependency checkpoints, and soft-gate behavior have been corrected. Scientific decisions D1–D32 remain in force.

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
| 01 | In progress: CPU RJob `exp-1109-031258-820360` submitted and verified Running; source audit and parity results not yet accepted. |
| 02 | Blocked by D1/D22; no implementation or upstream merge begun. |
| 03 | Pure module fixes verified on CPU; native-count checks and integration blocked by02. |
| 04 | Blocked; no A/full formal run submitted. |
| 05 | Blocked; requires launch prerequisites and actual A first-update inspection. |
| 06 | Blocked by formal-run evidence. |

The upstream `agent-opd` patch has historical partial scoring evidence, but its new-data capacity run collected only227/256 (<231), with no successful update. Its Ticket02 is not accepted. The branch is therefore not merged, and this task's training integration cannot start under D1/D22.

CPU job creator `i-fengyicheng`, 0 GPUs, 8 CPUs, 32000 Mi memory, exact image, and current-host NFS source were verified in `evidence/source-audit-admission-20261109.json`. Its local launcher remains alive. Real-source output, D26 distribution review, source `preserve_thinking` values, parity, and terminal-state verification are unfinished. Submission and synthetic PASS are not real-source acceptance. No benchmark, HF checkpoint, or formal training result is claimed.
