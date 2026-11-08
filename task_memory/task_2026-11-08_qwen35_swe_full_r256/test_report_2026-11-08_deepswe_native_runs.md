## Modification History

| Date | Change |
| --- | --- |
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

No runtime values, optimizer/HF outcomes or native SWE scores have been observed by this initial admission report. Formal04–07 remain gated on02/03 acceptance; original baseline08 continues independently.
