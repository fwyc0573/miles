## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Align current B context with18-H200/cell and32-GPU admission: actual A ACK/inspection remain logical prerequisites, while allocation release is a separate resource requirement. |
| 2026-11-10 | Add D36 A-wait context to current status only; B still requires actual A first ACK/inspection and fresh resources, with no changed acceptance or extra approval gate. |
| 2026-11-10 | Record satisfied CPU/configuration prerequisites; B still waits for A's actual first ACK, completed inspection and fresh resources, not A completion or auxiliary PASS. |
| 2026-11-10 | Record02 CPU readiness and B TP4/EP1 feasibility limits;retain authorized concurrent admission after A first ACK/inspection,not A completion or new approval. |
| 2026-11-10 | Record merge55fba827 complete; preserve02/03 readiness,A first formal-update inspection and B native-runtime limitations. |
| 2026-11-10 | Apply D35 parent capacity adoption without certifying B runtime or removing merge/integration and A formal first-update dependencies. |
| 2026-11-09 | Accept the D34 input re-audit without changing integration, A/full inspection or resource-admission dependencies. |
| 2026-11-09 | Apply D33 H800 authorization and remove the superseded count limit;01 is accepted. |
| 2026-11-09 | Admit B after A's actual first successful update and completed inspection, not an auxiliary PASS; separate native completion from complete profile acceptance. |
| 2026-11-08 | Draft the B/full formal cell ticket. |
| 2026-11-08 | Apply the D17 GPU budget. |
| 2026-11-08 | Add the update-20 timing report and D19. |
| 2026-11-08 | Use the SWE-1003 0913 data read in place (D23–D25). |

# 05: B/full 正式 cell（Qwen3.5-4B + Qwen3.5-35B-A3B）

**What to build:** 与 04 相同的协议，teacher 换为 Qwen3.5-35B-A3B。

**Blocked by:** 01 accepted、02 CPU implementation-ready、03 integration CPU-ready均已满足；仍等 04 实际首个successful update/ACK及完成inspection，然后fresh18-H200准入。A仍持18卡时A18+B18>32，必须等allocation释放；这是资源条件，不是A200/profile PASS逻辑门槛。

**Status:** pending actual A first ACK/inspection and fresh resources under **D37 H200_PREPARATION**. CPU prerequisites remain accepted; reporter/inspector preparation runs independently but its new CPU results/join are unfinished. [D37](../requirements.md#h200-switch--original-request-2026-11-10)and`d822174c`configure18 H200/cell on step_main, student2×8+teacher2, with a2-H200 TP2 B teacher not yet native accepted. Under the32 personal non-preemptible ceiling, A18+B18 cannot overlap at full allocation; even after A firstACK/inspection, B needs released allocation and fresh committed+18≤32 admission. No A200/profile-PASS/new-approval gate is added. Actual submission/status belongs to[the primary's live report](../test_report_2026-11-10_formal_runs.md), not a preparation/config inference. Old H800 formal configuration, capacity andFAILED0 attempts remain separate history. D34/science/S7 and200 distinct full banks with`bank_uses=50`are unchanged. **D37/S8 current resources supersede the historical D33/H800 wording in the existing unchecked deployment row; every checkbox/acceptance criterion below remains unchanged.**

- [ ] 冻结attempt identity、源代码、解析后的配置、输入和模型identity；按spec S8和D33在H800/codesign提交，无task GPU数量上限，正式cell非抢占。
- [ ] 输入使用 `loss_masked` turn source 和 01 审计生成的源文件 manifest；作业另挂载 posttrain 卷，原位读取源文件（spec S8）。
- [ ] 启动前核对 A 的实际 successful optimizer ACK 与已完成 inspection；A 的辅助 profile 失败须已报告并标 unverified，但不单独阻止 B。native first-update failure 和资源不足仍阻塞提交。
- [ ] B 第一个 actual successful update 做与 04 相同的检查，记录 S3 / bank identity / profile 内容和各阶段耗时的实际 verdict；辅助失败按 S7 隔离。
- [ ] 约第 20 个 update 时汇报各阶段耗时的趋势（S8）；第一个 update 因吞吐失败时按 D19 处理。
- [ ] Native training 完成：200 个实际 successful optimizer update / ACK，训练侧 record 和 native counters 对应，按实际 bank membership 记录训练 turn 数。
- [ ] 完整 profile accepted：两个文件各 200 个成对一致的 update，observation 数等于实际训练 turn 数，每个 update 的 S3 一致性通过，离线重建与记录值一致。S7 出错时本项未通过，healthy training 继续；完整核验前缀、未验证起点和缺失范围单列为 INCOMPLETE / UNVERIFIED，不补造记录。
- [ ] 每个已检查 update 的一致性 verdict 都已记录；profile 停止后的区间也明确列为未验证。
- [ ] 记录 RJob 业务终态和资源使用；失败的 attempt 单独保留。
