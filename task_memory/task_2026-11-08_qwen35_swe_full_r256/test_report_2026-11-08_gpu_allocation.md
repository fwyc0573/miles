## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Validate the D9 task allocation amendment, native SDK preemption labels, real task GPU accounting, and the remaining native-startup failure. |

# GPU allocation amendment and native startup verification

## Scope and observed result

The amended resource policy is implemented in `gpu_policy.json` and `tests/manual/agent_opd/rjob_budget.py`. The paired submitter selects `ResourceConfig.preemptible` from a fresh policy receipt under the shared admission lock. The evaluation store validates a matching job, requested GPU count, task identity, creator and hardware against its own configuration.

**Resource policy: PASS.** An actual one-H200 RJob was admitted under the task-scoped window and immediately appeared as one Pending GPU in the independent task ledger. **Native training startup: still FAIL / owned by T02.** The four actual Megatron parser cases succeeded, but the native driver configuration lacked `custom_reward_post_process_path`; no actor or optimizer update was started.

## CPU commands and results

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python 3.12.13, pytest 9.1.1, Linux. Commands ran from `/data/ycfeng/sota-engine/miles`.

```bash
env PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_rjob_budget.py tests/fast/test_swe_launcher.py -q
env PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_evaluation.py -k resource_admission -q
env PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_evaluation.py -q
```

| Check | Expected | Observed |
| --- | --- | --- |
| Task accounting and launch boundaries | Other tasks excluded inside window; all own nonterminal roles counted; exactly full budget remains non-preemptible; excess becomes preemptible | 18 PASS, 0.36s |
| Expiry and API-read boundary | Exact expiry restores personal ceiling; a read crossing expiry rechecks the personal inventory | Included in the 18 passing tests |
| Evaluation GPU admission | Invalid count/ceiling rejected before evaluation | 2 PASS, 0.48s |
| Evaluation lifecycle after policy integration | Deadline/recovery/readers/release retain their existing behavior | 29 PASS, 144.36s; raw log `/data/ycfeng/tmp/qwen35-swe-gpu-policy-evaluation-tests.log` |

After the focused policy review, receipt validation was additionally bound to the configured task/creator/hardware. The affected combined regression is recorded below when complete:

```bash
env TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_rjob_budget.py tests/fast/test_swe_launcher.py tests/fast/test_swe_evaluation.py tests/fast/test_swe_hf_export.py tests/fast/test_swe_native_evaluation.py -q
```

Final result: **92 PASS, 157.75s**. This includes receipt task/creator/hardware binding and the revised HF bridge/evaluation constructors. Raw log: `/data/ycfeng/tmp/qwen35-swe-gpu-policy-final-tests.log`.

Ruff 0.14.7 and isort 5.13.2 passed on the nine changed Python files in the policy, submitter, evaluation interface and tests. The local CPU environment does not install Ruff as a Python module; verification used the already installed tool binaries, without changing dependencies:

```text
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/8QpD66osZqn5M69v/ruff-0.14.7.data/scripts/ruff
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/YeSQ9F0UbXV9REOw/bin/isort
```

## Native SDK preemption propagation

`evidence/preemption-sdk-serialization.json` records execution with installed `brainpp==2.8.6`. Native `Job(..., Spec(preemptible=..., tasks={})).to_k8s_template(...)` writes the preemption flag into **root RJob metadata labels**, not just pod labels. Both `no` and `yes` preserve the task annotation; the admission counter charges a two-GPU fixture as 2 and 0 non-preemptible GPUs respectively.

The namespace accessor was stubbed to `cpu-fixture`, and the GPU request was a fixture. This was native SDK serialization, not a submitted preemptible workload. The decisive installed code is `brainpp/rjob/struct.py:1427–1478`: `job_labels()` produces the preemption label and `to_k8s_template()` attaches it to root metadata. The actual submitted non-preemptible RJob below supplies the independent platform observation.

## Actual RJob

Job: `exp-1108-164121-488177`; creator: `i-fengyicheng`; local mount source: `100.96.128.195:/data/ycfeng:/data/ycfeng`.

Submission used local StepMind Python `RJobBackend`, the shared `policy_admission_snapshot()`/admission lock, `ResourceConfig(cpu=8, gpu=1, mem_gb=64, replica=1)`, `charged_group=step_main`, the configured company image and mounts, and the policy-selected `preemptible=False`. `ResourceConfig.annotations` included the exact task identity and local filestore mount. The launcher stayed alive in `workers.wait()` until the worker ended.

Worker environment matched the actual launch environment: repository plus `/root/Megatron-LM` on `PYTHONPATH`, `MEGATRON_PATH=/root/Megatron-LM`, `/usr/local/cuda-13.0/compat` on `LD_LIBRARY_PATH`, offline Hugging Face, one OpenMP thread, and worker-local `/var/tmp/swe-launch-config-<job>` temporary storage. The check builds the real `ExecuteTrainConfig`/`ExecuteTrainRequest` and applies `train_env_vars`, including `CUDA_DEVICE_MAX_CONNECTIONS=1`.

Exact business command:

```bash
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.check_swe_launch --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/integration_config.json --report /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/native-launch-config-exp-1108-164121-488177.json
```

| Observation | Evidence |
| --- | --- |
| Admitted in the task window with the new task annotation | `evidence/native-config-admission-exp-1108-164121-488177.json` |
| Native API immediately counted exactly this job, Pending, one GPU; other tasks excluded | `evidence/native-config-task-accounting-exp-1108-164121-488177.json` |
| Actual worker GPU | `evidence/native-launch-config-exp-1108-164121-488177-gpu.txt`: NVIDIA H200, 143771 MiB |
| Python/Torch/SGLang | Python 3.12.16; torch 2.14.1+cu130; transformers 5.19.0; SGLang 0.5.24.dev80+g056f871 |
| Four parser cases reached the driver | `evidence/native-launch-config-exp-1108-164121-488177.json` and `.log` |
| Terminal failure before training | `/data/ycfeng/tmp/qwen35-swe-native-config-task-window-20261108.log`: native controller reports `failed` |

All four cases failed at `swe_replay.py:436` with `AttributeError: 'ImmutableNamespace' object has no attribute 'custom_reward_post_process_path'`. T02 owner received this exact evidence and the requirement to test the real typed orchestrator/hook view on CPU before another GPU check. This is not a quota failure, and no successful update or benchmark score is inferred from it.

## Focused review and dispositions

Read-only reviewer: D9-POLICY-CHECK, `ses_e45ad032dffe2SFPEGFdK06QqA`.

1. **SDK preemption propagation gap:** closed by the native serialization evidence above; root labels are authoritative in the installed SDK.
2. **Receipt identity binding:** fixed by requiring the evaluation configuration's task ID, creator and GPU tag, in addition to job/resource/policy consistency.
3. **Unknown hardware handling:** retained explicit classification. Current supported tasks use the known registry; treating an unknown non-empty tag set as zero could hide H200 commitments. No actual unsupported-hardware inventory failure was observed.
4. **Stale resource/status text:** summary and review now distinguish the earlier frozen policy from the approved S7 amendment.

The historical Qwen submitter is used by a separate task and cannot consume this task's configuration. Its independent entrypoint is not an alternative submission path for this experiment.

## Remaining acceptance

T02 still needs the corrected native startup path and real four-configuration training/KL/TIS checks. T03 still needs real HF reload, SWE agent/grader execution and reader-safe release. No formal cell or shared benchmark baseline has been run under this report.
