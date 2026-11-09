## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record T02-CAPACITY-REPLAY implementation, native CLI registration, CPU verification and remaining native gates. |

## 1. 规划完成情况

**汇总：** PASS 2｜BLOCKED/FAILED/SKIPPED 0｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| T02-CAPACITY-REPLAY：单个 saved bank 输入 seam | PASS | 只替换既有 `_generate` acquisition hook；未修改 `swe_replay.py`。 |
| CPU payload/ACK/真实 argv registration | PASS | 最终53 tests PASS，其中新文件14 tests；见下方命令和XML。 |
| 真实256-turn native red/green及两次更新 | TODO | 父任务负责GPU执行；本子任务未读取cloud bank、提交作业或取得native成功更新。 |

Deliverables:

- `tests/manual/agent_opd/probe_swe_capacity.py`: `CapacityReplay`, one-path `SavedBankConfig`, original acquisition-JSONL validation, and the delegating optimizer/protocol hook.
- `tests/fast/test_swe_capacity.py`: deterministic256-slot CPU fixture, private materialization across a skip and two successful ACKs, original status/source/tokens/mask/behavior/teacher/version preservation, formal/schedule/teacher/seal rejection, original-file protection, and refusal to silently train255 slots after source mismatch.
- This report and `evidence/t02-capacity-replay-verified.xml`.

Exact native integration fields:

```text
--rollout-function-path tests.manual.agent_opd.probe_swe_capacity.CapacityReplay
--custom-megatron-optimizer-step-hook-path tests.manual.agent_opd.probe_swe_capacity.optimizer_step
--swe-saved-bank-path /mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/capacity-smoke/r256/student/A/exp-1108-174749-557599/training/bank_0.jsonl
```

Keep existing `score_teacher`, reward postprocessor and TIS hooks. `SavedBankConfig` declares only `swe_saved_bank_path`; the existing teacher hook owns `SweReplayConfig`, which the real rollout custom-config composition includes. The optimizer delegate uses the same existing config class. No partially shared flag schema, core parser relaxation, duplicate replay flags or debug-load flag is introduced. The smoke contract is explicitly `r256`,256 slots, two bank uses and two successful updates. The parent-owned launcher must emit these three fields; this subtask did not edit `run_swe_opd.py` or its JSON configuration.

The reader accepts the original `acquisition_start`/`slot_finished`/`acquisition_sealed` JSONL, including each native `Sample` and its frozen `teacher_scoring.identity`. It does not accept a train-data dump or create missing masks/targets. Completion-order receipts return in the original sealed slot order. Existing `CanonicalTrajectory.seal/materialize`, native source lifecycle, pending/result ACK, successful/skip counters and D7 behavior remain authoritative. Original acquisition metadata/status/seed/version spans survive; `swe_saved_bank_path` is added only as training provenance. Loaded source payload references are removed as acquisition consumes each slot; the acknowledged bank is released by the existing lifecycle.

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, Torch2.11.0+cu130, pytest9.1.1; CPU execution only. Pytest temporary files were under `/data/ycfeng/tmp/pytest-of-brainpp/`. No GPU/platform/cloud/SSH/auth/commit operation occurred.

Verification command:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_capacity.py tests/fast/test_swe_replay.py -q --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t02-capacity-replay-verified.xml
```

Expected: every captured field remains equal, a skipped ACK preserves visit1, successful ACKs commit visits1/2, exactly one source acquisition occurs, and native combined hook flags register without duplicates. Actual: **53 PASS,4.02s**, no failures/skips. New file14 tests plus unchanged replay file39 tests. The real `run_swe_opd._training_args` output was supplied to `get_miles_extra_args_provider` with the three probe fields above. All custom flags resolved; actual rollout/orchestrator typed transport and native protocol driver construction passed. This is real custom-hook registration, not full GPU-dependent Megatron parser validation or model execution.

Additional commands:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m compileall -q tests/manual/agent_opd/probe_swe_capacity.py tests/fast/test_swe_capacity.py
git diff --check
```

Both were rerun after the final source/file-safety additions and returned0 with no output. A scoped Python whitespace assertion also passed for both new files (120/210 lines). Ruff is absent, so Ruff lint is UNVERIFIED. Initial XML `t02-capacity-replay-first.xml` records one test failure caused by registering hooks twice; the provider already registers them. Intermediate `t02-capacity-replay-final.xml` records fixture pollution from caching parser defaults under the smoke argv. Corrected the test to invoke the provider once and build cached typed fixtures under neutral argv; no production schema/parser behavior was changed. `t02-capacity-replay-green.xml` records51 PASS before the final source/file-safety checks; the final53-test XML is authoritative. Re-read the current requirements, including the newly recorded PP1 source-repair authorization and completion-only D2 clarification, before closing this slice.

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** T02-CAPACITY-REPLAY委派开始至最终CPU验证｜**当前前沿：** 父任务02 capacity/gradient及03 native SWE/dispatch

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 只实现阻塞capacity复测的单bank输入，并验证指定criteria。 |
| D2 细节反复重试 | CLEAR | 两个测试边界失败分别定位到重复registration和argv缓存污染，随后同套检查通过。 |
| D3 支线问题修补 | CLEAR | 未编辑其他任务、模型数学、平台或allocator。 |
| D4 可并行任务停滞 | CLEAR | 受委派文件所有权限制；PP1 patch/launcher及评测由其他owner并行执行。 |
| D5 超范围镀金 | CLEAR | 不支持formal、多bank、optimizer/RNG恢复、跨job恢复或重新生成。 |
| D6 分析空转 | CLEAR | 依据既有hook/schema源码确定最小方案后完成实现与验证。 |
| D7 路线违背 | CLEAR | 未改变D2 completion-only fresh scoring、D4、D7或正常engine lifecycle。 |

**文档检查：** 委派scope内S1–S6均未发现明显缺陷；Ticket02仍为in-progress，CPU PASS没有替代其native容量/gradient验收。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**

1. 父任务launcher集成上述三字段，保留同一原始bank和其teacher identity；red/green使用相同输入、资源、长度、数学及engine参数，只切换已批准的Megatron PP1 output-lifetime patch。新的attempt/evidence目录必须独立，不能覆盖原bank。
2. 父任务实际运行：确认原256条身份/顺序/所有token值，fresh current-student scoring进入两次visit，native optimizer ACK成功计数2，实际mask/D2指标有效，bank使用次数2；确认colocated SGLang仍正常startup/offload，而非debug-load或改变resident进程。
3. 并行继续02实际gradient和03真实SWE/dispatch验收；本seam不扩大formal frontier，也不证明原OOM已修复。

## 4. 最值得关注的 3 点

1. 只有新acquisition hook和delegate，`swe_replay.py`无需accessor/refactor；native ACK/counter/D7原实现保持不变。
2. 原cloud256-bank的实际读取/完整schema验证、修复后显存及两次optimizer更新尚未执行；CPU fixture与源码schema一致，但不冒充该真实bank的runtime PASS。
3. 原generation version/behavior/teacher不变；每次current-student评分仍由native训练执行，不能将旧completion relabel为新generation或精确fresh-policy KL。
