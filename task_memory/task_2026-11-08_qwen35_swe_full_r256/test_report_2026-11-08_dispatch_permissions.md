## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Add primary's real cross-UID filesystem check and readiness for the unchanged native qualification profile. |
| 2026-11-08 | Record T03-DISPATCH-PERMISSIONS RED, ranked hypotheses, single-variable test, local preparation fix, and CPU regression evidence. |

# Dispatch base creation before native submission

**TaskID:** T03-DISPATCH-PERMISSIONS. **Scope:** local CPU reproduction, ordering repair, tests, and static verification only. No commit or GPU submission was performed. The earlier mounts ownership repair remains intact.

## Native evidence and smallest trigger

The primary supplied `/data/ycfeng/tmp/qwen35-swe-deepswe-native-async-fixed-20261108.log`. Native run `exp-1108-224927-865957` passed the mounts snapshot boundary but failed in `EvaluationWatcher.__init__ → _publish_once → _locked → path.parent.mkdir` with `PermissionError`, errno13, before any evaluator/fault. Healthy native training completion is reported by the primary, not independently reverified here.

The supplied pre-repair metadata `/data/ycfeng/tmp/qwen35-swe-dispatch-permission-red-20261108.json` records submitter UID/GID10250, a writable evidence parent owned10250/mode0700, and a dispatch base and old/new job directories owned0/mode0755 and not writable by the submitter. This is historical evidence, not this agent's current filesystem stat or ownership repair.

The minimal local trigger is a missing configured dispatch base when the fake backend starts a worker publication. The worker's previous-job notification creates the base first; subsequent local construction attempts the new job directory. A targeted `Path.mkdir` fault models errno13 **only when that base was worker-created**. No OS UID, GID, mode, or ownership is changed in the reproduction.

The loop drives real `submit_swe_opd.main`, real previous-job `notify_ready`, real watcher construction/publication/identity lock, and real observer thread; API/backend/workers are existing local fakes. Prior-job notification is ignored by the current job's observer, so no evaluator or network is needed.

## Ranked hypotheses and one tested prediction

The ranked list was shown before testing a prediction:

| Rank | Hypothesis | Falsifiable prediction | Result |
| --- | --- | --- | --- |
| 1 | Worker-first base creation causes the local ownership failure | Creating the same base locally before submission removes the constructor errno13 without changing configuration or training behavior | Supported by the single-variable precreation probe and the production-main GREEN loop. |
| 2 | A higher parent or resolved path is itself unwritable/incorrect | Local base creation also fails before worker submission | Not separately tested as the native cause. Supplied parent metadata is writable and the local precreation probe succeeds. Invalid-path/mount cases are separately covered as validation contracts. |
| 3 | The job directory or identity lock is independently restrictive | Base precreation succeeds but constructor/job mkdir/lock still fails | Not separately tested as the native cause. The tested local constructor and identity/watcher locks succeed with the base prepared. Cross-UID same-job races are not certified by CPU evidence. |

**RED twice:** backend boundary `base_prepared=false`; first base mkdir actor=`worker`; errno13; constructor completed0; observer run0; native wait1; training exit0; configuration file unchanged; actual CPU UID/GID10250.

**Single-variable H1 probe, before production repair:** only precreate the base locally. Backend boundary becomes `base_prepared=true`, no error, constructor/observer run1/1, wait1, training exit0, same configuration bytes.

**Production GREEN without manual precreation:** same event order and counts as the probe. Real filesystem stat checks confirm the configured base, current job directory, `identity.lock`, and `watcher.lock` belong to the executing UID/GID10250. Successful constructor publication and observer journaling also demonstrate local write readiness.

## Implementation and preserved contracts

### Primary cross-UID filesystem verification

Primary additionally executed a temporary filesystem test as local UID10250 and a root subprocess, using `/data/ycfeng/tmp/T03-DISPATCH-CROSS-UID/1794152124549359796`. A worker-created base produces the actual PermissionError for the local user's child mkdir. In the positive order, local base/job/identity lock owners are10250, root creates the ready notification, and the local user can read that notification and write its lock/journal. This is a real Linux ownership test, not the unit test's injected errno. It does not invoke production helpers or certify same-job races/native evaluator behavior.

Exact driver is the retained session shell invocation: Python creates the local namespace, invokes `sudo -n python3 -c <temporary root publisher> <namespace>`, then performs local mkdir/lock/read/journal assertions. Result: negative PermissionError, positive PASS. Machine-readable evidence: `/data/ycfeng/tmp/qwen35-swe-dispatch-cross-uid-20261108.json`. The earlier one-directory ownership repair remains nonrecursive and does not modify old job directories or HF; its separate receipt is `/data/ycfeng/tmp/qwen35-swe-dispatch-directory-owner-repair-20261108.json`.

The existing `deepswe_integration_config.json` remains byte-identical. Forty-nine full dispatch tests and this filesystem check permit a new explicit native qualification attempt through the existing entrypoint; actual HF2 failure/HF3 reload/grading and reader cleanup remain pending.

Actual submitter interpreter check: from `/data/ycfeng`, `PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron PYTHONNOUSERSITE=1 /data/ycfeng/tmp/stepmind-env/bin/python -B -` invoked `prepare_dispatch` on the real unchanged profile and asserted input SHA256, writable base, and base UID=current UID. PASS on Python3.10.6; profile SHA256=`62add9c465ee5a5a6b049c7d7d95959e31e1113a6832b887ac4009510bd73bd5`, owner10250. Full command is the retained primary shell invocation; log `/data/ycfeng/tmp/qwen35-swe-dispatch-local-py310-20261108.log`. No platform call was made by that check.

- `tests/manual/agent_opd/watch_swe_evaluations.py:349–364`: `prepare_dispatch(config_path, config)` obtains the existing evaluation configuration, returns immediately when absent, rejects worker context, reuses `validate_dispatch` and `_local_path`, checks integration mount/current directory, and performs only `directory.mkdir(parents=True, exist_ok=True)` for the configured local base. Preparation exceptions are logged as an explicit training soft gate.
- `tests/manual/agent_opd/submit_swe_opd.py:102`: invoke preparation **after admitted=true and before ResourceConfig/native backend submission**, while still in the existing admission critical section. No fake job ID or per-job configuration is created before a real job name exists.
- `tests/fast/test_swe_evaluation_dispatch.py:559–675`: nine focused cases reuse existing fake backend/workers and real main/watcher paths. No new fixture framework or CI declaration was added.

The change does not add a config key, flag, retry, fallback, worker UID setting, or second configuration/snapshot mechanism. It does not chmod/chown existing paths. The earlier `mounts=list(config["mounts"])` remains at submitter line108. `start_dispatch` retains its exact immutable-file equality check and error; ready notification fields remain `{point_id, job_id, checkpoint_dir, configuration}`. Native wait/terminal ACK and observer drain/failure handling are unchanged.

Verified invariants:

| Contract | Evidence |
| --- | --- |
| Base exists before worker publication | Fake backend records true before invoking the real previous-job notifier; this assertion was RED before repair. |
| Current constructor and locks are ready | Real constructor/observer complete once; base/job/identity/watcher-lock UID/GID equal the current process; frozen integration/evaluation JSON match inputs. |
| Configuration remains immutable | Main-path tests preserve both source files byte-for-byte; original mounts/string identities/public-mount behavior and actual-file-drift rejection pass the real ResourceConfig backstop. |
| Preparation failure does not block training | Injected errno13 logs preparation failure, backend still submits once, wait runs once, native_execution_succeeded=true. Existing observer startup failure remains isolated. |
| No evaluation means no preparation effects | No evaluation JSON read, no dispatch directory creation, no evaluation launch or error log; training succeeds. |
| No native submission means no preparation | Existing dry-run and denied-admission paths neither create the base nor submit/wait. |
| Local validation remains authoritative | Outside-mount path, integration/evaluation mount mismatch, invalid poll interval, and worker context all log soft-gate failures without creating paths. |

## Exact commands and results

Working directory: `/data/ycfeng/sota-engine/miles`. Python `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, **3.12.13**; pytest **9.1.1**. All temporary writes/logs are under `/data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS`. No credentials were inspected or authenticated; existing tests use dummy environment fixtures. No network, API, GPU, platform, cloud, SSH, sudo, chown, or chmod operation was made.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -s --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/red-run /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/test_dispatch_permissions_repro.py > /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/red.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -s --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/red-repeat-run /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/test_dispatch_permissions_repro.py > /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/red-repeat.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -s --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/h1-precreate-run /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/test_dispatch_permissions_repro.py -k True > /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/h1-precreate.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/persistent-red-run tests/fast/test_swe_evaluation_dispatch.py -k local_submitter_creates_dispatch_base > /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/persistent-red.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -s --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/green-run /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/test_dispatch_permissions_repro.py -k False > /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/green.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/focused-run tests/fast/test_swe_evaluation_dispatch.py -k 'dispatch_preparation or local_submitter_creates_dispatch_base' > /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/focused.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/full-run tests/fast/test_swe_evaluation_dispatch.py > /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/full.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -s --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/alias-regression-run /data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/test_dispatch_snapshot_repro.py > /data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/alias-regression.log 2>&1
```

| Check | Expected / actual | Verdict |
| --- | --- | --- |
| Original loop | Exact errno13 and observer-not-started assertion; 1 failed, 6.48s | PASS: expected RED |
| Repeat | Same verdict and boundary counts | PASS: deterministic RED |
| H1-only precreation probe before repair | 1 passed, 1 deselected, 6.94s | PASS |
| Persistent ordering regression before repair | Prepared=[False], expected=[True]; 1 failed, 48 deselected, 0.89s | PASS: expected RED |
| Production-main loop without manual precreation | 1 passed, 1 deselected, 6.60s | PASS |
| Focused preparation/default/validation cases | 9 passed, 40 deselected, 1.31s | PASS |
| Full affected dispatch file | 49 passed, 17.56s | PASS; remains below the whole-file30s fast CPU budget |
| Existing real ResourceConfig alias/minimal/original-profile/file-drift loop | 3 passed, 8.54s | PASS |

The original RED commands ran before the temporary test acquired the two-valued precreation parameter. That parameter is test-only; production has no flag. Post-repair `-k False` proves that production ordering, not the manual probe, fixes the original loop. The temporary permission fault is retained solely in the named local debug directory for primary reproduction; no production instrumentation remains.

### Static verification

Existing cached Ruff **0.14.7**, Black **24.3.0**, isort **5.13.2** were reused without installation.

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check --no-cache tests/manual/agent_opd/watch_swe_evaluations.py tests/manual/agent_opd/submit_swe_opd.py tests/fast/test_swe_evaluation_dispatch.py

BLACK_CACHE_DIR=/data/ycfeng/tmp/T03-DISPATCH-PERMISSIONS/black-cache PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check tests/manual/agent_opd/watch_swe_evaluations.py tests/fast/test_swe_evaluation_dispatch.py

PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m isort --check-only tests/manual/agent_opd/watch_swe_evaluations.py tests/manual/agent_opd/submit_swe_opd.py tests/fast/test_swe_evaluation_dispatch.py

git diff --check -- tests/manual/agent_opd/watch_swe_evaluations.py tests/manual/agent_opd/submit_swe_opd.py tests/fast/test_swe_evaluation_dispatch.py
```

All checks PASS. Black initially requested one newly added test assignment be collapsed; it was corrected before the final full run. The submitter's pre-existing compact layout was preserved rather than bulk reformatted; Ruff/isort check it in full. Existing Ruff config and two Swig deprecation warnings remain unrelated.

The scope audit also passed: all five owned files are whitespace-clean, all three Python files parse, and seven existing lifecycle/validation definitions are AST-identical to HEAD. This confirms the watcher, frozen comparison, worker notification, terminal ACK, and existing path validation were not rewritten.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import ast
import subprocess
from pathlib import Path
files = [
    'tests/manual/agent_opd/watch_swe_evaluations.py',
    'tests/manual/agent_opd/submit_swe_opd.py',
    'tests/fast/test_swe_evaluation_dispatch.py',
    'task_memory/task_2026-11-08_qwen35_swe_full_r256/issues.md',
    'task_memory/task_2026-11-08_qwen35_swe_full_r256/test_report_2026-11-08_dispatch_permissions.md',
]
for file in files:
    text = Path(file).read_text()
    assert text.endswith('\n') and all(line == line.rstrip() for line in text.splitlines()), file
    if file.endswith('.py'):
        ast.parse(text, filename=file)
unchanged = {
    files[0]: ['start_dispatch', 'finish_dispatch', 'EvaluationWatcher', 'notify_ready'],
    files[1]: ['_validate_paths', '_job_succeeded', '_finish_training'],
}
for file, names in unchanged.items():
    before = ast.parse(subprocess.check_output(['git', 'show', f'HEAD:{file}'], text=True))
    after = ast.parse(Path(file).read_text())
    for name in names:
        old = next(node for node in before.body if getattr(node, 'name', None) == name)
        new = next(node for node in after.body if getattr(node, 'name', None) == name)
        assert ast.dump(old) == ast.dump(new), (file, name)
print('PASS: five owned files are whitespace-clean; three Python files parse; seven existing lifecycle/validation definitions match HEAD exactly')
PY
```

## Limits and handoff

- This prevents worker-first creation of a **new** configured base. It deliberately does not change an already root-owned base, old job directories, or old identity locks. The primary owns the one-existing-base remediation and its verification.
- CPU worker/API/backend are fakes, and the cross-UID denial is injected rather than produced by changing OS permissions. Current local directory/lock ownership and write readiness are exercised for real. Distinct-UID same-job publication/startup races and actual HF2-failure/HF3 native isolation remain outside this CPU verdict.
- No runtime profile, worker publication schema, mount UID/mode policy, evaluation deadline, admission policy, or scientific parameter was changed. No recursive filesystem operation, retry, fallback path, broad edit, staging, commit, or GPU rerun was performed.
- Ticket03 remains in progress until the primary verifies the native asynchronous evaluation scenario. This report completes only T03-DISPATCH-PERMISSIONS's CPU scope.
