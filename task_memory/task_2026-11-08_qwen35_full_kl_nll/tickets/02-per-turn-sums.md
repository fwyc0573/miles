## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the per-turn measurement ticket. |
| 2026-11-08 | Rename KL to RKL and `kl_sum` to `rkl_sum` (D21). |

# 02: optimizer-step record 携带逐 turn RKL/NLL

**What to build:** 实现 [spec S3](../spec.md#s3-逐-turn-测量d4d5d14)：利用已有张量计算每个 turn 的 `rkl_sum`、`nll_sum`、`tokens`，每个 update 汇总一次，随 optimizer-step record 送到 rollout 侧。

**Blocked by:** 复用 Ticket02 在 `agent-opd` 上提交并通过其 native smoke，然后合并到 `agent-opd-image`（D1）。

**Status:** blocked — reused Ticket02 not yet committed

- [ ] 逐 turn 的和在 `swe_tis.token_sums` 已有的逐样本循环中计算：用 native `opd_reverse_kl` 和更新前的 student log-prob，乘以原始 mask。没有新增 forward。
- [ ] 同一样本的 CP 部分和相加，只取一个 TP/PP 副本参与，每个 update 汇总一次；record 中的行用 source uid 标识。
- [ ] estimator 标签由 native 配置在一处推出，取代写死的字符串；`kl_before_tis` 和新增的 `nll_before_tis` 由同一组和推出。
- [ ] 一致性检查：`Σ tokens == original_tokens`，行数 `== actual_turns`；不一致时标记为未验证，训练继续。逐 turn 行不写入训练侧的 `updates.jsonl`。
- [ ] 新增 fast CPU 测试：长短不一的样本、两个 rank 的 CP 切分下，sampled-token 的逐 turn 和相加等于原有标量；复用 TIS 测试仍全部通过。
