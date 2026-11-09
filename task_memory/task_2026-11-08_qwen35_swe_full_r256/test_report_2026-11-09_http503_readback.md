## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Classify retained HTTP503 evidence and correct the missing-timeout diagnosis using the actual SWE generation hook. |

# D13 HTTP503 and timeout readback

## Scope and environment

Read-only inspection of the completed D12 A/r256 experiment, local full student/teacher logs, and the actual SWE hook configuration. Local Python: `3.10.6`, GCC `11.3.0`. No GPU submission, remote worker mutation, profile change, or model request was made.

Sources: `/data/ycfeng/tmp/T02-ROUND-ROBIN-RCA/native-full-20261109/student.log` and `teacher.log`. Selected output: `/data/ycfeng/tmp/qwen35-swe-D13-http-status-signal-20261109.json`.

## Method and commands

The one-off local classifier streams both logs, matches HTTP access rows with the expression `"(GET|POST|PUT|DELETE) ([^ ]+) HTTP/[^\"]+" (\d{3})`, counts method/path/status, and separately collects numeric `token usage:` observations. It does not treat a configuration literal `0.8`, a line number503, or a completion length503 as an error.

The initial probe failed before execution with `SyntaxError: cannot assign to expression here` at an unused `start-ups=None` assignment. Removing that assignment produced the corrected output with exit0. The error remains in the session tool transcript; no failed probe output is claimed as evidence.

The result was checked with:

```bash
python3 - <<'PY'
import json,sys
from pathlib import Path
j=json.loads(Path('/data/ycfeng/tmp/qwen35-swe-D13-http-status-signal-20261109.json').read_text())
assert j['student']['generation_http503_count']==0
assert j['teacher']['generation_http503_count']==0
assert j['teacher']['http503_count']==58 and j['teacher']['non_health_http503_count']==0
assert j['teacher']['access_status_counts']['POST /generate 200']==227
assert j['teacher']['access_status_counts']['POST /generate 400']==2
print(sys.version)
print('HTTP_STATUS_CLASSIFICATION_PASS; no generation503 inferred from58 startup health503; access coverage limited')
PY
```

Expected: classify startup-health503 separately from generation responses. Actual: assertions passed, exit0, `HTTP_STATUS_CLASSIFICATION_PASS`.

## Observed results

| Observation | Student | Teacher |
| --- | ---: | ---: |
| Logged POST /generate200 rows | 175 | 227 |
| Logged POST /generate400 rows | 0 | 2 |
| Logged POST /generate503 rows | 0 | 0 |
| Logged non-health503 rows | 0 | 0 |
| Logged GET /health503 rows | 0 | 58 |
| Numeric token-usage observations | 563 | 2247 |
| Maximum logged token-usage value | 0.04 | 0.08 |

These are access-row counts, not unique sample counts. Student access coverage is less than the229 successful generation outcomes reconstructed from lifecycle payloads. No claim that every transport response was logged follows. The token-usage counter has not been independently equated with the user's prior80% KV-cache occupancy metric; it does not establish total physical cache occupancy.

The retained-log analyzer separately matched512 actual lifecycle payloads (256 starts/256 ends),229 successes/27 cancellations, four registered TP2 engines over GPU0–7, and27 abort RIDs on PID7177/GPU0,1. It established the two teacher400 responses as131070 input tokens exceeding the actual131066 request allowance. These findings remain in `evidence/deepswe-round-robin-rca.json` and `test_report_2026-11-09_round_robin_acquisition.md`; no teacher envelope was changed.

## Corrected timeout diagnosis

The raw low-level generation HTTP client has no read timeout and retries5xx up to60 times. That fact alone does not diagnose the configured SWE path.

`tests/manual/agent_opd/run_swe_opd.py:79` selects `tests.manual.agent_opd.qwen_alignment.generate`. That function at `qwen_alignment.py:96-97` already wraps the entire native single-turn generation/retry chain in `asyncio.wait_for(..., timeout=input.args.sglang_router_request_timeout_secs)`, including retry sleeps. D12's selected timeout is3600 seconds. Its independent bank deadline is1800 seconds and was observed to fire within0.0097 seconds of the target. Native cancellation produced all27 lifecycle cancellations and27 engine abort records.

The initial read-only timeout report omitted this custom hook. Primary withdrew the proposed shared `http_utils` timeout implementation before accepting any production edit, and redirected task `T02-D13-HTTP-TIMEOUT` to fault-injection verification of the existing mechanism. No additional timeout knob, second wrapper, shorter600/900-second limit, retry-count change, or sample refill is authorized by this readback.

## Verdict and limits

**PASS**: retained-log HTTP status classification and identification of the existing overall SWE generation deadline. **FAIL** remains the actual acquisition result227/256 below231, with0 updates and no student scoring.

Current captured evidence does not establish generation503/KV-pressure blockage as the D12 cause. The user's reported prior failure and conditional D13 authorization remain valid; a confirmed similar trigger and supported rollout-only topology are required before expansion. Timeout/cancellation fault-injection verification is pending. An extra8 GPUs in fully disaggregated mode would leave four engines, so it must not be presented as a measured serving-capacity increase.
