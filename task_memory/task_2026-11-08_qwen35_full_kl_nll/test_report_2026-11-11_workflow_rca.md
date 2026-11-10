## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Open the requested comparative workflow RCA; separate workload/resource differences from testable excess scoring work. |
| 2026-11-11 | Record the CPU-ready scope fix, two-axis review, actual eight-H800 probe allocation and recovered supervision without resubmission. |
| 2026-11-11 | Record the completed historical comparison and H800 cold/warm results; retain the formal hold after measured warm-state probability drift. |
| 2026-11-11 | Confirm hidden canonical KV reuse and an intermediate-checkpoint rounding path; defer the possibly redundant coarse-barrier experiment and prepare selected-FP32 snapshot wiring. |
| 2026-11-11 | Close the normal-eager WAR publisher source chain; both snapshot source reviews returned No findings and integrated CPU checks passed202. Native parity remains pending. |

# Comparative workflow RCA

## Request and acceptance scope

The user requested comparison with `/data/ycfeng/steptron/task_memory/task_2026-10-06_mopd_step_timeline`, followed by RCA and correction of confirmed workflow or parameter problems. Fresh formal A/B submission is paused for this work. Subsequent native diagnostics use H800/codesign only under D39.

Acceptance requires inspected historical and current configurations, a falsifiable reproduction of each proposed defect, a correction at its existing owner, CPU regression checks, and an H800 comparison using the same checkpoint and token inputs. A shorter step in another model/layout is not alone a defect reproduction. Native training objectives, masks, source ordering, candidate selection, weight-version semantics and time budgets stay unchanged.

## Evidence already available

- [Current bank6 native generation and teacher log window](evidence/h200-bank6-native-stage-timeline-20261111.json).
- [Current bank6 measured attribution](evidence/h200-bank6-stage-attribution-20261111.json).
- [Preceding H200 terminal and acquisition investigation](test_report_2026-11-11_h800_only.md).
- Historical Steptron `summary.md`, `methods.md`, `test_report_2026-10-08_nccl_timeline.md`, actual timeline experiment and retained measured configuration.

The current failure contains256 completed native generations by1150.890 seconds, but only225 completed teacher/validation outcomes before1800 seconds. The entire final649 seconds have no remaining student-generation attempts. The teacher logs continuously report prefill work from about194.674 to1799.674 seconds, with no gap larger than1 second between logged prefill rows at one-second timestamp resolution. This establishes the deadline-critical teacher return path for bank6, not a universal ranking of GPU stages.

Historical Steptron `tl-1007b` reports a 965.962-second median across ten complete outer steps, including cold step0. The median of steps1–9 is 955.973 seconds. It uses 48 H200 trainer/teacher GPUs and eight separate H200 rollout GPUs with a 1024-sample asynchronous buffer and permitted weight staleness of five steps. Its Step3p6 model has 196.956B total parameters, with five same-architecture teachers used in rotation. Active parameters and actual prefix-cache hit rates remain unverified.

The failed current Qwen3.5-4B → 27B attempt has **18 physical H200 GPUs**, not the sum of overlapping roles: eight trainer GPUs colocate with eight of the sixteen rollout GPUs, and the teacher uses two additional GPUs. It consumes a fresh 256-sample bank before training. Historical teacher scoring is a packed distributed forward on 48 GPUs, whereas the current teacher is a TP2 HTTP service configured for one active request. Historical steady steps routed 9121 trajectories totaling 293,269,982 tokens, including 60,118,201 response tokens, and the teacher processed 306,686,032 padded tokens. Current bank6 sent 24,457,747 input tokens including only 147,115 response tokens; 225 samples completed, and no complete training cycle followed that bank. These are not comparable complete-step speed measurements.

Decisive historical sources: `/data/ycfeng/steptron/task_memory/task_2026-10-06_mopd_step_timeline/figures/tl-1007b/timeline_summary.md:69–100,148,199,208–252,332–345,363–375`, `test_report_2026-10-08_nccl_timeline.md:98–115`, and `/data/ycfeng/tmp/mopd_timeline_audit/tl-1007b/log_0.txt:1206–1285,1372–1442,2408–2544,2731,2847`. The replacement read-only comparison completed after the first subagent failed with an API reasoning-text transport error; the failed subtask did not provide an accepted result.

## Ranked hypotheses and falsifiable checks

| Hypothesis | Inspected basis | Reproduction / falsification | Status |
| --- | --- | --- | --- |
| Whole-input teacher probability work exceeds the required target positions | `_score_payload` requested `logprob_start_len=0`; downstream SWE extraction consumes only the generated-response suffix. Current bank teacher inputs total24,457,747 tokens, versus147,115 response tokens. | Same checkpoint and token sequence, full-input versus response-only logprob start; compare every response token ID/probability, measured request/body/parse times and cached-token counters. | CPU fix `7d993848`; cold native parity PASS; warm parity not accepted |
| Current serving/layout differs materially from the historical distributed packed teacher pass | Historical teacher uses48 trainer GPUs; current failed service isTP2 on2 H200 and has one configured active request. | Normalize exact routed/scored token counts, active model work, GPU resources and timing boundaries from retained runs. Keep queue time separate from GPU execution. | Configuration/timing comparison complete; no same-workload speed ratio or isolated capacity counterfactual |
| Prefix reuse is suppressed by current scoring semantics | Bank6 logs21,561,962 new prefill tokens and0 cached tokens across2735 prefill rows. | A same-input cold comparison plus a same-prefix warm stream under the same native teacher configuration; verify cache response fields and native logs, not merely a configuration flag. | Actual response-only cache hits confirmed; measured warm-state numerical drift blocks acceptance |
| Client setup, serialization, transfer or JSON parsing explains much of the scoring latency | Current request latency includes these stages. Generation adapters start only after initial bank/setup work. | Instrument HTTP headers/body bytes, body read, JSON parsing and canonical validation in the bounded feedback probe. Compare against server-side work/queue evidence. | Native client read/parse timings recorded; bank setup and server serialization are not isolated |
| A few unfinished student services cause this bank's deadline failure | User-proposed alternative; substantial student duration exists and overlaps teacher scoring. | Pair all512 native generation boundaries to256 source IDs and teacher starts; check unfinished student count at the deadline. | NOT SUPPORTED for bank6; all256 generation attempts succeeded by1150.890 seconds |

The confirmed excess scoring range is corrected in `7d993848`. SWE supplies the response length to the existing shared payload owner, which requests `P-1`: one preceding placeholder plus all response probabilities. Complete token inputs remain available for conditioning. Existing full-input, top-k and per-position callers retain their default range; existing student-prefill scoring reuses the same construction and is not additionally enabled. No oversampling, stale-weight asynchronous buffering, acquisition-timeout extension, allocator factor or teacher-concurrency adjustment has been applied.

## CPU implementation and fixed-image source verification

- Scope report: [teacher scoring scope](test_report_2026-11-11_teacher_scoring_scope.md): 8 RED cases, 102 focused GREEN cases. Expanded results are351 PASS,12 CUDA skips and4 failures reproduced with the original production implementation; they are not an all-green claim.
- Immutable comparison: [review evidence](evidence/teacher-scoring-scope-review-20261111/comparison.json), `59d61941 -> 7d993848`. Standards and Spec reviewers independently returned **No findings**. Their review was read-only and did not execute the recorded tests.
- Probe implementation: `59d61941`, followed by `9537e825` to use the actual fixed shared owner and retain raw input-score count/first placeholder evidence. Its33 focused CPU checks passed.
- Primary joint command, Python3.12.13 / pytest9.1.1: `TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/test_teacher_scoring_probe.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/teacher-scoring-joint-pytest-20261111a` -> **135 PASS**,20 warnings,4.21s.
- Isolated submission command and H800-only allocation checks: `tests/fast/test_teacher_scoring_submission.py` -> **3 PASS**,2 warnings,0.20s. Exact command: `TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_submission.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/teacher-scoring-submission-pytest-20261111a`.
- Pinned-image source worker `exp-1111-030539-334581` succeeded and retained11 actual source files. Its native SGLang0.5.24.dev80+g056f871 `schedule_batch.py:1768-1787` limits prefix reuse by scoring start; `logits_processor.py:794-812` prunes prompt hidden states before the projection. These verify the mechanism, not numerical or performance parity. A prior worker exited0 but used the editable distribution's wrong source location and retained no actual files; it is not counted as source verification.

## Completed native H800 experiment and new correctness blocker

The fixed fixture contains seven retained bank6 samples. Only the first four form a consecutive same-conversation stream; the fifth belongs to another group. Full input counts range3970-116053; response counts range67-8124. Preserve that order, rather than treating all five long samples as one prefix chain.

`teacher_scoring_probe_config.json` defines two repetitions,56 scoring requests and32 cache flushes per pair. `submit_teacher_scoring_probe.py` allocates only one native teacher task, with the frozen TP4/CPU/memory/image settings, explicit local NFS annotation and existing locked inventory owner. It does not allocate trainers or rollout servers. Both actual CPU submission dry-runs passed; stdout/stderr are retained under `evidence/teacher-scoring-probe-20261111/`.

| Pair | Native job | Allocation / provenance | Current acceptance |
| --- | --- | --- | --- |
| A /27B | `exp-1111-033133-704472` |4 actual H800,81559 MiB each; native SGLang0.5.24.dev80+g056f871 | Succeeded; all56 requests retained; cold parity PASS, warm parity not accepted |
| B /35B-A3B | `exp-1111-033134-236473` |4 actual H800,81559 MiB each; same native SGLang version | Succeeded; all56 requests retained; cold parity PASS, warm parity not accepted |

The parent shell tools incorrectly imposed a120-second launcher deadline. This interrupted local supervision, not the native worker's3600-second bound or the formal1800-second acquisition criterion. Direct native reads proved A was Running and B Starting; neither was resubmitted or stopped. Existing jobs are now supervised read-only with an unlimited outer shell lifetime. The first observer import failed because Steptron's `tests` package was imported before Miles; correcting import order applies the already recorded environment constraint, rather than adding a new compatibility path.

Admission, explicit source mount, creator and actual-device evidence are in `evidence/teacher-scoring-probe-20261111/{admission-*-r1.json,launcher-timeout-observation-*-r1.json,native/*/admission-*-r1/preload.json}`. Both native jobs reached Succeeded under recovered read-only supervision; terminal receipts are `supervision-{A,B}-r1-terminal.json`. No job was resubmitted or stopped. The temporary supervision failure is not a teacher-performance verdict.

| Numerical check | A/27B | B/35B-A3B | Conclusion |
| --- | --- | --- | --- |
| Cold full-input versus response-only | 14/14 token-wise exact; maximum absolute/relative error0 | 14/14 token-wise exact; maximum absolute/relative error0 | Response range and first-token semantics pass in cold mode. |
| Warm full-input versus response-only | 4/14 exact; maximum absolute error0.2006068229675293 | 4/14 exact; maximum absolute error1.0602149963378906 | Warm numerical parity is not accepted. |
| Response IDs and finite scores | All matched and finite | All matched and finite | ID/finite checks alone do not establish probability correctness. |

Observed settings include `mamba_radix_cache_strategy=extra_buffer`, `mamba_track_interval=256`, chunked prefill8192, BF16, Triton, deterministic inference enabled, and CUDA graph disabled. Warm response requests hit90,112 tokens at sample1, with only small numerical differences; samples2/3 hit96,576 tokens and have large differences. Samples5/6 hit1024 tokens and also differ materially. Samples0/4 hit zero and are exact. Later source inspection shows that `mamba_track_interval` is decode-only: the prefill grid is a separate runtime mechanism. Changing that interval to8192 is not a supported causal proposal.

Importantly, warm **full-input** requests report zero cached tokens but also differ from cold full-input references at samples2/3: maximum A errors0.17278575897216797 and0.12412643432617188; maximum B errors0.43444275856018066 and0.4388699531555176. The investigation therefore includes intermediate Mamba checkpoint tracking or another warm-state effect, not only response-only reuse. The existing full-input path is not an independent numerical oracle in the warm stream.

Native aggregation is retained in [the R1 comparison summary](evidence/teacher-scoring-probe-20261111/native-comparison-summary-r1.json). All112 requests pass raw range checks: N entries for full-input or R+1 for response-only, the expected first token with a null placeholder, exactly R returned response scores, matching response IDs and finite values.

| Cold measurement over14 requests | A full → response-only | B full → response-only |
| --- | --- | --- |
| Sum of request elapsed seconds | 81.735035 →65.090545 | 48.671685 →32.354768 |
| Median request elapsed seconds | 5.291266 →4.554808 | 2.679382 →1.681279 |
| Returned JSON body bytes | 41,009,031 →782,853 | 41,068,473 →781,199 |
| Returned input probability positions | 1,254,918 →23,172 | 1,254,918 →23,172 |
| Client JSON parse seconds, total | 0.800727 →0.010754 | 0.843518 →0.013230 |

Model loading is excluded, but first-use kernel warmup is included in the first request. Both modes retain identical conditioning input totals of1,254,918 tokens. The measured returned-position reduction for these deliberately selected seven cases is98.1535%, not the99.397% prediction for the entire historical bank. Client body-read totals are below0.021 seconds and client parse is below0.844 seconds over14 full-input requests; these measurements use the teacher-node loopback interface and do not price cross-node transfer, bank setup or server JSON serialization. No uniform speedup, full-bank throughput correction, warm-cache acceptance, or formal readiness is claimed.

The follow-up0-GPU source job `exp-1111-035902-035439` copied37 source files before failing an erroneous collector assertion that a file named `mamba_radix_cache.py` must exist. This fork includes unified-cache Mamba components instead. That source-copy attempt is recorded as FAILED, not successful source verification. The subsequent source job `exp-1111-040603-422872` succeeded and retained38 files selected directly from the measured GPU manifest, including `unified_radix_cache.py`; **all38 source hashes matched the A GPU reference**. Supplemental0-GPU job `exp-1111-042450-358109` succeeded, retaining175 runtime/attention/GDN sources. The requested filename `srt/model_executor/runner.py` is absent and recorded as such; actual `model_runner.py` is already retained. Source and terminal records are under `evidence/native-sglang-cache-source-20261111/`.

### Hidden reuse, event coverage and a concrete precision candidate

Full-input initial prefix matching is capped at0, but unfinished chunk checkpointing may later rebind this request's KV rows to canonical rows already in the unified cache. The cached-token statistic subtracts this request's own computed prefix and does not measure this replacement. Consequently, `cached_tokens=0` does not make warm-full an independent cold oracle. This proves hidden reuse, not that a particular substituted KV is wrong or that an ordering race exists. Relevant matched code: `unified_radix_cache.py:1238,1284–1298`, `schedule_batch.py:1768–1787,2968–2998`, and `scheduler.py:3936–3944`.

The isolated [coarse-barrier configuration](teacher_scoring_war_barrier_probe_config.json) is CPU-ready and has not been submitted. It changes only `SGLANG_FORCE_COARSE_WAR_BARRIER=1` and the output namespace. However, GDN inherits the `UNKNOWN` EXTEND shared-read contract, which propagates through the hybrid backend. The scheduler already waits on the whole forward stream when no shared-read event exists. The actual event publication/branch was not recorded in R1; therefore a forced-coarse experiment may be redundant, and unchanged output would not directly rule out ordering. No missing event or race has been proved. The experiment is deferred rather than spending8 GPUs without a demonstrated changed control.

The most concrete new precision candidate is an extra rounding path: recurrence accumulates in FP32, but intermediate `h` is allocated with `k.new_empty` and stored in `k.dtype`; an interior checkpoint then casts that already-rounded `h` into the temporal pool dtype. Final state instead casts the native accumulator directly into the temporal dtype. Even an FP32 temporal pool cannot reverse a preceding BF16 cast. Relevant C3 paths: `kernels/ops/attention/fla/chunk_delta_h.py:102–108,171–186,331–348,397` and `srt/layers/attention/hybrid_linear_attn_backend.py:1041–1063`. The underlying kernel already supports directly writing selected FP32 snapshots, but the Triton capability/forwarding chain is not connected (`linear/kernels/kernel_backend.py:18–24`, `gdn_triton.py:169–215`). A candidate will connect that existing path, preserving normal `h`, output and final-state computations rather than changing every intermediate dtype, cache policy, interval or backend. Actual donor provenance, native snapshot fidelity and resulting probabilities still require H800 verification; this path alone does not yet explain warm-full drift.

The native prefill checkpoint grid is `lcm(mamba_cache_chunk_size(), tree_page)`; Triton GDN's kernel chunk is64 and the backend reads the HF chunk setting with default64. Runtime-resolved cache/state/grid values and tensor dtypes must be recorded before being treated as measurements. Source inspection found no specific temporal/conv off-by-one at the examined boundary selections. No checkpoint interval, global dtype or numerical tolerance is changed.

Primary joined CPU verification, Python3.12.13/pytest9.1.1: **145 PASS in5.06 seconds**,20 existing SWIG/JIT/CPU quantization/datetime warnings. Exact command:

```bash
TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_prefill_logprobs.py tests/fast/rollout/test_on_policy_distillation.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_teacher_scoring_submission.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/teacher-scoring-war-joined-primary-20261111
```

These checks establish payload and diagnostic environment/receipt contracts, not deployed flag application or repaired native scoring. The existing global document checker has2 unresolved relative links inside the frozen candidate snapshot, not maintained task documents; neither snapshot nor checker was modified to hide that limitation. Formal04/05 remain paused. Numerical acceptance must use each case's retained cold reference, not a contaminated warm-full result.

### Source candidate review and native experiment readiness

Candidate `d7e7e301` passed independent Standards and Spec source reviews on the fixed `ab3f47d5 → d7e7e301` artifacts: both **No findings**. The reviewers inspected three repository files, the six qualified native seams and the generated two-file28-line patch. Their conclusions accept only the source phase, not deployed identity, CUDA compilation/stores, donor fidelity, performance, historical causality or formal readiness. Review artifacts: `evidence/selected-fp32-review-20261111/`.

Native0GPU source jobs `exp-1111-045750-493777` and `exp-1111-052149-761200` succeeded and retained25 runner/worker and9 runner-utils files respectively. The actual publisher body closes the static WAR chain: `runner_utils/shared_read_event.py:29–30` returns for every contract other than `PRE_REPLAY`, so `UNKNOWN` publishes no event. With initial None mailbox, per-round consumption/clear and no other publisher on the normal eager path, baseline already selects whole-forward `wait_stream`. The coarse variant is redundant on that path and remains unsubmitted. R1's actual runner/contract/mailbox branch was not recorded, so this source conclusion is not retrospective runtime proof and does not exclude other races.

The existing probe now records all four warm-to-independent-cold comparisons with matching pair/repetition/UID/index. The controller passes the isolated selected-FP32 input into the worker; both actual controller dry-runs passed. Primary joined CPU verification is **202 PASS in7.26s**. Exact commands and limits are in `test_report_2026-11-11_fp32_probe_integration.md`. All56 requests and32 flushes per pair, model/BF16/cache/concurrency/chunk settings and scientific parameters are unchanged. The next decisive evidence is actual H800 source preparation and same-input native warm probabilities; no fixed-run numerical or performance PASS is claimed.

## Feedback loop and verification limits

The historical failing native scenario is the current RED evidence:225 valid outcomes versus231 required, despite256 completed generations. CPU tests can verify payload and trimming semantics but cannot price GPU prefill, KV reuse or service capacity. The planned bounded H800 probe uses retained generated-token fixtures and the formal teacher command; model loading is outside the steady-state request timing. Full-input and proposed response-only requests are measured on one loaded engine, with explicit cache-reset and warm-stream methods.

Native probability differences, if any, are recorded explicitly. A passing CPU mock, an API response, a cache flag, or a model-load exit is not accepted as a throughput correction. A proposed fix must show the required unchanged response probabilities and reduced actual excess work before formal execution resumes.

## 1. 规划完成情况

**汇总：** PASS3｜BLOCKED2｜TODO1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 01 输入与审计 | PASS | D34 原始输入审计已接受。 |
| 02 逐 turn 测量 | PASS | D16 原生首更新验收已接受。 |
| 03 Profile | PASS | CPU 集成及既有边界验收已接受。 |
| 04 A/full | BLOCKED | 旧作业6/200失败；新提交等待用户要求的 RCA 修复及 H800 验证。 |
| 05 B/full | BLOCKED | 同一 workflow 修复尚未验证；不增加 A200/profile gate。 |
| 06 最终报告 | TODO | CPU 计算已接受，A/B最终数据未完成。 |

## 2. 偏离检测

**结论：** 已偏离：命中 D2；原生对照已完成，但 warm-state 数值检查发现新的真实阻塞。
**检测窗口：** D40 RCA 开始至历史对齐及 A/B 各56个原生评分完成｜**当前前沿：** Mamba checkpoint/cache 数值差异 RCA及修正；通过后恢复04/05。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 固定样本、专用 teacher 提交及原生测量直接验证D40阻塞；共享 payload 修复已提交。验证后不再扩展 harness。 |
| D2 细节反复重试 | HIT | SDK参数猜测、缺少NFS准备、editable源码路径，以及120秒外层超时和已知import顺序未复用，反复打断原生验证；不是事先记录的模型假设测试。 |
| D3 支线问题修补 | CLEAR | 对照 RCA 和修复由用户明确要求，属于04/05阻塞。 |
| D4 可并行任务停滞 | CLEAR | 两项H800原生测试和替代历史对照均已完成；新的缓存代码RCA和数值聚合可并行。 |
| D5 超范围镀金 | CLEAR | 未引入356候选、额外student评分、超时延长或异步旧权重缓存。 |
| D6 分析空转 | CLEAR | 已确认多余全prompt评分范围，生产修复和原生验证均有明确执行切片。 |
| D7 路线违背 | CLEAR | 无新H200执行；0-GPU源码作业在codesign；formal保持暂停。 |

**文档检查：** S1-S6无新增范围或依赖缺陷；`15982f81`已记录D40归属及formal暂停。CPU-ready、实际H800分配及未完成的native验收需继续同步当前进度；不是新增验收门槛。
**归因：** D2执行偏离；已有runbook、native提交路径及import顺序约束未及时应用。模型workflow缺陷与辅助launcher失败须分开归档。

## 3. 纠正建议

**分支：** A：D40范围及依赖已合理记录，无需更改spec/tickets的科学参数或门槛。

**需停止的偏离行为：**
- D2：停止按新错误逐次猜参数或无条件重提；复用SDK原生API、已验证NFS入口、Miles优先import及无外层超时的监督。两个健康远端作业直接继续，不重复加载模型。

**接下去的路线：**
1. 并行：原生 Mamba tracking/cache 代码 RCA ‖ 完整数值、返回范围和耗时聚合；保留原始 full-input 与 response-only 各自的 cold reference。
2. 依据确认的原因选择最小修正或可证伪的参数实验；不以放宽误差、忽略 warm failure 或任意禁用缓存替代修复。
3. 修正验证通过后恢复04/05独立formal，仍须实际231/1800s及200-update验收。

## 4. 最值得关注的 3 点

1. 多余评分范围的 cold 原生语义已通过；warm下两种范围均出现状态相关概率差异，formal继续暂停。
2. 辅助launcher失误没有造成GPU重提；两项8卡合计原生实验均已自然Succeeded，不能因退出成功而忽略数值失败。
3. 历史steady median955.973秒已查实，但56H200、异步1024样本及197B模型与当前协议不同，不能据此给同配置加速比。
