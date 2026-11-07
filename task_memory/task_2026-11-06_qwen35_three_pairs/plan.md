## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Qualify both H200 baselines and complete receipt chains through version3; advance to updated monitoring and final acceptance. |
| 2026-11-07 | Add D19 current-task OSS cleanup alongside running H200 validation; preserve active runs and essential evidence. |
| 2026-11-07 | Apply D18: submit A/B on H200/step_main within32 non-preemptible GPUs; keep optional storage diagnostics independent and C's existing H800 queue. |
| 2026-11-07 | Record real B preload restoration/baseline/first-update evidence, assign the later output-projection OOM to P3-A/B, and apply D17's B restart budget. |
| 2026-11-07 | Separate the probe-only private-pool cleanup defect from formal continuation after two real CUDA IPC restoration cycles; actual preload/full-model observations remain P3 runtime acceptance. |
| 2026-11-07 | Apply D16's C student memory allocation; defer optional rematerialization repair and keep actual restored-runtime qualification on the mainline. |
| 2026-11-07 | Record D15's approved fresh C100-step budget, retaining memory/runtime prerequisites and independent A/B release. |
| 2026-11-07 | Assign confirmed post-eval uniform-policy corruption and C host-memory OOM to P3; preserve actual update accounting before any restart decision. |
| 2026-11-07 | Close verified sample-boundary preparation and release A/B for formal resubmission. |
| 2026-11-07 | Assign the discovered formal-run sample-record and client-deadline gaps to P3 before A/B resubmission; preserve C's running workload and independent native-loader verification. |
| 2026-11-07 | Assign A/B first-backward OOM diagnosis and native fused validation to P3; select native SGLang text reload with final decoder checksum binding. |
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

Status: P1 and P2 initial qualification are complete; P3 owns actual optimization and final artifact qualification. [Requirements](requirements.md) owns D1–D19, including the fixed workload, execution baseline, B/C restart budgets, C memory allocation, A/B H200 migration and scoped OSS cleanup. Current colocated weight transfer uses CUDA IPC; original NCCL-direct qualification is deferred. P2 established the actual population, text-export integration, selected runtime, personal assets and initial resource qualification. This task has no tickets directory; P0–P4 below are its execution records.

## Steps and completion criteria

| Step | Work | Done condition | Status |
| --- | --- | --- | --- |
| P0 | Read repository rules, referenced resource analysis and relevant implementation; create task documents and resolved glossary terms. | Raw request, three pair identities, source-backed findings, unresolved decisions and verification limits are recorded and links validated. | completed |
| P1 | Preserve confirmed decisions in requirements; resolve workload, execution/assessment baseline, output scope and shared understanding. | Actual answers and source-backed implications are recorded; the user confirms shared understanding. No unanswered proposal is treated as a decision. | completed |
| P2 | Inspect and implement the current Miles paths, qualify the selected image and required assets, and resolve feasible resources; report architecture gaps. | Exact source/image/model identities, tokenizer compatibility, executable paths for required features and an approved feasible resource plan are recorded; gaps identify owners and scope. | completed — initial qualification; P3 owns optimization and final reload |
| P3-A | Pair A: same-version alignment, actual updates, synchronization, curves and HF export/reload. | Every applicable gate in design passes on the accepted workload and budget, or the precise incomplete gate and cause are recorded. | in-progress — H200 exp-1107-173758-712234; baseline PASS, same-version restore and published version3 verified |
| P3-B | Pair B: the same independent validation. | Same criterion, using pair B's own teacher, updates, evidence and HF artifact. | in-progress — H200 exp-1107-173758-806531; baseline PASS, same-version restore and published version3 verified; D17 fresh100 |
| P3-C | Pair C: the same independent validation. | Same criterion with the full 397B teacher; no reduced-layer result substitutes for the requested model. | blocked on scheduling — D15/D16 fresh100 run submitted with1500GiB; old failed update retained |
| P3-storage | D19 cleanup of obsolete current-task OSS artifacts, concurrent with formal execution. | Manifest identifies authorized terminal-run targets and retained evidence; deletion and remaining task usage measured; active runs, inputs and required evidence preserved; quota/trash limits explicit. | completed — four obsolete shards/15.668GiB unlinked;10.456GiB task remaining; physical quota unverified |
| P4 | Reconcile outcomes and archive. | Three pair results are reported separately against R1–R8, exact HF paths and reload evidence are recorded, limitations are explicit, and an English summary is written after rereading requirements. | pending |

## Dependencies and concurrent work

`P0 -> {P1, P2 local read-only prerequisites} -> P2 runtime qualification -> {P3-A, P3-B, P3-C} -> P4`; `D19 -> P3-storage -> P4`, concurrent with formal runs.

Local read-only source/image/asset-record investigation advanced alongside P1. D14 now permits implementation. Runtime execution remains gated by each pair's authorized assets and verified runtime/resource prerequisites. The narrow read-only source exceptions are owned by requirements; all generated cloud artifacts remain personal.

P2 has shared source/image checks and independent per-asset/per-pair checks. After shared prerequisites are ready, release each pair as soon as its own prerequisites pass; a pair C asset or capacity issue must not block A or B. Inside each pair: identity/input checks -> baseline alignment -> actual updates and weight publication -> final same-version alignment and HF export/reload -> assessment. Common runtime defects may block only the paths they actually affect.

P2 is complete at initial-qualification scope: frozen population, full assets, native scoring, teacher diagnostics, runtime/resource provenance and all three initial D8 results. The earlier artifacts without KV-version tracking remain INCOMPLETE and are not rewritten. Implementation commits and exact run evidence are maintained in [progress](progress.md), the [native report](test_report_2026-11-07_native_prerequisites.md) and the [teacher-diagnostic report](test_report_2026-11-07_teacher_diagnostic.md). P3's first actual optimizer update must establish full-model capacity within the approved100-position budget; no extra optimizer probe or baseline-only capacity claim is allowed.

Latest P3 frontier: both D18 jobs have passing24-sample H200 baselines and native same-epoch receipt chains from version0 through version3, including exact same-version restoration checks. Continue updated monitoring at position19 and the remaining100-position/final HF acceptance while retaining both launchers. Each uses10 H200 GPUs,20 total, within the session/task ceiling of32. The prior B H800 run and independent output-retention investigation remain historical evidence; early H200 success does not prove worst-case capacity or resolve that dependency defect. The independent fixture-only repair is pinned-verified93PASS and closed. C remains independently submitted on H800 under D15/D16. D19's selected cleanup is complete, with physical quota reclamation unverified. No extra optimizer probe or automatic further restart is authorized.

The corrected diagnostic `exp-1107-150925-737118` passes both CUDA cycles and complete worker/container exits; its cleanup work is closed. The original ERROR receipt remains historical evidence. Native failure isolation/refill-eight, task-specific attempt records and the existing3600-second deadline are implemented and pinned-verified. The [sample-boundaries report](test_report_2026-11-07_sample_boundaries.md) owns cancellation evidence. B now supplies the first actual repaired formal restoration and published optimizer update; updated/final D8, sustained capacity and final HF remain incomplete. Independent native4B text loading,822 decoder checksums and its full-interpreter cleanup regression are already qualified at baseline scope. No final artifact is available yet.

Final reload uses the existing pinned SGLang text loader with the actual run's TP and weight-affecting settings. Compare its complete native eligible decoder checksum dictionary with the final publication receipt, excluding only D13's declared vision/MTP scope and the native checksum exclusions. Reuse final monitoring inputs and perform actual text generation. This replaces the unqualified Transformers reload path, which loses saved FP32 `A_log`; it adds no dependency patch, custom hashing or checkpoint metadata path. The standalone validator cannot control healthy training. Evidence and outstanding limits are in the [HF reload report](test_report_2026-11-07_hf_reload.md).

For P2, reuse the existing fixed template and its parameters under D4/D10; no complete-history drop transformation is needed. The named Qwen TITO adapter already uses preservation for append-only sessions, but this task remains fresh single-turn OPD. Pass explicit settings through task preparation so the retained user override is effective. Verify actual prefix/response IDs, selected-policy lengths and masks. D5 research is complete at documentation/source scope; its original separated recommendation is superseded by the user's temporary colocation choice. The current layout and remaining native gates are in [deployment_research.md](deployment_research.md). D14 confirms shared understanding; do not re-ask resolved choices.

The user requested concurrency across the three experiments. Preserve it within verified quota and placement; do not promise three simultaneously running jobs from request counts alone. D5 research uses a background research agent as required by the invoked research skill; no GPU allocation is needed. Independent pair work can proceed concurrently once the interview and relevant prerequisites are complete.

## Verification

- P3-storage is complete under D19: primary platform terminal receipts, identity-rechecked four-file removal, retained evidence checks and remaining task usage are recorded in `test_report_2026-11-07_oss_cleanup.md`. Physical quota reclamation remains unverified; no shared trash was touched.

- P0: validate document structure, raw requirements, pair roles, existing source links, draft/confirmed separation and absence of unrelated changes. Record exact commands and results in the dated test report. This is static documentation validation.
- P1: each answer becomes a dated Q&A entry in requirements. CPU checks cover four local historical snapshots, two preserve-all generation modes and the three earlier native-history boundary cases retained as false-mode controls; see the format report. Loss-mask and transport observations are source evidence only. Freeze the relevant acceptance definitions before runs.
- P2: use actual model metadata and the selected Miles runtime, then targeted CPU/static tests and native checks. A registry entry, configuration render or successful run in another framework does not qualify Miles GPU execution.
- P3: use actual authorized H200 A/B and H800 C outputs, unfiltered valid token metrics, version receipts, optimizer results and HF reloading. Record expected/actual values and PASS/FAIL/INCOMPLETE separately for each gate. Persistent regression tests are added only for demonstrated repairs.
- P4: run `check-progress` at each completed milestone and after repeated unsuccessful repairs; fix documentary drift without inventing approval or runtime success.
