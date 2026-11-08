## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Retain original pre-baseline mutations in a fresh-sandbox runner; record current control, two detected mutants and one stale replacement without changing historical results. |
| 2026-11-08 | Record the ticket 03 module checks: fast test, injected bugs, synthetic 200 × 256 timing and memory. |

# Test report — ticket 03, Distillation profile module

Historical scope (2026-11-08): the module part of [ticket 03](tickets/03-distillation-profile.md) (criteria 1–4 and 6). The integration into `SweReplay.on_train_result` (criterion 5) was not tested here. The separate 2026-11-09 section records retained-script execution only and does not replace the historical module or timing evidence.

## Historical environment (2026-11-08)

- Worktree `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`, branch `agent-opd-image`; code under test is uncommitted on top of `f31c4bc5`:
  - `tests/manual/agent_opd/distillation_profile.py` (the module);
  - `tests/fast/test_distillation_profile.py` (fast CPU test, implicit `stage-a-cpu` registration);
  - `tests/manual/agent_opd/time_distillation_profile.py` (timing script, manual only).
- Python 3.12.13 at `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, pytest 9.1.1. No GPU. All commands run from the worktree root.
- No formatter is installed in this environment (`ruff`, `black` and `pre-commit` are absent). New lines were checked with `awk 'length > 119'` against the black line length in `pyproject.toml`; no new line exceeds it.

## Historical commands (2026-11-08)

```bash
# 1. Fast test
timeout 120s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q -p no:cacheprovider \
  tests/fast/test_distillation_profile.py

# 2. Injected bugs: copy the module and the test into a fresh directory, apply one text replacement, run the test
timeout 300s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python /data/ycfeng/tmp/agent-opd-image/inject_profile_bugs.py \
  /data/ycfeng/tmp/agent-opd-image/mutants-2

# 3. Timing, uniform conversation lengths 19–464 (the sample's min and max)
timeout 600s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.time_distillation_profile \
  --updates 200 --bank-turns 256 --open-conversations 32 --block-turns 8 --min-turns 19 --max-turns 464 \
  --max-tokens 4000 --trend-window 10 --seed 1234 \
  --temporary-root /data/ycfeng/tmp/agent-opd-image/profile-timing \
  --output task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/profile-timing.json

# 4. Timing, uniform lengths 19–162 (mean 90.5, close to the sample mean 90.69)
timeout 600s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.time_distillation_profile \
  --updates 200 --bank-turns 256 --open-conversations 32 --block-turns 8 --min-turns 19 --max-turns 162 \
  --max-tokens 4000 --trend-window 10 --seed 1234 \
  --temporary-root /data/ycfeng/tmp/agent-opd-image/profile-timing-mean-length \
  --output task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/profile-timing-mean-length.json
```

Evidence: [profile-timing.json](evidence/profile-timing.json), [profile-timing-mean-length.json](evidence/profile-timing-mean-length.json). The profile files written by runs 3 and 4 stay in their temporary roots under `distillation_profile/`.

## Historical results by acceptance criterion (2026-11-08)

| # | Check | Expected | Actual | Result |
| --- | --- | --- | --- | --- |
| 1 | Structures of spec S5 | column-wise append-only arrays for observations; update rows with an RKL-best pointer; per-conversation entries with best and latest; `group_id → c_id` and `(c_id, t_id) → latest row` lookups | `array` columns `update_id, c_id, t_id, replay_num` (`i`), `rkl_sum, nll_sum` (`d`), `tokens` (`q`) plus a `uid` list; `UpdateRow` list with `_best_update`; `_Conversation` entries with `best` index, latest = last entry; `_c_ids` and per-conversation `cells` | PASS |
| 1 | Queries of spec S4 | single update, RKL-best update, macro RKL trend and recovery gap; per conversation: latest, best, trend, recovery gap, alive; the all-conversation form; table cell and row lookup | `update`, `best_update`, `rkl_trend`, `recovery_gap`, `conversation`, `conversation_trend`, `conversation_states`, `cell`, `observation`, `conversation_id` | PASS |
| 2 | Hand-computed sequence of 4 updates, 10 turns, 4 conversations (`test_hand_computed_profile`) | values computed by hand in the test | all asserted values equal; covered cases below | PASS |
| 2 | Several turns of one conversation in one update | equal-weight mean of the turns' RKL (D6), not token-weighted | update 1, conversation 0: turns RKL 0.5 and 1.5 → entry RKL 1.0 (token-weighted would be 0.833) | PASS |
| 2 | Skipped update | no call; the next successful update has the next `update_id`; an attempt number instead is rejected | contiguous ids accepted; `update_id=2` as the first call marks the profile unverified (`attempt_id` case) | PASS |
| 2 | Window k not reached | macro trend None while `U ≤ k`; conversation trend None without a reference entry | `rkl_trend(1)` None at U=1; `rkl_trend(4)` None at U=4; conversations 1 and 3 None at k=2 | PASS |
| 2 | Tied best | earliest update stays best | macro: updates 2 and 4 both RKL 0.4375, best stays 2; conversation 2: updates 3 and 4 both RKL 0.5, best stays 3 | PASS |
| 2 | Table mapping | best entry's rows equal the `(c_id, t_id)` cells; columns have different heights | conversation 0 best rows → `cell(0, 3)`; column 0 has t_id 1–4, column 3 has t_id 1 only; `cell(1, 3)` None | PASS |
| 2 | `alive` changes | False after the successful update that trains the bank reporting the last turn; a conversation never trained is ignored | conversation 1 False after update 2, conversation 0 after update 3; `gX` has no `c_id` | PASS |
| 2 | Record rows join bank turns by `uid` | record row order may differ from slot order | the test passes record rows in reverse slot order | PASS |
| 3 | Two JSONL files (spec S6); offline rebuild equals memory (`test_files_rebuild_the_profile`) | exact first `observations.jsonl` line; last `updates.jsonl` line equals `summary()`; rebuilt updates, best, conversations, states for k = 1–4 and all 10 observations equal | all equal | PASS |
| 3 | Rebuild checks each update | a changed `updates.jsonl` line is rejected | `rkl` of line 3 increased by 1.0 → `ValueError: Update 3 does not reproduce its updates.jsonl line` | PASS |
| 4 | Write error (`test_write_error_marks_unverified`) | logged; `unverified_from` = first failing update; later updates ignored; no exception reaches the caller | directory under a regular file: `unverified_from=1`, `latest_update=1`, log contains "unverified from update 1" | PASS |
| 4 | Row count mismatch (`test_inconsistent_record_marks_unverified`) | same soft-gate behavior | missing row, duplicate row and attempt-number cases: `unverified_from` set, nothing added, error logged | PASS |
| — | Fast test run | 6 passed | `6 passed, 2 warnings in 0.28s` (the warnings are SWIG import deprecations from the environment) | PASS |
| — | Injected bugs are caught | the unpatched copy passes; each bug fails at least one test | unpatched: 6 passed; `<` → `<=` in the conversation best (tie moves best): 1 failed; token-weighted conversation mean: 1 failed; macro trend reference off by one: 1 failed; script verdict PASS | PASS |
| 6 | Synthetic 200 × 256 run (two length settings below) | status PASS: no unverified update, rebuilt summary equals the live one; 51,200 observations | both runs PASS, 200 updates, 51,200 observations | PASS |

## Historical timing and memory (2026-11-08)

Synthetic order: 32 open conversations taken 8 turns at a time in round robin (no length rejection), tokens per turn uniform in 1–4,000, random sums. `group_id` strings have the real form `file_sha256:index`. Each per-update time includes building the observations, the JSONL writes and `summary()`; the query time is `conversation_states(10)` over all conversations seen so far, measured after every update.

| Quantity | Lengths 19–464 | Lengths 19–162 (mean 90.5) |
| --- | --- | --- |
| Conversations seen / alive at the end / with a trend at k = 10 | 234 / 31 / 189 | 589 / 31 / 302 |
| `record_update` per update: mean / median / p95 / max | 1.65 / 1.62 / 1.84 / 3.54 ms | 1.82 / 1.81 / 2.05 / 3.62 ms |
| `record_update`, all 200 updates | 0.33 s | 0.36 s |
| `conversation_states(10)` per query: mean / p95 / max | 0.090 / 0.151 / 0.158 ms | 0.191 / 0.351 / 0.376 ms |
| Offline rebuild from the two files | 0.22 s | 0.25 s |
| Profile memory (tracemalloc, in-memory profile, inputs dropped) | 12.85 MB | 12.63 MB |
| `updates.jsonl` / `observations.jsonl` | 95,707 B / 6,886,741 B | 95,648 B / 6,905,025 B |

Expectation: the profile is cheap next to one update. No formal cell has run yet, so the comparison point is ticket 01's measurement: drawing the raw turns of one 256-turn bank alone takes about 2.1 s, before rendering, rollout and training. Observed: under 4 ms per update and under 0.4 ms per all-conversation query, at most 0.37 s for all 200 updates. The 19–162 run gives 589 conversations, close to spec S2's estimate of about 550–580, and 302 of them (about half) have a trend at k = 10, as S2 item 6 estimates.

Memory breakdown of the 19–464 profile (one-off `sys.getsizeof` count, `/data/ycfeng/tmp/agent-opd-image/memory_breakdown.py`): numeric columns 2.00 MB, `uid` strings 5.48 MB (mean 71 characters) plus their list 0.42 MB, `(c_id, t_id)` lookup dicts 1.95 MB; the remaining about 3 MB are per-conversation entry lists, Python ints held by the lookups and lists, and `group_id` strings. Spec S5 estimated about 2 MB from the numeric columns alone; it is corrected to the measured total in the same change.

## Historical limits (2026-11-08)

- Synthetic data: no length rejection, no timeout gaps and no real record. The join with a real optimizer-step record, the per-bank finished report from ticket 01 and the estimator label from ticket 02 are tested in the integration part of ticket 03.
- Timing is single-process wall time on a shared CPU host and varies between runs; the values show the order of magnitude, not a budget.
- Writes go to local disk under `/data/ycfeng/tmp`. In the formal cells the profile directory sits in the cell evidence directory; its write time there is not measured here.
- A write failure between the two files leaves them with different line counts; rebuild then raises an error instead of rebuilding a partial profile. This is the expected behavior for an unverified profile and was not separately injected.

## Retained script and current mutation execution (2026-11-09)

Retained script: `tests/manual/agent_opd/inject_profile_bugs.py`, adapted from `/data/ycfeng/tmp/agent-opd-image/inject_profile_bugs.py`, which remains untouched. The original three replacement texts are preserved; the implementation and test are copied from the repository-relative source into a fresh temporary sandbox. The baseline script reuses this runner rather than duplicating its sandbox execution logic; its current result is in [the remaining-gap report](test_report_2026-11-08_profile_remaining_gap.md#retained-script-and-current-mutation-execution-2026-11-09).

Exact executed invocation, from the repository root, Python 3.12.13 and pytest 9.1.1 in the same CPU environment:

```bash
timeout 300s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.inject_profile_bugs \
  --temporary-root /data/ycfeng/tmp/agent-opd-image
```

Each executed copy uses the current Python with `-B -m pytest -q -p no:cacheprovider --rootdir <copy> --basetemp <copy>/pytest-tmp tests/fast/test_distillation_profile.py`, with the working directory and `PYTHONPATH` set to that copy. Logs and `results.json` are retained at `/data/ycfeng/tmp/agent-opd-image/profile-mutations-xvd4k2wp/`.

| Current check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Unpatched control | pytest exit 0 | 10 passed in 0.24 s | PASS |
| `tie_moves_best` | Exactly one replacement; pytest exit 1 | 1 failed, 9 passed in 0.28 s | PASS |
| `trend_off_by_one` | Exactly one replacement; pytest exit 1 | 1 failed, 9 passed in 0.30 s | PASS |
| Original pre-baseline `token_weighted_conversation_mean` | Exact historical text must exist to execute the mutation | 0 replacement matches; `STALE`; pytest not run for this mutant | NOT VERIFIED |
| Complete historical mutation set on current source | All mutants executable and detected | `status: FAIL`, exit 1 because one replacement is stale, not because the control fails | INCOMPLETE |

The stale replacement names the pre-baseline implementation's `rkl = sum(...)` expression, which no longer exists after the baseline code switched to `turn_rkl`. It is retained for provenance rather than silently rewritten or counted as detected. The current baseline mutation script contains the applicable token-weighted-mean mutation and detected it, as reported separately. No repository module was overwritten. No new timing, memory, formal-training, or integration result is claimed by this retention task.
