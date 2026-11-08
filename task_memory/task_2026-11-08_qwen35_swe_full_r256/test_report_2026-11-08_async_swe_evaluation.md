## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | T03-REMEDIATION: correct native patch/infrastructure classification, recover scored outcomes and check-only trajectories, bind startup/resume to manifest pins, and join four-worker cancellation cleanup. |
| 2026-11-08 | T03 local delivery: persistent evaluator, pinned native adapter, 28 CPU regressions, and explicit runtime acceptance limits. |

# T03-eval — Async SWE evaluation

## Outcome and limits

**Local implementation and T03-REMEDIATION are delivered; Ticket03 live runtime acceptance remains incomplete.**

The owned implementation provides durable post-export enqueue, an existing Miles
`CheckpointEvalFn` seam, four independent native seed workers, immutable completed
slot results, original-deadline recovery, explicit reader leases, and owned-file
release. No training/launcher/platform/input/overlap files were edited. No commits,
GPU operations, cloud writes, or actual source/HF deletions were performed.

All reported scores and deleted bytes below are **CPU fault-injection fixtures**.
No live SWE model/ACS grading or HF inference reload was executed. The remediation
addendum records native serializers, autosubmit logic, and check-pipeline execution
with CPU fault injection; these checks do not establish live benchmark capability.

## Deliverables

| Code paths relative to Miles; evidence paths relative to this task | Purpose |
| --- | --- |
| `tests/manual/agent_opd/swe_evaluation.py` | Atomic persistent queue/state, reference FourAttempts ledger, independent async execution, bounded missing-slot recovery, reader-safe scoped release, CLI. |
| `tests/manual/agent_opd/swe_native_evaluation.py` | Pinned reference ACS config/pipeline/grader adapter, Qwen registry/template checks, actual HTTP request capture, remaining-deadline HTTP bound, native process-tree cleanup. |
| `tests/manual/agent_opd/swe_evaluation_fn.py` | Existing external checkpoint evaluator interface; enqueue only, return immediately, observable auxiliary failure without training exception. |
| `tests/fast/test_swe_evaluation.py` | 28 targeted CPU fault-injection cases; explicitly registered as stage-b-cpu, labels eval/ckpt, estimate 130s. |
| `evidence/evaluation-source-pins.json` | Exact native source SHA256/Git object equality, verified ordered100 tasks, four actual reference configuration payloads, request-limit evidence and limits. |
| `evidence/evaluation-verification.json` | Measured commands, test timing, retained fixture outcomes, release bytes, and native-capability blockers. |
| `evidence/evaluation-checkpoint.md` | T03 phase self-check; no scope/decision change. |

## Environment and tested commands

- Working directory: `/data/ycfeng/sota-engine/miles`.
- Python: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, **3.12.13**.
- pytest **9.1.1**; no conda environment was used.
- Raw fixture files/cache: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/`.
- Formatter/linter tools were isolated with `uv tool run`; no runtime dependency
  environment was changed. Initial PyPI access timed out; the known company mirror
  succeeded. The SWE runtime still needs its own dependencies and credentials.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_evaluation.py -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-eval-pytest-final
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m compileall -q tests/manual/agent_opd/swe_evaluation.py tests/manual/agent_opd/swe_native_evaluation.py tests/manual/agent_opd/swe_evaluation_fn.py tests/fast/test_swe_evaluation.py
git diff --check
```

Actual formatter/linter invocations used the following prefix:

```bash
/data/ycfeng/toolchain/bin/uv tool run --cache-dir /data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache --index-url http://mirrors.i.basemind.com/pypi/simple/ --allow-insecure-host mirrors.i.basemind.com
```

Append `--from black==24.3.0 black --line-length 120`,
`--from ruff==0.14.7 ruff check`, or
`--from isort==5.13.2 isort --profile=black --line-length=120 --check-only`,
then the same four Python paths in the compile command above. Final checks passed.

## Observed checks

| Check | Passing condition | Actual | Verdict |
| --- | --- | --- | --- |
| First lifecycle run | All then-existing 21 cases pass | 21 passed, 100.46s | PASS |
| Final targeted file | All 28 cases pass | 28 passed, 115.91s, two existing SWIG deprecation warnings | PASS |
| Real Miles class discovery | Existing registry recognizes SweEvaluationFn | `is_checkpoint_eval_fn(...) == True`; no native SWE dependencies loaded | PASS |
| Export gate | Missing `.complete`, unverified packaging, or missing shard does not enqueue | All three rejected; HF preserved | PASS |
| Native counter mapping | No update-minus-one assumption | Successful update 200 → observed rollout 213, version native-v214, 14 skipped fixture updates | PASS |
| Hung first request | Other seeds persist before the held request finishes | Three first-execution results saved; 397 missing logical slots recovered; final400 | PASS |
| Restart | Never overwrite completed rows or change task/seed/deadline | Original result bytes unchanged; only missing UIDs issued; original deadline unchanged | PASS |
| Absolute deadline | Cancel hung task, retain HF and null complete score | EXPIRED/INCOMPLETE, denominator400, avg_at_n=null | PASS |
| No queue skip / trainer wait | Every point durably queued before admission | 17 fixture points queued with no deadline before actual start; a running first point does not hide later queue entries | PASS |
| Model failure outcome | Completed False not rerolled | Slot removed from missing set; conflicting True rejected | PASS |
| Complete score / release | All 400 results archived, all readers exited | avg_at_n=1.0 for all-True fixture; 7 owned files, **258 bytes**, released including HF200 | PASS |
| Safety and interrupted release | Live reader, changed HF, unowned file, symlink, or corrupt native archive blocks release; interrupted own unlink is recoverable | Rejections/preservation pass; scoped interrupted release completes with correct inventory bytes | PASS |
| Native child cleanup | Local owned subprocess exits/reaps | Actual CPU sleep child terminated and reaped; no GPU | PASS |
| Resource admission | Eval GPUs included in personal nonterminal H200<=56 | 57 and less-than-eval total rejected | PASS |
| Baseline | Source model never owns deletion | PROTECTED_SOURCE, deleted_bytes0 | PASS |
| Producer-process exit | A fresh CLI can read durable queue/results after pytest exits | Original queued point recovered; incomplete summary 0/400/null | PASS |
| Syntax / lint / formatting | Targeted files compile/check | compileall, Ruff, isort check, diff whitespace pass | PASS |

The fresh independent CLI commands were:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.swe_evaluation --configuration /data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-eval-pytest-final/test_existing_checkpoint_evalu0/owned/configuration.json --action queue
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.swe_evaluation --configuration /data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-eval-pytest-final/test_existing_checkpoint_evalu0/owned/configuration.json --action summary --point A-full.attempt-1.HF200
```

The local tests used the **actual reference FourAttempts** implementation. A
test-only minimal scorer substitute exists solely for portable CI hosts lacking
the user's external Steptron checkout; neither path represents native grading.

## Source and benchmark evidence

- Original SWE commit: **`1af09e5f90f55f6fbce5f71efe7da0030a2e126e`**.
- Object repository: `/data/ycfeng/steptron/third_party/swe-agents`.
- New source snapshot:
  `/data/ycfeng/tmp/qwen35-swe-full-r256/swe-agents-1af09e5f-native/`.
- `git archive <commit>` was extracted into that new directory only. Unsafe
  absolute symlinks for unrelated Claude/Kilo/OpenClaw binaries were excluded;
  their exact names/count are retained in evaluation-source-pins.json. An initial
  extraction aborted on an absolute link and remains unused. Existing worktrees
  were not changed.
- The following six files were compared byte-for-byte against
  `git show <commit>:<relative_path>` and their Git blob IDs recorded:
  `src/swe_agents/models/step_align.py`, `src/swe_agents/cli/run.py`,
  `src/swe_agents/utils/agent_runtime.py`,
  `src/swe_agents/impl/sweagent/agents/default.py`,
  `src/swe_agents/swe_evaluation/evaluations.py`, and
  `src/swe_agents/swe_evaluation/harness/test_spec/test_spec.py`.
- Actual reference config, pipeline, scorer, FourAttempts, and StepAlign HTTP/retry
  source files have SHA256 records. These are observed file-content identities;
  a worktree HEAD alone is not used to describe locally modified source.
- T01 benchmark records were consumed, not rediscovered. Selected IDs exactly
  match `domain_manifest.benchmark.task_ids[:100]`, **not library[:100]**.
  Ordered-ID digest recomputed as compact JSON SHA256:
  `36394396b15746b75fbdfc1fbe8d74230161259a3dabf9d1ad824a1291140068`.
- Library:
  `/data/ycfeng/tmp/qwen35-swe-full-r256/swe_bench2512_all_sorted.json`, SHA256
  `f57b0957c562726bbc0a8f452d1b573d354d78fd0916459d249150fa257bf124`.
  The identity/personal-copy/source-overlap decision remains owned by T01.

The four real `SweAgentACSEvalConfig().to_dict()` payloads were constructed locally:
temperature 1.0, top_p 0.95, no top_k/max_tokens override, seeds 1729–1732,
context 131072 tokens, native agent 18000s/environment 1200s, concurrency 1 per seed.
Pinned DefaultAgent calls `model.query(dialog)` without a max_tokens override;
StepAlignModel omits None and Stepchat copies surviving kwargs without inserting
a max_tokens default. **No real HTTP body or resolved engine generation limit was
observed.** The executable native adapter captures actual HTTP JSON; the parent
must retain native engine request evidence for its resolved generation cap. max_tokens is
not replaced by a task-specific response cap. Native validation-only query retry 20
with 5s remains unchanged, and native in-flight HTTP 3000s is shortened only by the
remaining agent/evaluation deadline.

## Parent integration hooks

1. After the **existing** `qwen_export.post_save` packaging hook and its packaged
   report, call `EvaluationStore.enqueue_checkpoint(...)` immediately. Pass:
   `point_id`, actual `checkpoint_dir`, original `source`, the verified100 task IDs,
   frozen evaluation configuration, and `native_update` containing
   `successful_update`, observed `rollout_id`, actual `weight_version`, and native
   attempted/successful/skipped counter evidence. Trigger only 50/100/150/200 actual
   successful updates; never infer the native mapping from a directory label.
   Auxiliary enqueue failure must be logged/preserved and repaired without raising
   into healthy training. No new exporter or additional weight copy is supplied.
2. The existing external evaluator seam is
   `tests.manual.agent_opd.swe_evaluation_fn.SweEvaluationFn`; its parent-authored
   configuration path is `MILES_SWE_EVALUATION_CONFIGURATION`. The `publications`
   map is keyed by actual native rollout ID. This seam only calls the same durable
   enqueue API and reports enqueue metrics. **The post-packaging call is the
   authoritative immediate enqueue**; do not rely on old dispatcher wait/skip/GC
   to own this lifecycle. If using the seam, use existing save-HF directories, no
   separate `--eval-hf-dir` snapshot, and do not let snapshot GC delete them.
3. Parent/platform scheduler selects `store.queued()` and submits independently
   under the approved personal quota. `evaluate(..., runner=NativeSweRunner(...),
   allocation=...)` requires actual `job_id`, `eval_gpus`, and
   `personal_nonterminal_h200_gpus` including eval GPUs and all other nonterminal
   personal commitments. This module submits no jobs and manufactures no quota
   observations. The 72h timer starts at actual worker execution, not enqueue.
4. Parent starts/pins the Qwen server from the immutable HF **without copying it**,
   registers `reader_enter(point, server_reader_id, actual evidence)`, and supplies
   `server_identity` from real readback: model_path, weight_version, registered
   tool/reasoning parsers, context_length, preserve_thinking, enable_thinking, and
   fixed chat_template_sha256. The native runtime additionally needs `python`,
   `swe_source_root`, `swe_commit`, `source_sha256`, `input_sha256`, `dataset_path`,
   `manifest_path`, `python_paths`, model_name, URL, server_reader_id, `kill_grace_seconds`,
   and baseline_weight_version for the source baseline.
5. Independent CLI:
   `python -m tests.manual.agent_opd.swe_evaluation --configuration CONFIG --point POINT --action run`.
   Persisted output belongs under the approved task cloud namespace; worker-local
   caches remain outside that durable root. Parent keeps its platform launcher
   alive and owns all GPU lifecycle operations.
6. Incomplete evaluation preserves HF/results. Prove old readers exited, diagnose
   and repair the actual infrastructure cause, then call `resume(diagnosis=...,
   remedy=...)`; it never extends the deadline or rerolls completed False. On expiry,
   stop the affected server/worker via the approved platform lifecycle, retain HF,
   and continue healthy training.
7. After complete durable `evaluation.json`, stop/reap the parent server and record
   `reader_exit` using real process/platform evidence. Then `release(point)` or
   CLI `--action release` deletes only the original owned inventory and records
   its actual bytes, including HF200. It never uses shared free-space deltas.
   `enqueue_baseline` uses a registered protected original source and never deletes
   or copies its weights. Supply original/historical protected paths explicitly.

## Remaining acceptance work

1. Parent/T01: complete model, loader, and shared configuration acceptance.
2. Parent: prepare the native SWE dependency/auth environment and execute actual
   few-task ACS/tool/grader validation against the pinned source and Qwen server.
   Inspect request bodies, complete histories/tools/thinking, emitted max_tokens,
   native engine's effective generation cap, and grade artifacts. CPU mocks are
   not substitutes.
3. Parent/T02: perform real training successful update → HF packaging/reload →
   immediate enqueue → independent evaluation → reader exit → owned release, and
   demonstrate an evaluator failure does not stop healthy training.
4. Parent: verify atomic file publication, locking, restart recovery and deletion
   receipts on the actual mounted cloud filesystem, plus real allocation/server
   terminal receipts. Local POSIX fixture behavior is not cloud/RJob acceptance.

Requirements D10 and the execution authorization were re-read before handoff.

## T03-REMEDIATION — five phase-review findings

The scope was limited to the evaluator implementation, scoped regression tests,
and this evaluation report/evidence. Shared requirements/spec/plan/progress/review,
parent launch files, native snapshots, and the HF enqueue seam were not edited.
No dependency installation, source fallback, score-policy change, GPU/RJob action,
ACS/model HTTP request, cloud write, or commit was performed.

| Finding | Independently observed cause | Remediation and verification |
| --- | --- | --- |
| P1 native patch rejection | Pinned `evaluation_helpers.py:792–794` emits `apply_patch_fail` with a string traceback; the reference scorer requires a dict detail. | `swe_native_evaluation.py:40` accepts the native string rejection as False after checking infrastructure causes. A native serialized rejection is persisted through the actual store, removed from missing slots, and cannot be overwritten with True. |
| P1 environment autosubmit | Pinned `default.py:914–924,1338–1395,1934–1944` records `exit_env_error` / `autosubmit_reason=env_error` without requiring `meta.error_type`. | `swe_native_evaluation.py:55` inspects native exit/autosubmit fields before grading. The same native source maps API/runtime autosubmit to infrastructure causes. Bare/structured causes remain missing even with an unresolved or patch-failure grader; ordinary submitted/context outcomes retain the original scorer. |
| P2 interruption before ledger persistence | The old runner created a UUID before reading any existing slot artifacts. | `swe_native_evaluation.py:204,293,321` validates/reuses `outcome.json`, or reconstructs it from an already-scored native trajectory/grader. The regression forbids starting any child for both cases. If only grading is missing, the child copies completed trajectory/request bytes into a new grading evidence directory and calls only the original native check path. |
| P2 mutable self-supplied pins | Startup previously compared file bytes only with the runtime's own hashes. | `swe_native_evaluation.py:111,119` and constructor/child checks compare runtime pins and the complete inherited harness config with immutable manifest `configuration`. Updated self-supplied source/input hashes and a changed agent prompt are rejected; endpoint location replacement is accepted. |
| P2 cancellation interrupts cleanup | Cancelling gather propagated to workers; `finally` cancelled the remaining workers again after the fastest cleanup finished. | `swe_evaluation.py:473–489` shields the worker join, cancels unfinished workers once, then awaits cleanup. Four actual CPU children use TERM delays 0.05/0.25/0.45/0.65 s. Before the fix only one cleanup completed; after it all four returncode=0 children are reaped before evaluator exit. |

### Native artifacts and test oracle

`tests/fast/fixtures/swe_native/generate.py` ran in the existing native SWE
Python **3.10.20** environment. It used the real pinned `TaskTrajectory` serializer,
`DefaultAgent.attempt_autosubmission_after_error`, native exception handler, and
`get_eval_report` with a synthetic local test log. Environment methods were local
fault injections, not ACS clients. Printed native shell commands were **not executed**.

Raw native-format artifacts are retained under `tests/fast/fixtures/swe_native/`:
`submitted.json`, `exit_env_error.json`, `exit_api.json`, `exit_error.json`,
`exit_context.json`, `apply_patch_fail.json`, `unresolved.json`, `test_output.txt`,
and real `native_config.json` / `native_config.toml`. The portable test oracle
contains the exact original reference `read`/`outcome` function source segments;
production still loads only its configured pinned reference source. It is not a
production fallback or a mock of the new classification branches.

`evidence/evaluation-remediation-source-verification.json` records byte-for-byte
Git-object equality at commit `1af09e5f90f55f6fbce5f71efe7da0030a2e126e` for the native
serializer, DefaultAgent, exception handler, and grader. Both oracle function
segments match the source whose SHA256 remains
`2ea3fc4fc891fe048bc066d43f52cf4f702c5a35ea33425bbaf80d48e59eea5b`.

`tests/fast/fixtures/swe_native/check_only.py` executed the real pinned
`RunCheckPipeline` constructor, trajectory parsing, check-request construction,
check-task path, and result writer through the actual Miles `native_child` adapter.
Only `_run_check_subprocess` was injected with an existing native-format patch
rejection. Agent generation and **all** `requests.post` calls raised on use.
Observed PASS: one native check request, False, schema_version=1, and unchanged
trajectory/request hashes. The retained archive is
`evidence/evaluation-remediation-native-check-only/`, including original and
recovery trajectory/config/request files, invocation, grader, and `outcome.json`.
These are CPU fault-injection outputs, not a live model score or an observed live
HTTP generation cap.

### Exact remediation commands and observed iterations

All commands ran from `/data/ycfeng/sota-engine/miles`; no conda environment was
used. Outer tests used Python **3.12.13**, pytest **9.1.1**. Native scripts used
Python **3.10.20**, toml **0.10.2**, and the existing native source PYTHONPATH.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_native_evaluation.py tests/fast/test_swe_evaluation.py::test_four_seed_cancellation_joins_slow_native_cleanup -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-remediation-red --junitxml=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-remediation-red.xml
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_evaluation.py::test_four_seed_cancellation_joins_slow_native_cleanup -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-cleanup-red --junitxml=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-cleanup-red.xml
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_native_evaluation.py tests/fast/test_swe_evaluation.py::test_four_seed_cancellation_joins_slow_native_cleanup -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-remediation-targeted2 --junitxml=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-remediation-targeted2.xml
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_evaluation.py tests/fast/test_swe_native_evaluation.py -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-remediation-full --junitxml=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-remediation-full.xml > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-remediation-full.log 2>&1
```

| Iteration | Expected signal | Actual | Verdict |
| --- | --- | --- | --- |
| Native classification before correction | Reject the wrong score/missing behavior | Four failures: patch rejection unverified; three infrastructure autosubmits incorrectly accepted. Three other cases passed, 1.41 s. | Correct red reproduction |
| Unequal four-child TERM delays before correction | Four native child cleanups finish before evaluator raises | Only 1/4 cleanups finished; 1 failed, 1.57 s. The regression finally reaped the remaining local children. | Correct red reproduction |
| First corrected targeted run | Classification/config/cleanup pass; resume needs native TOML evidence | 11 passed, 3 failed because the outer CPU environment has no `toml`, 4.14 s. No installation followed. | FAIL, corrected |
| Corrected parser and native TOML fixture | Existing Python3.12 stdlib TOML and native Python3.10 toml both work | 14 passed, 5.00 s, two existing SWIG deprecation warnings. | PASS |
| Final affected suite | All existing lifecycle and new native-format cases pass | **51 passed**, 0 failed/skipped, **134.21 s**, two existing SWIG deprecation warnings. 29 lifecycle cases / 22 native-format cases. | PASS |

The TOML correction supports the two already-selected interpreters rather than
adding a dependency or a source fallback. Contract comparison accounts for the
native serializer omitting None-valued config fields; no sampling setting changed.

The two native script invocations used this exact prefix:

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/tmp/qwen35-swe-full-r256/swe-agents-1af09e5f-native/src:/data/ycfeng/steptron/.worktrees/step3p6-replay-v1:/data/ycfeng/steptron/third_party/step_align:/data/ycfeng/steptron/third_party/harbor/src HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CUDA_VISIBLE_DEVICES= WORLD_SIZE=1 /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/.venv/br-native-swe-py310-1008am/environment/bin/python -B
```

Append respectively:

```text
tests/fast/fixtures/swe_native/generate.py --dataset /data/ycfeng/tmp/qwen35-swe-full-r256/swe_bench2512_all_sorted.json --reference /data/ycfeng/steptron/.worktrees/step3p6-replay-v1
tests/fast/fixtures/swe_native/check_only.py --output /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/evaluation-remediation-native-check-only --dataset /data/ycfeng/tmp/qwen35-swe-full-r256/swe_bench2512_all_sorted.json --reference /data/ycfeng/steptron/.worktrees/step3p6-replay-v1 --swe-source /data/ycfeng/tmp/qwen35-swe-full-r256/swe-agents-1af09e5f-native
```

The check-only invocation additionally set `LOGURU_DIAGNOSE=NO` and redirected
stdout/stderr to `/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-native-check-only-final.log`.
Both commands exited 0. Native auth variable names were temporarily set to explicit
CPU-only placeholders inside the check-only fixture; no real credential was read
or used.

Existing cached binaries were used directly; no tool/runtime installation occurred:

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/-kQQ6CPyKAABpsmE/bin/black --line-length 120 --check tests/manual/agent_opd/swe_native_evaluation.py tests/manual/agent_opd/swe_evaluation.py tests/manual/agent_opd/swe_evaluation_fn.py tests/fast/test_swe_evaluation.py tests/fast/test_swe_native_evaluation.py tests/fast/fixtures/swe_native/generate.py tests/fast/fixtures/swe_native/check_only.py
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/8QpD66osZqn5M69v/ruff-0.14.7.data/scripts/ruff check tests/manual/agent_opd/swe_native_evaluation.py tests/manual/agent_opd/swe_evaluation.py tests/manual/agent_opd/swe_evaluation_fn.py tests/fast/test_swe_evaluation.py tests/fast/test_swe_native_evaluation.py tests/fast/fixtures/swe_native/generate.py tests/fast/fixtures/swe_native/check_only.py
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/YeSQ9F0UbXV9REOw/bin/isort --profile=black --line-length=120 --check-only tests/manual/agent_opd/swe_native_evaluation.py tests/manual/agent_opd/swe_evaluation.py tests/manual/agent_opd/swe_evaluation_fn.py tests/fast/test_swe_evaluation.py tests/fast/test_swe_native_evaluation.py tests/fast/fixtures/swe_native/generate.py tests/fast/fixtures/swe_native/check_only.py
git diff --check
```

Black **24.3.0**, Ruff **0.14.7**, isort **5.13.2**, AST parsing of all seven owned
Python files, and diff whitespace checks passed. Ruff emitted only the existing
top-level pyproject lint-settings deprecation warning. Generated raw reference
function source is intentionally not reformatted.

### Native integration API handoff

The signatures of `enqueue_checkpoint`, `enqueue_baseline`, `evaluate`, and
`SweEvaluationFn.evaluate_checkpoint` are unchanged. The existing `configuration`
argument must now contain the output of
`tests.manual.agent_opd.swe_native_evaluation.evaluation_contract(runtime)`, built
once with the accepted native configuration environment **before enqueue**. It
contains the scientific runtime/source/input pins plus the complete normalized
native harness config. Freeze it for each baseline/owned-HF point using that
point's accepted runtime; preserve identical shared benchmark/harness settings.
Checkpoint model path/version remain point-owned. Do not rebuild or replace an
already-enqueued point's configuration.

Only model endpoint URL and server reader allocation identity may vary between
native starts. Quota/allocation is still admitted independently by the existing
store API; source/input paths, hashes, interpreter/search paths, model label,
template/parser/context settings, and native harness settings stay pinned.
The existing scope-only configuration is insufficient and is rejected; there is
no silent compatibility fallback. No existing immutable manifest was migrated.

Internal native invocations now carry `point_manifest` and `trajectory_source`
(null for new model generation); `NativeSweRunner` constructs them. Outcome raw
evidence adds `request_sha256`. The parent need not manufacture either field.
Missing grading is recovered with a new grading evidence directory while original
model artifacts remain unchanged. Parent interruption after outcome publication
recovers the validated original row without creating any UUID/child.

Live ACS/model grading, effective engine generation cap, HF inference/export
integration, and mounted cloud/RJob lifecycle remain parent-owned acceptance work.

Final machine-readable evidence is `evidence/evaluation-remediation-verification.json`.
Selected red/final JUnit XMLs and the full test/native-check-only logs are retained
beside it with the `evaluation-remediation-` prefix. Per-file accumulated JUnit
test-case times, including setup/teardown, were 127.109 s for the 29 lifecycle tests
and 6.810 s for the 22 new native-format tests; the latter stays within the existing
implicit fast CPU budget. The main file's stage-b-cpu registration is unchanged.
The phase self-check is `evidence/evaluation-remediation-checkpoint.md`.
