## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record B teacher-only cold pass/warm blocker and completed historical comparison; formal B not started, no new A200/profile dependency or checkbox change. |
| 2026-11-11 | Hold formal B under shared D40 workflow RCA/fix verification; preserve satisfied A-inspection and all final checkboxes without a new A200/profile gate. |
| 2026-11-11 | Apply D39 parallel H800 B preparation, removing superseded32-H200 gate; preserve completed D16/common-cycle and all final criteria. |
| 2026-11-10 | Record accepted actual A profileprefix2 without a new B gate; keep fresh-resource-only blocking and all criteria unchanged. |
| 2026-11-10 | Accept common first native cycle from corrected A; B remains blocked only by fresh18-H200 resources within32, without A200/profile-PASS gate, stop-A authority or checkbox change. |
| 2026-11-10 | Record implemented/reviewed correction and new A execution; B still waits for common native verification/fresh resources, not a new logical A200/profile-PASS gate. |
| 2026-11-10 | Record controlled D38 evidence and the common native correction in progress; retain B's completed A-inspection edge and remaining resource/runtime work. |
| 2026-11-10 | Accept A firstACK/inspection prerequisite; block B on the common native host-memory fault and fresh admission, not A200/profile PASS. |
| 2026-11-10 | Reflect actual A H200/Ray startup and joined CPU readiness while retaining B's real ACK/inspection/resource blockers and all final criteria. |
| 2026-11-10 | Align current B context with18-H200/cell and32-GPU admission: actual A ACK/inspection remain logical prerequisites, while allocation release is a separate resource requirement. |
| 2026-11-10 | Add D36 A-wait context to current status only; B still requires actual A first ACK/inspection and fresh resources, with no changed acceptance or extra approval gate. |
| 2026-11-10 | Record satisfied CPU/configuration prerequisites; B still waits for A's actual first ACK, completed inspection and fresh resources, not A completion or auxiliary PASS. |
| 2026-11-10 | Record02 CPU readiness and B TP4/EP1 feasibility limits;retain authorized concurrent admission after A first ACK/inspection,not A completion or new approval. |
| 2026-11-10 | Record merge55fba827 complete; preserve02/03 readiness,A first formal-update inspection and B native-runtime limitations. |
| 2026-11-10 | Apply D35 parent capacity adoption without certifying B runtime or removing merge/integration and A formal first-update dependencies. |
| 2026-11-09 | Accept the D34 input re-audit without changing integration, A/full inspection or resource-admission dependencies. |
| 2026-11-09 | Apply D33 H800 authorization and remove the superseded count limit;01 is accepted. |
| 2026-11-09 | Admit B after A's actual first successful update and completed inspection, not an auxiliary PASS; separate native completion from complete profile acceptance. |
| 2026-11-08 | Draft the B/full formal cell ticket. |
| 2026-11-08 | Apply the D17 GPU budget. |
| 2026-11-08 | Add the update-20 timing report and D19. |
| 2026-11-08 | Use the SWE-1003 0913 data read in place (D23–D25). |

# 05: B/full 正式 cell（Qwen3.5-4B + Qwen3.5-35B-A3B）

**What to build:** 与 04 相同的协议，teacher 换为 Qwen3.5-35B-A3B。

**Blocked by:** 01、02、03 已接受；04 的firstA ACK/inspection/common cycle已核验。D40历史对比/CPU/cold通过后，实际warm概率差异仍需本ticket与04共有的因果RCA/修正/H800复验，之后fresh H800 admission。无A200/profile/32-H200 gate，也不授权stop其他task。

**Status:** BLOCKED / MAMBA_WARM_STATE_RCA D40; formal B not started. Teacher-only[probe B](../test_report_2026-11-11_workflow_rca.md#completed-native-h800-experiment-and-new-correctness-blocker)`exp-1111-033134-236473`naturally Succeeded,4actual H800/56requests; cold14/14 exact but warm4/14/maxabs1.0602149963378906 and full-input warm cached0 drift. CPU135/two immutable reviews accept only scope/cold, not formal/throughput. Historical actual comparison completed with different196.956B/56H200/async1024-staleness5 versus currentold18physical/fresh256/incompletebank6: no apples-to-apples ratio. Shared causal warm-state/cache/tracking correction and H800 revalidation remain; no tolerated roundoff, tolerance relaxation or arbitrary cache-disable fix. [D16 A-inspection](../test_report_2026-11-10_d16_first_update.md)/common-cycle remain satisfied; no A200/profile/32-H200 gate. D39 original-init/fixedscience/S7/checklists/old independentnative6-profile2 remain; freshformal admission and own200/terminal/profile still required, no newdecision/oversampling/async redesign or later-update auto-loop. [Current RCA](../progress.md#current-execution--workflow-rca).

- [ ] 冻结attempt identity、源代码、解析后的配置、输入和模型identity；按spec S8和D33在H800/codesign提交，无task GPU数量上限，正式cell非抢占。
- [ ] 输入使用 `loss_masked` turn source 和 01 审计生成的源文件 manifest；作业另挂载 posttrain 卷，原位读取源文件（spec S8）。
- [x] 启动前核对 A 的实际 successful optimizer ACK 与已完成 inspection；A 的辅助 profile 失败须已报告并标 unverified，但不单独阻止 B。native first-update failure 和资源不足仍阻塞提交。
- [ ] B 第一个 actual successful update 做与 04 相同的检查，记录 S3 / bank identity / profile 内容和各阶段耗时的实际 verdict；辅助失败按 S7 隔离。
- [ ] 约第 20 个 update 时汇报各阶段耗时的趋势（S8）；第一个 update 因吞吐失败时按 D19 处理。
- [ ] Native training 完成：200 个实际 successful optimizer update / ACK，训练侧 record 和 native counters 对应，按实际 bank membership 记录训练 turn 数。
- [ ] 完整 profile accepted：两个文件各 200 个成对一致的 update，observation 数等于实际训练 turn 数，每个 update 的 S3 一致性通过，离线重建与记录值一致。S7 出错时本项未通过，healthy training 继续；完整核验前缀、未验证起点和缺失范围单列为 INCOMPLETE / UNVERIFIED，不补造记录。
- [ ] 每个已检查 update 的一致性 verdict 都已记录；profile 停止后的区间也明确列为未验证。
- [ ] 记录 RJob 业务终态和资源使用；失败的 attempt 单独保留。
