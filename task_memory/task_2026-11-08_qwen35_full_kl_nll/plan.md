## Modification History

| Date | Change |
| --- | --- |
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

# Plan

**Phase: IMPLEMENTATION.** The user froze the documents on 2026-11-08 (requirements Round 5). GPU actions follow the tickets and S8.

## Scope and ownership

Behavior is owned by [spec.md](spec.md); raw requests and actual answers are in [requirements.md](requirements.md). This plan owns ticket dependencies and the verification strategy only.

## Tickets

| Ticket | Deliverable | Blocked by |
| --- | --- | --- |
| [01](tickets/01-interleaved-turn-order.md) | Interleaved turn order in the committed SWE input adapter, with the SWE-1003 loss-masked turn source and its source audit | Documentation freeze; D23–D27 |
| [02](tickets/02-per-turn-sums.md) | Per-turn RKL/NLL sums in the optimizer-step record | Reused Ticket02 committed and smoke-passed on `agent-opd`, then merged (D1) |
| [03](tickets/03-distillation-profile.md) | Distillation profile module, persistence and rollout-side integration | Documentation freeze (module and CPU test); 02 (integration) |
| [04](tickets/04-a-full.md) | Accepted A/full formal cell | 01, 02, 03 |
| [05](tickets/05-b-full.md) | Accepted B/full formal cell | 01, 02, 03; 04 first-update inspection |
| [06](tickets/06-profile-report.md) | Final profile report and archive | 04, 05 |

Dependency graph:

```text
documentation freeze -> {01, 03-module}
D28–D31 in the spec -> 03-module revision (CPU only)
D23–D27 in the spec -> 01 revision: {adapter code + local checks, source audit (CPU RJob)} -> checks on the files in place (CPU RJob)
reused Ticket02 accepted -> merge agent-opd -> 02 -> 03-integration
{01, 02, 03} -> 04
04 first-update inspection -> 05
{04, 05} -> 06
```

Parallel work: 01 and the pure profile module of 03 touch no uncommitted reused code, so they start right after the freeze while the reused Ticket02 is still in progress. This narrows D1, which blocked all implementation on the reused Ticket02; the freeze confirmation covers this narrowing. 02 and the integration part of 03 wait for the merge.

## Verification strategy

1. **Documentation:** trace each original requirement to a spec section or ticket; check local links, counts and the graph above.
2. **Input (01):** run the extended `tests/manual/agent_opd/check_swe_inputs.py` on CPU. Locally: the GLM copies with `all_assistants` and a synthetic file set with `loss_masked`. In a CPU RJob that mounts posttrain: the source audit `audit_swe1003_sources.py`, then the `loss_masked` checks on the 8 files in place — with one open conversation the sequence equals the native single-source sequence; with 32 × 8 the order properties hold on the raw mixer output.
3. **Measurement (02):** a fast CPU test of the per-sample sums with uneven lengths and a two-rank CP split, following the reused `tests/fast/test_swe_tis.py`; GPU acceptance happens at the first update of 04 rather than in a separate smoke (D16).
4. **Profile (03):** a fast CPU test with a synthetic update sequence and hand-computed expected values, including the baseline cases of D28–D31; offline rebuild from the JSONL files; fault injection for a failing write and a row-count mismatch; measured update and query time.
5. **Formal cells (04, 05):** inspect the first update before starting B; report stage times again near update 20, when the open conversations' progress has spread; then check 200 successful updates, complete profile files and per-update consistency flags against the spec.
6. **Report (06):** recompute every reported value from the retained files.

Each ticket records commands and evidence in `progress.md` and a dated test report in this directory.

## Current frontier

The 03 module is reopened for D28–D31 (remaining gap, run-relative gap, and the trend and recovery gap restated in remaining-gap units); this CPU-only change is the next step, with the baseline lengths of D32 as config defaults. 01 is reopened for the SWE-1003 0913 data (D23–D27): the adapter code and its local checks pass ([test report](test_report_2026-11-08_swe1003_turn_source.md)); the source audit and the checks on the files in place need a CPU RJob that mounts posttrain; the user's round-10 request to hand that submission to dsv4 was not carried out (see [progress](progress.md#round-10-remaining-gap)), so those two items are deferred. The interleaved order itself was verified on the GLM copies ([test report](test_report_2026-11-08_interleaved_turn_order.md)). 02 and the 03 integration wait for the reused Ticket02 to be committed and smoke-passed on `agent-opd`, then merged. Its code is committed, but its 256-turn capacity smoke fails with an out-of-memory error ([progress](progress.md#reused-ticket02-state-read-only-2026-11-08-after-c7dfbf5a)). By D22 this task waits for that fix to be complete before merging, and starts no part of ticket 02 early.
