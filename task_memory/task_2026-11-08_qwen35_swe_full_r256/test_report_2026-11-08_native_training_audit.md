## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Add completion-only RKL scope evidence: prompt exclusion, per-sample target offsets, and bank0 visit2 fresh-student check. |
| 2026-11-08 | Parent corrected two lint findings, applied Black and reran the exact native artifact audit; numerical results unchanged. |
| 2026-11-08 | Independently reconstruct actual A/r256 smoke tensors and record numerical results and missing native gradient seams. |

# Native A/r256 training audit — T02-ACTUAL-AUDIT

## Outcome and scope

**NUMERICAL PASS; native gradient scaling and complete Ticket02 acceptance remain unverified.** This audit independently reconstructs actual downloaded tensors from `exp-1108-172407-535512`, rather than invoking producer self-tests or using JSONL metrics as calculation inputs. All three primary KL numerators/denominators and exact TIS counts match the native receipts. Reconstructed PPO loss agrees within absolute tolerance `1e-8` (maximum error `2.10408012540908e-9`).

Only local CPU files were accessed. No GPU, platform, cloud, SSH, producer edit, shared progress/spec/ticket edit, or commit was performed. The parent separately owns the platform `Stopped` diagnosis; it does not affect this numerical comparison.

Deliverables:

- Reusable, standalone CPU audit: `tests/manual/agent_opd/audit_swe_native_training.py`.
- Compact numeric evidence: `evidence/native-training-A-r256-audit.json` (relative to this task directory).
- This report. Raw dumps remain only in the downloaded temporary directory; they were not copied into task records.

## Sources, environment and command

Source root: `/data/ycfeng/tmp/qwen35-swe-native-audit/exp-1108-172407-535512/`.

- `train_data/{0,1,2}_{0,2,4,6}.pt`: twelve actual native rank dumps.
- `policy_loss_debug/rank_{0,2,4,6}_call_{0,1,2}.pt`: twelve actual native PPO dumps.
- `updates.jsonl`: three native-boundary receipts, read **only after** reconstruction for comparison and observed LR/update counters.
- Scope contract: `tickets/02-replay-training-and-metrics.md`; `spec.md` S4.
- Inspected producer semantics, without importing or executing them: `tests/manual/agent_opd/swe_tis.py:26–58,107–134`, `swe_training.py:129–209`, `miles/backends/training_utils/loss/objective.py:73–125,173–243`, `loss/hub/opd.py:88–94`, `loss/hub/losses.py:103–149,197–234,260–319`, `loss/hub/math_utils.py:255–278`, `data/context_parallel.py:265–283`, and `metrics/debug_dump.py:28–76`. Native optimizer hook placement is `miles/backends/megatron_utils/model.py:607–700`. These are local inspected sources, not additional saved runtime tensor evidence.

Environment: Linux CPU host, `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python **3.12.13**, Torch **2.11.0+cu130**. The script uses CPU tensors and one Torch thread. Plain `timeout 60s` bounds the execution; `resource.RLIMIT_AS=30 GiB` is set before importing Torch because user systemd is unavailable. Observed maximum RSS was about **501 MiB**; the exact latest value is retained in JSON. No conda environment activation or package installation was needed.

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python \
  tests/manual/agent_opd/audit_swe_native_training.py \
  --root /data/ycfeng/tmp/qwen35-swe-native-audit/exp-1108-172407-535512 \
  --output task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/native-training-A-r256-audit.json \
  --ranks 0 2 4 6 --token-bounds 0.5 2 --answer-bounds 0.9897 1.001 \
  --ppo-bounds 0.8 1.28 --memory-gib 30 --expected-lr 2e-6
```

Passing conditions: complete four-rank coverage for each step; unique metadata-indexed sample membership; binary original masks; exact shape/value matching between actor and PPO dumps; exact saved OPD/PPO token calculations; exact integer KL denominator and TIS counts; KL/retention numerical errors at most `1e-8`; scalar loss error at most `1e-8`; replay content identity with changed student values; native receipt/metadata counter agreement. Actual execution exited **0**, returning `NUMERICAL_PASS_WITH_EXPLICIT_UNVERIFIED_SEAMS`. A successful exit is supplemented by the values below and the evidence JSON.

## Actual schema and identity checks

Parent re-verification after renaming the ambiguous training-logprob variable and removing an unused loop binding: the command above with output `/data/ycfeng/tmp/qwen35-swe-native-audit-parent-20261108.json` again returned numerical PASS with identical three-update results. Black formatting and Ruff checks passed; no producer behavior changed. The report's original evidence JSON remains unchanged.

The native `rollout_data` contains `tokens`, `sample_indices`, `metadata`, `loss_masks`, `log_probs`, `teacher_log_probs`, `rollout_log_probs`, `advantages`, `opd_reverse_kl`, native microbatch indices and lengths. Tokens are full prompt+response `int64`; masks are response-only `int32`; score/teacher/behavior/advantage tensors are response-only `float32`. All response shapes were checked against the individual sample's response length. CP fields explicitly report rank **0**, size **1**; `qkv_format=thd`.

The actual PPO dump has sample-local `index`, lengths, `train_log_probs`, `old_log_probs`, `advantages`, `local_loss_mask`, `rollout_log_probs`, plus concatenated pre-TIS `ppo_kl`/`pg_loss`. It does **not** contain canonical metadata, a final post-TIS mask, final scalar loss, or gradients. Its tensors were detached before saving; `requires_grad=False` in the file is not evidence about the original live training graph.

Each PPO sample was uniquely matched against all candidate training dumps on the same rank using exact old-score, behavior, advantage, original-mask and length equality. The audit did not assume filename/call order or canonical list order. Replay keys use `(attempt, bank, slot, source_uid, sample_index)`, independent of DP placement.

An initial audit assertion incorrectly equated `sample_index` with bank-local `swe_slot`. The saved artifacts disproved that hypothesis: bank0 indices are **0–7**, whereas bank1 indices are **8–15**, still with bank-local slots **0–7**. The assertion failed before writing output; a scoped inspection established the separate identities, and the audit was corrected to require `sample_indices == metadata.sample_index` while preserving `swe_slot` separately. This was an audit assumption error, not a producer defect. The corrected full audit passed.

The parent-supplied topology is TP2/DP4/CP1. Runtime dumps contain ranks **0,2,4,6**; every step has all four and eight disjoint canonical samples. The native producers write only TP-rank0 peers, so these ranks must be counted once, not doubled. The audit verifies coverage and identities, not a live distributed process group.

## Independent KL and D4 results

The audit computes float64 `sum(original_mask * (s-q))` and exact original-token counts, then applies token `exp(s-b)` bounds and answer `exp(mean(s-b))` on **all original eligible response tokens**. Both masks intersect with the original mask; retained weights are exactly binary. No row values enter those calculations.

| Successful update / bank visit | Original tokens | KL numerator | KL denominator | Recomputed primary KL | Surviving tokens | Retention |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 / bank0 visit1 | 668 | 62.20545252558421 | 668 | 0.09312193491853923 | 603 | 0.9026946107784432 |
| 2 / bank0 visit2 | 668 | 29.156633393696772 | 668 | 0.04364765478098319 | 132 | 0.19760479041916168 |
| 3 / bank1 visit1 | 1813 | 167.20409280191302 | 1813 | 0.09222509255483344 | 1038 | 0.5725317153888583 |

All primary KL, denominator, original/surviving counts and retention comparisons **PASS** with zero observed error. No saved eligible score is nonfinite.

Actual response lengths, sorted by bank-local slot:

- Bank0, both visits: **92,56,67,112,127,65,77,72**.
- Bank1: **91,557,646,104,78,58,150,129**.

These are nonuniform lengths. The audit adds token numerators and denominators rather than averaging sample means or rank retention rates. JSON also records the unequal sample-mean KL and incorrect sample/survivor loss alternatives for comparison.

| Update | Token-layer rejected | Answer-layer rejected | Overlap | Union rejected | Surviving |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 65 | 0 | 65 | 603 |
| 2 | 18 | 535 | 17 | 536 | 132 |
| 3 | 0 | 775 | 0 | 775 | 1038 |

Both actual TIS layers reject on visit2. Summing the two rejection counts without subtracting their overlap would incorrectly remove 553 tokens rather than 536.

Concrete saved rejected examples:

| Reason | Step/rank/slot/response index | Actual token ID | `s` | Frozen `b` | Token ratio | Answer ratio | Saved raw PPO token loss | Reconstructed binary contribution |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Answer only | 0/0/5/0 | 9764 | -0.09260504692792892 | -0.09261765331029892 | 1.0000126064618309 | 1.0014451503065593 | 0.20577722787857056 | 0 |
| Both layers | 1/0/3/19 | 913 | -2.293914556503296 | -1.4914665222167969 | 0.44823033669460594 | 0.9157276072107173 | 0.9845199584960938 | 0 |
| Token only | 1/6/6/5 | 12149 | -4.738163471221924 | -3.8148484230041504 | 0.3972001186012948 | 0.9902256394901224 | 0.725954532623291 | 0 |

In the token-only example, the answer passes and **76/77** original response tokens survive. This directly distinguishes the intersection rule from answer-only rejection. The actual native pre-TIS token loss is saved; the post-TIS zero here is independently reconstructed, not a downloaded final-mask observation.

## Native OPD/PPO loss and denominator

For every saved token, `advantages=q-s`, `opd_reverse_kl=s-q`, `ppo_kl=s-l`, and native pre-TIS `pg_loss=max(-exp(l-s)*a,-clip(exp(l-s),0.8,1.28)*a)` match the downloaded producer tensors **exactly** (maximum token error **0**). Scalar rewards and saved returns are zero. The standalone audit implements only this evidence calculation, not an alternate production loss.

Across all **3149** token presentations, training-forward `l` exactly equals current independent actor score `s`; therefore `rho=1` and no actual PPO clipping branch is exercised. This establishes the current native surrogate values, but it cannot distinguish all alternate objectives at unexercised ratios or prove a live detach edge.

Native original counts by dumped rank:

| Step | Rank0 | Rank2 | Rank4 | Rank6 | Global original denominator |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 177 | 72 | 286 | 133 | 668 |
| 1 | 177 | 72 | 286 | 133 | 668 |
| 2 | 240 | 241 | 1203 | 129 | 1813 |

The audit independently applies binary TIS to actual PPO token losses, uses native-style float32 sample/rank sums, and divides by the global **original** denominator:

| Step | Reconstructed PPO loss | Native receipt loss | Absolute error | Relative error | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| 0 | 0.09154772624641122 | 0.09154772687101079 | 6.24599566512174e-10 | 6.822666032901333e-9 | PASS |
| 1 | -0.0018305689274907826 | -0.0018305689274907826 | 0 | 0 | PASS |
| 2 | 0.0382059636986591 | 0.038205965802739224 | 2.10408012540908e-9 | 5.507203079939483e-8 | PASS |

The float64 scalar reference is respectively `0.09154772631489609`, `-0.0018305688141966793`, `0.03820596427468481`. Sub-nanounit/native float32 accumulation differences are reported, not hidden or attributed to a proven GPU summation order.

Using survivors as the denominator instead would produce `0.10141605494627312`, `-0.00926378820881699`, `0.06673161096885255`; sample-normalized values also differ. The observed native scalar receipts therefore support global original-token normalization, not survivor or sample normalization. JSON additionally records the counterfactual retained-TIS-ratio weighting.

**Evidence boundary:** the native dispatcher inspected locally returns the pre-TIS token count and unnormalized CP1 loss to Megatron's per-token path. Neither its actual finalizer token-count tensor nor actual gradients are downloaded. Effective `1/N` **gradient** scaling is consequently a source-backed inference, not measured proof. Scalar loss agreement alone cannot prove the distributed backward normalization.

## Replay and native counters

All eight bank0 sample keys occur exactly once on each visit. Tokens, original masks, frozen teacher scores, frozen behavior scores, teacher identity, generation-version metadata and prompt/completion identity are unchanged per key. Current student values change on all eight samples, with **547/668** tokens changed and maximum absolute score change **7.5952558517456055**. Derived advantages change correspondingly, and **471** reconstructed survivor-mask positions change. This is actual saved refreshed-score evidence, not reuse of stale feedback.

Bank1 has eight new source UIDs, sample indices **8–15**, and generation version **2**. Bank0 generation stays version **0** across visits1/2, while current versions are **0,1**; bank1 current version is **2**. The observed sequence is **bank0 visit1 → bank0 visit2 → bank1 visit1**.

Native-boundary receipts report successful updates **1,2,3**, attempted counts **1,2,3**, skipped count **0**, and optimizer parameter-group LR **[2e-6,2e-6]** each time. These agree with per-sample `swe_successful_before=0,1,2` and current versions. Locally inspected hook placement reads actual optimizer group LR and receives the native `optimizer.step()` success result; the receipt counters themselves are hook-maintained counters. No independently saved optimizer state or scheduler counters are available to verify parameter groups, Adam settings or optimizer-state continuity across the bank transition.

## Remaining seams and verification limits

1. **Actual backward/detach/DP scaling:** missing actual logprob/logit/parameter gradients, original live autograd graph, global finalizer token count and collective buffers. Detached serialized scores cannot verify these. This report does not substitute a synthetic CPU gradient for actual native evidence.
2. **Healthy final TIS mask/scalar:** downloaded healthy artifacts stop before native TIS application. Independently reconstructed masks agree with exact receipt counts and scalar loss, but direct saved post-TIS masks/final reduced loss tensors are absent.
3. **PPO clipping branches:** all actual `rho=1`; threshold/clipping activation is not observed in this smoke. No production behavior or thresholds were changed to manufacture coverage.
4. **Optimizer state/settings/skip paths:** LR and success/skips are observed native receipts only. No actual skipped update, state continuity, betas/epsilon/weight decay or parameter-group state is independently verified here.
5. **Full Ticket02/formal acceptance:** only A/r256, eight turns, two bank0 visits and three successful smoke updates. Representative256-turn capacity, other-cell numerical audits, full50-visit replay,200-successful-update schedules and their additional acceptance criteria are outside this audit. Their work remains with the parent; this audit does **not** mark Ticket02 or a formal cell complete.

## 1. 规划完成情况

**汇总：** PASS 2｜BLOCKED/FAILED/SKIPPED 0｜TODO 1（本次委派范围）。

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 实际 tensor 的独立 KL/TIS/PPO 与 replay 重算 | PASS | Evidence JSON 的三组数值及逐样本身份检查已完成。 |
| 精确记录证据与验证边界 | PASS | 本报告明确列出五类缺失 seam，不修改共享状态。 |
| 父任务 Ticket02 完整验收 | TODO | `tickets/02-replay-training-and-metrics.md:23–25` 还要求实际梯度、各配置与256容量；未由本委派完成。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** T02-ACTUAL-AUDIT 开始至本次真实重算通过｜**当前前沿：** 父任务02/03；本委派仅负责02独立数值证据。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 单一CPU审计是验证02真实数值的直接工具；通过后停止扩展。 |
| D2 细节反复重试 | CLEAR | 一次错误身份假设被实际bank1索引证据纠正，无重复参数试错。 |
| D3 支线问题修补 | CLEAR | 未修改producer、平台生命周期或其他文件。 |
| D4 可并行任务停滞 | CLEAR | `progress.md:79–81` 记录父会话另行推进256容量及其他短配置；本委派无重叠所有权。 |
| D5 超范围镀金 | CLEAR | 无替代production loss、广泛test suite或持久raw dump副本。 |
| D6 分析空转 | CLEAR | 调查落实为可执行审计、真实数值与本报告。 |
| D7 路线违背 | CLEAR | 保留D4双层binary和S4原始分母，不把短smoke称为正式验收。 |

**文档检查：** S1–S6 均未发现本委派范围内的明显缺陷。缺失的梯度/容量证据已由02明确拥有，不新增无主阻塞。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 交还已完成的独立数值审计；父会话按02已有验收项取得实际梯度/分母和代表性256-turn容量证据，不能以本报告关闭02。
2. 并行：父会话继续03原生HF/SWE验收，保持与02证据/平台RCA分工独立。

## 4. 最值得关注的 3 点

1. 原始/保留tokens与主KL已独立精确重算，visit2双层拒绝有真实token例子。
2. 真实PPO输入及scalar结果有证据；实际梯度缩放和detach尚无下载证据。
3. bank/indices应区分；本次8-turn三步smoke不证明256容量、完整排程或Ticket02完成。

## Follow-up: completion-only RKL scope (T02-COMPLETION-RKL)

**PASS.** Scope: prompt/prefix tokens must not enter the sampled RKL; the statistic is recomputed on each fixed completion by the current student at every visit, compared against the frozen teacher, over the pre-TIS original eligible completion mask, with no importance weighting. No producer, spec, requirements or progress file was changed; no GPU, cloud, SSH or platform access was used.

Command (same CPU environment and 30 GiB address-space cap; exits 0 and prints `NUMERICAL_PASS_WITH_EXPLICIT_UNVERIFIED_SEAMS`):

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python \
  tests/manual/agent_opd/audit_swe_native_training.py \
  --root /data/ycfeng/tmp/qwen35-swe-native-audit/exp-1108-172407-535512 \
  --output task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/native-training-A-r256-audit.json \
  --ranks 0 2 4 6 --token-bounds 0.5 2 --answer-bounds 0.9897 1.001 \
  --ppo-bounds 0.8 1.28 --memory-gib 30 --expected-lr 2e-6
```

The script now emits a `completion_rkl_scope` block; the numbers below are read from that block. A separate direct CPU assert over the JSON returned `PASS` for all three conditions: every saved score entry is one per completion token; the scope numerator/denominator equal the KL numerator/denominator in `updates`; and bank0 visit2 has a changed student with every other payload frozen.

### Implemented counting semantics

The saved score, mask, advantage and teacher tensors are response-length `R` vectors only; nothing in the training batch spans prompt positions. `_response_rows_without_cp` selects logits rows `[prompt_length-1, total_length-1)` and token rows `tokens[-R:]`, so response index `j` pairs the logits row at absolute index `prompt_length-1+j` with the target token at `prompt_length+j` — a one-token autoregressive label shift whose first valid completion target is `tokens[prompt_length]`. At CP1 the mask and score slices are returned unchanged, with `slice_log_prob_with_cp` asserting `len(log_prob) == response_length`. `token_sums` then sums `s-q` over the local original response mask, and the denominator is the global sum of those same mask values. The only weight applied is the 0/1 mask; no student/behavior ratio enters the numerator.

| Per-step aggregate | Prompt tokens excluded | Completion tokens | Original-mask tokens | Numerator | Denominator |
| --- | ---: | ---: | ---: | ---: | ---: |
| bank0 visit1 | 108,289 | 668 | 668 | 62.20545252558421 | 668 |
| bank0 visit2 | 108,289 | 668 | 668 | 29.156633393696772 | 668 |
| bank1 visit1 | 332,305 | 1,813 | 1,813 | 167.20409280191302 | 1,813 |

Per-sample scope. Bank0 prompt/completion/mask/token values are identical on visits 1 and 2 (the sample is frozen); bank1 has fresh samples. `first target` is the absolute token index of the first mask-1 completion token, which is also the first scored position; the logits row producing it is one earlier.

| Bank | Slot | Prompt | Completion | Mask tokens | First target (abs) | Target token id |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 1547 | 92 | 92 | 1547 | 40 |
| 0 | 1 | 2221 | 56 | 56 | 2221 | 9764 |
| 0 | 2 | 9048 | 67 | 67 | 9048 | 9764 |
| 0 | 3 | 12707 | 112 | 112 | 12707 | 6820 |
| 0 | 4 | 15918 | 127 | 127 | 15918 | 6820 |
| 0 | 5 | 16460 | 65 | 65 | 16460 | 9764 |
| 0 | 6 | 22277 | 77 | 77 | 22277 | 40 |
| 0 | 7 | 28111 | 72 | 72 | 28111 | 40 |
| 1 | 0 | 35760 | 91 | 91 | 35760 | 40 |
| 1 | 1 | 36774 | 557 | 557 | 36774 | 40 |
| 1 | 2 | 37111 | 646 | 646 | 37111 | 6820 |
| 1 | 3 | 42719 | 104 | 104 | 42719 | 6820 |
| 1 | 4 | 42853 | 78 | 78 | 42853 | 9764 |
| 1 | 5 | 42931 | 58 | 58 | 42931 | 9764 |
| 1 | 6 | 43274 | 150 | 150 | 43274 | 9764 |
| 1 | 7 | 50883 | 129 | 129 | 50883 | 14773 |

Every sample's first valid offset is 0 relative to the completion because all original masks are 1 here; the audit reads the mask rather than assuming that. Scored absolute ranges are `[prompt, total-1]`, e.g. bank0 slot5 is `[16460, 16524]` with 65 saved scores, and its last prompt token at 16459 is never a scored target.

### Fresh student versus frozen completion on bank0 visit2

Saved `log_probs` are the per-visit actor scoring pass (`actor.py:924-940`, enabled because the training protocol forbids `skip_actor_forward_only` and `use_rollout_logprobs`). On visit1 they already differ from generation-time `rollout_log_probs` at the same weight version on all eight samples (540/668 tokens, max 0.1904747486114502), so behavior and current student are distinct sources. Between visits, tokens, original masks, teacher values, behavior values, teacher identity and completion SHA256 are exactly equal; only student-derived values change.

| Slot | Student tokens changed | Max abs student change | Tokens/mask/teacher/behavior frozen |
| ---: | ---: | ---: | :---: |
| 0 | 65 | 2.815547466278076 | yes |
| 1 | 40 | 0.1853189468383789 | yes |
| 2 | 55 | 7.5952558517456055 | yes |
| 3 | 98 | 3.0716543197631836 | yes |
| 4 | 118 | 2.160860300064087 | yes |
| 5 | 44 | 0.2136526107788086 | yes |
| 6 | 66 | 0.922736644744873 | yes |
| 7 | 61 | 1.321018934249878 | yes |

Total 547/668 student tokens change. The KL numerator is computed from the training-forward log probs (`swe_tis.token_sums`), and for every sample that masked sum equals the independently scored `log_probs` sum exactly (maximum error 0). No importance weight or survivor reweighting is applied to this statistic.

### What the statistic is, and what it is not

The implemented quantity is an empirical sampled-token mean of `s-q` over each fixed completion's original eligible tokens, recomputed under the current student at the visit; it is the direct input of the D4 pre-TIS KL receipt. It is not the exact full current-policy expectation over all possible continuations, and it is not an importance-weighted correction of the behavior sample. Both distinctions are reported without proposing or testing a different estimator; the implemented formula is unchanged.

### Limits of this follow-up

- Prompt exclusion is verified from the saved tensor domains (exactly `R` score entries, mask length `R`, denominator `sum(mask) <= R < prompt+R`) plus the inspected CP1 slicing source. No saved artifact contains prompt-position scores, so prompt inclusion is structurally impossible rather than merely numerically small.
- The teacher token-id match is enforced at runtime in `swe_replay.score_teacher` (trimmed SGLang `input_token_logprobs` compared with `tokens[-R:]`), but that receipt (`teacher_stages.jsonl`) was not downloaded. The audit therefore relies on the completion SHA256, teacher identity, frozen teacher values and source for teacher alignment, not on a saved per-token teacher receipt.
- No logits or model execution were available on the CPU host, so the one-token shift is validated by source and by index/length consistency, not by re-running the student forward.
- This remains A/r256, eight turns, three smoke visits; it does not establish 256-turn capacity, the formal 200-update schedule, other cells or Ticket02 completion.
