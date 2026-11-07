# Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | 按check-progress检查T2交付状态与路线；父任务状态仅引用既有progress，不修改其他owner文件。 |

## 1. 规划完成情况

**汇总：** PASS 2｜BLOCKED/FAILED/SKIPPED 0｜TODO 2

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| T1 tokenizer/datasets | PASS | 父任务progress记录completed T1；本子任务不重复核查资产。 |
| T2 Lark records | PASS | lark_records.md已完成；31次成功搜索、15份不同正文、模型/数据/模板/结果及缺失字段有来源；精简JSON回执本地核验PASS。 |
| T3 Steptron branches | TODO | 父任务progress仍为in-progress；由另一owner交付。 |
| T4 synthesis/archive | TODO | 等T2/T3整合，由父任务负责。 |

T2子项：搜索/正文读取/来源归纳/本地回执验证PASS；嵌入表读取BLOCKED（缺scope），引用OPD Log的fetch FAILED（3380002）。两项均有错误证据，且requirements明确允许记录不可用字段，故不阻塞有界研究交付。

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** T2分派至本次交付｜**当前前沿：** T3完成及T4交叉核验。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 只用既有CLI与标准库核验，未新建测试框架或持久脚本。 |
| D2 细节反复重试 | CLEAR | 同批表格首次请求失败后一次auth诊断即停止；未改scope或反复重试。 |
| D3 支线问题修补 | CLEAR | 所有读操作用于Qwen记录、数据格式或实际OPD对照；未修外部系统。 |
| D4 可并行任务停滞 | CLEAR | plan明确T1/T2/T3并行，progress有相应owner；本子任务不越权协调。 |
| D5 超范围镀金 | CLEAR | 交付仅lark_records.md及精简lark-*证据，无训练或源代码改动。 |
| D6 分析空转 | CLEAR | 研究本身是T2交付，已形成计划/完成与新旧tokenizer区别，达到有界读取覆盖后停止。 |
| D7 路线违背 | CLEAR | 只使用指定认证CLI，系统只读；未访问GPU/云目录/修改认证/发布/提交Git/委派。 |

**文档检查：** S1–S6均未发现明显缺陷；requirements第17行允许明确缺失字段，故表格scope不构成不可达验收条件。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动。
**需停止的偏离行为：** 无。

**接下去的路线：**
1. 父任务接收T2并等待T3 → 完成标志：固定commit/model/dataset证据能与飞书线索对应。
2. T4综合核查 → 完成标志：回答四模型tokenizer、数据适配及历史Qwen OPD/MOPD记录，分开计划/实际与不可读字段。

## 4. 最值得关注的 3 点

1. 当前三组Qwen3.5在飞书有明确测试计划，但本次可读正文没有其完成回执；不要把Step后半测试记录移植成Qwen运行结果。
2. 旧Qwen3自定义tokenizer新增special tokens，旧小模型论文数据名DAPO-Math-17K不构成当前Qwen3.5 token-ID兼容证明。
3. 七个实验子表缺sheets:spreadsheet:read；已保留错误回执。是否补授权由用户决定，不阻塞当前注明边界的研究交付。
