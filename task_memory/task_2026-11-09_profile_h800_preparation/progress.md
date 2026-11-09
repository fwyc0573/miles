## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Close terminal review P3 and selected offline evidence delivery; reference parent D35 with merge still primary-owned and pending. |
| 2026-11-09 | Accept complete H800 D34 capacity and clean both terminal smoke roots; preserve unresolved upstream contract dependency. |
| 2026-11-09 | Accept the independent D34 bank admission: 256 valid slots in 1633.3 seconds; continue to native training checks. |
| 2026-11-09 | Record successful native eight-engine initialization and initial weight synchronization; keep bank/training acceptance open. |
| 2026-11-09 | Record fresh admission and actual network-fixed H800 job exp-1109-192340-580111, with initial platform Starting readback. |
| 2026-11-09 | Record cf98293a CPU/static repair acceptance and freeze a separate-output H800 D34 native retry candidate. |
| 2026-11-09 | Record terminal startup failure, node-network discriminator and cloud cleanup steering. |
| 2026-11-09 | Record the36-H800 submission, personal admission, platform role/resource policy and initial worker GPU evidence. |
| 2026-11-09 | Open the H800 resource-preparation slice from upstream c52991ac. |
| 2026-11-09 | Record the CPU admission baseline and explicit-unlimited regression coverage. |
| 2026-11-09 | Verify nullable ceilings, affected submission checks, and the scoped progress checkpoint. |
| 2026-11-09 | Complete the delegated admission slice and prepare the single verified delivery commit. |
| 2026-11-09 | Start the independently configured native prompt/response launcher follow-up. |
| 2026-11-09 | Verify 53 launcher and 7 directly affected argv tests; update the scoped length checkpoint. |
| 2026-11-09 | Complete session/source repairs and native visual receipts; prepare the36-H800 payload and diagnose the zero-GPU parity launch import failure. |

# Progress

## completed

- `profile-h800-admission-20261109`: inspected root `AGENTS.md`, all ten `.agents/rules` Markdown files, this task's requirements/plan/progress, budget implementation/tests, and the existing submission consumers. Scope remains budget code, the existing budget test file, and preparation progress/test-report/summary only.
- Baseline command: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_rjob_budget.py -q -p no:cacheprovider` from this worktree. Result: **10 passed**, 2 pre-existing SWIG deprecation warnings, 0.20 s; Python 3.12.13. No platform calls occurred.
- Added regression cases for explicit absent ceilings, fresh paginated/task/personal inventory, H800 requests of 160 GPUs, finite scope behavior, expiry during inventory reads, and allocation identity/resource/policy binding. Missing policy and receipt fields must remain errors rather than unlimited defaults.
- Before the implementation change, `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_rjob_budget.py -q -p no:cacheprovider -k test_unlimited_allocation_requires_explicit_ceiling_and_matching_receipt` produced **2 expected failures**, 23 deselected, 0.36 s: `TypeError: '<' not supported between instances of 'NoneType' and 'int'` at `rjob_budget.py:57`. This confirmed the unsupported nullable ceiling in both scopes.
- Extended the existing `ceiling` argument to `int | None`. Only explicit `None` disables the arithmetic count limit; all native inventory pages are still read. Existing policy keys remain required dictionary accesses, so absent keys do not become unlimited. No ceiling surrogate, flag, config change, or alternate admission path was added.
- Updated `validate_allocation` to require the explicit `ceiling_gpus` field, accept its recorded `None` only when the selected recorded policy also has `None`, and retain identity, job, requested/committed GPU counts, timestamp/scope and preemption consistency checks. Active finite task windows still select overflow preemption; expiry still reads the personal inventory and applies the personal policy. Previously admitted receipts remain valid after wall-clock expiry.
- Final budget command (same as baseline): **25 passed**, 2 pre-existing warnings, 0.25 s. An earlier verified run before adding the JSON receipt round-trip case passed all 25 tests in 0.28 s.
- Affected consumer command: `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_evaluation_submission.py -q -p no:cacheprovider -k 'fresh_snapshot_submit_and_receipt_share_the_lock or expired_personal_ceiling_denies_without_backend_submit'`: **4 passed**, 44 deselected, 2 pre-existing warnings, 0.90 s. Existing test fixtures replace the platform API/backend; no real RJob calls occurred.
- `git diff --check`: **PASS**, no output. Full evidence and acceptance values are in `test_report_2026-11-09_nullable_gpu_admission.md`.

- Admission slice final status: **completed**, commit `1ae93261` on branch `agent-opd-h800-capacity`. Only its two owned Python files and progress/test-report/summary were included. Initial untracked `requirements.md` and `plan.md` were preserved and excluded from that earlier commit; the new launcher follow-up explicitly authorizes updating and committing those primary-created records.

## Current frontier, 2026-11-10

- H800 D34 native capacity and both terminal-smoke cleanups are **completed**. Parent D35 explicitly adopts this accepted H800 result for parent D1/D22 and authorizes merge/T02/T03. Parent merge and Ticket02/03 remain **pending, primary-owned**, not completed here; upstream old-D11 acceptance is unchanged.
- `profile-h800-archive-close-20261110`: **completed** scoped archive verification and documentation, delivered by the associated Git commit (identity in Git history and the handoff). The existing offline checker, scoped Ruff/Black/isort and diff checks pass. All 21 explicitly selected files pass literal credential/private-key and size checks; 12 JSON receipts parse, maximum file 104231 bytes. The 73 untracked local evidence files/3832196 bytes and both complete raw archives are preserved. No platform, network, SSH, GPU operation or further cleanup occurred. Exact selection, commands and review limits: `test_report_2026-11-10_h800_archive_close.md`.
- Reviewer `profile-h800-terminal-acceptance-review-20261109` reported P3 for the stale frontier above and **No other findings**, as supplied by the primary's delegation. P3 is corrected here and in the current plan/checkpoint/summary. The supplied result is not a new review; receipt-only verification does not prove final NIC/HCA, whole-model/cryptographic provenance, physical OSS reclamation or formal-run trend coverage.

## Historical timeline, 2026-11-09

All subsequent Nov9 pending/in-progress labels and next actions record the state at that observation. They are not the current frontier; terminal completion entries and the Nov10 parent-only D35 decision supersede them without changing the upstream owner's contract or the original receipts.

## completed: profile-length-launcher-20261109

- User steering requires training/rollout context 131072, prompt budget 114688 and completion maximum 16384. Inspected the existing launch owner and native rollout field declarations; no equivalent prompt/response launch JSON inputs existed. Use the new explicit fields alongside `context_tokens`, not new CLI flags or literal defaults.
- Baseline command: `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_launcher.py -q -p no:cacheprovider`: **29 passed**, 20 warnings, 4.76 s; Python 3.12.13. The baseline launcher set response to context and omitted the prompt limit.
- Implemented required positive integer `context_tokens`/`prompt_tokens`/`response_tokens` validation and sum compatibility once in `_config`; `_training_args` directly consumes each owned input. Native seq/SGLang/rollout context remain independently sourced from `context_tokens`.
- Updated only in-memory archived-recipe fixtures in the launcher test file and three directly affected argv tests (`test_swe_capacity.py`, `test_swe_native_gradients.py`, `test_megatron_scoring_lifetime.py`). No archived JSON file changed; the separate historical `run_qwen35_opd.py` and `prepare_qwen35.py` constants remain unchanged.
- Integration limit: this worktree's `swe_inputs.py:177–178` still rejects response below context; its owner is another agent. The local worker dry-run renders flags without constructing inputs. A read-only attempt to inspect the parent's launcher found no file at the named `agent-opd-image` path, so no parent dry-run behavior is inferred. Full native input construction awaits the primary's integration; no validation monkeypatch is used.
- Final launcher command (same as baseline): **53 passed**, 20 existing warnings, 14.28 s. The actual unmocked subprocess dry-run passed and took 9.45 s; A/B × full/r256 argv checks found exactly one prompt flag 114688, one response flag 16384, and context/seq/SGLang lengths 131072. All 18 missing/invalid-field cases and the over-budget case rejected as expected.
- Affected argv command: `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_capacity.py tests/fast/test_swe_native_gradients.py tests/fast/test_megatron_scoring_lifetime.py -q -p no:cacheprovider -k 'combined_native_hook_registration_uses_real_generated_arguments or combined_native_hook_cli_registration_from_generated_argv or configuration_uses_existing_flag_carrier_without_recipe_edits or combined_cli_typed_before_log_prob_installs_without_swe_attempt or contrast_adds_only_observation_arguments'`: **7 passed**, 40 deselected, 20 existing warnings, 3.58 s. Broader unrelated tests were not run.
- `git diff --check`: **PASS**, no output. Complete exact commands, config contract, expected/actual native argv and limits are in `test_report_2026-11-09_native_launch_lengths.md`. All code in this launcher slice is verified; the scoped delivery commit contains the five owned Python files and preparation requirements/plan/progress/test-report/summary.
- Before staging, concurrent unowned changes appeared in `tests/manual/agent_opd/run_qwen35_opd.py` and `tests/manual/agent_opd/qwen35_pair_worker.py`. Read-only diff inspection shows multi-node allocation/lifecycle changes, not length constants or this launcher's argv path. Preserve and exclude these files from the length commit; no broadened tests or edits are required for this independently owned work.

## 1. 规划完成情况

**汇总：** PASS 2｜BLOCKED/FAILED/SKIPPED 2｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Plan 1：显式无限 GPU admission | PASS | 现有字段与 receipt 校验已扩展；25 项 budget 测试和 4 项相关 consumer 测试通过。 |
| Plan 2：H800 memory/topology 与 config | TODO | 主 agent 所有；本委派明确禁止 config/platform 操作，没有完成证据。 |
| Plan 3：CPU payload/worker 验证 | BLOCKED | 完整 native input 端验证需主 agent 的新 config 和另一个 agent 的 input/checker/audit 整合。 |
| Plan 4：整合至父分支 | BLOCKED | Plan 4 与 requirements 指定保留父任务 upstream/merge gate。 |
| Plan 5：native launcher 独立长度配置 | PASS | 53 项 launcher 和 7 项直接 argv 测试通过；实际 CPU dry-run 发出 112K/16K，无 context-sized response override。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 上次 admission checkpoint 至本次 launcher 验证｜**当前前沿：** launcher 代码交接与主 agent 的独立 H800 准备。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 只补长度边界、真实 dry-run 与直接受影响的 argv fixture；通过后停止扩大测试。 |
| D2 细节反复重试 | CLEAR | launcher 一次实现即 53 + 7 全通过，没有失败重试循环。 |
| D3 支线问题修补 | CLEAR | native inputs 的已知旧限制交给明确 owner，没有在本分支绕过或修改。 |
| D4 可并行任务停滞 | CLEAR | 用户明确分开所有权；主 agent 的并行准备不由本切片执行。 |
| D5 超范围镀金 | CLEAR | 只接入两个明确 JSON 字段和既有 native flag，没有默认值、重复 knob 或历史 workflow 改动。 |
| D6 分析空转 | CLEAR | owner/caller 检查确定接口，随后实现并完成有界验证。 |
| D7 路线违背 | CLEAR | 保留历史 preparer、archived config 和父 input/checker/audit；没有平台或父 Ticket02/03 操作。 |

**文档检查：** S1–S6 均未发现明显缺陷。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 本切片：提交 launcher 限定文件及已授权的 requirements/plan → 完成标志：提交 hash 与必填长度 contract 可交接。
2. 主 agent 并行：H800 config/资源准备 ‖ parent input/checker/audit 整合 → 完成标志：Plan 3 可以使用真实新配置验证，无 input 端旧 response>=context 限制。

## 4. 最值得关注的 3 点

1. 新 launch JSON 必须显式给出 context/prompt/response 正整数；当前值是 131072/114688/16384。
2. 本地 dry-run 和 native argv 已通过，但不是完整 native input 或 GPU 执行验证。
3. parent input/checker/audit 与新 H800 config 是整体验证依赖；不能通过 runtime monkeypatch 消除该依赖。

## Historical primary execution, 2026-11-09: native capacity prerequisite

### completed

- `7689fbec`: hybrid lifecycle regression RED2→GREEN2;80 related checks passed. Read-only fixed-diff review`profile-hybrid-session-review-20261109` returned no findings. Exact pinned-image CPU probe`exp-1109-161858-331786` succeeded and confirmed SGLang`0.5.24.dev80+g056f871` rejects distributed writes outside a session before receive.
- `422a613d`: align complete receiver metadata and local IPC mapping with upstream`864cac87`; source blob equality verified as`fa8d01b1b4bacd9edfe7b4f287f5391c136ed7bc`. Update two stale receiver-list assertions; final affected protocol/lifecycle suite37 PASS. No transport, timeout or NCCL behavior is replaced.
- `82915613`: existing native sequential capacity source accepts112K equality, skips oversized prompts before slots, caps completion at16K;39 affected checks passed. `8d517b48`: existing parity checker supports those native flags and checks the actual registry factory/request budget;19 checks passed. Parent32×8 profile integration is not part of either change.
- `h800_capacity_config.json`, `h800_gpu_policy.json`, `h800_capacity_sglang.yaml`: actual submitter dry-run requests36 GPUs, student replicas4×8 and teacher1×4, explicit null personal ceiling, codesign/H800, no preemption. Native config resolution returns8 engines,2 colocated and6 dedicated, TP4 each; only the colocated group offloads. Evidence:`evidence/h800-native-layout-20261109.json`.
- Candidate argv has exactly one seq/context131072, prompt114688, response16384, trainer8/TP4, rollout32, slots256, acquisition1800 and updates2. `save_interval=None` emits no save-interval flag and the native periodic predicate is false at both updates. This is CPU configuration evidence, not native execution.
- In-place native baseline/visual/filter job`exp-1109-164358-350923` completed the three unchanged native APIs in397.38s:9254 trajectories,102 excluded visual conversations,10008 excluded eligible targets. Filter`complete=true`, no failure codes, all8 source scans finished. Native hashes match the accepted upstream functions. Artifacts:`evidence/native-visual-in-place/`; no dataset copy or receipt relabeling.
- Native audit Python3.12.13/Transformers4.57.6 lacked`ijson` and`loguru`. A public PyPI install timed out; the documented Basemind mirror installed only`ijson==3.6.0` and`loguru==0.7.3`, followed by actual native tokenizer construction and the completed audit. The source producer's native atomic receipts were root-owned0600; only these three new task receipts were made0644. The new task evidence directory was returned to the submitting user's ownership for primary evidence writes; unrelated directories were untouched. The retained wrapper now sets published receipt readability itself.

### in-progress

- Original-source D34 parity is now accepted: CPU job`exp-1109-172310-849823` Succeeded09:28:42Z, verified personal creator/exact image/current-host source mount/8CPU/0GPU. Actual native registry factory and request construction PASS with4366 prompt tokens and max16384; all9 selected prefixes pass their identity/eligibility checks. Exact report:`test_report_2026-11-09_native_preflight.md`; artifacts:`evidence/native-inputs-in-place-d34/` and`evidence/native-input-preflight-jobs-20261109.json`.
- Historical first CPU job`exp-1109-170837-174061` failed before import: `No module named tests.manual`. The cause is`steptron/utils/stepmind.py:917`, which replaces`PYTHONPATH` with`code_mount_point`. The intermediate worker-shell attempt failed locally with`NameError: worker` and created no RJob. The successful worker shell follows production ordering by exporting the repo path before execution; its exact command is retained. No source behavior or acceptance threshold was changed to obtain PASS.
- Plan3/7 preflight is complete. Review`profile-h800-prelaunch-review-20261109` found a later override in real`SweReplay._generate`; fix`0e7e0df3` preserves the sample/default budgets and seed, with62 affected checks PASS and actual replay→request RED126706/16385→GREEN16384/16384. The reviewer closed P1 with no remaining findings. The actual Python3.10 submission environment's dry-run also passes36-GPU/role/RDMA/null-policy checks (`evidence/h800-submission-dry-run-20261109.json`). Configuration and preflight delivery frozen at`a470c841` before submission.
- Submitted`exp-1109-181120-274261` at10:11:20Z through the existing personal Python submitter from`/data/ycfeng`. Live admission counted24 other H800 GPUs plus this36-GPU request; explicit null ceiling, non-preemptible, codesign. Platform readback confirms both roles have H800 positive tags, codesign and preemptible=no, student4×8/teacher1×4, both required student RDMA limits, exact image and current-host NFS`100.96.128.195:/data/ycfeng:/data/ycfeng`. Receipts:`evidence/admission-h800-capacity-20261109.json`, `h800-native-startup-20261109.json`, `h800-native-resource-policy-20261109.json`.
- At10:20:53Z the job is Starting: student ranks1–3 and teacher Running; student rank0 Starting. At10:23:50Z worker receipts confirm28 actual H800 devices across those four started roles, each81559MiB/driver570.124.06. Teacher-ready is published. This is startup evidence, not synchronization or training acceptance. Receipts:`evidence/h800-native-resume-20261109T102053Z.json`, `h800-worker-gpu-readback-20261109.json`; live shared records are under`evidence/h800-capacity-112k/r256/exp-1109-181120-274261/A/`.
- Historical launcher owner:`sh_1bfca68aa001JWOGKI0d7wkd99`; local raw log:`/data/ycfeng/tmp/agent-opd-image/qwen35-h800-capacity-20261109.log`. It exited1 after the platform's terminal failure. No duplicate or fresh GPU attempt has been submitted.
- Trainer-head logs retrieved10:29:21Z show platform worker-init at10:25:03Z and Ready to go at10:25:05Z, with NODE_RANK0/NODE_COUNT4, H800, all8 CUDA device IDs and native RoCE/NCCL variables. This confirms head initialization has advanced; it does not replace its missing application GPU receipt or establish weight synchronization. Evidence:`evidence/h800-trainer-head-startup-log-20261109.json`.

### pending

- Correct and verify the native startup cause before a fresh capacity attempt; then verify all36 GPUs, eight engines and native weight publication, at least231/256 within1800s, two optimizer ACKs and second-student scoring. D1/D22 remain unmet until those business outcomes are accepted.
- Read-only upstream coordination at09:10Z found no new capacity retry after`exp-1109-144110-764758`; upstream's proposed18-H200 retry awaits its own approval. Its shared gate evidence and the isolated H800 prerequisite must not be counted as two different acceptances.
- Parent merge and Ticket02/03 integration remain blocked. The parent's independent full112K length-distribution audit is separate from this native visual/source readiness check.

### failed: first native H800 startup

- Platform job`exp-1109-181120-274261`, UID`8af62b65-5176-472a-bb2d-86ab35776203`, Failed at10:29:35Z. Student rank0 failed; the other three students and teacher were stopped afterwards with`Some critical tasks failed.` This is not capacity acceptance. Exact terminal readback:`evidence/h800-native-terminal-20261109.json`.
- Head application receipts subsequently confirm node0 published10:25:19Z and Ray cluster registered4 nodes/32 student GPUs by10:26:12Z. The earlier10:23:50Z missing-node0 observation was only startup timing, not a failure boundary.
- Full rank0 business log retained at`/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-181120-274261-head.log`. First native exceptions at10:28:57Z are two SGLang TP4 engines on rank2/10.191.5.7 failing in`ncclGetUniqueId()` with`NCCL error: invalid usage`. Later`matches=[]`, driver exit1, student supervision and platform cleanup follow those failures. Initial weight publication, bank acquisition and successful updates were not reached.
- Node platform receipts differ: head/ranks1/3 use`NCCL_SOCKET_IFNAME=ens20np0`; rank2 uses`ens22np0` and a different HCA ordering. A local ctypes NCCL2.28.9 discriminator returned5/invalid-usage and`Bootstrap : no socket interface found` when selecting the absent`ens20np0`, versus0/no-error with native local`eth0`. This is a CPU discriminator, not proof of the pinned native2.30.7 receiver environment.
- `profile-h800-node-network-20261109` owns the local production environment-propagation trace and CPU regression/fix. Primary owns all platform/cloud evidence. Exact-node read-only RCA collector completed all8 queries; raw query evidence is under`/data/ycfeng/tmp/agent-opd-image/rca-h800-exp-1109-181120-274261` and still requires interpretation before any external-stop or OOM claim.

### completed: cloud cleanup

- Latest user request authorizes timely cleanup of this session's obsolete smoke/temporary cloud outputs. Exact task-root inventory found only`capacity-h800-112k-20261109`, totaling15,325,989 logical bytes; no model/checkpoint/dataset payload was produced by this failed startup.
- Retained a restricted local raw archive at`/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-181120-274261-cloud-raw.tar.gz` (3,911,955 bytes), verified all167 file sizes and hashes, rechecked unchanged cloud contents, and deleted only that terminal smoke root at10:53:11Z. Independent readback finds the task's cloud parent empty. Source assets, other tasks and shared trash were untouched. Logical bytes removed:15,325,989; physical OSS reclamation remains unverified.
- Exact commands, archive verification and scope limits:`test_report_2026-11-09_cloud_cleanup.md`; receipts:`evidence/cloud-cleanup-{inventory,backup,result}-20261109.json`. Selected first native failures are preserved locally in`evidence/h800-first-native-failure-20261109.json`; raw code diagnosis can continue from the retained head log and archive.
- Local record checks: `git diff --check` PASS; selected28 task Markdown/top-level JSON files contain neither personal credential value and all JSON parses; backup/result receipts agree on167 files and15,325,989 bytes. No GPU check was rerun for this file cleanup. The updated`checkpoint_2026-11-09_native_preflight.md` maps Plan8 toFAILED, Plan9 toTODO and Plan10 toPASS, with no remaining route drift after correcting stale live-launcher records.

### completed: Plan9 CPU/static node-local NCCL repair

- `cf98293a` removes the head-inherited `NCCL_*` broadcast from `_runtime_env`; existing explicit deterministic/config controls and each node's raylet environment remain intact. Real launcher→Ray submission→native spec/manager→CommandActor→subprocess regression reproduces the heterogeneous rank2 socket/HCA overwrite before the fix and preserves native node values afterwards. Report:`test_report_2026-11-09_node_local_network.md`, RED1failed/2passed→GREEN3passed, final affected529passed/12skipped/1known-baseline parser case deselected. Native NCCL2.30.7 is not verified by the local2.28.9 discriminator.
- Fixed complete four-file diff`d91be845..cf98293a`, artifact`/data/ycfeng/tmp/agent-opd-image/cf98293a-fixed-review.diff`, was reviewed by`profile-h800-node-network-review-20261109` (`ses_e3ffdba19ffe6ry9e4fP59h2Sc`): Standards/Spec No Findings. The reviewer did not rerun tests; native engine environments, TP4 initialization, initial weight publication and capacity acceptance remain unverified.
- Original config is preserved in the previous commits and failed-job receipts. Current `h800_capacity_config.json` changes exactly`phase`, `run_root`, `shared_dir` for a new native attempt. All scientific/resource fields are unchanged. Real submission dry-run passes36GPU allocation; actual train CLI argv remains131072/114688/16384, TP4,32rollout GPUs,256slots,1800seconds,2ACK budget/2bank uses. Head NIC/HCA values are absent from the produced job env. Evidence:`evidence/h800-network-fixed-{submission,native-argv}-dry-run-20261109.json`.
- The first argv-inspection command incorrectly treated successful textual CLI output as JSON. Correct inspection uses`shlex.split`; no RJob was created and no product behavior changed. Exact commands and verification limits:`test_report_2026-11-09_network_fixed_prelaunch.md`.

### in-progress: fresh H800 D34 native verification

- At11:19Z the upstream local coordination check still found no new capacity job, but its18-H200 rerun is now approved in`23b29f66`. Upstream has not recorded the parent's112K/16K budgets; its D11 acceptance is separate. The H800 owner will verify its own D34 hardware/runtime contract without stopping or holding the other owner's job or claiming that a differently filtered bank accepts D11.
- New output root:`/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/capacity-h800-112k-network-fixed-20261109`; selected local evidence:`evidence/h800-capacity-112k-network-fixed`. Configuration/CPU readiness frozen at`ebc0e6a0`; the ordinary personal Python submitter from`/data/ycfeng` created`exp-1109-192340-580111` at11:23:40Z after fresh admission. Receipt:`evidence/admission-h800-network-fixed-20261109.json`,24otherH800+36requested, explicitnull personal ceiling, non-preemptible, current-host NFS`100.96.128.195:/data/ycfeng:/data/ycfeng`.
- First exact-job API read reports Starting, UID `28536e46-208d-4635-b648-27c782a09c9b`, creator `i-fengyicheng`, configured H800/codesign/no preemption, student4×8 and teacher1×4. The exact image, student host-network setting and requested RDMA resources are retained in `evidence/h800-network-fixed-native-startup-20261109.json`. This initial query verifies submitted platform resources, not worker hardware or business acceptance; later hardware observation is recorded below.
- New ordinary launcher owner:`sh_1c00ca257001FAmkzN0D28AQ9j`, log`/data/ycfeng/tmp/agent-opd-image/qwen35-h800-network-fixed-20261109.log`. Keep it alive throughout the workload. The older launcher exited1 and remains historical; no other owner's job was stopped orheld.
- At11:33:03Z, all five node receipts verify36 actual H800 GPUs,81559MiB each with driver570.124.06: four distinct student hosts with8 GPUs each and one teacher with4. Each receipt matches the job, pair, exact image and original model path. Evidence:`evidence/h800-network-fixed-worker-gpu-readback-20261109.json`. This completes worker hardware observation only; native engine initialization, weights and capacity remain open.
- Independent parent D34 source audit `exp-1109-154414-275606` is still Running at11:32:18Z. Its final-file progress reports `scanned=9200`, `renders=51549`, elapsed13382s at11:28:18Z. Missing final output files at this point do not imply a failed audit; the ordinary worker is making progress. Parent evidence:`evidence/source-audit-112k-runtime-20261109.json`; no final source-length statistics or parity acceptance is claimed yet.
- At 11:39:09Z, the complete 1,299,557-byte native head log confirms all eight engines ready by 11:36:41Z. Initial `update_weights` starts at 11:37:18.596Z and the eight-actor cell finishes `ok=true`, `elapsed_s=3.8` at 11:37:22.414Z. Begin/end session and distributed/tensor transfers return HTTP200; the native checksum event contains eight engine snapshots at weight version 0. Exact evidence: `evidence/h800-network-fixed-initial-sync-20261109.json`. Snapshot contents and the later changed-weight synchronization have not yet been independently verified.
- New tracebacks were inspected rather than treated as another NCCL failure: all nine headers in the captured stream belong to native post-warmup `/freeze_gc` connection-refused chains, including Ray-deduplicated messages. Servers subsequently report ready and initial synchronization succeeds. Evidence: `evidence/h800-network-fixed-initial-warning-classification-20261109.json`. No retry, source patch or stop was applied for this warning.
- Native source preparation is active: oversized candidate prompts are rejected against the configured context/prompt budgets. These rejection records are not successful generated/scored slots. Evidence: `evidence/h800-network-fixed-first-runtime-20261109.json`.
- Self-check after the native initialization milestone: Plan8 remains TODO, now at bank admission/training rather than startup; the parent and independent CPU source audit are still separate. All seven drift patterns are CLEAR. Corrected the stale Step8 scope phrase in `plan.md` under S5 without changing acceptance or authorization.
- Bank admission PASS: bounded read-only snapshot at 12:06:07Z finds `acquisition_sealed`, 256/256 completed slots, no invalid/missing/pending slots, and membership exactly 0–255. Native start/deadline/end timestamps are 1794224248.9532301 / 1794226048.953265 / 1794225882.2394156, yielding 1633.2862 seconds, below 1800. All 256 persisted samples retain `max_response_len=16384`. Evidence: `evidence/h800-network-fixed-acquisition-progress-20261109.json`. The journal is 594,158,701 bytes; it was read as a streaming snapshot and sample bodies were not duplicated into the local summary. This is the independent D34 bank, not the upstream frozen D11 acceptance artifact.
- Self-check after bank admission: Plan8 remains TODO at student scoring/backward/two optimizer ACKs and second scoring; startup and bank admission are now observed PASS. Keep the native launcher and healthy workload running. No auxiliary hard gate or unrelated fix is introduced; D1–D7 remain CLEAR.
- Next: obtain two optimizer ACKs, second-student scoring and two uses of this sealed bank. Later weight versions/consistency and effective engine environments remain unverified until captured. Auxiliary inspection failures cannot stop healthy training. Parent D1/D22 remain separate and unchanged.

### completed: Plan8 H800 D34 native capacity

- `exp-1109-192340-580111` and all five replicas are terminal Succeeded; the ordinary launcher exited successfully. Native bank 0 has 256 valid trajectories in 1633.2862 seconds, with two verified memberships/visits and two successful, unskipped optimizer ACKs. Every training rank 0–7 completes student scoring passes 0 and 1, each 88 microbatches; pass 1 uses updated weights after ACK1. Source identity and previous-output lifetime checks pass without observer-unverified events. The actual 128K TP4 logits tensor is 15.15625 GiB/rank; maximum observed scoring PyTorch allocation is 28.89246 GiB, not whole-device or backward usage.
- Existing checksum events verify all 1644 text hashes equal across eight engines at versions 0/1, with the same 972 changed hashes. The frozen 1188 visual hashes differ only by offload topology and are excluded by the existing recipe, not a new exception. Read-only scope verification found no actionable text-path defect. Final NIC/HCA values are not exposed by server-info and remain unverified; placeholder provenance is not cryptographic. No auxiliary finding changed or stopped training.
- Evidence: `evidence/h800-network-fixed-{native-capacity-final,native-terminal,version-one-checksum-check,capacity-acceptance}-20261109.json`; full checks and limits in `test_report_2026-11-09_network_fixed_prelaunch.md`. Status: **PASS_H800_D34_NATIVE_CAPACITY**, separate from frozen upstream D11 and parent D1/D22. No parent merge, Ticket02/03 integration, or formal A/B run occurred.
- The independent 112K full-source audit is accepted in parent commit `a404850c`: job/replica Succeeded; 512 parity and 2048 interleaved draws PASS; source bytes unchanged. 37.1927% of eligible turns are overlength; the 32×8/200-update simulation has span median 5/p90 7/max 9 and 0/869 conversations at least 11 updates. This is not runtime trend coverage. Pre-length median remains 90, so the frozen D26 adjustment condition is not triggered.

### completed: Plan10 second terminal-smoke cleanup

- Inventory: 412 files, 2136889910 logical bytes. Verified every file against `/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-192340-580111-cloud-raw.tar.gz` (458427717 bytes), then rehashed all cloud files before exact-root removal at 12:50:11Z. Independent readback finds the task cloud parent empty. Archive and cleanup receipts: `evidence/cloud-cleanup-network-fixed-{inventory,backup,result}-20261109.json`.
- The first streaming verifier reopened a member and failed; one stream per member corrected it. Ordinary unlink was denied before any removal by root:root mode0755; after confirming all 412 files remained, the exact approved path was removed with `sudo -n`, without permission changes. Source assets, other tasks and shared trash were untouched.
- Cumulative session cleanup: 579 files, **2152215899 logical bytes**. Physical OSS reclamation remains unverified. Retained raw archives and selected acceptance evidence support later diagnosis without retaining duplicate cloud smoke outputs.
- Historical next step, Nov9 (superseded for the parent by D35): reconcile the separately frozen upstream D1/D22 dependency before any parent integration. The latest root branch then inspected was `34242784`, with session24 H200 admission support and no newer native acceptance in those records. The upstream contract is not relabeled by the Nov10 parent-only decision.
