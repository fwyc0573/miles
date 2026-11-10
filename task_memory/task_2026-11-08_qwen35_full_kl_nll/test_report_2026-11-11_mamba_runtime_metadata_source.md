## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Clarify per-request versus batch/aggregate identity coverage; no recorder or native source changed. |
| 2026-11-11 | Add source-qualified diagnostic preparation, CPU binding results, receipt limits and scoped progress checkpoint. |

# Mamba runtime metadata source preparation

TaskID: `profile-mamba-live-metadata-source-20261111`.

**Outcome: CPU/source preparation PASS; actual runtime, CUDA completion and warm parity UNVERIFIED.** Only the two assigned Python files and this report are changed. No GPU, platform, authentication, SSH or delegation operation was performed. Formal source/math, configuration, cache policy, intervals, precision, concurrency and scientific criteria are unchanged.

## Deliverables and API

- `tests/manual/agent_opd/sglang_mamba_runtime_metadata.py`
- `tests/fast/test_sglang_mamba_runtime_metadata.py`
- This report.

Frozen API:

```python
prepare_runtime_metadata(
    native_sglang_package_root: Path, *, image: str, archive_dir: Path
) -> dict
```

Call after the existing `sglang_mamba_snapshots.prepare_source(selected_fp32=True)`, before attention imports/server startup. This module imports no SGLang/torch. Image, distribution version and selected-FP32 source identities come from the existing math-patch owner. Fifteen retained native files are qualified before any dependency/archive write; eight existing files receive diagnostic inserts and `srt/mamba_runtime_metadata.py` is created. C1/C2/C3 evidence roots supply the exact files; unrelated C4/C5 synchronization source is not edited. Missing/changed source, unprepared math sources, mismatched image/version, unknown existing recorder and conflicting archives are rejected before dependency writes. Repeating only this API is idempotent. Do not rerun the selected-FP32 preparer against an already instrumented package.

Qualification hashes are owned by `source_manifest()` and the existing snapshot manifest, not independently copied into this report. The native diff contains only recorder imports, CPU tuple appends and one addition to the existing readback Dict. Removing those diagnostic AST nodes restores each complete native AST exactly. Existing tensor indexing/casts/copies, native conditionals, kwargs, returns, allocators, resolvers and cache decisions are preserved.

## Receipt coverage and limits

| Native seam | Receipt and observed locals |
| --- | --- |
| C2 `schedule_batch.py` chosen extend boundary | `scheduler_track_boundary`: actual RID, prefix/extend/end lengths, cache/state chunk sizes, checkpoint grid, chosen mask/boundary/track length and post-choice ping-pong indices. No resolver is called again. |
| C3 hybrid physical translation and CPU-plan binding | `translated_track_metadata` records tensor metadata only. `prefill_track_plan` records the actual returned plan: CPU mask, prefix/extend/track lengths, tracked/final/unaligned/h/recompute rows, h source and chunk indices, chunk size and RIDs. The plan is not rebuilt for diagnostics. |
| C3 GDN allocation and dispatcher | `gdn_snapshot_allocation` records actual mask, h-source metadata, capability, selected kernel, allocated-buffer identity/dtype/shape/stride, temporal metadata, layer and RIDs. `gdn_extend_dispatch` records the actual chosen kernel/arguments without changing them. Buffer object IDs link allocation and dispatch. Optional CPU lengths remain `None` when unavailable. |
| C3 hybrid snapshot copy | `snapshot_store_enqueued` distinguishes the actual `h_track_buf`, per-chunk h, recompute and final-state branches. Actual source/temporal dtypes and source/destination tensor metadata are observed; the existing cast is untouched. No source is labeled FP32 merely because the experiment requested it. |
| C1 Mamba component and C2 runner | Selected COW match and donor skip/prepare carry RID; skipped COW matches record reason/node only. Clear/COW enqueues carry batch RIDs. Finished checkpoint choice or unfinished donation, keep/ping-pong indices, inserted-slot metadata and new/fill-existing/retain-existing node branches are observed without resolving donor returns again. Node commits do not directly carry RID; shared node IDs alone are not request identities. |
| C3 tree overlap and C2 canonical adoption | `duplicate_kv_release_queued` records actual CPU absolute interval/full-only subdivision and node; `kv_allocator_release_returned` follows native allocator calls. Both release kinds are aggregate-only, not request-associated by order or node equality. Checkpoint begin/returned and `canonical_kv_rebind_enqueued` directly carry RID; rebind follows the actual request-row write and records its selected node/interval. NodeIds returned outside TreeCore are recorded directly, not dereferenced as nodes. |
| C2 existing internal-state controller | Add `mamba_runtime_metadata` to the existing Dict, before its unchanged `msgspec_to_builtins` return. No new endpoint, request type or collective. |

The generated recorder accumulates immutable CPU tuples in process memory. Each row is `(sequence, event, ((field, value), ...))`; JSON/msgspec conversion may represent tuples as arrays. Tensor metadata is `(object_id, dtype, shape, stride, device)`. It retains no device tensor references and reads no tensor numeric contents. No new `.item()`, `.cpu()`, `.tolist()`, events, waits, synchronization, collectives, clocks, request-path logging or request-path file I/O is introduced.

Identity joins use native RID/pair, not sequence or request counts. CPU plan rows index the same batch RID list, so `rids[tracked_rows[j]]` identifies plan membership, not physical slot values. Allocation, store, clear and COW carry batch RIDs; dispatch may bind to allocation by a uniquely matching live buffer object ID. A shared node ID cannot identify a request. Tensor object IDs are process-local addresses and may be recycled, so ambiguous object-ID associations must remain unverified rather than selecting a request by chronology. This bounded diagnostic does not add request threading to dispatcher/allocator paths or promise per-request attribution for aggregate release events.

The existing internal-state Dict drain returns process ID, actual published DP/TP/PP/attention ranks, schema and rows, and clears only that process's buffer. The caller must drain after all scoring requests; integration/JSON collection is owned by the integration agent. Existing DP readback does **not** gather all TP shards. `physical_slot_values=UNMEASURED` and `device_store_completion=UNMEASURED` are explicit. Host enqueue/allocator return, object identity and CPU row plans do not prove device completion, physical slot values, donor contents, all-TP coherence, ordering/race exclusion or model probability parity. Synthetic/capture RIDs can be `None`; missing CPU plans are not fabricated.

## CPU validation

Environment: repository root `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`, Linux; `/data/ycfeng/envs/frontier-py310/bin/python`, Python 3.10.6, pytest 9.1.1. No conda activation. Standard-library source preparation and metadata-only tensor stand-ins are used; neither host nor worker SGLang is imported. The pinned distribution version is mocked only in CPU qualification tests, not asserted as the host's installed version. Native source bytes and all expected hashes are real retained evidence. Source-dependent CI cases explicitly skip when evidence is absent instead of using an older host package. The fast CPU file fits the 30-second budget and needs no additional CI declaration.

Exact final test command:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/frontier-py310/bin/python -m pytest \
  --noconftest -p no:cacheprovider -o addopts='' -q \
  tests/fast/test_sglang_mamba_runtime_metadata.py \
  tests/fast/test_sglang_mamba_snapshots.py
```

Expected: all source checks, actual retained Python bindings and diagnostic invariance checks pass without numeric device reads. Actual: **75 PASS / 16.67 seconds** (50 new runtime-metadata cases + 25 existing selected-FP32 cases), no skipped cases. Existing environment warning: `PytestConfigWarning: Unknown config option: asyncio_mode` because this isolated pytest environment does not load pytest-asyncio. `--noconftest` avoids unrelated rollout fixtures and is not a full repository-suite run.

Coverage includes all allocation mask/row/capability outcomes, present/absent optional CPU lengths, real retained CPU plan mapping, actual dispatch argument identities, all four store branches, boundary/branch-point/ping-pong choices, selected COW and existing-node retention, actual clear/COW branches, finished and unfinished donor return bindings, duplicate release interval subdivisions, canonical request-row rebind, existing Dict readback and process-local drain. Resolver/copy/allocator counts confirm diagnostics do not call them again. Metadata-only stand-ins trap tensor iteration, value-dependent bool and numeric device reads. Complete native AST restoration checks cover all eight edited files, including untouched return/kwargs/decision paths.

Initial iteration: **38 PASS / 4 FAIL**, all four failures were test-slice `StopIteration`, not native execution failures. The test selected the first `is_target_verify` else instead of the distinct actual allocation branch. Inspection selected the else containing the real `h_track_buf` assignment; no native decision was replaced. Corrected 42-case run passed before the final coverage additions. No repeated native-fix loop or GPU retry occurred.

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check \
  tests/manual/agent_opd/sglang_mamba_runtime_metadata.py \
  tests/fast/test_sglang_mamba_runtime_metadata.py
git diff --check -- \
  tests/manual/agent_opd/sglang_mamba_runtime_metadata.py \
  tests/fast/test_sglang_mamba_runtime_metadata.py \
  task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_mamba_runtime_metadata_source.md
```

Ruff: **PASS**, with existing deprecated top-level lint-settings warning. Scoped whitespace check: **PASS**. No broader business/runtime result is inferred.

## Exact CPU source artifacts

Final scratch artifact root: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-mamba-runtime-metadata-20261111-final-cybayqik`.

- `runtime/before/` and `runtime/after/`: exact post-selected-FP32 baseline and diagnostic candidate, including empty-before/new-after recorder.
- `runtime/runtime_metadata.diff`: all nine native changed-file sections.
- `runtime/source_manifest.json`: image/version and before/after SHA256 identities.
- `runtime/preflight.jsonl`: exact CPU preparation receipt, explicitly runtime/CUDA unverified.
- `selected-fp32/`: the unchanged existing preparer's source archive.

These paths are local CPU evidence, not worker deployment evidence. Native changed files are `srt/layers/attention/linear/gdn_backend.py`, `srt/layers/attention/hybrid_linear_attn_backend.py`, `srt/managers/schedule_batch.py`, `srt/mem_cache/unified_cache/components/mamba.py`, `srt/model_executor/model_runner.py`, `srt/mem_cache/unified_cache/unified_tree_core.py`, `srt/mem_cache/unified_radix_cache.py`, `srt/managers/scheduler_components/internal_state.py`, and new `srt/mamba_runtime_metadata.py`.

Exact artifact-generation command (the version mock is confined to this CPU harness):

```bash
PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/frontier-py310/bin/python - <<'PY'
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch
import json
from tests.manual.agent_opd import sglang_mamba_runtime_metadata as metadata
from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots
base = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111')
artifact = Path(mkdtemp(prefix='profile-mamba-runtime-metadata-20261111-final-', dir='/data/ycfeng/tmp/opencode-v2-tmp/opencode'))
root = artifact / 'sglang'
for relative, identity in metadata.source_manifest()['files'].items():
    content = (base / identity['native_source_job'] / 'source' / relative).read_bytes()
    expected = snapshots.source_manifest()['files'].get(relative, {}).get('before_sha256', identity['before_sha256'])
    assert metadata._sha256(content) == expected, relative
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
with patch('importlib.metadata.version', return_value=snapshots.source_manifest()['distribution_version']):
    snapshots.prepare_source(root, image=metadata.source_manifest()['image'], selected_fp32=True, archive_dir=artifact / 'selected-fp32')
    receipt = metadata.prepare_runtime_metadata(root, image=metadata.source_manifest()['image'], archive_dir=artifact / 'runtime')
print(json.dumps({'artifact_dir': str(artifact), 'changed_files': receipt['changed_files'], 'source_files_qualified': len(receipt['files']) - 1, 'native_runtime': 'UNVERIFIED', 'diff': str(artifact / 'runtime/runtime_metadata.diff'), 'receipt': str(artifact / 'runtime/preflight.jsonl')}, indent=2))
PY
```

Actual: fifteen pre-existing files qualified, eight existing diagnostic-only patches plus one recorder created, exact diff/manifest/receipt written. No package source identity was replaced with synthetic content.

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 本分工：native source qualification 和冻结 API | PASS | 15 个真实源文件先核验；保留 math owner 和 API。 |
| 本分工：实际 locals 的 CPU receipts 和现有 Dict drain | PASS | 八个文件仅诊断插入；完整 AST 去除诊断后相同。 |
| 本分工：CPU bindings、exact archive 和报告 | PASS | 新增 50 项及既有 25 项全部通过，真实 before/after/diff/receipt 保留。 |
| 集成代理：caller、JSON 和评分后 readback | TODO | 本分工不修改调用方；需要集成代理确认实际收集。 |
| 父任务 04/05：实际 runtime coherence 和 warm correctness | BLOCKED | plan 当前记录 full-model warm FAIL；本次 CPU 准备不能解除 formal hold。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本分工 source qualification 开始至 CPU deliverable 完成｜**当前前沿：** caller 集成、实际 runtime metadata 收集；formal04/05仍受正确性阻塞。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅实现明确要求的 receipts 和必要 CPU 检查，达标后停止扩展。 |
| D2 细节反复重试 | CLEAR | 一次 AST 测试定位错误已据实际 source 修正；无 native retry loop。 |
| D3 支线问题修补 | CLEAR | 没有修改环境告警、全局文档或其他文件。 |
| D4 可并行任务停滞 | NO DATA | 父会话负责其他独立分工；本分工明确禁止 delegation。 |
| D5 超范围镀金 | CLEAR | 无新 endpoint、通用框架、配置 knob 或兼容路径。 |
| D6 分析空转 | CLEAR | source 检查直接形成已验证 deliverable。 |
| D7 路线违背 | CLEAR | CPU-only 和三文件 ownership 遵守；无 GPU 操作或科学条件改变。 |

**文档检查：** S1–S6 在本分工未发现明显缺陷；requirements D40、plan 当前 warm FAIL 和04/05保持，不把 CPU PASS 当成整体完成。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 集成代理接入冻结 API，在 selected-FP32 prepare 后、startup 前调用，并在评分结束后经现有 Dict 收集 receipts → 完成标志：actual caller/JSON/drain integration 证据明确，不声称 all-TP coverage。
2. 父会话按已有授权决定实际验证，核对 allocation/store/donor/node/duplicate-release/canonical-rebind receipts → 完成标志：实际 worker evidence 与仍未测的 physical values、GPU completion、warm parity 分开记录；formal hold 不由本报告解除。

## 4. 最值得关注的 3 点

1. 所有新增 native writes 都先受真实 source hashes 限制，selected-FP32 math 不被重复实现或更改。
2. 现有 readback 只 drain 响应 scheduler 进程；TP 缺片、physical values 和 GPU 完成状态不能从 CPU tuples 推断。
3. 本分工 CPU deliverable 已达标，caller/实际 runtime/warm correctness 仍未验收；04/05保持 BLOCKED。
