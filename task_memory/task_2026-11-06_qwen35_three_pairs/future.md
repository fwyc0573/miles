## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Park the unselected rematerialization repair and superseded kernel-only diagnostic without blocking the approved normal-backup runs. |

# Deferred work

- **Optional rematerialized publication:** D16 selects more host memory instead. Before future enablement, obtain scope approval and revisit the failure window, owner-controlled residency and GPU-peak requirements in [the C host-memory report](test_report_2026-11-07_C_host_memory.md). No implementation is planned for the current formal runs.
- **Kernel-only uniform-score diagnostic:** keep the exploratory [probe report](test_report_2026-11-07_uniform_scores_probe.md) as incomplete historical evidence. The observed problem predates fused and has an independently reproduced restoration cause. Do not spend more GPU work on this diagnostic absent a new arithmetic failure.
