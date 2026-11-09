| Date | Modification History |
| --- | --- |
| 2026-11-08 | Check the post-smoke frontier after real completion-only audit, capacity OOM and native evaluator repair. |

## 1. 规划完成情况

**汇总：** PASS1｜BLOCKED/FAILED/SKIPPED7｜TODO1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 01 输入 | PASS | 已提交并验收的原生loader与身份对照。 |
| 02 训练/指标 | FAILED | 四短smoke与独立张量审计通过；256负载评分OOM，梯度observer的组合CLI注册失败正在修复。 |
| 03 HF/异步评测 | TODO | 实际HF3资格验证、原始4B缺失attempt恢复与dispatch收口并行。 |
| 04 A/full | BLOCKED | 等02、03验收。 |
| 05 A/r256 | BLOCKED | 等02、03验收。 |
| 06 B/full | BLOCKED | 等02、03验收。 |
| 07 B/r256 | BLOCKED | 等02、03验收。 |
| 08 原始学生基线 | BLOCKED | 等03；少量qualification不冒充基线。 |
| 09 比较 | BLOCKED | 等04–08真实结果。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** `checkpoint_native_smokes.md`后的实际短smoke验收到当前容量/评测验证｜**当前前沿：** 02、03。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 现有dump完成独立审计；只为02明确的真实梯度标准补observer，为03补原生资格/dispatch入口。 |
| D2 细节反复重试 | CLEAR | 两条容量对照首次暴露同一OOM，先保存trace未盲调；评测环境修复有实际missing-env red/green证据；单次恢复命令字段错误已明确修正。 |
| D3 支线问题修补 | CLEAR | critical终态、私有环境传递、失败时drain均直接阻塞02/03。 |
| D4 可并行任务停滞 | CLEAR | 梯度与HF3各自已准入；新暴露的observer注册失败已分派修复，容量RCA、HF3与原始4B恢复持续独立推进。 |
| D5 超范围镀金 | CLEAR | 用户RKL澄清保留原有计算，无新增估计器/采样；qualification复用正式账本且不造分数。 |
| D6 分析空转 | CLEAR | 每个调查落到真实失败、CPU修复或原生运行；旧任务已有lifetime证据仅读取复用，不重启其暂停工作。 |
| D7 路线违背 | CLEAR | 未启动正式cell；D2提示语误解已按用户回答撤回，实际训练数学未变。 |

**文档检查：** S1–S6未发现当前未解决的文档缺陷。容量失败由02拥有；实际梯度与少量原生SWE的完成条件明确；03通过前的资格验证不等于开始08正式基线。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 02：从保存的真实256批次定位评分显存占用，验证最小修复并完成实际gradient/finalizer/optimizer核对 → 完成标志为本票原生数学与代表性容量标准。
2. 并行03：完成HF3重载/真实agent/grader、原始4B原期限内缺失slot恢复及实际异步dispatch → 完成标志为本票发布、评测、恢复与reader生命周期标准。
3. 两票通过后进入04–08并行准入；不把小smoke或null评测当作正式结果。

## 4. 最值得关注的3点

1. 256条已全部生成/评分完成，故容量故障定位在当前student评分的GPU输出投影，不能用减少候选数掩盖。
2. RKL只计completion且每次使用当前student重算，真实tensor已证明prompt排除；原D2不变。
3. HF3与原始4B资格验证都必须获得真实SWE结果；当前尚无该原生结果或正式benchmark得分。
