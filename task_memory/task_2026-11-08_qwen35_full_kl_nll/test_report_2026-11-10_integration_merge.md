## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record D35 merge preflight and the input-interface reconciliation boundary. |

# Verified H800 branch integration

## Scope

D35 adopts the completed H800 D34 capacity result for this task's D1/D22 prerequisite. Merge the verified `agent-opd-h800-capacity` branch into `agent-opd-image`, preserving this task's accepted input contract and profile module. The upstream task keeps its own acceptance records and runs.

## Preflight

```bash
git merge-tree 20d0b3f4 agent-opd-image agent-opd-h800-capacity \
  > /data/ycfeng/tmp/agent-opd-image/merge-tree-profile-20261110.txt
git diff agent-opd-image agent-opd-h800-capacity -- \
  tests/manual/agent_opd/swe_inputs.py tests/manual/agent_opd/check_swe_inputs.py \
  > /data/ycfeng/tmp/agent-opd-image/profile-input-branches-20261110.diff
```

The installed Git does not support `merge-tree --write-tree`; that attempted read-only command returned `fatal: unknown rev --write-tree`. The supported three-tree invocation succeeded without changing either index or worktree. It identifies conflicts in `swe_inputs.py` and `check_swe_inputs.py` only.

The parent adapter/checker own the verified module pins, explicit prompt limit, source-kind registry, audited visual exclusions, native block mixer, 32×8 order and per-bank finished-conversation report. The candidate adapter uses an older single-loader interface and separate visual receipt. Keep the parent's accepted source contract; the merged native launcher and affected tests must consume that interface. Do not add a second compatibility constructor or rewrite historical source receipts. Native replay's verified response-budget preservation and network/session/scoring fixes remain required.

Existing tracked modifications before this step were task-owned documentation. They are being committed by their owners before merge. Untracked `.cortexkit/` remains untouched. The preparation branch's accepted artifacts are separately archived before consolidation.

## Verification state

Preflight and consolidation: PASS. Actual merge `55fba827`, reconciled caller checks and remaining integration boundaries are recorded in [the input merge report](test_report_2026-11-10_input_merge.md). Ticket02/03 integration is still pending. CPU test interpreter is `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python` (Python 3.12.13); torch, pytest, Ray and SGLang are available. Native profile acceptance remains at A's first formal successful update under D16, not an additional GPU smoke.

## Merge started

Parent D35 records committed as `6bdb4d32`; merge preflight as `eee754bc`. The candidate archived its reviewed terminal evidence as `0e6e8b1e9298638fd72651869692a41cad703b71`. With only unrelated untracked `.cortexkit/` in the parent, `git merge --no-ff --no-commit 0e6e8b1e9298638fd72651869692a41cad703b71` entered the predicted two-file conflict. Scoped resolution task `profile-input-merge-20261110` owns those files, their native launcher input wiring and directly affected test fixtures. The main session owns merge completion.

Checks on the consolidated evidence/document tree:

```bash
python3 -B tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll
python3 -B tests/manual/agent_opd/check_h800_capacity_evidence.py task_memory/task_2026-11-09_profile_h800_preparation/evidence
```

PASS: 26 documents, 88 links, 34 anchors, zero errors; retained terminal updates, bank visits, two student passes and text-only weight scope also PASS. These are archive/consolidation checks, not a new native run or completed profile integration.
