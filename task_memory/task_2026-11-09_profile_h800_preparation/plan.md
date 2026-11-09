## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Plan isolated H800 resource preparation and verification. |
| 2026-11-09 | Add the independently owned native launcher length slice and CPU acceptance checks. |

# Plan

1. Extend the existing GPU admission policy to represent an explicit absent limit; keep fresh resource inspection and finite-policy semantics. Verify through existing budget tests.
2. In parallel, inspect H800 memory/topology support and prepare a concrete config using existing launch mechanisms. Keep the upstream256-turn acceptance gate and parent scientific parameters.
3. Validate the selected payload and worker commands on CPU. Record any remaining native validation needs before GPU execution.
4. Consolidate the completed resource change and records into the parent's final branch once its upstream gate permits integration.
5. Independently wire explicit launch prompt/response lengths to existing native flags, validating the three positive integer limits and prompt/response compatibility at the config boundary. Adapt only directly affected in-memory test fixtures, preserve archived configs and the historical 100-update Qwen35 workflow, verify native argv and a CPU-only dry-run, and commit the scoped code/tests/records.

Dependencies and ownership: `{1, 5}` are separate CPU code slices and can proceed alongside primary-owned `2`; `{2, 5, parent input/checker/audit changes} -> 3`; `{1, 3, 5, parent upstream/merge gates} -> 4`. The delegated launcher slice does not implement parent integration.

Acceptance: unlimited policies do not impose a manufactured count ceiling or force preemption; finite policies and their validators retain their existing results; H800 config uses codesign and accurately counts roles; the updated native argv has context/training/SGLang limits 131072, prompt limit 114688 and response limit 16384 with no context-sized response override; missing/invalid budgets fail at the config boundary; no unrelated source edits or GPU operations occur in delegated CPU work.
