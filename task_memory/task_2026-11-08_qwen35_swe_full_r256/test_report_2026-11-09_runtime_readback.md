## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Collect full source-derived teacher/student logs and verify retained sampling metadata across184 shared valid UIDs. |
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

## Retained evidence follow-up

Downloaded complete existing logs with `timeout 60s ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng 'cat <exact-path>'`, using `set -C` and `umask 077` for new local files. No GPU job or remote write was created:

- Student source: `/mnt/ws-jfs/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/capacity-round-robin/r256/student/A/exp-1109-010244-280221.log`.
- Teacher source: `/mnt/ws-jfs/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/capacity-round-robin/r256/teacher/A/exp-1109-010244-280221/rank-0.log`. This follows `qwen35_pair_worker.py:218`, the protocol runtime root and the actual `teacher-ready.json`; it is not an inferred filename. The receipt binds the same job/pair/rank, two H200 GPUs, approved image and Qwen27B source.
- Local files: `/data/ycfeng/tmp/T02-ROUND-ROBIN-RCA/native-full-20261109/student.log` and `teacher.log`. Detailed log inspection belongs to the resumed local-only RCA agent.

The same bounded read-only SSH command streamed the two original bank JSONLs and extracted only requested probability/seed/completion and weight-version fields. The first collector failed on an actual null sample with `AttributeError: 'NoneType' object has no attribute 'get'`; the corrected collector explicitly records null samples and writes a separate `sampling-weight-metadata-20261109-v2.json`. It does not substitute a sample or change a slot result.

Local Python3.10.6 compared valid samples by source UID: new227, old206, shared184. Probability definitions, seed, maximum response budget and maximum sequence length have zero shared-UID mismatches. All observed output/prefill spans have version label0; all retained request seeds are1729. Completion hashes match70 and differ114. Expected identity/metadata consistency: PASS. Equal metadata does not establish equal weight bytes, bitwise inference or a causal routing-only throughput delta. No numerical or concurrency-safety verdict follows. Summary: `evidence/deepswe-round-robin-sampling-metadata.json`; original bank paths and raw capture are recorded there.

The independent baseline readback at1794162993.5202243 finds9 completed outcomes (4 true,5 false),391 missing,no infrastructure failure files and statusRUNNING. The original first start/deadline remain unchanged. Full-score acceptance is still NOT COMPLETE. Raw follow-up:`/data/ycfeng/tmp/qwen35-swe-original4b-progress-20261109-followup.json`; this advances the earlier8-result observation,which remains retained.
