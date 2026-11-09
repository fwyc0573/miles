## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | T03-HF-BRIDGE: native callback identity/packaging/queue implementation, CPU verification and parent integration handoff. |

# T03-HF-BRIDGE — Native HF publication bridge

## Outcome / 结果

**Local implementation PASS; native GPU and benchmark acceptance remain pending.**
本地桥接已交付；CPU 检查不代替正式训练、4B HF 重载或 SWE agent/grader 验收。
No GPU/platform/cloud operations, shared requirements/spec/plan/progress edits, commits,
or source-weight writes were performed. Existing unrelated edits were preserved.

## Owned deliverables

| Repository-relative file | Change and reason |
| --- | --- |
| `tests/manual/agent_opd/swe_hf_export.py:33,85` | Compose existing `qwen_export.post_save` with native TrainStepOutput identity and EvaluationStore enqueue; no new exporter or forward pass. |
| `miles/backends/megatron_utils/actor.py:163,441,779,811,1098` | Retain/reset the latest actual train result; opt-in callback receives it, actual native rollout and existing weight-version accessor. Original four-argument callers remain unchanged. These are the only actor changes owned by this subtask; optimizer-step changes belong to T02. |
| `tests/manual/agent_opd/swe_evaluation.py:105–150` | Validate the successful-index HF directory independently of actual native rollout; require packaged successful update/index/version/source agreement and formal run kind. No start/allocation code was edited. |
| `tests/fast/test_swe_hf_export.py` | 23 focused CPU cases, using production actor train/save/accessor methods with synthetic optimizer/collective-export boundaries and real tiny Qwen packaging. |
| `tests/fast/test_swe_evaluation.py:37–70,144–147` | Update matching HF200 fixture to `step_199`, actual rollout213; retain the parent's allocation-policy edits. |
| `evidence/checkpoint_t03_hf_bridge.md` | Chinese check-progress checkpoint and scoped next route. |

## Commands and environment

Working directory: `/data/ycfeng/sota-engine/miles`. Python executable:
`/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python **3.12.13**, pytest **9.1.1**,
PyTorch **2.11.0+cu130**, Transformers **5.19.0**; no conda environment or dependencies changed.
System `python` was unavailable and system `python3` lacked pytest; the existing CPU environment was used.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_hf_export.py tests/fast/test_qwen_text_export.py tests/fast/test_swe_evaluation.py -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-hf-bridge-combined-final --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t03-hf-bridge-combined-final-tests.xml
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_hf_export.py -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-hf-bridge-formatted-final --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t03-hf-bridge-formatted-final-tests.xml
PYTHONPYCACHEPREFIX=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-hf-pycache /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m compileall -q tests/manual/agent_opd/swe_hf_export.py tests/fast/test_swe_hf_export.py tests/manual/agent_opd/swe_evaluation.py tests/fast/test_swe_evaluation.py miles/backends/megatron_utils/actor.py
git diff --check
```

Formatter/linter prefix:

```bash
/data/ycfeng/toolchain/bin/uv tool run --cache-dir /data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache --index-url http://mirrors.i.basemind.com/pypi/simple/ --allow-insecure-host mirrors.i.basemind.com
```

Suffixes actually checked:

- `--from black==24.3.0 black --check --line-length 119 tests/manual/agent_opd/swe_hf_export.py tests/fast/test_swe_hf_export.py`
- `--from isort==5.13.2 isort --profile black --line-length 119 --check-only tests/manual/agent_opd/swe_hf_export.py tests/fast/test_swe_hf_export.py`
- `--from ruff==0.14.7 ruff check tests/manual/agent_opd/swe_hf_export.py tests/fast/test_swe_hf_export.py tests/manual/agent_opd/swe_evaluation.py tests/fast/test_swe_evaluation.py`

Only the new files were formatted, using targeted patches; unrelated/shared code was not reformatted.

## Observed verification

| Check | Passing condition | Observed result |
| --- | --- | --- |
| Combined affected suite | All bridge, Qwen export and durable-evaluation cases pass | **71 PASS, 160.49s**: bridge23 + Qwen19 + evaluation29. |
| Final formatted bridge file | New file remains within fast CPU budget and passes after final formatting | **23 PASS, 7.02s**; implicit stage-a-cpu registration is sufficient. |
| First fixture correction | Execute actual callback instead of failing in AST fixture setup | First run: 2 FAIL/38 PASS because fixture omitted existing `compute_custom_function_config`; supplied that namespace dependency, then 21 PASS/6.76s before the final two cases were added. No production workaround. Red XML: `evidence/t03-hf-bridge-tests.xml`. |
| Skipped attempt / directory | Successful50, actual rollout50, native directory49 remain distinct | Production actor callback creates `hf/step_49`; manifest records successful50 / rollout50 / index49 / actual model version907 and attempted51/skipped1. |
| HF200 fixture mapping | Skips do not force actual rollout into directory name | `hf/step_199`, successful200, actual rollout213 pass enqueue and safe release checks. |
| Packaging → metadata → marker → queue | Enqueue sees completed text configuration and matching identity | Actual tiny Qwen package is text-only before enqueue; `.complete` is republished after identity metadata. No source bytes changed. |
| No added forward / native save | Bridge does not score or save optimizer/native weights | Callback uses existing tensor/header packaging and accessor; synthetic actor native-save boundary is never invoked. Existing 19 tiny-model tests retain loader/dtype/numerical checks. |
| Soft metadata/version/queue failures | Healthy callback returns, HF stays present and diagnosis is durable | Injected identity/version/metadata/marker/queue failures produce `UNVERIFIED` diagnostics under `<attempt>/hf_publications/step_N.json`; HF shards remain. Native conversion I/O still propagates. |
| Partial enqueue recovery | Failure after manifest publication does not mutate inventoried HF | HF inventory remains identical; recovered state is QUEUED; identical enqueue is idempotent. Diagnostics remain outside HF inventory. |
| Smoke | Never enqueue a formal 400-attempt point | successful2 and successful50 smoke packages have `SMOKE_PACKAGED`; direct store enqueue rejects smoke; no score is invented. |
| Legacy callback | Old four arguments still work without native-state access | Original `qwen_export.post_save` runs through production actor.save_model with no latest-result attribute and no weight-version inspection. |
| Producer exit | Separate process can read queue | A fresh `python -m tests.manual.agent_opd.swe_evaluation ... --action queue` subprocess returns the queued HF50 point. |
| Static checks | Syntax, lint, formatting and whitespace pass | compileall, Ruff, Black, isort and `git diff --check`: PASS. Existing SWIG/torch.jit deprecation warnings remain; no runtime errors. |

These are observations from CPU fixtures, not formal scores. If the diagnostic storage itself
cannot write, the bridge logs that failure and remains non-blocking; storage repair is still required.

## Parent integration entrypoint and next actions

1. Set `checkpoint.post_save_hook` to **`tests.manual.agent_opd.swe_hf_export.post_save`**.
   The current native actor automatically supplies the opt-in state; preserve no native `--save`.
   Smoke needs no evaluation configuration and records packaging/native identity only.
2. For formal cells, pass **`--swe-evaluation-configuration <path>`**. The existing JSON must
   contain `root`, `owned_root`, `protected_sources`, `reference_root`, `task_ids` and
   `evaluation_contract`. The bridge derives point identity from the actual native receipt:
   `<cell with / replaced by ->.<attempt>.HF<successful_update>`; only the existing HF_UPDATES
   50/100/150/200 may enter the formal queue. No manually maintained publications map is needed.
   `run_swe_opd.py` currently does not consume `checkpoint.hook_args`; the parent must wire the
   explicit configuration flag for formal launch. That file and integration_config were not edited here.
3. Parent/T02 run the approved native smoke, verify actual TrainStepOutput/current model version,
   exported full4B text HF reload and preserved HF on evaluator failure. Then complete the actual
   SWE agent/grader checks and reader-safe lifecycle before formal acceptance. No GPU was launched here.
4. The check-progress checkpoint flags stale ticket02/03 status text referring to already-complete01;
   update those shared records in the parent session. No scientific scope change is proposed.
