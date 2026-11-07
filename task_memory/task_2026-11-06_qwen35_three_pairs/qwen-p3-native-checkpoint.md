## Modification History

| Date | Change |
| --- | --- |
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

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 3

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| P0 | PASS | 任务记录与来源齐备。 |
| P1 | PASS | D1–D16 已确认，C获批从初始权重新跑100步并申请1500GiB student内存。 |
| P2 | PASS | 三组初始 D8 均通过。 |
| P3-A | TODO | 修复已提交，实际CUDA恢复测量通过；待新正式运行验证，旧失败保留。 |
| P3-B | TODO | 与A独立就绪，待实际preload/完整模型及100步验收。 |
| P3-C | TODO | D15/D16准备完成；待新100步和实际1500GiB容量验证，旧1步保留为失败历史。 |
| P4 | BLOCKED | 依赖三组最终验收，当前均未完成。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** exact pinned CPU通过至实际CUDA恢复测量及清理错误定位｜**当前前沿：** 三组正式提交与实际preload/完整模型验收；探针清理独立收尾。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 已取得两周期真实CUDA恢复证据，清理修复限定于已观测API错误；立即解除工具与正式提交的错误依赖，不扩展探针。 |
| D2 细节反复重试 | CLEAR | 本次首个CUDA结果定位明确的私有清理签名错误；精确pinned源码CPU回归1FAIL→1PASS，原始ERROR保留，实际恢复测量已推进。 |
| D3 支线问题修补 | CLEAR | 概率恢复直接阻塞R3；C内存阻塞实际运行；HF资格属于D13。 |
| D4 可并行任务停滞 | CLEAR | 排队期间有明确资源限制；实际功能证据返回后修正S1，三组按现有批准资源并行提交，清理修复不再串行阻塞。 |
| D5 超范围镀金 | CLEAR | 未扩预算、未改参数目标、未引入新训练方案。 |
| D6 分析空转 | CLEAR | reader和owner修复已提交；C作出D16决策并通过配置验证，未继续实现未选的省内存路径。 |
| D7 路线违背 | CLEAR | 直接原始数据证明运行异常后停止；没有按辅助评分自动终止健康训练，没有新增Qwen optimizer probe。 |

**文档检查：** S1：上一版plan/progress及本检查点第54–55条将整个torch-hook探针正常退出绑定于正式提交，但QWEN-P3-CLEANUP-SCOPE证明该私有清理不可达于正式路径，且即使探针通过也不能代替preload/完整模型验收。其余S2–S6未发现新的明显缺陷。
**归因：** 无。

## 3. 纠正建议

**分支：** B：先修正内部依赖，再继续正式运行；需求、预算和最终验收规则保持既有定义。

**文档更新（先执行）：**
1. `plan.md`最新P3前沿和`progress.md`next actions：区分已测CUDA恢复、探针退出和正式preload/完整模型验收；解除仅由工具清理造成的串行依赖（可直接执行，已应用）。

**需停止的偏离行为：无**

**接下去的路线：**
1. 并行提交P3-A/P3-B/P3-C：平台资源/身份/本地源核对后，验证各自新基线、恢复发布及首次真实更新；运行和结果验收分别记录。
2. 并行完成探针清理的完整退出验证；原始ERROR和`cuda_ipc_qualified=false`保持，修复后的GPU退出结果仍待实测。
3. 每组按获准预算核验实际更新、发布、更新后/最终D8及HF，完成后进入P4。已通过的reader、tracker和隔离套件不重复扩大。

**暂缓事项：** 可选rematerialization的失败恢复修复与kernel-only探针记入[future.md](future.md)，引用各自唯一报告；当前C沿正常backup路径。

## 4. 最值得关注的 3 点

1. 两周期物理CUDA IPC和字节/分数恢复已测得正确，整体探针因清理而ERROR；实际formal preload/完整模型证据仍需运行获得。
2. C的1500GiB请求已通过dry-run，只有一个JSON值改变；旧失败update必须保留，新run预算100。
3. D8更新后/最终以及D13最终模型仍缺实际产物；模型容量只由获准正式运行证明。
