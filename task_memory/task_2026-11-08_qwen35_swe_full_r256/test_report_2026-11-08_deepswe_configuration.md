## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Parent rechecks four real formal argv/source/hook contracts and records CPU versus GPU validation limits. |
| 2026-11-08 | Activate the genuine native visual receipt in four real smoke argv configurations;18 final launcher regressions pass. |
| 2026-11-08 | T02-DEEPSWE-CAPACITY-CONFIG: derive the existing two-update/256-slot smoke for current inputs; verify both native custom-hook registrations and no-submit dry-runs. |
| 2026-11-08 | Wire the native masked-target/visual-receipt fields through the real launcher parser; 18 CPU regressions passed. |
| 2026-11-08 | Verify D11 source selection, native evaluation configuration construction and the existing async smoke submission dry-run. |

# DeepSWE configuration verification

## Scope and result

PASS for source-selection and four-cell smoke/formal configuration contracts. Full-source native visual receipt,ordinary non-injected factory,representative Qwen/native parity and qualified overlap audit passed in their respective reports. Ticket01 is reaccepted; native new-data GPU capacity and asynchronous integration remain02/03 gates. CPU post-parse typed transport is not full Megatron/SGLang validation.

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

## Native input policy transport

The selected DeepSWE loader requires its native mask-aware source and verified visual receipt. `run_swe_opd._training_args` forwards the two explicit input fields into the existing custom-function parser without duplicating defaults. The current profile selects the pinned SWE1003 loader,masked-target skipping and the genuine full-source receipt. Its earlier null-receipt candidate was explicitly rejected; the completed native scan and ordinary factory are now verified in `test_report_2026-11-08_deepswe_inputs.md`.

```bash
env TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_swe_launcher.py -q \
  --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/deepswe-launcher-input-policy.xml \
  > /data/ycfeng/tmp/qwen35-swe-deepswe-launcher-policy.log 2>&1
```

Observed: Python3.12.13, **18 passed, 0 failures/errors/skips; 2.815s**. The two source-policy cases build actual launcher argv and register all native custom hooks, then assert the resulting typed source config retains the boolean and a receipt path containing spaces. The legacy profile retains false/null defaults. These checks do not construct a data source or fabricate a full-source receipt.

After actual activation, a direct native AllConfig/custom-hook registration check built A/B full/r256 argv from `deepswe_integration_config.json` and asserted all six source fields exactly match `deepswe-input-activation.json`, receiptSHA256 matches and context/response limits remain131072 withone sample per prompt. Four checks PASS; `evidence/deepswe-active-launcher-inputs.json` retains the observed config SHA and six-field contract. Final unchanged regression command used `--junitxml=.../evidence/deepswe-active-launcher-regressions.xml` with log `/data/ycfeng/tmp/qwen35-swe-deepswe-active-launcher-regressions-20261108.log`:18 passed,0 failed/skipped/errors,2.479s. Three changed scripts compile; `git diff --check` passes. This verifies launcher transport,notGPU consumption or a full-population Qwen-length census.

## T02-DEEPSWE-CAPACITY-CONFIG — current-input native256 smoke

The final formal profile is `deepswe_formal_config.json`,SHA256 `e14b05b4546cf3510c3fa2d5c4d058420fe76fdd25b452356b13b31f6a3ce92a`. `evidence/deepswe-formal-launcher-inputs.json` records the exact nine approved field differences,all four real dry-run commands,backend flags not consumed by the CPU parser and the full verification source. Parent independently reran that source:

```bash
env TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c \
  'import json; from pathlib import Path; evidence=json.loads(Path("task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/deepswe-formal-launcher-inputs.json").read_text()); exec("\n".join(evidence["verification_source_lines"]))' \
  > /data/ycfeng/tmp/qwen35-swe-formal-input-parent-verification-20261108.log 2>&1
```

Expected/observed: exit0 and `FORMAL_PROFILE_RECHECK_PASS cells=4 input_fields=6 hooks=9 budget=200 slots=256 context=131072 n=1`. All source fields match the real ordinary factory contract; nominalfull200banks×1 andr2564banks×50,constant2e-6,save50/100/150/200 and unrestricted100×4 formal evaluation remain fixed. Existing CPU fixture supplies post-parse schema fields; every explicit recipe field is transported from actual parsed argv and backend arguments. This is not native Megatron validation or a successful training run. The CPU interpreter has no Megatron and its SGLang0.5.23 does not consume the pinned-image prefill-weight-version option; GPU startup remains a required02/03 check.

### Result and ownership

**PASS for local configuration, generated CLI/custom-hook registration and submission dry-run only.** New file: [deepswe_capacity_smoke_config.json](deepswe_capacity_smoke_config.json), SHA256 `fb08cbe905e9b7c1ab0390b1cb3fbda9d3f498b11145071ff68abded523adb75`. This reuses `run_swe_opd` and `submit_swe_opd`; no new harness, test, code, historical configuration or source-factory execution was added. Only this report section/history entry and the new configuration were edited. No authentication, GPU, API, cloud, SSH, network or commit operation was performed.

The source owner's receipt existed before derivation. A Python3.10.6 standard-library stdin check (`env PYTHONDONTWRITEBYTECODE=1 timeout 60s python3 -`) verified COMPLETE status, all eight ordered source paths, actual local size/mtime against pre/post-scan signatures, referenced baseline/visual audit hashes and the pinned loader hash. Observed source-byte sum: **16,559,540,463**; receipt exclusions: **102 trajectories**. Receipt SHA256: `fcc3bdd9bcbda5ef5ac27e0246e9db9cba9493f48dfb90fb29d3eedbe158ab35`; manifest SHA256 remains `c23a757918031592f6440cd50f0ca750f5de07da5590e98c55eb6b5760f7f73d`. This was an identity read, not a new source scan or acceptance of Ticket01.

Initially `deepswe_integration_config.json` still had a null visual receipt. During these independent checks the source owner activated the explicit receipt there. The final check confirms this smoke's entire `inputs` object equals that current profile, including the six fields recorded in `evidence/deepswe-input-activation.json:5–12`. The owner has separately recorded ordinary-factory results; this task neither reran that factory nor accepted01.

### Exact configuration differences

Relative to the final current `deepswe_integration_config.json`, exactly six leaf fields differ:

| Field | Integration value → capacity value |
| --- | --- |
| `phase` | `deepswe-integration` → `deepswe-capacity-smoke` |
| `run_root` | `/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/integration` → `/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/capacity-smoke` |
| `shared_dir` | `/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/deepswe-integration` → `/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/deepswe-capacity-smoke` |
| `training.successful_updates` | `3` → `2` |
| `training.bank_slots` | `8` → `256` |
| `checkpoint.hook_args.swe_evaluation_configuration` | `/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evaluation_deepswe_async_config.json` → absent (`hook_args={}`) |

Relative to historical `capacity_smoke_config.json`, exactly ten leaf fields differ: the three phase/output fields above, the six input fields below, and `training.release_scoring_output` (absent → `true`). No other values differ.

For that historical comparison, the old phase is `capacity-smoke`, the old `run_root` is `/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/capacity-smoke`, and the old `shared_dir` is `/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/capacity-smoke`; their new values are the capacity values in the preceding table.

| Input field | Historical value → current value |
| --- | --- |
| `source_root` | `/data/ycfeng/tmp/qwen35-swe-full-r256/swe-sources-20261023` → `/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420` |
| `source_manifest` | `/data/ycfeng/tmp/qwen35-swe-full-r256/swe-sources-20261023/COPY_COMPLETE.json` → `/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420/COPY_COMPLETE.json` |
| `native_loader_path` | `/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/playground/users/wyx/MOPD/step3p6_mopd_online_turn_loader_0710.py` → `/data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9/playground/users/cj/opd/s4_swe_turn_data_1001.py` |
| `native_loader_sha256` | `ffd9bb314c2ad5be44c52e2bd11684b51204aaa82b63e298d557b9834becacc8` → `8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980` |
| `skip_masked_assistant_turns` | absent → `true` |
| `visual_filter_receipt` | absent → `/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/deepswe-input-native-visual-filter.json` |

Both pairs retain the same original4B source, A/27B and B/35B-A3B teacher identities, student TP2/8GPU and teacher TP2/2GPU,131072 context/token budget, Qwen thinking template, AdamW-semantic science settings, TIS, seeds1234/1729,1800s acquisition and0.9 minimum. `ceil(256*0.9)=231`. The existing `SweReplay` interprets full as one use per bank despite `bank_uses=2`; the shortened schedules are A/r256 `(bank0,visit1)→(bank0,visit2)` and B/full `(bank0,visit1)→(bank1,visit1)`. Save interval2 keeps the native HF hook but is not the formal50/100/150/200 schedule.

Empty `hook_args` leaves `SweHFExportConfig.swe_evaluation_configuration=None`. `swe_hf_export.py:124–143` packages a smoke HF without qualification enqueue when this field is absent; `watch_swe_evaluations.py:348–353` returns before constructing any watcher. The inline check directly confirmed `start_dispatch(...)=None`. No evaluator configuration or existing hook implementation was changed.

### Native commands and observed checks

Working directory for CLI/registration/tests: `/data/ycfeng/sota-engine/miles`. Interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, **Python3.12.13**, PyTorch2.11.0+cu130; pytest9.1.1 for the existing observer checks. No conda activation or package installation. The variables below expand to the exact absolute paths used; each cell command was executed independently.

```bash
CONFIG=/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_capacity_smoke_config.json
CPU=/data/ycfeng/envs/miles-agent-opd-cpu/bin/python
OUT=/data/ycfeng/tmp/opencode-v2-tmp/opencode

env PYTHONPATH=/data/ycfeng/sota-engine/miles PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
  TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CUDA_VISIBLE_DEVICES= \
  WORLD_SIZE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 timeout 60s "$CPU" -B \
  -m tests.manual.agent_opd.run_swe_opd --config "$CONFIG" --pair A --protocol r256 --role train --dry-run \
  > "$OUT/t02-deepswe-capacity-A-r256.cli.txt" 2> "$OUT/t02-deepswe-capacity-A-r256.cli.log"

env PYTHONPATH=/data/ycfeng/sota-engine/miles PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
  TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CUDA_VISIBLE_DEVICES= \
  WORLD_SIZE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 timeout 60s "$CPU" -B \
  -m tests.manual.agent_opd.run_swe_opd --config "$CONFIG" --pair B --protocol full --role train --dry-run \
  > "$OUT/t02-deepswe-capacity-B-full.cli.txt" 2> "$OUT/t02-deepswe-capacity-B-full.cli.log"
```

Both commands exited0 and emitted **216 argv elements**. A direct stdin check used the same environment/`timeout 60s "$CPU" -B -`, then `get_miles_extra_args_provider()(parser)`, `parse_known_args`, `resolve_custom_function_configs` and `CustomFunctionConfig.model_validate_json(hook.model_dump_json())` on each real generated argv. It checked all nine selected hooks, unique parser options, all six source values, cell/protocol/attempt/teacher identity, smoke budgets, TIS/scoring fields, and the absent evaluation argument. All assertions passed. No `--swe-*`, `--scoring-lifetime-*` or `--tis-*` arguments remained unknown. The23 backend-specific options retained by `parse_known_args` are explicitly listed in the compact result; this does **not** validate Megatron's GPU-dependent backend parser or execute any hook's GPU work.

Registration stdout: `$OUT/t02-deepswe-capacity-registration.json`; stderr: `$OUT/t02-deepswe-capacity-registration.log`. The former deliberately retains two library log lines before its JSON body. An initial whole-file `json.loads` inspection failed with `JSONDecodeError: Expecting value: line 1 column 1`; inspection showed the vLLM CPU platform/import log preamble, not a registration failure. A corrected read checks those exact INFO/WARNING prefix lines and decodes the emitted JSON block; no raw output, producer or validation condition was changed. The retained warning is `Failed to import from vllm._C ... libcudart.so.12 ... No such file or directory`; this CPU-only check never calls vLLM CUDA inference.

The final Python3.10.6 stdin assertion check also verified actual generated scientific flag values, exact current/historical configuration differences, identical final input fields, both submitter outputs and absence of actual receipts. Result: **CONFIG_DIFF_AND_DRYRUN_OUTPUT_PASS**, retained at `$OUT/t02-deepswe-capacity-checks.json`.

Existing repaired-observer check, with the same CPU environment as the CLI commands:

```bash
env PYTHONPATH=/data/ycfeng/sota-engine/miles PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
  TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CUDA_VISIBLE_DEVICES= \
  WORLD_SIZE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 timeout 60s "$CPU" -B -m pytest \
  tests/fast/test_megatron_scoring_lifetime.py -k combined_cli_typed_before_log_prob \
  -q -p no:cacheprovider --basetemp="$OUT/t02-deepswe-capacity-observer-check" \
  --junitxml="$OUT/t02-deepswe-capacity-observer-check.xml" \
  > "$OUT/t02-deepswe-capacity-observer-check.log" 2>&1
```

Observed **2 PASS,18 deselected,0 failures/skips,2.58s**. These existing tests cover the repaired two-field observer through real CLI/typed trainer transport/native caller with CPU fixtures; they are not new DeepSWE GPU observations. The new configuration registers precisely those two fields and the expected patched schedule SHA256 `8b0370c0d50a2463781ae3c622e30f923d096485aed3c0f8939be4cc13689081`; it does not add `swe_attempt` to the observer. Existing CPU/deprecation warnings are retained in the log.

Submitter working directory: `/data/ycfeng`; interpreter `/data/ycfeng/tmp/stepmind-env/bin/python`, **Python3.10.6**, directly observed with `/data/ycfeng/tmp/stepmind-env/bin/python --version`. Existing dry-run returns before authentication checks, API imports, admission lock/receipt writes and submission (`submit_swe_opd.py:69–84`).

```bash
env PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron PYTHONNOUSERSITE=1 \
  PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  CUDA_VISIBLE_DEVICES= timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -B \
  -m tests.manual.agent_opd.submit_swe_opd --config "$CONFIG" --pair A --protocol r256 \
  --receipt "$OUT/t02-deepswe-capacity-A-r256.not-submitted.json" --dry-run \
  > "$OUT/t02-deepswe-capacity-A-r256.submit.json" 2> "$OUT/t02-deepswe-capacity-A-r256.submit.log"

env PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron PYTHONNOUSERSITE=1 \
  PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  CUDA_VISIBLE_DEVICES= timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -B \
  -m tests.manual.agent_opd.submit_swe_opd --config "$CONFIG" --pair B --protocol full \
  --receipt "$OUT/t02-deepswe-capacity-B-full.not-submitted.json" --dry-run \
  > "$OUT/t02-deepswe-capacity-B-full.submit.json" 2> "$OUT/t02-deepswe-capacity-B-full.submit.log"
```

Expected and observed: both exit0, `submitted=false`,10 requested GPUs each (one8GPU critical student, one2GPU noncritical teacher), the correct config/pair/protocol worker command and existing GPU-policy identity. Both `.not-submitted.json` paths remain absent. This checks resource construction, not live quota, admission, mounts or worker readiness.

Final local checks: `git diff --check -- task_memory/task_2026-11-08_qwen35_swe_full_r256/deepswe_capacity_smoke_config.json task_memory/task_2026-11-08_qwen35_swe_full_r256/test_report_2026-11-08_deepswe_configuration.md` exited0. A standard-library stdin assertion check (`env PYTHONDONTWRITEBYTECODE=1 timeout 60s python3 -`) returned `FINAL_LOCAL_ARTIFACT_CHECK PASS` for the configuration SHA, exact source-owner six-field contract, smoke budget and report section/fences/local links.

### Existing native evidence and remaining GPU gates

Let `RUN` be `/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/capacity-smoke/<protocol>/student/<pair>/<actual-job>`. Existing paths, not a new harness:

- `RUN/training/bank_<bank>.jsonl`: acquisition/slot/missing/scoring identities; `RUN/training/updates.jsonl` and `optimizer_attempts.jsonl`: actual optimizer acknowledgements, original/surviving token counts, KL/loss/LR, membership and weight versions (`swe_replay.py:353–376`; `swe_training.py:103–114,129–217`). D7 evidence uses the existing `failed_batches.jsonl` and `zero_tis_rollout_<id>_rank_<rank>.pt`.
- `RUN/train_data/<rollout_id>_<rank>.pt`, `policy_loss_debug/rank_<rank>_call_<call>.pt`, rollout/trajectory dumps and `events/`: generated by the existing `dump_details` path (`arguments.py:1352–1355`; `metrics/train_dump.py:11–47`; `metrics/debug_dump.py:13–76`). TP0 peers are retained once; planned TP2/DP4/CP1 corresponds to ranks0/2/4/6, but actual topology must be read from the worker evidence. Existing `audit_swe_native_training.py` can reconstruct current-completion RKL/TIS/PPO against these actual dumps.
- `RUN/megatron_scoring_lifetime/source/` and `observations/rank_<rank>.jsonl`: exact source preflight/archive, actor schedule hashes, microbatch weakrefs/storage and allocator measurements. Installation/receipt failures remain soft and make observations unverified, not failed training.
- `RUN/hf/step_1/` is the expected HF2 directory only if two successful attempts occur without skips; actual mapping must come from `.complete`, `qwen_text_export.json`, `hf_publications/` and native successful counters. No qualification evaluation is configured. Local synchronization uses the new `evidence/deepswe-capacity-smoke/<protocol>/` root, isolated from historical evidence.

Ticket02 remains open. The parent must first accept01, then perform live admission and the two new-input native runs. Required observations include source/model/mount/topology identity, representative256-slot acquisition within1800s with at least231 valid trajectories, completed current-student scoring/backward and **two actual successful optimizer ACKs**, fresh second scoring with unchanged r256 canonical teacher/behavior/tokens, B/full bank transition, recomputable completion-only RKL/TIS/loss and successful HF2 identity. All eight actor schedule hashes and repaired GPU lifetime/allocator observations remain unmeasured by this work. A/r256's two-use smoke does not exercise its next-bank transition or the formal50-use/200-update budget.

Historical GLM-5.2 evidence remains limited to its actual provenance: the green capacity contrast completed31 scoring microbatches/rank and entered backward but was externally stopped before optimizer ACK/second scoring; its GPU observer failed installation. The earlier8-turn gradient probe observed derivative, original-token finalization and AdamW state continuity, while four zero-only scale slices and optimizer-shard ownership remain unverified. See [scoring-lifetime report](test_report_2026-11-08_megatron_scoring_lifetime.md), [native tensor audit](test_report_2026-11-08_native_training_audit.md) and [native gradient audit](test_report_2026-11-08_native_gradient_audit.md). None closes replacement-data capacity, native failure/partial-bank/skip coverage, the full200-update schedule or all four native cell paths. No extra observer, flags or rerun was introduced to manufacture those missing results.

### 1. 规划完成情况

**汇总：** PASS2｜BLOCKED/FAILED/SKIPPED1｜TODO0（本委派切片）。

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| D11现有256-slot配置派生 | PASS | 与当前输入一致；仅改指定smoke预算、输出位置和evaluation参数。 |
| Native CLI/hook与submitter本地检查 | PASS | 两cell各9hooks；observer2/2；dry-run均未提交。 |
| 02新数据GPU容量验收 | BLOCKED | 仍需父agent接受01并执行真实native运行；不属于本委派操作权限。 |

### 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** T02-DEEPSWE-CAPACITY-CONFIG委派至本地验证完成｜**当前前沿：** 父agent01接受及02/03原生验收。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 复用已有入口和两项observer检查；通过后停止扩展。 |
| D2 细节反复重试 | CLEAR | 仅修正已观察到的stdout前导日志读取；未反复修改训练参数。 |
| D3 支线问题修补 | CLEAR | 未改代码、旧配置或其他owner的文档章节。 |
| D4 可并行任务停滞 | CLEAR | 配置准备独立推进；01工厂和父agentbaseline工作未被等待或接管。 |
| D5 超范围镀金 | CLEAR | 只有新配置和本报告切片，无新增harness/tests。 |
| D6 分析空转 | CLEAR | 已交付实际配置、生成CLI、typed hook和dry-run结果。 |
| D7 路线违背 | CLEAR | 保留science/TP2/128K；未把本地检查或历史GLM证据当GPU验收。 |

**文档检查：** 本切片S1–S6未发现需改变spec/ticket的缺陷；基线报告的旧pending描述由父agent独立维护，本节记录当前配置观察。
**归因：** 无。

### 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动。
**需停止的偏离行为：** 无。
**接下去的路线：**
1. 父agent接受01的来源与普通factory证据 → 完成标志：真实launch消费六字段且01明确接受。
2. 并行：02 A/r256与B/full256-slot原生容量 ‖ 03新数据异步集成 → 完成标志：各自ticket的真实训练/评测证据，不改变本smoke的空evaluation参数。

### 4. 最值得关注的 3 点

1. 本地配置和parser已通过；没有live admission或新数据GPU容量PASS。
2. Capacity smoke保留HF2打包但不入qualification队列；A/r256只有bank0两次使用。
3. 剩余GPU source/lifetime、实际optimizer ACK与下一次scoring由父agent接续；历史GLM观测不替代它们。
