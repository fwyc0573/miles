## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Record native qualification configuration, CPU worker/SDK checks, live quota observation and exact submission procedure. |

# Native H800 prerequisite execution

## Scope

These are P2 baseline/qualification jobs with `num_rollout=0`: each uses the frozen 24 monitoring prefixes, native student generation, frozen-teacher scoring and training-backend forward-only scoring. They perform no optimizer updates and save no HF checkpoint. Their diagnostic completions are additional prerequisite measurements, not part of the subsequent formal D9 update/monitoring budget. A successful probe is not a full P3/D8 verdict: updated/final versions, backward/optimizer capacity, learning behavior and real final HF reload remain to be tested.

The actual shared population and authorized model assets were verified by `exp-1106-233008-986003`; see the [P2 report](test_report_2026-11-06_p2.md). Data/export/evidence code is committed as `ede719c1`; native monitor and launcher code receive their own verified commit before GPU execution.

## Candidate resources, not measured capacity claims

Exact inputs: [native_probe_config.json](native_probe_config.json).

| Pair | Student allocation | Independent teacher allocation | Total GPUs |
| --- | --- | --- | ---: |
| A | 8 H800, trainer TP2/CP1/PP1; four TP2 rollout engines; 64 CPU, 512,000 MiB | 27B on 2 H800, TP2; 16 CPU, 128,000 MiB | 10 |
| B | Same 4B student layout as A, independent state and artifacts | 35B-A3B on 2 H800, TP2; 16 CPU, 128,000 MiB | 10 |
| C | 27B on 8 H800, trainer TP4/CP1/PP1; two TP4 rollout engines; 64 CPU, 768,000 MiB | Full 397B-A17B on two 8-H800 nodes, TP16; each 64 CPU, 512,000 MiB | 24 |

The matrix requests at most 44 GPUs for this prerequisite wave. These are candidate shapes based on the existing student recipes and indexed frozen-model storage sizes; they are not established minima or proof that 128K training fits. The 806.8 GB teacher source cannot fit on one 8×80 GB node; the two-node teacher must demonstrate actual load and forward behavior. No quantized or reduced-layer substitute is selected. Native optimizer/backward memory is not exercised by zero-update evaluation.

Each pair is one RJob with separate `student` and `teacher` task GPU allocations. Only the student is critical. Teacher head/address readiness and student-completion markers coordinate ordinary child processes; the worker does not call platform controls. The shared teacher and student are never put into the same student Ray GPU allocation. Pair C's teacher retains both native RDMA requests (`mellanox.com/mlnx_rdma:1`, `rdma/mlnx_shared:8`) and `DISTRIBUTED_JOB=true`. Student synchronization remains D5 CUDA IPC, not NCCL-direct qualification.

The two-GPU A/B teachers explicitly set `host_network=false` so their fixed HTTP/rendezvous ports remain isolated when sharing a physical node. Full-node students and the distributed C teacher keep native host networking. ResourceConfig defaults to host networking and only automatically disables it for partial-node allocations in its separate node-task-map branch; this ordinary task-spec path therefore requires the explicit JSON value (`steptron/exp/base_exp.py:4066,4442–4461`).

Native `gang_start=true` applies to all resolved tasks; `ResourceConfig.gang_group=true` also requires every task in the pair to have resources before group startup (`base_exp.py:4065,4144–4148`, `stepmind.py:453–460`). Retain these defaults so startup deadlines do not run on a partially scheduled student/teacher pair.

Native ResourceConfig resolution on the local Python 3.10.6 StepMind environment checked all six task shapes, replicas, role envs, criticality, image, mounts and C teacher RDMA values. Retained output: [native-resource-resolution-20261107.json](evidence/native-resource-resolution-20261107.json). The first inspection iterated dictionary keys and printed `None` attributes; it was not counted as validation. Correct inspection uses `for name, task_config in resource` and asserts the actual resolved fields.

The SDK automatically appends its existing public-tenant mount during resource iteration (`steptron/exp/base_exp.py:4383–4461`); this appears in the resolved receipt in addition to the two requested source-volume mounts. Task code does not read or write that directory. Native code pulling is disabled by the local-source `spawn_tasks` path. The approved model-source read exceptions and personal-write restrictions remain unchanged.

## Image and environment

Use the already CPU-qualified pinned Miles image in the JSON, with `/opt/sglang/bin/python3`. Preserve the verified prior H800 compatibility setup: prepend that image's `/usr/local/cuda-13.0/compat` to inherited `LD_LIBRARY_PATH` before Python starts. This exact requirement was established in the previous warmup's `test_report_2026-11-05_agent_opd.md`, including actual CUDA kernels; it is not a new worker install or retry fallback. No worker dependency installation is part of this path.

The parent `submit_qwen35.py` supplies local `/data/ycfeng` NFS source, H800/codesign, personal auth and the explicit image. `qwen35_pair_worker.py` places caches on worker-local storage and raw logs in the personal cloud run root. The student delegates to `run_qwen35_opd.py`. Existing deterministic-channel environment handling preserves matching platform `NCCL_*` values and rejects conflicts before launch instead of overwriting them.

## CPU verification

```bash
python3 tests/manual/agent_opd/submit_qwen35.py --config task_memory/task_2026-11-06_qwen35_three_pairs/native_probe_config.json --pair C --dry-run
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_qwen35_pair_worker.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen35-pair-worker-native-config -o addopts=''
```

Dry-run: PASS, 24 GPUs for C, no submission. Worker tests: **14 passed, 7 warnings, 0.43 s**, Python 3.12.13, exit 0. They cover model/readiness identity, native argv, source boundaries, rendezvous order, faithful return codes, cancellation and owned-child cleanup. HTTP and GPUs remain fixtures; none of this proves native H800 behavior. Shapes are supplied by JSON rather than inferred from a pair label.

## Live quota observation

At **2026-11-06T16:12:15.747108Z** (Nov 7 local), a bounded personal Python `RJobClient._list_rjobs_kapis(quota_group='codesign', limit=256, phases=['Running','Pending','Starting'])` read returned **33 Running RJobs requesting 112 non-preemptible GPUs**. This is active requested capacity, not free quota; no free-GPU count is asserted. The 128-GPU value is the user's stated ceiling. Submission/scheduler placement is authoritative, and queued jobs are retained rather than duplicated. Receipt: [codesign-capacity-20261107.json](evidence/codesign-capacity-20261107.json).

## Submission procedure

From `/data/ycfeng`, initialize the runbook's proxy and personal credentials without displaying their values, set `STEPMIND_BACKEND=rjob`, `PYTHONPATH=/data/ycfeng/steptron`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONNOUSERSITE=1` and local `TMPDIR`. Submit each pair in its own long-lived local launcher using:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/submit_qwen35.py --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/native_probe_config.json --pair A
/data/ycfeng/tmp/stepmind-env/bin/python -u -B /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/submit_qwen35.py --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/native_probe_config.json --pair B
/data/ycfeng/tmp/stepmind-env/bin/python -u -B /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/submit_qwen35.py --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/native_probe_config.json --pair C
```

The script sets the required EXP_ID before constructing the backend and calls `spawn_tasks`, whose wait keeps the local launcher alive. Inspect each exact returned job for creator, both task shapes/mount sources, worker H800 devices, teacher native load/readiness, generated/scored monitoring artifacts, and terminal state. Current status at creation of this report: **not submitted**. Append actual job IDs and observations after submission; these commands alone are not execution evidence.
