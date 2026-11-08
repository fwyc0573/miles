## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Repair native orchestrator field ownership for reward postprocessing and OPD mode; verify six typed lifecycle views and explicit formal/smoke factories. |
| 2026-11-08 | T02-REMEDIATION: separate mandatory masks from optional diagnostics, protect ACK sinks, release banks on ACK and record teacher stages. |
| 2026-11-08 | Document T02-native callable/driver integration and remaining GPU prerequisites. |

# T02-native integration API

Implementation and CPU verification, including T02-REMEDIATION, are complete for this slice. T01 is accepted in `20d0b3f4`; Ticket 02's actual native GPU integration/acceptance remains pending. No GPU jobs, platform operations, commits or cloud changes were made by T02.

## Launcher hooks

Use the existing native `train.py`, Megatron actor, rollout plugin and configured T01 `data_source_path`. Select these callable paths:

| Existing/native CLI field | Callable |
| --- | --- |
| `--rollout-function-path` | `tests.manual.agent_opd.swe_replay.SweReplay` |
| `--custom-rm-path` | `tests.manual.agent_opd.swe_replay.score_teacher` |
| `--custom-reward-post-process-path` | `tests.manual.agent_opd.swe_replay.post_process_rewards` |
| `--custom-tis-function-path` | `tests.manual.agent_opd.swe_tis.apply_tis` |
| New `--custom-megatron-optimizer-step-hook-path` | `tests.manual.agent_opd.swe_training.optimizer_step` |

The new optimizer hook is optional and defaults to `None`. Its callable's `training_protocol` attribute installs only the successful-result seam in the existing synchronous driver; it does not launch or run a second trainer.

`SweReplayConfig` owns custom fields and formal defaults. Required launch fields are `--swe-cell`, `--swe-attempt`, `--swe-protocol full|r256`, `--swe-teacher-identity`, and `--swe-evidence-dir`. Use a unique attempt and directory for each cell. The source metadata must contain T01's `metadata.source.uid` and `prompt_token_count`; native sample groups are `list[list[Sample]]`, with one Sample per group. Keep the native generation callable supplied by T01 and set `--rm-url` to the selected frozen teacher's actual `/generate` endpoint.

`SweTISConfig` owns the four D4 thresholds. `training_protocol()` in `swe_replay.py` validates the S4 recipe, native Adam parameters, frozen thresholds, fresh actor scoring, inline dense payloads, dynamic partial scheduling, and HF-only storage before GPU allocation. It rejects a shortened run unless explicitly labeled `--swe-run-kind smoke`.

For a shortened smoke, specify both `--swe-run-kind smoke --swe-successful-updates N` and `--num-rollout N`; bank slots/uses may be shortened explicitly in the smoke config if needed. Formal defaults must remain unchanged. `num_rollout` denotes the successful-update budget only when this protocol is configured. Generic driver behavior is unchanged otherwise.

Native scheduling must enable `--use-dynamic-batch-size --use-dynamic-global-batch-size --allow-partial-train-step`. Keep `use_tis=True`, `use_output_store=False`, fresh native actor forward enabled, `use_rollout_logprobs=False`, `keep_old_actor=False`, `true_on_policy_mode=False`, and native `calculate_per_token_loss=True`. Optimizer/config checks are source-owned by `training_protocol()`; do not duplicate or override its frozen science in the launcher.

## Native configuration-view contract

The production invocation in `train.py:130–133` and `check_swe_launch.py:59–63` is unchanged: slice the parsed `AllConfig` to `OrchestratorConfig`, then call `training_protocol(compute_custom_function_config(orchestrator, optimizer_hook))`. Do not replace this typed view with a flat namespace or transport native fields through a duplicate SWE custom schema.

The pinned-image receipt `native-launch-config-exp-1108-164121-488177.json` proves Megatron parsing completed for all four cells, but the subsequent factory failed. Two existing declarations belonged to rollout-only schemas despite being consumed by the driver:

- `miles/utils/args/configs/reward_model.py`: `custom_reward_post_process_path` now belongs to the existing shared `RewardModelConfig`.
- `miles/utils/args/configs/on_policy_distillation.py`: `opd_log_prob_top_k` now belongs to the existing shared `OnPolicyDistillationConfig`, because the sampled-token objective choice is also a training/driver constraint.

The declarations were moved, not copied. Their CLI spelling, metadata and defaults are unchanged. Existing component inheritance and the existing custom-view merge now carry them; no caller fallback, merge override or new launcher field was added. SWE startup also explicitly requires its native rollout and teacher-score hooks, and rejects an absent or different canonical reward postprocessor.

`tests/fast/test_swe_replay.py:76–179` covers the actual validated typed slice/JSON transport/merge/factory route for A/B, full/r256, formal and explicitly shortened smoke configurations. A proportional source-read audit verifies all configuration reads in six native lifecycle views: driver, replay/native generation helpers, teacher request/validation, reward postprocessing/native OPD conversion, optimizer hook, and TIS. Required-hook negative cases and rejection of shortened formal budgets remain enforced.

CPU tests validate real post-parse `AllConfig`, `OrchestratorConfig`, `RolloutConfig`, `TrainerConfig` and `ImmutableNamespace` schemas. Their parse-boundary fixture does not execute or mock Megatron's GPU-dependent parser. Parent must sync both native declaration changes and rerun the unchanged pinned-image checker before claiming production configuration acceptance. Two existing parser-backed custom-view tests cannot run locally because the CPU environment lacks the `megatron` package; their failure is retained, not hidden or mocked.

## Authoritative result and save/eval seam

1. The optional native hook receives `stage`, `rollout_id`, `step_id`, `data_iterator`, `model`, `optimizer`, `losses_reduced`, and `update_successful` immediately before/after the native optimizer boundary.
2. Its post-boundary dictionary is returned as `TrainStepOutput.optimizer_step` from every Megatron worker. Rank 0 broadcasts the identical record to avoid per-rank timestamp/metadata divergence.
3. Existing `train.py` calls `training_protocol.accept(train_outputs)`, then `rollout_executor.notify_train_result(rollout_id, step_result)` **before** releasing rollout payloads. `SweReplay.on_train_result()` commits only the returned native success signal.
   When this ACK crosses a bank boundary or exhausts the successful-update budget, the plugin immediately drops its canonical payload, bank identity and token count before the next acquisition. A skipped step retains the same bank. Late acquisition tasks capture only their own candidate, not the complete candidate map.
4. `step_result["successful_updates"]` is authoritative. Driver `action_index=successful_updates-1` controls save/eval cadence and labels, and termination. Attempted `rollout_id` remains the identity for rollout acquisition and weight publication. Skips do not save/eval, change bank, or advance the successful budget.
5. Parent/T03 should retain the existing HF/evaluator implementations. The loop already passes successful `action_index` to `save()` and `eval_dispatcher.dispatch()`; use `action_index+1` for update labels. T02 did not change the checkpoint/HF branch itself.

`SweReplay` is training-only. Set the separate native `--eval-function-path` to the T03 evaluator; do not send evaluation requests to the replay plugin.

No JSONL, parsed stdout, timer or rank file drives replay. `optimizer_attempts.jsonl`, `updates.jsonl`, `failed_batches.jsonl`, `bank_N.jsonl` and `teacher_stages.jsonl` are evidence only. Acquisition/update/teacher evidence I/O errors are soft failures; file, stdout/flush and warning-sink errors do not stop healthy training. Pending optimizer state is cleared before update evidence I/O, and native success/count ACKs still return. Actual global zero-survivor D7 remains an approved pre-optimizer stop and writes available rank mask/snapshot evidence when storage works.

Teacher stage receipts identify `teacher_request` and `teacher_validation` start/end separately, with source UID, bank/slot, teacher identity/endpoint, actual token counts, timestamps, deadlines, elapsed time and success/error/cancellation. Request deadline records the earlier of the configured HTTP timeout and whole-acquisition deadline; validation records the acquisition deadline. A deadline unavailable outside acquisition is `null`, not invented. Request failure/cancellation does not produce a fictitious validation-start event. These receipts supplement existing native generation records and add no model forwards.

## Native payload and loss additions

- `teacher_log_probs` reaches the native training microbatch so the custom TIS path can produce pre-TIS sums using the frozen teacher targets.
- Mandatory `training_mask_counts` is a detached int64 `[original_tokens, surviving_tokens, turns]` tensor computed at the actual native loss masks. It bypasses native rate normalization and is independent of diagnostic `token_sums` or `mask_evidence`.
- Additive float64 `token_sums` contains optional KL/rejection/loss diagnostics, not the authoritative counts. Missing/nonfinite/incomplete global diagnostics remain `null`, with `diagnostics_verified=False` and `unverified_diagnostics`; missing snapshots set `mask_evidence_verified=False`. Native post-TIS `opd_reverse_kl` remains separate. Unknown diagnostics never become zero and do not block optimizer success; formal metrics acceptance still requires the verified requested series.
- Native shard packaging retains metadata for bank/visit/source ownership. The existing dynamic/partial schedule preserves accepted odd banks rather than trimming to DP multiples.
- D7 SUM-reduces mandatory actual counts over DP and CP with one TP/PP replica; turns contribute only on CP rank 0. Every rank joins this collective before reporting a missing mandatory native signal. An unavailable mandatory count is a uniform native contract failure (`D7 is unknown, not zero`), never a fabricated zero or an auxiliary-diagnostic verdict. Only a known actual global zero raises `ZeroTISSurvivors`. Optional diagnostic reduction also participates uniformly and does not index mask evidence to derive turns. Sealed-bank count comparisons remain soft observers.

## Remaining acceptance prerequisites

1. T01 input/teacher/source acceptance is recorded in `20d0b3f4`. Preserve that identity contract; all four native GPU cells must still use the protected original student and their independently verified actual serving teacher endpoint/model identity.
2. Actual CPU checks do not qualify CUDA, Megatron optimizer internals, Qwen model bridge, bf16 kernel numerics, TP/CP/DP topology, or real 128K throughput. Parent must run the actual shortened recipe for both teachers, fresh scoring on repeated visits, binary weights, exact primary KL/TIS sums, successful counters and skip behavior, then formal configurations.
3. Confirm actual 231/255 payloads preserve every UID under the chosen topology and token capacity. If all samples require singleton microbatches, native aligned schedule capacity can fail; raise capacity/topology issues explicitly, not by dropping samples or adding fake trajectories.
4. Measure the frozen 1800-second acquisition/231 minimum under the real Qwen serving configuration. A new bank starts its deadline before source consumption; replay visits do not start another acquisition timer.
5. Parent/T03 must verify HF-only saves at successful updates, evaluator dispatch/reader lifecycle and cleanup. These are not accepted by the T02 control-flow test.

Evidence and exact CPU commands: `../test_report_2026-11-08_replay_training.md`.
