## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Follow shared API `7d993848`, add raw span/placeholder receipts, verify 33 focused cases and record the actual seven-case fixture without changing selection. |
| 2026-11-11 | Record the CPU-only native-payload probe, 32 passing checks, exact worker command and unverified native measurements. |

# Teacher scoring probe — CPU readiness

Task ID: `profile-teacher-scoring-probe-20261111`. Scope: the three assigned files only. The primary owns platform execution, frozen input selection and acceptance. No production scoring code, platform submitter, formal configuration or existing job was changed. No GPU, SSH, platform or external HTTP operation was performed.

## 1. 规划完成情况

**汇总：** PASS 2｜BLOCKED/FAILED/SKIPPED 1｜TODO 1

| Subtask | Status | Evidence |
| --- | --- | --- |
| Dedicated worker probe | PASS | `tests/manual/agent_opd/probe_teacher_scoring.py` implements the requested fixed-input comparison and native child lifecycle. |
| CPU acceptance | PASS | Original 32-case suite accepted at `59d61941`; post-`7d993848` follow-up has 33 passing cases and Python 3.10 syntax/help. |
| Native GPU measurements | SKIPPED | Explicitly outside this subagent's authorization; no performance or native numerical PASS. |
| Scoped commit and handoff | TODO | CPU-ready deliverables; final commit receipt is returned to the primary. |

### Implementation and expected outputs

- Full mode calls the real `miles.rollout.on_policy_distillation._score_payload(tokens)`. Following shared API commit `7d993848`, response-only mode calls that same owner with `response_length=sample['response_length']`; the probe no longer contains its own prompt-minus-one formula. Both retain all input IDs, zero generated tokens and native completion-tail trimming.
- Each request records `expected_input_token_logprobs_count` and `first_requested_input_token_id` from the actual payload start. Validation records actual `input_token_logprobs_count`, `first_input_token_logprob` and `first_input_token_id` before native tail trimming. These are observations, not new acceptance gates. Nonfinite diagnostic values use the existing JSON-safe metadata representation, including malformed token IDs, so receipt serialization does not replace the original native validation error.
- Cold comparisons flush before every mode/sample request. Mode order alternates by repetition plus sample position. Warm-stream comparisons flush once per mode stream, keep the fixed sample order and alternate mode order by repetition. Two repetitions balance each cold case's first mode and each warm stream's first mode; one repetition's imbalance is explicitly recorded.
- HTTP requests use native `aiohttp`, a new session per request and the required finite, positive timeout. Records separately report time to headers, body bytes/read duration, JSON parse and validation duration. Unreached stages are null, not fabricated zero timings. Metadata retains original scalar fields and nested dictionaries; arrays are represented by their lengths.
- `/flush_cache` HTTP success is required. Other native errors propagate. Only 404/405/501 are classified as unsupported, recorded as `cache_undefined`; the result explicitly reports cold-cache and warm-stream-initial-flush verification as false. No cold-cache claim is made for those requests.
- Retained outputs: `preload.json`, `server_info.json`, `cache.jsonl`, `requests.jsonl`, `comparisons.jsonl`, `completion_scores/*.json`, `result.json` and the archived `server.log`. Full input-logprob response bodies and temporary caches stay in the newly created job-local directory and are not archived. Existing output and local directories are never reused or deleted.
- Completion IDs must match the fixed completion and scores must be finite. Differences between modes are reported as exact-equality flags, maximum absolute errors and maximum relative errors, with zero-reference relative errors explicitly undefined. No numerical tolerance is invented. Optional historical expected scores are compared only for A; caller-provided historical teacher provenance still requires primary verification.
- Preload evidence captures Python/SGLang/torch versions, configured image, actual `nvidia-smi` device strings, required SGLang source hashes plus the actual scheduler/cache/Qwen source decomposition, native scoring-source hashes and mounted model-manifest hashes before starting the teacher. All platform `NCCL_*` values are inherited unchanged. `_teacher_command`, `_wait_teacher_ready`, `_check_server`, `_stop_child` and `_worker_environment` are reused. Only this probe's new subprocess session is stopped, including on failure/cancellation.

### Commands and observed results

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`.

CPU environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python 3.12.13, SGLang 0.5.23, torch 2.11.0, aiohttp 3.14.3. System `python3`: Python 3.10.6. No conda environment or dependency installation was used.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_teacher_scoring_probe.py -q -p no:cacheprovider \
  --basetemp=/data/ycfeng/tmp/teacher-scoring-probe-pytest-20261111e
python3 -B -m tests.manual.agent_opd.probe_teacher_scoring --help
python3 -B - <<'PY'
from pathlib import Path
for name in ('tests/manual/agent_opd/probe_teacher_scoring.py', 'tests/fast/test_teacher_scoring_probe.py'):
    compile(Path(name).read_text(), name, 'exec')
    print(name, 'Python 3.10 syntax PASS')
PY
git diff --check -- tests/manual/agent_opd/probe_teacher_scoring.py \
  tests/fast/test_teacher_scoring_probe.py \
  task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_teacher_scoring_probe.md
```

Observed: final CPU suite **32 passed, 4 warnings in 0.77 s**; syntax and help exit 0. This duration measures the CPU test suite, not teacher performance. Warnings were existing SWIG type and `datetime.utcnow()` deprecations. The tests cover real payload/trimming boundaries, duplicate identities and malformed fixtures, incorrect IDs/nonfinite/null scores, unexpected generation, explicit timeouts, HTTP failures, unsupported flushes, ordered warm streams, A-only historical comparisons, raw-body placement and real CPU subprocess cleanup on injected startup/scoring/archive failures. No mock response is reported as native scoring evidence.

### Post-shared-API follow-up verification

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest \
  tests/fast/test_teacher_scoring_probe.py -q -p no:cacheprovider \
  --basetemp=/data/ycfeng/tmp/teacher-scoring-probe-followup-pytest-20261111a
python3 -B -m tests.manual.agent_opd.probe_teacher_scoring --help
python3 -B - <<'PY'
from pathlib import Path
for name in ('tests/manual/agent_opd/probe_teacher_scoring.py', 'tests/fast/test_teacher_scoring_probe.py'):
    compile(Path(name).read_text(), name, 'exec')
    print(name, 'Python 3.10 syntax PASS')
PY
```

Observed: **33 passed, 4 warnings in 0.93 s**, with the same existing deprecations; syntax/help PASS. The original 32 cases remain, with the instrumented receipt case also parameterized for response-only mode. Tests spy on the actual shared owner and require the explicit `response_length` keyword, verify both raw span counts and first-placeholder IDs/probabilities, preserve completion-tail IDs and finite scores, and confirm that malformed nonfinite placeholder/token-ID diagnostics propagate the original validation message rather than a JSON serialization failure. No full suite or native GPU execution was run.

The primary-provided fixture was read and validated on CPU at `evidence/teacher-scoring-probe-20261111/retained-cases.json`: 3,703,152 bytes, SHA256 `c45424e8106c2beb7500acacb68aa0939da0088c926af8012dd9fbd780f0ffc9`. Its unchanged input/response counts in order are `(97365,734)`, `(98312,246)`, `(98942,431)`, `(99074,290)`, `(113743,8124)`, `(116053,1687)`, `(3970,67)`. Actual source UIDs identify four groups: the first four rows share conversation `:5:` with ascending source assistant ordinals 123/125/127/129; the fifth is conversation `:13:`, followed by `:19:` and `:32:`. Thus the inspected fixture has four, not five, consecutive same-conversation cases. Selection and ordering were not changed; the primary owns any correction to its earlier five-case description.

This read used the real `_load_samples` and `_payload` functions on the fixture, with `context_tokens=131072`; it verified full requested spans equal each input count and response-only requested spans equal 735/247/432/291/8125/1688/68. These are payload expectations, not returned native span observations. At two repetitions, dynamic counts are `4 * len(samples) * repeats = 56` scoring requests and `(2 * len(samples) + 2) * repeats = 32` flush requests. There is no fixed six-case guard.

Earlier iterations: the first 25 core checks passed. The expanded 32-case suite first reported `FileNotFoundError` for assumed `scheduler_output_processor_mixin.py`; inspection showed the actual local decomposition under `scheduler_components/`. Required common sources now remain mandatory, with actual additional scheduler/cache/model files discovered and hashed. The next iteration's positive-size assertion incorrectly rejected the observed empty `scheduler_components/__init__.py`; the assertion now accepts zero-byte discovered package files and still requires nonempty mandatory execution files. Both failures were diagnosed rather than hidden. `python -m ruff check ...` could not run because this environment has no `ruff`; no linter PASS is claimed.

### Primary-owned worker invocation and native argv

Invoke only inside a newly allocated, dedicated single-node H800/codesign teacher task, with the primary's approved image, mounted sources, CUDA compatibility environment and fixture. The CLI takes no platform-control options:

```bash
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.probe_teacher_scoring \
  --config "$CONFIG" --pair A --samples "$FIXED_SAMPLES" \
  --output-dir "$NEW_OUTPUT_DIR" --repeats 2 --request-timeout 3600
```

`CONFIG`, `FIXED_SAMPLES` and `NEW_OUTPUT_DIR` are primary-provided paths, not files created by this subagent. `FIXED_SAMPLES` now points to this task's `evidence/teacher-scoring-probe-20261111/retained-cases.json`. Repeat with `--pair B` and a different new output directory if authorized. The timeout above is the current formal configuration's 3600-second request budget, not a code default; the caller can supply another positive budget. For the actual seven samples and two repetitions the bound is 56 scoring requests, 32 flushes and one server-info request, plus native readiness polling. Native A/B execution remains primary-owned and pending at four H800 GPUs per teacher, with the same formal flags. Startup uses the selected pair's explicit budget, currently 1800 seconds. Native `_stop_child` waits up to 60 seconds before escalating only its own session.

The following was derived on CPU from the current formal config and native command builder; `WORKER_IP` is a placeholder, not an observed allocation. The actual worker records its concrete argv and `/get_server_info`:

```text
A /opt/sglang/bin/python3 -B -m sglang.launch_server --model-path /mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-27B/model --host 0.0.0.0 --port 30000 --nnodes 1 --node-rank 0 --dist-init-addr WORKER_IP:29501 --tp-size 4 --dtype bfloat16 --context-length 131072 --mem-fraction-static 0.85 --max-running-requests 1 --chunked-prefill-size 8192 --disable-cuda-graph --enable-deterministic-inference --attention-backend fa3 --linear-attn-prefill-backend triton
B /opt/sglang/bin/python3 -B -m sglang.launch_server --model-path /mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-35B-A3B/model --host 0.0.0.0 --port 30000 --nnodes 1 --node-rank 0 --dist-init-addr WORKER_IP:29501 --tp-size 4 --dtype bfloat16 --context-length 131072 --mem-fraction-static 0.85 --max-running-requests 1 --chunked-prefill-size 8192 --disable-cuda-graph --enable-deterministic-inference --attention-backend fa3 --linear-attn-prefill-backend triton
```

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** original CPU acceptance `59d61941` through the shared-API/span follow-up｜**当前前沿：** scoped follow-up commit and primary handoff.

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 Tooling polish | CLEAR | Only requested probe contracts and CPU acceptance were built. |
| D2 Retry loop | CLEAR | Follow-up focused suite passed on its first run. |
| D3 Side quest | CLEAR | All changes stay in the explicit three-file assignment. |
| D4 Stalled parallel work | CLEAR | Other CPU/GPU scopes belong to the primary and other assignees. |
| D5 Gold-plating | CLEAR | No extra modes, platform wrapper, tolerance flag or production change. |
| D6 Analysis sprawl | CLEAR | Source inspection resulted in implemented contracts and verification. |
| D7 Off-route | CLEAR | CPU-only execution; native measurements and acceptance remain primary-owned. |

**文档检查：** S1–S6 均未发现明显缺陷 within this assigned slice; the explicit assignment supplies ownership and boundaries without changing the parent tickets.
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。
**需停止的偏离行为：** 无。
**接下去的路线：**

1. Commit only the three assigned files and return the commit receipt, commands and limits to the primary.
2. Primary freezes the follow-up diff and actual seven-case fixture, then runs the pending H800 A/B probes and inspects actual image/source/server identity, returned spans/placeholders, cold/warm records, completion IDs and observed errors. The existing shared parameter change remains subject to native verification.

## 4. 最值得关注的 3 点

1. Post-`7d993848` CPU readiness is complete. The primary reports the exact-image source version as `0.5.24.dev80+g056f871`; its source0/model-file check is independent and was not awaited or performed here. `_runtime` still locates actual imported source via `find_spec`, not editable-distribution `locate_file`. Native behavior, performance and completion-probability parity remain **unverified** here; no GPU or actual teacher HTTP call occurred in this subagent.
2. Configured image digest and mounted manifest hashes are not independent container-image inspection or whole-weight checksum proof. Primary platform receipts and unchanged authorized model mounts remain necessary. Historical A expected-score provenance is caller-owned, and B never uses it as a teacher reference.
3. Header latency includes request encoding, server computation and server response serialization. Body reading and client JSON parsing are separately measured, but server JSON serialization is not isolated. Sequential cold/warm passes diagnose the payload/cache mechanism; they do not reproduce the formal concurrent teacher queue or prove acquisition throughput acceptance.
