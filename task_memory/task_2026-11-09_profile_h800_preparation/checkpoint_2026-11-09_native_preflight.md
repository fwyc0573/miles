Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Check terminal startup failure, parallel node-network RCA and verified session cloud cleanup. |
| 2026-11-09 | Check the submitted native prerequisite and advance the frontier from submission to worker/runtime acceptance. |
| 2026-11-09 | Check the repair/receipt milestone and correct the route toward real H800 capacity execution. |
| 2026-11-09 | Accept the completed pinned-image original-source parity and advance the frontier to native H800 submission. |

## 1. 规划完成情况

**汇总：** PASS 7｜BLOCKED/FAILED/SKIPPED 2｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Plan1：无数量上限 admission | PASS | `1ae93261`，25+4 项检查。 |
| Plan2：H800 配置与资源形状 | PASS | 36 卡、4 个 student 节点；原生配置解析得到2个同机和6个专用 TP4 引擎。 |
| Plan3：完整 CPU 启动前验证 | PASS | `0e7e0df3` 修复 replay 覆盖，62项受影响检查通过，review 关闭P1；真实提交环境 dry-run 通过。 |
| Plan4：合入 parent | BLOCKED | D1/D22 未通过。 |
| Plan5：native 长度参数 | PASS | 128K/112K/16K 分别传到既有参数。 |
| Plan6：混合权重 session 修复 | PASS | `422a613d` 与上游实现一致，37 项受影响检查通过；此前固定 diff review 无发现。此状态只覆盖修复与 CPU/source 验证。 |
| Plan7：原位输入准备 | PASS | native baseline/visual/filter 完成；真实 parity 在 exp-1109-172310-849823 通过，平台 Succeeded。 |
| Plan8：H800 native 容量验收 | FAILED | exp-1109-181120-274261在首次权重同步前失败；未进入bank采集或optimizer更新。 |
| Plan9：native启动RCA与修复 | TODO | 首个错误已定位到rank2的ncclGetUniqueId；真实环境传递CPU regression/fix由明确owner执行。 |
| Plan10：session云端清理 | PASS | 167文件全部本地留存并逐文件校验；删除15,325,989逻辑bytes，独立复查目录为空。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 上次native startup checkpoint至本次terminal RCA与云清理完成｜**当前前沿：** Plan9，native启动原因的CPU验证与修复。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 云清理是用户明确要求；只保留并验证现有167文件，不新增通用清理工具。 |
| D2 细节反复重试 | CLEAR | 首次H800失败后未重投GPU；先列出三个原因并用实际NCCL CPU对照缩小范围。 |
| D3 支线问题修补 | CLEAR | native错误阻塞Plan8，Plan9明确接管；Plan10由用户授权。 |
| D4 可并行任务停滞 | CLEAR | 代码环境传递RCA与primary云端留存/清理并行推进；平台操作由primary负责。 |
| D5 超范围镀金 | CLEAR | 无新增timeout、NCCL workaround、模型或协议；清理仅限终态session目录。 |
| D6 分析空转 | CLEAR | 从全量业务日志确认最早错误，建立网卡存在/不存在CPU对照；错误原因与下一验证owner明确。 |
| D7 路线违背 | CLEAR | 未把CPU或提交结果当容量通过；D1/D22、D34、个人云路径及原位源数据均保留。 |

**文档检查：** 原先仍称launcher运行中的S5记录已按终态证据修正；Plan9/10已接管新阻塞与用户清理要求。S1–S6无剩余明显缺陷。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Plan9：完成真实caller环境传递RED→GREEN与受影响检查 → 完成标志：节点本地平台网卡/HCA值不被首节点覆盖，固定diff复核通过。
2. Plan8：确认修复与fresh admission后进行受影响native验证 → 完成标志：八引擎和初始同步、231/256 within1800s、两次ACK及第二次评分均有真实证据。
3. Plan4：仅在D1/D22真实通过后接入parent。Plan10已完成；后续终态smoke按同样的授权边界及时清理，不扩展到共享trash或其他任务。

## 4. 最值得关注的 3 点

1. 首个H800作业失败在NCCL bootstrap；后续matches=[]不是最早错误，尚无容量通过证据。
2. 当前只验证修复原因，不盲目改timeout或重投；D1/D22仍阻塞parent接入。
3. 云端167个重复文件已清除，诊断副本逐文件校验后留在本地；只报告15.3MB逻辑占用减少，物理OSS回收未测量。
