## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Primary prelaunch inspection selects1H200,4 CPUs,mem_gb16,1024/64MiB cases and a600-second whole-worker command limit. |
| 2026-11-10 | Prepare the D38 one-H200 allocator-order diagnostic and record CPU validation only; native execution remains pending with the primary agent. |

# Allocator/TMS probe: CPU preparation

## Result and ownership

**CPU preparation PASS; GPU execution PENDING.** TaskID: `profile-h200-allocator-probe-20261110`.

Owned deliverables:

- `tests/manual/agent_opd/probe_tms_allocator.py`
- `tests/fast/test_tms_allocator_probe.py`
- This report.

The implementation agent performed no platform, SSH, network, GPU, or cloud operations. The primary owns admission, submission, the existing launcher, its worker-script timeout of at most 600 seconds excluding startup, monitoring, and native result acceptance. No model/training code or formal configuration was changed. This diagnostic is not a training gate.

## Mechanism and reproduction boundary

Two serial, separate subprocesses compare exactly one ordering difference:

1. `late_moments`: allocate and release the supplied BF16 transient, then call native Adam `init_state_fn`.
2. `early_moments`: call the same callback before allocating and releasing the same transient.

The worker uses `_get_megatron_optimizer_based_on_param_groups(..., skip_megatron_wrapping=True)` from its installed Megatron, receiving the real raw FusedAdam and callback. A missing callback, generic PyTorch fallback, or unsupported optimizer is a diagnostic failure; there is no generic-zeros substitute. The actual optimizer class, factory/callback source path, source hash and line numbers are recorded.

The callback must create exactly two zero FP32 moments of the requested size and be storage-idempotent. Persistent state is then filled with deterministic, exactly representable constants. Both cases perform the native `clear_memory()` sequence before pausing all TMS tags. The CPU backup views, restored GPU values, and virtual pointers must match exactly. A post-roundtrip native FusedAdam step verifies that it can consume the callback-created state.

The FP32 parameter represents a master-parameter shard. It and the moments use the formal default-tag CPU-backup context. No BF16 DDP param buffer is allocated; formal offload forces both param/grad buffer CPU-backup-disable flags at `miles/utils/arguments.py:1534–1536`. The temporary gradient used only after roundtrip follows `region(tag="grad_buffer", enable_cpu_backup=False)`.

**Boundary:** the late case does not run a full-model backward followed by FusedAdam's internal lazy initialization. It exercises Megatron's real state-initialization callback at the hypothesized allocation seam. It cannot establish which real tensor kept a formal transient segment live, reproduce the 500 GiB node OOM, or prove the formal run's root cause.

## Native environment and retained inputs

Inputs are read locally, not from model/cloud directories:

- Actual formal launch: `evidence/formal-h200-112k-20261110/full/student/A/exp-1110-140032-491115/launch.json`.
- Exact-image TMS source/identity: `evidence/native-tms-source-20261110/source.json` and its `python-source/` files.
- Recorded image: `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`.

The stdlib-only parent launches each case. That case calls the existing `miles.ray.specs.train.compute_trainer_env_vars` owner using the retained flags and native config defaults, then re-execs Python with its `LD_PRELOAD` and TMS settings before allocating tensors. Native `train_memory_margin_bytes` is also read from the launch/default owner, not tuned by the probe.

The retained launch contains no explicit `--train-env-vars` or PYTORCH allocator flags. The probe refuses nonempty inherited `PYTORCH_ALLOC_CONF`, `PYTORCH_CUDA_ALLOC_CONF`, or `PYTORCH_NO_CUDA_MEMORY_CACHING` unless declared in that launch's train-env-vars. It records the resulting values and requires the native caching allocator. This matches the retained explicit/default configuration; the receipt is not a retrospective dump of every image environment variable.

Before the allocation experiment, the worker checks TMS0.0.10 against the receipt, including the installed Python entrypoint and selected preload ELF hashes. The retained cu13 preload ELF SHA256 is `99bbe5e2df91c5f9e5cd0a65e3947ceb3304bbb6a2b6ad539f00326cc583dcd4`. It verifies active default-tag pinned CPU backup, disk backup disabled, exactly one CUDA-visible H200, and exactly one H200 in `nvidia-smi` output. Those checks are **not executed locally**.

## Measurements and interpretation

Each case records `baseline`, `transient_released`, `before_cleanup`, `before_pause`, `paused`, and `after_resume`:

- CUDA allocated/reserved/inactive-split bytes and device free/total bytes.
- Own `/proc/self/status` VmRSS and VmLck bytes.
- Resolved v1/v2 memory cgroup, current bytes and full small `memory.stat` counters.
- At `before_pause`, small CUDA segment/block descriptions without stack frames or a history dump.
- Remembered transient virtual range; persistent parameter/moment/scratch ranges and exact moment-state bytes.

The retained CUDA Python API exposes no total allocated/backup byte counter. Those fields are explicitly `null`/unavailable; no guessed native symbols are called. `get_cpu_backup(..., zero_copy=True)` verifies values, not total native shadow allocation size. CUDA segment sizes and process/cgroup deltas are not relabeled as measured TMS backup bytes. VmLck may omit CUDA-pinned pages; cgroup deltas include other processes and file cache.

The summary reports the observed ordering contrast only when late moments reuse the remembered transient range and retain more reserved/inactive-split bytes with equal moment-state bytes. RSS and cgroup pause deltas are reported separately. Identical results produce `complete` with `allocator_order_effect_observed=false`, not a forced failure or a changed test. `formal_run_root_cause_proven` is always false.

Independent failures are retained per case, with return code and elapsed time, while the other case still runs. Updates use same-directory atomic replacement so an abrupt subprocess exit retains its last complete receipt. Existing output files are never overwritten by a new invocation. The parent has no retry/deadline framework; the primary's existing launcher enforces the overall worker-script limit.

## CPU validation

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`.

### Parser, syntax, and dependency isolation

System Python: `/usr/bin/python3`, Python 3.10.6.

```bash
timeout 60s python3 -B tests/manual/agent_opd/probe_tms_allocator.py --help
```

Observed exit 0 with all five required public inputs. An inline `ast.parse` check covered both new Python files. An isolated import through `importlib.util.spec_from_file_location` verified that `torch`, `ray`, `megatron`, and `torch_memory_saver` were absent from `sys.modules`. Positive inputs 1024/64 parsed unchanged. Direct local metadata reading resolved this host's current v1 memory cgroup. **PASS**; none of these checks initialized CUDA.

The initial system-Python pytest/ruff attempts failed with `No module named pytest` and `No module named ruff`. No dependency was installed. The existing task CPU environment was used next. Ruff, Black and isort are unavailable there and on PATH; formatter/linter validation is **NOT RUN**.

### Persistent CPU regression checks

Existing environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python 3.12.13; no conda activation or environment changes.

```bash
timeout 60s env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts='' -q \
  tests/fast/test_tms_allocator_probe.py \
  --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-h200-allocator-probe-20261110-pytest-acceptance
```

Expected: all CPU cases pass without native/CUDA execution. Actual: **16 passed, 2 existing Swig deprecation warnings in 0.38s; PASS**. Coverage includes positive sizes, isolated help, v1/v2/private-namespace cgroup resolution, small snapshots, ordering/negative-result comparisons, independent failure retention, refusing overwrite, native environment-owner re-exec wiring with preserved platform environment, bootstrap failure receipts, and interrupted atomic writes. Earlier iterations passed 13 and 15 cases before the final fault-injection check was added. Final AST/import checks also passed with worker dependencies absent from `sys.modules`.

## Primary native invocation

Run from the mounted repo root with the same pinned image and its `/opt/sglang/bin/python3`. The launcher must prepare worker-local cache directories and set the following environment; preserve platform NCCL values and the assigned one-GPU visibility. Do not manually tune allocator flags or set a different preload mode.

```bash
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export PYTHONPATH="$REPO:/root/Megatron-LM"
export TMPDIR="$WORKER_LOCAL_ROOT/tmp"
export TRITON_CACHE_DIR="$WORKER_LOCAL_ROOT/triton"
export TORCHINDUCTOR_CACHE_DIR="$WORKER_LOCAL_ROOT/inductor"
export CUDA_CACHE_PATH="$WORKER_LOCAL_ROOT/cuda"
export TORCH_EXTENSIONS_DIR="$WORKER_LOCAL_ROOT/torch-extensions"

/opt/sglang/bin/python3 -B "$REPO/tests/manual/agent_opd/probe_tms_allocator.py" \
  --launch-receipt "$TASK/evidence/formal-h200-112k-20261110/full/student/A/exp-1110-140032-491115/launch.json" \
  --native-source-receipt "$TASK/evidence/native-tms-source-20261110/source.json" \
  --transient-mib "$TRANSIENT_MIB" --moment-mib "$MOMENT_MIB" \
  --output-dir "$PROBE_OUTPUT"
```

`REPO` is the mounted workspace root; `TASK=$REPO/task_memory/task_2026-11-08_qwen35_full_kl_nll`. `WORKER_LOCAL_ROOT` must be a fresh directory under the retained worker-local `/var/tmp` root. `PROBE_OUTPUT` must be a new directory in the mounted local workspace. The primary selects both explicit positive sizes; 1024/64 MiB is the request's example, not a hidden default. `LD_PRELOAD`, `TMS_INIT_ENABLE=1`, and CPU-backup settings come from the native owner inside each case's re-exec. Preserve the launcher's formal CUDA-compat loader environment; the retained launch records `cuda_compat_dir=/usr/local/cuda-13.0/compat`.

Outputs: `late_moments.json`, `early_moments.json`, and `summary.json`; raw stdout belongs to the existing launcher log. No large memory-history snapshot or model artifact is written.

### Native acceptance predicates — not yet evaluated

1. Both subprocesses execute independently with the expected image/TMS identity and one actual H200.
2. Both produce all required phases, before-pause segment/block state and exact requested state bytes.
3. Every persistent tensor's CPU backup and restored GPU value matches exactly; pointers are unchanged; device free bytes increase during pause on the isolated GPU; native FusedAdam step 1 completes with finite parameter values.
4. The summary honestly reports an observed or unobserved ordering difference, or an incomplete diagnostic if either case fails. Successful exit is not proof of the formal root cause.
5. The primary verifies actual elapsed worker-script time <=600s and terminal/native outputs, then appends native results here. No formal-run fix is accepted on CPU preparation alone.

## Primary prelaunch inspection

The primary inspected the complete465-line probe and its CPU report after commit`dd15bcb6`, including native environment re-exec, nonzero state fills, master-parameter/default backup context, all phase measurements, independent cases and negative-result handling. The existing native environment owner at `miles/ray/specs/train.py:213–250` has the fields supplied by the probe. The actual retained launch supplies optimizer=adam,lr=2e-6,weight_decay=0.1,betas0.9/0.98,epsilon1e-8 and `/var/tmp` as its worker-local root. The source-receipt schema has all referenced installed-file/hash fields.

[allocator_probe_config.json](allocator_probe_config.json) selects one GPU,4 CPUs,`mem_gb=16`,one replica,1024MiB transient and64MiB per moment. The pinned image, H200/step_main, creator, CUDA compat directory, local mount and personal32 policy are derived from the actual formal launch receipt. The worker will have a fresh `/var/tmp` cache tree and the existing personal cloud-volume mount; results go only to the supplied local evidence root. GNU `timeout --signal=KILL 600s` will wrap the entire inner worker shell, including its two child cases, to enforce D38's worker-script limit. No GPU output has yet been accepted at this prelaunch checkpoint.
