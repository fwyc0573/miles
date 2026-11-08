## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the Distillation profile ticket. |
| 2026-11-08 | Take `alive` from the per-bank report of finished conversations (D18). |
| 2026-11-08 | Documentation frozen: module work in progress; integration waits for 02. |
| 2026-11-08 | Module part done (criteria 1–4, 6); integration still blocked by 02. |
| 2026-11-08 | State that `t_id` is the training-turn ordinal (D24). |
| 2026-11-08 | Reopen the module part for the remaining gap, the run-relative gap and the restated trend and recovery gap (D28–D31). |

# 03: Distillation profile 模块与接入

**What to build:** 按 [spec S4–S7](../spec.md#s4-distillation-profile-的内容d3d6d9d13d28d31) 实现 `tests/manual/agent_opd/distillation_profile.py`，并接入 `SweReplay.on_train_result`。

**Blocked by:** 文档冻结（模块本身和 CPU 测试）；02（接入部分）。

**Status:** in-progress — module reopened for D28–D31 (earlier criteria: [test report](../test_report_2026-11-08_distillation_profile_module.md)); integration blocked by 02

- [x] 模块包含 Turn observation、宏观行、conversation 条目、查找表，以及 S4 定义的全部查询（单个 conversation 和全部 conversation 两种形式）。
- [x] fast CPU 测试使用合成的 update 序列，期望值手工计算。覆盖：同一 update 内多个 turn、跳过的 update、窗口 k 未到、并列最佳、表格映射和 `alive` 状态变化。
- [x] 按 S6 写两个 JSONL 文件；测试中由文件离线重建的 profile 与内存中的一致。
- [x] 故障注入（写文件抛错、行数不一致）只会把 profile 标记为未验证，调用方继续运行（S7）。
- [ ] 接入：successful update 的 record 加上 bank 中的 identity，正确映射到 `c_id`/`t_id`（`t_id` 为 training turn 序号，D24）；`alive` 来自 01 按 bank 报告的已取完 conversation；被跳过的 update 不产生 observation。
- [x] 测量合成的 200 update × 256 turn 运行中，每个 update 的更新耗时和全部 conversation 查询的耗时，并写入测试报告。
- [ ] D28–D31：B、N 作为 profile 配置；宏观 baseline、conversation baseline、两种 remaining gap 和 run-relative gap；trend 与 recovery gap 改用 remaining gap；单个和全部 conversation 两种查询；`updates.jsonl` 的新字段及离线重建。CPU 测试的期望值手工计算，覆盖 baseline 未固定、baseline ≤ 0、trend 参考条目落在 baseline 窗口内；重新测量上一条的两个耗时。
