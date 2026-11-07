## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Close Spec P2 and the follow-up documentation Nit after pinned replay, actual 200-step audit, archival checks and source lint. |
| 2026-11-08 | Record full-task review, archival corrections, C monitor recovery and pinned-source collection; actual training-evidence verification is in progress. |

# Full-task review fixes — verification

## Scope and current verdict

User-selected fixed comparison: `git diff 5c2e44635298675167c7c55e067dcb294f9e9fa9...69f3cda52dd7ea59202f560fedc6cbcfe1679ad9`. `git rev-parse` resolves both commits; `git log --oneline 5c2e4463..69f3cda5` identifies44 task commits and the source/repository-doc diff has42 files. Source-only diff retained at `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-full-task-review-20261107.diff` (653794 bytes). The original task directory is the issue tracker. No external review publication or formal training restart is requested.

**Full-task review repair: PASS.** Original Standards review has0 findings; follow-up adds one stale-report Nit, now corrected. The original Spec P2 (native denominator/every-step targets) is CLOSED by actual collection, pinned native reduction verification and independent targeted review. No production arithmetic defect was established. C/P4 remain incomplete. Detailed independent reviewer scopes and citations are in `review_final_pairs.md`.

## Archival corrections

- `plan.md` previously stated that no final HF existed and used the old post-deletion10.456GiB inventory as current. Those statements now link the authoritative actual training/HF/storage reports.
- `summary.md` and the plan first distinguished verified update/D8/curve/HF gates from the reopened training-denominator/target-count subgate; they now record that subgate's verified closure below. Existing native PASS receipts are unchanged.
- `design.md` identifies initial source-inspection observations as historical, with execution state owned by plan/summary. The original denominator and target-count requirements are preserved.
- `qwen-p3-native-checkpoint.md` corrects premature full-pair completion, includes the requested review work and removes the contradictory duplicate D7 row.

## C lifecycle monitoring — PASS for reattachment, exit cause UNKNOWN

Personal Python API read on2026-11-07T15:43:54Z confirms exact C job`exp-1107-150849-814926`, creator`i-fengyicheng`, Pending, no replicas and queue availability0H800 against24 requested. `/proc/3578129` is absent, and an exact submitter-command scan finds no local `submit_qwen35.py`. Hostname and current NFS source remain`kun-workspace-vgen2`/`100.96.128.195`. The original shell-output file is no longer available; the original process's exit time and cause remain **UNKNOWN**. Platform queuing is not proof of a live launcher.

Reattach using the existing StepMind classes, with the usual personal auth from the runbook and Python3.10.6:

```python
from steptron.exp.base_exp import ResourceConfig
from steptron.utils.stepmind import RJob, get_rjob_client
from steptron.utils.stepmind_control import RJobWorkers

name = 'exp-1107-150849-814926'
client = get_rjob_client()
live = client.list([name])[0]
assert live.metadata.name == name
# Parent separately verifies exact creator, codesign label and source identity.
cfg = ResourceConfig()
job = RJob(name='by-qwen35-c-training', charged_group='codesign',
           cfg=cfg, exp_id='qwen35-c-training')
job.meta.name = name
workers = RJobWorkers(cfg=cfg, rjob=job)
workers.wait()
```

The executed display name comes from the existing object's showname annotation. No submit/stop method or new exit-stop hook is invoked. The new monitor is a reader of the existing job, not a recreated original launcher. `evidence/C-controller-reattach.json` records the same RJob UID`bc1ea9ed-316c-40b0-8763-a65f63c4ba06`, PID851709 and `submitted=false`; `evidence/C-controller-live.json` verifies that process's actual interpreter/cwd/state at15:56:29Z. Native wait continues in background shell`sh_1b6b56990001133juBZLOsqPMG`. C allocation, model execution and training acceptance remain pending.

## Pinned native-source acquisition — corrected PASS

The first worker `exp-1107-235320-883298` exits1 before Python:

```text
bash: line 2: cd: /data/ycfeng/sota-engine/miles: No such file or directory
ExitCode= 1
```

Cause: submitting from the repository while specifying `code_mount_point=/data/ycfeng` mounted the repository at that container root. Correct only the submission working directory to `/data/ycfeng`, as required by the existing frozen manifest, and assert `Path.cwd() == Path(cfg['local_mount'])` before submission. No dependency or image change. The earlier tool-level literal-path lstat denial created no RJob and is separate from this worker failure.

Corrected worker`exp-1107-235600-946937` Succeeded (23:56:00–23:56:24 local). Resources4CPU/0GPU/32 memory units, H200 label, pinned image, non-preemptible step_main and existing local mount. Worker command is the configured interpreter `-B -c` source collector: resolve `Path(importlib.util.find_spec('megatron.core').origin).parent.parent`, copy the13 explicit paths listed in `evidence/normalization-source-exp-1107-235600-946937.json`, then record Python/package versions and exact retained paths. Source directory is `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937/`. Python3.12.16, torch2.14.1+cu130, Megatron0.19.0+eb547f33e, torch-memory-saver0.0.10. This is source acquisition, not numerical acceptance.

RCA command, after the runbook's proxy/auth environment:

```bash
timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
  exp-1107-235320-883298 --replica exp-1107-235320-883298-cfcd2084 \
  --expected-creator i-fengyicheng \
  --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
  --start 2026-11-07T15:53:00Z --end 2026-11-07T15:54:00Z --timeout 20 \
  --output /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-normalization-source-exp-1107-235320-883298
```

Six queries succeed; both audit reads time out at20s, so collector exits1. This limits audit coverage without changing the positive workload-error evidence. Raw selected log is `/data/ycfeng/tmp/opencode-v2-tmp/opencode/normalization-source-exp-1107-235320-883298.log`. Original failed receipts are preserved.

## Actual training evidence — PASS, targeted review CLOSED

The actual collection and exact commands are owned by `test_report_2026-11-07_training_token_audit.md`: corrected pinned job `exp-1108-002213-053180` verifies all 200 rows/1600 completions. Original target totals A237618/B201819 equal native counts at every step; fully masked samples and eligible nonfinite entries are both zero. The first INCOMPLETE result is preserved. Full final JSON is retained as a lossless gzip, with derived per-step counts and verified round-trip equality.

Independent `test_report_2026-11-07_native_token_normalization.md` records pinned job `exp-1108-001008-300177`: all eight CPU/Gloo ranks pass unchanged native schedule/DDP/reducer/final-scaling execution, denominator54 versus29 survivors, max gradient error1.0949594e-7 and wrong-denominator distance2.7139211. The Spec reviewer accepts this as D12 normalization-semantic evidence; no historical CUDA replay criterion is added. The subsequent complete count-receipt review closes the combined P2 with no actionable remaining issue.

At `2026-11-07T16:23:48Z`, `evidence/review-verification-platform-20261108.json` independently confirms normalizer job/default Succeeded and C still Pending with queue availability8H800 against24 requested. C's reattached PID851709 remains alive with the expected interpreter/cwd. This supersedes the older0-card queue snapshot for current status; old receipts remain unchanged.

## Scoped source checks

The two manual probes pass the versions pinned by `.pre-commit-config.yaml`: Ruff0.14.7, isort5.13.2, Black24.3.0 and autoflake2.0.2. They are installed only under `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages` using the existing Python3.12 lint interpreter. An attempted system-Python venv lacks `ensurepip`; no system repair is performed. The exact packages are installed to the isolated target with that existing interpreter's pip.

Native formatter application preserves the complete function/class AST, allowing only contiguous import-order changes. An initial strict comparison correctly identified isort reordering three local imports in `_args`; after inspecting this exact difference, the comparison accounts for import order and passes. No normalization arithmetic or collector condition changes. Checks:

```bash
export PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages
PY=/data/ycfeng/tmp/mopd-repair-lint312/bin/python
FILES="tests/manual/agent_opd/audit_qwen35_training_tokens.py tests/manual/agent_opd/probe_qwen35_token_normalization.py"
$PY -B -m ruff check --no-cache $FILES
$PY -B -m isort --check-only $FILES
$PY -B -m black --check $FILES
$PY -B -m autoflake --check --remove-all-unused-imports $FILES
```

All four checks exit0. `python3 -B tools/lint_config_attribute_access.py` also exits0. Ruff's existing top-level-config deprecation warning is retained; the repository config is not changed.

## Archive verification

The selected archive consists of28 files: two manual probes, ten maintained task documents, eleven parsed JSON receipts, three original worker logs, the lossless complete audit gzip and its every-step Markdown table. All paths exist; every selected maintained document has Modification History. The old collector JSON remains INCOMPLETE, final JSON PASS, and gzip decompression equals the original8,564,537bytes exactly. Total selected size is approximately1.31MB, with the full uncompressed final receipt retained locally.

`git diff --cached --check` initially finds one trailing blank line in the generated target-count table. After removing that line without changing counts, the staged check passes. The exact staged path set equals the28-file selection manifest at `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-stage-files.json`. Original worker logs/receipts are unchanged. No production module or pre-existing unrelated file belongs to this commit.
