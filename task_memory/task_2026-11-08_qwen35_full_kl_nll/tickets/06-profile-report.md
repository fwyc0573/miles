## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record delivered CPU join plus open review repairs/regression/re-review; keep actual A/B report data and all four final criteria incomplete. |
| 2026-11-10 | Separate independent CPU report preparation from actual A/B measurements and final acceptance, following the user's parallel-execution instruction. |
| 2026-11-09 | Require honest complete/incomplete reporting, verified paired prefixes and non-causal interpretation of normalized gaps. |
| 2026-11-08 | Draft the final report ticket. |
| 2026-11-08 | Rename the reported KL quantities to RKL (D21). |
| 2026-11-08 | Add the remaining gap, the run-relative gap and the baseline counts to the report (D28–D31). |

# 06: Profile 报告与归档

**What to build:** 根据保留的文件，按 [spec S9](../spec.md#s9-验证与交付) 生成两个 cell 的报告，并写 `summary.md`。

**Blocked by:** CPU dependency 03 已满足且initial CLI join PASS；offline inspector/reporter review findings open/fixing，需完成后的joined regression/re-review。正式数据/最终验收仍依赖 04、05 的真实native/terminal/profile证据；保留CPU准备与最终数据split，不能用fixtures或缺失记录填造结果。

**Status:** TODO — initial CPU join PASS; review repairs and final native report TODO. Inspector`a76fc527`57 tests/reporter`e6956e3c`26 tests/CLI4 PASS remain in[the actual proof report](../test_report_2026-11-10_offline_report_integration.md)and`evidence/offline-report-join-20261110.json`: hand4-update baseline0.59375, synthetic200 complete, synthetic native200/partial profile, retained first H800 Failed with actual count=null. Fixed six-path review`d822174c..a76fc527`found4 functional+1 naming nit, all open/fixing ([review](../review.md#offline-inspectorreport-phase-review--2026-11-10)). Inspector/reporter agents repair in parallel with native A, followed by joined regression/re-review; no fix result is assumed. A has actual18H200/Ray/first-bank generation, not firstACK/GPU-profile acceptance. Four final checkboxes remain unchanged and unchecked; CPU fixtures are not formal data.

CPU 准备范围：复用已有 `DistillationProfile` 查询和重建语义，实现S9统计及报告输出；与04/05的只读native/profile核验入口组合检查。合成记录只验证手算值和完整/不完整处置，已保留的失败attempt只验证真实失败的归档路径。保留原始文件，不修改训练路径，不引入新的GPU smoke或辅助硬门。以下最终验收项需真实A/B数据，CPU通过后仍不勾选。

- [ ] 从已验证、成对一致的 JSONL 记录重新计算 S9 的宏观值：选定 update 的 RKL/NLL 和 remaining gap、宏观 baseline、RKL-best update、默认 k 下的 RKL trend 和 recovery gap。baseline 不完整或值未验证时写 null / unverified，不从部分文件或不一致内存补造。
- [ ] 列出 S9 中训练结束时的 profile 统计：各类 conversation 计数（含 baseline 为正和 ≤ 0），以及 conversation remaining gap、run-relative gap、trend、recovery gap 的分位数。
- [ ] 分别报告 native successful update 数、native terminal status 与完整 profile 的验收；S7 失败列出完整核验前缀、首次错误和全部缺失 / 未验证区间。允许归档 INCOMPLETE 报告，不能因 healthy training 完成而宣称 profile 完整。
- [ ] 写明准确的云端路径、未验证的 update、观察到的局限，以及结论适用的范围（例如两个 cell 各只有一组 seed）。无量纲 remaining gap / trend / run-relative gap 不建立跨 teacher、模型或 turn 组成的受控比较；模型大小不证明严格正的最小 RKL，remaining gap 不等于仍可优化的比例。审计的 prompt hash 只作 exact-text proxy，native SWE instance / repository identity 的核验覆盖率另列。
