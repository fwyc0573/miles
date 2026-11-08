## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Freeze the nine-ticket dependency graph after user confirmation. |
| 2026-11-08 | Propose shared, independently verifiable prerequisites and four parallel formal-cell tickets. |

# Plan

**Phase: DOCS_LANDING_COMPLETE.** The user confirmed the nine-ticket graph and specification. Runtime work is pending; documentation completion does not satisfy any runtime ticket.

## Scope and ownership

The protocol is owned by [spec.md](spec.md); raw requests and actual answers are in [requirements.md](requirements.md). This plan owns dependencies and verification strategy rather than maintaining another parameter table.

Primary agent owns interview, shared-understanding confirmation, coordination and final acceptance. Scoped agents may investigate or implement independently owned slices after approval; they return evidence and leave final acceptance to the primary.

## Frozen tickets

| Ticket | Deliverable | Blocked by |
| --- | --- | --- |
| [01](tickets/01-native-swe-inputs.md) | GLM-5.2 SWE default-loader parity and frozen four-cell inputs | Documentation freeze — complete |
| [02](tickets/02-replay-training-and-metrics.md) | Native full/r256 training with replay and exact per-update KL/TIS | 01 |
| [03](tickets/03-hf-async-swe-evaluation.md) | HF publication → asynchronous SWE evaluation → scoped weight release | 01 |
| [04](tickets/04-a-full.md) | Accepted A/full formal cell | 02, 03 |
| [05](tickets/05-a-r256.md) | Accepted A/r256 formal cell | 02, 03 |
| [06](tickets/06-b-full.md) | Accepted B/full formal cell | 02, 03 |
| [07](tickets/07-b-r256.md) | Accepted B/r256 formal cell | 02, 03 |
| [09](tickets/09-original-student-baseline.md) | Shared original4B SWE baseline added by D8 | 01, 03 |
| [08](tickets/08-four-cell-comparison.md) | Auditable four-cell comparison and final archive | 04, 05, 06, 07, 09 |

Dependency graph:

```text
documentation freeze -> 01 -> {02, 03}
{02, 03} -> {04, 05, 06, 07}
{01, 03} -> 09
{04, 05, 06, 07, 09} -> 08
```

02 and03 share identity/configuration contracts from01, with separate implementation ownership. Native integrated training-to-export verification is required before the formal frontier. The four formal tickets have no artificial serial edge; actual simultaneous admission remains constrained by the resource contract. Each ticket owns its checkpoint evaluations, which overlap subsequent training updates when resources permit.

09 was added after the initial decomposition by explicitD8 approval; its ID does not define execution order. Baseline scoring and formal training are independent after their stated prerequisites, so final baseline completion is not a blocker of04–07. Follow graph edges rather than numeric order.

## Verification strategy

1. **Documentation:** trace every original requirement to a spec section/ticket; check source citations, local links, arithmetic, DAG and explicit unresolved decisions. Run a phase `check-progress` before asking for freeze.
2. **Inputs:** compare actual native and adapted loader outputs on representative multi-turn and filtering cases, then freeze the effective source population/configuration. Source inspection alone does not establish data equivalence.
3. **Training:** deterministic full-length scheduling/accounting checks, fault injection for a hung/late request, native representative batch verification and at least one bank transition per mode. Check real loss inputs and native counters rather than parsed flags alone.
4. **HF/evaluation:** verify real export identity and load, completion-order persistence while another attempt is held, actual SWE agent/grader operation and reader-safe deletion. A simulated scorer is insufficient for native benchmark acceptance.
5. **Formal cells:** validate complete observed updates, KL/TIS, evaluation and lifecycle records against the frozen contract. Record failed attempts separately and preserve finished work.
6. **Reporting:** recompute requested comparison from retained evidence; mark incomplete cells precisely and archive exact artifact paths and observed limits.

## Current frontier

Documentation landing is complete. The subsequent implementation frontier is01; after01,02and03 may proceed in parallel. Actual runtime results remain absent, and later tickets wait for their recorded prerequisites.
