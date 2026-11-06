## Modification History

| Date | Change |
| --- | --- |
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

## Explicit requirements

| ID | Requirement |
| --- | --- |
| R1 | Create the task and documents before implementation or GPU execution; interview one decision at a time. |
| R2 | Validate all three full model pairs independently and advance their ready work concurrently on H800. Smaller model is student, larger model is frozen teacher. |
| R3 | Make student training/inference consistency diagnosis and root-cause repair the central objective. |
| R4 | Use route replay where semantically applicable, TIS, NCCL weight transfer, and global total-token loss normalization; verify consumers and runtime behavior rather than flag presence. The dense-student interpretation of route replay requires an explicit interview decision. |
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
- The request names Steptron, while the active workspace is Miles (`agent-opd`). The framework is the first interview decision. Do not silently switch frameworks or treat the previous canceled Steptron investigation as authority for a new port.
- Documentation and local read-only investigation are active. Implementation and GPU execution wait for shared understanding under the explicitly invoked grilling skill. No RJobs have been submitted by this task.
- Preserve unrelated `.serena/` and `task_memory/task_2026-11-06_qwen_model_inventory/` work. No README edit, publication, cloud copy, deletion or broad refactor is part of this documentation phase.
- Future runs follow the workspace GPU/storage rules: personal StepMind Python submission, H800/codesign, local source mounts, live quota check, and cloud reads/writes confined to `/mnt/codesign-exp/ycfeng`. The stated 128 GPUs are a ceiling to check, not observed free capacity. Auxiliary validators remain non-blocking for runs using 32 or more GPUs.

## Decisions to resolve in order

1. **Framework:** literal Steptron execution, or Miles execution with equivalent Steptron semantics. No answer recorded yet.
2. **Route replay:** whether all three dense-student routes should explicitly report R3 as not applicable, with separate teacher routing diagnosis if needed. No answer recorded yet.
3. **Learning workload:** dataset and split, fresh sampling versus any offline objective, text/vision scope, history/thinking policy, token lengths, optimizer-update budget and success criterion. Historical defaults are evidence only.
4. **Numerical acceptance:** frozen input population, same-version comparisons before TIS, exact formulas, aggregation, tail checks and predeclared thresholds. The handbook's 0.03 example is a discussion point, not an accepted threshold.
5. **Resources and assets:** accessible personal model copies, inference/training topology, concurrent GPU budget and timing. Exact unsupported requirements go back to the user.
6. **HF output:** export contents, save cadence, reload checks, retention and final evidence. HF weights are requested; resumable optimizer state is not.

The [design](design.md) owns inspected facts and proposed verification semantics. The [plan](plan.md) owns the dependency graph and completion conditions. No numerical or resource proposal is accepted merely by appearing in either file.
