## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Accept small-run native loss reconstruction; record failed acquisition gates and pending large-bank verification. |
| 2026-11-08 | Record the reaccepted D11 prerequisite and actual replacement-data runtime progress; retain capacity gates. |
| 2026-11-08 | Mark the D11 input prerequisite reopened; retain source-independent math evidence with its historical dataset provenance. |
| 2026-11-08 | Accept directly observed native derivative/detach, original-token finalization and AdamW continuity; capacity remains open. |
| 2026-11-08 | Accept the four short native paths and exact A/r256 tensor reconstruction; keep actual gradient and256-turn capacity checks open. |
| 2026-11-08 | Clear the completed input prerequisite; keep native GPU acceptance in progress. |
| 2026-11-08 | Draft the generation-to-update replay and metrics slice. |

# 02: 打通 full/r256 训练与逐步 KL/TIS

**What to build:** 从已冻结输入生成学生轨迹、取得对应教师目标、按full/r256排程训练，并从真实loss输入和optimizer计数输出逐步KL及实际训练token统计。

**Blocked by:** 01 — 默认SWE输入与身份契约。

**Status:** in-progress — 01's D11 input prerequisite is reaccepted. Small-run completion RKL/TIS and native PPO reconstruction pass; both256-turn attempts failedD6 acquisition at206/224 valid before student scoring. Acquisition RCA is active; large-bank gradient/optimizer/lifetime and sourcepatch adoption remain unverified. Historical GLM evidence does not certify replacement-data capacity.

- [x] 使用已有Qwen训练路径和共享的显式实验配置；两种教师及两种模式无需复制整套实现。
- [ ] 完整200行排程符合spec；验证bank边界、成功/跳过计数及失败不提交使用次数。
- [ ] Replay保留canonical tokens/mask/behavior/teacher目标，每次重算当前student概率与TIS；cache不跨教师混用。
- [x] D4的token与回答几何平均两层binary筛选和参考计算一致；保留权重为1，survivor按交集精确计数，不沿用旧Qwen的ratio-weighted结果。
- [ ] D7首个全局零survivor batch终止当前attempt，保存证据且不提交成功update；其他cell继续，不将辅助观测错误误判为零。
- [ ] Hung request、晚返回、重复callback与有效样本不足按已确认策略结束，已完成结果可用且不会无限等待。
- [x] 在真实DP/rank与mask归约处输出KL numerator/denominator、TIS前后tokens及保留率；独立计算核验至少一个非均匀长度且有TIS丢弃的batch。
- [x] 检查实际optimizer、逐步LR、S4的原生OPD surrogate、detach关系、分布式原始token分母及同一bank多次更新；用真实loss/gradient核验而非只比较KL日志或配置开关。
- [ ] 分别验证A/B以及full/r256原生关键路径，使用代表性256-turn负载检查容量；测试缩短的排程与正式预算清晰分开。
- [ ] 实际GPU角色数、长上下文显存和bank转换证据支持正式并发计划，所有辅助观察符合soft-gate约束。
