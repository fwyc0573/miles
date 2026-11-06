## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Apply the confirmed Miles-only scope and ground the routing-replay question in Miles consumers. |
| 2026-11-06 | Record local implementation evidence and proposed acceptance semantics for the interview. |

# Validation design and evidence

This is an interview draft with the execution framework confirmed: current Miles only, per D1 in [requirements](requirements.md). Steptron supplies semantic/acceptance references. The canonical external inventory and consistency analysis remain in the handbook; this file records their implications for this task rather than copying them wholesale.

## Source boundary

- [Model inventory](/data/ycfeng/stepfun-env-handbook/resource_analysis/available-model-oss.md).
- [Consistency analysis](/data/ycfeng/stepfun-env-handbook/resource_analysis/opd-train-inference-consistency.md).
- Miles inspected HEAD: `5c2e44635298675167c7c55e067dcb294f9e9fa9`, branch `agent-opd`.
- [Earlier Miles warmup](/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-05_agent_opd_warmup/summary.md) supplies reusable entrypoints and historical observations, not acceptance or authorization for these new pairs.

## Framework evidence

| Component | Observation | What remains unverified |
| --- | --- | --- |
| Miles student definitions | [4B](/data/ycfeng/sota-engine/miles/scripts/models/qwen3.5-4B.py) and [27B](/data/ycfeng/sota-engine/miles/scripts/models/qwen3.5-27B.py) select the Qwen3.5 hybrid model and dense FFNs. | Actual requested assets, precision and parallel configurations. |
| Miles model/weight bridge | [Qwen3_5Bridge](/data/ycfeng/sota-engine/miles/miles_plugins/mbridge/qwen3_5.py) registers dense and MoE model types and maps linear/full-attention tensors. | Every required tensor and runtime behavior for each requested model. |
| Miles OPD/alignment | [Qwen entrypoint](/data/ycfeng/sota-engine/miles/tests/manual/agent_opd/rjob_qwen_alignment.py) already builds student/teacher inference engines, TIS, token loss and checks; [teacher scorer](/data/ycfeng/sota-engine/miles/tests/manual/agent_opd/qwen_alignment.py) scores sampled tokens. | Existing script is a two-update 4B/FrogNano experiment with fixed topology and labels; it is not a ready launcher for this matrix. Reuse underlying mechanisms rather than copy the recipe blindly. |
| Miles HF-only save | [actor save_model](/data/ycfeng/sota-engine/miles/miles/backends/megatron_utils/actor.py:916) calls export when `save_hf` is set and native backend `save` is unset. | Qwen final-update completeness, companion files, exact export contents and real reload. |
| Miles routing replay | [Megatron replay registration](/data/ycfeng/sota-engine/miles/miles/backends/megatron_utils/replay_utils.py) maps replay streams to MoE layers; [Qwen FSDP adapters](/data/ycfeng/sota-engine/miles/miles/backends/fsdp_utils/adaptations/specs/qwen3_5.py) declare routing replay only for the MoE variant. | The actual student config must be checked before launch. Backend selection remains to be resolved; neither path creates an MoE router for a dense model. |

The earlier Steptron branch discovery is historical investigation recorded in progress.md. It is not an implementation candidate after D1. Architecture-gap reports must identify missing Miles capabilities and their exact dependency/runtime boundaries.

## Asset access

The inventory records 4B in personal codesign storage, 27B and 35B-A3B under posttrain, and 397B-A17B under another user's codesign directory. Refer to the canonical inventory for exact source paths. Only the 4B location is currently documented inside this task's allowed cloud namespace. Do not read or copy the other locations under the current namespace restriction. P1/P2 must establish authorized personal locations or an explicit access decision before dependent execution. No source weight is downloaded, moved or changed in this phase.

Metadata/file-presence evidence does not prove complete loadability. Before use, pin actual config, tokenizer, template, index, shard metadata, dtype and revision; compare teacher/student token mappings rather than assuming compatibility from family names. If token mappings differ, token-ID scoring is a design blocker, not an invitation to silently retokenize completions.

## Required feature semantics

| User term | Semantic requirement | Candidate mapping and boundary |
| --- | --- | --- |
| R3 / route replay | Reuse a sampled policy's expert choices during the matching training forward/backward when the student has an MoE router. | All requested students are dense in the inspected definitions. Proposed result: `N/A: no student MoE router`, subject to the interview. A MoE teacher scoring a different model's tokens does not acquire the student's routes. Inspect teacher routing separately if teacher cross-engine comparisons are included. |
| TIS | Apply the accepted importance correction/mask using correctly defined rollout and training probabilities. | Miles has `--use-tis` and an existing custom MIS function in the inspected recipe. Mode, bounds, token/sequence semantics and normalization remain to be frozen; prior `[0.5, 2]` settings are not automatically accepted. |
| NCCL direct weight sync | Transfer the updated student through the native NCCL path, load it in the rollout engine and identify the consumed version. | Inspect Miles' actual publisher, transport and engine receipt. A completed collective alone does not prove the engine serves new weights. File polling/reload does not satisfy the requested direct transport. |
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

## Current interview question: routing replay

Recommend keeping the three requested pairs and recording student R3 as `N/A: dense student has no MoE routing decisions`. For a dense student, do not enable `--use-rollout-routing-replay` merely to satisfy a flag checklist. In the existing OPD workflow the teacher scores student token IDs; a MoE teacher does not turn the student into an MoE model or supply routes for its training pass. Other required features and numerical checks remain required.

Evidence includes the student model definitions, Megatron's `register_replay_list_moe`, the shared replay consumer, and the distinct dense/MoE Qwen FSDP adapters. FSDP's routing-replay installer explicitly rejects a missing adapter; that observation describes FSDP and is not a claim about the Megatron failure mode. No native run has been attempted.

Before/after: a literal all-pairs replay checklist demands routes that the dense student does not have; the proposed checklist records architectural non-applicability and verifies the student's probabilities, weight updates and loss on the requested model. This preserves the model matrix but does not qualify R3 on an MoE student. Adding/replacing a student to exercise R3 would change the requested matrix; it is not proposed without user redirection. Await the user's interpretation before marking R3 resolved.
