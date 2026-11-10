# Distillation profile report: A/full

- Job: `exp-1110-165312-132926`
- Expected successful updates: 200
- Report disposition: **INCOMPLETE**

## Native training and profile verification

| Evidence | Disposition | Progress / terminal evidence | Error |
| --- | --- | --- | --- |
| Native training | INCOMPLETE | Observed successful updates: 2; verified native counter: 2; terminal phase: null | No terminal receipt supplied; native completion is unverified |
| Profile | INCOMPLETE / UNVERIFIED | Verified prefix: 2; first unverified update: 3; unverified ranges: [[3, 200]] | Verified profile prefix ends at 2; expected 200 updates |

## Inspected paths

- training_dir: `task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/formal-H200-A-r2-first-two-20261110/training`
- profile_dir: `task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/formal-H200-A-r2-first-two-20261110/training/distillation_profile`
- terminal: `null`

## Macro values

Scope: verified prefix through update 2; not any later native updates.
Estimator: `sampled_current_student_minus_frozen_teacher_on_original_behavior_tokens`; baseline updates B=10; conversation baseline turns N=8; default k=10.
Macro baseline: null (INCOMPLETE). A missing or nonpositive baseline leaves dependent ratios, trend and recovery null.

| Update | Verification | RKL | Student NLL | Remaining gap |
| --- | --- | --- | --- | --- |
| 1 | VERIFIED | 0.090507041 | 0.55819255 | null |
| 10 | NOT_OBSERVED | null | null | null |
| 50 | NOT_OBSERVED | null | null | null |
| 100 | NOT_OBSERVED | null | null | null |
| 150 | NOT_OBSERVED | null | null | null |
| 200 | NOT_OBSERVED | null | null | null |

- RKL-best (earliest tie): {"update_id": 1, "rkl": 0.09050704144033206, "nll": 0.5581925452041884}
- Latest verified values: {"update_id": 2, "rkl": 0.11235144949131297, "nll": 0.7886505394118376, "tokens": 184306, "turns": 256, "conversations": 32, "remaining_gap": null}
- Default-k RKL trend (positive means RKL decreased): null
- Recovery gap: null

## Conversation statistics

Scope: each conversation's latest entry within the verified prefix through update 2; profile available: True. These are not counts for unverified later training.

- seen: 32
- alive: 32
- positive_baseline: 32
- nonpositive_baseline: 0
- defined_trend: 0
- incomplete_baseline: 0

Equal weight per conversation; exclude None, never replace it with zero. Sort the n defined values; for probability p use h=(n-1)*p and linearly interpolate between floor(h) and ceil(h). One defined value supplies every quantile; no defined values gives null quantiles.

| Quantity | Defined | Undefined | p10 | p25 | p50 | p75 | p90 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| remaining_gap | 32 | 0 | 0.83473319 | 0.98068001 | 1.3357072 | 1.649296 | 1.8870013 |
| run_relative_gap | 0 | 32 | null | null | null | null | null |
| rkl_trend | 0 | 32 | null | null | null | null | null |
| recovery_gap | 32 | 0 | 0 | 0 | 0.33570718 | 0.64929602 | 0.8870013 |

## Limitations

- Actual exact retained corrected-A snapshots through successful update 2, captured 2026-11-10T09:54:56.550810+00:00; not synthetic.
- Expected formal budget remains 200. Training was active at retention; no terminal receipt is supplied, so no terminal success or native offload repair verdict is claimed.
- Historical failed A exp-1110-140032-491115 (1/200) is independent and is not joined to this attempt.
- All metrics describe the verified profile prefix, not any later unverified native updates. Unavailable milestones remain null; they are never extrapolated or filled from partial records.
- RKL-best is the earliest minimum RKL, with NLL at that same update. NLL has no independent best, trend or recovery statistic.
- Conversation distributions use each conversation's own latest entry. These entries can have different measurement updates; trend uses the latest reference at least k updates earlier.
- Full-mode measurements mix training progress with turn position and actual turn/token membership. Later conversations measure their own baseline on a student trained longer.
- Remaining gap is an RKL-to-baseline ratio, not the fraction still reducible. Model size alone does not prove a strictly positive minimum RKL.
- Normalized gaps establish neither causal nor rank comparisons across teachers, models or runs. This report performs no benchmark evaluation.
- The report does not independently verify source SWE instance/repository identity, exact-text proxy coverage or seed count. Consult the attempt's source and configuration evidence.
