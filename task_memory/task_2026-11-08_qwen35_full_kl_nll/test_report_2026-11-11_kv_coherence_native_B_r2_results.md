## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Read-only verification of retained B r2 controls against immutable6119bee1 and4f1139b0; separate exact scoring/source/CPP evidence from failed capture and observation-only topology/banks/fragments. |
| 2026-11-11 | Verify subsequently provided primary-filtered B r2 terminal receipt only; retain all scoring/source/CPP/capture measurements and original raw evidence. |

# KV coherence B r2 retained control results

TaskID: `profile-kv-coherence-native-B-r2-20261111`.

**Control equivalence PASS; business attempt/readback FAIL; complete fresh/OLD physical capture and numeric acceptance UNVERIFIED; formal HOLD.** No collector RCA, correction, source/config/master-document edit, platform/auth/GPU operation, native execution, delegation, staging or commit occurred. Original r1/r2 raw and previous reports/proofs remain unchanged.

Run: `evidence/teacher-scoring-kv-coherence-probe-20261111/native/B/admission-B-r2`, job `exp-1111-171526-099435`.
Original accepted baseline: `evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1`, job `exp-1111-073825-734134`, caller `4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff`.
Machine evidence: [native-verification-B-r2.json](evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-B-r2.json).

## Verification results

| Check | Actual result | Verdict and limit |
| --- | --- | --- |
| Logical vectors and identities |16 vectors/6,804 finite values EXACT; exact response-tail token IDs, logical identities and response-bound RIDs; identity errors0 | PASS controls only |
| Error metrics | Max abs0; max defined rel0;64 zero-reference positions have undefined relative error | PASS, no tolerance |
| Requests/cache |16 HTTP200 scored;10 HTTP200 successful flushes;0 retractions | PASS |
| Original differences |8 comparison groups byte-identical to baseline;24 comparison contracts recomputed exactly | PASS reproduction; existing warm correctness FAIL remains |
| Immutable source | r2 8/8 identities match6119bee19eae6091ac757bbccbf9b168b5f508be; baseline6/6 match4f1139b0 | PASS snapshot identity; not live source attestation |
| Collector helper |38,793 bytes;SHA `e9e4798c2260db26f1cc532641bb3f02eec3897c8d744953648a53d1d1d0fc43` | PASS frozen Git; no live helper used |
| Source archives |97 before/after pairs:6 FP32,16 metadata,35 CPP WIT,40 coherence; template pins, receipts and exact archived bytes/rewrite agree | PASS source scope |
| R3/private ELF | Selected nested receiptSHA91458ef4, qualificationSHA2176426d, ELF SHA0dc763cc and35 source identities agree | PASS retained linkage; original bundled binary source commit still UNVERIFIED |
| Recorded private runtime |38 source paths are private;7 archive/runtime hash overlaps; four retained H800 device rows | PASS recorded provenance; no independent physical all-TP/module attestation |
| Ordinary CPP identity joins |1,690 unique one-to-one joins;169 explicit scheduler chunks/16 response-bound RIDs/10 FULL layers per chunk | PASS responding process347,TP0 only |
| Initializer/preallocation | Initial statusmetadata_only; exact initial/final topology equal,page1/capacity2752780/10 buffers/budget337248256 bytes | Observed; not complete capture PASS |
| Capture/readback | HTTP200; collectorunverified;140 globalerrors (70note_cpp/70fresh),RIDnull,`NoneType` len;16 completed_rids;two banks | FAIL/unverified, not a scoring/math failure |
| Physical7955/fresh/KV numerical/root-fix/race/all-TP/performance/formal200 | Two reported fragments are descriptors/intervals, not independently qualified physical tensor contents; no accepted numeric summaries | UNVERIFIED; formal04/05 HOLD unchanged |

Relative error is `abs(candidate-reference)/abs(reference)` only where reference is nonzero. Exact zero/zero remains undefined. Native RIDs differ from baseline and are joined to their own HTTP response metadata; logical cases use `(pair, phase, mode, source_uid, sample_index, repetition)`, not RID equality across runs or chronology. JSON records all16 exact request IDs,sourceUIDs,indexes,nativeRIDs,value counts and undefined counts. First4/repetition0 only; no56-request/second-repetition/global1024 acceptance.

The four original response lengths are734/246/431/290, indexes1693–1696 and UIDs ending`:5:123/:5:125/:5:127/:5:129`. Cold full versus response is4/4 exact; warm remains1/4 exact, including the original warm1 tiny mismatch and larger warm2/3 differences. The original `accepted=null` contracts are preserved. No new numeric interpretation, cause, tolerance, scientific change or fix is inferred from reproduction.

## Actual retained runtime and failed readback

Business result: `status=failed`, `native_measurements_completed=true`, `cleanup_completed=true`, `performance_accepted=false`, `numerical_acceptance=null`. Server alive before cleanup (`server_returncode_before_cleanup=null`); shutdown returncode−9. Exact independent-readback failure:

```text
Scoring completed; independent runtime metadata readback failed: KV coherence diagnostic unverified: Candidate cardinality/capture errors/unconsumed CPP witness
object of type 'NoneType' has no len()
```

Initial non-draining and final explicit-draining receipts report the same140 global error entries. Each hasRIDnull,P90112,E98304;70 entries each at`note_cpp` and`fresh`. No association with a selected request or causal diagnosis is inferred. Initial status`metadata_only` is not healthy-capture acceptance; initial already includes these errors. Final status`unverified`, numeric acceptance null, two banks and16 completed_rids. A completed RID list is not a complete fresh capture. Result `kv_coherence.summaries=[]`; the responding collector was process347,TP0/PP0/DPnull (recorded DP1), explicitly no all-TP gather.

Initializer/topology observations: root`HybridLinearKVPool`, writer`MHATokenToKVPool`, allocator`TokenToKVPoolAllocator`, page1, capacity2752780. Ten FULL layer mappings3/7/11/15/19/23/27/31/35/39 →0–9. K/V buffers each `[2752781,1,256]`,stride`[256,256,1]`,BF16,cuda:0. Reported budget:payload335544320,index1703936,total337248256 bytes =321.625 MiB. Initial/final exact topology equality and descriptors are verified, not tensor contents or per-bank copy completeness.

Bank observations are retained with their actual identities:

| Request | Insert/rebind | OLD fragment observations |
| --- | --- | --- |
| `cold-r0-s2-full_input`,RID`97eda4a0684a42f28c9f0a16b172c807` |P90112/E98304;Q90112;node67;FULL descriptorint64,cuda:0,shape98304;fresh_layers0–9;bankerrors[] | None |
| `warm_stream-r0-s2-full_input`,RID`564e4e7206a245c7aebd3b9e9c9b71ac` |P90112/E98304;Q98067;node127;FULL descriptorint64,cuda:0,shape98304;fresh_layers0–9;bankerrors[] | node124:[90112,96631),reportedprefix6519,FULLshape6519;node125:[96631,98067),reportedprefix1436,FULLshape1673 |

Both inserts and both warm fragment records name thread347,Torch stream1369454976. The ordinary CPP native/Torch stream is1369149904. These are separate observed receipts; equality between OLD and CPP streams, stream ownership, alias validity, event completion or physical7955 binding is **not** asserted. Fragment tensor shapes need not equal their reported consumed interval lengths. The verifier records these descriptors without evaluating KV values or explaining failure. The independently assigned collector owner owns RCA/fix.

Ordinary CPP joins use exact `(RIDs, prefix lengths, extend lengths, K pointer, V pointer, writer-location pointer, complete writer-location descriptor)`. Each stream/terminal key is unique and has one exact counterpart. Each169 explicit scheduler chunk has each10 FULL layers exactly once; terminal writer object/buffer pointers match this responding topology. Final metadata19,713 rows,sequence354–20066;353 initial startup rows are separate. No pointer alone, adjacency or filename ordering establishes a join. Device store completion remains UNVERIFIED; absent `old_full_observer_invalidation_failed` marker is not alias/GIL/CUDA/native physical proof.

WorkerPython3.12.16,`/opt/sglang/bin/python3`,Torch2.14.1+cu130,SGLang0.5.24.dev80+g056f871. Four actual retained device rows:`NVIDIA H800, 81559 MiB, 570.124.06`. Teacher argv is in JSON and exactly baseline argv except`--dist-init-addr`:TP4,BF16,context131072,static0.85,concurrency1,prefill8192,graphs disabled,deterministic inference,FA3,Triton linear prefill. Seed1013583994 versus baseline596871011 is recorded, not RNG-equivalence proof. Mounted model manifest identities equal baseline; not whole-weight checksums. Image165ff0be remains allocation input, not independently inspected imageID.

Recorded private package:`/var/tmp/teacher-scoring-kv-v8uxgy6t/kv-coherence-runtime/sglang`; original package:`/sgl-workspace/sglang/python/sglang`. Whole-package staging/import-origin/path receipts agree. Selected production module`sglang.srt.mem_cache.rust_tree_core.mem_cache`,private same-name CPython312 ELF target. Exact retained ELF is3,411,248 bytes,SHA`0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba`; build receiptSHA`91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7`. No ELF load/build/execution occurred here. A staging path/hash and matching callback descriptors do not prove actual selected library mapping, original OLD data/alias validity or full private-module/runtime/physical attestation. Accepted prior R3/source/CPU/WIT scope is unchanged.

Primary-retained `admission-B-r2.terminal.json` reports UID`85b88b38-cfc2-4903-8aaa-3fc133332f76`,creator`i-fengyicheng`,Failed/RJobFailed at2026-11-11T09:29:02Z. Separately filtered `terminal-platform-B-r2.json` was unavailable at the first snapshot and subsequently provided by primary; this owner read it locally without waiting or querying any platform. Its job/UID/creator/status and replica-owner UID agree with admission. Container`probe`:Error/exit1/restart0,started09:22:18Z,finished09:29:00Z. Retained source mount`100.96.128.195:/data/ycfeng:/data/ycfeng`,preemptible=`no` (non-preemptible),positive tagH800; no absent node/imageID details are invented. Receipt is1,756 bytes,SHA`60d209d801d5be04c85f445a377c1b5067a755846cf4cd5cc390ab7ea1844758`. Primary owns platform collection and launcher lifecycle. Business failure after scoring/readback precedes normal cleanup; missing qualification is not mathematical failure or the training root-cause conclusion.

## Exact local commands, environment and evidence

Working directory:`/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Local `/usr/bin/python3`3.10.6, Linux;no conda activation. Read-only Git blobs and exact r2/baseline scope only, no broad tests/source collection/global5,501/621 rehash or new permanent verifier framework. The historical worker command remains in`admission-B-r2.json.worker_command`; it was not rerun.

The initial local memory-limited inspection using`timeout 60s systemd-run --user --scope -p MemoryMax=30G env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B -` failed before Python with`Failed to connect to bus: No such file or directory`. No native/platform operation occurred. Local inspection then used the existing Python resource API for a30 GiB address-space ceiling and60-second timeout. This changes only verification process limits, never collector/runtime behavior.

Exact rerunnable verification:

```bash
timeout 60s env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
p = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_B_r2_results.md')
code = p.read_text().split('<!-- verification-python -->\n```python\n', 1)[1].split('\n```', 1)[0]
exec(compile(code, str(p), 'exec'))
PY
```

<!-- verification-python -->
```python
from pathlib import Path
from collections import Counter
import ast, hashlib, json, math, platform, resource, subprocess, sys, types
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
task = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
evidence = task / 'evidence/teacher-scoring-kv-coherence-probe-20261111'
run = evidence / 'native/B/admission-B-r2'
baseline = task / 'evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1'
commit, base_commit = '6119bee19eae6091ac757bbccbf9b168b5f508be', '4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff'
load = lambda p: json.loads(p.read_text())
lines = lambda p: [json.loads(x) for x in p.read_text().splitlines()]
sha = lambda x: hashlib.sha256(x).hexdigest()
file_id = lambda p: {'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
git = lambda rev, path: subprocess.check_output(['git', 'show', f'{rev}:{path}'], timeout=30)
r, p, old = load(run / 'result.json'), load(run / 'preload.json'), load(baseline / 'result.json')
assert r['job'] == 'exp-1111-171526-099435' and r['pair'] == 'B'
assert r['status'] == 'failed' and r['native_measurements_completed'] and r['cleanup_completed']
assert r['performance_accepted'] is False and r['numerical_acceptance'] is None
assert r['server_returncode_before_cleanup'] is None and r['server_shutdown_returncode'] == -9
for result, rev, count in ((r, commit, 8), (old, base_commit, 6)):
    assert len(result['native_scoring_sources']) == count
    for name, observed in result['native_scoring_sources'].items():
        blob = git(rev, name)
        assert len(blob) == observed['bytes'] and sha(blob) == observed['sha256'], name
owners = []
for stem in ('sglang_mamba_snapshots', 'sglang_mamba_runtime_metadata', 'sglang_kv_streams', 'sglang_kv_coherence'):
    name = 'tests.manual.agent_opd.' + stem
    module = types.ModuleType(name)
    module.__file__ = 'tests/manual/agent_opd/' + stem + '.py'
    sys.modules[name] = module
    content = git(commit, module.__file__)
    exec(compile(content, module.__file__, 'exec'), module.__dict__)
    owners.append(module)
fp, md, wit, coherence = owners
blob = git(commit, coherence.__file__)
assert len(blob) == 38793 and sha(blob) == 'e9e4798c2260db26f1cc532641bb3f02eec3897c8d744953648a53d1d1d0fc43'
runtime = ('"""CUDA-only opt-in FULL KV observer; no cache decisions or new waits."""\nimport math\nimport os\nimport threading\n\n'
           + blob.decode().split('# BEGIN INSTALLED RUNTIME\n', 1)[1].split('# END INSTALLED RUNTIME', 1)[0]).encode()
coherence._runtime_source = lambda: runtime
gate = coherence.compare_completion_vectors(run, baseline)
assert gate['all16_6804_exact'] and gate['vectors'] == 16
assert gate['baseline_values'] == gate['candidate_values'] == 6804
probe = git(commit, 'tests/manual/agent_opd/probe_teacher_scoring.py').decode()
node = next(n for n in ast.parse(probe).body if isinstance(n, ast.FunctionDef) and n.name == '_comparison')
namespace = {'math': math}
exec(ast.get_source_segment(probe, node), namespace)
comparison = namespace['_comparison']
requests, flushes = lines(run / 'requests.jsonl'), lines(run / 'cache.jsonl')
fixture = load(Path(r['sample_manifest']['source_fixture']['path']))['samples'][:4]
assert len(requests) == len({x['native_request_id'] for x in requests}) == 16
assert len(flushes) == 10 and all(x['status'] == 'flushed' and x['http_status'] == 200 for x in flushes)
scores, cases = {}, []
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
    result = next(x for x in gate['comparisons'] if all(x['case'][k] == request[k] for k in x['case']))
    cases.append([request['request_id'], request['native_request_id'], request['sample_position'], request['sample_index'], request['source_uid'], len(v['log_probs']), result['relative_error_undefined_count']])
    scores[request['request_id']] = v
assert sum(x[-1] for x in cases) == 64
groups = lines(run / 'comparisons.jsonl')
assert (run / 'comparisons.jsonl').read_bytes() == (baseline / 'comparisons.jsonl').read_bytes() and len(groups) == 8
contracts = 0
for group in groups:
    full, response = scores[group['full_request_id']], scores[group['response_request_id']]
    assert comparison(full, response) == group['full_vs_response_only']
    contracts += 1
    if group['cold_reference']:
        for cold_mode, cold_id in (('full', 'full_request_id'), ('response_only', 'response_request_id')):
            for warm_mode, warm in (('full', full), ('response_only', response)):
                assert comparison(scores[group['cold_reference'][cold_id]], warm) == group['cold_reference'][f'cold_{cold_mode}_vs_warm_{warm_mode}']
                contracts += 1
assert contracts == 24
strip_address = lambda argv: argv[:argv.index('--dist-init-addr')] + argv[argv.index('--dist-init-addr') + 2:]
assert strip_address(r['argv']) == strip_address(old['argv'])
assert r['runtime'] == p['runtime'] and r['runtime']['model_manifest_identity'] == old['runtime']['model_manifest_identity']
for item in (r['fixture'], r['config'], r['sample_manifest']['source_fixture']):
    assert file_id(Path(item['path'])) == {k: item[k] for k in ('bytes', 'sha256')}
config = load(Path(r['config']['path']))
stages = {}
for scope, owner in zip(('source_preflight', 'runtime_metadata_source_preflight', 'kv_store_stream_source_preflight', 'kv_coherence_source_preflight'), owners):
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
            if scope == 'runtime_metadata_source_preflight':
                assert after == (md._RECORDER_SOURCE.encode() if item.get('created') else md._rewrite(name, before))
            elif scope == 'kv_store_stream_source_preflight':
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
assert git(commit, 'tests/manual/agent_opd/sglang_rust_kv_observer.py') == git('17cb6fc6', 'tests/manual/agent_opd/sglang_rust_kv_observer.py')
assert file_id(Path(build['qualification_receipt']['path'])) == {k: build['qualification_receipt'][k] for k in ('bytes', 'sha256')}
library = Path(build['observer']['path'])
assert library.read_bytes().startswith(b'\x7fELF') and sha(library.read_bytes()) == native['compiled_sha256'] == build['observer']['sha256']
assert len(native['composition']) == 35
for name, item in native['composition'].items():
    assert file_id(run / 'kv_store_stream_source_preflight/after' / name) == item
package = r['kv_coherence_package']
assert native['package_root'] == r['kv_coherence_source_preflight']['package_root'] == package['package_root']
assert native['binary_target'].startswith(package['package_root'] + '/')
assert package['source_package_root'] != package['package_root'] and package['import_origin'] == package['package_root'] + '/__init__.py'
overlap = set(r['runtime']['sglang_sources']) & set(r['kv_coherence_source_preflight']['observed_after_sha256'])
assert len(overlap) == 7 and len(r['runtime']['sglang_sources']) == 38
for name, item in r['runtime']['sglang_sources'].items():
    assert item['path'] == package['package_root'] + '/' + name
    if name in overlap:
        assert file_id(run / 'kv_coherence_source_preflight/after' / name) == {k: item[k] for k in ('bytes', 'sha256')}
assert (r['runtime']['python'], r['runtime']['torch'], r['runtime']['sglang']) == ('3.12.16', '2.14.1+cu130', '0.5.24.dev80+g056f871')
assert r['runtime']['gpu_devices'] == ['NVIDIA H800, 81559 MiB, 570.124.06'] * 4
initial = load(run / 'server_info.json')['get_server_info']
readback = load(run / 'runtime_metadata.json')
assert readback['status'] == 'failed' and readback['http']['http_status'] == 200
assert len(initial['internal_states']) == len(readback['server_info']['internal_states']) == 1
state, first = readback['server_info']['internal_states'][0], initial['internal_states'][0]
kv, first_kv, metadata = state['kv_coherence'], first['kv_coherence'], state['mamba_runtime_metadata']
assert kv['process_id'] == first_kv['process_id'] == metadata['process_id'] == 347
assert first_kv['status'] == 'metadata_only' and kv['status'] == 'unverified' and kv['numeric_acceptance'] is None
assert kv['errors'] == first_kv['errors'] and len(kv['errors']) == 140
assert Counter(x['stage'] for x in kv['errors']) == {'note_cpp': 70, 'fresh': 70}
assert all(x['rid'] is None and x['P'] == 90112 and x['E'] == 98304 and x['message'] == "object of type 'NoneType' has no len()" for x in kv['errors'])
topology = kv['topology']
assert topology == first_kv['topology'] and topology['page_size'] == 1 and topology['capacity'] == 2752780
assert topology['mapping'] == [[layer, i] for i, layer in enumerate(range(3, 40, 4))]
assert topology['budget'] == {'payload_bytes': 335544320, 'index_bytes': 1703936, 'allocated_bytes': 337248256}
for b in topology['buffers']:
    for side in ('K', 'V'):
        assert b[side]['shape'] == [2752781, 1, 256] and b[side]['stride'] == [256, 256, 1]
        assert b[side]['dtype'] == 'torch.bfloat16' and b[side]['device'] == 'cuda:0'
by_rid = {x['native_request_id']: x for x in requests}
assert len(kv['completed_rids']) == 16 and set(kv['completed_rids']) == set(by_rid)
assert len(kv['banks']) == 2 and r['kv_coherence']['summaries'] == []
banks = []
for bank in kv['banks']:
    request = by_rid[bank['rid']]
    assert bank['insert']['rid'] == bank['rebind']['rid'] == bank['rid']
    assert bank['insert']['P'] == bank['rebind']['P'] == 90112 and bank['insert']['E'] == bank['rebind']['E'] == 98304
    assert bank['fresh_layers'] == list(range(10)) and bank['errors'] == []
    assert bank['insert']['thread_id'] == 347 and bank['insert']['torch_current_raw_stream'] == 1369454976
    assert all(f['rid'] == bank['rid'] and f['thread_id'] == 347 and f['torch_current_raw_stream'] == 1369454976 for f in bank['fragments'])
    banks.append({'request_id': request['request_id'], **bank})
assert banks[0]['request_id'] == 'cold-r0-s2-full_input' and banks[0]['fragments'] == [] and banks[0]['rebind']['Q'] == 90112
assert banks[1]['request_id'] == 'warm_stream-r0-s2-full_input' and banks[1]['rebind']['Q'] == 98067
assert [(f['node_id'], f['lo'], f['hi'], f['prefix_len'], f['original_FULL']['shape']) for f in banks[1]['fragments']] == [(124, 90112, 96631, 6519, [6519]), (125, 96631, 98067, 1436, [1673])]
assert readback['native_observer_errors']['matches'] == []
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
    t = terminals[k]
    assert f['store_kind'] == 'cpp_store_cache' and f['native_stream_scalar_observed'] and f['launch_enqueued']
    assert f['native_actual_stream'] == f['torch_current_raw_stream'] == 1369149904
    assert t['store_kind'] == 'mha_set_kv_buffer_impl' and t['pool_class'][-1] == 'MHATokenToKVPool'
    assert t['pool_object_id'] == topology['writer_object_id']
    assert t['k_cache_data_ptr'] == buffers[t['layer_id']]['K']['data_ptr'] and t['v_cache_data_ptr'] == buffers[t['layer_id']]['V']['data_ptr']
    chunk = (f['rids'][0], f['prefix_lens'][0], f['extend_lens'][0])
    assert chunk in scheduler
    seen = chunks.setdefault(chunk, set())
    assert t['layer_id'] not in seen
    seen.add(t['layer_id'])
assert len(chunks) == len(scheduler) == 169 and all(seen == set(buffers) for seen in chunks.values())
assert {x[0] for x in chunks} == set(by_rid)
terminal_path = evidence / 'admission-B-r2.terminal.json'
terminal = load(terminal_path)
assert terminal['job'] == r['job'] and terminal['uid'] == '85b88b38-cfc2-4903-8aaa-3fc133332f76'
assert terminal['creator'] == 'i-fengyicheng' and terminal['status']['phase'] == 'Failed'
assert terminal['status']['finishTime'] == '2026-11-11T09:29:02Z'
platform_path = evidence / 'terminal-platform-B-r2.json'
terminal_platform = load(platform_path)
assert all(terminal_platform[k] == terminal[k] for k in ('job', 'uid', 'creator', 'status'))
assert terminal_platform['source_mount'] == '100.96.128.195:/data/ycfeng:/data/ycfeng'
assert terminal_platform['preemptible'] == 'no' and terminal_platform['positive_tags'] == ['H800']
assert len(terminal_platform['replicas']) == 1
replica = terminal_platform['replicas'][0]
assert replica['owner_references'][0]['uid'] == terminal['uid'] and replica['phase'] == 'Failed'
assert len(replica['containers']) == 1
container = replica['containers'][0]
assert container['name'] == 'probe' and container['restart_count'] == 0
assert container['state']['terminated']['exitCode'] == 1 and container['state']['terminated']['reason'] == 'Error'
assert container['state']['terminated']['startedAt'] == '2026-11-11T09:22:18Z'
assert container['state']['terminated']['finishedAt'] == '2026-11-11T09:29:00Z'
raw_names = ('result.json', 'preload.json', 'requests.jsonl', 'cache.jsonl', 'comparisons.jsonl', 'server_info.json', 'runtime_metadata.json', 'server.log')
snapshot = {
    'task_id': 'profile-kv-coherence-native-B-r2-20261111',
    'modification_history': [{'date': '2026-11-11', 'change': 'Read-only retained B r2 controls; no collector RCA or native execution.'}],
    'run': str(run), 'baseline': str(baseline), 'job': r['job'], 'uid': terminal['uid'],
    'verdicts': {'controls': 'PASS', 'source_R3_linkage': 'PASS', 'selected_CPP_TP0_joins': 'PASS', 'business_attempt': 'FAIL', 'collector_readback': 'FAIL', 'warm_correctness': 'FAIL', 'complete_fresh_OLD_physical7955_numeric_KV': 'UNVERIFIED', 'formal': 'HOLD'},
    'controls': {'vectors': 16, 'values': 6804, 'max_absolute_error': 0.0, 'max_defined_relative_error': 0.0, 'zero_reference_relative_undefined': 64, 'identity_errors': 0, 'retractions': 0, 'scored': 16, 'flushes': 10, 'comparison_groups': 8, 'comparison_contracts': 24, 'case_columns': ['request_id', 'native_request_id', 'sample_position', 'sample_index', 'source_uid', 'values', 'relative_error_undefined_count'], 'cases': cases},
    'source': {'commit': commit, 'baseline_commit': base_commit, 'r2_identities': 8, 'baseline_identities': 6, 'installed_runtime': file_id(run / 'kv_coherence_source_preflight/after/srt/kv_coherence.py'), 'helper_git_bytes': len(blob), 'helper_git_sha256': sha(blob), 'stage_archives': stages, 'archive_pairs': 97, 'runtime_private_source_paths': 38, 'runtime_archive_hash_overlaps': 7},
    'R3': {'build_receipt_path': str(build_path), 'build_receipt': file_id(build_path), 'qualification_receipt_path': build['qualification_receipt']['path'], 'qualification_receipt': file_id(Path(build['qualification_receipt']['path'])), 'ELF_path': str(library), 'ELF': file_id(library), 'composition_identities': 35, 'private_binary_target': native['binary_target'], 'actual_private_module_mapping': 'UNVERIFIED', 'original_binary_source_commit': 'UNVERIFIED'},
    'runtime': {'local_python': platform.python_version(), 'worker_python': r['runtime']['python'], 'worker_executable': r['runtime']['executable'], 'torch': r['runtime']['torch'], 'sglang': r['runtime']['sglang'], 'gpu_devices': r['runtime']['gpu_devices'], 'argv': r['argv'], 'seed': state['random_seed'], 'baseline_seed': load(baseline / 'server_info.json')['get_server_info']['random_seed'], 'private_package': package, 'model_manifest': r['runtime']['model_manifest_identity']},
    'observations': {'process_id': 347, 'rank': metadata['rank'], 'initial_status': 'metadata_only', 'final_status': 'unverified', 'initial_final_topology_equal': True, 'topology': topology, 'completed_response_bound_rids': 16, 'global_errors': {'count': 140, 'stage_counts': {'note_cpp': 70, 'fresh': 70}, 'rid': None, 'P': 90112, 'E': 98304, 'message': "object of type 'NoneType' has no len()", 'initial_final_equal': True}, 'banks': banks, 'numeric_acceptance': None, 'numeric_summaries': [], 'invalidation_marker_matches': [], 'interpretation': 'Observations only; no collector RCA, complete fresh capture or physical7955/numeric acceptance.'},
    'CPP': {'process_id': 347, 'rank': metadata['rank'], 'unique_joins': 1690, 'explicit_chunks': 169, 'response_bound_rids': 16, 'FULL_layers': sorted(buffers), 'CPP_native_Torch_stream': 1369149904, 'OLD_insert_fragment_Torch_stream': 1369454976, 'OLD_CPP_stream_equivalence': 'UNVERIFIED', 'metadata_rows': 19713, 'startup_rows': 353, 'device_completion': 'UNVERIFIED'},
    'raw_files': {name: file_id(run / name) for name in raw_names}, 'score_files': {name: file_id(run / 'completion_scores' / (name + '.json')) for name in scores},
    'baseline_receipts': {name: file_id(baseline / name) for name in ('result.json', 'requests.jsonl', 'comparisons.jsonl')},
    'config': file_id(Path(r['config']['path'])), 'fixture': file_id(Path(r['fixture']['path'])), 'source_fixture': file_id(Path(r['sample_manifest']['source_fixture']['path'])),
    'failure': {'result_reason': r['reason'], 'readback_status': readback['status'], 'http_status': 200, 'collector_reason': kv['reason'], 'native_measurements_completed': True, 'cleanup_completed': True, 'server_alive_before_cleanup': True, 'shutdown_returncode': -9},
    'terminal_admission': {'path': str(terminal_path), **file_id(terminal_path), 'phase': terminal['status']['phase'], 'finishTime': terminal['status']['finishTime']},
    'terminal_platform': {'path': str(platform_path), **file_id(platform_path), 'status': 'PASS retained primary receipt', 'phase': terminal_platform['status']['phase'], 'source_mount': terminal_platform['source_mount'], 'preemptible': terminal_platform['preemptible'], 'positive_tags': terminal_platform['positive_tags'], 'container': container},
    'limits': ['Retained read-only B r2 only; no platform/auth/GPU/native/delegation/source/config/master-doc/old-report edits or staging/commit.', 'All16/6804 controls exact does not prove complete fresh/OLD capture or warm correctness.', 'Initializer/budget/banks/fragments are observation-only; no physical7955 or numeric KV interpretation.', 'Snapshot/private path and retained ELF hashes are not independent actual private-module/all-TP/alias/GIL/stream/device-completion attestation.', 'Original r1/r2 raw and prior source/CPU/WIT/R3 acceptance remain unchanged; formal HOLD and no B A200 gate.', 'Collector RCA/fix and separately filtered terminal-platform/lifecycle evidence are independently owned.']}
output = evidence / 'native-verification-B-r2.json'
if output.exists():
    assert load(output) == snapshot
    print(json.dumps({'local_verification': 'PASS', 'vectors': 16, 'values': 6804, 'max_abs': 0.0, 'max_defined_rel': 0.0, 'zero_undefined': 64, 'identity_errors': 0, 'scored': 16, 'flushes': 10, 'retractions': 0, 'source_pairs': 97, 'CPP_unique_joins': 1690, 'global_errors': 140, 'banks_observed': 2, 'capture': 'UNVERIFIED', 'formal': 'HOLD'}, sort_keys=True))
else:
    print(json.dumps(snapshot, ensure_ascii=False, indent=2, allow_nan=False))
```

Passing conditions are exactly the bounded assertions above, separately preserving the failed attempt/unverified capture. Actual full local verification PASS:16/6804 exact,maxabs/definedrel0,undefined64,identityerrors0,16scored/10flushes/0retractions,97sourcepairs,1690uniqueCPPjoins,140globalerrors,twoobservedbanks. No assertion interprets KV values. An initial local verifier assumption expected the R3 hash literally inside config; inspected config instead links the receipt path. Verification now checks the exact config-to-actual-receipt path and actual nested/retained receipt SHA separately. No config/source/raw edit or native fix was made. The subsequently provided terminal receipt is an affected-only follow-up; unaffected vectors/source/CPP checks were not broadly rerun.

Observed full local verification output before terminal follow-up:

```json
{"CPP_unique_joins": 1690, "banks_observed": 2, "capture": "UNVERIFIED", "flushes": 10, "formal": "HOLD", "global_errors": 140, "identity_errors": 0, "local_verification": "PASS", "max_abs": 0.0, "max_defined_rel": 0.0, "retractions": 0, "scored": 16, "source_pairs": 97, "values": 6804, "vectors": 16, "zero_undefined": 64}
```

Exact affected-only terminal follow-up command:

```bash
timeout 60s env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
import hashlib, json
root = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111')
e = json.loads((root / 'native-verification-B-r2.json').read_text())
t = json.loads((root / 'terminal-platform-B-r2.json').read_text())
a = json.loads((root / 'admission-B-r2.terminal.json').read_text())
p = Path(e['terminal_platform']['path'])
assert e['terminal_platform']['bytes'] == p.stat().st_size == 1756
assert e['terminal_platform']['sha256'] == hashlib.sha256(p.read_bytes()).hexdigest() == '60d209d801d5be04c85f445a377c1b5067a755846cf4cd5cc390ab7ea1844758'
assert all(t[k] == a[k] for k in ('job', 'uid', 'creator', 'status'))
assert t['job'] == e['job'] and t['uid'] == e['uid'] and t['creator'] == 'i-fengyicheng'
assert t['status']['phase'] == e['terminal_platform']['phase'] == 'Failed'
assert t['status']['finishTime'] == '2026-11-11T09:29:02Z'
assert t['source_mount'] == e['terminal_platform']['source_mount'] == '100.96.128.195:/data/ycfeng:/data/ycfeng'
assert t['preemptible'] == e['terminal_platform']['preemptible'] == 'no'
assert t['positive_tags'] == e['terminal_platform']['positive_tags'] == ['H800']
assert len(t['replicas']) == 1 and t['replicas'][0]['owner_references'][0]['uid'] == e['uid']
assert len(t['replicas'][0]['containers']) == 1
c = t['replicas'][0]['containers'][0]
assert c == e['terminal_platform']['container'] and c['name'] == 'probe' and c['restart_count'] == 0
assert c['state']['terminated']['exitCode'] == 1 and c['state']['terminated']['reason'] == 'Error'
assert c['state']['terminated']['startedAt'] == '2026-11-11T09:22:18Z'
assert c['state']['terminated']['finishedAt'] == '2026-11-11T09:29:00Z'
assert e['terminal_platform']['status'] == 'PASS retained primary receipt'
print('PASS: retained B r2 terminal/admission/job-UID-owner/source-mount/container Error/exit1/restart0; native capture remains UNVERIFIED.')
PY
```

Scoped whitespace commands:

```bash
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_B_r2_results.md
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-B-r2.json
```

Observed terminal-only follow-up: **PASS**; both new files emitted no whitespace diagnostics (expected`--no-index` new-file diff exit1). Neither check executes native code or modifies raw evidence.

```text
PASS: retained B r2 terminal/admission/job-UID-owner/source-mount/container Error/exit1/restart0; native capture remains UNVERIFIED.
```

## 1. 规划完成情况

**汇总：** PASS4｜BLOCKED/FAILED/SKIPPED2｜TODO0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| B r2原始control向量/identity | PASS |16/6804 exact，16scored/10flushes，identityerrors0 |
| B r2冻结source/R3/CPP与观察记录 | PASS |6119/4f1139、97pairs、1690身份join；不解释KV |
| 两份指定新产物 | PASS |report/JSON待primary acceptance，无stage/commit |
| B r2独立capture | FAILED |140全局errors，readbackunverified |
| OLD/physical7955/完整fresh/numeric验收与04/05 | BLOCKED |观察不是物理/数值证明；formal HOLD |
| 单独terminal-platform容器核验 | PASS |随后primary提供本地receipt，Error/exit1/restart0，job/UID/owner/mount匹配 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** B r2委托至两份产物交付｜**当前前沿：** primary接受control/观察边界；collector owner独立RCA/fix。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR |仅本r2接受条件的read-only报告内命令，无永久framework/广测 |
| D2 细节反复重试 | CLEAR |无native重试；systemd bus不可用后使用有界本地resource检查 |
| D3 支线问题修补 | CLEAR |无collector RCA/fix、source/config/shared docs编辑 |
| D4 可并行任务停滞 | CLEAR |B-only交付，不等A/terminal；独立owner继续 |
| D5 超范围镀金 | CLEAR |仅两份新owned产物，旧证明不改 |
| D6 分析空转 | CLEAR |exact/failed/observation-only边界与证据交付 |
| D7 路线违背 | CLEAR |不解释KV、不接受physical7955，formal HOLD/B noA200不变 |

**文档检查：** S1–S4/S6未发现明显缺陷；S5：初读`requirements.md:3`、`plan.md:3`、`tickets/05-b-full.md:3`仍为Initial Starting，与已保留Failed终态相异。Primary同步共享状态，本分工不编辑。
**归因：** 无执行偏离；状态同步由primary拥有。

## 3. 纠正建议

**分支：** B：更新共享状态记录，原scope/验收条件不变。

**文档更新（先执行）：**
1. Primary同步requirements/plan/progress/Ticket05当前终态和control/capture/观察边界（可直接执行；primary ownership）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Primary接受B r2两份产物 → 完成标志：control PASS与capture FAIL/UNVERIFIED分开记录。
2. 并行：collector owner RCA/fix ‖ A r2 retained control verification ‖ primary terminal receipt；不授予新native submission。
3. 原有physical/numeric → teacher RCA/minimal fix/warm correctness → fresh independent A‖B200 →06；B无A200 gate。

## 4. 最值得关注的 3 点

1.16/6804 exact、0retractions不能证明完整fresh/OLD capture或warm correctness。
2.Topology与two banks/warm fragments是观察；140RIDnull全局错误保持，physical7955/numeric仍UNVERIFIED。
3.只在responding process347/TP0核验CPP，private ELF/path/hash与无marker不替代实际模块/alias/stream/allTP证明。
