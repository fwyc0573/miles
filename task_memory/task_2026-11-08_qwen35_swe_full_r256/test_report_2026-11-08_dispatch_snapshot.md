## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record T03-DISPATCH-SNAPSHOT-RCA constructor/iterator/dispatch evidence, ownership repair, and CPU regression results. |

# Dispatch configuration ownership — CPU verification

**TaskID:** T03-DISPATCH-SNAPSHOT-RCA. **Scope:** CPU-only Stage2. GPU rerun, live-job acceptance, and final commit remain owned by the primary.

## Cause and implementation

The submitter passed its parsed configuration's mounts list directly to `ResourceConfig`. Steptron's `Config._merge_args` assigns keyword values without copying them (`/data/ycfeng/steptron/steptron/exp/utils.py:164–165`). The real `ResourceConfig.__iter__` appends `PUBLIC_MOUNT` (`/data/ycfeng/steptron/steptron/exp/base_exp.py:4459–4460`). Native `RJob.submit_rjob` invokes that iterator before submission (`/data/ycfeng/steptron/steptron/utils/stepmind.py:697`). The caller's object therefore changed while the JSON file did not.

`tests/manual/agent_opd/submit_swe_opd.py:104–107` now passes `mounts=list(config["mounts"])`. This gives the resource its own list and preserves the parsed input. Both reachable iterator branches only append the immutable public-mount string; neither mutates mount elements. A shallow list copy is sufficient. No extra configuration snapshot, retry, flag, or DeepSWE-specific branch was added. `start_dispatch` and its frozen-file equality check and diagnostic soft gate were not changed.

The existing `_local_training` seam in `tests/fast/test_swe_evaluation_dispatch.py` now replays this native list append before returning fake workers. It previously used `SimpleNamespace` plus a backend that immediately returned workers and thus missed the bug. Three persistent cases cover empty mounts, already-present public mount, and actual temporary-file drift. They exercise the production `submit_swe_opd.main` and real watcher; the fake resource keeps CI independent of external Steptron dependencies. Separate local verification uses the **real** Steptron `ResourceConfig` and its real iterator.

## Tested hypotheses

The primary showed the ranked hypotheses before these tests.

| Hypothesis | Prediction | Observed result |
| --- | --- | --- |
| H1: borrowed mounts are mutated by native resource iteration | Constructor leaves equality intact; iterator creates the first difference in mounts | Supported. After construction/before iteration: no differing fields, shared list. After iteration: only mounts differs, 0 → 1 entries. |
| H2: the configuration file is rewritten during submission | The dispatch-time file digest differs from its pre-submit digest | Falsified for the deterministic CPU reproduction: identical bytes and digest at every boundary. Deliberate file drift is separately detected after the repair. |
| H3: a pre-iterator conversion mutates the caller object | A difference exists after construction or before iteration | Falsified for the deterministic CPU reproduction: both boundaries still equal the file. |

These observations identify the local cause; they do not retrospectively instrument the running native job.

## Boundary evidence

Pre-repair minimal profile, `stage2-red.log`:

| Boundary | Caller mounts | Resource mounts | Shared list | Differing fields | File bytes |
| --- | --- | --- | --- | --- | --- |
| Before constructor | 0 | — | — | none | unchanged |
| After constructor | 0 | 0 | yes | none | unchanged |
| Before iterator | 0 | 0 | yes | none | unchanged |
| After iterator | 1 | 1 | yes | mounts | unchanged |
| Dispatch | 1 | 1 | yes | mounts | unchanged |

All five boundaries have SHA256 `2051c4ea46ea3eb253ce2074574dff6dad67a87d1d6ef464c2313bdb6d5aa9dc`. The exact production error is `ValueError: Training integration configuration changed after submission`. Watcher construction/run = 0/0; native wait = 1; healthy fake training exit = 0.

Post-repair, `stage2-final.log`:

| Case | Caller/resource mounts after iteration | Shared list | File bytes | Watcher construction/run | Native wait | Training ACK |
| --- | --- | --- | --- | --- | --- | --- |
| Minimal unchanged profile | 0 / 1 | no | unchanged | 1 / 1 | 1 | exit 0, native_execution_succeeded=true |
| Actual profile's original shapes, mounts, and training fields, with temporary local IO paths | 2 / 3 | no | unchanged | 1 / 1 | 1 | exit 0, native_execution_succeeded=true |
| Deliberate temporary-file phase change | 0 / 1 | no | changed | 0 / 0 | 1 | exit 0, native_execution_succeeded=true |

The original mount entries retain their identities and order. The public mount is still appended exactly once. In the file-drift case, the first difference is `phase` after the deliberate write; SHA256 changes from `52803857d680a7ff52649799edb0e06aedb2b3f4a98f41bc5a52339cabee1828` to `8a6817fe693f01d86b95b9b97f1448cd68666f019baaa259d8294931a43e994b`. The original diagnostic error is retained while training succeeds.

The actual input profile was read only. Its before/after SHA256 remains `62add9c465ee5a5a6b049c7d7d95959e31e1113a6832b887ac4009510bd73bd5` at `task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_integration_config.json`.

## Commands and results

Working directory: `/data/ycfeng/sota-engine/miles`. Python: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, **3.12.13**; pytest **9.1.1**. All worker/API responses are local fakes. No authentication, network, platform, GPU, cloud, SSH, or live-job operation was performed. No packages were installed.

### Real ResourceConfig RED → GREEN

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -s --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/stage2-red-run /data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/test_dispatch_snapshot_repro.py > /data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/stage2-red.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -s --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/stage2-green-run /data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/test_dispatch_snapshot_repro.py > /data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/stage2-green.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -s --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/stage2-final-run /data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/test_dispatch_snapshot_repro.py > /data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/stage2-final.log 2>&1
```

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Pre-repair boundary loop | Exact production exception and observer-not-started assertion | 1 failed, 7.53s; expected RED | PASS: reproduction |
| Same minimal loop after repair | Observer initializes/runs once, wait once, unchanged file | 1 passed, 7.96s | PASS |
| Final real-resource minimal/original-profile/file-drift cases | Owned lists; native public mount retained; true drift rejected without training failure | 3 passed, 9.25s | PASS |

### Persistent dispatch regressions

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/persistent-red-run tests/fast/test_swe_evaluation_dispatch.py -k 'training_resource_owns_mounts or real_file_drift' > /data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/persistent-red.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/persistent-green-run tests/fast/test_swe_evaluation_dispatch.py -k 'training_resource_owns_mounts or real_file_drift' > /data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/persistent-green.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/dispatch-full-run tests/fast/test_swe_evaluation_dispatch.py > /data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/dispatch-full.log 2>&1

/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/dispatch-final-run tests/fast/test_swe_evaluation_dispatch.py > /data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/dispatch-final.log 2>&1
```

| Check | Actual | Verdict |
| --- | --- | --- |
| New regressions before repair | 2 failed, 1 passed, 37 deselected, 0.84s; ownership failures include the already-present public mount | PASS: expected RED |
| New regressions after repair | 3 passed, 37 deselected, 2.35s | PASS |
| Complete affected dispatch file | 40 passed, 15.92s | PASS |
| Final formatting-only rerun | 40 passed, 2 warnings, 13.90s | PASS |

The full file includes real local evaluator-process handoff/drain, observer startup failure, native wait failure, failed evaluator isolation, conservative restart/admission handling, and manual native-async guard coverage. Existing two Swig deprecation warnings remain; no test failure is unresolved.

### Static checks

Existing cached tools: Ruff **0.14.7**, Black **24.3.0**, isort **5.13.2**.

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check --no-cache tests/manual/agent_opd/submit_swe_opd.py tests/fast/test_swe_evaluation_dispatch.py

PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check tests/fast/test_swe_evaluation_dispatch.py

PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m isort --check-only tests/manual/agent_opd/submit_swe_opd.py tests/fast/test_swe_evaluation_dispatch.py

git diff --check -- tests/manual/agent_opd/submit_swe_opd.py tests/fast/test_swe_evaluation_dispatch.py
```

All four checks PASS. The submitter's existing compact formatting was preserved rather than bulk reformatted; Ruff/isort cover that file in full. Initial `python -m ruff` / `python -m black` attempts reported missing modules, resolved by using inspected existing cached tools. Black initially requested one newly edited assignment be collapsed; it was corrected and the final full test-file Black check passed. Ruff reports only the existing top-level configuration deprecation warning.

The following final scope check also passed, including the new untracked task documents:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import ast
from pathlib import Path
paths = [
    Path('tests/manual/agent_opd/submit_swe_opd.py'),
    Path('tests/fast/test_swe_evaluation_dispatch.py'),
    Path('task_memory/task_2026-11-08_qwen35_swe_full_r256/issues.md'),
    Path('task_memory/task_2026-11-08_qwen35_swe_full_r256/test_report_2026-11-08_dispatch_snapshot.md'),
]
for path in paths:
    text = path.read_text()
    assert text.endswith('\n') and all(line == line.rstrip() for line in text.splitlines()), path
    if path.suffix == '.py':
        ast.parse(text, filename=str(path))
print('PASS: four owned files have clean whitespace; both Python files parse')
PY
```

## Limits and handoff

- The local loop uses the real Steptron resource class/iterator but fake backend/API/workers; it does not submit a native job or certify real GPU training/evaluation artifacts.
- Original-profile replay transports only the relevant fields into temporary fixture IO paths; no actual profile was edited and no volume was accessed.
- Persistent CI regressions replay the inspected list mutation at the existing seam, without introducing a Steptron/torch dependency into fast CI.
- No production debug instrumentation, guard weakening, retries, additional snapshot mechanism, or unrelated changes were added. Temporary boundary instrumentation remains only in `/data/ycfeng/tmp/T03-DISPATCH-SNAPSHOT-RCA/test_dispatch_snapshot_repro.py`.
- The primary owns GPU rerun, final task acceptance, and commit. No commit or staging was performed by this agent.
