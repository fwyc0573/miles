## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Implement the CPU-only first4/rep0 inspector; verify synthetic faults and archived A/B negative cases without reading the new native runs. |

# Cache-salt probe CPU inspection

TaskID: `profile-cache-salt-native-inspection-20261111`.

## Outcome and ownership

**CPU preparation PASS: 41 new regressions, 36 affected existing comparison/receiver checks, and both archived A/B CLI negative cases pass their expectations. New counterfactual native results remain UNVERIFIED and were not read.** No GPU/auth/platform/SSH operation, new instrumentation, source overlay, configuration change, tolerance or performance claim was made.

Owned deliverables only:

- `tests/manual/agent_opd/inspect_cache_salt_probe.py`
- `tests/fast/test_cache_salt_probe_inspection.py`
- This report.

Requirements and interpretation remain owned by [requirements.md](requirements.md), [plan.md](plan.md), and [preregistered spec](spec.md#d40-diagnostic-namespace-counterfactual-preregistration), canonical `272c`. Caller intervention semantics were inspected at `0c606967`. The supplied baseline must already be independently qualified under the [A](test_report_2026-11-11_runtime_metadata_native_A_results.md)/[B](test_report_2026-11-11_runtime_metadata_native_results.md) reports and pinned caller `4f1139b0`; the inspector does not replace that source/native qualification with a new hashing mechanism.

## API and CLI

```python
from tests.manual.agent_opd.inspect_cache_salt_probe import inspect_probe
report = inspect_probe(pair, output_dir, baseline_dir)
```

After the primary receives native termination, it can run the following command with the exact terminated run and same-pair verified baseline directories. This example is **not an executed new-run command**:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.inspect_cache_salt_probe \
  --pair B --output-dir "$TERMINATED_COUNTERFACTUAL_DIR" --baseline-dir "$VERIFIED_SAME_PAIR_BASELINE_DIR"
```

The CLI emits strict JSON to stdout and returns0 only for CPU controls/isolation/evidence qualification; otherwise it returns1. Native completion is a separate result-receipt observation, not a platform/container terminal assertion. A CPU PASS is not numerical warm acceptance: each of the four `warm_full_vs_own_cold` comparisons must be interpreted separately. Missing/ambiguous evidence stays UNVERIFIED; observed failed isolation equalities stay FAIL.

Report fields retain:

- Six-part logical identity `(pair, source_uid, sample_index, repetition, phase, mode)` explicitly mapped from native RID. Successful16 request/response/vector identities bind to the fixed source token tails; no sequence or count creates an RID association.
- Eight full-input salts equal to `pair + ':' + pre-send request_id`, eight response-only null-salt receipts, and the exact10 flush identities/statuses. Twelve controls compare eight response vectors and four cold-full vectors against the verified baseline using existing `_comparison`.
- Four warm-full comparisons against their own run's cold-full only, including exactness, maximum absolute/defined relative error and undefined-zero-reference count. There is no new tolerance or full-vs-response gate.
- Actual typed `request.meta_info.num_retractions`; missing/null/bool/string/negative/noninteger values remain unverified. Retraction and initial/complete chunk/tracking differences are observations, not an extra unchanged gate.
- Each responding process/rank scope validated through existing `_runtime_metadata_states`; raw DP1 `dp_rank=None` is retained. Begin/rebind buckets use unique `(rid,page_aligned_len)`; returned/rebind buckets use unique `(rid,node_id,prefix_len,mamba_exist)`. Bind first, then test returned prefix/protected, rebind start/protected, and rebind end/page-aligned independently. All ordinary rows must be used exactly once; declined/non-Mamba observations retain scope and counts without manufactured matching.
- Scheduler chunks keyed by `(rid,prefix_len,extend_len,seq_end)`, validated sum and contiguous token-position coverage. Plan batch row `i` binds through `rids[i]` and its CPU prefix/extend; native masks, track lengths, grids, chunk indices and logical batch context remain in the report. `h_src[k]` is retained as a flattened source index for `h_rows[k]`, never a request-chunk index. Identical normalized plan observations on a unique chunk deduplicate; conflicting plans remain unverified. Mask-false chunks remain present. Per-layer allocation/store counts are observations, not chunks. Tensor object addresses are not join or comparison identities.

## Environment and commands

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`.

CPU executable `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, pytest9.1.1; `CONDA_DEFAULT_ENV` unset. Final pytest temporary files use the approved local `TMPDIR`; bytecode and pytest result-cache writes are disabled. Isolated inspector import loads neither `torch` nor `sglang`.

### Focused regressions

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/fast/test_cache_salt_probe_inspection.py
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/fast/test_teacher_scoring_probe.py -k 'comparison_reports or metadata_single_dp or metadata_dp_rank or metadata_other_rank or metadata_dp_responses or runtime_metadata_malformed_payload'
```

Expected: all selected tests pass, qualified synthetic controls with original response-only warm drift pass, valid-bound negative inequalities FAIL, ambiguity/missing evidence UNVERIFIED, changed observed retractions/tracking do not introduce an unchanged gate. Actual: **41 passed** and **36 passed /115 deselected**, respectively; both exit0. Each run has two existing SwigPy deprecation warnings. The new file fits the implicit fast CPU registration; no CI registry or shared GPU runner was changed.

### Archived A/B CLI negative regressions

These are the only native business outputs read. A/B each use their own old directory as both run and baseline deliberately: vector controls must be exact, but the absent full salts and actual cross-request isolation failures must remain negative. This does not simulate a successful native salt intervention.

Exact final command:

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import resource
resource.setrlimit(resource.RLIMIT_AS,(30*1024**3,30*1024**3))
import json, os, subprocess, sys
from pathlib import Path
root=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-runtime-metadata-probe-20261111/native')
for pair in ('A','B'):
 directory=root/pair/f'admission-{pair}-r1'
 command=[sys.executable,'-B','-m','tests.manual.agent_opd.inspect_cache_salt_probe','--pair',pair,'--output-dir',str(directory),'--baseline-dir',str(directory)]
 completed=subprocess.run(command,text=True,capture_output=True,timeout=45,check=False,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 report=json.loads(completed.stdout)
 assert completed.returncode==1 and report['cpu_verdict']=='FAIL' and not report['errors'], (completed.returncode,report['errors'])
 assert report['request_integrity']['status']==report['vector_controls']['status']=='PASS'
 assert len(report['vector_controls']['cases'])==12 and len(report['warm_full_vs_own_cold'])==4
 scope=report['scopes'][0]
 assert scope['chunks']['status']=='PASS' and scope['isolation']['ordinary_joined']==165 and not scope['isolation']['issues']
 assert sum(j['status']=='FAIL' for j in scope['isolation']['joins'])==40
 assert scope['isolation']['declined_returned_rows']==scope['isolation']['non_mamba_begin_rows']==0
 assert all(r['candidate']['status']=='PASS' and r['values_equal'] for r in report['retractions'])
 assert all(r['chunk_tracking_equal'] is True for r in report['chunk_tracking_observations'])
 print(pair,'CLI_EXPECTED_NEGATIVE_PASS','exit',completed.returncode,'CPU',report['cpu_verdict'],'controls12/12 exact; ordinary joins165; isolation FAIL40; chunks169; retractions16 typed zero')
 print(pair,'WARM_FULL_ERRORS',[(r['logical_key'][2],r['comparison']['max_absolute_error'],r['comparison']['max_relative_error'],r['comparison']['relative_error_undefined_count']) for r in report['warm_full_vs_own_cold']])
 if pair=='B':
  negative=next(j for j in scope['isolation']['joins'] if j['sequences']==[13596,13599,13600])
  assert negative['join_status']=='PASS' and negative['status']=='FAIL'
  assert (negative['begin']['protected_len'],negative['returned']['prefix_len'],negative['rebind']['absolute_end'])==(90112,98067,98304)
  tail=next(c for r in scope['chunks']['requests'] for c in r['chunks'] if c['sequence']==16242)
  assert tail['scheduler']['extend_len']==8 and tail['scheduler']['mask'] is False
  print('B_ARCHIVE_NEGATIVE_AND_MASK_FALSE_TAIL_PASS')
print('CPU_ENV',sys.executable,sys.version.split()[0],'CONDA_DEFAULT_ENV',os.environ.get('CONDA_DEFAULT_ENV'))
PY
```

Expected: outer verification exit0; both child CLIs exit1 with CPU FAIL, twelve exact controls,165 ordinary unique joins with40 failed boundaries,169 complete chunks,16 explicit typed zero retractions. Actual: **PASS**, with `A CLI_EXPECTED_NEGATIVE_PASS`, `B CLI_EXPECTED_NEGATIVE_PASS`, and `B_ARCHIVE_NEGATIVE_AND_MASK_FALSE_TAIL_PASS`. No unbound/ambiguous ordinary checkpoint row occurred in either old archive. The B target joins successfully at sequences13596/13599/13600; protected90112, returned98067, end/page-aligned98304; returned-prefix equality alone fails. Sequence16242 remains an8-token mask-false chunk with `NOT_OBSERVED_MASK_FALSE` plan status. A process339 and B process352 each retain raw TP0/DP1 None rank scope.

All errors below are raw logprob errors against own cold-full reference. Zero-reference relative error remains undefined, including exact0 versus0:

| Pair | Sample index | Max absolute error | Max defined relative error | Undefined zero-reference count |
| --- | --- | --- | --- | --- |
| A |1693 |0.0 |0.0 |1 |
| A |1694 |2.3841676011215895e-7 |0.04545451786888886 |1 |
| A |1695 |0.17278575897216797 |0.2727263348137287 |1 |
| A |1696 |0.12412643432617188 |0.6187940669273067 |3 |
| B |1693 |0.0 |0.0 |3 |
| B |1694 |4.529893885774072e-6 |0.31249958276708867 |5 |
| B |1695 |0.43444275856018066 |12.818066557496891 |4 |
| B |1696 |0.4388699531555176 |1.4485754510908142 |4 |

These values reproduce the supplied verified old reports. They are not new counterfactual measurements.

### Syntax, isolated import and whitespace

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import ast,sys
from pathlib import Path
for path in map(Path,['tests/manual/agent_opd/inspect_cache_salt_probe.py','tests/fast/test_cache_salt_probe_inspection.py']):
 text=path.read_text()
 ast.parse(text,filename=str(path))
 compile(text,str(path),'exec')
 assert text.endswith('\n') and all(line==line.rstrip() for line in text.splitlines())
 print('SYNTAX_WHITESPACE_PASS',path,len(text.splitlines()),'lines')
from tests.manual.agent_opd import inspect_cache_salt_probe
assert 'torch' not in sys.modules and 'sglang' not in sys.modules
print('CPU_IMPORT_PASS no torch/sglang import')
PY
```

Expected and actual: exit0; both files parse/compile, newline/trailing whitespace checks PASS, isolated CPU import PASS. `git diff --check --` on the two owned paths also exited0; the explicit text check covers newly untracked files before staging.

## Iterations and limits

- Initial regression run:33 passed, one synthetic two-RID batch test failed because its fixture constructed only one prefix value. Corrected the test fixture to build one CPU prefix/extend entry per native batch RID. The inspector correctly rejected the malformed fixture; native behavior was not changed. Subsequent34/37/39 and final41-test runs pass. Final missing-request/flush injections confirm count shortages remain UNVERIFIED rather than a fabricated successful observation or a known numerical failure.
- The required memory-limited old-archive read first attempted `systemd-run --user --scope -p MemoryMax=30G`, which failed with `Failed to connect to bus: No such file or directory`; non-user scope failed with `Interactive authentication required`. No service/system permission was changed. Final exact CPU reads instead apply process/inherited `RLIMIT_AS=30GiB` and60-second timeout before loading the two bounded archives. This is inspection resource control, not a diagnostic behavior fallback.
- The qualification is responding CPU process/rank only. No global TP/device/physical slots, numerical state, coherence, race, loaded whole-model/source identity or performance proof follows. Baseline qualification comes from the existing reports; the inspector compares existing retained source identities and uses the existing source-fixture identity function, without creating another source-hash protocol.
- New counterfactual output contents, terminal status and controls/isolation/numerical results remain UNVERIFIED. Primary owns termination notification and any follow-up native inspection. Formal04/05 hold and all scientific gates remain unchanged.

## 1. 规划完成情况

**汇总：** PASS3｜SKIPPED1｜TODO1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 指定 inspector 与独立 RID/checkpoint/chunk 绑定 | PASS |165 个旧 archive join 和169 个 chunk；关键负例准确 FAIL。 |
| CPU fault injection 与已有 helper 受影响检查 | PASS |41 新测试、36 已有测试通过。 |
| 限定报告、语法/import/whitespace 交付 | PASS | 本报告与两个文件的实测证据；无额外 source/config 编辑。 |
| 正在运行的新 native 输出检查 | SKIPPED | 用户明确禁止；由 primary 后续通知。 |
| 仅三文件 commit 与返回 | TODO | 验证完成；下一步限定路径提交，不包含并行 parent 编辑。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本 CPU 委派开始至已验证交付｜**当前前沿：** 三文件限定提交与返回

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 此 inspector 正是委派交付；没有通用框架、额外 recorder 或 source-hash 机制。 |
| D2 细节反复重试 | CLEAR | 一次明确的 synthetic batch fixture 修正；没有 native 重试或调参。 |
| D3 支线问题修补 | CLEAR | 仅两个指定代码文件与报告。 |
| D4 可并行任务停滞 | CLEAR | Primary 执行独立 native；本 slice 不等待、不查询且不再委派。 |
| D5 超范围镀金 | CLEAR | 仅 first4/rep0 exact scenario；未加 tolerance、策略或平台功能。 |
| D6 分析空转 | CLEAR | 旧 schema 检查直接产出代码与可复现负例。 |
| D7 路线违背 | CLEAR | 未访问新 native 内容；formal/science/source/config 保持不变。 |

**文档检查：** 此限定 slice 的 S1–S6 均未发现明显缺陷。Parent 状态记录由独立 owner 维护，不据本 CPU PASS 声称新 native 完成。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。
**需停止的偏离行为：** 无。

**接下去的路线：**

1. 仅三个 owned 路径提交并返回 TaskID/API/验证结果 → 完成标志：commit 的 changed-file list 恰好三项。
2. Primary 获得 native termination 通知后再做独立 native inspection → 完成标志：新 run 的 controls/isolation 与四个 warm case 均有真实记录；本 slice 不执行。

## 4. 最值得关注的 3 点

1. 旧 B 关键三方 join 成功后边界 FAIL；没有用待测相等式筛掉负例。
2. 41+36 CPU 检查与两个旧 archive CLI 负例通过；retraction/tracking 差异不是额外 unchanged gate。
3. 新 native、TP/device/coherence/race 与 formal 正确性仍未验证；不得由 CPU 结果提前验收。
