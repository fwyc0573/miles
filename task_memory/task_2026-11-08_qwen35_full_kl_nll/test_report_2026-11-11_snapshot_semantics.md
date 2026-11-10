## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Prepare the isolated native CUDA worker and operator-input config; verify syntax/help/config only. GPU semantics remain UNVERIFIED for PRIMARY execution. |
| 2026-11-11 | Primary independently validated the operator config and inspected native calls/cache placement before freezing the worker for H800 execution. |
| 2026-11-11 | Submit one independent H800 operator worker; deployed source, compilation and numerical verdict remain pending. |
| 2026-11-11 | Verify PRIMARY's actual1-H800 operator run:44/44 CUDA checks PASS, eight exact native-prefix snapshots, qualified source hashes and terminal identity. Full-model warm probability remains FAILED; update the milestone checkpoint without releasing formal runs. |

# Native selected-FP32 snapshot semantics — actual CUDA PASS

TaskID: `profile-native-snapshot-semantics-20261111`.

**Result: actual operator CUDA PASS — PRIMARY's `exp-1111-055011-398371` Succeeded on one H800;44/44 checks PASS, eight selected snapshots exactly match native FP32 prefix final states.** Both full-model A/B probes have since Succeeded but their warm probability acceptance FAILED, as reported in PRIMARY's follow-up. This operator result does not complete RCA or release formal04/05.

**Preparation history:** the initial delegated phase delivered a CPU-ready worker and honestly left GPU semantics UNVERIFIED. PRIMARY subsequently submitted and executed the actual H800 run. This subagent performed no platform/authentication/SSH/GPU/delegation or dependency operation in either phase; this follow-up inspects retained receipts and updates/commits only this report. Historical CPU checks below remain preparation evidence, not the source of the new CUDA verdict.

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

Each numerical comparison records absolute error, relative error only where its reference is nonzero, zero-reference element counts and zero-reference absolute error. Relative error at zero is undefined; nonfinite values fail and their errors are marked undefined rather than serialized as NaN/Infinity. Actual dtype/shape/stride, native signatures, supplied arguments and runtime environment are retained. The actual measurements are recorded below; the original CPU-only checkpoint did not measure them.

## Historical CPU preparation verification

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

PRIMARY executed one dedicated H800 worker using the formal pinned image, local mount and existing CUDA compatibility environment. The exact executed wrapper is the `command` field in [worker-command-r1.json](evidence/snapshot-semantics-20261111/worker-command-r1.json), identical to `admission-r1.json.worker_command`:

```bash
bash -lc 'export PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image
export LD_LIBRARY_PATH=/usr/local/cuda-13.0/compat"${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
destination=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/snapshot-semantics-20261111/"$KUBEBRAIN_RJOB_NAME"
exec timeout --signal=TERM --kill-after=90s 3600s /opt/sglang/bin/python3 -u -B -m tests.manual.agent_opd.probe_mamba_fp32_snapshots --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/mamba_snapshot_semantics_config.json --image artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805 --output-dir "$destination" > /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/snapshot-semantics-20261111/worker-r1.log 2>&1'
```

The worker reuses `_worker_environment` for fresh worker-local compilation caches, only after source qualification. It preserves inherited native `SGLANG_*`, CUDA and `NCCL_*` inputs; it does not add tuning or compatibility flags. The actual primary-owned launch receipt must supply/confirm image and mount/environment provenance; reading formal configuration is not independent proof of the platform's mount or image identity.

It emits one JSON verdict on stdout and retains the same `verdict.json` under the supplied task evidence directory, with failed check names and original exceptions/tracebacks/subprocess outputs. Source receipts and exact candidate bytes stay under `source_preflight/` there. Raw small CPU tensors are initially saved at `<formal worker_local_root>/mamba-snapshots-<job>/tensors.pt`; compiled binaries stay in the sibling worker-local `triton/` cache. They are not copied to cloud storage. No cleanup or platform control is performed by the worker. On failure it exits1, but this independent probe is not called by or connected to training.

Operator PASS alone cannot release full-model warm probability, live donor/runtime, race, throughput or formal04/05 requirements.

**Historical submission checkpoint:** PRIMARY submitted `exp-1111-055011-398371`, creator `i-fengyicheng`, non-preemptible1H800/codesign through the personal `RJobBackend`. CPU/memory were8/64GB, derived from one formal teacher GPU share. The worker budget was3600s plus90s termination grace; the outer launcher had no timeout. Admission recorded82 committed personal H800 and no personal ceiling. That admission snapshot alone was not allocation, hardware, source or numeric proof; the terminal/runtime evidence below now supplies those observations.

## Actual H800 operator results

### Receipts and native identity

Evidence root: `evidence/snapshot-semantics-20261111/` in this task directory.

- [terminal-r1.json](evidence/snapshot-semantics-20261111/terminal-r1.json): job and its single replica Succeeded; container Completed, exit0, restart0, host `gpu-h800-0346.host.platform.shaipower.com`. Container timestamps are `2026-11-10T21:57:30Z`–`21:57:55Z`: **25seconds container lifetime**, not isolated kernel time or throughput. Platform job finish was `21:57:58Z`.
- [admission-r1.json](evidence/snapshot-semantics-20261111/admission-r1.json) and terminal replica agree on source mount `100.96.128.195:/data/ycfeng:/data/ycfeng`. Requested image, terminal container `imageID`, runtime formal image and source-preflight image all equal the exact `165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805` digest above.
- [Actual raw verdict](evidence/snapshot-semantics-20261111/exp-1111-055011-398371/verdict.json): `status=PASS`, `cuda_semantics=PASS`, all44 checks `passed=true`, `failed_checks=[]`, and no exception field. [native-verification.json](evidence/snapshot-semantics-20261111/native-verification.json) is a derived summary; this report independently recomputed its counts and maxima from the raw verdict, rather than accepting the summary alone.
- Actual `/opt/sglang/bin/python3`: Python3.12.16, Torch2.14.1+cu130, CUDA13.0, Triton3.8.0, SGLang `0.5.24.dev80+g056f871`. `nvidia-smi --query-gpu=name,uuid,memory.total,driver_version --format=csv,noheader,nounits` returned one NVIDIA H800, UUID `GPU-fcfb3306-0531-fdb4-7758-95949804ce8f`,81559MiB, driver570.124.06; device capability `[9,0]`. `CUDA_VISIBLE_DEVICES` was null; actual hardware is established by the successful one-GPU worker and device receipt, not an environment label.
- Actual backend: `sglang.srt.layers.attention.linear.kernels.gdn_triton.TritonGDNKernel`; snapshot capability true. Runtime signatures include both selected-snapshot kwargs; chunk size and configured prefill grid both64. Arguments were `query_start_loc=None`, `inplace_update=True`, `head_first=False`, Q/K native L2 normalization true, scale `0.08838834764831845`.

Source-preflight files live at `exp-1111-055011-398371/source_preflight/` under that root. The single `preflight.jsonl` receipt exactly equals `verdict.source_preflight`; all12 before/after archived source files were read and SHA256-recomputed against the six qualified identities. The diff changes exactly the existing two forwarding files; the recurrence, base, GDN backend and hybrid backend remain byte-identical. `selected_fp32=true`, `patch_applied=true`, source path `/sgl-workspace/sglang/python/sglang`. The preflight receipt's own `cuda_semantics=UNVERIFIED` is intentionally retained: it preceded execution and is not the final operator verdict.

| Modified native source | Verified deployed after SHA256 |
| --- | --- |
| `kernels/ops/attention/fla/chunk.py` | `b2c1cd76ab3558b893e082f07a8c587520e624e9988d19c0c1afa4f32a72e43c` |
| `srt/layers/attention/linear/kernels/gdn_triton.py` | `7060585d86347561a2caf36492163b584152e32efddea17b5b4cc8c33c5774bf` |

The complete six before/after hashes remain in `source_manifest.json` and the raw receipt, rather than being duplicated here. Recorded `SGLANG_IMAGE_TAG=lmsysorg/sglang:v0.5.23` and build labels are environment labels, not the inspected installed distribution identity. Actual `LD_LIBRARY_PATH` starts with `/usr/local/cuda-13.0/compat`; platform `NCCL_*` values are retained in `verdict.runtime.environment`. Temporary and compilation paths are worker-local under `/var/tmp/mamba-snapshots-exp-1111-055011-398371/{tmp,triton,inductor,cuda,torch-extensions}`. The cubin list contains12 entries, including two `chunk_gated_delta_rule_fwd_kernel_h_blockdim64.cubin` binaries; binaries were not reopened locally in this reporting phase.

### Measurements versus expectations

| Check group | Expected / actual | Result |
| --- | --- | --- |
| Ordinary and return contracts | 2 ordinary +4 tracked-return checks; BF16 output/h, FP32 pool and native `(o,None,h)` binding retained | PASS6/6 |
| Tracking off/on ordinary output, h and final pool | Exact finite unchanged values; actual12 comparisons each have absolute and defined-relative error0 | PASS12/12 |
| Selected interior snapshots versus native prefix final state | Eight FP32 snapshots, each65536 elements, for boundaries64/128 and batch rows0/1; all finite/exact, absolute and defined-relative error0 | PASS8/8 |
| Snapshot rounded once to BF16 versus ordinary h | Eight finite/exact comparisons at the same chunk entry; absolute and defined-relative error0 | PASS8/8 |
| `-1` snapshot skip row | Batch row2/state slot-1/track index-1 retains sentinel-999 in all four tracked forwards | PASS4/4 |
| Unused pool slots | Slots1/3 unchanged,131072 elements per length; absolute and defined-relative error0 | PASS2/2 |
| Padded row's initial ordinary h | Row2's first65536-element chunk state is all zero for both lengths; absolute error0, relative error undefined for every element | PASS2/2 |
| FP32 store distinct from BF16 round-trip | At least one selected element must retain extra precision; actual524283/524288 differ | PASS1/1 |
| Actual native CUDA compilation | Fresh worker-local cache produces native CUDA binaries; actual12 cubins recorded | PASS1/1 |

Diagnostic FP32 snapshot versus BF16 `h` cast back to FP32 has maximum absolute difference **0.0039055347442626953** and maximum defined relative difference **0.0039061307907104492** across the eight selected rows. These nonzero differences demonstrate retained accumulator precision, **not native-prefix error**: the prefix-oracle errors are0. Counts by length/tracking mode are131070,131072,131069,131072, totaling524283; five selected elements happen to equal their BF16 round-trip.

Batch mapping is verified directly from `cases[].tracked[].rows`: row0 selects pool slot2, row1 selects slot0; positions `[1,2,-1]` then `[2,1,-1]` select both64/128 boundaries for both live rows at each sequence length. It does not exercise live varlen donor mapping. For each unchanged-h comparison,65536 reference elements are zero; the reported relative maximum0 applies only to the nonzero elements, while zero-reference absolute error is0. For padded all-zero initial-h checks the relative maximum is null, not0. Selected-prefix comparisons have no zero reference elements.

Recorded tensors are all on `cuda:0`, with contiguous operator-input layouts:

| Tensor | dtype / shape | stride for T=192 / T=193 |
| --- | --- | --- |
| Q/K | BF16 `[3,T,2,128]` | `[49152,256,128,1]` / `[49408,256,128,1]` |
| V/output | BF16 `[3,T,4,128]` | `[98304,512,128,1]` / `[98816,512,128,1]` |
| g/beta | FP32 `[3,T,4]` | `[768,4,1]` / `[772,4,1]` |
| Ordinary h | BF16 `[3,3,4,128,128]` / `[3,4,4,128,128]` | `[196608,65536,16384,128,1]` / `[262144,65536,16384,128,1]` |
| Final pool | FP32 `[4,4,128,128]` | `[65536,16384,128,1]` for both |
| Selected buffer | FP32 `[3,4,128,128]` | `[65536,16384,128,1]` for both |
| Cache/track indices | int32 `[3]` | `[1]` for both |

Raw verdict flags `all_producer_forwards_ended=true` and `end_phase_synchronization_completed=true` agree with the worker's producer-then-end-inspection sequence. No producer-path tensor-content read or new synchronization was introduced. This reports the exercised isolated test ordering, not race exclusion or a measurement of native autotuner synchronization.

**Exactness limit:** worker comparison records exact numerical equality after FP64 conversion, plus unchanged tensor dtype/layout contracts. It does not record a separate bytewise/sign-bit comparison. The retained raw tensors are reported at `/var/tmp/mamba-snapshots-exp-1111-055011-398371/tensors.pt`; this CPU reporting phase did not reopen them or independently prove bitwise equality. No raw tensor arrays or large sources were copied into the report.

### Remaining acceptance boundary

This is the **same qualified candidate with tracking off/on**, not untouched original-code GPU A/B. It verifies equal-length operator stores and configured row mapping only: no live varlen scheduler/donor provenance, races, full-model warm correctness, historical cause or throughput acceptance. It uses no custom recurrence, invented tolerance, fallback or skips into PASS. PRIMARY's follow-up states both A/B full-model jobs Succeeded while **warm probability FAILED**; this report neither reruns nor certifies those separate probability measurements. RCA remains incomplete and formal04/05 remain blocked. No worker verdict is connected to training control.

### Local receipt verification

The report-only follow-up used `/usr/bin/python3 -B`, Python3.10.6, with standard-library reads only. Comprehensive verification passed: all raw check groups, eight selected rows and mapping, exact prefix/rounding errors, zero-reference semantics,12 cubins including two recurrence binaries,12 archived source hashes and regenerated exact diff, image/mount/command/terminal identity, and report argv/measurements/checkpoint. No retained evidence or worker tensor was changed or executed.

Reproducible concise receipt check, run from the repository root:

```bash
/usr/bin/python3 -B - <<'PY'
import hashlib, json
from pathlib import Path
from tests.manual.agent_opd.sglang_mamba_snapshots import source_manifest
root = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/snapshot-semantics-20261111')
v = json.loads((root/'exp-1111-055011-398371/verdict.json').read_text())
n = json.loads((root/'native-verification.json').read_text())
assert v['status'] == v['cuda_semantics'] == 'PASS' and v['failed_checks'] == []
assert len(v['checks']) == 44 and all(c['passed'] for c in v['checks'].values())
rows = [r for c in v['cases'] for t in c['tracked'] for r in t['rows'] if 'native_prefix_final_state' in r]
assert len(rows) == 8 and sum(r['native_prefix_final_state']['elements'] for r in rows) == 524288
assert sum(r['unrounded_elements'] for r in rows) == n['fp32_unrounded_elements'] == 524283
assert all(r['native_prefix_final_state']['max_absolute_error'] == r['native_prefix_final_state']['max_relative_error_nonzero_reference'] == 0 for r in rows)
assert max(r['snapshot_vs_bf16_h_cast_to_fp32']['max_absolute_error'] for r in rows) == 0.0039055347442626953
assert max(r['snapshot_vs_bf16_h_cast_to_fp32']['max_relative_error_nonzero_reference'] for r in rows) == 0.0039061307907104492
assert v['all_producer_forwards_ended'] and v['end_phase_synchronization_completed']
assert len(v['compiled_cuda_binaries_worker_local']) == 12
archive = root/'exp-1111-055011-398371/source_preflight'
assert json.loads((archive/'source_manifest.json').read_text()) == source_manifest()
for rel,identity in source_manifest()['files'].items():
    for phase in ('before','after'):
        assert hashlib.sha256((archive/phase/rel).read_bytes()).hexdigest() == identity[phase+'_sha256']
command = json.loads((root/'worker-command-r1.json').read_text())
admission = json.loads((root/'admission-r1.json').read_text())
terminal = json.loads((root/'terminal-r1.json').read_text())
container = terminal['replicas'][0]['containers'][0]
assert command['command'] == admission['worker_command']
assert command['image'] == container['imageID'] == v['source_preflight']['image']
assert terminal['status']['phase'] == 'Succeeded'
assert container['restartCount'] == container['state']['terminated']['exitCode'] == 0
assert container['state']['terminated']['reason'] == 'Completed'
print('PASS: raw44/8 numeric checks,12 source hashes,12 cubins and command/image/terminal identity')
PY
```

Observed: exit0, the expected PASS line. This checks retained operator evidence, not full-model acceptance or a new CUDA run.

## 1. 规划完成情况

**汇总：** PASS 4｜BLOCKED/FAILED/SKIPPED 2｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Native ABI inspection | PASS | C3 signatures and actual runtime forwarding/capability receipt agree. |
| Minimal worker/config | PASS | Existing delivered worker/config unchanged in this follow-up. |
| CPU readiness/report | PASS | Historical CPU checks preserved; actual receipts and all12 archived source hashes rechecked locally. |
| Actual operator CUDA semantics | PASS | PRIMARY Succeeded1H800,44/44 checks, eight exact FP32 native-prefix snapshots. |
| This agent's GPU execution | SKIPPED | Prohibited in both phases; no platform/SSH/GPU/delegation operation. |
| Full-model warm probability | FAILED | PRIMARY follow-up reports both A/B jobs Succeeded but warm probability FAILED; not replaced by operator PASS. |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** Historical preparation checkpoint through actual H800 receipt verification｜**当前前沿：** report-only verification/commit; PRIMARY's unresolved full-model warm probability RCA.

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | Verification stops at retained44 checks, identities and report; no new operator probe/harness. |
| D2 细节反复重试 | CLEAR | No new GPU attempt or parameter retry in this follow-up. |
| D3 支线问题修补 | CLEAR | Only the explicitly owned report is edited. |
| D4 可并行任务停滞 | CLEAR | A/B probes completed independently per PRIMARY; this report does not hold their RCA. |
| D5 超范围镀金 | CLEAR | No source/config change or added experiment; exactness limits remain explicit. |
| D6 分析空转 | CLEAR | Raw counts/maxima/source hashes resolve the report's pending operator milestone. |
| D7 路线违背 | CLEAR | Actual run remains PRIMARY-owned; this phase is read-only evidence verification plus report commit. |

**文档检查：** S1–S4/S6 CLEAR: D40 owns the remaining warm failure; operator and full-model acceptance remain separate, measurable and scoped. S5 corrected in this report: old leading UNVERIFIED/pending-CUDA and checkpoint TODO are replaced by actual operator PASS, preserving preparation history. Inspected parent `requirements.md` current phase, `plan.md` current frontier and `progress.md` current execution still say pending placement/operator-notready despite these receipts; PRIMARY owns their update, outside this report-only authorization.
**归因：** 无执行偏离。

## 3. 纠正建议

**分支：** B：correct stale milestone text without changing scope or acceptance.

**文档更新（先执行）：**
1. This report's outcome/results/checkpoint: actual operator CUDA PASS, qualified source/terminal measurements and unresolved warm failure（可直接执行；已更新）。
2. PRIMARY-owned `requirements.md` current phase / `plan.md` current frontier / `progress.md` current execution: replace pending placement/operator-notready with completed operator verification and failed full-model warm acceptance（可直接执行；本agent不编辑，不阻塞report提交）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Verify retained numeric groups/source bytes/image/terminal/command and scoped diff → commit only this report.
2. PRIMARY continues full-model warm probability RCA against corresponding cold references; operator PASS does not authorize formal release, a tolerance change or another experiment by this agent.

## 4. 最值得关注的 3 点

1. Actual operator44/44 PASS closes this small CUDA milestone; the initial CPU-only evidence remains historical.
2. Exact FP32 native-prefix errors are0;524283/524288 elements differ from BF16 round-trip, without proving separate bytewise equality.
3. A/B full-model warm probability remains FAILED; equal-length operator success proves neither live donor/race correctness nor RCA completion/formal release.
