## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Record subsequent D8 acceptance without changing the earlier CPU findings or collection-failure status. |
| 2026-11-06 | Trace current TIS diagnostics and token normalization, run a standalone CPU MIS example, and record the blocked pytest attempt. |

# Loss and numerical-metric semantics inspection

## Scope and environment

This report supports P1's numerical acceptance decision after D7 fixed the context budget. No production code, model weights, GPU jobs or cloud artifacts were changed. The user subsequently accepted the numerical rule under D8 in requirements; the evidence in this report does not itself grant that approval or establish runtime success.

- Repository: `/data/ycfeng/sota-engine/miles`, branch `agent-opd`, HEAD `9df78a8742e8f8a4a51dfeccddbf42127d419a4d`.
- Python: `/data/ycfeng/envs/openmopd-py312/bin/python`, 3.12.13.
- Libraries observed: torch `2.8.0+cu128`, pydantic `2.13.5`. The probe used CPU tensors only.
- Reference: [handbook consistency analysis](/data/ycfeng/stepfun-env-handbook/resource_analysis/opd-train-inference-consistency.md), inspected as local evidence. Its 0.03 value is a proposed discussion point, not a universal standard.

## Source findings

| Owner | Observed behavior | Consequence and verification limit |
| --- | --- | --- |
| [policy loss](/data/ycfeng/sota-engine/miles/miles/backends/training_utils/loss/hub/losses.py:233) | TIS replaces the response masks used by the loss reducer. Native `train_rollout_logprob_abs_diff` and `train_rollout_kl` subsequently use that reducer. Custom mismatch metrics retain the original reducer. | Native metric names alone do not establish pre-TIS coverage. Inspect each numerator and denominator. |
| [MIS](/data/ycfeng/sota-engine/miles/examples/infra_features/train_infer_mismatch_helper/mis.py:166) | Token mask mode retains ratios within the configured inclusive interval; the CP wrapper multiplies policy loss by IS weights and applies returned masks. PPL/K3 metrics are computed before filtering. | The CPU example below verifies this function's mask behavior. Task TIS mode, bounds and optional sequence rejection still need configuration decisions; the probe does not approve them. |
| [token reduction](/data/ycfeng/sota-engine/miles/miles/backends/training_utils/data/context_parallel.py:247) and [loss objective](/data/ycfeng/sota-engine/miles/miles/backends/training_utils/loss/objective.py:129) | Per-token reduction sums masked contributions. The objective counts original-mask tokens before TIS and returns the count for Megatron normalization; a completely masked sample counts as one. | Current inspected semantics use the original-token denominator. Global DP/CP/microbatch normalization and zero-target handling remain native verification items. |
| [debug dump](/data/ycfeng/sota-engine/miles/miles/backends/training_utils/metrics/debug_dump.py:13) | The pre-TIS dump retains current-forward, old trainer and rollout logprobs, original local masks, rank/call identifiers and finite checks. TP ranks other than zero do not write duplicate loss dumps. | Reuse this evidence mechanism. Actual version binding and complete CP reconstruction must be demonstrated in the selected run. |
| [existing normalization tests](/data/ycfeng/sota-engine/miles/tests/fast/backends/training_utils/loss/hub/test_backend_loss_normalization.py) | Tests cover backend token mode, TIS and scaling with uneven response lengths. A separate strict xfail records single-response-token concatenation losing its token dimension. | The suite did not collect in the local environment below. The known one-token case is a P2 investigation item, not a newly reproduced GPU failure or a general Qwen architecture gap. |

Native diagnostic sanitization can replace nonfinite values with zeros. Acceptance must independently report nonfinite/missing raw values and must not interpret sanitized zeros as agreement. Zero prefix target loss and completion-only supervision remain D6; normalization does not change target positions.

## Standalone CPU check — PASS

Exact command:

```sh
timeout 30s /data/ycfeng/envs/openmopd-py312/bin/python - <<'PY'
from types import SimpleNamespace
import json
import torch
from examples.infra_features.train_infer_mismatch_helper.mis import MisConfig, compute_mis_weights
args=SimpleNamespace(**MisConfig(tis_level='token', tis_mode='mask', tis_lower_bound=0.5, tis_upper_bound=2.0).model_dump(), use_tis=True)
rollout=torch.tensor([-2., -2., -2.],dtype=torch.float64)
train=rollout+torch.tensor([.01,.02,1.],dtype=torch.float64)
original=torch.ones(3,dtype=torch.float64)
weights,masks,metrics=compute_mis_weights(args,train_log_probs=[train],rollout_log_probs=[rollout],loss_masks=[original])
assert masks[0].tolist()==[1.,1.,0.]
d=(train-rollout).abs()
pre=(d*original).sum()/original.sum()
post_original=(d*masks[0]).sum()/original.sum()
post_survivor=(d*masks[0]).sum()/masks[0].sum()
assert abs(pre.item()-1.03/3)<1e-12
assert abs(post_original.item()-.01)<1e-12
assert abs(post_survivor.item()-.015)<1e-12
print(json.dumps({'torch':torch.__version__,'pre_tis_tokens':3,'retained_tokens':2,'rejection_mask':masks[0].tolist(),'pre_tis_mae':pre.item(),'filtered_sum_over_original_count':post_original.item(),'filtered_sum_over_survivor_count':post_survivor.item(),'scope':'actual CPU MIS function plus explicit arithmetic; no native distributed loss or model execution'},indent=2))
PY
```

Exit status: `0`. Inputs are constructed numbers, not actual model outputs. The MIS function ran directly; the following ratios of sums are explicit probe arithmetic, not a full native loss invocation.

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Three-token rejection mask | `[1, 1, 0]` | `[1.0, 1.0, 0.0]` | PASS |
| Original population mean absolute error | `1.03 / 3` | `0.3433333333333333` | PASS |
| Filtered error sum / original token count | `0.03 / 3` | `0.010000000000000009` | PASS |
| Filtered error sum / retained token count | `0.03 / 2` | `0.015000000000000013` | PASS |

Both filtered means hide the deliberately large third-token error. This establishes why acceptance must keep the pre-TIS population; it does not measure any requested pair's numerical agreement.

## Existing CPU suite — not executed beyond collection

```sh
timeout 60s /data/ycfeng/envs/openmopd-py312/bin/python -m pytest -q -p no:cacheprovider tests/fast/examples/infra_features/train_infer_mismatch_helper/test_mis.py tests/fast/backends/training_utils/loss/hub/test_backend_loss_normalization.py
```

Exit status: `4`. Collection imported `tests/conftest.py` -> `generation_fixtures` -> rollout executor -> dashboard hooks/store and failed with `ModuleNotFoundError: No module named 'polars'`. No selected test passed or failed its body. The root conftest's dashboard import creates an environment dependency even for this narrow CPU selection. `task_memory/env_handbook.md` is absent. No dependency was installed or fallback substituted; rerun this existing suite in the selected complete runtime during P2.

## Open validation

Actual worker-image Megatron gradient normalization, CP reconstruction, TIS configuration, one-token response handling and same-version model measurements are unverified. These are owned by P1 configuration or P2/P3 execution. A local collection error does not establish a model architecture gap. Numerical acceptance is now defined by D8; actual measurements remain outstanding.

## D7 documentation check — PASS

`git diff --check` exited 0. Inline Python 3.10.6 verified seven maintained document headers, 56 existing local links, the actual D7 reply and R8, and `131072 - 8192 == 122880`. The four retained Qwen format fixtures contain 86,669, 97,254, 95,907 and 93,256 prefix tokens; each fits with the full response reserve. Both successful probe output and pytest collection failure are preserved above. This verifies accepted-budget arithmetic and documentation consistency, not full-population eligibility or native memory capacity.
