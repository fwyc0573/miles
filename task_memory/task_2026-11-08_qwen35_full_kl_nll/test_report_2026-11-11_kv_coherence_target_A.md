## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Independently bind A's original partial-overlap checkpoint by native RID and unique CPU receipt keys. |

# A KV measurement target verification

TaskID: `profile-kv-coherence-target-A-20261111`.

Outcome: **PASS, CPU target geometry only.** A's original warm-full sample 1695 has the same numerical window as B, established independently from A's own receipts. This is not physical KV capture, coherence or GPU completion acceptance. The canonical capture design remains in [design_kv_coherence_measurement.md](design_kv_coherence_measurement.md).

## Environment and exact verification

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Interpreter: `/usr/bin/python3`, Python 3.10.6; no conda activation. Foreground command timeout: 60 seconds. Reads are confined to the two local files in the accepted original A output, without platform, GPU or authentication operations.

```bash
/usr/bin/python3 -B - <<'PY'
import json
from collections import defaultdict
from pathlib import Path
root = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-runtime-metadata-probe-20261111/native/A/admission-A-r1')
requests = [json.loads(line) for line in (root / 'requests.jsonl').read_text().splitlines()]
selected = [r for r in requests if r['pair'] == 'A' and r['phase'] == 'warm_stream' and r['repetition'] == 0 and r['mode'] == 'full_input' and r['sample_index'] == 1695]
assert len(selected) == 1
request = selected[0]
rid = request['native_request_id']
assert rid == request['meta_info']['id'] == '4b0a4f32c0a4431a964188b979fd3719'
raw = json.loads((root / 'runtime_metadata.json').read_text())
assert len(raw['server_info']['internal_states']) == 1
metadata = raw['server_info']['internal_states'][0]['mamba_runtime_metadata']
begins, returned, rebinds = defaultdict(list), defaultdict(list), []
for seq, event, fields in metadata['rows']:
    value = dict(fields)
    assert len(value) == len(fields)
    if value.get('rid') != rid:
        continue
    row = {'seq': seq, 'event': event, 'fields': value}
    if event == 'checkpoint_insert_begin':
        begins[(rid, value['page_aligned_len'])].append(row)
    elif event == 'checkpoint_insert_returned':
        returned[(rid, value['node_id'], value['prefix_len'], value['mamba_exist'])].append(row)
    elif event == 'canonical_kv_rebind_enqueued':
        rebinds.append(row)
targets = [r for r in rebinds if r['fields']['page_aligned_len'] == 98304]
assert len(targets) == 1
rebind = targets[0]
f = rebind['fields']
bs = begins[(rid, f['page_aligned_len'])]
rs = returned[(rid, f['node_id'], f['prefix_len'], f['mamba_exist'])]
assert len(bs) == len(rs) == 1
assert not rs[0]['fields']['rotation_tail_declined']
p, e, q = bs[0]['fields']['protected_len'], bs[0]['fields']['page_aligned_len'], rs[0]['fields']['prefix_len']
assert (p, e, q) == (90112, 98304, 98067)
assert (bs[0]['seq'], rs[0]['seq'], rebind['seq']) == (21138, 21141, 21142)
assert f['absolute_start'] == p and f['absolute_end'] == e
assert request['meta_info']['num_retractions'] == 0
result = {'task_id': 'profile-kv-coherence-target-A-20261111', 'pair': 'A', 'source_directory': str(root), 'source_uid': request['source_uid'], 'sample_index': request['sample_index'], 'phase': request['phase'], 'mode': request['mode'], 'repetition': request['repetition'], 'native_request_id': rid, 'protected_len': p, 'page_aligned_len': e, 'returned_prefix_len': q, 'old_overlap_rows': q-p, 'new_suffix_rows': e-q, 'begin_seq': bs[0]['seq'], 'returned_seq': rs[0]['seq'], 'rebind_seq': rebind['seq'], 'begin_bucket_count': len(bs), 'returned_bucket_count': len(rs), 'rebind_bucket_count': len(targets), 'num_retractions': request['meta_info']['num_retractions'], 'rank': metadata['rank'], 'process_id': metadata['process_id'], 'coverage': 'One original DP1 TP0 CPU enqueue scope; not physical values or device completion'}
print(json.dumps(result, indent=2))
PY
```

The command above ran successfully. Its output is retained as [kv-coherence-target-A-20261111.json](evidence/kv-coherence-target-A-20261111.json), with no changes to raw baseline receipts.

## Expected and actual results

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Logical sample to native response identity | One original A warm-full repetition0 sample1695; native ID equals `meta_info.id` | One request, RID `4b0a4f32c0a4431a964188b979fd3719` | PASS |
| Begin/rebind binding | Unique `(rid, page_aligned_len)` bucket | One begin and one rebind at end98304 | PASS |
| Returned/rebind binding | Unique `(rid, node_id, prefix_len, mamba_exist)` bucket; ordinary return | One returned and one rebind; rotation tail not declined | PASS |
| Target geometry | Inspect protected/end/returned values after binding | P90112 / E98304 / Q98067; old overlap7955 / new suffix237 | PASS |
| CPU row provenance | Original A receipt rows | Begin21138 / returned21141 / rebind21142 | PASS |
| Retractions | Zero for selected request | 0 | PASS |
| Scope | One responding process, raw ranks preserved | Process339, DP1 TP0, raw `dp_rank=null` | PASS, bounded |

The inequality Q != P records ordinary shared-cache adoption and is not itself a bug. The selected checkpoint has a partial old overlap; numerical content and its causal effect are unmeasured. The native RID identifies this original run only; a future probe must bind its own response ID to the unchanged logical sample. No node-ID-only or chronological join is used.

All-TP agreement, physical slot values/lifetime, actual store stream, CPP/Triton coverage, global writer-context publication, numerical parity, root cause, performance and formal 200-update acceptance are outside this CPU check. Formal A/B remain on HOLD.
