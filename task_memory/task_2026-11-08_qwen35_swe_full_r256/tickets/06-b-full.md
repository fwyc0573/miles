## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the independent B/full formal cell. |

# 06: 完成 Qwen3.5-35B-A3B 教师的 full 实验

**What to build:** 使用35B-A3B教师完成B/full正式训练及全部异步SWE评测，与B/r256保持共同起点和协议。

**Blocked by:** 02 — 训练与度量；03 — HF异步评测与释放。

**Status:** blocked — waiting for 02 and 03; formal run not started

- [ ] 采用独立attempt和正确35B-A3B teacher identity；参数、输入与4B起点符合共同契约，teacher目标不借用A组。
- [ ] 通过本cell原生准备检查，在GPU上限内完成200成功updates及逐步新bank生成。
- [ ] 保存200行实际KL/TIS及native counters；核对turn数、LR、生成版本和真实mask计数。
- [ ] 四个指定HF checkpoint均异步完成100×4评测，保留每个attempt身份和原生评分。
- [ ] 按已确认策略释放权重，归档结果、实际删除bytes及业务终态；失败attempt单独归档。
