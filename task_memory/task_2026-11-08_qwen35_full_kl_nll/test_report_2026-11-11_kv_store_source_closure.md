## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record conditional allocator/FFI source qualification, correct the missing writer-context field, and retain pending actual-call/payload limits. |
| 2026-11-11 | Extend retention verification to the complete installed allocator/Cython package scope; all source identities pass, execution qualification remains pending. |
| 2026-11-11 | Record two zero-GPU source jobs and independent archive checks; stream, lifetime and numerical qualification remain pending. |

# KV-store source retention verification

## Scope and environment

This report verifies retained source provenance and bytes for three zero-GPU jobs, not numerical capture or a library fix. The design prerequisites remain in `design_kv_coherence_measurement.md`.

- Workspace: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`.
- Submission: existing StepMind Python `RJobBackend`, personal creator `i-fengyicheng`, `codesign`, local NFS source, two CPUs / zero GPUs / 8 GB per source job.
- Controller: `/data/ycfeng/tmp/stepmind-env/bin/python`; API package output identifies Python 3.10. The exact controller interpreter patch version was not independently captured.
- Local verifier: `/usr/bin/python3`, Python 3.10.6 / GCC 11.3.0.
- Worker executable: `/opt/sglang/bin/python3`; its exact Python version was not retained.
- Image: `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`.
- Actual package: `sglang=0.5.24.dev80+g056f871`; the complete closure also retains `apache-tvm-ffi=0.1.11` source/headers.

## Commands and frozen provenance

All three submissions used the existing proxy/personal-auth environment with `STEPMIND_BACKEND=rjob`, `PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=$PWD:/data/ycfeng/steptron`, then:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -B \
  /data/ycfeng/tmp/opencode-v2-tmp/opencode/submit-full-component-source-20261111.py
```

The temporary submitter/collector changed between jobs. The exact worker Python `-c` program, image, mount and submission timestamp are frozen in the corresponding submission JSON, not inferred from the current temporary file. The worker collector was passed inline, avoiding a dependency on private mode-0700 temporary files.

Evidence root: `evidence/native-sglang-cache-source-20261111/`.

| Job | Submission receipt | Terminal receipt |
| --- | --- | --- |
| `exp-1111-094840-273565` | `kvcache-store-stream-submission.json` | `kvcache-store-stream-terminal.json` |
| `exp-1111-100210-790198` | `kvcache-stream-closure-submission.json` | `kvcache-stream-closure-terminal.json` |
| `exp-1111-102145-988437` | `allocator-cython-package-submission.json` | `allocator-cython-package-terminal.json` |

Independent local verification ran this Python logic for each job directory:

```python
from pathlib import Path
import hashlib, json

root = Path("task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111")
for job in ("exp-1111-094840-273565", "exp-1111-100210-790198",
            "exp-1111-102145-988437"):
    current = root / job
    receipt = json.loads((current / "source.json").read_text())
    for entry in receipt["files"]:
        content = (current / "source" / entry["path"]).read_bytes()
        assert len(content) == entry["bytes"]
        assert hashlib.sha256(content).hexdigest() == entry["sha256"]
        prior = [directory / "source" / entry["path"]
                 for directory in root.iterdir()
                 if directory.is_dir() and directory != current
                 and (directory / "source" / entry["path"]).is_file()]
        if prior:
            assert any(hashlib.sha256(path.read_bytes()).hexdigest()
                       == entry["sha256"] for path in prior)
```

The observed tool invocations verified each job after it finished. Earlier comparisons therefore preceded later archives' creation; the reported prior-match counts retain those original observations.

## Expectations and observations

Passing conditions: terminal Succeeded, nonempty retained source, every byte count/SHA256 matching its manifest, and at least one matching prior copy for every path that has prior retained copies. Prior-match counts are per path, not a claim that every historical variant is byte-identical.

| Check | Initial store source | Complete closure | Verdict |
| --- | --- | --- | --- |
| Native terminal | Succeeded | Succeeded | PASS |
| Files / bytes | 67 / 2,595,555 | 1,537 / 21,897,427 | PASS: retained and read back |
| Store-package files | 30 | 30 | PASS |
| Manifest byte/SHA checks | 67/67 | 1,537/1,537 | PASS |
| Prior matching files | 9 | 97 | PASS |
| Paths without a matching prior copy | 0 | 0 | PASS |
| Installed TVM FFI source/headers | Not part of initial selection | Retained, version 0.1.11 | PASS: source retention only |
| Numerical capture / GPU execution | Not performed | Not performed | NOT VERIFIED |

The third package-level collection closes the earlier missing SGLang allocator and Cython extension scope:

| Check | Actual | Verdict |
| --- | --- | --- |
| Native terminal `exp-1111-102145-988437` | Succeeded | PASS |
| Files / bytes | 5,501 / 79,478,292 | PASS: retained and read back |
| Manifest byte/SHA checks | 5,501/5,501 | PASS |
| Prior matching paths / paths without a matching prior copy | 1,805 / 0 | PASS |
| Cython source | 1 `.pyx` + 11 `.pxi` | PASS: retained |
| Conditional static allocator/FFI source qualification | Closed by read-only TaskID `profile-kv-recurrent-coherence-measurement-design-20261111` | PASS: source phase only |
| Actual launch stream and allocator class | Witness-only preparation selected; no new GPU run submitted | NOT VERIFIED |

Logs contain Paramiko TripleDES deprecation warnings; all three jobs nonetheless reached native Succeeded and yielded readable source. No warning was suppressed or reinterpreted as a business failure.

## Limits and next qualification

The initial archive revealed missing generic `LaunchKernel` and TVM stream dependencies. The second collection retained SGLang kernels and selected installed TVM FFI source/header suffixes, but omitted Cython and the complete allocator scope. The third retained complete installed SGLang and TVM FFI Python/Cython/C/CUDA source/header suffixes plus extension inventory. Source collection alone does not establish actual launch stream, PDL completion ordering, OLD index readiness, physical-slot lifetime, writer RID/row binding or numerical fidelity.

Read-only source qualification closes both Cython stream-source branches and the index-only allocator lifetime chain for the recorded B configuration's inferred `TokenToKVPoolAllocator`. Actual class/launch stream are not measured. Actual GDN CPU host-field carry is independently verified, but global writer-context publication is not: the specified `ForwardContext.forward_batch` is absent in the unmodified pinned source. Writer/FULL-index equality and prefix-valid per-row writes remain unverified. The canonical design records the corrected witness-only next stage and distinguishes CPP from Triton terminals. No additional wait/lock, cache policy change, fresh-slot read after release, tolerance change, formal admission or numerical GPU probe is accepted by this report.
