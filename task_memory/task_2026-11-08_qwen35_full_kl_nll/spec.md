## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the specification from decisions D1–D16; Q17–Q19 remain open. |
| 2026-11-08 | Apply D17 to S0/S8; mark S2 as withdrawn pending Q20. |
| 2026-11-08 | Rewrite S2 for the interleaved turn order (D18); update `alive`, the table and trend notes, S5, S8 (D19) and S9. |
| 2026-11-08 | Define KL as RKL, KL(student‖teacher), in S3 (D20). |

# Spec — Qwen3.5 full 模式 KL/NLL 与 Distillation profile

原始请求和用户的实际回答见 [requirements.md](requirements.md)（D1–D20；D11、D12 已被取代或撤回）。本文件是本 task 行为规格的唯一来源；从复用 task 继承的内容只给出链接，不复制。

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

## S2. Rollout 取数顺序（D18）

采用 Interleaved turn order：同时打开 M 个 source conversation，轮流从每个 conversation 按 turn 从小到大取一个 block；取完的 conversation 由文件顺序中的下一个补上。本 task 取 M = 32、block = 8。

1. **由 native 类组成**（Steptron loader `step3p6_mopd_online_turn_loader_0710.py`，已按 sha256 加载）：
   - 一个 `SequentialJsonArrayCursor`，按 manifest 的文件顺序、文件内的 conversation 顺序读取，与复用 Ticket01 相同。
   - M 个 `OnlineTrajectoryTurnSource` 共享这个 cursor：构造后把每个 source 的 `cursor` 换成共享的那一个（cursor 构造时只读取文件 stat，`close` 可重复调用，`:31–46`、`:297–301`）。每个 source 同一时间只打开一个 conversation，按 turn 从小到大发出，发完后从共享 cursor 取下一个 conversation（`:383–427`、`:463–492`）。
   - 外面套 `TurnBalancedTrajectoryBlockMixer`，权重全为 1，`trajectory_block_turns = block`。它每次选已发 turn 数最少的 source（并列时轮转），连续取 block 个 turn，或取到该 conversation 结束为止，然后重新选择（`:669–706`）。
   - 结果：每约 M × block 次取数中，每个打开的 conversation 贡献约 block 个连续 turn；同一 conversation 的 turn t+1 一定在 turn t 之后被取到。
2. **配置**：input config 新增 `swe_active_conversations`（M，默认 1）和 `swe_block_turns`（block，默认 8，即 native recipe 的 `online_trajectory_block_turns`）。M = 1 时与当前的 streaming 顺序完全相同，所以只保留这一条取数路径。本 task 设 M = 32、block = 8，M × block = 256，等于每个 update 的 slot 数。
3. **取数与长度规则**：
   - 顺序只由源数据决定，不依赖 tokenizer。每个取出的 turn 用复用的渲染和长度规则处理。
   - 超长的 turn 记一次 rejection（写日志），也算在 block 里，然后继续取下一个。
   - 通过长度检查的 turn 依次填入 256 个候选 slot。超时 slot 的处理沿用复用规则：记为缺失，不补取。
   - 因为有 rejection，且 block 会因 conversation 结束而提前终止，update 的边界与轮次不完全对齐：个别 conversation 在一个 update 中可能出现少于或多于 block 个 turn。profile 按用户规则对同一 update 内的 turn 取平均。
4. **identity**：沿用复用的 `uid`、`group_id`、`assistant_turn_ordinal`、`epoch` 等字段（`epoch` 取自共享 cursor），另外记录：
   - 全局取数序号（从 0 起）；native 的 `source_row_index` 在多个 source 下只是单个 source 内的计数。
   - `remaining_turns`：取出该 turn 后，它所属 conversation 还剩几个 turn 未取。由各 source 公开的 `active_remaining_turns` 得到。
   - data source 另外报告每次取数（一个 bank）中取完最后一个 turn 的 conversation，包括最后一个 turn 因超长被拒绝的情况。这个报告供 `alive` 使用（S4）。
5. **cell 之间相互独立**：每个 cell 有自己的 data source 和 cursor，都从文件开头开始，取到的序列相同。
6. **估算（推断，未计长度过滤和失败）**：
   - 一个 conversation 跨约 ceil(n / 8) 个 update。按 999 个 conversation 的样本统计（assistant turn 数最小 19、中位数 81、P90 144、最大 464，平均 90.69），分别约为 3、11、18、58 个 update。
   - 每个 update 约 32 个 conversation，每个约 8 个 turn。
   - 200 个 update 取约 51,200 个 turn，覆盖按文件顺序的前约 550–580 个 conversation，其中最后约 32 个只取了一部分。复用 task 的审计显示，前 51,200 个 turn 覆盖 546 个 conversation，所以训练用到的 conversation 与复用 task 的 full cell 基本是同一批。
   - 默认 k = 10 时，跨度不少于 11 个 update、即 turn 数不少于 81 的 conversation（约一半）会有 trend 值。
7. **已知后果**：
   - 起始阶段 32 个 conversation 同时从 turn 1 开始，前若干 update 的 prompt 偏短；大约 10–20 个 update 后，各 conversation 的进度错开，prompt 长度分布趋于稳定。所以第一个 update 的耗时偏低，吞吐要看前约 20 个 update 的各阶段耗时（S8）。
   - 同一 block 内的连续 turn 共享前缀，prefix cache 大部分仍然有效；block 的第一个 turn 能否命中上一个 update 留下的缓存，取决于缓存是否被换出。
   - 训练的 turn 集合与复用 task 的 full cell 基本相同，但顺序不同，两者的 KL 曲线不能逐点对比。

## S3. 逐 turn 测量（D4、D5、D14）

对一个 successful update 中的每个 training turn i，定义以下记号：
- `m`：TIS 之前的原始有效 target mask；
- `k`：native `opd_reverse_kl` 的逐 token 值，由当前配置的 estimator 写入；sampled-token 时等于 `s − q`（`miles/backends/training_utils/loss/hub/opd.py:90`）；
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
- **KL 的含义**（D20）：本 task 中的 KL 都指 RKL，即 KL(student‖teacher) = E_{y～student}[log student(y) − log teacher(y)]，回答“student 经常生成的内容，teacher 是否也倾向于生成”。在 student 自己采样的 token 上平均 `s − q`，就是它的 sampled-token 估计。以后加入的 top-k 或 full vocab estimator 必须估计同一方向（native 写入的字段同为 `opd_reverse_kl`）。
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
- `alive`（D7）：data source 报告该 conversation 的最后一个 turn 已被取出（S2 第 4 条），并且训练这个 bank 的 successful update 完成后，变为 False。被超长拒绝或超时缺失的 turn 不影响这一判断。

**宏观（每个 update）**：KL、NLL、tokens、turns、conversation 数。

**KL-best update**（D8、D13）：
- 宏观：宏观 KL 最低的 update。conversation：其各条目中 KL 最低的那个 update。
- 并列时取最早的 update。
- 记录 `(update_id, KL, NLL)`，NLL 只是读取该 update 上的值，没有单独的"最佳 NLL"。
- conversation 的最佳条目可以直接映射到表中的对应 observation。

**KL trend**（D9）：窗口 k 是查询参数；日志使用配置的默认值 10。
- 宏观：`KL(U) − KL(U−k)`，U 为最新的 update。`U ≤ k` 时不计算。
- conversation：设其最新条目在 update `u_c`，参考条目取 update `≤ u_c − k` 中最新的一个，值为两者 KL 之差。没有参考条目时不计算。
- 注意：full 模式下每个 turn 只训练一次，所以这里比较的是同一 conversation 的不同 turn（本顺序下相隔约 8k 个 turn），结果会混入 turn 位置本身带来的差异。

**Recovery gap**：
- 宏观：`KL(U) − KL(KL-best update)`。
- conversation：最新条目的 KL 减去其最佳条目的 KL。
- 两者恒 ≥ 0。

**二维表**：
- 行是 `t_id`（从小到大），列是 `c_id`（从左到右即首次训练的先后），每格是该 `(c_id, t_id)` 的最新 Turn observation；更早的 presentation 保留在历史中（D7）。
- 每列的格数等于该 conversation 已训练的 turn 数，各列高度不同（样本中为 19–464 个 turn）；超长、超时的 turn 留空。
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
  - `alive` 所需的"已取完的 conversation"由 data source 按 bank 报告（S2 第 4 条）。
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

## S8. GPU 与执行（D16、D17、D19）

- **D17**：本 task 自己的非抢占 H200 额度为 32 卡，只计本 task 已提交、未终止的作业，与其他 task 无关。超过 32 卡的部分可以用可抢占 RJob 提交（`ResourceConfig.preemptible=True`，按 RJob runbook 的可抢占提交一节）。
- **初始布局**：沿用复用 task 的每 cell 布局（复用 spec S7 中 8 student + 2 teacher 的估计，尚未验证），两个 cell 约 20 GPU，在 32 卡以内。
- **启动顺序**（D16）：先启动 A，检查它第一个 update 的 profile 和各阶段耗时，通过后再启动 B。
- **吞吐判断**：第一个 update 的 prompt 偏短（S2 第 7 条），所以 A 和 B 都逐个 update 记录各阶段耗时，并在约第 20 个 update 时再汇报一次耗时趋势。
- **D19**：第一个 update 若因 rollout 或 teacher 打分太慢违反 D6，按 D6 结束该 attempt，然后增加 GPU，作为新 attempt 重启，不再另行询问；本 task 的非抢占总数保持在 32 以内。两个 cell 同时放不下时改为先后运行，不把正式 cell 的角色放到可抢占作业上（被抢占会结束该 attempt，本 task 没有 checkpoint 可恢复，D10）。D6 的截止时间和最低条数不变。
- 第一个之后的 update 若因吞吐违反 D6，按 D6 结束该 attempt 并报告；D19 不覆盖这种情况，是否重启由用户决定。

## S9. 验证与交付

| 层次 | 检查 |
| --- | --- |
| 文档 | 每条原始需求都能对应到本 spec 的章节或 ticket；链接、计数、依赖图（DAG）正确 |
| 输入顺序（[01](tickets/01-interleaved-turn-order.md)） | 在真实固定副本上用 CPU 检查：M = 1 时与当前 streaming 序列完全相同；M = 32、block = 8 时的顺序性质、`remaining_turns` 和取完报告、超长 rejection、两个独立实例序列相同 |
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
