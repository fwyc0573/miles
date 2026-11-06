## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Qualify source availability, pinned CPU runtime and the full Qwen population; track native monitor review fixes and authorized cleanup within P2. |
| 2026-11-06 | Complete P1 under D14; release parallel P2 implementation and prerequisite checks, with runtime assets/resources still required before GPU execution. |
| 2026-11-06 | Confirm D9's finite training/monitoring budget; resume P1 and independent local prerequisite inspection. |
| 2026-11-06 | Apply the latest preserve_thinking=True trajectory-prefix default; retain D6 loss scope, D7 budget and D8 numerical acceptance. |
| 2026-11-06 | Accept D8 numerical qualification and advance P1 to the bounded training-effectiveness workload and monitoring population. |
| 2026-11-06 | Record D7's accepted context budget and move the interview to numerical acceptance and remaining workload/resource decisions. |
| 2026-11-06 | Apply temporary student colocation, native last-real-user rendering and completion-only loss; remove the superseded keep/drop implementation and historical-loss question. |
| 2026-11-06 | Replace mandatory retention with the latest user-controlled input switch and adopt the researched separated NCCL deployment. |
| 2026-11-06 | Add mandatory history preservation and independent deployment research; keep historical-loss semantics explicit. |
| 2026-11-06 | Record D3 and the completed CPU format check; keep full-corpus, deployed assets and runtime qualification pending. |
| 2026-11-06 | Record the confirmed R3 interpretation and advance the interview to learning data and sampling. |
| 2026-11-06 | Fix execution to current Miles and advance the interview to routing-replay applicability. |
| 2026-11-06 | Establish the documentation milestone and independent pair validation paths. |

# Plan

Status: P1 complete; P2 active under D14's confirmed shared understanding. [Requirements](requirements.md) owns D1–D14, including the fixed workload and execution baseline. Current colocated weight transfer uses CUDA IPC; original NCCL-direct qualification is deferred. P2 owns actual population identities, text-export integration, selected runtime, personal assets and feasible resources. This task has no tickets directory; P0–P4 below are its execution records.

## Steps and completion criteria

| Step | Work | Done condition | Status |
| --- | --- | --- | --- |
| P0 | Read repository rules, referenced resource analysis and relevant implementation; create task documents and resolved glossary terms. | Raw request, three pair identities, source-backed findings, unresolved decisions and verification limits are recorded and links validated. | completed |
| P1 | Preserve confirmed decisions in requirements; resolve workload, execution/assessment baseline, output scope and shared understanding. | Actual answers and source-backed implications are recorded; the user confirms shared understanding. No unanswered proposal is treated as a decision. | completed |
| P2 | Inspect and implement the current Miles paths, qualify the selected image and required assets, and resolve feasible resources; report architecture gaps. | Exact source/image/model identities, tokenizer compatibility, executable paths for required features and an approved feasible resource plan are recorded; gaps identify owners and scope. | in-progress |
| P3-A | Pair A: same-version alignment, actual updates, synchronization, curves and HF export/reload. | Every applicable gate in design passes on the accepted workload and budget, or the precise incomplete gate and cause are recorded. | pending |
| P3-B | Pair B: the same independent validation. | Same criterion, using pair B's own teacher, updates, evidence and HF artifact. | pending |
| P3-C | Pair C: the same independent validation. | Same criterion with the full 397B teacher; no reduced-layer result substitutes for the requested model. | pending |
| P4 | Reconcile outcomes and archive. | Three pair results are reported separately against R1–R8, exact HF paths and reload evidence are recorded, limitations are explicit, and an English summary is written after rereading requirements. | pending |

## Dependencies and concurrent work

`P0 -> {P1, P2 local read-only prerequisites} -> P2 runtime qualification -> {P3-A, P3-B, P3-C} -> P4`

Local read-only source/image/asset-record investigation advanced alongside P1. D14 now permits implementation. Runtime execution remains gated by each pair's authorized assets and verified runtime/resource prerequisites. The narrow read-only source exceptions are owned by requirements; all generated cloud artifacts remain personal.

P2 has shared source/image checks and independent per-asset/per-pair checks. After shared prerequisites are ready, release each pair as soon as its own prerequisites pass; a pair C asset or capacity issue must not block A or B. Inside each pair: identity/input checks -> baseline alignment -> actual updates and weight publication -> final same-version alignment and HF export/reload -> assessment. Common runtime defects may block only the paths they actually affect.

P2 execution slices: source population and model metadata (completed by zero-GPU `exp-1106-233008-986003`) -> {native scoring/eval integration and review fixes, three-pair launcher, original-token numerical report, H800 resource qualification} -> per-pair P3 release. The single-token repair is committed as `315a8724`; text-export CPU validation is complete, while real student reload remains native work. The v2 guard repair resolved the submission blocker. User-requested local cleanup is independently completed with selected evidence retained; it does not gate GPU qualification.

For P2, reuse the existing fixed template and its parameters under D4/D10; no complete-history drop transformation is needed. The named Qwen TITO adapter already uses preservation for append-only sessions, but this task remains fresh single-turn OPD. Pass explicit settings through task preparation so the retained user override is effective. Verify actual prefix/response IDs, selected-policy lengths and masks. D5 research is complete at documentation/source scope; its original separated recommendation is superseded by the user's temporary colocation choice. The current layout and remaining native gates are in [deployment_research.md](deployment_research.md). D14 confirms shared understanding; do not re-ask resolved choices.

The user requested concurrency across the three experiments. Preserve it within verified quota and placement; do not promise three simultaneously running jobs from request counts alone. D5 research uses a background research agent as required by the invoked research skill; no GPU allocation is needed. Independent pair work can proceed concurrently once the interview and relevant prerequisites are complete.

## Verification

- P0: validate document structure, raw requirements, pair roles, existing source links, draft/confirmed separation and absence of unrelated changes. Record exact commands and results in the dated test report. This is static documentation validation.
- P1: each answer becomes a dated Q&A entry in requirements. CPU checks cover four local historical snapshots, two preserve-all generation modes and the three earlier native-history boundary cases retained as false-mode controls; see the format report. Loss-mask and transport observations are source evidence only. Freeze the relevant acceptance definitions before runs.
- P2: use actual model metadata and the selected Miles runtime, then targeted CPU/static tests and native checks. A registry entry, configuration render or successful run in another framework does not qualify Miles GPU execution.
- P3: use actual H800 outputs, unfiltered valid token metrics, version receipts, optimizer results and HF reloading. Record expected/actual values and PASS/FAIL/INCOMPLETE separately for each gate. Persistent regression tests are added only for demonstrated repairs.
- P4: run `check-progress` at each completed milestone and after repeated unsuccessful repairs; fix documentary drift without inventing approval or runtime success.
