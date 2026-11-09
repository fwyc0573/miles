## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record the positive student-node generalization, four-node CPU lifecycle evidence, baseline limitations, and scoped checkpoint. |

# Four-Node Student Rollout Preparation

Task ID: `profile-h800-four-node-20261109`.

## Scope and Result

Worktree: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`.

The delegated request selects four student nodes with eight H800 GPUs each, an unchanged one-node eight-GPU TP4/DP2/CP1 trainer, 32 rollout GPUs with eight TP4 engines, and a separate four-GPU teacher: 36 allocated GPUs in total. The primary owns the mixed rollout configuration, parent integration, and native execution.

The existing `student_nodes` setting now accepts a positive integer instead of only 1/2. No alternate launch mode, wrapper, core change, resource submission, or historical length-constant change was introduced. The one-node default and existing two-node lifecycle remain covered.

Changed files:

- `tests/manual/agent_opd/run_qwen35_opd.py`: remove the parser's 1/2 choices, validate positive node counts, and permit positive integer counts at the existing `_run` boundary. Trainer configuration remains `num_nodes=1`.
- `tests/manual/agent_opd/qwen35_pair_worker.py`: accept positive integer student counts and make the head supervise every nonzero student rank's existing status file. Peers still supervise only the driver's completion file.
- `tests/fast/test_qwen35_pair_worker.py`: extend existing tests and fixtures for four-node H800 lifecycle, all peer ranks, exact registration totals, failure propagation, signal cleanup, and argv/resource contracts.
- This report only; shared `progress.md`, `summary.md`, `requirements.md`, and `plan.md` were not edited by this slice.

## Environment

- Linux; CPU-only virtual environment `/data/ycfeng/envs/miles-agent-opd-cpu`.
- Python 3.12.13; pytest 9.1.1; installed SGLang 0.5.23. No conda environment was used.
- `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`; `PYTHONDONTWRITEBYTECODE=1` for test execution.
- Ray startup, GPU inspection, and training submission boundaries use the existing CPU fixtures. Cancellation tests use real local Python children, not Ray/GPU/RJob workers.
- `submit_qwen35._task_specs` was evaluated as a pure payload constructor; no platform API or RJob call occurred.

## Commands and Observed Results

All commands ran from the worktree above.

### Baseline before code changes

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_qwen35_pair_worker.py tests/fast/test_qwen35_opd_launcher.py -q -p no:cacheprovider
```

Observed: **104 passed, 12 skipped, 1 failed**, 33 warnings, 9.57 s. All 55 paired-worker tests passed. The failed test was `test_native_parser_accepts_sglang_and_custom_mis_flags`, with this exact assertion difference:

```text
Extra items in the left set:
'--sglang-enable-prefill-weight-versions'
```

This occurred before the node-count changes: the locally installed SGLang parser does not register the launcher's existing prefill-version flag. The 12 skipped cases require native Megatron scheduler source absent from this CPU environment. Neither the flag nor the dependency/parser was changed or bypassed.

### Expanded paired-worker tests

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_qwen35_pair_worker.py -q -p no:cacheprovider
```

Observed: **122 passed**, 26 warnings, 2.24 s. PASS: existing one/two-node behavior and added count/lifecycle cases.

### Related launcher regression

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_qwen35_pair_worker.py tests/fast/test_qwen35_opd_launcher.py -q -p no:cacheprovider -o 'addopts=--strict-markers --durations=5' 2>&1 | tee /data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-h800-four-node-20261109-pytest.log
```

Observed: **171 passed, 12 skipped, 1 failed**, 44 warnings, 13.02 s. The only failure and all skips match the baseline limitations above; no new failure appeared. Overall combined-suite status is **FAIL with a pre-existing CPU dependency limitation**, not a clean full-suite pass. The log retains the unmodified failing assertion.

### Final paired-worker check with explicit H800 four-node fixture

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_qwen35_pair_worker.py -q -p no:cacheprovider -o 'addopts=--strict-markers --durations=5' 2>&1 | tee /data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-h800-four-node-20261109-final-pair.log
```

Observed: **122 passed**, 26 warnings, 2.71 s. PASS. The shared lifecycle fixture now explicitly tests `two-node-H200` and `four-node-H800`; its GPU inspection responses remain CPU fixtures, not hardware observations.

### Static checks

```bash
PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -c 'from pathlib import Path; paths = [Path("tests/manual/agent_opd/run_qwen35_opd.py"), Path("tests/manual/agent_opd/qwen35_pair_worker.py"), Path("tests/fast/test_qwen35_pair_worker.py")]; [(compile(path.read_text(), str(path), "exec"), print("PASS compile", path, "lines", len(path.read_text().splitlines()))) for path in paths]'
git diff --check -- tests/manual/agent_opd/run_qwen35_opd.py tests/manual/agent_opd/qwen35_pair_worker.py tests/fast/test_qwen35_pair_worker.py task_memory/task_2026-11-09_profile_h800_preparation/test_report_2026-11-09_four_node_rollout.md
```

Expected: all three files compile without bytecode writes; no whitespace errors. Observed: **PASS** for compilation and scoped diff checking. No Ruff check is claimed: Ruff is absent from this CPU environment.

## Acceptance Evidence

| Contract | Expected | Observed | Result |
| --- | --- | --- | --- |
| Positive student count | Existing setting accepts 1/2/4 and is not another whitelist | Config/allocation/argv cases accept 1, 2, 3, 4, 5; invalid types, zero and negative counts fail | PASS |
| Four-node registration | Four distinct addresses, each `ray start --num-gpus 8`; only one head | All four ranks traverse native `_run`; captured starts contain 8 GPUs each and one `--head` | PASS, CPU boundary |
| Exact readiness | Wait for exactly four nodes and 32 GPUs before one trainer submission | Simulated snapshots with 3 nodes, 5 nodes, or 31 GPUs are rejected; 4 nodes/32 GPUs allow submission at simulated second 6 | PASS |
| Incomplete startup | No trainer submission; driver failure completion is published | Missing-node snapshots reach the existing startup timeout with zero submissions | PASS |
| Trainer allocation | One trainer launch on an eight-GPU node, TP4/DP2/CP1 | Callback count is one; backend config stays one node; argv has actor nodes 1, GPUs 8, TP4, CP1 | PASS, CPU boundary |
| Peer completion ownership | Ranks 1/2/3 write only their own status; only rank 0 releases teacher | All peer returncode cases preserve the global driver completion owner; teacher ignores successful peer status files | PASS |
| Failure propagation | Head observes any peer failure; peers observe driver failure | Rank 1/2/3 failure cases stop the supervised child; real CPU children terminate with SIGTERM | PASS |
| Signal/cleanup behavior | Existing SIGTERM status, cleanup and restored handler remain unchanged | Four-node case exits 143, records failure, restores prior handler and removes only its owned temporary directory | PASS |
| Native platform environment | No new NCCL/RDMA overrides | Existing checks preserve platform NCCL values; all-rank preflight preserves `NCCL_SOCKET_IFNAME`, `NCCL_IB_HCA`, `UCX_TLS` | PASS for inspected/tested path |
| Resource payload | Student 4×8 plus teacher 1×4 = 36 GPUs | Existing pure payload constructor returns student replicas 4/GPU 8, teacher replicas 1/GPU 4, student RDMA resources retained | PASS |

## Runtime Assumptions and Unverified Work

- `student_nodes` controls Ray allocation and rendezvous only. It does **not** independently set `rollout_num_gpus=32` or create the mixed engine configuration. The primary must supply those through the existing native training builder and SGLang configuration: two colocated TP4 engines and six dedicated TP4 engines. This slice does not change the historical Qwen 100-update recipe's rollout/length constants.
- Actual H800 memory capacity, placement on the first node, eight engine construction, distributed weight transfer, RDMA/NCCL behavior, teacher readiness, training business outputs, and platform terminal state are **unverified**. CPU fixtures are not native execution evidence.
- All replicas must receive the same selected configuration, matching `KUBEBRAIN_REPLICA_TOTAL=4`, unique rank values 0–3, distinct physical node addresses, eight visible GPUs each, and the mounted shared rendezvous workspace. The existing bounded startup and driver-owned completion files remain required lifecycle markers.
- The existing reused warmup cluster timeout message still says “two-node”; its condition is count-driven and tested for four nodes. No unrelated diagnostic wording change was made to `rjob_warmup.py`.
- Primary integration and formal GPU execution remain pending and retain the parent source-input, scientific and merge gates. No other worktree, job, or platform system was touched.

# Scoped Progress Checkpoint

## 1. 规划完成情况

**汇总：** PASS 1｜BLOCKED/FAILED/SKIPPED 1｜TODO 2

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 本委派：推广现有节点设置并验证四节点生命周期/argv | PASS | 122 项 paired-worker 测试通过；本报告记录命令、原有失败和运行限制。 |
| 本委派：提交限定文件并交接 primary | TODO | 验证完成，等待 Git 提交 hash 和文件清单。 |
| Parent Plan 2/3：真实 mixed config 和 native 验证 | TODO | 由 primary 所有；本切片没有其完成证据，也未执行 GPU/platform 操作。 |
| Parent Plan 4：父分支整合 | BLOCKED | requirements/plan 指定的父任务 upstream/merge gate 保留。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本委派开始至本次验证｜**当前前沿：** 限定文件提交和交接。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅扩展直接拥有的 CPU 测试；达到四节点验收后停止扩大测试。 |
| D2 细节反复重试 | CLEAR | 一次节点/监督器实现后 122 项测试通过；没有修补无关 parser 失败。 |
| D3 支线问题修补 | CLEAR | 原有 SGLang/Megatron 限制只记录，不修改依赖、core 或 launcher flag。 |
| D4 可并行任务停滞 | CLEAR | length launcher 和 primary config 明确独立所有权；本切片未占用其文件。 |
| D5 超范围镀金 | CLEAR | 按请求沿用正整数 count-driven 路径，无新 launch mode、wrapper 或资源上限。 |
| D6 分析空转 | CLEAR | 一次 call-path 检查确定沿用 Ray lifecycle，并产生可提交代码和测试。 |
| D7 路线违背 | CLEAR | 未编辑禁改文件、历史长度常量或父分支；没有 RJob 调用。 |

**文档检查：** S1–S6 均未发现明显缺陷；当前委派补充 Parent Plan 2/3 的 CPU 生命周期切片。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 本切片：提交三项源码/测试文件与本报告 → 完成标志：准确 commit hash、diff 清单和验证限制可交接。
2. 并行：primary mixed config/payload 验证 ‖ parent input/checker/audit 整合 → 完成标志：满足既定 parent gate 后执行 native 验证，不用 CPU fixture 代替 GPU 证据。

## 4. 最值得关注的 3 点

1. 每个非零 rank 的失败必须被 head 读取；只放宽 1/2 whitelist 并不足以支持四节点。
2. 配对 CPU 测试通过；完整 launcher 回归仍有同一个已复现的本地 parser 失败和 12 项 Megatron 跳过。
3. 节点数不自动创建 32-GPU mixed rollout；真实八引擎配置和 native 执行仍由 primary 完成。
