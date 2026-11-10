## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Add the isolated FP32 probe configuration and CPU integration evidence; retain independent same-run cold references and native verification limits. |
| 2026-11-11 | Primary completed controller forwarding,202 joined checks and both real controller dry-runs; native submission remains pending. |
| 2026-11-11 | Both H800 probes submitted and await placement; preserve original admission receipts and correct controller-relative config metadata with a verified one-line follow-up. |
| 2026-11-11 | Verify actual deployed source/config and native terminals; cold parity passes, warm acceptance fails, and the isolated operator's44 CUDA checks pass separately. |

# FP32 teacher-scoring probe integration — CPU only

TaskID: `profile-fp32-probe-integration-20261111`.

## Deliverables and observed contracts

- `tests/manual/agent_opd/probe_teacher_scoring.py`: the existing `--config` accepts the isolated probe JSON and reads its repository-relative `formal_config`. A malformed `selected_fp32_snapshots` fails with `ValueError: selected_fp32_snapshots must be a JSON boolean`. Absent/false selection never calls the preparer or changes dependency sources. The existing pinned worker Python and actual H800 allocation checks remain.
- `_run` calls `prepare_source(Path(importlib.util.find_spec("sglang").origin).parent, image=config["image"], selected_fp32=True, archive_dir=output / "source_preflight")` before `_runtime` and teacher startup. The returned receipt is preserved unchanged as `source_preflight` in `preload.json` and `result.json`; its `cuda_semantics` remains `UNVERIFIED`. Only this experiment records the preparer module's actual file identity in `native_scoring_sources`.
- Cold request vectors and IDs are retained in a simple per-run dictionary keyed by `(pair, repetition, source_uid, sample_index)`. Every warm comparison references both independent cold requests and reports all four cold-to-warm numerical comparisons. Existing `full_vs_response_only`, cold full-versus-response comparisons, token/length/finite contracts and A-only historical comparisons remain. There is no numerical tolerance, automatic acceptance, excluded case or additional request/flush.
- `tests/fast/test_teacher_scoring_probe.py`: 20 additional CPU cases cover ordering and a real preparer receipt, absent/false selection, malformed booleans, qualified-image/source errors, unchanged native teacher argv/environment, and distinct cold vectors. The seven-case A/B HTTP fixtures each observe **56 scoring requests, 32 flushes and 28 comparison rows**. They include: correct warm response despite a drifting warm-full; two warm modes drifting together; and distinct cold modes with correct same-mode warm results. Matching uses repetition and sample identity, not token counts or request-count inference. B never uses historical A scores.
- `teacher_scoring_fp32_probe_config.json`: exact text clone of `teacher_scoring_probe_config.json` after removing the new true boolean and restoring `output_parent`. Effective `envs={}`, image, model paths, BF16 teacher argv, cache parameters, concurrency, protocol, seven samples, repeats=2 and budgets remain unchanged. Modification history for the new configuration is recorded here rather than adding a third JSON difference.

The preparation fixture copies the six qualified retained C3 files from `evidence/native-sglang-cache-source-20261111/exp-1111-042450-358109/source` into its temporary directory and executes the existing `prepare_source`. Package discovery/version are mocked; its actual returned receipt and archive are compared, including the two changed source files. These are source-preparation observations, not installed worker dependency verification or CUDA measurements. If retained source evidence is unavailable in another environment, the five source-dependent cases explicitly skip rather than substituting the older host package.

## Commands and results

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. CPU environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python **3.12.13**, pytest **9.1.1**. No GPU/platform/network/SSH/auth operation or delegation was executed. Native HTTP, GPU inspection and server startup are mocked; the pre-existing cleanup checks use only their owned CPU child.

Final focused command — **PASS: 55 passed, 4 warnings, 1.46 seconds**:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/fp32-probe-focused-final-20261111
```

Final existing-related-suite command — **PASS: 165 passed, 20 warnings, 5.20 seconds** (the existing 145 checks plus 20 new cases):

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/fp32-probe-joined-fixed-20261111
```

Warnings are existing SWIG/datetime/Torch-JIT deprecations and CPU-only AWQ/GGUF support notices, not GPU measurements.

### Primary end-to-end controller integration

The controller now passes the isolated probe path as worker `--config` only for a true `selected_fp32_snapshots`, and checks that path under the existing local mount. Absent/false retains the original formal-config command. Six A/B selection cases and six malformed-selection cases passed; no extra GPU role, environment or workload parameter was added.

Primary joined result: **202 passed,20 existing warnings in7.26s**, Python3.12.13/pytest9.1.1. Exact command:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py tests/fast/test_sglang_mamba_snapshots.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/teacher-scoring-fp32-joined-primary-20261111
```

Both controller dry-runs also passed using the actual Python3.10 StepMind environment. For each pair, replace `A` below with `A` or `B` in both arguments:

```bash
PYTHONPATH="$PWD:/data/ycfeng/steptron" PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/tmp/stepmind-env/bin/python -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_fp32_probe_config.json --pair A --receipt task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-fp32-probe-20261111/admission-A-r1.json --dry-run
```

Observed per pair: submitted=false,4 H800/codesign,1 teacher task,32 CPU/256GB,1 replica, no NIC/RDMA override, original two volume mounts, source directory `/data/ycfeng`, and the worker command selects `teacher_scoring_fp32_probe_config.json`. Request/flush counts remain56/32. This verifies launch construction, not actual admission, allocation, preparation or CUDA correctness.

### Native submission and controller receipt follow-up

Both non-preemptible H800 probes are now submitted: A `exp-1111-053300-533764`, B `exp-1111-053259-677817`. The first read-only SDK startup check records **Pending for both**, no replicas and no preload. Admission allowed4 GPUs per pair under the null personal ceiling; this is not physical placement proof. Evidence: `evidence/teacher-scoring-fp32-probe-20261111/{admission-A-r1.json,admission-B-r1.json,startup-A-r1.json,startup-B-r1.json}`. Launchers remain alive without an outer timeout; no new submission or stop was used to inspect them.

The admission receipt's `probe_config` exposed an existing controller bug: resolving the relative CLI path after `os.chdir(local_mount)` records `/data/ycfeng/task_memory/...` instead of the worktree path. The absolute worker argv was already correct, so neither job needs a restart. The fix reuses the existing precomputed `probe_path` for that single receipt field; request/source preparation, command, resources and GPU behavior are unchanged. Original JSON receipts remain untouched. `evidence/teacher-scoring-fp32-probe-20261111/admission-config-path-correction.json` records original receipt hashes and the correct config identity derived from each original worker argv, not from a guessed current directory.

Regression verification on Python3.12.13/pytest9.1.1:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_submission.py -q -k configured_envs -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/probe-config-receipt-red-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_submission.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/probe-config-receipt-green-20261111
```

Expected RED reproduced **2 failed/2 passed in0.38s**: both relative-path cases lost the repository component in `probe_config`. GREEN: **22 passed,2 existing SWIG warnings in0.42s**, including relative and absolute CLI paths under both configured-environment cases. These additional controller-only checks do not rerun or certify the native jobs.

Python 3.10 syntax and exact JSON isolation command — **PASS: both Python ASTs and exact clone assertion**. This checks syntax using Python 3.12's `feature_version`, not execution under Python 3.10:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import ast
import json
import sys
from pathlib import Path
paths = ['tests/manual/agent_opd/probe_teacher_scoring.py', 'tests/fast/test_teacher_scoring_probe.py']
for relative in paths:
    ast.parse(Path(relative).read_bytes(), filename=relative, feature_version=(3, 10))
    print('AST_PY310 PASS', relative)
root = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
base_text = (root / 'teacher_scoring_probe_config.json').read_text()
variant_text = (root / 'teacher_scoring_fp32_probe_config.json').read_text()
base, variant = json.loads(base_text), json.loads(variant_text)
restored = variant_text.replace('  "selected_fp32_snapshots": true,\n', '', 1)
assert restored.replace(json.dumps(variant['output_parent']), json.dumps(base['output_parent']), 1) == base_text
print('CONFIG_EXACT_CLONE PASS: only selected_fp32_snapshots and output_parent differ')
print('PYTHON', sys.version)
PY
```

Whitespace command — **PASS: exit 0, no diagnostics**:

```bash
git diff --check -- tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_teacher_scoring_probe.py task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_fp32_probe_config.json task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_fp32_probe_integration.md
```

The two new untracked files were also checked explicitly; both commands returned the expected no-index difference exit code **1**, with **no whitespace diagnostics**:

```bash
git diff --no-index --check /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_fp32_probe_config.json
git diff --no-index --check /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_fp32_probe_integration.md
```

### Iterations and corrected failure

All focused iteration commands use the final focused command's interpreter, environment, test path and pytest options; only `--basetemp` and the listed `-k` change. The joined first attempt uses the final joined command's test list/options with the listed `--basetemp`.

| Temporary-directory suffix under `/data/ycfeng/tmp/opencode-v2-tmp/opencode/` | Additional selection | Observed result |
| --- | --- | --- |
| `fp32-probe-cold-red-20261111` | `-k warm_scores_use_same_run` | Expected RED: 2 failed in 0.42s; missing `pair`/cold-reference output (`KeyError: 'pair'`). |
| `fp32-probe-cold-green-20261111` | `-k 'warm_scores_use_same_run or fixed_case_identities or comparison_reports'` | PASS: 5 passed in 0.33s. |
| `fp32-probe-source-red-20261111` | `-k selected_source_preparation` | Expected RED: 2 failed, 1 passed in 0.97s; worker did not yet accept probe JSON (`KeyError: 'pairs'`). |
| `fp32-probe-source-green-20261111` | `-k selected_source_preparation` | PASS: 3 passed in 0.75s. |
| `fp32-probe-focused-20261111` | None | PASS: 55 passed in 1.70s. |
| `fp32-probe-joined-20261111` | Joined test list | FAIL: 164 passed, 1 failed in 5.28s; test assumed no attention modules existed anywhere in the shared pytest process. |

The joined failure was diagnosed as a fixture assumption: preceding existing CPU tests already import host attention. The test now snapshots pre-existing attention modules and verifies that this probe adds none before preparation. No production behavior was changed for that failure. Both final focused and joined reruns pass.

## Acceptance limits and PRIMARY handoff

CPU deliverables are complete; no files were staged or committed. The source preparer, its tests/report, submit helper and shared task records were not edited by this task.

**Helper integration:** this was outside the delegated four-file ownership at delivery. PRIMARY subsequently completed it as described above; it is no longer a blocker. Combined fixed-diff review and native H800 execution remain pending.

No native H800 run, donor/state-buffer/dtype observation, kernel semantic verification, teacher probability acceptance, historical-cause attribution or performance PASS is claimed. The real worker must still use its pinned Python, native package origin, actual H800 allocation and this run's independent cold references. Receipt dtype/capability labels are not measured runtime buffers. Formal A/B remain blocked on the existing native acceptance requirements.

The requested JSON history wording conflicts with the stricter exact-two-difference configuration contract; this report records the configuration's history without changing its machine input. PRIMARY can resolve that documentation-format ambiguity without changing the experiment.

## 1. 规划完成情况

**汇总：** PASS 5｜BLOCKED/FAILED/SKIPPED 1｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Source preparation 接入 | PASS | 真实 receipt、顺序、baseline、拒绝路径已验证。 |
| 独立 cold 对照 | PASS | A/B 各56 requests/32 flushes，身份和独立模式匹配。 |
| 隔离配置 | PASS | 仅boolean和output_parent差异。 |
| CPU验证与报告 | PASS | 55 focused/165 joined PASS、AST3.10与diff检查。 |
| Native GPU验证 | FAILED | A/B native执行Succeeded，cold14/14 exact但warm仅4/14 exact；独立operator44/44 CUDA PASS不替代模型验收。 |
| Submit helper转发 | PASS | PRIMARY完成true variant路径转发及12个CPU检查。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 三项H800提交至实际source/terminal及概率核对｜**当前前沿：** 真实snapshot/store/donor选路与canonical KV一致性；不重复同配置提交。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | cb386e74仅修复实际CLI receipt路径；119bb871仅验证既有FP32 stores验收。 |
| D2 细节反复重试 | CLEAR | 路径错误先明确chdir原因，再做一次RED/GREEN；无native重复提交。 |
| D3 支线问题修补 | CLEAR | 修复证据身份和native snapshot验证均服务D40前沿。 |
| D4 可并行任务停滞 | CLEAR | 三项GPU执行均完成；RCA、operator报告、模型结果核对和records独立并行推进。 |
| D5 超范围镀金 | CLEAR | 无新cache/barrier/interval策略；56/32及科学参数不变。 |
| D6 分析空转 | CLEAR | 实际H800结果否定完整修复结论；下一步只采集能区分候选原因的live metadata。 |
| D7 路线违背 | CLEAR | 全部新GPU请求H800/codesign；formal仍暂停，env1未提交。 |

**文档检查：** 共享spec/tickets的S1–S6未发现本任务范围内缺陷；JSON历史格式歧义已单独交给PRIMARY。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动。
**需停止的偏离行为：** 无。
**接下去的路线：** 用既有server-info/internal-state回读接口，在全部请求结束后取得CPU metadata；先验证first4 fixtures×1 repetition的16-request循环能复现，再定位snapshot activation/store/donor或canonical KV一致性。无新GPU同步、内容读取、cache/dtype/interval或容差变化；formal04/05保持暂停。

## 4. 最值得关注的 3 点

1. 真实worker source/config已验证，但模型warm验收FAIL；operator CUDA PASS不是完整修复。
2. Warm-full不是cold oracle，两个cold模式及其request IDs独立保留。
3. CPU PASS不证明CUDA dtype、buffer、donor、概率、历史根因或performance。

## Actual native phase outcome

PRIMARY verified A`exp-1111-053300-533764`/B`exp-1111-053259-677817`: each4H800, actual image165ff0be, expected local NFS mount, creator`i-fengyicheng`, Completed/exit0/restart0. Both applied exactly two source files; all six after hashes match the separate44-check operator. Actual variant config path/sha256 matches the corrected receipt; teacher argv matches R1 except its new worker distribution address. Evidence: `evidence/teacher-scoring-fp32-probe-20261111/{deployed-source-verification.json,terminal-replica-verification.json}`. A first read-only terminal collector incorrectly used a nonexistent admission `image` field; it failed before writing and was corrected to the existing `formal_config` owner. No jobs or native outputs were affected.

Both pairs completed56 requests/32 flushes. Cold14/14 exact; warm full-vs-response exact4/14 with max absolute errors A0.24439287185668945/B0.43827223777770996. The independent-cold checks also fail and both repetitions reproduce. Raw `accepted=null` is not PASS. Full verification, defined-relative/zero-reference errors and matched timing are in `test_report_2026-11-11_fp32_teacher_scoring_results.md`.

The source-preflight `cuda_semantics=UNVERIFIED` label is deliberately retained as source-only history. The separate actual operator CUDA PASS proves exact numerical equality for its finite tensors, not an independently measured bytewise comparison or the model's live varlen donor path. The warm numerical cause remains unresolved; no new semantic fix has been selected.
