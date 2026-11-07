## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Parent completes the repaired pinned collection: all 200 steps/1600 completions PASS; archive exact targets, full lossless receipt and terminal identity evidence. |
| 2026-11-08 | Repair the actual train-shard contract using exact native identity/token/mask/execution-ID/version joins; record real representative RED/GREEN, six negative controls and ready full-collection CLI. |
| 2026-11-08 | Record the first actual pinned collector's metadata-assumption failure and preserved INCOMPLETE receipt; await parent-provided raw schema before changing the collector. |
| 2026-11-07 | Incorporate the parent-provided actual A/B artifact inventory; retain metadata-based four-shard expectations and pending raw-schema execution. |
| 2026-11-07 | Implement the scoped offline training-token collector and record CPU verification; parent-owned pinned-worker collection remains pending. |

# Training-token audit — QWEN-REVIEW-TOKEN-AUDIT

## Outcome and scope

**Actual A/B token-count collection: PASS, all 200 steps and 1600 completions.** The parent executed the repaired collector in the pinned zero-GPU worker and verified the complete result below. The representative regression first reproduced the unsupported TRAIN `metadata` assumption, then passed after the native-field join repair; six modified-field negative controls and the native CPU fixture also pass. The first full INCOMPLETE receipt remains unchanged. No optimizer step or production edit was performed. Platform execution is parent-owned; the implementation subagent used only local evidence.

Requirements [D12](requirements.md#tis-settings--confirmed) and D14 own the original-token denominator and every-step evidence requirements. This collector supplies the previously absent counts from retained artifacts. It does **not** qualify Megatron's gradient-finalizer scaling; the independently assigned finalizer replay owns that evidence.

Accepted runs supplied by the parent:

| Pair | Job | Expected accepted updates | Completions per update |
| --- | --- | ---: | ---: |
| A | `exp-1107-173758-712234` | 100 | 8 |
| B | `exp-1107-173758-806531` | 100 | 8 |

## Inspected native owners and evidence binding

| Owner | Observed behavior | Collector use |
| --- | --- | --- |
| `miles/backends/training_utils/loss/objective.py:129-131,173,230-240` | `count_loss_tokens` sums each original full-response mask with each fully masked sample clamped to one. With Megatron integration the loss callback returns this count before any modified TIS mask; gradient finalization owns division. | Invoke the existing function, report original eligible count separately, and flag any actual clamp-induced difference. Never call the clamped count a pure eligible-token count. |
| `miles/backends/megatron_utils/model.py:475-559` | Native training forwards the original `loss_masks`, `sample_indices` and `rollout_mask_sums` to the microbatch loss callback with `apply_megatron_loss_scaling=True`. | Bind each consumed microbatch to the original train rows and derive its native callback count from their full masks. |
| `miles/backends/training_utils/loss/hub/losses.py:192-227,266-278` | Native local masks and raw train/old/rollout scores/advantages are dumped before TIS. `ppo_kl` and `pg_loss` have already undergone native sanitization. TIS modified masks are not included in this debug dump. | Report raw per-field finite/nonfinite coverage separately from downstream sanitized tensors. Post-TIS retained counts remain `null`, not zero or a reconstructed acceptance claim. |
| `miles/backends/training_utils/metrics/debug_dump.py:28-74` | TP peers are suppressed. Payload contains global `rank`, per-process `call`, local row index, lengths, scores, advantages and local mask, but no rollout/sample identity. | Order by payload `call`, require a contiguous counter, then match lengths plus exact mask/old/rollout/advantage arrays and verify the matched row order against persisted `micro_batch_indices`. Zero or multiple matches are INCOMPLETE; filenames are not step or DP geometry. |
| `miles/backends/training_utils/metrics/train_dump.py:11-45` and `miles/backends/megatron_utils/actor.py:986` | Only TP0/PP-last writes a train shard, with payload rank/CP metadata and consumed rollout rows. Save occurs after the training pass. The actual train shard has no source `metadata`. | Verify sample indices, complete prefix/completion tokens, original masks, native rollout execution IDs and full generation-version spans before joining original-rollout source provenance. Do not claim an independent source-metadata receipt in the native train shard. |
| `miles/backends/megatron_utils/actor.py:727-755` | Native score metadata explicitly supplies cell/global rank and DP/TP/CP/PP identities. | Reuse `inspect_qwen35._score_slices` on baseline score files as the authoritative rank map. Compare dimensions with selected launch/config; never compute DP rank from a global-rank filename. |
| `miles/backends/training_utils/data/context_parallel.py:320-341` and `miles/backends/training_utils/data/rollout.py:128-171` | Native functions own local CP response-mask slicing and prefix-zero input-mask expansion. | Invoke both existing mask owners with recorded dimensions. Prefix-mask expansion is a native-function reconstruction, not a retained packed-runtime mask receipt. |
| `tests/manual/agent_opd/inspect_qwen35.py:_publication_receipts,_source_check,_decode_version,_response_positions` | Existing strict readers bind full publication/checksum chains, frozen source/full-token identities, actual consumed versions and CP positions. | Reuse unchanged readers. Require all 100 publications, one actor attempt and a counter delta of one per update, plus exactly eight distinct source/sample identities. |

Every successful row reports original eligible target tokens, native `count_loss_tokens` tokens, fully masked samples, prefix/response counts, consumed identities/version, actual published counter, DP/CP microbatch counts, and per-field nonfinite coverage. Full masks count once at CP0 across distinct DP owners; distinct CP local target slices must sum back to the original eligible count. Metadata selects TP0/PP-last authoritative records, rather than multiplying TP replicas. CP all-gather lacks sufficient dump position metadata and is explicitly INCOMPLETE; the actual selected A/B launch is CP1.

Source IDs/hashes in sample rows have `source_identity_binding_basis='verified_original_rollout_join'` and `native_train_source_metadata_persisted=false`. Original rollout provenance still passes unchanged `_source_check` against the frozen population. The native train-side join checks every full token, including the prefix, not only response length or completion hashes. It checks the full original mask and complete recorded version-call dictionaries as well as the sample index. There is no metadata default or per-field fallback.

`Sample.rollout_id` is the **rollout execution identity**, not the outer training schedule position. Native conversion at `miles/ray/rollout/train_data_conversion.py:121` uses `sample.index` when this execution ID is `None`; the actual retained rows therefore have native execution IDs `[7,2]` while the outer training position is `0`. This native convention is checked and reported explicitly. The train-shard `weight_versions` column is copied from generation calls at lines 213-214: it is a decode/prefill generation receipt, **not an independent trainer-version scalar**. Generation versions are compared with the previous native publication counter; both bases are labeled in JSON. The pre-update training version is publication-order-derived, not fabricated as direct shard metadata.

Exact debug-array matching compares native float32 dump values, including NaN-to-NaN equality for **identity only**. NaNs are still counted as nonfinite evidence, never sanitized into passing measurements. If a step cannot be bound, its row remains INCOMPLETE; no substitute completion, guessed identity or new training pass is generated. The report retains 100 scheduled rows per selected pair, including incomplete rows.

## Minimum parent-provided raw artifacts

The collector must run in the pinned zero-GPU worker; this subagent did not read these cloud files. For each accepted native `RUN` directory, retain/read:

| Paths | Required contents/reason |
| --- | --- |
| `RUN/rollout_data/0.pt` through `RUN/rollout_data/99.pt` | Fresh completion IDs, full tokens/original response masks, source and train identity receipts, actual decode/prefill version spans. |
| `RUN/train_data/0_*.pt` through `RUN/train_data/99_*.pt` | All native authoritative DP/CP shards: full tokens, full original masks, sample indices, `rollout_ids`, `weight_versions`, old/decode/teacher scores, advantages, lengths, `rollout_mask_sums`, `micro_batch_indices`, `num_microbatches` and `num_rollouts`. Source metadata is not required because it is absent from the actual native persisted contract. |
| `RUN/policy_loss_debug/*.pt` | All contiguous native payload call counters for each authoritative rank; exact original local-mask/old/decode/advantage binding and actual pre-TIS forward-score coverage. |
| `RUN/train_data/eval_monitor_0_*.pt` | Existing baseline score topology metadata, including explicit global/DP/TP/CP/PP rank identities. Other monitoring score checkpoints are not needed by this collector. |
| `RUN/events/**/*.jsonl` | Complete actor attempts, publication results and engine checksum chain, including initial/restoration publications. |
| Frozen `population.json` | Eligible training source identities, rendered prefix counts/hashes, template contract, group/evaluation exclusion checks. |
| Existing mounted-local `launch.json` for each pair | Exact run origin, full native argv and source commit; already inspected locally. |

If schema inspection is needed before execution, the precise smallest inventory request is one accepted `RUN/train_data/0_<payload-rank>.pt`, one matching `RUN/policy_loss_debug/rank_<payload-rank>_call_<payload-call>.pt`, and one `RUN/train_data/eval_monitor_0_<payload-rank>.pt`: list dictionary keys, field types, tensor dtypes/shapes and scalar metadata. Use payload ranks/calls, not assumed even-rank geometry.

The parent subsequently supplied an **actual read-only file inventory for both accepted runs**: 424 train files (400 training files = 100 positions × four representative ranks, plus 24 monitoring files), 800 policy-debug files (200 payload calls for each existing representative rank), 106 rollout files (100 training plus six evaluation), 106 trajectory JSONL files and 13 event JSONL files. Existing representatives are ranks 0/2/4/6; TP1 replicas 1/3/5/7 are not dumped. This is parent-observed inventory, not this subagent's cloud inspection. The collector requires the four metadata-confirmed authoritative shards, never eight training-rank files. Counter lengths are checked from payloads and are not hardcoded to the parent-provided filenames. This inventory supports proceeding directly to the parent-owned collector run; key/shape validation remains part of that run.

## Verification commands and observations

Working directory: `/data/ycfeng/sota-engine/miles`. Local interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python **3.12.13**, torch **2.11.0+cu130**; this is not the pinned worker runtime. Environment: `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`, `RAY_TMPDIR=/data/ycfeng/tmp`, `HF_HUB_OFFLINE=1`. No conda activation or GPU/model execution.

### Native CPU fixture — PASS

```bash
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode RAY_TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.audit_qwen35_training_tokens \
  --self-test --report /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-token-audit-cpu-fixture.json
```

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Original eligible targets for `[1,1,1]`, `[1,0]`, `[0,0]` | 4 | 4 | PASS |
| Native original-mask count with fully masked sample | 5 | 5 | PASS; explicitly distinct from 4 eligible targets |
| Native CP1 target count | 4 | 4 | PASS |
| Native CP2 local counts sum | 4 | `1 + 3 = 4` | PASS |
| Native prefix-zero mask expansion for total lengths `[5,5,3]` | Prefix excluded and completion masks unchanged | Exact expected 13-position packed mask | PASS |
| Exact debug-array identity with a raw NaN | Unique native row; NaN still counted | Unique row; `nonfinite_eligible=1` | PASS |
| Duplicate matching candidates | Reject as ambiguous | Rejected | PASS |

Observed stdout: `QWEN35_TRAINING_TOKEN_AUDIT PASS /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-token-audit-cpu-fixture.json`. This fixture does not simulate or qualify the 200 real update rows.

### Existing A/B launch receipts — PASS

```bash
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode RAY_TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
from pathlib import Path
from tests.manual.agent_opd.audit_qwen35_training_tokens import _contract
import json
base = Path('task_memory/task_2026-11-06_qwen35_three_pairs')
config = json.loads((base / 'training_config_h200.json').read_text())
for pair, job in (('A', 'exp-1107-173758-712234'), ('B', 'exp-1107-173758-806531')):
    receipt = base / 'evidence' / 'first-round' / 'student' / pair / job / 'launch.json'
    launch = json.loads(receipt.read_text())
    result = _contract(config, pair, Path(launch['output_dir']), launch)
    print(pair, {key: value for key, value in result.items() if key != 'training_argv'})
PY
```

Actual for both pairs: `steps=100`, `batch=8`, `tp_size=2`, `cp_size=1`, `pp_size=1`, `dp_size=4`, `source_commit=e3d626553bf1887c73c0423fb0f4905a1064cd13`. This validates real local receipt/config parsing, not native raw tensor schemas or distributed execution.

### Syntax and tooling

`python3` with `ast.parse(Path('tests/manual/agent_opd/audit_qwen35_training_tokens.py').read_text())` passed. An initial local native-module import timed out at 60 seconds; a diagnostic traceback located the delay at the installed `tvm_ffi`/`xgrammar` shared-library import through SGLang. Later real fixture and launch checks exited successfully without a dependency patch or import stub. The harmless warning `deep_ep is not installed, some functionalities may be limited` remained visible.

`/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m ruff check tests/manual/agent_opd/audit_qwen35_training_tokens.py --no-cache` could not run: `No module named ruff`. Local `black` and `isort` are also absent. No lint PASS is claimed and no dependencies were installed.

## First actual pinned-worker collection — INCOMPLETE (collector defect)

The parent executed the collector in zero-GPU job `exp-1108-000134-683400`. Job terminal status was Succeeded; the reporting soft gate returned INCOMPLETE. Preserve the original receipt unchanged:

`evidence/training-token-audit-exp-1108-000134-683400.json`

A local read of that existing selected receipt established:

| Observation | A | B |
| --- | ---: | ---: |
| Scheduled step rows | 100 | 100 |
| Rows with `corrupt_schema: 'metadata'` | 100 | 100 |
| Unconsumed debug calls per representative rank | 200 each at 0/2/4/6 | 200 each at 0/2/4/6 |
| Verified native successful/skipped publication increments | 100 / 0 | 100 / 0 |
| Baseline/final published versions | 0 / 100 | 0 / 100 |
| Restoration publications | 6 | 6 |

Actual pinned runtime in this receipt: Python **3.12.16**, torch **2.14.1+cu130**. Native publication-chain verification completed before the per-step collector failure. The zero cursors are a consequence of failing before debug binding, not evidence that the real training failed to consume data. Original/native token counts remain unknown in this first receipt.

Source inspection found a specific contract boundary: `convert_samples_to_train_data` writes `metadata` at `miles/ray/rollout/train_data_conversion.py:207-208`, but `_package_shards`'s persisted DP-row column list at lines 504-536 omits `metadata` while retaining `tokens`, `sample_indices` and `weight_versions`. The downstream `process_rollout_data_shard` only drops the partition key and reorders lengths. The collector erroneously included `metadata` in its required training-row fields and accessed `batch['metadata']`; this assumption must be repaired at the collector, not by changing production training or inventing a metadata fallback.

The initial checkpoint deliberately left the collector unchanged until actual schema evidence arrived. The parent then supplied `evidence/token-dump-schema-exp-1108-000817-467103.json` and four real retained native files. The traceback identified `_step -> _training_shards -> required-row-field length validation` raising `KeyError('metadata')`; baseline SCORE metadata was present, while TRAIN metadata was absent. The repair below uses that exact native contract, not production edits or a metadata fallback. No training rerun or additional optimizer update is authorized or needed.

## Actual representative regression and repair — RED/GREEN PASS

Parent-downloaded actual artifacts are retained locally under:

`/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-token-schema-exp-1108-000817-467103`

The four files are `train_data/0_0.pt` (1,239,572 bytes), `policy_loss_debug/rank_0_call_0.pt` (21,601 bytes), `rollout_data/0.pt` (20,138,313 bytes) and `train_data/eval_monitor_0_0.pt` (baseline SCORE metadata). Only these local selected copies were read by this subagent. They represent **one DP shard containing two of eight completions and one of its two debug calls**, not a complete update or 200-row acceptance.

First add the persistent `--representative-dir` regression to the assigned collector, then run before changing the shard reader:

```bash
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode RAY_TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.audit_qwen35_training_tokens \
  --representative-dir /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-token-schema-exp-1108-000817-467103 \
  --report /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-token-native-representative-red.json
```

**RED observed:** JSON `verdict=INCOMPLETE`, `issues=[{'code':'corrupt_schema','detail':"'metadata'"}]`; the exact original bug reproduced through the actual shard-reader seam. The soft-gate process exited normally; JSON, not exit code, owns the verdict.

After removing the unsupported field requirement, `_training_row` now validates only actual native consumed columns and joins them to the original rollout by exact sample index/full-token/full-mask/native-execution-ID/full-version-span equality. Source metadata is never synthesized or marked as directly persisted in TRAIN. `_training_shards` validates the retained native microbatch schedule; debug bindings must agree with that schedule's row order, and each schedule records the actual eight-completion global update.

Run the same actual-artifact regression after repair, with a new report path:

```bash
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode RAY_TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.audit_qwen35_training_tokens \
  --representative-dir /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-token-schema-exp-1108-000817-467103 \
  --report /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-token-native-representative-green.json
```

| Check | Expected from actual retained files | Actual | Result |
| --- | --- | --- | --- |
| Native representative sample IDs | `[7,2]` | `[7,2]` | PASS |
| Native execution IDs when raw execution ID is None | `[7,2]`, not outer schedule `0` | `[7,2]` | PASS |
| Full original tokens/masks and complete generation spans | Exact equality with original rollout rows | Exact equality | PASS |
| Original eligible shard targets | `565 + 182 = 747` | 747 | PASS |
| Native original-mask count | 747 | 747 | PASS |
| Generation-consumed versions | `['0','0']` | `['0','0']` | PASS; generation receipts, not direct trainer scalar |
| First debug call binding | Source sample index 7, matching first stored native microbatch | 7 | PASS |
| First debug eligible positions | 565 | 565 | PASS |
| Production `_consume_debug` replay of the one retained native microbatch | One call; original/native/local counts all 565 | One call; 565 / 565 / 565 | PASS; only this recorded microbatch, not the missing second call |
| Raw eligible score/advantage nonfinite entries | 0 | 0 | PASS |
| Native TRAIN source metadata receipt | Absent; verified original-rollout join instead | `false`, explicit join basis | PASS |

Six negative controls make single in-memory changes to the actual retained native shard and call the same `_training_row` validation seam. They do not alter any retained artifact or replace actual acceptance data:

| Modified actual field | Expected rejection | Actual | Result |
| --- | --- | --- | --- |
| One prefix token | `consumed_token_mismatch` | Same | PASS |
| One completion token | `consumed_token_mismatch` | Same | PASS |
| One original response-mask position | `consumed_original_mask_mismatch` | Same | PASS |
| Sample index | `consumed_sample_index_mismatch` | Same | PASS |
| Execution ID replaced by outer schedule position | `consumed_rollout_execution_id_mismatch` | Same | PASS |
| Generation prefill span boundary | `consumed_weight_version_spans_mismatch` | Same | PASS |

The repaired script's tiny native-function fixture was also rerun:

```bash
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode RAY_TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.audit_qwen35_training_tokens \
  --self-test --report /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-token-audit-cpu-fixture-after-schema-fix.json
```

Observed **PASS**, with original eligible count 4, native clamped count 5, native CP2 counts `[1,3]`, preserved raw NaN coverage and ambiguous binding rejection. These are CPU-function controls only.

Final `ast.parse`, whitespace checks and an AST check scoped to accesses of the **consumed `batch`** in `_training_row`/`_training_shards` passed. Two earlier overly broad static assertions incorrectly rejected legitimate baseline score metadata and the collector's rank-descriptor metadata; the check was corrected to target only consumed-batch metadata. No collector behavior was changed to satisfy those assertions. Missing local lint tooling remains unchanged.

## Parent-owned pinned-worker rerun — PASS

Pinned image: read the unchanged `training_config_h200.json:image`; worker interpreter is its `worker_python` (`/opt/sglang/bin/python3`). The actual collector writes its Python/torch versions into JSON; prior image receipts are not substituted for this execution.

Run from the repository in the already authorized zero-GPU worker:

```bash
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.audit_qwen35_training_tokens \
  --config task_memory/task_2026-11-06_qwen35_three_pairs/training_config_h200.json \
  --run A=/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/A/exp-1107-173758-712234 \
  --run B=/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/B/exp-1107-173758-806531 \
  --launch A=task_memory/task_2026-11-06_qwen35_three_pairs/evidence/first-round/student/A/exp-1107-173758-712234/launch.json \
  --launch B=task_memory/task_2026-11-06_qwen35_three_pairs/evidence/first-round/student/B/exp-1107-173758-806531/launch.json \
  --report task_memory/task_2026-11-06_qwen35_three_pairs/evidence/training-token-audit-exp-1108-002213-053180.json
```

Executed job `exp-1108-002213-053180`, local time 2026-11-08 00:22:13–00:25:25. Submission used the frozen config image, personal `step_main`, 8 CPUs, 0 GPUs, 64000Mi memory, both configured mounts and local source `100.96.128.195:/data/ycfeng:/data/ycfeng`. Submitter cwd was `/data/ycfeng`; worker cwd was the repository. Worker environment: configured CUDA-compat `LD_LIBRARY_PATH`, `CUDA_VISIBLE_DEVICES=""`, `OMP_NUM_THREADS=1`, offline HF/Transformers, `PYTHONDONTWRITEBYTECODE=1`, and job-local `TMPDIR=/var/tmp/qwen-token-audit-exp-1108-002213-053180`. Actual Python 3.12.16 and torch 2.14.1+cu130 match the pinned runtime.

| Actual gate | A | B | Result |
| --- | ---: | ---: | --- |
| Complete update rows | 100 | 100 | PASS; exact positions 0–99 |
| Consumed completions | 800 | 800 | PASS; eight unique identities per update |
| Original eligible targets, all steps | 237618 | 201819 | PASS |
| Per-step minimum / maximum | 593 / 5079 | 715 / 3703 | PASS; actual values, not generated-length estimates |
| Fully originally masked samples | 0 | 0 | PASS; native clamp adds no targets |
| Eligible nonfinite tensor entries | 0 | 0 | PASS |
| Native count = original eligible count = CP-local sum = DP count at CP0 | Every step | Every step | PASS |
| Complete DP ownership, stored microbatch/debug-call binding, original full-token/mask/version join | Every step | Every step | PASS |

The parent additionally checks all 200 rows for exact step ordering, four distinct DP owners, no duplicate/missing consumed completion within the update, one successful native counter increment, and all count equalities. The full JSON has `verdict=PASS`, no issues, and `{'PASS':100}` for each pair. The original 8,564,537-byte JSON is retained locally and archived losslessly as `evidence/training-token-audit-exp-1108-002213-053180.json.gz` (547,994 bytes); decompression is checked byte-for-byte against the original. `evidence/training-token-audit-summary.json` and `evidence/training-target-counts.md` derive every-step original/native counts and DP subtotals from this receipt. No raw result was edited.

Independent `evidence/training-token-audit-exp-1108-002213-053180-platform.json` confirms job/default Succeeded, finish `2026-11-07T16:25:24Z`, personal creator, pinned image/source, zero GPUs and no stop timestamp. The same-basename `.log` retains complete collector stdout. The collector remains a reporting soft gate; its JSON, not process exit alone, establishes collection PASS.

**Remaining limits:** the collector does not reconstruct post-TIS survivor masks or historical gradient buffers. Trainer pre-update version is native-publication-order-derived rather than a direct train-shard scalar. Native finalizer semantic replay is independently documented in `test_report_2026-11-07_native_token_normalization.md`. These scopes remain distinct from the complete actual target collection.

## 1. 规划完成情况

**汇总：** PASS 4｜BLOCKED/FAILED/SKIPPED 0｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Scoped collector repair and actual-schema regression | PASS | Real representative RED/GREEN and all six negative controls pass after the actual-contract repair. |
| Tiny native CPU fixture and selected launch parsing | PASS | Actual local commands/results above. |
| Exact execution/report handoff | PASS | Raw-artifact minimum, parent inventory, CLI and limits are recorded. |
| Corrected parent-owned 200-row count collection | PASS | All 200 rows/1600 completions verified; original and native counts match, no eligible nonfinite values. |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** Actual raw schema arrival through repaired full pinned collection｜**当前前沿：** targeted full-task review and archival closure.

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | Collector and tiny fixture directly supply the missing every-step token evidence; no broad test harness. |
| D2 细节反复重试 | CLEAR | The actual schema defect required one behavioral repair; actual representative regression passed. Over-broad static assertions were narrowed to their intended batch owner. |
| D3 支线问题修补 | CLEAR | No unrelated fixes or dependency installs. |
| D4 可并行任务停滞 | NO DATA | Parent owns parallel finalizer/platform work; this subagent did not block or inspect it. |
| D5 超范围镀金 | CLEAR | No optimizer replay, production logging, TIS-survivor reconstruction or new configuration path. |
| D6 分析空转 | CLEAR | Actual schema and RED reproduction led directly to the verified native-field join repair. |
| D7 路线违背 | CLEAR | No Git, cloud, SSH, platform, GPU or new optimizer steps. |

**文档检查：** S1–S6 均未发现本 scoped subtask 的明显缺陷；the parent owns full-task archival/current-state reconciliation.
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Parent reruns the ready pinned-worker CLI → done only after inspecting all 200 rows, original/native counts, identity/version coverage and issues; preserve the first receipt.
2. 并行：parent-owned native finalizer replay; its result is independent of this collector's CPU/representative regression.

## 4. 最值得关注的 3 点

1. Real file inventory confirms four authoritative rank shards per step; DP identity still comes from native metadata, not filename arithmetic.
2. Native fully-masked clamp counts are explicitly different from eligible-token counts; no survivor denominator is substituted.
3. Actual representative join and six strict negative controls now pass; full 200-row collection still requires the parent-owned rerun, and the first INCOMPLETE receipt remains historical evidence.
