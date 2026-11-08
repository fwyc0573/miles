## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the six-ticket dependency graph and verification strategy; awaiting Q17–Q19 and freeze. |

# Plan

**Phase: DOCS_LANDING.** No implementation or GPU action is authorized until the user freezes the documents.

## Scope and ownership

Behavior is owned by [spec.md](spec.md); raw requests and actual answers are in [requirements.md](requirements.md). This plan owns ticket dependencies and the verification strategy only.

## Tickets

| Ticket | Deliverable | Blocked by |
| --- | --- | --- |
| [01](tickets/01-indexed-turn-order.md) | Indexed turn order in the committed SWE input adapter | Documentation freeze |
| [02](tickets/02-per-turn-sums.md) | Per-turn KL/NLL sums in the optimizer-step record | Reused Ticket02 committed and smoke-passed on `agent-opd`, then merged (D1) |
| [03](tickets/03-distillation-profile.md) | Distillation profile module, persistence and rollout-side integration | Documentation freeze (module and CPU test); 02 (integration) |
| [04](tickets/04-a-full.md) | Accepted A/full formal cell | 01, 02, 03 |
| [05](tickets/05-b-full.md) | Accepted B/full formal cell | 01, 02, 03; 04 first-update inspection |
| [06](tickets/06-profile-report.md) | Final profile report and archive | 04, 05 |

Dependency graph:

```text
documentation freeze -> {01, 03-module}
reused Ticket02 accepted -> merge agent-opd -> 02 -> 03-integration
{01, 02, 03} -> 04
04 first-update inspection -> 05
{04, 05} -> 06
```

Parallel work: 01 and the pure profile module of 03 touch no uncommitted reused code, so they start right after the freeze while the reused Ticket02 is still in progress. This narrows D1, which blocked all implementation on the reused Ticket02; the freeze confirmation covers this narrowing. 02 and the integration part of 03 wait for the merge.

## Verification strategy

1. **Documentation:** trace each original requirement to a spec section or ticket; check local links, counts and the graph above.
2. **Input order (01):** run the extended `tests/manual/agent_opd/check_swe_inputs.py` on CPU against the real pinned source copies; compare population and permutation hashes with the Q41 manifest when the source bytes match.
3. **Measurement (02):** a fast CPU test of the per-sample sums with uneven lengths and a two-rank CP split, following the reused `tests/fast/test_swe_tis.py`; GPU acceptance happens at the first update of 04 rather than in a separate smoke (D16).
4. **Profile (03):** a fast CPU test with a synthetic update sequence and hand-computed expected values; offline rebuild from the JSONL files; fault injection for a failing write and a row-count mismatch; measured update and query time.
5. **Formal cells (04, 05):** inspect the first update before starting B; then check 200 successful updates, complete profile files and per-update consistency flags against the spec.
6. **Report (06):** recompute every reported value from the retained files.

Each ticket records commands and evidence in `progress.md` and a dated test report in this directory.

## Current frontier

Waiting for answers to Q17–Q19 and the user's freeze confirmation.
