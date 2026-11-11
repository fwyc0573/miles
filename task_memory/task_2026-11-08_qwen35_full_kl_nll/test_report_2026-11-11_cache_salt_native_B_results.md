## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Verify retained B namespace experiment against immutable4f1139b0 baseline and0c606967 caller:12 exact controls,4 exact salted warm-full cases, strict retractions and bounded metadata presence; record pending isolation/chunk plans and differing resolved server seeds. |
| 2026-11-11 | Incorporate completed075e75ca r2 CPU inspector:165 bindings, target8RIDs/100joins PASS and169complete chunks/16exact comparisons, TP0-only. Retain original false-scope FAIL and3 non-gating response geometry FAILs; add primary terminal replica/source RNG audit references and JSON-only replay without a seed hard gate. |

# Cache-salt native B controls and numerical results

TaskID: `profile-cache-salt-native-controls-B-20261111`.

**Numerical controls PASS12/12; salted warm-full is exact4/4. Corrected r2 CPU receipts qualify target-only isolation and complete chunk/tracking comparisons, TP0-only:165 bindings,100/100 joins across8 salted full-input RIDs,169 complete chunks and16/16 exact comparisons. Formal04/05 remain BLOCKED.** The3 failed unsalted-response geometry observations are retained and are not the target gate. No same-RNG claim, seed hard gate, numerical KV/physical/all-TP/coherence/race/historical-cause/root-fix/performance/formal acceptance is introduced.

Only this report and [native-verification-B-controls.json](evidence/teacher-scoring-cache-salt-probe-20261111/native-verification-B-controls.json) are owned. No GPU/platform/auth/SSH/query/poll/delegation occurred. A business results were not inspected. The completed primary r2 JSON is now referenced; no inspector or metadata-join analysis was rerun here. All original/raw files remain unchanged. Nothing was staged or committed.

## Execution and source identity

- New run: `evidence/teacher-scoring-cache-salt-probe-20261111/native/B/admission-B-r1`, job `exp-1111-083634-881422`. Retained `admission-B-r1.terminal.json`: **Succeeded**, creator `i-fengyicheng`, finish `2026-11-11T00:43:21Z`; `result.json` has `measurements_completed`, native measurements and cleanup completed. This is a local receipt read, not a platform query.
- Primary's earlier `initial-platform-verification.json` B projection recorded **Running**, pinned container-spec image, GPU limit`"4"`, and matching local source annotation`100.96.128.195:/data/ycfeng:/data/ycfeng`. It is historical placement evidence, not the current terminal state. No container Completed/exit/restart or independently measured imageID is inferred from it.
- New independent primary SDK reference: `evidence/teacher-scoring-cache-salt-probe-20261111/terminal-replica-B.json`, SHA256`d2720d13f8a6a33a7af078d378bc64af67305c4ff06e6c5905d914fdf6ae26ef`, collected`2026-11-11T00:48:16.498554+00:00`. Replica`exp-1111-083634-881422-cfcd2084` is Succeeded; probe container **Completed/exit0/restart0**, raw ready/started false after completion. Its actual `imageID` matches the pinned165ff0be digest; separate raw `image` is`sha256:b58475dbbe8386648157b485da7cc6984d12a3f4f436498c3f448f64c25867c0`, not rewritten to the imageID. Source placement remains supported by the earlier primary annotation and worker source receipts. This verifier performed no SDK/platform operation; terminal/image status is not CUDA/numerical/all-TP proof.
- Actual `preload.json.runtime.gpu_devices`: **four NVIDIA H800**,81559 MiB each, driver570.124.06. Worker `/opt/sglang/bin/python3`, Python3.12.16; SGLang0.5.24.dev80+g056f871; Torch2.14.1+cu130. Retained image input: `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`.
- Qualified baseline: `evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1`, with the retained B verification JSON SHA256`967f628e116b4cf7e5c6951d24e8c2f469e8a7877a41d12bcb3a0087aa51faaf`. Baseline6 caller hashes/byte counts match immutable Git blobs at **`4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff`**; new6 match **`0c6069678032930c79d5ed0f248164d3bdf78c06`**. Actual native-result relative keys select these blobs, never future working-tree source files. Only `tests/manual/agent_opd/probe_teacher_scoring.py` differs among the6 caller files; core scoring/source helpers are unchanged.
- Actual math6 and metadata-overlay16 before/after archive files, manifests and observed SHA maps match baseline byte-for-byte. Source math manifest SHA256`dd856add48fe221101c03b96fb018e8fc939362cc15415482cac6d5128370c6f`; metadata manifest`22aa07e3f10b9c9d8aec6f5fdc180076613d3014f6985542f0c8ea27bafcb3e9`. Preload/result/source receipts agree. Source identity is not independent loaded-code validation on allTP ranks.

Cache remains **ON**: actual server-info fields `disable_radix_cache=false`, `prefill_only_disable_kv_cache=false`, `disable_chunked_prefix_cache=false`; actual argv equals baseline after removing only `--dist-init-addr` and its deployment value. TP4/DP1/PP1, chunk8192, BF16, max-running1, context131072, deterministic inference and CUDA-graph-disabled settings remain unchanged. Teacher model path and model manifest hashes match baseline; this is not a whole-weight checksum. `SGLANG_FORCE_COARSE_WAR_BARRIER` remains raw null. Probe config differs only by the full-input salt flag and output parent; the original sample-selection input is unchanged.

**Measured RNG observation, not a new gate:** new actual server-info `random_seed=263946245`; baseline`random_seed=596871011`. Neither argv includes an explicit seed argument; same RNG is not claimed. Retained model-runner source`runtime_metadata_source_preflight/after/srt/model_executor/model_runner.py:2255–2284`, SHA256`5d07424971c85b63aa1ff0b7e788a6b7938f012a09c86352ccb8785817505181`, provides the prefill-only `compute_logprobs_only` method **without next-token sampling**. It may call `sampler.compute_logprobs_only` for probabilities, not `sampler(...)` for token selection. Actual server-info `enable_mamba_cache_stochastic_rounding=false` and `enable_dynamic_chunking=false`. These are bounded source/configuration observations, not a receipt that every worker dispatch selected the method. Resolver and worker-dispatch source remain **PENDING in primary's0-GPU collector**. No seed hard gate, identical-RNG or causal-effect inference is added; scoring/control numbers and tolerance remain unchanged.

## Request, salt and response integrity

Original source: `evidence/teacher-scoring-probe-20261111/retained-cases.json`, SHA256`c45424e8106c2beb7500acacb68aa0939da0088c926af8012dd9fbd780f0ffc9`. First4/rep0 source identities and fixed token inputs are unchanged. Full UIDs and native RIDs are retained in the evidence JSON.

| Position | Original UID suffix | Index | Input countN | Canonical responseR | Unsalted returned input-logprob countR+1 |
| --- | --- | --- | --- | --- | --- |
| 0 | `:5:123` | 1693 | 97365 | 734 | 735 |
| 1 | `:5:125` | 1694 | 98312 | 246 | 247 |
| 2 | `:5:127` | 1695 | 98942 | 431 | 432 |
| 3 | `:5:129` | 1696 | 99074 | 290 | 291 |

- **16/16 requests scored/HTTP200**,16 unique nonempty pre-send request IDs and16 distinct native RIDs. **10/10 flushes succeeded**:8 cold mode/case flushes and2 stream-start flushes. No cache-off change occurred.
- **8/8 full-input receipts** contain the actual sent nonempty unique salt `B:<pre-send request_id>`, e.g.`B:warm_stream-r0-s2-full_input`. **8/8 response-only receipts** retain raw`cache_salt=null`. The pinned caller records the same payload salt it sends; no salt is derived from a post-send native RID.
- For each response-only request, `logprob_start_len=prompt_count−1`, returned countR+1, leading logprob null and first requested/returned token ID equals the original preceding-prompt token. Full-input starts0 and returnsN with a leading null. All16 canonical vectors have exactlyR original response-tail token IDs and finiteR log probabilities: **6804 scores** checked. Placeholder positions are not silently treated as response scores.
- Requests/completions have exact logical identity `(pair,source_uid,sample_index,repetition,phase,mode)` and matching `native_request_id=meta_info.id`. Pointer destinations are the actual run's16 completion files. Neither file order nor request counts are identity joins. Salt strings/pre-send IDs are not persistent native/cache object identities.
- Native raw response arrays were kept worker-local by the existing caller. This verification checks retained first-element/count receipts, immutable sender/fixture provenance and canonical vectors; it does not claim a new full-body upload or independent capture of every submitted input token.

## Controls and salted warm-full measurements

All comparisons use existing `tests.manual.agent_opd.probe_teacher_scoring._comparison(reference,candidate)`. Its machine field `accepted` remains null; no tolerance or numerical policy is added. Relative error is `abs(reference−candidate)/abs(reference)` only for nonzero reference. Zero-reference positions remain **undefined even when both values are0**; reported maxima exclude those positions.

**Controls first:** all8 unsalted response vectors are exact against matching qualified baseline responses, **including the original warm drift**. All4 salted cold-full vectors are exact against qualified baseline cold-full. Each of the12 has matching token IDs, finite scores, `values_exact=true`, **max absolute error0.0 / max defined relative error0.0**. Logical keys select references; identical displayed pre-send IDs are not the join mechanism.

| Control group | Exact / total | Undefined-zero counts by position0/1/2/3 |
| --- | --- | --- |
| cold unsalted response-only | 4/4 | 3/5/4/4 |
| warm unsalted response-only | 4/4 | 3/5/3/4 |
| salted cold full-input | 4/4 | 3/5/4/4 |

**Four salted warm-full cases versus their own run's salted cold-full:**

| Position / index | Exact | Max absolute error | Max defined relative error | Undefined-zero count |
| --- | --- | --- | --- | --- |
| 0 /1693 | yes | 0.0 | 0.0 | 3 |
| 1 /1694 | yes | 0.0 | 0.0 | 5 |
| 2 /1695 | yes | 0.0 | 0.0 | 4 |
| 3 /1696 | yes | 0.0 | 0.0 | 4 |

The resulting count is **4/4 exact,0/4 nonexact**. This is not a full-versus-response equality gate: unchanged warm unsalted responses still contain baseline drift. Same-run cold-full is the numerical reference; warm-full is not an oracle. A control failure would be **inconclusive**, not permission to change tolerance/cache/science or a source-fix result.

## Retractions, metadata presence and interpretation limits

`meta_info.num_retractions` is present and a **strict nonnegative int, not bool**, for all16 new and16 baseline receipts. There is no missing-to-zero/default conversion. All16 new values are0; all16 matched baseline values are0; all16 differences(new−baseline) are0, sums0/0, changed-request count0. Each value/difference is retained under`retractions.observations`. Equality is an observed fact, **not an extra required unchanged condition**.

The initial verifier performed only cheap metadata presence/rank/RID-set coverage: final `runtime_metadata.json` is collected, schema`mamba-runtime-metadata-v1`, **one respondent**,16293 rows, raw rank`{dp_rank:null,tp_rank:0,pp_rank:0,attn_dp_rank:0,attn_tp_rank:0}`. Direct explicit RID-bearing fields cover16/16 actual native request IDs with no unmatched explicit RID. DP None is retained, not rewritten. The follow-up reads primary's completed CPU inspector output, not a duplicate raw event/plan/checkpoint analysis.

**Completed primary CPU inspector reference:** `evidence/teacher-scoring-cache-salt-probe-20261111/native-inspection-B-r2.json`, SHA256`9182c9737e51fab5f6ea3f1a0f30be1b002e7d659e9b09bf4ad4075972f43121`; corrected inspector commit`075e75ca52a613dcbd28ff40686f00d390771bf7`. Primary used **`/usr/bin/python3` (3.10.6)**; the absent `python` alias is not used. This verifier neither invoked the inspector nor performed a platform operation.

| Actual r2 field / scope | Result |
| --- | --- |
| `cpu_verdict`, `source_controls.status`, `protocol.status`, `vector_controls.status` | PASS;12 exact numerical controls |
| `scopes[0].isolation.binding_status` / `ordinary_joined` | PASS /165 uniquely bound checkpoint joins |
| `scopes[0].isolation.full_input_isolation` | PASS; target8/covered8 salted full-input RIDs,100 joined,0 failed |
| `scopes[0].isolation.control_observations` | Literal FAIL;65 unsalted-response geometry joins,62 PASS/3 FAIL; **not target isolation gate** |
| `scopes[0].isolation.status` | Literal aggregate FAIL, retained; not substituted for the scoped full-input gate |
| `scopes[0].chunks.status`, `chunk_tracking_observations` | PASS;169 complete candidate chunks,16/16 initial-prefix comparisons exact,16/16 complete chunk/tracking comparisons exact baseline |

The qualification is **responding process396/TP0 only**, with raw DP None.165 successful bindings do not mean all165 geometry checks passed. Primary's original `native-inspection-B.json`, SHA256`2bcc0ab925b627d957374942e8ac1c3500919a880c7d27ab6f6e20df26468a33`, remains literal **false-scope CPU FAIL** and was not overwritten. The r2 correction scopes the gate to salted full-input rather than treating the3 expected unsalted-response geometry observations as experiment failure. No GPU rerun, source/tolerance change, raw row renumbering or deletion occurred.

No all-zero/no-rebind/node/count shortcut establishes isolation. The full-input path already started0, and complete chunk/tracking comparisons are exact baseline; a new initial recompute is not inferred. Pointer/source receipts, bound geometry and exact numerical controls are not physical cache values or device completion receipts.

Controls and scoped isolation/chunk behavior are now qualified for interpretation of the4 observed cold-to-warm cases **within this bounded B first4/rep0/TP0 diagnostic**. This is not numerical KV–SSM causality, historical cause, physical slot identity/value, GPU device completion, allTP/coherence/race exclusion, performance or source/root-fix/formal acceptance. The seed difference remains an observation, not a new hard gate; missing resolver/worker-dispatch source remains pending0GPU collection. Dropped1024-hit groups and later repetitions remain outside scope; formal hold is unchanged.

## Exact local replay and validation

Local working directory `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`; verifier `/usr/bin/python3`, Python3.10.6, Linux, no conda activation. Reads use standard-library JSON/hashlib/subprocess plus existing pure comparison/receiver helpers, `-B`/`PYTHONDONTWRITEBYTECODE=1`,60-second tool timeouts and exact B paths. No raw writes, bytecode/cache, network operation or native run occurred.

Historical worker command is retained in `evidence/teacher-scoring-cache-salt-probe-20261111/admission-B-r1.json.worker_command`; it was **not rerun**. It uses `/opt/sglang/bin/python3 -u -B -m tests.manual.agent_opd.probe_teacher_scoring`, `--pair B`, `teacher_scoring_cache_salt_probe_config.json`, the unchanged `teacher_scoring_runtime_metadata_first4_manifest.json`, `--repeats 1 --request-timeout 3600` and `timeout --signal=TERM --kill-after=90s 3600s`.

Exact affected replay command (compiles then executes the retained Python block below):

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
p = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_cache_salt_native_B_results.md')
code = p.read_text().split('<!-- verification-python -->\n```python\n', 1)[1].split('\n```', 1)[0]
exec(compile(code, str(p), 'exec'))
PY
```

<!-- verification-python -->
```python
from pathlib import Path
import hashlib, json, math, platform, subprocess
from tests.manual.agent_opd.probe_teacher_scoring import _comparison, _runtime_metadata_states

base = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-cache-salt-probe-20261111')
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
lines = lambda p: [json.loads(x) for x in p.read_text().splitlines()]
e = load(base / 'native-verification-B-controls.json')
run, old = Path(e['run_path']), Path(e['baseline_path'])
assert platform.python_version() == e['environment']['verification_python']
for name, expected in e['raw_sha256'].items():
    assert sha(base / name) == expected, name
assert sha(Path(e['baseline_verification_path'])) == e['baseline_verification_sha256']
baseline = load(Path(e['baseline_verification_path']))
for name, expected in baseline['raw_run_sha256'].items():
    assert sha(old / name) == expected, name
r, p, b = load(run / 'result.json'), load(run / 'preload.json'), load(old / 'result.json')
terminal, admission = load(base / 'admission-B-r1.terminal.json'), load(base / 'admission-B-r1.json')
assert terminal['job'] == admission['job'] == r['job'] == e['job']
assert terminal['status']['phase'] == 'Succeeded' and terminal['creator'] == 'i-fengyicheng'
assert r['status'] == 'measurements_completed' and r['native_measurements_completed'] and r['cleanup_completed']
assert r['runtime'] == p['runtime']
for field, expected in (('python', '3.12.16'), ('executable', '/opt/sglang/bin/python3'), ('sglang', e['environment']['sglang']), ('torch', e['environment']['torch']), ('configured_image', e['environment']['image']), ('gpu_devices', e['environment']['gpu_devices'])):
    assert r['runtime'][field] == expected
placement = next(x for x in load(base / 'initial-platform-verification.json')['jobs'] if x['pair'] == 'B')
assert placement['phase'] == 'Running' and placement['job'] == r['job']
assert placement['source_annotations']['job'] == admission['source_mount'] == e['environment']['source_mount']
assert placement['containers'][0]['image'] == e['environment']['image']
assert placement['containers'][0]['limits']['nvidia.com/gpu'] == '4'
for current, commit in ((r, e['caller_commit']), (b, e['baseline_caller_commit'])):
    assert len(current['native_scoring_sources']) == 6
    for name, identity in current['native_scoring_sources'].items():
        blob = subprocess.check_output(['git', 'show', f'{commit}:{name}'], timeout=30)
        assert hashlib.sha256(blob).hexdigest() == identity['sha256'] and len(blob) == identity['bytes']
changed = [name for name in r['native_scoring_sources'] if r['native_scoring_sources'][name]['sha256'] != b['native_scoring_sources'][name]['sha256']]
assert changed == e['source']['changed_caller_files']
for scope, count, manifest in (('source_preflight', 6, 'math_manifest_sha256'), ('runtime_metadata_source_preflight', 16, 'metadata_manifest_sha256')):
    receipt = r[scope]
    assert receipt == p[scope] == lines(run / scope / 'preflight.jsonl')[0]
    assert len(receipt['files']) == count and receipt['image'] == e['environment']['image']
    assert sha(run / scope / 'source_manifest.json') == e['source'][manifest]
    for field in ('files', 'observed_before_sha256', 'observed_after_sha256'):
        assert receipt[field] == b[scope][field]
    for state in ('before', 'after'):
        for name, identity in receipt['files'].items():
            file = run / scope / state / name
            assert file.read_bytes() == (old / scope / state / name).read_bytes()
            assert sha(file) == identity[state + '_sha256'] == receipt['observed_' + state + '_sha256'][name]
def without_address(argv):
    i = argv.index('--dist-init-addr')
    return argv[:i] + argv[i + 2:]
assert without_address(r['argv']) == without_address(b['argv'])
assert '--random-seed' not in r['argv'] and '--random-seed' not in b['argv']
assert r['runtime']['model_manifest_identity'] == b['runtime']['model_manifest_identity']
assert r['runtime']['sglang_environment'] == b['runtime']['sglang_environment']
s, bs = load(run / 'server_info.json')['get_server_info'], load(old / 'server_info.json')['get_server_info']
expected_fields = {'disable_radix_cache': False, 'prefill_only_disable_kv_cache': False, 'disable_chunked_prefix_cache': False, 'chunked_prefill_size': 8192, 'dtype': 'bfloat16', 'max_running_requests': 1, 'tp_size': 4, 'dp_size': 1, 'pp_size': 1, 'context_length': 131072, 'disable_cuda_graph': True, 'enable_deterministic_inference': True}
for name, value in expected_fields.items():
    assert s[name] == bs[name] == value
assert s['random_seed'] == e['environment']['resolved_random_seed']
assert bs['random_seed'] == e['environment']['baseline_resolved_random_seed']
assert (s['random_seed'] == bs['random_seed']) == e['environment']['resolved_random_seed_equal']
config, old_config = load(Path(r['config']['path'])), load(Path(b['config']['path']))
assert sha(Path(r['config']['path'])) == r['config']['sha256']
assert config['cache_salt_full_input'] is True
for candidate in (config, old_config):
    candidate.pop('cache_salt_full_input', None)
    candidate.pop('output_parent')
assert config == old_config
assert r['fixture'] == b['fixture'] and sha(Path(r['fixture']['path'])) == r['fixture']['sha256']
assert sha(Path(e['integrity']['fixture_path'])) == e['integrity']['fixture_sha256']
samples = load(Path(e['integrity']['fixture_path']))['samples'][:4]
key = lambda x: tuple(x[k] for k in e['integrity']['logical_join_fields'])
requests, baseline_requests = lines(run / 'requests.jsonl'), lines(old / 'requests.jsonl')
request_map, baseline_map = {key(x): x for x in requests}, {key(x): x for x in baseline_requests}
assert len(requests) == len(request_map) == len(baseline_map) == 16 and set(request_map) == set(baseline_map)
native_ids = {x['native_request_id'] for x in requests}
assert len(native_ids) == 16 and all(isinstance(x, str) and x for x in native_ids)
request_display = {x[0]: x[1:] for x in e['requests']}
vectors, salts, retractions = {}, [], []
for x in requests:
    sample = samples[x['sample_position']]
    assert [x['sample_position'], x['source_uid'], x['sample_index'], x['input_count'], x['response_count']] == e['integrity']['samples'][x['sample_position']]
    assert x['source_uid'] == sample['source_uid'] and x['sample_index'] == sample['sample_index']
    assert x['input_count'] == len(sample['tokens']) and x['response_count'] == sample['response_length']
    assert x['pair'] == 'B' and x['repetition'] == 0 and x['status'] == 'scored' and x['http_status'] == 200
    assert x['request_id'] == f"{x['phase']}-r{x['repetition']}-s{x['sample_position']}-{x['mode']}"
    expected_salt = 'B:' + x['request_id'] if x['mode'] == 'full_input' else None
    assert x['cache_salt'] == expected_salt
    if expected_salt is not None:
        salts.append(expected_salt)
    start = 0 if x['mode'] == 'full_input' else x['prompt_count'] - 1
    assert x['logprob_start_len'] == start
    expected_count = x['input_count'] if x['mode'] == 'full_input' else x['response_count'] + 1
    assert x['input_token_logprobs_count'] == x['expected_input_token_logprobs_count'] == expected_count
    assert x['first_input_token_logprob'] is None and x['first_input_token_id'] == x['first_requested_input_token_id'] == sample['tokens'][start]
    path = Path(x['completion_scores'])
    assert path == run / 'completion_scores' / (x['request_id'] + '.json') or path.resolve() == (run / 'completion_scores' / (x['request_id'] + '.json')).resolve()
    assert sha(path) == e['completion_sha256'][x['request_id']]
    vector = load(path)
    assert key(vector) == key(x) and vector['request_id'] == x['request_id']
    assert vector['native_request_id'] == x['native_request_id'] == x['meta_info']['id']
    assert vector['token_ids'] == sample['tokens'][-sample['response_length']:]
    assert len(vector['log_probs']) == x['returned_completion_count'] == sample['response_length'] and all(math.isfinite(v) for v in vector['log_probs'])
    assert x['meta_info']['completion_tokens'] == 0 and x['meta_info']['output_token_logprobs']['omitted_array_length'] == 0
    assert [x['native_request_id'], x['sample_position'], x['cache_salt'], x['input_token_logprobs_count'], x['returned_completion_count']] == request_display[x['request_id']]
    current, reference = x['meta_info']['num_retractions'], baseline_map[key(x)]['meta_info']['num_retractions']
    assert type(current) is int and current >= 0 and type(reference) is int and reference >= 0
    retractions.append([x['request_id'], current, reference, current - reference])
    vectors[key(x)] = vector
assert len(salts) == len(set(salts)) == 8 and len({x['request_id'] for x in requests}) == 16
assert sum(len(x['log_probs']) for x in vectors.values()) == 6804
assert retractions == e['retractions']['observations']
assert e['retractions']['unchanged_is_acceptance_condition'] is False
cache = lines(run / 'cache.jsonl')
assert len(cache) == 10 and all(x['status'] == 'flushed' and x['http_status'] == 200 for x in cache)
assert sum(x['phase'] == 'cold' for x in cache) == 8 and sum(x['phase'] == 'warm_stream' for x in cache) == 2
controls, warm = [], []
for x in requests:
    if x['mode'] == 'response_only' or x['phase'] == 'cold':
        reference = baseline_map[key(x)]
        c = _comparison(load(Path(reference['completion_scores'])), vectors[key(x)])
        controls.append([x['request_id'], reference['request_id'], c['relative_error_undefined_count']])
        assert c == {**e['common_comparison'], 'relative_error_undefined_count': controls[-1][-1]}
    if x['phase'] == 'warm_stream' and x['mode'] == 'full_input':
        cold_key = key({**x, 'phase': 'cold'})
        cold = request_map[cold_key]
        c = _comparison(vectors[cold_key], vectors[key(x)])
        warm.append([x['request_id'], cold['request_id'], c['relative_error_undefined_count']])
        assert c == {**e['common_comparison'], 'relative_error_undefined_count': warm[-1][-1]}
assert controls == e['controls'] and len(controls) == 12
assert warm == e['salted_warm_full'] and len(warm) == 4
metadata = load(run / 'runtime_metadata.json')
states = _runtime_metadata_states(metadata['server_info'])
raw = metadata['server_info']['internal_states'][0]['mamba_runtime_metadata']
assert metadata['status'] == 'collected' and len(states) == 1 and raw['rank'] == e['runtime_metadata_presence']['rank']
assert len(raw['rows']) == 16293
explicit = set()
for _, _, fields in raw['rows']:
    f = dict(fields)
    explicit.update([f['rid']] if 'rid' in f else (f.get('rids') or []))
assert explicit & native_ids == native_ids and explicit - native_ids == set()
for name, expected in e['raw_sha256'].items():
    assert sha(base / name) == expected
print(json.dumps({'verification': 'PASS', 'pair': 'B', 'requests': 16, 'flushes': 10, 'unsalted_response_controls_exact': 8, 'salted_cold_full_controls_exact': 4, 'salted_warm_full_exact': 4, 'salted_warm_full_max_abs': 0.0, 'salted_warm_full_max_defined_rel': 0.0, 'salted_warm_full_undefined_counts': [3, 5, 4, 4], 'resolved_random_seed_equal': False, 'isolation': e['outcome']['checkpoint_isolation'], 'full_chunk_plan': e['outcome']['full_chunk_plan_comparison'], 'formal_hold_lifted': False}, sort_keys=True))
```

Syntax-only command:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
import json
p = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_cache_salt_native_B_results.md')
code = p.read_text().split('<!-- verification-python -->\n```python\n', 1)[1].split('\n```', 1)[0]
compile(code, str(p), 'exec')
json.loads(Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-cache-salt-probe-20261111/native-verification-B-controls.json').read_text())
print('SYNTAX PASS')
PY
```

Whitespace commands:

```bash
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_cache_salt_native_B_results.md
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-cache-salt-probe-20261111/native-verification-B-controls.json
```

Historical numerical validation before r2: controls8+4, warm4, max abs/defined rel0, undefined3/5/4/4; raw seed inequality retained. **Observed numerical replay: PASS**, including raw SHA256 recheck; **syntax: `SYNTAX PASS`**; **whitespace: no diagnostics**. The numerical replay above now prints current scoped qualification from the evidence JSON; it was not rerun for this JSON-reference-only follow-up. `--no-index` exit1 for a new-file difference is not an exit0 claim. No successful process exit is substituted for actual comparisons.

Historical numerical replay output before r2 (the old pending state is not the current qualification):

```json
{"flushes": 10, "formal_hold_lifted": false, "full_chunk_plan": "PENDING", "isolation": "PENDING", "pair": "B", "requests": 16, "resolved_random_seed_equal": false, "salted_cold_full_controls_exact": 4, "salted_warm_full_exact": 4, "salted_warm_full_max_abs": 0.0, "salted_warm_full_max_defined_rel": 0.0, "salted_warm_full_undefined_counts": [3, 5, 4, 4], "unsalted_response_controls_exact": 8, "verification": "PASS"}
```

### Affected follow-up: JSON-reference replay only

This command reads the completed primary JSONs and existing server-info JSON; it does not rerun the inspector, source qualification, numeric probe or platform operations. It checks retained receipt identities/scalars and the scope distinction, without repeating raw checkpoint joins.

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
p = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_cache_salt_native_B_results.md')
code = p.read_text().split('<!-- inspection-reference-python -->\n```python\n', 1)[1].split('\n```', 1)[0]
exec(compile(code, str(p), 'exec'))
PY
```

<!-- inspection-reference-python -->
```python
from pathlib import Path
import hashlib, json, platform
base = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-cache-salt-probe-20261111')
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
e = load(base / 'native-verification-B-controls.json')
assert platform.python_version() == '3.10.6'
ref = e['completed_inspector_reference']
assert sha(Path(ref['path'])) == ref['sha256']
assert sha(Path(ref['original_scope_report_path'])) == ref['original_scope_report_sha256']
r2 = load(Path(ref['path']))
assert r2['pair'] == 'B' and r2['output_dir'] == e['run_path'] and r2['baseline_dir'] == e['baseline_path']
assert r2['cpu_verdict'] == ref['cpu_verdict'] == 'PASS' and not r2['errors']
for field in ('source_controls', 'protocol', 'vector_controls'):
    assert r2[field]['status'] == 'PASS'
assert len(r2['vector_controls']['cases']) == ref['vector_control_count'] == 12
assert load(Path(ref['original_scope_report_path']))['cpu_verdict'] == 'FAIL'
scope = r2['scopes'][0]
assert scope['rank'] == ref['rank'] and scope['process_id'] == 396
isolation = scope['isolation']
assert isolation['binding_status'] == ref['checkpoint_binding_status'] == 'PASS'
assert isolation['ordinary_joined'] == len(isolation['joins']) == ref['unique_checkpoint_bindings'] == 165
assert isolation['status'] == ref['aggregate_geometry_status'] == 'FAIL'
target = isolation['full_input_isolation']
assert target['status'] == ref['full_input_isolation_status'] == 'PASS'
assert target['target_rid_count'] == target['covered_rid_count'] == ref['target_rid_count'] == 8
assert target['ordinary_joined'] == ref['full_input_ordinary_joined'] == 100 and target['failed_joins'] == 0
assert set(target['target_rids']) == {x[1] for x in e['requests'] if x[0].endswith('-full_input')}
observations = isolation['control_observations']
assert observations['status'] == ref['response_geometry_status'] == 'FAIL'
assert observations['ordinary_joined'] == ref['response_ordinary_joined'] == 65 and observations['failed_joins'] == ref['response_geometry_failed'] == 3
assert ref['response_geometry_is_isolation_gate'] is False and 65 - 3 == ref['response_geometry_passed'] == 62
assert scope['chunks']['status'] == ref['chunk_status'] == 'PASS'
chunks = r2['chunk_tracking_observations']
assert len(chunks) == ref['chunk_comparison_count'] == 16
assert sum(x['candidate']['chunk_count'] for x in chunks) == ref['complete_chunk_count'] == 169
assert sum(x['initial_prefix_equal'] is True for x in chunks) == ref['initial_prefix_exact_count'] == 16
assert sum(x['chunk_tracking_equal'] is True for x in chunks) == ref['chunk_tracking_exact_count'] == 16
warm = sorted(r2['warm_full_vs_own_cold'], key=lambda x: x['logical_key'][2])
assert len(warm) == e['outcome']['salted_warm_full_exact'] == 4
assert [x['comparison']['relative_error_undefined_count'] for x in warm] == [3, 5, 4, 4]
for x in warm:
    assert x['comparison'] == {**e['common_comparison'], 'relative_error_undefined_count': x['comparison']['relative_error_undefined_count']}
terminal_ref = e['terminal_replica_reference']
assert sha(Path(terminal_ref['path'])) == terminal_ref['sha256']
terminal = load(Path(terminal_ref['path']))
assert terminal['job'] == e['job'] and terminal['pair'] == 'B' and terminal['status']['phase'] == 'Succeeded'
container = terminal['status']['containerStatuses'][0]
assert container['state']['terminated']['reason'] == 'Completed' and container['state']['terminated']['exitCode'] == 0 and container['restartCount'] == 0
assert container['imageID'] == terminal_ref['imageID'] == e['environment']['image']
assert container['image'] == terminal_ref['container_image_field'] and container['ready'] is False and container['started'] is False
info = load(Path(e['run_path']) / 'server_info.json')['get_server_info']
audit = e['source_rng_audit']
assert info['random_seed'] == audit['resolved_random_seed'] == 263946245
assert audit['baseline_resolved_random_seed'] == e['environment']['baseline_resolved_random_seed'] == 596871011
assert info['enable_mamba_cache_stochastic_rounding'] is False and info['enable_dynamic_chunking'] is False
assert audit['same_rng_claimed'] is False and audit['seed_hard_gate_added'] is False and e['outcome']['seed_hard_gate_added'] is False
print(json.dumps({'verification': 'PASS_JSON_REFERENCE_ONLY', 'cpu_inspector': 'PASS', 'checkpoint_bindings': 165, 'target_rids': 8, 'target_joins': 100, 'target_failed': 0, 'unsalted_geometry_failed': 3, 'unsalted_geometry_is_gate': False, 'complete_chunks': 169, 'chunk_comparisons_exact': 16, 'controls_exact': 12, 'warm_full_exact': 4, 'warm_zero_reference_undefined': [3, 5, 4, 4], 'scope': 'TP0_ONLY', 'seed_hard_gate_added': False, 'resolver_dispatch_source': 'PENDING_0GPU', 'formal_hold_lifted': False}, sort_keys=True))
```

Expected affected checks: valid own/primary JSON and hashes, target gate8RIDs/100joins PASS0failed while unsalted geometry3FAIL remains non-gating,169chunks/16exact comparisons,12controls/4warm unchanged, TP0-only/no seed hard gate, terminalCompleted/exit0/restart0. **Observed: PASS_JSON_REFERENCE_ONLY** with exact output below; both owned-file whitespace checks produced no diagnostics (expected new-file `--no-index` exit1). No inspector/source/raw/numerical/platform rerun occurred for this reference update.

```json
{"checkpoint_bindings": 165, "chunk_comparisons_exact": 16, "complete_chunks": 169, "controls_exact": 12, "cpu_inspector": "PASS", "formal_hold_lifted": false, "resolver_dispatch_source": "PENDING_0GPU", "scope": "TP0_ONLY", "seed_hard_gate_added": false, "target_failed": 0, "target_joins": 100, "target_rids": 8, "unsalted_geometry_failed": 3, "unsalted_geometry_is_gate": false, "verification": "PASS_JSON_REFERENCE_ONLY", "warm_full_exact": 4, "warm_zero_reference_undefined": [3, 5, 4, 4]}
```

## 1. 规划完成情况

**汇总：** PASS5｜BLOCKED/FAILED/SKIPPED1｜TODO1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| B retained execution/source/16requests/10flushes/salt/placeholder/retractions | PASS |actual4H800，6+16 source字节与baseline一致；6+6 Git blobs固定；strict retractions32receipts。 |
| B numerical controls及salted warm-full | PASS |8+4controls exact；4warm-full对own cold-full exact；零reference仍undefined。 |
| B owned报告/evidence | PASS |仅两份新文件；raws保留，不stage/commit。 |
| target-only checkpoint isolation | PASS |r2 TP0：165bindings PASS，8salted full RIDs/100joins PASS0failed；response3FAIL不是gate。 |
| 完整chunk-plan比较 | PASS |r2：169complete chunks，16/16initialprefix及chunk/tracking exactbaseline，TP0-only。 |
| resolver/worker-dispatch source | TODO |primary0GPUcollector待完成；seed差异保留，无same-RNG/seed hard gate。 |
| formal04/05 | BLOCKED |required acceptance尚未完成，无因果/rootfix/perf/formalPASS。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次B controls委托至r2-reference follow-up交付｜**当前前沿：** primary归档B数值与TP0-qualified r2证据；接收pending0GPUsourcecollector，不启动新GPU。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR |只新增所需两份证据，沿用existing comparison，无新harness/sourcequal tests。 |
| D2 细节反复重试 | CLEAR |无native重试或行为修复。 |
| D3 支线问题修补 | CLEAR |RNG/sourceaudit只记录；未改seed/config，不添加hardgate或调查历史因果。 |
| D4 可并行任务停滞 | CLEAR |B直接交付；A与inspector独立ownership不等待。 |
| D5 超范围镀金 | CLEAR |不增加tolerance/full-v-response gate或formal策略。 |
| D6 分析空转 | CLEAR |12controls/4warm保持；r2只读取completed JSON字段，不重复rawjoins/inspector执行。 |
| D7 路线违背 | CLEAR |无GPU/platform/auth/SSH/query/poll/delegation；raws与hold保留。 |

**文档检查：** target-only gate与response geometry observations区分明确；旧false-scope FAIL保留，r2 scopedPASS并不改科学条件。本分工不修改spec/tickets/其他文档；primary同步phase状态。
**归因：** 无执行偏离；不把aggregate geometry FAIL擦掉，不把seed差异/缺失source隐写为same-RNG或新增hardgate。

## 3. 纠正建议

**分支：** A：spec/tickets无需本分工改动；先保留原始差异与未完成验收。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. primary归档两份B文件 → 完成标志：12controls/4warm exact、target100PASS、response3non-gating FAIL、169chunks/16exact及原false-scope报告同时保留，不写成rootfix/formalPASS。
2. primary接收pending0GPUresolver/worker-dispatch sourcecollector → 完成标志：缺失source有独立receipt后再更新sourceaudit；保留resolved seeds263946245/596871011，不添加seed hardgate或GPU重跑。

## 4. 最值得关注的 3 点

1. 12controls与4salted warm-full全部exact，max abs/defined rel0，undefined counts保留；unsalted warm原drift未改。
2. r2 target-only isolation/fullchunk已qualified TP0-only；response3FAIL非gate，原FAIL不删。缺失resolver/worker-dispatch source仍pending0GPU。
3. 只交付两份B文件；A/inspector不碰，raws未改，不stage/commit，formalhold未解除。
