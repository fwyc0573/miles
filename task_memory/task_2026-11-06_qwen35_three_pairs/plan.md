## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Enable native prefill-version tracking and pass89 affected checks in the pinned runtime; release actual baseline requalification. |
| 2026-11-07 | Record completed A/B native execution with an INCOMPLETE consumed-prefill-version gate; P2 owns enabling the existing engine tracker and actual requalification while C runs independently. |
| 2026-11-07 | Assign the measured C readiness-timeout repair to P2; use pair-specific startup waits while A/B retain their independent queues. |
| 2026-11-07 | Record successful native Ray startup and the zero-update scheduler initialization blocker; retain independent pair release and formal optimizer requirements. |
| 2026-11-07 | Record actual A teacher startup and student Ray-path failure; P2 owns repair and A/B resubmission while C keeps its independent queue. |
| 2026-11-07 | Close offline teacher-diagnostic implementation/review and record admitted A/B fixes with all native baselines still queued. |
| 2026-11-07 | Mark native integration complete, record actual startup/queue blockers and retain independent per-pair release after qualification. |
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

P2 execution slices: source population and model metadata (completed by zero-GPU `exp-1106-233008-986003`) -> {native scoring/eval integration, three-pair launcher, original-token numerical report, H800 resource qualification} -> per-pair P3 release. Integration/review fixes are committed as `ec127a1a`, data/text export as `ede719c1`, singleton repair as `315a8724`. ConfigMap/Ray/scheduler corrections now have native A/B execution evidence: each student completed24 monitoring generations and four trainer-score shards with exit0. Their numerical reports remain INCOMPLETE because the shared launcher omitted existing prefill/KV version tracking. P2 owns enabling that supported engine flag, validating the pinned parser/producer and requalifying actual inputs; old missing spans must not be inferred or rewritten. C's wait correction `6461e6e2` is CPU-verified and its new24-GPU job is Running, independently loading the full teacher. Current identities, status and evidence are maintained in [progress](progress.md) and the [native report](test_report_2026-11-07_native_prerequisites.md). The [offline teacher-diagnostic phase](test_report_2026-11-07_teacher_diagnostic.md) is closed at CPU-contract scope. Numerical acceptance, backward/optimizer capacity and final reload remain unverified; zero-update evaluation cannot qualify optimization capacity. User-requested local cleanup is complete with selected evidence retained and does not gate GPU qualification.

The tracking flag is now implemented and89 affected checks pass in the pinned runtime, including native parsing, scheduler construction and asynchronous baseline execution. That source/runtime slice is complete; actual newly generated prefix-version evidence and D8 measurements remain the next qualification step. No further general test expansion precedes the new baseline runs.

For P2, reuse the existing fixed template and its parameters under D4/D10; no complete-history drop transformation is needed. The named Qwen TITO adapter already uses preservation for append-only sessions, but this task remains fresh single-turn OPD. Pass explicit settings through task preparation so the retained user override is effective. Verify actual prefix/response IDs, selected-policy lengths and masks. D5 research is complete at documentation/source scope; its original separated recommendation is superseded by the user's temporary colocation choice. The current layout and remaining native gates are in [deployment_research.md](deployment_research.md). D14 confirms shared understanding; do not re-ask resolved choices.

The user requested concurrency across the three experiments. Preserve it within verified quota and placement; do not promise three simultaneously running jobs from request counts alone. D5 research uses a background research agent as required by the invoked research skill; no GPU allocation is needed. Independent pair work can proceed concurrently once the interview and relevant prerequisites are complete.

## Verification

- P0: validate document structure, raw requirements, pair roles, existing source links, draft/confirmed separation and absence of unrelated changes. Record exact commands and results in the dated test report. This is static documentation validation.
- P1: each answer becomes a dated Q&A entry in requirements. CPU checks cover four local historical snapshots, two preserve-all generation modes and the three earlier native-history boundary cases retained as false-mode controls; see the format report. Loss-mask and transport observations are source evidence only. Freeze the relevant acceptance definitions before runs.
- P2: use actual model metadata and the selected Miles runtime, then targeted CPU/static tests and native checks. A registry entry, configuration render or successful run in another framework does not qualify Miles GPU execution.
- P3: use actual H800 outputs, unfiltered valid token metrics, version receipts, optimizer results and HF reloading. Record expected/actual values and PASS/FAIL/INCOMPLETE separately for each gate. Persistent regression tests are added only for demonstrated repairs.
- P4: run `check-progress` at each completed milestone and after repeated unsuccessful repairs; fix documentary drift without inventing approval or runtime success.
