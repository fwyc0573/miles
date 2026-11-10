## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Resolve the Standards naming Nit with a local `param_group` rename; verify AST equivalence under that rename. |
| 2026-11-10 | Implement early native optimizer-state initialization and record CPU ordering/restoration regressions under D38. |

# Native optimizer-state initialization

TaskID: `profile-native-optimizer-init-fix-20261110`.

**Result:** the scoped Miles correction and CPU regressions are complete. Corrected native formal execution remains the primary agent's responsibility; neither this report nor the controlled diagnostic proves the failed full-model allocation owner.

## Gain and existing gap

The primary accepted the existing native mechanism from diagnostic `exp-1110-160647-698733`: job/replica Succeeded, exit0/restart0,72 seconds. Both cases used native TE FusedAdam and its factory-created `init_state_fn`, with exact TMS0.0.10 preload. Factory source: `/root/Megatron-LM/megatron/core/optimizer/__init__.py`, SHA256 `2bad8558ca6b818406186fd9df6b052bb77ae82c9336d340e1c6e3ed71d9e66a`, factory line451, initializer line589. See `evidence/tms-allocator-20261110/exp-1110-160647-698733/early_moments.json` and `evidence/tms-allocator-20261110/native-verification.json`.

| Observed controlled case | Late initialization | Early initialization |
| --- | ---: | ---: |
| Total moments |134217728 bytes |134217728 bytes |
| CUDA allocated |201327104 bytes |201327104 bytes |
| CUDA reserved |1142947840 bytes |203423744 bytes |
| Pause RSS delta |1142812672 bytes |203436032 bytes |

Late moments occupied the original1GiB transient segment and retained896MiB inactive. Early moments occupied separate64MiB segments. Backup, restore and pointer checks passed; both native steps reached1. RSS is an observed host change, not a native backup-byte counter. `formal_allocation_owner_proven` remains false.

The gain is to allocate persistent native optimizer state before scoring/training transient allocations can supply large cached segments for that state to retain during TMS sleep. Miles already invoked this callback when **resetting** state, but that path clears moments/step and cannot be used after a true checkpoint restoration. No new allocator setting, flag, model dispatch, manual production Adam allocation, disk offload, timeout or failure fallback is introduced.

## Callable and seam

- `miles/backends/megatron_utils/optimizer_utils.py:6-15`: `initialize_optimizer_state(optimizer: MegatronOptimizer) -> None` traverses the existing `ChainedOptimizer.chained_optimizers` wrapper structure, including nested chains, and invokes exactly `optimizer.init_state_fn(optimizer.optimizer, optimizer.config)` on non-stub leaves with a callback. A direct `DistributedOptimizer` reaches the same leaf call. State allocation and preservation remain owned by the native callback; Miles does not clear state or write step counters.
- The existing `USING_PYTORCH_OPTIMIZER` exclusion is preserved. PyTorch's initializer also needs a per-parameter step; initializing only native moments would interfere with its empty-state detection. Native errors propagate unchanged.
- `optimizer_utils.py:44` reuses the same callable in the existing reset operation, after that operation's explicitly requested clearing. Reset semantics are unchanged.
- `miles/backends/megatron_utils/actor.py:447-472`: shared `_load_state_core` completes checkpoint/model/optimizer/scheduler restoration, restores actor weights after auxiliary checkpoints, clears loading caches, and then initializes state at line470. This is before either actor/critic initial sleep and before the shared load returns to subsequent scoring/training. Initial setup and reload already use this shared seam.
- The call is limited to `offload_train`, with an optimizer present, and excludes the existing streaming-to-disk owner. That owner binds an independent canonical moment store; this correction must not allocate a second GPU copy. No new supported wrapper category or generic attribute-based traversal is introduced.
- Existing scheduler restoration and any deliberate fresh-run reset occur as before. The added operation itself does not modify loaded moments, optimizer step, gradients, model weights or scheduler state.

## Verification environment

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`.

Python: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`,3.12.13, Torch2.11.0+cu130. All executed tensors and updates were CPU-only. No GPU, platform, SSH, network or delegation operations were performed in this implementation phase.

The focused tests execute the actual Miles declarations and shared actor load method against the external Megatron wrapper ABI, avoiding CUDA-only imports. The test callback models the accepted native empty-state contract; it is not evidence of executing the pinned native callback or real distributed wrappers locally. Loaded-history checks use a real CPU `torch.optim.Adam`, actual `state_dict` restoration and the existing comparison/update assertions in `test_optimizer_utils.py`.

## Commands and observed results

### Ordering RED -> GREEN

The first test was written before either production edit. The unchanged actor returned with no initialization before simulated initial sleep: expected `load, auxiliary, actor, clear, initialize, sleep`; actual `load, auxiliary, actor, clear, sleep`.

```bash
timeout 60s env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts='' -q tests/fast/backends/megatron_utils/test_optimizer_state_initialization.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-native-optimizer-init-red
```

**RED:**1 failed,0.31s, exit1. After the minimal helper/call-site change, the same test with `--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-native-optimizer-init-green` passed: **GREEN**,1 passed,0.21s, exit0.

### Affected CPU regressions

```bash
timeout 60s env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts='' -q -rs tests/fast/backends/megatron_utils/test_optimizer_state_initialization.py tests/fast/backends/megatron_utils/test_actor_state_load_call_sites.py tests/fast/backends/megatron_utils/test_optimizer_utils.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-native-optimizer-init-affected-final
```

**PASS:**18 passed,20 skipped,0.91s, exit0. The10 new behavioral checks cover fresh zeroed moments before sleep, actual loaded state/step preservation, unchanged next CPU update, storage identity on repeated initialization, direct/nested wrappers, non-offload/streaming/no-optimizer exclusions, PyTorch lazy initialization, stubs/absent callbacks, native-error propagation, and unchanged explicit reset. The8 actor source checks verify the actual import/callable wiring and shared load ordering. The20 existing optimizer utility tests skip because the CPU environment has no `megatron`; they are not counted as passing. Two existing SWIG deprecation warnings were emitted.

A first expanded run also selected `test_optimizer_state_reset.py` and exited2 at collection because it directly imports `megatron.core.optimizer.emerging_optimizers`. The exact command was the regression command above with that fourth file, without `-rs`, and `--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-native-optimizer-init-regressions`. That unrelated Muon reset implementation was not changed; no dependency workaround was added. A later AST check initially compared actor and critic branches across each other (288 <270), then was corrected to compare each branch's load and sleep; production behavior did not change.

### Scoped static checks

`git diff --check`: **PASS**, no output. Each of the four changed Python files was parsed with `ast.parse` and compiled with `compile(source, path, "exec")`: **PASS**. Both focused test files have no lines above119 characters. Commands used the system `python3 -B` and in-memory compilation, without writing bytecode.

`ruff`, `black` and `isort` are unavailable on PATH and in the CPU environment; no package installation or lint claim was made. A separate pre-test availability attempt to import Megatron with `/data/ycfeng/envs/verl-agent-opd-megatron-sglang/bin/python -B` under `timeout 60s` exited124 without output. No repeated import diagnosis was attempted.

### Standards naming correction

The Standards reviewer identified one manual naming Nit in the new test callback: local `group` conflicted with `.agents/rules/pool-cell-worker-names.md`. It is now `param_group`; the upstream `optimizer.param_groups` API is retained. A system-Python3.10.6 AST comparison against `git show edd3be00:tests/fast/backends/megatron_utils/test_optimizer_state_initialization.py`, transforming only `ast.Name.id` from `group` to `param_group`, produced an identical tree. In-memory compilation and scoped `git diff --check` passed. This cosmetic follow-up does not claim another CPU or native run.

## Remaining limits and handoff

The primary must verify the corrected real training path with its pinned Megatron image, TP2/DP4 native FusedAdam and TMS offload: initialization before first transient use, loaded-state semantics where applicable, actual train -> sleep -> restore/weight-update -> next train, and native terminal/host-memory evidence. This implementation did not execute real distributed wrappers, a native loaded FusedAdam checkpoint, or the full model. The accepted controlled diagnostic establishes the allocation-order mechanism, not that these moments owned the retained segment in the historical formal failure.

Only the two existing modules, the two focused fast files and this report are owned by this change. Existing untracked evidence and all primary-owned task/config/probe files are preserved. The commit accompanying this report contains only these five owned files.

## 1. 规划完成情况

**汇总：** PASS2｜BLOCKED/FAILED/SKIPPED0｜TODO1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 最小 native 初始化修正 | PASS | 两个现有模块；没有新增运行配置 |
| CPU 顺序、恢复与报告 | PASS |18 PASS；20 skip 明确区分 |
| Corrected native formal 验证 | TODO | primary 所有；本次未执行 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。窗口：本次 implementation scope update 至 CPU 验证完成。当前前沿：提交 owned files 后交回 primary。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | source-execution 测试只解决本次 CPU 验证；缺包后未扩展工具链 |
| D2 细节反复重试 | CLEAR | 单次 import timeout；仅修正已诊断的分支比较测试 |
| D3 支线修补 | CLEAR | 没有修复 Muon 或环境依赖 |
| D4 并行停滞 | CLEAR | 用户禁止进一步 delegation，GPU 由 primary 所有 |
| D5 超范围镀金 | CLEAR | 没有新 flag、allocator tuning 或通用框架 |
| D6 分析空转 | CLEAR | 已完成 production 修改和 RED -> GREEN |
| D7 路线违背 | CLEAR | 遵循 D38 native 证据与 full-model 未证明边界 |

**文档检查：** S1–S4、S6 未发现本 slice 的明显缺陷。S5：primary 所有的 `plan.md:39,90,96` 与 `tickets/04-a-full.md:28-30` 仍描述诊断/修正未选择；`progress.md:89` 和本次明确 scope update 已记录诊断 PASS 及实施授权。归因：无执行偏离。

## 3. 纠正建议

**分支：** B，primary 更新现阶段状态，不改变验收标准。

**文档更新：** primary 在交接时更新上述 plan/ticket 当前状态，记录本提交及 CPU 限制；原始历史与正式200-update 条件保留。本 agent 无权编辑这些文件。

**需停止的偏离行为：** 无。

**接下去的路线：** 提交五个 owned files -> primary 接受修正并执行其 native formal 验证。不得把当前 CPU PASS 或机制诊断标为 full-model root-cause proof。

## 4. 最值得关注的 3 点

1. 初始化调用位于 shared restoration/cache-clear 后、首次 sleep/forward 前。
2. Loaded moments、step、scheduler 和 native failure 语义保持；CPU 验证与 native 限制分别记录。
3. Full-model allocation owner 与 corrected formal 验证仍未证明，由 primary 继续。
