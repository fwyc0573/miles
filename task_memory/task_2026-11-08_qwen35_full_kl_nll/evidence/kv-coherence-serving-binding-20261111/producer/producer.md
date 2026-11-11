## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Deliver one-shot serving-binding identity producer and focused CPU/source evidence; leave consumer/native acceptance and existing reports untouched. |

# Serving binding producer — CPU source delivery

TaskID: `profile-kv-coherence-serving-binding-producer-20261111`.

## Outcome and actual seam

Only `tests/manual/agent_opd/sglang_kv_coherence.py` and `tests/fast/test_sglang_kv_coherence.py` are edited. New selected evidence is confined to this `producer/` directory. Base `eeaaa4f6`, docs `71c3560b`, the accepted49/19.77s mode-fix evidence, R3/raw/source/README/probe/config/reports/master documents/native helper remain unchanged. No stage/commit, delegation, platform/auth/GPU operation or native build was performed.

The existing source patch passes live `self.tree_core` at checkpoint before `self.insert(insert_params)`. `Collector.insert:229` calls `_capture_native_binding:204` before even looking up the selected bank. Thus an ordinary nonselected native request can identify the actual module before the target bank is selected. The actual adapter class holds `_bindings` at retained `srt/mem_cache/rust_tree_core/adapter.py:311`, constructs `_binding` from `_binding_class()` at468–469, and the existing CPU factory at509–513 selects an exported class without any tree operation. The adapter, Rust helper, source overlay path list and callback/stream hooks are untouched.

Exactly one attempt is cached using `native_binding` and `binding_error`, whether it succeeds or fails. It resolves actual module `__file__` once, reads actual bytes once, computes SHA256 and byte length, and records:

```text
native_binding = {module, module_file, module_sha256, module_bytes,
                  class, class_module, class_is_module_attribute,
                  factory_class_matches, process_id}
binding_error = None | "<error type>: <precise message>"
```

The two boolean ties are actual object identities: exported module attribute is the actual instance class, and existing adapter factory returns that same class. `class_module` is evidence only; equality with module name is deliberately not required for PyO3 classes. No expected artifact/path/hash/PID, environment input, new flag, stat fingerprint, process map, ELF probe or retry is added. Failure is isolated by existing `invalidate`; FULL capture and scoring serving behavior are not changed. All receipts, including unavailable/default paths, contain both fields. Requested drain after all16 rejects missing/errored identity before physical or numerical tensor reads; default failure receipt is unverified. Stage-only `serving_native_origin_sha=PENDING` remains honest and cannot attest the loaded server artifact.

The parent consumer independently compares this actual receipt against existing preflight `binary_target`/`compiled_sha256` and PID/class ties after all16. This producer does **not** perform or claim that comparison.

## CPU verification

Commands were executed from `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, pytest9.1.1; Python3.10 syntax was separately parsed. Two pre-existing Swig builtin-type deprecation warnings remain unchanged.

Focused checks: exit0, **5 PASS,0 FAIL/skip,1.90s**:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_sglang_kv_coherence.py::test_generated_binding_identity_before_selection_and_one_shot tests/fast/test_sglang_kv_coherence.py::test_binding_failure_isolated_once_and_blocks_complete_bank_metrics tests/fast/test_sglang_kv_coherence.py::test_missing_serving_identity_and_unavailable_collector_receipts -q --tb=short --durations=3 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-serving-binding-affected-20261111
```

The real generated runtime test (`test_sglang_kv_coherence.py:352`) captures a canonical symlink target and actual disk SHA/size before bank selection, accepts `class_module="builtins"` via object ties, and prohibits any reread on the second insert even with an invalid replacement core. This is a fake tree/binding class backed by real CPU disk bytes, **not a loaded Rust ABI claim**. The failure test at385 covers wrong export, wrong factory and missing file; each precise error survives a second valid core, both complete-looking bank captures/all16 completions, and prohibits physical/metric computation. The missing/unavailable test at419 checks both unconditional receipt fields. Existing toy tensor tests receive only the minimum fake binding attributes needed by the new actual-interface seam.

Whole existing fast module was run **once**, exit0, **54 PASS,0 FAIL/skip,19.35s**, within30s:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_sglang_kv_coherence.py -q --tb=short --durations=5 -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-serving-binding-module-20261111
```

Mode regressions and all six malformed EXTEND variants/12 global-error assertions are preserved, not reset. Existing source composition/RPC/idempotence/private package/scoring independence/physical index/error/pending gates remain checked. No unrelated or broad suite was run.

## Selected source and checksum evidence

Existing source DI driver, no additional source collection or native build: exit0 with explicit `CPU_SOURCE_DI_ONLY ... production native/GPU qualification PENDING`:

```bash
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/kv-coherence-source-20261111/prepare_cpu_source_di.py --source task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source --output task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/kv-coherence-serving-binding-20261111/producer/cpu-source-di
```

The35 selected source identities and additional native/image pins equal the previous forward-mode manifest; only generated runtime SHA changes to `7ed5b5fb56ef736afee2c9e9aefa7543a779e53f18b3cf3cf7c0943618816308` (25034 bytes). Native preparer remains one DI call; no extra source overlay path is added. R3 receipt SHA stays `91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7`. Runtime and both edited files parse as Python3.10.

A bounded validation command first assumed a retained `cpu-source-di/after/` path and failed with FileNotFoundError **after**35/pin and edited-file AST/hash checks; the existing driver retains only compact diffs/manifests. The corrected validation compares `coherence._runtime_source()` directly to the retained DI SHA and passes. No source/driver behavior or artifact is changed to hide this inspection error. JSON reads use60s timeout and30GiB process address-space limit; this is not a cgroup MemoryMax claim.

Diff: two files,131 insertions/4 deletions,12549 bytes. Collector SHA256 `6be5ef8642f33512fb463f30040247750b472716289eba0c139cb65e5d005721` (41066 bytes); tests `16c5b496eb28f91feec390993d98e9abb282c2fd9d6c011b5b10f56f07b0d78c` (45686 bytes). Exact values/contract/counts are in `producer-manifest.json`; diff is `source-and-tests.diff`; selected preflight/receipt/source hashes are in `cpu-source-di/`.

GPU tensor budget is unchanged: A539361280 bytes (514.375MiB), B337248256 (321.625MiB), no additional GPU buffers. Only compact binding metadata is added to existing JSON drain.

## Limits and next owner

Actual worker Rust extension ABI, actual loaded serving module origin/SHA/PID comparison, joined consumer checks and fixed reviews remain primary work. No native/GPU/model/private-SO/S/all16 active capture,7955 physical/index/KV/root/scoring parity or formal acceptance is obtained from these CPU fixtures. Formal04/05 HOLD and baseline identity criteria remain unchanged. Stop at unstaged/uncommitted producer delivery; primary owns report updates, joined integration, review and commit.
