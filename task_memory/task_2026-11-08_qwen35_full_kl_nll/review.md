## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record Ticket03 fixed-diff Standards0/Spec0 review and explicit final profile configuration; A formal runtime acceptance remains pending. |
| 2026-11-10 | Record separate Standards and Spec phase reviews of Ticket02 commit6129aefe; neither axis has findings, GPU/profile acceptance remains pending. |
| 2026-11-09 | Complete fixed-diff D33/D34 preparation review across parent and isolated H800 worktrees; no new findings, runtime/integration gates retained. |
| 2026-11-09 | Record separate Standards and Spec reviews, fixes, and the upstream gate. |

# Ticket03 phase review — 2026-11-10

Scope: immutable`git diff ba3cb696...15186817`, one commit/seven files; full artifact`/data/ycfeng/tmp/agent-opd-image/t03-profile-fixed-review-20261110.diff`. Both reviewers also inspected the current`formal_config.json`, with explicit profile10/10/8 and full protocol. Neither reviewer reran tests or accessed the platform.

## Standards

Reviewer:`ses_e3ea07cacffe3xcqCOUT4dnitM`, task`profile-t03-standards-review-20261110`. **No findings.** Bank-bound identity/finish reporting, typed profile defaults, centralized invalidation and sole ownership of paired persistence follow the documented standards. Auxiliary isolation does not introduce retry or fabricated values.

## Spec

Reviewer:`ses_e3ea07d9cffe9mQZOCTx7gD5RV`, task`profile-t03-spec-review-20261110`. **No findings.** Native training notifies the original rollout plugin before clearing the bank, including the final ACK. Only successful ACKs append observations; canonical UID/per-UID tokens/native counts/macros/estimator and bank-bound finish reports are checked. Initialization, mismatch and write errors permanently suppress profile append/derivation while native counters continue. Historical entries, baseline boundaries, sparse trends and paired-file rebuild match S4–S7.

**Summary:** Standards0 / Spec0 actionable findings. Both axes support CPU integration readiness with the recorded201-case suite ([report](test_report_2026-11-10_profile_integration.md)). Final configuration/dry-run evidence is in[the formal configuration report](test_report_2026-11-10_formal_configuration.md). A's actual first successful update/D16 and both200-update native/profile terminal verdicts remain unverified; no extra profile GPU smoke is required.

# Ticket02 phase review — 2026-11-10

Scope: immutable`git diff 4863e68e...6129aefe`, one commit and eight changed files. Complete diff artifact:`/data/ycfeng/tmp/agent-opd-image/t02-per-turn-fixed-review-20261110.diff`; both refs are committed. Reviewers inspected this entire diff and relevant native scoring, scheduling, metadata and ACK dependencies. Concurrent Ticket03 changes were excluded. Tests were not independently rerun by the reviewers.

## Standards

Reviewer:`ses_e3ea07cacffe3xcqCOUT4dnitM`, task`profile-t02-standards-review-20261110`. **No findings.** Necessary native tensor reuse and compact loss/ACK transport provide the required capability without a new forward. Estimator configuration retains a single native owner; nullable source metadata is preserved without mutation. Rank-local auxiliary failures become error payloads before the collective. No actionable documented-standard violation or baseline smell was identified.

## Spec

Reviewer:`ses_e3ea07d9cffe9mQZOCTx7gD5RV`, task`profile-t02-spec-review-20261110`. **No findings.** Native pre-TIS RKL, held pre-optimizer student NLL, original masks, CP reduction and one TP/PP contribution match S3. Native sample-index transport maps to canonical source UIDs; macros derive from the same rows; count/UID/CP inconsistencies mark auxiliary evidence unverified without skipping collectives or changing mandatory D7 handling. Rows remain in the ACK and are excluded from trainer JSONL/stdout.

**Summary:** Standards0 / Spec0 actionable findings. CPU implementation-ready is supported by static review and the recorded110-case run plus79 final affected checks ([report](test_report_2026-11-10_per_turn_sums.md)); this is not Ticket02 GPU acceptance. Native128K`bshd`, actual NCCL overhead and256-turn runtime cost remain unmeasured. Ticket03 rollout persistence, permanent suppression after failure and formal A-first-update checks remain separate acceptance work.

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

**Remediation review, 2026-11-09:** the same Standards reviewer inspected the fixed-ref diff, commit list, complete repair diff, submitter/config, retained scripts and current documents. All four original findings are closed. One additional P3 remained: the documentation checker was still temporary-only. The primary retained it byte-for-byte as `tests/manual/agent_opd/check_profile_docs.py`, verified equality with `cmp`, updated the report command, and ran the retained copy: 73 links, 22 anchors, zero errors. That last fix was verified by the primary, not sent for another review. No Standards finding remains open; real-source and GPU acceptance remain outside this verdict.

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

**Remediation review, 2026-11-09:** the same Spec reviewer inspected the immutable initial diff, 21-entry commit list, repair hunks, corresponding code and receipts. All five findings are closed, with **zero remaining actionable Spec findings**. The CPU-ready / GPU-accepted split removes the dependency cycle while preserving D1/D22. This verdict covers the reviewed changes; it does not certify real-source scan completion, native task identities, prompt-length assumptions or GPU integration. The reviewer did not rerun tests or perform platform operations.

## Upstream prerequisite

Read-only reviewer: `ses_e43737fe8ffe4iK1j8uAE81u0C`, task `profile-upstream-20261109`. Inspected `agent-opd` at `f33546f4` plus identified local, uncommitted late evidence.

- Patch `cee3bfa5` has a historical GPU contrast: the fixed scoring path reached backward after 31 scoring microbatches per rank, then was externally stopped for `release_quota`; no successful optimizer ACK or second scoring was observed.
- New DeepSWE attempts reached 206 and 224 valid slots. D12 `exp-1109-010244-280221` reached 227/256, below the 231 minimum, with zero updates.
- Therefore D1/D22 remain **NOT MET**. No merge, Ticket02 implementation, Ticket03 integration, or formal run is accepted by this review. Other-session uncommitted edits remain untouched.

Decisive current upstream artifacts: `/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/capacity-lifetime-gpu-partial.json`, `test_report_2026-11-09_round_robin_acquisition.md`, and `tickets/02-replay-training-and-metrics.md`.

## D33/D34 preparation phase

Reviewer:`ses_e40bbe487ffeqJc4LSyAlspkFg`, task`profile-h800-length-review-20261109`. Fixed ranges: parent`2d695ba0..438d25fc`; isolated preparation`c52991ac..46e7b292`, including nullable admission`1ae93261`, native lengths`8c9537bf` andfour-node lifecycle`46e7b292`.

Inspected artifacts: input/audit/checker/synthetic code andtests; budget/receipt, SWE argv andQwen worker lifecycle code/tests; parentrequirements/spec/plan/tickets/configs/reports; preparation task reports. Exact diffs retained at`/data/ycfeng/tmp/agent-opd-image/profile-h800-length-parent-438d25fc.diff` and`profile-h800-length-preparation-46e7b292.diff`; their Git ranges remain reproducible. The initial review lacked exact diff access; the follow-up read both artifacts against inspected current code and closed that coverage limitation.

**Result: fixed-diff phase review complete; no new actionable findings.** Inclusive112K filtering,16K completion requests, explicit-null admission andall-rank supervision align with the stated contracts. No new data copying, out-of-scope cloud write orauxiliary hard gate was identified. No test orplatform operation was performed by the reviewer.

This is not native readiness: D1/D22 remains closed; typed-input wiring/merge is deferred toTicket02;112K real-source audit isRunning butunaccepted;36-GPU H800 placement, full peak memory, mixed weight synchronization andthroughput remain unverified. The broader local related test run retains its existing parser failure andis not reported as all-pass.
