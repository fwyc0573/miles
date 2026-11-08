## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Check failed D12 and baseline8/400; correct stale experiment/03 dependency statuses without changing acceptance. |
| 2026-11-09 | Accept03 after actual native isolation and review; track approved02 routing experiment and independent08. |
| 2026-11-08 | Accept numerical audit; stop blind reruns after acquisition/permission failures and retain independent baseline progress. |
| 2026-11-08 | Check actual worker/native/baseline progress and correct stale02/03 input statuses; isolate the dispatch snapshot repair. |
| 2026-11-08 | Verify32 task GPU commitments after three new-data admissions; keep runtime and optional review independent. |
| 2026-11-08 | Reaccept01 after actual formal-profile recheck; route directly to parallel02/03 new-data GPU acceptance. |
| 2026-11-08 | Accept native source/factory delivery and four-cell smoke wiring; capacity and asynchronous dry-runs pass while formal-profile parsing finishes. |
| 2026-11-08 | Apply the independent baseline-readiness correction and verify actual two-GPU admission; retain input-owner finalization and native capacity as pending. |
| 2026-11-08 | Record representative parity and typed launcher policy; require the native full-source visual receipt and check baseline-specific readiness independently. |
| 2026-11-08 | Accept the source-audit subtask and configuration dry-run; retain native parity and integrated execution as the frontier. |
| 2026-11-08 | Check the mainline after D11 replacement and source-copy verification. |

## 1. 规划完成情况

**汇总：** PASS 2｜BLOCKED/FAILED/SKIPPED 6｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 01 输入 | PASS | 全源visual/普通factory与四组formal配置通过；200/256/50合同及CPU/GPU验证边界明确。 |
| 02 训练与度量 | FAILED | 旧两组收集206/224；单次D12也仅227/256，未评分或更新，容量未验收。 |
| 03 HF/评测 | PASS | 实际HF2故障不阻止update3；HF3重载/grader/3reader退出通过，独立review GO。 |
| 04 A/full | BLOCKED | 等待02实际容量与完整原生训练验收。 |
| 05 A/r256 | BLOCKED | 等待02；D12不是正式profile变更。 |
| 06 B/full | BLOCKED | 等待02。 |
| 07 B/r256 | BLOCKED | 等待02。 |
| 08 原始学生基线 | TODO | 已持久化8/400结果，4 true/4 false；392缺失，原72h不变，无完整avg@4。 |
| 09 比较归档 | BLOCKED | 无正式cell或完整benchmark结果。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 上次原生03验收checkpoint至今｜**当前前沿：** 02失败收集的只读RCA、08完整评测；03已完成。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 03通过后未追加harness；只收集02失败与08真实结果。 |
| D2 细节反复重试 | CLEAR | D12是事先记录queue假设且获批的单次检验；失败后未再提交。 |
| D3 支线问题修补 | CLEAR | 只读RCA直接服务02容量门槛，未修无关问题。 |
| D4 可并行任务停滞 | CLEAR | 02失败取证与08基线并行；03验收已提交49aa6f8b。 |
| D5 超范围镀金 | CLEAR | D12单次范围保持；正式profile与门槛未变。 |
| D6 分析空转 | CLEAR | 新增227/256终态与8/400基线结果；后续分析限定在未完成请求原因。 |
| D7 路线违背 | CLEAR | D12已记录原始批准；231/1800/128K/n1/max1/graphFalse/TP2保持，04–07未提前启动。 |

**文档检查：** S5：plan/progress仍称D12运行中，ticket08仍称03未完成，与实际Failed及49aa6f8b矛盾；已修正。S1–S4/S6无新缺陷；三次未达门槛不证明criterion不可达。
**归因：** 无执行偏离；S5状态滞后已修正。

## 3. 纠正建议

**分支：** B：tickets存在状态滞后，先更新记录，不改变scope或验收条件。

**文档更新（先执行，已完成）：**
1. plan、progress、ticket02：记录D12 failed227/256、未评分；只读RCA继续，另一GPU实验需审批（可直接执行，已更新）。
2. ticket08：03能力已验收；记录8/400与原72h，移除旧03阻塞描述（可直接执行，已更新）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 02：完成256-slot及router/queue只读取证，给出剩余原因与有证据的下一步 → 后续实验先获批准；容量完成仍需至少231有效及原生评分/两次ACK/下一轮评分/source-lifetime。
2. 并行08：保留原72h与400分母，按实际results核验完成数；完成400后才报告avg@4。
3. 04–07：继续等02验收；03不再阻塞，不为已通过03追加新harness或GPU故障实验。

## 4. 最值得关注的 3 点

1. D12单次对照失败227/256；未进入评分，不能评价sourcepatch容量，也不自动重提。
2. 03原生流程通过，但HF3只是1/400；两份qualification HF必须继续保留。
3. baseline核实8个完成结果，4 true/4 false；false不重抽，392缺失。04–07等待02，不等待03或完整baseline。
