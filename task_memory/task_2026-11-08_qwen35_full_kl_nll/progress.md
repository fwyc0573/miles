## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record the worktree setup and the source investigation that shapes interview round 1. |
| 2026-11-08 | Answer the round-1 loader-order concern with source evidence; correct Finding 8. |
| 2026-11-08 | Record round 2 (D12–D16), the drafted spec, plan and six tickets, the Q41 manifest check and the document checks. |
| 2026-11-08 | Record the round-3 answer and the second loader verification (Finding 12); spec S2 and tickets 01/04/05 wait for Q20. |
| 2026-11-08 | Record the round-4 answer (D18, D19); rewrite spec S2/S4/S5/S8/S9, tickets 01/03/04/05, the plan and the glossary order term. |

# Progress

## completed

- Loaded `grilling` and `domain-modeling`. Read repository `AGENTS.md`, the loaded `.claude/rules/` files, `GLOSSARY.md`, and the reused task's requirements, spec, plan, progress, checkpoint, ticket 02/04 and `evidence/training-integration-api.md`.
- Created worktree `.worktrees/agent-opd-image` on new branch `agent-opd-image` from `agent-opd` HEAD `20d0b3f4`. Added `.worktrees/` to the local `.git/info/exclude` only; no tracked file changed.

## Findings that shape the interview

1. **The reused task is not finished.** Its checkpoint records Ticket 01 (inputs) PASS; Ticket 02 (training, replay, KL/TIS sums) and Ticket 03 (HF/evaluation) are TODO; no formal cell has run (`task_2026-11-08_qwen35_swe_full_r256/checkpoint_2026-11-08_implementation.md`).
2. **Its training code is uncommitted and still being edited.** On `agent-opd`, 16 tracked files are modified and `tests/manual/agent_opd/{swe_replay,swe_training,swe_tis,run_swe_opd,submit_swe_opd,...}.py` are untracked; `swe_replay.py` was modified at 07:38 UTC, three minutes before inspection. The new worktree therefore contains only the committed Ticket 01 input adapter (`tests/manual/agent_opd/swe_inputs.py`).
3. **Reusable values already computed per training batch (uncommitted prior code).** `swe_tis.apply_tis` holds, per sample, the current-student log probabilities, teacher log probabilities and the original target mask, and reduces float64 sums (`kl_before_tis_numerator`, `original_tokens`) that `swe_training.optimizer_step` all-reduces once per update. Per-turn sums need only a per-sample reduction of the same tensors; no extra model forward.
4. **Native per-token KL already exists for every estimator.** `miles/backends/training_utils/loss/hub/opd.py:31–94` writes `rollout_data["opd_reverse_kl"]`: sampled-token `old_student - teacher`, or a precomputed tensor for top-k. The estimator is selected by existing config `opd_log_prob_top_k` (0 = sampled) and `opd_top_k_strategy` (`miles/utils/args/configs/on_policy_distillation.py:42–60`).
5. **Result path to the rollout side exists (uncommitted).** The optimizer-step hook record travels `TrainStepOutput.optimizer_step` → `train.py` `training_protocol.accept` → `RolloutExecutor.notify_train_result` → `SweReplay.on_train_result`, which runs next to the data source and bank selection.
6. **NLL precedent.** The user's Steptron replay code defines `student_nll_numerator = -sum(current student log prob)` over the response tokens (`steptron/.worktrees/step3p6-replay-v1/playground/users/ycfeng/MOPD/bounded_replay_anchors.py:598–623`).
7. **Conversation/turn identity.** The input adapter emits `metadata.source.group_id = file_sha256:source_item_index` and `assistant_turn_index` (message position) plus `assistant_turn_ordinal` (1-based assistant count) (`tests/manual/agent_opd/swe_inputs.py:125–140`). The native loader does not expose a conversation's total assistant-turn count; it consumes conversations and turns strictly in order.
8. **Short per-conversation history holds for the streaming order only (corrected after the round-1 concern).** The reused task's audit found the first 51,200 raw turns cover 546 conversations (about 94 turns each) before length filtering. Under the streaming order that the reused Ticket 01 implements, a conversation spans one or two consecutive updates of 256 turns and each turn is trained once. Under the native indexed order (Finding 10), the same 51,200 turns spread over nearly all 4,992 conversations; see Finding 10 for the estimate.
9. **Glossary conflict.** `GLOSSARY.md` uses *trajectory* for generated outputs (`Trajectory replay`) and *Training turn* for one assistant response with its context. The request uses "traj" for a dataset conversation.

10. **Steptron loader order (round-1 concern).** Source: `/data/ycfeng/steptron/.worktrees/behavior-turn-replay-step3p6/playground/users/wyx/MOPD/`.
    - Streaming (recipe default, `online_turn_streaming=True`, recipe `step3p6_mopd_turn_5experts_fullyasync_tis_no_kl_0710_h200.py:589–627`): one `OnlineTrajectoryTurnSource` per `SOURCE_SPECS` entry. Each source keeps exactly one active conversation and emits all its assistant turns in order before loading the next (`step3p6_mopd_online_turn_loader_0710.py:383–425,463–493`). `SequentialJsonArrayCursor` reads files and conversations in file order, no shuffle (`:26`). `TurnBalancedTrajectoryBlockMixer` alternates only between sources, in blocks of 8 turns, ending a block early when the conversation ends (`:636–707`).
    - `SOURCE_SPECS` (recipe `:225–262`) has five sources: working, stem, swe, tb, swift. All 11 SWE files are one source (`swe`, `:244–246`). So in the SWE-only setting the mixer sees one source and a conversation's turns are strictly consecutive. In the five-source production setting, SWE turns are interleaved with other domains, but still come from one SWE conversation at a time (the Steptron review estimates about 205 SWE turns from 2–3 consecutive conversations per 1,024-turn update, `review_report_2026-11-03_ticket06_07.md:358`).
    - Indexed (`online_turn_streaming=False`, recipe `:629–665`): native `LazySWETurnSplitDataset` (`:350–409`) builds a byte-range conversation index and a turn index; `MultiEpochSampler` draws `torch.randperm` (seed `0 + epoch`), a uniform random order over all turns.
    - The user's behavior-turn-replay decision Q41 adopted the indexed order with seed 1234 over all 446,569 GLM assistant positions of 4,992 conversations, in stable order file → conversation → assistant (`review_report_2026-11-03_ticket06_07.md:426–427`; universe counts in `evidence/swe-category-pairs-20261025b/swe-category-pairs-20261025b-verification.json`).
    - Estimate for this task under the indexed order (inference, ignoring length rejection and failed turns): 51,200 / 446,569 = 11.5% of turns. A conversation of 89.5 turns appears in about 10 updates, about 19.5 updates apart; two turns of one conversation in the same update are rare; nearly every conversation is visited. A conversation's turns arrive in random turn order, not ascending.
    - Conclusion: the user's expectation (turns spread evenly over conversations) matches the native indexed order, not the streaming default. The reused Ticket 01 adapter (`tests/manual/agent_opd/swe_inputs.py`) uses the streaming source directly.

11. **Q41 manifest facts (no longer used after D12 was withdrawn).** `fresh-smoke-20261104a.json` in the Steptron behavior-turn-replay task evidence records `status=smoke_prefix_ready`, seed 1234, 11 files, population count 446,569 over 4,992 conversations, rows `(file_index, source_item_index, assistant_position)` hashed as little-endian row-major int64: population sha256 `fdcf79d2…bd547e`, permutation sha256 `8a5f64ce…1baf1aa`. The hash algorithm is in `tests/e2e/mopd_turn_replay/freeze_glm_fresh_order.py:143–157`. Spec S2 cited both until D12 was withdrawn.

12. **Second loader verification (round-3 question: does the native indexed order keep ascending turns and take about 8 turns per conversation at a time?).** Source: `/data/ycfeng/steptron/.worktrees/behavior-turn-replay-step3p6/`.
    - Indexed path (`online_turn_streaming=False`, recipe `playground/users/wyx/MOPD/step3p6_mopd_turn_5experts_fullyasync_tis_no_kl_0710_h200.py:636–667`): `LazySWETurnSplitDataset._build_index` (`:429–450`) appends every assistant turn of every conversation to one flat `turn_index` list; `MultiEpochSampler(len(dataset))` (`third_party/datahub/src/datahub/text/samplers/multi_epoch_sampler.py:41–47`) draws `torch.randperm(size, seed=base_seed + epoch)` over that list. Turn order within a conversation is not kept and there is no 8-turn grouping.
    - Streaming path (default `online_turn_streaming=True`, `online_trajectory_block_turns=8`, recipe `:589–634`): `OnlineTrajectoryTurnSource.__next__` (`step3p6_mopd_online_turn_loader_0710.py:463–492`) emits the active conversation's assistant turns in ascending order and loads the next conversation only after the last turn. `TurnBalancedTrajectoryBlockMixer.__next__` (`:687–706`) picks a source, emits up to 8 turns from it and then picks a source again; the source keeps the same active conversation, so the next block from that source continues it. The 8-turn block therefore alternates between sources (domains), not between conversations of one source.
    - With SWE as the only source (this task), the mixer always picks the same source and a conversation's turns are fully consecutive. In the 5-domain production run, a SWE conversation is taken 8 turns at a time with other domains' blocks in between. The behavior-turn-replay task recorded the same reading (`task_2026-10-25_swe_behavior_turn_replay/progress.md:3269`).
    - A search of all 58 Steptron worktrees' `playground/users` and `tests/e2e` for sampler, mixer and turn-source classes found no loader that keeps several conversations of one source active at once.
    - Conversation lengths (999-conversation sample, `task_2026-10-23_swe_turn_replay/swe-dataset-format.md:61`): assistant turns min 19, median 81, P90 144, max 464, mean 90.69. With 8 turns per conversation per update, a conversation spans ceil(n/8) updates: min 3, median 11, P90 18, max 58.

13. **Native classes cover the interleaved order (D18).** `SequentialJsonArrayCursor.__init__` only collects file stat signatures and opens files lazily; `close` is idempotent (`step3p6_mopd_online_turn_loader_0710.py:31–46,297–301`). `OnlineTrajectoryTurnSource` loads conversations through `self.cursor.next_record()` (`:383–427`), so several sources can share one cursor by replacing the attribute after construction. `TurnBalancedTrajectoryBlockMixer` picks the source with the fewest emitted turns, ties rotating, and ends a block at `trajectory_block_turns` or at the end of the conversation (`:669–706`). With one source the mixer emits exactly the source's sequence. The committed adapter uses one native source directly (`tests/manual/agent_opd/swe_inputs.py:171–174,213`).

## Interview and document iterations

- Round 2 answer recorded as D12–D16 in `requirements.md` (indexed order, KL-only best, trainer-side per-turn sums, column-wise profile with its own JSONL, soft gate and no separate smoke).
- Drafted `spec.md` (S0–S9), `plan.md` and `tickets/01`–`06`; added glossary terms Source conversation, Indexed turn order, Distillation profile, Turn observation, KL-best update, KL trend and Recovery gap.
- Design choices made from evidence while drafting, put to the user with the freeze request:
  - 01 and the pure module part of 03 start right after the freeze, because they touch only committed code; this narrows D1.
  - "Existing metrics log" resolves to the JSONL evidence: the reused configuration enables no wandb/tensorboard.
  - The profile module lives in `tests/manual/agent_opd/` next to its only user, `SweReplay`.
- Round 3 questions Q17–Q19 recorded in `requirements.md` with recommendations.
- Round 3 answer: random order rejected (D12 withdrawn); D17 GPU budget recorded and applied to spec S0/S8; spec S2 marked as waiting for Q20.
- Round 4 answer: D18 (interleaved order, 32 × 8) and D19 (relaunch rule) recorded. Rewrote spec S2; updated S4 `alive`, the table and trend notes, S5, S8 (start-up prompt lengths, D19) and S9; rewrote ticket 01 and updated 03/04/05, the plan and the glossary term (Indexed turn order → Interleaved turn order). The ticket 01 file keeps its old name `01-indexed-turn-order.md` until the user approves a `git mv`.

## in-progress

- Waiting for the user's freeze confirmation and approval to rename the ticket 01 file.

## pending

1. After the freeze: start 01 and the 03 module; 02 waits for the reused Ticket02 and the merge (D1).
