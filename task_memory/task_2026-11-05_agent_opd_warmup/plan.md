## Modification History

| Date | Change |
| --- | --- |
| 2026-11-05 | Create the agentic OPD preparation record. |

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
