## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record the isolated D34 source correction, RED/GREEN evidence, CPU consumer checks and limits. |

# Capacity Input Lengths Test Report

Task ID: `profile-capacity-input-lengths-20261109`.

## Scope and Environment

- Worktree: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`; branch `agent-opd-h800-capacity`, initially clean at `7689fbec620d0538785d8896a1b55861888d6951`.
- Owned code: `tests/manual/agent_opd/swe_inputs.py` and the existing generation-budget tests at `tests/fast/rollout/test_sample_max_response_len.py`. This report is the only owned task record. Primary-owned configs, requirements, plan, progress and summary were not edited.
- The current delegation explicitly authorizes this discovered source-consumer blocker within D34, superseding the previous launcher's source exclusion at preparation `requirements.md:35`. The primary owns recording that updated authorization and scope.
- Interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`; Python 3.12.13, pytest 9.1.1, torch 2.11.0, SGLang 0.5.23, Linux. No environment/dependency installation or configuration change.
- Offline lint packages: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages`; Ruff 0.14.7, Black 24.3.0, isort 5.13.2. Caches and pytest fixture files stay under `/data/ycfeng/tmp/opencode-v2-tmp/opencode`.
- No platform/authentication/RJob/cloud/network/GPU operation was performed. Three existing tests that open localhost HTTP servers were deliberately deselected.

## Correction and Source Contracts

The previous constructor rejected the already-authorized 16384 response maximum because it required response >= context. Its sample emission also used all remaining context, which could exceed the run's response maximum and be rejected by the existing generation consumer.

The source now consumes the existing native `rollout_max_prompt_len` and `rollout_max_response_len` fields. No custom knob, new default, typed input API, alternate scheduling path or parent integration was introduced.

| Contract | Implementation/evidence |
| --- | --- |
| Context remains caller-owned 131072 | `swe_inputs.py:208,225,294`; all accepted test samples retain `max_seq_len=131072`. |
| Response must be set and positive, not context-sized | `swe_inputs.py:178–179`; the D34 constructor succeeds with 16384. |
| Prompt equality is eligible; excess is skipped without truncation or accepted-slot consumption | `swe_inputs.py:272–291`; 114688 accepted, 114689 rejected, source positions `[0,2,3]` retain accepted indices/group indices `[0,1,2]`. |
| Native optional prompt limit `None` remains supported | `swe_inputs.py:209,272–274`; no prompt-specific rejection when unset. Native `miles/utils/data.py:93–95,131–135` already defines None as no prompt filter and equality as accepted. |
| Per-sample budget is the smaller of response maximum and remaining context | `swe_inputs.py:295`; tested budgets below. No mutation of run-wide sampling parameters. |
| Receipt identifies all three limits and actual rules | `swe_inputs.py:225–233,280–287`; saved receipt and rejection logs asserted through public source operations. |

The original `OnlineTrajectoryTurnSource`/`MaskAwareSWETurnSource` selection, manifest order, source cursor, dataset paths, normalization/rendering, native ground truth, mask policy, visual exclusion verification and dependency identities are unchanged. The change does not introduce the parent's interleaved source or alter experiment science beyond the explicitly authorized lengths.

Read-only inspection of `qwen_alignment.py:86–103` confirmed that it validates prompt identity and forwards the same input to native single-turn generation; it has no response-cap override and was not edited. `inference_rollout_common.py:91,113–118` applies the sample budget before constructing `GenerateFnInput`; `generate_endpoint_utils.py:63–82` rejects sample budgets above the run maximum rather than silently clamping them. That existing consumer is exercised by the new regression.

## Regression Seam and Observed Budgets

The tests reuse the existing `_CharacterTokenizer`, `_fixture_population`, `make_state` and `_RecordingGenerate`. Real `NativeSWEDataSource` construction, rendering, token hashing, `get_samples()`, rejection receipts, `save()` and native `generate_and_rm()` budget application execute without replacements.

The external pinned-loader boundary is represented only by an injected finite sequence of turn dictionaries with deterministic native identities. A verified no-op loader file and placeholder tokenizer/template files satisfy construction's byte-identity reads; they are not production assets. The character tokenizer provides exact boundary lengths, not Qwen length estimates. The tests do not recreate training, Ray or the native loader's conversation/file/epoch implementation.

| Prompt maximum | Response maximum | Input prompt counts | Accepted prompt counts | Accepted response budgets | Rejections |
| --- | --- | --- | --- | --- | --- |
| 114688 | 16384 | 64, 114689, 114688, 128 | 64, 114688, 128 | 16384, 16384, 16384 | 114689; no accepted slot consumed |
| None | 16384 | 114689, 131071, 131072, 64 | 114689, 131071, 64 | 16383, 1, 16384 | 131072; no accepted slot consumed |
| None | 131072 | 114689, 131071, 131072, 64 | 114689, 131071, 64 | 16383, 1, 131008 | 131072; historical remaining-context behavior retained |

Each accepted sample reaches the real budget consumer and the existing recording generator with the expected `max_new_tokens`. The configured short/long D34 prompts never receive more than 16384 response tokens. Context equality remains rejected to avoid a zero generation budget.

## Exact Test Commands and Results

All commands ran from the worktree above. The same focused test was run before and after the source correction; only temporary output paths differ.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/rollout/test_sample_max_response_len.py::test_native_swe_prompt_limit_preserves_slots_and_generation_budget --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/capacity-input-lengths-red
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/rollout/test_sample_max_response_len.py::test_native_swe_prompt_limit_preserves_slots_and_generation_budget --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/capacity-input-lengths-green
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/rollout/test_sample_max_response_len.py tests/fast/rollout/generate_utils/test_generate_endpoint_utils.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/capacity-input-lengths-budget-suite
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/rollout/test_sample_max_response_len.py tests/fast/rollout/generate_utils/test_generate_endpoint_utils.py tests/fast/test_qwen35_sample_lifecycle.py -k 'not test_teacher_and_student_scoring_keep_independent_native_total_timeouts and not test_native_scoring_timeout_preserves_teacher_failure_and_observer_soft_failure' --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/capacity-input-lengths-final-suite
```

| Run | Passing/expected condition | Actual result | Verdict |
| --- | --- | --- | --- |
| New focused regression before fix | Expose the old source restriction, not a fixture/import error | 1 failed, 18 warnings, 3.60 s; `swe_inputs.py:178` raised `ValueError: Native SWE remaining-context generation requires rollout_max_response_len >= rollout_max_context_len` | Expected RED |
| Same focused regression after fix | Accept equality, skip +1, emit contiguous accepted slots and safe consumer budgets | 1 passed, 18 warnings, 2.49 s | PASS |
| Budget/source and payload tests | All new None/remaining-context cases and existing budget/payload checks pass | 26 passed, 18 warnings, 2.78 s | PASS |
| Final affected source/generation tests, after formatting new test code | Preserve sample budgets and Qwen prompt/completion/lifecycle behavior without real networking | 39 passed, 3 deselected, 18 warnings, 2.90 s | PASS |

Warnings were not suppressed: two SWIG import deprecations, fourteen `torch.jit.script_method` deprecations, and existing CPU AWQ/GGUF support warnings; a `swigvarlink` deprecation was also printed at interpreter exit. The complete affected test file remains within the fast CPU budget.

## Lint and Diff Evidence

```bash
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m ruff check --no-cache tests/manual/agent_opd/swe_inputs.py tests/fast/rollout/test_sample_max_response_len.py
BLACK_CACHE_DIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode/black-cache-capacity-input-lengths PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check --diff tests/manual/agent_opd/swe_inputs.py tests/fast/rollout/test_sample_max_response_len.py
BLACK_CACHE_DIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode/black-cache-capacity-input-lengths PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check --diff tests/fast/rollout/test_sample_max_response_len.py
git show HEAD:tests/manual/agent_opd/swe_inputs.py | BLACK_CACHE_DIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode/black-cache-capacity-input-lengths PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check --stdin-filename tests/manual/agent_opd/swe_inputs.py -
BLACK_CACHE_DIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode/black-cache-capacity-input-lengths PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check tests/manual/agent_opd/swe_inputs.py
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m isort --check-only --diff tests/manual/agent_opd/swe_inputs.py tests/fast/rollout/test_sample_max_response_len.py
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import platform
from pathlib import Path
from importlib.metadata import version
from tools.lint_config_attribute_access import _violations
print('Python', platform.python_version())
for name in ('pytest', 'torch', 'sglang'):
    print(name, version(name))
for path in (Path('tests/manual/agent_opd/swe_inputs.py'), Path('tests/fast/rollout/test_sample_max_response_len.py')):
    violations = _violations(path)
    print(path, 'PASS' if not violations else violations)
    assert not violations
PY
git diff --check
```

- Ruff: PASS, `All checks passed!`, including a final recheck. The existing top-level `select`/`ignore` configuration deprecation is unchanged.
- isort: PASS, no output or import-order changes.
- Repository config-attribute checker: PASS for both changed Python files.
- Black initially reported both files. New test formatting was corrected with scoped patches; final test-file check: PASS, unchanged. The source's full-file Black check remains FAIL (`would reformat`), also reproduced on the untouched HEAD version. Its existing unrelated formatting was preserved rather than bulk-reformatted; the changed rejection block uses Black-compatible formatting. This is a recorded baseline limitation, not a claimed lint pass.
- `git diff --check`: PASS, no whitespace errors; changed-file inspection contained only owned code before this report was added.

## Acceptance and Remaining Limits

The isolated CPU source prerequisite is complete: explicit D34 lengths are honored, equality/+1 and contiguous accepted slots are checked, sample budgets reach the existing generation consumer, optional prompt None is supported, and receipt semantics match behavior.

No actual SWE dataset, production Qwen tokenizer, full-source visual receipt, native loader epoch, real HTTP generation, optimizer update, GPU capacity or upstream 256-turn business acceptance was tested. Existing mock-transport Qwen generation tests ran without opening network connections. The excluded tests are one teacher/student total-timeout test and two parametrized native-scoring timeout cases, all using `_scoring_server()` localhost sockets.

The historical manual checker remains outside this ownership: `check_swe_inputs.py:66–76` constructs a namespace without the native prompt field and still uses context-sized response for its historical probe. It was neither edited nor run; adding a fallback for that missing namespace field would invent an unauthorized compatibility/default path. A supported native runtime with `rollout_max_prompt_len=None` is covered directly. Primary-owned updated launch config/records and any checker follow-up are separate deliverables.

This is not parent Ticket02/03 integration, an upstream merge, permission to submit a job, or proof of native H800 capacity acceptance. The completion checkpoint found no D1–D7 execution drift; the only S5 record synchronization is primary-owned and already authorized by the current delegation.
