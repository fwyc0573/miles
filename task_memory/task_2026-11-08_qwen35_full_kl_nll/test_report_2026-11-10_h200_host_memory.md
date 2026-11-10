## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Accept the corrected attempt's first-two-update native lifecycle; retain stage-matched memory comparisons and long-run/attribution limits. |
| 2026-11-10 | Add controlled native allocation-order evidence from the successful D38 diagnostic and retain the full-model attribution boundary. |
| 2026-11-10 | Record the post-update host-memory failure, pinned TMS source inspection and D38 diagnostic authorization. |

# H200 post-update host-memory investigation

## Confirmed failure

Formal A `exp-1110-140032-491115` completed its first optimizer update and passed[the D16 measurement checks](test_report_2026-11-10_d16_first_update.md). The subsequent trainer sleep/offload exceeded Ray's host-memory threshold and Ray killed trainer PID8670. The later Gloo/weight-update errors followed that termination. The attempt is Failed,1/200, and all replicas are terminal.

The raw rank0 log is `/data/ycfeng/tmp/agent-opd-image/d16-exp-1110-140032-491115/rank-0.log`. Relevant ranges are4154–4166 for NORMAL outcomes/sleep and4206–4259 for the memory-monitor decision. Selected evidence and query availability are in[evidence/d16-H200-A-20261110/failure-and-coverage.json](evidence/d16-H200-A-20261110/failure-and-coverage.json).

The selected text excerpt adds source line numbers and normalizes two whitespace-only line tails for Git whitespace checks. The complete raw log is retained unchanged at the path above.

- One Ray diagnostic reports487.49GiB of500GiB. A separate kill-scan observation is510,431,268,864 bytes =475.376GiB against a510,027,366,400-byte =475GiB threshold. They are different samples.
- The80.31GB CPU log field comes from `psutil.virtual_memory().used / 1e9` at `miles/backends/training_utils/metrics/log_utils.py:448–456`: it is node-global and cannot be used as per-rank RSS or the Ray cgroup's memory.
- The eight process-memory lines sum to approximately434.76GB; that sum is not a unique-physical-memory accounting. Ray's object-store reading is about9.58MB.

No Ray protection setting, memory request or training/offload target has been changed as a result of this investigation.

## Inspected ownership and limits

The read-only source investigation traced `miles/train.py:259–293` → `miles/ray/train/group.py:581–584` → `miles/backends/megatron_utils/actor.py:496–526`. Before `torch_memory_saver.pause(tag=None)`, the existing path clears TE workspaces, synchronizes, runs garbage collection, empties CUDA/host caches and destroys process groups. Both disable-parameter-CPU-backup and disable-gradient-CPU-backup flags were already true in the actual launch.

After clearing, rank4 still reported19.09GiB allocated versus79.93GiB reserved, a60.84GiB difference. Rank6's difference was28.74GiB. This supports investigating retained underlying allocation segments; it does not identify which live tensor kept any particular segment resident. A possible explanation is first-use Adam moment allocation splitting previously cached large forward-output segments. The failed process's segment/block ownership snapshot was not captured, so that attribution is **unproven**.

The source-based state estimate uses2,102,962,433 parameters per TP rank at TP2/DP4: BF16 parameters3.917GiB, FP32 gradients7.834GiB, FP32 master shard1.959GiB and Adam moment shards3.917GiB. Including the actor mirror gives roughly172.35GiB across eight ranks; with parameter/gradient TMS backups disabled, master/moments/mirror account for roughly78.34GiB. These are estimates excluding padding, auxiliary buffers and runtime allocations. They are not measured backup sizes or grounds to change the500GiB request.

## Pinned-image CPU inspection

The primary submitted zero-GPU job `exp-1110-144951-170247` locally through personal StepMind `RJobBackend`. Its job and sole replica succeeded. The exact command, image and resource/mount inputs are retained in[evidence/native-tms-source-20261110/worker-command.json](evidence/native-tms-source-20261110/worker-command.json); [terminal identity](evidence/native-tms-source-20261110/terminal.json) and[source manifest](evidence/native-tms-source-20261110/source.json) are retained separately.

Observed environment: Python3.12.16, `torch-memory-saver==0.0.10`, the same immutable image digest `165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805` as formal A. The script read installed Python source, SHA256-hashed each source/native binary and ran `nm -D --defined-only` on both native libraries. It performed no CUDA allocation or pause/resume.

| Binary | SHA256 | Observed support |
| --- | --- | --- |
| Preload CUDA13 | `99bbe5e2df91c5f9e5cd0a65e3947ceb3304bbb6a2b6ad539f00326cc583dcd4` | Disk enable/get/set-directory exports and DiskBackend symbols |
| Torch CUDA13 | `7a65bf68eb376d13d4ee28bdc123e88fd7abed556b40485ed98c67a408dde8fb` | Same exported disk interface |

This confirms the installed version and available interfaces. It does not measure native CPU backup bytes, disk offload correctness, page-cache behavior or the available storage on a subsequently allocated H200 worker. The source copies remain locally under the manifest's explicit paths. The CPU worker's `/var/tmp` had2,748,533,202,944 available bytes at capture; that is not a placement or disk-space promise for another worker.

## D38 diagnostic: prelaunch record

[D38](requirements.md#host-memory-diagnostic-route--original-request-2026-11-10) authorized one H200 allocator/TMS diagnostic with a600-second worker-script limit, startup separate. At the prelaunch checkpoint, a separate implementation owner was preparing the comparison and the diagnostic had not been submitted. The primary owns submission and result acceptance.

Acceptance will distinguish successful execution and roundtrip checks from support for the allocation-retention hypothesis. Controlled behavior alone will not be called proof of the old full-model run's specific allocation owner. Any correction must subsequently pass the actual train → sleep → weight-update → next-train path, with optimizer progression and native business outputs inspected.

The existing disk-offload alternative was not selected. Formal artifacts remain protected, and the two earlier H800 zero-update attempts remain separate. Audited platform stop-request actor/time are still UNKNOWN because those two bounded audit reads failed; the native memory-monitor evidence is retained independently.

## Controlled native result

Job`exp-1110-160647-698733`and its one H200 replica succeeded, exit0/restart0,container72s. The full[native diagnostic report](test_report_2026-11-10_allocator_probe.md#native-result--pass) and[independent verification](evidence/tms-allocator-20261110/native-verification.json) confirm that late64MiB Adam moments occupy active blocks within the released1GiB transient segment, retaining896MiB inactive; early initialization gives the same moments independent64MiB segments. Equal live allocation produces1090 versus194MiB reserved and approximately1090 versus194MiB pause RSS increase. Both native pause/resume/state/step checks pass.

This diagnostic supported correcting optimizer-state allocation timing through the existing native callback. It did not establish which allocation owned the old full-model segment. The subsequent implementation and formal validation are recorded below.

## Corrected formal lifecycle — first two updates

**PASS for the previously failing lifecycle, as of09:54:09Z; formal completion remains2/200.** Correction`edd3be00`and naming follow-up`d2b3af8c`passed the[fixed-diff reviews](review.md#optimizer-initialization-phase-review--2026-11-10). Independent corrected attempt`exp-1110-165312-132926`uses the same18-H200 configuration and CPU offload route. The[successful ACK notification](evidence/formal-H200-A-r2-second-update-notification-20261110.json)contains updates1/2,zero skipped updates,banks0/1 each visited once,and256 turns per update. These are separate from the old failed attempt's1/200.

The[retained lifecycle extract](evidence/formal-H200-A-r2-first-two-lifecycle-20261110.json)contains original cloud-log line numbers and message timestamps. The primary inspected these records; read-only follow-up `profile-h200-post-update-host-oom-20261110` independently confirmed the following sequence without changing the run:

| Stage | UTC observation | Evidence |
| --- | --- | --- |
| Train1 | Successful ACK retained; before-optimizer timestamp09:21:48.140657; train timer188.283s | Notification72–81; lifecycle219–224 |
| Post-update1 offload | Visible before09:21:50.378 through last visible after09:22:08.100 | Lifecycle227–244,375–376 |
| Weight sync1 | Controller09:22:08.241→09:22:09.441;8 actors;`ok=true`;1.200s | Lifecycle259–264,355–356 |
| Restore for train2 | Rank0 timer09:45:52.749→09:46:02.130;9.381s. Rank6 ends09:46:03.283,reported10.5s | Lifecycle403–440 |
| Train2 | Successful ACK retained; before-optimizer timestamp09:50:08.640495; train timer246.575s | Notification139–148; lifecycle443–448 |
| Post-update2 offload | Visible09:50:12.352→09:50:29.866; followed by sync | Lifecycle451–468,607–608 |
| Weight sync2 | Controller09:50:30.001→09:50:31.177;8 actors;`ok=true`;1.176s | Lifecycle487–492,587–588 |
| Continued generation | Subsequent successful samples carry weight version2 | Lifecycle649–650,745–746 |

Controller success is emitted after gathering all actors (`miles/ray/train/cell.py:252–274`); this establishes group-level return, not a complete per-rank timing record. Ray deduplication delays repeated messages and does not expose hidden rank values. The visible offload intervals are not eight-rank barrier timers. `perf1.sleep_time=18.190s`belongs to the first post-update sleep, because the performance logger resets timers; it is not a measurement of the second sleep. The native receipt timestamps are1700.500s apart, but `swe_training.py:281–321`captures them before the optimizer and`:347–365`publishes success afterward. Thus they are not exact ACK-publication times. The primary corrected this interpretation from the lifecycle follow-up using the independently inspected receipt writer.

### Memory observations and comparison limits

GPU values below are allocated/reserved **GiB**, despite the log's`GB`labels (`miles/utils/memory_utils.py:18–32`). A dash means that stage/rank was not retained independently.

| Rank/PID | Update1 before→after offload | Update2 before→after offload |
| --- | --- | --- |
| 0/9066 | —→— |19.31/52.37→— |
| 3/9069 |19.11/34.46→19.11/34.46 |—→19.33/34.47 |
| 4/9070 |—→19.11/51.29 |—→19.35/51.30 |
| 6/9072 |19.08/51.75→19.08/51.75 |—→19.31/51.76 |
| 7/9073 |—→— |19.31/51.75→— |

- The shown ranks3/4/6 have post-offload device usage3.14–3.18GiB. Their post-offload reserved counters differ by only0.01GiB between the two visits; this is two observations, not a long-run growth bound or proof that inactive space is gone.
- Same-stage descriptive comparisons to the old log are mixed: rank3 after-offload reserved50.94→34.46GiB (−16.48GiB),rank6 before-offload47.82→51.75GiB (+3.93GiB). Old log anchors4170,4173,4180. Different attempt inputs prevent treating these as a controlled causal comparison.
- Old rank4 was captured **before** offload at19.09/79.93GiB; the new rank4 value19.11/51.29GiB is **after** offload. No same-stage reduction is claimed from that pair.
- Rank0's CPU logger prints84.73 and80.68 decimalGB. As established above, these are`psutil.virtual_memory().used / 1e9`, not trainer RSS,Ray cgroup peak or measured TMS backup bytes. Current cgroup peak and exact full-model allocation ownership remain unverified.

The[subsequent personal API readback](evidence/formal-H200-A-r2-two-update-readback-20261110.json)shows the job and all three replicas Running,non-preemptible,zero container restarts. No new native blocker requiring interruption was found. The main launcher remains active, with a read-only observer now targeting update10. Final200-update stability,terminal status and complete profile acceptance remain open. The separate[first-two canonical/profile verification](test_report_2026-11-10_corrected_profile_prefix.md)is accepted:512 observations,exact original-file rebuild,zero absolute/relative RKL/NLL errors and both acquisitions within1800s. That prefix does not establish long-run memory behavior.

### Evidence collection

The main session read only this attempt's exact personal cloud log via`ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng 'test "$(id -un)" = i-fengyicheng && python3 -B -'`, with a60-second local timeout. It streamed the log once, retaining157 lines matching memory/sleep/wake/weight-update/native-success events and the last30 lines. Line numbers and file size are preserved in the lifecycle JSON. No cloud file was written or altered.

Six exact canonical/native/profile files were copied through a read-only tar stream, totaling349,252,623 bytes. [Retention manifest](evidence/formal-H200-A-r2-first-two-20261110/retention.json)records each retained size/SHA256 and source path; the temporary transfer archive is`/data/ycfeng/tmp/agent-opd-image/formal-H200-A-r2-first-two-20261110.tar`. The large bank snapshots remain untracked; formal cloud artifacts remain protected. These copies support the existing offline inspector, not another GPU run or an auxiliary hard gate.

### Primary delivery verification

Local Python3.10.6 verification passed:9 delivered output fingerprints match,18 curated files parse/scan cleanly,credential-value/private-key-block matches0,native/profile verified counts2 with full-completefalse,and runtime/config diff from`d2b3af8c`empty. Scoped whitespace also passes. Exact command from the worktree root:

```bash
python3 -B - <<'PY'
import hashlib,json,re,subprocess,sys
from pathlib import Path
root=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll');snap=root/'evidence/formal-H200-A-r2-first-two-20261110';delivery=json.loads((snap/'delivery-verification.json').read_text());retention=json.loads((snap/'retention.json').read_text())
assert delivery['verdict']=='PASS' and delivery['input_fingerprints']==retention['files']
files=[Path(name) for name in delivery['outputs']]
for path in files:
 raw=path.read_bytes();expected=delivery['outputs'][str(path)]
 assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['sha256'],path
receipt=json.loads((snap/'inspection-prefix.json').read_text())
assert receipt['native']['observed_successful_update_ids']==[1,2] and receipt['profile']['verified_updates']==2
assert not receipt['native']['complete'] and not receipt['profile']['complete'] and receipt['expected_updates']==200
assert delivery['actual_errors_all_zero'] and delivery['original_rebuild_exact_match']
files += [snap/'retention.json',snap/'delivery-verification.json']
files += [root/'evidence'/name for name in ('formal-H200-A-r2-second-update-notification-20261110.json','formal-H200-A-r2-first-two-lifecycle-20261110.json','formal-H200-A-r2-two-update-readback-20261110.json')]
files += [root/name for name in ('progress.md','review.md','test_report_2026-11-10_formal_runs.md','test_report_2026-11-10_h200_host_memory.md')]
secrets=[(Path('/data/ycfeng/tmp/brainctl-auth-i-fengyicheng')/name).read_text().strip() for name in ('accesskey_id','accesskey_secret')];assert all(secrets)
for path in files:
 text=path.read_text()
 if path.suffix=='.json':json.loads(text,parse_constant=lambda value:(_ for _ in ()).throw(ValueError(value)))
 assert not any(secret in text for secret in secrets),path
 assert not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\r?\n[A-Za-z0-9+/=]',text),path
assert not subprocess.check_output(['git','diff','d2b3af8c','--','miles','tests/manual/agent_opd',str(root/'formal_h200_config.json'),str(root/'h200_gpu_policy.json')])
subprocess.run(['git','diff','--check','--',*[str(path) for path in files]],check=True)
print(json.dumps({'python':sys.version.split()[0],'verdict':'PASS','delivery_hashes':len(delivery['outputs']),'curated_files':len(files),'native_updates':2,'verified_profile_updates':2,'formal_complete':False,'credential_value_or_private_key_matches':0,'runtime_config_diff':'empty','scope_diff_check':'PASS'}))
PY
```
