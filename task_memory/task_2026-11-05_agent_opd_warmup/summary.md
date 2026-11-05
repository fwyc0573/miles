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
The current warmup will use16H800, with otherwise unchanged training parameters.
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
The explicit H800 worker CLI check passed. Local launcher 72538 created `exp-1105-130232-725485`; personal API confirmed Starting, two eight-GPU replicas, current-local NFS and both RDMA limits. Actual H800 optimizer execution is pending.

## Remaining work

1. Run the selected16H800 warmup and inspect actual worker/GPU/source/runtime.
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
needed. Only code and Markdown conclusions enter Git. Verified scalar-fix remote
SHA is `b3fd5780dabe40ca761d99110c7779d7b71be68d`; final validation and synchronization
remain unfinished.
