## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Implement bounded read-only native/profile prefix inspection; record CPU readiness, retained failed-attempt disposition and remaining formal acceptance. |

# Offline Distillation run inspection

TaskID: `profile-offline-inspection-20261110`.

Outcome: **CLI CPU-ready, 57 selected tests PASS in 1.78s**. This completes only the delegated offline entry and its tests. Ticket04/05 first-update and final formal acceptance remain pending; Ticket06 report computation belongs to another agent. No network, platform, SSH, GPU, delegation, training control or runtime/configuration edit was performed.

## Owned deliverables

- `tests/manual/agent_opd/inspect_distillation_run.py`
- `tests/fast/test_distillation_run_inspection.py`
- This report: `task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-10_offline_inspection.md`

Existing runtime, report computation, configuration, master task documents, other tests and unrelated working changes are excluded from the commit. The existing fast profile fixture and `DistillationProfile` public APIs are reused; no second RKL/NLL/baseline/trend implementation was added.

## Frozen Python and CLI interfaces

```python
from pathlib import Path
from tests.manual.agent_opd.distillation_profile import DistillationProfile
from tests.manual.agent_opd.inspect_distillation_run import inspect_run

inspect_run(
    training_dir: Path,
    *,
    job: str,
    expected_updates: int,
    terminal_path: Path | None = None,
) -> tuple[dict, DistillationProfile | None]
```

- All minimum receipt keys requested by the primary are preserved: `job`, `expected_updates`, `paths`, `native` and `profile`, including both completion booleans and both progress/count fields.
- `job` must match each native ACK's `attempt` and the supplied terminal's `job`. This follows `run_swe_opd._prepare_training`, which supplies `KUBEBRAIN_RJOB_NAME` as `swe_attempt`. ACK cell, teacher, protocol and run-kind identity must stay constant. Full mode uses bank `u-1`, visit1; skipped attempts advance attempted counters without advancing successful IDs or bank IDs.
- `observed_successful_updates` counts successful receipts in the bounded parsed snapshot. `successful_updates` is null when the native sequence is absent, partial, discontinuous or outside the expected budget. When present, its explicitly recorded scope is the retained successful ACK sequence, not an inferred final count from exit status. Native completion requires the supplied expected count plus a matching `Succeeded` terminal with `native_execution_succeeded=true`.
- Final formal inspection supplies `expected_updates=200`. A first-update/live snapshot may omit a terminal. Its verified prefix remains queryable, but native completion is unverified.
- `verified_updates` requires complete paired rows, reproducible summaries, native counts/macros/estimator, and retained canonical bank UID/source-turn/mask evidence. Missing `bank_<id>.jsonl`, missing seal or mismatching UID/mask evidence ends the prefix; no UID verification is inferred from a native boolean alone.
- Inclusive `unverified_ranges` covers everything after the verified prefix to the expected budget, including observed extra records. `missing_pair_ranges` separately identifies updates lacking either paired file row. `read_errors` preserves missing-file and malformed-tail evidence; `terminal_error` separately preserves terminal failure when native files are missing.
- Return value two is a clean rebuilt profile of exactly the verified prefix, or `None` for zero verified updates. Error-tainted first-pass state is discarded. The returned object has no persistence directory and no runtime invalidation attached to later unverified updates.

CLI: `python -m tests.manual.agent_opd.inspect_distillation_run --training-dir ... --job ... --expected-updates 200 [--terminal ...] [--output ...]`. Without `--output`, JSON is printed. Incomplete evidence returns a normal exit; it is not a native gate. Output cannot overwrite retained evidence inside `training_dir` or the supplied terminal.

## Verification method

Native and paired profile files are read only through the bounded snapshot: at most `expected_updates+1` records from each file. Complete newline-terminated rows are required. A sealed bank's candidate declaration bounds its events; only source UID/group/turn and original-mask counts are retained in memory, not large token/score payloads.

The first pass calls real `DistillationProfile.record_update(..., native_record=..., bank_token_counts=...)`, checks its public observations and summary against the retained pair, and checks the existing native numerators/denominators against the resulting `UpdateRow`. Only accepted original pairs are copied under `/data/ycfeng/tmp` into a temporary prefix. The second pass calls strict `DistillationProfile.rebuild` on that prefix. Originals are never trimmed, repaired or appended. No parsing of rebuild error strings determines the prefix.

## Environment and exact commands

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`.

Python: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, 3.12.13; pytest9.1.1. No conda activation or dependency installation. Initial `python --version` failed with `zsh:1: command not found: python` (exit127). System `/usr/bin/python3` is 3.10.6 and has no pytest; the established CPU environment was used instead. Ruff, Black and isort are absent from that environment.

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_distillation_run_inspection.py tests/fast/test_distillation_profile.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/offline-inspection-pytest --basetemp=/data/ycfeng/tmp/offline-inspection-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_distillation_run_inspection.py tests/fast/test_distillation_profile.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/offline-inspection-final-pytest --basetemp=/data/ycfeng/tmp/offline-inspection-final-v2-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m ruff check tests/manual/agent_opd/inspect_distillation_run.py tests/fast/test_distillation_run_inspection.py
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'import ast; from pathlib import Path; paths = ["tests/manual/agent_opd/inspect_distillation_run.py", "tests/fast/test_distillation_run_inspection.py"]; [ast.parse(Path(p).read_text()) for p in paths]; print("AST PASS", len(paths), "owned Python files")'
git diff --check
git diff --cached --check
```

| Check | Expected / passing condition | Observed | Verdict |
| --- | --- | --- | --- |
| Initial selected suite | Inspection plus accepted profile tests pass | 53 passed in1.01s; no failures | PASS |
| Final selected suite | Required additional missing/native-tail/extra-row cases and job binding pass | 57 passed in1.78s, two existing SWIG deprecation warnings | PASS |
| Whole new fast CPU file budget | Less than30s; no explicit slow registration needed | New46 cases plus existing11 cases complete in1.78s | PASS |
| CLI partial snapshot | Exit0, honest incomplete receipt, protected original bytes | Test passes; verified1, unverified2–200, overwrite attempt exits2 without modifying source | PASS |
| Syntax | Both owned Python files parse | AST PASS2 | PASS |
| Ruff | Selected files lint successfully | Original error: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python: No module named ruff`, exit1 | UNAVAILABLE |
| Whitespace and staging scope | No whitespace errors; only three owned files staged | Final scoped checks and staged file list checked before commit | PASS |

No unit-test assertion failed during implementation. The unavailable interpreter alias/lint tool are environment limitations, not repaired with new tooling.

## Decisive synthetic CPU observations

- Uneven turns reuse the existing hand-computed sequence: update1 has3 turns and8 tokens, RKL `6/8=0.75`, NLL `8/8=1`; its first conversation's equal-turn baseline is `(2/4+3/2)/2=1`, rather than its token-weighted mean. The run baseline after two updates is `(0.75+0.4375)/2=0.59375`; rebuilt historical remaining gap is `0.75/0.59375`. Tied best remains update2. Query results match the accepted fixture.
- A skipped ACK between successful updates1/2 produces successful IDs1–4, attempted IDs0,2,3,4 and unchanged full bank numbering0–3. No skipped observation is fabricated.
- Successful native completion with one profile file cut after update1, malformed final bytes, or valid JSON without a final newline still reports4 native successful updates and native complete=true, but only verified profile update1, first unverified2 and unverified/missing-pair range2–4. Returned baseline is null, so partly applied update2 cannot leak derived values.
- Native token/turn counts, expected counts, both macros, numerator/denominator, estimator and verification flags fail only profile acceptance. Exchanging individual masks while keeping aggregate token totals fixed also fails. Unknown source UID, changed source turn, mismatching membership, missing bank and missing seal bound the profile prefix at1.
- Corruption of an earlier derived baseline, best, alive count or configuration summary ends the prefix before that row even when later rows are present. A partial native receipt makes the total null while retaining the earlier paired prefix. One-file-only profile evidence cannot supply a first verified update. Extra records are explicitly unverified, not silently discarded.
- A four-update fixture with expected200 is incomplete, covering unverified5–200. The separate synthetic200-update fixture verifies the full bounded path in0.10s and is identified as `run_kind=smoke`; it proves CPU readiness only.

## Retained failed H800 receipt: identity/failure disposition only

Only one existing terminal receipt was inspected; no cloud scan, platform query or log/RCA expansion was performed. The expected local `A/training` files are not retained in the inspected directory. Exact command:

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.inspect_distillation_run --training-dir /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/formal-h800-112k-20261110/full/exp-1110-014836-849060/A/training --job exp-1110-014836-849060 --expected-updates 200 --terminal /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/admission-formal-A-20261110.terminal.json --output /data/ycfeng/tmp/opencode-v2-tmp/opencode/offline-inspection-failed-H800-verified.json
```

Observed output: exit0; matching job `exp-1110-014836-849060`, terminal UID `ccc4c4e4-3945-4159-8021-e0f0b17008f5`, phase `Failed`, and failure message `Tasks with failed status: [student]`. Native observed receipts=0, but successful_updates=null, not a proven0 actual updates. Native complete=false, profile verified_updates=0, profile=None, first unverified1, unverified/missing-pair range1–200. The missing paths and terminal failure remain separate error fields. PASS means honest offline disposition, not native/profile acceptance or an independent reconstruction of the historical startup failure.

## Remaining verification limits

- Actual A first-ACK/D16, per-turn GPU measurement acceptance, timing checks, B admission and both200-update formal results remain unverified by this work. H200 configuration/platform work is owned by the primary.
- Canonical bank UID/group/training-turn/mask verification does not establish native SWE instance/repository identity, source-manifest provenance, model checksums, actual scoring timing or tensor values. Source conversation finish IDs are replayed from retained profile observations; the transient source finish report is not independently reconstructed, especially for rejected/missing last turns.
- Native successful count is explicitly scoped to retained receipts. A terminal exit alone cannot establish a missing native counter or missing ACK sequence. Full runtime/scientific acceptance still requires the primary's actual evidence, not synthetic receipts.
- The reporter must use this API on retained `training` directories and supply matching job/attempt identity. Fixtures exercising the joined CLI need canonical `bank_<id>.jsonl` files; without them the correct result is zero UID-verified prefix and no queryable profile. The other agent's reporter integration is not claimed complete here.
- Ruff was unavailable; syntax and selected runtime tests passed. No lint dependency installation or unrelated formatting was attempted.

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 2

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Ticket01 | PASS | 已有D34原位验收，本次不重跑 |
| Ticket02 | TODO | CPU已接受，GPU验收仍需A首个真实update |
| Ticket03 | PASS | 已有15186817 CPU接入验收 |
| Ticket04离线准备 | PASS | 本slice接口、CLI和57个CPU测试已验证 |
| Ticket05正式执行 | BLOCKED | 仍依赖A真实首个ACK、完成inspection和fresh资源 |
| Ticket06最终报告 | TODO | 计算实现并行由另一agent负责；真实数据未完成 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本TaskID委派开始至CPU CLI-ready｜**当前前沿：** primary H200准备、reporter联合CLI检查。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅交付指定离线入口和验收用例，CPU-ready后停止 |
| D2 细节反复重试 | CLEAR | 测试无失败；无平台retry或新工具安装 |
| D3 支线问题修补 | CLEAR | 只拥有指定三文件 |
| D4 可并行任务停滞 | CLEAR | reporter文件并行出现，平台由primary负责 |
| D5 超范围镀金 | CLEAR | 无新算法、runtime gate、配置或GPU smoke |
| D6 分析空转 | CLEAR | 读代码后完成实现、CPU测试和真实失败处置 |
| D7 路线违背 | CLEAR | 遵循D37和并行授权；未修改科学/native规则 |

**文档检查：** S5：`plan.md` current frontier及`spec.md` S0/`tickets/04-a-full.md`仍有D36/H800等待文本，与`requirements.md` D37及plan当前H200阶段不一致；S1/S2/S3/S4/S6未发现新的明显缺陷。
**归因：** 无执行偏离；旧阶段文字由primary维护，不作为本slice新增阻塞。

## 3. 纠正建议

**分支：** B：当前阶段记录存在旧文字；离线行为规格无需变更。

**文档更新（先执行）：**
1. Primary更新`plan.md` current frontier、`spec.md` S0和`tickets/04-a-full.md` current status，按已授权D37表述H200准备并保留历史H800失败（可直接执行；这些文件不在本slice所有权内）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Reporter联合CPU CLI：使用冻结接口和canonical bank fixture → 完成标志：S9报告只读取验证前缀，真实失败和合成值区分清楚。
2. 并行：primary H200准备/准入 → A实际首个ACK及完成inspection → B fresh资源准入；不等待A200或辅助PASS。

## 4. 最值得关注的 3 点

1. 指定离线入口已CPU-ready；不能据此勾选正式cell验收。
2. 缺少canonical bank或native ACK时不推断UID/实际更新数；只返回真实验证前缀。
3. Reporter接口已冻结；H200执行和真实A/B数据仍归primary推进。
