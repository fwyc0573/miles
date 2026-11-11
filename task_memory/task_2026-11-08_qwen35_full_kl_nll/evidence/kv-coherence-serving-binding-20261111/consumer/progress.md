## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Close final focused tests, Python 3.10 source-scope checks, and selected consumer evidence. |
| 2026-11-11 | Record the consumer-only serving binding gate and first affected CPU verification. |

# Consumer progress

TaskID: `profile-kv-coherence-serving-binding-consumer-20261111`.

Scope: only `tests/manual/agent_opd/probe_teacher_scoring.py`, `tests/fast/test_teacher_scoring_probe.py`, and new evidence in this consumer directory. Producer, platform, authentication, GPU, native build, delegation, staging, commits, configuration, raw runs, and parent documentation are outside this assignment.

- completed: pass the unchanged prepared `native_observer` receipt to the existing parent metadata helper only when capture is enabled.
- completed: compare post-all16 serving module path/SHA, capture PID, exact class/factory booleans, and required null `binding_error` before accepting summaries. Missing expected evidence fails; no staged-byte or CPU-library fallback.
- completed: initial `metadata_only` readback remains ungated; false/absent selection has no binding checks or coherence preparer imports. Scoring, payload, argv, flushes, and existing independent gates are unchanged.
- completed: first affected CPU run: **38 PASS, 0 SKIP, 211 deselected, 3.11s**. Expected/actual binding cases are synthetic schema fixtures, not native identity evidence.
- completed: final focused config/preparer/structural regressions: **83 PASS, 0 SKIP, 166 deselected, 6.05s**; no broad producer/full-join run.
- completed: Python 3.10.6 AST parsing/compilation and whole-source scope comparison PASS. After removing only the permitted optional receipt argument, its enabled main option, the one drain-branch call, and the new gate function, the source AST exactly equals baseline `71c3560b`.
- completed: scoped whitespace check, frozen `consumer.diff`, source checksums in `scope.json`, and final pytest log/XML. See [test report](test_report_2026-11-11_consumer_serving_binding.md) and [checkpoint](checkpoint.md).

First command, repository-root working directory:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/fast/test_teacher_scoring_probe.py -k 'coherence_serving_binding or coherence_true_only or kv_stream_witness_api_binding'
```

Environment observed: Python 3.12.13 at `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, pytest 9.1.1; system `/usr/bin/python3` is Python 3.10.6. Existing SWIG and `datetime.utcnow()` deprecation warnings are outside the changed scope. All post-loop auxiliary failures tested retain every score file and exact original readback; numerical acceptance remains null. Producer integration and actual private native-library/CUDA evidence remain pending under the primary's ownership.
