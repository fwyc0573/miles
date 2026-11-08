## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record the approved two-indentation dependency patch, final34-check CPU verification, source preflight, soft-only observer checks, and scoped progress checkpoint. |

# T02-CAPACITY-FIX: Megatron scoring output lifetime

## Result and scope

**CPU verification PASS; actual same-256-bank GPU red/green remains pending.** The source change consists only of moving the two existing `del output_tensor` statements outside `not forward_only` in the pinned PP1 schedule. No logits/probability math, allocator behavior, collective, topology, context budget, bank budget, TIS rule, or current-student rescoring is changed. No GPU, platform, cloud, SSH, or authentication operation was performed by this owner, and no commit was made.

The authoritative dependency/source/diff identities are in `tests/manual/agent_opd/megatron_scoring_lifetime.json`; the exact diff is `tests/manual/agent_opd/megatron_scoring_lifetime.patch`. The qualified retained source used for CPU checks is `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937/core/pipeline_parallel/schedules.py`. It was read only. Temporary fixture checkouts, not an installed Megatron environment, were patched by the tests.

## Interface and retained evidence

`training.release_scoring_output` is an optional JSON boolean. Omission leaves the existing launcher unchanged. Explicit `false` verifies the original pinned source without changing it; explicit `true` applies the verified patch or accepts its exact already-patched state. Both explicit contrast modes enable the same soft-only before-log-prob observer. A red run refuses an already-patched checkout rather than restoring or discarding any source changes.

The student `_prepare_training` preflight precedes Ray startup and native-driver submission. It validates the configured qualified image, full dependency commit, installed distribution version, original Git-HEAD source hash, current source hash, and diff hash. Actual container-image/platform identity still requires the parent's worker receipts.

At `<student-run>/megatron_scoring_lifetime/source/`, it retains `schedules.before.py`, `schedules.after.py`, the exact `.patch` and `.json`, and append-only `preflight.jsonl`. The launch receipt includes the same preflight result. The observer independently records each actor's schedule path/hash and expected hash under `<student-run>/megatron_scoring_lifetime/observations/rank_<rank>.jsonl`.

Observer events include scoring-pass/forward-microbatch indices, a weak-reference alive verdict, prior/full output storage bytes and pointer, and allocated/active/reserved/inactive-split allocator bytes. It uses ordinary module hooks at forward entry, vocabulary-projection entry, and forward exit. It never retains a tensor, synchronizes, or returns a replacement output. Gradient-enabled training is not observed. Installation, memory, source-identity, and receipt failures are reported as unverified and never escape into training; partially registered hooks are removed on installation failure.

## Commands and observations

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python **3.12.13**, PyTorch **2.11.0+cu130**, pytest **9.1.1**. CUDA was not used.

```bash
MILES_PINNED_MEGATRON_SCHEDULE=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937/core/pipeline_parallel/schedules.py \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_megatron_scoring_lifetime.py tests/fast/test_swe_launcher.py \
  -q -p no:cacheprovider \
  --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/scoring-lifetime-tests-verified \
  --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/megatron_scoring_lifetime_cpu.xml
```

Final observed **34 PASS**, **0 FAIL**, **0 skipped**, pytest duration **0.87 s**. The retained JUnit artifact is `evidence/megatron_scoring_lifetime_cpu.xml`. The actual pinned AST functions `forward_backward_no_pipelining`, `forward_step`, `forward_step_calc_loss`, and `backward_step` execute on CPU. SDK metadata/groups, the unused CUDA token counter, and unused MTP import are mocked; no schedule implementation is copied. The callback uses a CPU log-softmax reference, not the CUDA fused scorer.

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Forward-only old-output lifetime | Red retains one prior output; green retains none | Red `[0,1,1]`, green `[0,0,0]`; both final alive count0 | PASS |
| Callback ordering | Same three native microbatch indices | `[0,1,2]` in both | PASS |
| Callback outputs | Exact equality | `rtol=0, atol=0` passes for all output tensors | PASS |
| Native backward control | Same gradients, no lifetime regression | Exact gradient/output equality; live counts `[0,0,0]` in both | PASS |
| Preflight | Exact source, identity and diff; idempotent green; no destructive red reset | All identity/drift/idempotency tests pass | PASS |
| Observer | Weak references only; transparent forward/backward; failures isolated | Memory/write/source/registration fault checks pass | PASS |
| Launcher | Default unchanged; red/green add only observational arguments | Exact original argv preserved after removing three observer arguments | PASS |

Initial 28-check iteration also passed. The Python environment lacked `ruff` and `black` modules; no packages were installed. Existing lint tools at `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages` were used instead:

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check \
  tests/manual/agent_opd/megatron_scoring_lifetime.py \
  tests/manual/agent_opd/megatron_scoring_lifetime_observer.py \
  tests/manual/agent_opd/run_swe_opd.py tests/fast/test_megatron_scoring_lifetime.py

PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check \
  tests/manual/agent_opd/megatron_scoring_lifetime.py \
  tests/manual/agent_opd/megatron_scoring_lifetime_observer.py \
  tests/fast/test_megatron_scoring_lifetime.py
```

The first Ruff check found one unused test import, subsequently removed; the final check passed. Black's final check passed for all three new Python files; formatting changes were applied only to new owned files, and existing dense launcher formatting was preserved. `git diff --check` passed. A final independent source read still matched the manifest's original hash, confirming that the retained pinned schedule was not modified.

## Remaining native gate

Parent packaging check: staged whitespace validation flagged two blank context lines in the patch asset. Their context-space markers were removed (Git accepts empty context lines), and the patch artifact SHA was updated; original/patched schedule hashes and the two source edits are unchanged. The same34 tests passed again using `--basetemp=/data/ycfeng/tmp/scoring-lifetime-packaged-20261108`; JUnit is `evidence/megatron-scoring-lifetime-packaged.xml`, with raw output `/data/ycfeng/tmp/scoring-lifetime-packaged-20261108.log`. Both actual red/green configuration files also passed combined custom-hook CLI registration with replay+observer enabled; `evidence/capacity-replay-combined-registration.json` retains the complete argv and confirms that the only configuration difference is `training.release_scoring_output`.

The parent owns canonical-bank replay and resource operations. Use separately allocated, freshly pinned red/green workers, the same actual256-trajectory bank, identical TP2/DP4/CP1, 128K limits and scientific configuration. Confirm source receipts and every actor's observed SHA, red/green prior-output lifetime and allocator counters, the exact OOM versus completed scoring, current completion log-prob/TIS numerical checks, real backward and optimizer acknowledgement, and the next scoring pass. A CPU pass does not prove H200 capacity, CUDA fused-scoring equivalence, throughput, or a formal200-update run.

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 0｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| T02批准的两处输出引用释放 | PASS | 精确patch/hash及CPU生命周期对照 |
| 学生preflight与soft-only观测 | PASS | 身份、幂等、故障隔离及argv检查 |
| CPU验证与复现记录 | PASS | 34项通过，JUnit及本报告 |
| 同一实际256-bank GPU对照 | TODO | 父会话与独立replay owner继续；不属于本owner的资源权限 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** T02-CAPACITY-FIX明确授权至今｜**当前前沿：** 实际bank replay接入与native GPU red/green

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅满足明确要求的CPU/soft-observer验证；现在停止扩展 |
| D2 细节反复重试 | CLEAR | 运行检查无失败；单次unused import修正，不是容量重试 |
| D3 支线问题修补 | CLEAR | 未触及旧probe、replay、gradient或allocator |
| D4 可并行任务停滞 | CLEAR | replay与GPU由独立owner承接，未建立新串行依赖 |
| D5 超范围镀金 | CLEAR | patch只有两处缩进，观测与archive由本次请求明确要求 |
| D6 分析空转 | CLEAR | 已交付可接入源码及实测CPU对照 |
| D7 路线违背 | CLEAR | 遵循requirements第80–82行；未选择TP4或改变科学配置 |

**文档检查：** 对本次切片检查S1–S6，未发现明显缺陷；Ticket02原生容量仍未勾选，与现有证据一致。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动。
**需停止的偏离行为：** 无。

**接下去的路线：**
1. 父会话接入独立replay模块并执行获批GPU对照 → 完成标志：同一256-bank真实容量、数值、optimizer ACK及下一次scoring证据。
2. 本owner停止继续扩展工具；保留最小patch和当前验证产物，等待具体原生失败证据。

## 4. 最值得关注的 3 点

1. CPU生命周期问题已消除；这不是H200容量PASS。
2. 源码、身份与数学保持可核查；红色模式不恢复或丢弃任何已修改源码。
3. 原生GPU对照仍是Ticket02的必要前沿，正式cell不能据此提前验收。
