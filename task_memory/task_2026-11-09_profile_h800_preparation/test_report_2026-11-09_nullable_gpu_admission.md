## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record CPU verification of explicit-unlimited GPU admission and existing finite handoff behavior. |

# Nullable GPU Admission Test Report

Task ID: `profile-h800-admission-20261109`.

## Environment

- Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`.
- Branch/base: `agent-opd-h800-capacity`, `c52991ac`.
- Interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`; `Python 3.12.13` from the exact command below. This is the supplied CPU environment, not a GPU worker; no conda environment changes were made.
- pytest: 9.1.1; Linux; repository `pyproject.toml` configuration.
- Modified code: `tests/manual/agent_opd/rjob_budget.py`; existing tests extended in `tests/fast/test_rjob_budget.py`.
- Consumer tests use synthetic platform API/backend fixtures. Temporary consumer artifacts use `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`.

## Exact Commands and Results

Commands ran from the working directory above.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python --version
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_rjob_budget.py -q -p no:cacheprovider
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_rjob_budget.py -q -p no:cacheprovider -k test_unlimited_allocation_requires_explicit_ceiling_and_matching_receipt
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_evaluation_submission.py -q -p no:cacheprovider -k 'fresh_snapshot_submit_and_receipt_share_the_lock or expired_personal_ceiling_denies_without_backend_submit'
git diff --check
```

| Run | Expected condition | Actual result | Verdict |
| --- | --- | --- | --- |
| Interpreter | Required CPU Python resolves | Python 3.12.13 | PASS |
| Budget baseline, before new tests/code | Existing finite suite passes | 10 passed, 0.20 s | PASS |
| New nullable allocation tests, before code change | Both selected scopes expose the unsupported None comparison | 2 failed, 23 deselected, 0.36 s; `TypeError` at `rjob_budget.py:57` | EXPECTED FAIL |
| Full affected budget suite, after code change | All original and new tests pass | 25 passed, 0.28 s | PASS |
| Full affected budget suite, after JSON receipt round-trip test | Persisted null receipt also passes without losing required fields | 25 passed, 0.25 s | PASS |
| Selected existing submission/receipt tests | Finite admission lock, resource preemption, submitted receipt and personal denial stay intact | 4 passed, 44 deselected, 0.90 s | PASS |
| Diff whitespace | No whitespace errors | Exit 0, no output | PASS |

Every pytest run reported the same two existing warnings: builtin types `SwigPyPacked` and `SwigPyObject` have no `__module__` attribute. No test failure remains after implementation.

## Acceptance Evidence

| Concern | Explicit expected values | Observed assertion result |
| --- | --- | --- |
| Unlimited pagination | With `ceiling=None`, committed 40 plus requested 160 is admitted; still read both pages with API timeout 20 | PASS; 2 native-API fixture calls, `ceiling_gpus=None`, admitted true |
| Active unlimited task policy | H800 requested 160, task commitments 80, other task commitments 72 excluded; None task ceiling admits without preemption even if personal ceiling is 56 | PASS; task committed count 80, then 88 after a new task Pending job; 2 fresh reads |
| Both policy ceilings explicitly None | Task scope counts 80/88 before expiry; personal scope counts 152/160 at expiry; requested 160 admitted without preemption | PASS in both scopes; no manufactured ceiling |
| Unlimited personal policy with finite active task policy | Before expiry, task ceiling 64 and committed 80 plus requested 160 must still select whole-job preemption | PASS; task scope, admitted true, preemptible true |
| Finite boundary/denial | Committed 40 plus request 16 equals finite ceiling 56 and admits; request 17 denies | PASS |
| Exact expiry | Task ceilings 64 and None both hand off to finite personal ceiling 56; personal commitments 50 plus request 1 admit, commitments 82 plus request 1 deny | PASS in all four combinations |
| Expiry during inventory read | Task/personal ceilings independently 64/56 or None; scope crossing must trigger a second personal read counting 72 | PASS; 2 reads in all four combinations, personal None admits and personal 56 denies; preemptible false |
| Allocation binding | Submitted job, requested count, committed count, creator, GPU tag, task ID, selected ceiling, evaluated scope and preemption must match | PASS; valid unlimited receipts accepted in both scopes; all enumerated tampered receipts rejected |
| Explicit null versus omission | JSON round-trip preserves None receipt/policy fields; missing selected policy fields raise KeyError and missing receipt ceiling raises ValueError | PASS; omitted values never default to unlimited |
| Finite approval and handoff | Finite receipt with a tampered None ceiling rejects; previously admitted receipts validate independently of current wall-clock expiry | PASS; original finite checks retained |
| Existing submission binding | Fresh read and submit occur under the same admission lock; finite committed counts 0/62/64 yield preemption false/false/true; expired personal commitment 56 plus request 2 does not submit | PASS; existing synthetic consumer tests verify resource and published receipt behavior |

## Verification Limits

- The 160-GPU requests are deliberately synthetic inputs larger than 32 and 128. They verify absence of a code count ceiling; they are not a proposed allocation or evidence of actual platform capacity.
- No config, platform credential, real API, RJob, GPU, source mount, cloud artifact or other worktree was modified or accessed for platform operations.
- No broad suite was run beyond the affected budget file and four selected consumer cases. Existing finite behavior is supported by the retained regression cases, not by an exhaustive proof over all integer inputs.
- H800 memory/topology, codesign resource availability, real submission and parent integration remain primary-agent responsibilities.
