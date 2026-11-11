## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Verify completed B r3 retained controls, frozen source/build inputs, actual serving receipt and bounded observer/CPP scope; leave physical and K/V numerical interpretation to their independent owner. |
| 2026-11-11 | Record primary ACCEPTED bounded stage and locally verify the subsequently provided terminal-platform receipt only; preserve the initial absent-receipt snapshot and all measured values/limits. |

# KV coherence B r3 retained control results

TaskID: `profile-kv-coherence-native-B-r3-controls-20261111`.

**Primary disposition: ACCEPTED bounded stage.** Primary accepts only the recorded controls/source/build linkage, actual serving file/class/PID identity, insert-OLD OS native thread/Torch S, responding TP0 CPP-only joins and error scope. Physical/KV interpretation, F-S equivalence, race, allTP and formal acceptance are not included. The follow-up below verifies the new retained terminal receipt without rerunning any prior vector/source/CPU/native checks.

**Controls PASS; retained serving binding and insert/OLD callback thread/S scope PASS; original warm correctness FAIL remains. Physical7955 equality, complete physical FRESH/OLD qualification and K/V numerical interpretation are UNVERIFIED/pending independent ownership, not failures from this verification. Formal04/05 HOLD remains.**

Run: `evidence/teacher-scoring-kv-coherence-probe-20261111/native/B/admission-B-r3`, job `exp-1111-194636-897299`.
Original accepted baseline: `evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1`, job `exp-1111-073825-734134`, frozen caller `4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff`. This is the original baseline, not failed coherence r1/r2.
Machine evidence: [native-verification-B-r3.json](evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-B-r3.json).

## Per-gate results and limits

| Gate | Observed result | Verdict / exact scope |
| --- | --- | --- |
| Score controls / identities / shapes |16 vectors,6,804 finite values, exact logical cases, response-tail token IDs and response-bound RIDs; identity errors0 | PASS, original first4/repetition0 only |
| Error metrics | Max abs0, max defined rel0;64 zero-reference positions | PASS; relative error undefined at reference0, including zero/zero |
| Requests/cache |16 HTTP200 scored,10 HTTP200 successful flushes,0 retractions | PASS |
| Original comparison contracts |8 groups byte-identical to original baseline;24 contracts independently recomputed | PASS reproduction, not warm repair |
| Cold/warm full versus response | Cold4/4 exact; warm1/4 exact | Cold PASS; original warm FAIL remains |
| Frozen caller/helper/config |8 active identities matchf8b6b43a;6 original baseline identities match4f1139b0; unchanged config matches027018aa | PASS snapshot identity; no live source execution |
| Generated runtime/source stages |97 before/after pairs:6 FP32,16 metadata,35 WIT,40 coherence; exact owner rewrites and manifests | PASS retained bytes/composition |
| R3/native build inputs/two ELFs |22 baseline and22 observer Rust inputs match pins/candidate; three Python input pins;35 composed identities;R3 SHA91458ef4; observer SHA0dc763cc; baseline SHAfbe6ea7c | PASS retained linkage/build receipts; original bundled source commit UNVERIFIED |
| Actual serving receipt | Initial/final same private module path/hash/3,411,248 bytes/PID350; actual class is module export and matches adapter factory | PASS bounded process receipt, not mapped-ELF measurement |
| Observer insert/OLD thread/S | Two inserts and two warm OLD callbacks have OS native thread350 and Torch current raw stream532178656; RID/P/E match | PASS responding TP0 callback scope; no independent Rust-thread syscall or arbitrary race/GIL proof |
| Ordinary CPP witness |1,690 unique exact stream/terminal joins,169 explicit chunks,16 response-bound RIDs,10 FULL layers each; CPP native scalar=Torch F531885904 | PASS responding process350/TP0 only; no CPP-to-OLD stream equivalence, Triton or all-TP proof |
| Errors independent of bank completion | Initial/final globalerrors0, binding_errornull; independent log marker/error scan0; existing consumer rejects mutated binding errors/identities even with captured/complete receipts; producer error predicate independently rejects capture errors | PASS bounded error controls; absence of a marker is not alias/device proof |
| Business/readback/cleanup | `measurements_completed`, native measurements and cleanuptrue; readbackcollected/HTTP200; server alive before cleanup, shutdown−9 | PASS completed bounded execution, not mathematical/formal acceptance |
| Retained admission terminal | Succeeded/RJobSucceeded at2026-11-11T11:54:54Z, native_execution_succeededtrue, UID8c094c1d-c90e-48e5-be55-76b40125d246 | PASS retained primary receipt only; platform API collection remains primary-owned |
| Subsequently retained terminal platform | Same job/UID/creator/status; image165/local NFS/H800/codesign/nonpreemptible/oneGPU4replica/ownerRefs; Succeeded/Completed exit0/restart0 | PASS local filtered-receipt linkage only; allocation/node label are not physical hardware proof |
| Physical7955/FRESH/OLD/KV/root/performance/formal200 | No physical/numerical metrics read or adjudicated here | UNVERIFIED/pending independent owner; formal HOLD |

Relative error is `abs(candidate-reference)/abs(reference)` only at nonzero references; no epsilon or tolerance. Native RIDs differ across runs: score cases are joined by `(pair, phase, mode, source_uid, sample_index, repetition)` and each run's RID is tied to its own request/meta/completion record, never to chronology. Response lengths734/246/431/290 correspond to indexes1693–1696 and original UIDs ending`:5:123/:5:125/:5:127/:5:129`.

Original warm full-versus-response differences remain exactly unchanged: sample0 exact; sample1 maxabs`2.9801958589814603e-06`,definedrel`0.3055551434731875`;sample2 maxabs`0.33083581924438477`,definedrel`10.83576074484674`;sample3 maxabs`0.24397611618041992`,definedrel`2.1428543402212714`. Original `accepted=null` fields remain. These are score comparisons, not K/V metrics, a cause, or a new tolerance.

## Serving identity and observer scope

Private package: `/var/tmp/teacher-scoring-kv-n9dc7xtg/kv-coherence-runtime/sglang`; source package: `/sgl-workspace/sglang/python/sglang`. Whole-package staging/import-origin receipts agree.38 recorded runtime source paths use the private package;7 retained archive hash overlaps agree. The package preparation's `serving_native_origin_sha=PENDING` and native preflight's CUDA qualificationPENDING are historical preparation fields. Actual runtime `native_binding` is checked separately, not inferred from those fields.

Actual module: `sglang.srt.mem_cache.rust_tree_core.mem_cache`; path: private package + `/srt/mem_cache/rust_tree_core/mem_cache.cpython-312-x86_64-linux-gnu.so`; SHA`0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba`;3,411,248 bytes. Receipt names `RustUnifiedTreeCoreBinding`, class_module`builtins`, class_is_module_attributetrue, factory_class_matchestrue, PID350. Source producer reads `type(tree_core)._bindings`, `type(tree_core._binding)` and `tree_core._binding_class()`; this checks actual instance/export/factory class identity, not merely a configured class label (`tests/manual/agent_opd/sglang_kv_coherence.py:204–229`). Existing after-all16 consumer ties path/hash/PID/exacttrue flags to the staged receipt (`tests/manual/agent_opd/probe_teacher_scoring.py:556–625`).

**Bounded assumption:** module SHA/size are bytes read from resolved `bindings.__file__` after import. No process maps, mapped ELF bytes or new buildID demand were introduced. Acceptance assumes that file still represents the imported library at receipt time; file/mapping replacement is not independently excluded. Only the responding scheduler is attested, not all four TP processes.

Cold `cold-r0-s2-full_input`,RID`011d6bcddb7140a38a4667cbcb0fbf30`:P90112/E98304/Q90112,node67,thread350,Torch S532178656,no OLD fragments. Warm `warm_stream-r0-s2-full_input`,RID`ab9c724339da47169960dcd488c647cd`:P90112/E98304/Q98067,node127,same thread/S. Two inline callbacks record node124,[90112,96631),prefix6519,FULL descriptor shape6519 and node125,[96631,98067),prefix1436,FULL descriptor shape1673. Descriptors and consumed intervals are retained as observations; their physical equality/content is not evaluated. Source bridge invokes Python inline from the native observer before FULL split, and the callback measures `threading.get_native_id()` and Torch current raw stream and rejects deviation from the insert's scheduler receipt (`sglang_rust_kv_observer.py:58–97,163–191`; `sglang_kv_coherence.py:228–286`). This is an OS native thread ID measured inside a Rust-entered Python callback, not an additional independent Rust thread scalar.

CPP joins use exact `(RIDs,prefix lengths,extend lengths,K pointer,V pointer,writer-location pointer,complete writer-location descriptor)`, uniqueness on both sides, explicit scheduler-chunk membership and all10 FULL layers per chunk. Terminal pool object/buffer pointers match the retained topology.19713 final metadata rows,sequence354–20066, are separate from353 initial rows. Rank receipt isTP0/PP0,DPnull for recordedDP1; no all-TP gather. CPP native/Torch F531885904 differs from observed insert/OLD S532178656: stream equivalence is UNVERIFIED. CPP host enqueue and scalar do not establish CUDA completion or unselected prefix-valid Triton coverage.

Initial statusmetadata_only and final reported statuscaptured, two final banks and16 completed RIDs are recorded without accepting the physical/numeric fields. Initial/final topology is exact: HybridLinearKVPool → MHATokenToKVPool, TokenToKVPoolAllocator,page1,capacity2752780,10 FULL layers3/7/11/15/19/23/27/31/35/39,reported total337248256 bytes (321.625 MiB). Those descriptors/budgets are not physical content proof. No original r1/r2 report or raw artifact was overwritten.

## Exact local verification command and environment

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Local Linux5.10.25-nvidia-gpu,glibc2.35,`/usr/bin/python3`3.10.6,no conda activation. Worker receipt: Python3.12.16,`/opt/sglang/bin/python3`,Torch2.14.1+cu130,SGLang0.5.24.dev80+g056f871,four recorded `NVIDIA H800,81559 MiB,570.124.06` rows. Teacher argv is exactly original baseline except`--dist-init-addr`; seed630625153 versus original596871011 is recorded, not RNG-equivalence proof. Model manifest identities equal baseline, not whole-weight hashes. Image165 remains allocation/build receipt input, not independently inspected imageID.

Reuse the r2 canonical verification mechanisms with AST-selected **pure comparison/source-rewrite/binding functions and source constants only**. No module imports/initializers, installed runtime class execution, native loads/builds, model/GPU/API/auth/SSH/cloud calls or new generalized harness occur. Numeric bank `physical` and `metrics` fields are never selected. Exact rerunnable command (read-only;30 GiB address-space ceiling and60-second timeout):

```bash
timeout 60s env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
p = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_B_r3_results.md')
code = p.read_text().split('<!-- verification-python -->\n```python\n', 1)[1].split('\n```', 1)[0]
exec(compile(code, str(p), 'exec'))
PY
```

<!-- verification-python -->
```python
from pathlib import Path
from collections import Counter
from types import SimpleNamespace
import ast, copy, hashlib, json, math, platform, re, resource, subprocess, sys
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
task = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
evidence = task / 'evidence/teacher-scoring-kv-coherence-probe-20261111'
run = evidence / 'native/B/admission-B-r3'
baseline = task / 'evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1'
commit = subprocess.check_output(['git', 'rev-parse', 'f8b6b43a'], text=True).strip()
base_commit = '4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff'
load = lambda p: json.loads(p.read_text())
lines = lambda p: [json.loads(x) for x in p.read_text().splitlines()]
sha = lambda x: hashlib.sha256(x).hexdigest()
identity = lambda b: {'bytes': len(b), 'sha256': sha(b)}
file_id = lambda p: identity(p.read_bytes())
git = lambda rev, path: subprocess.check_output(['git', 'show', f'{rev}:{path}'], timeout=30)
r, p, old = load(run / 'result.json'), load(run / 'preload.json'), load(baseline / 'result.json')
assert r['job'] == 'exp-1111-194636-897299' and r['pair'] == 'B'
assert r['status'] == 'measurements_completed' and r['native_measurements_completed'] and r['cleanup_completed']
assert r['numerical_acceptance'] is None and r['performance_accepted'] is False
assert r['server_returncode_before_cleanup'] is None and r['server_shutdown_returncode'] == -9
for result, rev, count in ((r, commit, 8), (old, base_commit, 6)):
    assert len(result['native_scoring_sources']) == count
    for name, item in result['native_scoring_sources'].items():
        assert identity(git(rev, name)) == {k: item[k] for k in ('bytes', 'sha256')}, name

# Only selected pure functions/constants are evaluated, never module imports,
# runtime classes, preparation entrypoints, installed/native modules or metrics.
def pure(stem, functions, dependencies=None, assignments=None):
    name = 'tests/manual/agent_opd/' + stem + '.py'
    text = git(commit, name).decode()
    ns = {'Path': Path, 'json': json, 'hashlib': hashlib, 'math': math, 're': re, **(dependencies or {})}
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and (assignments is None or any(isinstance(n, ast.Name) and n.id in assignments for n in node.targets)):
            exec(compile(ast.Module(body=[node], type_ignores=[]), name, 'exec'), ns)
        if isinstance(node, ast.FunctionDef) and node.name in functions:
            node = copy.deepcopy(node)
            node.body = [n for n in node.body if not isinstance(n, (ast.Import, ast.ImportFrom))]
            exec(compile(ast.Module(body=[node], type_ignores=[]), name, 'exec'), ns)
    return SimpleNamespace(**ns)
fp = pure('sglang_mamba_snapshots', {'source_manifest', '_sha256', '_rewrite'})
md = pure('sglang_mamba_runtime_metadata', {'_receipt', 'source_manifest', '_sha256', '_rewrite'}, {'snapshots': fp})
wit = pure('sglang_kv_streams', {'_descriptor', '_terminal', 'source_manifest', '_rewrite', '_qualified_baseline'}, {'metadata': md})
helper = git(commit, 'tests/manual/agent_opd/sglang_kv_coherence.py')
runtime = ('"""CUDA-only opt-in FULL KV observer; no cache decisions or new waits."""\n'
           'import hashlib\nimport math\nimport os\nimport threading\nfrom pathlib import Path\n\n'
           + helper.decode().split('# BEGIN INSTALLED RUNTIME\n', 1)[1].split('# END INSTALLED RUNTIME', 1)[0]).encode()
assert identity(helper) == {'bytes': 41066, 'sha256': '6be5ef8642f33512fb463f30040247750b472716289eba0c139cb65e5d005721'}
coherence = pure('sglang_kv_coherence', {'_edits', '_rewrite', 'source_manifest', 'compare_completion_vectors'},
                 {'streams': wit, '_runtime_source': lambda: runtime},
                 {'SCORING_REQUEST_COUNT', '_HTTP', '_CONTROL', '_IO', '_OUTPUT', '_IMPORT', '_EXTRA_PINS'})
probe = pure('probe_teacher_scoring', {'_comparison', '_coherence_native_bindings', '_native_observer_errors'},
             {'marker': 'old_full_observer_invalidation_failed'}, set())
coherence.compare_completion_vectors.__globals__['_comparison'] = probe._comparison
gate = coherence.compare_completion_vectors(run, baseline)
assert gate['all16_6804_exact'] and gate['vectors'] == 16 and gate['baseline_values'] == gate['candidate_values'] == 6804
requests, flushes = lines(run / 'requests.jsonl'), lines(run / 'cache.jsonl')
fixture = load(Path(r['sample_manifest']['source_fixture']['path']))['samples'][:4]
assert len(requests) == len({x['request_id'] for x in requests}) == len({x['native_request_id'] for x in requests}) == 16
assert len(flushes) == 10 and all(x['status'] == 'flushed' and x['http_status'] == 200 for x in flushes)
scores, cases = {}, []
for request in requests:
    sample = fixture[request['sample_position']]
    v = load(run / 'completion_scores' / (request['request_id'] + '.json'))
    assert request['status'] == 'scored' and request['http_status'] == 200 and request['repetition'] == 0
    assert request['source_uid'] == sample['source_uid'] and request['sample_index'] == sample['sample_index']
    assert v['native_request_id'] == request['native_request_id'] == request['meta_info']['id']
    assert v['request_id'] == request['request_id']
    assert all(v[k] == request[k] for k in ('pair', 'phase', 'mode', 'source_uid', 'sample_index', 'repetition'))
    assert v['token_ids'] == sample['tokens'][-sample['response_length']:]
    assert len(v['log_probs']) == sample['response_length'] == request['returned_completion_count']
    assert all(math.isfinite(x) for x in v['log_probs'])
    assert request['input_token_logprobs_count'] == request['expected_input_token_logprobs_count']
    assert request['meta_info']['num_retractions'] == 0
    assert request['completion_token_id_mismatches'] == request['nonfinite_log_prob_positions'] == []
    comparison = next(x for x in gate['comparisons'] if all(x['case'][k] == request[k] for k in x['case']))
    assert comparison['max_absolute_error'] == comparison['max_relative_error'] == 0.0
    cases.append([request['request_id'], request['native_request_id'], request['sample_position'], request['sample_index'], request['source_uid'], len(v['log_probs']), comparison['relative_error_undefined_count']])
    scores[request['request_id']] = v
assert sum(x[-1] for x in cases) == 64
groups = lines(run / 'comparisons.jsonl')
assert (run / 'comparisons.jsonl').read_bytes() == (baseline / 'comparisons.jsonl').read_bytes() and len(groups) == 8
contracts = 0
for group in groups:
    full, response = scores[group['full_request_id']], scores[group['response_request_id']]
    assert probe._comparison(full, response) == group['full_vs_response_only']
    contracts += 1
    if group['cold_reference']:
        for cold_mode, cold_id in (('full', 'full_request_id'), ('response_only', 'response_request_id')):
            for warm_mode, warm in (('full', full), ('response_only', response)):
                assert probe._comparison(scores[group['cold_reference'][cold_id]], warm) == group['cold_reference'][f'cold_{cold_mode}_vs_warm_{warm_mode}']
                contracts += 1
assert contracts == 24
agreement = {phase: sum(g['full_vs_response_only']['values_exact'] for g in groups if g['phase'] == phase) for phase in ('cold', 'warm_stream')}
assert agreement == {'cold': 4, 'warm_stream': 1}
strip_address = lambda argv: argv[:argv.index('--dist-init-addr')] + argv[argv.index('--dist-init-addr') + 2:]
assert strip_address(r['argv']) == strip_address(old['argv'])
assert r['runtime'] == p['runtime'] and r['runtime']['model_manifest_identity'] == old['runtime']['model_manifest_identity']
for item in (r['fixture'], r['config'], r['sample_manifest']['source_fixture']):
    assert file_id(Path(item['path'])) == {k: item[k] for k in ('bytes', 'sha256')}
config_path = Path(r['config']['path'])
assert config_path.read_bytes() == git('027018aa', str(config_path.relative_to(Path.cwd())))
config = load(config_path)
stages = {}
for scope, owner in zip(('source_preflight', 'runtime_metadata_source_preflight', 'kv_store_stream_source_preflight', 'kv_coherence_source_preflight'), (fp, md, wit, coherence)):
    path, receipt = run / scope, r[scope]
    assert p[scope] == receipt and lines(path / 'preflight.jsonl') == [receipt]
    manifest, expected = load(path / 'source_manifest.json'), owner.source_manifest()
    for key in expected:
        if key != 'files':
            assert manifest[key] == expected[key]
    for name, pins in expected['files'].items():
        assert all(manifest['files'][name][k] == v for k, v in pins.items())
    files = receipt.get('files', receipt.get('observed_after_sha256'))
    if scope != 'kv_coherence_source_preflight':
        assert manifest['files'] == files
    for name in files:
        before, after = (path / 'before' / name).read_bytes(), (path / 'after' / name).read_bytes()
        if scope == 'kv_coherence_source_preflight':
            assert after == (runtime if name == 'srt/kv_coherence.py' else coherence._rewrite(name, before))
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
            if scope == 'source_preflight':
                assert after == fp._rewrite(name, before)
            elif scope == 'runtime_metadata_source_preflight':
                assert after == (md._RECORDER_SOURCE.encode() if item.get('created') else md._rewrite(name, before))
            else:
                wit._qualified_baseline(name, before, manifest['files'][name])
                assert after == wit._rewrite(name, before)
    stages[scope] = {'archive_pairs': len(files), 'manifest': file_id(path / 'source_manifest.json'), 'receipt': file_id(path / 'preflight.jsonl')}
assert [x['archive_pairs'] for x in stages.values()] == [6, 16, 35, 40]
native = r['kv_coherence_source_preflight']['native_observer']
assert load(run / 'kv_coherence_source_preflight/native_observer/preflight.json') == native
build_path = Path(native['build_receipt'])
assert Path(config['kv_coherence_build_receipt']).resolve() == build_path.resolve()
assert sha(build_path.read_bytes()) == native['build_receipt_sha256'] == '91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7'
build = load(build_path)
assert build['status'] == build['qualification']['status'] == 'PASS'
assert build['module'] == native['module'] and build['features'] == native['features'] == ['python-extension']
rust_path = 'tests/manual/agent_opd/sglang_rust_kv_observer.py'
assert git(commit, rust_path) == git('17cb6fc6', rust_path)
rust = pure('sglang_rust_kv_observer', {'_sha', '_replace', '_rust_candidate', '_adapter_candidate', '_verify_compiled_build', '_verify_qualification'})
rust._verify_qualification(build['qualification'])
assert load(Path(build['qualification_receipt']['path'])) == build['qualification']
assert file_id(Path(build['qualification_receipt']['path'])) == {k: build['qualification_receipt'][k] for k in ('bytes', 'sha256')}
for item in build['input_receipts'].values():
    assert file_id(Path(item['path'])) == {k: item[k] for k in ('bytes', 'sha256')}
assert load(Path(build['input_receipts']['source_manifest']['path'])) == build['source_manifest']
elfs = {}
for variant, manifest_key in (('baseline', 'before'), ('observer', 'after')):
    record = build[variant]
    rust._verify_compiled_build(record, variant)
    assert load(Path(build['input_receipts'][variant]['path'])) == record
    library = Path(record['path'])
    assert library.read_bytes().startswith(b'\x7fELF') and sha(library.read_bytes()) == record['sha256']
    elfs[variant] = {'path': str(library), **file_id(library)}
    for name, item in build['source_manifest'][manifest_key].items():
        content = (Path(record['workspace']) / name).read_bytes()
        assert identity(content) == item
        before = (Path(build['baseline']['workspace']) / name).read_bytes()
        assert sha(before) == rust._RUST_PINS[name]
        assert content == (before if variant == 'baseline' else rust._rust_candidate(name, before))
assert len(build['source_manifest']['before']) == len(build['source_manifest']['after']) == 22
assert elfs['observer']['sha256'] == native['compiled_sha256']
source_root = task / 'evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source'
for name, digest in rust._PYTHON_PINS.items():
    assert sha((source_root / name).read_bytes()) == digest
adapter = rust._adapter_candidate((source_root / rust._ADAPTER).read_bytes())
assert sha(adapter) == native['adapter_after_sha256'] == build['source_manifest']['adapter_after_sha256']
import difflib
adapter_patch = ''.join(difflib.unified_diff((source_root / rust._ADAPTER).read_text().splitlines(keepends=True), adapter.decode().splitlines(keepends=True), fromfile='a/' + rust._ADAPTER, tofile='b/' + rust._ADAPTER)).encode()
assert (run / 'kv_coherence_source_preflight/native_observer/adapter.patch').read_bytes() == adapter_patch
assert len(native['composition']) == 35
for name, item in native['composition'].items():
    assert file_id(run / 'kv_store_stream_source_preflight/after' / name) == item
package = r['kv_coherence_package']
assert native['package_root'] == r['kv_coherence_source_preflight']['package_root'] == package['package_root']
assert package['source_package_root'] != package['package_root'] and package['import_origin'] == package['package_root'] + '/__init__.py'
overlap = set(r['runtime']['sglang_sources']) & set(r['kv_coherence_source_preflight']['observed_after_sha256'])
assert len(overlap) == 7 and len(r['runtime']['sglang_sources']) == 38
for name, item in r['runtime']['sglang_sources'].items():
    assert item['path'] == package['package_root'] + '/' + name
    if name in overlap:
        assert file_id(run / 'kv_coherence_source_preflight/after' / name) == {k: item[k] for k in ('bytes', 'sha256')}
first = load(run / 'server_info.json')['get_server_info']['internal_states'][0]
readback = load(run / 'runtime_metadata.json')
assert readback['status'] == 'collected' and readback['http']['http_status'] == 200
assert len(readback['server_info']['internal_states']) == 1
state = readback['server_info']['internal_states'][0]
kv, first_kv, metadata = state['kv_coherence'], first['kv_coherence'], state['mamba_runtime_metadata']
assert kv['process_id'] == first_kv['process_id'] == metadata['process_id'] == 350
assert first_kv['status'] == 'metadata_only' and kv['status'] == 'captured'
assert kv['errors'] == first_kv['errors'] == [] and kv['binding_error'] is first_kv['binding_error'] is None
binding = kv['native_binding']
assert binding == first_kv['native_binding'] and binding['module'] == native['module']
assert binding['module_bytes'] == elfs['observer']['bytes'] == 3411248
assert binding['class'] == 'RustUnifiedTreeCoreBinding' and binding['class_module'] == 'builtins'
probe._coherence_native_bindings(readback['server_info'], native)
observed_errors = probe._native_observer_errors(run / 'server.log')
assert observed_errors['matches'] == readback['native_observer_errors']['matches'] == []
log_errors = [{'line_number': n, 'text': s} for n, s in enumerate((run / 'server.log').read_text(errors='replace').splitlines(), 1) if re.search(r'Traceback|(?:^|[^a-z])(?:Error|Exception|ERROR)(?:[^a-z]|$)|old_full_observer_invalidation_failed', s)]
assert log_errors == []
binding_rejections = []
for field, value in (('binding_error', 'injected retained check'), ('module_file', '/not-staged.so'), ('module_sha256', 'wrong'), ('process_id', 351), ('class_is_module_attribute', False), ('factory_class_matches', False)):
    info = copy.deepcopy({'internal_states': [{'kv_coherence': {k: kv[k] for k in ('schema', 'status', 'errors', 'binding_error', 'native_binding', 'process_id', 'completed_rids')}}]})
    capture = info['internal_states'][0]['kv_coherence']
    capture['banks'] = [{k: b[k] for k in ('rid', 'insert', 'rebind', 'fragments')} for b in kv['banks']]
    assert capture['status'] == 'captured' and len(capture['completed_rids']) == 16 and len(capture['banks']) == 2
    if field == 'binding_error':
        capture[field] = value
    else:
        capture['native_binding'][field] = value
    try:
        probe._coherence_native_bindings(info, native)
    except ValueError as error:
        binding_rejections.append({'field': field, 'error': str(error)})
    else:
        raise AssertionError(field)
probe_text = git(commit, 'tests/manual/agent_opd/probe_teacher_scoring.py').decode()
collect = next(n for n in ast.parse(probe_text).body if isinstance(n, ast.AsyncFunctionDef) and n.name == '_collect_runtime_metadata')
marker_if = next(n for n in ast.walk(collect) if isinstance(n, ast.If) and ast.unparse(n.test) == "record['native_observer_errors']['matches']")
record = {'native_observer_errors': {'matches': [{'line_number': 1, 'text': observed_errors['marker']}], 'marker': observed_errors['marker']}}
record['capture_status'], record['completed_RIDs'], record['bank_count'] = 'captured', 16, 2
try:
    exec(compile(ast.Module(body=[marker_if], type_ignores=[]), 'retained marker gate', 'exec'), {'record': record})
except ValueError as error:
    marker_rejection = str(error)
else:
    raise AssertionError('Marker must reject independently of captured banks')
collector = next(n for n in ast.parse(helper.decode()).body if isinstance(n, ast.ClassDef) and n.name == 'Collector')
drain = next(n for n in collector.body if isinstance(n, ast.FunctionDef) and n.name == 'drain')
error_if = next(n for n in ast.walk(drain) if isinstance(n, ast.If) and 'self.pending_cpp' in ast.unparse(n.test))
assert eval(compile(ast.Expression(error_if.test), 'retained capture-error gate', 'eval'), {'self': SimpleNamespace(by_rid={1: None, 2: None}, errors=['injected error'], pending_cpp={}), 'BANK_COUNT': 2})
topology = kv['topology']
assert topology == first_kv['topology'] and topology['page_size'] == 1 and topology['capacity'] == 2752780
assert topology['mapping'] == [[layer, i] for i, layer in enumerate(range(3, 40, 4))]
assert topology['budget'] == {'payload_bytes': 335544320, 'index_bytes': 1703936, 'allocated_bytes': 337248256}
by_rid = {x['native_request_id']: x for x in requests}
assert len(kv['completed_rids']) == 16 and set(kv['completed_rids']) == set(by_rid)
assert len(kv['banks']) == 2
banks = []
for bank in kv['banks']:
    request = by_rid[bank['rid']]
    assert bank['insert']['rid'] == bank['rebind']['rid'] == bank['rid']
    assert bank['insert']['P'] == bank['rebind']['P'] == 90112 and bank['insert']['E'] == bank['rebind']['E'] == 98304
    assert bank['insert']['thread_id'] == 350 and bank['insert']['torch_current_raw_stream'] == 532178656
    assert all(f['rid'] == bank['rid'] and f['P'] == 90112 and f['E'] == 98304 and f['thread_id'] == 350 and f['torch_current_raw_stream'] == 532178656 for f in bank['fragments'])
    banks.append({'request_id': request['request_id'], **{k: bank[k] for k in ('rid', 'insert', 'rebind', 'fragments')}})
assert banks[0]['request_id'] == 'cold-r0-s2-full_input' and banks[0]['fragments'] == [] and banks[0]['rebind']['Q'] == 90112
assert banks[1]['request_id'] == 'warm_stream-r0-s2-full_input' and banks[1]['rebind']['Q'] == 98067
assert [(f['node_id'], f['lo'], f['hi'], f['prefix_len'], f['original_FULL']['shape']) for f in banks[1]['fragments']] == [(124, 90112, 96631, 6519, [6519]), (125, 96631, 98067, 1436, [1673])]
rows = metadata['rows']
assert metadata['rank']['tp_rank'] == metadata['rank']['pp_rank'] == 0 and metadata['rank']['dp_rank'] is None
assert len(rows) == 19713 and rows[0][0] == 354 and rows[-1][0] == 20066
assert len(first['mamba_runtime_metadata']['rows']) == 353
freeze = lambda x: tuple(map(freeze, x)) if isinstance(x, list) else x
join_fields = ('rids', 'prefix_lens', 'extend_lens', 'k_cache_data_ptr', 'v_cache_data_ptr', 'writer_loc_data_ptr', 'writer_loc')
key = lambda f: tuple(freeze(f[n]) for n in join_fields)
streams, terminals, scheduler = {}, {}, set()
for seq, event, fields in rows:
    f = dict(fields)
    assert len(f) == len(fields)
    if event == 'scheduler_track_boundary':
        chunk = (f['rid'], f['prefix_len'], f['extend_len'])
        assert chunk not in scheduler and f['rid'] in by_rid
        scheduler.add(chunk)
    if event in ('kv_store_stream', 'kv_store_terminal'):
        target = streams if event == 'kv_store_stream' else terminals
        k = key(f)
        assert k not in target and len(f['rids']) == 1 and f['rids'][0] in by_rid
        target[k] = f
assert streams.keys() == terminals.keys() and len(streams) == 1690
chunks, buffers = {}, {x['layer_id']: x for x in topology['buffers']}
for k, f in streams.items():
    terminal = terminals[k]
    assert f['store_kind'] == 'cpp_store_cache' and f['native_stream_scalar_observed'] and f['launch_enqueued']
    assert f['native_actual_stream'] == f['torch_current_raw_stream'] == 531885904
    assert terminal['store_kind'] == 'mha_set_kv_buffer_impl' and terminal['pool_class'][-1] == 'MHATokenToKVPool'
    assert terminal['pool_object_id'] == topology['writer_object_id']
    assert terminal['k_cache_data_ptr'] == buffers[terminal['layer_id']]['K']['data_ptr'] and terminal['v_cache_data_ptr'] == buffers[terminal['layer_id']]['V']['data_ptr']
    chunk = (f['rids'][0], f['prefix_lens'][0], f['extend_lens'][0])
    assert chunk in scheduler
    seen = chunks.setdefault(chunk, set())
    assert terminal['layer_id'] not in seen
    seen.add(terminal['layer_id'])
assert len(chunks) == len(scheduler) == 169 and all(seen == set(buffers) for seen in chunks.values())
assert {x[0] for x in chunks} == set(by_rid)
admission_path, terminal_path = evidence / 'admission-B-r3.json', evidence / 'admission-B-r3.terminal.json'
admission, terminal = load(admission_path), load(terminal_path)
assert admission['job'] == terminal['job'] == r['job'] and terminal['uid'] == '8c094c1d-c90e-48e5-be55-76b40125d246'
assert terminal['creator'] == 'i-fengyicheng' and terminal['status']['phase'] == 'Succeeded' and terminal['native_execution_succeeded'] is True
assert terminal['status']['finishTime'] == '2026-11-11T11:54:54Z'
platform_path = evidence / 'terminal-platform-B-r3.json'
platform_receipt = {'path': str(platform_path), 'status': 'UNVERIFIED; primary-filtered terminal platform receipt absent at snapshot'}
if platform_path.exists():
    platform_data = load(platform_path)
    assert all(platform_data[k] == terminal[k] for k in ('job', 'uid', 'creator', 'status'))
    platform_receipt = {'path': str(platform_path), **file_id(platform_path), 'status': 'PASS retained primary receipt identity/allocation/owner/container linkage', 'snapshot_history': [{'stage': 'initial_local_verification', 'status': 'UNVERIFIED; primary-filtered terminal platform receipt absent at snapshot'}], 'details': platform_data}
raw_names = ('result.json', 'preload.json', 'requests.jsonl', 'cache.jsonl', 'comparisons.jsonl', 'server_info.json', 'runtime_metadata.json', 'server.log')
snapshot = {
    'task_id': 'profile-kv-coherence-native-B-r3-controls-20261111',
    'modification_history': [{'date': '2026-11-11', 'change': 'Read-only B r3 controls, actual serving receipt and bounded observer/CPP scope; physical/KV interpretation pending independent owner.'}],
    'run': str(run), 'baseline': str(baseline), 'job': r['job'], 'uid': terminal['uid'],
    'verdicts': {'controls': 'PASS', 'cold_agreement': 'PASS', 'warm_correctness': 'FAIL', 'source_generated_runtime_composition_R3_two_ELFs': 'PASS', 'actual_serving_binding_retained_receipt': 'PASS', 'insert_OLD_callback_thread_Torch_S': 'PASS', 'responding_TP0_CPP_joins': 'PASS', 'error_controls': 'PASS', 'business_readback_cleanup': 'PASS', 'retained_terminal_admission': 'PASS', 'independent_physical7955_complete_FRESH_OLD_KV_numerical_root': 'UNVERIFIED; pending independent owner', 'mapped_ELF_allTP_Triton_race_GIL_device_completion': 'UNVERIFIED', 'formal': 'HOLD'},
    'controls': {'vectors': 16, 'values': 6804, 'max_absolute_error': 0.0, 'max_defined_relative_error': 0.0, 'zero_reference_relative_undefined': 64, 'identity_errors': 0, 'scored': 16, 'flushes': 10, 'retractions': 0, 'comparison_groups': 8, 'comparison_contracts': 24, 'agreement': agreement, 'case_columns': ['request_id', 'native_request_id', 'sample_position', 'sample_index', 'source_uid', 'values', 'relative_error_undefined_count'], 'cases': cases},
    'source': {'commit': commit, 'baseline_commit': base_commit, 'closure_commit': 'c089f0b3', 'submission_docs_commit': '4f76ae41', 'active_identities': 8, 'baseline_identities': 6, 'helper': identity(helper), 'installed_runtime': identity(runtime), 'stage_archives': stages, 'archive_pairs': 97, 'native_composition_identities': 35, 'native_Rust_baseline_inputs': 22, 'native_Rust_observer_inputs': 22, 'Python_build_input_pins': 3, 'private_runtime_paths': 38, 'runtime_archive_overlaps': 7},
    'R3': {'build_receipt_path': str(build_path), 'build_receipt': file_id(build_path), 'qualification_receipt': build['qualification_receipt'], 'source_manifest': build['input_receipts']['source_manifest'], 'ELFs': elfs, 'original_binary_source_commit': 'UNVERIFIED'},
    'binding': binding,
    'observer': {'process_id': 350, 'rank': metadata['rank'], 'scope': 'responding TP0 only; OS native thread measured inside Rust-entered Python callback, not independent Rust syscall receipt', 'thread_id': 350, 'Torch_S': 532178656, 'initial_status': first_kv['status'], 'reported_final_status': kv['status'], 'completed_response_RIDs': 16, 'banks': banks, 'physical_KV_fields': 'NOT INSPECTED; pending independent owner'},
    'errors': {'initial_global_errors': 0, 'final_global_errors': 0, 'binding_error': None, 'independent_marker_matches': [], 'independent_log_error_matches': [], 'existing_binding_consumer_rejections': binding_rejections, 'existing_marker_gate_rejection': marker_rejection, 'existing_producer_error_predicate_rejects': True},
    'CPP': {'process_id': 350, 'rank': metadata['rank'], 'unique_joins': 1690, 'explicit_chunks': 169, 'response_bound_RIDs': 16, 'FULL_layers': sorted(buffers), 'native_Torch_F': 531885904, 'insert_OLD_Torch_S': 532178656, 'F_equals_S': False, 'F_S_equivalence': 'UNVERIFIED; different observed scalars', 'metadata_rows': 19713, 'startup_rows': 353, 'allTP_Triton_device_completion': 'UNVERIFIED'},
    'runtime': {'local_python': platform.python_version(), 'local_executable': sys.executable, 'worker_python': r['runtime']['python'], 'worker_executable': r['runtime']['executable'], 'torch': r['runtime']['torch'], 'sglang': r['runtime']['sglang'], 'GPU_device_receipt': r['runtime']['gpu_devices'], 'argv': r['argv'], 'seed': state['random_seed'], 'baseline_seed': load(baseline / 'server_info.json')['get_server_info']['random_seed'], 'private_package': package},
    'business': {'status': r['status'], 'readback_status': readback['status'], 'http_status': 200, 'native_measurements_completed': True, 'cleanup_completed': True, 'server_alive_before_cleanup': True, 'shutdown_returncode': -9, 'performance_accepted': False, 'numerical_acceptance': None},
    'terminal_admission': {'path': str(terminal_path), **file_id(terminal_path), 'details': terminal}, 'terminal_platform': platform_receipt,
    'raw_files': {name: file_id(run / name) for name in raw_names}, 'baseline_receipts': {name: file_id(baseline / name) for name in ('result.json', 'requests.jsonl', 'comparisons.jsonl')},
    'config': file_id(config_path), 'fixture': file_id(Path(r['fixture']['path'])),
    'limits': ['Only completed retained B r3 local evidence; no module imports/initializers/native execution/build/GPU/API/auth/SSH/cloud/delegation/source/config/tests/shared-doc/old-artifact edits or staging/commit.', 'Original baseline first4/repetition0 only; relative error undefined at reference0; warm correctness FAIL remains.', 'Binding SHA/size are resolved file bytes after import, not mapped ELF; file represents imported library at receipt time is a bounded assumption, no new buildID demand.', 'Responding PID350/TP0 only; callback OS native thread/Torch S and CPP native/Torch F are separate receipts, no CPP Triton/allTP/stream equivalence/device completion/race/GIL claim.', 'No physical/index/KV numerical metrics inspected or interpreted; physical7955/complete FRESH/OLD/KV/root scopes pending independent owner, not failures.', 'Primary owns terminal platform API/lifecycle and master status synchronization; formal04/05 HOLD, B noA200 dependency, history/raw/science unchanged.']}
output = evidence / 'native-verification-B-r3.json'
if output.exists():
    recorded = load(output)
    snapshot['modification_history'] = recorded['modification_history']
    snapshot['primary_acceptance'] = recorded['primary_acceptance']
    snapshot['verdicts'].update(primary_bounded_stage='ACCEPTED', terminal_platform_binding='PASS')
    assert load(output) == snapshot
    print(json.dumps({'local_verification': 'PASS', 'vectors': 16, 'values': 6804, 'max_abs': 0.0, 'max_defined_rel': 0.0, 'zero_undefined': 64, 'identity_errors': 0, 'scored': 16, 'flushes': 10, 'retractions': 0, 'source_pairs': 97, 'Rust_input_pairs': 22, 'ELFs': 2, 'binding_PID': 350, 'observer_thread': 350, 'Torch_S': 532178656, 'CPP_unique_joins': 1690, 'CPP_native_Torch_F': 531885904, 'global_errors': 0, 'marker_matches': 0, 'warm_correctness': 'FAIL', 'physical_KV': 'UNVERIFIED pending independent owner', 'formal': 'HOLD'}, sort_keys=True))
else:
    print(json.dumps(snapshot, indent=2, allow_nan=False))
```

Passing conditions are the bounded assertions above, not the pending physical/numerical scopes. No native run or source/config/test change was made by this verifier. Primary's independent API/container terminal receipt is not required to finish this local assignment; only retained filtered evidence is consumed when present.

Actual local verification: **PASS**, including exact JSON recomputation, retained adapter patch, existing native build/qualification validators and negative binding/marker/capture-error checks. Initial execution passed without an assertion failure; the same command then verified the written JSON and the explicit captured/16-RID/two-bank error scenarios. No runtime or behavior correction occurred.

```json
{"CPP_native_Torch_F":531885904,"CPP_unique_joins":1690,"ELFs":2,"Rust_input_pairs":22,"Torch_S":532178656,"binding_PID":350,"flushes":10,"formal":"HOLD","global_errors":0,"identity_errors":0,"local_verification":"PASS","marker_matches":0,"max_abs":0.0,"max_defined_rel":0.0,"observer_thread":350,"physical_KV":"UNVERIFIED pending independent owner","retractions":0,"scored":16,"source_pairs":97,"values":6804,"vectors":16,"warm_correctness":"FAIL","zero_undefined":64}
```

Scoped whitespace commands:

```bash
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_B_r3_results.md
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-B-r3.json
```

Both emitted no whitespace diagnostics (expected new-file `--no-index` exit1). Only the two assigned outputs were created. No source/config/tests/shared eight documents/raw files/staging/commit changes were made. **Historical initial snapshot:** `terminal-platform-B-r3.json` was absent then, so container/platform details were UNVERIFIED and primary-owned, without blocking or causing a platform call here. The later terminal-only follow-up below supersedes that current missing-receipt status, not its history. Retained admission terminal is470 bytes,SHA`c9e550d07acbbd58064f498b0a490738b7932782dc3b4daaa2562ebd72a019ef`.

## Terminal-only primary acceptance follow-up

The primary explicitly ACCEPTS the bounded stage stated above. New primary-filtered `terminal-platform-B-r3.json`, observed at2026-11-11T12:03:59.987988+00:00, is2603 bytes,SHA`f3fa51901e8eabf04ac8048252de1f7a7f5dc325d65dc2e0ed0805ab35832d24`. Job/UID/creator/status agree exactly with the retained admission terminal and this report's JSON. SDK and API filtered statuses agree: Succeeded/RJobSucceeded,finish11:54:54Z.

Observed inputs: image165ff0be, local NFS`100.96.128.195:/data/ycfeng:/data/ycfeng`,positive tagH800,charged groupcodesign,preemptible=no;one`probe` container/one replica,request=limit CPU32/memory250Gi/GPU4. ReplicaUID`31f87bec-998c-4359-aba0-6e5dcc21c557` has exact RJob job/UID/controller ownerRef and phaseSucceeded. Container`probe` isCompleted/exit0/restart0,last_state{},started11:47:46Z,finished11:54:52Z. Primary-filtered `node_name` is`gpu-h800-0030.host.platform.shaipower.com`, derived from observed `status.nodeName`, not `spec`. Node/allocation facts alone do not prove physical hardware; the prior four retained `nvidia-smi` device rows remain separate, unchanged evidence. The filtered collector's historical spec-lookup `KeyError nodename` correction is retained as receipt text, not a native/business failure.

Only the two owned artifacts were updated. Original numbers, warmFAIL, CPP F531885904/observer S532178656 and all scope limits are unchanged. The initial JSON was18452 bytes,SHA`f6b74702214ad660d41b9420c88ab93ecc458bd5ab3b34fe12036653c1bac795`; its absent-receipt disposition is preserved in `terminal_platform.snapshot_history`. A canonical hash over the unchanged owned JSON sections verifies preservation without opening or recomputing vectors, source archives, native modules or K/V metrics.

Exact affected-only command, same local `/usr/bin/python3`3.10.6/Linux environment, no conda activation:

<!-- terminal-followup-command -->
```bash
timeout 60s env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
import hashlib, json, sys
root = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111')
e = json.loads((root / 'native-verification-B-r3.json').read_text())
p = root / 'terminal-platform-B-r3.json'
t = json.loads(p.read_text())
a = json.loads((root / 'admission-B-r3.terminal.json').read_text())
assert all(t[k] == a[k] == e['terminal_admission']['details'][k] for k in ('job', 'uid', 'creator', 'status'))
assert t['job'] == e['job'] == 'exp-1111-194636-897299'
assert t['uid'] == e['uid'] == '8c094c1d-c90e-48e5-be55-76b40125d246'
assert t['creator'] == 'i-fengyicheng' and t['pair'] == 'B'
assert t['status'] == t['sdk_terminal_status'] and t['status']['phase'] == 'Succeeded'
assert t['status']['finishTime'] == '2026-11-11T11:54:54Z'
assert t['positive_tags'] == ['H800'] and t['charged_group'] == 'codesign' and t['preemptible'] == 'no'
assert t['source_mount'] == '100.96.128.195:/data/ycfeng:/data/ycfeng' and t['source_commit'] == e['source']['commit']
assert len(t['containers']) == len(t['replicas']) == 1
c = t['containers'][0]
assert c['name'] == 'probe'
assert c['image'] == 'artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805'
assert c['resources']['limits'] == c['resources']['requests'] == {'cpu': '32', 'memory': '250Gi', 'nvidia.com/gpu': '4'}
r = t['replicas'][0]
assert r['uid'] == '31f87bec-998c-4359-aba0-6e5dcc21c557' and r['phase'] == 'Succeeded'
assert r['node_name'] == 'gpu-h800-0030.host.platform.shaipower.com'
assert r['owner_references'] == [{'kind': 'RJob', 'name': e['job'], 'uid': e['uid'], 'controller': True}]
assert len(r['containers']) == 1
c = r['containers'][0]
assert c['name'] == 'probe' and c['restart_count'] == 0 and c['last_state'] == {}
assert c['terminated'] == {'exitCode': 0, 'reason': 'Completed', 'startedAt': '2026-11-11T11:47:46Z', 'finishedAt': '2026-11-11T11:54:52Z'}
assert e['terminal_platform']['details'] == t
assert e['terminal_platform']['status'] == 'PASS retained primary receipt identity/allocation/owner/container linkage'
assert e['terminal_platform']['bytes'] == p.stat().st_size == 2603
assert e['terminal_platform']['sha256'] == hashlib.sha256(p.read_bytes()).hexdigest() == 'f3fa51901e8eabf04ac8048252de1f7a7f5dc325d65dc2e0ed0805ab35832d24'
assert e['terminal_platform']['snapshot_history'] == [{'stage': 'initial_local_verification', 'status': 'UNVERIFIED; primary-filtered terminal platform receipt absent at snapshot'}]
assert e['primary_acceptance']['status'] == 'ACCEPTED_BOUNDED_STAGE'
assert e['verdicts']['primary_bounded_stage'] == 'ACCEPTED' and e['verdicts']['terminal_platform_binding'] == 'PASS'
sections = ('controls', 'source', 'R3', 'binding', 'observer', 'errors', 'CPP', 'runtime', 'business', 'terminal_admission', 'raw_files', 'baseline_receipts', 'config', 'fixture', 'limits')
bounded = {k: e[k] for k in sections}
digest = hashlib.sha256(json.dumps(bounded, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
assert digest == e['primary_acceptance']['unchanged_bounded_sections_sha256'] == '37be007b1dbd48feae72a831e93997752ad26337ccd81f648b8901e4f72aaa60'
assert e['controls']['agreement'] == {'cold': 4, 'warm_stream': 1} and e['verdicts']['warm_correctness'] == 'FAIL'
assert e['CPP']['native_Torch_F'] == 531885904 and e['CPP']['insert_OLD_Torch_S'] == 532178656
assert e['CPP']['F_S_equivalence'] == 'UNVERIFIED; different observed scalars' and e['verdicts']['formal'] == 'HOLD'
print(json.dumps({'terminal_only_check': 'PASS', 'primary_bounded_stage': 'ACCEPTED', 'receipt_bytes': 2603, 'job_UID_owner_image_NFS_allocation_container': 'PASS', 'node_name': r['node_name'], 'phase': r['phase'], 'container_reason': c['terminated']['reason'], 'exitCode': 0, 'restarts': 0, 'unchanged_bounded_sections': 'PASS', 'local_python': sys.version.split()[0]}, sort_keys=True))
PY
```

Expected/observed: terminal-only PASS, primary boundedACCEPTED, exact receipt identity/owner/image/NFS/allocation/Succeeded/Completed0/restart0 and unchanged owned bounded-section hash PASS. No original full verification command or CPU/native/platform call was rerun. Scoped whitespace commands above remain the only additional checks.

Actual invocation evaluated only that follow-up block:

```bash
timeout 60s env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
p = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_B_r3_results.md')
block = p.read_text().split('<!-- terminal-followup-command -->\n```bash\n', 1)[1].split('\n```', 1)[0]
code = block.split("<<'PY'\n", 1)[1].rsplit('\nPY', 1)[0]
exec(compile(code, str(p) + ':terminal-only', 'exec'))
PY
```

```json
{"container_reason":"Completed","exitCode":0,"job_UID_owner_image_NFS_allocation_container":"PASS","local_python":"3.10.6","node_name":"gpu-h800-0030.host.platform.shaipower.com","phase":"Succeeded","primary_bounded_stage":"ACCEPTED","receipt_bytes":2603,"restarts":0,"terminal_only_check":"PASS","unchanged_bounded_sections":"PASS"}
```

## 1. 规划完成情况

**汇总：** PASS6｜BLOCKED/FAILED/SKIPPED3｜TODO0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| B r3原始control向量/identity | PASS |16/6804 exact，16scored/10flushes/0retractions |
| 冻结source/R3/两ELF/native inputs | PASS |97pairs、35composition、22Rust input pairs，原config不变 |
| 实际serving binding | PASS | retained PID350/path/SHA/size/export/factory ties |
| observer S/thread与CPP独立scope | PASS | thread350/S532178656；CPP1690joins/F531885904，TP0 only |
| 两份指定本地输出 | PASS |primary ACCEPTED bounded stage；affected-only terminal linkage/保存检查PASS |
| 原warm correctness | FAILED |cold4/4、warm1/4仍与原baseline相同 |
| physical7955/完整FRESH/OLD/KV解释 | BLOCKED |本分工未核验；独立owner负责，不标为本次failure |
| retained平台/container linkage | PASS |primary提供filtered receipt；本地校验Succeeded/Completed0/restart0，无API采集 |
| formal04/05/06终验 | BLOCKED |warm仍FAIL，fresh own200未完成；B无A200依赖 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次B r3委托至primary ACCEPTED及terminal-only后续校验｜**当前前沿：** independent physical/KV核验；本分工停止。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR |复用r2 canonical；后续仅三份小JSON/terminal linkage，无广测/新harness |
| D2 细节反复重试 | CLEAR |首验PASS；后续无CPU/native/全量重算或streamprobe |
| D3 支线问题修补 | CLEAR |无source/config/root fix/KV numerical解释 |
| D4 可并行任务停滞 | CLEAR |explicit B-only/no-delegation ownership；不等primary平台或另一物理owner |
| D5 超范围镀金 | CLEAR |只生成两份指定产物，原raw/report保留 |
| D6 分析空转 | CLEAR |输出已落地且exact recomputation PASS |
| D7 路线违背 | CLEAR |不把CPP扩为Triton/allTP，不把captured/bankcomplete作物理或formal验收 |

**文档检查：** S5：`requirements.md:3`、`plan.md:3`、`progress.md:219`、`tickets/05-b-full.md:3`仍记Initial/submitted状态；retained admission已Succeeded，bounded本地结果已可核验。Primary同步共享current状态，本分工不编辑。S1–S4/S6在本分工对应的边界未发现明显缺陷；未重审全部历史spec/tickets。
**归因：** 无执行偏离；共享状态同步归primary。

## 3. 纠正建议

**分支：** B：共享current状态需同步，scope/criterion/科学决定不变。

**文档更新（先执行）：**
1. Primary在共享requirements/plan/progress/Ticket05 current段落同步已ACCEPTED bounded stage及retained terminal linkage；physical/KV待独立owner、warmFAIL/formalHOLD/B noA200保留（可直接执行；primary ownership）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Primary bounded acceptance及本地terminal linkage已记录 → 完成标志：ACCEPTED/local PASS、warmFAIL、未核验physical/KV范围分开。
2. 独立physical/KV owner继续；本subagent停止，不额外streamprobe/API/native/mappedELF/buildID gate。
3. 原teacher RCA/最小warm修正 → fresh independent A ‖ B own200 →06；不增加B等待A200边。

## 4. 最值得关注的 3 点

1.16/6804与原baseline exact，原warm1/4 FAIL仍在，不能推进formal验收。
2.PID350实际binding receipt和inline callback thread/Torch S已核验；文件SHA是after-import路径字节，不是mappedELF/allTP证明。
3.CPP F531885904与observer S532178656是不同记录；physical7955/完整FRESH/OLD/KV结论由另一owner完成，本报告不判其failure。
