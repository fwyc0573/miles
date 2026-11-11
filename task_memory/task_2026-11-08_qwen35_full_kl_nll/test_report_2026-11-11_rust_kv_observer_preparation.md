## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record actual baseline/observer production build-load PASS and original-constructor native RED; correct int64 key buffers, inspect fixture ABI, and prepare explicit qualification-only resume through the sole finalizer. |
| 2026-11-11 | Correct compiler/test caches to worker-local TMPDIR; add error-only native invalidation marker, receipt/path proof and four affected CPU workflow checks. Native execution remains pending. |
| 2026-11-11 | Implement pinned original-FULL observer preparation and isolated production CPU qualification workflow; record host source tests and pending native execution. |

# Rust original-FULL observer preparation

TaskID: `profile-native-rust-kv-observer-implementation-20261111`.

**Outcome: 23 CPU SOURCE checks PASS; actual production baseline/observer build-load PASS; native semantic qualification FAILED before insert and corrected-source replay PENDING.** PRIMARY executed the GPU0 native run. No native library, Torch, CUDA, platform/authentication/API, SSH, GPU operation, package installation, delegation, staging, or commit was executed by this subagent. Existing accepted CPP witnesses/all16 vectors and formal04/05 HOLD are unchanged. The original bundled binary's source commit remains **UNVERIFIED**.

## Deliverables and boundaries

Repository-relative paths:

- `tests/manual/agent_opd/sglang_rust_kv_observer.py`: one owner for native source identity, guarded candidate transformations, existing-loader build orchestration, qualified binary staging, and the fixed `prepare_source(root, *, image, archive_dir, build_receipt)` API. `build_source(root, *, image, archive_dir)` retains the baseline and observer in isolated build roots and writes `observer-build.json` only after qualification succeeds.
- `tests/manual/agent_opd/probe_rust_kv_observer.py`: production-module CPU build/qualification CLI. The public existing `load_rust_extension` is the sole builder; explicit `mode="force"` runs before native import in fresh build processes. Qualification uses the same production module in `mode="never"`, selecting private probe library directories, not inspection or a second builder.
- `tests/fast/test_sglang_rust_kv_observer.py`: 23 CPU preparation/source tests. A source-only adapter test executes the actual pinned `begin_insert` AST against a recording boundary. Placement/resume tests mock only orchestration boundaries; none is Rust runtime evidence. New checks export actual int64 buffers, audit the used ABI, preserve failed inputs, and hash the real retained libraries without loading them.
- `rust_kv_observer_cpu_config.json`: PRIMARY's GPU0 worker recipe, relative to this task directory. It records the exact command arguments and environment without submitting or configuring a worker.
- `evidence/rust-kv-observer-source-20261111/{observer.patch,adapter.patch,source-manifest.json,source-topology-manifest.json}`: candidate patches and source identity receipts only. No new raw621/5501 archive was created.

Actual native patch scope: **two Rust behavior files plus five Rust fixture files**; the diagnostic adapter is one additional Python edit. Core/walk params own `Option<Arc<dyn Fn(...) + Send + Sync>>`; each component-local reconstructed `InsertParams` gets `None`. The walk retains the callback across existing barriers and invokes it exactly after originalR `unified_tree_core.rs:1984`, before1985's split. It borrows `node.try_device_value(FULL)`, not incoming indices, a concatenation, a narrow copy, a new split copy, or a restored value. The bridge filters CPU window overlap before attachment/wrapping and uses only the existing `tensor_to_py(original.shallow_clone())`. Missing FULL is passed as Python `None`.

Source transformation/fixture definitions remain at `sglang_rust_kv_observer.py:58,101,163`; build API at257, retained-input verifier at326, sole finalizer at374, explicit resume at398, and staging API at432. CPU insert buffer is at `probe_rust_kv_observer.py:234`, snapshot at268, native fixtures at437, and four-way qualification at469. Native behavior/fixture/adapter candidate bytes are unchanged from the actual completed builds.

### Observable bridge errors

The callback must expose callable `invalidate(rid,P,E,stage,message)`. Native wrap/capture errors invoke it without returning a cache decision. A failing invalidation emits exactly one purpose-specific **ERROR-ONLY** stderr marker, `old_full_observer_invalidation_failed rid=<rid> P=<P> E=<E> stage=<stage>`, followed by **both** PyErr values through existing PyO3 `write_unraisable`; no PyErr is silently discarded. The marker value is owned by `sglang_rust_kv_observer.INVALIDATION_ERROR_MARKER`. This adds no bridge-error state, cache lock, serving fallback, retry, event, stream, wait, or synchronization. Healthy callbacks perform no file logging.

A double failure does not guarantee collector-bank invalidation. **The future diagnostic acceptance consumer must reject any occurrence of this native marker independently of complete bank coverage.** Collector integration is outside this owner's scope. CPU qualification deliberately injects one capture+invalidation failure, requires exactly one marker with the correct RID/P/E/stage plus both PyErr messages, and compares unchanged native semantics. Original/rebuilt/observer-None stderr must contain no marker. This controlled injection is qualification evidence, not permission to accept a marker in a business probe. A staging receipt now requires the verified marker check. Existing native panic/error/poison handling is unchanged.

## Host verification actually executed

Environment: local host/worktree; `/usr/bin/python3`, **Python3.10.6**; standard-library-only execution. Temporary candidate files use `/data/ycfeng/tmp/opencode-v2-tmp/opencode`. No Cargo/compiler/native extension/Torch invocation occurred.

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.fast.test_sglang_rust_kv_observer -v
```

Expected: source identity rejection and no writes on unsupported prerequisites; original baseline lacks the observer; guarded candidate has immediate original-storage seam; exact fixture scope; actual adapter forwards optional tuple without changing other arguments; compiler/test targets stay under TMPDIR and are removed while selected library/log/receipt copies persist; injected double-failure evidence requires the native marker and both errors independently of bank coverage. Actual: **17/17 PASS, zero skips, latest0.075 seconds**; first corrected run17/17 in0.073 seconds. The earlier delivered13/13 in0.067 seconds and initial12/12 remain historical source evidence. Deliberate mismatched-source/library/receipt and missing/duplicate marker cases are expected rejection tests, not actual native failures. The two cache-placement tests use mock orchestration boundaries, not real compilation or native execution.

The source preparation command used standard Python imports of the two owned modules, `_qualified_files(R, _RUST_PINS)`, `_rust_candidate` on each file, `_adapter_candidate`, `_diff`, `_identities`, and `_source_topology(S, temporary_root)`. It wrote only the four source artifact paths above, populated baseline/candidate22-file roots only inside `TemporaryDirectory`, then rechecked the originalR pins. It parsed all three new Python files using `ast.parse`.

The follow-up regenerated `observer.patch` from the code-owned transformation and updated `source-manifest.json`; the adapter and baseline-only topology artifacts were unchanged. The following exact final command verified those generated bytes, original inputs and owned code/config hashes, then checked whitespace without native execution:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
import ast,json,subprocess
from pathlib import Path
from tests.manual.agent_opd import sglang_rust_kv_observer as o
T=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
A=T/'evidence/rust-kv-observer-source-20261111'
R=T/'evidence/native-rust-source-20261111/exp-1111-124522-553024/checkout/rust/sglang-radix-tree'
S=T/'evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source'
before=o._qualified_files(R,o._RUST_PINS)
after={r:o._rust_candidate(r,b) for r,b in before.items()}
manifest=json.loads((A/'source-manifest.json').read_text())
assert (A/'observer.patch').read_bytes()==o._diff(before,after)
assert manifest['source_before']==o._identities(before) and manifest['source_after']==o._identities(after)
assert manifest['invalidation_failure_marker']==o.INVALIDATION_ERROR_MARKER
for p,sha in manifest['owned_code_sha256'].items():
 assert o._sha(Path(p).read_bytes())==sha,p
 if Path(p).suffix=='.py':ast.parse(Path(p).read_text())
assert (A/'adapter.patch').read_bytes()==o._diff({o._ADAPTER:(S/o._ADAPTER).read_bytes()},{o._ADAPTER:o._adapter_candidate((S/o._ADAPTER).read_bytes())})
assert o._qualified_files(R,o._RUST_PINS)==before
print('PASS: regenerated Rust/adapter patches exact; 22 before/after inputs and four owned-code hashes match; original22 unchanged; three Python ASTs parsed.')
for p in [*(Path(p) for p in manifest['owned_code_sha256']),T/'test_report_2026-11-11_rust_kv_observer_preparation.md']:
 result=subprocess.run(['git','diff','--no-index','--check','/dev/null',str(p)],capture_output=True,text=True)
 assert result.returncode in (0,1) and not result.stdout and not result.stderr,(str(p),result.returncode,result.stdout,result.stderr)
 print('Whitespace PASS exit='+str(result.returncode)+' '+str(p))
print('observer.patch SHA256='+o._sha((A/'observer.patch').read_bytes()))
print('source-manifest.json SHA256='+o._sha((A/'source-manifest.json').read_bytes()))
PY
```

Historical actual: all assertions passed; all five whitespace commands exited1 with empty stdout/stderr. These historical code hashes describe the then-current17-check delivery, not the corrected replay files; do not rerun this historical hash command against current code. Current hashes are in `evidence/rust-kv-observer-qualification-preparation-20261111-r2/source-manifest.json:owned_code`. The unchanged native patch SHA256 is `91754871e394cdab9fda0a1f1b75d1399546b92d0d23b5e77a62d55c4777b213`.

Whitespace verification ran `git diff --no-index --check /dev/null FILE` for each of the three Python files, this report, and the CPU config, plus a standard-library trailing-whitespace check. Actual: five new-file diff exit codes1, empty stdout/stderr, zero trailing-whitespace lines; three ASTs and config JSON parse. The first checker incorrectly required exit0 and raised `AssertionError: ('tests/manual/agent_opd/sglang_rust_kv_observer.py', '', '')`. Inspection confirmed normal no-index new-file diff status1; correcting that expectation passed without changing source or Git configuration. Raw patch context whitespace was preserved, not stripped.

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| OriginalR source inputs | 22 exact files /19 `.rs` | 22/19, all pinned hashes match | PASS |
| Native candidate changes | 2 behavior +5 fixture files | 7 files; Cargo manifests/lock/header/node/components unchanged | PASS |
| Adapter constructor | Original fields unchanged plus optional tuple | Actual pinned constructor AST forwards None/present context | PASS source-only |
| Pre-split ordering | Original FULL borrowed after match length, before split | One immediate native invocation | PASS source-only |
| Source topology | Existing synchronous scheduler and detached core calls | 130 core-call methods contain detach; selected dispatch/normal/overlap sources retained | PASS source-only |
| Temporary candidate/original archive | Candidate only in private temp; rawR unchanged | Original22 pins rechecked; no raw archive edits | PASS |
| Worker TMPDIR | Existing formal config worker-local root | CPU config TMPDIR equals `/var/tmp` | PASS source/config |
| Loader/compiler and native test targets | TMPDIR-scoped, cleaned; only selected library/log/receipt retained | Both orchestration placement/cleanup checks passed | PASS mock boundary only |
| Double-failure qualification | Marker with RID/P/E/stage and both errors | Missing either error/marker and duplicate marker rejected | PASS CPU/source only |
| Python syntax | Three files parse | Three ASTs parsed | PASS |
| Production Rust extension compilation/load | Actual locked production build | Both variants built/loaded in PRIMARY's actualGPU0 run | PASS native build/load only |
| Original/rebuilt/None/enabled semantics/alias/GIL | Actual same-module native outputs | First original constructor FAILED before insert; corrected replay not run | FAILED / replay PENDING |
| Locked dependency implementations | Installed build cache inspected | NOT RUN | PENDING |
| CUDA callback OS thread/S stream/payload | Actual GPU witness | NOT RUN, outside this slice | PENDING |

## Historical initial CPU workflow — do not rerun the build

PRIMARY already ran this initial command. Its retained libraries/source workspace/receipts must be reused by the explicit resume below; the build command is historical evidence, not the replay route:

```bash
TMPDIR=/var/tmp CUDA_VISIBLE_DEVICES='' SGLANG_RUST_BUILD_MODE=never CARGO_NET_OFFLINE=true PYTHONDONTWRITEBYTECODE=1 /opt/sglang/bin/python3 -B tests/manual/agent_opd/probe_rust_kv_observer.py build --root /sgl-workspace/sglang/python/sglang --image artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805 --archive-dir task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-rust-kv-observer-build-20261111
```

Preserve `CUDA_VISIBLE_DEVICES=''`, global/formal `SGLANG_RUST_BUILD_MODE=never`, `CARGO_NET_OFFLINE=true`, `PYTHONDONTWRITEBYTECODE=1`, and the config's worker-local temporary directory. Missing installed Cargo sources/dependencies fail with retained logs; the workflow does not install/download packages or retry. The archive must be new; do not overwrite a failed attempt.

Worker TMPDIR is derived from existing `formal_config.json:worker_local_root` (`/var/tmp` in the pinned image), not the host's NFS temporary path. Each fresh loader build and native fixture run uses `TemporaryDirectory(dir=TMPDIR)` for high-frequency compiler/cache/target files. Those directories are removed on scope exit. The archive retains only the selected compiled `.so`, the22-file baseline/candidate source copies, selected six dependency sources, commands, logs and receipts; it never retains loader caches or Cargo object targets. Loader receipts preserve the now-deleted cache/artifact path as provenance plus `loader_cache_retained=false`; native fixture receipts similarly record `target_retained=false`.

Pinned existing loader source confirms that explicit `cache_dir` owns its target directory (`loader.py:150`) and is forwarded as `CARGO_TARGET_DIR` (`loader.py:414`), rather than writing Cargo objects into the retained workspace. This was a scoped source read, not actual worker execution.

Expected final receipt: `evidence/native-rust-kv-observer-build-20261111/observer-build.json` relative to this task. `observer-build-pending.json` is not acceptance and cannot arm staging. Logs and exact commands are retained for every child phase. Each qualification variant has a60-second timeout to expose native/GIL deadlocks; build/test duration is governed by PRIMARY's worker lifecycle.

Required executed checks before `status=PASS`:

1. Initial build (now complete): retained baseline/observer through the existing loader, same package/module and `python-extension` features, private source/cache roots; imported package/compiler/artifact/CUDA-uninitialized proof. Resume does not repeat this step.
2. In four fresh processes compare original bundled production library, baseline rebuild, observer explicit-None, and enabled observer on ordinary insert/match, original4-row tensor/2-row partial split, missing FULL before restoration, end/abort/missing-resume rejection/next insert, and FULL+MAMBA barrier/resume. Compare actual action tags/index payloads, results, collected topology, and post-insert FULL/MAMBA indices. MAMBA eviction actions execute through the real native method. No fake walker is used.
3. Assert callback pointer/storage/shape/stride/dtype/device metadata against the real old getter read outside capture; observe native OS-thread identity. Test observer ownership after Python params/context are dropped across a real barrier, and release after resume/end. Test an excluded window, capture error, invalidation error, serial callers, and a contended outside native getter while capture releases the GIL. The CPU harness's events/sleep never enter production code.
4. Retain decisive installed locked-source files/hash/excerpts for tch0.24.0 tensor/Python wrapper, torch-sys0.24.0 C++ shallow/wrap/unpack, and PyO3 0.29.2 attach/detach/state. Read only these six selected files from the existing Cargo cache.
5. Compile/run the two added actual Rust observer fixtures using the crate's default native test linking and existing `torch_build_configuration`: `cargo test --locked --offline --manifest-path ARCHIVE/sources/observer/Cargo.toml --target-dir TMPDIR/rust-kv-tests-<temporary>/target old_full_observer -- --nocapture`; require `2 passed`. Production Python-extension compilation is separately required by step1.

Only after PRIMARY verifies build/semantics and completes review may it call `prepare_source` on its **private diagnostic package copy**, after existing selected-FP32 -> CPU metadata -> KV WIT preparation and before any native import. The helper requires exact composition, build scenario coverage/ABI, source identities, original private-bundle SHA, and actual compiled observer ELF/SHA before any archive or source write. It copies the same-name module and modifies only actual adapter forwarding. Shared baseline/retained archives/global never remain unchanged. Receipt is returned for verbatim caller retention. Collector/checkpoint/FRESH/drain integration belongs to the parallel collector owner.

The absolute-path shared-baseline guard is unchanged: `root == receipt.original.package_root` is rejected even across different pods. PRIMARY supplies a different explicit private diagnostic package root and owns runtime import-binding proof. Staging targets that copy's actual `srt/mem_cache/rust_tree_core/mem_cache*.so`; `preflight.json:binary_target` records its resolved full path, with module API `sglang.srt.mem_cache.rust_tree_core.mem_cache` and actual adapter `InsertParamsBinding(..., old_full_observer=...)` forwarding. CPU variant output records `production_module` and resolved `library_path`. Actual build-load library bindings now exist; no private diagnostic staging target/binding is accepted yet.

## Actual native RED and corrected replay preparation

PRIMARY-reported run envelope: `exp-1111-140628-265232`, actual2CPU/8000Mi/GPU0, personal creator, pinned image165 and local NFS verified; terminal `Failed`, exit1, restart0. This subagent read only the retained local build receipts and failure log, not platform APIs.

Both actual production builds loaded `sglang.srt.mem_cache.rust_tree_core.mem_cache` with Python3.12.16, Torch2.14.1+cu130, CXX11=true, CUDA initialized=false, rustc1.99.1. Loader caches were worker-local and cleaned. Unchanged retained artifacts:

- Baseline `.so`: SHA256 `fbe6ea7c5e48216daa34f13b792b38ecf39090a99a3f9a72f776a388d67124aa`,3398568 bytes.
- Observer `.so`: SHA256 `0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba`,3411248 bytes.
- Initial `source-manifest.json`: SHA256 `41bc2e1788d0c423530a91a26f37beaff3100aa81ce100563ebdfb183ca061d3`.
- Compiled observer `src/python_bindings.rs` SHA256 `1e4f7d60918e2d6f8cc110d59f2b1564c31801a73547027b22597ad3b9ecb0fe`; all22 before/after identities still match current transformation.

**Declared cause before replay:** raw fixture list lacks the buffer protocol. Original production `InsertParamsBinding(**kwargs)` failed at archived source line235 with `TypeError: a bytes-like object is required, not 'list'`, in `evidence/native-rust-kv-observer-build-20261111/qualify-original.stderr:12-15`. Its SHA256 is `9e03df976a6f6913cabb123dd396502d235d6e24f5b4e4389b30d516219e7c68`. The actual source `python_bindings.rs:158-174` explicitly extracts `PyBuffer<i64>` and requires C-contiguity; canonical `array('q')` supplies the native int64 buffer while preserving all key values. This is a CPU fixture contract defect, not a Rust compile/model failure.

Only fixture key handling changed: the Insert constructor and all four Match constructors now use `array('q', key)`. Match snapshots additionally enumerate both existing SWA result fields so all13 canonical getters are compared. No native API, Rust source, adapter patch, parameter default, model behavior, lock, fallback or exception suppression changed.

Scoped ABI audit of actual retained bindings (original source SHA `d6f55c307b99195902f6e2c24f8c013b6a1aace0edd51982fedac17bb67adf61`):

| Fixture contract | Inspected source / result |
| --- | --- |
| Key/value and init parameters | `python_bindings.rs:158-174,176-244,258-373,1003-1024`: owned int64 key vector from contiguous buffer; CPU int64 value covers aligned key; existing init keyword names/defaults; MAMBA value is a Tensor |
| Match/insert/step getters | `:427-514,516-575,643-675`: all13 match fields,10 insert fields, list actions and optional step result |
| Begin/resume/end/error | `:1153-1208`; `unified_tree_core.rs:1902-1931,1935-1960`: real native barriers, idempotent end, missing-resume RuntimeError preserved |
| Collected graph/getter | `:1332-1355,1397-1411`: six-field node tuple and optional shallow-cloned device Tensor; no getter inside capture |
| Backup/demote/MAMBA eviction | `:1933-1944,1988-2039`: CPU Tensor plus empty transfer map; actual four-field eviction result |
| Action tags/payload/barriers | `cache_action.rs:140-157`; `python_bindings/cache_action.rs`: tuple tags/index payloads; MAMBA tail-node ID; backup and MAMBA are real insert barriers, free-device/split bookkeeping are not |
| Barrier setup | `unified_tree_core.rs:2128-2139,2146-2275`; `components/mamba.rs:70-79`: existing write-through threshold2 and MAMBA cap1 exercise existing native barriers |

Host RED command (two focused checks, before buffer fix):

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.fast.test_sglang_rust_kv_observer.ObserverCPUWorkflow.test_insert_fixture_exports_actual_contiguous_int64_key_buffer tests.fast.test_sglang_rust_kv_observer.ObserverCPUWorkflow.test_every_native_match_constructor_uses_the_same_int64_buffer -v
```

Actual RED: memoryview failed with the same raw-list buffer TypeError; the Match coverage test initially had an incorrect expected count5, corrected to the inspected four call sites. Same command after the buffer fix: **2/2 PASS,0.012s**. Full source suite after resume/ABI checks: **23/23 PASS, zero skips, latest0.134s** (previous0.136s), Python3.10.6. Six additions are buffer export, all Match constructors, canonical ABI schema, existing-output rejection, failure-only resume orchestration, and real retained ELF/source hashing. No successful native qualification dictionary was fabricated and no host native module executed.

### Exact PRIMARY qualification-only replay

Run only in PRIMARY's approved GPU0 worker, from the mounted repository root. Runnable JSON is `evidence/rust-kv-observer-qualification-preparation-20261111-r2/resume-config.json` relative to this task. **Do not run `build` again.**

```bash
TMPDIR=/var/tmp CUDA_VISIBLE_DEVICES='' SGLANG_RUST_BUILD_MODE=never CARGO_NET_OFFLINE=true PYTHONDONTWRITEBYTECODE=1 /opt/sglang/bin/python3 -B tests/manual/agent_opd/probe_rust_kv_observer.py resume --root /sgl-workspace/sglang/python/sglang --image artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805 --archive-dir task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-rust-kv-observer-build-20261111 --output task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-rust-kv-observer-qualification-20261111-r2
```

`resume_source(root, *, image, archive_dir, output_dir)` first validates the initial pending header, source manifest/current22 baseline and observer sources, adapter identity, original bundle, both actual ELF/build receipts/commands and ABI. It requires the retained failed qualification command and a separate new output directory, then runs the **existing** `qualify --archive-dir OLD --output NEW` child exactly once. `--output` is a qualification directory for this child and a JSON file only for `_exercise`; the resume API creates the directory. No automatic retry, separate replay script, second builder, library copy/rebuild, shared force mode, or global switch is introduced.

All variant JSON/stdout/stderr/commands, selected dependency evidence, topology, actual Rust fixture outputs and `qualification.json` go to the new directory. Existing source workspace and library absolute paths remain inputs. Actual Rust fixture compilation/test execution is still required; its Cargo target is local TMPDIR, not a rebuild of either retained Python extension. Initial failure logs/source/build receipts stay read-only.

Initial `build_source` and explicit `resume_source` both call the **same sole** `finalize_build(root, *, image, archive_dir, qualification_dir)`. The finalizer revalidates retained input identities, reads the actual new qualification/command/variant files, checks required four variants/five cases/native fixtures/marker coverage and actual production module/path/SHA bindings, then writes the original root `evidence/native-rust-kv-observer-build-20261111/observer-build.json`. A following failed native assertion propagates and no PASS receipt/staging occurs. The final receipt retains original library paths/receipts, exact new qualification receipt identity and original binary source commit **UNVERIFIED**.

Static replay inputs/code hashes/ABI list are retained in the new `evidence/rust-kv-observer-qualification-preparation-20261111-r2/source-manifest.json`. No old source archive or failed file was regenerated/overwritten. Current helper SHA `bd289a0d2dfe2d6738b22f329ffab3ffc59a30549e0c20929a099fc7da456690`; probe SHA `380f6aaea1ed2be28750b8eee0b6082146290dc52aff00af1574938d5602042b`.

Final current-source verification command (no native execution):

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
import ast,json,subprocess
from pathlib import Path
from tests.manual.agent_opd import sglang_rust_kv_observer as o
T=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
N=T/'evidence/rust-kv-observer-qualification-preparation-20261111-r2'
m=json.loads((N/'source-manifest.json').read_text())
for item in [*m['inputs'].values(),*m['retained_libraries'].values(),*m['owned_code'].values()]:
 assert o._sha(Path(item['path']).read_bytes())==item['sha256'],item['path']
for name in m['owned_code']:
 if Path(name).suffix=='.py':ast.parse(Path(name).read_text())
for path in [*(Path(name) for name in m['owned_code']),T/'test_report_2026-11-11_rust_kv_observer_preparation.md']:
 result=subprocess.run(['git','diff','--no-index','--check','/dev/null',str(path)],capture_output=True,text=True)
 assert result.returncode in (0,1) and not result.stdout and not result.stderr,(str(path),result.stdout,result.stderr)
print('PASS: six immutable input files, two retained actual ELF hashes, four current source/config hashes, three ASTs and five whitespace checks.')
PY
```

Actual: the current-source verification command above passed all checks. `PYTHONDONTWRITEBYTECODE=1 python3 -B tests/manual/agent_opd/probe_rust_kv_observer.py --help` exited0 and exposed the explicit `resume` action and directory/file meaning of `--output`; no native import occurred.

## Phase checkpoint

### 1. 规划完成情况

**汇总：** PASS3｜BLOCKED/FAILED/SKIPPED3｜TODO0

| 子任务 | 状态 | 依据 |
| --- | --- | --- |
| Native observer/source preparation | PASS | Candidate bytes unchanged; fixed API/error marker and23 CPU/source checks delivered |
| Production native extension build/load | PASS | Actual baseline/observer receipts and ELF hashes verified |
| Corrected explicit resume workflow | PASS | Buffer/ABI/source guards and sole finalizer reuse delivered; actual replay not claimed |
| Native semantic/alias/GIL/lifetime/fixture qualification | FAILED | Original constructor failed before insert; corrected replay remains pending |
| Diagnostic staging | BLOCKED | Passing native receipt and PRIMARY review required |
| Numeric/GPU arm | SKIPPED | Outside delegated authority; formal hold retained |

### 2. 偏离检测

**结论：** 未偏移，正常推进。窗口为17-check交付至本次 actual native RED修正；前沿为复用现有 libraries 的 GPU0 native semantic qualification。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | Declared PyBuffer failure blocks the next qualification; six affected checks stop at source readiness |
| D2 细节反复重试 | CLEAR | No native replay/recompile here; buffer hypothesis declared before fix and host RED/GREEN |
| D3 支线问题修补 | CLEAR | PRIMARY requested ABI inspection and sole-finalizer reuse; owned paths only |
| D4 可并行任务停滞 | CLEAR | Collector and PRIMARY execution are separately owned; further delegation prohibited |
| D5 超范围镀金 | CLEAR | No collector, generic backend, second builder or cache-policy addition |
| D6 分析空转 | CLEAR | Inspected source produced candidate and passing source tests |
| D7 路线违背 | CLEAR | No platform/GPU/build execution or shared-baseline edit |

**文档检查：** Parent `plan.md:3-7` and `requirements.md:415-418` correctly record the failed qualification/reuse frontier and formal HOLD. This owned report's stale17/compile-pending snapshot is corrected above; no spec/ticket edge or scope change. S1–S6 otherwise sound. **归因：** 无。

### 3. 纠正建议

**分支：** B；仅更新本 report 的过期状态，可直接执行且已完成；不修改共享 spec/tickets。**需停止的偏离行为：** 无。

1. PRIMARY runs the explicit qualification-only GPU0 resume, preserving existing artifacts; done requires actual four-way cases, alias/GIL/lifetime/thread/dependencies/Rust fixtures and sole-finalizer root PASS.
2. In parallel, collector owner continues its own CPU/source integration. Diagnostic staging waits for the verified native receipt and review; numerical GPU evidence remains independently pending.

### 4. 最值得关注的3点

1. Both production extensions compiled/loaded;23 host checks do not prove native semantics. Original-constructor RED is source-corrected, not yet replayed.
2. Original binary's source commit remains UNVERIFIED even if prospective rebuild/qualification passes.
3. Double callback/invalidation failure emits a stable native marker that future acceptance must reject independently of bank coverage; native injection proof remains pending.
