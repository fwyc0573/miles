## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Archive the verified, scoped nullable GPU admission implementation. |
| 2026-11-09 | Add the verified explicit native launcher length contract and integration limits. |

# Scoped H800 Preparation Summary

Task IDs: `profile-h800-admission-20261109` and `profile-length-launcher-20261109`.

## Outcome

The existing admission mechanism now supports explicit `None` / JSON `null` in the selected GPU ceiling. Both `temporary_task_allocation.nonpreemptible_gpus` and `personal_nonpreemptible_gpus` can use that value without imposing a surrogate count ceiling or forcing preemption. Required fields remain required; omitted ceilings do not mean unlimited.

Fresh paginated task/personal inventory reads, finite admission denial, finite task-window overflow preemption, expiry handoff, and already-submitted receipt semantics remain intact. `validate_allocation` accepts an explicitly nullable receipt ceiling only when it matches the selected recorded policy, while retaining job, identity, resource, scope and preemption binding.

The follow-up native SWE launcher now requires explicit positive integer `context_tokens`, `prompt_tokens`, and `response_tokens`, with prompt plus response not exceeding context. The requested recipe values are 131072/114688/16384. They emit independent native prompt/response flags while preserving training `seq_length`, SGLang context and rollout context at 131072. No literal default, duplicate knob or context-sized response override remains in this launcher.

## Deliverables

Paths are relative to `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`.

- `tests/manual/agent_opd/rjob_budget.py`: nullable ceiling and matching allocation validation in the existing admission path.
- `tests/fast/test_rjob_budget.py`: existing finite coverage retained; new nullable, H800 160-GPU, fresh inventory, expiry and persisted allocation-binding regressions.
- `tests/manual/agent_opd/run_swe_opd.py`: explicit config-boundary length validation and native prompt/response argv wiring.
- `tests/fast/test_swe_launcher.py`: positive/missing/over-budget cases, all four A/B × full/r256 native argv checks and an actual CPU dry-run.
- `tests/fast/test_swe_capacity.py`, `tests/fast/test_swe_native_gradients.py`, `tests/fast/test_megatron_scoring_lifetime.py`: directly affected argv fixtures explicitly set prompt/response budgets in memory; archives stay unchanged.
- `task_memory/task_2026-11-09_profile_h800_preparation/requirements.md` and `plan.md`: primary-created records now included by explicit follow-up authorization; preserve the parent gates and record the length contract/dependencies.
- `task_memory/task_2026-11-09_profile_h800_preparation/progress.md`: execution evidence and the required progress checkpoint.
- `task_memory/task_2026-11-09_profile_h800_preparation/test_report_2026-11-09_nullable_gpu_admission.md`: exact CPU commands, expected/actual values and verification limits.
- `task_memory/task_2026-11-09_profile_h800_preparation/test_report_2026-11-09_native_launch_lengths.md`: exact launcher/argv commands, observed independent length values and pending input integration.
- `task_memory/task_2026-11-09_profile_h800_preparation/summary.md`: this scoped completion archive.

## Observed Validation

- Required CPU interpreter: Python 3.12.13.
- Original budget baseline: 10 passed.
- New nullable tests reproduced the pre-change TypeError in both scopes.
- Final affected budget file: 25 passed, 0.25 s.
- Selected existing submission/receipt consumers: 4 passed, 44 deselected, 0.90 s.
- `git diff --check`: passed with no output.
- Two pre-existing SWIG deprecation warnings occurred; no unresolved test failures remain. See the test report for exact commands and values.
- Admission delivery commit: `1ae93261`, accepted by the primary for later review.
- Launcher baseline: 29 passed; final launcher file: 53 passed, 14.28 s, including an unmocked module dry-run.
- Seven selected tests in the three directly affected argv/hook files passed, 40 deselected, 3.58 s. Existing CPU/deprecation warnings match the baseline; no runtime validation bypass or warning suppression was added.
- Observed argv for A/B × full/r256: prompt 114688, response 16384, seq/SGLang/rollout context 131072, each exactly once. `git diff --check` passed.

## Open and Primary-Owned Work

- No configuration files, platform/RJob operations, parent Ticket02/03 integration, or other worktrees were touched.
- H800 memory/topology/configuration, CPU payload validation and real GPU execution remain with the primary agent.
- Full input-side acceptance remains pending integration of another agent's `swe_inputs.py`/checker/audit changes. The old constructor on this branch still requires response >= context; the local dry-run only renders argv and does not prove generation with the new cap. Parent dry-run behavior could not be inspected at its named launcher path.
- Parent branch integration remains subject to the parent task's source-input, scientific, formal-run and merge gates. This scoped change grants no additional platform authorization.
- The initial preparation `requirements.md` and `plan.md` were excluded from the admission commit; this follow-up explicitly authorized their update and inclusion. Archived config JSON and historical Qwen35 preparation constants remain unchanged.
- Concurrent unowned multi-node edits to `run_qwen35_opd.py` and `qwen35_pair_worker.py` are preserved and excluded from the launcher length delivery commit; their correctness belongs to their owner.
