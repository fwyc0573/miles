## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Reference the latest preserve-all default while keeping completion-only targets and the chosen colocated layout. |
| 2026-11-06 | Record the user's temporary colocation choice, native CUDA IPC transport and deferred NCCL qualification; retain the original research recommendation as historical evidence. |
| 2026-11-06 | Compare deployment options against current Miles source, official documentation and upstream issue evidence; recommend a separated NCCL baseline with external teachers. |

# Deployment research for the three Qwen3.5 pairs

## Scope and source identity

Research date: **2026-11-06**. This report supports decision D5 in [requirements.md](requirements.md). It is a deployment recommendation, not a GPU qualification result. No jobs were submitted, no cloud artifacts were written, and no current CI success receipts were collected.

- Inspected local Miles HEAD: `9df78a8742e8f8a4a51dfeccddbf42127d419a4d`; origin is the personal fork `fwyc0573/miles`. Current local implementation, including its task-specific additions, is the execution authority.
- Official upstream is `radixark/miles`. Its GitHub API returned main HEAD [`b133ce9cac3c8b4d9969d20d6a03117d545c2865`](https://github.com/radixark/miles/commit/b133ce9cac3c8b4d9969d20d6a03117d545c2865) during this research. This is a reference identity, not a source upgrade or an assertion that every upstream file matches the local checkout.
- Official documentation and first-party issue links below were read on 2026-11-06. The selected worker image, SGLang/Megatron versions, actual model copies, H800 memory capacity and TP configurations remain unverified.

## Current decision: temporary student colocation

The user explicitly selected **colocated student Megatron training and student SGLang rollout** after this research. The two student roles share GPUs through the existing offload/wake-up lifecycle. Each pair retains its external frozen SGLang teacher on an independent allocation; A and B retain separate evolving student states. Begin with synchronous scheduling for the consistency investigation. Exact GPU counts and parallelism remain unverified.

Current Miles selects CUDA IPC for colocated weight updates, even if `broadcast` is supplied. Validate that native path and label it accurately. Original NCCL-direct qualification is **deferred during temporary colocation**, not passed or permanently waived. No change to the core dispatcher is proposed. This user decision supersedes the separated recommendation below; it does not negate the source findings.

## Original research recommendation — superseded by the user

The original recommendation was **Megatron student training on GPUs separate from the student SGLang rollout engines, with explicit NCCL broadcast weight transfer and a separate frozen SGLang teacher**. It addressed the original transport requirement. Synchrony was selected for diagnosing consistency; it is not evidence that asynchronous execution is generally less mature. The role identities below remain valid, but student placement now follows the current decision above.

| Pair | Student training role | Student rollout role | Frozen teacher role |
| --- | --- | --- | --- |
| A | Independent Qwen3.5-4B Megatron state | Qwen3.5-4B SGLang engines receiving A's weights | External Qwen3.5-27B SGLang scorer |
| B | Independent Qwen3.5-4B Megatron state | Qwen3.5-4B SGLang engines receiving B's weights | External Qwen3.5-35B-A3B SGLang scorer |
| C | Independent Qwen3.5-27B Megatron state | Qwen3.5-27B SGLang engines receiving C's weights | External full Qwen3.5-397B-A17B SGLang scorer |

Under the original separated proposal the three roles had distinct GPU allocations. Under the current choice, student trainer and rollout share GPUs, and the teacher stays frozen outside the student's weight-update group. A and B share an initial model identity, not an optimizer or evolving rollout engine. Exact GPU counts, teacher TP/EP and student TP/CP remain capacity decisions after complete-prefix lengths and runtime versions are fixed. The 397B teacher must retain the full requested model; its activated-parameter count is not its resident weight size.

This choice follows the task's transport constraint and available implementation, rather than a claim that one layout is universally more mature. Both colocated and separated layouts have maintained code, official documentation and registered tests. Official guidance recommends Megatron for model parallelism; FSDP is useful when the HF implementation itself is wanted and data parallelism suffices. FSDP is therefore a possible numerical reference, not the first execution choice for these long-prefix experiments. [Official backend guidance](https://miles.radixark.com/docs/user-guide/training-backend)

## Deployment and implementation evidence

| Option or capability | Evidence in the current checkout | Consequence for this task |
| --- | --- | --- |
| Separated trainer and rollout | [Protocol dispatch](../../miles/backends/training_utils/weight_update/protocol.py) selects `UpdateWeightFromDistributed` for non-colocated `broadcast`; [group setup](../../miles/backends/training_utils/weight_update/protocols/broadcast.py) explicitly selects `backend="nccl"` for both sides. | Omit `--colocate` and explicitly select `--update-weight-transfer-mode broadcast`. Validate actual transport and publication receipts in the worker. |
| Colocated trainer and rollout | The same dispatcher returns `UpdateWeightFromTensor` when `args.colocate` is true, before choosing broadcast; [CUDA IPC implementation](../../miles/backends/training_utils/weight_update/protocols/cuda_ipc.py) owns that path. | Current user-selected option. `--colocate --update-weight-transfer-mode broadcast` still selects IPC. Qualify IPC and explicitly defer NCCL-direct acceptance. |
| Layout and scheduling | Official docs describe colocated memory handoff and separated resident allocations. A synchronous separated loop may leave one GPU group idle during the other phase. | Current colocation must verify actual memory handoff, wake-up and consumed weights. Layout alone does not select asynchronous scheduling. [GPU layout documentation](https://miles.radixark.com/docs/user-guide/training-backend) |
| Other transfer modes | Current dispatch also has `broadcast_packed`, `p2p` and `disk-delta`. The P2P design uses Mooncake/NIXL rather than the baseline broadcast path. | These are not needed for this decision; do not silently replace required NCCL with P2P or disk publication. [Local P2P documentation](../../docs/advanced/p2p-weight-transfer.md) |
| External teacher | [OPD reward implementation](../../miles/rollout/on_policy_distillation.py) sends `sample.tokens` as input IDs to the scoring endpoint. Official documentation selects external SGLang for a different or too-large teacher. | Existing fit for all three pairs. Verify the exact assets share token-ID semantics and that each sample reaches its assigned frozen teacher. [Official OPD guide](https://miles.radixark.com/docs/advanced/on-policy-distillation) |
| In-process Megatron teacher | [`load_other_checkpoint()`](../../miles/backends/megatron_utils/actor.py) loads teacher weights into `self.model` and backs them up under a tag; teacher scoring switches that same model slot. | Different sizes or dense/MoE architectures cannot be supported merely by changing `--opd-teacher-load`. Same Qwen family is insufficient. Supporting heterogeneous in-process teachers would require additional implementation; the external teacher avoids that change. |
| HF-only output | [`MegatronTrainRayActor.save_model()`](../../miles/backends/megatron_utils/actor.py) calls the native checkpoint writer only when `args.backend.save` is set. With `save_hf` and no native save path it calls `export_hf()` directly. | An existing HF-only route is available. Actual Qwen export completeness and reload still need validation; source presence is not a usable checkpoint receipt. |

The user separately settled input and loss semantics under the latest D4/D6: preserve all historical reasoning by default across real-user boundaries, prefix target mask zero, completion-only target loss with TIS. Existing template settings retain user control. Deployment must preserve the same prefix/completion IDs across consumers and verify TIS and global token normalization; no historical SFT/KD mixture is required.

## What the registered tests establish

These are inspected test definitions, **not observed passing jobs**. Their H200 suite names do not establish H800 acceptance, even where registration includes the broader Hopper hardware family.

| Inspected evidence | What it exercises | What it does not establish |
| --- | --- | --- |
| [Qwen3-30B-A3B separated broadcast test](../../tests/e2e/megatron/test_qwen3_30B_A3B/test_disagg_broadcast.py) | Separated Megatron/SGLang, broadcast, and registered gradient-norm and train/rollout logprob metrics; H200 CUDA suite. | Qwen3.5 dense behavior, external teacher integration, full historical contexts, or any requested pair. |
| [Qwen3.5-35B-A3B separated asynchronous test](../../tests/e2e/megatron/test_qwen3_5_35B_A3B/test_nospec_r3_bf16_sgl_dpattn1x4_meg_tp1cp1_fullyasync.py) | Full 35B-A3B with separated broadcast, R3, BF16 and registered consistency metrics; H200 suite. | H800 qualification, dense-student OPD or the 397B teacher. It excludes visual weights from equality checking because its training path lacks vision training. |
| [External SGLang OPD test](../../tests/e2e/short/test_qwen2.5_0.5B_opd_sglang.py) | An independently launched teacher plus a colocated student, two rollouts, top-k OPD, and a pinned legacy rollout environment switch. | The combined separated-NCCL/full-Qwen3.5 path. This small self-distillation test is useful interface evidence only. |
| [Qwen3.5 model recipe](https://miles.radixark.com/docs/models/qwen/qwen3-5) | Official dense 4B and 27B recipes, with model configuration and TP settings. | Capacity at this task's complete historical lengths, required teacher memory, or native H800 results. |

A targeted search of `tests/e2e` did not find a test covering any complete requested pair with all required features. That is a coverage gap to fill with task execution, not proof that the architecture is unsupported.

## Version-specific community evidence

- The official dense recipe restricts rollout TP to one because SGLang 0.5.9 produced incorrect Qwen3.5 output with TP greater than one. [SGLang issue 21039](https://github.com/sgl-project/sglang/issues/21039), opened 2026-03-20 and closed 2026-03-29, records a 4B TP discrepancy; a maintainer suggested [PR 20956](https://github.com/sgl-project/sglang/pull/20956), merged 2026-03-20. This is version-scoped evidence, not a permanent TP limit or a guarantee that an arbitrary newer image is correct. [Official recipe caveat](https://miles.radixark.com/docs/models/qwen/qwen3-5)
- [SGLang issue 20550](https://github.com/sgl-project/sglang/issues/20550), opened 2026-03-13, records 27B empty or malformed outputs and later reports from several GPU environments, including H800. Its 2026-07-07 closure followed inactivity automation. A closed issue does not provide a verified fix for the selected image.
- [SGLang issue 34239](https://github.com/sgl-project/sglang/issues/34239), opened 2026-08-10, reports a 397B-A17B-FP8 problem on H800 with speculative decoding near a 262,144-token boundary. Those conditions differ from the requested full model and plain teacher scoring. It is a reason to qualify the exact context/kernel configuration, not evidence that the requested teacher is generally unsupported.

Community evidence therefore strengthens the requirement for exact native validation; it does not justify substituting another model, quantization, hardware, or framework. No recommendation here depends on issue counts or on a default setting alone.

## Required native checks before qualification

1. Record the selected image and Miles/Megatron/SGLang/CUDA versions, actual H800 devices, full model identities and tokenizer compatibility. Confirm that the exact source-mounted implementation is used. Select TP/CP and teacher capacity from measured complete-prefix lengths and worker memory, not recipe GPU counts.
2. Run the same token IDs through student generation, teacher scoring and student training with preserve_thinking=True selected through the existing template parameter. Verify retained reasoning across real-user boundaries, zero prefix target loss and completion-only targets, including generated reasoning. Check ordinary and long prefixes, packed boundaries and the chosen CP/TP configuration. Inspect output contents and numerical differences; HTTP success alone is insufficient.
3. Record initial and post-update weight versions, actual CUDA IPC publication and engine-consumption evidence, train/rollout weight equality where applicable, and same-version logprob comparisons. Keep each teacher's identity and weights fixed. Validate TIS behavior and global token normalization in the actual loss path. Record original NCCL qualification as deferred during this phase.
4. Execute real optimizer updates separately for A/B/C, inspect loss and gradient-norm curves, then export only the requested HF artifact under `/mnt/codesign-exp/ycfeng`. Reload that artifact and compare its behavior; verify that no native model or optimizer checkpoint was also produced. Check required untouched companion weights when the source HF model contains a vision component.
5. Release independent pair work concurrently after its own prerequisites pass and live quota is verified. A capacity or model issue in C should not serialize ready work in A/B. Keep auxiliary validators non-blocking for runs using at least 32 GPUs, as required by repository policy.

**Research outcome:** source findings are complete and the user has selected temporary student colocation with an external teacher. History and loss semantics are resolved by D4/D6. H800 image viability, exact TP/CP capacity, complete-pair numerical consistency, learning behavior and HF reload acceptance remain unverified; original NCCL-direct qualification is deferred.
