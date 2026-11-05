## Modification History

| Date | Change |
| --- | --- |
| 2026-11-05 | Record verified preparation, real NCCL evidence, reward fix and temporary H800 steering. |

# Agentic OPD Preparation Snapshot

The preparation code and requested model assets are ready. **Real OPD optimizer
updates remain zero.** The first16-H200 allocation confirmed the deterministic
NCCL channel fix, then failed in rollout metrics before optimization. The scalar
reward adapter is verified on CPU and pushed at `b3fd5780`.

The user requested a temporary switch to H800/codesign. The queued H200 replacement
`exp-1105-124538-296267` was intentionally stopped through the mandated script.
The previous16H800 warmup overlapped student/teacher local GPUs4/5 and was intentionally stopped at13:19:27HKT before optimization. The repaired rerun exp-1105-132957-419084 passed all16H800 runtime checks, independent transfer and disjoint engine initialization, then failed05:43:48Z during Megatron optimizer initialization. The Ray job broadcast the head node NIC ens20np0 onto a trainer node configured for ens22np0. A CPU regression reproduces the overwrite; the minimal Ray environment fix is under verification. Updates remain0. Per-engine subprocess visibility binding is repaired and passed413related CPU checks with23existing GPU/TPU skips; rerun the same training parameters for actual validation.
H200 training qualification remains open.

## Deliverables

- Branch `agent-opd` in `/data/ycfeng/sota-engine/miles`; personal origin
  `https://github.com/fwyc0573/miles.git`.
- `examples/agentic_opd/glm_turns.py` and `rollout.py` preserve original token
  boundaries, reasoning, ordinary body, tool arguments and source identity.
  Parsed fields never replace tokens used for training.
- `scripts/run_glm47_flash_agent_opd.py` configures sampled-token OPD, R3, TIS,
  deterministic FA3 and the scalar reward adapter:8student-training GPUs,
  4student-inference GPUs and4frozen-teacher GPUs.
- `tests/manual/agent_opd/prepare_glm5_2.py`, `rjob_warmup.py`, `runtime_probe.py`,
  `weight_sync_probe.py` and `inspect_warmup.py` provide preparation, explicit
  H200/H800 device checks and native output inspection.
- `miles/utils/distributed_utils.py` and
  `tests/fast/utils/test_independent_process_group.py` cover the independent
  transfer-world initialization fix.
- `docs/advanced/on-policy-distillation.md` documents the recipe. Exact commands,
  measurements, source rationale and limitations remain in this task's test report.

## Model assets

Authenticated Lark search returned no FrogNano result and three contextual
Qwen3.5-4B documents without a verified asset path. This does not establish
company-wide absence. The company HF mirror completed both missing pinned
assets:22files,18,685,617,357bytes, full size/SHA256 checks passed. VPS was unnecessary.

- `/mnt/codesign-exp/ycfeng/opd-assets/models/microsoft/FrogNano-4B-2609/b90468c11a913c1916b4542b4b7a530ec42024a4`
- `/mnt/codesign-exp/ycfeng/opd-assets/models/Qwen/Qwen3.5-4B/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`

Shared GLM student/teacher weights and original glm5.2 sources remain unchanged.

## Observed validation

All four real source categories matched ticket07 counts/hashes. CPU inspection
covered thinking, ordinary text, submit/bash/editor calls and truncated text.
The scalar reward adapter passed106OPD/metrics checks in4.17s, including exact
teacher token order, logprobs and unchanged launch arguments. Launcher snapshot
checks passed; latest full suite:584passed,18failed,50errors in22.03s. These
68failures remain the documented unchanged baseline.

The original16H200 allocation used two distinct nodes and the pinned CUDA13
image's existing compatibility libraries. The asymmetric sender had unset channel
bounds while receivers had8; it reproduced Message truncated2048/512. Matching
bounds8passed BF16 broadcasts496/528 and parent reductions36/10. The real GLM
path then published initial weights and generated rollout0, but metrics attempted
round(dict) and failed before optimization. Trainer exit1preceded fail-policy
cleanup. Incident-bound preemption/OOM was not established.

Fresh codesign query before H800 submission returned186nodes/63usable GPUs and
0personal Running/Starting GPUs. This is capacity evidence, not a reservation.
The explicit H800 worker CLI check passed. `exp-1105-130232-725485` failed before Python: the local-mount wrapper tried to exec the export builtin. Exact worker logs and a CPU reproduction confirmed exit 127; an explicit bash wrapper passed. Two eight-GPU replicas, current-local NFS and RDMA limits were verified; The corrected job exp-1105-130933-760790 passed all16 CUDA kernel checks and independent transfer, then encountered the GPU overlap and native KV-memory failure. Actual optimizer execution remains unverified.

## Remaining work

1. Run the selected16H800 warmup with the verified per-engine device binding.
2. Confirm two normal finite updates, nonzero gradients, changed published
   weights, identical teacher/student token IDs, R3 arrays, weight versions and
   measured train/inference logprob and TIS differences.
3. Immediately remove all task-owned raw data, logs, compile caches, manifests
   and disposable cloud outputs. Retain code/Markdown conclusions and push the
   final branch. Keep requested model assets and shared source datasets.

Verification covers single-turn OPD; live multi-turn tool execution is unqualified.
The native driver does not publish its final optimizer update. Publication checks
apply to versions actually sent to inference. H800 results do not qualify H200.

## Cleanup and synchronization

Consumed failed cloud output117,262,536bytes, raw RCA/logs/channel receipts and
CPU test scratch have been removed. Earlier task image cleanup recovered about
83GB. Local free space is approximately110GiB; remaining task temporary source
is173MiB and active manifest/configuration988KiB. These are removed when no longer
needed. Only code and Markdown conclusions enter Git. Latest preparation remote
SHA is `26a1ad72f8be17bb265fdd52b290dd6016ad56d7`; final validation and synchronization
remain unfinished.
