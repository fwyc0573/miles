## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record independent Ticket08 baseline-specific readiness and correct its overbroad progress blocker without accepting all of03. |
| 2026-11-08 | Record parent-launch, T02 and T03 phase findings, remediation ownership and native-verification limits. |
| 2026-11-08 | Record the post-freeze two-axis review of commit `f2f86fea` and its remediation; renumber the baseline/comparison rows. |
| 2026-11-08 | Refresh the final D1–D10 checkpoint, nine-ticket graph and closure of both follow-up review findings. |
| 2026-11-08 | Record the phase checkpoint and remediation of DOC-REVIEW findings after D1/D2. |

## 1. 规划完成情况

**汇总：** PASS 4｜BLOCKED/FAILED/SKIPPED 8｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| Spec + 9 tickets 落地 | PASS | 全部文件已写入，D1–D10已记录；不是运行验收。 |
| 源码证据汇总 | PASS | DATA/MILES/EVAL/OPTIMIZER完成，主agent已复核决定性证据。 |
| 文档检查与review修订 | PASS | 17文件、9票、25链接、1anchor检查通过；5项累计review findings均已修订。 |
| 文档冻结 | PASS | 用户实际回答“确认冻结（推荐）”。 |
| 01 默认SWE输入 | TODO | 文档前置已完成，实施尚未开始。 |
| 02 Replay与指标 | BLOCKED | 等待01。 |
| 03 HF异步评测与释放 | BLOCKED | 等待01。 |
| 04 A/full | BLOCKED | 等待02/03。 |
| 05 A/r256 | BLOCKED | 等待02/03。 |
| 06 B/full | BLOCKED | 等待02/03。 |
| 07 B/r256 | BLOCKED | 等待02/03。 |
| 08 原始学生基线 | BLOCKED | 等待01/03，不阻塞04–07。 |
| 09 对比归档 | BLOCKED | 等待04–08。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** D2阶段checkpoint至整体冻结｜**当前前沿：** 文档归档；后续实施从01开始。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 文档变更后按需更新一次九票图/链接/预算检查，无新增测试框架。 |
| D2 细节反复重试 | CLEAR | 单次patch上下文错误纠正后成功；review回执缺正文只补取一次。 |
| D3 支线问题修补 | CLEAR | 未编辑旧任务、部署配置或训练代码。 |
| D4 可并行任务停滞 | CLEAR | 优化器研究、主体访谈与后续review独立推进；未来baseline与正式cell无串行边。 |
| D5 超范围镀金 | CLEAR | 共同baseline由D8明确授权；其余扩写落实已有需求。 |
| D6 分析空转 | CLEAR | 每项源码结论或回答均进入合同，已形成最终17文档交付。 |
| D7 路线违背 | CLEAR | 保持docs-only；未把推荐、历史验收或文件提交当作执行批准。 |

**文档检查：** 当前S1–S6均无残留缺陷。原full/r256验收和HF200清理矛盾已修正；本轮补齐原生gradient objective的归属与验收，旧八票编号检查已由实际九票DAG检查替代。未验证运行能力均由01/02/03承担，不借文档PASS放行。
**归因：** 无。

## 3. 纠正建议

**分支：** A：当前spec/tickets合理，无需新增改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 归档已确认的文档交付 → 完成标志：冻结答复、验证与仅含本任务文件的提交可追溯。
2. 后续实施入口为01 → 完成标志：默认SWE加载与身份契约达到该票验收条件。
3. 01完成后02与03并行 → 完成标志以各ticket实际验收为准，本次docs交付不提前标done。

## 4. 最值得关注的 3 点

1. 全矩阵目标800updates与6800评测attempts；D7早停、缺失评测均需保留INCOMPLETE，不能补造计划数。
2. 主KL、真实OPD梯度和TIS是不同契约，S4已明确其计算与detach，02负责原生验证。
3. 冻结时的D9为个人合计56卡；后续用户明确修订，当前规则见spec S7。实际容量与运行仍由后续tickets验证。

审查记录：DOC-REVIEW，reviewer session`ses_e48b02733ffejx5fyyB0aqqlby`，范围为新任务全部文档及GLOSSARY新增术语。初轮3项P2已独立确认关闭；复轮2项P2（缺实际反传目标、旧八票图检查）由主agent依据源码与本次执行检查修订关闭。未声称reviewer已重查最后修订或做过运行验证。

## 5. 冻结后双轴审查 — 2026-11-08

**范围：** 提交 `f2f86fea` 相对父提交 `cc1401d5` 的 18 个文档文件（task 目录 17 个新增文件与 `GLOSSARY.md` 新增 12 行）。审查前 `git diff f2f86fea` 与 `git status` 对这些文件均无输出，工作区与提交一致。
**审查者：** Standards 子代理 `ses_e4658531affeyA0QT4RKm7MVRM`，依据 `.agents/rules/single-source-of-truth.md`、`REVIEW.md`、全局 AGENTS.md 的 Task Records 与表述规则、to-tickets 模板和 GLOSSARY 格式；Spec 子代理 `ses_e4658531affdEO4PN5SKX9XDFl`，对照原始请求、D1–D10、Steptron 与 Miles 源码。两者只读。

| ID | 轴 | 级别 | 发现 | 处理 |
| --- | --- | --- | --- | --- |
| R1 | Standards | Nit | 优化器参数在 requirements D3 与 spec S4 重复，summary 另列 TIS 上下界，违反 SSOT。 | requirements D3 只保留回答、采纳决定与依据，参数链接 spec；summary 改为链接 spec S4；spec 不变。 |
| R2 | Standards | Nit | 基线票 09 阻塞对比票 08，编号与依赖顺序相反（to-tickets 约定）。 | 用户批准后互换：08 为共同原始学生基线，09 为四 cell 对比；同步 plan、tickets、summary、progress、review 与 test report。 |
| R3 | Standards | Nit | progress、test report 等处英文叙述丢失词间空格（如 `successfulupdates`、`zerokeep`）。 | 补回空格，`zerokeep` 改写为 “stop on zero TIS survivors”；只改写法，不改记录内容。 |
| R4 | Standards | Judgement | 04–07 四票重复共同验收条件。 | 保留：每张正式 cell 票需要在独立上下文中单独判定完成。 |
| — | Spec | — | 无 P1–P3 发现。 | 无需修改。审查者未独立复核 SWE submodule 两版本差异；数据一致性、256 目标容量、梯度归约与 HF/评测/删除运行能力仍由 01–03 实测。 |

**验证：** 见 test report 的 “Post-review revision check”。本次修订不改变任何科学决定或验收条件。

## 6. Implementation phase reviews — 2026-11-08

The earlier sections record the documentation phase. Current execution status is in `progress.md` and `checkpoint_2026-11-08_implementation.md`.

### Parent launch/admission

Reviewer `ses_e4600735bffex5pmiLBYPLO0GQ` inspected the eight specified parent launch/config/test artifacts and frozen requirements. The changed-file list, dry-run/admission receipts and local report were supplied; the historical baseline diff was not independently verified by the reviewer.

| ID | Finding | Remediation and evidence |
| --- | --- | --- |
| L1 / P1 | Missing native dynamic-global-batch flag rejects SWE startup. | Added the flag. Exact native Megatron parser/driver check remains pending. |
| L2 / P1 | Small integration budgets defaulted to formal mode. | Configuration now explicitly sets `run_kind=smoke`; launcher forwards it. Formal checks remain strict. |
| L3 / P2 | Native `Terminated` jobs incorrectly consumed the budget. | Added native Terminated/Deleted states; Stopping still counts. Admission regression passed. |
| L4 / P2 | Shared/config/repo/temp path boundaries were not validated. | One validator is used by submitter and worker; seven combined path/signal regression cases passed. |
| L5 / P3 | Child exit/status handling diverged from the existing paired worker. | Shared signal-status conversion and CalledProcessError handling preserve23 and137 in fault-injection checks. |

Local affected suite:42 passed. Pinned-image suite:104 passed, no skips (`launch-checks-exp-1108-153652-994118.xml`). Native configuration acceptance is still pending: the separate full Megatron parse needs a real GPU and the existing complete training environment. No claim of parent launch runtime acceptance yet.

### T02 native replay/training

Reviewer `ses_e45deee1cffeShOOhyp106Skes` inspected the complete T02 changed-file list, mathematical specification, public integration contract and CPU/Gloo evidence. No native model/platform calls were performed. No actionable error was found in the recorded surrogate/detach, original denominator, pre-TIS KL/count mathematics or success-only control logic.

| ID | Finding | Owner/status |
| --- | --- | --- |
| T2-1 / P1 | Optional diagnostic omissions can stop healthy optimization or fail rank-locally before D7 collective. | T02-REMEDIATION: separate actual training-mask counts from optional diagnostic evidence. |
| T2-2 / P2 | stdout failure after optimizer success can prevent acknowledgement. | T02-REMEDIATION: isolate all diagnostic sinks and preserve native result/cleanup. |
| T2-3 / P2 | Canonical bank remains resident after its final successful use. | T02-REMEDIATION: release immediately at successful bank boundary/end; retain on skip. |
| T2-4 / P3 | Teacher failure/cancellation receipts lack stage/deadline identity. | T02-REMEDIATION: add isolated stage receipts without extra forwards. |

Remediation session: `ses_e46206d68ffeuuECrBU2rN5aa7`. Real Qwen GPU/231/255/128K and throughput checks remain pending; T02 is not accepted.

### T03 persistent evaluation

Reviewer `ses_e45eb6f97ffeKvjf34jqPxjGk5` inspected all four new Python modules/tests, three evidence files, frozen requirements and relevant native grader/agent/exporter interfaces. No native/ACS/platform execution was performed.

| ID | Finding | Owner/status |
| --- | --- | --- |
| T3-1 / P1 | Model `apply_patch_fail` can be treated as retryable infrastructure failure. | T03-REMEDIATION: archive verified model failure as False using real native artifact formats. |
| T3-2 / P1 | Native `exit_env_error` autosubmit may be hidden by ordinary unresolved grading. | T03-REMEDIATION: inspect structured native infrastructure exits before terminal scoring. |
| T3-3 / P2 | Complete child outcomes or grading-only recovery can be lost before parent ledger persistence. | T03-REMEDIATION: recover validated native outcomes/trajectories before new generation. |
| T3-4 / P2 | Runtime can replace its self-supplied source/input hashes across resume. | T03-REMEDIATION: bind scientific configuration and pins to immutable point manifest. |
| T3-5 / P2 | Repeated worker cancellation can interrupt native child reaping. | T03-REMEDIATION: cancel once and await protected cleanup; verify four slow-TERM workers. |

Remediation session: `ses_e45df2e96ffeu2r2c5xjvsDOn8`. Existing28 fixture passes do not establish native ACS/model/grader, cloud durability or reader-platform termination; T03 is not accepted.

### Ticket08 baseline-specific readiness

Reviewer `ses_e44a21e69ffewws62CNDQ7RzIu` inspected the current requirements/spec/plan,03/08 tickets, qualification/source/reader receipts, formal-accounting report, cloud lifecycle JUnit, five evaluator/submission modules and `evaluation_deepswe_formal_{inputs,config}.json`. It returned GO for starting08 only; no tests, resource operations or writes were performed by the reviewer.

OneP2 documentation finding: progress incorrectly grouped02 capacity, D11 training inputs and03 asynchronous training integration as04–08 prerequisites. Ticket08 explicitly depends only on01's original-model/task identities and03's native SWE evaluation capability. Corrected the progress line and documented these scoped edges;03 stays in-progress and04–07 retain their full prerequisites.

Readiness evidence: real original4B recovery/HF3 native agent/grader outcomes, stable task/seed/version/artifact references, exited readers,215+8 accounting checks and8 cloud lifecycle fixtures. The new formal profile keeps the qualified runtime/server/contract and fixed100 IDs unchanged, enables no qualification subset and protects the original source. Its actual launcher dry-run passed. This is not a400-result score, a throughput guarantee or final08 acceptance. Submission still requires fresh policy admission; formal failure/timing accounting must be inspected in real output.
