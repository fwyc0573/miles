## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Separate current acceptance state from historical preparation and recovery. |
| 2026-11-06 | Verify complete twenty-update HF, native terminal success and actual updated-model reload. |
| 2026-11-06 | Reconcile queued learning and active evaluation; reference timestamped progress. |
| 2026-11-05 | Correct current BaseMind and save-inspector status after resumption. |
| 2026-11-05 | Record failed short HF save, decoder/MTP qualification and bucketed explicit export repair. |
| 2026-11-05 | Record twenty verified updates, incomplete checkpoint save, save diagnostics and question-sharded evaluation. |
| 2026-11-05 | Archive the verified real 16 H800 OPD warmup and record its limits. |

# Agentic OPD Warmup

The additional twenty-update phase has completed twenty normal finite optimizer updates on sixteen H800 GPUs, the complete final HF export, native inspection and actual update20 reload. The paired native benchmark is still running. Final scoring, disposable cleanup and final branch synchronization remain incomplete. The timestamped measured state is maintained in [the learning report](test_report_2026-11-05_agent_opd_learning.md); [progress.md](progress.md) records queue and cleanup evidence.

The real GLM-4.7-Flash-Coder → GLM-4.7-Flash OPD warmup completed two successful optimizer updates on 16 H800 GPUs on November 5, 2026, following the user's temporary hardware change. Native inspection exited 0. Both containers exited 0 with no restarts, and the platform reported Succeeded. H200 training is not qualified by this result.

Training job: `exp-1105-141808-864508`; native run: `261105-062519-86os`; source commit: `0e78c5e5cf81cd2f9bc030f8ea21ed734dc95b32`. Personal creator: `i-fengyicheng`; quota: `codesign`; nodes: `gpu-h800-0105` and `gpu-h800-0157`. Each replica requested 8 GPUs, 48 CPUs, 600000 Mi memory and both platform RDMA resources. Local NFS source was `100.96.128.195:/data/ycfeng/sota-engine/miles`.

## Deliverables

1. Branch `agent-opd` in `/data/ycfeng/sota-engine/miles`, with personal origin `https://github.com/fwyc0573/miles.git`.
2. `examples/agentic_opd/glm_turns.py` and `examples/agentic_opd/rollout.py` preserve original token boundaries, reasoning, ordinary body, tool names/arguments, truncation status and source identity. Parsed fields do not replace training token IDs. The reward adapter keeps scalar rollout metrics separate from teacher token scores and uses the existing frozen-config copy mechanism.
3. `scripts/run_glm47_flash_agent_opd.py` configures sampled-token OPD, R3, TIS mask bounds 0.5–2, deterministic FA3, BF16, CPU optimizer offload and the existing GLM model definition. Eight GPUs train the student; four serve the student and four serve the frozen teacher. Static inference memory remains 0.75.
4. `tests/manual/agent_opd/prepare_glm5_2.py`, `rjob_warmup.py`, `runtime_probe.py`, `weight_sync_probe.py` and `inspect_warmup.py` provide input preparation, explicit H200/H800 checks, native execution and aggregate inspection.
5. `miles/utils/distributed_utils.py` fixes independent process-group initialization; `miles/ray/specs/inference.py` and platform visibility declarations bind engines to their assigned devices; `miles/utils/external_utils/command_utils/ray_backend/backend.py` preserves each node's network interface selectors. Existing regression tests cover these changes.
6. `docs/advanced/on-policy-distillation.md` documents the recipe. Exact commands, measured results, research sources and earlier failure evidence are in `task_memory/task_2026-11-05_agent_opd_warmup/test_report_2026-11-05_agent_opd.md`.

## Requested model assets

Authenticated Lark search returned no visible FrogNano result and three contextual Qwen3.5-4B documents without a verified asset path. This limited search does not establish company-wide absence. Following the handbook and Lark mirror documentation, the company HF mirror downloaded both pinned assets to personal codesign storage. All 22 files passed complete size/SHA256 verification: 18,685,617,357 bytes. VPS was unnecessary.

- `/mnt/codesign-exp/ycfeng/opd-assets/models/microsoft/FrogNano-4B-2609/b90468c11a913c1916b4542b4b7a530ec42024a4`
- `/mnt/codesign-exp/ycfeng/opd-assets/models/Qwen/Qwen3.5-4B/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`

The shared GLM weights and original Steptron glm5.2 dataset remain unchanged.

## Actual training and alignment

Four original glm5.2 turns from the referenced ticket07 task were used in each rollout. Prompt counts and hashes matched the source: 40380, 28408, 33616 and 10366 tokens. Original submit/thinking/body/editor/bash representations were verified. Eight newly sampled turns produced 2779 scored completion tokens; seven completed normally and one was explicitly truncated at 1024 tokens. The truncated turn retained its reasoning/body and was teacher-scored and consumed without token changes.

All eight trainer-rank outcomes were `normal` in each update. Both gradient norms were finite and nonzero; all eight native policy-loss debug calls were finite. Teacher, inference and training used identical token IDs. The full training R3 arrays equalled inference arrays, with shape `[sequence_length - 1, 47, 4]`. Completion weight versions matched publications 0 and 1. The first update changed 1368 published inference tensor checksums.

| Rollout | Loss | Gradient norm | Native logprob absolute mean | All-token absolute mean | p95 | Maximum | TIS outside [0.5, 2] |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.1218385722 | 8.0741624832 | 0.0228575670 | 0.0228575673 | 0.1842243075 | 0.5691769123 | 0 / 1137 = 0% |
| 1 | 0.1338641484 | 5.3127408028 | 0.0247820460 | 0.0253208224 | 0.1820047647 | 0.8846728802 | 1 / 1642 = 0.0609013% |

The native statistic uses the reducer rebuilt from TIS-adjusted masks; the inspector includes all sampled tokens. Small numerical differences remain. No token, routing or policy-version mismatch was found in these eight turns; exact bitwise parity and convergence are not asserted. The current driver does not publish the final optimizer update, so publication verification covers versions 0 and 1 only. Native generated tools were bash/editor; original submit serialization has separate source/CPU evidence. The initial two-update warmup did not qualify live multi-turn tool execution or H200 training. Native tool execution has since been observed in the ongoing benchmark; H200 training remains unqualified.

## Environment and regression evidence

Both workers verified Python 3.12.16, Torch 2.14.1+cu130, Transformers 5.19.0, Ray 2.58.1 and SGLang 0.5.24.dev80+g056f871. All 16 GPUs passed FP32 sum 10416 and BF16 matrix checks. Existing CUDA13 compatibility libraries were used; no host driver was changed. Ray registered two distinct nodes and 16 GPUs. Independent BF16 weight broadcasts passed sums 496/528 and parent reductions 36/10 with both NCCL channel bounds set to 8.

Both engines reported ready, TP4/base0/BF16/FA3/deterministic/routed-expert enabled. Actual launch masks were disjoint 0–3 and 4–7; weights used 14.37 GB per TP rank. All trainer ranks retained node0105's `ens20np0`; inference processes retained node0157's `ens22np0`, each matching its platform socket setting.

Relevant CPU evidence includes 413 passed GPU-visibility/platform checks with 23 existing skips, 17 passed Ray-backend checks, and 115 passed reward/OPD/conversion checks. Two existing local Ray/GCS object-store fixture startup errors remain documented. Existing broader launcher-suite baseline failures are also recorded; they were not represented as passing or repaired outside scope.

## Cleanup and synchronization

The native workers removed their own compilation, Ray, kernel and temporary caches before successful exit. All consumed local raw logs, copied manifest/configuration, samples/dumps/receipts and the 173 MiB temporary SGLang source were removed. Only code and Markdown conclusions remain in the task directory. Requested model assets, shared datasets, credentials and persistent Python environments were preserved.

Previous failed cloud outputs and the old H200 warmup dataset were removed. Final zero-GPU cleanup `exp-1105-144243-835275` succeeded at06:46:57Z; its container exited0/Completed with no restarts. Independent read-only SSH confirmed the completed141808 cloud root and oldH200 dataset are absent; the task cloud namespace contains no warmup data. The short cleanup log API returned0rows, so no unobserved file/byte count is asserted. Personal Running/Starting jobs were empty. Local free disk space is approximately110GiB. Archive commit `e975d4070989f869a53807c618b32c6fd58a2973` was pushed normally and independently matched `origin/agent-opd` via `git ls-remote`. Only task records differ from the qualified source commit; training code is unchanged. The final status commit records this completed synchronization; its SHA is reported with the completion response. All current H800 warmup deliverables and cleanup are complete. H200 qualification remains unverified.


## Earlier learning and save attempts (November 5; superseded)

The twenty-update learning phase was incomplete at the following earlier observations. Failed GLM job `exp-1105-183414-941283` completed twenty normal optimizer updates but failed before HF export at the synchronous driver's unrequested rollout checkpoint save. The driver fix has 23 passing CPU driver/actor regressions at revision `fea1302190a2489e3a359d9347c8d44f88862f7a`. The failed namespace and obsolete ACS evaluation outputs have been consumed and removed. The complete failed-run signal and numerical measurements are recorded in the learning report; they do not supply a recoverable update20 checkpoint.

Short qualification `exp-1105-195913-137332` completed two normal updates but failed during HF export at12:30:22Z. No safetensors or completion marker were written. The cgroup peak629144678400bytes nearly reached its629145600000byte limit; native workers aborted in the NCCL watchdog during Bridge save_generator. No explicit OOM or Ray memory-kill evidence is available, so memory pressure is a hypothesis rather than a confirmed initiating cause. Explicit export now reuses the existing weight publisher and bucketed writer; 44 CPU checks pass on the local host and pinned image, while actual GPU writing remains unverified. The existing zero-GPU inspection checks all tensor names/shapes, sampled changed values, the index and completion identity before consuming its outputs. A single local waiter will then submit the unchanged twenty-update population. Actual update20 reload and both complete BaseMind eighty-attempt cells remain required. Original question0 remains running with four seeds and has two valid native grader outcomes. Seed1731 completed98 verified engine requests and returned resolved=true; its trajectory includes thinking, body, bash/editor/submit and tool responses. Original indices1–12 have been submitted once, with two followups Running and the remaining followups queued. The complete original denominator remains2/80; updated remains0/80.

Bounded FrogNano/Qwen3.5 job `exp-1105-191135-503140` completed two normal updates on eight H800, with inspector/container/platform success, matching tokens/versions, 486 changed published tensors and measured trainer/decode absolute means 0.0069650090/0.0094554098. All eight independent prefill comparisons were measured. Thinking, body and tool signals were generated; no generated submit was observed in this bounded run. Its disposable outputs have been removed. Numerical equality is not established for either model pair, and H200 training remains unqualified.


Current save qualification `exp-1105-205143-864435` remains Starting without assigned nodes; both eight-GPU replicas retain the same approved shape. The zero-GPU decoder inspector `exp-1105-205240-904801` failed before reading training outputs: `find_spec` imported Bridge and Transformer Engine, which required an unavailable `libcuda.so.1`. The previously consumed source diagnostic was removed from that temporary inspector, with decoder validation unchanged and CPU imports verified. A corrected zero-GPU inspector is submitted; the unique twenty-update waiter and update20 evaluator waiter remain alive. No new twenty-update job has been submitted as of 21:15 HKT.


At 21:41 HKT, original BaseMind has three valid resolved outcomes out of eighty; updated remains zero. The native seed1730 record includes125 thinking turns,39 body turns and two submit calls. Full paired scores remain unavailable. Temporary final-score/cleanup continuation11266 is prepared and waiting; actual complete training/export/reload and both full cells are its prerequisites. All existing launchers are preserved.
