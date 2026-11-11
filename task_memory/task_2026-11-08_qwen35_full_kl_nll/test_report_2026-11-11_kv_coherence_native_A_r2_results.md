## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Verify retained native A r2 controls against the accepted metadata baseline; separate source/CPP evidence and incomplete collector observations from KV/formal acceptance. |

# Native KV coherence A r2 retained controls

TaskID: `profile-kv-coherence-native-A-r2-20261111`.

## Scope and acceptance boundary

Read-only verification of `exp-1111-171524-888127`, retained under `evidence/teacher-scoring-kv-coherence-probe-20261111/native/A/admission-A-r2`. The only new files are this report and `evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-A-r2.json`. No source/config/master-document/old-report/raw edits, native execution, platform/auth/GPU access, delegation, source collection, broad tests, staging or commit. Collector RCA/fix belongs to its independent owner.

The accepted reference is `evidence/teacher-scoring-runtime-metadata-probe-20261111/native/A/admission-A-r1`, job `exp-1111-073826-369716`. All six baseline native scoring-source identities are checked against immutable `4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff` bytes. Raw run files are retained filesystem evidence, not Git objects: an initial attempt to read baseline `result.json` through `git show 4f1139b0:...` returned128 (`exists on disk, but not in '4f1139b0'`). This verifier does not invent Git provenance for raw results; it hashes their actual retained bytes.

The new run is checked against immutable `6119bee19eae6091ac757bbccbf9b168b5f508be`. Helper SHA256 is `e9e4798c2260db26f1cc532641bb3f02eec3897c8d744953648a53d1d1d0fc43` /38,793 bytes. Live helper equality is not an acceptance gate. The frozen helper's original `_runtime_source` function reads immutable Git bytes through a scoped self-source API binding, never a later live `__file__`.

**Control PASS is not overall diagnostic PASS.** The result reports `failed` after16 scores/10 flushes, with `native_measurements_completed=true`, `cleanup_completed=true`, numerical acceptance null and performance acceptance false. Independent readback remains `unverified` with global `note_cpp`/`fresh` errors and no interpreted summaries. Warm correctness/formal holds and all original R2/CPU/WIT/r1 evidence remain unchanged. Caller cleanup and server shutdown `-9` do not establish a platform stop or container terminal state. The separately filtered `terminal-platform-A-r2.json` is not a prerequisite for these controls and is not used by this sealed verifier; terminal/platform conclusions remain UNVERIFIED pending primary's independent receipt.

## Required checks and observations

| Item | Passing condition or boundary |
| --- | --- |
| Logical vectors |16 unique logical cases/native RIDs;6,804 finite values; exact token/value identity to the accepted baseline, no tolerance |
| Errors | maxabs=0; maximum defined relative error=0;6,780 defined relative positions,24 zero-reference positions undefined;0 identity/shape/nonfinite errors |
| Business controls |16 scored HTTP200,10 HTTP200 flushes and10 log confirmations;0 retractions/generated tokens;8 unchanged comparisons and40 recomputed groups |
| Original comparisons | Cold4/4 exact; warm1/4 exact,3/4 different; original warm errors preserved, not repaired |
| Source/archive |8 new and6 baseline scoring-source identities; frozen config/first4 manifest;194 before/after archive hashes;40-file coherence transformation from frozen6119 |
| R3/library linkage | Config and nested native receipt select SHA `91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7`;44 retained Rust input checks,2 ELF checks and5 linked receipts |
| Private package | Retained whole-package staging/import/PYTHONPATH and7 overlapping source hashes agree; staging is not a same-GPU-callback module-origin/SO-hash attestation |
| Selected CPP | Existing exact process-local join schema only;2,704 unique in-call/terminal joins,169 unique chunk/scheduler joins,16 FULL layers and16 response RIDs; no adjacency |
| Capture | Failed auxiliary qualification; startup/post snapshots retain topology/budget and partial banks/fragments only; complete FRESH, observer-native stream, physical7,955 and KV numeric evidence UNVERIFIED |

The actual startup snapshot is `metadata_only`; post-loop snapshot is `unverified`, both responding process340/TP0 only. Both expose topology page_size1,16 layer mappings, CUDA BF16 K/V buffer metadata and budget payload536,870,912 + index2,490,368 = allocated539,361,280 bytes (514.375MiB). These are startup/preallocation observations, not a sealed raw/resolved initializer receipt or independently measured allocation/callback origin. Neither snapshot provides a separate initializer/preallocation stage receipt; the original r1 preallocation failure is not rewritten.

Both snapshots retain224 global errors:112 `note_cpp` and112 `fresh`, each RID null, P90112/E98304 and exact message `object of type 'NoneType' has no len()`. Post-loop reports16 completed RIDs and two candidate banks. Each bank lists16 `fresh_layers` and no per-bank errors, but this does **not** override global errors or prove complete fresh capture. One bank has no OLD fragments; the other has two recorded fragments with prefix lengths6519/1436, intervals[90112,96631)/[96631,98067), original_FULL tensor shapes[6519]/[1673], thread340 and Torch stream scalar1320513136. These are retained callback metadata observations only, not original physical FULL slot values, independent7,955 equality, callback/SO provenance, observer-native S evidence, device completion or numeric acceptance. No tensors are imported or interpreted.

CPP joins reuse the accepted r1/WIT mechanism: `(rids,prefix_lens,extend_lens,k_cache_data_ptr,v_cache_data_ptr,writer_loc_data_ptr)` within the single responding process/rank, then unique `(RID,prefix,extend)` scheduler linkage and `seq_end=prefix+extend`. The matched CPP in-call scalar is separate from the terminal row, whose own scalar-observed flag is false. Scalar identity to Torch's current stream is not proof of the new Rust observer stream or completed device writes.

Exact RID lookup identifies the retained banks as `cold-r0-s2-full_input` and `warm_stream-r0-s2-full_input` (sample1695), not an adjacency-based join. The selected CPP-native scalar is1320220896; the OLD-fragment `torch_current_raw_stream` field is1320513136. These separately named receipts are recorded without equating their contexts or drawing a causal/stream-coherence conclusion.

## Exact local verification

Workdir `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Interpreter `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, `CONDA_DEFAULT_ENV` unset. Standard library plus existing pure helper definitions compiled from frozen Git bytes;60-second timeout and30GiB address-space limit. No dependency changes, package/native imports, capture/build/preparation methods, GPU operations or new verifier framework. Existing source-rewrite functions only compute bytes in memory. The scoped verifier below reads selected retained evidence and prints JSON; it writes nothing and does not hash the global5,501/621 inventory.

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'from pathlib import Path; p=Path("task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_A_r2_results.md"); exec(compile(p.read_text().split("```python\n",1)[1].split("\n```",1)[0],str(p)+":verifier","exec"))'
```

```python
import difflib, hashlib, json, math, os, resource, subprocess, sys, types
from collections import Counter, defaultdict
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
task = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
base = task/'evidence/teacher-scoring-kv-coherence-probe-20261111'
run = base/'native/A/admission-A-r2'
baseline = task/'evidence/teacher-scoring-runtime-metadata-probe-20261111/native/A/admission-A-r1'
commit = '6119bee19eae6091ac757bbccbf9b168b5f508be'
baseline_commit = '4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff'
snapshots, git_inputs = {}, {}
def content(path):
    raw = path.read_bytes(); digest = hashlib.sha256(raw).hexdigest()
    if path in snapshots: assert snapshots[path] == digest
    snapshots[path] = digest
    return raw
read_json = lambda p: json.loads(content(p))
read_lines = lambda p: [json.loads(x) for x in content(p).decode().splitlines()]
sha = lambda p: hashlib.sha256(content(p)).hexdigest()
def fixed(ref, path):
    blob = subprocess.check_output(['git','show',f'{ref}:{path}'])
    key = (ref,str(path)); digest = hashlib.sha256(blob).hexdigest()
    if key in git_inputs: assert git_inputs[key] == digest
    git_inputs[key] = digest
    return blob
result, preload, old_result = (read_json(p) for p in (run/'result.json',run/'preload.json',baseline/'result.json'))
assert result['job'] == 'exp-1111-171524-888127' and old_result['job'] == 'exp-1111-073826-369716'
assert result['status'] == 'failed' and result['native_measurements_completed'] and result['cleanup_completed']
assert result['numerical_acceptance'] is None and result['performance_accepted'] is False
for record,ref,count in ((result,commit,8),(old_result,baseline_commit,6)):
    assert len(record['native_scoring_sources']) == count
    for path,identity in record['native_scoring_sources'].items():
        blob = fixed(ref,path)
        assert len(blob) == identity['bytes'] and hashlib.sha256(blob).hexdigest() == identity['sha256']
assert result['native_scoring_sources'] == preload['native_scoring_sources']
helper_path = 'tests/manual/agent_opd/sglang_kv_coherence.py'
assert result['native_scoring_sources'][helper_path]['sha256'] == 'e9e4798c2260db26f1cc532641bb3f02eec3897c8d744953648a53d1d1d0fc43'
for name in ('tests','tests.manual','tests.manual.agent_opd'):
    module = types.ModuleType(name); module.__path__ = []; sys.modules[name] = module
for name in ('probe_teacher_scoring','sglang_mamba_snapshots','sglang_mamba_runtime_metadata','sglang_kv_streams','sglang_kv_coherence','sglang_rust_kv_observer'):
    path = f'tests/manual/agent_opd/{name}.py'; module = types.ModuleType('tests.manual.agent_opd.'+name)
    module.__file__ = f'{commit}:{path}'; sys.modules[module.__name__] = module
    setattr(sys.modules['tests.manual.agent_opd'],name,module)
    exec(compile(fixed(commit,path),module.__file__,'exec'),module.__dict__)
probe, coherence, witness, native = (sys.modules['tests.manual.agent_opd.'+n] for n in ('probe_teacher_scoring','sglang_kv_coherence','sglang_kv_streams','sglang_rust_kv_observer'))
frozen_helper = fixed(commit,helper_path).decode()
def frozen_helper_path(path):
    assert path == coherence.__file__
    return types.SimpleNamespace(read_text=lambda:frozen_helper)
coherence._runtime_source = types.FunctionType(coherence._runtime_source.__code__,{**coherence.__dict__,'Path':frozen_helper_path},'_runtime_source')
gate = coherence.compare_completion_vectors(run,baseline)
assert gate['all16_6804_exact'] and gate['vectors'] == 16 and gate['baseline_values'] == gate['candidate_values'] == 6804
undefined = sum(c['relative_error_undefined_count'] for c in gate['comparisons']); assert undefined == 24
for field in ('fixture','config'):
    identity = result[field]; assert identity == preload[field]
    blob = fixed(commit,str(Path(identity['path']).relative_to(Path.cwd())))
    assert len(blob) == identity['bytes'] and hashlib.sha256(blob).hexdigest() == identity['sha256']
config = json.loads(blob)
assert config['repeats'] == 1 and config['kv_coherence_build_receipt'].endswith('native-rust-kv-observer-qualification-20261111-r3/observer-build.json')
fixture_id = result['sample_manifest']['source_fixture']; fixture = Path(fixture_id['path'])
assert sha(fixture) == fixture_id['sha256'] == 'c45424e8106c2beb7500acacb68aa0939da0088c926af8012dd9fbd780f0ffc9'
samples = read_json(fixture)['samples'][:4]
requests, old_requests, cache, comparisons = (read_lines(p) for p in (run/'requests.jsonl',baseline/'requests.jsonl',run/'cache.jsonl',run/'comparisons.jsonl'))
fields = ('pair','phase','mode','source_uid','sample_index','repetition'); key = lambda r:tuple(r[k] for k in fields)
assert len(requests) == len({r['request_id'] for r in requests}) == len({r['native_request_id'] for r in requests}) == 16
assert [key(r) for r in requests] == [key(r) for r in old_requests]
assert len(list((run/'completion_scores').glob('*.json'))) == 16
vectors, identities = {}, []
for r,old in zip(requests,old_requests):
    s = samples[r['sample_position']]; n,length = len(s['tokens']),s['response_length']; start = 0 if r['mode']=='full_input' else n-length-1
    assert (r['source_uid'],r['sample_index']) == (s['source_uid'],s['sample_index'])
    assert r['status']=='scored' and r['http_status']==200 and r['cache_salt'] is None and r['repetition']==0
    assert (r['input_count'],r['prompt_count'],r['response_count'],r['logprob_start_len']) == (n,n-length,length,start)
    assert r['input_token_logprobs_count']==r['expected_input_token_logprobs_count']==n-start
    assert r['first_input_token_logprob'] is None and r['first_input_token_id']==r['first_requested_input_token_id']==s['tokens'][start]
    assert r['returned_completion_count']==length and r['token_ids_match'] and r['finite_log_probs']
    assert r['completion_token_id_mismatches']==r['nonfinite_log_prob_positions']==[]
    assert r['meta_info']['completion_tokens']==r['meta_info']['output_token_logprobs_length']==r['meta_info']['num_retractions']==0
    v = read_json(run/'completion_scores'/f"{r['request_id']}.json"); previous = read_json(baseline/'completion_scores'/f"{old['request_id']}.json")
    assert key(v)==key(r) and v['request_id']==r['request_id'] and v['native_request_id']==r['native_request_id']==r['meta_info']['id']
    assert v['token_ids']==previous['token_ids']==s['tokens'][-length:] and len(v['token_ids'])==len(v['log_probs'])==length
    assert all(math.isfinite(x) for x in v['log_probs']) and v['log_probs']==previous['log_probs']
    vectors[r['request_id']]=v
    identities.append({'request_id':r['request_id'],'native_request_id':r['native_request_id'],'sample_index':r['sample_index'],'values':length})
assert len(cache)==10 and all(c['status']=='flushed' and c['http_status']==200 for c in cache)
assert content(run/'server.log').decode().count('Cache flushed successfully!')==10
assert len(comparisons)==8 and content(run/'comparisons.jsonl')==content(baseline/'comparisons.jsonl')
recomputed,warm_errors=0,[]; error=lambda c:[c['max_absolute_error'],c['max_relative_error'],c['relative_error_undefined_count']]
for row in comparisons:
    full,response=vectors[row['full_request_id']],vectors[row['response_request_id']]
    assert probe._comparison(full,response)==row['full_vs_response_only']; recomputed+=1
    if row['cold_reference']:
        ref=row['cold_reference']; cf,cr=vectors[ref['full_request_id']],vectors[ref['response_request_id']]
        for name,left,right in (('cold_full_vs_warm_full',cf,full),('cold_full_vs_warm_response_only',cf,response),('cold_response_only_vs_warm_full',cr,full),('cold_response_only_vs_warm_response_only',cr,response)):
            assert probe._comparison(left,right)==ref[name]; recomputed+=1
        warm_errors.append({'sample_index':row['sample_index'],'warm_full_vs_response':error(row['full_vs_response_only']),'cold_full_vs_warm_full':error(ref['cold_full_vs_warm_full']),'cold_response_vs_warm_response':error(ref['cold_response_only_vs_warm_response_only'])})
    s=samples[row['sample_position']]; expected={'token_ids':s['tokens'][-s['response_length']:],'log_probs':s['expected_teacher_log_probs']}
    for name,v in (('full_input',full),('response_only',response)):
        assert probe._comparison(expected,v)==row['historical_expected'][name]; recomputed+=1
assert recomputed==40 and sum(c['full_vs_response_only']['values_exact'] for c in comparisons if c['phase']=='cold')==4
assert sum(c['full_vs_response_only']['values_exact'] for c in comparisons if c['phase']=='warm_stream')==1
counts,archive_checks={},0
for stage in ('source_preflight','runtime_metadata_source_preflight','kv_store_stream_source_preflight'):
    receipt=result[stage]; assert receipt==preload[stage]==read_lines(run/stage/'preflight.jsonl')[-1]
    assert read_json(run/stage/'source_manifest.json')['files']==receipt['files']; counts[stage]=len(receipt['files'])
    for relative,identity in receipt['files'].items():
        for side in ('before','after'):
            assert sha(run/stage/side/relative)==identity[f'{side}_sha256']==receipt[f'observed_{side}_sha256'][relative]; archive_checks+=1
assert list(counts.values())==[6,16,35]
wit=result['kv_store_stream_source_preflight']
for relative,identity in witness.source_manifest()['files'].items():
    before=content(run/'kv_store_stream_source_preflight/before'/relative); after=content(run/'kv_store_stream_source_preflight/after'/relative)
    witness._qualified_baseline(relative,before,identity); assert witness._rewrite(relative,before)==after
for p in result['source_preflight']['files']:
    assert result['runtime_metadata_source_preflight']['observed_before_sha256'][p]==result['source_preflight']['observed_after_sha256'][p]
for p,d in result['runtime_metadata_source_preflight']['observed_after_sha256'].items(): assert wit['observed_before_sha256'][p]==d
receipt=result['kv_coherence_source_preflight']; package=result['kv_coherence_package']; private=Path(package['package_root'])
assert receipt==preload['kv_coherence_source_preflight']==read_lines(run/'kv_coherence_source_preflight/preflight.jsonl')[-1]
assert read_json(run/'kv_coherence_source_preflight/source_manifest.json')==receipt['manifest']==coherence.source_manifest()
assert package==preload['kv_coherence_package'] and receipt['package_root']==str(private)
assert private!=Path(package['source_package_root']) and package['import_origin']==str(private/'__init__.py')
assert package['child_pythonpath'].split(':')[0]==str(private.parent)
assert all(Path(v['path']).is_relative_to(private) for v in result['runtime']['sglang_sources'].values())
before_map,after_map={},{}
for p,d in receipt['observed_after_sha256'].items():
    before=content(run/'kv_coherence_source_preflight/before'/p); after=content(run/'kv_coherence_source_preflight/after'/p)
    assert hashlib.sha256(after).hexdigest()==d and after==(coherence._runtime_source() if p=='srt/kv_coherence.py' else coherence._rewrite(p,before))
    if p in wit['files']: assert hashlib.sha256(before).hexdigest()==wit['observed_after_sha256'][p]
    elif p in receipt['manifest']['additional_native_sha256']: assert hashlib.sha256(before).hexdigest()==receipt['manifest']['additional_native_sha256'][p]
    else: assert p=='srt/kv_coherence.py' and before==b''
    before_map[p],after_map[p]=before,after; archive_checks+=2
assert len(after_map)==40 and archive_checks==194
diff=''.join(''.join(difflib.unified_diff(before_map[p].decode().splitlines(True),after_map[p].decode().splitlines(True),fromfile=f'a/{p}',tofile=f'b/{p}')) for p in before_map if before_map[p]!=after_map[p])
assert content(run/'kv_coherence_source_preflight/coherence.diff').decode()==diff
overlap=0
for p,i in result['runtime']['sglang_sources'].items():
    if p in after_map: assert i['sha256']==receipt['observed_after_sha256'][p]; overlap+=1
n=receipt['native_observer']; build_path=Path(n['build_receipt'])
assert n==read_json(run/'kv_coherence_source_preflight/native_observer/preflight.json')
assert build_path==Path.cwd()/config['kv_coherence_build_receipt']
assert sha(build_path)==n['build_receipt_sha256']=='91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7'
build=read_json(build_path); r3=read_json(build_path.parent/'native-verification.json')
assert build['status']==build['qualification']['status']=='PASS' and build['module']==n['module']==native.MODULE
assert n['package_root']==str(private) and Path(n['binary_target']).is_relative_to(private) and n['compiled_sha256']==build['observer']['sha256']
assert n['composition']=={p:{'bytes':len(content(run/'kv_store_stream_source_preflight/after'/p)),'sha256':d} for p,d in wit['observed_after_sha256'].items()}
assert n['adapter_before_sha256']==build['source_manifest']['adapter_before_sha256'] and n['adapter_after_sha256']==build['source_manifest']['adapter_after_sha256']
sha(run/'kv_coherence_source_preflight/native_observer/adapter.patch')
rust_checks=0
for variant,side in (('baseline','before'),('observer','after')):
    raw=content(Path(build[variant]['path'])); assert raw.startswith(b'\x7fELF') and hashlib.sha256(raw).hexdigest()==build[variant]['sha256']
    for p,i in build['source_manifest'][side].items():
        raw=content(Path(build[variant]['workspace'])/p); assert len(raw)==i['bytes'] and hashlib.sha256(raw).hexdigest()==i['sha256']
        if side=='before': assert i['sha256']==native._RUST_PINS[p]
        rust_checks+=1
assert rust_checks==44
for p in native._RUST_PINS: assert native._rust_candidate(p,content(Path(build['baseline']['workspace'])/p))==content(Path(build['observer']['workspace'])/p)
for i in (*build['input_receipts'].values(),build['qualification_receipt']): assert len(content(Path(i['path'])))==i['bytes'] and sha(Path(i['path']))==i['sha256']
assert read_json(Path(build['qualification_receipt']['path']))==build['qualification']
r3source=r3['source_identity']; assert r3source['native_code_ref']=='17cb6fc66fa8b5e866c0c83d5f5c93cf971ac898' and r3source['final_build_sha256']==sha(build_path)
for name,d in (('sglang_rust_kv_observer.py',r3source['helper_sha256']),('probe_rust_kv_observer.py',r3source['probe_sha256'])):
    p='tests/manual/agent_opd/'+name; blob=fixed(r3source['native_code_ref'],p)
    assert hashlib.sha256(blob).hexdigest()==d and blob==fixed(commit,p)
original_r2=task/'evidence/rust-kv-observer-qualification-receipts-20261111/observer-build-r2.json'
assert sha(original_r2)=='4c967246e2cb3ab54e454b87f1a22231c73a7829037dbd98f19ad19bfb2e017b'
assert content(original_r2)==content(task/'evidence/native-rust-kv-observer-build-20261111/observer-build.json')
runtime=result['runtime']; assert runtime==preload['runtime'] and runtime['model_manifest_identity']==old_result['runtime']['model_manifest_identity']
assert (runtime['python'],runtime['executable'],runtime['sglang'],runtime['torch'])==('3.12.16','/opt/sglang/bin/python3','0.5.24.dev80+g056f871','2.14.1+cu130')
assert runtime['gpu_devices']==['NVIDIA H800, 81559 MiB, 570.124.06']*4
without_address=lambda a:[v for i,v in enumerate(a) if i==0 or a[i-1]!='--dist-init-addr']
assert without_address(result['argv'])==without_address(old_result['argv'])
initial=read_json(run/'server_info.json')['get_server_info']; metadata=read_json(run/'runtime_metadata.json'); post=metadata['server_info']
assert len(initial['internal_states'])==len(post['internal_states'])==1 and (post['dp_size'],post['tp_size'],post['pp_size'])==(1,4,1)
settings={'disable_cuda_graph':True,'page_size':1,'enable_memory_saver':False,'enable_unified_memory':False,'enable_hierarchical_cache':False,'enable_unified_cache_external_linker':False}
assert {k:initial[k] for k in settings}=={k:post[k] for k in settings}==settings
kv,ikv=(i['internal_states'][0]['kv_coherence'] for i in (post,initial))
m,im=(i['internal_states'][0]['mamba_runtime_metadata'] for i in (post,initial))
assert kv['process_id']==ikv['process_id']==m['process_id']==im['process_id']==340 and m['rank']==im['rank']=={'dp_rank':None,'tp_rank':0,'pp_rank':0,'attn_dp_rank':0,'attn_tp_rank':0}
assert ikv['status']=='metadata_only' and kv['status']=='unverified' and kv['numeric_acceptance'] is None
assert kv['reason']=='Candidate cardinality/capture errors/unconsumed CPP witness'
assert metadata['status']==result['runtime_metadata']['status']=='failed' and metadata['http']['http_status']==200
assert result['kv_coherence']['summaries']==[] and result['kv_coherence']['status']=='failed'
assert kv['errors']==ikv['errors'] and len(kv['errors'])==224 and Counter(e['stage'] for e in kv['errors'])=={'note_cpp':112,'fresh':112}
assert all(e=={'rid':None,'P':90112,'E':98304,'stage':e['stage'],'message':"object of type 'NoneType' has no len()"} for e in kv['errors'])
top=kv['topology']; layers=list(range(3,64,4)); assert top==ikv['topology'] and top['mapping']==[[l,i] for i,l in enumerate(layers)]
assert top['page_size']==1 and top['capacity']==1833688 and len(top['buffers'])==16
assert top['budget']=={'payload_bytes':536870912,'index_bytes':2490368,'allocated_bytes':539361280}
assert len(kv['completed_rids'])==16 and set(kv['completed_rids'])=={r['native_request_id'] for r in requests}
assert len(kv['banks'])==len(ikv['banks'])==2
streams,terminals,chunks,boundaries=(defaultdict(list) for _ in range(4))
join=lambda f:(tuple(f['rids']),tuple(f['prefix_lens']),tuple(f['extend_lens']),f['k_cache_data_ptr'],f['v_cache_data_ptr'],f['writer_loc_data_ptr'])
for seq,event,fields_row in m['rows']:
    f=dict(fields_row); assert len(f)==len(fields_row)
    if event=='kv_store_stream':
        assert f['store_kind']=='cpp_store_cache' and f['native_stream_scalar_observed'] and f['launch_enqueued']
        assert type(f['native_actual_stream']) is int and f['native_actual_stream']>=0 and f['native_actual_stream']==f['torch_current_raw_stream']
        streams[join(f)].append(f)
    elif event=='kv_store_terminal':
        assert f['store_kind']=='mha_set_kv_buffer_impl' and f['native_stream_scalar_observed'] is False and f['native_actual_stream'] is None
        assert len(f['rids'])==len(f['prefix_lens'])==len(f['extend_lens'])==1
        terminals[join(f)].append(f); chunks[(f['rids'][0],f['prefix_lens'][0],f['extend_lens'][0])].append(f)
    elif event=='scheduler_track_boundary': boundaries[(f['rid'],f['prefix_len'],f['extend_len'])].append(f)
assert len(streams)==len(terminals)==2704 and set(streams)==set(terminals) and all(len(v)==1 for v in (*streams.values(),*terminals.values()))
assert len(chunks)==len(boundaries)==169 and set(chunks)==set(boundaries) and {k[0] for k in chunks}==set(kv['completed_rids'])
for k,chunk in chunks.items():
    assert len(chunk)==16 and sorted(f['layer_id'] for f in chunk)==layers and len(boundaries[k])==1 and boundaries[k][0]['seq_end']==k[1]+k[2]
    for f in chunk:
        cpp=streams[join(f)][0]; assert f['pool_class']==['sglang.srt.mem_cache.memory_pool','MHATokenToKVPool']
        assert f['pool_layer_id']==f['buffer_layer_idx']==(f['layer_id']-3)//4
        assert f['writer_loc'][1:]==cpp['writer_loc'][1:]==['torch.int64',[k[2]],[1],'cuda:0'] and cpp['row_bytes']==cpp['v_row_bytes']==512
        for name in ('k_cache','v_cache'):
            assert f[name][1:]==['torch.bfloat16',[1833689,1,256],[256,256,1],'cuda:0'] and cpp[name][1:]==['torch.bfloat16',[1833689,256],[256,1],'cuda:0']
bank_observations=[]; by_rid={r['native_request_id']:r['request_id'] for r in requests}
for b in kv['banks']:
    assert b['rid'] in by_rid and b['fresh_layers']==list(range(16)) and b['errors']==[]
    assert b['insert']['rid']==b['rebind']['rid']==b['rid']
    bank_observations.append({'request_id':by_rid[b['rid']],'rid':b['rid'],'P':b['insert']['P'],'E':b['insert']['E'],'Q':b['rebind']['Q'],'fresh_layer_labels':b['fresh_layers'],'per_bank_errors':b['errors'],'fragments':[{'rid':f['rid'],'node_id':f['node_id'],'cursor':f['cursor'],'prefix_len':f['prefix_len'],'lo':f['lo'],'hi':f['hi'],'original_FULL_shape':f['original_FULL']['shape'],'original_FULL_dtype':f['original_FULL']['dtype'],'device':f['original_FULL']['device'],'thread_id':f['thread_id'],'torch_current_raw_stream':f['torch_current_raw_stream']} for f in b['fragments']]})
assert [len(b['fragments']) for b in bank_observations]==[0,2]
old_proofs={str(p):sha(p) for p in (task/'test_report_2026-11-11_kv_coherence_native_A_results.md',base/'native-verification-A.json')}
critical=(run/'result.json',run/'preload.json',run/'requests.jsonl',run/'cache.jsonl',run/'comparisons.jsonl',run/'server_info.json',run/'runtime_metadata.json',baseline/'result.json',baseline/'requests.jsonl',baseline/'comparisons.jsonl',build_path)
output={'task_id':'profile-kv-coherence-native-A-r2-20261111','pair':'A','job':result['job'],
 'verdicts':{'retained_controls':'PASS','all16_6804_baseline_reproduction':'PASS','frozen_source_archive_r3_linkage':'PASS','selected_cpp_in_call_joins':'PASS','warm_correctness':'FAIL','auxiliary_capture_qualification':'FAIL','complete_fresh_capture':'UNVERIFIED','rust_old_physical_7955':'UNVERIFIED','observer_native_stream_and_callback_origin':'UNVERIFIED','kv_numeric_coherence':'UNVERIFIED','terminal_platform':'UNVERIFIED','formal04_05':'HOLD'},
 'local_environment':{'python':sys.version.split()[0],'executable':sys.executable,'conda_default_env':os.environ.get('CONDA_DEFAULT_ENV'),'timeout_seconds':60,'address_space_limit_bytes':30*1024**3},
 'baseline':{'path':str(baseline),'job':old_result['job'],'source_commit':baseline_commit,'native_source_identities_verified':6,'raw_results_git_objects':False},
 'workload':{'requests':16,'unique_native_rids':16,'finite_vectors':16,'values':6804,'http200_flushes':10,'log_flushes':10,'retractions':0,'generated_tokens':0,'unchanged_comparisons':8,'recomputed_groups':40,'cold_exact':4,'warm_exact':1,'warm_different':3},
 'vector_errors':{'max_absolute_error':max(c['max_absolute_error'] for c in gate['comparisons']),'max_defined_relative_error':max(c['max_relative_error'] for c in gate['comparisons']),'defined_relative_count':6804-undefined,'zero_reference_relative_undefined':undefined,'identity_shape_nonfinite_errors':0,'tolerance':None},
 'response_identities':identities,'warm_errors':warm_errors,
 'source':{'frozen_commit':commit,'helper_sha256':result['native_scoring_sources'][helper_path]['sha256'],'native_scoring_source_sha256':{p:i['sha256'] for p,i in result['native_scoring_sources'].items()},'config_sha256':result['config']['sha256'],'archive_file_counts':{**counts,'kv_coherence_source_preflight':40},'archive_hash_checks':archive_checks,'runtime_overlap_hash_matches':overlap,'r3_build_sha256':sha(build_path),'r3_helper_sha256':r3source['helper_sha256'],'r3_source_commit':r3source['native_code_ref'],'rust_source_checks':rust_checks,'elf_checks':2,'linked_receipts':5,'original_rust_r2_receipt_preserved':True,'live_source_identity_gate':False,'runtime_source_read':'Original frozen function; immutable Git self-source API binding','global_5501_621_rehash':False},
 'private_staging':{'package_root':str(private),'import_origin':package['import_origin'],'child_pythonpath':package['child_pythonpath'],'production_module':n['module'],'binary_target':n['binary_target'],'compiled_sha256':n['compiled_sha256'],'serving_native_origin_sha':package['serving_native_origin_sha'],'actual_gpu_callback_origin_and_sha':'UNVERIFIED; staging/metadata are not same-callback attestation','original_binary_source_commit':'UNVERIFIED'},
 'worker_runtime':{k:runtime[k] for k in ('python','executable','sglang','torch','gpu_devices','configured_image','model_path','model_manifest_identity','sglang_environment')},'teacher_argv':result['argv'],
 'selected_cpp':{'status':'PASS_SELECTED_IN_CALL_ONLY','process_id':m['process_id'],'rank':m['rank'],'startup_rows':len(im['rows']),'post_rows':len(m['rows']),'unique_cpp_terminal_joins':2704,'unique_chunk_scheduler_joins':169,'missing_or_ambiguous_joins':0,'full_layers':layers,'response_rids':16,'cpp_native_scalar_values':sorted({f['native_actual_stream'] for v in streams.values() for f in v}),'join_fields':['rids','prefix_lens','extend_lens','k_cache_data_ptr','v_cache_data_ptr','writer_loc_data_ptr'],'terminal_own_scalar_observed':False,'device_completion':'UNVERIFIED'},
 'capture_observations':{'status':'FAILED_AUXILIARY_QUALIFICATION','startup_status':ikv['status'],'post_status':kv['status'],'runtime_metadata_bytes':len(content(run/'runtime_metadata.json')),'server_info_bytes':len(content(run/'server_info.json')),'http_status':200,'process_id':kv['process_id'],'coverage':kv['coverage'],'settings':settings,'global_errors':len(kv['errors']),'error_stage_counts':dict(Counter(e['stage'] for e in kv['errors'])),'first_error':kv['errors'][0],'reason':kv['reason'],'initializer_stage_receipt':'UNVERIFIED; snapshot topology/budget only','topology':{'page_size':top['page_size'],'capacity':top['capacity'],'root_class':top['root_class'],'writer_class':top['writer_class'],'allocator_class':top['allocator_class'],'mapping':top['mapping'],'buffer_layers':len(top['buffers']),'budget':top['budget']},'completed_rid_labels':len(kv['completed_rids']),'banks':bank_observations,'numeric_acceptance':kv['numeric_acceptance'],'interpreted_summaries':0,'physical_slot_values':'UNVERIFIED','complete_fresh_capture':'UNVERIFIED'},
 'terminal_platform':{'status':'UNVERIFIED','expected_primary_receipt':str(base/'terminal-platform-A-r2.json'),'receipt_used':False,'stop_inferred_from_cleanup':False,'result_status':result['status'],'native_measurements_completed':result['native_measurements_completed'],'caller_cleanup_completed':result['cleanup_completed'],'server_returncode_before_cleanup':result['server_returncode_before_cleanup'],'server_shutdown_returncode':result['server_shutdown_returncode']},
 'critical_input_sha256':{str(p):sha(p) for p in critical},'original_a_r1_proofs_sha256':old_proofs,
 'limits':['Controls/source/selected CPP PASS is not overall KV diagnostic PASS','Global RID-null note_cpp/fresh errors prevent complete capture qualification; no RCA or fix here','Partial bank/fresh-layer/OLD fragment labels do not prove physical7955, zero-cold OLD, original slot equality, native observer S or KV numbers','One responding TP0 process only; no all-TP or device-completion acceptance','Private package/library staging and source inventories are not same-GPU-callback origin/SO-hash proof','Retained model manifests are not full-weight checksums; configured image is not terminal imageID proof','Terminal/platform verdict reserved for primary filtered receipt; cleanup does not establish stop','Original R2/CPU/WIT/r1 proofs, warm1/4 FAIL and formal HOLD remain preserved']}
for p,d in snapshots.items(): assert hashlib.sha256(p.read_bytes()).hexdigest()==d
for (ref,p),d in list(git_inputs.items()): assert hashlib.sha256(fixed(ref,p)).hexdigest()==d
output['scoped_inputs_checked_unchanged']={'retained_files':len(snapshots),'immutable_git_blobs':len(git_inputs)}
print(json.dumps(output,indent=2))
```

### Artifact verification command

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import contextlib,io,json,time
from pathlib import Path
p=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_A_r2_results.md')
q=p.parent/'evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-A-r2.json'
code=p.read_text().split('```python\n',1)[1].split('\n```',1)[0]
stream=io.StringIO();start=time.perf_counter()
with contextlib.redirect_stdout(stream): exec(compile(code,str(p)+':verifier','exec'),{})
assert json.loads(stream.getvalue())==json.loads(q.read_text())
for f in (p,q): assert f.read_bytes().endswith(b'\n') and all(line==line.rstrip() for line in f.read_text().splitlines())
print('A_R2_ARTIFACT_EQUALITY_AND_WHITESPACE_PASS',round(time.perf_counter()-start,3),'seconds; capture FAIL/physical UNVERIFIED/formal HOLD preserved')
PY
```

## Recorded validation

**PASS:** the exact stdout CLI above exited0. It verified16/6,804 exact values, maxabs0/definedrel0,6,780 defined positions/24 zero-reference undefined positions,0 identity/shape/nonfinite errors,16 data-identified HTTP200 responses,10 flushes/log confirmations,0 retractions/generated tokens,8 unchanged comparisons and40 recomputed groups. Cold4/4 and warm1/4 are unchanged; all three warm differences retain their original exact errors in the owned JSON.

**PASS:**194 archived before/after hashes and the40-file frozen6119 source transformation; eight new/six original4f1139 scoring sources; fixed config/R3 linkage,44 Rust source checks,2 retained ELF checks and5 linked receipts. Private staging/runtime source inventory agrees on7 overlapping files, subject to the same-callback limitations above. Selected process340/TP0 metadata has551 startup/30,795 post-loop rows,2,704 unique CPP/terminal joins and169 unique chunk/scheduler joins,16 FULL layers/response RIDs,0 absent/ambiguous joins. All306 retained files and20 immutable Git blobs checked remained unchanged across verification, including both original A r1 result proofs and the original Rust R2 receipt.

**PASS:** exact JSON equality and both owned files' trailing-whitespace/final-newline check exited0 in2.347 seconds. Actual stdout: `A_R2_ARTIFACT_EQUALITY_AND_WHITESPACE_PASS 2.347 seconds; capture FAIL/physical UNVERIFIED/formal HOLD preserved`. Only prose/this checkpoint was added afterwards; the verifier and JSON were unchanged.

**FAIL:** auxiliary capture qualification, with224 global errors preserved in startup/post snapshots and no interpreted summaries. This does not classify training/root math or repair warm correctness. **UNVERIFIED:** complete fresh capture, original physical7,955/zero-cold OLD, original-slot equality, observer-native stream/callback/SO origin, device completion, KV numbers, all-TP coverage and separately filtered platform/container termination. Topology/budget/bank/fragment fields are observations only. Formal04/05 HOLD and original R2/CPU/WIT/r1 proofs remain preserved. No collector RCA/fix, fallback, wait, broader test, raw write, shared edit, native operation, staging or commit was performed.

Final whitespace-only check, after the prose update:

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
from pathlib import Path
p=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_A_r2_results.md')
q=p.parent/'evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-A-r2.json'
for f in (p,q): assert f.read_bytes().endswith(b'\n') and all(line==line.rstrip() for line in f.read_text().splitlines())
print('A_R2_FINAL_OWNED_WHITESPACE_PASS')
PY
```

## 1. 规划完成情况

**汇总：** PASS 3｜FAILED 1｜SKIPPED 1｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| r2 retained scoring/baseline controls | PASS |16/6804 exact；数据身份/比较/flush/retractions均核验。 |
| Frozen6119/source/R3/selected CPP核验 | PASS |194 archive、44 Rust、2 ELF、2704唯一CPP joins。 |
| 辅助采集资格 | FAILED |224全局RID-null错误；只记录，不在本scope修复。 |
| 两个新专属结果文件 | PASS |JSON equality/whitespace exit0/2.347s；旧proofs保留。 |
| 平台终态核验 | SKIPPED |primary独立filtered receipt不在当前依赖；不等待/推断。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次r2 read-only委托至结果交付｜**当前前沿：** primary整合控制结果；collector RCA与filtered终态分别由原owner负责。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR |复用已有pure helper/精确join；stdout/equality核验完成即停止。 |
| D2 细节反复重试 | CLEAR |一次raw Git路径失败明确source与raw边界；完整verifier/equality首次通过。 |
| D3 支线问题修补 | CLEAR |只有两新结果文件；未诊断/修collector。 |
| D4 可并行任务停滞 | CLEAR |collector与terminal由独立owner推进；明确禁止delegation/等待。 |
| D5 超范围镀金 | CLEAR |无新framework、功能或验收扩张；未改原r1/raw。 |
| D6 分析空转 | CLEAR |证据核验是本任务交付；16向量/source/CPP结果已落盘。 |
| D7 路线违背 | CLEAR |无平台/auth/GPU/native/shared-doc/stage/commit；formal HOLD保留。 |

**文档检查：** S1–S4/S6未发现本scoped委托缺陷。S5 `requirements.md:3`、`plan.md:154`、`tickets/04-a-full.md:3`仍以Initial Starting表述Current；应由primary根据实际业务失败与独立终态收据刷新，不能把本报告控制PASS改写为完整capture PASS。此agent无shared-doc编辑权限。
**归因：** 无执行偏离。

## 3. 纠正建议

**分支：** B：Current状态需primary更新，原spec/tickets验收条件不变。

**文档更新（先执行）：**
1. Primary刷新上述Current状态，分列16/6804/source/CPP控制PASS、224全局错误/capture FAIL、partial observations、物理/numeric UNVERIFIED；平台状态仅使用其独立receipt（primary可直接执行；本agent不编辑）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. Primary接受/整合两新结果文件 → 完成标志：限定controls与capture FAIL/UNVERIFIED/HOLD分别保留。
2. 并行：collector owner独立RCA ‖ primary filtered终态核验；本agent无等待或追加操作。

## 4. 最值得关注的 3 点

1. r2再次16/6804 exact，原warm1/4 FAIL未修复；这不是KV diagnostic PASS。
2. topology/budget、两bank及warm OLD fragments仅为观察，224全局错误不能被per-bank无错误/fresh_layers标签覆盖。
3. 2704 CPP joins只限响应process340/TP0；native observer S、physical7955、同callback/SO及平台终态仍待各自证据，不由cleanup推断。
