## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record the ticket 01 acceptance run on the real pinned source copies. |

# Test report — ticket 01, interleaved turn order

## Environment

- Worktree `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`, branch `agent-opd-image`; code under test is the uncommitted change to `tests/manual/agent_opd/swe_inputs.py` and `tests/manual/agent_opd/check_swe_inputs.py` on top of `beb996a4`.
- Python 3.12.13 at `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python` (CPU environment of the reused task), transformers 5.19.0. No GPU.
- Native loader `step3p6_mopd_online_turn_loader_0710.py`, sha256 `ffd9bb31…becacc8`, from the `step3p6-replay-v1` Steptron worktree.
- Source copies: the reused task's pinned copy `/data/ycfeng/tmp/qwen35-swe-full-r256/swe-sources-20261023` with its `COPY_COMPLETE.json`.

## Command

```bash
timeout 900s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.check_swe_inputs \
  --source-root /data/ycfeng/tmp/qwen35-swe-full-r256/swe-sources-20261023 \
  --source-manifest /data/ycfeng/tmp/qwen35-swe-full-r256/swe-sources-20261023/COPY_COMPLETE.json \
  --native-loader /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/playground/users/wyx/MOPD/step3p6_mopd_online_turn_loader_0710.py \
  --native-loader-sha256 ffd9bb314c2ad5be44c52e2bd11684b51204aaa82b63e298d557b9834becacc8 \
  --native-recipe /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/playground/users/wyx/MOPD/step3p6_mopd_turn_5experts_fullyasync_tis_no_kl_0710_h200.py \
  --tokenizer /data/ycfeng/tmp/swe-model-pairs-20261103/Qwen/Qwen3.5-4B \
  --chat-template miles/utils/chat_template_utils/templates/qwen3.5_fixed.jinja \
  --rollout-max-context-len 131072 --active-conversations 32 --block-turns 8 \
  --order-draws 2048 --parity-draws 512 \
  --temporary-root /data/ycfeng/tmp/agent-opd-image/t01 \
  --output-root task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence \
  --model-source-receipt task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/model-sources-exp-1108-144027-369537.json
```

Result: exit 0 after 69 s; stdout `{"status": "PASS", "prefix_checks": 7, "lengths": [1547, 2221, 28111, 72857, 107274, 146694, 181478], ...}`. Raw log: `/data/ycfeng/tmp/agent-opd-image/t01/input-parity.log`. Evidence: [input-parity.json](evidence/input-parity.json), [input-config.json](evidence/input-config.json), [input-source-manifest.json](evidence/input-source-manifest.json).

## Results by acceptance criterion

| # | Check | Expected | Actual | Result |
| --- | --- | --- | --- | --- |
| 1 | New config fields and their defaults | `swe_active_conversations=1`, `swe_block_turns=8` | as expected; the real `compute_custom_function_config` merge carries 32 and 8 from the command line (`configuration.config`) | PASS |
| 1 | Adapter built from a shared cursor, M native sources and the native block mixer; old single-source path removed | `len(sources) == identity.active_conversations == M`, `mixer.trajectory_block_turns == identity.block_turns` | 32 and 8 asserted; the `self.native` attribute is removed | PASS |
| 1 | Global draw index recorded | every sample's `metadata.source` carries `draw_index`; the save receipt counts draws | e.g. the turn after the real over-length rejection has `draw_index=6`, `sample_index=5`; synthetic receipt `emitted_turns=8` | PASS |
| 2 | Existing checks at M = 1 on the real copies | the four existing sections equal the reused task's evidence | `diff` against `task_2026-11-08_qwen35_swe_full_r256/evidence/input-parity.json`: `actual_prefix_checks`, `boundary_checks`, `length_rejection`, `four_cursors` identical except the two new fields `draw_index`, `remaining_turns` | PASS |
| 2 | First 512 draws at M = 1 equal one native `OnlineTrajectoryTurnSource` | whole items equal (stronger than uid equality); `remaining_turns` equal | equal for all 512 draws, 6 conversations | PASS |
| 3 | M = 32, block = 8, first 2,048 raw mixer draws (no rendering) | turns ascending without gaps in each conversation; conversations open in file order; at most 32 open | all three hold; `remaining_turns` equals an independent count of assistant turns minus the ordinal | PASS |
| 3 | Open conversations | 32 at most | max 32; min 29 after the first window | PASS |
| 3 | Conversations per 256-draw window | about 32 | `[32, 32, 32, 32, 33, 33, 32, 32]` | PASS |
| 3 | Turns per conversation per window | mostly 8 | windows 1–4 and 7: all 32 conversations have 8; other windows have 29–30 conversations with 8, and the remaining conversations have 2, 3, 5, 6, 6, 6, 7, 7, 10, 12 | PASS (explained below) |
| 3 | Longest consecutive run of one conversation | 8 | 8; `runs_longer_than_block` is empty; runs: 251 × 8, 2 × 7, 4 × 6, 1 × 2 | PASS |
| 4 | Synthetic fixture (2 files, M = 2, block = 2, character-count tokenizer, context 512) | calls `get_samples(2, 3, 1, 1)` give the hand-written `(group_id, ordinal, draw_index, remaining_turns)` rows and finished sets | all four calls equal: finished `(c0)`, `(c2)`, `(c1)`, `(c3)`; one-turn conversation reported in the same call; conversation whose last turn is too long reported in the call that drew and rejected it (draw 5); `skipped_overlength=1` | PASS |
| 5 | Two independent instances | equal sequences | equal over 2,048 draws | PASS |
| 5 | Timing | recorded | construction 0.018 s per instance; mean draw 8.38 ms (raw mixer output, no rendering), about 2.1 s per 256-turn bank | recorded |

## Notes on the observed order

- **Short runs are conversation endings.** The 7 runs shorter than 8 match the 7 conversations that finished within the 2,048 draws: the native mixer ends a block when the conversation ends.
- **Fewer than 32 open conversations for a short time.** A source whose conversation ended opens its next conversation only when the mixer picks it again, so the open count can drop to 29 between a conversation's last turn and that source's next draw.
- **10 or 12 turns of one conversation in one window.** Windows are fixed 256-draw slices. After a short block, the 32-block cycle no longer lines up with the window edges, so the tail of one block and the next full block of the same conversation can fall in the same window (for example 4 + 8). In training, the same can happen inside one 256-turn bank; spec S4 already averages a conversation's turns within an update, so the profile is unaffected.

## Limits

- The interleaved order was checked over the first 2,048 draws (8 updates' worth) of the real copies, not over a whole cell (51,200 turns).
- Epoch wrap with M > 1 was not exercised. It is unreachable in this task: 51,200 turns per cell is far below the 446,569 assistant positions in the source population. Epoch wrap at M = 1 stays covered by `boundary_checks`.
- Draw timing covers the raw mixer only; Qwen rendering cost is unchanged from the reused adapter and was not re-measured.
