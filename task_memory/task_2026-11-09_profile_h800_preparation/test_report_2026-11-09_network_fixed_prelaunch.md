## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Add fresh admission, actual submission and initial filtered platform Starting evidence; leave business checks pending. |
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
| Fresh platform admission/submission | Actual receipt and job required | exp-1109-192340-580111 submitted11:23:40Z; fresh24other+36requested; non-preemptible/personal creator/current-host source verified | PASS |
| Worker GPU observation | Four student hosts×8 plus teacher4, all H800; current image/models | Five matching node receipts,36 actual H800 GPUs at11:33:03Z | PASS |
| Native engines, NCCL, weights and capacity | Real36GPUs,8engines, initial synchronization,231/256within1800s,2ACKs/second scoring/same-bank2uses | Not yet performed | PENDING |

The first local argv inspection incorrectly used`json.loads` on the CLI's successful shell-quoted text and raised`JSONDecodeError`. The corrected inspection follows the existing CLI contract with`shlex.split`, verifies each flag/value and records the result. This was an inspection error, not a failed training launch; no RJob or product change resulted.

## Contract and soft-gate limits

As of11:19Z, upstream`agent-opd` at`23b29f66` has an approved original18-H200 rerun but no new submitted job or native acceptance in its local records. It has not recorded this parent's D34 split. The H800 run verifies this parent's H800/112K-prompt/16K-completion readiness; it does not accept the frozen upstream D11 contract or lift D1/D22. No other owner's job is stopped or held.

The actual native retry uses the existing personal Python backend from`/data/ycfeng`, obtains a fresh inventory under the ordinary admission lock, keeps its launcher alive and writes only to the new personal cloud run root. Native timeouts, source models, mask/sequence policy, seeds, loss and topology stay unchanged. Existing event/receipt reporting is reused. Missing auxiliary environment evidence is marked unverified and reported; it is not a training hard gate. A terminal smoke's obsolete cloud duplicates are cleaned only after exact local evidence retention and verification under the existing authorization.

## Actual submission and initial platform readback

After the runbook's personal authentication/proxy initialization, the exact ordinary submitter invocation was:

```bash
export STEPMIND_BACKEND=rjob
export PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity:/data/ycfeng/steptron
cd /data/ycfeng
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_swe_opd \
  --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity/task_memory/task_2026-11-09_profile_h800_preparation/h800_capacity_config.json \
  --pair A --protocol r256 \
  --receipt /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity/task_memory/task_2026-11-09_profile_h800_preparation/evidence/admission-h800-network-fixed-20261109.json
```

Local submitter interpreter: Python3.10.6. The shell sets`PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR=/data/ycfeng/tmp` and retains its output at`/data/ycfeng/tmp/agent-opd-image/qwen35-h800-network-fixed-20261109.log`. Background owner`sh_1c00ca257001FAmkzN0D28AQ9j` remains alive under the ordinary native lifecycle.

Fresh admission at11:23:40Z requested36 H800 GPUs alongside24 other H800 commitments, under the explicit null ceiling and non-preemptible personal scope. Actual job `exp-1109-192340-580111`, UID `28536e46-208d-4635-b648-27c782a09c9b`, has creator `i-fengyicheng` and source `100.96.128.195:/data/ycfeng:/data/ycfeng`. Initial readback: Starting, student4×8/teacher1×4, H800/codesign/no preemption. The filtered task payload retains requested image/resources/host-network and node-NCCL declarations without exposing credentials. Evidence: `evidence/admission-h800-network-fixed-20261109.json` and `evidence/h800-network-fixed-native-startup-20261109.json`.

Exact platform call after the same auth initialization:

```python
client.api.get_namespaced_custom_object(
    group=client.group, version=client.version, namespace=client.namespace,
    plural=client.plural, name="exp-1109-192340-580111", _request_timeout=20,
)
```

Only filtered metadata/status and task resources/network declarations were retained. The independent query asserts creator, current source mount and36 total requested GPUs; failure of this readback could not propagate into the live training process. Paramiko emits the same existing TripleDES deprecation warnings; the call succeeds. Requested platform resources and Starting do not establish observed worker hardware, effective engine environment, native NCCL behavior, optimizer outcomes or capacity acceptance.

At11:33:03Z a separate local read of all five `*-node-*.json` receipts confirms36 actual H800 devices,81559MiB each, driver570.124.06. Student hosts are distinct, each with8 devices; the teacher has4. Each receipt's job, pair, image, model path and device count matches the frozen configuration. These validated records are retained in `evidence/h800-network-fixed-worker-gpu-readback-20261109.json`. This is hardware observation, not an engine-environment or training verdict. Engine initialization, native NCCL, weight synchronization and capacity criteria remain pending.
