## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Observe actual per-seed cloud archival while three sibling generators remain running. |
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

The native subprocess and cloud destination are simulated filesystem operations in the CPU checks. Real early archival is now observed in the production worker below. Existing workers retained their earlier loaded implementation; question2 has since produced its normal final archive and is undergoing unchanged-patch native regrading, while question5 still waits for that archive. Both invalid sources remain explicitly held from raw consumption.

Consumed temporary qualification artifacts: 55files/25230bytes; exact candidate and pytest temporary directory absent. Persistent regression source: `tests/fast/test_agent_opd_benchmark_archive.py`. No additional GPU request was created for this change.


## Actual production observation (2026-11-06T06:41:40.928585+08:00)

PASS for early native archival in `exp-1106-022355-390181`,UID`d89a55d9-8d34-47b7-93da-d109b01bb704`,node0507. The verified worker started05:57:19HKT after the archive repair and loaded the exact update20HF/version. Question14 `django__django-14053`,seed1732 completed79 verified model requests in2166.726seconds; native grading took35.870seconds and returned resolved=true. Source seeds1729,1730 and1731 were independently observedgeneration running,with no grading records. The whole-job pipeline-exits marker was absent.

At that same observation, `diagnostics/native-20-1732.log` and the canonical `diagnostics/step20/seed-1732` directory were already present. The latter contained the19693-byte native check_result,517827-byte trajectory,656221-byte native log and1243-byte check log. This verifies closed-seed evidence becomes available before its three sibling generators finish. Native signals were79 assistant/thinking turns,7body turns,60bash calls,17str_replace_editor calls,2submit calls and79tool responses.

Read-only verification used bounded SSH as i-fengyicheng and Python pathlib/json over the exact personal cloud job root. No new inference request or GPU allocation was needed. Worker-local file removal was not independently inspected because native Pod access is forbidden by the personal API; the qualified CPU checks verify that operation's implementation. This observation does not mark the complete eighty-attempt benchmark or final cleanup complete.
