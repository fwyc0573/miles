## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record the real SWE-hook RED/GREEN, shared response-scoring owner, CPU ABI inspection, expanded regression results and outstanding native acceptance. |

# Teacher sampled-token scoring scope

TaskID: `profile-teacher-scoring-scope-fix-20261111`.

**Result:** the requested API/behavior change is CPU-ready. It is **not accepted as a native performance correction**. The focused suite passes; the expanded suite has four independently reproduced baseline failures outside this change and twelve CUDA skips.

## Request, ownership and acceptance

[Original Request] The delegated correction implements the teacher sampled-token request scope required by [D40](requirements.md#workflowparameter-rca--original-request-2026-11-11), following the [current RCA](test_report_2026-11-11_workflow_rca.md). Its agreed seams are the real `score_teacher` HTTP payload/validation boundary, existing canonical trajectory sealing, student prefill scoring, and the existing full-input/top-k payload contract.

Only these six files belong to this slice:

- `miles/rollout/on_policy_distillation.py`
- `miles/rollout/generate_utils/prefill_logprobs.py`
- `tests/manual/agent_opd/swe_replay.py`
- `tests/fast/test_swe_replay.py`
- `tests/fast/rollout/generate_utils/test_prefill_logprobs.py`
- This report.

No GPU/platform/SSH/network operations, delegation, benchmark-probe edits, configuration changes or edits to the main task records occurred. Existing unrelated modifications are preserved. The primary owns native H800 parity/performance measurements and separate immutable diff artifacts.

Acceptance path: real-hook RED -> central payload correction -> focused CPU regressions -> expanded CPU checks and baseline attribution -> scoped commit -> primary's native H800 parity/performance comparison. CPU completion does not release the formal-run hold.

## Confirmed cause and correction

The old SWE hook called `_score_payload(sample.tokens)`, which fixed `logprob_start_len=0`, then consumed only the response suffix. The requested bank6 context is 24,457,747 input tokens versus 147,115 response tokens; those workload counts are supplied primary evidence, not measured by this CPU slice. They are not a measured speedup or avoided attention-token count.

The real-hook regression now uses `[10, 11, 12, 20, 30]`: three prompt tokens and two response tokens. Its independent expected request start is **2**, not **0** or **3**. The original one-prompt-token fixture could not distinguish full-input and response scope.

`_score_payload` is the sole owner of the start formula. Its new keyword-only `response_length=None` preserves the existing full-input default. For explicit R, it derives P = N - R, requires nonnegative R and at least one prompt token, and starts at P - 1. The SWE hook supplies R; native input IDs, zero-generation sampling settings and request timeout remain unchanged. The optional API argument is not a wire field.

The existing student prefill builder reuses that payload and retains its sampling overrides, LoRA adapter, encoded images and established missing-prompt error message. Batch grouping uses prompt length rather than independently deriving a start; the existing group membership and cache-flush behavior remain unchanged. No student recomputation flag is enabled.

The response is still trimmed with `values[1:][-R:]`. Native regular readout places a placeholder at P - 1 and returns all R response positions after it. Starting at P would put the placeholder on the first response token and discard its probability. No per-position arrays, full-input diagnostics, top-k callers, observer expectations, teacher identity/finite checks, canonical checks, profile soft gates, native counters, timings, candidate ordering, timeouts or TIS behavior changed.

R=0 retains the existing empty trim result. Empty responses are not valid canonical SWE training trajectories (`CanonicalTrajectory.seal` requires a positive response length), and this patch does not add a new zero-response teacher path.

## CPU environment and source ABI

Working directory for every command below:

```text
/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image
```

Executable: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python` (existing environment, no dependency installation).

```text
Python 3.12.13 (main, May 10 2026, 19:30:01) [Clang 22.1.3]
SGLang 0.5.23
torch 2.11.0
pytest 9.1.1
```

Version command:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -c 'import importlib.metadata as m,sys; print(sys.version); print("sglang="+m.version("sglang")); print("torch="+m.version("torch")); print("pytest="+m.version("pytest"))'
```

The inspected source root is `/data/ycfeng/envs/miles-agent-opd-cpu/lib/python3.12/site-packages/sglang/srt/`:

| Source | Relevant observed behavior | SHA256 |
| --- | --- | --- |
| `managers/schedule_batch.py:1766-1785` | Logprob requests cap prefix matching by `logprob_start_len`; start=0 caps it at zero. | `0e66c8af3cd653e7db646f31c02219587afc6c617311b72c4e286307b97e68a7` |
| `layers/logits_processor.py:772-819` | Prunes hidden states by the extended logprob start before logits work. | `5154d547402a84649e625f3eae4e8e5671f4d3fdf0ef2d255b5a60611c1debb5` |
| `managers/scheduler_components/logprob_result_processor.py:26-50` | Regular readout prepends `None`, removes the sampling position, and indexes IDs from `logprob_start_len`. | `a128fc8a3ddd22ee30f14c96fa38db3068fa8fba799f22073f4c8db941111f29` |
| `managers/io_struct.py` | `GenerateReqInput` accepts and normalizes the unchanged native payload fields. | `0518aa62b3d864be6f4d76a7fcf14720a2f5854b557df19ddd8ea717de62cb57` |

Source hashes were captured with:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -c 'from pathlib import Path; import hashlib; root=Path("/data/ycfeng/envs/miles-agent-opd-cpu/lib/python3.12/site-packages/sglang/srt"); paths=["managers/schedule_batch.py", "layers/logits_processor.py", "managers/scheduler_components/logprob_result_processor.py", "managers/io_struct.py"]; print("\n".join(str(root/p)+" sha256="+hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths))'
```

These are local 0.5.23 observations. They do not verify the pinned worker's `0.5.24.dev80+g056f871` implementation, hybrid-attention cache behavior, numerical parity or runtime cost. In particular, removing prompt probability readout does not remove the prompt's necessary attention context; a cold request must still compute its context.

## Exact test commands and outcomes

### Real RED before production edits

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_replay.py -k teacher_request_and_validation_stage_receipts --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/teacher-scoring-scope-red -q
```

Expected failure: the actual SWE hook posts start=0 instead of the required start=2. **Observed RED: 8 failed, 31 deselected, 0.56 seconds, exit 1.** All eight failures show the same payload mismatch:

```text
{'logprob_start_len': 0} != {'logprob_start_len': 2}
tests/fast/test_swe_replay.py:403: AssertionError
```

The eight cases retain success, transport error, cancellation, validation error and receipt-sink failure checks. Their RED is the scoring-scope defect, not an import or fixture failure.

### Initial GREEN

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py -k 'teacher_request_and_validation_stage_receipts or prefill' --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/teacher-scoring-scope-green -q
```

Passing condition: the same real-hook cases use start=2 while existing student prefill behavior remains unchanged. **PASS: 12 passed, 31 deselected, 0.43 seconds, exit 0.**

### Persistent focused regressions

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/teacher-scoring-scope-focused -q
```

**PASS: 102 passed, 14.85 seconds, exit 0.**

Coverage includes P=1/P=3, R=1/multiple responses, placeholder+R request/readout expectations, actual teacher postprocessing and canonical sealing, mismatched/missing first score, missing field, nonfinite teacher score, zero-response trimming, supported invalid-length/missing-prompt errors, student alignment/None-score errors, request sampling retention without mutation, fixed/disk/train-only LoRA routing, image RGB PNG encoding, existing batching, and unchanged full/default/top-k/per-position behavior. Existing tests were extended rather than copied to new test files.

### Expanded affected regression set

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_replay.py tests/fast/test_swe_tis.py tests/fast/test_swe_turn_sums.py tests/fast/test_swe_profile_integration.py tests/fast/test_distillation_profile.py tests/fast/test_swe_capacity.py tests/fast/test_swe_native_gradients.py tests/fast/test_qwen35_sample_lifecycle.py tests/fast/test_qwen35_opd_launcher.py tests/fast/test_qwen35_monitoring.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/teacher-scoring-scope-regression -q
```

**PARTIAL: 351 passed, 4 failed, 12 skipped, 149.51 seconds, exit 1.** The skips are actual local CUDA-dependent skips, not native evidence. No skip count of twenty is claimed. All new scoped tests pass, as do the existing full-prompt lifecycle, nested teacher diagnostics, monitoring, TIS, native counter and soft-profile checks. The complete command is not labeled PASS.

Unchanged failing tests:

| Test | Actual failure |
| --- | --- |
| `tests/fast/test_swe_capacity.py::test_combined_native_hook_registration_uses_real_generated_arguments` | `run_swe_opd.py:96`, `KeyError: 'steptron_root'` in historical configuration. |
| `tests/fast/test_swe_native_gradients.py::test_combined_native_hook_cli_registration_from_generated_argv` | Same missing historical input key. |
| `tests/fast/test_swe_native_gradients.py::test_configuration_uses_existing_flag_carrier_without_recipe_edits` | Same missing historical input key. |
| `tests/fast/test_qwen35_opd_launcher.py::test_native_parser_accepts_sglang_and_custom_mis_flags` | `test_qwen35_opd_launcher.py:183`; local parser leaves `--sglang-enable-prefill-weight-versions` unknown. |

### Original-production baseline attribution

The same four tests were rerun with the three original production modules loaded directly from immutable commit `b8541ec86f975c197ac65df203e716bb95dd718d` into memory. No worktree files were reverted or overwritten. The failing test files, launcher and historical configurations were not edited.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python - <<'PY'
import importlib
import subprocess
import pytest

base = 'b8541ec86f975c197ac65df203e716bb95dd718d'
for name, path in [
    ('miles.rollout.on_policy_distillation', 'miles/rollout/on_policy_distillation.py'),
    ('miles.rollout.generate_utils.prefill_logprobs', 'miles/rollout/generate_utils/prefill_logprobs.py'),
    ('tests.manual.agent_opd.swe_replay', 'tests/manual/agent_opd/swe_replay.py'),
]:
    module = importlib.import_module(name)
    original = subprocess.check_output(['git', 'show', f'{base}:{path}'], text=True)
    exec(compile(original, f'{base}:{path}', 'exec'), module.__dict__)
    print(f'BASELINE loaded {base}:{path}', flush=True)
raise SystemExit(pytest.main([
    '-q', '--tb=short', '--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/teacher-scoring-scope-baseline',
    'tests/fast/test_swe_capacity.py::test_combined_native_hook_registration_uses_real_generated_arguments',
    'tests/fast/test_swe_native_gradients.py::test_combined_native_hook_cli_registration_from_generated_argv',
    'tests/fast/test_swe_native_gradients.py::test_configuration_uses_existing_flag_carrier_without_recipe_edits',
    'tests/fast/test_qwen35_opd_launcher.py::test_native_parser_accepts_sglang_and_custom_mis_flags',
]))
PY
```

**Observed: the identical 4 failures, 2.86 seconds, exit 1.** This confirms their baseline status for this correction. No parser assertion, unrelated fixture or production launcher was changed to make the suite appear green.

### Direct local native-schema and regular-readout check

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python - <<'PY'
from types import SimpleNamespace
from sglang.srt.managers.io_struct import GenerateReqInput
from sglang.srt.managers.scheduler_components.logprob_result_processor import SchedulerLogprobResultProcessor
from miles.rollout.on_policy_distillation import _score_payload, _trim_input_field

processor = SchedulerLogprobResultProcessor(model_config=SimpleNamespace(vocab_size=100))
for tokens, response_length, expected_start, native_values, expected in [
    ([10, 20], 1, 0, [-1.0, -9.0], [[None, 10], [-1.0, 20]]),
    ([10, 20, 30], 2, 0, [-1.0, -2.0, -9.0], [[None, 10], [-1.0, 20], [-2.0, 30]]),
    ([10, 11, 12, 20], 1, 2, [-1.0, -9.0], [[None, 12], [-1.0, 20]]),
    ([10, 11, 12, 20, 30], 2, 2, [-1.0, -2.0, -9.0], [[None, 12], [-1.0, 20], [-2.0, 30]]),
]:
    payload = _score_payload(tokens, response_length=response_length)
    parsed = GenerateReqInput(**payload)
    parsed.normalize_batch_and_arguments()
    assert parsed.logprob_start_len == expected_start
    req = SimpleNamespace(origin_input_ids=tokens, logprob_start_len=expected_start,
                          is_prefill_only=False, logprob=SimpleNamespace())
    processor._process_input_token_logprobs(req, native_values)
    returned = [list(item) for item in zip(req.logprob.input_token_logprobs_val, req.logprob.input_token_logprobs_idx, strict=True)]
    assert returned == expected, (returned, expected)
    trimmed = _trim_input_field({'input_token_logprobs': returned}, 'input_token_logprobs', response_length)
    assert trimmed == expected[1:]
    print(f'PASS SGLang 0.5.23 CPU schema/readout N={len(tokens)} R={response_length} start={expected_start} items={len(returned)} ids={[item[1] for item in trimmed]}')
PY
```

**PASS: four schema/readout cases** with `(N,R,start,items)` = `(2,1,0,2)`, `(3,2,0,3)`, `(4,1,2,2)`, `(5,2,2,3)`. This invokes the installed regular-readout method with supplied probabilities, not a model forward or service. The minimal request stub uses `is_prefill_only=False` to select regular readout without initializing the serving runtime; it does not exercise MIS/setwise runtime selection. CUDA/vLLM import warnings are retained as environment limitations, not suppressed.

### Static checks

```bash
git diff --check -- miles/rollout/on_policy_distillation.py miles/rollout/generate_utils/prefill_logprobs.py tests/manual/agent_opd/swe_replay.py tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m ruff check miles/rollout/on_policy_distillation.py miles/rollout/generate_utils/prefill_logprobs.py tests/manual/agent_opd/swe_replay.py tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py
```

Diff whitespace check **PASS**, exit 0. Ruff **UNAVAILABLE**, exit 1: `No module named ruff`. No installation or unrelated formatting was attempted.

The report's embedded production diff and five original/revised hash pairs were checked directly against Git and the actual files before staging:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python - <<'PY'
from pathlib import Path
import re
import hashlib
import subprocess
report_path = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_teacher_scoring_scope.md')
report = report_path.read_text()
production = ['miles/rollout/generate_utils/prefill_logprobs.py', 'miles/rollout/on_policy_distillation.py', 'tests/manual/agent_opd/swe_replay.py']
retained = report.split('```diff\n', 1)[1].split('\n```', 1)[0] + '\n'
actual = subprocess.check_output(['git', 'diff', 'b8541ec86f975c197ac65df203e716bb95dd718d', '--', *production], text=True).replace('\n \n', '\n\n')
assert retained == actual, 'Retained production diff differs from actual diff'
for path, original_sha, revised_sha in re.findall(r'\| `([^`]+\.py)` \| `([a-f0-9]{64})` \| `([a-f0-9]{64})` \|', report):
    original = subprocess.check_output(['git', 'show', f'b8541ec86f975c197ac65df203e716bb95dd718d:{path}'])
    assert hashlib.sha256(original).hexdigest() == original_sha
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == revised_sha
print('PASS retained production diff and five original/revised SHA256 pairs')
PY
```

**PASS**, exit 0. The index was empty before staging this slice. The first staged whitespace check identified five single-space blank context lines inside the embedded diff; they are rendered as empty lines below rather than retained as Markdown trailing whitespace. No production code changed. The corrected final staged whitespace check passed.

## Immutable original/revised production diff

Original source: commit `b8541ec86f975c197ac65df203e716bb95dd718d`. The following captured production diff is retained in this owned report only; blank context lines are rendered empty to avoid Markdown trailing whitespace. Source hashes preserve byte-exact original/revised identities. No additional diff artifact was written by this slice.

```diff
diff --git a/miles/rollout/generate_utils/prefill_logprobs.py b/miles/rollout/generate_utils/prefill_logprobs.py
index 1b12f938..88b7cb17 100644
--- a/miles/rollout/generate_utils/prefill_logprobs.py
+++ b/miles/rollout/generate_utils/prefill_logprobs.py
@@ -5,6 +5,7 @@ from collections.abc import Mapping
 from typing import Any

 from miles.rollout.generate_utils.generate_endpoint_utils import compute_routing_headers, router_routes_by_key
+from miles.rollout.on_policy_distillation import _score_payload
 from miles.utils.http_utils import post
 from miles.utils.lora.utils import LORA_ADAPTER_NAME, lora_rollout_enabled
 from miles.utils.processing_utils import encode_image_for_rollout_engine
@@ -23,27 +24,16 @@ def _build_prefill_scoring_payload(
     sample: Sample,
     sampling_params: Mapping[str, Any],
 ) -> dict[str, Any]:
-    prompt_len = len(sample.tokens) - sample.response_length
-    if prompt_len <= 0:
+    try:
+        payload = _score_payload(sample.tokens, response_length=sample.response_length)
+    except ValueError as error:
         raise ValueError(
             "Cannot recompute rollout logprobs via prefill without at least one prompt token: "
             f"tokens={len(sample.tokens)}, response_length={sample.response_length}"
-        )
+        ) from error

-    payload = {
-        "input_ids": sample.tokens,
-        "sampling_params": {
-            **dict(sampling_params),
-            "max_new_tokens": 0,
-            "temperature": 0,
-            "skip_special_tokens": False,
-        },
-        "return_logprob": True,
-        # SGLang returns input_token_logprobs aligned to tokens from logprob_start_len,
-        # with the first value None. Start one token before the response so the
-        # returned tail contains every response-token logprob.
-        "logprob_start_len": prompt_len - 1,
-    }
+    # Preserve request sampling options, but scoring overrides generation settings.
+    payload["sampling_params"] = {**dict(sampling_params), **payload["sampling_params"]}

     if (lora_path := _lora_path_for_sample(args, sample)) is not None:
         payload["lora_path"] = lora_path
@@ -150,11 +140,11 @@ async def recompute_samples_rollout_logprobs_via_prefill(
     flush_url = url.rsplit("/", 1)[0] + "/flush_cache"

     if _can_batch_prefill_score(args, samples_to_score):
-        # A batch must share one logprob_start_len and one lora_path, so group by both.
+        # Equal prompt lengths share a logprob_start_len; adapters must also match.
         samples_by_batch_key: dict[tuple[int, str | None], list[Sample]] = defaultdict(list)
         for sample in samples_to_score:
             prompt_len = len(sample.tokens) - sample.response_length
-            samples_by_batch_key[(prompt_len - 1, _lora_path_for_sample(args, sample))].append(sample)
+            samples_by_batch_key[(prompt_len, _lora_path_for_sample(args, sample))].append(sample)

         for batch_samples in samples_by_batch_key.values():
             # SGLang can serve scoring requests from radix/KV cache. Flush before
diff --git a/miles/rollout/on_policy_distillation.py b/miles/rollout/on_policy_distillation.py
index a18b3c9c..3ee1a0c3 100644
--- a/miles/rollout/on_policy_distillation.py
+++ b/miles/rollout/on_policy_distillation.py
@@ -98,7 +98,20 @@ def _score_payload(
     token_ids: list[int] | None = None,
     token_ids_positions: list[list[int]] | None = None,
     extra_key: str | None = None,
+    *,
+    response_length: int | None = None,
 ) -> dict[str, Any]:
+    logprob_start_len = 0
+    if response_length is not None:
+        prompt_len = len(input_ids) - response_length
+        if response_length < 0 or prompt_len <= 0:
+            raise ValueError(
+                "Response scoring requires a nonnegative response_length and at least one prompt token: "
+                f"tokens={len(input_ids)}, response_length={response_length}"
+            )
+        # The first returned input position is a placeholder. Include the last
+        # prompt token so every response token, including the first, has a score.
+        logprob_start_len = prompt_len - 1
     payload = {
         "input_ids": input_ids,
         "sampling_params": {
@@ -107,7 +120,7 @@ def _score_payload(
             "skip_special_tokens": False,
         },
         "return_logprob": True,
-        "logprob_start_len": 0,
+        "logprob_start_len": logprob_start_len,
     }
     if top_k > 0:
         payload["top_logprobs_num"] = top_k
diff --git a/tests/manual/agent_opd/swe_replay.py b/tests/manual/agent_opd/swe_replay.py
index 44ea23dc..bc26290a 100644
--- a/tests/manual/agent_opd/swe_replay.py
+++ b/tests/manual/agent_opd/swe_replay.py
@@ -285,7 +285,9 @@ async def score_teacher(args, sample, **kwargs):
     deadlines = [value for value in (acquisition_deadline, time.time() + timeout if timeout is not None else None) if value is not None]
     request_deadline = min(deadlines) if deadlines else None
     with _teacher_stage(args, sample, "teacher_request", deadline_at=request_deadline):
-        response = await opd._post_json(args.rm_url, opd._score_payload(sample.tokens), timeout_secs=timeout)
+        response = await opd._post_json(
+            args.rm_url, opd._score_payload(sample.tokens, response_length=sample.response_length), timeout_secs=timeout,
+        )
     with _teacher_stage(args, sample, "teacher_validation", deadline_at=acquisition_deadline):
         scores = opd._trim_input_field(response["meta_info"], "input_token_logprobs", sample.response_length)
         if [item[1] for item in scores] != sample.tokens[-sample.response_length:]:
```

| File | Original SHA256 | Revised SHA256 |
| --- | --- | --- |
| `miles/rollout/on_policy_distillation.py` | `72e2f59054b07cb258c4b6e0f89d6b8d9b9ae15c31accdd0dd2565883d11ada0` | `42e1055fce349e30f2a52d37fa56388102ccc9b46d7ea6d37f087a85d91f82ef` |
| `miles/rollout/generate_utils/prefill_logprobs.py` | `e2d01e6607a9e590c88c43191c5277bcd505b9443d8f95e09bbf92780c7a9298` | `271a07f2ee459bb82d65b94596e79d252d2ea4ab31f03baf948326f340c7e62e` |
| `tests/manual/agent_opd/swe_replay.py` | `7473336d1b21db1a0696a7f1bbb22b9ba074b38e4d5121edee99f6b36724ecb3` | `2ec0834f5eba14d6cac64ed3ce923be4a1369409e659af82115e9327824fa97d` |
| `tests/fast/test_swe_replay.py` | `e00fb25a0e6e6e83ad2164e30cfcc2c22ee41b1af7f9ed608b35e56c4e5eb1f4` | `4c0cb22737cd3181a30ab496d87e4db554e6c9ea081f8b2adec710780e7e21bd` |
| `tests/fast/rollout/generate_utils/test_prefill_logprobs.py` | `55f9872f5211c1ec638559cbce85b71f677ead661c7b7d60b1cf3fbd13b2cd21` | `765e258d32e4050c36ebf19cc6f65c15cf006d9ac381ced880b22872cd97a7e3` |

## Required native payload and remaining limits

For each retained fixture, the primary compares the same teacher checkpoint and full token sequence using:

```json
{
  "input_ids": [10, 11, 12, 20, 30],
  "sampling_params": {"temperature": 0, "max_new_tokens": 0, "skip_special_tokens": false},
  "return_logprob": true,
  "logprob_start_len": 2
}
```

The original request differs only in `logprob_start_len=0`. The revised regular response must have the last prompt token's placeholder followed by exactly R matching response IDs and finite probabilities; the first response probability must not be missing. The actual worker's ABI/source must be inspected, and probability differences must be measured on every required response position. Cold and same-prefix warm conditions need separate cache evidence. Required observations include actual scored positions/returned bytes, request and parse time, native prefill/cache counters and GPU execution/queue attribution. No numerical tolerance, speedup, capacity result or native acceptance is invented here.

The four baseline failures and unavailable Ruff remain recorded, not repaired in this slice. A clean whole-expanded-suite result is not claimed. No selected transient log or additional supporting artifact was written outside this report by this slice.

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 2｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 真实 SWE hook RED | PASS | 既有八项用例真实收到 start=0，独立预期为2。 |
| 共享 payload 与 focused CPU | PASS | 三个 production 文件完成；102 PASS。 |
| 扩展 CPU 与 baseline 归因 | PASS | 351 PASS；原始 production 再现同四项 baseline FAIL。 |
| 完整扩展 suite 全绿 | FAILED | 四项非本范围 baseline failure，未改断言或 fixture。 |
| H800 native 概率/性能接受 | BLOCKED | Primary 独占；本 slice 无 GPU 权限或实测。 |
| 六文件 scoped commit | TODO | 需提交本报告及五个已验证文件；commit 本身不代替 native 接受。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本 slice 开始至已完成 focused/扩展 CPU/baseline 归因｜**当前前沿：** scoped commit，primary native 验证。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 扩展检查按委派要求执行；baseline 归因只复测四项，未扩建工具。 |
| D2 细节反复重试 | CLEAR | 一次生产修正转绿；四项 baseline 用 immutable originals 定向证伪。 |
| D3 支线问题修补 | CLEAR | 未修历史 config/parser 或安装 Ruff。 |
| D4 可并行任务停滞 | CLEAR | 主会话独占 native；本 slice 禁止 GPU/代理操作，CPU 与 source 读取并行。 |
| D5 超范围镀金 | CLEAR | 仅六文件，无新 flag、重算模式、fallback、observer 改动。 |
| D6 分析空转 | CLEAR | 实际 RED、修改、GREEN、baseline 归因均有输出。 |
| D7 路线违背 | CLEAR | full/top-k 默认及固定 science/soft gates 保留，不绕过 native hold。 |

**文档检查：** S1-S4/S6 在本 scoped 路径未发现明显缺陷。S5：读取时 `spec.md` S0 仍写 H800_PREPARATION，而 `requirements.md` 当前 phase、`plan.md` 与 tickets04/05 已写 D40 WORKFLOW_RCA/formal hold；本 slice 依最新明确请求执行，未按旧 phase 启动。
**归因：** 无执行D命中；S5 是 primary-owned 主文档状态，不能由本 slice 越权编辑。

## 3. 纠正建议

**分支：** B：主文档有局部旧状态，本 slice 不改变 agreed scope。

**文档更新（先执行）：**
1. Primary-owned `spec.md` S0 当前状态：与已批准 D40/formal hold 同步（可直接执行，由主会话/文档 owner 处理；不阻塞本独立 CPU commit）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 提交本 slice 六文件 → 完成标志：commit 仅含指定文件及所记录 CPU 证据。
2. Primary 并行继续历史实际配置比较与 H800 native 验证 → 完成标志：same-input response 概率/ID 一致性和实际减少开销的证据；CPU PASS 不替代该结论。

## 4. 最值得关注的 3 点

1. P-1 必须保留首个 response 概率；本地 regular ABI 与 canonical 测试通过，worker ABI 仍需检查。
2. 351 PASS 不等于完整 suite PASS；四项相同 baseline failure 与12 CUDA skip 均明确保留。
3. 本改变仅 CPU-ready；native parity/performance 未接受，正式A/B hold 不解除。
