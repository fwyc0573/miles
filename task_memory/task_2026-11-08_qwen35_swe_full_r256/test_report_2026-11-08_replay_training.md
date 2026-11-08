## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Native configuration blocker: move two rollout-only declarations to shared owners; 16 actual typed-path checks, 52 SWE checks and the original 86 native regressions pass. |
| 2026-11-08 | T02-REMEDIATION: independently reproduce and fix all four review findings; 36 CPU/Gloo checks and 86 native regressions pass. |
| 2026-11-08 | Record T02-native CPU/Gloo verification, implementation interfaces and explicit runtime limits. |

# T02-native — replay/training verification

## Outcome and scope

The native full/r256 replay, exact binary two-level TIS, original-token primary KL and successful optimizer-result integration are implemented. Development/CPU verification, including the four T02-REMEDIATION fixes below, is PASS. T01 is accepted in `20d0b3f4`; actual GPU integration acceptance is still pending. No GPU/platform operation, cloud write, shared plan/progress/spec/ticket edit, commit or historical Qwen launcher edit was performed by this subtask.

The implementation uses the existing native rollout/data-source path and native policy loss; it adds no parallel training stack. The authoritative control signal is returned by the native optimizer callback in `TrainStepOutput.optimizer_step`, not read from evidence files. Detailed callable/launcher interfaces and remaining prerequisites are in [evidence/training-integration-api.md](evidence/training-integration-api.md); scientific scope remains owned by [spec.md](spec.md).

## Environment

- Working directory: `/data/ycfeng/sota-engine/miles`.
- Interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`.
- Python `3.12.13`; PyTorch `2.11.0+cu130`; `torch.cuda.is_available()` actually returned `False`.
- pytest `9.1.1`; real two-process Gloo/CPU DDP for distributed checks. No CUDA availability or CUDA model execution was faked. Gloo checks use native tensor functions eagerly; CUDA compiler/kernel qualification is deferred.
- Temporary pytest artifacts: `/data/ycfeng/tmp/pytest-of-brainpp/`. TIS file is explicitly registered in `stage-b-cpu` with a 50-second estimate because the measured full precision/distributed file exceeds the fast-suite 30-second budget.

## Commands and observed results

### New replay/TIS checks

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_replay.py tests/fast/test_swe_tis.py -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-fast-20261108.log 2>&1
```

Expected: independent math, immutable canonical payloads, full 200-success schedules, skips and transitions, finite hung/late/invalid acquisition, exact odd-bank UID preservation, native driver cadence, and actual distributed tensor/optimizer checks all pass. Final actual run: **20 passed in 37.69 seconds**, PASS. Raw evidence: [training-fast-20261108.log](evidence/training-fast-20261108.log).

| Check | Explicit expectation | Observed | Result |
| --- | --- | --- | --- |
| Full/r256 complete schedules | 200 successful updates; full 200 one-success banks; r256 four banks × 50 consecutive successful uses; skips do not move position | Exact enumerated reference matched | PASS |
| Native rollout plugin | Standard nested Sample source; four real bank acquisitions across 200 successes with skips; visit mutations do not alter frozen targets | Four source calls, fixed membership per bank | PASS |
| Canonical isolation | Prompt/response tokens, original masks, behavior and teacher targets survive private materialization; teacher identity cannot cross | Exact payload checks and rejection passed | PASS |
| Deadline and late isolation | Hung slot cannot hold collection past deadline; invalid/cancelled slot consumed; completed results persisted in completion order; late completion does not change sealed membership/records | Slots 2–5 sealed in source order; completion order 5,4,3,2; late suppressed-cancellation return isolated; ValueError and CancelledError variants passed | PASS |
| Partial native banks | 231, 255 and 256 unique UIDs reach native scheduled DP shards without dropping to a DP multiple | Counts/UID sets exactly matched for DP=4 | PASS |
| D4 threshold edges | Inclusive token/answer endpoints, uneven original masks, masked nonfinite scores, unit retained weights | Independent Python reference matched | PASS |
| Native S4 gradient | Detached q/s advantage; clipped ratios 0.8/1.28; eligible denominator 7 rather than survivor 3; no q/s gradient | Loss/logit gradient matched independent reference; pre-TIS numerator −2.1 and native separate post-TIS numerator −0.9 (unclipped case) | PASS |
| Real CPU/Gloo DP gradient | One rank has zero survivors but the global batch survives; original/survivor counts 6/4; primary numerator −1.8; whole-batch denominator 6 | Real DDP gradient matched reference; actual AdamW step counter became 1 | PASS |
| Global D7 stop | On next actual all-rejected batch, stop before optimizer.step, preserve true masks and leave parameters/counter unchanged | Both ranks raised ZeroTISSurvivors; counter remained 1; parameters exactly unchanged | PASS |
| CPU/Gloo CP | Geometric mean uses full original eligible response across CP; no duplicate counts | Original/survivor counts 7/5, numerator −2.1, exact sliced binary gradients | PASS |
| Native driver AST control test | With five injected skips, finish at success 200 after 205 attempts; save at success 100/200 and eval at 50/100/150/200; generic no-protocol loop remains 200 attempts | Actual loop AST passed both custom and generic cases | PASS |
| Custom schema transport | Shared SweReplayConfig registered once and carried through native custom-function JSON transport | All three hook configs equal; restored payload equal | PASS |
| Auxiliary observer failures | Evidence disk errors and bank-consumption observer mismatch cannot stop healthy training or become false D7 | Acquisition completed despite injected OSError; native skipped result returned despite update receipt OSError; mismatch marked unverified | PASS |

The driver control test fault-injects controller/Ray dependencies and executes the actual native loop AST. It verifies cadence/termination/control wiring only, not Ray/GPU initialization or evaluator/HF behavior. The Gloo test uses a real CPU model, native log-prob/advantage/policy-loss/TIS functions, real DDP reduction, and real torch AdamW; it does not claim to execute the CUDA Megatron optimizer.

### Existing native regression checks

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/backends/training_utils/loss/test_opd.py tests/fast/backends/training_utils/test_opd_cp_data.py tests/fast/utils/test_dp_schedule.py tests/fast/backends/training_utils/loss/hub/test_backend_loss_normalization.py tests/fast/rollout/test_opd_config_contract.py tests/fast/utils/args/test_custom_function.py tests/fast/utils/args/test_custom_function_construction.py tests/fast/ray/rollout/test_typed_conversion_hooks.py -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-native-regression-20261108.log 2>&1
```

Expected: native OPD detachment/scoring, CP payload precision/slicing, DP scheduling, token normalization, typed custom function config and native conversion remain correct. Actual: **86 passed in 14.82 seconds**, PASS. Raw evidence: [training-native-regression-20261108.log](evidence/training-native-regression-20261108.log).

### Syntax and whitespace

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m compileall -q tests/manual/agent_opd/swe_replay.py tests/manual/agent_opd/swe_tis.py tests/manual/agent_opd/swe_training.py tests/fast/test_swe_replay.py tests/fast/test_swe_tis.py miles/backends/megatron_utils/actor.py miles/backends/megatron_utils/model.py miles/backends/training_utils/loss/hub/losses.py miles/backends/training_utils/loss/objective.py miles/backends/training_utils/types.py miles/ray/rollout/rollout_data_conversion.py miles/ray/rollout/rollout_executor.py miles/ray/rollout/train_data_conversion.py miles/utils/args/configs/custom_megatron_plugins.py train.py
git diff --check
```

Both returned successfully with no output, PASS. `python -m ruff check ...` was attempted, but the CPU environment has no ruff package and the host has no ruff executable; lint is UNVERIFIED, not silently labeled PASS. No dependency installation was performed.

## Diagnosed issue and correction

The first CPU/Gloo gradient run failed with `AttributeError: 'NoneType' object has no attribute 'rank'` in native vocab-parallel cross entropy. The test had supplied a `None` TP process group under the distributed non-true-on-policy path. Matching the existing native CP test, it now creates a real singleton Gloo TP group per rank. The corrected distributed run and full reruns passed. No production behavior was changed to suppress this error.

## Remaining limits

1. T01 is accepted in `20d0b3f4`; preserve its raw input/source and teacher/student identity contract during native runtime integration.
2. Actual Qwen3.5 CUDA/Megatron recipe, AdamW-semantic native grouping, bf16 TP/CP/DP numerics, fresh repeated-visit actor scoring and 128K acquisition throughput remain unverified on GPU.
3. The actual capacity/topology must schedule all 231/255 sample UIDs; CPU checks settle the conversion logic, not 128K memory feasibility. Do not trim or pad fake samples if capacity fails.
4. Parent/T03 own HF-only save/evaluator/reader/deletion integration and formal launches. The driver now supplies successful labels and cadence, but these external lifecycles are not accepted by this report.
5. Shared historical Qwen launcher/future edits observed in git status belong to other tasks and were preserved.

## Final verification

The initial 20-case rerun, targeted compileall and `git diff --check` passed after the cancellation/soft-observer changes. This completed the initial T02-native development/CPU evidence, not GPU/HF/evaluation acceptance. The subsequent review and remediation are recorded below.

The final SSOT cleanup removed duplicate defaults from the pure `ReplaySchedule` constructor; production already passes `SweReplayConfig` values explicitly. The affected replay suite was rerun:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_replay.py -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-replay-final-20261108.log 2>&1
```

Actual: **14 passed in 0.46 seconds**, PASS; final `git diff --check` also passed. Raw evidence: [training-replay-final-20261108.log](evidence/training-replay-final-20261108.log).

## T02-REMEDIATION — four reviewed defects

The parent requested independent verification and minimal in-scope fixes, with no GPU/platform operations, commits or task-wide record edits. Scientific parameters, original-token objective, native failure behavior and formal/smoke distinction were preserved.

### Reproduction and disposition

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_tis.py tests/fast/test_swe_replay.py -k 'optional_diagnostic or stdout_failure or native_rollout_plugin or teacher_request' -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-remediation-red-20261108.log 2>&1
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_replay.py -k teacher_request -q >> task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-remediation-red-20261108.log 2>&1
```

First command: **11 failed, 19 deselected, 13.01 s** (expected RED). One teacher-success fixture initially omitted SGLang's required first-token placeholder, causing a different validation failure; the fixture was corrected without changing production parsing. The second RED command then reproduced missing stage files in all four teacher outcomes. The sink regression was subsequently renamed `test_diagnostic_sink_failure_after_real_update_still_returns_ack` and expanded to file/logger failures.

| Finding | Independently observed failure | Minimal correction | Affected verification |
| --- | --- | --- | --- |
| P1 optional diagnostics stop optimization | Missing KL/rejection raises RuntimeError; missing `mask_evidence` raises KeyError before peers' collective | Native detached int64 actual-mask signal is mandatory and independent; all ranks reduce it first. Optional incomplete sums are null/unverified; turns no longer index snapshots | Single-rank omissions; real two-rank Gloo omissions and consistent ACKs; unknown mandatory signal fails uniformly, not as D7; true global zero still stops before AdamW |
| P2 evidence sink loses success ACK | BrokenPipeError/OSError escapes stdout after a real successful AdamW update | Protect file/stdout/flush/warning sinks and clear pending state before evidence I/O | Four real-update file/stdout faults, including broken warning sink; real Gloo rank-0 stdout failure returns identical ACKs; AdamW counter is 1 and parameters changed |
| P2 canonical bank retained | Boundary/final ACK leaves payload, identity and token count live | Release all three fields in successful ACK at boundary/budget; keep them on skips; late tasks own only their candidate | Complete full/r256 200-success schedules with skips; source asserts empty bank before acquisition; weakref proves canonical object released immediately; final ACK leaves empty bank |
| P3 teacher failure stage absent | Request error, token-ID validation error and cancellation have no stage receipt | Isolated request/validation start/end context with deadline/status/error identity, preserving native outcome | Native teacher parser with success/error/cancellation and receipt-I/O faults; four correctly ordered success rows, two request-failure/cancellation rows; one request only, no extra forwards |

No temporary production debug instrumentation or replacement training stack was introduced.

### Final affected checks

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_tis.py tests/fast/test_swe_replay.py -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-remediation-full-20261108.log 2>&1
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/backends/training_utils/loss/test_opd.py tests/fast/backends/training_utils/test_opd_cp_data.py tests/fast/utils/test_dp_schedule.py tests/fast/backends/training_utils/loss/hub/test_backend_loss_normalization.py tests/fast/rollout/test_opd_config_contract.py tests/fast/utils/args/test_custom_function.py tests/fast/utils/args/test_custom_function_construction.py tests/fast/ray/rollout/test_typed_conversion_hooks.py -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-remediation-native-regression-20261108.log 2>&1
```

Expected: all four defect regressions pass with frozen S4 math; optional evidence cannot prevent real healthy optimization or create a false global-zero verdict. Actual: **36 passed in 40.86 s**, PASS. Native regressions: **86 passed in 15.36 s**, PASS. Exact original/survivor/turn counts were 6/4/4 in Gloo omission cases; missing KL stayed null. Both ranks completed the same collectives. The all-rejected case preserved parameters and actual optimizer step counter 1 despite omitted KL/snapshot diagnostics.

The real CPU/Gloo tests still do not qualify CUDA/Megatron optimizer kernels or the actual Qwen serving/128K configuration. T01's acceptance does not turn these checks into runtime acceptance. Parent/T03 own native integration, evaluation remediation, admission and task-wide status; no new launcher field or HF/eval hook is required for these fixes.

The final sink audit also protected acquisition's warning/error logger and extended its existing disk-failure regression to make the logger fail too. The affected replay suite was rerun after that last change:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_replay.py -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-remediation-replay-final-20261108.log 2>&1
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m compileall -q tests/manual/agent_opd/swe_replay.py tests/manual/agent_opd/swe_tis.py tests/manual/agent_opd/swe_training.py tests/fast/test_swe_replay.py tests/fast/test_swe_tis.py miles/backends/training_utils/loss/hub/losses.py miles/backends/training_utils/loss/objective.py
git diff --check
```

Actual: **23 passed in 0.75 s**, PASS; compilation and whitespace checks returned successfully with no output, PASS. Lint remains unverified because ruff is unavailable. The phase route check is updated in [evidence/training-checkpoint-20261108.md](evidence/training-checkpoint-20261108.md); it leaves ticket acceptance pending and flags stale Ticket02/03 T01-blocker text for the parent, without editing shared records.

## Native orchestrator configuration blocker

### Observed failure and cause

The parent supplied [native-launch-config-exp-1108-164121-488177.json](evidence/native-launch-config-exp-1108-164121-488177.json): all four cells completed real pinned-image Megatron parsing with `CUDA_DEVICE_MAX_CONNECTIONS=1`, then the driver factory raised `AttributeError: 'ImmutableNamespace' object has no attribute 'custom_reward_post_process_path'` at `swe_replay.py:436`. Inspection confirmed `check_swe_launch.py:59–63` and production `train.py:130–133` use the same typed orchestrator slice and custom-config merge. The checker was not at fault.

The CPU regression first reproduced that exact factory exception for full/r256 through validated `AllConfig → OrchestratorConfig.slice_from → JSON roundtrip → compute_custom_function_config → training_protocol`. The first fixture construction lacked nine fields resolved at the real parse boundary; those explicit input values/types were supplied to the fixture before the retained RED run, without changing production. A subsequent all-field audit exposed a second missing driver field, `opd_log_prob_top_k`, before any new GPU operation.

Both fields had rollout-only declaration owners despite being consumed by the driver. The fix moves their original declarations into `RewardModelConfig` and `OnPolicyDistillationConfig`, respectively. No declaration is duplicated, CLI/default/scientific value is changed, or fallback/alternate merge is introduced. The existing native component inheritance transports them. SWE's required rollout, teacher-score and canonical reward-postprocessor hooks are explicitly validated; missing/wrong hooks and implicit shortened formal runs fail.

### Actual typed-path checks

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_replay.py -k actual_typed_orchestrator -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-typed-view-red-20261108.log 2>&1
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_replay.py -k 'typed_orchestrator or lifecycle_configuration or typed_protocol' -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-typed-view-20261108.log 2>&1
```

Retained RED: **2 failed** at the exact factory missing attribute, as expected. Final actual typed-path run: **16 passed, 23 deselected in 0.80 s**, PASS. Eight valid factories cover A/B × full/r256 × formal/smoke. Formal budget is 200; the explicit smoke uses 3 successful updates, 8 slots and 2 bank uses. Six missing/wrong-hook cases reject invalid required paths; shortened formal budget is rejected. The lifecycle audit checks all native configuration reads, including dynamic S4 contract keys, across six actual component/custom-function views and typed JSON roundtrips; no remaining missing field was found.

The CPU fixture validates the real post-parse schemas and uses native `compute_trainer_config`, `_compute_rollout_function_config` and `compute_custom_function_config`. It does not pretend to run or mock the GPU-dependent Megatron parser; the local environment has no `megatron` package. Thus this settles the typed contract defect, not pinned-image runtime acceptance.

### Affected full and native reruns

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_replay.py tests/fast/test_swe_tis.py -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-typed-view-swe-suite-20261108.log 2>&1
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/backends/training_utils/loss/test_opd.py tests/fast/backends/training_utils/test_opd_cp_data.py tests/fast/utils/test_dp_schedule.py tests/fast/backends/training_utils/loss/hub/test_backend_loss_normalization.py tests/fast/rollout/test_opd_config_contract.py tests/fast/utils/args/test_custom_function.py tests/fast/utils/args/test_custom_function_construction.py tests/fast/ray/rollout/test_typed_conversion_hooks.py -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-typed-view-native-original-20261108.log 2>&1
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m compileall -q miles/utils/args/configs/reward_model.py miles/utils/args/configs/on_policy_distillation.py tests/manual/agent_opd/swe_replay.py tests/fast/test_swe_replay.py
git diff --check
```

Expected: the new native-view regressions and all previous math/schedule/D7/diagnostic fault-injection checks remain passing. Actual: **52 SWE checks passed in 39.69 s**; **the original 86 native checks passed in 12.22 s**. Compilation and whitespace checks passed. No loss equation, threshold, actual-mask reduction or optimizer behavior changed in this configuration fix.

A broader run added `tests/fast/utils/args/test_custom_view.py` to the original native command: **94 passed, 2 failed in 12.32 s**. Both failed tests call the real Megatron parser and raised `ModuleNotFoundError: No module named 'megatron'`; those checks are environment-unverified, not declared PASS. Raw output: [training-typed-view-native-regression-20261108.log](evidence/training-typed-view-native-regression-20261108.log). An earlier test-selection command named nonexistent `test_train_data_conversion_payloads.py`, exited 4 and collected no tests; its raw output is retained in [training-typed-view-native-suite-20261108.log](evidence/training-typed-view-native-suite-20261108.log). It was corrected to the existing canonical paths above, not by adding placeholders or skipping tests.

Parent must sync the two native declaration files plus `swe_replay.py` and rerun the unchanged pinned-image checker. No new launcher field is needed; `train.py`, the checker, actor/HF files, launchers, cloud/platform and shared task records were not edited. GPU/native Qwen acceptance remains pending. Prior 36/86/23 results remain historical evidence; the new observed configuration failure is covered by the 16 new typed-path checks, not retroactively by those earlier passes.
