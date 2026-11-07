## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Parent verifies the eight-rank replay in the exact pinned runtime and archives independent platform/config receipts. |
| 2026-11-08 | Complete eight-rank CPU/Gloo native reducer replay and wrong-survivor negative control; retain pinned-runtime and historical CUDA limits. |
| 2026-11-07 | Record native loss/schedule evidence, actual A/B scaling flags and the pinned-source prerequisite for the unfinished reducer replay. |

# Native original-token normalization

Task ID: `QWEN-REVIEW-NATIVE-DENOMINATOR`.

**Pinned native CPU/Gloo replay: PASS. Historical full-model CUDA replay: not observed.** The eight-rank replay passes both host and exact pinned runtime execution. The parent-owned pinned run and platform verification are recorded below. No optimizer was constructed or stepped. The implementation subagent performed no platform operation; the parent owns the recorded runtime execution.

## Source contract observed

- `miles/backends/training_utils/loss/objective.py:129-131,172-184,229-240`: the denominator returned to MCore is `sum(max(original_loss_mask.sum(), 1))`, calculated before the configured policy loss/TIS hook. With Megatron per-token scaling enabled, the numerator is multiplied by CP size, without a local token or microbatch division.
- `miles/backends/training_utils/loss/hub/losses.py:244-278,304`: the real custom D12 MIS hook adjusts contribution weights and masks. The per-token reducer is a SUM, not a survivor-token mean (`miles/backends/training_utils/data/context_parallel.py:277-283,317`).
- `examples/infra_features/train_infer_mismatch_helper/mis.py:147-163,235-253,283-289`: token mask mode retains inclusive `[0.5, 2.0]` ratios and their detached importance weights; outside that interval the contribution is masked. Batch normalization is disabled.
- `miles/backends/training_utils/loss/hub/opd.py:88-94`: native OPD advantages subtract the detached sampled-token reverse KL times the coefficient.
- Extracted pinned `core/pipeline_parallel/schedules.py:323-342`: a three-element loss callback with `calculate_per_token_loss=True` receives no token or microbatch division.
- The same pinned schedule at `:743-819` accumulates callback token counts across microbatches and passes `total_num_tokens` to `finalize_model_grads_func`. `miles/backends/megatron_utils/model.py:733-751` binds the real finalizer and `optimizer.scale_loss`.
- Pinned `training/training.py:2385-2425` converts the actual resolved launch flags into `DistributedDataParallelConfig`, including `grad_reduce_in_fp32`, `average_in_collective` and `use_distributed_optimizer`. This unchanged function is executed by the probe.
- Pinned `core/distributed/distributed_data_parallel.py:177-183` sets the per-token gradient scaling factor to `1.0` and rejects collective averaging. The unchanged DDP constructor is executed, including its real gradient accumulation post-hook at `:460-489`, with synthetic CPU buffer allocation/layout and process-group seams.
- Pinned `core/distributed/param_and_grad_buffer.py:651-831` uses SUM and the real reduce-scatter path for the actual distributed-optimizer/non-overlap settings; the probe executes that unchanged native method with genuine synchronous Gloo `reduce_scatter_tensor`. Only NCCL batching and unused CUDA-stream access are seams. `:833-878` completes native synchronization.
- Pinned `core/distributed/finalize_model_grads.py:515-519,567-583` completes native gradient synchronization, broadcasts tokens within PP, all-reduces tokens within DP+CP, then calls native `DDP.scale_gradients`. The unchanged buffer scaler at `core/distributed/param_and_grad_buffer.py:1669-1673` applies the reciprocal global original-token count to the communication buffer.
- Pinned `core/optimizer/__init__.py:639-665` selects no grad scaler for the actual BF16/FP16=False/loss_scale=None flags; `core/optimizer/optimizer.py:778-785` defines unity scale in that case. The native `get_loss_scale` and `scale_loss` methods execute on a state-only unity-scale seam. Optimizer construction/selection is source evidence, not an executed optimizer constructor.

The intended CP1/PP1 contract is:

```text
L = SUM_dp,microbatch,token(original_mask * tis_keep * tis_weight * policy_token_loss)
    / SUM_dp,microbatch,sample(max(original_mask.sum(), 1))
```

For the accepted actual completions with nonempty original masks, this is the original eligible-token global mean. A fully originally masked sample counts as one by the native Miles contract. TIS rejection does not change that count. The native DDP constructor, accumulation hook, schedule, finalizer, reduce-scatter and final scaling execute in the replay below; there is no extra DP averaging factor or microbatch-average division.

## Actual resolved A/B flags

Both original formal stdout files are locally retained:

- A: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/A-exp-1107-173758-712234-complete.log`
- B: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/B-exp-1107-173758-806531-complete.log`

Both record `TP=2/DP=4/CP=1/PP=1`, `calculate_per_token_loss=True`, `ddp_average_in_collective=False`, `use_distributed_optimizer=True`, `num_distributed_optimizer_instances=1`, `overlap_grad_reduce=False`, `accumulate_allreduce_grads_in_fp32=True`, `grad_reduce_in_bf16=False`, `bf16=True`, `fp16=False`, `loss_scale=None`, `optimizer_cpu_offload=False`, and the accepted D12 TIS settings. Representative native stdout lines are identical between A/B: DP `259`, DDP averaging `268`, BF16 `133`, FP16 `469`, explicit loss scale `684`, distributed-optimizer instance count `897`, overlap reduction `955`, distributed optimizer `1893`. These are observed runtime flags, not guessed recipe defaults. They are not yet observation of the constructed gradient buffer's scaling factor.

The actual launch receipts are `evidence/first-round/student/A/exp-1107-173758-712234/launch.json` and `evidence/first-round/student/B/exp-1107-173758-806531/launch.json`; native completion receipts are their `training.json` files. The frozen image/config owner is `training_config_h200.json`. Parent extraction receipt `evidence/normalization-source-exp-1107-235600-946937.json` records `megatron-core=0.19.0+eb547f33e`, `torch=2.14.1+cu130`, producer Python `3.12.16`; exact files are retained under `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937/`. The probe checks source paths and sizes against that receipt before executing unchanged AST nodes. It does not alter installed modules.

## Verification performed so far

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python `3.12.13`, torch `2.11.0+cu130`; CPU-only. `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`.

The synthetic probe's first microbatch executes unmodified Miles `loss_function`, `apply_opd_kl_to_advantages` and the real D12 custom MIS hook. Only selected log-probabilities/model outputs are replaced. The native objective returns numerator `0.4`, original token count `3`, survivor count `2`, and gradient `[1.100000038743019, 0.5500000193715096, 0.36666667958100635, 0.2750000096857548]`; the explicit numerator-gradient reference is `[1.1, 0.55, 0.3666666666666667, 0.275]`. Largest absolute gradient discrepancy is `3.8743019e-8`; native policy arithmetic includes FP32 conversion. Local loss-seam check: **PASS**, not a global final-scaling result. The first preparation attempt failed because the synthetic batch lacked `unconcat_tokens`; supplying the required native batch field repaired the probe, not production behavior.

### Eight-rank native schedule/reducer/final-scaling replay

Artifact: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-native-token-normalization-host-A.json`. Raw log: the adjacent `.log` file. Reader/execution versions are Python `3.12.13`, torch `2.11.0+cu130`; the pinned source producer versions above are distinct.

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Original counts by DP rank / two microbatches | `3+6`, `4+8`, `5+10`, `6+12` | Same; global `54` per TP coordinate | PASS |
| TIS rejection preserves denominator | Some rejected tokens; one wholly TIS-rejected microbatch still counts its original tokens | `29` survivors vs `54` original; DP3/microbatch1 contributes zero but counts `12` original tokens | PASS |
| Native DDP constructor scaling | `1.0`, no collective average | `1.0`, `average_in_collective=False` | PASS |
| Native collective | DP4 synchronous FP32 SUM reduce-scatter | Genuine Gloo `reduce_scatter_tensor`, SUM, size4, asyncFalse | PASS |
| Native final token scaling | Broadcast PP1; SUM DP4; scale by `1/54` | Global count `54`, FP32 reciprocal `0.018518518656492233` | PASS |
| Explicit global mean | Nonuniform numerator `25.85 / 54` | Reference mean `0.4787037037037037` | PASS |
| Complete post-reduce/scaling gradient | `[3.148148148148148, 2.1212962962962963, 1.7790123456790123, 1.6078703703703703]` | `[3.1481480598449707, 2.1212964057922363, 1.7790123224258423, 1.60787034034729]`; max absolute error `1.0949594e-7` | PASS |
| Wrong-survivor denominator negative control | Native path with intentionally incorrect count29 must disagree with correct count54 | Wrong mean `0.8913793103448275`; maximum gradient distance `2.713921070098877`; own-reference error `1.6442661e-7` | PASS: wrong denominator detected |
| A/B actual config consistency | All30 required normalization flags match the accepted configuration | All30 match in both preserved formal stdout files | PASS |

The negative control intentionally substitutes survivor counts only in the probe callback, then executes the same unchanged native schedule/reducer/finalizer/scaler. It does not change the production path. This tests the final gradient, not just a local loss SUM. Gradient tolerance is the existing Miles native loss snapshot absolute tolerance `2e-6` (`tests/fast/backends/training_utils/loss/loss_test_utils.py:288-292`); observed errors are below it.

Two scoped preparation failures were corrected without production changes: the existing `make_parallel_state` fixture must be called before initializing an eight-rank WORLD, and original masks must use native `torch.int` tensorization (`miles/backends/training_utils/data/rollout.py:57-59`) so schedule integer count accumulation remains valid. The original float-mask fixture failed with `RuntimeError: result type Float can't be cast to the desired output type Int`; changing the synthetic fixture to the inspected native dtype repaired it.

## Parent-owned pinned-image CPU run — PASS

Run from `/data/ycfeng/sota-engine/miles` inside the frozen image. This command requires no GPU and creates no optimizer:

```bash
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
  /opt/sglang/bin/python3 -B -m torch.distributed.run --standalone --nproc-per-node=8 \
  --module tests.manual.agent_opd.probe_qwen35_token_normalization \
  --pinned-source /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937 \
  --source-receipt task_memory/task_2026-11-06_qwen35_three_pairs/evidence/normalization-source-exp-1107-235600-946937.json \
  --launch-receipt task_memory/task_2026-11-06_qwen35_three_pairs/evidence/first-round/student/A/exp-1107-173758-712234/launch.json \
  --native-stdout /data/ycfeng/tmp/opencode-v2-tmp/opencode/A-exp-1107-173758-712234-complete.log \
  --report /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-native-token-normalization-A.json
```

The successful host command is identical except for `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python` in place of `/opt/sglang/bin/python3`, adding `timeout 180s`, `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode` and `OMP_NUM_THREADS=1`, and naming the JSON output `qwen-native-token-normalization-host-A.json`; stdout/stderr were redirected to the adjacent `.log`. The probe emits `replay_status=PASS` but `status=INCOMPLETE` deliberately: a passing synthetic reducer replay is not full historical CUDA qualification. `pinned_torch_runtime` records whether the executing torch version matches the extraction producer.

The parent executed this command in job `exp-1108-001008-300177`, with `--report` set to `task_memory/task_2026-11-06_qwen35_three_pairs/evidence/native-token-normalization-exp-1108-001008-300177.json`. The same basename `.log` retains complete stdout/stderr. Submission used the frozen H200 config image, 16 CPUs, 0 GPUs, 64000Mi memory, non-preemptible `step_main`, and local mount `100.96.128.195:/data/ycfeng:/data/ycfeng`; submitter cwd was `/data/ycfeng`. Worker environment added `CUDA_VISIBLE_DEVICES=""`, `OMP_NUM_THREADS=1`, the configured CUDA-compat library directory, and job-local `TMPDIR`.

**Observed:** Python 3.12.16, torch 2.14.1+cu130, `pinned_torch_runtime=true`, eight ranks, `replay_status=PASS`. Every rank reports denominator 54, survivors 29, two real DP4 FP32 SUM reduce-scatter calls, unit bucket/loss scaling, and the table's final gradients. Maximum absolute gradient error is `1.0949593987064077e-7`; wrong-denominator gradient distance is `2.713921070098877`. Parent assertions check all eight rank records. This verifies the selected normalization semantics, without claiming historical CUDA gradient values.

Independent personal API receipt `evidence/review-verification-platform-20261108.json` confirms job/default Succeeded, finish `2026-11-07T16:11:00Z`, correct pinned image/source/identity, zero GPU request, no stop annotation or stop timestamp. `evidence/native-normalization-A-B-flags.json` separately records all 30 matching resolved flags from both actual formal stdout files. A shared semantic replay applies to those identical normalization settings; it does not substitute A's training counts for B's.

## Remaining evidence limits

1. The host and pinned executions are distinct and both retained. Only `exp-1108-001008-300177` is labeled exact pinned-runtime execution.
2. No historical native A/B gradient buffer before and after finalizer was observed. The synthetic native reducer replay does not retroactively replay full-model CUDA backward, native CUDA allocation/layout, NCCL coalescing/stream ordering, TP layernorm gradient sums, gradient clipping or optimizer consumption. CP1/PP1 are the actual topology; CP>1/PP>1 are not qualified. The runtime flags and executed unchanged DDP constructor do prove this topology's configured DP scaling rule, not the values of unretained historical gradients.
3. Real per-step mask/token audit is owned by the independent token-audit agent and is not duplicated here. This report does not infer exact historical denominators from the successful process exit or generated response count.

## 本次任务自己的 check-progress 检查点

### 进展实况

- Source contract、实际 A/B flags、native CPU/Gloo replay 和错误 survivor 分母对照已完成；证据为本报告、脚本及 host JSON/log。
- Parent pinned-image CPU execution 已通过；历史每一步真实 masks/counts 由独立 token-audit collector 处理。完整 Spec 缺口的关闭仍取决于实际逐步审计和针对性复核。

### 主线偏差判断

- 未新增训练、optimizer steps、production edits 或平台操作。Replay 不停留在 loss SUM，已经执行最后的 gradient scaling。
- 准备失败只修复 probe 的 distributed fixture 生命周期和 inspected native mask dtype，没有 ABI 安装或行为 fallback。当前没有未结束的重试。

### Spec/Ticket 健康度

- D12 的原始 token global denominator 与 design.md:140 的每一步真实 token 记录是不同验收项。当前 replay 解决前者的 source/scaling contract，不能替代后者的历史 artifact audit。
- 当前子任务没有 tickets；没有证据支持把历史 CUDA qualification 直接标为 PASS。保留 INCOMPLETE，避免错误扩大结论。

### 下一步纠偏

1. Parent 合并独立 token-audit 的真实 per-step evidence，按原始 D12/design140 要求完成针对性复核。
2. 保留 replay 的历史 CUDA 边界；不为已经验证的语义增加训练或重复 replay。
