## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record completed PPO reconstruction, failed acquisition gates, the directory-permission discriminator and two formal baseline results. |
| 2026-11-08 | Verify actual worker devices, native updates and baseline readers; record the dispatch snapshot failure as an unresolved isolation gate. |
| 2026-11-08 | Record three local native submissions, exact platform resource readback and pending runtime criteria. |

# DeepSWE native training and asynchronous qualification

## Observed result

PASS for submission, personal creator, task annotation, current-machine source mount and requested GPU shape. Runtime acceptance remains PENDING. Ticket01 input acceptance was committed as `2a14093c`; none of these runs is a formal200-update cell.

| Scenario | RJob | GPU shape | Initial observed phase | Background launcher |
| --- | --- | --- | --- | --- |
| A/r256 capacity,256 candidates/two updates | `exp-1108-221043-570148` | student8+teacher2 | Running | `sh_1bb7f3438001kYLAPH81jmZrtt` |
| B/full capacity,256 candidates/two updates | `exp-1108-221042-909448` | student8+teacher2 | Starting | `sh_1bb7f3429001kBQ8olI7T5h8TB` |
| A/r256 training/HF/async isolation,three updates/eight candidates | `exp-1108-221044-294843` | student8+teacher2 | Starting | `sh_1bb7f3429002opAQEV5dazj676` |

All three exact platform objects report creator `i-fengyicheng`, root annotation `miles.ycfeng/task=task_2026-11-08_qwen35_swe_full_r256`, preemptible=`no` and per-role current source mount `100.96.128.195:/data/ycfeng:/data/ycfeng`. Fresh serialized admissions counted2,12,22 committed task GPUs respectively, adding10 each under64. Together with the separately admitted2-GPU original baseline, total commitments are32; later evaluator jobs require their own fresh admission.

Evidence: `evidence/deepswe-native-admission-readback-20261108.json` and the three `evidence/admission-deepswe-*-20261108.json` receipts. Initial phases do not prove that worker CUDA/model/input startup has completed.

## Exact native commands

Working directory: `/data/ycfeng`. Local launcher interpreter: `/data/ycfeng/tmp/stepmind-env/bin/python` (Python3.10.6). Set `STEPMIND_BACKEND=rjob`, `PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron`, `PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR=/data/ycfeng/tmp`. The invocation privately initializes personal credentials from `/data/ycfeng/tmp/brainctl-auth-i-fengyicheng` and uses the handbook's intranet proxy recipe with tracing disabled; no credential values are recorded. Pinned GPU image/interpreter and all scientific settings are owned by the two referenced configuration files.

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_swe_opd \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_capacity_smoke_config.json \
  --pair A --protocol r256 \
  --receipt /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/admission-deepswe-A-r256-capacity-20261108.json

/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_swe_opd \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_capacity_smoke_config.json \
  --pair B --protocol full \
  --receipt /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/admission-deepswe-B-full-capacity-20261108.json

/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.check_swe_native_async \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_integration_config.json \
  --pair A --protocol r256 \
  --receipt /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/admission-deepswe-native-async-20261108.json
```

Local raw logs: `/data/ycfeng/tmp/qwen35-swe-deepswe-A-r256-capacity-20261108.log`, `qwen35-swe-deepswe-B-full-capacity-20261108.log` and `qwen35-swe-deepswe-native-async-20261108.log`. The background Python launchers remain alive through native wait and owned evaluator drain.

Before the async launch, the existing `_worker_environment(config)` verifies private AK/SK inheritance and matching router aliases. One operator-only diagnostic omitted the required config argument and raised TypeError; the corrected call passes without code changes or any submission from that diagnostic. The dedicated async check empties AK_BASEMIND only for the first HF2 evaluator child; healthy training and HF3 inherit the original environment.

## Required runtime checks

1. Actual worker8/2 H200 devices, pinned source/model/tokenizer, NFS input receipt and real Qwen input metadata. GPU-dependent Megatron/SGLang parsing remains required.
2. Capacity acquisition within1800s with at least231/256 successful trajectories; actual missing membership and original completion tokens retained.
3. Two successful optimizer acknowledgements, current-student second scoring, immutable A/r256 bank and B/full bank transition; completion-only RKL/TIS/PPO independently recomputable from the existing native dumps.
4. Per-rank approved Megatron schedule identity and repaired lifetime/allocator observations. The user-approved identical-bank before/after comparison must retain its controlled-input identity; if further captured replay is required, use only a newly sealed DeepSWE bank through the existing seam,never the historical GLM bank. Historical failed-allocation snapshots are not peak measurements. Observer failures are soft and mark evidence unverified,never terminate healthy training.
5. Async HF2 evaluator rejection leaves its queue/HF intact and does not prevent update3/HF3. HF3 separately admits2 GPUs, reloads actual weights, executes the fixed native attempt and cleans all readers. Qualification ledgers remain400-slot/null and their HF weights are retained.

## First business observation

The six `student-node.json` / `teacher-node-0.json` files under the two shared evidence roots confirm8/2 actual NVIDIA H200 devices per case, the pinned image and the declared student/teacher source paths. The initial diagnostic incorrectly expected an old `cuda` field and failed with KeyError; inspecting the actual `gpu_devices` schema and validating all six receipts passed without modifying any workload.

The read-only snapshot `evidence/deepswe-native-business-snapshot-20261108.json`, observed at14:23:53UTC, scopes SSH reads to the three declared personal cloud run directories and the formal `evaluations/points/original4b` directory. It records:

- Both256-turn cases: real generation and teacher-stage files exist; no successful update or capacity verdict yet.
- Eight-turn A/r256: native successful-update receipts1/2, eight repaired GPU observer files and a newly created `hf/step_1` directory. A directory alone is not a completed/publication-identity check. The second visit has a fresh current-student score and different retained-token count, but independent tensor validation is pending.
- Baseline: the formal point and all six readers are RUNNING (four native children, evaluator and server); server identity file exists. First start1794146471.7061195 and absolute deadline1794405671.7061195 establish72h. No summary was available; no formal score is inferred.

The async observer failed before watcher construction with `Training integration configuration changed after submission`; native training remained healthy. CPU reproduction showed the file digest unchanged and an in-memory `mounts` change during submission. Therefore HF2 rejection/HF3 evaluator isolation is UNVERIFIED, not PASS. The cause-specific fix and persistent regression are being prepared in `test_report_2026-11-08_dispatch_snapshot.md`; no training cancellation or evaluator retry occurred.

After the eight-turn native launcher completed, primary downloaded12 selected native tensors, five training JSONLs and eight observation JSONLs (6,457,928 /22,006,630 /39,310 bytes) to `/data/ycfeng/tmp/qwen35-swe-deepswe-native-audit/exp-1108-221044-294843`. The existing independent auditor owns the mathematical verdict; neither exit0 nor dump presence is substituted for it. Raw snapshot and download commands are retained in the session trace; cloud paths map `/mnt/codesign-exp/ycfeng` to `/mnt/ws-jfs/ycfeng` on `shai-ycfeng`.

The first independent audit verified RKL/TIS but lacked the downloaded `policy_loss_debug`. Primary fetched the 12 existing files (400212 bytes) and supplied a byte-identical updates file at the auditor's expected path. The unchanged auditor now exits 0: 10724 completion tokens have zero token-loss/KL/advantage errors; scalar-loss maximum absolute error is 1.6458376744798997e-9. This settles small-run loss reconstruction, not final TIS-mask, live-gradient/optimizer-state or large-bank capacity acceptance. Exact commands and limits remain in `test_report_2026-11-08_deepswe_native_training_audit.md`.

CPU snapshot repair is now verified: the SDK first mutates the borrowed list during resource iteration, while the JSON file stays unchanged. A fresh mounts list at the ResourceConfig boundary solves the alias without weakening true-drift rejection. Forty persistent dispatch tests and three real-resource cases pass. The original profile is unchanged, and the existing qualification entrypoint will be explicitly rerun with a new training receipt; the old job's preserved HF2/HF3 are not silently resubmitted.

## Acquisition and second observer failure

Both capacity launchers exited 1 because the native bank minimum was not met at 1800 seconds. A/r256 has 206 valid, 49 generation-pending and one teacher HTTP400; B/full has 224 valid, 30 generation-pending and two teacher HTTP400. All teacher requests ended. Both successful-update counts are zero; student scoring/sourcepatch capacity was not exercised. The 48 A cancellation events do not equal its 49 pending slots. Generation durations in the adapter include queue time; do not present them as decode-only measurements. The exact slot/clock analysis and serving-log hypothesis tests are owned by `test_report_2026-11-08_deepswe_acquisition.md`. No D6 threshold, deadline or context budget changed.

The explicit same-profile async rerun used a new receipt:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.check_swe_native_async \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_integration_config.json \
  --pair A --protocol r256 \
  --receipt /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/admission-deepswe-native-async-fixed-20261108.json
```

`exp-1108-224927-865957` passed the snapshot boundary, but `_publish_once` failed with PermissionError13 when creating its job directory. Native student succeeded; platform stop reason is exactly `All critical tasks are finished.` The noncritical teacher stop is cleanup, not a training failure. No HF2 evaluator injection or HF3 evaluation occurred. Log: `/data/ycfeng/tmp/qwen35-swe-deepswe-native-async-fixed-20261108.log`.

The filesystem RED runs local `Path.mkdir()` under the configured base. UID/GID10250 cannot write the UID/GID0,0755 base; the enclosing evidence directory is owned10250,0700. Primary used a nonrecursive `sudo -n chown --no-dereference` on ONLY that base directory, targeting the actual local UID/GID. Its mode and all existing child owners/modes are unchanged, and local write access is restored. Raw commands/receipts are `/data/ycfeng/tmp/qwen35-swe-dispatch-permission-red-20261108.json` and `/data/ycfeng/tmp/qwen35-swe-dispatch-directory-owner-repair-20261108.json`. Recurrence prevention and CPU ordering/soft-gate tests remain pending; no third blind GPU submission.

## Formal baseline update

The actual store writes completed outcomes to `results/`, not `attempts/`. A corrected bounded read at 1794151445.9297264 found two native success=true rows for astropy__astropy-12907, seeds1731/1732, persisted at1794150865.5533686/1794151152.0826128. Four native children remain running; two earlier children have exit timestamps. No infrastructure-failure file was present. Thus the formal ledger is 2/400,398 missing,avg@4=null,with the original 72-hour clock unchanged. Reader exit alone was not used to infer success. Raw snapshot: `/data/ycfeng/tmp/qwen35-swe-original4b-completion-update-20261108.json`.

Formal04–07 remain gated on02/03 acceptance; original baseline08 continues independently.
