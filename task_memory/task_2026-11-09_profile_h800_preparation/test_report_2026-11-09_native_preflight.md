## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record the candidate H800 payload, genuine in-place visual receipts and successful pinned-image D34 source/request parity. |

# H800 Capacity Prerequisite Preflight

## Scope and outcome

CPU preflight passes for the candidate36-H800 A/r256 prerequisite. The review's later response-budget finding is fixed in`0e7e0df3` and its closure independently verified; native GPU acceptance remains open. Configuration files are`h800_capacity_config.json`, `h800_gpu_policy.json`, and`h800_capacity_sglang.yaml` in this task directory. Working directory for local commands is`/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`.

| Check | Passing condition | Observed result | Verdict |
| --- | --- | --- | --- |
| Resource builder |36 H800/codesign,4×8 student plus1×4 teacher | Exact submitter dry-run returns36, four student replicas, explicit null personal ceiling | PASS |
| Native engine resolution |8 TP4 engines;2 colocated and6 dedicated | Original SglangConfig resolver returns GPU groups8/24 at offsets0/8, engine offsets0/2; only first group offloads | PASS |
| Native argv |128K context,112K prompt,16K response, two updates,256 slots,1800s acquisition | Each expected flag occurs exactly once with the requested value | PASS |
| HF schedule |No checkpoint due for this prerequisite | `save_interval=None`, no emitted interval flag; native periodic predicate false for both updates | CPU PASS |
| Native visual exclusion |Genuine complete filter for original paths |9254 conversations;102 exclusions,10008 excluded eligible targets; all8 files scanned, no filter failure codes | PASS |
| Actual Qwen/source parity |Real native prefix conversion, source identity and16K native request budget |9 selected prefixes pass;5 eligible requests each capped16384;4 oversized prefixes skipped; actual registry factory/request pass | PASS |
| Replay-to-request budget |Real SweReplay preserves16K |`0e7e0df3` removes both overrides; real replay/request regression RED126706/16385→GREEN16384/16384; remaining1 and seed preserved;62 affected PASS | PASS |
| Native GPU/runtime |Actual H800, synchronization,231/256 admission, two ACKs and second scoring |Not submitted at this checkpoint | NOT VERIFIED |

## Local resource and argument checks

Python3.12.13: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.submit_swe_opd \
  --config task_memory/task_2026-11-09_profile_h800_preparation/h800_capacity_config.json \
  --pair A --protocol r256 --receipt /data/ycfeng/tmp/agent-opd-image/h800-dry-run-receipt.json --dry-run
```

The dry-run does not create the requested receipt or contact the platform. `_config` and `_training_args` were invoked with the same config and an inert teacher URL; `shlex.split` verified exactly one occurrence of each value: seq/context/SGLang context131072; prompt114688; response16384; tensor parallel4; actor nodes1/GPUs8; rollout GPUs32; bank slots256; acquisition1800; updates2. The real `should_run_periodic_action(i, None, None, 2)` returned false for both `i=0,1`.

The actual submitting interpreter also passed the same dry-run: `/data/ycfeng/tmp/stepmind-env/bin/python` (Python3.10.6), from`/data/ycfeng`, with`STEPMIND_BACKEND=rjob` and`PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity:/data/ycfeng/steptron`, all command paths made absolute. Output:`evidence/h800-submission-dry-run-20261109.json`. Assertions verify36 GPUs, student4×8/teacher1×4, null personal ceiling and both student RDMA resources (`mellanox.com/mlnx_rdma:1`, `rdma/mlnx_shared:8`). It does not claim a free-capacity count or replace the fresh serialized admission at submission.

The real `_RawSglangConfig.from_file_arg` and `SglangConfig.resolve` consumed the configured YAML with the corresponding native role/placement values. All assertions and serialized resolved objects are represented in`evidence/h800-native-layout-20261109.json`; this is configuration resolution, not engine construction. A first evidence-write attempt failed because the new evidence directory had been created by the root worker. Only that task-owned new directory's owner was corrected, then the identical assertions and evidence write passed.

## Genuine native in-place exclusion receipts

RJob`exp-1109-164358-350923`: creator`i-fengyicheng`,8CPU/0GPU,32GB, Succeeded08:50:45Z. Local launcher used the personal Python backend from`/data/ycfeng`; actual NFS source/target is`100.96.128.195:/data/ycfeng:/data/ycfeng`. Exact pinned image is`sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`. API terminal/resource/creator/mount evidence is`evidence/native-input-preflight-jobs-20261109.json`.

Worker command:

```bash
prlimit --as=32212254720 -- timeout 1800s /data/ycfeng/envs/openmopd-py312/bin/python -u -B \
  /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity/tests/manual/agent_opd/prepare_swe_visual_filter.py \
  --native-repo /data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9 \
  --source-manifest /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/source-audit-20261109/swe1003-source-manifest.json \
  --output-dir /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity/task_memory/task_2026-11-09_profile_h800_preparation/evidence/native-visual-in-place \
  --workers 1 --max-prompt-length 131071
```

The final length argument belongs to the unchanged native Step-tokenizer reservoir diagnostic, not Qwen rollout filtering. Python3.12.13, Transformers4.57.6, ijson3.6.0, loguru0.7.3; `TOKENIZERS_PARALLELISM=false`, no bytecode writes. The resource and timeout limits cover the producer and child. Total native calls took397.38s. Retained wrapper only calls the existing native baseline/visual/filter APIs; native hashes and statistics are in`evidence/native-visual-in-place/runtime.json`. The complete filter matches the original posttrain file metadata. No source data copy, mocked receipt, or copied-source receipt rebinding occurred.

The native producer's temporary-file publication created three new root-owned0600 receipts. After the job, those three files alone were made0644 for the host reader. The retained wrapper now sets those receipt modes and refuses an incomplete filter. This publication-only change does not require rescanning the unchanged sources; the already-generated complete receipts were inspected directly.

The native audit environment initially lacked`ijson` and`loguru`. A public PyPI request timed out. The documented mirror command succeeded without changing existing packages:

```bash
UV_CACHE_DIR=/data/ycfeng/tmp/uv-cache uv pip install \
  --python /data/ycfeng/envs/openmopd-py312/bin/python \
  --index-url http://mirrors.i.basemind.com/pypi/simple/ --trusted-host mirrors.i.basemind.com \
  ijson==3.6.0 loguru==0.7.3
```

Actual native tokenizer construction and the completed native job verified the repair. Source:`/data/ycfeng/stepfun-env-handbook/python-package-mirror.md`.

## Original-source D34 parity

Successful RJob`exp-1109-172310-849823`: same personal creator, exact image,8CPU/0GPU/32GB and current-host NFS source, Succeeded09:28:42Z. Worker uses the image's`/opt/sglang/bin/python3`, Python3.12.16, Transformers5.19.0. The complete exact argv, worker-shell command, expected import root and image are retained in`evidence/native-inputs-in-place-d34/worker-command.json`; the script path and actual argv are repeated in`h800-d34-input-parity.json`. Limits are30GiB address space and600s; the shell explicitly exports the project PYTHONPATH before executing the checker. GPU scheduling is not involved.

Observed `status=PASS` covers native prefix/conversion identity, tools/thinking/target masks, independent cursors, actual file/EOF boundaries and the normal typed registry factory. Selected prompt lengths are4366,5707,35290,87770,137552,160643,184310,256934,87374. Five eligible prompts receive a16384 maximum; four oversized prefixes are rejected. The actual factory uses`RolloutConfig`, real default/config merge and the genuine visual filter; its first source UID is`00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6:0:2`, prompt4366, constructed request max16384. No HTTP request was sent. All source files are original posttrain paths; the full source manifest is streamed and verified by the ordinary factory.

Historical failures are preserved:

- `exp-1109-170837-174061`, Failed09:13:07Z: import failed with`No module named tests.manual`; no data check ran. `spawn_tasks()` overwrites resource PYTHONPATH with the code mount at`steptron/utils/stepmind.py:917`; exporting the repo inside the worker shell uses the production launcher's existing ordering. Filtered failure readback is retained in`/data/ycfeng/tmp/agent-opd-image/h800-d34-native-input-parity-failure-20261109.json`.
- An intermediate local launcher had`NameError: worker` from nested shell quoting and created no RJob. Log:`/data/ycfeng/tmp/agent-opd-image/h800-d34-native-input-parity-workerpath-20261109.log`. The final command precomputes its log path, is serialized and round-trip checked before submission; it succeeds as recorded above.

The nine selected prefixes are not a whole-corpus Qwen length census. Synthetic boundary checks and actual-file closing-bracket checks retain their stated scope. The parent's independent full112K audit, native teacher/model compatibility, GPU memory, NCCL behavior and actual capacity remain separate acceptance items.

## Prelaunch review finding

Reviewer`profile-h800-prelaunch-review-20261109` identified one P1 at`swe_replay.py:331–337`: the replay path replaced the source sample cap and generation sampling cap with total remaining context. The source parity check did not traverse that caller. Fix`0e7e0df3` preserves the existing sample/default budgets and adds only the original seed. The real replay→request regression failed with126706/16385 before the fix and produces16384/16384 after it, also preserving a one-token remainder and seed1729. The62 affected checks pass; physical POST and tokenizer are fixtures, with exact commands and baseline lint limits in`test_report_2026-11-09_capacity_input_lengths.md`.

The same reviewer inspected the fix, regression and report and closed P1 with no remaining findings. Other configuration/role/resource/source/soft-gate conclusions remain unchanged. This permits moving to the authorized native prerequisite, not declaring CUDA/NCCL or capacity acceptance.
