## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Close preparation blockers after76 pinned checks and phase review; advance A/B submission while native text-loader reconstruction proceeds independently. |
| 2026-11-07 | Recheck after verified commits and lifecycle preflight; retain independent C/native-loader progress while A/B preparation is blocked. |
| 2026-11-07 | Check the P3 memory/reload milestone and stop repetition of known incompatible CPU-forward tests. |

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 3

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| P0 | PASS | 任务记录与来源齐备。 |
| P1 | PASS | D1–D14 已确认。 |
| P2 | PASS | 三组初始 D8 均通过。 |
| P3-A | TODO | fused与样本边界准备已通过固定镜像检查；现在重提，真实更新/数值待验。 |
| P3-B | TODO | 同上；首次失败和首批数据完整保留。 |
| P3-C | TODO | 独立运行；实际argv为fused/100步，已发布baseline0，更新/最终结果待验。 |
| P4 | BLOCKED | 依赖三组最终验收，当前均未完成。 |

## 2. 偏离检测

**结论：** 已偏离：命中 D1。
**检测窗口：** 三组初始 D8 完成后至76项固定镜像检查及准备阶段复核｜**当前前沿：** P3-A/B恢复并核验实际更新、P3-C运行、共享HF重载。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | HIT | `exp-1107-075006-580618` 再次包含已知不兼容的4项 Transformers CPU-forward 测试；本次修改无需重跑这些用例。 |
| D2 细节反复重试 | CLEAR | 对照脚本的单-rank初始化错误有明确原因，CPU双进程通过后同尺寸GPU对照通过。 |
| D3 支线问题修补 | CLEAR | backward 峰值阻塞实际更新；HF dtype/最终身份阻塞 D13；清理由用户要求。 |
| D4 可并行任务停滞 | CLEAR | C 独立运行；HF 实现/审查与 A/B 内存定位并行。 |
| D5 超范围镀金 | CLEAR | 复用现有 fused/原生文本 loader；未扩训练预算或新增库 patch。 |
| D6 分析空转 | CLEAR | 已取得真实长度、两卡完整梯度与显存对照，并落实单个已有参数。 |
| D7 路线违背 | CLEAR | D7/D8/D9/D12/D14 保持；没有额外 optimizer probe。 |

**文档检查：** S1–S6 当前未发现明显缺陷；plan 中旧 Running/待补 tracking 叙述已按最新证据纠正。
**归因：** D1 执行偏离。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。

**需停止的偏离行为：**
- D1：停止在固定镜像 CPU 上重复不兼容的旧 forward 测试；使用已通过的129项修改相关检查，推进真实更新与原生 GPU 重载。

**接下去的路线：**
1. P3-A/B：准备检查已通过，立即重提；实际首步梯度与新发布版本才证明优化可执行。
2. 并行：P3-C 继续原作业；HF 原生 loader 的真实 GPU 资格验证继续，最终 checksum 必须绑定最终产物。
3. 各组按原100计划步验收更新后/最终 D8、HF、loss/梯度和失败计数，再进入 P4。

## 4. 最值得关注的 3 点

1. Loss-stage 峰值64.48→21.49 GiB且完整梯度通过，不等于整模型训练已通过。
2. HF 最终权重绑定 P1 在实现层关闭；真实最终产物仍不存在。
3. A/B重提后必须核对成功更新数与实际版本；旧失败尝试保留，禁止把调度位置当成功次数。
