## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | T03-HF-QUALIFICATION: add explicit owned-smoke enqueue/submit seam and repair the parent-observed private ACS environment handoff. |

# Owned HF native SWE qualification

## Outcome and scope

Local implementation is complete: **182 PASS** across the affected regression, followed by **50 PASS** after formatting. Native exported-HF reload and SWE acceptance remain parent-owned and unverified by this agent. No real weight copy, real package metadata rewrite, formal-update bypass, source deletion, platform operation, credential-value inspection, source-pin change, or automatic resume was performed.

Changed code/tests:

- `tests/manual/agent_opd/swe_evaluation.py`
- `tests/manual/agent_opd/submit_swe_evaluation.py`
- `tests/fast/test_swe_evaluation.py`
- `tests/fast/test_swe_evaluation_submission.py`

`run_swe_evaluation.py`, `swe_native_evaluation.py`, the exporter, integration configuration, shared progress/spec, and existing immutable manifests are unchanged. No commit was created.

## Delivered API and safety

```python
store.enqueue_qualification_checkpoint(
    point_id="qualification.A-r256-smoke-HF3",
    checkpoint_dir=actual_smoke_hf,
    source=configuration["original_source"],
    task_ids=configuration["task_ids"],
    configuration=configuration["evaluation_contract"],
)
```

The method only accepts a `/qualification-evaluations` store and a nonempty `qualification.<name>` point. It reads the existing `hf_publications/step_N.json`, requires `SMOKE_PACKAGED`, `run_kind=smoke`, `formal_evaluation=false`, and the same checkpoint path, then validates native successful/index/rollout/version/counters against the packaged Qwen export. Successful/attempted/skipped counts must be actual integers with attempted=successful+skipped. Source must match the caller's protected original and the HF must be inside the current owned root. The complete marker must be at least as recent as every inventoried HF file; partial packaging/index/config/tokenizer exports are refused.

The manifest keeps the existing100-task/four-seed configuration, native update and file inventory, adding only `run_kind=qualification`. The same400-slot scorer/ledger is reused. At enqueue, completed=0, missing=400, avg@4=null, and the deadline is not started. `release()` returns `PROTECTED_QUALIFICATION`, deleted_bytes=0, even if all400 slots are subsequently populated. It does not write a deletion receipt or change completed state.

Formal `enqueue_checkpoint` keeps its exact50/100/150/200 gate and formal package requirement. Baseline manifests/behavior remain unchanged. Shared directory/package primitives were extracted rather than creating another packager or identity scheme.

The explicit local submit option `--qualification-checkpoint PATH` is mutually exclusive with `--original-source`. It requires the qualification namespace/point, distinct explicit frozen attempt IDs, and the exact registered original student from both integration pairs. It does not permit selecting all400 slots as a small qualification. On the GPU worker, the existing submit adapter validates the actual admission receipt's qualification source/point, enqueues the observed smoke HF, and execs the unchanged `run_swe_evaluation` worker. The receipt adds `run_kind=qualification` and the exact `qualification_checkpoint`; no credentials enter receipt or argv. The worker retains the existing SGLang server, readers, native update selection, pure-text architecture check, `NativeSweRunner`, grader, deadline and cleanup behavior.

## Parent-observed native failure and environment repair

Parent supplied the actual failure for original4B qualification job `exp-1108-175747-357945`: server model/parser/template/version validation passed, but `RunCheckPipeline.__init__` at `sweagents_swe.py:583–587` failed because `AK_BASEMIND`/`SK_BASEMIND` were absent from the worker environment. Parent's exact red probe found both names locally present and both absent from `submit._worker_environment(...)`; equality assertion failed. Redacted evidence: `evidence/qualification-original4b-native-failure.log`.

The known cause was the submit adapter copying only SR token aliases. The minimum fix requires and privately inherits both native ACS key variables, rejects all four private credential names in configuration `envs`, and errors with the missing **name only** for absent/empty keys. There is no fallback, missing-variable suppression, new retry flag, contract change, or automatic recovery. Credential values stay in the private worker environment. Real credential probes and GPU reruns remain with parent; all agent tests remove real credential names first and inject synthetic values.

Parent reports the failed qualification has0 completed/400 missing results, three EXITED readers and its original deadline retained. This is infrastructure incompleteness with avg@4=null, not a completed model failure scored0. Those existing records were not edited. Parent alone diagnoses/resumes that point explicitly.

## CPU verification

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, pytest9.1.1; repository cwd `/data/ycfeng/sota-engine/miles`. Local fixture files and raw JUnit XML are under `/data/ycfeng/tmp`. No real HF or credentials enter fixtures.

1. Private environment targeted checks: **11 PASS,22 deselected,0.80s**. Assertions cover exact AK/SK inheritance, absent/empty errors, config-file refusal and no credential values in dry-run/submission receipt/argv/stdout.

```bash
env -u SR_USER_TOKEN -u SESSION_ROUTER_USER_TOKEN -u AK_BASEMIND -u SK_BASEMIND \
  -u BRAINPP_ACCESS_KEY -u BRAINPP_SECRET_KEY TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_swe_evaluation_submission.py \
  -k 'native_acs or private_tokens or fresh_snapshot or dry_run' -q \
  --basetemp=/data/ycfeng/tmp/t03-hf-qualification-env-fixtures
```

2. Qualification/environment selected checks: **50 PASS,57 deselected,28.33s**. Cover actual3/2/2/3 identity, formal-vs-smoke rejection, required namespace, stale/partial export, counter/version/source mismatches, original/current-root protection, immutable full400/null ledger, no release after synthetic400-slot completion, mutually exclusive submit arguments and durable worker enqueue-before-exec. Synthetic400 records only test retention; they are not native SWE results.

```bash
env -u SR_USER_TOKEN -u SESSION_ROUTER_USER_TOKEN -u AK_BASEMIND -u SK_BASEMIND \
  -u BRAINPP_ACCESS_KEY -u BRAINPP_SECRET_KEY TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_swe_evaluation.py tests/fast/test_swe_evaluation_submission.py \
  -k 'qualification or native_acs' -q \
  --basetemp=/data/ycfeng/tmp/t03-hf-qualification-new-fixtures
```

3. Complete affected regression: **182 PASS,0 failures/skips,186.30s**, with16 existing deprecation warnings. This also exercises the unchanged exporter, GPU worker wiring and native format fixtures without real GPU/ACS calls.

```bash
env -u SR_USER_TOKEN -u SESSION_ROUTER_USER_TOKEN -u AK_BASEMIND -u SK_BASEMIND \
  -u BRAINPP_ACCESS_KEY -u BRAINPP_SECRET_KEY TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_swe_evaluation.py tests/fast/test_swe_evaluation_submission.py \
  tests/fast/test_swe_hf_export.py tests/fast/test_swe_evaluation_worker.py \
  tests/fast/test_swe_native_evaluation.py -q \
  --basetemp=/data/ycfeng/tmp/t03-hf-qualification-regression-fixtures \
  --junitxml=/data/ycfeng/tmp/t03-hf-qualification-regression-20261108.xml
```

Per-file accumulated testcase durations (including fixture setup/teardown), from the retained XML:

| File under tests/fast | Passed | Seconds |
| --- | ---: | ---: |
| test_swe_evaluation.py | 59 | 137.325 |
| test_swe_evaluation_submission.py | 48 | 1.555 |
| test_swe_hf_export.py | 23 | 7.078 |
| test_swe_evaluation_worker.py | 30 | 34.321 |
| test_swe_native_evaluation.py | 22 | 3.942 |

The lifecycle file retains stage-b-cpu/its existing labels and updates its estimate to180s with headroom for the measured137.325s. After formatting-only changes and that registration estimate update, the qualification/environment command was rerun with `--basetemp=/data/ycfeng/tmp/t03-hf-qualification-final-fixtures --junitxml=/data/ycfeng/tmp/t03-hf-qualification-final-20261108.xml --override-ini='junit_family=xunit2' --durations=5`: **50 PASS,57 deselected,69.58s**. The longer fsync fixture duration is an observation, not a runtime/GPU regression claim.

Black24.3.0, Ruff0.14.7, isort5.13.2, Python AST parsing and scoped diff-whitespace checks pass. Black checks the two implementation files plus submit tests in full and `test_swe_evaluation.py` lines508–1000, avoiding unrelated pre-existing compact fixtures. Commands used the existing cached binaries:

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/-kQQ6CPyKAABpsmE/bin/black --line-length 120 --check tests/manual/agent_opd/swe_evaluation.py tests/manual/agent_opd/submit_swe_evaluation.py tests/fast/test_swe_evaluation_submission.py
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/-kQQ6CPyKAABpsmE/bin/black --line-length 120 --line-ranges 508-1000 --check tests/fast/test_swe_evaluation.py
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/8QpD66osZqn5M69v/ruff-0.14.7.data/scripts/ruff check tests/manual/agent_opd/swe_evaluation.py tests/manual/agent_opd/submit_swe_evaluation.py tests/fast/test_swe_evaluation.py tests/fast/test_swe_evaluation_submission.py
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/YeSQ9F0UbXV9REOw/bin/isort --profile=black --line-length=120 --check-only tests/manual/agent_opd/swe_evaluation.py tests/manual/agent_opd/submit_swe_evaluation.py tests/fast/test_swe_evaluation.py tests/fast/test_swe_evaluation_submission.py
git diff --check -- tests/manual/agent_opd/swe_evaluation.py tests/manual/agent_opd/submit_swe_evaluation.py tests/fast/test_swe_evaluation.py tests/fast/test_swe_evaluation_submission.py
```

The known warnings are existing pyproject lint-settings, SWIG type and Torch JIT deprecations. No package/tool installation occurred.

## Exact parent command proposal

After parent prepares a separate owned qualification configuration retaining the accepted scientific/native contract, privately initializes the existing credentials and performs fresh admission, run from `integration_config.json`'s **local_mount**:

The new configuration's `owned_root` must contain this actual `/integration/.../hf/step_2` source, while `original_source`/`protected_sources` remain the accepted original inputs. Do not edit the already-enqueued baseline configuration or change its immutable contract to accommodate another point.

```bash
env STEPMIND_BACKEND=rjob \
  PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron \
  PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp \
  /data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  -m tests.manual.agent_opd.submit_swe_evaluation \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/integration_config.json \
  --configuration "${OWNED_QUALIFICATION_CONFIG:?parent-owned local configuration required}" \
  --point qualification.A-r256-smoke-HF3 \
  --receipt "${NEW_QUALIFICATION_RECEIPT:?new local admission receipt required}" \
  --qualification-checkpoint /mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/integration/r256/student/A/exp-1108-172407-535512/hf/step_2 \
  --qualification-attempt "${FROZEN_ATTEMPT_ID:?exact frozen task#attempt-N required}"
```

Expected source identity is the **parent-supplied observation**, successful3, rollout2, checkpoint_index2, weight_version3 and426 text tensors. The agent has not opened the real package/publication JSON. Do not call this HF50 or an original4B baseline. The worker's unchanged native role command is:

```text
<configuration.runtime.python> -B -m tests.manual.agent_opd.run_swe_evaluation --native --configuration <point/workers/server-reader/configuration.json> --point qualification.A-r256-smoke-HF3 --qualification-attempt <exact frozen task#attempt-N>
```

The existing worker creates this invocation after actual server identity validation; do not manufacture another scorer or bypass reader/deadline ownership. For the already-failed original point, parent reuses its original source/manifest/deadline after explicit RCA/resume rather than reusing this owned source or creating a new baseline identity.

## Remaining runtime evidence

Parent must rerun the real redacted environment equality probe, explicitly resume/relaunch under the retained deadline as applicable, and retain actual owned HF reload/model_info pure-text architecture/native version, complete request/tool/grader evidence, per-slot outcome or infrastructure failure, and reader cleanup. No native benchmark score or formal-cell acceptance is claimed by these CPU fixtures.

Scope self-check: the explicitly requested enqueue, submit handoff and known ACS environment repair are complete locally. No task/spec change is required; stop implementation/testing expansion here and return the real runtime acceptance frontier to parent. The native failure was already diagnosed by parent's exact red probe, so no additional hypothesis sweep or environment discovery was performed.
