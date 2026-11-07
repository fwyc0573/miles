# Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | 保存只读飞书正文的决定性短摘录；完整文档仍仅放临时目录。 |

# 决定性原文短摘录

任务：`QWEN-TOKENIZER-T2-LARK`。这是2026-11-08读取快照，不是另一份维护中的实验配置。行号指CLI返回Markdown，实际Docx revision见`lark-read-receipts.json`。

## 当前三组是测试要求

来源：[explore-mopd](https://wvixbzgc0u7.feishu.cn/wiki/IAvRwliqDikShjkrDZac5lGtncc)，行11–31：

> [11.06 qwen系初步列测试]
>
> 创建task，先落地docs。核心为验证以下comb：
> - Qwen3.5-4B + Qwen3.5-27B
> - Qwen3.5-4B + Qwen3.5-35B-A3B
> - Qwen3.5-27B + Qwen3.5-397B-A17B
>
> 较小的作为student，较大的作为teacher
>
> 使用默认的 dataloader 等，trainer等待batch设定为256；无需使用replay机制

## 旧小模型数据不是统一单 OPD 设置

来源：[ROADMAP](https://wvixbzgc0u7.feishu.cn/wiki/NJfJw6yihiSJRrkg19xcCtTEn6I)，行127–130：

> Small size模型：
> - （旧）qwen-1.5b-deepseek- distillation（5teacher），问题：这是mopd的数据，设定并未统一
> - e1-1：补充opd下的运行结果（5个teacher/domain，200steps，每x步替换一次数据，参考旧设定）

## Qwen Ticket07 并不具备完整模型绑定

来源：[AGENTIC OPD](https://wvixbzgc0u7.feishu.cn/wiki/Kuldwh97Pic6yhkV1Sgchs90nZf)，行19–36：

> Ticket 07 （qwen-a3b-35b）：
>
> 使用 小模型：参考 yc-mopd-learning-dynamics-s4-branch 中的 teacher和student，只使用swe teacher（先确认swe的teacher model是否存在；注意，当前tikcket是单opd而非mopd）
>
> 使用 glm-5.2 dataset的4个类型（control_only, thinking_only, control_thinking, neither)
>
> 统一关闭 Ticket06和07 的 router replay，并记录tis保留率。

同页后半，行149–154，实际旧记录：

> 模型：相同初始 student it4046_text/hf；相同、固定的 SWE teacher it973/hf；四组独立从 θ0 开始
>
> 优化：训练 seed 1234；Muon；配置 LR 2e-6；保留 100-step schedule、20-step warmup，实际执行 12 次更新
>
> 运行开关：Router replay、TIS 开启；NCCL checkpoint_engine 权重同步；全局 batch 按 token 平均 loss

## 旧 Qwen3 自定义 tokenizer

来源：[Qwen Template Update](https://wvixbzgc0u7.feishu.cn/wiki/TBqWw6I34ipJ09ke4njcO8shnhg)，行9、17–19、43：

> Tokenizer 名称：`Qwen3MainlineVLLMMultiTurn`
>
> 目前 template 去除 input/output tool_call_id，不让模型学习无意义字符串
>
> 保留最后一轮 user 后的 reasoning_content，丢弃之前轮的 reasoning_content，让模型能够进行多轮 tooluse with reasoning
>
> 加入 `<tool_calls>` 和 `</tool_calls>` 作为多个并行 tool_call 的开头和结束，支持 `"</tool_calls>"` 为 eos token，这两个 tokens 为 special tokens
>
> 一定要用 `Qwen3MainlineVLLMMultiTurnTokenizer` 和 `Qwen3MultiTurnMaskSFTTemplate`

## 数据格式转换并非 tokenizer 等价证明

来源：[ROADMAP](https://wvixbzgc0u7.feishu.cn/wiki/NJfJw6yihiSJRrkg19xcCtTEn6I)，行185开头：

> 训练dataset的数据格式不一致（tool call，thinking等）：需要先将glm-5.2的swe dataset转为step3p6格式，否则训练存在不匹配问题，且格式分类统计也会出错。

来源：[SWE 0602-0801](https://wvixbzgc0u7.feishu.cn/wiki/RAI9wdUUJiSlpCk9O14ca2G7nLf)，行1681–1686：

> 目前得到的最好的SWE turn-level OPD setting是
> - 不开TIS和开KL（SWE-mtlg和SWE-pro基本上能在同时达到高点）
> - 数据选择原始非空think的traj
> - 训练~125iter
>
> SWE-mtlg上，student和teacher最后还是有一个点左右差距；SWE-pro上，student和teacher水平比较接近

## 论文综述中可以确定的数据名

来源：[Rethinking Supervision](https://wvixbzgc0u7.feishu.cn/docx/ISo7dsuDooLLtUxOQvBcmOVxn0g)，行49–52：

> 数据：math，DAPO-Math-17K
>
> 模型： DeepSeek-R1-Distill-Qwen-1.5B student ← JustRL-1.5B teacher
>
> 每个 step：从更新中的 student 采样 64 条新 rollout，采用 top-k reverse KL 优化目标

该页是论文综述，没有公司复现run ID。不要将这些旧模型的数据与当前Qwen3.5 token IDs等同。
