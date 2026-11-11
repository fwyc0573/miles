## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record primary acceptance of the scoped numerical audit after reading both artifacts and checking all20 retained metric rows,40 FP32 extrema and totals against the small result receipt; causal and formal conclusions remain unaccepted. |
| 2026-11-11 | Interpret only retained B r3 compact FULL K/V metrics after consuming primary-accepted scoped prerequisites at281e70f7; preserve warm failure and formal holds. |

# B r3 compact FULL K/V numerical results

TaskID: `profile-kv-coherence-native-B-r3-numeric-20261111`.

## Result and scope

**Focused numerical audit PRIMARY ACCEPTED. Measured local FULL K/V exact equality FAIL:20/20 rows are nonexact,22,514,691/40,729,600 element pairs differ.** This supports adopted candidate1 only for the measured warm TP0/7955-row window. Maximum absolute error is16.3125 at global layer27/K,token95012/local head0/dimension70,OLD12.3125 versus FRESH−4. Maximum OLD-reference relative error is5,111,807 at layer15/V,token95114/head0/dimension181,OLD`2.9802322387695312e-08` versus FRESH0.15234375. All20 rows report zero OLD/FRESH nonfinite and zero OLD-zero relative-undefined counts. The latter is an observed zero count, not a redefinition of relative error at OLD0. Original warm1/4 **FAIL**, formal04/05 **HOLD** and all causal/TP limits remain. No accepted gate is reopened; routine shared-record reconciliation remains independently owned and is not an additional approval or serial gate.

Let `T=task_memory/task_2026-11-08_qwen35_full_kl_nll`, `D=T/evidence/teacher-scoring-kv-coherence-probe-20261111`, and `B=D/native/B/admission-B-r3`. Machine evidence: [numeric-verification-B-r3.json](evidence/teacher-scoring-kv-coherence-probe-20261111/numeric-verification-B-r3.json).

Consumed authority: the three **committed** qualification artifacts at `281e70f7f691a42ea90dc9b27382cd3ca77bcd4f` are `D/physical-index-verification-r3.json`, `T/test_report_2026-11-11_kv_coherence_r3_physical_indices.md`, and `T/test_report_2026-11-11_kv_coherence_r3_submission.md`. They record `complete_numeric_measurement_prerequisites=PRIMARY_ACCEPTED_SCOPED` and original producer/lifetime/F→S `PASS_SOURCE_BACKED`; A/B bounded controls were already primary accepted at `4da5c3eb`. The accepted B controls are `D/native-verification-B-r3.json` and `T/test_report_2026-11-11_kv_coherence_native_B_r3_results.md`. Their historical physical/numeric-pending labels describe their earlier scope and do not reset the later primary acceptance. No baseline/source/build/CPU/native/control verification was rerun.

Selection: job `exp-1111-194636-897299`, responding PID350/TP0, sample1695/position2/repetition0, source UID `00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6:5:127`, mode `full_input`, input98942, logprob start0. Warm RID `ab9c724339da47169960dcd488c647cd` and cold RID `011d6bcddb7140a38a4667cbcb0fbf30` are joined to retained request identities, not selected by bank order. Warm P90112/E98304/Q98067 gives OLD `[90112,98067)`,7955 rows;237 suffix rows `[98067,98304)` are **not** in these metrics.

Actual topology is `TokenToKVPoolAllocator`, page1, `HybridLinearKVPool` root and `MHATokenToKVPool` writer, capacity2752780; each K/V backing is BF16 CUDA0 `[2752781,1,256]`, stride `[256,256,1]`. FULL global layers are `[3,7,11,15,19,23,27,31,35,39]`, dense mapping0–9. Each layer/side compares7955×1×256=**2,036,480 elements**;10 layers×2 sides gives20 rows/**40,729,600 element pairs**, not40,729,600 physical token rows or all four TP ranks. Each side spans20,364,800 element pairs.

## Metric definition and retained-copy limits

The accepted installed `B/kv_coherence_source_preflight/after/srt/kv_coherence.py:311–344` defines `a=OLD[:n].cpu().float()`, `b=FRESH[:n].cpu().float()`: BF16 payloads expanded to FP32, `mismatch_count=sum(a!=b)`, `values_exact=all finite && torch.equal(a,b)`, absolute error `abs(a-b)` over jointly finite pairs, and relative error `abs(a-b)/abs(OLD)` only over jointly finite, **nonzero OLD** references. OLD zero references have undefined relative error, including zero/zero; no epsilon or new tolerance. OLD/FRESH nonfinite counts are separate. An absolute or relative extremum retains global token, local head, dimension, OLD and FRESH; masked flattened argmax chooses one source extremum, not proof of unique maximum or earliest divergence.

The local scalar check rounds subtraction and relative division separately with `struct.pack/unpack('<f')` to match those FP32 source operations. It checks exact serialized extremum consistency, not approximate equality or an independently reproduced array reduction. Source-backed mismatch counts/maxima cannot be independently recomputed from raw arrays: compact drain discarded payload/indices (`:392–394`), and raw K/V archives were deliberately not retained. No raw replay is invented or requested.

The three compared projections are `result.json -> kv_coherence.summaries[0]`, raw `runtime_metadata.json -> server_info.internal_states[0].kv_coherence`, and normalized `runtime_metadata.json -> kv_coherence[0]`. They are **three copies of the same RPC readback**, not independent captures or measurements. Exact full metric-row objects (including all extrema) plus RID/window/shape/status are compared. Legacy `numeric_acceptance=null` and producer interpretation strings remain untouched in the raw files; later independent acceptance and interpretation are recorded only here.

Cold Q=P90112 and n0 makes `_metrics` return `None`; absent cold OLD is not zero equality. Optional cold-FRESH versus warm-FRESH payloads are not retained: **SKIP**, no code or new run. The compared FRESH is the immediate post-store full8192 capture restricted to the first7955 OLD positions, not the237 suffix or a cross-cold-run comparison.

## Accepted ordering and interpretation limits

The accepted B scalars remain **F531885904 ≠ S532178656**. Existing scheduler `S.wait_stream(F)` covers the **whole forward before the next-loop chunk stash**, including immediate all-layer FRESH gathers; original inline index producers/OLD gathers are on S, and later F waits S before slot reuse. This consumes the `281e70f7` source-backed chain, not stream-scalar equality, newly measured events, a per-kernel completion receipt or universal race proof. Successful captured drain plus the accepted unchanged all-layer source gate closes FRESH coverage even though serialized banks omit `fresh_layers`. Nothing is reopened for that intentional omission.

Numerical nonzero results can support only adopted **candidate1: local FULL K/V difference in this measured warm window/TP0**. They do not establish invalid SSM, warm-score cause, earliest divergence, allTP, an arbitrary race, a fix, performance causality or formal readiness. If equal, they would only narrow candidate1 for this scope. Original cold4/4 and **warm1/4 FAIL** are consumed unchanged, not rerun. Formal04/05 remain **HOLD**;06 still requires each independent200-update attempt, and B does not wait for A200. No SSM/performance causal interpretation is performed.

## Exact focused audit command and environment

Workspace `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`; local `/usr/bin/python3`3.10.6, Linux5.10.25-nvidia-gpu/glibc2.35, no conda activation. Retained worker environment, **not executed locally**: `/opt/sglang/bin/python3`3.12.16, Torch2.14.1+cu130, SGLang0.5.24.dev80+g056f871. All focused JSON/source reads use60-second timeouts and a30-GiB address-space ceiling. Only stdlib parsing, scalar FP32 checks and aggregation of20 serialized rows occur; no runtime/native imports, fixtures, suites, hashes, API/auth/SSH/GPU/capture/code/delegation/staging/commit or old/shared-document edits.

The command prints the new JSON content without writing any files. It consumes closed gates, checks actual retained metric projections, schema/geometry/bounds and scalar extrema, then derives scoped aggregates/maxima. Artifact formatting is checked separately without rereading the43.5-MB runtime archive. No generalized harness or new context gate is introduced.

<!-- numeric-audit-command -->
```bash
timeout 60s env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
import json, math, platform, resource, struct, subprocess
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
T = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
D = T / 'evidence/teacher-scoring-kv-coherence-probe-20261111'
B = D / 'native/B/admission-B-r3'
C = '281e70f7f691a42ea90dc9b27382cd3ca77bcd4f'
def committed(path):
    return subprocess.check_output(['git', 'show', C + ':' + str(path)], text=True, timeout=30)
Q = json.loads(committed(D / 'physical-index-verification-r3.json'))
assert Q['complete_numeric_measurement_prerequisites'] == 'PRIMARY_ACCEPTED_SCOPED'
assert Q['original_producer_lifetime_F_to_S_readiness'] == 'PASS_SOURCE_BACKED'
assert Q['dependency_qualification']['status'] == 'PASS_SOURCE_BACKED'
assert Q['primary_acceptance']['A_and_B_control_archive'] == '4da5c3eb'
for name in ('test_report_2026-11-11_kv_coherence_r3_physical_indices.md',
             'test_report_2026-11-11_kv_coherence_r3_submission.md'):
    assert 'PRIMARY ACCEPTED' in committed(T / name)
controls = json.loads((D / 'native-verification-B-r3.json').read_text())
assert controls['primary_acceptance']['status'] == 'ACCEPTED_BOUNDED_STAGE'
assert controls['verdicts']['warm_correctness'] == 'FAIL'
assert controls['controls']['agreement']['warm_stream'] == 1
assert (controls['CPP']['native_Torch_F'], controls['observer']['Torch_S']) == (531885904, 532178656)
R = json.loads((B / 'result.json').read_text())
M = json.loads((B / 'runtime_metadata.json').read_text())
S = R['kv_coherence']['summaries'][0]
raw = M['server_info']['internal_states'][0]['kv_coherence']
normalized = M['kv_coherence'][0]
def projection(c):
    return {'process_id': c['process_id'], 'status': c['status'], 'coverage': c['coverage'],
            'topology': c['topology'],
            'banks': [{'rid': b['rid'], 'status': b['status'], 'P': b['insert']['P'],
                       'E': b['insert']['E'], 'Q': b['rebind']['Q'], 'metrics': b['metrics']}
                      for b in c['banks']]}
assert projection(S) == projection(raw) == projection(normalized)
assert (S['process_id'], S['status']) == (350, 'captured')
assert len(S['banks']) == 2
banks = {b['rid']: b for b in S['banks']}
warm_rid, cold_rid = 'ab9c724339da47169960dcd488c647cd', '011d6bcddb7140a38a4667cbcb0fbf30'
W, cold = banks[warm_rid], banks[cold_rid]
requests = [json.loads(line) for line in (B / 'requests.jsonl').read_text().splitlines() if line]
identities = []
for phase, rid in (('cold', cold_rid), ('warm_stream', warm_rid)):
    matches = [a for a in requests if a['native_request_id'] == rid]
    assert len(matches) == 1
    a = matches[0]
    assert (a['pair'], a['phase'], a['mode'], a['sample_index'], a['sample_position'],
            a['repetition'], a['input_count'], a['logprob_start_len']) == ('B', phase, 'full_input', 1695, 2, 0, 98942, 0)
    assert a['source_uid'] == '00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6:5:127'
    assert a['meta_info']['id'] == rid
    assert {k: a[k] for k in ('pair', 'phase', 'mode', 'source_uid', 'sample_index', 'repetition')} == banks[rid]['logical_case']
    identities.append({'phase': phase, 'rid': rid, 'source_uid': a['source_uid'],
                       'sample_index': 1695, 'sample_position': 2, 'repetition': 0,
                       'mode': 'full_input', 'input_count': 98942, 'logprob_start_len': 0})
P, E, end = W['insert']['P'], W['insert']['E'], W['rebind']['Q']
assert (P, E, end) == (90112, 98304, 98067)
assert cold['rebind']['Q'] == cold['insert']['P'] == P and cold['metrics'] is None
n, suffix = end - P, E - end
top = S['topology']; layers = [x['layer_id'] for x in top['buffers']]
assert layers == list(range(3, 40, 4)) and top['mapping'] == [[v, i] for i, v in enumerate(layers)]
assert (top['allocator_class'], top['root_class'], top['writer_class'], top['page_size'], top['capacity']) == ('TokenToKVPoolAllocator', 'HybridLinearKVPool', 'MHATokenToKVPool', 1, 2752780)
shapes = []
for b in top['buffers']:
    for side in ('K', 'V'):
        d = b[side]
        assert d['shape'] == [2752781, 1, 256] and d['stride'] == [256, 256, 1]
        assert (d['dtype'], d['device']) == ('torch.bfloat16', 'cuda:0')
        shapes.append(tuple(d['shape'][1:]))
assert len(set(shapes)) == 1
heads, dim = shapes[0]; size = n * heads * dim
assert (n, suffix, heads, dim, size) == (7955, 237, 1, 256, 2036480)
source = (B / 'kv_coherence_source_preflight/after/srt/kv_coherence.py').read_text()
source = source.split('    def _metrics(self, bank):', 1)[1].split('    def drain(self, requested):', 1)[0]
for text in ('a, b = reference[:n].cpu().float(), candidate[:n].cpu().float()',
             'mismatch = a != b', 'relative_mask = finite & (a != 0)',
             'relative = errors[relative_mask] / a[relative_mask].abs()',
             '"OLD": float(a.flatten()[position])', '"FRESH": float(b.flatten()[position])'):
    assert text in source
f32 = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
rows = W['metrics']; assert len(rows) == 20
assert [(r['layer_id'], r['side']) for r in rows] == [(layer, side) for layer in layers for side in ('K', 'V')]
counts = ('mismatch_count', 'relative_error_undefined_count', 'old_nonfinite_count', 'fresh_nonfinite_count')
keys = {'layer_id', 'side', 'old_rows', 'values_exact', *counts,
        'max_absolute_error', 'max_relative_error', 'absolute_extremum', 'relative_extremum'}
scope = 'B-r3:PID350:TP0:ab9c724339da47169960dcd488c647cd:P90112:Q98067:E98304'
out_rows = []
for index, row in enumerate(rows):
    assert set(row) == keys
    assert type(row['layer_id']) is int and type(row['old_rows']) is int and row['old_rows'] == n
    assert type(row['side']) is str and type(row['values_exact']) is bool
    for k in counts:
        assert type(row[k]) is int and 0 <= row[k] <= size
    for k in ('max_absolute_error', 'max_relative_error'):
        assert type(row[k]) is float and math.isfinite(row[k]) and row[k] >= 0 and f32(row[k]) == row[k]
    assert row['old_nonfinite_count'] == row['fresh_nonfinite_count'] == 0
    assert row['relative_error_undefined_count'] == 0
    assert row['values_exact'] == (row['mismatch_count'] == 0)
    assert (row['max_absolute_error'] > 0) == (row['mismatch_count'] > 0)
    assert row['values_exact'] is False and row['mismatch_count'] > 0
    for label in ('absolute', 'relative'):
        x = row[label + '_extremum']
        assert set(x) == {'token', 'head', 'dimension', 'OLD', 'FRESH'}
        assert all(type(x[k]) is int for k in ('token', 'head', 'dimension'))
        assert P <= x['token'] < end and 0 <= x['head'] < heads and 0 <= x['dimension'] < dim
        assert all(type(x[k]) is float and math.isfinite(x[k]) and f32(x[k]) == x[k] for k in ('OLD', 'FRESH'))
        error = abs(f32(x['OLD'] - x['FRESH']))
        if label == 'relative':
            assert x['OLD'] != 0
            error = f32(error / abs(x['OLD']))
        assert error == row['max_' + label + '_error'], (index, label, error)
    out_rows.append({'scope_id': scope + ':L' + str(row['layer_id']) + ':' + row['side'],
                     'element_pairs': size, **row, 'sanity': 'PASS', 'FP32_extremum_consistency': 'PASS'})
def aggregate(selected):
    return {'metric_rows': len(selected), 'element_pairs': size * len(selected),
            'exact_rows': sum(r['values_exact'] for r in selected),
            'nonexact_rows': sum(not r['values_exact'] for r in selected),
            **{k: sum(r[k] for r in selected) for k in counts},
            'max_absolute_error': max(r['max_absolute_error'] for r in selected),
            'max_relative_error': max(r['max_relative_error'] for r in selected)}
maxima = {}
for label in ('absolute', 'relative'):
    field = 'max_' + label + '_error'; maximum = max(r[field] for r in rows)
    maxima[label] = {'value': maximum, 'scope_ids': [r['scope_id'] for r in out_rows if r[field] == maximum],
                     'locations': [{'layer_id': r['layer_id'], 'side': r['side'], **r[label + '_extremum']}
                                   for r in rows if r[field] == maximum]}
output = {'schema': 'kv-coherence-B-r3-compact-numeric-v1',
          'task_id': 'profile-kv-coherence-native-B-r3-numeric-20261111',
          'modification_history': [{'date': '2026-11-11', 'change': 'Interpret retained B r3 compact metrics under primary-accepted scoped prerequisites; no new capture or reopened gates.'}],
          'run': str(B), 'job': controls['job'], 'scope_id': scope,
          'prerequisites': {'commit': C, 'status': Q['complete_numeric_measurement_prerequisites'],
                            'producer_lifetime_F_to_S': 'PASS_SOURCE_BACKED', 'controls_archive': '4da5c3eb',
                            'consumed_not_rerun': True},
          'environment': {'workspace': str(Path.cwd()), 'local_python': platform.python_version(),
                          'local_executable': '/usr/bin/python3', 'kernel': platform.release(),
                          'worker_python': controls['runtime']['worker_python'], 'torch': controls['runtime']['torch'],
                          'sglang': controls['runtime']['sglang'], 'timeout_seconds': 60, 'address_space_limit_GiB': 30,
                          'execution': 'stdlib JSON/text parsing and20-row aggregation/scalar FP32 checks only'},
          'identities': identities,
          'topology': {'process_id': 350, 'TP_rank': 0, 'FULL_layers': layers, 'mapping': top['mapping'],
                       'allocator_class': top['allocator_class'], 'root_class': top['root_class'],
                       'writer_class': top['writer_class'], 'capacity': top['capacity'], 'page_size': 1,
                       'each_K_V_shape': [2752781, heads, dim], 'stride': [256, 256, 1],
                       'dtype': 'torch.bfloat16', 'device': 'cuda:0', 'comparison_arithmetic': 'FP32'},
          'window': {'P': P, 'E': E, 'warm_Q': end, 'old_rows': n, 'excluded_suffix_rows': suffix,
                     'element_pairs_per_metric_row': size, 'total_metric_rows': len(rows),
                     'total_element_pairs': size * len(rows)},
          'copy_projection': {'status': 'PASS_EXACT',
                              'copies': ['result.json#/kv_coherence/summaries/0',
                                         'runtime_metadata.json#/server_info/internal_states/0/kv_coherence',
                                         'runtime_metadata.json#/kv_coherence/0'],
                              'independent_measurements': 1, 'metric_row_objects_identical': True,
                              'scope': 'PID/status/coverage/topology and both RID/P/E/Q/status/full-metric objects; three copies of one RPC'},
          'ordering': {'F': 531885904, 'S': 532178656, 'F_equals_S': False,
                       'status': 'CONSUMED_PRIMARY_ACCEPTED_SOURCE_BACKED',
                       'basis': 'Existing S.wait(F) whole-forward before next-loop chunk stash; original index producers/OLD gathers on S; later F.wait(S) before reuse; no scalar readiness proof/new events'},
          'metric_reference': {'candidate': 'FRESH', 'reference': 'OLD', 'relative_denominator': 'abs(OLD)',
                               'zero_reference': 'UNDEFINED including zero/zero; no epsilon/tolerance',
                               'nonfinite_domain': 'Absolute/relative maxima use jointly finite pairs; relative excludes OLD0',
                               'source': str(B / 'kv_coherence_source_preflight/after/srt/kv_coherence.py') + ':311-344',
                               'FP32_consistency': 'Exact struct float32 subtraction then division for each serialized extremum; not raw-array reduction replay'},
          'rows': out_rows, 'aggregates': {'all': aggregate(rows), 'K': aggregate([r for r in rows if r['side'] == 'K']),
                                         'V': aggregate([r for r in rows if r['side'] == 'V'])}, 'maxima': maxima,
          'checks': {'closed_prerequisites_consumed': 'PASS', 'metric_projection_unchanged': 'PASS',
                     'identity_topology_window': 'PASS', 'all20_schema_types_count_bounds_finiteness': 'PASS',
                     'all40_extremum_coordinates_and_FP32_scalar_consistency': 'PASS',
                     'measured_local_FULL_KV_values_exact': 'FAIL;20/20 nonexact rows',
                     'raw_array_counts_maxima_independent_replay': 'NOT_CLAIMED; raw payload archives deliberately absent',
                     'cold_OLD_equality': 'NOT_APPLICABLE; n0 metrics=None, not zero equality',
                     'optional_cold_FRESH_vs_warm_FRESH': 'SKIP; payloads not retained, no new run/code',
                     'warm_correctness': 'FAIL unchanged;1/4 agreement', 'formal04_05': 'HOLD'},
          'interpretation': {'candidate1': 'SUPPORTED_LOCAL_FULL_KV_DIFFERENCE',
                             'scope': 'Only measured responding TP0 warm RID and7955 OLD rows across10 FULL layers/K/V',
                             'not_established': ['invalid SSM', 'warm-score cause', 'earliest divergence', 'allTP',
                                                 'universal race absence', 'fix', 'performance causality', 'formal readiness'],
                             'formal_dependency': '06 needs each independent200-update attempt; B does not wait A200'},
          'verification_limit': 'Source-backed serialized reductions with exact same-RPC copy equality and scalar extrema consistency; no raw-array counts/maxima replay, new tolerance, raw hash/paired GPU/event/mappedELF/buildID/allTP/context gate',
          'prohibited_actions_performed': []}
print(json.dumps(output, ensure_ascii=True, separators=(',', ':'), allow_nan=False))
PY
```

## Observed check results

| Check | Expected / passing condition | Actual | Disposition |
| --- | --- | --- | --- |
| Original scoped prerequisites | Primary281e committed acceptance; producer/lifetime/F→S PASS_SOURCE_BACKED; A/B controls4da accepted | Consumed exactly; no original gate rerun | PASS, consumed |
| Actual raw/normalized/result metric projection | Both RID/window/topology/status/full metric objects equal | Three projections exactly equal | PASS; one RPC, not three measurements |
| Selection/topology/geometry | Exact warm/cold RID and sample identity; actual10 FULL layers/local1×256/BF16;7955+237 window | All checks match;2,036,480 elements per row,40,729,600 pairs total | PASS |
| Every row's schema/types/count bounds/finiteness |20 expected unique layer/side rows; exact boolean/int/float types; counts0…2,036,480; finite nonnegative maxima |20/20 PASS; OLD/FRESH nonfinite0; OLD-zero undefined0 | PASS, serialized metrics |
| Every retained extremum |40 coordinate/value objects within warm token/local-head/dimension bounds; exact source FP32 difference/ratio |40/40 PASS without epsilon/tolerance | PASS, scalar sanity only |
| Measured local K/V exact equality | For equality, all20 `values_exact=true`,mismatch0,maxabs0 | All20 false;22,514,691 mismatches,maxabs16.3125 | **FAIL equality**; valid observation, supports local candidate1 |
| Independent raw-array reduction replay | Not required by compact-only original scope | Raw arrays intentionally absent; no counts/maxima recomputation from arrays | NOT_CLAIMED, not added gate |
| Cold OLD payload/equality | n0 must produce `metrics=None` | Cold metrics null in all copies | PASS absent-OLD contract; equality NOT_APPLICABLE |
| Optional cold-FRESH versus warm-FRESH | Optional only if payloads retained | Payload pair not retained | SKIP, no new run/code |
| Existing warm correctness/formal | Preserve accepted earlier outcome and dependencies | Cold4/4,warm1/4 FAIL;04/05 HOLD;06 each own200,B not A200 | Unchanged, no cause/fix/formal acceptance |

All20 metric rows have OLD7955,`values_exact=false`,relative-undefined0,OLD-nonfinite0 and FRESH-nonfinite0. The JSON preserves each row's exact values, both complete extrema, coordinate scope ID and scalar-check result. Values below are serialized FP32 reductions, not independently replayed maxima.

| Global FULL layer / side | Mismatch elements /2,036,480 | Max absolute | Max relative /abs(OLD) | Schema/extrema sanity |
| --- | --- | --- | --- | --- |
|3/K|856333|0.359375|253220.953125|PASS|
|3/V|882940|0.25390625|27437.265625|PASS|
|7/K|1078084|0.62109375|23129.353515625|PASS|
|7/V|1124126|0.25390625|74471.7265625|PASS|
|11/K|1124807|5.5078125|35723.51171875|PASS|
|11/V|1135623|1.20703125|78221.390625|PASS|
|15/K|1149004|8.078125|755496.75|PASS|
|15/V|1164826|1.3046875|5111807.0|PASS|
|19/K|1163316|11.4140625|97035.734375|PASS|
|19/V|1172931|8.609375|47691.515625|PASS|
|23/K|1166565|15.3125|153940.890625|PASS|
|23/V|1171164|11.8740234375|952154.1875|PASS|
|27/K|1169678|16.3125|239257.40625|PASS|
|27/V|1180020|11.7734375|629144.5625|PASS|
|31/K|1168655|11.25|86529.0|PASS|
|31/V|1176534|14.78125|334411.71875|PASS|
|35/K|1162293|12.0|110682.0234375|PASS|
|35/V|1180984|9.453125|571098.4375|PASS|
|39/K|1166948|14.21875|399372.75|PASS|
|39/V|1119860|8.236328125|236658.78125|PASS|

| Aggregate | Metric rows / element pairs | Exact / nonexact rows | Mismatch count | Max absolute / max relative |
| --- | --- | --- | --- | --- |
|K|10 /20,364,800|0 /10|11,205,683|16.3125 /755496.75|
|V|10 /20,364,800|0 /10|11,309,008|14.78125 /5111807.0|
|All|20 /40,729,600|0 /20|22,514,691|16.3125 /5111807.0|

Maximum scope IDs share prefix `B-r3:PID350:TP0:ab9c724339da47169960dcd488c647cd:P90112:Q98067:E98304`, with absolute`:L27:K` and relative`:L15:V`. Their complete OLD/FRESH extrema are in JSON `maxima`;these are different coordinates. A large relative error can reflect a tiny nonzero OLD denominator, as the retained maximum explicitly shows; no error-normalization repair or new acceptance threshold is introduced.

Observed command result: **PASS**, first focused audit exited0; all assertions passed and printed the linked JSON content. There was no checker/serving error, new tolerance or runtime correction. Full runtime metadata was parsed once during this decisive audit. Actual invocation (extracts only the documented stdlib body, not an installed runtime module):

```bash
timeout 60s env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
import resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
p = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_B_r3_numeric_results.md')
block = p.read_text().split('<!-- numeric-audit-command -->\n```bash\n', 1)[1].split('\n```', 1)[0]
code = block.split("<<'PY'\n", 1)[1].rsplit('\nPY', 1)[0]
exec(compile(code, str(p) + ':numeric-audit', 'exec'))
PY
```

Final small-artifact consistency: **PASS_ARTIFACTS**. All20 row objects/extrema equal the small retained result projection; scope IDs, serialized-row aggregates/maxima and report table agree. Both owned files have final LF/no trailing whitespace. This check only reopens the123-KB result and new artifacts, not runtime metadata, source, baseline or any native module; it does not independently recompute raw-array reductions. Exact command:

```bash
timeout 60s env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
import json, resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
T = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
D = T / 'evidence/teacher-scoring-kv-coherence-probe-20261111'
J = D / 'numeric-verification-B-r3.json'
P = T / 'test_report_2026-11-11_kv_coherence_native_B_r3_numeric_results.md'
a = json.loads(J.read_text())
r = json.loads((D / 'native/B/admission-B-r3/result.json').read_text())
w = next(b for b in r['kv_coherence']['summaries'][0]['banks'] if b['rid'] == 'ab9c724339da47169960dcd488c647cd')
assert len(a['rows']) == len(w['metrics']) == 20
for row, original in zip(a['rows'], w['metrics']):
    assert {k: row[k] for k in original} == original
    assert row['scope_id'] == a['scope_id'] + ':L' + str(row['layer_id']) + ':' + row['side']
    assert row['sanity'] == row['FP32_extremum_consistency'] == 'PASS'
for side, group in a['aggregates'].items():
    selected = a['rows'] if side == 'all' else [x for x in a['rows'] if x['side'] == side]
    assert group['mismatch_count'] == sum(x['mismatch_count'] for x in selected)
    assert group['element_pairs'] == 2036480 * len(selected)
for label, maximum in a['maxima'].items():
    field = 'max_' + label + '_error'
    selected = [x for x in a['rows'] if x[field] == maximum['value']]
    assert maximum['value'] == max(x[field] for x in a['rows'])
    assert maximum['scope_ids'] == [x['scope_id'] for x in selected]
    assert maximum['locations'] == [{'layer_id': x['layer_id'], 'side': x['side'], **x[label + '_extremum']} for x in selected]
assert a['aggregates']['all']['mismatch_count'] == 22514691
assert a['ordering']['F'] == 531885904 != a['ordering']['S'] == 532178656
assert a['checks']['warm_correctness'] == 'FAIL unchanged;1/4 agreement'
assert a['checks']['formal04_05'] == 'HOLD'
text = P.read_text()
for row in a['rows']:
    expected = f"|{row['layer_id']}/{row['side']}|{row['mismatch_count']}|{row['max_absolute_error']}|{row['max_relative_error']}|PASS|"
    assert expected in text
for path in (P, J):
    b = path.read_bytes()
    assert b.endswith(b'\n') and b'\r' not in b
    assert all(line.rstrip() == line for line in b.splitlines())
print('PASS_ARTIFACTS: all20 source metric objects/extrema unchanged; scope IDs, aggregates, maxima and report table agree; LF/whitespace PASS. No runtime metadata/native/baseline/source/hash rerun.')
PY
```

Exact whitespace/status commands (run independently, not a chained shell):

```bash
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_B_r3_numeric_results.md
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/numeric-verification-B-r3.json
git status --short -- task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_B_r3_numeric_results.md task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/numeric-verification-B-r3.json
```

Actual: both `--no-index` checks emitted no whitespace diagnostics; exit1 is expected because each new file differs from `/dev/null`. Scoped status showed exactly the two new untracked outputs. Only these files were created; all old/raw/source/config/tests/shared eight documents/README were preserved, with no staging/commit. Scope complete; this subagent stops.

## 1. Plan completion checkpoint

**Summary: PASS6 | BLOCKED/FAILED0 | SKIPPED1 | TODO0.** A measured equality FAIL is a completed numerical observation, not an unsuccessful audit task.

| Assigned subtask | Status | Recorded evidence |
| --- | --- | --- |
| Consume committed original prerequisite acceptance | PASS |281e qualification artifacts and accepted B controls consumed, not rerun. |
| Compare actual same-RPC metric projections | PASS | Raw/normalized/result full row objects agree. |
| Inspect20 rows/40 extrema/schema/topology/geometry | PASS | Focused stdlib audit first execution passed. |
| Interpret only local FULL K/V candidate1 | PASS | Nonexact observation bounded to selected warm TP0/7955 rows; no causal conclusion. |
| Produce the two owned English/JSON artifacts | PASS | Exact rows, aggregates, maxima scope IDs and reproducible commands recorded. |
| Verify final artifact consistency and preservation | PASS | PASS_ARTIFACTS and scoped whitespace/status evidence. |
| Optional cold-FRESH versus warm-FRESH | SKIPPED | Payload pair not retained; no new run or code. |

## 2. Drift detection

**Conclusion: no execution drift.** Window: this scoped numeric assignment through final artifact checks. Frontier: return the two completed artifacts and stop; parent RCA/fix/formal work is outside this assignment.

| Pattern | Verdict | Evidence |
| --- | --- | --- |
|D1 Tooling polish|CLEAR|Only the required row/scalar/copy audit and small artifact checks; no reusable/generalized harness.|
|D2 Retry loop|CLEAR|First focused numeric audit passed; no source/runtime fix or rerun.|
|D3 Side quest|CLEAR|No SSM/performance/root-fix investigation or edits.|
|D4 Stalled frontier|CLEAR|Explicit no-delegation scope; shared status writer remains independently owned, not awaited.|
|D5 Gold-plating|CLEAR|Only two new assigned artifacts; no raw/event/buildID/context/allTP gate.|
|D6 Analysis sprawl|CLEAR|Focused reads directly produced all20 numerical rows and the bounded conclusion.|
|D7 Off-route|CLEAR|Accepted281e is the gate; no live eight-document reads, GPU/native/API calls or broadened causal acceptance.|

**Document checks:** S1–S4/S6 show no defect in this explicit scoped assignment. S5 historical headers in `requirements.md@281e:3` and `plan.md@281e:3,160` still describe ordering in progress, while the three committed qualification artifacts accept it. The user explicitly makes281e acceptance authoritative and assigns concurrent status reconciliation to another owner; this historical mismatch is not a new approval or serial gate. No live eight documents were read. **Attribution:** no execution HIT.

## 3. Route correction

**Branch B, routine historical status reconciliation only.** Document update belongs to the already-running primary/status writer: retain historical wording, update the current frontier from committed281e acceptance and these bounded numerical observations without promoting cause/fix/formal. This is already authorized and independently owned; no additional approval, waiting dependency or edit by this subagent is introduced.

**Deviation behaviors to stop: none.** Next route:
1. Return both completed numeric artifacts; done condition: exact20 rows/aggregates/maxima scopes, explicit PASS/FAIL/SKIP/limits and commands recorded. Stop this assignment.
2. Primary independently combines scoped A/B findings and chooses its existing RCA/fix work. This report neither performs nor accepts that work.

## 4. Three points needing attention

1.20/20 measured rows differ;22,514,691/40,729,600 pairs support only local FULL K/V candidate1, not a warm cause or earliest divergence.
2.Projection/scalar consistency PASS is source-backed compact evidence; raw-array reductions cannot be independently replayed and are not requested.
3.Warm1/4 FAIL,formal04/05 HOLD,06 each own200 and B no-A200 edge remain unchanged; no extra readiness gate or stream-equivalence claim.
