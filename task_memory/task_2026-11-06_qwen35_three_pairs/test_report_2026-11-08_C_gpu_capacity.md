## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Inspect exact parent-supplied rollout0 metadata and replay existing dynamic/fixed singleton DP schedules on CPU; distinguish first-batch row reduction from full-context capacity and refresh the checkpoint. |
| 2026-11-08 | Record read-only diagnosis of C fresh-run training CUDA OOM, existing-config candidates, verification limits and authorization boundaries. |

# C fresh-run GPU capacity diagnosis

Task ID: `QWEN-P3-C-GPU-OOM-CAUSE`.

## 结论

**已证实：`exp-1107-150849-814926` 在 rollout 0 的训练 forward、native no-pipeline schedule 的最后一个 microbatch，分配 LM output projection 的结果时发生 CUDA OOM。不是 eval forward-only，也不是 fused logprob 内部失败。** 当前配置已经使用 fused logprob、full/uniform/1 activation recompute 和完全 CPU optimizer offload；不能把“再开启这些已有选项”作为修复。

异常请求 14.15 GiB，而驱动当时只报告 10.06 GiB free。这里证实的是该次分配失败，不是“该模型在任何 H800 配置下一定放不下”：6.75 GiB reserved-unused 是否可回收、59.05 GiB allocated 的实际持有者、失败 microbatch 的真实 CUDA 张量形状均未获得。不能据此证明 fragmentation、从舍入 allocation 推算失败样本/rank 归属，或承诺某个容量方案必然成功。

**后续 CPU 重放结果：两个 DP shard 的最后一个 microbatch 均包含两个样本，分别为 `[2,5]` 和 `[4,3]`，源码预测 padded tokens 为 130560 和 122368；固定 singleton 对同八个样本的最大值为 89600，降低本批最大 padded rows 31.372549%。** 这使 fixed singleton 成为针对本批 output allocation 更直接、证据更强的首选提案；不证明 CUDA 容量 PASS，也不降低单个 131072-token 样本的最坏上界。详见第6节和 [geometry evidence](evidence/C-first-batch-geometry.json)。

本子任务只读本地源码、日志和已收集的 receipts；只写本报告及明确授权的 compact geometry JSON。没有 GPU、平台、SSH、cloud、auth、delegation、restart 或 optimizer probe；未修改生产代码、flags、manifest 或预算。

## 1. 已观察到的证据

下文 `LOG` 指 `/data/ycfeng/tmp/opencode-v2-tmp/opencode/C-exp-1107-150849-814926-complete.log`；`SCHED` 指 `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-schedule-exp-1107-170946-430400/core/pipeline_parallel/schedules.py`。仓库路径均相对于 `/data/ycfeng/sota-engine/miles`。

| 观察 | 精确来源 |
| --- | --- |
| C student 8 GPU、TP4，teacher 2×8 GPU、TP16；student host memory 配置值 1536 | `training_config.json:87–115` |
| runtime TP4 / DP2 / PP1 / CP1，sequence parallel=True，dynamic batch=True；micro_batch_size=1，max_tokens_per_gpu=131072 | `LOG:206,259,719,742,981,1242,1815,1895` |
| BF16、policy_loss、padded_vocab_size=248320、THD；full/uniform/1 recompute | `LOG:133,686,966,1006,1011–1016` |
| log_probs_backend=fused、recompute_loss_function=False、native cross_entropy_loss_fusion=False | `LOG:220,652–653,1013` |
| optimizer_cpu_offload=True、optimizer_offload_fraction=1.0、overlap_cpu_optimizer_d2h_h2d=True；normal parameter-backup route retained | `LOG:943–953,1025` |
| inference release 请求成功；训练 rollout=0 attempt=0 开始，actor wake_up 成功 | `LOG:3794–3799,3817,3826–3828` |
| rank6/GPU2 wake-up 后 allocated=38.92 GiB、reserved=39.23 GiB、free=36.88 GiB；这是 wake-up 阶段，不是失败前的分解 | `LOG:3826` |
| standalone `_compute_log_prob` 最终返回 ok=true；随后 `actor_train` 开始 | `LOG:3830–3836,3843` |
| 较早还有 allocator/TorchMemorySaver OOM 消息，但这些消息没有阻止 standalone scorer 返回成功；不能把它们等同于最后的终止异常 | `LOG:3815,3819,3830–3833,3850` |
| 终止栈：actor.train → _train_actor → model.train → train_one_step → run_forward_backward_pass → schedules.py:790 → forward_step:511 → model.py:545 → GPT._postprocess:840 → output_layer → layers.py:514 `torch.matmul(total_input, weight.t())` | `LOG:3936–4018` |
| 最终失败 GPU2：request=14.15 GiB；total=79.19 GiB；free=10.06 GiB；process use=67.36 GiB；PyTorch allocated=59.05 GiB；reserved-unused=6.75 GiB；private pools=3.98 MiB；other process 9925=1.72 GiB | `LOG:4018` |
| 另一 actor/rank4 的原始 allocator 消息给出 request=15193866240 bytes、free=10802167808 bytes；不将该 rank 的精确 bytes 替代 GPU2 的舍入数字 | `LOG:4027–4031` |
| 当前可见完整日志只有两次 candidate_version=0 / published_version=0，没有 completed `op=train_step` 记录 | `LOG:2735,3510`；下述只读检查 |
| student cgroup peak=438841257984 bytes=408.7027702331543 GiB；limit=1610612736000 bytes=1500 GiB；failcnt=0，oom_kill=0 | `evidence/first-round/student/C/exp-1107-150849-814926/memory.json:4–16` |
| 已收集 platform receipt 为 Failed，student failed、teacher stopped；这不是新的平台查询 | `evidence/C-terminal-exp-1107-150849-814926-20261108.json:27–42` |

因此，本次首要失败是 **CUDA OOM**。host cgroup 没有重现旧 C 的 host OOM kill；泛化的 Ray worker-death 文本（`LOG:4039`）不能覆盖上述具体异常和 cgroup counters。父任务现已完成 zero-update/无 final HF 链，权威结论及13个 native event 文件的覆盖范围见 [C failure report](test_report_2026-11-08_C_failure.md) lines61–81；本报告不复制平台采集或预算计数。

## 2. 为什么现有 fused/recompute 没有消除这次分配

1. **模型先输出 logits，后计算 completion loss。** `model.py:530–559` 传 `labels=None`，policy_loss 使用 `fp32_output=False`，返回 model output 后才构造 loss callback。`model_provider.py:310–320` 创建 `parallel_output=True` 的 GPT，词表按 TP 分片；没有本次任务的 response-only output projection。日志直接证明失败发生在 output matmul，尚未进入这个 microbatch 的 loss callback。
2. **fused 是 logits 后面的 logprob 运算，不是 fused LM projection。** `logit_processors.py:411–462` 从已有完整 logits 选择 response rows，然后调用 fused scorer；`fused_log_probs.py:67–101` 保存 logits，并在 `inplace_backward=True` 时复用它们写梯度。`logit_processors.py:456–457` 由 `not recompute_loss_function` 选择复用。因此，它避免额外的 vocab-sized 梯度副本，但不能使前面的 `output_layer` 不生成 logits。修改 `log_probs_chunk_size` 也不会缩小这次上游 matmul，而且 fused 分支没有读取该参数。
3. **full recompute 指 transformer layer checkpoint，不包含这次 output projection。** 已提取 pinned `transformer_config.py:680–706` 明确定义 full checkpoint 整个 transformer layer、uniform 按 `recompute_num_layers` 分组。本次是 full/uniform/1，不是未开启 recompute。保存的 checkpoint inputs、当前 layer/workspace 和常驻参数/梯度可能共同形成训练 footprint；没有 allocation snapshot，不能把 59.05 GiB 中的某个精确数值全部归给 checkpoint inputs。
4. **训练与旧 B forward-only 引用模式不能混为一谈。** `SCHED:327–345` 在训练 callback 后返回 scalar loss、只收集 loss metrics；`SCHED:764–787` 每个前序训练 microbatch backward 后执行 `del output_tensor`。`SCHED:790–810` 是最后一个 microbatch，最终异常发生在这里的 forward，而不是 backward recompute。forward-only 则不执行这些删除。旧 B 的 forward-only retention 证据不能自动证明本次训练仍持有上一份完整 logits；`LOG:3899–3907` 的 AccumulateGrad stream warning 也不是 retained CUDA storage 的量化证据。
5. **CPU optimizer offload 不等于模型和梯度不在 GPU。** pinned normalization extraction 的 `core/optimizer/__init__.py:503–543` 使用 `HybridDeviceOptimizer(offload_fraction=...)`；实际 runtime fraction 已是 1.0。参数与 DDP gradients 仍参与 GPU forward/backward。本次不能通过“进一步提高 fraction”改善；也没有证据把异常归给已经执行的 optimizer.step。`model.py:595–605,677–681` 明确在 forward/backward 返回后才执行 optimizer.step/version bump。

两个 supplied schedule copies（normalization extraction 与 schedule extraction）的 `cmp` 为 exit 0。它们的最后-microbatch行号与日志一致。两个目录都不含 pinned `gpt_model.py`、`tensor_parallel/layers.py`、`transformer_block.py` 或 `linear_cross_entropy.py`，本报告关于这些 runtime 文件的具体失败行来自异常栈，**不是声称已读完整 pinned 实现**。另读到的本机参考安装 `.../envs/verl-agent-opd-megatron-sglang/.../gpt_model.py:739–794` 与 `layers.py:566–576` 有 sequence gather / matmul 的相同机制，但版本不同，不能用于确认本次实际 shape/dtype 或推出修复可用。

## 3. 因果判断及还缺什么

**高置信观察：** 训练状态下的一次 LM output matmul 无法取得所需的大块 GPU allocation；已有常驻/训练状态加上新输出触发了失败。该操作一般需要 `element_size × output_rows × local_vocab_columns` bytes。runtime 的 padded vocab/TP 配置可解释为什么此类输出很大，但实际 output rows、dtype、输入 gather buffer、分配对齐尚未实测；不从 14.15 GiB 反解它们。

**待验证推断，按优先级：**

- checkpoint inputs 与训练临时量使 output 前 live allocation 明显高于 no-grad scorer；验证应分别归类参数/梯度、checkpoint inputs、global gather buffers 和当前 output。改变 recompute 分组应改变 checkpoint-boundary持有量，但可能把更大峰值移到 backward。
- 当前源码对 exact rollout0 的 CPU 重放确实把多个样本放进最后一个 microbatch；native log 的8样本/3 microbatches与重放一致。`micro_batch_size=1` 不约束 dynamic packing：`data/rollout.py:484–490` 优先接受预计算 indices，`utils/dp_schedule.py:121–159` 有独立 dynamic/static 分支。dump 未保存实际消费的 indices，故仍不把重放当作 captured CUDA shape。
- allocator cached blocks 或其他未归类持有者可能影响可分配性；reserved-unused 的总量不足以说明它们是否可回收/分割，也不足以证明 fragmentation。

**不能作为已证实根因或独立修复：**

- `14.15−10.06=4.09 GiB` 只是舍入的 request/free 差。不得将 `free+reserved-unused` 当作保证可用预算；也不能反过来把 request>free 当作绝对物理容量不可能的证明。
- 其他进程 1.72 GiB 的全部释放，仅按舍入值也仍差 2.37 GiB；未确认其身份，不能停止它或把 inference 常驻完整 KV cache 作为根因。实际 inference release/wake-up receipts 已成功。
- TMS margin 是 1 GiB（`LOG:1862,2181`）。即使不保留 margin，当时 driver free 仍小于 request；不能推荐取消 margin 或修改 allocator 配置作为未验证的解决办法。
- 再提高 host memory 不直接为 GPU matmul增加显存；旧 host OOM 修复与本次 CUDA allocation 是两个问题。
- `--recompute-loss-function` 不 checkpoint 上游 projection；它还把 fused backward 改成 `torch.empty_like(logits)`（`fused_log_probs.py:84`），不应作为降低本次 output 峰值的默认方案。
- native `cross_entropy_loss_fusion` 不等于本次 OPD policy loss 的 projection融合。当前 `labels=None` 且栈仍经过 `linear_cross_entropy.py:41` 的 `super().forward`，没有证据证明仅开启 native CE flag就能规避这里。

**仍缺失的决定性证据：** 失败 GPU/rank 对应实际消费 indices、真实 tensor dtype与形状；output 前 allocator snapshot/active storage分类；pinned GPT/linear/checkpoint-grouping实现。exact artifact 的 deterministic source geometry已补齐，完整 update/checkpoint链已由父任务审计；二者都不补足 GPU capacity measurement。没有获准重放 GPU 场景，不具备真实 OOM red/green feedback loop，也不声称修复验证 PASS。

## 4. 最小候选方案与权限

以下均为提案，未改变任何配置。必须保持 D7 的完整 prefix/131072总长、8192 response、D9/D15 的八 completions和100计划更新、optimizer及 D8 acceptance。

| 候选 | 有依据的收益与代价 | 使用条件与权限 |
| --- | --- | --- |
| 本地 artifact审计，保持 C 停止 | exact rollout0 metadata/CPU schedule重放已完成；zero-update链由父任务报告拥有 | 本子任务已完成；下一步是父任务形成容量/新授权提案，不追加采集或自动restart |
| 已有 fixed microbatch=1 路径，保留 global batch8和八个样本 | 对本批重放直接把最大 padded rows 从130560降至89600；每rank accumulation由3增至4，全部600920原始tokens和八个rollouts保留，不截断prefix | 本批首选容量提案，不是全流程保证。`utils/dp_schedule.py:143–159` 支持；需在rollout-side owner选择static，不能只改train-side参数。当前共同launcher仍显式写入dynamic，须新的配置/launcher选择及运行授权；不在本子任务实施 |
| 调整已有 full/uniform recompute 分组，例如从1评估2 | pinned config 支持uniform分组；64 layers按其语义从64个一层组变为32个两层组，可能减少checkpoint-boundary inputs，但不缩小任何microbatch的完整logits；backward峰值可能增大 | 对完整长单样本也可能改变checkpoint持有量，但无pinned block实现/snapshot/容量验证，证据弱于本批singleton。须新的配置选择与测量授权；不能承诺2足够，也不自动追加两个改动 |
| 同8学生GPU改TP8/DP1，或者TP4/CP2/DP1 | TP8候选增加词表/参数分片；CP2候选减少每rank序列行数。两者重新组织已有8GPU，不增加样本预算，但通信/packing与数值顺序改变 | 都需要明确拓扑选择、新运行授权与D8/实际capacity测量；不是已验证方案。TP8先核验全部 head约束；`linear_attn_layout.py:50–54` 要求 GDN key heads能整除TP。CP2已有 `linear_attn.py:94–110,545–555` / `cp_utils.py:24–36` FLA路径，但 pinned dependency能力未验证，且 `cp_utils.py:87–105` 引入 gather/relayout临时量，不能保证总峰值减半 |
| C改更大显存硬件 | 不改算法/长度，直接增加可分配空间，但没有本次完整训练峰值测量，仍不能保证全流程容量 | D18只批准A/B H200，明确排除C；需新的C硬件/资源与restart授权 |
| response-only/chunked LM projection | 能针对本次失败直接减少完整 `[rows,V_local]` 输出；与已经存在的 logprob chunking不同 | 未找到本次任务可直接启用的既有配置；涉及 model输出、TP/SP/CP与policy-loss/backward contract，属于R6架构选择，需要单独设计和授权，不在本子任务实现 |

不推荐先降低 context/response、删长样本、改optimizer/parameter-backup、关闭margin、设置 `expandable_segments` 或直接套用 B retention修复。原生 `distribute_saved_activations` 也不能直接叠加：pinned `transformer_config.py:2457–2460` 明确禁止与当前 sequence_parallel=True并用；普通 CPU layer activation offload 与当前 recompute同样被 `:2419–2422` 拒绝。

授权边界由 `requirements.md:239–255`（D15/D16）与 `:265–271`（D18）拥有。D15/D16已使用的fresh run不授权下一次自动restart、额外optimizer probe或parameter sweep；D18不授权C H200。报告只提出选择，不创建新的预算授权。

## 5. 只读验证记录

环境：cwd `/data/ycfeng/sota-engine/miles`；本机 `python3` 为Python3.10.6；检查时HEAD=`9fb14ae2dc55da8ac7af9f4d9a99c5f891f089ce`。extraction receipt `evidence/score-schedule-source-exp-1107-170946-430400.json:1–8` 记录 worker Python3.12.16、MCore0.19.0+eb547f33e、torch2.14.1+cu130、TMS0.0.10；本子任务没有import或执行该worker runtime。

执行命令（无CUDA/platform访问、无文件写入）：

```bash
python3 -B - <<'PY'
import json, re
from pathlib import Path
base = Path('task_memory/task_2026-11-06_qwen35_three_pairs')
log = re.sub(r'\x1b\[[0-9;]*m', '', Path('/data/ycfeng/tmp/opencode-v2-tmp/opencode/C-exp-1107-150849-814926-complete.log').read_text())
assert 'schedules.py", line 790, in forward_backward_no_pipelining' in log
assert 'layers.py", line 514, in forward' in log and 'output = torch.matmul(total_input, weight.t())' in log
assert 'Tried to allocate 14.15 GiB' in log
versions = re.findall(r'event=WeightUpdateResultEvent[^\n]*?candidate_version=(\S+) published_version=(\S+)', log)
assert versions == [('0', '0'), ('0', '0')]
assert not re.findall(r'^.*op=train_step[^\n]*$', log, re.M)
final = json.loads((base / 'evidence/first-round/student/C/exp-1107-150849-814926/memory.json').read_text())['final_counters']
assert final['/sys/fs/cgroup/memory/memory.failcnt'] == '0'
assert 'oom_kill 0' in final['/sys/fs/cgroup/memory/memory.oom_control']
print('STATIC_EVIDENCE_PASS', versions, 'host_peak_GiB', int(final['/sys/fs/cgroup/memory/memory.max_usage_in_bytes']) / 2**30, 'host_limit_GiB', int(final['/sys/fs/cgroup/memory/memory.limit_in_bytes']) / 2**30)
PY
cmp /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937/core/pipeline_parallel/schedules.py /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-schedule-exp-1107-170946-430400/core/pipeline_parallel/schedules.py
```

预期/实际：exit0；`STATIC_EVIDENCE_PASS [('0', '0'), ('0', '0')] host_peak_GiB 408.7027702331543 host_limit_GiB 1500.0`；`cmp`无差异。**静态证据校验PASS；已运行C训练capacity FAIL；所有候选容量/修复验证INCOMPLETE。** 没有执行训练或CUDA回归。一次尝试检查本机 `/root/Megatron-LM` 被文件权限拒绝（EACCES）；没有重试、提权或访问worker。

## 6. Exact rollout0：已保存事实、CPU 重放与边界

输入 `/data/ycfeng/tmp/opencode-v2-tmp/opencode/C-exp-1107-150849-814926-rollout0.pt` 为父任务取回的 actual `rollout_data/0.pt`，文件20165513 bytes。本子任务没有重新获取远程内容。CPU reader Python3.12.13、torch2.11.0+cu130，与producer版本不同；`torch.load(map_location='cpu', weights_only=False)`只读此可信本地artifact。

**先检查实际 metadata：** root为`rollout_id=0, metadata={}, samples=[8 dicts]`。每条`train_metadata`只包含source UID/group/category、prompt/completion token counts及hash、sample index/group；没有partitions、micro_batch_indices或num_microbatches。所有`sample.rollout_id=None`，源码`train_data_conversion.py:121`使用sample.index作为rollout identity，得到0..7；lineage均为一source一output，remove_sample=False，multimodal_train_inputs=None，loss_mask=None。完整token长度与`prompt_token_count+completion_token_count`逐条相等。权威数字保留在JSON，未保存prompt/history全文或新的probe脚本。

**实际日志只确认counts：** `LOG:3777`记录`num_samples=8, num_rollouts=[8], num_microbatches=[3]`。没有本次实际消费的per-rank indices或CUDA shape dump。以下为**当前仓库源码的deterministic CPU重放**，不是从14.15 GiB反解，也不是worker-side张量capture。

重放输入来自`LOG:97,99,124–125,256,500,719,742–743,1006,1895–1896,1955`：DP2/CP1/TP4、无VPP、balance_data=True、balance_by_flops=False、dynamic=True、global_batch8、micro_batch1、max_tokens131072、THD、pad multiplier128、allgather_cp=False。`utils/dp_schedule.py:121–141`先FFD packing，`:164–178`再按token权重均衡分配；`seqlen_balancing.py:185–204`实现FFD。raw bins为`[[1],[0],[6],[7],[2,5],[4,3]]`，无需额外alignment splitting。

| CPU source replay | DP rank0样本批顺序 | DP rank1样本批顺序 | 每rank批数 | 最大原始/预测padded tokens |
| --- | --- | --- | --- | --- |
| 原dynamic | `[0] → [7] → [2,5]` | `[1] → [6] → [4,3]` | 3 | 130191 / 130560 |
| fixed singleton | `[0] → [2] → [3] → [6]` | `[1] → [4] → [5] → [7]` | 4 | 89570 / 89600 |

原dynamic最后两批分别130191/122073原始tokens、130560/122368预测padded tokens。预测只使用源码规则：`context_parallel.py:433–437`在CP1返回原序列，`data/rollout.py:227,277–298`串接后按`TP4 × 128 = 512`补齐，`model.py:502–504`传递实际padding参数。故可预测`input_ids=[1,T_padded]`；未执行GPU get_batch/output_layer，不断言具体失败GPU对应哪一个T，也不报告captured logits shape/dtype。

### fixed1 与 recompute2 的窄比较

- **本批优先考虑fixed1：** 两个最后批确实都为multi-sample source replay；singleton直接减少本次output rows。保留全部八个rollouts/600920完整tokens、global batch8和context131072，增加accumulation次数而非增加optimizer updates。最大padded rows减少40960（31.372549%），不等于总GPU峰值减少31.37%；参数/gradient常驻量、backward峰值与accumulation数值顺序仍需实际验收。
- **不能称为population/context保证：** fixed1仍允许一个完整131072-token样本；512对齐后上界仍是131072，与原token-cap packing最坏上界相同。只重放了rollout0，未测全population、后续100 updates、长单样本或optimizer lazy allocation，不能以首批较短证明全部容量。
- **recompute2作用不同：** pinned `core/transformer/transformer_config.py:680–703`定义full/uniform按layers分组，runtime `LOG:901,1016`为64 layers/group1。group2按该语义减半组数，但只是checkpoint-boundary数量推断，不是保存tensor/GiB实测；可能增加两层backward recomputation内部峰值。packed output rows原封不动，对同一失败分配的收益间接，当前证据不足以优先于本批singleton或保证full-context可行。
- **配置owner边界：** `data/rollout.py:484–490`优先使用rollout-side schedule。现有static支持已由实际`build_dp_schedule`重放证实；`args/configs/data.py:187–207`定义dynamic=False默认，`backend_fields.py:48–49`说明dynamic时忽略micro_batch_size。实际C `launch.json:94–104`显式dynamic/group1；`tests/manual/agent_opd/run_qwen35_opd.py:204–205`共同launcher仍无条件生成两项。将其改为C的static或group2需要获准的launch选择/实现，不能靠仅设置一个已为1的trainer参数生效，也不能改变A/B已验收recipe。

### 可复现的 CPU 校验命令

以下命令实际执行，cwd为仓库根；不写artifact，不初始化GPU，不执行model或optimizer。所需geometry JSON由本报告更新时通过patch工具写入。初次metadata检查同一环境下只打印root/sample keys、lineage和train_metadata；没有访问CUDA。schedule模块import输出`deep_ep is not installed`警告，CPU重放与断言均完成，非训练能力验证。

```bash
timeout 60s env PYTHONPATH=/data/ycfeng/sota-engine/miles PYTHONNOUSERSITE=1 OMP_NUM_THREADS=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import json, torch
from types import SimpleNamespace
from pathlib import Path
from miles.utils.dp_schedule import build_dp_schedule, TrainParallelConfig
p='/data/ycfeng/tmp/opencode-v2-tmp/opencode/C-exp-1107-150849-814926-rollout0.pt'
d=torch.load(p,map_location='cpu',weights_only=False); samples=d['samples']
assert d['rollout_id']==0 and d['metadata']=={}
assert [s['index'] for s in samples]==list(range(8))
lengths=[len(s['tokens']) for s in samples]
assert lengths==[88244,89570,66714,60010,62063,63477,85708,85134]
for s in samples:
    m=s['train_metadata']
    assert m['prompt_token_count']+m['completion_token_count']==len(s['tokens'])
    assert m['completion_token_count']==s['response_length']
    assert s['lineage']==dict(source_sample_index=s['index'],output_index=0,output_count=1)
    assert not s['remove_sample'] and s['multimodal_train_inputs'] is None
    assert not any(k in m for k in ('micro_batch_indices','partitions','num_microbatches'))
rids=[s['rollout_id'] if s['rollout_id'] is not None else s['index'] for s in samples]
a=SimpleNamespace(use_dynamic_batch_size=True,max_tokens_per_gpu=131072,micro_batch_size=1,allow_partial_train_step=False,balance_by_flops=False,balance_data=True)
t=TrainParallelConfig(dp_size=2,cp_size=1,vpp_size=None,microbatch_group_size_per_vp_stage=None,independent_dp=False,supports_precomputed_schedule=True)
e=json.loads(Path('task_memory/task_2026-11-06_qwen35_three_pairs/evidence/C-first-batch-geometry.json').read_text())
for mode in ('dynamic','fixed_singleton'):
    a.use_dynamic_batch_size=mode=='dynamic'
    sc=build_dp_schedule(a,t,lengths,global_batch_size=8,rollout_indices=rids)
    assert sc._asdict()==e['replay'][mode]['schedule']
    rows=[]
    for rank,mbs in enumerate(sc.micro_batch_indices):
        local=[]
        for ids in mbs:
            g=[sc.partitions[rank][i] for i in ids]; n=sum(lengths[i] for i in g)
            local.append(dict(sample_indices=g,full_tokens=n,thd_padded_tokens_source_prediction=(n+511)//512*512))
        rows.append(local)
    assert rows==e['replay'][mode]['microbatches_by_dp_rank']
    assert sorted(i for r in rows for mb in r for i in mb['sample_indices'])==list(range(8))
    assert max(mb['thd_padded_tokens_source_prediction'] for r in rows for mb in r)==e['replay'][mode]['max_padded_tokens']
assert sum(lengths)==600920 and 1-89600/130560==e['comparison']['max_padded_tokens_reduction']
print('CPU_GEOMETRY_ARTIFACT_REPLAY_PASS',600920,130560,89600,e['comparison']['max_padded_tokens_reduction'])
PY
```

预期与实际：exit0，`CPU_GEOMETRY_ARTIFACT_REPLAY_PASS 600920 130560 89600 0.3137254901960784`。**CPU artifact/source replay PASS；captured failing CUDA shape、fixed1 capacity、recompute2 capacity均UNVERIFIED。** 未新增persistent probe machinery。

## 7. 阶段自检

### 1. 规划完成情况

汇总：PASS3｜BLOCKED1｜TODO1。

| 子任务 | 状态 | 依据 |
| --- | --- | --- |
| 本子任务的本地phase/source诊断 | PASS | 已定位终止train栈，区分已启用机制和缺失measurement |
| 本子任务的静态证据检查及exact geometry CPU重放 | PASS | 上述命令exit0，不冒充GPU验证 |
| 父任务C zero-update/actual baseline链 | PASS | C failure report owns完整native events及pinned inspector结果 |
| 父任务P3-C正式完成 | BLOCKED | plan.md:57明确capacity/restart decision阻塞；本次attempt仍FAIL |
| 父任务容量选择/新授权提案 | TODO | 明确first-batch singleton收益及full-context未验证边界 |

### 2. 偏离检测

结论：本子任务未偏移；窗口为上次诊断交付后的明确CPU geometry follow-up，前沿为交付replay证据和有边界的fixed1/recompute2建议。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1工具打磨 | CLEAR | 直接CPU artifact/source replay，无新harness |
| D2重复修复 | CLEAR | 未实施修复/重启；一次config路径错误已按实际glob纠正 |
| D3支线修补 | CLEAR | 所有检查服务明确requested geometry对比 |
| D4并行停滞 | CLEAR | 无delegation；父任务独立平台/inspector结果不重复采集 |
| D5超范围扩展 | CLEAR | 只写授权report/compact JSON |
| D6分析空转 | CLEAR | 新exact artifact推进geometry结论，交付后停止扩展 |
| D7路线违背 | CLEAR | 保留D15/D16/D18，无额外GPU动作 |

文档检查：当前`plan.md:57,72`已由父任务修正为C failed/capacity decision blocked，原S5关闭。S1–S6均未发现本子任务范围内的新缺陷；无tickets。归因：无。

### 3. 纠正建议

分支A：当前spec/plan合理，无需修改。

需停止的偏离行为：无。本子任务只更新自身证据，不改父任务plan/requirements。

下一步：父任务汇总已完成geometry/update链 → 提出fixed1为本批首选、明确full-context与group2未验证边界 → 获得必要的新配置/measurement/restart授权后才执行。已有A/B完成记录不受此optional调查阻塞。

### 4. 最值得关注的3点

1. 故障已从旧host OOM转为训练LM output allocation OOM，不能沿用旧原因。
2. fixed1确实降低本批source replay的packed rows；不保证131072单样本或完整population容量，59.05 GiB持有者仍缺measurement。
3. 不得自动再重启C或追加optimizer probe；C不在D18 H200授权内。
