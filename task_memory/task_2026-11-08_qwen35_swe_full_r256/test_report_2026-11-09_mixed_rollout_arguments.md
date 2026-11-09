## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Reproduce the production colocated rollout-count overwrite, implement missing-only defaulting, and record native CPU parsing, regression results, and GPU verification limits. |

# Mixed rollout argument validation

Task ID: **T02-D13-MIXED-ARGS**. Session ID: `ses_e41449368ffe60SW5yDWEPstjQ` (observed in `OPENCODE_SESSION_ID`). Branch: `agent-opd`. Parent owns final acceptance, launcher/rule changes, GPU/platform/auth/network operations, task progress, and commits.

## Outcome and scope

The actual production validation chain previously overwrote an explicit `--rollout-num-gpus 16` with the eight-GPU training span under `--colocate`. Native SGLang config parsing then rejected two eight-GPU server pools. The minimal fix preserves any explicit rollout count and defaults only `None` to the training GPU count.

The selected parent experiment is an isolated A/r256 capacity smoke: 18 H200 total, trainer8 TP2/DP4/CP1, rollout16 (8 shared + 8 dedicated), teacher2, eight TP2 engines with concurrency1. This report verifies the shared argument/configuration seam, **not** the Megatron training parallelism or that GPU experiment. No scientific setting, timeout, sampling budget, retry behavior, launcher, or formal profile changed here.

| Deliverable | Exact location | Observed result |
| --- | --- | --- |
| Missing-only colocated default | `miles/utils/arguments.py:1507-1513` | Explicit16 survives; omitted count defaults to trainer8; no new flag or branch by platform/model. |
| Production parser regression | `tests/fast/backends/sglang_utils/test_sglang_config.py:421-508` | Six cases use the existing `parse_fsdp_test_config` fixture, which calls real production `parse_args`. |
| Exact code/test diff | `evidence/t02-d13-mixed-args.diff` | Only the owned production file and existing config test file change; no new fixture/wrapper. |
| Progress checkpoint | `evidence/t02-d13-mixed-args-checkpoint.md` | Scoped handoff; native GPU acceptance remains parent-owned. |

The seam was explicitly requested in the delegation: actual `miles_validate_args` followed by native `SglangConfig.parse_args`. The existing CPU fixture drives `parse_args` → `parse_args_and_get_parser` → `miles_validate_args` → SGLang validation → `SglangConfig.parse_args` → validated `AllConfig`. The test does not call only `SglangConfig.resolve`, construct a hand-written Namespace, or mock the overwrite or parser. FSDP supplies the CPU-importable backend defaults; the shared overwrite is the same production code exercised by Megatron launches.

## Environment

- Working directory: `/data/ycfeng/sota-engine/miles`.
- Interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13; no conda activation.
- pytest9.1.1, SGLang0.5.23, Torch2.11.0+cu130. This environment has no Megatron or TransformerEngine package.
- Existing lint packages: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages`; Black24.3.0, isort5.13.2, Ruff0.14.7.
- Tests set Hugging Face/Transformers offline mode, disable bytecode/cache writes, and place temporary files under `/data/ycfeng/tmp/opencode-v2-tmp/opencode`. No dependency installation, network operation, GPU inspection, platform/auth operation, or cloud write occurred.

## RED: actual production failure

Run before changing production code:

```bash
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/backends/sglang_utils/test_sglang_config.py::TestValidatedRolloutGpuCount::test_explicit_colocated_rollout_gpus_support_shared_and_dedicated_engines -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-mixed-args-red --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-mixed-args-red.xml > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-mixed-args-red.log 2>&1
```

Expected discriminator: real Miles validation rewrites16→8, then native YAML parsing rejects16≠8. Actual: **1 failed,2 warnings,0.57s,exit1**. This is a reproduced production bug, not an unsupported proposed API or dependency/import failure.

Decisive captured production output:

```text
arguments.py:1508 - rollout_num_gpus 16 != actor_num_gpus_per_node 8 * actor_num_nodes 1, overriding rollout_num_gpus to match actor_num_gpus_per_node * actor_num_nodes.
AssertionError: sglang_config total GPUs (16) != rollout_num_gpus + eval_num_gpus (8)
```

The error occurs at `miles/backends/sglang_utils/sglang_config.py:395`; the call stack includes the actual parser boundary at `miles/utils/arguments.py:411`. Retained failure: `evidence/t02-d13-mixed-args-red.xml`; raw log path is in the command.

## GREEN: same test after minimal fix

```bash
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/backends/sglang_utils/test_sglang_config.py::TestValidatedRolloutGpuCount::test_explicit_colocated_rollout_gpus_support_shared_and_dedicated_engines -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-mixed-args-green --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-mixed-args-green.xml > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-mixed-args-green.log 2>&1
```

Expected: explicit16 reaches native config parsing and both eight-GPU pools resolve. Actual: **1 passed,2 warnings,0.48s,exit0**. The initial GREEN precedes adding the five compatibility cases and the explicit concurrency1 check below.

## Final focused and affected regressions

```bash
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/backends/sglang_utils/test_sglang_config.py::TestValidatedRolloutGpuCount -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-mixed-args-final --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-mixed-args-final.xml > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-mixed-args-final.log 2>&1

env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/backends/sglang_utils/test_sglang_config.py tests/fast/backends/sglang_utils/test_sglang_scaling_config.py tests/fast/utils/args/test_schema.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-mixed-args-regression --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-mixed-args-regression.xml > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-mixed-args-regression.log 2>&1
```

Actual focused result: **6 passed,2 warnings,1.56s,exit0**. Actual affected-suite result: **85 passed,2 warnings,1.90s,exit0**, with no skips or deselections:64 SGLang config tests,3 scaling tests,18 schema tests.

| Case | Passing conditions / actual values | Status |
| --- | --- | --- |
| Colocated mixed pools | Trainer1×8 unchanged; rollout16; two regular pools8+8; TP2 widths `[2,2]`;8 native server cells; GPU offsets `[0,8]`; engine offsets `[0,4]`; concurrency `[1,1]`; pool offload `[True,False]`; only dedicated pool injects `enable_memory_saver=False`. | PASS |
| Colocated omitted count | Rollout8;4 TP2 engines; train/rollout offload enabled. | PASS |
| Colocated explicit shared8 | Rollout8 retained;4 TP2 engines; train/rollout offload enabled. | PASS |
| Non-colocated explicit16 | Rollout16 retained;8 TP2 engines; offload remains disabled. | PASS |
| Non-colocated omitted count | `None` remains unset; no local rollout models/engines; offload remains disabled. | PASS |
| Train-only with colocate and explicit16 | Existing train-only override still wins: rollout0 and no inference models/engines. | PASS |

Each resolved pool contains four engines, so the `[True,False]` pool offload policy supplies four shared engines needing offload followed by four dedicated engines not needing it. This describes parsed configuration, not observed GPU engine lifecycle.

## Lint, formatting, syntax, and whitespace

```bash
env PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages PYTHONDONTWRITEBYTECODE=1 timeout 30s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m ruff check --no-cache miles/utils/arguments.py tests/fast/backends/sglang_utils/test_sglang_config.py > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-mixed-args-ruff.log 2>&1
env PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages BLACK_CACHE_DIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-mixed-args-black-cache PYTHONDONTWRITEBYTECODE=1 timeout 30s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check --diff miles/utils/arguments.py tests/fast/backends/sglang_utils/test_sglang_config.py > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-mixed-args-black.log 2>&1
env PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages PYTHONDONTWRITEBYTECODE=1 timeout 30s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m isort --check-only --diff miles/utils/arguments.py tests/fast/backends/sglang_utils/test_sglang_config.py > /data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-d13-mixed-args-isort.log 2>&1
git diff --check -- miles/utils/arguments.py tests/fast/backends/sglang_utils/test_sglang_config.py
git diff -- miles/utils/arguments.py tests/fast/backends/sglang_utils/test_sglang_config.py > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-mixed-args.diff
```

Ruff/isort/whitespace: **PASS**. Ruff emits only the pre-existing deprecated config-layout warning. Black: test file **PASS**; the production file reports pre-existing formatting differences exclusively in the unrelated `validate_eval_train_log_probs` function. Those bytes were preserved. The baseline/current formatter diff comparison below proves those differences are identical to HEAD, and both changed files parse/compile.

```bash
env PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages PYTHONDONTWRITEBYTECODE=1 timeout 30s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'import ast, difflib, json, subprocess; from pathlib import Path; import black, isort; result={}; mode=black.FileMode(line_length=119); files=("miles/utils/arguments.py", "tests/fast/backends/sglang_utils/test_sglang_config.py"); config=isort.Config(settings_path=".");
for name in files:
    original=subprocess.check_output(["git", "show", "HEAD:"+name], text=True); current=Path(name).read_text(); ast.parse(current); compile(current, name, "exec"); before_diff=list(difflib.unified_diff(original.splitlines(), black.format_str(original, mode=mode).splitlines())); after_diff=list(difflib.unified_diff(current.splitlines(), black.format_str(current, mode=mode).splitlines())); assert before_diff == after_diff, name; assert isort.code(current, config=config) == current, name; result[name]={"ast_compile": "PASS", "isort": "PASS", "black_changed_lines": "PASS", "black_whole_file": "PASS" if not after_diff else "PRE_EXISTING_DIFF_IDENTICAL_TO_HEAD"}
print(json.dumps({"black_version": black.__version__, "isort_version": isort.__version__, "files": result}, indent=2))' > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-d13-mixed-args-format.json
```

Actual: **PASS,exit0**. Neither a dependency workaround nor assertion weakening was used. No commit, staging, `progress.md`, `plan.md`, `requirements.md`, README, or rule edit occurred in this child scope.

## Limits and parent-owned follow-up

1. CPU shared validation and native SGLang configuration parsing are verified. Full native Megatron parser/backend validation and TP2/DP4/CP1 training validation were **not run** because local Megatron is unavailable; the GPU-dependent parser limit is not masked by a skip or CUDA monkeypatch.
2. Parsed eight-engine/offload/concurrency semantics do not certify16 PG bundles, real CUDA IPC + remote NCCL transfer, source identity, offload/restore lifecycle,231/256 acquisition within1800s, scoring/backward, two successful optimizer ACKs, or any formal cell. Parent owns the approved native smoke and these acceptance checks.
3. Parent was notified that `miles/utils/args/configs/scaling.py:15-17` still claims colocate ignores this explicit count, and `.agents/rules/launch-and-model-scripts.md:95-98` tells launchers to drop it. Parent owns updating the obsolete CLI help and rule/launcher documentation; neither was edited here.
