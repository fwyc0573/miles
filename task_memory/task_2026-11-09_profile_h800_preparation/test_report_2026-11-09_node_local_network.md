## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record the first H800 engine startup failure, complete environment trace, CPU RED/GREEN regression, minimal correction and native verification limits. |

# Node-local network environment diagnosis

Task ID: `profile-h800-node-network-20261109`.
Branch/worktree: `agent-opd-h800-capacity`, `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`.
Scope: plan step9, local diagnosis/code/tests and this report only. The primary owns all platform, SSH, cloud and GPU operations, task configuration and other task records. None of those operations was performed here.

## Outcome and first-cause evidence

**Confirmed defect:** `_runtime_env()` copied every head-inherited `NCCL_*` value into an explicit Ray job environment. Ray inherited that job environment into remote actors, replacing their node-local platform NIC/HCA selection. The final SGLang subprocess received the head values, even though its own node's platform environment selected different devices.

Native evidence supplied by the primary, read locally:

- Failed job: `exp-1109-181120-274261`, terminal `Failed` at10:29:35Z, before initial weight synchronization.
- Raw log: `/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-181120-274261-head.log`. The first real exceptions are at lines2157–2186 and2213–2241: SGLang `pynccl` calls `ncclGetUniqueId`, which raises `NCCL error: invalid usage` on `10.191.5.7`, `gpu-h800-0057`, rank2; engines1878 and1879 both fail. Other nodes finish TP4 initialization. Later WorkerManager `matches=[]` failures are aftermath and were not changed.
- `evidence/h800-native-node-network-20261109.json`: ranks1/3 select `ens20np0`; rank2 selects `ens22np0` and has a different ordered HCA list. The recorded head selects `ens20np0` in `evidence/h800-trainer-head-startup-log-20261109.json`.
- Actual native launch/runtime records: `evidence/h800-capacity-112k/r256/student/A/exp-1109-181120-274261/{launch,training}.json`. The head's `NCCL_SOCKET_IFNAME=ens20np0` and `NCCL_IB_HCA` are present in the submitted runtime environment.

| Value | Head/ordinary nodes | Rank2 platform | Before fix, rank2 engine | After fix, rank2 engine |
| --- | --- | --- | --- | --- |
| `NCCL_SOCKET_IFNAME` | `ens20np0` | `ens22np0` | `ens20np0` | `ens22np0` |
| `NCCL_IB_HCA` | `=mlx5_0,mlx5_1,mlx5_2,mlx5_3,mlx5_4,mlx5_6,mlx5_7,mlx5_8` | `=mlx5_2,mlx5_3,mlx5_1,mlx5_0,mlx5_4,mlx5_6,mlx5_8,mlx5_7` | Head order | Rank2 order |
| `NCCL_IB_GID_INDEX` | `3` | `3` | `3` | `3` |
| `NVSHMEM_BOOTSTRAP_UID_SOCK_IFNAME` / `NVSHMEM_HCA_PE_MAPPING` | Head socket/HCA mapping | Rank2 socket/HCA mapping | Rank2 values | Rank2 values |

The leak is proven through the production caller path on CPU. It strongly explains the observed native first exception; it does not establish that every other native startup condition is healthy or replace a rerun with the pinned image.

## Complete environment propagation trace

The trace includes both the launcher and later actor/subprocess boundaries, not just an environment factory.

| Boundary | Inspected path/lines | Effective behavior |
| --- | --- | --- |
| Pair-worker parent/child | `tests/manual/agent_opd/qwen35_pair_worker.py:298–326` | Local student child inherits its own container environment; no head-network serialization at this boundary. |
| Worker and Ray startup | `tests/manual/agent_opd/run_qwen35_opd.py:372–391`; `tests/manual/agent_opd/rjob_warmup.py:43–64,136–175` | Worker-local cache/proxy/node-address setup leaves platform NCCL/RDMA values intact. Every raylet starts in its own node environment. |
| Explicit deterministic settings | `scripts/run_glm47_flash_agent_opd.py:83–102` | Existing `_training_env` returns explicit user settings, NVTE/CUBLAS determinism and the validated matching deterministic NCCL channel bounds. It does not return the whole inherited environment. |
| Defective head serialization | `tests/manual/agent_opd/run_qwen35_opd.py:253–265,394–413` | Previously added all inherited `NCCL_*` to explicit job env; now retains the existing cache/offline/library allowlist and `_training_env` only. Multi-node `MILES_NODE_EXTERNAL_IP` removal is unchanged. |
| Real SWE caller | `tests/manual/agent_opd/run_swe_opd.py:195–212` | Enters native `_run` with the ordinary preparation callback, then the preceding runtime-env path. |
| Backend merge | `miles/utils/external_utils/command_utils/common.py:42–82`; `miles/utils/external_utils/command_utils/ray_backend/backend.py:38–76,122–136` | Request env and existing config env have their original precedence. Existing global `NCCL_NVLS_ENABLE`, `NCCL_DEBUG` and `NCCL_DEBUG_FILE` handling is unchanged; no NIC/HCA lookup here. |
| Submission | `miles/utils/external_utils/ray_job.py:17–38` | Native independent-lifetime path passes runtime env unchanged to `ray job submit --runtime-env-json`. The alternate existing launcher-owned path only adds `PYTHONUNBUFFERED`. |
| Native driver/orchestrator | `train.py:127–148,314`; `miles/utils/orchestration_utils.py:59–83`; `miles/ray/wiring.py:16–46` | Native argv parsing starts the worker manager via the existing Ray backend. No new network env is constructed here. |
| Manager actor | `miles/utils/workers/ray_worker_manager.py:64–68` | Manager `.options(name=...)` supplies no runtime-env override; it inherits the job env, not arbitrary head-process `os.environ`. |
| Engine spec | `miles/ray/specs/inference.py:298–332,450–480`; `miles/ray/specs/train.py:211–258` | Engine env selects existing SGLang/global controls; neither engine nor trainer spec copies NIC/HCA selections. Existing intentional CUMEM/NVSHMEM controls are unchanged. |
| Engine actor | `miles/utils/workers/ray_worker_manager.py:409,478` | Actor receives spec env in `runtime_env`; Ray merges parent job env and actor env. `run(..., envs={})` adds no second network override. |
| Final subprocess | `miles/utils/workers/command_actor.py:21–24`; `miles/utils/workers/process_utils.py:11–19` | `Popen(env={**os.environ, **envs})` inherits actor environment. Actual command contains no socket/HCA export. |

After removing the broad inherited NCCL copy, no later boundary reintroduces a head NIC/HCA value. Existing explicit config overrides remain explicit and retain precedence.

## Minimal code and regression changes

- `tests/manual/agent_opd/run_qwen35_opd.py:253–265`: remove `key.startswith("NCCL_")` from inherited forwarding. No new default, API, retry, timeout, fallback, interface classification or transport workaround.
- `tests/fast/test_qwen35_opd_launcher.py:423–455`: update the existing expectation to preserve the final local environment rather than require head-network serialization; add coverage for the existing explicit config-env override mechanism.
- `tests/fast/utils/workers/test_node_network_env.py:34–202`: persistent heterogeneous/uniform/single-node regression using captured platform values. Real path: SWE `_train` → native `_run` / worker environment → RayCommandBackend submission construction → actual native argv / typed SGLang scaling → `InferenceEngineSpec.create` → `RayWorkerManager.init` → actual Ray `_merge_runtime_env` and `RuntimeEnvContext.exec_worker` → real `CommandActor.run` → captured `Popen(env=...)`.
- Ray placement/actor transport, GPU/tokenizer preflight and `Popen` are CPU fakes; submission is captured, not executed. Two TP4 engines per node and separate8/24-GPU inference groups model the failed32-GPU student allocation. Socket/HCA/GID/NVSHMEM mappings are checked for every engine, including both rank2 engines.
- Existing global controls are checked unchanged: `NCCL_NVLS_ENABLE`, IB traffic classes, relaxed ordering, IB enablement, QPS, timeout/retry settings, deterministic channel bounds and NVTE/CUBLAS controls. The test does not add these as defaults to production.

## Verification commands and results

All commands below ran locally in the worktree above. Interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, Ray2.58.1, SGLang0.5.23, Torch2.11.0+cu130, pytest9.1.1. The interpreter's existing pytest module resolves under `/data/ycfeng/envs/openmopd-py312/lib/python3.12/site-packages`; no environment packages were installed or changed. The directly loaded NCCL library reports2.28.9 (`22809`), independently of package metadata. No conda environment change was made.

### Production-path RED → GREEN

```bash
env TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest \
  tests/fast/utils/workers/test_node_network_env.py \
  -q -o addopts='' --tb=short --show-capture=no
```

- Before fix: **expected RED, 1 failed / 2 passed**,4.56s. Rank2 subprocess had `ens20np0` and head HCA order instead of `ens22np0` and rank2 HCA order. Uniform and single-node cases passed.
- After fix: **PASS, 3 passed**,4.28s; the final identical-command run after formatting and test-cache isolation is **3 passed**,2.16s. The expanded regression below also includes all3 cases.
- The final strengthened test also remained RED when only the old `_runtime_env` function from unmodified commit `d91be845` was restored in memory: **1 failed / 2 passed**,2.02s, with the same socket/HCA mismatch. No source reset/checkout was used. Exact restoration command:

```bash
env TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python - <<'PY'
import ast, subprocess, pytest
from tests.manual.agent_opd import run_qwen35_opd as native
source = subprocess.check_output(['git', 'show', 'd91be845:tests/manual/agent_opd/run_qwen35_opd.py'], text=True)
node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == '_runtime_env')
namespace = dict(native.__dict__)
exec(compile(ast.Module(body=[node], type_ignores=[]), 'd91be845:run_qwen35_opd.py', 'exec'), namespace)
native._runtime_env = namespace['_runtime_env']
raise SystemExit(pytest.main(['tests/fast/utils/workers/test_node_network_env.py', '-q', '-o', 'addopts=', '--tb=short', '--show-capture=no']))
PY
```

### Existing affected regressions

```bash
env TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest \
  tests/fast/utils/workers/test_node_network_env.py \
  tests/fast/test_qwen35_opd_launcher.py tests/fast/test_qwen35_pair_worker.py \
  tests/fast/test_swe_launcher.py tests/fast/ray/specs/test_inference.py \
  tests/fast/utils/workers/test_command_actor.py tests/fast/utils/workers/test_process_utils.py \
  tests/fast/utils/external_utils/command_utils/ray_backend/test_backend.py \
  -q -o addopts='' --tb=short --show-capture=no \
  -k 'not test_native_parser_accepts_sglang_and_custom_mis_flags'
```

**PASS: 397 passed,12 skipped,1 deselected**,34.01s. Skips require unavailable Megatron source. The deselected parser test was first run without exclusions: **1 failed,394 passed,12 skipped**,32.57s before adding the3 new cases. Local SGLang does not register the existing `--sglang-enable-prefill-weight-versions` flag. Restoring old `_runtime_env` in memory and running only that existing parser test gives the identical failure (**1 failed**,3.44s). Its argv builder is unchanged; this existing local dependency mismatch was not fixed or suppressed in production.

An intermediate combined run exposed test-only parser-default cache pollution: the new test initialized the shared `parser_defaults()` fixture while SWE argv was installed, causing4 later SWE tests to see conflicting `swe_cell=None` and `A/r256`. The regression now initializes that existing fixture under canonical `sys.argv=['test']` before native argv parsing. The final run above includes those4 tests and passes. No product parser or merge behavior was changed.

```bash
env TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest \
  tests/fast/utils/workers/test_ray_worker_manager.py \
  -q -o addopts='' --tb=short --show-capture=no
```

**PASS: 132 passed**,2.82s. Total final affected checks: **529 passed,12 skipped,1 known-baseline parser case deselected**.

### Local NCCL bootstrap discriminator

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python - <<'PY'
import subprocess, os, socket
library = '/data/ycfeng/envs/miles-agent-opd-cpu/lib/python3.12/site-packages/nvidia/nccl/lib/libnccl.so.2'
code = '''import ctypes, json
library=ctypes.CDLL(%r)
version=ctypes.c_int()
library.ncclGetVersion(ctypes.byref(version))
unique_id=ctypes.create_string_buffer(128)
result=library.ncclGetUniqueId(ctypes.byref(unique_id))
print(json.dumps({"nccl_version": version.value, "ncclGetUniqueId": result}))
''' % library
print('local_interfaces=', socket.if_nameindex())
for interface in ('ens20np0', 'eth0'):
    child = subprocess.run(
        ['/data/ycfeng/envs/miles-agent-opd-cpu/bin/python', '-c', code],
        env={**os.environ, 'NCCL_SOCKET_IFNAME': interface, 'NCCL_DEBUG': 'WARN'},
        capture_output=True, text=True, check=True)
    print(interface, child.stdout.strip(), child.stderr.strip())
PY
```

**PASS, discriminator only:** local interfaces `lo,eth0,docker0`; a fresh subprocess with absent `ens20np0` returns5 (`invalid usage`) and `Bootstrap : no socket interface found`; a fresh subprocess with existing `eth0` returns0. Both libraries report version22809. No GPU initialization/collective was performed. Native image NCCL is2.30.7, so this is not an exact pinned-native reproduction.

### Lint, formatting and diff

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check \
  --per-file-ignores tests/fast/test_qwen35_opd_launcher.py:F401 \
  --per-file-ignores tests/fast/test_qwen35_opd_launcher.py:F811 \
  tests/manual/agent_opd/run_qwen35_opd.py tests/fast/test_qwen35_opd_launcher.py \
  tests/fast/utils/workers/test_node_network_env.py
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/black --check \
  tests/fast/utils/workers/test_node_network_env.py
git diff --check
```

**PASS** for all3 checks. Ruff exclusions are confined to pre-existing unused/redefined fixture imports in the existing launcher test; production/new regression files pass without exclusions. Ruff reports the existing deprecated top-level config keys. The CPU interpreter has no Ruff/Black module, so existing local lint executables were used; no installation occurred.

## Remaining native verification

The primary must perform any native rerun, not this scoped agent. On the pinned image and intended heterogeneous H800 nodes, inspect the actual submitted runtime env and each final engine's env: no head-inherited socket/HCA selection in the job env; rank2 uses `ens22np0` and its ordered HCA mapping; ordinary nodes retain their own values; existing deterministic controls remain unchanged. Confirm both rank2 engines finish TP4 initialization and initial weight synchronization before evaluating the original capacity acceptance criteria. Native NCCL/library/host-network hypotheses remain unexcluded until that evidence exists. No transport disabling, socket substitute, retry or timeout change is part of this correction.

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Plan9：首错和完整 env 路径 | PASS | 原生日志、实际 launch env、rank2 平台值和最终 subprocess RED 一致。 |
| Plan9：最小修复与 CPU GREEN | PASS | 删除继承 NCCL 广播；异构、同构、单节点及显式覆盖均通过。 |
| Plan9：相关回归和单份报告 | PASS | 529 passed；跳过与旧版本 parser 失败均明确记录。 |
| Scoped commit | TODO | 本 checkpoint 在精确 owned-file staging/commit 前记录。 |
| 后续 native verification / Plan8 acceptance | BLOCKED | 必须由 primary 执行；本委派禁止平台/GPU操作，不能用 CPU 结果代替。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** scoped assignment 至本次最终 CPU 验证｜**当前前沿：** 单份报告与 owned-file commit。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 复现覆盖必要 caller/actor/subprocess 边界；相关验证通过后停止扩展。 |
| D2 细节反复重试 | CLEAR | 测试修正针对 placement 和已证实 parser cache；没有产品参数试错。 |
| D3 支线问题修补 | CLEAR | 旧 parser 版本不匹配仅记录；未修改 WorkerManager aftermath。 |
| D4 可并行任务停滞 | CLEAR | 用户明确禁止委派；平台和 cleanup 由 primary 独立所有。 |
| D5 超范围镀金 | CLEAR | 生产仅删除继承 NCCL 广播；没有新 API/default/transport 分支。 |
| D6 分析空转 | CLEAR | 完整路径检查形成可复现 RED、最小修复和 GREEN。 |
| D7 路线违背 | CLEAR | 仅 scoped code/tests/单份报告；没有平台、SSH、云或 GPU 操作。 |

**文档检查：** 本切片的 plan9 和显式委派范围中，S1–S6 均未发现明显缺陷。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。
**需停止的偏离行为：** 无。
**接下去的路线：**
1. 精确提交3个 owned Python 文件和本报告 → 完成标志：commit 无 primary docs/config/runtime evidence。
2. 交回 primary → 完成标志：保留 native 未验证状态，并由 primary 获取原生节点 env/TP4/初始权重同步证据。

## 4. 最值得关注的 3 点

1. 根因是显式 job env 覆盖节点选择，不是 WorkerManager 清理报错。
2. 后续 actor 和 subprocess 无第二次 socket/HCA 广播；既有 job-global 控制保持不变。
3. CPU NCCL2.28.9 证明缺失 NIC 可触发同类错误，但不能替代 native2.30.7 复验。
