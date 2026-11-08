## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Add explicit qualification-only slot execution; fix the supported native3.10/GPU3.12 import boundary; verify full real native construction and 53 focused checks. |
| 2026-11-08 | T03-WORKER: single-point worker/config assembly, CPU verification, deployment inputs and remaining native prerequisites. |

# T03-WORKER — Single-point native evaluation worker

## Outcome and scope

**Local implementation PASS; live native acceptance remains pending.**

The worker owns one separately admitted two-GPU SGLang server and invokes the
unchanged reviewed `NativeSweRunner` / `evaluate` / `EvaluationStore` mechanisms.
It registers the server reader before launch, validates endpoint readback, joins
owned cleanup before reader exit, and releases only a complete archived point.
Incomplete evaluations and failed cleanup retain HF/results. Baseline source
weights are never copied or deleted. No automatic resume, infrastructure retry,
deadline renewal, completed-slot rescore, platform submitter or alternative grader
was added.

No GPU/platform/network/cloud operation, credential-value read, commit, shared task
document edit, core training edit or existing evaluator edit was performed. CPU
fixtures include tiny owned-HF deletion and actual local sleep-process cleanup;
these are not real model deletions or native benchmark scores.

## Deliverables

| Repository-relative path | Purpose |
| --- | --- |
| `tests/manual/agent_opd/run_swe_evaluation.py` | Pinned server command, actual endpoint identity checks, native-only role, reader-safe one-point orchestration, worker CLI; qualification follow-up below. |
| `tests/manual/agent_opd/swe_evaluation_config.py:18` | Source-backed constructor calling the existing native configuration/contract owner; refuses mismatched pins, tasks, harness or Qwen identity. |
| `tests/fast/test_swe_evaluation_worker.py` | Initially 15 focused CPU tests; now 30 with qualification and interpreter-boundary regression coverage. |
| `evidence/swe-evaluation-inputs.template.json` | Accepted paths/digests; required deployment observations remain explicit null inputs rather than invented IDs/versions. |
| `evidence/checkpoint_t03_worker.md` | Updated milestone check-progress; parent corrected the prior ticket03 state defect. |

## Configuration and deployment handoff

1. Copy the input template to a new parent-owned input file. Fill `url` with an
   available loopback HTTP port, `server_reader_id` with the candidate endpoint
   identity, actual `server_identity.sglang_version`, original-source
   `baseline_weight_version` and endpoint `weight_version`, and positive native
   cleanup/server request/server cleanup timeouts. Coordinator cleanup grace must
   exceed native child cleanup grace. The worker creates a fresh persistent server
   reader identity for each launch; endpoint/reader locations are excluded from
   the shared immutable scientific contract by the existing evaluator.
2. The template's ordered-manifest SHA256 was recomputed locally as
   `b3a0d001a746119f0434d05b5e22e74ce5d5fcf9486958a183ee5e24329ea129`.
   The constructor checks the accepted source pins, library, manifest-ordered 100
   IDs and actual native constructor against all four reviewed payloads. It does
   not select library[:100], invent task IDs or maintain another harness recipe.
3. Construct **once before enqueue**, with the existing native3.10 environment:

   ```bash
   env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= WORLD_SIZE=1 \
     PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/tmp/qwen35-swe-full-r256/swe-agents-1af09e5f-native/src:/data/ycfeng/steptron/.worktrees/step3p6-replay-v1:/data/ycfeng/steptron/third_party/step_align:/data/ycfeng/steptron/third_party/harbor/src \
     /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/.venv/br-native-swe-py310-1008am/environment/bin/python \
     -B -m tests.manual.agent_opd.swe_evaluation_config --inputs INPUTS.json --output CONFIG.json
   ```

   This is a deployment command proposal, **not a performed configuration of a real
   endpoint**. Existing output files are refused. For formal training, pass this
   path through `checkpoint.hook_args.swe_evaluation_configuration`; the existing
   `swe_hf_export.post_save` consumes `task_ids` and `evaluation_contract` without a
   publications map. Do not rebuild an already-enqueued contract.
4. Baseline uses the same config and existing API:

   ```python
   store_from_config(config).enqueue_baseline(
       point_id=parent_selected_baseline_id,
       source=config["original_source"],
       task_ids=config["task_ids"],
       configuration=config["evaluation_contract"],
   )
   ```

5. Parent selects an existing queued point and admits one RJob using its existing
   platform owner/shared `gpu_policy.json`. Provide the actual allocation JSON:
   `job_id` from the submitted job, `eval_gpus=2`, and its actual `admission` receipt.
   No new quota values or job IDs are synthesized. Store validation binds
   `allocation_identity={task_id, creator, gpu_tag}`; main also checks the actual
   RJob name, single replica/rank, two visible matching GPUs and GPU interpreter.

   ```bash
   /opt/sglang/bin/python3 -B -m tests.manual.agent_opd.run_swe_evaluation \
     --configuration CONFIG.json --point POINT --allocation ACTUAL_ALLOCATION.json
   ```

6. Resources: one node / two H200 GPUs, existing `step_main` allocation, exact
   `integration_config.json` image and mounted `/data/ycfeng` workspace plus
   `juicefs+s3://oss.i.shaipower.com/codesign-exp:/mnt/codesign-exp`. All durable
   writes stay under the task's `/mnt/codesign-exp/ycfeng` root; caches use the
   existing worker-local preparation. CPU and memory resource requests must be
   supplied/verified by parent; no new measured sizing claim is made. Every RJob
   must carry the shared policy's `miles.ycfeng/task` annotation.
7. GPU server stays in image Python3.12. The native coordinator and agent/grader
   children use the existing repaired Python3.10, with Miles → pinned SWE source →
   replay reference → StepAlign → Harbor **source** order. No Python3.12 binary
   site-packages are appended to Python3.10. Native CUDA visibility is empty.
   `SR_USER_TOKEN` and `SESSION_ROUTER_USER_TOKEN` are inherited privately; values
   are never configuration/command fields. Parent supplies both aliases and owns
   the platform launcher lifecycle.

## Verified checks

| Check | Passing condition | Actual / verdict |
| --- | --- | --- |
| First worker suite | Exercise config and lifecycle boundaries | 10 PASS / 2 FAIL, 5.72s; fixture used an undefined unqualified `evaluate`; corrected to `swe.evaluate`, without production workaround. |
| Initial complete suite | All worker cases pass | 14 PASS, 12.57s. |
| Combined affected checks | Worker15 + reviewed native22 + real four-child cancellation1 | **38 PASS, 21.78s**, no skips; two existing SWIG deprecation warnings. |
| Final cleanup receipt refinement | Failed cleanup explicitly records `CLEANUP_FAILED` and retains reader/HF | **15 PASS, 12.51s**. |
| Real native constructor, CPU only | Four actual native configs match reviewed evidence | Python3.10.20: seeds1729–1732, exact normalized config equality PASS. No model/ACS/grader call. |
| Reader/ownership ordering | Reader enter precedes load; reaping precedes reader exit/release | Actual owned CPU process reaped; separate foreign process remained live until fixture cleanup. PASS. |
| Native role seam | Use actual reviewed constructor and real store; fake only model/ACS call | Exact NativeSweRunner constructor checks pins/harness/tasks/path/version/parsers/reader, issues only two missing slots, leaves live server reader for worker cleanup. PASS. |
| Missing infrastructure result | Null complete score and retained HF; no auto retry | 399/400 completed; avg=null; repeated run rejected pending diagnosed resume; unchanged deadline. PASS, CPU fixture. |
| Completed model outcome | Never issue the 398 precompleted fixture slots again | Only the two missing task/seed slots issued. PASS. |
| Baseline | Use original path/version and never delete source | PROTECTED_SOURCE / deleted_bytes0; original fixture bytes unchanged. PASS. |
| Static/help | Black24.3.0, Ruff0.14.7, isort5.13.2, AST/whitespace, native3.10 CLI help | PASS; existing Ruff configuration warning only. |

Commands ran from `/data/ycfeng/sota-engine/miles`; outer Python3.12.13 / pytest9.1.1,
native Python3.10.20; no conda or dependency environment change.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_evaluation_worker.py tests/fast/test_swe_native_evaluation.py tests/fast/test_swe_evaluation.py::test_four_seed_cancellation_joins_slow_native_cleanup -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-worker-final --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t03-worker-final.xml
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_evaluation_worker.py -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-worker-cleanup-final --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t03-worker-cleanup-final.xml
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/-kQQ6CPyKAABpsmE/bin/black --line-length 120 --check tests/manual/agent_opd/run_swe_evaluation.py tests/manual/agent_opd/swe_evaluation_config.py tests/fast/test_swe_evaluation_worker.py
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/8QpD66osZqn5M69v/ruff-0.14.7.data/scripts/ruff check tests/manual/agent_opd/run_swe_evaluation.py tests/manual/agent_opd/swe_evaluation_config.py tests/fast/test_swe_evaluation_worker.py
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/YeSQ9F0UbXV9REOw/bin/isort --profile=black --line-length=120 --check-only tests/manual/agent_opd/run_swe_evaluation.py tests/manual/agent_opd/swe_evaluation_config.py tests/fast/test_swe_evaluation_worker.py
git diff --check
```

Native constructor check used the exact native environment prefix above, followed
by `python -B -` and this CPU-only body (URL is deliberately a config-only fixture):

```python
from tests.manual.agent_opd import swe_native_evaluation as native
from tests.manual.agent_opd.swe_evaluation import SEEDS, read_json
pins = read_json("task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/evaluation-source-pins.json")
runtime = {"dataset_path": pins["configuration_payloads"][0]["dataset"]["name_or_path"],
           "model_name": pins["configuration_payloads"][0]["model"]["model_name"],
           "url": "http://cpu-config-only-fixture"}
for seed, recorded in zip(SEEDS, pins["configuration_payloads"]):
    actual = native.native_config(runtime, request={"seed": seed}, dataset_index=0)
    assert native._config_contract(actual) == native._config_contract(recorded)
```

Native help used the same prefix and `-B -m tests.manual.agent_opd.run_swe_evaluation --help`.
Selected raw JUnit evidence is `evidence/t03-worker-first.xml`,
`evidence/t03-worker-second.xml`, `evidence/t03-worker-final.xml` and
`evidence/t03-worker-cleanup-final.xml`.

## Specific remaining blockers / limits

- Real endpoint/version/admission values are deliberately absent from the template.
  Parent must supply them, not treat the template as launch-ready.
- Qwen parser selection is registry-backed `qwen3_coder` / `qwen3` and explicitly
  `CANDIDATE_PENDING_NATIVE_VERIFICATION`. Native agent history/tools/thinking,
  actual HTTP request bodies, engine generation cap and real grading remain pending.
- `--weight-version` and `--default-chat-template-kwargs` are backed by the locally
  inspected SGLang source (`srt/arg_groups/fields/serving.py:172–218`), and native
  `/model_info` / `/server_info` identity surfaces by `entrypoints/http_server.py:812–890`.
  Their availability/readback in the **pinned worker image** is not yet verified.
  Unsupported flags/readback fail and retain HF; no replacement server/template or
  grader path was invented. `--weight-version` is an operator-set native label,
  **not** content-equality proof; full HF reload/checksum acceptance remains parent-owned.
- Actual mounted-cloud atomicity/deletion, creator/image/mount/terminal receipts,
  ACS authentication/capacity, and training → HF → native evaluation → release are
  still required. The worker does not accept those prerequisites from CPU results.

Requirements D8–D10 and execution authorization were re-read before handoff.

## Qualification follow-up — T03-WORKER

### Requests, implemented boundary and outcome

[Original Request / Follow-up excerpt]: "one or a short explicit list" selected
from the frozen100×4, "never label partial output avg@4/complete or release its
HF", "no fake completion"; preserve the original deadline and completed slots.
The later explicit steering authorizes moving Qwen registry validation to the
GPU Python3.12 worker, not installing SGLang in native3.10 or modifying core
chat-template/training files.

**PASS: real native3.10 full build_configuration and NativeSweRunner construction;
53 focused CPU checks. Real serving/ACS/native grading remains pending.**

- `run_swe_evaluation.py:216`: repeated `--qualification-attempt TASK_ID#attempt-N`
  requires a root whose final component is `qualification-evaluations` and a
  `qualification.<name>` point. Missing selection in that namespace, formal
  namespace selection, duplicate/ambiguous/foreign slots, and a selection that
  would complete the full ledger are rejected before server launch.
- `run_swe_evaluation.py:244`: the small sequential qualification loop uses the
  exact NativeSweRunner/scorer and existing store `start/request/record/infra_failure/
  reader_enter/reader_exit/settle`. It executes only selected missing slots under
  the original absolute deadline. It does not invoke the full 400-attempt loop,
  fill unexecuted slots, change the scientific contract, retry automatically or
  release HF. Ordinary formal execution still invokes the unchanged `evaluate`.
- `start/server/cleanup/worker.json` and `qualification_runs/*.json` explicitly
  carry `run_kind=qualification`; the full immutable manifest and 400-slot ledger
  remain intact. Partial full-benchmark summaries retain `avg_at_n=null` and
  `INCOMPLETE`; a completed native False is persisted once, not rerun.
- Native3.10 construction previously failed through
  `chat_template_utils.__init__ → template.py → sglang`; reproduced directly with
  the parent's exact inputs. The original error is retained in
  `/data/ycfeng/tmp/qwen35-swe-evaluation-config-20261108.log`.
- `run_swe_evaluation.py:195` now validates the actual registered Qwen parser names,
  fixed template path/bytes and thinking/context in outer Python3.12 **before any
  server reader/model launch**. No parser table was duplicated.
  `swe_evaluation_config.py:57` puts the accepted template path into the frozen
  runtime. `swe_native_evaluation.py:166–195` keeps manifest/source/harness/task,
  live-reader/model-path/version checks and verifies this pinned template's actual
  bytes, without any GPU chat-package import. Actual HTTP/native request validation
  and grading code remain unchanged.

### Exact real native3.10 checks performed

Working directory `/data/ycfeng/sota-engine/miles`; native Python3.10.20,
`PYTHONNOUSERSITE=1`; no conda/install, GPU/network/platform/cloud call or credential
read. The existing interpreter/source order is unchanged:

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= WORLD_SIZE=1 \
  PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/tmp/qwen35-swe-full-r256/swe-agents-1af09e5f-native/src:/data/ycfeng/steptron/.worktrees/step3p6-replay-v1:/data/ycfeng/steptron/third_party/step_align:/data/ycfeng/steptron/third_party/harbor/src \
  /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/.venv/br-native-swe-py310-1008am/environment/bin/python \
  -B -m tests.manual.agent_opd.swe_evaluation_config \
  --inputs task_memory/task_2026-11-08_qwen35_swe_full_r256/evaluation_qualification_inputs.json \
  --output /data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-qualification-native310-built-20261108.json
```

**Actual: exit0, complete configuration written.** Parent input/output files were
not changed. The exact same environment prefix plus `python -B -` then ran:

```python
import copy, json, os, sys, tempfile
from pathlib import Path
from tests.manual.agent_opd.swe_evaluation import read_json, store_from_config
from tests.manual.agent_opd.swe_native_evaluation import NativeSweRunner
config = copy.deepcopy(read_json('/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-qualification-native310-built-20261108.json'))
root = Path(tempfile.mkdtemp(prefix='t03-native310-constructor-', dir='/data/ycfeng/tmp/opencode-v2-tmp/opencode'))
source = root / 'cpu-original-source'
source.mkdir()
config.update(root=str(root / 'qualification-evaluations'), owned_root=str(root), protected_sources=[str(source)])
config['runtime']['server_identity']['model_path'] = str(source)
store = store_from_config(config)
point = 'qualification.native310-constructor-fixture'
store.enqueue_baseline(point_id=point, source=source, task_ids=config['task_ids'], configuration=config['evaluation_contract'])
store.reader_enter(point, config['runtime']['server_reader_id'], {'pid': os.getpid(), 'cpu_fixture': True, 'run_kind': 'qualification'})
runner = NativeSweRunner(store, point, config['runtime'])
assert not any(name == 'sglang' or name.startswith('sglang.') or name.startswith('miles.utils.chat_template_utils') for name in sys.modules)
summary = store.summary(point)
assert summary['completed'] == 0 and summary['avg_at_n'] is None and len(summary['missing_attempt_ids']) == 400
store.reader_exit(point, config['runtime']['server_reader_id'], {'constructor_only': True, 'cpu_fixture': True})
```

**Actual: NativeSweRunner constructor PASS; no SGLang or GPU chat-package imported,
100 tasks / 400 missing / avg=null.** Retained local fixture:
`/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-native310-constructor-9sk0cs78`.
The model directory/endpoint reader were deliberately CPU fixtures, not a real
loaded model. Native source/harness/benchmark construction was actual, unmocked.
Native3.10 `-B -m tests.manual.agent_opd.run_swe_evaluation --help` also passed with
the new qualification option.

### Focused verification and iteration evidence

| Check | Expectation | Actual |
| --- | --- | --- |
| Qualification selection/lifecycle + reviewed native regressions | Selected slots only; real CPU process cleanup; no formal-path regression | First51 PASS /31.15s. |
| Expanded suite | Include wrong-parser actual-launch rejection and four-seed cancellation | 52 PASS /1 FAIL /32.15s: fixture selected an old EXITED reader by sorted random UUID. Corrected fixture to select the unique RUNNING server reader; no production workaround. |
| Final affected suite | All worker30 + reviewed native22 + real four-child cancellation1 | **53 PASS /31.78s**, two existing SWIG deprecation warnings, no skips. |
| Two explicit task/seed slots | Remaining398 missing, null full score, all readers reaped, no release | PASS; manifest bytes unchanged, only selected slots recorded, all actual owned CPU server/child process groups reaped. |
| Explicit diagnosed continuation | No automatic restart; completed slot untouched; no deadline renewal | PASS; second run issues only the new missing slot; original absolute deadline and completed result bytes unchanged. |
| Infrastructure/cancellation | Missing slot remains missing; native child/server cleanup joined | PASS; zero fake successes/completion, null summary, no release. |
| Native import boundary | Fail if builder/constructor imports SGLang or GPU chat package | Persistent import-block regression PASS and real Python3.10 checks above PASS. |
| Actual GPU-side registry gate | Wrong parser/template must still fail before launch | Three registry identity cases and constructed wrong-parser launch PASS. No real GPU operation used. |
| Static checks | Black24.3.0 / Ruff0.14.7 / isort5.13.2 / git diff --check | PASS; pre-existing Ruff config deprecation warning only. |

Final command (outer Python3.12.13 / pytest9.1.1):

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_evaluation_worker.py tests/fast/test_swe_native_evaluation.py tests/fast/test_swe_evaluation.py::test_four_seed_cancellation_joins_slow_native_cleanup -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-qualification-verified --junitxml=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/t03-qualification-verified.xml
```

Earlier runs used the same pytest command without the single cancellation selector
for `t03-qualification-first`, and with it for `t03-qualification-final`, replacing
the matching basetemp/XML suffix. Their raw XML remains retained. Static commands
are the existing exact formatter/linter prefixes listed above, with all five owned
files: `run_swe_evaluation.py`, `swe_evaluation_config.py`, `swe_native_evaluation.py`,
`test_swe_evaluation_worker.py`, `test_swe_native_evaluation.py` (repository paths
under the corresponding `tests/manual/agent_opd/` or `tests/fast/` directories).

### Parent's next exact qualification command / remaining seam

Parent can rerun the real construction command above, changing **only its output**
to `task_memory/task_2026-11-08_qwen35_swe_full_r256/evaluation_qualification_config.json`.
This output remains parent-owned; none was written by this subtask. In that config's
existing `qualification-evaluations` root, enqueue an original-source baseline with
the unchanged existing API and exact100-task/config values:

```python
store_from_config(config).enqueue_baseline(
    point_id='qualification.original4b', source=config['original_source'],
    task_ids=config['task_ids'], configuration=config['evaluation_contract'],
)
```

Then parent/local-submit owner can run the existing worker on its actual admitted
two-H200 allocation, inheriting both SR token aliases privately:

```bash
/opt/sglang/bin/python3 -B -m tests.manual.agent_opd.run_swe_evaluation \
  --configuration /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evaluation_qualification_config.json \
  --point qualification.original4b --allocation ACTUAL_ALLOCATION.json \
  --qualification-attempt 'astropy__astropy-12907#attempt-0'
```

The task ID is source-backed by the first frozen manifest entry, with seed1729.
Repeat the option for an explicit short list. Parent's supplied version0,
SGLang`0.5.24.dev80+g056f871`, URL30000 and120/600/5s cleanup/request settings were
used unchanged in the real configuration construction; they are not a serving or
grading PASS. Real request/tool/context/parser behavior and ACS/native grader
qualification are still required. Partial qualification must never enter the
formal17-point score table.

Owned **smoke-export HF is not yet admitted**: the formal `enqueue_checkpoint`
50/100/150/200 successful-update gate is unchanged. If required later, the minimal
new seam is an explicit qualification-only enqueue method that validates the
existing completion/export/publication evidence with its **actual** successful
update and weight version, binds the same full contract in this separate namespace,
and prohibits release. Do not rewrite smoke update3 as formal50 or disguise owned
smoke HF as the protected original baseline. That store/publication seam is not
implemented in this scoped follow-up.

No GPU/platform/cloud/network operation, credential-value read, commit, parent
configuration edit or live-training/core chat-template edit occurred. Source/harness
pins, native request checks, native scoring and formal four-seed execution remain
intact. Required milestone check-progress is updated in the existing owned report
`evidence/checkpoint_t03_worker.md`; Ticket03 remains TODO until real native acceptance.
