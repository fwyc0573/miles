## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | T03-NATIVE-ASYNC qualification wiring, dedicated local fault check and final affected CPU evidence. |

# T03-NATIVE-ASYNC — qualification wiring

Outcome: local implementation ready for the parent-operated native run. No GPU,
platform, cloud, authentication operations or commits were performed by this agent.
本地实现完成；真实训练→两卡评测验收仍由父 session 执行。科学训练参数未变。

## Delivered paths

| Path | Change |
| --- | --- |
| `tests/manual/agent_opd/swe_hf_export.py:127–143` | Explicit smoke qualification first persists actual SMOKE_PACKAGED identity, then reuses enqueue_qualification_checkpoint. Status stays SMOKE_PACKAGED; evaluation_status tracks QUEUED. Same notify_ready afterwards. |
| `tests/manual/agent_opd/watch_swe_evaluations.py:73,124,212` | Optional explicit selected slots validated against configured task IDs/SEEDS, qualification namespace/prefix and actual native HF index; same Popen argv appends existing qualification-attempt options. |
| `tests/manual/agent_opd/check_swe_native_async.py:28,64,86` | Dedicated local smoke launcher wraps the same submit_swe_opd CLI. Only first HF2 child environment gets empty AK_BASEMIND; HF3/parent environment stay unchanged. The watcher module's subprocess alias alone is intercepted; unrelated SDK subprocesses are untouched. |
| `tests/fast/test_swe_hf_export.py:452` | Public native actor train/save callback methods, synthetic optimizer/export boundaries, actual Qwen packaging/store/notifications; real model companion version and separate successful-index/native-rollout identities. |
| `tests/fast/test_swe_evaluation_dispatch.py:663,755` | Real independent Python HF2 submitter rejects missing key before admission; HF3 CPU receipt child proves same main/observer drain and healthy ACK. Also fault-record I/O failure remains soft. |

No changes to swe_evaluation, swe_native_evaluation, run_swe_evaluation,
swe_evaluation_config, submit_swe_opd, submit_swe_evaluation or parent-owned worker CI
were made in this follow-up. Existing unrelated edits remain preserved.

## Configuration and parent command

Use the already qualified evaluation contract, original protected source, manifest,
server/template/version and existing local mount. Its root must end in
`qualification-evaluations`; its owned_root must cover the actual training HF saves.
Supply this stanza explicitly in builder inputs (the existing builder preserves it):

```json
{
  "dispatch": {
    "local_mount": "/data/ycfeng",
    "directory": "/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/native-async-dispatch",
    "poll_seconds": 1,
    "qualification_attempt_ids": ["<one existing evaluation.task_ids entry>#attempt-0"]
  }
}
```

Replace the placeholder with one actual frozen task ID, never a new task or all400
slots. There are no production defaults. Freeze the final evaluation JSON under
the same local mount before submission. The normal integration config retains:

```json
{
  "training": {
    "run_kind": "smoke",
    "successful_updates": 3,
    "bank_slots": 8,
    "bank_uses": 2,
    "save_interval": 2
  },
  "checkpoint": {
    "post_save_hook": "tests.manual.agent_opd.swe_hf_export.post_save",
    "hook_args": {"swe_evaluation_configuration": "<absolute final evaluation JSON under /data/ycfeng>"}
  }
}
```

These are fragments, not replacements for the existing full configuration.
Do not modify science, resources, policy expiry, source/teacher identities, timeouts
or private environment. Use the parent's existing authenticated local StepMind
Python environment from `/data/ycfeng` (the configured local_mount):

```bash
PYTHONPATH=/data/ycfeng/sota-engine/miles:$PYTHONPATH "$LOCAL_STEPMIND_PYTHON" -u -B -m tests.manual.agent_opd.check_swe_native_async --config "$INTEGRATION" --pair A --protocol r256 --receipt "$NEW_TRAINING_RECEIPT"
```

INTEGRATION and NEW_TRAINING_RECEIPT are absolute local-mounted paths. This uses
exactly the existing submit_swe_opd CLI/admission/launcher. No production fault flag
or new grader/submission pipeline exists. Do not unset credentials in the parent.
The guard rejects formal/changed profiles, RJob-worker execution, another mount,
nonlocal receipt/configuration and anything other than one explicit selected slot.

Smaller supported route: the GPU callback has already durably enqueued the owned
HF. Thus local Popen adds only repeated `--qualification-attempt UID`, NOT
`--qualification-checkpoint`: no local cloud mount/stat or second worker enqueue
is necessary. The existing qualification runner revalidates the manifest and all
native server/source/version/reader rules.

## Expected native receipts (parent acceptance, not yet observed here)

Let JOB be the actual created training job; CELL is `A-r256`. Local dispatch scope:
`dispatch.directory/JOB/`. Actual HF2/HF3 point IDs are
`qualification.CELL.JOB.HF2` and `qualification.CELL.JOB.HF3`; directories use
`hf/step_1` and `hf/step_2`, never fake formal HF50 identities.

1. HF2 SMOKE_PACKAGED publication precedes durable qualification enqueue/ready
   notification. `fault.json` contains only point_id, field=`AK_BASEMIND`, at.
   Its evaluator log reports `Native ACS evaluation requires inherited AK_BASEMIND`.
   No HF2 admission receipt/pending/job is created; local journal is UNVERIFIED and
   not automatically retried. Cloud HF2 remains QUEUED, deadline null, all400 slots
   missing; HF/source weights remain present.
2. Healthy native update3 continues independently. Compare actual native training
   records, HF2 publication/notification time and local child/fault time; do not
   infer concurrency just from an eventual successful exit.
3. HF3 uses the unchanged inherited private environment, the same evaluator argv
   and real two-GPU admission. Inspect local `receipts/POINT.admission-1.json`:
   submitted=true, real job_id, eval_gpus/requested_gpus=2 and the existing policy.
4. Inspect actual cloud point `workers/server-*/server.json`, `worker.json`,
   `cleanup.json`, native grader artifacts and `qualification_runs/*.json`.
   Exactly the selected UID must execute through native SWE. On an actual graded
   completion, denominator remains400/completed1/missing399/avg_at_n=null.
   A solved task is not required, but real grading/artifacts and no infrastructure
   failure are required. All readers exit and cleanup reports no live child members.
5. Existing training terminal receipt records native_execution_succeeded=true;
   local main returns0 even though observer reports1 for the failed HF2 child.
   Parent wait drains the real HF3 launcher. Local observer.json records HF2
   UNVERIFIED and HF3 EVALUATOR_EXITED/exit0. Both qualification HFs remain protected
   regardless of result; no formal full400 score or HF release is manufactured.

Do not turn missing/unknown/failed receipts into safe resubmission. Quota denial
retains the existing proven-denial cadence only; no scorer resume, reroll or
deadline renewal is introduced. Recording errors are auxiliary soft gates and
must not cancel healthy training/admitted evaluations, including aggregate32+ runs.

## Observed CPU verification

Environment: Python3.12.13, pytest9.1.1, torch2.11.0, transformers5.19.0;
`/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`; approved local temporary/cache paths.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/fast/test_swe_hf_export.py tests/fast/test_swe_evaluation_dispatch.py -k 'qualification or manual_native_async or manual_launcher' --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-native-async-first --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t03-native-async-first.xml
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/fast/test_swe_hf_export.py tests/fast/test_swe_evaluation_dispatch.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-native-async-final --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t03-native-async-final.xml
PYTHONPYCACHEPREFIX=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-native-async-pycache /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m compileall -q tests/manual/agent_opd/swe_hf_export.py tests/manual/agent_opd/watch_swe_evaluations.py tests/manual/agent_opd/check_swe_native_async.py tests/fast/test_swe_hf_export.py tests/fast/test_swe_evaluation_dispatch.py
git diff --check
```

First new checks:22 PASS/45 deselected,8.50s. Final affected files:69 PASS,29.16s
(HF32 cases11.957s, dispatcher37 cases15.364s from JUnit per-case durations).
The entire final run is below30s; both implicit stage-a-cpu files remain within budget.
Assertions cover default smoke, original callback, formal guard, actual identity,
qualification frozen selection, real fork rejection before admission, unchanged
parent credentials, independent healthy ACK/drain, and soft fault-record failure.

Formatting/lint used `/data/ycfeng/toolchain/bin/uv tool run --cache-dir
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache --index-url
http://mirrors.i.basemind.com/pypi/simple/ --allow-insecure-host mirrors.i.basemind.com`:
isort5.13.2 (`--profile black --line-length 119 --check-only`), Black24.3.0
(`--line-length 119`, final5 files unchanged), Ruff0.14.7 (`ruff check`) on the five
delivered source/test files. All final checks PASS. Initial Ruff B023 was a test
loop variable captured late; bind that result in the lambda. No production fix or
retry was needed. Existing Swig/Torch deprecation warnings remain unrelated.

Limits: CPU optimizer/collective/platform boundaries and HF3 receipt child are
fixtures, not native GPU/RJob/grader PASS. The actual forked HF2 submitter only
rejects synthetic missing credentials before optional platform imports. The CPU
400-slot summary reuses the existing portable test fixture, not fabricated grader
results. Parent real qualification and another owner's minimal native attempt
accounting remain outstanding. No unrelated worker/grading suites were run.
Checkpoint: `evidence/checkpoint_t03_native_async.md`.
