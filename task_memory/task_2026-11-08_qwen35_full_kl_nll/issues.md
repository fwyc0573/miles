## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record the r2 platform audit-read coverage gap separately from the confirmed capture failure. |

# Evidence gaps

## r2 all-operation audit reads — OPEN coverage gap

The A/B r2 RJob and replica audit reads each returned `ok: false` after a 12-second `ReadTimeout`. Live and historical events, incident logs, and existing DeepScan reads succeeded. The retained audit failures are not empty audit results and do not prove the absence of external actions or identify an external actor.

The independently bound terminal receipts confirm both jobs failed with container `Error`, exit code 1, and zero restarts. The application capture/readback failure is observed before terminal completion. Missing audit coverage does not invalidate those observations and does not block the independent CPU metadata diagnosis. No repeated audit-query loop, new GPU submission, or platform control action is authorized by this gap.

Evidence: [platform failure report](test_report_2026-11-11_kv_coherence_r2_platform_failure.md), [A query summary](evidence/teacher-scoring-kv-coherence-probe-20261111/platform-rca-r2/A/query-summary.json), and [B query summary](evidence/teacher-scoring-kv-coherence-probe-20261111/platform-rca-r2/B/query-summary.json). Capture RCA is maintained separately in [the diagnosis report](evidence/kv-coherence-batch-metadata-rca-20261111/rca.md).
