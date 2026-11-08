## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the end-to-end native-input parity slice. |

# 01: 对齐 Steptron 默认 SWE 数据加载

**What to build:** 同一份 GLM-5.2 SWE 原始数据经 Steptron 默认加载与 Miles 适配后，得到语义一致、来源可追踪的训练 turn；四个实验配置共用冻结的数据和模型身份契约。

**Blocked by:** Documentation freeze（访谈决策完成且用户确认）。

**Status:** ready — documentation frozen; implementation not started

- [ ] 根据已冻结spec，解析实际默认源配方、记录选择、turn顺序、shuffle/seed、过滤、长度与模板规则，区分历史 replay 定制规则。
- [ ] 用实际多轮样本逐阶段比较原始消息、assistant-turn边界、prompt与来源identity；记录不一致和其修复，禁止把旧Qwen小数据集当本次原始输入。
- [ ] 验证 Qwen student/teacher token IDs及有效模板契约，冻结两个教师与共同初始化来源。
- [ ] 提供四个配置实际可消费的数据receipt和已解析配置；样本数量与重复策略满足最终确定的full/r256预算，不静默改采样。
- [ ] 确认 benchmark 100题与训练数据关联检查采用最终已批准规则；未能核验的来源明确列出。
- [ ] Native对照命令、实际样例identity和差异结论进入本任务测试报告；数据阻塞不标为PASS。
