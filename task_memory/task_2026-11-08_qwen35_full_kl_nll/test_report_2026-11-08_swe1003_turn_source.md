## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Local checks of the ticket 01 revision: selectable turn source, `loss_masked` fixture, GLM copies with `all_assistants`, synthetic SWE-1003 files with `loss_masked`. |

# Test report — ticket 01 revision for the SWE-1003 data (local part)

Scope: the ticket 01 criteria that can be checked without the 8 SWE-1003 files ([ticket 01](tickets/01-interleaved-turn-order.md), items 1–4 of "待完成"). The source audit and the checks on the files in place need a CPU RJob that mounts posttrain; they have not run (see "Not run").

## Code under test

- `tests/manual/agent_opd/swe_inputs.py`:
  - `SWEInputConfig` replaces `swe_native_loader_path` / `swe_native_loader_sha256` with `swe_steptron_root`, `swe_module_sha256` (dotted module name → SHA256) and `swe_turn_source`.
  - `TURN_SOURCES` table: `all_assistants` → base loader `OnlineTrajectoryTurnSource` with the GLM 0710 recipe normalization (`recipe_chat_messages`); `loss_masked` → turn data `MaskAwareSWETurnSource` with the `tokenize_swe_prefix` normalization (`swe_prefix_messages`), the manifest's `visual_source_item_indices` as `excluded_source_item_indices`, and three extra ground-truth fields in the source identity.
  - `load_pinned_modules` (moved here from the audit) verifies each module's SHA256 and registers it under its dotted name; the cursor and the mixer always come from the base loader.
  - Tools: `history_tools` takes the first message's `tools`, else `tool_schemas`; `reasoning_effort` is not passed.
  - Data source identity adds `turn_source`, `steptron_root`, `pinned_module_sha256` and, for `loss_masked`, `visual_exclusion_sha256`.
- `tests/manual/agent_opd/audit_swe1003_sources.py`: imports `load_pinned_modules`, the module names, the `loss_masked` normalization and `history_tools` from `swe_inputs.py`, so the audit and the adapter have one owner each.
- `tests/manual/agent_opd/check_swe_inputs.py`:
  - New flags `--steptron-root`, `--module-sha256`, `--turn-source`; `--native-recipe` is required only for `all_assistants`.
  - The population checks follow the turn source: the parity oracle is the same native class with the same exclusions; the order check counts training turns through `eligible_assistant_positions` and the exclusion list; the parity check compares the adapter's normalized history and tools with the native reference for every draw (GLM recipe converter, or `tokenize_swe_prefix` through a recording tokenizer stub).
  - New `_loss_masked_fixture_check` runs in every invocation.

## Environment

- Worktree `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`, base commit `735a3a95` plus the uncommitted changes above.
- `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`: Python 3.12.13, transformers 5.19.0. CPU only.
- Pinned Steptron modules from `/data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9` (commit `f4522d45`): base loader `0c11561f…efaa740f`, turn data `8850287f…7603980`.
- Tokenizer `/data/ycfeng/tmp/swe-model-pairs-20261103/Qwen/Qwen3.5-4B`, template `miles/utils/chat_template_utils/templates/qwen3.5_fixed.jinja`.

## Commands

`PINS` is `{"playground.baseline_new.mopd.online_turn_loader": "0c11561f33dacf1a15cd804dbd2f4feed4d1c33734bfaea7a416fdf1efaa740f", "playground.users.cj.opd.s4_swe_turn_data_1001": "8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980"}`; `T=/data/ycfeng/tmp/agent-opd-image`.

1. GLM copies, `all_assistants` (same population, sizes and draw counts as the [earlier report](test_report_2026-11-08_interleaved_turn_order.md)):

   ```bash
   timeout 1200s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.check_swe_inputs \
     --source-root /data/ycfeng/tmp/qwen35-swe-full-r256/swe-sources-20261023 \
     --source-manifest /data/ycfeng/tmp/qwen35-swe-full-r256/swe-sources-20261023/COPY_COMPLETE.json \
     --steptron-root /data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9 --module-sha256 "$PINS" \
     --turn-source all_assistants \
     --native-recipe /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/playground/users/wyx/MOPD/step3p6_mopd_turn_5experts_fullyasync_tis_no_kl_0710_h200.py \
     --tokenizer /data/ycfeng/tmp/swe-model-pairs-20261103/Qwen/Qwen3.5-4B \
     --chat-template miles/utils/chat_template_utils/templates/qwen3.5_fixed.jinja \
     --rollout-max-context-len 131072 --active-conversations 32 --block-turns 8 \
     --order-draws 2048 --parity-draws 512 \
     --temporary-root $T/t01b --output-root $T/t01b/evidence \
     --model-source-receipt task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/model-sources-exp-1108-144027-369537.json
   ```

2. Synthetic SWE-1003-shaped files, `loss_masked`. The 8 files come from `$T/make_and_check_swe1003_synthetic.py make` (written for the audit's synthetic check). The audit was re-run first on them with the refactored imports (the command in [progress](progress.md#round-89-swe-1003-0913-data), output root `$T/swe1003-synthetic-out2`), and its manifest is the input here:

   ```bash
   timeout 900s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.check_swe_inputs \
     --source-root $T/swe1003-synthetic --source-manifest $T/swe1003-synthetic-out2/swe1003-source-manifest.json \
     --steptron-root /data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9 --module-sha256 "$PINS" \
     --turn-source loss_masked \
     --tokenizer /data/ycfeng/tmp/swe-model-pairs-20261103/Qwen/Qwen3.5-4B \
     --chat-template miles/utils/chat_template_utils/templates/qwen3.5_fixed.jinja \
     --rollout-max-context-len 2000 --active-conversations 2 --block-turns 2 \
     --order-draws 12 --parity-draws 30 \
     --temporary-root $T/t01c --output-root $T/t01c/evidence
   ```

   The order check uses 12 draws at 2 × 2; the parity check's 30 draws cross one epoch boundary, so each skipped conversation is counted twice there.

## Results

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Audit on the synthetic files after the import refactor | `make_and_check_swe1003_synthetic.py check` PASS; manifest identical to the earlier run | PASS, `failures: []`; `cmp` of the two manifests: identical | PASS |
| Run 1 exit and status | exit 0, `status: PASS` | exit 0, PASS; 7 real prefixes, prompt tokens 1547, 2221, 28111, 72857, 107274, 146694, 181478 | PASS |
| Run 1 vs earlier evidence (`evidence/input-parity.json`) | `actual_prefix_checks`, `boundary_checks`, `length_rejection`, `four_cursors`, `interleaved_order`, `finished_report` equal apart from timings; `single_source_parity` only gains fields | All six sections equal; `single_source_parity` adds `history_and_tools_equal_native_normalization: true`, `draws_with_tools: 512`, `skipped_by_turn_source: {skipped_no_assistant: 0}`; 6 conversations as before | PASS |
| Run 1 order (32 × 8, 2,048 draws) | Same values as the earlier report | 38 conversations, 7 finished, longest run 8, no run longer than the block | PASS |
| Run 1 GLM tools rule | The new rule (`tools`, else `tool_schemas`) equals the earlier rule (`tools`) on all 512 parity draws | equal on 512 of 512 | PASS |
| `loss_masked` fixture: training turns | The masked assistant (message 2, with reasoning and a tool call) stays in the prefix and is not a turn; the turns are messages 4 and 6 with `t_id` 1, 2 | uids `…:2:4`, `…:2:6`; `assistant_turn_ordinal` 1, 2; `history[2]` is the assistant with `loss_mask: 0` | PASS |
| `loss_masked` fixture: identity fields | `source_assistant_turn_ordinal` [2, 3], `context_masked_assistant_count` [1, 1], `num_context_messages` [4, 6], native `target_policy` | as expected | PASS |
| `loss_masked` fixture: skipping | The visual conversation (excluded through the manifest) and the conversation without `loss_mask=1` assistants are skipped, once per epoch | each skipped once per epoch (`visual_and_no_training_turn_conversations_skipped_per_epoch: 1`) | PASS |
| `loss_masked` fixture: order, `remaining_turns`, finished report | Calls (2, 2, 1): [(c2, t1, draw 0, 1 left), (c2, t2, 1, 0)] finished c2; [(c3, t1, 2, 1), (d0, t1, 4, 0)] finished c3 and d0 (c3's last turn, draw 3, over the 2,048-character limit); [(c2, t1, 5, 1, epoch 1)] | as expected; `skipped_overlength` 1, 5 samples, 6 draws | PASS |
| `loss_masked` fixture: native normalization | History and tools equal `tokenize_swe_prefix`'s normalized messages and tools | equal; tools are the `tool_schemas` list | PASS |
| `loss_masked` fixture: Qwen rendering | Both prompts end with the thinking generation prompt and contain the masked reasoning, `<function=run_tests>`, `<tool_response>`, `<tools>`; turn 2 also contains turn 1's reasoning and answer (`preserve_thinking`) | as expected; 324 and 349 tokens | PASS |
| `loss_masked` fixture: alias | Renaming `tool_schemas` to `tools` renders the same prompt | identical | PASS |
| Run 2 parity (M = 1, 30 draws) | Items and `remaining_turns` equal one native `MaskAwareSWETurnSource` with the same exclusions; history and tools equal `tokenize_swe_prefix` | equal on all 30; 8 conversations; skips 2 and 2 (two epochs) | PASS |
| Run 2 order (2 × 2, 12 draws) | Turns ascending without gaps, conversations open in file order (skipping visual and no-training-turn conversations), at most 2 open, `remaining_turns` equal to the independent training-turn count, two instances equal | all true; 6 conversations, 5 finished; longest run 2 | PASS |
| Run 2 configuration | The real custom-function config merge builds the `loss_masked` adapter (the dict-valued `swe_module_sha256` passes `model_validate`) | PASS; `input-config.json` records `turn_source: loss_masked`, the pinned module hashes and `visual_exclusion_sha256` | PASS |

Timings (run 1, 32 × 8): construction 0.0184 s per instance, 8.44 ms per draw (earlier report: 0.0183 s, 8.38 ms); 512 parity draws with the extra normalization comparison: 16.4 s.

Evidence:
- `evidence/input-all-assistants-f4522d45/` (run 1: `input-parity.json`, `input-config.json`, `input-source-manifest.json`);
- `evidence/input-loss-masked-synthetic/` (run 2: `input-parity.json`, `input-config.json`, and the synthetic audit's `swe1003-source-manifest.json`).

The earlier `evidence/input-*.json` files stay unchanged as the record of the [earlier report](test_report_2026-11-08_interleaved_turn_order.md).

## Observations and inferences

- Observed: with the f4522d45 base loader, the GLM sequences, counts and real-prefix prompts are identical to the 0710 loader's evidence. This is consistent with the spec's statement that the three classes are byte-identical in both loaders.
- Observed: the two native normalizations differ on inputs that the checked data do not contain. The GLM recipe drops `value` when `content` exists and raises on a missing `content`; `tokenize_swe_prefix` keeps the message as is. Each turn source therefore carries its own function, and each is compared with its native reference.
- Inference: the synthetic set checks the logic of `loss_masked`, not the real data distribution. Real lengths, skip counts and the D26 numbers come only from the audit.

## Not run

- The source audit on the 8 files in place (ticket 01 item 5) and the `loss_masked` checks on them (item 6: 512 parity draws with native normalization, 2,048 draws at 32 × 8, two instances, timings). Both need a CPU RJob that mounts posttrain read-only, and the submission route is still open.
