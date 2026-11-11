# Rust observer production-native CPU qualification

## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Primary accepts the independently verified actual R3 bounded serial CPU scenarios and repaired contended-getter oracle at17cb6fc6; CUDA capture, numerical/rootfix and formal acceptance remain unverified. |
| 2026-11-11 | Verify actual R3 GPU0 replay at fixed source17cb6fc6: four-variant semantics, repaired retained-Capture oracle, native fixtures and preserved98-file R1/R2 identities PASS; primary R3 acceptance remains PENDING. Preserve R2 acceptance/open-P2 history and its frozen receipt. |
| 2026-11-11 | Preserve accepted bounded R2 serial CPU evidence and raw PASS, reopen the contended-getter oracle as UNVERIFIED after both fixed reviews identify the same P2 at8683a032/probe:385–397, and HOLD qualification release pending corrected GPU0 R3 replay without extension rebuild. Bind R2 to the frozen observer-build-r2.json snapshot; no raw results or commands changed. |
| 2026-11-11 | Record explicit primary ACCEPTED disposition for bounded actual serial CPU qualification only; native code phase reference8683a032, fixed source Standards/Spec reviews pending, no GPU capture approval. Preserve all raw results, commands, first FAIL and source-proof limits. |
| 2026-11-11 | Verify completed GPU0 reuse-library replay against all four raw CPU variants, native Rust fixtures, source/library identities and terminal platform receipts; qualify CPU scope only, preserving the first FAIL and primary acceptance boundary. |
| 2026-11-11 | Record the explicit affected resume after the int64-buffer fixture correction, reusing the same compiled libraries; GPU0 job submitted and initially Running, qualification pending. |
| 2026-11-11 | Record actual GPU0 baseline/observer compile and load success, followed by the original-variant fixture key-buffer failure; semantic qualification is not accepted. |
| 2026-11-11 | Record GPU0 controller preparation and the verified submitter import-order correction; native execution remains pending. |

## Scope and status

**Controller preparation: PASS. Actual baseline/observer compile and load: PASS.
First native semantic attempt: FAIL, preserved below. Affected reuse-library
replay: actual R3 bounded serial CPU qualification PASS and primary ACCEPTED
for the executed CPU scenarios only. Raw R2 PASS/bounded acceptance preserved.**

R3 verifies the retained-Capture contended-getter repair at
`17cb6fc6:probe_rust_kv_observer.py:395–399` using the fixed executed source,
successful enabled child and matching native/library receipts. It does not
manufacture per-callback records or establish general Mutex/race safety.
PRIMARY reports both fixed source review axes have no new findings and the
shared P2 is CLOSED, source-only; those reviews do not accept R3 runtime or
release GPU capture. The actual R3 evidence and disposition are recorded in
[Actual R3 GPU0 CPU replay](#actual-r3-gpu0-cpu-replay--retained-evidence-verification).
R2 raw PASS/bounded acceptance, its historical reopened oracle and the first
constructor FAIL below remain preserved. Original binary source commit,
CUDA, 7955/6804, all-TP, rootfix, performance and formal limits are unchanged.
The absent standalone GIL-contrast artifact is a stated evidence limit, not a
new acceptance gate; arbitrary Mutex reentry and blanket race/deadlock freedom
remain unsupported.

The completed replay exercises the actual production ABI on CPU tensors in
the pinned production image, without rebuilding either retained extension.
It allocates zero GPUs. No H200 run, training, KV numeric capture, or formal
submission is authorized by this CPU result.

- Image: `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`.
- Runtime: `/opt/sglang/bin/python3`; the retained image receipt records Python
  3.12.16, Torch 2.14.1+cu130, CXX11 ABI enabled, and rustc 1.99.1.
- Actual R3 resource limits/requests: one replica, CPU2 / 8000Mi / GPU0;
  submission group `codesign`, positive tag `H800` (template label only).
- Local NFS source: `100.96.128.195:/data/ycfeng:/data/ycfeng`.
- Worker-local `TMPDIR`: `/var/tmp`; Cargo/compiler caches must not use the
  persistent task directory.
- Existing production `SGLANG_RUST_BUILD_MODE=never` remains unchanged. The
  CPU builder selects the existing production loader's explicit force mode
  only in isolated build subprocesses.

## Commands and observed results

Controller script:
`/data/ycfeng/tmp/opencode-v2-tmp/opencode/submit-rust-kv-observer-cpu-20261111.py`.

```bash
STEPMIND_BACKEND=rjob PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH='/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image:/data/ycfeng/steptron' \
/data/ycfeng/tmp/stepmind-env/bin/python -B \
/data/ycfeng/tmp/opencode-v2-tmp/opencode/submit-rust-kv-observer-cpu-20261111.py \
--cpu 2 --memory-gb 8 --dry-run \
> /data/ycfeng/tmp/opencode-v2-tmp/opencode/rust-kv-cpu-controller-dry-run-20261111.json
```

Local environment: Python 3.10.6 in the existing StepMind virtual environment.

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| Controller dry-run | No platform submission; fixed image/local mount; GPU0 | `submitted=false`, GPU0, CPU2/memory8, expected image and NFS source | PASS |
| Worker temporary placement | Formal worker-local root | `TMPDIR=/var/tmp` | PASS |
| Production/formal mode | No global mode change | `formal_build_mode_change=false` | PASS |
| Actual replica and resources | GPU0 personal job with local mount/image | GPU0/CPU2/8000Mi, expected creator/image/NFS source | PASS |
| Baseline/observer compile and load | Existing production loader and module name | Both compiled and loaded, CUDA uninitialized | PASS |
| Four-way semantic/alias/GIL qualification | Actual CPU execution | Original variant failed at fixture key construction | FAIL / NOT EXECUTED |

### Preserved first failure and causal correction

The first dry-run failed before any submission:

```text
from tests.manual.agent_opd.submit_swe_opd import _job_succeeded
ModuleNotFoundError: No module named 'tests.manual'
```

The submitter imported `steptron.exp.base_exp` first. A focused probe showed
that import prepends Steptron's third-party paths; a subsequent `tests` import
resolved to `third_party/super_agent/tests/__init__.py`, not Miles.

The correction uses the existing source submitter's import order: import the
Miles `_job_succeeded` function before the StepTron resource/backend modules.
The same controller command then exited zero and produced the retained
dry-run receipt. No dependency install, module purge, retry fallback, or
platform write was used. Existing Paramiko TripleDES deprecation warnings
were observed and left unchanged.

## First actual native execution — preserved FAIL

Job: `exp-1111-140628-265232`, replica
`exp-1111-140628-265232-cfcd2084`.

The local launcher selected the existing personal Python `RJobBackend`,
remained alive until terminal state, and retained its submission/terminal
receipts under `evidence/rust-kv-observer-cpu-platform-20261111/`. The filtered
platform read confirms creator `i-fengyicheng`, the exact image/local mount,
one CPU2/8000Mi/GPU0 replica, and owner UID binding. The platform reported
`Failed / RJobFailed`; the container exited 1 with reason `Error`, restart
count 0, at `2026-11-11T06:12:33Z`. The launcher's subsequent stop log follows
the failed workload and is not its cause. No OOM conclusion is supported.

The task supplied `H800` as its declared positive tag, but the actual GPU0
template prefers non-GPU machines and exposes no H800 node selection.
Physical node type is not established; no GPUs were requested or allocated.

Both libraries were successfully built and loaded in fresh production-loader
processes, using `python-extension`, Python 3.12.16, Torch 2.14.1+cu130,
CXX11 ABI enabled, rustc 1.99.1, and `cuda_initialized=false`. Both module
names were `sglang.srt.mem_cache.rust_tree_core.mem_cache`. The worker-local
loader caches were `/var/tmp/rust-kv-build-*/loader-cache` and are not retained.

| Variant | SHA256 | Observed result |
| --- | --- | --- |
| Rebuilt baseline | `fbe6ea7c5e48216daa34f13b792b38ecf39090a99a3f9a72f776a388d67124aa` | Build/load PASS |
| Observer candidate | `0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba` | Build/load PASS |

The corresponding exact build commands, stdout/stderr, source manifests and
library receipts are retained under
`evidence/native-rust-kv-observer-build-20261111/`.

### Native RED and next hypothesis

The first original-library CPU variant failed before an insertion:

```text
probe_rust_kv_observer.py:235
return module.InsertParamsBinding(**kwargs)
TypeError: a bytes-like object is required, not 'list'
```

`qualify-original.stderr` preserves the traceback. Canonical retained
`python_bindings.rs:158–174` requires `PyBuffer<i64>` and C-contiguous storage,
explicitly giving `array.array('q')` as an example. The fixture passed a
nonempty Python list for `key`; this is a fixture/native-ABI contract error,
not a Rust compile error. Its prediction is specific: retain the same key
values in the canonical int64 buffer, and the original constructor should
succeed without changing the native library or cache behavior.

The fixture correction uses `array('q')` for the Insert constructor and four
Match constructor call sites, retaining key values. The source owner checked
the complete 13 Match and 10 Insert result fields. Its 23/23 CPU/source checks
passed on Python 3.10.6 in 0.134 s; these do not execute the native module.
All 22 Rust identities and the two compiled library hashes remained unchanged.

### Affected qualification resume

The existing submitter now accepts the explicit resume config. Its dry-run
returned `submitted=false`, `action=resume`, `extension_rebuild=false`,
CPU2/8000Mi/GPU0 and unchanged image, local source and `codesign` allocation.
The resume command and source hashes are retained at
`/data/ycfeng/tmp/opencode-v2-tmp/opencode/rust-kv-cpu-resume-dry-run-20261111.json`.

Exact local launcher command, after the unchanged personal/proxy environment
initialization:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -B -u \
  /data/ycfeng/tmp/opencode-v2-tmp/opencode/submit-rust-kv-observer-cpu-20261111.py \
  --cpu 2 --memory-gb 8 \
  --config task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/rust-kv-observer-qualification-preparation-20261111-r2/resume-config.json
```

This submitted `exp-1111-145408-924409`. The initial exact RJob read confirmed
`Running`, creator `i-fengyicheng`, the same pinned image and local NFS source,
and one CPU2/8000Mi/GPU0 replica. Its filtered platform receipt is
`evidence/rust-kv-observer-cpu-platform-20261111/exp-1111-145408-924409-initial-platform.json`.
Physical node type remains unverified; no GPU was requested.

The worker runs `probe_rust_kv_observer.py resume`, using the completed build
archive and a separate new
`evidence/native-rust-kv-observer-qualification-20261111-r2/` output. It does
not rebuild either extension. Initial build and resume share the sole
`finalize_build`; only a successful actual qualification can create the final
build-root `observer-build.json`. Original failed logs, sources and library
receipts remain read-only. The launcher remains alive until terminal state.

That initial Running checkpoint did not accept the replay. The completed
results below supersede its pending execution status, not the preserved first
failure or the separate primary acceptance decision.

## Completed affected CPU replay — independently verified

Verification task: `profile-rust-native-cpu-verification-20261111`. Verification
read existing artifacts only; it did not execute native code, query/authenticate
to the platform, submit work, rebuild libraries, stage files, or commit.

### Actual job and command disposition

The four filtered SDK receipts are
`evidence/rust-kv-observer-cpu-platform-20261111/exp-1111-145408-924409-{submission,initial-platform,terminal,terminal-platform}.json`.
They agree on job UID `30aee748-9927-4527-82b9-08e8909f3245`, creator
`i-fengyicheng`, one `native-cpu` replica, image165 and the local NFS source.
Actual requests and limits are CPU2 / **8000Mi** / GPU0. Submission records
`codesign`, `action=resume`, `extension_rebuild=false`, and no formal build-mode
change. The terminal replica is bound to that job UID and reports
`Succeeded`, container `Completed`, exit **0**, restart **0**, starting
`2026-11-11T06:54:30Z` and finishing `2026-11-11T06:56:36Z`; job finish time is
`06:56:38Z`. The GPU0 template prefers `MachineType NotIn [GPU]`, with no node
selector; terminal `node=null`. **No physical H800 node claim is supported.**

Actual worker qualification command, retained exactly in
`evidence/native-rust-kv-observer-qualification-20261111-r2/qualification-command.json`:

```bash
/opt/sglang/bin/python3 -B \
  /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/tests/manual/agent_opd/probe_rust_kv_observer.py qualify \
  --root /sgl-workspace/sglang/python/sglang \
  --archive-dir /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-rust-kv-observer-build-20261111 \
  --output /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-rust-kv-observer-qualification-20261111-r2
```

Return code is **0**; qualification stdout/stderr are empty. Each of the four
`qualify-{original,rebuilt,observer-none,observer-enabled}-command.json` records
its exact fresh-process `_exercise` command and return **0**. Original uses the
bundled library; rebuilt selects the baseline library; observer-none selects
the observer library with `--explicit-none`; observer-enabled selects it with
`--enabled`. All four runtime receipts show Python **3.12.16**, executable
`/opt/sglang/bin/python3`, Torch **2.14.1+cu130**, CXX11 ABI **true**, and
**CUDA initialized false**, with distinct PIDs **40/44/48/52**.

### Source, build and actual library identities

R2 is bound to the immutable selected snapshot
`evidence/rust-kv-observer-qualification-receipts-20261111/observer-build-r2.json`,
not the mutable build-root finalizer output. This snapshot preserves the exact
R2 receipt consistent with the four raw variant outputs, qualification command
and qualification receipt, not merely its `status`. Its byte size is **15,835**
and SHA256 is
`4c967246e2cb3ab54e454b87f1a22231c73a7829037dbd98f19ad19bfb2e017b`;
the r2 qualification SHA256 is
`8b05f90ee8ae1f83cf36952692d7e51047617a17415af4bb201fbd4db1fa68f1`.
The separate current finalizer path is
`evidence/native-rust-kv-observer-build-20261111/observer-build.json`; a future
R3 finalizer may overwrite it. It must not be followed silently as R2 evidence.
The primary froze the snapshot outside the read-only r2 raw directory after
a write there failed; this verifier changed no directory permissions.

- The final, pending and standalone source manifests are exactly equal.
  `source-manifest.json` SHA256 is
  `41bc2e1788d0c423530a91a26f37beaff3100aa81ce100563ebdfb183ca061d3`.
  Its 22 baseline identities match the source owner's `_RUST_PINS`; all **22
  actual observer workspace files** match `after` byte sizes and hashes.
  Seven files differ from baseline: the two observer implementation files and
  five existing test files. Cargo.toml, Cargo.lock and torch_compat.h are unchanged.
- Baseline and observer build receipts bind the separate `sources/baseline`
  and `sources/observer` workspaces to their respective `libraries/` paths.
  Both actual local files have ELF headers and match their recorded SHA256:
  baseline **3,398,568 bytes**, observer **3,411,248 bytes**. The hashes in the
  earlier build table remain unchanged and match rebuilt/none/enabled outputs.
  Original reports the production path and SHA256
  `2c1e54965c8139358df1ef2a7751620c339ad1ff4988cee54cc35467a8b90f6c`;
  the pinned worker loader verifies that actual original binary before use.
  That worker file is not present on this verifier's host, so no independent
  host read of the original binary is claimed.
- All four final input-receipt hashes/byte sizes match actual retained files
  and `resume-inputs.json`. The failed qualification command still returns 1.
  This proves the no-extension-rebuild transition; the separate native test
  executable was compiled in a worker-local target directory, not either `.so`.
- At the R2 verification checkpoint, helper/probe/config hashes matched the submission pins: helper
  `bd289a0d2dfe2d6738b22f329ffab3ffc59a30549e0c20929a099fc7da456690`,
  probe `380f6aaea1ed2be28750b8eee0b6082146290dc52aff00af1574938d5602042b`,
  resume config `2e04decbac9065982131b3d70d049e37578be70645839539f0069f5490eb79c4`.
  The previously accepted 5501/621 source-root audits were **not repeated**.

Both compile commands returned 0, and both retained stderr logs end with
`Finished release profile [optimized]` after **2m13s**. The same production
module name is `sglang.srt.mem_cache.rust_tree_core.mem_cache`, library name
`mem_cache`, crate type `cdylib`, feature `python-extension` (not `inspection`).
The inspected, hash-pinned production loader's `_cargo_build` selects
`cargo build --release --locked --package sglang-radix-tree --features python-extension`;
the build receipts confirm force mode only in isolated loader caches. This
Cargo argv is source-backed; wrapper command receipts and compiler logs do not
independently print the full inner argv. Serving/qualification mode remains
`never`. No original-binary source commit is established.

### Actual four-way semantic and observer results

Every raw `semantic` object was compared recursively, including actions,
results, path topology, adopted ranges and FULL/Mamba index tensors. All **20
variant/case executions** are equal to the original-library reference.
Each variant contains **10 non-null Insert results × all 10 fields** and
**11 Match results × all 13 fields**: **40/44** results across the four variants.
The field sets also match the actual production Rust result structs
(`sources/observer/src/python_bindings.rs:639–691`).

| Case | Actual enabled observer/result | Four-way equality |
| --- | --- | --- |
| ordinary | One OLD row: node1/cursor0/prefix3, indices `[10,11,12]`; redundant incoming prefix freed | PASS |
| partial_split | One OLD row before split: prefix2 but original shape4/indices `[10,11,12,13]`; post-split values `[10,11]`, `[12,13]`, `[22]` | PASS |
| missing_full | One row with tensor/metadata `None`, before FULL restoration to `[20,21,22]` | PASS |
| end_abort | Suspended backup step; `end_actions=[]`; resume fails with `no in-flight insert`; later independent insert `[90]` succeeds | PASS |
| mamba_barrier | Two steps, `mamba_evict_excess_path_states` actions; one original FULL row; resumed FULL/Mamba values match reference | PASS |

All five ordinary enabled-case rows run on native thread **52**, the invoking
thread. The four present CPU tensor aliases have equal original/getter and
callback `data_ptr`, storage pointer, shape, stride `[1]`, offset **0**, dtype
`torch.int64` and CPU device; `_Capture` checks the complete metadata equality
at runtime (`probe_rust_kv_observer.py:205–224,293–308`). Expected metadata is
checked in the executing fixture, not separately serialized. These cases do
not qualify noncontiguous/nonzero-offset tensors. Original/rebuilt/none have
no observer rows; all five normal enabled cases have no invalidations.

The enabled child additionally executes two failure injections, eight
sequentially joined thread invocations, one contended outside getter, two
suspended observer lifetime paths (resume and abort), and an outside-window
case before writing its PASS output (`probe_rust_kv_observer.py:336–435`).
Their evidence is the hash-pinned executed source plus successful child
completion, not individual per-check JSON logs. The contended-getter callback
oracle is the exception now reopened below: isolated callback assertions do
not establish its claimed result. In both lifetime paths, the
native walk keeps the callback alive after Python params/callback deletion
across the Mamba barrier, then releases it on resume completion or end/abort.
No test retains a Python callback tensor through later CUDA completion.

Actual native Rust fixtures, with exact command in `native-fixtures.json`:

```text
cargo test --locked --offline --manifest-path /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-rust-kv-observer-build-20261111/sources/observer/Cargo.toml --target-dir /var/tmp/rust-kv-tests-z6_n6usl/target old_full_observer -- --nocapture
running 2 tests
old_full_observer_precedes_partial_split_and_borrows_original_storage ... ok
old_full_observer_sees_none_before_fresh_restoration ... ok
2 passed; 0 failed; 0 ignored; 0 measured; 943 filtered out; finished in 0.11s
```

The first fixture also retains an original shallow Tensor owner and verifies
its values after the split. The second observes missing FULL before fresh
restoration. Cargo returns **0**; test compilation takes **1m05s**; the temporary
target is not retained. This is **two selected tests**, not the entire Rust suite.

### Dependency bridge, GIL and independent failure marker

All **six** retained dependency files match manifest byte sizes/hashes and all
recorded decisive lines. Cargo.lock and actual build logs identify
`tch/torch-sys 0.24.0` and `pyo3 0.29.2`. Exact implementations inspected:

- `dependencies/tch-0.24.0/src/wrappers/tensor.rs:510–514` and
  `dependencies/torch-sys-0.24.0/libtch/torch_api.cpp:118–121`:
  `shallow_clone` calls `at_shallow_clone`, constructing a shallow C++ Tensor owner.
- `dependencies/tch-0.24.0/src/wrappers/python.rs:15–33` and
  `dependencies/torch-sys-0.24.0/libtch/torch_python.cpp:10–20`:
  wrap uses `THPVariable_Wrap(*t)`; unpack constructs a new Tensor owner from
  `THPVariable_Unpack`. Source ownership plus actual CPU alias/retention tests
  support the tested storage-sharing lifetime, not copying tensor values.
- `dependencies/pyo3-0.29.2/src/marker.rs:562–572` and
  `dependencies/pyo3-0.29.2/src/internal/state.rs:146–182,245–272`:
  detach uses `PyEval_SaveThread`/restore; attach uses `PyGILState_Ensure`/release
  on the current thread. Candidate `python_bindings.rs:1192–1252` detaches
  before native core calls; the inline observer attaches around the callback.

`source-topology.json` lists **130** core-call methods with detach; this is a
**static method count**, not 130 independently executed tests. Its baseline
binding SHA matches the actual retained binding. Selected scheduler loop
source supports serial dispatch, not actual CUDA scheduler-thread execution.
The raw R2 receipt records `contended_outside_getter=PASS`, and the enabled
child completed. **Its oracle is now REOPENED / UNVERIFIED**, distinct from
the preserved static count and same-current-CPU-thread evidence. No separate
named GIL-contrast artifact exists in r2 or is required as a new gate;
arbitrary unscheduled Mutex reentry remains **UNSUPPORTED**, not blanket
race/deadlock freedom.

#### Reopened contended-getter oracle — shared source P2

Both fixed Native Standards and Spec reviews identify the same reachable
false-PASS path at `8683a032`,
`tests/manual/agent_opd/probe_rust_kv_observer.py:385–397`: the temporary
`Capture(expected)` object is discarded by the caller. If callback wait/Mutex
assertions fail, the native bridge isolates their errors in
`_Capture.invalidations`. The caller then checks only getter events/thread
completion, without retaining Capture and asserting observed rows and no
invalidations. A failed callback oracle can therefore coexist with child PASS.
This source defect **does not prove R2 encountered that path** and does not
invalidate the retained 4×5 exact semantics, 40 Insert/44 Match results,
22 source identities, six dependency files, two libraries, two Rust fixtures,
normal CPU aliases/Arc/barrier/abort/missing-FULL/Mamba evidence or stderr marker.

Qualification release is **HOLD** until the owner retains the Capture object,
checks rows and absence of invalidations, and completes the affected actual
GPU0 R3 resume without rebuilding either extension. R3 is not prepared or
submitted at this steering checkpoint. Source130-detach and same CPU thread
remain source/execution facts; they do not substitute for the reopened oracle.

`qualify-observer-enabled.stderr` is **785 bytes**, with exactly one:

```text
old_full_observer_invalidation_failed rid=cpu-rid P=0 E=32 stage=capture
ValueError: injected OLD capture failure
ValueError: injected invalidation failure
```

This marker is in **stderr, not stdout**. Capture-only failure calls invalidate;
capture plus failed invalidate emits the independent marker and preserves
both unraisable errors. Both injected cases assert unchanged partial-split
semantics before the child finishes. Original/rebuilt/none stderr and all four
stdout files are empty. The inspected caller's
`probe_teacher_scoring.py:542–553,574–584` consumes the same marker from its
existing server log and marks affected measurement UNVERIFIED independently
of metadata. **Caller compatibility is source-backed here; an actual collector
server-log injection was not run by this CPU fixture.**

### Local read-only validation and disposition

The verifier used `python3 -B - <<'PY'` from the repository root on host Python
**3.10.6**, with `json.loads`, `ast.parse`/`ast.literal_eval`, file-byte SHA256
and recursive semantic equality assertions. It checked the 22 observer files,
22 baseline manifest pins, 4 final input receipts, 2 actual ELF libraries,
3 submission source pins, 6 dependency files, all 4 variant command/results,
40 Insert/44 Match result field sets, and the exact failure marker. **PASS**.
An initial read-only AST extraction included `_PYTHON_PINS`, whose `_ADAPTER`
name is not a literal; it failed locally with `ValueError: malformed node or
string`. Restricting extraction to the literal `_RUST_PINS` fixed that verifier
error. It is not a native or platform failure and changed no artifact/code.

Compact verified facts, identities, raw references and uncovered cases are in
`evidence/native-rust-kv-observer-qualification-20261111-r2/native-verification.json`.
The first patch could update this report but received EACCES when creating that
JSON: the r2 directory is root-owned mode0755, while the verifier UID is10250.
A noninteractive local `sudo -n /usr/bin/python3 -B` invocation used
`os.open(..., O_WRONLY | O_CREAT | O_EXCL, 0o644)` and `os.fchown(fd,10250,10250)`
to create **only the authorized new empty JSON file**; the patch tool then
filled it. No existing file/directory ownership or permissions were changed.
The first failure remains intact; the successful replay reused the same Rust
sources and libraries. The helper/probe's prior host 23/source-preparation
checks alone are not counted as native PASS evidence.

Historical pre-acceptance read-only delivery check, exact command preserved
without rerun (host Python3.10.6; expected
`PASS: 20 exact CPU cases; 40 Insert / 44 Match results; 31 raw references; preserved first FAIL`):

This historical command read the then-current root finalizer output and the
pre-acceptance status. It is not a current validation recipe. R2 now resolves
the frozen snapshot above; do not rerun this command against a future R3 root.

```bash
python3 -B - <<'PY'
import hashlib, json
from pathlib import Path
t = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
q = t / 'evidence/native-rust-kv-observer-qualification-20261111-r2'
b = t / 'evidence/native-rust-kv-observer-build-20261111'
load = lambda p: json.loads(p.read_text())
v = load(q / 'native-verification.json')
assert v['status'] == 'PASS' and v['primary_acceptance'] == 'PENDING'
assert load(b / 'qualification-command.json')['returncode'] == 1
variants = list(v['source_identity']['variants'])
raw = {name: load(q / f'qualify-{name}.json') for name in variants}
counts = [0, 0]
for name, record in raw.items():
    assert record['library_sha256'] == v['source_identity']['variants'][name]['sha256']
    assert record['environment']['cuda_initialized'] is False
    for case, result in record['cases'].items():
        assert result['semantic'] == raw['original']['cases'][case]['semantic']
        for step in result['semantic']['seed'] + result['semantic']['steps']:
            if step.get('result') is not None:
                assert len(step['result']) == 10
                counts[0] += 1
        for match in result['semantic']['snapshot']['matches']:
            assert len(match) == 13
            counts[1] += 1
assert counts == [40, 44]
refs = v['raw_evidence']
paths = refs['qualification'] + refs['variants'] + refs['native_and_source'] + [refs['build']] + refs['platform']
assert len(paths) == 31 and all((q / p).is_file() for p in paths)
assert hashlib.sha256((b / 'observer-build.json').read_bytes()).hexdigest() == v['source_identity']['final_build_sha256']
print('PASS: 20 exact CPU cases; 40 Insert / 44 Match results; 31 raw references; preserved first FAIL')
PY
```

Observed final check: the exact expected PASS line above, exit0. Both owned
files also passed direct newline/trailing-whitespace checks and JSON parsing;
the scoped `git diff --check -- <report> <native-verification.json>` exited0.
These files are untracked at this checkpoint, so direct content checks, not
the Git diff check alone, establish their formatting. No stage/commit occurred.

At the historical R2 reopened-oracle checkpoint, the raw R2 execution remains **PASS** and the bounded actual serial CPU evidence
remains **primary ACCEPTED**. The contended outside-getter/topology release
oracle is **REOPENED / UNVERIFIED**; fixed Native Standards and Spec reviews
each have the same **OPEN 1 P2**. Full qualification/review release is **HOLD**
pending retained-Capture oracle correction and actual GPU0 R3 no-extension-
rebuild replay. Neither review acceptance nor GPU capture approval is implied. This does not
establish CUDA schedule stream S, physical KV indices/payload/RID binding,
whole-FULL7955 capture, all16/6804 scoring parity, private GPU module SHA,
all-TP coverage, numerical root-cause correction, performance, race freedom,
or either formal200 result. Original binary source commit remains UNVERIFIED.

Historical pre-acceptance read-only phase checkpoint: scoped verification is complete; report/JSON
delivery precedes primary acceptance. D1–D7 are CLEAR within this delegated
window. Branch B/S5: master requirements/plan/progress still describe replay
as not submitted; primary owns their routine status update. No master files,
ticket/scientific criteria, or formal holds were changed by this verifier.

Historical R2 affected-only steering checkpoint: only this report and native-verification
metadata were updated. A single read of the selected frozen snapshot observed
15,835 bytes and the exact R2 SHA above; no source/library sweep, tests, native
execution, platform/auth/GPU operation, permission change, stage or commit was
performed. The next dependent work is the owner's oracle correction and R3
replay; accepted serial evidence and the original first FAIL remain preserved.

## Actual R3 GPU0 CPU replay — retained evidence verification

TaskID: `profile-rust-native-cpu-verification-20261111`. This verifier only read
local retained evidence, source text and Git blobs, updated this report, and
created `evidence/native-rust-kv-observer-qualification-20261111-r3/native-verification.json`.
It did not execute native libraries, Torch, Cargo, compilation, tests, platform
or RJob APIs, authentication, SSH, GPU operations, delegation, staging or commits.
The earlier R2 verification JSON and all raw R1/R2 files remain unchanged.

### Actual terminal, environment and commands

The three exact filtered receipts are
`evidence/rust-kv-observer-cpu-platform-20261111/exp-1111-154156-742418-{submission,terminal,terminal-platform}.json`.
The submission and terminal job/creator agree; the replica's controller owner
UID equals RJob UID `82277179-4014-4a1f-94a2-54ce40b658e5`. The retained platform
receipt reports one `native-cpu` replica/container, requests and limits
**CPU2 / 8000Mi / GPU0**, image165, local NFS
`100.96.128.195:/data/ycfeng:/data/ycfeng`, creator `i-fengyicheng`, and
**Succeeded / Completed / exit0 / restart0**, with empty last state and stop
annotations. Job finish is **2026-11-11T07:44:41Z**; container finish is
**07:44:37Z**. Submission declares codesign, resume and no extension rebuild.
Its H800 positive tag is a template label, not a physical node/GPU claim;
retained replica `node` is null. No fresh live platform query was made here.

The exact submitted shell command is retained verbatim at `submission.json:command`;
it uses `/opt/sglang/bin/python3 -B -c`, changes to this worktree, reads the pinned
R3 config, applies its environment/argv, and executes its script with `runpy`.
The effective configured invocation is:

```text
TMPDIR=/var/tmp CUDA_VISIBLE_DEVICES='' SGLANG_RUST_BUILD_MODE=never CARGO_NET_OFFLINE=true PYTHONDONTWRITEBYTECODE=1 /opt/sglang/bin/python3 -B tests/manual/agent_opd/probe_rust_kv_observer.py resume --root /sgl-workspace/sglang/python/sglang --image artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805 --archive-dir task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-rust-kv-observer-build-20261111 --output task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-rust-kv-observer-qualification-20261111-r3
```

The qualification command returns0; each of four `_exercise` commands returns0.
Their exact resolved argv are in `qualification-command.json` and
`qualify-{original,rebuilt,observer-none,observer-enabled}-command.json` inside
the R3 evidence directory. All four native outputs report Python **3.12.16**,
`/opt/sglang/bin/python3`, Torch **2.14.1+cu130**, CXX11 ABI **true** and
`cuda_initialized=false`; their PIDs are38/42/46/50, respectively. Retained
baseline/observer build receipts identify `rustc 1.99.1 (58cf8f9c3 2026-10-13)`,
production feature `python-extension`, loader force-mode COMPILE+LOAD and the
same runtime module. This is retained build compiler provenance, not a new
R3 compiler-version query or Python-extension rebuild.

### Exact R3 native results and repaired oracle

All **four variants × five cases** (`ordinary`, `partial_split`, `missing_full`,
`end_abort`, `mamba_barrier`) have recursively identical full semantic objects:
actions, result getters, ranges, topology, FULL/Mamba indices and abort/resume
errors. Each also equals the unchanged R2 original baseline. Counts were
derived from actual results, not copied from R2: each variant has **10 Insert
results with10 canonical fields and11 Match results with13 canonical fields**;
totals are **40 Insert / 44 Match results**, across **20 case executions**.

The original module/path is
`sglang.srt.mem_cache.rust_tree_core.mem_cache` at
`/sgl-workspace/sglang/python/sglang/srt/mem_cache/rust_tree_core/mem_cache.cpython-312-x86_64-linux-gnu.so`,
worker-reported SHA `2c1e54965c8139358df1ef2a7751620c339ad1ff4988cee54cc35467a8b90f6c`.
The two retained local ELF libraries remain at their original absolute
`evidence/native-rust-kv-observer-build-20261111/libraries/{baseline,observer}/mem_cache.cpython-312-x86_64-linux-gnu.so`
paths and hash to the previously recorded baseline `fbe6ea7c...124aa` and
observer `0dc763cc...b49ba`. Rebuilt uses baseline; explicit-None and enabled
both use observer. All four actual module names, paths and hashes match the
R3 final build/retained build/resume receipts. Original binary source commit
is still **UNVERIFIED**, not recovered from its successful load/hash.

Enabled normal cases each retain one actual callback row and zero invalidations;
all five rows record native thread50. Fixed `_Capture` checks that thread against
the calling thread and compares data/storage pointers, shape/stride/offset,
dtype/device to the original pre-walk tensor. Partial split captures the original
four indices `[10,11,12,13]`, shape4 and prefix2, not the split copy; missing FULL
captures `None`. Ordinary/end-abort/Mamba capture original `[10,11,12]`.
The executed child also completes the existing suspended-Arc resume and abort
lifetime checks, finish/end release, missing-resume rejection/next insert,
Mamba barrier/eviction, outside-window rejection, two callback-failure
injections and eight sequentially joined thread calls.

The repaired `_contended_getter` retains `capture = Capture(expected)` and forwards
it; after the existing walk/getter join and completion/error checks it requires
`capture.rows and not capture.invalidations` at line399. The exact executed probe
bytes equal the immutable17cb6fc6 Git blob, submission pin and resume fixture pin.
The enabled child returns0 and writes its PASS output only after this check.
Together these establish **PASS for that actually executed contended-getter
oracle**, including callback assertions not being silently invalidated. Its
individual callback rows/events are not separately persisted; none are invented
here. R2's reachable false-PASS defect remains historical and is not proof that
R2 encountered it. PRIMARY reports both source axes independently CLOSED/no new
findings; source29/29, two deterministic invalidating-path controls and three
receipt-routing checks are source-only evidence, not substitutes for this run.

`source-topology.json` is byte-identical to R2 and lists **130** detached core-call
methods. This is static coverage, not130 runtime checks. Actual same-current-CPU-
thread capture and the repaired contended getter support the limited exercised
branch with the same six installed bridge sources described above. Arbitrary
unscheduled Mutex reentry remains **UNSUPPORTED**. No standalone GIL-contrast
artifact exists or becomes a new gate; no blanket race/deadlock claim is made.

The enabled **stderr is785 bytes** and contains exactly one
`old_full_observer_invalidation_failed rid=cpu-rid P=0 E=32 stage=capture`, plus
both `injected OLD capture failure` and `injected invalidation failure` errors.
All four stdout files, original/rebuilt/None stderr and parent qualification
stdout/stderr are empty. The two injections assert unchanged partial-split
semantics. The marker's independent caller source gate stays accepted/source-
backed; this is **not an actual native caller/collector training integration test**.

Actual Rust command and output, from R3 `native-fixtures.json/.stdout/.stderr`:

```text
cargo test --locked --offline --manifest-path /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-rust-kv-observer-build-20261111/sources/observer/Cargo.toml --target-dir /var/tmp/rust-kv-tests-zt5r9pha/target old_full_observer -- --nocapture
test unified_tree_core::tests::old_full_observer_precedes_partial_split_and_borrows_original_storage ... ok
test unified_tree_core::tests::old_full_observer_sees_none_before_fresh_restoration ... ok
test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 943 filtered out; finished in 0.11s
```

Return0 and actual stderr compilation/test-profile output (**1m06s**) corroborate
the two selected fixtures. The worker-local target is recorded
`target_retained=false`; temporary Cargo fixture compilation is **not** a
rebuild/copy/move of either retained Python extension. The six selected dependency
implementations and their manifest are byte-identical to R2 and match their own
recorded sizes, SHA256 and decisive lines. Cargo.lock pins tch/torch-sys0.24.0
and PyO3 0.29.2.

### Identity preservation, readback errors and disposition

The R3 preparation source manifest is45,108 bytes, SHA
`10f581ca97cede3587d90ce51498eacaf2e966b842d51eb22e1e5185c33f553a`.
All its **98 old files match**:65 initial-build files and33 R2 files, including
the R2 verification JSON. Both22-file baseline/observer source maps match actual
bytes; all22 baseline hashes match the fixed helper's owned `_RUST_PINS`.
The two actual retained ELF hashes/workspaces, four retained input receipts and
R3 final qualification identity agree. No5501/621 archive sweep was repeated.
Helper/probe/config current bytes equal their full17cb6fc6 Git blobs, immutable
review artifact and submission pins, respectively:

- helper: `acf89c7425ba38a0a497adfd27cf2fe71979f77922d7af5f6b66a6685175442d`;
- probe: `e8a7944bcf9fbf3601b5d1f4c386bc39d9398cd59cf6627707e600cf3365310c`;
- R3 config: `ad1e1d7f85cf429d86954ba4b1465afa8dc92d7f008859afca8e3c66047fe042`.

R3's own finalizer receipt is
`evidence/native-rust-kv-observer-qualification-20261111-r3/observer-build.json`,
**15,835 bytes**, SHA `91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7`.
The frozen R2 snapshot
`evidence/rust-kv-observer-qualification-receipts-20261111/observer-build-r2.json`
is still **15,835 bytes / SHA4c967246e2cb3ab54e454b87f1a22231c73a7829037dbd98f19ad19bfb2e017b**;
the old root `evidence/native-rust-kv-observer-build-20261111/observer-build.json`
remains byte-identical to it. R2 does not silently follow R3's selected receipt.

Local readback used host **Python3.10.6**, `python3 -B - <<'PY'`, standard-library
JSON/AST/byte hashing, recursive object comparison and read-only `git show
17cb6fc66fa8b5e866c0c83d5f5c93cf971ac898:<pinned-path>` subprocess reads. Expected
checks were98 preserved identities,22 owned pins, two ELF identities, six
dependencies,20 exact cases,40/44 result counts and strict executed oracle;
actual values equal those expectations: **PASS**. No native import/test was made.

PRIMARY reported an initial local platform-inspection `KeyError` from using
normalized `spec.tasks` instead of actual `taskSpecs`, before any receipt write;
the verified API shape was corrected. This verifier also initially looked for
`required_rjob_uid` in the saved submission JSON and got a local `KeyError`;
the saved filtered format instead binds `terminal-platform.uid` to each replica
`owner_references[].uid`. After reading those exact three files, the narrow
metadata check PASSes job/creator/status, owner UID, CPU2/8000Mi/GPU0,
image/mount, Completed/exit0/restart0 and expected R3 receipt. Both errors are
**limited metadata harness issues, not native job failures**; no raw files were
rewritten to repair them. Exact successful metadata command:

```bash
python3 -B - <<'PY'
import hashlib, json, platform
from pathlib import Path
root=Path.cwd(); t=root/'task_memory/task_2026-11-08_qwen35_full_kl_nll'; e=t/'evidence'; q=e/'native-rust-kv-observer-qualification-20261111-r3'; p=e/'rust-kv-observer-cpu-platform-20261111'; job='exp-1111-154156-742418'
read=lambda name:json.loads((p/f'{job}-{name}.json').read_text()); sub=read('submission'); terminal=read('terminal'); live=read('terminal-platform')
assert sub['job']==terminal['job']==live['job']==job and sub['creator']==terminal['creator']==live['creator']=='i-fengyicheng'
assert terminal['status']==live['status'] and terminal['status']['phase']=='Succeeded' and terminal['native_execution_succeeded'] is True
assert sub['expected_build_receipt']==str(q/'observer-build.json') and sub['extension_rebuild'] is False and sub['requested_gpus']==0
assert list(live['tasks'])==['native-cpu']; task=live['tasks']['native-cpu']; assert task['replicas']==1 and task['source_mount']==sub['source_mount']=='100.96.128.195:/data/ycfeng:/data/ycfeng'
container=task['containers'][0]; assert len(task['containers'])==1 and container['image']==sub['image']
limits={'cpu':'2','memory':'8000Mi','nvidia.com/gpu':'0'}; assert container['resources']=={'limits':limits,'requests':limits}
assert len(live['replicas'])==1; replica=live['replicas'][0]; owner=replica['owner_references'][0]; assert owner['uid']==live['uid'] and owner['name']==job and owner['kind']=='RJob' and owner['controller'] is True
assert replica['phase']=='Succeeded' and replica['node'] is None and len(replica['containers'])==1; state=replica['containers'][0]; stopped=state['state']['terminated']; assert stopped['reason']=='Completed' and stopped['exitCode']==0 and state['restart_count']==0 and state['last_state']=={}
print('PASS actual saved filtered shapes: matching job/creator/status; owner UID',live['uid'],'CPU2/8000Mi/GPU0; pinned image/source mount; Completed exit0/restart0')
print('TIMES job finish',terminal['status']['finishTime'],'container finish',stopped['finishedAt'])
print('PLATFORM',json.dumps({'creator':live['creator'],'owner_uid':live['uid'],'replica_uid':replica['uid'],'container_id':stopped['containerID'],'source_mount':task['source_mount'],'charged_group_submission':sub['charged_group'],'positive_tags_submission':sub['positive_tags']}))
for suffix in ['submission','terminal','terminal-platform']:
 f=p/f'{job}-{suffix}.json'; print('RECEIPT',f.name,len(f.read_bytes()),hashlib.sha256(f.read_bytes()).hexdigest())
f=e/'rust-kv-observer-qualification-preparation-20261111-r3/source-manifest.json'; print('PREP_MANIFEST',len(f.read_bytes()),hashlib.sha256(f.read_bytes()).hexdigest())
print('R3_DIRECTORY',oct(q.stat().st_mode & 0o777),'owner',q.stat().st_uid,'host Python',platform.python_version())
PY
```

**Disposition: actual bounded R3 serial CPU qualification PASS; primary
ACCEPTED for the executed serial CPU scenarios and repaired contended-getter
oracle only (2026-11-11, fixed source17cb6fc6).** The repaired oracle is verified
for this executed branch, while both source-axis P2 closures are PRIMARY-reported
source-only. Source/class/CPP witness and existing all16 acceptance are not reset.
Original binary source commit; actual CUDA S/thread/stream/payload and private
GPU module origin; whole-FULL7955 physical/RID capture; all16-6804/all-TP numeric
coverage; arbitrary unscheduled Mutex reentry/race freedom; rootfix/performance;
and formal200 remain unverified or unsupported as before. No H800 numerical or
formal acceptance follows from this CPU disposition. Bounded diagnostic authority
is separately recorded in D40; formal submissions remain held.
Affected-only phase checkpoint: this delegated verification is complete; primary
owns acceptance, source-review archive/registry/collector/master records and
any next H800 preparation. No new GIL artifact gate or wider test was introduced.

The R3 directory is root-owned0755. Noninteractive local exact-file creation
used `sudo -n /usr/bin/python3 -B`, `os.open` with `O_CREAT | O_EXCL`, and
`os.fchown` on **only the authorized new empty verification JSON**; the patch
tool then filled it. No existing file/directory owner or permission changed.
Final owned-metadata/format check: JSON parses, dependency hash literals match
the retained manifest, primary remains PENDING, strict R3 oracle remains PASS,
both files have final newlines/no trailing whitespace, and **30 raw references**
plus selected snapshot/prep/source references resolve: **PASS**. This check read
metadata only and did not rehash raw/source/library files or execute any test.
The earlier verifier check recorded primary PENDING before the primary decision.
The primary then inspected this report, the R3 verification JSON, actual
qualification receipt and fixed oracle and accepted the bounded CPU evidence.
Commit9c2a0a95 already synchronized source P2 closure and R3 terminal success;
the subsequent primary acceptance and selected-receipt linkage are routine
master-record updates, not additional native qualification gates.
