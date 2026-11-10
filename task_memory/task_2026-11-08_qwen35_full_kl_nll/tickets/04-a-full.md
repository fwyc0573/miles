## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record actual H200 first-bank/generation progress and open offline review repairs; retain real ACK/D16 and every final checkbox as incomplete. |
| 2026-11-10 | Update current context to D37 H200 preparation plus parallel inspector implementation; retain all unchecked criteria and historical H800 evidence. |
| 2026-11-10 | Record selected D36 wait route in current status only; resource improvement/readback and fresh admission remain pending, with no third attempt or acceptance change. |
| 2026-11-10 | Record both attempts failed before training; block further submission pending a placement/startup strategy decision, without changing ticket acceptance or CPU readiness. |
| 2026-11-10 | Retain first formal A FAILED0 updates separately and record freshly admitted unchanged retry; startup/first-update and all runtime criteria remain incomplete. |
| 2026-11-10 | Record actual A/full submission and worker-startup evidence; leave runtime acceptance incomplete. |
| 2026-11-10 | Record accepted03 CPU integration, explicit formal profile configuration and pre-run lifecycle checks; ready for fresh admission, not launched or GPU accepted. |
| 2026-11-10 | Record02 CPU-ready6129aefe;retain03 integration and formal native/profile checks as unfinished,without extra GPU smoke. |
| 2026-11-10 | Record merge55fba827 complete without accepting02/03 readiness or formal first-update profile verification. |
| 2026-11-10 | Apply D35 capacity adoption; preserve pending merge/integration and D16 profile verification at A's first formal update without another GPU smoke. |
| 2026-11-09 | Accept the completed D34 input re-audit while retaining the separate integration and formal-run blockers. |
| 2026-11-09 | Apply D33 H800 authorization and remove the superseded count limit;01 is accepted. |
| 2026-11-09 | Separate CPU launch readiness, actual first-update inspection and native/profile acceptance; retain soft-gate continuation and explicit incomplete evidence. |
| 2026-11-08 | Draft the A/full formal cell ticket. |
| 2026-11-08 | Apply the D17 GPU budget. |
| 2026-11-08 | Use the interleaved turn order (D18); add the update-20 timing report and D19. |
| 2026-11-08 | Use the SWE-1003 0913 data read in place (D23–D25). |

# 04: A/full 正式 cell（Qwen3.5-4B + Qwen3.5-27B）

**What to build:** 使用 SWE-1003 0913 数据、interleaved turn order（32 × 8）和 Distillation profile，完成 200 个 successful update；不保存 HF，不做评测。

**Blocked by:** 01 accepted、02 CPU implementation-ready、03 integration CPU-ready、D37/config review/admission/submission均已满足。当前native A已首bank采集/generation，仍需真实firstACK/D16；offline inspector/reporter review repairs并行，不作为native执行hardgate。

**Status:** TODO / native first bank in progress. A`exp-1110-140032-491115`submitted14:00:32HKT with18 H200/step_main/nonpreemptible, all3 replicas assigned, actual18 GPUs/teacher ready/Ray2 nodes16GPU verified. The06:17:12Z[startup context](../evidence/formal-H200-A-startup-context-20261110.json)records bank0 start14:14:56.775HKT/1794291296.775030 and256 candidates; generation succeeded, and server-ready/HTTP200/generation follow the freeze_gc trace rather than a blocking native failure. No firstACK/D16/GPU-profile acceptance yet verified. Initial inspector57/reporter26 tests and CLI4 PASS are delivered; offline review deduplicates4 functional+1 local naming nit, all open/fixing ([review](../review.md#offline-inspectorreport-phase-review--2026-11-10)). Repairs/regression/re-review do not stop healthy native A or replace its acceptance. Primary owns watchers/platform/exact commands in[the formal report](../test_report_2026-11-10_formal_runs.md). **D37/S8 overrides historical D33/H800 deployment wording below; all final checkboxes/science remain unchanged and incomplete.**

- [ ] 冻结attempt identity、源代码、解析后的配置、输入和模型identity；按spec S8和D33在H800/codesign提交，无task GPU数量上限，正式cell非抢占。
- [ ] 输入使用 `loss_masked` turn source 和 01 审计生成的源文件 manifest；作业另挂载 posttrain 卷，原位读取源文件（spec S8）。
- [ ] 第一个formal update检查（D16，不新增GPU smoke；完成并记录之后才进入 05 的资源准入）：先确认实际 successful native optimizer update / ACK，再检查 S3 token / 行数 / uid 一致性、采集 / teacher / 训练耗时及 profile 两个文件和复算值。将这份 runtime evidence 交给 02 GPU 验收；profile 辅助失败明确报告 unverified 并按 S7 停止其更新，healthy training 继续，不能单凭辅助 verdict 阻止 05。native 首次 update 未成功、native failure 或资源不足仍是 blocker。
- [ ] 约第 20 个 update 时汇报各阶段耗时的趋势（S8）；第一个 update 因吞吐失败时按 D19 处理。
- [ ] Native training 完成：200 个实际 successful optimizer update / ACK，训练侧 record 和 native counters 对应，按实际 bank membership 记录训练 turn 数；失败 attempt 不拼接。
- [ ] 完整 profile accepted：两个文件各 200 个成对一致的 update，observation 数等于实际训练 turn 数，每个 update 的 S3 一致性通过，离线重建与记录值一致。S7 出错时本项未通过，但不阻止 healthy training 完成；保留完整核验前缀、未验证起点和缺失范围，标 INCOMPLETE / UNVERIFIED，不补造 200 行。
- [ ] 每个已检查 update 的一致性 verdict 都已记录；没有 profile 的后续 update 明确列为未验证，不仅列出第一条错误。
- [ ] 记录 RJob 业务终态和资源使用；失败的 attempt 单独保留，不拼接到正式结果中。
