## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record the worktree setup and the source investigation that shapes interview round 1. |
| 2026-11-08 | Answer the round-1 loader-order concern with source evidence; correct Finding 8. |
| 2026-11-08 | Record round 2 (D12–D16), the drafted spec, plan and six tickets, the Q41 manifest check and the document checks. |

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

11. **Q41 manifest facts (for ticket 01).** `fresh-smoke-20261104a.json` in the Steptron behavior-turn-replay task evidence records `status=smoke_prefix_ready`, seed 1234, 11 files, population count 446,569 over 4,992 conversations, rows `(file_index, source_item_index, assistant_position)` hashed as little-endian row-major int64: population sha256 `fdcf79d2…bd547e`, permutation sha256 `8a5f64ce…1baf1aa`. The hash algorithm is in `tests/e2e/mopd_turn_replay/freeze_glm_fresh_order.py:143–157`. Spec S2 item 6 now cites both.

## Interview and document iterations

- Round 2 answer recorded as D12–D16 in `requirements.md` (indexed order, KL-only best, trainer-side per-turn sums, column-wise profile with its own JSONL, soft gate and no separate smoke).
- Drafted `spec.md` (S0–S9), `plan.md` and `tickets/01`–`06`; added glossary terms Source conversation, Indexed turn order, Distillation profile, Turn observation, KL-best update, KL trend and Recovery gap.
- Design choices made from evidence while drafting, put to the user with the freeze request:
  - 01 and the pure module part of 03 start right after the freeze, because they touch only committed code; this narrows D1.
  - "Existing metrics log" resolves to the JSONL evidence: the reused configuration enables no wandb/tensorboard.
  - The profile module lives in `tests/manual/agent_opd/` next to its only user, `SweReplay`.
- Round 3 questions Q17–Q19 recorded in `requirements.md` with recommendations.

## in-progress

- Waiting for the user's answers to Q17–Q19 and the freeze confirmation.

## pending

1. Apply the Q17–Q19 answers to `spec.md` S4/S8 and rerun the document checks.
2. After the freeze: start 01 and the 03 module; 02 waits for the reused Ticket02 and the merge (D1).
