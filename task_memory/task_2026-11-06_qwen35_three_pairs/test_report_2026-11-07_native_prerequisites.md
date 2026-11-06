## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Record C readiness timeout, continuous loading progress, exact cleanup chronology and per-pair startup wait verification. |
| 2026-11-07 | Confirm repaired Ray startup on eight H800 GPUs and retain the distinct zero-update scheduler initialization failure and its exact RCA. |
| 2026-11-07 | Verify actual 27B teacher readiness, diagnose the 133-byte Ray socket failure, and validate the one-boundary local-root fix with 58 CPU checks. |
| 2026-11-07 | Record ineffective per-task correction, identify admission mutation with non-persisting server dry-runs, and validate all-single-node A/B configuration. |
| 2026-11-07 | Add real job identities, H800 allocation evidence, ConfigMap startup failure and controlled stop receipts. |
| 2026-11-07 | Record native qualification configuration, CPU worker/SDK checks, live quota observation and exact submission procedure. |

# Native H800 prerequisite execution

## Scope

These are P2 baseline/qualification jobs with `num_rollout=0`: each uses the frozen 24 monitoring prefixes, native student generation, frozen-teacher scoring and training-backend forward-only scoring. They perform no optimizer updates and save no HF checkpoint. Their diagnostic completions are additional prerequisite measurements, not part of the subsequent formal D9 update/monitoring budget. A successful probe is not a full P3/D8 verdict: updated/final versions, backward/optimizer capacity, learning behavior and real final HF reload remain to be tested.

The actual shared population and authorized model assets were verified by `exp-1106-233008-986003`; see the [P2 report](test_report_2026-11-06_p2.md). Data/export/evidence code is committed as `ede719c1`; native monitor and launcher code receive their own verified commit before GPU execution.

## Candidate resources, not measured capacity claims

Exact inputs: [native_probe_config.json](native_probe_config.json).

| Pair | Student allocation | Independent teacher allocation | Total GPUs |
| --- | --- | --- | ---: |
| A | 8 H800, trainer TP2/CP1/PP1; four TP2 rollout engines; 64 CPU, 512,000 MiB | 27B on 2 H800, TP2; 16 CPU, 128,000 MiB | 10 |
| B | Same 4B student layout as A, independent state and artifacts | 35B-A3B on 2 H800, TP2; 16 CPU, 128,000 MiB | 10 |
| C | 27B on 8 H800, trainer TP4/CP1/PP1; two TP4 rollout engines; 64 CPU, 768,000 MiB | Full 397B-A17B on two 8-H800 nodes, TP16; each 64 CPU, 512,000 MiB | 24 |

The matrix requests at most 44 GPUs for this prerequisite wave. These are candidate shapes based on the existing student recipes and indexed frozen-model storage sizes; they are not established minima or proof that 128K training fits. The 806.8 GB teacher source cannot fit on one 8×80 GB node; the two-node teacher must demonstrate actual load and forward behavior. No quantized or reduced-layer substitute is selected. Native optimizer/backward memory is not exercised by zero-update evaluation.

Each pair is one RJob with separate `student` and `teacher` task GPU allocations. Only the student is critical. Teacher head/address readiness and student-completion markers coordinate ordinary child processes; the worker does not call platform controls. The shared teacher and student are never put into the same student Ray GPU allocation. Pair C's teacher retains both native RDMA requests (`mellanox.com/mlnx_rdma:1`, `rdma/mlnx_shared:8`) and `DISTRIBUTED_JOB=true`. Student synchronization remains D5 CUDA IPC, not NCCL-direct qualification.

The two-GPU A/B teachers explicitly set `host_network=false` so their fixed HTTP/rendezvous ports remain isolated when sharing a physical node. Full-node students and the distributed C teacher keep native host networking. ResourceConfig defaults to host networking and only automatically disables it for partial-node allocations in its separate node-task-map branch; this ordinary task-spec path therefore requires the explicit JSON value (`steptron/exp/base_exp.py:4066,4442–4461`).

The current configuration makes `gang_start=false` explicit for both single-node tasks in A/B; both C tasks retain true. The intermediate teacher-only correction was ineffective because server admission reintroduced the map reference under the job-wide annotation, as shown below. The final server dry-run retains `stepmind.com/gang-group=true`, GPU/replica counts, local source and network modes. Job-level resource scheduling and successful container initialization remain distinct observations.

Native ResourceConfig resolution on the local Python 3.10.6 StepMind environment checked all six task shapes, replicas, role envs, criticality, image, mounts and C teacher RDMA values. Retained output: [native-resource-resolution-20261107.json](evidence/native-resource-resolution-20261107.json). The first inspection iterated dictionary keys and printed `None` attributes; it was not counted as validation. Correct inspection uses `for name, task_config in resource` and asserts the actual resolved fields.

The SDK automatically appends its existing public-tenant mount during resource iteration (`steptron/exp/base_exp.py:4383–4461`); this appears in the resolved receipt in addition to the two requested source-volume mounts. Task code does not read or write that directory. Native code pulling is disabled by the local-source `spawn_tasks` path. The approved model-source read exceptions and personal-write restrictions remain unchanged.

## Image and environment

Use the already CPU-qualified pinned Miles image in the JSON, with `/opt/sglang/bin/python3`. Preserve the verified prior H800 compatibility setup: prepend that image's `/usr/local/cuda-13.0/compat` to inherited `LD_LIBRARY_PATH` before Python starts. This exact requirement was established in the previous warmup's `test_report_2026-11-05_agent_opd.md`, including actual CUDA kernels; it is not a new worker install or retry fallback. No worker dependency installation is part of this path.

The parent `submit_qwen35.py` supplies local `/data/ycfeng` NFS source, H800/codesign, personal auth and the explicit image. `qwen35_pair_worker.py` places caches on worker-local storage and raw logs in the personal cloud run root. The student delegates to `run_qwen35_opd.py`. Existing deterministic-channel environment handling preserves matching platform `NCCL_*` values and rejects conflicts before launch instead of overwriting them.

## CPU verification

```bash
python3 tests/manual/agent_opd/submit_qwen35.py --config task_memory/task_2026-11-06_qwen35_three_pairs/native_probe_config.json --pair C --dry-run
env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_qwen35_pair_worker.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen35-pair-worker-native-config -o addopts=''
```

Dry-run: PASS, 24 GPUs for C, no submission. Worker tests: **14 passed, 7 warnings, 0.43 s**, Python 3.12.13, exit 0. They cover model/readiness identity, native argv, source boundaries, rendezvous order, faithful return codes, cancellation and owned-child cleanup. HTTP and GPUs remain fixtures; none of this proves native H800 behavior. Shapes are supplied by JSON rather than inferred from a pair label.

## Live quota observation

At **2026-11-06T16:12:15.747108Z** (Nov 7 local), a bounded personal Python `RJobClient._list_rjobs_kapis(quota_group='codesign', limit=256, phases=['Running','Pending','Starting'])` read returned **33 Running RJobs requesting 112 non-preemptible GPUs**. This is active requested capacity, not free quota; no free-GPU count is asserted. The 128-GPU value is the user's stated ceiling. Submission/scheduler placement is authoritative, and queued jobs are retained rather than duplicated. Receipt: [codesign-capacity-20261107.json](evidence/codesign-capacity-20261107.json).

## Submission procedure

From `/data/ycfeng`, initialize the runbook's proxy and personal credentials without displaying their values, set `STEPMIND_BACKEND=rjob`, `PYTHONPATH=/data/ycfeng/steptron`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONNOUSERSITE=1` and local `TMPDIR`. Submit each pair in its own long-lived local launcher using:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/submit_qwen35.py --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/native_probe_config.json --pair A
/data/ycfeng/tmp/stepmind-env/bin/python -u -B /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/submit_qwen35.py --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/native_probe_config.json --pair B
/data/ycfeng/tmp/stepmind-env/bin/python -u -B /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/submit_qwen35.py --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/native_probe_config.json --pair C
```

The script sets the required EXP_ID before constructing the backend and calls `spawn_tasks`, whose wait keeps the local launcher alive. Inspect each exact returned job for creator, both task shapes/mount sources, worker H800 devices, teacher native load/readiness, generated/scored monitoring artifacts, and terminal state. Actual observations follow; commands alone are not execution evidence.

## First native submissions and observed startup failure

Submission source: `ec127a1a`; local Python 3.10.6 StepMind environment and the exact configuration above. All were created at approximately 2026-11-07 00:58 local.

| Pair | RJob | Observed result |
| --- | --- | --- |
| A | `exp-1107-005818-695093` | Student Running with eight verified H800 devices; teacher Starting with `CreateContainerConfigError`; explicitly stopped at 01:22 before model execution. |
| B | `exp-1107-005818-919543` | Pending; explicitly stopped at 01:22 to avoid repeating A's identical two-GPU teacher startup configuration before diagnosis. |
| C | `exp-1107-005818-919546` | Pending at the recorded inspection; its local launcher remains alive. |

Creator, current-host NFS source, image and both task allocations were read back through the personal Python API. The initial scheduler reported six GPUs remaining while B/C queued; that is a timestamped scheduler observation, not a permanent free-capacity value.

Allocation receipt: [A student node](evidence/native-prerequisites/exp-1107-005818-695093/A/student-node.json). Observed hostname `gpu-h800-0128.host.platform.shaipower.com`, IP `10.191.8.5`, eight `NVIDIA H800, 81559 MiB, 570.124.06` devices, expected 4B source and pinned image. Platform startup log also records inherited `NCCL_*` values. This proves actual device allocation, not model loading, CUDA scoring, 128K capacity or D8 numerical acceptance.

At 2026-11-06T17:17:48.546198Z, the exact teacher replica was scheduled on `gpu-h800-0057.host.platform.shaipower.com`, host IP `10.191.5.7`, pod IP `100.98.76.67`. Container status:

```text
state.waiting.reason = CreateContainerConfigError
state.waiting.message = configmaps "exp-1107-005818-695093-teacher" not found
started = false
restartCount = 0
```

The matching platform event reports the same missing ConfigMap. Evidence: [startup status and events](evidence/startup-reason-exp-1107-005818-695093-teacher-cfcd2084.json), [replica summary](evidence/startup-exp-1107-005818-695093.json), [student startup log](evidence/startup-exp-1107-005818-695093-student-cfcd2084.log). The teacher produced no process log. This is a platform/container initialization failure before Python or SGLang, not evidence of a Qwen, CUDA or model-capacity failure.

The local SDK at `/data/ycfeng/tmp/stepmind-env/lib/python3.10/site-packages/brainpp/rjob/struct.py:775–779` injects `envFrom.configMapRef=<rjob>-<task>` whenever that task has `gang_start=true`. The missing map's generation condition is not yet verified. The `host_network=false`/gang interaction is under investigation; no causal claim beyond the observed missing ConfigMap is accepted yet.

Controlled resource release used the required existing wrapper:

```bash
bash /data/ycfeng/steptron/playground/users/ycfeng/tools/rjob_stop.sh --creator i-fengyicheng --reason "P2 native prerequisite cannot start: A teacher CreateContainerConfigError, task ConfigMap absent; hold identical A/B two-GPU teacher configuration for diagnosis before retry. No optimizer updates started." exp-1107-005818-695093 exp-1107-005818-919543
```

The wrapper verified both creators and codesign quota before stopping them. Both native launchers subsequently printed `QWEN35_PAIR_FINISHED ... stopped`; exit 0 is not classified as successful qualification. Audit records are retained in `/data/ycfeng/tmp/rjob-stop-audit.log`. C was not stopped. No optimizer update, completed monitoring population, learning metric or HF export is claimed from these attempts.

A's retained [student finally receipt](evidence/native-prerequisites/exp-1107-005818-695093/A/student-finished.json) reports `status=failed`, `returncode=null`, `error_type=SystemExit`, `reason=143`. This is retained alongside the controlled-stop evidence; it is not a successful native training result.

**Result:** startup qualification FAIL for A; B deliberately held before the same startup path; C unfinished. Repair the established launch cause, verify the resolved SDK payload and actual container startup, then resume affected qualification. Preserve the approved finite formal-run budget.

## First configuration correction: local serialization passed, admission failed

The original single-node teachers unnecessarily inherited the trainer's gang-start ConfigMap dependency. The failed replica's actual container already contains direct `KUBEBRAIN_RJOB_NAME`, `KUBEBRAIN_REPLICA=0` and `KUBEBRAIN_REPLICA_TOTAL=1` environment entries; the application's independent head/ready markers provide its rendezvous. See [the retained actual replica inspection](evidence/configmap-investigation-exp-1107-005818-695093.json). No platform address value is invented or overridden.

Supporting platform documents, read as the authenticated user:

- [RJob ConfigMap waiting diagnosis](https://wvixbzgc0u7.feishu.cn/docx/Z0jQdtdf0ontxvx8yiTc3HJynbh), revision 727: gang-start generates the map; required network information can delay it, including non-host-network Multus data.
- [RJob multi-task tests](https://wvixbzgc0u7.feishu.cn/wiki/NpOWwvm5NiIecnk3YExc2qhnnQg), revision 689: records missing ConfigMaps with gang-start and task-level configuration. This older example is supporting evidence, not proof of the current controller's internal fault.

The first document's diagnostic endpoint could not be queried because `sys-platform-k8s.iap.platform.shaipower.com` does not resolve on this host. Therefore the underlying missing network field/controller condition is not claimed as diagnosed. The task-owned correction is to select native non-gang mode for a standalone one-node teacher, retaining its isolated pod networking and all GPU/model/workload settings. The two-node C teacher retains gang-start, host networking and RDMA. No runtime producer/training code was changed.

Changes: `submit_qwen35._task_specs` passes the explicit per-resource `gang_start`; the JSON sets false only for A/B teachers. Direct native `ResourceConfig -> RJob -> Job.to_k8s_template('shai-core')` verification used Python 3.10.6 without submission. All six serialized task contracts PASS: A/B teacher `envFrom=[]`; other tasks retain their expected map reference; replica/GPU counts and host-network settings match the JSON; the pair gang-group label remains true. Evidence: [native serialized payload checks](evidence/native-configmap-payload-20261107.json).

Verification environment and entrypoint:

```bash
PYTHONPATH=/data/ycfeng/steptron PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 EXP_ID=qwen35-configmap-verification TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/tmp/stepmind-env/bin/python -B - <<'PY'
import json, runpy
from pathlib import Path
from steptron.exp.base_exp import ResourceConfig
from steptron.utils.stepmind import RJob
module = runpy.run_path('/data/ycfeng/sota-engine/miles/tests/manual/agent_opd/submit_qwen35.py')
path = Path('/data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/native_probe_config.json')
config = json.loads(path.read_text())
for pair in config['pairs']:
    resource = ResourceConfig(image=config['image'], positive_tags=[config['gpu_tag']], extra_requirements=[], mounts=config['mounts'], envs={}, command='{COMMAND}', task_specs=module['_task_specs'](config, pair), preemptible=config['preemptible'])
    resource.exp_name = f'qwen35-{pair.lower()}-payload-only'
    job = RJob(resource.exp_name, config['charged_group'], resource, exp_id=resource.exp_name)
    job.meta.name = resource.exp_name
    for name, leaf in resource:
        job.add(module['_worker_command'](config, path, pair), task_name=name, cfg=leaf)
    payload = job.job.to_k8s_template(namespace='shai-core')
    assert payload['metadata']['labels']['stepmind.com/gang-group'] == 'true'
    for role, task in payload['spec']['taskSpecs'].items():
        expected = config['pairs'][pair][role]
        pod = task['template']['spec']
        container = pod['containers'][0]
        refs = [{'configMapRef': {'name': f'{resource.exp_name}-{role}'}}] if expected['gang_start'] else []
        assert container['envFrom'] == refs
        assert pod['hostNetwork'] == expected['host_network']
        assert task['replicas'] == expected['nodes']
        assert int(container['resources']['limits']['nvidia.com/gpu']) == expected['gpus_per_node']
PY
```

The executed check also serialized its Python version and the six observed rows into the linked JSON. The first inspection tried importing `tests.manual` alongside Steptron's distinct `tests` package and failed before construction with `ModuleNotFoundError`; using `runpy.run_path` on the exact standalone submitter resolved that inspection-only namespace collision. No package or worker environment was altered. **Corrected limit:** this proves only the local representation. The subsequent API readback disproved removal of the dependency from the actual submitted object.

## Admission mutation and second configuration correction

The first correction was committed as `f9966cdf`. A `exp-1107-015013-220777` and B `exp-1107-015014-617751` were created at 01:50 local, but both stored objects still referenced their teacher ConfigMap. The initial verification asserted before writing its receipt; filtered exact objects were subsequently recovered into [A](evidence/platform-exp-1107-015013-220777.json) and [B](evidence/platform-exp-1107-015014-617751.json). Both were stopped while Pending at 01:57 through the required wrapper, before GPU allocation:

```bash
bash /data/ycfeng/steptron/playground/users/ycfeng/tools/rjob_stop.sh --creator i-fengyicheng --reason 'P2 corrected A/B submission readback still contains teacher ConfigMap envFrom despite native local serialization with gang_start false. Stop queued incompatible submissions before allocation; diagnose exact full submission pipeline. No optimizer updates.' exp-1107-015013-220777 exp-1107-015014-617751
```

Full `spawn_tasks -> RJobBackend -> RJobController.submit` interception still showed teacher `gang_start=false` and `envFrom=[]` immediately before the client/API call, with the actual local NFS source: [full-chain capture](evidence/configmap-full-pipeline-capture-20261107.json). Client `validate` is a no-op; submission serializes this object directly. This narrowed the change to the server boundary.

At 02:03, actual server-side dry-runs isolated the cause:

| Input configuration | Before admission | After admission | Persisted job |
| --- | --- | --- | --- |
| Student true, teacher false | Root gang-start annotation true; teacher reference empty | Teacher `<job>-teacher` ConfigMap reference inserted | No: GET404 |
| Both single-node tasks false | No root gang-start annotation; both references empty | Both references remain empty | No: GET404 |

Evidence: [admission before/after](evidence/configmap-admission-dry-run-20261107.json). This is observed server mutation, not an inference from the old documentation. The underlying reason why the original map was never generated remains separate and unproven.

The JSON now sets false for **both A/B student and teacher**, since each is a single-node task with its own application rendezvous. C remains true for both tasks, including its two-node teacher. At 02:07 the exact final A and B configuration both PASS server admission: no root gang-start annotation or ConfigMap refs; pair gang-group label true; expected host networking, replicas, GPUs and `100.96.128.195:/data/ycfeng:/data/ycfeng` retained. All dry-run names return GET404: [final admission checks](evidence/configmap-admission-final-20261107.json).

The checks used the same Python 3.10.6 environment and proxy/auth setup as submission. The verification intercepted `RJobController.submit` after the complete `spawn_tasks` construction; for its native `job.job.to_k8s_template(namespace=client.namespace)` body, the exact server calls were:

```python
admitted = client.api.create_namespaced_custom_object(
    group=client.group, version=client.version, namespace=client.namespace,
    plural=client.plural, body=body, dry_run="All", _request_timeout=25,
)
assert "kubebrain.brainpp.cn/gang-start" not in admitted["metadata"]["annotations"]
assert admitted["metadata"]["labels"]["stepmind.com/gang-group"] == "true"
for role, task in admitted["spec"]["taskSpecs"].items():
    expected = config["pairs"][pair][role]
    pod = task["template"]["spec"]
    assert not pod["containers"][0].get("envFrom", [])
    assert pod.get("hostNetwork", False) == expected["host_network"]
    assert task["replicas"] == expected["nodes"]
    assert int(pod["containers"][0]["resources"]["limits"]["nvidia.com/gpu"]) == expected["gpus_per_node"]
    assert task["template"]["metadata"]["annotations"]["kubebrain.brainpp.cn/filestore-volume"] == "100.96.128.195:/data/ycfeng:/data/ycfeng"
# An ApiException with status == 404 is required; any persisted object fails this check.
client.api.get_namespaced_custom_object(
    group=client.group, version=client.version, namespace=client.namespace,
    plural=client.plural, name=body["metadata"]["name"], _request_timeout=15,
)
```

No native worker environment, training implementation or controller was patched. The verified admission behavior, source links and runtime limitation were added to `/data/ycfeng/stepfun-env-handbook/stepmind-python-rjob.md`; that handbook directory has no Git repository and was not initialized. **Admission contract PASS; actual container/model execution still INCOMPLETE.** C's existing launcher is preserved. The latest recorded scheduler capacity before these corrections was zero H800; see [capacity receipt](evidence/codesign-capacity-before-configmap-retry-20261107.json).

## Admitted corrected jobs — PASS at submission scope

Configuration commit `5e9f5551` was submitted at 02:14 local through the same long-lived Python RJobBackend commands. A is `exp-1107-021450-020231`; B is `exp-1107-021450-039035`. Actual stored API objects now PASS all identity/source/resource checks: `i-fengyicheng`, pinned digest, expected NFS and network modes, per-task GPU/replica counts, no root gang-start annotation, **empty envFrom on both tasks**, and retained `stepmind.com/gang-group=true`. Receipts: [A](evidence/platform-exp-1107-021450-020231.json), [B](evidence/platform-exp-1107-021450-039035.json).

Both are Pending at the readback. The scheduler explicitly reports eight remaining H800 against ten requested per A/B pair. C remains Pending with 24 requested GPUs, as recorded immediately before submission in [the capacity observation](evidence/codesign-capacity-before-admission-fixed-launch-20261107.json). All three launchers remain long-lived; this is not worker-startup, numerical, training or export acceptance.

## Actual startup and Ray socket-path failure

A `exp-1107-021450-020231` subsequently started both native containers. [Student devices](evidence/native-prerequisites/exp-1107-021450-020231/A/student-node.json) show eight H800 GPUs on `gpu-h800-0210.host.platform.shaipower.com`; [teacher devices](evidence/native-prerequisites/exp-1107-021450-020231/A/teacher-node-0.json) show two. All report 81,559 MiB and driver570.124.06. The [teacher-ready receipt](evidence/native-prerequisites/exp-1107-021450-020231/A/teacher-ready.json) binds the actual configured 27B model and external URL. Its [tail](evidence/native-prerequisites/exp-1107-021450-020231/A/teacher-tail-0.log) shows native warmup completion and health/model-info HTTP200 at18:46:13Z. **The gang-start correction therefore passed actual container startup.** This is not 128K scoring or student-training acceptance.

At18:47:23Z, the [student tail](evidence/native-prerequisites/exp-1107-021450-020231/A/student-tail.log) instead reports:

```text
OSError: validate_socket_filename failed: AF_UNIX path length cannot exceed 107 bytes: /var/tmp/qp-exp-1107-021450-020231-A-student-0/qo-1107-021450-020231/ray/session_2026-11-06_18-47-23_102563_1114/sockets/plasma_store
```

Parent executed this deterministic CPU feedback loop before changing code; Python3.12.13 reproduced the same OSError, exit1, with `observed socket path bytes=133`:

```bash
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
from ray._private.utils import validate_socket_filepath
path='/var/tmp/qp-exp-1107-021450-020231-A-student-0/qo-1107-021450-020231/ray/session_2026-11-06_18-47-23_102563_1114/sockets/plasma_store'
print(f'observed socket path bytes={len(path.encode())}',flush=True)
validate_socket_filepath(path)
PY
```

The direct exception and native validator establish the cause, so no speculative multi-hypothesis or environment-install loop was needed. `qwen35_pair_worker._student_command` passed an already job-scoped temporary directory as `--local-root`; `run_qwen35_opd._run` then appended its own job directory. The fix passes `local.parent` through the existing argument. The student CLI retains its own job isolation. Native worker/package code, dataset/model/numerical settings and startup timeout were not changed.

### Failure/cleanup chronology

- Student container exit1:18:47:28Z; `reason=Error`, `message=user command: exit status 1`.
- System stop timestamp18:47:30Z; `Some critical tasks failed.` Teacher subsequently receives termination.
- RJob Failed:18:47:42Z, `Tasks with failed status: [student]`.
- Local launcher cleanup `Job Stop`:02:47:45 local (UTC+8), after the original failure.

The exact job/replica UIDs, owner binding, container/image/node and timestamps are retained in [selected objects](evidence/ray-path-failure-rca-objects-20261107.json). The eight source queries all succeeded; [query index](evidence/ray-path-failure-rca-index-20261107.json) and [selected events/audits](evidence/ray-path-failure-rca-summary-20261107.json) retain coverage. Live job/replica event counts were2/0; historical counts9/0; all-operation audit counts20/1, with `data` absent; no existing DeepScan flow. Returned events contain startup/queue and subsequent teacher-close records, not a positive preemption/OOM event. The initiating application exception is preserved independently; a missing explicit manual-stop actor remains UNKNOWN rather than inferred from a later controller update. Raw incident/response/audit files remain under `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-exp-1107-021450-020231`.

After the standard runbook proxy setup, the exact collector command was:

```bash
PYTHONPATH=/data/ycfeng/steptron PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
  exp-1107-021450-020231 --replica exp-1107-021450-020231-student-cfcd2084 \
  --expected-creator i-fengyicheng --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
  --start 2026-11-06T18:46:50Z --end 2026-11-06T18:47:50Z --timeout 35 \
  --output /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-exp-1107-021450-020231
```

At02:49 local, B was Running with the same already-imported faulty caller, while C was Pending ([API observation](evidence/platform-after-ray-path-failure-20261107.json)). B had no teacher-ready/student-launch receipt and was stopped at02:52:39 to avoid the known identical student failure:

```bash
bash /data/ycfeng/steptron/playground/users/ycfeng/tools/rjob_stop.sh --creator i-fengyicheng --reason 'P2 A native student failed before Ray startup: nested worker local-root produces 133-byte AF_UNIX socket path, above107. CPU native validator reproduced. B imported the same pair-worker launcher and has not produced teacher-ready/student-launch; stop before predictable student failure. No optimizer updates. Preserve C queued.' exp-1107-021450-039035
```

Its launcher confirmed Stopped at02:52:57. C keeps its existing queued job and local source mount; its future import will use the corrected source, whose actual Git state is recorded by the native student launch receipt.

### Scoped repair verification

Owner `QWEN-P2-PAIR-WORKER` changed only `qwen35_pair_worker.py:129` and its test module. Parent inspected the complete diff. The regression calls the actual student CLI and observes its chosen directory before worker initialization; it then invokes native Ray's validator with real session-name structure, the observed PID and a seven-digit PID. It checks two distinct job IDs without duplicating the CLI's directory-composition logic or starting Ray/GPU processes.

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
tests/fast/test_qwen35_pair_worker.py::test_native_student_ray_socket_paths_fit_and_remain_job_isolated \
-q -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/pytest-qwen35-pair-worker

# Green used the same command with cache_dir=.../pytest-qwen35-pair-worker-green.
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
tests/fast/test_qwen35_pair_worker.py tests/fast/test_qwen35_opd_launcher.py \
-q -o cache_dir=/data/ycfeng/tmp/opencode-v2-tmp/opencode/pytest-qwen35-pair-worker-full
```

Python3.12.13: regression before fix **1 failed**, after fix **1 passed/0.48s**; complete pair-worker/launcher checks **58 passed (15+43)/8.74s**. Corrected paths are95 bytes for the observed PID and98 for seven-digit PID, within107; job directories remain distinct. `git diff --check` PASS. **CPU repair PASS; actual repaired Ray startup and all original numerical/training/export gates remain unfinished.**

### Repaired-source submissions

Repair and selected failure evidence were committed as `bb297964`. Before submitting, [exact job/replica inspection](evidence/platform-before-ray-root-retry-20261107.json) confirmed old A Failed/Stopped and old B all Stopped. C remained Pending with eight available H800 reported in its queue annotation.

The unchanged runbook proxy/auth initialization and the same long-lived submit command above created:

| Pair | Current job | Actual admitted-object checks | Observed state |
| --- | --- | --- | --- |
| A | `exp-1107-030522-873302` | [PASS](evidence/platform-exp-1107-030522-873302.json) | Pending |
| B | `exp-1107-030522-896828` | [PASS](evidence/platform-exp-1107-030522-896828.json) | Pending |
| C | `exp-1107-005818-919546` | Original queued launcher retained | Pending at pre-submission observation |

Checks cover personal creator, current local machine's `IP:/data/ycfeng:/data/ycfeng` filestore annotation, exact image digest, role GPU/node/host-network shape, gang-group and absent A/B ConfigMap dependency. The first auxiliary inspection incorrectly searched for Kubernetes `nfs` fields in the RJob CRD and exited on an empty-source assertion; the established `spec.taskSpecs[role].template.metadata.annotations['kubebrain.brainpp.cn/filestore-volume']` inspection above then passed. That inspection error did not stop or modify any workload. Both A/B readbacks report eight remaining H800 for ten requested. Long-lived launchers remain active. Native repaired startup is still **UNVERIFIED**.

## Repaired Ray startup passed; zero-update optimizer initialization failed

Subsequent A `exp-1107-030522-873302` proves the Ray-root repair: [cluster.json](evidence/native-prerequisites/student/A/exp-1107-030522-873302/cluster.json) reports one live node at10.191.9.44 with8 GPUs. Ray session `session_2026-11-06_19-39-46_931208_1123` started successfully and launched the actual Megatron actors. Student model construction reached the optimizer setup path; this does not prove pretrained student weights finished loading or any score/update succeeded.

The [selected original traceback](evidence/scheduler-failure-native-trace-20261107.txt) comes from the completed personal cloud log `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/native-prerequisites/student/A/exp-1107-030522-873302.log` (5,702,926 bytes). Local filesystem cloud access is unavailable; read-only `ssh shai-ycfeng` succeeded on this attempt using its equivalent `/mnt/ws-jfs/ycfeng/...` path. A separate `timeout 12s ssh -o BatchMode=yes -o ConnectTimeout=8 shai-ycfeng 'id -un'` returned `i-fengyicheng`. Only bounded traceback lines were retained locally; the full log remains on personal cloud storage.

```text
miles/backends/megatron_utils/actor.py:244 init
  -> model.py:1015 build_model_and_optimizer
  -> model.py:246 setup_model_and_optimizer
  -> model.py:118 get_optimizer_param_scheduler
  -> /root/Megatron-LM/megatron/core/optimizer_param_scheduler.py:169
assert self.lr_decay_steps > 0
AssertionError
```

All eight trainer ranks report this initialization failure at19:45:48Z. The baseline-only command has `num_rollout=0`; the native builder derives `train_iters=0`, then default `lr_decay_iters=0`. The existing `debug_disable_optimizer` path returns the model with no optimizer/scheduler and is being verified for baseline-only execution. This is a launcher-mode contract defect, not evidence of a dependency/import failure. The formal100-update Adam configuration remains the required training path. Zero-update scoring cannot establish backward/optimizer memory capacity.

### Exact termination evidence

[Object binding](evidence/scheduler-failure-rca-objects-20261107.json): RJob UID `5742f4e6-d30b-4f10-8ca0-d7ed63c5f7b4`, student replica UID `00f03bb6-f811-4888-8629-0ff8251f98c2`, node `gpu-h800-0210.host.platform.shaipower.com`, personal creator and pinned image verified. Application failure precedes container exit1 at19:46:01Z, system-stop timestamp19:46:03Z (`Some critical tasks failed.`), RJob Failed19:46:16Z and local launcher cleanup03:46:18 local. The launcher cleanup did not initiate the scheduler assertion.

[Query index](evidence/scheduler-failure-rca-index-20261107.json) and [selected events/audits](evidence/scheduler-failure-rca-summary-20261107.json): all eight queries succeeded; live job/replica event counts2/0, historical5/0, audit18/1, existing DeepScan0, incident log rows1. All returned audit `data` fields were absent. Events show startup and subsequent teacher closure, with no positive preemption/OOM event in returned coverage. The [371-sample cgroup receipt](evidence/native-prerequisites/student/A/exp-1107-030522-873302/memory.json) reports peak sampled usage62,842,441,728 bytes, kernel high-water63,418,052,608 against536,870,912,000 limit, final failcnt0/oom_kill0. Ray's generic worker-exit message lists OOM among possibilities, but the specific observed cause is the Python scheduler assertion. Missing manual-stop actor/reason/request-time remain UNKNOWN; negative sampled evidence is not a complete kernel history.

With the runbook proxy initialized, the collector ran under Python3.10.6/brainpp2.8.6:

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -u -B \
/data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
exp-1107-030522-873302 --replica exp-1107-030522-873302-student-cfcd2084 \
--expected-creator i-fengyicheng --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
--start 2026-11-06T19:45:30Z --end 2026-11-06T19:46:30Z --timeout 35 \
--output /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-scheduler-exp-1107-030522-873302
```

[Concurrent platform observation](evidence/platform-after-native-ray-failure-20261107.json) showed B Starting and C Pending. B had no student-launch/teacher-ready receipt when the shared defect was identified. Parent stopped only B through `rjob_stop.sh --creator i-fengyicheng` at03:50:30 local with the recorded zero-update-scheduler reason; its launcher confirmed Stopped03:50:40. C's original queued launcher is retained. The in-scope correction/regression belongs to `QWEN-P2-LAUNCH`; repaired model scoring remains **UNVERIFIED**.

### Zero-update baseline correction and CPU regression

`QWEN-P2-LAUNCH` reused the existing `--debug-disable-optimizer` flag only when the task launcher selects `num_rollout=0`. Native `setup_model_and_optimizer` then returns model/None/None; native argument validation disables optimizer-state loading/saving. No positive scheduler duration is substituted. Formal100 preserves Adam/constant2e-6/no-warmup/betas0.9,0.98/zero-weight-decay, and native scheduler duration800 samples. Parent inspected the complete two-file diff; no core code or resource/configuration file changed.

The regression drives actual launcher output through the native setup/scheduler functions and a read-only reference Megatron scheduler class. GPU model/optimizer factories are CPU fixtures. A/B/C baseline cases failed on the original assertion before repair; formal100 cases passed. Subsequent tests run the production score RPC with no optimizer and preserve model values, masks, weight version and residency; the production driver performs exactly one initial eval/publication with no train/save/export calls.

| Check | Expected | Actual |
| --- | --- | --- |
| Native setup before repair, both budgets and all pairs | Baseline reproduces actual zero-duration assertion | 3 failed / 3 passed,4.42s — expected red |
| Same test selection after repair | Baseline returns no optimizer/scheduler; formal remains initialized | 6 passed,3.91s |
| Complete launcher file | Existing43 checks plus15 setup/scoring/driver regressions | 58 passed,10.14s |
| `git diff --check` | No patch whitespace errors | PASS |

Executed with Python3.12.13 and the existing CPU environment. `MEGATRON_PATH` supplies source only; it does not import packages from the reference environment:

```bash
MEGATRON_PATH=/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages \
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider \
tests/fast/test_qwen35_opd_launcher.py --tb=short
```

Red and first Green used the same command with `-k test_native_setup_for_baseline_or_formal_budget`. These checks do not establish actual HF loading, CUDA offload, optimizer capacity or H800 D8 values. Native model scoring is the next verification input; no further unrelated CPU test expansion is required.

### Independent C allocation

[Pre-retry states](evidence/platform-before-scheduler-retry-20261107.json) verify old A Failed/teacher Stopped and old B both Stopped. C proceeded independently. [Exact container states](evidence/platform-c-starting-20261107.json) and its [student](evidence/native-prerequisites/exp-1107-005818-919546/C/student-node.json), [teacher rank0](evidence/native-prerequisites/exp-1107-005818-919546/C/teacher-node-0.json), [teacher rank1](evidence/native-prerequisites/exp-1107-005818-919546/C/teacher-node-1.json) receipts verify24 H800 across gpu-h800-0210/0071/0223,8 per node,81,559MiB/device, driver570.124.06 and the pinned image. Both teacher logs reached TP0–15 model construction at20:02:16Z; head began loading94 shards. Full teacher readiness is not yet established. The original local C launcher remains responsible for its lifetime; later student startup reads the repaired mounted launcher.

### Actual resubmission after the zero-update correction

Source `4a1364ca` was committed after the58 passing checks. Invocation from the Miles checkout failed the existing pre-submission guard (`Run from the local NFS source directory: /data/ycfeng`); neither attempt created a job. Using the required `/data/ycfeng` workdir and the same absolute submitter/config paths created A `exp-1107-041127-564012` and B `exp-1107-041127-467864` at04:11:27 local. Both long-lived launchers continue.

[A actual admission](evidence/platform-exp-1107-041127-564012.json) and [B actual admission](evidence/platform-exp-1107-041127-467864.json) pass personal identity, current-machine NFS source, pinned digest image,8+2 H800 resources, host-network shape, gang-group and no ConfigMap dependency. Both are Pending, with queue remaining H800=8. The read-only inspector first indexed the optional `hostNetwork` field and raised KeyError where native Kubernetes omits false; reading its documented false default completed the check without changing a job. Source/mount/resource admission is **PASS**; repaired native model scoring is **UNVERIFIED**.

Document link validation passed59 local references after its first naive regex mistook fenced Python subscription/call syntax for a Markdown link; the corrected check excludes code. These auxiliary inspection errors did not propagate into any workload.

## C readiness deadline expired during progressing weight loading

The original C job `exp-1107-005818-919546` failed at 04:21 local. Its [student result](evidence/native-prerequisites/exp-1107-005818-919546/C/student-finished.json) records `TimeoutError: RJob rendezvous did not publish .../teacher-ready.json`, with no student subprocess return code. The student log is absent because `_run_student` opens it only after readiness; this was confirmed after the first bounded remote inspection encountered that missing path. No student generation, score or update occurred.

Both [teacher status 0](evidence/native-prerequisites/exp-1107-005818-919546/C/teacher-status-0.json) and [status 1](evidence/native-prerequisites/exp-1107-005818-919546/C/teacher-status-1.json) report a live child before cleanup (`returncode=null`), followed by wrapper `SystemExit:143` and child shutdown return code -15. [Teacher tail 0](evidence/native-prerequisites/exp-1107-005818-919546/C/teacher-tail-0.log) retains continuous progress from 0 to 19/94 shards in 18:09 elapsed; [tail 1](evidence/native-prerequisites/exp-1107-005818-919546/C/teacher-tail-1.log) shows other TP ranks loading without a returned exception. These observations establish a readiness deadline failure while loading was progressing, not full teacher readiness or a measured total loading time.

### Exact chronology and query coverage

[Bound objects](evidence/c-readiness-rca-objects-20261107.json) identify the same personal RJob UID `7d7c069f-f0a2-47f5-85db-34da52395b1b`, student replica UID `b64ef802-0055-4bdb-9836-df33ba615ada`, node gpu-h800-0210 and pinned image:

| Observation | UTC |
| --- | --- |
| Student container starts | 19:50:50 |
| All teacher TP ranks log weight-load begin | 20:02:16 |
| Student exits 1 after readiness timeout | 20:21:08 |
| System-stop timestamp; both teacher pods deleted | 20:21:09 |
| Teacher replicas close | 20:21:10 |
| RJob Failed | 20:21:15 |
| Local launcher cleanup | 20:21:15.688 |

The student clock starts in `_run_student` after its initialization; the container-to-loading interval of 686 seconds is a conservative observed allowance, not an exact timer-start measurement. Tqdm provides elapsed loading times, not individual absolute timestamps.

All eight [queries](evidence/c-readiness-rca-index-20261107.json) succeeded. [Selected events/audits/progress](evidence/c-readiness-rca-summary-20261107.json): live job/replica events 4/0, historical 16/0, all-operation audits 49/1, existing DeepScan 0, incident-log rows 1. Pagination completed for event/audit/flow queries. All 50 audit data fields were empty; retained text was checked against personal credential values. Returned coverage contains no positive initiating OOM/preemption evidence. There is no C kernel memory time series here; absent manual-stop actor/reason/request time remain UNKNOWN. Teacher deletion and launcher cleanup followed the application timeout.

With the documented personal proxy initialized, Python 3.10.6/brainpp 2.8.6:

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -u -B \
/data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
exp-1107-005818-919546 --replica exp-1107-005818-919546-student-cfcd2084 \
--expected-creator i-fengyicheng --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
--start 2026-11-06T20:19:30Z --end 2026-11-06T20:21:30Z --timeout 35 \
--output /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-readiness-exp-1107-005818-919546
```

Original full teacher logs remain at `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/native-prerequisites/teacher/C/exp-1107-005818-919546/rank-{0,1}.log`; read-only SSH accessed their `/mnt/ws-jfs/ycfeng/...` equivalents with bounded 18KB tails. Local copies retain only the already-created selected 8KB worker tails. [Subsequent platform check](evidence/platform-after-c-readiness-failure-20261107.json) confirms C student Failed and both teachers Stopped; A/B are independently Pending with no replicas.

### Measured wait-policy correction and CPU verification

Hypothesis: a common 1,800-second startup wait cannot cover this full teacher's observed load plus staggered container startup. A fake-clock run that still expires at 1,800 seconds despite selecting C's longer configured wait would disprove the correction. The actual loops are retained, with GPU/process/HTTP boundaries simulated.

The observed first 19 shards take 1,089 seconds, giving an average-rate projection of 5,387.68 seconds for 94 shards. The slowest observed shard interval is 79 seconds; `94*79+686=8,112` seconds includes observed container startup but excludes final service warmup. C therefore receives a bounded **9,000-second (2.5-hour) startup wait** for the next full-load probe. This is an estimate from partial progress, not a measured full-loading bound or a guarantee. A/B retain 1,800 seconds. No automatic extension or readiness bypass was added.

`qwen35_pair_worker._load_config` moves the selected pair's required timeout into the existing shared runtime config once. The JSON removes the former common input and owns one value under each pair. Existing waits, native child-error propagation, `/health` and exact `/model_info` identity checks remain authoritative. [Actual config validation](evidence/c-startup-config-check-20261107.json) resolves 1800/1800/9000 and confirms all other model/resource/workload fields equal the committed configuration.

| Check | Expected | Actual |
| --- | --- | --- |
| Regression before correction | C still expires under the old shared wait | 4 failed / 3 passed — red |
| Same selection after correction | Late readiness accepted only after health/identity; timeout and native error still propagate | 7 passed, 0.66s |
| Owner combined run without reference Megatron path | Available tests pass; native fixture dependency reported | 70 passed / 12 skipped, 9.66s |
| Parent combined run with existing read-only reference path | All affected checks execute | **82 passed, no skips, 10.73s** |
| Actual JSON, role shapes and workload comparison | Only timeout ownership/C value changes | PASS |

Python 3.12.13; exact complete command:

```bash
MEGATRON_PATH=/data/ycfeng/envs/verl-agent-opd-megatron-sglang/lib/python3.12/site-packages \
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
tests/fast/test_qwen35_pair_worker.py tests/fast/test_qwen35_opd_launcher.py \
-q -p no:cacheprovider \
--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-startup-final-$(date +%s)-$$ --tb=short \
2>&1 | tee /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-startup-final-20261107.log
```

Readiness at simulated second 8,112 precedes student launch; no readiness by second 9,000 fails. A native teacher error code 23 propagates at simulated second 1,000. These tests establish wait semantics only. Actual full teacher loading, scoring, training capacity and D8 numerical qualification remain **UNVERIFIED**.

### Submitter integration closure

Parent's real CLI check with the changed C JSON reproduced `TypeError: 'int' object is not subscriptable` in `submit_qwen35._task_specs`: its loop treated every pair key as a resource role. No platform job was created. Three new A/B/C regressions were red with the same error; the caller now constructs only the two supported student/teacher roles. This is the second consumer of the changed configuration shape, not a new scheduling mode.

```bash
python3 -B tests/manual/agent_opd/submit_qwen35.py \
--config task_memory/task_2026-11-06_qwen35_three_pairs/native_probe_config.json --pair C --dry-run

# Red: 3 failed, 0.51s; all reproduced the integer-as-role error.
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
tests/fast/test_qwen35_pair_worker.py -k startup_budget_is_not_a_submitted_role \
-q -p no:cacheprovider --tb=short
```

The complete command from the preceding section was rerun after the submitter repair, changing the basetemp prefix to `qwen-startup-submit-final-` and the retained log to `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-startup-submit-final-20261107.log`: **85 passed, 0 skipped, 10.94s**, Python 3.12.13. Real CLI `--dry-run` for each pair then returned exactly student/teacher tasks, 10/10/24 GPUs and `submitted=false`; [retained outputs](evidence/c-startup-submit-dry-run-20261107.json) establish the final config-to-submission contract. Final CPU/config acceptance is PASS; native completion remains unverified.
