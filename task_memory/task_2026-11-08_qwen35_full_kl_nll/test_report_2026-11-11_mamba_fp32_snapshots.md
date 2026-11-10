## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Deliver the CPU-qualified, two-file selected-FP32 wiring candidate, exact native identities, RED/GREEN evidence, and future worker API. CUDA and warm probability semantics remain unverified. |
| 2026-11-11 | Primary independently reran25 retained-source checks and froze the candidate for two-axis review; native acceptance remains open. |

# Selected FP32 Mamba snapshots — source-fidelity fix candidate

TaskID: `profile-native-mamba-fp32-snapshots-20261111`.

**Result: CPU-ready candidate; 25 CPU tests PASS. No GPU, platform, SSH, network, delegation, staging, or commit operation was performed. Formal A/B remain blocked.**

## Scope and deliverables

The delegated request owns only these new files:

- `tests/manual/agent_opd/sglang_mamba_snapshots.py`: standard-library source preparer and CLI.
- `tests/fast/test_sglang_mamba_snapshots.py`: retained-native-source fixture copies and Python call-binding checks.
- This report.

No retained source, launcher, probe, formal/config file, requirement, plan, ticket, or other existing repository file was edited. No full dependency source is vendored. A separate supporting patch artifact is unnecessary: the preparer contains small reversible edits and generates its exact two-file diff in the runtime archive.

The gain is the existing native FP32 checkpoint fidelity: connect the selected recurrence snapshot to the existing temporal-pool copy without changing the workload or introducing another recurrence. Parent authority remains [requirements D40](requirements.md#workflowparameter-rca--original-request-2026-11-11), [plan current frontier](plan.md#current-frontier), and [spec S8](spec.md#s8-gpu-与执行d16d19d33d39d40). The authoritative measured-drift evidence remains [the primary RCA report](test_report_2026-11-11_workflow_rca.md).

## Native identity and inspected seams

Supported image/version are owned by `source_manifest()` in the preparer:

- Image: `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`.
- SGLang: `0.5.24.dev80+g056f871`.
- C3 retained root: `evidence/native-sglang-cache-source-20261111/exp-1111-042450-358109/source/`.
- Observed native package path in the C3 receipt: `/sgl-workspace/sglang/python/sglang`.

The preparer verifies six complete, narrowly selected source identities before any dependency write. Two are modified; four remain byte-identical. It checks both image and actual installed distribution version without importing SGLang, Torch, or Triton. The host's CPU SGLang `0.5.23` is explicitly unsupported.

All line references below are to pristine C3 files relative to that root:

| File / lines | Observation and candidate action |
| --- | --- |
| `kernels/ops/attention/fla/chunk_delta_h.py:102–108,171–207,331–348,364–378,397,419–436` | Existing FP32 recurrence and selected snapshot stores already exist. Ordinary `h` remains allocated from `k`; the final state retains the pool dtype. No kernel edit. |
| `srt/layers/attention/linear/kernels/kernel_backend.py:18–24` | Existing capability defaults to False. No base-class edit. |
| `srt/layers/attention/linear/gdn_backend.py:1166–1205,1219–1225` | Existing capability-selected FP32 buffer allocation and snapshot/position forwarding. No allocation or backend edit. |
| `srt/layers/attention/hybrid_linear_attn_backend.py:503–529,1041–1063` | Existing chunk indices and batch-row mapping; selected-buffer copy already precedes the activation-rounded `h` path. No position, pool-dtype, or cache-policy edit. |
| `srt/layers/attention/linear/kernels/gdn_triton.py:40–44,169–215` | Add the existing snapshot capability for native CUDA only; forward the two existing snapshot kwargs only on that supported implementation. CPU/NPU/XPU do not advertise support. |
| `kernels/ops/attention/fla/chunk.py:36–73,93–132,136–149,254–266` | Append optional `track_state` and `track_chunk_idx` to public/forward/fwd signatures and transport both through `Function.apply` to the existing `fwd_h` consumer. Return values, normal output construction, and cold arithmetic are unchanged in source. |

`input_guard` was also inspected in `fla/utils.py:145–179`: it makes tensors contiguous without changing dtype. Its CUDA `autocast_custom_fwd` definition at lines320–323 supplies no `cast_inputs` override. Neither decorator is edited; their GPU behavior is not exercised by these binding tests.

C1 retains the same `hybrid_linear_attn_backend.py` SHA256 as C3. C2's retained `source.json` reports `all_gpu_reference_hashes_matched=true`, but does not retain the two candidate files. Therefore this preparer qualifies C3 directly; it does not extrapolate C2 into a complete kernel-source receipt or use host CPU source as a substitute.

### Exact native edits

The generated diff has **two files and 28 inserted lines**, including five API documentation lines. The recurrence, normal `h` allocation, intra-chunk computation, output computation, final-state stores, decode/target-verify methods, positions, interval, pool dtype, cache policy, and backend selection are not edited.

| Native file | Before SHA256 | Candidate SHA256 |
| --- | --- | --- |
| `kernels/ops/attention/fla/chunk.py` | `0fa7c1a0c1b9a9f1b5548dfeed58181df88ded8e4bbb36e27ce63e16c3d7fd85` | `b2c1cd76ab3558b893e082f07a8c587520e624e9988d19c0c1afa4f32a72e43c` |
| `srt/layers/attention/linear/kernels/gdn_triton.py` | `ede52671dd880b4317c2308ad58d21d33544044b7bddda93d24bc08216fa812a` | `7060585d86347561a2caf36492163b584152e32efddea17b5b4cc8c33c5774bf` |

The other four before/after hashes are identical and are recorded in `source_manifest()` and every receipt. Hashes prevent changing the wrong dependency before a costly native launch, rather than serving as workload metadata.

## CPU verification

Environment: existing `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, pytest9.1.1, host SGLang0.5.23. No dependencies were installed. The fixture substitutes only the installed-version check with the retained native version; all source bytes are actual C3 files copied into the owned temporary directory. The host SGLang is never imported by these tests.

### RED: missing wiring reproduced before implementation

Exact command:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python - <<'PY'
import shutil,tempfile
from pathlib import Path
from tests.fast.test_sglang_mamba_snapshots import _RETAINED,_Tensor,_native_call
root=Path(tempfile.mkdtemp(prefix='mamba-fp32-red-'))
for relative in ['kernels/ops/attention/fla/chunk.py','kernels/ops/attention/fla/chunk_delta_h.py','srt/layers/attention/linear/kernels/gdn_triton.py']:
 target=root/relative
 target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(_RETAINED/relative,target)
snapshot=_Tensor((2,2,64,128),'float32')
observed=_native_call(root,snapshot=snapshot,positions=_Tensor((2,),'int32'))
print('fixture:',root)
print('capability:',observed.capability,'TRACK_STATE:',observed.launch['TRACK_STATE'],'track_state:',observed.launch['track_state'])
assert observed.launch['track_state'] is snapshot, 'native extend silently dropped the selected FP32 snapshot'
PY
```

Observed fixture: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/mamba-fp32-red-48lraaxb`.

Observed signal: `capability: False TRACK_STATE: False track_state: None`, followed by `AssertionError: native extend silently dropped the selected FP32 snapshot`; exit1, **expected RED**. This reproduces the source-wiring defect, not the full-model teacher probability drift.

### GREEN: required CPU acceptance

Final exact command:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_sglang_mamba_snapshots.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/mamba-fp32-final-20261111 -q
```

Observed: **25 passed, 2 warnings in1.83s**, exit0. Warnings are pytest plugin import deprecations for `SwigPyPacked` / `SwigPyObject`; no warnings were suppressed.

Primary independently reran the same25 checks: **25 passed,2 existing SWIG warnings in1.54s**, Python3.12.13/pytest9.1.1. No native GPU or installed dependency was modified. Exact command:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_sglang_mamba_snapshots.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/mamba-fp32-primary-20261111
```

Passing conditions and observations:

- Four equal/variable-length × inplace-writeback combinations: pristine source drops both snapshot inputs; candidate transports the same FP32 buffer and position objects to the native low-level launch and sets `TRACK_STATE=True`.
- Ordinary `h` remains BF16, output/return binding and final-writeback control stay unchanged, and unchanged launch metadata retains the same values. Envelope slot stride is retained at the low-level binding.
- Baseline verification is read-only. Applying twice and applying to an already-prepared source with a new archive is idempotent. Before/after archive bytes and source hashes match exactly. Baseline mode rejects prepared source rather than silently reverting it.
- Unsupported changes to each of the six sources, wrong image/version/boolean, and a conflicting archive are rejected before any dependency source write; fixture bytes remain unchanged.
- Existing low-level paired-input and FP32-dtype assertions are reached; they reject a missing partner or a rounded buffer.
- CUDA-only capability is evaluated from the actual native class definition for CUDA/CPU/NPU/XPU flags. Non-CUDA kernels are not executed.
- The four unmodified source files remain byte-identical. AST checks confirm unchanged output/intra/cumsum/l2norm calls, return statements, and packed-decode/decode/target-verify methods.
- CLI emits the preflight receipt with exact source path, applied state, and `cuda_semantics=UNVERIFIED`.

Initial suite iteration:23 PASS /1 FAIL in1.89s. The failure was a CPU test recorder incorrectly trying to execute the NPU gather with a non-subscriptable metadata object, not a native candidate defect. The test was narrowed to the actual CUDA call chain and separate non-CUDA capability evaluation. The corrected suite passed25/25 in1.59s, then passed again after final source formatting as above. No native behavior was changed to accommodate that harness failure.

Additional observed checks:

- `/usr/bin/python3`3.10.6 parsed both delivered modules and all candidate native bytes, imported the standard-library preparer, checked all six retained hashes unchanged, and verified the two candidate hashes: **PASS**.
- `git diff --no-index --check /dev/null tests/manual/agent_opd/sglang_mamba_snapshots.py` and the analogous test-file command produced no whitespace diagnostics. Exit1 denotes the new-file difference under `--no-index`, not a whitespace error.
- Black/Ruff/isort were unavailable in the existing CPU environment; no formatter/linter installation or package change was performed.

Temporary exact candidate archive:

`/data/ycfeng/tmp/opencode-v2-tmp/opencode/mamba-fp32-final-20261111/test_preparer_archives_exact_s0/candidate/`

It contains `before/<native-relative-path>`, `after/<native-relative-path>`, `source_manifest.json`, `selected_fp32.diff`, and two append-only `preflight.jsonl` receipts. These are disposable CPU fixture artifacts, not a native worker application receipt. The source preparer regenerates them on the future worker; the report and retained C3 source are the persistent reproduction inputs.

## Exact future worker API — PRIMARY only

Run using the **pinned worker Python**, before importing SGLang attention code or starting engines, on every worker/container that will serve the candidate. The native package must be writable, and the actual run image must be supplied as `IMAGE`; do not forge the installed version check or replace it with host CPU metadata.

```python
from importlib import util
import os
from pathlib import Path

from tests.manual.agent_opd.sglang_mamba_snapshots import prepare_source

receipt = prepare_source(
    Path(util.find_spec("sglang").origin).parent,
    image=os.environ["IMAGE"],
    selected_fp32=True,
    archive_dir=Path(os.environ["SNAPSHOT_ARCHIVE"]),
)
```

API: `prepare_source(root: Path, *, image: str, selected_fp32: bool, archive_dir: Path) -> dict`.

CLI equivalent:

```bash
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.sglang_mamba_snapshots --sglang-path /sgl-workspace/sglang/python/sglang --image "$IMAGE" --archive-dir "$SNAPSHOT_ARCHIVE" --selected-fp32
```

Use a fresh, PRIMARY-selected attempt archive. Omitting `--selected-fp32` / passing False only verifies and archives the pristine baseline; it does not revert a prepared dependency. The receipt records all six observed before/after hashes, the two changed files, capability scope, dtype label, and whether the patch was actually applied. An idempotent application records `patch_applied=false` while retaining the exact candidate after hashes. The preparer rejects unsupported source or conflicting archive before writes; it is not a transaction/rollback system for an OS write failure and must not run concurrently with serving/imports.

## Verification limits and remaining work

This candidate makes no historical-root-cause claim. Tests execute the real native Python definitions from retained source, with metadata-only tensors, identity decorators, a positional `Function.apply` adapter, and a recorded Triton launch. They do not execute the recurrence, real PyTorch autograd/decorators, CUDA compilation, selected GPU stores, or full-model inference.

No GPU `.item()`, `.cpu()`, `.tolist()`, synchronization, wait, broad logging, tolerance change, monkeypatch/fallback in runtime code, all-`h` FP32 conversion, interval/dtype/cache-policy/backend change, or new recurrence was added. Canonical-KV/full-warm changes and the deferred coarse-barrier question are outside this candidate.

PRIMARY must integrate/execute the source preflight on an H800 worker, archive the actual installed-source receipt, and validate native cold/output/final-state and warm-response probabilities against independent cold references. A successful preflight or CPU GREEN is not acceptance of CUDA semantics, the teacher warm-cache correction, throughput, or formal04/05 readiness. Full-input warm cached0 is not an oracle because it still contains canonical-KV substitutions; this candidate may improve only response warm and may leave other warm-state defects.

## Check-progress checkpoint

### 1. Planned work completion

PASS3 / TODO1: source preparer, CPU acceptance, and report are delivered; PRIMARY native integration and H800 revalidation are unfinished. This is a phase-status checkpoint, not a code-quality or native-correctness review.

### 2. Drift detection

Window: delegated CPU candidate scope through this report. Frontier: native selected-FP32 integration/revalidation by PRIMARY.

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 Tooling polish | CLEAR | Tests stop at required wiring/identity/idempotence checks. |
| D2 Retry loop | CLEAR | One recorder failure was identified and narrowed; no native workaround/retry loop. |
| D3 Side quest | CLEAR | Only the three explicitly owned new files are delivered. |
| D4 Stalled parallel frontier | CLEAR | Other investigations and native operations remain PRIMARY-owned; no delegation allowed here. |
| D5 Gold-plating | CLEAR | Two existing snapshot inputs/capability only; no new algorithm or policy. |
| D6 Analysis sprawl | CLEAR | Inspected seams yielded the preparer and reproducible tests. |
| D7 Off-route | CLEAR | CPU-only; formal/config/probe/launcher/source evidence untouched. |

S1–S6: no scoped document defect found.04/05 own the shared native correctness blocker, CPU versus native acceptance remain separate, requirements are measurable, and the delegated file ownership is explicit. Attribution: none.

### 3. Route correction

Branch A: leave spec/tickets unchanged. No drift behavior needs stopping. Next: PRIMARY worker preflight with source receipt → actual H800 cold/warm revalidation → only then the existing formal readiness/admission route.

### 4. Three points to watch

1. CPU25/25 settles wiring and source preparation only.
2. Actual installed version/source hashes must match before importing serving code.
3. Warm probabilities must be checked against cold references; formal hold is not released by this candidate.
