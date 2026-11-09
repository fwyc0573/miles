## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record explicit personal50 authorization and existing-policy boundary verification;production/runtime source is unchanged. |
| 2026-11-09 | Record selected D13 A implementation, combined CPU verification, scoped configuration errors and remaining native/admission limits. |

# D13 A rollout expansion: CPU integration

## Outcome

CPU integration PASS:293 passed,20 skipped,1 deselected in58.29s. This does not establish native capacity, CUDA/NCCL mixed weight synchronization, or optimizer acceptance. No expanded GPU job has been submitted.

The selected profile uses two8-GPU student containers and one2-GPU teacher. Training remains one8-GPU node,TP2/DP4/CP1. Native inference uses sixteen GPUs in two pools:the first eight share training GPUs;the next eight are dedicated inference GPUs. Each pool has fourTP2 engines. Max running requests remains1;128K,n1,231/256 within1800s,two successful updates/two bank uses and the existing3600s generation-chain guard remain unchanged. Formal profiles and teacher input limits are unchanged.

## Deliverables

- `miles/utils/arguments.py`: omitted colocated rollout GPU count defaults to the training count; an explicit count is retained. Existing debug-train-only behavior is preserved.
- `miles/utils/args/configs/scaling.py` and `.claude/rules/launch-and-model-scripts.md`: synchronize the CLI help and canonical launcher guidance.
- `tests/manual/agent_opd/run_qwen35_opd.py` and `qwen35_pair_worker.py`: configured two-node startup,per-node preparation,rank0-only driver/global completion,peer supervision,and teacher-safe completion. Existing node-address and NCCL mechanisms are reused.
- `tests/manual/agent_opd/run_swe_opd.py`: transports native rollout count/config and student node count; moves the existing dependency preparation into `prepare_node`. Single-node source archives keep their existing path;two-node archives use `source/rank-{rank}`. No patch implementation is copied.
- `deepswe_capacity_expanded_config.json` and `deepswe_capacity_expanded_sglang.yaml`: A-only isolated configuration with explicit native `worker_type: regular` pools and the existing `default` model name.

Scoped RED/GREEN evidence and detailed commands remain in `test_report_2026-11-09_mixed_rollout_arguments.md` and `test_report_2026-11-09_two_node_student_worker.md`.

## Environment

Working directory:/data/ycfeng/sota-engine/miles,branch agent-opd. CPU Python:/data/ycfeng/envs/miles-agent-opd-cpu/bin/python3.12.13;pytest9.1.1,Torch2.11.0,Ray2.58.1,SGLang0.5.23. No dependency installation or GPU operation was used for these checks. Native worker image uses the existing pinned Python/SGLang environment;that environment still requires actual verification.

## Combined regression

```bash
TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q \
  tests/fast/test_swe_launcher.py tests/fast/test_qwen35_pair_worker.py \
  tests/fast/test_qwen35_opd_launcher.py tests/fast/test_qwen35_sample_lifecycle.py \
  tests/fast/test_qwen35_monitoring.py tests/fast/test_megatron_scoring_lifetime.py \
  tests/fast/backends/sglang_utils/test_sglang_config.py \
  -k 'not native_parser_accepts_sglang_and_custom_mis_flags' \
  --basetemp=/data/ycfeng/tmp/pytest-expanded-parent-verified \
  --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/d13-expanded-cpu-verified.xml \
  > /data/ycfeng/tmp/qwen35-swe-expanded-cpu-verified-20261109.log 2>&1
```

Expected:all selected,available CPU cases pass. Actual:293 PASS,20 SKIP,1 DESELECT;exit0. Skipped cases require missing Megatron/source conditions. The single deselection is the known localSGLang0.5.23 parser limitation for the unchanged `--sglang-enable-prefill-weight-versions` flag. This flag must be checked in the pinned0.5.24 native image;it was not removed or weakened.

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check \
  miles/utils/arguments.py miles/utils/args/configs/scaling.py \
  tests/manual/agent_opd/run_swe_opd.py tests/manual/agent_opd/run_qwen35_opd.py \
  tests/manual/agent_opd/qwen35_pair_worker.py tests/fast/test_swe_launcher.py \
  tests/fast/test_megatron_scoring_lifetime.py tests/fast/test_qwen35_pair_worker.py \
  tests/fast/backends/sglang_utils/test_sglang_config.py
```

Actual:PASS;existing top-levelRuff configuration deprecation remains unrelated.

## Iterations and limits

- The first parent regression exposed the old source-preflight fixture calling driver preparation directly. It now calls the actual per-node callback before driver preparation. Production patch behavior was not bypassed.
- One attempted parent command used nonexistent test filenames;zero tests ran. Evidence:`d13-expanded-cpu-green.xml`,raw log `/data/ycfeng/tmp/qwen35-swe-expanded-cpu-green-20261109.log`. That invocation is not a passing check.
- An unfiltered expanded regression found the known local parser limitation and sixteen monitoring fixture failures. The monitoring fixture omitted `gpu_tag`,although HEAD already required it for GPU identity checks. The fixture now supplies H200 explicitly;no production fallback was added. Owner verification:123 PASS in48.79s. Initial parent evidence:`d13-expanded-cpu-final.xml` and the matching raw log;final acceptance uses only `d13-expanded-cpu-verified.xml`.
- A direct native-YAML parse found missing mandatory `worker_type`;the new YAML was corrected through the existing native schema. A later temporary model-level graph getter assertion returned None,which is not evidence of the final effective global graph configuration. Geometry,engine count,concurrency and pool offload were observed before that assertion;the failed script is not counted as a complete PASS. Preserve `/data/ycfeng/tmp/qwen35-swe-expanded-native-layout-20261109.log` and `...-verified-20261109.log`. Actual engine graph settings remain a GPU readback requirement.
- Two diagnostic commands attempted unavailable local linter locations. The exact existingRuff command above passed;no package was installed.

## Remaining acceptance

1. Independent phase review of `evidence/d13-expansion-review-snapshot.diff` is complete:reviewer`ses_e411974f8ffet8IZR86PtH3Gkg` returns implementationGO/no actionableP1–P3 findings. Archived in `evidence/checkpoint_d13_expansion_preflight_review.md`.
2. Final fresh personal admission counts31 non-preemptible H200;plus18 requested equals49. OriginalD9's56 admits,but the applicable32 check denies. Evidence:`evidence/admission-deepswe-expanded-preflight-final-20261109.json`;raw command log:`/data/ycfeng/tmp/qwen35-swe-expanded-capacity-preflight-final-20261109.log`. The old64 window expired. No submitted job exists;do not stop unrelated jobs or substitute preemptible resources without approval.
3. On the single approved native attempt,verify creator,mounts,both containers' GPUs/source identities,eight actual engine registrations,concurrency/graph settings,and initial/subsequent mixed weight updates.
4. Verify231/256 within1800s,then original native scoring/backward,two optimizer acknowledgements,second scoring and HF exports using retained native tensors. Keep unsuccessful or missing stages explicitly unverified.

Acquisition allocation is at most9 GPU-hours (18 GPUs×0.5h),plus authorized startup and two-update cost. CPU success alone closes none of Ticket02's native capacity gates.

## User-resolved personal50 admission

After the31+18=49 hold,the user explicitly permitted `允许提高到50卡内` for the selected experiment. The candidate now points to `deepswe_capacity_expanded_gpu_policy.json`:the existing policy schema with personal50 and the original already-expired window metadata. CurrentUTC must select personal scope,include other tasks and keep preemptibleFalse. OriginalD9/formal files are unchanged. No admission code or new timeout implementation is added.

Existing budget regression:10 PASS,exit0.

```bash
TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q tests/fast/test_rjob_budget.py --basetemp=/data/ycfeng/tmp/pytest-d13-personal50 --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/d13-personal50-budget-regression.xml > /data/ycfeng/tmp/qwen35-swe-personal50-budget-regression-20261109.log 2>&1
```

Additional direct checks use the unchanged `policy_admission_snapshot` plus existing `_client`/`_job` fixtures from `tests/fast/test_rjob_budget.py`,with an other-personal-task row and awareUTC2026-11-09. Committed31+18=49 and32+18=50 admit;33+18=51 denies. All three retain personal scope,ceiling50 and preemptibleFalse. Evidence:`evidence/d13-personal50-boundaries.json`. A JSON comparison against52e84dea confirms the only candidate change is `gpu_policy`;the old expired timestamp is unchanged. Live admission remains to run under the existing submission lock.
