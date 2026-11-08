## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Complete D1–D10, final checks and explicit whole-document freeze; leave runtime tickets unstarted. |
| 2026-11-08 | Start source-backed documentation landing and the one-question-at-a-time interview. |

# Progress

## completed

- Read Miles `AGENTS.md` and every Markdown rule under `.agents/rules/`; loaded `grilling` and `domain-modeling` as requested.
- Recorded raw requirements in the new task directory. Inspected both worktree HEADs and the existing A/B completion archive.
- Confirmed that prior A/B qualification uses different data/budgets from this task, and that the reference task's original spec contains superseded settings. Exact current behavior is being traced from code and later decisions.
- Inspected local Git status. The modified old-task `future.md`, untracked historical evidence/probes, `.cortexkit/`, and `.serena/` predate this work and are outside this documentation change.
- DOC-DATA: completed, session `ses_e48b56aebffeb4as6aCIwmUUZN`. Integrated source-backed default-loader findings in spec S0/S3. Rejected the report's proposed “924-prefix shortage” blocker: the user explicitly requires the raw default loader, which permits epoch wrap and does not use that old population. The report's opening claim of default shuffle also contradicted its own decisive loader analysis; parent verified sequential/wrapping behavior directly.
- DOC-EVAL: completed, session `ses_e48b53c70ffeTtM6Ps0hWFNNrk`. Integrated100-question/FourAttempts and lifecycle differences. Parent verified the requested replay worktree against the follow-up fixed-LR worktree: protocol/config equal; evaluation module differs only in probe TimeoutError catching; SWE runner differs and needs explicit pinning. Corrected report overstatements: existingQwen packaging already records identity, native successful optimizer counters exist, and native partial-step scheduling must be assessed before adding a replacement.
- DOC-MILES: completed, session `ses_e48b51640ffedQIqdjLBcUdiCO`. Integrated reuse/counter/count gaps. Parent additionally verified native OPD logging uses modified TIS masks and rejected an unmeasured13–17day runtime estimate based on old data and uncached steps. Exact TIS counts are already requested; rate-only is not a new user option.
- DOC-REVIEW: completed, session `ses_e48b02733ffejx5fyyB0aqqlby`. Three P2 document findings were corrected: no premature normalization choice, full/r256-specific bank acceptance, and deletion of HF200 after successful evaluation under the original request.
- DOC-OPTIMIZER: completed, session `ses_e48a242cfffe7vL5YD4O8eZAe4`, wrote`optimizer_research.md`. Official original optimizer unconfirmed; direct Miles Qwen3.5 OPD/RL recipes and verl4B←35B-A3B supportAdamW. Primary reviewed the artifact, checked localQwen recipe and adoptedMiles adam/AdamW semantics, betas(0.9,0.98),eps1e-8,wd0.1 underD3.
- Final source audit: resolvedQwen preserve-thinking template, independent default cursors, actor/PPO-vs-TIS ratios, actualbenchmarktop_p0.95, originalSWE submodule commit1af09e5f, and taskcloudroot. The reference submodule is not checked out, but its commit objects were inspected from the later submodule repository; missing file is an implementation setup prerequisite.
- DOC-REVIEW follow-up returned twoP2 findings: missing explicit gradient objective and stale eight-ticket validation. Parent traced native objective/advantages/PPO implementation and wroteS4's formula/detach contract; the final document check below replaces the stale graph algorithm. Previous3findings remain closed.
- Final user confirmation: “确认冻结（推荐）”, accepting D1–D10, source-backed spec and all nine tickets as the documentation deliverable. Requirements/spec/plan/summary now record DOCS_LANDING_COMPLETE.

## in-progress

- None. Documentation landing is complete; implementation and experiment tickets have not started.

## pending

1. Subsequent implementation begins at ticket01. Tickets02/03 follow01; four formal cells and baseline follow their own graph edges; finalcomparison waits for allfive results. All runtime tickets are unstarted.

## Interview and document iterations

- Draft specification, dependency plan and8 tickets landed; initial link/structure/budget checks passed (see test report).
- D1 actual user answer: “有效子集继续（推荐）”. Updated requirements, conditional budgets, valid-bank replay and failure boundaries accordingly.
- D2 actual user answer: “筛选前均值（推荐）”. Defined the primaryKL as a pre-TIS original-token mean of current-student minus teacher log probability; preserved native post-TIS logging and replay sampling caveats.
- D3 actual user answer requests official/community optimizer research. Neither proposed optimizer was selected; research delegated to one artifact owner while source integration continued independently.
- D4 actual user answer: “Steptron双层筛选（推荐）”. Recorded token[0.5,2], answer-geometric[0.9897,1.001], binary retained weight1 and exact intersection counts. Primary traced the effective source override and loss implementation; this is not the old Miles ratio-weightedTIS.
- D5 actual user answer: “剩余128K额度（推荐）”. Recorded complete prompts<131072 and response budget131072−prompt length; previous8192 response/prefix reservation is not inherited.
- D6 actual user answer: “采用参考规则（推荐）”. Recorded1800s acquisition and minimum231/256, below-minimum attempt termination, and independent healthycell continuation.
- D7 actual user answer: “结束当前cell”. First globally zeroTIS-survivor batch terminates thatattempt with evidence and no synthetic successfulupdate; othercells continue. Formal200-row acceptance remains a target, not a reason to fabricate completion after an approved stop.
- D8 actual user answer: “增加一次基线（推荐）”. Addedticket09 for one shared original4B100×4 baseline; total planned evaluation becomes17points/6800attempts. Finalticket08 waits for09; formal04–07 do not.
- D9 user continuation: “确认，继续” following the resource-scope question; acknowledged as the recommended personal aggregate56nonpreemptibleH200 ceiling, including other tasks and allsubmitted nonterminal roles.
- D10 actual user answer: “采用此规则（推荐）”. Preserve incompleteHF/results, recover onlymissing same-task/seed slots within the same72h deadline, stop/report on expiry and leave healthy training running.
- Source evidence establishes default11-source sequential assistant-turn loading with epoch wrap. Raw-data availability remains an implementation prerequisite, not a924-prefix budget blocker.
- Optional phase DOC-REVIEW inspected changed-file list and reported threeP2 documentation issues; all three were corrected before further interview. No code/runtime approval was inferred.

## Commands and observations

- `git status --short`, `git branch --show-current`, `git rev-parse HEAD`, and `git log -1 --format='%h %s'` in the Miles worktree: branch/HEAD recorded in requirements.
- `git rev-parse HEAD && git branch --show-current` in the reference worktree: branch/HEAD recorded in requirements.
- Local `python --version` was not used successfully: invoking `python` for rule-file reads failed with `command not found`; repeated the read using `python3`. `python3 --version`: **Python 3.10.6**.
- No experiment runtime verification has been performed during documentation landing.
- Source audit used`git ls-tree HEAD third_party/swe-agents` in the reference worktree and`git diff 1af09e5f90f55f6fbce5f71efe7da0030a2e126e 9919c7a3338deb95d5ce82e605ebda48c74cdda0 -- src/swe_agents/models/step_align.py src/swe_agents/cli/run.py` in the later submodule. Diff only adds onecontext-limit error condition in the inspectedfiles. Direct reads confirmed`configs()` onlyoverrides model/context/endpoint/seed, leavingtop_p0.95.
- A patch rejected one substring-only context line and made no changes; reapplied with the exact full line successfully. No unresolved edit error.
- Finalpre-confirmation Python3.10.6check passed:17Markdownfiles,9tickets,25local links,1anchor,0errors. It parsesactualticket/plan edges, accepts08←09 and detectsrealcycles. Budgets:800updates,16HFs,17evaluationpoints,6800attempts; exactcommand/outputin`test_report_2026-11-08_docs_landing.md`.
- Final`check-progress` updated`review.md`: no mainline drift or remaining document defect. Whole-document confirmation subsequently passed;01is the next implementation frontier and all nine runtime tickets remain unstarted.
- Post-confirmation check reran the exact saved validator after frozen status updates:17files,9tickets,25links,1anchor,0errors and unchanged correctDAG/budgets. Re-read finalrequirements; verified an empty Git index and a glossary diff containing only this task's three new terms. This archive is scoped to the17task documents andGLOSSARY.md.
