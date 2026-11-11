# Original r2 metadata replay against the new generated runtime

## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record the executed CPU-only replay through existing composed test fixtures; preserve original raw/RCA runtime and results. |

TaskID: `profile-kv-coherence-forward-mode-fix-20261111`.

This command was executed from the repository root and returned exit0. It uses the existing source/composed test fixture, exact retained ForwardMode enum and real context publish/restore. DECODE is supplied as the primary-accepted source/event inference, not fabricated as a captured WIT mode. The original null fields are replayed again as true EXTEND to verify fail-loud behavior. No original runtime/artifact is rewritten; the output uses exclusive creation, so choose a fresh output filename if rerunning.

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import hashlib,json,resource,tempfile
from pathlib import Path
from types import SimpleNamespace
import pytest
from tests.fast import test_sglang_kv_coherence as cases
resource.setrlimit(resource.RLIMIT_AS,(30*1024**3,30*1024**3))
base=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence')
recorded=json.loads((base/'kv-coherence-batch-metadata-rca-20261111/receipt_counts.json').read_text())
result={'task_id':'profile-kv-coherence-forward-mode-fix-20261111','scope':'CPU_SOURCE_REPLAY_ONLY','mode_column_captured':False,'pairs':{}}
for pair in ('A','B'):
 with tempfile.TemporaryDirectory(dir='/data/ycfeng/tmp/opencode-v2-tmp/opencode',prefix='kv-forward-mode-replay-') as directory, pytest.MonkeyPatch.context() as patch:
  root=Path(directory)
  composed=cases.composed.__wrapped__(root,patch)
  collector,pool,capture=cases.generated_callbacks.__wrapped__(composed,root,patch)
  modes=cases.forward_mode.__wrapped__()
  collector.start,collector.end=90112,98304
  selected=recorded['pairs'][pair]['selected_rows']
  def batch(row,mode):
   fields=dict(row[2])
   return SimpleNamespace(rids=fields['rids'],extend_prefix_lens_cpu=fields['prefix_lens'],extend_seq_lens_cpu=fields['extend_lens'],forward_mode=mode,moe_num_token_non_padded=lambda:None)
  capture(None)
  capture(batch(selected['startup_null_stream'],modes.DECODE))
  capture(batch(selected['business_first_stream'],modes.EXTEND))
  assert collector.errors==[] and collector.pending_cpp=={}
  capture(batch(selected['startup_null_stream'],modes.EXTEND))
  assert [error['stage'] for error in collector.errors]==['note_cpp','fresh']
  assert all(error['message']=="object of type 'NoneType' has no len()" for error in collector.errors)
  result['pairs'][pair]={'native_process_id':recorded['pairs'][pair]['process_id'],'recorded_null_seq':selected['startup_null_stream'][0],'recorded_business_seq':selected['business_first_stream'][0],'mode_for_null_state':'DECODE supplied from accepted source/event inference, not captured native enum','absent_context_and_decode_and_business_extend':'PASS','same_null_fields_as_true_EXTEND':'FAIL_LOUD_EXPECTED','invalid_extend_error_count':len(collector.errors),'generated_runtime_sha256':hashlib.sha256((composed/cases.coherence._RUNTIME).read_bytes()).hexdigest()}
print(json.dumps(result,indent=2))
with (base/'kv-coherence-forward-mode-fix-20261111/original-scenario-replay.json').open('x') as output:
 json.dump(result,output,indent=2)
PY
```

Observed A process340/seq184 and business566; B process347/seq118 and business368: absent context, inferred DECODE-compatible native null state and real business EXTEND counterpart PASS. Replaying the same missing fields as true EXTEND appends exactly the original two global errors in both pairs. Both generated-runtime hashes are `773e2c6186d95e10e2fc287f9c6f37e9489df068267257ae3c3ba6ad4e8733ed`. No tensor contents, native library or GPU are validated by this replay.
