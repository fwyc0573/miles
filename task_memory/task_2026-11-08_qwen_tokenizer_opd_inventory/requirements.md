# Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record the requested tokenizer, dataset and historical OPD/MOPD investigation. |

# Requirements

[Original Request]

> 当前涉及的3组comb模型使用的tokenizer是否是一致的？/data/ycfeng/stepfun-env-handbook/resource_analysis中给出的数据集是否有和 当前涉及的3组comb模型使用的tokenizer一致的？调用lark-cli查看是否有qwen系列的opd/mopd测试记录（是否记录了使用的 dataset等细节），并查看 steptron已有的branch（特别是qwen系列），是否是否有qwen系列的opd/mopd测试记录（是否记录了使用的 dataset等细节）。梳理这些信息。

## Scope and acceptance

1. Identify the four distinct models in current pairs A/B/C and compare actual tokenizer assets, effective prompt templates and runtime use from primary receipts/code. Distinguish token vocabulary equivalence from model output-head size and template options.
2. Classify the datasets in `/data/ycfeng/stepfun-env-handbook/resource_analysis`: original producer, serialization/tokenizer, raw messages versus encoded IDs, evidence of exact compatibility with the current Qwen3.5 assets, and existing conversion/use in the current task.
3. Search accessible Feishu documents using the authenticated Lark CLI, and read relevant primary OPD/MOPD experiment records. Record model, dataset path/name, tokenizer/template, experiment mode, run/result evidence, dates and source links where present; mark absent details explicitly.
4. Inspect existing local and remote-tracking Steptron branches and relevant history, especially Qwen branches. Record fixed commit/path references and distinguish available configuration from evidence that an experiment actually ran.
5. Produce a source-backed synthesis in Chinese with explicit coverage/limitations. Retain English operational completion summary. This is read-only research of systems and source assets; only local task research records may be written. No training, dataset switch, cleanup or external publication is requested.

Current reference task: `../task_2026-11-06_qwen35_three_pairs/`; its budgets and C execution remain unchanged.
