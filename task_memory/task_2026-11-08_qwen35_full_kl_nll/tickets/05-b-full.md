## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record implemented/reviewed correction and new A execution; B still waits for common native verification/fresh resources, not a new logical A200/profile-PASS gate. |
| 2026-11-10 | Record controlled D38 evidence and the common native correction in progress; retain B's completed A-inspection edge and remaining resource/runtime work. |
| 2026-11-10 | Accept A firstACK/inspection prerequisite; block B on the common native host-memory fault and fresh admission, not A200/profile PASS. |
| 2026-11-10 | Reflect actual A H200/Ray startup and joined CPU readiness while retaining B's real ACK/inspection/resource blockers and all final criteria. |
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

**Blocked by:** 01、02、03 已接受；04 的firstA ACK/inspection由D16满足。Common correction已implemented/reviewed，但native verification及fresh18-H200资源≤32未完成；不是新A200/profile-PASS逻辑门槛。

**Status:** BLOCKED — common fix verification and fresh admission; B not started. Correction`edd3be00`/`d2b3af8c`is committed with[immutable reviews No findings](../review.md#optimizer-initialization-phase-review--2026-11-10). Independent corrected A`exp-1110-165312-132926`is[worker-ready/executing](../evidence/formal-H200-A-r2-worker-startup-20261110.json), not the oldFailed1/200 result; no first/second ACK for this new attempt accepted yet. Existing[A-firstACK/inspection D16](../test_report_2026-11-10_d16_first_update.md)is satisfied, not reset or spliced. Common real train/sleep/restore/weight-update/next-train verification and fresh18H200 quota within32 remain; A18+B18cannot hold full allocation together, a resource condition not A200/profile-PASS gate. D38 controlled PASS is not old full-model owner/native repair acceptance. D37/S8 remains the resource authority over historical D33/H800 wording; all B native/profile/200 criteria and checkbox states stay unchanged. Primary owns observations, no additionalGPU probe/config/timeouts/HF/eval change.

- [ ] 冻结attempt identity、源代码、解析后的配置、输入和模型identity；按spec S8和D33在H800/codesign提交，无task GPU数量上限，正式cell非抢占。
- [ ] 输入使用 `loss_masked` turn source 和 01 审计生成的源文件 manifest；作业另挂载 posttrain 卷，原位读取源文件（spec S8）。
- [x] 启动前核对 A 的实际 successful optimizer ACK 与已完成 inspection；A 的辅助 profile 失败须已报告并标 unverified，但不单独阻止 B。native first-update failure 和资源不足仍阻塞提交。
- [ ] B 第一个 actual successful update 做与 04 相同的检查，记录 S3 / bank identity / profile 内容和各阶段耗时的实际 verdict；辅助失败按 S7 隔离。
- [ ] 约第 20 个 update 时汇报各阶段耗时的趋势（S8）；第一个 update 因吞吐失败时按 D19 处理。
- [ ] Native training 完成：200 个实际 successful optimizer update / ACK，训练侧 record 和 native counters 对应，按实际 bank membership 记录训练 turn 数。
- [ ] 完整 profile accepted：两个文件各 200 个成对一致的 update，observation 数等于实际训练 turn 数，每个 update 的 S3 一致性通过，离线重建与记录值一致。S7 出错时本项未通过，healthy training 继续；完整核验前缀、未验证起点和缺失范围单列为 INCOMPLETE / UNVERIFIED，不补造记录。
- [ ] 每个已检查 update 的一致性 verdict 都已记录；profile 停止后的区间也明确列为未验证。
- [ ] 记录 RJob 业务终态和资源使用；失败的 attempt 单独保留。
