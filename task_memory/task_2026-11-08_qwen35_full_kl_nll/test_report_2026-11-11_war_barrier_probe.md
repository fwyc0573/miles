## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Prepare one isolated native coarse-WAR-barrier experiment; record CPU contracts, exact commands and verification limits. No GPU or platform operation. |
| 2026-11-11 | Primary joined verification:145 PASS. Defer native submission because the GDN UNKNOWN contract may already select the coarse fallback. |

# Teacher scoring coarse WAR barrier probe preparation

TaskID: `profile-war-barrier-probe-preparation-20261111`.

## Outcome and scope

**CPU-ready; native experiment NOT RUN.** Only the following six owned files were edited or created. No staging, commit, delegation, SSH, GPU allocation or platform request was performed. The primary owns acceptance and any subsequent execution.

| File, relative to repository root | Change |
| --- | --- |
| `tests/manual/agent_opd/submit_teacher_scoring_probe.py` | Extend the existing, untracked primary launcher with optional canonical `envs`; pass the mapping to `ResourceConfig.envs` and serialize it in dry-run output and submission receipts. |
| `tests/manual/agent_opd/probe_teacher_scoring.py` | Record the actual `os.environ.get("SGLANG_FORCE_COARSE_WAR_BARRIER")` in `runtime.sglang_environment`, retained by the existing `preload.json` and `result.json` writers. |
| `tests/fast/test_teacher_scoring_submission.py` | Preserve the primary's original tests; add default, environment boundary/receipt and byte-equivalent variant checks. |
| `tests/fast/test_teacher_scoring_probe.py` | Extend the existing runtime test to actual absent/`0`/`1` environment values and secret exclusion. |
| `task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_war_barrier_probe_config.json` | New isolated diagnostic variant. |
| `task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_war_barrier_probe.md` | This preparation and CPU verification report. |

The absent `envs` default remains `{"PYTHONPATH": "/data/ycfeng"}` for the real configuration. Controller environment values are not copied into the resource. The variant adds only `SGLANG_FORCE_COARSE_WAR_BARRIER="1"`. Receipts capture the configured resource environment before native platform additions such as `EXP_ID`; the snapshot uses a copy so those additions cannot change the recorded configuration. No ambient environment or credential dump was added. Existing NCCL recording is unchanged.

The worker records the flag from its actual environment, not from either config. A missing variable is JSON `null`, not an inferred default or a claim that the switch was applied. The native teacher child continues to inherit the worker environment through the existing `subprocess.Popen` call; no command export, alternative teacher launcher, production monkeypatch or scheduler source edit was added.

## Diagnostic rationale and invariants

The retained native scheduler's existing switch is inspected at `evidence/native-sglang-cache-source-20261111/exp-1111-040603-422872/source/srt/managers/scheduler.py:2027-2038`: when forced, the scheduling stream waits for the whole forward stream instead of the published shared-read event. The native event loop invokes this barrier after `run_batch` at lines 2123-2127. The local native resource owner defines `envs` at `/data/ycfeng/steptron/steptron/exp/base_exp.py:4055`; the existing serializer passes `cfg.envs` into template and container environments at `/data/ycfeng/steptron/steptron/utils/stepmind.py:488-506`. These are source inspections, not executed platform serialization or deployed-worker evidence.

This is a controlled test of ordering sensitivity, not a proven race or a causal correction. The authoritative historical measurements remain in [the primary RCA report](test_report_2026-11-11_workflow_rca.md): each R1 teacher job had cold 14/14 exact pairs but warm only 4/14, with maximum absolute differences A 0.2006068229675293 and B 1.0602149963378906. Warm full-input scoring with zero cached tokens also differs from cold references. Hidden/canonical KV replacement and another warm-state cause therefore remain hypotheses; warm full-input results are not a numerical oracle.

Exact variant difference from `teacher_scoring_probe_config.json`:

```diff
+  "envs": {"SGLANG_FORCE_COARSE_WAR_BARRIER": "1"},
-  "output_parent": "task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-probe-20261111/native",
+  "output_parent": "task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-war-barrier-probe-20261111/native",
```

Removing that environment line and restoring the output string reproduces the base file **byte for byte**. `task_id`, `formal_config`, sample fixture, pair list, repeats, all timeouts and acceptance text remain byte-equivalent. The formal configuration and native teacher command owner also compare byte-equal to repository HEAD. Cache policy, chunk size 8192, native tracking configuration, dtype, models, math, input order and seeds are not edited. Each pair still uses seven samples and two repeats: 56 scoring requests and 32 cache flushes. No tolerance, retry, timeout or default behavior was added.

## CPU verification

Working directory for every command below:

```text
/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image
```

Environment: existing `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python **3.12.13**, pytest **9.1.1**; no conda activation or dependency installation. Controller dry-runs and syntax checks use `/usr/bin/python3`, Python **3.10.6**. Temporary pytest artifacts stay under `/data/ycfeng/tmp`; bytecode and pytest cache writes are disabled. HTTP, GPU inspection and submission boundaries in tests are mocked; existing cleanup tests launch only an owned CPU child.

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Existing baseline tests | Original tests succeed before edits | 36 passed, 4 warnings, 0.69 seconds | PASS |
| Extended CPU contracts | All original and new cases succeed | 43 passed, 4 warnings, 1.04 seconds; final run 43 passed, 4 warnings, 0.85 seconds | PASS |
| Default dry-run environment | Only existing resource `PYTHONPATH`; ambient flag excluded | Exact expected mapping | PASS |
| Environment boundary and receipt | `ResourceConfig.envs` at mocked backend boundary and receipt contain configured flag; receipt unaffected by native-style `EXP_ID` mutation | Both absent and `1` cases succeed | PASS, mocked submission only |
| Runtime environment serialization | Actual absent/`0`/`1`, regardless of a deliberately conflicting config value; test secret omitted | `null`/`"0"`/`"1"` recorded as expected | PASS, mocked GPU inspection |
| Variant invariants | Only `envs` and output isolation differ; seven samples, two repeats, 56 requests, 32 flushes, chunk 8192 | Byte-equivalent restoration and counts succeed | PASS |
| Real-config A/B controller dry-runs | One teacher task each, H800/codesign, GPU4/CPU32/memory256/replica1, configured flag, isolated output, no receipt writes | Both exit 0 with exact expected fields; neither receipt exists | PASS, no allocation |
| Protected formal config and native teacher owner | No edit | Both byte-equal to HEAD | PASS |
| Python 3.10 parsing and scoped whitespace check | Four Python files parse; no diff whitespace errors | Four parses succeed; `git diff --check` exits 0 | PASS |
| Native flag application, score drift and performance | Actual deployed runtime and scoring measurements | Not run | UNVERIFIED; no parity/performance PASS |

The four pytest warnings are the baseline SWIG type deprecations and two existing `datetime.utcnow()` deprecations from `miles/utils/external_utils/command_utils/common.py:140`; no test failure was suppressed.

Primary inspected the delivery and reran it with the existing payload contracts: **145 passed,20 warnings in5.06 seconds**, Python3.12.13/pytest9.1.1. The added warnings are existing Torch JIT deprecations and CPU-only quantization notices. This does not prove native flag application or scoring correctness. The native experiment is **DEFERRED, not submitted**: later source analysis shows GDN's shared-read contract is `UNKNOWN`, so the original scheduler may already select coarse fallback. Without actual event/branch evidence, unchanged results would not exclude ordering. See the primary RCA report for the selected-FP32 snapshot candidate now being prepared. Exact joined command:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/teacher-scoring-war-joined-primary-20261111
```

Exact test commands:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_submission.py tests/fast/test_teacher_scoring_probe.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/war-barrier-baseline-pytest-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_submission.py tests/fast/test_teacher_scoring_probe.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/war-barrier-contract-pytest-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_submission.py tests/fast/test_teacher_scoring_probe.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/war-barrier-final-pytest-20261111
git diff --check -- tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_teacher_scoring_probe.py
```

Exact source/byte/syntax check:

```bash
python3 -B - <<'PY'
import ast
import json
import subprocess
from pathlib import Path
repo = Path.cwd()
task = repo / 'task_memory/task_2026-11-08_qwen35_full_kl_nll'
base = (task / 'teacher_scoring_probe_config.json').read_bytes()
variant = (task / 'teacher_scoring_war_barrier_probe_config.json').read_bytes()
b, v = json.loads(base), json.loads(variant)
restored = variant.replace(b'  "envs": {"SGLANG_FORCE_COARSE_WAR_BARRIER": "1"},\n', b'', 1).replace(v['output_parent'].encode(), b['output_parent'].encode(), 1)
assert restored == base
for relative in ('task_memory/task_2026-11-08_qwen35_full_kl_nll/formal_config.json', 'tests/manual/agent_opd/qwen35_pair_worker.py'):
    assert (repo / relative).read_bytes() == subprocess.check_output(['git', 'show', 'HEAD:' + relative])
for relative in ('tests/manual/agent_opd/submit_teacher_scoring_probe.py', 'tests/manual/agent_opd/probe_teacher_scoring.py', 'tests/fast/test_teacher_scoring_submission.py', 'tests/fast/test_teacher_scoring_probe.py'):
    ast.parse((repo / relative).read_text(), filename=relative, feature_version=(3, 10))
for pair in ('A', 'B'):
    assert not (task / f'evidence/teacher-scoring-war-barrier-probe-20261111/admission-{pair}-r1.json').exists()
print(json.dumps({'variant_changed_keys': ['envs (added)', 'output_parent'], 'remaining_variant_bytes_equal_base': True, 'formal_config_bytes_equal_HEAD': True, 'native_teacher_owner_bytes_equal_HEAD': True, 'python_3_10_ast_parse_files': 4, 'dry_run_receipts_not_created': ['A', 'B']}, indent=2))
PY
```

## Exact submit and worker CLI

The following CPU dry-runs were executed; they do not initialize authentication, import the native submission backend, allocate resources or create receipts:

```bash
python3 -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_war_barrier_probe_config.json --pair A --receipt task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-war-barrier-probe-20261111/admission-A-r1.json --dry-run
python3 -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_war_barrier_probe_config.json --pair B --receipt task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-war-barrier-probe-20261111/admission-B-r1.json --dry-run
```

Prepared native submission commands for the PRIMARY ONLY, **not executed here**. Initialize the existing handbook personal-auth/proxy environment first; retain `STEPMIND_BACKEND=rjob`, `PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image:/data/ycfeng/steptron`, `PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, and `TMPDIR=/data/ycfeng/tmp`. Keep each native launcher alive through its worker's lifetime. The configured environment flag is carried by `ResourceConfig.envs`, not a controller shell export.

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_war_barrier_probe_config.json --pair A --receipt task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-war-barrier-probe-20261111/admission-A-r1.json
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_war_barrier_probe_config.json --pair B --receipt task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-war-barrier-probe-20261111/admission-B-r1.json
```

Exact worker scripts emitted by the dry-runs; the submitter wraps each in its existing `bash -lc` command:

```bash
# Pair A
export PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image
export LD_LIBRARY_PATH=/usr/local/cuda-13.0/compat"${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec timeout --signal=TERM --kill-after=90s 3600s /opt/sglang/bin/python3 -u -B -m tests.manual.agent_opd.probe_teacher_scoring --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/formal_config.json --pair A --samples /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-probe-20261111/retained-cases.json --output-dir /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-war-barrier-probe-20261111/native/A/admission-A-r1 --repeats 2 --request-timeout 3600

# Pair B
export PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image
export LD_LIBRARY_PATH=/usr/local/cuda-13.0/compat"${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec timeout --signal=TERM --kill-after=90s 3600s /opt/sglang/bin/python3 -u -B -m tests.manual.agent_opd.probe_teacher_scoring --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/formal_config.json --pair B --samples /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-probe-20261111/retained-cases.json --output-dir /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-war-barrier-probe-20261111/native/B/admission-B-r1 --repeats 2 --request-timeout 3600
```

The actual teacher argv remains owned by `tests/manual/agent_opd/qwen35_pair_worker.py:_teacher_command`, invoked unchanged by the probe. The pinned image's worker Python version and scheduler source identity must be read from actual runtime artifacts, not inferred from these CPU checks.

## Preparation checkpoint — check-progress self-check

## 1. 规划完成情况

**汇总：** PASS 4｜BLOCKED/FAILED/SKIPPED 1｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Canonical `envs` 传递及 receipt | PASS | 既有提交入口已扩展；CPU boundary/receipt 测试通过。 |
| 实际 runtime flag 记录 | PASS | 实际环境 absent/0/1 与冲突配置测试通过。 |
| 唯一 variant 与 workload invariants | PASS | 差异仅 envs/output；剩余字节、56 requests/32 flushes 已核验。 |
| CPU 验证、CLI 与本报告 | PASS | 43 tests、2 dry-runs、源码边界与 Python3.10 解析通过，CLI 已记录。 |
| 本子任务 GPU/platform 执行 | SKIPPED | 明确禁止执行，由 PRIMARY 拥有。 |
| PRIMARY 最终验收/提交及 native 因果结论 | TODO | 本子任务交付 CPU-ready 改动，不替 PRIMARY 验收，不提交。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次 preparation assignment 至最终 CPU 验证｜**当前前沿：** PRIMARY 验收这 6 个文件；native controlled experiment 不属于本子任务执行权限。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅为明确要求扩展既有 env/receipt/runtime 合同，验证后停止。 |
| D2 细节反复重试 | CLEAR | baseline 与新合同均通过；最终复验仅覆盖一次对齐修正。 |
| D3 支线问题修补 | CLEAR | 没有修改 scheduler、formal workload 或其他 RCA 问题。 |
| D4 可并行任务停滞 | CLEAR | CPU tests、dry-runs 和只读边界核验已并行；不 delegation 的限制保留。 |
| D5 超范围镀金 | CLEAR | 只有 canonical envs 与单个实际 flag；没有新 flag、retry、timeout 或 tolerance。 |
| D6 分析空转 | CLEAR | 源码检查服务于唯一 variant，已有可执行 CLI 和 CPU-ready 交付。 |
| D7 路线违背 | CLEAR | 只改 6 个授权文件；没有平台操作、formal 改动、stage 或 commit。 |

**文档检查：** S1–S6 均未发现本 preparation 范围内的明显缺陷。`requirements.md` D40、`plan.md` 当前前沿、04/05 tickets 与 `progress.md` 均保留 warm-state native correctness blocker；本次 assignment 不改变它们。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。
**需停止的偏离行为：** 无。

**接下去的路线：**
1. PRIMARY 验收：检查 6 文件和测试证据 → 完成标志：确认默认不变、唯一 variant 差异及 configured/actual 两类记录，随后由 PRIMARY 决定提交。
2. PRIMARY native controlled experiment：按既有权限和 fresh admission 执行 → 完成标志：实际 resource flag、runtime flag、native source/model 身份与全部56 requests/32 flushes齐备；分别比较 cold/warm 与既有 cold references，不自动判定 race、parity 或性能通过。

## 4. 最值得关注的 3 点

1. 43 CPU PASS 只验收 preparation；actual native flag 和概率变化仍未验证。
2. Variant 仅增加 native coarse barrier 环境变量及隔离输出，formal/input/math/缓存配置保持原样。
3. Formal A/B 仍暂停；本子任务没有提交、启动、停止或修改任何作业。
