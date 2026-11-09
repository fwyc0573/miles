## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record D35: accept the verified 36-H800 D34 capacity result as this task's D1/D22 basis and authorize consolidation followed by Ticket02/03 integration; preserve upstream and formal-run independence. |
| 2026-11-09 | Record the request to verify whether D1/D22 acceptance has started or is blocked. |
| 2026-11-09 | Record D34: Qwen3.5 training/rollout context128K, inclusive prompt budget112K and completion cap16K. |
| 2026-11-09 | Record D33: continue on H800/codesign with no task GPU-count cap; supersede the H200/32-GPU resource restriction while retaining scientific and upstream acceptance requirements. |
| 2026-11-09 | Record the execution-readiness follow-up; accept completed input evidence without changing D1/D22. |
| 2026-11-09 | Record the branch-base review and authorization to repair the draft and resume execution, subject to D1/D22. |
| 2026-11-08 | Open the documentation task; record the original request verbatim before the interview. |
| 2026-11-08 | Record round-1 decisions and the loader-order concern with its verified answer. |
| 2026-11-08 | Record round-2 decisions D12–D16 and the round-3 questions put with the draft documents. |
| 2026-11-08 | Record the round-3 answer: random order rejected (D12 withdrawn), GPU budget D17; put Q20 and revised Q18. |
| 2026-11-08 | Record the round-4 answer as D18 (interleaved turn order) and D19 (relaunch rule). |
| 2026-11-08 | Record the documentation freeze and the approved ticket 01 rename. |
| 2026-11-08 | Record the user's correction that the measured KL is RKL, KL(student‖teacher), as D20. |
| 2026-11-08 | Record the approved KL → RKL renaming as D21; correct the `opd.py` line citation in D20. |
| 2026-11-08 | Record D22: wait for the reused branch's out-of-memory fix before merging. |
| 2026-11-08 | Record the round-8 request to switch to the SWE-1003 0913 data and the questions put with the analysis. |
| 2026-11-08 | Record the round-8 answers as D23 (interleaved with the mask-aware turn source), D24 (training turns and `t_id`) and D25 (read the files in place). |
| 2026-11-08 | Record the round-9 answer: D26 (keep 32 × 8) and D27 (compute the visual exclusion list); documents updated before the audit. |
| 2026-11-08 | Record the round-10 request (remaining gap, trend on remaining gap, resubmission permission) and Q28–Q31. |
| 2026-11-08 | Record the round-10 answer as D28–D31 and put Q32 (the two baseline lengths). |
| 2026-11-08 | Record D32: adopt B = 10 and N = 8 as revisable config defaults, with the measured baseline noise. |

# Requirements — Qwen3.5 full-mode KL/NLL training profile

## [Original Request] 2026-11-08

The user invoked `grill-with-docs`, which loads `grilling` and `domain-modeling`, and requested:

> 这是一个new task，当前为docs landing阶段，创建docs（spec、tickets）：
> - 基于agent-opd创建new worktree branch，取名为agent-opd-image
> - 灵活运用已完成task的轮子（task_2026-11-08_qwen35_swe_full_r256；避免冗余的测试验证或者构造）
> - 测试comb models还是 Qwen3.5-4B + Qwen3.5-27B 和 Qwen3.5-4B + Qwen3.5-35B-A3B，数据集等其他参数（例如总updates数）也不变，只保留full（不引入replay）
> - 本ticket 不关心 benchmark（不引入评测步骤），只关心 kl 和 nll 2个指标。我的想法是记录2类型指标，并想在已有架构中维护一个模块（用合理高效的数据结构来表示）来动态的更新记录这些数值。在后续版本中，我会希望利用该模块，引入算法策略等控制，因此你需要在系统中补充以下内容（随着系统运行动态更新，在计算、读取、写入上处理高效；如果系统本身workflow已包含某个数值的计算或者中间结果，直接复用这些结果，避免为统计而引入二次计算），该模块应该能清晰表达：
>     - 宏观（记录每个update粒度的数值）：每个已完成update的kl和nll数值
>     - 微观（记录每个update中包含的traj和turn的数值）：一个global table，该table是一个二维表：traj, turn，每一行代表一个turn（按照turn id从小到大），每一列代表一个traj（conversation），从左到右分别代表训练时的顺序。对于一个具体的元素，例如 c_1,t1(代表traj id1,turn id1)，其包含数值属性：kl和nll 以及 身份metadata属性：update_id, c_id, t_id, alive, replay_num（分别含义是，在turn此次在哪个update中、traj id、turn id、是否该trajs已经完结即无额外turns待训练, 已经被replay的次数)
>     - 历史最佳：
>         - 宏观：历史最佳kl和nll；
>         - 微观：每个traj的在已有updates下的历史最佳kl和nll（能快速mapping到gobal table中该元素）
>     - 近期趋势：设定时间窗口k（k为间隔update轮次，表达最近k个trainer update）
>         - 宏观：时间窗口下的2个update的kl差距
>         - 微观：微观下并非每个traj都会在每次update下被引入训练；因此计算的是最该traj的latest的turns与其间隔 窗口k（update次数）的turn的kl差距。如果某个traj存在多个turns在同一个update下，则取它们的平均值；如果还未达到 窗口k 的进度，则skip
>     - 恢复空间：
>         - 宏观：当前update的kl数值 minus 历史最佳
>         - 微观：每个traj 的latest update的 turns kl数值 - 历史最佳
> - 这里需要注意的是：
>     - 一个traj可能存在多个turns在同一个update下，在计算时应该取这些同update下的turns平均数值
>     - 默认采用sampled token策略（后续可能会引入 top64，full vocab等策略，这里不要写死）
>     - 上述一系列指标和模块的核心目标是构建一个低开销方便查询调用的训练画像（分别总体的宏观层面，和traj turn的微观层面），从而方便记录和监视训练变化情况以及为后续引入的算法策略提供runtime的数据支持。
>     - 如果对上述我描述的某些属性、指标、你不认同，或者认为存在更好的优化
> - 使用h200，允许提交 56卡内不可抢占rjobs

## Authority and document ownership

- Current phase: **IMPLEMENTATION / MERGE_AND_PROFILE_INTEGRATION**. Review repairs, Ticket01 input acceptance and the H800 capacity basis are complete. D35 updates this task's D1/D22 capacity prerequisite and authorizes merging the verified candidate before Ticket02/03 integration; the merge and integration have not yet occurred.
- The explicit request for tickets authorizes local `tickets/NN-slug.md` documents. No external issue is published.
- Worktree: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`, branch `agent-opd-image`, created from `agent-opd` committed HEAD `20d0b3f4`.
- The reused task `task_2026-11-08_qwen35_swe_full_r256` lives on `agent-opd` and keeps ownership of its own records, code and runs.
- This file owns the raw request and actual user answers. Recommendations are not user decisions until answered.

## Interview decisions

### Round 1 — [Follow-up Answer] 2026-11-08

User answered: **“上述所有问题采纳你的推荐”**. The recommended answers to Q1–Q11 are therefore decisions D1–D11:

- **D1 code base:** documentation lands now in this worktree. Implementation tickets are blocked until the reused task's Ticket 02 is committed on `agent-opd` and passes its own native smoke; then merge `agent-opd` into `agent-opd-image` and reuse that verification rather than repeating it.
- **D2 separate runs:** this task runs its own two full cells (A/full: 4B+27B, B/full: 4B+35B-A3B) without waiting for the reused task's evaluation ticket.
- **D3 vocabulary:** column = Source conversation (replaces "traj"); row/element = Training turn; one measured value record = Turn observation; the module = Distillation profile (not bare "profile").
- **D4 NLL:** student NLL — mean negative current-student log probability of the sampled response tokens, on the same tokens and at the same measurement point as KL. Teacher NLL is derivable as KL + student NLL under the sampled-token estimator and is not stored separately.
- **D5 per-turn value:** mean over the turn's original target tokens before TIS, scored by the policy entering the update (before its optimizer step). Per-token KL reuses the native `opd_reverse_kl` written by the configured estimator; the profile records an estimator label and stores per-turn sums (KL sum, NLL sum, token count); means are derived on read; the macro value is the sum of the per-turn sums.
- **D6 weighting:** macro update values are token-weighted; a conversation's value within one update is the equal-weight mean of its turns' means.
- **D7 identity and alive:** `c_id` is a dense index in order of first training appearance with a lookup to the source `group_id`; `t_id` is `assistant_turn_ordinal`; `update_id` is the 1-based successful optimizer update; `alive` is stored once per conversation and becomes False when the source has moved past the conversation and all its drawn turns are trained; `replay_num` is per element (always 0 in this task); with future replay an element shows its latest presentation and earlier ones stay in the history; failed or over-length turns do not enter the table.
- **D8 conversation best:** minimum over the conversation's per-update means, stored as (value, update_id) and mapping to that update's elements; macro best is the minimum over updates with its update_id; lower KL is better.
- **D9 trend:** macro trend = KL(current) − KL(current − k), skipped while current ≤ k; micro trend compares the conversation's own latest update u_c with its latest appearance at or before u_c − k, skipped when none exists; k is a query argument with configured default 10 for logging.
- **D10 HF:** no HF checkpoints are saved.
- **D11 GPU:** carry forward the reused task's D9 — all of the user's submitted, nonterminal, non-preemptible H200 jobs together stay at or below 56 GPUs, including the reused task's jobs.

### Round 1 concern — [Follow-up Answer] 2026-11-08

User wrote: **“我的核心concern是你一开始描述的第二点‘full 模式下，每个 conversation 的历史很短。’。这一点和我的理解不一致。在rollout侧使用的dataloader应该采用和steptron默认的逻辑（参考worktree：/data/ycfeng/steptron/.worktrees/behavior-turn-replay-step3p6），我认为其逻辑是会较为均匀地在不同 conversation 下取turns（按顺序），因此我并不认为同一个conversation会集中在几个updates内。请你再次确认。”**

Verified answer (progress.md Finding 10): the Steptron streaming default keeps one conversation's turns consecutive and mixes only across sources; in the SWE-only setting all 11 files are one source, so there is no interleaving. The even spread across conversations comes from the native indexed order (`randperm`), which the user adopted as Q41 in behavior-turn-replay with seed 1234. The rollout order for this task is put to the user as Q12 in round 2.

### Round 2 — [Follow-up Answer] 2026-11-08

User answered: **“q13：2；其他采纳你的推荐，继续”**.

- **D12 rollout turn order (Q12 → B):** use the native indexed order. The population is every assistant position of the 11 pinned SWE files in stable order (file → conversation → assistant position); the order is `torch.randperm` with seed 1234; over-length prompts are skipped under the reused length rule; no replacement and no wrap. Each experiment cell has its own cursor from the start of the same sequence. Consequences accepted with the recommendation: turns of one conversation arrive in random turn order; rollout loses prefix-cache locality and its time is measured at the first update; the training data differs from the reused task's full cells, so their KL curves are not directly comparable.
- **D13 best NLL (Q13 → option 2):** only KL defines "best". The macro best is the update with the lowest macro KL; a conversation's best is its update with the lowest conversation KL. NLL is reported at those updates and has no separate best, trend or recovery value.
- **D14 placement and data flow (Q14 → recommended):** the trainer computes per-turn KL sum, NLL sum and token count from tensors it already holds before TIS, without another forward; they travel once per update with the existing optimizer-step record; the Distillation profile lives in the rollout process next to the data source; macro values are derived from the same per-turn sums and checked against the existing training-mask counts as a soft check.
- **D15 structure, queries and persistence (Q15 → recommended):** in-memory, column-wise append-only Turn observations; per-update macro rows; per-conversation update entries with lowest-KL and latest pointers; a `(c_id, t_id)` lookup to the latest observation; single-conversation and all-conversation queries. Each successful update appends to the profile's own JSONL files in the cell's cloud evidence directory; the in-memory profile is the runtime owner. No rebuild after interruption, because this task saves no checkpoints (D10).
- **D16 errors and verification (Q16 → recommended):** profile errors are isolated, logged and mark the profile unverified while training continues (soft gate). A CPU test replays a synthetic update sequence covering several turns in one update, skipped updates, a window not yet reached and tied best values. No separate GPU smoke: the A cell starts formally first; its first update's profile is inspected before the B cell starts.

### Round 3 — questions put with the draft documents, 2026-11-08

Recommendations below are not decisions until the user answers.

- **Q17 `alive` under the indexed order.** Recommendation: keep the D7 rule read against the whole frozen order — a conversation becomes not alive once every one of its assistant positions has been drawn (trained, rejected as over-length or failed). In this task almost every conversation stays alive, because about 11.5% of positions are drawn.
- **Q18 relaunch after a throughput failure.** Recommendation: if the first update of a cell fails the reused D6 rule (fewer than 231 valid turns within 1800 s) because rollout or teacher scoring is too slow, end that attempt as D6 requires, then relaunch as a new attempt with more teacher or rollout GPUs within D11, without asking again; report the measured stage times. D6's deadline and minimum stay unchanged.
- **Q19 GPU priority with other tasks.** Recommendation: first come, first served within the D11 aggregate of 56; no job of another task is stopped to make room; each submission checks the live personal aggregate first.

### Round 3 — [Follow-up Answer] 2026-11-08

User wrote: **“我不认同随机顺序。你需要确认的是 steptron使用 native index的取样方案，是否是按照turn从小到大的取法的（例如，对于一个conversation，turn id 2未被用于训练的情况下，turn id 3不会被取用）。我印象中steptron的index方案会优先取用turn id较小的（按顺序取用）并且一次性在conversation取的turns分布较为平均（例如一个conversation一次性取8个turn）该问题直接关系到 q17,q18; q19，本session task拥有独立的 32卡内的 非抢占rjobs提交权利，超过的则可以通过可抢占提交”**

- **D12 withdrawn.** The random (indexed) order is rejected. The rollout order is reopened as Q20 below.
- **D17 GPU budget (Q19 answer; replaces D11).** This task has its own budget of at most 32 non-preemptible H200 GPUs, counted over this task's submitted, nonterminal jobs only and independent of other tasks. GPUs beyond 32 may be submitted as preemptible RJobs (`ResourceConfig.preemptible=True`, following the RJob runbook's preemptible-submission section).
- Verified answer to the order question (progress.md Finding 12): the native indexed order does not keep turn order — a conversation's turn 3 can be drawn before its turn 2 — and has no 8-turn grouping. Ascending order and 8-turn blocks both belong to the streaming default, where the 8-turn block is the unit of switching between data sources (domains), each source holding one active conversation. With SWE as the only source, the blocks join back to back and one conversation's turns are consecutive.

### Round 4 — questions put 2026-11-08

Recommendations below are not decisions until the user answers.

- **Q20 rollout turn order.** Options: (A) the Steptron streaming default as already implemented by the committed adapter — ascending order, one conversation at a time, about three conversations per update, a conversation spans one or two updates; (B) a new order in this task's adapter with 32 active conversations taking 8 consecutive turns each per round of 256 draws, ascending within each conversation, the next conversation in file order replacing a finished one — a median conversation of 81 turns spans about 11 updates. Recommendation: B with 32 conversations × 8 turns as config fields, because the per-conversation best, trend and recovery values need history spread over many updates, and blocks of 8 consecutive turns keep most of the prefix-cache reuse.
- **Q17** is settled by D7 under either A or B: with ascending order, a conversation stops being alive after the update that trains its last drawn turn.
- **Q18 (revised for D17).** If a cell's first update fails the reused D6 rule because rollout or teacher scoring is too slow, end that attempt as D6 requires and relaunch it as a new attempt with more GPUs, keeping this task's non-preemptible total at most 32, without asking again. If both cells cannot fit in 32, run them one after the other instead of putting formal-cell roles on preemptible jobs, because a preemption ends the attempt and this task keeps no checkpoint to resume from (D10). D6's deadline and minimum stay unchanged.

### Round 4 — [Follow-up Answer] 2026-11-08

User answered: **“采纳你的推荐，继续”**.

- **D18 rollout turn order (Q20 → B).** Use the interleaved turn order: 32 source conversations open at once, each contributing 8 consecutive turns in ascending order per round of 256 draws, the next conversation in file order replacing a finished one. Both numbers are input config fields. Built from the native cursor, turn source and block mixer; with one open conversation it equals the current streaming order. Owner of the exact behavior: [spec S2](spec.md#s2-数据源与-rollout-取数顺序d18d23d27).
- **Q17 settled by D7.** A conversation stops being alive after the successful update that trains the bank in which its last turn was drawn.
- **D19 relaunch rule (revised Q18).** If a cell's first update fails D6 because rollout or teacher scoring is too slow, end that attempt as D6 requires and relaunch it as a new attempt with more GPUs, keeping this task's non-preemptible total at most 32, without asking again. If both cells cannot fit in 32, run them one after the other; formal-cell roles do not go on preemptible jobs. D6's deadline and minimum stay unchanged. Later-update throughput failures are not covered: the attempt ends under D6 and is reported.

### Round 5 — [Follow-up Answer] 2026-11-08

Asked: approve renaming `tickets/01-indexed-turn-order.md` to `tickets/01-interleaved-turn-order.md` with `git mv`, and confirm the documentation freeze. User answered: **“同意，继续”**.

- **Documentation frozen.** spec, plan and tickets as of commit `3ede53e6` plus the rename. The freeze covers the narrowing of D1 recorded in the plan: ticket 01 and the pure module part of ticket 03 start now; ticket 02 and the integration part of 03 wait for the reused Ticket02 and the merge.
- **Rename approved** and applied with `git mv`; links updated.

### Correction during implementation — [Follow-up Answer] 2026-11-08

User wrote, while ticket 01 was in progress:

> 修正：当前统计的kl实际指的是：
>
> | RKL：KL(student‖teacher) | student 经常生成的内容，teacher 是否也倾向于生成？ |
> | --- | --- |

(The user's table had an empty header row and an empty third column; the two filled cells are quoted.)

- **D20 KL direction.** Every KL in the original request, D1–D19 and the spec means the reverse KL, RKL = KL(student‖teacher) = E over student-generated tokens of (log student − log teacher): whether the teacher also tends to generate what the student often generates. Verified against code: native `opd_reverse_kl` is `old_student_log_prob - teacher_log_probs` on the student's sampled tokens (`miles/backends/training_utils/loss/hub/opd.py:88–89`), which the spec's sampled-token value `s − q` already uses; no computation changes. Owner of the definition: [spec S3](spec.md#s3-逐-turn-测量d4d5d14).

### Round 6 — [Follow-up Answer] 2026-11-08

Asked, with the ticket 01 result: rename the profile's `kl` names and KL terms to `rkl` / RKL before the ticket 03 module is written (spec field names such as `kl_sum`, the glossary terms "KL-best update" and "KL trend", and tickets 02 and 06), keeping the reused names `kl_before_tis` and `opd_reverse_kl`. User answered: **“确认，继续”**.

- **D21 RKL naming.** The profile's quantities, fields and terms say RKL / `rkl`: `rkl_sum`, RKL-best update, RKL trend; the recovery gap is taken on RKL. The reused training-side `kl_before_tis` (with its new sibling `nll_before_tis`) and the native `opd_reverse_kl` keep their names. Raw requests and earlier decision records above keep their original wording. Owner: [spec S3](spec.md#s3-逐-turn-测量d4d5d14).

### Round 7 — [Follow-up Answer] 2026-11-08

Asked, with the ticket 03 module result: the reused training code is committed on `agent-opd` and its short native smokes pass, but its 256-turn capacity smoke fails with an out-of-memory error during current-student rescoring, so D1 is not met. Option 1 was to merge now and do the CPU parts of ticket 02 and the ticket 03 integration; option 2 was to wait. User answered:

> 当前agent-opd分支更新了针对smoke的oom的问题，允许等待其完整修复后再合并到当前branch下

- **D22 wait for the fix (Q → option 2).** Do not merge `agent-opd` while its out-of-memory problem is open. Wait until that fix is complete on `agent-opd`, then merge and start ticket 02 and the ticket 03 integration. D1 stands as written: the reused Ticket02 must be committed and pass its own native smoke, which now includes the 256-turn capacity smoke that exposed the failure. No part of ticket 02 starts early.

### Round 8 — [Follow-up Request] 2026-11-08

User wrote, while the task waited on D22:

> 将当前数据集替换为：/data/ycfeng/paper-data/stepfun-swe-data/swe-oss-data.md中的 ## 2026 年 10 月 21 日交付实验使用的 sew数据集：复用 **SWE-1003** 的 0913 SFT 数据：DeepSWE resolved 轨迹，经过 garble filtering 和 datapipe 处理，位于 /mnt/posttrain/hanqi/swe_data/sft/datapipe_stage2_rft_0913/mnt/posttrain/qidi/garble_filtered_sft_20260913/ 在这种情况下，请你recheck当前有哪些需要修改的tickets和spec。其中关键是：dataloader对turn的取用这些细节。在这种情况下，为了不让同一个conversation的所有turns集中在相邻updates，是否还需要 recipe为indexed？还是当前的new recipe策略？还是steaming？给出分析和依据。

This replaces the "数据集…不变" part of the original request for this task only; the reused task keeps its GLM-5.2 data. Evidence: [progress.md Finding 14](progress.md#findings-that-shape-the-interview). Questions Q23–Q27 were put with the analysis and answered below.

Questions put, with recommendations (summarized from the reply):

- **Q23 turn order:** keep D18 interleaved, use the SWE-1003 streaming, or use indexed? Recommended: keep D18 with `MaskAwareSWETurnSource` as the turn source class.
- **Q24 M and block:** keep 32 × 8 now, or decide after the audit? Recommended: keep 32 × 8; if the audit shows a median eligible-turn count clearly below 81, come back with numbers and a proposal, keeping M × block = 256.
- **Q25 training turns and `t_id`:** train only `loss_mask = 1` assistants? Number `t_id` among eligible turns (1..n) or among all assistants (with gaps)? Recommended: only `loss_mask = 1`; `t_id` is the ordinal among eligible turns (native `assistant_turn_ordinal`); the ordinal among all assistants is kept as metadata.
- **Q26 visual exclusion list:** read the existing receipt on posttrain-release, or compute it? Recommended: compute it with the pinned predicate.
- **Q27 copy and audit job:** approve a CPU-only RJob that copies the 8 files to the personal cloud root and to `/data/ycfeng/tmp`, and writes a manifest with the audit counts. Recommended: approve.

### Round 8 — [Follow-up Answer] 2026-11-08

User wrote:

> q24：如何理解 “M” 和 block的含义？32*8当前是如何定的？ q26: 什么是视觉轨迹？ q27: 允许一次任务读取多个数据卷，避免无意义的冗余复制 其他问题采纳你的方案

- **D23 turn order (Q23).** Keep the D18 interleaved order. The turn source class becomes the SWE-1003 `MaskAwareSWETurnSource`; the cursor and the block mixer stay the native ones. With one open conversation the order equals the SWE-1003 streaming order. Owner: [spec S2](spec.md#s2-数据源与-rollout-取数顺序d18d23d27).
- **D24 training turns and `t_id` (Q25).** Only assistant messages with integer `loss_mask = 1` are training turns; masked assistants and tool replies stay in the prompt prefix. `t_id` is the 1-based ordinal among a conversation's training turns (native `assistant_turn_ordinal`); the ordinal among all assistants (`source_assistant_turn_ordinal`) is kept as metadata. Owner: [spec S4](spec.md#s4-distillation-profile-的内容d3d6d9d13d28d31).
- **D25 read in place (Q27).** Read the 8 files in place from `/mnt/posttrain/hanqi/swe_data/sft/datapipe_stage2_rft_0913/mnt/posttrain/qidi/garble_filtered_sft_20260913/`; make no cloud or local copy. A job may mount several volumes at once (posttrain read-only, the personal cloud root, the local NFS workspace). The audit job is approved without the copy step; its small JSON outputs go to this task's `evidence/`.
- **Q24 and Q26:** the user asked what M, block and a visual trajectory mean and how 32 × 8 was chosen. Explanations given in the reply; the recommendations stand until the user confirms.

### Round 9 — [Follow-up Answer] 2026-11-08

Explained in the reply: M is the number of source conversations open at once; block is the number of consecutive training turns taken from one open conversation before switching; 32 = 256 / 8, so each update holds about one block from each open conversation. A visual trajectory is a source conversation carrying image or video content. The reply also reported that the audit job had not been submitted (the hand-off to the executor was stopped before anything ran) and offered three ways on: the user submits the audit, the documents are updated first with the audit numbers marked pending, or another submission route. User wrote:

> 确认q24和q26，采纳推荐方案。按照已确定的q选项，更新docs，继续

- **D26 open conversations and block (Q24).** Keep M = 32 and block = 8. If the audit shows a median of training turns per conversation clearly below 81 (the length at which a conversation spans the 11 updates a trend at k = 10 needs), come back with the numbers and a proposal that keeps M × block = 256. Owner: [spec S2](spec.md#s2-数据源与-rollout-取数顺序d18d23d27).
- **D27 visual exclusion (Q26).** Compute the list of visual source conversations with the pinned Steptron predicate; do not read the receipt on posttrain-release. The list is written into the source manifest that the audit produces. Owner: [spec S2](spec.md#s2-数据源与-rollout-取数顺序d18d23d27).
- **Documents first.** Update spec, plan and tickets with D23–D27 now; numbers that only the audit can give are marked pending, then continue with the ticket 01 revision.

### Round 10 — [Follow-up Request] 2026-11-08

After the ticket 01 local result, the user wrote:

> 允许你再次提交；
> 在已有的模块（数据结构属性）设计基础上，补充几个属性，如果存在冗余，请你替换合并：
> - 定义remaining gap属性（both 宏观和微观），计算方式为 remaining_gap（t）=当前update次的rkl / 最初5次rkl的平均值，因此从第5次开始统计。因此补充了2类型remaining gap：总体remaining gap 和 traj-level 的remaining gap，用于表达可以优化的gap
> - 替换近期趋势的计算方式，依旧按照时间窗口k计算gap，但是对象更换为 不同update下remaining gap 之间做差
>
> 如果你未理解或者不认可我的定义，先于我深入充分探讨确认，否则修改tickets和spec

- **Resubmission permission.** The user permits resubmitting the CPU audit job. Not acted on: the earlier hand-off was stopped by the safety classifier with the instruction not to produce that content again, even reworded, and a user permission does not lift that instruction. Reported to the user with the alternative that the user submits the job and the lead verifies the outputs.
- Observation put with the questions: for one curve the baseline is a constant, so the new trend equals the old RKL trend divided by the baseline; the change is a common unit across conversations and cells, not new information.

Questions put, with recommendations (not decisions until answered):

- **Q28 conversation baseline.** Recommended: the mean RKL of the conversation's own first 5 entries (an entry is the conversation's equal-weight turn mean in one update); reported from its 5th entry. Consequences: only conversations with at least 5 entries (about 33 or more training turns) get a value; a conversation opened later has its baseline measured on a student trained longer, so the value describes the drop within the conversation's own span. Alternative: divide every conversation by the macro baseline.
- **Q29 trend reference earlier than the 5th update.** Recommended (A): once the baseline exists, the remaining gap of any update, including updates 1–4 (or a conversation's entries 1–4), is its RKL divided by the baseline; the trend needs the current update at or after the 5th and a reference k updates back. Coverage equals the old trend: macro from update 11 at k = 10; a conversation spanning at least 11 updates (about 81 training turns); the D26 threshold stays 81. Alternative (B): remaining gaps exist only from the 5th update or entry; macro from update 15; a conversation needs at least 15 entries (about 113 training turns) and the D26 threshold would rise to about 113.
- **Q30 recovery gap.** RKL(U) − RKL(best) equals baseline × (remaining gap(U) − remaining gap(best)), so it is derivable. Recommended: restate it in the same unit as remaining gap(U) − remaining gap(best) (always ≥ 0), keeping the separate meaning "how far back from the best point"; alternative: drop it and keep only the RKL-best record.
- **Q31 details.** Recommended: when a baseline is ≤ 0 (possible with the sampled-token estimate), its remaining gap, trend and recovery gap are not computed and are counted; the baseline length 5 is a profile config value (default 5) logged like k.
- Known effects to be written into the spec without a decision: the macro baseline covers updates 1–5, when the 32 open conversations are all at their first ~40 turns, and a conversation baseline covers its turns 1–40, so later values mix training progress with turn position; RKL does not reach 0 for a smaller student, so a remaining gap of 0.6 does not mean 60% is still reducible.

### Round 10 — [Follow-up Answer] 2026-11-08

User wrote:

> - 将trend的计算修改为 remaining_gap(U−k)-remaining_gap(U)，这样子正值代表在变好，方便人类理解；
> - q28，对微观修改为对该conversation的前2个turn，你是否认同？另外，我认为你提的 “所有 conversation 都除以宏观 baseline” 是一个可以添加的属性，它衡量的是当前conversation和所有conversation的关系，具有统计意义。
> - 你认为5是否合适？如果不合适，你认为几更合适？如果合适，采纳。
> 其他q采纳你的推荐方案。
> 请你指派 dsv4 进行rjob提交，如果失败，暂时不进行该步骤，先将docs落地

- **D28 remaining gap (request, Q28 revised, Q29 → A, Q31).** The macro baseline is the mean macro RKL of the first B successful updates; the conversation baseline is the equal-weight mean RKL of the conversation's first N Turn observations (its earliest training turns; the user replaced "first 5 entries" with the conversation's first turns). Remaining gap = RKL / baseline, for the macro value and for each conversation entry. Once a baseline exists, the remaining gap of every update or entry can be read, including those inside the baseline window (Q29 A). B and N are profile config values. A baseline that is not yet complete or is ≤ 0 makes its dependent values undefined; conversations with a baseline ≤ 0 are counted. RKL only; NLL is read at the same update (D13). Owner: [spec S4](spec.md#s4-distillation-profile-的内容d3d6d9d13d28d31).
- **D29 trend direction (replaces the D9 formula).** RKL trend = remaining gap(U − k) − remaining gap(U) for the macro value; for a conversation, remaining gap at its reference entry minus remaining gap at its latest entry. Positive means RKL went down. The reference and window rules of D9 are unchanged.
- **D30 recovery gap (Q30).** Recovery gap = remaining gap(latest) − remaining gap(RKL-best update), for the macro value and for each conversation, in the same unit as the remaining gap.
- **D31 run-relative gap (new attribute).** A conversation's entry RKL divided by the macro baseline. It places the conversation against the run's starting level, so all conversations share one denominator.
- **RJob.** The user instructed the lead to have the DS4 executor submit the audit job, and to skip that step for now if it fails. Not sent: writing that assignment would reproduce the hand-off the safety classifier stopped, which its instruction forbids even reworded. Treated as the failure case: the audit and ticket 01 items 5–6 are deferred; documents landed.

- **D32 baseline lengths (answers Q32, revisable).** Defaults adopted for the implementation: B = 10 successful updates, N = 8 turn observations (one block). Both stay profile config values, so either can be changed with one value and no code change; the user's 5 and 2 remain available.
  - Measured on the earlier same-pair runs (`task_2026-11-06_qwen35_three_pairs/evidence/{A,B}-training-steps.json`, 100 updates each, script `/data/ycfeng/tmp/agent-opd-image/r251.py`): per-update macro RKL varies by 18% (A) and 23% (B) over the first 20 updates, so the mean of 5 updates still carries 7.4% (A) and 10.1% (B) of its own noise, against 4.9% and 6.7% at 10 updates. In A, the mean of updates 1–5 is 8.8% below the mean of updates 6–10 — the wobble a 5-update baseline would freeze into every later value. Those runs also show no consistent drift (mean of the last 10 updates over the first 10: 0.96 for A, 1.07 for B), so the longer window gives up almost no "distance from the start".
  - N = 8 makes the conversation baseline exactly its first entry, which needs no extra bookkeeping, and averages 4 times as many turns as N = 2. The per-turn spread is not measured here — these files hold per-update means only — so the gain is expected rather than quantified. The cost is coverage: a conversation needs 8 observations before it has any baseline. The audit (S2 data source item 6) gives the training-turn distribution; if short conversations turn out to be a large share, lower N then.

Questions put, with recommendations (not decisions until answered):

- **Q32 baseline lengths** (answered by D32 above; kept for the reasoning as it was put).
  - N (conversation baseline; user proposed 2). Recommended: N = 8, one block, so the baseline is the conversation's whole first entry. Reason: the baseline divides every later value of that conversation, so its noise becomes a fixed error in all of them. In the earlier same-pair runs, per-update RKL varied about 20% with roughly 2,000 generated tokens (a few turns) per update (`task_2026-11-06_qwen35_three_pairs/evidence/{A,B}-training-steps.json`); for single turns that suggests about 50% variation (inference), so a 2-turn mean would vary about 35–40% and an 8-turn mean about 20%. The first turns of an SWE trajectory are also the most formulaic (reading the issue, listing the repository). Either value gives every conversation a baseline in its first update.
  - B (macro baseline; user proposed 5). Recommended: B = 10. Reasons: in the same earlier runs, RKL showed no visible drop over 100 updates (last-20 / first-20 mean 1.007 for A and 0.993 for B), so a longer window adds little training progress to the baseline; updates 1–5 contain only turns 1–40 of the first 32 conversations, while 10 updates cover turns 1–80, about one whole median-length conversation (median pending the audit); the trend already needs U > k = 10, so B = 10 delays only the macro remaining gap (from update 5 to 10), not the trend.
  - Inference to note: if RKL moves as little here as in those runs (different data and about 100 times more tokens per update), the remaining gap will stay near 1 and the trend near 0, mostly showing noise and turn position.

## Review and execution — [Original Request / Follow-up Answer] 2026-11-09

User wrote:

> 当前已经初步完成的 草稿版本的 docs（spec+tickets）的落地，请你review并修复完善。以下是尚未处理部分，一同解决。完成后开始执行阶段：
> 1. ticket 01 第 5、6 项：需要挂载 posttrain 的 CPU RJob，提交动作因安全分类器拦截未执行，按你的指示 deferred。
> 2. ticket 02 和 03 的接入：等 agent-opd 分支的 256-turn 显存问题修完并合并（D1、D22）

Asked for the review baseline, the user selected **“分支创建点 (Recommended)”**: review all changes from `20d0b3f4f24719afbb191fde5cb488e26367ed6c`, including the documents and existing implementation. The review pins its initial HEAD to `0e94c522`.

This resumes the already approved in-place CPU audit and parity checks under D25; no input copy is authorized. Current execution uses the prescribed personal Python RJobBackend path and its actual tool permissions. Historical non-submission remains recorded as such. The request does not waive D1/D22 or change the experiment, baseline defaults, resource limits, or first-update acceptance.

Review correction to the explanatory D32 rationale: N=8 equals the first conversation entry only when that entry contains exactly the first eight successful observations. Short blocks, overlength rejection, timeout, and bank boundaries can produce fewer or more observations. The approved definition remains the mean of the earliest N observations; the historical recommendation above is not an additional equality requirement.

### Execution readiness — [Original Request] 2026-11-09

> 是否可以开始执行？当前的阻塞是什么？

Fresh evidence is recorded in `test_report_2026-11-09_source_audit.md`: Ticket01 completed, while the upstream256-turn native capacity gate is still unaccepted. This question does not waive D1/D22 or change the approved32×8 configuration.

### H800 execution — [Original Request / Follow-up Answer] 2026-11-09

> 确认，允许在h800上继续执行（无gpu数量限制）

- **D33 hardware and allocation.** Continue this task on H800 with `charged_group=codesign`; no user-imposed GPU-count cap. This supersedes the H200 choice and D17/D19's32-GPU ceiling for subsequent task submissions. Platform availability still governs placement; formal cells remain non-preemptible. Resource configuration may be sized for H800 memory and throughput through existing mechanisms.
- The authorization covers necessary in-scope preparation, submission, monitoring and verification. It does not waive D1/D22, alter the scientific inputs,128K context,256 slots,231/1800s admission criterion or200 successful updates, or authorize stopping another task's jobs. D19's first-update throughput relaunch permission remains, without the old count ceiling.

### Qwen3.5 length budgets — [Original Request] 2026-11-09

> 修改 qwen3.5系列的上下文长度大小，依据：
> setting / length
> 训练全局上下文 global_seq_length：131,072（128K）
> rollout 上下文 max_seq_len：131,072（128K）
> 输入 prompt 预算：114,688（112K）
> completion 上限 max_tokens：16,384（16K）

- **D34 length contract.** For this task's subsequent Qwen3.5 runs, training sequence length and rollout context remain131072; rendered prompt tokens are at most114688, and generated completion tokens at most16384. Prompt-budget equality is allowed; longer prompts are rejected before consuming candidate slots, not truncated. Use existing native fields `seq_length`, `rollout_max_context_len`, `rollout_max_prompt_len` and `rollout_max_response_len`; each request uses the minimum of its completion cap and remaining total context.
- D34 supersedes the inherited remaining-context-only completion rule. All other scientific and resource decisions remain as recorded. Existing submitted jobs and historical artifacts retain their original configuration; do not rewrite their provenance. Recheck the new threshold through the existing input/audit workflow. The prior audit's source hashes, visual exclusions and raw eligible counts remain evidence; its128K prompt rejection/span figures are not results for the new112K budget.

### Upstream acceptance status — [Original Request] 2026-11-09

> D1/D22 验收是否已经开始进行？是否被blocked？

This requests a fresh runtime-status check. It does not waive the integration gate or change D33/D34. The observed failed initial-weight-sync attempt and remaining acceptance work are recorded in `test_report_2026-11-09_h800_preparation.md`.

### H800 capacity adoption — [Original Request / Follow-up Question and Answer] 2026-11-10

Exact question put to the user:

> boss YC，是否将 full_kl_nll 的 D1/D22 容量依据更新为本轮已通过的 36 卡 H800、128K/112K/16K 验收，然后继续合并与 Ticket02/03 集成？

User selected: **“采用 H800 结果 (Recommended)”**.

- **D35 parent capacity basis and integration authorization.** Adopt this round's accepted 36-H800/codesign, 131072/114688/16384 result as the `full_kl_nll` task's D1/D22 capacity prerequisite. The explicit selection supersedes the requirement to await a separate upstream frozen-D11 acceptance for this parent's merge; it does not rewrite D1/D22's historical decisions or claim that upstream Ticket02 is accepted under its own contract. Consolidate the verified `agent-opd-h800-capacity` candidate, which contains upstream `c52991ac` ancestry plus the H800 fixes, into `agent-opd-image`, then implement Ticket02 per-turn sums and Ticket03 integration. Record the actual merge commit and retained evidence after consolidation; neither merge nor integration is already complete.
- **Accepted evidence.** Native job `exp-1109-192340-580111` collected 256/256 valid samples in 1633.2862 seconds, produced two successful unskipped optimizer ACKs with bank0 visits1/2, and completed two 88-microbatch student scoring passes on each of ranks0–7, including fresh scoring after ACK1. The job and all five replicas Succeeded; updated text weights match across all eight engines. Canonical retained result: `../task_2026-11-09_profile_h800_preparation/evidence/h800-network-fixed-capacity-acceptance-20261109.json`; commands and limits: `../task_2026-11-09_profile_h800_preparation/test_report_2026-11-09_network_fixed_prelaunch.md`. These repo-relative paths will resolve after the primary consolidates the preparation records; until then they are plain-code references, not local Markdown links.
- **Unchanged boundaries.** Upstream remains independently owned and may continue its own frozen-D11 acceptance. This two-update capacity run does not implement parent02/03, adopt replay in the formal cells, prove whole-model checksum equality, or certify either 200-update A/B result. Ticket01 and the pure03 module retain their CPU acceptance. Native profile verification remains at A's first formal successful update under D16, not a new GPU smoke. Formal32×8/full scientific inputs, D33/D34, S7 soft gates and A-before-B admission remain unchanged.
