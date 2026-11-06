## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Add preparation/export/monitoring CPU results, repaired guard and symlink/report regressions, full zero-GPU population/asset evidence and cleanup receipts. |
| 2026-11-06 | Record the reproduced single-token defect, verified repair, personal API access and blocked cloud probe. |

# P2 implementation and prerequisite verification

## Single-response-token repair — PASS on CPU

Task `QWEN-P2-ONE-TOKEN`, agent session `ses_e4f8ab166ffefjF8IxD4g2CcAz`, changed only:

- `miles/backends/training_utils/loss/hub/logit_processors.py`
- `tests/fast/backends/training_utils/loss/hub/test_backend_loss_normalization.py`

The scorer can already return `[R]`. Applying `squeeze(-1)` to `[1]` made a scalar that could not be concatenated. `reshape(-1)` preserves the response dimension for both supported scorer layouts, `[R]` and `[R, 1]`. The existing strict-xfail regression is now a passing test covering singleton/multiple response lengths, both normalization modes, chunked/unchunked scoring, exact probabilities, entropy, loss and gradients. No mask, probability formula, CP mapping or denominator changed.

Working directory: `/data/ycfeng/sota-engine/miles`. Interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python 3.12.13, torch 2.11.0+cu130. This is the CPU environment, not the pinned worker image. The following shared command prefix and selector reproduce the recorded commands:

```bash
BASE=(timeout 300s env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -rxX -p no:cacheprovider -o addopts=)
T=tests/fast/backends/training_utils/loss/hub/test_backend_loss_normalization.py::TestBackendLossNormalization::test_single_response_token_preserves_a_concatenable_log_probability_dimension
B=/data/ycfeng/tmp/opencode-v2-tmp/opencode
"${BASE[@]}" --basetemp="$B/pytest-qwen-p2-one-token-repro-20261106-a" "$T"
"${BASE[@]}" --runxfail --tb=long --basetemp="$B/pytest-qwen-p2-one-token-repro-20261106-b" "$T"
"${BASE[@]}" --tb=short --basetemp="$B/pytest-qwen-p2-one-token-red-20261106-c" "$T"
"${BASE[@]}" --basetemp="$B/pytest-qwen-p2-one-token-green-20261106-d" "$T"
```

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Original strict xfail | Existing defect reproduced | 1 xfailed, 2.13 s | PASS: reproduction |
| Original test, xfail disabled | Real concatenation failure | 1 failed, 2.18 s; `zero-dimensional tensor (at position 0) cannot be concatenated` | PASS: reproduction |
| Expanded regression before repair | Four parameter cases fail | 4 failed, 2.23 s | PASS: regression sensitivity |
| Expanded regression after repair | All four cases pass | 4 passed, 15.83 s | PASS |

Focused verification used the same prefix:

```bash
"${BASE[@]}" --basetemp="$B/pytest-qwen-p2-one-token-focused-20261106-e" \
  tests/fast/backends/training_utils/loss/hub/test_backend_loss_normalization.py \
  tests/fast/backends/training_utils/test_chunked_log_probs.py \
  tests/fast/backends/training_utils/loss_hub/test_logit_processors.py \
  tests/fast/examples/infra_features/train_infer_mismatch_helper/test_mis.py
"${BASE[@]}" --basetemp="$B/pytest-qwen-p2-one-token-cp2-20261106-f" \
  tests/fast/backends/training_utils/loss/test_loss_cp2_consistency.py
git diff --check -- miles/backends/training_utils/loss/hub/logit_processors.py tests/fast/backends/training_utils/loss/hub/test_backend_loss_normalization.py
```

Observed: **29 passed**, 21 warnings, 12.02 s; **3 passed**, 16 warnings, 44.15 s; diff check PASS. The latter suite covers CP=2, an empty local response and FP32/BF16/FP16. The primary agent inspected the two-file diff against the failure and requirements. Full test stdout was not copied into this report; these are the executing agent's command/output receipts. No GPU numerical acceptance follows from these results.

## Personal API and asset/runtime probe

Local credential files and `/data/ycfeng/tmp/stepmind-env/bin/python` exist, are readable and nonempty; credential contents were not displayed. Following the handbook proxy initialization, a personal `brainpp.rjob.RJobClient` queried the exact historical job `exp-1105-191135-503140` using `get_namespaced_custom_object(..., _request_timeout=(5,15))`:

```json
{"api":"reachable","name":"exp-1105-191135-503140","creator":"i-fengyicheng","phase":"Succeeded"}
```

This passes local authentication/API reachability only. It does not qualify new assets, the current image or free GPU quota.

An SSH personal-directory read timed out at 60 seconds; the isolated command below returned 124 without output:

```bash
timeout 25s ssh -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=2 shai-ycfeng id -un
```

Prepared `tests/manual/agent_opd/inspect_qwen35_assets.py` to inspect only the personal cloud namespace: exact model metadata, indexed shard sizes and the eleven manifest-listed source-file sizes. System Python `ast.parse` passed; the actual manifest has a list of eleven `files` with `path`, `sha256` and `size` fields. This preparatory syntax check is not a cloud result.

A local Python `spawn_tasks`/RJobBackend probe was requested with zero GPUs, eight CPUs, 64 GB, one replica, codesign, the pinned image from the resume report, current-machine `/data/ycfeng` NFS source and the personal cloud mount. Its worker commands were the new asset inspector followed by the existing `runtime_probe.py`, writing selected evidence under this task's `evidence/` directory. The tool rejected the submission command before returning any RJob receipt:

```text
grill-me is user-invoked only. Agent skill calls and direct file/shell reads are forbidden; use only instructions supplied by the user's /grill-me command.
```

Historical status at that attempt: **BLOCKED at the tool layer**. The authorization and actual repair below supersede this blocker; the rejected operation was not routed through a different path.

## Prepared population and text-only export — CPU PASS

`QWEN-P2-DATA` (`ses_e4f8ab177ffe1xOtrk8j0VIVcF`) implemented `prepare_qwen35.py`, reusing the original GLM source checks and fixed Qwen template. It validates source/group membership, renders every selected manifest entry without a GLM-length prefilter, reserves complete monitoring groups and writes datasets only when coverage passes. Original histories and targets remain provenance; only fresh completions train. The existing GLM CLI remains covered.

```bash
env TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_agent_opd_qwen35_preparation.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-p2-data-pytest-20261106-c -p no:cacheprovider -o addopts='' -q
```

Observed **21 passed, 6.45 s**. All 1,024 local manifest membership records and 175 benchmark-exclusion pins passed. Four actual local fixtures retained all historical reasoning and reproduced 86,669 / 97,254 / 95,907 / 93,256 Qwen tokens. These local checks preceded, and did not substitute for, the actual cloud population audit below.

`QWEN-P2-HF` (`ses_e4f8ab167ffeaA07chV3shmdoG`) implemented `qwen_export.post_save` through the existing native post-save hook. It validates decoder coverage/names/shapes/dtypes, retains tokenizer/RoPE, removes visual/MTP tensors, maps `model.language_model.*` to `model.*`, writes official `qwen3_5_text` / `Qwen3_5ForCausalLM` configuration and rebuilds the index. Successful packaging still records `reload_verified=false` until real model inference is tested.

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_qwen_text_export.py tests/fast/backends/megatron_utils/test_hf_only_save.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/pytest-qwen-text-export-qwen-p2-hf-4 -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/pytest-cache-qwen-p2-hf-4 > /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-p2-hf-tests-4.log 2>&1
```

Observed **22 passed, 2 warnings, 4.31 s**. FP32/BF16 × tied/untied tiny hybrid models preserve exact parameters, fixed-input logits and greedy token IDs through actual HF save/reload. Actual 4B metadata has 426 decoder tensors plus the valid tied-head alias, matching 427 logical text-schema tensors; 297 visual and 15 MTP tensors are excluded. The real 4B tokenizer's 248,077 vocabulary entries and an 18-token thinking prefix match after text-config conversion. This is not real 4B/27B weight reload or Megatron conversion acceptance.

### Review repairs: auxiliary report and metadata symlinks

The reviewer identified an auxiliary JSON-write exception that could escape the soft export verdict. Fault injection reproduced both paths before repair: **2 failed, 17 deselected**, with `OSError: Injected auxiliary report disk failure` at the first report write and the contract-error report write. All auxiliary report writes now use one non-blocking writer; actual checkpoint conversion I/O failures still propagate.

```bash
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_qwen_text_export.py -k auxiliary_report_io_failure --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/pytest-qwen-report-io-red -p no:cacheprovider -o addopts='' -q --tb=short
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_qwen_text_export.py tests/fast/backends/megatron_utils/test_hf_only_save.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/pytest-qwen-report-io-green -p no:cacheprovider -o addopts='' -q
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_qwen_asset_inspection.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/pytest-qwen-assets-symlinks -p no:cacheprovider -o addopts='' -q
```

After repair: **24 passed, 2 warnings, 3.13 s** for export/native-save coverage. Asset inspection: **3 passed, 2 warnings, 0.18 s**. Config and index paths are resolved and authorized before reading; escaped symlinks are rejected before content access. Requested model directories may include only explicitly approved source roots. All referenced cloud source files remain personal.

## V2 tool-guard repair — PASS

The user authorized the scoped repair. `QWEN-P2-GUARD-FIX` (`ses_e4e9af2b8ffenggXFCSIr30twC`) corrected `/home/brainpp/.opencode-v2/xdg/config/opencode/plugins/grill-me-access.js`: shell glob expansion is distinguished from quoted/heredoc literals, while protected paths, recursive ancestor checks, aliases and manual invocation gates remain enforced. No protected skill content was read, and v1 was unchanged.

From `/home/brainpp/.opencode-v2/xdg/config/opencode` with Node v20.11.0:

```bash
node --experimental-vm-modules --test tests/test_skill_access.mjs
node --check plugins/grill-me-access.js
```

Observed **38/38 passed** with mocked protected filesystem access. A harmless real Python heredoc and `curl --noproxy '*' --version` both passed from the original `/data/ycfeng` cwd after automatic hot reload. No service restart or cwd workaround was needed. Exact diff and original backup: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/QWEN-P2-GUARD-FIX.diff` and `grill-me-access.QWEN-P2-GUARD-FIX.original.js` in that same directory.

The first restored launch exposed a separate local prerequisite: `stepmind_control.py:393` requires `os.environ['EXP_ID']`; `cfg.exp_name` alone is insufficient. It failed with `KeyError: 'EXP_ID'` before job creation. Exporting `EXP_ID=qwen35-assets-runtime-population` fixed that demonstrated cause; no SDK fallback was introduced.

## Actual zero-GPU prerequisite job — PASS at CPU/data scope

Job **`exp-1106-233008-986003`**, submitted through local `spawn_tasks`/Python RJobBackend as **i-fengyicheng**, used 0 GPU / 8 CPU / 64,000 MiB, one codesign replica. The selected image was `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`. Platform metadata verified current-host NFS `100.96.128.195:/data/ycfeng:/data/ycfeng` on `kun-workspace-vgen2`. Mount requests were the approved codesign volume plus `juicefs+s3://aliyun-sh/posttrain:/mnt/posttrain`; source paths are in requirements.

Worker commands used `/opt/sglang/bin/python3 -B`, repository `/data/ycfeng/sota-engine/miles` on `PYTHONPATH`, offline Hugging Face, disabled tokenizer parallelism and worker-local `/var/tmp/qwen35-$KUBEBRAIN_RJOB_NAME` caches:

```bash
/opt/sglang/bin/python3 -B /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/inspect_qwen35_assets.py --model Qwen3.5-4B /mnt/codesign-exp/ycfeng/opd-assets/models/Qwen/Qwen3.5-4B/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a --model Qwen3.5-27B /mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-27B/model --model Qwen3.5-35B-A3B /mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-35B-A3B/model --model Qwen3.5-397B-A17B /mnt/codesign-exp/pj_dflash_edge_i-pengyajuan/models/Qwen3.5-397B-A17B --manifest /data/ycfeng/steptron/.worktrees/behavior-turn-replay-step3p6/task_memory/task_2026-10-25_swe_behavior_turn_replay/evidence/glm-replay-subsets-20261104.json --report /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/evidence/assets-exp-1106-233008-986003.json
/opt/sglang/bin/python3 -B /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/runtime_probe.py --report /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/evidence/runtime-exp-1106-233008-986003.json
/opt/sglang/bin/python3 -B /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/prepare_qwen35.py --manifest /data/ycfeng/steptron/.worktrees/behavior-turn-replay-step3p6/task_memory/task_2026-10-25_swe_behavior_turn_replay/evidence/glm-replay-subsets-20261104.json --glm-tokenizer /mnt/codesign-exp/ycfeng/steptron/behavior-turn-replay-step3p6/glm-native-20261103/models/zai-org/GLM-4.7-Flash/7dd20894a642a0aa287e9827cb1a1f7f91386b67 --qwen-tokenizer /mnt/codesign-exp/ycfeng/opd-assets/models/Qwen/Qwen3.5-4B/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a --output-root /mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/population-exp-1106-233008-986003
```

Actual runtime: Python **3.12.16**, torch **2.14.1+cu130**, transformers **5.19.0**, Ray **2.58.1**, SGLang **0.5.24.dev80+g056f871**, polars **1.42.1**, safetensors **0.8.0**. Source HEAD was `315a8724` with the explicitly recorded uncommitted task-preparation files. CPU imports/parser checks passed; CUDA availability false and no GPU-module validation were expected for this zero-GPU job.

| Asset | Indexed shards | Actual bytes | Availability |
| --- | ---: | ---: | --- |
| Qwen3.5-4B | 2 | 9,319,828,096 | All exist |
| Qwen3.5-27B | 11 | 55,563,022,432 | All exist |
| Qwen3.5-35B-A3B | 14 | 71,903,878,016 | All exist |
| Qwen3.5-397B-A17B | 94 | 806,796,241,352 | All exist |

All four sources share tokenizer SHA256 `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42`, tokenizer-config SHA256 `316230d6a809701f4db5ea8f8fc862bc3a6f3229c937c174e674ff3ca0a64ac8`, and template SHA256 `a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715`. All eleven original source files match their declared sizes. Shard presence/size does not establish full model loadability or native numerical agreement.

Actual population: **1,024** rendered source entries; eligible **short 8 / medium 206 / long 804**; **6** over-budget exclusions. Monitoring selects **8/8/8 prefixes** from **4/8/8 groups**. Excluding another **70** prefixes in complete monitoring groups leaves **924** training prefixes across **264** groups. Every source/group/inherited-evaluation overlap list is empty. The earlier GLM-derived short-stratum concern is conclusively replaced by these Qwen measurements; eight distinct groups per stratum were never required.

- Shared `train.jsonl`: SHA256 `1c0742224d0a4ca3c3ce5c07fd6108fe7a83ee0d2871fcdc31545d0c97118f21`, 924 rows.
- Shared `monitor.jsonl`: SHA256 `09d8876bd90d4eac3b989b98812c08c005d8e2a1b782718d33acf970ac996dc6`, 24 rows.
- Both are under `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/population-exp-1106-233008-986003/`, alongside the full `population.json` with identities, lengths and exclusion evidence.
- The fixed template is SHA256 `ca447731ed457cb460b7522ea9edb986d52e4ea62c5d8482365146592d69b1b9`, with both `preserve_thinking` and `enable_thinking` true.

Selected evidence: [assets](evidence/assets-exp-1106-233008-986003.json), [runtime](evidence/runtime-exp-1106-233008-986003.json), [platform identity/mount/resources](evidence/platform-exp-1106-233008-986003.json), [population](evidence/population-exp-1106-233008-986003.json). Local launcher stayed alive through success (23:40:24 local time), then its native exit cleanup ran. A subsequent personal API inspection confirmed **RJob Succeeded / replica SUCCEED**; launcher exit was 0. Exact inspection command after handbook proxy initialization:

```bash
timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -B /data/ycfeng/steptron/tests/integration/inspect_stepmind_personal_job.py exp-1106-233008-986003
```

The inspector retained 11 log rows / 110,472 bytes at `/data/ycfeng/tmp/exp-1106-233008-986003.log`. Container exit-code details were not returned by this inspection; no separate container-code assertion is made. No training GPU was allocated and no student update or full-model inference was performed.

## Native fixed-monitoring integration — combined CPU PASS, review fixes pending

`QWEN-P2-SCORE-RPC` (`ses_e4e9609a8ffe5AnxsFNmb1aKAe`) and `QWEN-P2-EVAL-INTEGRATION` (`ses_e4e90ed01ffefB7zW2Ke1EOk6A`) added the read-only actor/controller call and optional synchronous shared-engine eval integration. Only PP-last/TP0 emits scored references; the native CP zigzag layout and actual model-companion version are recorded. Original eval Samples remain separate from the training source and preserve raw masks/tokens/versions. Native training schedule trimming is disabled for all 24 monitoring rows. Evidence output uses native rank dumps with `eval_{escaped_dataset}_{rollout_id}` names. No optimizer/backward/publication is invoked by scoring.

Primary combined command after the schema/rank/delayed-split integration corrections:

```bash
env TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode RAY_TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/backends/megatron_utils/test_score_log_probs.py tests/fast/ray/train/test_score_log_probs.py tests/fast/ray/rollout/test_eval_train_data.py tests/fast/ray/rollout/test_eval_dispatch.py tests/fast/test_train.py tests/fast/utils/test_eval_train_log_probs_args.py tests/fast/ray/rollout/test_rollout_executor_store_refs.py tests/fast/ray/rollout/test_rollout_executor.py tests/fast/ray/rollout/test_rollout_executor_rpc_surface.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-p2-combined-score-eval -o addopts=''
```

Observed **132 passed, 16 warnings, 50.84 s**, exit 0. Real Gloo TP/CP/DP, real Ray/cell, 24-row loading, native dump/RPC serialization and state-preservation fault injection are covered. The CPU environment lacks Megatron; the actor fixture executes production methods extracted from AST with SDK/GPU boundaries replaced. This is not native Megatron/H800 or Mooncake acceptance. Broader optional argument checks were unavailable because `megatron` and `miles_ext_kernels` are absent; those dependency failures were not repaired or counted as passes.

Phase review `QWEN-P2-MONITOR-REVIEW` (`ses_e4e792d5affeGsj3IUWlUanlWV`) found two actionable issues: a failed/cancelled cell call can let the driver restore inference before slow remote scoring siblings finish, and a recovered observer-offload exception can still escape the soft gate. Both are assigned back to their owners for a focused fix and affected regression. Default Ray reference counting means the hidden partial-ref concern alone is not evidence of a permanent leak; other transports remain unverified. Native D8 validity also requires complete original eval artifacts, not filtered/sanitized loss metrics.

## User-requested local artifact cleanup — PASS within verified scope

`QWEN-LOCAL-DISK-CLEANUP` (`ses_e4e952011ffe8xhc4aK4k5uzXI`) deleted 154,955,776 allocated bytes of completed Qwen test artifacts, then 5,615,460,352 bytes of completed sklearn caches and byte-identical duplicate EP ledgers. Total attributed deletion is **5,770,416,128 bytes (about 5.37 GiB)**. The second deletion's adjacent `df` free-space readings were **104,587,931,648 -> 110,170,853,376 bytes**, 91% -> 90% used. Other concurrent cleanup gains are not attributed to this task.

The selected original HF log and protected current outputs were unchanged; 263 processes had no references to the second deletion targets, and retained-file/ledger hashes matched. Unreplicated profiling traces, source trees, environments, models and active outputs remain intact. Exact deleted paths, per-item sizes, commands and before/after evidence are in [cleanup-20261106.json](evidence/cleanup-20261106.json). No cloud operation was performed by the cleanup agent.
