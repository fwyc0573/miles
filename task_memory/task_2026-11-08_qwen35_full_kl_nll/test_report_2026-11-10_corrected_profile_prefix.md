## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Verify the actual retained corrected-A first two updates with existing CPU APIs; record exact errors, acquisition/version provenance, immutable inputs and incomplete-run limits. |

# Corrected A/full retained profile prefix — updates 1–2

## Result and ownership

**Local prefix verification PASS.** TaskID `profile-corrected-A-first-two-profile-20261110`, corrected A/full attempt `exp-1110-165312-132926`. Existing inspector verifies two successful native ACKs and a canonical paired profile prefix of two updates, containing **512 observations**. Rebuilding the **original** paired files reproduces the inspector profile's summary and every observation exactly.

**Formal acceptance is unfinished:** expected budget remains **200**, both `native.complete` and `profile.complete` are **false**, and the generated reporter returns native `INCOMPLETE`, profile `INCOMPLETE / UNVERIFIED`, overall `INCOMPLETE`. No terminal receipt was supplied. Training was active at snapshot retention; this local inspection does not observe its later state or accept the native offload/memory repair. Those operations remain primary-owned.

Only new small local evidence/report artifacts were written. No code, configuration, existing report, main task document, input, source dataset, or training artifact was edited. No platform/GPU/SSH/network operation, dependency installation, persistent test machinery, or further delegation was performed. No input was staged; no commit was made by this slice.

## Inputs and contracts

Snapshot root: `task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/formal-H200-A-r2-first-two-20261110/`, captured at `2026-11-10T09:54:56.550810+00:00` according to its original `retention.json`. The six raw files total **349,252,623 bytes**. Their sizes and SHA256 hashes matched the supplied retention manifest before inspection and remained identical afterward; the retention receipt itself was also unchanged. These are actual retained records, not synthetic fixtures.

| Raw file relative to snapshot | Bytes |
| --- | ---: |
| `training/updates.jsonl` | 3,129 |
| `training/optimizer_attempts.jsonl` | 3,103 |
| `training/bank_0.jsonl` | 70,797,558 |
| `training/bank_1.jsonl` | 278,378,782 |
| `training/distillation_profile/updates.jsonl` | 1,344 |
| `training/distillation_profile/observations.jsonl` | 68,707 |

Complete fingerprints are in [prefix-verification.json](evidence/formal-H200-A-r2-first-two-20261110/prefix-verification.json) and the final read-only preservation check in [delivery-verification.json](evidence/formal-H200-A-r2-first-two-20261110/delivery-verification.json).

Inspected contracts:

- `spec.md:154–184,271–291,303–322`: original-mask token sums, S7 isolated profile failure, S9 separate native/profile final acceptance and honest missing ranges.
- `tests/manual/agent_opd/inspect_distillation_run.py:70–100,103–208,211–239,256–333`: dense successful ACK sequence, full-mode bank/visit identity, sealed canonical UID/group/training-turn/original-mask binding, native numerator/denominator consistency, verified paired prefix and rebuild.
- `tests/manual/agent_opd/distillation_profile.py:264–320,322–383`: per-UID tokens and native means/estimator; first-appearance conversation mapping; original paired-file replay.
- `tests/manual/agent_opd/distillation_report.py:115–179,252–265`: existing S9 report computation and exclusive new output files, without changing completion verdicts.
- `tests/manual/agent_opd/swe_replay.py:152–230,390–429`: acquisition includes candidate draw/collection, generation, teacher scoring and validation; later training is not part of the acquisition duration. Materialized samples carry generation spans and the rollout input's current version.
- Native input/version serialization: `miles/utils/types.py:23–82,312–335`; train-data metadata/spans transport: `miles/ray/rollout/train_data_conversion.py:207–226`; native receipt selector/timestamps: `tests/manual/agent_opd/swe_training.py:277,297–322,349–365`.

The existing source audit/parity remains independently owned by Ticket01. This slice verifies retained canonical identity/masks; it does not re-read original source files or claim an independent SWE instance/repository/seed audit.

## Acceptance observations

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Input preservation | Exact original bytes/hash | All six raw files match retention manifest before/after; retention receipt unchanged | PASS |
| Native ACK identity | One actual formal A/full attempt and teacher | Both records are `exp-1110-165312-132926`, `A/full`, `formal`, `full`, Qwen3.5-27B teacher | PASS |
| Native counters/attempt pairing | Dense successful sequence; no hidden skipped attempts in retained prefix | successful/attempted = 1/1, 2/2; skipped = 0/0; optimizer-attempt rows exactly equal successful rows after excluding the added `update` key | PASS |
| Canonical identities/original masks | Per-UID group/training-turn/tokens match bank and profile | 256 one-to-one rows in each bank; 35,509/184,306 target tokens; all retained original masks binary and all ones | PASS |
| Original file pairing/rebuild | Two complete pairs; no reconstructed missing updates | Original files have 2 summary lines and 2 observation lines; exact summary and all 512 observation equality | PASS |
| Full-mode semantics | Distinct banks, each first visit; no turn replay | bank0/visit1 → bank1/visit1; all 512 replay numbers 0; UID and `(group_id,t_id)` intersections both 0 | PASS |
| Interleaved prefix | 32 conversations × 8 ascending training turns each | Both banks have 32×8; bank0 t_id 1–8, bank1 t_id 9–16; same 32 conversations | PASS |
| Macro sums/denominators | Profile sums/native numerators; original-token denominator | Both RKL/NLL numerators and means exactly match; denominators 35,509 and 184,306 | PASS |
| Acquisition | ≥231/256 within 1800s | Both 256/256, no missing/pending/invalid; 517.8451368808746s and 1409.9740009307861s | PASS |
| Retained length bounds | prompt≤114688; response≤16384 | Prompt maxima 55,049/86,644; response maxima 8,690/9,534 | PASS |
| Retained teacher alignment | Same teacher, response token count/alignment | Both banks: 256 sample metadata records with matching teacher, `token_ids_match=true`, scored tokens=response length | PASS, metadata scope |
| All-sample generation versions | Inspect actual decode/prefill spans, not just one receipt | Both banks: 256/256 samples with spans; bank0 exclusively version `"0"`, bank1 exclusively `"1"`; contiguous full response/prompt coverage | PASS |
| Formal/native completion | 200 actual successful ACKs plus successful terminal | 2 retained ACKs, no terminal receipt | UNVERIFIED / INCOMPLETE; not a prefix failure |
| Complete formal profile | 200 verified paired updates | Prefix 2; first unverified 3; missing/unverified snapshot range `[3,200]` | INCOMPLETE; not a observed S7 runtime fault |
| Native offload/memory repair | Primary's actual lifecycle/memory evidence | Not present in these six raw files | UNVERIFIED here |

`assistant_turn_ordinal`, not raw `assistant_turn_index`, is profile `t_id`. UID strings can encode the raw assistant message index. Inspector comparisons use the native canonical training-turn ordinal and group mapping.

## Exact profile-versus-native errors

Profile values below were recomputed by the existing `DistillationProfile.rebuild` from original per-turn observations. Native values are the retained `kl_before_tis` / `nll_before_tis`. Absolute error is `abs(profile-native)`; relative error is that absolute error divided by `abs(native)`. All four native values are nonzero, so relative error is defined. Zeros below are **calculated outcomes**, not an assumed tolerance result. Persisted profile macro values and native numerators also compare exactly equal.

| Update | Metric | Profile sum / original tokens | Recomputed profile | Native | Absolute error | Relative error | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | RKL | 3213.814534504751 / 35509 | 0.09050704144033206 | 0.09050704144033206 | 0.0 | 0.0 (0%) | PASS |
| 1 | Student NLL | 19820.859087655524 / 35509 | 0.5581925452041884 | 0.5581925452041884 | 0.0 | 0.0 (0%) | PASS |
| 2 | RKL | 20707.046249945928 / 184306 | 0.11235144949131297 | 0.11235144949131297 | 0.0 | 0.0 (0%) | PASS |
| 2 | Student NLL | 145353.02631683814 / 184306 | 0.7886505394118376 | 0.7886505394118376 | 0.0 | 0.0 (0%) | PASS |

These are pre-TIS, pre-optimizer measurements on original behavior target tokens. TIS survivors are separately 28,598/177,185, retention 0.8053732856458926/0.9613631677753302; survivor counts are **not** the profile denominator. No second model forward or independent loss recomputation was performed. Full machine values: [prefix-measurements.json](evidence/formal-H200-A-r2-first-two-20261110/prefix-measurements.json).

## Acquisition timings and generation-version provenance

| Observation | Bank0 / update1 | Bank1 / update2 |
| --- | ---: | ---: |
| `acquisition_start.started_at` | 1794301794.7310216 | 1794302529.6763701 |
| Start UTC | 2026-11-10T09:09:54.731022+00:00 | 2026-11-10T09:22:09.676370+00:00 |
| `acquisition_sealed.ended_at` | 1794302312.5761585 | 1794303939.650371 |
| Sealed UTC | 2026-11-10T09:18:32.576159+00:00 | 2026-11-10T09:45:39.650371+00:00 |
| Acquisition seconds, sealed minus start | 517.8451368808746 | 1409.9740009307861 |
| `acquisition_start.deadline_at` | 1794303594.7310479 | 1794304329.6764138 |
| Completed slots / candidate slots | 256 / 256 | 256 / 256 |
| Missing / pending / invalid slots | 0 / 0 / 0 | 0 / 0 / 0 |
| Event counts: start / slot_finished / sealed | 1 / 256 / 1 | 1 / 256 / 1 |
| Native `current_weight_version` | 0 | 1 |
| Samples with one generation call | 256 | 256 |
| All decode / prefill versions | `"0"` / `"0"` | `"1"` / `"1"` |
| Decode spans / prefill spans | 256 / 256 | 256 / 256 |
| Decode tokens with that version | 35,509 | 184,306 |
| Prefill tokens with that version | 3,280,534 | 9,312,800 |

For every completed `slot_finished`, actual generation receipts come from `sample.weight_versions[*].spans[*].{version,abs_start,abs_end}` and `sample.weight_versions[*].prefill_spans[*].{version,abs_start,abs_end}`. Each sample has one call; decode spans cover all its response tokens and prefill spans cover all its prompt tokens. Versions were read for all samples, not inferred from update/bank number or historical `metadata.messages` responses.

`CanonicalTrajectory.materialize` copies those receipts into `train_metadata.generation_weight_versions` (`swe_replay.py:119–137`). `SweReplay.__call__` sets `train_metadata.current_weight_version` from the actual rollout input scalar (`swe_replay.py:423–429`). The native training receipt reads only `data_iterator[0].rollout_data["metadata"][0]` (`swe_training.py:277,302–303`), so its `generation_weight_versions` is one selected train-data sample's receipt, **not a bank-wide aggregate**.

An initial supplementary comparison incorrectly assumed that selected metadata corresponded to canonical slot0; both slot0 comparisons returned **false**. The original output is retained unchanged in `prefix-measurements.json`. A focused read of all 256 samples then found exactly one matching native generation receipt per bank: bank0 **slot119**, source group suffix `:14`, training turn8 (47,878 prompt / 200 response tokens); bank1 **slot118**, same source group, training turn15 (85,887 / 68). This is an audit-assumption correction, not a native/profile defect or a changed training artifact. The exact UID/match evidence and final PASS are in [generation-provenance-verification.json](evidence/formal-H200-A-r2-first-two-20261110/generation-provenance-verification.json). Native train-data ordering itself is not retained.

All 512 retained **pre-materialization** bank samples were also checked: none has `current_weight_version` or `generation_weight_versions` inside `train_metadata`. Their `sample.weight_versions` does contain generation receipts. Consequently the bank files independently prove all-sample generation versions, while the native current-training scalar remains a single native receipt field; no per-sample trainer scalar or whole-model checksum equality is claimed.

The native record `timestamp` is captured in `before_optimizer`, then its success receipt is published after the optimizer boundary. Start-to-native-measurement intervals are 713.4096357822418/1678.9641244411469s; sealed-to-measurement intervals are 195.5644989013672/268.9901235103607s. They are **not** measured optimizer completion, scoring-only, training-only, teacher-stage, or pure profile CPU durations. Separate teacher-stage and trainer timing logs are absent from this six-file input, so those durations are unverified here.

This formal prefix uses **two newly acquired different banks once each**. It is not the earlier capacity smoke's one saved bank visited twice; retained group-turn and UID membership is disjoint between banks.

## Actual generated S9 report and limits

[Machine report](evidence/formal-H200-A-r2-first-two-20261110/profile-report-prefix.json) and [unmodified generated Markdown](evidence/formal-H200-A-r2-first-two-20261110/profile-report-prefix.md) are outputs from existing `build_report` / `write_report`. The inspector receipt is [inspection-prefix.json](evidence/formal-H200-A-r2-first-two-20261110/inspection-prefix.json).

- Configuration is the actual persisted estimator `sampled_current_student_minus_frozen_teacher_on_original_behavior_tokens`, B=10, k=10, N=8. Macro baseline is `null` / `INCOMPLETE`; macro remaining gap/trend/recovery and all run-relative gaps are null.
- **B10 and k10 are immature, but N8 is already complete:** all 32 conversations have a positive baseline from their first eight observations; 32 alive, zero nonpositive/incomplete conversation baselines, zero defined conversation trends. Each has 16 observed training turns by update2. No conversation is marked finished in either observation batch.
- Verified-prefix RKL-best is update1, RKL `0.09050704144033206`, NLL `0.5581925452041884`. This is only the best among the two inspected updates.
- Conversation remaining-gap quantiles p10/p25/p50/p75/p90 are `0.8347331861575763 / 0.9806800063748706 / 1.3357071813340502 / 1.6492960179174267 / 1.887001298260252`; recovery-gap quantiles are `0.0 / 0.0 / 0.33570718133405003 / 0.6492960179174267 / 0.8870012982602519`. Each has 32 defined values. These are prefix statistics, not terminal statistics or mature k10 trend evidence.
- Default S9 milestones remain 1/10/50/100/150/200: update1 VERIFIED; all later milestones NOT_OBSERVED with null values. Update2 is the report's latest verified row and is additionally detailed above.
- Inspector returns first unverified update3, missing-pair and unverified ranges `[3,200]`. These are **snapshot coverage relative to the unchanged 200 budget**, not evidence that live files stopped appending, a real profile error occurred at update3, or the remaining run failed.
- No terminal readback was supplied; `terminal_phase=null`, `terminal_job_verified=false`. Its native error is exactly `No terminal receipt supplied; native completion is unverified`; profile error is exactly `Verified profile prefix ends at 2; expected 200 updates`.
- Old failed A `exp-1110-140032-491115` remains independently **1/200 Failed**, as recorded in `test_report_2026-11-10_d16_first_update.md`. No row or terminal from it was supplied to this inspection or spliced into corrected A.
- Generation-version labels/metadata do not prove whole-model weight equality, native memory usage, the old allocation owner, or offload repair. The primary's native lifecycle/memory inspection and ongoing formal run remain independent.

## Commands, environment and verification results

All commands ran from `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Existing interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, **Python3.12.13**, built May10 2026 with Clang22.1.3; Linux5.10.25-nvidia-gpu x86_64, glibc2.35. `CONDA_PREFIX` was unset. Used `PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, `python -B`, and `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`.

Exact executable command bodies, including the existing API calls and read-only streamed checks, are retained in [verification-commands.md](evidence/formal-H200-A-r2-first-two-20261110/verification-commands.md). No substitute dataset, dependency, new reusable test, training entrypoint, or platform command was used.

| Execution | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| `timeout 60s systemd-run --user --scope -p MemoryMax=30G ...` readiness | Use user scope when supported | Exit1: `Failed to connect to bus: No such file or directory` | UNAVAILABLE; no inspection ran in this scope |
| `timeout 60s systemd-run --scope -p MemoryMax=30G ...` readiness | Use system scope when supported | Exit1: `Failed to start transient scope unit: Interactive authentication required.` | UNAVAILABLE; no auth/privilege operation attempted |
| Existing inspector + original-file rebuild + reporter | Prefix2, incomplete formal flags, exact original rebuild, unchanged hashes | Exit0; 3.173605169169605s; peak RSS39,708KiB; six inputs349,252,623 bytes unchanged | PASS |
| Streamed original bank/metric checks | Match UID/group/t_id/mask, compute actual errors/durations/all-sample versions | Exit0; 5.631639575585723s; peak RSS39,224KiB; required checks pass; unsupported slot0 comparison returns false and is separately corrected | PASS required checks; initial slot0 audit assumption FAILED |
| Focused generation provenance check | Find actual native receipt match, inspect retained scalar presence | Exit0; 2.4980510901659727s; peak RSS32,764KiB; unique slots119/118; current scalar absent in all512 retained bank samples | PASS |
| Final delivery/preservation check | Generated artifacts parse and reflect actual results; raw bytes/hash still unchanged | `delivery-verification.json` records exact final results | PASS when receipt verdict is PASS |

Each substantive Python inspection used `timeout 60s` and `resource.setrlimit(resource.RLIMIT_AS, (30*1024**3, 30*1024**3))` because systemd scope creation was unsupported without additional authentication. This is a **30GiB virtual-address-space limit**, not a claimed cgroup `MemoryMax` receipt. Measured RSS was below40MiB for the three substantive passes. No error was suppressed or converted into a training verdict.

## Completion checkpoint

[Local check-progress checkpoint](evidence/formal-H200-A-r2-first-two-20261110/scope-checkpoint.md): D1–D7 CLEAR; no scoped S1–S6 defect requiring edits. The shortest remaining local step is immutable delivery verification, then return these results to primary. Formal04/05/06 final acceptance and native memory/lifecycle remain unfinished outside this agent's ownership. The requirements/spec were reread for closure; science, soft gates, 200-update budget and independent-attempt boundaries remain unchanged.
