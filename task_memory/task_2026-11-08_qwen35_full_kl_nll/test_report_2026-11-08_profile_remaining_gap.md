## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Retain baseline mutation script with a shared fresh-sandbox runner; record the current 10-test control and 8 detected mutants separately from historical timing and results. |
| 2026-11-08 | Record the remaining-gap checks: fast test, injected bugs, re-measured 200 × 256 timing. |

# Test report — ticket 03, remaining gap and run-relative gap (D28–D32)

Historical scope (2026-11-08): the module criterion added to [ticket 03](tickets/03-distillation-profile.md) for D28–D32 — the run baseline and the per-conversation baseline, the two remaining gaps, the run-relative gap, and the trend and recovery gap restated in baseline units ([spec S4](spec.md#s4-distillation-profile-的内容d3d6d9d13d28d31)). The earlier criteria were verified in [the module report](test_report_2026-11-08_distillation_profile_module.md); its checks were re-run unchanged at that time. The separate current section below covers script retention and mutation execution only, not training integration or new timing.

## Historical environment (2026-11-08)

- Worktree `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`, branch `agent-opd-image`; code under test is uncommitted on top of `e30a07df`:
  - `tests/manual/agent_opd/distillation_profile.py` (the module);
  - `tests/fast/test_distillation_profile.py` (fast CPU test, implicit `stage-a-cpu` registration);
  - `tests/manual/agent_opd/time_distillation_profile.py` (timing script, manual only; gained `--baseline-updates` and `--baseline-turns`).
- Python 3.12.13 at `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, pytest 9.1.1. No GPU. All commands run from the worktree root.
- No formatter is installed in this environment (`ruff`, `black` and `pre-commit` are absent). The three files were checked against the 119-character black line length in `pyproject.toml` (`/data/ycfeng/tmp/agent-opd-image/r262.py`): no line exceeds it.

## Historical commands (2026-11-08)

```bash
# 1. Fast test
timeout 300s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q \
  tests/fast/test_distillation_profile.py

# 2. Injected bugs: copy the module and the test into a fresh directory, apply one text replacement, run the test
timeout 600s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python \
  /data/ycfeng/tmp/agent-opd-image/inject_profile_bugs_baselines.py \
  /data/ycfeng/tmp/agent-opd-image/mutants-baselines

# 3. Timing, uniform conversation lengths 19–464 (the sample's min and max)
timeout 600s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.time_distillation_profile \
  --updates 200 --bank-turns 256 --open-conversations 32 --block-turns 8 --min-turns 19 --max-turns 464 \
  --max-tokens 4000 --trend-window 10 --baseline-updates 10 --baseline-turns 8 --seed 1234 \
  --temporary-root /data/ycfeng/tmp/agent-opd-image/profile-timing-rg \
  --output task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/profile-timing-remaining-gap.json

# 4. Timing, uniform lengths 19–162 (mean 90.5, close to the sample mean 90.69)
timeout 600s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.time_distillation_profile \
  --updates 200 --bank-turns 256 --open-conversations 32 --block-turns 8 --min-turns 19 --max-turns 162 \
  --max-tokens 4000 --trend-window 10 --baseline-updates 10 --baseline-turns 8 --seed 1234 \
  --temporary-root /data/ycfeng/tmp/agent-opd-image/profile-timing-rg-mean \
  --output task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/profile-timing-remaining-gap-mean-length.json
```

Evidence: [profile-timing-remaining-gap.json](evidence/profile-timing-remaining-gap.json), [profile-timing-remaining-gap-mean-length.json](evidence/profile-timing-remaining-gap-mean-length.json). The earlier files `profile-timing.json` and `profile-timing-mean-length.json` keep the pre-baseline numbers the module report quotes. The profile files written by runs 3 and 4 stay in their temporary roots under `distillation_profile/`.

## Historical results (2026-11-08)

The shared hand-computed sequence runs with a 2-update run baseline and a 2-turn conversation baseline, so every baseline state appears in one sequence. Run baseline `b = (0.75 + 0.4375) / 2 = 0.59375`.

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Run baseline not yet complete (update 1) | baseline, remaining gap, recovery gap all undefined | all three `None` | PASS |
| Run baseline complete (update 2) | `b = 0.59375` | equal | PASS |
| Remaining gap inside the baseline window (D28 retroactive rule) | update 1 readable after the baseline exists: `0.75 / b` | equal | PASS |
| Macro trend sign (D29) | `G(1) − G(2) = (0.75 − 0.4375) / b`, positive because RKL went down | equal | PASS |
| Macro trend with a reference inside the baseline window | at update 3, k = 2: `(0.75 − 0.5) / b` | equal | PASS |
| Macro trend window not reached | `None` while `U ≤ k` | `rkl_trend(4)` at U = 4 is `None` | PASS |
| Macro recovery gap (D30) | at update 3: `(0.5 − 0.4375) / b`; at update 4, where the latest ties the best: 0.0 | equal | PASS |
| Conversation baseline inside one entry | g1: `(0.5 + 1.5) / 2 = 1.0` | equal | PASS |
| Conversation baseline across two updates | g0: `(0.5 + 0.25) / 2 = 0.375`, complete at update 2; g2: 0.75, complete at update 3 | equal | PASS |
| Conversation baseline never complete | g3, one turn only: `None`, and its remaining gap, trend and recovery gap `None` | equal | PASS |
| Baseline full mid-update (`test_baseline_stops_at_its_turn_count`) | an update offering 2 turns with 1 baseline slot left uses only the first of them: baseline `(1.0 + 0.5) / 2 = 0.75`, entry 1.75, remaining gap `1.75 / 0.75` | equal | PASS |
| Conversation remaining gap and run-relative gap (D31) | latest over own baseline `(0.5, 0.25/0.375, 0.5/0.75, None)`; latest over `b` `(0.5/b, 0.25/b, 0.5/b, 0.375/b)`, defined for g3 as well | equal | PASS |
| Conversation trend and recovery gap in baseline units | k = 2: `(0.5, None, (1.0 − 0.5)/0.75, None)`; k = 1: `((0.25 − 0.5)/1.0, (0.5 − 0.25)/0.375, 0.0, None)`; recovery `(0.25, 0.0, 0.0, None)` | equal | PASS |
| Baseline not positive (`test_nonpositive_baseline_leaves_its_values_undefined`) | a conversation with baseline −0.5: remaining gap and recovery gap `None`, run-relative gap still `−1.0` against the positive run baseline 0.5; counts 1 with a baseline, 1 not positive | equal | PASS |
| Lengths rejected | a baseline length of 0 raises | `ValueError: Trend window 2 and baseline lengths 0 updates, 2 turns must all be positive` | PASS |
| `updates.jsonl` fields (spec S6) | `baseline_updates`, `baseline_turns`, `baseline`, `remaining_gap`, the two baseline counts; undefined values as null | present; last line equals `summary()`; `(2, 2, 0.59375, 0.4375/0.59375)` and counts `(seen 4, with baseline 3, not positive 0, with trend 2, alive 2)` | PASS |
| Offline rebuild | rebuilt profile reproduces every `updates.jsonl` line and carries the same two lengths and run baseline | equal; a changed line is still rejected | PASS |
| Fast test run | all tests pass | `9 passed, 2 warnings in 0.29s` (the warnings are SWIG import deprecations from the environment) | PASS |
| Injected bugs are caught | the unpatched copy passes; each bug fails at least one test | unpatched 9 passed; 8 mutants each failed: tie moves best, token-weighted conversation mean, macro trend off by one, conversation trend sign flipped, run-baseline window off by one, a non-positive baseline allowed to divide, conversation baseline taking every turn of an update, run-relative gap using the conversation's own baseline; script verdict PASS | PASS |
| Synthetic 200 × 256 runs | status PASS, 51,200 observations, no unverified update | both runs PASS, 200 updates, 51,200 observations | PASS |

The first mutation run left `conversation_baseline_takes_every_turn` alive: no conversation in the data offered more turns in one update than its baseline still needed. `test_baseline_stops_at_its_turn_count` was added for that case, which rejections make reachable in a real run, and the mutant then failed.

## Historical timing and memory (2026-11-08)

Same synthetic order as the module report: 32 open conversations taken 8 turns at a time in round robin, tokens per turn uniform in 1–4,000, random sums, `group_id` of the real form `file_sha256:index`. Per-update time includes building the observations, the JSONL writes and `summary()`; the query time is `conversation_states(10)` over all conversations seen so far, measured after every update. Pre-baseline columns are the module report's numbers on the same seed and settings.

| Quantity | 19–464, now | 19–464, before | 19–162, now | 19–162, before |
| --- | --- | --- | --- | --- |
| Conversations seen / alive / with a trend at k = 10 | 234 / 31 / 189 | 234 / 31 / 189 | 589 / 31 / 302 | 589 / 31 / 302 |
| Conversations with a baseline / with one not positive | 234 / 0 | — | 589 / 0 | — |
| Run baseline / remaining gap at update 200 | 0.503 / 0.956 | — | 0.507 / 0.990 | — |
| `record_update` per update: mean / median / p95 / max | 1.73 / 1.71 / 1.92 / 2.76 ms | 1.65 / 1.62 / 1.84 / 3.54 ms | 1.96 / 1.92 / 2.59 / 2.80 ms | 1.82 / 1.81 / 2.05 / 3.62 ms |
| `record_update`, all 200 updates | 0.35 s | 0.33 s | 0.39 s | 0.36 s |
| `conversation_states(10)` per query: mean / p95 / max | 0.82 / 1.41 / 3.04 ms | 0.090 / 0.151 / 0.158 ms | 2.02 / 3.32 / 19.34 ms | 0.191 / 0.351 / 0.376 ms |
| Offline rebuild from the two files | 0.23 s | 0.22 s | 0.29 s | 0.25 s |
| Profile memory (tracemalloc, inputs dropped) | 12.86 MB | 12.85 MB | 12.67 MB | 12.63 MB |
| `updates.jsonl` / `observations.jsonl` | 134,331 B / 6,886,741 B | 95,707 B / 6,886,741 B | 134,319 B / 6,905,025 B | 95,648 B / 6,905,025 B |

Expectation and observation:
- Per-update cost stays within a few percent of the earlier measurement: the baselines add two running sums and `summary()` now counts baselines instead of building the full per-conversation state. A first version that let `summary()` call `conversation_states` cost 2.39 ms and 3.64 ms per update; that call was removed, which is why the numbers above are close to the pre-baseline ones.
- The all-conversation query is about 10 times its earlier cost, 0.8 ms at 234 conversations and 2.0 ms at 589, because it now returns four value tuples built from per-conversation views, so each formula has one definition shared with the single-conversation query. It is O(conversation count) as spec S5 states, is not on the per-update path, and stays far below one update.
- Memory is unchanged; `updates.jsonl` grows about 40% (190 B more per line) from the new fields, 134 kB over 200 updates.
- Sanity check on the synthetic data: its per-turn values are random with a fixed distribution, so no trend exists; the remaining gap at update 200 is 0.956 and 0.990, near 1 as expected, and no conversation has a baseline that is not positive, since the synthetic sums are all positive.

## Historical limits (2026-11-08)

- Synthetic data: no length rejection, no timeout gaps, no real record, and all sums positive. The not-positive baseline and the baseline that fills mid-update are covered only by the hand-computed tests.
- Timing is single-process wall time on a shared CPU host and varies between runs; the 19.34 ms maximum of one query is one outlier in 200, most likely array growth or garbage collection. The values show the order of magnitude, not a budget.
- The two default lengths (10 updates, 8 turns) are config values (D32); the tests use 1 or 2 for hand-computable values, and the timing runs use the defaults. Whether the defaults suit the real data depends on the training-turn distribution, which the source audit has not yet produced.
- No formal cell has run, so no real RKL has been divided by a real baseline yet.

## Retained script and current mutation execution (2026-11-09)

Retained entrypoint: `tests/manual/agent_opd/inject_profile_bugs_baselines.py`; shared runner: `tests/manual/agent_opd/inject_profile_bugs.py`. The original `/data/ycfeng/tmp/agent-opd-image/inject_profile_bugs_baselines.py` remains untouched. All original replacement texts are preserved. The source repository is derived from the retained runner's location; the runner creates a fresh `tempfile.mkdtemp` sandbox outside that repository, copies the module and fast test there, and never mutates repository code. A replacement must match exactly once; otherwise it is `STALE`. Only pytest exit 1 counts as detecting a mutant, so collection/import failures do not produce a false PASS.

Exact executed invocation, from the repository root, Python 3.12.13 and pytest 9.1.1 in the same CPU environment:

```bash
timeout 600s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.inject_profile_bugs_baselines \
  --temporary-root /data/ycfeng/tmp/agent-opd-image
```

Pytest invocation for each sandbox copy uses the executing Python with `-B -m pytest -q -p no:cacheprovider --rootdir <copy> --basetemp <copy>/pytest-tmp tests/fast/test_distillation_profile.py`; its working directory and `PYTHONPATH` are that copy. The runner retains each `pytest.log` and `results.json` at `/data/ycfeng/tmp/agent-opd-image/profile-baseline-mutations-1hog9gz6/`.

| Current check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Unpatched control | pytest exit 0 | 10 passed in 0.25 s | PASS |
| All eight retained mutants | Every replacement matches once; pytest exit 1 for each | Eight detected; no stale replacement; failed-test counts 1, 3, 1, 1, 3, 1, 1, 2 in script order | PASS |
| Script verdict | Exit 0 only when control and all mutants satisfy expectations | `status: PASS`, exit 0 | PASS |

This run exercises the current source snapshot, including the concurrently added historical-query test, but makes no claim to own or review that implementation. The 2026-11-08 9-test result and timing measurements above remain historical; neither timing run, memory measurement, formal training, nor the integration workflow was re-executed here.

Additional executed retention checks (same Python, repository-root working directory):

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import ast
from pathlib import Path
from tests.manual.agent_opd.inject_profile_bugs import REPO_ROOT, run_mutations

for name in ('inject_profile_bugs.py', 'inject_profile_bugs_baselines.py'):
    def mutations(path):
        tree = ast.parse(path.read_text())
        return next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == 'MUTATIONS' for target in node.targets))
    assert mutations(REPO_ROOT / 'tests/manual/agent_opd' / name) == mutations(Path('/data/ycfeng/tmp/agent-opd-image') / name)
try:
    run_mutations({'unpatched': None}, REPO_ROOT, 'must-not-write-')
except ValueError as error:
    assert str(error) == 'Mutation sandboxes must be outside the repository'
else:
    raise AssertionError('Repository sandbox was not rejected')
for name in ('make_and_check_swe1003_synthetic.py', 'inject_profile_bugs.py', 'inject_profile_bugs_baselines.py'):
    ast.parse((REPO_ROOT / 'tests/manual/agent_opd' / name).read_text())
print('PASS: retained mutation dictionaries equal originals; repository sandbox rejected; three scripts parse')
PY
```

Observed: exit 0 and the printed PASS line. This verifies both retained mutation dictionaries equal the originals, repository sandbox rejection occurs before creating files, and all three retained scripts parse. A scoped `git diff --check` over the three scripts and three updated reports also exited 0 with no whitespace errors; no commit was made.
