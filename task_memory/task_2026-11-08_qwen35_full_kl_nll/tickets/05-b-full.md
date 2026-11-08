## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the B/full formal cell ticket. |
| 2026-11-08 | Apply the D17 GPU budget. |
| 2026-11-08 | Add the update-20 timing report and D19. |
| 2026-11-08 | Use the SWE-1003 0913 data read in place (D23–D25). |

# 05: B/full 正式 cell（Qwen3.5-4B + Qwen3.5-35B-A3B）

**What to build:** 与 04 相同的协议，teacher 换为 Qwen3.5-35B-A3B。

**Blocked by:** 01、02、03；04 的第一个 update 检查通过。

**Status:** blocked — waiting for 04 first-update inspection

- [ ] 冻结 attempt identity、源代码、解析后的配置、输入和模型 identity；在 D17 额度内提交（本 task 非抢占不超过 32 卡）。
- [ ] 输入使用 `loss_masked` turn source 和 01 审计生成的源文件 manifest；作业另挂载 posttrain 卷，原位读取源文件（spec S8）。
- [ ] 第一个 update 做与 04 相同的检查，并记录各阶段耗时。
- [ ] 约第 20 个 update 时汇报各阶段耗时的趋势（S8）；第一个 update 因吞吐失败时按 D19 处理。
- [ ] 完成 200 个实际 successful update：训练侧 record 200 行，profile 两个文件各 200 行，observation 数等于实际训练的 turn 数。
- [ ] 每个 update 的一致性标记都已记录；未验证的 update 列出原因。
- [ ] 记录 RJob 业务终态和资源使用；失败的 attempt 单独保留。
