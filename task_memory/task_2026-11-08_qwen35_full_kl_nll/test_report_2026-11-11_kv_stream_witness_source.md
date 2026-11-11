## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record Source590 qualification and the reproduced missing forward-batch accessor; stop before implementing an unsupported witness. |

# Native KV stream witness source prerequisite

TaskID: `profile-native-kv-stream-witness-source-20261111`.

**Outcome: BLOCKED before native edits.** The required
`get_forward_context().forward_batch` accessor does not exist in the complete
pinned Source590 package. The selected-FP32 and existing CPU-metadata preparers
do not add it. Implementing that accessor would add a native context field and
change publication behavior, which the assignment does not authorize. No
replacement receiver, inferred RID, getter-owner fallback, or partial unbound
witness was implemented.

Only this owned report is delivered. `tests/manual/agent_opd/sglang_kv_streams.py`
and `tests/fast/test_sglang_kv_streams.py` were intentionally not created. There
is no usable `prepare_source` implementation, prepared native diff, or GREEN
witness acceptance result. The integration must not enable the flag/import
until the prerequisite and implementation are resolved.

## Qualified source and decisive evidence

The root used exclusively for read-only qualification was:

```text
task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source/
```

- Manifest: adjacent `source.json`, SHA256
  `73d0248a245878a5c1acb9a2f48a42ce4b170725b8839514a8b350fdd537b7cf`.
- Image: `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`.
- Retained versions: SGLang `0.5.24.dev80+g056f871`, `apache-tvm-ffi=0.1.11`.
  These are retained source identities, not imported host package versions.
- All 5,501 hashes and byte counts pass: 79,478,292 bytes, including 12 Cython
  files. All 5,501 hashes remain unchanged after the CPU reproduction.
- All 15 files required by the metadata owner's manifest match their expected
  pristine/selected-FP32 identities. The owner rewrites were derived and Python
  compiled in memory, not rerun on or written into retained source.

All paths below are relative to that root:

| Evidence | Observation |
| --- | --- |
| `srt/model_executor/forward_context.py:39-47` | Frozen, slotted `ForwardContext` fields are only `attn_backend` and `moe_num_token_non_padded`; no `forward_batch`. |
| `srt/model_executor/forward_context.py:85-99` | The `forward_batch` argument only publishes its bound `moe_num_token_non_padded` getter using `dataclasses.replace`. |
| `srt/model_executor/model_runner.py:1989-2007` | Actual `_forward_raw` publishes through that context manager; passing `forward_batch` is not equivalent to retaining a batch field. |
| `srt/model_executor/model_runner.py:998-1006` | The actual allocator becomes `self.token_to_kv_pool_allocator` from the configurator result. This existing site is suitable for a later CPU class receipt; it already receives the metadata overlay in other methods. |
| `srt/model_executor/model_runner_components/kv_pool_runtime.py:59-216` | This module contains post-capture resizing, not the allocation creation/publication site requested as a preference. |
| `kernels/jit/csrc/elementwise/kvcache.cuh:89-96,151,180-181` | Native `run` returns `void`; an empty batch exits without launching; normal launch uses `LaunchKernel(..., device).enable_pdl(kUsePDL)`. |
| `kernels/jit/include/sgl_kernel/utils.cuh:397-418,474,493` | Existing resolver and raw-stream constructor can support a future in-call stream scalar without a new launcher API. No scalar patch was made or compiled. |
| `kernels/ops/kvcache/kvcache.py:69-82,112-120` | Python custom-op contract is `-> None`; its current body discards the native return. No API-contract change was attempted. |
| `srt/mem_cache/memory_pool.py:3377-3390,3412-3421` | CUDA prefix-valid terminals use separate Triton implementations, not the CPP store. A CPP-only hook cannot claim their actual launch coverage. |

Decisive source hashes:

```text
srt/model_executor/forward_context.py e612cb6399e58a1c01d7ce72e5309148edbb4b0d28eccc053489c6cc5c6b3852
srt/model_executor/model_runner.py 0109f0d51947a646c643f1c56b55a7a0ef2638eaf20203159884588f8be7f4f3
srt/model_executor/model_runner_components/kv_pool_runtime.py 5e20b0e7fe9850f8545f8609b546c114842f314542b0fb167664ca90694c8082
srt/mem_cache/memory_pool.py e077773e25c02be4dc597741e5f987375a221e595bccf92997dea684d5445a26
kernels/ops/kvcache/kvcache.py fe75ca2abad09ee4911f1049f1c054d93f0470578f2a3e234452d19980e0ad81
kernels/jit/csrc/elementwise/kvcache.cuh 8b4cc36204b5623608c2467974bcd2a8daf283e96cdbd2f7ee268b07fa0f12e6
kernels/jit/include/sgl_kernel/utils.cuh 18b0bb2e27dccc20d7509e8b6b6c16e2b57a5ce98be648865fb75059be8a13db
tvm_ffi/cython/function.pxi 40fba9880817d3b013e8978146491110434bd8b36d3a702ff4a93a230ff1c021
```

## CPU verification

Environment: local Linux host, repository workdir
`/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`, system
`python3` **3.10.6**, no conda environment activated. No Torch/SGLang runtime
imports, platform/auth operations, GPU/delegation, native source writes,
device-value reads, or preparer calls were performed. The only imported project
modules were the existing standard-library source preparers.

The second focused command below followed an initial read-only manifest/AST
check. It reproduces the actual publication shape, including a supplied batch
and its bound getter; it does not merely inspect a context created without a
batch. The output expression includes existing manifest inventories; those
inventories are not new validation results.

```bash
python3 -B - <<'PY'
import ast, hashlib, json, platform
from pathlib import Path
from types import SimpleNamespace
from tests.manual.agent_opd import sglang_mamba_runtime_metadata as metadata
from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots
base = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437')
root = base / 'source'
manifest = json.loads((base / 'source.json').read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
before = {}
for entry in manifest['files']:
    b = (root / entry['path']).read_bytes()
    assert len(b) == entry['bytes'] and sha(b) == entry['sha256'], entry['path']
    before[entry['path']] = sha(b)
owner = metadata.source_manifest()
for relative, identity in owner['files'].items():
    raw = (root / relative).read_bytes()
    expected = snapshots.source_manifest()['files'].get(relative, {}).get('before_sha256', identity['before_sha256'])
    assert sha(raw) == expected, relative
    selected = snapshots._rewrite(relative, raw)
    assert sha(selected) == identity['before_sha256'], relative
    compile(metadata._rewrite(relative, selected), relative, 'exec')
relative = 'srt/model_executor/forward_context.py'
assert relative not in metadata._EDITS and relative not in snapshots._EDITS
namespace = {}
exec(compile((root / relative).read_bytes(), relative, 'exec'), namespace)
class Batch:
    rids = ['native-request']
    extend_prefix_lens_cpu = [90112]
    extend_seq_lens_cpu = [8192]
    def moe_num_token_non_padded(self):
        return None
batch = Batch()
ctx = namespace['ForwardContext'](attn_backend=object())
with namespace['forward_context'](ctx, forward_batch=batch):
    active = namespace['get_forward_context']()
    assert active.moe_num_token_non_padded.__self__ is batch
    try:
        active.forward_batch
    except AttributeError as error:
        print('RID_ACCESSOR_RED:', repr(error))
    else:
        raise AssertionError('Unqualified accessor unexpectedly succeeded')
assert namespace['_current'] is None
for path, digest in before.items():
    assert sha((root / path).read_bytes()) == digest, path
print(json.dumps({'python': platform.python_version(), 'manifest_checks': len(before), 'retained_source_unchanged_checks': len(before), 'metadata_owner_binding_checks':len(owner['files']), 'cython_files':sum(Path(x).suffix in ('.pyx','.pxi','.pxd') for x in before), 'native_patch_diff_bytes':0, 'sglang':manifest['sglang_version'], 'other_manifest_keys':{k:v for k,v in manifest.items() if k not in ('files','extensions','image','package')}}, indent=2))
for path in (relative, 'srt/model_executor/model_runner.py', 'srt/model_executor/model_runner_components/kv_pool_runtime.py', 'srt/mem_cache/memory_pool.py', 'kernels/ops/kvcache/kvcache.py', 'kernels/jit/csrc/elementwise/kvcache.cuh', 'kernels/jit/include/sgl_kernel/utils.cuh', 'tvm_ffi/cython/function.pxi'):
    print(path, before[path])
PY
```

Observed decisive output:

```text
RID_ACCESSOR_RED: AttributeError("'ForwardContext' object has no attribute 'forward_batch'")
python: 3.10.6
manifest_checks: 5501
retained_source_unchanged_checks: 5501
metadata_owner_binding_checks: 15
cython_files: 12
native_patch_diff_bytes: 0
```

| Check | Expectation | Actual | Verdict |
| --- | --- | --- | --- |
| Complete retained source binding | All manifest SHA256 and byte counts equal | 5,501/5,501, zero mismatches | PASS |
| Prior preparer identity compatibility | Existing owner identities match; derive without writes | 15/15 Python sources compiled in memory | PASS |
| Required RID accessor | Actual published context has `forward_batch` | Reproduced `AttributeError` | FAIL / BLOCKER |
| Native context restoration | Original manager restores previous context | `_current is None` after exit | PASS |
| Retained source preservation | No changed hashes | 5,501/5,501 unchanged | PASS |
| Prepared witness/CPP ABI/actual streams/allocator class | Actual implementation and native verification | Not attempted after prerequisite failure | UNVERIFIED |

These are direct CPU source checks, not a pytest suite or CUDA binding proof.
The report's single fenced shell command was extracted and replayed through
`subprocess.run(['zsh', '-c', command], timeout=60)`: PASS, with all five decisive
output markers checked. Report trailing-whitespace and absent preparer/test
stub checks also passed. Scoped Git whitespace check:
`git diff --cached --check -- task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_stream_witness_source.md`.
No real allocator instance or stream was observed; no all-16 score vectors were
run. Native compilation, selected Torch CAPI execution, PDL completion, physical
KV values/lifetime, all-TP coverage, numerical parity, and formal readiness
remain UNVERIFIED. Native patch diff size is **0 bytes**; no fabricated
`before/after/source_manifest/preflight` witness archive is claimed.

## Scoped progress checkpoint

### 1. 规划完成情况

**汇总：** PASS 1｜BLOCKED 1｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Complete Source590 and existing overlay qualification | PASS | 5,501 file identities and 15 owner-derived sources checked. |
| Specified source-only witness implementation | BLOCKED | Required forward-batch accessor is absent in qualified source. |
| Focused witness GREEN checks and three-file implementation commit | TODO | No unsupported implementation or test stub was created. |

### 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** This assignment start to reproduced prerequisite failure｜**当前前沿：** Resolve RID publication prerequisite for D40 tickets04/05.

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | Only prerequisite source checks; no harness expansion. |
| D2 细节反复重试 | CLEAR | Initial AST check followed by exact publication reproduction, not workaround retries. |
| D3 支线问题修补 | CLEAR | Missing RID publication directly blocks the assigned witness. |
| D4 可并行任务停滞 | NO DATA | Parent coordination is outside this subagent's ownership; no delegation allowed. |
| D5 超范围镀金 | CLEAR | No alternate API, receiver, fallback, or partial witness was added. |
| D6 分析空转 | CLEAR | Investigation changed disposition to a concrete blocker and stopped implementation. |
| D7 路线违背 | CLEAR | CPU-only work, zero native edits, no platform/GPU operations. |

**文档检查：** S5 `design_kv_coherence_measurement.md:40` contradicts qualified `forward_context.py:39-47,85-99`; the claimed batch accessor is absent. S3 fixed assignment requires that absent accessor while disallowing a new native API or substitute. S1/S2/S4/S6: no further defect established in this scoped assignment.
**归因：** 无 execution drift; source/design premise must be corrected.

### 3. 纠正建议

**分支：** B：spec/tickets 存在缺陷，先更新文档再继续。

**文档更新（先执行）：**
1. Parent-owned `design_kv_coherence_measurement.md:40`: replace the claimed existing accessor with this verified missing-field blocker; preserve the other measured CPU host-field facts（可直接执行 by parent; outside this agent's ownership）.
2. Assignment RID seam: explicitly authorize minimal per-call batch-field publication through the existing frozen context, or provide a different hash-qualified existing accessor（需用户确认 / parent scope decision; no change made）.

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Resolve the concrete publication prerequisite before implementing the witness; done means an authorized, source-qualified actual CPU RID/length path, not inferred identity.
2. Then prepare the reversible CPP scalar/None-wrapper and actual allocator receipt, covering both prefix-valid terminals; native execution remains owned by the parent under D39.

### 4. 最值得关注的 3 点

1. The required RID accessor fails on actual qualified context publication, even with a batch supplied.
2. Full source identity and existing overlays are compatible; the blocker is not an incomplete old snapshot.
3. No witness implementation, native stream/allocator observation, payload capture, GPU run, or formal release is accepted.
