## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the specification from decisions D1–D16; Q17–Q19 remain open. |
| 2026-11-08 | Apply D17 to S0/S8; mark S2 as withdrawn pending Q20. |

# Spec — Qwen3.5 full 模式 KL/NLL 与 Distillation profile

原始请求和用户的实际回答见 [requirements.md](requirements.md)（D1–D16，Q17–Q19 待答）。本文件是本 task 行为规格的唯一来源；从复用 task 继承的内容只给出链接，不复制。

## S0. 复用与改动范围

复用 task：[`task_2026-11-08_qwen35_swe_full_r256`](../task_2026-11-08_qwen35_swe_full_r256/spec.md)（以下称"复用 spec"；本 worktree 中的副本与 `agent-opd` 上的冻结版本相同）。

**原样继承**（以复用 spec 为准）：

| 内容 | 复用 spec 位置 |
| --- | --- |
| 11 个 GLM-5.2 SWE 源文件、固定副本 manifest、完整前缀、Qwen 模板、identity | S3 第 1–3、6 条 |
| D5 长度规则：prompt `<131072` tokens，`max_new_tokens = 131072 − prompt_tokens` | S3 D5 |
| full 定义：200 个 successful optimizer update，每个 update 256 个候选 slot，update u 使用 bank u−1，跳过的 update 不计数、不换 bank | S2 |
| 优化参数、D4 两层 binary TIS、实际 loss、D2 的 KL 定义（TIS 前，原始 target tokens，更新前的当前 student） | S4 |
| D6 采集规则（1800 s 内至少 231/256）、D7 零 survivor 停止、故障隔离 | S5 |
| GPU 提交方式（StepMind Python `RJobBackend`、H200）；额度改由本 task 的 D17 规定 | S7 |
| train seed 1234、rollout base seed 1729 | S3 第 5 条 |

**不继承**：r256 cell、HF 导出（D10）、benchmark 与基线、权重删除流程、四 cell 对比。

**本 task 改动**：rollout 取数顺序（S2）、逐 turn 测量（S3）、Distillation profile（S4–S7）。

**代码复用**：
- 已提交的输入适配器 `tests/manual/agent_opd/swe_inputs.py` 及其检查脚本 `check_swe_inputs.py`（复用 Ticket01）。
- 复用 Ticket02 的训练代码（`swe_replay.py`、`swe_training.py`、`swe_tis.py` 和启动脚本），目前在 `agent-opd` 上未提交。按 D1，它提交并通过自己的 native smoke 后，合并进 `agent-opd-image` 再使用；不重复它已做过的验证。

## S1. 目标与实验矩阵

为两个 teacher 组合各跑一个 full 正式 cell。训练中同时维护 Distillation profile：它记录每个 update 的整体 KL/NLL，以及每个 source conversation、每个 training turn 的 KL/NLL。它用于监控，也为以后的算法策略提供运行时数据。

| Experiment cell | Student | Frozen teacher | Protocol |
| --- | --- | --- | --- |
| A/full | Qwen3.5-4B | Qwen3.5-27B | full |
| B/full | Qwen3.5-4B | Qwen3.5-35B-A3B | full |

- 两个 cell 都从同一个原始 Qwen3.5-4B 初始化。每次启动使用独立的 attempt identity。
- 名义规模：每个 cell 200 个 update × 最多 256 turns = 51,200 个 Turn observation；两个 cell 共 400 个 update、102,400 个 Turn observation。实际数量按有效 bank 记录。
- 云端根目录：`/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/`，每个 cell/attempt 一个子目录。
- 不保存 HF，不做评测（D10）。

## S2. Rollout 取数顺序（D12）

> **状态：已撤回。** 用户否决了随机顺序（requirements Round 3），本节待 Q20 回答后重写；以下内容仅保留到重写为止，不作为实现依据。

采用 native indexed turn order，取代复用 Ticket01 的 streaming 顺序。

1. **总体（population）**：11 个源文件按 manifest 顺序，文件内 conversation 按文件顺序，conversation 内 assistant 位置按消息顺序，组成一个固定列表。
   - 建索引的方法与 native `LazySWETurnSplitDataset._build_index` 相同（Steptron recipe `step3p6_mopd_turn_5experts_fullyasync_tis_no_kl_0710_h200.py:350–409`）。
   - 使用已经按 sha256 加载的 native loader 模块中的 `iter_json_array_item_spans` 和 `message_role`。
   - 每个 conversation 记录：文件、字节区间、`source_item_index`、消息数。每个 turn 记录：所属 conversation、`assistant_turn_index`、`assistant_turn_ordinal`。
2. **顺序**：`torch.randperm(N, generator=torch.Generator().manual_seed(seed))`。seed 是 input config 的字段，本 task 设为 1234，与 behavior-turn-replay 的 Q41 相同。
3. **取数**：
   - 按排列顺序逐个取位置，用复用的渲染和长度规则处理。
   - 超长的位置记一次 rejection（写日志），也算"已取过"，然后继续取下一个。
   - 通过长度检查的位置依次填入 256 个候选 slot。超时 slot 的处理沿用复用规则：记为缺失，不补取。
   - 不放回，不回绕。走到排列末尾时直接报错；本 task 只用约 11.5% 的位置，正常运行不会走到末尾。
4. **identity**：沿用复用的 `uid`、`group_id`、`assistant_turn_ordinal` 等字段，另外记录该 turn 在排列中的位置，便于审计。
5. **cell 之间相互独立**：每个 cell 有自己的 cursor，都从排列的第 0 个位置开始，取到的序列相同。
6. **预期事实**：N = 446,569 个 assistant 位置，4,992 个 conversation（来自 Steptron 的扫描）。
   - population 表示为 `(file_index, source_item_index, assistant_position)` 的 int64 张量；population 和排列的 hash 都是其 `<i8` 字节的 sha256，与 Q41 冻结脚本的算法相同（Steptron behavior-turn-replay worktree `tests/e2e/mopd_turn_replay/freeze_glm_fresh_order.py:143–157`）。
   - 若本 task 的固定副本与 Q41 的源字节相同，两个 sha256 应等于 Q41 manifest（同一 worktree 的 `task_memory/task_2026-10-25_swe_behavior_turn_replay/evidence/glm-parity-20261104/fresh-smoke-20261104a.json` 中的 `population.sha256`、`population.permutation_sha256`）。
   - 若不同，记录本 task 自己的值，并说明原因。
7. **已接受的后果**（D12）：
   - 同一 conversation 的 turns 以随机 turn 顺序到达，不是递增顺序。
   - 相邻 turns 不再共享前缀，SGLang 的 prefix cache 基本失效，teacher 和 student 的 prefill 量会明显增加，耗时在第一个 update 实测。
   - 训练数据与复用 task 的 full cell 不同，两者的 KL 曲线不能直接对比。
8. **估算（推断，未计长度过滤和失败）**：几乎每个 conversation 都会被训练到。一个约 89.5 turns 的 conversation 大约出现在 10 个 update 中，平均间隔约 19.5 个 update。同一 update 内出现同一 conversation 的多个 turn 很少见。

## S3. 逐 turn 测量（D4、D5、D14）

对一个 successful update 中的每个 training turn i，定义以下记号：
- `m`：TIS 之前的原始有效 target mask；
- `k`：native `opd_reverse_kl` 的逐 token 值，由当前配置的 estimator 写入；sampled-token 时等于 `s − q`；
- `s`：更新前的 actor 评分，即 D2 使用的当前 student log-prob。

则：

```text
kl_sum_i  = sum(m * k)
nll_sum_i = sum(m * (-s))
tokens_i  = sum(m)
KL_i  = kl_sum_i  / tokens_i
NLL_i = nll_sum_i / tokens_i
```

- **计算位置**：在 `swe_tis.token_sums` 已有的逐样本循环中计算。不增加模型 forward。
- **分布式汇总**：
  - 同一样本在不同 CP rank 上的部分和相加；只取一个 TP/PP 副本参与，与复用 D7 的计数方式一致。
  - 每个 update 只汇总一次，数据量约 256 行 × 3 个 float64，外加样本 identity。
  - 这些行随现有的 optimizer-step record 送到 rollout 进程。
- **宏观值**：`KL(u) = Σ kl_sum / Σ tokens`，`NLL(u) = Σ nll_sum / Σ tokens`，按 token 加权（D6）。
  - record 中已有的 `kl_before_tis` 改为由同一组和推出，保证只有一个来源；新增 `nll_before_tis`。
  - 一致性检查：`Σ tokens` 必须等于 native 训练 mask 统计的 `original_tokens`，行数必须等于 `actual_turns`。不一致时把该 update 标记为未验证，训练继续（S7）。
- **Estimator 标签**：
  - 由 native 配置 `opd_log_prob_top_k`、`opd_top_k_strategy`（`miles/utils/args/configs/on_policy_distillation.py:42–60`）在一处推出，写入 record 和 profile。
  - 取代复用代码中写死的标签字符串。以后加入 top-k 或 full vocab 时，只改 native estimator 和这一处推导。
  - sampled-token 下，数值与复用 D2 相同。
- **NLL 的含义**：student 在自己采样的 token 上的 NLL，相当于 student 每 token 熵的采样估计。sampled-token 下，teacher NLL = KL + NLL，因此不单独存储（D4）。

## S4. Distillation profile 的内容（D3、D6–D9、D13）

每个 experiment cell 一个 profile，放在 rollout 进程中，位于 data source 旁边。

**Turn observation**（一个 training turn 在一个 successful update 中的一次测量）：

| 字段 | 含义 |
| --- | --- |
| `update_id` | 1-based successful update 序号 |
| `c_id` | conversation 编号：按首次参与训练的顺序从 0 起连续编号 |
| `t_id` | `assistant_turn_ordinal`（1-based） |
| `replay_num` | 同一 turn 此前已有的 observation 数；本 task 恒为 0 |
| `kl_sum`、`nll_sum`、`tokens` | S3 的三个和；KL、NLL 均值在读取时计算 |
| `uid` | 复用的 source uid，用于回连原始数据 |

**Source conversation**：`c_id`、`group_id`、`alive`，以及按 update 追加的条目。
- 条目内容：该 update 中这个 conversation 各 turn 均值的等权平均（KL 和 NLL 各一个，D6），以及对应的 observation 行。
- `alive` 的口径待 Q17 决定。推荐：按 D7 的规则，对照整个固定排列判断——该 conversation 的全部 assistant 位置都已被取过（训练、超长 rejection 或失败）后，才变为 False。

**宏观（每个 update）**：KL、NLL、tokens、turns、conversation 数。

**KL-best update**（D8、D13）：
- 宏观：宏观 KL 最低的 update。conversation：其各条目中 KL 最低的那个 update。
- 并列时取最早的 update。
- 记录 `(update_id, KL, NLL)`，NLL 只是读取该 update 上的值，没有单独的"最佳 NLL"。
- conversation 的最佳条目可以直接映射到表中的对应 observation。

**KL trend**（D9）：窗口 k 是查询参数；日志使用配置的默认值 10。
- 宏观：`KL(U) − KL(U−k)`，U 为最新的 update。`U ≤ k` 时不计算。
- conversation：设其最新条目在 update `u_c`，参考条目取 update `≤ u_c − k` 中最新的一个，值为两者 KL 之差。没有参考条目时不计算。
- 注意：full 模式下每个 turn 只训练一次，所以这里比较的是同一 conversation 的不同 turn，结果会混入 turn 位置本身带来的差异。

**Recovery gap**：
- 宏观：`KL(U) − KL(KL-best update)`。
- conversation：最新条目的 KL 减去其最佳条目的 KL。
- 两者恒 ≥ 0。

**二维表**：
- 行是 `t_id`（从小到大），列是 `c_id`（从左到右即首次训练的先后），每格是该 `(c_id, t_id)` 的最新 Turn observation；更早的 presentation 保留在历史中（D7）。
- 这张表是稀疏的：本 task 每列约 10 格。
- 失败、超长、超时的 turn 不进入表（D7）。

## S5. 数据结构与查询（D15）

| 部分 | 结构 | 写入代价 |
| --- | --- | --- |
| Turn observations | 按列存放、只追加的数组（容量按倍数增长） | 每个 update O(该 update 的 turn 数) |
| 宏观行 | 以 `update_id` 为下标的数组，另存 KL-best 指针 | O(1) |
| Conversation 条目 | 每个 conversation 一串只追加的条目，另存最佳条目和最新条目的指针 | 每次出现 O(1) |
| 查找表 | `group_id → c_id`；`(c_id, t_id) → 最新 observation 行` | O(1) |

- **查询**：只读已有数据，不重算历史。
  - 单个 conversation：trend 用二分查找，O(log 条目数)；其他查询 O(1)。
  - 宏观查询 O(1)。
  - 另提供对全部 conversation 一次性计算 trend、recovery gap、alive 的批量版本，O(conversation 数)，供以后的算法策略使用。
- **内存**：每个 cell 约 51,200 行，每行约 40 字节，共约 2 MB。
- **代码位置**：`tests/manual/agent_opd/distillation_profile.py`，与它唯一的使用方 `SweReplay` 放在同一目录。等出现第二个使用方时，再考虑移入 `miles/`。
- **接入点**：
  - `SweReplay.on_train_result` 收到 successful update 的 record 后更新 profile。
  - 每个 bank 里的 trajectory 已带有 source identity，用来映射到 `c_id` 和 `t_id`。
  - `alive` 所需的"剩余未取位置数"由 data source 提供。
  - 被跳过的 update 不产生 observation。

## S6. 持久化与日志（D15）

目录：`<cell evidence dir>/distillation_profile/`。每个 successful update 向两个文件各追加一行：

- `updates.jsonl`：`update_id`、estimator 标签、宏观 KL/NLL 及其和、tokens、turns、conversation 数、KL-best `(update, KL, NLL)`、默认 k 下的 KL trend、recovery gap，以及三个计数：已出现的 conversation 数、默认 k 下 trend 有定义的 conversation 数、alive 的 conversation 数。
- `observations.jsonl`：`update_id`，该 update 的全部 observation 行（`uid, c_id, t_id, replay_num, kl_sum, nll_sum, tokens`），本次新出现的 conversation（`c_id, group_id`），以及本次 alive 发生变化的 conversation。

补充说明：
- 这两个文件足以离线重建整个 profile。运行时只以内存中的 profile 为准，不回读文件。
- 训练侧已有的 `updates.jsonl` 新增 `nll_before_tis` 和 estimator 标签。逐 turn 行不重复写入训练侧文件。
- 复用配置没有启用 wandb/tensorboard，所以"现有 metrics 日志"指的就是上述 JSONL 证据。

## S7. 容错（D16）

- profile 的更新和写文件是 soft gate：
  - 出错时写日志，记下第一次出错的 update，并把 profile 标记为未验证。
  - 之后 profile 停止更新，避免基于不一致的状态继续推导；训练照常进行。
- S3 的一致性检查失败时，只把对应 update 标记为未验证，训练继续。
- native 训练、通信和 I/O 的故障处理不变，D6、D7 的停止规则不变。
- profile 不参与任何训练控制。

## S8. GPU 与执行（D16、D17、Q18）

- **D17**：本 task 自己的非抢占 H200 额度为 32 卡，只计本 task 已提交、未终止的作业，与其他 task 无关。超过 32 卡的部分可以用可抢占 RJob 提交（`ResourceConfig.preemptible=True`，按 RJob runbook 的可抢占提交一节）。
- **初始布局**：沿用复用 task 的每 cell 布局（复用 spec S7 中 8 student + 2 teacher 的估计，尚未验证），两个 cell 约 20 GPU，在 32 卡以内。
- **启动顺序**（D16）：先启动 A，检查它第一个 update 的 profile 和各阶段耗时，通过后再启动 B。
- **Q18（待答）**：第一个 update 若因吞吐不足违反 D6，按 D6 结束该 attempt。推荐：之后增加 GPU，作为新 attempt 重启，不再另行询问，本 task 的非抢占总数保持在 32 以内；两个 cell 同时放不下时改为先后运行，而不是把正式 cell 的角色放到可抢占作业上（被抢占会结束该 attempt，本 task 没有 checkpoint 可恢复，D10）。D6 的截止时间和最低条数不变。

## S9. 验证与交付

| 层次 | 检查 |
| --- | --- |
| 文档 | 每条原始需求都能对应到本 spec 的章节或 ticket；链接、计数、依赖图（DAG）正确 |
| 输入顺序（[01](tickets/01-indexed-turn-order.md)） | 在真实固定副本上用 CPU 检查 population 和排列、前 512 次取数的 identity、超长 rejection、两个独立 cursor、剩余位置计数、建索引的耗时和内存 |
| 逐 turn 测量（[02](tickets/02-per-turn-sums.md)） | CPU：长短不一的样本、CP 切分时，逐 turn 和相加等于原有标量；GPU：在 A 的第一个 update 上检查一致性 |
| Profile（[03](tickets/03-distillation-profile.md)） | CPU 合成序列：同一 update 内多个 turn、跳过的 update、窗口未到、并列最佳；离线重建结果与内存一致；故障注入；每个 update 的计算耗时 |
| 正式 cell（[04](tickets/04-a-full.md)、[05](tickets/05-b-full.md)） | 200 个实际 successful update；profile 文件各 200 行；observation 数等于实际训练的 turn 数；每个 update 都通过一致性检查；采集耗时；RJob 终态 |
| 报告（[06](tickets/06-profile-report.md)） | 用保留的证据重新计算 |

最终报告按 cell 给出：
- update 1、10、50、100、150、200 处的宏观 KL/NLL；
- KL-best update、默认 k 下的 KL trend 和 recovery gap；
- 训练结束时 profile 的统计：出现过的 conversation 数、alive 数、trend 有定义的 conversation 数、conversation recovery gap 的分位数；
- 准确的产物路径和观察到的局限。

不做 benchmark，也不做因果结论。
