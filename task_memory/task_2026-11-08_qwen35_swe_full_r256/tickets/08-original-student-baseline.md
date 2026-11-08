## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Advance observed ledger to10/400 (4 true,6 false),with the original deadline unchanged. |
| 2026-11-09 | Advance observed ledger to9/400 (4 true,5 false),with the original deadline unchanged. |
| 2026-11-09 | Record8/400 outcomes and correct03 to capability-accepted; preserve the original72h deadline and incomplete baseline. |
| 2026-11-08 | Accept the baseline-specific model/task/evaluator prerequisites after independent readiness review; retain the dependency edges and pending400-result acceptance. |
| 2026-11-08 | Distinguish still-qualified model/benchmark identities from D11's reopened training-input criteria. |
| 2026-11-08 | Clear the completed input prerequisite; retain native evaluation as the remaining blocker. |
| 2026-11-08 | Renumber from 09 to 08 so ticket numbers follow dependency order; the final comparison is now 09. |
| 2026-11-08 | Add the explicitly approved shared original-student baseline under D8. |

# 08: 完成四cell共同原始学生基线

**What to build:** 使用原始Qwen3.5-4B完成与16个训练checkpoint相同的SWE100题×4评测，为full/r256结果提供一个共同起点。

**Blocked by:** 01 — 原始模型与题集身份；03 — 原生SWE评测能力。

**Status:** in-progress — 01 and03 capability prerequisites are accepted. Formal400-attempt job exp-1108-215214-032806 continues on2 non-preemptible H200 GPUs,with10 persisted outcomes (4 true,6 false),390 missing and no full avg@4. Original72h deadline is unchanged; model-false outcomes are not rerolled. Complete ledger,score and terminal acceptance remain pending.02 capacity still gates04–07,not this baseline.

- [ ] 使用四cell共同的原始4B源权重，任务IDs、seeds、模板、精度和native grader与训练checkpoint评测一致。
- [ ] 完成400个逻辑attempt；每个完成结果即时保存，基础设施缺失按同一协议恢复且不缩分母。
- [ ] 归档baseline avg@4、完整ledger、有效请求配置和资源/业务终态；原始模型不复制、不清理。
- [ ] 可与04–07正式训练并行，服从共同GPU上限；baseline完成不人为阻塞这些训练票。
