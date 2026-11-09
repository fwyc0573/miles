## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Accept cf98293a CPU/static node-network repair, prepare a fresh-output H800 retry and preserve the distinct upstream D11 gate. |
| 2026-11-09 | Record terminal native startup failure and verified session-owned cloud cleanup; keep capacity open. |
| 2026-11-09 | Record the frozen preflight delivery and active36-H800 capacity prerequisite; acceptance remains pending. |
| 2026-11-09 | Archive the verified, scoped nullable GPU admission implementation. |
| 2026-11-09 | Add the verified explicit native launcher length contract and integration limits. |
| 2026-11-09 | Record completed mixed-session/source repairs, candidate H800 topology and genuine in-place native receipts; keep real input/GPU acceptance open. |

# Scoped H800 Preparation Summary

Task IDs: `profile-h800-admission-20261109`, `profile-length-launcher-20261109`, `profile-initial-weight-sync-20261109`, and `profile-capacity-input-lengths-20261109`.

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

- The primary froze the36-H800/codesign configuration and accepted CPU preflight at`a470c841`, then submitted`exp-1109-181120-274261` at10:11:20Z. Actual platform resources, non-preemption, codesign, H800 tags, personal creator and current-host source are verified. The job subsequently Failed10:29:35Z before weight publication or bank acquisition. Ray registered four nodes/32 student GPUs, but two TP4 engines on student rank2 first failed in`ncclGetUniqueId()` at10:28:57Z; the later`matches=[]` and supervision errors followed engine loss. Commit`cf98293a` corrects confirmed head-to-node NCCL environment overwrite;529 affectedCPU tests passed,12 skipped and1known-baseline parser case was deselected. Complete fixed-diff review returned No Findings. Native capacity remains unaccepted.
- The old source constructor restriction is removed in`82915613`; the existing real-factory parity tool accepts D34 budgets in`8d517b48`. Original-source pinned-image parity passed in`exp-1109-172310-849823` (Succeeded09:28:42Z), including the normal native factory and actual16K request budget. Earlier worker PYTHONPATH and local quoting failures are retained in`test_report_2026-11-09_native_preflight.md`; neither reached training.
- Native baseline/visual/filter receipts for original posttrain paths completed in CPU job`exp-1109-164358-350923`:9254 conversations,102 excluded visual conversations,10008 excluded targets. Retained files are`evidence/native-visual-in-place/{baseline,visual,filter,runtime}.json`; these are native exclusion evidence, not full112K Qwen length statistics.
- The session correction is reviewed and CPU-verified; subsequent`422a613d` matches upstream`864cac87` byte-for-byte and passes37 directly affected checks. Pinned-image source inspection confirms the absent-session400 guard, but native CUDA/NCCL synchronization and capacity acceptance remain open.
- Prelaunch review's P1 replay-budget override is closed by`0e7e0df3`:62 affected checks pass, including the actual replay-to-request budget regression. The actual submitting Python3.10 environment's36-GPU dry-run passes. Native GPU execution is the remaining prerequisite step.
- Parent branch integration remains subject to the parent task's source-input, scientific, formal-run and merge gates. This scoped change grants no additional platform authorization.

The historical launcher`sh_1bfca68aa001JWOGKI0d7wkd99` exited1 after native failure. No replacement GPU attempt has been submitted. Exact submission and terminal evidence remain in`test_report_2026-11-09_native_preflight.md`, `evidence/admission-h800-capacity-20261109.json` and`evidence/h800-native-terminal-20261109.json`.

The current retry candidate changes only output identity/path fields and passes both real36-GPU submission dry-run and native argv inspection; head NIC/HCA values are no longer serialized. See`test_report_2026-11-09_network_fixed_prelaunch.md` and`evidence/h800-network-fixed-{submission,native-argv}-dry-run-20261109.json`. Its H800 D34 contract is distinct from the upstream owner's approved original18-H200 D11 retry; neither result may be relabeled as acceptance of the other's input budgets. Fresh submission, native NCCL2.30.7 and all runtime/capacity outcomes remain pending.

At the user's request, obsolete cloud duplicates from this terminal smoke were removed after a byte/hash-verified local backup:167 files /15,325,989 logical bytes, with no generated weights or checkpoints. The task cloud root is now empty. Raw evidence remains in the restricted local archive`/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-181120-274261-cloud-raw.tar.gz`; selected failure lines and structured receipts remain in the task directory. See`test_report_2026-11-09_cloud_cleanup.md` and`evidence/cloud-cleanup-{inventory,backup,result}-20261109.json`. Source assets, other tasks and shared trash were untouched; physical OSS reclamation was not measured.
- The initial preparation `requirements.md` and `plan.md` were excluded from the admission commit; this follow-up explicitly authorized their update and inclusion. Archived config JSON and historical Qwen35 preparation constants remain unchanged.
- Concurrent unowned multi-node edits to `run_qwen35_opd.py` and `qwen35_pair_worker.py` are preserved and excluded from the launcher length delivery commit; their correctness belongs to their owner.
