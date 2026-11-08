## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Verify D11 source selection, native evaluation configuration construction and the existing async smoke submission dry-run. |

# DeepSWE configuration verification

## Scope and result

PASS for configuration construction and source-selection binding. Native input parity, benchmark overlap and new-data GPU acceptance remain pending with their respective owners; this report does not close Ticket01, 02 or 03.

- `deepswe_integration_config.json` selects the eight D11 files and a new `deepswe-0913/integration` output namespace. Historical configurations and outputs retain their original source selection.
- The three-update/eight-slot profile enables the approved scoring-lifetime patch for qualification. It does not authorize formal adoption before capacity acceptance.
- `evaluation_deepswe_async_inputs.json` and the generated `evaluation_deepswe_async_config.json` use the existing 100-task manifest and one explicit qualification slot. The existing async check will reject the first HF2 evaluator before submission by clearing only that child's AK variable, then dispatch HF3 normally. No such GPU run was submitted by the checks below.

## Source identity observations

Zero-GPU job `exp-1108-205005-924420` returned Succeeded. Its source-stream SHA256 was independently compared with both the local and personal-cloud copies for all eight files, totaling **16,559,540,463 bytes**.

- Selection: `evidence/deepswe-source-selection.json`.
- Copy receipt: `evidence/deepswe-source-copy-exp-1108-205005-924420.json`.
- Local manifest: `/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420/COPY_COMPLETE.json`.
- Manifest SHA256: `c23a757918031592f6440cd50f0ca750f5de07da5590e98c55eb6b5760f7f73d`.
- Cloud copies: `/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/inputs/deepswe-0913/exp-1108-205005-924420/`.
- Copy worker log: `evidence/deepswe-source-copy-worker.log`; launcher log: `/data/ycfeng/tmp/qwen35-swe-deepswe-sources-20261108.log`.

These establish byte identity and order, not semantic loader parity or absence of benchmark overlap.

## Native configuration construction

Working directory: `/data/ycfeng/sota-engine/miles`. Native interpreter: Python 3.10.20. Exact successful command:

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/tmp/qwen35-swe-full-r256/swe-agents-1af09e5f-native/src:/data/ycfeng/steptron/.worktrees/step3p6-replay-v1:/data/ycfeng/steptron/third_party/step_align:/data/ycfeng/steptron/third_party/harbor/src \
  TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  LOGURU_DIAGNOSE=NO OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES= WORLD_SIZE=1 \
  timeout 60s /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/.venv/br-native-swe-py310-1008am/environment/bin/python \
  -B -m tests.manual.agent_opd.swe_evaluation_config \
  --inputs /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evaluation_deepswe_async_inputs.json \
  --output /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evaluation_deepswe_async_config.json \
  > /data/ycfeng/tmp/qwen35-swe-deepswe-async-config-absolute-20261108.log 2>&1
```

Expected: native source/input hashes and inherited harness contract agree, the output is created once, and dispatch uses absolute local paths. Actual: exit0; 100 frozen task IDs and the requested qualification slot are present. The generated file is an immutable input, so do not rerun this command over it.

Initial operator invocation used a relative `--output` and was rejected before writing: `ValueError: Dispatch paths must be absolute local workspace paths, not cloud paths`. Original error retained at `/data/ycfeng/tmp/qwen35-swe-deepswe-async-config-20261108.log`. The correction changed only the caller's path spelling; no validation was weakened.

## Existing submission dry-run

Working directory: `/data/ycfeng`. No authentication or platform operation is performed by this dry-run.

```bash
env PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron \
  PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp \
  timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -B \
  -m tests.manual.agent_opd.check_swe_native_async \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_integration_config.json \
  --pair A --protocol r256 \
  --receipt /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/admission-deepswe-async-20261108.json \
  --dry-run > /data/ycfeng/tmp/qwen35-swe-deepswe-async-dry-run-20261108.log 2>&1
```

Expected and actual: exit0 through the real smoke configuration, path, slot and worker-command checks, without job submission. This is not Megatron execution or an evaluation outcome.

## Structural checks

A Python 3.10.6 inline assertion check passed: the copy receipt is COMPLETE, its ordered eight paths exactly match the selected delivery list, its byte sum matches the value above, the configured source root matches the receipt, both pairs and TIS values equal the previous qualified profile, and training settings differ only by the explicitly approved lifetime-patch switch. It also checked the qualification owned-root/model-image binding, 100-task/one-slot selection and maintained-document headers/local links for ten changed task documents.

The active runtime profile remains a smoke. Formal200-update execution still requires Ticket01 replacement acceptance and the remaining native02/03 gates.
