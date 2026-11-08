## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the independent A/full formal cell. |

# 04: 完成 Qwen3.5-27B 教师的 full 实验

**What to build:** 从冻结的4B初始化完成A/full正式训练及其全部异步SWE评测，形成可与A/r256直接比较的证据。

**Blocked by:** 02 — 训练与度量；03 — HF异步评测与释放。

**Status:** blocked — waiting for 02 and 03; formal run not started

- [ ] 冻结独立attempt、源代码、配置、输入与模型identity；通过本cell原生准备检查并在当前GPU承诺上限内提交。
- [ ] 完成spec规定的200成功updates，full每步使用新生成bank；turn数量、超时及失败语义遵守最终冻结决定。
- [ ] 保存200行实际KL/TIS、native counters、学习率及生成版本；统计可回连真实训练tokens。
- [ ] 在四个指定成功update正确导出HF并异步完成每份100×4评测；不依赖其他cell完成才开始。
- [ ] 按已确认条件释放权重，归档完整结果、实际删除bytes及RJob业务终态；原生失败与未完成评测明确保留。
