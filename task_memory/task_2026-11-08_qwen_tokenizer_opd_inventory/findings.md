# Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | 汇总当前tokenizer实证、手册数据、Lark记录和Steptron固定分支记录。 |

# Qwen tokenizer、数据集与 OPD/MOPD 记录汇总

## 核心结论

1. **当前三组的四个Qwen3.5模型使用相同tokenizer。** 实际来源的 `tokenizer.json`、`tokenizer_config.json`、原生chat template均一致，配置完整词表为248,077。Miles实际使用另一份统一的preserve-thinking模板。
2. **手册没有确认另一份“已由相同Qwen3.5 tokenizer原生编码”的历史语料。** GLM/Step/DeepSWE等来源多保存消息，可以按目标tokenizer重新编码。当前Miles的924训练/24监测prefix已这样处理。
3. **Steptron已有当前三组的直接实验与另一套数据。** `qwen35-opd-h200`使用55个raw JSON、9组、记录482,359条。其当前本地tokenizer与Miles的全部token→ID、BPE规则及抽样编码相同；其输入模板文件和训练数据配比不同。
4. **Qwen系列确有历史OPD/MOPD记录，但证据完整度不同。** 最明确的完整历史运行是R1-Distill-Qwen-1.5B/JustRL两套200-step数学实验；还有Qwen3-8B配置、Qwen3-30B-A3B准备/smoke/replay记录。不能统称为当前Qwen3.5结果。

## 1. 当前三组：哪些“相同”已证实

| 组合 | Student | Teacher | 实际tokenizer资产比较 |
| --- | --- | --- | --- |
| A | Qwen3.5-4B | Qwen3.5-27B | 三份资产一致 |
| B | Qwen3.5-4B | Qwen3.5-35B-A3B | 三份资产一致 |
| C | Qwen3.5-27B | Qwen3.5-397B-A17B | 三份资产一致 |

共同 `tokenizer.json` SHA256：`5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42`。

必须分开的三个数：BPE基础词表248,044；结合config的实际token条目248,077；本轮核实的4B HF模型 `text_config.vocab_size` 为248,320。旧Qwen3 medium回执则记录151,669个token；其内部兼容结果不适用于Qwen3.5。

Miles统一模板是 `qwen3.5_fixed.jinja`，`preserve_thinking=true`、`enable_thinking=true`。Steptron保存的tokenizer文件经重新序列化，所以文件SHA不同，但本轮证实词表、BPE、added-token规则和10组实际编码相同。两侧template文件不同，因此不把词表相同写成所有输入构造和训练协议一致。

证据与方法：[tokenizer与数据明细](tokenizer_datasets.md)，[四模型检查](evidence/tokenizer-checks.json)，[跨backend本地检查](evidence/steptron-tokenizer-crosscheck.json)。

## 2. 手册中的数据与当前tokenizer

| 数据来源 | 已知原始表示/来源 | 能否说已经是当前Qwen3.5 token数据？ |
| --- | --- | --- |
| GLM-5.2 SWE，11文件 | GLM历史conversation，reasoning/tool calls | 原始文件不能这样说；当前任务选定部分已转成Qwen输入 |
| 1003 SWE OPD，8文件 | DeepSWE相关raw消息；原实验配置Step4 tokenizer | 不能复用其Step token IDs；raw消息可另适配 |
| Step3p6 it698 | Step轨迹及DPO/chosen-SFT/datapipe多种转换 | 未证实Qwen编码；还需注意转换版缺失reasoning字段 |
| Terminal-Bench / hard2000 | 多producer与终端协议的历史轨迹 | 未证实；数据文件/协议也不能由同一任务名推断 |
| DeepSWE / general-SWE / Mini-SWE-Agent | 多版本、多模型、多harness | 家族名不规定tokenizer，需落实到具体文件 |

**已经落实到当前Qwen词表的两条数据线：**

| 当前使用处 | 数据 | 准备/运行证据 |
| --- | --- | --- |
| Miles A/B/C | GLM历史派生924训练prefix、24固定监测prefix | 冻结population；A/B各100-step已验收；C尚未完成 |
| Steptron c1/c2/c3 | golden recipe：55 raw JSON、9组、482,359条 | 固定manifest/inventory；c1/c2在固定快照有7/8个update；c3只有诊断/失败证据 |

Miles数据目录：

```text
/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/population-exp-1106-233008-986003/
```

Steptron完整55路径的现存记录：

```text
/data/ycfeng/steptron/.worktrees/qwen35-opd-h200/
  task_memory/task_2026-11-06_qwen35_opd_h200/evidence/default_data_manifest.json
  task_memory/task_2026-11-06_qwen35_opd_h200/evidence/default_data_inventory.json
```

本报告固定引用 `b48739f615e9a933003859f7a948398320774af5`，避免工作分支后续推进改变来源。例如该recipe含 `.../hard_data_0701/hujingcheng_datasets_orz_dapo17k_cleaned_hard_932.json`，这是DAPO衍生子集，不是完整原始DAPO-Math-17K。它与Miles的GLM-SWE输入内容/域分布也不同，不能仅因tokenizer一致而做等数据效果对照。

## 3. Lark找到的记录

| 文档 | 模型/模式 | dataset细节 | 实际记录程度 |
| --- | --- | --- | --- |
| [explore-mopd](https://wvixbzgc0u7.feishu.cn/wiki/IAvRwliqDikShjkrDZac5lGtncc) / [ROADMAP](https://wvixbzgc0u7.feishu.cn/wiki/NJfJw6yihiSJRrkg19xcCtTEn6I) | 当前三组Qwen3.5，OPD比较计划 | ROADMAP写GLM-5.2 SWE、swe-1003，未逐组绑定实际文件 | 可读章节是计划；本地Miles/Steptron已有运行，不能由飞书缺结果推断未运行 |
| [AGENTIC OPD，Ticket07](https://wvixbzgc0u7.feishu.cn/wiki/Kuldwh97Pic6yhkV1Sgchs90nZf) | 标题 `qwen-a3b-35b`；完整模型ID未写全；单OPD | GLM-5.2 SWE四类；fresh/replay=1:1；没有完整路径/tokenizer | 没有Qwen完成回执；同页后半真实12步是Step模型 |
| [Rethinking Supervision综述](https://wvixbzgc0u7.feishu.cn/docx/ISo7dsuDooLLtUxOQvBcmOVxn0g) | R1-Distill-Qwen-1.5B/JustRL，One-Shot OPD/MOPD等 | 明确 `DAPO-Math-17K`；MOPD有数学/代码/指令三域 | 论文综述，有数值和设置；不是公司复现实验回执 |
| [Qwen Template Update](https://wvixbzgc0u7.feishu.cn/wiki/TBqWw6I34ipJ09ke4njcO8shnhg) | 旧内部Qwen3 tokenizer/template | `Qwen3MainlineVLLMMultiTurn`；新增 `<tool_calls>` 等special tokens | 模板/SFT说明，不是OPD结果，更不能直接代替当前词表 |

ROADMAP还提到旧 `qwen-1.5b-deepseek` 五teacher MOPD，但没有五个teacher、各域数据和结果清单。本轮没有把它强行合并到已核实的单教师600条实验。

飞书覆盖：28个query、31次成功search、15份不同正文及来源图片。7个嵌入实验表缺 `sheets:spreadsheet:read`，一个引用的OPD Log返回3380002；这些表中的完整模型/路径/成绩未核实。宽泛查询仍有更多结果，因此不宣称已读公司全部历史。[Lark完整清单与摘录](lark_records.md)

## 4. Steptron分支与可复用历史

| 固定ref / 记录 | 模型、模式 | 已记录dataset | 运行证据 |
| --- | --- | --- | --- |
| `qwen35-opd-h200@b48739f` | 当前三组，sampled-token pure OPD，GBS256 | 上述55 JSON / 9组 / 482,359条 | c1 step0–6、c2 step0–7及256 samples/step审计；c3 frozen-reference诊断不算训练完成 |
| `yc-step@1e588c90`，2026-09-23 task | R1-Distill-Qwen-1.5B ← JustRL-DeepSeek-1.5B；文件名MOPD，但只有1 teacher | 指定数学轨迹的前600条raw conversation slice | H800/H200各200steps；归档数学macro提升+9.40/+8.73pp |
| `origin/ssj/opd-dev@408af136` | Qwen3-8B单OPD / math+science+logic三专家MOPD | 单OPD数学recipe含6文件主组；MOPD共22 JSON，含DAPO/Math166k/科学/IFTrain衍生 | 完整配置和teacher路径；本轮未取得独立成功终态/效果报告 |
| `yc-step@1e588c90`，2026-09-24 task | Qwen3-30B-A3B Instruct，STEM/SWE两teacher | STEM切片；SWE为相同GLM-5.2的11文件来源 | 实际staging、2-step smoke、HF流程；teardown失败与正式终态不足已分开 |
| `medium-replay-v1@6cd5b785` | Qwen3-30B-A3B，Math/STEM/SWE单领域replay | DAPO、DeepScaleR、WebInstruct、GLM-5.2 SWE | 有精确源路径、词表兼容回执和6个smoke workflows；不能称正式100-update全部完成 |

**最值得直接复查的路径：**

```text
# 当前Qwen3.5配置
playground/users/ycfeng/qwen35_opd/exp.py

# 已完成的1.5B/JustRL数学实验
playground/users/ycfeng/MOPD/r1distill1p5b_mopd_math_fullyasync_tis_no_kl.py
task_memory/task_2026-09-23_mopd_r1distill1p5b_math_disagg/

# Qwen3 medium公开源、tokenizer和数据准备清单
task_memory/task_2026-10-02_h800_medium_singleteacher_bounded_replay/preparation_inputs.json
task_memory/task_2026-10-02_h800_medium_singleteacher_bounded_replay/artifacts/readiness/
```

1.5B实验的runtime数据路径为：

```text
/mnt/codesign-exp/ycfeng/steptron/task_2026-09-23_mopd_r1distill1p5b_math_disagg/data/math_slice.json
```

原始文件明确位于 `.../runs/kimi-k2.6/math_collect11k_dsv4pro_gte_acc0p5/no_tools/trajectories_correct_0511/sft_data_list_0.json`；完整原路径见 [Steptron记录第5节](steptron_records.md)。**飞书One-Shot综述的DAPO与这次内部实际600-item实验是两条不同来源。**

旧Qwen3 medium的公开源回执记录实际DAPO17,917条、DeepScaleR40,315条、WebInstruct228,736条；名字中的17K不应覆盖实际样本数。它们的raw文本可以重新用Qwen3.5编码，已有Qwen3缓存/prompt IDs则不可直接视为等价。

Steptron覆盖52 local heads、8,335 remote-tracking refs，重点检查Qwen/OPD路径及继承；未fetch、未逐文件遍历每个分支。上述状态都是固定本地记录，不是本轮平台实时检查。[完整分支/commit/路径清单](steptron_records.md)

## 5. 如何使用这些信息

- 复用当前SWE输入：已有Miles冻结924/24数据与相同词表，来源链最完整。
- 研究另一种Qwen3.5训练数据配比：现有Steptron55文件recipe已经接入同词表，但数据域、模板和GBS与Miles不同，比较时必须逐项注明。
- 查历史可复现OPD流程：1.5B/JustRL200-step记录最完整；查多域数据/teacher routing：旧Qwen3-8B和medium配置提供具体路径。
- 判断能否直接复用历史产物：raw消息可重新编码；已tokenized prompt、old completion logprobs、KV或replay缓存必须按目标tokenizer/template和版本契约重新核验。本次没有转换或切换任何训练数据。
