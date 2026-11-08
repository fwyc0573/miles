## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record the typed-view repair and targeted native GPU recheck; distinguish the completed CPU bridge from native acceptance. |
| 2026-11-08 | Record launch/admission checks, the CPU SGLang mismatch and the pending pinned-image rerun. |

# SWE launch and admission integration

## Scope and current outcome

Parent-owned integration for Tickets 01–03 and subsequent cell admission. The new worker composes the native SWE input/replay/TIS plugins while reusing the existing Qwen paired-worker, Ray, export and process cleanup mechanisms. It has not yet run GPU training or benchmark attempts.

The qualification profile is [integration_config.json](integration_config.json): its reduced update/bank budgets exercise protocol mechanics. These budgets are not formal-cell budgets. The selected `swe_hf_export.post_save` hook now packages smoke HF and records native identity; it intentionally does not create a formal benchmark point for a shortened smoke.

## Local regression — 84 PASS, 12 SKIP, 1 FAIL_ENV

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python 3.12.13, pytest 9.1.1, SGLang 0.5.23. From the Miles repository:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_rjob_budget.py \
  tests/fast/test_qwen35_pair_worker.py \
  tests/fast/test_qwen35_opd_launcher.py -q
```

Observed: 97 collected, 84 passed, 12 skipped, one failure, 13.93 seconds. The new admission tests passed all four cases: nonterminal role/replica commitments, init-container requests, hardware classification, paginated listing and the exact admission boundary.

The failing existing test is `test_native_parser_accepts_sglang_and_custom_mis_flags`:

```text
Extra items in the left set:
'--sglang-enable-prefill-weight-versions'
```

The installed CPU SGLang does not register the existing flag. An AST comparison of `run_qwen35_opd._training_args` against `git show HEAD:tests/manual/agent_opd/run_qwen35_opd.py` confirmed the entire legacy training-argv function is unchanged. The flag was retained; no assertion was weakened. The required pinned-image verification below remains pending.

## Native custom configuration parsing — PASS

Directly composed `_training_args` from the actual integration JSON for A/r256, set `sys.argv`, and ran `get_miles_extra_args_provider()(ArgumentParser())` followed by `parse_known_args`.

Observed parsed configuration includes the real source root/manifest/loader hash, cell `A/r256`, teacher 27B, eight slots, two bank uses, three successful updates, 131072 context and the approved answer TIS thresholds. No `--swe-*` or `--tis-*` flag remained unrecognized. Remaining flags were Megatron-owned fields and the SGLang extension above. The configured native loader SHA256 matched the file bytes.

This checks argument registration, not GPU execution, source consumption or numerical correctness. Parent separately flagged the adapter's nonexistent native `args.max_seq_len` field to T01; that integration fix belongs to T01 acceptance.

## Four submitter CLI dry-runs — PASS

Executed the following for each pair A/B and protocol full/r256:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.submit_swe_opd \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/integration_config.json \
  --pair A --protocol full \
  --receipt /data/ycfeng/tmp/swe-dry-run-unused.json --dry-run
```

Passing conditions and observed results: all four report `submitted=false`; each requests 10 GPUs across independently allocated student/teacher roles; only the student is critical; the actual shell command forwards the new module, selected protocol and `QWEN35_ROLE`. The dry-run receipt path was not created. Full command/result records: [evidence/launch-dry-runs.json](evidence/launch-dry-runs.json).

## Live personal admission query — PASS, no submission

Environment: local handbook personal auth, Python 3.10.6 in `/data/ycfeng/tmp/stepmind-env`; repository plus Steptron on `PYTHONPATH`. The actual Python client call was:

```python
from tests.manual.agent_opd.rjob_budget import admission_snapshot
from steptron.utils.stepmind import get_rjob_client
result = admission_snapshot(
    get_rjob_client(), creator="i-fengyicheng", gpu_tag="H200",
    requested_gpus=10, ceiling=56, timeout=20,
)
```

Observed at 2026-11-08T07:09:37Z: 20 committed non-preemptible H200 GPUs; 20 + 10 <= 56, `admitted=true`, `submitted=false`. Filtered exact job/role counts: [evidence/budget-live-20261108T070937Z.json](evidence/budget-live-20261108T070937Z.json). This is a snapshot, not a resource reservation; the submitter repeats it under its admission lock immediately before submission.

The initial invocation imported StepMind first and failed before querying with `ModuleNotFoundError: No module named 'tests.manual'`. `find_spec('tests')` demonstrated that StepMind prepends `third_party/super_agent/tests`, shadowing Miles' package. Importing the Miles module first resolved the collision. The new `python -m` submitter already uses this order; no environment/package change was needed.

## Pinned-image regression — PASS; native launch contract pending

Submitted through local `spawn_tasks` with `STEPMIND_BACKEND=rjob`, personal auth and the configured image/mounts. ResourceConfig: 8 CPU, zero GPU, 64 GB, one replica, H200 tag, `step_main`, non-preemptible. The launcher remains alive through `workers.wait()`.

Worker command, with repository `/data/ycfeng/sota-engine/miles` on `PYTHONPATH`:

```bash
/opt/sglang/bin/python3 -B -m pytest \
  /data/ycfeng/sota-engine/miles/tests/fast/test_rjob_budget.py \
  /data/ycfeng/sota-engine/miles/tests/fast/test_qwen35_pair_worker.py \
  /data/ycfeng/sota-engine/miles/tests/fast/test_qwen35_opd_launcher.py -q -rs \
  --junitxml="$EVIDENCE/launch-checks-$KUBEBRAIN_RJOB_NAME.xml" \
  > "$EVIDENCE/launch-checks-$KUBEBRAIN_RJOB_NAME.log" 2>&1
```

`EVIDENCE` denotes this task's `evidence/` directory. Raw launcher log: `/data/ycfeng/tmp/qwen35-swe-launch-checks-20261108.log`.

Job `exp-1108-151053-428999` failed at collection, before executing tests. Actual Python 3.12.16 / pytest 9.2.0. The import chain was SGLang dumper → Megatron → TransformerEngine → `ctypes.CDLL`, ending with `OSError: libcuda.so.1: cannot open shared object file`. Exact log/XML: `evidence/launch-checks-exp-1108-151053-428999.{log,xml}`.

Diagnosis: the auxiliary test command omitted the production submitter's configured `cuda_compat_dir` from `LD_LIBRARY_PATH`. This is an already documented environment requirement, not a new compatibility shim: see the historical task's `test_report_2026-11-07_native_prerequisites.md:46,554–591` and `test_report_2026-11-07_baseline_actor_fixture.md:90` (93 tests passed in the pinned zero-GPU environment). The next run prepends `integration_config.json`'s `cuda_compat_dir` exactly as `submit_qwen35._worker_command` does. Expected discriminator: collection proceeds past TransformerEngine and the existing SGLang extension flag is registered. No code fallback or skipped assertion is added.

The corrected compatibility-library run `exp-1108-152925-862947` passed92 tests and hit12 existing scheduler-fixture setup errors. Those fixtures require explicit `MEGATRON_PATH`; namespace-package discovery otherwise selected site-packages rather than the actual native source. The next run used both the configured source path and its normal PYTHONPATH.

`exp-1108-153652-994118`: **104 passed,0 skipped,0 errors/failures,11.580 seconds**, including the previously failing SGLang flag and native scheduler cases. Exact results: `evidence/launch-checks-exp-1108-153652-994118.{xml,log}`. Environment: Python3.12.16, Torch2.14.1+cu130, Transformers5.19.0, SGLang0.5.24.dev80+g056f871. Original image and local mount were verified through the Python platform client in `evidence/launch-check-terminal.json`.

The same job's subsequent full native configuration check failed on all four cases because Megatron's `get_device_arch_version()` reads a real CUDA device. Thus the platform job correctly ended Failed even though all104 pytest cases passed. This is not a training/configuration PASS. The exact trace is in `evidence/native-launch-config-exp-1108-153652-994118.json`.

## Actual native launch contract — historical admission block, current recheck

The dedicated1-H200 job `exp-1108-154045-807505` reached Megatron's next native environment check and failed because the standalone checker had not applied production `train_env_vars`: TP/CP requires `CUDA_DEVICE_MAX_CONNECTIONS=1`. Its GPU receipt and four actual error traces are retained under `evidence/native-launch-config-exp-1108-154045-807505*`.

Correction: `check_swe_launch.py` now reuses `ExecuteTrainConfig`, `ExecuteTrainRequest`, `train_env_vars` and the original Qwen `_runtime_env`, rather than recreating production defaults one variable at a time. It uses the exact `OrchestratorConfig.slice_from(parse_args())` view before calling the optimizer-hook driver factory. No CUDA monkeypatch or weakened assertion is used.

The next1-GPU check was **not submitted**: at2026-11-08T07:55:08Z the personal non-preemptible H200 commitment was72, so72+1 exceeded the approved56 ceiling. Exact receipt: `evidence/native-config-admission-denied.json`; local command exited2. The new56-GPU job's native label was independently confirmed as `preemptible=no` (6×8 training plus1×8 inference). Other jobs were not altered.

Pending acceptance: four real native parser/driver cases with the complete environment, subsequent Qwen training, capacity/throughput and HF/evaluation lifecycle. Resume only under the authorized resource ceiling.

The subsequent explicit D9 amendment removed that resource block. The actual one-H200 check `exp-1108-164121-488177` passed Megatron argument parsing in all four cells, then exposed missing fields in the production orchestrator/custom-function view. T02 moved `custom_reward_post_process_path` and `opd_log_prob_top_k` to their existing shared configuration owners. Six lifecycle views were audited, 16 typed-path tests passed, the complete SWE tests passed 52, and native regressions passed 86. The two locally unavailable parser-backed tests are retained as environment-unverified, not skipped or mocked. Details: [test_report_2026-11-08_replay_training.md](test_report_2026-11-08_replay_training.md).

The targeted GPU recheck uses the same pinned image, one H200, eight CPU, 64 GB, local NFS, personal Python RJobBackend and the active task policy/annotation. Raw launcher command/result: `/data/ycfeng/tmp/qwen35-swe-native-config-fixed-20261108.log`. Worker environment is composed from the existing `megatron_path`, `cuda_compat_dir` and worker-local temporary path. Commands:

```bash
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.check_swe_launch \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/integration_config.json \
  --report "$EVIDENCE/native-launch-config-$KUBEBRAIN_RJOB_NAME.json"
CUDA_DEVICE_MAX_CONNECTIONS=1 /opt/sglang/bin/python3 -B -m pytest \
  /data/ycfeng/sota-engine/miles/tests/fast/utils/args/test_custom_view.py -q -rs \
  --junitxml="$EVIDENCE/native-custom-view-$KUBEBRAIN_RJOB_NAME.xml"
```

Expected: all four production driver factories pass, followed by the real parser-backed custom-view cases; no actors or training run in this check. **Actual PASS:** job `exp-1108-172044-476666` completed Succeeded; all four A/B × full/r256 factories passed with the actual smoke budget, dynamic partial scheduling and context intact. All 10 custom-view tests passed in 12.12 seconds, including the two previously unavailable parser-backed tests. Worker: NVIDIA H200, 143771 MiB; Python 3.12.16, Torch 2.14.1+cu130, Transformers 5.19.0, SGLang 0.5.24.dev80+g056f871. Receipts: `evidence/native-launch-config-exp-1108-172044-476666.json`, `evidence/native-custom-view-exp-1108-172044-476666.xml`, the matching GPU text and admission JSON. This settles startup configuration, not actual optimization or benchmark acceptance.

## Remaining acceptance

- T01 is accepted in `20d0b3f4`; launch review findings are corrected and 104 pinned-image tests passed.
- Inspect the new native configuration check, then execute actual Qwen training for both teachers and both protocols.
- Complete T02/T03 GPU/benchmark acceptance before formal-cell admission. The current launch profile does not establish 256-turn throughput, distributed loss correctness, or asynchronous HF/eval/delete readiness.
