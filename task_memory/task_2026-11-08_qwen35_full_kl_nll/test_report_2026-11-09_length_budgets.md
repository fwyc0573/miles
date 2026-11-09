## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Verify D34 input/request/audit changes and prepare the in-place112K source audit. |

# Qwen3.5 length budgets

## Contract and environment

D34: training `seq_length` and rollout `max_seq_len`/context131072, inclusive rendered-prompt budget114688, completion cap16384. Over-budget prompts are skipped before consuming slots; messages are not truncated. The native request cap is `min(response_limit, context_limit - prompt_tokens)`.

Worktree:`/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`; Python:`/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`,3.12.13; torch2.11.0, transformers5.19.0, pytest9.1.1. No conda change. The isolated upstream-based launcher change is committed as`8c9537bf` on`agent-opd-h800-capacity`, following admission change`1ae93261`; parent integration remains gated.

## Commands and observed results

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/fast/test_swe_input_limits.py tests/fast/test_swe_input_pins.py \
  tests/fast/rollout/test_sample_max_response_len.py tests/fast/rollout/test_sglang_opd_request_contract.py
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B tests/manual/agent_opd/submit_swe1003_audit.py \
  --config task_memory/task_2026-11-08_qwen35_full_kl_nll/source_audit_config.json --dry-run
python3 tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll
git diff --check
```

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Affected fast suite | Adapter, native request and sample cap contracts hold |33 passed in3.09s; existing SWIG/torch deprecations and CPU-only quantization warnings | PASS |
| Inclusive prompt boundary |114688 accepted,114689 skipped without allocating a slot | Accepted source draws0/2, slots0/1; rejected draw still reported as finished | PASS |
| Completion and total limits | Short/boundary prompts capped at16384; boundary total131072 | Actual native payload has114688+16384=131072; short prompt also16384 | PASS |
| Native input checks under new budgets | Existing source order/render/mask/finish behavior preserved | GLM512 native parity+2048 interleaved; SWE synthetic30+12 | PASS |
| Audit threshold independent of context | A prompt within context but above prompt cap rejects | Synthetic1568-token prefix rejects against1500 prompt cap while total context is2000; one overlength turn, native mask/visual counts correct | PASS |
| Audit bisection | Equal112K accepted,112K+1 rejected | Three boundary sequences return expected first-overlength ordinals | PASS |
| Audit/parity workflow integration | Both commands receive three explicit budgets | Synthetic16 parity+16 interleaved PASS; real-source dry-run carries131072/114688/16384 in both argv | PASS |
| Documentation and diff | Links/DAG/arithmetic valid; no whitespace errors | Before this report:22 documents,75 links,22 anchors,zero errors; diff clean | PASS |
| New real-source audit | Actual112K statistics and terminal success | `exp-1109-154414-275606` Running at07:45:51Z; worker command carries all three approved limits | RUNNING, NOT ACCEPTED |

Durable receipts with exact CLI argv:

- `evidence/length-budget-glm-parity-20261109.json`
- `evidence/length-budget-swe-synthetic-parity-20261109.json`
- `evidence/length-budget-audit-synthetic-20261109.json` (includes synthetic audit and checker commands).

The audit agent's first cumulative verification command exceeded60 seconds; the same independent checks passed in one imported process under a120-second envelope. No runtime workaround was added. The synthetic receipt's outstanding old-D5-table note was subsequently fixed in`spec.md`.

## Runtime verification limits

The input and native request path is CPU-verified. The launcher's explicit `prompt_tokens` and `response_tokens` contract is separately verified by53 launcher tests and7 related tests in the isolated preparation worktree; see its`test_report_2026-11-09_native_launch_lengths.md`. These results do not prove a live H800 training run or replace the D1/D22 native capacity gate.

Prior audit output`evidence/source-audit-20261109/` remains the accepted pre-D34 source evidence at commit`2d695ba0`; its128K prompt-rejection and span statistics do not apply to112K. Updated`source_audit_config.json` writes only to`evidence/source-audit-112k-20261109/`, with separate temporary storage. Source files continue to be read in place from posttrain.

## Submitted112K audit

After committing the verified input/audit code as`438d25fc`, the primary submitted the existing CPU workflow using personal StepMind authentication and the runbook proxy setup:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/tests/manual/agent_opd/submit_swe1003_audit.py \
  --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/source_audit_config.json
```

Environment:`STEPMIND_BACKEND=rjob`, `PYTHONPATH=/data/ycfeng/steptron`, `PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, local mount cwd`/data/ycfeng`. The local launcher remains alive as`sh_1bf43bd8e0011S3o8uZqd0btZi`; raw log:`/data/ycfeng/tmp/agent-opd-image/source-audit-112k-launch-20261109.log`.

Filtered receipt`evidence/source-audit-112k-admission-20261109.json` confirms creator`i-fengyicheng`,8 CPU,32000Mi,0 GPU, pinned image, local NFS source`100.96.128.195:/data/ycfeng:/data/ycfeng`, codesign/posttrain volume mounts and worker startup withPython3.12.13/torch2.11.0+cu130/transformers5.19.0. Startup argv binds131072/114688/16384 and the new output directory. This verifies submission/startup only; completion, business outputs and final parity remain pending.
