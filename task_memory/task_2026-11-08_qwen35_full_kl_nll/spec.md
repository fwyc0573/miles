## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the specification from decisions D1–D16; Q17–Q19 remain open. |
| 2026-11-08 | Apply D17 to S0/S8; mark S2 as withdrawn pending Q20. |
| 2026-11-08 | Rewrite S2 for the interleaved turn order (D18); update `alive`, the table and trend notes, S5, S8 (D19) and S9. |
| 2026-11-08 | Define KL as RKL, KL(student‖teacher), in S3 (D20). |
| 2026-11-08 | Rename the profile's KL quantities and fields to RKL/`rkl` (D21); correct the `opd.py` line citation. |
| 2026-11-08 | Correct the S5 memory estimate to the measured total. |
| 2026-11-08 | Switch the source data to SWE-1003 0913 (D23–D27): S0 inheritance, S1, S2 data source and turn source, S4 `t_id` and table heights, S8 mounts, S9 checks; numbers that need the audit are marked pending. |
| 2026-11-08 | Add the remaining gap and the run-relative gap; restate the RKL trend and the recovery gap in remaining-gap units (D28–D31) in S4–S6 and S9; set the default baseline lengths B = 10, N = 8 (D32). |

# Spec — Qwen3.5 full 模式 RKL/NLL 与 Distillation profile

原始请求和用户的实际回答见 [requirements.md](requirements.md)（D1–D32；D11、D12 已被取代或撤回）。本文件是本 task 行为规格的唯一来源；从复用 task 继承的内容只给出链接，不复制。

## S0. 复用与改动范围

复用 task：[`task_2026-11-08_qwen35_swe_full_r256`](../task_2026-11-08_qwen35_swe_full_r256/spec.md)（以下称"复用 spec"；本 worktree 中的副本与 `agent-opd` 上的冻结版本相同）。

**原样继承**（以复用 spec 为准）：

| 内容 | 复用 spec 位置 |
| --- | --- |
| 每个 prompt 保留目标 turn 之前的完整消息前缀；Qwen 模板及 `preserve_thinking=true`、`enable_thinking=true`；Steptron 与 Miles 逐阶段对照的要求；数据 receipt 的字段 | S3 第 1–3、6 条（数据源改为本 spec S2） |
| D5 长度规则：prompt `<131072` tokens，`max_new_tokens = 131072 − prompt_tokens` | S3 D5 |
| full 定义：200 个 successful optimizer update，每个 update 256 个候选 slot，update u 使用 bank u−1，跳过的 update 不计数、不换 bank | S2 |
| 优化参数、D4 两层 binary TIS、实际 loss、D2 的 KL 定义（TIS 前，原始 target tokens，更新前的当前 student） | S4 |
| D6 采集规则（1800 s 内至少 231/256）、D7 零 survivor 停止、故障隔离 | S5 |
| GPU 提交方式（StepMind Python `RJobBackend`、H200）；额度改由本 task 的 D17 规定 | S7 |
| train seed 1234、rollout base seed 1729 | S3 第 5 条 |

**不继承**：11 个 GLM-5.2 源文件及其固定副本和 manifest（本 task 改用 SWE-1003 0913 数据，D23–D25，见 S2）、r256 cell、HF 导出（D10）、benchmark 与基线、权重删除流程、四 cell 对比。

**本 task 改动**：数据源和 rollout 取数顺序（S2）、逐 turn 测量（S3）、Distillation profile（S4–S7）。

**代码复用**：
- 已提交的输入适配器 `tests/manual/agent_opd/swe_inputs.py` 及其检查脚本 `check_swe_inputs.py`（复用 Ticket01，本 task 的 ticket 01 已扩展为 interleaved 顺序，并按 S2 改为可选 turn source）。
- 已提交的源数据审计脚本 `tests/manual/agent_opd/audit_swe1003_sources.py`（`721090cc`），生成 S2 的源文件 manifest 和审计数字。
- 复用 Ticket02 的训练代码（`swe_replay.py`、`swe_training.py`、`swe_tis.py` 和启动脚本），已在 `agent-opd` 上提交。按 D1、D22，它的 256-turn 显存问题完整修好、通过自己的 native smoke 后，合并进 `agent-opd-image` 再使用；不重复它已做过的验证。

## S1. 目标与实验矩阵

为两个 teacher 组合各跑一个 full 正式 cell，数据为 SWE-1003 的 0913 SFT 数据（S2）。训练中同时维护 Distillation profile：它记录每个 update 的整体 RKL/NLL，以及每个 source conversation、每个 training turn 的 RKL/NLL。它用于监控，也为以后的算法策略提供运行时数据。

| Experiment cell | Student | Frozen teacher | Protocol |
| --- | --- | --- | --- |
| A/full | Qwen3.5-4B | Qwen3.5-27B | full |
| B/full | Qwen3.5-4B | Qwen3.5-35B-A3B | full |

- 两个 cell 都从同一个原始 Qwen3.5-4B 初始化。每次启动使用独立的 attempt identity。
- 名义规模：每个 cell 200 个 update × 最多 256 turns = 51,200 个 Turn observation；两个 cell 共 400 个 update、102,400 个 Turn observation。实际数量按有效 bank 记录。
- 云端根目录：`/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/`，每个 cell/attempt 一个子目录。
- 不保存 HF，不做评测（D10）。

## S2. 数据源与 rollout 取数顺序（D18、D23–D27）

### 数据源（D23–D25、D27）

1. **源文件**：SWE-1003 的 0913 SFT 数据（DeepSWE resolved 轨迹，经过 garble filtering 和 datapipe 处理），共 8 个 JSON 数组文件。
   - 文件名和顺序以下表 source manifest 模块的 `SWE_DATA_FILES` 为准。
   - 直接从 `/mnt/posttrain/hanqi/swe_data/sft/datapipe_stage2_rft_0913/mnt/posttrain/qidi/garble_filtered_sft_20260913/` 读取，不做云端或本地副本（D25）。读这些文件的作业同时挂载 posttrain 卷（只读使用）、个人云端根目录和本地 NFS 工作区。
   - 源文件 manifest 由审计（第 6 条）读一遍原文件生成：每个文件的路径、recipe 路径、sha256、字节数、mtime、conversation 数、assistant 数、training turn 数，以及视觉 conversation 的 source item index。data source 构造时按 manifest 核对字节数和 sha256（复用 `load_source_population`），不一致即报错。
2. **固定版本的 Steptron 代码**：commit `f4522d45` 中的以下模块，按 sha256 核对后加载，并以 Steptron 模块名注册，因为 turn data 模块按这个名字导入 base loader。

   | 模块 | 用到的内容 | sha256 |
   | --- | --- | --- |
   | `playground/baseline_new/mopd/online_turn_loader.py`（base loader） | `SequentialJsonArrayCursor`、`OnlineTrajectoryTurnSource`、`TurnBalancedTrajectoryBlockMixer`；这三个类与 0710 loader 逐字节相同 | `0c11561f33dacf1a15cd804dbd2f4feed4d1c33734bfaea7a416fdf1efaa740f` |
   | `playground/users/cj/opd/s4_swe_turn_data_1001.py`（turn data） | `MaskAwareSWETurnSource`、`eligible_assistant_positions` | `8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980` |
   | `playground/users/cj/opd/s4_swe_source_manifest_1001.py` | `SWE_DATA_FILES` | `0a46156646a098161151b4ba311a1811e1c61c5e8ab950f3a3617ecf7e67df16` |
   | `playground/users/cj/opd/s4_swe_visual_audit_1001.py` | 视觉判断 `_scan_message`（只在审计中使用） | `5838a812996890f003199b7575788962360ef27810a7c29c4df466b64d0ebc1e` |

3. **Training turn（D24）**：
   - 只有整数 `loss_mask = 1` 的 assistant 消息是 training turn（`eligible_assistant_positions`，`s4_swe_turn_data_1001.py:106–129`）。`loss_mask = 0` 的 assistant（连同它的 reasoning 和 tool calls）以及 tool 回复都留在 prompt 前缀中，不单独生成，也不进入 profile。
   - 每条消息都必须带 0 或 1 的整数 `loss_mask`，否则 native 代码报错。没有 training turn 的 conversation 被跳过。
   - `t_id` 就是 native `assistant_turn_ordinal`：该 turn 在所属 conversation 的 training turn 中的 1-based 序号。它在全部 assistant 中的序号 `source_assistant_turn_ordinal`，以及前缀中被 mask 的 assistant 数 `context_masked_assistant_count`，作为元数据保留在 source identity 中（`s4_swe_turn_data_1001.py:397–409`）。
4. **视觉 conversation（D27）**：
   - 含图像或视频内容的 source conversation 整条跳过。student 只读文本：在 Qwen 文本渲染下，base64 图像会让长度暴涨，视觉 token 会出现却没有对应的图像特征。
   - 判断用上表固定版本的 `_scan_message` 检查每条消息：图像或视频字段（如 `image`、`pixel_values`、`video`），图像或视频类型的内容片段，base64 的 `data:image/...`，视觉 token（如 `<|vision_start|>`、`<|image_pad|>`）。
   - 名单由审计计算，写入源文件 manifest 的 `visual_source_item_indices`，再作为 `excluded_source_item_indices` 传给 `MaskAwareSWETurnSource`。不读取 posttrain-release 上的 receipt。
5. **渲染输入**：
   - 工具定义取首条消息的 `tools`，没有时取 `tool_schemas`，与 native `tokenize_swe_prefix` 相同（`s4_swe_turn_data_1001.py:77`）。
   - Qwen 模板参数由配置给出（S0 继承表）。首条消息的 `reasoning_effort` 不传入，因为 Qwen 模板不读取它。
   - 审计记录首条消息中 `preserve_thinking` 和 `reasoning_effort` 的取值。若有首条消息的 `preserve_thinking` 不为 true，在正式 cell 之前报告。
6. **审计（ticket 01）**：在 CPU RJob 中读一遍原文件，报告：
   - 每个文件的 conversation、assistant、training turn、视觉 conversation 数，以及每个 conversation 的 training turn 数分布；
   - Qwen 渲染后的 prompt 长度和超长 turn；
   - 同一 SWE 任务的多条 conversation 在文件顺序中是否相邻；
   - 32 × 8 和 1 × 8 两种配置下 200 个 update 的模拟：每个 conversation 跨的 update 数、trend 有定义的 conversation 数、每个 update 覆盖的 conversation 数和任务数。

   结果写入 ticket 01 的测试报告，并更新下文"取数顺序"第 6 条的估算。

### 取数顺序（D18、D23、D26）

采用 Interleaved turn order：同时打开 M 个 source conversation，轮流从每个 conversation 按 turn 从小到大取一个 block；取完的 conversation 由文件顺序中的下一个补上。本 task 取 M = 32、block = 8（D26）。

1. **由 native 类组成**（上表的固定模块）：
   - 一个 `SequentialJsonArrayCursor`，按 manifest 的文件顺序、文件内的 conversation 顺序读取。
   - M 个 `MaskAwareSWETurnSource` 共享这个 cursor：构造后把每个 source 的 `cursor` 换成共享的那一个（cursor 构造时只读取文件 stat，`close` 可重复调用，`online_turn_loader.py:31–46`、`:297–301`）。每个 source 同一时间只打开一个 conversation；它从共享 cursor 取 conversation 时跳过视觉 conversation 和没有 training turn 的 conversation（`s4_swe_turn_data_1001.py:360–395`），然后按 training turn 从小到大发出，发完再取下一个（`online_turn_loader.py:575–604`）。
   - 外面套 `TurnBalancedTrajectoryBlockMixer`，权重全为 1，`trajectory_block_turns = block`。它每次选已发 turn 数最少的 source（并列时轮转），连续取 block 个 turn，或取到该 conversation 结束为止，然后重新选择（`online_turn_loader.py:781–818`）。
   - 结果：每约 M × block 次取数中，每个打开的 conversation 贡献约 block 个连续 turn；同一 conversation 的 turn t+1 一定在 turn t 之后被取到。
2. **配置**：
   - input config 的 `swe_active_conversations`（M，默认 1）和 `swe_block_turns`（block，默认 8，即 native recipe 的 `online_trajectory_block_turns`）不变。M = 1 时与 SWE-1003 的 streaming 顺序（一个 source 加 block mixer）完全相同，所以只保留这一条取数路径。本 task 设 M = 32、block = 8，M × block = 256，等于每个 update 的 slot 数。
   - turn source 由配置按名字从一张表中选择：`loss_masked` 对应 `MaskAwareSWETurnSource`（本 task）；`all_assistants` 对应 `OnlineTrajectoryTurnSource`，供复用 task 的 GLM-5.2 数据使用（这些数据没有 `loss_mask` 字段）。保留后者，是因为 GLM 副本在本地可读，取数顺序的共用逻辑可以在本地用真实数据回归检查；SWE-1003 原文件只能在 RJob 中读取。
   - 配置还给出固定版本 Steptron 代码的根目录和上表各模块的 sha256。
3. **取数与长度规则**：
   - 顺序只由源数据决定，不依赖 tokenizer。每个取出的 turn 用复用的渲染和长度规则处理。
   - 超长的 turn 记一次 rejection（写日志），也算在 block 里，然后继续取下一个。
   - 通过长度检查的 turn 依次填入 256 个候选 slot。超时 slot 的处理沿用复用规则：记为缺失，不补取。
   - 因为有 rejection，且 block 会因 conversation 结束而提前终止，update 的边界与轮次不完全对齐：个别 conversation 在一个 update 中可能出现少于或多于 block 个 turn。profile 按用户规则对同一 update 内的 turn 取平均。
4. **identity**：沿用复用的 `uid`、`group_id`、`assistant_turn_ordinal`、`epoch` 等字段（`epoch` 取自共享 cursor），另外记录：
   - 全局取数序号（从 0 起）；native 的 `source_row_index` 在多个 source 下只是单个 source 内的计数。
   - `remaining_turns`：取出该 turn 后，它所属 conversation 还剩几个 training turn 未取。由各 source 公开的 `active_remaining_turns` 得到。
   - `source_assistant_turn_ordinal`、`context_masked_assistant_count` 和 native 的 `target_policy`（数据源第 3 条）；data source 的 identity 另记 turn source 名称、视觉排除名单的 sha256 和源文件 manifest 的 sha256。
   - data source 另外报告每次取数（一个 bank）中取完最后一个 turn 的 conversation，包括最后一个 turn 因超长被拒绝的情况。这个报告供 `alive` 使用（S4）。
5. **cell 之间相互独立**：每个 cell 有自己的 data source 和 cursor，都从文件开头开始，取到的序列相同。
6. **估算（待审计）**：
   - 一个有 n 个 training turn 的 conversation 跨约 ceil(n / 8) 个 update。默认 k = 10 时，跨度不少于 11 个 update、即 training turn 数不少于 81 的 conversation 才有 trend 值。
   - 每个 update 约 32 个 conversation，每个约 8 个 turn。200 个 update 取约 51,200 个 turn；覆盖的 conversation 数约为 51,200 除以每个 conversation 的平均 training turn 数。
   - SWE-1003 数据的 training turn 数分布、覆盖的 conversation 数和 trend 有定义的比例，由审计给出。若每个 conversation 的 training turn 数中位数明显低于 81，带着数字和保持 M × block = 256 的方案回来找用户（D26）。
7. **已知后果**：
   - 起始阶段 32 个 conversation 同时从 turn 1 开始，前若干 update 的 prompt 偏短；大约 10–20 个 update 后，各 conversation 的进度错开，prompt 长度分布趋于稳定。所以第一个 update 的耗时偏低，吞吐要看前约 20 个 update 的各阶段耗时（S8）。
   - 同一 block 内的连续 turn 共享前缀，prefix cache 大部分仍然有效；block 的第一个 turn 能否命中上一个 update 留下的缓存，取决于缓存是否被换出。
   - 若同一 SWE 任务的多条 conversation 在文件中相邻（source manifest 模块注明保留原有的行重复），同时打开的 32 个 conversation 可能来自少数几个任务；审计报告每个 update 覆盖的任务数。
   - 数据与复用 task 不同，两者的 RKL 曲线不能对比。

## S3. 逐 turn 测量（D4、D5、D14）

对一个 successful update 中的每个 training turn i，定义以下记号：
- `m`：TIS 之前的原始有效 target mask；
- `k`：native `opd_reverse_kl` 的逐 token 值，由当前配置的 estimator 写入；sampled-token 时等于 `s − q`（`miles/backends/training_utils/loss/hub/opd.py:88–89`）；
- `s`：更新前的 actor 评分，即 D2 使用的当前 student log-prob。

则：

```text
rkl_sum_i = sum(m * k)
nll_sum_i = sum(m * (-s))
tokens_i  = sum(m)
RKL_i = rkl_sum_i / tokens_i
NLL_i = nll_sum_i / tokens_i
```

- **计算位置**：在 `swe_tis.token_sums` 已有的逐样本循环中计算。不增加模型 forward。
- **分布式汇总**：
  - 同一样本在不同 CP rank 上的部分和相加；只取一个 TP/PP 副本参与，与复用 D7 的计数方式一致。
  - 每个 update 只汇总一次，数据量约 256 行 × 3 个 float64，外加样本 identity。
  - 这些行随现有的 optimizer-step record 送到 rollout 进程。
- **宏观值**：`RKL(u) = Σ rkl_sum / Σ tokens`，`NLL(u) = Σ nll_sum / Σ tokens`，按 token 加权（D6）。
  - record 中已有的 `kl_before_tis` 改为由同一组和推出，保证只有一个来源；新增 `nll_before_tis`。
  - 一致性检查：`Σ tokens` 必须等于 native 训练 mask 统计的 `original_tokens`，行数必须等于 `actual_turns`。不一致时把该 update 标记为未验证，训练继续（S7）。
- **Estimator 标签**：
  - 由 native 配置 `opd_log_prob_top_k`、`opd_top_k_strategy`（`miles/utils/args/configs/on_policy_distillation.py:42–60`）在一处推出，写入 record 和 profile。
  - 取代复用代码中写死的标签字符串。以后加入 top-k 或 full vocab 时，只改 native estimator 和这一处推导。
  - sampled-token 下，数值与复用 D2 相同。
- **RKL 的含义**（D20、D21）：本 task 测量的 KL 都是 RKL，即 KL(student‖teacher) = E_{y～student}[log student(y) − log teacher(y)]，回答“student 经常生成的内容，teacher 是否也倾向于生成”。在 student 自己采样的 token 上平均 `s − q`，就是它的 sampled-token 估计。以后加入的 top-k 或 full vocab estimator 必须估计同一方向（native 写入的字段同为 `opd_reverse_kl`）。profile 的量、字段和术语都用 RKL / `rkl` 命名（D21）；复用代码已有的 `kl_before_tis` 和 native 的 `opd_reverse_kl` 保持原名。
- **NLL 的含义**：student 在自己采样的 token 上的 NLL，相当于 student 每 token 熵的采样估计。sampled-token 下，teacher NLL = RKL + NLL，因此不单独存储（D4）。

## S4. Distillation profile 的内容（D3、D6–D9、D13、D28–D31）

每个 experiment cell 一个 profile，放在 rollout 进程中，位于 data source 旁边。

**Turn observation**（一个 training turn 在一个 successful update 中的一次测量）：

| 字段 | 含义 |
| --- | --- |
| `update_id` | 1-based successful update 序号 |
| `c_id` | conversation 编号：按首次参与训练的顺序从 0 起连续编号 |
| `t_id` | `assistant_turn_ordinal`：在该 conversation 的 training turn 中的 1-based 序号（D24）；被 mask 的 assistant 不是 training turn，不占序号 |
| `replay_num` | 同一 turn 此前已有的 observation 数；本 task 恒为 0 |
| `rkl_sum`、`nll_sum`、`tokens` | S3 的三个和；RKL、NLL 均值在读取时计算 |
| `uid` | 复用的 source uid，用于回连原始数据 |

**Source conversation**：`c_id`、`group_id`、`alive`、conversation baseline，以及按 update 追加的条目。
- 条目内容：该 update 中这个 conversation 各 turn 均值的等权平均（RKL 和 NLL 各一个，D6），以及对应的 observation 行。
- `alive`（D7）：data source 报告该 conversation 的最后一个 training turn 已被取出（S2 取数顺序第 4 条），并且训练这个 bank 的 successful update 完成后，变为 False。被超长拒绝或超时缺失的 turn 不影响这一判断。

**宏观（每个 update）**：RKL、NLL、tokens、turns、conversation 数。

**RKL-best update**（D8、D13）：
- 宏观：宏观 RKL 最低的 update。conversation：其各条目中 RKL 最低的那个 update。
- 并列时取最早的 update。
- 记录 `(update_id, RKL, NLL)`，NLL 只是读取该 update 上的值，没有单独的"最佳 NLL"。
- conversation 的最佳条目可以直接映射到表中的对应 observation。

**Baseline 与 remaining gap**（D28、D31）：
- 两个长度由 profile 配置给出：宏观 baseline 的 update 数 B，conversation baseline 的 turn 数 N。默认 B = 10、N = 8（D32，可改）：N = 8 等于一个 block，使 conversation baseline 正好是它的第一个条目；依据见 [D32](requirements.md#round-10--follow-up-answer-2026-11-08)。
- 宏观 baseline `b`：前 B 个 successful update 的宏观 RKL 的算术平均。第 B 个 update 完成后固定。
- conversation baseline `b_c`：该 conversation 最早的 N 个 Turn observation（取数顺序保证 `t_id` 递增）的 RKL 等权平均，与 D6 的等权一致。超长、超时的 turn 没有 observation，不计入。第 N 个 observation 到达后固定；若某个 update 提供的 turn 多于还缺的个数，只取前面几个，其余只作为被测值。
- 三个比值，都只对 RKL 定义，NLL 只在对应 update 上读取（D13）：

  | 量 | 定义 | 含义 |
  | --- | --- | --- |
  | 宏观 remaining gap | `G(u) = RKL(u) / b` | 整体 RKL 相对开始时还剩的比例 |
  | conversation remaining gap | `G_c(u) = RKL_c(u) / b_c`，`RKL_c(u)` 为该 conversation 在 update u 的条目 | 该 conversation 相对它自己开头还剩的比例 |
  | run-relative gap | `RKL_c(u) / b` | 该 conversation 相对整个 run 开始时水平的位置；所有 conversation 共用一个分母 |

- baseline 一旦固定，任何 update 或条目的比值都可以读取，包括 baseline 窗口之内的（D28）。查询时用已存的值相除，不重算历史。
- baseline 尚未固定，或 baseline ≤ 0 时，依赖它的比值、trend 和 recovery gap 都不计算。sampled-token 估计在 token 少时均值可能为负，所以 baseline ≤ 0 能够发生；这类 conversation 单独计数，不做截断或替换。

**RKL trend**（D9、D29）：窗口 k 是查询参数；日志使用配置的默认值 10。正值表示 RKL 下降（变好）。
- 宏观：`G(U−k) − G(U)`，U 为最新的 update。`U ≤ k` 或宏观 baseline 未固定时不计算。
- conversation：设其最新条目在 update `u_c`，参考条目取 update `≤ u_c − k` 中最新的一个，值为 `G_c(参考) − G_c(u_c)`。没有参考条目或 conversation baseline 未固定时不计算。
- 同一条曲线的 baseline 固定，所以 trend 就是两个 update 的 RKL 之差除以 baseline：比较的仍是两个 update，换成 baseline 的单位后，不同 conversation、两个 cell 之间可以直接比较。
- 注意：full 模式下每个 turn 只训练一次，所以 conversation trend 比较的是同一 conversation 的不同 turn（本顺序下相隔约 8k 个 turn），结果会混入 turn 位置本身带来的差异。

**Recovery gap**（D30）：
- 宏观：`G(U) − G(RKL-best update)`。
- conversation：`G_c(最新条目) − G_c(最佳条目)`。
- 与 remaining gap 共用 baseline，恒 ≥ 0；baseline 未固定或 ≤ 0 时不计算。

**解读限制**：
- 开头 32 个 conversation 同时从 turn 1 开始（S2 取数顺序第 7 条），所以宏观 baseline 只覆盖这些 conversation 的前约 8B 个 turn，之后的 update 混合了各种位置的 turn。conversation baseline 来自它的前 N 个 turn，之后的条目来自更靠后的 turn。full 模式下无法把训练带来的变化和 turn 位置本身的差异分开。
- 越晚开始训练的 conversation，baseline 是在训练得越久的 student 上测得的；conversation remaining gap 描述的是它自己跨度内的变化，run-relative gap 才与整个 run 的开头比较。
- student 比 teacher 小，RKL 不会降到 0。remaining gap 是相对开始时还剩的比例，其中一部分可能无法降低。

**二维表**：
- 行是 `t_id`（从小到大），列是 `c_id`（从左到右即首次训练的先后），每格是该 `(c_id, t_id)` 的最新 Turn observation；更早的 presentation 保留在历史中（D7）。
- 每列的格数等于该 conversation 已训练的 training turn 数，各列高度不同（分布待审计，S2 数据源第 6 条）；超长、超时的 turn 留空。被 mask 的 assistant 不是行。
- 失败、超长、超时的 turn 不进入表（D7）。

## S5. 数据结构与查询（D15）

| 部分 | 结构 | 写入代价 |
| --- | --- | --- |
| Turn observations | 按列存放、只追加的数组（容量按倍数增长） | 每个 update O(该 update 的 turn 数) |
| 宏观行 | 以 `update_id` 为下标的数组，另存 RKL-best 指针和宏观 baseline | O(1) |
| Conversation 条目 | 每个 conversation 一串只追加的条目，另存最佳条目和最新条目的指针，以及 baseline 的累计和与已计入的 observation 数 | 每次出现 O(1) |
| 查找表 | `group_id → c_id`；`(c_id, t_id) → 最新 observation 行` | O(1) |

- **查询**：只读已有数据，不重算历史。
  - 单个 conversation：trend 用二分查找，O(log 条目数)；remaining gap、run-relative gap、recovery gap 等其他查询 O(1)。
  - 宏观查询 O(1)。
  - 另提供对全部 conversation 一次性计算 remaining gap、run-relative gap、trend、recovery gap、alive 的批量版本，O(conversation 数)，供以后的算法策略使用。
- **内存**：每个 cell 约 51,200 行。数值列每行约 40 字节，共约 2 MB；加上每行保留的 `uid` 字符串和 `(c_id, t_id)` 查找表等，合成的 200 × 256 运行实测共约 13 MB（[ticket 03 模块测试报告](test_report_2026-11-08_distillation_profile_module.md)）。
- **代码位置**：`tests/manual/agent_opd/distillation_profile.py`，与它唯一的使用方 `SweReplay` 放在同一目录。等出现第二个使用方时，再考虑移入 `miles/`。
- **接入点**：
  - `SweReplay.on_train_result` 收到 successful update 的 record 后更新 profile。
  - 每个 bank 里的 trajectory 已带有 source identity，用来映射到 `c_id` 和 `t_id`。
  - `alive` 所需的"已取完的 conversation"由 data source 按 bank 报告（S2 取数顺序第 4 条）。
  - 被跳过的 update 不产生 observation。

## S6. 持久化与日志（D15）

目录：`<cell evidence dir>/distillation_profile/`。每个 successful update 向两个文件各追加一行：

- `updates.jsonl`：`update_id`、estimator 标签、B 和 N、宏观 RKL/NLL 及其和、tokens、turns、conversation 数、RKL-best `(update, RKL, NLL)`、宏观 baseline 和 remaining gap、默认 k 下的 RKL trend、recovery gap，以及五个计数：已出现的 conversation 数、baseline 已固定且为正的 conversation 数、baseline ≤ 0 的 conversation 数、默认 k 下 trend 有定义的 conversation 数、alive 的 conversation 数。未定义的值写为 null。
- `observations.jsonl`：`update_id`，该 update 的全部 observation 行（`uid, c_id, t_id, replay_num, rkl_sum, nll_sum, tokens`），本次新出现的 conversation（`c_id, group_id`），以及本次 alive 发生变化的 conversation。

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
- **挂载**（D25）：正式 cell 的作业除个人云端根目录外，另挂载 posttrain 卷 `juicefs+s3://aliyun-sh/posttrain:/mnt/posttrain`，只读使用，直接读取 S2 的源文件。
- **启动顺序**（D16）：先启动 A，检查它第一个 update 的 profile 和各阶段耗时，通过后再启动 B。
- **吞吐判断**：第一个 update 的 prompt 偏短（S2 取数顺序第 7 条），所以 A 和 B 都逐个 update 记录各阶段耗时，并在约第 20 个 update 时再汇报一次耗时趋势。
- **D19**：第一个 update 若因 rollout 或 teacher 打分太慢违反 D6，按 D6 结束该 attempt，然后增加 GPU，作为新 attempt 重启，不再另行询问；本 task 的非抢占总数保持在 32 以内。两个 cell 同时放不下时改为先后运行，不把正式 cell 的角色放到可抢占作业上（被抢占会结束该 attempt，本 task 没有 checkpoint 可恢复，D10）。D6 的截止时间和最低条数不变。
- 第一个之后的 update 若因吞吐违反 D6，按 D6 结束该 attempt 并报告；D19 不覆盖这种情况，是否重启由用户决定。

## S9. 验证与交付

| 层次 | 检查 |
| --- | --- |
| 文档 | 每条原始需求都能对应到本 spec 的章节或 ticket；链接、计数、依赖图（DAG）正确 |
| 输入（[01](tickets/01-interleaved-turn-order.md)） | 源数据审计（S2 数据源第 6 条，CPU RJob）；在原位源文件上用 `loss_masked` 检查：M = 1 时与单个 native `MaskAwareSWETurnSource` 的序列完全相同，渲染前的消息与 native 规范化结果相同；M = 32、block = 8 时的顺序性质、`remaining_turns` 和取完报告、超长 rejection、两个独立实例序列相同；`all_assistants` 在本地 GLM 副本上的已有检查仍通过 |
| 逐 turn 测量（[02](tickets/02-per-turn-sums.md)） | CPU：长短不一的样本、CP 切分时，逐 turn 和相加等于原有标量；GPU：在 A 的第一个 update 上检查一致性 |
| Profile（[03](tickets/03-distillation-profile.md)） | CPU 合成序列：同一 update 内多个 turn、跳过的 update、窗口未到、并列最佳；baseline 未固定、baseline ≤ 0、trend 参考条目落在 baseline 窗口内、remaining gap 与 run-relative gap 的手算值；离线重建结果与内存一致；故障注入；每个 update 的计算耗时 |
| 正式 cell（[04](tickets/04-a-full.md)、[05](tickets/05-b-full.md)） | 200 个实际 successful update；profile 文件各 200 行；observation 数等于实际训练的 turn 数；每个 update 都通过一致性检查；采集耗时；RJob 终态 |
| 报告（[06](tickets/06-profile-report.md)） | 用保留的证据重新计算 |

最终报告按 cell 给出：
- update 1、10、50、100、150、200 处的宏观 RKL/NLL 和 remaining gap（baseline 窗口内的 update 在 baseline 固定后补算），以及宏观 baseline；
- RKL-best update、默认 k 下的 RKL trend 和 recovery gap；
- 训练结束时 profile 的统计：出现过的 conversation 数、alive 数、baseline 为正和 ≤ 0 的 conversation 数、trend 有定义的 conversation 数，以及 conversation remaining gap、run-relative gap、trend、recovery gap 的分位数；
- 准确的产物路径和观察到的局限。

不做 benchmark，也不做因果结论。
