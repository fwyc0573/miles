## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record the post-freeze two-axis review and its documentation-only remediation; restore word spacing. |
| 2026-11-08 | Complete D1–D10, final checks and explicit whole-document freeze; leave runtime tickets unstarted. |
| 2026-11-08 | Start source-backed documentation landing and the one-question-at-a-time interview. |

# Progress

## completed

- Read Miles `AGENTS.md` and every Markdown rule under `.agents/rules/`; loaded `grilling` and `domain-modeling` as requested.
- Recorded raw requirements in the new task directory. Inspected both worktree HEADs and the existing A/B completion archive.
- Confirmed that prior A/B qualification uses different data/budgets from this task, and that the reference task's original spec contains superseded settings. Exact current behavior is being traced from code and later decisions.
- Inspected local Git status. The modified old-task `future.md`, untracked historical evidence/probes, `.cortexkit/`, and `.serena/` predate this work and are outside this documentation change.
- DOC-DATA: completed, session `ses_e48b56aebffeb4as6aCIwmUUZN`. Integrated source-backed default-loader findings in spec S0/S3. Rejected the report's proposed “924-prefix shortage” blocker: the user explicitly requires the raw default loader, which permits epoch wrap and does not use that old population. The report's opening claim of default shuffle also contradicted its own decisive loader analysis; parent verified sequential/wrapping behavior directly.
- DOC-EVAL: completed, session `ses_e48b53c70ffeTtM6Ps0hWFNNrk`. Integrated 100-question/four-attempt and lifecycle differences. Parent verified the requested replay worktree against the follow-up fixed-LR worktree: protocol/config equal; evaluation module differs only in probe TimeoutError catching; SWE runner differs and needs explicit pinning. Corrected report overstatements: existing Qwen packaging already records identity, native successful optimizer counters exist, and native partial-step scheduling must be assessed before adding a replacement.
- DOC-MILES: completed, session `ses_e48b51640ffedQIqdjLBcUdiCO`. Integrated reuse/counter/count gaps. Parent additionally verified native OPD logging uses modified TIS masks and rejected an unmeasured 13–17 day runtime estimate based on old data and uncached steps. Exact TIS counts are already requested; rate-only is not a new user option.
- DOC-REVIEW: completed, session `ses_e48b02733ffejx5fyyB0aqqlby`. Three P2 document findings were corrected: no premature normalization choice, full/r256-specific bank acceptance, and deletion of HF200 after successful evaluation under the original request.
- DOC-OPTIMIZER: completed, session `ses_e48a242cfffe7vL5YD4O8eZAe4`, wrote `optimizer_research.md`. The official original optimizer is unconfirmed; direct Miles Qwen3.5 OPD/RL recipes and verl 4B←35B-A3B support AdamW. The primary reviewed the artifact, checked the local Qwen recipe and adopted the Miles AdamW-semantic recipe under D3; exact parameters are owned by [spec.md](spec.md#优化参数).
- Final source audit: resolved the Qwen preserve-thinking template, independent default cursors, actor/PPO-versus-TIS ratios, actual benchmark top_p 0.95, original SWE submodule commit `1af09e5f`, and the task cloud root. The reference submodule is not checked out, but its commit objects were inspected from the later submodule repository; the missing checkout is an implementation setup prerequisite.
- DOC-REVIEW follow-up returned two P2 findings: missing explicit gradient objective and stale eight-ticket validation. Parent traced the native objective/advantages/PPO implementation and wrote S4's formula/detach contract; the final document check replaced the stale graph algorithm. The previous three findings remain closed.
- Final user confirmation: “确认冻结（推荐）”, accepting D1–D10, the source-backed spec and all nine tickets as the documentation deliverable. Requirements/spec/plan/summary record DOCS_LANDING_COMPLETE.
- Post-freeze two-axis review of commit `f2f86fea` (Standards session `ses_e4658531affeyA0QT4RKm7MVRM`, Spec session `ses_e4658531affdEO4PN5SKX9XDFl`): Spec found no P1–P3 issue; Standards reported three Nits and one judgement call. The user approved the proposed fixes (“确认，继续”). Requirements D3 and the summary now link the spec instead of restating optimizer/TIS parameters; the baseline and comparison tickets were renumbered 08/09 to follow dependency order; squashed words were respaced. The judgement call (shared acceptance text in 04–07) is intentionally kept so each formal-cell ticket remains self-contained. Details in [review.md](review.md); no scientific decision or acceptance criterion changed.

## in-progress

- None. Documentation landing is complete; implementation and experiment tickets have not started.

## pending

1. Subsequent implementation begins at ticket 01. Tickets 02/03 follow 01; the four formal cells (04–07) and the baseline (08) follow their own graph edges; the final comparison (09) waits for all five results. All runtime tickets are unstarted.

## Interview and document iterations

- Draft specification, dependency plan and 8 tickets landed; initial link/structure/budget checks passed (see test report).
- D1 actual user answer: “有效子集继续（推荐）”. Updated requirements, conditional budgets, valid-bank replay and failure boundaries accordingly.
- D2 actual user answer: “筛选前均值（推荐）”. Defined the primary KL as a pre-TIS original-token mean of current-student minus teacher log probability; preserved native post-TIS logging and replay sampling caveats.
- D3 actual user answer requests official/community optimizer research. Neither proposed optimizer was selected; research delegated to one artifact owner while source integration continued independently.
- D4 actual user answer: “Steptron双层筛选（推荐）”. Recorded the token and answer-geometric bounds, binary retained weight 1 and exact intersection counts. Primary traced the effective source override and loss implementation; this is not the old Miles ratio-weighted TIS.
- D5 actual user answer: “剩余128K额度（推荐）”. Recorded complete prompts below 131072 tokens and response budget 131072 minus prompt length; the previous 8192-token response cap/prefix reservation is not inherited.
- D6 actual user answer: “采用参考规则（推荐）”. Recorded 1800 s acquisition and minimum 231/256, below-minimum attempt termination, and independent healthy-cell continuation.
- D7 actual user answer: “结束当前cell”. The first globally zero TIS-survivor batch terminates that attempt with evidence and no synthetic successful update; other cells continue. Formal 200-row acceptance remains a target, not a reason to fabricate completion after an approved stop.
- D8 actual user answer: “增加一次基线（推荐）”. Added the baseline ticket (numbered 09 at that time, renumbered 08 after the post-freeze review) for one shared original 4B 100×4 baseline; total planned evaluation becomes 17 points / 6,800 attempts. The final comparison waits for the baseline; formal 04–07 do not.
- D9 user continuation: “确认，继续” following the resource-scope question; acknowledged as the recommended personal aggregate ceiling of 56 non-preemptible H200 GPUs, including other tasks and all submitted nonterminal roles.
- D10 actual user answer: “采用此规则（推荐）”. Preserve incomplete HF/results, recover only missing same-task/seed slots within the same 72 h deadline, stop/report on expiry and leave healthy training running.
- Source evidence establishes default 11-source sequential assistant-turn loading with epoch wrap. Raw-data availability remains an implementation prerequisite, not a 924-prefix budget blocker.
- Optional phase DOC-REVIEW inspected the changed-file list and reported three P2 documentation issues; all three were corrected before further interview. No code/runtime approval was inferred.

## Commands and observations

- `git status --short`, `git branch --show-current`, `git rev-parse HEAD`, and `git log -1 --format='%h %s'` in the Miles worktree: branch/HEAD recorded in requirements.
- `git rev-parse HEAD && git branch --show-current` in the reference worktree: branch/HEAD recorded in requirements.
- Local `python --version` was not used successfully: invoking `python` for rule-file reads failed with `command not found`; repeated the read using `python3`. `python3 --version`: **Python 3.10.6**.
- No experiment runtime verification has been performed during documentation landing.
- Source audit used `git ls-tree HEAD third_party/swe-agents` in the reference worktree and `git diff 1af09e5f90f55f6fbce5f71efe7da0030a2e126e 9919c7a3338deb95d5ce82e605ebda48c74cdda0 -- src/swe_agents/models/step_align.py src/swe_agents/cli/run.py` in the later submodule. The diff only adds one context-limit error condition in the inspected files. Direct reads confirmed `configs()` only overrides model/context/endpoint/seed, leaving top_p 0.95.
- A patch rejected one substring-only context line and made no changes; reapplied with the exact full line successfully. No unresolved edit error.
- Final pre-confirmation Python 3.10.6 check passed: 17 Markdown files, 9 tickets, 25 local links, 1 anchor, 0 errors. It parsed actual ticket/plan edges, accepted the then-current `08←09` edge and detects real cycles. Budgets: 800 updates, 16 HFs, 17 evaluation points, 6,800 attempts; exact command/output in `test_report_2026-11-08_docs_landing.md`.
- Final `check-progress` updated `review.md`: no mainline drift or remaining document defect. Whole-document confirmation subsequently passed; 01 is the next implementation frontier and all nine runtime tickets remain unstarted.
- Post-confirmation check reran the exact saved validator after frozen status updates: 17 files, 9 tickets, 25 links, 1 anchor, 0 errors and unchanged correct DAG/budgets. Re-read the final requirements; verified an empty Git index and a glossary diff containing only this task's three new terms. This archive is scoped to the 17 task documents and `GLOSSARY.md`.
- Post-review revision: `git mv` swapped the two ticket files (`08-original-student-baseline.md`, `09-four-cell-comparison.md`); the post-review revision check result is recorded in the test report.
