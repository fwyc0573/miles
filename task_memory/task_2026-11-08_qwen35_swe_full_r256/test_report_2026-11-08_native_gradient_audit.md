## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Identify the audited probe as historical GLM-5.2 engineering evidence after the D11 dataset replacement. |
| 2026-11-08 | Independently audit the actual eight-rank gradient JSONLs; record measured derivative, denominator, scaling, optimizer continuity and remaining ownership/zero-slice limits. |

# Actual native gradient audit — T02-ACTUAL-GRADIENT-AUDIT

## Outcome

**Observed numerical criteria PASS. Complete nonzero scale-call coverage and optimizer-owned gradient interpretation remain UNVERIFIED.** All eight rank files from actual fixed probe `exp-1108-195742-592659` were audited independently; the job's terminal status was not an audit input. No native observer, core, producer, launcher, requirements, spec, progress or shared test report was edited. No GPU, platform, cloud, SSH, authentication or commit operation was performed.

The actual probe is **three successful updates, eight turns per bank**, bank0 visits1/2 followed by bank1 visit1. Its original token counts are **666,666,1532**, not the previous smoke's668,668,1813. No tensors or row values from that other job enter this audit.

This probe used the historical GLM-5.2 inputs. Its observed native mathematics remains engineering evidence; it does not accept the replacement DeepSWE source, its capacity, or a formal cell.

Owned deliverables:

- `tests/manual/agent_opd/audit_swe_native_gradients.py`: standalone standard-library CPU audit; imports no observer/producer, creates no model/optimizer/collective, and compares every saved numerical position.
- `evidence/native-gradient-audit.json`: compact results, per-call errors/examples, native identities/counters, input SHA256s and runtime/source digest matches.
- This report, scoped to the required observations in [test_report_2026-11-08_native_gradient_probe.md](test_report_2026-11-08_native_gradient_probe.md#evidence-seam-and-native-pass-conditions).

## Sources, environment and exact command

Inputs are the eight local files:

```text
task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-native-gradient-live/native_gradients_rank_{0..7}.jsonl
```

They contain **264 JSON rows**, **24 rank/update tuples**, **24 actual graph calls**, **24 finalizer calls**, **24 actual DDP scale calls**, **48 optimizer-boundary rows** and **24 native ACKs**. There are **zero missing/duplicate expected events and zero `observer_unverified` rows**. Each rank supplies11 records/update. The eight files total390,238 bytes; no copies of them were created. Their exact SHA256s are retained in the audit JSON.

The authoritative numerical bounds/settings are read from existing `evidence/training-native-gradient-config.json`; pass tolerances are those of the required probe report. CPU execution uses `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, **Python3.12.13**, with standard-library FP32 rounding via `struct` and independent `math.exp` arithmetic. It requires no Torch/conda activation or dependency installation. `RLIMIT_AS=30 GiB` is set before any file calculation; plain `timeout60s` bounds the command. Observed maximum RSS is about20 MiB; the exact latest KiB value is in JSON.

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python \
  tests/manual/agent_opd/audit_swe_native_gradients.py \
  --root task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-native-gradient-live \
  --output task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/native-gradient-audit.json \
  --config task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-native-gradient-config.json \
  --job-id exp-1108-195742-592659 --ranks 0 1 2 3 4 5 6 7 \
  --pinned-core /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937/core \
  --memory-gib 30
```

Actual result: **exit0**, `OBSERVED_MATH_PASS_WITH_UNVERIFIED_ZERO_SLICES_AND_SHARD_OWNERSHIP`. Syntax, JSON completeness and whitespace were separately checked. Successful exit alone is not the acceptance evidence; the explicit results follow.

## Required criteria and measured results

| Criterion | Verdict | Actual evidence / largest error |
| --- | --- | --- |
| Every expected rank/microbatch and join | PASS | 8ranks ×3updates ×1call;264 rows; call/flat positions/sample indices match exactly. Missing/soft counts0. |
| Live graph and detach | PASS | All24 actual `SubBackward0` boundaries have no baseline edge/gradient and a live `CatBackward0` logprob edge. Native KL/PG tensors require grad; scored student, teacher, behavior, advantages and masks do not. |
| Original∩TIS incoming gradient | PASS | All256 saved presentations have incoming derivative exactly0 or1 equal to original×retained. Measured retained backward multiplier1;144 retained positions are nonzero and112 eligible rejected positions have zero incoming/live-logprob gradients. |
| Actual `dLoss/dl` and sign | PASS | Independently recomputed FP32 `a=q-s`; maximum derivative absolute/relative error0; maximum `dLoss/dl + dLoss/d(s-l)` error0. Float64-source reference difference at most2.9802322387695312e-8. |
| Actual local/global original-token count | PASS | Every local finalizer count equals the live original mask sum. Each actual DP-CP group sums to666,666,1532, exactly matching all native global count tensors and ACK originals. |
| DDP is not averaged | PASS | Every actual DDP config has `average_in_collective=False`, and every actual buffer pre-scaling factor is1. Hash-matched DDP source enforces this per-token configuration. |
| Actual passed factor is `1/N` | PASS | All24 factors use originalN, not survivors/sample count. Maximum relative error2.421438694867606e-8, below1e-7. |
| Saved before/after scale multiplication | PASS for observed arithmetic | All192 FP32 sample positions satisfy `after=before*factor`. Maximum absolute error5.4569682106375694e-11, relative5.459640927496467e-8; exact independently rounded FP32 reference error0. |
| Nonzero sample at every scale call | **UNVERIFIED for4calls** |20/24calls contain nonzero values; rollout1, ranks2,3,4,5 contain genuine all-zero eight-value slices. Zero preservation is observed, but cannot establish nonzero scaling at those four calls. |
| Native optimizer/group settings | PASS for saved groups |8 actual `ChainedOptimizer` wrappers, each with one actual TE `FusedAdam` leaf in AdamW mode1. Both groups have LR2e-6, betas(.9,.98), eps1e-8; native decay/no-decay WD0.1/0. |
| Optimizer state/counter continuity | PASS for saved observations | Every actual group advances1→2→3; wrapper/leaf/leaf-state identities remain stable across before-train and both optimizer boundaries.16 sampled initialized parameter-state dictionaries retain their parameter IDs, state IDs and `exp_avg`/`exp_avg_sq` keys through the bank transition. |
| Runtime delegate provenance | PASS for recorded digests | Five callable identities, four source files, one stable digest each across all ranks/updates; each exactly matches an inspected local retained/current copy. |
| Final optimizer-owned parameter gradient | **UNVERIFIED** | Distributed optimizer is enabled, but no parameter-to-buffer shard ranges are saved. The sampled full-parameter `main_grad` slice is not established as the rank-owned optimizer gradient. |

The required derivative tolerances are absolute1e-6/relative1e-5; scale-multiplication tolerances absolute1e-8/relative1e-6; factor relative tolerance1e-7. All nonzero actual numerical errors above satisfy each individual absolute/relative bound. A relative error against an expected zero is undefined, represented as `null` in individual examples, not fabricated0.

## Independent actual loss-gradient reconstruction

The auditor does not import the observer's derivative implementation. For each saved graph position it obtains the actual `s-l`, teacher/current-student source values and incoming PG gradient, independently computes FP32 `a=q-s`, then:

```text
r = exp(-(s-l))
dPG/dl = -a*r
dPG/dl = 0 if a>0 and r>1.28, or a<0 and r<0.8
dLoss/dl = (dPG/dl) * actual incoming PG gradient
```

All **256 saved presentations** have `s-l=0`, `r=1`, and zero active clipping branches. This is the actual reachable configured observation, not a manufactured clipping test. Nothing is claimed about the unsaved ratios. All sampled values are finite and outside exponent-saturation cases. The independently rounded FP32 source subtraction matches saved native advantages exactly; the native observed derivative then matches exactly. The audit also verifies the opposite sign at the actual subtraction boundary.

TP peers present the same sampled token derivatives twice. Exact sample/index/value equality was checked before de-duplication: **128 distinct update/sample/response positions**, comprising **72 retained and56 rejected**. The256/144/112 counts are observations, not256 distinct training tokens or256-turn capacity.

Concrete actual examples from rollout0, rank6, call1 (metadata/response-shape join, not file order):

| Example | Canonical sample/response index | Original/retained | `s` | `q` | Independent `a=q-s` | Incoming PG grad | Actual / expected `dLoss/dl` |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Rejected, flat0 | sample6/0 |1/0| -2.3140931129455566 | -2.4338161945343018 | -0.11972308158874512 |0|0 /0|
| Retained, flat75 | sample1/0 |1/1| -0.23104046285152435 | -0.24754191935062408 | -0.01650145649909973 |1|0.01650145649909973 /0.01650145649909973|

The rejected advantage is nonzero, so its actual zero derivative is evidence of the mask, not merely a zero-advantage case. Graph callbacks return `None`, delegating backward without changing gradients. These are live logprob derivatives **after local reduction and before parameter finalization**, not final parameter gradients.

## Native denominator, topology and scale-call boundary

Runtime DP-CP groups are `[0,2,4,6]` and `[1,3,5,7]`; TP groups are `[0,1]`, `[2,3]`, `[4,5]`, `[6,7]`. Every group is checked from actual local topology receipts. Samples are disjoint within each DP-CP group and identical across TP peers; eight turns are counted once in each DP-CP group, not twice across all eight ranks.

| Rollout / bank visit | Local original counts, DP group `[0,2,4,6]` | Global originalN | Global surviving | Actual factor |
| --- | --- | ---: | ---: | ---: |
|0 / bank0 visit1|177,72,286,131|666|591|0.0015015015378594398|
|1 / bank0 visit2|177,72,286,131|666|56|0.0015015015378594398|
|2 / bank1 visit1|267,323,813,129|1532|1223|0.0006527415243908763|

The odd DP group independently gives the same totals. These are actual finalizer count observations before and after the native mutation, plus an independent SUM across the correct group, not counts inferred from a scalar loss. OriginalN remains666 on replay even when only56 tokens survive.

For example, rollout0/rank0's actual `main_grad[0]` before its native scale method is `-1.3607177734375`; after the actual passed `1/666` FP32 factor it is `-0.002043119864538312`. The sampled `gradient_attr` is explicitly `main_grad`, not `parameter.grad`; parameter name and indices match before/after each call.

**Ownership limit:** actual `use_distributed_optimizer=True`. Hash-matched DDP code delegates scaling to buffers, and retained native buffer code scales the full gradient buffer. The retained distributed optimizer source separately copies only `param_range.start:end` into the owning main shard. Those ranges are absent from the receipts. Consequently this report establishes the actual **scale-method call/factor/count/multiplication**, but makes no cross-rank SUM interpretation of sampled gradient values, and does not label non-owned full-buffer values as optimizer-owned final gradients. Reduce-scatter payloads and optimizer-owned values are not reconstructed.

Four all-zero scale slices are real saved observations, not absent rows or suppressed observer errors. Their exact factor/count and zero preservation pass, while per-call **nonzero** scaling remains unverified. The strict requirement for a nonzero sampled gradient at every scale call is therefore not fully closed.

## Optimizer observations and transition

Actual TE leaf group parameter counts by global rank:

| Ranks | Decay parameters | No-decay parameters | Actual post-step group counters |
| --- | ---: | ---: | --- |
|0,1|62|43|[1,1] →[2,2] →[3,3]|
|2,3|71|44|[1,1] →[2,2] →[3,3]|
|4,5|67|44|[1,1] →[2,2] →[3,3]|
|6,7|28|22|[1,1] →[2,2] →[3,3]|

Every group's LR/betas/epsilon/weight decay is checked at **before-train, before-optimizer and after-optimizer** in all three updates. Group counter fields are absent before initialization; they are not treated as measured zero. After initialization the actual counter is the TE **group** counter. Sampled per-parameter states contain `exp_avg` and `exp_avg_sq`, but no per-parameter `step`; this absence is reported rather than fabricating parameter counters.

Native ACKs on all ranks report successful1/2/3, attempted1/2/3, skipped0 and current version0/1/2. Exact sample metadata agrees on `(bank,visit,successful_before)=(0,1,0),(0,2,1),(1,1,2)`. Stable process-local identities are compared **within each rank**, never across processes. The16 sampled parameter-state dictionaries remain initialized and unchanged in identity at every later boundary. Group object identities, all parameter IDs and unsaved moment values are not recorded; continuity is limited to the actual sampled identities/group counters and persistent leaf state containers.

## Provenance and source references

Recorded runtime digests match inspected local copies exactly:

| Runtime source | SHA256 | Inspected evidence |
| --- | --- | --- |
| Miles `model.py`|`d8d8f5a4afb8023cb523091c0c45c3c8723b879b9487735bba30055669c7182e`|Current local `miles/backends/megatron_utils/model.py`; before-train599–605, actual optimizer694, finalizer wrapper742–772.|
| Megatron `finalize_model_grads.py`|`ee0936e28c99083a65eb19af6f72c74345f6fb0379eb05f0245d3e7976ec6536`|Retained pinned copy466–583; actual grad sync followed by token broadcast/DP-CP SUM and`1/N` call567–583.|
| Megatron `distributed_data_parallel.py`|`3898ac3f6d10e50ac61f0a70698e2c0a27e2d1d0df23195118e2fa44b842741b`|Retained pinned copy177–183 and586–589; averaging prohibited/per-token buffer pre-factor1; scale/sync callable digests both match.|
| Megatron `optimizer.py`|`328e6ad17d0f60b3bd9e6e1eaf372ea274dd91165ff861051e635e55386bcccb`|Retained pinned copy538–540; actual configured loss-scale delegate. The incoming multiplier is measured1, not inferred from this source.|

Retained pinned root is `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937/core/`. Runtime paths/digests and exact local paths are in JSON; no worker/cloud source read was performed. A host installed-Megatron mapping was inaccessible through its worker-path symlink; the already-retained pinned copy then supplied the exact matching source. This is a provenance-path limitation, not a native numerical failure.

Additional inspected **source context**, without a corresponding runtime digest in these receipts:

- Pinned `distributed/param_and_grad_buffer.py:712–775,1669–1673`: prescale/SUM-vs-AVG selection, reduce-scatter owner view, and full-buffer multiplication.
- Pinned `optimizer/distrib_optimizer.py:2842–2886`: only the optimizer-owned parameter range is copied from model `main_grad`.
- Local `/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/transformer_engine/pytorch/optimizers/fused_adam.py:563–590`: native per-group step, not a missing per-parameter counter. Actual class/mode/group counters are directly recorded, but the worker TE file digest is not present.
- Current `miles/backends/training_utils/loss/objective.py:129–131,173,229–243`: pre-TIS original count and native per-token finalizer path. Fully masked samples would count at least one in this backend; sealed samples here have nonempty original masks, and observed counts are exact originals.
- Current `miles/backends/training_utils/loss/hub/math_utils.py:255–278`: PPO surrogate; `tests/manual/agent_opd/swe_tis.py:107–134`: detached binary mask, original-mask sums and `torch.where` gating.
- Current observer `tests/manual/agent_opd/probe_swe_native_gradients.py:153–189,260–302,322–383`: read-only actual scale/graph/state observations and metadata-index joins. The worker observer digest itself is not recorded, so it is not falsely included among digest-verified native files.

## Remaining verification limits

1. Nonzero scaling at rollout1/ranks2,3,4,5 remains UNVERIFIED from zero-only slices; no observer or allocation was changed to manufacture coverage.
2. Optimizer-owned final gradient values, shard mappings, collective payloads, post-finalizer optimizer clipping and all parameter state/moment values are absent. No final full-buffer or cross-rank gradient claim is made.
3. Only selected actual positions are saved: full answer-level TIS ratios/full vector derivatives cannot be independently recomputed from these JSONLs alone. The audit independently proves derivative and incoming-mask behavior for every saved position; actual full original/survivor counts match ACKs.
4. All saved sampled ratios equal1. Clipping/saturation/nonfinite branches are not native observations; a nonfinite/saturated or missing/soft observer record is markedUNVERIFIED, not silently assigned a gradient or treated as D7 zero survival.
5. Three eight-turn A/r256 updates do not prove256-turn capacity, full formal schedules, other cells or complete Ticket02 acceptance.

## 1. 规划完成情况

**汇总：** PASS2｜BLOCKED/FAILED/SKIPPED0｜TODO1（本委派范围）。

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 实际rank记录的独立数学/状态审计 | PASS |264条记录，已完成全部保存观察位置的计算与明确范围判定。 |
| 持久化数值、源码依据及未核验项 | PASS |本报告与独立JSON；只新增三个自有文件。 |
| 父任务02完整验收 | TODO |02仍拥有256容量及其余运行验收；四个零切片非零缩放、shard所有权证据不由本报告补造。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** T02-ACTUAL-GRADIENT-AUDIT开始至本地计算和记录完成｜**当前前沿：**02/03，本委派仅拥有02实际梯度独立审计。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR |独立CPU脚本直接验证关键数学；无新增observer或test framework。 |
| D2 细节反复重试 | CLEAR |本地源码映射不可读后改查已保留且digest匹配的副本；数值检查无反复行为修改。 |
| D3 支线问题修补 | CLEAR |未修复平台、共享代码或其他任务。 |
| D4 可并行任务停滞 | CLEAR |用户明确由父会话拥有GPU及其他验收，本委派独立文件无竞争。 |
| D5 超范围镀金 | CLEAR |不扩充observer采样、不制造clipping覆盖、不保存完整梯度或moments。 |
| D6 分析空转 | CLEAR |实际计算已落实为独立数值与精确验收限制。 |
| D7 路线违背 | CLEAR |未改原始分母/公式/配置，也未把小probe当256容量或正式完成。 |

**文档检查：**S1–S6未发现本委派范围内明显缺陷；required probe criteria已有明确数值界限，缺证据仍由02拥有。
**归因：**无。

## 3. 纠正建议

**分支：**A：spec/tickets合理，无需改动。

**需停止的偏离行为：**无。

**接下去的路线：**
1. 交还已验证的live导数、原始分母、20次非零scale和实际optimizer连续性；父会话决定是否还需逐调用非零证据，并保留shard所有权限制。
2. 并行继续02已有256容量验收与03已有实际评测；本报告不关闭任何父任务ticket。

## 4. 最值得关注的3点

1. Live梯度独立FP32误差0；原始分母确为666、666、1532，不是survivor或旧作业值。
2. 参数scale数值通过，但4次全零切片和缺失shard范围限制了完整结论。
3. 实际AdamW组计数1→2→3及16个sampled state字典跨bank连续，不证明未保存的全部optimizer状态或256容量。
