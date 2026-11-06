## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Record local implementation evidence and proposed acceptance semantics for the interview. |

# Validation design and evidence

This is an interview draft. Decisions are owned by [requirements](requirements.md). The canonical external inventory and consistency analysis remain in the handbook; this file records their implications for this task rather than copying them wholesale.

## Source boundary

- [Model inventory](/data/ycfeng/stepfun-env-handbook/resource_analysis/available-model-oss.md).
- [Consistency analysis](/data/ycfeng/stepfun-env-handbook/resource_analysis/opd-train-inference-consistency.md).
- Miles inspected HEAD: `5c2e44635298675167c7c55e067dcb294f9e9fa9`, branch `agent-opd`.
- Steptron root inspected HEAD: `1e588c90ac7b5b29c454c668e93f2fe2d4d69fe4`, branch `yc-step`.
- Locally available Steptron remote-tracking ref `origin/zhuchenglin/qwen3p5-35a3-port`: `43c7d755878d6ca76462b3b7fafd0b043139981f`. This is local Git evidence; no fetch or claim about the current remote head was made.
- [Earlier Miles warmup](/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-05_agent_opd_warmup/summary.md) supplies reusable entrypoints and historical observations, not acceptance or authorization for these new pairs.

## Framework evidence

| Component | Observation | What remains unverified |
| --- | --- | --- |
| Miles student definitions | [4B](/data/ycfeng/sota-engine/miles/scripts/models/qwen3.5-4B.py) and [27B](/data/ycfeng/sota-engine/miles/scripts/models/qwen3.5-27B.py) select the Qwen3.5 hybrid model and dense FFNs. | Actual requested assets, precision and parallel configurations. |
| Miles model/weight bridge | [Qwen3_5Bridge](/data/ycfeng/sota-engine/miles/miles_plugins/mbridge/qwen3_5.py) registers dense and MoE model types and maps linear/full-attention tensors. | Every required tensor and runtime behavior for each requested model. |
| Miles OPD/alignment | [Qwen entrypoint](/data/ycfeng/sota-engine/miles/tests/manual/agent_opd/rjob_qwen_alignment.py) already builds student/teacher inference engines, TIS, token loss and checks; [teacher scorer](/data/ycfeng/sota-engine/miles/tests/manual/agent_opd/qwen_alignment.py) scores sampled tokens. | Existing script is a two-update 4B/FrogNano experiment with fixed topology and labels; it is not a ready launcher for this matrix. Reuse underlying mechanisms rather than copy the recipe blindly. |
| Miles HF-only save | [actor save_model](/data/ycfeng/sota-engine/miles/miles/backends/megatron_utils/actor.py:916) calls export when `save_hf` is set and native backend `save` is unset. | Qwen final-update completeness, companion files, exact export contents and real reload. |
| Steptron Qwen3.5 | Root source search found no `qwen3_5`, `Qwen3.5` or `GatedDeltaNet` in `steptron/`. The local remote-tracking ref above contains `steptron/model/qwen3p5_model.py`, `steptron/model/common/gated_deltanet.py`, `steptron/model/common/qwen3p5_mrope.py`, `steptron/model/vision/qwen3p5_vit.py` and `tools/checkpoint/reshape/impl/qwen3p5_reshapers.py`. The model docstring explicitly describes dense and MoE variants. | Integration into the chosen worktree, exact dependencies, 27B/397B configurations, OPD/replay/sync/export compatibility and native H800 behavior. Absence on root HEAD is not evidence of a general unsupported architecture. |

If Steptron is selected, inspect this existing port before proposing a new architecture implementation. Its GatedDeltaNet loader explicitly requires `flash-linear-attention`; the source states it is not vendored or in requirements. Check the selected image before calling that a runtime blocker.

## Asset access

The inventory records 4B in personal codesign storage, 27B and 35B-A3B under posttrain, and 397B-A17B under another user's codesign directory. Refer to the canonical inventory for exact source paths. Only the 4B location is currently documented inside this task's allowed cloud namespace. Do not read or copy the other locations under the current namespace restriction. P1/P2 must establish authorized personal locations or an explicit access decision before dependent execution. No source weight is downloaded, moved or changed in this phase.

Metadata/file-presence evidence does not prove complete loadability. Before use, pin actual config, tokenizer, template, index, shard metadata, dtype and revision; compare teacher/student token mappings rather than assuming compatibility from family names. If token mappings differ, token-ID scoring is a design blocker, not an invitation to silently retokenize completions.

## Required feature semantics

| User term | Semantic requirement | Candidate mapping and boundary |
| --- | --- | --- |
| R3 / route replay | Reuse a sampled policy's expert choices during the matching training forward/backward when the student has an MoE router. | All requested students are dense in the inspected definitions. Proposed result: `N/A: no student MoE router`, subject to the interview. A MoE teacher scoring a different model's tokens does not acquire the student's routes. Inspect teacher routing separately if teacher cross-engine comparisons are included. |
| TIS | Apply the accepted importance correction/mask using correctly defined rollout and training probabilities. | Miles has `--use-tis` and an existing custom MIS function in the inspected recipe. Mode, bounds, token/sequence semantics and normalization remain to be frozen; prior `[0.5, 2]` settings are not automatically accepted. |
| NCCL direct weight sync | Transfer the updated student through the native NCCL path, load it in the rollout engine and identify the consumed version. | Inspect the selected framework's actual publisher, transport and engine receipt. A completed collective alone does not prove the engine serves new weights. File polling/reload does not satisfy the requested direct transport. |
| Enable total token loss | Normalize the loss by the agreed global number of eligible tokens across ranks/microbatches, rather than averaging per-sample means. | Miles `--calculate-per-token-loss` is a candidate, not yet a proven semantic equivalence. Trace numerator, denominator, TIS mask, distributed reduction and gradient accumulation before adopting it. Metrics may use different aggregation. |
| HF-only checkpoint | Export the trained student in a declared loadable HF format, with required config/tokenizer assets, excluding native model and optimizer checkpoints. | Existing Miles actor export is a candidate. Text decoder versus full multimodal/MTP contents must be explicit; no silently incomplete VLM package. |

## Proposed acceptance gates

These gates define what must be evidenced; numerical thresholds, workload and duration await P1.

| Gate | Required evidence | Insufficient evidence |
| --- | --- | --- |
| Identity and inputs | Exact model revisions and trained/published/served versions; actual prompt/completion IDs, positions, masks, EOS, template, sampling and logprob definitions; teacher scoring the intended new student tokens. | Model names, shared tokenizer class or flag presence. |
| Same-version numerical agreement | Frozen short/medium/long real inputs; baseline and post-update comparisons on the same student weights; pre-TIS token-weighted absolute logprob error, declared K3 directions, p95/p99/max, valid/missing denominators and token-position/length breakdowns. | Teacher–student KL, TIS retention, iter0 alone, or a mean that hides identified token/mask/weight errors. |
| Weight synchronization | Initial and updated publications, transport completion, actual engine consumption/version, changed student values and same-version rescoring including the final accepted update. | Successful NCCL send, a running engine, or only penultimate publication. |
| Training behavior | Count actual successful optimizer updates; finite/nonzero pre-clipping grad norms, clipping and skipped-update records, loss definition and denominator, token retention, LR and trainable parameter changes; scalar tables and plots. Assess trends on a predeclared population/window. | Exit code, decreasing gradient norm alone, or a few fluctuating on-policy loss values described as general convergence. |
| HF persistence and reload | Exact personal codesign destination and successful update identity, expected tensor names/shapes/dtypes and shards/index, required companion assets, no unrequested optimizer/native weights, and real inference reload with fixed-input checks against the exported version. | Directory exists, save returned, or index/header inspection without reload. |
| Architecture assessment | Exact missing module/symbol/interface, source or reproducible native error, affected pairs, existing alternatives, smallest repair and cost/risk. | No filename match on one branch, guessed lack of model support, or a silent backend/model substitution. |

Define `d = log p_student_train - log q_student_rollout` and `r = exp(d)` on identical eligible tokens. The handbook defines `r*log(r)-r+1` and `r-1-log(r)` with different directions; confirm the selected implementation and sampling distribution before naming either KL. Compute diagnostic errors before TIS rejection, with padding and non-target tokens excluded by the original target mask. Track malformed/missing samples explicitly. The handbook's example `mean abs(logprob diff) <= 0.03` and historical KL magnitudes are proposals/diagnostic references, not universal pass lines.

Root-cause order: identity and token alignment -> sampling/probability semantics -> publication/consumption -> repeated fixed-weight forward -> first differing layer (norm/RoPE, attention, linear-attention state and packed sequence boundaries, dtype/parallel layout; router only where present) -> minimal repair and identical rerun. Do not widen tolerances, discard more tokens or change learning rate to conceal a same-weight defect.

For large runs, observer or artifact-validator failures mark evidence unverified and notify the user while healthy native training continues, per workspace policy. Final acceptance can remain incomplete without making an auxiliary validator a training stop mechanism.

## Interview recommendation

The first question compares executing in the active Miles repository, reusing its model/OPD/export paths, with executing literally in Steptron after inspecting and selecting the existing Qwen3.5 port. Miles is the provisional recommendation if the objective is qualifying the three pairs in the current workspace; Steptron is required if qualification of Steptron itself is part of the goal. No choice has been made. Combining both frameworks would expand the requested matrix and is not proposed. Reimplementing Qwen3.5 before inspecting the existing ports is rejected because reusable implementations exist.
