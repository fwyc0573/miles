## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record separate Standards and Spec reviews, fixes, and the upstream gate. |

# Branch-base review

Scope: `git diff 20d0b3f4...0e94c522`, 35 changed files, 21 commits. The user selected the branch creation point. Exact initial diff and commit list are retained at `/data/ycfeng/tmp/agent-opd-image/review-base-20d0b3f4-0e94c522.diff` and `review-base-commits.txt`; Git retains both refs. Reviewers initially inspected the changed files and refs, not a complete fixed-ref diff; their findings are valid targeted findings, not a full-diff PASS.

## Standards

Reviewer: `ses_e4373800affezhqaC06Ftzyn1p`, task `profile-standards-20261109`.

| Finding | Severity | Remediation |
| --- | --- | --- |
| Reusable synthetic/mutation scripts exist only under temporary storage. | P3 | Retain the scripts under `tests/manual/agent_opd/` and link reproducible commands. |
| The SWE synthetic audit report points to a command absent from progress. | P3 | Record the complete audit invocation. |
| Profile docstring claims observations alone support rebuild; code needs both files. | P3 | Correct the description to match `rebuild()`. |
| Requirements still declare documentation landing despite the freeze. | P3 | Fixed: current phase and new execution authorization recorded. |

Four findings, all P3; no additional smell finding. Verification and fixed-ref rereview are recorded in the dated test report.

## Spec

Reviewer: `ses_e43738006ffeim4QCGXqygBMha`, task `profile-spec-20261109`.

| Finding | Severity | Remediation |
| --- | --- | --- |
| Disk hash checks can certify a different preimported module under the same name. | P2 | Reuse only the exact cached module object previously loaded from the matching verified bytes. Unknown/mismatched imports fail explicitly. |
| First-user text hash is reported as a SWE task identity. | P2 | Report exact-prompt groups separately; task identity and per-update task count remain unverified/null. |
| Arbitrary historical conversation entries lack a public ratio query. | P2 | Add stored-entry lookup and retroactive baseline-ratio queries with regression evidence. |
| B startup is gated on A's auxiliary profile verdict passing. | P2 | Require native first-update success and completed inspection; auxiliary errors mark profile unverified and do not stop healthy training. |
| N=8 is claimed to equal every conversation's first entry. | P3 | State the exact aligned/full-block condition; preserve the earliest-N-observation equation. |

Five findings: four P2 and one P3. The upstream missing implementation is explicitly blocked work, not a newly discovered defect.

## Upstream prerequisite

Read-only reviewer: `ses_e43737fe8ffe4iK1j8uAE81u0C`, task `profile-upstream-20261109`. Inspected `agent-opd` at `f33546f4` plus identified local, uncommitted late evidence.

- Patch `cee3bfa5` has a historical GPU contrast: the fixed scoring path reached backward after 31 scoring microbatches per rank, then was externally stopped for `release_quota`; no successful optimizer ACK or second scoring was observed.
- New DeepSWE attempts reached 206 and 224 valid slots. D12 `exp-1109-010244-280221` reached 227/256, below the 231 minimum, with zero updates.
- Therefore D1/D22 remain **NOT MET**. No merge, Ticket02 implementation, Ticket03 integration, or formal run is accepted by this review. Other-session uncommitted edits remain untouched.

Decisive current upstream artifacts: `/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/capacity-lifetime-gpu-partial.json`, `test_report_2026-11-09_round_robin_acquisition.md`, and `tickets/02-replay-training-and-metrics.md`.
