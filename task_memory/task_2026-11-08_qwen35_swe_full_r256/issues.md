## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record T03-DISPATCH-SNAPSHOT-RCA's proven mounts ownership failure and CPU-verified repair. |

# Issues

## T03-DISPATCH-SNAPSHOT-RCA — observer falsely reports configuration drift

**Status:** CPU repair verified; native GPU rerun and final acceptance remain with the primary.

**Observed native symptom:** `exp-1108-221044-294843` reported `ValueError: Training integration configuration changed after submission` at `watch_swe_evaluations.start_dispatch:355`, before watcher construction. The primary reported that native training continued. This agent did not inspect or control the live job.

**Proven local cause:** the submitter shared its parsed mounts list with `ResourceConfig`. The real native iterator appends `PUBLIC_MOUNT` to that same list. Boundary tracing found no difference after construction or before iteration, then mounts became the first and only differing field after iteration while file bytes/digest stayed unchanged. File-rewrite and pre-iterator-mutation hypotheses were falsified for the CPU reproduction.

**Repair:** construct the resource with `list(config["mounts"])` in `tests/manual/agent_opd/submit_swe_opd.py`. The reachable native iterator appends strings without mutating entries, so a shallow copy preserves all native mount behavior. The frozen-file equality check, diagnostic soft gate, and native training ACK remain unchanged.

**Regression gap closed:** the existing fast-test submitter seam now replays native mount-list normalization. Persistent tests cover empty/already-present public mount ownership and actual fixture-file drift. Real ResourceConfig CPU replay verifies the original-profile mount list still receives its public mount only in the resource, while the caller configuration stays untouched. Deliberate file drift still blocks the observer, logs the original error, and lets healthy fake training succeed.

**Evidence:** [test_report_2026-11-08_dispatch_snapshot.md](test_report_2026-11-08_dispatch_snapshot.md) contains exact commands, before/after boundary digests, expected RED failures, PASS counts, raw-log paths, and verification limits. No retry, flag, extra configuration snapshot, DeepSWE-specific workaround, profile change, or live-job operation was introduced.
