## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record the first4 diagnostic integration, real source-preparer ordering, joined CPU checks, independent readback failures and pending native acceptance. |

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

## Verification limits and next dependency

All HTTP/GPU-inspection/engine-startup operations in integration tests are CPU mocks; existing cleanup checks start only their owned CPU child. First4 mock HTTP bodies contain only the completion tail needed for request/identity/readback contracts; they do not certify native full-input score ranges or probability vectors. `collected` means structurally present CPU metadata, never native PASS, device-store completion, physical slot content, causal proof or numerical parity. DP respondents do not expose independent receipts from all TP ranks.

The first4 reduction is a candidate minimized reproduction, not accepted until actual A/B four-H800 first4 vectors are compared with the existing FP32 repetition0 vectors and still reproduce sample2/3 drift. It does not cover dropped1024-hit boundary groups. Existing R2 evidence remains cold14/14 exact and warm4/14 exact, max absolute A0.24439287185668945/B0.43827223777770996, with warm-full sample2/3 deviations unchanged; those are prior observations, not this diagnostic's results. Source/operator44/44 and matching after-hashes do not measure live model donor/dtype paths. Native metadata, first4 reproduction, numerical/performance/cause acceptance and formal release remain **PENDING**; only the primary owns any later approved native execution.

## 1. 规划完成情况

**汇总：** PASS 4｜BLOCKED/FAILED/SKIPPED 1｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 独立 diagnostic 配置与原始 first4 manifest | PASS | 原 UID/index/token 不变，16 scoring/10 flush；baseline56/32 不变。 |
| 真实 preparer 接线与独立 receipts | PASS | selected-FP32 后、runtime/attention/teacher 前，两个实际 CPU receipts 分开保留。 |
| post-loop 既有 endpoint 与失败证据 | PASS | DP-only coverage；缺失/malformed 独立失败，scoring 文件保留。 |
| joined CPU 验证 | PASS | 304 passed，20 existing warnings，26.75s。 |
| 实际 H800 first4 重现与 runtime metadata | BLOCKED | 本 subagent 无 GPU/platform 权限；native 仍 PENDING。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次 scoped integration 开始至 joined CPU 完成｜**当前前沿：** 交付已验证的 CPU candidate；primary 独立决定后续 native 验证。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅执行本次所需合约检查；joined 完成后停止扩展。 |
| D2 细节反复重试 | CLEAR | config、focused、joined 三个阶段均通过；没有失败修复循环。 |
| D3 支线问题修补 | CLEAR | 只编辑五个授权文件，未修改 recorder、launcher 或原始 fixtures。 |
| D4 可并行任务停滞 | CLEAR | source agent 独立准备模块；本 slice 同时完成配置/subset/readback。 |
| D5 超范围镀金 | CLEAR | 一个 manifest prefix 机制、一个 diagnostic boolean、一次 post-loop fetch。 |
| D6 分析空转 | CLEAR | retained endpoint/DP 证据直接用于接线和已通过的测试。 |
| D7 路线违背 | CLEAR | 无 GPU/platform/auth/SSH/delegation；原生验收未冒充完成。 |

**文档检查：** 当前 scoped assignment 下 S1–S6 均未发现明显缺陷；父任务 formal hold 保持不变。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 交付 scoped candidate 与本报告 → 完成标志：只提交 owned files，保留其他 agent 的修改。
2. primary 后续 native 验证 → 完成标志：实际 H800 first4 与旧 FP32 repetition0 比较、sample2/3 drift 保留、真实 DP metadata receipt 可读；不以 CPU 或缺失 trace 替代。

## 4. 最值得关注的 3 点

1. CPU 接线已通过304项 joined 检查；没有任何新的 native PASS。
2. server-info 仅覆盖每个 DP 的 responding process，不覆盖全部 TP ranks，也不测设备写完成。
3. first4 尚未获原生重现验收，且未覆盖 dropped1024-hit groups；formal hold 不变。
