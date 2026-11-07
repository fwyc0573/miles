## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Parent verifies76 pinned tests/11.88s and closes preparation review/documentation finding; actual training acceptance remains pending. |
| 2026-11-07 | Record QWEN-P3-SAMPLE-BOUNDARIES implementation, red/green evidence, focused CPU checks and the completion checkpoint. |

## 1. 规划完成情况

**汇总：** PASS 5｜BLOCKED/FAILED/SKIPPED 0｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Qwen native generation deadline | PASS | `qwen_alignment.py:97` uses the existing request-timeout setting around the entire native generation await, including HTTP retries and retry sleeps. |
| Attempt start/terminal receipts | PASS | `qwen_alignment.py:25-54` emits `QWEN35_SAMPLE_ATTEMPT` JSON lines at both adapter boundaries and reraises every caught exception/cancellation. |
| Student observer timeout inspection | PASS | `alignment.py:24-26` calls the same single-attempt `on_policy_distillation._post_json`; its `aiohttp.ClientTimeout(total=timeout_secs)` already bounds the complete HTTP operation. No second observer or teacher timeout was added. |
| Focused CPU regressions | PASS | 14 new lifecycle cases and 29 existing launcher/generation/teacher/probability cases pass; both owned Python files pass syntax and whitespace checks. |
| Pinned-runtime preparation | PASS | Parent job `exp-1107-084523-486765`:76 passed/11.88s, zero GPUs. |
| Actual training/result acceptance | TODO | Native updates, new fused D8 measurements and final artifacts remain unverified. |

### Exact verification environment

- Working directory: `/data/ycfeng/sota-engine/miles`.
- Python executable: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`; Python `3.12.13`, Clang `22.1.3`.
- `pytest 9.1.1`, `torch 2.11.0`, `sglang 0.5.23`, `aiohttp 3.14.3`, `httpx 0.28.1`, `httpcore 1.0.9`.
- `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`; `-B` disables bytecode writes and `-p no:cacheprovider` disables pytest cache writes.
- No environment or dependency change was made. The initial inspection command used unavailable `python` and exited 127; subsequent commands use the exact approved executable.

### Red/green commands and observations

All pytest commands used the prefix below, from the working directory above:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -p no:cacheprovider
```

| Arguments after the prefix | Expected result | Actual result |
| --- | --- | --- |
| `tests/fast/test_qwen35_sample_lifecycle.py -q` before the deadline edit | RED: the configured 0.05-second timeout does not finish the stalled native request within the test's independent 0.5-second observation window. | 1 failed, 3.21s; `done == set()` and the task remained at the old unbounded generation await. Test cleanup cancelled/drained it. |
| Same command after the deadline edit | GREEN: timeout cancels the real async HTTP transport handler and drains it before returning. | 1 passed, 2.43s. |
| `tests/fast/test_qwen35_sample_lifecycle.py -k success_receipts -q` before receipt logging | RED: success has no start/end JSON receipts. | 1 failed, 1 deselected, 2.58s; `not enough values to unpack (expected 2, got 0)`. Native token/probability/identity assertions passed before that failure. |
| `tests/fast/test_qwen35_sample_lifecycle.py -q` after generation receipt logging | GREEN: both generation cases pass. | 2 passed, 2.60s. |
| `tests/fast/test_qwen35_sample_lifecycle.py -k teacher_failure -q` before teacher receipt logging | RED: teacher failure has no start/end JSON receipts. | 1 failed, 2 deselected, 2.61s; same missing-receipt error, with the original exception preserved. |
| `tests/fast/test_qwen35_sample_lifecycle.py -q` after teacher receipt logging | GREEN: all three tracer cases pass. | 3 passed, 2.55s. |
| Same command after adding the remaining requested boundary checks | Fixture diagnosis, not a production failure. | 12 passed, 2 failed, 3.01s. Both failures exposed missing fixture `sglang_model_routers`; the unchanged observer recorded `AttributeError: 'types.SimpleNamespace' object has no attribute 'sglang_model_routers'`. |
| Same command after adding the supported fixture router field | GREEN: all lifecycle criteria pass. | **14 passed**, 18 warnings, **3.16s**. |
| `tests/fast/test_qwen35_opd_launcher.py -k 'teacher or generation or probability or reader_verdict or unresolved_decode or prefill' -q` | GREEN: existing generation/teacher/probability contracts remain valid; exclude the known pinned-only parser case. | **29 passed**, 33 deselected, 20 warnings, **8.33s**. No existing launcher fixture was edited. |

The last two commands ran independently in parallel. Their total is 43 passing cases, not a combined-suite timing. Warnings are existing SWIG/Torch/SGLang/deprecated datetime warnings, not test failures.

The syntax/environment command was:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import ast
import importlib.metadata
import sys
from pathlib import Path
print('Python:', sys.version)
for name in ('pytest', 'torch', 'sglang', 'aiohttp', 'httpx', 'httpcore'):
    print(name + ':', importlib.metadata.version(name))
for path in (Path('tests/manual/agent_opd/qwen_alignment.py'), Path('tests/fast/test_qwen35_sample_lifecycle.py')):
    text = path.read_text()
    compile(ast.parse(text), str(path), 'exec')
    trailing = [index for index, line in enumerate(text.splitlines(), 1) if line.rstrip() != line]
    assert not trailing, (str(path), trailing)
    print(str(path) + ': syntax and trailing whitespace PASS')
PY
```

Observed exit 0, both files PASS; environment values are listed above. No bytecode was written.

### Acceptance evidence

- Timeout cancellation/drain uses real `asyncio.wait_for`, the actual native single-turn request/update path and native `http_utils._post`, with only the external HTTP transport replaced by `httpx.MockTransport`. A transport handler remains stalled until cancelled and performs an awaited drain before the caller observes `TimeoutError`.
- Native retry-sleep timeout is exercised with HTTP 503: exactly one HTTP request occurs, and the entire invocation terminates during the native retry sleep. HTTP 400 and timeout failures each permit a separate later sample to complete successfully; this is adapter recovery evidence, not a second verification of the owner's native refill/credit tests.
- External cancellation at generation and teacher boundaries propagates `CancelledError` after draining the awaited fixture. A start receipt is already visible while the request is pending, and exactly one terminal receipt follows cancellation.
- Success preserves the original Sample object, sampled token IDs/logprobs, sampling parameters, source/history/train identities and probability declaration. Native `completed`, `truncated` and `aborted` states remain distinct from the adapter receipt's `succeeded` outcome. End receipts carry the original decode/prefill version spans, not invented versions.
- Changed prompt hashes fail before any HTTP request and still produce start/end attempt receipts.
- Real local `aiohttp` scoring requests each take at least 0.12 seconds with a 0.2-second per-POST total bound: the whole teacher-plus-observer operation exceeds 0.24 seconds and succeeds. This verifies there is no duplicate timeout enclosing both scoring requests. Each endpoint receives one request, with the unchanged sampled token IDs.
- Real teacher HTTP timeout propagates and prevents observer invocation. Real observer HTTP timeout retains native reward success, records existing `student_rescoring.status=unverified` with `error_type=TimeoutError`, and does not claim measured prefill probabilities. No new exception-suppressing path was added.

### Parent pinned verification and review

Pinned command (repo cwd, image from `training_config.json`, Python3.12.16, existing CUDA compatibility path prepended to `LD_LIBRARY_PATH`, offline model access, `CUDA_VISIBLE_DEVICES=''`, plugin autoload enabled):

```bash
/opt/sglang/bin/python3 -B -m pytest -p no:cacheprovider \
  tests/fast/test_qwen35_sample_lifecycle.py tests/fast/test_qwen35_opd_launcher.py \
  -q --basetemp=/var/tmp/qwen-samples-exp-1107-084523-486765/pytest --tb=short
```

Expected: all76 lifecycle/launcher cases pass with the native parser and optimizer-budget assertions intact. Actual: **76 passed,54 warnings,11.88s; PASS**. Log: [sample-boundaries-exp-1107-084523-486765.log](evidence/sample-boundaries-exp-1107-084523-486765.log). Reviewer `QWEN-P3-RESUME-PREP` independently inspected the code/native paths and this result, found no actionable code defect, and requested stale preparation-status updates. Those updates are complete; the review did not execute tests.

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** QWEN-P3-SAMPLE-BOUNDARIES 开始至本次 focused 验证完成｜**当前前沿：** 父会话的 pinned-runtime 检查和 A/B 正式恢复。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | Tests cover only the assigned lifecycle criteria; stop after 14+29 passing cases. |
| D2 细节反复重试 | CLEAR | Three expected red/green slices verified the recorded cause; the one later fixture failure was diagnosed from its exact AttributeError and repaired only in the new test fixture. |
| D3 支线问题修补 | CLEAR | No unrelated module or issue was changed. |
| D4 可并行任务停滞 | CLEAR | Scoped subagent assignment explicitly prohibits delegation/platform work; independent final test commands ran in parallel. |
| D5 超范围镀金 | CLEAR | No shared contract, retry policy, filter reason, scheduler, flag, Sample field or generic framework was added. |
| D6 分析空转 | CLEAR | Inspected observer timeout ownership before editing; delivered and verified the two assigned seams. |
| D7 路线违背 | CLEAR | D7/D9/D12/D14, native exception propagation, filter/refill behavior and observer soft-failure handling remain unchanged. |

**文档检查：** S1–S6 均未发现明显缺陷。`plan.md:56` owns both preparation gaps and explicitly preserves C's independent work. This report records local completion without marking the parent P3 task or runtime gates complete.
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Parent runs the required focused cases in the selected pinned runtime; completion means actual runtime contracts pass without weakening the pinned-only parser test.
2. Parent advances authorized A/B formal runs and preserves C independently; completion remains the existing P3 numerical/update/publication/export criteria, not a successful CPU test exit.

## 4. 最值得关注的 3 点

1. Count attempted generation by unique `attempt_id` on `stage=generate,event=start`; join terminal outcomes by that ID. Count teacher invocations separately. A start without an end is interrupted/unresolved work, never a never-attempted sample. `status=succeeded` means the adapter returned successfully, **not** that a sample was consumed; native consumed-eight, filtered, aborted and optimizer counts remain authoritative and separate.
2. Generation reuses the existing timeout to bound the entire native HTTP retry chain. Teacher and observer POSTs already have independent single-attempt `aiohttp` total bounds; duplicating them would change the established soft-observer behavior or incorrectly impose one shared deadline.
3. CPU transport fixtures prove adapter cancellation/drain and metadata preservation; local loopback `aiohttp` requests prove real scoring timeout behavior. No native SGLang engine abort/GPU runtime result is claimed. The parent's exact pinned SGLang router AbortOnDrop/abort-before-dispatch findings remain source-only evidence; the owner already verified native refill/credit isolation and those unrelated suites were not repeated.
