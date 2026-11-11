# Cache-salt teacher-scoring probe preparation

**Modification History**

| Date | Change |
| --- | --- |
| 2026-11-11 | Record the scoped request, source qualification and first request-boundary RED/GREEN checkpoint. |
| 2026-11-11 | Complete config/worker RED/GREEN,24 affected and350 joined CPU checks, real A/B controller dry-runs, syntax validation and the pre-commit checkpoint. |
| 2026-11-11 | Resolve the Standards documentation Nit by referencing canonical native preregistration instead of adding an unchanged-observations acceptance condition. |

## 1. Plan completion

TaskID: `profile-cache-salt-counterfactual-preparation-20261111`.

**Original Request:** prepare only the CPU-ready first4/one-repetition diagnostic. Only full-input requests may add the existing native `cache_salt`, equal to pair plus the existing pre-send local request ID. Response-only requests, flags, inputs, scoring math, RNG, ordering,16 requests/10 flushes, selected-FP32/runtime-metadata preparation and teacher resources remain unchanged. Persist the salt directly from the sent payload, including failures; never replace native RID. Clone the current metadata config except the single boolean experiment and isolated output. Own only the existing probe/test plus this new report and the new cache-salt config. No source/submission/formal/core edits, delegation or GPU/platform/auth/SSH operations.

The parent `requirements.md:75` and `plan.md:53` report A/B16/16 exact parity with original FP32 repetition0 first4, cold4/4 and warm1/4. Those are prior accepted parent observations, not measurements from this preparation. The direct assignment authorizes CPU preparation only; parent formal04/05 remain held.

**Summary:** PASS 4 | BLOCKED 1 | TODO 1. This verification checkpoint precedes the scoped Git commit; the returned immutable commit is the final delivery evidence.

| Subtask | Status | Evidence |
| --- | --- | --- |
| Full-only request salt and direct receipt/native RID contract | PASS | Sent salt is retained on success/HTTP/validation failure; native RID remains independent. |
| Boolean config and exact isolated clone | PASS | Exact text/JSON clone apart from cache_salt_full_input=true and output_parent; both teacher argv unchanged. |
| First4 structure, unsalted controls, failure preservation and worker wiring | PASS | A/B absent/False/True retain16 requests/10 flushes and exact order;8 controls/4 cold-full/4 warm-full. |
| Real controller dry-run, syntax and joined CPU checks | PASS | A/B submitted=false;24 affected and350 joined PASS, valid syntax/JSON. |
| Scoped four-file commit | TODO | Only after required verification. |
| Future native acceptance | BLOCKED | Outside this assignment; no GPU execution authorized. |

The agreed test seams are the existing `/generate` HTTP boundary and retained receipts, existing probe config/worker, and existing controller dry-run. External HTTP/startup/inspection are CPU mocks; core score construction and source preparers remain real where their retained inputs are available. No replacement recorder is implemented.

**Owned deliverables:** `tests/manual/agent_opd/probe_teacher_scoring.py`, `tests/fast/test_teacher_scoring_probe.py`, `task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_cache_salt_probe_config.json` and this report. Owned code starts from4f1139b0; parent-only documentation/evidence changes are outside this slice.

**Exact implementation contract:** `cache_salt_full_input` is one JSON boolean in the existing probe experiment map, validated before worker startup. True is passed through the existing formal-config wrapper and worker/benchmark to the request boundary. Absent/False sends no new keyword to legacy worker/benchmark collaborators and no salt in either payload. `_payload` and production `_score_payload` remain untouched. For True/full_input only, the existing request ID is computed before send and payload gains `cache_salt=f"{pair}:{request_id}"`; for example `A:cold-r2-s3-full_input`, never a server RID or UID/index. The existing request receipt stores `payload.get("cache_salt")` before HTTP, including failed requests; unsalted receipts have null. Native `meta_info.id`/native_request_id and completion identity handling are unchanged. No additional runtime instrumentation, HTTP, flush, file per request or loop/order change is introduced.

The new config is byte-for-byte recoverable to the metadata config by removing only the boolean line and restoring output_parent. Inherited task_id/acceptance text is deliberately unchanged under the exact-clone request. The current counterfactual's acceptance protocol is the explicit scoped request recorded here, not a new interpretation of the inherited metadata-probe text.

**Source qualification:** retained C1 root is `evidence/native-sglang-cache-source-20261111/exp-1111-040603-422872/source/`. `srt/managers/io_struct.py:377–378` declares the native cache namespace; `tokenizer_manager.py:1716` forwards it; `schedule_batch.py:1086,1172` retains it on Req. `srt/mem_cache/radix_cache.py:222–247` namespaces child keys by `(extra_key, cache_salt)`. `unified_radix_cache.py:1204–1209,1260–1265` passes the same namespace to checkpoint/prompt keys, covering the shared KV/Mamba tree rather than changing scoring parameters. C3 retains selected changed files rather than every C1 file; missing C3 copies of these unchanged files are not silently invented.

`schedule_batch.py:1768–1777` already limits full-input lookup to0 because return_logprob is true and logprob_start_len is0. Salting does not justify a changed initial prefill schedule. `unified_radix_cache.py:1232–1238,1284–1298,1317` inserts page-aligned checkpoints, rebinds from the currently protected prefix and advances protection. Future per-RID ordinary checkpoints must satisfy returned.prefix_len==begin.protected_len, rebind.start==begin.protected_len and rebind.end==begin.page_aligned_len; the request's own protected prefix can grow. Do not require every prefix to be0 or prohibit rebinds.

Pristine retained-source SHA256 values below are source qualification only, not live/salted-worker evidence:

| Relative source under the C1 root | SHA256 |
| --- | --- |
| srt/managers/io_struct.py | 1f94aca08ed27f74280e87ec80999df32df3088be987ec1377ff2f572e13739b |
| srt/managers/tokenizer_manager.py | 65a92c050d33a9749a5f7f76fe98dba85a7fcb89d2fb20eddb2e89e6ed648f06 |
| srt/managers/schedule_batch.py | 455b597607f9ae753272666b4d3d07e9390d620d7ce400fda6f4686a74d84c0d |
| srt/mem_cache/radix_cache.py | eea7015fcf678167ac7296b08c8dc568ccbe42a4bb106da23b33a7c59debec01 |
| srt/mem_cache/unified_radix_cache.py | 9c1a1116081c266301ecfeef4faf4178d18114a8996010765d9aa238cd83deb3 |

**Environment:** Linux, `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`; CPU interpreter `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, pytest9.1.1. Temporary storage is under `/data/ycfeng/tmp/opencode-v2-tmp/opencode`; bytecode and pytest repository cache writes are disabled below.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'cache_salt_full_input_is_pre_send' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/cache-salt-request-red-20261111
```

Expected RED: the dedicated probe cannot yet send the experiment. Observed1 failed/133 deselected/2 existing warnings/0.83s, `TypeError: _request() got an unexpected keyword argument 'cache_salt_full_input'`.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'cache_salt_full_input_is_pre_send' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/cache-salt-request-green-20261111
```

Expected GREEN: sent full-input JSON gains only `cache_salt=A:cold-r2-s3-full_input`; retained native RID remains the independent response ID. Observed1 passed/133 deselected/2 existing warnings/0.77s; PASS.

**Config cycle:**

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'cache_salt_config' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/cache-salt-config-red-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'cache_salt_config' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/cache-salt-config-green-20261111
```

Expected RED: missing variant and ignored non-boolean key. Observed7 failed/134 deselected/4 existing warnings/1.27s:2 FileNotFoundError cases and5 DID NOT RAISE ValueError cases. After the exact clone and boolean validation/forwarding, expected GREEN: A/B argv/allocation unchanged and variant passed by existing controller --config; observed7 passed/134 deselected/4 existing warnings/0.89s; PASS.

**Worker/structure cycle:** the initial command below, with basetemp `cache-salt-worker-red-20261111`, failed collection (0 items/2 existing warnings/0.85s) because pytest9 rejects a parametrized argument with a default. Only that test confound was corrected: remove its default and pass None explicitly in the existing override regression's two direct calls. Production worker wiring was still unchanged before the qualified RED.

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'cache_salt_first4 or selected_source_preparation' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/cache-salt-worker-red-qualified-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'cache_salt_first4 or selected_source_preparation' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/cache-salt-worker-green-20261111
```

Expected qualified RED: existing worker loses True and benchmark cannot accept the experiment; absent controls remain functional. Observed5 failed/9 passed/135 deselected/4 existing warnings/4.24s. Expected GREEN after one wiring change: unchanged real selected-FP32→metadata→runtime→teacher order/receipts/argv, correct8 full salts and8 controls,16/10 and native RID; observed14 passed/135 deselected/4 existing warnings/4.69s; PASS. The source fixture continues to honor MILES_PINNED_SGLANG_SOURCE and explicit missing-evidence skips, copying only to its isolated root.

**Affected and joined checks:**

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -k 'cache_salt or selected_source_preparation' -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/cache-salt-affected-20261111
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py tests/fast/test_sglang_mamba_snapshots.py tests/fast/test_sglang_mamba_runtime_metadata.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/cache-salt-joined-20261111
```

Expected: direct sent-salt retention on HTTP503/validation failures, no native RID overwrite, exact baseline absent/False/response-only JSON, original first4 identities/order, no extra request/flush, real source preparation and unchanged comparisons. Observed affected24 passed/127 deselected/4 existing warnings/4.97s; joined350 passed/20 existing warnings/31.67s, including all151 probe tests; PASS with no suite failure/skip. Existing baseline7×2 remains56 scoring requests/32 flushes. The macro deliberately injects one warm-full deviation despite salting and verifies existing max absolute0.125/relative1, accepted=None; it does not invent a numerical salt PASS. Existing zero-reference regression still verifies undefined relative errors. Reversed metadata RID order remains independent of retained request order.

**Real standalone controller dry-runs:**

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_cache_salt_probe_config.json --pair A --receipt /data/ycfeng/tmp/opencode-v2-tmp/opencode/cache-salt-controller-A.json --dry-run
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_cache_salt_probe_config.json --pair B --receipt /data/ycfeng/tmp/opencode-v2-tmp/opencode/cache-salt-controller-B.json --dry-run
```

Expected: return0 before auth/client construction, submitted=false,4 H800/codesign per pair with identical native image/resources/mounts/source and variant worker --config. Observed both returned0/submitted=false,4 GPUs,32 CPUs,256GB,replica1, source_directory=/data/ycfeng, existing two cloud mounts and PYTHONPATH=/data/ycfeng; PASS. Both worker commands select the new absolute variant path, original first4 manifest, repeats1/request-timeout3600, worker budget3600/cleanup90. Output is isolated under `evidence/teacher-scoring-cache-salt-probe-20261111/native/{A,B}/cache-salt-controller-{A,B}`. No receipt/output directory, job or auth access is created by the dry-run. The config test also runs both base/variant through the real controller and proves only worker --config/--output-dir and output path differ; full teacher argv is equal to the formal owner, preserving model/BF16/chunk8192/cache-on/concurrency1/deterministic settings. The immutable image is still sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805.

**Syntax/JSON and source-hash checks:**

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
from pathlib import Path
import json
for path in (Path('tests/manual/agent_opd/probe_teacher_scoring.py'), Path('tests/fast/test_teacher_scoring_probe.py')):
    compile(path.read_text(), str(path), 'exec')
json.loads(Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_cache_salt_probe_config.json').read_text())
print('PASS: both owned Python files compile and the new config is valid JSON; no bytecode written')
PY
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
from pathlib import Path
import hashlib
import json
root = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111/exp-1111-040603-422872/source')
files = ('srt/managers/io_struct.py', 'srt/managers/tokenizer_manager.py', 'srt/managers/schedule_batch.py', 'srt/mem_cache/radix_cache.py', 'srt/mem_cache/unified_radix_cache.py')
print(json.dumps({name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files}, indent=2))
PY
```

Observed expected syntax/JSON PASS with no bytecode writes, and the five existing pristine source hashes shown above. Scoped code diff changes only boolean propagation, full-only native payload salt and its direct receipt field; source/submission/formal/core score/comparison/RNG paths are unchanged. No Tensor read, CUDA event/wait/sync, new runtime trace, polling or extra HTTP/cache flush was added.

```bash
git diff -- tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_teacher_scoring_probe.py
git diff --check -- tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_teacher_scoring_probe.py task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_cache_salt_probe_config.json task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_cache_salt_probe_preparation.md
git diff --cached --check -- tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_teacher_scoring_probe.py task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_cache_salt_probe_config.json task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_cache_salt_probe_preparation.md
```

Observed the scoped source/test diff described above and no whitespace errors in the worktree or staged four-file diff; PASS. The pre-commit parent HEAD is272c12dd; no unrelated native evidence is staged by this slice.

**Future native contract:** follow the [canonical preregistration](spec.md) for controls, per-RID checkpoint isolation and numerical comparisons. Compare and report initial/full-chunk/tracking/num_retractions observations and their differences; this report adds no unchanged-observations acceptance condition. Native execution, performance, root-fix and formal acceptance remain unverified.

## 2. Drift detection

**Verdict:** no drift detected. Window: first request checkpoint through350 joined checks and A/B standalone dry-runs. Frontier: scoped four-file commit/handoff only; native execution remains outside scope.

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 Tooling polish | CLEAR | Only requested proportional regressions and affected/joined/dry-run/syntax checks; stop after they pass. |
| D2 Retry loop | CLEAR | Three vertical RED/GREEN slices; one pytest fixture confound corrected before qualified worker RED. |
| D3 Side quest | CLEAR | Only the four-file assignment is being edited. |
| D4 Stalled frontier | CLEAR | Shared probe/test ownership and explicit no delegation require serial slices. |
| D5 Gold-plating | CLEAR | One boolean/full-only native parameter; no CLI/registry/source recorder. |
| D6 Analysis sprawl | CLEAR | Inspected source binds the requested parameter and rejects the initial-prefill assumption. |
| D7 Off-route | CLEAR | No GPU/platform/auth/SSH/native execution or unrelated evidence edits. |

**Spec checks:** S1–S6 show no defect in the direct scoped assignment. The inherited config task ID/acceptance text will remain untouched as explicitly requested; this report records the new preparation protocol, not a parent-doc update. Attribution: none.

## 3. Route correction

Branch A: scope and criteria are sound; no parent spec/ticket edits. Behaviors to stop: none.

1. Commit only the four verified owned files and return the immutable preparation, preserving parent documents and unrelated untracked native evidence.
2. Primary may later judge the precise native control/isolation/numerical contract after explicit authorization; do not launch it from this preparation or broaden the tests.

## 4. Three points to watch

1. CPU preparation is complete:24 affected/350 joined PASS and real A/B dry-runs preserve the worker variant and native allocation inputs.
2. Salting changes cache namespace only; initial full-input prefix0 and the request's own growing checkpoint protection must not be misinterpreted.
3. Native controls/isolation/warm-full comparison remain PENDING; source qualification and CPU mocks do not prove KV–SSM causality, numerical correction, performance or formal acceptance.
