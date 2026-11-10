## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Fix the accepted P2 milestone disposition finding using mandatory retained successful ACK IDs; record RED/GREEN and 27 passing selected checks. |
| 2026-11-10 | Record independent Ticket06 CPU report computation, focused validation, public API and remaining integration/formal evidence work. |

# Ticket06 report computation — synthetic CPU readiness

Task ID: `profile-t06-report-20261110`.

## Outcome and scope

**CPU computation ready: 16 report cases PASS; 27 cases PASS including the existing profile tests after the accepted P2 fix.** No fixture or number below is a formal A/B result. Ticket06 final acceptance remains pending.

Owned deliverables:

- `tests/manual/agent_opd/distillation_report.py`: pure S9 computation, JSON/Markdown output and minimal inspector-backed CLI.
- `tests/fast/test_distillation_report.py`: independent hand-built CPU fixtures and output assertions.
- This report: `task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-10_report_computation.md`.

No core/runtime/inspection module, H200 configuration, task master document, README or other agent's test was edited. No GPU, platform, SSH, network, publication or further delegation was performed.

Inspected authoritative inputs:

- `AGENTS.md` and all ten Markdown rules under `.agents/rules/`.
- `task_memory/task_2026-11-08_qwen35_full_kl_nll/requirements.md`, including D28–D32, the parallel-execution request and D37.
- `task_memory/task_2026-11-08_qwen35_full_kl_nll/spec.md`, S4–S9.
- `task_memory/task_2026-11-08_qwen35_full_kl_nll/plan.md` and `tickets/06-profile-report.md`.
- Existing queries in `tests/manual/agent_opd/distillation_profile.py`; existing CPU examples in `tests/fast/test_distillation_profile.py` and `tests/manual/agent_opd/time_distillation_profile.py`.
- `pyproject.toml`, `.pre-commit-config.yaml` and the CPU environment command in `test_report_2026-11-10_profile_integration.md`.

The frozen `inspect_run` contract came from the primary's task assignment. This slice neither inspected the other agent's progress nor implemented a second native/profile parser or profile state engine.

## Public API and CLI

```python
build_report(receipt, profile, *, cell, milestones=S9_MILESTONES, limitations=()) -> dict
quantile_summary(values) -> dict
render_markdown(report) -> str
write_report(report, *, output_prefix: Path) -> tuple[Path, Path]
```

`build_report` reads the inspector's queryable verified prefix and preserves its complete receipt, including job, expected updates, inspected paths, native counters/terminal/error and profile prefix/first-unverified/ranges/error. It does not derive native success from profile availability. Failed runtime memory and a profile whose length differs from the receipt are rejected rather than reported as verified.

The shared field `receipt.native.observed_successful_update_ids` is mandatory: a list of actual positive integer update IDs from retained successful ACKs, supplied by the inspector. Outside the verified profile prefix, a milestone is `UNVERIFIED` only when its ID is in that list; otherwise it is `NOT_OBSERVED`. `observed_successful_updates` remains a progress count, never an ID-range proxy. The report does not parse native files, infer contiguous ACK IDs or fall back to the count. Every CPU receipt fixture explicitly supplies its synthetic ACK IDs.

The default milestones are the explicit S9 tuple `(1, 10, 50, 100, 150, 200)`; callers can pass another strictly increasing positive sequence. Expected updates are an explicit receipt/CLI input. Estimator, B, N and default k come only from `DistillationProfile`. There are no new training flags, loss calculations, runtime hooks, plots or dashboards.

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B \
  -m tests.manual.agent_opd.distillation_report \
  --training-dir /path/to/one-attempt/training \
  --job exp-one-attempt --cell A/full --expected-updates 200 \
  --terminal-path /path/to/one-attempt/terminal.json \
  --output-prefix /path/to/reports/A-profile
```

The CLI imports `tests.manual.agent_opd.inspect_distillation_run.inspect_run` only after argument parsing, then calls its frozen signature. It writes `<output-prefix>.json` and `<output-prefix>.md`, refusing to overwrite either existing artifact. The example paths/job are placeholders, not inspected formal artifacts. The combined inspector-backed command remains primary-owned and was not run in this slice; `--help` works without that dependency.

## Quantile convention

Only conversation remaining gap, run-relative gap, RKL trend and recovery gap have distributions. Each uses the conversation's own latest entry within the verified prefix. Different conversations can therefore have different latest measurement updates.

Each conversation has equal weight. Exclude only `None`; retain zero and negative defined values. Sort the `n` defined values. At probability `p`, set `h=(n-1)*p` and linearly interpolate between indices `floor(h)` and `ceil(h)`. Report P10/P25/P50/P75/P90. One value supplies every quantile; zero defined values supplies null quantiles. Each distribution separately reports defined and undefined counts. Nonpositive and incomplete conversation baselines are separate counts. No SciPy dependency is used; nonfinite inputs are rejected rather than silently omitted.

## Environment and exact validation commands

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`.

- Test interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python **3.12.13**, pytest **9.1.1**, no conda activation (`CONDA_PREFIX=None`).
- System interpreter: `/usr/bin/python3`, Python **3.10.6**; pure module/quantile checks and CLI help pass on it.
- Host: Linux 5.10.25-nvidia-gpu, x86_64, glibc 2.35. Tests are CPU-only despite the host kernel name.
- Pytest caches and temporary artifacts were confined to `/data/ycfeng/tmp/opencode-v2-tmp/opencode/`.

Initial shell checks found no `python` executable. `/usr/bin/python3` has no pytest package. No environment was installed or changed; the existing task's CPU environment was reused.

First focused run (14 PASS, one FAIL in 0.33 s):

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_distillation_report.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-t06-report-cache --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-t06-report-tests
```

The only failure was exact float equality for interpolated P10: observed `3.0000000000000004`, hand value `3.0`. The assertion was changed to `pytest.approx`; no computed value was rounded, scaled or replaced.

Initial delivery's final focused run and existing-query regression:

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_distillation_report.py tests/fast/test_distillation_profile.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-t06-report-final-cache --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-t06-report-final-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'import ast; from pathlib import Path; paths = ["tests/manual/agent_opd/distillation_report.py", "tests/fast/test_distillation_report.py"]; [ast.parse(Path(path).read_text()) for path in paths]; print("AST PASS", len(paths), "owned Python files")'
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'from tests.manual.agent_opd.distillation_report import quantile_summary; result = quantile_summary([None, 0.0, 10.0, 20.0, 30.0]); assert result["defined_count"] == 4 and result["undefined_count"] == 1; assert result["quantiles"]["p50"] == 15.0; print("Python 3.10 pure reporting import and quantiles PASS")'
python3 -m tests.manual.agent_opd.distillation_report --help
git diff --check
```

Observed: **26 PASS in 0.39 s**, comprising 15 new report cases and 11 existing profile cases. Two pre-existing SWIG import deprecation warnings (`SwigPyPacked` / `SwigPyObject`) were observed. AST: **2 owned files PASS**. System Python pure import/quantiles and CLI help: **PASS**. Whitespace check: **PASS**.

Tool availability command:

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'import importlib.util; print({name: bool(importlib.util.find_spec(name)) for name in ("ruff", "black", "isort", "pre_commit")})'
```

Observed all four modules absent. Ruff/Black/isort/pre-commit validation is **UNAVAILABLE**, not PASS. No network install or unrelated tool repair was attempted.

## Expected versus observed values

All jobs here are hand-built receipts named `synthetic-cpu-report-fixture` (one output-escaping test uses `synthetic|cpu`). Receipt paths are `/synthetic/cell/training`, `/synthetic/cell/training/distillation_profile` and `/synthetic/cell/terminal.json`; these are fixture labels, not real inspected files.

| Case / passing condition | Expected | Observed | Result |
| --- | --- | --- | --- |
| S9 milestones with B10/N8/k10 | Macro baseline mean(2..11)=6.5; RKL at 1/10/50/100/150/200 = 2/11/1/1/4/3; corresponding NLL = update+0.25; each remaining gap = RKL/6.5, including update1 | Exact profile/query values match every milestone and retrospective update1/update10 ratio | PASS |
| Earliest macro RKL tie and associated NLL | Update50 and100 both RKL1; choose50 and NLL50.25, not minimum NLL | `{update_id:50, rkl:1, nll:50.25}` | PASS |
| Default-k macro trend/recovery | At200: trend=(4−3)/6.5; recovery=(3−1)/6.5 | 1/6.5 and2/6.5 | PASS |
| Conversation distributions, full synthetic sequence | Own baseline2; latest RKL3; remaining1.5, run-relative3/6.5, trend0.5, recovery1; all quantiles equal the one defined value | All values and defined1/undefined0 counts match | PASS |
| Sparse own history and baseline-window reference | g entries1/3/5, own baseline4; k3 reference at1, not3; trend=(4−1)/4=0.75 | 0.75; macro baseline2 and retrospective milestone ratios2.5/−0.5/0.5 | PASS |
| Undefined/nonpositive populations | Seen4, alive1, positive baseline1, nonpositive2, incomplete1, defined trend1 | Exact counts; remaining/trend/recovery defined1, undefined3 | PASS |
| Run-relative values retain zero/negative | Sorted latest values [−1,0,0.5,1.5]; P10/P25/P50/P75/P90 = −0.7/−0.25/0.25/0.75/1.2 | Values match within float interpolation tolerance; defined4/undefined0 | PASS |
| Macro baseline zero or−2 | Preserve raw RKL/NLL; dependent remaining/trend/recovery and all conversation ratios null | Raw NLL3 retained; nonpositive count1 and every distribution defined0/undefined1 | PASS |
| No profile or empty profile | Missing macro/best/trend/recovery null; no milestone invented; empty quantiles null; scope explicitly verified prefix | All assertions match; absent profile config unavailable, empty configured profile baseline incomplete | PASS |
| Native200 success with profile3 | Native COMPLETE, profile INCOMPLETE / UNVERIFIED, overall INCOMPLETE; first unverified4/range[4,200]; report only prefix3 | Receipt errors/ranges/counters preserved; later milestones null/UNVERIFIED; conversation scope3 | PASS |
| Quantiles excluding None | [None,30,0,None,20,10] yields defined4/undefined2 and3/7.5/15/22.5/27 | Values match hand arithmetic within float tolerance; zero retained | PASS |
| Written JSON/Markdown | JSON round-trips the report; exact fixture job/paths, limitations, multiline error and quantile convention visible; existing outputs never overwritten | Output files read back and asserted; second write raises FileExistsError without changing bytes | PASS |
| Prefix and milestone contract | Reject failed runtime memory, mismatched/nonempty missing profile and invalid milestone order/types | Expected ValueError assertions pass | PASS |

## Accepted P2 follow-up — retained successful ACK IDs

Task ID remains `profile-t06-report-20261110`.

**[Original Request] Follow-up:** fix the count-based milestone disposition when retained ACK5 is missing but ACK200 exists; consume mandatory `receipt.native.observed_successful_update_ids` directly, provide explicit IDs in CPU fixtures, run RED/GREEN and selected report/profile checks, and leave the joined CLI to primary. Ownership remains the same three files. No inspector/runtime/config/master-document edit or GPU/platform/network/SSH operation is authorized or performed.

The user-confirmed test seam is the existing public `build_report(receipt, profile, ...)` output, with `render_markdown` checking the readable result. The regression uses actual `DistillationProfile` public recording/query APIs and a hand-built receipt; it neither mocks private code nor reads native files.

The fixture retains IDs `1,2,3,4,6,...,200`, exactly 199 successful ACK records. The verified profile contains only updates1–4. The independent expected output is:

| Milestone | Expected disposition | Expected RKL / NLL / remaining gap | GREEN observed |
| --- | --- | --- | --- |
| 1 | VERIFIED | RKL2 retained in verified prefix | Matches |
| 5 | NOT_OBSERVED | null / null / null | Matches |
| 200 | UNVERIFIED | null / null / null | Matches |
| 201 | NOT_OBSERVED | null / null / null | Matches |

The receipt's count remains199 in JSON and readable progress. Exact ACK IDs are preserved unchanged in JSON. Missing ACK5 is not labeled observed merely because5≤199, and ACK200 is not labeled absent merely because200>199. Native/profile completeness is still taken from the inspector receipt; no new native success inference or training gate is introduced.

RED command, before changing report implementation:

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_distillation_report.py::test_sparse_native_ack_ids_distinguish_unverified_from_not_observed -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-t06-ackids-red-cache --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-t06-ackids-red-tests
```

Observed expected **RED: 1 FAIL in0.33s**, specifically `assert 'NOT_OBSERVED' == 'UNVERIFIED'` for milestone200. This reproduced the accepted P2 finding, not an import/setup failure.

Minimal implementation: `_milestone` uses direct ID membership, and `build_report` reads the mandatory shared field once. No count fallback, inferred range, parser, configuration option or profile state engine was added.

GREEN and selected report/profile commands:

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_distillation_report.py::test_sparse_native_ack_ids_distinguish_unverified_from_not_observed -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-t06-ackids-green-cache --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-t06-ackids-green-tests
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_distillation_report.py tests/fast/test_distillation_profile.py -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-t06-ackids-final-cache --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-t06-ackids-final-tests
git diff --check -- tests/manual/agent_opd/distillation_report.py tests/fast/test_distillation_report.py task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-10_report_computation.md
```

Observed: **GREEN1 PASS in0.21s; selected27 PASS in0.39s** (16 report, 11 profile). Python3.12.13/pytest9.1.1 and the existing CPU environment are unchanged. The same two SWIG import deprecation warnings remain. Scoped whitespace: PASS.

The inspector owner supplies the new field independently. This slice did not inspect that agent's progress or invoke the joined CLI. Primary must rerun the inspector-backed CLI with this mandatory field before accepting the joined change. Formal A/B results remain pending. Healthy H200 A is unaffected by this pure CPU report fix; no runtime hook, stop, cancellation or hard gate was added or invoked.

## Verification limits and next actions

1. **Primary: combined CLI integration.** Join the report with the shared inspector, use retained failed-attempt evidence and independently checked synthetic paired records, and inspect both output artifacts. This slice verifies pure receipt+profile reporting and file output, not the inspector's parser or actual native terminal schema.
2. **Formal A/B evidence remains pending.** No actual A/B milestone, source-identity coverage, native counter or terminal result was inspected here. A successful synthetic200 fixture is not a formal run, admission or acceptance receipt. The final task summary and Ticket06 checkboxes were not changed.
3. **Preserve the scientific limits.** The generated reports describe only the verified prefix, do not fill missing updates, and do not claim cross-teacher causality/ranking or that remaining gap measures still-reducible capacity.

## Scoped progress checkpoint

### 1. 规划完成情况

**汇总：** PASS 2｜BLOCKED/FAILED/SKIPPED 1｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 06 CPU S9计算与P2修复 | PASS | RED复现后GREEN通过；16个report与11个profile用例共27 PASS |
| 06 JSON/Markdown输出 | PASS | 输出回读、路径、错误、quantile约定和不覆盖已有证据均通过 |
| Inspector组合CLI | TODO | Primary负责；本slice不读取另一agent进度 |
| 06真实A/B报告与最终验收 | BLOCKED | 仍需04/05实际运行和终态证据 |

### 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次P2 follow-up至RED/GREEN和选定回归完成｜**当前前沿：** 新shared field的组合CLI

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 测试仅覆盖S9与用户明确要求；通过后停止扩展 |
| D2 细节反复重试 | CLEAR | 一次RED复现count/ID差异、一次最小修复、GREEN与回归通过 |
| D3 支线问题修补 | CLEAR | 未修改runtime、H200、inspection或无关工具 |
| D4 可并行任务停滞 | NO DATA | 本slice独立推进；其他agent执行状态不在观察范围 |
| D5 超范围镀金 | CLEAR | 无dashboard、plot、依赖、训练flags或第二解析器 |
| D6 分析空转 | CLEAR | 已交付计算、输出和可重复CPU检查 |
| D7 路线违背 | CLEAR | 直接消费最终shared字段；仅修改3个owned文件，未干预H200 A或声明06done |

**文档检查：** 本次明确的P2验收与shared-field契约没有S1–S6缺陷；owned报告已同步新字段及验证。主task文档当前状态未在本follow-up重新核验，也未改写。
**归因：** 无执行偏离；原问题属于已接受的正确性finding，本次按授权修复。

### 3. 纠正建议

**分支：** A：本次spec/follow-up契约合理，无需改动主文档或tickets。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Primary组合CLI：共享inspector提供actual successful ACK ID列表，再生成JSON/Markdown → 完成标志：稀疏ACK ID、缺失及future milestone均得到正确处置。
2. 独立继续健康H200 A；本CPU fix不引入native停止或辅助hard gate。06最终验收仍使用真实终态证据。

### 4. 最值得关注的 3 点

1. P2已RED/GREEN修复；27个选定检查通过，没有真实A/B测量或完整profile验收。
2. Count199不再误判ACK200；ACK5/201确实缺失时NOT_OBSERVED，prefix外数值保持null。
3. 新mandatory字段的组合CLI仍归primary；本slice不扩大所有权或干预H200 A。
