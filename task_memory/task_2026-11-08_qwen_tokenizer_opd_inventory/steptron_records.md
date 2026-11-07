# Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | 完成 Steptron 本地 refs、固定提交配置继承、数据/tokenizer 和已记录 OPD/MOPD 结果的只读调查。 |

# Steptron Qwen OPD/MOPD 记录调查

Task ID: `QWEN-TOKENIZER-T3-STEPTRON`。源码仓库：`/data/ycfeng/steptron`。本文中的云路径来自已经保存到 Git 的配置或实验凭证；本次没有访问云存储或平台，没有训练、提交作业、SSH、fetch、checkout、切换分支、修改源码或提交 Git。

## 1. 结论

1. **存在 Qwen 系列的真实 OPD/MOPD 实验记录，且部分记录有完整数据路径、tokenizer/template 和测量结果。** 不能把它们全部称为 Qwen3.5：至少要区分 DeepSeek-R1-Distill-Qwen-1.5B 的 Qwen2.x/Qwen2.5 衍生模型、Qwen3-8B、Qwen3-30B-A3B 和当前 Qwen3.5。
2. **当前三对 Qwen3.5 在 Steptron 中也有直接对应记录**：`qwen35-opd-h200` 的 c1=4B/27B、c2=4B/35B-A3B、c3=27B/397B-A17B。c1/c2 有已完成 optimizer updates、HF5、sample audit；c3 有大量真实失败/诊断记录，但所读最新固定快照**不能证明 c3 已完成 OPD optimizer update**，更不能证明三对正式跑完或有最终效果评估。
3. Qwen3.5 这组继承的是 `ys/golden/qwen3_8b_fullyasync_baseline/exp.py` 的 **9 组、55 个 raw conversation JSON、记录共 482,359 条**。训练前用本组的 Qwen3.5 tokenizer 重新编码，不是直接加载一个名为 Qwen 的预打包 token-ID 数据集。完整 55 路径已在该任务的 `evidence/default_data_manifest.json` 中。
4. **名称命中不足以证明 tokenizer 兼容或 Qwen 实验。** 例如 jxr 的部分 Step3p5air MOPD 仅数据文件名含 `qwen3_8b`，实际学生/教师是 Step4air；Qwen3 的 mainline wrapper 也不是当前 Qwen3.5 wrapper。历史 raw JSON/Parquet 可作为重新编码的来源，但历史 packed IDs/缓存目标不可据此直接复用。
5. 比较完整、可借鉴的历史记录有：2026-09-23 的 R1-Distill-Qwen-1.5B 单教师 MOPD（H800/H200 各 200 steps 与数学评估）；2026-09-24 的 Qwen3-30B-A3B 双教师 MOPD（STEM/SWE slices 与实际运行记录）；2026-10-02 的 Qwen3 medium 单领域 replay（DAPO/DeepScaleR/WebInstruct/SWE、资产兼容凭证、smoke 与未完成正式运行记录）。它们的 tokenizer 不因此与当前 Qwen3.5 相同。

## 2. refs 范围、固定快照与新鲜度

`git for-each-ref refs/heads refs/remotes` 枚举了 **8,387 个 refs：52 local heads、8,335 remote-tracking refs**；名字含 `qwen` 的 155 个，含 `opd`（包括 `mopd`）的 99 个，两类可重叠。另读取 `git worktree list --porcelain`、重点分支树、与 Qwen+OPD/MOPD 相关的 commit messages 和本地 `task_memory`。没有逐文件读取全部 8,335 个远端跟踪分支，以下是决定主要结论的 refs；相同继承链的 replay/control branches 不重复算作独立模型实验。

日期是 commit committer date，不是 remote 抓取日期。`origin/master` 固定在 `f9de82919cf9551b2771526b7c187328ce9d7637`，日期 `2026-11-06T09:04:33+00:00`。本次未做 `ls-remote`/fetch，因此不能保证服务器当前 refs 与本地跟踪 refs 完全相同。当前主 checkout HEAD 始终读取为 `1e588c90ac7b5b29c454c668e93f2fe2d4d69fe4`。

| ref（本地或 remote-tracking） | 固定 commit | committer 日期 | 与本题的关系 |
| --- | --- | --- | --- |
| `qwen35-opd-h200` | `b48739f615e9a933003859f7a948398320774af5` | 2026-11-08 01:21:10 +08 | 当前三对 Qwen3.5、数据清单、真实运行/诊断凭证 |
| `yc-step` | `1e588c90ac7b5b29c454c668e93f2fe2d4d69fe4` | 2026-10-08 20:41:33 +00 | R1-Distill、Qwen3 medium 和历史 MOPD task records |
| `yc-mopd-learning-dynamics` | `c573ce27106718e7222591d22a90eb285b4431f0` | 2026-09-26 19:29:40 +08 | 学习/反馈 bank 后续分支；不等于新的 tokenizer 家族 |
| `medium-replay-v1` | `6cd5b785736db931348f2f4fd8bf059ceb606703` | 2026-10-14 01:58:52 +08 | Qwen3 medium 单教师 replay；资产与 source receipts |
| `github/medium-replay-v1` | `8845fd147198580c778e5258f37a27ad0da9c2a7` | 2026-10-12 17:52:46 +08 | 比本地 medium ref 旧，不能代替本地最终记录 |
| `origin/ssj/opd-dev` | `408af136836af8888a59bac89b63d42dfb8fb2e8` | 2026-01-10 11:13:24 +08 | Qwen3-8B OPD、self-distill 与三专家 MOPD 配置 |
| `origin/ssj/opd-0213` | `50635a910d4aae07a05cb814ddb1ee43a856c128` | 2026-04-21 18:58:28 +08 | 后续 OPD configs；不从 ref 名推断执行结果 |
| `origin/ssj/opd-mr` | `72b6f1d6bbff8eb5e29b5c1d5d1b5a1e59dca6ca` | 2026-02-12 14:33:22 +08 | OPD 继承/重构覆盖 |
| `origin/ssj/fully-aysnc-mopd` | `24fe7faf1ba219610cbb8713982b0e63d3f9e5ca` | 2026-03-23 13:33:45 +08 | 含 Step3p5air MOPD；不能因数据名 Qwen 判为 Qwen 学生 |
| `origin/jxr/mopd-260202` | `7fac9dad0a959d01d32f8b95399cd9d2ce0eea79` | 2026-02-02 16:47:17 +08 | Step3p5air/Step4air 主体，作为误命中对照 |
| `origin/jxr/mopd-dev-260202` | `f4b309102c9d4e6e6b72ba77ee08313c2e28651f` | 2026-02-09 23:13:32 +08 | 实际模型/teacher/data inheritance 检查 |
| `origin/yasmine-opd-dev` | `96869a273d4c84afa45a97620121d9a63a1aa8fc` | 2025-12-27 22:59:30 +08 | zym Qwen3-8B OPD 路径可见 |
| `origin/yasmine-fullyasync-opd-dev` | `912bc143f5a3aa21b2d183ddfcc654f84a1abe4f` | 2026-04-28 11:49:33 +08 | fully-async OPD 基线后续 |
| `origin/yasmine-opd-dev-0710` | `e739e9928140b2c3fa17fd02787c45c869237e99` | 2026-07-13 15:52:55 +08 | MOPD timing 文档分支 |
| `origin/wangheng-qwen-distill` | `1c0fab858e0384cfc22e4093e912c0076e895d75` | 2025-02-20 15:20:36 +08 | commit 为 `qwen sft`；distill 名不证明 OPD/MOPD |
| `origin/qwen2p5_32b_rl` | `a8c885abc612690827a3735673612e98a729f66f` | 2025-11-06 14:28:49 +08 | Qwen2.5-32B PPO/RL configs，未取得独立 OPD 结果证据 |
| `origin/zq/qwen2p5` | `c45c6a2e515a506ca6bae8141a15693abccbd98c` | 2025-07-10 00:39:41 +08 | Qwen2.5 模型/并行变体；不据名称归为 OPD |
| `origin/codex/qwen35-grounding-distill-20260402` | `11da526c685795ef0cf5b114f019d5fbd1992a5f` | 2026-04-02 22:52:42 +08 | grounding reward/distill 调查，非当前三对的 OPD 结果 |
| `origin/mrh/qwen35-writer` | `ae11591a11782f4258a2c3c36b5114c554f74661` | 2026-08-27 13:28:50 +08 | context-memory/writer/SFT/holdout 工作，不当作同题 OPD |
| `origin/qww/qwen3p5-posttrain-32gpu-gbs128` | `438a28c439a70dcb3587e55646236d2b50d28d06` | 2026-09-23 16:00:36 +08 | Qwen3.5 CP8 posttrain，不等于 OPD/MOPD |
| `origin/zhuchenglin/qwen3p5-35a3-port` | `43c7d755878d6ca76462b3b7fafd0b043139981f` | 2026-10-09 19:15:08 +08 | omni midtrain/posttrain/port |
| `origin/qww/zhuchenglin/qwen3p5-35a3-port-opt` | `5ba1d2b32f4fe024911c43ccba911c088ab15740` | 2026-10-10 22:19:45 +08 | omni prefetch 变更，与本题 OPD 结果不同 |

调查过程中 `qwen35-opd-h200` 被其他进行中的工作从初读 `8f237bc46773ee813ca8151b7718bf89e1340fb3` 推进到上表 `b48739f...`；本次读了两者 diff 和后者凭证，以下 Qwen3.5 结论一律钉在后者，不以可变 branch HEAD 作为唯一引用。

## 3. Qwen3.5：当前三对的直接记录

以下路径均位于 **`b48739f615e9a933003859f7a948398320774af5`**。

### 模型、数据、tokenizer 与模式

- `playground/users/ycfeng/qwen35_opd/exp.py:55-85` 明确定义 c1/c2/c3；与父任务 A/B/C 模型角色一致。c1 teacher 从 27B HF 源加载；c2 teacher native input 是 `/mnt/codesign-exp/ycfeng/qwen35-opd-h200/teacher-inputs/35b-tp1-pp1-ep1-1106a`；c3 是 `/mnt/codesign-exp/ycfeng/qwen35-opd-h200/teacher-inputs/397b-tp1-pp8-ep1-1107b`。模型原始 HF 路径由 `probe_models.py::MODELS` 引用。native conversion inputs 不是另一种 tokenizer。
- `exp.py:255-274` 的 `DataConfig(golden.DataConfig)` 使用 golden 数据与 template，再把生成的 `generation_prompt` token IDs 发给 student rollout；teacher 与 actor 对实际相同轨迹 token positions 评分。
- 完整来源清单：`task_memory/task_2026-11-06_qwen35_opd_h200/evidence/default_data_manifest.json`，来源 `playground/users/ys/golden/qwen3_8b_fullyasync_baseline/exp.py`。
- 9 组 `(weight, files)`：`(1.0,16),(1.0,12),(0.5,5),(0.15,13),(0.15,4),(0.05,1),(0.15,2),(0.1,1),(0.1,1)`。来源覆盖 hard math、hard code、STEM/science、其他推理与 IFTrain；精确成员以 manifest 为准，不能把它简称为完整 DAPO 或完整 Math166k。
- 逐文件凭证：同目录 `evidence/default_data_inventory.json`，55 文件全部 `status=PASS`，`samples` 求和 **482,359**，记录 role sequences 与 bytes。示例完整路径：
  - `/mnt/step2-alignment-jfs/hujingcheng/datasets/step3_main_ppo/hard_data_0701/hujingcheng_datasets_orz_math166k_cleaned_dedup_hard_7k_0228_hard_4k.json`
  - `/mnt/step2-alignment-jfs/hujingcheng/datasets/step3_main_ppo/hard_data_0701/hujingcheng_datasets_orz_dapo17k_cleaned_hard_932.json`
  - 其余完整路径直接见该固定 commit 的 manifest，无需推测云目录。
- `exp.py:89-100`：`StudentTokenizer(HFCompatTokenizer)`，`hf_path=TOKENIZER_PATH`，其来源是 worktree `.runtime/tokenizer`；不是 `Qwen3MainlineVLLMMultiTurnTokenizer`。`prepare_tokenizer.py:1-24` 从实际 HF tokenizer 保存本地 assets，并把 history reasoning 分支改为 **`preserve_thinking | default(true)`**，即默认保留旧 turn reasoning。这是一项 template policy 修改，不能把“同 Qwen3.5 vocab”误写成“原生模板字节未改”。源中没有独立 teacher chat-template 替换轨迹的路径。
- `exp.py:283-312`：fully-async；pure OPD `coefficient_opd_advantages=0`；reward function off；reference/actor scoring on；额外 KL penalty/loss 都为 0；skip advantage normalization；sample/token TIS，其中 token range `[0.5,2.0]`；global token-mean loss；GBS256、1 sample/prompt、30 steps 目标。inference T=1、top-p=1。这是 **sampled-token OPD advantage 路径**，不是 full-vocab KL/top-k KD。

### 执行与结果证据

记录目录：`task_memory/task_2026-11-06_qwen35_opd_h200/`。

- c1/c2 `test_report_2026-11-07_opd_runtime.md`、`test_report_2026-11-07_formal_window_c3_memory.md`、`evidence/formal_scalars_20261108_0107.json`、`evidence/formal_sample_audit_20261108_0113.json` 是实际运行凭证，不只是可运行 config。
- 最新 scalar snapshot 对 c1 已记录 optimizer step **0..6**、c2 **0..7**；sample audit 对应 7/8 个 iterations，每 step 256 samples/256 unique IDs、历史 iteration 重复 ID 计数均为 0，并有保存路径。c2 另有 D05/HF5 对照。本文不把 sample IDs 不重复解释成全数据集没有语义重复。
- c3 的 `evidence/c3_memory_pair_results_20261108.json` 明确 scope 为：**matched frozen-reference diagnostic on all retained rollouts; no training, weight sync or D05 acceptance**。`test_report_2026-11-08_c3_qualification.md`、OOM/RDMA/offload/load-payload receipts 表明实际尝试过，但不能拿 reference-forward PASS 代替完整 OPD update PASS。
- 没有把这份 snapshot 认作 30-step 正式终态或 benchmark accuracy improvement；ongoing 状态以原任务后续记录为准，本调查不查询 live jobs。

## 4. Qwen3-8B：较早的 OPD/MOPD 配置与精确来源

以下路径钉在 **`408af136836af8888a59bac89b63d42dfb8fb2e8`**，其中 zym 的 OPD 两个入口也存在于 `origin/yasmine-opd-dev@96869a273d4c84afa45a97620121d9a63a1aa8fc`。

### 单教师 OPD（有配置；本次未取得独立终态/效果报告）

入口：

`playground/users/ssj/opd_baseline/zym_version/stu_qwen3_8b_1208_s2_tea_math_exp_lt0p5_it200_plr2e6_yarn_opd_skip_adv_norm_onpolicy_stepcloud_judger_new_opd_0102.py`

- `:960-966` 学生 `/mnt/step2-alignment-jfs/hujingcheng/checkpoints/steptron-sft/qwen3_8b_sft1013_sft_d1205_ds_0p05_g32_1208_rerun/it4200`；teacher `/mnt/step2-alignment-jfs/hujingcheng/checkpoints/steptron-ppo/qwen3_8b_mainrecipe1129_s2ds5_s64k_64x16_g64_vllm_plr5e6_yarn_partial_rollout_new_filter_lt0p5_math_1220/it200/actor`。
- `:573-635` 数据 recipe 是 raw JSON，经 `MinDataset -> SimpleDataLoader -> TokenizerTemplate` 编码。数学主组来自 `/mnt/step2-alignment-jfs/shangshijie/datasets/math_expert_prepare/keep_any_acc_lt_0p5_1220/` 的 6 个固定 JSON（竞赛数学、math173、DAPO17k、Math166k hard/hardest、shuzhimi），另有 large-number-multiplication source。
- 可直接核查的 DAPO 路径：`/mnt/step2-alignment-jfs/shangshijie/datasets/math_expert_prepare/keep_any_acc_lt_0p5_1220/hujingcheng_datasets_orz_dapo17k_cleaned_17k_17k_17k_731.json`。完整 recipe 就在上面固定入口的 `DataConfig`，不是外部未找到的 packed manifest。
- `:277-294` training tokenizer 是 `Qwen3MainlineVLLMMultiTurnTokenizer`，vLLM tokenizer 也是该 class 的 `hf_path`；T=1、top-p=1、模型 padded vocab 151936。`TokenizerTemplate` 用 `apply_chat_template(conversation_data[:-1], tokenize=True, add_generation_prompt=True)`，未显式指定 `enable_thinking`。
- OPD advantage 是 `teacher_logprob - student_logprob`；reward advantage coefficient=0，额外 KL loss/penalty=0。`Exp.__init__` 将 class 默认的 `skip_forward_actor=True` 改成 **False**，不能只读基类默认就称其使用旧 sampling logprobs。

对照入口 `playground/users/zym/qwen/opd/qwen3_8b_mainrecipe1013_s2ds5_s64k_64x16_g64_vllm_plr5e6_yarn_stepcloud_judger_new_opd.py` 的默认 `coefficient_opd_advantages=0.5`，最终 advantage 为 `opd_advantage + 0.5*reward_advantage`；另有同起点 actor/reference 的 self-distill 配置。它们并非都属于 pure OPD，也不能把 config 文件名中的 `it200` 当作本次取得的运行结果。

### 三专家 MOPD（有完整配置；未取得独立结果报告）

入口：

`playground/users/jxr/opd/qwen3_8b_sft1208s2_MSL_vllm_plr1e5_yarn_mopd_self_distill_stepcast_partial_rollout_fix_rope_warmup_10it_rl_data_260102.py`

- `DomainConfig:107-165` 明确 3 域与 teacher：math **16 JSON，weight=1**；science **5 JSON，weight=1**；logic **1 JSON，weight=0.5**。完整 22 路径在该类内。
- math teacher `/mnt/step2-alignment-jfs/hujingcheng/checkpoints/steptron-ppo/qwen3_8b_mainrecipe1129_s2ds5_s64k_64x16_g64_vllm_plr5e6_yarn_partial_rollout_math_1212/it50/actor`；science teacher `/mnt/step2-alignment-jfs/hujingcheng/checkpoints/steptron-sft/qwen3_8b_sft1013_sft_d1114_ds_0p05_g32_1219/it1118`；logic teacher `/mnt/step2-alignment-jfs/hujingcheng/checkpoints/steptron-ppo/qwen3_8b_onpolicyppo_mainrecipe0826_0828_ifdata/it900/actor_hf`。
- logic 数据为 `/mnt/step2-alignment-jfs/zhaoqian/data/release/rl/IFTrain/iftrain_only_ifeval_no_repeat_prompt_17393.json`。math 含 Math166k hard/hardest、DAPO、BigMath/DeepMath/OpenR1/OT/LIMO/s1k、OMR 等衍生；science 含 chemistry、college math、GPQA MegaScience 与 SciBench 衍生。文件名已带 filtering/count 信息，不等于公开原始数据集完整 split。
- student 从同一 1208 Qwen3-8B SFT `it4200` 初始化。教师经 stepcast 返回各域 token logprobs；代码说明要求 **same tokenizer，不做 tokenizer translation**；advantage=-reverse-KL，critic off，importance-sampling loss。
- tokenizer 同 `Qwen3MainlineVLLMMultiTurnTokenizer`；prompt 保留对话 prefix，template wrapper 注释声明仅保留 latest user turn 之后的 reasoning。

### old wrapper 的精确 asset 来源

`steptron/tokenizer/qwen_tokenizers.py:17-70` 区分 `Qwen2p5Tokenizer -> Qwen2.5_Instruct`、`PublicQwen3Tokenizer -> Qwen3`、`Qwen3Tokenizer -> Qwen3Internal`、`Qwen3MainlineVLLMTokenizer -> Qwen3MainlineVLLM`、`Qwen3MainlineVLLMMultiTurnTokenizer -> Qwen3MainlineVLLMMultiTurn`。不能把这些 class 合并成一个“Qwen tokenizer”。

`steptron/huggingface/hf_tokenizers.py` 的 folder mapping 是仓库 `third_party/steptokenizer/tokenizers/<folder-name>`。此固定提交的 submodule gitlink 为 **`6786e77df20077e065558d86577cd02266877ce5`**。所以这组 wrapper 的仓库内 asset 路径精确为 `third_party/steptokenizer/tokenizers/Qwen3MainlineVLLMMultiTurn`；本次没有重新加载该 submodule assets 或验证其与 Qwen3.5 的字节/token mapping 相同。该 gitlink 来自 `git ls-tree`；它不是 superproject object database 中可直接 `cat-file` 的对象，未因此做 submodule update/fetch。

## 5. Qwen2.x/Qwen2.5 衍生 1.5B：真实测试及成功结果

以下均在 **`1e588c90ac7b5b29c454c668e93f2fe2d4d69fe4`**。模型名是 **DeepSeek-R1-Distill-Qwen-1.5B**，实现采用 `Qwen2Model`；不要称它为 Qwen3/Qwen3.5，也不要与普通 Qwen2.5-Instruct tokenizer 混同。

### 2026-09-10：real weights MOPD 的初次失败记录

- Config：`ci_tests/optional_exp/mopd_real_weights/qwen1p5b_mopd.py`。
- 模型/teacher 同起点：`/data/ycfeng/steptron/task_memory/task_2026-09-10_mopd_real_weights/models/DeepSeek-R1-Distill-Qwen-1.5B`；tokenizer 是该目录的 `HFCompatTokenizer`。
- 原数据：任务目录 `data/gsm8k/main/train-00000-of-00001.parquet`（GSM8K train=7473）与 `data/arc/ARC-Easy/train-00000-of-00001.parquet`（ARC-Easy train=2251）。`tests/e2e/mopd_real_weights/prepare_data.py` 取每域 16 real records、保留 provenance/ground truth，转成 raw `data/math.json`、`data/science.json`，runtime 再编码。
- `task_memory/task_2026-09-10_mopd_real_weights/test_report_2026-09-10_assets.md` 只证明下载/权重完整/局部编码，明确 GPU training 尚待验证；`h200_first_run_evidence.md` 则有真实 RJob `exp-0911-011447-680532`、H200、worker Python 3.10.12、actor/reference all keys matched、critic backbone loaded，随后 **`KeyError: -1`，business FAIL before rollout**。
- 对应早期定位 commit：`3aad5ae67992e8e55e28ee2ad75bfd22025fee0c`（2026-09-11 01:20:49 +08）修 data/tokenizer padding contracts。此记录不能叫完成训练的 MOPD 效果测试。

### 2026-09-23：单教师数学 MOPD，200-step 与评估记录

- Config：`playground/users/ycfeng/MOPD/r1distill1p5b_mopd_math_fullyasync_tis_no_kl.py`。
- student `/mnt/codesign-exp/ycfeng/opd-assets/oneshot-r1distill1p5b/student` = DeepSeek-R1-Distill-Qwen-1.5B；teacher `/mnt/codesign-exp/ycfeng/opd-assets/oneshot-r1distill1p5b/teacher` = JustRL-DeepSeek-1.5B。tokenizer `StudentTokenizer(HFCompatTokenizer)` 直接用 student asset。
- runtime dataset `/mnt/codesign-exp/ycfeng/steptron/task_2026-09-23_mopd_r1distill1p5b_math_disagg/data/math_slice.json`，600-item raw conversation slice。
- 精确原文件由 `task_memory/task_2026-09-23_mopd_r1distill1p5b_math_disagg/stage_probe.py:23-27` 指定：

  `/mnt/posttrain/liujunfeng/tmp/chat_template_adapt/text_0616_all_domains_v1/remaining/interleaved/science/mnt/posttrain/liujunfeng/data/sft/0512_hle_math_filter/mnt/posttrain/yuangpeng/data/codes/step-agents-python/runs/kimi-k2.6/math_collect11k_dsv4pro_gte_acc0p5/no_tools/trajectories_correct_0511/sft_data_list_0.json`

  路径中有 `science` 不改变其实际数学样本用途；也不能因为 student 名 R1，就把该数据说成 DAPO/GSM8K。
- `StudentTokenizerTemplate` 用 student chat template，raw messages 在 runtime 编码；fully-async、critic off、TIS、额外 KL loss/penalty=0、pure OPD；训练 T=1/top-p=1。评估使用另一套固定 yardstick：avg@16、T=0.7、top-p=0.9、31744 response cap、EOS-only stop。
- `docs/agents/15-mopd-stepcast-dense-disagg.md:3,96-102` 与原任务的 `summary.md`/test reports 记录 H200/H800 **各 200 steps**。保存的测量：H800 macro 数学分数 **+9.40 percentage points [6.56,12.50]**；H200 **+8.73 pp [6.20,11.49]**，约 step100 后趋平。这是 archived measured result；本次没有重跑或读取其 cloud checkpoints。
- 文件名 MOPD 此处实际上是 **one teacher**，不代表多教师混合；这一点配置 docstring 明确写出。

## 6. Qwen3-30B-A3B medium：数据、教师模板与已有运行

### 2026-09-24 双教师 MOPD

固定在 **`1e588c90ac7b5b29c454c668e93f2fe2d4d69fe4`**。

Config：`playground/users/ycfeng/MOPD/qwen3_30b_a3b_mopd_turn_2experts_fullyasync_tis_no_kl_smalldata.py`；记录：`task_memory/task_2026-09-24_mopd_medium_step3_2teacher/`。

- model assets root：`/mnt/codesign-exp/ycfeng/steptron/task_2026-09-24_mopd_medium_step3_2teacher/models/`。
- student `Qwen3-30B-A3B-Instruct-2507@0d7cf239`；STEM teacher `Qwen3-30B-A3B-Thinking-2507@144afc2f`；SWE teacher `Qwen3-Coder-30B-A3B-Instruct@b2cff646`。checksum manifests 在记录目录 `analysis/checksums/`。
- raw slices 来自 `/mnt/codesign-exp/ycfeng/steptron/task_2026-09-24_step3p6_mopd_2teacher_smalldata/data/stem_slice.json` 和 `.../data/swe_slice.json`。`analysis/slice_stats.json` 明确指向这两个输入；上游 task `analysis/probe/slice_stats.json` 记录 7 个 STEM source 精确路径。SWE 的原 11 JSON 列在 `playground/users/wyx/MOPD/step3p6_mopd_turn_5experts_fullyasync_tis_no_kl_0710_h200.py:59-71`：目录 `/mnt/posttrain/hanqi/data/swe/distill_ablation_0623/`，`glm5.2_distill_0_include_unresolved_part0000..0004.json`、`glm5.2_distill_1_include_unresolved_part0000..0005.json`。
- `:152-171` training tokenizer `StudentTokenizer(HFCompatTokenizer)` 从 student 加载；模型/training padded vocab=151936。vLLM chat-completion tokenizer path 却配置为 **STEM teacher**，因为 token-ID rollout 不依赖 server chat rendering，held-out chat eval 用 STEM template。不能仅从 server tokenizer path 判定 train prompt template。
- `:490-499` 明确 `PROMPT_TEMPLATE_SOURCES={stem:TEACHER_STEM,swe:TEACHER_SWE}`，各域使用对应 teacher 的 HF `chat_template` 渲染、用 shared token vocabulary 编码。它与下面 10 月 replay 的“冻结 student template”策略不同。
- 记录保留 raw assistant-turn prefix/metadata，在运行时做角色规范化、tool-call arguments adaptation 与编码，不是拿 Step4 的旧 packed IDs 直接喂 Qwen3。
- `progress.md:51-58,289-336`、`analysis/slice_stats.json`、`analysis/checksums/*`、阶段 `test_report_*.md` 有真实 staging、smoke 和评估工作记录：STEM 633/633 assistant turns kept，SWE 814/848 kept（原 Step3p6 tokenizer 下为 738）；smoke f 两 steps 完成训练但 teardown watchdog 导致 job Failed；`exp-0926-151216-342799` 的 HF workflow check 为 `E2E_CHECK PASS`。
- `progress.md:56` 的 step0/teacher-stem 保存评估分别为 macro **0.737 / 0.886**（step0 strict 0.0，有后续 parser rescore），不能称为学生训练提升。该 pin 的 S5 记录曾被停止/改成 S5-20，**本文未据此确认完整 20-step 正式训练终态**。源码还包含后续 50-step config，不能仅从当前 `train_iters` 反推某一历史 run 的合同。对最终跨域效果，应按原 task 的具体 run/eval report 引用。

### 2026-10-02 单领域 replay：更完整的公开源路径与 token compatibility receipt

固定在 **`6cd5b785736db931348f2f4fd8bf059ceb606703`**。记录根 `task_memory/task_2026-10-02_h800_medium_singleteacher_bounded_replay/`。

`preparation_inputs.json` 与 `artifacts/readiness/assets-inputs-1002a.json` 记录：

| 域 | dataset/source | 精确路径 |
| --- | --- | --- |
| Math | DAPO | `/mnt/codesign-exp/ycfeng/steptron/task_2026-09-26_mopd_learning_dynamics/data/raw/math/DAPO/train.parquet` |
| Math | agentica-org/DeepScaleR-Preview-Dataset | `/mnt/codesign-exp/ycfeng/steptron/task_2026-09-24_mopd_medium_step3_2teacher/data/agentica-org/DeepScaleR-Preview-Dataset/deepscaler.json` |
| STEM | TIGER-Lab/WebInstruct-verified | `/mnt/codesign-exp/ycfeng/steptron/task_2026-09-24_mopd_medium_step3_2teacher/data/TIGER-Lab/WebInstruct-verified/data/train-00000-of-00001.parquet` |
| SWE | GLM5.2 trajectories，11 files | `/mnt/posttrain/hanqi/data/swe/distill_ablation_0623/glm5.2_distill_{0,1}_include_unresolved_partNNNN.json`；0 有 0000..0004，1 有 0000..0005；`preparation_inputs.json` 展开全部路径 |

原始来源都是 text/messages，Math/STEM 使用去掉答案的 question prompt，SWE 使用完整 assistant-turn prefix；新 query pools/probes/缓存轨迹有额外固定 tokenizer/template 合同，不能当作原 raw corpus 等价替换。

四角色模型是在上节 assets root 下的 student、STEM、SWE，加 Math teacher `PromptCoT-2.0-SelfPlay-30B-A3B@ff191c76`（repo `xl-zhao/PromptCoT-2.0-SelfPlay-30B-A3B`）。`spec.md:128-143` 要求读取真实 tokenizer，并冻结 **student rendered template**，teacher 对 student 的真实 prefix 评分，不替换为 teacher 模板；开启 router replay 的路线也有独立记录。

`artifacts/readiness/assets-medium-assets-1002a.json` 是保存的实际 asset preflight：四模型 `token_ids_equal_student=true`、`same_token_vocabulary=true`、`vocab_count=151669`、EOS151645/PAD151643；**tokenizer JSON SHA 和 chat-template SHA 并非全相同**。例如 student tokenizer SHA `aeb13307...`，Math `6191e4eb...`，STEM/SWE `19564a48...`；各 template 也不同。该 receipt 同时明确 `data_ready=false`、`contamination_verified=false`、`capacity_verified=false`，所以资产兼容 PASS 不等于整任务 PASS。

该 receipt 中三公开源的实际行数/哈希：DAPO **17,917**、SHA256 `11371fdd2ee0ef0fd88d397fa1e4cc818bb78f06d6820be4cf1b375db4165d21`；DeepScaleR **40,315**、`4e9e7b18248d982b4498a54a6bdb37b1bb653cf5f77bc309fa67a6c2533c8ba4`；WebInstruct **228,736**、`e55a8e985e18e378e4cee9059442e94ed3e8d0f6280c4b3c6e0b2231982fc975`。

当前固定 ref 的最新 commit 是 `Record Math r256 native startup and initial serving wait`。`spec.md`/`progress.md` 区分已 PASS 的六项 smoke workflows、延期设计、正式 continuation 与 startup/故障；不能把 smoke whole-workflow PASS 写成正式 100-update curves 已完成。与当前 Qwen3.5 是否相同 tokenizer，本来源没有给出这种跨家族实测。

## 7. 应排除的误命中

- `origin/jxr/mopd-dev-260202@f4b309102...` 的 `playground/users/jxr/opd/step3p5air_midtrain_mainrecipe0107_s64k_256x4_g64_mopd_rlhf_rlvr_0202.py`、其 `playground/baseline_new/mopd/step3p5air/step3p5air_mopd_base.py`，虽然含 `qwen3_8b` 数据文件/注释，teacher load 路径实际是 `step4air_*`。这些只能证明复用含 Qwen 产物的数据，不能证明 Qwen 学生 OPD。
- `origin/wangheng-qwen-distill` 的 latest `qwen sft`、Qwen2.5 PPO branches，以及 Qwen3.5 writer/context-memory、grounding reward、omni midtrain/posttrain 分支分别有别的工作；没有独立 OPD/MOPD run/result 证据时，只归为旁证或排除项，不作不存在相关实验的全局断言。
- `Qwen2Model` class 是架构标签，不能单靠它断定具体 checkpoint 一定是 Qwen2.5-Instruct；R1-Distill checkpoint 以自己的 HF asset 作为 tokenizer 来源。

## 8. 本次验证、限制和交接

已完成：读取父任务 `requirements.md`/`plan.md`；读取 Steptron `AGENTS.md`、`docs/agents/{03-experiments-and-configs,04-validation-and-show-exp,06-git-and-worktree,15-mopd-stepcast-dense-disagg}.md`，相关 HJC subtree rules；全 ref metadata 枚举；固定 commit 的 tree/show/grep/log；用 Python3 标准库 `ast.parse`/`ast.literal_eval`/`json.loads` 静态检查 recipe、counts 和 receipts。**没有 import 任一 experiment config**（部分 config 会读取环境/建立服务）。没有运行 `show_exp.py`、pytest、training 或下载模型。

主要复查命令（均在 `/data/ycfeng/steptron`）：

```bash
git for-each-ref --format='%(refname)|%(objectname)|%(committerdate:iso-strict)' refs/heads refs/remotes
git worktree list --porcelain
git log --all --regexp-ignore-case --extended-regexp --grep='qwen.*(opd|mopd)|(opd|mopd).*qwen' -n 100 --format='%h|%cI|%s'
git show b48739f615e9a933003859f7a948398320774af5:playground/users/ycfeng/qwen35_opd/exp.py
git show b48739f615e9a933003859f7a948398320774af5:task_memory/task_2026-11-06_qwen35_opd_h200/evidence/default_data_manifest.json
git show 408af136836af8888a59bac89b63d42dfb8fb2e8:steptron/huggingface/hf_tokenizers.py
git ls-tree 408af136836af8888a59bac89b63d42dfb8fb2e8 third_party/steptokenizer
git show 6cd5b785736db931348f2f4fd8bf059ceb606703:task_memory/task_2026-10-02_h800_medium_singleteacher_bounded_replay/preparation_inputs.json
```

核查结果：ref counts、当前三对组合、55 raw files/482359 recorded rows、22 old MOPD JSONs、wrapper registry paths、archived medium token-equivalence flags 都来自上述固定 sources；实际结果与“仅 config/准备/diagnostic”已分开。Cloud file 是否仍在、最新 live run status、服务器尚未跟踪的新 refs、旧 tokenizer 与当前四 Qwen3.5 assets 的实际字节/token equivalence，本次**未验证**。父任务负责当前 tokenizer asset receipts、handbook 数据集表和 Lark 记录交叉核查；不应把本文历史模型兼容 receipt 外推成 Qwen3.5 兼容结论。

文件复查：本文 25 个 superproject commit IDs 经 `git cat-file -t` 均为 commit；另一个 40 位 ID 是上文单独标记的历史 tokenizer submodule gitlink。已静态复查 raw-format 转换代码和 c1/c2 scalar/sample-audit 实际字段。文档有 Modification History；未改其他任务文件或 Steptron 内容。

最终交付：`task_memory/task_2026-11-08_qwen_tokenizer_opd_inventory/steptron_records.md`。
