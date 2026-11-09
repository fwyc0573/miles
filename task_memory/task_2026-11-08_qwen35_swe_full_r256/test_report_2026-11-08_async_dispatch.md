## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Follow-up: preserve builder dispatch through its validation owner and drain on native wait failure; affected CPU checks PASS. |
| 2026-11-08 | T03-ASYNC-DISPATCH local ready notification, observer/submitter handoff and CPU verification. |

# T03-ASYNC-DISPATCH — local asynchronous evaluation dispatch

## Outcome / 结果

**Implementation and CPU verification PASS; native end-to-end acceptance remains pending.**
训练 HF 持久入队后写本地挂载通知；实际训练 job 创建后自动开始本地观察，调用现有单点评测 submitter。
健康训练不等待 benchmark；实际 `workers.wait()` 返回或抛错后 drain 已启动的 evaluator launcher。
This agent performed no GPU/platform/cloud/auth operations, SSH, cloud mount, commits,
or edits to shared task requirements/spec/plan/progress or another agent's native files.

## Deliverables and ownership

| File / entrypoint | Scope |
| --- | --- |
| `tests/manual/agent_opd/swe_hf_export.py:142` | After durable formal enqueue, publish minimal ready identity; notification errors leave HF and queue intact with durable publication diagnosis. Existing typed hook configuration is unchanged. |
| `tests/manual/agent_opd/watch_swe_evaluations.py:47,90,127` | One dispatch validation owner; own-job notifications, frozen JSON, conservative admission journals and actual subprocess handles. One dispatcher serves automatic observer and standalone CLI. |
| `tests/manual/agent_opd/watch_swe_evaluations.py:326,352` | Start after actual job creation; native wait return or failure signals drain without stopping healthy training. |
| `tests/manual/agent_opd/submit_swe_opd.py:120–153` | Native wait is inside try/finally. Capture available terminal evidence on failure, preserve the original exception, and drain the observer. No resource policy change. |
| `tests/manual/agent_opd/swe_evaluation_config.py:108,137` | Preserve explicit dispatch through the existing owner; validate the CLI output mount. Absent dispatch remains valid for qualification. |
| `tests/fast/test_swe_evaluation_dispatch.py` | 20 CPU process-handoff cases, including native wait failure and evaluator-failure isolation. Existing submitter argv is redirected only in tests to a real CPU receipt-stub subprocess. No real GPU, ACS or grading occurs. |
| `tests/fast/test_swe_evaluation_worker.py:139–206` | Builder CLI output consumed by actual watcher/notification code; no-dispatch compatibility, invalid scope/cadence rejection and unchanged scientific contract. |
| `tests/fast/test_swe_hf_export.py:40,157,390,402` | Existing tiny Qwen/native-callback fixtures plus ready notification, soft notification failure, and frozen-configuration rejection. |

`run_swe_opd.py`, `submit_swe_evaluation.py`, `swe_evaluation.py`, native runners,
integration_config and GPU policy were not edited. Unrelated changes remain intact.

## Exact configuration additions

Add this operational stanza to the evaluation JSON **before the training run**:

```json
"dispatch": {
  "local_mount": "/data/ycfeng",
  "directory": "/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/evaluation-dispatch",
  "poll_seconds": 30
}
```

The mount must equal the integration configuration's actual local_mount. The
directory must resolve under it; each actual job gets a separate directory.
poll_seconds is an explicit positive operational cadence, not a science parameter
or hardcoded default. No resource ceiling is duplicated here.

The existing integration checkpoint block must identify the same evaluation file:

```json
"checkpoint": {
  "post_save_hook": "tests.manual.agent_opd.swe_hf_export.post_save",
  "hook_args": {
    "swe_evaluation_configuration": "/absolute/local/mounted/evaluation.json"
  }
}
```

The existing run_swe_opd recipe already forwards hook_args; no new worker launcher
path was added. Supply the same explicit `dispatch` stanza in the builder inputs;
`swe_evaluation_config.build_configuration()` now preserves it, with no defaults.
The builder and its CLI reuse `watch_swe_evaluations.validate_dispatch()`; the CLI
output must remain under that local mount. Qualification inputs without dispatch
remain valid. Do not mutate a configuration after its job-local frozen copy exists.

Ready notifications contain exactly point_id, job_id, checkpoint_dir and the frozen
configuration path. Local layout under `<dispatch.directory>/<actual training job>/`:

- `evaluation.json`, `integration.json`: immutable consumed configurations; GPU policy remains an existing live file reference for fresh admission, including expiry.
- `ready/<point>.json`: immutable notification only; no weights, trajectories or credentials.
- `dispatch/<point>.json`: process/admission outcome journal.
- `receipts/<point>.admission-N.json[.pending]`, `logs/<point>.admission-N.log`: existing submitter receipts and local launcher logs.
- `observer.json`: final local outcomes and unverified paths; not benchmark scores.

## Local entrypoint and lifecycle

Automatic dispatch needs no extra local CLI: start the existing `submit_swe_opd`
with the configured hook_args. It starts the observer only after obtaining the
actual job name. The observer launches this existing single-point command using
the **same local Python environment** as the training submitter:

```bash
python -u -B -m tests.manual.agent_opd.submit_swe_evaluation --config "$FROZEN_INTEGRATION" --configuration "$FROZEN_EVALUATION" --point "$POINT" --receipt "$NEW_LOCAL_RECEIPT"
```

For explicit local observation/reopening after inspecting recorded state:

```bash
python -B -m tests.manual.agent_opd.watch_swe_evaluations --config "$INTEGRATION" --configuration "$EVALUATION" --job "$ACTUAL_TRAINING_JOB" --trainer-receipt "$TRAINING_RECEIPT"
```

Run from integration.local_mount. Standalone completion requires the matching
actual `<TRAINING_RECEIPT with .terminal.json suffix>`; missing files do not imply
completion. Automatic drain comes directly from native workers.wait return or failure.
On a native wait failure the launcher attempts the existing terminal read/write
once, then re-raises the original exception after drain. An unavailable terminal
query is logged as unverified and cannot replace the original native error.

Only exit2 plus a matching receipt with job_id=null, submitted=false,
admitted=false and no pending file permits another fresh admission check. While
training is alive, check at poll_seconds. After training terminal, perform at most
one check per point per observer instance, drain admitted children, then report
denied points as queued. Explicitly reopening the observer can recheck proven
denials, not failed/incomplete/unknown evaluator runs. STARTING/ADMITTED journals
without a currently owned process handle are UNVERIFIED and never safe retries.
CLI exit2 means points remain admission-denied; exit1 means observer/evaluator
failure; neither changes the training submitter's native success result.

The existing submitter still owns exact2 GPUs, fresh locked policy/quota admission,
preemption, `.pending` publication and native launcher lifetime. The existing worker
and EvaluationStore still own the original deadline/ledger, grading, reader cleanup
and HF release. This observer does not query or mount cloud files locally.

## Verification evidence

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13,
pytest9.1.1, torch2.11.0, Transformers5.19.0. No environment/dependencies changed.
Working directory: `/data/ycfeng/sota-engine/miles`.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_evaluation_dispatch.py tests/fast/test_swe_hf_export.py tests/fast/test_swe_evaluation_submission.py tests/fast/test_swe_launcher.py -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-dispatch-final --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t03-dispatch-final.xml
PYTHONPYCACHEPREFIX=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-dispatch-pycache /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m compileall -q tests/manual/agent_opd/watch_swe_evaluations.py tests/manual/agent_opd/swe_hf_export.py tests/manual/agent_opd/submit_swe_opd.py tests/fast/test_swe_evaluation_dispatch.py tests/fast/test_swe_hf_export.py
git diff --check
```

**106 PASS, 21.72s**: dispatch17, HF25, existing submission48, launcher16.
XML per-case setup/call/teardown totals: dispatch10.673s, HF7.390s; both new/affected
fast files fit the implicit stage-a-cpu budget. Static compile and whitespace PASS.

Formatter/linter prefix used:
`/data/ycfeng/toolchain/bin/uv tool run --cache-dir /data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache --index-url http://mirrors.i.basemind.com/pypi/simple/ --allow-insecure-host mirrors.i.basemind.com`

- `--from black==24.3.0 black --check --line-length 119 tests/manual/agent_opd/watch_swe_evaluations.py tests/manual/agent_opd/swe_hf_export.py tests/fast/test_swe_evaluation_dispatch.py tests/fast/test_swe_hf_export.py`: PASS.
- `--from isort==5.13.2 isort --profile black --line-length 119 --check-only` with those four files: PASS.
- `--from ruff==0.14.7 ruff check` with those four files plus `tests/manual/agent_opd/submit_swe_opd.py`: PASS.

The first run recorded99 PASS/3 fixture failures; missing local-submit fixture fields
and independent receipt sampling were corrected as hypothesized in
`evidence/t03_async_dispatch_plan.md`. The next isolated dispatch run passed13/5.49s;
the final suite adds CLI/scoping/denial reopening/journal failure cases. Raw XMLs:
`evidence/t03-dispatch-first.xml`, `evidence/t03-dispatch-second.xml`, `evidence/t03-dispatch-final.xml`.
Existing SWIG/torch.jit/datetime and Ruff-settings deprecation warnings remain.

Observed assertions include real local child creation/reaping; one child per point;
two independent points progressing despite a malformed receipt; no duplicate
launch under a second watcher; denial retention/recheck; no restart after pending,
missing, failed or uncertain handoff; actual training main order and post-terminal
drain; frozen config and cross-job/symlink rejection; observer I/O/start failure
isolation; notification failure leaves queued HF intact.

## Remaining runtime acceptance

Parent owns actual local auth/platform/GPU qualification. Verify actual mounted
ready notification→independent two-GPU evaluator admission→live local launcher,
training continuing through subsequent updates, final HF200 drain and native
ledger/deadline/release behavior. Also check a real denied-admission outcome under
the active/expired policy without treating it as launched.

This dispatcher intentionally accepts only formal50/100/150/200 trainer-enqueued
points. Smoke packaging still creates no formal400-attempt point; the existing
explicit owned-HF qualification workflow remains separate and unchanged. CPU
receipt stubs and watcher exit0 are not native SWE scores or formal task PASS.
Lost notifications and detached/unknown launchers require evidence-based repair,
not automatic cloud discovery or rescore. Check-progress record:
`evidence/checkpoint_t03_async_dispatch.md`.

## Integration follow-up / 本次追加验证

Request: preserve explicit builder dispatch; native capacity-failure wait must
execute the observer finally path. Scientific training configuration is unchanged,
including completion-only current-student rescoring and prompt exclusion.

Before edits, the focused reproduction produced **5 FAIL / 1 PASS, 3.16s**:
the builder discarded dispatch and accepted invalid dispatch inputs; both wait-error
cases exited without automatic drain. The evaluator-failure/healthy-native ACK
control already passed. Root causes are the reconstructed builder dictionary and
the wait call outside the finally region, not grader or admission behavior.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/fast/test_swe_evaluation_worker.py tests/fast/test_swe_evaluation_dispatch.py -k 'builder or native_wait_failure or failed_evaluator_does_not_change' --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-dispatch-followup-red --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t03-dispatch-followup-red.xml
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/fast/test_swe_evaluation_dispatch.py tests/fast/test_swe_evaluation_worker.py -k 'dispatch or configuration' --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-dispatch-followup-final --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t03-dispatch-followup-final.xml
```

Final affected checks: **30 PASS / 24 deselected, 16.42s** (dispatch20, configuration10).
Assertions use a real held CPU evaluator subprocess and the actual training main:
wait raises the same injected RuntimeError, terminal evidence is attempted, the
parent remains alive until that evaluator exits, and the identical original error
is re-raised. Missing terminal evidence does not replace it. A failed evaluator
leaves a Succeeded native receipt and main return0. No evaluator is resumed/retried.
The builder CLI's real output is frozen and consumed by the real watcher and ready
publisher; all scientific fields equal the no-dispatch output exactly.

Static commands additionally used the previously recorded uv prefix:
`--from black==24.3.0 black --check --line-length 119` and
`--from isort==5.13.2 isort --profile black --line-length 119 --check-only`
on watcher, builder and dispatch tests; isort also checks worker tests.
`--from ruff==0.14.7 ruff check` covers all five source/test files below.

```bash
PYTHONPYCACHEPREFIX=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-dispatch-followup-pycache /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m compileall -q tests/manual/agent_opd/watch_swe_evaluations.py tests/manual/agent_opd/swe_evaluation_config.py tests/manual/agent_opd/submit_swe_opd.py tests/fast/test_swe_evaluation_dispatch.py tests/fast/test_swe_evaluation_worker.py
git diff --check
```

CPU fixtures substitute the platform boundary and native constructor payload;
these results are not real StepMind wait, Python3.10-native grader or GPU PASS.
No unrelated worker execution/qualification/grading suites were run. Selected
checks fit the stage-a-cpu budget (the whole selected run is below30s).
Black/isort checks cover the new watcher, builder and dispatch tests; original
worker fixture layout and submitter formatting are preserved. Ruff, compileall
and diff-check cover all five follow-up source/test files. Native qualification
and current policy admission remain parent-owned and are not retried by this agent.
