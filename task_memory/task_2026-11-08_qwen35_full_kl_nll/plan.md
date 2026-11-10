## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record actual H200 first-bank/generation progress and delivered CPU CLI; track open parallel review repairs before regression/re-review, retaining native/final gates. |
| 2026-11-10 | Align remaining current D36 statements with D37 H200 preparation and parallel CPU work; record18-H200/cell and the32-GPU resource constraint without changing science or final criteria. |
| 2026-11-10 | Correct the overbroad06 edge: run offline inspection and report implementation alongside04 resource waiting; retain04/05 runtime dependencies for actual data and final acceptance. |
| 2026-11-10 | Apply selected D36: retain the accepted 36-H800 layout, wait for improved placement evidence and fresh resource admission; do not infer a third attempt or available resources. |
| 2026-11-10 | Record both A attempts failed before training; pause submissions at PLACEMENT_BLOCKED pending an evidence-backed placement/startup strategy decision. |
| 2026-11-10 | Retain failed first A attempt with zero updates and partial RCA; move current frontier to unchanged retry after fresh admission, without changing gates or adding a rerun loop. |
| 2026-11-10 | Record formal A submission and move the frontier to startup/first-update inspection. |
| 2026-11-10 | Accept03 CPU integration15186817 and final profile configurationec002ea8; move to fresh A admission/first-update verification without changing B concurrent admission. |
| 2026-11-10 | Accept02 CPU readiness6129aefe and move the frontier to active03 integration;keep pending reviews,GPU acceptance and existing A-first-ACK concurrent B admission separate. |
| 2026-11-10 | Record verified D35 merge55fba827 and resolved prep references; move the frontier to02 implementation, retaining03 CPU-readiness and formal-update dependencies. |
| 2026-11-10 | Apply D35: capacity basis accepted, candidate merge is the frontier, then02 CPU-ready and03 integration; upstream frozen-D11 acceptance is independent. |
| 2026-11-09 | Close Ticket01's D34 original-source112K audit and return the parent frontier to the unchanged upstream integration gate. |
| 2026-11-09 | Replace the stale running prerequisite with the observed initial-weight-sync timeout and scoped diagnosis. |
| 2026-11-09 | Add D34 input/launcher budget changes and renewed112K audit in parallel with H800 preparation. |
| 2026-11-09 | Start D33 H800 preparation in parallel with read-only monitoring of the upstream capacity attempt. |
| 2026-11-09 | Accept Ticket01 source audit/parity; independent CPU work complete, integration waits for the freshly rechecked upstream gate. |
| 2026-11-09 | Repair executable dependency checkpoints, soft-gate acceptance and B admission; refresh the upstream blocker and pending in-place CPU evidence. |
| 2026-11-08 | Draft the six-ticket dependency graph and verification strategy; awaiting Q17–Q19 and freeze. |
| 2026-11-08 | Update ticket 01 and the verification strategy for D18; awaiting freeze. |
| 2026-11-08 | Record the freeze; rename the ticket 01 link; move the frontier to 01 and the 03 module. |
| 2026-11-08 | Ticket 01 done; frontier is the 03 module. |
| 2026-11-08 | Rename KL to RKL in the ticket 02 row (D21). |
| 2026-11-08 | The 03 module is done; the frontier waits for the reused Ticket02. |
| 2026-11-08 | Note the reused Ticket02 capacity failure in the frontier. |
| 2026-11-08 | Apply D22: the frontier waits for that branch's out-of-memory fix. |
| 2026-11-08 | Reopen 01 for the SWE-1003 0913 data (D23–D27); add the source audit and the checks on the files in place. |
| 2026-11-08 | 01 SWE-1003 items 1–4 done locally; the frontier is the CPU RJob for items 5–6. |
| 2026-11-08 | Reopen the 03 module for D28–D32; the frontier is that change, with 01 items 5–6 deferred. |
| 2026-11-08 | The 03 module covers D28–D32; the frontier is again the wait for the reused Ticket02. |

# Plan

**Phase: D37 H200_EXECUTING; offline review repairs in parallel.** Actual A`exp-1110-140032-491115`has18 H200/teacher/Ray8+8 verified; the06:17:12Z[startup context](evidence/formal-H200-A-startup-context-20261110.json)records bank0 start14:14:56.775HKT/256 candidates and successful generation. freeze_gc context is followed by server ready/generation, not a native blocking failure. FirstACK/D16/profile acceptance are not yet verified. Inspector`a76fc527`57 tests/reporter`e6956e3c`26 tests and CLI4 PASS are delivered; fixed-diff reviews yielded4 functional+1 naming nit, open/fixing ([review](review.md#offline-inspectorreport-phase-review--2026-11-10)). Repair agents run alongside native A, then joined regression/re-review. CPU fixtures are not formal metrics; final04/05/06 criteria and32 non-preemptible resources are unchanged.

## Scope and ownership

Behavior is owned by [spec.md](spec.md); raw requests and actual answers are in [requirements.md](requirements.md). This plan owns ticket dependencies and the verification strategy only.

## Tickets

| Ticket | Deliverable | Blocked by |
| --- | --- | --- |
| [01](tickets/01-interleaved-turn-order.md) | Interleaved turn order in the committed SWE input adapter, with the SWE-1003 loss-masked turn source and its source audit | Documentation freeze; D23–D27 |
| [02](tickets/02-per-turn-sums.md) | Per-turn RKL/NLL sums: CPU implementation-ready, then GPU acceptance at A's first update | Satisfied: D35 capacity basis accepted and candidate merged as`55fba827`; no remaining merge blocker |
| [03](tickets/03-distillation-profile.md) | Done: Distillation profile module, persistence and CPU rollout integration15186817 | Satisfied: documentation freeze/module CPU and 02 CPU implementation-ready6129aefe |
| [04](tickets/04-a-full.md) | Executing18-H200 A, first bank/generation in progress; first ACK/D16 pending | Satisfied: 01, 02 CPU, 03 CPU, D37/configuration review/admission/submission; native A continues while offline inspector/reporter repairs run |
| [05](tickets/05-b-full.md) | B/full native training and separately verified profile | Satisfied: 01 accepted, 02 CPU-ready, 03 CPU integration; pending: 04 actual first ACK/inspection and fresh18-H200 admission within32; allocation release needed while A holds18 |
| [06](tickets/06-profile-report.md) | CPU join delivered; review repairs/regression/re-review and actual final report pending | CPU dependency 03 and initial CLI satisfied; final measurements still need 04, 05 native/terminal/profile evidence, not repaired fixtures alone |

Dependency graph:

```text
documentation freeze -> {01, 03-module}
D28–D32 in the spec -> 03-module revision (CPU only)
D23–D27 in the spec -> 01 revision: {adapter code + local checks, source audit (CPU RJob)} -> checks on the files in place (CPU RJob)
D35 H800 capacity basis accepted -> candidate merge55fba827 verified -> 02 CPU implementation-ready6129aefe accepted -> 03-integration CPU-ready15186817 accepted
{01 accepted, 02 CPU implementation-ready, 03-integration CPU-ready, final formal configuration/lifecycle checks} -> 04 fresh admission -> 04 launch
historical 04 H800 startup failures -> historical D36 wait route (superseded for current execution by D37)
D37 -> reviewed18-H200 configuration -> actual submission/18-H200/teacher/Ray verified -> bank0 acquisition/generation in progress -> real firstACK/D16 pending
04 actual first successful update -> inspection completed -> {02 GPU acceptance evidence, 05 fresh resource admission}
05 fresh resource admission requires personal committed H200 +18 <=32; A18+B18 cannot overlap while both retain full allocation
03 CPU-ready -> {04/05 offline inspection preparation, 06 report computation preparation}
{04/05 inspector a76fc527 delivered, 06 reporter e6956e3c delivered} -> initial CPU CLI4 PASS -> parallel review repairs -> joined regression + re-review
{04 terminal evidence, 05 terminal evidence, CPU report readiness} -> 06 actual reports and final acceptance
```

Historical parallel work:01 and the pure03 module started after the freeze without touching uncommitted reused code.02`6129aefe`and03`15186817`still satisfy CPU dependencies; the earlier H800 configuration/lifecycle/review evidence remains historical. Both failed H800 formal attempts and D36's wait decision are retained separately. At the previous D37 checkpoint, H200 preparation plus independent CPU implementation replaced H800 waiting; actual H200 startup/CPU join now supersedes that preparation status. Upstream acceptance remains independent.

The table's02/03 edges into formal cells are CPU readiness checkpoints, not full ticket closure;02 GPU verification cannot be a circular A-launch prerequisite. B requires A's actual first successful native update, completed inspection and fresh resource admission. With18 H200/cell and the32 ceiling, B must await allocation release while A still holds18; this is a resource constraint, not an A200-update or auxiliary-profile-PASS gate. S7 errors continue healthy training and are reported separately as incomplete profile acceptance. Failed/incomplete evidence permits honest06 reporting, not complete-cell acceptance.

## Verification strategy

1. **Documentation:** trace each original requirement to a spec section or ticket; check local links, counts and the graph above.
2. **Input (01):** run the extended `tests/manual/agent_opd/check_swe_inputs.py` on CPU. Locally: the existing historical GLM copies with `all_assistants` and a synthetic file set with `loss_masked`. In a CPU RJob that mounts posttrain: the source audit `audit_swe1003_sources.py`, then the `loss_masked` checks on the 8 files in place, with no input copy (D25) — with one open conversation the sequence equals the native single-source sequence; with 32 × 8 the order properties hold on the raw mixer output. Native instance/repository identity and exact-text proxy coverage are reported separately under S2; unavailable native identity stays null / unverified.
3. **Measurement (02):** a fast CPU test of the per-sample sums with uneven lengths and a two-rank CP split, following the reused `tests/fast/test_swe_tis.py`; GPU acceptance happens at the first update of 04 rather than in a separate smoke (D16).
4. **Profile (03):** a fast CPU test with a synthetic update sequence and hand-computed expected values, including D28–D32 and first entries with fewer/more than N observations; offline rebuild from complete paired JSONL files; fault injection for a failing write, row-count/uid mismatch and subsequent update suppression; measured update and query time. CPU module evidence does not verify rollout integration.
5. **Formal cells (04, 05):** after A's first actual successful native update, complete and record the profile inspection before B's resource admission, reporting auxiliary failure without stopping healthy training. Report stage times again near update 20; check actual 200 successful updates separately from complete paired profile files, per-update consistency and rebuild. Mark incomplete profile ranges explicitly under S7.
6. **Report (06):** recompute every reported value from verified retained records, distinguish native training from profile acceptance and retain honest failed/incomplete dispositions. Dimensionless gaps do not establish controlled comparisons across teachers or turn composition.

Each ticket records commands and evidence in `progress.md` and a dated test report in this directory.

## Current frontier

**Parallel CPU frontier (D37):** initial inspector57/reporter26 tests and CLI4 cases PASS remain recorded in[the joined report](test_report_2026-11-10_offline_report_integration.md)and`evidence/offline-report-join-20261110.json`. Standards1 material+1 nit/Spec4 deduplicate to4 functional+1 nit: tempfile directory, adjacent known native auxiliary failure, extra unverified native tail, actual update-ID milestones, local group/groups naming. All are open/fixing; inspector/reporter repairs run in parallel with native A, followed by joined regression/re-review. Existing fixture results do not prove fixes or final06/native acceptance. The CPU-versus-final-data dependency split remains unchanged; no extra execution gate.

Ticket01 is accepted including D34: the original-source112K CPU audit,512 native parity draws and2,048 interleaved raw draws passed; job/replica Succeeded at11:47:11Z and source identities reconcile ([current length/source report](test_report_2026-11-09_length_budgets.md#completed112k-original-source-audit)). The [historical128K report](test_report_2026-11-09_source_audit.md) retains its original policy and results. D26 keeps32×8 from the pre-length eligible median90; current simulated spans and absent post-length median are limitations, not a new blocker or native trend acceptance. The03 module retains D28–D32 CPU evidence ([test report](test_report_2026-11-08_profile_remaining_gap.md)) and historical query/baseline/partial-write checks ([review test report](test_report_2026-11-09_review_execution.md)). Native-count consistency and the full CPU integration path are now accepted in [ticket03](tickets/03-distillation-profile.md), with [201-PASS evidence](test_report_2026-11-10_profile_integration.md); actual GPU/profile verification remains separate. Current state is owned by [progress](progress.md#in-progress).

The historical2026-11-09T07:56Z upstream refresh at `c52991ac` recorded capacity job`exp-1109-144110-764758` failing at initial trainer-to-rollout weight synchronization after600s, before rollout collection or optimizer updates. This failure remains unaccepted evidence, as do earlier acquisition227<231 and historical interrupted scoring. Those historical outcomes are not relabeled byD35; exact limits remain in [the H800 preparation report](test_report_2026-11-09_h800_preparation.md#upstream-prerequisite-failure-2026-11-09t0756z).

Current frontier: **04 real firstACK/D16 plus parallel inspector/reporter repairs**. A`exp-1110-140032-491115`was submitted14:00:32HKT with18 H200/step_main, all3 assigned and actual workers/Ray verified. Bank0 acquisition began14:14:56.775HKT with256 candidates; generation succeeded, and the freeze_gc request context is non-blocking on this evidence. Primary owns actual monitoring/commands in[the formal report](test_report_2026-11-10_formal_runs.md); this agent does not query watchers/platform. Offline findings remain open until completion receipts, joined regression and re-review; native A continues independently. Actual firstACK triggers D16/02 GPU inspection, then B fresh resources after release within32. No A200/profile-PASS logical gate. Each cell's200 native ACKs/paired-profile disposition and actual final06 remain pending; historical H800 artifacts/science remain protected, no GPU smoke/auxiliary hardgate.

Historical H800 preparation`4863e68e`, correction`059a6a75`, profile configuration`ec002ea8`and its4/4 native-argv dry-runs remain in[the configuration report](test_report_2026-11-10_formal_configuration.md), not proof of current H200 runtime. The earlier16-case lifecycle inspection and exact mock limits remain in[its retained section](test_report_2026-11-10_formal_configuration.md#pre-formal-sample-lifecycle-check). D37's separate H200 configuration is committed without altering the old H800 file. Full still visits200 distinct banks once each with`bank_uses=50`. Current B teacher is configured2 H200/TP2, not native verified. B may follow ACK/inspection only when fresh resources fit the32 ceiling; do not replace that budget condition with A200/profile-PASS/extra-approval/GPU-smoke gates. Native acceptance and S7 isolation are unchanged.

D34's input length slice is complete: adapter/native-request bounds, CPU boundary/config checks and the existing in-place112K prompt/16K completion audit have verified evidence separate from the historical128K run. No repeat full-source scan or sampling change is needed for Ticket01 closure. D35 explicitly adopts the now-completed H800 capacity basis; it does not certify02/03 integration, B's native runtime or either200-update profile.
