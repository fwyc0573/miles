## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Add B-only retained native verification: exact first4/repetition0 equivalence, reproduced warm drift, source qualification and identity-only runtime metadata coverage. A/unified verification remains a follow-up. |
| 2026-11-11 | Pin scoring caller/module identity replay to immutable4f1139b0 Git blobs and primary native-code receipt; reference independent primary-retained B container/image/resource evidence without changing numerical or metadata contracts. |

# Runtime metadata native results — B only

TaskID: `profile-runtime-metadata-native-verification-20261111`.

**B verification PASS within the requested scope; warm correctness remains FAIL and formal04/05 remain BLOCKED.** All16 actual completion vectors exactly match original selected-FP32 B repetition0 first4. The minimized instrumented run reproduces the original sample2/3 warm drift; it is not a numerical correction. A was not inspected, waited for or polled. No GPU, platform, authentication or SSH operation was performed. Only this new report and the new [B evidence JSON](evidence/teacher-scoring-runtime-metadata-probe-20261111/native-verification-B.json) are owned; code/config/science/old data/README remain unchanged.

## Native execution, source and input integrity

Run root: `task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1`.

- Retained terminal receipt: `evidence/teacher-scoring-runtime-metadata-probe-20261111/admission-B-r1.terminal.json`, job `exp-1111-073825-734134`, creator `i-fengyicheng`, **Succeeded**, finish time `2026-11-10T23:42:03Z`. This is a read of primary-retained evidence, not a new platform query.
- Independent primary reference: `evidence/teacher-scoring-runtime-metadata-probe-20261111/terminal-platform-containers.json`, observed `2026-11-10T23:56:25.694462+00:00`, records B job/replica Succeeded, container **Completed/exit0/restart0**, `imageID` equal to the pinned165ff0be digest and GPU limit`"4"`. Its source-filestore annotation is `100.96.128.195:/data/ycfeng:/data/ycfeng`, matching the local submission receipt. The selected replicaSpec contains no direct NFS source-volume entries; this does **not** establish an unmounted workspace, the mount implementation or all-TP coverage. Only the existing local receipt was read here; no platform operation was performed and A's business report remains independently owned.
- `preload.json` contains four actual `nvidia-smi` rows: **NVIDIA H800,81559 MiB,driver570.124.06**. `result.json` records `measurements_completed`, `native_measurements_completed=true`, `cleanup_completed=true`, runtime metadata `collected`. Preload's initial `status=failed` is its pre-execution default, not the terminal outcome. Native server was alive before ordinary cleanup; retained shutdown return code is `-9`.
- Worker Python `/opt/sglang/bin/python3`, **3.12.16**; SGLang **0.5.24.dev80+g056f871**; Torch **2.14.1+cu130**. Local verifier `/usr/bin/python3`, **3.10.6**, Linux, standard library plus existing pure probe/source functions; no conda activation or pytest run.
- Retained image input: `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`. Teacher source `/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-35B-A3B/model`. Model `config.json` SHA256 `5e4d7f74fec2f360eb9cfbfcd6ec0c4c76e684d3a11caaed259d9fd9bfbc7944`; index SHA256 `d8d0b7ca4e61ae107e3e87a3ff21136b3ac7c789e64bb24267227ca804e04205`. Image input is not an independently inspected container digest; manifest hashes are not a whole-weight checksum.
- TP4/DP1/PP1, BF16 engine, context131072, concurrency1, chunk8192, deterministic inference, FA3 attention/Triton linear prefill, CUDA graphs disabled, `SGLANG_FORCE_COARSE_WAR_BARRIER=null`. Existing native flags match the original B FP32 probe except its deployment address. No cache, dtype, tolerance, budget or payload adjustment occurred in this verification.

Source acceptance used actual retained before/after bytes, not just receipt booleans:

| Check | Expected | Actual / verdict |
| --- | --- | --- |
| `source_preflight/{before,after,source_manifest.json,preflight.jsonl}` | Pinned selected-FP32 source/observed hashes agree | **6/6 PASS**; only chunk.py and gdn_triton.py changed |
| `runtime_metadata_source_preflight/{before,after,source_manifest.json,preflight.jsonl}` | Qualified post-FP32 baseline; exact diagnostic `_rewrite`; matching hashes | **16/16 PASS**:15 existing files,8 inserts and1 new recorder |
| Two source receipts in preload/result/preflight | Separate, identical retained receipts | **PASS** |
| Overlap with actual `runtime.sglang_sources` | Metadata after hashes agree | **4/4 PASS**:schedule_batch/internal_state/unified_radix_cache/model_runner |
| Actual `native_scoring_sources` | Six caller/module hashes and byte counts match immutable Git blobs and primary receipt | **6/6 PASS** at `4f1139b09f6d040cfdc3fe9fffacb9833e7f7aff` |

Scoring-source replay reference: `evidence/teacher-scoring-runtime-metadata-probe-20261111/native-code-commit.json`, SHA256 `2e4eff2caab44d2b6e1505cc0e50be039f7210acef008e9d8d1bbce365819cc5`. Each B native-result relative path selects its Git blob at the pinned commit, so a later working-tree probe edit does not invalidate the historical measurement. Current `_comparison`/receiver/source-helper contracts and all native source-preflight inputs remain unchanged. The independent platform-reference SHA256 is `63f62b487f44b34a0bf9900b5816c0b756f75cc2dd368dd4d600ee1c776ea4ee`; both receipt paths/hashes are retained in the B evidence JSON.

Selected-FP32 `chunk.py` after hash is `b2c1cd76ab3558b893e082f07a8c587520e624e9988d19c0c1afa4f32a72e43c`; `gdn_triton.py` is `7060585d86347561a2caf36492163b584152e32efddea17b5b4cc8c33c5774bf`. Diagnostic GDN backend after hash is `7296198be4586f2c703e719bc40ac657d2f6a0682d7851f58669b6ba33487025`; hybrid backend is `fa1331457e307f5d172fd62730be0dd026a36a10a10319b7ec630e1d097c3d36`. This establishes retained deployment/source identity, not independently loaded source identity on all four TP ranks.

Original fixture remains `evidence/teacher-scoring-probe-20261111/retained-cases.json`, SHA256 `c45424e8106c2beb7500acacb68aa0939da0088c926af8012dd9fbd780f0ffc9`. First4 selection preserves original UID, index, tokens and turn ordinal:

| Position | Original UID suffix (full UIDs in evidence JSON) | Index | Input tokens | Response tokens | Assistant ordinal |
| --- | --- | --- | --- | --- | --- |
| 0 | `:5:123` | 1693 | 97365 | 734 | 57 |
| 1 | `:5:125` | 1694 | 98312 | 246 | 58 |
| 2 | `:5:127` | 1695 | 98942 | 431 | 59 |
| 3 | `:5:129` | 1696 | 99074 | 290 | 60 |

Actual `requests.jsonl`: **16/16 scored,16 HTTP200,16 unique native response IDs**; actual `cache.jsonl`: **10/10 flushed**. All16 completion files preserve `(pair,phase,mode,source_uid,sample_index,repetition)`, actual `native_request_id=meta_info.id`, exact original response-tail token IDs and finite, complete vectors. **6804 completion log probabilities** checked. Returned full-input/requested logprob counts and completion counts match for all requests. These observations supplement, not replace, the separately completed332 CPU checks and both preparation-phase No findings reviews.

## Exact numerical results

Reference: `evidence/teacher-scoring-runtime-metadata-probe-20261111/original-fp32-first4-reference.json`, SHA256 `2bdcecc77744977e30c3d5ba9cf21a04f4840256e01b6e724ab1bc5c3f4ac903`. All16 B reference score SHA256s and the original B `comparisons.jsonl` SHA256 were checked. The reference supplies pair identity for older receipts that did not yet store it explicitly. Vectors are joined by **pair/phase/mode/source_uid/sample_index/repetition**, not file order, request chronology or metadata counts. The existing probe contract is named `_comparison(reference,candidate)` in current code.

**Original versus instrumented:** all16 vectors have `token_ids_match=true`, `finite_log_probs=true`, `values_exact=true`, **max absolute error0.0 and max defined relative error0.0**. All eight retained comparison groups also exactly match the supplied original B first4/repetition0 groups.

Relative error is `abs(reference−candidate)/abs(reference)` only where reference is nonzero. It remains **undefined at zero reference, even for exact0 versus0**; zero positions are never reported as relative error0. The maximum below excludes those positions.

| Phase | Position | Full-input zero-reference count | Response-only zero-reference count | Each vector max abs / max defined rel |
| --- | --- | --- | --- | --- |
| cold | 0 | 3 | 3 | 0.0 / 0.0 |
| cold | 1 | 5 | 5 | 0.0 / 0.0 |
| cold | 2 | 4 | 4 | 0.0 / 0.0 |
| cold | 3 | 4 | 4 | 0.0 / 0.0 |
| warm_stream | 0 | 3 | 3 | 0.0 / 0.0 |
| warm_stream | 1 | 5 | 5 | 0.0 / 0.0 |
| warm_stream | 2 | 4 | 3 | 0.0 / 0.0 |
| warm_stream | 3 | 5 | 4 | 0.0 / 0.0 |

**Own full-input versus response-only:** cold4/4 exact; warm1/4 exact. Reference is own full-input vector:

| Phase / position | Exact | Max absolute error | Max defined relative error | Undefined count |
| --- | --- | --- | --- | --- |
| cold0/1/2/3 | yes | 0.0 | 0.0 | 3/5/4/4 |
| warm0 | yes | 0.0 | 0.0 | 3 |
| warm1 | no | 2.9801958589814603e-06 | 0.3055551434731875 | 5 |
| warm2 | no | 0.33083581924438477 | 10.83576074484674 | 4 |
| warm3 | no | 0.24397611618041992 | 2.1428543402212714 | 5 |

**Own independently flushed cold versus warm:** the two cold modes are exact, so either cold mode produces the same below comparison. All four cold-reference contracts per position were recomputed and checked against retained groups. Warm-full is not an oracle.

| Position | Warm candidate | Exact | Max absolute error | Max defined relative error | Undefined count |
| --- | --- | --- | --- | --- | --- |
| 0 | full_input | yes | 0.0 | 0.0 | 3 |
| 0 | response_only | yes | 0.0 | 0.0 | 3 |
| 1 | full_input | no | 4.529893885774072e-06 | 0.31249958276708867 | 5 |
| 1 | response_only | no | 3.4569602576084435e-06 | 0.1071427598289923 | 5 |
| 2 | full_input | no | 0.43444275856018066 | 12.818066557496891 | 4 |
| 2 | response_only | no | 0.5321998596191406 | 12.296145876202624 | 4 |
| 3 | full_input | no | 0.4388699531555176 | 1.4485754510908142 | 4 |
| 3 | response_only | no | 0.3178117275238037 | 2.99999928474422 | 4 |

Thus **sample2/3 warm drift is reproduced, including warm-full deviations from both cold modes**. B's minimized instrumented run is numerically equivalent to the16 specified original vectors. This does not establish equivalence for the original56 requests, second repetition or dropped1024-hit groups, numerical correctness, a causal correction or performance acceptance.

## Runtime metadata: identity, coverage and actual paths

Actual `runtime_metadata.json` is **32874422 bytes**, SHA256 `ef17ed6e6e4a387ebe46e8dd784d94b92a159e2efc14c914e8601da3b0a695b9`. The existing receiver validates DP1/TP4/PP1 and one respondent. Schema `mamba-runtime-metadata-v1`, process352, actual raw rank `{dp_rank:null,tp_rank:0,pp_rank:0,attn_dp_rank:0,attn_tp_rank:0}`. Raw DP None is legal absent-controller DP1 and was neither rewritten nor used to assert an extra respondent.

**16333 typed rows, sequence173–16505,15 observed event kinds;52912 tensor-metadata observations checked.** The existing initial `server_info.json` readback already drained172 startup rows, sequence1–172; the recorder clears rows without resetting its sequence. Startup rows are separate from the final16333-row receipt, not additional scoring requests. Every observed final row has unique named fields; tensor IDs/dtype/shape/stride/device tuples are structurally valid. **11206 RID-bearing rows join to all16 actual request/completion receipts by `(B,native_request_id)`; no explicit RID is unmatched.** The remaining5127 rows have no direct RID. Sequence is checked for schema validity, never used for identity. CPU plan rows index the actual batch RID list, not device slot contents.

| Event | Rows | Direct/batch RID rows | Distinct requests | Coverage |
| --- | --- | --- | --- | --- |
| scheduler_track_boundary | 169 | 169 | 16 | Direct RID |
| translated_track_metadata | 169 | 169 | 16 | Batch RIDs |
| prefill_track_plan | 165 | 165 | 16 | Batch RIDs + CPU row membership |
| gdn_snapshot_allocation | 5070 | 5070 | 16 | Batch RIDs |
| gdn_extend_dispatch | 5070 | 0 | 0 direct |390 trace-unique buffer associations;4680 null-buffer rows unassociated |
| snapshot_store_enqueued | 4950 | 4950 | 16 | Batch RIDs |
| mamba_clear_enqueued | 13 | 13 | 13 | Batch RIDs |
| mamba_cow_enqueued | 3 | 3 | 3 | Batch RIDs |
| cow_match_selected | 3 | 3 | 3 | Direct RID |
| cow_match_skipped | 13 | 0 | 0 | Aggregate; no node-to-request inference |
| mamba_donor_prepared | 169 | 169 | 16 | Direct RID |
| checkpoint_insert_begin | 165 | 165 | 16 | Direct RID |
| checkpoint_insert_returned | 165 | 165 | 16 | Direct RID |
| canonical_kv_rebind_enqueued | 165 | 165 | 16 | Direct RID |
| kv_allocator_release_returned | 44 | 0 | 0 | Aggregate only |

`duplicate_kv_release_queued` has **0 observed rows**, not per-request acceptance or proof that all possible release paths were covered. Per-request row counts and exact native RIDs are retained in `native-verification-B.json.request_metadata`, joined to the original identities from requests/completions. For warm response-only sample1/2/3, direct RID row counts are102/69/69; scheduler rows2/1/1, plan rows1/1/1, donor rows2/1/1, canonical rebind rows1/1/1, allocation rows60/30/30 and store rows30/30/30. These are multiple receipts for the same request, not additional requests.

Actual conditional paths and dtypes:

- Allocation: `TritonGDNKernel`, snapshot capability true in5070 rows.390 rows allocated a selected buffer;4560 tracked rows had empty h source and no buffer;120 rows were untracked and did not allocate.390 nonnull allocation buffer IDs each appear once in this retained trace.
- Store:4560 `final_state`,390 `h_track_buf`; no observed `per_chunk_h` or recompute branch. Plans:152 final-row plans and13 unaligned/h-row plans; no nonempty recompute rows. Absence is bounded to this run.
- Actual temporal state metadata is **torch.float32** for allocation5070/dispatch5070/store4950 observations. Actual selected buffer metadata is **torch.float32** in390 allocation/dispatch/store observations, shape`[1,8,128,128]`, stride`[131072,16384,128,1]`, device label`cuda:0`. This label describes the responding process's metadata, not independent all-TP validation. Index metadata is typed int32/int64; store destination slots are int64 in4950 observations. No source was called FP32 solely because configuration requested it.
- Exactly390 dispatcher rows can associate with a unique allocation by identical nonnull object ID, tensor metadata, layer and kernel **within this process/trace**.4680 null-buffer dispatcher rows remain unassociated. No chronological, shared-node or count association is substituted. Object addresses and shared node IDs are **not persistent identities**; potential address reuse in other fields/runs is not excluded.

These are CPU host enqueue, allocator-return, branch and dtype/shape receipts. **Physical slot values, device-store completion, donor numeric contents, all-TP coherence, numerical causality and race exclusion remain UNMEASURED/UNVERIFIED.** Neither full RID coverage nor reproduced drift supplies the full RCA; primary/analyzer owns interpretation.

## Commands and reproducible local verification

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Inspections were read-only Python heredocs with `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B` and60-second tool limits, scoped to the exact B directory and supplied B reference. No bytecode/cache/raw writes, GPU command, network request or new native run was made.

The historical worker command is retained verbatim in `evidence/teacher-scoring-runtime-metadata-probe-20261111/admission-B-r1.json.worker_command`; it was **not rerun** here:

```bash
bash -lc 'export PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image
export LD_LIBRARY_PATH=/usr/local/cuda-13.0/compat"${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec timeout --signal=TERM --kill-after=90s 3600s /opt/sglang/bin/python3 -u -B -m tests.manual.agent_opd.probe_teacher_scoring --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_runtime_metadata_probe_config.json --pair B --samples /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_runtime_metadata_first4_manifest.json --output-dir /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-runtime-metadata-probe-20261111/native/B/admission-B-r1 --repeats 1 --request-timeout 3600'
```

Exact local final verification command (executes only the read-only Python block below from this maintained report):

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
p = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_runtime_metadata_native_results.md')
code = p.read_text().split('<!-- verification-python -->\n```python\n', 1)[1].split('\n```', 1)[0]
exec(compile(code, str(p), 'exec'))
PY
```

<!-- verification-python -->
```python
from pathlib import Path
from collections import Counter, defaultdict
import hashlib, json, math, platform, subprocess
from tests.manual.agent_opd.probe_teacher_scoring import _comparison, _runtime_metadata_states
from tests.manual.agent_opd import sglang_mamba_runtime_metadata as metadata
from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots

base = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-runtime-metadata-probe-20261111')
e = json.loads((base / 'native-verification-B.json').read_text())
run = Path(e['run_path'])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
lines = lambda p: [json.loads(x) for x in p.read_text().splitlines()]
assert platform.python_version() == e['environment']['verification_python_version']
for relative, expected in e['raw_run_sha256'].items():
    assert sha(run / relative) == expected, relative
for prefix in ('reference', 'terminal_receipt'):
    assert sha(Path(e[prefix + '_path'])) == e[prefix + '_sha256']
terminal = load(Path(e['terminal_receipt_path']))
result, preload = load(run / 'result.json'), load(run / 'preload.json')
assert terminal['job'] == result['job'] == e['job']
assert terminal['status']['phase'] == 'Succeeded'
assert result['status'] == 'measurements_completed' and result['native_measurements_completed'] and result['cleanup_completed']
assert preload['runtime'] == result['runtime']
assert result['runtime']['gpu_devices'] == e['environment']['gpu_devices']
assert len(result['runtime']['gpu_devices']) == 4
assert len(result['source_preflight']['files']) == 6 and len(result['runtime_metadata_source_preflight']['files']) == 16
assert len(set(result['runtime_metadata_source_preflight']['files']) & set(result['runtime']['sglang_sources'])) == 4
for scope, expected in (('source_preflight', snapshots.source_manifest()), ('runtime_metadata_source_preflight', metadata.source_manifest())):
    receipt = result[scope]
    assert receipt == preload[scope] == lines(run / scope / 'preflight.jsonl')[0]
    assert receipt['files'] == load(run / scope / 'source_manifest.json')['files']
    assert receipt['image'] == expected['image'] == e['environment']['image']
    assert receipt['distribution_version'] == expected['distribution_version'] == result['runtime']['sglang']
    for name, identity in receipt['files'].items():
        before, after = run / scope / 'before' / name, run / scope / 'after' / name
        assert sha(before) == identity['before_sha256'] == receipt['observed_before_sha256'][name]
        assert sha(after) == identity['after_sha256'] == receipt['observed_after_sha256'][name]
        if name in expected['files']:
            assert identity['before_sha256'] == expected['files'][name]['before_sha256']
        if scope == 'source_preflight':
            assert identity['after_sha256'] == expected['files'][name]['after_sha256']
        else:
            candidate = metadata._RECORDER_SOURCE.encode() if identity.get('created') else metadata._rewrite(name, before.read_bytes())
            assert after.read_bytes() == candidate
            if name in result['runtime']['sglang_sources']:
                assert result['runtime']['sglang_sources'][name]['sha256'] == identity['after_sha256']
source_reference = e['source_verification']
code_receipt_path = Path(source_reference['native_code_receipt_path'])
assert sha(code_receipt_path) == source_reference['native_code_receipt_sha256']
code_receipt = load(code_receipt_path)
commit = source_reference['native_code_commit']
assert code_receipt['native_code_commit'] == commit
code_pair = next(p for p in code_receipt['pairs'] if p['pair'] == 'B')
assert code_pair['job'] == result['job']
code_files = {f['path']: f for f in code_pair['files']}
assert len(code_files) == 6 and set(code_files) == set(result['native_scoring_sources'])
for name, identity in result['native_scoring_sources'].items():
    blob = subprocess.check_output(['git', 'show', f'{commit}:{name}'], timeout=30)
    assert hashlib.sha256(blob).hexdigest() == identity['sha256'] == code_files[name]['sha256']
    assert len(blob) == identity['bytes'] == code_files[name]['bytes']
platform_reference = e['terminal_platform_reference']
platform_path = Path(platform_reference['path'])
assert sha(platform_path) == platform_reference['sha256']
platform_receipt = load(platform_path)
platform_pair = next(p for p in platform_receipt['jobs'] if p['pair'] == 'B')
assert platform_pair['job'] == result['job']
container = next(c for c in platform_pair['replica_status']['containerStatuses'] if c['name'] == 'probe')
assert container['state']['terminated']['reason'] == platform_reference['container_reason'] == 'Completed'
assert container['state']['terminated']['exitCode'] == platform_reference['container_exit_code'] == 0
assert container['restartCount'] == platform_reference['restart_count'] == 0
assert container['imageID'] == platform_reference['imageID'] == e['environment']['image']
resources = next(c for c in platform_pair['containers'] if c['name'] == 'probe')['resources']
assert resources['limits']['nvidia.com/gpu'] == platform_reference['gpu_limits'] == '4'
assert platform_pair['source_annotation'] == platform_reference['source_annotation']
assert platform_pair['source_volumes'] == platform_reference['source_volumes'] == []
for name in ('fixture', 'config'):
    assert sha(Path(result[name]['path'])) == result[name]['sha256']
assert sha(Path(e['fixture']['source_path'])) == e['fixture']['sha256']
fixture = load(Path(e['fixture']['source_path']))['samples'][:4]
requests = lines(run / 'requests.jsonl')
assert len(requests) == 16 and len({r['native_request_id'] for r in requests}) == 16
request_by_id = {r['request_id']: r for r in requests}
request_by_rid = {(r['pair'], r['native_request_id']): r for r in requests}
vectors = {}
identity_key = lambda x, pair: (x.get('pair', pair), x['phase'], x['mode'], x['source_uid'], x['sample_index'], x['repetition'])
for r in requests:
    sample = fixture[r['sample_position']]
    vector = load(Path(r['completion_scores']))
    assert r['pair'] == 'B' and r['repetition'] == 0 and r['status'] == 'scored' and r['http_status'] == 200
    assert r['source_uid'] == sample['source_uid'] and r['sample_index'] == sample['sample_index']
    assert vector['native_request_id'] == r['native_request_id'] == r['meta_info']['id']
    assert isinstance(r['native_request_id'], str) and r['native_request_id']
    assert identity_key(vector, 'B') == identity_key(r, 'B')
    assert vector['token_ids'] == sample['tokens'][-sample['response_length']:]
    assert len(vector['log_probs']) == r['returned_completion_count'] == sample['response_length']
    assert all(math.isfinite(v) for v in vector['log_probs'])
    assert r['input_token_logprobs_count'] == r['expected_input_token_logprobs_count']
    vectors[identity_key(vector, 'B')] = vector
assert sum(len(v['log_probs']) for v in vectors.values()) == 6804
cache = lines(run / 'cache.jsonl')
assert len(cache) == 10 and all(r['status'] == 'flushed' for r in cache)
reference = next(r for r in load(Path(e['reference_path']))['reference'] if r['pair'] == 'B')
assert sha(Path(reference['comparisons_path'])) == reference['comparisons_sha256']
original_result = load(Path(reference['comparisons_path']).parent / 'result.json')
def without_deployment_address(argv):
    i = argv.index('--dist-init-addr')
    return argv[:i] + argv[i + 2:]
assert without_deployment_address(result['argv']) == without_deployment_address(original_result['argv'])
assert result['runtime']['model_manifest_identity'] == original_result['runtime']['model_manifest_identity']
undefined = dict(e['completion_equivalence']['per_vector'])
for entry in reference['score_files']:
    path = Path(entry['path'])
    assert sha(path) == entry['sha256']
    old = load(path)
    candidate = vectors[identity_key(entry, reference['pair'])]
    assert identity_key(old, reference['pair']) == identity_key(entry, reference['pair'])
    observed = _comparison(old, candidate)
    expected = {**e['completion_equivalence']['common_vector_comparison'], 'relative_error_undefined_count': undefined[candidate['request_id']]}
    assert observed == expected, candidate['request_id']
groups = lines(run / 'comparisons.jsonl')
assert len(groups) == 8 and groups == reference['comparisons']
summary = lambda c: [c[k] for k in ('values_exact', 'max_absolute_error', 'max_relative_error', 'relative_error_undefined_count')]
own_modes = {(x[0], x[1]): x[2:] for x in e['own_comparisons']['full_vs_response_only']}
own_cold = {(x[0], x[1]): x[2:] for x in e['own_comparisons']['cold_full_vs_warm']}
for g in groups:
    full = load(run / 'completion_scores' / (g['full_request_id'] + '.json'))
    response = load(run / 'completion_scores' / (g['response_request_id'] + '.json'))
    assert _comparison(full, response) == g['full_vs_response_only']
    assert summary(g['full_vs_response_only']) == own_modes[g['phase'], g['sample_position']]
    if g['cold_reference']:
        for cold_mode, cold_name in (('full', 'full_request_id'), ('response_only', 'response_request_id')):
            cold = load(run / 'completion_scores' / (g['cold_reference'][cold_name] + '.json'))
            for warm_name, warm in (('full', full), ('response_only', response)):
                c = _comparison(cold, warm)
                assert c == g['cold_reference'][f'cold_{cold_mode}_vs_warm_{warm_name}']
                assert summary(c) == own_cold[g['sample_position'], 'full_input' if warm_name == 'full' else 'response_only']
runtime = load(run / 'runtime_metadata.json')
observations = _runtime_metadata_states(runtime['server_info'])
assert runtime['status'] == 'collected' and len(observations) == 1
raw = runtime['server_info']['internal_states'][0]['mamba_runtime_metadata']
assert raw['rank'] == e['runtime_metadata']['rank'] and raw['process_id'] == 352
rows = raw['rows']
assert len(rows) == 16333 and rows[0][0] == 173 and rows[-1][0] == 16505
initial = load(run / 'server_info.json')['get_server_info']['internal_states'][0]['mamba_runtime_metadata']['rows']
assert len(initial) == 172 and initial[0][0] == 1 and initial[-1][0] == 172
counts, direct, per_request, event_rids = Counter(), Counter(), defaultdict(Counter), defaultdict(set)
allocations, dispatches, dtype_counts, stores, tensors = defaultdict(list), [], defaultdict(Counter), Counter(), 0
for seq, event, fields in rows:
    assert len(fields) == len(dict(fields))
    f = dict(fields)
    counts[event] += 1
    rids = [f['rid']] if 'rid' in f else (f.get('rids') or [])
    if rids:
        direct[event] += 1
    for rid in rids:
        assert ('B', rid) in request_by_rid
        per_request['B', rid][event] += 1
        event_rids[event].add(('B', rid))
    for field, v in f.items():
        if isinstance(v, list) and len(v) == 5 and isinstance(v[1], str) and v[1].startswith('torch.'):
            assert type(v[0]) is int and v[0] > 0
            assert isinstance(v[2], list) and isinstance(v[3], list) and len(v[2]) == len(v[3])
            assert all(type(n) is int and n >= 0 for n in v[2] + v[3]) and isinstance(v[4], str)
            tensors += 1
            dtype_counts[event, field][v[1]] += 1
    if event == 'gdn_snapshot_allocation' and f['track_state'] is not None:
        allocations[f['track_state'][0]].append(f)
    if event == 'gdn_extend_dispatch':
        dispatches.append(f)
    if event == 'snapshot_store_enqueued':
        stores[f['source']] += 1
for event, n, rid_n, requests_n, association in e['runtime_metadata']['events']:
    assert (counts[event], direct[event], len(event_rids[event])) == (n, rid_n, requests_n), event
assert len(counts) == 15 and sum(direct.values()) == 11206 and len(per_request) == 16 and tensors == 52912
for request_id, rid, total, schedule, plan, donor, rebind, allocation, store in e['request_metadata']:
    assert request_by_id[request_id]['native_request_id'] == rid
    c = per_request['B', rid]
    assert [sum(c.values()), c['scheduler_track_boundary'], c['prefill_track_plan'], c['mamba_donor_prepared'], c['canonical_kv_rebind_enqueued'], c['gdn_snapshot_allocation'], c['snapshot_store_enqueued']] == [total, schedule, plan, donor, rebind, allocation, store]
assert len(allocations) == 390 and all(len(v) == 1 for v in allocations.values())
matched, null = 0, 0
for f in dispatches:
    buffer = f['track_state']
    if buffer is None:
        null += 1
        continue
    candidates = allocations[buffer[0]]
    assert len(candidates) == 1
    a = candidates[0]
    assert (a['track_state'], a['layer_id'], a['kernel']) == (buffer, f['layer_id'], f['kernel'])
    matched += 1
assert (matched, null) == (390, 4680)
assert stores == Counter(final_state=4560, h_track_buf=390)
assert dtype_counts['gdn_snapshot_allocation', 'temporal'] == Counter({'torch.float32': 5070})
assert dtype_counts['gdn_snapshot_allocation', 'track_state'] == Counter({'torch.float32': 390})
assert dtype_counts['gdn_extend_dispatch', 'temporal'] == Counter({'torch.float32': 5070})
assert dtype_counts['gdn_extend_dispatch', 'track_state'] == Counter({'torch.float32': 390})
assert dtype_counts['snapshot_store_enqueued', 'temporal'] == Counter({'torch.float32': 4950})
assert dtype_counts['snapshot_store_enqueued', 'track_state'] == Counter({'torch.float32': 390})
for relative, expected in e['raw_run_sha256'].items():
    assert sha(run / relative) == expected
print(json.dumps({'status': 'PASS', 'pair': 'B', 'vectors_exact': 16, 'comparison_groups_exact': 8, 'requests': 16, 'flushes': 10, 'metadata_rows': 16333, 'rid_covered_requests': 16, 'tensor_metadata_observations': 52912, 'formal_hold_lifted': False}, sort_keys=True))
```

Expected: every identity/hash/integrity/numerical/schema/RID assertion passes, no original file changes; vector exact16,comparison groups exact8,requests16,flushes10,metadata rows16333,RID-covered requests16. **Observed: PASS** with exact output below; final consistency includes raw SHA256 recheck. No successful exit alone is used to claim numerical correctness.

```json
{"comparison_groups_exact": 8, "flushes": 10, "formal_hold_lifted": false, "metadata_rows": 16333, "pair": "B", "requests": 16, "rid_covered_requests": 16, "status": "PASS", "tensor_metadata_observations": 52912, "vectors_exact": 16}
```

One report-consistency assertion initially expected the final metadata sequence to start at1. Actual final rows start173/end16505, and the existing initial server-info receipt contains startup rows1–172. Inspection of those two raw receipts and the recorder's drain implementation diagnosed the assumption; only this new report/evidence and its assertion were corrected. The corrected check passed; no raw row was renumbered or discarded. An exact set-intersection check also corrected the runtime/source overlap count to4; GDN/hybrid deployment identities are covered by the retained source archives, not separate entries in `runtime.sglang_sources`.

Scoped whitespace commands:

```bash
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_runtime_metadata_native_results.md
git diff --check --no-index /dev/null task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-runtime-metadata-probe-20261111/native-verification-B.json
```

Observed: no whitespace diagnostics for either file; exit1 reflects the expected new-file difference under `--no-index`, not a zero-exit claim.

## 1. 规划完成情况

**汇总：** PASS4｜BLOCKED/FAILED/SKIPPED2｜TODO1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 本分工B actualH800/source/原始样本完整性 | PASS | four actualH800；6/16 source files、16requests/10flushes完整。 |
| 本分工B first4/rep0等价与own cold parity | PASS |16vectors、8comparison groups exact；cold4/4 exact。 |
| 本分工B runtime schema/RID覆盖/dtype | PASS |16333rows；16requests按nativeRID覆盖；不伪造aggregate关联。 |
| 本分工B evidence/report及immutable follow-up | PASS |仅两个owned artifacts；scoring identities固定Git blobs，primary平台receipt独立引用，raws保留。 |
| 原生warm数值正确性 | FAILED |sample2/3 drift原样重现；无因果修复。 |
| 父任务04/05 formal结果 | BLOCKED |requiredRCA/fix尚未接受，不解除hold。 |
| A/unified follow-up | TODO |本次明确B-only；不等待、不poll。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次B-only委托开始至immutable-reference follow-up交付｜**当前前沿：** primary归档两个owned files；primary/analyzer解释真实metadata，A独立报告不属本分工。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR |只执行settle16vectors/source/RID的必要本地检查，不扩展harness。 |
| D2 细节反复重试 | CLEAR |无native重试或修复循环。 |
| D3 支线问题修补 | CLEAR |无代码、配置、science或旧数据编辑。 |
| D4 可并行任务停滞 | CLEAR |按显式B-only指令立即交付，不等待A。 |
| D5 超范围镀金 | CLEAR |只保留要求的两份报告证据，不增加recorder/RCA实现。 |
| D6 分析空转 | CLEAR |实际比较与结构/RID检查直接形成验收证据。 |
| D7 路线违背 | CLEAR |无GPU/platform/auth/SSH；formal hold保留。 |

**文档检查：** S1/S2/S3/S4/S6未发现本分工范围的明显缺陷。S5：`plan.md:51,113`和`requirements.md:73`仍记录metadata未提交/CPU330或306，而较新的`04:40–42`、`05:37–39`已记录CPU332/固定双review/提交；本次又有B终态与numerical验收。只需primary同步当前phase状态，不改科学标准。
**归因：** 无执行偏离；S5为父记录状态滞后，非新业务问题。

## 3. 纠正建议

**分支：** B：当前状态文档存在滞后，primary更新当前phase，不改spec/tickets验收条件。

**文档更新（先执行）：**
1. `requirements.md:73`、`plan.md:51,113`及当前progress/ticket状态：同步CPU332/固定review已接受、B retainedSucceeded/first4等价、A未由本报告验证；保留warmFAIL/formalhold和旧raws（可直接执行；不属于本分工两文件ownership）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. primary接收B报告 → 完成标志：原始16vectors与8groups exact、RID/aggregate边界明确记录，warmFAIL不误写成rootfix。
2. 并行：primary/analyzer解释B实测路径 ‖ A完成后按同样contract做A/unified follow-up；本次不等待A。

## 4. 最值得关注的 3 点

1. B最小化instrumented16vectors逐值等价；sample2/3warmFAIL完整保留，formalhold未解除。
2. metadata覆盖16真实RID，但仅一个DP scheduler；physicalvalues、devicecompletion、allTP和cause/race仍未验证。
3. scoring-source replay已固定到4f1139b0 Git blobs；primary平台receipt仅独立引用，A报告不改动，本分工不stage/commit。
