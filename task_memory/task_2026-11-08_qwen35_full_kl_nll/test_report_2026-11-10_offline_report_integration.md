## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Close the remaining prefix-zero cause-retention finding at219489ef after12 affected checks and final Spec re-review. |
| 2026-11-10 | Repeat all four joined CLI cases after review repairs and apply the combined tools to the actual one-update H200 attempt. |
| 2026-11-10 | Join the independently delivered inspector and reporter through the actual CLI; verify complete, partial and retained failed-attempt dispositions. |

# Offline inspection and report CLI integration

The primary initially joined inspector`a76fc527`and reporter`e6956e3c`, then rechecked repaired inspector`24e8386f`and reporter`d0f67887`. These are planned CPU deliverables for04/05 inspection and06 reporting. The CPU cases below do not close06; actual first-update evidence is separately linked at the end.

## Environment and commands

Repository:`/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`; Python`/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`3.12.13. Set`PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp`. No dependency installation or runtime code change.

Reuse the retained fixture `tests.fast.test_distillation_run_inspection._run(case_dir, count=N)` and its `JOB` constant. Create independent case directories beneath `/data/ycfeng/tmp/agent-opd-image/joined-profile-report-20261110/`. Use N=4 for hand-computed values and N=200 for complete and partial synthetic cases. For the partial case only, retain the first complete line of the fixture's`distillation_profile/observations.jsonl`and append the incomplete bytes`{"update_id":2,"rows":`; the untouched native fixture still contains200 successful ACKs. No real source/terminal evidence is modified.

For each case run the actual joined CLI:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.distillation_report \
  --training-dir "$TRAINING" --job "$JOB" --cell "$CELL" --expected-updates 200 \
  --terminal-path "$TERMINAL" --output-prefix "$CASE/report"
```

The three synthetic cells are explicitly named`SYNTHETIC CPU / <case>`. The retained failure uses job`exp-1110-014836-849060`, its unchanged`evidence/admission-formal-A-20261110.terminal.json`, and the missing local training path listed in the inspector's report. All exact expanded command arrays, output paths and dispositions are retained in`evidence/offline-report-join-20261110.json`; raw generated JSON/Markdown and fixtures remain under the temporary root above.

## Expectations and observations

| Case | Passing condition | Observed | Verdict |
| --- | --- | --- | --- |
| Hand-computed4-update fixture | Rebuild and historical ratio use fixed baseline; expected200 remains incomplete | Baseline0.59375; update1 RKL0.75/NLL1; gap`0.75/0.59375`; earliest best update2; prefix4; INCOMPLETE | PASS |
| Synthetic200-update fixture | All six S9 milestones and both completion flags agree | Prefix200; all milestones RKL1/NLL2/gap1; native/profile/overall COMPLETE, explicitly synthetic | PASS |
| Synthetic native200 with partial profile | Preserve native completion but reject complete profile and partial-state ratios | Native COMPLETE; profile/overall INCOMPLETE; verified prefix1; unverified2–200; baseline null | PASS |
| Retained failed H800 attempt | Keep actual terminal failure and absent local data distinct | Terminal Failed; observed ACKs0; actual count null; prefix0; all RKL milestones null; overall INCOMPLETE | PASS |

All four subprocesses exited0 and produced both JSON and readable Markdown. The original real terminal receipt remained byte-identical. Normal exits for incomplete evidence are intentional: the offline tools cannot control the training job.

## Verification limits

- Inspector tests reported57 PASS and reporter/profile tests26 PASS; this primary check runs the combined CLI instead of repeating those suites.
- Missing local records do not prove zero actual updates; the historical task's zero-update diagnosis comes from its independent startup failure evidence.
- Synthetic COMPLETE is only a CPU test result. No real A/B per-turn values, stage timings, model checksums or native SWE task identities are supplied here.
- Actual first-update/D16 and final200-update acceptance still require the corresponding job's native records, canonical banks, terminal evidence and paired profile files. Review of the new offline code is recorded separately.

## Review repairs and repeated joint verification

The four functional findings were fixed: portable temporary-directory selection and failure isolation; retaining an adjacent native auxiliary error after profile stops; rejecting complete-profile status with an extra unverified native tail; and determining observed milestones from actual successful update IDs. The naming Nit was also corrected. Inspector`24e8386f`records69 selected PASS; reporter`d0f67887`records27 report/profile PASS, with RED/GREEN evidence in their existing reports.

The primary repeated the exact four original CLI command arrays using new `report-review-fixed` output prefixes, preserving the original reports. All four dispositions and verified-prefix lengths remained correct, and each output supplied the mandatory `native.observed_successful_update_ids` list. Exact expanded commands and results are in[evidence/offline-report-join-review-fixed-20261110.json](evidence/offline-report-join-review-fixed-20261110.json). PASS:4/4. Standards re-review closed both findings. Spec re-review identified one remaining prefix-zero cause-retention case, fixed at`219489ef`:3 RED→3 GREEN and12 affected tests PASS in0.92s. Final read-only Spec review closed it with no findings. No redundant full-suite rerun was required; the additional change preserves API/schema and all zero-prefix measurements remain unverified.

The combined CLI was also applied to the actual H200 A snapshot. It reported native Failed with one observed/verified update, profile prefix1, and overall INCOMPLETE for expected200. Canonical256-turn identity,37,628 tokens and exact paired rebuild passed. This is actual evidence described in[the D16 report](test_report_2026-11-10_d16_first_update.md), not part of the synthetic CPU totals above; it does not convert the failed1/200 attempt into a completed formal run.

After219489ef the primary also ran the actual combined CLI on two newly generated synthetic cases: first ACK auxiliary failure with empty profile files, and with missing profile files. Both return native COMPLETE for the fixture's one-update budget, profile/overall INCOMPLETE, zero verified prefix and null derived metrics. The concrete cause appears in both JSON and Markdown. Exact commands, interpreter, outcomes and macro values are in[evidence/offline-report-prefix-zero-20261110.json](evidence/offline-report-prefix-zero-20261110.json). PASS:2/2. This targeted check settles the repaired cross-module edge and does not repeat the broader suites.
