## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record D12 teacher admission mismatch, verify the existing generation deadline, and close the accepted T03 dispatch issues. |
| 2026-11-08 | Append T03-DISPATCH-PERMISSIONS's worker-first base ownership failure, local ordering repair, and CPU verification limits. |
| 2026-11-08 | Record T03-DISPATCH-SNAPSHOT-RCA's proven mounts ownership failure and CPU-verified repair. |

# Issues

## T02-D12-TEACHER-INPUT — canonical input exceeds native admission limit

**Status:** diagnosed from retained logs; serving-envelope compatibility remains unresolved and unapproved.

Two inputs at slots58/150 have131070 tokens and receive HTTP400 because the native maximum is131066,despite configured context131072. The source-derived teacher identity and literal diagnostics are retained in `test_report_2026-11-09_round_robin_acquisition.md:193-210`. Why the guard reserves six tokens requires source inspection; raw HTTP response bytes were not logged. The206-second second rejection includes queue delay and must not be treated as GPU scoring time. Fixing both would still leave229<231.

Preserve every canonical token. Do not enable auto-truncation,reduce the training128K budget,or change the teacher serving envelope without a supported compatibility proposal and approval. This is separate from the27 generation requests stranded on one engine.

## T02-D13-HTTP-TIMEOUT — existing total deadline verified

**Status:** no current generation-guard defect reproduced; test-only verification complete.

The selected `qwen_alignment.generate` wraps the entire native retry coroutine with the existing3600-second deadline. The independent bank1800-second deadline also operates. A low-level read timeout ofNone is not evidence that this configured path is unbounded. Repeated503,typed recipe transport and cancellation tests pass; guard-bypass negative control fails as expected. No production timeout layer or profile change was added. See `test_report_2026-11-09_generation_http_timeout.md` for93+8 regression passes,primary5-case rerun and limits. Captured503s are teacher startup-health requests,not demonstrated generationKV-pressure failures.

## T03-DISPATCH-SNAPSHOT-RCA — observer falsely reports configuration drift

**Status:** resolved; CPU repair and subsequent native asynchronous isolation accepted in49aa6f8b. Historical review limits below describe the original CPU scope.

**Observed native symptom:** `exp-1108-221044-294843` reported `ValueError: Training integration configuration changed after submission` at `watch_swe_evaluations.start_dispatch:355`, before watcher construction. The primary reported that native training continued. This agent did not inspect or control the live job.

**Proven local cause:** the submitter shared its parsed mounts list with `ResourceConfig`. The real native iterator appends `PUBLIC_MOUNT` to that same list. Boundary tracing found no difference after construction or before iteration, then mounts became the first and only differing field after iteration while file bytes/digest stayed unchanged. File-rewrite and pre-iterator-mutation hypotheses were falsified for the CPU reproduction.

**Repair:** construct the resource with `list(config["mounts"])` in `tests/manual/agent_opd/submit_swe_opd.py`. The reachable native iterator appends strings without mutating entries, so a shallow copy preserves all native mount behavior. The frozen-file equality check, diagnostic soft gate, and native training ACK remain unchanged.

**Regression gap closed:** the existing fast-test submitter seam now replays native mount-list normalization. Persistent tests cover empty/already-present public mount ownership and actual fixture-file drift. Real ResourceConfig CPU replay verifies the original-profile mount list still receives its public mount only in the resource, while the caller configuration stays untouched. Deliberate file drift still blocks the observer, logs the original error, and lets healthy fake training succeed.

**Evidence:** [test_report_2026-11-08_dispatch_snapshot.md](test_report_2026-11-08_dispatch_snapshot.md) contains exact commands, before/after boundary digests, expected RED failures, PASS counts, raw-log paths, and verification limits. No retry, flag, extra configuration snapshot, DeepSWE-specific workaround, profile change, or live-job operation was introduced.

## T03-DISPATCH-PERMISSIONS — worker-created base prevents local observer initialization

**Status:** resolved; directory preparation and native async acceptance verified in49aa6f8b. The earlier mounts alias repair was preserved; original CPU evidence remains below.

**Observed native symptom:** after the alias fix, `exp-1108-224927-865957` fails in `EvaluationWatcher.__init__ → _publish_once → _locked → path.parent.mkdir` with errno13, before any evaluator/fault. The primary reports healthy native training completion. Supplied pre-repair metadata identifies a writable local evidence parent but a dispatch base and job artifacts created by UID/GID0, while the submitter is UID/GID10250.

**Cause and discriminator:** the submitter previously waited until a real job existed before creating observer transport. A worker could become the first creator of the shared dispatch base after a prior observer failure. The deterministic CPU loop reproduces the constructor errno13 while preserving training ACK/configuration bytes. After the ranked hypotheses were shown, the single-variable local-precreation probe removes the failure and allows real constructor/identity/watcher-lock creation by the current user.

**Repair:** `watch_swe_evaluations.prepare_dispatch` validates the existing local dispatch/configuration scope and creates only the configured base. `submit_swe_opd.main` calls it after successful admission but before native backend submission. Preparation exceptions are logged soft gates, never training blockers. No-evaluation, dry-run, denied-admission, immutable-file comparisons, mounts ownership, and native training/observer drain behavior are preserved.

**Limits:** this code does not repair any existing owner/mode or old child artifact; no permission command was executed by this agent. CPU publication/API/worker fakes do not certify native asynchronous evaluation or a distinct-UID same-job startup race. The primary owns native acceptance and any existing-base remediation.

**Evidence:** [test_report_2026-11-08_dispatch_permissions.md](test_report_2026-11-08_dispatch_permissions.md) owns the exact RED/GREEN commands, single-variable result, focused/full/alias regression counts, directory/lock readiness checks, and scope limits.
