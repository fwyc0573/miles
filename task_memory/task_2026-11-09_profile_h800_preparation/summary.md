## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Archive the verified, scoped nullable GPU admission implementation. |

# Scoped Admission Summary

Task ID: `profile-h800-admission-20261109`.

## Outcome

The existing admission mechanism now supports explicit `None` / JSON `null` in the selected GPU ceiling. Both `temporary_task_allocation.nonpreemptible_gpus` and `personal_nonpreemptible_gpus` can use that value without imposing a surrogate count ceiling or forcing preemption. Required fields remain required; omitted ceilings do not mean unlimited.

Fresh paginated task/personal inventory reads, finite admission denial, finite task-window overflow preemption, expiry handoff, and already-submitted receipt semantics remain intact. `validate_allocation` accepts an explicitly nullable receipt ceiling only when it matches the selected recorded policy, while retaining job, identity, resource, scope and preemption binding.

## Deliverables

Paths are relative to `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`.

- `tests/manual/agent_opd/rjob_budget.py`: nullable ceiling and matching allocation validation in the existing admission path.
- `tests/fast/test_rjob_budget.py`: existing finite coverage retained; new nullable, H800 160-GPU, fresh inventory, expiry and persisted allocation-binding regressions.
- `task_memory/task_2026-11-09_profile_h800_preparation/progress.md`: execution evidence and the required progress checkpoint.
- `task_memory/task_2026-11-09_profile_h800_preparation/test_report_2026-11-09_nullable_gpu_admission.md`: exact CPU commands, expected/actual values and verification limits.
- `task_memory/task_2026-11-09_profile_h800_preparation/summary.md`: this scoped completion archive.

## Observed Validation

- Required CPU interpreter: Python 3.12.13.
- Original budget baseline: 10 passed.
- New nullable tests reproduced the pre-change TypeError in both scopes.
- Final affected budget file: 25 passed, 0.25 s.
- Selected existing submission/receipt consumers: 4 passed, 44 deselected, 0.90 s.
- `git diff --check`: passed with no output.
- Two pre-existing SWIG deprecation warnings occurred; no unresolved test failures remain. See the test report for exact commands and values.

## Open and Primary-Owned Work

- No configuration files, platform/RJob operations, parent Ticket02/03 integration, or other worktrees were touched.
- H800 memory/topology/configuration, CPU payload validation and real GPU execution remain with the primary agent.
- Parent branch integration remains subject to the parent task's source-input, scientific, formal-run and merge gates. This scoped change grants no additional platform authorization.
- The initial untracked preparation `requirements.md` and `plan.md` are preserved unchanged and excluded from this slice's commit because they are outside delegated file ownership.
