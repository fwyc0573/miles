## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Advance D40 to pending namespace-counterfactual implementation/controls while retaining formal BLOCKED state and acceptance checkboxes. |
| 2026-11-11 | Record actual A metadata first4 equivalence, retain warm failure and the unselected namespace diagnostic frontier; no acceptance checkbox change. |
| 2026-11-11 | Accept CPU332/fixed dual review and record metadata A submitted with initial Starting snapshot; keep formal hold, native equivalence and all checkboxes unchanged. |
| 2026-11-11 | Advance A's current RCA to CPU first-four metadata/receiver/review preparation; no metadata GPU or minimization acceptance, all final checkbox states preserved. |
| 2026-11-11 | Record actual A source/cold success and full-model warm FAIL after bounded CUDA acceptance; retain formal hold and every acceptance checkbox. |
| 2026-11-11 | Record source/integration reviews and submitted A teacher-only FP32 probe Pending placement; formal A remains blocked and acceptance checkboxes stay unchanged. |
| 2026-11-11 | Advance A's current hold to unreviewed selected-FP32 source candidate/source identity/H800 cold-reference verification; retain all final checkbox states. |
| 2026-11-11 | Record A teacher-only native cold pass and warm-state probability blocker after completed comparison; formal A remains blocked with all checkboxes unchanged. |
| 2026-11-11 | Hold formal A under D40 workflow/parameter RCA; parallel benchmark/history preparation and phase-only config review do not change acceptance checkboxes. |
| 2026-11-11 | Apply D39 H800 A preparation from original initialization; retain terminal H2006/profile2, all prior evidence and every checkbox. |
| 2026-11-10 | Accept actual profileprefix2 and original-file rebuild; distinguish record/ACK timestamps, retaining every full-run checkbox. |
| 2026-11-10 | Record actual native IDs1/2 and accepted first corrected offload/restore/next-train cycle; keep detailed profile/200 verification pending and every checkbox unchanged. |
| 2026-11-10 | Record reviewed correction and independent corrected A executing/worker-ready; retain all checkbox states and pending native lifecycle/ACK/200 proof. |
| 2026-11-10 | Record D38 controlled diagnostic PASS and the in-progress native state-initialization correction; formal verification remains blocked. |
| 2026-11-10 | Accept the D16 first-update row; current A failed natively after1/200, blocking continuation/fresh attempts while allocation mechanism and fix remain unresolved. |
| 2026-11-10 | Record actual H200 first-bank/generation progress and open offline review repairs; retain real ACK/D16 and every final checkbox as incomplete. |
| 2026-11-10 | Update current context to D37 H200 preparation plus parallel inspector implementation; retain all unchecked criteria and historical H800 evidence. |
| 2026-11-10 | Record selected D36 wait route in current status only; resource improvement/readback and fresh admission remain pending, with no third attempt or acceptance change. |
| 2026-11-10 | Record both attempts failed before training; block further submission pending a placement/startup strategy decision, without changing ticket acceptance or CPU readiness. |
| 2026-11-10 | Retain first formal A FAILED0 updates separately and record freshly admitted unchanged retry; startup/first-update and all runtime criteria remain incomplete. |
| 2026-11-10 | Record actual A/full submission and worker-startup evidence; leave runtime acceptance incomplete. |
| 2026-11-10 | Record accepted03 CPU integration, explicit formal profile configuration and pre-run lifecycle checks; ready for fresh admission, not launched or GPU accepted. |
| 2026-11-10 | Record02 CPU-ready6129aefe;retain03 integration and formal native/profile checks as unfinished,without extra GPU smoke. |
| 2026-11-10 | Record merge55fba827 complete without accepting02/03 readiness or formal first-update profile verification. |
| 2026-11-10 | Apply D35 capacity adoption; preserve pending merge/integration and D16 profile verification at A's first formal update without another GPU smoke. |
| 2026-11-09 | Accept the completed D34 input re-audit while retaining the separate integration and formal-run blockers. |
| 2026-11-09 | Apply D33 H800 authorization and remove the superseded count limit;01 is accepted. |
| 2026-11-09 | Separate CPU launch readiness, actual first-update inspection and native/profile acceptance; retain soft-gate continuation and explicit incomplete evidence. |
| 2026-11-08 | Draft the A/full formal cell ticket. |
| 2026-11-08 | Apply the D17 GPU budget. |
| 2026-11-08 | Use the interleaved turn order (D18); add the update-20 timing report and D19. |
| 2026-11-08 | Use the SWE-1003 0913 data read in place (D23–D25). |

# 04: A/full 正式 cell（Qwen3.5-4B + Qwen3.5-27B）

**What to build:** 使用 SWE-1003 0913 数据、interleaved turn order（32 × 8）和 Distillation profile，完成 200 个 successful update；不保存 HF，不做评测。

**Blocked by:** 01、02、03 及D16/common-cycle、既有CPU/fixed review/native first4重现均已接受；新counterfactual实现/controls/isolation/native case结果PENDING，数值正确性及freshformal admission/独立200仍未解除。不resume或拼接旧probe/6。

**Status:** BLOCKED formal / CACHE_SALT_COUNTERFACTUAL_IMPLEMENTATION_IN_PROGRESS D40. Prior [A report](../test_report_2026-11-11_runtime_metadata_native_A_results.md)/[verification](../evidence/teacher-scoring-runtime-metadata-probe-20261111/native-verification-A.json), archive`92f3b9a0`and pinned replay`5c6ebce5`remain accepted first4/rep0 evidence, not a warm fix. Implementation owner prepares four files under [preregistration](../spec.md#d40-diagnostic-namespace-counterfactual-preregistration); no code/CPU/native placement/control/isolation/source-fix/performance/root-cause PASS yet. Baseline is immutable qualified caller`4f1139b0`, not pre-FP32. Only full-input unique salt changes; eight response controls and four cold controls must exactly match baseline before four same-run warm comparisons with original errors, including undefined zero-reference counts. Per-RID protected/page-aligned isolation replaces no-rebind/all-zero assumptions. Report cases rather than a generic warm summary; control/isolation failure is inconclusive. Cache remainsON, model/argv/RNG/input/FP32+metadata/dtype/concurrency/budgets/tolerance unchanged; no core score payload/runtime instrumentation/WAR/formal fallback change. TP0/slot/device/allTP/race/1024 limits, historical NFS/admission and old independent counters stay unchanged. Formal numerical acceptance/fresh admission/200/profile remain open, env1 DEFERRED/no A200 gate/auto-loop. [Current RCA](../progress.md#current-execution--workflow-rca).

- [ ] 冻结attempt identity、源代码、解析后的配置、输入和模型identity；按spec S8和D33在H800/codesign提交，无task GPU数量上限，正式cell非抢占。
- [ ] 输入使用 `loss_masked` turn source 和 01 审计生成的源文件 manifest；作业另挂载 posttrain 卷，原位读取源文件（spec S8）。
- [x] 第一个formal update检查（D16，不新增GPU smoke；完成并记录之后才进入 05 的资源准入）：先确认实际 successful native optimizer update / ACK，再检查 S3 token / 行数 / uid 一致性、采集 / teacher / 训练耗时及 profile 两个文件和复算值。将这份 runtime evidence 交给 02 GPU 验收；profile 辅助失败明确报告 unverified 并按 S7 停止其更新，healthy training 继续，不能单凭辅助 verdict 阻止 05。native 首次 update 未成功、native failure 或资源不足仍是 blocker。
- [ ] 约第 20 个 update 时汇报各阶段耗时的趋势（S8）；第一个 update 因吞吐失败时按 D19 处理。
- [ ] Native training 完成：200 个实际 successful optimizer update / ACK，训练侧 record 和 native counters 对应，按实际 bank membership 记录训练 turn 数；失败 attempt 不拼接。
- [ ] 完整 profile accepted：两个文件各 200 个成对一致的 update，observation 数等于实际训练 turn 数，每个 update 的 S3 一致性通过，离线重建与记录值一致。S7 出错时本项未通过，但不阻止 healthy training 完成；保留完整核验前缀、未验证起点和缺失范围，标 INCOMPLETE / UNVERIFIED，不补造 200 行。
- [ ] 每个已检查 update 的一致性 verdict 都已记录；没有 profile 的后续 update 明确列为未验证，不仅列出第一条错误。
- [ ] 记录 RJob 业务终态和资源使用；失败的 attempt 单独保留，不拼接到正式结果中。
