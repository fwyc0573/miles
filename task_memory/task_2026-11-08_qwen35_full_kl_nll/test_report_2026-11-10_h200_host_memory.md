## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record the post-update host-memory failure, pinned TMS source inspection and D38 diagnostic authorization. |

# H200 post-update host-memory investigation

## Confirmed failure

Formal A `exp-1110-140032-491115` completed its first optimizer update and passed[the D16 measurement checks](test_report_2026-11-10_d16_first_update.md). The subsequent trainer sleep/offload exceeded Ray's host-memory threshold and Ray killed trainer PID8670. The later Gloo/weight-update errors followed that termination. The attempt is Failed,1/200, and all replicas are terminal.

The raw rank0 log is `/data/ycfeng/tmp/agent-opd-image/d16-exp-1110-140032-491115/rank-0.log`. Relevant ranges are4154–4166 for NORMAL outcomes/sleep and4206–4259 for the memory-monitor decision. Selected evidence and query availability are in[evidence/d16-H200-A-20261110/failure-and-coverage.json](evidence/d16-H200-A-20261110/failure-and-coverage.json).

The selected text excerpt adds source line numbers and normalizes two whitespace-only line tails for Git whitespace checks. The complete raw log is retained unchanged at the path above.

- One Ray diagnostic reports487.49GiB of500GiB. A separate kill-scan observation is510,431,268,864 bytes =475.376GiB against a510,027,366,400-byte =475GiB threshold. They are different samples.
- The80.31GB CPU log field comes from `psutil.virtual_memory().used / 1e9` at `miles/backends/training_utils/metrics/log_utils.py:448–456`: it is node-global and cannot be used as per-rank RSS or the Ray cgroup's memory.
- The eight process-memory lines sum to approximately434.76GB; that sum is not a unique-physical-memory accounting. Ray's object-store reading is about9.58MB.

No Ray protection setting, memory request or training/offload target has been changed as a result of this investigation.

## Inspected ownership and limits

The read-only source investigation traced `miles/train.py:259–293` → `miles/ray/train/group.py:581–584` → `miles/backends/megatron_utils/actor.py:496–526`. Before `torch_memory_saver.pause(tag=None)`, the existing path clears TE workspaces, synchronizes, runs garbage collection, empties CUDA/host caches and destroys process groups. Both disable-parameter-CPU-backup and disable-gradient-CPU-backup flags were already true in the actual launch.

After clearing, rank4 still reported19.09GiB allocated versus79.93GiB reserved, a60.84GiB difference. Rank6's difference was28.74GiB. This supports investigating retained underlying allocation segments; it does not identify which live tensor kept any particular segment resident. A possible explanation is first-use Adam moment allocation splitting previously cached large forward-output segments. The failed process's segment/block ownership snapshot was not captured, so that attribution is **unproven**.

The source-based state estimate uses2,102,962,433 parameters per TP rank at TP2/DP4: BF16 parameters3.917GiB, FP32 gradients7.834GiB, FP32 master shard1.959GiB and Adam moment shards3.917GiB. Including the actor mirror gives roughly172.35GiB across eight ranks; with parameter/gradient TMS backups disabled, master/moments/mirror account for roughly78.34GiB. These are estimates excluding padding, auxiliary buffers and runtime allocations. They are not measured backup sizes or grounds to change the500GiB request.

## Pinned-image CPU inspection

The primary submitted zero-GPU job `exp-1110-144951-170247` locally through personal StepMind `RJobBackend`. Its job and sole replica succeeded. The exact command, image and resource/mount inputs are retained in[evidence/native-tms-source-20261110/worker-command.json](evidence/native-tms-source-20261110/worker-command.json); [terminal identity](evidence/native-tms-source-20261110/terminal.json) and[source manifest](evidence/native-tms-source-20261110/source.json) are retained separately.

Observed environment: Python3.12.16, `torch-memory-saver==0.0.10`, the same immutable image digest `165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805` as formal A. The script read installed Python source, SHA256-hashed each source/native binary and ran `nm -D --defined-only` on both native libraries. It performed no CUDA allocation or pause/resume.

| Binary | SHA256 | Observed support |
| --- | --- | --- |
| Preload CUDA13 | `99bbe5e2df91c5f9e5cd0a65e3947ceb3304bbb6a2b6ad539f00326cc583dcd4` | Disk enable/get/set-directory exports and DiskBackend symbols |
| Torch CUDA13 | `7a65bf68eb376d13d4ee28bdc123e88fd7abed556b40485ed98c67a408dde8fb` | Same exported disk interface |

This confirms the installed version and available interfaces. It does not measure native CPU backup bytes, disk offload correctness, page-cache behavior or the available storage on a subsequently allocated H200 worker. The source copies remain locally under the manifest's explicit paths. The CPU worker's `/var/tmp` had2,748,533,202,944 available bytes at capture; that is not a placement or disk-space promise for another worker.

## Next authorized experiment

[D38](requirements.md#host-memory-diagnostic-route--original-request-2026-11-10) authorizes one H200 allocator/TMS diagnostic with a600-second worker-script limit, startup separate. A separate implementation owner is preparing a controlled comparison of allocation ordering, allocator segment/block ownership and pause/resume observations. The primary owns submission and result acceptance. The diagnostic has not yet been submitted at this checkpoint.

Acceptance will distinguish successful execution and roundtrip checks from support for the allocation-retention hypothesis. Controlled behavior alone will not be called proof of the old full-model run's specific allocation owner. Any correction must subsequently pass the actual train → sleep → weight-update → next-train path, with optimizer progression and native business outputs inspected.

The existing disk-offload alternative was not selected. Formal artifacts remain protected, and the two earlier H800 zero-update attempts remain separate. Audited platform stop-request actor/time are still UNKNOWN because those two bounded audit reads failed; the native memory-monitor evidence is retained independently.
