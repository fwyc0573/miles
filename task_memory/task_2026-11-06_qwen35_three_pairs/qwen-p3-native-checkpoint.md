## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Actual B preload restoration/baseline/first publication pass; record later projection OOM, A0-update stop, D17 and independent C scheduling. |
| 2026-11-07 | Corrected H800 diagnostic completes two cycles and all exits successfully; formal jobs are submitted and queued, so stop diagnostic work and await actual formal evidence. |
| 2026-11-07 | Separate probe cleanup from formal execution after real CUDA restoration measurements; correct S1 while preserving the failed diagnostic artifact and actual formal acceptance requirements. |
| 2026-11-07 | Recheck the stalled frontier on continuation: exact14:45 platform status is Queued and the owning Python launcher remains alive; no new execution or scope change. |
| 2026-11-07 | Exact pinned CPU cycles now pass; record committed D16/probe implementation and the sole remaining queued CUDA restoration prerequisite. |
| 2026-11-07 | Check D16's rendered memory allocation and pinned API failures; close reader/isolation work and keep actual CUDA restoration as the remaining shared prerequisite. |
| 2026-11-07 | Apply D15 and pinned tracker closure; close source/CPU publication P1 and retain actual IPC, test isolation and C memory qualification as the frontier. |
| 2026-11-07 | Recheck after actual TMS causal evidence, 67 core CPU checks and native HF content qualification; keep full-exit cleanup and restoration contracts open. |
| 2026-11-07 | Recheck after confirmed raw probability corruption and C OOM; apply stale-frontier correction and preserve consumed-step accounting. |
| 2026-11-07 | Close preparation blockers after76 pinned checks and phase review; advance A/B submission while native text-loader reconstruction proceeds independently. |
| 2026-11-07 | Recheck after verified commits and lifecycle preflight; retain independent C/native-loader progress while A/B preparation is blocked. |
| 2026-11-07 | Check the P3 memory/reload milestone and stop repetition of known incompatible CPU-forward tests. |

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 4｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| P0 | PASS | 任务记录与来源齐备。 |
| P1 | PASS | D1–D17 已确认；B/C分别获得一次新100步授权，C student1500GiB。 |
| P2 | PASS | 三组初始 D8 均通过。 |
| P3-A | BLOCKED | 同一4B TP2/GPU-optimizer容量路径，训练开始前停止，实际0更新。 |
| P3-B | FAILED | 新基线和恢复通过，发布1次真实更新；下一轮输出投影GPU OOM。 |
| P3-C | BLOCKED | 既有D15/D16作业仍待调度；没有新增B容量依赖。 |
| P4 | BLOCKED | 依赖三组最终验收，当前均未完成。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 上次CUDA完整退出检查点至B首步通过、后续OOM及D17确认｜**当前前沿：** P3-A/B显存原因与最小修正；并行等待P3-C调度。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 已关闭小型探针；使用原有inspector和原始事件完成正式验收取证，没有扩展工具。 |
| D2 细节反复重试 | CLEAR | 新失败发生于下一轮输出投影；未盲目重投，先记录三条可区分的容量假设。 |
| D3 支线问题修补 | CLEAR | 新OOM直接阻塞P3-A/B的100步；其余已通过工具没有再修。 |
| D4 可并行任务停滞 | CLEAR | 原三组同时提交；有明确配额限制，C保持独立，两个源代码核查并行且不重叠。 |
| D5 超范围镀金 | CLEAR | 尚未改变优化器/上下文；B的新100步获得D17明确授权。 |
| D6 分析空转 | CLEAR | 新增原始证据明确了baseline PASS、同版本恢复、1次更新、后续OOM和A0更新。 |
| D7 路线违背 | CLEAR | A暂停依据实际同配置容量失败；B重新开始前先取得预算授权，无额外optimizer探针。 |

**文档检查：** S5：`plan.md`步骤表/最新前沿及`progress.md`next actions仍写A/B0更新、三组排队、正式preload未观察，与新原始事件及D17冲突。S1/S2/S3/S4/S6未发现新的明显缺陷。
**归因：** 无。

## 3. 纠正建议

**分支：** B：更新实际状态和已批准预算，再继续容量诊断及独立C运行。

**文档更新（先执行）：**
1. `requirements.md`记录D17；`plan.md`、`progress.md`更新B1/A0、容量阻塞和独立C状态（用户预算确认已取得，其余可直接执行，已应用）。
2. `test_report_2026-11-07_training.md`保留正式baseline/完整checksum/更新及原始OOM证据，限制结论范围（可直接执行，已应用）。

**需停止的偏离行为：无**

**接下去的路线：**
1. P3-A/B：区分评分存储生命周期、optimizer常驻和形状/分配器因素 → 完成标志：真实调用路径的原因与最小修正得到验证，满足上下文/优化器/预算约束后恢复获准运行。
2. 并行：P3-C既有提交继续等待调度 → 完成标志：实际GPU/cgroup、新baseline、恢复和首步内存均取得证据。
3. 各组按批准预算推进更新后/最终D8和HF → 完成标志：完整100位置及最终产物分别验收，随后P4。

**暂缓事项：** 可选rematerialization的失败恢复修复与kernel-only探针记入[future.md](future.md)，引用各自唯一报告；当前C沿正常backup路径。

## 4. 最值得关注的 3 点

1. B真实preload/4B基线和同版本恢复通过，4cells×1416个checksum零差异，已有1次真实发布更新。
2. B随后输出投影19.12GiB申请失败；A0更新暂停，D17批准B修复后重新100步，原因尚待区分。
3. C仍受调度资源约束；各组更新后/最终D8及HF均未完成，不能把阶段PASS当作任务验收。
