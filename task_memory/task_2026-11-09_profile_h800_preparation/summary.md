## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record parent-only D35 approval, terminal review remediation and selected offline archive delivery; parent merge remains primary-owned and pending. |
| 2026-11-09 | Archive successful two-update H800 D34 verification and 2.15 GB cumulative logical smoke cleanup; parent integration remains gated. |
| 2026-11-09 | Accept 256 D34 bank slots in 1633.3 seconds and record first backward entry without an optimizer verdict. |
| 2026-11-09 | Record eight ready engines and successful native initial weight synchronization in 3.8 seconds. |
| 2026-11-09 | Record network-fixed H800 job exp-1109-192340-580111 and initial Starting platform readback without claiming native acceptance. |
| 2026-11-09 | Accept cf98293a CPU/static node-network repair, prepare a fresh-output H800 retry and preserve the distinct upstream D11 gate. |
| 2026-11-09 | Record terminal native startup failure and verified session-owned cloud cleanup; keep capacity open. |
| 2026-11-09 | Record the frozen preflight delivery and active36-H800 capacity prerequisite; acceptance remains pending. |
| 2026-11-09 | Archive the verified, scoped nullable GPU admission implementation. |
| 2026-11-09 | Add the verified explicit native launcher length contract and integration limits. |
| 2026-11-09 | Record completed mixed-session/source repairs, candidate H800 topology and genuine in-place native receipts; keep real input/GPU acceptance open. |

# Scoped H800 Preparation Summary

Task IDs: `profile-h800-admission-20261109`, `profile-length-launcher-20261109`, `profile-initial-weight-sync-20261109`, `profile-capacity-input-lengths-20261109`, and `profile-h800-archive-close-20261110`.

## Outcome

H800 D34 native capacity and both terminal-smoke cleanups are complete. On Nov10 the user explicitly selected the H800 result under parent D35 for the parent full_kl_nll D1/D22 prerequisite and approved primary-owned merge/T02/T03. Parent integration is approved but still pending; this archive task does not perform it. The upstream owner's unchanged old-D11 contract and original Nov9 receipts are preserved.

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
- `tests/manual/agent_opd/check_h800_capacity_evidence.py`: existing fixed-run offline receipt checker, not a live training gate.
- `task_memory/task_2026-11-09_profile_h800_preparation/test_report_2026-11-10_h800_archive_close.md`: terminal review P3 remediation, exact scoped commands, selected committed receipts and retained local-only evidence.

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

- The first 36-H800 attempt `exp-1109-181120-274261` failed before weights or acquisition because two TP4 engines received the head's network environment. Commit `cf98293a` removes that broadcast; 529 affected CPU tests passed, 12 skipped and one baseline parser case was deselected. Complete fixed-diff review returned No Findings. That failed attempt never established capacity; the corrected terminal result is recorded below.
- The old source constructor restriction is removed in`82915613`; the existing real-factory parity tool accepts D34 budgets in`8d517b48`. Original-source pinned-image parity passed in`exp-1109-172310-849823` (Succeeded09:28:42Z), including the normal native factory and actual16K request budget. Earlier worker PYTHONPATH and local quoting failures are retained in`test_report_2026-11-09_native_preflight.md`; neither reached training.
- Native baseline/visual/filter receipts for original posttrain paths completed in CPU job`exp-1109-164358-350923`:9254 conversations,102 excluded visual conversations,10008 excluded targets. Retained files are`evidence/native-visual-in-place/{baseline,visual,filter,runtime}.json`; these are native exclusion evidence, not full112K Qwen length statistics.
- The session correction `422a613d` matches upstream `864cac87` byte-for-byte and passes 37 directly affected checks. Pinned-image source inspection confirms the absent-session HTTP400 guard. The corrected native run now verifies both initial and updated-weight text synchronization, two optimizer ACKs and second scoring.
- The replay-budget override is closed by `0e7e0df3`: 62 affected checks pass, including replay-to-request verification. All 256 native bank samples preserve the 16384 completion cap.
- Parent branch integration and Ticket02/03 are now approved under parent D35 and primary-owned, but not done here. Remaining scientific and formal-run requirements are unchanged. This archive change grants no additional platform authorization.

The historical launcher`sh_1bfca68aa001JWOGKI0d7wkd99` exited1 after native failure. Its exact submission and terminal evidence remain in`test_report_2026-11-09_native_preflight.md`, `evidence/admission-h800-capacity-20261109.json` and`evidence/h800-native-terminal-20261109.json`.

The network-fixed retry froze at `ebc0e6a0` and submitted from the current host at 11:23:40Z as `exp-1109-192340-580111`, with fresh personal admission, 36 H800/codesign GPUs and no preemption. All five worker receipts confirm actual devices and matching images/models. The job and all replicas are now **Succeeded**, and the ordinary launcher exited successfully. Exact commands and evidence are in `test_report_2026-11-09_network_fixed_prelaunch.md`.

All eight engines initialize; first weight synchronization completes in 3.8 seconds. Mixed transfers and begin/end sessions return HTTP200. Native checksums verify 1644 text hashes equal across eight engines at versions 0/1 and the same 972 changed hashes after the first update. Untrained `visual.*` hashes are excluded by the existing text-only recipe; their constant-fill cause remains inferred. Final process NIC/HCA values are not exposed by server-info and remain unverified. Native warnings did not trigger a patch, retry or stop.

**H800 D34 native capacity PASS:** 256/256 valid samples in 1633.2862 seconds; two successful, unskipped optimizer ACKs and bank visits; every rank completes two 88-microbatch student scoring passes, including updated weights after ACK1. The real 128K logits storage is 15.15625 GiB/rank, with verified source and previous-output lifetime. Scoring PyTorch allocation peaks at 28.89246 GiB; this is not a whole-device or backward peak. `evidence/h800-network-fixed-capacity-acceptance-20261109.json` binds the native checks. The original receipt records the Nov9 separation from parent D1/D22; parent-only D35 now adopts this H800 evidence without rewriting the receipt or accepting upstream old-D11. Parent merge/T02/T03 remain pending with the primary; this two-update result does not certify a 200-update formal A/B run.

Both terminal smoke roots were removed after complete local retention and per-file size/hash checks: 167 files/15325989 bytes from the failed startup and 412 files/2136889910 bytes from the successful run, totaling **579 files/2152215899 logical bytes**. Independent readback finds the task cloud parent empty. Raw archives remain under `/data/ycfeng/tmp/agent-opd-image/h800-exp-<job>-cloud-raw.tar.gz`; selected evidence is retained in this task. Root-owned successful-run output required exact-path `sudo -n` unlink, not permission changes. Source assets, other tasks and shared trash were untouched. Physical OSS reclamation remains unmeasured.
- The initial preparation `requirements.md` and `plan.md` were excluded from the admission commit; this follow-up explicitly authorized their update and inclusion. Archived config JSON and historical Qwen35 preparation constants remain unchanged.
- Concurrent unowned multi-node edits to `run_qwen35_opd.py` and `qwen35_pair_worker.py` are preserved and excluded from the launcher length delivery commit; their correctness belongs to their owner.

Terminal reviewer `profile-h800-terminal-acceptance-review-20261109` reported stale-frontier P3 and No other findings, as supplied by the primary. The current frontier, plan and checkpoint now reflect completed native capacity/cleanup and approved, pending parent integration. Archive closure is complete with 21 explicitly selected owned files, including 12 JSON receipts; the fixed-run offline checker, diff and scoped lint checks pass. Credential scanning found no literal local personal credentials or private keys. The 73 remaining untracked evidence files/3832196 bytes, complete raw archives and logs are intentionally retained locally; see the Nov10 test report for exact paths and verification limits.
