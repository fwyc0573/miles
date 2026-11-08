## Modification History

| Date | Change |
| --- | --- |
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
| 02 训练与度量 | FAILED | 旧两组256收集仅206/224；D12独立routing对照已准入，容量/两次更新/source-lifetime仍未验收。 |
| 03 HF/评测 | PASS | 实际HF2故障不阻止update3；HF3重载/grader/3reader退出通过，独立review GO。 |
| 04 A/full | BLOCKED | 等待02实际容量与完整原生训练验收。 |
| 05 A/r256 | BLOCKED | 等待02；D12不是正式profile变更。 |
| 06 B/full | BLOCKED | 等待02。 |
| 07 B/r256 | BLOCKED | 等待02。 |
| 08 原始学生基线 | TODO | 已持久化2/400原生成功结果；398缺失、avg@4=null，原72h不变。 |
| 09 比较归档 | BLOCKED | 无正式cell或完整benchmark结果。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 上次acquisition/permission checkpoint至今｜**当前前沿：** 02批准的D12容量对照、08完整评测；03已完成。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 目录准备只解除真实03阻塞；原生路由transport仅两行，未另造router/harness。 |
| D2 细节反复重试 | CLEAR | CPU/cross-UID判别后真实03通过；D12在queue不均测量及用户批准后仅改路由。 |
| D3 支线问题修补 | CLEAR | ownership修复在03路径；路由直接检验02的有效样本不足。 |
| D4 可并行任务停滞 | CLEAR | 02配置/准入、03原生评分/验收、08正式评测独立推进。 |
| D5 超范围镀金 | CLEAR | D12明确批准单次隔离A/r256；默认216 argv完全一致，正式profile未改。 |
| D6 分析空转 | CLEAR | 512 slots与1083 serving观察收敛为routing-only决策，已实际准入；03完成。 |
| D7 路线违背 | CLEAR | D12已记录原始批准；231/1800/128K/n1/max1/graphFalse/TP2保持，04–07未提前启动。 |

**文档检查：** S5：03待验收及D12未提交状态落后于原生grader/review GO和实际admission，已更新tickets/plan/progress；fault时间已按原始文件纠正。S1–S4/S6无新缺陷；吞吐不足不是不可达criterion的证明。
**归因：** 无执行偏离；S5状态/时间滞后已修正。

## 3. 纠正建议

**分支：** B：tickets存在状态滞后，先更新记录，不改变scope或验收条件。

**文档更新（先执行，已完成）：**
1. ticket03、plan、progress：将实际流程能力验收标done，保留1/400/null与fixture/真实benchmark边界（可直接执行，已更新）。
2. native test report/review：从fault.json纠正时间为1794153345.1932557，并记录update3晚350.20s；D12记录实际准入且不改正式profiles（可直接执行，已更新）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 02：核对D12实际router/engine/GPU身份 →1800s至少231有效 → 两次原生optimizer ACK/第二轮scoring/source-lifetime；未达标保留证据，不扩展为额外未批准实验。
2. 并行08：保留原72h与400分母，按实际results核验完成数；完成400后才报告avg@4。
3. 04–07：继续等02验收；03不再阻塞，不为已通过03追加新harness或GPU故障实验。

## 4. 最值得关注的 3 点

1. D12只批准一个A/r256对照，现请求10张H200、baseline2张；容量和sourcepatch仍未通过。
2. 03原生流程通过，但HF3只是1/400；两份qualification HF必须继续保留。
3. baseline最近核实2个真实成功结果，仍不完整；04–07等待02，而不是等待03或完整baseline。
