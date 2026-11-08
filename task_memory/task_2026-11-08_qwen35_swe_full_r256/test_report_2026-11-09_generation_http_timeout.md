## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Primary accepts the two-file test-only diff and reruns all five added cases successfully; no production change. |
| 2026-11-09 | Verify the existing Qwen generation deadline and typed SWE recipe transport; record the withdrawn shared-client proposal, bounded negative control, test-only changes, and verification limits. |

# Generation HTTP timeout verification

Task ID: **T02-D13-HTTP-TIMEOUT**. Final scope: test-only verification of the existing Qwen guard, not a shared HTTP implementation change. Parent owns acceptance, progress, resource decisions, and commits.

## Outcome and corrected inference

The current SWE generation path is already bounded:

1. `tests/manual/agent_opd/run_swe_opd.py:79` selects `tests.manual.agent_opd.qwen_alignment.generate`; line 115 passes the profile's request timeout.
2. `tests/manual/agent_opd/qwen_alignment.py:96-97` wraps the entire native `single_turn.generate` coroutine in `asyncio.wait_for`. Therefore request waits, response reads, retries, and retry sleeps share one overall generation budget.
3. The inspected DeepSWE smoke, round-robin, and formal profiles retain `request_timeout=3600` and `training.acquisition_seconds=1800`. `tests/manual/agent_opd/swe_replay.py:145-223` applies an independent absolute acquisition deadline and cancels unfinished slots without waiting indefinitely for cancellation suppression.

The unbounded read timeout of the low-level HTTP client does **not** imply an unbounded current SWE request. No evidence in this subtask establishes that a missing client timeout caused D12, that generation returned HTTP503 because KV usage exceeded 80%, or that a timeout change would improve acquisition capacity. The parent's counterevidence superseded the initial implementation proposal before any production edit.

Observed final verification: **93 passed** in the selected Qwen/SWE/schema suite, **8 passed** at the HTTP retry boundary, and **5 passing added cases** in the focused test-only verification. Existing native exceptions and external cancellation remain observable; no production behavior changed.

## Deliverables and unchanged files

| Path | Change and reason |
| --- | --- |
| `tests/fast/test_qwen35_sample_lifecycle.py:189-231` | Add two fake-clock cases for repeated503 responses. A 2-second overall budget expires after two attempts and two retry sleeps; a 5-second budget permits three503 responses followed by success on attempt4. This fills the multiple-retry coverage gap without changing retry policy. |
| `tests/fast/test_swe_launcher.py:179-266` | Add three profile cases exercising actual recipe argv, native hook resolution, validated `AllConfig`, `RolloutConfig` JSON transport, `_compute_rollout_function_config`, and actual `GenerateState` hook selection. A stalled in-memory HTTP request is cancelled after advancing the clock beyond the transported3600-second budget. |
| `evidence/t02-d13-test-only.diff` | Exact two-file test diff for primary review; no production changes. |
| `evidence/t02-d13-checkpoint.md` | Scoped progress/drift checkpoint and corrections. |

Only two existing test files changed:45 and90 added lines respectively. No schema field or timeout knob was added. `miles/utils/http_utils.py`, `miles/rollout/generate_hub/single_turn.py`, `tests/fast/utils/test_http_utils.py`, the Qwen/SWE implementations, shared profiles, and `progress.md` have no edits from this subtask. No commit, resource change, sample truncation, drop/refill policy change, or GPU/platform/cloud/credential operation occurred.

The typed test uses existing schema/fixture mechanisms, not a `SimpleNamespace` for configuration. Only the tokenizer/processor boundary and HTTP transport are substituted to keep execution local and independent of model downloads. Mutable router addresses are resolved in the test as native startup does. It verifies timeout transport and hook behavior, not Megatron's GPU-dependent full launch validation or scientific generation fidelity.

## Environment

- Working directory: `/data/ycfeng/sota-engine/miles`.
- Interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13.
- pytest9.1.1, httpx0.28.1, Pydantic2.13.5; Black24.3.0 and isort5.13.2 from the existing local lint packages.
- No conda activation, dependency installation, or network download. Commands set `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and `PYTHONDONTWRITEBYTECODE=1` where relevant.
- Raw logs and temporary inspection script are under `/data/ycfeng/tmp/opencode-v2-tmp/opencode/`; selected JUnit/static evidence is under this task's `evidence/` directory.

## Exact final commands

### Qwen, SWE bank cancellation, recipe, and schema regressions

```bash
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_qwen35_sample_lifecycle.py tests/fast/test_swe_launcher.py tests/fast/test_swe_replay.py tests/fast/utils/args/test_schema.py -k 'not teacher_and_student_scoring_keep_independent_native_total_timeouts and not native_scoring_timeout_preserves_teacher_failure_and_observer_soft_failure' -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-verified-regression --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-verified-regression.xml > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-verified-regression.log 2>&1
```

Expected: selected tests pass, native request cancellation drains, permanent errors remain errors, and late/invalid bank slots cannot alter sealed membership. Actual: **93 passed,3 deliberately deselected,20 dependency warnings,5.77s; exit0**. The3 deselections are existing socket-backed teacher/student scoring tests outside this network-free verification slice; assertions were not weakened.

Decisive reused tests:

- `test_generation_deadline_cancels_and_drains_native_request`: native hung request ends with `TimeoutError`, cancellation and cleanup both complete.
- `test_deadline_covers_native_retry_sleep_without_background_retries`:503 retry sleep is interrupted by the outer generation deadline.
- `test_external_cancellation_propagates_after_one_terminal_receipt[generate]`: external cancellation remains `CancelledError`, not a retry or timeout.
- `test_failed_attempt_does_not_prevent_a_later_successful_sample`: both permanent HTTP400 and timeout preserve the failed sample and permit a later independent success.
- `tests/fast/test_swe_replay.py:229`, `test_hung_late_invalid_collection_is_finite_and_slot_ordered[ValueError/CancelledError]`: deadline seals only successful slots2–5, records missing0/1, and late completion cannot change bank membership or append receipts.

### Existing HTTP retry policy

```bash
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 timeout 30s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/utils/test_http_utils.py::test_post_does_not_retry_permanent_client_errors tests/fast/utils/test_http_utils.py::test_post_still_retries_transient_responses -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-http-regression --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-http-regression.xml > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-http-regression.log 2>&1
```

Expected:400/401/403/404/422 make exactly one attempt;408/429/503 recover on the second attempt. Actual: **8 passed,2 warnings,0.26s; exit0**. Existing callers and retry limits remain unchanged.

### Formatting, lint, and scope preservation

```bash
env PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages BLACK_CACHE_DIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-black-cache PYTHONDONTWRITEBYTECODE=1 timeout 30s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02_d13_check_format.py > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-format.json
env PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages PYTHONDONTWRITEBYTECODE=1 timeout 30s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m ruff check --no-cache tests/fast/test_qwen35_sample_lifecycle.py tests/fast/test_swe_launcher.py > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-ruff.log 2>&1
git diff --check -- tests/fast/test_qwen35_sample_lifecycle.py tests/fast/test_swe_launcher.py
git diff -- miles/utils/http_utils.py miles/rollout/generate_hub/single_turn.py tests/fast/utils/test_http_utils.py tests/manual/agent_opd/qwen_alignment.py tests/manual/agent_opd/run_swe_opd.py tests/manual/agent_opd/swe_replay.py
```

Actual: new test fragments pass Black/isort; AST parse/compile pass; original file bytes outside the additions are preserved; Ruff reports **All checks passed!**; diff checks are clean and production diff is empty. Both files already have whole-file Black differences; `test_swe_launcher.py` also has pre-existing isort differences. These unrelated bytes remain untouched. Ruff reports only the existing deprecated configuration layout warning.

## Negative control, explicitly not a production RED

This bounded control bypasses the existing Qwen wrapper only in one Python process. The in-memory endpoint returns success after4 attempts, so the control itself terminates. It makes no production file edit.

```bash
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 timeout 30s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'import asyncio, types, pytest; from tests.manual.agent_opd import qwen_alignment
async def bypass_guard(awaitable, *, timeout):
    return await awaitable
qwen_alignment.asyncio = types.SimpleNamespace(wait_for=bypass_guard, CancelledError=asyncio.CancelledError)
print("NEGATIVE CONTROL: bypass the existing Qwen deadline; production files are unchanged")
raise SystemExit(pytest.main(["tests/fast/test_qwen35_sample_lifecycle.py::test_repeated_503_responses_share_one_generation_deadline[2-2]", "-q", "-p", "no:cacheprovider", "--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-negative-control", "--junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-negative-control.xml"]))' > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-negative-control.log 2>&1
```

Expected negative-control result: the deadline assertion fails. Actual: **1 expected failure**, `Failed: DID NOT RAISE TimeoutError`,0.46s; exit1. With the actual wrapper retained, both repeated503 cases pass. This demonstrates regression sensitivity; it is **not** evidence of a production bug or a production RED→GREEN fix.

## Preserved initial proposal and test-development history

Before the parent's decisive recipe counterevidence, the initial proposal was to add an optional `timeout=None` to public `http_utils.post`, wrap its existing dispatch/retry coroutine in `asyncio.wait_for`, and pass the native field from `single_turn`. No production patch was applied.

Two provisional low-level tests were added and run:

```bash
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/utils/test_http_utils.py -k 'test_post_timeout' -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-http-timeout-red --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-http-timeout-red.xml > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-http-timeout-red.log 2>&1
```

Actual:2 failures at `TypeError: post() got an unexpected keyword argument 'timeout'`, before entering HTTP/retry behavior. This was a proposed API-contract RED, **not** a reproduced current SWE timeout defect. After the scope correction, only those provisional test additions were removed with `patch`; the low-level test file returned to its original bytes. The RED JUnit remains as an explicitly superseded artifact.

The first new test-only invocation used a frozen clock and unresolved router addresses in the typed fixture. It produced a retry-count assertion failure and hit the60-second test-process watchdog; the frozen-clock-only rerun printed1 failed/1 passed before its15-second watchdog. Neither was a production failure. Diagnosis: timer callbacks need event-loop scheduling turns, and typed router addresses must be resolved before HTTP dispatch. The corrected tests retain real clock progression plus a simulated offset, yield for timer callbacks, and resolve the existing mutable router addresses. The next focused command passed5 cases in2.83s:

```bash
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 timeout 30s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_qwen35_sample_lifecycle.py tests/fast/test_swe_launcher.py -k 'repeated_503_responses or recipe_timeout_reaches' -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-guard-additions-fixed --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-guard-additions-fixed.xml > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-guard-additions-fixed.log 2>&1
```

An overly broad regression command used a file-path expression in `-k` that did not exclude the low-level HTTP module. It unintentionally ran existing **local loopback socket tests** despite the no-network scope; no external network access or model download was performed. The result was161 passed and2 failures from existing `test_custom_view.py` Megatron parser tests: `ModuleNotFoundError: No module named 'megatron'`. Evidence: `evidence/t02-d13-final-regression.xml`; raw log `/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-final-regression.log`. The selection mistake was reported to the parent and corrected using explicit HTTP test nodes. No dependency workaround, assertion weakening, or environment change followed.

## Limits and parent follow-up

- No remaining current-generation guard defect was reproduced in this scope. Native `asyncio.wait_for` can depend on cooperative cancellation; fault-injected httpx cancellation drains, while the bank's existing separate deadline protects collection from late private results.
- The two unrelated Megatron-dependent parser tests remain unverified in this CPU environment. The actual typed timeout/hook path is verified through validated schemas and serialization, but full GPU-dependent parser/launch validation was not run.
- HTTP response/clock fault injection and successful cancellation do not certify231/256 acquisition, KV pressure, throughput, native capacity, scoring/backward/optimizer acceptance, or any formal cell. D12's recorded capacity failure remains unchanged.
- Parent reviews and commits the test-only diff. `progress.md` was not edited because it has concurrent ownership. Suggested entry:

> completed T02-D13-HTTP-TIMEOUT local verification: current SWE selects qwen_alignment.generate, whose existing wait_for bounds the entire native request/retry chain at3600s; independent bank acquisition remains1800s. No shared-core/schema/profile change. Added repeated503 total-budget and actual typed recipe transport tests;93 selected Qwen/SWE/schema tests +8 HTTP retry tests pass. Explicit guard-bypass negative control fails as expected; initial low-level unexpected-timeout-argument RED is superseded, not a production bug. Broader selection mistakenly ran loopback tests and exposed2 unavailable Megatron parser checks; corrected explicit-node verification passes. Native capacity and231/256 remain unverified; primary review/commit pending.

## Primary acceptance

Primary inspected the actual two-file diff and confirmed no sharedHTTP/single-turn production diff. Repeated503 tests consume one deadline across responses and sleeps; native recipe tests carry the existing timeout through validated schema/JSON transport to the actual selected Qwen hook. No full GPU-dependent parser claim is made.

```bash
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 timeout 30s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_qwen35_sample_lifecycle.py tests/fast/test_swe_launcher.py -k 'repeated_503_responses or recipe_timeout_reaches' -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-parent-guard-20261109 --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-parent-guard.xml
```

Expected five added cases pass and stalled HTTP cancellation completes. Observed **5 passed,34 deselected,20 dependency warnings,2.97s,exit0**,Python3.12.13. JUnit:`evidence/t02-d13-parent-guard.xml`. `git diff --check` over both test files and task records passes. No new GPU job or production behavior change occurred.
