## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Apply D18 H200 frontier after device-identity regression checks; stop optional memory diagnostics from becoming a formal-launch dependency. |
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

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 2｜TODO 2

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| P0 | PASS | 任务记录与来源齐备。 |
| P1 | PASS | D1–D18 已确认；A/B改H20020卡，限制32卡内不可抢占；C保留H800。 |
| P2 | PASS | 三组初始 D8 均通过。 |
| P3-A | TODO | H200 exp-1107-173758-712234已提交/Starting，平台配置PASS；实际训练待验收。 |
| P3-B | TODO | H200 exp-1107-173758-806531已提交/Starting，student8H200实测；D17 fresh100。 |
| P3-C | BLOCKED | 既有D15/D16作业仍待调度；没有新增B容量依赖。 |
| P4 | BLOCKED | 依赖三组最终验收，当前均未完成。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** B首步/OOM检查点至D18及设备身份修正｜**当前前沿：** 并行提交P3-A/B H200；P3-C保留原有H800队列。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | D18后停止可选CUDA诊断扩展；设备guard是实际启动阻塞，相关检查通过后转提交。补充pinned复跑不串行阻挡队列。 |
| D2 细节反复重试 | CLEAR | namespace取证错误按实际模块修正；硬编码guard RED→修正通过，没有轮换allocator参数试错。 |
| D3 支线问题修补 | CLEAR | 旧H800存储问题转future.md；当前仅修H200启动真正经过的设备检查。 |
| D4 可并行任务停滞 | CLEAR | A/B共享guard准备并将同时提交；C持续排队且平台仅余14H800，需求24。 |
| D5 超范围镀金 | CLEAR | 只把现有gpu_tag传到两处检查；没有优化器、TP、上下文或数值设置扩展。 |
| D6 分析空转 | CLEAR | manifest/原生dry-run已通过，相关CPU回归通过；前沿由H800诊断转为D18提交。 |
| D7 路线违背 | CLEAR | H200由新D18明确授权；额外optimizer probe和自动追加restart仍未发生。 |

**文档检查：** S1：旧“先完成H800容量修复再提交”边与D18已选硬件路线不符；S5：旧全H800状态/检查点须同步D18。requirements、plan、progress已更新；本检查点同步修正。S2/S3/S4/S6未发现新缺陷。
**归因：** 无。

## 3. 纠正建议

**分支：** B：同步D18与真实依赖后直接执行获准提交。

**文档更新（先执行）：**
1. `requirements.md`记录D18；`plan.md`、`progress.md`记录A/B H20020卡与32卡上限，C继续独立（用户已确认，已应用）。
2. 本检查点与H200报告区分准备PASS、补充pinned pending和实际runtime未验证；移除非必要串行边（可直接执行，已应用）。

**需停止的偏离行为：无**

**接下去的路线：**
1. P3-A/B并行：保持两个H200正式launcher并核验运行 → 完成标志：完整8+2 H200、baseline/恢复/更新及最终产物逐项验收；平台身份/挂载/请求已PASS。
2. 并行：P3-C既有提交继续等待调度 → 完成标志：实际GPU/cgroup、新baseline、恢复和首步内存均取得证据。
3. 各组按批准预算推进更新后/最终D8和HF → 完成标志：完整100位置及最终产物分别验收，随后P4。

**暂缓事项：** 可选rematerialization、kernel-only探针与Megatron输出寿命修复均在[future.md](future.md)；当前C保留正常backup路径。

## 4. 最值得关注的 3 点

1. A/B已并行提交并获准入，Starting，20张不可抢占H200小于32卡上限；B student实际8H200已确认。
2. 固定镜像90项通过，3项旧baseline toy-actor fixture失败已分配独立修复；设备检查及native parser均PASS。
3. C仍受最后观测的14卡可用配额约束；所有新的正式基线、更新后/最终D8与HF验收须等待实际运行。
