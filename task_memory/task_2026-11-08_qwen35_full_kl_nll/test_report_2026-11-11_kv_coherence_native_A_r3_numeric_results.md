## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record primary acceptance after reading both artifacts and checking all32 small-result metric rows,64 FP32 extrema and aggregate totals; source-backed numerical differences do not establish a causal root or fix. |
| 2026-11-11 | Verify the copied32 machine rows/scope IDs and all/K/V aggregates against retained compact result rows; record the scope checkpoint and stop without rerunning the complete verifier. |
| 2026-11-11 | Record PASS compact projection/field/FP32-extremum verification and all32 nonzero rows; add complete machine rows/aggregates and local-only interpretation. |
| 2026-11-11 | Interpret the retained A-r3 compact OLD/FRESH metrics after primary acceptance at281e70f7; preserve the original scientific and execution limits. |

# A-r3 scoped KV numerical results

TaskID: `profile-kv-coherence-native-A-r3-numeric-20261111`.

## Scope and acceptance authority

This is a local, standard-library-only interpretation of the existing A-r3 capture, not another capture, GPU run, CPU fixture, source/hash/baseline qualification or root-cause investigation. Only this report and `evidence/teacher-scoring-kv-coherence-probe-20261111/numeric-verification-A-r3.json` are owned.

The primary explicitly accepts all original scoped measurement prerequisites at committed `281e70f7`. The following three committed artifacts were read through Git, not through live shared files:

- `evidence/teacher-scoring-kv-coherence-probe-20261111/physical-index-verification-r3.json`: `complete_numeric_measurement_prerequisites=PRIMARY_ACCEPTED_SCOPED`, original producer/lifetime/F-to-S `PASS_SOURCE_BACKED`, all-layer FRESH source gate, and responding-TP0/window/FULL-layer bounds.
- `test_report_2026-11-11_kv_coherence_r3_physical_indices.md`:13,55-73,91-138: original physical, producer, owning-Tensor/inline lifetime, whole-forward S.wait(F), subsequent F.wait(S), and successful captured-drain qualification.
- `test_report_2026-11-11_kv_coherence_r3_submission.md`:48-51,68-70: scoped A/B controls and measurement prerequisites accepted; numerical/root/fix/formal claims not accepted by that archive.

The committed A controls artifact at `4da5c3eb` was consumed: actual ORIGINAL all16/6804 exact, serving after-import file/class/PID ties, insert/OLD thread333/Torch S647954864, CPP-only F642383120, independent errors/marker0, and owner-bound execution. These checks are not rerun. F differs from S; scalar equality is not the ordering proof. The later explicit acceptance supersedes the older prerequisite-pending labels retained in those historical controls and the collector's unchanged `numeric_acceptance=null`/UNVERIFIED interpretation text.

The frozen original criteria are in `design_kv_coherence_measurement.md` at `281e70f7`:147-166. Shared eight-document routine S5 synchronization is separately owned and is not an approval or dependency gate. No new `fresh_layers`, raw-hash/archive, paired GPU descriptor, event timestamp or mapped-ELF criterion is imposed.

## Evidence and numerical definition

Let `T=task_memory/task_2026-11-08_qwen35_full_kl_nll` and `A=T/evidence/teacher-scoring-kv-coherence-probe-20261111/native/A/admission-A-r3`.

- Actual job: `exp-1111-194637-456465`, previously accepted Succeeded at2026-11-11T11:56:55Z, responding PID333/TP0.
- `A/result.json`:1432-2041 topology;2124-2132 cold absence/identity;2135-2230 warm window;2231-3064 all32 compact metric rows;3066-3077 warm identity/coverage and unchanged collector acceptance field.
- `A/runtime_metadata.json`: actual raw `server_info.internal_states[0].kv_coherence`, normalized `kv_coherence[0]`, and the above result summary. They are projections/copies of **one RPC readback**, not independent measurements.
- Accepted installed collector `A/kv_coherence_source_preflight/after/srt/kv_coherence.py`:311-344 defines the measured metrics;369-387 gates complete captured banks;392-395 removes payload/indices. Its previously accepted source binding is consumed, not rehashed.

Warm RID `d1f39efbb85546309cb149c82d6341e3`; cold RID `2743596029b34b6a93ede6fe881e55a4`. Actual logical case is A/sample1695/position2/repetition0, `full_input`, UID `00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6:5:127`, original input98942/start0. Position/input/start and original request joins are consumed from the accepted physical archive; this task does not repeat completion-score or baseline reads.

Derive the comparison size from the actual topology and window: P90112, E98304, warm Q98067, OLD rows `Q-P=7955`, unmeasured new suffix `E-Q=237`; FULL global layers3,7,...,63 map to dense0,...,15. Every K/V backing descriptor is BF16 CUDA0 `[1833689,1,256]`; one local KV head, head dimension256. Each layer/side therefore compares `7955*1*256=2036480` elements;32 rows compare `65167360` layer/side elements. The count is not a count of unique tokens or distinct measurements across copies.

Source arithmetic uses OLD as reference: BF16 OLD/FRESH are promoted to FP32 on CPU; `abs(FP32(OLD-FRESH))` gives absolute error, and `FP32(error/abs(OLD))` gives relative error only where both values are finite and OLD is nonzero. `relative_error_undefined_count` counts OLD==0; nonfinite counts are reported separately. Exact equality also requires all OLD/FRESH elements finite. Extrema are selected in flattened token/head/dimension order within the OLD overlap. Their token coordinates are absolute input positions, not earliest-divergence claims.

The verifier below uses `struct.pack/unpack('=f')` for the source FP32 rounding at subtraction and division, with **exact equality**, no epsilon/tolerance/scaling. It checks64 reported extrema, their128 OLD/FRESH scalar values, coordinate bounds, count bounds, field types, finiteness, exact-flag/count/maxima consistency and raw/normalized projection equality. Extrema arithmetic can be independently checked from retained scalar pairs; **full mismatch counts/maxima over the original payload cannot be independently recomputed** because raw payload archives were intentionally not retained and the collector cleared payload/indices. These are source-backed computed metrics, not fabricated raw replay.

## Verification result

**PRIMARY ACCEPTED: compact projection and all32 field/64-extremum checks. FAIL: exact OLD/FRESH payload equality in all32 measured warm rows.** The focused verifier completed successfully once and printed the machine artifact. The primary additionally checked all32 rows against the small retained result,64 exact FP32 extrema and the aggregate totals without reopening controls or rereading full runtime metadata. Both verdicts are necessary: a consistent compact metric is not a numerical equality pass.

| Check / observation | Expected / passing condition | Actual | Verdict |
| --- | --- | --- | --- |
| Raw internal state / normalized runtime / result metric projection | Exact unchanged metric/shape/window projections | Three exact copies of one RPC, not3 independent measurements | PASS |
| Complete layer/side scope |16 FULL layers, both K/V, actual7955x1x256 |32 rows,2036480 elements/row,65167360 total | PASS |
| Compact fields | Strict keys/types, finite values, counts within0..2036480, flags/maxima consistent | All32 pass; mismatch counts728399..1122820; all exact flags false | PASS |
| Extrema | Token90112<=t<98067, head0, dimension0..255; exact source FP32 arithmetic |64 extrema/128 retained scalar values;32 absolute and32 relative exact matches | PASS |
| OLD/FRESH nonfinite and OLD-zero undefined | Report separately, no substituted epsilon | OLD0, FRESH0, zero-reference undefined0 across65167360 compared elements | PASS, observed finite |
| OLD/FRESH equality | Zero mismatches and finite values in every row |32/32 different;32424908/65167360 mismatches (49.756362694453177%);32742452 equal | FAIL, observed payload difference |
| Cold OLD | n0 yields metricsNone, not fake zero equality | Cold RID has no OLD rows and `metrics=null` | PASS absent observation |
| Optional cold-FRESH versus warm-FRESH | Only if already-retained paired values exist | Not present in compact metrics; payload cleared | SKIPPED, no new run/code |
| Full raw-payload count/maxima replay | Distinguish independent replay from source-computed metrics | Raw archive intentionally absent | NOT POSSIBLE / NOT CLAIMED |

| Side | Compared elements | Mismatches | Mismatch fraction | Maximum absolute error | Maximum OLD-reference relative error |
| --- | --- | --- | --- | --- | --- |
| K,16 rows |32583680 |15794225 |48.472809087248586% |12.4345703125, layer47/token95747/head0/dim95 |275332.625, layer59/token94508/head0/dim188 |
| V,16 rows |32583680 |16630683 |51.03991630165776% |59.03125, layer63/token94985/head0/dim5 |5800634.0, layer47/token95115/head0/dim172 |

Global absolute maximum: layer63 V, token94985/head0/dimension5, OLD=-58.5, FRESH=0.53125, absolute difference59.03125. Global relative maximum: layer47 V, token95115/head0/dimension172, OLD=-4.377216100692749e-08, FRESH=0.25390625, FP32 OLD-reference relative error5800634.0. Its tiny OLD denominator explains the large ratio arithmetically; this does not measure causal significance or performance. The machine artifact preserves every row, both extrema and scope IDs, not just these maxima.

## Local interpretation and unchanged limits

**Observed:** after the original physical/source/FRESH/lifetime prerequisites were accepted, all32 A warm K/V rows report nonzero OLD/FRESH differences at actual adoption over the same7955 physical rows. **Inference:** this supports candidate1, a local canonical-KV/current-trajectory payload difference, only for the responding TP0, this `[90112,98067)` window and the16 measured FULL layers. It does not establish that the recurrent/SSM state is invalid, that these differences cause the warm scoring failure, an earliest divergent token/layer, a universal race, a required fix or a performance effect. Shape/chunk-dependent arithmetic remains a possible contributor, not a diagnosed cause.

This interpretation is falsifiable: qualified exact equality would narrow candidate1 only within this scope; observed nonzero differences do not exclude other candidates or windows. The extrema are maximum-error coordinates, not the earliest affected positions. All other TP ranks/windows and earliest Mamba state are unmeasured. Source-backed F-to-S/lifetime readiness is consumed; no new native event or device-completion measurement is claimed. F642383120!=S647954864 remains explicit, with no Triton/allTP/mapped-ELF/race-exclusion proof.

Original warm1/4 FAIL remains unchanged; formal04/05 HOLD and06 each branch's own independent200 requirement remain unchanged. No source/config/science/root fix, new GPU capture or performance conclusion follows from this result.

## Exact verification command

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Local interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, Clang22.1.3; Linux5.10.25-nvidia-gpu x86_64/glibc2.35. Retained native receipt, not executed locally: Python3.12.16/Torch2.14.1+cu130/SGLang0.5.24.dev80+g056f871. No conda activation or Torch/SGLang/native module import is used. Shell timeout60s; Python address-space limit30GiB for bounded JSON inspection. The command prints the machine artifact to stdout; its output is retained in the owned JSON via the patch tool, not a runtime data writer.

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import json, math, platform, resource, struct, subprocess, sys
from pathlib import Path

resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
T = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
EVIDENCE = T / 'evidence/teacher-scoring-kv-coherence-probe-20261111'
A = EVIDENCE / 'native/A/admission-A-r3'
TASK = 'profile-kv-coherence-native-A-r3-numeric-20261111'
WARM = 'd1f39efbb85546309cb149c82d6341e3'
COLD = '2743596029b34b6a93ede6fe881e55a4'
UID = '00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6:5:127'

def committed_json(commit, path):
    return json.loads(subprocess.check_output(['git', 'show', f'{commit}:{path}']))

def f32(value):
    return struct.unpack('=f', struct.pack('=f', value))[0]

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def metric_projection(summary):
    return {
        'schema': summary['schema'], 'process_id': summary['process_id'],
        'mapping': summary['topology']['mapping'],
        'buffers': summary['topology']['buffers'],
        'banks': {b['rid']: {
            'P': b['insert']['P'], 'E': b['insert']['E'],
            'Q': b['rebind']['Q'], 'old_rows': b['physical']['old_rows'],
            'metrics': b['metrics']
        } for b in summary['banks']}
    }

physical = committed_json('281e70f7', EVIDENCE / 'physical-index-verification-r3.json')
controls = committed_json('4da5c3eb', EVIDENCE / 'native-verification-A-r3.json')
assert physical['complete_numeric_measurement_prerequisites'] == 'PRIMARY_ACCEPTED_SCOPED'
assert physical['original_producer_lifetime_F_to_S_readiness'] == 'PASS_SOURCE_BACKED'
assert controls['primary_acceptance']['status'] == 'ACCEPTED_BOUNDED_ACTUAL_STAGE'
accepted_A = physical['pairs']['A']
result = json.loads((A / 'result.json').read_text())
runtime = json.loads((A / 'runtime_metadata.json').read_text())
assert len(result['kv_coherence']['summaries']) == len(runtime['kv_coherence']) == 1
assert len(runtime['server_info']['internal_states']) == 1
summary = result['kv_coherence']['summaries'][0]
normalized = runtime['kv_coherence'][0]
raw = runtime['server_info']['internal_states'][0]['kv_coherence']
projection = canonical(metric_projection(summary))
assert projection == canonical(metric_projection(normalized)) == canonical(metric_projection(raw))
assert summary['process_id'] == accepted_A['process_id'] == 333
assert summary['status'] == 'captured' and summary['errors'] == []
assert summary['binding_error'] is None
banks = {b['rid']: b for b in summary['banks']}
assert len(summary['banks']) == 2 and set(banks) == {WARM, COLD}
warm, cold = banks[WARM], banks[COLD]
for rid, phase in ((WARM, 'warm_stream'), (COLD, 'cold')):
    b = banks[rid]
    assert b['logical_case'] == {
        'pair': 'A', 'phase': phase, 'mode': 'full_input',
        'source_uid': UID, 'sample_index': 1695, 'repetition': 0
    }
    assert 'payload' not in b and 'indices' not in b

P, E, Q = warm['insert']['P'], warm['insert']['E'], warm['rebind']['Q']
n = Q - P
assert (P, E, Q, n, E - Q) == (90112, 98304, 98067, 7955, 237)
assert cold['rebind']['Q'] - cold['insert']['P'] == 0
assert cold['metrics'] is None
topology = summary['topology']
mapping = topology['mapping']
layers = [pair[0] for pair in mapping]
assert layers == accepted_A['topology']['FULL_layers'] == list(range(3, 64, 4))
assert [pair[1] for pair in mapping] == list(range(len(layers)))
buffers = {b['layer_id']: b for b in topology['buffers']}
assert len(buffers) == len(topology['buffers']) == len(layers) == 16
shape = buffers[layers[0]]['K']['shape']
heads, dim = shape[1:]
assert shape == [1833689, 1, 256]
for layer in layers:
    for side in ('K', 'V'):
        desc = buffers[layer][side]
        assert desc['shape'] == shape
        assert desc['dtype'] == 'torch.bfloat16' and desc['device'] == 'cuda:0'
elements = n * heads * dim
assert elements == 2036480
rows = warm['metrics']
assert [(r['layer_id'], r['side']) for r in rows] == [(l, s) for l in layers for s in ('K', 'V')]
assert len(rows) == 32 and elements * len(rows) == 65167360
row_keys = {
    'layer_id', 'side', 'old_rows', 'values_exact', 'mismatch_count',
    'max_absolute_error', 'max_relative_error', 'relative_error_undefined_count',
    'old_nonfinite_count', 'fresh_nonfinite_count', 'absolute_extremum', 'relative_extremum'
}
count_keys = ('mismatch_count', 'relative_error_undefined_count', 'old_nonfinite_count', 'fresh_nonfinite_count')
scope = 'A-r3-TP0-OLD90112-98067'
validated_rows = []
for row in rows:
    assert set(row) == row_keys
    assert type(row['layer_id']) is int and type(row['side']) is str
    assert type(row['old_rows']) is int and row['old_rows'] == n
    assert type(row['values_exact']) is bool
    for key in count_keys:
        assert type(row[key]) is int and 0 <= row[key] <= elements
    assert row['old_nonfinite_count'] == row['fresh_nonfinite_count'] == 0
    assert row['relative_error_undefined_count'] == 0
    assert row['values_exact'] == (row['mismatch_count'] == 0)
    assert row['values_exact'] is False and row['mismatch_count'] > 0
    for key in ('max_absolute_error', 'max_relative_error'):
        assert type(row[key]) is float and math.isfinite(row[key]) and row[key] > 0
    for label in ('absolute', 'relative'):
        extremum = row[label + '_extremum']
        assert set(extremum) == {'token', 'head', 'dimension', 'OLD', 'FRESH'}
        for key in ('token', 'head', 'dimension'):
            assert type(extremum[key]) is int
        assert P <= extremum['token'] < Q
        assert 0 <= extremum['head'] < heads and 0 <= extremum['dimension'] < dim
        for key in ('OLD', 'FRESH'):
            assert type(extremum[key]) is float and math.isfinite(extremum[key])
            assert f32(extremum[key]) == extremum[key]
        assert extremum['OLD'] != 0
        difference = abs(f32(extremum['OLD'] - extremum['FRESH']))
        ratio = f32(difference / abs(extremum['OLD']))
        if label == 'absolute':
            assert difference == row['max_absolute_error']
            assert ratio <= row['max_relative_error']
        else:
            assert ratio == row['max_relative_error']
            assert difference <= row['max_absolute_error']
    validated_rows.append({'scope_id': f"{scope}-L{row['layer_id']}-{row['side']}", **row})

def maximum(selected, label):
    key = 'max_' + label + '_error'
    row = max(selected, key=lambda x: x[key])
    return {'scope_id': row['scope_id'], 'layer_id': row['layer_id'], 'side': row['side'],
            'value': row[key], 'extremum': row[label + '_extremum']}

def aggregate(selected):
    total = elements * len(selected)
    mismatch = sum(row['mismatch_count'] for row in selected)
    return {
        'metric_rows': len(selected), 'comparison_elements': total,
        'exact_rows': sum(row['values_exact'] for row in selected),
        'different_rows': sum(not row['values_exact'] for row in selected),
        'mismatch_count': mismatch, 'equal_element_count': total - mismatch,
        'mismatch_fraction': mismatch / total,
        'relative_error_undefined_count': sum(row['relative_error_undefined_count'] for row in selected),
        'old_nonfinite_count': sum(row['old_nonfinite_count'] for row in selected),
        'fresh_nonfinite_count': sum(row['fresh_nonfinite_count'] for row in selected),
        'minimum_row_mismatch_count': min(row['mismatch_count'] for row in selected),
        'maximum_row_mismatch_count': max(row['mismatch_count'] for row in selected),
        'max_absolute_error': maximum(selected, 'absolute'),
        'max_relative_error': maximum(selected, 'relative')
    }

output = {
    'schema': 'kv-coherence-native-A-r3-numeric-v1', 'task_id': TASK,
    'date': '2026-11-11', 'pair': 'A', 'job': accepted_A['job'],
    'verdicts': {
        'measurement_prerequisites': 'PRIMARY_ACCEPTED_SCOPED_CONSUMED_281e70f7',
        'compact_metric_projection': 'PASS_SAME_RPC_RAW_NORMALIZED_RESULT',
        'all32_metric_consistency': 'PASS', 'all64_extremum_FP32_arithmetic': 'PASS_EXACT',
        'scoped_OLD_FRESH_equality': 'FAIL_NONZERO_32_OF_32_ROWS',
        'candidate1': 'SUPPORTED_LOCAL_PAYLOAD_DIFFERENCE_AT_ADOPTION_ONLY',
        'cold_OLD': 'ABSENT_METRICS_NULL',
        'optional_cold_FRESH_vs_warm_FRESH': 'SKIPPED_NOT_RETAINED_PAYLOAD_CLEARED',
        'raw_payload_count_maxima_replay': 'NOT_POSSIBLE_INTENTIONALLY_ABSENT',
        'warm_correctness': 'FAIL_UNCHANGED_1_OF_4', 'formal04_05': 'HOLD',
        'formal06': 'EACH_BRANCH_REQUIRES_OWN_INDEPENDENT_200_UNCHANGED'
    },
    'prerequisites': {
        'accepted_commit': '281e70f7', 'controls_commit': '4da5c3eb',
        'physical_artifact': str(EVIDENCE / 'physical-index-verification-r3.json'),
        'physical_report': str(T / 'test_report_2026-11-11_kv_coherence_r3_physical_indices.md'),
        'submission_report': str(T / 'test_report_2026-11-11_kv_coherence_r3_submission.md'),
        'A_controls_artifact': str(EVIDENCE / 'native-verification-A-r3.json'),
        'original_producer_lifetime_F_to_S': physical['original_producer_lifetime_F_to_S_readiness'],
        'all_layer_FRESH': physical['checks']['complete_FRESH_before_duplicate_release_source_and_capture_gate'],
        'fresh_layers_raw_hash_paired_descriptor_new_gate': False,
        'F_scalar': 642383120, 'S_scalar': 647954864, 'F_equals_S': False,
        'baseline_hash_CPU_native_qualification_repeated': False
    },
    'measurement_scope': {
        'scope_id': scope, 'warm_rid': WARM, 'cold_rid': COLD,
        'sample_index': 1695, 'sample_position': 2, 'repetition': 0,
        'source_uid': UID, 'mode': 'full_input', 'input_count': 98942, 'logprob_start_len': 0,
        'identity_basis': 'Actual result.logical_case plus already-accepted original request identities; no repeated baseline/score reads',
        'responding_process_id': summary['process_id'], 'responding_rank': 'TP0',
        'configured_tp_size': runtime['tp_size'], 'coverage': summary['coverage'],
        'P': P, 'E': E, 'Q': Q, 'old_rows': n, 'uncompared_suffix_rows': E - Q,
        'FULL_global_to_dense_mapping': mapping, 'K_V_backing_shape': shape,
        'dtype': 'torch.bfloat16', 'device': 'cuda:0', 'local_KV_heads': heads, 'head_dimension': dim,
        'per_layer_side_comparison_shape': [n, heads, dim],
        'per_layer_side_comparison_elements': elements,
        'total_layer_side_comparison_elements': elements * len(rows),
        'relative_reference': 'OLD', 'relative_undefined': 'OLD==0; not replaced by epsilon',
        'arithmetic': 'BF16 to FP32; rounded FP32 subtraction/absolute/division',
        'cold_old_rows': 0, 'cold_metrics': None
    },
    'metric_provenance': {
        'result': str(A / 'result.json'), 'runtime_metadata': str(A / 'runtime_metadata.json'),
        'projections': ['result.kv_coherence.summaries[0]', 'runtime_metadata.kv_coherence[0]',
                        'runtime_metadata.server_info.internal_states[0].kv_coherence'],
        'metric_projection_exact_equal': True, 'projection_copies': 3,
        'independent_measurement_count': 1,
        'source_metric_definition': str(A / 'kv_coherence_source_preflight/after/srt/kv_coherence.py') + ':311-344',
        'source_payload_release': 'same file:392-395; captured receipt has no raw payload/indices',
        'collector_numeric_acceptance_unchanged': summary['numeric_acceptance'],
        'collector_interpretation_unchanged': summary['interpretation'],
        'counts_and_maxima_basis': 'Source-backed computed compact metrics; not independent raw-payload replay'
    },
    'checks': {
        'rows_checked': len(rows), 'extrema_checked': 2 * len(rows),
        'extremum_OLD_FRESH_scalars_checked': 4 * len(rows),
        'row_keys_types_finiteness_count_bounds': 'PASS_ALL32',
        'exact_flags_mismatch_maxima_consistency': 'PASS_ALL32',
        'extremum_token_head_dimension_bounds': 'PASS_ALL64',
        'FP32_absolute_extremum_error_exact_matches': len(rows),
        'FP32_relative_extremum_ratio_exact_matches': len(rows),
        'extremum_cross_maximum_bounds': 'PASS_ALL64', 'epsilon_tolerance': None,
        'metric_consistency_failures': [], 'nonfinite_reported': 0, 'zero_reference_undefined_reported': 0
    },
    'aggregate': aggregate(validated_rows),
    'by_side': {side: aggregate([r for r in validated_rows if r['side'] == side]) for side in ('K', 'V')},
    'rows': validated_rows,
    'environment': {
        'workspace': str(Path.cwd()), 'local_python': platform.python_version(),
        'local_executable': sys.executable, 'local_platform': platform.platform(),
        'native_receipt': {k: result['runtime'][k] for k in ('python', 'torch', 'sglang')},
        'execution': 'Standard-library JSON/text/scalar checks only; no runtime/native imports',
        'timeout_seconds': 60, 'address_space_limit_bytes': 30 * 1024**3
    },
    'limits': [
        'Nonzero qualified OLD/FRESH metrics support candidate1 only: local payload difference at actual adoption.',
        'No invalid-SSM, causal warm-failure, earliest-token/layer, root-fix or performance claim.',
        'No allTP, other-window, earliest-Mamba-state, universal-race or mapped-ELF claim.',
        'Equality would narrow only this TP0/window/FULL-layer span; it is not observed here.',
        'Relative maxima may be large because OLD is close to zero; they do not independently measure causal severity.',
        'Full counts/maxima cannot be independently replayed from intentionally absent raw payload.',
        'Cold OLD is absent, not fabricated zero-error evidence; optional cross-bank FRESH comparison is skipped.',
        'Original warm1/4 FAIL, formal04/05 HOLD and06 each-own200 conditions remain unchanged.',
        'Concurrent routine shared-document synchronization is not a new approval or dependency gate.'
    ],
    'inspection_history': {
        'offline_schema_error': "KeyError: 'layers' in an initial topology inspection; corrected to actual mapping/buffers before numerical verification; not a runtime failure",
        'read_only_scope_deviation': 'One design symbol grep accidentally read the live design_kv_coherence_measurement.md; final criteria were reread from281e70f7 through Git, no live shared document was changed or used as current acceptance authority'
    },
    'owned_artifacts': [str(T / 'test_report_2026-11-11_kv_coherence_native_A_r3_numeric_results.md'),
                        str(EVIDENCE / 'numeric-verification-A-r3.json')]
}
print(json.dumps(output, indent=2, allow_nan=False))
PY
```

Expected: exact same-RPC metric projections,32 typed/finite/count-bounded warm rows,64 bounded and exactly FP32-consistent extrema,0 OLD/FRESH nonfinite values,0 zero-reference undefined values, cold `metrics=null`, and2036480/65167360 comparison counts. Actual: all assertions PASS; the output contains32424908 mismatches, all32 exact flags false and the extrema/aggregates reported above. Equality of OLD/FRESH is tested separately and is not assumed from a successful verification command.

The exact executed invocation extracted and ran the above unchanged command body once, rather than importing any runtime module:

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
from pathlib import Path
p=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_A_r3_numeric_results.md')
code=p.read_text().split("python -B - <<'PY'\n",1)[1].split('\nPY\n```',1)[0]
exec(compile(code,str(p)+':numeric-verifier','exec'),{})
PY
```

## Inspection commands and limitations

Committed evidence discovery used `git show --format=fuller --stat --name-only 281e70f7` and `git log -8 --format='%H %s'`. Frozen requirements/plan headers were read using `git show 667641c6:T/{requirements,plan}.md` through standard-library `subprocess.check_output`; the newer explicit primary acceptance at281e70f7 controls this follow-up. The three committed artifacts and selected A control fields were read with `git show 281e70f7:T/<artifact>` and `git show 4da5c3eb:T/evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-A-r3.json`; Markdown code fences were omitted from display because they describe prior completed verifiers, which were not executed. The frozen original criteria were read with `git show 281e70f7:T/design_kv_coherence_measurement.md`.

Dedicated bounded file reads examined only the installed collector definition, actual metric/identity fields and owned artifacts. Two standard-library schema/metric discovery commands read JSON under the same60s/30GiB limit. The first exited1 at stdin9 with `KeyError: 'layers'`; the actual topology uses `mapping` and `buffers`. The second established the actual schema and printed all32 metrics. No guessed schema was retained in the verifier, no serving error was inferred and no CPU/native fixture or module was run. Local environment values above came from `sys.version`, `sys.executable`, `platform.platform()` and the retained `result.runtime` fields, not an executed native environment.

One read-only design symbol search accidentally targeted the live measurement design rather than its Git snapshot. This was a read-scope deviation while the shared-document writer was active; the design was subsequently reread from committed281e70f7. Neither the live content nor historical design-blocker labels are used as current acceptance authority; only the explicit primary acceptance and committed prerequisite artifacts are consumed. No shared file was edited. No baseline/hash/CPU/native verification, GPU/new capture, authentication/API/SSH/cloud action, delegation, staging or commit was performed.

## Final owned-artifact copy check

Expected: every copied machine row equals its actual retained compact result row including exact field/value types,32 distinct scope IDs, exact all/K/V aggregate counts/fractions/maxima and parseable embedded verifier syntax; final LF/no trailing whitespace. Actual: **PASS_A_R3_NUMERIC_ARTIFACT_COPY:32 source rows/unique scope IDs;all/K/V aggregates/maxima exact;verifier AST parse;LF/whitespace;no full verifier re-execution**. This checks artifact transcription only; it does not rerun the large runtime-metadata projection/source/control verifier or independent raw-payload arithmetic.

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import ast,json,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS,(30*1024**3,30*1024**3))
T=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
report=T/'test_report_2026-11-11_kv_coherence_native_A_r3_numeric_results.md'
artifact=T/'evidence/teacher-scoring-kv-coherence-probe-20261111/numeric-verification-A-r3.json'
d=json.loads(artifact.read_text())
s=json.loads(Path(d['metric_provenance']['result']).read_text())['kv_coherence']['summaries'][0]
banks={b['rid']:b for b in s['banks']}
rows=banks[d['measurement_scope']['warm_rid']]['metrics']
original=[{k:v for k,v in row.items() if k!='scope_id'} for row in d['rows']]
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
assert canonical(original)==canonical(rows)
assert len(d['rows'])==32 and len({row['scope_id'] for row in d['rows']})==32
for side,group in [('all',d['rows']),('K',[r for r in d['rows'] if r['side']=='K']),('V',[r for r in d['rows'] if r['side']=='V'])]:
 a=d['aggregate'] if side=='all' else d['by_side'][side]
 total=d['measurement_scope']['per_layer_side_comparison_elements']*len(group)
 mismatch=sum(r['mismatch_count'] for r in group)
 assert (a['comparison_elements'],a['mismatch_count'],a['equal_element_count'],a['mismatch_fraction'])==(total,mismatch,total-mismatch,mismatch/total)
 for label in ('absolute','relative'):
  r=max(group,key=lambda r:r['max_'+label+'_error']);m=a['max_'+label+'_error']
  assert m=={'scope_id':r['scope_id'],'layer_id':r['layer_id'],'side':r['side'],'value':r['max_'+label+'_error'],'extremum':r[label+'_extremum']}
assert banks[d['measurement_scope']['cold_rid']]['metrics'] is None
code=report.read_text().split("python -B - <<'PY'\n",1)[1].split('\nPY\n```',1)[0]
ast.parse(code)
for p in (report,artifact):
 assert p.read_bytes().endswith(b'\n') and all(line==line.rstrip() for line in p.read_text().splitlines())
print('PASS_A_R3_NUMERIC_ARTIFACT_COPY:32 source rows/unique scope IDs;all/K/V aggregates/maxima exact;verifier AST parse;LF/whitespace;no full verifier re-execution')
PY
```

## 1. Planned scope completion

**Summary:** PASS5 / BLOCKED-FAILED-SKIPPED2 / TODO0. The two intentional skips do not block acceptance of the requested compact-only result.

| Scoped subtask | Status | Evidence |
| --- | --- | --- |
| Consume committed281e prerequisites and4da A controls | PASS | Explicit PRIMARY_ACCEPTED_SCOPED; no repeated baseline/hash/CPU/native verification. |
| Read actual compact rows and source numerical definition | PASS | result2231-3064 and accepted installed collector311-344. |
| Verify projections,32 fields/scope rows and64 extrema | PASS | Focused standard-library verifier passed,3 copies/one RPC. |
| Interpret observed differences within original limits | PASS |32424908/65167360 mismatches support candidate1 locally only. |
| Copy and check the two owned deliverables | PASS |32 exact source rows/unique scope IDs;all/K/V aggregates/maxima and syntax/LF checks pass. |
| Optional cold-FRESH/warm-FRESH comparison | SKIPPED | Not retained; source cleared payload; no new capture/code. |
| Independent full raw-payload count/maxima replay | SKIPPED | Raw archive intentionally absent; source-backed metrics are explicitly distinguished. |

## 2. Drift check

**Verdict:** D7 read-scope deviation occurred and was corrected. Window: new numeric assignment through copied-artifact verification. Current frontier: return the two numeric artifacts and stop.

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 Tooling polish | CLEAR | One bounded compact verifier and artifact-copy check; no suite/generalized harness/native imports. |
| D2 Retry loop | CLEAR | One schema discovery error resolved from actual mapping/buffers; no serving fix/retry or repeated full verification. |
| D3 Side quest | CLEAR | No unrelated source/config/science/rootfix. |
| D4 Stalled parallel frontier | CLEAR | Shared-document owner remains independent; no wait/dependency gate or prohibited delegation. |
| D5 Gold-plating | CLEAR | Only the two requested new artifacts; no old evidence/report edits or new measurement gate. |
| D6 Analysis sprawl | CLEAR | Reads produced the requested all-row numerical result and bounded falsifiable interpretation. |
| D7 Off-route | HIT, corrected | One symbol grep read the live design while its owner was active; final original criteria reread through Git281e, no further live shared reads. |

Spec checks S1-S4/S6: no scoped defect found. S5: requirements/plan headers at667641c6 and frozen design16 retain older readiness-pending labels; newer281e acceptance and the explicit numeric assignment supersede them. Routine reconciliation belongs to the concurrent eight-document owner, not a new approval/blocker. Attribution: D7 is an execution read-scope deviation, not caused by the agreed criteria.

## 3. Course correction

Branch B, historical S5 reconciliation is independently underway. The shared owner updates current frontier labels from original readiness to accepted measurement prerequisites/numerical interpretation, without changing original criteria. Under the explicit assignment, that update is neither a new dependency nor a reason to pause the numeric work; this agent does not edit those files.

Stop D7 live shared-design/requirements/plan searches; consume committed281e/667 snapshots and the explicit primary decision instead. This correction has been applied. No additional CPU, source/hash, native, API or GPU qualification is needed here. Route: return the completed two owned artifacts with scoped metrics/limitations, then stop. Root RCA/fix, any later measurement and each branch's own200 qualification are outside this task.

## 4. Three points to preserve

1. All32 measured warm rows differ;32424908/65167360 elements mismatch within only TP0/[90112,98067)/16 FULL layers.
2.64 extrema checks and same-RPC projections pass, but absent raw payload prevents independent full count/maxima replay; cold OLD remains absent.
3. Candidate1 receives local support only; warm1/4 FAIL, formal04/05 HOLD and06 each-own200 remain. The live-design read deviation is recorded and corrected, with no shared-file edit or new gate.
