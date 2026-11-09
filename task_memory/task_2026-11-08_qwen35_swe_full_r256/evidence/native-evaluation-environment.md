## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | T03-NATIVE-ENV: existing environment/path reconnaissance, credential-name/location checks, CLI help, and native smoke command proposal. |

# Native SWE environment handoff

**Use the existing repaired Python3.10 SWE environment; no installation is needed to obtain the reference dependency path.** T01 is accepted. This handoff does not accept native ACS/agent/grader execution or the evaluator implementation under review.

## Existing environment and source paths

Native child interpreter:

```text
/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/.venv/br-native-swe-py310-1008am/environment/bin/python
```

Current local metadata: Python **3.10.20**, toml **0.10.2**, datasets **2.14.4**, pyarrow **12.0.1**, numpy **1.26.4**, pydantic **2.13.5**, torch distribution **2.6.0**, transformers **4.51.3**, brainpp **2.8.6**. These are interpreter/distribution observations, not a fresh native import or model-load test.

- Reference bundle explicitly selects this SWE interpreter. Its separate coordinator uses `.venv/br-native-harbor-py312-1007ck/bin/python`; do not substitute that Python3.12 Harbor environment for the native SWE child.
- The earlier `.venv/br-native-swe-py310-1007cl/environment/bin/python` still has datasets2.14.4/pyarrow25.0.1. The reference report documents its real `PyExtensionType` failure and the subsequent12.0.1 repair. Prefer **1008am**, not1007cl.
- Miles' `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python` remains Python3.12.13 and is available for the outer Miles coordinator. Set its evaluation configuration's `runtime.python` to the native3.10 interpreter above. Do not combine Python3.10 and3.12 binary site-packages.
- `step_align` and `swe_agents` are source checkouts, not installed distributions in the native environment. Their initial absence from default module search is solved by **PYTHONPATH**, not package installation.

Required source search order for the Miles-native child:

```text
/data/ycfeng/sota-engine/miles
/data/ycfeng/tmp/qwen35-swe-full-r256/swe-agents-1af09e5f-native/src
/data/ycfeng/steptron/.worktrees/step3p6-replay-v1
/data/ycfeng/steptron/third_party/step_align
/data/ycfeng/steptron/third_party/harbor/src
```

All paths exist. Import-free `PathFinder` checks resolve `tests` to Miles, `swe_agents` to the task's existing source snapshot, `step_align` to its existing checkout, and `playground` to the reference worktree. **Miles must precede the reference worktree**, because both own a top-level `tests` package. The Harbor source path preserves the existing reference dependency environment; it does not authorize Harbor/TB evaluation. No source pins were changed or re-investigated.

## Authentication: distinct owners

| Purpose | Names/configuration location | Current observation and limit |
| --- | --- | --- |
| ACS session creation and grader commands | `SweAgentShellEnvConfig.session_router_user_token = "${SESSION_ROUTER_USER_TOKEN}"`; `SweAgentACSShellEnvConfig.session_router_url` is the existing ACS endpoint. Native grading uses `SR_USER_TOKEN`. `SessionRouterClient` sends the **User-Token** header. | `SR_USER_TOKEN` name is present; `SESSION_ROUTER_USER_TOKEN` name is absent. Parent must inject the two aliases through its existing private worker environment mechanism. Presence does not establish nonempty content, validity, service permission, or network reachability. |
| Qwen model HTTP endpoint | StepAlign's `custom_upstream_url`; headers come from `extra_headers`, if the caller supplies them. | The native StepChat path does **not** automatically turn `OPENAI_API_KEY` into a bearer header. Direct unauthenticated serving needs no such key. A protected endpoint needs supported caller header wiring, resolved by the module/endpoint owner. An ACS token is not model-endpoint authentication. |
| Legacy Harbor sandbox alias | `STEPFUN_SANDBOX_TOKEN` in the reference private worker names. | Absent here; the reference launcher aliases it from the existing SR token. It is not a demonstrated requirement of the selected raw Session Router SWE path. |
| BrainPP/platform SDK and job submission | `BRAINPP_ACCESS_KEY`, `BRAINPP_SECRET_KEY`; reference launcher reads `/data/ycfeng/tmp/brainctl-auth-i-fengyicheng/accesskey_id` and `accesskey_secret`. Default SDK files are `/.auth/accesskey_id` and `/.auth/accesskey_secret`. | All four files exist by **stat only**; BRAINPP env names are absent. `AK_BASEMIND`, `SK_BASEMIND`, and `BRAIN_USERNAME` names are present. These are separate from ACS HTTP auth and do not prove an authenticated personal principal or quota. Parent owns any later platform/auth operation. |

The reference configuration's ACS endpoint is `http://session-router-acs.i-stepfun.com`. No request was sent. The reference launcher used `OPENAI_API_KEY=EMPTY` for its broader coordinator environment; do not interpret that placeholder as a required or valid SWE model credential.

`/home/brainpp/.zshenv`, `.zshrc`, `.bashrc`, and `.profile` exist. Their bodies were **not read**; the exact startup-file origin of the inherited SR/Basemind variables is therefore unverified. No credential-value files were opened, and environment checks used name membership only. Do not embed credentials in the invocation JSON, public configuration, command arguments, or this report.

## Executable command proposal

Parent/reviewer supplies the existing native invocation JSON for the next selected task/seed, with the accepted inputs, actual Qwen endpoint identity, original deadline and unchanged sampling/history/tool/thinking configuration. Set `SWE_NATIVE_INVOCATION` to that absolute file path. The following is the native child command, **not executed here**:

```bash
cd /data/ycfeng/sota-engine/miles
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/tmp/qwen35-swe-full-r256/swe-agents-1af09e5f-native/src:/data/ycfeng/steptron/.worktrees/step3p6-replay-v1:/data/ycfeng/steptron/third_party/step_align:/data/ycfeng/steptron/third_party/harbor/src \
  TMPDIR=/data/ycfeng/tmp HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  LOGURU_DIAGNOSE=NO OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  CUDA_VISIBLE_DEVICES= WORLD_SIZE=1 \
  /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/.venv/br-native-swe-py310-1008am/environment/bin/python \
  -B -m tests.manual.agent_opd.swe_native_evaluation \
  --invocation "${SWE_NATIVE_INVOCATION:?parent-authored absolute invocation JSON required}"
```

Before actual execution, parent injects `SR_USER_TOKEN` and `SESSION_ROUTER_USER_TOKEN` privately, using the existing credential owner. The model server is a separate parent-owned process/environment; hiding CUDA for this CPU agent/grader child does not change the server's approved GPU allocation. Run the child under the existing parent `NativeSweRunner` deadline/process ownership rather than treating this standalone diagnostic command as a substitute for the persistent runner. No new timeout, response cap, seed, topology, parser, model slice, dataset subset, retry rule, or resource budget is proposed.

The outer persistent entrypoint remains:

```text
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.swe_evaluation --configuration <parent-config.json> --point <point-id> --action run
```

That command runs the configured complete point, not a one-slot reconnaissance smoke. Use the task's existing contract and reviewed configuration; do not execute any historical reference `--submit`/`--check-native-contract` launcher as an environment probe, because those branches read credentials and may construct platform clients or submit jobs.

## Checks performed and remaining prerequisites

**Performed:** local Python version/distribution metadata, source-path resolution without importing native modules, directory/file stat checks, and both native CLI `--help` commands. The help commands used the native3.10 interpreter, `-B`, `PYTHONNOUSERSITE=1`, and the exact source-path order above; both exited0 and exposed `--invocation` and `--configuration/--point/--action`, respectively. No package installation, native SDK import/client construction, ACS call, auth-file read, model call, GPU/RJob operation, remote mutation, or external message occurred.

**Known missing:** this reconnaissance shell lacks the required `SESSION_ROUTER_USER_TOKEN` alias; a parent-authored real-smoke invocation/serving binding has not been supplied to this task. This is not an observation of a launched worker's private environment. Native imports and real execution remain parent-owned next steps.

**Declared package gaps, not established SWE blockers:** the native environment's BrainPP metadata lists absent `awscli`, `psutil`, `deprecated`, `elasticsearch`, `confluent_kafka`, `refile`, and `nvidia-ml-py3`. The reference report already distinguishes these optional/full-SDK gaps from its successful selected SWE import path. Do not install them merely to make a broad metadata check green. `tiktoken` is also absent; no requirement for it in this selected command was established.

**Unverified, not asserted missing:** actual module import compatibility in the assembled worker; credential content/validity and native CurrentVM principal; reachable Qwen endpoint/authentication; ACS capacity/image access; native agent/tool/grader output; worker mounts and effective platform environment. The separate evaluator review remains in progress. No genuine native capability PASS follows from `--help` or package presence.

## Evidence locations

- Reference runtime/environment report: `/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/task_memory/task_2026-10-01_step3p6_single_teacher_bounded_replay_h200/test_report_2026-10-07_native_evaluator_environment.md`, especially the1008am dataset repair and selected SWE retry sections.
- Reference executable/environment selection: that task's `artifacts/readiness/br-native-swe-selected-1008ay.bundle.json` (`swe_python`, `coordinator_python`, `pythonpath`, private **names** only) and `br-native-swe-selected-1008ay.launcher.py:21–31,61–62`.
- ACS configuration/inference: `/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/playground/agenticeval/sweagents_configs.py:153–165,215–219`; `sweagents_swe.py:619–650`.
- ACS header owner: `/data/ycfeng/tmp/qwen35-swe-full-r256/swe-agents-1af09e5f-native/src/swe_agents/utils/session_router_client.py:342–405`.
- Model endpoint header owner: `/data/ycfeng/steptron/third_party/step_align/step_align/model/stepchat.py:268–286`.
- Interpreter configuration: `/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/.venv/br-native-swe-py310-1008am/environment/pyvenv.cfg`.

Scope checkpoint: all requested reconnaissance items are delivered; stop environment exploration here. Next work is parent-owned reviewed invocation/private environment preparation and real native validation, not lifecycle rework, package installation, or another source-pin audit.
