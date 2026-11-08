## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Fix the RKL direction and completion-only scope: rescore the same completion with current student each update; preserve the original D2 reduction. |
| 2026-11-08 | Apply the explicit D9 temporary independent allocation and post-expiry continuation amendment. |
| 2026-11-08 | Freeze D1–D10 and the source-backed contract after explicit whole-document confirmation. |
| 2026-11-08 | Draft the four-cell protocol from the request; explicitly hold source-dependent decisions for the interview. |

# Qwen3.5 SWE full versus r256 — Specification

**Status: FROZEN / DOCS_LANDING_COMPLETE.** 用户已确认D1–D10及源码继承契约，作为后续实施依据。原始需求与实际回答由 [requirements.md](requirements.md) 维护。

## S0. 已核实的复用依据

下表中Miles路径相对本仓库；Steptron路径相对`/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/`。参考worktree存在本地修改，HEAD身份不等于全部文件内容身份；执行冻结需同时保存实际源内容。

| Topic | Inspected source | Fact and implication |
| --- | --- | --- |
| Qwen既有配置 | Miles `tests/manual/agent_opd/run_qwen35_opd.py:175–245` | 原始HF初始化，Adam、constant2e-6、warmup0、TP2/DP4、GBS8、128K context、8192 response、token-mask TIS[0.5,2]；本次256目标与replay不是已验证行为。 |
| GLM-5.2 SWE来源 | Steptron `playground/users/wyx/MOPD/step3p6_mopd_turn_5experts_fullyasync_tis_no_kl_0710_h200.py:59–71` | 原始目录`/mnt/posttrain/hanqi/data/swe/distill_ablation_0623/`，distill_0 part0000–0004和distill_1 part0000–0005，共11源。实际读取优先核验已记录的个人云副本身份。 |
| Native turn/default ordering | Steptron `playground/users/wyx/MOPD/step3p6_mopd_online_turn_loader_0710.py:218–236,407–425,463–518`；上述recipe`:527–577,589–627` | 全assistant-turn前缀、完整历史、角色规范化、在线顺序读取并epoch回绕；未做replay实验的task去重/随机pool。SWE-only只有一类source。 |
| 旧replay的定制 | Steptron `playground/users/ycfeng/MOPD/bounded_replay_inputs.py:187–300,377–395` | task组划分/去重/shuffle与不回绕的QueryStream属于定制，不是默认loader。 |
| Replay预算参考 | Steptron `playground/users/ycfeng/MOPD/bounded_replay_protocol.py:22–36,122–129` | 当前旧r256为8次连续复用，d50是相位偏移；本次50次连续复用/200updates是显式新预算。当前参考LR2e-6、warmup0、train seed1234、rollout seed1729、eval100题。 |
| KL计算与聚合 | Miles `miles/backends/training_utils/loss/hub/opd.py:88–94`；`hub/losses.py:266–278,400–403` | 原始OPD逐token值为student_logp−teacher_logp；现有logged `opd_reverse_kl`经过TIS修改后的mask聚合、分母仍为原始token数。它不是未经筛选的全部原始token均值。 |
| 精确TIS计数缺口 | Miles `examples/infra_features/train_infer_mismatch_helper/mis.py:147–163`；`tests/manual/agent_opd/audit_qwen35_training_tokens.py:607–608` | 已有low/high mask fractions；历史后TIS mask未落盘、绝对survivor count为空。本次需在实际mask处做低成本计数，不能从四舍五入日志比例伪造精确tokens。 |
| 参考双层TIS | Steptron `playground/users/wyx/MOPD/step3p6_mopd_turn_5experts_fullyasync_tis_no_kl_0710_h200.py:926–929`；`playground/baseline_new/mopd/step3p6/step3p6_mopd_fullyasync_64x4_0415.py:751–755`；`playground/rl/ppo_tis_cfg_negative.py:180–209,249–317,393–395` | token[0.5,2]与回答几何平均[0.9897,1.001]的两个binary mask相乘。D4已选此规则；与既有Miles保留后仍乘ratio的规则不同。 |
| Replay扩展入口 | Miles `miles/rollout/data_source.py`、`miles/rollout/fully_async_data_buffer.py` 与现有rollout/data-source插件配置 | `num_steps_per_rollout`是拆分batch，不等于同bank重复更新。应在已有rollout/data-source生命周期接入复用，而不是复制整套训练栈。具体最小入口在实施前设计检查中选择。 |
| 100题与avg@4 | Steptron `playground/users/ycfeng/MOPD/bounded_replay_evaluation.py:131–147,571–661`；`tests/e2e/mopd_step3p6_bounded_replay/swe_formal.py:20` | `formal_subset`取既有500题manifest前100题，seeds1729–1732；完整400attempt才产出avg@4，基础设施缺失时为INCOMPLETE/null。 |
| 有效子集参考 | Steptron `playground/users/ycfeng/MOPD/bounded_replay_runtime.py:459–525`；参考task `requirements.md:1286–1292` | 原参考使用1800s acquisition wait与90%最低比例，即至少231/256；D1/D6已明确采用。 |
| 已有导出身份 | Miles `tests/manual/agent_opd/qwen_export.py:180–239` | 已有`qwen_text_export.json`的packaged状态、source、dtype/tensor覆盖和rollout_id，不必另造重复的Qwen包装器。新任务需关联successful update与eval生命周期。 |
| Async eval可复用入口 | Miles `miles/ray/rollout/eval_dispatch.py:38–118`；`miles/rollout/checkpoint_eval.py:63–80` | 现有外部checkpoint evaluator接口可承载参考SWE评测；默认队列满时会wait/skip、自有快照失败也删除，且不删除复用的save-HF。任务生命周期须补足这些实际差异。 |
| 已有成功计数证据 | Miles `tests/manual/agent_opd/inspect_qwen35.py:705–746` | 既有Megatron成功optimizer counter与publication deltas可复用；rollout_id不是successful update，不能仅按目录编号计训练进度。 |

先前A/B实际运行与完整HF验收见`../task_2026-11-06_qwen35_three_pairs/summary.md`。当前原始11源数据字节、SWE evaluator运行能力和新batch容量均未在本次文档阶段实际读取/运行验证。

## S1. 目标与实验矩阵

在 Miles 已完成的 Qwen3.5 A/B OPD 验收基础上，比较两种教师下的新鲜轨迹训练与连续轨迹复用。数据仅使用 GLM-5.2 的 SWE 部分，数据取用与加载对齐 Steptron 默认逻辑。

| Experiment cell | Student | Frozen teacher | Protocol |
| --- | --- | --- | --- |
| A/full | Qwen3.5-4B | Qwen3.5-27B | full |
| A/r256 | Qwen3.5-4B | Qwen3.5-27B | r256 |
| B/full | Qwen3.5-4B | Qwen3.5-35B-A3B | full |
| B/r256 | Qwen3.5-4B | Qwen3.5-35B-A3B | r256 |

这里的 experiment cell 是实验配置组合，不是 Miles 部署中的 reconcile cell。每次启动使用独立 attempt identity；失败重启不能覆盖先前证据，也不能拼接为一条无中断训练记录。

既有 A/B 验收只提供模型加载、数值、权重发布与纯文本 HF 重载基础，不证明本任务的默认数据加载、256-turn batch、50次 replay、200-update 或 SWE benchmark 已可运行。

## S2. 实验预算与计数

用户明确指定：四个 cell、每 update 使用256个 turn、学习率2e-6、同 bank 连续训练50次、总计200 updates、每50 updates 存储 HF、100题 avg@4、逐 update KL 与 TIS 训练 token 数；资源规则采用 S7 中的 D9 及其显式修订。

以下继承参考full/r256定义及已有Qwen初始化方式，纳入最终文档冻结：

- 一个 training turn 是一个 assistant-turn 的完整输入及其一次学生续写；多轮 conversation 可以提供多个 turn，不把整段 conversation 计为一个 turn。
- full 每次 update 获取一个新 bank；r256 每个 bank 目标256条新生成轨迹，每次 update 各使用一次，连续使用50次后换 bank。
- update 按 successful optimizer update 计数；跳过的优化或失败尝试不占成功计数，不发布对应 checkpoint。
- 四个 cell 独立从同一原始 Qwen3.5-4B 初始化；旧 A/B 已训练 HF 只作为历史证据。

**D1已确认：** 到达有限截止时间后，使用已完成的有效子集；r256固定复用该实际bank。以下是每次均有256条有效轨迹时的名义预算，实际计数必须按有效membership记录，不能把计划数填为实际数。

| Protocol | Update 范围与 bank | Banks/cell | 新生成轨迹/cell | 训练 presentations/cell |
| --- | --- | ---: | ---: | ---: |
| full | update u 使用 bank u−1 | 200 | 51,200 | 51,200 |
| r256 | 1–50 / 51–100 / 101–150 / 151–200 各一个 bank | 4 | 1,024 | 51,200 |

全矩阵计划800个成功 updates；204,800次 presentations、104,448条新生成轨迹是无缺失时的名义数，不含失败请求成本。“新生成”不等于“prompt 全局不重复”：默认loader允许epoch回绕。r256 无旧实验中的8次上限、尾部补齐或 delayed revisit。

## S3. 输入、加载与比较控制

1. 采用Steptron默认SWE配方中的11个GLM-5.2原始JSON源，展开每段对话全部assistant turns；每个prompt保留目标turn之前的完整消息前缀。默认在线loader按文件及对话turn顺序消费、无shuffle，文件用尽后允许epoch回绕。冻结实际使用的代码内容和解析后的配置；原始文件当前可读性与Qwen重编码后的数量待执行核验。
2. 通过同一真实样本的Steptron与Miles逐阶段对照，证明任务/对话/turn identity、消息内容与轮次选择一致。Qwen沿用已有`miles/utils/chat_template_utils/templates/qwen3.5_fixed.jinja`，`preserve_thinking=true`、`enable_thinking=true`；输入训练与评测全过程保留消息和工具语义。默认loader一致不能用token vocabulary一致替代，也不能强行采用Step tokenizer或Step专用parser。
3. 复用已有 loader/预处理接口；实现差异必须有逐阶段证据。不能直接沿用旧 Qwen 的924训练/24监测输入来代表本次默认 GLM-5.2 加载。
4. 旧replay的prompt去重、task组shuffle、train/probe划分、256固定监测输入与全程唯一prompt约束属于其定制逻辑，不是默认loader。本任务不自动继承这些数据重写；“51,200个full生成slot”不要求51,200条唯一prefix，也不因旧924条数据而减少本任务预算。已知benchmark重叠若在源调查中发现，记录事实后再提出具体处理决定。
5. 四cell共用源配方、默认有序turn流、基准题集与seed定义。每个cell建立独立cursor，从同一默认流起点开始；按已计划的256slots推进，超时slot记录缺失，不因完成先后改变下个bank输入。对应bank序号的输入候选一致，而full/r256在相同update的覆盖量不同，这是协议本身的差异。train seed1234、rollout base seed1729；沿用现有确定性请求seed派生并记录实际seed，不要求异步运行bitwise相同。每cell自己生成轨迹，teacher目标按身份隔离，不共用一个竞争消费cursor或跨教师冒用目标。
6. 数据 receipt 至少保存 source identity、conversation/turn identity、实际呈现顺序、prompt 长度、原始有效生成 tokens，以及失败/过滤原因。训练记录能回连到实际来源，而不是只保留合成 batch 序号。

**D5长度规则：** Qwen重新编码后的prompt必须`<131072`，保留完整历史，`max_new_tokens=131072-prompt_tokens`。取消旧Qwen小数据构建时为8192response预留输入空间的规则。相同消息在Step与Qwen tokenizer下不要求token IDs相同；长度过滤由各自真实编码决定，差异需要计数解释。

## S4. Replay、优化与逐步度量

### Replay 行为

Canonical bank 保留原始 prompt/response tokens、原始有效 target mask、生成时行为策略概率、生成版本、冻结 teacher 对相同 tokens 的目标。复用 update 重新计算当前 student 的概率与 TIS；不得用旧的 student feedback 代替当前前向。当前两组 student 均为 dense 4B，不能把 teacher 的 MoE 架构误认为需要 student routing replay。

复用的每次成功 update 只提交一次 bank 使用计数。异步重复/晚到返回不得增加 bank 容量、覆盖已确认轨迹或污染后续 bank。完整 bank 最后一次使用后，依实际所有权释放其临时 payload，保存轻量审计信息。

### 优化参数

**D3研究后采纳：** Miles/Megatron CLI`adam`，采用decoupled-weight-decay即AdamW语义；betas`(0.9,0.98)`、epsilon`1e-8`、weight decay`0.1`，按native parameter-group规则施加；学习率**constant2e-6**、warmup**0**。依据与官方披露限制见`optimizer_research.md`；其超参数建议已按用户“研究并采纳”指令落实。weight decay从旧A/B的0变为0.1，不能把旧运行验收当本任务新配置验收。

当前参考协议也已将warmup改为0，旧spec中的warmup20不再适用。训练采样保留双方已有的temperature1.0、top_p1.0、top_k−1、n1；参考源配置见`artifacts/readiness/native-anchor-config-reconcile-1007b/preview-config.json:880–890`，执行时验证实际请求。D5使用剩余128K总长额度；TIS由D4确定。其他模型/部署参数从已有Qwen兼容路径继承，不搬用Step3p6大模型拓扑。

### D4 — 已确认TIS规则

令`r_t = exp(logp_student_current_t - logp_behavior_at_generation_t)`。对每条回答，使用原始有效生成token计算`r_answer = exp(mean(log(r_t)))`。token保留条件为`0.5 <= r_t <= 2`，回答保留条件为`0.9897 <= r_answer <= 1.001`；实际保留mask是原始mask与上述两层条件的交集。两层都通过的权重为1，其他为0，**不再对保留token乘r_t**。

每个update重算当前student值，原始behavior/teacher目标保持不变。训练采用参考及既有Qwen共同的**全局原始有效target token分母**；TIS不以survivor数重新归一化。适配优先通过已有custom-TIS/损失接口，并用参考公式与非均匀长短样本验证binary权重、阈值边界与实际token归约。

### 实际反向传播目标

保留已有Miles Qwen的sampled-token OPD路径，**D2主KL是观测量，不直接对该均值反向传播**。入口链为`loss/objective.py:29–125` → `hub/opd.py:8–94` → `hub/losses.py:95–212,244–278` → `hub/math_utils.py:255–278`。

对每个update，记该次更新前独立actor评分为`s_i`，带梯度的训练前向log-prob为`l_i`，冻结teacher目标为`q_i`，原始生成行为概率为`b_i`。令`sg`为stop-gradient：

```text
a_i   = sg(q_i - s_i)                       # Scalar task reward is zero.
rho_i = exp(l_i - sg(s_i))                  # PPO training ratio, not TIS ratio.
w_i   = sg(D4_binary_mask(s_i, b_i))
N     = sum(original_valid_mask_i)          # Global DP/microbatch target count.
L_pg  = sum(m_i * w_i * max(-rho_i * a_i,
                           -clip(rho_i, 0.8, 1.28) * a_i)) / N
```

固定`loss_type=policy_loss`、`use_opd=true`、`opd_type=sglang`、`opd_log_prob_top_k=0`、`opd_kl_coef=1`、`advantage_estimator=grpo`、`normalize_advantages=false`、`use_rollout_logprobs=false`、`skip_actor_forward_only=false`、`eps_clip=0.2`、`eps_clip_high=0.28`、`eps_clip_c=None`、`kl_coef=0`、`use_kl_loss=false`、`entropy_coef=0`、`use_opsm=false`及total-token normalization。零scalar reward来自`miles/rollout/on_policy_distillation.py:411–443`；其余为旧Qwen显式配置与native默认。Optimizer state在bank边界持续保留，不能每bank重新初始化。

每次replay重新生成`s_i`及其派生的advantages/`opd_reverse_kl`；不从canonical bank复用旧current评分或旧advantages。只有`l_i`承载本次policy梯度；teacher、behavior、评分快照和筛选mask全部detach。D4改变TIS为双层binary权重，保留已有PPO surrogate；不宣称它与Step未clip的log-prob surrogate在所有数值情形完全等同。实际loss、detach和分布式gradient scaling须由02核验，不能只看同名KL曲线。

### 逐 update 观测记录

完成一个cell必须有**200行实际成功update的KL/TIS记录**；全矩阵完成时共800行。以1-based successful update为主键，保留native attempted/skipped counter和weight version关联。D7终止的cell保留实际完成行数并标FAILED/INCOMPLETE，不为补齐200行制造数据；触发失败的batch记录另列。

每行至少包含：cell/attempt、update、bank、bank visit、生成/当前权重版本、实际 turn 数、KL estimator 名称与方向、KL numerator/denominator/value、TIS 前有效 target tokens、TIS 后实际参与训练的 tokens、保留率、有效权重统计、实际 LR、训练 loss、时间戳。

- **D2已确认：** RKL方向为`KL(student‖teacher)`。本实验的逐步采样统计只包含TIS前原始有效**completion tokens**；prompt/prefix和padding不进入分子或分母。每个update用该次更新前的当前student重新评分同一个已存completion，与对应冻结teacher值求差。令仅覆盖有效completion位置的原始mask为`m`，则`kl_before_tis = sum(m * (logp_student_current - logp_teacher)) / sum(m)`，跨DP/microbatch累计分子分母。不得复用生成时或上个update的student评分；不增加重要性权重或额外rollout。该操作与已实施的原D2一致，估计器待选项撤回。OPD surrogate loss、train/rollout数值差与benchmark得分保持各自名称。
- 原生`train/opd_reverse_kl`经过后TIS mask聚合且保留原始token分母，继续作为原生日志保留，不代替主曲线。主曲线复用已有逐token差增加归约，无需额外模型前向。replay旧轨迹上的sampled log-prob gap准确标记其采样来源，不能声称是当前策略fresh分布下的精确KL；有限样本值也不能因负数而裁成0。
- TIS 保留率是实际 surviving training tokens / original eligible target tokens；原始 padding/prompt mask、非有限数排除、TIS 丢弃须可区分。跨 rank 使用实际计数总和，不能平均每序列比率。
- D4的token与整条回答筛选可能重叠，最终survivor数按两个mask交集计数，不能简单相减两层丢弃率。可分别记录两层原因，但同一token不重复扣减。
- TIS 后 token 数必须在真实训练 mask 处记录。旧 A/B 只有原始 target 计数与部分汇总，不足以填补本任务精确的逐步 survivor 要求。
- 零denominator、native skipped update明确记录；D7规定TIS后全batch零survivor时停止当前attempt。缺失KL不得写0或复制邻近update，真实零保留数量则如实记录。
- 同步保留低成本 JSONL/表格与趋势图输入；汇总按实际 token 加权。来自不同 fresh/replay 批次的训练 KL 不自动证明在固定题集上的能力提升。

## S5. 长尾请求与故障隔离

参考 Steptron 当前已实现的 request/collection deadline、有限 retry、completion-order 持久化、`await asyncio.sleep(0)` 协作式让出和晚回调处理。冻结数值时追踪实际 caller 覆盖，不能只抄最内层默认值。

**D6已确认：** 新bank acquisition截止1800s、最低90%（至少231/256）；少于231条结束当前attempt并保留证据，其他cell继续。固定已sealed bank的后续replay visit不重新生成或重新启动采集计时。参考同步collector是`time.sleep(0.1)`轮询，`await asyncio.sleep(0)`位于异步任务/stream消费，不是超时机制本身。SWE agent的请求、环境命令、整个任务和整份benchmark各有独立deadline；不能把长达数小时的agent任务限制拿来替代训练bank截止。

单请求超时不得无限占用 slot 或阻塞其他已完成请求的保存；generation、teacher scoring 与 benchmark attempt 都记录 identity、阶段、起止、deadline、终态和错误摘要。保留已完成结果，后续 RCA 使用持久证据。

**D1/D6已确认：** 256是目标数量；231–256条有效子集可封存。保留原slot identity及缺失原因，不隐藏复制、不无限重试、不改题补足。r256固定实际成功membership并连续复用50次；例如缺1条时，随后50次使用同一255条bank。零有效样本属于低于231的采集失败。

**D7已确认：** 一个已封存bank经全局TIS mask归约后首次出现零survivor，立即结束该cell此次运行，保存触发batch与已有进度，其他cell继续。该batch不执行/伪造成功optimizer update，不提前换bank，不放宽阈值，不静默重启。有效性判断来自真实训练mask与跨rank计数，不能用辅助日志缺失推断为零。D7为用户明确批准的训练数据条件，不改变一般辅助validator的soft-gate要求。

Miles已有`allow_partial_train_step`与动态DP排程，实施先检查其真实支持范围。必须保留合法有效子集，包括231、255等不整除DP数的情况；不能在conversion处静默trim/drop后声称用了封存bank全部有效turn。小规模检查应直接核对实际消耗的UID和mask。

服务整体失效与单样本异常分别处理；请求层故障不能靠吞掉 native 训练/通信/I/O 错误掩盖。独立 cell 与评测的故障不级联停止健康训练。

## S6. HF、异步评测与删除

### Checkpoint

每个 cell 在成功 update **50、100、150、200** 导出最小可直接推理的纯文本 HF package；全矩阵16个 checkpoint。只保存所需 HF 权重、配置、tokenizer 和必要身份元数据；不保存额外 native/distributed/optimizer/reference 权重副本。

任务cloud root为`/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/`；各cell/attempt独立命名，HF沿用`hf/step_{rollout_id}`模板，结果与attempt evidence放同一任务root。高频缓存放worker-local。复用既有Qwen text-HF exporter的精度、必要FP32 tensor与token/config契约；减少I/O不能改动权重语义。原始模型/数据优先使用既有个人目录副本并核验身份；不对其他cloud目录新增写入。

导出必须绑定成功 update 与当前发布权重版本。所有文件完成后发布完成标记，再由独立 evaluator 消费。部分写入的目录不得进入评测。只保留 HF 意味着不能声称可无损恢复 optimizer/RNG/replay 状态。

复用现有`.complete`和`qwen_text_export.json`的已完成导出证据及native counter/publication记录；避免平行建立一套重复身份系统。默认目录模板使用0-based `rollout_id`：在每次恰好一个成功update且无skip时，四个目录是`step_49/99/149/199`，显示标签仍是HF50/100/150/200；有skip时必须按native成功计数触发并记录实际映射，不靠减一猜测。

### Benchmark

复用参考任务当前的 **SWE-bench Verified + SWE-Agent ACS/native grader**。100题取既有500题有序manifest的前100题，不按本次模型得分重挑；对应原始有序题库`/mnt/stepeval/sweagents_logdir/data/swe_bench2512_all_sorted.json`。seeds为**1729、1730、1731、1732**。每checkpoint400个逻辑attempt，16个训练checkpoint为6,400个。

**D8已确认：** 另做一次共同原始4B基线，使用完全相同的100题、4seeds及评测配置。总计**17个评测点、6,800个逻辑attempt**；仍只产生16个训练HF。基线直接读取受保护的原始模型，不新增权重副本；完整基线分数可与正式训练并行获得，不作为训练启动的额外等待条件。

必须冻结实际task IDs、harness/agent/scorer、模板、采样、context、超时和失败记分规则。avg@4为成功attempts/400，等价于每题4次得分的平均再对100题平均，不能替换为pass@4。模型patch/测试失败计0；基础设施失败保留缺失slot，任何缺失时完整avg@4为null并标INCOMPLETE，不缩分母计算冒充完整成绩。保存每个task/seed/attempt结果，缺失恢复只补同一slot。

评测源以用户指向的`step3p6-replay-v1`为准：`swe_formal.py:182–215`实例化`SweAgentACSEvalConfig`，模型设置来自`playground/agenticeval/sweagents_configs.py:10–25`。**冻结调用配置为temperature1.0、top_p0.95、top_k不覆盖、n1、四固定seed、128K context；max_tokens不增加任务专用override，沿用原调用链，由03记录最终请求上限。** 历史bundle声明top_p1.0与代码配置不一致；本任务按实际构造链采用0.95，并在03核对发出的请求，不将历史wire取值冒充已观察事实。

原参考Git指向`swe-agents` **`1af09e5f90f55f6fbce5f71efe7da0030a2e126e`**，其工作目录本次未展开。源码对象可从后续worktree的submodule读取；核查旧/new两个commit的`step_align.py`/`cli/run.py`，差异仅是new版增加一种context-limit错误分类，未改模型采样传参或agent deadline。采用原参考commit并在01准备实际源；后续`9919c7a3338deb95d5ce82e605ebda48c74cdda0`及其运行成绩只作证据参考。移植模型无关的100题/账本/ACS/native grader，不照搬原runner的Step专用TP8、step3p5 parser和HF12校验；模型入口接已有Qwen配置注册，基线与16HF保持一致。

超时分别继承：单agent任务**18000s**、单环境命令**1200s**（`sweagents_configs.py:66–69,153–161`）；模型query最多**20次**，仅重试native ValidationError/EmptyToolcallError、间隔**5s**，不扩大为任意异常重试。整个checkpoint评测外层deadline最多**72h**（`swe_formal.py:513–515`），跨恢复保留同一绝对deadline，不因重启续期；清理grace单独记录并保证结束所有child。4个seed worker独立，每worker按参考concurrency1处理任务；其他seed/cell结果即时保存。实际HTTP内层重试必须被剩余任务/评测deadline覆盖，在03记录完整caller参数，不误用其他Harbor客户端的timeout作为此SWE链证据。

### Lifecycle

预期生命周期：导出完成 → 持久化 evaluation 入队 → 资源允许时异步启动 → 每个 attempt 完成即保存 → 完整结果归档 → 全部 reader 退出 → 删除该新任务 HF → 保存删除 receipt。

优先复用Miles外部checkpoint evaluator和参考SWE原生执行入口，新增内容只承担task identity适配、持久队列与释放条件。`EvalDispatcher`默认队列满时wait/skip、只从队首回收、失败也释放自有快照，不能直接等同于本任务“16点全部评测且不拖训练”；应在现有接口上完成适配并用阻塞首请求/后请求完成的场景验收。一个cell训练结束后，其待评测记录仍可独立恢复；训练进程退出不能使评测队列或已有attempt证据丢失。

训练只等待自身正确导出所需步骤，不等待benchmark完成；评测失败不能阻塞后续健康训练。按原请求，完整评测归档且全部reader退出后删除所有本任务HF，**包括HF200**。删除范围限本任务生成且达到释放条件的HF；历史A/B验收HF和源模型不属于此范围。

**D10：** 未完成评测保留HF及已有attempt账本；排查/修复基础设施原因后只恢复缺失的同题同seed slot。完整模型失败已经计0，不能重做以挑选更高分。每份评测在首次实际启动时记录72h绝对deadline，跨重启不续期；排队等待GPU不伪称已运行。到期停止该评测并清理进程，保留HF/结果且报告INCOMPLETE，不影响其他训练。最终完整结果未取得的HF不能提前删除；baseline原始权重始终不归本任务清理。

保留轻量结果、per-attempt 状态、checkpoint identity、KL/TIS与删除字节清单。删除 receipt 记录实际删除 bytes，不用共享空间变化反推删除效果或物理 quota 回收。

## S7. GPU 与执行准备

**D9及其修订：** 香港时间 **2026-11-09 05:00之前**（UTC **2026-11-08 21:00**），本任务享有独立的 **64张不可抢占GPU** 额度，其他任务不占此额度。新增RJob若会超过该额度，整份RJob以 `ResourceConfig.preemptible=True` 提交。窗口内获准的作业在截止后可继续完成；截止时及之后的新提交恢复原D9：本人全部已提交、未终止的不可抢占H200承诺合计≤56，含其他任务。

两种规则均计入training student、teacher、rollout、eval和辅助角色，按Pending/Starting/Running请求配置计承诺；未终态的停止中作业也不提前释放账面额度。所有本任务RJob在提交时写入相同task annotation，统一准入锁覆盖实时清单读取与提交。共享执行规则为 [gpu_policy.json](gpu_policy.json)；评测使用实际提交receipt，不另外硬编码额度。提交前核对当前作业及平台quota，不凭旧空闲值提交。

旧A/B每cell的已验收布局为8student+2teacher H200，但其batch仅8turns，不能据此声称新任务256目标已满足容量/吞吐。暂以四个独立10-GPU训练组合40卡作为**未验证估算**；临时额度内剩余部分可供评测及辅助作业，实际布局/并发由真实batch smoke及当时额度决定。旧约75K平均输入长度不能代表新数据，简单将旧单步耗时乘32不足以承诺工期；应测量新数据长度、acquisition/current-student scoring/training各阶段与50次cache reuse耗时。

使用个人认证与本机 source mount 的 StepMind Python `RJobBackend`，遵循现有 GPU/存储 runbook。平台容量和任务 ceiling 分开核查；不为扩大并发复制健康任务或越限排队。两个教师对的测试可并行，共享代码与数据配方。

任何32卡及以上运行的 agent-written 辅助 validator 保持 non-blocking soft gate；其错误保存证据并标记未验证，不能单凭辅助判定停止健康训练。

## S8. 验证与交付

先完成文档冻结，再按 [plan.md](plan.md) 的 ticket frontier 实施：真实默认 loader 对照、精确200行排程检查、native 小规模四配置行为验证、checkpoint/异步eval/delete生命周期验证，最后独立四个正式 cell。

接受一个正式 cell 需要：200实际成功updates及原始counters、逐步KL/TIS完整可复算、符合该模式的bank使用与转换证据（full每bank一次；r256每bank连续50次）、四个正确HF发布、四份100×4 benchmark结果、符合已确认策略的权重释放receipt、资源/终态与异常记录。800 updates或exit0本身不能代替其余验收。

最终比较表按教师分别列 full/r256 的50/100/150/200 avg@4、训练 KL、TIS token 数与保留率、生成数量、时间和存储。仅报告实测差异；一组 seed 的结果不支持额外因果或统计显著性结论。

## Freeze and implementation prerequisites

**整体文档已冻结，无遗留访谈决策。** 用户已确认spec与9tickets；D1–D10保留实际回答，其他源码继承和实现约束在最终整体确认中一并接受。

运行前仍需验证的数据可读性、实际Qwen parser/tool交互、native loss/DP计数、256目标吞吐、GPU配额、HF/eval/cleanup能力分别由01/02/03承担，属于已分配实施验收，不是新增科学决策。失败后改变科学规则、继续D7已终止cell或超出原预算的重训须另行决定；只保存HF不提供无损训练恢复。
