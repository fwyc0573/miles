## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record D11: replace GLM-5.2 training inputs with the eight SWE-1003/0913 DeepSWE resolved sources; reopen input acceptance. |
| 2026-11-08 | Clarify completion-only RKL statistics with fresh current-student scoring on the unchanged completion; no new estimator or sampling path. |
| 2026-11-08 | Amend D9 with the user-approved temporary independent task allocation, overflow preemption, and continuation after expiry. |
| 2026-11-08 | Record approval to implement and execute the frozen tickets in parallel after the documentation review fixes. |
| 2026-11-08 | After the post-freeze review, link the spec for D3 optimizer parameters instead of restating them and restore word spacing; no decision changed. |
| 2026-11-08 | Record D1–D10 and explicit final confirmation; freeze the documentation deliverable. |
| 2026-11-08 | Open the new documentation task; preserve the original request and separate confirmed requirements from interview decisions. |

# Requirements — Qwen3.5 SWE full versus r256

## [Original Request] 2026-11-08

The user invoked `grill-with-docs`, which loads `grilling` and `domain-modeling`, and requested:

> 这是一个new task，当前为docs landing阶段。你需创建task memory下的任务文档（spec+tickets）.
> - 在过去已经完成了qwen系列的opd测试，基于这些基础推进当前任务
> - 当前task涉及的opd实验需要涉及 Qwen3.5-4B + Qwen3.5-27B 和 Qwen3.5-4B + Qwen3.5-35B-A3B，可以并行推进它们的测试任务，共用一些基础模块
> - 使用glm-5.2数据集；当前架构使用的dataload的数据取用加载应保持与 steptron 的默认逻辑一致
> - 参考 /data/ycfeng/steptron/.worktrees/step3p6-replay-v1的task_2026-10-01_step3p6_single_teacher_bounded_replay_h200 的训练参数设置，使用其r256的设定逻辑，进行 full vs r256 的实验（只需要swe domain即可），每个update使用256个turn。
> - 一共有 2 * 2 =4个cell需要run
> - 学习率为2e-6，且同bank的连续训练次数为50次，总共训练200个updates；每50个updates进行一次最小代价的hf ckpt存储（save到codesign oss，不要存储其他权重）
> - benchmark采用与step3p6-replay-v1（task_2026-10-01_step3p6_single_teacher_bounded_replay_h200）的一致， avg@4，100题
> - 记录每个update（step）的kl数值，200个update共要记录200个kl数值；记录tis保留率（有多少toks被用于训练）
> - 对于某些长时间未返回的rollouts，不要死等（避免单个阻塞后面任务），timeout、await asyncio.sleep(0)等设定参考step3p6-replay-v1
> - 当某个ckpt保存好后，异步始其评测工作，完成后及时删除
> - 使用h200，<=许提交 56卡内不可抢占rjobs

## Authority and document ownership

- Current phase: **IMPLEMENTATION_IN_PROGRESS**. Documentation landing is complete; the user subsequently authorized implementation and parallel execution. Actual ticket completion is tracked in the plan and progress records.
- The explicit request for tickets authorizes local `tickets/NN-slug.md` documents. Use the existing local ticket template; publish no external issues.
- This task is separate from the completed A/B qualification and the unfinished C work in `../task_2026-11-06_qwen35_three_pairs/`. Historical artifacts and unrelated working-tree changes remain owned by their original tasks.
- D9 resolves the resource boundary as **56 H200 GPUs in non-preemptible RJobs across all of the user's submitted, nonterminal jobs**, including other tasks. This explicit request supersedes the older default 32-GPU ceiling; it does not transfer historical Step3p6 resource permissions.
- This file owns the raw request and actual user answers. [spec.md](spec.md) owns the executable experiment contract and explicitly marks unresolved fields. [plan.md](plan.md) owns the ticket dependency graph. [progress.md](progress.md) owns investigation and document-validation evidence.
- Recommendations, inherited source behavior, arithmetic deductions, and unanswered questions are not user decisions.

## Reference identities

- Miles worktree: `/data/ycfeng/sota-engine/miles`, branch `agent-opd`, inspected HEAD `9fb14ae2dc55da8ac7af9f4d9a99c5f891f089ce`.
- Replay reference worktree: `/data/ycfeng/steptron/.worktrees/step3p6-replay-v1`, inspected HEAD `08450c77b8674893cae6e662238af7240c76cdbd`.
- Reference task: `/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/task_memory/task_2026-10-01_step3p6_single_teacher_bounded_replay_h200`.
- Prior Qwen acceptance: `../task_2026-11-06_qwen35_three_pairs/summary.md`; tokenizer/data distinction: `../task_2026-11-08_qwen_tokenizer_opd_inventory/findings.md`.
- Reference documents have multiple dated overrides. Resolve current behavior against the latest actual request and code; do not inherit the historical 8-use schedule, 100-update budget, 500-question benchmark, or superseded checkpoint cadence by reading the original spec alone.

### D11 — [Original Request / Follow-up Amendment] 2026-11-08: replace training data

> big change：将当前数据集替换为：
> /data/ycfeng/paper-data/stepfun-swe-data/swe-oss-data.md中的 ## 2026 年 10 月 21 日交付实验使用的 sew数据集：复用 SWE-1003 的 0913 SFT 数据：DeepSWE resolved 轨迹，经过 garble filtering 和 datapipe 处理，位于
> /mnt/posttrain/hanqi/swe_data/sft/datapipe_stage2_rft_0913/mnt/posttrain/qidi/garble_filtered_sft_20260913/

This explicitly supersedes the original GLM-5.2 dataset selection for all four training cells. The requested delivery consists of eight ordered JSON sources; spec S3 owns their selection reference. Preserve the repeated `mnt/posttrain` components in the source path. Reading those requested source files is authorized; any generated cloud copy remains inside the existing personal namespace.

Retain the previously approved default Steptron loading requirement. Reopen Ticket01 for the replacement sources' identity, schema, native loader parity, Qwen rendering/length filtering and benchmark-overlap evidence. Prior GLM-5.2 input counts, overlap checks, training smokes and saved-bank capacity probes retain their actual provenance and cannot certify the replacement data. Existing model/math/evaluator evidence remains evidence for the implementation that was actually exercised. No formal cell has started. A future formal configuration must select the replacement sources after their acceptance.

## Interview decisions

### D1 — [Original Request / Follow-up Answer] 2026-11-08: valid subset after timeout

Question: “超时后不足256条有效turn时，本任务采用哪种规则？”

User selected: **“有效子集继续（推荐）”**.

The selected option states: “每步目标256；到期用已完成样本训练，r256固定复用实际bank，记录缺失与真实token数量。”

This explicitly relaxes exact 256 to a target of 256 when individual rollouts fail to return by the deadline. Seal the actual successful bank membership; replay that membership rather than refill, duplicate or relabel missing trajectories. Preserve actual per-update counts and missing-request evidence. The response does not approve an arbitrary minimum-success fraction or an empty/all-zero-supervision update; those policies must be resolved against the reference and remaining interview.

### D2 — [Original Request / Follow-up Answer] 2026-11-08: pre-TIS primary KL statistic

Question: “每个update的主KL曲线采用哪种统计口径？”

User selected: **“筛选前均值（推荐）”**.

The selected option states: “全部原始有效tokens上的当前学生−教师log-prob均值；TIS保留率另列，旧轨迹采样属性明确标注。”

The primary200-point series is the mean current-student minus frozen-teacher log probability on all original eligible target tokens before TIS. Retain the native post-TIS statistic in its existing logs under its own identity. No extra model forward is required merely to obtain the pre-TIS reduction. Replayed trajectories retain their original sampling distribution; the primary statistic is not relabeled as an exact fresh-policy KL.

**[Original Request / Follow-up Correction] 2026-11-08:** “修正：当前统计的kl实际指的是：RKL：KL(student‖teacher)；student 经常生成的内容，teacher 是否也倾向于生成？”

This explicitly identifies the target direction as reverse KL, student to teacher. The implementation's subtraction direction already agrees. The parent asked an unnecessary estimator-choice question referring to “fixed prefixes”; the user clarified the intended operation below rather than selecting either proposed option.

**[Original Request / Follow-up Clarification] 2026-11-08:** “我没有理解你说的。什么叫做固定前缀？前缀部分也要算入到rkl中吗？这是不允许的。应该用当前student来重新计算该completion的logprob来计算rkl”.

Decision: only original eligible **completion** tokens enter the numerator and denominator; all prompt/prefix and padding positions are excluded. Each update recomputes the current student's log-probabilities for that same stored completion, then compares the corresponding frozen teacher values before TIS. No importance weighting or extra current-policy sampling is introduced. The original D2 reduction remains the implemented statistic and the estimator-choice question is withdrawn. Replay results describe this fixed-completion sampled statistic, not an exact all-output current-policy KL expectation. The explicit formula and reporting contract remain owned by spec S4.

### Capacity repair authorization

**[Original Request / Follow-up Decision] 2026-11-08:** Asked whether to approve a minimal source patch to pinned Megatron that releases the previous scoring microbatch's completed logits before the next forward, with a same256-trajectory GPU before/after comparison, the user selected “批准源码修复（推荐）”.

Approved scope: move the existing PP1 schedule output-reference release outside its training-only branch, record the pinned dependency and source patch, and verify the unchanged workload on GPU before adopting the patch for formal runs. Existing parallelism, context/candidate budgets and training mathematics remain fixed for this comparison. The alternative TP4 route was not selected. This approval covers the controlled dependency source edit; it is not a native capacity PASS or permission for an unrelated allocator workaround.

### D3 — [Original Request / Follow-up Answer] 2026-11-08: research-based optimizer selection

Question offered the previously qualified Qwen Adam settings versus the reference Steptron Muon settings.

User answered: **“调研确认qwen3.5官方系列使用的优化器，采纳官方或者社区推荐”**.

This directs primary-source research and adoption of a supported official/community recommendation. It does **not** select either offered optimizer. Findings belong to [optimizer_research.md](optimizer_research.md); the resulting choice and evidence will be recorded here. Distinguish pretraining, SFT, adapter training and full-parameter OPD rather than treating a toolkit default as official Qwen disclosure.

**Research-based adoption under D3:** the primary adopted the Miles AdamW-semantic community recipe for full-parameter Qwen3.5 OPD after reviewing the research report and checking the local Qwen recipe, keeping the requested constant learning rate 2e-6 without warmup. Exact optimizer parameters are owned by [spec.md](spec.md#优化参数); evidence and its limits are in [optimizer_research.md](optimizer_research.md). No official original-training optimizer was established. The weight decay differs from the historical A/B runs, so this configuration needs new runtime acceptance. This selection implements the user's research-and-adopt direction, not a fabricated choice between the previous options.

### D4 — [Original Request / Follow-up Answer] 2026-11-08: Steptron two-level TIS

Question: “本任务的TIS采用哪套筛选与加权规则？”

User selected: **“Steptron双层筛选（推荐）”**.

The selected option states: “token比率[0.5,2]，回答几何平均比率[0.9897,1.001]；两层都通过才训练，保留权重为1。”

Adopt this same rule in all four cells. Current-student scoring is recomputed for every update; the behavior-policy log probabilities remain those of the original generation. This supersedes the previous Qwen qualification's token-only mask with retained importance-ratio weights. The current task must verify the adapted rule against the reference calculation, not cite the old QwenTIS qualification as proof.

### D5 — [Original Request / Follow-up Answer] 2026-11-08: use remaining 128K generation budget

Question: “训练rollout的回答长度采用哪种规则？”

User selected: **“剩余128K额度（推荐）”**.

The selected option states: “max_new_tokens=131072−实际prompt长度，按参考逻辑生成，保留真实终止原因。”

Keep complete prompt history; reject a prompt whose token count is at least 131072, following the default loader. Do not impose the previous Qwen 8192-token response cap or reserve 8192 tokens by excluding otherwise valid long prompts. Record real EOS/length/timeout outcomes.

### D6 — [Original Request / Follow-up Answer] 2026-11-08: 1800 s / 90% acquisition rule

Question: “是否采用参考的1800秒收集截止、至少231/256条有效样本规则？不足下限时结束当前cell此次运行并保留证据。”

User selected: **“采用参考规则（推荐）”**.

The selected option states: “1800秒内至少231条；231–256条封存继续，少于231条结束该次运行，其他cell继续。”

Freeze the acquisition deadline/minimum as 1800 s and 0.9, with `ceil(256*0.9)=231`. Record the actual collection start and deadline, including pending/in-flight identities. This concerns acquisition of a new bank, not a new 1800 s timer on each replay visit, and not the independent SWE agent/evaluation deadlines. The new Qwen load must be measured before formal submission; poor throughput is not authorization to silently change the threshold or deadline.

### D7 — [Original Request / Follow-up Answer] 2026-11-08: stop on zero TIS survivors

Question: “一个已封存bank在某次update被TIS全部筛掉时，如何处理？”

User selected: **“结束当前cell”**.

The selected option states: “首次全部被筛掉就结束该次运行，保存证据，其他cell继续。”

Stop the affected cell's current attempt at the first globally zero-survivor TIS batch. Preserve its actual completed updates and the triggering batch's pre-TIS KL, original-token count and mask evidence; do not count a synthetic successful update, change the bank early, relax TIS or silently restart. This is an explicitly approved training-data validity stop, not a stop based solely on an auxiliary observer's failure. Other healthy cells continue. The cell remains incomplete against the planned 200 updates until separately resolved.

### D8 — [Original Request / Follow-up Answer] 2026-11-08: shared original-student baseline

Question: “是否增加四个cell共用的一次原始Qwen3.5-4B SWE基线评测？”

User selected: **“增加一次基线（推荐）”**.

The selected option states: “同一100题×4，共新增400 attempts；不复制或删除原始权重。”

Add one shared baseline using the same original 4B source, selected 100 tasks, four seeds, serving precision/template and harness as the trained checkpoints. Total planned benchmark volume becomes 17 points / 6,800 logical attempts; generated training HFs remain 16. The baseline's complete score does not gate independent healthy training once the evaluator's native capability has been verified. Source weights remain protected.

### D9 — [Original Request / Follow-up Answer] 2026-11-08: 56 H200 GPU personal aggregate

The question contrasted a personal aggregate limit with a new-task-only limit, recommending the personal aggregate. The interactive tool was interrupted and supplied no decision. The user subsequently wrote: **“确认，继续”**.

The primary explicitly acknowledged that confirmation as the recommended rule: all personal submitted, nonterminal non-preemptible H200 commitments together must remain at or below 56, including other tasks and every role of this task. Count Pending/Starting/Running requested GPUs, not only active CUDA processes. This confirmation continues documentation landing; no implementation or GPU action was performed under it.

#### D9 amendment — [Original Request / Follow-up Answer] 2026-11-08

After the personal aggregate reached 72 GPUs and denied a one-GPU check, the user initially selected **“等待释放（推荐）”**. The user subsequently replaced that waiting decision with:

> 关于用卡规则：在hk时间11.9日凌晨5点之前，允许当前task使用独立的64卡内的gpus资源（不可抢占rjobs），超过数量则通过 可抢占方式提交

The primary asked how to handle admitted non-preemptible jobs still running at Hong Kong 2026-11-09 05:00. The user selected **“继续完成”**, whose description was **“此前获准的作业继续运行；05:00后新提交恢复原D9准入规则。”**

The active policy is specified in [spec S7](spec.md#s7-gpu-与执行准备). This exception counts this task's nonterminal training, teacher, rollout, evaluation and auxiliary GPU commitments independently of other tasks. Whole RJobs that would exceed the temporary non-preemptible ceiling use preemptible submission; a paired job is not split across preemption classes. At expiry, already admitted jobs continue and new admissions return to the original personal aggregate rule.

### D10 — [Original Request / Follow-up Answer] 2026-11-08: preserve incomplete evaluation and bounded recovery

Question: “是否采用‘未完成评测保留HF，只补缺失attempt；同一72小时截止到期后停止该评测并报告’的规则？”

User selected: **“采用此规则（推荐）”**.

The selected option states: “保留HF与已完成结果；只补同题同seed缺失项，不续期；完整评测且reader退出后删除HF。”

Preserve the immutable HF and completed-attempt ledger after incomplete evaluation. After diagnosing/remedying an infrastructure failure, restore only missing slots under the original 72-hour absolute evaluation deadline; restarting does not extend it. At expiry, stop the affected evaluation, preserve its HF/results and report incompleteness while healthy training continues. Complete model failures are scored outcomes, not missing slots to reroll. The shared original-model baseline uses the same ledger/deadline but never owns source-weight deletion.

## Documentation freeze — [Original Request / Follow-up Answer] 2026-11-08

Question: “是否确认这版spec和9张tickets，结束本次docs landing，作为后续实施依据？”

User selected: **“确认冻结（推荐）”**.

The selected option states: “认可已记录的D1–D10及源码继承契约，完成文档归档和提交。”

The specification and dependency graph are now frozen as the documentation deliverable. The whole-document confirmation includes the stated original 4B initialization, default input/seed/template behavior, existing Miles OPD surrogate and original-token denominator, benchmark call configuration and output namespace. Later changes to scientific scope or recorded decisions require an explicit update; implementation must verify its assigned runtime prerequisites rather than treating this confirmation as a runtime PASS.

The frozen contract's runtime prerequisites are listed in [spec.md](spec.md#freeze-and-implementation-prerequisites).

## Execution authorization — [Original Request / Follow-up Answer] 2026-11-08

Following the landing review, the user wrote: **“确认，继续，完成后开始按照tickets/spec并行执行任务”** and subsequently repeated **“continue”**. The approved documentation fixes were committed as `df66bf4b`. This authorizes ordinary implementation, verification, and execution of the frozen tickets, including their approved GPU runs. Scientific decisions, budgets, and prerequisite acceptance remain as frozen.

## Documentation acceptance criteria

1. A source-backed spec covers the four experiment cells, Steptron-compatible input loading, bank/update semantics, optimizer and objective, exact KL/TIS observations, checkpoint/evaluation/deletion lifecycle, resources, and failure behavior.
2. Each implementation/execution ticket is a verifiable vertical slice with acceptance criteria and explicit blocking edges; the two teacher pairs and four formal cells have independent execution paths after shared prerequisites.
3. Unanswered scientific or operational choices remain visibly unresolved. No future implementation or runtime PASS is inferred from historical qualification.
4. Local links, requirement coverage, arithmetic and the ticket dependency graph are checked. A final documentation freeze requires the user's explicit confirmation.
