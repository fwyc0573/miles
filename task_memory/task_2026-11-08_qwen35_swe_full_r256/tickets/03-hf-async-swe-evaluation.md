## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the complete checkpoint-to-evaluation-to-release slice. |

# 03: 打通 HF 异步 SWE 评测与权重释放

**What to build:** 一个训练checkpoint正确保存为最小纯文本HF后立即持久入队，在独立资源上完成指定SWE评测、增量保存结果并安全释放该checkpoint，同时训练可继续。

**Blocked by:** 01 — 模型、数据与benchmark身份契约。

**Status:** in-progress — independent development authorized; integration and acceptance blocked by 01

- [ ] 复用Qwen HF导出路径，保存正确dtype/config/tokenizer和成功update/weight-version identity；无额外训练或optimizer权重。
- [ ] 实际重载可生成文本，完成标记晚于全部文件写入；导出部分失败不会被评测消费。
- [ ] 复用参考SWE agent/grader与已冻结100题、4 attempts规则；原生少量题验证真实环境、请求模板和评分，不用mock评分代替。
- [ ] 同一题/seed/attempt稳定标识；一个请求悬挂时，其他完成结果立即持久化；有限超时和恢复按spec执行。
- [ ] 评测入队/重启不重复覆盖已完成结果；资源统计计入异步评测，训练不等待完整benchmark。
- [ ] 结果完整且reader退出后删除本任务HF，包括HF200；D10未完成时保留，只补缺失slot，72h绝对deadline跨恢复不续期，到期报告并保留HF。
- [ ] 保存benchmark ledger、identity、实际删除文件/bytes receipt；源模型与历史A/B验收HF不进入清理目标。
- [ ] 与02完成一次真实训练→导出→独立评测的集成验证，并实测评测异常不级联中止健康训练。
