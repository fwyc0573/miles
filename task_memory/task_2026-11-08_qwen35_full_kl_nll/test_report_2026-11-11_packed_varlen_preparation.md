## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Prepare the existing single-request packed operator diagnostic and A/B configs; verify CPU/source orchestration only, without native execution or changes to accepted equal-length receipts. |
| 2026-11-11 | Correct host-bound fast-test fixtures in R2, retain seven tests and add two-location CLI coverage; rerun only that module, preserving historical32 results and native UNVERIFIED. |

# Packed-varlen differential preparation

TaskID: `profile-native-packed-varlen-differential-preparation-20261111`.

**CPU/source preparation complete; R2 portable fixture tests pass7/7; packed native semantics UNVERIFIED.** Only the affected seven-test module was rerun for this correction. The earlier combined32/32 result remains historical, not new portability or native acceptance. No platform/auth/native/CUDA/GPU/model execution, delegation, staging or commit occurred. Shared task documents and original44 operator receipts are untouched.

## Owned deliverables and source contract

- `tests/manual/agent_opd/probe_mamba_fp32_snapshots.py`: add supported `layout="packed"` to the existing diagnostic. No new CLI flag, recurrence, backend/compiler/dtype change, tolerance, retry or fallback.
- `tests/fast/test_mamba_fp32_snapshot_probe.py`: seven CPU tests with NumPy mock tensors or recorded native Python bindings. No mock is promoted to a native verdict.
- `mamba_snapshot_packed_prefix_{A,B}_config.json`: explicit operator inputs, not captured natural-request values.
- This report and compact [preparation evidence](evidence/packed-varlen-preparation-20261111/preparation.json). No raw inputs, K/V, states or compiled binaries are copied here or to cloud.

Authority: the scoped delegation advances existing D40/H3/H2 only; [requirements](requirements.md), [plan](plan.md#current-frontier), [accepted source structure report](test_report_2026-11-11_kv_coherence_trajectory_source_rca.md), [existing operator report](test_report_2026-11-11_snapshot_semantics.md). Warm/formal/scientific decisions remain unchanged.

Native references use retained C3 at `evidence/native-sglang-cache-source-20261111/exp-1111-042450-358109/source/`:

| Source | Contract |
| --- | --- |
| `kernels/ops/attention/fla/chunk.py:238–251` | `q.shape[0]==1` is the packed storage axis; logical sequence count is `len(cu_seqlens)-1`. It is not a general one-logical-sequence restriction. This diagnostic deliberately owns only one reachable live request. |
| `srt/layers/attention/linear/kernels/gdn_triton.py:169–215` | Native extend passes `query_start_loc` as `cu_seqlens`, indexed FP32 state, default inplace update and native Q/K L2 normalization. |
| `kernels/ops/attention/fla/chunk_delta_h.py:380–398,417–436` | For `[0,T]`, `N=1`, `NT=ceil(T/64)`, `h=(1,NT,Hv,V,K)`, `IS_VARLEN=True`; selected snapshots use the existing kernel. |
| `kernels/ops/attention/fla/chunk_delta_h.py:137–164,188–207` | Selected FP32 state is stored at chunk entry; row113 is the state after7232 input tokens. |
| `kernels/ops/attention/fla/index.py:17–26` | Native index preparation internally calls `.tolist()`. This behavior is retained: no zero-CUDA-wait claim. |

`prepare_source(selected_fp32=True)` and its six pins are unchanged. CPU source checks verify all six before/candidate hashes; two forwarding files keep their already-qualified candidate hashes and four native files remain byte-identical. The old equal-length config, preparer and44-check verdict are unmodified. The original RNG draw order is retained in the extracted `_inputs` function and the equal-length branch still generates each length separately.

## Cases and actual added comparisons

Configs own all workload values: one request, four state slots, cache index`[2]`, BF16 Q/K/V, FP32 state/gates/snapshots, int32 indices, K=V128, Q/K heads4; A value heads12, B8. Outer lengths7253/8192; boundaries7168/7232; tracking cases`[[112],[113]]`; comparison prefix6519. Packed config rejects zero/padded slots, multiple requests, missing outer-length contrast and an out-of-range comparison prefix. The old equal-length >=2 live/nonsequential-slot rule still applies only there.

Packed generation draws Q/K/V/g/beta **once at8192** and slices every full/tracked/own-prefix call from those buffers. Each of the ten producer forwards clones the same initial pool once and supplies a fresh CUDA int32`[0,tokens]`; inplace update remains true. No probe-side producer content read or explicit synchronization is added. All new reductions run in `_inspect_packed`, called by existing `_inspect` only after all producer forwards and the existing end-phase `torch.cuda.synchronize()`.

Exact, finite diagnostic comparisons now execute, rather than only asserting input construction:

1. Every full/tracked/prefix call: non-null CUDA int32 cu-seqlens values/shape and native argument metadata; actual supplied Q/K/V/g/beta versus the corresponding buffer prefix; first native BF16 h row versus the configured initial FP32 slot rounded once. The latter checks initial entry only at BF16 precision; one FP32 pool clone per call is source-verified and CPU-mock-tested.
2. Existing tracking-off/on output, h and final pool comparisons remain. Every selected FP32 snapshot compares against its **own** native prefix final state, including7232 for each outer length, plus unchanged existing snapshot/BF16-rounding checks.
3. Cross7253/8192: actual common Q/K/V/g/beta buffers and initial pool; `core_attn_out` over configured6519 tokens; all114 common h chunk-entry rows; selected FP32 chunk112 and113 buffers. Final states at different outer lengths are not falsely required equal.

Each comparison retains existing absolute/relative error handling: undefined relative error at zero reference is reported separately; nonfinite tensors fail. No actual packed CUDA values/errors have been measured here.

**Causal limit:** synthetic inputs are identical through7253, unlike the two natural requests, which share only `[90112,96631)`=6519 rows. The7232-token reference ending97344 is1693's own prefix, contains713 divergent suffix rows and is invalid as a1695 cached donor. Operator results support only a kernel prediction; they cannot prove actual1693/1695 initial/input/state equality, H1/H4, historical writes or warm cause. H2's specific1695 partial-seed theory remains falsified; no restore/state copy is introduced.

## Initial CPU verification — historical

Environment: Linux, repository worktree; `/usr/bin/python3`3.10.6, NumPy1.24.3 for explicitly mocked tensors; no conda change, package installation or native Torch import. Existing pytest environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`3.12.13, pytest9.1.1. Retained bindings use actual candidate Python definitions but identity decorators, metadata tensors, mock index preparation/intra/output and a recorded Triton launch; no recurrence/compiler/decorator execution.

Exact commands from repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -m unittest tests.fast.test_mamba_fp32_snapshot_probe -v
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_mamba_fp32_snapshot_probe.py tests/fast/test_sglang_mamba_snapshots.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/packed-varlen-prep-20261111-pytest
git diff --check -- tests/manual/agent_opd/probe_mamba_fp32_snapshots.py
```

| Check | Expected / observed | Result |
| --- | --- | --- |
| Python3.10 unit checks | 7/7, no skips; observed0.402s | PASS |
| Combined unchanged source-preparer/new probe tests | 32/32, no skips; observed2.39s, two existing SWIG deprecation warnings | PASS |
| Config CLI | Old config and A/B emit CPU_CONFIG_PASS, cuda_semantics=UNVERIFIED, no failed checks | PASS |
| Invalid cases | Fourteen packed/config mutations rejected; old one-live-row equal-length layout rejected | PASS |
| Packed orchestration, mock only | Six RNG draws total including initial pool; ten distinct state clones, identical shared prefixes; no host reads before mock end synchronization | PASS |
| Numeric comparison wiring, mock only | Full inspector executes own-prefix/unchanged and cross-length checks; changed output/h/chunk113/input/initial values each produce the expected failed comparison | PASS |
| Actual specialization binding, source only | A/B×7253/8192: same non-null int32 cu object reaches native fwd_h launch, IS_VARLEN=True; h114/128 rows; QK4/Hv12 or8/KV128/state slots4/index2; existing native arguments retained | PASS |
| Original equal-length source versus new producer, mock only | 11 identical RNG draws and126 tensor entries byte/shape/dtype/stride equal under the same mock; native RNG values not measured | PASS |
| Existing six source pins/44 receipt | Same six identities; old verdict SHA and44 PASS retained, not a GPU rerun | PASS |
| Scoped whitespace | No diagnostics | PASS |

Source/config RED and GREEN were checked with Python3.10 against frozen original source, not native execution:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
import ast, json, math, subprocess
from pathlib import Path
from tests.fast.test_mamba_fp32_snapshot_probe import _MockTorch, _MockBackend, _MockTensor
from tests.manual.agent_opd import probe_mamba_fp32_snapshots as p
from tests.manual.agent_opd.sglang_mamba_snapshots import source_manifest, _source_versions
T=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
old=subprocess.check_output(['git','show','ec532bc226159dfddb67902bcd299237d96a4300:tests/manual/agent_opd/probe_mamba_fp32_snapshots.py'])
ns={'json':json,'math':math,'Path':Path,'source_manifest':source_manifest}
nodes=[n for n in ast.parse(old).body if isinstance(n,ast.FunctionDef) and n.name in ('_load_config','_produce')]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'old-source-only.py','exec'),ns)
for v in 'AB':
    path=(T/f'mamba_snapshot_packed_prefix_{v}_config.json').resolve()
    try: ns['_load_config'](path)
    except ValueError as e: print(v,'expected source/config RED:',str(e))
    else: raise AssertionError('Original source unexpectedly accepted packed layout')
    assert p._load_config(path)[0]['layout']=='packed'
c=p._load_config((T/'mamba_snapshot_semantics_config.json').resolve())[0]
a,b=_MockTorch(),_MockTorch()
x=ns['_produce'](a,_MockBackend(a,c),c); y=p._produce(b,_MockBackend(b,c),c)
assert a.draws==b.draws
count=0
def same(a,b):
    global count
    if isinstance(a,_MockTensor):
        assert (a.dtype,a.shape,a.stride())==(b.dtype,b.shape,b.stride()) and a.values.tobytes()==b.values.tobytes()
        count+=1
    elif isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a: same(a[k],b[k])
    elif isinstance(a,list):
        assert len(a)==len(b)
        for u,v in zip(a,b): same(u,v)
    else: assert a==b
same(x,y)
_source_versions(T/'evidence/native-sglang-cache-source-20261111/exp-1111-042450-358109/source',True)
print('GREEN: both packed configs; equal-length mock byte entries',count,'RNG draws',len(a.draws),'; six unchanged pins')
PY
```

Expected/actual: A/B old source rejects with `This isolated native ABI probe requires Triton equal-length inputs`; current source accepts both. GREEN prints126 byte-equal mock entries/11 RNG draws and six pins. One initial standalone verification-script failure was `AttributeError: 'dict' object has no attribute 'dtype'`: `hasattr(values)` misclassified dicts. Replacing that script predicate with `isinstance(_MockTensor)` resolved it; neither producer nor native behavior was changed. This is no native RED/causal evidence.

Final verification after the source-binding recorder derived its positions/cache index directly from config: Python3.10 unit checks7/7 in0.332s, no skips. The exact embedded source command above was extracted and executed successfully; producer AST, absence of Torch/Triton/SGLang imports in that CPU check, unchanged preparer bytes and old44 receipt SHA also passed. This does not broaden native acceptance.

## R2 portable CPU fixtures

Primary review found two host dependencies in the new fast test: direct CLI validation read the production formal mount `/data/ycfeng`, and invalid-config fixtures used an explicit host temporary directory. A checkout outside that production mount cannot pass the unchanged guard. This follow-up changes only `tests/fast/test_mamba_fp32_snapshot_probe.py`, this report and its compact evidence/hashes; the production probe, native configs, guards and producer/consumer witness files are not modified.

`_fixture_task` copies the three actual operator config files byte-for-byte. Its cloned formal config changes only `local_mount` and `repo`, locating the fixture repository and configs under one internally consistent temporary mount. Image/model/operator values and all other formal fields remain retained metadata; no native allocation is claimed. Every `TemporaryDirectory` now uses default storage, obeying `TMPDIR` supplied by local commands. The CLI test validates all three configs at **two fixture locations**, asserts unchanged `operator_inputs`, CPU_CONFIG_PASS and native UNVERIFIED, and never skips. The rejection test first verifies that its unmodified cloned config passes, then tests the same fourteen invalid mutations. Seven test methods and their previous numeric/source coverage remain.

The CPU relocation reproducer runs that same seven-test module with its input task moved outside a distinct declared native mount, and rejects any explicit `TemporaryDirectory(dir=...)`. Before correction it produced three CLI subtest failures plus one tempfile failure: two affected methods, other five methods PASS,7 tests in0.191s, no skips. Direct CLI inspection reports the exact unchanged `ValueError: Config and repository must use the formal local mount`. This is a CPU fixture RED, not a native arithmetic RED. An initial wrapper summarized unittest subtest names as `runTest`; mapping `case.test_case` to the parent method corrected only that summary.

Exact affected-module commands:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -m unittest tests.fast.test_mamba_fp32_snapshot_probe -v
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_mamba_fp32_snapshot_probe.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/packed-varlen-portability-r2-20261111-pytest
```

Actual: Python3.10.6/NumPy1.24.3 unittest **7/7 PASS in0.219s**, no skips; Python3.12.13/pytest9.1.1 affected-module pytest **7/7 PASS in0.43s**, no skips, two existing SWIG deprecation warnings. No broad source suite was rerun.

Exact relocation feedback loop, rerun after correction:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
import contextlib, io, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from tests.fast import test_mamba_fp32_snapshot_probe as module
original_task = module._TASK
temporary_directory = tempfile.TemporaryDirectory
with temporary_directory(prefix='packed-portability-repro-') as root:
    root = Path(root)
    relocated = root / 'relocated-checkout' / original_task.name
    relocated.mkdir(parents=True)
    for name in ('mamba_snapshot_semantics_config.json', 'mamba_snapshot_packed_prefix_A_config.json', 'mamba_snapshot_packed_prefix_B_config.json'):
        (relocated / name).write_bytes((original_task / name).read_bytes())
    formal = json.loads((original_task / 'formal_config.json').read_text())
    formal.update(local_mount=str(root / 'native-mount'), repo=str(root / 'native-mount' / 'repo'))
    (relocated / 'formal_config.json').write_text(json.dumps(formal))
    with contextlib.redirect_stdout(io.StringIO()) as captured:
        assert module.probe.main(['--config', str(relocated / 'mamba_snapshot_packed_prefix_A_config.json'), '--validate-config']) == 1
    assert json.loads(captured.getvalue())['exception']['message'] == 'Config and repository must use the formal local mount'
    def portable_temp(*args, **kwargs):
        if kwargs.get('dir') is not None:
            raise AssertionError('Portable CPU fixture must not pass a host-specific TemporaryDirectory dir')
        return temporary_directory(*args, **kwargs)
    with patch.object(module, '_TASK', relocated), patch.object(module.tempfile, 'TemporaryDirectory', portable_temp):
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
    assert result.wasSuccessful() and result.testsRun == 7 and not result.skipped
    print('CPU FIXTURE GREEN: relocated seven-test module passes; no explicit temporary dir; production out-of-mount guard still rejects')
PY
```

Actual: **7/7 PASS in0.252s**, no skips; expected GREEN line printed. For the pre-correction RED run, the final success assertion instead checked parent method names `{test_actual_configs_and_cpu_only_cli, test_packed_rejections_and_old_live_row_constraint}`,7 tests and no skips; the expected RED summary matched. Probe/A/B file hashes still match their pre-correction values.

**Portability limits:** these are local temporary-fixture regressions, not an executed GitHub CI allocation. They remove dependency on the host mount or temporary-directory path while retaining production validation. The retained C3 source-binding test keeps its explicit source-only skip when those untracked sources are absent; CPU CLI/rejection checks do not skip. Prior source/config RED/GREEN, combined32 results, six source pins and native UNVERIFIED remain unchanged. The old frozen R1 review package is not edited; PRIMARY will freeze the corrected R2 package.

## Planned native command, not submitted

Reuse existing dedicated worker plan **per variant**: non-preemptible1H800/codesign, CPU8, memory64GB, existing165ff pinned image/formal local mount/environment;3600s plus90s termination grace, primary launcher remains alive. A/B may run independently under fresh primary resource admission. No model execution is needed by this operator probe.

PRIMARY worker command template; set `variant=A` on the A worker and `variant=B` on the independent B worker:

```bash
export PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image
export LD_LIBRARY_PATH=/usr/local/cuda-13.0/compat"${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
variant=A
task=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll
exec timeout --signal=TERM --kill-after=90s 3600s /opt/sglang/bin/python3 -u -B -m tests.manual.agent_opd.probe_mamba_fp32_snapshots --config "$task/mamba_snapshot_packed_prefix_${variant}_config.json" --image artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805 --output-dir "$task/evidence/packed-varlen-preparation-20261111/native/$variant/$KUBEBRAIN_RJOB_NAME"
```

Fresh verdict and selected-source receipts use those NEW per-variant/job paths. Native tensor evidence remains at the existing worker-local `/var/tmp/mamba-snapshots-<job>/tensors.pt`; compilation caches remain sibling worker-local directories. The existing raw save is not copied/archived elsewhere or turned into a new acceptance gate. Actual hardware/image/creator/mount/terminal identity, compilation and packed numeric results remain PRIMARY's pending native verification.

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Minimal packed producer/configs/comparisons | PASS | Existing probe extended, single-request scope and old RNG preserved. |
| CPU/source preparation | PASS | R2 affected module7/7 and relocation7/7; combined32 remains historical; no native claims. |
| Report/compact evidence/planned command | PASS | Owned paths only; six pins and original44 receipt retained. |
| Delegated native/platform operations | SKIPPED | Explicitly prohibited; nothing submitted. |
| PRIMARY packed numeric/causal acceptance | TODO | Future native results and natural-request values remain missing. |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** R2 scoped test-fixture correction｜**当前前沿：** PRIMARY freezes the corrected review package; native diagnostic and actual-state witness remain independent.

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | Only affected seven-test module rerun; portable fixtures resolve the recorded CI defect. |
| D2 细节反复重试 | CLEAR | Reproduced mount/temp-dir failure, one fixture correction, GREEN; no native workaround. |
| D3 支线问题修补 | CLEAR | Only test/report/evidence files; production guards and witness files untouched. |
| D4 可并行任务停滞 | CLEAR | No new blocking edge; witness/native work remain parent-owned. |
| D5 超范围镀金 | CLEAR | Seven methods retained; one fixture cloning seam, no production options. |
| D6 分析空转 | CLEAR | CPU fixture RED→GREEN and relocation regression delivered. |
| D7 路线违背 | CLEAR | No broad source rerun, production change, raw archive or prohibited execution. |

**文档检查：** S1–S6 CLEAR for this fixture-only correction; report now distinguishes current affected-module results from historical32 checks. Shared task records remain outside this follow-up's ownership.
**归因：** 无执行偏离。

## 3. 纠正建议

**分支：** A：fixture correction and its records are complete; no spec/ticket change.

**需停止的偏离行为：** 无。

**接下去的路线：**
1. PRIMARY freezes the corrected R2 source-review package; original R1 package remains historical. Packed native acceptance stays UNVERIFIED pending the existing bounded execution route.
2. 并行：actual-state-value witness design remains independent; neither result alone proves warm cause or releases formal A/B.

## 4. 最值得关注的 3 点

1. R2 CLI fixtures preserve actual parameters and pass at two locations; production mount guards remain unchanged.
2. Packed native index preparation retains its internal `.tolist()`; all added diagnostic reductions are end-phase only.
3. Own7232-prefix validation cannot make1693's donor valid for1695; only6519 natural input rows are shared.
