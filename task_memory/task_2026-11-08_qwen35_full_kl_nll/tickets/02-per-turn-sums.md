## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Accept retained real D16 first-update GPU criterion; all CPU/S7 and GPU checks complete, ticket done without accepting the failed1/200 formal run. |
| 2026-11-10 | Accept downstream S7 CPU evidence from15186817 while retaining A's first actual formal update as incomplete GPU acceptance. |
| 2026-11-10 | Accept trainer CPU readiness at6129aefe; split achieved trainer consistency from pending downstream S7 without closing GPU acceptance or changing scope. |
| 2026-11-10 | Record verified merge55fba827; unblock implementation while retaining incomplete CPU-ready and formal A-update acceptance. |
| 2026-11-10 | Apply D35 accepted H800 capacity basis; retain pending candidate merge and separate CPU readiness from A formal first-update acceptance. |
| 2026-11-09 | Refresh the prerequisite to the expanded attempt's initial-weight-sync timeout. |
| 2026-11-09 | Refresh the unaccepted upstream gate; define post-merge CPU implementation-ready separately from A first-update GPU acceptance; align consistency failures with S7. |
| 2026-11-08 | Draft the per-turn measurement ticket. |
| 2026-11-08 | Rename KL to RKL and `kl_sum` to `rkl_sum` (D21). |
| 2026-11-08 | Update the blocker: reused code committed; its 256-turn capacity smoke fails. |
| 2026-11-08 | Apply D22: wait for that branch's complete fix; start nothing early. |

# 02: optimizer-step record 携带逐 turn RKL/NLL

**What to build:** 实现 [spec S3](../spec.md#s3-逐-turn-测量d4d5d14)：利用已有张量计算每个 turn 的 `rkl_sum`、`nll_sum`、`tokens`，每个 update 汇总一次，随 optimizer-step record 送到 rollout 侧。

**Blocked by:** 无剩余merge blocker；D35容量已接受，候选已由`55fba827`合并，second parent`0e6e8b1e`。合并前不得提前开工的历史要求已满足；验证见[input merge报告](../test_report_2026-11-10_input_merge.md#post-merge-verification-2026-11-10)。

**Status:** done / PASS. CPU trainer`6129aefe`and S7 integration`15186817`remain accepted; the actual A first successful update/canonical UID-mask binding, counts, macros and paired rebuild are now PASS in[the D16 report](../test_report_2026-11-10_d16_first_update.md)and[verification receipt](../evidence/d16-H200-A-20261110/first-update-verification.json). All seven criteria are covered. The subsequent native host-memory failure leaves formal A1/200 INCOMPLETE, not a failure of the verified measurement or evidence of200 completion. CPU reviews remain0/0; runtime/configuration/science unchanged.

**Readiness checkpoints:** CPU/S7及借用04实际首ACK的D16 GPU验收均完成，本票done。不新增smoke。B的A首ACK/inspection条件已满足，但共同native内存故障和fresh准入仍阻塞；辅助profile verdict不是新hardgate。

- [x] 逐 turn 的和在 `swe_tis.token_sums` 已有的逐样本循环中计算：用 native `opd_reverse_kl` 和更新前的 student log-prob，乘以原始 mask。没有新增 forward。
- [x] 同一样本的 CP 部分和相加，只取一个 TP/PP 副本参与，每个 update 汇总一次；record 中的行用 source uid 标识。
- [x] estimator 标签由 native 配置在一处推出，取代写死的字符串；`kl_before_tis` 和新增的 `nll_before_tis` 由同一组和推出。
- [x] Trainer一致性与传输：核对`Σ tokens == original_tokens`、行数`== actual_turns`、uid唯一与完整CP贡献；辅助不一致或准备异常通过既有ACK的`turn_sums_verified=False`和原因传给下游，不中断healthy native optimizer/collectives。逐turn行不重复写入训练侧的`updates.jsonl`。CPU证据见上述报告。
- [x] 下游S7 CPU全链路（由03 `15186817` 接入验证，保留原一致性条件）：uid与实际bank一一对应；successful ACK携带未验证的turn sums或映射/计数失败时，profile从该update起未验证并停止后续追加/推导，训练继续。真实consumer、partial-file及后续healthy ACK故障注入见[接入报告](../test_report_2026-11-10_profile_integration.md#decisive-cpu-observations)；这项CPU验收不替代下一项formal GPU检查。
- [x] 新增 fast CPU 测试：长短不一的样本、两个 rank 的 CP 切分下，sampled-token 的逐 turn 和相加等于原有标量；复用 TIS 测试仍全部通过。
- [x] GPU accepted（在 04 内，不是它的启动依赖）：A 第一个实际 successful native update 的 record 能关联 attempt、update、bank 与实际 uid；逐 turn sums 的宏观 RKL/NLL、token 数、行数及 bank 映射一致性通过，profile 中的对应值可复算。记录实测 verdict 与产物路径；失败或缺证据时本验收仍未完成，不宣称 ticket done。
