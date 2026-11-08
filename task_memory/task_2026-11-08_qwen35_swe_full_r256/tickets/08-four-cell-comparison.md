## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the final evidence-based comparison slice. |

# 08: 汇总四个实验的效果与训练成本

**What to build:** 从四个正式cell的实际证据生成full/r256对比表、逐步KL/TIS曲线与完成归档，让读者能复算效果和成本。

**Blocked by:** 04 — A/full；05 — A/r256；06 — B/full；07 — B/r256；09 — 共同原始学生基线。

**Status:** blocked — waiting for 04–07 and 09; comparison not started

- [ ] 重新读取requirements和最终spec，核对所有cell、checkpoints、updates与benchmark ledger完整性。
- [ ] 按教师分别比较四个checkpoint的avg@4、KL与TIS；指标方向、分母和训练/评测样本来源明确。
- [ ] 四cell对照同一已完成原始4B基线；总计17个评测点、6,800个逻辑attempt，基线不冒充训练checkpoint。
- [ ] 汇总实际生成数、训练token数、超时/失败、训练/评测时间、GPU配置和存储删除bytes，计划值不冒充实测。
- [ ] 图表可由保留的800行逐步记录、16份checkpoint benchmark和一份共同baseline结果重建；若任何cell或baseline未完成则本ticket不标done。
- [ ] 记录单seed等结论边界；英文summary列出精确交付路径、验证结果和未解决问题。
