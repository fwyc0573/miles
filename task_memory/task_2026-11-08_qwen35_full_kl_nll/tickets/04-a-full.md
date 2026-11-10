## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record reviewed correction and independent corrected A executing/worker-ready; retain all checkbox states and pending native lifecycle/ACK/200 proof. |
| 2026-11-10 | Record D38 controlled diagnostic PASS and the in-progress native state-initialization correction; formal verification remains blocked. |
| 2026-11-10 | Accept the D16 first-update row; current A failed natively after1/200, blocking continuation/fresh attempts while allocation mechanism and fix remain unresolved. |
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

**Blocked by:** 01、02、03 及旧A的D16已接受；native correction/review及新A fresh准入/worker-startup已完成。当前执行真正native repair核验，未验收first/secondACK或full生命周期；200/profile仍需本attempt实际证据。Offline CPU已accepted，不再有旧Spec fix阻塞；辅助verdict不是native hardgate。

**Status:** TODO / EXECUTING native repair verification. Independent corrected A`exp-1110-165312-132926`[submitted08:53:12Z](../evidence/admission-formal-H200-A-r2-20261110.json)through unchanged`formal_h200_config.json`,10+18≤32/personal nonpreemptible/local source;[09:06:11Z worker receipt](../evidence/formal-H200-A-r2-worker-startup-20261110.json)has all3 Running/imageIDs/restart0/source matched, actual18 H200, teacher-ready/Ray2×8. Correction`edd3be00`initializes native state after shared restoration/cache clear and before initial offload/forward;`d2b3af8c`closes test naming nit,18 CPU PASS/20 SKIP(no Megatron),[both immutable reviews No findings](../review.md#optimizer-initialization-phase-review--2026-11-10). First/second ACK for this new attempt not accepted; startup does not prove offload fix. Verify train→sleep→restore/weight-update→next-train and own200/paired-profile. Old[D16/Failed1/200](../test_report_2026-11-10_d16_first_update.md)and H8000 attempts remain distinct/protected; D38 probe does not identify old full-model owner. Primary's second-ACK-or-native-failure observer owns ongoing verification, not queried here. **D37/S8 remains the resource authority over historical D33/H800 wording; every checkbox is preserved, no config/timeouts/HF/eval/additional probe or acceptance change.**

- [ ] 冻结attempt identity、源代码、解析后的配置、输入和模型identity；按spec S8和D33在H800/codesign提交，无task GPU数量上限，正式cell非抢占。
- [ ] 输入使用 `loss_masked` turn source 和 01 审计生成的源文件 manifest；作业另挂载 posttrain 卷，原位读取源文件（spec S8）。
- [x] 第一个formal update检查（D16，不新增GPU smoke；完成并记录之后才进入 05 的资源准入）：先确认实际 successful native optimizer update / ACK，再检查 S3 token / 行数 / uid 一致性、采集 / teacher / 训练耗时及 profile 两个文件和复算值。将这份 runtime evidence 交给 02 GPU 验收；profile 辅助失败明确报告 unverified 并按 S7 停止其更新，healthy training 继续，不能单凭辅助 verdict 阻止 05。native 首次 update 未成功、native failure 或资源不足仍是 blocker。
- [ ] 约第 20 个 update 时汇报各阶段耗时的趋势（S8）；第一个 update 因吞吐失败时按 D19 处理。
- [ ] Native training 完成：200 个实际 successful optimizer update / ACK，训练侧 record 和 native counters 对应，按实际 bank membership 记录训练 turn 数；失败 attempt 不拼接。
- [ ] 完整 profile accepted：两个文件各 200 个成对一致的 update，observation 数等于实际训练 turn 数，每个 update 的 S3 一致性通过，离线重建与记录值一致。S7 出错时本项未通过，但不阻止 healthy training 完成；保留完整核验前缀、未验证起点和缺失范围，标 INCOMPLETE / UNVERIFIED，不补造 200 行。
- [ ] 每个已检查 update 的一致性 verdict 都已记录；没有 profile 的后续 update 明确列为未验证，不仅列出第一条错误。
- [ ] 记录 RJob 业务终态和资源使用；失败的 attempt 单独保留，不拼接到正式结果中。
