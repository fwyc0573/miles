## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Independently verify retained native A vectors, fixed source composition, actual H800 record, process-local CPP/class/row receipts and filtered terminal evidence. |

# Native A KV stream witness results

TaskID: `profile-kv-stream-witness-native-A-20261111`.

**PASS for bounded source/H800/CPP witness qualification; formal 04/05 remain HOLD. No KV numerical capture or coherence acceptance.** All 16 vectors exactly reproduce the accepted metadata baseline before metadata interpretation. Cold mode parity remains 4/4 exact; warm mode parity remains 1/4 exact and 3/4 different. This preserves the correctness failure rather than repairing it.

## Evidence and ownership

Paths below are relative to `task_memory/task_2026-11-08_qwen35_full_kl_nll/`:

- New run: `evidence/teacher-scoring-kv-stream-witness-probe-20261111/native/A/admission-A-r1/`, job `exp-1111-113511-067358`.
- Accepted baseline: `evidence/teacher-scoring-runtime-metadata-probe-20261111/native/A/admission-A-r1/`, job `exp-1111-073826-369716`, caller `4f1139b0`.
- Derived results: `evidence/teacher-scoring-kv-stream-witness-probe-20261111/native-verification-A.json`.
- Admission/initial CR: `evidence/teacher-scoring-kv-stream-witness-probe-20261111/{admission-A-r1.json,initial-platform-verification.json}`.
- Terminal: the adjacent `admission-A-r1.terminal.json` and primary-provided `terminal-platform-containers.json`, queried at `2026-11-11T03:45:14.622334+00:00`.

Only this new report and the derived JSON are owned/written. No raw source, retained native output, helper/probe/config, shared task document, platform state or Git index is changed; no commit is made. Requirements, plan, tickets 04/05, `design_kv_coherence_measurement.md`, source/integration reports and current progress were inspected. This report does not replace their decision ownership.

## Expected versus actual

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Vector prerequisite | All original first4/repetition0 vectors exactly equal their metadata baseline | 16/16; 6,804 completion log probabilities and corresponding token IDs; shape/ID/nonfinite errors 0; max absolute and defined relative errors 0 | PASS |
| Identity | Join across runs by pair/UID/sample_index/phase/mode/repetition, not native RID | Original samples 1693–1696; all 16 native RIDs differ across runs but each matches its own request/response/vector | PASS |
| Workload | 16 scoring responses, 10 flushes, unsalted sequential original order | 16 scored HTTP200, 8 cold + 8 warm; 10 HTTP200 flushes, 8 cold + 2 warm; no generated tokens/retractions | PASS |
| Own comparisons | Preserve every comparison group and its errors/undefined-zero counts | All 8 complete comparison records equal baseline; recompute full/response, all four cold-reference groups and historical descriptive groups | PASS for reproduction, NOT warm correctness |
| Fixed source | Caller `26664e81`, helper `79dba51b`; no mutable-tree reference | All 7 worker source identities match fixed Git bytes; all 6 baseline identities match `4f1139b0` | PASS |
| Overlay composition | Selected FP32 -> CPU metadata -> witness, 35 final identities/5 witness edits | Fixed helper derives all 35 retained before/after pairs exactly; archive/receipt/preload/result agree; six final attention sources equal baseline | PASS |
| Final runner hash | Use witness final runner, not metadata-stage runner | Final `27eb08f7…` agrees with runtime inventory; metadata-stage `5d074249…` is pre-witness | PASS |
| Actual H800 | Retained worker GPU record, not declared limit | Four `NVIDIA H800, 81559 MiB, 570.124.06` rows | PASS |
| Terminal execution | Exact job UID, one successful replica, Completed0/restart0, pinned image | Job/replica Succeeded; container Completed/exit0/restart0; job finish `03:41:45Z`; imageID equals pinned digest | PASS for execution only |
| Actual allocator/config | TokenToKVPoolAllocator with qualified page1/CP1/disabled alternative branches | Initial row1 actual class/module; page1; CP1; memory saver/hicache/unified memory/sharding off, CUDA graphs off | PASS for this static branch only |
| Scoring CPP scalar | Native scalar observed and launch enqueued, equal Torch current raw stream | 2,704/2,704 actual CPP rows, stream `1266433792`; mismatches/missing/no-launch/zero streams 0 | PASS for in-call launch source only |
| Layer/class/RID join | Explicit keys with uniqueness, complete responding-process coverage | 2,704 unique CPP–plain terminal joins, 169 unique RID/prefix/extend chunks, 16 FULL layers per chunk, all 16 response RIDs | PASS for CPU descriptors only |
| CUDA prefix-valid Triton | Count separately; never certify with CPP/Torch scalar | Scoring 0 plain-prefix Triton / 0 FP8-prefix Triton; startup also 0/0 | NOT EXERCISED / stream UNVERIFIED |
| Physical values/indices, completion, PDL, all TP | Require separate evidence and authorization | No K/V or FULL index contents, CUDA commit lengths, completion or all-TP readback | UNMEASURED / UNVERIFIED; HOLD |

Exact equality has no tolerance. Relative errors are undefined where the reference is zero: 24 zero-reference completion positions across the 16 baseline vector comparisons. The maximum over defined relative errors is zero; undefined positions are not replaced with an epsilon.

### Preserved own warm failures

| Sample | Completion length | Cold full/response max abs error | Warm full/response max abs error | Warm max relative error | Zero-reference positions |
| --- | --- | --- | --- | --- | --- |
| 1693 | 734 | 0 | 0 | 0 | 1 |
| 1694 | 246 | 0 | 7.152048056013882e-07 | 0.14285706500614642 | 1 |
| 1695 | 431 | 0 | 0.19622063636779785 | 0.6111100632456284 | 1 |
| 1696 | 290 | 0 | 0.24439287185668945 | 1.3806473175677756 | 3 |

The four warm comparisons against either independently flushed cold mode are also unchanged. `result.json` retains `numerical_acceptance=null` and `performance_accepted=false`; comparison `accepted` fields stay null. Platform success does not turn any of these into acceptance. The original unsalted shared-cache observations are expected to remain; no salted `full_input` isolation gate is applied.

## Source observations

Fixed caller SHA256: `94cd9f0c93d2f693172367fcce347fb6d2564877d523fa06bf020633c0b3c86f` (39,948 bytes, `26664e81`). Fixed helper SHA256: `6140cdc283c457938d34f06dc8adad3657465cbc800acf08c80cede6e378e51d` (17,123 bytes, `79dba51b`). The source verifier loads only these fixed Git definitions and their fixed standard-library preparer dependencies, then performs reversible string/hash qualification in memory. It never calls `prepare_source`, imports Torch/SGLang, compiles CUDA or changes an installed package.

New `kv_store_stream_source_preflight/source_manifest.json` SHA256 is `076b60a28b3c5de49154e42cdd8ede7f7f99091e4860293cbc61de2b5d4228d0`; `kv_streams.diff` SHA256 is `a6b72b26c5f257ad3c8d5caefb88edfb72bdb3cd60e023a6b95a928c354bc8a2` (11,615 bytes/229 lines/5 files). All 35 before/after hashes match the receipt's observed maps. Six selected-FP32/metadata attention-source final hashes equal the accepted baseline; their CPU metadata differences from the *FP32-only* stage are expected. The witness does not change those six files.

Final witness hashes and recorded runtime paths (root `/sgl-workspace/sglang/python/sglang/`):

| Relative path | Final SHA256 |
| --- | --- |
| `srt/model_executor/model_runner.py` | `27eb08f7f3bb60b15725d0e7bfebab2a9677d38fefe46a2ecf4c015d4f0dd345` |
| `srt/model_executor/forward_context.py` | `6eaceb910915685ad010d8ca04a390c0295009769c36971e679508beb45fe19f` |
| `srt/mem_cache/memory_pool.py` | `74479b98fa3585d46de24f6f7f2f472a8841957ed9221cd6298041f37a2931ad` |
| `kernels/ops/kvcache/kvcache.py` | `ecb70382f151b7d519f9db674305f48109c80dc1b16b7848943b28f29940c0ea` |
| `kernels/jit/csrc/elementwise/kvcache.cuh` | `3e972568f8a731a5e79b5729fb2fc0bf3d823cad2ffd484b4c5c11a263599555` |

All six TVM source paths resolve beneath `/opt/sglang/lib/python3.12/site-packages/tvm_ffi/`, not beneath the SGLang archive. Versions are SGLang `0.5.24.dev80+g056f871`, TVM FFI `0.1.11`; native Python `/opt/sglang/bin/python3` `3.12.16`, Torch `2.14.1+cu130`. The runtime inventory independently repeats four of the 35 identities, including the final runner; the other identities are direct prelaunch file/hash receipts, not independent imported-module/binary attestation. Runtime CPP integer receipts demonstrate the return channel was exercised; no separate compiled-binary hash or selected CAPI-versus-fallback branch receipt exists.

Pinned image: `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`. Initial CR verifies personal creator, local NFS `100.96.128.195:/data/ycfeng:/data/ycfeng` and declared allocation. The filtered terminal `imageID` verifies that digest separately from the worker's configured-image string; its `image` field is a different local image identifier, not a mismatch. Model manifest hashes and mounted source path are retained, not a whole-weight checksum.

## Process-local metadata and joins

Both initial `server_info.json:get_server_info.internal_states[0].mamba_runtime_metadata` and post-loop `runtime_metadata.json:server_info.internal_states[0].mamba_runtime_metadata` belong to process391, TP0/PP0/attention-DP0/attention-TP0, DP size1. Raw `dp_rank=null` is legal only in this DP1 scope. There is no all-TP gather despite the four-GPU TP4 engine.

- Initial drain: 551 rows (seq1–551), including actual allocator row1, 144 CPP stream rows and 144 plain terminals from startup. These are not the 16 diagnostic scoring requests.
- Post-loop drain: 30,795 rows (seq552–31346), including 2,704 CPP stream rows, 2,704 plain terminals, 169 scheduler boundaries and 165 prefill plans. Combined CPP count2,848; combined plain terminal count2,848; both Triton-prefix terminal variants0. No missing/unobserved CPP scalar or no-launch receipt is present. Stream0 would be valid; `-1` is the native no-launch sentinel, not a witness.
- Allocator row1 records `sglang.srt.mem_cache.allocator.token.TokenToKVPoolAllocator`, object139599833335664, size1,833,688/page1/BF16, with outer `HybridLinearKVPool` object139600601903472. Plain terminals record inner `MHATokenToKVPool` object139600597851248. These are different objects. No explicit runtime parent/child object link is recorded; they must not be joined by equality of object IDs. The allocator class is directly observed, while applying its source lifetime argument is a conditional inference restricted to the recorded config.
- Join CPP to terminal only by `(rids, prefix_lens, extend_lens, k_cache_data_ptr, v_cache_data_ptr, writer_loc_data_ptr)` within this process/rank. Each side has2,704 unique keys, exactly one row per key and identical key sets: zero absent or ambiguous joins. Sequence adjacency and recycled tensor object IDs are not used.
- Group terminals by `(nativeRID, prefix, extend)` only after checking equal field lengths. All observed batches have one explicit RID, not an assumed one-request default. Each of169 keys has one scheduler boundary with the same RID/prefix/extend and `seq_end=prefix+extend`, and exactly one terminal/CPP pair for each of16 actual layers. Layer IDs3,7,…,63 map explicitly to pool/buffer indices0…15. Every layer has169 records; all16 response RIDs are covered.
- Class-owned K/V descriptors are BF16 `[1833689,1,256]`, strides `[256,256,1]`; CPP views are `[1833689,256]`, strides `[256,1]`, same K/V buffer pointers and512 bytes per K or V row. Writer descriptors are int64 `[extend]`, stride1, with matching writer pointers. These verify descriptor shapes and host row binding, not physical slot indices or K/V contents.

Decisive target references: original warm-full sample1695 binds through response/vector RID `c1745ed1548e4b12885700dc3d5c0617`. Its `(RID,90112,8192)` chunk has scheduler row25695 (`seq_end=98304`), sixteen actual layer pairs; layer3 CPP row25707 and terminal row25708 join by K pointer139571874496512, V pointer139572813345280, writer pointer139577020907520, RID/prefix/extend. These row numbers are references, never chronology-based join keys. The terminal itself truthfully keeps `native_stream_scalar_observed=false/native_actual_stream=null`; only its uniquely joined *CPP in-call row* supplies the scalar. No terminal flag is rewritten to pretend it observed the stream itself.

### Interpretation limits

CPP integer equality with Torch current raw stream proves only the recorded in-call launch-source scalar, after host launch. It is not launch-before preflight, kernel completion, PDL/canonical KV coherence, physical lifetime verification, race exclusion, a fix or retroactive fidelity for another run. CUDA prefix-valid Triton paths were not exercised; their stream status remains UNVERIFIED. If a later required path selects either without its own witness, the CPP receipts are insufficient to arm payload capture.

The actual allocator/config permits applying only the previously qualified static TokenToKVPoolAllocator argument: page1/CP1, graphs off, memory saver/hicache/unified memory/sharding off. No model-label inference or other-allocator claim is added. FULL physical writer/insert/rebind index contents and CUDA commit lengths remain unmeasured; no numeric capture is performed or authorized by this PASS. Warm correctness, all TP ranks, full original56-request/two-repeat coverage, dropped1024-hit groups, whole-model checksums, causal diagnosis and performance remain unaccepted. Formal04/05 stay HOLD; no new A200 dependency is introduced.

## Execution errors and terminal limits

The initial exact-job corev1 pod read returned retained `ForbiddenException/status403` in `terminal-platform-containers-A.json:26–29`. The primary's later exact-replica kapis receipt succeeds independently; the old403 is unchanged, non-blocking historical evidence, not a probe failure or substituted authorization. This agent performs no platform/auth/private evidence query. Job/replica UID names match local receipts; raw owner references are not included in the filtered file, so its owner-UID qualification relies on the primary's supplied verification rather than a new independent raw owner-reference read.

The local first attempt to apply `systemd-run --scope -p MemoryMax=30G` failed **before Python execution**: `Failed to start transient scope unit: Interactive authentication required.` No authentication was attempted. Subsequent exact-job reads use `timeout60s` plus Python `RLIMIT_AS=30GiB`, with no system configuration change. Server log lines11/13/15/17 retain four NVML memory-affinity warnings; successful outputs and terminal proof do not erase them. `server_returncode_before_cleanup=null`, `server_shutdown_returncode=-9`, `cleanup_completed=true` describe the caller's child cleanup (`26664e81:probe_teacher_scoring.py:647–653`), not the main container exit, which is0.

## Reproducible offline verification

Workdir: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Local verification uses `/usr/bin/python3`, Python3.10.6, no conda activation, no third-party runtime imports; only standard-library JSON/hash/AST and fixed Git source definitions. No CUDA content reads, synchronization or runtime GPU commands are executed. The command below recomputes the derived result on stdout without writing any file. Input snapshots are checked again before exit to verify raw bytes stayed unchanged during the command. Other inspected paths are listed above; early inventory commands only read those same scoped artifacts. Expected: all assertions pass and JSON carries bounded witness PASS with formal HOLD.

```bash
timeout 60s /usr/bin/python3 -B - <<'PY'
import ast, hashlib, json, math, platform, resource, subprocess, sys, types
from collections import Counter, defaultdict
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
task = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
proof = task / 'evidence/teacher-scoring-kv-stream-witness-probe-20261111'
run = proof / 'native/A/admission-A-r1'
baseline = task / 'evidence/teacher-scoring-runtime-metadata-probe-20261111/native/A/admission-A-r1'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
read = lambda path: json.loads(path.read_text())
lines = lambda path: [json.loads(x) for x in path.read_text().splitlines()]
raw_before = {p: sha(p.read_bytes()) for root in (run, baseline) for p in root.rglob('*') if p.is_file()}
result, base_result, preload = read(run / 'result.json'), read(baseline / 'result.json'), read(run / 'preload.json')
identity_fields = ('pair', 'source_uid', 'sample_index', 'phase', 'mode', 'repetition')
identity = lambda row: tuple(row[k] for k in identity_fields)
def vectors(root):
    rows = [read(p) for p in sorted((root / 'completion_scores').glob('*.json'))]
    mapped = {identity(row): row for row in rows}
    assert len(rows) == len(mapped) == 16
    return mapped
current, previous = vectors(run), vectors(baseline)
requests, base_requests = lines(run / 'requests.jsonl'), lines(baseline / 'requests.jsonl')
assert len(requests) == len(base_requests) == 16 and set(current) == set(previous)
assert [identity(q) for q in requests] == [identity(q) for q in base_requests]
fixture = read(task / 'evidence/teacher-scoring-probe-20261111/retained-cases.json')['samples'][:4]
samples = {(s['source_uid'], s['sample_index']): s for s in fixture}
vector_rows = []
for q in requests:
    key = identity(q)
    score, old = current[key], previous[key]
    sample = samples[(q['source_uid'], q['sample_index'])]
    assert score['token_ids'] == old['token_ids'] == sample['tokens'][-sample['response_length']:]
    assert score['log_probs'] == old['log_probs'] and all(math.isfinite(v) for v in score['log_probs'])
    assert len(score['token_ids']) == len(score['log_probs']) == q['response_count'] == sample['response_length']
    assert q['input_count'] == len(sample['tokens']) and q['repetition'] == 0 and q['cache_salt'] is None
    assert q['native_request_id'] == score['native_request_id'] == q['meta_info']['id']
    assert q['status'] == 'scored' and q['http_status'] == 200 and q['token_ids_match'] and q['finite_log_probs']
    assert not q['completion_token_id_mismatches'] and not q['nonfinite_log_prob_positions']
    assert q['meta_info']['completion_tokens'] == q['meta_info']['output_token_logprobs_length'] == q['meta_info']['num_retractions'] == 0
    vector_rows.append({'request_id': q['request_id'], 'sample_index': q['sample_index'], 'completion_length': len(score['log_probs']),
                        'native_request_id': q['native_request_id'], 'exact': True, 'baseline_rid_differs': score['native_request_id'] != old['native_request_id']})
assert len({q['native_request_id'] for q in requests}) == 16
flushes = lines(run / 'cache.jsonl')
assert len(flushes) == 10 and all(q['status'] == 'flushed' and q['http_status'] == 200 for q in flushes)
assert result['expected_scoring_requests'] == 16 and result['sample_count'] == 4 and result['repeats'] == 1
assert result['numerical_acceptance'] is None and result['performance_accepted'] is False
fixed = lambda revision, path: subprocess.check_output(['git', 'show', f'{revision}:{path}'])
caller = fixed('26664e81', 'tests/manual/agent_opd/probe_teacher_scoring.py').decode()
node = next(n for n in ast.parse(caller).body if isinstance(n, ast.FunctionDef) and n.name == '_comparison')
namespace = {'math': math}
exec(compile(ast.get_source_segment(caller, node), '<fixed-comparison>', 'exec'), namespace)
compare = namespace['_comparison']
comparisons = lines(run / 'comparisons.jsonl')
assert comparisons == lines(baseline / 'comparisons.jsonl') and len(comparisons) == 8
by_request = {v['request_id']: v for v in current.values()}
recomputed = 0
for row in comparisons:
    full, response = by_request[row['full_request_id']], by_request[row['response_request_id']]
    assert compare(full, response) == row['full_vs_response_only']; recomputed += 1
    if row['cold_reference']:
        reference = row['cold_reference']
        cf, cr = by_request[reference['full_request_id']], by_request[reference['response_request_id']]
        for name, left, right in [('cold_full_vs_warm_full', cf, full), ('cold_full_vs_warm_response_only', cf, response),
                                  ('cold_response_only_vs_warm_full', cr, full), ('cold_response_only_vs_warm_response_only', cr, response)]:
            assert compare(left, right) == reference[name]; recomputed += 1
    sample = samples[(row['source_uid'], row['sample_index'])]
    expected = {'token_ids': sample['tokens'][-sample['response_length']:], 'log_probs': sample['expected_teacher_log_probs']}
    for name, score in [('full_input', full), ('response_only', response)]:
        assert compare(expected, score) == row['historical_expected'][name]; recomputed += 1
source_checks = []
for entry, revision in [(result, '26664e81'), (base_result, '4f1139b0')]:
    for path, item in entry['native_scoring_sources'].items():
        rev = '79dba51b' if path.endswith('sglang_kv_streams.py') else revision
        raw = fixed(rev, path)
        assert sha(raw) == item['sha256'] and len(raw) == item['bytes']
        source_checks.append((revision, path))
for field in ('fixture', 'config'):
    path = Path(result[field]['path'])
    raw = fixed('26664e81', str(path.relative_to(Path.cwd())))
    assert sha(raw) == result[field]['sha256'] and len(raw) == result[field]['bytes']
source_fixture = result['sample_manifest']['source_fixture']
assert sha(Path(source_fixture['path']).read_bytes()) == source_fixture['sha256']
for name in ('tests', 'tests.manual', 'tests.manual.agent_opd'):
    module = types.ModuleType(name); module.__path__ = []; sys.modules[name] = module
for name, revision in [('sglang_mamba_snapshots', '26664e81'), ('sglang_mamba_runtime_metadata', '26664e81'), ('sglang_kv_streams', '79dba51b')]:
    module = types.ModuleType('tests.manual.agent_opd.' + name)
    module.__file__ = f'{revision}:tests/manual/agent_opd/{name}.py'
    sys.modules[module.__name__] = module; setattr(sys.modules['tests.manual.agent_opd'], name, module)
    exec(compile(fixed(revision, f'tests/manual/agent_opd/{name}.py'), module.__file__, 'exec'), module.__dict__)
witness = sys.modules['tests.manual.agent_opd.sglang_kv_streams']
receipt = result['kv_store_stream_source_preflight']; owner = witness.source_manifest()
assert set(owner['files']) == set(receipt['files']) and len(receipt['files']) == 35 and len(receipt['changed_files']) == 5
assert receipt['selected_fp32_precondition'] and receipt['cpu_metadata_precondition'] and receipt['diagnostic_only']
archive_checks = 0
for stage in ('source_preflight', 'runtime_metadata_source_preflight', 'kv_store_stream_source_preflight'):
    recorded = result[stage]
    assert recorded == preload[stage] == lines(run / stage / 'preflight.jsonl')[-1]
    for path, item in recorded['files'].items():
        for side in ('before', 'after'):
            raw = (run / stage / side / path).read_bytes()
            assert sha(raw) == item[f'{side}_sha256'] == recorded[f'observed_{side}_sha256'][path]
            archive_checks += 1
for path, item in owner['files'].items():
    assert all(receipt['files'][path][k] == v for k, v in item.items())
    before = (run / 'kv_store_stream_source_preflight/before' / path).read_bytes()
    after = (run / 'kv_store_stream_source_preflight/after' / path).read_bytes()
    witness._qualified_baseline(path, before, item)
    assert witness._rewrite(path, before) == after
for path in result['source_preflight']['files']:
    assert result['runtime_metadata_source_preflight']['files'][path]['before_sha256'] == result['source_preflight']['observed_after_sha256'][path]
    assert receipt['files'][path]['before_sha256'] == result['runtime_metadata_source_preflight']['observed_after_sha256'][path]
    assert receipt['observed_after_sha256'][path] == base_result['runtime_metadata_source_preflight']['observed_after_sha256'][path]
runtime_matches = 0
for path, item in result['runtime']['sglang_sources'].items():
    if path in receipt['files']:
        assert item['sha256'] == receipt['observed_after_sha256'][path]; runtime_matches += 1
assert result['runtime']['gpu_devices'] == ['NVIDIA H800, 81559 MiB, 570.124.06'] * 4
metadata = read(run / 'runtime_metadata.json')
initial_info = read(run / 'server_info.json')['get_server_info']
post_info = metadata['server_info']
initial = initial_info['internal_states'][0]['mamba_runtime_metadata']
post = post_info['internal_states'][0]['mamba_runtime_metadata']
assert len(initial_info['internal_states']) == len(post_info['internal_states']) == 1
assert metadata['dp_size'] == 1 and metadata['tp_size'] == 4 and metadata['pp_size'] == 1
assert initial['process_id'] == post['process_id'] == 391 and initial['rank'] == post['rank']
assert post['rank'] == {'dp_rank': None, 'tp_rank': 0, 'pp_rank': 0, 'attn_dp_rank': 0, 'attn_tp_rank': 0}
def decoded(rows):
    output = []
    for seq, event, fields in rows:
        assert len(fields) == len(dict(fields))
        output.append((seq, event, dict(fields)))
    return output
start, rows = decoded(initial['rows']), decoded(post['rows'])
allocator = [(s, f) for s, e, f in start if e == 'kv_allocator_created']
assert len(allocator) == 1 and allocator[0][1]['allocator_class'] == ['sglang.srt.mem_cache.allocator.token', 'TokenToKVPoolAllocator']
config_fields = ('page_size', 'attn_cp_size', 'dcp_size', 'enable_memory_saver', 'enable_hierarchical_cache', 'enable_unified_memory', 'enable_kv_cache_sharding', 'disable_cuda_graph')
config = {k: post_info[k] for k in config_fields}
assert config == dict(zip(config_fields, (1, 1, 1, False, False, False, False, True)))
assert {k: initial_info[k] for k in config_fields} == config
stream_rows = [(s, f) for s, e, f in rows if e == 'kv_store_stream']
terminal_rows = [(s, f) for s, e, f in rows if e == 'kv_store_terminal']
join = lambda f: (tuple(f['rids']), tuple(f['prefix_lens']), tuple(f['extend_lens']), f['k_cache_data_ptr'], f['v_cache_data_ptr'], f['writer_loc_data_ptr'])
stream_index, terminal_index, chunks, boundaries = (defaultdict(list) for _ in range(4))
for seq, fields in stream_rows:
    assert fields['store_kind'] == 'cpp_store_cache' and fields['native_stream_scalar_observed'] and fields['launch_enqueued']
    assert type(fields['native_actual_stream']) is int and fields['native_actual_stream'] >= 0
    assert fields['native_actual_stream'] == fields['torch_current_raw_stream']
    stream_index[join(fields)].append((seq, fields))
for seq, fields in terminal_rows:
    assert fields['store_kind'] == 'mha_set_kv_buffer_impl' and fields['native_stream_scalar_observed'] is False and fields['native_actual_stream'] is None
    assert len(fields['rids']) == len(fields['prefix_lens']) == len(fields['extend_lens']) == 1
    terminal_index[join(fields)].append((seq, fields))
    chunks[(fields['rids'][0], fields['prefix_lens'][0], fields['extend_lens'][0])].append((seq, fields))
for seq, event, fields in rows:
    if event == 'scheduler_track_boundary': boundaries[(fields['rid'], fields['prefix_len'], fields['extend_len'])].append((seq, fields))
assert len(stream_index) == len(terminal_index) == 2704 and set(stream_index) == set(terminal_index)
assert all(len(v) == 1 for v in list(stream_index.values()) + list(terminal_index.values()))
layers = sorted({f['layer_id'] for s, f in terminal_rows})
assert layers == list(range(3, 64, 4)) and len(chunks) == len(boundaries) == 169 and set(chunks) == set(boundaries)
assert set(q['native_request_id'] for q in requests) == set(key[0] for key in chunks)
for key, chunk in chunks.items():
    assert len(chunk) == 16 and sorted(f['layer_id'] for s, f in chunk) == layers
    assert len(boundaries[key]) == 1 and boundaries[key][0][1]['seq_end'] == key[1] + key[2]
    for seq, fields in chunk:
        cpp = stream_index[join(fields)][0][1]
        assert fields['pool_class'] == ['sglang.srt.mem_cache.memory_pool', 'MHATokenToKVPool']
        assert fields['pool_layer_id'] == fields['buffer_layer_idx'] == (fields['layer_id'] - 3) // 4
        assert fields['writer_loc'][2:] == [[key[2]], [1], 'cuda:0'] and fields['writer_loc'][1] == 'torch.int64'
        assert fields['writer_loc'][1:] == cpp['writer_loc'][1:]
        for name in ('k_cache', 'v_cache'):
            assert fields[name][1:] == ['torch.bfloat16', [1833689, 1, 256], [256, 256, 1], 'cuda:0']
            assert cpp[name][1:] == ['torch.bfloat16', [1833689, 256], [256, 1], 'cuda:0']
        assert cpp['row_bytes'] == cpp['v_row_bytes'] == 512
per_request = [{'request_id': q['request_id'], 'native_request_id': q['native_request_id'],
                'chunks': sum(key[0] == q['native_request_id'] for key in chunks),
                'terminal_rows': sum(len(v) for k, v in chunks.items() if k[0] == q['native_request_id'])} for q in requests]
terminal = read(proof / 'terminal-platform-containers.json')['jobs']['A']
core_terminal = read(proof / 'admission-A-r1.terminal.json')
initial_platform = read(proof / 'initial-platform-verification.json')['jobs']['A']
assert terminal['job'] == result['job'] == core_terminal['job'] == initial_platform['job']
assert terminal['uid'] == core_terminal['uid'] == initial_platform['uid'] and terminal['creator'] == 'i-fengyicheng'
assert terminal['status']['phase'] == core_terminal['status']['phase'] == 'Succeeded' and core_terminal['native_execution_succeeded']
assert len(terminal['replicas']) == 1 and terminal['replicas'][0]['phase'] == 'Succeeded'
replica = terminal['replicas'][0]; assert len(replica['containers']) == 1
container = replica['containers'][0]; terminated = container['state']['terminated']
assert container['restartCount'] == 0 and terminated['exitCode'] == 0 and terminated['reason'] == 'Completed'
assert container['imageID'] == replica['declared_containers'][0]['image'] == receipt['image'] == initial_platform['tasks']['probe']['containers'][0]['image']
assert result['status'] == 'measurements_completed' and result['native_measurements_completed'] and result['cleanup_completed']
assert all(sha(p.read_bytes()) == digest for p, digest in raw_before.items())
event_counts = lambda entries: dict(Counter(e for s, e, f in entries))
kind_counts = lambda entries: dict(Counter(f['store_kind'] for s, e, f in entries if e == 'kv_store_terminal'))
target = next(q for q in requests if q['request_id'] == 'warm_stream-r0-s2-full_input')
target_key = (target['native_request_id'], 90112, 8192)
target_layer = next((s, f) for s, f in chunks[target_key] if f['layer_id'] == 3)
output = {
    'task_id': 'profile-kv-stream-witness-native-A-20261111', 'job': result['job'], 'pair': 'A',
    'disposition': 'PASS bounded source/H800/CPP witness; formal HOLD; no KV numeric capture',
    'local_python': platform.python_version(), 'local_executable': sys.executable,
    'baseline_job': base_result['job'], 'identity_join_fields': list(identity_fields),
    'vectors': {'exact': 16, 'total_completion_values': sum(len(v['log_probs']) for v in current.values()),
                'shape_id_nonfinite_errors': 0, 'max_absolute_error': 0, 'max_defined_relative_error': 0,
                'zero_reference_positions': sum(v == 0 for s in previous.values() for v in s['log_probs']), 'rows': vector_rows},
    'workload': {'requests': len(requests), 'flushes': len(flushes), 'unsalted': True, 'comparison_records_unchanged': len(comparisons),
                 'recomputed_comparison_groups': recomputed, 'cold_exact': 4, 'warm_exact': 1, 'warm_different': 3},
    'source': {'caller_commit': '26664e81', 'helper_commit': '79dba51b', 'baseline_commit': '4f1139b0',
               'fixed_worker_identities': len(result['native_scoring_sources']), 'fixed_baseline_identities': len(base_result['native_scoring_sources']),
               'qualified_files': 35, 'changed_files': receipt['changed_files'], 'archive_hash_checks': archive_checks,
               'runtime_inventory_overlap_matches': runtime_matches, 'six_final_attention_sources_equal_baseline': True,
               'source_manifest_sha256': sha((run / 'kv_store_stream_source_preflight/source_manifest.json').read_bytes()),
               'native_diff_sha256': sha((run / 'kv_store_stream_source_preflight/kv_streams.diff').read_bytes()),
               'final_witness_hashes': {p: receipt['observed_after_sha256'][p] for p in receipt['changed_files']},
               'final_witness_runtime_paths': {p: receipt['source_paths'][p] for p in receipt['changed_files']},
               'tvm_ffi_runtime_root': '/opt/sglang/lib/python3.12/site-packages/tvm_ffi', 'tvm_ffi_version': receipt['tvm_ffi_distribution_version']},
    'runtime': {'python': result['runtime']['python'], 'executable': result['runtime']['executable'], 'sglang': result['runtime']['sglang'],
                'torch': result['runtime']['torch'], 'actual_gpu_devices': result['runtime']['gpu_devices'], 'image': container['imageID']},
    'terminal': {'uid': terminal['uid'], 'job_phase': terminal['status']['phase'], 'replica': replica['name'], 'replica_phase': replica['phase'],
                 'container_reason': terminated['reason'], 'container_exit_code': terminated['exitCode'], 'restart_count': container['restartCount'],
                 'job_finish': terminal['status']['finishTime'], 'original_corev1_403_retained': True, 'raw_owner_references_independently_read': False},
    'metadata': {'process_id': post['process_id'], 'rank': post['rank'], 'dp_size': 1, 'tp_size': 4, 'responding_tp_only': True,
                 'initial_rows': len(start), 'post_loop_rows': len(rows), 'initial_event_counts': event_counts(start), 'post_loop_event_counts': event_counts(rows),
                 'allocator_row': allocator[0][0], 'allocator_fields': allocator[0][1], 'qualified_runtime_config': config,
                 'initial_terminal_kinds': kind_counts(start), 'post_loop_terminal_kinds': kind_counts(rows),
                 'prefix_valid_triton': 0, 'prefix_valid_triton_fp8': 0, 'triton_stream_status': 'UNVERIFIED; not exercised',
                 'scoring_cpp_stream_rows': len(stream_rows), 'startup_cpp_stream_rows': sum(e == 'kv_store_stream' for s, e, f in start),
                 'native_scalar_observed_launch_enqueued_torch_equal': len(stream_rows), 'actual_stream_values': sorted({f['native_actual_stream'] for s, f in stream_rows}),
                 'missing_mismatched_no_launch_cpp_rows': 0, 'plain_terminal_own_scalar_observed': False,
                 'cpp_terminal_join_keys': ['rids', 'prefix_lens', 'extend_lens', 'k_cache_data_ptr', 'v_cache_data_ptr', 'writer_loc_data_ptr'],
                 'unique_cpp_terminal_joins': len(stream_index), 'absent_or_ambiguous_joins': 0, 'unique_rid_prefix_extend_chunks': len(chunks),
                 'unique_scheduler_boundary_joins': len(boundaries), 'actual_full_layer_ids': layers, 'layers_per_chunk': 16, 'response_rids_covered': 16,
                 'per_request': per_request, 'target': {'native_request_id': target['native_request_id'], 'prefix': 90112, 'extend': 8192,
                 'scheduler_seq': boundaries[target_key][0][0], 'layer3_terminal_seq': target_layer[0], 'layer3_cpp_seq': stream_index[join(target_layer[1])][0][0]}},
    'raw_files_checked_unchanged': len(raw_before), 'numerical_acceptance': None, 'performance_accepted': False, 'formal_status': 'HOLD',
    'limits': ['CPU descriptors are not physical K/V or FULL indices', 'No CUDA commit length values or kernel completion/PDL proof',
               'CPP equality is in-call launch-source only, not launch-before preflight', 'Triton stream remains unverified if a later required path selects it',
               'Only responding DP1/TP0 process; no all-TP coherence', 'No explicit allocator-outer/inner-pool runtime object link',
               'No compiled-binary hash or selected CAPI/fallback attestation', 'Warm correctness remains failed; no cache fix or race exclusion',
               'No original56/two-repeat/full-weight/historical-cause/performance acceptance', 'No KV numerical capture or new formal authorization']
}
print(json.dumps(output, indent=2, allow_nan=False))
PY
```

Observed execution: the exact fenced command above returned0; all assertions PASS. It recomputed40 comparison groups,114 source archive hashes across all three stages,35 fixed-helper witness derivations and2,704 explicit unique CPP/terminal joins. All221 raw files in the new run and baseline were checked unchanged before exit. The derived JSON records those actual counts; no pytest/GPU test is claimed.

Final artifact verification: replayed the report's command, compared its parsed stdout with the retained derived JSON, and checked both owned files' whitespace/newlines. Expected and actual: **PASS**,2.286 seconds. Both files remain untracked/uncommitted. Exact commands:

```bash
python3 -B - <<'PY'
import json,re,subprocess,time
from pathlib import Path
root=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
report=root/'test_report_2026-11-11_kv_stream_witness_native_A_results.md'
evidence=root/'evidence/teacher-scoring-kv-stream-witness-probe-20261111/native-verification-A.json'
command=re.search(r'```bash\n(.*?)\n```',report.read_text(),re.S).group(1)
start=time.perf_counter()
result=subprocess.run(['zsh','-c',command],capture_output=True,text=True,timeout=65)
assert result.returncode==0,(result.returncode,result.stderr)
assert json.loads(result.stdout)==json.loads(evidence.read_text())
for path in (report,evidence):
 assert all(line.rstrip()==line for line in path.read_text().splitlines()),path
 assert path.read_bytes().endswith(b'\n'),path
print(json.dumps({'verification_replay':'PASS','derived_json_exactly_matches_stdout':'PASS','owned_whitespace':'PASS','elapsed_seconds':round(time.perf_counter()-start,3),'report':str(report),'evidence':str(evidence)},indent=2))
PY
git status --short -- task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_kv_stream_witness_native_A_results.md task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-stream-witness-probe-20261111/native-verification-A.json
```

The initial memory-scope command was `timeout 60s systemd-run --scope -p MemoryMax=30G python3 -B - <<'PY' ... PY` for the same exact native A JSON inventory; it failed before the script ran with the authentication error quoted above. The successful commands thereafter used the timeout/RLIMIT pattern in the reproducible command, inspecting vector equality first, then fixed-source hash/rewrites and unique metadata keys. No retry or fallback changed runtime behavior.

## Scoped progress checkpoint

### 1. Planned completion

PASS3 / BLOCKED0 / TODO1: vector/workload reproduction PASS; source/H800/process-local witness PASS; terminal/report evidence PASS; primary review/acceptance TODO. Parent tickets01/02/03 remain recorded PASS,04/05 BLOCKED,06 TODO. No checkbox or blocking edge is edited.

### 2. Drift detection

Window: this assignment through retained-vector prerequisite and witness verification. Frontier: independent A report/derived evidence, then primary acceptance; numerical stage is separate.

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 tooling polish | CLEAR | Only scoped offline checks needed for assigned acceptance; no new harness/tool feature. |
| D2 retry loop | CLEAR | One systemd permission failure; process memory limit applied without auth/config changes or runtime retry. |
| D3 side quest | CLEAR | All reads/checks qualify the assigned native A evidence. |
| D4 stalled parallel work | NO DATA | Parent owns independent B and coordination; no further delegation authorized. |
| D5 gold-plating | CLEAR | Exactly two new owned artifacts, no source/runtime edits. |
| D6 analysis sprawl | CLEAR | Investigation is the requested deliverable, with decisive16-vector/2,704-join results. |
| D7 off-route | CLEAR | Local-only verification, fixed commits, raw preserved, formal HOLD and no commit. |

Document check: S1–S4/S6 have no new defect in this bounded assignment. S5: shared current descriptions still call A Running/native evidence pending (`progress.md:193,207`, tickets04/05 current status), while the supplied terminal and this new evidence are newer. Primary owns their update after review; this is not authority to edit them or to widen acceptance. Attribution: no execution drift.

### 3. Route correction

Branch B, stale current state only: primary updates the existing current sections after accepting this independent report, preserving historical Running/403/source-preparation limits and all formal checkboxes. Stop behavior: none. Next: primary review of these two artifacts; keep numeric capture/formal HOLD unless separately qualified/authorized. Independent B work continues without an A200 gate.

### 4. Three important points

1. All16 baseline vectors reproduce exactly while warm failures remain unchanged.
2. Actual TokenToKVPoolAllocator/config and2,704 unique CPP–layer/RID/row joins qualify only responding DP1/TP0 launch-source metadata.
3. Raw403 and startup warnings remain historical; terminal execution is verified, not KV numeric/coherence or formal acceptance. Primary review and the separate numerical stage remain unfinished.
