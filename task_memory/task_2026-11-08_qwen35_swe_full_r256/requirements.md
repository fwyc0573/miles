## Modification History

| Date | Change |
| --- | --- |
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

- Current phase: **DOCS_LANDING_COMPLETE**. The user explicitly confirmed the specification and nine local tickets as the basis for subsequent implementation. This completed task delivers documentation; runtime tickets have not been executed.
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

## Documentation acceptance

1. A source-backed spec covers the four experiment cells, Steptron-compatible input loading, bank/update semantics, optimizer and objective, exact KL/TIS observations, checkpoint/evaluation/deletion lifecycle, resources, and failure behavior.
2. Each implementation/execution ticket is a verifiable vertical slice with acceptance criteria and explicit blocking edges; the two teacher pairs and four formal cells have independent execution paths after shared prerequisites.
3. Unanswered scientific or operational choices remain visibly unresolved. No future implementation or runtime PASS is inferred from historical qualification.
4. Local links, requirement coverage, arithmetic and the ticket dependency graph are checked. A final documentation freeze requires the user's explicit confirmation.
