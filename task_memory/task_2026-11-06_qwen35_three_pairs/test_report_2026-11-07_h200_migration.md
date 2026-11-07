## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Parent wires the manifest GPU identity through both worker checks; record CPU red/green limits and pending pinned qualification. |
| 2026-11-07 | QWEN-P3-H200-MANIFEST: freeze A/B-only H200 manifest, verify exact structural/native dry-run deltas, reuse pinned lifecycle evidence, and report existing H800 device-name blockers. |

## 1. 规划完成情况

**任务：** `QWEN-P3-H200-MANIFEST`。本报告仅验证准备工作，不代表实际 H200 runtime 合格。父会话负责 personal platform inspection、最小启动修正、提交和实际运行验收。

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 3。设备身份变更的本机与固定镜像检查已通过；固定镜像整套90 PASS/3 FAIL，另有3个旧baseline测试fixture待修，正式提交继续。

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| P0 | PASS | 已记录要求、规则和设计；本次重新读取所有 `.agents/rules/**/*.md`。 |
| P1 | PASS | [requirements.md](requirements.md) D18 明确 A/B H200、32 卡内不可抢占和原有预算。 |
| P2 initial qualification | PASS | 既有 population、pinned runtime 和 baseline evidence；不替代 H200 runtime。 |
| P3-A | TODO | H200 manifest/dry-run与设备/CLI检查PASS；待正式提交和实际运行。 |
| P3-B | TODO | 同一准备路径；D17 fresh100 已批准，旧一次 update 保留为 discarded historical work。 |
| P3-C | BLOCKED | 最新计划记为 H800 scheduling 阻塞；本次未检查或改变其 job/config。 |
| P4 | TODO | 实际 updated/final D8、100-position accounting 和 HF artifact 尚未完成。 |

### Deliverables and exact delta

- 新 manifest：[training_config_h200.json](training_config_h200.json)。它完整保存 source manifest 的全部保留字段，不是 override fragment，也没有新增 loader。
- Source：[training_config.json](training_config.json)，未编辑；C 仍在 source，student memory allocation 仍为1536 configured units。C 现有 H800 job 和 D15/D16 预算不变。
- 仅三处 root scalar 修改：`charged_group: codesign -> step_main`、`gpu_tag: H800 -> H200`、`capacity_gpus: 128 -> 32`；仅排除 `pairs.C`。
- `preemptible=false` 本来就为 false，原样保留，**不是第四处 scalar 修改**。
- A/B 的整个 nested allocation 与 source 精确相等：每个 student 1 node ×8 GPUs、teacher 1 node ×2 GPUs，双方 TP2；student 每个 rollout engine 使用2 GPUs，即4个 student engines。每对10 GPUs，合计20 <=32。
- Image digest、worker Python、CUDA compatibility path、local source/mount、cloud mounts、population、output/rendezvous paths、context131072、request timeout3600、startup timeout1800、token/memory/request settings、`num_rollout=100` 均原样保留。
- Optimizer 不在 JSON 内另行复制：现有 `run_qwen35_opd.py:216–219` 继续拥有 Adam、LR2e-6、constant、warmup0、decay0、betas0.9/0.98；`scripts/run_qwen3_dense.py:83` 的4B recipe 保持 `optimizer_cpu_offload=False`。未编辑代码、sampling、TIS、monitoring、loss mask 或 weight transport。
- A 保留100 positions，discarded updates 为0；B 为 D17 fresh100，旧1次 update 不计入新100；C 不变。没有额外 optimizer probe 或自动延长预算。

### Environment and executed commands

Workdir：`/data/ycfeng/sota-engine/miles`；本地 `python3` 为 **3.10.6**。验证仅使用 standard library；未使用 conda、Git、platform/GPU/SSH/cloud 或新依赖。

两个原生 CLI 命令均 exit0，stderr 为空：

```bash
python3 -B tests/manual/agent_opd/submit_qwen35.py --config task_memory/task_2026-11-06_qwen35_three_pairs/training_config_h200.json --pair A --dry-run
python3 -B tests/manual/agent_opd/submit_qwen35.py --config task_memory/task_2026-11-06_qwen35_three_pairs/training_config_h200.json --pair B --dry-run
```

实际输出字段：

| Field | A | B |
| --- | --- | --- |
| `requested_gpus` | 10 | 10 |
| `charged_group` | `step_main` | `step_main` |
| `positive_tags` | `["H200"]` | `["H200"]` |
| `preemptible` | false | false |
| `num_rollout` | 100 | 100 |
| `submitted` | false | false |
| `tasks.student` | cpu64, gpu8, mem_gb512, replica1, host_network=true, gang_start=false, critical=true | 相同 |
| `tasks.teacher` | cpu16, gpu2, mem_gb128, replica1, host_network=false, gang_start=false, critical=false | 相同 |

两种角色均保留 `custom_resources=[]` 和原有 `QWEN35_ROLE`。输出的 `image`、`mounts`、`local_mount` 精确等于 source。输出 `worker_command` 精确保留原有 Python/CUDA environment 和角色转发，只将 config path 换为 H200 manifest；A/B 各自保留相应 `--pair`。

精确 structural diff 命令与实际 PASS 输出：

```bash
python3 -B - <<'PY'
import json
import platform
from pathlib import Path
root = Path('task_memory/task_2026-11-06_qwen35_three_pairs')
source = json.loads((root / 'training_config.json').read_text())
target = json.loads((root / 'training_config_h200.json').read_text())
expected = json.loads(json.dumps(source))
expected.update(charged_group='step_main', gpu_tag='H200', capacity_gpus=32)
del expected['pairs']['C']
assert target == expected
assert target.keys() == source.keys()
changes = [(key, source[key], target[key]) for key in source if key != 'pairs' and source[key] != target[key]]
assert changes == [('charged_group', 'codesign', 'step_main'), ('gpu_tag', 'H800', 'H200'), ('capacity_gpus', 128, 32)]
assert tuple(target['pairs']) == ('A', 'B')
assert target['preemptible'] is False and source['preemptible'] is False
counts = {}
for pair in target['pairs']:
    assert target['pairs'][pair] == source['pairs'][pair]
    student = target['pairs'][pair]['student']
    teacher = target['pairs'][pair]['teacher']
    assert student['tp_size'] == teacher['tp_size'] == student['engine_gpus'] == 2
    assert (student['nodes'], student['gpus_per_node'], teacher['nodes'], teacher['gpus_per_node']) == (1, 8, 1, 2)
    counts[pair] = sum(target['pairs'][pair][role]['nodes'] * target['pairs'][pair][role]['gpus_per_node'] for role in ('student', 'teacher'))
assert counts == {'A': 10, 'B': 10}
assert sum(counts.values()) == 20 <= target['capacity_gpus'] == 32
assert source['pairs']['C']['student']['memory_gb_per_node'] == 1536
print('PYTHON', platform.python_version())
print('STRUCTURAL_DIFF_PASS', json.dumps(changes))
print('EXCLUDED_PAIR_C_PASS; ALL_OTHER_ROOT_FIELDS_AND_A_B_NESTED_VALUES_EXACT')
print('NON_PREEMPTIBLE_PASS; GPU_COUNTS_PASS', json.dumps(counts), 'combined=20 ceiling=32')
print('SOURCE_C_PRESENT_PASS; C_STUDENT_MEMORY_UNCHANGED=1536')
PY
```

```text
PYTHON 3.10.6
STRUCTURAL_DIFF_PASS [["charged_group", "codesign", "step_main"], ["gpu_tag", "H800", "H200"], ["capacity_gpus", 128, 32]]
EXCLUDED_PAIR_C_PASS; ALL_OTHER_ROOT_FIELDS_AND_A_B_NESTED_VALUES_EXACT
NON_PREEMPTIBLE_PASS; GPU_COUNTS_PASS {"A": 10, "B": 10} combined=20 ceiling=32
SOURCE_C_PRESENT_PASS; C_STUDENT_MEMORY_UNCHANGED=1536
```

进一步比较 **source 和 H200 两份 config 的实际原生输出**，不是手写 submit spec：

```bash
python3 -B - <<'PY'
import json
import subprocess
import sys
from pathlib import Path
root = Path('task_memory/task_2026-11-06_qwen35_three_pairs')
source_path = root / 'training_config.json'
h200_path = root / 'training_config_h200.json'
source_bytes = source_path.read_bytes()
source = json.loads(source_bytes)
h200 = json.loads(h200_path.read_bytes())
for pair in ('A', 'B'):
    def dry_run(path):
        command = [sys.executable, '-B', 'tests/manual/agent_opd/submit_qwen35.py', '--config', str(path), '--pair', pair, '--dry-run']
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        assert not result.stderr, result.stderr
        return json.loads(result.stdout)
    old, new = dry_run(source_path), dry_run(h200_path)
    expected = dict(old)
    expected.update(charged_group='step_main', positive_tags=['H200'])
    expected['worker_command'] = old['worker_command'].replace(str(source_path.resolve()), str(h200_path.resolve()))
    assert new == expected
    assert new['preemptible'] is False and new['submitted'] is False
    assert new['requested_gpus'] == 10 and new['num_rollout'] == 100
    assert tuple(new['tasks']) == ('student', 'teacher')
    assert new['tasks']['student']['gpu'] == 8 and new['tasks']['teacher']['gpu'] == 2
    print(f'NATIVE_DRY_RUN_{pair}_PASS exit=0 requested_gpus=10 num_rollout=100 submitted=false')
    print(f'NATIVE_OUTPUT_DIFF_{pair}_PASS only=charged_group,positive_tags,config_path_in_worker_command')
assert source_path.read_bytes() == source_bytes
assert h200_path.read_bytes() and json.loads(h200_path.read_bytes()) == h200
print('SOURCE_CONFIG_BYTE_PRESERVATION_PASS')
print('H200_CONFIG_PRESERVATION_PASS')
PY
```

```text
NATIVE_DRY_RUN_A_PASS exit=0 requested_gpus=10 num_rollout=100 submitted=false
NATIVE_OUTPUT_DIFF_A_PASS only=charged_group,positive_tags,config_path_in_worker_command
NATIVE_DRY_RUN_B_PASS exit=0 requested_gpus=10 num_rollout=100 submitted=false
NATIVE_OUTPUT_DIFF_B_PASS only=charged_group,positive_tags,config_path_in_worker_command
SOURCE_CONFIG_BYTE_PRESERVATION_PASS
H200_CONFIG_PRESERVATION_PASS
```

### Source inspection: genuine launch blockers, not kernel failures

| Inspected path/symbol | Observation | Consequence |
| --- | --- | --- |
| `tests/manual/agent_opd/qwen35_pair_worker.py:91–100`, `_allocation` | Both roles reject any GPU name not containing literal `H800`; does not use manifest `gpu_tag`. | Actual H200 student and teacher fail before model startup. Parent must correct this guard before formal submission. |
| `tests/manual/agent_opd/run_qwen35_opd.py:309–313`, `_run` | Independently requires literal `H800` for the student. | Fixing only the outer worker does not unblock H200 training. |
| `tests/fast/test_qwen35_pair_worker.py:360–370` | Existing fixture explicitly expects H200 rejection under its H800 allocation. | Preserve wrong-hardware rejection while extending the selected hardware case; do not merely remove validation. |
| `qwen35_pair_worker.py:119–120`; `run_qwen35_opd.py:205,231–233` | BF16, FA3, Triton linear-attention prefill, FLA/TE training and fused logprobs. Repository CI rule identifies FA3 as Hopper-only. | H200 is Hopper; no generation-level incompatibility found in these settings. This is source inspection, not actual pinned H200 kernel execution. |
| `run_qwen35_opd.py:130–134,240–243` | Allocation/divisibility checks derive from provided GPU count/TP/engine size; student remains one8-GPU node. | No new topology or optimizer assumption is introduced by the JSON delta. |
| `submit_qwen35.py:61–73` | Dry-run checks only this pair's ceiling and returns before StepMind imports/auth/submission or worker execution. | PASS does not detect either H800 guard or enforce total live session usage. Parent must account for all concurrent H200 allocations, including auxiliaries. |

### Reused pinned lifecycle/launcher evidence

Existing [sample-boundaries report](test_report_2026-11-07_sample_boundaries.md) lines83–93 records job `exp-1107-084523-486765`, selected image, Python3.12.16, compatibility `LD_LIBRARY_PATH`, `CUDA_VISIBLE_DEVICES=''`, plugin autoload enabled:

```bash
/opt/sglang/bin/python3 -B -m pytest -p no:cacheprovider \
  tests/fast/test_qwen35_sample_lifecycle.py tests/fast/test_qwen35_opd_launcher.py \
  -q --basetemp=/var/tmp/qwen-samples-exp-1107-084523-486765/pytest --tb=short
```

Expected76 cases; retained [raw log](evidence/sample-boundaries-exp-1107-084523-486765.log) line242: **76 passed,54 warnings,11.88s; PASS**. This report and raw final line were inspected, not rerun. Existing success/timeout/failure/later-success attempts, deadlines, identity records and native refill-eight remain applicable to this JSON-only delta. Earlier formal restoration/baseline evidence is retained in [publication restore report](test_report_2026-11-07_publication_restore.md) and [plan.md](plan.md); no unrelated suites or model probes were repeated.

### Parent device-contract correction and verification

The two H800 literals were replaced by one shared `_gpu_devices(gpu_type, count)` check in `run_qwen35_opd.py`. The pair worker reads the existing `config['gpu_tag']`, passes it explicitly as required `--gpu-type` to the student CLI, and both stages retain GPU-name/count rejection. No hardware default, alternate model/kernel/optimizer path or native training argument was added. H800 remains accepted when requested, and H200 is rejected for an H800 allocation and vice versa. Existing H800 C submissions obtain the same explicit value from their original manifest.

Exact local commands (repo cwd, `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`, Python `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, no conda):

```bash
python -B -m pytest -q -o addopts='' -p no:cacheprovider \
  tests/fast/test_qwen35_pair_worker.py \
  -k 'selected_pair_scope_and_native_commands or allocation_is_checked_against_selected_hardware_and_role' --tb=short
python -B -m pytest -q -o addopts='' -p no:cacheprovider \
  tests/fast/test_qwen35_pair_worker.py tests/fast/test_qwen35_opd_launcher.py \
  -k 'not resolved_sglang' --tb=short
```

The first tool invocation timed out at120s with no output; no remaining pytest process was found. Re-executing the first selection through `pytest.main` with a20s faulthandler deadline completed before that deadline: expected RED, **7 failed/1 passed/23 deselected,1.81s**, showing absent GPU-identity propagation and H200 rejection. This does not establish the initial tool timeout's cause. After correction the second command gives **80 passed/12 skipped/1 failed,30.32s**. The failure is the already-known local SGLang parser missing `--sglang-enable-prefill-weight-versions`; no assertion or production flag was removed. The new hardware/role/command checks pass. Full affected files are submitted to the fixed image in a0GPU `step_main` job with `CUDA_VISIBLE_DEVICES=''` and plugin autoload enabled; its result remains pending.

Raw local logs: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-h200-test-startup-trace.log` and `qwen-h200-device-guards-green.log`. Existing lifecycle success/timeout/failure/recovery proof above remains applicable. The hardware guard change does not alter sample handling. Formal H200 GPU identity, baseline, restored publication, actual updates and capacity remain unverified until the jobs run.

At09:31:54Z the supplementary pinned job `exp-1107-172750-953553` isStarting, with personal identity/local NFS source verified and native admission at09:27:59Z. The changed hardware/CLI cases already pass locally and the sole old-parser incompatibility has unchanged pinned evidence; this repeat does not block formal queue entry. No pinned rerun PASS is claimed before it finishes. C is stillPending with no active worker, so the required argument change has not raced an already-loaded C command. The parent stages only the verified migration files before A/B submission.

Final supplementary result: **90 passed/3 failed,14.38s**, jobFailed. The changed hardware/CLI checks and native parser pass in the exact image. All failures are `test_baseline_native_scoring_needs_no_optimizer[True-{A,B,C}]`: the manually assembled toy actor bypasses native initialization, lacks `with_ref`, and now reaches `_switch_model` through the previously repaired scoring restore. Native `_init_common` sets both role flags (`miles/ray/train_actor.py:204–205`); Megatron init calls it (`actor.py:164`). The actual repaired B baseline already passed that production route. This is separate fixture maintenance, not evidence of a missing formal runtime field; no production fallback is added. Raw evidence: `evidence/h200-launch-contracts-exp-1107-172750-953553.log:8–160,335`. The original failed result stays retained while the fixture owner corrects the test independently.

## 2. 偏离检测

**结论：** 未偏移，正常推进。**检测窗口：** 本次 scoped manifest 子任务开始至上述验证完成｜**当前前沿：** P3-A/B 最小 hardware guard 修正和并行正式提交，P3-C 独立保留。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅 JSON、原生 dry-run、exact diff 和已有证据复用；没有扩展 harness/suites。 |
| D2 细节反复重试 | CLEAR | 所有准备验证通过；没有对同一失败进行参数试探或重复修复。 |
| D3 支线问题修补 | CLEAR | 硬件检查直接阻塞 P3-A/B；已通知父会话，未越权编辑代码。 |
| D4 可并行任务停滞 | CLEAR | 本次 dry-run 并行；平台提交归父会话，C 不作为 A/B dependency。 |
| D5 超范围镀金 | CLEAR | 严格只新增两份获授权 artifact，无新 loader、依赖或功能。 |
| D6 分析空转 | CLEAR | 一轮源码检查找到两个确定阻塞，并交付验证后的 manifest。 |
| D7 路线违背 | CLEAR | 遵守 D18；不改变模型、数学设定、预算和 C。 |

**文档检查：** S1–S6 均未发现明显缺陷；父会话已将 D18 和 H200 frontier 写入 requirements/plan。新发现的两处启动阻塞由 P3-A/B 拥有，不是另建任务的理由。**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/plan 合理，无需改动。**需停止的偏离行为：** 无。

**接下去的路线：**
1. 父会话以配置拥有的硬件选择修正上述两处 guard，并完成针对这些改动的必要验证；保留 GPU 数量与错误硬件拒绝。完成标志：H200 正确设备不再被 H800-only guard 拒绝，原 C/H800 行为不变。
2. 并行：P3-A ‖ P3-B；使用本 manifest，由 `/data/ycfeng` 的 long-lived personal launchers 提交正式100-position runs。完成提交前核对配额、creator、image、source mounts 和32卡 session/task ceiling；不等待独立 output-retention investigation。
3. 实际运行内验证 H200 identity/driver/memory、baseline、restore、first update、后续 scoring capacity、D8、sample/update accounting 和 final HF reload。C 现有 H800 job/launcher 继续独立推进。

未完成的是实际 H200 runtime，不是 manifest：没有 H200 allocation/readiness、numerical acceptance、OOM 修复成效、successful-update count 或 final HF artifact 的本次测量。`capacity_gpus=32` 是预算上限，不是当前空闲配额或容量保证。

## 4. 最值得关注的 3 点

1. Manifest preparation **PASS**：仅三处 scalar 修改并排除 C；A/B 原生 dry-run 均10卡、合计20卡、不可抢占、100 positions、`submitted=false`。
2. 正式启动前必须修正两个 literal-H800 guards；这是确定的源码阻塞，不是 H200 kernel 或 GPU memory 的实测失败。
3. 复用既有76-case lifecycle/launcher PASS 和 restoration evidence；修正最小启动阻塞后优先并行正式提交，保持原数学设定、D17/D15/D16 预算和真实 runtime 验收边界。
