## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Parent verifies the exact pinned device-module caller and replaces the obsolete CPU no-op stub with the real torch CPU module; retain explicit-device behavior and pending runtime verdict. |
| 2026-11-07 | Supply factual startup address/size metadata on the tiny runner's existing owner and add a negative control executing the pinned native published-storage assertion. |
| 2026-11-07 | Replace unconditional cleanup resume with native actor/SG lifecycle owners; reproduce active-resume failure with a strict CPU regression and inspect pinned torch-hook disable/free semantics. |
| 2026-11-07 | Adapt the probe to the repaired native placement-group transaction and native tensor sender/receiver; verify two CPU orchestration cycles with zero optimizer updates and retain CUDA execution as parent-owned. |
| 2026-11-07 | Record complete real-TMS causal red and prepare worker-owned torch-hook pool disposal with CPU lifetime checks; leave native transaction adapter to the next authorized slice. |
| 2026-11-07 | Fix probe-only CPU/CUDA report ownership after the parent H800 run; preserve completed evidence on errors and verify reporting with CPU fault injection. |
| 2026-11-07 | Incorporate parent raw tensor evidence for C and A; replace the manual actor restore control with the native ordinary-training restore/forward callsite. |
| 2026-11-07 | Record the local native-callsite restore counterexample and an unexecuted synthetic CUDA command. |

# QWEN-P3-EVAL-RESTORE

## Scope and interpretation

Delegated scope: local investigation and manual-probe implementation only; no production edit, GPU/platform/SSH/cloud/Git operation or delegation. QWEN-P3-EVAL-RESTORE-FIX owns production `train.py`, `actor.py` and existing fast fixtures. The parent owns GPU execution, review, formal experiment artifacts and RCA.

Added [probe_eval_restore.py](../../tests/manual/agent_opd/probe_eval_restore.py). Two processes model the actor and inference engine separately. The actual `train.py` scoring transaction drives the actual actor scorer/sleep/wake and SGLang scheduler release/resume methods, extracted from source without editing production behavior. The existing 8-token model/pipeline fixture replaces model architecture and Megatron execution. Actor parameters have a non-backed `param_buffer` allocation; synthetic Adam masters/moments have backed `default` allocations. This policy represents the native offload arguments, not actual Megatron DDP/optimizer construction.

CPU mode deliberately zero-fills newly remapped allocations without backups. It proves that the callsites require a restore under their declared allocation semantics. It does **not** prove that the formal GPU run remapped to zeros or establish its cause. CUDA mode uses actual TMS regions with the supported `torch` hook, on one GPU shared by the two processes. CUDA mode is prepared but **not executed** by this subtask.

## Parent raw evidence incorporated

Read the parent-produced [raw tensor report](evidence/raw-score-evidence-exp-1107-092209-060993.json) locally with JSON parsing only. Its stated scope is direct `torch.load` of native saved tensors, independently of inspector arithmetic. This subtask did not read the cloud tensors or repeat the parent platform inspection.

| Actual boundary | Count | Native recorded values |
| --- | --- | --- |
| C eval_0 SG decode / prefill | 7,169 each | Nonuniform; means **-0.3438427470 / -0.3441828373** |
| C eval_0 trainer, both DP dumps combined | 4,004 + 3,165 = 7,169 | All **-12.422473907470703**, unique count 1 |
| C rollout0 SG decode / prefill after eval | 65,536 each | All **-12.422473907470703**, unique count 1 |
| C rollout0 completions | 8 | All length **8,192**; distinct token counts **8,045–8,078** |
| C ordinary training log_probs | 32,768 + 32,768 = 65,536 | Nonuniform; min **-26.0380687714**, max **-6.5390582085**, means **-13.3481975103 / -13.3530305733** |
| A new formal eval trainer, four DP dumps combined | 1,195 + 868 + 1,491 + 777 = 4,331 | All **-12.422473907470703**, unique count 1 |
| A eval_0 SG decode / prefill | 4,331 each | Nonuniform; means **-0.6615089475 / -0.6620616540** |
| B | No scoring evidence yet | No conclusion |

The parent identifies A as TP2 and C as TP4. The repeated scorer symptom therefore disfavors a TP4-only explanation. Actual SG decode **and** prefill changed after eval; an inspector-only scoring error cannot explain the native saved generation sequence. Ordinary trainer probabilities becoming nonuniform again is consistent with its existing restore callsite, while the scorer omits that callsite. These are constraints on diagnosis, not proof that real GPU parameters were zeroed.

Later evidence supersedes the table's historical B status: [historical-torch-scores-and-C-flags.json](evidence/historical-torch-scores-and-C-flags.json) records **4,712 B** and **4,279 A** native trainer values from the earlier formal runs, all exactly **-12.422473907470703**, unique count 1, backend **torch**. Local JSON count/value checks passed. A fused-only explanation does not account for this cause; no further kernel-only GPU run is requested by this subtask.

The same parent artifact confirms actual C flags: `disable_grad_buffers_cpu_backup=True`, `disable_param_buffers_cpu_backup=True`, `offload_train=True`, `offload_rollout=True`, `offload_train_target=cpu`, `optimizer_cpu_offload=True`, `rematerialize_param_from_master_weight=False`, `use_distributed_optimizer=True`. Both native engine snapshots have `enable_memory_saver=True` and `enable_weights_cpu_backup=False`. These are parent-read flags, not synthetic assumptions. The synthetic optimizer still differs from the actual CPU-offloaded distributed optimizer; this reporting-only fix does not change that model.

[Parent evidence] C completed one optimizer step before actor.sleep failure; the student container was explicitly OOMKilled. Host-memory RCA remains parent-owned and separate from the earlier probability corruption. This subtask does not infer that the sleep failure and uniform scores share a cause.

## Parent pinned CPU API follow-up

Pinned retry `exp-1107-133708-233964` passes the startup-address gate, then fails at native `WeightUpdater.update_weights_from_tensor`:387: `torch.get_device_module(self.device)` calls the fixture's old zero-argument lambda. The raw [log](evidence/eval-restore-exp-1107-133708-233964.log):39–45 retains the exact `TypeError`; no CUDA work or optimizer step ran.

Hypothesis before the next run: the receiver's CPU-only no-op device stub, rather than native transfer, blocks the pinned caller. Replace it with the real `torch.get_device_module`, supplying `cpu` only as the default for the older local zero-argument call. Explicit device arguments are forwarded unchanged; CPU mode receives actual `torch.cpu.current_device` and `synchronize`, and CUDA mode is untouched. Direct local checks confirm default/explicit CPU return `torch.cpu`, explicit CUDA returns `torch.cuda`, and actual CPU synchronization succeeds.

The exact downloaded pinned updater was read through its complete tensor load and begin/end paths, including receiver synchronization at423 and both immutable startup-address checks. The next exact pinned two-cycle run must preserve all byte/score/version/master/Adam/counter/exit assertions. It is a CPU API prerequisite only; actual CUDA IPC and allocator lifetime still require GPU evidence.

**Actual pinned result: PASS**, job `exp-1107-134716-167829`, Python3.12.16, torch2.14.1+cu130,43.599s. Both cycles preserve exact parameter bytes, nonuniform scores with all comparison errors0, synthetic master/Adam bytes, version7 and optimizer update count0. Workers51/52 both exit0. The report explicitly has `cuda_ipc_qualified=false`; [raw report](evidence/eval-restore-exp-1107-134716-167829.json). Exact worker invocation from repo cwd:

```bash
export PYTHONPATH=/data/ycfeng/sota-engine/miles PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 MEGATRON_PATH=/root/Megatron-LM
export LD_LIBRARY_PATH=/usr/local/cuda-13.0/compat"${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CUDA_VISIBLE_DEVICES=""
export TMPDIR="/var/tmp/qwen-api-$KUBEBRAIN_RJOB_NAME"
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.probe_eval_restore --mode cpu \
  --report "/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/evidence/eval-restore-$KUBEBRAIN_RJOB_NAME.json"
```

Actual CUDA job `exp-1107-135028-993396` is submitted with1H800 and remains Pending on the exact admission read. [Platform receipt](evidence/restore-pinned-api-platform.json) verifies the personal creator, pinned image and current local NFS source. The prior failed CPU jobs are retained separately. An initial inspection filtered annotation names for the word `mount` and therefore missed the native NFS field; source inspection of `steptron/utils/stepmind.py:907–917` corrected the reader to the exact `kubebrain.brainpp.cn/filestore-volume` field. This inspection error did not change any workload or allocation.

## Historical pre-fix source evidence

- `miles/utils/arguments.py:1534–1538`: native train offload disables DDP gradient and parameter CPU backups, independently of the master-weight rematerialization option.
- `miles/backends/megatron_utils/actor.py:494–559`: non-rematerialized sleep pauses all TMS allocations; wake only resumes allocations and process groups.
- `actor.py:613–619`: `_switch_model("actor")` owns the full weight restore. `miles/utils/tensor_backper.py:98–111` copies normal backups into live tensors. Under master-weight rematerialization, `tensor_backper.py:164–179` additionally casts masters, starts forced parameter synchronization and restores extras; `rematerialize_utils.py:46–68` selects the native optimizer copy implementation.
- `actor.py:648–693`: scoring wakes/sleeps but does not call `_switch_model`. `actor.py:893–929` restores the selected actor before ordinary actor logprob computation. Native training and scoring therefore have different restore call chains.
- `tests/fast/backends/megatron_utils/score_rpc_fixtures.py:246–255`: the existing boundary fixture replaces native wake/sleep with boolean changes, leaving parameters resident throughout.
- `train.py:71–76,103–105`: eval scoring offloads inference, invokes actor scoring, then only onloads inference and prepares eval.
- `miles/backends/sglang_utils/sglang_engine.py:106,192–202`: memory saver is enabled by rollout offload; base-weight CPU backup is explicitly enabled for the supported LoRA case, not the ordinary dense case.
- Installed SGLang `srt/arg_groups/fields/exec_.py:62–65`: `enable_weights_cpu_backup=False`. `srt/model_executor/model_runner_components/load_model_utils.py:307–325` applies that option to the weights allocation region.
- Installed SGLang `srt/managers/scheduler_components/weight_updater.py:368–403,478–490`: release/resume pauses/resumes weights and preserves **named buffers**, not parameters. This is not a same-version weight publication.
- `miles/ray/placement_group.py:317–359`: the existing `update_weights` transaction owns start-update, native actor publication, end-update and consumed-version bookkeeping. A possible same-version restoration should use the existing owner rather than inventing a replacement publish API. This subtask does not modify or test that publication path.
- `miles/backends/training_utils/weight_update/protocol.py:54–61,86–89`: colocation selects `UpdateWeightFromTensor`; its inherited `begin_sync` returns true. `protocols/cuda_ipc.py` has no `begin_sync` override. `updater.py:140–195` therefore streams weights in the existing session even when asked to publish the same version. Its ordinary lifecycle already includes begin/end, cache handling and version bookkeeping; a bare tensor copy would not exercise this contract.

Installed SGLang source prefix: `/data/ycfeng/envs/miles-agent-opd-cpu/lib/python3.12/site-packages/sglang/`. The parent has now verified the actual resolved offload flags above; formal fork source and physical allocation behavior remain separate evidence.

## Executed commands and observations

Repository cwd: `/data/ycfeng/sota-engine/miles`. Python `3.12.13`; torch `2.11.0+cu130`; SGLang `0.5.23`; pytest `9.1.1`. No conda environment. This subtask performed no CUDA execution.

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m \
  tests.manual.agent_opd.probe_eval_restore --mode cpu \
  --report /data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_cpu_repeat.json
```

Three completed runs produced the same red signal; the timed repeat took **11.10 seconds** and the final run **10.49 seconds**, exit **1**. The final run used the same command with `--report /data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_cpu_final.json` and additionally gated master/optimizer/control equality. AST, newline and trailing-whitespace checks passed for all three new files:

| Boundary / expected behavior | Actual | Status |
| --- | --- | --- |
| Scorer sees original live parameters | Max parameter error **1.015625** | FAIL under injected remap |
| Scorer preserves nonuniform scores | All ten values **-2.079441547393799**, exactly `-ln(8)` | FAIL under injected remap |
| Native scorer restores original sleeping state | `true` | PASS |
| Weight-version metadata alone catches bad bytes | Version remains **7** while parameter comparison fails | Does not catch it |
| Inference native resume restores weights | Parameter equality `false`; score max error **1.0814299583435059** | FAIL under injected remap |
| Native inference static-state restore remains intact | Static buffer remains **17** | PASS |
| Separate actor control: wake + native `_switch_model("actor")` | Exact parameter equality; score max error **0.0** | PASS |
| Control preserves synthetic Adam/master state | Master and optimizer-state equality `true` | PASS |

The old boundary test still passes, demonstrating its coverage limitation rather than validating the new lifecycle:

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m pytest -p no:cacheprovider \
  tests/fast/backends/megatron_utils/test_score_log_probs.py \
  -k native_scoring_is_read_only_and_retains_original_response_population -q
```

**8 passed, 14 deselected, 16 warnings in 2.18 seconds**, exit 0. AST parsing of the new manual repro passed.

The first harness attempt supplied an unsplit object ref with pre-split arguments and failed with `TypeError: object of type '_MooncakeStoreObjectRef' has no len()`. Corrected the manual fixture to the supported delayed-split mode; this was a harness error, not the formal failure. Its cleanup also exposed a broken-pipe handling issue, corrected only in the manual script.

### Native ordinary-training callsite control

After the new parent evidence, the manual control now calls **`MegatronTrainRayActor._train_actor`**, not `_switch_model` directly. Native `actor.py:918–935` restores the actor and computes its ordinary training log_probs; the probe deliberately stops immediately after that forward, before advantage computation, backward or optimizer work. The unchanged native scorer also measures a healthy resident baseline before sleep using identical inputs and full-vocabulary probabilities.

Executed the CPU command above with `--report /data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_train_callsite_cpu.json`: **10.76 seconds, exit 1**. The scorer baseline has nonuniform values **[-3.4683361053, -1.2840144634]**; post-sleep scorer values are all `-ln(8)`, max baseline score error **1.3888945580**. SG baseline is nonuniform and post-resume values are all `-ln(8)`. The actual ordinary-training callsite control restores exact parameter bytes and native scores with **0.0** max score error; Adam/master equality is true. Its reported `stopped_before_optimizer_step=true` distinguishes the intentional control stop from a training failure. Native logging may record this deliberate sentinel stop as `_train_actor ok=false`; it is not a workload failure.

Final repeat: `--report /data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_train_callsite_cpu_final.json`, **10.72 seconds, exit 1**, same values and verdict. AST verification confirms the control calls `_train_actor` and does **not** call `_switch_model` directly. Local JSON checks confirm C/A trainer counts **7,169 / 4,331** and exact uniform values. Syntax/whitespace checks passed.

This local signature now matches the formal sequence at the relevant boundaries: healthy SG baseline, bad eval scorer, bad post-eval SG probabilities, healthy ordinary trainer forward. It still uses injected CPU remaps and tiny tensors, so it does not independently establish real TMS behavior or execute the native SG sampler.

## Parent CUDA command and reached reporting failure

Parent run **exp-1107-094209-081782**, one H800, reached the native ordinary-training forward/control sentinel. The local [log](evidence/eval-restore-exp-1107-094209-081782.log):41–44 then records:

```text
probe_eval_restore.py:242: (actual_scores - expected_scores).abs().max().item()
RuntimeError: Expected all tensors to be on the same device, but found at least two devices, cuda:0 and cpu!
```

No report was produced, so the log alone does not supply a CUDA equality verdict. The sentinel at log:2–11 is the intentional pre-optimizer control stop, not this failure. This subtask read the log locally and performed no GPU/platform inspection.

The later [exp-1107-100112-455338 JSON](evidence/eval-restore-exp-1107-100112-455338.json) supersedes that missing-report limitation. All behavioral stages completed: actor live-byte equality **false**, parameter error **1.015625**, uniform-score error **0.0**; native SG resume byte equality **false**, score error **1.081430196762085**, uniform-score error **0.0**; native ordinary `_train_actor` control restores exact bytes, score error **0.0**, and preserves master/Adam state. The overall verdict is **ERROR only because both workers exit 1 during cleanup**. The [log](evidence/eval-restore-exp-1107-100112-455338.log):12–13 reports `tms_torch_free`, `csrc/entrypoint.cpp:107`, `only support interesting region`. This is measured real-TMS causal red, not merely the injected CPU counterexample. It does not qualify a production green run.

[Parent-provided source identity] The measured red used `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-restore-pre-fix-kuns6vae` at `442afdb8` plus the reporting-fixed probe. This subtask does not run Git or alter that frozen source. No further pre-fix behavioral run is needed.

**Do not launch the current working-tree main loop as a green verification yet.** The inspected repair and new driver require the native same-version transaction adapter described below. The command is retained as the CLI shape, not a claim that the old adapter supports the new driver.

Run only in an independently approved small synthetic allocation using the pinned Miles image and its existing CUDA compatibility environment; do not add a Qwen optimizer probe or extend the formal workload budget. Set `TMPDIR` to existing worker-local temporary storage and `RESTORE_REPORT` to an approved task-local or personal artifact path. No model source, teacher, HTTP server or download is needed.

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.probe_eval_restore \
  --mode cuda --gpu-id 0 --report "$RESTORE_REPORT"
```

Loop: backed Adam/master state + non-backed actor parameters -> healthy resident native scorer baseline -> native actor sleep -> native eval transaction releases inference -> native actor scorer wakes, forwards and returns to sleep -> native inference resume -> compare both boundaries against initial parameter bytes and nonuniform scores -> native ordinary `_train_actor` restore/logprob-forward control -> stop before optimizer work. A completed report with `FAIL`, exit 1, means an equality check failed. Exceptions instead write `ERROR` with completed evidence and propagate to a nonzero exit. `PASS` is written only after checks and worker cleanup finish successfully. This is not a training stop command or formal soft-gate verdict.

Predicted red signal: actor parameter inequality at the scorer's first forward and/or inference parameter inequality after resume. Zero-filled remaps additionally produce uniform `-ln(vocab)` scores. The native actor control should recover exact weights and scores while preserving optimizer/master state.

## Outstanding evidence

1. Actual C offload and backup flags are verified in the parent artifact above. Native physical allocation ownership still requires evidence distinct from flag values.
2. The parent real-TMS retry completed all behavioral measurements and confirmed both restore omissions; only torch-hook pool disposal remains an execution error. The cleanup preparation below is CPU-checked, not GPU-qualified. Do not repeat the pre-fix red loop. A future green must exercise the full native same-version publication transaction. The synthetic CUDA mode uses the supported torch hook rather than formal preload; it does not construct Megatron DDP/optimizer, execute Ray transport/process-group teardown, reproduce TP4/DP2, or capture CUDA graphs.
3. Historical torch uniform scores exclude a fused-only explanation for this cause. The terminal actor.sleep OOMKilled remains a separate parent-owned RCA; this subtask does not request additional kernel-only runs or establish unrelated fused correctness.
4. A real native same-version republish control is not executed. Inference-only red would support checking that contract; actor-only red would isolate the scorer restore boundary. Both green would leave native optimizer/DDP construction, layout, asynchronous behavior or fused computation as unresolved alternatives.
5. Why the earlier optimizer-disabled baseline passed is not settled by this synthetic allocation model. Actual optimizer/DDP parameter-storage ownership remains distinct from the now-confirmed flags; do not infer that `--debug-disable-optimizer` alone changes the buffer policy.

## Ranked restore hypotheses and next evidence

1. **Scorer omits full restore after unbacked parameter remap.** The frozen pre-fix real-TMS loop now measures the predicted bad bytes/uniform scores and exact recovery through ordinary `_train_actor`. Together with the actual formal flags/raw tensors, this supports the native omission diagnosis. A production-fixed GPU green is still separate evidence.
2. **Inference resume after scoring omits required same-version publication.** Prediction: healthy pre-eval engine weights become incorrect after release/resume, and the existing full publication transaction at unchanged version restores them. Parent native decode/prefill establishes the temporal corruption; the last publication-control prediction is not executed by this subtask.
3. **Further fixed-path qualification.** The actual allocation-loss red is measured. A future fixed native transaction must restore byte/score equality and exit cleanly; neither a mock transport nor bare tensor copy qualifies that result. Do not replace this step with generic kernel-only investigation.

No production changes or fix recommendation are accepted as verified by this report.

## Probe-only reporting correction and CPU validation

Scope remains **probe + this report only**. No production edit, GPU/platform/SSH/cloud/Git action, optimizer construction change, or new probe mode was performed.

- `_score_receipt` at `probe_eval_restore.py:62–64` takes an independent detached CPU copy. Initial native scores, eval scores and ordinary-training control scores all use it; parameter/master/moment comparisons already use CPU snapshots. The native model and probability computations are unchanged.
- The driver retains received actor and SG results in the report immediately rather than building an all-or-nothing return dictionary. The worker attaches prior JSON-safe receipts and the control's native scores/parameter comparison to a propagated error. Completed control comparisons are recorded before the later sleep.
- A comparison/worker/cleanup exception writes `verdict=ERROR` with its traceback and available completed evidence, then raises. Failures are not converted to successful results. Worker cleanup finishes before a `PASS` can be written.

### Native CPU loop

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m \
tests.manual.agent_opd.probe_eval_restore --mode cpu \
--report /data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_reporting_cpu.json
```

Observed **13.83 seconds, exit 1, report present, `verdict=FAIL`**. The injected native lifecycle signal is unchanged: scorer and SG uniform errors **0.0**; actor parameter error **1.015625**; native control parameter equality true, score error **0.0**, optimizer/master equality true. This is the expected red counterexample, not a reporting error. Environment remains Python **3.12.13**, torch **2.11.0+cu130**, CPU execution only.

### Targeted reporting checks

The following exact inline command passed **6 tests in 0.017 seconds**, exit 0. Its native-device spy verifies the CPU-copy contract without invoking CUDA; it does not replace the parent GPU rerun. RuntimeError, EOFError and worker-error injections all preserve actor/SG results, write `ERROR`, and raise. A cleanup failure cannot produce `PASS`.

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B - <<'PY'
import asyncio, contextlib, copy, io, json, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import torch
from tests.manual.agent_opd import probe_eval_restore as p

class Connection:
    def __init__(self, responses=()): self.responses, self.sent = iter(responses), []
    def recv(self): return next(self.responses)
    def send(self, value): self.sent.append(copy.deepcopy(value))
    def close(self): pass

class Worker:
    def __init__(self, exitcode=0): self.exitcode = exitcode
    def start(self): pass
    def is_alive(self): return False
    def join(self, timeout): pass

class Context:
    def __init__(self, exitcode=0): self.exitcode = exitcode
    def Pipe(self): return Connection([{'ready': True}]), Connection()
    def Process(self, **kwargs): return Worker(self.exitcode)

class ReportingChecks(unittest.TestCase):
    def test_receipt_is_detached_owned_cpu(self):
        value = torch.tensor([1., 2.], requires_grad=True)
        receipt = p._score_receipt(torch, [value])
        self.assertEqual(receipt.device.type, 'cpu')
        self.assertFalse(receipt.requires_grad)
        with torch.no_grad(): value.fill_(9.)
        self.assertEqual(receipt.tolist(), [1., 2.])

    def test_native_device_boundary_requests_cpu_copy(self):
        class NativeOutput:
            def detach(self): return self
            def to(self, *, device, copy):
                self_test.assertEqual((device, copy), ('cpu', True))
                return torch.tensor([3., 4.])
        self_test = self
        receipt = p._score_receipt(SimpleNamespace(cat=lambda values: NativeOutput()), [object()])
        self.assertEqual(receipt.tolist(), [3., 4.])

    def test_driver_keeps_stages_on_late_worker_error(self):
        result = {'actor_score': []}
        stage = {'actual_native_scores': [-1., -2.], 'stopped_before_optimizer_step': True}
        def rpc(connection, method, *args):
            if method == 'score': return {'native_scores': [-2.0794415]}
            if method == 'observation': return {'scores': [-2.0794415]}
            if method == 'control': raise p._WorkerError(method, 'injected comparison failure', stage)
        with patch.object(p, '_rpc', side_effect=rpc):
            with self.assertRaises(p._WorkerError): asyncio.run(p._driver(object(), object(), result))
        self.assertEqual(len(result['actor_score']), 1)
        self.assertIn('sg_wake', result)
        self.assertNotIn('actor_native_restore_control', result)

    def test_worker_error_receipt_keeps_json_safe_completed_stage(self):
        def handlers(torch, saver, mode, device, evidence):
            def fail():
                evidence['actor_native_restore_control'] = {'actual_native_scores': [-1., -2.]}
                raise RuntimeError('injected comparison failure')
            return {'onload': lambda: SimpleNamespace(success=True), 'control': fail}
        connection = Connection([('onload', ()), ('control', ()), ('close', ())])
        with patch.object(torch.distributed, 'init_process_group'), patch.object(p, '_sglang', side_effect=handlers):
            p._worker(connection, 'sglang', 'cpu', 0, 'not-opened')
        failure = next(value for value in connection.sent if 'error' in value)
        json.dumps(failure)
        self.assertEqual(failure['evidence']['onload'], {'completed': True})
        self.assertEqual(failure['evidence']['actor_native_restore_control']['actual_native_scores'], [-1., -2.])
        with self.assertRaises(p._WorkerError): p._rpc(Connection([failure]), 'control')

    def test_main_errors_persist_evidence_and_raise(self):
        root = Path(tempfile.mkdtemp(prefix='eval-restore-report-check-'))
        for index, error in enumerate([RuntimeError('comparison failed'), EOFError('worker lost'), p._WorkerError('control', 'worker comparison failed', {'actual_native_scores': [-1., -2.]})]):
            async def driver(actor, sg, result):
                result['actor_score'].append({'native_scores': [-2.0794415]})
                result['sg_wake'] = {'scores': [-2.0794415]}
                raise error
            target = root / f'error-{index}.json'
            with patch.object(p.mp, 'get_context', return_value=Context()), patch.object(p, '_driver', side_effect=driver), patch('sys.argv', ['probe', '--mode', 'cpu', '--report', str(target)]), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(type(error)): p.main()
            result = json.loads(target.read_text())
            self.assertEqual(result['verdict'], 'ERROR')
            self.assertEqual(len(result['actor_score']), 1)
            self.assertIn('sg_wake', result)
            self.assertIn('error', result)
            if isinstance(error, p._WorkerError): self.assertEqual(result['worker_error']['evidence'], error.evidence)
        print('Fault report evidence directory:', root)

    def test_cleanup_failure_cannot_publish_pass(self):
        async def driver(actor, sg, result):
            result.update(actor_score=[{'weight_equal_at_forward': True}], sg_wake={'weight_equal_after_native_resume': True}, actor_native_restore_control={'weight_equal_after_native_switch': True, 'score_max_error_after_native_switch': 0, 'optimizer_state_equal': True, 'master_equal': True})
        target = Path(tempfile.mkdtemp(prefix='eval-restore-cleanup-check-')) / 'error.json'
        with patch.object(p.mp, 'get_context', return_value=Context(exitcode=7)), patch.object(p, '_driver', side_effect=driver), patch('sys.argv', ['probe', '--mode', 'cpu', '--report', str(target)]), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'exitcode=7'): p.main()
        result = json.loads(target.read_text())
        self.assertEqual(result['verdict'], 'ERROR')
        self.assertIn('actor_native_restore_control', result)
        self.assertIn('cleanup_error', result)

unittest.main(verbosity=2)
PY
```

Retained injected error reports: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/eval-restore-report-check-9c93p9f6/error-0.json`, `error-1.json`, `error-2.json`.

Final-source verification reran the exact `ReportingChecks` block extracted from this report: **6 passed in 0.017 seconds**, exit 0. Final probe/report newline and trailing-whitespace checks, probe AST parsing and both recorded inline-source AST checks passed. Repeat fault reports are retained under `/data/ycfeng/tmp/opencode-v2-tmp/opencode/eval-restore-report-check-rorw87s8/`.

### Actual native CPU control, error after completed comparison

The following command passed, exit 0. It reaches the actual native training restore/forward, then injects a later sleep exception and confirms the **completed** control receipts remain available. The exception is required and is not swallowed by the probe. Selected evidence: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/eval-restore-native-report-check-y1k0n46i/partial-native-control.json`.

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B - <<'PY'
import ast, json, tempfile
from pathlib import Path
import torch
from tests.manual.agent_opd import probe_eval_restore as p
root = Path(tempfile.mkdtemp(prefix='eval-restore-native-report-check-'))
torch.distributed.init_process_group('gloo', init_method=f'file://{root / "rendezvous"}', rank=0, world_size=1)
evidence = {}
handlers = p._actor(torch, p._CpuRemap(), 'cpu', torch.device('cpu'), evidence)
control = handlers['control']
actor = dict(zip(control.__code__.co_freevars, [cell.cell_contents for cell in control.__closure__]))['actor']
def fail_sleep(): raise RuntimeError('injected failure after completed comparisons')
actor.sleep = fail_sleep
try:
    control()
except RuntimeError as error:
    assert str(error) == 'injected failure after completed comparisons'
else:
    raise AssertionError('late error was swallowed')
snapshot = evidence['actor_native_restore_control']
assert snapshot['weight_equal_after_native_switch']
assert snapshot['score_max_error_after_native_switch'] == 0
assert snapshot['optimizer_state_equal'] and snapshot['master_equal']
assert snapshot['stopped_before_optimizer_step']
(root / 'partial-native-control.json').write_text(json.dumps(evidence, indent=2) + '\n')
print('Actual native CPU control late-error receipt: PASS', root)
torch.distributed.destroy_process_group()
source = Path('tests/manual/agent_opd/probe_eval_restore.py').read_text()
ast.parse(source)
assert source.endswith('\n') and all(line.rstrip() == line for line in source.splitlines())
f = json.loads(Path('task_memory/task_2026-11-06_qwen35_three_pairs/evidence/historical-torch-scores-and-C-flags.json').read_text())
for pair, expected in [('A', 4279), ('B', 4712)]:
    rows = [row for row in f['historical_scores'] if row['pair'] == pair]
    assert sum(row['count'] for row in rows) == expected
    assert all(row['backend'] == 'torch' and row['unique'] == 1 and row['min'] == row['max'] == -12.422473907470703 for row in rows)
    print('Historical torch raw evidence PASS', pair, expected)
print('Probe syntax/whitespace PASS')
PY
```

### 1. Planned scope completion

PASS: report tensors have CPU ownership; completed-stage receipts survive later errors; errors remain nonzero and cannot publish PASS. Parent corrected tiny-GPU rerun remains unexecuted by this subtask.

### 2. Drift check

CLEAR: changes are confined to the probe and this report. No production restore patch, additional workload, GPU/platform/Git operation, or kernel-only investigation was added.

### 3. Route correction

This checkpoint was superseded by the real-TMS retry and later authorized native transaction adaptation below. The current route is parent execution/review of the tiny CUDA/native-IPC loop; CPU results do not satisfy that runtime gate.

### 4. Three important limits

1. The original H800 log reaches native control but contains no equality report.
2. CPU tests verify reporting and error preservation, not CUDA remap contents.
3. Actual flags and historical torch evidence are incorporated; no kernel-only rerun is needed for this cause.

## Historical cleanup-only preparation

### Ownership and allocation/free lifetime

Local source inspected read-only: `/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/torch_memory_saver`, distribution **0.0.9.post1**. No installed file or library was changed.

- `hooks/mode_torch.py:10–19`: the pluggable allocator routes frees to `tms_torch_free`.
- `entrypoint.py:80–92`: the TMS instance owns a persistent private `torch.cuda.MemPool`; region scopes use that pool.
- `entrypoint.py:102–111`: native `_with_region_config` enables the interesting region on entry and disables it on exit.
- Local torch `cuda/memory.py:1295–1320`: `use_mem_pool` releases a scope's pool reference; that does not dispose TMS's persistent owner reference. Cached segments outlive the model/region until pool disposal/cache draining.
- The old worker only closed its connection. It left model/optimizer closure cycles and the private pool to interpreter teardown, outside an interesting region. The actual allocator error matches that free-lifetime violation; it is independent of the already-complete behavioral red.

`probe_eval_restore.py:68–92,357–394` now releases resources at the worker owner. For CUDA, it resumes tracked allocations for disposal, enters the existing native `_with_region_config`, drops handlers/model closure cycles, synchronizes, releases **this instance's owned private pool**, and drains the cache before leaving that region. CPU cleanup releases its own remap references. A never-initialized TMS instance has no pool to dispose. Connection close remains in `finally`, and disposal exceptions propagate. Parent worker-exit checks and `ERROR` reports remain unchanged.

TMS exposes no public disposal method; the probe therefore uses its inspected native internal region/pool ownership explicitly. This is a pinned test-harness teardown, not a production TMS API change or compatibility fallback. Parent pinned GPU cleanup remains unverified. No `os._exit`, ignored exit code, error suppression, process kill, installed-library edit, extra GPU allocation, or pre-fix behavioral rerun was introduced.

### Coordination with the completed restore patch

Read [QWEN-P3-EVAL-RESTORE-FIX report](test_report_2026-11-07_eval_restore_fix.md):19–28,119–123 and inspected current `train.py:42–64,105–111`. The scorer entrypoint now requires keyword **`rollout_executor`**; released weights are onloaded before calling the complete existing `placement_group.update_weights` owner, followed by only the released KV/graph tags. The current manual driver's old call at `probe_eval_restore.py:440–443` has not been adapted in this cleanup-only slice.

The next authorized adapter must supply the executor and execute that existing native start/publish/end/consumed-version transaction. The other agent's CPU owner-boundary checks are not real CUDA IPC proof; this probe's CPU cleanup spies are not transport proof either. A bare model copy or mocked `update_weights` success cannot establish the required green. No production `train.py`, `actor.py`, or existing fast fixture was edited by this subtask.

### Exact CPU cleanup checks

Working directory `/data/ycfeng/sota-engine/miles`; Python **3.12.13**, CPU torch **2.11.0+cu130**. The command below executes the **actual installed Python `_with_region_config` and `BinaryWrapper.set_config` methods**, with CPU allocation/free spies. It invokes no CUDA runtime or platform operation. It does not rerun the already-measured behavioral loop.

Observed: **6 tests passed in 0.205 seconds, exit 0**. Old unowned pool release reproduces a false interesting-region flag and the strict free check goes red. Owner disposal releases cyclic resources and the pool with the flag true, before cache draining; the original region configuration is restored afterward. Injected free/worker-cleanup failures propagate, and already-sent result receipts remain intact.

Final-source repeat extracted this exact cleanup-only block from the report: **6 passed in 0.202 seconds, exit 0**. Probe/report syntax, newline and trailing-whitespace checks and recorded inline-source AST checks passed. A local JSON check confirms complete real-TMS actor/SG red and exact native control recovery, with only `cleanup_error` and the unchanged overall `ERROR` verdict. No behavioral or GPU loop was rerun.

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B - <<'PY'
import ast, contextlib, copy, gc, unittest, weakref
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import torch
from tests.manual.agent_opd import probe_eval_restore as p
lib = Path('/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/torch_memory_saver')
ns = {'contextmanager': contextlib.contextmanager, '_TAG_DEFAULT': 'default'}
for filename, class_name, method in [('entrypoint.py', '_TorchMemorySaverImpl', '_with_region_config'), ('binary_wrapper.py', 'BinaryWrapper', 'set_config')]:
    cls = next(n for n in ast.parse((lib / filename).read_text()).body if isinstance(n, ast.ClassDef) and n.name == class_name)
    cls.body = [n for n in cls.body if getattr(n, 'name', None) == method]
    exec(compile(ast.Module(body=[cls], type_ignores=[]), str(lib / filename), 'exec'), ns)

class State:
    def __init__(self): self.interesting, self.backup, self.events = False, True, []
    def tms_get_interesting_region(self): return self.interesting
    def tms_get_enable_cpu_backup(self): return self.backup
    def tms_set_interesting_region(self, value): self.interesting = value
    def tms_set_enable_cpu_backup(self, value): self.backup = value
    def tms_set_current_tag(self, value): self.tag = value

class Pool:
    def __init__(self, state): self.state = state
    def __del__(self): self.state.events.append(('pool_release', self.state.interesting))

class Resource:
    def __init__(self, state): self.state, self.cycle = state, self
    def __del__(self): self.state.events.append(('resource_release', self.state.interesting))

def setup():
    state = State()
    binary = ns['BinaryWrapper'](); binary.cdll = state
    impl = ns['_TorchMemorySaverImpl'](); impl._binary_wrapper = binary
    impl._primary_mem_pool = Pool(state)
    def empty_cache():
        state.events.append(('empty_cache', state.interesting))
        if not state.interesting: raise RuntimeError('only support interesting region')
        assert impl._primary_mem_pool is None
    fake_torch = SimpleNamespace(cuda=SimpleNamespace(synchronize=lambda: state.events.append(('synchronize', state.interesting)), empty_cache=empty_cache))
    saver = SimpleNamespace(_impl=impl, resume=lambda: state.events.append(('resume', state.interesting)))
    return state, saver, fake_torch

class CleanupChecks(unittest.TestCase):
    def test_old_unowned_pool_release_is_red(self):
        state, saver, fake_torch = setup()
        saver._impl._primary_mem_pool = None
        self.assertIn(('pool_release', False), state.events)
        with self.assertRaisesRegex(RuntimeError, 'interesting region'): fake_torch.cuda.empty_cache()

    def test_owner_releases_under_real_native_region_config(self):
        state, saver, fake_torch = setup()
        handlers = {'model': Resource(state)}
        resource_ref = weakref.ref(handlers['model'])
        pool_ref = weakref.ref(saver._impl._primary_mem_pool)
        p._close_allocations(fake_torch, saver, handlers, 'cuda')
        self.assertFalse(handlers)
        self.assertIsNone(resource_ref()); self.assertIsNone(pool_ref())
        self.assertIn(('resource_release', True), state.events)
        self.assertIn(('pool_release', True), state.events)
        self.assertIn(('empty_cache', True), state.events)
        self.assertLess(state.events.index(('pool_release', True)), state.events.index(('empty_cache', True)))
        self.assertFalse(state.interesting); self.assertTrue(state.backup)

    def test_cache_free_failure_propagates(self):
        state, saver, fake_torch = setup()
        def fail(): raise RuntimeError('injected cache free failure')
        fake_torch.cuda.empty_cache = fail
        with self.assertRaisesRegex(RuntimeError, 'cache free failure'): p._close_allocations(fake_torch, saver, {}, 'cuda')
        self.assertFalse(state.interesting); self.assertTrue(state.backup)

    def test_cpu_owner_is_released(self):
        saver = p._CpuRemap(); saver.regions.append(object())
        handlers = {'model': object()}
        p._close_allocations(None, saver, handlers, 'cpu')
        self.assertFalse(handlers); self.assertFalse(saver.regions)

    def test_uninitialized_pool_needs_no_cuda_call(self):
        handlers = {'model': object()}
        p._close_allocations(None, SimpleNamespace(_impl=None), handlers, 'cuda')
        self.assertFalse(handlers)

    def test_worker_cleanup_error_is_not_swallowed(self):
        class Connection:
            def __init__(self): self.commands = iter([('observation', ()), ('close', ())]); self.sent = []; self.closed = False
            def recv(self): return next(self.commands)
            def send(self, value): self.sent.append(copy.deepcopy(value))
            def close(self): self.closed = True
        connection = Connection()
        with patch.object(torch.distributed, 'init_process_group'), patch.object(p, '_sglang', return_value={'observation': lambda: {'completed': True}}), patch.object(p, '_close_allocations', side_effect=RuntimeError('injected worker cleanup failure')):
            with self.assertRaisesRegex(RuntimeError, 'worker cleanup failure'): p._worker(connection, 'sglang', 'cpu', 0, 'not-opened')
        self.assertTrue(connection.closed)
        self.assertIn({'result': {'completed': True}}, connection.sent)

unittest.main(verbosity=2)
PY
```

### Cleanup checkpoint: 1. Scope completion

PASS: worker-owned pool disposal is prepared and CPU lifetime/error checks pass. Actual GPU cleanup and the new complete native transaction adapter are pending; no fixed-path green is claimed.

### Cleanup checkpoint: 2. Drift check

CLEAR: only the manual probe and this report changed. No pre-fix behavioral rerun, production/fixture/library edit, GPU/platform/Git action, generic kernel investigation, or new publication substitute.

### Cleanup checkpoint: 3. Next action

Parent coordinates the complete native executor/publication adapter, then owns fixed-path GPU qualification. Do not relaunch the old adapter or repeat the causal red loop solely to remeasure known failures.

### Cleanup checkpoint: 4. Three limits

1. The actual frozen loop already proves byte loss and native actor recovery; its overall execution error is separate.
2. Disposal uses the inspected pinned TMS internal pool/config ownership because no public disposal method exists; actual GPU teardown remains unverified.
3. A green loop requires the full existing same-version update transaction and honest CUDA IPC evidence, not a mock or bare copy.

## Current native transaction adaptation

[Original Request] The next owned slice authorizes only this probe and report: adapt to the repaired `rollout_executor` callback and complete `placement_group.update_weights`; prepare at least two same-version tiny TMS cycles, zero optimizer updates, real native CUDA IPC sender/bucket/receiver in CUDA mode, and supported cleanup. A tiny `load_weights` destination and local control-RPC shim are allowed when declared accurately. CPU execution is not GPU/IPC qualification. The parent owns GPU execution/review; production/RPC/fast-fixture files and failure semantics remain outside this slice.

**Current outcome:** the adapter is implemented and the two-cycle CPU orchestration check passes. There is no observed API/architecture blocker at this seam. **CUDA/native-IPC qualification and actual CUDA teardown remain pending parent execution**, not implied by the CPU result or the earlier real-TMS causal red.

### Native path and declared boundaries

- `train.py:42–122` is loaded without behavior edits and receives the required executor. Its weight-onload path invokes the actual `miles/ray/placement_group.py:317–359` start/publish/end/consumed-version transaction.
- Publication calls the actual `MegatronTrainRayActor.update_weights` and `_update_receiver_weights`, then the imported backend-neutral `WeightUpdater`. The protocol is asserted to be the native `UpdateWeightFromTensor`.
- CUDA sender execution is native `protocols/cuda_ipc.py:162–186,193–258`: native flattened bucket creation, `MultiprocessingSerializer.serialize`, Gloo gather, receiver API invocation and producer-lifetime barrier. CUDA mode does not replace these methods or the native after-resume IPC collection.
- Receiver execution uses native `BaseTpWorker.deserialize_own_rank`, native `SchedulerWeightUpdaterManager` begin/update/end, and native model-runner `WeightUpdater.update_weights_from_tensor` / `_update_weights_from_flattened_bucket`. CUDA uses the installed reduction patch and actual imported CUDA tensors. Every receipt records the distinct sender/receiver process IDs, imported device, bucket bytes and completed native load.
- **Control boundary:** local pipes replace Ray/HTTP controller delivery. The local API client preserves the native tensor/version request methods; direct HTTP-only pause/resume/cache/version-query methods are routed over the same control pipe. HTTP base64 metadata is decoded before constructing the native internal request. Tiny base-only begin/end requests assert `sync_base=True` and no adapter checksums. This is not a full SGLang server, Ray control deployment, real KV cache or CUDA graph capture.
- **Model boundary:** the supplied public iterator factory projects the one tiny parameter named `weight`; the native sender transports it. The tiny model's `load_weights` copies the imported tensor into its destination parameter, as a model loader must. This destination copy is **not** a replacement for IPC transport. Both 8x8 BF16 models start from identical CPU-generated bytes before device transfer.
- **Optimizer boundary:** fixture constructors that perform `Adam.step()` are not used. Native Adam `_init_group` initializes state only; no optimizer step runs. Initial Adam step/moments are zero, the FP32 master is nonuniform, and the native ordinary-training control stops immediately after forward. Master, moments, step tensor and param groups must remain unchanged.
- Equality is shape/dtype/raw-byte equality for model/master/Adam tensors. Scores must stay nonuniform and have exactly zero error against each component's native baseline. Actor, engine and consumed rollout versions remain **7** over both cycles. The two native engine frames and two controller transaction frames must match the expected order.
- **Cleanup ownership:** actual CUDA synchronization is restored after installing the pipeline fixture. Worker cleanup first releases fixture globals (including the object store) inside the interesting region, collects model references, disposes its own pool and drains cache. Receiver shutdown precedes producer peer closure. Exit codes are recorded and remain hard failures of this probe; no library edit, `_exit`, error suppression or process killing is used.
- **CPU exception:** injected no-backup remaps and native CPU tensor serialization test orchestration only. CPU mode explicitly skips CUDA reduction hooks / post-resume CUDA collection and always reports `cuda_ipc_qualified=false`.

### Exact CPU command and observed checks

Working directory `/data/ycfeng/sota-engine/miles`; Python **3.12.13**, torch **2.11.0+cu130**, SGLang **0.5.23**. No conda or CUDA execution in this subtask.

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m tests.manual.agent_opd.probe_eval_restore \
--mode cpu --report /data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_native_transaction_cpu_final.json \
> /data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_native_transaction_cpu_final.log 2>&1
```

First complete adapter run: **PASS, 24.2268 seconds, exit 0**. Raw-byte comparison run: **PASS, 24.7523 seconds, exit 0**. The most recent final-source result is appended below rather than treating either CPU run as CUDA qualification.

Prior adapter source, including identical CPU initialization before device transfer: **PASS, 24.4756 seconds, exit 0**. Both cycles have scorer/SG/control score errors **(0.0, 0.0, 0.0)**, exact parameter/master/Adam bytes, zero optimizer steps and version 7. Workers **902935 / 902936** both exit **0**; `cuda_ipc_qualified=false`. This older CPU mapper did not reject active resume; the strict lifecycle correction below supersedes its cleanup qualification.

| Gate, both cycles | Observed | Result |
| --- | --- | --- |
| Native eval scorer parameter bytes / baseline scores | Equal; score max error **0.0**, nonuniform | PASS |
| SG post-publication parameter bytes / scores | Equal; score max error **0.0**, nonuniform | PASS |
| Native ordinary-training control | Exact bytes; score max error **0.0** | PASS |
| Master / Adam tensors and param groups | Unchanged; optimizer step **0.0** | PASS |
| Versions | Actor **7**, engine **"7"**, published/consumed **7** | PASS |
| Outer transaction | Twice `start → publish → end → rollout_set_version` | PASS |
| Engine session | Twice `pause_generation → flush_cache → begin_weight_update → update_weights_from_tensor → end_weight_update → update_weight_version → continue_generation → model_info` | PASS |
| Native imported buckets | **2 × 128 bytes**, distinct processes, CPU tensors | PASS for CPU serialization only |
| Process cleanup | Both exit **0** | PASS on CPU; CUDA disposal pending |
| CUDA IPC qualification | Explicitly **false** | NOT QUALIFIED |

Four additional byte-comparison boundary checks passed: equal scalar, distinct signed-zero bits, different shape, and different dtype. AST checks confirm no `step()` call in the actor fixture and no `_exit`, terminate or kill path; syntax/whitespace checks passed.

Integration failures were probe-owned and corrected against inspected APIs: deserialization belongs to `BaseTpWorker`, not its child; derived no-LoRA/FT arguments needed explicit supported values; HTTP-only client methods needed control shims; internal array-like msgspec structs needed named constructors and HTTP-shaped output dictionaries. Failed runs retained scorer evidence and abort/error receipts; none was called PASS.

The historical cleanup-only six cases were re-executed against the current peer signature with the following exact adaptation command. **6 passed in 0.215 seconds, exit 0.** The worker test uses only CPU control spies; this is not IPC proof. An initial bootstrap exec namespace discovered zero tests and exited 5; using the actual module globals corrected that test runner, not the probe.

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B - <<'PY'
import re
from pathlib import Path
text=Path('task_memory/task_2026-11-06_qwen35_three_pairs/test_report_2026-11-07_eval_restore.md').read_text()
block=next(x for x in re.findall(r'```bash\n(.*?)\n```',text,re.S) if 'class CleanupChecks' in x)
source=block.split("<<'PY'\n",1)[1].rsplit('\nPY',1)[0]
source=source.replace('connection = Connection()', 'connection = Connection(); peer = Connection()')
source=source.replace("with patch.object(torch.distributed, 'init_process_group'),", "with patch('miles.utils.distributed_utils.init_gloo_group'), patch.object(p, 'wait', return_value=[connection]), patch.object(torch.distributed, 'init_process_group'),")
source=source.replace("p._worker(connection, 'sglang', 'cpu', 0, 'not-opened')", "p._worker(connection, 'sglang', 'cpu', 0, 'not-opened', peer)")
exec(compile(source,'<cleanup-checks-current-peer-signature>','exec'),globals())
PY
```

### Parent-only CUDA command and required result

From the final source root, in the parent's approved single-H800 worker and pinned CUDA compatibility environment:

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.probe_eval_restore \
--mode cuda --gpu-id 0 --report "$RESTORE_REPORT"
```

Expected: exit **0**, verdict **PASS**, `cuda_ipc_qualified=true`, two complete same-version cycles, two actual CUDA bucket imports between distinct processes, byte equality / nonuniform zero-error scores, unchanged master/Adam with zero steps, two full transaction/session frames and both worker exits **0**. Any native transport/teardown failure must retain the completed data and return **ERROR**, not PASS. A successful tiny result does not qualify full Qwen training, TP4/DP2, formal D8 or optimizer capacity. No further pre-fix causal-red or kernel-only GPU run is requested.

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 新 executor / 完整 native transaction 适配 | PASS | 实际 CPU 两周期完成完整 frame。 |
| native sender/receiver seam 实现 | PASS | CUDA 路径保留 native transport；CPU 真实序列化已运行。 |
| byte/version/zero-step/cleanup CPU 检查 | PASS | 本节记录两周期和六项 lifetime 检查。 |
| 本子任务 GPU/platform/Git 操作 | SKIPPED | 用户明确禁止，由父任务负责。 |
| tiny CUDA IPC green 与 review | TODO | 仍待父任务实测和审阅。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 新 owned slice 授权至今｜**当前前沿：** 父任务 tiny CUDA/native-IPC 实测。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | probe 就是本次交付；CPU gate 完成后停止扩展。 |
| D2 细节反复重试 | CLEAR | 分别定位并修复具体 API 边界，未重复 GPU 尝试。 |
| D3 支线问题修补 | CLEAR | 未进入 core failure semantics、OOM 或 kernel 支线。 |
| D4 可并行任务停滞 | CLEAR | 用户禁止 delegation；GPU/review 和 core 调查由各自 owner 执行。 |
| D5 超范围镀金 | CLEAR | 只有固定 tiny model、两周期和所需 IPC/control seam，无新 CLI flags。 |
| D6 分析空转 | CLEAR | 产出可执行 native adapter 和真实 CPU 两周期结果。 |
| D7 路线违背 | CLEAR | 只编辑 probe 与现有报告，未执行 GPU/platform/Git。 |

**文档检查：** S5：本报告旧 cleanup-only blocker 已标为 historical，并由当前结果取代；S1–S4、S6 未发现本 slice 的明显缺陷。父任务旧 progress 摘要仍需由其维护，不在本次文件 ownership 内。
**归因：** 无。

## 3. 纠正建议

**分支：** B：本报告旧 adapter pending 文案已更新。
**文档更新（先执行）：** 当前报告已记录新授权、真实 CPU 结果及尚未运行的 CUDA gate（可直接执行，已完成）。
**需停止的偏离行为：** 无。
**接下去的路线：** 父任务审阅最终 probe → 在已批准的 1H800 上执行上述 CUDA 命令 → 完成标志：全部 tiny native-IPC、版本、bytes、zero-step 和退出条件通过；实际 formal continuation 仍由父任务处理。

## 4. 最值得关注的 3 点

1. CPU PASS 不是 CUDA IPC qualification；本报告仍明确保留 runtime pending。
2. 本地 pipe 只替代控制 RPC；CUDA bucket/open/transfer 必须由 native transport 完成。
3. 没有新增 optimizer update 或 Qwen workload，也没有修改 production failure semantics。

## Latest strict cleanup lifecycle correction

[Original Request] Before parent GPU launch, check the unconditional cleanup `saver.resume()` against native invalid-active-resume evidence, inspect paused free and torch-hook `disable()` semantics, and correct only the probe/report with a focused strict CPU lifecycle regression. No GPU/platform/Git/SSH/cloud/delegation, suppression, signals, library/core edit or native IPC replacement.

**Correction:** `_close_allocations` no longer calls raw `saver.resume()`. It calls the existing owner before releasing storage: native `actor.wake_up()` for the actor, and native SGLang `resume_memory_occupation` only for the manager's nonempty `offload_tags`. An ACTIVE SG manager has no paused tags, so no resume request is issued; an empty tag list must not be sent because native SGLang interprets it as resume-all. Existing pool disposal still occurs inside the native interesting region. The CPU mapper now rejects duplicate pause and active resume instead of silently ignoring them. Native sender/bucket/receiver code is unchanged.

### Inspected pinned semantics

The parent-owned [core report](test_report_2026-11-07_eval_restore_fix.md):201–218 documents the installed active-resume exit(1) branch. This subtask independently inspected the same pinned torch-hook binary, without executing it:

- Native pause unmaps at **0x3e11**, releases its physical handle at **0x3e24**, and stores paused state at **0x3e33**.
- Native `free(void*)` has no paused-state branch before unconditional `cuMemUnmap` at **0x5253** and `cuMemRelease` at **0x5267**; failure leads to native exit(1). Merely deleting cleanup resume would therefore assume that already-unmapped/released storage can be freed again. The owner must map paused allocations before pool free. This is inspected control flow, not an induced real-GPU paused-free result.
- Healthy probe control calls native `actor.sleep()` after each forward. The strict two-cycle report confirms `final_actor_asleep=true`. Native actor `wake_up` at `actor.py:541–559` resumes only when asleep and records mapped residency before clear/PG reload.
- Native SG release/resume at installed `scheduler_components/weight_updater.py:337–422` owns `offload_tags`. The strict two-cycle report confirms **empty SG offload tags** at both completed cycles. Cleanup only resumes actual outstanding tags; it does not invent a second residency flag.

Installed TMS Python prefix: `/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/torch_memory_saver`.

- `hooks/mode_torch.py:10–19` creates the allocator using **`tms_torch_malloc` / `tms_torch_free`**; it does not replace the global allocator.
- `entrypoint.py:88–92` routes the torch-mode primary pool inside an interesting region.
- `entrypoint.py:113–127` explicitly supports `disable()` inside that region: require interesting=true, set false, use a separate `torch.cuda.MemPool()` with its default allocator, dispose that pool, restore interesting=true. There is no preload-only guard on this method. The preload-only restriction belongs to `cuda_graph`, not disable.
- Pinned torch `cuda/memory.py:1245–1249` declares `allocator=None` as the default/current caching allocator, and `:1296–1320` provides current-thread pool routing. The strict CPU check executes the **actual installed region/disable/config Python methods** with allocator-state spies, asserting primary/TMS → default/disabled → primary/TMS, including pool disposal.

This establishes the intended **torch-hook Python API path**, not a formal-preload equivalence claim or physical CUDA qualification. Actual nested CUDA pool allocation/free and CUDA IPC remain for the parent GPU run.

Exact read-only binary commands:

```bash
nm -C /data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/torch_memory_saver_hook_mode_torch_cu13.abi3.so
objdump -d -C --start-address=0x50a0 --stop-address=0x5810 /data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/torch_memory_saver_hook_mode_torch_cu13.abi3.so
objdump -d -C --start-address=0x62e0 --stop-address=0x6740 /data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/torch_memory_saver_hook_mode_torch_cu13.abi3.so
objdump -d -C --start-address=0x3d60 --stop-address=0x4080 /data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/torch_memory_saver_hook_mode_torch_cu13.abi3.so
```

### Strict regression and original-loop verification

Persistent, focused test lives in the owned probe: `test_native_tms_cleanup_lifecycle`. It tests initially ACTIVE SG, PAUSED actor through native `wake_up`, PAUSED SG through native manager resume, rejection of paused free, true-region pool disposal and the installed torch-mode disable implementation. Python spies raise assertions to detect native-invalid state; this does **not** claim native exit(1) is a catchable Python exception.

Exact unchanged red/green command, CPU environment Python **3.12.13**, torch **2.11.0+cu130**, pytest **9.1.1**:

```bash
TMS_PYTHON_PACKAGE=/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/torch_memory_saver \
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m pytest -p no:cacheprovider -q \
tests/manual/agent_opd/probe_eval_restore.py::test_native_tms_cleanup_lifecycle
```

| Check | Actual | Result |
| --- | --- | --- |
| Original unconditional cleanup resume | **1 failed, 2.42 s**, exit 1; exact callsite line98 fails `native active resume exits 1` on ACTIVE SG | Meaningful RED |
| Native-owner correction | **1 passed, 5.38 s**, exit 0 | GREEN |
| Strengthened pool/paused-free assertions | **1 passed, 5.88 s**, exit 0 | PASS |

Warnings are the existing CPU SGLang/vLLM optional-kernel and deprecation warnings; no CUDA runtime, binary or platform operation was executed.

The original fixed-path native two-cycle orchestration loop was also rerun with the now-strict mapper:

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m tests.manual.agent_opd.probe_eval_restore \
--mode cpu --report /data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_strict_cleanup_cpu.json \
> /data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_strict_cleanup_cpu.log 2>&1
```

**PASS, 25.9656 seconds, exit 0.** Both cycles retain exact model/master/Adam bytes, nonuniform scorer/SG/control scores with errors **(0,0,0)**, optimizer steps **0** and version **7**. Actor ends each cycle asleep; SG ends with `offload_tags=[]`. Worker PIDs **2085541 / 2085542** both exit **0**. `cuda_ipc_qualified=false`. AST checks confirm no raw resume in `_close_allocations`; syntax/whitespace checks pass.

Runtime limits: actual CUDA pool disposal, imported IPC storage lifetimes and allocator nesting still need the parent H800 run. The regression does not prove recovery from partial native resume/constructor failure or CUDA-driver faults; native fatal/worker-exit behavior remains an ERROR, never an inferred PASS. No production failure semantics changed.

### Strict lifecycle checkpoint

#### 1. 规划完成情况

PASS：native owner cleanup、active/paused strict regression、torch-hook Python disable 检查及严格 CPU 两周期。TODO：父任务实际 CUDA pool/IPC qualification。

#### 2. 偏离检测

D1–D7 均 CLEAR：只修用户指定的 cleanup owner 和相关 regression，未展开 core、kernel、平台或新 transport 工作。S5：旧宽松 CPU cleanup 证据已明确 superseded；其余 S1–S4/S6 未发现本 slice 的明显缺陷。

#### 3. 纠正建议

分支 B：已更新本报告的过时 cleanup qualification。停止把宽松 CPU remap 当作 native lifecycle 证据。父任务继续 pinned receipt tests 与实际 1H800 执行；本子任务不扩展测试或 GPU 操作。

#### 4. 最值得关注的 3 点

1. ACTIVE SG 不 resume；PAUSED actor 必须由 native owner map 后才能 free。
2. 已检查 torch-hook 的实际 Python disable 路径，不等同于 CUDA 实测。
3. 两周期保持版本 7 和零 optimizer updates；native IPC 未替换，runtime gate 仍未完成。

## Pinned published-storage owner correction

[Original Request] The exact pinned CPU preflight `exp-1107-131627-198417` failed because the tiny runner had no `remote_instance_weight_transporter.weight_info`. Supply factual startup address metadata through its existing fixture owner, preserve the native assertion/loaders/transport, add an address-movement negative control, and leave exact pinned CPU/CUDA execution to the parent. Scope: probe plus this report only; no extra CLI/core/library/Git/GPU/platform/SSH/cloud/delegation.

**Observed failure:** [local raw log](evidence/eval-restore-exp-1107-131627-198417.log):39–53 reaches pinned native `begin_weight_update → _assert_published_storage_unmoved`, then raises AttributeError on the absent owner. This is a concrete fixture ABI mismatch, not a sender/IPC or weight-value failure.

**Minimal correction:** the existing tiny `SimpleNamespace` runner now owns a metadata-only `remote_instance_weight_transporter` with a non-None dictionary:

```python
{name: (param.data_ptr(), param.numel(), param.element_size())
 for name, param in model.named_parameters()}
```

It is captured once at model startup by `_published_weight_info`, before any update session, and is **never recomputed after loads**. Only the one real BF16 8×8 parameter is published in this fixture. Static buffers are not parameters. No transfer engine is initialized, remote bootstrap is not simulated or claimed, and this holder supplies only the factual metadata queried by the native gate. Native begin/end assertions, loaders, bucket sender/receiver and CUDA IPC remain untouched; there is no None skip or check monkeypatch. No broader fake ModelRunner is needed.

### Exact pinned source and negative control

Source revision: **056f871a7ee8b4573832049011f0fdf52589cfd8**.

- [Pinned WeightUpdater](https://raw.githubusercontent.com/sgl-project/sglang/056f871a7ee8b4573832049011f0fdf52589cfd8/python/sglang/srt/model_executor/model_runner_components/weight_updater.py):330–353 reads the owner's `weight_info`, then compares published addresses/bytes to current named parameters. The unchanged assert rejects a moved/removed/resized parameter.
- [Pinned native metadata owner](https://raw.githubusercontent.com/sgl-project/sglang/056f871a7ee8b4573832049011f0fdf52589cfd8/python/sglang/srt/model_executor/model_runner_components/remote_instance_weight_transporter.py) declares `weight_info: Optional[dict[str, tuple[int, int, int]]]`. The actual engine/registration methods are unrelated to the read-only gate and are not replaced by this fixture.

Persistent test: `tests/manual/agent_opd/probe_eval_restore.py::test_pinned_published_storage_rejects_address_movement`. It compiles the **unedited native assertion method from the exact downloaded pinned source**, not the local 0.5.23 module that lacks this check. Same-address metadata passes. Replacing the BF16 8×8 Parameter with an identical-value clone changes its address and raises the native **`a weight-update session moved published parameters` AssertionError**. Restoring the original Parameter passes again; the startup metadata is unchanged throughout.

Exact download/check commands:

```bash
curl --fail --silent --show-error \
'https://raw.githubusercontent.com/sgl-project/sglang/056f871a7ee8b4573832049011f0fdf52589cfd8/python/sglang/srt/model_executor/model_runner_components/weight_updater.py' \
--output /data/ycfeng/tmp/opencode-v2-tmp/opencode/sglang-056f871a7ee8b4573832049011f0fdf52589cfd8-weight_updater.py

SGLANG_PINNED_WEIGHT_UPDATER_SOURCE=/data/ycfeng/tmp/opencode-v2-tmp/opencode/sglang-056f871a7ee8b4573832049011f0fdf52589cfd8-weight_updater.py \
TMS_PYTHON_PACKAGE=/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages/torch_memory_saver \
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m pytest -p no:cacheprovider -q \
tests/manual/agent_opd/probe_eval_restore.py::test_pinned_published_storage_rejects_address_movement \
tests/manual/agent_opd/probe_eval_restore.py::test_native_tms_cleanup_lifecycle
```

**PASS: 2 tests, 5.17 seconds, exit 0**, including the expected native-assert address-movement failure. CPU Python **3.12.13**, torch **2.11.0+cu130**, pytest **9.1.1**. Existing optional-kernel/deprecation warnings only.

Local two-cycle command additionally passed:

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m tests.manual.agent_opd.probe_eval_restore \
--mode cpu --report /data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_address_owner_cpu.json \
> /data/ycfeng/tmp/opencode-v2-tmp/opencode/eval_restore_address_owner_cpu.log 2>&1
```

**Local orchestration PASS: 25.8279 seconds; workers 2411959/2411960 exit 0; both cycles score errors (0,0,0), optimizer updates 0, version 7; `cuda_ipc_qualified=false`.** This uses local **SGLang 0.5.23**, not the exact pinned runtime. It cannot qualify the full pinned begin/end path; only the isolated assertion negative control above executes the pinned gate. Syntax and whitespace checks pass.

**Pending parent gate:** rerun the original **exact pinned CPU two-cycle preflight once**; only after that passes, run the parent-owned CUDA loop. Physical CUDA IPC and pool teardown remain unqualified here. No blocker requiring a broader runner was observed for this concrete ABI correction.

### Published-address slice checkpoint

#### 1. 规划完成情况

PASS：事实启动 metadata、保留 pinned native assert 的地址移动负例、本地 CPU regression。TODO：父任务 exact pinned CPU 与 CUDA 两周期。

#### 2. 偏离检测

D1–D7 CLEAR：仅修具体 ABI 缺口，没有扩大 fake runner 或替换 transport。S1–S6 未发现本 slice 的明显缺陷；local/pinned qualification 已明确区分。

#### 3. 纠正建议

分支 A：保持范围不变，停止本地扩展；父任务先 exact pinned CPU，通过后再 CUDA。完成标志仍是原生 gate、字节/分数、同版本、零 optimizer updates 与退出检查全部通过。

#### 4. 最值得关注的 3 点

1. metadata 是实际启动地址快照，不是 None skip，也没有 load 后重算。
2. clone 地址移动触发的是 pinned 原 assert；native sender/receiver 未改。
3. 本地 0.5.23 通过不等于 pinned runtime 通过，父任务 preflight 仍必需。
