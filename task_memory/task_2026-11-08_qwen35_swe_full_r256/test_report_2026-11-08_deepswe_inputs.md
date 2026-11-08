## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Revalidate final native reference/hash/exclusion chain and six-field typed contract after parent recovery; report no remaining local input blocker and provide the complete successful parity argv. |
| 2026-11-08 | Complete genuine native baseline/visual/filter receipts and ordinary full-source typed-factory parity; freeze102 excluded conversations,10008 excluded mask1 turns and868775 retained native eligible turns. |
| 2026-11-08 | Start authorized native full-source receipt preparation; diagnose original-template/runtime preflight failures without altering native code, and select the existing supported runtime and recipe tokenizer. |
| 2026-11-08 | Consume verified eight-source handoff, implement the native mask/receipt wiring, pass representative real parity and legacy regression; retain the full-source visual-receipt blocker. |
| 2026-11-08 | Trace D11's actual SWE-1003/delivery native loaders and record unverified eight-source candidate; preserve historical GLM code/evidence. |

# D11 DeepSWE inputs — native activation and historical source review

**Task ID:** T01-DEEPSWE-ACTIVATION (continues T01-DEEPSWE-REPLACEMENT).
**Current status:** **PASS_LOCAL_NATIVE_INPUT_ACTIVATION**. Genuine full-source native receipts and the ordinary full-source typed factory/parity passed. Parent-owned actual launch wiring, four-cell integration and final ticket acceptance remain outside this subtask. The source-only pre-acquisition review and earlier receipt-pending checks below are historical; the completed activation section owns current observations.

## Actual handoff, implementation and validation

### Native full-source activation phase — completed

The parent supplied the completed independent source audit: [deepswe-benchmark-training-overlap.json](evidence/deepswe-benchmark-training-overlap.json), SHA256 `75623c82a18a875c26310299e6dbbc3f13d582b9e005ba72d4ccce44a97866a0`. Its factual totals are9254 conversations,892620 raw assistant positions,878783 mask1 and13837 mask0; exact statement matches are zero, while absent task/repo/commit IDs leave identity/semantic claims limited. This work does not repeat its overlap scan.

The unchanged pinned APIs are `s4_swe_data_audit_1001.audit_sources` (baseline), `s4_swe_visual_audit_1001.audit_sources`, then `s4_swe_visual_filter_1001.filter_sources`. The filter cross-checks real baseline/visual receipts and source paths/size/mtime, and requires the visual audit's only failure to be `visual_payload_detected`. A zero-visual complete audit is not accepted by that pinned filter API; such an outcome must be reported, never converted to a synthetic failure/receipt.

Initial attempt used the Qwen original template through the native audit's Step wrapper. Native `_audit_file` failed at its controlled tokenizer preflight, before source bytes were scanned, with `TypeError: Can only get item pairs from a mapping.` Evidence: `/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-input-native-baseline-preflight-error.log`. The recipe's actual tokenizer exists readonly at `third_party/steptokenizer/tokenizers/Step4VMainlineVLLMMultiTurnMultiRoleXMLV0ReasonEffortSpacePreserveThinkingAdaptive` inside the native worktree. No tokenizer asset or template was edited.

A second preflight exposed a runtime contract difference: Transformers5.19.0 returns `BatchEncoding`, so the pinned audit's `len(result)` would count two dictionary keys instead of tokens. Native Docker requirements specify Transformers4.57.3; existing `/data/ycfeng/envs/openmopd-py312/bin/python` has4.57.6. With the actual recipe tokenizer, that runtime returns a genuine integer token list, **53 tokens** for the native controlled preflight. The production Qwen adapter/parity runtime remains the original Miles CPU environment and model/template contract.

Missing declared CPU dependencies were installed only in `/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-native-deps`: `ijson==3.6.0` (`yajl2_c`) and `loguru==0.7.3`. Existing environments, worktree/source files and main configs were not changed. `systemd-run --user --scope -p MemoryMax=30G /usr/bin/true` failed with `Failed to connect to bus: No such file or directory`; the native scans use inherited `prlimit --as=32212254720` and `timeout 1800s`, **workers=1**, one file at a time. Native imports use `python -B` / `PYTHONDONTWRITEBYTECODE=1`; native source files/worktree remain readonly.

Scan log: `/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-input-native-scan-supported-runtime.log`. Runtime evidence [deepswe-input-native-scan-runtime.json](evidence/deepswe-input-native-scan-runtime.json) retains the initial failed attempt. All three genuine receipts were published by unchanged native APIs; none is a test or relabeled cloud receipt.

| Genuine native output | Complete / expected outcome | Content SHA256 |
| --- | --- | --- |
| `evidence/deepswe-input-native-baseline-audit.json` | true;9254 trajectories,1866371 messages,892620 assistants,878783 mask1,13837 mask0 | `84e607ab08d43abac4569434f1f5e0660bf5aaaa3fceef08ee882c4ba52f8019` |
| `evidence/deepswe-input-native-visual-audit.json` | false with only `visual_payload_detected`;229 visual messages in102 conversations, no schema/signature failure | `094a95fb7b97202ded7a7283e14b053e83098d010a7d834b392ec0d68e75a437` |
| `evidence/deepswe-input-native-visual-filter.json` | true with `failure_codes=[]`; excludes102 entire conversations and10008 mask1 turns | `fcc3bdd9bcbda5ef5ac27e0246e9db9cba9493f48dfb90fb29d3eedbe158ab35` |

Frozen native visual-policy SHA256: **`086dcf806d9670985c0a5fedb058255eda8f4e1848cd0db558dd189968aa7470`**. All before/after source signatures match the exact local absolute paths/size/mtime. All three API source files matched pinned commit `f4522d451a9db59e5f1fee3990aedd73bc549002`; source hashes appear in runtime/config evidence.

| Recipe file index | Excluded conversations | Excluded mask1 turns | Retained native eligible turns |
| ---: | ---: | ---: | ---: |
| 0 | 0 | 0 | 93723 |
| 1 | 4 | 556 | 92525 |
| 2 | 6 | 696 | 91488 |
| 3 | 6 | 851 | 91125 |
| 4 | 15 | 1412 | 73950 |
| 5 | 29 | 2575 | 176335 |
| 6 | 29 | 2603 | 176323 |
| 7 | 13 | 1315 | 73306 |
| Total | **102** | **10008** | **868775** |

Exactly **9152 conversations /868775 native eligible turns remain before Qwen length rejection**. The full102 zero-based exclusion rows are retained per file in the filter receipt and [deepswe-input-activation.json](evidence/deepswe-input-activation.json). This is not a claim that868775 Qwen prefixes fit128K: only the recorded representative Qwen prefixes were encoded.

Native stage wall times were120.50s baseline,127.67s visual,127.26s filter; total **375.44s**. Peak RSS was533368 KiB in the parent and688992 KiB in a child. The30 GiB `RLIMIT_AS` is a **per-process address-space limit**, not an aggregate RSS measurement. The unchanged native calls executed under:

```bash
prlimit --as=32212254720 -- timeout 1800s /data/ycfeng/envs/openmopd-py312/bin/python -B -
```

```python
baseline.audit_sources(data_files=paths, output_path=str(baseline_path),
                       tokenizer_dir=str(native_repo / TOKENIZER_PATH),
                       workers=1, max_prompt_length=131071)
visual.audit_sources(data_files=paths, output_path=str(visual_path),
                     baseline_audit_path=str(baseline_path), workers=1)
filtering.filter_sources(data_files=paths, output_path=str(filter_path),
                         baseline_audit_path=str(baseline_path),
                         visual_audit_path=str(visual_path), workers=1)
```

`paths` is the ordered basename mapping of the unchanged verified `COPY_COMPLETE.json` to the exact local root. The `native_repo` and `TOKENIZER_PATH` are the readonly pinned worktree and its actual manifest constant; all receipt paths above are inside this task's evidence directory. The script set `PYTHONDONTWRITEBYTECODE=1`, `TOKENIZERS_PARALLELISM=false`, and prepended only the approved temporary dependency directory and native repo to `sys.path`. The baseline's4-per-file reservoir is its existing bounded tokenizer diagnostic, not the training source sampler; its Step tokenizer lengths are not Qwen lengths.

#### Final ordinary typed factory and Qwen parity

The exact representative parity command retained below was rerun with the **real full-source receipt**; the60s attempt timed out (`exit124`) without a new PASS artifact. The successful identical arguments used180s with no behavioral change. Complete successful parity argv:

```bash
prlimit --as=32212254720 -- timeout 180s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B \
  -m tests.manual.agent_opd.check_swe_inputs \
  --source-root /data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420 \
  --source-manifest /data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420/COPY_COMPLETE.json \
  --native-loader /data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/users/cj/opd/s4_swe_turn_data_1001.py \
  --native-loader-sha256 8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980 \
  --native-recipe /data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/baseline_new/mopd/turn_5teachers_data.py \
  --tokenizer /data/ycfeng/tmp/swe-model-pairs-20261103/Qwen/Qwen3.5-4B \
  --chat-template /data/ycfeng/sota-engine/miles/miles/utils/chat_template_utils/templates/qwen3.5_fixed.jinja \
  --rollout-max-context-len 131072 --turn-ordinals 1,2,8,32,64,last --file-last-prefixes 1,4,6 \
  --skip-masked-assistant-turns --evidence-prefix deepswe-input \
  --temporary-root /data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-parity-20261108 \
  --output-root task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence \
  --model-source-receipt task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/model-sources-exp-1108-144027-369537.json \
  --visual-filter-receipt /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/deepswe-input-native-visual-filter.json
```

All arguments are preserved exactly in [deepswe-input-final-parity-runtime.json](evidence/deepswe-input-final-parity-runtime.json). The executed wrapper read the historical recorded argv, appended the real receipt argument and called `subprocess.run` using the original Miles CPU Python. `TOKENIZERS_PARALLELISM=false` and `python -B` were inherited; source/population/native-source injection was **not** supplied to the actual full-source typed factory. Its construction performs its own full-source streaming hash verification, in addition to the CLI's initial verification.

Result **PASS**, exit0, **75.36s**, peak child RSS1289480 KiB (~1.23 GiB). `RolloutConfig` → `compute_custom_function_config` → registry factory produced the first original source UID `00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6:0:2`, Qwen4366 tokens, request `max_new_tokens=126706`. The final full-source identity explicitly records **`visual_filter_verified=true`**, **`native_source_injected_for_test=false`** and eight original files. The nine prefix lengths, tools/thinking/target identity, four independent cursors, actual ordered file/EOF boundaries and equality/overlength regressions all passed unchanged. Small regression fixtures and selected other-file subset probes remain explicitly scoped tests; they are not substituted into the ordinary full-source factory.

Final `deepswe-input-config.json` SHA256: `147ca3f3b0cf3f99d2f9ddbf8a4078e3e9c2c29acc52b559afec5a5059c17e1c`; final `deepswe-input-parity.json` SHA256: `f3919e1b1dce989532410757ebe910438767d082b1f8640c190712f6a0b7c5a0`. No adapter/check-script bug arose in this activation phase, so neither file was edited again. Old GLM input artifacts remained byte-identical.

After parent recovery, final handoff verification reran unchanged native `s4_swe_visual_filter_1001._read_references(baseline_path, visual_path, actual_signatures)` and `s4_swe_turn_data_1001.load_visual_filter_exclusions(filter_path, actual_filelist)`. It verified the full102 per-file exclusion indices, actual unchanged paths/size/mtime, baseline/visual/filter content-hash chain and policy, native loader/base/dependency hashes, original model tokenizer/fixed-template hashes, exact agreement among activation/config/ordinary typed-factory six fields, recorded final parity `PASS`/exit0, and all three protected historical GLM artifact hashes. **PASS_FINAL_HANDOFF_VERIFICATION** with `remaining_local_input_blockers=[]`; [deepswe-input-final-verification.json](evidence/deepswe-input-final-verification.json). This was a bounded receipt/stat/hash verification under the same `prlimit` and `timeout60s`, not a repeated source scan, Qwen population encoding, overlap scan or new factory run.

Final local checks passed: Python `compile()` for the two owned scripts; `json.loads` for nine final input/receipt/runtime artifacts; report Markdown fences/headline; and `git diff --check -- tests/manual/agent_opd/swe_inputs.py tests/manual/agent_opd/check_swe_inputs.py task_memory/task_2026-11-08_qwen35_swe_full_r256/test_report_2026-11-08_deepswe_inputs.md task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/deepswe-input-checkpoint.md`. No GPU/platform/cloud/auth/SSH operation or commit was performed by this subtask.

#### Phase checkpoint

- Mainline completed locally: native full-source receipts → ordinary full-source typed factory/parity. Parent actual launch activation remains next.
- D1/D3/D4/D5/D6/D7: CLEAR; no new scanner/framework/model changes, no unrelated fix or platform operation. D2: hypothesis tests narrowed source-template incompatibility, HF return-type incompatibility, and one missing declared dependency; the unchanged APIs and full-source parity now passed, so environment exploration and extra verification stop.
- Ticket01 owns final configuration consumption; canonical task records remain parent-owned. Spec S3 now records the actual mask/visual rules. Independent source-statistics/overlap are complete and referenced; no semantic-disjointness, whole-population Qwen tokenization or GPU acceptance claim is made.

The parent supplied zero-GPU copy receipt `evidence/deepswe-source-copy-exp-1108-205005-924420.json` and local root `/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420`. `COPY_COMPLETE.json` SHA256 is **`c23a757918031592f6440cd50f0ca750f5de07da5590e98c55eb6b5760f7f73d`**. The parity CLI stream-hashed the eight files, one at a time, and confirmed all hashes/sizes and total **16,559,540,463 bytes**. It did not compute a new full-source conversation/turn/overlap census; missing population counts are reported as `null`, not zero. The parent owns that census and overlap work.

The smallest supported wiring uses the **existing pinned SWE1003 module** in `/data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9`, not a new/copy sampler. `swe_inputs.py` exposes only two additional config fields:

```json
{
  "swe_source_root": "/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420",
  "swe_source_manifest": "/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420/COPY_COMPLETE.json",
  "swe_native_loader_path": "/data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/users/cj/opd/s4_swe_turn_data_1001.py",
  "swe_native_loader_sha256": "8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980",
  "swe_skip_masked_assistant_turns": true,
  "swe_visual_filter_receipt": "/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/deepswe-input-native-visual-filter.json"
}
```

This six-field **local activation contract passed** with the real receipt. `data_source_path` stays `tests.manual.agent_opd.swe_inputs.NativeSWEDataSource`; native `rollout_max_context_len`/`rollout_max_response_len` stay131072, `n_samples_per_prompt=1`, both thinking kwargs staytrue, and all models/math/protocol/benchmark settings remain unchanged. An ordinary parsed factory has no source-injection option; missing receipt with the mask policy enabled raises `Native mask-aware SWE inputs require a verified swe_visual_filter_receipt`. The private keyword-only source injection is restricted to CPU test calls and recorded as `native_source_injected_for_test=true`, `visual_filter_verified=false`.

The native package root is derived from the actual module's existing `playground/users/cj/opd` location for its CPU-only imports. No machine path is hardcoded in code. The parent must make that **existing readonly native worktree** and the data/receipt paths available to the worker. Effective source/base/visual-filter/visual-audit/source-manifest content hashes are recorded once in `deepswe-input-config.json`; all five native files matched pinned commit `f4522d451a9db59e5f1fee3990aedd73bc549002`. Native target policy, target mask, all-assistant ordinal and masked-context count are added to source metadata without changing required Qwen generation keys. `load()` still rejects training restore; `save()` remains audit-only.

### Real observations

All16 inspected conversations (first two from each original file) passed strict native scalar-mask/role selection and the **actual native `_scan_message` visual detector**. None of these16 contained a visual payload under that policy. This does not prove the other source conversations are non-visual. The eight first conversations have respectively **85/84,124/121,74/73,114/113,238/233,63/62,55/52,79/77** all/eligible assistant counts, confirming real masked assistants in every selected file. Each first system message has3 tool schemas; inspected `reasoning_effort` values are `null`.

| Actual prefix | Qwen tokens | Result |
| --- | ---: | --- |
| file0 / conversation0 / eligible turn1 | 4366 | Accepted; budget126706 |
| file0 / conversation0 / eligible turn2 | 5707 | Accepted |
| file0 / conversation0 / eligible turn8 | 35290 | Accepted; thinking/tool history retained |
| file0 / conversation0 / eligible turn32 | 87770 | Accepted; one masked assistant retained |
| file0 / conversation0 / eligible turn64 | 137552 | Overlength; focused run skipped21 remaining invalid turns |
| file0 / conversation0 / eligible turn84 | 160643 | Rejected; next conversation source row84 accepted |
| file1 / conversation0 / eligible turn121 | 184310 | Rejected; next conversation source row121 accepted |
| file4 / conversation0 / eligible turn233 | 256934 | Rejected; next conversation source row233 accepted |
| file6 / conversation0 / eligible turn52 | 87374 | Accepted; three masked assistants retained |

All nine selected raw prefix boundaries, native role/content conversion, target message hashes and original source UIDs were checked; eligible Samples matched actual prompt bytes/token hashes and remaining budgets. Original raw arguments remain JSON strings in history metadata; only the existing Qwen render-copy normalizes them. No original target assistant content is trained through this adapter, and no history truncation was used.

The focused middle-overlength run began at native source row63 and rejected **21 turns** through source row83. It accepted source row84 (`00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6:1:2`), prompt2896, budget128176, still at **sample/group slot0**. The three other last-turn checks each rejected exactly one turn and consumed no generation slot. JSON-character fault injection separately verified equality-at-limit rejection and consecutive skip accounting.

Four actual-source independent cursors started at UID `00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6:0:2`; advancing only one yielded counts **[2,1,1,1]**, with the other cursors independently reaching `:0:5`. File/EOF testing used **each actual file's real closing bracket** with explicitly test-positioned native cursors: all eight files appeared in recipe order and wrapped to the original first UID at epoch1. This is a bounded boundary check, **not a traversal of all intervening conversations or a full epoch**.

The historical typed `RolloutConfig` → `compute_custom_function_config` → registry factory fixture passed with the six fields and native visual validator. That controlled receipt used an actual source prefix plus one explicit `<image>` fault: the native constructor excluded the whole marked trajectory and produced the next unchanged prefix, budget126706. This proved API/validator wiring, **not a full-source receipt**. The completed activation section above separately records the ordinary real full-source receipt/factory PASS without test injection.

### Historical representative actual-parity command

Environment: local Python3.12.13 / Transformers5.19.0. `systemd-run --user --scope -p MemoryMax=30G ...` was attempted and failed with `Failed to connect to bus: No such file or directory`; the authorized `timeout 60s` fallback was used. Reads were streaming/one-file-at-a-time; no whole3.33GB file was JSON-expanded. The environment's `deep_ep is not installed` import warning was nonfatal.

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.check_swe_inputs \
  --source-root /data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420 \
  --source-manifest /data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420/COPY_COMPLETE.json \
  --native-loader /data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/users/cj/opd/s4_swe_turn_data_1001.py \
  --native-loader-sha256 8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980 \
  --native-recipe /data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/baseline_new/mopd/turn_5teachers_data.py \
  --tokenizer /data/ycfeng/tmp/swe-model-pairs-20261103/Qwen/Qwen3.5-4B \
  --chat-template /data/ycfeng/sota-engine/miles/miles/utils/chat_template_utils/templates/qwen3.5_fixed.jinja \
  --rollout-max-context-len 131072 --turn-ordinals 1,2,8,32,64,last --file-last-prefixes 1,4,6 \
  --skip-masked-assistant-turns --evidence-prefix deepswe-input \
  --temporary-root /data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-parity-20261108 \
  --output-root task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence \
  --model-source-receipt task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/model-sources-exp-1108-144027-369537.json
```

Observed result: **`PASS_REPRESENTATIVE_PARITY_VISUAL_RECEIPT_PENDING`**, nine recorded lengths as above. The final changed-scope rerun reused the exact retained `argv` and reproduced all nine prompt hashes; three native dependency hashes are present. Focused middle-rejection output is [deepswe-input-middle-overlength.json](evidence/deepswe-input-middle-overlength.json). Syntax `compile()` and `git diff --check -- tests/manual/agent_opd/swe_inputs.py tests/manual/agent_opd/check_swe_inputs.py` passed.

The historical missing-receipt typed full-source factory call with the six-field candidate and `swe_visual_filter_receipt=null` was explicitly executed and rejected with **`Native mask-aware SWE inputs require a verified swe_visual_filter_receipt`**. This guard fires before raw-file hashing/consumption. JSON/syntax checks and all three historical input-artifact SHA256 checks passed; no receipt fixture was substituted into that real candidate. The completed activation above uses the genuine full-source receipt instead of null and passes.

### Legacy behavior regression

The corrected regression command read the original frozen `input-parity.json` `argv`, retained its native loader/recipe/model/template values, changed only temporary/output directories, and appended `--evidence-prefix legacy-input`. The literal executed wrapper was:

```python
report = json.loads(Path("task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/input-parity.json").read_text())
argv = report["argv"][1:]
argv[argv.index("--temporary-root") + 1] = "/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-legacy-regression-20261108"
argv[argv.index("--output-root") + 1] = "/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-legacy-regression-20261108/evidence"
argv.extend(["--evidence-prefix", "legacy-input"])
subprocess.run([sys.executable, "-m", "tests.manual.agent_opd.check_swe_inputs", *argv], check=True)
```

Under the same `timeout 60s` Python, all seven old prefixes exactly reproduced UID, assistant index, raw/normalized history hash, target message hash, prompt token count/hash and budget: **1547,2221,28111,72857,107274,146694,181478**. The legacy typed config/default false path and native boundaries passed. The first manually entered regression command used a nonexistent recipe filename and failed `FileNotFoundError`; the recorded frozen argv supplied the actual path, with no code fallback or behavior change. The three old `input-config.json`, `input-source-manifest.json`, `input-parity.json` hashes remain unchanged. No existing Qwen qualification, shared canonical task record or active/inflight config was edited.

### Remaining parent acceptance

The actual local receipt, full-source typed factory and source-statistics/overlap prerequisites are now complete; parent also corrected spec S3's mask/visual selection. Parent must wire the verified six fields into actual four-cell launch configuration and accept worker consumption. These receipts bind exact **local absolute paths, sizes and mtimes**; a different mount path, changed mtime or new copy is not covered and requires the existing native audit/filter validation for that actual source state, not receipt relabeling. The full ordered native files/base/dependency hashes and input/model/template identities are already recorded. No raw-source acquisition, extra model revalidation or sampler implementation is missing from this local subtask. No new-data formal/GPU acceptance is claimed.

---

## Historical pre-acquisition review

Only local code/Git objects and deliberately synthetic fixtures were inspected/executed. No GPU, platform, cloud, auth, SSH, model, benchmark or native-external-recipe operations were performed. The shared requirements/spec/plan/progress/ticket/summary and active run configurations were not edited.

## Source identity and exact order

[evidence/deepswe-source-entry.json](evidence/deepswe-source-entry.json) retains the initial path/code review and links the actual verified input evidence. Its explicitly named `pre_acquisition_path_snapshot` preserves earlier unknown raw-identity fields; current measured hashes/sizes are in `deepswe-input-source-manifest.json`. It is not an activatable native visual receipt.

The source-list owner is the requested `dataset_paths.json` key `swe_1003_reused_by_20261021_step3p7_student.swe`; its local content SHA256 is `576045f3183b8a38ffbe47b5cee133f7fd60ba8708c928b672ae0325b8b177a3`. Native constants and the first published delivery entrypoint both match all eight paths **and order** exactly. There are eight unique paths and basenames. The repeated `mnt/posttrain` segment remains intact. The two `ds0p5` files are already downsampled upstream; no second downsampling is selected.

The originating SFT manifest records equal file sampling ratios and a common 0.4-epoch SFT factor (`s4_swe_source_manifest_1001.py:10–19,96–116`). These are source-provenance facts, not a new OPD stopping/sampling rule: the inspected OPD stream wraps at EOF and preserves existing multiplicity. No source glob, file sort, deduplication, status filter or new sampler is proposed.

## Native trace and reproducibility limits

The document-pinned reused code is commit **`f4522d451a9db59e5f1fee3990aedd73bc549002`**:

```text
s4_swe_opd_sft105_teacher400_1003.py
  -> s4_swe_opd_sft105_teacher400_1002.py
  -> s4_swe_opd_sft105_teacher400_1001.py:75 DataConfig(LossMaskedSWEDataConfig)
  -> s4_swe_turn_data_1001.py:489 LossMaskedSWEDataConfig
  -> :529 MaskAwareSWETurnSource
  -> :544 DPMux(TurnBalancedTrajectoryBlockMixer(...))
```

Those files are not present as working-tree files on the local lookup branch; the review read their exact `git show COMMIT:PATH` bytes without modifying that branch or executing full recipes.

Key computed **content SHA256** values (not Git blob IDs):

| Pinned file | SHA256 |
| --- | --- |
| `playground/users/cj/opd/s4_swe_source_manifest_1001.py` | `0a46156646a098161151b4ba311a1811e1c61c5e8ab950f3a3617ecf7e67df16` |
| `playground/users/cj/opd/s4_swe_turn_data_1001.py` | `8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980` |
| `playground/baseline_new/mopd/turn_5teachers_data.py` | `164eba4694e62d01d5d4565ce4194f58b4b2f8abd03cda88c67620b4dd77964f` |
| `playground/baseline_new/mopd/online_turn_loader.py` | `0c11561f33dacf1a15cd804dbd2f4feed4d1c33734bfaea7a416fdf1efaa740f` |

The source-manifest docstring's warning about the generic source not honoring loss masks (`:21–28`) does **not** describe the overriding `LossMaskedSWEDataConfig` used by 1003. The inherited implementation settles target selection.

The delivery document's reported run commit **`abf1271d6bf47056a241bccfc30bb50e92e6a9c1`** does not contain the stated Getianyi entrypoint in available local Git objects. Therefore this review does **not** certify the binary/effective runtime that ran on 2026-10-21. It verifies the document-pinned reused SWE1003 source contract and the corresponding delivery code published later.

The first published delivery entrypoint is commit **`7e9393e89eeff0c85bd66e7f127103d6e516b644`**, dated 2026-10-26:

- `playground/users/getianyi/mopd/step4/step4_teacher_dsa_step3p6_sametopo_online_reasoning.py`, SHA256 `be6172cbed136b75d6353c67041537211eb7efca513a3f56c7687ee72776468d`.
- Its `ReasoningDataConfig:369–429` selects the same ordered files, sets `skip_masked_assistant_turns=True`, validates the visual receipt, maps exclusion rows **by file**, and delegates to the streaming parent.
- The parent `turn_5teachers_data.py:495–549` retains `online_turn_streaming=True`, block size 8, and passes the two native source-selection parameters.
- Its standalone stdlib `online_turn_loader.py` has SHA256 **`7daf23d39de4f6884c008858a0b4329049133535a1465b41c00a565e27782685`**. This is a direct-load candidate; it already implements the required native mask/exclusion behavior, so there is no reason to copy/reimplement its sampler.

## Behavior compared with the historical 0710 adapter

| Area | Inspected native DeepSWE contract | Current Miles adapter / needed attention |
| --- | --- | --- |
| Raw schema | Top-level JSON array; each item a conversation list; message dicts with `role`/`from`; **every message has scalar integer `loss_mask` 0/1** (`s4_swe_turn_data_1001.py:106–129`) | Actual eight files not yet audited. Do not coerce bool, string, vector, missing or fractional masks. |
| Target selection | Only assistants with `loss_mask=1`; positions remain in original message order | `swe_inputs.py:171` constructs the unmasked generic source. Merely changing eight paths would wrongly target mask=0 assistants. |
| Historical messages | Prefix is copied intact, including masked assistants, reasoning/tool calls and tool replies; original target is replaced with an empty assistant | Reuse existing history/render/identity functions. **Never remove mask=0 messages from history.** |
| Visual filtering | Exclude the **entire source trajectory** using verified per-file source-row indices (`s4_swe_turn_data_1001.py:180–306,353–395`) | Current adapter supplies no exclusions. No exclusion indices or zero-visual claim can be inferred before data/receipt verification. |
| Source order | Ordered eight-file list → ordered conversations → eligible assistants; native cursor wraps to epoch+1 | Base cursor/source/mixer AST equals 0710; no random/shuffle branch is present. |
| Mixer / DP | One group, weight1, block8, DPMux; one-source mixer always chooses that source | Existing direct source remains appropriate if the **native eligibility/exclusion parameters** are wired. A DPMux(1,0) wrapper does not change presentation order. |
| Ordinals / identity | `assistant_turn_ordinal` counts eligible turns; `source_assistant_turn_ordinal` counts all assistants; `context_masked_assistant_count` records retained masked history | Keep original `assistant_turn_index` in UID; capture new native policy/ordinal metadata. Do not equate eligible ordinal with all-assistant ordinal. `source_row_index` advances only for emitted eligible turns, before Qwen length rejection. |
| Tools/thinking | SWE1003 `tokenize_swe_prefix:54–82` forwards `tools` **or `tool_schemas`**, first-message `preserve_thinking`, and optional `reasoning_effort` | Current adapter reads only `history[0].tools`. Inspect actual field distribution before a minimal normalization change; do not drop schemas. Qwen's fixed template/thinking contract remains unchanged. |
| Step rendering versions | SWE1003 uses its adaptive prefix helper; first published delivery's generic template caller omits explicit tools (`turn_5teachers_data.py:469–471`) | Do not claim Step/Qwen prompt byte or token equality. Record actual field/model-specific rendering differences without changing models/template by this data amendment. |
| Length | SWE1003 used `max_prompt_len=256*1024-1` with `>` rejection; first published delivery used256K | This task's approved Qwen limit remains **prompt<131072**, generation budget `131072-prompt`; do not inherit256K or reserve8192 tokens. |
| Upstream resolved/garble/datapipe | Already encoded in the exact delivery paths and source masks | No extra resolved-status filter, garble rewrite, reprocessing or second ds0p5 sampling. |

The pinned SWE1003 generic base has different bytes from 0710 only because it adds `iter_json_array_item_spans` for an indexed path. AST comparison found **identical** `JsonArrayRecord`, `SequentialJsonArrayCursor`, `OnlineTrajectoryTurnSource`, `TurnBalancedTrajectoryBlockMixer`, `message_role` and `source_meta_from_trajectory`. The actual selected SWE1003 config rejects `online_turn_streaming=False` (`s4_swe_turn_data_1001.py:514–517`), so that indexed helper does not change this stream.

The default native visual receipt is `/mnt/posttrain-release/cj/opd/s4_swe_1001/data/swe_visual_filter_1001.json`; it was **not read** in this local-only task. Its validator binds absolute paths, file size and mtime before/after scan, filter policy/version and per-file indices. A receipt for original cloud paths cannot simply be relabeled for local copies. The parent must provide an authorized receipt/correspondence or allow the existing native scan to establish local-copy exclusions; no empty exclusion default is accepted as proof.

## Local verification and observations

All checks used `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python` (Python3.12.13), under `timeout 60s`, in `/data/ycfeng/sota-engine/miles`. Static Git reads and the stdlib source probe did not need Transformers, Torch, conda activation or the training runtime.

Exact source-read invocation pattern:

```bash
git -C /data/ycfeng/steptron/.worktrees/yc-mopd-learning-dynamics-s4-branch show \
  f4522d451a9db59e5f1fee3990aedd73bc549002:playground/users/cj/opd/s4_swe_turn_data_1001.py
git -C /data/ycfeng/steptron/.worktrees/yc-mopd-learning-dynamics-s4-branch show \
  7e9393e89eeff0c85bd66e7f127103d6e516b644:playground/baseline_new/mopd/online_turn_loader.py
```

The executed probe used `subprocess.check_output(['git','show',f'{commit}:{path}'],cwd=repo)` to read each pinned file. It computed `hashlib.sha256(bytes).hexdigest()`, compared `ast.dump(node, include_attributes=False)` for base definitions, registered each in-memory module in `sys.modules` **before** executing its verified Git bytes, and instantiated the actual native classes. It did not reconstruct or stub their selection/cursor code. Source manifests and delivery path constants were evaluated only from inspected constant assignments; no full recipe imports were executed.

The deliberately synthetic two-file fixtures are `/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-source-review-fixture/part{0,1}.json`. They are **not the eight requested raw files**. The actual constructor calls were:

```python
kwargs = dict(filelist=files, domain="reasoning", source_group="swe",
              source_load_path=None, source_load_safetensors=None)
masked = swe1003.MaskAwareSWETurnSource(
    **kwargs, excluded_source_item_indices=((2,), ()))
delivery = first_published.OnlineTrajectoryTurnSource(
    **kwargs, skip_masked_assistant_turns=True,
    excluded_source_item_indices_by_file={0: [2]})
historical = pinned0710_equivalent.OnlineTrajectoryTurnSource(**kwargs)
```

| Check | Expected / passing condition | Observed | Result |
| --- | --- | --- | --- |
| Exact source list | All eight paths and order match requested key, SWE1003 constants and delivery constants | All equal; eight unique paths | PASS |
| Base behavior identity | Compare AST, not merely filenames or SHA labels | Six core definitions identical; only indexed helper added | PASS |
| Native target/EOF parity on synthetic fixtures | SWE1003 subclass and delivery native flags produce identical full objects | Six outputs equal; target indices **4,6,1,4,6,1**, epochs **0,0,0,1,1,1** | PASS, synthetic only |
| Historical-loader contrast | Mask=0 assistant must not become a new-data target | Historical generic source starts at index**2**; masked native starts at index**4** | PASS, synthetic only |
| Whole-trajectory and no-eligible skipping | Per-file excluded row and mask=0-only conversation are skipped on each epoch | Two excluded skips and two no-eligible skips across the probe | PASS, synthetic only |
| Prefix retention | Earlier masked reasoning, JSON-string tool arguments and reply IDs survive verbatim | All asserted equal to fixture prefix | PASS, synthetic only |
| Strict mask validation | Both native variants reject bool/string/missing/vector/out-of-range mask | `True`, `"1"`, `None`, `[1]`, `2` each rejected by both implementations | PASS, synthetic only |
| Native prefix kwargs | Recording tokenizer sees source tools, thinking and effort kwargs | `tools`, `preserve_thinking=True`, `reasoning_effort="high"` forwarded | PASS, capture only; no real token lengths |
| Direct native import | Standalone first-published loader runs with stdlib only | Actual module bytes executed successfully after registration | PASS |
| Receipt integrity / old behavior preservation | Every recorded code hash matches pinned Git bytes; historical protected files unchanged | Eleven code hashes and five existing adapter/CLI/input-receipt hashes match | PASS |
| Reject unverified activation | Existing real adapter must not consume this non-COMPLETE source candidate | `load_source_population(...)` raises **`SWE source manifest is not COMPLETE`** before opening source files | PASS |
| Actual DeepSWE schema/bytes/parity | Read the eight verified raw sources and compare actual eligible boundaries/rendering | Raw data not supplied locally; no actual records or Qwen lengths checked | **BLOCKED** |

The source probe reported `PASS_LOCAL_SOURCE_REVIEW_ONLY` and `PENDING_RAW_DATA`. Its retained observations and protected-file hashes are in `deepswe-source-entry.json`. It does **not** prove all source records satisfy the documented schema, that all visual exclusions are empty, or that native rendering equals Qwen bytes. No raw SHA256/count was invented.

The final receipt validation re-read the pinned Git objects and five protected local files, then invoked the **existing** `tests.manual.agent_opd.swe_inputs.load_source_population` against the candidate and a synthetic local root. It returned PASS with `ordered_paths=8`, `verified_pinned_code_hashes=11`, `historical_protected_files_unchanged=5` and the expected candidate rejection. Importing the existing Miles module emitted the environment's nonfatal `deep_ep is not installed` warning; no GPU operation or native training execution was involved.

## Candidate and minimal next step

The candidate in `deepswe-source-entry.json` deliberately has `null` local root/manifest/loader path and `activation_ready=false`. The current four-field `SWEInputConfig` and adapter remain unchanged, preserving historical inflight GLM behavior. Current code is **not** new-data ready: it neither passes the native mask/visual constructor fields nor exposes them through the candidate config.

Once the parent provides the verified local root:

1. Match each file, in exact order, to its original path and measured SHA256/size; establish the native scalar-mask/schema and visual-exclusion receipt for those bytes. Distinguish all assistants, eligible assistants, excluded trajectories and Qwen-overlength rejects. Do not propagate old GLM population or overlap counts.
2. Reuse `swe_inputs.py` with the smallest explicit wiring of **existing native** `skip_masked_assistant_turns=True` and verified `excluded_source_item_indices_by_file`. The verified standalone delivery module already supplies these behaviors; do not copy its scanner/sampler or add dataset-name branches/new generic configuration machinery. Preserve the old false/no-exclusion path for historical qualification.
3. Reuse `check_swe_inputs.py`, replacing its all-assistant/first-conversation assumptions and mask-less fixtures with the actual native eligible selector/source identities. Its current default probe ordinals also assume a156-assistant GLM first conversation; do not use them blindly for DeepSWE. Write **deepswe-*** evidence without overwriting any `input-*` artifact. Verify actual tools/thinking, mask=0 history, long-prefix skip, next conversation/file/EOF and four independent cursors using the real Qwen tokenizer and unchanged thinking/template/128K settings.
4. Parent updates `spec.md:77` from “全部assistant turns” to native eligible `loss_mask=1` turns plus verified whole-trajectory visual exclusions, completes/assigns the replacement-data overlap check, and activates the new four-cell configurations only after actual source acceptance.

The original model identities, mathematics, protocols and benchmark stay unchanged. The old GLM adapter report/receipts and captured red/green banks retain **historical GLM provenance only**. No result here recertifies those banks as DeepSWE or closes the reopened Ticket01.
