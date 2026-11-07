## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Close the ResourceTracker P2 with two real-interpreter checks on pinned Python3.12.16; preserve the original post-PASS error and pending final artifacts. |
| 2026-11-07 | Record phase-review P2 after native PASS, repair terminal ResourceTracker through its stdlib owner, and verify isolated interpreter exit with five focused CPU cases. |
| 2026-11-07 | Qualify the native text loader on two H800 GPUs: 822 decoder entries equal before/after inference, real scoring/generation/cleanup PASS, and 82 pinned contract tests PASS. Final trained artifacts remain pending. |
| 2026-11-07 | Record actual native Engine startup, exact deployment delta classification, invalid baseline-reference rejection, terminal-child cleanup and 82 local checks. |
| 2026-11-07 | Record actual baseline-loader prerequisite failure, native per-cell seed diagnosis, narrow CPU repair and pending pinned confirmation. |
| 2026-11-07 | Complete native SGLang replacement and CPU contract verification; close the final-weight identity finding at implementation scope. |
| 2026-11-07 | Record initial checker results, pinned dtype loss, final-weight identity finding and native SGLang replacement scope. |

# Final text-HF reload verification

## Scope and current verdict

D13/R5 require the final updated text decoder, compatible configuration/tokenizer and actual text inference. Final-artifact verdict: **INCOMPLETE**, because no final100-step artifact is available. The baseline4B text-loader qualification is now **PASS** on the actual pinned2-H800 runtime, as recorded below. This standalone validator has no training control path.

## Initial implementation and local verification

The initial implementation added `tests/manual/agent_opd/qwen_reload.py` and `tests/fast/test_qwen_reload.py`. The owning agent reported **38 passed in8.93s** on Python3.12.13/torch2.11.0+cu130, using:

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q -o addopts='' \
  -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-reload-final \
  tests/fast/test_qwen_reload.py tests/fast/test_qwen_text_export.py \
  tests/fast/test_qwen35_monitoring.py::test_native_zigzag_cp_reassembles_token_positions_not_rank_order \
  tests/fast/test_qwen35_monitoring.py::test_unknown_cp_allgather_is_explicitly_incomplete
```

These tests cover actual tiny Transformers loading, forward/generation and injected faults. They include a successful rejection of mixed-dtype corruption;38 passing tests do not mean the default loader preserves the real checkpoint's FP32 parameters.

## Pinned dtype reproduction and failed auxiliary jobs

The pinned image uses Python3.12.16, torch2.14.1+cu130 and Transformers5.19.0. A tiny official text model was converted to BF16, its `A_log` set to FP32 `0.123456789`, saved with `save_pretrained`, read through safetensors and reloaded using `AutoModelForCausalLM.from_pretrained(..., local_files_only=True, dtype='auto')`.

Expected: identical saved/loaded dtype and values. Actual **FAIL**: saved `torch.float32`, value0.12345679104328156; loaded `torch.bfloat16`, value0.12353515625. Both native keep-FP32 lists are empty. Exact [pinned receipt](evidence/hf-dtype-exp-1107-065617-263305.json) was produced by `exp-1107-065617-263305`.

The first0-GPU job `exp-1107-065241-081272` failed while serializing the loader's set-valued policy attribute to JSON. The corrected command sorted those fields; its dtype probe completed. Its subsequent CPU pytest invocation of `test_qwen_reload.py test_qwen_text_export.py` produced **4 failed,15 passed,15 errors in8.74s**: installed CUDA-only convolution was selected for CPU fixture inputs. Logs are `evidence/hf-reload-runtime-<job>.log`. No actual full-model GPU reload occurred, and no more CPU forward retries are scheduled against that mismatched kernel setup.

Both jobs have8 successful RCA queries under `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-hf-{runtime,dtype}-<job>/`, collected with the canonical failure collector, personal identity and exact incident windows22:52–22:54Z /22:56–22:59Z. They are auxiliary failures independent of A/B's later native backward OOM.

Source/probe analysis confirms that Transformers5.19's supported strict keep-FP32 class declaration can preserve the tiny package; a dtype dict is collapsed to the global dtype and post-load casting cannot restore rounded values. No library class policy, dependency patch or dtype relaxation has been adopted.

## Review finding and chosen native path

Reviewer `QWEN-P3-HF-RELOAD-REVIEW` found a P1 false-PASS path: final directory/rollout markers, package-internal tensor equality and<=0.03 sampled logprob agreement cannot prove that the HF files contain the final published weights. Native export completion carries no content-bound publication metadata. The replacement and regressions now close this finding at implementation scope; actual final artifact acceptance remains INCOMPLETE.

Existing `InferenceEngineWeightChecksumEvent` records provide full-byte checksums of native eligible engine tensors, bound to publication/load epoch/engine incarnation. The actual [B initial receipt](evidence/initial-engine-checksums-B-exp-1107-062459-796906.json) contains1416 entries over TP2, including vision weights and derived `gemma_weight` decoder buffers. Raw HF tensors have a different fused/sharded layout, so directly hashing safetensors cannot be compared to these engine hashes.

Use the **existing pinned SGLang text loader** at the original engine TP/configuration, then compare its native eligible decoder checksum dictionary with the final publication's dictionary. This reuses the actual HF-to-engine loader and FP32 `A_log` parameter policy. D13 excludes vision/MTP; all eligible decoder entries and derived decoder buffers remain checked. The fresh engine's own version is reported separately from the training publication version, whose connection is established by content equality. Retain package/schema/tokenizer validation, original fixed inputs/masks, numerical reporting and actual text generation.

No new hashing algorithm, partial-norm identity substitute or exporter metadata path is introduced. The superseded Transformers loading path was replaced in the same two files. Actual baseline4B native loading, checksum equality, shortest retained-input inference and cleanup are qualified below; full monitoring-length coverage and all three final artifacts remain pending.

## Replacement verification and phase review

Implementation owner `QWEN-P3-HF-RELOAD-IMPLEMENT` supplied **63 passed /13.77s**, comprising40 reload tests and23 export/CP checks, using the earlier local command with basetemp `qwen-reload-native-contracts`. Package checks are real; native Engine/API boundary cases use fixtures. Exact initial namespace audit:1416 entries ->822 decoder entries and594 excluded vision entries;162 derived gemma buffers remain within decoder coverage. TP2 tied-head canonical naming is embedding.

Reviewer `QWEN-P3-HF-RELOAD-REVIEW` inspected the changed-file list (`qwen_reload.py`, `test_qwen_reload.py`), task records and native producer/loader/checksum sources. **Original P1 CLOSED; no new actionable finding.** Final checksums bind publication ID/version plus load epoch/cell/incarnation; pre/post-inference decoder dictionaries must match exactly. Stale packages below0.03, missing decoder keys, derived-buffer mismatch, TP mismatch and incomplete final receipts cannot pass. The review did not run tests or GPU work.

The report's image field is a configuration declaration; actual container provenance requires the parent's RJob API receipt. The successful baseline job below supplies that receipt and the native checks; longer-input/final-artifact coverage remains pending. No dependency or model-class policy patch is adopted.

Pinned registry prerequisite is now **PASS**: `exp-1107-075006-580618` resolves requested `Qwen3_5ForCausalLM` directly to `sglang.srt.models.qwen3_5_text.Qwen3_5ForCausalLM` on SGLang0.5.24.dev80+g056f871, without the Transformers fallback. Exact [runtime receipt](evidence/text-entry-exp-1107-075006-580618.json). All40 replacement reload tests pass in this image. The combined run's four failures are the previously known unchanged Transformers CPU-forward cases, as recorded in the [training report](test_report_2026-11-07_training.md); they do not represent native text loading. Full-model GPU reload and final artifact content equality remain outstanding.

## Native startup and retained settings repair

The locally inspected [probe report](evidence/text-loader-probe-exp-1107-093036-947852.json) and [log](evidence/text-loader-probe-exp-1107-093036-947852.log) show that the pinned 2-H800 probe created the native text Engine, then failed the retained-settings check. Both native versions are `0.5.24.dev80+g056f871`. After filtering to actual native `ServerArgs` fields and the existing allocation fields, the only changed field is `served_model_name`: the original asset path becomes the copied artifact path.

Native source explains the change: `sglang/srt/arg_groups/serving_hook.py:642-646` resolves an omitted `served_model_name` to `model_path`; `fields/serving.py:168-171` identifies it as the OpenAI `v1/models` deployment name. The repaired shared comparison allows only that exact omitted-name mapping on both reference and reload. An explicit name remains an exact retained setting, even when it looks like a path. No global allocation exclusion was added for it.

The observed `max_total_num_tokens` changed from 1,697,128 to 1,743,657. It is a runtime KV allocation result, not the explicit native `max_total_tokens` input. `model_executor/model_runner_components/kv_pool_runtime.py:59-75,142-150` computes pool sizing from available GPU memory and pool budgets. `_server_config` already excludes `max_total_num_tokens`, top-level `startup_time` and `frontend` through the native field registry; no new skip was required. Explicit `max_total_tokens`, memory fractions, seed and all retained kernel/probability settings remain checked.

The existing native CLI reconstruction remains the sole executable configuration source. Redacted `/server_info` values are observations only. No watermark-specific skip, dependency change, custom hash or probability correction was added. Pre/post-inference full decoder checksums, including `gemma_weight`, remain unchanged.

## Baseline-reference qualification and cleanup

Parent inspection using read-only SSH and direct PyTorch 2.5.1 loads found the old first-round B `exp-1107-062459-796906` baseline trainer vector uniformly equal to `-12.422473907470703` across 4,712 tokens; A `exp-1107-063447-691018` has the same value across 4,279 tokens. These are parent-provided observations, not local tensor measurements by this implementation session. The old formal B reference is invalid for loader qualification. The parent will explicitly select the D8-PASS baseline at `native_probe_config.run_root/student/B/exp-1107-055408-654957`; this agent did not read that cloud run or change the selection automatically.

`probe_qwen35_text_reload._input` now qualifies its deterministically selected recorded sample using the existing `_token_metrics` reader at the unchanged 0.03 threshold, original masks, actual version0 and native probability contract. A threshold miss, missing/nonfinite valid score, zero denominator or invalid identity raises before copying/loading. It does not try another sample or run. The report distinguishes this selected-sample prerequisite from whole-run D8 and final D13 acceptance.

The actual failed probe reported PIDs 211, 212, 229 and 230 as remaining after shutdown but retained no process states. Their zombie/running state is therefore **unverified**, not assumed. `psutil.Process.is_running` includes zombies. Native `Engine.shutdown` controls its interpreter's child tree (`entrypoints/engine.py:1450-1497`), while native resource-wait logic considers zombies released (`utils/common.py:2452-2487`). The shared validator now requires an isolated interpreter, calls native shutdown, reports process status and uses stdlib process joins or non-blocking waits only on already-terminal owned direct children. It sends no extra signals. Live children, inspection/reaping errors or native shutdown errors remain INCOMPLETE. Real CPU tests verify zombie reaping, own multiprocessing-handle joining, preservation of a live sibling and refusal to launch beside a preexisting child. Actual pinned cleanup remains pending.

## Focused local verification

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python 3.12.13, torch 2.11.0+cu130, Transformers 5.19.0, SGLang 0.5.23, psutil 7.2.2. No GPU, platform, SSH, cloud, Git or dependency operation was performed in this repair session.

Red command: **2 failed in 1.40s**, reproducing automatic served-name rejection and failure to reject a uniform corrupted selected reference:

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q --tb=line \
  -o addopts='' -p no:cacheprovider \
  --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-reload-deployment-red \
  tests/fast/test_qwen_reload.py::test_automatic_served_name_follows_relocated_model_only \
  tests/fast/test_qwen_reload.py::test_corrupted_selected_baseline_reference_is_rejected
```

Final command: **82 passed in 32.73s**. Expected conditions: exact automatic-name relocation succeeds; explicit name/token-budget/seed/kernel corruption remains unverified; corrupted reference never reaches copy or Engine; terminal children are reaped and live/unrelated children are not killed. All conditions passed. Three warnings include the real multiprocessing test's Python fork-in-a-multithreaded-process deprecation; its target calls `os._exit` and its own handle is joined. Intermediate affected suite: 80 passed in 30.47s.

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q --tb=line \
  -o addopts='' -p no:cacheprovider \
  --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-reload-deployment-final \
  tests/fast/test_qwen_reload.py
```

The CPU suite proves package and API/lifecycle contracts, not pinned deferred resolution, full-model probabilities or GPU resource release. Local SGLang 0.5.23 rejects the pinned `--enable-prefill-weight-versions` flag; it was not removed or translated. The parent owns the new selected baseline, actual pinned 0.5.24 runtime/cleanup checks and final artifact acceptance. Overall D13/R5 remains **INCOMPLETE**.

## Actual pinned baseline qualification — PASS

Job `exp-1107-100927-934443`, submitted locally with `native_probe_config.json` image and personal StepMind Python auth, succeeded. The [API readback](evidence/restore-and-hf-platform-readback.json) verifies creator `i-fengyicheng`, the digest-pinned Miles image, local NFS `100.96.128.195:/data/ycfeng:/data/ycfeng`, and one16-CPU/2-H800/128-GB requested worker. The [log](evidence/text-loader-probe-exp-1107-100927-934443.log) verifies both H800 UUIDs and81559MiB per GPU. Runtime: Python3.12.16, torch2.14.1+cu130, SGLang0.5.24.dev80+g056f871, actual model class `sglang.srt.models.qwen3_5_text.Qwen3_5ForCausalLM` at TP2.

Worker commands, after repository `cd`, CUDA compat-library setup, offline HF flags and job-local caches:

```bash
CUDA_VISIBLE_DEVICES="" /opt/sglang/bin/python3 -B -m pytest -q --tb=short \
  -o addopts='' -p no:cacheprovider --basetemp="$TMPDIR/pytest" tests/fast/test_qwen_reload.py
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.probe_qwen35_text_reload \
  --source /mnt/codesign-exp/ycfeng/opd-assets/models/Qwen/Qwen3.5-4B/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a \
  --run-dir /mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/native-prerequisites/student/B/exp-1107-055408-654957 \
  --output /mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/text-loader-probe/exp-1107-100927-934443/model \
  --report task_memory/task_2026-11-06_qwen35_three_pairs/evidence/text-loader-probe-exp-1107-100927-934443.json
```

The complete submission command is retained in harness shell `sh_1b3c48706001RyTNBPyT4rLi0b`; it uses `ResourceConfig`/`spawn_tasks` from local cwd `/data/ycfeng`, `gang_start=False`, `charged_group=codesign`, and the existing personal-volume mount. No dependency installation or library patch occurred.

Observed acceptance evidence in the [native report](evidence/text-loader-probe-exp-1107-100927-934443.json):

- Pinned CPU contract: **82 passed**,22 warnings,22.76s, exit0. The test file now explicitly registers stage-b CPU with a40s estimate because its measured local runtime32.73s exceeds the implicit30s budget.
- Original selected baseline sample7 first qualifies at mean absolute error0.010834013553763552,91 valid tokens, zero missing/nonfinite values. It is from the previously qualified zero-update run, not the corrupted optimizer-bearing formal run.
- Full native eligible decoder dictionary: **822 entries, zero mismatches**, both before and after inference, including derived gemma buffers. Explicit seed/settings and the original native text-loader configuration checks pass.
- Full original input:11428 prefix tokens plus91 completion tokens, no truncation. All91 valid same-token prefill scores are finite. Mean absolute error **0.014099925691702786 <=0.03**; p950.07452890276908875, p990.10255198478698717, maximum0.12498855590820312. Both K3 means and per-token positions are retained in the report. No TIS selection changes the denominator.
- Actual temperature0, one-token generation yields token9764, text`Let`. It is not compared for equality to historical temperature1 generation.
- Native Engine shutdown completes; the helper reports four owned zombie children reaped and no owned children remaining. One native-terminated child reports exit-9, consistent with the native shutdown path; the validator sends no additional signals. The helper's **PASS** did not cover interpreter exit: the phase-review P2 below identifies the stale ResourceTracker owner and leaves whole-exit cleanup pending its focused pinned validation.

Scope remains `baseline native loader qualification`, `final_artifact_accepted=false`. This qualifies the actual4B loader and short-input path; it does not qualify the27B loader, all24 final monitoring inputs or any final trained artifact. Formal fused-backend D8 must still be measured anew after restoration is repaired.

## Phase-review P2: ResourceTracker owner at interpreter exit

The same actual pinned [log](evidence/text-loader-probe-exp-1107-100927-934443.log), lines 189-194, contains `ResourceTracker.__del__ -> _stop -> _stop_locked -> ChildProcessError: [Errno 10] No child processes` after the PASS marker at line 187. The loader/content/numerical observations above remain unchanged. Whole-interpreter cleanup was incomplete: generic `psutil.Process.wait` consumed the tracker's PID but left its stdlib owner's `_pid` and `_fd` populated.

Inspected local source is `/data/ycfeng/envs/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/multiprocessing/resource_tracker.py:74-112`. `ResourceTracker._stop()` obtains its own lock and `_stop_locked` closes the owner's FD, waits for its own PID and clears `_pid`. The pinned Python 3.12.16 traceback reaches the corresponding destructor/stop/wait lines 77/86/111, but direct validation of the pinned owner implementation remains the parent's responsibility.

`qwen_reload._reap_terminal_children` now selects that owner only after confirming an owned direct child is terminal and its PID equals `multiprocessing.resource_tracker._resource_tracker._pid`. It calls the existing owner `_stop()`, not a generic wait, and records the owner name without inventing an unavailable exit status. Live trackers remain INCOMPLETE and retain their owner PID/FD. Normal multiprocessing children still use their own handle's join; other terminal direct children retain the existing wait. There is no signal, stdlib mutation, unraisable hook, error suppression or global cleanup fallback.

The regression starts a real stdlib tracker in a separate interpreter, uses EOF fault setup (replacing only its owned writer FD with `/dev/null`) to make it terminal without a signal while preserving the owner's valid FD, and then runs the actual reaper. It checks both owner state and stderr after normal interpreter exit. The live variant checks that the helper does not stop the live tracker; the existing stdlib destructor handles it on ordinary process exit. No native model or unchanged probability test was rerun. The parent's `register_cpu_ci(est_time=40, suite="stage-b-cpu", labels=["megatron"])` remains unchanged.

Local red result: **1 failed, 1 passed in 21.66s**, reproducing the exact ignored destructor `ChildProcessError` at interpreter exit.

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q --tb=line \
  -o addopts='' -p no:cacheprovider \
  --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-resource-tracker-red \
  tests/fast/test_qwen_reload.py::test_resource_tracker_owner_and_whole_interpreter_exit
```

Local green result: **5 passed in 22.03s**. Terminal tracker: owner PID/FD both None, PID absent, no ignored exception or ChildProcessError in exit stderr. Live tracker: INCOMPLETE with owner state unchanged. Other checks confirm terminal-child reaping, own multiprocessing-handle joins and protection of a live unrelated/preexisting child. Three warnings are existing SWIG deprecations and the already-recorded fork warning. Environment remains Python 3.12.13 with the local CPU runtime above.

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q --tb=line \
  -o addopts='' -p no:cacheprovider \
  --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-resource-tracker-green \
  tests/fast/test_qwen_reload.py::test_resource_tracker_owner_and_whole_interpreter_exit \
  tests/fast/test_qwen_reload.py::test_real_terminal_children_are_reaped_without_touching_live_sibling \
  tests/fast/test_qwen_reload.py::test_real_multiprocessing_child_is_joined_with_its_own_handle \
  tests/fast/test_qwen_reload.py::test_native_shutdown_refuses_interpreter_with_preexisting_child
```

Only `qwen_reload.py`, `test_qwen_reload.py` and this report changed. No GPU/platform/Git/cloud/SSH/dependency operation or delegation occurred. Parent owns one focused pinned 0-GPU execution of the interpreter-exit regression; no model rerun is warranted solely for this cleanup defect. Final D13 artifact acceptance remains independent and INCOMPLETE.

### Parent pinned closure

The focused check completed in0-GPU job `exp-1107-103428-476945`: **2 passed in29.14s**, using the unchanged pinned image and Python3.12.16. Command: `CUDA_VISIBLE_DEVICES="" /opt/sglang/bin/python3 -B -m pytest -p no:cacheprovider -o addopts='' tests/fast/test_qwen_reload.py::test_resource_tracker_owner_and_whole_interpreter_exit -q`. The [complete log](evidence/restore-exit-contracts-exp-1107-103428-476945.log) ends after the passing summary and a known SWIG deprecation warning; it contains no ignored exception or ResourceTracker error. Both owner-state and whole-interpreter stderr assertions pass. P2 is closed for this measured cleanup defect. The earlier GPU report remains unmodified, including its prematurely written PASS; its independent content/numerical observations remain valid.

The stage-b CPU estimate is now60s, accounting for the measured32.73s preexisting file and22.03s added lifecycle slice; this is an estimate, not a new whole-file timing. Same-version restoration receipt handling is recorded separately in [publication restore](test_report_2026-11-07_publication_restore.md). Final artifacts and their complete24-input runtime acceptance remain pending.
