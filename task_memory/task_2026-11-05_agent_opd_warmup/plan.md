## Modification History

| Date | Change |
| --- | --- |
| 2026-11-05 | Record twenty verified updates, incomplete checkpoint save, save diagnostics and question-sharded evaluation. |
| 2026-11-05 | Create the agentic OPD preparation record. |
| 2026-11-05 | Record two verified H800 optimizer updates, numeric alignment and complete artifact cleanup. |

# Plan

1. Establish branch, repository contracts, ticket07 settings, and acceptance checks.
2. Query company model records through Lark; verify FrogNano/Qwen3.5-4B assets or download missing pinned weights to personal codesign storage.
3. Reuse Miles GLM/OPD/R3/TITO mechanisms to prepare glm5.2 input and a reproducible 16-H200 warmup. Preserve raw tokens, reasoning, body text, tool calls, and turn/source identity.
4. Run CPU checks and the actual H200 workflow; measure teacher scoring, finite optimizer updates, token alignment, routes, train/rollout logprobs, and updated-weight synchronization. Diagnose in-scope failures.
5. Retain code and Markdown verification conclusions only; stop task jobs, promptly remove all task-owned logs, compilation caches, smoke data and disposable outputs, commit and push `agent-opd` to the personal repository.

Dependencies: 1 -> {2, 3}; 3 -> 4; {2, 4} -> 5. Model download (2) progresses independently of GLM implementation and verification (3/4).

The dependency on step4 applies to final cleanup, the completed validation archive and final synchronization. While the exact GPU job is externally queued, completed preparation commits and their explicitly incomplete verification status can be synchronized incrementally; this does not mark step4 or step5 complete.

## Acceptance

- Branch and final remote SHA match; working tree changes are accounted for.
- Company search evidence and model inventory distinguish known availability from negative search results; missing requested models have complete indexed files at recorded cloud paths.
- GLM warmup consumes actual glm5.2 turns, preserves each requested signal and unmodified source identity, and produces at least two successful OPD optimizer updates with a teacher distinct from the student.
- Compare inference and training logprobs on the same token IDs and weights; report numeric differences and routing evidence, and do not equate a successful process with numeric agreement.
- Verify worker GPU type/count, creator, local source mounts, source revision, environment versions, terminal status and weight update behavior.
- Cleanup removes only task-created disposable data/checkpoints after evidence is retained; shared models/dataset and other jobs remain available.
- Run existing checks applicable to changed components. Keep exact commands and observed results in the Markdown test report; retain no raw warmup data or logs.

## Temporary hardware steering

The user requested H800 on November5. Step4 now executes the identical16-GPU
warmup on H800/codesign, with an explicit worker GPU-type check. This establishes
workflow and H800 numerical evidence; the original H200 training qualification
remains open. The queued H200 replacement is stopped through the mandated script.
Do not expand the training size, change model/data inputs or retain warmup data.

## Verified execution status (November 5, 2026)

1. Branch, repository contracts and acceptance: completed.
2. Company search and pinned FrogNano/Qwen3.5-4B downloads: completed,22files fullyverified.
3. Actual glm5.2 turns and the native GLM OPD recipe: completed.
4. Current temporary16H800/codesign warmup: completed. Two normal finite optimizer updates, nonzero gradients, exact token/R3 alignment, matching weightversions0/1,1368changedpublished tensors and measuredlogprob/TIS. Inspector exit0; bothcontainers andplatformSucceeded. H200training qualification remains outside theseH800observations.
5. Final disposable artifact cleanup and branch synchronization: completed. Archive commit `e975d4070989f869a53807c618b32c6fd58a2973` matched the personal remote branch. Only code and Markdown remain; final source code equals the qualified0e78c5e5 revision. The final status commit records completion and is synchronized separately.


## Twenty-update learning test (new acceptance phase)

1. Freeze 20 questions from Ticket06 fixed50 (2 astropy,18 django; seed1234) and 80 distinct eligible Ticket07 glm5.2 turns (20/category); verify source boundaries and inherited fixed175 exclusions.
2. Configure 20 real updates, native final HF export and unambiguous rollout19 -> completed-update20 identity. Preserve qualified R3/TIS/precision/topology; sample up to4096 tokens within65536 context.
3. Prepare the existing native SWE evaluator for GLM/SGLang and identical model0/model20 sampling, tool execution, grading and complete80-attempt denominators. CPU-check supported imports and exact configuration.
4. Submit the 16H800 learning test locally through personal Python RJobBackend; verify every normal finite update, version/R3/token alignment and actual final export. Run both80-attempt benchmark cells and report paired scores plus per-question bootstrap interval. Lack of improvement is reported honestly.
5. Delete all task temporary local/cloud outputs, verify absence and no task GPU allocation, retain concise conclusions, commit and push branch with remote SHA check.

Dependencies: 1 -> 2; {1,3} -> benchmark; {2,3} -> 4; 4 -> 5. Native evaluator preparation(3) can progress while the learning workload(4) runs. Every consumed output may be removed before final cleanup. Acceptance requires actual20 updates and actual80 valid outcomes per model, separately from platform success.

Current phase status:1 input freeze completed;2 configuration completed with actual export pending;3 native adapter preparation completed with four valid first-question outcomes; complete benchmark pending;4 twenty optimizer updates verified but final save failed; save diagnostic failed with a native Ray memory-pressure kill and initial benchmark in progress;5 final cleanup/push pending. Initial benchmark runs independently of the final training export. The prior two-update phase remains completed and does not satisfy this phase.
