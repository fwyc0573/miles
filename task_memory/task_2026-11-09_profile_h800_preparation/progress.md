## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Open the H800 resource-preparation slice from upstream c52991ac. |
| 2026-11-09 | Record the CPU admission baseline and explicit-unlimited regression coverage. |
| 2026-11-09 | Verify nullable ceilings, affected submission checks, and the scoped progress checkpoint. |
| 2026-11-09 | Complete the delegated admission slice and prepare the single verified delivery commit. |
| 2026-11-09 | Start the independently configured native prompt/response launcher follow-up. |
| 2026-11-09 | Verify 53 launcher and 7 directly affected argv tests; update the scoped length checkpoint. |

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

## pending

- Primary-owned work: hardware feasibility/configuration and CPU payload validation; consolidate onto the parent final branch after its upstream gate. This subagent did not edit configs or parent Ticket02/03, inspect/change platform resources, or touch other worktrees.

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
