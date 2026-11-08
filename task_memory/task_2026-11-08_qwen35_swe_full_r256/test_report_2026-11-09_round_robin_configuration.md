## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | T02-ROUND-ROBIN-EXPERIMENT: implement the optional native router policy transport, isolate the approved A/r256 profile, and verify local argv/schema/hooks with CPU-only regressions. |

# Round-robin capacity configuration verification

## Result and scope

**PASS for local configuration and native transport only.** [D12](requirements.md#d12--original-request--follow-up-answer-2026-11-09-one-routing-only-capacity-experiment) approves one isolated A/r256 routing-only experiment after the actual cache-aware acquisition failure. This slice prepares that experiment; it performs no GPU/platform/API/SSH/cloud/network/auth/resource operation or commit. Ticket02 remains in-progress.

Gain: the existing SWE recipe can now send an explicitly selected policy to its existing native SGLang router. `run_swe_opd._training_args` adds only the optional top-level `router_policy` field beside existing run-wide serving configuration; `_flags` already emits the native argument and omits null fields. No CLI flag, generic extra-args path, wrapper, core router change, default override or fallback was added.

Owned files:

- `tests/manual/agent_opd/run_swe_opd.py`: two-line explicit transport.
- `tests/fast/test_swe_launcher.py`: two parameterized persistent regression cases.
- [deepswe_capacity_round_robin_config.json](deepswe_capacity_round_robin_config.json).
- [evidence/deepswe-round-robin-launcher.json](evidence/deepswe-round-robin-launcher.json): actual dry-run argv, config differences, typed policy, six source fields, nine hooks and validation limits.
- This report. Parent-owned requirements/plan/progress/tickets and all existing profiles were not edited by this slice.

## Exact configuration differences

The new profile equals a deep copy of the current [deepswe_capacity_smoke_config.json](deepswe_capacity_smoke_config.json) with **exactly four leaf changes**:

| Field | Before → after |
| --- | --- |
| `phase` | `deepswe-capacity-smoke` → `deepswe-capacity-round-robin` |
| `router_policy` | absent → `round_robin` |
| `run_root` | `.../deepswe-0913/capacity-smoke` → `.../deepswe-0913/capacity-round-robin` |
| `shared_dir` | `.../evidence/deepswe-capacity-smoke` → `.../evidence/deepswe-capacity-round-robin` |

Exact absolute paths are retained in the evidence. Configuration SHA256: `9babf538a61298fbe30068d689ba5638039b99a5bd550c64006b415a09ab63aa`; base SHA256: `fb08cbe905e9b7c1ab0390b1cb3fbda9d3f498b11145071ff68abded523adb75`.

All inputs/models/seeds/LR/objective/TIS/checkpoint settings remain identical: 256 candidates, two successful updates, two bank uses, save interval2, `release_scoring_output=true`, 131072 context, n1, minimum231, acquisition1800s, `max_running_requests=1`, CUDA graph disabled, studentTP2/8GPUs and teacherTP2/2GPUs. Empty checkpoint hook args preserve `swe_evaluation_configuration=None`; no evaluation is enabled. The copied B section is unchanged to preserve exact identity parity, **not authorization to run B**. Only A/r256 is approved.

The original failure, integration/async, formal, formal evaluation and baseline profiles remain untouched. Five tracked relevant profiles were independently compared byte-for-byte with HEAD by the configuration check.

## Observed native transport

- `miles/utils/args/configs/router.py:61` registers the existing `RouterArgs.add_cli_args(...use_router_prefix=True...)`; `from_args` stores `router_args['policy']`.
- Actual action: `--router-policy`, destination `router_policy`, native default `cache_aware`; `round_robin` is an accepted native choice. No `--sglang-router-policy` is emitted.
- The original profile's actual CLI argv was captured before and after the edit: **216 elements, exactly identical**. Explicit null also preserves that argv. The isolated profile emits **218 elements**, exactly one additional `--router-policy round_robin`; after removing those two elements and normalizing only the isolated output root, its complete argv equals the original.
- Real native parser/custom-hook registration passes with unique options, all six source fields and all nine existing hooks. `AllConfig`, `OrchestratorConfig`, `RolloutConfig` and `TrainerConfig` JSON roundtrips preserve `router_args.policy=round_robin` and `sglang_router_policy=None`.
- The existing `compute_sglang_router_args → router_args_to_argv → parse_router_args_argv` chain returns native `RouterArgs.policy=round_robin`. The native request timeout remains3600s; the independent bank-acquisition deadline remains1800s.
- The existing smoke `training_protocol` accepts two updates/256 candidates/two uses; the scoring observation retains patched-source SHA256 `8b0370c0d50a2463781ae3c622e30f923d096485aed3c0f8939be4cc13689081`. No patch was applied by these checks.

CPU transport uses the existing `_typed_swe_config` post-parse fixture only for resolved schema fields. Actual explicit CLI/hook fields and remaining backend argv values replace its inputs. The local CPU interpreter has no Megatron package; its SGLang0.5.23 does not consume the pinned-image prefill-weight-version extension. Unconsumed backend/version arguments are listed in the evidence; no router/source/TIS/scoring argument is unconsumed. This does not certify full GPU startup or capacity.

## Commands, environment and checks

Working directory: `/data/ycfeng/sota-engine/miles`. Python `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, version3.12.13; pytest9.1.1, SGLang router0.3.2, SGLang0.5.23, PyTorch2.11.0, Pydantic2.13.5. No conda activation or dependency installation. All temporary scripts/logs use `/data/ycfeng/tmp/T02-ROUND-ROBIN-EXPERIMENT`.

The following environment was used for each actual CLI/check/test command:

```bash
PYTHONPATH=/data/ycfeng/sota-engine/miles
PYTHONNOUSERSITE=1
PYTHONDONTWRITEBYTECODE=1
TMPDIR=/data/ycfeng/tmp/T02-ROUND-ROBIN-EXPERIMENT
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
CUDA_VISIBLE_DEVICES=
WORLD_SIZE=1
OMP_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
```

Exact executed commands below are prefixed with `env` assigning those variables. The original config command ran both before and after the recipe edit, retaining `default-before.argv.txt`/`default-after.argv.txt` and their matching `.log` files. The experiment command retained `round-robin.argv.txt`/`round-robin.log`. All three exited0.

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.run_swe_opd --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_capacity_smoke_config.json --pair A --protocol r256 --role train --dry-run

timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.run_swe_opd --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_capacity_round_robin_config.json --pair A --protocol r256 --role train --dry-run

timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B /data/ycfeng/tmp/T02-ROUND-ROBIN-EXPERIMENT/verify_configuration.py > /data/ycfeng/tmp/T02-ROUND-ROBIN-EXPERIMENT/configuration-verification.log 2>&1

timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_launcher.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/T02-ROUND-ROBIN-EXPERIMENT/launcher-final --junitxml=/data/ycfeng/tmp/T02-ROUND-ROBIN-EXPERIMENT/launcher-final.xml > /data/ycfeng/tmp/T02-ROUND-ROBIN-EXPERIMENT/launcher-final.log 2>&1
```

Expected and actual: `ROUND_ROBIN_CONFIG_PASS differences=4 default_argv=216 experiment_argv=218 source_fields=6 hooks=9 minimum=231`; **20 tests PASS, zero failures/errors/skips, 2.88s**. The new cases cover absent/null unchanged defaults, exactly one native policy flag and byte-identical remaining argv, real custom-hook registration, native typed roundtrip and actual backend router argument construction. The first run also passed20 in4.43s; only the new test block was subsequently formatted/sorted, then the final suite reran.

Existing cached Ruff0.14.7/Black24.3.0/isort5.13.2 were reused without installation:

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check --no-cache tests/manual/agent_opd/run_swe_opd.py tests/fast/test_swe_launcher.py > /data/ycfeng/tmp/T02-ROUND-ROBIN-EXPERIMENT/ruff-final.log 2>&1

env PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages BLACK_CACHE_DIR=/data/ycfeng/tmp/T02-ROUND-ROBIN-EXPERIMENT/black-cache PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B /data/ycfeng/tmp/T02-ROUND-ROBIN-EXPERIMENT/static_check.py > /data/ycfeng/tmp/T02-ROUND-ROBIN-EXPERIMENT/static-check.log 2>&1

git diff --check -- tests/manual/agent_opd/run_swe_opd.py tests/fast/test_swe_launcher.py task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_capacity_round_robin_config.json
```

PASS: Ruff on both whole files, AST/compile on both files, Black/isort on the new regression, and diff whitespace. Existing whole-file Black differences in both files and the test's existing isort blank-line difference are preserved; those whole-file formatter checks are **not** reported PASS. Static verification proves the old test bytes are an exact unchanged prefix and the recipe differs only by the two transport lines. Raw result: `static-check.json`.

An initial inspection-only prefix assertion incorrectly stripped HEAD's final newline; the observed lengths/endings were identical and `source.startswith(baseline)` was true. The check was corrected to compare exact prefix bytes; no repository code changed for that inspection failure. CPU import/deprecation warnings, including unavailable `vllm._C/libcudart.so.12`, remain in logs and did not execute GPU inference.

## 1. 规划完成情况

**汇总：** PASS2｜BLOCKED/FAILED/SKIPPED1｜TODO0（本委派切片；Ticket02整体仍在执行）。

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 原生策略 transport 与隔离配置 | PASS | 两行 recipe transport；配置只有四项差异；旧 argv 不变。 |
| CPU argv/schema/hooks/tests 与证据 | PASS | 实际 parser、四种 typed roundtrip、九 hooks、20 回归及 scoped static 检查完成。 |
| 实际 GPU 采集/scoring/optimizer/HF | SKIPPED | 本切片明确禁止；CPU 结果不满足 Ticket02 的原生容量验收。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** T02-ROUND-ROBIN-EXPERIMENT 委派至本地验证完成｜**当前前沿：** 父 agent 的一次已批准 A/r256 experiment；02/03/08独立推进。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 最小 transport 和已有 fast test；验证完成后不扩展 harness。 |
| D2 细节反复重试 | CLEAR | 仅修正新 block 格式及一个检查器的换行比较；科学参数没有反复修改。 |
| D3 支线问题修补 | CLEAR | 保留既有全文件格式差异和所有其他 owner 的工作。 |
| D4 可并行任务停滞 | CLEAR | 明确文件切片；不接管或等待父 agent 的GPU/03/baseline工作。 |
| D5 超范围镀金 | CLEAR | 无新CLI、core修改、wrapper、fallback或generic extra args。 |
| D6 分析空转 | CLEAR | 已交付实际配置、真实dry-run和持久回归；检查完成即返回。 |
| D7 路线违背 | CLEAR | requirements D12/明确委派批准仅routing；阈值、deadline、context、sampling、资源不变。 |

**文档检查：** 本切片S1–S6未发现需改变spec/ticket的缺陷；D12已由父agent记录。配置验收不关闭02，也不直接改正式配置。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动。
**需停止的偏离行为：** 无。
**接下去的路线：**
1. 父 agent 核对本切片配置/transport → 完成标志：唯一 `--router-policy round_robin`、四项配置差异、原策略默认不变。
2. 父 agent 执行且仅执行已批准的 A/r256 GPU experiment → 完成标志：实际1800s内至少231条，真实scoring/两次optimizer ACK/固定bank复用/HF身份；不能用本CPU报告替代。
3. 并行：03既有async验收 ‖ 08既有baseline；正式04–07仍受02/03原生前置验收约束。

## 4. 最值得关注的 3 点

1. 本地transport和配置完成；GPU、scoring、optimizer与capacity均未在本切片验证。
2. 原始cache-aware失败证据、正式/async/evaluation/baseline配置保持原样；B未获此次运行授权。
3. 父agent接续一次已批准A/r256；不增加采样、retry、deadline或放宽231门槛。
