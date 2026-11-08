## Modification History

| Date | Change |
| --- | --- |
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

**汇总：** PASS 1｜BLOCKED/FAILED/SKIPPED 6｜TODO 2

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 01 输入 | PASS | 全源visual/普通factory与四组formal配置通过；200/256/50合同及CPU/GPU验证边界明确。 |
| 02 训练与度量 | FAILED | 小批量RKL/TIS/PPO独立重算通过；两组256收集只有206/224有效，未进入student评分。 |
| 03 HF/评测 | TODO | mounts别名修复通过；新运行暴露root目录写权限问题，HF2/HF3隔离仍未执行。 |
| 04 A/full | BLOCKED | 等待02/03及新源验收。 |
| 05 A/r256 | BLOCKED | 等待02/03及新源验收。 |
| 06 B/full | BLOCKED | 等待02/03及新源验收。 |
| 07 B/r256 | BLOCKED | 等待02/03及新源验收。 |
| 08 原始学生基线 | TODO | 已持久化2/400原生成功结果；398缺失、avg@4=null，原72h不变。 |
| 09 比较归档 | BLOCKED | 无正式cell或完整benchmark结果。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 上次worker/reader checkpoint至今｜**当前前沿：** 02收集瓶颈、03本机/worker目录ownership与隔离、08完整评测。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 复用原生dump完成PPO复算；CPU目录准备直接解除03阻塞，没有扩展harness。 |
| D2 细节反复重试 | CLEAR | mounts预测经CPU与新运行验证；错误推进到独立权限边界，停止第三次盲重跑。 |
| D3 支线问题修补 | CLEAR | 03真实共享目录无法写入，直接阻塞已有HF2/HF3验收。 |
| D4 可并行任务停滞 | CLEAR | 02 serving日志分析、03权限修复和08正式评测独立进行。 |
| D5 超范围镀金 | CLEAR | 没有新协议、重试或科学参数；仅修一个本机通知根目录owner，旧子目录/HF未动。 |
| D6 分析空转 | CLEAR | 512 slots归类、PPO误差和2个真实benchmark结果均已有实值；下一实验须基于日志判别。 |
| D7 路线违背 | CLEAR | 231/256、1800s、128K保持不变；未以小批量或历史GLM结果放行正式训练。 |

**文档检查：** S5：02/03状态行仍称tensor审计或snapshot原因待验收，与最新PPO PASS、alias修复和权限失败证据不符；已更新当前阻塞。S1–S4/S6无新缺陷；未把初次吞吐不足宣称为不可达criterion。
**归因：** 无执行偏离；S5结果/状态滞后已修正。

## 3. 纠正建议

**分支：** B：tickets存在状态滞后，先更新记录，不改变scope或验收条件。

**文档更新（先执行，已完成）：**
1. tickets02/03、plan、progress：记录PPO PASS、206/224失败和权限阻塞，保持验收条件（可直接执行，已更新）。
2. native test report：记录原始失败、正确49 pending/48 cancellations区别、单目录owner修复与2/400实值（可直接执行，已更新）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 03：提交前创建本机拥有的共享目录，先通过CPU ordering/soft-gate验证；不改变true-drift guard → 再执行HF2失败/HF3原生评分与reader清理。
2. 并行02：以已有serving日志判别queue/prefill和long decode，得到最小有证据实验；不放宽D6 → 收齐至少231后才验证large-bank scoring/optimizer和受控sourcepatch对照。
3. 并行08：保留原72h与400分母，按实际results核验完成数；04–07继续等待02/03。

## 4. 最值得关注的 3 点

1. 两组失败在生成收集，不在student projection；没有large-bank sourcepatch PASS或OOM判定。
2. 第二个observer问题是root拥有0755目录；CPU/文件系统验证前不再消耗GPU重跑。
3. baseline已有2个真实成功结果，但仍398缺失；最终avg@4不可报告。
