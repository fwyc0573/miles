## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Archive02 trainer CPU-ready6129aefe,completed clean reviews,formal guard commit and staged03 delivery;retain pending primary integration/GPU acceptance and original concurrent B admission. |
| 2026-11-10 | Archive verified merge55fba827 and local prep-reference resolution; identify02 implementation as the frontier without accepting03 integration or formal profiles. |
| 2026-11-10 | Archive D35 parent-only H800 capacity adoption and merge authorization; retain independent upstream provenance and pending02/03/formal acceptance. |
| 2026-11-09 | Close D34 original-source112K audit/parity and record isolated H800 initial synchronization; retain historical128K evidence and unchanged upstream/integration gates. |
| 2026-11-09 | Record the expanded upstream attempt failing before rollout at initial weight synchronization. |
| 2026-11-09 | Record D33 H800 preparation and D34 input/request budget implementation; reopen only the changed source length verification. |
| 2026-11-09 | Accept completed Ticket01 source audit/parity and refresh the remaining upstream-only integration gate. |
| 2026-11-09 | Archive the review repair milestone and ongoing, prerequisite-limited execution. |

# Review, input, capacity and merge milestones — profile integration pending

The user selected `20d0b3f4` as the review base for `agent-opd-image`, initially at `0e94c522`. The draft contract and soft gates have been corrected. D33 authorizes H800/codesign without a task GPU-count cap;D34 retains128K context with112K inclusive prompts/16K completions. D35 adopts the accepted H800 capacity basis;merge`55fba827`consolidates archived candidate`0e6e8b1e`. The primary now accepts02 trainer CPU-ready`6129aefe`;03 integration is executing,not yet accepted.02 GPU and downstream S7 acceptance remain pending;other scientific/formal conditions are unchanged.

Historical draft repair commit:`a0b0d113`. Both remediation reviews completed and all original findings closed;the final Standards P3 was resolved by retaining and verifying the unchanged document-check script. T02 phase reviews of`4863e68e...6129aefe`are separately complete in`ba3cb696`,with Standards0/Spec0 actionable findings ([review](review.md));reviewers did not independently rerun tests and do not certify GPU/03 acceptance.

## Deliverables

- Task contract and execution graph: `spec.md`, `requirements.md`, `plan.md`, and `tickets/01-*.md` through `tickets/06-*.md` in this directory.
- Review evidence: `review.md`, `checkpoint_2026-11-09_review.md`, and `test_report_2026-11-09_review_execution.md`.
- Input fixes: `tests/manual/agent_opd/swe_inputs.py` verifies cached native code identity; `audit_swe1003_sources.py` reports exact-prompt groups without inventing SWE task identities.
- Profile fixes: `tests/manual/agent_opd/distillation_profile.py` exposes historical conversation entries and baseline-relative values; both JSONL files are documented as necessary for rebuild.
- Reproducible checks: `tests/fast/test_swe_input_pins.py`, extended `tests/fast/test_distillation_profile.py`, and retained synthetic/mutation scripts under `tests/manual/agent_opd/`.
- CPU execution: `tests/manual/agent_opd/submit_swe1003_audit.py` and `source_audit_config.json`; inputs are read in place without copies.
- D35 authorization, current gate and checkpoint: `requirements.md`, `spec.md` S0, `plan.md`, `progress.md`, `tickets/02-*.md` through `tickets/05-*.md`, and `test_report_2026-11-09_h800_preparation.md` D35 section. Scoped verification: `test_report_2026-11-10_d35_records.md`.
- Consolidated input and merge verification: `test_report_2026-11-10_input_merge.md` post-merge section; current four-section milestone checkpoint in`progress.md`. The previous D35/input slice reports retain their pre-merge snapshots; no separate merge/checkpoint report was added.
-02 CPU-ready commit`6129aefe`:native original-mask per-turn measurements and existing ACK transport;consumer contract,exact tests and limits in`test_report_2026-11-10_per_turn_sums.md`. Current03 owner:`profile-t03-integration-20261110`/`ses_e3ea12276ffeR5IWKB9CfabC5k`.
- Formal preparation`4863e68e`and correction`059a6a75`:existing`formal_config.json`/`test_report_2026-11-10_formal_configuration.md`. Both are committed;those artifacts and all proof reports remain outside this documentation commit.

## Observed validation

- Affected fast tests: 15 passed, including unknown native imports, changed pins, historical queries, baseline boundaries, and partial-write isolation.
- Synthetic audit and native parity worker commands: PASS. Updated same-prompt/different-instance fixture: PASS; task identity/counts remain unverified/null.
- Synthetic profile: 200 updates, 51,200 observations, 589 conversations; mean record cost 1.460 ms/update, all-conversation query 1.316 ms, profile memory 12.943 MiB.
- Document links, ticket DAG and arithmetic checks: 73 links, 22 anchors, zero errors using the retained `tests/manual/agent_opd/check_profile_docs.py`. See the test report for exact commands and environments.
- Historical pre-merge D35 document check:26 documents,6 tickets,88 links,34 anchors,zero errors;candidate ancestry and`git diff --check`PASS under systemPython3.10.6. Commands and the then-pending reference resolution are retained in`test_report_2026-11-10_d35_records.md`; no runtime check was rerun by that delegation.
- Post-merge verification: two input conflict files retain first-parent bytes;139 related CPU tests and seven genuine native synthetic checks PASS in the input report. All seven unique prep references resolve;retained H800 checker,docchecker(27 documents/87 links/33 anchors/zero errors)and scoped merge code/task whitespace checks PASS. Whole merge whitespace is not clean:17 inherited upstream XML/diff artifact paths exactly match incoming`0e6e8b1e`blobs; no historical evidence was rewritten. Commands and limits are owned by`test_report_2026-11-10_input_merge.md`post-merge section.
-02 recorded evidence:110 combined PASS;79 affected PASS after final nullable-metadata preservation;8-process CPU/Gloo2CP×2TP×2PP and genuine AdamW updates under auxiliary errors. These are the report's accepted CPU results,not reruns by this delegation. Native Megatron/NCCL overhead and A actual bank/profile remain unverified.

## Execution and open work

| Ticket | Status at this milestone |
| --- | --- |
| 01 | Done: historical128K evidence retained; D34 budgets, boundaries, actual native request construction and completed original-source112K audit/parity accepted. |
| 02 | Trainer CPU-ready6129aefe accepted;downstream S7 and A-update GPU acceptance pending,not full ticket done. |
| 03 | Pure module CPU accepted;02 dependency satisfied;201-PASS CPU-ready delivery staged,primary acceptance/commit pending. |
| 04 | Blocked; no A/full formal run submitted. |
| 05 | Blocked; requires launch prerequisites and actual A first-update inspection. |
| 06 | Blocked by formal-run evidence. |

The historical2026-11-09T07:56Z refresh at upstream`c52991ac` recorded expanded attempt`exp-1109-144110-764758` failing at07:47:18Z after initial weight synchronization timed out at600s, before rollout collection or optimizer updates. It remains unaccepted, as do earlier227/256 acquisition and historical partial scoring. The retained11:19Z upstream checkpoint (`23b29f66`) had an approved original18-H200 retry but no new submission/acceptance and no recorded adoption of this parent's112K/16K. Those are historical upstream facts, not current parent blockers underD35. The later parent authorization does not rewrite frozen-D11 provenance or certify upstream Ticket02.

Historical128K CPU job`exp-1109-031258-820360` is retained in`evidence/source-audit-admission-20261109.json` and`evidence/source-audit-terminal-20261109.json`, with job/replica Succeeded, finish00:24:08Z and worker completion marker. Its real-source output/counts and512/2,048 raw-draw parity remain accepted under their original policy in`test_report_2026-11-09_source_audit.md`; no historical provenance is rewritten.

Current112K CPU job`exp-1109-154414-275606` completed under`438d25fc`; its personal creator`i-fengyicheng`,0GPU/8CPU,image,mount and131072/114688/16384 worker argv were verified. The primary's direct `get_rjob_client()` / API read at11:52:22.402210Z confirmed UID`6e08e161-435d-4195-bcd4-88d40d291eac`, job/audit replica Succeeded and finish11:47:11Z (`evidence/source-audit-112k-terminal-20261109.json`). All five business JSONs in`evidence/source-audit-112k-20261109/` were inspected; source SHA/bytes/counts/visual exclusions match128K, and512 native parity/2,048 interleaved raw draws pass. The local first terminal import of nonexistent `get_client` failed before any API request and was corrected from `stepmind.py:744`; it was not an audit failure or relaunch.

Current112K results:9,254 source/9,152 trainable conversations;868,775 pre-length eligible turns;102 visual conversations/10,008 eligible turns excluded;323,121 length rejections (37.1927%) across6,257 conversations. Eligible-turn median90 **before length filtering** retains D26's32×8; the length-accepted per-conversation median is absent/unverified and is not a new blocker. The32×8 CPU simulation accepts51,200 from84,229 draws, rejects33,029, covers869 conversations, has span median5/P90 7/max9 with0/869 spanning≥11 updates, and covers median23 conversations/update, not verified tasks. Simulated spans are not native runtime trend coverage.955 exact first-prompt groups remain proxies; native SWE identity and task counts stay UNVERIFIED/null. All first-source messages omit`preserve_thinking`; Qwen explicitly enables both thinking kwargs. No most-conversation-trend, benchmark, HF checkpoint or formal-training result is claimed. Historical128K27.51% rejection/span7/17-of745 results remain historical in the source report.

The new input/request contract also passes33 affected primary fast tests, pinned GLM512/2048 checks and synthetic SWE/audit workflow checks, including inclusive112K/+1 rejection with zero slot consumption and actual4,366-token prompt→16,384-token native request construction. Exact commands, environments, current acceptance and limits are in`test_report_2026-11-09_length_budgets.md`; this closes Ticket01 only.

Historical H800 initial-sync milestone: isolated changes include explicit-null admission`1ae93261`, native length argv`8c9537bf`, four-node lifecycle`46e7b292`, and reviewed node-local NCCL correction`cf98293a`. Network-fixed attempt`exp-1109-192340-580111` was submitted at11:23:40Z, with36 actual H800 GPUs confirmed and all8 engines ready by11:36:41Z. Initial synchronization completed in3.8s at11:37:22.414Z; its11:39Z readback did not yet verify bank/optimizer/capacity or updated checksum contents. The original initial-sync receipt and its scope remain retained. Four-node affected tests pass122cases; broader related tests retain171PASS/12SKIP/one existing local SGLang parser failure, so that broader suite is not claimed all-pass.

Current terminal H800 capacity is accepted underD35:256/256 valid samples in1633.2862s, two successful unskipped optimizer ACKs on bank0 visits1/2, and ranks0–7 each completing2×88 student scoring microbatches with second scoring afterACK1. The job and all five replicas Succeeded;1644 text hashes match across eight engines atversions0/1, including the same972 changed hashes. The full128K logits storage is15.15625GiB/rank and observed scoring PyTorch allocation peaks at28.89246GiB, not whole-device/backward usage. Whole-model checksum equality and final engine NIC/HCA values remain unverified. Canonical record: `../task_2026-11-09_profile_h800_preparation/evidence/h800-network-fixed-capacity-acceptance-20261109.json`; exact commands and limits: `../task_2026-11-09_profile_h800_preparation/test_report_2026-11-09_network_fixed_prelaunch.md`. These repo-local paths now resolve after merge55fba827; the historical pre-merge references retain their original scope.

Next:primary acceptance/commit of the staged[03 CPU-ready delivery](test_report_2026-11-10_profile_integration.md),then final profile configuration/launch checks. T02 reviews and formal correction have completed independently. The prior spec merge-pending status is resolved;`requirements.md:59`still names02 frontier and remains a primary-owned status update. No formal A/B run or02 GPU acceptance is recorded. D16 uses A's first actual formal successful ACK/profile inspection,without another GPU smoke.

The primary's real`training_protocol`RED1/GREEN50 verifies working`bank_uses=50`;`ReplaySchedule(full)`still performs200 distinct banks with one visit each. B's four-H800 TP4/EP1 teacher is feasible by completed read-only mapping,not native load/memory/throughput accepted. Under unchangedS8,B may run concurrently with continuing A after A's firstactual ACK/inspection and fresh resource admission;neither A200-update completion nor another user approval is required. Upstream acceptance remains independent. Formal cells still require their own200 native updates and separate complete paired-profile acceptance.
