## 1. 规划完成情况

**Modification History**

| Date | Change |
| --- | --- |
| 2026-11-09 | Check the submitted D13 native frontier and correct the stale Ticket02 admission state. |

**汇总：** PASS2｜BLOCKED/FAILED/SKIPPED5｜TODO2

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
|01 输入和身份 | PASS | D11已验收，原生receipt及输入合同保持。 |
|02 训练/容量 | TODO | CPU集成已完成；18卡新attempt已提交，native容量仍待验收。 |
|03 异步评测能力 | PASS | 原生HF2故障隔离/HF3成功验收已记录。 |
|04 A/full | BLOCKED | 等02 native容量。 |
|05 A/r256 | BLOCKED | 等02 native容量。 |
|06 B/full | BLOCKED | 等02 native容量。 |
|07 B/r256 | BLOCKED | 等02 native容量。 |
|08 原始4B基线 | TODO | 独立400-slot执行中；缺失结果不能计False。 |
|09 对照汇总 | BLOCKED | 等04–08正式结果。 |

## 2. 偏离检测

**结论：** 已偏离：命中D2，已停止相关临时调参。
**检测窗口：** 较早的03最新PASS（49aa6f8b）至fc3e6ed2｜**当前前沿：**02 native验收、08独立基线。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
|D1 工具打磨 | CLEAR | 85/55/293回归直接验证新拓扑、worker和source入口，之后进入真实提交。 |
|D2 细节反复重试 | HIT | 临时actual-YAML检查先后因错误Python环境、漏worker_type和无效graph断言失败；并非每次都有预先记录的排除条件。另有重复猜测Ticket02路径。停止临时探针调参和路径猜测，使用既有真实parse链/准确glob结果。 |
|D3 支线问题修补 | CLEAR | 基线四个missing-slot诊断归属08；未改client或结果口径。 |
|D4 可并行任务停滞 | CLEAR |02已由CPU进入真实提交，08持续独立执行并完成缺失诊断。 |
|D5 超范围镀金 | CLEAR | 只修选定A必需的参数、两节点和source入口；撤回重复HTTP timeout方案。 |
|D6 分析空转 | CLEAR |52e84dea交付实现、58d39c35接入明确50授权、fc3e6ed2记录真实提交。 |
|D7 路线违背 | CLEAR | 用户明确选择18卡A并提高到个人50；正式profile、science、teacher包络、并发1不变。 |

**文档检查：** S5 Ticket02状态第22行仍写32额度HOLD和未提交，与用户50授权及实际admission冲突；其余S1–S4、S6未发现明显缺陷。
**归因：** D2执行偏离，非S5导致。

## 3. 纠正建议

**分支：** B：spec/tickets存在过期状态，先更新文档。

**文档更新（先执行）：**
1. `tickets/02-replay-training-and-metrics.md`状态：记录个人49/50、实际job和首次Pending读回；保留native未验收。（可直接执行）

**需停止的偏离行为：**
- D2：停止反复修临时parse检查和猜测文件路径；已有生产parse回归足够CPU阶段，有效graph/设备/权重值由真实worker日志验证。

**接下去的路线：**
1.02：保持现有本地launcher存活；核验双节点、实际8服务、关闭graph、source/lifetime和IPC/NCCL，再核验1800秒内>=231有效轨迹、两次当前student评分/真实optimizer ACK。平台Pending和CPU通过都不能替代这些条件。
2. 并行08：保留原72小时/400-slot账本、源权重和四个missing；健康执行继续，不自动重抽、截断或计False。

## 4. 最值得关注的 3 点

1. 18卡attempt `exp-1109-144110-764758` 已提交，首次平台读回仍排队；暂无实际容量结果。
2. native admission确为个人31+18=49、ceiling50、不可抢占；旧64窗口及正式profile未改。
3. 08三个输入超限和一个终态断连仍缺失；不将基础设施异常替换成模型成绩。
