## Modification History

| Date | Change |
| --- | --- |
| 2026-11-05 | Start the bounded20-update learning and20×4 native benchmark verification. |

# Twenty-update OPD learning test

Status: preparation in progress; no new optimizer update or benchmark result is claimed.

Expected:20normal finite optimizer updates,80distinct glm5.2 turns, exact post-update20 export,20fixed questions×4 seeds with80valid native grader outcomes for both original and updated student. Tool execution and tests determine resolved/unresolved; infra/invalid outcomes remain missing. Cleanup removes all transient files after consumption.

Initial evidence: qualified two-update branch38ff410a0a8a3ca5fec8b3ce5a6ad8e3325200e7, current clean workingtree,109GiB local free. Relevant current source contracts: train.py final-save ordering and skipped final publication; miles/backends/megatron_utils/hf_export.py complete-marker export; referenced Ticket06 fixed50 manifest and native RunCheckPipeline.


## CPU preparation checks

Command: `PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/rollout/test_sglang_opd_request_contract.py tests/fast/rollout/test_opd_config_contract.py tests/fast/backends/training_utils/loss/test_opd.py -q`. Python3.12.13/pytest9.1.1:20PASS in3.85s. These check existing OPD request/loss contracts; they do not validate20-step learning or benchmark outcomes.

AST parse of modified prepare_glm5_2.py/rjob_warmup.py and new checkpoint_identity.py PASS; exported hook import PASS. Native evaluator imports of toml, swe_agents.cli.run, swe_agents.models.step_align, step_align.model.stepchat and playground.agenticeval.sweagents_swe PASS in the existing mounted Python3.10.20 environment. Exact interpreter: `/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/.venv/br-native-swe-py310-1008am/environment/bin/python`; native SWE/StepAlign source: `/data/ycfeng/steptron/.worktrees/step3p6-native-eval-1015z/third_party/`. Existing sandbox credentials are present; values were not printed.

The20-update adapter changes only bounded input count,4096-token response cap, native final save and export identity. Four rows per rollout/global batch and20rollouts mean20optimizer updates if every native outcome is normal.80different prompts are selected from20different groups per category under<=61440prompt tokens, with no wraparound; exact-source/hash checks execute before training. Original fixed175 membership and parent selection evidence are rehashed. This reuses inherited exact-text/marker exclusions and does not guarantee semantic paraphrase isolation.

Local source mount for this phase uses `/data/ycfeng` because Miles, the independently maintained Steptron input manifests and existing native evaluator environment are in different local directories. Expected NFS source remains the current local host, never the SSH server. Large outputs stay under the personal cloud learning namespace; local scratch is confined to `/data/ycfeng/tmp/agent-opd-learning-20261105` and deleted after consumption.
