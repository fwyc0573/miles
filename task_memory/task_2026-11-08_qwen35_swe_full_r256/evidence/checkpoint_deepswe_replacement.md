## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Accept existing-guard verification and primary5-case rerun; nextdependentfrontier is the scoped resource choice. |
| 2026-11-09 | Check D13 diagnosis/correction and baseline10/400; close repeated-log analysis and require a scoped resource decision before new native execution. |
| 2026-11-09 | Verify retained policy/metadata evidence and baseline9/400; continue only the specific missing-log RCA without another GPU trial. |
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
| 08 原始学生基线 | TODO | 已持久化10/400结果，4 true/6 false；390缺失，原72h不变，无完整avg@4。 |
| 09 比较归档 | BLOCKED | 无正式cell或完整benchmark结果。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 77cfa618 checkpoint至今｜**当前前沿：** 02rollout资源选择、08完整评测；原始日志RCA和现有deadline验证已完成。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 发现现有Qwen总超时后撤回共享HTTP改动；只验证已部署机制，不增加第二套deadline。 |
| D2 细节反复重试 | CLEAR | D12是事先记录queue假设且获批的单次检验；失败后未再提交。 |
| D3 支线问题修补 | CLEAR | D13明确要求有限timeout和条件扩容；teacher输入边界只取证，没有擅自修包络。 |
| D4 可并行任务停滞 | CLEAR | 02的deadline/拓扑调查并行，08持续9→10结果；未暂停基线。 |
| D5 超范围镀金 | CLEAR | 共享HTTP补丁被取消；多节点只准备选择，未扩容或更改formal参数。 |
| D6 分析空转 | CLEAR | full-log核验完成512payload/4engines/teacherguard，当前转向有成本的资源选择；不再索取同一日志中的缺失字段。 |
| D7 路线违背 | CLEAR | D13原话已记录；仍保留231/1800/128K/n1/max1/graphFalse/TP2，04–07未启动。 |

**文档检查：** S5：ticket02仍称原始日志RCA进行中并未记录D13；plan/ticket08尚是9/400，与最新分析和10结果不一致。S1–S4/S6无新缺陷；失败不证明231门槛不可达。
**归因：** 无执行偏离；S5状态与授权记录需同步。

## 3. 纠正建议

**分支：** B：ticket状态与D13记录滞后，先同步，不改变验收条件。

**文档更新（先执行，已完成）：**
1. plan、progress、ticket02：原始日志RCA已完成，现有总超时已部署；记录D13条件授权与18/26卡可选拓扑（可直接执行，已更新）。
2. ticket08：同步10/400与原72h，false不重抽（可直接执行，已更新）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 02：现有deadline故障注入已通过93+8regressions和primary5-case rerun；生产/共享HTTP未改，总时限覆盖retry/sleep/read，取消与typed hook路径已核验（完成）。
2. 02：确认D13是否适用于当前非已证实KV/503的队首阻塞，选择18卡半共置或26卡解耦 → 完成标志：owner确认范围/成本，CPU配置与多节点生命周期通过，然后fresh admission和原生231/评分/两次ACK/下一轮评分/source-lifetime验收。
3. 并行08：保留原72h/400分母，按实际results核验；400完成后才报avg@4。
4. 04–07：继续等02；不为已通过03追加harness或GPU故障实验。

**暂缓事项：** teacher131070>131066输入包络修正 → `issues.md`已有失败证据；未获批准，不auto-truncate。

## 4. 最值得关注的 3 点

1. D12仍227<231且未评分；不自动重提、改max1或以startup-health503冒充KV证据。
2. 当前SWE已有总超时；扩8卡必须真正把4服务变8，18卡方案需修参数入口，26卡方案成本更高，二者尚未获本次队首阻塞用途确认。
3. baseline10/400，4true/6false，390缺失且原72h不变；04–07继续等待02，不等待03或完整baseline。
