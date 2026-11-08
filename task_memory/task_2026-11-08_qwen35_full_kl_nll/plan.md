## Modification History

| Date | Change |
| --- | --- |
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

**Phase: IMPLEMENTATION / REVIEW_REPAIRS.** The user froze the documents on 2026-11-08 (requirements Round 5) and authorized review repairs and resumed execution on 2026-11-09. GPU actions follow the tickets and S8; D1/D22 remain mandatory.

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

The 03 module has recorded D28–D32 CPU evidence ([test report](test_report_2026-11-08_profile_remaining_gap.md)); historical entry queries, baseline boundaries and partial-write isolation now also pass CPU checks ([review test report](test_report_2026-11-09_review_execution.md)). Native-count consistency and the full integration path in [ticket 03](tickets/03-distillation-profile.md) remain pending. Its integration has not started. 01's adapter and local checks pass ([test report](test_report_2026-11-08_swe1003_turn_source.md)); the primary's latest [progress record](progress.md#in-progress) reports the in-place CPU audit/parity RJob `exp-1109-031258-820360` Running, with its launcher alive. There is no completed source audit/parity result yet: items 5–6 remain pending and 01 is not accepted; submission is no longer deferred. Historical GLM order evidence ([test_report](test_report_2026-11-08_interleaved_turn_order.md)) does not substitute for current-source parity.

The current upstream gate is owned by [spec S0](spec.md#s0-复用与改动范围): at `f33546f4` plus retained local evidence, reused Ticket02 is NOT ACCEPTED. Historical green scoring completed 31 microbatches/rank but was externally stopped before optimizer; DeepSWE D12 collected 227 < 231 and never reached scoring. D1/D22 therefore still block merge, every part of 02, and the 03 integration. Current independent work is doc repair, running 01 CPU evidence and 03 module verification; no formal cell has begun and no GPU/profile runtime gate is claimed passed.
