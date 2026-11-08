## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Admit B after A's actual first successful update and completed inspection, not an auxiliary PASS; separate native completion from complete profile acceptance. |
| 2026-11-08 | Draft the B/full formal cell ticket. |
| 2026-11-08 | Apply the D17 GPU budget. |
| 2026-11-08 | Add the update-20 timing report and D19. |
| 2026-11-08 | Use the SWE-1003 0913 data read in place (D23–D25). |

# 05: B/full 正式 cell（Qwen3.5-4B + Qwen3.5-35B-A3B）

**What to build:** 与 04 相同的协议，teacher 换为 Qwen3.5-35B-A3B。

**Blocked by:** 01 accepted、02 CPU implementation-ready、03 integration CPU-ready；04 实际完成第一个 successful native update 且检查已完成并记录；资源准入满足。不要求辅助 profile verdict 为 PASS。

**Status:** blocked — no accepted 01 or 02/03 CPU integration readiness and no actual A first successful update / completed inspection; upstream D1/D22 still unaccepted

- [ ] 冻结 attempt identity、源代码、解析后的配置、输入和模型 identity；在 D17 额度内提交（本 task 非抢占不超过 32 卡）。
- [ ] 输入使用 `loss_masked` turn source 和 01 审计生成的源文件 manifest；作业另挂载 posttrain 卷，原位读取源文件（spec S8）。
- [ ] 启动前核对 A 的实际 successful optimizer ACK 与已完成 inspection；A 的辅助 profile 失败须已报告并标 unverified，但不单独阻止 B。native first-update failure 和资源不足仍阻塞提交。
- [ ] B 第一个 actual successful update 做与 04 相同的检查，记录 S3 / bank identity / profile 内容和各阶段耗时的实际 verdict；辅助失败按 S7 隔离。
- [ ] 约第 20 个 update 时汇报各阶段耗时的趋势（S8）；第一个 update 因吞吐失败时按 D19 处理。
- [ ] Native training 完成：200 个实际 successful optimizer update / ACK，训练侧 record 和 native counters 对应，按实际 bank membership 记录训练 turn 数。
- [ ] 完整 profile accepted：两个文件各 200 个成对一致的 update，observation 数等于实际训练 turn 数，每个 update 的 S3 一致性通过，离线重建与记录值一致。S7 出错时本项未通过，healthy training 继续；完整核验前缀、未验证起点和缺失范围单列为 INCOMPLETE / UNVERIFIED，不补造记录。
- [ ] 每个已检查 update 的一致性 verdict 都已记录；profile 停止后的区间也明确列为未验证。
- [ ] 记录 RJob 业务终态和资源使用；失败的 attempt 单独保留。
