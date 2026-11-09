## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Close D34 original-source112K audit/parity and record isolated H800 initial synchronization; retain historical128K evidence and unchanged upstream/integration gates. |
| 2026-11-09 | Record the expanded upstream attempt failing before rollout at initial weight synchronization. |
| 2026-11-09 | Record D33 H800 preparation and D34 input/request budget implementation; reopen only the changed source length verification. |
| 2026-11-09 | Accept completed Ticket01 source audit/parity and refresh the remaining upstream-only integration gate. |
| 2026-11-09 | Archive the review repair milestone and ongoing, prerequisite-limited execution. |

# Review and input milestones — integration waits for upstream

The user selected `20d0b3f4` as the review base for `agent-opd-image`, initially at `0e94c522`. The draft's implementation phase, inherited contract, statistical interpretation, dependency checkpoints, and soft-gate behavior have been corrected. D33 subsequently authorizes H800/codesign without a task GPU-count cap; D34 sets112K inclusive prompts and16K completions within unchanged128K training/rollout context. Other scientific decisions and D1/D22 remain in force.

Main repair commit: `a0b0d113`. Both independent remediation reviews are complete. All original findings are closed; the final Standards P3 was resolved by retaining and verifying the unchanged document-check script. No review finding remains open.

## Deliverables

- Task contract and execution graph: `spec.md`, `requirements.md`, `plan.md`, and `tickets/01-*.md` through `tickets/06-*.md` in this directory.
- Review evidence: `review.md`, `checkpoint_2026-11-09_review.md`, and `test_report_2026-11-09_review_execution.md`.
- Input fixes: `tests/manual/agent_opd/swe_inputs.py` verifies cached native code identity; `audit_swe1003_sources.py` reports exact-prompt groups without inventing SWE task identities.
- Profile fixes: `tests/manual/agent_opd/distillation_profile.py` exposes historical conversation entries and baseline-relative values; both JSONL files are documented as necessary for rebuild.
- Reproducible checks: `tests/fast/test_swe_input_pins.py`, extended `tests/fast/test_distillation_profile.py`, and retained synthetic/mutation scripts under `tests/manual/agent_opd/`.
- CPU execution: `tests/manual/agent_opd/submit_swe1003_audit.py` and `source_audit_config.json`; inputs are read in place without copies.

## Observed validation

- Affected fast tests: 15 passed, including unknown native imports, changed pins, historical queries, baseline boundaries, and partial-write isolation.
- Synthetic audit and native parity worker commands: PASS. Updated same-prompt/different-instance fixture: PASS; task identity/counts remain unverified/null.
- Synthetic profile: 200 updates, 51,200 observations, 589 conversations; mean record cost 1.460 ms/update, all-conversation query 1.316 ms, profile memory 12.943 MiB.
- Document links, ticket DAG and arithmetic checks: 73 links, 22 anchors, zero errors using the retained `tests/manual/agent_opd/check_profile_docs.py`. See the test report for exact commands and environments.

## Execution and open work

| Ticket | Status at this milestone |
| --- | --- |
| 01 | Done: historical128K evidence retained; D34 budgets, boundaries, actual native request construction and completed original-source112K audit/parity accepted. |
| 02 | Blocked by D1/D22; no implementation or upstream merge begun. |
| 03 | Pure module fixes verified on CPU; native-count checks and integration blocked by02. |
| 04 | Blocked; no A/full formal run submitted. |
| 05 | Blocked; requires launch prerequisites and actual A first-update inspection. |
| 06 | Blocked by formal-run evidence. |

The historical2026-11-09T07:56Z refresh at upstream`c52991ac` recorded expanded attempt`exp-1109-144110-764758` failing at07:47:18Z after initial weight synchronization timed out at600s, before rollout collection or optimizer updates. It remains unaccepted, as do earlier227/256 acquisition and historical partial scoring. A later isolated H800 initial-sync milestone below does not establish representative256-turn capacity or upstream acceptance. The latest retained upstream checkpoint at11:19Z (`23b29f66`) had an approved original18-H200 retry but no new submission/acceptance and no recorded adoption of this parent's112K/16K. D1/D22 still block merge and training integration until the upstream owner records authoritative frozen-D11 acceptance; H800 D34 readiness is separate.

Historical128K CPU job`exp-1109-031258-820360` is retained in`evidence/source-audit-admission-20261109.json` and`evidence/source-audit-terminal-20261109.json`, with job/replica Succeeded, finish00:24:08Z and worker completion marker. Its real-source output/counts and512/2,048 raw-draw parity remain accepted under their original policy in`test_report_2026-11-09_source_audit.md`; no historical provenance is rewritten.

Current112K CPU job`exp-1109-154414-275606` completed under`438d25fc`; its personal creator`i-fengyicheng`,0GPU/8CPU,image,mount and131072/114688/16384 worker argv were verified. The primary's direct `get_rjob_client()` / API read at11:52:22.402210Z confirmed UID`6e08e161-435d-4195-bcd4-88d40d291eac`, job/audit replica Succeeded and finish11:47:11Z (`evidence/source-audit-112k-terminal-20261109.json`). All five business JSONs in`evidence/source-audit-112k-20261109/` were inspected; source SHA/bytes/counts/visual exclusions match128K, and512 native parity/2,048 interleaved raw draws pass. The local first terminal import of nonexistent `get_client` failed before any API request and was corrected from `stepmind.py:744`; it was not an audit failure or relaunch.

Current112K results:9,254 source/9,152 trainable conversations;868,775 pre-length eligible turns;102 visual conversations/10,008 eligible turns excluded;323,121 length rejections (37.1927%) across6,257 conversations. Eligible-turn median90 **before length filtering** retains D26's32×8; the length-accepted per-conversation median is absent/unverified and is not a new blocker. The32×8 CPU simulation accepts51,200 from84,229 draws, rejects33,029, covers869 conversations, has span median5/P90 7/max9 with0/869 spanning≥11 updates, and covers median23 conversations/update, not verified tasks. Simulated spans are not native runtime trend coverage.955 exact first-prompt groups remain proxies; native SWE identity and task counts stay UNVERIFIED/null. All first-source messages omit`preserve_thinking`; Qwen explicitly enables both thinking kwargs. No most-conversation-trend, benchmark, HF checkpoint or formal-training result is claimed. Historical128K27.51% rejection/span7/17-of745 results remain historical in the source report.

The new input/request contract also passes33 affected primary fast tests, pinned GLM512/2048 checks and synthetic SWE/audit workflow checks, including inclusive112K/+1 rejection with zero slot consumption and actual4,366-token prompt→16,384-token native request construction. Exact commands, environments, current acceptance and limits are in`test_report_2026-11-09_length_budgets.md`; this closes Ticket01 only.

H800 resource changes remain isolated in`agent-opd-h800-capacity`: explicit-null admission`1ae93261`, native length argv`8c9537bf`, four-node lifecycle`46e7b292`, and reviewed node-local NCCL correction`cf98293a`. Network-fixed native attempt`exp-1109-192340-580111` was submitted at11:23:40Z, with36 actual H800 GPUs confirmed and all8 rollout engines ready by11:36:41Z. Initial8-actor `update_weights` began11:37:18.596Z and ended11:37:22.414Z (`ok=true`,elapsed_s3.8); begin/end/tensor/distributed endpoints returned HTTP200. The11:37:27.670Z checksum event reports8 engine snapshots and weight_version0 only; checksum contents and later changed-weight consistency remain unverified. Decisive receipt:`/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity/task_memory/task_2026-11-09_profile_h800_preparation/evidence/h800-network-fixed-initial-sync-20261109.json`. This is a startup/initial-sync milestone underD34, not accepted native bank/optimizer/capacity, upstream frozenD11 or parent02/03/formal acceptance. Runtime memory/throughput and parent/isolated consolidation remain pending. Four-node affected tests pass122cases; broader related tests retain171PASS/12SKIP/one existing local SGLang parser failure, so that broader suite is not claimed all-pass.
