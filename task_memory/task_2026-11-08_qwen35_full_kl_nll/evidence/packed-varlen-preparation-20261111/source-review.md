## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record the fixed R2 two-axis source review, primary CPU acceptance and phase checkpoint. |
| 2026-11-11 | Clarify the configured memory unit after initial API inspection: mem_gb64 produces64000Mi, not65536Mi. |

# Packed-varlen source acceptance

**PRIMARY ACCEPTED: CPU/source preparation only. Packed native values remain UNVERIFIED.**

Fixed point: `ec532bc226159dfddb67902bcd299237d96a4300`. The immutable five-file WIP artifact is `/data/ycfeng/tmp/opencode-v2-tmp/opencode/packed-varlen-source-review-20261111-r2/`; `manifest.json` and `changes.patch` bind all five candidates. The only intervening commit at review was the separate `54a94b20` design archive, not a probe implementation commit.

## Standards

Reviewer: `ses_e351698b0ffesI2orfR9z3PhXI`, TaskID `profile-packed-varlen-source-standards-review-20261111`.

**No findings:** zero actionable documented-standard violations and zero actionable baseline smells. All five candidates, the complete diff, original probe and frozen rules/spec references were inspected. The R2 CPU fixtures relocate only cloned formal filesystem fields; production guards and configs remain unchanged. CUDA/H800 behavior stays in the isolated manual probe. Supplied tests/checksums were not rerun by this reviewer; actual GitHub CI and native semantics were not accepted.

## Spec

Reviewer: `ses_e3516239bffeBOG44QH7ZJaXJa`, TaskID `profile-packed-varlen-source-spec-review-20261111`.

**No findings:** no missing, incorrect or unrequested requirement was identified across the five candidates. The existing dispatcher receives non-null CUDA int32 `[0,T]`, nonzero indexed FP32 state, cloned initial pools and shared maximum-length input buffers. The own7232 golden and configured common6519 comparisons remain distinct. No equal-length substitute, new flag, serving policy or explicit producer synchronization was introduced. Native index preparation's existing host read is documented. Synthetic results cannot establish natural-request state equality or warm causality.

**Axis summary:** Standards0, worst issue none; Spec0, worst issue none. The axes are not merged or ranked.

## Primary verification

- [R2 checksum](primary-checksum-verification-r2.json): five frozen SHA256s, Python/JSON syntax, six unchanged native before/candidate identities; production probe and A/B configs unchanged by the fixture correction.
- [Raw primary unit log](primary-r2-unit.log): `/usr/bin/python3`3.10.6, `timeout 60s`, `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`, `-B -m unittest tests.fast.test_mamba_fp32_snapshot_probe -v`; **7/7 PASS,0 SKIP,0.249s**. This is CPU/mock/source binding only. The closed32 suite was not rerun.
- [Preparation record](preparation.json) retains the earlier32 checks, fixture RED/GREEN, source-only bindings and unchanged original44 receipt. [A](controller-dryrun-A.json)/[B](controller-dryrun-B.json) controller dry-runs are `submitted=false`, each H800/codesign/GPU1/CPU8/`mem_gb=64` with the existing3600s+90s budget. The subsequent initial API reports memory64000Mi, not65536Mi. No native run had occurred at the CPU checkpoint; subsequent admissions are recorded separately.
- CPU archive acceptance adds no claim about real model inputs/state, canonical-P publication, native replay fidelity, warm correctness, a causal fix or formal200.

## 1. 规划完成情况

**汇总：** PASS3｜BLOCKED2｜TODO1。01输入、02 per-turn、03 profile 已记录完成；04/05仍被 causal root、warm correctness 和各自 fresh200 阻塞；06仍等待两组真实最终结果。当前新增完成项仅为 packed CPU/source；实际值 producer/consumer 联调尚未完成。

## 2. 偏离检测

**结论：** 未偏移，正常推进。窗口为此前 recurrent-design checkpoint 至本次 CPU/source acceptance；前沿为 packed native A‖B 与独立实际值联调。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅修复阻塞 implicit CPU CI 的 fixture；7项通过后停止，未泛化。 |
| D2 细节反复重试 | CLEAR | 一次有明确 mount/tempfile 原因的修正；未重复 native/GPU 试错。 |
| D3 支线问题修补 | CLEAR | 五件候选和一次 proportional7检查服务04/05的既有 D40。 |
| D4 可并行任务停滞 | CLEAR | 实际值两端独立推进；两个 packed configs 可并行，不新增 A200 依赖。 |
| D5 超范围镀金 | CLEAR | 仅现有 probe 的生产 packed 路径；无 serving flag、cache policy 或 raw archive。 |
| D6 分析空转 | CLEAR | CPU/source 已完成；旧 r3 数据确认四候选均有既有 layer0/P metadata，不新增 logger。 |
| D7 路线违背 | CLEAR | 不以 equal-length 替代 packed，不以 own7232 作为1695 donor，不宣称 causal/warm PASS。 |

**文档检查：** S1–S4/S6 CLEAR。S5 HIT：已提交的 `requirements.md:3`、`plan.md:3,163`、04票`:3,79`、05票`:3,76`仍为旧 two-design/no-code 状态。既有八文档 owner 正在 routine sync；原 scope、criteria、53 checkbox、science 不变。归因：无执行 HIT。

## 3. 纠正建议

**分支B：** 既有八文档 owner 直接同步当前阶段标签，无需新决策或审批。该文档更新不阻塞独立实施；接收此次 source acceptance/commit 后记录实际 native admission，不把 dry-run 或 code review 当 native PASS。

**需停止的偏离行为：无。** 路线为 source archive→既有1H800 A‖B native→scoped operator结果；并行实际值两端真实联调→native实值→causal discrimination/minimal fix→原 unsalted warm green→fresh A‖B各200→06。

## 4. 最值得关注的 3 点

1. Production packed 数值未执行；CPU7、历史32/44和两轴 review 都不能替代 native。
2. 6519是真共同范围；own7232多出的713行不能作为1695 donor。
3. Cause UNRESOLVED、warm1/4 FAIL、formal04/05 HOLD、06各自200及 B不等 A200 均不变。
