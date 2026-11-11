## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Complete scoped CPU integration/regression, preserve RED evidence and real-module skip, and verify actual A/B controller dry-run outputs. |
| 2026-11-11 | Repair Spec P2 witness inheritance with RED/GREEN controls; qualify the now-available real preparer through pinned CPU distribution fixtures; record 190/451 passing checks. |
| 2026-11-11 | Bind committed source 79dba51b with the full override, remove obsolete module-absence skip, verify CPP/TVM missing-evidence skips and 192/453 passing checks, and correct legacy mocked-request wording. |

# KV store stream witness probe integration

TaskID: `profile-kv-stream-witness-integration-20261111`.

Initial outcome at `262f1539` (historical): CPU/injected integration delivered in exactly these files; real-source joined acceptance was pending the independently owned preparer:

- `tests/manual/agent_opd/probe_teacher_scoring.py`
- `tests/fast/test_teacher_scoring_probe.py`
- `task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_stream_witness_probe_config.json`
- `task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_stream_witness_integration.md`

## Scope and agreed seams

The caller's requested seams are the existing config owner, isolated-probe/formal merge, source preparation before runtime/server startup, retained preload/result identities, unchanged scoring payload/teacher argv and single post-loop runtime metadata readback. Only the four assigned files are edited. The source preparer's fixed API is `prepare_source(native_sglang_package_root: Path, *, image: str, archive_dir: Path) -> dict`; dependency-injected binding checks and real-module joined checks are reported separately.

Plan: config typing/dependencies RED -> GREEN; source binding/order/receipt RED -> GREEN; exact isolated config and controller dry-runs; affected/joined CPU tests, Python 3.10 syntax, JSON and scoped whitespace verification.

Formal A/B remain on HOLD. Source preparation is not native stream validation. No platform/auth/GPU operation, payload capture, CUDA tensor value read, synchronization, waits, events, locks, stream changes, numerical coherence or performance acceptance is in this slice.

## Verification

Config RED: `21 failed, 1 passed, 151 deselected` in 1.82 seconds, Python 3.12.13 / pytest 9.1.1 / four existing warnings. Expected failures showed missing boolean/dependency checks and the wrapper dropping the true witness selection. The one passing case was direct-formal true with both dependencies, which already retained arbitrary direct config fields.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'kv_stream_witness' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-config-red-20261111
```

Working directory for every command: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. CPU tests use `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python **3.12.13**, pytest **9.1.1**. Controller and syntax checks use `/usr/bin/python3`, Python **3.10.6**. No conda activation; `TMPDIR=/data/ycfeng/tmp`, bytecode disabled, pytest cache disabled, test outputs confined to the specified temporary paths. Pinned native distribution versions are CPU fixture inputs, not claims about this host or a new worker.

| Check | Expected | Actual | Disposition |
| --- | --- | --- | --- |
| Config GREEN | Strict JSON boolean, both dependencies, original formal merge; original formal file unchanged | 22 passed / 151 deselected / four existing warnings / 0.99 s | PASS, CPU |
| Injected API/order RED | Enabled witness fails before runtime because its preparer has not been wired; four absent/false baseline cases remain valid | 3 failed / 4 passed / 173 deselected / four warnings / 1.45 s; missing `kv_streams` event | Expected RED |
| Injected config/binding GREEN | Keyword-only fixed API; snapshots -> metadata -> KV streams -> runtime -> server; independent receipt and source identity; no import/preparation/readback added for false/absent | 29 passed / 151 deselected / four warnings / 1.18 s | PASS, CPU injection only |
| Exact-clone RED | Missing new config fails A/B construction | 2 failed / 180 deselected / four warnings / 1.14 s; `FileNotFoundError` for new config | Expected RED |
| Exact clone and affected suite | Only task_id/output_parent/acceptance/new true boolean differ; same native argv, allocation, fixture and budgets | 182 passed / four warnings / 8.73 s | PASS, CPU |
| Existing seven-file relevant prejoin suite | Preserve native scoring, snapshot, metadata, submission, HTTP error-body and DP1 None/RID contracts | 381 passed / 20 existing warnings / 31.96 s | PASS; new source module not included |
| Added real-preparer joined binding case and affected source order | Exercise actual new preparer only when available; explicitly skip absent module/native evidence | 39 passed / 1 skipped / 143 deselected / four warnings / 3.12 s; skip: `Real KV stream source preparer is not yet available` | Injected/existing paths PASS; real module SKIPPED, not accepted |
| Final seven-file relevant regression including real-module joined case | All available required checks pass; explicitly report unavailable real source module | 381 passed / 1 skipped / 20 existing warnings / 36.54 s | PASS for available CPU scope; real-module acceptance still SKIPPED |
| Actual A/B controller dry-runs | No auth/client/submission; forward new config through existing selected-FP32 path | Both exit 0, `submitted=false`, 4 requested H800/codesign each | PASS, configuration only |
| Python 3.10 syntax / JSON / scoped whitespace | Both owned Python files compile; JSON parses and dependencies are true; no whitespace errors | PASS | CPU/source only |

Exact CPU commands, in execution order after the config RED above:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'kv_stream_witness' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-config-green-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'kv_stream_witness_api_binding' --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-binding-red-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'kv_stream_witness' --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-binding-green-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'kv_stream_witness_config_exact' --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-clone-red-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-affected-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py tests/fast/test_sglang_mamba_snapshots.py tests/fast/test_sglang_mamba_runtime_metadata.py -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-prejoin-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'kv_stream_witness or selected_source_preparation' --tb=short -rs --durations=5 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-joined-binding-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py tests/fast/test_sglang_mamba_snapshots.py tests/fast/test_sglang_mamba_runtime_metadata.py -q --tb=short -rs --durations=5 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-final-regression-20261111
```

## Retained observations and limitations

- The injected end-to-end `_run` case executes the real benchmark and metadata receiver with mocked HTTP/runtime/server and injected source preparers. Its synthetic seven-sample/two-repeat baseline remains **56 requests / 32 flushes / one initial server-info request**. Its four-sample/one-repeat diagnostic remains **16 requests / 10 flushes / one initial and one post-loop server-info request**. False/absent selection does not import or call the KV preparer and never adds a metadata readback. Existing original-first4 tests separately preserve actual sample identities **1693–1696**, request order and unsalted payloads. No salt intervention is selected.
- Enabled injection retains `kv_store_stream_source_preflight` independently in preload/result and adds `tests/manual/agent_opd/sglang_kv_streams.py` to `native_scoring_sources` only when selected. Injected missing/malformed metadata leaves all previously written scoring/source artifacts byte-identical and `native_measurements_completed=true`; the independent readback failure is surfaced without numerical/performance acceptance. Existing HTTP failure-body, native RID and legal raw DP1 `dp_rank=None` checks remain unchanged.
- The real-source joined test reuses `snapshot_source` and `MILES_PINNED_SGLANG_SOURCE`, never assumes local evidence exists in CI, and skips an absent source module/native evidence explicitly. It preserves actual preparer calls and verifies preparation order/receipt/identity before mocked runtime/server. At this checkpoint the new module is absent, so **the real new API was not executed**. A joined rerun with the externally owned module and its required source evidence is unfinished.
- No new tests are registered for GPU CI. The affected test file completed within the existing fast CPU budget. No source preparer, shared task document, submit helper, snapshot, other test, platform/auth/GPU action or formal config was edited by this slice.

## Actual controller dry-runs

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_stream_witness_probe_config.json --pair A --receipt /data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-dry-run-A-20261111.json --dry-run > /data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-controller-A-20261111.json
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_stream_witness_probe_config.json --pair B --receipt /data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-dry-run-B-20261111.json --dry-run > /data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-controller-B-20261111.json
```

Both inspected output JSON files retain the accepted image digest ending `7805`, two unchanged source volumes, `/data/ycfeng` local source mount, only the existing `PYTHONPATH` resource environment, one 4-GPU/32-CPU/256-GiB replica and the original timeout wrapper (`3600s`, cleanup grace `90s`). Worker commands use `/opt/sglang/bin/python3`, the new isolated config, the original first4 manifest, `--repeats 1`, `--request-timeout 3600`, with no extra flags. The requested receipt paths and native output directories were not created; these are configuration constructions, not actual GPU allocation or runtime evidence.

The final Python 3.10 readback explicitly checked both output JSON objects, forwarded config/manifest/repeat/request-timeout argv, `submitted=false`, four-H800/codesign policy fields and absence of receipt/native-output directories. Expected and actual: PASS. Final strict JSON reserialization used `allow_nan=False`; clone comparison excluded only the four allowed keys.

## Syntax, JSON and whitespace

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
import json
import platform
paths = [Path('tests/manual/agent_opd/probe_teacher_scoring.py'), Path('tests/fast/test_teacher_scoring_probe.py')]
for path in paths:
    compile(path.read_text(), str(path), 'exec')
config_path = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_stream_witness_probe_config.json')
config = json.loads(config_path.read_text())
assert config['kv_store_stream_witness'] is True
assert config['selected_fp32_snapshots'] is True and config['mamba_runtime_metadata'] is True
print('PASS: Python', platform.python_version(), 'syntax for', len(paths), 'owned Python files; strict JSON clone parsed')
PY
git diff --check -- tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_teacher_scoring_probe.py task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_stream_witness_probe_config.json task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_stream_witness_integration.md
```

## 1. 规划完成情况

**汇总：** PASS 4｜BLOCKED/FAILED/SKIPPED 1｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 配置 typing/dependencies 与原 merge | PASS | 22 项 RED/GREEN 完成 |
| 注入 API/order/receipt 与 baseline 行为 | PASS | 29 项通过；56/32、16/10 不变 |
| exact clone 与现有 A/B controller dry-run | PASS | affected 182 项；两个 dry-run 均未提交 |
| 真实 source preparer joined binding | SKIPPED | 新模块尚未提供；不是 native 验收 |
| 最终 regression、report、Python 3.10/JSON | PASS | 381 PASS / 1 显式 skip；语法及实际 dry-run readback 通过 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本 slice 开始至最终 CPU regression｜**当前前沿：** scoped commit；真实模块等待外部交付。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅补授权验收测试，沿用现有 receiver 和 launcher |
| D2 细节反复重试 | CLEAR | RED 均直接暴露缺失配置/调用；对应实现转 GREEN |
| D3 支线问题修补 | CLEAR | 未修改范围外文件 |
| D4 可并行任务停滞 | CLEAR | 两个 dry-run 并行；禁止进一步 delegation |
| D5 超范围镀金 | CLEAR | 只加一个 opt-in boolean 和现有路径消费 |
| D6 分析空转 | CLEAR | 已交付 config、runtime wiring 和 CPU 证据 |
| D7 路线违背 | CLEAR | 无平台/GPU/同步干预，formal HOLD 不变 |

**文档检查：** 本次明确授权 slice 的 S1–S6 均未发现明显缺陷；父任务历史 design HOLD 不被 CPU 集成改写。
**归因：** 无。

## 3. 纠正建议

**分支：** A：本次 scope 合理，无需修改 shared spec/tickets。
**需停止的偏离行为：** 无。

**接下去的路线：**
1. CPU regression、report、Python 3.10/JSON 已完成；检查 scoped whitespace 后仅提交四个 owned files。
2. 外部 preparer 交付后重跑 real joined binding；完成标志为真实 API/source preparation/order/receipt 通过，不是 native stream PASS。

## 4. 最值得关注的 3 点

1. 真实 preparer 未交付，当前通过项只支持 CPU 注入与已有 source 路径。
2. single post-loop metadata receipt 与 scoring artifacts 仍独立，缺失/异常不会变成 scoring 或 witness PASS。
3. Formal A/B 继续 HOLD；actual stream/class、CUDA compile、GPU parity、numeric coherence、性能均未验收。

## Spec P2 repair continuation — 2026-11-11

**[Original Request / primary review feedback]:** on `pinned3aba -> 262f1539`, the direct-formal branch supports `kv_store_stream_witness=true`, but the probe/formal merge inherited it when the wrapper selected false or omitted the key. Standards reported No findings; Spec reported one P2. Repair only this witness ownership issue in the existing merge, preserve direct true, original formal bytes and all other flag behavior, perform RED/GREEN and affected/joined CPU checks, and commit only the probe, its existing CPU test and this report. The new config, source preparer and shared docs are not editable in this continuation. No GPU/auth/platform operations or further delegation.

**Plan and cause:** inherited-input RED -> clear only the copied witness key at the existing merge -> {CPU regression/real preparer binding, Python 3.10/unchanged-config checks} -> report/scoped commit -> primary re-review. The actual failing config and `_run` watcher confirm the reviewed cause, so no broad bisection, speculative fallback or generic merge framework is needed. `config.pop("kv_store_stream_witness", None)` runs only in the wrapper/formal branch, before re-adding an explicitly selected true. Direct-formal input is unchanged. No selected-FP32, metadata, salt or engine merge logic changes.

### Updated CPU evidence

Same working directory and environments as the historical section: Python **3.12.13**, pytest **9.1.1**, `TMPDIR=/data/ycfeng/tmp`, bytecode/cache disabled; Python **3.10.6** for syntax/JSON and receipt readback. No conda activation or platform call.

| Check | Expected | Actual | Disposition |
| --- | --- | --- | --- |
| Inherited true RED | False/absent wrappers expose unwanted inherited key and actual witness import; wrapper true/direct true remain supported | 4 failed, 3 passed, 183 deselected, four existing warnings, 1.68 s | Expected RED |
| One-line merge GREEN | False/absent merged dictionaries omit the witness key; actual `_run` performs zero witness imports/preparer calls; true controls still prepare once; formal bytes unchanged | 7 passed, 183 deselected, four warnings, 1.79 s | PASS |
| First affected rerun, now with new real module | Existing source fixture must supply both pinned distribution identities and an independent TVM-FFI source location | 189 passed, 1 failed, four warnings, 11.09 s; `apache-tvm-ffi=0.5.24.dev80+g056f871; expected=0.1.11` | Retained failure; fixture defect, not a skip/native verdict |
| Real source binding after fixture correction | Call actual snapshots -> metadata -> KV preparer before mocked runtime/server; archive real receipt and source identity | 1 passed, 189 deselected, four warnings, 1.52 s | PASS, real API/source preparation under CPU fixtures only |
| Final affected test file | All config, baseline, new inherited-input, HTTP/DP1/RID and real-source binding contracts pass | 190 passed, zero skips, four warnings, 10.02 s | PASS |
| Final eight-file joined suite | Preserve seven prior relevant suites and include 62 externally owned new source tests | 451 passed, zero skips, 20 existing warnings, 46.34 s | PASS, CPU only |
| Python 3.10 syntax / JSON / unchanged config / receipt readback / whitespace | Both owned Python files compile; new config remains byte-identical to `262f1539`; receipt agrees across preload/result/archive | PASS, Python 3.10.6; scoped whitespace clean | PASS |

Exact test commands:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'probe_selection_overrides_inherited_formal_true or inherited_true_run_respects_probe_opt_out' --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-inheritance-red-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'probe_selection_overrides_inherited_formal_true or inherited_true_run_respects_probe_opt_out' --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-inheritance-green-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q --tb=short -rs -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-inheritance-affected-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'kv_stream_witness_real_preparers_join_before_runtime' --tb=short -rs -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-inheritance-real-joined-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q --tb=short -rs --durations=5 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-inheritance-affected-green-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py tests/fast/test_sglang_mamba_snapshots.py tests/fast/test_sglang_mamba_runtime_metadata.py tests/fast/test_sglang_kv_streams.py -q --tb=short -rs --durations=5 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-inheritance-joined-final-20261111
```

### Real-module binding and retained limits

The earlier **381 PASS / 1 SKIP** is unchanged historical evidence. The new module became available during this continuation. Its first actual call exposed the older snapshot fixture's global `version` stub returning the SGLang version for every distribution. The joined test now derives both expected versions from the actual module's `source_manifest()`, stages only required retained files, and injects the TVM distribution's `locate_file` into a separate temporary `native-tvm-ffi` directory. Production source preparation still resolves TVM files through its own distribution API, not a nested SGLang snapshot. Missing retained source is explicitly skipped in CI; identity/seam failures are not suppressed. No source preparer, installed distribution or unrelated flag is changed.

Actual joined receipt: **35 qualified source files**, five changed files (`model_runner.py`, `forward_context.py`, `memory_pool.py`, `kvcache.py`, `kvcache.cuh`); pinned CPU inputs SGLang `0.5.24.dev80+g056f871` and apache-tvm-ffi `0.1.11`. Retained source-preparer identity is **17,123 bytes**, SHA256 `6140cdc283c457938d34f06dc8adad3657465cbc800acf08c80cede6e378e51d`. Preload, result and `kv_store_stream_source_preflight/preflight.jsonl` contain the same independent real preparer receipt. Correction: the reused real-preparer joined scenario uses one synthetic sample/two repetitions with an eight-request expected budget, but its benchmark/readback are mocked and **no scoring HTTP requests are made**. The inherited-input `_run` watcher separately retains four synthetic samples/**16 requests / 10 flushes**, one post-loop metadata readback and unchanged native argv through mocked HTTP. The existing unsalted **56/32** baseline and original-first4 checks also pass. None of those CPU synthetic vectors establish native first4 reproduction.

The receipt itself keeps `native_compilation=UNVERIFIED`, `actual_streams_allocator_class_vectors=UNVERIFIED; CPU binding is not native execution`, `physical_slot_values=UNMEASURED`; numerical acceptance remains null and performance acceptance false. Actual stream/class, CUDA compile, GPU parity, numeric coherence and performance remain unaccepted. Formal A/B remain HOLD. The primary's re-review of the repaired artifact and the separately owned source review are not completed by this test report.

Final syntax/JSON and decisive actual receipt readback command:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
import json
import platform
import subprocess
for path in [Path('tests/manual/agent_opd/probe_teacher_scoring.py'), Path('tests/fast/test_teacher_scoring_probe.py')]:
    compile(path.read_text(), str(path), 'exec')
config = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_stream_witness_probe_config.json')
assert config.read_bytes() == subprocess.check_output(['git', 'show', f'262f1539:{config}'])
json.dumps(json.loads(config.read_text()), allow_nan=False)
output = Path('/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-inheritance-joined-final-20261111/test_kv_stream_witness_real_pr0/retained-new')
preload, result = (json.loads((output / name).read_text()) for name in ('preload.json', 'result.json'))
receipt = result['kv_store_stream_source_preflight']
assert receipt == preload['kv_store_stream_source_preflight']
assert receipt == json.loads((output / 'kv_store_stream_source_preflight/preflight.jsonl').read_text())
assert receipt['native_compilation'] == 'UNVERIFIED'
assert receipt['actual_streams_allocator_class_vectors'].startswith('UNVERIFIED')
assert receipt['physical_slot_values'] == 'UNMEASURED'
assert all(Path(path).is_relative_to(output.parents[1] / 'test_kv_stream_witness_real_pr0/native-tvm-ffi') for relative, path in receipt['source_paths'].items() if relative.startswith('tvm_ffi/'))
assert result['numerical_acceptance'] is None and result['performance_accepted'] is False
print(json.dumps({'python': platform.python_version(), 'syntax_json_unchanged_config': 'PASS', 'receipt_identity_archive': 'PASS',
                  'source_preparer_identity': result['native_scoring_sources']['tests/manual/agent_opd/sglang_kv_streams.py'],
                  'qualified_source_files': len(receipt['files']), 'changed_files': receipt['changed_files'],
                  'distribution_version': receipt['distribution_version'], 'tvm_ffi_distribution_version': receipt['tvm_ffi_distribution_version'],
                  'native_compilation': receipt['native_compilation'], 'actual_streams_allocator_class_vectors': receipt['actual_streams_allocator_class_vectors'],
                  'scoring_requests': result['expected_scoring_requests'], 'metadata_status': result['runtime_metadata']['status']}, indent=2))
PY
git diff --check -- tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_teacher_scoring_probe.py task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_stream_witness_integration.md
```

## 1. 规划完成情况（P2 修复 checkpoint）

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 0｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| inherited true RED/GREEN 与 direct/true controls | PASS | 4 个真实失败转为 7 PASS；仅一行生产变更 |
| affected 与真实 preparer joined CPU checks | PASS | 190/451 PASS，零 skip；真实 API/order/receipt 已调用 |
| Python 3.10/JSON/原 config bytes/report | PASS | 原 config 未改，archive/preload/result receipt 一致 |
| primary 重审修复产物 | TODO | 本 slice 不代替 review；source/native 验收仍独立 |

## 2. 偏离检测（P2 修复 checkpoint）

**结论：** 未偏移，正常推进。
**检测窗口：** P2 feedback 至最终 451-PASS CPU 验证｜**当前前沿：** 三文件 scoped commit 与 primary 重审。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 实际新 preparer 的 distribution seam 阻塞 required joined check；修正后停止 |
| D2 细节反复重试 | CLEAR | 精确 RED 后单行修复；新失败以版本/定位证据修复 fixture |
| D3 支线问题修补 | CLEAR | 只修授权 P2 与 required CPU binding fixture |
| D4 可并行任务停滞 | CLEAR | affected/joined checks 并行；遵守无 further delegation |
| D5 超范围镀金 | CLEAR | 未扩展 flags/merge/source/GPU 功能 |
| D6 分析空转 | CLEAR | 已交付单行变更及 190/451 通过证据 |
| D7 路线违背 | CLEAR | 三文件 ownership、新 config 不变、formal HOLD 不变 |

**文档检查：** 本次明确授权 scope 的 S1–S6 均未发现明显缺陷。
**归因：** 无。

## 3. 纠正建议（P2 修复 checkpoint）

**分支：** A：scope 合理，不修改 shared spec/tickets。
**需停止的偏离行为：** 无。
**接下去的路线：**
1. scoped whitespace 检查后只提交三个 owned files；primary 重审固定 diff。
2. 实际 stream/class、CUDA 编译与 numeric/native 验证留在其独立授权阶段；不得用本 CPU PASS 释放 formal HOLD。

## 4. 最值得关注的 3 点（P2 修复 checkpoint）

1. False/absent 确实删除继承 witness，direct true 未受影响；实际 `_run` opt-out 无新 import/preparer。
2. 真实 module CPU binding 已执行通过，但分布版本/HTTP/runtime 是明确 fixture inputs，不是安装或 native 证据。
3. Primary 重审未完成；formal HOLD 与 actual stream/class、GPU/numeric/performance 限制保持不变。

## Committed source delivery binding — 2026-11-11

**[Original Request / dependency delivery]:** source `79dba51b` is CPU complete and exposes actual `prepare_source(root, *, image, archive_dir)`. Complete real binding after the opt-out repair using the full `MILES_PINNED_SGLANG_SOURCE` override and the source-owner manifest, redirect TVM distribution lookup only in the CPU fixture, retain honest missing-evidence skips, remove the obsolete module-absence skip, preserve the original 381-PASS/1-SKIP history, and recheck the 4-H800 driver dry-runs. Only the existing three integration-owned files are editable; source/module tests, shared docs and config are protected. Independent source reviews are not repeated. No GPU/auth/platform/delegation operation.

**Changes:** the existing manifest-copy block is now the `kv_stream_source` CPU fixture so both real binding and missing-evidence cases use one preparation path. It copies 34 retained manifest inputs, lets the actual metadata preparer generate its recorder, and qualifies all 35 IDs through the actual KV preparer. It does not copy the 5,501-file source package. Normal import now requires the committed real module; there is no fake module, `importorskip`, or import suppression in this real binding. CPP/TVM missing files still raise an explicit pytest evidence skip. The test now compares the returned KV receipt with its actual archive as well as preload/result, without changing the receipt. Production probe/config/argv are unchanged from the opt-out repair.

**Actual order:** real snapshots preparation -> real metadata preparation -> real `sglang_kv_streams.prepare_source` -> mocked runtime inspection -> mocked teacher startup -> mocked benchmark -> mocked metadata collector. The CPU distribution versions/TVM locator are injected from `source_manifest()`. The actual preparers and their native source rewrites are not faked. This proves source binding/order/receipt, not native execution or a real server readback.

| Check | Expected | Actual | Disposition |
| --- | --- | --- | --- |
| Full override focused binding and missing CPP/TVM controls | Real source API called; the two incomplete overrides raise the precise expected evidence skip before launch | 3 passed, zero outer skips, 189 deselected, four warnings, 1.94 s | PASS |
| Full override affected file | All available integration/config/HTTP/source contracts pass | 192 passed, zero skips, four existing warnings, 11.53 s | PASS |
| Full override eight-file joined suite | All prior relevant tests plus actual source tests and new evidence controls pass | 453 passed, zero skips, 20 existing warnings, 50.07 s | PASS, CPU only |
| Actual missing override invocation | Unavailable retained evidence must propagate as SKIP, never binding PASS | 1 skipped, 191 deselected, four warnings, 0.89 s; `Actual retained native SGLang C3 source is not available` | Expected SKIP; not acceptance |
| A/B actual controller dry-runs | Each remains 4 H800/codesign, unsubmitted, identical worker argv except dated output directory | Both exit 0; `submitted=false`, 4 requested GPUs each; resource fields and normalized argv identical to the earlier actual A/B outputs | PASS, construction only |
| Python 3.10/unchanged source/config/receipt readback | Both owned Python files compile; config equals 262f1539 bytes; real module equals 79dba51b bytes; real source receipt agrees across result/preload/archive | PASS, Python 3.10.6; 35 source IDs / five source edits, same 17,123-byte SHA256 identity recorded above | PASS |

All commands use the same working directory and Python/pytest versions documented above. Exact commands:

```bash
MILES_PINNED_SGLANG_SOURCE=task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'kv_stream_witness_real_preparers or kv_stream_source_override' --tb=short -rs -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-source-delivery-binding-20261111
MILES_PINNED_SGLANG_SOURCE=task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q --tb=short -rs --durations=5 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-source-delivery-affected-20261111
MILES_PINNED_SGLANG_SOURCE=task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py tests/fast/test_sglang_mamba_snapshots.py tests/fast/test_sglang_mamba_runtime_metadata.py tests/fast/test_sglang_kv_streams.py -q --tb=short -rs --durations=5 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-source-delivery-joined-20261111
MILES_PINNED_SGLANG_SOURCE=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-source-delivery-missing-evidence-20261111 TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'kv_stream_witness_real_preparers_join_before_runtime' --tb=short -rs -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-source-delivery-absence-20261111
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_stream_witness_probe_config.json --pair A --receipt /data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-source-delivery-dry-run-A-20261111.json --dry-run > /data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-source-delivery-controller-A-20261111.json
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_stream_witness_probe_config.json --pair B --receipt /data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-source-delivery-dry-run-B-20261111.json --dry-run > /data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-stream-witness-source-delivery-controller-B-20261111.json
```

The old 381-PASS/1-SKIP and later 190/451 results remain historical. The current full-evidence run has no module/evidence skips. The missing-evidence invocation deliberately has one SKIP; the two persistent CPP/TVM controls catch their expected inner evidence skips and therefore count as passing tests, not completed real bindings for those incomplete inputs.

**Readback-query correction:** an auxiliary report query incorrectly accessed `result['runtime_metadata']['scope']`, raising `KeyError: 'scope'`; the result owns only a summarized status/receipt reference. Following that reference then raised `FileNotFoundError`, because this legacy collector is mocked and returns without writing the raw metadata artifact. Inspection of the existing mock and result established the cause. The corrected query checks the real source archive but explicitly asserts the mock metadata artifact is absent. No receiver behavior, fallback or native error handling changed. The legacy real-source case made no scoring HTTP calls or actual metadata readback; its expected eight-request budget is not a measured request count. Separate HTTP-contract tests preserve 56/32 baseline and 16/10 diagnostic behavior.

Decisive final readback and driver comparison:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
import json
import platform
import shlex
import subprocess
for path in [Path('tests/manual/agent_opd/probe_teacher_scoring.py'), Path('tests/fast/test_teacher_scoring_probe.py')]:
    compile(path.read_text(), str(path), 'exec')
config = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_stream_witness_probe_config.json')
assert config.read_bytes() == subprocess.check_output(['git', 'show', f'262f1539:{config}'])
source = Path('tests/manual/agent_opd/sglang_kv_streams.py')
assert source.read_bytes() == subprocess.check_output(['git', 'show', f'79dba51b:{source}'])
base = Path('/data/ycfeng/tmp/opencode-v2-tmp/opencode')
output = base / 'kv-stream-witness-source-delivery-joined-20261111/test_kv_stream_witness_real_pr0/retained-new'
preload, result = (json.loads((output / name).read_text()) for name in ('preload.json', 'result.json'))
receipt = result['kv_store_stream_source_preflight']
assert receipt == preload['kv_store_stream_source_preflight'] == json.loads((output / 'kv_store_stream_source_preflight/preflight.jsonl').read_text())
assert receipt['native_compilation'] == 'UNVERIFIED' and receipt['physical_slot_values'] == 'UNMEASURED'
assert result['cache_observations'] == {'scope': 'CPU mock; no requests made'}
assert not Path(result['runtime_metadata']['receipt']).exists()  # The mocked collector returns without writing a readback artifact.
assert result['numerical_acceptance'] is None and result['performance_accepted'] is False
for pair in ('A', 'B'):
    current = json.loads((base / f'kv-stream-witness-source-delivery-controller-{pair}-20261111.json').read_text())
    previous = json.loads((base / f'kv-stream-witness-controller-{pair}-20261111.json').read_text())
    assert current['submitted'] is False and current['requested_gpus'] == 4
    assert {k: v for k, v in current.items() if k not in ('output', 'worker_command')} == {k: v for k, v in previous.items() if k not in ('output', 'worker_command')}
    commands = [shlex.split(shlex.split(record['worker_command'])[2].splitlines()[-1]) for record in (previous, current)]
    for command in commands:
        command[command.index('--output-dir') + 1] = '--output-dir'
    assert commands[0] == commands[1]
    assert not Path(current['output']).exists()
    assert not (base / f'kv-stream-witness-source-delivery-dry-run-{pair}-20261111.json').exists()
print(json.dumps({'python': platform.python_version(), 'syntax_unchanged_config_source': 'PASS',
                  'receipt_unchanged_preload_result_archive': 'PASS', 'source_ids': len(receipt['files']), 'native_files_changed': len(receipt['changed_files']),
                  'source_identity': result['native_scoring_sources']['tests/manual/agent_opd/sglang_kv_streams.py'],
                  'expected_request_budget_only': result['expected_scoring_requests'], 'scoring_http_executed': False,
                  'driver_AB_submitted': False, 'driver_gpus_each': 4, 'driver_argv_unchanged': 'PASS',
                  'native_scope': receipt['actual_streams_allocator_class_vectors']}, indent=2))
PY
git diff --check -- tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_teacher_scoring_probe.py task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_stream_witness_integration.md
```

## 1. 规划完成情况（source delivery checkpoint）

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 0｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| committed real API/order/receipt 与 missing-evidence controls | PASS | 3 focused PASS；真实 module 与 79dba51b 字节一致 |
| full override affected/joined 与 driver/syntax checks | PASS | 192/453 PASS 零 skip；两个 4-H800 driver dry-run 未提交 |
| history/limits/report correction | PASS | 原 381/1 历史保留；旧 mock 请求/metadata 说法已明确纠正 |
| primary 与独立 source reviewers 的最终验收 | TODO | 本 slice 未重复 review，也未作 native 验收 |

## 2. 偏离检测（source delivery checkpoint）

**结论：** 未偏移，正常推进。
**检测窗口：** source 79dba51b 交付至 full override 验证｜**当前前沿：** scoped commit 与 primary review。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 只补 required evidence skips 与 receipt 比较；验证后停止 |
| D2 细节反复重试 | CLEAR | 两次 auxiliary 查询失败定位 summary/mock 无文件；纠正证据查询，不改运行行为 |
| D3 支线问题修补 | CLEAR | 不改 source/共享文档/config；仅维护授权 CPU fixture/report |
| D4 可并行任务停滞 | CLEAR | focused/driver、affected/joined/absence 检查均并行 |
| D5 超范围镀金 | CLEAR | 无 flags/launcher/native 功能增长，production probe 不变 |
| D6 分析空转 | CLEAR | 真实 binding、absence 行为、完整 CPU aggregate 均有实际结果 |
| D7 路线违背 | CLEAR | 无 GPU/auth/platform/delegation/re-review，formal HOLD 不变 |

**文档检查：** 本次明确授权 scope 的 S1–S6 均未发现明显缺陷。
**归因：** 无。

## 3. 纠正建议（source delivery checkpoint）

**分支：** A：scope 合理，不改 shared spec/tickets。
**需停止的偏离行为：** 无。
**接下去的路线：**
1. 只提交授权 test/report 变更；production probe/config/source 保持不变，primary 使用固定 artifact review。
2. 保留 native 全部 UNVERIFIED，不用 CPU source binding 或 driver dry-run 释放 formal HOLD。

## 4. 最值得关注的 3 点（source delivery checkpoint）

1. 完整 evidence 时真实 API 已运行、453 PASS 零 skip；缺 evidence 时诚实 SKIP，不假装完成 binding。
2. 返回的 source receipt 原样保留；benchmark/collector 的 mock 不能当作请求、metadata 或 GPU 证据。
3. 实际 stream/class、CUDA compile、GPU parity、numeric coherence、性能及独立 review 仍未验收。
