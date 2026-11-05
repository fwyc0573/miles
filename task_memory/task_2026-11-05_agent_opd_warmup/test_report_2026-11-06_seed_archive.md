## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Verify immediate closed-seed archival and local evidence preservation on I/O failure. |

# Native benchmark seed archival

The native benchmark previously archived all logs and trajectories after every seed finished. Two observed invalid grades could not be diagnosed while their healthy sibling seeds continued. `tests/manual/agent_opd/rjob_benchmark.py` now archives each completed seed's closed native log and work directory to the existing personal `diagnostics` path, then removes that seed's worker-local files. The final archive merges the remaining server output after shutdown. Source files remain available if an archive copy fails; the I/O error propagates.

## Verification

The candidate source passed four direct function cases before being applied to the live mounted checkout. The exact applied source then passed these checks:

```text
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron \
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
-q -p no:cacheprovider \
--basetemp=/data/ycfeng/tmp/agent-opd-learning-20261105/pytest-archive-20261106a \
tests/fast/test_agent_opd_benchmark_archive.py tests/fast/test_agent_opd_export.py
```

Environment: Python3.12.13, pytest9.1.1, existing mounted CPU virtualenv. Actual result:10passed in1.29seconds; three existing deprecation warnings.

| Scenario | Passing condition | Actual result |
| --- | --- | --- |
| Completed seed, native exit0 | Closed native log and error trajectory available in canonical cloud destination; completed local files consumed; active sibling/server files preserved | PASS |
| Completed seed, native exit1 | Same archive/cleanup behavior and original native exit code returned | PASS |
| Injected archive EIO | Error propagates; original local native log/trajectory and active sibling/server files remain available | PASS |
| Final archive merge | Previously archived seed evidence remains and server output is added | PASS |
| Existing HF export qualification | Six decoder/index/MTP identity regressions remain passing | PASS |

The native subprocess and cloud destination are simulated filesystem operations in these CPU checks. Real early archival by a new GPU worker remains to be observed. Existing workers retain their previously loaded implementation; source questions2/5 therefore still require their normal final archive. Both invalid samples are explicitly held from raw consumption.

Consumed temporary qualification artifacts: 55files/25230bytes; exact candidate and pytest temporary directory absent. Persistent regression source: `tests/fast/test_agent_opd_benchmark_archive.py`. No additional GPU request was created for this change.
