## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Establish the documentation milestone and independent pair validation paths. |

# Plan

Status: documentation-first interview; runtime plan is provisional until decisions in [requirements](requirements.md) are answered.

## Steps and completion criteria

| Step | Work | Done condition | Status |
| --- | --- | --- | --- |
| P0 | Read repository rules, referenced resource analysis and relevant implementation; create task documents and resolved glossary terms. | Raw request, three pair identities, source-backed findings, unresolved decisions and verification limits are recorded and links validated. | completed |
| P1 | Resolve framework, replay applicability, workload, acceptance, storage and resource decisions one at a time. | Actual answers are recorded in requirements; the user confirms shared understanding. No unanswered proposal is treated as a decision. | pending |
| P2 | Inspect the selected framework/image and all required assets; reuse its existing paths and report architecture gaps. | Exact source/image/model identities, tokenizer compatibility, executable paths for required features and an approved feasible resource plan are recorded; gaps identify owners and scope. | pending |
| P3-A | Pair A: same-version alignment, actual updates, synchronization, curves and HF export/reload. | Every applicable gate in design passes on the accepted workload and budget, or the precise incomplete gate and cause are recorded. | pending |
| P3-B | Pair B: the same independent validation. | Same criterion, using pair B's own teacher, updates, evidence and HF artifact. | pending |
| P3-C | Pair C: the same independent validation. | Same criterion with the full 397B teacher; no reduced-layer result substitutes for the requested model. | pending |
| P4 | Reconcile outcomes and archive. | Three pair results are reported separately against R1–R6, exact HF paths and reload evidence are recorded, limitations are explicit, and an English summary is written after rereading requirements. | pending |

## Dependencies and concurrent work

`P0 -> P1 -> P2 -> {P3-A, P3-B, P3-C} -> P4`

P2 has shared source/image checks and independent per-asset/per-pair checks. After shared prerequisites are ready, release each pair as soon as its own prerequisites pass; a pair C asset or capacity issue must not block A or B. Inside each pair: identity/input checks -> baseline alignment -> actual updates and weight publication -> final same-version alignment and HF export/reload -> assessment. Common runtime defects may block only the paths they actually affect.

The user requested concurrency across the three experiments. Preserve it within verified quota and placement; do not promise three simultaneously running jobs from request counts alone. This documentation milestone needs no sub-agent or GPU allocation. A future executor can advance independent pair work concurrently once the interview is complete.

## Verification

- P0: validate document structure, raw requirements, pair roles, existing source links, draft/confirmed separation and absence of unrelated changes. Record exact commands and results in the dated test report. This is static documentation validation.
- P1: each answer becomes a dated Q&A entry in requirements. Freeze the relevant acceptance definitions before runs.
- P2: use actual model metadata and selected runtime, then targeted CPU/static tests and native checks appropriate to the selected route. A registry entry or configuration render does not qualify GPU execution.
- P3: use actual H800 outputs, unfiltered valid token metrics, version receipts, optimizer results and HF reloading. Record expected/actual values and PASS/FAIL/INCOMPLETE separately for each gate. Persistent regression tests are added only for demonstrated repairs.
- P4: run `check-progress` at each completed milestone and after repeated unsuccessful repairs; fix documentary drift without inventing approval or runtime success.
