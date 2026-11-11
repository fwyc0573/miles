## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record primary ACCEPTED bounded actual A-r3 stage by explicit follow-up; preserve all measurement commands/numbers/input snapshots and other-owner physical/FRESH/KV limits; no verifier or test re-execution. |
| 2026-11-11 | Verify only retained A-r3 scoring controls, frozen source/native artifacts, serving binding and bounded callback/CPP stream receipts; read primary's subsequently available filtered terminal receipt; independent physical/FRESH and all KV interpretation remain outside this verifier. |

# Native KV coherence A r3 bounded controls

TaskID: `profile-kv-coherence-native-A-r3-controls-20261111`.

**Primary status: ACCEPTED_BOUNDED_ACTUAL_STAGE.** Primary explicitly accepts the reported actual controls, source/R3 linkage, serving after-import file/class/PID binding, insert–OLD callback OS thread/Torch S, CPP-only unique joins, independent error checks and filtered platform owner-bound scope. Original warm1/4 FAIL and CPP F642383120 != callback S647954864 remain unchanged. No Triton/allTP, alias, device-completion, race or mapped-ELF proof is accepted. Primary reports that the separate compact physical source gate independently passed; final original ordering/lifetime qualification remains in progress under its other owner. This is not this agent's physical/FRESH/KV acceptance.

## Scope and acceptance boundary

Only this report and `evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-A-r3.json` are owned. The actual run is `exp-1111-194637-456465`, retained in `evidence/teacher-scoring-kv-coherence-probe-20261111/native/A/admission-A-r3`. The canonical ORIGINAL baseline remains `evidence/teacher-scoring-runtime-metadata-probe-20261111/native/A/admission-A-r1`, job `exp-1111-073826-369716`, frozen scoring source `4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff`. The accepted A-r2 report/JSON at `027018aa144266833855556f8dcec9dd045b1e4e` supplies the existing controls and verification mechanisms, not a replacement baseline.

READ-ONLY local bounded verification. No native extension, installed runtime, project module import/entrypoint, test suite, build, GPU, API, StepMind, authentication, SSH, cloud, delegation, stage/commit, source/config/test/shared-document/old/raw edits. The fenced verifier adapts the existing A-r2 standard-library checks. It extracts only existing pure comparison, source-string and binding-validation definitions plus data constants from immutable Git bytes. Imports, classes and preparation/build/runtime entrypoints are excluded. No generalized harness is added. KV metrics and physical/FRESH fields are not inspected or interpreted.

**Control/source/binding/S PASS is not overall KV diagnostic PASS.** Actual cold/warm agreement is recomputed against the ORIGINAL baseline; warm1/4 FAIL remains unchanged. Independent physical7955/FRESH qualification belongs to the other agent and remains PENDING here. A global error, binding error or independent native invalidation marker rejects this bounded diagnostic qualification even when bank labels look complete. Marker absence alone does not prove ABI/GIL/alias/race/device-completion properties. Formal04/05 HOLD and06 own200 requirements remain unchanged; B has no A200 dependency.

## Required observations

| Check | Passing condition / boundary |
| --- | --- |
| ORIGINAL vector reproduction |16 logical cases and native RIDs,6804 finite token/value positions, exact identity/shapes; maxabs0 and maximum definedrel0; zero-reference relative error undefined |
| Business controls |16 scored HTTP200,10 HTTP200 flushes and log confirmations,0 retractions/generated tokens;8 identical comparisons and40 recomputed comparison groups |
| Actual mode agreement |Cold4/4 exact; warm1/4 exact,3/4 different; original exact errors preserved |
| Frozen source |8 active and6 ORIGINAL scoring identities; source f8b6b43a, closure c089f0b3, submission-docs4f76ae41 agree on selected source/config/test bytes;6/16/35/40 staged archives and generated runtime agree with frozen source transformations |
| Native artifacts |Original R3 receipt91458e, both ELF files,44 Rust input hashes/transformations, retained native Python pins/adapter overlay and linked receipts; no new build-ID gate |
| Actual serving binding |Resolved module_file/SHA/size match original native preflight and retained observer ELF; module and class labels, positive serving PID, exactTrue module-export/factory-class object ties |
| Bounded S receipts |Insert and inline OLD callback OSthread/Torch current-stream scalar agree within responding serving PID; separate original CPP-only exact unique process-local joins, not adjacency/Triton/allTP proof |
| Error rejection |Startup/post global errors empty, binding_error null, independent invalidation marker absent; otherwise bounded acceptance rejects, independent qualification still pending |
| Platform |Use primary's filtered terminal receipt only; do not infer container termination from caller cleanup or server shutdown-9 |

The serving hash measures file bytes at the resolved loaded-module path after import, **not mapped ELF pages**. Its bounded interpretation relies on the fresh job-owned private package, verified staging and no post-import writer. The frozen receipt-producing code performs a one-shot actual-instance binding capture before selected-bank filtering. No adversarial replacement claim or new build-ID requirement is introduced. Insert/OLD S and CPP in-call F remain separately named contexts, not equated.

## Exact command and environment

Workdir `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Interpreter `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13; conda environment unset. Standard library only; timeout60 seconds and30GiB address-space bound. No dependency or environment changes. A preliminary `python` rule-read command returned127 (`command not found`); the corrected instruction read used `python3`. This was not a verification/native failure.

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'from pathlib import Path; p=Path("task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_A_r3_results.md"); exec(compile(p.read_text().split("```python\n",1)[1].split("\n```",1)[0],str(p)+":verifier","exec"))'
```

```python
import ast, difflib, hashlib, json, math, os, re, resource, subprocess, sys, types
from collections import Counter, defaultdict
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
task = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
base = task/'evidence/teacher-scoring-kv-coherence-probe-20261111'
run = base/'native/A/admission-A-r3'
baseline = task/'evidence/teacher-scoring-runtime-metadata-probe-20261111/native/A/admission-A-r1'
commit = 'f8b6b43a599502cb7ac7fac7231ecf9a5ae5523d'
closure = 'c089f0b3207ac3b55dff4aba2dad03ce53bb4cd1'
submission_docs = '4f76ae4142a0ee7e8445021d7f9d221b8c5dd825'
baseline_commit = '4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff'
r2_commit = '027018aa144266833855556f8dcec9dd045b1e4e'
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
old_proofs = {}
for p in (task/'test_report_2026-11-11_kv_coherence_native_A_r2_results.md', base/'native-verification-A-r2.json', task/'test_report_2026-11-11_kv_coherence_native_A_results.md', base/'native-verification-A.json'):
    assert content(p) == fixed(r2_commit,p)
    old_proofs[str(p)] = sha(p)
old_controls = read_json(base/'native-verification-A-r2.json')
for p,d in old_controls['critical_input_sha256'].items():
    if Path(p).is_relative_to(baseline): assert sha(Path(p)) == d
result, preload, old_result = (read_json(p) for p in (run/'result.json',run/'preload.json',baseline/'result.json'))
assert result['job'] == 'exp-1111-194637-456465' and old_result['job'] == 'exp-1111-073826-369716'
assert result['status'] == 'measurements_completed' and result['native_measurements_completed'] is True and result['cleanup_completed'] is True
assert result['numerical_acceptance'] is None and result['performance_accepted'] is False
for record,ref,count in ((result,commit,8),(old_result,baseline_commit,6)):
    assert len(record['native_scoring_sources']) == count
    for path,identity in record['native_scoring_sources'].items():
        blob = fixed(ref,path)
        assert len(blob) == identity['bytes'] and hashlib.sha256(blob).hexdigest() == identity['sha256']
assert result['native_scoring_sources'] == preload['native_scoring_sources']
for field in ('fixture','config'):
    identity = result[field]; assert identity == preload[field]
    blob = fixed(commit,str(Path(identity['path']).relative_to(Path.cwd())))
    assert len(blob) == identity['bytes'] and hashlib.sha256(blob).hexdigest() == identity['sha256']
config = json.loads(blob)
assert result['config']['sha256'] == old_controls['source']['config_sha256']
assert config['repeats'] == 1 and config['kv_coherence_build_receipt'].endswith('native-rust-kv-observer-qualification-20261111-r3/observer-build.json')
scoped_paths = list(result['native_scoring_sources']) + ['tests/manual/agent_opd/sglang_rust_kv_observer.py','tests/manual/agent_opd/probe_rust_kv_observer.py','tests/fast/test_sglang_kv_coherence.py','tests/fast/test_teacher_scoring_probe.py']
scoped_paths += [str(Path(result[k]['path']).relative_to(Path.cwd())) for k in ('config','fixture')]
for p in scoped_paths:
    assert fixed(commit,p) == fixed(closure,p) == fixed(submission_docs,p) == content(Path(p))
# Definition-only extraction: no imports, classes, runtime or preparation entrypoints.
pure = {
 'sglang_mamba_snapshots': ('source_manifest','_sha256','_rewrite'),
 'sglang_mamba_runtime_metadata': ('_receipt','source_manifest','_sha256','_rewrite'),
 'sglang_kv_streams': ('_descriptor','_terminal','source_manifest','_rewrite','_qualified_baseline'),
 'sglang_kv_coherence': ('_runtime_source','_edits','_rewrite','source_manifest'),
 'sglang_rust_kv_observer': ('_sha','_replace','_rust_candidate','_adapter_candidate'),
 'probe_teacher_scoring': ('_comparison','_coherence_native_bindings'),
}
definitions = {}
for name,names in pure.items():
    path = f'tests/manual/agent_opd/{name}.py'; text = fixed(commit,path).decode()
    scope = {'hashlib':hashlib,'math':math,'re':re,'Path':Path,'__file__':f'{commit}:{path}', **definitions}
    nodes = [n for n in ast.parse(text).body if (isinstance(n,ast.FunctionDef) and n.name in names) or (isinstance(n,ast.Assign) and name != 'probe_teacher_scoring')]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),scope['__file__']+':pure-definitions','exec'),scope)
    module = types.SimpleNamespace(**scope)
    definitions[{'sglang_mamba_snapshots':'snapshots','sglang_mamba_runtime_metadata':'metadata','sglang_kv_streams':'streams','sglang_kv_coherence':'coherence','sglang_rust_kv_observer':'native','probe_teacher_scoring':'probe'}[name]] = module
coherence, witness, native, probe = (definitions[n] for n in ('coherence','streams','native','probe'))
frozen_helper = fixed(commit,'tests/manual/agent_opd/sglang_kv_coherence.py').decode()
def frozen_helper_path(path):
    assert path == coherence.__file__
    return types.SimpleNamespace(read_text=lambda:frozen_helper)
coherence._runtime_source.__globals__['Path'] = frozen_helper_path
fixture_id = result['sample_manifest']['source_fixture']; fixture = Path(fixture_id['path'])
assert sha(fixture) == fixture_id['sha256'] == 'c45424e8106c2beb7500acacb68aa0939da0088c926af8012dd9fbd780f0ffc9'
samples = read_json(fixture)['samples'][:4]
requests, old_requests, cache, comparisons = (read_lines(p) for p in (run/'requests.jsonl',baseline/'requests.jsonl',run/'cache.jsonl',run/'comparisons.jsonl'))
fields = ('pair','phase','mode','source_uid','sample_index','repetition'); key = lambda r:tuple(r[k] for k in fields)
assert len(requests) == len({r['request_id'] for r in requests}) == len({r['native_request_id'] for r in requests}) == 16
assert [key(r) for r in requests] == [key(r) for r in old_requests]
assert len(list((run/'completion_scores').glob('*.json'))) == 16
vectors, identities, vector_rows = {}, [], []
for r,old in zip(requests,old_requests):
    s = samples[r['sample_position']]; n,length = len(s['tokens']),s['response_length']; start = 0 if r['mode']=='full_input' else n-length-1
    assert (r['source_uid'],r['sample_index']) == (s['source_uid'],s['sample_index'])
    assert r['status']=='scored' and r['http_status']==200 and r['cache_salt'] is None and r['repetition']==0
    assert (r['input_count'],r['prompt_count'],r['response_count'],r['logprob_start_len']) == (n,n-length,length,start)
    assert r['input_token_logprobs_count']==r['expected_input_token_logprobs_count']==n-start
    assert r['first_input_token_logprob'] is None and r['first_input_token_id']==r['first_requested_input_token_id']==s['tokens'][start]
    assert r['returned_completion_count']==length and r['token_ids_match'] is True and r['finite_log_probs'] is True
    assert r['completion_token_id_mismatches']==r['nonfinite_log_prob_positions']==[]
    assert r['meta_info']['completion_tokens']==r['meta_info']['output_token_logprobs_length']==r['meta_info']['num_retractions']==0
    v = read_json(run/'completion_scores'/f"{r['request_id']}.json"); previous = read_json(baseline/'completion_scores'/f"{old['request_id']}.json")
    assert key(v)==key(r) and v['request_id']==r['request_id'] and v['native_request_id']==r['native_request_id']==r['meta_info']['id']
    assert v['token_ids']==previous['token_ids']==s['tokens'][-length:] and len(v['token_ids'])==len(v['log_probs'])==length
    assert all(math.isfinite(x) for x in v['log_probs']) and v['log_probs']==previous['log_probs']
    c = probe._comparison(previous,v); assert c['token_ids_match'] and c['finite_log_probs'] and c['values_exact']
    vector_rows.append(c); vectors[r['request_id']]=v
    identities.append({'request_id':r['request_id'],'native_request_id':r['native_request_id'],'sample_index':r['sample_index'],'values':length})
assert sum(len(v['log_probs']) for v in vectors.values()) == 6804
undefined = sum(c['relative_error_undefined_count'] for c in vector_rows); assert undefined == 24
assert len(cache)==10 and all(c['status']=='flushed' and c['http_status']==200 for c in cache)
log = content(run/'server.log').decode(errors='replace'); assert log.count('Cache flushed successfully!')==10
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
assert recomputed==40 and warm_errors==old_controls['warm_errors']
assert sum(c['full_vs_response_only']['values_exact'] for c in comparisons if c['phase']=='cold')==4
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
assert receipt['manifest']['runtime_sha256']=='7ed5b5fb56ef736afee2c9e9aefa7543a779e53f18b3cf3cf7c0943618816308'
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
native_root=task/'evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source'
for p,d in native._PYTHON_PINS.items(): assert sha(native_root/p)==d
adapter=content(native_root/native._ADAPTER); after_adapter=native._adapter_candidate(adapter)
assert hashlib.sha256(after_adapter).hexdigest()==n['adapter_after_sha256']
adapter_diff=''.join(difflib.unified_diff(adapter.decode().splitlines(True),after_adapter.decode().splitlines(True),fromfile=f'a/{native._ADAPTER}',tofile=f'b/{native._ADAPTER}'))
assert content(run/'kv_coherence_source_preflight/native_observer/adapter.patch').decode()==adapter_diff
rust_checks=0; elf_bytes={}
for variant,side in (('baseline','before'),('observer','after')):
    raw=content(Path(build[variant]['path'])); assert raw.startswith(b'\x7fELF') and hashlib.sha256(raw).hexdigest()==build[variant]['sha256']; elf_bytes[variant]=len(raw)
    for p,i in build['source_manifest'][side].items():
        raw=content(Path(build[variant]['workspace'])/p); assert len(raw)==i['bytes'] and hashlib.sha256(raw).hexdigest()==i['sha256']
        if side=='before': assert i['sha256']==native._RUST_PINS[p]
        rust_checks+=1
assert rust_checks==44
for p in native._RUST_PINS: assert native._rust_candidate(p,content(Path(build['baseline']['workspace'])/p))==content(Path(build['observer']['workspace'])/p)
for i in (*build['input_receipts'].values(),build['qualification_receipt']): assert len(content(Path(i['path'])))==i['bytes'] and sha(Path(i['path']))==i['sha256']
assert read_json(Path(build['qualification_receipt']['path']))==build['qualification']
dependencies=read_json(build_path.parent/'dependency-source-manifest.json')
assert len(dependencies)==6
for p,i in dependencies.items():
    raw=content(build_path.parent/'dependencies'/p); assert len(raw)==i['bytes'] and hashlib.sha256(raw).hexdigest()==i['sha256']
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
assert kv['process_id']==ikv['process_id']==m['process_id']==im['process_id']==333
assert m['rank']==im['rank']=={'dp_rank':None,'tp_rank':0,'pp_rank':0,'attn_dp_rank':0,'attn_tp_rank':0}
probe._coherence_native_bindings(post,n)
binding=kv['native_binding']; assert binding==ikv['native_binding']
assert binding['module']==native.MODULE and binding['module_file']==n['binary_target'] and binding['module_sha256']==n['compiled_sha256']
assert type(binding['module_bytes']) is int and binding['module_bytes']==elf_bytes['observer']==3411248
assert binding['class']=='RustUnifiedTreeCoreBinding' and binding['class_is_module_attribute'] is True and binding['factory_class_matches'] is True
assert binding['process_id']==333 and type(binding['process_id']) is int
marker=native.INVALIDATION_ERROR_MARKER
marker_matches=[{'line_number':i,'text':line} for i,line in enumerate(log.splitlines(),1) if marker in line]
assert n['invalidation_failure_marker']==build['qualification']['invalidation_failure_marker']==marker
# Independent marker/global-error checks never accept from bank completeness alone.
assert not marker_matches and kv['errors']==ikv['errors']==[] and kv['binding_error'] is None and ikv['binding_error'] is None
assert ikv['status']=='metadata_only' and kv['status']=='captured' and kv['numeric_acceptance'] is None
assert metadata['status']==result['runtime_metadata']['status']=='collected' and metadata['http']['http_status']==200
assert result['kv_coherence']['status']=='collected'
assert len(kv['completed_rids'])==16 and set(kv['completed_rids'])=={r['native_request_id'] for r in requests}
streams,terminals,chunks,boundaries=(defaultdict(list) for _ in range(4))
join=lambda f:(tuple(f['rids']),tuple(f['prefix_lens']),tuple(f['extend_lens']),f['k_cache_data_ptr'],f['v_cache_data_ptr'],f['writer_loc_data_ptr'])
for seq,event,fields_row in m['rows']:
    f=dict(fields_row); assert len(f)==len(fields_row)
    if event=='kv_store_stream':
        assert f['store_kind']=='cpp_store_cache' and f['native_stream_scalar_observed'] is True and f['launch_enqueued'] is True
        assert type(f['native_actual_stream']) is int and f['native_actual_stream']>=0 and f['native_actual_stream']==f['torch_current_raw_stream']
        streams[join(f)].append(f)
    elif event=='kv_store_terminal':
        assert f['store_kind']=='mha_set_kv_buffer_impl' and f['native_stream_scalar_observed'] is False and f['native_actual_stream'] is None
        assert len(f['rids'])==len(f['prefix_lens'])==len(f['extend_lens'])==1
        terminals[join(f)].append(f); chunks[(f['rids'][0],f['prefix_lens'][0],f['extend_lens'][0])].append(f)
    elif event=='scheduler_track_boundary': boundaries[(f['rid'],f['prefix_len'],f['extend_len'])].append(f)
layers=list(range(3,64,4))
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
by_rid={r['native_request_id']:r for r in requests}; callback_receipts=[]
assert len(kv['banks'])==2
for b in kv['banks']:
    case=by_rid[b['rid']]; insert=b['insert']
    assert case['sample_index']==1695 and case['sample_position']==2 and case['mode']=='full_input' and case['repetition']==0
    assert insert['rid']==b['rid'] and insert['P']==90112 and insert['E']==98304
    assert type(insert['thread_id']) is int and insert['thread_id']==binding['process_id']
    assert type(insert['torch_current_raw_stream']) is int and insert['torch_current_raw_stream']>=0
    callbacks=[]
    for f in b['fragments']:
        assert f['rid']==b['rid'] and (f['P'],f['E'])==(insert['P'],insert['E'])
        assert type(f['thread_id']) is int and type(f['torch_current_raw_stream']) is int
        assert (f['thread_id'],f['torch_current_raw_stream'])==(insert['thread_id'],insert['torch_current_raw_stream'])
        callbacks.append({k:f[k] for k in ('rid','thread_id','torch_current_raw_stream')})
    callback_receipts.append({'request_id':case['request_id'],'rid':b['rid'],'serving_process_id':binding['process_id'],'insert_thread_id':insert['thread_id'],'insert_torch_current_raw_stream':insert['torch_current_raw_stream'],'callbacks':callbacks})
assert {c['request_id'] for c in callback_receipts}=={'cold-r0-s2-full_input','warm_stream-r0-s2-full_input'}
assert [len(c['callbacks']) for c in callback_receipts]==[0,2]
terminal_path=base/'admission-A-r3.terminal.json'; terminal=read_json(terminal_path)
assert terminal['job']==result['job'] and terminal['creator']=='i-fengyicheng' and terminal['status']['phase']=='Succeeded'
assert terminal['status']['finishTime']=='2026-11-11T11:56:55Z' and terminal['native_execution_succeeded'] is True
platform_path=base/'terminal-platform-A-r3.json'; platform=read_json(platform_path)
assert (platform['job'],platform['uid'],platform['creator'])==(terminal['job'],terminal['uid'],terminal['creator'])
assert platform['status']==platform['sdk_terminal_status']==terminal['status'] and platform['source_commit']==commit
assert platform['source_mount']=='100.96.128.195:/data/ycfeng:/data/ycfeng' and platform['charged_group']=='codesign' and platform['preemptible']=='no'
assert platform['positive_tags']==['H800'] and len(platform['containers'])==len(platform['replicas'])==1
container=platform['containers'][0]; replica=platform['replicas'][0]
assert container['name']=='probe' and container['image']==runtime['configured_image']
assert container['resources']['limits']==container['resources']['requests']=={'cpu':'32','memory':'250Gi','nvidia.com/gpu':'4'}
assert replica['phase']=='Succeeded' and replica['node_name']=='gpu-h800-0246.host.platform.shaipower.com'
assert replica['owner_references']==[{'kind':'RJob','name':result['job'],'uid':terminal['uid'],'controller':True}]
assert len(replica['containers'])==1
terminal_container=replica['containers'][0]; stopped=terminal_container['terminated']
assert terminal_container['name']=='probe' and terminal_container['restart_count']==0 and terminal_container['last_state']=={}
assert stopped=={'exitCode':0,'reason':'Completed','startedAt':'2026-11-11T11:51:24Z','finishedAt':'2026-11-11T11:56:52Z'}
critical=(run/'result.json',run/'preload.json',run/'requests.jsonl',run/'cache.jsonl',run/'comparisons.jsonl',run/'server_info.json',run/'runtime_metadata.json',run/'server.log',baseline/'result.json',baseline/'requests.jsonl',baseline/'comparisons.jsonl',build_path,terminal_path,platform_path)
output={'task_id':'profile-kv-coherence-native-A-r3-controls-20261111','pair':'A','job':result['job'],
 'verdicts':{'retained_controls':'PASS','all16_6804_ORIGINAL_baseline_reproduction':'PASS','frozen_source_archive_r3_linkage':'PASS','serving_file_binding':'PASS_BOUNDED_FILE_IDENTITY','insert_old_thread_torch_S':'PASS_RESPONDING_PID_ONLY','selected_cpp_in_call_joins':'PASS_CPP_ONLY','independent_marker_global_errors':'PASS_NO_ERROR_OBSERVED','warm_correctness':'FAIL_UNCHANGED_1_OF_4','independent_physical_7955':'PENDING_OTHER_AGENT','complete_FRESH_qualification':'PENDING_OTHER_AGENT','kv_numeric_coherence':'NOT_INSPECTED','full_terminal_platform':'PASS_PRIMARY_FILTERED_BOUNDED','formal04_05':'HOLD'},
 'local_environment':{'python':sys.version.split()[0],'executable':sys.executable,'conda_default_env':os.environ.get('CONDA_DEFAULT_ENV'),'timeout_seconds':60,'address_space_limit_bytes':30*1024**3,'project_native_module_execution':False,'source_definitions':'Existing pure definitions/data constants only; imports/classes/entrypoints excluded'},
 'baseline':{'path':str(baseline),'job':old_result['job'],'source_commit':baseline_commit,'native_source_identities_verified':6,'raw_results_git_objects':False,'accepted_r2_controls_commit':r2_commit,'r2_used_as_replacement_baseline':False},
 'workload':{'requests':16,'unique_native_rids':16,'finite_vectors':16,'values':6804,'http200_flushes':10,'log_flushes':10,'retractions':0,'generated_tokens':0,'unchanged_comparisons':8,'recomputed_groups':40,'cold_exact':4,'warm_exact':1,'warm_different':3},
 'vector_errors':{'max_absolute_error':max(c['max_absolute_error'] for c in vector_rows),'max_defined_relative_error':max(c['max_relative_error'] for c in vector_rows),'defined_relative_count':6804-undefined,'zero_reference_relative_undefined':undefined,'identity_shape_nonfinite_errors':0,'tolerance':None},
 'response_identities':identities,'warm_errors':warm_errors,
 'source':{'frozen_commit':commit,'closure_commit':closure,'submission_docs_commit':submission_docs,'scoped_cross_commit_live_byte_matches':len(scoped_paths),'helper_sha256':result['native_scoring_sources']['tests/manual/agent_opd/sglang_kv_coherence.py']['sha256'],'native_scoring_source_sha256':{p:i['sha256'] for p,i in result['native_scoring_sources'].items()},'config_sha256':result['config']['sha256'],'generated_runtime_sha256':receipt['manifest']['runtime_sha256'],'archive_file_counts':{**counts,'kv_coherence_source_preflight':40},'archive_hash_checks':archive_checks,'runtime_overlap_hash_matches':overlap,'r3_build_sha256':sha(build_path),'r3_source_commit':r3source['native_code_ref'],'rust_source_checks':rust_checks,'native_python_pins':3,'retained_dependency_checks':6,'elf_checks':2,'elf_bytes':elf_bytes,'linked_receipts':5,'original_rust_r2_receipt_preserved':True,'global_inventory_rehash':False},
 'private_staging':{'package_root':str(private),'import_origin':package['import_origin'],'child_pythonpath':package['child_pythonpath'],'production_module':n['module'],'binary_target':n['binary_target'],'compiled_sha256':n['compiled_sha256'],'package_legacy_pending_label':package['serving_native_origin_sha'],'actual_binding_source':'server_info.internal_states[0].kv_coherence.native_binding','original_binary_source_commit':'UNVERIFIED'},
 'serving_binding':{'status':'PASS_BOUNDED_FILE_IDENTITY','receipt':binding,'binding_error':kv['binding_error'],'startup_and_post_receipts_equal':True,'expected_preflight_path_sha_match':True,'observer_ELF_size_sha_match':True,'hash_semantics':'Resolved module file bytes after import, not mapped ELF pages','assumption':'Fresh job-owned private package; staged bytes verified; no post-import writer','build_id_gate_added':False,'callback_module_rehashed_per_callback':False},
 'worker_runtime':{k:runtime[k] for k in ('python','executable','sglang','torch','gpu_devices','configured_image','model_path','model_manifest_identity','sglang_environment')},'teacher_argv':result['argv'],
 'callback_S':{'status':'PASS_RESPONDING_PID_ONLY','process_id':binding['process_id'],'coverage':kv['coverage'],'receipt_mechanism':'Existing insert and inline OLD callback OS native thread plus Torch current raw stream','banks':callback_receipts,'cpp_and_callback_contexts_equated':False,'device_completion':'UNVERIFIED','native_CUDA_observer_stream_API_measurement':'NOT_CLAIMED'},
 'selected_cpp':{'status':'PASS_SELECTED_CPP_IN_CALL_ONLY','process_id':m['process_id'],'rank':m['rank'],'startup_rows':len(im['rows']),'post_rows':len(m['rows']),'unique_cpp_terminal_joins':2704,'unique_chunk_scheduler_joins':169,'missing_or_ambiguous_joins':0,'full_layers':layers,'response_rids':16,'cpp_native_scalar_values':sorted({f['native_actual_stream'] for v in streams.values() for f in v}),'join_fields':['rids','prefix_lens','extend_lens','k_cache_data_ptr','v_cache_data_ptr','writer_loc_data_ptr'],'terminal_own_scalar_observed':False,'KV_prefix_valid_Triton_receipts':0,'all_TP_coverage':False,'device_completion':'UNVERIFIED'},
 'error_gate':{'status':'PASS_NO_ERROR_OBSERVED','startup_global_errors':len(ikv['errors']),'post_global_errors':len(kv['errors']),'binding_error':kv['binding_error'],'independent_native_marker':marker,'marker_matches':marker_matches,'error_or_marker_rejects_even_complete_bank_labels':True,'marker_absence_proves_native_safety':False,'raw_startup_status':ikv['status'],'raw_post_status':kv['status'],'completed_RID_labels':len(kv['completed_rids']),'physical_FRESH_metrics_inspected':False},
 'primary_terminal_receipt':{'path':str(terminal_path),'status':'OBSERVED_FILTERED_JOB_SUCCEEDED','job':terminal['job'],'uid':terminal['uid'],'creator':terminal['creator'],'phase':terminal['status']['phase'],'finishTime':terminal['status']['finishTime'],'native_execution_succeeded':terminal['native_execution_succeeded'],'cleanup_inferred_as_platform_stop':False,'caller_cleanup_completed':result['cleanup_completed'],'server_shutdown_returncode':result['server_shutdown_returncode']},
 'primary_filtered_platform':{'path':str(platform_path),'status':'PASS_PRIMARY_FILTERED_BOUNDED','observed_at':platform['observed_at'],'job_uid':platform['uid'],'creator':platform['creator'],'source_mount':platform['source_mount'],'charged_group':platform['charged_group'],'preemptible':platform['preemptible'],'image':container['image'],'resource_limits':container['resources']['limits'],'replica_name':replica['name'],'replica_uid':replica['uid'],'replica_phase':replica['phase'],'node_name':replica['node_name'],'RJob_owner_UID_exact':True,'container':terminal_container,'imageID':'NOT_RETAINED_IN_FILTERED_RECEIPT','scope':platform['acceptance_limit'],'agent_platform_API_calls':0},
 'critical_input_sha256':{str(p):sha(p) for p in critical},'preserved_a_r1_r2_proofs_sha256':old_proofs,
 'remaining_scope':['Independent physical7955 and complete FRESH qualification owned by the other agent, not inspected here','All numerical KV interpretation and root RCA excluded','Platform/container/ownerUID/image/source allocation read from primary filtered receipt only; imageID not retained, no independent API or actual filesystem mount probe here','One responding PID333/TP0 only; no all-TP, Triton KV, device-completion, race/GIL/alias or mapped-ELF claim','ORIGINAL warm1/4 FAIL and formal04/05 HOLD remain unchanged']}
for p,d in snapshots.items(): assert hashlib.sha256(p.read_bytes()).hexdigest()==d
for (ref,p),d in list(git_inputs.items()): assert hashlib.sha256(fixed(ref,p)).hexdigest()==d
output['scoped_inputs_checked_unchanged']={'retained_files':len(snapshots),'immutable_git_blobs':len(git_inputs)}
output['primary_acceptance']={
 'status':'ACCEPTED_BOUNDED_ACTUAL_STAGE','authority':'Primary explicit follow-up for the same TaskID','recorded_date':'2026-11-11',
 'accepted_scope':['Actual ORIGINAL baseline scoring controls','Frozen source and original R3 linkage','Serving after-import file identity, class-object ties and PID','Insert-OLD callback OS thread and Torch S receipts','CPP-only exact unique joins','Independent marker/global-error checks','Primary filtered platform owner-bound scope'],
 'retained_limits':['Original warm1/4 FAIL unchanged','CPP F642383120 != callback S647954864; contexts not equated','No Triton/allTP/alias/device-completion/race/mapped-ELF proof','Physical/FRESH/KV qualification remains with the other owner'],
 'other_owner_update':{'compact_physical_source_gate':'INDEPENDENTLY_PASSED_PRIMARY_REPORTED','final_original_ordering_lifetime_qualification':'IN_PROGRESS_OTHER_OWNER','independent_evidence_inspected_by_this_agent':False},
 'verification_rerun_for_status_update':False}
print(json.dumps(output,indent=2))
```

## Recorded validation

**PASS:** the exact verifier exited0 on its first execution. All16 ORIGINAL vectors/6804 values reproduce exactly: maxabs0, maximum definedrel0,6780 defined relative positions/24 zero-reference undefined positions,0 identity/shape/nonfinite errors. All16 scored HTTP200,10 HTTP200 flushes/10 log confirmations,0 retractions/generated tokens,8 byte-identical comparisons and40 independently recomputed groups passed. Actual cold4/4/warm1/4 remains unchanged; the three warm failures' exact original errors are retained in the owned JSON.

**PASS:**8 active/6 ORIGINAL scoring-source identities,14 selected cross-commit/live byte equalities for f8b6b43a/c089f0b3/4f76ae41, unchanged config/fixture,194 archived before/after hashes,35 original WIT transformations and40 coherence transformations. Generated runtime SHA is `7ed5b5fb56ef736afee2c9e9aefa7543a779e53f18b3cf3cf7c0943618816308`. The original R3 receipt SHA `91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7`,44 Rust inputs/transformations,3 native Python pins/exact adapter patch,6 retained dependency files,2 ELF files and5 linked receipts passed. Seven serving-source inventory overlaps agree. Initially333 scoped retained files/54 immutable Git blobs remained unchanged through verification, including original A-r1/r2 proof bytes and the original Rust R2 receipt. The final verifier adds the subsequently available primary filtered platform receipt as one more sealed input.

**PASS, bounded file identity:** actual startup/post serving binding receipts agree. Module `sglang.srt.mem_cache.rust_tree_core.mem_cache`, actual private `module_file` equals the original preflight `binary_target`; file SHA `0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba`,3411248 bytes equals the retained observer ELF. Serving PID333 matches both drains and metadata. Class `RustUnifiedTreeCoreBinding` has `class_module="builtins"`; acceptance uses module-export and factory-class object ties, both exactTrue, not the label. The legacy package `serving_native_origin_sha` PENDING string is preserved raw and is not mistaken for the new actual receipt. No per-callback file rehash or mapped-ELF attestation is claimed.

**PASS, responding PID/CPP only:** both selected sample1695 FULL insert receipts have OSthread333/TorchS647954864; both retained warm inline OLD callbacks match that RID/P/E/thread/S and serving PID. Cold has no callback receipt. Exact original process-local CPP keys produce2704 unique CPP/terminal joins and169 unique chunk/scheduler joins,16 FULL layers/16 response RIDs,0 missing/ambiguous joins. Startup551/post30795 metadata rows are retained. The separately measured CPP in-call scalar is642383120 and equals that call's Torch current stream; it is not equated to callback S647954864. Terminal rows' own native scalar observation isfalse. KV-prefix-valid Triton receipts are0; no allTP or device-completion acceptance.

**PASS, no error observed:** startup/post global errors0, binding_error null, independent `old_full_observer_invalidation_failed` marker matches0. These checks execute independently of bank labels and reject on any error/marker. Raw startup `metadata_only`/post `captured` and16 completed RID labels are observations, not this agent's physical/FRESH/KV acceptance. Independent physical7955/FRESH remains PENDING_OTHER_AGENT; KV metrics are NOT_INSPECTED.

**Observed filtered platform facts:** primary's `admission-A-r3.terminal.json` records `Succeeded` at `2026-11-11T11:56:55Z`, native_execution_succeeded exactTrue, creator `i-fengyicheng`, job UID `ea73209b-61cd-4b5d-9d6d-ce49621ffaa4`. During final artifact verification, primary's independent `terminal-platform-A-r3.json` became available at12:03:59Z; it is now an explicit read-only input. It records the same SDK/job terminal state, exact controller owner UID, replicaSucceeded on `gpu-h800-0246.host.platform.shaipower.com`, probe containerCompleted/exit0/restart0, finished11:56:52Z. Source allocation is codesign/nonpreemptible/H800, CPU32/250Gi/GPU4, local NFS `100.96.128.195:/data/ycfeng:/data/ycfeng` and immutable configured image165, consistent with this run. The filtered receipt does not retain runtime imageID or an independent filesystem-mount probe; no new gate is added. Caller cleanup true/server shutdown-9 is not used as a platform-stop inference. Retained model config/index identities are not full-weight checksums. No native execution, platform operation or root RCA was performed. Formal04/05 HOLD and original warm1/4 FAIL are preserved.

**Final artifact PASS:** the command below re-executed the final verifier including the primary filtered receipt, reproduced the owned JSON exactly and passed both files' trailing-whitespace/final-newline checks in2.446 seconds, exit0. Actual stdout: `A_R3_CONTROLS_BINDING_S_ARTIFACT_EQUALITY_PASS 2.446 seconds; physical/FRESH pending; KV not inspected; warm FAIL/formal HOLD preserved`. All334 scoped retained files/54 immutable Git blobs remained unchanged. The earlier pre-platform artifact check passed in2.411 seconds. Only this recorded prose and the checkpoint's completed-artifact status were changed afterwards; verifier/JSON are unchanged. Scoped Git status shows precisely the two owned files untracked; nothing was staged or committed.

## Primary acceptance follow-up

Primary read the complete owned JSON and the recorded native evidence, then explicitly **ACCEPTED_BOUNDED_ACTUAL_STAGE** for the scope stated at the top. This follow-up changes only acceptance annotations in the two owned artifacts; all exact commands, measured values, prior validation timings, histories and sealed input snapshots are retained. The fenced verifier has only a literal primary-acceptance annotation added to its output, matching the JSON annotation; no measurement check is changed and it was not executed again. No full verifier, broad CPU/test, metric read, source/config/shared-document edit, staging/commit, API or native execution occurred. Terminal linkage already passed and requires no new test.

The compact physical source-gate update is primary-reported independent progress, not evidence read by this agent. Final original ordering/lifetime qualification remains in progress with the other owner; the original physical/FRESH pending and KV-not-inspected verdicts remain unchanged here. Original warm1/4 FAIL, distinct F642383120/S647954864 and all stated proof limits are retained. The earlier artifact equality timings below remain historical observations, not a claim that the acceptance-annotated artifacts were re-executed.

## Final artifact check

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import contextlib,io,json,time
from pathlib import Path
p=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_coherence_native_A_r3_results.md')
q=p.parent/'evidence/teacher-scoring-kv-coherence-probe-20261111/native-verification-A-r3.json'
code=p.read_text().split('```python\n',1)[1].split('\n```',1)[0]
stream=io.StringIO();start=time.perf_counter()
with contextlib.redirect_stdout(stream): exec(compile(code,str(p)+':verifier','exec'),{})
assert json.loads(stream.getvalue())==json.loads(q.read_text())
for f in (p,q): assert f.read_bytes().endswith(b'\n') and all(line==line.rstrip() for line in f.read_text().splitlines())
print('A_R3_CONTROLS_BINDING_S_ARTIFACT_EQUALITY_PASS',round(time.perf_counter()-start,3),'seconds; physical/FRESH pending; KV not inspected; warm FAIL/formal HOLD preserved')
PY
```

The four-section checkpoint below is the preserved pre-acceptance verification checkpoint. The primary acceptance follow-up above supersedes only its pending-primary-integration wording; other-owner physical/FRESH/KV and formal limits remain unchanged. This follow-up is complete and this agent stops.

## 1. 规划完成情况

**汇总：** PASS 5｜BLOCKED 1｜SKIPPED 1｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| A-r3 ORIGINAL baseline controls | PASS |16/6804 exact；cold4/4、warm1/4原误差不变。 |
| Frozen source/R3/native inputs | PASS |194 archive、44 Rust、2 ELF、14跨commit/live byte matches。 |
| Actual serving binding / bounded S / CPP | PASS |PID333/S647954864；exactTrue ties；2704/169唯一CPP joins。 |
| Independent marker/global errors and primary terminal receipt | PASS |全局错误0/marker0；ownerUID/Completed0/restart0来自primary filtered receipt。 |
| 两个专属结果文件 | PASS |final JSON equality/whitespace exit0/2.446s；334 retained/54 Git inputs不变。 |
| Independent physical7955/FRESH | TODO |由另一个agent负责；本scope不读取其数值或判定。 |
| KV interpretation / root RCA | SKIPPED |明确不属于本委托，不做数值解释或修复。 |
| Formal04/05与06最终数据 | BLOCKED |warm correctness仍FAIL；06需要各自真实200，不由本probe解除。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次A-r3 read-only委托至交付｜**当前前沿：** primary整合bounded verdict；独立physical/FRESH由原owner推进。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR |复用A-r2 pure checks/唯一join；不增加framework/测试，验收完成即停止。 |
| D2 细节反复重试 | CLEAR |完整verifier首次通过；追加primary新receipt不是修复重试。 |
| D3 支线问题修补 | CLEAR |只写两个专属文件；不处理root/collector问题。 |
| D4 可并行任务停滞 | CLEAR |physical/FRESH独立owner；本agent禁止delegation/等待/API。 |
| D5 超范围镀金 | CLEAR |无新功能/flag/build-ID gate；SO hash按原bounded假设解释。 |
| D6 分析空转 | CLEAR |控制/source/binding/S数值和证据已落盘。 |
| D7 路线违背 | CLEAR |无native/GPU/API/shared-doc/stage/commit；warm FAIL/formal HOLD保留。 |

**文档检查：** S1–S4/S6在本scope与plan/tickets边界未发现明显缺陷。S5 `requirements.md:3`、`plan.md:159`、`progress.md:219`、`tickets/04-a-full.md:75`仍写A-r3 SUBMITTED/Initial与本已观察终态不一致；应由primary分列实际terminal、bounded controls/binding/S与尚待physical/FRESH/KV，不修改科学标准或checkboxes。`tickets/05-b-full.md`的B状态不由本agent推断。
**归因：** 无执行偏离。

## 3. 纠正建议

**分支：** B：Current状态需primary刷新；原spec/tickets验收条件不变。

**文档更新（先执行）：**
1. Primary更新上述Current位置，引用两专属结果文件和自己的terminal receipt；保留independent physical/FRESH pending、KV未解释、warm FAIL/formal HOLD（primary可直接执行；本agent无shared-doc权限）。

**需停止的偏离行为：无。**

**接下去的路线：**
1. Primary整合A-r3 controls/source/binding/S → 完成标志：bounded PASS与pending/not-inspected/HOLD清楚分列。
2. 并行：独立physical/FRESH资格 ‖ primary其余native结果整合；本agent不重复调查、不等待、不追加执行。

## 4. 最值得关注的 3 点

1. A-r3再次16/6804 exact，原warm1/4 FAIL没有被“captured”标签修复。
2. 实际PID333/SO SHA/size/exactTrue ties与insert/OLD S成立；不是mapped ELF、allTP、Triton或device-completion证明。
3. 新primary receipt证明owner-bound Completed0/restart0；physical7955/FRESH仍属独立owner，KV/root/formal不在本scope验收。
