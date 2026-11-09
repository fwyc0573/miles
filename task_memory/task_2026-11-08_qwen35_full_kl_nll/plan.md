## Modification History

| Date | Change |
| --- | --- |
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

**Phase: IMPLEMENTATION / MERGE_AND_PROFILE_INTEGRATION.** Review repairs,Ticket01 and theD35 H800 capacity basis are complete. D35 authorizes candidate consolidation, which is stillpending, before02/03 integration. GPU actions follow the tickets andS8; formal runtime acceptance is unchanged.

## Scope and ownership

Behavior is owned by [spec.md](spec.md); raw requests and actual answers are in [requirements.md](requirements.md). This plan owns ticket dependencies and the verification strategy only.

## Tickets

| Ticket | Deliverable | Blocked by |
| --- | --- | --- |
| [01](tickets/01-interleaved-turn-order.md) | Interleaved turn order in the committed SWE input adapter, with the SWE-1003 loss-masked turn source and its source audit | Documentation freeze; D23–D27 |
| [02](tickets/02-per-turn-sums.md) | Per-turn RKL/NLL sums: CPU implementation-ready, then GPU acceptance at A's first update | D35 capacity basis accepted; verified `agent-opd-h800-capacity` candidate merged |
| [03](tickets/03-distillation-profile.md) | Distillation profile module, persistence and rollout-side integration | Documentation freeze (module and CPU test); 02 CPU implementation-ready (integration) |
| [04](tickets/04-a-full.md) | A/full native training and separately verified profile | 01 accepted, 02 CPU implementation-ready, 03 integration CPU-ready |
| [05](tickets/05-b-full.md) | B/full native training and separately verified profile | 01 accepted, 02 CPU implementation-ready, 03 integration CPU-ready; 04 actual first successful update and inspection completed |
| [06](tickets/06-profile-report.md) | Final profile report and archive with explicit complete/incomplete disposition | 04, 05 terminal evidence and completion checks |

Dependency graph:

```text
documentation freeze -> {01, 03-module}
D28–D32 in the spec -> 03-module revision (CPU only)
D23–D27 in the spec -> 01 revision: {adapter code + local checks, source audit (CPU RJob)} -> checks on the files in place (CPU RJob)
D35 H800 capacity basis accepted -> merge agent-opd-h800-capacity candidate -> 02 CPU implementation-ready -> 03-integration CPU-ready
{01 accepted, 02 CPU implementation-ready, 03-integration CPU-ready} -> 04 launch
04 actual first successful update -> inspection completed -> {02 GPU acceptance evidence, 05 resource admission}
{04 terminal evidence, 05 terminal evidence} -> 06
```

Historical parallel work: 01 and the pure profile module of 03 touched no uncommitted reused code and started after the freeze; both now have CPU acceptance. The freeze narrowed D1 for those slices only. Current02 and03 integration still wait for the candidate merge underD35; upstream's separate acceptance may continue independently and is no longer their blocking edge.

The table's 02/03 edges into formal cells are CPU readiness checkpoints, not full ticket closure. 02 remains unaccepted until its A runtime checks are verified, but waiting for that before launching A would be circular. B requires A's real successful native update and a completed inspection, not a PASS auxiliary profile verdict or all 200 A updates. S7 errors continue healthy training and are reported separately as incomplete profile acceptance. Failed/incomplete terminal evidence permits honest reporting in 06; it does not satisfy complete-cell acceptance.

## Verification strategy

1. **Documentation:** trace each original requirement to a spec section or ticket; check local links, counts and the graph above.
2. **Input (01):** run the extended `tests/manual/agent_opd/check_swe_inputs.py` on CPU. Locally: the existing historical GLM copies with `all_assistants` and a synthetic file set with `loss_masked`. In a CPU RJob that mounts posttrain: the source audit `audit_swe1003_sources.py`, then the `loss_masked` checks on the 8 files in place, with no input copy (D25) — with one open conversation the sequence equals the native single-source sequence; with 32 × 8 the order properties hold on the raw mixer output. Native instance/repository identity and exact-text proxy coverage are reported separately under S2; unavailable native identity stays null / unverified.
3. **Measurement (02):** a fast CPU test of the per-sample sums with uneven lengths and a two-rank CP split, following the reused `tests/fast/test_swe_tis.py`; GPU acceptance happens at the first update of 04 rather than in a separate smoke (D16).
4. **Profile (03):** a fast CPU test with a synthetic update sequence and hand-computed expected values, including D28–D32 and first entries with fewer/more than N observations; offline rebuild from complete paired JSONL files; fault injection for a failing write, row-count/uid mismatch and subsequent update suppression; measured update and query time. CPU module evidence does not verify rollout integration.
5. **Formal cells (04, 05):** after A's first actual successful native update, complete and record the profile inspection before B's resource admission, reporting auxiliary failure without stopping healthy training. Report stage times again near update 20; check actual 200 successful updates separately from complete paired profile files, per-update consistency and rebuild. Mark incomplete profile ranges explicitly under S7.
6. **Report (06):** recompute every reported value from verified retained records, distinguish native training from profile acceptance and retain honest failed/incomplete dispositions. Dimensionless gaps do not establish controlled comparisons across teachers or turn composition.

Each ticket records commands and evidence in `progress.md` and a dated test report in this directory.

## Current frontier

Ticket01 is accepted including D34: the original-source112K CPU audit,512 native parity draws and2,048 interleaved raw draws passed; job/replica Succeeded at11:47:11Z and source identities reconcile ([current length/source report](test_report_2026-11-09_length_budgets.md#completed112k-original-source-audit)). The [historical128K report](test_report_2026-11-09_source_audit.md) retains its original policy and results. D26 keeps32×8 from the pre-length eligible median90; current simulated spans and absent post-length median are limitations, not a new blocker or native trend acceptance. The03 module has recorded D28–D32 CPU evidence ([test report](test_report_2026-11-08_profile_remaining_gap.md)); historical entry queries, baseline boundaries and partial-write isolation also pass ([review test report](test_report_2026-11-09_review_execution.md)). Native-count consistency and the full integration path in [ticket03](tickets/03-distillation-profile.md) remain pending. Current state is owned by [progress](progress.md#in-progress).

The historical2026-11-09T07:56Z upstream refresh at `c52991ac` recorded capacity job`exp-1109-144110-764758` failing at initial trainer-to-rollout weight synchronization after600s, before rollout collection or optimizer updates. This failure remains unaccepted evidence, as do earlier acquisition227<231 and historical interrupted scoring. Those historical outcomes are not relabeled byD35; exact limits remain in [the H800 preparation report](test_report_2026-11-09_h800_preparation.md#upstream-prerequisite-failure-2026-11-09t0756z).

CurrentD35 frontier: merge the verified`agent-opd-h800-capacity`candidate and its retained preparation artifacts into the parent, recording the actual merge commit and source resolution. Then execute02 CPU implementation-ready ->03 integration CPU-ready ->04 formal launch ->A first successful update/inspection ->05 resource admission. H800 capacity is accepted, not merely startup/synchronization; the result and limits are in [the D35 adoption record](test_report_2026-11-09_h800_preparation.md#d35-parent-adoption-2026-11-10). Merge,02 per-turn work and03 integration have not started; no formal cell has begun. Upstream frozen-D11 work remains independent, not a parent blocker. Formal cells use `before-steptron-run` and existing per-sample isolation/soft gates; D16 verifies the native profile at A's first formal update, without another GPU smoke.

D34's input length slice is complete: adapter/native-request bounds, CPU boundary/config checks and the existing in-place112K prompt/16K completion audit have verified evidence separate from the historical128K run. No repeat full-source scan or sampling change is needed for Ticket01 closure. D35 explicitly adopts the now-completed H800 capacity basis; it does not certify02/03 integration, B's native runtime or either200-update profile.
