## Modification History

| Date | Change |
| --- | --- |
| 2026-11-05 | Record CPU/GPU prerequisites, native failures, resource constraints, cleanup and intermediate synchronization; OPD qualification pending. |

# Agentic OPD Warmup Validation

## Scope and expected results

Use the actual frozen glm5.2 training turns, distinct GLM-4.7-Flash-Coder teacher and GLM-4.7-Flash student, native Miles OPD/R3, and 16 H200 GPUs. Require at least two finite optimizer updates; preserve thinking, body text and all tool calls; measure train/inference logprob differences on identical token IDs and weights. A process exit alone is insufficient. Retain code and Markdown conclusions only; remove all task-owned raw warmup data, logs, caches and cloud outputs after inspection.

## CPU GLM serialization: PASS

Environment: `/data/ycfeng/envs/openmopd-py312/bin/python`, Python3.12.13. Script: `examples/agentic_opd/glm_turns.py`; the exact instrumented probe and raw logs are in `/data/ycfeng/tmp/agent-opd-20261105/cpu-tokenizer-probe.log`. The unchanged ticket07 parent manifest is `/data/ycfeng/steptron/.worktrees/behavior-turn-replay-step3p6/task_memory/task_2026-10-25_swe_behavior_turn_replay/evidence/glm-replay-subsets-20261104.json`. The preparer selects the shortest complete training turn per category directly from that manifest. Selected complete prompt byte ranges were fetched read-only from the personal cloud mount; their conversation SHA256s matched.

The probe instantiated `AutoTokenizer.from_pretrained(.../glm-input/tokenizer, local_files_only=True)`, encoded each complete source history and selected assistant completion, then asserted both token counts and SHA256s against the fixed manifest.

| Category | Prompt tokens | Completion tokens | Count/hash assertions |
| --- | ---: | ---: | --- |
| control_and_thinking | 40380 | 614 | PASS |
| control_only | 28408 | 598 | PASS |
| thinking_only | 33616 | 464 | PASS |
| neither | 10366 | 23 | PASS |

All prompts end with `<|assistant|>`; the initial thinking tag is not forced. All previous reasoning is retained with `clear_thinking=False`. No source text was shortened or replaced. `control_only` contains ordinary body text without reasoning. `thinking_only` and `neither` still contain non-submit tool calls; absence of control is not absence of tools.

The first 60-second invocation timed out during environment startup; an instrumented unbounded process with asynchronous tool monitoring completed all assertions. Transformers emitted a generic tokenizer regex warning. The pinned source token counts/hashes still matched, so no unverified regex change was applied. This is input serialization evidence, not GPU numerical parity.

## Launcher snapshot: initial FAIL (environment)

Exact command:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
MILES_UPDATE_LAUNCH_SCRIPT_SNAPSHOTS=1 \
/data/ycfeng/envs/openmopd-py312/bin/python -m pytest \
  tests/manual/launch_scripts/test_py_launch_scripts.py \
  -k run_glm47_flash_agent_opd -q
```

Observed: test collection failed because the shared CPU environment lacks `polars`, imported by `miles/dashboard/store.py`. No launcher assertion ran. Fix: use a separate persistent Miles CPU environment and install the missing declared dependency there. Raw traceback: `/data/ycfeng/tmp/agent-opd-20261105/launcher-snapshot.log`.

## GPU and workflow validation: PENDING

Initial CUDA12 0-GPU probe `exp-1105-003619-953445` failed by importing TransformerEngine without an injected libcuda.so.1. Corrected CPU probe `exp-1105-004709-090270` Succeeded. Its Ray2.59.0 is outside the project requirement <2.59; the CUDA12 image is not used for training. New cu13 image qualification is in progress. At this initial runtime checkpoint, the 16-H200 training run had not yet been submitted; the latest GPU attempt is recorded below.

## Requested model preparation: PASS

Authenticated Lark CLI searches used the personal user identity. FrogNano returned zero visible results (`has_more=false`); Qwen3.5-4B returned three contextual documents without a verified asset directory. This is limited visible search evidence, not proof of company-wide absence. Read the current HF artifact-proxy document through Lark: `https://wvixbzgc0u7.feishu.cn/wiki/SZrWwFFSDivOERkXLYscs5Yonic`.

The first known company-runtime download (`exp-1105-002603-492786`) failed on FrogNano's second shard with curl HTTP408. Incident-bound platform/replica objects show worker exit1 at2026-11-04T16:36:31Z and platform Failed16:36:32Z; subsequent launcher cleanup is not the initiating cause. All eight RCA read sources completed; no separate initiating OOM/preemption/manual-stop event was identified. New 45s HEAD checks returned200 through both company mirrors and the existing VPN, while official direct timed out after10s. This supported retrying the cached company object; VPS was unnecessary.

The temporary `python:3.10-slim` retry failed because curl was absent. Reused the first download's known company runtime rather than installing packages in workers. Final job `exp-1105-005757-165193` finished Succeeded at00:59:13HKT; launcher exit0. All22 files,18,685,617,357 bytes, were verified by size and full SHA256, including four LFS weight shards.

Exact successful worker command:

```bash
python3 tests/manual/agent_opd/download_models.py \
  --manifest task_memory/task_2026-11-05_agent_opd_warmup/evidence/model-download-manifest.json \
  --output-root /mnt/codesign-exp/ycfeng/opd-assets/models \
  --report /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-05_agent_opd_warmup/evidence/model-download-result.json \
  --endpoint https://a.z01.normandyfunc.com/artifactory/api/huggingfaceml/huggingface-mirror \
  --workers 2 --timeout 3600
```

Model directories:

- `/mnt/codesign-exp/ycfeng/opd-assets/models/microsoft/FrogNano-4B-2609/b90468c11a913c1916b4542b4b7a530ec42024a4`
- `/mnt/codesign-exp/ycfeng/opd-assets/models/Qwen/Qwen3.5-4B/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`

| Model shard | Bytes | Verified SHA256 |
| --- | ---: | --- |
| FrogNano 00000 | 5,350,373,880 | `4a3ea221092b94e9c28adffe554d3d944ee189043cad8aa569e0d9c241fc4aed` |
| FrogNano 00001 | 3,969,447,040 | `5805e9ec4b8a243108ba41d02e1b254a6d234e491aee068f617559806e77dd09` |
| Qwen3.5 00001 | 5,329,398,688 | `26a93f066e1916adb13453dae5a0c707c0fbc71299ed98779571a907b8e74c61` |
| Qwen3.5 00002 | 3,990,429,408 | `cb544bd9bfae93dc59b0f22b292f5933573854a7f9b97835c67060d7d910e188` |

## Local disk cleanup: PASS (first milestone)

No container used this task's pinned CUDA12 image. `docker image rm docker.io/radixark/miles@sha256:49637ea95c9757f6bbf461faf902f95a5cd0c0f0a3dfbda194595e42f48164c5` removed only that image; no global prune or forced removal was used. `/data` available space increased from34GB to117GB. CPU dependency work subsequently used approximately5GB; all task-owned disposable caches/logs remain scheduled for cleanup.

## Completion parsing and launcher qualification: PASS (2026-11-05 continuation)

CPU runtime: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13,
Torch2.11/torchvision0.26/torchaudio2.11, Transformers5.19.0 and Ray2.58.1.
Parser source is SGLang commit `056f871a7ee8b4573832049011f0fdf52589cfd8`,
matching the qualified worker image. The shared CPU environment was unchanged.

All four original completions matched original reasoning, body and JSON tool
arguments: `control_and_thinking` (93 reasoning chars,2491 body chars,submit),
`control_only` (0,2460,submit), `thinking_only` (1650,86,bash), and
`neither` (0,0,str_replace_editor). Plain body, empty-reasoning `</think>`,
explicit and implicit opening reasoning markers, truncated thinking and
truncated tool envelopes passed. Raw tokens/text remain available when a tool
envelope is incomplete. GLM emits `</think>` even without reasoning; selecting
`force_reasoning` from that marker fixed the observed control-only mismatch.
Tool calls use native `call_` IDs for subsequent tool-response linkage.

The new launcher snapshot passed both entrypoint checks. Its sequence flag is
native `--seq-length`; its run ID uses the snapshot-frozen `U.create_run_id()`.
Removed mutually exclusive `--use-rollout-logprobs` when TIS is enabled.
Response budget1024 includes the two historical598/614-token completions.

Exact full-suite command (source path abbreviated only here):

```bash
PYTHONPATH=/data/ycfeng/tmp/agent-opd-20261105/sglang-source/sglang-056f871a7ee8b4573832049011f0fdf52589cfd8/python:/data/ycfeng/sota-engine/miles \
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest \
  tests/fast/launch_scripts tests/manual/launch_scripts -q
```

Observed:584 passed,18 failed,50 errors in25.49s. The new launcher passed.
Errors include `PermissionError: /root/models`; failed cases concern other
tracked recipes and missing or stale snapshots. Their relationship to the
unchanged baseline still needs a scoped check. No unrelated recipe was edited.
The suite as a whole is not PASS.

## Pinned CUDA13 CPU runtime: PASS; GPU qualification still pending

Job `exp-1105-005353-468156` Succeeded at01:04:18HKT; launcher exit0,
creator `i-fengyicheng`, local Miles NFS source. Image:
`artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`.
Observed Python3.12.16 (`/opt/sglang/bin/python3`), Torch2.14.1+cu130,
Transformers5.19.0, Ray2.58.1, SGLang0.5.24.dev80+g056f871,
Polars1.42.1 and safetensors0.8.0. The two zero-GPU replicas shared one CPU node;
this is not evidence for two distinct physical nodes or any GPU imports.
The platform rank variables are `KUBEBRAIN_REPLICA/TOTAL/NAME` and
`KUBEBRAIN_RJOB_NAME`, confirmed in Steptron's existing rank implementation.

## Unchanged launcher baseline classification: PASS

Extracted unchanged HEAD `ff97a63b` with `git archive HEAD` into task-owned
`/data/ycfeng/tmp/agent-opd-20261105/baseline`. Ran the same full launcher suite
with its PYTHONPATH pointing to that extracted checkout and the same pinned
SGLang source/CPU interpreter. Observed582 passed,18 failed,50 errors in22.32s.
All68 failing/error test IDs are identical to the modified checkout; the only
count difference is the new launcher's two passing checks. This establishes
the observed full-suite failures as unchanged baseline/environment failures.
No unrelated recipe or snapshot was repaired. The extracted checkout and raw
baseline log are disposable and removed after this conclusion was recorded.

## First 16-H200 attempt: FAIL before training

Exact job: `exp-1105-012438-455920`, created01:24:38HKT from this local
Miles checkout using personal StepMind Python `spawn_tasks`/RJobBackend.
Creator independently verified `i-fengyicheng`; non-preemptible `no`;
step_main;2 replicas, each8H200/48CPU/600000Mi. Final limits preserve
`mellanox.com/mlnx_rdma:1` and `rdma/mlnx_shared:8`. NFS source is
`100.96.128.195:/data/ycfeng/sota-engine/miles:/data/ycfeng/sota-engine/miles`.
Native inference checksum logging is enabled to compare initial and first
updated inference weights. The default driver does not sync after its final
update, so synchronization qualification covers updates actually published.

Worker command is the current `tests/manual/agent_opd/rjob_warmup.py` with
`--manifest` pointing to a disposable identical parent-manifest copy,
`--student/--teacher` pointing to the unchanged personal GLM asset paths,
`--output-root /mnt/codesign-exp/ycfeng/miles/agent-opd/warmup-20261105`,
`--shared-dir` pointing to this task's disposable rendezvous directory, and
`--num-rollout 2`. Interpreter is `/opt/sglang/bin/python3` in the pinned image.


## CUDA driver failure RCA: PASS (cause identified; workload not qualified)

Job `exp-1105-012438-455920` ended Failed at2026-11-04T17:37:05Z
(2026-11-05 01:37:05HKT). Replica1 on `gpu-h200-0040.lgcm.sh.istep.fun`
exited1 at17:37:03Z. Its first CUDA initialization warning at17:36:40Z and
final traceback report `The NVIDIA driver on your system is too old (found
version12080)`. Torch is2.14.1+cu130. Training and dataset preparation had not
started. Replica0 on `gpu-h200-1033.lgcm.sh.istep.fun` reported driver570.124.06,
eight H200s, CUDA available and GPU module imports passed; it did not execute
an arithmetic kernel. Its SIGTERM at17:37:05Z followed replica1's failure.

The job's returned system stop annotation is `Task fail policy [any] caused
undesired running replicas.` Its stopTimestamp is17:37:05Z; the historical
RJob Events show the sibling Pod delete at that time and replica close at
17:37:06Z. These are failure cleanup. No initiating manual-stop actor, reason
or audited request time was returned; those fields remain UNKNOWN.

Executed the bundled `collect_failure_evidence.py` twice through the existing
personal wrapper, binding each exact replica and owner UID, creator
`i-fengyicheng`, and the window17:35:00Z–17:38:00Z. Both collectors exited0;
all eight read sources succeeded and pagination completed. Driver-case
live/historical RJob Events2/10, replica Events3/3, all-operation RJob/replica
audits18/1; sibling replica Events2/4 and audits6. Existing DeepScan count0.
Returned Events/container state contain no positive initiating
OOM/preemption/manual-stop evidence. This is limited platform coverage;
Sherlock native Pod/node/audit logs were not needed to identify the explicit
application CUDA failure and were not queried. Worker-init's missing `ip`
executable is a separate platform P2P-probe error, not this traceback.

Exact collector invocation shape:

```bash
timeout 60s bash /data/ycfeng/tmp/agent-opd-20261105/personal_exec.sh   /data/ycfeng/stepcode-codex-home/.stepcode/codex/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py   exp-1105-012438-455920 --replica exp-1105-012438-455920-c4ca4238   --expected-creator i-fengyicheng   --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng   --start 2026-11-04T17:35:00Z --end 2026-11-04T17:38:00Z   --timeout 45 --output /data/ycfeng/tmp/agent-opd-20261105/rca-glm16-driver
```

Second call changes the replica suffix to`cfcd2084` and output to
`rca-glm16-sibling`. Collector environment is Python3.10.6/brainpp2.8.6.
Raw evidence is disposable and will be removed after these conclusions.

## CUDA compatibility repair: hypothesis and CPU qualification in progress

The pinned public image config confirms a build step for`cuda-compat-13-0`;
its default LD_LIBRARY_PATH places host NVIDIA libraries first and omits the
compat directory. NVIDIA's official forward-compatibility table marks
`cuda-compat-13-0` compatible with570+ drivers. Source:
https://docs.nvidia.com/deploy/cuda-compatibility/forward-compatibility.html
(read2026-11-05). The image's exact compatibility layer is
`sha256:f0af354daeda18f18684b23520969ef6bb3de82bb267936f867b12769be9125d`,
compressed104,893,539bytes. Inspect this layer on the CPU host before retrying.

Hypothesis before retry: explicitly preferring the pinned image's
`/usr/local/cuda-13.0/compat` libraries before Python startup will resolve the
CUDA13 initialization failure on both570-driver nodes. The worker adapter
passes the selected LD_LIBRARY_PATH through the existing Ray runtime-env
mechanism. The runtime probe now requires FP32 elementwise reduction and
BF16 cuBLAS matmul on every allocated GPU, and records loaded driver libraries
and driver API version. Failure of either node's kernels rules out this repair.
No host driver, unrelated environment, or package installation is changed.


CPU compatibility qualification: PASS. Full image layer size and SHA256 match
the pinned manifest. It contains libcuda580.126.20 and its NVVM/PTX JIT companion
libraries. A CPU-host ctypes load returned cuDriverGetVersion13000/exit0; ldd
resolved all dependencies of all versioned libraries. This proves the
selected files/layout and CPU ELF dependencies, not GPU execution. The adapter
syntax and CPU --help imports passed after the runtime-probe changes.

Exact CPU driver query used LD_LIBRARY_PATH pointing to the extracted
`compat-image/usr/local/cuda-13.0/compat`, then
`ctypes.CDLL(.../libcuda.so.1).cuDriverGetVersion(byref(c_int()))`.
The extracted layer and libraries are removed immediately; GPU workers use
the unchanged pinned image's own copies.


## Community parameter rationale (primary sources inspected)

The recipe uses student-generated completions scored by the frozen teacher on
the same input IDs, matching Thinking Machines' sampled-token reverse-KL OPD
recipe (2025-10-27):
https://thinkingmachines.ai/blog/on-policy-distillation/ .
`--opd-log-prob-top-k 0` intentionally exercises that existing native path;
top-k reward experiments are outside this workflow warmup.

Miles' TITO article describes token-preserving turn boundaries and identifies
retokenization and discarded reasoning as alignment failures:
https://www.lmsys.org/blog/2026-05-13-no-token-left-behind/ .
The adapter retains the original prompt and generated token IDs rather than
training on parsed/re-rendered text; it uses clear_thinking=False for histories.
This warmup verifies individual complete turns and does not claim qualification
of a live multi-turn tool execution loop.

The Miles authors' training/inference mismatch article describes R3 plus
importance-sampling correction:
https://staging.lmsys.org/blog/2026-01-16-training-inference-mismatch .
The recipe enables native routing replay, mismatch measurements, TIS/IcePop
masking with the existing0.5–2 bounds, deterministic Hopper FA3, zero dropout,
FP32 softmax and gradient accumulation. Pinned SGLang056f871 selects FA3 for
Hopper deterministic GLM4MoeLite and rejects FlashInfer radix-cache determinism
for MLA; this was checked against source before the GPU attempt. No
`--use-rollout-logprobs` flag is combined with TIS because native argument
validation rejects that combination. Untruncated temperature1/top-p1/top-k-1
sampling keeps the scored distribution consistent with the native softmax.
Numerical agreement is measured separately; these flags do not prove it.


### Native consumer review: single-sample GRPO is compatible with pure OPD

The actual custom reward hook returns zero scalar task rewards and records
teacher logprobs (`miles/rollout/on_policy_distillation.py:411`).
`miles/ray/rollout/train_data_conversion.py:375` returns that hook result before
the default reward-normalization branch. `get_grpo_returns`
(`miles/backends/training_utils/loss/hub/math_utils.py:516`) expands each scalar
reward to its token positions without computing a within-prompt standard
deviation. `compute_advantages_and_returns`
(`miles/backends/training_utils/loss/objective.py:113`) then applies the detached
old-student minus teacher token logprob penalty; `normalize_advantages` defaults
to False (`miles/utils/args/configs/algo.py:155`). Thus one sample per prompt
provides a pure token OPD signal without a singleton standard-deviation NaN in
this inspected path. Even the unused default normalization branch requires
more than one rollout before computing its standard deviation. This is source
qualification, not an observed finite optimizer update.

R3 reaches both consumers: engine setup enables return_routed_experts
(`miles/backends/sglang_utils/sglang_engine.py:145`), each request asks for the
routes (`miles/rollout/generate_utils/generate_endpoint_utils.py:107`), and the
Megatron replay registration maps the received layer arrays to local MoE layers
(`miles/backends/megatron_utils/replay_utils.py:5`). The configured custom TIS
consumer computes exp(old-training-logprob minus rollout-logprob), detaches the
weights, and masks out-of-range token positions using the configured bounds
(`examples/infra_features/train_infer_mismatch_helper/mis.py:234`). These checks
confirm the existing flags have consumers; the actual route arrays and numeric
ratios still require the pending GPU run.

## CUDA-compatible 16-H200 retry: Starting

Created `exp-1105-015559-912357` at01:55:59HKT with the original image and
16-GPU shape. Creator, quota, local mount and RDMA limits verified through the
personal API. The command is the first warmup command prefixed by:

```text
env LD_LIBRARY_PATH=/usr/local/cuda-13.0/compat:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/cuda/lib64 /opt/sglang/bin/python3 -u -B
```

The local launcher remains alive. Two worker IPs are distinct. GPU kernel and
training observations are pending; no success is inferred from Starting.

## CUDA-compatible GPU and Ray prerequisite: PASS (2026-11-05T02:11:53.226300+08:00)

The same retry is Running. Both nodes (gpu-h200-0192 and gpu-h200-0024) report eight NVIDIA H200 GPUs,143771MiB each,driver570.124.06. Both load `/usr/local/cuda-13.0/compat/libcuda.so.580.126.20`, return driver API13000, and pass actual FP32 reduction10416 and BF16 matrix product16 on each of the16 GPUs. Ray reports the two distinct IPs10.204.16.46/10.204.8.36 and16 total GPUs. This verifies the recorded compatibility hypothesis on this pinned image and these nodes; it does not prove all CUDA features or business training.

The warmup preparer writes four actual glm5.2 training turns and repeats the exact prompt/completion counts and hashes above. Native student and teacher loading is underway; optimizer and numerical qualification remain pending. Runtime0 records source77efcf319eebae42d86db06b0056de50896cf995 and the three uncommitted manual-run scripts. Runtime1 uses the earlier probe report schema and has no source_revision field; the shared local NFS source is independently verified for both replicas.

## Second 16-H200 attempt: FAIL at initial weight synchronization

Job `exp-1105-015559-912357` finished Failed at2026-11-04T18:13:05Z
(2026-11-05 02:13:05HKT). Replica0 `cfcd2084` on gpu-h200-0192 exits1
at18:13:04Z. Native trainer actors loaded HF weights and initialized, then the
first `broadcast.py:187` weight transfer reports NCCL2.30.7 and
`Message truncated : received 2048 bytes instead of 512`. There is no completed
optimizer update, rollout dump or train dump. The successful CUDA kernels,
Ray topology, tokenizers and original-turn preparation remain prerequisite PASS.

Replica1 `c4ca4238` on gpu-h200-0024 is subsequently Stopped, with a stale running
container snapshot. RJob stopTimestamp18:13:05Z and the system annotation
`Task fail policy [any] caused undesired running replicas.` are cleanup. All-operation
replica audits contain five system rjob-controller stop rows at18:13:05/06Z,
after the application failure. No initiating manual-stop actor/reason/request
was returned; those fields are UNKNOWN. Startup scheduling messages about
waiting for other preempted Pods do not establish preemption of this running job.

Both exact-replica RCA collectors exited0 with all eight queries successful and
pagination complete, window18:10–18:14Z, log limit3000. Trainer live/historical
RJob Events2/10, replica Events0/3, RJob/replica audits11/1; sibling replica
Events2/5 and audits6. Both RJob audit snapshots have count11 versus page total9;
report actual returned rows, not an invented consistent total. Incident log
rows1363/1, below limit; existing DeepScan0. No returned terminal state or
incident event positively identifies OOM or preemption. Native Sherlock logs
were not queried because an explicit application traceback identifies the failure.
Raw evidence is removed once these conclusions are recorded.

## Independent process-group CPU regression: PASS; GPU qualification pending

Environment: isolated Python3.12.13, Torch2.11 CPU and pytest9.1.1. Command:

```bash
PYTHONPATH=/data/ycfeng/sota-engine/miles PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest \
  tests/fast/utils/test_independent_process_group.py -q -p no:cacheprovider
```

Expected: the real PyTorch `_new_process_group_helper` must construct an independent
5-rank world without `Options.split_from` from an eager-device-bound8-rank
parent; the parent device must be restored even when construction raises.
Observed before fix:1FAIL/1.12s, `An independent world inherited the trainer's
communicator`. After the minimal context around the existing helper:
1PASS/1.02s. Only the NCCL constructor is replaced; ProcessGroup/HashStore and
the helper's splitting logic are real. This test qualifies that code path,
not actual cross-node NCCL or OPD optimization.

The fixed SGLang revision056f871a7ee8b4573832049011f0fdf52589cfd8 already
protects `init_custom_process_group` with `_no_split_from_default_group`
(common.py2856–2945). Miles sender lacked it. Ranked predictions are recorded
before GPU retry in progress.md. The CUDA probe uses trainer world8, inference
world4, independent transfer world5, BF16 tensor versions0/1 and restored
parent-world reductions. It releases all probe actors before real warmup.

## Minimal GPU probe attempt: FAIL with initiating exception unavailable

Exact job `exp-1105-023323-244560` Failed at2026-11-04T18:35:36Z
(2026-11-05 02:35:36HKT), launcher exit1. Both workers independently record
source a465e4b4 and pass all16 FP32/BF16 kernels using compat libcuda580.126.20.
Ray registers distinct nodes10.204.4.55/10.204.9.75, eight GPUs each. The child
probe connects at18:35:22Z and returns1 by18:35:31Z, before any weight-sync
report or native model/data artifact. Returned logs contain the parent
CalledProcessError, but no initiating child exception. Its cause remains
UNKNOWN; this is not evidence that the NCCL fix failed.

RCA completed all eight queries for both exact owner-bound replicas, exit0,
pagination complete; incident window18:33–18:36Z and limit3000:

```json
[
  {
    "name": "exp-1105-023323-244560-cfcd2084",
    "node": "gpu-h200-0040.lgcm.sh.istep.fun",
    "phase": "Failed",
    "coverage": {
      "rjob-live-events": 10,
      "replica-live-events": 8,
      "rjob-historical-events": 10,
      "replica-historical-events": 2,
      "rjob-audit": 11,
      "replica-audit": 1,
      "existing-deepscan": 0
    },
    "incident_rows": 161
  },
  {
    "name": "exp-1105-023323-244560-c4ca4238",
    "node": "gpu-h200-1033.lgcm.sh.istep.fun",
    "phase": "Stopped",
    "coverage": {
      "rjob-live-events": 10,
      "replica-live-events": 13,
      "rjob-historical-events": 10,
      "replica-historical-events": 5,
      "rjob-audit": 11,
      "replica-audit": 5,
      "existing-deepscan": 0
    },
    "incident_rows": 77
  }
]
```

Replica0 exits1 at18:35:34Z; sibling Stopped retains a stale running container
snapshot. System fail-policy cleanup and RJob stopTimestamp18:35:36Z follow
this application exit. No initiating manual-stop actor/reason/time, OOMKilled
or incident-bound preemption is returned. No existing DeepScan; Sherlock was
not queried because the immediate next diagnostic targets the missing child
exception. Raw logs/RCA/runtime files are disposable and removed now.

CPU prediction tested before another GPU allocation: Ray cloudpickle actor
serialization succeeded (18,916bytes), excluding the recorded serialization
hypothesis. The probe now writes stage/error/traceback before Ray cleanup.
An injected node-discovery StopIteration on CPU produced the exact failed
report and kept the original exception; PASS. This verifies evidence capture,
not the actual GPU failure. Same image, shape and NCCL parameters are retained
for a sharper minimal-probe rerun.

## Exact probe-state failure and CPU repair: cause identified

Job `exp-1105-024340-358946` ended Failed at2026-11-04T18:50:40Z
(2026-11-05 02:50:40HKT). The child failure report identifies
`initialize_default_worlds`, `RayTaskError(AttributeError)` and
`_world.default_pg` being None immediately after native init. All16 kernels
and the two-node Ray topology passed; independent broadcasts and GLM training
were not reached. Replica0 on gpu-h200-1033 exits1 at18:50:36Z;
replica1 on gpu-h200-0107 is subsequently Stopped with a stale running snapshot.
System fail-policy stopTimestamp18:50:39Z follows the application error.
Launcher90266 exited1 at02:50:42HKT.

Both exact-owner RCA collectors exited0 with all eight read sources successful,
complete pagination, window18:49–18:52Z, loglimit3000. RJob live/historical
Events7/7 and audits10; trainer replica live/historical Events9/2 and audit1;
sibling8/2 and audit4. Existing DeepScan0. No initiating manual-stop
actor/reason/request time is returned; keep these UNKNOWN. The sibling's
stopped-by rjob-controller and terminal timestamps describe cleanup.
The explicit application traceback identifies the failure; no native Sherlock
query was needed.

CPU reproduction used Python3.12.13, Ray2.58.1,
`ray.cloudpickle.loads(dumps(_WeightSyncRank.__ray_metadata__.modified_class))`
and `inspect.unwrap(restored.initialize).__globals__`. The captured `_world`
is a different object from `torch.distributed.distributed_c10d._world`: PASS
for the cause reproduction. Serialization itself can succeed while capturing
a stale process-global snapshot.

The probe now reads `dist.group.WORLD.bound_device_id` through the referenced
Torch module. On the actual deserialized actor method, a newly installed
real ProcessGroup/HashStore with bound cuda0 is observed correctly: PASS.
Only the init call and subsequent numeric method were substituted on CPU;
this qualifies actor state identity, not GPU collectives. Ruff0.14.7, cached
Black and isort checks passed. No core, image, topology or NCCL setting changed.

Exact probe RCA incident logs returned90 trainer rows and76 sibling rows, belowlimit3000. All returned audit data fields are null; sibling controller stop rows occur at18:50:40/41Z after trainer exit18:50:36Z. Event messages cover startup placement/image/configmap events and subsequent sibling deletion; no incident-bound OOMKilled or preemption is returned. These are bounded negative observations, not a proof of complete log ingestion. Removed the exact old job raw RCA/log/rendezvous after recording this conclusion.

## Independent NCCL GPU broadcast: PASS (job025447)

Actual job `exp-1105-025447-723908` is Running with creator
`i-fengyicheng`, the same local NFS100.96.128.195, original pinned image,
2x8H200/48CPU/600000Mi, both RDMA limits and nonpreemptible=no.
Runtime reports on both nodes repeat16 actual FP32/BF16 CUDA kernel PASS.
Source revision a465e4b4 plus the four recorded manual scripts.

The deserialized Ray actors initialize eagerly device-bound default NCCL
worlds8/4, using trainer node10.204.9.75 and inference node10.204.14.5.
Their default reductions equal36/10. The independent weight world5 uses
Miles sender and pinned SGLang receiver factories. Both32-element BF16
versions are bitwise equal at all5 participants: sums496 and528. After
weight-world destruction, every default-world reduction still equals36/10.
All probe actors are released before the real GLM workflow. This is actual
cross-node broadcast qualification for the minimum case; full model transfer
and optimizer updates still need native observations.

Actual worker probe command:

```bash
/opt/sglang/bin/python3 tests/manual/agent_opd/weight_sync_probe.py \
  --address 10.204.9.75:9223 \
  --report <task-rendezvous>/exp-1105-025447-723908/weight-sync.json \
  --trainer-gpus 8 --inference-gpus 4
```

The same job's data preparer again verifies all4 fixed original turns and
token hashes. Native run ID is `261104-185538-q770`. Real student/teacher
loading follows the probe without a new GPU submission or package install.

## Full-model synchronization after the minimum probe: FAIL

Job`exp-1105-025447-723908` on gpu-h200-1033/gpu-h200-0107 failed at
2026-11-04T19:05:12Z (November5 03:05:12HKT). Native trainer rank0
`broadcast.py:187` reports NCCL2.30.7`Message truncated : received 2048 bytes
instead of 512` at19:04:53Z. Source0ec6a6af was committed while the job ran;
loaded worker code was a465e4b4 plus the manual probe repairs recorded above.
Both engines finished loading; the first HF broadcast failed before rollout
or optimization. This invalidates full-model synchronization qualification;
the earlier minimum broadcast observations remain limited PASS.

RCA ran the same bundled collector on both exact owner-bound replicas, with
window19:03–19:06Z and loglimit3000. All eight queries succeeded with complete
pagination. RJob live/historical Events2/4 and audits10; trainer replica
Events0/0 and audit1; sibling Events2/1 and audit4. Incident logs614/0 rows;
existing DeepScan0. Trainer exits1 at19:05:11Z. Sibling Stopped retains a stale
running container snapshot; system fail-policy stopTimestamp19:05:12Z and
controller stop audits19:05:12/13Z follow the application failure. Every returned
audit data field is null; initiating manual-stop actor/reason/request are
UNKNOWN. No incident-bound OOMKilled/preemption evidence is returned. Native
Sherlock was not needed for this explicit application exception.

Pinned SGLang source`arg_groups/attention_hook.py:735–737` sets deterministic
NCCL channels from`envs.SGLANG_DETERMINISTIC_NCCL_NCHANNELS` (default8).
The prior probe did not model this receiver-only launch setting. Before
retrying full GLM, the minimum probe now tests asymmetric versus equal channel
configuration. The exact initiating transport cause remains unqualified until
that differential test executes.

## Candidate channel alignment CPU checks: PASS; GPU diagnosis Pending

The current job is exp-1105-031302-898658, local launcher50766, creator
`i-fengyicheng`, personal local NFS100.96.128.195, original pinned image and
2x8H200/48CPU/600000Mi. Both RDMA limits are present. It is preemptible=yes;
no new non-preemptible GPUs were added. A bounded queue read reports global
queue rank8 and no usable GPUs in64 queried step_main nodes. Queue messages
are placement observations, not training outcomes.

Prepared `scripts/run_glm47_flash_agent_opd.py::_training_env` as a candidate
configuration change. It derives the channel count from pinned SGLang's
`envs.SGLANG_DETERMINISTIC_NCCL_NCHANNELS`, uses the existing
`U.resolve_extra_env_vars` precedence, retains matching inherited bounds,
and rejects conflicting bounds at startup. No copied default or transport
fallback was introduced. CPU assertions passed for source-derived default8,
a canonical runtime override4, matching inherited min, preserved
LD_LIBRARY_PATH/NCCL_IB_HCA overrides, and rejected conflicting min/max9.

CPU commands use Python3.12.13 in `/data/ycfeng/envs/miles-agent-opd-cpu` and
PYTHONPATH pointing to the pinned SGLang056f871 source and Miles checkout,
TMPDIR=/data/ycfeng/tmp and PYTHONDONTWRITEBYTECODE=1:

```bash
MILES_UPDATE_LAUNCH_SCRIPT_SNAPSHOTS=1 python -m pytest   tests/manual/launch_scripts/test_py_launch_scripts.py   -k run_glm47_flash_agent_opd -q -p no:cacheprovider
python -m pytest tests/fast/launch_scripts tests/manual/launch_scripts   -q -p no:cacheprovider
```

New snapshot:2PASS/1.38s; exactly two runtime-env keys were added,
NCCL_MIN_NCHANNELS=8 and NCCL_MAX_NCHANNELS=8. Full suite:584PASS,
18FAIL,50ERROR/22.18s, the same counts and unrelated failing recipes as the
already classified baseline. No unrelated recipe was changed. Ruff0.14.7,
Black and isort pass for the five changed Python files. The three manual
entrypoints' CPU imports and --help pass.

The inspector additionally matches each completion's recorded weight version
to the corresponding native checksum publication. This is an offline
acceptance assertion, not a change to training or an invented numerical
parity tolerance.

The queued job now runs the original asymmetric/matching differential before
any model load. Only identical-truncation failure in the asymmetric case and
success in the matching case permit the unchanged two-update warmup to run
in that same allocation. Otherwise it reports diagnosis only. The actual
channel cause, full-model synchronization, optimizer updates and numerical
parity remain unverified until GPU execution.

### External Ray canonical-value propagation: PASS

A canonical channel override exported only in the submitting process may be
absent from an already-running external Ray cluster. `_training_env` now emits
SGLANG_DETERMINISTIC_NCCL_NCHANNELS as well as both NCCL bounds. The value
still comes from the installed SGLang field; no default is duplicated.
A direct call with only the submitter's canonical env set to4 returned all
three runtime-env fields as4: PASS. Updated snapshot2PASS/1.42s, full launcher
suite584PASS/18FAIL/50ERROR in20.31s. The sole new snapshot field is the
source-derived canonical8; known unrelated baseline failures remain.

The diagnostic records actual inherited sender/receiver bounds, including
failure reports. The continuation requires actual asymmetric sender bounds
unset, the identical truncation, and matching-case exit0, so a no-op setting
change cannot falsely qualify the cause. This remains GPU-unverified while
exp-1105-031302-898658 is Pending.

## Resource checkpoint and cleanup: GPU validation still incomplete

At the November5 continuation, the original exact job
`exp-1105-031302-898658` remains Pending with creator `i-fengyicheng`,
preemptible=yes and local NFS 100.96.128.195. Launcher session 50766 is alive.
The last full-model attempt completed zero optimizer updates; no new native
warmup output exists for the queued job.

The current personal Running/Starting query reports 48 non-preemptible H200
across 6 unrelated jobs. Adding 16 non-preemptible GPUs would exceed the stated 32
limit. All unrelated jobs are preserved. Current step_main capacity reads
return all 64 nodes with 8 usable GPUs; this is below the 16-GPU gang requirement.
The queue annotation remains rank8 and approval empty; its reason reports
H200=409 at the latest refresh. These observations are neither reservations
nor successful execution evidence.

The alternate codesign query returned all 185 reported nodes. Platform
`metadata.labels.GPUType` counts are H800=166 and no_gpu_type_label=19;
usable GPU counts are190 and 0 respectively. No H200 label was returned.
The prior infer_af_test query returned only 2 CPU nodes. Neither observation
provides a verified alternate allocation for the requested H200 warmup.

Exact observation commands used the existing personal wrapper and Python3.10.6
with brainpp2.8.6:

```bash
timeout 60s bash /data/ycfeng/tmp/agent-opd-20261105/personal_exec.sh   /data/ycfeng/steptron/tests/integration/inspect_stepmind_personal_job.py   exp-1105-031302-898658
timeout 60s bash /data/ycfeng/tmp/agent-opd-20261105/personal_exec.sh   /data/ycfeng/tmp/agent-opd-20261105/current_h200_usage.py
timeout 60s bash /data/ycfeng/tmp/agent-opd-20261105/personal_exec.sh   /data/ycfeng/tmp/agent-opd-20261105/queue_read.py
```

The one-off codesign query used the same authenticated client's
`/kapis/node.brainpp.cn/v1alpha1/nodes/details` endpoint, tenant=shai,
project=shai-core, group=codesign, page 1/pageSize=500 and 25s request timeout.
Its temporary script and response were removed after the aggregate counts
above were recorded. All consumed usage/capacity snapshots, inactive smoke
inputs, raw RCA/logs, lint caches and root pytest/Ruff caches have been removed.
Earlier raw-file paths in this report document historical commands rather
than retained artifacts. Requested model assets and shared original data are
preserved. The active manifest/entrypoint and pinned Python source remain
necessary inputs for the queued job and any affected CPU verification.

Observed `/data` free space is 111GiB, with task tmp 173MiB and active inputs 988KiB;
these values were stable during this continuation. There is no new compiled,
log or smoke-data growth. The prior task-only image cleanup recovered about 83GB.

Read-only `gh api repos/fwyc0573/miles --jq '{full_name, push_allowed: .permissions.push}'`
returned `full_name=fwyc0573/miles` and `push_allowed=true`. Only the verified
preparation snapshot and Markdown conclusions are ready for intermediate
synchronization. Actual channel diagnosis, two optimizer updates and numeric
parity remain unqualified.

## Continuation checkpoint: preparation synchronized; actual warmup BLOCKED

At 2026-11-05T06:47:27.391606+08:00, read-only `git ls-remote --heads origin agent-opd`
matched local HEAD `c403bdc7af16b7ddce640c4af1144b7f36e7fc31`. This proves the preparation
branch is synchronized; it does not qualify OPD. No training code, parameters
or resource shape changed in this continuation.

The exact personal inspection reports `exp-1105-031302-898658` Pending,
creator `i-fengyicheng` and local NFS source100.96.128.195. Launcher50766
is alive. The original queue has rank8, approval empty and explicitly says
insufficient GPU quota; its remaining-H200 field is460, a queue observation.
All64 step_main nodes report 8 usable GPUs total, below the16-GPU
gang requirement. No worker or native result file exists yet, and actual
optimizer updates remain0.

Local `/data` free111GiB; task temporary inputs/source173MiB and active
evidence988KiB. The consumed query responses and exact-job log snapshot were
removed after these aggregate conclusions were recorded. Active job inputs,
shared environments, credentials, requested model assets and original datasets
remain available. PASS for intermediate synchronization and consumed-data
cleanup; BLOCKED for GPU channel diagnosis and real OPD optimization.


## Original channel differential and first rollout: transfer PASS, OPD FAIL

Exact job `exp-1105-031302-898658`, creator `i-fengyicheng`, source revision2171fd65,
local NFS100.96.128.195,16H200 on gpu-h200-0754 and gpu-h200-0232.
Image/runtime remain the pinned CUDA13 environment described above.
The real asymmetric sender had both channel bounds unset and receivers8:
`Message truncated : received 2048 bytes instead of 512` (FAIL).
With both sender/receivers8: two BF16 broadcasts summed496 and528; parent
worlds8/4 reduced36/10 before and after transfer (PASS). The subsequent matching
weight probe also passed. The same allocation entered the full real model path,
published initial weights and generated rollout0. It failed before any optimizer
update when `_compute_zero_std_metrics` called `round()` on the teacher dict.
The offline cloud check found20 files/117262536bytes and native event counts:
env_report46,engine_env_report2,inference_engine_weight_checksum1,weight_update_result1;
no actor optimizer event. `full_training_executed=false` indicates the training
function never returned successfully, not that real models never started.

RCA commands used the installed collect_failure_evidence.py, personal Python3.10.6/
brainpp2.8.6 and exact trainer/sibling replicas with UTC window23:26–23:29 on
November4. Eight sources per replica completed with pagination. RJob UID
b22aaac3-a467-4058-a787-2068319189c6; replica UIDs
a3a05fd6-2d52-4f99-ae53-90baf8a145bf and0ff081fa-7bc8-43ea-9a69-f60d0bfc8e00.
Trainer container exit1/Error at23:27:59Z preceded fail-policy stop23:28:02Z;
sibling audits explicitly identify rjob-controller at23:28:02/03Z.
Historical Events counts39(job),7(trainer),8(sibling); audits73/1/6; live Events0,
existing DeepScan0. Startup FailedScheduling messages are not incident preemption.
Initiating failure: Python reward/metrics contract; subsequent sibling stop:
fail-policy cleanup. Sibling final container code UNKNOWN (stale running projection).
No OOM/preemption attribution is supported. Raw evidence is disposable.

## Teacher reward adapter regression: PASS

The unchanged native metrics ran before native OPD post-processing. Separate the
zero task reward from the teacher response with existing reward-key/custom hook
mechanisms. No core metrics change or launch-state mutation is needed.

```bash
PYTHONPATH=/data/ycfeng/tmp/agent-opd-20261105/sglang-source/sglang-056f871a7ee8b4573832049011f0fdf52589cfd8/python:/data/ycfeng/sota-engine/miles \
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest \
 tests/fast/rollout/test_on_policy_distillation.py tests/fast/ray/rollout/test_metrics.py \
 -q -p no:cacheprovider
```

Python3.12.13. Before patch: corrected regression FAIL/KeyError reward; the
original no-reward-key native repro separately reproduced round(dict) TypeError.
After patch:106PASS in4.17s. Expected/observed: scalar metric0, teacher logprobs
[-0.2,-0.3] on exact tokens[11,12], unchanged args, unchanged response object,
exact teacher scoring request. Launcher snapshot2PASS/1.46s;
only reward-key and custom post-process path changed in snapshot.
Real optimizer verification remains pending a new16H200 run.

Required full launcher suite command used the same environment and `python -m pytest tests/fast/launch_scripts tests/manual/launch_scripts -q -p no:cacheprovider`:584PASS,18FAIL,50ERROR in22.65s. Failures remain the documented unchanged baseline IDs. Incident logs coverage721/1 rows below3000 limit.


## Temporary H800 switch: preparation

User request: temporarily switch to H800. At12:57:35HKT the mandated personal
rjob_stop.sh stopped queued exp-1105-124538-296267 (creator checked); its terminal
state will be confirmed. Fresh personal codesign query:186nodes,63usable GPUs,
0personal Running/Starting GPUs. Capacity is a snapshot, not a reservation.
The existing RJob entrypoint's explicit --gpu-type now selects H200/H800; --help
passed in the pinned CPU environment. Training parameters and16GPU topology are
unchanged. H800 evidence will not qualify H200 training.

Required full launcher suite after the hardware docstring update:584PASS/18FAIL/50ERROR in22.03s (same exact CPU environment/command above). The H800 worker check will be exercised on allocated devices, not simulated CPU devices.

## Actual H800 warmup submission

The local launcher session 72538 created `exp-1105-130232-725485` on November 5 at 13:02:32 HKT. Personal Python API confirms creator `i-fengyicheng`, phase Starting, `preemptible=no`, two replicas with 8 GPUs / 48 CPU / 600000 Mi each, both existing RDMA limits and current-machine NFS `100.96.128.195:/data/ycfeng/sota-engine/miles`. Source revision is `cdb861da`.

The local submission used `bash /data/ycfeng/tmp/agent-opd-20261105/personal_exec.sh /data/ycfeng/tmp/agent-opd-20261105/submit.py` with `--name agent-opd-native-h800 --gpu-type H800 --gpus 8 --replicas 2 --cpus 48 --memory 600 --group codesign` and the pinned image recorded above. The exact worker command was:

```bash
export LD_LIBRARY_PATH="/usr/local/cuda-13.0/compat${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" && exec /opt/sglang/bin/python3 /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/rjob_warmup.py --manifest /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-05_agent_opd_warmup/evidence/glm-replay-parent.json --student /mnt/codesign-exp/ycfeng/steptron/behavior-turn-replay-step3p6/glm-native-20261103/models/zai-org/GLM-4.7-Flash/7dd20894a642a0aa287e9827cb1a1f7f91386b67 --teacher /mnt/codesign-exp/ycfeng/steptron/behavior-turn-replay-step3p6/glm-native-20261103/models/whitecircle/GLM-4.7-Flash-Coder/d3c65039ae0797fb41d87cfa0c26438d7c425aa9 --output-root /mnt/codesign-exp/ycfeng/miles/agent-opd/warmup-20261105-h800 --shared-dir /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-05_agent_opd_warmup/evidence/native-warmup-h800 --gpu-type H800 --nodes 2 --gpus-per-node 8 --num-rollout 2 --startup-timeout 600 --training-timeout 3600
```

Expected: 16 actual H800 GPUs; two normal finite updates, nonzero gradients, changed published weights and native token/R3/logprob inspection. Actual: requested allocation shape is confirmed; GPU runtime and optimizer observations are pending.

## H800 first attempt: FAIL before Python; command wrapping fixed on CPU

`exp-1105-130232-725485` ended Failed at 13:06:43 HKT. Job UID `5f0b16ab-c269-41cf-b090-8e612eca7ca5`; replica `cfcd2084` UID `4bde48ca-33bd-47c9-9c4a-dd624befaf9d` on gpu-h800-0056 started its container at 13:06:34, then exited 127 / Error at 13:06:36. The exact incident log contains `bash: line 1: exec: export: not found`. `RJob.submit_rjob` wraps a local-mounted command with `cd SOURCE && exec COMMAND`; an entrypoint beginning with export becomes an invalid exec of a shell builtin.

CPU command reconstruction used `/usr/bin/python3`, Bash and Python shlex quoting. The original `bash -lc 'cd SOURCE && exec export ... && exec PROBE'` returned 127 with the same error. The corrected outer command execs `bash -lc INNER`, where INNER performs the export before execing Python. It returned 0 and printed WRAPPED_COMMAND_PASS after asserting the CUDA compatibility directory was prepended. This reproduces and fixes command semantics only; actual H800 Python and GPU training remain unverified. The earlier pinned image observations independently verified `/opt/sglang/bin/python3`.

Sibling `c4ca4238` UID `9b6e74d9-c0f8-4a8c-8a33-d899a4de07e8` on gpu-h800-0415 was still creating its container when the RJob failed. Its stop annotation names `system:serviceaccount:kubebrain:rjob-controller`; stopTimestamp 13:06:43 follows the other replica's error. Its final container exit code is UNKNOWN. The local launcher's Job Stop at 13:06:44.956 is later cleanup. There is no initiating preemption or OOM evidence in returned incident data.

RCA used the installed collect_failure_evidence.py through the existing personal Python 3.10.6 / brainpp 2.8.6 wrapper. Window 2026-11-05T05:06:25Z through 05:07:10Z, timeout 12s, exact job/replica names and personal creator. Logs returned 33 failing-replica rows and 0 sibling rows, below limit 3000. Live Events 9/11 and 9/4, historical Events 8/4 and 8/2; all pages completed. Existing DeepScan count 0. Both all-operation audit queries for both replicas timed out at 12s, so audited stop-request details remain unavailable. This query failure does not invalidate the observed shell error or container/stop timeline. No Python receipt or cloud warmup output was produced.

Consumed raw RCA files were removed immediately. Real optimizer updates remain 0.

## Corrected H800 submission

Local launcher 8731 created `exp-1105-130933-760790` at 13:09:33 HKT. Same submission flags and allocation as the first H800 attempt; name `agent-opd-native-h800-bash`. The corrected exact user command is:

```bash
bash -lc 'export LD_LIBRARY_PATH="/usr/local/cuda-13.0/compat${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" && exec /opt/sglang/bin/python3 -u -B /data/ycfeng/sota-engine/miles/tests/manual/agent_opd/rjob_warmup.py --manifest /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-05_agent_opd_warmup/evidence/glm-replay-parent.json --student /mnt/codesign-exp/ycfeng/steptron/behavior-turn-replay-step3p6/glm-native-20261103/models/zai-org/GLM-4.7-Flash/7dd20894a642a0aa287e9827cb1a1f7f91386b67 --teacher /mnt/codesign-exp/ycfeng/steptron/behavior-turn-replay-step3p6/glm-native-20261103/models/whitecircle/GLM-4.7-Flash-Coder/d3c65039ae0797fb41d87cfa0c26438d7c425aa9 --output-root /mnt/codesign-exp/ycfeng/miles/agent-opd/warmup-20261105-h800 --shared-dir /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-05_agent_opd_warmup/evidence/native-warmup-h800 --gpu-type H800 --nodes 2 --gpus-per-node 8 --num-rollout 2 --startup-timeout 600 --training-timeout 3600'
```

This retains the platform local-mount wrapper and only places the required export inside an executable bash entrypoint. No worker package changes or training parameter changes.

## Actual H800 runtime and allocation: PASS

Corrected job `exp-1105-130933-760790` is Running on gpu-h800-0056 and gpu-h800-0415. Personal API verifies creator i-fengyicheng, codesign, non-preemptible, current-local NFS 100.96.128.195, two replicas with 8 GPUs / 48 CPU / 600000 Mi and both RDMA limits. Both actual runtime reports list eight NVIDIA H800 devices.

Both workers run `/opt/sglang/bin/python3`, Python 3.12.16, Torch 2.14.1+cu130, Transformers 5.19.0, Ray 2.58.1, SGLang 0.5.24.dev80+g056f871, Polars 1.42.1 and Safetensors 0.8.0. Source revision is 26a1ad72f8be17bb265fdd52b290dd6016ad56d7; both targeted source_status lists are empty. This revision adds records to the previously committed H800 code.

All 16 GPUs execute the native runtime probe's FP32 elementwise reduction and BF16 cuBLAS multiplication. Expected/actual squared sum 10416; expected/actual every matrix output 16. Both workers load `/usr/local/cuda-13.0/compat/libcuda.so.580.126.20` and return driver API 13000. Expected GPU count/type, imports and kernels PASS. Ray/communication, models, optimizer and numerical alignment require separate observations.

## Actual H800 independent transfer worlds: PASS

The same allocation passed weight_sync_probe.py with eight trainer ranks, four student-inference ranks and a separate five-rank transfer world. Both sender and receiver use channel bounds 8. BF16 tensor broadcast expected/actual sums 496 (version 0) and 528 (version 1), including all four receivers. Independent parent reductions expected/actual 36 for the trainer world and 10 for inference, before and after transfer. This verifies communication isolation on both actual H800 nodes. Both nvidia-smi outputs report 81559 MiB per GPU and driver 570.124.06. The platform's missing `ip` executable diagnostic is the same non-blocking P2P-probe message observed previously; all workload runtime/communication checks above completed. Native full-model synchronization and optimizer updates are still pending.


## H800 engine device binding: FAIL before optimization

Exact job exp-1105-130933-760790 is Stopped at2026-11-05T05:19:27Z after the authorized stop script; launcher8731 exited1. Native run261105-051021-ev3r produced24 env reports but no optimizer event, rollout/train dump or weight publication. Updates=0.

Worker gpu-h800-0056 inherited CUDA_VISIBLE_DEVICES=2,3,0,1,4,5,7,6. The student context local_gpu_ids=[2,3,0,1] became --base-gpu-id2 --tp-size4 --gpu-id-step1, so SGLang used local2,3,4,5. Teacher base4 used4,5,6,7. Overlap4/5 is established by native argv and the pinned SGLang GPU-index formula. Ray2.58.1 get_gpu_ids returns IDs from the original visibility mask; the generic Miles remapper correctly preserves requested order. The loss of the remaining IDs occurs at the inference-spec launch consumer.

Student reported28.75GB weight memory and failed every TP rank with Loaded weights leave no GPU memory for the KV cache under mem-fraction-static0.75; minimum0.7512. Teacher had14.37GB weights and28.79GB KV. Device overlap plausibly caused the planning failure; successful isolated initialization must test this inference. No memory-fraction increase is justified before that test. Regression covers identity, actual reordered and interleaved masks, two disjoint four-GPU engines, and platform-specific visibility environment selection.


## Device isolation CPU regression: PASS

The engine command now binds only ctx.gpu_ids in its subprocess through the platform visibility variable and uses base_gpu_id0. Ray worker and generic remapper contracts remain unchanged. This overrides inherited visibility because placement owns device selection. CUDA/HIP/TPU variable selection belongs to Platform; no call-site hardware branch was added.

Environment: /data/ycfeng/envs/miles-agent-opd-cpu/bin/python, Python3.12.13, pytest9.1.1, Torch2.11CPU, pinned SGLang056f871 source. All commands use PYTHONPATH=/data/ycfeng/tmp/agent-opd-20261105/sglang-source/sglang-056f871a7ee8b4573832049011f0fdf52589cfd8/python:/data/ycfeng/sota-engine/miles, TMPDIR=/data/ycfeng/tmp and PYTHONDONTWRITEBYTECODE=1.

- RED: python -m pytest tests/fast/ray/specs/test_inference.py -k TestEngineBaseGpuId -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/agent-opd-20261105/gpu-binding-pytest. Four failures in1.94s: no isolation prefix under identity/reordered/interleaved masks, and missing platform variable consumer.
- GREEN: python -m pytest tests/fast/ray/specs/test_inference.py tests/fast/utils/workers/test_ray_worker_manager.py tests/fast/utils/test_misc.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/agent-opd-20261105/gpu-binding-pytest-green. 308PASS in7.65s. Both four-device engine sets match their allocation and are disjoint; existing ID-order and worker lifecycle checks pass.
- Related: python -m pytest tests/fast/test_platform_contract.py tests/fast/utils/test_platforms.py tests/fast/backends/sglang_utils/test_sglang_engine.py tests/fast/utils/external_utils/command_utils/helm_backend/launcher/values/test_pool_entry.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/agent-opd-20261105/gpu-binding-pytest-related. 105PASS,23SKIP in6.19s. GPU/TPU-dependent cases retain their existing skips on this CPU host. No new failure.
- git diff --check: PASS. Ruff executable is absent from the existing CPU environment; no package was installed for this optional check.

Real GPU initialization and OPD numerical acceptance remain required. CPU launch correctness alone does not establish the absence of an H800 memory or training error.


## Isolated-device 16H800 rerun: runtime PASS, optimization pending

Local personal Python submission exp-1105-132957-419084 at13:29:57HKT; launcher13179 remains alive. Creator i-fengyicheng, codesign, nonpreemptible,2×8H800,48CPU/600000Mi per replica, bothRDMA resources, pinnedimage165ff0be and localNFS100.96.128.195:/data/ycfeng/sota-engine/miles. Nodesgpu-h800-0029/0056. Head image pull completed and container started05:34:43Z; bothreplicas are Running.

Both runtime receipts confirm committedsource4188258a630041f8a91f7c13edc3b22c9055ac20,Python3.12.16,Torch2.14.1+cu130,Transformers5.19.0,Ray2.58.1,SGLang0.5.24.dev80+g056f871. Actual16NVIDIAH800,81559MiB/driver570.124.06; existingcuda-compat580.126.20/driverAPI13000; all16FP32sum10416/BF16matmul16PASS. Ray registers two distinctnodes and16GPU. Independentweight-sync probePASS with matchingchannelbounds8 and intacttrainer/inferenceparentworlds.

The worker command is the recorded corrected bash-wrapped command, with identicalmodels/manifest, num-rollout2,startup-timeout600,training-timeout3600 and mem-fraction-static0.75. Native run261105-053527-goqu; cloud /mnt/codesign-exp/ycfeng/miles/agent-opd/warmup-20261105-h800/exp-1105-132957-419084/261105-053527-goqu. Actualenginebinding and optimizer/numerical inspection remain pending.

Old outputcleanup exp-1105-132840-138098 Succeeded05:32:48Z, solecontainerexit0/restart0. It removed13files/4,497,154bytes only from the previous130933cloudpath. Read-onlySSH confirms absence. Worker-root-owned localreceipts were removed with sudo scoped to the exactpreviousjobdirectory. No sharedassets or globaltrash cleanup.


## Real engine isolation PASS; native trainer initialization FAIL

132957 endedFailed05:43:48Z with0optimizerupdates. ActualSGLangsubprocesscommands bindstudentCUDA_VISIBLE_DEVICES=0,1,2,3 andteacher=4,5,6,7; bothTP4 anddefaultbase0. Studentweightsfinished05:41:51Z,14.37GBperGPU/free63.83GB. Original0.75memoryfractionpassedKVplanning;HTTPstartupcompleted05:42:14Z. post-warmupfreeze_gcfailed withConnectionRefused, butpinnedhttp_server.py catchesRequestException and logsawarning; thisisnotaninitiatingtrainingexception.

Initiatingtrace05:43:24Z: Megatronoptimizer _get_param_groups invokesall_gather_object; NCCL2.30.7 reportsncclInvalidUsage / Bootstrap:no socket interface found. All8trainerenvreports ongpu-h800-0056 containNCCL_SOCKET_IFNAME=ens20np0, despiteworker-init/platformNVSHMEMselectorens22np0. Driverongpu-h800-0029 correctlyusesens20np0. RayCommandBackend._ray_env_vars automaticallyforwardedthishead-onlyNICname toallworkers. TheindependentNCCLprobe, whichretainsnodeenvironment,passed.

CPUfeedback: PYTHONPATH=/data/ycfeng/sota-engine/miles TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/utils/external_utils/command_utils/ray_backend/test_backend.py -k TestNodeNetworkEnvironment -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/agent-opd-20261105/network-env-red. Result1FAIL1PASS in1.16s: inheritedlauncherens20np0 overwritesworkerens22np0. Explicitinterfaceoverride andfixedchannelcontrols alreadyPASS.

Fix: removeautomaticNCCL_SOCKET_IFNAME/GLOO_SOCKET_IFNAME forwardingfromRaybackend; workersinheritindividualplatformNICnames. Explicitextra_env_vars retainsnormalprecedence. NCCLdebug/channelsettings remainunchanged. Verifyfullbackend/launcherchecks, thenreruntheoriginal16H800recipe. Thisisa root-causeconfigurationrepair, withoutarbitraryNICnames,memorytuning orerror-suppression.


## Network environment fix CPU validation and RCA

GREEN command uses the same isolatedPython3.12.13/pytest9.1.1 environment with pinnedSGLangPYTHONPATH:

python -m pytest tests/fast/utils/external_utils/command_utils/ray_backend tests/fast/launch_scripts tests/manual/launch_scripts -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/agent-opd-20261105/network-env-green

Result601PASS,18FAIL,50ERROR in20.92s. All17Raybackend casesPASS, including inheritedper-nodeNICpreservation and explicitoverride/channelcontrols. The68launcher failures retainthe recordedbaselinecategories/counts; no launcherrecipe/snapshotchange. gitdiff--checkPASS. TheNICcopyrepairistworemovedautomaticenvkeys, withno trainalgorithmchange.

RCAexactRJobUIDa5ab46b8-9254-4506-8893-0d5ae70b3b6f. FailingheadreplicaUID3d002713-9cde-40e4-8784-84ba174c28ef ongpu-h800-0029 containerexit1/Error at05:43:43Z/restart0. PlatformstopTimestamp05:43:47Z andFailedfinish05:43:48Z followthe05:43:24Ztrainerexception. SiblingUID01d304ba-40f4-4711-8de8-e02686d0767c ongpu-h800-0056 closedbyrjob-controller at05:43:48Z; cachedcontainerstate remainsrunning,soterminalexitcodeUNKNOWN. LauncherJobStop05:43:51Z islatercleanup.

Collectorcommands: existingpersonal_exec.sh invokes installedstepmind-gpu-worker/scripts/collect_failure_evidence.py withoneexact--replica percall,expectedcreatori-fengyicheng,credentialdirbrainctl-auth-i-fengyicheng,start2026-11-05T05:43:15Z/end05:44:05Z,timeout12,outputs tasktmp/rca-isolated-head andrca-isolated. Eachcompleted6/8readcategories. Head/siblingincidentlogs1042/0rows,belowlimit3000. Historicaljob9events; historicalreplicas5/1;livejob2;livereplicas0/2. Allreturnedpagescomplete; existingDeepScancount0forboth. Fourall-operationauditqueriestimedoutat12s. AuditedinitiatingstopdetailsUNKNOWN. ReturnedincidentdatadoesnotestablishpreemptionorOOM; nativeNICmismatchanditsCPUreproductionestablishtheapplicationconfigurationfailure.

Task-owned failedcloudoutput24,494,868bytesawaitsexactcleanup; sharedmodel/datasetunchanged. RawRCA/logsaredeletedafterthisMarkdownconclusion.
