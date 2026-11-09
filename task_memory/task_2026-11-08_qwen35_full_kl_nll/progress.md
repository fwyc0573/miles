## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record A/full actual submission and first worker evidence; native first-update inspection remains pending. |
| 2026-11-10 | Record final accepted CPU integration15186817, explicit profile configurationec002ea8 and lifecycle verification before launch; move to A admission and append the exact four-section milestone checkpoint. |
| 2026-11-10 | Record02 trainer CPU-ready6129aefe,clean completed phase reviews,committed formal correction and staged03 delivery;preserve pending primary integration/GPU/S7 acceptance and append the four-section milestone checkpoint. |
| 2026-11-10 | Record actual merge55fba827, resolved prep references and scoped verification; move implementation to02 and append the four-section post-merge checkpoint without rewriting earlier snapshots. |
| 2026-11-10 | Record D35 parent-only capacity adoption and pending candidate consolidation; move the frontier to merge→02 CPU→03 integration, preserve historical observations and add a scoped checkpoint. |
| 2026-11-09 | Accept the completed D34 original-source112K audit/parity; record successful H800 initial synchronization separately from still-unaccepted upstream capacity and parent integration. |
| 2026-11-09 | Supersede first H800 startup with terminal failure, reviewed node-local NCCL correction and new network-fixed H800 job Starting; preserve separate upstream D11 gate. |
| 2026-11-09 | Record submitted H800 prerequisite exp-1109-181120-274261 and initial Starting/worker evidence; D1/D22 stay unaccepted. |
| 2026-11-09 | Record the reviewed hybrid-session repair, exact pinned receiver contract and in-place native source preparation for the isolated H800 prerequisite. |
| 2026-11-09 | Record upstream initial-weight-sync failure, terminal API evidence and the active scoped diagnosis; D1/D22 remain blocked. |
| 2026-11-09 | Begin D34 budget implementation and a fresh112K prompt audit; retain prior source evidence and historical128K outputs. |
| 2026-11-09 | Start H800 execution preparation underD33 and record live resource/upstream status. |
| 2026-11-09 | Accept the completed in-place CPU audit/parity and refresh upstream gate at05:10Z; Ticket01 done,02/03 integration still blocked. |
| 2026-11-09 | Resume with the user-selected branch-base review, in-place audit preparation, and read-only upstream prerequisite verification. |
| 2026-11-08 | Record the worktree setup and the source investigation that shapes interview round 1. |
| 2026-11-08 | Answer the round-1 loader-order concern with source evidence; correct Finding 8. |
| 2026-11-08 | Record round 2 (D12–D16), the drafted spec, plan and six tickets, the Q41 manifest check and the document checks. |
| 2026-11-08 | Record the round-3 answer and the second loader verification (Finding 12); spec S2 and tickets 01/04/05 wait for Q20. |
| 2026-11-08 | Record the round-4 answer (D18, D19); rewrite spec S2/S4/S5/S8/S9, tickets 01/03/04/05, the plan and the glossary order term. |
| 2026-11-08 | Record the freeze and the ticket 01 rename; start 01 and the 03 module. |
| 2026-11-08 | Record D20 (profiled KL is RKL) and ticket 01 done. |
| 2026-11-08 | Record the D21 renaming to RKL and correct the `opd.py` line citation. |
| 2026-11-08 | Record the ticket 03 module part done. |
| 2026-11-08 | Record the reused Ticket02 state found after the module commit. |
| 2026-11-08 | Record D22: wait for the reused branch's out-of-memory fix before merging. |
| 2026-11-08 | Record Finding 14: the SWE-1003 0913 data, its mask-aware streaming loader and the order comparison. |
| 2026-11-08 | Record the round-8 answers (D23–D25); replace the copy step with reading the files in place. |
| 2026-11-08 | Record the audit script, the stopped audit hand-off, the round-9 answer (D26, D27) and the document update; reopen 01. |
| 2026-11-08 | Record the ticket 01 SWE-1003 revision: selectable turn source, local checks PASS (items 1–4). |
| 2026-11-08 | Record the round-10 request and the questions put; the audit job is not resubmitted. |
| 2026-11-08 | Record the round-10 answer (D28–D31) and the document update; reopen the 03 module; defer 01 items 5–6. |
| 2026-11-08 | Record D32 with the measured baseline noise: default B = 10, N = 8. |

# Progress

## completed

- Final CPU-readiness document verification under system Python3.10.6:31 documents/6 tickets/121 links/40 anchors,01→02→03→04→05→06 DAG,unchanged51,200/cell/102,400 total/81-turn estimate,zero errors. Nine-owned-document scoped whitespace PASS. A one-off read-only assertion checks the exact four checkpoint sections,all D1–D7/S1–S6 rows,11/11 checked03 CPU criteria,02 downstream S7 checked/GPU unchecked,all8 A and9 B formal criteria unchecked,and the pre-launch lifecycle evidence link; PASS. Six unique backticked prep paths resolve; Markdown references are separately checked by the retained docchecker. The first docchecker run had two dependency-text mismatches because `and02`/`for04` and a Chinese-adjacent04 lacked the existing `\b0\d\b` boundary; restoring explicit numbered references/spacing passed without changing checker code or dependency semantics. No business/lifecycle/GPU check was rerun, and no code/config/proof report or new task file was written.

```bash
python3 -B tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll
git diff --check -- task_memory/task_2026-11-08_qwen35_full_kl_nll/requirements.md task_memory/task_2026-11-08_qwen35_full_kl_nll/spec.md task_memory/task_2026-11-08_qwen35_full_kl_nll/plan.md task_memory/task_2026-11-08_qwen35_full_kl_nll/progress.md task_memory/task_2026-11-08_qwen35_full_kl_nll/summary.md task_memory/task_2026-11-08_qwen35_full_kl_nll/tickets/02-per-turn-sums.md task_memory/task_2026-11-08_qwen35_full_kl_nll/tickets/03-distillation-profile.md task_memory/task_2026-11-08_qwen35_full_kl_nll/tickets/04-a-full.md task_memory/task_2026-11-08_qwen35_full_kl_nll/tickets/05-b-full.md
```

- Final CPU readiness accepted before formal A launch:02 trainer `6129aefe` and03 integration `15186817` are primary accepted. [Integration evidence](test_report_2026-11-10_profile_integration.md) records201 PASS in67.48s through the real `SweReplay.on_train_result` path, including successful/skipped ACKs, canonical bank/source/finished identity, native counters and permanent S7 suppression. All03 module/CPU integration criteria and02 downstream S7 CPU criteria are checked;02 GPU acceptance is still unchecked and reserved for04's first actual formal successful update.
- Explicit formal profile configuration `ec002ea8` is committed. The final A/B submission and native-argv dry-runs repeated4/4 PASS: each of13 valued flags once, profile-enabled once, no HF save/evaluation; full still visits200 distinct banks once each with configured `bank_uses=50`. Exact commands and preparation/native limits remain in [the existing formal configuration report](test_report_2026-11-10_formal_configuration.md). Neither dry-runs nor readiness records are launch receipts.
- **Before-launch lifecycle inspection recorded now, before formal admission/launch:** primary loaded `before-steptron-run` and inspected existing `qwen_alignment`/`swe_replay` sample, retry, teacher, cancellation and evidence-sink boundaries rather than adding instrumentation. Its16 targeted CPU cases PASS in2.63s with18 existing warnings: cancellation/draining, repeated503 sharing one deadline, failure followed by success, late/invalid slots, teacher success/error/cancelled receipts and soft sink failures. Python3.12.13; real asyncio deadlines/scheduling execute while network/GPU calls are mocked. The exact command and inspected boundary details are in [Pre-formal sample lifecycle check](test_report_2026-11-10_formal_configuration.md#pre-formal-sample-lifecycle-check). Formal per-sample failure counts and post-run RCA still require actual job evidence. No lifecycle test or platform action was rerun by this documentation slice.
- T03 review was Spec-pending at delegation. The inspected primary-owned [review record](review.md#ticket03-phase-review--2026-11-10) now explicitly records Standards/Spec No findings; this is observed completion, not anticipation. The review remains primary-owned and is not edited here; CPU review does not certify formal GPU/profile output.
- Current-state synchronization is limited to requirements phase, spec S0 status, plan/progress/summary and tickets02–05.03 is done for its CPU criteria;04 is ready for fresh formal admission but not launched;05 still waits for A's first actual successful ACK, completed inspection and fresh resources, not A200 or auxiliary profile PASS. Historical checkpoints/reports remain dated evidence; no further historical cleanup or new task file is added.

### Historical trainer CPU milestone — before03 acceptance15186817

- Scoped milestone-document verification (systemPython3.10.6):30 documents/6 tickets/107 links/35 anchors,valid01→02→03→04→05→06 DAG,unchanged51,200/cell/102,400 total/81-turn estimate,zero errors. Scoped whitespace PASS. One-off local text assertions PASS:trainer consistency checked,downstream S7/GPU unchecked,and the appended exact four-section checkpoint covers allD1–D7/S1–S6. No CPU/Gloo/formal test was rerun and no code/config/proof report was edited. The30-file checker scope includes the primary's staged03 report,which is excluded from this seven-document commit.

```bash
python3 -B tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll
git diff --check -- task_memory/task_2026-11-08_qwen35_full_kl_nll/plan.md task_memory/task_2026-11-08_qwen35_full_kl_nll/progress.md task_memory/task_2026-11-08_qwen35_full_kl_nll/summary.md task_memory/task_2026-11-08_qwen35_full_kl_nll/tickets/02-per-turn-sums.md task_memory/task_2026-11-08_qwen35_full_kl_nll/tickets/03-distillation-profile.md task_memory/task_2026-11-08_qwen35_full_kl_nll/tickets/04-a-full.md task_memory/task_2026-11-08_qwen35_full_kl_nll/tickets/05-b-full.md
```

-02 trainer CPU implementation-ready accepted by the primary at`6129aefe`(eight owned files). [Per-turn sums report](test_report_2026-11-10_per_turn_sums.md)records110 combined PASS,79 affected PASS after final nullable-metadata preservation,and8-process Gloo2CP×2TP×2PP checks with genuine AdamW updates during auxiliary failures. Existing original-mask/native-RKL tensors yield compact rows in the native ACK;trainer consistency and transport are accepted. Downstream bank joining/permanent S7 suppression and A-firstformal-update GPU acceptance are not done.
- Formal preparation`4863e68e`and correction`059a6a75`are committed. The primary validated`bank_uses=50`through real`training_protocol`RED1/GREEN50 for both A/B and`ReplaySchedule(full)`200 distinct banks/one visit each. This does not introduce replay into full. Proof,commands and four-H800 B TP4/EP1 feasibility limits remain owned by[the formal configuration report](test_report_2026-11-10_formal_configuration.md);no configuration or proof report is edited by this delegation.
- T02 Standards/Spec phase reviews completed and archived in`ba3cb696`:0/0 actionable findings on immutable`4863e68e...6129aefe`,with reviewers not independently rerunning tests. [Review record](review.md)retains CPU/native limits;review completion is not GPU or03 acceptance.
- Prior current-state S5 for spec S0's merge-pending wording is resolved in the inspected repository:spec now records`55fba827`merged. The prior merge checkpoint remains explicitly historical;current`requirements.md`phase still names02 as the frontier and is assigned to the primary for status-only synchronization,not a renewed dependency.
- D35 consolidation accepted: actual merge`55fba827`, first parent`eee754bc`,second parent archived H800 candidate`0e6e8b1e`. The two input conflict files exactly retain first-parent bytes;`run_swe_opd`now transports the explicit parent source schema. The owned input report records139 affected CPU tests and seven genuine native synthetic checks PASS, with local SGLang/lint baselines preserved. These checks do not implement02 per-turn/profile integration.
- Post-merge local checks: all seven unique`../task_2026-11-09_profile_h800_preparation/`references resolve; existing retained-capacity checker PASS; scoped merge code/parent-task`git diff --check`PASS. The whole merge still reports whitespace in17 inherited upstream XML/diff artifact paths; each committed blob is byte-identical to incoming`0e6e8b1e`, independently verified locally. Exact commands, primary acceptance, local diagnostic-parser correction and limits are appended to`test_report_2026-11-10_input_merge.md`; no historical artifact was rewritten and no new runtime was launched.
- Post-merge documentation PASS underPython3.10.6:27 documents/6 tickets/87 links/33 anchors,valid DAG,unchanged51,200/102,400/81 arithmetic,zero errors;owned-document scoped whitespace PASS. The initial ticket03 Chinese/identifier boundary was corrected without changing its02 CPU-ready dependency or the existing checker. The exact command and first/final results are in`test_report_2026-11-10_input_merge.md`;independently edited code and the primary integration-merge report are excluded from this commit.

### Historical D35 adoption and checks — before merge55fba827

- D35 decision recorded on2026-11-10: exact question/selection are in`requirements.md`. The user accepts the verified36-H800 D34 result as this parent's D1/D22 capacity basis and authorizes candidate consolidation followed by02/03 integration; upstream frozen-D11 acceptance stays independently owned. The terminal result and retained paths are in[the H800 adoption record](test_report_2026-11-09_h800_preparation.md#d35-parent-adoption-2026-11-10). No merge, parent per-turn implementation, profile integration or formal A/B result is claimed.
- ScopedD35 documentation verification: systemPython3.10.6;`git merge-base --is-ancestor c52991ac agent-opd-h800-capacity`exit0; existing`python3 -B tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll`reports26 documents/6 tickets/88 links/34 anchors,valid DAG and unchanged51,200/102,400/81 arithmetic,zero errors;`git diff --check`PASS. Exact checks, pending post-merge path resolution and preserved prior-document scope are in`test_report_2026-11-10_d35_records.md`. The primary's concurrent merge-preflight report and`.cortexkit/`are excluded from this delegation's commit.

### Earlier completed milestones — evidence retained as recorded

- D34 original-source CPU re-audit accepted for task`profile-source-audit-112k-records-20261109`: the primary's direct personal `get_rjob_client()` / API read at11:52:22.402210Z confirms`exp-1109-154414-275606`, UID`6e08e161-435d-4195-bcd4-88d40d291eac`, creator`i-fengyicheng`, job/audit replica Succeeded, finish11:47:11Z. The first terminal import of nonexistent `get_client` failed locally before any request; reading `stepmind.py:744` corrected the method, with no audit failure/relaunch. Terminal receipt:`evidence/source-audit-112k-terminal-20261109.json`.
- Ticket01's D34 slice is done: all8 original file SHA/bytes/counts/visual indices match historical128K evidence;16,559,540,463 bytes,9,254 source/9,152 trainable conversations,868,775 pre-length eligible turns,102 visual conversations/10,008 eligible turns excluded. Current112K rejects323,121 turns (37.1927%) across6,257 conversations.512 native parity and2,048 interleaved raw draws PASS; inclusive112K/+1skip/zero consumed-slot and real4,366-token→16,384-token native request construction PASS. Current32×8 simulation:51,200 accepted/84,229 draws/33,029 rejected,869 conversations,span median5/P90 7/max9;0/869 span≥11 updates,median23 conversations/update (not tasks). D26's pre-length eligible median90 retains32×8; post-length median remains absent/unverified. Native SWE identity stays UNVERIFIED/null;955 first-prompt groups are proxies. Full commands/environment/limits are owned by`test_report_2026-11-09_length_budgets.md`; old128K report/receipts remain explicitly historical. This is input acceptance only, not native trend/capacity or02/03 integration.
- Scoped local record checks: systemPython3.10.6, JSON syntax/identity/count/budget/parity/terminal reconciliation PASS for five business JSONs plus the terminal receipt, credential-pattern matches0, no original-source file opened. First local assertion misread `local_verified_files` as integer8; field-type inspection showed a list, and `len(...)==8` passed. Existing document checker and its temporary original were inspected and `cmp` passed. This was a local readback correction, not an audit/runtime defect. No code/platform operations or new test machinery.
- Final scoped document verification: `python3 -B tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll` reports24 documents/6 tickets/82 links/28 anchors,valid DAG and51,200-per-cell/102,400-total/81 arithmetic,zero errors; `git diff --check` PASS. `cmp tests/manual/agent_opd/check_profile_docs.py /data/ycfeng/tmp/agent-opd-image/check_docs.py` PASS; explicit recursive credential-key/value scan on six selected JSONs PASS withzero matches and no credential output. Commit scope is the seven owned documents plus five new business JSONs and their terminal receipt; primary-owned H800 report edits and `.cortexkit/` are untouched.
- Isolated prerequisite repairs:`7689fbec` fixes mixed-engine lifecycle coverage; reviewer`profile-hybrid-session-review-20261109` found no defects. Follow-up`422a613d` matches upstream`864cac87` and passes37 directly affected checks. Exact pinned-image CPU probe`exp-1109-161858-331786` succeeded and confirms the receiver rejects absent-session distributed writes before receive; receipts are`evidence/native-weight-session-source{,-job}-20261109.json`. Original HTTP body and stalled program counter are still unavailable; native rerun remains required.
- The H800 preparation's old sequential source now supports D34 (`82915613`,39 affected PASS), and its parity checker consumes those budgets (`8d517b48`,19 checks PASS). Fresh genuine native exclusion receipts from original posttrain paths completed in`exp-1109-164358-350923`, excluding102 conversations/10008 targets from9254 originals. This is independent prerequisite input preparation, not parent Ticket02/03 integration or the full112K distribution audit.
- D33/D34 fixed-diff phase review completed by`profile-h800-length-review-20261109` (`ses_e40bbe487ffeqJc4LSyAlspkFg`): parent`2d695ba0..438d25fc` andpreparation`c52991ac..46e7b292`, no new actionable findings. Scope andnative/integration limitations are in`review.md`; this does not mark a GPU run accepted.
- D34 input/audit implementation committed as`438d25fc`: existing native prompt limit now114688 inclusive; response cap16384 and total131072 reach the actual request builder. Primary affected suite33 PASS; pinned GLM512/2048 and synthetic SWE30/12 checks PASS; audit threshold/bisection and synthetic16/16 workflow PASS. Durable receipts and exact commands:`test_report_2026-11-09_length_budgets.md`. Old128K source artifacts remain intact.
- Isolated H800 preparation commits:`1ae93261` makes the existing admission ceiling explicitly nullable (25 budget+4 consumer checks PASS); `8c9537bf` wires explicit prompt/response fields (53 launcher+7 related checks PASS); `46e7b292` enables the four-node lifecycle (122 affected PASS; broader related171PASS/12SKIP/one baseline parser failure). These commits are not merged into the parent branch beforeD1/D22.
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

14. **SWE-1003 0913 data and its loader (round-8 request).** Sources: Steptron commit `f4522d451a9db59e5f1fee3990aedd73bc549002`, files under `playground/users/cj/opd/` and `playground/baseline_new/mopd/online_turn_loader.py`, extracted to `/data/ycfeng/tmp/agent-opd-image/s4_*.py`; the lookup task's `findings.md` ("October delivery streaming versus indexed recipe").
    - **The recipe is streaming with one source.** Chain 1003 → 1002 → 1001 → `LossMaskedSWEDataConfig`. `build_dataloader` raises unless `online_turn_streaming` is true (`s4_swe_turn_data_1001.py:514–517`); the pinned base config sets it true and `online_trajectory_block_turns = 8` (`turn_5teachers_data.py` DataConfig). `SOURCE_SPECS` has one entry holding all 8 files (`s4_swe_opd_sft105_teacher400_1001.py:50–59`), so the mixer always picks that source and a conversation's turns are drawn strictly consecutively. 1001–1003 change only resources; `infer_samples = 1024` per update (`1001.py:198`).
    - **Same native classes.** The pinned base loader (sha256 `0c11561f…efaa740f`) equals the 0710 loader this task pins (sha256 `ffd9bb31…ecacc8`) plus one added function, `iter_json_array_item_spans`; the cursor, turn source and mixer are byte-identical.
    - **Mask-aware turn source.** `MaskAwareSWETurnSource(OnlineTrajectoryTurnSource)` (`s4_swe_turn_data_1001.py:309–481`) overrides `_load_next_trajectory`, which still reads `self.cursor.next_record()`, so cursor sharing (Finding 13) still works. Only assistants with integer `loss_mask = 1` are training turns (`eligible_assistant_positions`, `:106–129`); masked assistants, their reasoning and tool calls, and tool replies stay in the prefix. `active_remaining_turns` then counts eligible turns only, and the native `assistant_turn_ordinal` becomes the 1-based ordinal among eligible turns (base `__next__`: `offset + 1`); `_make_ground_truth` adds `source_assistant_turn_ordinal` (ordinal among all assistants), `context_masked_assistant_count` and `target_policy` (`:397–409`).
    - **Visual exclusion.** Whole source conversations with image or video payloads are skipped through `excluded_source_item_indices` (`:316–358`), read from a receipt at `/mnt/posttrain-release/cj/opd/s4_swe_1001/data/swe_visual_filter_1001.json` that checks absolute path, size and mtime of each file (`:180–306`). It lies outside the permitted cloud root and would not match personal copies; the predicate itself is in `s4_swe_visual_audit_1001.py` (`VISUAL_FIELDS`, `VISION_MARKERS` including Qwen `<|vision_start|>`, data URIs).
    - **Schema** (from the audit script `s4_swe_data_audit_1001.py:130–165`): `content` string, optional string `reasoning_content`, `tool_calls` with `id` and string `function.arguments`, `tool` messages with `tool_call_id`, per-message `loss_mask`. Tool schemas are read from the first message's `tools` or `tool_schemas`, plus optional `reasoning_effort` and `preserve_thinking` (`s4_swe_turn_data_1001.py:72–82`). The adapter reads only `tools` (`swe_inputs.py:243`).
    - **Unknown until the files are read:** per-file conversation and eligible-turn counts, eligible turns per conversation, the share of masked assistants, the number of visual conversations, prompt lengths under the Qwen template, and whether trajectories of the same SWE instance sit next to each other in file order (the manifest says to keep "existing row multiplicity", `s4_swe_source_manifest_1001.py:10–15`). The data are not mounted locally (`/mnt/posttrain/...` and `/mnt/codesign-exp` both absent); no personal copy exists. Local disk has 244 GB free; the GLM local copy is 3.2 GB.
    - **Order comparison for this task (inference from the code above):**
      - Streaming (M = 1, which is what the SWE-1003 recipe does here): a conversation with n ≤ 256 eligible turns sits in one or two adjacent updates; trend at k = 10 needs a span of at least 11 updates, so it is undefined for nearly every conversation.
      - Indexed: not available for this data. The SWE-1003 config rejects it, and the native `LazySWETurnSplitDataset` indexes every assistant without the loss mask or the visual exclusion, so it would need new code. It also breaks ascending turn order, which the user rejected in round 3 (D12 withdrawn).
      - Interleaved (D18): carries over by building `MaskAwareSWETurnSource` objects instead of `OnlineTrajectoryTurnSource`. A conversation spans about ceil(n / block) updates; M = 1 still reproduces the SWE-1003 streaming sequence exactly, which keeps ticket 01's parity check meaningful.

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

- Round 5 answer: documentation frozen; `git mv` of ticket 01 to `01-interleaved-turn-order.md` approved and applied; links in the plan, spec S9 and the checker updated; checker rerun: 21 links, 5 anchors, 0 errors.
- User correction during implementation: the measured KL is RKL, KL(student‖teacher). Recorded as D20 in `requirements.md`, spec S3 and `GLOSSARY.md` (commit `beb996a4`). Native `opd_reverse_kl = old_student_log_prob - teacher_log_probs` on student-sampled tokens (`miles/backends/training_utils/loss/hub/opd.py:88–89`) is already the sampled-token RKL estimate, so no computation changes. Checker rerun: 22 links, 6 anchors, 0 errors.

- Round 6 answer: renaming approved as D21. Applied with a script that requires each exact text to match once (`/data/ycfeng/tmp/agent-opd-image/rename_rkl.py`): spec (title, S1–S6, S9), `GLOSSARY.md` (Turn observation, RKL-best update, RKL trend, Recovery gap; old terms moved to _Avoid_), plan row 02, tickets 02 and 06. The `opd.py` citation in spec S3 and D20 was `:90`; in this worktree the lines are `:88–89`, corrected. Checker rerun: 13 files, 29 links, 7 anchors, 0 errors.

## Ticket 01 (done)

- Reason: spec S2 (D18) needs 32 open conversations taken 8 turns at a time; ticket 03 needs each turn's remaining count and the conversations finished in each bank.
- Method: `NativeSWEDataSource` now builds `swe_active_conversations` native `OnlineTrajectoryTurnSource` objects that share the first one's cursor, mixed by the native `TurnBalancedTrajectoryBlockMixer` with `swe_block_turns`. `draw()` finds the emitting source by comparing `mixer.emitted_turns` before and after the draw and returns its `active_remaining_turns`. Each sample's `metadata.source` gains `draw_index` and `remaining_turns`; `finished_conversations` holds the group_ids whose last turn the latest `get_samples` call drew, including a last turn rejected for length. `check_swe_inputs.py` gains the M = 1 parity, the 32 × 8 order check and the synthetic finished-report check.
- Expectation and result: all criteria PASS on the real pinned copies in 69 s; the four existing sections equal the reused evidence; longest run 8; mean draw 8.38 ms. Details in [test_report_2026-11-08_interleaved_turn_order.md](test_report_2026-11-08_interleaved_turn_order.md).

## Ticket 03, module part (done)

- Reason: spec S4–S7 define the profile; the module and its CPU test touch no uncommitted reused code, so they run before 02 (plan, parallel work).
- Method: `tests/manual/agent_opd/distillation_profile.py`. `record_update(update_id, sums, bank_turns, finished_group_ids)` joins the record's per-turn sums to the bank's `(group_id, t_id)` by `uid`, requires a one-to-one match and contiguous successful-update ids, assigns `c_id` in first-trained order, then appends columns, conversation entries (equal-weight means, D6) and the update row, and writes one line to each JSONL file. Any error marks the profile unverified from that update and stops later updates; the caller continues (S7). Conversations reported finished but never trained are ignored. `rebuild` replays `observations.jsonl` and requires every replayed summary to equal its `updates.jsonl` line.
- Tests: `tests/fast/test_distillation_profile.py` (6 cases, hand-computed values); three injected bugs each fail a test; `tests/manual/agent_opd/time_distillation_profile.py` times a synthetic 200 × 256 interleaved run.
- Result: all module criteria PASS; under 4 ms per update, under 0.4 ms per all-conversation query, about 13 MB. Details in [test_report_2026-11-08_distillation_profile_module.md](test_report_2026-11-08_distillation_profile_module.md).
- Finding: spec S5's 2 MB counted the numeric columns only; the `uid` strings and lookups bring the total to about 13 MB. S5 now states the measured total.

## Reused Ticket02 state (read only, 2026-11-08 after `c7dfbf5a`)

- `agent-opd` moved from `20d0b3f4` to `2df38065` (5 commits). `176ffd05` commits the reused training code (`swe_replay.py`, `swe_training.py`, `swe_tis.py`, `run_swe_opd.py`, `submit_swe_opd.py`) and `0869183b` records four short native smokes.
- The committed reused ticket 02 accepts the four short native paths and the exact A/r256 tensor reconstruction; it stays in-progress with the gradient check and the 256-turn capacity check open.
- Staged but uncommitted in the main checkout (another session): `test_report_2026-11-08_capacity_oom.md`. Both 256-turn capacity smokes (A/r256 `exp-1108-174749-557599`, B/full `exp-1108-174748-739227`) collected 256/256 trajectories, then failed with `torch.OutOfMemoryError` in Megatron `tensor_parallel/layers.py:514` during the current-student rescoring (`_compute_log_prob`) before any successful update. The fix is being diagnosed there.
- Inference: the same failure blocks this task's 04 and 05, which use the same models and 256-turn banks.
- Merge check: the two branches change disjoint files since `20d0b3f4` (`agent-opd` does not touch `GLOSSARY.md`, `swe_inputs.py` or `check_swe_inputs.py`), so a merge has no textual conflict. `run_swe_opd.py` loads `NativeSWEDataSource` by path; ticket 01 keeps its interface and M = 1 behavior.
- D1 is not met (the reused ticket's own capacity smoke fails). Put to the user; answered as D22: wait for that branch's complete out-of-memory fix before merging, and start no part of ticket 02 early.
- Checked again at 20:30 (read only): `agent-opd` is at `cee3bfa5`, which adds a Megatron scoring output-lifetime patch, a saved-bank replay seam for re-running the failing bank, and their CPU tests (53 pass). Its own report states that the real 256-turn run on the saved bank has not happened and that the CPU result "不证明原 OOM 已修复". So D22's condition is still open; this task stays stopped.

## Round 8–9: SWE-1003 0913 data

- Audit script `tests/manual/agent_opd/audit_swe1003_sources.py` (commit `721090cc`). Reason: the counts that decide D26 and the visual exclusion list (D27) are only known after reading the 8 files. Method: one pass with the pinned cursor; training turns by `eligible_assistant_positions`; visual conversations by `_scan_message` on every message; the prefix before each trainable conversation's last training turn rendered with the Qwen template, with bisection for the first over-length turn; then the native mixer over `MaskAwareSWETurnSource` for 32 × 8 and 1 × 8 until 200 × 256 accepted turns. It writes an audit JSON and a source manifest readable by `load_source_population`. `load_native_module` gained an optional module name so pinned modules register under their Steptron dotted names.
- Synthetic check: `/data/ycfeng/tmp/agent-opd-image/make_and_check_swe1003_synthetic.py` writes 8 files shaped like the recipe list and compares the audit output with hand-computed values (10 conversations, 21 assistants, 18 training turns, 1 visual, 1 over-length turn; M = 1: 7 draws, 6 accepted, 1 rejected). PASS.
- The audit job hand-off to the executor was stopped before it ran: no run directory, no launcher, no output directory exist (checked). No job was submitted. Reported to the user.
- Round 9 answer: D26 (keep 32 × 8; come back if the median training-turn count is clearly below 81) and D27 (compute the visual list). Documents updated with D23–D27 (spec S0–S2, S4, S5, S8, S9; tickets 01, 03, 04, 05; plan; `GLOSSARY.md` Training turn); numbers that need the audit are marked pending.
- Ticket 01 revision, items 1–4 (local). Reason: the SWE-1003 recipe trains only `loss_mask=1` assistants and excludes visual conversations (D23, D24, D27), which the GLM-era adapter could not express.
  - Method: `swe_inputs.py` now loads the pinned f4522d45 modules by dotted name after a SHA256 check (`load_pinned_modules`, moved from the audit) and picks the turn source from the `TURN_SOURCES` table (`all_assistants` → `OnlineTrajectoryTurnSource` with the GLM recipe normalization; `loss_masked` → `MaskAwareSWETurnSource` with the `tokenize_swe_prefix` normalization and the manifest's visual list). Tools: first message `tools`, else `tool_schemas`. The audit imports these owners instead of keeping copies. `check_swe_inputs.py` follows the turn source and gains a `loss_masked` fixture check.
  - Finding: the two native normalizations differ (the GLM recipe drops `value` and requires `content`; `tokenize_swe_prefix` maps `value` to `content` only when `content` is missing), so each turn source carries its own; the parity check now compares normalized history and tools with the native reference on every draw.
  - Result: PASS on the GLM copies with `all_assistants` (all order, prefix, boundary, length and cursor sections equal to the earlier evidence) and on the synthetic SWE-1003 set with `loss_masked`; the synthetic audit output is unchanged after the import refactor. Commands, values and limits: [test report](test_report_2026-11-08_swe1003_turn_source.md); evidence in `evidence/input-all-assistants-f4522d45/` and `evidence/input-loss-masked-synthetic/`.

## Round 10: remaining gap

- Request and Q28–Q31: [requirements Round 10](requirements.md#round-10--follow-up-request-2026-11-08). Spec, tickets and the ticket 03 module change wait for the answers.
- The audit job resubmission was permitted by the user but not performed: the safety classifier's stop on the earlier hand-off forbids producing that content again. The user was asked to submit; the lead verifies the outputs.
- Answer: [requirements Round 10 answer](requirements.md#round-10--follow-up-answer-2026-11-08), recorded as D28–D31; Q32 (the two baseline lengths) is open.
  - Reason: give the profile a scale-free view of how much RKL is left, per run and per conversation, and a trend whose sign reads directly.
  - Method: spec S4 replaces the trend and recovery-gap blocks with a baseline block, the restated trend (D29) and recovery gap (D30), and interpretation limits; S5 stores the baseline sums; S6 adds the `updates.jsonl` fields; S9 adds the CPU cases and report items. Ticket 03 gets one new module criterion, ticket 06 its report items, the glossary two terms and two restated terms. The S4 anchor was renamed and its two links updated.
  - Expectation for the run: from the earlier three-pairs runs, RKL barely moved over 200 updates, so the remaining gap may stay near 1 and the trend near 0 (inference, not a measurement).
- Q32 answered as D32 (B = 10, N = 8, both config values). Measured with `/data/ycfeng/tmp/agent-opd-image/r251.py` on `task_2026-11-06_qwen35_three_pairs/evidence/{A,B}-training-steps.json`: per-update RKL coefficient of variation over the first 20 updates 0.177 (A) and 0.234 (B); standard error of a 5-update baseline 7.4% / 10.1%, of a 10-update baseline 4.9% / 6.7%; A's updates 1–5 mean 0.09159 against updates 6–10 mean 0.10037 (−8.8%); mean of the last 10 updates over the first 10 is 0.96 (A) and 1.07 (B), so no consistent drift. The N choice rests on one block making the baseline the conversation's first entry; the per-turn spread is not in that evidence.
- The user asked to hand the audit RJob to dsv4 and, if that failed, to skip it and land the documents first. The hand-off is the content stopped by the safety classifier, so it was not written; ticket 01 items 5–6 are deferred.

## Ticket 03, module part for D28–D32 (done)

- Change: `tests/manual/agent_opd/distillation_profile.py` takes `baseline_updates` and `baseline_turns`, keeps the run baseline and a per-conversation baseline running sum, and exposes `baseline`, `remaining_gap(update_id)`, the restated `rkl_trend` and `recovery_gap`, and per conversation `remaining_gap`, `run_relative_gap`, `recovery_gap` plus the batch `conversation_states`. `updates.jsonl` gained the two lengths, the run baseline, the macro remaining gap and the two baseline counts. The timing script takes the two lengths.
- Reason: D28–D32. Expectation: values in baseline units, undefined where a baseline is missing or not positive, at the same per-update cost. Result: 9 fast tests PASS, 8 injected bugs all caught, two synthetic 200 × 256 runs PASS ([test report](test_report_2026-11-08_profile_remaining_gap.md)).
- `summary()` no longer calls `conversation_states`: with that call, per-update time rose from 1.65 to 2.39 ms (lengths 19–464) and 1.82 to 3.64 ms (19–162); counting baselines and trends directly brought it back to 1.73 and 1.96 ms. The batch query itself is about 10 times its earlier cost, 0.8–2.0 ms, and is not on the per-update path.
- The first mutation run left one bug alive (a conversation baseline that takes every turn of an update instead of only the turns it still needs); `test_baseline_stops_at_its_turn_count` was added and the mutant then failed.

## Formal A launch checkpoint — 2026-11-10

## 1. 规划完成情况

**汇总：** PASS 2｜BLOCKED/FAILED/SKIPPED 2｜TODO 2

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 01 输入 | PASS | D34原位审计及native parity已接受 |
| 02 逐turn测量 | TODO | CPU已接受；GPU检查等待A首个正式update |
| 03 Profile集成 | PASS | 15186817、201项CPU检查、两轴无发现 |
| 04 A/full | TODO | exp-1110-014836-849060已提交，启动证据部分到达 |
| 05 B/full | BLOCKED | 等待A实际首ACK和完成D16检查 |
| 06 终态报告 | BLOCKED | 等待两cell终态及profile完整性 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** CPU readiness checkpoint至本次正式提交｜**当前前沿：** 04 startup与首update检查

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 最终配置/回执检查已完成，实际A已提交；无新GPU smoke |
| D2 细节反复重试 | CLEAR | 单次正式提交成功，无GPU重试 |
| D3 支线问题修补 | CLEAR | 本窗口只推进04准备及执行 |
| D4 可并行任务停滞 | CLEAR | B有真实A首ACK依赖；只读首update观察已启动 |
| D5 超范围镀金 | CLEAR | 保留既定36H800和200update配置 |
| D6 分析空转 | CLEAR | CPU里程碑已转为实际formal job |
| D7 路线违背 | CLEAR | D35/02/03前置满足，D16和soft gates保留 |

**文档检查：** S1–S6均未发现明显缺陷；当前状态已同步实际提交，历史ready记录保留原时间范围。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 04：确认全部worker与引擎启动，完成实际首ACK/D16检查 → 完成标志：native与profile分别有可追溯判定。
2. 并行：A继续训练 ‖ 首ACK/检查完成后B fresh admission → 完成标志：B提交回执；不等待A200或辅助PASS。
3. 两cell约20update报告阶段耗时，终态后按06核对200成功update和完整paired profile。

## 4. 最值得关注的 3 点

1. A已提交且身份/资源/source匹配，但当前只确认rank0和teacher的12张实际H800。
2. 首个实际ACK和profile检查尚未到达，B仍有真实启动依赖。
3. 正式产物不属于smoke清理范围；profile辅助失败不会停止健康native训练。

## in-progress

- Latest startup diagnosis18:22Z: student0/1/3 plus teacher have28 actual H800; student2 remains`PodScheduled=False/Unschedulable`. Exact replica/Pod Events confirm resource placement failure, with10 retained`FailedScheduling`records and no missing pagination. Ray-head startup deadline is approximately18:23:53Z; acquisition has not started and this is not a D6/D19 throughput result. The previous12-GPU snapshot below is historical. No live timeout/config/placement change was made. See[formal execution report](test_report_2026-11-10_formal_runs.md#partial-placement-observation--1822z).

- Current frontier: A/full`exp-1110-014836-849060`startup and first actual successful update/D16 inspection. Submission and direct platform readback are committed in`1976048f`;36 non-preemptible H800, personal creator and local NFS source match. Initial platform state was Starting. Worker evidence now confirms rank0's8 H800 and the ready27B teacher's4 H800, both with the frozen image/model paths; the other student ranks and all-engine/first-update readiness are not yet confirmed. See[formal execution evidence](test_report_2026-11-10_formal_runs.md). Local launcher`sh_1c16d0f990014RQthEERNRrdWW`remains alive; read-only observer`sh_1c16ff2bb0017aVjX6GHz8NQ1s`will notify on the first native update without controlling training.

-02 GPU/full-ticket acceptance remains at A's first actual formal successful ACK and completed D16 inspection: actual bank membership, token/row/uid consistency, collection/teacher/training timing and both profile files/recomputed values. Auxiliary profile errors report unverified and permanently stop profile updates, not healthy native training. No additional GPU smoke is required.
- B's four-H800 TP4/EP1 teacher remains feasible, not native load/memory/throughput verified.05 admission remains authorized after A's actual first successful ACK, completed inspection and fresh resources while A continues; neither A200 updates, auxiliary profile PASS nor another user approval is required.
- Historical upstream frozen-D11 failures and independent ownership are retained below. D35 replaces their former parent blocking edge, not their evidence or verdict; no upstream acceptance, platform operation or stop is performed by this documentation delegation.

### Historical preparation snapshots — 2026-11-09 before D35

- failed upstream prerequisite, refreshed07:56:39Z: capacity job`exp-1109-144110-764758` finishedFailed at07:47:18Z. Initial`update_weights` began07:34:31Z and timed out at07:44:31Z after600s; the fatal stack is`train.py:169`, before rollout collection and optimizer updates. Student exited1; other roles were stopped after critical failure. This supersedes the07:45:51Z Running snapshot. Underlying synchronization cause remainsUNKNOWN; no OOM or manual-stop cause is inferred. Evidence:`evidence/upstream-weight-sync-timeout-20261109.json`; command/query limits:`test_report_2026-11-09_h800_preparation.md`.
- Historical first H800 attempt: `exp-1109-181120-274261`, submitted at10:11:20Z after freeze `a470c841`, Failed at10:29:35Z before weight publication or acquisition. The full log supersedes initial startup tails: two TP4 engines on rank2 first failed `ncclGetUniqueId` with invalid usage; subsequent `matches=[]` and supervision failures followed. Ray registered4 nodes/32 student GPUs. The head's serialized `ens20np0`/HCA values overwrote rank2's platform `ens22np0`. Isolated `cf98293a` removes that inherited NCCL broadcast; the real caller-to-subprocess regression is RED/GREEN, with529 affected tests passed,12 skipped and1 known-baseline parser case deselected. Complete fixed-diff review returned No Findings; native NCCL2.30.7 remains unverified.
- In-progress H800 D34 runtime verification: `exp-1109-192340-580111`, submitted at11:23:40Z from the current host after freeze `ebc0e6a0` and fresh personal admission,36 non-preemptible H800/codesign GPUs, creator `i-fengyicheng`, source `100.96.128.195:/data/ycfeng:/data/ycfeng`, student4×8/teacher1×4. Initial Starting is superseded by worker receipts confirming36 actual H800 GPUs at11:33:03Z, all8 rollout engines ready by11:36:41Z and successful initial8-actor `update_weights` from11:37:18.596Z to11:37:22.414Z (`ok=true`,elapsed_s3.8). Native bank/optimizer and representative capacity acceptance remain pending. Ordinary launcher: `sh_1c00ca257001FAmkzN0D28AQ9j`; log `/data/ycfeng/tmp/agent-opd-image/qwen35-h800-network-fixed-20261109.log`; cloud root `/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/capacity-h800-112k-network-fixed-20261109`. Authoritative receipts/report remain in the isolated preparation task, including `evidence/h800-network-fixed-initial-sync-20261109.json` and `test_report_2026-11-09_network_fixed_prelaunch.md`. Keep this launcher alive; the first attempt's launcher exited1.
- Gate boundary: upstream `agent-opd` at `23b29f66` has an approved original18-H200 retry but no new submission or acceptance as of11:19Z. It has not recorded this parent's112K/16K budget. Our H800 D34 readiness and upstream frozen D11 acceptance are separate; neither result may be relabeled as acceptance of the other. D1/D22 remain blocked until the upstream owner records authoritative acceptance. The parent's full D34 source audit is independent. No other job was stopped or held.
- Latest retained H800 synchronization observation (`2026-11-09T11:39:09.570570Z`): begin/end/tensor/distributed weight-update endpoints return HTTP200; initial8-actor sync completes in3.8s. `InferenceEngineWeightChecksumEvent` at11:37:27.670Z reports `weight_version=0` and `engine_snapshots=<list len=8>`; checksum contents and later changed-weight consistency remain unverified. Evidence:`/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity/task_memory/task_2026-11-09_profile_h800_preparation/evidence/h800-network-fixed-initial-sync-20261109.json`. This is initial synchronization underD34, not upstream frozenD11 acceptance or a successful native optimizer update. The CPU audit's11:32:18Z Running snapshot in`evidence/source-audit-112k-runtime-20261109.json` is historical and superseded by the accepted11:47:11Z terminal result above.
- Session cloud cleanup: the first terminal smoke's167 cloud duplicates/15,325,989 logical bytes were removed after a byte/hash-verified local backup; source assets, other tasks and shared trash were untouched. Raw diagnostic archive: `/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-181120-274261-cloud-raw.tar.gz`; selected evidence and the exact cleanup report remain in the preparation task. Physical OSS reclamation was not measured. The new live output root is not a cleanup candidate.
- D34 implementation history:128K training/rollout total,112K inclusive prompt budget,16K completion cap. Input adapter/checker changes were delegated to`profile-length-inputs-20261109` (`ses_e40c9ced3ffeuhJ4fOwvF1d5vS`); audit/submitter/synthetic commands to`profile-length-audit-20261109` (`ses_e40c9927efferVhKwq9xSHQCwk`); isolated upstream-based launcher wiring to`profile-length-launcher-20261109` (`ses_e40d1c58dffeRxbihEEvr5yxwj`). These CPU implementations and the original-source re-audit are complete; outputs are in`evidence/source-audit-112k-20261109`, preserving prior128K evidence. No running job configuration was changed.
- D33 execution: H800/codesign, no task GPU-count cap. Inspecting existing launch/config support and H800 memory sizing; no premature merge or02/03 implementation. Fresh direct personal API read at07:13:27Z:24 non-preemptible H800 GPUs committed across other jobs; upstream capacity job`exp-1109-144110-764758` is nowStarting,18 H200 GPUs. Receipt:`evidence/h800-resource-readback-20261109.json`. This is startup, not native acceptance.
- Local readback first failed with`ModuleNotFoundError: No module named 'tests.manual'`: importing Steptron prepends`third_party/super_agent/tests`, shadowing Miles' tests package. Importing the existing Miles budget reader before Steptron, as the established submitter already does, resolved it. No environment or launcher code changed.
- Resource preparation is isolated in`/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`, branch`agent-opd-h800-capacity` fromupstream`c52991ac`; parent integration remains gated. The existing admission field supports explicit`null` underD33 (`1ae93261`). The candidate`h800_gpu_policy.json` uses no count ceiling; its expired temporary-window entry selects the unlimited personal branch. Preparation records and candidate configs live in that worktree's`task_memory/task_2026-11-09_profile_h800_preparation/` and will be consolidated with code.
- Upstream refresh at2026-11-09T05:10Z (`ses_e43737fe8ffe4iK1j8uAE81u0C`): `agent-opd` at`d8c27b75`, no new256-turn acceptance. D1/D22 NOT MET. Latest D12 acquisition remains227/256<231 within1800s, zero updates; OOM mechanism patch has no completed two-update native capacity proof.02/03 integration and formal cells remain blocked.

### Latest completed work

- Standards/Spec review of`20d0b3f4...0e94c522` and repairs are complete. Reviewer sessions:`ses_e4373800affezhqaC06Ftzyn1p` and`ses_e43738006ffeim4QCGXqygBMha`; all findings closed.
- Historical pre-D34 Ticket01 acceptance: CPU job`exp-1109-031258-820360` finished at2026-11-09T00:24:08Z. Direct personal Python query at05:11:30Z confirmed job/replica Succeeded and worker completion marker. Original source identities/counts,512 native parity draws and2,048 interleaved draws were inspected. Historical128K results and limits: [source test report](test_report_2026-11-09_source_audit.md); terminal receipt:`evidence/source-audit-terminal-20261109.json`. Current112K acceptance is recorded under completed above.
- Historical128K D26/source result: eligible-turn median90 before length filtering retained32×8;27.51% rejection,32×8 simulated span median7 and17/745≥11updates applied only to the old prompt threshold, not current112K. Neither audit measures runtime trend coverage. Source first-message`preserve_thinking` is absent in all9,254 conversations; the Qwen config explicitly sets it true. Native task identity remainsunverified/null. Current rejection/span values are in the D34 acceptance above; scientific parameters remain unchanged.
- Repairs implemented: native module cache requires matching verified code and object identity; audit exact-text grouping is separate from task identity; historical profile entry/ratio queries and partial-write isolation are verified. Final affected fast suite:15/15 PASS. Complete synthetic worker audit → parity PASS; retained changed-identity fixture audit/check PASS. Task document links/DAG/arithmetic: zero errors. Commands and evidence: [test report](test_report_2026-11-09_review_execution.md).
- Repair milestone committed as `a0b0d113`. Independent Spec remediation review closed all five findings with zero new actionable findings. Standards remediation review closed all four original findings; its last P3 (temporary-only document checker) was fixed by retaining the script byte-for-byte under `tests/manual/agent_opd/check_profile_docs.py`, with `cmp` and the retained check passing (73 links/22 anchors/0 errors). All review findings are closed. No new experiment choices or upstream edits were made.

## pending

1. Primary/04: finish fresh live resource admission and formal identity/configuration/input/model freezing, then submit A through the existing approved mechanism. CPU integration, explicit profile configuration and before-run lifecycle checks are complete; no new review/user approval or GPU smoke gate is introduced.
2. Primary/02/04: at A's first actual successful native ACK, complete and record D16 inspection and the02 GPU verdict. Profile auxiliary failure is reported separately underS7; healthy native training continues. Near update20, report stage-time trends; actual sample failures remain individually attributable and need post-run RCA.
3. Primary/05: after A's actual first ACK and completed inspection, perform fresh B resource admission and run concurrently with continuing A if resources allow. Do not wait for A200 or require profile PASS.04/05 each need their own200 actual successful ACKs and separate complete/incomplete paired-profile disposition;06 follows terminal evidence.
4. Upstream may continue its own frozen-D11 acceptance independently; no parent action waits for it underD35 and no result is relabeled as upstreamPASS.

## Scoped checkpoint — profile-source-audit-112k-records-20261109

### 1. 规划完成情况

**汇总：** PASS1｜BLOCKED/FAILED/SKIPPED5｜TODO0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
|01含D34 | PASS | 原位112K审计、parity、终态与本轮指定文档已核对。 |
|02 | BLOCKED | D1/D22未验收、未合并。 |
|03剩余接入 | BLOCKED | CPU模块已完成；接入仍依赖02。 |
|04 | BLOCKED |02/03接入未就绪；无正式update。 |
|05 | BLOCKED | 接入未就绪；A真实首update/inspection缺失。 |
|06 | BLOCKED | 正式cell证据尚无。 |

### 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次文档/evidence委派开始至112K验收记录完成｜**当前前沿：** 主agent的隔离H800 D34 native验证与上游owner的冻结D11验收；本委派只交付文档/证据。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
|D1工具打磨 | CLEAR | 复用现有文档checker；仅JSON readback，无新增测试框架。 |
|D2细节反复重试 | CLEAR | 单次本地字段类型错误经实际结构核对修正，不改参数/业务。 |
|D3支线问题修补 | CLEAR | 仅指定文档与新审计证据；H800只读已提供receipt。 |
|D4可并行任务停滞 | CLEAR | CPU证据收口与主agent H800工作独立；本委派明确禁止再委派。 |
|D5超范围镀金 | CLEAR | D34要求重验新阈值；未更改32×8或引入新blocker。 |
|D6分析空转 | CLEAR | 证据核对已转成01 done和指定记录更新。 |
|D7路线违背 | CLEAR | 无merge/代码/平台操作；D1/D22、D11与D34分开。 |

**文档检查：** S1/S2/S3/S4/S6未发现新增缺陷。S5：`tickets/04-a-full.md:18`与`tickets/05-b-full.md:18`仍称01因D34重开，已被01当前done状态取代；两票不在本委派编辑范围，交主agent修正。指定七份文档中的旧128K/current112K混淆已修正。
**归因：** 无执行偏离；剩余S5为外部ownership的状态文字，实际02/03及正式cell阻塞不变。

### 3. 纠正建议

**分支：** B：先由主agent修正剩余S5，不改变验收条件。

**文档更新（先执行）：**
1. `tickets/04-a-full.md:18`、`tickets/05-b-full.md:18`：把01 reopened子句改为01 accepted；保留所有02/03、D1/D22和A首update阻塞（可直接执行，交主agent；本委派不编辑）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 主agent继续隔离H800 D34验证；完成标志是实际native bank/scoring/optimizer证据，不能只用initial sync。
2. 并行：上游owner取得冻结D11自身验收；只有权威D1/D22验收后才merge→02 CPU→03接入→04。

### 4. 最值得关注的 3 点

1. 112K源审计已完成，01不再等待CPU结果；历史128K产物完整保留。
2. 过滤后每conversation中位数未验证；模拟跨度不等于native trend；D26继续32×8。
3. 36实际H800/all8 engines/initial sync3.8s不等于上游D11、native optimizer或正式cell验收。

## Historical scoped checkpoint — profile-d35-records-20261110 before merge55fba827

### 1. 规划完成情况

**汇总：** PASS1｜BLOCKED/FAILED/SKIPPED4｜TODO1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
|01 | PASS | 原位112K审计与CPU parity已接受；本轮不重开。 |
|02 | BLOCKED | D35容量已接受；候选merge尚未执行，逐turn代码未实现。 |
|03 | TODO | 纯模块CPU已接受；接入与native计数仍待02 CPU-ready。 |
|04 | BLOCKED | merge/02/03接入缺失；没有formal attempt。 |
|05 | BLOCKED | 同上，另缺A首次formal successful update与inspection。 |
|06 | BLOCKED | 两个formal cell的终态与profile证据尚无。 |

### 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** D35用户选择至本轮指定父task记录更新｜**当前前沿：** 主agent合并候选和prep records，然后02 CPU→03接入。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
|D1工具打磨 | CLEAR | 复用既有docchecker；未增加GPU smoke、源扫描或测试框架。 |
|D2细节反复重试 | CLEAR | 本轮仅核对已保留terminal evidence，无容量重试。 |
|D3支线问题修补 | CLEAR | 只修改指定父task文档，prep/upstream/code/platform不变。 |
|D4可并行任务停滞 | CLEAR | 主agent明确等待本轮共享文档提交后merge；同checkout存在资源冲突，上游独立不被hold。 |
|D5超范围镀金 | CLEAR | D35只变容量依据；full/32×8/200 updates/soft gates不变。 |
|D6分析空转 | CLEAR | 明确用户选择已转成当前gate和merge→02→03路线，不新增研究。 |
|D7路线违背 | CLEAR | 按后续明确D35更新父契约；旧D1/D22与上游失败保留，不冒称集成完成。 |

**文档检查：** S1–S6均未发现当前缺陷；原有上游等待状态已按D35同步，旧日期证据明确标为historical。合并后的prep引用解析由plan当前frontier拥有，不是新验收或无owner blocker。
**归因：** 无。

### 3. 纠正建议

**分支：** A：当前spec/tickets已对齐D35，无需再改变范围或验收条件。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 主agentmerge候选和prep records → 完成标志：实际merge commit、代码冲突处理和repo-local evidence解析已记录。
2.02 CPU→03接入CPU → 完成标志：各ticket代码/计数/identity/S7条件在真实接入路径通过；不新增GPU smoke。
3.04正式A首update/inspection→05资源准入 → 完成标志：D16真实ACK/profile检查已记录；各cell完整native/profile分别验收。并行：上游独立冻结D11工作，不阻塞本路线。

### 4. 最值得关注的 3 点

1. D35接受的是完整H800容量证据，不只是initial sync；上游自身验收没有被冒认。
2. merge、02逐turn、03接入均未完成；纯模块CPU PASS不代表集成PASS。
3. A首个formal successful update承担D16原生profile检查；不额外smoke，不把辅助错误升级为training stop。

---

### Historical merge milestone checkpoint — before02 CPU-ready6129aefe

## 1. 规划完成情况

**汇总：** PASS 1｜BLOCKED/FAILED/SKIPPED 4｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
|01 | PASS |112K原始源审计已接受；merge保留parent input字节且139 tests/七项native合成检查PASS。 |
|02 | TODO |`55fba827`解除merge依赖，当前实现前沿；CPU-ready/GPU验收尚未记录。 |
|03 | BLOCKED | 纯模块CPU已接受；接入等02 CPU-ready，不能由容量/input检查代替。 |
|04 | BLOCKED |02/03 CPU-ready缺失；没有formal attempt或profile首update证据。 |
|05 | BLOCKED | 同上，另等A实际首次formal ACK和inspection。 |
|06 | BLOCKED | 两个formal cell终态与profile完成判定尚无。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 前次D35 checkpoint至本轮merge后记录更新（TaskID`profile-d35-records-20261110`）｜**当前前沿：**02实现与CPU-ready；primary协调独立实施。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 本轮用户要求状态同步；复用docchecker/evidence checker，未新增harness或GPU smoke。 |
| D2 细节反复重试 | CLEAR | merge和139/七项检查明确推进；本地whitespace路径解析一次按真实diagnostic边界修正，未改业务或反复试参。 |
| D3 支线问题修补 | CLEAR | inherited XML/diff和既有parser/lint仅归因留存，不修补历史证据或无关code。 |
| D4 可并行任务停滞 | CLEAR | merge前input冲突为真实依赖；merge后02立即成为前沿，primary独立协调agents，本slice不持有其code。 |
| D5 超范围镀金 | CLEAR | 仅更新已完成merge事实，保留32×8/full/200-update和S7标准。 |
| D6 分析空转 | CLEAR |`55fba827`和本地解析/字节验证直接用于解除merge等待，无新研究文档。 |
| D7 路线违背 | CLEAR | D35授权merge已执行；02/03 CPU-ready未冒认，GPU/profile仍按D16正式首update验收。 |

**文档检查：** S1–S4/S6无明显缺陷；S5：合并前`plan.md`当前前沿、`requirements.md`phase、tickets02–05及summary/progress仍写merge pending，本轮已同步；`spec.md`S0仍写“实际合并仍pending”，primary-owned，待同步。先前D35/input resolver报告保留其原始pre-merge时间范围，不视为新blocker。
**归因：** 无执行偏离；S5为完成milestone后的状态同步，不改变契约。

## 3. 纠正建议

**分支：** B：spec/tickets状态有S5，先同步事实，不改变范围或验收。

**文档更新（先执行）：**
1. `requirements.md`phase、`plan.md`当前前沿、`progress.md`、`summary.md`和tickets02–05：记录merge`55fba827`已验证，02为前沿，03仍等02 CPU-ready（可直接执行，本轮已更新）。
2. `test_report_2026-11-10_input_merge.md`：追加真实merge、prep路径解析、checker及历史whitespace限制；不改旧input slice的原始结果（可直接执行，本轮已更新）。
3. `spec.md`S0：primary将当前merge pending状态改为`55fba827`已完成，保留历史gate和D35行为（可直接执行，但本slice无文件ownership；已交接，不阻塞02）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1.02实现：既有tensor循环生成逐turn sums、CP汇总和uid/native计数一致性 → 完成标志：ticket02 CPU implementation-ready条件通过并记录。
2.03接入：02 CPU-ready后验证真实`SweReplay.on_train_result`identity/finished/skipped/S7传播 → 完成标志：ticket03 integration CPU-ready；primary可并行协调不依赖02完成的准备工作和状态同步。
3.04正式A首update/inspection→05资源准入 → 完成标志：D16真实ACK和profile检查记录；辅助错误按S7隔离，不增smoke、不阻止healthy training。上游冻结D11可独立继续。

## 4. 最值得关注的 3 点

1. merge`55fba827`已验证、七个prep引用已解析；17处历史whitespace是incoming原始artifact，不是新merge代码错误。
2.02当前可实施；03接入仍等02 CPU-ready，input/capacity PASS不能替代逐turn/profile验收。
3. primary还需同步spec S0状态；正式A首个successful update承担D16 GPU/profile检查，不新增GPU smoke。

---

## 1. 规划完成情况

**历史汇总（02 trainer CPU milestone，03验收之前）：** PASS 1｜BLOCKED/FAILED/SKIPPED 3｜TODO 2

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
|01 | PASS | 原始源112K审计与输入契约已接受，未重开。 |
|02 | TODO | Trainer CPU-ready`6129aefe`已接受；下游S7和A首formal update的GPU验收仍未完成，非ticket done。 |
|03 | TODO |02依赖已满足，指定agent已stage201-PASS CPU-ready交付；primary acceptance/commit未记录。 |
|04 | BLOCKED | 等03 CPU-ready和formal launch准备；无A actual ACK/profile验收。 |
|05 | BLOCKED | 等03及A首次actual ACK/inspection/资源准入；B native teacher仍未验证。 |
|06 | BLOCKED | 两个formal cell终态与profile完成判定尚无。 |

## 2. 偏离检测

**结论：** 已偏离：命中D2，仅本轮文档patch重试；业务代码/测试milestone仍直接推进主线，局部纠正已应用。
**检测窗口：** 上次merge checkpoint至02 CPU-ready`6129aefe`及本次记录同步（TaskID`profile-d35-records-20261110`）｜**当前前沿：**03 primary验收；并行review/formal修正已完成，native配置准备继续。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR |110/79测试与8-process检查直接验收S3；通过后转03，仅按用户要求同步文档，未扩展harness。 |
| D2 细节反复重试 | HIT | 本slice多次手工重建旧paragraph的空格导致patch拒绝；没有先核对字面原文。已停止猜测，实际重读progress/summary后成功更新，未影响并行03。T02业务测试和formal RED/GREEN本身不是此偏离。 |
| D3 支线问题修补 | CLEAR | Estimator/native index传输和formal budget guard均在既有S3/S8执行路径，不修无关parser/历史artifact。 |
| D4 可并行任务停滞 | CLEAR |03已stage交付，Standards/Spec reviews和formal修正独立完成；无可执行项因等待A200updates而闲置。 |
| D5 超范围镀金 | CLEAR | 复用既有ACK/tensor循环；仅拆开原一致性条目的trainer/下游状态，不新增机制或验收。 |
| D6 分析空转 | CLEAR |`6129aefe`代码/测试完成后立即交接03；只引用现有proof reports，不新增研究文档。 |
| D7 路线违背 | CLEAR |02 CPU-ready不冒认GPU/S7；full仍200 distinct banks一次访问；S8允许A首ACK检查后并行B，无新审批或smoke。 |

**文档检查：** S1依赖正确：03等02 CPU-ready而非02GPU/全部done；S2所有未完成项已有03/04/05/primary owner；S3标准可达且B TP4/EP1只是feasible；S4以明确CPU/ACK/JSONL条件判定；S5本轮前plan/progress/summary/tickets02–05落后于`6129aefe`，已同步，`requirements.md:59`phase仍由primary同步；S6原一致性trainer与03全链路条件已拆开标状态，原scope/criteria不变。上次spec merge-pending S5已解决，历史checkpoint不改写。
**归因：** D2执行偏离，与spec/tickets无关；S5另为完成milestone后的状态同步。

## 3. 纠正建议

**分支：** B：当前状态有S5，先同步事实，不改spec scope或准入。

**文档更新（先执行）：**
1. `plan.md`/`progress.md`/`summary.md`和tickets02–05：记录02 CPU-ready及active03；一致性条目分别标已验收trainer和pending下游S7/GPU，保留历史snapshot（可直接执行，本轮已更新）。
2. `requirements.md:59`当前phase：primary将02 frontier改为已接受CPU-ready/03 executing，其余决定不变（可直接执行，本slice无ownership，不阻塞03）。

**需停止的偏离行为：**
- D2：停止凭记忆重建旧paragraph或压缩其空格；改用最新字面文件内容、缩小patch块并验证再继续。本轮已应用，不新增测试工具或重跑业务检查。

**接下去的路线：**
1. Primary验收/提交03交付 → 完成标志：真实`SweReplay.on_train_result`successful/skipped、bank/finished identity、native计数及永久S7 suppression验收通过，CPU-ready与实际commit记录完成。
2. 并行：primary最终profile配置/启动验证 ‖ 当前requirements状态同步；T02 reviews`ba3cb696`和formal修正`059a6a75`已完成，不重复开工。
3.03 CPU-ready后launchA；A首次actual ACK/inspection→B fresh资源准入，可与继续运行的A并行 → 完成标志：D16 GPU/profile检查及各cell自己的native/profile判定；不另增用户审批或GPU smoke。

## 4. 最值得关注的 3 点

1.02 trainer CPU-ready已接受；全ticket仍缺下游S7/GPU证据，combined criterion未被错误整项勾选。
2.03已stage201-PASS交付，仍待primary验收/提交；两个T02 reviews已0/0完成，requirements phase文字待primary同步。本slice局部patch重试已纠正，没有停住业务主线。
3. formal`bank_uses=50`已真实RED/GREEN且full仍每bank一次；B TP4/EP1只是可行性，不是native验收，原A首ACK后并行准入不变。

## Final CPU readiness checkpoint — profile-d35-records-20261110

## 1. 规划完成情况

**汇总：** PASS 2｜BLOCKED/FAILED/SKIPPED 2｜TODO 2

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
|01 | PASS | D34输入/原位112K审计已接受，未重开。 |
|02 | TODO | Trainer及下游S7 CPU已接受；仅正式A首个actual successful update的GPU验收仍未完成。 |
|03 | PASS | Primary接受 `15186817`；201 PASS覆盖全部CPU/module/真实consumer/S7条件，ticket done不代表正式GPU验收。 |
|04 | TODO | CPU、显式profile配置 `ec002ea8` 和启动前lifecycle检查完成；可进入fresh admission，尚未launch。 |
|05 | BLOCKED | 等A首次actual successful ACK、完成inspection和fresh资源准入，不等A200/profile PASS。 |
|06 | BLOCKED | 等两个formal cell终态及native/profile完整或不完整判定。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进；CPU代码、测试和配置milestone直接推进formal主线。
**检测窗口：** 上次02 CPU milestone checkpoint至03 primary接受 `15186817`、final配置 `ec002ea8` 和本次启动前记录｜**当前前沿：**04 fresh admission / A首个actual update。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR |201-case真实路径及16-case lifecycle检查直接验收接入/启动准备；不新增工具或重复GPU smoke。 |
| D2 细节反复重试 | CLEAR | 本窗口按实际字面原文做小范围状态更新，无反复修复；旧checkpoint的patch重试HIT保留为历史。 |
| D3 支线问题修补 | CLEAR | 仅更新指定当前状态，不修历史artifact、Python/config/proof reports。 |
| D4 可并行任务停滞 | CLEAR | Review、配置、lifecycle和primary只读admission独立推进；B仍在A首ACK检查后可并行，无A200等待。 |
| D5 超范围镀金 | CLEAR | 不增机制、验收、审批或任务文件；只按已接受证据完成现有CPU条目。 |
| D6 分析空转 | CLEAR | 接受CPU证据后立即转fresh formal admission，不重做capacity/source audit或无关研究。 |
| D7 路线违背 | CLEAR |02 GPU仍未勾选；D16在A首actual update，S7是soft gate，B不依赖profile PASS或A完成。 |

| 文档模式 | 判定 | 依据 |
| --- | --- | --- |
| S1 依赖错误 | CLEAR |03的CPU依赖已满足并done；04不等待自己才能提供的02 GPU证据；05只等首ACK/inspection/fresh资源。 |
| S2 无法执行的待办 | CLEAR | Fresh admission/submit、D16 GPU检查、B准入和终态/RCA均明确由primary及04/05/06负责。 |
| S3 不可能的标准 | CLEAR | 原CPU条件已实际通过；native及200-update条件留给实际run，B TP4/EP1可行性不冒认native验证。 |
| S4 模糊标准 | CLEAR |03所有CPU条目有201-case真实路径证据；formal依据actual ACK、成对文件、实测计数与明确完整性判定。 |
| S5 文档落后 | FOUND → CORRECTED | Requirements phase、spec S0和当前plan/progress/summary/tickets02–05原有staged03/wait02状态已同步；旧报告/历史checkpoint不改写。 |
| S6 范围或验收变更 | CLEAR | 仅完成已有03 CPU及02下游S7 CPU条目；02 GPU与04/05全部formal条件仍未勾选，不放宽scope。 |

**归因：** S5来自已接受milestone后的状态同步，不是新业务缺陷；已在本授权范围纠正。Review在请求时Spec-pending，但实际读取的primary记录已为No findings；不以预判完成review。

## 3. 纠正建议

**分支：** B：先同步已接受事实，已完成；不改行为规格或formal准入。

**文档更新（已执行）：**
1. Requirements只更新phase、spec只更新S0当前状态；plan/progress/summary与tickets02–05记录03 done CPU、02下游S7 CPU已接受但GPU未完成、04 ready/not launched及05实际准入边界。
2. 在launch前记录primary已完成的lifecycle检查及既有report/精确命令链接；保留mock与实际GPU/RCA限制，不新建报告或重复检查。

**需停止的偏离行为：** 无新命中；不扩展历史清理、额外review、工具或GPU smoke。

**接下去的路线：**
1. Primary/04：fresh只读资源准入 → 冻结attempt/源代码/解析配置/输入/模型identity → A正式提交。完成标志：实际准入与提交receipt，不能由dry-run代替。
2. Primary/02/04：A首actual successful ACK → 完成并记录D16 inspection/GPU verdict。完成标志：实际bank/uid/token/行数、stage timing、两个profile文件及复算值；辅助unverified按S7隔离，不停止healthy native training。
3. Primary/05：上述ACK/inspection完成后fresh资源准入，可与继续运行的A并行。完成标志：B自己的submit/native首update/终态证据；不加A200/profile-PASS/用户审批gate。随后两cell各自200-update与profile完整性/RCA →06。

## 4. 最值得关注的 3 点

1.03已primary接受并完成全部CPU条件；02仅GPU验收未完成，CPU/dry-run不代表native acceptance。
2. Before-run lifecycle检查和报告链接已在launch前记录；fresh admission/actual A launch、实际sample失败和RCA仍未验证。
3. B等A首次actual ACK和完成inspection/fresh资源，不等A200或profile PASS；S7失败只标未验证并停止profile派生，healthy训练继续。
