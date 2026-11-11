## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Verify retained first B coherence attempt against the accepted original metadata baseline; retain Failed/readback failure, exact scoring parity, source/R3 linkage and physical/numeric limitations. |
| 2026-11-11 | Primary accepts bounded retained scoring/source/CPP controls only; auxiliary capture failure and all physical/numeric/formal holds remain unchanged. |
| 2026-11-11 | Primary independently reruns the frozen verifier and confirms retained-artifact equality and all bounded control verdicts. |

# Retained KV coherence native results — B

TaskID: `profile-kv-coherence-native-B-20261111`.

**PRIMARY ACCEPTED: bounded retained scoring/source/CPP controls only. Scoring equivalence PASS; native attempt/readback FAIL; physical OLD and KV numerical acceptance UNVERIFIED; formal04/05 HOLD.** The original Failed attempt is retained unchanged. No platform, authentication, SSH, GPU, native library load/build or new serving execution was performed by this verifier. Ownership is limited to this report and [native-verification-B.json](evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-B.json).

## Results and acceptance boundaries

Primary independently reran the verifier below with `timeout 60s /usr/bin/python3 -B`. Its retained JSON equality check passed: 16 scored requests, 6,804 exact values, 10 flushes, zero retractions/identity errors, 97 source archive pairs and 35-source R3 composition. The verifier explicitly retained native-attempt FAIL, physical/KV UNVERIFIED and formal HOLD.

Run: `evidence/teacher-scoring-kv-coherence-probe-20261111/native/B/admission-B-r1`.
Baseline: `evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1`, accepted in [the original metadata B report](test_report_2026-11-11_runtime_metadata_native_results.md).

| Requirement | Observed result | Verdict |
| --- | --- | --- |
| Logical completion vectors | 16/16 exact; 6,804 finite values; max absolute error 0; max defined relative error 0; 64 zero-reference positions have undefined relative error | PASS |
| Identity, responses and cache | 16 unique logical cases and native RIDs; HTTP200/scored16; response-tail IDs/counts exact; retractions0; 10 HTTP200 successful flushes | PASS |
| Original numerical differences | All8 retained comparison groups equal baseline; own cold4/4 exact, warm1/4 exact | PASS reproduction; FAIL warm correctness |
| Frozen scoring source | 8/8 native scoring identities match Git `b9e1ebb64725b0998aa6df57919bd8bfc6f2e9aa`, not mutable working-tree bytes | PASS identity |
| Source archives | FP32 6, metadata16, CPP WIT35, coherence40: 97 before/after pairs checked; exact qualified composition/rewrite and all observed hashes | PASS source only |
| Selected R3 | Actual nested build receipt SHA `91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7`; qualification receipt/library/hash and 35 source identities agree | PASS retained linkage; prior CPU acceptance unchanged |
| Private package/runtime | Whole private-package staging receipt, private source paths and7 runtime/archive overlaps agree; four retained actual H800 rows | PASS recorded provenance; not independent all-TP attestation |
| Optional ordinary CPP witness | 1,690 unique identity joins,169 chunks,16 response-bound RIDs,10 FULL layers; native stream equals Torch stream | PASS bounded TP0 CPP witness only |
| Independent readback | HTTP200 but auxiliary validation failed; initial/final responding collector returns identical preallocation error | FAIL |
| Original OLD callback, stream S,7,955 FULL binding, physical indices and KV values | No collector topology, banks, completion count, OLD fragments or KV summaries returned | UNVERIFIED, not accepted |
| Numerical cause/fix, race/all-TP, performance and formal200 | No new evidence settling these criteria | UNVERIFIED; formal HOLD |

Relative error is `abs(candidate-reference)/abs(reference)` only for nonzero reference; exact zero/zero remains undefined, never relative error0. `accepted=null` in original numerical receipts remains unchanged; exact baseline reproduction does not imply mathematical correctness.

### Exact case coverage and differences

Cases are joined by `(pair, phase, mode, source_uid, sample_index, repetition)`, never request chronology, filename order or pointer adjacency. Each of `cold` and `warm_stream`, repetition0, contains both `full_input` and `response_only` for positions0–3. Exact request IDs, new response-bound RIDs and per-vector undefined counts are in the JSON. Original UID prefix is `00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6`.

| Position | UID suffix | Original index | Input / response tokens | Cold zeros, each mode | Warm zeros full / response |
| --- | --- | --- | --- | --- | --- |
| 0 | `:5:123` | 1693 | 97365 / 734 | 3 | 3 / 3 |
| 1 | `:5:125` | 1694 | 98312 / 246 | 5 | 5 / 5 |
| 2 | `:5:127` | 1695 | 98942 / 431 | 4 | 4 / 3 |
| 3 | `:5:129` | 1696 | 99074 / 290 | 4 | 5 / 4 |

Own full-input reference versus response-only: cold0–3 and warm0 exact; warm1 max abs `2.9801958589814603e-06`, defined rel `0.3055551434731875`, undefined5; warm2 `0.33083581924438477` / `10.83576074484674` /4; warm3 `0.24397611618041992` / `2.1428543402212714` /5. No tolerance was introduced.

| Position | Warm candidate | Max abs versus own cold full | Max defined rel | Undefined |
| --- | --- | --- | --- | --- |
| 0 | full / response | 0 / 0 | 0 / 0 | 3 / 3 |
| 1 | full | 4.529893885774072e-06 | 0.31249958276708867 | 5 |
| 1 | response | 3.4569602576084435e-06 | 0.1071427598289923 | 5 |
| 2 | full | 0.43444275856018066 | 12.818066557496891 | 4 |
| 2 | response | 0.5321998596191406 | 12.296145876202624 | 4 |
| 3 | full | 0.4388699531555176 | 1.4485754510908142 | 4 |
| 3 | response | 0.3178117275238037 | 2.99999928474422 | 4 |

Both independently flushed cold modes were recomputed as references; warm-full is descriptive, not an oracle. All24 individual comparison contracts embedded in the8 groups match recomputation and original groups exactly.

## Actual attempt, runtime and retained failure

Primary-retained [terminal admission](evidence/teacher-scoring-kv-coherence-probe-20261111/admission-B-r1.terminal.json) and [terminal platform B](evidence/teacher-scoring-kv-coherence-probe-20261111/terminal-platform-B.json) agree: job `exp-1111-162637-872429`, UID `83dc1dc7-6830-443b-a8a4-6795cc385d34`, creator `i-fengyicheng`, **Failed at2026-11-11T08:40:33Z**. Actual container was **Error/exit1/restart0**, started08:34:28Z, finished08:40:31Z. The retained terminal queue annotation is historical, not an explanation for the completed16 requests. No imageID/node/resource details absent from that terminal receipt are invented.

Business `result.json`: `native_measurements_completed=true`, `cleanup_completed=true`, `status=failed`, `performance_accepted=false`, `numerical_acceptance=null`, server alive before cleanup (`server_returncode_before_cleanup=null`), shutdown returncode−9. Native scoring succeeded, then independent readback validation failed with:

```text
RuntimeError: Scoring completed; independent runtime metadata readback failed: KV coherence diagnostic unverified: Responding collector unavailable; no device readback
preallocation / ValueError: Collector actual graph/page/memory/cache config differs from qualified WIT
```

Both initial non-draining and final explicit-draining server receipts contain the same error for process340; no topology/banks were emitted. Missing KV is **not** a math failure or a new RCA of the training root failure. The source RCA is independently owned/closed: the supplied closure identifies raw sealed `ServerArgs.page_size=None` versus resolved1, not later mutation. This report verifies original frozen bytes only, does not duplicate or repair that guard. Primary's later launcher `JobStop` after finished cleanup is not the initiating error; launcher lifecycle evidence is primary-owned.

Worker `/opt/sglang/bin/python3` **3.12.16**, Torch **2.14.1+cu130**, SGLang **0.5.24.dev80+g056f871**; four retained `NVIDIA H800, 81559 MiB, 570.124.06` rows. Local verification `/usr/bin/python3` **3.10.6**, Linux, no conda activation. Teacher path `/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-35B-A3B/model`; config SHA `5e4d7f74fec2f360eb9cfbfcd6ec0c4c76e684d3a11caaed259d9fd9bfbc7944`, index SHA `d8d0b7ca4e61ae107e3e87a3ff21136b3ac7c789e64bb24267227ca804e04205`. These are manifest identities, not whole-weight checksums. Pinned image165ff0be is the allocation input, not an independently supplied terminal imageID.

Teacher argv exactly matches baseline except `--dist-init-addr`: TP4, BF16, context131072, static memory0.85, concurrency1, prefill8192, graphs disabled, deterministic inference, FA3 and Triton linear prefill. Existing seeds/arguments/payloads were not changed. Resolved generated seed differs across attempts and is not an RNG equivalence proof; it is recorded in JSON. No HF/eval, cache salt, dtype, backend or scientific change is made here.

Private package root `/var/tmp/teacher-scoring-kv-ly3630ga/kv-coherence-runtime/sglang`; original source package `/sgl-workspace/sglang/python/sglang` was not selected as the staged target. Nested native observer names the production module and private same-name library, SHA `0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba`. Receipt, retained ELF and qualification linkage are checked without loading that library. Native source helper is fixed to Git `17cb6fc66fa8b5e866c0c83d5f5c93cf971ac898`; source/CPU/WIT acceptance is not reset. **A staged path/hash does not prove execution of original OLD callback, GIL/thread/alias/CUDA stream or physical data.** Original bundled binary source commit remains UNVERIFIED. Neither absent invalidation marker nor accepted bounded CPU tests closes these native requirements.

Optional WIT uses the entire exact key `(RIDs, CPU prefix lengths, CPU extend lengths, K pointer, V pointer, writer-location pointer, complete writer-location descriptor)`. All1,690 stream and1,690 terminal keys are individually unique and have exactly one counterpart. All169 explicit scheduler chunk keys cover the16 response-bound RIDs with10 FULL layers per chunk. CPP native/Torch stream is `1342830624`. No adjacency, row sequence or pointer alone establishes a join. Final metadata has19,713 rows, process340, TP0/PP0/DP-null (legal DP1), sequence354–20066; initial353 startup rows are separate. CPP descriptors/host context are not physical contents or device completion. No prefix-valid KV Triton receipt, original OLD stream S, topology/capture/7,955 binding or all-TP proof is inferred.

## Commands and reproducible verification

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Historical worker command is retained verbatim in `admission-B-r1.json.worker_command`; **not rerun**. Existing timeout3600/cleanup90 and outer launcher lifetime are unchanged. Local inspections used `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B` with60-second tool limits, exact B/baseline scope and read-only `git show`. No global5,501/621-file rehash or broad tests were run.

Exact final command (only the read-only code below):

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
p = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_B_results.md')
code = p.read_text().split('<!-- verification-python -->\n```python\n', 1)[1].split('\n```', 1)[0]
exec(compile(code, str(p), 'exec'))
PY
```

<!-- verification-python -->
```python
from pathlib import Path
from collections import Counter
import hashlib, json, math, platform, subprocess, types
from tests.manual.agent_opd import sglang_mamba_snapshots as fp
from tests.manual.agent_opd import sglang_mamba_runtime_metadata as md
from tests.manual.agent_opd import sglang_kv_streams as wit
from tests.manual.agent_opd.probe_teacher_scoring import _comparison

task = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
evidence = task / 'evidence/teacher-scoring-kv-coherence-probe-20261111'
run = evidence / 'native/B/admission-B-r1'
baseline = task / 'evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1'
load = lambda p: json.loads(p.read_text())
lines = lambda p: [json.loads(x) for x in p.read_text().splitlines()]
sha = lambda content: hashlib.sha256(content).hexdigest()
identity = lambda p: {'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
git = lambda commit, name: subprocess.check_output(['git', 'show', f'{commit}:{name}'], timeout=30)
commit = 'b9e1ebb64725b0998aa6df57919bd8bfc6f2e9aa'
rust_commit = '17cb6fc66fa8b5e866c0c83d5f5c93cf971ac898'
r, p, old = load(run / 'result.json'), load(run / 'preload.json'), load(baseline / 'result.json')
assert r['pair'] == 'B' and r['native_measurements_completed'] and r['cleanup_completed']
assert r['status'] == 'failed' and r['performance_accepted'] is False and r['numerical_acceptance'] is None
assert r['server_returncode_before_cleanup'] is None and r['server_shutdown_returncode'] == -9
terminal = load(evidence / 'admission-B-r1.terminal.json')
native_platform = load(evidence / 'terminal-platform-B.json')
assert terminal['job'] == native_platform['job'] == r['job'] == 'exp-1111-162637-872429'
assert terminal['uid'] == native_platform['uid'] == '83dc1dc7-6830-443b-a8a4-6795cc385d34'
assert terminal['creator'] == native_platform['creator'] == 'i-fengyicheng'
assert terminal['status'] == native_platform['status']
assert terminal['status']['phase'] == 'Failed' and terminal['status']['finishTime'] == '2026-11-11T08:40:33Z'
container = native_platform['replicas'][0]['containers'][0]
assert container['restart_count'] == 0 and container['state']['terminated']['exitCode'] == 1
assert container['state']['terminated']['reason'] == 'Error'
assert p['runtime'] == r['runtime'] and len(r['runtime']['gpu_devices']) == 4
assert all(x == 'NVIDIA H800, 81559 MiB, 570.124.06' for x in r['runtime']['gpu_devices'])
assert (r['runtime']['python'], r['runtime']['torch'], r['runtime']['sglang']) == ('3.12.16', '2.14.1+cu130', '0.5.24.dev80+g056f871')
for name, observed in r['native_scoring_sources'].items():
    content = git(commit, name)
    assert len(content) == observed['bytes'] and sha(content) == observed['sha256'], name
assert len(r['native_scoring_sources']) == 8
blob = git(commit, 'tests/manual/agent_opd/sglang_kv_coherence.py')
frozen = types.ModuleType('frozen_coherence_B')
frozen.__file__ = 'tests/manual/agent_opd/sglang_kv_coherence.py'
exec(compile(blob, frozen.__file__, 'exec'), frozen.__dict__)
runtime = ('"""CUDA-only opt-in FULL KV observer; no cache decisions or new waits."""\n'
           'import math\nimport os\nimport threading\n\n'
           + blob.decode().split('# BEGIN INSTALLED RUNTIME\n', 1)[1].split('# END INSTALLED RUNTIME', 1)[0]).encode()
frozen._runtime_source = lambda: runtime
gate = frozen.compare_completion_vectors(run, baseline)
assert gate['all16_6804_exact'] and gate['vectors'] == 16
assert (gate['baseline_values'], gate['candidate_values']) == (6804, 6804)
requests, cache, fixture = lines(run / 'requests.jsonl'), lines(run / 'cache.jsonl'), load(Path(r['sample_manifest']['source_fixture']['path']))['samples'][:4]
assert len(requests) == 16 and len({x['native_request_id'] for x in requests}) == 16
assert len(cache) == 10 and all(x['status'] == 'flushed' and x['http_status'] == 200 for x in cache)
vectors, request_rows = {}, []
for request in requests:
    sample = fixture[request['sample_position']]
    v = load(run / 'completion_scores' / (request['request_id'] + '.json'))
    assert request['status'] == 'scored' and request['http_status'] == 200 and request['repetition'] == 0
    assert request['source_uid'] == sample['source_uid'] and request['sample_index'] == sample['sample_index']
    assert v['native_request_id'] == request['native_request_id'] == request['meta_info']['id']
    assert all(v[k] == request[k] for k in ('pair', 'phase', 'mode', 'source_uid', 'sample_index', 'repetition'))
    assert v['token_ids'] == sample['tokens'][-sample['response_length']:]
    assert len(v['log_probs']) == sample['response_length'] == request['returned_completion_count']
    assert all(math.isfinite(x) for x in v['log_probs'])
    assert request['input_token_logprobs_count'] == request['expected_input_token_logprobs_count']
    assert request['meta_info']['num_retractions'] == 0
    assert request['completion_token_id_mismatches'] == request['nonfinite_log_prob_positions'] == []
    vectors[request['request_id']] = v
    comparison = next(x for x in gate['comparisons'] if all(x['case'][k] == request[k] for k in x['case']))
    request_rows.append([request['request_id'], request['native_request_id'], request['sample_position'], request['sample_index'], request['source_uid'], len(v['log_probs']), comparison['relative_error_undefined_count']])
assert sum(x[-1] for x in request_rows) == 64
groups = lines(run / 'comparisons.jsonl')
assert groups == lines(baseline / 'comparisons.jsonl') and len(groups) == 8
contracts = 0
for g in groups:
    full, response = vectors[g['full_request_id']], vectors[g['response_request_id']]
    assert _comparison(full, response) == g['full_vs_response_only']
    contracts += 1
    if g['cold_reference']:
        for cold_mode, cold_id in (('full', 'full_request_id'), ('response_only', 'response_request_id')):
            for warm_mode, warm in (('full', full), ('response_only', response)):
                assert _comparison(vectors[g['cold_reference'][cold_id]], warm) == g['cold_reference'][f'cold_{cold_mode}_vs_warm_{warm_mode}']
                contracts += 1
assert contracts == 24
def without_address(argv):
    i = argv.index('--dist-init-addr')
    return argv[:i] + argv[i + 2:]
assert without_address(r['argv']) == without_address(old['argv'])
assert r['runtime']['model_manifest_identity'] == old['runtime']['model_manifest_identity']
for name in ('fixture', 'config'):
    assert identity(Path(r[name]['path'])) == r[name]
assert identity(Path(r['sample_manifest']['source_fixture']['path'])) == r['sample_manifest']['source_fixture']
stages = {}
for scope, owner in (('source_preflight', fp), ('runtime_metadata_source_preflight', md), ('kv_store_stream_source_preflight', wit), ('kv_coherence_source_preflight', frozen)):
    path, receipt = run / scope, r[scope]
    assert p[scope] == receipt and lines(path / 'preflight.jsonl') == [receipt]
    manifest, expected = load(path / 'source_manifest.json'), owner.source_manifest()
    for key in expected:
        if key != 'files':
            assert manifest[key] == expected[key], (scope, key)
    for name, pins in expected['files'].items():
        assert all(manifest['files'][name][key] == value for key, value in pins.items()), (scope, name)
    files = receipt.get('files', receipt.get('observed_after_sha256'))
    if scope != 'kv_coherence_source_preflight':
        assert manifest['files'] == files
    for name in files:
        before, after = (path / 'before' / name).read_bytes(), (path / 'after' / name).read_bytes()
        if scope == 'kv_coherence_source_preflight':
            assert after == (runtime if name == 'srt/kv_coherence.py' else frozen._rewrite(name, before))
            assert sha(after) == receipt['observed_after_sha256'][name]
            if name == 'srt/kv_coherence.py':
                assert before == b''
            elif name in expected['additional_native_sha256']:
                assert sha(before) == expected['additional_native_sha256'][name]
            else:
                assert before == (run / 'kv_store_stream_source_preflight/after' / name).read_bytes()
        else:
            item = files[name]
            assert sha(before) == item['before_sha256'] == receipt['observed_before_sha256'][name]
            assert sha(after) == item['after_sha256'] == receipt['observed_after_sha256'][name]
            if scope == 'runtime_metadata_source_preflight':
                assert after == (md._RECORDER_SOURCE.encode() if item.get('created') else md._rewrite(name, before))
            elif scope == 'kv_store_stream_source_preflight':
                wit._qualified_baseline(name, before, manifest['files'][name])
                assert after == wit._rewrite(name, before)
    stages[scope] = {'archive_pairs': len(files), 'manifest': identity(path / 'source_manifest.json'), 'receipt': identity(path / 'preflight.jsonl')}
assert [x['archive_pairs'] for x in stages.values()] == [6, 16, 35, 40]
native = r['kv_coherence_source_preflight']['native_observer']
assert load(run / 'kv_coherence_source_preflight/native_observer/preflight.json') == native
build_path = Path(native['build_receipt'])
assert sha(build_path.read_bytes()) == native['build_receipt_sha256'] == '91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7'
build = load(build_path)
assert build['status'] == build['qualification']['status'] == 'PASS'
assert build['module'] == native['module'] and build['features'] == native['features'] == ['python-extension']
assert git(commit, 'tests/manual/agent_opd/sglang_rust_kv_observer.py') == git(rust_commit, 'tests/manual/agent_opd/sglang_rust_kv_observer.py')
assert identity(Path(build['qualification_receipt']['path'])) == build['qualification_receipt']
library = Path(build['observer']['path'])
assert library.read_bytes().startswith(b'\x7fELF') and sha(library.read_bytes()) == native['compiled_sha256'] == build['observer']['sha256']
assert len(native['composition']) == 35
for name, observed in native['composition'].items():
    content = (run / 'kv_store_stream_source_preflight/after' / name).read_bytes()
    assert len(content) == observed['bytes'] and sha(content) == observed['sha256']
package = r['kv_coherence_package']
assert native['package_root'] == r['kv_coherence_source_preflight']['package_root'] == package['package_root']
assert native['binary_target'].startswith(package['package_root'] + '/')
assert package['source_package_root'] != package['package_root']
assert package['import_origin'] == package['package_root'] + '/__init__.py'
overlap = set(r['runtime']['sglang_sources']) & set(r['kv_coherence_source_preflight']['observed_after_sha256'])
assert len(overlap) == 7
for name, observed in r['runtime']['sglang_sources'].items():
    assert observed['path'] == package['package_root'] + '/' + name
    if name in overlap:
        content = (run / 'kv_coherence_source_preflight/after' / name).read_bytes()
        assert len(content) == observed['bytes'] and sha(content) == observed['sha256']
initial = load(run / 'server_info.json')['get_server_info']
readback = load(run / 'runtime_metadata.json')
assert readback['status'] == 'failed' and readback['http']['http_status'] == 200
assert len(initial['internal_states']) == len(readback['server_info']['internal_states']) == 1
state, initial_state = readback['server_info']['internal_states'][0], initial['internal_states'][0]
kv = state['kv_coherence']
assert kv == initial_state['kv_coherence'] and kv['status'] == 'unverified' and kv['numeric_acceptance'] is None
assert kv['errors'] == [{'stage': 'preallocation', 'error_type': 'ValueError', 'message': 'Collector actual graph/page/memory/cache config differs from qualified WIT'}]
assert 'topology' not in kv and 'banks' not in kv and r['kv_coherence']['summaries'] == []
m = state['mamba_runtime_metadata']
assert m['process_id'] == kv['process_id'] == 340 and m['rank']['tp_rank'] == 0 and m['rank']['dp_rank'] is None
rows = m['rows']
assert len(rows) == 19713 and rows[0][0] == 354 and rows[-1][0] == 20066
assert len(initial_state['mamba_runtime_metadata']['rows']) == 353
freeze = lambda value: tuple(map(freeze, value)) if isinstance(value, list) else value
fields_key = ('rids', 'prefix_lens', 'extend_lens', 'k_cache_data_ptr', 'v_cache_data_ptr', 'writer_loc_data_ptr', 'writer_loc')
key = lambda f: tuple(freeze(f[name]) for name in fields_key)
streams, terminals, scheduler = {}, {}, set()
rids = {x['native_request_id'] for x in requests}
for seq, event, fields in rows:
    f = dict(fields)
    assert len(f) == len(fields)
    if event == 'scheduler_track_boundary':
        chunk = (f['rid'], f['prefix_len'], f['extend_len'])
        assert chunk not in scheduler and f['rid'] in rids
        scheduler.add(chunk)
    if event in ('kv_store_stream', 'kv_store_terminal'):
        target = streams if event == 'kv_store_stream' else terminals
        k = key(f)
        assert k not in target and len(f['rids']) == 1 and f['rids'][0] in rids
        target[k] = f
assert streams.keys() == terminals.keys() and len(streams) == 1690
chunks, chunk_layers = Counter(), {}
layers = set()
for k, f in streams.items():
    t = terminals[k]
    assert f['store_kind'] == 'cpp_store_cache' and f['native_stream_scalar_observed'] and f['launch_enqueued']
    assert f['native_actual_stream'] == f['torch_current_raw_stream'] == 1342830624
    assert t['store_kind'] == 'mha_set_kv_buffer_impl' and t['pool_class'][-1] == 'MHATokenToKVPool'
    chunk = (f['rids'][0], f['prefix_lens'][0], f['extend_lens'][0])
    assert chunk in scheduler
    chunks[chunk] += 1
    seen = chunk_layers.setdefault(chunk, set())
    assert t['layer_id'] not in seen
    seen.add(t['layer_id'])
    layers.add(t['layer_id'])
assert len(chunks) == len(scheduler) == 169 and set(chunks.values()) == {10}
assert len(layers) == 10 and {x[0] for x in chunks} == rids
assert all(seen == layers for seen in chunk_layers.values())
selected = ['result.json', 'preload.json', 'requests.jsonl', 'cache.jsonl', 'comparisons.jsonl', 'server_info.json', 'runtime_metadata.json', 'server.log']
snapshot = {
    'schema': 'kv-coherence-native-B-verification-v1', 'task_id': 'profile-kv-coherence-native-B-20261111',
    'modification_history': [{'date': '2026-11-11', 'change': 'Retained B verification; first Failed attempt preserved.'}],
    'run_path': str(run), 'baseline_path': str(baseline), 'job': r['job'], 'uid': terminal['uid'],
    'verdicts': {'scoring_equivalence': 'PASS', 'source_R3_linkage': 'PASS', 'CPP_TP0_witness': 'PASS', 'native_attempt': 'FAIL', 'readback': 'FAIL', 'warm_correctness': 'FAIL', 'original_OLD_S_7955_physical_KV': 'UNVERIFIED', 'root_fix_race_allTP_performance': 'UNVERIFIED', 'formal': 'HOLD'},
    'counts': {'requests_scored': 16, 'completion_values': 6804, 'flushes': 10, 'retractions': 0, 'identity_errors': 0, 'comparison_groups': 8, 'comparison_contracts': 24, 'zero_reference_relative_undefined': 64, 'source_archive_pairs': 97, 'R3_composition': 35},
    'completion_equivalence': {'max_absolute_error': 0.0, 'max_defined_relative_error': 0.0, 'values_exact': True, 'case_columns': ['request_id', 'native_request_id', 'sample_position', 'sample_index', 'source_uid', 'values', 'relative_error_undefined_count'], 'cases': request_rows},
    'raw_files': {name: identity(run / name) for name in selected},
    'score_files': {name: identity(run / 'completion_scores' / (name + '.json')) for name in vectors},
    'baseline_receipts': {name: identity(baseline / name) for name in ('requests.jsonl', 'comparisons.jsonl')},
    'source_stages': stages, 'frozen_native_scoring_commit': commit, 'frozen_rust_source_commit': rust_commit,
    'frozen_rust_helper_sha256': sha(git(rust_commit, 'tests/manual/agent_opd/sglang_rust_kv_observer.py')),
    'original_guard_helper_sha256': sha(blob), 'original_installed_runtime_sha256': sha(runtime),
    'R3': {'build_receipt': identity(build_path), 'qualification_receipt': build['qualification_receipt'], 'observer_library': identity(library), 'composition_count': 35, 'runtime_callback_execution_proven': False},
    'runtime': {'verification_python': platform.python_version(), 'worker_python': r['runtime']['python'], 'worker_executable': r['runtime']['executable'], 'torch': r['runtime']['torch'], 'sglang': r['runtime']['sglang'], 'gpu_devices': r['runtime']['gpu_devices'], 'argv': r['argv'], 'seed': state['random_seed'], 'baseline_seed': load(baseline / 'server_info.json')['get_server_info']['random_seed'], 'private_package_root': package['package_root'], 'runtime_source_archive_overlaps': 7},
    'CPP_witness': {'process_id': 340, 'rank': m['rank'], 'metadata_rows': 19713, 'startup_rows': 353, 'unique_identity_joins': 1690, 'chunks': 169, 'requests': 16, 'FULL_layers': sorted(layers), 'native_and_torch_stream': 1342830624, 'device_completion': 'UNVERIFIED'},
    'readback': {'status': 'FAIL', 'http_status': 200, 'initial_and_final_same_error': True, 'collector': kv, 'topology_captured': False, 'banks_captured': False, 'KV_summaries': [], 'native_measurements_completed': True, 'cleanup_completed': True, 'result_reason': r['reason']},
    'terminal_admission': identity(evidence / 'admission-B-r1.terminal.json'), 'terminal_platform': identity(evidence / 'terminal-platform-B.json'),
    'limits': ['No platform/authentication/GPU/native execution; no staging/commit.', 'No original OLD callback, S stream,7955 binding, physical indices or numeric KV captured.', 'Staged ELF/hash and absent invalidation marker are not runtime physical proof.', 'Original source/CPU/WIT criteria and formal04/05 HOLD unchanged; B has no A200 gate.', 'First4/repetition0 only; no56-request/second-repetition/1024/global/all-TP/race/performance/root-fix acceptance.', 'Guard RCA and post-finish launcher JobStop evidence are independently primary/source-owned.']}
output = evidence / 'native-verification-B.json'
if output.exists():
    assert load(output) == snapshot
    print(json.dumps({'local_verification': 'PASS', **snapshot['counts'], 'max_absolute_error': 0.0, 'max_defined_relative_error': 0.0, 'native_attempt': 'FAIL', 'physical_KV': 'UNVERIFIED', 'formal': 'HOLD'}, sort_keys=True))
else:
    print(json.dumps(snapshot, ensure_ascii=False, indent=2, allow_nan=False))
```

Passing condition: all explicit assertions above,16 exact vectors/6,804 values/identity errors0,8 original groups and24 contracts,97 source pairs,selected R3 linkage and1,690 exact CPP identity joins; separately retain readback/attempt FAIL and physical UNVERIFIED. Final observed values are in the companion JSON. Two initial verification-scaffold assertions incorrectly treated source-helper manifest templates as completed receipts; inspection showed that preparation adds observed before/after SHA fields. The corrected verifier checks template pins, completed receipt equality and actual archived bytes independently. A separate initial overlap-count assumption was corrected from10 to the observed7 explicit matching paths. These were local verifier assumptions, not native/source failures; no raw artifact or guard changed.

Scoped whitespace checks (new files; `--no-index` exit1 indicates a new-file diff, not a validation failure):

```bash
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_B_results.md
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-B.json
```

Observed final command: **local verification PASS**, with independently retained native FAIL/physical UNVERIFIED. Both whitespace checks emitted no diagnostics (expected new-file diff exit1).

```json
{"R3_composition": 35, "comparison_contracts": 24, "comparison_groups": 8, "completion_values": 6804, "flushes": 10, "formal": "HOLD", "identity_errors": 0, "local_verification": "PASS", "max_absolute_error": 0.0, "max_defined_relative_error": 0.0, "native_attempt": "FAIL", "physical_KV": "UNVERIFIED", "requests_scored": 16, "retractions": 0, "source_archive_pairs": 97, "zero_reference_relative_undefined": 64}
```

## 1. 规划完成情况

**汇总：** PASS3｜BLOCKED/FAILED/SKIPPED3｜TODO0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| B原始逻辑向量与请求完整性 | PASS |16/6804 exact，16scored/10flushes，identity errors0 |
| 原始source/R3/private staging与CPP TP0核验 | PASS |冻结Git、97source pairs、35composition、1690身份join |
| 本分工两份产物 | PASS |仅指定report/JSON，等待primary acceptance，无stage/commit |
| B独立collector readback | FAILED |原始preallocation错误，无topology/banks |
| B原生warm正确性 | FAILED |原始warm差异原样复现，无容差/修复 |
| 父任务04/05正式与physical/numeric验收 | BLOCKED |Ticket05要求OLD/physical/RCA/correctness，formal HOLD |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次B-only委托开始至两份核验产物交付｜**当前前沿：** primary接受保留结果；独立source owner完成guard修正，physical/numeric仍未通过。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR |仅settle指定vectors/source/receipt的本地核验，无扩展tests |
| D2 细节反复重试 | CLEAR |manifest新增字段经原始证据定位；无native重试 |
| D3 支线问题修补 | CLEAR |不编辑guard或复制独立RCA，不处理无关问题 |
| D4 可并行任务停滞 | CLEAR |B-only立即交付，不等待A，source修正独立推进 |
| D5 超范围镀金 | CLEAR |仅两个owned artifacts，无新行为/兼容/flags |
| D6 分析空转 | CLEAR |调查输出明确exact/Failed/unverified边界与交付 |
| D7 路线违背 | CLEAR |formal HOLD，原始Failed保留，无GPU/platform/native execution |

**文档检查：** S1–S6均未发现明显缺陷。初读的Initial/PENDING状态已由primary在`requirements.md:3`、`plan.md:3`和`tickets/05-b-full.md:3`更新为terminal Failed/独立parity待acceptance；本分工未改shared docs。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动验收条件。Primary已同步实际Failed状态，parity acceptance归primary。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Primary接受本B核验与独立terminal证据 → 完成标志：两份owned artifacts和Failed/native boundary归档。
2. 并行：独立guard source修正与其受影响核验 ‖ A保留结果核验；本分工不执行或授权新的native attempt。
3. 原有physical/numeric → RCA/minimal fix/warm correctness → fresh independent A‖B200 →06；保留B无A200 gate。

## 4. 最值得关注的 3 点

1.16向量/6804值完全复现baseline，但warm correctness仍FAIL，不能解除formal HOLD。
2.Collector在preallocation前失败，没有OLD/S/7955/topology/banks/KV证据；缺失不等于数学失败。
3.R3/library/source/hash linkage与普通CPP TP0 witness仅关闭各自范围，不替代原始OLD物理与数值验收。
