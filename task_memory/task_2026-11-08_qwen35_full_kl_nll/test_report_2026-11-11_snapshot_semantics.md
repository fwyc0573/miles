## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Prepare the isolated native CUDA worker and operator-input config; verify syntax/help/config only. GPU semantics remain UNVERIFIED for PRIMARY execution. |
| 2026-11-11 | Primary independently validated the operator config and inspected native calls/cache placement before freezing the worker for H800 execution. |

# Native selected-FP32 snapshot semantics preparation

TaskID: `profile-native-snapshot-semantics-20261111`.

**Result: CPU-ready worker. CUDA compilation, H800 execution and numerical semantics are UNVERIFIED.** No platform/authentication/submission/SSH/GPU execution, dependency edit, staging or commit was performed by this agent. Only the requested worker, operator-input config and this report were created.

## Deliverables and authority

- Worker: `tests/manual/agent_opd/probe_mamba_fp32_snapshots.py`.
- Operator inputs: `mamba_snapshot_semantics_config.json` in this task directory.
- This report.

The worker reads `formal_config.json` as the existing owner of image, native Python, local mount, worker-local root and declared cloud mounts. It does not modify that configuration, teacher/model sources, scientific inputs, cache policy, backend policy or numerical tolerances. The explicit delegated request adds this small isolated operator verification to the existing [S8 source-fidelity acceptance](spec.md#s8-gpu-与执行d16d19d33d39d40); it is not a new formal run or an auxiliary training gate. [Requirements D40](requirements.md#workflowparameter-rca--original-request-2026-11-11), [plan](plan.md#current-frontier), and the [source candidate report](test_report_2026-11-11_mamba_fp32_snapshots.md) retain their authority.

## Inspected native ABI

All native references below use C3:

`evidence/native-sglang-cache-source-20261111/exp-1111-042450-358109/source/`.

| Source | Observed contract used by this probe |
| --- | --- |
| `srt/layers/attention/linear/kernels/gdn_triton.py:169–215` | `TritonGDNKernel.extend(q,k,v,g,beta, *, ssm_states,cache_indices,query_start_loc,inplace_update=True,**kwargs)` invokes the native chunk operator with Q/K L2 normalization. Candidate forwarding is supplied only by the existing preparer. |
| `kernels/ops/attention/fla/chunk.py:93–132,135–269` | Equal-length `[B,T,H,D]` with `cu_seqlens=None` is supported. Actual return is `(o,None,h)`, despite stale final-state prose. Native final state is written into the caller's state pool, not returned separately. |
| `kernels/ops/attention/fla/chunk_delta_h.py:122–150,171–207,331–348,371–397` | FP32 accumulator snapshot is stored before chunk `c`; `h[c]` represents the state after exactly `64*c` tokens. Ordinary `h` is BF16 from `k.new_empty`; final state follows the FP32 pool dtype. State slots use `initial_state_indices`; snapshots use batch-row indices. Negative state index loads zero and skips final write; negative tracking index skips snapshot stores. |
| `kernels/ops/attention/fla/index.py:16–26` | Native varlen index preparation calls `.tolist()` on lengths. This probe deliberately uses the supported equal-length operator ABI and does not change or emulate that function. |
| `srt/runtime_context.py:1958–1971` | Prefill checkpoint grid is `lcm(mamba_cache_chunk_size,tree_page)`, distinct from the kernel chunk and decode interval. Config supplies operator inputs `64` and `1`; this probe does not measure live engine cache metadata. |
| `test/kits/attention_unittest/attention_methods/gdn_attention.py:38–45,81–162,795–887,1193–1215` | Retained backend tests use BF16 CUDA inputs, FP32 temporal state, and a custom recurrence with loose tolerances. That recurrence and those tolerances are not copied; this probe instead compares native prefix final states exactly. |

The existing `prepare_source` is invoked before attention imports and validates the actual installed version, image and all six native hashes, then archives its exact two-file candidate. The worker does not guess a final-state API, replace native functions, or apply additional source edits. Both comparison modes run in the **same qualified candidate**, with tracking disabled/enabled; this is explicitly **not untouched-code GPU A/B**.

## Configured cases and required GPU checks

The config owns seed1234; BF16 Q/K/V; FP32 gates/temporal state/snapshots; int32 indices; batch3; Q/K heads2/value heads4; key/value dimensions128; four state slots; nonsequential cache indices `[2,0,-1]`; sequence lengths192/193; interior boundaries64/128; selected chunk-entry rows `[1,2,-1]` and `[2,1,-1]`; initial-state/gate scales and diagnostic snapshot sentinel. These are small **operator inputs**, not claimed live model dimensions or a teacher-cache-policy change.

Ten native producer forwards are enqueued: for each length, one ordinary, two selected-snapshot and two independent prefix forwards. The ordinary and selected cases clone the same initial state. Prefix forward at `c*64` supplies the actual native FP32 final-state oracle for snapshot row `i` and its configured state slot. No GPU tensor contents are read by the probe until all ten producer forwards end. One explicit synchronization occurs only in the end inspection phase; no new read/wait/synchronization is inserted into the producer function. Native compilation/autotuning remains unmodified. This arrangement is an isolated semantics test, **not a race-exclusion experiment**.

Required verdict checks:

1. Actual formal worker Python, installed native source receipt, CUDA snapshot capability, H800 Torch identity and `nvidia-smi`; fresh worker-local Triton cache with produced CUDA binaries.
2. Ordinary BF16 output and `h`, and FP32 final pool, are finite and exactly unchanged for each tracking case. Native return/layout/dtype contract is retained.
3. Every selected interior snapshot exactly equals its corresponding native prefix's FP32 final state. Both boundaries are selected for both live batch rows across the two tracking cases.
4. Snapshot rounded to BF16 equals the ordinary `h` at the same chunk entry. At least one element differs between the FP32 snapshot and BF16 `h` cast back to FP32, so dtype-only BF16 round-trip storage cannot qualify.
5. `-1` tracking rows retain the diagnostic sentinel, padded state rows start with zero ordinary `h`, and unused state slots remain unchanged. No zero-token forward is added: it is not a reachable teacher-scoring input. No mocked CUDA, skip, fallback or invented tolerance can produce PASS.

Each numerical comparison records absolute error, relative error only where its reference is nonzero, zero-reference element counts and zero-reference absolute error. Relative error at zero is undefined; nonfinite values fail and their errors are marked undefined rather than serialized as NaN/Infinity. Actual dtype/shape/stride, native signatures, supplied arguments and runtime environment are retained. Values are **not yet measured**.

## CPU verification

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13; also `/usr/bin/python3`3.10.6 for syntax/JSON parsing. No dependency installation or Torch/Triton/SGLang import occurs in the CPU modes.

Exact commands from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.probe_mamba_fp32_snapshots --help
PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.probe_mamba_fp32_snapshots --config task_memory/task_2026-11-08_qwen35_full_kl_nll/mamba_snapshot_semantics_config.json --validate-config
/usr/bin/python3 -B - <<'PY'
import ast, json
from pathlib import Path
worker = Path('tests/manual/agent_opd/probe_mamba_fp32_snapshots.py')
ast.parse(worker.read_text(), filename=str(worker))
json.loads(Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/mamba_snapshot_semantics_config.json').read_text())
print('Python syntax and JSON parse: PASS')
PY
```

Observed: all exit0. Help renders without CUDA imports; config emits `status=CPU_CONFIG_PASS`, `cuda_semantics=UNVERIFIED`, checkpoint grid64 and no failed checks; syntax/JSON parsing PASS.

PRIMARY independently reran the config-validation command: exit0, `CPU_CONFIG_PASS`, `cuda_semantics=UNVERIFIED`, grid64, no failed checks. PRIMARY inspected the worker's direct `TritonGDNKernel.extend` calls, deferred tensor inspection and existing `_worker_environment` cache placement (`TRITON_CACHE_DIR=<local>/triton`). This remains CPU/source acceptance, not a CUDA result.

Exact extended config-validation command:

```bash
PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import ast, copy, json, platform, sys, tempfile
from pathlib import Path
from tests.manual.agent_opd.probe_mamba_fp32_snapshots import _load_config
worker = Path('tests/manual/agent_opd/probe_mamba_fp32_snapshots.py')
ast.parse(worker.read_text(), filename=str(worker))
path = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/mamba_snapshot_semantics_config.json').resolve()
config, formal, formal_path, grid = _load_config(path)
assert grid == 64
assert not any(name == 'torch' or name == 'triton' or name.startswith('sglang') for name in sys.modules)
mutations = {
    'wrong_qkv_dtype': {'qkv_dtype': 'float32'},
    'wrong_temporal_dtype': {'state_dtype': 'bfloat16'},
    'wrong_backend': {'backend': 'cpu'},
    'varlen_gpu_read_path': {'layout': 'variable_length'},
    'invalid_state_slot': {'cache_indices': [4, 0, -1]},
    'duplicate_state_slot': {'cache_indices': [0, 0, -1]},
    'missing_interior_boundary': {'boundary_tokens': [64]},
    'off_grid_boundary': {'boundary_tokens': [64, 127]},
    'boundary_not_interior': {'sequence_lengths': [128]},
    'padded_row_selected': {'track_chunk_indices': [[1, 2, 1], [2, 1, -1]]},
    'unknown_selected_boundary': {'track_chunk_indices': [[1, 3, -1], [2, 1, -1]]},
    'unknown_prefix_coverage': {'track_chunk_indices': [[1, 1, -1]]},
    'unsupported_key_dim': {'key_dim': 257},
    'wrong_gpu_count': {'visible_gpus': 2},
}
root = Path(tempfile.mkdtemp(prefix='snapshot-config-', dir='/data/ycfeng/tmp/opencode-v2-tmp/opencode'))
for name, update in mutations.items():
    invalid = copy.deepcopy(config)
    invalid.update(update, formal_config=str(formal_path))
    target = root / f'{name}.json'
    target.write_text(json.dumps(invalid))
    try:
        _load_config(target)
    except ValueError as error:
        print(f'{name}: REJECTED: {error}')
    else:
        raise AssertionError(f'Invalid configuration accepted: {name}')
module = ast.parse(worker.read_text())
producer = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == '_produce')
for node in ast.walk(producer):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        assert node.func.attr not in {'cpu', 'item', 'tolist', 'synchronize', 'wait'}, ast.unparse(node)
print(f'PASS: syntax, valid config, {len(mutations)} invalid config rejections, stdlib-only imports, no producer content-read/sync calls; Python {platform.python_version()}')
print(f'Temporary config evidence: {root}')
PY
```

Observed: exit0; all14 invalid configurations rejected with original `ValueError` messages. Final output: `PASS: syntax, valid config, 14 invalid config rejections, stdlib-only imports, no producer content-read/sync calls; Python 3.12.13`. Temporary inputs: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/snapshot-config-8bh53wsn`. This structural inspection does not claim native runtime synchronization behavior or CUDA validation.

Final help/config commands above were rerun after the evidence corrections: both exit0 with the same CPU-only results. Scoped whitespace commands:

```bash
git diff --no-index --check /dev/null tests/manual/agent_opd/probe_mamba_fp32_snapshots.py
git diff --no-index --check /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/mamba_snapshot_semantics_config.json
git diff --no-index --check /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_snapshot_semantics.md
```

All produced no whitespace diagnostics; exit1 denotes new-file differences under `--no-index`, not whitespace failures.

Preparation inspection corrected two worker-only evidence hazards before final CPU validation: write `verdict.json` only inside a fresh output directory created by this invocation, and represent nonfinite comparison errors as undefined while failing the check. Neither correction changes native arithmetic or suppresses a failure into PASS.

## PRIMARY worker argv and evidence

PRIMARY alone submits/executes on one dedicated H800 using the actual formal pinned image, local mount and existing CUDA compatibility environment. Do not execute this worker in a serving container or substitute host Python/version metadata. The source preparer requires writable native source before any attention import.

```bash
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.probe_mamba_fp32_snapshots --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/mamba_snapshot_semantics_config.json --image "$IMAGE" --output-dir "/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/snapshot-semantics-20261111/$KUBEBRAIN_RJOB_NAME"
```

The worker reuses `_worker_environment` for fresh worker-local compilation caches, only after source qualification. It preserves inherited native `SGLANG_*`, CUDA and `NCCL_*` inputs; it does not add tuning or compatibility flags. The actual primary-owned launch receipt must supply/confirm image and mount/environment provenance; reading formal configuration is not independent proof of the platform's mount or image identity.

It emits one JSON verdict on stdout and retains the same `verdict.json` under the supplied task evidence directory, with failed check names and original exceptions/tracebacks/subprocess outputs. Source receipts and exact candidate bytes stay under `source_preflight/` there. Raw small CPU tensors are initially saved at `<formal worker_local_root>/mamba-snapshots-<job>/tensors.pt`; compiled binaries stay in the sibling worker-local `triton/` cache. They are not copied to cloud storage. No cleanup or platform control is performed by the worker. On failure it exits1, but this independent probe is not called by or connected to training.

PRIMARY must record actual job/hardware/terminal state and inspect numerical verdicts before claiming CUDA acceptance. Operator PASS alone cannot release full-model warm probability, donor/runtime, race, throughput or formal04/05 requirements.

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Native ABI inspection | PASS | C3 signatures and inplace FP32 final-state contract inspected. |
| Minimal worker/config | PASS | Only the three owned deliverables; no source or formal-config edits. |
| CPU readiness/report | PASS | Syntax/help/config and14 rejection checks pass. |
| This agent's GPU execution | SKIPPED | Explicitly prohibited; PRIMARY owns H800 execution. |
| Actual CUDA semantics | TODO | No GPU evidence or numeric result yet. |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** Delegated task start through CPU preparation｜**当前前沿：** PRIMARY isolated H800 operator execution in parallel with probability probes.

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | Small native verification was explicitly required; no extra framework/test suite. |
| D2 细节反复重试 | CLEAR | No repeated native fixes or GPU attempts. |
| D3 支线问题修补 | CLEAR | Worker/config/report only; no unrelated fix. |
| D4 可并行任务停滞 | CLEAR | PRIMARY probability probes remain independent; this agent performs no platform work. |
| D5 超范围镀金 | CLEAR | Existing native operator and prefix oracle only. |
| D6 分析空转 | CLEAR | ABI inspection produced executable worker and fixed inputs. |
| D7 路线违背 | CLEAR | CPU-only preparation; no training/policy/source-owner edits. |

**文档检查：** S1–S4/S6 show no scoped defect. S5: parent current-phase text still describes candidate review as pending, while this explicit assignment records `d7e7e301` reviewed on both axes; this agent does not own those records and does not infer CUDA acceptance from either status.
**归因：** 无执行偏离。

## 3. 纠正建议

**分支：** B：PRIMARY synchronizes the already-completed review status; no scope or acceptance change.

**文档更新（先执行）：**
1. PRIMARY-owned `plan.md` current frontier / `progress.md` current execution / requirements phase: distinguish completed `d7e7e301` source review from pending deployed-source/CUDA/probability evidence（可直接执行；本agent不编辑）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. PRIMARY executes this worker → actual source/hardware receipt, exact numeric checks and original failures retained.
2. 并行：existing A/B probability probes → corresponding cold-reference evidence; preserve formal hold and scientific inputs until required verification.

## 4. 最值得关注的 3 点

1. CPU_CONFIG_PASS is not CUDA compilation or semantics acceptance.
2. Native FP32 prefix final states, not rounded BF16 `h`, are the snapshot oracle.
3. Equal-length isolated execution cannot certify live varlen scheduling, donor mapping, races or full-model warm probabilities.
