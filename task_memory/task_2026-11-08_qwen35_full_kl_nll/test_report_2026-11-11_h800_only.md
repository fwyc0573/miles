## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Pair all512 native generation events with256 teacher requests; distinguish overlapping stage duration from the observed deadline-critical teacher backlog. |
| 2026-11-11 | Record the H800-only directive, H200 terminal evidence, server-side teacher queue backlog, and unchanged candidate-selection policy before fresh H800 execution. |

# H800-only execution and preceding H200 terminal evidence

## Scope

The user directed subsequent execution in this session to H800 GPUs only, with no GPU-count limit. Formal roles remain non-preemptible on `codesign`. No H200 job may be submitted or resumed. The existing scientific inputs, length budgets, 200-successful-update target, 231-valid-turn minimum within 1800 seconds, and soft auxiliary gates remain unchanged.

The proposed oversampling question is not approval to change the fixed candidate count or select training samples by completion time. No oversampling implementation or configuration change has been made.

## Preceding H200 attempt: observed terminal state

Job: `exp-1110-165312-132926`, the independent corrected A/full attempt.

The local personal Python client read the exact RJob CR and every replica through `get_rjob_client()`, `client.api.get_namespaced_custom_object(...)`, `get_rjob_infos(name)`, and `client._get_replica_kapis(replica_name)`. The creator was asserted to be `i-fengyicheng` before archiving filtered fields. The client environment used `/data/ycfeng/tmp/stepmind-env/bin/python` (Python 3.10.6), handbook proxy configuration, personal credentials from permission-restricted files, `STEPMIND_BACKEND=rjob`, and `PYTHONPATH=/data/ycfeng/steptron`.

Evidence:

- [Filtered platform and replica readback](evidence/h200-before-h800-only-20261111.json).
- [Native successful ACKs and retained failure tail](evidence/h200-final-native-before-h800-only-20261111.json).
- [Failed bank6 acquisition and teacher-stage records](evidence/h200-bank6-stage-evidence-20261111.json).

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| No continuing task-owned H200 execution | All replicas terminal before H800 continuation | RJob Failed; student rank0 Failed; other student and teacher Stopped | PASS |
| Creator | `i-fengyicheng` | Exact match | PASS |
| Existing attempt remains independent | No joining counters with new H800 attempts | Successful native update IDs `[1,2,3,4,5,6]` retained under the H200 job identity | PASS |
| Formal completion | 200 successful updates and accepted terminal result | 6/200, platform finish `2026-11-10T12:51:43Z` | FAIL / INCOMPLETE |
| Seventh bank acquisition | At least 231 valid turns within 1800 seconds | 225 valid, 31 pending; observed closure after 1800.025831 seconds | FAIL |

All six native ACKs report zero optimizer skips and verified turn sums. Updates1–5 contain256 turns each; update6 contains242 turns. This is native receipt evidence, not independent canonical/profile acceptance of all six updates. Detailed canonical/profile acceptance currently covers updates1/2 only.

No stop was issued: the H200 job had already ended before this readback. The final failure is an acquisition-throughput failure, not a recurrence of the earlier post-update host-memory failure. The previously verified train/offload/sync/restore/next-train cycle remains accepted within its observed scope; the historical full-model allocation owner remains unproven.

## Seventh-bank stage evidence

All31 pending slots had a `teacher_request` start before the deadline. Those starts occurred886.309545–1150.890934 seconds after acquisition began. Teacher request end records comprise225 successes and31 cancellations. For the225 successful requests, median elapsed time was411.105525 seconds and maximum909.323159 seconds; median total input length was98,050 tokens and maximum116,053 tokens.

The retained [teacher service tail](evidence/formal-h200-112k-20261110/full/exp-1110-165312-132926/A/teacher-tail-0.log) confirms the queue backlog before the deadline. At12:50:41Z the service reports one new sequence,8192 new tokens,0 cached tokens,30 queued requests,2,903,977 pending tokens, and input throughput12,681.07 tokens/s. At12:50:42Z it reports30 queued requests and2,895,785 pending tokens. Client disconnect/abort messages then appear as the acquisition deadline cancels pending requests. These errors are downstream of cancellation, not evidence of the initiating failure.

The `teacher_request` start in `swe_replay.py:254–267` is recorded before the HTTP request; it does not prove scheduler admission or the beginning of GPU computation. The exact worker command preserves `--max-running-requests 1` and an8192-token prefill chunk. `_score_payload` in `miles/rollout/on_policy_distillation.py:95–123` sends the complete prompt plus generated answer, with `max_new_tokens=0`, `return_logprob=true`, and `logprob_start_len=0`. Thus scoring still performs long-input processing; it is not a second teacher generation, nor a constant-time lookup after student generation.

These request intervals include service/queue latency; they do not measure isolated teacher GPU compute time. Queue backlog is directly observed, but the records do not give a complete per-request queue/compute breakdown or predict H800 throughput. H800's existing teacher TP4 allocation differs from the failed H200 TP2 allocation and still requires native throughput evidence. No claim of a completed throughput fix is made before that native run.

## Native generation/teacher timeline: addressing the rollout-tail hypothesis

The user challenged whether individual student generation requests, rather than teacher scoring, held up the flow. New submission is paused while this attribution is checked; CPU H800 configuration preparation remains independent.

The primary streamed the exact job's retained student and teacher logs over the permitted read-only SSH route, selecting bank6 sample indices and its time window. The source student log is11,682,226 bytes and teacher log3,743,285 bytes. [Native stage events and teacher window](evidence/h200-bank6-native-stage-timeline-20261111.json) retain512 matched `QWEN35_SAMPLE_ATTEMPT` generation start/end records and the relevant teacher log window. [Computed attribution](evidence/h200-bank6-stage-attribution-20261111.json) records the checks and measurements.

All256 generation attempts ended `succeeded`. Every sample index matches a teacher-request start, with a0.000587–0.010996-second generation-end-to-teacher-start gap. The generation adapter finishes before reward/teacher scoring in `inference_rollout_common.py:98–150`; the selected `swe_replay.score_teacher` path does not call the separate student-prefill observer used by `qwen_alignment.score_teacher`.

| Seconds since acquisition start | Student generations completed | Teacher requests successfully returned |
| --- | ---: | ---: |
| 300 | 38 | 17 |
| 600 | 120 | 61 |
| 900 | 227 | 101 |
| 1200 | 256 | 142 |
| 1500 | 256 | 186 |
| 1799 | 256 | 225 |

Actual native generation completion times: median616.748195 seconds, P90 approximately925.128644 seconds,231st completion930.218728 seconds, and last completion1150.889550 seconds. The time from the last student completion to the acquisition deadline was649.136281 seconds. This interval contains no remaining student-generation attempts for this bank.

Teacher prefill is visible from approximately194.674074 to1799.674074 seconds. Within the pre-deadline window,2735 prefill log rows report21,561,962 new tokens,0 cached tokens, exactly1 new sequence per logged prefill batch, and a peak queue length of128. The256 teacher inputs total24,457,747 tokens. These are logged-work counts, not hardware kernel timing or a complete probability/transfer/JSON cost decomposition. Response lengths have median195 tokens, P90 of1223 tokens, and maximum8124 tokens; the large teacher load is predominantly the supplied long context rather than a need to generate new answers.

The observed failure is therefore not a wait for a handful of unfinished student services at the deadline. Student generation itself is substantial and overlaps teacher processing; the two stage durations must not be added or ranked solely by separate averages. The decisive observation is that all student outputs existed around1151 seconds, while the teacher still had only225 valid completions at1800 seconds. A hypothetical instantaneous teacher applied to the same generated outputs would meet both the231 and256 count targets before the deadline, although this is a timing counterfactual and not a GPU throughput measurement.

Oversampling could change which workloads are admitted and favor shorter/faster samples; it has not been tested and cannot be declared universally ineffective. It does not address an observed unfinished-student tail in this bank, because none remained. Its proposed selection policy is still a separate experimental decision.

## Current candidate-selection behavior

Inspected paths:

- `tests/manual/agent_opd/swe_replay.py:398–419`: draw exactly `swe_bank_slots` candidates (256), reject a different count, and invoke the acquisition owner.
- `tests/manual/agent_opd/swe_replay.py:152–230`: submit one asynchronous task per candidate, wait until all tasks return or the absolute deadline expires, cancel remaining tasks, and require `ceil(256 * 0.9) = 231` valid results.
- `tests/manual/agent_opd/swe_replay.py:377–388`: a valid returned sample includes generation, teacher scoring and canonical validation, not generation alone.

Reaching231 completed candidates does not currently close the bank early. Completion of all256 closes it early; otherwise it closes at the deadline and trains on the accepted partial bank if its count is at least231.

Generating356 candidates and selecting the first256 valid completions would change source consumption, trained bank membership, and completion-time selection. It may prefer shorter prompts/responses and adds teacher workload. Such a policy remains an unresolved experimental choice; the existing256-candidate policy is preserved.

## Verification commands and limits

The exact-name platform query and scoped SSH read used the handbook's local personal Python API and read-only `ssh shai-ycfeng` route respectively. The SSH command asserted `id -un == i-fengyicheng`; only the named job's `training/bank_6.jsonl`, `training/teacher_stages.jsonl`, and checkpoint-directory names were read. There were no checkpoint directories and no cloud writes.

Local receipt checks used `python3 -B` with `json.loads`, asserting native successful IDs equal `[1,2,3,4,5,6]`, counting bank/teacher statuses, and calculating timing/token statistics from the retained source records. Values above are observations from that check, not estimates.

H800 pre-launch configuration checks and actual submission/startup results will be recorded separately as they complete. No new H800 RJob is claimed by this preparation record.
