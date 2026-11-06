## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Confirm dense-student routing replay as not applicable while retaining the three-pair matrix and other required features. |
| 2026-11-06 | Confirm current Miles as the implementation framework; supersede the immediately corrected verl wording. |
| 2026-11-06 | Record the original request and open the documentation-first design interview. |

# Requirements

## Original request

[Original Request]

> $grill-with-docs 创建task，先落地docs。核心为验证以下comb：
> - Qwen3.5-4B + Qwen3.5-27B
> - Qwen3.5-4B + Qwen3.5-35B-A3B
> - Qwen3.5-27B + Qwen3.5-397B-A17B
>
> 具体要求：
> - 并行推进3个comb的steptron的测试验证，使用h800推进；上述模型已经在oss中（/data/ycfeng/stepfun-env-handbook/resource_analysis）
> - 较小的作为student，较大的作为teacher
> - 训推一致性的验证和检查和修复是核心重点(参考/data/ycfeng/stepfun-env-handbook/resource_analysis)
> - 开启参数（如果有一致语义功能，我 当前等描述使用的是steptron的开关）：r3（route replay）、tis打开、开启 nccl 直传（weight sync）、开启 enable total token loss
> - 验证训练的有效性：关注loss、norm grad的收敛情况，可否保存hf ckpt到codesign oss（无需保存模型和优化器的其他权重参数）
> - 如果出现了普遍性质的架构支持性缺失，先具体定位这些缺失模块和依据，交给我决策。

[Original Request] The supplied `grill-with-docs` skill invokes `grilling` and `domain-modeling`.

## Framework decision — confirmed

[Original Request] First reply, immediately corrected by the user:

> A；必须在当前verl实现当前task，而不是使用steptron中实现，注意区别

[Original Request] Authoritative correction:

> A；必须在当前miles实现当前task，而不是使用steptron中实现，注意区别

**Decision D1:** Implement, diagnose, repair and validate all three pairs in the current Miles repository. Steptron is a reference for requested feature semantics and acceptance evidence only. Do not implement this task in Steptron or verl, switch to either framework, or count their runtime results as Miles qualification. The corrected wording supersedes `verl` in the preceding message. This answers the framework question; the remaining interview decisions are still open.

## Routing-replay decision — confirmed

[Original Request] Reply to the proposal to record all three student R3 checks as not applicable and preserve the requested model matrix:

> 确认，继续

**Decision D2:** Keep pairs A, B and C unchanged. Record student routing replay as `N/A: dense student has no MoE routing decisions` for every pair; do not enable a replay flag that has no applicable student router. MoE teacher routing does not provide routes for the dense student's training pass. TIS, NCCL direct weight synchronization and total-token loss normalization remain required and must be verified. This decision does not qualify R3 on an MoE student or authorize adding one. Continue the documentation interview with the learning workload; runtime execution still depends on the remaining material decisions.

## Explicit requirements

| ID | Requirement |
| --- | --- |
| R1 | Create the task and documents before implementation or GPU execution; interview one decision at a time. |
| R2 | Validate all three full model pairs independently and advance their ready work concurrently on H800. Smaller model is student, larger model is frozen teacher. |
| R3 | Make student training/inference consistency diagnosis and root-cause repair the central objective. |
| R4 | Student route replay is not applicable to these three pairs under D2. Enable and verify TIS, NCCL weight transfer, and global total-token loss normalization; verify consumers and runtime behavior rather than flag presence. |
| R5 | Measure and plot training loss and gradient norm, assess learning behavior, and save a usable student HF checkpoint to personal codesign storage without additional native model or optimizer checkpoints. |
| R6 | Identify general architecture support gaps by exact module, symbol and evidence; return material architecture decisions to the user before implementing them. |

## Pair identity

| Pair | Student | Teacher |
| --- | --- | --- |
| A | Qwen3.5-4B | Qwen3.5-27B |
| B | Qwen3.5-4B | Qwen3.5-35B-A3B |
| C | Qwen3.5-27B | Qwen3.5-397B-A17B |

No Base, quantized, reduced-layer or different model substitution is approved. A and B have separate optimizer states and output paths despite sharing the initial student asset.

## Scope and authority

- This is a new task. Prior warmup choices such as 20 updates, the GLM5.2 dataset, four seeds, learning rate, cleanup, benchmark and GitHub push do not become decisions for this task.
- The current Miles workspace (`agent-opd`) is the confirmed implementation target under D1. The original request's Steptron wording supplies semantic references; the earlier canceled Steptron investigation and initial branch inspection supply no implementation authority for this task.
- Documentation and local read-only investigation are active. Implementation and GPU execution wait for shared understanding under the explicitly invoked grilling skill. No RJobs have been submitted by this task.
- Preserve unrelated `.serena/` and `task_memory/task_2026-11-06_qwen_model_inventory/` work. No README edit, publication, cloud copy, deletion or broad refactor is part of this documentation phase.
- Future runs follow the workspace GPU/storage rules: personal StepMind Python submission, H800/codesign, local source mounts, live quota check, and cloud reads/writes confined to `/mnt/codesign-exp/ycfeng`. The stated 128 GPUs are a ceiling to check, not observed free capacity. Auxiliary validators remain non-blocking for runs using 32 or more GPUs.

## Decisions to resolve in order

1. **Framework — resolved:** current Miles only, as recorded in D1 above.
2. **Route replay — resolved:** all three student paths report R3 as not applicable, per D2. Other required features remain enabled and subject to verification.
3. **Learning workload — next:** decide whether to use the existing original GLM-5.2 SWE histories for text-only, freshly sampled single-turn OPD in Miles. The [design proposal](design.md) is not yet accepted. Split/population, history/thinking policy, token lengths, update budget and learning criteria remain separate unresolved decisions; historical defaults are evidence only.
4. **Numerical acceptance:** frozen input population, same-version comparisons before TIS, exact formulas, aggregation, tail checks and predeclared thresholds. The handbook's 0.03 example is a discussion point, not an accepted threshold.
5. **Resources and assets:** accessible personal model copies, inference/training topology, concurrent GPU budget and timing. Exact unsupported requirements go back to the user.
6. **HF output:** export contents, save cadence, reload checks, retention and final evidence. HF weights are requested; resumable optimizer state is not.

The [design](design.md) owns inspected facts and proposed verification semantics. The [plan](plan.md) owns the dependency graph and completion conditions. No numerical or resource proposal is accepted merely by appearing in either file.
