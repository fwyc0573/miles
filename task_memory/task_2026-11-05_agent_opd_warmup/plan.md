## Modification History

| Date | Change |
| --- | --- |
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
