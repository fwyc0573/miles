## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record the CPU RED/GREEN regression, minimal mixed-session correction, verification and native limits. |

# Hybrid Weight-Update Session Test Report

Task ID: `profile-initial-weight-sync-20261109`.

## Scope and Environment

- Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`; branch `agent-opd-h800-capacity`, initially clean at `46e7b292ab13148d78882ca3781c9671ad07ca56`.
- Interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`; Python 3.12.13, pytest 9.1.1, torch 2.11.0, local SGLang 0.5.23, Linux. No dependency installation or environment/configuration change.
- Existing offline lint packages: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages`; Ruff 0.14.7, Black 24.3.0, isort 5.13.2. Tools read repository `pyproject.toml`.
- Owned changes only: `miles/backends/training_utils/weight_update/protocols/cuda_ipc.py`, `tests/fast/backends/training_utils/weight_update/test_dist_weight_update_lifecycle.py`, and this report. Primary-owned requirements/plan/progress/summary remain unchanged.
- No platform/authentication/RJob/cloud/GPU operation or network connection was performed. Existing baseline distributed-group tests reserve ephemeral local ports using socket bind, without listen/connect/transmit; the final suite deselects these three tests to avoid repeating socket creation.

## Change and Required Gain

`UpdateWeightFromTensor.connect()` already builds lifecycle cell updaters for every rollout engine. Its mixed-layout branch then incorrectly replaced that dictionary with a colocated-only dictionary while still selecting dedicated engines for distributed tensor transfer.

The correction deletes only that three-line dictionary reassignment. The original complete lifecycle dictionary survives. The existing colocated IPC client list, dedicated distributed client list, GPU offsets/counts, group construction, selectors, timeout values and NCCL parameters are unchanged. This repairs a concrete correctness requirement: a dedicated tensor receiver must participate in the same begin/end/version/resume lifecycle as a colocated receiver. No new flag, API, fallback, retry or alternate lifecycle mechanism was added.

## Regression Seam and Expectations

The new parametrized test reuses the existing `_RecordingApiClient` and lifecycle phase conventions. It covers one colocated plus one dedicated engine and four colocated plus four dedicated engines, each engine with two GPUs, using the corresponding simulated trainer worlds of two and eight ranks.

Real code exercised:

- `WeightUpdater` construction and protocol selection;
- `WeightUpdater.connect_rollout_engines()` and `UpdateWeightFromTensor.connect()`;
- both successive `WeightUpdater.update_weights()` calls, with assigned versions 4 and 5;
- real hybrid protocol `begin_sync()`, `send_bucket()`, distributed transfer submission, finalization and post-resume hook;
- real cell updater creation, session fan-out and version publication.

For each version and each engine the test asserts exactly one ordered pause, cache flush, begin, end, matching version publication and continue-generation sequence. It checks the complete healthy cell-ID map used for successful-cell accounting. It also asserts that only dedicated clients reach the distributed group builder and distributed transfer; the rank-zero colocated client uses IPC.

CPU doubles are confined to physical/backend boundaries: a one-bucket CPU weight iterator supplied through the existing iterator factory, recording API clients instead of HTTP servers, distributed group/collective operations, CUDA IPC serialization/send and CUDA cache cleanup. Lifecycle/protocol classes and their methods are not replaced. The distributed transfer helper and actual async submission/wait machinery run against these doubles.

Only trainer rank zero is executed. In the four-plus-four case, the other three colocated engines receive their real rank-zero-driven lifecycle calls, but peer trainer ranks' IPC sends are not simulated. The one-plus-one case observes the tensor send and the full lifecycle for both receivers. No real actor, SGLang receiver, tensor transport or NCCL communication is claimed.

## Exact Test Commands

All commands ran from the working directory above. `-B` disables Python bytecode writes; pytest's cache provider is disabled. The RED and targeted GREEN commands were identical and used the same test, first before and then after the three-line correction.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/backends/training_utils/weight_update/test_cuda_ipc.py tests/fast/backends/training_utils/weight_update/test_dist_weight_update_lifecycle.py tests/fast/backends/training_utils/weight_update/test_broadcast.py
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/backends/training_utils/weight_update/test_dist_weight_update_lifecycle.py::test_mixed_engines_complete_successive_weight_update_sessions
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/backends/training_utils/weight_update/test_cuda_ipc.py tests/fast/backends/training_utils/weight_update/test_dist_weight_update_lifecycle.py tests/fast/backends/training_utils/weight_update/test_broadcast.py tests/fast/backends/training_utils/weight_update/test_weight_update_fan_out.py tests/fast/backends/training_utils/weight_update/test_updater.py tests/fast/backends/training_utils/weight_update/test_colocated_lora_base_resync.py tests/fast/backends/training_utils/weight_update/test_lora_weight_sync_validation.py -k 'not TestConnectRolloutEnginesFromDistributed'
```

| Run | Expected condition | Observed result | Verdict |
| --- | --- | --- | --- |
| Original existing-test baseline | Existing IPC, distributed protocol and lifecycle tests pass | 43 passed, 2 warnings, 0.75 s | PASS |
| New regression before correction | Both layouts expose dedicated lifecycle omission, rather than a fixture/import failure | 2 failed, 2 warnings, 0.37 s; dedicated trace contains only `update_weights_from_distributed` | Expected RED |
| Same regression after correction | Both layouts complete versions 4 and 5 for every engine with unchanged transfer selection | 2 passed, 2 warnings, 0.33 s | PASS |
| Related existing tests plus regression | Preserve colocated sends, sparse placement, fully distributed metadata/collectives, fan-out, LoRA and lifecycle behavior | 80 passed, 3 deselected, 2 warnings, 3.10 s | PASS |

The RED failure was a missing lifecycle, not a timeout: at the first dedicated engine the actual method list was `['update_weights_from_distributed']`, whereas the expected list includes all six preparation/finalization phases around the transfer. No fixture fix or failure suppression was needed. Both GREEN cases execute their second synchronization using the same connected protocol and engines.

The two pytest warnings are baseline SWIG deprecations concerning missing `__module__`; they were not suppressed. All observed runs remain below the fast-test execution budget.

## Lint and Diff Commands

```bash
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m ruff check --no-cache miles/backends/training_utils/weight_update/protocols/cuda_ipc.py tests/fast/backends/training_utils/weight_update/test_dist_weight_update_lifecycle.py
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check --diff miles/backends/training_utils/weight_update/protocols/cuda_ipc.py tests/fast/backends/training_utils/weight_update/test_dist_weight_update_lifecycle.py
BLACK_CACHE_DIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode/black-cache-hybrid-weight-session PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check --diff miles/backends/training_utils/weight_update/protocols/cuda_ipc.py tests/fast/backends/training_utils/weight_update/test_dist_weight_update_lifecycle.py
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m isort --check-only --diff miles/backends/training_utils/weight_update/protocols/cuda_ipc.py tests/fast/backends/training_utils/weight_update/test_dist_weight_update_lifecycle.py
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
from pathlib import Path
from tools.lint_config_attribute_access import _violations
paths=[Path('miles/backends/training_utils/weight_update/protocols/cuda_ipc.py'),Path('tests/fast/backends/training_utils/weight_update/test_dist_weight_update_lifecycle.py')]
for path in paths:
 issues=_violations(path)
 print(str(path), 'PASS' if not issues else issues)
 assert not issues
PY
git diff --check
```

Ruff reported `All checks passed!`; Black left both files unchanged; isort emitted no diff; the repository's config-attribute check passed for both changed Python files; `git diff --check` returned no errors. Ruff also emitted the pre-existing configuration warning about top-level `select`/`ignore`; repository configuration was not changed. No formatter modified code.

The Black recheck explicitly places its cache under the approved temporary root; it also left both files unchanged.

## Native Limits and Acceptance Status

This CPU correction establishes the source-level mixed-session defect and its regression, not the root cause of native job `exp-1109-144110-764758`. Native SGLang `0.5.24.dev80+g056f871`, its first 400 response body and trainer stack readback remain primary-owned evidence work and were not duplicated during implementation. The tests do not validate native session rejection, native actor outputs, communication progress, optimizer/rollout execution or the upstream 256-turn business criterion.

D1/D22 acceptance remains blocked until the primary's native evidence and acceptance work complete. This commit is an isolated preparation deliverable, not authorization for parent integration or GPU execution.
