## Modification History

| Date | Change |
| --- | --- |
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
