## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record reviewed network correction, unchanged retry configuration, production dry-run checks and native acceptance limits. |

# Network-fixed H800 prelaunch verification

## Scope and environment

Task: `task_2026-11-09_profile_h800_preparation`, Plan9 and the next Plan8 attempt. Worktree: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`. Local interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13. No GPU or external operation was performed by these prelaunch commands.

## Code acceptance

Commit`cf98293a2037c27899636df8f2a37a99058b38b5` removes head-inherited NCCL forwarding while retaining existing explicit job-wide controls. The code owner's exact commands, production-path RED/GREEN and final529passed/12skipped/1known-baseline parser case deselected are in`test_report_2026-11-09_node_local_network.md`. The primary inspected the code diff and decisive report; it did not rerun the529 checks.

Reviewer`profile-h800-node-network-review-20261109`, session`ses_e3ffdba19ffe6ry9e4fP59h2Sc`, inspected the complete immutable four-file diff`d91be845..cf98293a` at`/data/ycfeng/tmp/agent-opd-image/cf98293a-fixed-review.diff`: **Standards/Spec No Findings**, limited to static and recordedCPU evidence. Actual native effective engine environments and NCCL2.30.7 behavior remain unverified.

## Primary checks

Commands ran with`PYTHONPATH` equal to this worktree,`PYTHONDONTWRITEBYTECODE=1`, and`TMPDIR=/data/ycfeng/tmp`.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.submit_swe_opd \
  --config task_memory/task_2026-11-09_profile_h800_preparation/h800_capacity_config.json \
  --pair A --protocol r256 \
  --receipt task_memory/task_2026-11-09_profile_h800_preparation/evidence/admission-h800-network-fixed-20261109.json \
  --dry-run
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.run_swe_opd \
  --config task_memory/task_2026-11-09_profile_h800_preparation/h800_capacity_config.json \
  --pair A --protocol r256 --role train --dry-run
```

Full absolute command arrays and outputs are retained in`evidence/h800-network-fixed-submission-dry-run-20261109.json` and`evidence/h800-network-fixed-native-argv-dry-run-20261109.json`.

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Config comparison against`git show cf98293a:task_memory/task_2026-11-09_profile_h800_preparation/h800_capacity_config.json` | Only output identity/path fields change | Exactly`phase`, `run_root`, `shared_dir` | PASS |
| Submitter request | H800/codesign, student4×8, teacher1×4,36total, no submission | Matches;`submitted=false`; explicit null policy unchanged | PASS |
| Native argv | Context131072, prompt114688, completion16384; trainerTP4, rollout32, engineTP4 | All expected fields match | PASS |
| Capacity budget argv | 256slots,1800seconds,2successful updates,2bank uses | All expected fields match | PASS |
| Actual `_runtime_env(ExecuteTrainConfig())` with head NIC/HCA present in the local environment | No implicit job-wide socket/HCA override | Both keys absent from returned env | PASS |
| Fresh platform admission/submission | Actual receipt and job required | Not yet performed | PENDING |
| Native engines, NCCL, weights and capacity | Real36GPUs,8engines, initial synchronization,231/256within1800s,2ACKs/second scoring/same-bank2uses | Not yet performed | PENDING |

The first local argv inspection incorrectly used`json.loads` on the CLI's successful shell-quoted text and raised`JSONDecodeError`. The corrected inspection follows the existing CLI contract with`shlex.split`, verifies each flag/value and records the result. This was an inspection error, not a failed training launch; no RJob or product change resulted.

## Contract and soft-gate limits

As of11:19Z, upstream`agent-opd` at`23b29f66` has an approved original18-H200 rerun but no new submitted job or native acceptance in its local records. It has not recorded this parent's D34 split. The H800 run verifies this parent's H800/112K-prompt/16K-completion readiness; it does not accept the frozen upstream D11 contract or lift D1/D22. No other owner's job is stopped or held.

The actual native retry uses the existing personal Python backend from`/data/ycfeng`, obtains a fresh inventory under the ordinary admission lock, keeps its launcher alive and writes only to the new personal cloud run root. Native timeouts, source models, mask/sequence policy, seeds, loss and topology stay unchanged. Existing event/receipt reporting is reused. Missing auxiliary environment evidence is marked unverified and reported; it is not a training hard gate. A terminal smoke's obsolete cloud duplicates are cleaned only after exact local evidence retention and verification under the existing authorization.
