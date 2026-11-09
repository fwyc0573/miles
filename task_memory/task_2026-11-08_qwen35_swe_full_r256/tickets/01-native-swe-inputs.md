## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Reaccept D11 inputs after real native factory and formal four-cell source/budget transport pass; GPU consumption remains owned by02/03. |
| 2026-11-08 | Accept genuine full-source native visual/factory validation and real four-cell smoke source transport; formal-profile parsing remains the final configuration item. |
| 2026-11-08 | Record actual representative parity and overlap completion; retain full-source visual receipt and ordinary factory activation as the remaining input gate. |
| 2026-11-08 | Reopen source-dependent criteria after D11 replaces GLM-5.2 with the specified DeepSWE dataset. |
| 2026-11-08 | Accept actual-source parity, four independent cursors, model identity and the qualified overlap audit. |
| 2026-11-08 | Draft the end-to-end native-input parity slice. |

# 01: 对齐 Steptron 默认 SWE 数据加载

**What to build:** D11指定的SWE原始数据经Steptron默认加载与Miles适配后，得到语义一致、来源可追踪的训练turn；四个实验配置共用冻结的数据和模型身份契约。

**Blocked by:** Documentation freeze（访谈决策完成且用户确认）。

**Status:** done — D11 source identity,full-source native visual receipt,ordinary factory,representative parity,qualified overlap audit and all four formal source/budget contracts verified. CPU typed transport does not replace GPU-dependent Megatron validation. Tickets02/03 own actual new-input native consumption and integration.

- [x] 根据当前spec，解析D11实际默认源配方、记录选择、turn顺序、shuffle/seed、过滤、长度与模板规则，区分历史replay定制规则。
- [x] 用实际多轮样本逐阶段比较原始消息、assistant-turn边界、prompt与来源identity；记录不一致和其修复，禁止把旧输入结果当作替换后数据验收。
- [x] 验证 Qwen student/teacher token IDs及有效模板契约，冻结两个教师与共同初始化来源。
- [x] 提供四个配置实际可消费的数据receipt和已解析配置；样本数量与重复策略满足最终确定的full/r256预算，不静默改采样。`deepswe_formal_config.json`及`evidence/deepswe-formal-launcher-inputs.json`绑定真实六字段契约；full200×1、r2564×50、256目标和save50保持不变。完整GPU parser/startup验证不在此CPU结论内。
- [x] 确认benchmark 100题与D11训练数据关联检查采用已批准规则；未能核验的来源明确列出。
- [x] Native对照命令、实际样例identity和差异结论进入本任务测试报告；数据阻塞不标为PASS。
