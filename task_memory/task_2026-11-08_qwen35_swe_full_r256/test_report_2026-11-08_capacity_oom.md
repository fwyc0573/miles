## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record the first actual256-turn capacity failures and their native scoring exception; preserve successful acquisition evidence. |

# Native capacity verification and scoring OOM

## Result

**Capacity acceptance FAIL; acquisition PASS.** Both jobs sealed all256 trajectories before the acquisition deadline, then failed during current-student rescoring before any successful update. No shortened batch, changed length limit or substitute metric was used.

| Cell | Job | Completed/missing slots | Requested allocation at failure | Free GPU memory | Successful updates |
| --- | --- | --- | --- | --- | --- |
| A/r256 | exp-1108-174749-557599 | 256/0 | 30.31GiB | 29.58GiB | 0 |
| B/full | exp-1108-174748-739227 | 256/0 | 30.31GiB | 29.49GiB | 0 |

The run configuration is `capacity_smoke_config.json`, derived from the accepted short native configuration. It requests two successful updates at the representative full candidate budget; it is a smoke, not a formal cell. Each RJob has8 student and2 teacher H200, native TP2/DP4/CP1. Submission used the existing serialized temporary task allowance, personal Python3.10.6/brainpp2.8.6 and the pinned image from that configuration. Worker Python3.12 and native Megatron are the same previously qualified image paths.

## Commands and retained evidence

Executed from `/data/ycfeng` after the handbook's private personal-auth/proxy setup:

```bash
STEPMIND_BACKEND=rjob PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron \
  /data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_swe_opd \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/capacity_smoke_config.json \
  --pair A --protocol r256 \
  --receipt /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/admission-A-r256-capacity-20261108.json
```

The independent B invocation uses `--pair B --protocol full` and `admission-B-full-capacity-20261108.json`. Raw launcher logs: `/data/ycfeng/tmp/qwen35-swe-{A-r256,B-full}-capacity-20261108.log`. Both exit1 because native student work failed, not the earlier normal-critical-completion classification bug.

Parent executed the existing personal-client `collect_failure_evidence.py` for both exact jobs/student replicas, with incident window `2026-11-08T10:20:00Z`–`10:27:00Z`, per-request timeout15s and external timeout180s. Outputs: `/data/ycfeng/tmp/rca-capacity-<job>/`. Exact replica objects report container exit1/Error, followed by `Some critical tasks failed.`; the later teacher stop is cleanup. All-operation audit queries were unavailable, so no unknown external actor is invented. Native business stdout is redirected into the run's sibling `.log`, not the platform replica console.

`evidence/capacity-first-failure-20261108.json` retains both first exception traces, acquisition start/seal receipts, successful/missing counts and exact cloud paths. Parent downloaded only this selected evidence through the authorized read-only `shai-ycfeng` mount, using an external60s timeout; original trajectory/tensor artifacts remain on the personal cloud volume.

## Native failure

The first exception is `torch.OutOfMemoryError` in Megatron `tensor_parallel/layers.py:514`, `output = torch.matmul(total_input, weight.t())`, reached from the actor's `_compute_log_prob` call before the update. A reports45.73GiB allocated and61.35GiB reserved-but-unallocated by PyTorch; B reports45.91GiB and61.27GiB. The colocated inference process is reported at1.68GiB. These are actual allocator observations, not a measured explanation of all retained memory.

Acceptance requires the unchanged representative workload to complete its successful updates with the existing scientific/statistical contract. The next diagnosis tests previous-output lifetime, available native output chunking and fragmentation/offload evidence before selecting a fix. The captured256-trajectory batch can potentially shorten the reproducer through an existing replay/debug seam; this seam must be verified before use. No extra scoring path or lower sequence limit is accepted by this report.
