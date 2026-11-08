## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | T03-FORMAL-ACCOUNTING: reuse failure/result/reader records for prelaunch accounting and exit timestamps; remove an unused builder label without changing native behavior. |

# Formal SWE readiness metadata

## Scope and existing acceptance

The parent-approved formal baseline is still unstarted. This change is metadata preparation only. No GPU, platform, cloud, authentication, package installation, commit, new qualification run, scoring-policy change or configuration rewrite was performed.

Inspected native evidence: `test_report_2026-11-08_native_swe_qualification.md` and `evidence/native-swe-qualified-20261108.json`. The receipt records real original4B and trainedHF3 one-slot successes, all197 request hashes and native artifact hashes verified, six/three exited readers, and incomplete1/400 ledgers with399 missing and null avg@4. Parent's newer instruction additionally confirms8 cloud-filesystem fixture passes; the older native report's pending cloud-fixture paragraph was not edited by this scoped agent.

## Changes and definitions

- `tests/manual/agent_opd/swe_evaluation.py`: load existing failure JSON into the reference `FourAttempts.infra_failure()` **before** loading scored results. Return the existing durable failure path from `infra_failure()`. Add derived `accounting` and `failure_paths` to `summary()`; do not add a ledger or modify a scored result.
- The existing `reader_exit()` adds `finished_at` after actual child/process cleanup. This covers native children through their unchanged `NativeSweRunner` call, plus evaluator/server readers. Older exited readers remain readable without invented timestamps or migration writes.
- Formal sample cancellation persists an existing-format `CancelledError` failure event after native cleanup, then reraises cancellation. Existing sample exceptions/timeouts remain isolated, completed results remain immutable, and no retry/resume is introduced.
- `tests/manual/agent_opd/swe_evaluation_config.py`: remove the unused `parser_validation=CANDIDATE_PENDING_NATIVE_VERIFICATION` output field. Repository Python search found no runtime consumer; the sole test assertion is corrected. Parent's worker CI registration remains exactly `est_time=50`, `suite=stage-b-cpu`, existing labels.

Counts are by **distinct frozen task/seed UID**, not execution attempts across recovery:

| Field | Meaning |
| --- | --- |
| attempted | UID has a durable scored result, failure event, or native child reader. |
| successful | Completed native Boolean True. |
| model_failed | Completed native Boolean False, including any native terminal condition that the unchanged grader scores False. |
| timed_out | Missing UID's latest applicable failure is a recorded `TimeoutError`. This does not reinterpret a completed native model outcome as missing. |
| infra_failed | Missing attempted UID has another failure, cancellation, or an exited native reader without a scored result. |
| in_progress | Missing UID's latest native reader is still RUNNING and newer than its historical failure. This describes the recorded native-reader boundary, not a new scheduler state. |
| unstarted | No durable result, failure or native child reader for the UID. |
| skipped | Zero: the frozen benchmark has no permanent slot-skip policy. Not reexecuting a completed slot during resume is not a new skipped result. |
| failure_events | Historical failure JSON count, deliberately separate from final slot categories. |

Completed outcomes take precedence over historical failures. Example: one failed UID later resolves ⇒ attempted1, successful1, infra_failed0, failure_events1; its failure path and error remain in `raw_records`/`failure_paths`. Categories reconcile to400 with unstarted; attempted excludes unstarted. Denominator stays400, missing-only recovery and the original72h deadline are unchanged, and any missing result keeps avg@4 null.

No new routine trajectory reads, source profiling, configuration fingerprints, logging framework or state machine was added. Existing storage errors still propagate through their existing native/lifecycle I/O boundary; required durable writes are not silently suppressed. The independent evaluator boundary still prevents these errors from stopping unrelated training.

## Configuration refresh

**No refresh is required before formal enqueue.** The removed field is top-level descriptive metadata, outside `evaluation_contract`/scientific runtime and unused by server/agent/scorer/dispatch. Existing `evaluation_formal_inputs.json`, `evaluation_formal_config.json` and immutable qualification configurations were not edited. A fresh builder output simply omits the field; it does not claim future HF50/100/150/200 already passed native validation. Actual per-point `workers/<server-reader>/server.json` and the verified native qualification receipt remain authoritative.

## Verification

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, pytest9.1.1; cwd `/data/ycfeng/sota-engine/miles`. All checks unset real private evaluator/platform credential names and use CPU/local synthetic fixtures under `/data/ycfeng/tmp`; no real model/ACS execution occurs.

Exact red/green command (change only `red` to `green` in the two output paths):

```bash
env -u SR_USER_TOKEN -u SESSION_ROUTER_USER_TOKEN -u AK_BASEMIND -u SK_BASEMIND \
  -u BRAINPP_ACCESS_KEY -u BRAINPP_SECRET_KEY TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_swe_evaluation.py -k accounting -q \
  --basetemp=/data/ycfeng/tmp/t03-formal-accounting-red \
  --junitxml=/data/ycfeng/tmp/t03-formal-accounting-red.xml --durations=3
```

- RED:4 failed,59 deselected,1.92s. Three failures expose missing accounting; the fourth exposes absence of the new exit timestamp at the existing required state-write boundary.
- GREEN:4 passed,59 deselected,2.05s. Covers neverstarted vs failed, same-UID recovery/history/no double count, original deadline, recorded-reader progress/exit time, isolated timeout then healthy outcome, cancellation cleanup/counts, completed-model no-reroll and durable write-error propagation.
- Builder assertion: `tests/fast/test_swe_evaluation_worker.py -k configuration_binds -q`,1 passed/33 deselected,1.03s, basetemp `/data/ycfeng/tmp/t03-formal-accounting-builder`.
- Additional native fixture checks cover invocation/start/exit timestamp wiring, valid historical exited records with no timestamp migration or regeneration, and native outcome-publication I/O failure. Complete related regression: **215 PASS,0 failures/skips,220.79s**, with16 existing SWIG/Torch JIT deprecation warnings:

```bash
env -u SR_USER_TOKEN -u SESSION_ROUTER_USER_TOKEN -u AK_BASEMIND -u SK_BASEMIND \
  -u BRAINPP_ACCESS_KEY -u BRAINPP_SECRET_KEY TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_swe_evaluation.py tests/fast/test_swe_native_evaluation.py \
  tests/fast/test_swe_evaluation_worker.py tests/fast/test_swe_evaluation_submission.py \
  tests/fast/test_swe_hf_export.py tests/fast/test_swe_evaluation_dispatch.py -q \
  --basetemp=/data/ycfeng/tmp/t03-formal-accounting-regression \
  --junitxml=/data/ycfeng/tmp/t03-formal-accounting-regression.xml --durations=5
```

After formatting-only changes, final selected checks were **8 PASS,114 deselected,4.99s**:

```bash
env -u SR_USER_TOKEN -u SESSION_ROUTER_USER_TOKEN -u AK_BASEMIND -u SK_BASEMIND \
  -u BRAINPP_ACCESS_KEY -u BRAINPP_SECRET_KEY TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_swe_evaluation.py tests/fast/test_swe_native_evaluation.py tests/fast/test_swe_evaluation_worker.py \
  -k 'accounting or actual_exit_boundary or timestamp_migration or native_io_failure or configuration_binds' -q \
  --basetemp=/data/ycfeng/tmp/t03-formal-accounting-final \
  --junitxml=/data/ycfeng/tmp/t03-formal-accounting-final.xml --durations=3
```

Ruff0.14.7, isort5.13.2, Black24.3.0 and scoped `git diff --check` pass. Existing cached tools were used, without installation. Black checked the two implementation files/native tests in full and only changed lifecycle-test fixture/new-test ranges83–128 and748–1000, preserving unrelated compact fixtures. Ruff/isort checked those four Python files plus the worker assertion file. The existing pyproject lint-setting deprecation remains unrelated.

Modified tests: `tests/fast/test_swe_evaluation.py`, `tests/fast/test_swe_native_evaluation.py`, and only the stale-label assertion in `tests/fast/test_swe_evaluation_worker.py`. Native execution modules `swe_native_evaluation.py`/`run_swe_evaluation.py` remain unchanged; the per-child timestamp is supplied by the existing store interface.

Scope checkpoint: requested accounting, failure provenance, reader exit timing and stale-label removal are complete; the215-test regression and eight final checks passed. No shared spec/progress/configuration change or further implementation is needed. Existing native qualification remains accepted; no new behavior-dependent GPU validation is needed for this metadata-only patch. Parent owns final formal admission/submission and actual formal accounting evidence.
