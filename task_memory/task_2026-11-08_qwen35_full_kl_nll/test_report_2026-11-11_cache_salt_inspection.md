## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Implement the CPU-only first4/rep0 inspector; verify synthetic faults and archived A/B negative cases without reading the new native runs. |
| 2026-11-11 | Fix the diagnosed isolation gate scope with RED/GREEN regression; preserve all control FAIL observations and the original A/B FAIL JSON byte-for-byte. |

# Cache-salt probe CPU inspection

TaskID: `profile-cache-salt-native-inspection-20261111`.

## Outcome and ownership

**Follow-up scope fix PASS: 46 inspector regressions and36 affected existing checks pass. All165 native A/B checkpoint joins remain unchanged; each pair's100 full-input joins pass, while three of65 response-control joins remain visibly FAIL. The original A/B FAIL JSON remains unchanged. Primary owns the fresh full-API r2 JSON.** No GPU/auth/platform/SSH operation, new instrumentation, source overlay, configuration change, tolerance or performance claim was made.

Initial preparation at `5da6cfc1` passed41 new regressions,36 affected existing checks and both archived A/B CLI negative expectations before native counterfactual content was authorized. That preparation missed the gate-scoping defect; its original evidence below is retained as history, not a qualification of the new runs.

## Follow-up: full-input gate, shared control observations

[Original Request — follow-up] The primary diagnosed a CPU gate-scoping error: all16 requests were gated by checkpoint geometry even though only eight `full_input` requests receive salts. Join/report all rows and binding integrity; gate counterfactual isolation only on the eight full-input logical identities; preserve unsalted control inequalities as observations. Keep the original `native-inspection-{A,B}.json` immutable. No GPU rerun, new instrumentation, tolerance, math, flags or extra unchanged-chunk gate is authorized. Ownership remains the same three files.

The pre-agreed regression seam is the public `inspect_probe(pair, output_dir, baseline_dir)` API. The already diagnosed cause justified skipping speculative hypotheses and instrumentation. One mixed synthetic native fixture reproduces three shared warm response-control inequalities while every full-input checkpoint remains exact.

Exact RED and GREEN command, run before and after the minimal source change:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/fast/test_cache_salt_probe_inspection.py -k only_full_input_isolation_gates
```

- RED actual: exit1, `1 failed,41 deselected`; eight full-input joins PASS and three response-control joins FAIL were confirmed before `AssertionError: assert 'FAIL' == 'PASS'` on `cpu_verdict`.
- GREEN actual: exit0, `1 passed,41 deselected`; `cpu_verdict=PASS`, full-input coverage8/8 and target PASS, with original aggregate/control statuses still FAIL.
- Final full inspector command from **Focused regressions**: exit0, **46 passed**, comprising the original41 plus the mixed-scope test and four target/control binding fault cases. The existing receiver/comparison command: exit0, **36 passed /115 deselected**. Target inequality still FAIL; duplicate target/control buckets and missing target checkpoint coverage stay UNVERIFIED. The old negative-inequality test, missing retraction checks, response-drift controls and report-only chunk/retraction changes all remain passing.

Implementation is confined to the existing `_checkpoint_isolation` summary and the existing overall status selection. It still joins and reports every ordinary row with the unchanged independent identity buckets/equalities. Public keys under `scopes[i].isolation` now explicitly include:

- `status`, `joins`, `event_counts`, `ordinary_joined`, `nonordinary`, `issues`: unchanged all-request observations, including control FAIL.
- `binding_status`: UNVERIFIED for any missing/ambiguous ordinary binding, including controls.
- `full_input_isolation`: counterfactual gate, eight explicitly bound intended salted full-input RIDs, ordinary joined coverage8/8, unchanged independent boundary checks and failed-join count. The existing salt protocol gate independently verifies sent salts; missing salts never remove a request from target scope.
- `control_observations`: response-only geometric status/counts labeled observational, not a counterfactual gate. Every individual failed join remains in `joins`; no FAIL is rewritten to PASS.

Overall `cpu_verdict` now uses target isolation and all existing source/protocol/vector/RID/chunk/retraction/binding integrity gates, not unsalted control geometry. No equality, matching rule, native behavior, comparison definition or unchanged-chunk acceptance gate changed.

### Authorized read-only native scope regression and immutable originals

These exact files remain the primary's original FAIL evidence:

| Pair | Immutable path | SHA256 before and after |
| --- | --- | --- |
| A | `evidence/teacher-scoring-cache-salt-probe-20261111/native-inspection-A.json` | `cc76e426ab3ad838a4fb460420de39f7815ac03f18f06470354c9ba5ff672730` |
| B | `evidence/teacher-scoring-cache-salt-probe-20261111/native-inspection-B.json` | `2bcc0ab925b627d957374942e8ac1c3500919a880c7d27ab6f6e20df26468a33` |

The following focused CPU replay reads the authorized runtime rows, compares every original isolation output field against the preserved JSON, and checks only the repaired scope. It does not run the full actual API or write an r2 artifact; that remains the primary's follow-up.

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import resource
resource.setrlimit(resource.RLIMIT_AS,(30*1024**3,30*1024**3))
import hashlib,json
from pathlib import Path
from tests.manual.agent_opd import inspect_cache_salt_probe as p
root=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-cache-salt-probe-20261111')
expected={'A':'cc76e426ab3ad838a4fb460420de39f7815ac03f18f06470354c9ba5ff672730','B':'2bcc0ab925b627d957374942e8ac1c3500919a880c7d27ab6f6e20df26468a33'}
normalize=lambda value:json.loads(json.dumps(value))
for pair in ('A','B'):
 path=root/f'native-inspection-{pair}.json'
 before=path.read_bytes(); report=json.loads(before)
 assert hashlib.sha256(before).hexdigest()==expected[pair] and report['cpu_verdict']=='FAIL'
 by_rid={(r['pair'],r['native_rid']):tuple(r['logical_key']) for r in report['rid_joins']}
 runtime=p._read(Path(report['output_dir'])/'runtime_metadata.json')
 observations=p._runtime_metadata_states(runtime['server_info'])
 for state,scope in zip(runtime['server_info']['internal_states'],report['scopes']):
  actual=p._checkpoint_isolation(state['mamba_runtime_metadata']['rows'],by_rid,pair)
  old=scope['isolation']
  assert {name:normalize(actual[name]) for name in old}==old
  target,controls=actual['full_input_isolation'],actual['control_observations']
  assert actual['status']=='FAIL' and actual['binding_status']=='PASS' and actual['ordinary_joined']==165
  assert target['status']==target['coverage_status']=='PASS'
  assert (target['ordinary_joined'],target['failed_joins'],target['target_rid_count'],target['covered_rid_count'])==(100,0,8,8)
  assert controls['status']=='FAIL' and (controls['ordinary_joined'],controls['failed_joins'])==(65,3)
  print(pair,'FOCUSED_NATIVE_SCOPE_PASS','joins165 unchanged; full100 PASS/0 FAIL, RID8/8; controls62 PASS/3 FAIL retained; binding PASS')
 assert report['vector_controls']['status']=='PASS' and len(report['vector_controls']['cases'])==12
 assert all(r['comparison']['values_exact'] for r in report['warm_full_vs_own_cold'])
 assert path.read_bytes()==before
 print(pair,'ORIGINAL_FAIL_JSON_PRESERVED',str(path),expected[pair])
old_dir=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1')
requests=p._lines(old_dir/'requests.jsonl')
by_rid={(r['pair'],r['native_request_id']):p._key(r) for r in requests}
rows=p._read(old_dir/'runtime_metadata.json')['server_info']['internal_states'][0]['mamba_runtime_metadata']['rows']
isolation=p._checkpoint_isolation(rows,by_rid,'B')
negative=next(j for j in isolation['joins'] if j['sequences']==[13596,13599,13600])
assert isolation['status']=='FAIL' and negative['join_status']=='PASS' and negative['status']=='FAIL'
assert (negative['begin']['protected_len'],negative['returned']['prefix_len'],negative['rebind']['absolute_end'])==(90112,98067,98304)
print('OLD_B_BOUND_NEGATIVE_RETAINED_PASS','13596/13599/13600; 90112 != 98067; end98304')
PY
```

Expected/actual: outer exit0, both `FOCUSED_NATIVE_SCOPE_PASS` and `ORIGINAL_FAIL_JSON_PRESERVED`; all165 joins per pair and every legacy isolation field identical to the original. Full-input100 PASS/0 FAIL, response-only62 PASS/3 FAIL, target RIDs8/8 and binding PASS. `OLD_B_BOUND_NEGATIVE_RETAINED_PASS` confirms the old13596/13599/13600 join still succeeds and fails the protected-prefix equality honestly. Checksums here preserve requested evidence, not source qualification or a new source-hash mechanism. Syntax/isolated CPU import and scoped `git diff --check` also exit0.

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

For its r2 rerun, the primary can use the following command with the exact terminated run and same-pair verified baseline directories. This example is **not an executed full actual API command in this subagent**:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.inspect_cache_salt_probe \
  --pair B --output-dir "$TERMINATED_COUNTERFACTUAL_DIR" --baseline-dir "$VERIFIED_SAME_PAIR_BASELINE_DIR"
```

The CLI emits strict JSON to stdout and returns0 only for CPU controls/full-input isolation/evidence qualification; otherwise it returns1. Native completion is a separate result-receipt observation, not a platform/container terminal assertion. A CPU PASS is not numerical warm acceptance: each of the four `warm_full_vs_own_cold` comparisons must be interpreted separately. Missing/ambiguous evidence stays UNVERIFIED; observed failed equalities stay FAIL, including control observations outside the target gate.

Report fields retain:

- Six-part logical identity `(pair, source_uid, sample_index, repetition, phase, mode)` explicitly mapped from native RID. Successful16 request/response/vector identities bind to the fixed source token tails; no sequence or count creates an RID association.
- Eight full-input salts equal to `pair + ':' + pre-send request_id`, eight response-only null-salt receipts, and the exact10 flush identities/statuses. Twelve controls compare eight response vectors and four cold-full vectors against the verified baseline using existing `_comparison`.
- Four warm-full comparisons against their own run's cold-full only, including exactness, maximum absolute/defined relative error and undefined-zero-reference count. There is no new tolerance or full-vs-response gate.
- Actual typed `request.meta_info.num_retractions`; missing/null/bool/string/negative/noninteger values remain unverified. Retraction and initial/complete chunk/tracking differences are observations, not an extra unchanged gate.
- Each responding process/rank scope validated through existing `_runtime_metadata_states`; raw DP1 `dp_rank=None` is retained. Begin/rebind buckets use unique `(rid,page_aligned_len)`; returned/rebind buckets use unique `(rid,node_id,prefix_len,mamba_exist)`. Bind first, then test returned prefix/protected, rebind start/protected, and rebind end/page-aligned independently. All ordinary rows must be used exactly once; only the eight full-input targets gate isolation, while shared unsalted control inequalities remain observations. Declined/non-Mamba observations retain scope and counts without manufactured matching.
- Scheduler chunks keyed by `(rid,prefix_len,extend_len,seq_end)`, validated sum and contiguous token-position coverage. Plan batch row `i` binds through `rids[i]` and its CPU prefix/extend; native masks, track lengths, grids, chunk indices and logical batch context remain in the report. `h_src[k]` is retained as a flattened source index for `h_rows[k]`, never a request-chunk index. Identical normalized plan observations on a unique chunk deduplicate; conflicting plans remain unverified. Mask-false chunks remain present. Per-layer allocation/store counts are observations, not chunks. Tensor object addresses are not join or comparison identities.

## Environment and commands

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`.

CPU executable `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, pytest9.1.1; `CONDA_DEFAULT_ENV` unset. Final pytest temporary files use the approved local `TMPDIR`; bytecode and pytest result-cache writes are disabled. Isolated inspector import loads neither `torch` nor `sglang`.

### Focused regressions (initial preparation; commands reused for follow-up)

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/fast/test_cache_salt_probe_inspection.py
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/fast/test_teacher_scoring_probe.py -k 'comparison_reports or metadata_single_dp or metadata_dp_rank or metadata_other_rank or metadata_dp_responses or runtime_metadata_malformed_payload'
```

Expected: all selected tests pass, qualified synthetic controls with original response-only warm drift pass, valid-bound negative inequalities FAIL, ambiguity/missing evidence UNVERIFIED, changed observed retractions/tracking do not introduce an unchanged gate. Actual: **41 passed** and **36 passed /115 deselected**, respectively; both exit0. Each run has two existing SwigPy deprecation warnings. The new file fits the implicit fast CPU registration; no CI registry or shared GPU runner was changed.

### Archived A/B CLI negative regressions (initial preparation)

In the initial preparation these were the only native business outputs read. A/B each use their own old directory as both run and baseline deliberately: vector controls must be exact, but the absent full salts and actual cross-request isolation failures must remain negative. This historical check does not simulate a successful native salt intervention; the separately authorized follow-up replay above reads the counterfactual runtime rows.

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
- Initial preparation did not inspect new counterfactual content. The follow-up now verifies the authorized native checkpoint scope only and preserves the primary's original FAIL JSON; the primary's full actual API r2 verdict is still pending. Formal04/05 hold and all scientific gates remain unchanged.

## 1. 规划完成情况

**汇总：** PASS3｜SKIPPED1｜TODO1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| RED/GREEN 修正 full-input gate scope | PASS | 混合 full PASS/control FAIL 从错误整体 FAIL 到正确 target PASS；control FAIL 保留。 |
| CPU 回归与只读 native scope 复验 | PASS |46+36 检查通过；A/B165 joins 与原始字段不变；旧 B 负例仍 FAIL。 |
| 限定报告、语法/import/whitespace 交付 | PASS | 原始 FAIL JSON 字节保持；无额外 source/config 编辑。 |
| Full actual API r2 输出 | SKIPPED | Primary 明确拥有后续重跑与新 JSON；本 slice 不写。 |
| 仅三文件 commit 与返回 | TODO | 验证完成；下一步限定路径提交，不包含并行 parent 编辑。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** gate-scoping follow-up 开始至已验证交付｜**当前前沿：** 三文件限定提交与返回

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅既有函数内 scope 摘要与验收回归；无平行 validator/框架。 |
| D2 细节反复重试 | CLEAR | 单一已诊断原因的 RED→GREEN；无 GPU 重跑或调参。 |
| D3 支线问题修补 | CLEAR | 仅两个指定代码文件与报告。 |
| D4 可并行任务停滞 | CLEAR | Primary owns r2/evidence；本 slice 独立完成修复、不再委派。 |
| D5 超范围镀金 | CLEAR | 仅 first4/rep0 exact scenario；未加 tolerance、策略或平台功能。 |
| D6 分析空转 | CLEAR | 明确混合请求回归直接产出最小修复与原始字段复验。 |
| D7 路线违背 | CLEAR | 按最新授权只读 native scope；原始 FAIL 与 full equations/science 保持不变。 |

**文档检查：** 此限定 slice 以最新 explicit follow-up 为准，S1–S6 均未发现影响执行的缺陷。Parent 的较早 phase snapshots 由其独立 owner 更新，不据本 CPU 修复声称 r2 或 formal 完成。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。
**需停止的偏离行为：** 无。

**接下去的路线：**

1. 仅三个 owned 路径提交并返回 TaskID/API/验证结果 → 完成标志：commit 的 changed-file list 恰好三项。
2. Primary 重新运行实际 API 并写新 r2 JSON → 完成标志：overall uses full-input gate、control FAIL 保留且 original FAIL JSON 不变；本 slice 不写。

## 4. 最值得关注的 3 点

1. target100/100 PASS 与 control62/65 PASS 在同一165-row observation 中区分；三个 control FAIL 没有擦除。
2. 46+36 CPU 检查、target failure/ambiguity/coverage 和旧 B 负例通过；原始 A/B FAIL JSON 不变。
3. Primary full-API r2 仍待执行；TP/device/coherence/race 与 formal 正确性不能由 scope 修复提前验收。
