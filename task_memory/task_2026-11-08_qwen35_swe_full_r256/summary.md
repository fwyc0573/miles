## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record D11's authorized data replacement and reopened input acceptance; retain the earlier documentation archive. |
| 2026-11-08 | Retain the documentation archive and update implementation status and the explicitly amended D9 resource policy. |
| 2026-11-08 | Record the post-freeze two-axis review: link the spec for optimizer/TIS parameters and list the renumbered tickets. |
| 2026-11-08 | Archive the completed, explicitly confirmed documentation deliverable. |

# Qwen3.5 SWE full/r256 — Documentation landing

## Status

Documentation landing is complete and implementation is authorized. The user subsequently replaced the training data under D11; [spec S3](spec.md#s3-输入加载与比较控制) owns the current source contract. Ticket01's acceptance in `20d0b3f4` applies to the former GLM-5.2 inputs and is reopened for the replacement. Tickets02/03 continue native integration. No formal training or complete benchmark result is claimed.

## Deliverables

All paths below are relative to `task_memory/task_2026-11-08_qwen35_swe_full_r256/`:

- `requirements.md`: original request, actual answers, authority and source identities.
- `spec.md`: four-cell protocol, default Steptron SWE loading, 200-update budget, replay/TIS/objective, metrics, HF/evaluation lifecycle and resource limits.
- `plan.md` and `tickets/01-native-swe-inputs.md` through `tickets/09-four-cell-comparison.md`: nine independently verifiable tickets, numbered in dependency order, and their dependency graph. Ticket 08 is the shared baseline added under D8; ticket 09 is the final comparison.
- `optimizer_research.md`: primary-source official/community optimizer findings and adoption of Miles AdamW semantics with explicit evidence limits.
- `progress.md`, `review.md` and `test_report_2026-11-08_docs_landing.md`: investigation, review remediation, checkpoint and exact local validation evidence.
- Repository `GLOSSARY.md`: resolved training-turn, replay-bank and experiment-cell terminology, with no implementation details.

## Experiment contract

Two teachers, 27B and 35B-A3B, each train an independently initialized original 4B student under full and r256. Each cell targets 200 successful updates; r256 uses each bank 50 consecutive times. The batch target of 256 permits 231–256 valid turns under a 1800-second acquisition deadline. The first globally zero-survivor TIS batch terminates that cell's attempt, preserving actual progress.

All cells use constant LR 2e-6, the optimizer recipe adopted under D3 and the Steptron two-level binary TIS selected under D4; [spec.md S4](spec.md#s4-replay优化与逐步度量) owns their exact parameters. The primary per-update KL is the pre-TIS original-target-token mean of current-student minus teacher log probability; it is distinct from the detached-advantage OPD gradient objective.

There are 16 planned training HFs at successful updates 50/100/150/200 and one shared original 4B baseline. Each SWE-bench Verified point uses 100 fixed tasks × 4 seeds: 17 points and 6,800 logical attempts. Complete checkpoint evaluations release their generated HF after readers exit, including HF200; incomplete evaluations retain HF/evidence with time-limited missing-slot recovery. Original source and historical accepted weights are protected.

The user subsequently amended the resource policy; [spec.md S7](spec.md#s7-gpu-与执行准备) and `gpu_policy.json` define the temporary independent task allocation, preemptible overflow, continuation of admitted jobs, and post-expiry personal admission. Actual Qwen 256-target capacity and concurrency remain unverified.

## Validation and limitations

The final document check passed: 17 Markdown files, nine tickets, 25 local links, one anchor, a valid plan/ticket DAG and correct 800-update/16-HF/17-point/6,800-attempt arithmetic. The two follow-up review findings were corrected, in addition to the three earlier closed findings. A post-freeze two-axis review of commit `f2f86fea` then found no Spec issue and three Standards Nits; the Nits were fixed without changing any decision, and the post-review revision check passed. Exact evidence is recorded in the test report and [review.md](review.md). Historical A/B qualification establishes reusable foundations, not acceptance of this new data/replay/optimizer/benchmark contract. The official Qwen3.5 original-training optimizer remains unconfirmed; the adopted settings come from explicitly identified community recipes.

Replacement input readability/parity and overlap checks are pending under Ticket01. Retained native math, evaluator and lifecycle evidence must be reported with its actual scope; new-data load qualification and remaining integration checks gate formal execution under the plan. Ticket09 awaits formal results. A failed cell or missing benchmark result must remain incomplete rather than be filled with planned values.
