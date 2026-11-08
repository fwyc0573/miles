## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record exact-job terminal readback, failed D12 acquisition and independent baseline progress. |

# D12 and baseline runtime readback

## Commands and environment

- Platform: local personal-auth Python `/data/ycfeng/tmp/stepmind-env/bin/python -B`, Python3.10.6, `PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron`, `STEPMIND_BACKEND=rjob`, existing credential files privately inherited. Called `get_rjob_client().api.get_namespaced_custom_object(...,_request_timeout=20)` for exactly `exp-1109-010244-280221` and `exp-1108-215214-032806`. Outer command timeout65s; no submission or control call.
- Cloud: `timeout 60s ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng 'python3 -'` with scoped read-only Python programs. Read only the D12 student run's training/source-preflight files and the baseline point's state/results/failure filenames through `/mnt/ws-jfs/ycfeng`. Remote interpreter version was not captured in this readback; no environment change occurred.
- D12 cloud root: `/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/capacity-round-robin/r256/student/A/exp-1109-010244-280221`.
- Baseline cloud point: `/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/evaluations/points/original4b`.
- Exact executed Python programs are retained in the session tool transcript. Raw local outputs: `/data/ycfeng/tmp/qwen35-swe-round-robin-live-20261109.json`, `qwen35-swe-round-robin-acquisition-packet-20261109.json`, `qwen35-swe-original4b-progress-20261109.json`, `qwen35-swe-original4b-outcome-identities-20261109.json`. Selected platform output: `evidence/round-robin-and-baseline-platform-latest.json`.

## Observations

| Check | Expected / passing condition | Actual | Result |
| --- | --- | --- | --- |
| Exact identity and source | Personal creator, current local NFS and expected GPU roles | Both jobs match; D128+2,baseline2,all non-preemptible | PASS |
| D12 acquisition | At least231/256 valid under1800s |227 valid,2 HTTP400 outcomes,27 collector-pending; ended1800.0097s after start | FAIL |
| D12 platform terminal | Explain failed critical task without assuming manual stop | Student failed; teacher system-stopped; `Some critical tasks failed.`,finish17:42:57UTC | FAIL, attributed to acquisition exception |
| D12 sourcepatch capacity | Actual scoring,backward,two ACKs and next scoring | Dependency preflight applied patch; acquisition failed before these stages | NOT TESTED |
| Baseline completeness |400 completed outcomes before reporting avg@4 |8 completed,4 true/4 false,392 missing; no failure files | NOT COMPLETE |
| Baseline deadline | Original72h interval unchanged |1794146471.7061195→1794405671.7061195,exactly259200s | PASS |
| Healthy baseline | Independent evaluation keeps running | Exact platform Running on2 H200 | IN PROGRESS |

The27 pending slots are collector observations; detailed generation/teacher classification and actual resolved router/queue evidence belong to the scoped offline RCA. The teacher HTTP400 responses are genuine losses,not a reason to reroll a model outcome or relax the minimum. Even recovering only those two slots would yield229,still below231.

## Limits and next action

D12's approval covers one experiment,now concluded unsuccessfully. No further GPU run,concurrency/graph/deadline/threshold change or formal-profile change was made. Router effect and uniqueness of the remaining bottleneck are not proven by the227 total. Independent source-lifetime capacity remains unverified. The baseline's4 false outcomes are completed model outcomes,not infrastructure-missing slots; the full score remains unavailable. Captured files and retained HFs/results are preserved. Continue read-only RCA and baseline monitoring; prepare a concrete approval request only after the remaining cause is narrowed.
