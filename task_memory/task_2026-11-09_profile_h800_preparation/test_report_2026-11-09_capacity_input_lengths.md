## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record the isolated D34 source correction, RED/GREEN evidence, CPU consumer checks and limits. |
| 2026-11-09 | Extend the existing parity checker with optional native limits, accepted-factory/request verification and original-source worker invocation. |

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

At source commit `82915613`, the historical manual checker remained outside this ownership and still used context-sized response. It was neither edited nor run in that initial slice. The explicitly authorized follow-up below resolves that limitation through the checker's existing CLI and preserves its historical omission semantics; it does not add a production compatibility path.

This is not parent Ticket02/03 integration, an upstream merge, permission to submit a job, or proof of native H800 capacity acceptance. The completion checkpoint found no D1–D7 execution drift; the only S5 record synchronization is primary-owned and already authorized by the current delegation.

## Authorized Checker Follow-up

The same task ID continues from `82915613`. Ownership is now only `tests/manual/agent_opd/check_swe_inputs.py` and this existing report. The primary's uncommitted `rollout_max_prompt_len=None` addition in `_args` was incorporated, not reverted. Its config, preflight scripts, requirements/plan and genuine in-place receipts remain untouched. No persistent test file or new tool was added.

The checker now accepts optional `--rollout-max-prompt-len` and `--rollout-max-response-len`. The parser retains None for omitted options; `_args` forwards the prompt limit and resolves only an omitted checker response maximum to its historical context-sized value. Explicit D34 values remain independent. Non-positive CLI lengths fail before any source read; no prompt/response sum constraint is imposed on historical remaining-context probes.

Prefix eligibility and recorded budgets use those resolved limits. The existing native oracle skips rejected prefixes before selecting the next expected accepted turn, preserving full history/ground-truth equality, accepted slot continuity, conversation/file ordering and epoch checks when the prompt cap causes additional skips. The original fixed sequence assertions remain for the no-length-rejection case. The small context-boundary fault-injection fixture explicitly leaves its prompt cap unset so its original context-equality rejection remains a context check, not a contradiction of prompt equality acceptance.

The ordinary factory still uses `RolloutConfig -> compute_custom_function_config -> load_function -> NativeSWEDataSource`, including genuine visual-filter validation. It now verifies the accepted prompt count/hash, configured context, sample response budget, real `apply_sample_max_response_len()` merge and real `compute_request_payload()` result. Its receipt records resolved length limits, accepted source UID/slot, request prompt count/hash and actual request `max_new_tokens`. `native_request_payload_constructed=true` and `native_request_sent=false` distinguish payload validation from HTTP generation.

### Follow-up Verification

No original posttrain data or production tokenizer was read locally. The only local native code loaded was the already-pinned CPU loader/converter used by the existing checker fixtures. Small synthetic JSON fixtures were generated by its existing `_length_rejection_check` and `_fixture_population`; no real dataset copy was created.

| Check | Observed result | Verdict/limit |
| --- | --- | --- |
| Existing checker-related fast tests | 19 passed, 18 existing warnings, 2.73 s | PASS; reuses `_CharacterTokenizer` and `_fixture_population` |
| Actual CLI `--help` | Both optional native length flags appear with omission semantics | PASS; no source/platform read |
| Resolved args and exact budget examples | Historical `(131072,None,131072)`; D34 `(131072,114688,16384)`; equality 114688 -> 16384, +1 -> rejection; unset prompt 131071 -> 1 | PASS |
| Existing native mask-aware context/equality fixture | Two overlength turns skipped; accepted source positions `[0,3]`, accepted slots `[0,1]`; context equality rejected | PASS with actual pinned native CPU loader |
| Existing native conversation/file/epoch fixtures | None and 114688 prompt caps: zero length skips; 128 cap: two length skips; full-history, ground-truth, slot and epoch assertions pass | PASS with synthetic fixtures and character tokenizer |
| Ordinary registry factory and native payload | Both historical and D34 factory/payload checks pass; accepted prompt count 54, historical request 131018, D34 request 16384; slot 0 | PASS with only external tokenizer loading substituted by `_CharacterTokenizer`; actual native loader, factory, source/filter and payload construction execute |
| Existing ordered-file/EOF fixture | Two ordered files, matching first accepted UID, wrap epoch 1 | PASS with synthetic fixtures |
| Compile/config-access/diff | Compile and repository config-access checker pass; scoped diff checks pass | PASS |
| Full Ruff checker lint | Exactly one B905 at unchanged `zip(signatures, rows)` | Baseline limitation: reproduced on untouched HEAD at line 363; current position shifted to line 398 before final formatting. No cosmetic fix or suppression. |

CLI and pytest commands, from the same worktree and interpreter as the initial slice:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.check_swe_inputs --help
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/rollout/test_sample_max_response_len.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/capacity-input-checker-fixtures
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m ruff check --no-cache tests/manual/agent_opd/check_swe_inputs.py
git show HEAD:tests/manual/agent_opd/check_swe_inputs.py | PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m ruff check --no-cache --stdin-filename tests/manual/agent_opd/check_swe_inputs.py -
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
from pathlib import Path
from tools.lint_config_attribute_access import _violations
path = Path('tests/manual/agent_opd/check_swe_inputs.py')
compile(path.read_text(), str(path), 'exec')
issues = _violations(path)
print('Compile: PASS')
print('Config access:', 'PASS' if not issues else issues)
assert not issues
PY
git diff --check -- tests/manual/agent_opd/check_swe_inputs.py task_memory/task_2026-11-09_profile_h800_preparation/test_report_2026-11-09_capacity_input_lengths.md
```

Exact direct existing-fixture checks:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import copy
import json
import uuid
from pathlib import Path
from types import SimpleNamespace
from tests.manual.agent_opd import check_swe_inputs as check

root = Path('/data/ycfeng/tmp/opencode-v2-tmp/opencode') / ('capacity-input-checker-direct-' + uuid.uuid4().hex)
root.mkdir()
for name in ('tokenizer.json', 'tokenizer_config.json', 'template.jinja'):
    (root / name).write_text('fixture')
args = SimpleNamespace(
    source_root=root, source_manifest=root / 'COPY_COMPLETE.json',
    native_loader=Path('/data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/users/cj/opd/s4_swe_turn_data_1001.py'),
    native_loader_sha256='8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980',
    native_recipe=Path('/data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/baseline_new/mopd/turn_5teachers_data.py'),
    skip_masked_assistant_turns=True, visual_filter_receipt=None,
    tokenizer=root, chat_template=root / 'template.jinja', rollout_max_context_len=131072,
    rollout_max_prompt_len=None, rollout_max_response_len=None,
    temporary_root=root, evidence_prefix='checker-fixture',
)
historical = check._args(args)
assert historical.rollout_max_prompt_len is None
assert historical.rollout_max_response_len == 131072
args.rollout_max_prompt_len, args.rollout_max_response_len = 114688, 16384
config = check._args(args)
assert (config.rollout_max_context_len, config.rollout_max_prompt_len, config.rollout_max_response_len) == (131072, 114688, 16384)
assert [check._prompt_budget(config, count) for count in (64, 114688, 114689, 131072)] == [16384, 16384, None, None]
config.rollout_max_prompt_len = None
assert [check._prompt_budget(config, count) for count in (114689, 131071, 131072)] == [16383, 1, None]
print('PASS checker historical/D34 length resolution and exact prompt/response boundaries')
native = check.load_swe_native_module(check._args(args))
converter = check._native_converter(args.native_recipe)
length = check._length_rejection_check(args, native)
assert length['status'] == 'PASS' and length['overlength_turns_skipped'] == 2
print('PASS existing native mask-aware context/equality rejection fixture', json.dumps(length))
conversations = json.loads((root / 'checker-fixture-length' / 'part0.json').read_text())
for limit in (None, 114688, 128):
    selected = copy.copy(args)
    selected.rollout_max_prompt_len = limit
    selected.evidence_prefix = 'checker-boundary-' + str(limit)
    boundaries = check._boundary_checks(selected, native, check._CharacterTokenizer(), converter, conversations)
    assert boundaries['status'] == 'PASS'
    if limit == 128:
        assert boundaries['overlength_turns_skipped'] > 0
    print('PASS existing native conversation/file/epoch fixtures', limit, boundaries['overlength_turns_skipped'])
print('Fixture root:', root)
PY
```

The recorded fixture root is `/data/ycfeng/tmp/opencode-v2-tmp/opencode/capacity-input-checker-direct-c99f9b1c87294ac5b267dcd5f2161d77`. The next command reused that generated synthetic fixture, not real SWE data:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import copy
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from tests.manual.agent_opd import check_swe_inputs as check, swe_inputs

root = Path('/data/ycfeng/tmp/opencode-v2-tmp/opencode/capacity-input-checker-direct-c99f9b1c87294ac5b267dcd5f2161d77')
args = SimpleNamespace(
    source_root=root, source_manifest=root / 'COPY_COMPLETE.json',
    native_loader=Path('/data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/users/cj/opd/s4_swe_turn_data_1001.py'),
    native_loader_sha256='8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980',
    native_recipe=Path('/data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/baseline_new/mopd/turn_5teachers_data.py'),
    skip_masked_assistant_turns=True, visual_filter_receipt=None,
    tokenizer=root, chat_template=root / 'template.jinja', rollout_max_context_len=131072,
    rollout_max_prompt_len=114688, rollout_max_response_len=16384,
    temporary_root=root, evidence_prefix='checker-factory',
)
native = check.load_swe_native_module(check._args(args))
conversations = json.loads((root / 'checker-fixture-length' / 'part0.json').read_text())
for prompt, response in ((None, None), (114688, 16384)):
    selected = copy.copy(args)
    selected.rollout_max_prompt_len, selected.rollout_max_response_len = prompt, response
    selected.evidence_prefix = 'checker-factory-' + str(prompt)
    with patch.object(swe_inputs, 'load_tokenizer', return_value=check._CharacterTokenizer()):
        result = check._configuration_check(selected, native, conversations)
    assert result['status'] == 'PASS'
    assert result['uses_actual_custom_function_config_merge']
    assert result['native_request_payload_constructed'] and not result['native_request_sent']
    assert result['rollout_length_limits']['rollout_max_prompt_len'] == prompt
    assert result['rollout_length_limits']['rollout_max_response_len'] == (131072 if response is None else response)
    if response == 16384:
        assert result['native_request_max_new_tokens'] == 16384
    print('PASS existing ordinary factory and native payload with fixture tokenizer', json.dumps(result))
population = check._fixture_population(root / 'checker-file-boundaries', [conversations, conversations], masked=True)
result = check._actual_file_boundaries(args, native, population, check._CharacterTokenizer())
assert result['status'] == 'PASS' and len(result['ordered_files']) == 2
print('PASS existing native actual-file/EOF fixture', json.dumps(result))
PY
```

### Original-Source D34 Worker Invocation — Not Executed by This Subagent

Run from `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity` inside the primary-owned worker with its existing local NFS, posttrain and codesign mounts. Paths and lengths come from primary-owned `h800_capacity_config.json`; the pinned converter and selected parity ordinals retain the historical SWE1003 checker invocation. No old model-source receipt is substituted.

```bash
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.check_swe_inputs \
  --source-root /mnt/posttrain/hanqi/swe_data/sft/datapipe_stage2_rft_0913/mnt/posttrain/qidi/garble_filtered_sft_20260913 \
  --source-manifest /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/source-audit-20261109/swe1003-source-manifest.json \
  --native-loader /data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/users/cj/opd/s4_swe_turn_data_1001.py \
  --native-loader-sha256 8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980 \
  --native-recipe /data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/baseline_new/mopd/turn_5teachers_data.py \
  --tokenizer /mnt/codesign-exp/ycfeng/opd-assets/models/Qwen/Qwen3.5-4B/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a \
  --chat-template /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity/miles/utils/chat_template_utils/templates/qwen3.5_fixed.jinja \
  --rollout-max-context-len 131072 --rollout-max-prompt-len 114688 --rollout-max-response-len 16384 \
  --turn-ordinals 1,2,8,32,64,last --file-last-prefixes 1,4,6 \
  --skip-masked-assistant-turns --evidence-prefix h800-d34-input \
  --visual-filter-receipt /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity/task_memory/task_2026-11-09_profile_h800_preparation/evidence/native-visual-in-place/filter.json \
  --temporary-root /var/tmp/h800-capacity-input-parity-d34 \
  --output-root /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity/task_memory/task_2026-11-09_profile_h800_preparation/evidence/native-inputs-in-place-d34
```

Expected worker evidence: `h800-d34-input-parity.json` status PASS; configuration limits 131072/114688/16384; accepted request budget <=16384 and consistent with remaining context; real request prompt hash/count and accepted UID/slot; saved `h800-d34-input-config.json` with original posttrain paths, the genuine in-place filter reference, `visual_filter_verified=true` and `native_source_injected_for_test=false`. The checker constructs payloads but intentionally does not send HTTP requests.

Primary-owned original-source/Qwen parity remains pending this invocation. Local fixture success does not verify the original data, genuine full-source receipt on the current worker, production tokenizer, remote mounts, generation, GPU capacity, parent integration or upstream acceptance. No platform/auth/cloud/network/GPU operation was performed, and no GPU wait or submission is needed for this handoff. The follow-up checkpoint found D1–D7 CLEAR; the implementation/fixture deliverable is complete and remaining native evidence is primary-owned.
