# KV coherence r2: platform termination and retained failure evidence

## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record exact r2 platform/container identities, application failure timeline, metadata observations, and bounded query coverage. |

## Scope and result

Both bounded diagnostics failed after completing their 16 scoring requests and 10 cache flushes. The initiating application failure recorded in each incident log is the final metadata-readback verdict, not a reported CUDA exception or a demonstrated scheduler preemption. Numerical and physical-index acceptance remain **UNVERIFIED**. Independent scoring/source verification is pending; this report does not substitute for it.

| Pair | RJob | Replica UID | Container | Platform finish (UTC) |
| --- | --- | --- | --- | --- |
| A | `exp-1111-171524-888127` | `4e7006ed-d46c-440a-867e-e519e84d107b` | Error / exit 1 / restart 0 | 2026-11-11T09:28:13Z |
| B | `exp-1111-171526-099435` | `f81ce794-39b9-4406-afa2-89d53bd15a1d` | Error / exit 1 / restart 0 | 2026-11-11T09:29:02Z |

Creator `i-fengyicheng` and replica owner UID were checked through the personal Python client. Initial resource receipts retain image165, four non-preemptible H800 per pair, and the local NFS source `100.96.128.195:/data/ycfeng:/data/ycfeng`. These declarations alone do not establish physical GPU or numerical acceptance.

## Observed timeline

- A: incident log records the application `RuntimeError` at 09:28:09 UTC; container finishes at 09:28:11; RJob finishes Failed at 09:28:13; the retained launcher issues its cleanup `Job Stop` at 09:28:15.
- B: application `RuntimeError` at 09:28:58 UTC; container finishes at 09:29:00; RJob finishes Failed at 09:29:02; launcher cleanup follows at 09:29:06.
- Incident-log nodes are `gpu-h800-0316.host.platform.shaipower.com` (A) and `gpu-h800-0030.host.platform.shaipower.com` (B), bound to the exact replica names. The replica API's `nodeName` was absent; it was not filled from inference.
- The retained result records scoring completion, cleanup completion, and a server shutdown return code of -9. That server cleanup result is not the container exit code and is not OOM evidence.

Exact application error:

```text
RuntimeError: Scoring completed; independent runtime metadata readback failed: KV coherence diagnostic unverified: Candidate cardinality/capture errors/unconsumed CPP witness
```

## Metadata observations, not numerical acceptance

Both after-all-16 readbacks returned HTTP 200, then failed the diagnostic verdict. The resolved-config fix reached initialization and preallocation:

| Observation | A | B |
| --- | --- | --- |
| FULL layers | 16 | 10 |
| Allocated diagnostic bytes | 539,361,280 | 337,248,256 |
| Global `note_cpp` errors | 112 | 70 |
| Global `fresh` errors | 112 | 70 |
| Error message | `object of type 'NoneType' has no len()` | Same |
| Selected banks | 2 | 2 |
| Warm original-FULL fragments | 2, totaling 7,955 rows | 2, totaling 7,955 rows |

Actual topology records `TokenToKVPoolAllocator`, `HybridLinearKVPool`, `MHATokenToKVPool`, and page size 1. The warm fragment lengths are 6,519 and 1,436, with returned Q=98,067. These host receipts do not establish completed GPU reads, fresh capture completeness, independent physical-index equality, or usable KV statistics. `fresh_layers` enumerates entries and must not be treated as a completeness verdict. `numeric_acceptance` is null. Collector-field RCA belongs to the separate batch-metadata investigation, not this report.

## Commands and environment

- Platform inspection: `/data/ycfeng/tmp/stepmind-env/bin/python -B` with `STEPMIND_BACKEND=rjob`, the runbook's existing personal-auth/proxy environment, and `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`. Exact reads use `client.api.get_namespaced_custom_object(...)`, `client.get_rjob_infos(exact_job)`, and `client._get_replica_kapis(exact_replica)`; filtered receipts only, no raw secret-bearing spec/env.
- RCA collection uses the same Python environment (Python 3.10.6, brainpp 2.8.6):

```bash
timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
  exp-1111-171524-888127 --replica exp-1111-171524-888127-cfcd2084 \
  --expected-creator i-fengyicheng --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
  --start 2026-11-11T09:26:00Z --end 2026-11-11T09:30:00Z --timeout 12 \
  --output /data/ycfeng/tmp/opencode-v2-tmp/opencode/rca-exp-1111-171524-888127-r2

timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
  exp-1111-171526-099435 --replica exp-1111-171526-099435-cfcd2084 \
  --expected-creator i-fengyicheng --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
  --start 2026-11-11T09:27:00Z --end 2026-11-11T09:31:00Z --timeout 12 \
  --output /data/ycfeng/tmp/opencode-v2-tmp/opencode/rca-exp-1111-171526-099435-r2
```

Both collectors exited 1 because RJob and replica all-operation audit reads each hit `ReadTimeout` at 12 seconds. These are evidence-query failures, not additional native execution failures. They were not retried or recorded as empty audits. Live events: zero returned, complete pagination. Historical events: 3 RJob and 2 replica rows per pair, all startup scheduling/pull/start events. Existing DeepScan: zero flows, complete pagination. Incident logs: 12 rows per pair, `has_more=false`; selected traceback/verdict lines retained. No positive OOM/preemption/independent eviction event appears in these queried records; this limited coverage does not exclude an unrecorded event. External initiating stop actor/reason/request time remain UNKNOWN, rather than being assigned from creator or subsequent cleanup.

## Evidence and validation limits

All paths below are under `evidence/teacher-scoring-kv-coherence-probe-20261111/`:

- `terminal-platform-A-r2.json`, `terminal-platform-B-r2.json`: exact filtered container and owner records.
- `initial-platform-A-r2.json`, `initial-platform-B-r2.json`: original allocation/source declarations.
- `r2-capture-failure-observations.json`: compact retained-result and metadata observations.
- `platform-rca-r2/{A,B}/`: query outcomes, original redacted event records, audit timeout records, and selected incident-log signal.
- `native/{A,B}/admission-{A,B}-r2/`: original business/result/readback artifacts, unchanged.

Expected successful native execution required a verified readback and exit 0: **FAIL**. Successful HTTP delivery and preserved scoring completion: **OBSERVED**, not numerical acceptance. No fix, additional GPU submission, stream change, raw-KV archive, or formal retry is authorized by this report. Formal04/05 HOLD and independent 200-update requirements remain unchanged.
