## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Archive the completed, explicitly confirmed documentation deliverable. |

# Qwen3.5 SWE full/r256 — Documentation landing

## Status

Documentation landing is complete. The user explicitly selected “确认冻结（推荐）”, accepting decisions D1–D10, the source-backed specification and all nine tickets for subsequent implementation. Implementation and experiment execution have not started; no runtime result is claimed.

## Deliverables

All paths below are relative to `task_memory/task_2026-11-08_qwen35_swe_full_r256/`:

- `requirements.md`: original request, actual answers, authority and source identities.
- `spec.md`: four-cell protocol, default Steptron SWE loading, 200-update budget, replay/TIS/objective, metrics, HF/evaluation lifecycle and resource limits.
- `plan.md` and `tickets/01-native-swe-inputs.md` through `tickets/09-original-student-baseline.md`: nine independently verifiable tickets and their dependency graph. Ticket 09 was added after the initial decomposition; the graph defines execution order.
- `optimizer_research.md`: primary-source official/community optimizer findings and adoption of Miles AdamW semantics with explicit evidence limits.
- `progress.md`, `review.md` and `test_report_2026-11-08_docs_landing.md`: investigation, review remediation, checkpoint and exact local validation evidence.
- Repository `GLOSSARY.md`: resolved training-turn, replay-bank and experiment-cell terminology, with no implementation details.

## Experiment contract

Two teachers, 27B and 35B-A3B, each train an independently initialized original 4B student under full and r256. Each cell targets 200 successful updates; r256 uses each bank 50 consecutive times. The batch target of 256 permits 231–256 valid turns under a 1800-second acquisition deadline. The first globally zero-survivor TIS batch terminates that cell's attempt, preserving actual progress.

All cells use constant LR 2e-6 and the documented Miles AdamW-semantic community recipe. Reference two-level binary TIS uses token bounds [0.5, 2] and answer-geometric bounds [0.9897, 1.001]. The primary per-update KL is the pre-TIS original-target-token mean of current-student minus teacher log probability; it is distinct from the detached-advantage OPD gradient objective.

There are 16 planned training HFs at successful updates 50/100/150/200 and one shared original 4B baseline. Each SWE-bench Verified point uses 100 fixed tasks × 4 seeds: 17 points and 6,800 logical attempts. Complete checkpoint evaluations release their generated HF after readers exit, including HF200; incomplete evaluations retain HF/evidence with time-limited missing-slot recovery. Original source and historical accepted weights are protected.

All personal submitted nonterminal non-preemptible H200 commitments, including other tasks, must total at most 56 GPUs. Actual Qwen 256-target capacity and concurrency remain unverified.

## Validation and limitations

The final document check passed: 17 Markdown files, nine tickets, 25 local links, one anchor, a valid plan/ticket DAG and correct 800-update/16-HF/17-point/6,800-attempt arithmetic. The two follow-up review findings were corrected, in addition to the three earlier closed findings. Exact evidence is recorded in the test report and review. Historical A/B qualification establishes reusable foundations, not acceptance of this new data/replay/optimizer/benchmark contract. The official Qwen3.5 original-training optimizer remains unconfirmed; the adopted settings come from explicitly identified community recipes.

All nine runtime tickets remain unstarted. Data readability/parity, actual distributed loss/gradient scaling, long-context capacity, native SWE requests/grading, and HF cleanup require the assigned implementation checks before formal runs. A failed cell or missing benchmark result must remain incomplete rather than be filled with planned values.
