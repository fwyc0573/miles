## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Apply D35 accepted H800 capacity basis; retain pending candidate merge and separate CPU readiness from A formal first-update acceptance. |
| 2026-11-09 | Refresh the prerequisite to the expanded attempt's initial-weight-sync timeout. |
| 2026-11-09 | Refresh the unaccepted upstream gate; define post-merge CPU implementation-ready separately from A first-update GPU acceptance; align consistency failures with S7. |
| 2026-11-08 | Draft the per-turn measurement ticket. |
| 2026-11-08 | Rename KL to RKL and `kl_sum` to `rkl_sum` (D21). |
| 2026-11-08 | Update the blocker: reused code committed; its 256-turn capacity smoke fails. |
| 2026-11-08 | Apply D22: wait for that branch's complete fix; start nothing early. |

# 02: optimizer-step record 携带逐 turn RKL/NLL

**What to build:** 实现 [spec S3](../spec.md#s3-逐-turn-测量d4d5d14)：利用已有张量计算每个 turn 的 `rkl_sum`、`nll_sum`、`tokens`，每个 update 汇总一次，随 optimizer-step record 送到 rollout 侧。

**Blocked by:** D35容量依据已接受；验证通过的`agent-opd-h800-capacity`候选合并到`agent-opd-image`。当前契约见[spec S0](../spec.md#s0-复用与改动范围)；合并前本ticket任何部分均不提前开工。

**Status:** blocked — D35 accepts the H800 capacity basis and authorizes consolidation, but the candidate merge is stillpending. No per-turn implementation has begun. Historical upstream failures remain unaccepted under their own contract and no longer block this parent; see the[current D35 record](../test_report_2026-11-09_h800_preparation.md#d35-parent-adoption-2026-11-10).

**Readiness checkpoints:** 按D35完成候选合并后，下列代码和 CPU 条件完成才是 **CPU implementation-ready**，可供 03 接入及 04 启动；不是 GPU accepted / done。已接受的容量run不包含本ticket逐turn测量。GPU 验收借用 04 的第一个实际formal successful update（D16），不新增 smoke，不要求 04 在启动前提供该证据。辅助验收失败按 S7 报告，不单独停止 healthy training 或阻止 05。

- [ ] 逐 turn 的和在 `swe_tis.token_sums` 已有的逐样本循环中计算：用 native `opd_reverse_kl` 和更新前的 student log-prob，乘以原始 mask。没有新增 forward。
- [ ] 同一样本的 CP 部分和相加，只取一个 TP/PP 副本参与，每个 update 汇总一次；record 中的行用 source uid 标识。
- [ ] estimator 标签由 native 配置在一处推出，取代写死的字符串；`kl_before_tis` 和新增的 `nll_before_tis` 由同一组和推出。
- [ ] 一致性检查：`Σ tokens == original_tokens`，行数 `== actual_turns`，uid 与实际 bank 一一对应；不一致时记录原因，使 profile 从该 update 起未验证并停止追加 / 推导，训练继续（S7）。逐 turn 行不重复写入训练侧的 `updates.jsonl`。
- [ ] 新增 fast CPU 测试：长短不一的样本、两个 rank 的 CP 切分下，sampled-token 的逐 turn 和相加等于原有标量；复用 TIS 测试仍全部通过。
- [ ] GPU accepted（在 04 内，不是它的启动依赖）：A 第一个实际 successful native update 的 record 能关联 attempt、update、bank 与实际 uid；逐 turn sums 的宏观 RKL/NLL、token 数、行数及 bank 映射一致性通过，profile 中的对应值可复算。记录实测 verdict 与产物路径；失败或缺证据时本验收仍未完成，不宣称 ticket done。
