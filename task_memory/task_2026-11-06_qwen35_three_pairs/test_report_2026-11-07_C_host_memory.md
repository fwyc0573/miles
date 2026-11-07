## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Record D16's selected1500GiB student limit, observed node capacity and passing exact-change/dry-run checks; defer optional rematerialization repair. |
| 2026-11-07 | Record measured host OOM, bounded source accounting, corrected censored-peak interpretation and the rematerialization/scoring failure window. |

# C host-memory qualification

## Decision and current status

D15 approves a new100-position C run from initial weights, preserving the discarded historical update. **D16 selects1500GiB for the C student container while retaining normal parameter backups.** No additional optimizer probe is authorized. A/B do not depend on C capacity.

Personal Python RJobClient read the historical student replica's node, `gpu-h800-0223.host.platform.shaipower.com`, then its Kubernetes node capacity. Actual allocatable memory is1,994,674,160Ki, approximately1902.27GiB; [retained capacity evidence](evidence/C-node-capacity.json). This is node capacity, not free memory or guaranteed scheduling.

Only `pairs.C.student.memory_gb_per_node` changed768→1536 in `training_config.json`. Native local rendering used:

```bash
/usr/bin/python3 tests/manual/agent_opd/submit_qwen35.py \
  --config task_memory/task_2026-11-06_qwen35_three_pairs/training_config.json \
  --pair C --dry-run
```

Expected and observed: `submitted=false`,100 positions,24 GPUs, student `mem_gb=1536`, teacher `mem_gb=512`. A structural comparison against Git HEAD verifies exactly that one JSON leaf changed. Expected platform conversion:1,536,000Mi =1500GiB. **PASS for configuration rendering**, with platform allocation and full-model capacity still unverified. Full resolved command and output: [C restart resources](evidence/C-restart-resources.json). No persistent test was added for the one-value configuration edit.

The failed C job `exp-1107-064200-013666` reached one optimizer update but did not publish version1 or save updated weights. Its student cgroup hit750GiB and recorded `oom_kill:0→1`. This is a measured host OOM, separate from the earlier incorrect scoring/restoration.

## Measured evidence

Sources: [C memory window](evidence/C-host-memory-window.json), [actual launch flags and historical scores](evidence/historical-torch-scores-and-C-flags.json), and `evidence/first-round/student/C/exp-1107-064200-013666/memory.json`.

| Observation | Actual |
| --- | --- |
| cgroup limit | 805,306,368,000 bytes =750GiB |
| sampled maximum | 805,304,623,104 bytes |
| kernel maximum | 805,305,688,064 bytes |
| pre-step plateau | 384.12GiB at01:10:30 UTC |
| capped peak | 750GiB at01:11:14.63 UTC |
| completed native step | 01:11:11.107 UTC;8/8 ranks NORMAL |
| ramp | At least365.88GiB; OOM-censored |

The v1 cgroup usage includes page cache. The measurements do not identify the anonymous/pinned/cache split, nor an uncensored peak. Exit137 alone was not used to infer OOM.

## Source accounting, not a capacity measurement

C uses8 student GPUs, TP4/DP2, full CPU-offloaded precision-aware Adam and one normal `actor` backup. Text architecture arithmetic estimates26.896B parameters, or6.724B/rank before DP sharding. The original full asset size is a conservative cross-check, not an exact decoder count.

| Host allocation | Estimated GiB/node |
| --- | --- |
| Normal pinned actor backup | 100.2 |
| HDO BF16 CPU copy | 50.1 |
| HDO FP32 master | 100.2 |
| HDO FP32 gradient, allocated on first step | 100.2 |
| Adam moments, allocated on first step | 200.4 |

The first-step gradient/moment estimate is300.6GiB versus the censored measured ramp≥365.88GiB. The residual≥65GiB is unassigned; it is not an empirical scaling factor. The pre-step plateau similarly exceeds the enumerated persistent model allocations by about134GiB.

`--rematerialize-param-from-master-weight` can remove approximately100GiB of normal actor backup by reusing existing HDO reconstruction. It does not remove HDO's BF16 CPU copy, master, gradients or moments. **Subtracting that estimate from a750GiB censored peak produces only a roughly650GiB lower bound; the upper bound and remaining headroom are unknown.** The earlier investigation's claims of a650GiB forecast,≥100GiB headroom or a required850GiB allocation are withdrawn.

## Pinned allocation support

The parent0-GPU job `exp-1107-125038-984696` collected exact source excerpts using `importlib.import_module`, `inspect.getsource` and `inspect.getfile`. [Retained source evidence](evidence/restore-source-exp-1107-125038-984696.json) records Python/runtime provenance and the original baseline-origin check. This inspection does not instantiate the C model or optimizer.

Actual pinned `/root/Megatron-LM/megatron/core/distributed/param_and_grad_buffer.py` contains `disable_param_buffers_cpu_backup` and constructs its `param_buffer` context with `enable_cpu_backup=False` (1142–1146,1286,1293–1295). The actual distributed-data-parallel config contains the field. This closes the earlier concern based on a different local Megatron package. HDO and main-cast implementation excerpts are retained in the same JSON. Actual C mapping coverage and full-cycle behavior remain unmeasured.

## Rematerialization and evaluation failure interaction

Read-only analysis by `QWEN-P3-C-HOST-MEMORY` found a reachable source-level window, not a reproduced GPU failure:

1. Eval scoring resumes non-backed parameter memory, then fails before completing `_switch_model("actor")`, for example during transient PG reload.
2. Normal backup mode can safely publish its intact CPU backup after successful rollback. In rematerialized mode, native `sleep()` deliberately leaves `param_buffer` resident for publication.
3. If PG reload subsequently succeeds, `update_weights()` can read those un-restored live parameters through the main-cast backuper's `get("actor")`. Its companion/version comes from intact extras, so the published version can look correct despite wrong bytes.

Relevant owners: `actor.py::wake_up/score_log_probs/sleep/_update_receiver_weights`, `tensor_backper.py` main-cast `get/restore`, and `train.py` eval restoration. Existing PG-failure tests use the normal backuper and cannot qualify this combination. The Qwen35 rematerialization e2e precedent lacks `--eval-train-log-probs`.

The completed read-only minimal-owner review found that simply calling `_switch_model("actor")` before publication is insufficient: default-region master/extras can also be paused. A candidate must manage that region's residency and force-sync before reading parameters, cover already-paused parameter entry states, and measure the additional GPU peak while SG weights are resident. D16 does not select that repair; it remains deferred and the flag stays false. No validity bit, new RPC/error classification, semantic change or flag was implemented. Disabling required evaluation scoring is not an accepted solution. Disk offload is also not established as a way to remove the separate normal pinned actor backup.

## Acceptance still required

- Verify the actual platform memory request/limit equals the rendered D16 allocation, preserving D8/D9/D12/D14 semantics and D15 accounting.
- Measure actual C host usage and the successful first update within the approved fresh100-position run. A source estimate or tiny probe cannot prove full-model capacity.
- Verify fresh baseline, post-eval generation, planned updates, final publication and final text-HF qualification independently.

Current verdict: **INCOMPLETE**. Measured failure attribution is complete; sufficient runtime capacity is not established.
