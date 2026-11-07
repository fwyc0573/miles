## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Close the full-task Spec P2 using actual 200-step counts and pinned native normalization; correct the follow-up stale-report Nit and confirm C monitoring. |
| 2026-11-07 | Add user-selected full-task Standards/Spec review; reopen one original training-evidence subgate and record parent archival/monitoring corrections. |
| 2026-11-07 | Record independent A final review: no actionable findings, with numerical/training/inference scope limits preserved. |
| 2026-11-07 | Record B final phase review, two P2 delivery/evidence gaps, remediation and targeted closure. |

# Final pair acceptance reviews

## Full task — user-requested review at69f3cda5

Fixed comparison: `git diff 5c2e44635298675167c7c55e067dcb294f9e9fa9...69f3cda52dd7ea59202f560fedc6cbcfe1679ad9`,44 commits and42 source/test/repository-document files. Original specification is requirements/plan/design. This broader review supersedes the blanket A/B completion statement below, while retaining the earlier reviews' verified numerical, update, HF and two closed delivery findings.

### Standards

Native reviewer `ses_e4954d0c7ffe7Ogcy2zKCRRkSk` / `QWEN-FULL-REVIEW-STANDARDS` inspects all42 diff files and applicable repository rules:0 correctness findings,0 Nits, no actionable judgement smell. Static review only, with existing reported tests; no runtime execution or independent large-JSON audit. No speculative refactor is requested.

### Spec

Native reviewer `ses_e49547f14ffe8iDT1zTLSqozZC` / `QWEN-FULL-REVIEW-SPEC` identifies **P2, INCOMPLETE**: D12 explicitly requires native original-token global-denominator verification, and design requires per-step target token counts. The actual loss-memory probe exercises a SUM and does not establish final distributed scaling; the completion archive acknowledges missing step counts/replay. This is missing verification, not an established arithmetic defect. Parent reopens only this subgate and delegates independent existing-dump target counting and native reduction verification. Exact post-TIS survivor counts are not added as a new acceptance condition. No confirmed implementation bug or scope creep is found.

### Parent archival and operational findings

- Current plan contradicts actual final A/B artifacts and post-training storage inventory by retaining obsolete no-final-HF/10.456GiB statements. Corrected to authoritative report links while historical receipts remain unchanged.
- At15:43:54Z C is stillPending, but original launcher PID3578129 is absent and no matching local submitter is found on the same hostname/NFS source. The original shell output is no longer present, so its exit cause remains UNKNOWN. Restore monitoring of the existing job with native `RJobWorkers.wait`; no duplicate submission or platform mutation. Verify the new monitor receipt and process before closing this operational finding.

### Verified follow-up and closure — 2026-11-08

- **Standards follow-up:** same reviewer inspects both new manual probes and their reports. No correctness defect or actionable judgement smell; one Nit under `.agents/rules/single-source-of-truth.md` identifies a stale pinned-runtime-pending statement. Parent updates the native-normalization report with the exact PASS receipt and independent terminal/config evidence, preserving historical CUDA limits. The Nit is closed by direct document/receipt comparison. This report edit occurred concurrently with review, explaining the earlier snapshot.
- **Spec follow-up:** same Spec reviewer first independently inspects the native source/call-body seams, actual A/B flags and eight-rank pinned result. D12 semantics PASS: final post-reduce/scaling gradients use54 original targets rather than29 survivors, with1.095e-7 max error and a2.714 wrong-denominator distance. Historical CUDA buffer replay is not an original acceptance condition.
- **Actual target audit:** `exp-1108-002213-053180` gives200 PASS rows/1600 completions, A237618/B201819 original targets, complete0–99 positions and every-step native/original/DP/CP equality. No fully originally masked samples or eligible nonfinite entries. The reviewer independently recomputes the full receipt's per-step fields and checks source guards for duplicate/missing identities, DP ownership, microbatches and debug consumption. **Original Spec P2: CLOSED for A/B; no remaining actionable finding.** The review does not claim to reload every cloud tensor independently.
- **Parent archive verification:** lossless gzip round-trips byte-for-byte to the full final JSON; the compact JSON/table retains all200 step counts and DP subtotals. Original INCOMPLETE/failed receipts remain unchanged. Formatting/lint checks pass for the two new probes. Their logic is unchanged by formatting.
- **C monitoring:** the16:23:48Z exact personal API read confirms the same queued UID and live reattached PID851709; original-launcher exit cause remains UNKNOWN. Queue availability is8H800 against24 requested. No job is duplicated.

Canonical repair commands and receipt paths: `test_report_2026-11-08_review_fixes.md`, `test_report_2026-11-07_training_token_audit.md` and `test_report_2026-11-07_native_token_normalization.md`. This closes P3-review and A/B's reopened evidence subgate. C/P4 remain incomplete, as do explicitly deferred NCCL-direct and optional memory work.

## B — QWEN-P3-B-FINAL-REVIEW

Reviewer: native `reviewer`, session`ses_e49d0d769ffe01H8jNWPttGxIu`. Scope is B's actual100-update H200 run and final text-HF acceptance, against requirements/plan/design; no branch-wide code review, platform access, commands, tests or edits. Parent owns runtime observations. Changed deliverables are task reports/status documents and generated receipts/plots; no production code changed in this completion phase.

Inspected artifacts: `test_report_2026-11-07_training.md`, `test_report_2026-11-07_hf_reload.md`, `test_report_2026-11-07_B_monitoring.md`, the completion/native reload JSON and log, platform and package receipts, and local worker/native CLI receipts for`exp-1107-173758-806531`. The reviewer supports D17's1 discarded +100 accepted update accounting, all six original-denominator D8 checkpoints and final-HF binding to planned99/version100 rather than the final restore. No new D17/D8/HF-binding correctness defect was found.

| Initial finding | Effect | Remediation | Follow-up |
| --- | --- | --- | --- |
| P2: only synthetic loss/gradient plot qualification; actual D14 per-step curves/windows absent | P3-B was prematurely marked complete despite correct numerical/HF gates | Extract100 settled native loss/pre-clipping-grad points, exact publication/counter mapping, recorded LR/PPO/TIS and length metrics; plot with unchanged existing plotter; compare updates1–20 vs81–100 | **CLOSED**: `test_report_2026-11-07_training_plot.md`, `evidence/B-training-steps.{json,md}`, `evidence/B-training-curves.png` |
| P2: cited HF platform receipt stillRunning | In-process PASS and parent completion notification lacked a separately archived terminal platform receipt | Preserve allocation snapshot and add personal API terminal readback for the same run | **CLOSED**: `evidence/final-hf-reload-B-platform-terminal.json`, observed13:31:19Z; job/replicaSucceeded, finish13:21:28Z, no stopTimestamp |

Targeted follow-up confirms both P2 findings closed and no new actionable issue in the inspected remediation. Actual generated response/full-input counts are explicitly mean×8 derivations, not original-mask or post-TIS denominators. Native gradient clipping activity is threshold-derived, not a measured coefficient. Early/late windows are retrospective and do not establish learning improvement. The independent raw distributed-normalization replay and full800-completion tensor audit were not performed; these limits are recorded and are not reasons to reopen the two closed findings.

B can close after this delivery/evidence remediation. A/C remain separately subject to their own runtime, numerical, curves and final-HF evidence.

## A — QWEN-P3-A-FINAL-REVIEW

Reviewer: same native reviewer session, independent A scope. Inspected requirements/plan/design; A completion and business receipts; actual100-point JSON/table/PNG and `test_report_2026-11-07_A_training_curves.md`; independent final-HF JSON/log; package, hardware/source allocation and separate terminal receipts. No production review, commands, tests, platform access, tensor/token replay or delegation; B was not reopened.

**No actionable findings.** Evidence supports A's original100 successful/0 skipped budget (earlier aborted attempts0), all six24-sample original-denominator D8 checkpoints, and final planned99 ID`defc4f8a67da479bb282ddb735b99bbe`/version100. Final-HF receipt verifies822 before/after decoder checksums,24 complete inputs/5197 tokens, mean0.0084664004, actual generation and zero remaining children; the independent terminal receipt confirms job/default replicaSucceeded, finish13:45:48Z.

D14 actual100-point curves and early1–20/late81–100 comparisons are complete. The initial synthetic-block selection was explicitly excluded and corrected; no overclaim was found in clipping/TIS or learning interpretation. Exact target/survivor counts, independent distributed-normalization replay and actual post-clipping norms remain unverified; teacher semantics are source/launch-derived. Numerical and execution success do not prove convergence or capability improvement. C remains outside this review.
