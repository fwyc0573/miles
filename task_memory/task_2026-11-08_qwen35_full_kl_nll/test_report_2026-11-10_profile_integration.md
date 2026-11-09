## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Implement Ticket03 native ACK integration, typed launcher configuration and permanent profile soft-gate isolation; record CPU verification and formal-runtime limits. |

# Ticket03 — rollout profile integration

TaskID: `profile-t03-integration-20261110`. Prerequisites: D35 merge `55fba827`; accepted Ticket02 CPU-ready commit `6129aefe` and its [measurement report](test_report_2026-11-10_per_turn_sums.md). Primary-owned formal guard correction `059a6a75` keeps configured `bank_uses=50` while full mode still visits each bank once. No GPU, platform, network, new smoke or formal run was performed.

Outcome: **Ticket03 integration CPU-ready**. Final selected suite: **201 PASS in67.48s**, including Ticket02 CPU/Gloo regressions, real rollout/ACK fault handling and native custom-view/launcher propagation. Formal profile/GPU acceptance remains at A's actual first successful update under D16.

## Implementation and ownership

- `tests/manual/agent_opd/swe_replay.py`: constructs one optional rollout-side profile; only successful `on_train_result` ACKs reach it. Canonical acquired trajectories join ACK rows by UID to `source.group_id` and `source.assistant_turn_ordinal`, in actual bank slot order. Failed slots never become observations. The data source's `finished_conversations` tuple is captured immediately after bank drawing and retained through skipped optimizer attempts, rather than inferred from retained samples. Thus a final turn rejected for length or missing after native acquisition still closes an already-trained conversation on the successful bank ACK. Native ACK admission, successful counters, full/r256 scheduling and native failure handling remain unchanged.
- `tests/manual/agent_opd/distillation_profile.py`: owns all derived measurements, consistency checks and the two durable files. It compares row coverage, each UID's original-mask token count, native actual/expected counts, bank membership verdict, both macro means and the native estimator label. The first valid native label binds the profile; no second estimator classifier was introduced. `invalidate(update_id, reason)` is the sole public invalidation API, retaining the first `unverified_from`, `unverified_reason` and `latest_verified_update` with structured log evidence. Subsequent updates are ignored; derived queries reject the invalidated profile rather than exposing values based on partly applied state. Earlier raw update/conversation-entry rows remain readable. `latest_update` can include an applied but unsuccessfully persisted update and must not be interpreted as the verified prefix.
- Directory initialization failures are soft and invalidate from update1. If construction itself raises, `SweReplay` retains `profile_initialization_error`, logs the update1 unverified start, never retries construction, and still processes healthy native ACKs. Logging failures are also isolated.
- `tests/manual/agent_opd/run_swe_opd.py`: maps the explicit top-level `profile` object into existing custom-function CLI/schema fields. Field validation derives directly from `SweReplayConfig`; there is no parallel profile defaults table. Unknown keys, non-objects, blocks without explicit `enabled`, coerced booleans and invalid lengths are rejected before execution.
- Tests: existing `tests/fast/test_distillation_profile.py` and `tests/fast/test_swe_launcher.py`; new `tests/fast/test_swe_profile_integration.py`. No edits to `swe_tis.py`, `swe_training.py`, native core, configs, shared progress, tickets or documentation were made by this delegation. Concurrent primary changes are excluded from its commit.

No model forward was added. Turn sums remain transient in the existing native ACK, not duplicated into trainer logs/ACK fields. The only durable turn rows are `<swe_evidence_dir>/distillation_profile/observations.jsonl`; macro/query summaries use the paired `updates.jsonl`.

## Exact configuration interface

Primary-owned formal configuration must explicitly enable the new path:

```json
"profile": {
  "enabled": true,
  "trend_window": 10,
  "baseline_updates": 10,
  "baseline_turns": 8
}
```

| JSON key | Typed native field / CLI flag | Default |
| --- | --- | --- |
| `profile.enabled` | `swe_profile_enabled` / `--swe-profile-enabled` | false |
| `profile.trend_window` | `swe_profile_trend_window` / `--swe-profile-trend-window` | 10 |
| `profile.baseline_updates` | `swe_profile_baseline_updates` / `--swe-profile-baseline-updates` | 10 |
| `profile.baseline_turns` | `swe_profile_baseline_turns` / `--swe-profile-baseline-turns` | 8 |

Lengths are strict positive integers and enabled is a strict boolean. Omitted `profile` preserves the reused capacity/formal paths with profiling disabled. An explicit object must include `enabled`; omitted lengths then use the typed native defaults. Both existing protocols retain their scheduling behavior; this parent's formal cells still require full mode.

## Environment and exact commands

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Python: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, 3.12.13; pytest9.1.1. No conda activation. All training/measurement checks use CPU fixtures and the existing CPU/Gloo Ticket02 tests, not CUDA execution.

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_distillation_profile.py tests/fast/test_swe_profile_integration.py tests/fast/test_swe_replay.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-pytest --basetemp=/data/ycfeng/tmp/t03-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_swe_launcher.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-launcher-pytest --basetemp=/data/ycfeng/tmp/t03-launcher-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_distillation_profile.py tests/fast/test_swe_profile_integration.py tests/fast/test_swe_replay.py tests/fast/test_swe_launcher.py tests/fast/test_swe_tis.py tests/fast/test_swe_turn_sums.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-final-pytest --basetemp=/data/ycfeng/tmp/t03-final-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m ruff check tests/manual/agent_opd/distillation_profile.py tests/manual/agent_opd/swe_replay.py tests/manual/agent_opd/run_swe_opd.py tests/fast/test_distillation_profile.py tests/fast/test_swe_launcher.py tests/fast/test_swe_profile_integration.py
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'import ast; from pathlib import Path; paths = ["tests/manual/agent_opd/distillation_profile.py", "tests/manual/agent_opd/swe_replay.py", "tests/manual/agent_opd/run_swe_opd.py", "tests/fast/test_distillation_profile.py", "tests/fast/test_swe_launcher.py", "tests/fast/test_swe_profile_integration.py"]; [ast.parse(Path(p).read_text()) for p in paths]; print("AST PASS", len(paths), "owned Python files")'
git diff --check
git diff --cached --check
```

| Check | Passing condition | Observed | Verdict |
| --- | --- | --- | --- |
| Initial profile/real integration/replay | All selected cases pass | 94 passed in2.25s | PASS |
| Launcher and native custom-schema propagation | All selected cases pass | 71 passed in15.19s | PASS |
| Final affected suite including Ticket02 | All selected cases pass after final fault-case refinements | 201 passed in67.48s;41 dependency/runtime warnings, no failures | PASS |
| Ruff | Owned files pass lint | `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python: No module named ruff`; no host `ruff` executable found | UNAVAILABLE |
| Syntax | All six owned Python files parse | AST PASS6/6 | PASS |
| Whitespace / commit scope | No changed-line whitespace errors; stage only seven owned files | `git diff --check` and final `git diff --cached --check` exit0; staged list contains only this report and six owned Python files | PASS |

## Decisive CPU observations

- The real plugin processes skipped ACK0 followed by successful ACK1 on the identical canonical bank without new generation. The bank's source finish report survives both the skip and an intentionally changed source report. Initial valid slots0/2 contain3 target tokens; source conversations are assigned c_id0=`g1`, c_id1=`g0` despite reversed ACK row order. RKL=4/3, NLL=8/3, g0 becomes not alive, and failed/untrained conversations have no profile column. Four successful updates produce eight observation rows, four paired file lines and identical offline rebuild/query results; full mode uses four banks, with12 native generation calls total. Baseline and historical gap queries use hand-computed values.
- Mismatch injections cover missing/duplicate/unknown UIDs, per-UID token exchanges that preserve the aggregate count, native and expected tokens/turn counts, unverified row/bank flags, changed estimator, both macro means, bank/visit, teacher/protocol and missing/invalid/duplicate source turn identity. A failure at successful update2 leaves `latest_verified_update=1`; subsequent healthy ACKs reach successful update4 and exhaust the native schedule, while profile files remain byte-identical to the prefix. Native `unverified_turn_sums` reasons survive intact, including a successful ACK with no measurement rows.
- Native custom-schema parsing, serialization and actual rollout custom-view construction preserve all four fields. Enabled and disabled paths are separately checked. The serialized formal full configuration still carries bank_uses50, while `ReplaySchedule.uses=1`; existing r256 visits and replay_num remain supported without changing this parent's protocol.

## Partial-file failure evidence and honest disposition

Fault injection uses the real `SweReplay.on_train_result` path, with a healthy update1, a filesystem error at update2, then healthy native updates3/4. In all cases the native successful counter reaches4, the profile's verified prefix ends at1, the unverified start remains2, and no later profile bytes are appended. The logged reason is `OSError: injected profile filesystem failure` and structured evidence includes `verified_through=1`.

| Failure point | Complete update IDs in observations | Complete update IDs in updates | Tail evidence / rebuild disposition |
| --- | --- | --- | --- |
| Before observations update2 | 1 | 1 | Only the complete paired prefix1 rebuilds; native updates2–4 are missing from the profile |
| Before updates update2 | 1,2 | 1 | Unpaired observation2 is retained; whole-file rebuild rejects `1 update lines and 2 observation lines` |
| Partial observations update2 write | 1 | 1 | Observations retains malformed tail `{"update_id": 2, "incomplete":`; whole-file rebuild raises JSONDecodeError |
| Partial updates update2 write | 1,2 | 1 | Updates retains the same malformed tail; whole-file rebuild raises JSONDecodeError |

No trimming, rollback, fabricated rows or derived values fill updates2–4. The valid common prefix is update1 only; the orphan/malformed update2 bytes are failure evidence, not verified observations. An otherwise rebuildable one-update paired prefix is not a complete four-update training profile, and would not satisfy the formal200-update criterion. Runtime does not reread the files; offline inspection must compare paired-prefix counts with native successful ACKs and the retained unverified start/reason.

## Remaining acceptance

- CPU implementation readiness is not Ticket02 GPU acceptance or formal Ticket04/05 completion. D16 inspection still requires A's first actual formal successful update: actual native row/token counts and current-policy timing, canonical bank UID/source identity, estimator and both profile files. B admission depends on that actual update and completed inspection, not a PASS auxiliary verdict.
- This delegation does not claim performance measurements at256 native GPU turns, actual interleaved-source training values, 200-update profile completeness, B teacher runtime or whole-run trend coverage. Existing accepted module performance evidence is reused rather than rerun.
- If invalidation occurs, derived runtime profile queries reject the profile. A caller needing verified historical queries should rebuild/inspect only the complete retained prefix; incomplete files must not be silently repaired. Ruff could not be run in the existing CPU environment; no dependency installation was attempted.

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 2

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Ticket01 input acceptance | PASS | 已有D34原位审计证据，当前任务未重复执行 |
| Ticket02 CPU prerequisite | PASS | 用户接受6129aefe和测量报告；GPU验收仍待A首次update |
| Ticket03 integration CPU slice | PASS | 最终201项、AST6/6和报告完成；GPU验收不在本slice |
| Ticket04 A/full | TODO | 尚未启动，等待03 CPU-ready和primary配置冻结 |
| Ticket05 B/full | BLOCKED | 等待A真实首次successful update和完成检查 |
| Ticket06 report | TODO | 等待两cell终态和profile完整性证据 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次Ticket03授权至最终201项CPU检查｜**当前前沿：** 本slice提交与primary formal配置冻结

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 测试直接核验03一致性、S7和typed launcher criteria |
| D2 细节反复重试 | CLEAR | 两组首轮测试均通过，无反复修复循环 |
| D3 支线问题修补 | CLEAR | 无上游、GPU、平台或无关代码修改 |
| D4 可并行任务停滞 | CLEAR | 当前agent禁止再委派；primary独立拥有formal config和共享文档 |
| D5 超范围镀金 | CLEAR | 新字段、public invalidation和故障案例均由本次授权要求 |
| D6 分析空转 | CLEAR | 读取直接形成代码和可执行验收证据 |
| D7 路线违背 | CLEAR | 已满足D35/02 CPU前置条件；保持D16、不增加smoke |

**文档检查：** S5：共享`progress.md:179–181`仍称02 CPU-ready未记录，与用户已接受6129aefe及测量报告不一致；由primary更新。S1–S4、S6未发现新的执行阻塞。
**归因：** 无执行偏离；共享状态落后于已接受的代码和报告。

## 3. 纠正建议

**分支：** B：共享状态需同步，不改变spec/tickets的验收标准。

**文档更新（先执行）：**
1. Primary更新`progress.md`当前frontier，并按新证据同步02/03 CPU-ready状态；保留GPU验收未完成（可直接执行，超出本agent文件所有权）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 本agent仅提交owned files → 完成标志：已验证03 CPU-ready代码及本报告的scoped commit。
2. Primary并行显式启用formal profile配置并冻结 → 完成标志：原生CLI解析和full bank uses保持原行为。
3. A首次真实successful update及D16 inspection → 完成标志：保留native/profile分开判定的检查结果，再考虑B资源准入。

## 4. 最值得关注的 3 点

1. Native成功计数继续推进，不等于profile完整；失败后仅update1配对前缀可验证。
2. 正式配置必须显式启用`profile.enabled=true`；复用路径缺省关闭。
3. 201项CPU通过不代替GPU验收；A正式首次update检查仍未执行。
