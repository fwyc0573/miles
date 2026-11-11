## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Link primary-accepted bounded R3 native CPU qualification through the sole config input;283 affected/joined CPU checks and both unchanged four-H800 controller dry-runs PASS. Actual CUDA/numerical acceptance remains pending. |
| 2026-11-11 | Record the closed Standards recheck and actual A/B CPU controller dry-runs; preserve the reopened native contention oracle and R3 release hold. |
| 2026-11-11 | Close the frozen407 Standards P3 constant-ownership Nit with opt-in imports only;25 affected and254 joined CPU checks PASS. Preserve historical407 and distinguish primary-reported zero-GPU build/load PASS from still-pending replay/GIL/H800/numeric qualification. |
| 2026-11-11 | Correct real native shared-root prerequisite with one whole private runtime copy before transitive SGLang imports; add independent native stderr-marker rejection;407 final CPU checks pass, compiled/native GPU proof pending. |
| 2026-11-11 | Record CPU collector/source/probe preparation,380 composed-overlay and246 final affected passing checks, explicit source-only DI, compact drain correction, and pending production-native/GPU qualification. |

# KV coherence collector preparation — CPU phase only

TaskID: `profile-kv-coherence-collector-implementation-20261111`.

## Outcome and limits

**CPU/source preparation PASS; bounded production-native R3 serial CPU qualification primary ACCEPTED; actual CUDA capture and numerical acceptance PENDING.** The original collector implementation subtask performed no platform, authentication, API, SSH, GPU worker, Docker or Torch CUDA operation. Its original Source621/Source5501 evidence, parallel Rust builder's files, shared records and README were left unchanged. The separately executed native CPU prerequisite and primary disposition are owned by the [canonical native CPU report](test_report_2026-11-11_rust_native_cpu_qualification.md#actual-r3-gpu0-cpu-replay--retained-evidence-verification), not the collector's source DI.

The accepted `9d1d821f` source/provenance and `1d694444` selected CPP/WIT scope remain independent evidence. This task does not reinterpret either as a bundled native binary's source commit, original-tensor observer execution, CUDA stream proof or physical/numeric acceptance. Selected CPP WIT remains accepted; unselected prefix-valid Triton stays unverified and unsupported by this collector. A future CPP compilation qualification is not relabeled as a blocker of the previously accepted WIT. Warm FAIL and formal A/B HOLD remain unchanged.

### Primary follow-up: source review and CPU controller checks

The collector Spec review reported No findings. Its Standards recheck closed the sole constant-ownership Nit and reported no new findings. Both Rust observer source rechecks closed the repaired contention-oracle P2 at17cb6fc6 with no new findings. Primary then accepted the independently verified actual R3 serial CPU scenarios, including the repaired executed oracle, while preserving the R2 raw evidence and unchanged compiled libraries. These bounded CPU/source dispositions are not native CUDA/numerical acceptance.

The single `kv_coherence_build_receipt` input in [the diagnostic config](teacher_scoring_kv_coherence_probe_config.json) now selects the R3 finalizer receipt, not the earlier R2 build-root receipt. The [linked controller comparison](evidence/teacher-scoring-kv-coherence-probe-20261111/controller-dryrun-comparison-r3-linked.json) verifies that selection, the primary CPU disposition, the unchanged R2 hash, and both four-H800 dry-runs. It preserves all prior dry-run files rather than overwriting them.

Actual controller dry-runs used system Python 3.10.6 from the worktree, without authentication or platform submission:

```bash
python3 -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_coherence_probe_config.json --pair A --receipt task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/admission-A-r1.json --dry-run > /data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-controller-A-dryrun-20261111.json
python3 -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_coherence_probe_config.json --pair B --receipt task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/admission-B-r1.json --dry-run > /data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-controller-B-dryrun-20261111.json
```

Expected and observed: both returned `submitted=false`, requesting four H800 GPUs each in `codesign`. Direct JSON comparisons with `kv-stream-witness-controller-{A,B}-20261111.json` passed for `tasks`, `mounts`, `image`, `source_directory`, and `envs`. Parsing each worker command with `shlex.split` and replacing only the `--config` and `--output-dir` values produced identical token sequences. No allocation, mount, image, environment, timeout, or other worker-command change was observed.

The latest outputs are `controller-dryrun-{A,B}-r3-linked.json` and `controller-dryrun-comparison-r3-linked.json` in [the coherence diagnostic evidence directory](evidence/teacher-scoring-kv-coherence-probe-20261111/). Their temporary command outputs were `/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-r3-controller-{A,B}-dryrun-20261111.json`. These controller checks did not invoke the real native preparer or establish CUDA/private-module origin, physical index equality,7955 OLD rows,6804 native logprobs, a root-cause fix, or formal readiness. Neither H800 diagnostic had been submitted at this preparation checkpoint.

After linking the R3 receipt, the existing collector, probe and native-source/orchestration suites passed **283/283**, zero skips/failures, four unchanged warnings,30.03s (Python3.12.13, pytest9.1.1). This checks the changed acceptance/configuration paths; it neither repeats nor replaces the actual native CPU run or the historical407 composed-overlay result.

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_sglang_kv_coherence.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_sglang_rust_kv_observer.py -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-r3-receipt-linked-20261111
```

Counts are30 collector,224 probe,29 native CPU/source checks. Hardware-rejection cases mentioning H200 are CPU-only argument tests; no H200 job or CUDA execution occurred.

Python3.10 grammar, source whitespace and fixed reviewed probe/test byte hashes also PASS. The first all-artifact cached whitespace check flagged blank context lines in the retained `cpu-source-di-r3/coherence.diff`: a unified diff encodes those lines with a single space. Preserve that raw diff verbatim. Cached code/document/config whitespace checks excluding only that exact raw diff then PASS; no source or serving behavior was changed to silence the artifact-format warning.

## Deliverables

### Narrow Standards follow-up: constant ownership — CPU PASS

TaskID remains `profile-kv-coherence-collector-implementation-20261111`. The primary reported frozen407 Spec review No Findings and one Standards Nit/P3. This follow-up edits **only** `tests/manual/agent_opd/probe_teacher_scoring.py`, `tests/fast/test_teacher_scoring_probe.py`, and this report. The earlier407 results, build/load-pending statements at that historical source phase, source artifacts and original design records are preserved.

The probe now imports existing `SCORING_REQUEST_COUNT` only inside the `kv_coherence_capture` branch of `_collect_runtime_metadata`; `_coherence_states`, called only for opt-in, imports the existing `WINDOW_START`, `WINDOW_END`, `CANDIDATE_INPUT_COUNT`, `BANK_COUNT`, `SCORING_REQUEST_COUNT` alongside `covered_once`. Existing numeric predicates, `WINDOW_START + old_rows`, and fragment coverage endpoints use those constants. Sample index1695, sample position2, repetition0, and the distinct7955 original OLD warm-target constraint remain exact; `BANK_COUNT` is not substituted for sample position. No helper, capture/runtime injection, marker, bank selector, config, payload, argv, science, registry, flag or dataclass change was made.

The test DI module borrows the real owner's request-count constant; its existing import guard still fails any False/absent collector import. True performs one additional cached local constant import, reflected in the expected import count, not another preparation call. One proportional AST regression verifies local opt-in import ownership, removal of duplicated numeric predicates, and preservation of the distinct sample/OLD-target literals. The existing17 coherence cases preserve all independent RID/physical/native-error gates, including a complete-looking bank with native invalidation failure and all16 score files retained.

**Affected check —25 PASS,0 skip/FAIL,4 unchanged warnings,1.98s:**17 existing coherence cases (6 lifecycle,9 schema/identity/physical faults,2 dry argv),7 baseline/WIT import cases, and1 new constant-wiring regression. False/absent still imports no collector; baseline56 scoring/32 flush and diagnostic16/10 remain exact.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py::test_coherence_true_only_preparation_after_wit_and_after_all16_error_independence tests/fast/test_teacher_scoring_probe.py::test_coherence_schema_joins_only_native_response_identity_and_actual_old_coverage tests/fast/test_teacher_scoring_probe.py::test_coherence_variant_existing_controller_dry_run_and_unchanged_native_argv tests/fast/test_teacher_scoring_probe.py::test_coherence_numeric_predicates_reuse_opt_in_constants tests/fast/test_teacher_scoring_probe.py::test_kv_stream_witness_api_binding_order_and_baseline_artifacts_with_injected_preparers -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-constants-nit-20261111
```

**Joined changed acceptance paths —254 PASS,0 skip/FAIL,4 unchanged warnings,24.83s:** unchanged collector30 and probe224. This is not a rerun or replacement of historical407, and no408/native/GPU PASS is asserted.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_sglang_kv_coherence.py tests/fast/test_teacher_scoring_probe.py -q --tb=short --durations=5 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-constants-nit-joined-20261111
```

Final Python3.10 AST/no-trailing-whitespace checks passed. Normalizing **only** the five imported names back to their existing owner values and removing those added imports yields exact entire-probe AST equality against `/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-source-review-407-20261111/candidate/tests/manual/agent_opd/probe_teacher_scoring.py`, including every untouched branch, message and independent check. The final cosmetic restoration of the pre-existing continuation indentation changes no AST and does not expand scope. Scoped `git diff --check` also passes.

| Code file | Frozen407 SHA256 | Final SHA256 | Narrow delta |
| --- | --- | --- | --- |
| `tests/manual/agent_opd/probe_teacher_scoring.py` | `d7ca7591bbc641159a7c04fc81463379c3297eb481a56e00d29bfbbaa2fad606` | `45715a95212cc034c0b19e363ba380de457778df48453a521d8f973b1e354601` | +15/-11 lines, constant imports/substitutions only |
| `tests/fast/test_teacher_scoring_probe.py` | `86b62f71056e4c9e57a97f707650b14d56a2b6d39a04dce0797bd4e6113268a2` | `655abf07fafbec57bf07563e89453a62c2fd3f88c589c6e513e9e8151fb38ff6` | +32/-1 lines, DI constant/import-count update and one AST regression |

**Current native status comes from the primary, not this follow-up:** zero-GPU actual compilation and load PASS were reported; qualification still awaits replay and no7955/H800/model/GIL acceptance is granted. The primary's fixed23 source-fixture/resume checks and submitted CPU replay are independent, not blockers for this Nit and not run/polled here. No native helper/API/source/test files, shared docs or config were edited. The joined collector suite includes its unchanged CPU-only PENDING-receipt API rejection, not a native build/load/replay or GPU qualification. No platform, GPU, auth or delegation operation, stage or commit was performed. A fixed Standards recheck remains the primary's next action.

Self-check: the sole finding is closed within the three-file ownership; verification stops after affected and joined checks pass. No tooling side quest, new scientific predicate, native acceptance shortcut or dependency on pending replay was added.

| Path | Result |
| --- | --- |
| `tests/manual/agent_opd/sglang_kv_coherence.py` | Real-pool-derived two-bank FULL K/V collector; preallocated int64 writer/FULL-insert/OLD/rebind receipts; whole private package copy and ordinary import binding; fixed real native preparer composition; source pins; one-shot compact drain; independent offline completion-vector gate. |
| `tests/fast/test_sglang_kv_coherence.py` | 30 CPU tests: prior collector/source/vector contracts plus fresh-process whole-package/child import, symlink isolation, already-imported rejection, real native PENDING gate on private root, and actual transitive import ordering. |
| `tests/manual/agent_opd/probe_teacher_scoring.py` | True-only coherence preparation after FP32 -> metadata -> KV WIT and before runtime/Teacher; required build-receipt input; inherited wrapper opt-out; original unsalted first4/one-repeat workload; one final true drain; schema/native-RID join; diagnostic failure preserves scores. |
| `tests/fast/test_teacher_scoring_probe.py` | 223 tests total, including coherence dependencies/False/absent/direct-formal ownership, private selected root/preparation order, after-all16 marker, independent complete-looking-bank/native-error rejection, schema/physical/checkpoint/fragment fields, response-RID phase association and unchanged-argv dry constructions. |
| `teacher_scoring_kv_coherence_probe_config.json` | Isolated A/B variant of the existing WIT configuration. Only task/output/acceptance labels, `kv_coherence_capture=true` and required `kv_coherence_build_receipt` are added/changed. No artifact-directory, backend, dtype, scientific, payload, cache-salt, concurrency or synchronization flag is introduced. |
| `evidence/kv-coherence-source-20261111/prepare_cpu_source_di.py` | Explicit standalone CPU source DI driver; no fake .so, native build, native load or serving fallback. |
| `evidence/kv-coherence-source-20261111/cpu-source-di-r3/` | Latest dry composition `receipt.json`, `source_manifest.json`, `coherence.diff`, `preflight.jsonl`. `cpu-source-di-r1/r2` are earlier CPU-only iterations, not current production proof or serving import attestations. |

The production native API is imported separately, called once, and its receipt is preserved verbatim under `native_observer`:

```python
sglang_rust_kv_observer.prepare_source(root, image=image,
                                     archive_dir=archive_dir / "native_observer",
                                     build_receipt=build_receipt)
```

The probe resolves the explicit `kv_coherence_build_receipt` from the diagnostic config; the current selection is the primary-qualified R3 receipt linked above. The real `sglang_rust_kv_observer.py` API is consumed without a provisional module, fake serving fallback or weakened root/ABI guard. An actual joined caller test invokes that real API once on the selected private root and is correctly blocked by a deliberately `PENDING` test receipt, before a runtime module/native binary is loaded. The dry source driver still deliberately injects native preparation solely for AST/source composition: its nested receipt explicitly says `CPU_SOURCE_DI_ONLY`, build/load/GPU pending and `no_fake_binary=true`. Neither DI nor a fail-closed real-API test is compiled native qualification.

## Private runtime/import and native-error correction

The real native API rejects `root == build_receipt.original.package_root`; that absolute baseline path is shared across CPU/GPU image layouts. Its guard is unchanged. `prepare_package(root, worker_tmpdir=...)` copies the **whole runtime SGLang package**, not a35-file verifier subset, into one fresh worker-local temporary directory under the existing `worker_local_root`. Source symlinks are dereferenced so staging a library cannot write through to baseline. It rejects every prior SGLang namespace import, binds normal parent `sys.path` and child `PYTHONPATH` once, and verifies ordinary `find_spec("sglang")` selects the private package. No module purge/reload, backend flag, inspection module or alternate .so loader is added.

Decisive inspected import chain: `qwen35_pair_worker.py:23 -> scripts/run_glm47_flash_agent_opd.py:30 -> sglang.srt.environ`; `run_qwen35_opd.py:48` also imports that training script. Binding only after `_worker_environment()`/`_load_config()` would therefore be too late. The probe now resolves the existing config flags/merge with the pure `_config_input()` function, makes/binds the private copy **before those runtime/config helper imports**, then uses unchanged validation/registries and worker environment. Only true enters this route; False/absent performs no private copy or path binding.

Order: **pure config selection -> fresh whole private package/binding -> existing config/runtime helper imports -> FP32 -> metadata -> KV WIT -> real native prepare once -> collector Python patches -> runtime source inspection -> ordinary unchanged teacher command**. All preparers use the private root. The native receipt's private `package_root` is preserved verbatim nested and checked against the selected root; the caller retains the package receipt and rechecks ordinary root selection before runtime/Teacher. `-m sglang.launch_server` inherits that package's `PYTHONPATH`; all existing engine argv/payload/scientific parameters remain unchanged. The temporary copy stays alive through server termination, log/result preservation and normal cleanup. Baseline files and raw source archives remain untouched by this selected route.

CPU proofs use clean subprocesses because the repository `tests/conftest.py` already imports SGLang. They never purge that namespace. A whole-package fixture includes a module absent from every collector manifest and a source symlink: the real copy includes the extra module, does not preserve the write-through link, and the actual ordinary Python child imports from the private copy while original bytes remain exact. A second fresh-process test intercepts the real first transitive SGLang import **only as a CPU test**, verifies the private ordinary root/path before it happens, then stops before SGLang execution. Production installs no import hook. Main lifecycle tests remain explicitly DI/mock runtime/server tests; their package copy is made through the real helper in a clean CPU child, not evidence that the host's pre-imported test namespace was rebound.

The caller also consumes the native owner's stable error-only marker `old_full_observer_invalidation_failed` through the delivered module's `INVALIDATION_ERROR_MARKER` constant, not a second protocol definition. After all16 scored responses, it scans the existing combined `server.log` once and retains exact matching line numbers/text. A matching marker makes the diagnostic `FAIL/UNVERIFIED` independently of complete-looking coverage/index/equality masks, while leaving serving and all score artifacts intact. No global unraisable hook, logger thread, mutex, collective, fallback or new wait is installed. Missing log evidence cannot pass; marker absence remains only absence of an observed error, not alias/GIL/CUDA qualification. The full existing log archive retains both PyErr details. The native-marker fault test preserves16 completion-score files and verifies a `captured`/all-true bank still cannot reach numeric interpretation.

**CPU prerequisite closed:** primary-accepted bounded R3 qualification owns the real compiled artifact and executed alias/lifetime/thread/contended-getter evidence. **Still pending:** the actual server's effective private module origin/SHA and new-library CUDA capture. Ordinary CPU import-path proofs and staged/preflight hashes do not assert that those GPU gates passed; arbitrary unscheduled Mutex reentry and blanket GIL/race safety are not claimed.

## Source seams, schema and allocation

The preparer qualifies **35 complete original file identities**, reverses the previously qualified FP32/metadata/WIT overlays, preserves those overlays, then checks full-file hashes and exact new seams. Its own patch changes **11 paths**: ten existing Python files plus generated `srt/kv_coherence.py`. Of those ten, **four are required new native RPC plumbing**, not presumed existing support: `srt/entrypoints/http_server.py`, `srt/managers/tokenizer_control_mixin.py`, `srt/managers/io_struct.py`, `srt/managers/scheduler_components/internal_state.py`. The native owner's adapter/binary/Rust edits are separate from this count.

- The real `checkpoint_into_tree()` retains the FULL `InsertParams` constructor and every original argument. After its real `insert_params.value = values` assignment and before `insert()`, freeze the FULL int64 window; never use `mamba_value`. Attach `(collector, rid, P, E)` only for a selected opaque bank.
- Register two unique opaque RIDs using the design's exact host candidate predicates before OLD decisions. No phase, sample UID, bank order or Q is used to select a bank. Phase attribution is performed only after all responses, through actual response/meta/completion native RID identity.
- FRESH runs just after original CPP store on the same producer F and before free, across all actual FULL layers. It uses published ForwardContext host RIDs/prefix/extend lengths and cumulative flattened request offsets. Unsupported prefix-valid Triton marks diagnostic invalid, without deriving commit length from capacity or pretending a CPP scalar proves that terminal.
- OLD callable has the fixed seven arguments and CPU-only `invalidate(rid,P,E,stage,message)` interface. It takes the original native node tensor before clone/split/free; intersects only native cursor/prefix with `[P,E)`, copies original locations and both full K/V sides, and records original tensor pointer/shape/stride/dtype/device, CPU thread and Torch current-S scalar. It never traverses a tree, reacquires a cache lock or selects by Q.
- Index qualification independently compares every layer's writer versus real FULL insert, original OLD versus canonical rebind, and the rebind fresh suffix versus insert. OLD fragments must cover `[P,Q)` once; cold OLD remains absent, never zero-filled evidence. Runtime topology comes from actual HybridLinear/MHA buffers, FULL global-to-dense mapping, shape, dtype and bytes.

For `P=90112`, `E=98304`, `R=8192` and the observed BF16 local row size of512 bytes per K or V:

| Pair | FULL layers | Two-bank two-sided K/V | Int64 receipts `2*(L+3)*8192*8` | Total |
| --- | --- | --- | --- | --- |
| A | 16 | 512 MiB | 2.375 MiB | 514.375 MiB |
| B | 10 | 320 MiB | 1.625 MiB | 321.625 MiB |

These are descriptor-derived budget expectations, not allocations measured on GPU. Persistent CPU budget tests use synthetic actual-shape descriptors. Allocation occurs after finalized pool backing, before requests, on responding TP0 only. Other TP ranks are inactive; no gather is added. Unsupported allocator/page/graph/topology settings or allocation exhaustion produce explicit diagnostic invalidation, without silently reducing capture coverage or changing serving.

`kv-coherence-v1` contains topology/budget scalars, opaque banks, CPU insert/rebind/fragment descriptors, distinct completed RIDs, physical equality/bounds/coverage booleans, compact per-layer K/V extrema/count summaries and an explicit uninterpreted status. No raw K/V or int64 arrays are returned. Error/default receipts retain CPU-only bank metadata. Summary is cached and transient bank payload/index tensors are released after the final drain.

## Canonical drain correction

The earlier raw-retention steering was withdrawn and its implementation removed before any native submission. There is **no large raw archive, cloud/NFS tensor dump, tensor `tolist()`/base64 JSON payload, new `kv_coherence_artifact_dir`, or extra native prepare argument**.

`kv_coherence_drain: bool=False` is forwarded over the four actual source-bound RPC files. Startup/default readback does not perform D2H. The caller first verifies16 distinct successful scoring RIDs, then issues exactly one extra existing `/get_server_info?kv_coherence_drain=true` readback. The responding scheduler independently verifies16 distinct completed scoring RIDs before any content read. The returned RID set must equal the actual response set. No second RID-list transport protocol is added.

Only then may the existing native ordering permit standard layerwise D2H and CPU float32 comparison; no explicit wait/event/synchronization/record_stream, post-free fresh-slot read or critical-path logging is introduced. Raw BF16 GPU banks are not reinterpreted in-place. Only selected compact metrics/logs/source receipts are retained locally; no cloud access/write was performed. Diagnostic HTTP/schema/coverage/auxiliary errors mark evidence invalid and preserve `requests.jsonl`, completion-score files, comparisons and native score accounting.

## Verification

Environment: workspace `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`; executable `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`; Python3.12.13; Torch2.11.0+cu130, used only with CPU tensors. No conda environment was activated. Python3.10 syntax is verified separately by AST parsing, not by claiming a3.10 runtime execution.

### Earlier composed-overlay regression — PASS (historical CPU phase)

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_sglang_kv_coherence.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_sglang_kv_streams.py tests/fast/test_sglang_mamba_runtime_metadata.py tests/fast/test_sglang_mamba_snapshots.py -q --tb=short --durations=5 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-overlay-regression-20261111
```

Expected: all selected CPU checks pass, no skip, native/GPU status not promoted. Actual: **380 passed,0 skipped,0 failed,4 unchanged warnings,45.60s**: collector24, probe219, WIT62, metadata50, snapshots25. Existing SWIG and `datetime.utcnow()` deprecation warnings were retained; the shutdown `swigvarlink` warning remains unrelated. Earlier iteration totals17/234/239 were CPU-only, superseded by this final run.

### Earlier affected regression after schema hardening — PASS (historical CPU phase)

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_sglang_kv_coherence.py tests/fast/test_teacher_scoring_probe.py -q --tb=short --durations=5 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-schema-final-20261111
```

Expected/actual: **246 passed,0 skipped,0 failed,4 unchanged warnings,15.28s**: collector24 and probe222. Missing independent physical equality fields, wrong checkpoint RID/P/E/Q and missing original fragment coverage now fail explicitly even if a malformed producer claims `status=captured`. Source collector and previously passing unchanged WIT/metadata/snapshot modules were not modified after the380-check run; only the affected two files/tests were rerun. Final3.10 AST/config parsing also passed.

### Final private-root/native-error composed regression — PASS

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_sglang_kv_coherence.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_sglang_rust_kv_observer.py tests/fast/test_sglang_kv_streams.py tests/fast/test_sglang_mamba_runtime_metadata.py tests/fast/test_sglang_mamba_snapshots.py -q --tb=short --durations=5 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-private-overlay-final-r2-20261111
```

Expected/actual: **407 passed,0 skipped,0 failed,4 unchanged warnings,73.91s**, host shell timeout120s. Counts: collector30, probe223, native-source/preflight17, WIT62, metadata50, snapshots25. Native-source tests are not a compiled/native execution receipt. Immediate affected run: **253 passed,4 warnings,31.43s** using the first two files and `--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-private-second-20261111`.

Preserved unsuccessful attempts: the first private-root test run had **6 failed/246 passed** because conftest's loaded SGLang namespace correctly triggered the new guard; no purge was used. A fresh import audit stopped before SGLang and identified the real script chain above. A direct two-test retry also failed for the same conftest contamination, confirming the need for fresh-process tests, not a weaker guard. After the correction,253 passed. The first407-test combined attempt at `--basetemp=.../kv-coherence-private-overlay-final-20261111` then exceeded the60s shell limit after caller/native-source/WIT completed; it is an interrupted run, not PASS. The same checks on a fresh basetemp with120s host timeout produced the full407 result. No serving/request timeout, concurrency or scientific parameter changed.

After407 passed, the only code change was replacing the caller's marker literal with the actual native module's shared constant, preserving its string and behavior. The affected opt-in/opt-out/missing/malformed/native-error lifecycle cases then passed **6/6,4 unchanged warnings,1.75s**:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py::test_coherence_true_only_preparation_after_wit_and_after_all16_error_independence -q --tb=short -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-native-marker-constant-r2-20261111
```

An initial targeted command also named nonexistent `::test_native_observer_failure_marker_and_missing_log_do_not_pass`; pytest exited4 at collection and executed no tests. The corrected command above covers the actual existing marker fault case; the collection error is not a source failure or PASS. After the constant change, all five owned Python files again passed `ast.parse(..., feature_version=(3,10))` and no-trailing-whitespace checks; config JSON parsing and scoped `git diff --check` also passed. These are syntax/source checks, not image execution.

### Latest explicit dry source composition — PASS, DI ONLY

```bash
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/kv-coherence-source-20261111/prepare_cpu_source_di.py --source task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source --output task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/kv-coherence-source-20261111/cpu-source-di-r3
```

Expected/actual: one native DI call; full source pin/seam/after-write readback and Python compilation pass; stdout `CPU_SOURCE_DI_ONLY ... production native/GPU qualification PENDING`;35 identity manifest entries and11 own changed files. This command neither builds nor loads a native binary. Temporary copies use `/data/ycfeng/tmp/opencode-v2-tmp/opencode`; final selected evidence is the small source receipt/diff, not tensor payload.

### Syntax/config/diff — PASS; optional lint unavailable

- `ast.parse(Path(path).read_text(), feature_version=(3,10))` passed for the collector, probe, both owned fast test files and CPU DI driver; `json.loads()` passed for the isolated config. Source tests additionally parse all emitted changed native Python sources with3.10 grammar.
- `git diff --check -- tests/manual/agent_opd/sglang_kv_coherence.py tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_sglang_kv_coherence.py tests/fast/test_teacher_scoring_probe.py task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_coherence_probe_config.json task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/kv-coherence-source-20261111` returned0, no output.
- `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m ruff check tests/manual/agent_opd/sglang_kv_coherence.py tests/fast/test_sglang_kv_coherence.py` could not execute: `No module named ruff`. No dependency was installed. This is an unavailable lint check, not a test PASS or runtime defect.

CPU faults cover preallocation exhaustion, inactive other-TP behavior, missing original FULL, duplicate OLD spans, stream mismatch, unsupported Triton, third eligible bank, ambiguous rebind, missing build receipt, unknown pinned source, missing/malformed drain schema and response/completion RID mismatch. Early/default drain tests replace `Tensor.cpu` with a throwing function and still reject before contents are read. Tests bind actual transformed HTTP/control/request/internal-state source methods; injected scalar/thread values are not native CUDA stream/GIL proof.

The offline `compare_completion_vectors(output, baseline)` gate reuses the existing probe `_comparison` exactly, requires the same16 logical successful cases and6804 values in both outputs, and reports exact/token/finite/maxabs/maxrel/zero-reference-undefined results. CPU fault tests change values, token IDs or counts and cannot pass. Even a passing vector gate leaves source/thread/stream/physical qualification explicitly pending; no tolerance or scaling factor is introduced.

## Remaining acceptance gates

1. The bounded production CPU prerequisite and R3 receipt selection are closed as linked above. Confirm actual server private module origin/new-library SHA and scheduler/callback CUDA thread/stream, and independently reject retained native invalidation-failure markers. This task's DI/fresh CPU import-path/PENDING API rejection is not that GPU proof.
2. Primary-only future approved actual A/B runs: original first4/one-repeat16 scores/10 flushes; original56/32 path unchanged; all16 baseline vectors/6804 values and original comparison records exactly reproduced. Verify actual responding TP0 allocator/page/graphs/FULL descriptors, CPP stream/terminal evidence and original native S/F dependencies with no new wait.
3. Require all FULL writer/FULL-insert and original-OLD/rebind independent indices/bounds, full8192 FRESH coverage including7955 OLD+237 suffix, warm7955 OLD per layer and actual absent cold OLD. Unknown terminal/coverage/source/stream evidence stays unverified, not equality.
4. Only after those gates interpret compact layerwise K/V results. Do not infer race exclusion, historical cause, SSM validity, repair, performance, all-TP coverage or formal A/B readiness. No actual capture/numeric run was done in this task.

## Phase checkpoint — scoped self-check

### 1. 规划完成情况

**汇总：** PASS3｜BLOCKED1｜TODO1。CPU collector/source preparation、probe/RPC preparation、CPU verification 已完成；production native qualification 由并行 owner 负责且本任务未消费；actual CUDA/numeric qualification 未执行。

### 2. 偏离检测

**结论：** D7 原始大块归档偏离已纠正；当前正常推进。窗口为本次 CPU 实现；当前前沿为交付 CPU 证据并等待 production native/GPU qualification。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 测试仅增加用户指定的 private import 与 independent native-marker 验收；407通过后停止扩展。 |
| D2 细节反复重试 | CLEAR | 两次 guard 失败定位到 conftest 与真实 early-import 链，fresh-process 纠正后253/407通过；60s联合超时只增加 host-test预算。 |
| D3 支线问题修补 | CLEAR | 未触及其他 owner、原始证据或正式训练路径。 |
| D4 可并行任务停滞 | CLEAR | Rust builder 与 collector ownership 独立；用户禁止本子任务进一步 delegation/platform 操作。 |
| D5 超范围镀金 | CLEAR | 无新原始数据归档、额外 artifact flag、协议框架或 fallback。 |
| D6 分析空转 | CLEAR | 已产生代码、配置、CPU 测试和 source DI 交付。 |
| D7 路线违背 | HIT，已关闭 | 曾按已撤回 steering 添加 raw archive；已按 canonical design139–147 删除，未运行 native/GPU/archive。 |

**文档检查：** S1–S6 当前无明显缺陷；master requirements/plan 当前 active frontier 明确 compact summaries 与 CPU-only qualification。归因为已撤回的 steering；不更改 canonical scope 或 master docs。

### 3. 纠正建议

**分支：** A。raw archive、artifact-only flag、shared-baseline staging、late path-only binding 与把 DI 当作 native PASS 的行为均不允许；已修正实际 early-import 路径并加入独立 marker gate。下一步由 primary 消费 compiled native receipt、review，再执行独立授权的原16请求物理/数值资格验证。完成标志是上列实际证据，不是407 CPU PASS。

### 4. 最值得关注的 3 点

1. 407联合 CPU PASS 只证明 preparation/import/error 合同；compiled native/GPU 证据未执行。
2. private package 在真实 transitive import 前绑定；native error marker 独立否决完整 bank。四文件 drain仍默认/早读CPU-only，无 raw archive。
3. all16/6804 exact、7955 OLD 和独立三组物理 index equality 均未因 CPU 成功而放宽；warm FAIL/formal HOLD 保留。
