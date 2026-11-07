# Baseline Actor Fixture Repair

## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Parent verifies the exact pinned two-file rerun: 93 PASS in12.06s and platformSucceeded; fixture repair closed. |
| 2026-11-07 | Record the fixture-only initialization repair, pinned red evidence, local validation limits, and independent pinned follow-up. |

## Outcome and scope

- Task: **QWEN-P3-BASELINE-FIXTURE**.
- The toy baseline actor now has both native role flags and a real actor weight backup. Production code and the native `_switch_model("actor")` path are unchanged.
- Owned files: `tests/fast/test_qwen35_opd_launcher.py` and this new report only.
- A/B H200 formal jobs are independent. This work neither controls nor gates them. No GPU, platform, SSH, cloud, Git, or delegation operation was performed.
- Functional green is **PASS**: parent job `exp-1107-175209-311197` runs both original files in the same pinned image and returns **93 passed /12.06s**, no skips, platformSucceeded. Local collection failure remains historical evidence; no environment repair or skip expansion was required.

## Diagnosis and smallest correction

The recorded pinned run `exp-1107-172750-953553` completed with **90 PASS / 3 FAIL in 14.38s**. The only failures were the `asleep=True` A/B/C instances of `test_baseline_native_scoring_needs_no_optimizer`:

```text
actor.py:666 -> _switch_model("actor") -> _enable_weight_backup
AttributeError: 'MegatronTrainRayActor' object has no attribute 'with_ref'
```

Source/evidence:

- `evidence/h200-launch-contracts-exp-1107-172750-953553.log:8-22,332-335`: exact failures and totals.
- `miles/ray/train_actor.py:198-205`: native `_init_common` sets `with_ref` and `with_opd_teacher`, both defaulting to `False`.
- `miles/backends/megatron_utils/actor.py:613-619`: a supported switch requires the real backup's actor tag and calls its restore method.
- `tests/fast/backends/megatron_utils/score_rpc_fixtures.py:264-285`: the existing training actor factory supplies those flags and a real `TensorBackuper`, but also constructs Adam and executes a step. Reusing that factory would violate this baseline's zero-optimizer requirement.

The manually built baseline actor bypassed native initialization and omitted **three required pieces**: `with_ref`, `with_opd_teacher`, and `weights_backuper` with an `actor` backup. Fixing only the first attribute would expose the remaining omissions.

The correction is one import and three fixture statements:

```python
actor.with_ref = actor.with_opd_teacher = False
actor.weights_backuper = TensorBackuper.create(source_getter=model[0].named_parameters)
actor.weights_backuper.backup("actor")
```

No optimizer, scheduler, fallback, exception suppression, switch override, or new test case was introduced. The memory/process-group SDK boundaries remain as before. The parent-committed `"--gpu-type", "H800"` fixture input is preserved.

## Validation

| Check | Expected | Observed | Status |
| --- | --- | --- | --- |
| Original pinned two-file run | All baseline instances succeed | 90 PASS / 3 missing-role-flag failures, 14.38s | RED; recorded pre-fix evidence |
| Owned-file stdlib AST check | Valid syntax; original assertions and native switch intact | All 7 original assert expressions and exact `assert_close(..., rtol=0, atol=0)` retained; GPU-type input and complete role/backup state checked | PASS |
| Local baseline-only pytest | Six A/B/C × residency instances pass | Two no-output timeouts; diagnostic run later terminated by SIGSEGV during collection | BLOCKED; not a functional result |
| Pinned post-fix two-file run | 93 PASS, including all 6 baseline scoring instances | 93 passed,60 warnings,12.06s; exit0, platformSucceeded | PASS; parent execution |

Local interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3`, **Python 3.12.13**. The existing `native_model_setup` fixture was given read-only scheduler source through `MEGATRON_PATH=/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages`; no native-package import or environment edit was substituted for that fixture.

Exact initial local invocation (tool timeout: 60s):

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 MEGATRON_PATH=/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m pytest -q -p no:cacheprovider tests/fast/test_qwen35_opd_launcher.py::test_baseline_native_scoring_needs_no_optimizer --tb=short
```

A second invocation used the same selector with `CUDA_VISIBLE_DEVICES=''`, `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, and a 30s faulthandler timer; it timed out at 120s. Neither timeout supplied a pytest verdict. The diagnostic invocation below preserved its stack samples (tool limit: 90s):

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MEGATRON_PATH=/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -S -B -c 'import faulthandler, site, sys, tempfile; log=tempfile.NamedTemporaryFile(mode="w", prefix="pytest-", suffix=".log", dir="/data/ycfeng/tmp/opencode-v2-tmp/opencode/baseline-fixture-site-20261107", delete=False); print(log.name, flush=True); faulthandler.dump_traceback_later(15, repeat=True, file=log); site.main(); import pytest; log.write("pytest imported\n"); log.flush(); status=pytest.main(["-q", "-p", "no:cacheprovider", "tests/fast/test_qwen35_opd_launcher.py::test_baseline_native_scoring_needs_no_optimizer", "--tb=short"]); faulthandler.cancel_dump_traceback_later(); sys.exit(status)'
```

Selected diagnostic evidence: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/baseline-fixture-site-20261107/pytest-gf489493.log:1-14,67-81,155-184`. Pytest imported; samples were still inside `tests/conftest.py` dependency loading, including SGLang/Transformers/SciPy file reads. The command then reported `Killed by SIGSEGV`. The underlying runtime/filesystem cause is **not established**; the repaired test body had not produced a result. A separate `-S` bootstrap and explicit `site.main()` both succeeded, ruling out the initial suspicion of site initialization itself. No environment repair was attempted.

The static check used `python3 -S -B` and stdlib AST only, comparing all seven original assertion expressions, the exact zero-tolerance weight comparison, the preserved GPU-type tokens, the real backup setup, and the absence of a `_switch_model` assignment. It passed. This is source evidence, not a substitute for functional green.

## Exact pinned follow-up command

Run independently in the same **0GPU pinned image/source mount** used for the recorded run, from `/data/ycfeng/sota-engine/miles`:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 MEGATRON_PATH=/root/Megatron-LM /opt/sglang/bin/python3 -B -m pytest -q -p no:cacheprovider tests/fast/test_qwen35_pair_worker.py tests/fast/test_qwen35_opd_launcher.py --tb=short
```

Passing condition: **93 PASS**, with no added skip and all six baseline scoring instances retaining weight, score, version, residency, and zero-optimizer assertions. Historical 67/restoration suites need no rerun. Failure to complete this follow-up is a fixture-verification limitation only, not a gate on A/B formal jobs.

## Self-check checkpoint

### Parent pinned completion

The parent ran the command above with `-o addopts=''`, `--basetemp="$TMPDIR/pytest"`, `TMPDIR=/var/tmp/qwen-h200-contracts-$KUBEBRAIN_RJOB_NAME`, CUDA invisible, repository PYTHONPATH, `/root/Megatron-LM`, the configured CUDA compatibility library directory, and offline HuggingFace settings. ResourceConfig was8CPU/0GPU/64units memory, one replica, gang_startFalse, same pinned image, H200/step_main, personal creator and local source. No cloud volume was needed; no optimizer budget was consumed.

- Native launcher: created09:52:09Z, reportsSucceeded09:59:20Z and exit0.
- Raw business result: `evidence/h200-launch-contracts-exp-1107-175209-311197.log:177`, **93 passed,60 warnings in12.06s**; no failed/skipped/ignored-exception entries.
- Exact personal API terminal check: `evidence/oss-cleanup-loader-terminal.json`, this job finishes09:59:16Z asSucceeded with default task succeeded1. The shared receipt also independently records two failed loader jobs for cleanup; those are not test results.
- Original90PASS/3FAIL receipt remains unchanged. Functional verification and the fixture repair are complete; no more baseline-fixture or local import retries are required.

The following owner checkpoint is the historical handoff before the parent pinned result.

### 1. Planning completion

PASS: cause and complete missing toy state diagnosed; smallest owned fixture repair applied; static assertion preservation verified; evidence/report written. BLOCKED: local functional execution. TODO: independent pinned follow-up.

### 2. Drift detection

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 Tooling polish | CLEAR | Only the requested toy state and bounded diagnostics were changed. |
| D2 Retry loop | HIT | Two timeout retries did not produce a verdict; stop further runtime retries and hand off the exact pinned command. |
| D3 Side quest | CLEAR | No environment fix was performed. |
| D4 Stalled frontier | CLEAR | Same-file ownership and no-delegation constraint; formal jobs explicitly independent. |
| D5 Gold-plating | CLEAR | One import and three fixture statements; no new API, fallback, or case. |
| D6 Analysis sprawl | CLEAR | Diagnosis produced the minimal repair; import investigation stops at the recorded limit. |
| D7 Off-route | CLEAR | Only the two owned files were edited; no formal job operation. |

S1-S6: no scope/dependency defect identified in this bounded assignment. D2 is execution drift, not a specification defect.

### 3. Route correction

Branch A: leave requirements/parent plan unchanged. Stop local runtime/environment retries. Parent may run the supplied pinned command independently; do not rerun unrelated restoration suites or gate formal jobs.

### 4. Three priorities

1. Real role flags and actor backup preserve the native restore path without creating an optimizer.
2. Functional green is still unverified; source checks are not a pytest PASS.
3. A/B formal jobs remain independent and untouched.
