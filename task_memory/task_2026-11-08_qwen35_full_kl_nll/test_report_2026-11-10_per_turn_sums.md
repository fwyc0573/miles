## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Implement Ticket02 original-mask turn sums and record CPU verification, ACK API and native runtime limits. |

# Ticket02 — per-turn sums CPU verification

TaskID: `profile-t02-sums-20261110`. Base: committed D35 merge `55fba827` (documentation HEAD subsequently `07378aad`). Scope: spec S3 only; no GPU, external network, platform operations or formal run.

Outcome: **CPU implementation-ready**. Current-tree verification covers all110 selected cases; the final nullable-metadata preservation edit also passes all79 directly affected conversion/metadata cases. Ticket02 GPU acceptance and T03 integration remain pending.

## Implementation and ownership

- `tests/manual/agent_opd/swe_tis.py`: existing `token_sums` sample loop measures original-mask native `opd_reverse_kl`, negative pre-optimizer current-student scores and token counts as detached float64 partials. It does not recreate student-minus-teacher RKL, add a forward or persist per-token measurements.
- `tests/manual/agent_opd/swe_training.py`: one turn-row exchange per optimizer attempt, with one device-to-host copy per contributing rank. CP partials for the same native sample index add; only last-PP-stage / TP-rank0 contributes. Rows restore native source-index order and preserve canonical `source_uid` from existing bank metadata. Row count, UID uniqueness, complete CP membership, original tokens and sealed-bank counts are soft checks. Local auxiliary preparation exceptions become exchanged error payloads rather than skipping collectives. Native mandatory-mask/D7 and optimizer-success handling remain unchanged.
- `miles/backends/training_utils/loss/{hub/losses.py,objective.py}`: pass native RKL into the TIS hook and pass the resulting compact turn sums through the existing loss record, outside scalar logging.
- Necessary native transport edit: `miles/ray/rollout/train_data_conversion.py` carries raw native estimator configuration through existing per-sample `metadata`. `opd_top_k_strategy` and weighting are rollout-only; no config schema or new transport column is added. `_estimator_label` in `swe_training.py` is the sole label owner. Sample metadata is not mutated.
- Rows occur only in the existing native ACK. Trainer `updates.jsonl`, `optimizer_attempts.jsonl`, D7 failed-batch JSONL and `SWE_NATIVE_UPDATE` stdout exclude `turn_sums`; the rollout profile will own durable rows. The existing D7 tensor evidence is unchanged.
- Owned tests: `tests/fast/test_swe_tis.py`, `tests/fast/test_swe_turn_sums.py`. No edits to `swe_replay.py`, `distillation_profile.py`, `run_swe_opd.py`, configs, tickets or shared progress.

## T03 consumer API

The dict returned by `optimizer_step(..., stage="after_optimizer")` retains existing attempt/cell/bank/success counters and adds:

```python
record["turn_sums"]  # list[dict], sorted by canonical native sample index:
# {"uid": str, "rkl_sum": float, "nll_sum": float, "tokens": int}
record["turn_sums_verified"]      # bool
record["unverified_turn_sums"]    # list[str]; empty when verified
record["kl_estimator"]           # native-config-derived str, or None on invalid rows
record["kl_before_tis_numerator"] # sum of the verified rows' rkl_sum, else None
record["nll_before_tis_numerator"]# sum of the verified rows' nll_sum, else None
record["kl_before_tis"]           # rkl numerator / original_tokens, else None
record["nll_before_tis"]          # nll numerator / original_tokens, else None
record["nll_before_tis_denominator"]  # same original_tokens as kl denominator
```

Consume observations only when `update_successful` is true. Skipped ACKs keep the same successful-update count and may contain valid measurements, but must not append observations. A successful ACK with `turn_sums_verified=False` has `turn_sums=[]` and unknown macros; T03 must mark its profile unverified from that successful update and stop subsequent profile appends/derivation under S7 while native training continues. T02 does not own rollout-side suppression or bank-to-conversation/turn joining. Existing `bank_membership_verified`, `actual_turns`, `original_tokens`, `expected_bank_turns`, `expected_bank_tokens` remain available.

Sampled label: `sampled_current_student_minus_frozen_teacher_on_original_behavior_tokens`. Native top-k label: `native_top{k}_{strategy}_{weight_mode}`. Labels derive only from `metadata[*]["opd_estimator_config"]` populated by native conversion; no fallback for old source/config records.

## Environment and exact commands

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Python: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, 3.12.13 (Clang22.1.3), torch2.11.0+cu130, transformers5.19.0, pytest9.1.1; no conda activation. All workload tensors and distributed checks use CPU/Gloo, not CUDA.

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_swe_tis.py tests/fast/test_swe_turn_sums.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-pytest --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/ray/rollout/test_train_data_conversion.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-native-pytest --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-native-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/ray/rollout/test_train_data_conversion.py -k 'weight_versions_survive_the_object_store or store_plans_survive_the_object_store' -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-ray-pytest --basetemp=/data/ycfeng/tmp/t02-ray-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_swe_tis.py tests/fast/test_swe_turn_sums.py tests/fast/ray/rollout/test_train_data_conversion.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-final-pytest --basetemp=/data/ycfeng/tmp/t02-final-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_swe_turn_sums.py::test_native_metadata_transports_rollout_only_estimator_config tests/fast/ray/rollout/test_train_data_conversion.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t02-metadata-final-pytest --basetemp=/data/ycfeng/tmp/t02-metadata-final-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'import ast; from pathlib import Path; paths = ["tests/manual/agent_opd/swe_tis.py", "tests/manual/agent_opd/swe_training.py", "tests/fast/test_swe_tis.py", "tests/fast/test_swe_turn_sums.py", "miles/backends/training_utils/loss/hub/losses.py", "miles/backends/training_utils/loss/objective.py", "miles/ray/rollout/train_data_conversion.py"]; [ast.parse(Path(p).read_text()) for p in paths]; print("AST PASS", len(paths), "owned Python files")'
git diff --check
```

## Observed results

| Check | Expected / passing condition | Observed | Verdict |
| --- | --- | --- | --- |
| Initial TIS/turn tests | Existing TIS regressions and new measurement/ACK checks all pass | 30 passed in76.93s | PASS |
| Initial native conversion regression | All77 cases pass | 75 passed;2 Ray fixture setup errors in7.18s: `AF_UNIX path length cannot exceed107 bytes` for the long TMPDIR | FAIL (environment path) |
| Targeted Ray rerun | Short approved local TMPDIR removes the socket-path failure without code changes | 2 passed,75 deselected in10.80s | PASS |
| Full run before ndarray refinement | All selected TIS, estimator metadata, turn/ACK and native conversion cases pass | 109 passed in59.00s | PASS |
| Full run with native ndarray-index check | All current110 selected cases pass | 110 passed in59.61s | PASS |
| Final nullable-metadata preservation | Conversion remains healthy with optional metadata absent; all affected native conversion cases pass | 79 passed in10.73s after the final code edit | PASS |
| Static syntax / whitespace | Owned Python files parse; diff has no whitespace errors | AST parse7/7; `git diff --check` exit0 | PASS |

Meaningful assertions include uneven target lengths and masked nonfinite padding, fully TIS-rejected turns still measured, NLL using held current-student scores even when the gradient forward differs, native precomputed top-k RKL differing from student-minus-teacher, successful/skipped ACKs, no duplicated durable rows, and real AdamW state changes during auxiliary failures. Native `sample_indices` uses an int64 ndarray codec; integer scalar representations normalize to Python integers without losing UID mapping or accepting floats/booleans. This is native transport support, not old-source compatibility.

The8-process CPU test uses2CP×2TP×2PP logical topology and real world collectives. Only last-stage/TP0 ranks contribute. Expected rows: `(source-10,rkl_sum=1,nll_sum=4,tokens=2)` and `(source-30,rkl_sum=2,nll_sum=13,tokens=4)`, including an empty CP partial; macro RKL=0.5, NLL=17/6, original tokens=6, actual turns=2. Its second real optimizer step injects rank-local row and scalar-diagnostic exceptions and must still ACK successful update2 with an unverified measurement verdict. Missing CP partials, duplicate replica contributions, CP UID disagreement, nonfinite sums, row/native-count mismatch, unknown indices and missing estimator config are rejected as auxiliary evidence, not optimizer stops.

## Limits and remaining acceptance

- CPU readiness does not close Ticket02's GPU acceptance. A's first formal successful update must validate actual native row sums, current policy timing, bank membership, attempt identity, counts and T03 profile persistence under D16; no additional GPU smoke was performed.
- Logical TP/PP selection is verified with CPU/Gloo; native Megatron TP/PP kernels, NCCL cost and actual256-turn GPU overhead are not measured here.
- Existing native sampled and precomputed top-k fields are consumed, not reimplemented. The unchanged SWE canonical bank currently resets precomputed OPD RKL and uses sampled teacher targets; these tests do not authorize or claim an end-to-end top-k SWE producer. No full-vocabulary estimator or old-source compatibility path was added.
- Native communication/mandatory training errors retain their existing failure handling. Only auxiliary measurement/preparation/consistency/sink failures are isolated. T03 integration and permanent suppression after a failed observation remain outside this ownership.

## Scope checkpoint

`check-progress` self-check against current requirements, plan, Ticket02 and merge/progress records: D35 merge prerequisite PASS; S3 implementation/CPU verification PASS; scoped commit pending at this checkpoint; T03 consumer integration and A-first-update GPU acceptance remain outside this delivered slice. D1–D7 drift patterns CLEAR: all exploration, code edits and tests advance S3; the sole observed Ray environment error was resolved by a short TMPDIR rather than fixture/config work. S1–S6 document defects not found in the active post-merge records. Route: commit only the owned files, hand the ACK API to T03, retain D16 runtime acceptance as unfinished; no scope or ticket edits needed.
