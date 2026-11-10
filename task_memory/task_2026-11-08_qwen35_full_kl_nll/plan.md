## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Advance D38 from controlled diagnostic PASS to the existing-native-API initialization-timing correction and formal verification. |
| 2026-11-10 | Accept the independent offline CPU slice and record D38 as the next native diagnostic action. |
| 2026-11-10 | Accept01/02/03 and D16; block formal04/05 on native host-memory fault/fresh admission, retaining independent final offline edge fix and unchanged scientific criteria. |
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

**Phase: D16 PASS / NATIVE_HOST_MEMORY_REPAIR.**01/02/03 and the independent offline CPU slice are accepted. Formal A remainsFailed1/200 after native TMS offload host-memory pressure. The controlled D38 diagnostic is PASS; an existing-native-API initialization-timing correction is in progress. Its formal verification and fresh resources remain outstanding for04/05. B's firstACK/inspection dependency is satisfied. See[authoritative current state](progress.md#in-progress)and[real D16 proof](test_report_2026-11-10_d16_first_update.md).

## Scope and ownership

Behavior is owned by [spec.md](spec.md); raw requests and actual answers are in [requirements.md](requirements.md). This plan owns ticket dependencies and the verification strategy only.

## Tickets

| Ticket | Deliverable | Blocked by |
| --- | --- | --- |
| [01](tickets/01-interleaved-turn-order.md) | Interleaved turn order in the committed SWE input adapter, with the SWE-1003 loss-masked turn source and its source audit | Documentation freeze; D23–D27 |
| [02](tickets/02-per-turn-sums.md) | Done: CPU/S7 and actual first-update GPU measurement/persistence accepted by D16 | Satisfied: D35 merge, CPU checks and retained real firstACK/canonical bank/paired rebuild |
| [03](tickets/03-distillation-profile.md) | Done: Distillation profile module, persistence and CPU rollout integration15186817 | Satisfied: documentation freeze/module CPU and 02 CPU implementation-ready6129aefe |
| [04](tickets/04-a-full.md) | BLOCKED: native host-memory fault after D16; current attemptFailed1/200 | 01, 02, 03 accepted; native allocation mechanism/fix and fresh formal admission pending |
| [05](tickets/05-b-full.md) | BLOCKED: common native memory fault and fresh admission | 01, 02, 03 accepted; 04 firstACK/inspection satisfied, common fix and fresh18-H200 resources within32 still pending |
| [06](tickets/06-profile-report.md) | TODO: CPU slice accepted, final data pending | CPU dependency 03 satisfied; final measurements still need 04, 05 actual native/terminal/profile evidence |

Dependency graph:

```text
documentation freeze -> {01, 03-module}
D28–D32 in the spec -> 03-module revision (CPU only)
D23–D27 in the spec -> 01 revision: {adapter code + local checks, source audit (CPU RJob)} -> checks on the files in place (CPU RJob)
D35 H800 capacity basis accepted -> candidate merge55fba827 verified -> 02 CPU implementation-ready6129aefe accepted -> 03-integration CPU-ready15186817 accepted
{01 accepted, 02 CPU implementation-ready, 03-integration CPU-ready, final formal configuration/lifecycle checks} -> 04 fresh admission -> 04 launch
historical 04 H800 startup failures -> historical D36 wait route (superseded for current execution by D37)
D37 -> actual H200 A firstACK + D16 PASS -> 02 done; 05 firstACK/inspection edge satisfied
04 native host-memory failure after update1 -> allocation mechanism verification -> evidence-backed fix -> fresh independent formal attempts
05 fresh resource admission requires personal committed H200 +18 <=32; A18+B18 cannot overlap while both retain full allocation
03 CPU-ready -> {04/05 offline inspection preparation, 06 report computation preparation}
{inspector24e8386f, reporterd0f67887} ->69/27 PASS + postfix CLI4 PASS ->219489ef +12 affected PASS +2 prefix-zero CLI PASS -> both review axes closed -> CPU slice accepted
{04 terminal evidence, 05 terminal evidence, CPU report readiness} -> 06 actual reports and final acceptance
```

Historical parallel work:01 and the pure03 module started after the freeze without touching uncommitted reused code.02`6129aefe`and03`15186817`still satisfy CPU dependencies; the earlier H800 configuration/lifecycle/review evidence remains historical. Both failed H800 formal attempts and D36's wait decision are retained separately. At the previous D37 checkpoint, H200 preparation plus independent CPU implementation replaced H800 waiting; actual H200 startup/CPU join now supersedes that preparation status. Upstream acceptance remains independent.

The original02/03 launch edges were CPU readiness checkpoints, not circular GPU prerequisites;02 is now fully accepted through D16. B's actual firstACK/inspection edge is satisfied, but the common native fault and fresh admission still block it.18 H200/cell/32 ceiling remain resource constraints, not A200/profile-PASS gates. S7 does not stop healthy training; this attempt failed natively. Failed/incomplete evidence permits honest06 reporting, not complete-cell acceptance.

## Verification strategy

1. **Documentation:** trace each original requirement to a spec section or ticket; check local links, counts and the graph above.
2. **Input (01):** run the extended `tests/manual/agent_opd/check_swe_inputs.py` on CPU. Locally: the existing historical GLM copies with `all_assistants` and a synthetic file set with `loss_masked`. In a CPU RJob that mounts posttrain: the source audit `audit_swe1003_sources.py`, then the `loss_masked` checks on the 8 files in place, with no input copy (D25) — with one open conversation the sequence equals the native single-source sequence; with 32 × 8 the order properties hold on the raw mixer output. Native instance/repository identity and exact-text proxy coverage are reported separately under S2; unavailable native identity stays null / unverified.
3. **Measurement (02):** a fast CPU test of the per-sample sums with uneven lengths and a two-rank CP split, following the reused `tests/fast/test_swe_tis.py`; GPU acceptance happens at the first update of 04 rather than in a separate smoke (D16).
4. **Profile (03):** a fast CPU test with a synthetic update sequence and hand-computed expected values, including D28–D32 and first entries with fewer/more than N observations; offline rebuild from complete paired JSONL files; fault injection for a failing write, row-count/uid mismatch and subsequent update suppression; measured update and query time. CPU module evidence does not verify rollout integration.
5. **Formal cells (04, 05):** after A's first actual successful native update, complete and record the profile inspection before B's resource admission, reporting auxiliary failure without stopping healthy training. Report stage times again near update 20; check actual 200 successful updates separately from complete paired profile files, per-update consistency and rebuild. Mark incomplete profile ranges explicitly under S7.
6. **Report (06):** recompute every reported value from verified retained records, distinguish native training from profile acceptance and retain honest failed/incomplete dispositions. Dimensionless gaps do not establish controlled comparisons across teachers or turn composition.

Each ticket records commands and evidence in `progress.md` and a dated test report in this directory.

## Current frontier

**Independent CPU slice accepted:** the final219489ef repair passed12 affected tests and2 joined prefix-zero CLI cases; both review axes are closed ([review](review.md#offline-review-repair-state--2026-11-10)).06 final report acceptance still requires actual completed A/B records. **D38 native action:** the single-H200 diagnostic passed in72 seconds and independently demonstrates896MiB extra inactive retention when moments reuse the former transient segment. Implement the smallest earlier state-initialization correction through existing native APIs, preserve checkpoint-restored state/step, run focused CPU checks/review, then verify actual formal train→sleep→weight-update→next-train before accepting a full-workload repair. The original allocation owner remains unproven. See[the native diagnostic](test_report_2026-11-10_allocator_probe.md#native-result--pass).

Ticket01 is accepted including D34: the original-source112K CPU audit,512 native parity draws and2,048 interleaved raw draws passed; job/replica Succeeded at11:47:11Z and source identities reconcile ([current length/source report](test_report_2026-11-09_length_budgets.md#completed112k-original-source-audit)). The [historical128K report](test_report_2026-11-09_source_audit.md) retains its original policy and results. D26 keeps32×8 from the pre-length eligible median90; current simulated spans and absent post-length median are limitations, not a new blocker or native trend acceptance. The03 module retains D28–D32 CPU evidence ([test report](test_report_2026-11-08_profile_remaining_gap.md)) and historical query/baseline/partial-write checks ([review test report](test_report_2026-11-09_review_execution.md)). Native-count consistency and the full CPU integration path are now accepted in [ticket03](tickets/03-distillation-profile.md), with [201-PASS evidence](test_report_2026-11-10_profile_integration.md); actual GPU/profile verification remains separate. Current state is owned by [progress](progress.md#in-progress).

The historical2026-11-09T07:56Z upstream refresh at `c52991ac` recorded capacity job`exp-1109-144110-764758` failing at initial trainer-to-rollout weight synchronization after600s, before rollout collection or optimizer updates. This failure remains unaccepted evidence, as do earlier acquisition227<231 and historical interrupted scoring. Those historical outcomes are not relabeled byD35; exact limits remain in [the H800 preparation report](test_report_2026-11-09_h800_preparation.md#upstream-prerequisite-failure-2026-11-09t0756z).

Native verification must still show the corrected full-workload offload and subsequent training path. The accepted controlled diagnostic does not establish the old full-model allocation owner or certify either200-update formal cell. Exact evidence remains linked in[progress](progress.md#in-progress); both final cell records are required by06.

Historical H800 preparation`4863e68e`, correction`059a6a75`, profile configuration`ec002ea8`and its4/4 native-argv dry-runs remain in[the configuration report](test_report_2026-11-10_formal_configuration.md), not proof of current H200 runtime. The earlier16-case lifecycle inspection and exact mock limits remain in[its retained section](test_report_2026-11-10_formal_configuration.md#pre-formal-sample-lifecycle-check). D37's separate H200 configuration is committed without altering the old H800 file. Full still visits200 distinct banks once each with`bank_uses=50`. Current B teacher is configured2 H200/TP2, not native verified. B may follow ACK/inspection only when fresh resources fit the32 ceiling; do not replace that budget condition with A200/profile-PASS/extra-approval/GPU-smoke gates. Native acceptance and S7 isolation are unchanged.

D34's input length slice is complete: adapter/native-request bounds, CPU boundary/config checks and the existing in-place112K prompt/16K completion audit have verified evidence separate from the historical128K run. No repeat full-source scan or sampling change is needed for Ticket01 closure. D35 explicitly adopts the now-completed H800 capacity basis; it does not certify02/03 integration, B's native runtime or either200-update profile.
