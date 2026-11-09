## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Close the CPU/static NCCL repair and separate H800 D34 runtime readiness from upstream D11 acceptance. |
| 2026-11-09 | Add the native startup RCA and user-authorized session cloud cleanup. |
| 2026-11-09 | Plan isolated H800 resource preparation and verification. |
| 2026-11-09 | Add the independently owned native launcher length slice and CPU acceptance checks. |
| 2026-11-09 | Add native synchronization/source-consumer repairs and in-place receipt preparation to the H800 capacity prerequisite. |

# Plan

1. Extend the existing GPU admission policy to represent an explicit absent limit; keep fresh resource inspection and finite-policy semantics. Verify through existing budget tests.
2. In parallel, inspect H800 memory/topology support and prepare a concrete config using existing launch mechanisms. Keep the upstream256-turn acceptance gate and parent scientific parameters.
3. Validate the selected payload and worker commands on CPU, including D34 preservation through the real SweReplay generation caller into the request builder. A source-factory-only request check does not establish this later path. Record any remaining native validation needs before GPU execution.
4. Consolidate the completed resource change and records into the parent's final branch once its upstream gate permits integration.
5. Independently wire explicit launch prompt/response lengths to existing native flags, validating the three positive integer limits and prompt/response compatibility at the config boundary. Adapt only directly affected in-memory test fixtures, preserve archived configs and the historical 100-update Qwen35 workflow, verify native argv and a CPU-only dry-run, and commit the scoped code/tests/records.

Dependencies and ownership: `{1, 5}` are separate CPU code slices and can proceed alongside primary-owned `2`; `{2, 5, independent source preparation in7} -> 3`; `{1, 3, 5, parent upstream/merge gates} -> 4`. The capacity prerequisite does not depend on importing the parent's different profile-input API. Parent integration remains separate.

Acceptance: unlimited policies do not impose a manufactured count ceiling or force preemption; finite policies and their validators retain their existing results; H800 config uses codesign and accurately counts roles; the updated native argv has context/training/SGLang limits 131072, prompt limit 114688 and response limit 16384 with no context-sized response override; missing/invalid budgets fail at the config boundary; no unrelated source edits or GPU operations occur in delegated CPU work.

6. Repair mixed-engine lifecycle coverage, prove the CPU regression RED→GREEN, inspect the exact pinned receiver contract and review the fixed diff.
7. Apply D34 to the existing native capacity source without changing its sequential sampling. Prepare genuine native visual receipts against original posttrain paths; validate the ordinary source factory and candidate H800 payload before submission.
8. Submit the A/r256 H800 D34 capacity/readiness run through the existing personal Python backend; verify creator, local NFS source, actual workers/topology, weight publication, bank admission and two successful updates. Record native evidence before any parent merge; retain a failed/partial verdict if those conditions are not met. This H800 result does not accept upstream's unchanged D11 input-length contract.

Updated execution frontier: `{6, source part of7, native receipts in7}` run independently; `{1, 2, 3, 5, 6, 7} -> 8`; `{8 accepted, parent gate acceptance} -> 4`. Step8 is the upstream-native prerequisite, not parent Ticket02/03 implementation or a formal profile run.

9. Diagnose the first native startup exception from the terminal H800 attempt. Establish a production-path CPU discriminator, correct only the confirmed cause, and verify affected checks before any fresh native attempt. Preserve node-local platform network values; no timeout, retry, or transport workaround is authorized.
10. In parallel with9, inventory session-owned cloud smoke/temporary outputs, retain exact diagnostic evidence locally, and remove only obsolete terminal-job outputs authorized by the latest request. Verify backup content, deleted paths and logical byte counts. Preserve source assets, live/formal/evaluation artifacts and shared trash; report physical reclamation as unverified unless measured.

Current dependency: `8 failed -> {9, 10}`; `{9 verified, fresh admission} -> affected native verification -> 8 acceptance`; `{8 accepted, separately recorded upstream D1/D22 acceptance} -> 4`. Cleanup is independent of the code diagnosis and is not an acceptance gate. Collect node/runtime/environment evidence through existing receipts and event reporting; auxiliary inspection gaps stay non-blocking and are marked unverified.
