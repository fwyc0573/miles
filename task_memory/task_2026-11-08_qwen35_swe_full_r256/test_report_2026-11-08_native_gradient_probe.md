## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Reproduce the actual combined CLI registration failure, share one complete schema across all probe hooks, and pass 13 CPU checks including real registration and frozen/soft-observer regressions. |
| 2026-11-08 | Implement the existing-hook native gradient observer, validate12 CPU mechanics checks, prepare the separate3-update probe configuration, and specify native numerical acceptance boundaries. |

# Native gradient probe — T02-NATIVE-GRADIENT

## Outcome

**Probe implementation, real combined CLI registration and CPU mechanics PASS; actual native Qwen gradient acceptance remains unverified.** Parent's first real probe failed before training because the original observer schemas partially overlapped at CLI registration; that failure provides no gradient verdict. The assembly cause is fixed below. No native core, existing SWE rollout/TIS/training modules, launcher, actor/HF code, shared task records, GPU/platform/cloud/SSH or credentials were changed or accessed. No commit was made. The probe saves only small JSON gradient/settings observations, not model weights, optimizer weights, moments or complete state dictionaries. Normal recipe checkpoint behavior is left unchanged, not augmented by the observer.

Deliverables:

- `tests/manual/agent_opd/probe_swe_native_gradients.py` — three existing-hook entrypoints, native finalizer/scale observations and local config preparation.
- `tests/fast/test_swe_native_gradients.py` — CPU-only regression checks, explicitly not native gradient proof.
- `evidence/training-native-gradient-config.json` — generated copy of the existing integration recipe; explicit smoke3 updates/8 turns/2 bank uses, same model/data/seed/optimizer/TIS values.
- `evidence/training-native-gradient-probe-acceptance-20261108.log` and `training-native-gradient-typed-final-20261108.log` — retained CPU checks.
- This report — evidence contract, commands, numerical pass conditions and limits.

## Why these seams

Native `miles/backends/megatron_utils/model.py:599–605` invokes the before-train hook after zeroing gradients and before forward/backward. `setup_train_iteration_config:754–773` configures the real `finalize_model_grads_func`; the before hook wraps that callable, preserving the native empty-cache wrapper and actual underlying finalizer. The hook handles that configuration being reset at each rollout; it does not multiply-wrap an existing observation.

The native TIS call at `miles/backends/training_utils/loss/hub/losses.py:260–275` passes detached trainer-scored `s`, not the live training `l`. Substituting this argument would change D4. Instead, the probe delegates `swe_tis.apply_tis` once, then attaches read-only hooks to the actual `pg_loss` graph. Native `policy_loss` constructs `s-l`, applies `nan_to_num`, and then enters PPO math. Its saved actual `NanToNumBackward` input exposes the `SubBackward` boundary with an absent baseline edge and the live concatenated train-logprob edge. The bounded search stops at the CatBackward boundary; it does not traverse/copy the model graph or inject new tensors into training. It works with the inspected AOTAutograd PPO boundary as well as uncompiled math. If the native graph differs, evidence becomes unverified and training continues; there is no alternate scientific computation or fallback graph.

Read-only `SubBackward.register_hook` captures the actual gradient of the concatenated live training logprobs. A separate `pg_loss.register_hook` captures the incoming gradient after actual TIS/local loss reduction. Both callbacks return `None`, and neither changes an input gradient. Graph observations select at most8 original eligible retained positions and8 original eligible rejected positions per microbatch. Matching source scores and advantages are sampled later from the real metadata-indexed native data iterator, not reconstructed teacher forwards.

The original finalizer wrapper temporarily wraps only each actual DDP instance's `scale_gradients`, calling the original method exactly once with its original factor. It samples `parameter.main_grad` immediately before and after that method and retains its return value. It reads the actual `num_tokens` tensor before native broadcast/allreduce and at/after actual scaling. Temporary scale wrappers are restored even when native finalization throws; true native failures are not swallowed.

Inspected local pinned source (a previously retained copy, not a new platform read):

- `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937/core/distributed/finalize_model_grads.py:466–583` — native DP gradient sync, TP/embedding sync, token broadcast, DP-CP SUM, and actual `1/clamp(num_tokens,1)` scaling.
- Same directory, `distributed_data_parallel.py:177–183,586–589` — per-token DDP prohibits averaging and sets the buffer gradient pre-scaling to1; `scale_gradients` delegates to the real buffers.
- Local installed `/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/megatron/core/optimizer/optimizer.py:488–506,1429–1482` — wrapper/chained optimizer state and parameter-group ownership.
- Local installed TransformerEngine `pytorch/optimizers/fused_adam.py:177,563–587` — AdamW mode and actual per-group step counter, including empty groups. Torch AdamW uses per-parameter `state['step']`; the probe records whichever existing counters the real leaf provides, without inventing missing zero counters.
- `miles/backends/megatron_utils/megatron_to_hf/qwen3_5.py:63` — actual Qwen native final norm name `module.module.decoder.final_layernorm.weight`; the profile uses the exact suffix `decoder.final_layernorm.weight` and requires a unique observed match.

Runtime receipts include actual delegate source paths and SHA256s. The current worker's pinned implementation is not assumed to match the local inspected copy without checking that runtime provenance.

## Explicit hook and launch configuration

The existing `run_swe_opd.py:122` carrier passes native flags from `config['tis']`; no launcher change is needed. The generated profile installs:

```text
custom_megatron_before_train_step_hook_path = tests.manual.agent_opd.probe_swe_native_gradients.before_train
custom_megatron_optimizer_step_hook_path = tests.manual.agent_opd.probe_swe_native_gradients.optimizer
custom_tis_function_path = tests.manual.agent_opd.probe_swe_native_gradients.tis
```

New observer-only custom-config fields are owned by `GradientProbeConfig`: evidence directory, exact parameter suffix, slice size(default8), bounded graph-node search(default64). `NativeGradientProbeConfig` composes that owner with the unchanged `SweReplayConfig` and `SweTISConfig`. All three observer hooks declare exactly this same config class. The first actual hook registers the complete namespace once; the other two reuse that class, and later native SWE hooks share all their existing identical flags. No flag is copied, registered piecemeal, given a different default, or moved into the parser. Actual typed orchestrator and trainer JSON transport/merge were also tested, including all three hook views.

The optimizer wrapper retains `training_protocol`. Its explicit observational adapter restores only the declared delegated native TIS callable/config for the original protocol validator. All existing original-model/source/rollout/reward checks, thresholds, objective, optimizer, scheduler, successful-budget and formal-vs-smoke checks still run. A changed threshold is rejected; the adapter does not weaken the original native validator. Original D7 and successful-update ACK run through `swe_training.optimizer_step` exactly once.

CPU-executed profile generation:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.probe_swe_native_gradients \
  --config task_memory/task_2026-11-08_qwen35_swe_full_r256/integration_config.json \
  --output task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-native-gradient-config.json \
  --evidence-dir /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-native-gradient-live \
  --parameter-suffix decoder.final_layernorm.weight
```

Observed generation completed successfully, with the existing optional `deep_ep is not installed` warning. Inspection verifies3 successful updates,8 slots,2 uses, original seed1234/rollout_seed1729, identical weights/data/optimizer/thresholds and all three explicit hook paths. The profile is a separate file; active capacity configurations/core were not modified. Use a unique evidence directory if repeating the probe.

Parent-only launch through the existing admission/worker lifecycle(not executed here):

```bash
python -m tests.manual.agent_opd.submit_swe_opd \
  --config task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-native-gradient-config.json \
  --pair A --protocol r256 \
  --receipt task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-native-gradient-admission.json
```

Parent must use its existing qualified launcher interpreter, mounted source and pinned environment; the command above is not authorization to bypass quota or create another training stack. Expected successful sequence is bank0 visit1 → bank0 visit2 → bank1 visit1. This is not a formal256-turn/50-visit/200-update run.

## Evidence seam and native pass conditions

For the expected TP2/DP4/CP1/PP1 worker, eight per-rank files are written under the configured local evidence directory as `native_gradients_rank_<actual global rank>.jsonl`. No observer introduces an allreduce, broadcast, barrier, process group or model forward. Process-group ranks/size/backend calls are local metadata reads. Existing native/SWE collectives remain delegated unchanged.

Events join on actual rank, `rollout_id`, `step_id`, and per-microbatch `call`. `live_graph_source_values` additionally records actual sample indices/flat positions; optimizer-boundary metadata carries bank/visit/successful-before/slot/sample-index. `optimizer_ack.native_result` preserves the real successful signal and actual global original/survivor counts.

| Required native observation | Passing condition |
| --- | --- |
| Live source and detach | `l`'s actual graph edge is present; baseline edge/gradient is absent. Source teacher, behavior, scored-student, advantages and original/survivor mask flags show no gradient. Live native KL and pre-TIS PG tensors require gradients. Every expected rank/microbatch is represented; missing records are unverified, never zero. |
| Incoming TIS gradient | Actual `dLoss/d(pre-TIS pg_loss)` equals binary original∩TIS mask times the native backward multiplier. For this BF16, CP1, per-token path that multiplier must be measured as1, not microbatch/sample/survivor normalization. Rejected eligible positions must have zero incoming/live-logprob gradients. Require at least one nonzero retained gradient and one actually rejected sample position in the real run. |
| Actual `dLoss/dl` | Use observed actual native `s-l` and source advantage `a=q-s`. With `r=exp(-(s-l))`, the unclipped derivative is `-a*r`; it is0 when `a>0,r>1.28` or `a<0,r<0.8`, then multiplied by observed incoming PG gradient. Check sampled native gradients at absolute tolerance1e-6/relative1e-5(FP32). Verify measured `dLoss/dl = -dLoss/d(s-l)`. Do not fabricate an active clipping case if native ratios remain1; nonfinite or exponent-saturation cases are unverified rather than silently assigned a derivative. |
| Native token denominator | Native local finalizer count equals this rank's summed original eligible microbatch counts. Actual global finalizer count equals their SUM over the actual DP-CP group, counting each TP group separately, and equals ACK `original_tokens`. All integer equalities are exact; survivor/sample count is not a denominator. |
| Native distributed scaling | DDP runtime config has `average_in_collective=False`; actual buffer gradient pre-scaling factors are1. Record actual DP/TP groups and delegate provenance. The actual passed finalizer factor equals `1/global ORIGINAL count`, relative tolerance1e-7(FP32 scalar). At every observed real DDP scale call, sampled `main_grad_after = main_grad_before * actual_factor`, relative tolerance1e-6/absolute1e-8, with a nonzero finite sampled gradient. |
| Optimizer/settings | Record actual Megatron wrapper and leaf optimizer classes. Each actual group matches native grouping: LR2e-6, betas(.9,.98), eps1e-8, WD according to its actual native decay/no-decay group(0.1 or0); TE/APEX AdamW mode must be1/true where supported. Unknown settings/counters are unverified, not fabricated defaults. |
| State continuity | Same wrapper/leaf optimizer/state-dictionary identities across all3 successful updates; existing per-group/per-parameter step advances1→2→3, with the same sampled initialized state dictionary from update1 through the bank transition. Momentum tensors need not share device/storage identity because native offload transfers them; no moment/weight values are saved. ACK counts and actual metadata verify bank0 visits1/2 thenbank1 visit1. |

**Do not conflate boundaries:** logprob gradients are recorded after local loss reduction but before Megatron parameter finalization. They are not the final DP-scaled parameter gradients. Parameter observations use real DDP `main_grad` only, not `parameter.grad` or a manufactured logprob gradient. Runtime `use_distributed_optimizer` is recorded: if reduce-scatter is active, the parent must restrict any cross-rank SUM interpretation to the owning shard. A non-owned/full-buffer slice by itself must not be claimed to be the final optimizer-owned gradient; exact scale-method multiplication and denominator remain directly observed. Probe errors or incomplete shard ownership do not stop training and cannot be relabelled native PASS.

## CPU verification

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, Torch2.11.0+cu130. All actual tensor operations in these checks use CPU; Megatron/CUDA device execution is not faked. No dependency installation was performed.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_native_gradients.py -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-native-gradient-probe-acceptance-20261108.log 2>&1
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_native_gradients.py -k actual_typed_hook_factory -q > task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/training-native-gradient-typed-final-20261108.log 2>&1
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m compileall -q tests/manual/agent_opd/probe_swe_native_gradients.py tests/fast/test_swe_native_gradients.py
git diff --check
```

Observed: **12 passed in13.66s**, then final expanded typed-view check **1 PASS**; compile and whitespace checks PASS. Coverage includes native CPU policy-loss graph observation and independent expected-gradient equality, AOT-compiled PPO graph discovery, read-only hooks, source detach, broken evidence sinks, exact single delegation/restoration of real scale arguments, native failure propagation, native config reset handling, three real CPU AdamW step/state observations, successful ACK preservation, frozen-threshold rejection and unchanged recipe flag-carrier wiring. CPU finalizer fixtures deliberately mutate a count7→12 to test observation mechanics; those values are not presented as a native DP reduction or native PASS.

Retained initial failures are fixture mistakes: the reused ConfigNamespace is mutable and has no `model_copy`, and the reused native fixture returns full `[1,15,8]` logits rather than a nine-element logprob tensor. The fixes changed only the new test fixture handling/reference gradient, not production semantics. Logs `training-native-gradient-probe-20261108.log` and `training-native-gradient-probe-rerun-20261108.log` retain those failures. The later10-PASS run and final12-PASS run settle the affected mechanism. A nested read-only exploration delegation was attempted but the harness depth limit denied it; the local source inspection was completed directly, with no delegated GPU/private access.

## Actual combined CLI registration remediation

Task ID: **T02-NATIVE-GRADIENT**. Parent reported actual job `exp-1108-183945-095719` failed at `miles/utils/args/custom_function.py:114` **before scientific training started**. The local tail contains only wrapper exit; no additional cloud/business log was read here and no gradient result is inferred.

The initial observer bindings declared only the four probe flags on `before_train`, then probe+SWE flags on `optimizer`, then probe+TIS flags on `tis`. The real parser prohibits partial hook overlap: all of a hook's flags must already be identically registered, or none. Previous typed-view tests bypassed that registration boundary and therefore did not cover this defect.

The new tight test reads the actual generated `evidence/training-native-gradient-config.json`, obtains native argv through unchanged `run_swe_opd._training_args`, registers actual `AllConfig` flags, sets the real process argv, and calls **`add_user_provided_function_arguments` without replacing registration**. It preserves the actual `AllConfig` hook order:

```text
probe.before_train → probe.optimizer → swe_replay.score_teacher
→ swe_replay.post_process_rewards → swe_hf_export.post_save → probe.tis
→ swe_inputs.NativeSWEDataSource → swe_replay.SweReplay → qwen_alignment.generate
```

RED reproduced the exact partial-overlap `ValueError` at line114: **1 failed,12 deselected in2.89s**. The fix replaces the separate probe schemas with one shared `NativeGradientProbeConfig` for all three bindings. GREEN completes the real combined registration, parses every SWE/TIS/probe flag, checks one action per complete schema field, resolves all actual hook configs, verifies common-schema equality, and retains original replay budget/D4 thresholds: **1 passed,12 deselected in2.47s**. The complete affected suite is **13 passed in13.85s**, including actual typed views, threshold rejection, source detach and all soft observer/native-failure checks.

Tight RED/GREEN command(run before and after the schema fix; separate retained logs):

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_native_gradients.py \
  -k combined_native_hook_cli_registration -q -s
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_native_gradients.py -q
```

Evidence: `evidence/training-native-gradient-registration-red-20261108.log`, `training-native-gradient-registration-green-20261108.log`, and `training-native-gradient-registration-suite-20261108.log`. After expanding the one-action assertion to every field in the complete shared schema, the final identical registration command also passed **1 check in2.52s** (`training-native-gradient-registration-final-20261108.log`); final compile/diff-check PASS. The existing generated probe JSON requires **no flag/value change**; no native parser/core, fallback, duplicate-flag exception, relaxed validation or scientific parameter was changed. Original D2 remains completion-only: unchanged eligible completion tokens and fresh current-student scoring, excluding prompt/prefix/padding, with no new estimator or sampling path.

This is the actual CPU-safe custom-registration portion of the production parser, not a rerun of GPU-dependent Megatron validation or a native backward. Parent may rerun the unchanged generated profile after syncing the new schema binding; actual Qwen gradients remain pending.

## Remaining native work

Parent must run the corrected mounted module with the actual Qwen model, pinned Megatron/TE, accepted sources and native topology, retain all eight rank receipts, then independently check the numerical criteria above. The first real worker attempt stopped at CLI assembly before scientific training; the corrected assembly has not reached real Qwen backward. Native class/source/shard observations, real nonzero/rejected token gradients, actual denominator/factor, parameter scaling and actual optimizer continuity remain pending. Existing smoke scalar agreement and CPU test results do not close those seams. No new launcher wiring, model forward, objective/normalizer implementation or weight artifact is needed.

## 1. 规划完成情况

**汇总：** PASS2｜BLOCKED/FAILED/SKIPPED0｜TODO1（本次委派范围）。

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 最小原生hook observer与独立probe配置 | PASS | 三个existing hooks显式代理production；source core和active配置未改。 |
| CPU机制、typed-view与真实combined registration核验 | PASS | 13项检查包含实际argv/hook顺序注册；compile/diff检查通过，仍不是native gradient PASS。 |
| 实际Qwen backward/finalizer/optimizer验收 | TODO | 父会话运行并独立核验上述数值条件。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 首次observer交接至实际CLI assembly修复｜**当前前沿：** 父任务02梯度/容量与03原生评测。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 紧凑真实registration测试直接复现运行阻塞；13项通过后停止扩展。 |
| D2 细节反复重试 | CLEAR | 同一实际argv精确RED→单一schema修复→GREEN；无parser绕过或训练参数试错。 |
| D3 支线问题修补 | CLEAR | 无active core、launcher、评测或平台修复。 |
| D4 可并行任务停滞 | CLEAR | 本次只拥有observer assembly；用户明确由父会话运行GPU，其他评测代理独立拥有文件。 |
| D5 超范围镀金 | CLEAR | 一个observer模块，无新增训练/评测框架、collectives或额外权重保存。 |
| D6 分析空转 | CLEAR | source检查落到一个schema修复及13项CPU检查；既有profile无需改参数。 |
| D7 路线违背 | CLEAR | 无GPU/private访问或commit；保留全部S4/正式与smoke边界。 |

**文档检查：** S1–S6未发现本委派范围内缺陷；02拥有实际梯度验收，缺失证据不另造ticket或降低标准。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 父会话运行独立A/r256梯度probe → 完成标志：完整rank/call证据满足本报告S4数值标准，不以scalar loss或CPU梯度替代。
2. 并行：继续已有256容量与03评测原生核验；各自已有验收标准不变。

## 4. 最值得关注的3点

1. 实际`dLoss/dl`和实际native参数`main_grad`是两条不同证据，不混用。
2. observer不新增collective、不修改loss/mask/梯度；缺证据或I/O错误保持soft/unverified。
3. 三个hooks已走现有flag carrier；父会话只需同步新模块并使用独立probe配置，真实GPU验收仍未完成。
