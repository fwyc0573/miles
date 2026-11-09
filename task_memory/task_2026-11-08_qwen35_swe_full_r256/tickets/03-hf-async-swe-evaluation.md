## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Accept the actual new-data asynchronous isolation and independent phase review; preserve qualification and lifecycle-fixture boundaries. |
| 2026-11-08 | Verify pre-submission directory preparation and cross-UID readiness; retain native isolation as pending. |
| 2026-11-08 | Record verified snapshot fix and the native rerun's separate local directory-ownership blocker. |
| 2026-11-08 | Record the reaccepted D11 prerequisite and the observed dispatch snapshot failure without accepting async isolation. |
| 2026-11-08 | Track D11's reopened input prerequisite while retaining verified evaluator/model capabilities. |
| 2026-11-08 | Verify actual trainedHF3 reload and original/trained native SWE qualification; cloud lifecycle and formal dispatch acceptance remain open. |
| 2026-11-08 | Clear the completed input prerequisite; keep native HF/SWE acceptance in progress. |
| 2026-11-08 | Draft the complete checkpoint-to-evaluation-to-release slice. |

# 03: 打通 HF 异步 SWE 评测与权重释放

**What to build:** 一个训练checkpoint正确保存为最小纯文本HF后立即持久入队，在独立资源上完成指定SWE评测、增量保存结果并安全释放该checkpoint，同时训练可继续。

**Blocked by:** 01 — 模型、数据与benchmark身份契约。

**Status:** done — actual new-data job `exp-1108-234430-904523` verifies HF2 submission-failure isolation, later successful update3, independent2-H200 HF3 reload/native grading and all3 reader exits. Independent phase review `ses_e43dee3a4ffe7TwCS350olE3Pw` supports capability acceptance with no unmet criterion or actionable code defect. Existing eight actual-cloud-filesystem fixtures verify complete400 persistence, missing-only recovery, deadlines and reader-safe HF200 deletion; they are not native benchmark results. Native qualification remains1/400 with null avg@4; both HF2/HF3 stay retained. Evidence: `../test_report_2026-11-09_native_async_isolation.md` and `../evidence/checkpoint_t03_native_async_acceptance.md`.

- [x] 复用Qwen HF导出路径，保存正确dtype/config/tokenizer和成功update/weight-version identity；无额外训练或optimizer权重。
- [x] 实际重载可生成文本，完成标记晚于全部文件写入；导出部分失败不会被评测消费。
- [x] 复用参考SWE agent/grader与已冻结100题、4 attempts规则；原生少量题验证真实环境、请求模板和评分，不用mock评分代替。
- [x] 同一题/seed/attempt稳定标识；一个请求悬挂时，其他完成结果立即持久化；有限超时和恢复按spec执行。
- [x] 评测入队/重启不重复覆盖已完成结果；资源统计计入异步评测，训练不等待完整benchmark。
- [x] 结果完整且reader退出后删除本任务HF，包括HF200；D10未完成时保留，只补缺失slot，72h绝对deadline跨恢复不续期，到期报告并保留HF。
- [x] 保存benchmark ledger、identity、实际删除文件/bytes receipt；源模型与历史A/B验收HF不进入清理目标。
- [x] 与02完成一次真实训练→导出→独立评测的集成验证，并实测评测异常不级联中止健康训练。
