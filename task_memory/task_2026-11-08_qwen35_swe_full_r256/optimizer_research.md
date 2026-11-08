## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Trace official Qwen3.5 disclosures and first-party non-LoRA OPD/RL recipes; recommend a Miles-compatible AdamW-semantic configuration with explicit evidence limits. |

# Qwen3.5 OPD 优化器调查

**Task ID: DOC-OPTIMIZER · 检查日期：2026-11-08 · 状态：研究交付，不是实验配置冻结或运行验收。**

## 结论与建议

1. **不能确认 Qwen3.5 官方原始训练使用 Adam、AdamW 或 Muon。** 已完整读取的官方 README 和模型卡没有披露 optimizer、betas、optimizer epsilon 或 weight decay；官方发布博客本次未取得正文。准确表述是“在下述可检查的一手资料中未找到官方优化器披露”，不是“证明官方在所有地方均未披露”。
2. **有直接相关的社区一手配方支持 AdamW 路线。** Miles 的 Qwen3.5-35B-A3B 非 LoRA OPD 配方显式使用 `--optimizer adam`、betas `(0.9, 0.98)`、weight decay `0.1`；Miles 的 Qwen3.5-4B/27B GRPO 配方使用同组参数。verl 有与本任务 B 组相同的 `Qwen3.5-4B ← Qwen3.5-35B-A3B` 非 LoRA OPD 示例，使用 FSDP 的 `torch.optim.AdamW` 默认配置，但其 betas/weight decay 是框架默认值，不是 Qwen3.5 显式推荐。
3. **建议采纳 Miles 自身 Qwen3.5 OPD/RL 配方：保留 CLI 名称 `adam`，采用 AdamW 的 decoupled-weight-decay 语义、betas `(0.9, 0.98)`、epsilon `1e-8`、weight decay `0.1`。** epsilon 来自实际 Miles 所用 Megatron 版本的通用默认值，不是 Qwen 官方超参数。用户指定的 constant LR `2e-6`、无 warmup、200 updates 与同 bank 连续复用 50 次不因本研究改变。

这是依据已合并、可复现社区配方提出的**本任务推荐**，不是作者做过优化器对照后认定的最优解。官方身份由模型发布者 Qwen 拥有；社区训练配方由各框架仓库维护者拥有；最终实验合同仍由 [requirements.md](requirements.md) 和 [spec.md](spec.md) 拥有，本文件不修改它们。

## 1. 官方检索范围与结果

### 1.1 可完整检查的来源

| 来源与 owner | 来源日期 / 固定版本 | 实际检查结果 |
| --- | --- | --- |
| QwenLM 官方 Qwen3.5 发布期 [README](https://github.com/QwenLM/Qwen3.8/blob/7e103aebdbff11c98cc1cd6a2a568988cfd38168/README.md) | 2026-03-02，`7e103aeb…` | 完整 178 行；训练和 RL 的概要、finetuning 框架建议，没有优化器/相关数值。Paper 只是无链接文字，不是可读取的技术报告。 |
| Qwen 官方 [Qwen3.5-4B 模型卡](https://huggingface.co/Qwen/Qwen3.5-4B/blob/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a/README.md) | 模型仓库最后修改 2026-03-02；`851bf6e8…` | 完整正文 77,646 字符；optimizer/Adam/AdamW/Muon/beta/epsilon/weight-decay 检索均无命中。 |
| Qwen 官方 [Qwen3.5-27B 模型卡](https://huggingface.co/Qwen/Qwen3.5-27B/blob/fc05daec18b0a78c049392ed2e771dde82bdf654/README.md) | 模型仓库最后修改 2026-04-24；`fc05daec…` | 完整正文 92,402 字符；同组关键词无命中。 |
| Qwen 官方 [Qwen3.5-35B-A3B 模型卡](https://huggingface.co/Qwen/Qwen3.5-35B-A3B/blob/59d61f3ce65a6d9863b86d2e96597125219dc754/README.md) | 模型仓库最后修改 2026-04-24；`59d61f3c…` | 完整正文 93,145 字符；同组关键词无命中。 |
| Qwen 官方 [Qwen3.5-397B-A17B 模型卡](https://huggingface.co/Qwen/Qwen3.5-397B-A17B/blob/8472618112abcbd45acbcdc58436aff4233c23f7/README.md) | 模型仓库最后修改 2026-04-24；`84726181…` | 完整正文 94,777 字符；同组关键词无命中。覆盖系列首发旗舰，而非只检查 4B。 |
| Qwen 官方 [Qwen3.5-4B-Base 模型卡](https://huggingface.co/Qwen/Qwen3.5-4B-Base/blob/1001bb4d826a52d1f399e183466143f4da7b741b/README.md) | 模型仓库最后修改 2026-04-23；`1001bb4d…` | 完整正文 3,713 字符；同组关键词无命中。Base 卡也不能给出 pretraining optimizer。 |

模型仓库日期和 revision 来自各模型的 Hugging Face `https://huggingface.co/api/models/Qwen/<model-name>`，是**仓库最后修改时间**，不是 README 的单独修订日期。检查日期均为 2026-11-08。

模型卡的关键原话只说明阶段与产物，例如 4B 卡第 17 行：

> “This repository contains model weights and configuration files for the post-trained model in the Hugging Face Transformers format.”

第 46 行的 `Training Stage: Pre-training & Post-training` 也没有提供两阶段的 optimizer。模型结构的 `norm-epsilon` 不能当作 optimizer epsilon，推理 sampling 的 Best Practices 不能当作训练建议。

官方对后训练的公开建议可确证到 [README 第 152–154 行](https://github.com/QwenLM/Qwen3.8/blob/7e103aebdbff11c98cc1cd6a2a568988cfd38168/README.md#L152-L154)：

> “We advise you to use training frameworks, including UnSloth, Swift, Llama-Factory, etc., to finetune your models with SFT, DPO, GRPO, etc.”

这推荐的是**框架和训练方式**，没有推荐 AdamW/Muon 或其 betas/epsilon/weight decay，也没有 Qwen3.5 full-parameter OPD 的优化器合同。

### 1.2 博客、技术报告与访问限制

- 官方首发日期由发布期 README 的 News 确认为 **2026-02-16**；引用项指向 [Qwen3.5: Towards Native Multimodal Agents](https://qwen.ai/blog?id=qwen3.5)。该 URL 本次 `webfetch` 返回空正文；普通 HTTP fetch 返回 HTTP 200、92,790 字符的站点前端 HTML，而非文章正文。**没有把这个访问失败记作“博客不含 optimizer”。**
- 官方旧地址 `https://qwenlm.github.io/blog/qwen3.5/` 返回 404。官方 GitHub Pages 仓库 main tree 本次没有 Qwen3.5 文章路径。没有继续逆向前端或绕路获取文章。
- `QwenLM/Qwen3.5` 当前自动解析为 **QwenLM/Qwen3.8**；因此额外读取 2026-03-02 的 Qwen3.5 发布期 commit，避免把 Qwen3.8 的内容冒充 Qwen3.5 披露。当前 README 的 Qwen3.5 段落也没有 optimizer，最终证据以上述固定发布期版本为准。
- 搜索使用 `Qwen3.5 official optimizer AdamW Muon technical report`、`Qwen3.5 official blog technical report Qwen3.5 optimizer reinforcement learning Adam` 和 `"Qwen3.5" "technical report" optimizer`。结果没有提供可确认属于本任务 dense/MoE 系列的独立官方技术报告；出现了 Qwen3 Technical Report 与 Qwen3.5-Omni Technical Report，**均排除**。这是有限检索结果，不是不存在报告的证明。

**官方证据缺口：** pretraining、SFT、RL、distillation 各阶段的 optimizer、betas、epsilon、weight decay 和选择理由均未能确认。本报告不把 Qwen3/Qwen2.5/Qwen3.5-Omni/Qwen3.8 的优化器结论迁移过来。

## 2. 决定性社区一手证据

### 2.1 Miles：Qwen3.5 非 LoRA OPD 的显式配方

Owner：**radixark/miles**。本次固定仓库 snapshot `bb18e6ab7811e9301ee1690914eb7499ff3996c9`；OPD 脚本最后触及 commit [12754e95…](https://github.com/radixark/miles/commit/12754e9507e64d5e537288da17793246e913c525)，日期 **2026-09-21**。日期是文件修订时间，不是实验运行时间。

- [例子 README](https://github.com/radixark/miles/blob/bb18e6ab7811e9301ee1690914eb7499ff3996c9/examples/on_policy_distillation/qwen3_5_35b_selfdistill/README.md) 明确写：`Qwen3.5-35B-A3B`、`single 8×H200 node`、`--opd-type megatron`；学生是 base 35B，教师是经过 RLVR 的同模型 checkpoint。不是 LoRA/SFT 示例。
- [Phase 2 脚本第 67–72 行](https://github.com/radixark/miles/blob/bb18e6ab7811e9301ee1690914eb7499ff3996c9/examples/on_policy_distillation/qwen3_5_35b_selfdistill/phase2_opd_selfdistill.sh#L67-L72) 绑定 Qwen3.5 checkpoint 并启用 OPD；[第 87–91 行](https://github.com/radixark/miles/blob/bb18e6ab7811e9301ee1690914eb7499ff3996c9/examples/on_policy_distillation/qwen3_5_35b_selfdistill/phase2_opd_selfdistill.sh#L87-L91) 是实际传给训练入口的参数：

```text
--optimizer adam --lr 1e-5 --lr-decay-style constant --weight-decay 0.1
--adam-beta1 0.9 --adam-beta2 0.98
```

- [Miles dense recipe 第 83–85 行](https://github.com/radixark/miles/blob/bb18e6ab7811e9301ee1690914eb7499ff3996c9/scripts/run_qwen3_dense.py#L83-L85) 显式注册 Qwen3.5-4B、9B、27B；[第 174–181 行](https://github.com/radixark/miles/blob/bb18e6ab7811e9301ee1690914eb7499ff3996c9/scripts/run_qwen3_dense.py#L174-L181) 对这些 GRPO 模型使用 `adam`、LR `1e-6`、betas `(0.9, 0.98)`、weight decay `0.1`。这是共享配方，但 Qwen3.5 明确是其成员，不能仅凭文件名当作 Qwen3 的结果。

**证据强度：** Qwen3.5-specific 的实际非 LoRA RL/OPD 配方，且使用本任务相同框架，是主要选择依据。OPD README 的 DAPO-math 结果是作者报告，不是本次复测：pure OPD 的 step 0/5 accuracy 为 `0.840/0.852`，response length 为 `14,070/6,132`。不能用它证明 4B SWE、teacher 27B、200 updates 或 50 次 bank 复用收敛，更不能证明 `0.1` 比 `0` 最优。

### 2.2 `adam` 名称追到实现：实际是 AdamW 语义

本地 Miles [model.py](../../miles/backends/megatron_utils/model.py) 第 194–201、234–238 行把 backend 参数组成 `OptimizerConfig` 后交给 `get_megatron_optimizer`；Muon 是第 206–226 行的另一条路径。CLI 名称本身不足以区分 coupled Adam 与 AdamW。

历史 A/B 使用的 Megatron 版本记录为 `0.19.0+eb547f33e`，见 [历史记录](../task_2026-11-06_qwen35_three_pairs/future.md)。本次直接核对 owner **radixark/Megatron-LM** 的公开固定 commit [eb547f33e183479530cfb5428b7c665a110c785f](https://github.com/radixark/Megatron-LM/commit/eb547f33e183479530cfb5428b7c665a110c785f)，日期 **2026-11-03**：

- [optimizer_config.py 第 247–252 行](https://github.com/radixark/Megatron-LM/blob/eb547f33e183479530cfb5428b7c665a110c785f/megatron/core/optimizer/optimizer_config.py#L247-L252)：`adam_eps: float = 1e-08`；`decoupled_weight_decay: bool = True`，原话为 “equivalent to AdamW”。这是 **Megatron 通用默认值**。
- [optimizer/__init__.py 第 509–523 行](https://github.com/radixark/Megatron-LM/blob/eb547f33e183479530cfb5428b7c665a110c785f/megatron/core/optimizer/__init__.py#L509-L523)：CPU offload 要求 decoupled weight decay；CPU Adam class 是 `torch.optim.AdamW`，同时传入 betas 和 epsilon。
- [同文件第 545–561 行](https://github.com/radixark/Megatron-LM/blob/eb547f33e183479530cfb5428b7c665a110c785f/megatron/core/optimizer/__init__.py#L545-L561)：非 offload 路径把 `decoupled_weight_decay` 传给 TE/Apex 的 `adam_w_mode`；PyTorch 路径按该字段选 `torch.optim.AdamW` 或 `torch.optim.Adam`。

因此建议的准确名称是 **“Miles/Megatron `adam`，采用默认 decoupled weight decay，即 AdamW 语义”**；不应擅自把 Miles CLI 改成未核实支持的 `--optimizer adamw`。本次没有启动新 worker，最终有效 optimizer/config/parameter groups 仍需在任务 ticket 02 的原生验证中检查。

### 2.3 verl：与本任务 B 组相同大小的非 LoRA OPD

Owner：**verl-project/verl**。固定仓库 snapshot `b17218ba58a6fbcdfb0de32772e3c2a79f88529d`；示例加入 commit [7757fb0d…](https://github.com/verl-project/verl/commit/7757fb0dfb94a07fcdd59e44041c20e19c583d31)，日期 **2026-06-06**。

实际 [run_qwen3_5_4b_fsdp.sh](https://github.com/verl-project/verl/blob/b17218ba58a6fbcdfb0de32772e3c2a79f88529d/examples/on_policy_distillation_trainer/run_qwen3_5_4b_fsdp.sh) 指定：

```text
STUDENT_MODEL=Qwen/Qwen3.5-4B
TEACHER_MODEL=Qwen/Qwen3.5-35B-A3B
actor_lr=1e-6
actor_rollout_ref.actor.strategy=fsdp2
distillation.enabled=True
distillation.distillation_loss.use_task_rewards=False
```

该脚本没有 optimizer/betas/weight-decay/epsilon override，也没有 LoRA override。配置链为 [ppo_trainer.yaml](https://github.com/verl-project/verl/blob/b17218ba58a6fbcdfb0de32772e3c2a79f88529d/verl/trainer/config/ppo_trainer.yaml) → [actor/dp_actor.yaml](https://github.com/verl-project/verl/blob/b17218ba58a6fbcdfb0de32772e3c2a79f88529d/verl/trainer/config/actor/dp_actor.yaml) → [optim/fsdp.yaml](https://github.com/verl-project/verl/blob/b17218ba58a6fbcdfb0de32772e3c2a79f88529d/verl/trainer/config/optim/fsdp.yaml)：

```text
optimizer: AdamW
optimizer_impl: torch.optim
betas: [0.9, 0.999]
weight_decay: 0.01
lr_warmup_steps_ratio: 0.0
lr_scheduler_type: constant
override_optimizer_config: null
```

[hf_model.yaml 第 42–43、108–109 行](https://github.com/verl-project/verl/blob/b17218ba58a6fbcdfb0de32772e3c2a79f88529d/verl/trainer/config/model/hf_model.yaml#L42-L43) 的两种 LoRA rank 默认均为 `0`。[FSDP engine 第 494–497 行](https://github.com/verl-project/verl/blob/b17218ba58a6fbcdfb0de32772e3c2a79f88529d/verl/workers/engine/fsdp/transformer_impl.py#L494-L497) 对 `module.parameters()` 调用 [build_optimizer 第 328–353 行](https://github.com/verl-project/verl/blob/b17218ba58a6fbcdfb0de32772e3c2a79f88529d/verl/workers/config/optimizer.py#L328-L353)，实际按上述 module/class 实例化优化器。epsilon 没有显式传参，来自 [PyTorch AdamW 默认 `eps=1e-8`](https://docs.pytorch.org/docs/2.15/generated/torch.optim.AdamW.html)。

**证据强度：** Qwen3.5-specific、相同 student/teacher 大小、非 LoRA OPD，实现上确为 AdamW；但采用的是 geo3k vision 数据、vLLM/FSDP2，且优化器数字是**框架继承默认值**，不是 Qwen3.5/SWE OPD 的专门推荐或对照结论。它支持 AdamW 家族选择，却也说明社区对 beta2/weight decay **没有统一共识**。不要把 verl 的 `0.01` 或 `0.999` 说成所有 Qwen3.5 的标准。

辅助交叉检查：owner **THUDM/slime** 的 [Qwen3.5-27B RL 脚本第 117–127 行](https://github.com/THUDM/slime/blob/79aa41a884ab0bf65222c94418f6357d3c31192b/scripts/run-qwen3.5-27B.sh#L117-L127) 也显式使用 `adam`、betas `(0.9, 0.98)`、weight decay `0.1`；该文件最后修订 [859938dc…](https://github.com/THUDM/slime/commit/859938dcb2b0791dbae9084a4d9ae91a4f38f3b7) 于 **2026-10-17**。这是相近 Megatron/SGLang 生态的佐证，不当作独立优化器对照实验。

## 3. 本任务如何采纳，以及不能采纳什么

| 项目 | 建议 | 依据身份 |
| --- | --- | --- |
| Optimizer | Miles CLI `adam`，`decoupled_weight_decay=True`，即 AdamW 语义 | Qwen3.5-specific Miles OPD/RL 配方 + Megatron 实现 |
| Betas | `(0.9, 0.98)` | Miles/Slime 显式 Qwen3.5 配方；也与历史 A/B 一致 |
| Epsilon | `1e-8` | 实际版本 Megatron 通用默认值；不是官方 Qwen3.5 披露 |
| Weight decay | `0.1`，沿用 native parameter-group 应用规则 | Miles 显式 Qwen3.5 OPD/RL 配方；不是所有框架共识 |
| LR / warmup | 仍为 constant `2e-6` / `0` | 用户约束，不移植社区例子的 `1e-5` 或 `1e-6` |

选择 Miles 而不是 verl 数值的理由：**当前任务就用 Miles；Miles 同时提供 Qwen3.5-4B 的非 LoRA RL 配方和 Qwen3.5 的非 LoRA OPD 配方，而且 betas 与已验收 A/B 相同。** 因此按框架所有者的相关配方选 `0.1` 有明确来源，不是随意取值。所有四个 cell 应采用同一冻结配置，避免 full/r256 对照额外引入优化器变量。

历史 A/B 的 `adam` / betas `(0.9, 0.98)` / **weight decay `0`** 已验收，见 [历史验收 archive](../task_2026-11-06_qwen35_three_pairs/summary.md) 和 [历史 native prerequisites 报告](../task_2026-11-06_qwen35_three_pairs/test_report_2026-11-07_native_prerequisites.md) 第 339 行。本建议对该配置的实际变化是 **`weight_decay: 0 → 0.1`**。这必须在主 agent 的最终 spec/requirements 中明写为新任务采用的社区配方；不能把旧 A/B PASS 自动继承为新参数/new bank schedule 的 PASS。本次只给建议，没有改合同或运行配置。

**不建议本任务改用 Muon。** 这不是断言 Muon 不兼容或一定更差，而是未取得 Qwen3.5 官方 optimizer 披露，也没有在上述最相关 Qwen3.5 非 LoRA OPD/RL 一手配方中取得采用 Muon 的依据。Miles 有 `get_megatron_muon_optimizer` 只证明存在实现路径，不能证明该 Qwen3.5 配置、TP2/DP4、OPD 目标和 50 次复用已验收。Steptron 的 Muon + `wd=0.1` 是另一个模型/任务的参考，不作为 Qwen3.5 官方或社区推荐证据。

剩余科学限制：没有 optimizer/weight-decay ablation，没有 SWE 数据证据，没有 200-update/50-reuse 配方验证；教师 27B 的 OPD 适用性来自本地已有 A/B 资格，而不是以上社区 OPD 实验。社区证据已经足以支持上述有边界的选择，停止扩搜 Unsloth/Axolotl/ms-swift 的 LoRA/SFT 配方，避免用不相关例子制造结论。

## 4. 核对方法、工具问题与验收边界

- 一手访问使用 `webfetch` 和 Code Mode 的 HTTP `fetch`；GitHub tree/commit API 定位实际文件和日期，再读取固定 SHA 的 raw source。对模型卡读取完整 raw README 后检查章节与 optimizer 关键词；不是只看搜索摘要。
- Hugging Face `webfetch` 首次发生 `Transport error (GET https://huggingface.co/Qwen/Qwen3.5-4B/raw/main/README.md)`；HTTP fetch 同地址成功返回 200 并取得全文。博客的空正文/前端 HTML、旧博客 404 见第 1.2 节，仍作为未解决的官方正文访问限制。
- 几个猜测的旧框架文件路径返回 404；随后改用仓库 tree API 找到当前真实文件。不是框架没有 Qwen3.5 支持，也没有对错误 URL 反复重试。
- 未做 GPU/平台/私有云操作，未修改 spec/requirements/代码，未提交 Git。本交付仅写本文件。源码/模型仓库读取不等于本任务运行验证；新配置的 effective optimizer、epsilon、weight-decay groups 与逐步 LR 由 [ticket 02](tickets/02-replay-training-and-metrics.md) 验收。
- 本地文档检查：Python **3.10.6**，`python3 -B -` 内联读取本文件并断言顶端 Modification History、无行末空白、代码围栏配对、全部本地链接存在。实际 **7 个本地链接全部 PASS**；外部 URL 引用 32 次，关键来源的 HTTP 读取证据见上文，不宣称批量外链健康检查。`git diff --no-index --check /dev/null task_memory/task_2026-11-08_qwen35_swe_full_r256/optimizer_research.md` 无空白诊断；退出码为 1（no-index 新文件有差异），不把它记作零退出码测试。

### Phase checkpoint — DOC-OPTIMIZER only

#### 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 0｜TODO 0。官方检索范围与缺口、相关社区配方追到实现、本任务有边界推荐均已记录；博客读取限制随研究交付保留，不伪称成功取得正文。

#### 2. 偏离检测

**结论：** 未偏移，正常推进。检测窗口为本子任务开始至交付；当前前沿为优化器研究文档，其他实验任务不属于本子 agent 的验收范围。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 无新增工具或 harness。 |
| D2 细节反复重试 | CLEAR | 404 后用 tree API 定位；博客限制记录后停止。 |
| D3 支线问题修补 | CLEAR | 未修框架、博客前端或历史运行问题。 |
| D4 可并行任务停滞 | NO DATA | 不评价主 agent 的其他并行任务；本子任务只有一个文档所有权。 |
| D5 超范围镀金 | CLEAR | 仅研究文件，无配置或代码变更。 |
| D6 分析空转 | CLEAR | 两项决定性 OPD 证据已形成推荐，不继续穷尽框架。 |
| D7 路线违背 | CLEAR | 保留用户 LR/bank 约束；推荐与已冻结决定分开。 |

**文档检查：** 本研究验收路径未发现 S1–S6 明显缺陷；不对全任务未检查的 tickets 宣称通过。**归因：** 无。

#### 3. 纠正建议

**分支：** A：研究范围与文档所有权合理，不改 spec/tickets。**需停止的偏离行为：** 无。

接下去由主 agent 将 optimizer 推荐及 `wd=0 → 0.1` 的来源/历史验收边界写入最终实验合同；文档冻结后按 ticket 02 验证实际配置。完成标志不是本报告存在，而是合同明确采纳内容且实际检查满足该 ticket。

#### 4. 最值得关注的 3 点

1. 官方原始 optimizer 仍不能确认；博客正文访问限制必须保留。
2. 推荐的算法是 AdamW 语义，但 Miles CLI 名字仍是 `adam`。
3. `wd=0.1` 是新任务社区配方选择，不继承历史 `wd=0` 的运行 PASS。
