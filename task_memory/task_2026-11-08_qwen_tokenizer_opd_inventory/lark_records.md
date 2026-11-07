# Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | 完成 QWEN-TOKENIZER-T2-LARK 的只读飞书检索、正文与图片核查，记录实验/计划区别、数据字段及权限缺口。 |

# Qwen OPD / MOPD 飞书记录

任务 ID：`QWEN-TOKENIZER-T2-LARK`。检索日期：2026-11-08。本文只记录通过现有认证 `/data/ycfeng/stepcode-codex-home/bin/lark-cli` 实际读取的证据；不代替父任务的模型资产或 Steptron Git 核查。

## 结论

1. **找到了当前三组 Qwen3.5 组合的明确测试要求，但未在已读取的飞书正文中找到这三组已经完成的 OPD/MOPD 结果表。** `explore-mopd` 的 11.06 部分是“创建 task、先落地 docs、开展测试”的要求；`ROADMAP` 是实验设计。不能把它们当成成功运行回执。
2. **找到了旧 Qwen 单 OPD ticket、旧 Qwen/DeepSeek 1.5B 五教师 MOPD 数据的回顾性提及，以及包含模型/数据集/结果的论文综述。** 旧 ticket 未写全 teacher/student 路径；旧五教师数据未写具体数据集名称/路径。论文综述不是公司内部复现实验回执。
3. **旧 Qwen3 内部 tokenizer 有明确的自定义名称和规则。** `Qwen3MainlineVLLMMultiTurn` / `Qwen3MainlineVLLMMultiTurnMultiRole` 不能仅凭 Qwen 名称被认定与当前 Qwen3.5 tokenizer 等价。飞书未给当前四模型的完整 token→ID 对照或 tokenizer 资产比较。
4. **可读正文有 GLM-5.2 SWE、swe-1003、Step3p6 it698 自产轨迹、Terminal-Bench hard2000、DeepSWE/Critpt 等具体来源。** 但“被 Step 模型 OPD 使用”不等于“已经用当前 Qwen3.5 tokenizer 编码”。已有结构化消息/模板转换记录，不能把原始 producer、教师模型和 tokenizer 混为一项。
5. 文档正文和图片可读；**电子表格缺少 `sheets:spreadsheet:read`**。多份实验的准确模型、完整数据路径、超参和成绩只放在嵌入表格里，这些字段本次无法确认。没有修改认证、申请新权限或用记忆补齐缺失数据。

## 1. 与当前 Qwen3.5 直接相关

### L1：`explore-mopd`，11.06 qwen 系初步列测试

- 来源：[explore-mopd](https://wvixbzgc0u7.feishu.cn/wiki/IAvRwliqDikShjkrDZac5lGtncc)，创建 2026-09-09，最近编辑 2026-11-06；读取 Docx `AQT5d97i2ofKirxePLvc2Zcsn8x`，revision `2737`，相关正文行 11–70。
- 模型方向明确：小模型为 student，大模型为 teacher：
  - Qwen3.5-4B ← Qwen3.5-27B；
  - Qwen3.5-4B ← Qwen3.5-35B-A3B；
  - Qwen3.5-27B ← Qwen3.5-397B-A17B。
- **计划参数**：Steptron/H200 与 Miles/Verl/H800 两条验证路线；TIS、R3、NCCL weight sync、total-token loss；Steptron 等待 batch=256；不使用 replay；仅保留 HF checkpoint。若 student 不支持 R3，Miles/Verl 路线允许不开。
- **模板要求**：最后一条真实 user 消息之后的历史 assistant reasoning 保留；之前的 reasoning 在序列化时剔除。prefix 不参与 loss，completion 参与。
- 数据集：该部分要求集中记录“数据集、格式转换”等配置，但**没有实际选用的数据集名/完整路径**。不能据此认定三组使用同一份数据。
- 模型来源明确列出 27B/35B-A3B 的 `/mnt/posttrain/checkpoints/open-models/Qwen/.../model`，4B 的个人 `opd-assets` snapshot 和 397B-A17B 的模型来源目录；**本任务没有访问这些云目录**。
- **执行结果缺失**：无这三组的 run ID、成功更新数、loss 数值、评测数值或 tokenizer 比较结果；状态判为计划。

### L2：`ROADMAP`，运行设定与旧实验回顾

- 来源：[ROADMAP](https://wvixbzgc0u7.feishu.cn/wiki/NJfJw6yihiSJRrkg19xcCtTEn6I)，创建 2026-11-04，最近编辑 2026-11-08；Docx `C0jtdoIhpo6g0uxhNg3cMztbnRg`，revision `3725`；正文行 109–130、167–186。
- 上述三组 Qwen3.5 与 Step3p6 都列在待比较模型里；backend 为 Steptron+Stepcast，Verl/Miles 为支持 hybrid 架构和处理训推差异的备选。
- **计划参数**：LR=2e-6，自 update0；total-token loss、NCCL 直传、TIS、MoE R3、GBS=256。
- **计划数据**：`glm-5.2` SWE 与 `swe-1003`。没有为每个 Qwen3.5 combo 绑定唯一实际文件列表或 tokenizer 路径。
- 旧实验原文：`（旧）qwen-1.5b-deepseek- distillation（5teacher），问题：这是mopd的数据，设定并未统一`。这是旧数据的回顾性线索，**并非附有可复现实验配置/成绩的完整记录**。
- **旧五教师缺失项**：student 完整模型 ID/路径、五个 teacher 名称/路径、每域训练数据名/路径、tokenizer/template、run ID、指标/完成时间均未写出；不能补成当前 Qwen3.5 或推定为特定公开数据集。
- `e1-1` 的“5 teacher/domain、200 steps、每 x 步替换数据”是补充单 OPD 的计划，不是旧 MOPD 已完成参数。
- 原文明示 GLM 数据需做 Step 格式转换：原始 `reasoning_content`、`content`、结构化 `tool_calls` 要组成 Step 的 thinking/tool-call 序列，否则格式分类和训练不匹配。**这证明存在模板转换需求，不证明已转换为当前 Qwen3.5 token IDs。**
- 数据来源图片实际通过 CLI 下载并打开核查；下文 L8 归纳其可确认内容。没有依赖自动生成的图片 alt 文本当作图片事实。

## 2. 旧 Qwen OPD 线索及公开实验综述

### L3：`AGENTIC OPD`，Ticket 07（qwen-a3b-35b）

- 来源：[AGENTIC OPD](https://wvixbzgc0u7.feishu.cn/wiki/Kuldwh97Pic6yhkV1Sgchs90nZf)，创建 2026-10-25，最近编辑 2026-11-03；Docx `PmYddZiyyoLw1Nxvzg2cQGm6nfh`，revision `246`；全文 161 行。
- 标题是 **`qwen-a3b-35b`**，但正文只要求参考 `yc-mopd-learning-dynamics-s4-branch` 的 teacher/student，只用 SWE teacher，并“先确认 teacher 是否存在”。**未给完整模型 ID，不直接归为 Qwen3.5-35B-A3B 已运行实验。**
- 算法明确为**单 OPD，非 MOPD**。
- **计划数据**：GLM-5.2 SWE；四类 `control_only`、`thinking_only`、`control_thinking`、`neither`；fresh/replay=1:1；补充要求 fresh 与 old 均来自 GLM-5.2 同一数据来源，允许 trajectory/turn 重复。
- **计划设置**：固定 LR=2e-6、无 warmup、TIS、NCCL checkpoint_engine/TP=2、total-token loss、200 steps、每30步 HF保存/异步评分、50题 avg@4、H200。后续补充明确关闭 Ticket06/07 的 router replay。
- **没有 Qwen Ticket07 的完成回执或数据完整路径/tokenizer 名称。**
- 文档后半的“测试记录”有真实 run ID，但模型明确为 student `it4046_text/hf`、SWE teacher `it973/hf`，对应 48 train + 8 rollout H200 的 Step 实验；仅12次更新、仍有20-step warmup、R3/TIS开。这不能移植成 Ticket07 已完成的200步 Qwen证据。四组均取得512个样本，HF4/8/12各700个评测结果，证明此后半确有执行记录，**也证明其实际设置不同于前半新 ticket 要求**。

### L4：`Rethinking Supervision in On-Policy Distillation`

- 来源：[飞书论文综述](https://wvixbzgc0u7.feishu.cn/docx/ISo7dsuDooLLtUxOQvBcmOVxn0g)，创建 2026-09-16，最近编辑 2026-09-17；Docx `ISo7dsuDooLLtUxOQvBcmOVxn0g`，revision `763`；全文353行。
- **来源性质**：作者对论文的记录/综述，不是公司内部 GPU run receipt；本任务未另用 Web 或 GitHub 拉取论文/仓库。

| 记录 | 模型 | 训练数据/设置 | 文档给出的结果 | 缺失字段 |
| --- | --- | --- | --- | --- |
| One-Shot OPD | DeepSeek-R1-Distill-Qwen-1.5B student ← JustRL-1.5B teacher | `DAPO-Math-17K`；每步64条当前student新rollout；数学主实验top-k reverse KL，文档注明top-16 | 300 steps：one-shot 68.5 vs full-data 69.8；MATH-500/AMC2023/AIME2025平均avg@16；16题设置70.9 vs full70.8 | 数据文件路径、tokenizer文件/模板完整实现、LR/optimizer、公司复现run均未给 |
| One-Shot MOPD | 数学/代码/指令跟随三域，每域一个teacher；本页未完整列三个teacher ID | 每域16题，共48题；step300 | 平均52.9 vs full52.8 | 代码/指令训练数据精确名称、各teacher完整ID/路径、tokenizer及内部运行信息缺失 |
| What Matters | R1-Distill-Qwen-1.5B ← JustRL-DeepSeek-1.5B（文档采用此写法） | `DAPO-Math-17K`；student top-16 RKL；固定8 hard题 | 初始42.4；8hard53.6；full约17K题53.7；六个数学bench平均准确率 | tokenizer、文件路径及内部复现信息缺失；不能与上一行3个bench的分数直接比较 |
| Sparse OPD | Qwen3-8B ← Qwen3-4B-Instruct-2507 | sampled-token PPO-style OPD；位置mask，rand1tok/mintok/maxtok/minmaxtok | mean avg@8：student19.3、teacher46.8、dense47.5、rand1tok29.9、mintok42.8、maxtok48.1、minmaxtok49.3 | 本页未给该配置训练集精确名/路径、tokenizer/template完整资产、公司复现run |

- 外部论文链接在飞书原文中明确给出：[One-Shot](https://arxiv.org/abs/2609.04172)、[What Matters](https://arxiv.org/abs/2609.05198)、[Sparse OPD](https://arxiv.org/abs/2609.04565)；One-Shot仓库链接为 `https://github.com/Thinking-Space/One-Shot-OPD`。
- 这些模型属于**旧 Qwen/DeepSeek-Qwen 或 Qwen3**，不是当前四个 Qwen3.5 模型。综述没有证明它们与 Qwen3.5 tokenizer 等价。

### L5：`20260917周报` 的 Qwen teacher 计划

- 来源：[20260917周报](https://wvixbzgc0u7.feishu.cn/wiki/LNkww8FdEibhfyk0dqlc13gVnwf)，创建 2026-09-17、最近编辑2026-09-20；Docx `Yio2d0qpxoRpwax3nzFcbKoSnje`，revision `680`；全文124行。
- 文档“下周计划”写 `qwen3.8-flash-next作为teacher进行mopd实验`。**是计划，不是完成结果；也不是 Qwen3.5。**
- 上文有 light/capture/intent-recall 的 MOPD 框架调整和训练完成报告，但不能把上文已完成结果归因于下周拟用的 Qwen teacher。该Qwen计划缺student ID、训练文件路径、tokenizer、超参和成绩。

## 3. 旧 Qwen tokenizer / 非 OPD 记录：防止错误归类

### L6：`[ToolUse] Qwen Template Update`

- 来源：[Qwen Template Update](https://wvixbzgc0u7.feishu.cn/wiki/TBqWw6I34ipJ09ke4njcO8shnhg)，文档日期本次未观察到；Docx `SLBVdJK7sotfKfxUEOucrcqVn1c`，revision `1107`；全文133行。
- 精确名称：`Qwen3MainlineVLLMMultiTurn`；SFT要求 `Qwen3MainlineVLLMMultiTurnTokenizer` + `Qwen3MultiTurnMaskSFTTemplate`；reshape/eval也要求一致使用该tokenizer。
- 路径：[steptokenizer/tokenizers/Qwen3MainlineVLLMMultiTurn](https://gitlab.basemind.com/basemind/steptokenizer/-/tree/master/tokenizers/Qwen3MainlineVLLMMultiTurn?ref_type=heads)。本任务只记录链接，未访问GitLab。
- 规则：去掉 input/output `tool_call_id`；最后一轮user之后 reasoning保留，更早的丢弃；新增 `<tool_calls>` / `</tool_calls>` **special tokens**，后者可作EOS；以user而不是每个tool/user交互切分多轮；assistant可设置`loss_mask=0`。
- vLLM 示例使用 `hermes` tool parser + `deepseek_r1` reasoning parser；对丢弃`reasoning_content`字段的服务给出把reasoning/content拼成`<think>... </think>...`的处理方式。这是旧服务/自定义模板约定，**不能自动成为当前 Qwen3.5 运行设置**。
- 原文链接是SFT/reshape/eval例子，**不是Qwen OPD完成记录**。special-token改动尤其要求父任务用真实资产验证，不应仅比较模型家族名。

### L7：`SWE-Agents实验记录 0401-0601` 与 `Qwen3接入`

- [SWE 0401-0601](https://wvixbzgc0u7.feishu.cn/wiki/HhgMwCZfQimPLgkucRCcULurnzf)，创建2026-03-31、最近编辑2026-09-04；Docx `HeWUdXE4moRI40xIpoKczCS3n0c`，revision `34137`；取得完整正文并读取完整Qwen相关段落。
  - MultiRole段给出 `Qwen3MainlineVLLMMultiTurnMultiRole`，并要求exp和reshape一起改tokenizer config。
  - [tokenizer路径](https://gitlab.basemind.com/basemind/steptokenizer/-/tree/master/tokenizers/Qwen3MainlineVLLMMultiTurnMultiRole?ref_type=heads)。
  - Qwen2.5-32B/Qwen3-8B/32B主要是SFT、tooluse、数据消融；例如Qwen3-32B的Opus-distill TB扩量5.83k/epoch、4ep结果28.08%，旧Kaggle1.83k/epoch、5ep22.41%。**是离线蒸馏/SFT数据实验，不是当前Qwen OPD/MOPD。**
- [Qwen3接入](https://wvixbzgc0u7.feishu.cn/wiki/GHDpw16ShiwIWpk3pCCchTcEnuc)，创建2025-07-14、最近编辑2025-09-12；Docx `QAmudCVGVo04glxRfHtcZMIBnLd`，revision `668`；全文125行。
  - Qwen3-30B-A3B 的PPO实际评测有it0/150/300/365，AVG60.39/60.92/60.75/60.61；没有teacher蒸馏设定或OPD/MOPD完成记录。
  - 与当前 `Qwen3.5-35B-A3B` 不是同一个明确模型ID。不能把旧30B-A3B PPO当成35B-A3B OPD。
- [Reasoner 0101-0328](https://wvixbzgc0u7.feishu.cn/wiki/Yv7BwbduhiWQnbktAaocqf04njd)，创建2026-01-23、最近编辑2026-06-26；Docx `CbhjdrBJAo7OqbxS4WUcZks0nUf`，revision `18553`。
  - 0112 Qwen3-8B Nemotron RL验证写明训练路径 `/mnt/step2-alignment-jfs/lina/data/ifdata/nemotron/nemotron_rl/instruction_following_train.json`，46391条；base为`/mnt/step2-alignment-jfs/hujingcheng/checkpoints/steptron-sft/qwen3_8b_sft1013_sft_d1114_ds_0p05_g32_1114/it3660/`。
  - [固定Git commit exp链接](https://gitlab.basemind.com/stepresearch/steptron/-/blob/7e6c5030b1a6ee3413c5e363ea606cee3a97b31b/playground/users/lina/qwen/rl/qwen3_8b_mainrecipe1129_s2ds5_s64k_256x16_g64_ait4_vllm_plr2e6_yarn_nemotron.py)。这是RL数据验证，不是Qwen OPD记录；同一大页其他MOPD内容多为Step3p5，不能因搜索同页命中而合并模型归属。

## 4. 可复用的数据来源与真实 Step OPD/MOPD 记录

### L8：数据来源表的图片核查

来源为L2 `ROADMAP` 数据集图片：[原图](https://feishu.cn/file/ZmFqbA0aaoT2Hrx0eZsc6HhwnGf)。已用 `docs +media-preview --as user` 成功读取570013字节PNG并打开查看；这是作者对实验来源的整理，不是本次云文件核查。

| 来源 | 图片实际写出的信息 | 与本任务的边界 |
| --- | --- | --- |
| GLM-5.2 SWE轨迹 | SWE-factory筛选约1600题、repeat4；过滤生成失败，但保留resolved/unresolved；当前Ticket06来源冻结11个文件、4992 conversations；引用SWE 0602-0801 | 不是公司所有SWE数据；未给11个文件完整列表、tokenizer或Qwen完成回执 |
| 1003 SWE单teacher OPD数据 | 复用程杰`s4_swe_opd_sft105_teacher400_1003.py`；`datapipe_stage2_rft_0913/.../garble_filtered_sft_20260913`下8个JSON | 路径中间是原图的省略号，**不是完整可访问路径**；原图链接到Step5交付页，须由本地配置补全 |
| Step3p6 it698自产SWE轨迹 | 两个原始任务来源、对应rollout目录；`pairs_onpolicy_resolved_vs_unresolved.json`；resolved选rubric最高、unresolved随机最多两个 | 历史自蒸馏/DPO来源，与GLM四分类不是同一组数据；不直接等同OPD prefix输入 |
| Terminal-Bench/hard2000 | GLM/Opus历史轨迹；环境泄漏和grader noise清洗记录 | 图片明确没有验证它可直接替换Ticket06输入 |
| DeepSWE/general-SWE/Mini-SWE-Agent | 新实验有不同模型/harness合成和SWE OPD/DeepSWE MOPD | loader适配与thinking/tool字段保留仍要逐组验证，不能从名称推出兼容性 |

L9的SWE原文还给出 it698 DPO 实际pair文件：`/mnt/posttrain/zhoujie/data/post-training-sft/swe_data/rubric/dpo/onpolicy_it698_resvsunres_v1/pairs_onpolicy_resolved_vs_unresolved.json`；原始任务JSON为 `/mnt/juicesfs_step2_alignment/zhangjiaran/multi-28w-0612-55-88-6533_add_meta.json` 和 `/mnt/juicesfs_step2_alignment/zhangjiaran/multi-28w-0521-24-51-5597_add_meta.json`。原文说明DPO处理没有把`reasoning_content`塞入`content`，实际只学习tool_calls。**文件名有onpolicy不意味着它是当前Qwen OPD训练数据。**

### L9：SWE/TB turn-level OPD 的真实观察

- 来源：[SWE-Agents实验记录 0602-0801](https://wvixbzgc0u7.feishu.cn/wiki/RAI9wdUUJiSlpCk9O14ca2G7nLf)，创建2026-06-02、最近编辑2026-10-06；Docx `GpOudO1mdoDqFhxH5oOcRU4cnSh`，revision `29107`。
- `[DONE] 0607 Turn-level SWE OPD`：SFT按assistant turn切分；原数据63607条，其中41432条历史交互有空reasoning（约66%）；更换原始非空think轨迹后，前43iter缺thinking平均约0.05%。结论最佳setting不开TIS、开KL、约125iter；SWE-mtlg最后仍与teacher差约1pp，SWE-pro较接近。
- `[WIP] 0610 SWE OPD`：完整traj与逐步增长rollout长度消融；正文记录traj版到50iter，并给出[commit b1fdc33e](https://gitlab.basemind.com/stepresearch/steptron/-/commit/b1fdc33e6045a84f430917343cbc561781795b6c)；最终turn-level点数类似、iter更快，后续合版选turn-level。
- `[DONE] 0627 TB turn-level OPD`：MOPD前置单domain验证；iter125与teacher差0.2pp，待纳入合版；“数据换成RL traj”仍在TODO。
- 这些段落的准确student/teacher名、训练完整文件路径及细参数在嵌入表格中；本次读取被scope挡住，**不认定是Qwen实验，也不猜其tokenizer**。

### L10：Step MOPD 与 1003 数据的实际运行入口

- [Reasoner实验管理0601-1010](https://wvixbzgc0u7.feishu.cn/wiki/DGu5wGExbiKKQukfoagccVPKnVe)，创建2026-06-08、最近编辑2026-11-05；Docx `LYxXdnI8Do2vKdxL0rAc7S6VnGb`，revision `51112`。
  - `0731 MOPD baseline构建`明确template=`Step4Tokenizer_V0_0528_PreserveThinking`，init=`step3p7_256k_midtrain0620_text0727full_pp6_vpp2_H200/it1246`，vLLM0.19 async scheduling/session admission。
  - working/stem/scicode/tb/swe五域；data balance权重30.3/1.0/10.2/32.1/99.5；adv mask token[-2,2]、sample[-0.6,0.6]。正文称1024×1优于256×4，adv mask平均涨约0.3；TB有效，HLE/GDPval不达预期。精确teacher路径、数据文件列表在表格，无法核查。
- [SWE-Agents实验记录0802-1103](https://wvixbzgc0u7.feishu.cn/wiki/GgeMwy94Di8io9k3MbQc1siynCf)，创建2026-08-03、最近编辑2026-11-08；Docx `Ah8Sd9bjio1gjaxdVNKcWvTSn9d`，revision `27957`。
  - `[DONE] 1004 S4 OPD on swe`是1003实验实际入口；256train+32infer，infer idle10%，iter约1300s；正文列未接入dx grad clip、adv mask、weight decay→0、gbtm。准确模型/数据表不可读。
  - `[DONE] 1015 MOPD on HLE & DeepSWE`：Critpt logprob约100iter从-0.8到-1，出现偏离题目的回答；DeepSWE it25 pass@4下降约5–8pp，原文讨论hard/soft reward和置信区间。不能把该页的`DONE`等同所有domain有正收益；也没有Qwen OPD完成记录。
- [【交付清单】step5 MOPD性能版](https://wvixbzgc0u7.feishu.cn/wiki/Lzuvw9DcSiydhtkl8BNcZBnInsf)，创建2026-10-27、最近编辑2026-11-07；Docx `V1D0db9znovvEBxMdYoc1VYqn2r`，revision `1129`。
  - 明确Step5基线`playground/baseline_new/mopd/step5/step5_mopd_swe_critpt_s256k_1024x1_1012.py`与本次交付[exp](https://gitlab.basemind.com/stepresearch/steptron/-/blob/wyx/step4-opd-frozen-indexer-exp-1030/playground/users/wyx/MOPD/step5_swe_critpt_w4a8_mtp3_quant_teacher_1102.py)、[RJob exp-1106-124918-338642](https://platform.shaipower.com/kubebrain/shai-core/job/detail/exp-1106-124918-338642?lang=zh_CN)、[MR4639](https://gitlab.basemind.com/stepresearch/steptron/-/merge_requests/4639)。数据标签为DeepSWE+Critpt。
  - sampled-token、264k（256k+8k padding）、infer_train_batch_size1024×1、GBS48、fixed_iter1、冻结indexer；actor/teacher用FP8KV+W4A8 QDQ+MoonEP，infer加MTP3。
  - 原文报告iter36.87→14.55min、MFU24.85%→31.81%、TPSC733→940；两行卡数也改变，**不是等资源性能对照**。配置框推理64卡，表格/问题日志为128卡；原文解释临时扩容，不能只摘64卡当最终运行值。
  - 是Step5交付/运行证据，不是当前Qwen3.5 tokenizer或数据兼容证明。
- [E0 & E1](https://wvixbzgc0u7.feishu.cn/wiki/TcXCwoRdMiyqm5kbIuGcrSIMn1d)，创建2026-11-07、最近编辑2026-11-08；Docx `EvGSd7AtwoGJePxN9DAcYSXMncg`，revision`84`。Step3p6 full/r256在STEM/TB各12、SWE50成功updates；SWE HF50 avg@4为65.5%/68.5%。有参数和run ID，但未给当前Qwen模型/数据绑定。

## 5. 已执行覆盖与失败边界

### 命令与读取

所有业务读操作显式`--as user`，检查JSON `ok == true`；未使用其他Lark客户端、Web搜索、GPU、云文件系统、发布/发送/编辑操作。wrapper已有认证未修改。

```bash
/data/ycfeng/stepcode-codex-home/bin/lark-cli drive +search --query '<query>' --as user --page-size 20 --format json
/data/ycfeng/stepcode-codex-home/bin/lark-cli docs +fetch --doc '<source-url>' --as user --doc-format markdown
/data/ycfeng/stepcode-codex-home/bin/lark-cli sheets +csv-get --spreadsheet-token '<token>' --sheet-id '<id>' --as user --format json
/data/ycfeng/stepcode-codex-home/bin/lark-cli auth status --json --verify
/data/ycfeng/stepcode-codex-home/bin/lark-cli docs +media-preview --token ZmFqbA0aaoT2Hrx0eZsc6HhwnGf --output ./roadmap-datasets.png --as user --format json
```

- 已加载`lark-cli` skill及CLI嵌入shared/drive/doc/sheets skill、相应identity/output/search/fetch/read-data/media操作参考和help；只执行只读命令。
- **28个query，31次search，全部`ok:true`**：
  `Qwen3.5 OPD`、`qwen MOPD`、`MOPD`、`OPD`、`qwen3`、`on-policy distillation`、`千问 蒸馏`、`在线蒸馏`、`qwen tokenizer`、`Qwen3.5`、`qwen3 OPD`、`qwen2.5 OPD`、`"Qwen3.5" OPD`、`Qwen3.5 MOPD`、`qwen-1.5b`、`Open-MOPD`、`JustRL`、`qwen 蒸馏`、`qwen OPD dataset`、`Qwen3Tokenizer OPD`、`多教师 蒸馏`、`在策略 蒸馏`、`OPD Log`、`qwen opd 实验`、`qwen 1.5b`、`qwen3 MOPD 数据`、`Open-MOPD dataset`、`Qwen DeepSeek multi-teacher`。
- `qwen MOPD`两页读到`has_more:false`（20+14条）。泛`MOPD`/`OPD`各两页40条仍有更多；`qwen3`/`qwen tokenizer`/`Qwen3.5`/`qwen 蒸馏`/`在策略 蒸馏`/`OPD Log`仅读首20条且有更多。**这是相关性筛选后的有界覆盖，不是公司全量文档清单。**
- `"Qwen3.5" OPD`、`qwen-1.5b`、`Qwen3Tokenizer OPD`零结果，不能证明不存在；同义query实际返回了相关记录，搜索词解析并不可靠地等同精确全文匹配。
- 读取**15个不同成功文档**（16次成功fetch，其中Step5交付重复读取一次）；已读相关整段/短文全文，巨大实验页以全文落临时文件后检索并读取完整相关节。另1次fetch失败：Reasoner页引用的`OPD Log` token `GmVewaoYDi3fIVk5JiEcIkUXnDg`返回3380002 Document not found；用`OPD Log`搜索检查，首20条未定位出该同名文档，未无限重试。

### 权限缺口

- 7个嵌入子表在同一批并行首次请求中都失败：`sheets:spreadsheet:read`缺失。涉及SWE turn/traj/length、TB turn，以及Step3p7 MOPD domains/shared/diff。发现统一scope错误后没有再请求其他实验表或重试。
- 一次`auth status --json --verify`诊断：identity=user、verified=true、user.status=ready、tokenStatus=valid；现有scope里没有`sheets:spreadsheet:read`。auth status是专用状态输出，不含通常业务命令的顶层`ok`，按其verified/status字段判定。
- 保存[失败回执](evidence/lark-sheet-permission.json)。不改变认证的前提下，表格中的完整teacher/student、dataset文件列表和结果单元格仍未核实。
- GitLab配置/commit/RJob链接均是飞书原文引用；本子任务没有打开这些外部系统，固定commit内容由T3核查。模型/数据云路径只抄录，不验证存在性或读取内容。
- 文档日期来自drive search的create/update字段（UTC+8）；章节内日期是实验记录标题，不一定等于实际作业结束日期。Docx revision与search图标version不是同一字段，本文记录实际fetch的revision。

### 本地证据

- [精简读取回执](evidence/lark-read-receipts.json)：来源token、实际Docx ID/revision、成功状态、原文总行数、日期。
- [原文短摘录](evidence/lark-primary-excerpts.md)：保留区分计划/执行、tokenizer规则和旧五教师缺失的决定性短摘录。
- [T2交付自检](evidence/lark-checkpoint.md)：T2完成、表格读取受限、下一步交还父任务整合；不越权修改父任务进度。
- 本地标准库验证PASS：15个文档回执的Docx ID/revision/正文行数与原始CLI JSON逐一一致；31次search均`ok:true`；7个表格失败均为同一缺失scope；本地证据链接存在，Markdown均带Modification History。没有新建持久测试脚本。
- 未把完整私有文档复制到持久task目录。原始JSON/Markdown和已查看图片保留在临时目录`/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-lark-t2-20261108/`，便于父任务按需复核；精简证据才是本次持久留存范围。

## 6. 父任务整合建议

1. 把L1/L2标为当前Qwen3.5**计划**，把L3标题保留原写法并用T3确认branch模型，不从`35b`缩写推定完整model ID。
2. 对L4只报告“飞书综述记录的公开实验”，不报告公司已复现；`DAPO-Math-17K`是可确认名称，不能自动补全成某个本地训练文件或认为其已用当前tokenizer编码。
3. 用T1资产核查区分“消息数据可以重新序列化”和“已有token IDs无需转换”：当前四模型的一致性仍须真实tokenizer/template证据；旧Qwen3 special-token/模板说明只能作为需要核查的线索。
4. L8–L10证明Step OPD/MOPD来源和运行存在，但不得拿Step tokenizer或Step结果替代Qwen3.5配置；后续如需嵌入表精确参数，先由用户决定是否补读权限。
