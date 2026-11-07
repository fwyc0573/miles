## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | 对照四模型实际资产回执、本地 tokenizer 字节、运行配置和资源手册，核实 tokenizer 与数据格式关系。 |
| 2026-11-08 | 补充 Steptron 当前运行资产的词表/BPE/编码交叉核验及55文件数据来源。 |

# 当前三组模型的 tokenizer 与手册数据集

## 1. 三组 tokenizer 一致

| 组合 | Student | Teacher | Tokenizer 资产 |
| --- | --- | --- | --- |
| A | Qwen3.5-4B | Qwen3.5-27B | 相同 |
| B | Qwen3.5-4B | Qwen3.5-35B-A3B | 相同 |
| C | Qwen3.5-27B | Qwen3.5-397B-A17B | 相同 |

依据不是模型名称相近，而是原0-GPU资产核验作业 `exp-1106-233008-986003` 对四个实际来源目录计算的文件摘要。三种资产均逐字节一致：

| 文件 | 四模型共同 SHA256 |
| --- | --- |
| `tokenizer.json` | `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42` |
| `tokenizer_config.json` | `316230d6a809701f4db5ea8f8fc862bc3a6f3229c937c174e674ff3ca0a64ac8` |
| 原生 `chat_template.jinja` | `a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715` |

本轮确认四条来源路径与当前 H800/H200 配置中对应模型路径一致，并对本地4B tokenizer三份文件重新计算SHA；全部一致。[本轮检查](evidence/tokenizer-checks.json)记录配置路径、比较项和范围。它是对已存实际资产回执和本地副本的核查，没有重新扫描云端模型。

原始来源：[资产回执](../task_2026-11-06_qwen35_three_pairs/evidence/assets-exp-1106-233008-986003.json)，[固定配置](../task_2026-11-06_qwen35_three_pairs/training_config.json)，[原作业环境与命令](../task_2026-11-06_qwen35_three_pairs/test_report_2026-11-06_p2.md)。

### 词表大小的三个不同数字

- BPE基础词表：248,044项。
- 合并 `tokenizer_config.json` 的33个added tokens后：248,077项。`tokenizer.json` 自身只列26个added tokens；另外7个音频token由config补充。因此只数单个JSON会得到248,070。
- HF `config.json` 的 `text_config.vocab_size`：本轮在本地4B副本核实为248,320，且该config的SHA与原4B资产回执一致。它是模型输出词表维度，不能当成tokenizer实际条目数；本轮未重新读取其他三个模型的HF config内容。

已核实的特殊ID：`<|endoftext|>=248044`，`<|im_start|>=248045`，`<|im_end|>=248046`，`<think>=248068`，`</think>=248069`。配置类名虽然写 `Qwen2Tokenizer`，也不能据此声称与所有Qwen2/2.5/3的词表相同；类实现可以加载不同词表。

### 当前实际使用的是统一的 preserve-thinking 模板

当前三组共用 `miles/utils/chat_template_utils/templates/qwen3.5_fixed.jinja`，SHA256为 `ca447731ed457cb460b7522ea9edb986d52e4ea62c5d8482365146592d69b1b9`，`preserve_thinking=true`、`enable_thinking=true`。它保留历史reasoning，与上述发布包原生模板是两个不同文件；这是已批准的统一输入策略，不是三组之间的差别。

数据准备先用该模板渲染，再以Qwen tokenizer编码；正式生成检查实际prompt token数和hash，teacher直接接收student完整token IDs打分。没有给teacher另渲染一套prompt：

- [prepare_qwen35.py](../../tests/manual/agent_opd/prepare_qwen35.py):92–126，字段规范化、渲染与token身份。
- [run_qwen35_opd.py](../../tests/manual/agent_opd/run_qwen35_opd.py):145–172，冻结数据和student tokenizer校验；318，teacher/student一致性检查。
- [rjob_warmup.py](../../tests/manual/agent_opd/rjob_warmup.py):209–220，实际tokenizer组件与config/template逐项比较。
- [qwen_alignment.py](../../tests/manual/agent_opd/qwen_alignment.py):86–105、173–196，prompt检查与teacher评分；[原生评分payload](../../miles/rollout/on_policy_distillation.py):95–111，传入 `input_ids`。

A/B已完成运行的launch receipts和C旧失败尝试均绑定同一个冻结数据集；C新排队作业使用同一配置，但本结论不替代它尚未完成的实际运行验收。

## 2. 手册没有确认“原生Qwen3.5 tokenizer的数据集”

这里要区分：原生成模型、数据保存格式、训练时的tokenizer。JSON里的 `role/content/reasoning_content/tool_calls` 本身不是某个词表的token IDs，可以按目标模型模板重新编码；已经保存成另一词表的IDs则不能直接沿用。

`/data/ycfeng/stepfun-env-handbook/resource_analysis` 当前有四份文档；其中数据说明覆盖以下五组。**文档没有为任何一组提供“原始导出已经使用当前Qwen3.5同一词表”的完整证明。** “没有确认”不等于断言所有原始数据都不含Qwen生成样本。

| 手册数据组 | 已记录来源/表示 | Tokenizer证据 | 与当前三组的关系 |
| --- | --- | --- | --- |
| GLM-5.2 SWE，11份JSON | `glm5.2_distill_{0,1}_include_unresolved_part*.json`；完整conversation消息列表，保留reasoning/tool calls | 生成端为GLM；字段足以重渲染为Step/Qwen格式；手册本身未给出在这11份文件上的其他模型完整运行凭证 | 原源不是Qwen3.5 token-ID包；当前任务已实际重渲染成Qwen输入 |
| 1003 SWE OPD，8份DeepSWE来源文件 | `datapipe_stage2_rft_0913/.../garble_filtered_sft_20260913/`；消息加loss mask | 固定Steptron配置使用 `Step4Tokenizer_V0_0528_PreserveThinkingAdaptive` | 非当前Qwen3.5 tokenizer配置；原始消息可另行适配，未在当前任务使用 |
| Step3p6 it698 | raw DPO、chosen SFT、datapipe DPO三种表示 | Step轨迹；转换版可能缺顶层reasoning，但嵌入原响应保留；手册对照为Step tokenizer | 不能复用Step IDs；原始消息可重渲染，需明确缺失/合并reasoning策略 |
| Terminal-Bench / hard2000 | Terminus JSON/XML；`commands[].keystrokes`、`task_complete` | 所引固定采集配置的实际model_name为 `claude-fable-5`，不是从文件名 `opus48` 推断；完整导出未核实 | 未确认同Qwen3.5 tokenizer；22份混合TB文件也不等同hard2000；需匹配终端协议 |
| 后续DeepSWE/general-SWE/Mini-SWE-Agent | 数据家族、多版本；bash正文、`THOUGHT:`、工具反馈及drop/merge-thinking差异 | 家族名称不规定唯一生成模型或tokenizer；未取得全部实际导出 | 不能按DeepSWE/miniswa名字判定同词表；逐文件确认消息/IDs、模板和harness |

手册原文定位：

- [agent-dataset-completion-formats.md](/data/ycfeng/stepfun-env-handbook/resource_analysis/agent-dataset-completion-formats.md):63–71（总表）、140–162（8文件及Step tokenizer）、204–214（it698）、266–283（hard2000配置/混合TB边界）、333–399（Mini-SWE家族）。
- [swe-dataset-format.md](/data/ycfeng/stepfun-env-handbook/resource_analysis/swe-dataset-format.md):13–30、75–105（GLM源和Step序列化），246–253（个人源副本）。
- [opd-train-inference-consistency.md](/data/ycfeng/stepfun-env-handbook/resource_analysis/opd-train-inference-consistency.md):76–96（GLM消息转Qwen及格式边界）。其中FrogNano与Qwen格式相同是模型资产结论，并未给出一个FrogNano/Qwen原生生成的数据集。

手册中部分相对链接源于历史Steptron任务目录，移动到handbook后不再解析；本报告以现存绝对路径、固定commit及实际receipt为依据，不把断开的相对链接当作已读取证据。

## 3. 现在确有一份已按相同Qwen tokenizer准备的数据

它就是当前任务的已冻结派生数据，而不是新发现的独立Qwen原生语料：

```text
/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/population-exp-1106-233008-986003/
  train.jsonl       924个训练prefix
  monitor.jsonl      24个固定监测prefix
  population.json   tokenizer/模板/身份/排除/长度证据
```

源为手册第一组GLM-5.2 SWE中的已选历史：1,024个候选，6个超长排除；选24个监测prefix，另外70个同监测任务组prefix排除，留下924个训练prefix。prompt在Qwen格式下准备，旧GLM completion只作来源信息；训练目标是student新生成的completion。A/B实际训练使用它，C配置也绑定它。[population回执](../task_2026-11-06_qwen35_three_pairs/evidence/population-exp-1106-233008-986003.json)

该本地population文件是云端 `population.json` 的字段摘录，可复核上述计数、模板和输出文件摘要，但不是云端文件的字节副本；它未保留 `qwen_tokenizer` 字段，因此不能单独重放launcher对该字段的读取。完整运行中的tokenizer校验由launcher代码、实际launch/运行凭证及独立四模型资产回执共同支持，本轮没有再次读取完整云文件。

因此，如果问题是“有没有已适配当前tokenizer、能复用的输入”，答案是**有，当前冻结数据就是**；如果是“手册是否提供另一份已证明由同Qwen3.5 tokenizer原生生成的历史数据”，本次手册范围内**没有确认**。历史Qwen OPD/MOPD记录是否给出其他候选，分别见 [Steptron](steptron_records.md) 和 [Lark](lark_records.md)。

## 4. Steptron另有一套已接入同词表的原始数据

`qwen35-opd-h200@b48739f615e9a933003859f7a948398320774af5` 的三组模型与本任务相同，继承golden recipe的55个raw conversation JSON、9组、记录482,359条，运行时以Qwen3.5分词。它包含数学、代码、STEM、指令跟随等；这套混合语料与Miles的924/24 GLM-SWE切片不是同一份数据。

本轮另外读取本地 `/data/ycfeng/steptron/.worktrees/qwen35-opd-h200/.runtime/tokenizer/`，与已核实的Miles原始tokenizer比较：

- 全部248,077个token→ID映射相同。
- BPE模型参数、247,587条有序merge pairs相同；normalizer、pre-tokenizer、post-processor、decoder、padding/truncation配置相同；added-token配置相同。
- Transformers实际加载后，10组中英文、代码、空白、reasoning/tool标记和Unicode文本的编码逐项相同。
- JSON SHA不同：`save_pretrained`将merges从字符串序列重写为二元数组，并把config中的7个补充token纳入 `tokenizer.json`。这是已核实的表示差异，不能由不同SHA直接判词表不同。
- chat template文件也不同，Steptron默认保留history reasoning。这里只证明分词/词表等价；没有把跨backend任意消息的完整渲染序列宣称为一致。

这是当前本地运行资产检查，不是对每个历史worker二进制的重放。[完整回执](evidence/steptron-tokenizer-crosscheck.json)；[固定数据/运行凭证复核](evidence/steptron-source-checks.json)。55个源文件的逐一读取发生于原Steptron任务，本次只读取其固定Git回执，没有访问这些云目录。
