## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | 在D13 A合并CPU回归后检查路线，纠正临时配置核验重试和过时pending状态。 |

## 1. 规划完成情况

**汇总：** PASS 2｜BLOCKED/FAILED/SKIPPED 6｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 01 输入与身份 | PASS | D11真实receipt与普通factory已验收。 |
| 02 原生训练/容量 | FAILED | D12仅227/256；D13 A的CPU集成已完成，但18卡native尚未提交。 |
| 03 HF/异步SWE流程 | PASS | 已验收并提交49aa6f8b；qualification账本边界仍保留。 |
| 04 A/full | BLOCKED | 等02新数据容量与更新验收。 |
| 05 A/r256 | BLOCKED | 同上。 |
| 06 B/full | BLOCKED | 同上。 |
| 07 B/r256 | BLOCKED | 同上。 |
| 08 原始4B基线 | TODO | 记录23/400，9 true/14 false，另4个缺失失败slot；原deadline不变。 |
| 09 四cell比较 | BLOCKED | 等04–08。 |

## 2. 偏离检测

**结论：** 已偏离：命中D2。
**检测窗口：** d8c27b75之后的D13 A准备至今｜**当前前沿：** 02、08。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 原生参数和双节点fixture直接验证18卡所需能力；293项合并回归通过后停止扩展。 |
| D2 细节反复重试 | HIT | 临时配置读回连续因错误环境、缺少worker_type和误用model级graph getter失败，未预先记录可排除原因的假设；占用了02的配置就绪路径。见rollout expansion报告的迭代记录。 |
| D3 支线问题修补 | CLEAR | baseline缺失slot诊断属于08；没有改上下文、重试已完成结果或新增GPU实验。 |
| D4 可并行任务停滞 | CLEAR | core与worker两线并行交付；08持续执行。新增GPU受当前额度约束。 |
| D5 超范围镀金 | CLEAR | 显式GPU默认行为和两节点生命周期是已选择A方案的必要条件；未改formal profiles、teacher envelope或concurrency。 |
| D6 分析空转 | CLEAR | 两线交付实现，parent集成并获得293 PASS；独立review已启动，不继续重复探索。 |
| D7 路线违背 | CLEAR | A选择已记录；未把CPU通过当作native容量通过，未重启失败GPU作业。 |

**文档检查：** S5 `progress.md:pending`仍要求finish integration/combine CPU，与最新293 PASS记录冲突。S1/S2/S3/S4/S6未发现明显缺陷。

**归因：** D2执行偏离；S5是独立的状态过时，不是临时核验重试的原因。

## 3. 纠正建议

**分支：** B：spec/tickets存在状态缺陷，先更新文档再继续。

**文档更新（先执行）：**
1. `progress.md:pending`：将下一步改为review→fresh admission→single18-card native smoke，保留02/08未完成边界。（可直接执行，已应用）

**需停止的偏离行为：**
- D2细节反复重试：停止追加临时配置断言和猜测字段；复用已通过的生产parse链。实际graph配置直接在native引擎读回时确认。

**接下去的路线：**
1. 02：完成固定diff的独立review并修复可行动缺陷 → 完成标志：没有未处理的prelaunch阻塞发现。
2. 02：fresh个人额度/平台quota与H200限制 → 完成标志：18卡在全部适用约束内获准，且没有改停其他作业或擅自抢占式替代。
3. 02：只提交获批的A/r256一次 → 完成标志：231/256 within1800s、8引擎/训练8卡、原生两次optimizer ACK、第二次scoring及native tensor验收；失败时保留stage边界。
4. 并行：08继续原400-slot账本并确认缺失原因，不缩分母、不续deadline、不自动重抽。

**暂缓事项：** native context overflow和缺失grader的恢复决策 → 记入`issues.md`；不得用截断、增大128K或自动重采样代替已有评测规则。

## 4. 最值得关注的 3 点

1. 293项CPU通过仍不证明混合CUDA IPC/NCCL权重同步或容量；GPU gate完全保留。
2. 记录额度23+18=41，workspace H20032限制仍阻塞；D9的56 ceiling不能替代更严格的适用约束。
3. 08仍只有23/400；缺失slot不能算False或当完整baseline，所有相关deadline/reader/源权重保护保持不变。
