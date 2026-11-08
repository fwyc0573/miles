## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Remove the observer's redundant swe_attempt dependency; reproduce RED at the real CLI/typed/native-caller boundary and verify GREEN plus all36 CPU checks. Dependency patch and native GPU acceptance remain unchanged. |
| 2026-11-08 | Analyze historical GPU red/green receipts: red reproduces OOM; green completes31 scoring microbatches per rank and begins backward before external stop; observer installation fails, leaving GPU lifetime/peaks unverified. Apply D11 provenance boundary. |
| 2026-11-08 | Record the approved two-indentation dependency patch, final34-check CPU verification, source preflight, soft-only observer checks, and scoped progress checkpoint. |

# T02-CAPACITY-FIX: Megatron scoring output lifetime

## Result and scope

**CPU verification PASS; historical GPU contrast is partial, not full capacity PASS.** Red reproduces the30.31GiB projection OOM. Green completes initial fresh scoring and starts native backward, then is externally stopped before any retained optimizer ACK/train_data. The historical GPU observer failed at installation; the typed-scope repair below now passes CPU verification, but supplies no retrospective GPU weakref or allocator-peak evidence. D11 replaces training inputs with eight DeepSWE sources: these captured GLM-5.2-bank runs are historical engineering evidence only.

The source change consists only of moving the two existing `del output_tensor` statements outside `not forward_only` in the pinned PP1 schedule. No logits/probability math, allocator behavior, collective, topology, context budget, bank budget, TIS rule, or current-student rescoring is changed. This owner performed only local-file analysis for the GPU follow-up and made no producer/core edits, GPU, platform, cloud, SSH, or authentication operation, or commit.

The authoritative dependency/source/diff identities are in `tests/manual/agent_opd/megatron_scoring_lifetime.json`; the exact diff is `tests/manual/agent_opd/megatron_scoring_lifetime.patch`. The qualified retained source used for CPU checks is `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937/core/pipeline_parallel/schedules.py`. It was read only. Temporary fixture checkouts, not an installed Megatron environment, were patched by the tests.

## Interface and retained evidence

`training.release_scoring_output` is an optional JSON boolean. Omission leaves the existing launcher unchanged. Explicit `false` verifies the original pinned source without changing it; explicit `true` applies the verified patch or accepts its exact already-patched state. Both explicit contrast modes enable the same soft-only before-log-prob observer. A red run refuses an already-patched checkout rather than restoring or discarding any source changes.

The student `_prepare_training` preflight precedes Ray startup and native-driver submission. It validates the configured qualified image, full dependency commit, installed distribution version, original Git-HEAD source hash, current source hash, and diff hash. Actual container-image/platform identity still requires the parent's worker receipts.

At `<student-run>/megatron_scoring_lifetime/source/`, it retains `schedules.before.py`, `schedules.after.py`, the exact `.patch` and `.json`, and append-only `preflight.jsonl`. The launch receipt includes the same preflight result. The observer independently records each actor's schedule path/hash and expected hash under `<student-run>/megatron_scoring_lifetime/observations/rank_<rank>.jsonl`.

Observer events include scoring-pass/forward-microbatch indices, a weak-reference alive verdict, prior/full output storage bytes and pointer, and allocated/active/reserved/inactive-split allocator bytes. It uses ordinary module hooks at forward entry, vocabulary-projection entry, and forward exit. It never retains a tensor, synchronizes, or returns a replacement output. Gradient-enabled training is not observed. Installation, memory, source-identity, and receipt failures are reported as unverified and never escape into training; partially registered hooks are removed on installation failure.

## Commands and observations

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python **3.12.13**, PyTorch **2.11.0+cu130**, pytest **9.1.1**. CUDA was not used.

```bash
MILES_PINNED_MEGATRON_SCHEDULE=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937/core/pipeline_parallel/schedules.py \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_megatron_scoring_lifetime.py tests/fast/test_swe_launcher.py \
  -q -p no:cacheprovider \
  --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/scoring-lifetime-tests-verified \
  --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/megatron_scoring_lifetime_cpu.xml
```

Final observed **34 PASS**, **0 FAIL**, **0 skipped**, pytest duration **0.87 s**. The retained JUnit artifact is `evidence/megatron_scoring_lifetime_cpu.xml`. The actual pinned AST functions `forward_backward_no_pipelining`, `forward_step`, `forward_step_calc_loss`, and `backward_step` execute on CPU. SDK metadata/groups, the unused CUDA token counter, and unused MTP import are mocked; no schedule implementation is copied. The callback uses a CPU log-softmax reference, not the CUDA fused scorer.

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Forward-only old-output lifetime | Red retains one prior output; green retains none | Red `[0,1,1]`, green `[0,0,0]`; both final alive count0 | PASS |
| Callback ordering | Same three native microbatch indices | `[0,1,2]` in both | PASS |
| Callback outputs | Exact equality | `rtol=0, atol=0` passes for all output tensors | PASS |
| Native backward control | Same gradients, no lifetime regression | Exact gradient/output equality; live counts `[0,0,0]` in both | PASS |
| Preflight | Exact source, identity and diff; idempotent green; no destructive red reset | All identity/drift/idempotency tests pass | PASS |
| Observer | Weak references only; transparent forward/backward; failures isolated | Memory/write/source/registration fault checks pass | PASS |
| Launcher | Default unchanged; red/green add only observational arguments | Exact original argv preserved after removing three observer arguments | PASS |

Initial 28-check iteration also passed. The Python environment lacked `ruff` and `black` modules; no packages were installed. Existing lint tools at `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages` were used instead:

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check \
  tests/manual/agent_opd/megatron_scoring_lifetime.py \
  tests/manual/agent_opd/megatron_scoring_lifetime_observer.py \
  tests/manual/agent_opd/run_swe_opd.py tests/fast/test_megatron_scoring_lifetime.py

PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check \
  tests/manual/agent_opd/megatron_scoring_lifetime.py \
  tests/manual/agent_opd/megatron_scoring_lifetime_observer.py \
  tests/fast/test_megatron_scoring_lifetime.py
```

The first Ruff check found one unused test import, subsequently removed; the final check passed. Black's final check passed for all three new Python files; formatting changes were applied only to new owned files, and existing dense launcher formatting was preserved. `git diff --check` passed. A final independent source read still matched the manifest's original hash, confirming that the retained pinned schedule was not modified.

## Typed observer scope repair (current follow-up)

**Minimal production fix:** delete only `"attempt": self.args.swe_attempt` from `tests/manual/agent_opd/megatron_scoring_lifetime_observer.py`. The observer already writes beneath the student-run-specific `scoring_lifetime_dir`; filename rank, scoring-pass index, store prefix and microbatch index preserve its existing identity context. `swe_attempt` remains owned by the SWE replay/teacher/optimizer configuration, not the scoring hook. No extra config field, CLI flag, missing-field fallback, forward, collective or reducer is added. The two-field `ScoringLifetimeConfig`, source guards, exact dependency diff and launcher are unchanged. Default operation remains unchanged.

The affected tests no longer inject `swe_attempt` into observer fixtures. The new `test_combined_cli_typed_before_log_prob_installs_without_swe_attempt[False/True]` executes generated combined Miles CLI registration/resolution, validated `AllConfig`, real `compute_trainer_config`, `TrainerConfig` JSON transport, and `compute_custom_function_config`. Teacher/optimizer hook configs still contain `swe_attempt`, while the actual immutable before-log-prob view deliberately does not. The test executes the repository's real `forward_only` AST with its decorator and its real hook loader/composition/call block; only unused dumper/SDK services are substituted and its GPU microbatch loop is empty. A CPU model then verifies installed module hooks and weak references. The schedule file/hash and CUDA allocator counters in this typed-boundary test are fixtures; the separate retained-pinned-source tests verify the actual dependency patch. This is not the full CUDA Megatron parser, fused scorer, distributed execution or GPU numerical verification.

### Exact RED/GREEN discriminator

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_megatron_scoring_lifetime.py \
  -k combined_cli_typed_before_log_prob -q -p no:cacheprovider \
  --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/scoring-observer-typed-red
```

Before the one-line producer fix: **2 FAIL**,18 deselected,2.84s. Both modes emit the exact original symptom, `MEGATRON_SCORING_LIFETIME_UNVERIFIED install AttributeError 'ImmutableNamespace' object has no attribute 'swe_attempt'`, and leave no `rank_0.jsonl`; the test fails on that missing observation file. The hook failure remains soft and the native caller returns normally.

After the fix, the same invocation with `--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/scoring-observer-typed-green` gives **2 PASS**,18 deselected,2.61s. The discriminator is successful installation and exactly `[source_identity, forward_enter, projection_enter, forward_exit]` with verified fixture source identity, no `observer_unverified`, no redundant `attempt` record field, and three installed hook handles. The typed view still lacks `swe_attempt`. Deleting the CPU output makes both its weak reference and the observer's weak reference dead immediately.

### Full affected verification

```bash
MILES_PINNED_MEGATRON_SCHEDULE=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-pinned-normalization-exp-1107-235600-946937/core/pipeline_parallel/schedules.py \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_megatron_scoring_lifetime.py tests/fast/test_swe_launcher.py \
  -q -p no:cacheprovider \
  --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/scoring-observer-typed-full-20261108 \
  --junitxml=/data/ycfeng/tmp/opencode-v2-tmp/opencode/scoring-observer-typed-full-20261108.xml
```

Observed **36 PASS**,0 FAIL,0 skipped,3.30s in the Python3.12.13/PyTorch2.11.0+cu130 CPU environment above. This includes the exact pinned schedule lifecycle/callback/backward contrast, identity/drift/idempotency guards, memory/write/source/registration soft-failure checks, output non-retention, default skip and exact launcher argv checks. Existing CPU-only SDK/deprecation warnings remain, including unavailable vLLM CUDA extension warnings in the focused RED run; they are not observer failures or GPU validation.

Ruff and Black checks pass on the two affected Python files using the previously recorded tool paths. `git diff --exit-code -- tests/manual/agent_opd/megatron_scoring_lifetime.py tests/manual/agent_opd/megatron_scoring_lifetime.json tests/manual/agent_opd/megatron_scoring_lifetime.patch tests/manual/agent_opd/run_swe_opd.py` returns0 with no diff, proving this follow-up leaves dependency/source guards, exact patch and launcher unchanged. `git diff --check -- tests/manual/agent_opd/megatron_scoring_lifetime_observer.py tests/fast/test_megatron_scoring_lifetime.py task_memory/task_2026-11-08_qwen35_swe_full_r256/test_report_2026-11-08_megatron_scoring_lifetime.md` passes.

Only the observer, its affected test file and this existing report are changed; JUnit/fixture artifacts are confined to the approved local temporary directory. No main config, input, other-agent producer/core, platform, GPU, cloud, SSH or authentication operation, or commit was performed. The historical empty GPU observation directories remain empty historical evidence. A new accepted-DeepSWE native run must still supply eight independently recorded actor source hashes, actual microbatch/lifetime/allocator observations, numerical checks and completed optimizer/next-scoring evidence before native capacity PASS.

Scoped progress self-check: the diagnosed typed-boundary repair and CPU red/green deliverable are complete. D1–D7 show no execution drift; stop tooling work after this verification. The report distinguishes current repaired code from the historical failed observer; no shared requirements, plan, source ownership or acceptance criterion is changed. The remaining native gate belongs to the parent after D11 input acceptance.

## Remaining native gate

Parent packaging check: staged whitespace validation flagged two blank context lines in the patch asset. Their context-space markers were removed (Git accepts empty context lines), and the patch artifact SHA was updated; original/patched schedule hashes and the two source edits are unchanged. The same34 tests passed again using `--basetemp=/data/ycfeng/tmp/scoring-lifetime-packaged-20261108`; JUnit is `evidence/megatron-scoring-lifetime-packaged.xml`, with raw output `/data/ycfeng/tmp/scoring-lifetime-packaged-20261108.log`. Both actual red/green configuration files also passed combined custom-hook CLI registration with replay+observer enabled; `evidence/capacity-replay-combined-registration.json` retains the complete argv and confirms that the only configuration difference is `training.release_scoring_output`.

The parent owns input acceptance and resource operations. After D11, future native capacity qualification must use the accepted replacement inputs; do not resubmit the old GLM bank. Source/lifetime observations, numerical checks, optimizer ACK and subsequent scoring remain necessary unverified gates. The historical results below do not qualify the DeepSWE sources, B/full, a two-update capacity run, or formal200-update execution.

## Historical GPU contrast: local receipt analysis

Read-only source: `/data/ycfeng/tmp/qwen35-swe-capacity-replay-evidence/`, red `exp-1108-202530-030326`, green `exp-1108-202530-681419`. Compact extracted evidence is [`evidence/capacity-lifetime-gpu-partial.json`](evidence/capacity-lifetime-gpu-partial.json). Both logs identify256 actual samples and the same original bank, with TP2/DP4/CP1,131072-token GPU budget and `num_microbatches=[31]` (red log2735–2737; green2759–2760). Source archive SHA verification and a Python `difflib.unified_diff` comparison confirm the following:

| Evidence | Red | Green |
| --- | --- | --- |
| Shared source preflight | Original source before/after; `patch_applied=false` | Original→patched source; `patch_applied=true`, exactly two dedents |
| Actor repository reports | Pinned clean commit | Same commit, `dirty-ea9262ed334b` |
| Individual actor file SHA receipts | 0/8 | 0/8 |
| Observer JSONL files/events | 0/0 | 0/0 |
| Fresh scoring | Fails at vocabulary projection; completed count/index unknown | All31 scheduled microbatches per rank complete; indices0–30 |
| Native backward | Not reached in retained evidence | Begins; completed backward count unknown |
| Retained completed optimizer ACK/train_data | 0/0 | 0/0 |

**Source scope.** Both `source/preflight.jsonl:1` records match the exact archived files and packaged patch. Original schedule SHA is `968b3c2ab8e80b5d30992bb572bae8aa7cbc6b2fba7137d851bb71ee51bf489f`; green SHA is `8b0370c0d50a2463781ae3c622e30f923d096485aed3c0f8939be4cc13689081`. Actor env reports show the expected source state across a population represented by one explicit record plus seven Ray-deduplicated records (red2068/2079; green2074/2080, repeated2862/2868). Explicit repository rank IDs are red2/5 and green4/5. This supports consistent population-wide shared-source state, but does **not** supply eight independently recorded schedule hashes. The reported GPU runtime is Python3.12.16/PyTorch2.14.1+cu130, distinct from the prior CPU fixture environment.

**Unexpected observer failure.** Both extracted `observations/` directories are empty; the tar inventory also contains no observation files. Red2771/2779 and green2793/2803 report `MEGATRON_SCORING_LIFETIME_UNVERIFIED install AttributeError 'ImmutableNamespace' object has no attribute 'swe_attempt'`, representing all eight actors via Ray deduplication. The captured observer version declares only two fields (`megatron_scoring_lifetime_observer.py:21–23`), but its `write()` unconditionally reads `args.swe_attempt` at43. Native custom-view composition merges root/backend fields and the selected hook's config, not unrelated hook configs (`custom_view.py:17–34`). Its initial `source_identity` write occurs before registering hooks (`observer.py:126–141`); it fails, and the soft-only handler allows training to continue. Consequently no GPU prior-output weakref, storage bytes, microbatch events, active bytes or inactive-split bytes were measured. The original CPU fixtures supplied this field directly and did not establish that native typed-view boundary. No fix was made during the read-only analysis; the later authorized typed-scope repair is recorded above and does not change these historical GPU receipts.

**Red failure snapshot, not peak.** Red2947–2955 reproduces `torch.matmul(total_input, weight.t())` OOM on GPU2: requested30.31GiB, total139.81GiB, free29.59GiB, process108.52GiB, PyTorch allocated45.73GiB, reserved-but-unallocated61.35GiB, and colocated process1.67GiB. Derived reserved is approximately107.08GiB, subject to the log's rounding. This is not an active/inactive-split measurement or a whole-run peak. The actual failing microbatch index and how many red microbatches finished cannot be reconstructed from these receipts. High reserved memory alone does not prove fragmentation.

**Green completed fresh scoring and began backward.** Green2873/2875/2887 contain eight successful `_compute_log_prob` completions represented as one explicit record plus Ray groups of two and five. Global log-gather succeeds and logs fresh current scores (2878–2889); the `log_probs` timer is163.4s. Since all DP shards receive the same31-microbatch schedule (`train_data_conversion.py:438–456`), successful return proves31 scheduled scoring microbatches per rank, or248 rank-forwards/124 DP microbatches excluding TP duplication. These are schedule-and-return-derived counts, not direct per-microbatch weakref observations. `actor_train` starts at12:38:23.200Z (2880); actual `Variable._execution_engine.run_backward` stream warnings at2944–2952 prove native backward was entered, beyond merely compiling backward kernels. Compiler buffer-init/stream warnings are retained evidence, not proven fatal failures or validated numerical correctness.

**External stop and limits.** `/data/ycfeng/tmp/rca-capacity-replay-exp-1108-202530-681419/objects.json:15–36` attributes the stop to `alimasiyilixiati`, reason `release_quota`, timestamp12:44:32Z; the job finishes12:44:51Z with both roles stopped. The retained green business log has no OOM, but no completed optimizer ACK, train_data, backward-completion or second-scoring evidence either. It cannot prove eventual training completion or whether progress continued throughout the interval before the stop. No green scoring/backward memory peak or red/green peak reduction is measured. Saved rollout metrics are not a substitute for independent completion-token/TIS/loss/gradient verification. The patch contrast is consistent with a useful source fix, but the actual GPU lifetime mechanism and complete scientific/capacity acceptance remain unverified.

Local analysis used Python3 standard-library file reads, SHA256 checks, JSON parsing and in-memory diffing, plus `tar -tf /data/ycfeng/tmp/qwen35-swe-capacity-replay-evidence/evidence.tar`. No GPU work or new harness was executed. Only this existing report and the permitted compact evidence JSON were updated.

Final local validation: `python3 -` with a one-off standard-library stdin check loaded the compact JSON and original local receipts, asserted both preflight/source/diff hashes, both empty observation directories, the common31-microbatch schedule, observer failures, red OOM, green eight successful scoring returns/backward entry, and the exact manual-stop fields. Result: `PARTIAL_EVIDENCE_VALIDATION PASS; Python 3.10.6`. Whitespace validation `git diff --check -- task_memory/task_2026-11-08_qwen35_swe_full_r256/test_report_2026-11-08_megatron_scoring_lifetime.md` passed. No producer, legacy probe or GPU test was executed.

Scoped progress self-check: the requested read-only source/observer/lifecycle analysis and permitted evidence extraction are complete; full native acceptance remains unverified. No execution drift was found. The prior report's pending-old-bank wording was stale after D11 and is superseded above; the original checkpoint below remains explicitly historical. Next work belongs to the parent's reopened input acceptance and independent native qualification, not an old-bank resubmission or an unauthorized observer edit.

## Historical implementation checkpoint (before D11)

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 0｜TODO 1

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| T02批准的两处输出引用释放 | PASS | 精确patch/hash及CPU生命周期对照 |
| 学生preflight与soft-only观测 | PASS | 身份、幂等、故障隔离及argv检查 |
| CPU验证与复现记录 | PASS | 34项通过，JUnit及本报告 |
| 同一实际256-bank GPU对照 | TODO | 父会话与独立replay owner继续；不属于本owner的资源权限 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** T02-CAPACITY-FIX明确授权至今｜**当前前沿：** 实际bank replay接入与native GPU red/green

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 仅满足明确要求的CPU/soft-observer验证；现在停止扩展 |
| D2 细节反复重试 | CLEAR | 运行检查无失败；单次unused import修正，不是容量重试 |
| D3 支线问题修补 | CLEAR | 未触及旧probe、replay、gradient或allocator |
| D4 可并行任务停滞 | CLEAR | replay与GPU由独立owner承接，未建立新串行依赖 |
| D5 超范围镀金 | CLEAR | patch只有两处缩进，观测与archive由本次请求明确要求 |
| D6 分析空转 | CLEAR | 已交付可接入源码及实测CPU对照 |
| D7 路线违背 | CLEAR | 遵循requirements第80–82行；未选择TP4或改变科学配置 |

**文档检查：** 对本次切片检查S1–S6，未发现明显缺陷；Ticket02原生容量仍未勾选，与现有证据一致。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets合理，无需改动。
**需停止的偏离行为：** 无。

**接下去的路线：**
1. 父会话接入独立replay模块并执行获批GPU对照 → 完成标志：同一256-bank真实容量、数值、optimizer ACK及下一次scoring证据。
2. 本owner停止继续扩展工具；保留最小patch和当前验证产物，等待具体原生失败证据。

## 4. 最值得关注的 3 点

1. CPU生命周期问题已消除；这不是H200容量PASS。
2. 源码、身份与数学保持可核查；红色模式不恢复或丢弃任何已修改源码。
3. 原生GPU对照仍是Ticket02的必要前沿，正式cell不能据此提前验收。
