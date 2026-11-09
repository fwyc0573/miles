## Modification History

| Date | Change |
| --- | --- |
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

**Phase: IMPLEMENTATION / H800_PREPARATION.** Review repairs andTicket01 are complete. D33 authorizes H800 execution without a task GPU-count cap; GPU actions follow the tickets andS8. D1/D22 remain mandatory for integration.

## Scope and ownership

Behavior is owned by [spec.md](spec.md); raw requests and actual answers are in [requirements.md](requirements.md). This plan owns ticket dependencies and the verification strategy only.

## Tickets

| Ticket | Deliverable | Blocked by |
| --- | --- | --- |
| [01](tickets/01-interleaved-turn-order.md) | Interleaved turn order in the committed SWE input adapter, with the SWE-1003 loss-masked turn source and its source audit | Documentation freeze; D23–D27 |
| [02](tickets/02-per-turn-sums.md) | Per-turn RKL/NLL sums: CPU implementation-ready, then GPU acceptance at A's first update | Reused Ticket02 accepted on `agent-opd`, then merged (D1/D22) |
| [03](tickets/03-distillation-profile.md) | Distillation profile module, persistence and rollout-side integration | Documentation freeze (module and CPU test); 02 CPU implementation-ready (integration) |
| [04](tickets/04-a-full.md) | A/full native training and separately verified profile | 01 accepted, 02 CPU implementation-ready, 03 integration CPU-ready |
| [05](tickets/05-b-full.md) | B/full native training and separately verified profile | 01 accepted, 02 CPU implementation-ready, 03 integration CPU-ready; 04 actual first successful update and inspection completed |
| [06](tickets/06-profile-report.md) | Final profile report and archive with explicit complete/incomplete disposition | 04, 05 terminal evidence and completion checks |

Dependency graph:

```text
documentation freeze -> {01, 03-module}
D28–D32 in the spec -> 03-module revision (CPU only)
D23–D27 in the spec -> 01 revision: {adapter code + local checks, source audit (CPU RJob)} -> checks on the files in place (CPU RJob)
reused Ticket02 accepted (D1/D22) -> merge agent-opd -> 02 CPU implementation-ready -> 03-integration CPU-ready
{01 accepted, 02 CPU implementation-ready, 03-integration CPU-ready} -> 04 launch
04 actual first successful update -> inspection completed -> {02 GPU acceptance evidence, 05 resource admission}
{04 terminal evidence, 05 terminal evidence} -> 06
```

Parallel work: 01 and the pure profile module of 03 touch no uncommitted reused code, so they start right after the freeze while the reused Ticket02 is still in progress. This narrows D1, which blocked all implementation on the reused Ticket02; the freeze confirmation covers this narrowing. 02 and the integration part of 03 wait for the merge.

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

Ticket01 is accepted: the real-source CPU audit,512 native parity draws and2,048 interleaved draws passed; job/replica Succeeded ([source test report](test_report_2026-11-09_source_audit.md)). The03 module has recorded D28–D32 CPU evidence ([test report](test_report_2026-11-08_profile_remaining_gap.md)); historical entry queries, baseline boundaries and partial-write isolation also pass ([review test report](test_report_2026-11-09_review_execution.md)). Native-count consistency and the full integration path in [ticket03](tickets/03-distillation-profile.md) remain pending. Current state is owned by [progress](progress.md#in-progress).

At the2026-11-09T05:10Z read-only refresh, upstream `agent-opd` was at `d8c27b75` with no newer capacity acceptance. The gate defined in [specS0](spec.md#s0-复用与改动范围) remains NOT MET: historical patched scoring was stopped before optimizer; the latest DeepSWE acquisition collected227<231 and produced zero updates. D1/D22 block merge, every part of02 and03 integration. Independent authorized CPU work is complete; the next executable integration step requires upstream acceptance. No formal cell has begun.

D33 adds executable H800 resource preparation: inspect existing native launch mechanisms, H800 memory/topology constraints and task-scoped admission; validate the chosen configuration on CPU before GPU submission. Independently monitor the already-submitted upstream capacity attempt, using current evidence rather than resubmitting it. OnceD1/D22 is satisfied, merge and execute02 ->03 integration ->04 ->05 underD33. Formal cells additionally use the `before-steptron-run` workflow and the existing per-sample failure isolation/soft-gate rules.

D34 now reopens the input length slice: adapter/native-request bounds and audit workflow changes run in parallel with isolated launcher wiring. After CPU boundary/config checks, run the existing in-place CPU audit at112K prompt/16K completion and record its actual output separately. Historical source identities/exclusions remain valid; historical length-rejection/span figures do not verify the new threshold. This work proceeds before the unchanged upstream integration gate.
