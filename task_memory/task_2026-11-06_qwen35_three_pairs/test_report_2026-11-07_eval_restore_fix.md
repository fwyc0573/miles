## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Record pinned core, Ray and ordinary-publication checks; distinguish a separate fake-HF fixture failure and retain actual-TMS/IPC qualification as pending. |
| 2026-11-07 | Record the scoped native restore repair, injected-remap red/green checks, cancellation checks, and the unresolved actor-lifecycle error boundary. |
| 2026-11-07 | Read-only follow-up: retract blanket lifecycle-fatal classification; verify safe continuation, existing unavailable-worker handling, and one late residency-flag defect with an in-memory-only cause correction. |
| 2026-11-07 | Apply the approved native residency assignment move; persist first-PG-failure/fatal-path regression, record 1 FAIL/2 PASS → 3 PASS and 63 affected core checks PASS; mark architecture BLOCKED superseded. |

# QWEN-P3-EVAL-RESTORE-FIX

## Outcome and scope

The two confirmed restore omissions and the measured late residency-flag defect are repaired in their existing owners. The approved assignment move has a persistent red→green regression, and all **63 affected core checks pass**. The earlier architecture **BLOCKED** verdict is **superseded**, not a remaining decision: D8 permits auxiliary faults when training remains healthy; native persistent-PG/unavailable-worker failures remain fatal through their existing path. This is not full formal-run qualification: real TMS execution and pinned-runtime validation remain parent-owned. Historical sections preserve the earlier evidence; the approved implementation and latest checkpoint below are current.

Read the task's requirements, plan, historical restore report, historical TORCH scores/actual C flags, root AGENTS.md, and all ten repository Markdown rule files. Requirements R3/R4/R6 were reread before handoff. No GPU, platform, SSH, cloud, Git, delegation, manual-probe, HF-reload, or parent-document operation was performed. Only the six owned Python files and this new report were edited.

## Parent pinned verification

The unchanged pinned image ran the implemented core changes with0 GPUs. `exp-1107-103043-142033` first passed60 core checks, but7 Ray cases failed fixture setup because the parent command set `CUDA_VISIBLE_DEVICES=""` while the existing CPU fixture declares8 logical GPU scheduling resources. Removing that command override preserved the fixture contract; `exp-1107-103428-476945` passed all7 Ray cases in106.86s and7 existing ordinary snapshot/publication cases in15.24s. Its log also contains the independent2-case ResourceTracker closure. [Complete corrected log](evidence/restore-exit-contracts-exp-1107-103428-476945.log).

After the late-PG residency correction, `exp-1107-125038-984696` ran `tests/fast/test_train.py`, `tests/fast/backends/megatron_utils/test_score_log_probs.py`, monitoring and two HF origin nodes. All63 affected core cases pass within **133 passed /1 failed**,56.32s total. The sole failure is the fake-HF test's actual isolated-interpreter guard encountering a preexisting child, not a core restoration assertion; it is separately owned by the receipt-test slice. [Complete log](evidence/restore-final-contracts-exp-1107-125038-984696.log). No actual Qwen optimizer step was executed by these checks.

The Ray file's stage-b CPU estimate is now120s based on its106.86s measured pinned whole-file runtime. This is scheduling metadata, not a new timing run. Phase review found no new core code defect and closed the consumer P1 at source/CPU scope; real tiny TMS/IPC and formal Qwen validation remain pending.

## Changes and reasons

| File | Change | Expected result |
| --- | --- | --- |
| `train.py:42–65,104–112,175–178` | Thread the existing rollout executor through the scorer callback. Resume released weight storage, run the complete existing `placement_group.update_weights` transaction with omitted `rollout_id`, then resume only the released KV/graph tags. | Restore actual engine weights and native consumed-version bookkeeping without inventing a publication API or changing actor weight version. Weight-only offload must not resume unreleased KV storage. KV-only/no-offload must not publish. |
| `miles/backends/megatron_utils/actor.py:664–666` | After the scorer wakes an offloaded actor, call its existing `_switch_model("actor")` restore. | Forward uses actor parameters rather than newly mapped, non-backed parameter storage. |
| `actor.py:1207–1208` | Skip old/rollout actor queue advancement when `rollout_id is None`. | Initialization/restoration publishes no new rollout. Existing checkpoint initialization already creates those snapshots; same-version restoration must neither rotate them nor overwrite them from paused live parameters. Ordinary publication with a rollout ID retains its existing behavior. |
| `tests/fast/backends/megatron_utils/score_rpc_fixtures.py:174–180,273,289–327` | Extract the existing restore/sleep/wake/publication methods; use native TensorBackuper; add a CPU parameter-storage remap with separately backed FP32 Adam master/moments. | A boolean wake alone cannot satisfy the regression. Restore must recover actual bytes. No real Megatron DDP/optimizer construction is claimed. |
| `tests/fast/backends/megatron_utils/test_score_log_probs.py:135–208` | Check restored bytes before native forward, exact nonuniform response scores, Adam/master invariants, and real old/rollout snapshots at both update intervals. | Demonstrate both cause repairs rather than only checking the published integer version. |
| `tests/fast/test_train.py:458–547` | Exercise actual `placement_group.update_weights` start/publish/end/executor-version bookkeeping against deliberately erased engine weights and four offload modes; adapt existing soft-failure/cancellation cases to the restore transaction. | Same-version publication restores bytes/logits before graph/KV restoration, while masks/metadata and exact reference cleanup remain unchanged. |
| `tests/fast/test_eval_score_remote_cancellation.py:59–225` | Preserve real Ray scorer/controller fanout; inject restoration failures at six stages and cancel during both remote scoring and same-version publication. | Driver shielding drains workers and restoration; publication failure aborts the native transaction; restoration errors outrank pending cancellation. |
| `test_eval_score_remote_cancellation.py:22` | Register the expanded CPU file as stage-b, estimated 90 seconds. | Its observed 75.62-second test runtime exceeds the repository's 30-second implicit fast-file budget. |

The production driver still logs observer scoring/dump errors only after the restoration transaction completes. New engine restore/publication exceptions remain outside the observer catches in `finally` and propagate fatally. There is no optimizer step, scheduler step, model-version bump, new flag, alternate protocol, counter, or snapshot representation in the repair.

## Executed CPU checks

Working directory: `/data/ycfeng/sota-engine/miles`. Interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3`; Python **3.12.13**, torch **2.11.0+cu130**, pytest **9.1.1**, SGLang **0.5.23**. No conda environment and no CUDA execution.

Common command prefix:

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m pytest -p no:cacheprovider
```

### Meaningful red → green

```bash
# Append to the common prefix:
tests/fast/backends/megatron_utils/test_score_log_probs.py \
tests/fast/test_train.py \
-k 'nonbacked_parameter or same_version_restore or released_weights' -q
```

Before production edits: **5 failed, 2 passed, 53 deselected, 16 warnings in 2.86s**, exit 1. The actor's parameter `.data` was replaced by new zero storage on native wake; all **64/64** entries differed from original parameters, maximum absolute error **1.0099902153**. Both real snapshot queue cases changed unexpectedly (maximum error **1.0** in the first compared changed snapshot). Both released-weight engine cases still differed by maximum **3.0** after native memory resume. KV-only and no-offload controls passed.

After production edits: **7 passed, 53 deselected, 16 warnings in 2.39s**, exit 0. Assertions require exact parameter/score equality (`rtol=atol=0`), more than one distinct response score, unchanged Adam/master tensors and version **7**, unchanged scheduler **19** and last training rollout **2**, and exact snapshot equality at update intervals 1 and 2. Native publication verifies start → actor publish → end → consumed version, followed by only the released KV/graph tags.

Early fixture attempts failed before the acceptance assertions: an incorrectly located WeightUpdateOutput import, a missing UpdatableEngines annotation binding, and a missing logger binding. These were test-boundary defects and were corrected without production edits. A `--tb=short` attempt also collided with the native parser's `--tb-project-name`/`--tb-experiment-name` prefix matching; that argument was removed. The meaningful red result above is the later run with all fixture errors resolved.

### Existing affected scorer/driver and Ray boundaries

```bash
# Append to the common prefix:
tests/fast/test_train.py \
tests/fast/test_eval_score_remote_cancellation.py \
tests/fast/backends/megatron_utils/test_score_log_probs.py \
tests/fast/ray/train/test_score_log_probs.py -q
```

**60 passed, 13 setup errors in 20.27s**, exit 1. Every driver/actor scoring case passed, including the existing two-process Gloo TP/CP/DP mapping and response-mask/metadata/RNG/mode invariants. Ray's socket path exceeded the native **107-byte** AF_UNIX limit under the long TMPDIR. No test/production code was changed to address that environment constraint.

With `RAY_TMPDIR=/data/ycfeng/tmp`, the combined Ray command completed all seven owned restore/cancellation cases, then encountered an existing controller-test failure and timed out at 120 seconds. That optional controller extension was not chased or edited. Its full-suite outcome is INCOMPLETE, not PASS.

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode RAY_TMPDIR=/data/ycfeng/tmp \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m pytest -p no:cacheprovider \
tests/fast/test_eval_score_remote_cancellation.py -q
```

The isolated owned Ray file reported **7 passed, 2 warnings in 75.62s**. The shell timed out during interpreter exit at 90 seconds, so that invocation's process completion remains unverified. The session-scoped repository Ray fixture deliberately does not shut down its cluster. The final affected-only invocation below explicitly shuts down only its own local Ray client/cluster after pytest.

The first explicit-shutdown invocation ran pytest from Python stdin: **66 passed, 1 failed, 16 warnings in 81.20s**, exit 1. Ray shutdown completed, but the existing two-process Gloo test could not spawn from `/data/ycfeng/sota-engine/miles/<stdin>` (`FileNotFoundError`). Its prior normal `python -m pytest` execution passed. The final command uses `python -c` instead of stdin, allowing native multiprocessing spawn while retaining explicit local Ray shutdown:

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode RAY_TMPDIR=/data/ycfeng/tmp \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -c '
import sys
import pytest
import ray
sys.argv = [sys.argv[0]]
status = pytest.main(["-p", "no:cacheprovider", "tests/fast/test_train.py", "tests/fast/test_eval_score_remote_cancellation.py", "tests/fast/backends/megatron_utils/test_score_log_probs.py", "-q"])
ray.shutdown()
raise SystemExit(status)
'
```

Final affected-only result: **67 passed, 16 warnings in 94.90s**, with normal process completion after explicit `ray.shutdown()`. The final run includes the existing two-process Gloo mapping test and all seven real-Ray cancellation/restoration cases. No failing affected test remains. Selected raw output is retained by the harness at `/home/brainpp/.opencode-v2/xdg/data/opencode/shell/3b5f454bcb6ad7d1046e498db20b184ac66f215e/sh_1b3c5af5c001u150RoJfVgLi1q.out`.

Additional read-only checks of existing ordinary-publication queue tests used the common prefix with `tests/fast/backends/megatron_utils/test_old_actor_weight_queue.py tests/fast/backends/megatron_utils/test_shared_ppo_lifecycle.py -k 'weight_publication_rotates or actor_update_preserves_model_version' -q`: **7 setup errors, 60 deselected in 1.34s**, because this CPU environment has no `megatron` package. These tests were not edited or replaced. Parent pinned-runtime qualification must cover them.

AST parsing, final-newline and trailing-whitespace checks passed for all six changed Python files using the same interpreter, with no bytecode writes.

## Earlier actor lifecycle proposal — superseded by read-only follow-up

The following records the first investigation and its then-proposed options, not the current recommendation. The later read-only continuation checks below retract the claim that a switch/forward failure with successful rollback must be fatal or requires an R6 architecture decision.

**Observed unresolved behavior:** injecting `OSError("Injected native actor parameter restoration failure")` at the new actor `_switch_model` call makes native `score_log_probs` raise that original error, but the driver's existing broad observer catch logs it and returns normally. A direct CPU execution confirmed `native_restore_failure_driver_returned=true`, `actor_asleep=true`, and the input reference removed. This issue already applied to wake/sleep failures; the new restore now also reaches that indistinguishable error boundary.

The direct command used the common Python environment (not pytest), loaded `ScoreStore/install_cpu_runtime/load_score_actor/make_actor/make_args/make_parallel`, replaced `actor._switch_model` with the OSError-raising function, and called `asyncio.run(train._score_eval_train_data(SimpleNamespace(offload_rollout=False), SimpleNamespace(score_log_probs=score), None, 19, {"monitor": RolloutDataPack(data_ref=ref)}, rollout_executor=None))`. It intentionally stopped at the restore fault before any rollout load/forward; no DDP or optimizer work ran.

Inspected evidence: `train.py:78–96` catches all actor RPC exceptions as observer errors. `miles/ray/train/group.py:335–376` drains workers then forwards an exception without phase metadata. `miles/utils/workers/rpc/client/call.py:77–78` represents remote errors as RpcWorkerCallError; a controller rethrow becomes another RPC error, so changing an actor exception class alone does not reliably preserve its classification across all supported transports.

No extra exception/API/controller edit was made: the assignment explicitly requires returning architectural decisions and excludes ownership of those RPC/controller files.

Options for the parent:

1. **Recommended:** introduce a narrow scoring-lifecycle fatal classification at the actor boundary and preserve that classification through the existing controller/RPC error representation. Exempt only that classification from the driver observer catch. Cost: a small additional owned slice across actor, controller, existing error serialization, and driver, with fault-injected wake/restore/sleep checks. This preserves observer failures as soft and original fatal causes as evidence.
2. Move observer error handling into the actor and propagate all actor RPC errors fatally. Cost: changes scoring-result failure semantics and distributed partial-output handling; returning None alone cannot distinguish non-producer ranks from failed scoring and is not recommended without an explicit result contract.

Until that decision/repair lands, **the complete failure-semantics requirement is INCOMPLETE** even though the actual weight restoration and engine fatal behavior are verified locally.

## Handoff and verification limits

The internal scorer entrypoints now require keyword `rollout_executor`. The production callback and owned tests supply it. The separately owned `tests/manual/agent_opd/probe_eval_restore.py` owner must update its driver adapter to supply the executor and exercise the complete restoration transaction; this subtask did not edit or run that probe.

Real TMS/SG engine/CUDA IPC bucket transport, pinned Megatron construction, native ordinary-publication queue tests, final same-version Qwen scores, and formal-run release remain parent-owned. The CPU regression does not qualify D8 or any A/B/C run. No additional Qwen optimizer update or budget extension occurred.

## Earlier self-check: 1. 规划完成情况

**汇总：** PASS 2｜BLOCKED 1｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 非备份 actor 恢复／same-version engine 发布 | PASS | 明确 5 red → 7 green；改动限于现有 owners。 |
| cancellation、原始 masks/metadata 和状态保留 | PASS | 最终 67 个 affected-only 用例通过，且进程正常完成。 |
| actor lifecycle 致命错误分类 | BLOCKED | 实际 fault injection 证实被现有 observer catch 软化；需父任务决定并补充 RPC/controller ownership。 |
| pinned/TMS 验证 | TODO | 本委派的 CPU 检查和进程退出已完成；pinned/TMS 由父任务执行。 |

## Earlier self-check: 2. 偏离检测

**结论：** 未偏移，正常推进。检测窗口：本次委派开始至最终 67 PASS；当前前沿：架构边界 handoff 和父任务 pinned/TMS 验证。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | fixture 只覆盖已确认 remap 和委派要求；额外 native 依赖失败后停止。 |
| D2 细节反复重试 | CLEAR | 每次修正对应明确的缺失 binding／socket 长度，未反复调整生产参数。 |
| D3 支线问题修补 | CLEAR | 不修复缺失 Megatron、optional controller 测试或父任务的 manual probe。 |
| D4 可并行任务停滞 | CLEAR | 独立 CPU/Ray 检查并行；无进一步 delegation 授权。 |
| D5 超范围镀金 | CLEAR | 未加 flag、协议、counter、wrapper 或替代发布 API。 |
| D6 分析空转 | CLEAR | source 调查落实为两处恢复修复及 red/green；只报告必要架构边界。 |
| D7 路线违背 | CLEAR | 没有 GPU/Git/cloud/SSH 或父文档修改。 |

**文档检查：** S1–S6 均未发现本委派的明显缺陷。父任务 plan 的 P3 已拥有 restore blocker；额外 actor 错误分类按 R6 返回决定。**归因：** 无。

## Earlier self-check: 3. 纠正建议

**分支：** A：spec 合理，无需改动。**需停止的偏离行为：** 无。

**接下去的路线：** 1. 父任务决定并分派 actor lifecycle 错误分类 → 保持 observer soft／restoration fatal。2. 并行推进父任务已分派的 pinned/TMS 检查和 manual probe adapter；不以 CPU 结果释放正式训练。已停止额外 CPU 测试扩展。

## Earlier self-check: 4. 最值得关注的 3 点

1. 相同整数 version 不证明字节正确；回归以原始参数和非均匀概率的精确恢复为准。
2. engine 恢复失败已原样致命传播，但 actor lifecycle 异常仍需跨 RPC 分类。
3. CPU 结果不替代父任务 pinned/TMS 和正式 Qwen gate。

## Historical read-only follow-up: precise unsafe continuation

This section records the pre-fix eight-case evidence and the in-memory-only cause test. Its baseline scratch script deliberately expects the original unsafe state; after the production repair, use the persistent regression below rather than re-running that old unsafe-state expectation as a green gate. References to the move not yet being applied describe that historical read-only phase.

Task ID remains **QWEN-P3-EVAL-RESTORE-FIX**. The parent explicitly requested read-only investigation/fault checks, preserving all production patches and D8's healthy-training soft gates. This follow-up changed **no production code, existing fast test, manual probe, HF-reload file, or parent-owned document**. Only this owned evidence report and the temporary CPU fault script were written. No GPU, platform, SSH, cloud, Git, delegation, or formal optimizer update occurred. Parent-reported actual-TMS red and HF2H800 PASS were not re-executed by this agent.

### Native owner checks and results

Scratch artifact: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_fault_semantics.py`. The script runs the actual actor sleep/wake/switch/scorer/publication bodies, native `ReloadableProcessGroup` static lifecycle, native `TrainerController` scoring/publication, native `TrainerCell.execute` and state transitions, native `WeightUpdater.update_weights`, and the complete existing `placement_group.update_weights` transaction. Actual CPU Gloo supplies updater collectives and the native score calculation. CUDA allocation, PG construction/destruction, model-specific weight conversion, engine transport, and physical worker termination are CPU substitutes. The latter records termination; it does not kill a process or platform worker. The restored source getter is the actual actor CPU-backup getter with `colocate=True`.

```bash
PYTHONPATH=/data/ycfeng/sota-engine/miles \
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B \
/data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_fault_semantics.py
```

**Eight fault scenarios passed their assertions; exit 0.** All eight preserve the immutable CPU actor backup, FP32 master, and Adam tensors. No optimizer or scheduler step is executed after establishing each fixture baseline. The next-forward check uses ordinary training's same native wake → `_switch_model("actor")` → `_compute_log_prob` sequence; it is not a full Megatron optimizer/DDP training run.

| Injected fault | Driver after native publication | Actor state at driver return | Next native forward | Interpretation |
| --- | --- | --- | --- | --- |
| `_switch_model` once | Returns; SG bytes exactly restored at version 7 | asleep / unmapped / PG destroyed | Correct bytes and nonuniform scores | Intentionally soft observer failure is safe. |
| Forward once | Returns; SG bytes exactly restored at version 7 | asleep / unmapped / PG destroyed | Correct bytes and nonuniform scores | Intentionally soft observer failure is safe. |
| Sleep clear-memory failure before side effects | Returns; SG bytes exactly restored at version 7 | resident / mapped / PG live | Correct bytes and nonuniform scores | Original offload was not achieved, but residency flag agrees with reality and healthy training continues. Not automatically fatal. |
| Sleep PG-destroy failure before that PG's side effects | Returns; SG bytes exactly restored at version 7 | resident / mapped / PG live | Correct bytes and nonuniform scores | Same safe-continuation distinction. |
| Wake PG reload fails once after successful TMS resume | **Returns; SG bytes exactly restored at version 7** | **asleep / mapped / PG destroyed** | **Cannot perform the next wake: remapper detects already-active storage** | Genuine unsafe continuation: false residency state survives an otherwise successful native transaction. |
| Wake PG reload fails persistently | Raises native `NonRetryableError`; transaction aborted | Cell marked errored, termination recorded | Not attempted | Existing native publication already blocks continuation. |
| Sleep destroys one needed PG then another destruction fails | Raises native `NonRetryableError`; transaction aborted when publication needs the destroyed PG | Cell marked errored, termination recorded | Not attempted | Existing publication/controller handling already blocks this case. Model-specific PG requirement is supplied by the CPU conversion boundary. |
| Worker becomes unavailable | Raises native `NonRetryableError`; transaction aborted | Cell marked errored, termination recorded | Not attempted | Existing unavailable-worker handling is reusable; no new fatal error taxonomy is needed. |

Initial scratch-boundary errors were resolved before the eight-case result: invalid Pydantic worker/IndepDPInfo fixtures, unmatched engine/engine-ID lengths, unsharded rollout references, and an absent CPU TP process group. These were not production behavior failures; the final fixture uses actual validated cell state, existing DP split fixtures, and a real CPU Gloo TP group. No persistent test machinery was added.

### Exact unsafe path and native TMS consequence

1. `actor.py:554` successfully resumes the non-backed TMS allocations, changing physical residency.
2. `actor.py:557` calls `reload_process_groups()`. Native `reloadable_process_group.py:156` can raise while constructing a PG. `_asleep=False` is assigned only afterward at `actor.py:558`.
3. `score_log_probs`'s `finally` at `actor.py:691–692` therefore sees `_asleep=True` and skips sleep/rollback, despite mapped storage.
4. Native actor publication at `actor.py:1162–1164` treats the actor as offloaded. If the PG fault was transient, its reload now succeeds. It reads the correct immutable CPU actor backup (`actor.py:1131–1136`), publishes version 7, and destroys temporary PGs at `actor.py:1221–1222`. The complete controller transaction finishes normally, including end-update and consumed-version bookkeeping. It neither pauses actor storage nor corrects `_asleep` for the current non-rematerializing configuration.
5. The driver proceeds through KV/graph restoration and `prepare_eval` with `_asleep=True` but mapped actor storage. The next ordinary wake tries to resume already-active allocations before it can restore actor bytes.

The CPU mapper asserts that resume requires paused storage. This is **not merely a fixture-only strictness assumption**: read-only disassembly of the installed pinned `torch_memory_saver_hook_mode_torch_cu13.abi3.so` confirms the native invalid-active-resume path. Its message lives at `.rodata` address `0x81b0`; resume prints it from `0x4ad9`, then branches from `0x4dde`/`0x4df2` to `0x4acf`, sets exit status **1**, and calls `exit` at `0x4ad4`. The native condition therefore terminates the worker; it is not an idempotent resume or a catchable Python observer exception. No binary or CUDA runtime was executed or modified.

Exact binary inspection commands:

```bash
nm -D /data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/torch_memory_saver_hook_mode_torch_cu13.abi3.so
objdump -d -C --start-address=0x4ad9 --stop-address=0x4e80 /data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/torch_memory_saver_hook_mode_torch_cu13.abi3.so
```

This is a CPU fault-injection proof plus inspected installed-binary control flow, **not an observed real-GPU PG failure**. The native full transaction's physical CUDA IPC transport remains parent-owned. A TMS native pause/resume allocation error that already terminates the worker must be treated through existing unavailable-worker handling, rather than simulated as a soft Python OSError.

### Smallest seam and in-memory-only cause check

The smallest correction is in the existing `wake_up` owner: move the **existing `_asleep=False` assignment** to immediately after all relevant TMS resumes succeed and before `clear_memory()`/PG reload. This makes the existing scorer rollback condition reflect actual memory residency. A later PG failure then reaches existing native sleep, which can restore the original offload state. Gain: prevent false offloaded state after a successfully mapped allocation. No current mechanism corrects this flag before publication.

Cost: approximately a **two-line move in actor.py**, plus a regression in the existing remap fixture. No new flag, exception class, result contract, retry, API, worker wrapper, or RPC change is required. Persistent rollback/publication failures retain their existing native fatal behavior. This is a narrow cause repair, not a newly demonstrated general R6 architecture gap. **It has not been applied to production.**

The script's `wake_reload_once_in_memory` case compiles an AST copy of just native `wake_up`, relocates that existing assignment on a test object, and leaves every repository source untouched. Exact additional command:

```bash
PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/tmp/opencode-v2-tmp/opencode \
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -c '
import asyncio, os, tempfile
import torch.distributed as dist
import eval_restore_fault_semantics as checks
fd, path = tempfile.mkstemp(prefix="eval-restore-seam-", dir="/data/ycfeng/tmp/opencode-v2-tmp/opencode")
os.close(fd)
dist.init_process_group("gloo", init_method="file://" + path, rank=0, world_size=1)
try:
    asyncio.run(checks.check("wake_reload_once_in_memory"))
finally:
    dist.destroy_process_group()
'
```

**One additional case passed; exit 0.** The same injected PG fault remains an observer error. Native rollback now leaves **asleep / unmapped / PG destroyed**, full same-version publication succeeds, next native forward restores exact parameter bytes and nonuniform scores, and CPU backup/master/Adam remain unchanged. The new check tests the proposed cause correction, not a fallback or exception suppression.

### Structured RPC cause and existing reusable handling

Two direct native `RpcCallExecutor._run` → `RpcCall.run` → controller executor/client fault checks passed without HTTP/network traffic or error-string parsing. Roots were `builtins.OSError` and `miles.utils.workers.worker_handle.WorkerUnreachableError`. The first wire outcome correctly carries each root's qualified class in `CallStatusResponse.error_type` (`protocol.py:32–40` / `executor.py:79–85`). The client wraps it as RpcWorkerCallError with that field (`client/call.py:77–78`). A second controller RPC outcome carries the qualified **RpcWorkerCallError** class, not the nested root field. Qualified-type matching is already used for a direct call in `cell_operations/kubernetes.py:89–91`; it is not an existing cross-hop residency/successful-rollback signal.

A local RayTaskError construction check passed: `.as_instanceof_cause()` retains the direct cause class and `.cause`. `RayWorkerHandle:32–33` already translates RayActorError to WorkerUnreachableError. Native scoring drains RPCs without cell execution/recovery (`group.py:350–373`); subsequent publication uses `TrainerCell.execute`, whose existing exception path marks and kills failed cells (`cell.py:279–292`). `group.py:672–680,639–647` then fails when no healthy cell remains. If publication cannot reach any inference target, `group.py:480–481` already raises NonRetryableError. Driver native publication errors escape from `finally`, aborting the transaction through `placement_group.py:334–336`.

These mechanisms already protect the persistent PG/unavailable-worker cases above. The successful-publication case has **no exception to classify** at that stage; fixing the native residency flag is the right seam. **The earlier recommendation to classify every lifecycle-named observer failure as fatal is withdrawn.**

## Approved native residency repair and persistent validation

The parent subsequently authorized the measured owner fix and persistent regression. This follow-up changed only:

- `miles/backends/megatron_utils/actor.py:555`: move the existing `_asleep=False` assignment after the completed native TMS resume branch and before `clear_memory()` / PG reload. There is no new catch, flag, retry, exception type, RPC or publication change.
- `tests/fast/backends/megatron_utils/score_rpc_fixtures.py`: expose the existing native actor CPU-backup getter to the boundary and add `eval_publication`, which reuses the previously verified native controller/cell/updater/full-transaction fault setup. PG construction, model conversion/engine transport and worker termination remain explicit CPU substitutes. Native TMS itself is not replaced in production.
- `tests/fast/backends/megatron_utils/test_score_log_probs.py:215`: persistent `once` / `persistent` / `unavailable` parameterized regression. No existing manual probe, HF-reload artifact, `train.py`, Ray cancellation test or parent-owned document was edited in this follow-up.
- This owned report: mark the earlier architecture blocker superseded and retain exact red/green and verification limits.

The once-failing PG regression traverses native scorer → controller → cell → actor receiver publication → native WeightUpdater → complete existing placement-group start/update/end/consumed-version transaction. It requires restored exact engine bytes at **the same version 7**, weights-before-KV/graph ordering, actor **asleep / unmapped / PG destroyed** at driver return, original consumed input refs cleanup, observer-unverified logging rather than an abort, and unchanged CPU actor backup/master/Adam, weight version, last rollout counter and scheduler counter. It then executes the next native wake → actor restore → forward with real CPU Gloo, requires exact original actor bytes and expected nonuniform scores, and checks two successful remaps with an intervening native pause. The remapper rejects any already-active resume, so this is not a boolean-only wake check.

The persistent-PG and unavailable-worker controls require existing native `NonRetryableError`, cell transition to errored, termination recording, transaction abort, **no** successful end-update, consumed-version bookkeeping or `prepare_eval`, and intact immutable CPU backup/master/Adam. These already passed before the assignment move and continue to pass afterward. Worker termination is recorded in the CPU boundary; no physical worker is stopped.

Exact persistent red/green command, unchanged across the one-assignment production fix:

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m pytest -q \
tests/fast/backends/megatron_utils/test_score_log_probs.py::test_eval_pg_reload_failure_restores_residency_or_native_publication_fails
```

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Pre-fix persistent regression | Only `once` exposes original unsafe state; existing fatal controls pass | **1 FAIL / 2 PASS**, **2.25 s**, exit 1. The driver had completed native publication, but `actor._asleep=True` and `saver.snapshots=None` (mapped allocation) failed the residency assertion. | Meaningful RED reproduced |
| Same regression after the existing assignment move | All three contracts pass; no double resume | **3 PASS**, **2.07 s**, exit 0. Correct bytes/nonuniform forward, same-version full publication, exact state and unchanged backup/master/Adam verified. | GREEN / PASS |
| Affected actor/scorer/driver checks only | Existing 60 core checks plus the three new cases pass | **63 PASS**, **17.82 s**, exit 0. Includes Gloo TP/CP/DP payload mapping, read-only mode/RNG/mask/metadata checks, queue preservation, native full publication, KV-only/no-offload and driver failure cleanup. | PASS |

Exact affected core command:

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m pytest -q \
tests/fast/test_train.py tests/fast/backends/megatron_utils/test_score_log_probs.py
```

Environment is the same CPU boundary as above: Python **3.12.13**, pytest **9.1.1**, asyncio AUTO; Torch **2.11.0+cu130** without GPU execution. Existing Swig and torch.jit deprecation warnings remain; they are not failures. The parent reported its pinned 60 core checks PASS and separate corrected Ray invocation/native ordinary-publication checks; these parent-owned results were not duplicated or inferred complete here.

### Native partial-resume limit

The assignment is deliberately **after all resume calls return successfully**, including LoRA's default and grad-buffer resumes. It does not claim to recover a failure *inside* a native TMS resume or a failure between partially completed native allocations. The inspected installed TMS uses native error/`exit(1)` paths for invalid state/CUDA allocation failures, which cannot be converted into a Python observer failure by this move. A worker terminated during partial resume remains subject to existing unavailable-worker/controller/publication handling. No real GPU partial-resume or PG-construction fault was induced; these checks prove late Python PG failure rollback after a completed resume, not arbitrary CUDA/NCCL fault recovery. No new error suppression or blanket fatal classification was introduced.

## 1. 规划完成情况

**汇总：** PASS 4｜BLOCKED/FAILED/SKIPPED 0｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 原生 residency 赋值时序窄修复 | PASS | 现有赋值移至全部 resume 完成后、clear/PG reload 前，无新异常／API。 |
| 持久一次 PG 失败恢复及原生 fatal 回归 | PASS | 1 FAIL/2 PASS → 3 PASS；完整同版本发布、下一次非均匀 forward、backup/master/Adam 和 ref cleanup 均验证。 |
| 受影响 CPU core 检查 | PASS | 仅两个相关文件，63 PASS / 17.82 s；未重复父任务 Ray/GPU 工作。 |
| owned evidence 和架构 BLOCKED 更新 | PASS | 历史提议明确 superseded，记录原生 partial-resume failure 限制。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。**检测窗口：** 父任务批准窄修复至 63 项相关检查通过。**当前前沿：** 已完成此修复 slice；父任务继续 pinned/GPU 资格验证。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 复用八场景证据，仅持久化要求的完整恢复／fatal 三场景；相关检查通过后停止。 |
| D2 细节反复重试 | CLEAR | 新持久回归首次即复现预期 red，单次赋值移动即 green。 |
| D3 支线问题修补 | CLEAR | 未改第三方库、RPC serialization、manual probe 或 HF 路径。 |
| D4 可并行任务停滞 | CLEAR | 未重复占用父任务 Ray/GPU frontier；本 slice 的 red→move→green 是真实串行依赖。 |
| D5 超范围镀金 | CLEAR | production 只移动既有赋值，无新增 flag、协议或 fatal 分类。 |
| D6 分析空转 | CLEAR | native owner 窄修复和持久红绿验证均已完成。 |
| D7 路线违背 | CLEAR | 严守批准文件范围，无 GPU/Git/cloud/SSH/delegation；原生错误传播保持。 |

**文档检查：** S1–S6 未发现当前 plan/spec 的明显缺陷；本报告已将早期架构 BLOCKED／blanket-fatal 提议标为 superseded，并更新为已验证的窄修复。**归因：** 无。

## 3. 纠正建议

**分支：** A：spec 合理，无需新增 R6 架构决定。**需停止的偏离行为：** 无。

**接下去的路线：** 1. 父任务验证这三项新增回归在 pinned 环境的结果及其已安排的 Ray/native ordinary-publication 检查。2. 保持 D8：成功恢复健康状态的 observer 故障继续软处理；真实发布／worker 不可用走现有原生处理。3. 继续父任务 GPU 和正式 Qwen gate；本 slice 不把 CPU fault check 当作真实 GPU PG 故障验证。

## 4. 最值得关注的 3 点

1. 名为 switch/sleep 的异常不等于不可恢复；健康 policy/backup/master 和可恢复 native runtime 状态才是判据。
2. `_asleep=True / mapped=True` 的原 red 已由现有 owner 时序修复消除；持久 full-transaction 回归证明恢复成功。
3. 三个新故障回归和 63 项相关 core 检查已通过；真实 GPU partial-resume 和 pinned 发布资格仍属父任务。
