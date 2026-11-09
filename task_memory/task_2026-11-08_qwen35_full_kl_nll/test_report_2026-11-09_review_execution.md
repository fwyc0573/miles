## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Link completed real-source and terminal acceptance; retain the earlier launch-time observations as history. |
| 2026-11-09 | Record review repair checks and the approved in-place CPU audit launch. |

# Review repairs and execution

## Environment

- Worktree: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`, branch `agent-opd-image`; reviewed initial HEAD `0e94c522`.
- Worker/local validation: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python 3.12.13, torch 2.11.0+cu130, transformers 5.19.0; no conda activation.
- Submitter: `/data/ycfeng/tmp/stepmind-env/bin/python`, personal StepMind environment. Runtime imports are checked before submission.
- Job configuration: [source_audit_config.json](source_audit_config.json), 8 CPU, 0 GPU, 32 GB, one codesign replica, pinned company image. The local NFS source is `/data/ycfeng`; posttrain inputs are read in place. No dataset copy is made.

## Local checks

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_swe_input_pins.py
/data/ycfeng/tmp/stepmind-env/bin/python -B tests/manual/agent_opd/submit_swe1003_audit.py \
  --config task_memory/task_2026-11-08_qwen35_full_kl_nll/source_audit_config.json --dry-run
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B tests/manual/agent_opd/submit_swe1003_audit.py \
  --config /data/ycfeng/tmp/agent-opd-image/source-audit-submit-check-20261109/config.json --worker
```

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Native cached-module identity | Same verified object reuses; preimported, changed-pin, replaced-object cases reject | 4/4 tests pass, 0.19 s | PASS |
| Submitter dry run | Python 3.10 can build commands; no allocation; eight pinned sources and four module hashes | `submitted=false`, GPU=0, two commands, all four module hashes match | PASS |
| Synthetic worker sequence | Audit then parity without dependency installation | Exit 0; `SWE1003_IN_PLACE_AUDIT_AND_PARITY_PASS` | PASS |
| Synthetic source totals | 10 conversations, 21 assistants, 18 eligible; one visual and one overlength turn | Exact expected totals; both simulations repeat zero turns; parity PASS | PASS |
| Historical conversation queries | Arbitrary stored entry, missing update, baseline incomplete/nonpositive, retroactive ratios, offline rebuild | 10 profile tests PASS, 0.27 s; new test failed before the API fix | PASS |
| Profile cost after adding history index | Existing 200-update × 256-turn synthetic scenario, correct counts and rebuild | 200 updates, 51,200 observations, 589 conversations, no invalidation; 1.460 ms mean record/update, 1.316 ms mean all-conversation query, 12.943 MiB | PASS |
| Final affected fast suite | Profile and native import-cache regressions, including partial JSONL write | 15/15 PASS, 0.35 s; two existing SWIG deprecation warnings | PASS |
| Task links and dependency graph | All links resolve; six tickets form a DAG; 200×256×2 arithmetic holds | 72 links, 22 anchors, zero errors | PASS |
| Retained synthetic audit | Different instance metadata must not become a verified task count | Audit and retained output checker PASS; all expected counts and null task metrics match | PASS |

Final checks:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q \
  tests/fast/test_distillation_profile.py tests/fast/test_swe_input_pins.py
python3 tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll
git diff --check
```

The partial-write fault leaves one complete summary/observation pair and an orphan second observations row; the caller continues, later updates append nothing, and `rebuild()` rejects a complete-profile claim. Native token-count comparison and healthy trainer integration still await Ticket02; this CPU result does not certify them.

The documentation checker is retained unchanged from `/data/ycfeng/tmp/agent-opd-image/check_docs.py` at `tests/manual/agent_opd/check_profile_docs.py` following the final Standards review. `cmp` confirmed byte equality; the retained command above passed with 20 documents, 73 links, 22 anchors and zero errors after the final report link was added. The original temporary file remains available. This last documentation-only check does not change the 15-test code result.

Profile verification commands:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_distillation_profile.py -q \
  -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-history-query-20261109-pytest \
  --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-history-query-20261109-final
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.time_distillation_profile \
  --updates 200 --bank-turns 256 --open-conversations 32 --block-turns 8 --min-turns 19 --max-turns 162 \
  --max-tokens 4000 --trend-window 10 --baseline-updates 10 --baseline-turns 8 --seed 1234 \
  --temporary-root /data/ycfeng/tmp/agent-opd-image/profile-review-timing-20261109 \
  --output task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/profile-review-timing-20261109.json
```

The measurements are local synthetic profile costs, not GPU training throughput. The worker's startup log confirms the same Python/torch/transformers versions on the CPU RJob; the full source scan had not yet produced a completion marker at startup inspection.

The synthetic config derives from the real job config, changing only source/output/temp paths, context=2000, simulation=2x2 and 1x2, updates=2, turns/update=3, active=2, block=2, order draws=12, parity draws=30. This exercises the worker commands, not real-source acceptance. Complete command argv and output are in `/data/ycfeng/tmp/agent-opd-image/source-audit-submit-check-20261109/worker.log`.

## In-place CPU RJob

Submission uses `tests/manual/agent_opd/submit_swe1003_audit.py` after the authoritative runbook section 2 proxy/personal-auth initialization, with `STEPMIND_BACKEND=rjob`, `PYTHONPATH=/data/ycfeng/steptron`, `PYTHONNOUSERSITE=1`, and `PYTHONDONTWRITEBYTECODE=1`:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/tests/manual/agent_opd/submit_swe1003_audit.py \
  --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/source_audit_config.json
```

Launcher raw log: `/data/ycfeng/tmp/agent-opd-image/source-audit-launch-20261109.log`. The launcher stays alive throughout `spawn_tasks`. Audit and parity artifacts are written under `evidence/source-audit-20261109/`.

Job `exp-1109-031258-820360` was Running at `2026-11-08T19:14:27Z` (2026-11-09 local time). The personal Python client verified creator `i-fengyicheng`, non-preemptible, one audit replica, 8 CPU / 32000 Mi / 0 GPU, exact image digest, and NFS source `100.96.128.195:/data/ycfeng:/data/ycfeng`. Filtered receipt: [source-audit-admission-20261109.json](evidence/source-audit-admission-20261109.json). Business results and terminal state are pending. Ticket01 items 5–6 are not yet accepted.

**Subsequent acceptance:** job and replica finished Succeeded at2026-11-09T00:24:08Z. The actual source outputs and parity checks were inspected and Ticket01 items5–6 accepted; see [source audit report](test_report_2026-11-09_source_audit.md). The preceding pending statements describe the launch-time inspection only.

## Verification limits

- Exact first-user text is only a grouping proxy. Native SWE task/repository identity is not established; the corresponding metrics are null/unverified.
- Prefix-length bisection uses the configured preserving Qwen template and its append-only history behavior; this is not a general guarantee for other templates or `preserve_thinking=false`.
- D1/D22 are still blocked by upstream capacity acceptance. No training integration or formal-cell result is claimed.
