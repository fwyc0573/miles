## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record merge55fba827 complete; preserve module CPU acceptance and02 CPU-ready as the integration blocker. |
| 2026-11-10 | Apply D35 candidate merge authorization while retaining02 CPU readiness and unimplemented rollout/native-count integration. |
| 2026-11-09 | Make integration depend on 02 CPU readiness, retain the upstream gate, and add explicit incomplete-profile, baseline-entry and post-failure verification. |
| 2026-11-08 | Draft the Distillation profile ticket. |
| 2026-11-08 | Take `alive` from the per-bank report of finished conversations (D18). |
| 2026-11-08 | Documentation frozen: module work in progress; integration waits for 02. |
| 2026-11-08 | Module part done (criteria 1–4, 6); integration still blocked by 02. |
| 2026-11-08 | State that `t_id` is the training-turn ordinal (D24). |
| 2026-11-08 | Reopen the module part for the remaining gap, the run-relative gap and the restated trend and recovery gap (D28–D31). |
| 2026-11-08 | Module part done again for D28–D32; integration still blocked by 02. |

# 03: Distillation profile 模块与接入

**What to build:** 按 [spec S4–S7](../spec.md#s4-distillation-profile-的内容d3d6d9d13d28d31) 实现 `tests/manual/agent_opd/distillation_profile.py`，并接入 `SweReplay.on_train_result`。

**Blocked by:** 文档冻结已满足，模块CPU已接受，D35合并`55fba827`已验证；接入部分仍等待 02 的 CPU implementation-ready。

**Status:** in-progress — pure module and review-added historical queries / baseline boundaries / partial-write isolation retain CPU acceptance ([review test report](../test_report_2026-11-09_review_execution.md)). Candidate merge`55fba827`is verified, but02 CPU-ready and this ticket's integration/native-count/S7 full-path acceptance are not yet recorded. Integration remains blocked by02 CPU readiness; neither input merge checks nor H800 capacity establish profile acceptance.

- [x] 模块包含 Turn observation、宏观行、conversation 条目、查找表，以及 S4 定义的全部查询（单个 conversation 和全部 conversation 两种形式）。
- [x] fast CPU 测试使用合成的 update 序列，期望值手工计算。覆盖：同一 update 内多个 turn、跳过的 update、窗口 k 未到、并列最佳、表格映射和 `alive` 状态变化。
- [x] 按 S6 写两个 JSONL 文件；测试中由文件离线重建的 profile 与内存中的一致。
- [x] 已有故障注入证据：写文件抛错、行数不一致会把 profile 标记为未验证，调用方继续运行。后续停止追加与不完整产物判定由下面补充条件验收（S7）。
- [ ] 接入：successful update 的 record 加上 bank 中的 identity，正确映射到 `c_id`/`t_id`（`t_id` 为 training turn 序号，D24）；`alive` 来自 01 按 bank 报告的已取完 conversation；被跳过的 update 不产生 observation。
- [x] 测量合成的 200 update × 256 turn 运行中，每个 update 的更新耗时和全部 conversation 查询的耗时，并写入测试报告。
- [x] D28–D32：B、N 作为 profile 配置（默认 10 和 8）；宏观 baseline、conversation baseline、两种 remaining gap 和 run-relative gap；trend 与 recovery gap 改用 remaining gap；单个和全部 conversation 两种查询；`updates.jsonl` 的新字段及离线重建。CPU 测试的期望值手工计算，覆盖 baseline 未固定、baseline ≤ 0、trend 参考条目落在 baseline 窗口内；重新测量上一条的两个耗时。
- [x] 核对 CPU evidence：`test_historical_conversation_entry_and_gaps` 与 `test_baseline_stops_at_its_turn_count` 覆盖跨条目累计及只取最早 N 个 observation；未知 / 非正 baseline 的 dependent values 为 null。历史 entry 和两种 ratio 可在 baseline 固定后追溯查询，缺席 update 不冒用邻近条目。N = 8 不假设首个条目恰好是完整 block。
- [x] 模块故障隔离：写入异常与行数 / uid 错误标记 unverified；`test_partial_write_preserves_evidence_and_stops_later_updates` 验证已写 observations、未写 summary 时保留不完整证据、拒绝完整 rebuild、后续调用不再追加。完整 native token-counter 传播仍由下一项及接入验收。
- [ ] S7 全链路：token / 行数 / uid mismatch 或写入异常记录 `unverified_from` 和原因；随后 successful update 不再追加或派生已验证新值，调用方和 healthy native training 继续。分别核对两个文件部分写入时的完整成对前缀与缺失范围，不能用部分内存 / 文件状态声称完整 profile。
- [ ] 03 integration CPU-ready：在真实 `SweReplay.on_train_result` 接入路径核对 successful / skipped update、bank identity 和 finished conversation 的传播；02 GPU acceptance 留在 04 的首个 successful update，不成为 03 CPU 接入的前置循环。
