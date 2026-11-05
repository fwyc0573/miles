## Modification History

| Date | Change |
| --- | --- |
| 2026-11-05 | Assess both OPD model pairs; verify Frog/Qwen tokenizer prerequisites and retain numerical qualification limits. |
| 2026-11-05 | Reconcile 72 requested H800 GPUs against exact replica/container states and record consumption cleanup. |
| 2026-11-05 | Record twenty verified updates, incomplete checkpoint save, save diagnostics and question-sharded evaluation. |
| 2026-11-05 | Start the bounded20-update learning and20×4 native benchmark verification. |

# Twenty-update OPD learning test

Status: 20 normal optimizer updates verified offline; final native checkpoint save failed. Root cause remains UNKNOWN. No complete post-update-20 export or benchmark score is available. A save diagnostic and original-model question shards are running or queued.

Expected:20normal finite optimizer updates,80distinct glm5.2 turns, exact post-update20 export,20fixed questions×4 seeds with80valid native grader outcomes for both original and updated student. Tool execution and tests determine resolved/unresolved; infra/invalid outcomes remain missing. Cleanup removes all transient files after consumption.

Initial evidence: qualified two-update branch38ff410a0a8a3ca5fec8b3ce5a6ad8e3325200e7, current clean workingtree,109GiB local free. Relevant current source contracts: train.py final-save ordering and skipped final publication; miles/backends/megatron_utils/hf_export.py complete-marker export; referenced Ticket06 fixed50 manifest and native RunCheckPipeline.


## CPU preparation checks

Command: `PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/rollout/test_sglang_opd_request_contract.py tests/fast/rollout/test_opd_config_contract.py tests/fast/backends/training_utils/loss/test_opd.py -q`. Python3.12.13/pytest9.1.1:20PASS in3.85s. These check existing OPD request/loss contracts; they do not validate20-step learning or benchmark outcomes.

AST parse of modified prepare_glm5_2.py/rjob_warmup.py and new checkpoint_identity.py PASS; exported hook import PASS. Native evaluator imports of toml, swe_agents.cli.run, swe_agents.models.step_align, step_align.model.stepchat and playground.agenticeval.sweagents_swe PASS in the existing mounted Python3.10.20 environment. Exact interpreter: `/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/.venv/br-native-swe-py310-1008am/environment/bin/python`; native SWE/StepAlign source: `/data/ycfeng/steptron/.worktrees/step3p6-native-eval-1015z/third_party/`. Existing sandbox credentials are present; values were not printed.

The20-update adapter changes only bounded input count,4096-token response cap, native final save and export identity. Four rows per rollout/global batch and20rollouts mean20optimizer updates if every native outcome is normal.80different prompts are selected from20different groups per category under<=61440prompt tokens, with no wraparound; exact-source/hash checks execute before training. Original fixed175 membership and parent selection evidence are rehashed. This reuses inherited exact-text/marker exclusions and does not guarantee semantic paraphrase isolation.

Local source mount for this phase uses `/data/ycfeng` because Miles, the independently maintained Steptron input manifests and existing native evaluator environment are in different local directories. Expected NFS source remains the current local host, never the SSH server. Large outputs stay under the personal cloud learning namespace; local scratch is confined to `/data/ycfeng/tmp/agent-opd-learning-20261105` and deleted after consumption.


## Initial shared-mount import failure and repair

`exp-1105-153807-012700` failed before native runtime initialization,20updates=0. Exact RJob UID60113a67-cc0a-48bd-a1cd-c82130b59a4b; replica c4ca4238 UID644c9ced-f59d-40c6-804f-30075900e3be on0415, exit1/Error07:38:35Z; platformFailed07:38:41Z. The incident API returned36rows in07:38:25–07:39:00Z, ending with `ModuleNotFoundError: No module named 'scripts'` at rjob_warmup.py:21. Personal local NFS and16GPU requests were correct. `spawn_tasks` atsteptron/utils/stepmind.py:917 overwrites PYTHONPATH with the mountroot; no runtime library or training change is needed.

Hypothesis/falsifier before rerun: explicit `export PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron` in Bash after platform mount preparation must make the same import pass; the same traceback would falsify the repair. CPU Python3.12.13 reproduces REDexit1 with PYTHONPATH=/data/ycfeng and GREENexit0/rollout_batch_size4 with corrected paths, cwd=/data/ycfeng.

Collector: `timeout 60s bash /data/ycfeng/tmp/agent-opd-learning-20261105/personal_exec.sh /data/ycfeng/stepcode-codex-home/.stepcode/codex/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py exp-1105-153807-012700 --replica exp-1105-153807-012700-c4ca4238 --expected-creator i-fengyicheng --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng --start 2026-11-05T07:38:25Z --end 2026-11-05T07:39:00Z --timeout 12 --output /data/ycfeng/tmp/agent-opd-learning-20261105/rca-mount-import`. Six of8query categories returned; both all-operation audits timed out. Existing DeepScan0, historical root12events. Initiating manual-stop fields UNKNOWN; root-cause import traceback is independent of unavailable audits. All consumed raw RCA files are disposable.

## Prepared inputs and benchmark adapter

Input job `exp-1105-154320-374829` succeeded at 2026-11-05T07:47:51Z; container exit0/Completed/restart0. Independently read frozen membership from personal cloud:20 tasks (2 astropy,18 django), seeds1729–1732, temperature1/top_p0.95, denominator80. Question dataset SHA256 `03a9beccd8ef6c4de38e1c24a51ffe9193d8afc2e0e14680e0bc3b258f5007af`; parent SHA256 `260c24512ed780274bcc735c8c264bb15309f79b8fd33d6bda64e86994d792aa`. All20 belong to unchanged fixed175 exclusions. The actual prepared training receipt contains80unique UIDs, prompt tokens10366–57113,20/category.

Existing CPU interpreter `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python` executed the export-value fixture: changed tensors PASS; wrong completed-update identity, unchanged sampled values and mismatched shapes rejected PASS. Fixture removed. Native Python3.10.20 `-B tests/manual/agent_opd/native_benchmark.py --help` with the recorded Steptron/SWE/StepAlign/Harbor/datahub/step_env paths exited0. The adapter uses the unchanged native RunCheckPipeline generation, tools and grader; grading validates the original outcome function. Per-attempt infrastructure/invalid outcomes remain missing.

Host Python3.10.6 fixture exercised `summarize_benchmark.summarize`:20×4 scores0.50→0.75 produce paired difference0.25, question-bootstrap95% interval[0.10,0.45] with10000 resamples/seed20261105. Invalid actual seed gives79valid attempts, avg@4=null and no paired claim. These are synthetic checks of denominator/accounting only, not measured model results. Fixture removed.

Benchmark resource plan: one4H800 TP4 job per model, original evaluation concurrent with16H800 training; updated evaluation only after the actual final export. Identical BF16/FA3/deterministic/GLM reasoning+tool parsers/131072 context/staticmemory0.75 settings. Four native seed pipelines, concurrency1 per seed, real sandbox tools/unit-test grader. SGLang JSON request logs verify actual sampling_seed,n,temperature/top_p in each generation interval; one active native pipeline per seed makes interval attribution unambiguous within each model server.

## Actual original-model evaluator startup

Personal job `exp-1105-155335-867117` isRunning: creator i-fengyicheng,codesign,one4H800 replica,24CPU/300000Mi,bothRDMAresources,100.96.128.195:/data/ycfeng localmount,pinnedimage. Worker0044 started07:59:52Z/restart0. Actual/model_info confirms the pinned originalGLM student path, servedname agent-opd-step0, weight_version0, glm45 reasoning parser and glm47 tool-call parser. Four native pipelines each load exactly20ordered questions,repeat1,run/checkconcurrency1. Actual SGLang request.received JSON confirms seeds1729–1732,n1,temp1/top_p0.95, independently of config parsing. Native requests have returned real token usage/weight-version metadata. The later resource verification records three completed native grader outcomes; the full80-attempt benchmark remains incomplete.

CPU request/config/loss checks repeated after adapter preparation:20PASS in3.65s, Python3.12.13/pytest9.1.1; no further broadening is required without new concerns.

Actual original sampling-default check: SGLang received top_k=-1,min_p0,presence/frequency penalties0,repetition_penalty1,max_new_tokens=null,ignore_eosFalse,skip_special_tokensFalse, in addition to the frozen seed/n/temp/top_p. Original generation_config defines eos[154820,154827,154829],pad154820 andtemperature1; it has no top_k setting. Native SnapshotPublisher.write_model copies the original non-weight/non-index metadata unchanged at lines91–95, including config/tokenizer/generation_config; compare actual copied files again after export. This resolves the investigated default-config concern without changing sampling.

The dependent updated benchmark waiter was stopped after the final save failed. There is no updated benchmark RJob. Resubmission depends on a complete actual post-update20 export and verified normal updates. Worker startup additionally checks finalHF .complete, rollout19/update20 identity, every exported tensor name/shape and changed sampled values before serving updatedweights. No updated evaluation job exists yet.


## 17:05 HKT continuation: twenty updates verified; final save failed

- Offline inspector `exp-1105-164845-421010` Succeeded, container exit0 at08:57:12Z. It checked all20 rollouts from failed learning job `exp-1105-154247-809306`; this does not change that training job's Failed status.
- Actual80 source UID/prompt-SHA256 pairs exactly equal the prepared80 pairs, with no duplicates. All20 same-token/R3 checks passed; sampled versions0–19 equal publications0–19. Final update20 was not published to inference.
- Generated completions contain 18 thinking turns, 50 body turns and 17 submit turns. Completion-category counts: {'control_only': 9, 'neither': 53, 'thinking_only': 10, 'control_and_thinking': 8}.
- Mean absolute same-token logprob difference across rollout means: range 0.005970–0.035865; maximum token difference 1.597615. TIS outside0.5–2 fraction maximum 0.002751. These are measured residuals, not a zero-parity claim. Last loss 0.04617585, grad_norm 12.71181965.
- Native torch_dist save started08:42:54Z; worker PID2227 on node0105 disconnected about7seconds later. Three partial distcp files total22.50GB; no .metadata/tracker/HF completion marker. Not recoverable as a completed checkpoint. Root OOM/preemption/segfault cause remains UNKNOWN; Sherlock userinfo401 and new QR monitoring ended unauthenticated.
- Next hypothesis test: a two-update run with the same models/topology/save/resource600000Mi per replica will exercise the same native save, with cgroup counters and bounded Ray logs retained before cleanup. An OOM counter increase or worker kill log can identify memory pressure; a complete save rules out a universally failing save path under this shape. No training algorithm or arbitrary memory scaling is changed.
- In parallel, evaluate remaining19 original questions using one4H800 TP4 job per question; retain original job's current first question. Each shard keeps allfour seeds, native5h per-question budget and6h outer budget. Initial maximum task allocation96GPUs including16GPU save probe and4GPU original job; queued jobs remain in FIFO, no duplicate submissions.


## Save diagnostics and question shards: implementation checks

Six changed/new manual adapters AST PASS; Black24.3.0 and isort5.13.2 format PASS; Ruff0.14.7 `check --no-cache` PASS. Formatter packages were installed in task temporary storage; the host Python3.10 lacks ensurepip, so the existing CPU Python3.12.13 installed them with `pip --target` without changing its dependencies. Installer warnings describe the pre-existing optional GPU stack and are unrelated to the manual adapter checks. The temporary formatter environment/packages are deleted after use.

After formatting, CPU Python3.12.13 `rjob_benchmark.py --help` PASS; native Python3.10.20 `native_benchmark.py --help` PASS with the recorded native Python path and `--task-index`. Formatting does not change native sampling/grading.

Actual failed worker node0105 replica `-c4ca4238` was queried for08:42:40–08:44:00Z with the exact job/replica UIDs. Six of eight RCA reads succeeded; all-operation audits timed out and no existing DeepScan result identified the initiating cause. The old authenticated October29 session now returns userinfo400; normal Feilian SSO reuse ended with a bounded Sherlock read timeout. No OOM or preemption diagnosis is inferred from these unavailable sources.

Save probe `exp-1105-170005-882383`, UID0d3ed9ef-e365-4ec3-95e0-b12e71e8c088, is queued/Starting. Confirmed personal creator, codesign, two8H800 allocations, each48CPU/600000Mi, pinned company image and100.96.128.195:/data/ycfeng source. Launcher session57076 remains alive. Original question shard launchers remain alive in session97672;19 exact job receipts have been created, some Pending/Starting. Capacity endpoint HTTP200 returned186 accessible machine records; this is not a reservation or proof of free quota. Task allocation cap96GPUs.


## Resource and cleanup verification

Commands: personal Python 3.10.6 / brainpp 2.8.6 through `bash /data/ycfeng/tmp/agent-opd-learning-20261105/personal_exec.sh <scratch>/audit_active.py`; exact read through `<scratch>/read_job.py exp-1105-155335-867117 --logs`. The audit filtered active jobs by creator and queried exact RJob and replica objects. These reads submitted or stopped no jobs. Consumed temporary audit files and raw query logs were deleted.

PASS at 2026-11-05T09:19:10Z: all 21 active codesign jobs matched current session receipts. Running + Starting requests totaled 72 GPUs (4 + 52 + 16); Pending requests totaled 24 GPUs; total active requests were 96 GPUs. Running containers accounted for 4 GPUs; two ContainerCreating replicas bound to node 0036 accounted for 8 GPUs. The remaining Starting requests, including both save-probe replicas, accounted for 60 GPUs and had PodScheduled=False, Unschedulable and no nodeName. The user's 72-GPU display is consistent with Running + Starting request accounting. The display implementation and hardware utilization were not queried. Independent step_main jobs were preserved.

PASS refresh at 2026-11-05T09:25:23Z: the two bound question shards had entered Running. Running containers and Running requests now both totaled 12 GPUs; Starting requests totaled 60 GPUs and remained unbound; Pending requests remained 24 GPUs. Running + Starting remained 72 GPUs. This confirms that the same request total can cover different container states over time.

PASS cleanup: job `exp-1105-170054-161169` Succeeded. It removed 215 files totaling 28,278,315,373 bytes; cloud and local failed-run directories were both absent afterward. Partial failed checkpoints are unavailable for updated-model evaluation. Shared original models and datasets remain.

At the earlier 17:19 HKT audit, PARTIAL benchmark: the first original-model task, `astropy__astropy-12907`, has three valid resolved outcomes (seeds 1729, 1731 and 1732), each with verified actual seed/sampling. Seed 1730 is still generating. Generation durations were 3738.97, 4053.83 and 4095.01 seconds; native grading durations were 106.64, 113.74 and 111.91 seconds. The 80-attempt avg@4 remains undefined. No updated-model score is available.

The initial temporary question-0 consumption guard ran in local session 93006; its later correction and completed consumption are recorded below. Its initial design was to verify the exact original job UID/creator, stop through rjob_stop.sh, wait for terminal replica status, then submit a personal 0-GPU RJob. That worker copies only eight temporary outcome receipts plus engine identity into `benchmark/original-question-00`, verifies four valid attempts with the existing reader, and deletes the exact original-job raw output directory. Both temporary scripts passed AST parsing before consumption. The nineteen existing question shards remain the source of all other questions.


## Training/inference alignment assessment for both model pairs

Assessment: neither pair is qualified as having fully resolved training/inference mismatch. Successful updates and enabled mitigation flags are separate from numerical qualification.

GLM-4.7-Flash student / GLM-4.7-Flash-Coder teacher: the actual H800 test verified 20 normal optimizer updates, unchanged source/completion token IDs, unchanged R3 replay arrays and matching sampled/published policy versions 0–19. The recorded rollout-level absolute logprob means range from 0.005970 to 0.035865; the maximum single-token absolute difference is 1.597615. The largest recorded fraction of ratios outside [0.5, 2] is 0.002751, or 0.2751%. These observations do not identify the source of numerical differences or establish an acceptable error budget. The inspector explicitly reports measured parity without an uncalibrated tolerance. TIS mask mode changes weights and masks; it does not make the inference and training forward outputs equal. Complete post-update-20 export and reload qualification remain pending after the save failure.

Qwen3.5-4B student / FrogNano-4B-2609 teacher: weights were previously fully downloaded and verified. The current read-only personal cloud check additionally compared tokenizer.json fields model, added_tokens, normalizer, pre_tokenizer, post_processor and decoder; all matched. tokenizer_config.json and chat_template.jinja bytes also matched. Both configs identify qwen3_5 / Qwen3_5ForConditionalGeneration, with text vocab_size=248320, hidden_size=2560 and num_hidden_layers=32. Neither model has a generation_config.json in these pinned directories. This is a tokenizer/template prerequisite check, not training/inference numerical evidence. No Frog/Qwen OPD training job, teacher-scoring validation, same-token Megatron/SGLang comparison or trained-weight reload is recorded for this task.

Command for the new prerequisite check: `ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng 'test "$(id -un)" = i-fengyicheng && python3 -'` with a scoped stdin script reading only config/tokenizer metadata from the two pinned personal cloud model paths listed in summary.md. No weights were copied, no GPU job was submitted and no raw model metadata artifact was retained. PASS applies only to the stated metadata comparisons.

The mismatch comparison is between the same student's training and rollout probabilities on identical tokens and policy versions. A difference between student and teacher probabilities is the intended OPD learning signal; equality of those two models is not the alignment acceptance criterion. Implementations inspected: scripts/run_glm47_flash_agent_opd.py, tests/manual/agent_opd/inspect_warmup.py and examples/infra_features/train_infer_mismatch_helper/mis.py.

Current execution update: save diagnostic exp-1105-170005-882383 is Running on nodes 0178/0128; runtime/Ray startup and four-turn preparation were observed, but save completion is not yet verified. All four first-question original benchmark seeds returned valid resolved outcomes. The original job is Stopped with replica finishTimestamp=2026-11-05T09:33:09Z. Its retained containerStatuses still shows the old Running snapshot; the temporary consumption guard was corrected to use terminal replica phase plus finishTimestamp. A direct native Pod read returned403 and does not establish live Pod state. The corrected local guard keeps cleanup submission and its receipt separate from this terminal-status verification.


Question-0 consumption PASS: corrected guard session 62319 submitted personal 0-GPU job `exp-1105-174121-815795`, UID `951bd60a-4179-4686-9801-825ad46bd501`. The job and replica Succeeded; container exit0/Completed/restart0 at09:41:33Z. Its business receipt reports 42 files / 98,215,176 bytes removed and four valid, resolved attempts copied to the temporary canonical root. Independent personal cloud reads verified all four canonical grading records. At09:44:03Z the SSH observer still saw an empty original directory but found zero files and zero bytes; directory absence is therefore not independently confirmed. The remaining empty directory is included in final task cleanup. Both temporary consumption scripts and their launch manifest self-deleted after completion; query logs were consumed and removed. The task still requires both complete 80-attempt benchmarks and exact post-update20 weights.


Continuation inspection on November 5 at 17:50 HKT: the exact save-diagnostic RJob and both replicas remain Running on nodes0128/0178, with creator i-fengyicheng, codesign, the pinned image and local NFS100.96.128.195:/data/ycfeng. Personal cloud read at09:50:39Z found native normal-step event for rollout0 and publication events0/1; no complete checkpoint metadata or HF identity marker existed in that snapshot. This does not settle the final-save hypothesis. A concurrent exact batch query found six original-question shards Running and thirteen Starting; the original serial job remains Stopped and failed-run cleanup remains Succeeded. GPU requests are not hardware utilization. No new GPU job was submitted in this continuation.

Inspected primary implementation: the GLM launcher fixes sampling temperature1/top_p1/top_k-1 and dropout0, enables R3 plus deterministic BF16/FA3 and TIS mask, while inspect_warmup.py compares trainer batch log_probs against rollout_log_probs on unchanged tokens. The TIS implementation explicitly changes weights and masks. These source checks support the stated qualification limits; they do not calibrate the remaining numerical error. Local disk inspection reports109GiB available on /data. Consumed exact replica logs and batch/capacity snapshots are deleted; active launcher manifests/receipts and native rendezvous files remain until their workloads finish.
