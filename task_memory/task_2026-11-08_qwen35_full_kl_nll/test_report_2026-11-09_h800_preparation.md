## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Record D35 adoption of the accepted terminal H800 capacity result; preserve all dated historical readbacks and parent-owned prior initial-sync progress. |
| 2026-11-09 | Record eight native engines ready and successful 3.8-second initial synchronization; leave bank/training acceptance pending. |
| 2026-11-09 | Record first H800 terminal failure/cleanup, reviewed node-network correction and submitted network-fixed H800 retry; distinguish upstream D11 acceptance. |
| 2026-11-09 | Record actual36-H800 submission, Starting state and initial worker GPU identities. |
| 2026-11-09 | Record the reviewed session repair, pinned receiver evidence, native in-place receipts and source parity launch status. |
| 2026-11-09 | Record exact upstream terminal/timeout evidence and failed audit-query coverage; synchronization diagnosis is pending. |
| 2026-11-09 | Record D33 documentation checks, live resource inspection and isolated admission preparation. |

# H800 execution preparation

## Authorization and current gate

D33 authorizes H800/codesign execution with no task GPU-count cap. Parent Ticket01 is accepted. D35 now adopts the accepted H800 capacity basis and authorizes candidate consolidation followed by Ticket02/03 integration; neither consolidation nor integration has occurred. The upstream task remains independent. The checks and readbacks below retain their2026-11-09 scope and original verdicts; current adoption is recorded in[the D35 section](#d35-parent-adoption-2026-11-10).

## Observed checks

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Document links and dependency graph afterD33 | Existing six tickets remain coherent |21 documents,6 tickets,75 links,22 anchors; zero errors | PASS |
| Whitespace | No diff errors | `git diff --check` exits0 | PASS |
| Fresh personal H800 commitments | Query actual nonterminal non-preemptible jobs using Python API | At07:13:27Z:24 GPUs across three other jobs | RECORDED |
| Upstream native gate | Actual capacity evidence, not submission/startup alone | `exp-1109-144110-764758`: Failed at07:47:18Z; initial weight synchronization timed out after600s, before rollout collection | FAILED / GATE NOT MET |
| Unlimited allocation | No manufactured numeric ceiling | Candidate`gpu_policy.json` has explicitnull; isolated`1ae93261` passes25 budget+4 consumer checks | CPU PASS |
| H800 payload/runtime | Configuration validated, then actual H800 runtime evidence | First`exp-1109-181120-274261` Failed10:29:35Z; correctednetworkretry`exp-1109-192340-580111` submitted11:23:40Z andStarting; businessgatepending | IN PROGRESS |

Commands:

```bash
python3 tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll
git diff --check
```

Resource queries used `/data/ycfeng/tmp/stepmind-env/bin/python` (Python3.10.6), with the authoritative runbook's personal authentication/proxy initialization, `STEPMIND_BACKEND=rjob`, `PYTHONNOUSERSITE=1` and `PYTHONDONTWRITEBYTECODE=1`. The paginated native `list_namespaced_custom_object` query used creator label`kubebrain.brainpp.cn/creator=i-fengyicheng`, page limit100 and20-second request timeout, feeding the existing `rjob_budget.committed_jobs` forH800 andH200. Exact-job queries then used `get_namespaced_custom_object`, `get_rjob_infos` and bounded replica logs. Filtered artifacts:

- `evidence/h800-resource-readback-20261109.json`
- `evidence/upstream-h200-startup-readback-20261109.json`

Importing Steptron before Miles initially raised`ModuleNotFoundError: No module named 'tests.manual'`. A focused import probe showed Steptron's initialization prepends`third_party/super_agent/tests` ahead of Miles. Importing the Miles budget reader before Steptron, matching the existing submitter's ordering, fixed the local readback. No dependency installation or worker retry occurred.

## Isolated code preparation

Worktree:`/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`, branch`agent-opd-h800-capacity`, base`c52991ac`. Local preparation record:`task_memory/task_2026-11-09_profile_h800_preparation/`. This isolates resource changes from the live upstream job and does not merge upstream into the parent branch. The completed code and records must be consolidated into the final parent branch after its gate permits integration.

No GPU capacity or formal-run acceptance is claimed by these CPU/read-only checks. A personal commitment count is not an estimate of free cluster capacity; the platform remains the scheduling authority.

## H800 sizing decision

Prepare36 H800 GPUs per pair: four student/rollout nodes of8, with the first8 also running trainerTP4/DP2/CP1;32 rollout GPUs host8 TP4 engines, two colocated and six dedicated. Teacher uses4 GPUs/TP4. Existing memory fraction0.7, max-running1,128K total context and131072 dynamic-batch token target remain unchanged. D34 separately sets112K prompt/16K completion. Native rollout layout is declared by`h800_sglang.yaml`.

Evidence: a131072-token scoring tensor at vocab248320 has bf16 logits of30.3125GiB per TP2 rank and15.15625GiB per TP4 rank; the former matches the measured H200 allocation request32,547,799,040bytes. These are individual tensor sizes, not measured H800 peak memory. `max_tokens_per_gpu` is a packing target: `seqlen_balancing.first_fit_decreasing_pack` leaves an oversized sample whole, so reducing that target cannot bound a single128K sample. The prior exploration's32768-token workaround and0.6 memory fraction were withdrawn as unsupported. No guessed throughput multiplier is used as acceptance evidence.

The existing entrypoint's two-student-node restriction blocks this layout despite native engine-group support. `profile-h800-four-node-20261109` owns the isolated lifecycle extension and CPU checks. Native36-GPU memory, mixed weight sync and throughput remain unverified. The existing scoring-lifetime observer isolates all installation and per-forward errors through its `soft` method; it is not an auxiliary hard gate for a≥32-GPU run.

The restriction has now been removed by`46e7b292` in the isolated worktree. The four-node lifecycle keeps one trainer head and supervises ranks1–3;122 affected tests PASS. The broader related run records171PASS,12SKIP and one existing local parser failure for`--sglang-enable-prefill-weight-versions`. That broader run is not an all-pass result; the pinned worker image's native path remains the relevant runtime check. Exact commands and failure are in`task_memory/task_2026-11-09_profile_h800_preparation/test_report_2026-11-09_four_node_rollout.md`in the preparation worktree.

The separate length launcher commit`8c9537bf` passes53 launcher+7 related tests, using explicit`context_tokens`, `prompt_tokens` and`response_tokens`. Formal profile-input wiring still requires parentTicket02 integration afterD1/D22. The standalone capacity prerequisite instead uses the existing sequential source, independently updated for D34 in`82915613`; that source preparation does not require starting parent integration. The historical Running receipt is`evidence/upstream-h200-length-checkpoint-20261109.json`; the terminal refresh follows below.

## Upstream prerequisite failure 2026-11-09T07:56Z

The previous Running observation is superseded. Direct personal Python API read at07:56:39Z reports job`exp-1109-144110-764758` Failed, finish07:47:18Z. Exact replica`exp-1109-144110-764758-student-cfcd2084` exits1 at07:47:04Z; platform cleanup subsequently stops the other student and teacher with`Some critical tasks failed.` The collector verifies creator`i-fengyicheng` and replica ownership by RJob UID`fa85b2a7-f48c-4ac5-8a06-402113aa874f`.

The native student log records:

| UTC | Observation | Source log line |
| --- | --- | --- |
|07:34:31.721|Initial`update_weights` starts on eight trainer actors|2902–2904|
|07:34:32|A colocated`/update_weights_from_tensor` request returns200|2921|
|07:34:31|Dedicated-engine custom NCCL group initialization reports world size9|2936|
|07:44:31.736|The same`update_weights` fails with`elapsed_s=600.0`, followed by`TimeoutError`|3063–3087|
|Fatal stack|`train.py:169` initial weight synchronization, before the rollout/training loop|3205–3213|

This establishes the failed stage and zero successful optimizer updates. It does not establish why synchronization stalled, nor a GPU OOM, network fault, or manual stop. No new256-turn admission or scoring-capacity acceptance was obtained. The next prerequisite is a cause-based synchronization repair followed by the unchanged native capacity checks.

Evidence: `evidence/upstream-capacity-status-20261109T0755Z.json` and `evidence/upstream-weight-sync-timeout-20261109.json`. The latter retains16 decisive native log lines, filtered exact platform objects and query limitations. The complete native log remains at`/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/capacity-expanded/r256/student/A/exp-1109-144110-764758-rank-0.log` (6,788,149 bytes). Bounded read-only SSH extraction used the corresponding`/mnt/ws-jfs/ycfeng` path; the line-numbered local excerpt is`/data/ycfeng/tmp/agent-opd-image/d1-d22-status-20261109T0755Z/native-failure-excerpt.json`. No source or runtime parameter was changed.

Exact platform collector command, after the runbook's personal proxy/auth initialization:

```bash
timeout 60s /data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/codex-home/skills/stepmind-gpu-worker/scripts/collect_failure_evidence.py \
  exp-1109-144110-764758 \
  --replica exp-1109-144110-764758-student-cfcd2084 \
  --expected-creator i-fengyicheng \
  --credential-dir /data/ycfeng/tmp/brainctl-auth-i-fengyicheng \
  --start 2026-11-09T07:43:00Z --end 2026-11-09T07:48:00Z \
  --timeout 15 \
  --output /data/ycfeng/tmp/agent-opd-image/rca-exp-1109-144110-764758
```

Environment: Python3.10.6, brainpp2.8.6. Collector exit1: six event/log/DeepScan queries succeeded, while both all-operation audit queries raised`ReadTimeout` after15s. No existing DeepScan flow was returned. Failed/empty query coverage does not exclude events; manual-stop actor/request time remainUNKNOWN. The business timeout is independently present in the retained native log. Read-only diagnosis owner:`profile-initial-weight-sync-20261109` (`ses_e40a9a62effejB0VqD42HkARmR`); no replacement GPU job has been submitted.

Documentation verification uses the existing two commands above. The first check found two new links whose anchors omitted the heading's punctuation-derived hyphen; the heading was simplified before rerunning. Final result:24 files,6 tickets,76 links,23 anchors,zero errors; `git diff --check` PASS. This is a documentation correction, separate from the native job failure.

## Subsequent prerequisite repair and preparation

The native excerpt also records a dedicated`/update_weights_from_distributed` HTTP400 at07:34:32, before the outer600-second deadline. CPU reproduction found that hybrid setup discarded dedicated engines' lifecycle updaters while continuing to send tensors to them. Isolated commit`7689fbec` retains the complete lifecycle map, and review`profile-hybrid-session-review-20261109` found no defects. Subsequent`422a613d` aligns the full receiver collection with upstream`864cac87`; byte comparison passed and the37 affected protocol/lifecycle checks pass. The earlier broader80-test result belongs to the initial repair, not a repeated all-suite run.

Exact-image source probe`exp-1109-161858-331786`: Succeeded at08:19:13Z; creator`i-fengyicheng`;2CPU/0GPU; Python3.12.16; SGLang`0.5.24.dev80+g056f871`. It confirms scheduler lines266–319 refuse a distributed write without an active session before entering receive and HTTP lines1537–1552 map failure to400. Evidence:`evidence/native-weight-session-source-20261109.json` and`evidence/native-weight-session-source-job-20261109.json`. This closes the previous version mismatch; it does not recover the original HTTP response body or stalled trainer program counter and does not establish native CUDA/NCCL success.

The isolated source/checker fixes`82915613` and`8d517b48` pass39 and19 affected checks respectively. Candidate`h800_capacity_config.json` requests36 GPUs, eightTP4 rollout engines (two colocated/six dedicated), and the unchanged231/256-in1800s/two-update prerequisite. Native group resolution and exact argv values pass on CPU. `save_interval=None` disables scheduled HF saves through the existing periodic predicate. Parent formal profiles and200-update execution remain gated.

Native in-place receipt job`exp-1109-164358-350923` ran the unchanged baseline/visual/filter APIs against original posttrain sources, producing a complete filter in397.38s:9254 conversations,102 visual exclusions,10008 excluded eligible targets. The source metadata and native module hashes match the prior accepted audits. Receipts live in the preparation task's`evidence/native-visual-in-place/` directory and are not relabeled copy-based receipts or Qwen112K length statistics.

The original-source D34 parity job`exp-1109-170837-174061` failed before importing the checker because`spawn_tasks()` overrides`PYTHONPATH` with the mount root (`steptron/utils/stepmind.py:917`). A local quoting mistake in the next launcher produced no RJob. The corrected worker shell explicitly exports the project path, as the production submitter already does; its command is retained under preparation`evidence/native-inputs-in-place-d34/worker-command.json`. Retry`exp-1109-172310-849823` Succeeded09:28:42Z: all9 selected prefix checks and the real registry factory/request pass, first prompt4366 and request cap16384. Personal creator, exact image,0GPU and local NFS source were verified by API. Full commands/results are in the preparation task's`test_report_2026-11-09_native_preflight.md`. The new H800 native capacity run is pending; no parent merge or Ticket02/03 implementation has begun.

Prelaunch review found that the later`SweReplay._generate` caller still expanded the response budget. `0e7e0df3` removes that override, preserving the source and GenerateState limits while adding only the seed. Real replay→request regressions observe RED126706/16385 versus GREEN16384/16384;62 affected checks pass. The same reviewer closed P1 with no remaining findings. A final dry-run using the actual Python3.10.6 StepMind submission environment passes36-GPU role/RDMA/null-policy checks. No source re-audit or GPU acceptance is inferred from this caller correction.

## Historical first H800 attempt

The isolated configuration/source were frozen at`a470c841`, then the existing Python submitter created`exp-1109-181120-274261` at10:11:20Z. Fresh admission observed24 other H800 GPUs and requested36 with no count ceiling. Actual platform metadata verifies creator`i-fengyicheng`, H800/codesign, non-preemption, student4×8/teacher1×4, both student RDMA resources, exact image and NFS`100.96.128.195:/data/ycfeng:/data/ycfeng`. Earlier Pending state advanced to Starting at10:20:53Z; three student replicas and the teacher run while trainer-head startup remains pending. Four worker receipts expose28 actual H800 devices,81559MiB each, driver570.124.06; teacher-ready is published.

That launcher `sh_1bfca68aa001JWOGKI0d7wkd99` exited1 after the job Failed at10:29:35Z. Full native logs reveal two TP4 engines on rank2 first failed `ncclGetUniqueId` with invalid usage at10:28:57Z; later `matches=[]` errors and critical-failure cleanup followed. Ray registered4 nodes/32 student GPUs, but initial weights, bank acquisition and optimizer updates were not reached. Exact terminal and selected failure evidence is retained in preparation `evidence/h800-native-terminal-20261109.json` and `evidence/h800-first-native-failure-20261109.json`.

## Network-fixed H800 D34 native verification

Confirmed code behavior: head-inherited NCCL values in the job runtime env replaced rank2's local platform NIC/HCA selection (`ens20np0` versus `ens22np0`). Isolated `cf98293a` removes this inherited broadcast without new timeout or transport workarounds. The real caller-to-final-subprocess CPU regression is RED1 failed/2 passed→GREEN3 passed; related checks record529 passed/12 skipped/1 known-baseline parser case deselected. Review of the complete four-file diff `d91be845..cf98293a` returned No Findings. Native NCCL2.30.7 and effective engine environments are still unverified. Exact commands/limits: preparation `test_report_2026-11-09_node_local_network.md`.

After freeze `ebc0e6a0`, ordinary personal Python submission from `/data/ycfeng` created `exp-1109-192340-580111` at11:23:40Z. Fresh admission counts24 other H800+36 requested, with the explicit null personal ceiling and no preemption. Initial exact-job API read reports Starting, UID `28536e46-208d-4635-b648-27c782a09c9b`, creator `i-fengyicheng`, current-host source `100.96.128.195:/data/ycfeng:/data/ycfeng`, student4×8/teacher1×4, H800/codesign. Actual worker GPU observations,8 engines, weights and capacity outcomes are pending. Ordinary launcher `sh_1c00ca257001FAmkzN0D28AQ9j` remains responsible for job lifetime; log `/data/ycfeng/tmp/agent-opd-image/qwen35-h800-network-fixed-20261109.log`. The config changes only `phase`, `run_root`, `shared_dir`; lengths, seeds, models, loss, topology and native timeouts are unchanged. Cloud output root: `/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/capacity-h800-112k-network-fixed-20261109`.

Authoritative exact commands and filtered receipts are in preparation `test_report_2026-11-09_network_fixed_prelaunch.md`, `evidence/admission-h800-network-fixed-20261109.json`, `evidence/h800-network-fixed-native-startup-20261109.json`. Auxiliary environment/evidence checks remain soft-only; missing data is marked unverified and cannot stop healthy training.

At11:33:03Z all five current node receipts confirm36 actual H800 GPUs, matching the configured image and original model paths. Four student hosts have8 devices each; teacher has4,81559MiB/device anddriver570.124.06. Preparation `evidence/h800-network-fixed-worker-gpu-readback-20261109.json` retains the validated records. This hardware observation alone does not establish engines, effective process environment, synchronization or training.

The later complete native head-log read at 11:39:09Z confirms all eight engines ready by 11:36:41Z. Initial eight-actor `update_weights` starts at 11:37:18.596Z and ends successfully at 11:37:22.414Z with `elapsed_s=3.8`. Mixed tensor/distributed transfers and session begin/end return HTTP200. The native checksum event contains eight snapshots at version 0; contents and later changed-weight consistency are not yet independently verified. Exact preparation evidence: `evidence/h800-network-fixed-initial-sync-20261109.json`, with commands/limits in `test_report_2026-11-09_network_fixed_prelaunch.md`. Native post-warmup `/freeze_gc` connection-refused warnings were inspected, retained and not patched; they did not prevent readiness or synchronization. Source preparation is active, but no valid-bank count, optimizer ACK or second scoring is accepted in this readback. The H800 readiness result still does not replace the separate upstream D1/D22 contract.

Coordination at11:19Z: upstream `23b29f66` approves the original18-H200 retry, but no new job or acceptance is recorded. It has not adopted the parent D34 budget in its authoritative requirements. The H800112K/16K readiness run and upstream frozen D11 acceptance therefore stay separate; H800 results will not automatically satisfy D1/D22. Parent merge,02/03 integration and formal runs remain blocked; no other owner's job was stopped or held.

User-authorized cleanup removed the first terminal H800 smoke's167 cloud duplicates/15,325,989 logical bytes only after complete byte/hash-verified local retention. Original source assets, other tasks and shared trash were untouched. Raw archive: `/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-181120-274261-cloud-raw.tar.gz`; the exact report and receipts are in the preparation task. Physical OSS reclamation was not measured; the new live job's root is protected from cleanup.

## D35 parent adoption 2026-11-10

The user explicitly selected adoption of the completed H800 result; the exact question, answer and parent-only authorization are owned by[requirements D35](requirements.md#h800-capacity-adoption--original-request--follow-up-question-and-answer-2026-11-10). This changes the parent's capacity dependency, not the provenance or verdict of the preceding historical observations.

| Accepted check | Expected | Recorded actual | Verdict |
| --- | --- | --- | --- |
| Hardware and length contract | Current task's H800 D33/D34 configuration |36 actual H800/codesign GPUs;131072 context/114688 inclusive prompt/16384 completion | PASS |
| Native bank admission |≥231/256 within1800s |256/256 valid in1633.2862s; no invalid/missing/pending slots | PASS |
| Optimizer and fresh scoring |Two successful ACKs and second scoring on the same bank |Two unskipped ACKs;bank0 visits1/2; ranks0–7 each complete2×88 microbatches;second scoring afterACK1 | PASS |
| Terminal state |Job and all replicas Succeeded |`exp-1109-192340-580111`, UID`28536e46-208d-4635-b648-27c782a09c9b`;four student replicas and one teacher Succeeded | PASS |
| Updated text weights |Same text hashes on all eight engines, including update |1644 hashes equal atversions0/1;same972 hashes changed on all engines | PASS, TEXT ONLY |

Canonical preparation evidence, relative to this task after consolidation:

- `../task_2026-11-09_profile_h800_preparation/evidence/h800-network-fixed-capacity-acceptance-20261109.json`
- `../task_2026-11-09_profile_h800_preparation/evidence/h800-network-fixed-native-capacity-final-20261109.json`
- `../task_2026-11-09_profile_h800_preparation/evidence/h800-network-fixed-native-terminal-20261109.json`
- `../task_2026-11-09_profile_h800_preparation/evidence/h800-network-fixed-version-one-checksum-check-20261109.json`
- `../task_2026-11-09_profile_h800_preparation/test_report_2026-11-09_network_fixed_prelaunch.md` — exact native/readback commands, environment and limits.

These references are deliberately plain-code paths: the records are currently in the sibling preparation worktree and will resolve locally only after the primary merges them. Candidate`agent-opd-h800-capacity`contains`c52991ac`ancestry and H800 fixes; actual merge commit and final artifact resolution remainpending. The original result receipt's upstream-not-accepted field correctly describes its2026-11-09 scope; D35 is the separate later parent authorization, not a rewrite of that receipt.

Limits remain unchanged: this was the sequential A/r256 two-use capacity prerequisite, not parent32×8/full/profile integration or either200-update formal cell. Whole-model checksum equality and final engine NIC/HCA variables are not verified. Native profile checks are due at A's first formal successful update underD16; no additionalGPU smoke is required. Local D35 documentation checks are recorded in`test_report_2026-11-10_d35_records.md`; this delegation performs no platform operation or fresh runtime verification.
