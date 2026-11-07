## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Record requested full-task review and repair, pinned to5c2e4463...69f3cda5; existing run budgets remain unchanged. |
| 2026-11-07 | Record D19: delegate prompt cleanup of obsolete current-task codesign OSS artifacts with measured space reclamation. |
| 2026-11-07 | Record D18: move pairs A/B to H200 with a session/task ceiling of32 concurrent non-preemptible H200 GPUs; retain C on H800 and all existing workload budgets. |
| 2026-11-07 | Record D17: after B publishes one update then fails with output-projection GPU OOM, approve one fresh100-step B restart after capacity repair. |
| 2026-11-07 | Record D16: raise only C student's effective host-memory limit to1500GiB, preserving normal parameter backups and the approved fresh100-step budget. |
| 2026-11-07 | Record D15: restart C from initial weights for a complete 100-step run after repairs; retain the discarded failed step in historical accounting. |
| 2026-11-06 | Record authorized v2 guard repair, local runtime-artifact cleanup, and the workspace's explicit read-only model-source exceptions. |
| 2026-11-06 | Confirm D14 execution baseline/shared understanding and explicit removal of the old Git index lock before the task-document commit. |
| 2026-11-06 | Confirm D13: deliver a text-only HF student model with matching configuration/names and real text-inference reload. |
| 2026-11-06 | Confirm D11 length-balanced task-group-isolated monitoring and D12 token-level TIS mask settings. |
| 2026-11-06 | Confirm D10: enable new-generation thinking for all three pairs and every training/monitoring sample. |
| 2026-11-06 | Resume the Miles task and confirm D9: 100 planned updates with eight completions each, plus 24 held-out monitoring prefixes at six checkpoints. |
| 2026-11-06 | Revise D4 to preserve_thinking=True by default across real-user boundaries; retain user control and completion-only D6 supervision. |
| 2026-11-06 | Confirm D8 numerical acceptance: pre-TIS same-version token-weighted absolute logprob error at most 0.03, with length coverage and unresolved-defect exclusions. |
| 2026-11-06 | Confirm D7: 131,072 total tokens, up to 8,192 completion tokens and no truncation of selected prefixes; advance to numerical acceptance. |
| 2026-11-06 | Select temporary colocation, the last-real-user history rule, and completion-only loss; supersede the keep/drop interpretation and historical-loss question. |
| 2026-11-06 | Revise D4 to a user-controlled history-reasoning input switch; keep the prior retention preference as the provisional default. |
| 2026-11-06 | Require historical reasoning in every prefix (D4), preserve the supervision clause verbatim, and authorize evidence-based deployment selection (D5). |
| 2026-11-06 | Record the request for a concrete prefix example; distinguish conditioning history from supervised completion. |
| 2026-11-06 | Accept original GLM histories with fresh single-turn student OPD (D3); record the requested Qwen format verification and unresolved history policy. |
| 2026-11-06 | Confirm dense-student routing replay as not applicable while retaining the three-pair matrix and other required features. |
| 2026-11-06 | Confirm current Miles as the implementation framework; supersede the immediately corrected verl wording. |
| 2026-11-06 | Record the original request and open the documentation-first design interview. |

# Requirements

## Original request

[Original Request]

> $grill-with-docs 创建task，先落地docs。核心为验证以下comb：
> - Qwen3.5-4B + Qwen3.5-27B
> - Qwen3.5-4B + Qwen3.5-35B-A3B
> - Qwen3.5-27B + Qwen3.5-397B-A17B
>
> 具体要求：
> - 并行推进3个comb的steptron的测试验证，使用h800推进；上述模型已经在oss中（/data/ycfeng/stepfun-env-handbook/resource_analysis）
> - 较小的作为student，较大的作为teacher
> - 训推一致性的验证和检查和修复是核心重点(参考/data/ycfeng/stepfun-env-handbook/resource_analysis)
> - 开启参数（如果有一致语义功能，我 当前等描述使用的是steptron的开关）：r3（route replay）、tis打开、开启 nccl 直传（weight sync）、开启 enable total token loss
> - 验证训练的有效性：关注loss、norm grad的收敛情况，可否保存hf ckpt到codesign oss（无需保存模型和优化器的其他权重参数）
> - 如果出现了普遍性质的架构支持性缺失，先具体定位这些缺失模块和依据，交给我决策。

[Original Request] The supplied `grill-with-docs` skill invokes `grilling` and `domain-modeling`.

## Framework decision — confirmed

[Original Request] First reply, immediately corrected by the user:

> A；必须在当前verl实现当前task，而不是使用steptron中实现，注意区别

[Original Request] Authoritative correction:

> A；必须在当前miles实现当前task，而不是使用steptron中实现，注意区别

**Decision D1:** Implement, diagnose, repair and validate all three pairs in the current Miles repository. Steptron is a reference for requested feature semantics and acceptance evidence only. Do not implement this task in Steptron or verl, switch to either framework, or count their runtime results as Miles qualification. The corrected wording supersedes `verl` in the preceding message. This answers the framework question; the remaining interview decisions are still open.

## Routing-replay decision — confirmed

[Original Request] Reply to the proposal to record all three student R3 checks as not applicable and preserve the requested model matrix:

> 确认，继续

**Decision D2:** Keep pairs A, B and C unchanged. Record student routing replay as `N/A: dense student has no MoE routing decisions` for every pair; do not enable a replay flag that has no applicable student router. MoE teacher routing does not provide routes for the dense student's training pass. TIS, NCCL direct weight synchronization and total-token loss normalization remain required and must be verified. This decision does not qualify R3 on an MoE student or authorize adding one. Continue the documentation interview with the learning workload; runtime execution still depends on the remaining material decisions.

## Learning-workload decision — confirmed

[Original Request] Reply to the original GLM-5.2 SWE history / fresh single-turn OPD proposal:

> 同意采用。但是你需要确认的是 该数据集 和 qwen的 chat template 是否一致？是否需要提前的format格式转换？

**Decision D3:** Use original GLM-5.2 SWE training histories as context. Each current student freshly generates the next assistant turn; its assigned teacher scores those actual generated token IDs. The old target completion remains provenance/analysis metadata and is not the new training target. Use the same selected source identities across the three pairs. This is single-turn OPD, not a full live tool-execution episode or fixed-old-completion training. D4/D6 resolve history rendering and target scope, D7 fixes context/response limits, D9 fixes the first-round update budget, D10 enables new thinking and D11 defines population selection; exact eligible source identities remain to be frozen.

**Requested verification:** Establish whether the structured source is compatible with Qwen's actual chat template, identify necessary format conversion, and distinguish CPU formatting evidence from full-corpus and runtime qualification. Results are in the [format test report](test_report_2026-11-06_qwen_format.md). The report does not grant approval to change Qwen history semantics.

[Original Request] Follow-up clarification request:

> 我没有理解你当前的提问。模型输入的内容是否指的是训练使用的前缀？给出一个具体的case来帮助我理解不同方案的区别，和对模型训练造成的直接影响。

Baseline explained before D4: the history policy changes the conditioning prefix shared by student generation, teacher scoring and the matching student training forward. Rendering alone does not add old reasoning tokens to the completion loss. No omission was observed in the four actual single-user snapshots. The latest detailed clarification below is authoritative over earlier preservation interpretations.

## Historical reasoning — user-controlled preserve-all default

[Original Request]

> 必须保证前缀部分包含历史reasoning，该部分的监督不允许省略。继续。

[Original Request] Earlier update requesting user control:

> 更新：前缀中的thinking/reasoning是否保留在输入应该作为一个开关（可供我控制，不要将其写死）

[Original Request] Earlier clarification of deployment, history policy and supervision; its history policy is superseded below, while deployment and completion-only supervision remain valid:

> 1.暂时采用共置方案。
> 2.对于之前提到的reasoning/thinking是否保留问题，具体来说，当前应该使用的reasoning是否剔除的规则应该遵循和 /data/ycfeng/steptron/.worktrees/behavior-turn-replay-step3p6 的设定一致：最后一条真实 user 消息之后的历史 assistant reasoning，此时保留，作为上下文；最后一条真实 user 消息之前的历史 assistant reasoning，此时在序列化时剔除。 更加具体一些：
> 举一个示意例子：模型正在修复代码，我们选择它收到测试结果后的那次回复做训练。构造的样本是：
>
> 【输入前缀】
>
> user:
> 修复 parser.py 中的解析错误。
>
> assistant:
> <think>
> 先运行测试，确认错误发生在哪个输入上。
> </think>
> 调用工具：运行测试。
>
> tool:
> 测试失败：空字符串输入触发 IndexError。
>
> assistant:
> <think>
>
> 【本次训练的 completion】
>
> 根据测试结果，需要在访问第一个字符之前检查空字符串。
> </think>
> 调用工具：修改 parser.py，添加空字符串检查。
>
> 这个例子中：
>
> - “先运行测试，确认错误发生在哪个输入上。”会保留在输入前缀中。 模型生成下一次回复时能看到这段历史 thinking。
> - “根据测试结果，需要……”属于这次选中 turn 的 completion。 它参与训练的 loss 选择，之后仍受 TIS 筛选。
> - 前缀末尾的 <think> 只是本次回复的起始标记；本次回复的 reasoning 正文属于 completion。
>
> 我之前说的“最后一条真实 user 消息之后”，在这个例子里，就是从 “修复 parser.py 中的解析错误” 这条提问开始，到当前训练位置之间的消息。中间的工具返回不会开始一个新的 user 问题，所以此前 assistant 的 thinking 会保留。
>
> 只有出现另一条新的 user 提问，例如用户随后说 “接下来修改 README”，原生模板才会把这条新提问之前的 assistant reasoning 剔除。这条剔除规则取决于前缀中的消息结构，与 single-turn 训练本身无关。
> 3.前缀部分无需参与loss部分（只根据completion产生监督）

[Original Request] Latest authoritative update:

> 【更新】再次更新当前使用的reasoning前缀设定，将这条设定作为默认使用的traj前缀设定：应对应steptron中的traj的前缀默认设置 preserve_thinking=True。默认保留历史 reasoning，后续出现真实 user 消息也不会触发剔除

**Decision D4, latest authoritative revision:** Default trajectory-prefix rendering to **`preserve_thinking=True`**, preserving all historical assistant reasoning, including reasoning before later real user messages. A new real user message does not trigger removal under this default. This supersedes the prior last-real-user omission policy as the task default. Keep original source metadata, ordinary assistant text, tool interactions and user control through existing Miles Qwen3.5 fixed-template settings. An explicit `False` override remains available for native last-real-user omission; do not add a separate all-history keep/drop transformation. Input rendering, new-generation thinking mode and loss masks remain separate settings. Generation, teacher scoring and training must use the same final prefix IDs. Recount actual lengths under the selected policy while preserving D7's limits and no-prefix-truncation rule.

**Decision D6 — loss scope confirmed:** Prefix tokens, including retained historical reasoning and the final assistant/`<think>` generation marker, have no direct target loss. Only the selected fresh completion supplies supervised target positions. Its newly generated reasoning body, closing tags and other eligible completion tokens remain subject to the actual completion mask and TIS. Do not add historical SFT/KD loss or a mixture coefficient. This supersedes the earlier ambiguous supervision clause; do not ask that question again.

## Deployment selection — research and choice authorized

[Original Request]

> 补充：- 在具体的训推架构部署模式选择上，允许采用更成熟的训推方案（共置或者分离皆可）；具体的，调研当前架构的社区和官方docs，查看哪一种方案更加成熟和完善。

**Decision D5, revised by the explicit colocation instruction above:** Use colocated student Megatron training and student SGLang rollout for the current phase. Their GPUs are time-shared through the native offload/wake-up lifecycle. Keep the differently sized/architected frozen teacher in an independent SGLang allocation. The original deployment research remains evidence, but its separated-layout recommendation is superseded. Current Miles colocation selects CUDA IPC for weight updates; record that transport honestly and defer the original NCCL-direct qualification during this temporary phase. Do not claim IPC satisfies NCCL, permanently waive the original requirement, or modify core protocol selection merely to force NCCL into colocation. H800, the three exact pairs, TIS, total-token loss and HF-only output remain required.

## Context budget — confirmed

[Original Request] Reply to the proposal “128K 总长、8K completion、入选前缀不截断”:

> 确认，继续

**Decision D7:** Use a maximum combined prefix/completion length of **131,072 tokens**, with up to **8,192 newly generated completion tokens**, for the first validation phase. Preserve each selected prefix in full after D4 rendering; do not truncate history to fit. Reserving the full response budget makes the maximum selected rendered prefix 122,880 tokens. Recount the actual source population with the selected Qwen tokenizer/template, record over-budget exclusions and retain identical selected source identities across pairs. Include shorter inputs for diagnosis and long inputs for coverage. This approves the workload limits, not a claim of H800 capacity, a particular GPU topology, sample count or successful model execution.

## Numerical consistency acceptance — confirmed

[Original Request] Reply to the proposed rule “筛选前平均绝对 logprob 差 ≤ 0.03，按长度分别检查，并排除未修复实现错误”:

> 确认，继续

**Decision D8:** For each pair independently, compare the same student's training and inference probabilities under the same consumed weight version, prefix/completion token IDs and probability definition. Before TIS rejection, require the global token-weighted mean absolute logprob difference to be **<= 0.03**, both overall and in every populated short/medium/long prefix stratum. Freeze the input identities and stratum boundaries before measurement; missing required coverage is INCOMPLETE. Check initial weights and updated weights, including the final published update. Keep decode-time and same-token inference-prefill measurements separate.

Report p95/p99/max, both declared K3 directions, token positions, missing values and nonfinite counts from the original valid completion population. An identified unresolved token, template, mask, version or numerical implementation defect prevents PASS even when the mean passes. The accepted 0.03 threshold is task-specific, not a universal guarantee, and must not be relaxed based on observed residuals or more aggressive TIS rejection. Verified threshold misses are FAIL; absent or invalid evidence is INCOMPLETE. Auxiliary verdicts do not authorize stopping healthy large GPU runs. Teacher/student learning divergence and cross-version policy staleness remain distinct from this same-student numerical check.

## First-round training budget — confirmed

[Original Request] Resume instruction:

> resume当前qwen测试task，按已有spec和tickets，继续推进执行。以下的最新的反馈的提示信息，供你参考：
> 继续当前qwen任务执行：接下来推进尚未确定的首轮训练规模。

The supplied reference restated the pending 100-step/eight-completion/24-prefix proposal. Repository inspection identifies this Miles task as the matching task; it currently uses P0–P4 in plan.md and has no tickets directory. Neighboring verl tickets belong to a different task and do not change D1.

[Original Request] Answer to the explicit confirmation question, covering 100 planned update steps per pair, eight fresh completions per step, 24 fixed monitoring prefixes at baseline and steps 20/40/60/80/100, actual successful-update accounting and no automatic extension:

> 确认该规模 (Recommended)

**Decision D9:** For each pair, budget **100 planned optimizer steps**, each consuming **eight freshly generated training completions**, with one completion per selected prefix and one rollout/global batch per planned update. Reserve **24 fixed monitoring prefixes** outside optimization. Generate a fresh student completion and score it with the assigned frozen teacher at baseline and after planned steps **20, 40, 60, 80 and 100**. The planned totals are **800 training completions and 144 monitoring completions per pair** (2,400 and 432 across all three pairs). Report actual successful/skipped updates and consumed/published weight versions; do not silently equate schedule position with a successful update or extend the budget until convergence. Monitoring outputs never enter training. This confirms the finite workload budget, not convergence, exact split identities/stratum allocation, GPU topology, or the remaining shared-understanding decision.

## New-generation thinking — confirmed

[Original Request] Answer to whether all three pairs should enable thinking for newly generated training and fixed-monitoring completions:

> 统一开启 (Recommended)

**Decision D10:** Set `enable_thinking=True` uniformly for fresh training and monitoring generation across all three pairs. Do not derive this value from the historical target's category or `has_thinking`. The fresh reasoning body and subsequent reply share D7's 8,192-token completion cap and D6's completion-only target mask/TIS semantics. D4 independently preserves historical reasoning in the prefix. Existing template/kwargs controls own these two settings.

## Training/monitoring population — confirmed selection rule

[Original Request] Answer to short/medium/long monitoring with eight prefixes each, whole-task-group exclusion from training, identical source identities across pairs, and shuffled cycling through remaining eligible training prefixes with fresh completions:

> 采用该划分 (Recommended)

**Decision D11:** Render and count the actual source using D4/D10. Select eight fixed monitoring prefixes in each Qwen-token length interval `(0, 32768]`, `(32768, 65536]` and `(65536, 122880]`. Reserve their complete task groups, using verified source `group_id` membership, outside training; retain all inherited evaluation exclusions. Freeze the same source identities across A/B/C. Shuffle the remaining eligible training prefixes and cycle when needed, generating a fresh completion on every use. Do not truncate prefixes or silently fill missing length coverage with another stratum. Actual source identities, complete-group membership, eligibility counts and sufficient coverage remain prerequisites; an unmet selection rule returns for decision and is reported INCOMPLETE.

## TIS settings — confirmed

[Original Request] Answer to token-level TIS mask with inclusive bounds `[0.5, 2]`, without additional sequence rejection or batch weight normalization:

> 确认该设置 (Recommended)

**Decision D12:** Enable the existing custom MIS path with `tis_level=token`, `tis_mode=mask`, `tis_lower_bound=0.5`, `tis_upper_bound=2.0`, `use_rs=False` and `tis_batch_normalize=False`. Within the inclusive ratio interval retain the token and apply its importance weight; outside it remove that token's training contribution. Preserve the original eligible completion population for D8 numerical acceptance and report TIS retention separately. Verify the native original-token global denominator; do not substitute a survivor-token average, silently add a sequence veto or adjust the accepted D8 threshold.

## HF output scope — text-only model selected

[Original Request] The export investigation presented complete-original-model packaging versus explicitly text-only HF delivery. The user selected:

> 仅纯文本 HF 模型

The selected option stated: “明确只交付文本 decoder；相应转换配置和权重名，并验证文本推理重载。”

**Decision D13:** Deliver the updated student's **text-only HF model**, with configuration, architecture declaration, tensor names and tokenizer assets matching the selected text-model loader, and verify actual text-inference reload. Do not label a decoder-only tensor set with an incompatible full multimodal configuration. Do not implement frozen-vision/full-VLM reconstruction merely to satisfy the rejected full-package proposal. This narrows the export artifact, not the requested full-depth student/teacher training identities. Keep R5's HF-only storage requirement and exclude native model/optimizer checkpoints. Exact text-loader compatibility, save cadence, retention and output paths still require freezing or runtime verification; the alternative choice did not automatically accept the recommended option's full-package repair or final-only cadence.

## Fixed execution baseline and shared understanding — confirmed

[Original Request] Answer to ending the design interview and entering implementation/prerequisite validation under D1–D13 plus the presented fixed first-round baseline, while GPU execution still requires personal assets, runtime and a verified H800 resource plan:

> 确认，推进执行 (Recommended)

**Decision D14:** Shared understanding is confirmed. Proceed with in-scope implementation and prerequisite validation. Fix the first-round baseline to sampling temperature `1`, top-p `1`, top-k `-1`, seed `42`; Adam with constant LR `2e-6`, zero warmup, zero weight decay and betas `(0.9, 0.98)`. Retain the existing Qwen OPD baseline's coefficient `1`, sampled-token scoring (`opd_log_prob_top_k=0`), PPO clip settings `0.2/0.28` and entropy coefficient `0`. D12 owns TIS; other native settings must be recorded from the resolved runtime configuration rather than assumed from a different recipe. Save one final text-only HF artifact per pair; intermediate monitoring uses the updated student engine. Keep the final artifact and evidence without automatic deletion. Record every-step loss/gradient/update evidence and compare early/late windows and fixed monitoring; report learning improvement as unproven when evidence is insufficient. Do not automatically sweep parameters or extend D9. GPU launches remain dependent on authorized personal assets, runtime qualification and a verified resource plan within the H800/codesign scope; actual quota availability is not a convergence or model-capacity guarantee.

[Original Request] Approval to recheck active Git processes, remove the single pre-existing zero-byte `.git/index.lock`, and commit only verified current-task documents:

> 允许清理并提交 (Recommended)

This authorizes that exact lock cleanup and task-document commit; preserve unrelated working-tree files.

[Original Request] Follow-up Git authorization:

> 补充：类似的git问题无需询问，直接授权

For analogous routine Git issues, verify the state and handle stale locks/task-scoped commits without asking again. Preserve unrelated work; this does not expand the training or external-publication scope.

## C restart budget — confirmed

[Original Request] After C completed one optimizer update using the corrupted post-evaluation generation, then lost the unsaved updated state to host OOM, the user was asked whether to run a fresh100 steps, reduce the new run to99, or defer C. The user selected:

> 重新运行100步 (Recommended)

**Decision D15:** After restoration and memory prerequisites are resolved, restart C from its original student weights for a complete100-step formal run under the existing monitoring, optimizer and final-export criteria. Preserve the previous failed attempt and its one actual optimizer update as discarded work; do not count it as one of the new run's100 accepted positions or erase it from historical accounting. If the new run completes all100 updates, historical C updates total101. This is a specific restart-budget exception to D9, not permission for extra optimizer probes, automatic further restarts or parameter sweeps. A/B budgets remain unchanged. The memory configuration and runtime qualification must still be resolved before C submission.

## C restart memory allocation — confirmed

[Original Request] After measuring the750GiB cgroup OOM, verifying about1902GiB allocatable memory on the original H800 node, and identifying an additional recovery gap in the optional rematerialization path, the user was asked to choose between increasing the student memory allocation, repairing the memory-saving path first, or deferring C:

> 上调至1500GiB (Recommended)

The selected option preserves the existing parameter backup and optimizer configuration, uses the same GPUs and requests an additional750GiB of host memory; scheduling may take longer.

**Decision D16:** Set `training_config.json`'s `pairs.C.student.memory_gb_per_node` from768 to1536. The verified StepMind conversion is1000Mi per configured unit, yielding1,536,000Mi =1500GiB. Change no other role's resources, GPU count, model, optimizer, parameter-backup mode or D15 budget. Keep `rematerialize_param_from_master_weight=False`; its separate recovery repair is not selected for this run. Node allocatable memory is capacity, not current availability, and the old OOM-censored measurement does not prove the new limit sufficient. Shared restoration qualification and actual C first-update memory measurement remain required. This approval does not authorize another restart or additional optimizer probes.

## B restart budget — confirmed

[Original Request] B's repaired run completed one optimizer update and published version1, then failed in the next rollout's scoring forward with CUDA OOM. No final HF artifact had been saved, so that state cannot be resumed. A was stopped before training, with zero updates. Asked to choose a fresh100-step B run, a new99-step run from initial weights with revised acceptance, or deferral, the user selected:

> 重新跑100步 (Recommended)

**Decision D17:** After resolving the observed capacity issue, restart B from its original student weights for one complete100-step formal run with the existing monitoring, optimizer and final-export criteria. Retain the previous run's one actual optimizer update and version1 publication as discarded historical work; it is not one of the new run's100 positions. Historical B updates total101 if every new update succeeds. This specific exception does not authorize further automatic restarts, extra optimizer probes or parameter sweeps. A retains its existing100-step budget; C retains D15/D16. The budget decision does not select a memory implementation or certify capacity.

## A/B H200 execution — confirmed

[Original Request]

> 由于h800的调度资源限制问题，将task中3个comb中的前2个combs（不含397b的）提交到 h200集群上测试验证，允许本session/task提交 32卡内的不可抢占 rjobs

**Decision D18:** Run pairs A/B on H200, using the handbook's H200/step_main pairing and no more than32 concurrent non-preemptible H200 GPUs for this session/task, including auxiliary allocations. Keep each pair's existing8-GPU student and2-GPU teacher topology, for20 H200 GPUs across both formal jobs. `training_config_h200.json` is the frozen A/B launch manifest derived from the existing H800 configuration; its hardware tag, charged group and capacity ceiling change, and it excludes C. C retains its existing H800/codesign submission and D15/D16 allocation. A retains100 planned positions; B uses the already-approved D17 fresh100. Preserve the selected model identities, population, optimizer, TP, numerical criteria, context, monitoring and HF-only output. This hardware change supersedes the original all-H800 requirement for A/B; it does not certify H200 capacity or authorize extra optimizer probes, further restarts, preemptible work or numerical relaxation. Verify actual H200 runtime and D8 in the submitted runs. The output-lifetime investigation remains independent evidence; its optional diagnostic work does not block this explicitly selected hardware migration.

## Current-task OSS cleanup — authorized

[Original Request]

> ps：及时分派子agent清理在当前task生成的保存在codesign oss上的运行产物，磁盘空间快要达到上限。

**Decision D19:** Delegate timely cleanup of obsolete generated cloud artifacts belonging to this task. Restrict deletion to the task's personal codesign output tree, `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs` (the authorized SSH mount maps it to `/mnt/ws-jfs/ycfeng/miles-qwen35-three-pairs`). Verify job ownership and terminal status, preserve active A/B/C paths, frozen inputs/model assets and minimum irreplaceable acceptance/RCA evidence, then remove obsolete regenerable large files. Record exact targets, sizes, retained evidence and measured remaining usage; distinguish logical deletion from physical quota reclamation. This authorizes scoped destructive cleanup, not unrelated task/model deletion or a blanket purge of shared `.trash`. Continue healthy formal jobs concurrently.

## Post-acceptance review and repair — requested

[Original Request]

> 进入一轮review，修复错误和遗漏

[Original Request] The user selected the full-task review scope rather than only the latest acceptance commit:

> 本 task 全量 (Recommended)

Review all task implementation and acceptance changes from `5c2e44635298675167c7c55e067dcb294f9e9fa9` to `69f3cda52dd7ea59202f560fedc6cbcfe1679ad9`. Fix evidence-backed errors and omissions, preserving unrelated work and original runtime receipts. This requests ordinary in-scope corrections and verification; it does not change D9/D15/D17 optimizer budgets, enable deferred memory features, authorize external publication or restart formal training.

## Execution support authorizations

[Original Request] After the false-positive v2 tool guard was diagnosed and its local repair was requested:

> 授权，继续

The authorization covers the local v2 plugin repair and verification while preserving its protected-skill restrictions. It does not authorize changes to v1 or reading the protected skill.

[Original Request] During P2 implementation:

> ps：及时分派子agent清理在当前机器生成的运行产物，当前磁盘空间快要达到上限。

Delegate local generated-artifact cleanup promptly. Preserve active work, source/model/data assets and necessary evidence; verify ownership, completion and retained results before removing generated outputs from older tasks.

The updated workspace instruction explicitly permits read-only model access to these three sources for this Qwen task:

- `/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-27B/model`
- `/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-35B-A3B/model`
- `/mnt/codesign-exp/pj_dflash_edge_i-pengyajuan/models/Qwen3.5-397B-A17B`

These are narrow exceptions to the former personal-only read restriction. All cloud writes remain under `/mnt/codesign-exp/ycfeng`; no other shared cloud directories are authorized. Mount posttrain through Python RJobBackend as `juicefs+s3://aliyun-sh/posttrain:/mnt/posttrain`, as verified by the local inventory and existing Steptron recipes. Existing personal Qwen3.5-4B and GLM source assets remain the inputs for their respective roles.

## Explicit requirements

| ID | Requirement |
| --- | --- |
| R1 | Create the task and documents before implementation or GPU execution; interview one decision at a time. |
| R2 | Validate all three full model pairs independently and advance their ready work concurrently: A/B on H200 under D18, C on H800. Smaller model is student, larger model is frozen teacher. |
| R3 | Make student training/inference consistency diagnosis and root-cause repair the central objective; apply D8's accepted numerical rule. |
| R4 | Student route replay is not applicable under D2. Enable and verify TIS, actual native student weight synchronization and global total-token loss normalization. Current D5 colocation uses CUDA IPC; original NCCL-direct qualification is deferred and must not be reported as passed. |
| R5 | Measure and plot training loss and gradient norm, assess learning behavior, and save a usable student HF checkpoint to personal codesign storage without additional native model or optimizer checkpoints. |
| R6 | Identify general architecture support gaps by exact module, symbol and evidence; return material architecture decisions to the user before implementing them. |
| R7 | Apply D4's preserve_thinking=True default across real-user boundaries with explicit user control, and verify completion-only target loss and TIS under D6. |
| R8 | Apply D7's total/response limits, preserve complete selected prefixes and validate actual Qwen lengths before runtime allocation. |

## Pair identity

| Pair | Student | Teacher |
| --- | --- | --- |
| A | Qwen3.5-4B | Qwen3.5-27B |
| B | Qwen3.5-4B | Qwen3.5-35B-A3B |
| C | Qwen3.5-27B | Qwen3.5-397B-A17B |

No Base, quantized, reduced-layer or different model substitution is approved. A and B have separate optimizer states and output paths despite sharing the initial student asset.

## Scope and authority

- This is a new task. Prior warmup choices such as 20 updates, four seeds, learning rate, cleanup, benchmark and GitHub push do not become decisions for this task. The GLM-5.2 source and fresh single-turn objective are now explicitly accepted under D3; old selection and thinking defaults remain unaccepted.
- The current Miles workspace (`agent-opd`) is the confirmed implementation target under D1. The original request's Steptron wording supplies semantic references; the earlier canceled Steptron investigation and initial branch inspection supply no implementation authority for this task.
- D14 closes the shared-understanding gate and authorizes in-scope implementation/prerequisite checks. GPU execution still needs the specified assets/runtime/resource prerequisites. At the D14 decision, no RJobs have been submitted by this task.
- Preserve unrelated `.serena/` and `task_memory/task_2026-11-06_qwen_model_inventory/` work. No README edit, external publication, unrelated deletion or broad refactor is authorized. The exact old Git index-lock cleanup is separately approved above. Cloud operations remain within the personal namespace and approved run scope.
- Future runs follow the workspace GPU/storage rules: personal StepMind Python submission, A/B H200/step_main under D18 and C H800/codesign, local source mounts, live quota check, personal cloud writes and only the explicit model-read exceptions above. The H200 session/task ceiling is32 concurrent non-preemptible GPUs; the stated H800128 GPUs are cluster capacity, not observed free capacity. Auxiliary validators remain non-blocking for runs using32 or more GPUs.

## Decisions to resolve in order

1. **Framework — resolved:** current Miles only, as recorded in D1 above.
2. **Route replay — resolved:** all three student paths report R3 as not applicable, per D2. Other required features remain enabled and subject to verification.
3. **Workload — resolved by D3/D4/D6/D7/D9–D12/D14:** fresh single-turn OPD with preserved history, completion-only targets, enabled fresh thinking, finite first-round budget, length-balanced group-isolated monitoring, token-mask TIS and a fixed execution/assessment baseline. Existing template configuration remains user-controllable. Actual population identities/eligibility and native results remain to be verified.
4. **Numerical acceptance — resolved by D8:** pre-TIS same-version global token-weighted mean absolute error <= 0.03, both overall and by prefix-length stratum, with tails/K3 and unresolved-defect exclusions. D9/D11 fix monitoring counts, cadence and stratum boundaries; actual identities and complete same-version evidence remain prerequisites.
5. **Deployment — current choice resolved by D5; resources pending:** colocate the student trainer/rollout and use an external frozen teacher. Establish authorized model sources, feasible topology, concurrent GPU budget and timing. Track NCCL-direct validation as deferred under this temporary choice. Exact unsupported requirements go back to the user.
6. **HF output — resolved by D13/D14:** retain one final text-only HF artifact per pair, with matching configuration/tensors/tokenizer and real text-inference reload. Freeze exact personal output paths and verify loader support in P2. Resumable optimizer state and full-VLM reconstruction are not requested.

The [design](design.md) owns inspected facts and proposed verification semantics. The [plan](plan.md) owns the dependency graph and completion conditions. No numerical or resource proposal is accepted merely by appearing in either file.
