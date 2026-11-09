## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Reference parent-only D35 and the offline archive closure report; preserve original Nov9 observations and receipts. |
| 2026-11-09 | Accept terminal H800 D34 capacity: two optimizer ACKs, two complete student scoring passes on every rank, and consistent updated text weights. |
| 2026-11-09 | Accept 256 valid D34 bank slots within 1633.3 seconds; keep optimizer/second-scoring checks pending. |
| 2026-11-09 | Inspect successful native engine initialization and initial synchronization; retain non-blocking native warning classification. |
| 2026-11-09 | Add fresh admission, actual submission and initial filtered platform Starting evidence; leave business checks pending. |
| 2026-11-09 | Record reviewed network correction, unchanged retry configuration, production dry-run checks and native acceptance limits. |

# Network-fixed H800 verification

Current integration status: parent D35 (Nov10) adopts this accepted H800 D34 result for parent D1/D22 and approves primary-owned merge/T02/T03, which remain pending. The contract cautions and pending labels in the dated Nov9 observations below describe that historical state; upstream old-D11 and original receipts are unchanged. Offline archive verification and terminal review remediation are recorded in `test_report_2026-11-10_h800_archive_close.md`.

## Scope and environment

Task: `task_2026-11-09_profile_h800_preparation`, Plan9 and the next Plan8 attempt. Worktree: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`. Local interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13. No GPU or external operation was performed by these prelaunch commands.

## Code acceptance

Commit`cf98293a2037c27899636df8f2a37a99058b38b5` removes head-inherited NCCL forwarding while retaining existing explicit job-wide controls. The code owner's exact commands, production-path RED/GREEN and final529passed/12skipped/1known-baseline parser case deselected are in`test_report_2026-11-09_node_local_network.md`. The primary inspected the code diff and decisive report; it did not rerun the529 checks.

Reviewer`profile-h800-node-network-review-20261109`, session`ses_e3ffdba19ffe6ry9e4fP59h2Sc`, inspected the complete immutable four-file diff`d91be845..cf98293a` at`/data/ycfeng/tmp/agent-opd-image/cf98293a-fixed-review.diff`: **Standards/Spec No Findings**, limited to static and recordedCPU evidence. Native engine environments and NCCL behavior were unverified at this prelaunch review; later native observations are recorded below.

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
| Native engine initialization and initial weights | Eight ready engines; successful eight-actor synchronization with complete session lifecycle | All eight ready; initial cell `ok=true`, 3.8 seconds; begin/end and tensor/distributed transfers HTTP200 | PASS |
| Bank admission | At least 231/256 valid samples within 1800 seconds | 256/256 valid; 1633.2862 seconds; no invalid/missing/pending slots | PASS |
| Training capacity | Two optimizer ACKs, second scoring, same bank used twice | Two successful ACKs, bank 0 visits 1/2, 256 trajectories each; eight ranks each complete two 88-microbatch student passes | PASS |

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

At11:33:03Z a separate local read of all five `*-node-*.json` receipts confirms36 actual H800 devices,81559MiB each, driver570.124.06. Student hosts are distinct, each with8 devices; the teacher has4. Each receipt's job, pair, image, model path and device count matches the frozen configuration. These validated records are retained in `evidence/h800-network-fixed-worker-gpu-readback-20261109.json`. At this observation, engine initialization, synchronization and capacity were still pending; later results follow.

## Native initialization and first synchronization, 11:39Z

The primary read only the current job's retained cloud head log through `ssh shai-ycfeng`, using `BatchMode=yes`, `ConnectTimeout=10`, a remote current-user check and `timeout 60s python3 -B -`. The exact remote file is `/mnt/ws-jfs/ycfeng/miles-qwen35-full-kl-nll/capacity-h800-112k-network-fixed-20261109/r256/student/A/exp-1109-192340-580111-rank-0.log`. Each query read at most 4 MiB and retained only selected startup/weight messages or traceback classifications; no GPU process, source file or cloud output was changed. The initial-sync capture at 11:39:09Z covers the complete 1,299,557-byte file, not a truncated tail.

| Native observation | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Engine initialization | Eight configured engines become ready | One ready message, five Ray-deduplicated ready messages, then the two colocated engines ready at 11:36:41Z | PASS |
| Initial eight-actor synchronization | Cell completes successfully, not at the 600-second deadline | Start 11:37:18.596Z; cell end 11:37:22.414Z, `ok=true`, `elapsed_s=3.8` | PASS |
| Mixed transfer/session lifecycle | Both transfer paths and all receivers' begin/end succeed | Tensor/distributed HTTP200; begin/end HTTP200, including seven additional receiver messages | PASS |
| Checksum event coverage | Eight receiver snapshots reported | `InferenceEngineWeightChecksumEvent`, `engine_snapshots=<list len=8>`, version 0 at 11:37:27.670Z | PASS for event coverage only |
| Changed weights and native capacity | Later weight version/consistency, accepted bank, two updates and second scoring | Not yet inspected or accepted | PENDING |

Evidence: `evidence/h800-network-fixed-initial-sync-20261109.json`. The successful first synchronization demonstrates native startup and mixed communication on this new allocation; it does not independently establish every final process environment, the original failed node's counterfactual behavior, snapshot-value consistency or later training capacity.

The startup log contains nine traceback headers from native post-warmup `/freeze_gc` connection-refused chains, including Ray-deduplicated messages. All captured headers were inspected in `evidence/h800-network-fixed-initial-warning-classification-20261109.json`. Servers subsequently report ready and initial synchronization succeeds. The warning is retained without a source patch, retry or stop; healthy training continues. Oversized input rejection records in `evidence/h800-network-fixed-first-runtime-20261109.json` establish active source preparation, not successful generated/scored slots. No accepted bank or optimizer ACK is inferred from them.

## Native bank admission, 12:06Z

The primary used the same bounded read-only SSH mechanism to stream `/mnt/ws-jfs/ycfeng/miles-qwen35-full-kl-nll/capacity-h800-112k-network-fixed-20261109/r256/student/A/exp-1109-192340-580111/training/bank_0.jsonl`. The snapshot reads only records up to the initial file size; a live incomplete trailing record would be marked partial, not used as a verdict. This snapshot has 258 complete records in 594,158,701 bytes and no incomplete trailing record. Sample bodies remain in the native journal and were not copied into the local summary.

Expected: at least 231 valid trajectories out of 256 fixed candidate slots, including teacher scoring/validation, within 1800 seconds. Actual: native `acquisition_sealed`, 256 completed, zero invalid/missing/pending, membership exactly 0–255. Start `1794224248.9532301`, deadline `1794226048.953265`, end `1794225882.2394156`: elapsed **1633.2862 seconds**, **PASS**. Every persisted native sample's `max_response_len` is 16384. No successful optimizer update, later weight version, or second scoring is inferred from this bank result.

Evidence: `evidence/h800-network-fixed-acquisition-progress-20261109.json`, retaining exact file path, SSH invocation, record counts and native timestamps. This independent D34 bank does not substitute for the upstream frozen D11 contract. The live smoke output stays protected from cleanup until terminal evidence is retained and verified.

## Terminal capacity acceptance, 12:41Z

The ordinary launcher exited successfully. The exact-job Python API reports job and all four student replicas plus the teacher replica **Succeeded**; UID and source identity match admission. Native `training/updates.jsonl` records two successful, unskipped optimizer updates at `1794226968.9307168` and `1794227779.6973712`. Both verify all 256 trajectories and 128547 original response tokens in bank 0, visits 1 and 2, under current student weight versions 0 and 1. Native mask and diagnostic verification also succeed. Learning rate remains 2e-6.

All eight `megatron_scoring_lifetime/observations/rank_*.jsonl` files contain student scoring passes 0 and 1, each with 88 distinct microbatch indices 0–87 and 88 forward-enter/projection-enter/forward-exit events. Their source identity is verified, no observer-unverified event occurs, and no previous full output remains alive at the 264 boundaries checked per pass. Pass 1 starts after the first optimizer ACK and completes before the second. The actual `[1, 131072, 62080]` bf16 logits storage is **16273899520 bytes = 15.15625 GiB/rank**, matching the TP4 projection. Maximum observed scoring PyTorch allocation is **28.89246 GiB**; this is neither whole-device usage nor a backward peak.

Existing native checksum events show 1644/1644 text parameter hashes equal across all eight engines at both versions; the same 972 text hashes change after the first optimizer update on every engine. The 1188 frozen `visual.*` hashes differ between two colocated and six dedicated engines but never change between versions. The existing recipe explicitly skips `visual` and uses verified non-visual inputs; this does not invalidate text-only equality. The reason for the colocated constant-fill signature remains an inference about pinned memory-saver internals, not a proven transport defect. `workers_hash=pseudo-hash-1` is not cryptographic publication provenance. Native server-info does not expose final process socket/HCA values: those values remain **UNVERIFIED**, despite successful communication. No warning or auxiliary comparison triggered a source change or job stop.

Evidence: `evidence/h800-network-fixed-{native-capacity-final,native-terminal,version-one-checksum-check,capacity-acceptance}-20261109.json`. Read-only inspection `profile-h800-unused-vision-checksums-20261109` confirmed existing text-only training and skip-list semantics. The primary's final local check parses the four evidence files, asserts five terminal replicas, both bank memberships and ACKs, ranks 0–7, complete passes and their ordering, source/lifetime verification and the existing text-only checksum result. **PASS_H800_D34_NATIVE_CAPACITY**. This does not accept or waive the separately frozen upstream D11/D1/D22 contract, implement profile hooks, or certify a 200-update formal run.

The exact offline check is retained for this fixed run, not installed as a live training gate:

```bash
python3 -B tests/manual/agent_opd/check_h800_capacity_evidence.py \
  task_memory/task_2026-11-09_profile_h800_preparation/evidence
```

Its fixed expected counts describe this archived run only; they are not workload defaults or a general admission policy.

## Post-run evidence retention and cleanup

After terminal acceptance, the exact smoke root contained 412 files and **2136889910 logical bytes**. A restricted local archive at `/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-192340-580111-cloud-raw.tar.gz` retains all files; its 458427717 bytes have SHA256 `1bda816ef0f16138c3376c947a2031f88eb92e046b860f4dfba185b02f8bd1c5`. All member lengths and hashes match the cloud inventory. The cloud contents were independently rehashed before any unlink. The exact root was removed at 12:50:11Z and a separate read confirms the task cloud parent is empty. Sources, other tasks and shared trash remain untouched; physical OSS reclamation is unmeasured.

The first archive-verification attempt incorrectly reopened a tar member in each block-read and raised `StreamError`; using one stream per member corrected the verifier without extracting or deleting data. Ordinary unlink then failed before the first removal because `student/A` was root:root mode 0755; all 412 files remained. The authorized exact-root operation used `sudo -n` after another complete hash check, without chmod/chown or broader deletion. Receipts: `evidence/cloud-cleanup-network-fixed-{inventory,backup,result}-20261109.json`. Full original journals and logs are now in the verified local archive; selected summaries remain in this task.
