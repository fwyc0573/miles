## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Independently verify retained A scoring, frozen source/R3 staging and selected CPP receipts; separate auxiliary capture failure from unchanged numerical/formal holds. |
| 2026-11-11 | Record primary's limited acceptance, correct the six guard settings and bind archival recomputation to immutable Git helper bytes rather than the later working tree. |
| 2026-11-11 | Primary independently reruns the frozen verifier and confirms exact JSON artifact equality after the live helper changed; bounded controls only remain accepted. |

# KV coherence native A retained-result verification

TaskID: `profile-kv-coherence-native-A-20261111`.

## Outcome and scope

Primary independently reran the verifier below with `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B` and a 60-second timeout. JSON equality with `native-verification-A.json` passed in 2.800 seconds; all16/6,804 baseline reproduction, 194 archive hash checks and the absence of a working-tree identity gate were confirmed. Capture/warm FAIL, physical/KV UNVERIFIED and formal HOLD were preserved.

**PASS: all16 logical completion vectors /6,804 values reproduce the accepted original metadata A baseline exactly. FAIL: independent KV capture qualification. UNVERIFIED: original Rust OLD GPU callback, new observer stream, physical indices/7,955 overlap and KV numerical coherence.** Cold parity remains4/4 exact; warm parity remains1/4 exact. This does not release formal04/05 HOLD or accept a training/root-math fix, performance, original56/two-repeat coverage, all-TP agreement or200 updates.

Primary accepted the actual bounded A retained controls/source/selected CPP evidence, four-H800 worker receipt and failed-terminal consistency on2026-11-11. This is **limited evidence acceptance, not overall KV diagnostic PASS**. The auxiliary capture FAIL, warm1/4 FAIL, absent OLD/new-stream/7,955/KV proof and formal HOLD remain unchanged.

Actual job `exp-1111-162637-295253` is Failed at `2026-11-11T08:33:20Z`. Its `result.json` nevertheless records `native_measurements_completed=true`, `cleanup_completed=true`,16 scored requests, `numerical_acceptance=null`, `performance_accepted=false`. The failure is **auxiliary capture qualification after healthy teacher scoring**, not native scoring/training failure or evidence that the teacher's original warm drift has changed.

Owned result: [native-verification-A.json](evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-A.json). Baseline: `evidence/teacher-scoring-runtime-metadata-probe-20261111/native/A/admission-A-r1`. All raw artifacts, original R2/CPU/WIT acceptance and scientific decisions remain unchanged. The initializer/config RCA has a separate owner; this report does not duplicate it or implement a fallback.

## Observations and acceptance boundaries

| Required check | Observed | Verdict |
| --- | --- | --- |
| Exact logical baseline join | Existing `sglang_kv_coherence.compare_completion_vectors`; `(pair,phase,mode,source_uid,sample_index,repetition)`,16/16 vectors,6,804 values on each side | PASS |
| IDs/shapes/finite values |16 unique request IDs and16 unique response RIDs; every RID equals vector RID and `meta_info.id`; exact fixture completion token IDs; full N versus response-only R+1; null first logprob and correct first token | PASS; identity/shape/nonfinite errors0 |
| Exact error accounting | Maximum absolute0 / maximum defined relative0 across6,780 defined elements;24 zero-reference entries have undefined relative error, including0 vs0 | PASS; no tolerance |
| Unchanged protocol | Original first4 / repetition0 /16 requests /10 HTTP200 flushes and10 server confirmations; no salt, no generated tokens, no retractions | PASS |
| Original comparisons | All8 records byte-for-byte equal baseline;40 comparison groups independently recomputed, including16 historical comparisons | PASS, reproduction only |
| Cold versus warm mathematics | Cold4/4 exact; warm1/4 exact,3 different | Cold PASS; warm FAIL unchanged |
| Frozen source/probe | Eight native scoring-source hashes/lengths equal immutable `b9e1ebb6` blobs; config/first4 manifest also match frozen blobs. Working-tree equality was observed only at the initial verification | PASS, frozen source identity; later working-tree identity is not a gate |
| Composed source archives | FP32 six, metadata16, WIT35, coherence40 files; both archived sides and source-owned rewrites checked, including unchanged final six attention sources | PASS, source/staging only |
| Selected R3 | Real nested `native_observer`, selected receipt15,835 bytes/SHA91458ef…; source17cb6fc6/helperacf89c…;22+22 Rust source files, two retained ELFs and linked receipts checked | PASS, accepted CPU prerequisite only |
| Private package | Whole private runtime import origin/child PYTHONPATH and same-name extension target are recorded; compiled ELF SHA0dc763… matches retained artifact | PASS for recorded staging; actual GPU callback origin/hash UNVERIFIED |
| Worker hardware/environment | Actual retained worker runtime reports four NVIDIA H800,81559 MiB each, driver570.124.06; Python3.12.16 `/opt/sglang/bin/python3`, Torch2.14.1+cu130, SGLang0.5.24.dev80+g056f871 | PASS within worker receipt scope, not an H800 template-label inference |
| Teacher argv/model identity | TP4/BF16/context131072/memory0.85/concurrency1/chunk8192/fa3/Triton/deterministic/graphs disabled; baseline argv unchanged except distributed address; model manifest identities unchanged | PASS, no whole-weight checksum |
| Selected CPP normal-store receipts | Unique existing six-field CPP/terminal join, explicit RID/prefix/extend scheduler joins,16 actual FULL layers | PASS only for selected in-call CPP scalar/terminal coverage; not Rust observer/new-stream/KV capture |
| Collector readback | HTTP200 but `kv_coherence.status=unverified`, no topology/banks/payload/summaries; exact preallocation ValueError retained | FAIL, auxiliary capture qualification |
| Terminal platform/container | Primary's independent retained receipt binds owner job UID, Failed/container Error exit1/restart0; system-stop annotation explicitly recorded | PASS, terminal evidence consistency; job itself FAILED |

### Numerical values

Each cell is **maximum absolute logprob error / maximum defined relative error**. Relative error is undefined wherever the reference is zero; one such entry for samples1693–1695 and three for1696 per comparison. No tolerance or probability-space conversion is used.

| Sample index / N,R | Warm full versus response | Own cold full versus warm full | Own cold response versus warm response |
| --- | --- | --- | --- |
|1693 /97365,734 |0 /0 |0 /0 |0 /0 |
|1694 /98312,246 |7.152048056013882e-7 /0.14285706500614642 |2.3841676011215895e-7 /0.04545451786888886 |7.152048056013882e-7 /0.14285706500614642 |
|1695 /98942,431 |0.19622063636779785 /0.6111100632456284 |0.17278575897216797 /0.2727263348137287 |0.1781916618347168 /0.9333317481132808 |
|1696 /99074,290 |0.24439287185668945 /1.3806473175677756 |0.12412643432617188 /0.6187940669273067 |0.1765437126159668 /1.0611983494486865 |

### Capture failure and terminal evidence

`runtime_metadata.json` retains85,026,768 bytes, including the exact server response, typed Mamba/WIT metadata and the failed collector receipt. Size is not evidence of a KV tensor payload. Startup `server_info.json` uses wrapper `get_server_info`; its six actual guard settings are present: `disable_cuda_graph=true`, `page_size=1`, `enable_memory_saver=false`, `enable_unified_memory=false`, `enable_hierarchical_cache=false`, `enable_unified_cache_external_linker=false`. Additional cache/workload geometry is checked separately: `disable_radix_cache=false`, `chunked_prefill_size=8192`, `max_running_requests=1`. These final readbacks do not retroactively prove the collector's initializer observed them.

Separate initializer/source RCA, supplied by primary in the2026-11-11 follow-up, records sealed raw `page_size=None`, resolved `page_size=1` and no later mutation. This is a reference to that owner's finding, not a duplicate RCA or a change to original A evidence; the fix owner retains the source/RCA scope.

Both startup and post-loop collector receipts preserve:

```text
stage=preallocation
error_type=ValueError
message=Collector actual graph/page/memory/cache config differs from qualified WIT
reason=Responding collector unavailable; no device readback
```

This is the retained `_startup_error` path, before a usable collector/topology/banks result. There are no original OLD callbacks, physical index-equality receipts,7,955 OLD coverage, cold-zero OLD coverage, K/V statistics or numerical acceptance to inspect. Source staging and successful vectors do not substitute for those absent receipts.

The primary's [terminal-platform-A.json](evidence/teacher-scoring-kv-coherence-probe-20261111/terminal-platform-A.json), observed `2026-11-11T08:38:00.940906+00:00`, independently records Failed job/replica, container Error/exit1/restart0 and owner UID `8f26af09-bb4b-4f67-b60b-f9d58aefaf44`. Container finished `2026-11-11T08:32:14Z`; job finished08:33:20Z. Its explicit `rjob.brainpp.cn/system-stop-reason="Some critical tasks failed."` is platform evidence. `server_returncode_before_cleanup=null`, `server_shutdown_returncode=-9`, `cleanup_completed=true` describe caller-owned child cleanup, **not** platform stop or main-container exit. This verifier made no platform/auth operation. The terminal receipt does not independently attest imageID; configured image/mount inputs remain qualified as such.

### Source and selected CPP scope

R3 selection is the nested `kv_coherence_source_preflight.native_observer`, not a flattened/native observer stand-in. Exact selected build receipt SHA256: `91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7`. Helper source SHA256: `acf89c7425ba38a0a497adfd27cf2fe71979f77922d7af5f6b66a6685175442d`, matching `17cb6fc66fa8b5e866c0c83d5f5c93cf971ac898` and immutable `b9e1ebb6` bytes. Current-byte equality was an initial, time-bounded observation only. Staged production module is `sglang.srt.mem_cache.rust_tree_core.mem_cache`; retained observer ELF SHA256 is `0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba`. Actual GPU-side callback module origin/new SO hash is absent. Original bundled binary source commit remains UNVERIFIED. No native extension import, Cargo test, compile or GPU callback is executed locally.

CPP rows are joined only by `(rids,prefix_lens,extend_lens,k_cache_data_ptr,v_cache_data_ptr,writer_loc_data_ptr)` in the same responding process/rank, following the accepted [A WIT join schema](test_report_2026-11-11_kv_stream_witness_native_A_results.md#process-local-metadata-and-joins). Scheduler joins then use explicit `(RID,prefix,extend)` with uniqueness and `seq_end=prefix+extend`. Sequence adjacency, tensor object IDs and node-only equality are never joins. Plain terminal receipts keep their own scalar flag false; the uniquely matched **CPP in-call** row supplies its separate scalar. These old WIT receipts do not attest new Rust OLD callbacks, observer stream, device completion, physical KV values or all-TP coherence.

## Exact local verification

Workdir: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Local interpreter `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13; `CONDA_DEFAULT_ENV` unset. Standard-library JSON/hash/AST plus existing pure helper definitions from immutable Git blobs. Timeout60s and `RLIMIT_AS=30GiB`; no conda activation, dependency change, network/platform/auth/GPU/native execution, new broad tests, stage/commit or shared-document edit. Source rewrites below only compute bytes in memory; no preparer/builder/capture method runs. Hashing is confined to this A run, its selected baseline files and22-file R3 source maps/linked receipts, not a5501/621 sweep.

Initial host-only attempts retained these errors: bare `python` was unavailable (`zsh:1: command not found: python`, exit127); `systemd-run --user --scope -p MemoryMax=30G` failed before Python (`Failed to connect to bus: No such file or directory`); non-user `systemd-run --scope` failed before Python (`Interactive authentication required`). No authentication was attempted. The successful local inspection uses timeout/RLIMIT only, without runtime behavior changes.

Recompute the result on stdout, without writing files:

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'from pathlib import Path; p=Path("task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_A_results.md"); exec(compile(p.read_text().split("```python\n",1)[1].split("\n```",1)[0],str(p)+":verifier","exec"))'
```

```python
import difflib, hashlib, json, math, os, resource, subprocess, sys, types
from collections import Counter, defaultdict
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
task = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
base = task / 'evidence/teacher-scoring-kv-coherence-probe-20261111'
run = base / 'native/A/admission-A-r1'
baseline = task / 'evidence/teacher-scoring-runtime-metadata-probe-20261111/native/A/admission-A-r1'
snapshots = {}
def content(path):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if path in snapshots: assert snapshots[path] == digest
    snapshots[path] = digest
    return raw
read_json = lambda p: json.loads(content(p))
read_lines = lambda p: [json.loads(x) for x in content(p).decode().splitlines()]
sha = lambda p: hashlib.sha256(content(p)).hexdigest()
fixed = lambda ref, p: subprocess.check_output(['git', 'show', f'{ref}:{p}'])
commit = subprocess.check_output(['git', 'rev-parse', 'b9e1ebb6']).decode().strip()
frozen_sources = {}
def source_blob(path):
    blob = fixed(commit, path)
    digest = hashlib.sha256(blob).hexdigest()
    if path in frozen_sources: assert frozen_sources[path] == digest
    frozen_sources[path] = digest
    return blob
result, preload, old_result = (read_json(p) for p in (run/'result.json', run/'preload.json', baseline/'result.json'))
terminal = read_json(base / 'admission-A-r1.terminal.json')
assert result['job'] == terminal['job'] == 'exp-1111-162637-295253'
assert result['status'] == 'failed' and result['native_measurements_completed'] and result['cleanup_completed']
assert result['numerical_acceptance'] is None and result['performance_accepted'] is False
assert terminal['status']['phase'] == 'Failed' and terminal['status']['finishTime'] == '2026-11-11T08:33:20Z'
assert terminal['native_execution_succeeded'] is False
source_ids = {}
for path, identity in result['native_scoring_sources'].items():
    blob = source_blob(path)
    assert len(blob) == identity['bytes'] and hashlib.sha256(blob).hexdigest() == identity['sha256']
    source_ids[path] = identity['sha256']
assert len(source_ids) == 8 and result['native_scoring_sources'] == preload['native_scoring_sources']
for name in ('tests', 'tests.manual', 'tests.manual.agent_opd'):
    module = types.ModuleType(name); module.__path__ = []; sys.modules[name] = module
for name in ('probe_teacher_scoring', 'sglang_mamba_snapshots', 'sglang_mamba_runtime_metadata',
             'sglang_kv_streams', 'sglang_kv_coherence', 'sglang_rust_kv_observer'):
    path = f'tests/manual/agent_opd/{name}.py'
    module = types.ModuleType('tests.manual.agent_opd.' + name)
    blob = source_blob(path)
    module.__file__ = f'{commit}:{path}'
    sys.modules[module.__name__] = module; setattr(sys.modules['tests.manual.agent_opd'], name, module)
    exec(compile(blob, f'{commit}:{path}', 'exec'), module.__dict__)
probe = sys.modules['tests.manual.agent_opd.probe_teacher_scoring']
coherence = sys.modules['tests.manual.agent_opd.sglang_kv_coherence']
native = sys.modules['tests.manual.agent_opd.sglang_rust_kv_observer']
witness = sys.modules['tests.manual.agent_opd.sglang_kv_streams']
frozen_helper = source_blob('tests/manual/agent_opd/sglang_kv_coherence.py').decode()
def frozen_helper_path(path):
    assert path == coherence.__file__
    return types.SimpleNamespace(read_text=lambda: frozen_helper)
# Reuse the frozen function unchanged, with its self-source read bound to Git bytes.
coherence._runtime_source = types.FunctionType(coherence._runtime_source.__code__,
    {**coherence.__dict__, 'Path': frozen_helper_path}, '_runtime_source')
compare = probe._comparison
gate = coherence.compare_completion_vectors(run, baseline)
assert gate['all16_6804_exact'] and gate['vectors'] == 16
assert gate['baseline_values'] == gate['candidate_values'] == 6804
assert sum(c['relative_error_undefined_count'] for c in gate['comparisons']) == 24
for field in ('fixture', 'config'):
    identity = result[field]; path = Path(identity['path'])
    assert identity == preload[field] and sha(path) == identity['sha256']
    assert len(content(path)) == identity['bytes'] and content(path) == fixed(commit, str(path.relative_to(Path.cwd())))
fixture_identity = result['sample_manifest']['source_fixture']
fixture_path = Path(fixture_identity['path'])
assert sha(fixture_path) == fixture_identity['sha256'] == 'c45424e8106c2beb7500acacb68aa0939da0088c926af8012dd9fbd780f0ffc9'
samples = read_json(fixture_path)['samples'][:4]
requests, old_requests, cache, comparisons = (read_lines(p) for p in
    (run / 'requests.jsonl', baseline / 'requests.jsonl', run / 'cache.jsonl', run / 'comparisons.jsonl'))
key_fields = ('pair', 'phase', 'mode', 'source_uid', 'sample_index', 'repetition')
key = lambda r: tuple(r[k] for k in key_fields)
assert len(requests) == len({r['request_id'] for r in requests}) == len({r['native_request_id'] for r in requests}) == 16
assert [key(r) for r in requests] == [key(r) for r in old_requests]
assert len(list((run / 'completion_scores').glob('*.json'))) == 16
vectors, identities = {}, []
for r, old in zip(requests, old_requests):
    sample = samples[r['sample_position']]; n, length = len(sample['tokens']), sample['response_length']
    start = 0 if r['mode'] == 'full_input' else n-length-1
    assert (r['source_uid'], r['sample_index']) == (sample['source_uid'], sample['sample_index'])
    assert r['status'] == 'scored' and r['http_status'] == 200 and r['cache_salt'] is None and r['repetition'] == 0
    assert (r['input_count'], r['prompt_count'], r['response_count'], r['logprob_start_len']) == (n,n-length,length,start)
    assert r['input_token_logprobs_count'] == r['expected_input_token_logprobs_count'] == n-start
    assert r['first_input_token_logprob'] is None and r['first_input_token_id'] == r['first_requested_input_token_id'] == sample['tokens'][start]
    assert r['returned_completion_count'] == length and r['token_ids_match'] and r['finite_log_probs']
    assert r['completion_token_id_mismatches'] == r['nonfinite_log_prob_positions'] == []
    assert r['meta_info']['completion_tokens'] == r['meta_info']['output_token_logprobs_length'] == r['meta_info']['num_retractions'] == 0
    v = read_json(run / 'completion_scores' / f"{r['request_id']}.json")
    previous = read_json(baseline / 'completion_scores' / f"{old['request_id']}.json")
    assert key(v) == key(r) and v['request_id'] == r['request_id']
    assert r['native_request_id'] == v['native_request_id'] == r['meta_info']['id']
    assert v['token_ids'] == previous['token_ids'] == sample['tokens'][-length:]
    assert len(v['token_ids']) == len(v['log_probs']) == length and all(math.isfinite(x) for x in v['log_probs'])
    assert v['log_probs'] == previous['log_probs'] and r['native_request_id'] != old['native_request_id']
    vectors[r['request_id']] = v
    identities.append({'request_id': r['request_id'], 'native_request_id': r['native_request_id'],
                       'sample_index': r['sample_index'], 'completion_values': length})
assert len(cache) == 10 and all(c['status'] == 'flushed' and c['http_status'] == 200 for c in cache)
assert content(run / 'server.log').decode().count('Cache flushed successfully!') == 10
assert len(comparisons) == 8 and content(run / 'comparisons.jsonl') == content(baseline / 'comparisons.jsonl')
recomputed = 0; warm_errors = []
error = lambda c: [c['max_absolute_error'], c['max_relative_error'], c['relative_error_undefined_count']]
for row in comparisons:
    full, response = vectors[row['full_request_id']], vectors[row['response_request_id']]
    assert compare(full,response) == row['full_vs_response_only']; recomputed += 1
    if row['cold_reference']:
        ref = row['cold_reference']; cf, cr = vectors[ref['full_request_id']], vectors[ref['response_request_id']]
        for name,left,right in [('cold_full_vs_warm_full',cf,full), ('cold_full_vs_warm_response_only',cf,response),
                                ('cold_response_only_vs_warm_full',cr,full), ('cold_response_only_vs_warm_response_only',cr,response)]:
            assert compare(left,right) == ref[name]; recomputed += 1
        warm_errors.append({'sample_index':row['sample_index'], 'warm_full_vs_response':error(row['full_vs_response_only']),
                            'cold_full_vs_warm_full':error(ref['cold_full_vs_warm_full']),
                            'cold_response_vs_warm_response':error(ref['cold_response_only_vs_warm_response_only'])})
    sample = samples[row['sample_position']]
    expected = {'token_ids':sample['tokens'][-sample['response_length']:], 'log_probs':sample['expected_teacher_log_probs']}
    for name,v in [('full_input',full),('response_only',response)]:
        assert compare(expected,v) == row['historical_expected'][name]; recomputed += 1
assert recomputed == 40
assert sum(c['full_vs_response_only']['values_exact'] for c in comparisons if c['phase']=='cold') == 4
assert sum(c['full_vs_response_only']['values_exact'] for c in comparisons if c['phase']=='warm_stream') == 1
source_counts, archive_checks = {}, 0
for stage in ('source_preflight','runtime_metadata_source_preflight','kv_store_stream_source_preflight'):
    receipt = result[stage]
    assert receipt == preload[stage] == read_lines(run/stage/'preflight.jsonl')[-1]
    assert read_json(run/stage/'source_manifest.json')['files'] == receipt['files']
    source_counts[stage] = len(receipt['files'])
    for relative, identity in receipt['files'].items():
        for side in ('before','after'):
            assert sha(run/stage/side/relative) == identity[f'{side}_sha256'] == receipt[f'observed_{side}_sha256'][relative]
            archive_checks += 1
assert list(source_counts.values()) == [6,16,35] and archive_checks == 114
wit_receipt = result['kv_store_stream_source_preflight']
for relative,identity in witness.source_manifest()['files'].items():
    before = content(run/'kv_store_stream_source_preflight/before'/relative)
    after = content(run/'kv_store_stream_source_preflight/after'/relative)
    witness._qualified_baseline(relative,before,identity)
    assert witness._rewrite(relative,before) == after
for relative in result['source_preflight']['files']:
    assert result['runtime_metadata_source_preflight']['observed_before_sha256'][relative] == result['source_preflight']['observed_after_sha256'][relative]
for relative,digest in result['runtime_metadata_source_preflight']['observed_after_sha256'].items():
    assert wit_receipt['observed_before_sha256'][relative] == digest
receipt = result['kv_coherence_source_preflight']; package = result['kv_coherence_package']
assert receipt == preload['kv_coherence_source_preflight'] == read_lines(run/'kv_coherence_source_preflight/preflight.jsonl')[-1]
assert read_json(run/'kv_coherence_source_preflight/source_manifest.json') == receipt['manifest'] == coherence.source_manifest()
assert package == preload['kv_coherence_package'] and receipt['package_root'] == package['package_root']
private = Path(package['package_root'])
assert private != Path(package['source_package_root']) and package['import_origin'] == str(private/'__init__.py')
assert package['child_pythonpath'].split(':')[0] == str(private.parent)
assert all(Path(v['path']).is_relative_to(private) for v in result['runtime']['sglang_sources'].values())
coherence_before, coherence_after = {}, {}
for relative,digest in receipt['observed_after_sha256'].items():
    before = content(run/'kv_coherence_source_preflight/before'/relative)
    after = content(run/'kv_coherence_source_preflight/after'/relative)
    assert hashlib.sha256(after).hexdigest() == digest
    assert after == (coherence._runtime_source() if relative=='srt/kv_coherence.py' else coherence._rewrite(relative,before))
    if relative in result['kv_store_stream_source_preflight']['files']:
        assert hashlib.sha256(before).hexdigest() == result['kv_store_stream_source_preflight']['observed_after_sha256'][relative]
    elif relative in receipt['manifest']['additional_native_sha256']:
        assert hashlib.sha256(before).hexdigest() == receipt['manifest']['additional_native_sha256'][relative]
    else: assert relative == 'srt/kv_coherence.py' and before == b''
    coherence_before[relative], coherence_after[relative] = before,after; archive_checks += 2
assert len(coherence_after) == 40 and archive_checks == 194
diff = ''.join(''.join(difflib.unified_diff(coherence_before[p].decode().splitlines(True),coherence_after[p].decode().splitlines(True),fromfile=f'a/{p}',tofile=f'b/{p}')) for p in coherence_before if coherence_before[p]!=coherence_after[p])
assert content(run/'kv_coherence_source_preflight/coherence.diff').decode() == diff
for relative in result['source_preflight']['files']:
    assert result['source_preflight']['observed_after_sha256'][relative] == old_result['source_preflight']['observed_after_sha256'][relative]
    assert receipt['observed_after_sha256'][relative] == old_result['runtime_metadata_source_preflight']['observed_after_sha256'][relative]
runtime_matches = 0
for relative,identity in result['runtime']['sglang_sources'].items():
    if relative in receipt['observed_after_sha256']:
        assert identity['sha256'] == receipt['observed_after_sha256'][relative]; runtime_matches += 1
native_receipt = receipt['native_observer']; build_path = Path(native_receipt['build_receipt'])
assert native_receipt == read_json(run/'kv_coherence_source_preflight/native_observer/preflight.json')
assert sha(build_path) == native_receipt['build_receipt_sha256'] == '91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7'
assert build_path.parent.name == 'native-rust-kv-observer-qualification-20261111-r3' and len(content(build_path)) == 15835
build = read_json(build_path); r3 = read_json(build_path.parent/'native-verification.json')
assert build['status'] == build['qualification']['status'] == 'PASS' and build['module'] == native_receipt['module'] == native.MODULE
assert native_receipt['package_root'] == str(private) and Path(native_receipt['binary_target']).is_relative_to(private)
assert native_receipt['compiled_sha256'] == build['observer']['sha256']
assert native_receipt['composition'] == {p:{'bytes':len(content(run/'kv_store_stream_source_preflight/after'/p)), 'sha256':d} for p,d in result['kv_store_stream_source_preflight']['observed_after_sha256'].items()}
assert native_receipt['adapter_before_sha256'] == build['source_manifest']['adapter_before_sha256']
assert native_receipt['adapter_after_sha256'] == build['source_manifest']['adapter_after_sha256']
sha(run/'kv_coherence_source_preflight/native_observer/adapter.patch')
rust_source_checks = 0
for variant,side in [('baseline','before'),('observer','after')]:
    library = Path(build[variant]['path']); raw = content(library)
    assert raw.startswith(b'\x7fELF') and hashlib.sha256(raw).hexdigest() == build[variant]['sha256']
    for relative,identity in build['source_manifest'][side].items():
        p = Path(build[variant]['workspace'])/relative; raw = content(p)
        assert len(raw) == identity['bytes'] and hashlib.sha256(raw).hexdigest() == identity['sha256']
        if side == 'before': assert identity['sha256'] == native._RUST_PINS[relative]
        rust_source_checks += 1
assert rust_source_checks == 44
for relative in native._RUST_PINS:
    before = content(Path(build['baseline']['workspace'])/relative)
    after = content(Path(build['observer']['workspace'])/relative)
    assert native._rust_candidate(relative,before) == after
for identity in [*build['input_receipts'].values(),build['qualification_receipt']]:
    p = Path(identity['path']); assert len(content(p)) == identity['bytes'] and sha(p) == identity['sha256']
assert read_json(Path(build['qualification_receipt']['path'])) == build['qualification']
source = r3['source_identity']; r3ref = source['native_code_ref']
assert r3ref == '17cb6fc66fa8b5e866c0c83d5f5c93cf971ac898' and source['final_build_sha256'] == sha(build_path)
for name,digest in [('sglang_rust_kv_observer.py',source['helper_sha256']),('probe_rust_kv_observer.py',source['probe_sha256'])]:
    p = Path('tests/manual/agent_opd')/name; blob = fixed(r3ref,str(p))
    assert hashlib.sha256(blob).hexdigest() == digest and blob == source_blob(str(p))
assert source['helper_sha256'] == 'acf89c7425ba38a0a497adfd27cf2fe71979f77922d7af5f6b66a6685175442d'
frozen_r2 = task/'evidence/rust-kv-observer-qualification-receipts-20261111/observer-build-r2.json'
assert sha(frozen_r2) == '4c967246e2cb3ab54e454b87f1a22231c73a7829037dbd98f19ad19bfb2e017b'
assert content(frozen_r2) == content(task/'evidence/native-rust-kv-observer-build-20261111/observer-build.json')
runtime = result['runtime']; assert runtime == preload['runtime']
assert (runtime['python'],runtime['executable'],runtime['sglang'],runtime['torch']) == ('3.12.16','/opt/sglang/bin/python3','0.5.24.dev80+g056f871','2.14.1+cu130')
assert runtime['gpu_devices'] == ['NVIDIA H800, 81559 MiB, 570.124.06']*4
assert runtime['model_manifest_identity'] == old_result['runtime']['model_manifest_identity']
without_address = lambda a: [v for i,v in enumerate(a) if i==0 or a[i-1]!='--dist-init-addr']
assert without_address(result['argv']) == without_address(old_result['argv'])
initial_info = read_json(run/'server_info.json')['get_server_info']; metadata = read_json(run/'runtime_metadata.json')
post_info = metadata['server_info']; assert len(initial_info['internal_states']) == len(post_info['internal_states']) == 1
settings = {'disable_cuda_graph':True,'page_size':1,'enable_memory_saver':False,'enable_unified_memory':False,'enable_hierarchical_cache':False,'enable_unified_cache_external_linker':False}
assert {k:initial_info[k] for k in settings} == {k:post_info[k] for k in settings} == settings
geometry = {'disable_radix_cache':False,'chunked_prefill_size':8192,'max_running_requests':1}
assert {k:initial_info[k] for k in geometry} == {k:post_info[k] for k in geometry} == geometry
assert (post_info['dp_size'],post_info['tp_size'],post_info['pp_size']) == (1,4,1)
post_state, initial_state = post_info['internal_states'][0], initial_info['internal_states'][0]
kv = post_state['kv_coherence']; expected_error = {'stage':'preallocation','error_type':'ValueError','message':'Collector actual graph/page/memory/cache config differs from qualified WIT'}
assert kv == initial_state['kv_coherence'] and kv['status']=='unverified' and kv['errors']==[expected_error]
assert kv['reason']=='Responding collector unavailable; no device readback' and kv['numeric_acceptance'] is None
assert not any(k in kv for k in ('topology','banks','summaries','payload','buffers'))
assert metadata['status']==result['runtime_metadata']['status']=='failed' and metadata['http']['http_status']==200
assert result['kv_coherence']['summaries']==[] and result['kv_coherence']['status']=='failed'
m = post_state['mamba_runtime_metadata']; initial_m = initial_state['mamba_runtime_metadata']
assert m['process_id'] == initial_m['process_id'] == kv['process_id'] == 340
assert m['rank'] == initial_m['rank'] == {'dp_rank':None,'tp_rank':0,'pp_rank':0,'attn_dp_rank':0,'attn_tp_rank':0}
def decoded(rows):
    output=[]
    for seq,event,fields in rows:
        assert len(fields)==len(dict(fields)); output.append((seq,event,dict(fields)))
    return output
rows, startup = decoded(m['rows']),decoded(initial_m['rows'])
streams, terminals, chunks, boundaries = (defaultdict(list) for _ in range(4))
join = lambda f: (tuple(f['rids']),tuple(f['prefix_lens']),tuple(f['extend_lens']),f['k_cache_data_ptr'],f['v_cache_data_ptr'],f['writer_loc_data_ptr'])
for seq,event,f in rows:
    if event=='kv_store_stream':
        assert f['store_kind']=='cpp_store_cache' and f['native_stream_scalar_observed'] and f['launch_enqueued']
        assert type(f['native_actual_stream']) is int and f['native_actual_stream']>=0 and f['native_actual_stream']==f['torch_current_raw_stream']
        streams[join(f)].append((seq,f))
    if event=='kv_store_terminal':
        assert f['store_kind']=='mha_set_kv_buffer_impl' and f['native_stream_scalar_observed'] is False and f['native_actual_stream'] is None
        assert len(f['rids'])==len(f['prefix_lens'])==len(f['extend_lens'])==1
        terminals[join(f)].append((seq,f)); chunks[(f['rids'][0],f['prefix_lens'][0],f['extend_lens'][0])].append((seq,f))
    if event=='scheduler_track_boundary': boundaries[(f['rid'],f['prefix_len'],f['extend_len'])].append((seq,f))
assert len(streams)==len(terminals)==2704 and set(streams)==set(terminals)
assert all(len(v)==1 for v in [*streams.values(),*terminals.values()])
assert len(chunks)==len(boundaries)==169 and set(chunks)==set(boundaries)
assert {k[0] for k in chunks}=={r['native_request_id'] for r in requests}
layers=list(range(3,64,4))
for k,chunk in chunks.items():
    assert len(chunk)==16 and sorted(f['layer_id'] for _,f in chunk)==layers
    assert len(boundaries[k])==1 and boundaries[k][0][1]['seq_end']==k[1]+k[2]
    for seq,f in chunk:
        cpp=streams[join(f)][0][1]
        assert f['pool_class']==['sglang.srt.mem_cache.memory_pool','MHATokenToKVPool']
        assert f['pool_layer_id']==f['buffer_layer_idx']==(f['layer_id']-3)//4
        assert f['writer_loc'][1:]==cpp['writer_loc'][1:]==['torch.int64',[k[2]],[1],'cuda:0']
        assert cpp['row_bytes']==cpp['v_row_bytes']==512
        for name in ('k_cache','v_cache'):
            assert f[name][1:]==['torch.bfloat16',[1833689,1,256],[256,256,1],'cuda:0']
            assert cpp[name][1:]==['torch.bfloat16',[1833689,256],[256,1],'cuda:0']
platform_path=base/'terminal-platform-A.json'; platform=read_json(platform_path)
assert platform['job']==result['job'] and platform['uid']==terminal['uid'] and platform['creator']=='i-fengyicheng'
assert platform['status']==terminal['status'] and len(platform['replicas'])==1
replica=platform['replicas'][0]; owner=replica['owner_references'][0]; container=replica['containers'][0]
assert owner['uid']==platform['uid'] and owner['name']==platform['job'] and owner['kind']=='RJob' and owner['controller']
assert replica['phase']=='Failed' and container['state']['terminated']['exitCode']==1 and container['state']['terminated']['reason']=='Error' and container['restart_count']==0
assert platform['stop_annotations']=={'rjob.brainpp.cn/system-stop-reason':'Some critical tasks failed.'}
critical=[base/'admission-A-r1.terminal.json',platform_path,run/'result.json',run/'preload.json',run/'requests.jsonl',run/'cache.jsonl',run/'comparisons.jsonl',run/'runtime_metadata.json',run/'server_info.json',build_path]
output={'task_id':'profile-kv-coherence-native-A-20261111','pair':'A','job':result['job'],
 'primary_accepted_disposition':{'date':'2026-11-11','scope':'Actual bounded A retained controls/source/selected CPP/four-H800 worker receipt/failed-terminal consistency only','overall_kv_diagnostic_pass':False},
 'verdicts':{'retained_evidence_consistency':'PASS','all16_6804_baseline_reproduction':'PASS','cold_parity':'PASS','warm_correctness':'FAIL','auxiliary_capture_qualification':'FAIL','original_rust_old_gpu_callback':'UNVERIFIED','observer_cuda_stream':'UNVERIFIED','physical_indices_7955':'UNVERIFIED','kv_numeric_coherence':'UNVERIFIED','formal04_05':'HOLD'},
 'local_environment':{'python':sys.version.split()[0],'executable':sys.executable,'conda_default_env':os.environ.get('CONDA_DEFAULT_ENV'),'timeout_seconds':60,'address_space_limit_bytes':30*1024**3},
 'workload':{'requests':16,'unique_native_rids':16,'finite_vectors':16,'baseline_values':6804,'candidate_values':6804,'http200_flushes':10,'log_flush_confirmations':10,'retractions':0,'generated_tokens':0,'comparisons_unchanged':8,'recomputed_comparison_groups':40,'cold_exact':4,'warm_exact':1,'warm_different':3},
 'vector_errors':{'maximum_absolute_error':max(c['max_absolute_error'] for c in gate['comparisons']),'maximum_defined_relative_error':max(c['max_relative_error'] for c in gate['comparisons']),'defined_relative_value_count':gate['baseline_values']-sum(c['relative_error_undefined_count'] for c in gate['comparisons']),'zero_reference_relative_undefined':24,'identity_shape_nonfinite_errors':0,'relative_error_rule':'Undefined for every zero reference, including 0 versus 0; no tolerance'},
 'baseline':str(baseline),'baseline_job':old_result['job'],'join_fields':list(key_fields),'response_identities':identities,'warm_errors':warm_errors,
 'source':{'frozen_commit':commit,'native_scoring_source_sha256':source_ids,'archive_file_counts':{**source_counts,'kv_coherence_source_preflight':40},'archive_content_hash_checks':archive_checks,'coherence_changed_files':receipt['changed_files'],'runtime_inventory_overlap_matches':runtime_matches,'six_final_attention_sources_equal_baseline':True,'r3_source_commit':r3ref,'r3_helper_sha256':source['helper_sha256'],'r3_build_receipt_sha256':sha(build_path),'r3_build_bytes':15835,'rust_source_files_verified':rust_source_checks,'retained_elfs_verified':2,'r3_linked_receipts_verified':5,'frozen_r2_receipt_unchanged':True,'global_5501_621_sweep':False},
 'private_staging':{'package_root':str(private),'import_origin':package['import_origin'],'child_pythonpath':package['child_pythonpath'],'production_module':native_receipt['module'],'binary_target':native_receipt['binary_target'],'compiled_sha256':native_receipt['compiled_sha256'],'actual_gpu_callback_origin_and_sha':'UNVERIFIED; absent because collector unavailable','original_binary_source_commit':'UNVERIFIED'},
 'worker_runtime':{k:runtime[k] for k in ('python','executable','sglang','torch','gpu_devices','configured_image','model_path','model_manifest_identity','sglang_environment')},'teacher_argv':result['argv'],
 'capture':{'status':'FAILED_AUXILIARY_QUALIFICATION','error':expected_error,'reason':kv['reason'],'runtime_metadata_bytes':len(content(run/'runtime_metadata.json')),'metadata_http_status':200,'startup_and_post_settings':settings,'additional_cache_workload_geometry':geometry,'source_rca_reference':{'authority':'Primary supplied separate initializer/source RCA, 2026-11-11','sealed_raw_page_size':None,'resolved_page_size':1,'later_mutation':False,'independently_reinvestigated_here':False},'topology_banks_payload_present':False,'kv_summaries':0,'numeric_acceptance':None},
 'selected_cpp_witness':{'status':'PASS_SELECTED_IN_CALL_CPP_ONLY','process_id':m['process_id'],'rank':m['rank'],'dp_size':1,'tp_size':4,'pp_size':1,'startup_rows':len(startup),'post_loop_rows':len(rows),'unique_cpp_terminal_joins':2704,'ambiguous_or_absent_joins':0,'chunks_and_unique_scheduler_joins':169,'full_layer_ids':layers,'response_rids_covered':16,'cpp_actual_stream_values':sorted({f['native_actual_stream'] for values in streams.values() for _,f in values}),'join_fields':['rids','prefix_lens','extend_lens','k_cache_data_ptr','v_cache_data_ptr','writer_loc_data_ptr'],'terminal_own_scalar_observed':False,'kv_prefix_triton_exercised':False,'device_completion':'UNVERIFIED','rust_observer_new_stream':'UNVERIFIED'},
 'terminal':{'primary_receipt':str(platform_path),'observed_at':platform['observed_at'],'job_uid':platform['uid'],'job_phase':'Failed','job_finish':terminal['status']['finishTime'],'container_reason':'Error','container_exit_code':1,'restart_count':0,'container_finish':container['state']['terminated']['finishedAt'],'system_stop_annotations':platform['stop_annotations'],'stop_inferred_from_cleanup':False,'caller_cleanup_completed':True,'server_returncode_before_cleanup':result['server_returncode_before_cleanup'],'server_shutdown_returncode':result['server_shutdown_returncode']},
 'critical_input_sha256':{str(p):sha(p) for p in critical},
 'limits':['Auxiliary capture failure, not training/root-math failure or a repaired warm path','No actual Rust OLD GPU callback/module-origin/SO-hash/observer-stream receipt','No physical indices/7955 OLD/zero-cold OLD/KV values/statistics/numeric acceptance','Selected CPP in-call scalar is not device completion or observer stream proof','Responding DP1/TP0 only; no all-TP/race/coherence/56/two-repeat/performance/formal200 acceptance','Model manifests are not whole-weight checksums; configured image is not terminal imageID attestation','No original R2/CPU/WIT acceptance is reset; raw artifacts and formal hold preserved']}
for path,digest in snapshots.items(): assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
for path,digest in frozen_sources.items(): assert hashlib.sha256(fixed(commit,path)).hexdigest()==digest
assert len(snapshots) == 308 and len(frozen_sources) == 10
output['scoped_input_binding']={'initial_verification_live_files_checked_unchanged':318,'retained_files_checked_unchanged':len(snapshots),'immutable_git_source_files_checked_unchanged':len(frozen_sources),'workingtree_identity_acceptance_gate':False,'runtime_source_self_read':'Original frozen _runtime_source function bound to immutable Git helper bytes'}
output['scoped_input_files_checked_unchanged']=len(snapshots)+len(frozen_sources)
print(json.dumps(output,indent=2,allow_nan=False))
```

Expected: all consistency assertions PASS;16/6804 exact,40 comparisons reproduced,194 source-content hash checks,44 selected Rust source files,2 retained ELFs,2,704 unique CPP joins; capture FAIL/warm FAIL and physical/numeric UNVERIFIED remain explicit.

Initial full verification: exit0; the above counts match. The readback contains551 startup and30,795 post-loop typed rows from process340/TP0. There are2,704 unique CPP/terminal joins,169 unique scheduler/chunk joins,16 FULL layers and16 covered response RIDs, with0 missing/ambiguous joins. Every selected CPP scalar equals Torch's current scalar1391112320; no prefix-valid KV Triton path was exercised. All318 initially scoped live input files retained their original hashes during that command. This historical check is preserved, not asserted against later working-tree edits. No global archive rehash or raw writes occurred.

The initial full-verifier attempt failed locally with `FileNotFoundError` when `_runtime_source()` read a symbolic `commit:path` supplied as `__file__`. This was a verifier context issue, not a source/collector/native failure. The first correction used a live path after a byte-equality assertion; its successful initial verification remains historical evidence. The archival correction above instead retains symbolic Git `__file__` values and reuses the original frozen `_runtime_source` function with only its `Path(__file__).read_text()` source API bound to immutable helper bytes. There is no live-source identity acceptance gate or temporary source fixture. The same318 scoped inputs now comprise308 unchanged retained files plus10 immutable Git source files; all194 archive,44 Rust-input and two ELF gates are unchanged.

Initial artifact verification: **PASS**, exit0 in2.699 seconds. Parsed stdout exactly equaled the initial owned JSON; both owned files had clean trailing whitespace and final newlines. The same equality/whitespace command is rerun after the archival correction:

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import contextlib,io,json,time
from pathlib import Path
p=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_A_results.md')
artifact=p.parent/'evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-A.json'
code=p.read_text().split('```python\n',1)[1].split('\n```',1)[0]
stream=io.StringIO();start=time.perf_counter()
with contextlib.redirect_stdout(stream): exec(compile(code,str(p)+':verifier','exec'),{})
assert json.loads(stream.getvalue())==json.loads(artifact.read_text())
for f in (p,artifact):
 assert f.read_bytes().endswith(b'\n') and all(line==line.rstrip() for line in f.read_text().splitlines())
print('ARTIFACT_MATCH_AND_WHITESPACE_PASS',round(time.perf_counter()-start,3),'seconds; all16/6804 exact; 194 archive hashes; 44 Rust sources; 2704 explicit CPP joins; 318 scoped inputs unchanged; capture FAIL/warm FAIL/physical UNVERIFIED preserved')
import hashlib,subprocess
helper='tests/manual/agent_opd/sglang_kv_coherence.py'
frozen=subprocess.check_output(['git','show',f'b9e1ebb6:{helper}'])
print('LIVE_HELPER_DIFFERS_FROM_FROZEN_OBSERVATION',Path(helper).read_bytes()!=frozen)
PY
```

Initial stdout: `ARTIFACT_MATCH_AND_WHITESPACE_PASS 2.699 seconds; all16/6804 exact; 194 archive hashes; 44 Rust sources; 2704 explicit CPP joins; 318 scoped inputs unchanged; capture FAIL/warm FAIL/physical UNVERIFIED preserved`. Primary has accepted only the bounded evidence scope stated above. Files remain unstaged/uncommitted; archival-correction verification is recorded below.

Archival-correction verification: **PASS**. The original stdout CLI was run once and exited0. The equality/whitespace command above then exited0 in3.003 seconds, printing `ARTIFACT_MATCH_AND_WHITESPACE_PASS 3.003 seconds; all16/6804 exact; 194 archive hashes; 44 Rust sources; 2704 explicit CPP joins; 318 scoped inputs unchanged; capture FAIL/warm FAIL/physical UNVERIFIED preserved` and `LIVE_HELPER_DIFFERS_FROM_FROZEN_OBSERVATION True`. The latter is a time-bounded observation outside the returned JSON, not an acceptance gate. Thus the actual later-fixed live helper differs while the immutable A source/archive recomputation and exact JSON equality pass. The initial318-file check, first failures, all numeric results, R3/archive hashes and original raw artifacts remain preserved. Current318-input accounting is308 retained disk files plus10 immutable Git source files. No source fixture, broader test, source fix, shared-document edit, platform/auth/GPU/native action, staging or commit was performed.

## 1. 规划完成情况

**汇总：** PASS 3｜FAILED 0｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 六个guard settings及RCA引用修正 | PASS |实际六字段与额外geometry分列；仅引用primary已知RCA。 |
| 冻结helper source读及原CLI复算 | PASS |live helper已不同，Git冻结函数/bytes与194 archive gates仍通过。 |
| JSON/whitespace与限定验收记录 | PASS |exit0/3.003s；318输入与所有原FAIL/UNVERIFIED/HOLD保留。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** primary两项archival follow-up至复算完成｜**当前前沿：** 返回相同两文件；shared源码修正与B验收仍由各自owner负责。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR |仅用户要求的冻结self-source绑定；原CLI与equality通过即停止。 |
| D2 细节反复重试 | CLEAR |一次修正；原CLI及指定equality检查均首次通过。 |
| D3 支线问题修补 | CLEAR |只改相同两文件；未重复initializer RCA或修shared源码。 |
| D4 可并行任务停滞 | CLEAR |两个修正共享两文件；其他owner独立推进，禁止新delegation。 |
| D5 超范围镀金 | CLEAR |未改原数学、raw、archive/R3 gates或增加新测试。 |
| D6 分析空转 | CLEAR |只检查冻结函数self-read与实际六字段；两项已交付。 |
| D7 路线违背 | CLEAR |无平台/auth/GPU/native/stage/commit；formal HOLD保留。 |

**文档检查：** 本次明确的两项follow-up没有S1–S6未解决缺陷：步骤无错误依赖、遗漏owner、矛盾/无界criteria或重叠scope；两处过时表述已修正。Shared requirements/plan/ticket状态不在本次调查或编辑scope；原验收条件未改。
**归因：** 无执行偏离。

## 3. 纠正建议

**分支：** A：本次follow-up明确，无需改动spec/tickets。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Primary归档同两结果文件 → 完成标志：实际六guard字段、不可变helper复算、限定controls验收和原FAIL/UNVERIFIED/HOLD分别保留。
2. 并行：B核验 ‖ initializer/source修正继续由原owner推进；本agent无新增任务。

## 4. 最值得关注的 3 点

1. 实际六guard字段已完整分列；sealed rawNone/resolved1且无后续mutation仅引用primary已知RCA。
2. live helper不同仍复算PASS；原318-file检查保留，当前318输入明确分为308 retained文件和10 frozenGit source。
3. Primary仅接受bounded controls/source/CPP证据；aux capture FAIL、warm1/4 FAIL、OLD/new-stream/7955/KV UNVERIFIED与formal HOLD未变。
