## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Continue scoped retained-log RCA and independent baseline9/400; keep additional GPU experiments approval-dependent. |
| 2026-11-09 | Record the failed single D12 acquisition and continue read-only02 RCA in parallel with08; no additional experiment approval inferred. |
| 2026-11-09 | Accept Ticket03 after actual native isolation/review; advance02 to the approved D12 experiment while08 continues. |
| 2026-11-08 | Route parallel02/03 to the measured acquisition and filesystem blockers while08 continues independently. |
| 2026-11-08 | Reaccept D11 Ticket01 and move the new-data runtime frontier to parallel02/03;08 is already independently running. |
| 2026-11-08 | Clarify08's existing capability-specific prerequisites after independent readiness review; retain the full01/03 gates for04–07. |
| 2026-11-08 | Reopen Ticket01 for D11's replacement dataset while continuing independent training/evaluation implementation checks. |
| 2026-11-08 | Accept Ticket01 and move the integration/acceptance frontier to parallel Tickets02 and03. |
| 2026-11-08 | Start authorized execution and distinguish independent development from prerequisite-dependent runtime acceptance. |
| 2026-11-08 | Renumber the baseline (08) and comparison (09) tickets into dependency order after the post-freeze standards review; restore word spacing. |
| 2026-11-08 | Freeze the nine-ticket dependency graph after user confirmation. |
| 2026-11-08 | Propose shared, independently verifiable prerequisites and four parallel formal-cell tickets. |

# Plan

**Phase: IMPLEMENTATION_IN_PROGRESS.** Documentation landing is complete and the user authorized parallel execution. Runtime acceptance remains outstanding.

## Scope and ownership

The protocol is owned by [spec.md](spec.md); raw requests and actual answers are in [requirements.md](requirements.md). This plan owns dependencies and verification strategy rather than maintaining another parameter table.

Primary agent owns interview, shared-understanding confirmation, coordination and final acceptance. Scoped agents may investigate or implement independently owned slices after approval; they return evidence and leave final acceptance to the primary.

## Frozen tickets

| Ticket | Deliverable | Blocked by |
| --- | --- | --- |
| [01](tickets/01-native-swe-inputs.md) | Accepted D11 source identity, default-loader parity and frozen four-cell inputs | done; documentation freeze and D11 amendment |
| [02](tickets/02-replay-training-and-metrics.md) | Native full/r256 training with replay and exact per-update KL/TIS | 01 |
| [03](tickets/03-hf-async-swe-evaluation.md) | HF publication → asynchronous SWE evaluation → scoped weight release | 01 |
| [04](tickets/04-a-full.md) | Accepted A/full formal cell | 02, 03 |
| [05](tickets/05-a-r256.md) | Accepted A/r256 formal cell | 02, 03 |
| [06](tickets/06-b-full.md) | Accepted B/full formal cell | 02, 03 |
| [07](tickets/07-b-r256.md) | Accepted B/r256 formal cell | 02, 03 |
| [08](tickets/08-original-student-baseline.md) | Shared original 4B SWE baseline added by D8 | 01, 03 |
| [09](tickets/09-four-cell-comparison.md) | Auditable four-cell comparison and final archive | 04, 05, 06, 07, 08 |

Dependency graph:

```text
documentation freeze -> 01 -> {02, 03}
{02, 03} -> {04, 05, 06, 07}
{01, 03} -> 08
{04, 05, 06, 07, 08} -> 09
```

02 and 03 share identity/configuration contracts from 01, with separate implementation ownership. Native integrated training-to-export verification is required before the formal frontier. The four formal tickets have no artificial serial edge; actual simultaneous admission remains constrained by the resource contract. Each ticket owns its checkpoint evaluations, which overlap subsequent training updates when resources permit.

The edges above gate integration and acceptance. Independent 02 algorithm/replay development and 03 evaluation-lifecycle development can proceed while 01 finishes input parity and identity verification; neither may consume unverified inputs in a formal run or claim completion before 01 passes. This uses the user's parallel-execution approval without changing any experiment or acceptance criterion.

08 was added by explicit D8 approval after the initial decomposition and renumbered after the post-freeze standards review, so ticket numbers now follow dependency order. Baseline scoring and formal training are independent after their stated prerequisites, so final baseline completion is not a blocker of 04–07.

Ticket08's edges refer to its stated capability slices:01 original-model/task identities and03 native SWE evaluation capability. Independent readiness review verified these slices from real original4B/HF3 agent/grader results, reader exit, failure recovery and cloud lifecycle evidence. At baseline admission,D11's training-input activation and03's then-unfinished isolation did not block08. That limited readiness decision did not complete the full tickets;01 and03 subsequently passed their independent acceptance checks.02 remains a prerequisite for04–07,not for08.

## Verification strategy

1. **Documentation:** trace every original requirement to a spec section/ticket; check source citations, local links, arithmetic, DAG and explicit unresolved decisions. Run a phase `check-progress` before asking for freeze.
2. **Inputs:** compare actual native and adapted loader outputs on representative multi-turn and filtering cases, then freeze the effective source population/configuration. Source inspection alone does not establish data equivalence.
3. **Training:** deterministic full-length scheduling/accounting checks, fault injection for a hung/late request, native representative batch verification and at least one bank transition per mode. Check real loss inputs and native counters rather than parsed flags alone.
4. **HF/evaluation:** verify real export identity and load, completion-order persistence while another attempt is held, actual SWE agent/grader operation and reader-safe deletion. A simulated scorer is insufficient for native benchmark acceptance.
5. **Formal cells:** validate complete observed updates, KL/TIS, evaluation and lifecycle records against the frozen contract. Record failed attempts separately and preserve finished work.
6. **Reporting:** recompute requested comparison from retained evidence; mark incomplete cells precisely and archive exact artifact paths and observed limits.

## Current frontier

01 is reaccepted for D11 and03 is capability-accepted after actual HF2-failure/HF3 native grading and independent phase review. Small-run native RKL/TIS/PPO reconstruction passes. The original256-turn acquisitions failed at206/224 valid; the single approved D12 routing-only A/r256 experiment`exp-1109-010244-280221` also failed at227/256 before scoring.02 now completes read-only RCA from retained full logs; any further GPU experiment requires a concrete approval rather than another D12 retry. Formal profiles and all science/deadline/threshold parameters remain unchanged.08 independently continues with9/400 persisted outcomes and no full avg@4. Historical GLM and the eight-slot isolation smoke do not certify replacement-data GPU capacity;04–07 remain blocked on02 and unstarted.
