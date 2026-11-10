## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record the first4 diagnostic integration, real source-preparer ordering, joined CPU checks, independent readback failures and pending native acceptance. |
| 2026-11-11 | Add explicit retained native RID associations, a reordered real-schema regression, failed-validation retention and306-pass joined follow-up verification. |
| 2026-11-11 | Accept native single-DP absent-controller rank without relabeling it; retain strict rank checks and record RED/GREEN plus330-pass joined verification. |
| 2026-11-11 | Repair both phase-review P2s: reuse pristine-source override/explicit skips and retain failure-only HTTP body provenance; record4-case RED,14-case GREEN and332-pass joined verification. |

# Runtime metadata teacher-probe integration

TaskID: `profile-mamba-live-metadata-integration-20261111`.

## Outcome and scope

**CPU integration PASS; native H800 reproduction PENDING.** Only the worker probe, its existing CPU test file, the new diagnostic config, one dedicated first4 manifest and this report are owned by this integration slice. Source preparation and its native recorder remain independently owned; no recorder, source patching, launcher wrapper, GPU/platform/auth/SSH operation or delegation was added here. Existing submission tests exercise only mocks or `--dry-run` construction; no platform client was called.

Deliverables:

- `tests/manual/agent_opd/probe_teacher_scoring.py`: strict opt-in `mamba_runtime_metadata` JSON boolean, requiring `selected_fp32_snapshots=true`; original-fixture prefix manifest support; separately retained source receipts; one post-loop readback through the existing server-info endpoint; independent probe failure after scoring if readback fails.
- `tests/fast/test_teacher_scoring_probe.py`: configuration/identity/command preservation, actual preparer receipts and ordering, baseline56/32 with no extra metadata fetch, diagnostic16/10, DP-only readback coverage, malformed/missing metadata and retained scoring files after failures.
- `task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_runtime_metadata_probe_config.json`: A/B, four H800 per teacher, first four exact existing fixtures, one repetition, isolated output. The formal config continues to own all teacher weights, mounts, engine arguments and budgets.
- `task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_runtime_metadata_first4_manifest.json`: only `source_fixture` and `sample_count=4`, passed through the existing `--samples` argument. No token copy, index renumbering or second subset selector.

The original fixture remains `evidence/teacher-scoring-probe-20261111/retained-cases.json`, SHA256 `c45424e8106c2beb7500acacb68aa0939da0088c926af8012dd9fbd780f0ffc9`, 3,703,152 bytes. Its first four sample indices remain1693/1694/1695/1696 with their original full UIDs, input tokens, response lengths734/246/431/290 and assistant-turn ordinals57/58/59/60. Baseline7×2 remains56 scoring requests/32 flushes per pair; diagnostic4×1 is16/10. Cache behavior, concurrency1, chunk8192, BF16, deterministic inference, model paths, two source-volume mounts, worker/request3600s and cleanup90s remain unchanged.

## API, receipts and source evidence

The worker calls the source owner's real API in this order:

```python
snapshots.prepare_source(root, image=config["image"], selected_fp32=True,
                         archive_dir=output / "source_preflight")
metadata.prepare_runtime_metadata(root, image=config["image"],
                                  archive_dir=output / "runtime_metadata_source_preflight")
# _runtime inspection, teacher command/startup, all scoring loops, readback
```

`source_preflight` and `runtime_metadata_source_preflight` remain separate in preload/result and in their respective `preflight.jsonl` archives. Both source modules have independent identities in `native_scoring_sources`. CPU tests run both real preparers on copied hash-qualified retained sources; they do not change host-installed SGLang or import new attention modules before preparation.

Joined dependency snapshot:

| Independently owned file | SHA256 |
| --- | --- |
| `tests/manual/agent_opd/sglang_mamba_runtime_metadata.py` | `c820ff7aa4a820b7f81ced8e2567eef51c0534c7f6cace074f905176a6c160e1` |
| `tests/fast/test_sglang_mamba_runtime_metadata.py` | `04553316d4cab17b7ba91ef8cceb682606aa699c27e92ff921b0885475062c70` |

Actual retained source establishes the endpoint and envelope, rather than a guessed TP-shard layout:

- C2 `evidence/native-sglang-cache-source-20261111/exp-1111-040603-422872/source/srt/entrypoints/http_server.py:854–889`: `/get_server_info` delegates to `/server_info`; the response contains `internal_states`, explicitly one entry per DP.
- Same C2 `srt/managers/io_struct.py:2442–2450`: `GetInternalStateReqOutput.internal_state` is a Dict; `srt/managers/scheduler_components/internal_state.py:45–63` builds that payload. The source owner adds the recorder readback at this existing seam.
- C3 source qualification and the source-owner CPU tests verify the overlay before application; the joined integration tests preserve its actual receipt instead of recreating source edits.
- Actual existing A FP32 `evidence/teacher-scoring-fp32-probe-20261111/native/A/admission-A-r1/server_info.json` reports DP1/TP4/PP1 and exactly one `internal_states` entry. This verifies the original response shape, not new runtime metadata.

After all scoring requests, the diagnostic performs one `GET /get_server_info`, retaining one `runtime_metadata.json`. It validates one response per reported DP, individual process/rank metadata, schema `mamba-runtime-metadata-v1`, and nonempty ordered CPU rows. It does not assume DP list order or all-TP coverage. Full valid JSON response evidence is retained; malformed readback also retains exact response text when available. HTTP timeout/error, missing key, empty rows, malformed schema/rank/row and duplicate/out-of-range DP ranks never count as collected metadata.

The result references this receipt without duplicating the trace. A readback failure raises an independent probe `RuntimeError`, leaves `native_measurements_completed=true` for already-finished scoring, retains scoring files/cache observations and performs ordinary child cleanup. It never changes training, requests, numerical acceptance or performance acceptance. Absent/false diagnostic configuration performs no overlay or post-loop HTTP request and retains the original benchmark path.

## Commands, environment and observed checks

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. CPU interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, pytest9.1.1. Controller-only source/identity reads used `/usr/bin/python3`, Python3.10.6. No conda activation. Temporary test artifacts stayed under `/data/ycfeng/tmp/opencode-v2-tmp/opencode/`; bytecode and pytest cache writes were disabled.

Initial config/prefix regression:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-config-prefix-20261111
```

Expected: preserve original behavior, validate diagnostic selection, select exact first4 and preserve A/B allocation/argv. Observed **79 passed,4 warnings,1.82s; PASS**.

Focused complete integration:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-probe-focused-20261111
```

Expected: both real preparation receipts in order, no pre-preparation attention imports, original commands/scoring counts, post-loop-only metadata collection, honest failures and scoring retention. Observed **105 passed,4 warnings,4.77s; PASS**.

Actual joined CPU verification, including the independently owned native-source preparer tests:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py tests/fast/test_sglang_mamba_snapshots.py tests/fast/test_sglang_mamba_runtime_metadata.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-probe-joined-20261111
```

Expected: no regressions in native scoring, original submission/FP32 snapshot behavior, qualified metadata source and integration. Observed **304 passed,20 existing warnings,26.75s; PASS**. Warnings concern existing SWIG, deprecated Torch JIT/datetime APIs, and unsupported CPU AWQ/GGUF; no test failure or skip occurred.

```bash
git diff --check -- tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_teacher_scoring_probe.py task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_runtime_metadata_probe_config.json task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_runtime_metadata_first4_manifest.json task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_runtime_metadata_probe_integration.md
```

Expected/observed: no scoped whitespace errors; PASS. Required CPU checks have passed; no unrelated edits are staged.

## Native RID association follow-up

**Verified cause:** the local `request_id` is a synthetic filename identity (`phase-rN-sN-mode`), not the native scheduler RID. The original request JSONL already retained `meta_info.id` through `_meta_summary`, so the response ID was not wholly lost. However, neither request nor completion receipts exposed a top-level native RID association, completion receipts omitted the native ID entirely, and their benchmark identity lacked the pair. Raw native responses remain worker-temporary; chronological request or metadata row counts are not a substitute for the explicit association.

The locally retained actual A FP32 receipt at `evidence/teacher-scoring-fp32-probe-20261111/native/A/admission-A-r1/requests.jsonl` confirms this narrower gap: its first `cold-r0-s0-full_input` request has a native string at `meta_info.id`, but no top-level `native_request_id` or `pair`; the corresponding completion receipt also has neither field. This read-only inspection did not change the historical artifacts.

Native RID equivalence is source-backed:

- C1 `evidence/native-sglang-cache-source-20261111/exp-1111-035902-035439/source/srt/model_executor/forward_batch_info.py:1103` constructs `ForwardBatch.rids=[req.rid for req in batch.reqs]`.
- C2 `exp-1111-040603-422872/source/srt/managers/scheduler_components/output_streamer.py:488` emits `req.rid`; `srt/managers/tokenizer_manager.py:2727–2740` uses that same received RID as response `meta_info.id`.

**Exact identity contract:** within a run's isolated output directory, join native metadata `rids` to request/completion receipts by `(pair, native_request_id)`, where `native_request_id` is the actual returned `meta_info.id`, never the synthetic `request_id` or a sequence number. Both receipts retain `pair`, `repetition`, `phase`, `mode`, original `source_uid`, original `sample_index` and `sample_position` alongside the native ID. The synthetic `request_id` remains unchanged for filenames and existing numerical comparisons. Repeated native metadata rows with the same RID associate with the same scoring request regardless of row/receipt order; they are not additional scoring requests.

The ID is captured before `_scores` validation, so a known native RID remains in the failed request receipt even when token/logprob validation raises. A failed validation does not produce a completion receipt. If an HTTP/timeout/JSON failure prevents observing the response ID, `native_request_id=null` records that it is unknown; no synthetic ID, chronological association or success claim is substituted. Native response strings are used directly; there is no injected payload `rid`, new config selector, extra request/flush, new metadata recorder, Tensor read, CUDA event, wait or synchronization. Baseline and diagnostic payloads, teacher flags and counts remain unchanged; only receipt fields are additive.

The new focused regression executes the real `_request`/receipt path for both pairs and uses the source owner's actual `mamba-runtime-metadata-v1` recorder schema. It returns two successful requests and one token-ID validation failure with arbitrary native RIDs unrelated to filenames, reorders native `rids`, reverses request receipt lookup order and joins by native ID. It also checks the original payload exactly, retained failed-request identity and matching completion identity. Existing first4 tests additionally verify that the actual benchmark path propagates pair and native ID to all16 requests/completions, still with10 flushes.

Same environment as above. The deterministic retention regression was run before the fix:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k native_response_rids -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-rid-red-20261111
```

Expected: expose the missing native RID association. Observed **2 failed,105 deselected,2 existing warnings,0.90s; expected RED**, both at `KeyError: 'native_request_id'`. The concrete missing-field failure and inspected native RID path identify a receipt-retention defect; no alternative CUDA/runtime hypotheses or temporary debug instrumentation were needed.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'native_response_rids or request_failures' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-rid-green-20261111
```

Expected: exact RID associations survive reordered metadata and validation failures; unobserved IDs remain null. Observed **6 passed,101 deselected,2 existing warnings,0.74s; PASS**.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py tests/fast/test_sglang_mamba_snapshots.py tests/fast/test_sglang_mamba_runtime_metadata.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-rid-joined-20261111
```

Expected: native scoring/submission/source integration unchanged, baseline56/32 and diagnostic16/10 preserved. Observed **306 passed,20 existing warnings,25.54s; PASS**, including all107 probe tests. No test failure or skip occurred. Follow-up owns only the two existing probe/test files and this existing report; no native execution occurred. These CPU joins do not prove that an H800 diagnostic has complete runtime RID coverage or reproduced the drift.

## Single-DP absent-controller receiver follow-up

**Verified cause:** pinned C3 `evidence/native-sglang-cache-source-20261111/exp-1111-042450-358109/source/srt/runtime_context.py:230–240` defines `SpawnRanks.dp_rank: Optional[int]=None`, explicitly meaning no data-parallel controller. Publication at1588 copies this value verbatim. The native recorder correctly retains it, but the previous receiver required all five rank fields to be nonnegative integers. A healthy ordinary DP1 teacher could therefore finish16 scoring requests and then fail only the auxiliary readback.

**Exact contract:** an explicitly present native `rank.dp_rank=None` is accepted only when reported `dp_size==1`. The receiver uses effective respondent0 solely for its bounds/uniqueness checks; it never writes0 into the raw metadata or returned observation rank. Missing `dp_rank` remains malformed, not an absent-controller default. DP>1 still requires explicit nonnegative integer DP ranks, rejects None/bools/negative/out-of-range/duplicates, and requires one response per DP. `tp_rank`, `pp_rank`, `attn_dp_rank` and `attn_tp_rank` still require nonnegative integers and reject None and bools. No other rank normalization or default was added.

The CPU fixture now gives attention-DP its independently assigned integer0 instead of coupling it to optional controller-DP; this changes only the synthetic test rank object, not native source or metadata. Existing A/B first4 HTTP tests now use the actual recorder schema with `dp_rank=None` and integer attention ranks, finish16 requests/10 flushes and assert that both `server_info` and `dp_responses` retain JSON null. Added tests preserve raw input/observation rank, reject missing DP rank and strict invalid values, and retain the existing duplicate-DP check.

Same CPU interpreter/environment as above. An initial fixture-preparation run used the following filter with `--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-dp-none-red-20261111`: **3 failed,33 passed,95 deselected,2 warnings,3.46s**. Its old synthetic helper also set `attn_dp_rank=None`; that confound was corrected before the qualified RED run below, without changing the receiver or relaxing attention-rank typing.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'single_dp or other_rank_types or dp_rank_rejects or first4_16_requests' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-dp-none-red-qualified-20261111
```

Expected: reproduce rejection of a legitimate single respondent with native None while strict invalid cases remain rejected. Observed **3 failed,33 passed,95 deselected,2 existing warnings,2.97s; expected RED**. Both healthy A/B first4 cases ended with readback `failed` instead of `collected`; the direct case raised `ValueError: DP response 0 has malformed metadata rank` with all other rank fields integer0.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'single_dp or other_rank_types or dp_rank_rejects or first4_16_requests' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-dp-none-green-20261111
```

Expected: preserve native None, accept only the supported single-DP case, reject malformed ranks and preserve all scoring artifacts/counts. Observed **36 passed,95 deselected,2 existing warnings,2.71s; PASS**.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py tests/fast/test_sglang_mamba_snapshots.py tests/fast/test_sglang_mamba_runtime_metadata.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-dp-none-joined-20261111
```

Expected: no regression in receipts/RID association, scoring, submission or native preparer contracts; baseline56/32 and diagnostic16/10 remain unchanged. Observed **330 passed,20 existing warnings,27.16s; PASS**, including all131 probe tests; no test failure or skip. Only the existing probe/test/report changed. Native source/recorder, config, flags, payload, requests and flushes remain untouched; no polling, GPU/platform/auth action, Tensor read, event, wait or synchronization occurred. Native first4 acceptance remains PENDING. The two phase reviewers' prior pinned range is not treated as acceptance of this repair; final re-review must inspect the fixed artifacts.

## Phase-review P2 follow-up to67ac0d7f

The primary supplied two phase-review findings from reviewers `ses_e385140f8ffekze1xWJqdjXsEo` and `ses_e385140d9ffei45dl7LAKl9vfw`. This section records their scoped repairs and CPU verification, not a final re-review verdict.

**Standards cause and contract:** the diagnostic extra-native-file branch read only task-local C1/C2/C3 paths, unlike the existing `snapshot_source` fixture's `MILES_PINNED_SGLANG_SOURCE` override. It now reads every extra file from that same pristine override when set; otherwise it uses the existing per-file retained evidence path. A missing required file explicitly skips with its exact path rather than raising incidental `FileNotFoundError` or substituting the host package. The base snapshot fixture applies the same per-file explicit-skip convention. All source bytes are copied to the isolated test temporary root; real preparation changes only that copy, never the override/pristine package.

The new regression builds the complete pristine source set required by both preparers from retained native bytes (or the existing override), supplies it through the existing override, and hides local evidence behind a nonexistent test repository path. It executes both real preparers through the existing worker-ordering test and checks every pristine byte remains unchanged. Its no-override case explicitly checks both missing-base and missing-extra evidence raise the established pytest skip, not an incidental file error. No new source selector, fixture host fallback or native source edit was introduced.

**Spec cause and contract:** `_http` already read the response body, then `raise_for_status()` raised before returning it. The collector's `raw` therefore remained None on503, losing the readback body. `_http` now retains the already-read text only when that same call raises `aiohttp.ClientResponseError`, then bare re-raises the original exception. The passed HTTP record receives `http_error_body={response_text, encoding, provenance}`; the existing final collector receipt retains it at `runtime_metadata.json.http.http_error_body` alongside HTTP status, body byte count/timing, exception type and reason. Encoding is explicitly `utf-8 with replacement`; provenance is `aiohttp response.read(), before raise_for_status()`, not an assertion of raw compressed wire bytes.

No successful HTTP request receives this extra full-body field. The normal scoring payload, exception propagation, existing unsupported-flush handling, collector's independent failure result, scoring-file retention and one final readback are unchanged. There is no fallback, retry, error suppression, extra file/request/flush or new body read. The existing A/B first4 tests assert exact503 content, status503 and `ClientResponseError`, after16 scoring requests/10 flushes with every previously written scoring file unchanged. Existing request/flush tests also assert the original exceptions still propagate; success tests reject extra body dumps.

Same Python3.12.13/pytest9.1.1 CPU environment and temporary storage as above:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'diagnostic_source_fixture_override or first4_16_requests' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-review-p2-red-20261111
```

Expected: reproduce exactly both reported gaps. Observed **4 failed,10 passed,119 deselected,4 existing warnings,3.11s; expected RED**: override/no-evidence cases raised `FileNotFoundError`, and both A/B503 cases lacked `http_error_body`.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'diagnostic_source_fixture_override or first4_16_requests' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-review-p2-green-20261111
```

Expected: real preparation succeeds from pristine override without local evidence, missing evidence skips explicitly, and503 body/status/error remain retained without changing scoring or counts. Observed **14 passed,119 deselected,4 existing warnings,3.18s; PASS**.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py tests/fast/test_sglang_mamba_snapshots.py tests/fast/test_sglang_mamba_runtime_metadata.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/runtime-metadata-review-p2-joined-20261111
```

Expected: original scientific/request/FP32/metadata contracts unchanged. Observed **332 passed,20 existing warnings,27.75s; PASS**, including all133 probe tests; no suite failure or skip. The missing-evidence regression explicitly catches and verifies the expected skip. Only the existing probe/test/report changed; native recorder/source, flags/config/payload/math, baseline56/32 and diagnostic16/10 remain untouched. No GPU/platform operations or reviewer resumption occurred. Immutable fixed-artifact re-review and native acceptance remain PENDING.

## Verification limits and next dependency

All HTTP/GPU-inspection/engine-startup operations in integration tests are CPU mocks; existing cleanup checks start only their owned CPU child. First4 mock HTTP bodies contain only the completion tail needed for request/identity/readback contracts; they do not certify native full-input score ranges or probability vectors. `collected` means structurally present CPU metadata, never native PASS, device-store completion, physical slot content, causal proof or numerical parity. DP respondents do not expose independent receipts from all TP ranks.

The first4 reduction is a candidate minimized reproduction, not accepted until actual A/B four-H800 first4 vectors are compared with the existing FP32 repetition0 vectors and still reproduce sample2/3 drift. It does not cover dropped1024-hit boundary groups. Existing R2 evidence remains cold14/14 exact and warm4/14 exact, max absolute A0.24439287185668945/B0.43827223777770996, with warm-full sample2/3 deviations unchanged; those are prior observations, not this diagnostic's results. Source/operator44/44 and matching after-hashes do not measure live model donor/dtype paths. Native metadata, first4 reproduction, numerical/performance/cause acceptance and formal release remain **PENDING**; only the primary owns any later approved native execution.

## 1. 规划完成情况

**汇总：** PASS 8｜BLOCKED/FAILED/SKIPPED 1｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 独立 diagnostic 配置与原始 first4 manifest | PASS | 原 UID/index/token 不变，16 scoring/10 flush；baseline56/32 不变。 |
| 真实 preparer 接线与独立 receipts | PASS | selected-FP32 后、runtime/attention/teacher 前，两个实际 CPU receipts 分开保留。 |
| post-loop 既有 endpoint 与失败证据 | PASS | DP-only coverage；缺失/malformed 独立失败，scoring 文件保留。 |
| 明确 native RID 关联 | PASS | 真实 response ID 关联到 pair/repetition/phase/mode/UID/index；乱序与 failed validation 回归通过。 |
| native DP1 absent-controller receipt | PASS | 仅DP=1接受显式None，raw/observation保持None，其余rank与非法值仍严格拒绝。 |
| Standards P2：pristine override 与显式 skip | PASS | 无 local evidence 的真实 preparer 回归通过，pristine bytes未变；缺失路径显式skip。 |
| Spec P2：HTTP failure body provenance | PASS | 503 body/status/exception保留，原样re-raise；success不附加完整body。 |
| joined CPU 验证 | PASS | 最新332 passed，20 existing warnings，27.75s。 |
| 实际 H800 first4 重现与 runtime metadata | BLOCKED | 本 subagent 无 GPU/platform 权限；native 仍 PENDING。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 两个phase-review P2 follow-up 请求至332项 joined CPU 完成｜**当前前沿：** 提交三个 owned files 供 immutable re-review；primary 独立决定后续 native 验证。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 只补充两个明确P2的回归及required joined检查，完成后停止扩展。 |
| D2 细节反复重试 | CLEAR | 对应4-case RED→两项定点修复→14-case GREEN；没有失败修复循环。 |
| D3 支线问题修补 | CLEAR | follow-up 只编辑三个授权旧文件，未修改 recorder、launcher、配置或原始 fixtures。 |
| D4 可并行任务停滞 | CLEAR | source 已就绪；本 follow-up 无可独立启动的 native 工作，也无 delegation 权限。 |
| D5 超范围镀金 | CLEAR | 复用现有override/receipt；failure-only body，不加selector/retry/fallback或normal body dump。 |
| D6 分析空转 | CLEAR | 两个具体review findings直接对应真实代码路径、RED与修复。 |
| D7 路线违背 | CLEAR | 无 GPU/platform/auth/SSH/delegation；原生验收未冒充完成。 |

**文档检查：** 当前 scoped assignment 下 S1–S6 均未发现明显缺陷；父任务 formal hold 保持不变。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 交付两个P2 repairs与本报告 → 完成标志：只提交三个 owned files，保留其他 agent 的修改，供两位reviewers的immutable follow-up。
2. primary 后续 native 验证 → 完成标志：按真实 RID 关联 H800 metadata 与评分 identity，first4 与旧 FP32 repetition0 比较且sample2/3 drift 保留；不以 CPU 或缺失 trace 替代。

## 4. 最值得关注的 3 点

1. 两个P2 repairs已通过332项 joined检查；pristine override无local evidence可用，503 content不再丢失。
2. HTTPerror仍原样传播、scoring文件保留，success不dump额外body；RID/DP1契约保持不变。
3. first4 尚未获原生重现验收，且未覆盖 dropped1024-hit groups；formal hold 不变。
