## Modification History

| Date | Change |
| --- | --- |
| 2026-11-05 | Archive verified preparation, confirmed intermediate GitHub synchronization and pending GPU qualification. |

# Agentic OPD Preparation Snapshot

The preparation code and requested model assets are ready. **The actual GLM OPD
warmup has not passed.** Previous full model attempts completed zero optimizer
updates; the current diagnostic job is queued for 16 H200 GPUs. This record is
an intermediate snapshot with GPU qualification still pending. The preparation
branch has been synchronized to the personal origin at commit
`c403bdc7af16b7ddce640c4af1144b7f36e7fc31`; this is not warmup completion.

## Deliverables

- Branch: `agent-opd` in `/data/ycfeng/sota-engine/miles`; requested personal
  origin: `https://github.com/fwyc0573/miles.git`.
- `examples/agentic_opd/glm_turns.py` and `examples/agentic_opd/rollout.py` retain
  original token boundaries, reasoning, ordinary text, tool arguments and turn
  identity. Parsed text never replaces the token sequence used for training.
- `scripts/run_glm47_flash_agent_opd.py` configures native OPD, R3, TIS and
  deterministic FA3 for 8 GPUs for student training, 4 GPUs for student inference and 4
  GPUs for frozen teacher inference.
- `tests/manual/agent_opd/prepare_glm5_2.py`, `rjob_warmup.py`, `runtime_probe.py`,
  `weight_sync_probe.py` and `inspect_warmup.py` provide the reproducible source
  preparation, worker entrypoint, actual-kernel checks and native inspection.
- `miles/utils/distributed_utils.py` and
  `tests/fast/utils/test_independent_process_group.py` cover the independent
  transfer-world initialization fix.
- `docs/advanced/on-policy-distillation.md` documents the recipe. Exact commands,
  observations, community sources and qualification limits are maintained in
  `test_report_2026-11-05_agent_opd.md` in this task directory.

## Model assets

Visible authenticated Lark search returned no FrogNano result and three
contextual Qwen3.5-4B documents without a verified asset path. This does not
establish company-wide absence. The company HF mirror completed the missing
pinned download; all 22 files, 18,685,617,357 bytes, passed size and complete SHA256 checks.
VPS fallback was unnecessary.

- `/mnt/codesign-exp/ycfeng/opd-assets/models/microsoft/FrogNano-4B-2609/b90468c11a913c1916b4542b4b7a530ec42024a4`
- `/mnt/codesign-exp/ycfeng/opd-assets/models/Qwen/Qwen3.5-4B/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`

The GLM student/teacher weights remain the existing shared personal assets
recorded in the warmup configuration. No shared model or original dataset was
deleted or modified.

## Observed validation

- All four real glm5.2 source categories matched ticket07 prompt/completion
  counts and hashes. Thinking, ordinary text, submit/bash/editor calls and
  plain/truncated completion cases passed CPU inspection.
- The new launcher has 2 passing snapshot checks. The full launcher suite is
  584PASS/18FAIL/50ERROR; all 68 failing/error IDs match the unchanged baseline
  (582PASS/18FAIL/50ERROR). These unrelated failures were not repaired.
- The independent process-group regression passed on CPU. Actual two-node
  H200 kernels passed on all 16 GPUs using the pinned CUDA13 image's existing
  compatibility libraries. The minimum world 5 BF16 broadcast passed twice
  with intact parent worlds 8/4; full model transfer still failed afterwards.
- The latest full model failure is NCCL 2.30.7 `Message truncated`, 2048/512 bytes,
  before rollout or optimization. Sender/receiver deterministic channel
  alignment is a candidate qualified on CPU; GPU confirmation is pending.
- Verification covers single turn OPD. Live multi-turn tool execution remains
  unqualified. The native driver does not publish its final optimizer update;
  publication checks apply to versions actually sent to inference.

## Active work and resource constraint

Keep local launcher session 50766 alive for
`exp-1105-031302-898658`. It uses the personal StepMind Python RJobBackend,
local Miles NFS 100.96.128.195, 2 × 8 H200 and preemptible=yes. Do not submit a duplicate.
At 2026-11-05T06:47:27.391606+08:00, the exact job is Pending, queue rank8 and approval empty.
The capacity query reports 8 usable GPUs in step_main. The last personal
non-preemptible usage query recorded48 GPUs across6 unrelated jobs. Codesign returned 166 H800 nodes and 19 nodes without GPUType, with no
H200 label; infer_af_test returned only CPU nodes.

The queued entrypoint compares receiver8/sender-unset with matching8/8.
It proceeds to the same allocation's two-update GLM warmup only when the
actual sender bounds are unset, the asymmetric case reproduces the identical
truncation, and the matching case passes. RJob Succeeded alone does not prove
OPD PASS; inspect the separate inspection exit code and native observations.

Remaining work:

1. Read the original job's actual channel differential and conditional
   training result after placement.
2. Verify two normal optimizer outcomes, finite/nonzero gradients and changed
   published weights, teacher scoring of identical tokens, R3 arrays, weight versions
   and measured train/inference logprob and TIS differences.
3. Remove all remaining created by this task raw warmup outputs, logs, caches, manifests
   and temporary source after inspection; update the final English archive
   and synchronize `agent-opd` again.

## Cleanup and synchronization

Consumed raw logs/RCA, inactive smoke inputs, lint caches and root pytest/Ruff
caches have been removed. Image removal for this task recovered about 83GB.
Current local free space is approximately 111GiB; the remaining task tmp is 173MiB
and active inputs are 988KiB. These remaining dependencies support the queued job and pending verification. Requested model assets and shared source data remain available.
Only code and Markdown conclusions belong in the branch. The preparation
snapshot was synchronized to personal origin `fwyc0573/miles`; a read-only
`git ls-remote --heads origin agent-opd` check at 2026-11-05T06:47:27.391606+08:00
matched local commit `c403bdc7af16b7ddce640c4af1144b7f36e7fc31`. Final verification, cleanup
and synchronization after training remain unfinished.
