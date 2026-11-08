## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Verify original4B and trainedHF3 native agent/grader results, artifact/request hashes and reader cleanup after the private environment repair. |
| 2026-11-08 | Record the first real Qwen serving PASS, native harness environment failure and CPU red/green reproduction. |

# Native SWE qualification

## First attempt: serving PASS, agent/grader not reached

- Job: `exp-1108-175747-357945`, point `qualification.original4b`, explicit slot `astropy__astropy-12907#attempt-0` (seed1729). This is not the formal shared400-attempt baseline.
- Deployment: pinned image from `integration_config.json`, two H200s,16 CPUs/128GiB; local mount `100.96.128.195:/data/ycfeng:/data/ycfeng`. Admission20+2 of the temporary64-card task budget, non-preemptible. Local launcher stayed alive until platform Succeeded.
- Input: immutable `evaluation_qualification_config.json`, built with the actual repaired native Python3.10 interpreter. Local submitter dry-run then real invocation used `--original-source <original4B>` and the one explicit `--qualification-attempt`; exact source/config/point/job identity is retained in `evidence/admission-eval-original4b-qualification-20261108.json`.
- Serving: owned two-GPU SGLang loaded the original4B snapshot. Actual model endpoint weight version0, SGLang `0.5.24.dev80+g056f871`,128K context, `qwen3_coder`/`qwen3`, fixed template SHA `ca447731ed457cb460b7522ea9edb986d52e4ea62c5d8482365146592d69b1b9`, preserved/enabled thinking all matched. This does not prove a generated HF reload or a real agent response.
- Native child failed before agent/grader execution: `RunCheckPipeline.__init__` raised `RuntimeError: Should setup env vars: AK_BASEMIND & SK_BASEMIND`. Both variables exist in the parent's environment, while the submitted worker environment contained neither. The submitter had forwarded only router-token aliases.
- Ledger: completed0/400, avg@4 null, INCOMPLETE; server, native child and qualification evaluator readers all EXITED. No HF/source deletion. Platform exit0 is not native evaluation acceptance.

Persistent selected evidence:

- `evidence/qualification-original4b-first-result.json`: actual model identity, deadline and reader exits.
- `evidence/qualification-original4b-native-failure.log`: redacted original traceback.
- Raw local launcher log: `/data/ycfeng/tmp/qwen35-swe-original4b-qualification-20261108.log`.
- Cloud point: `/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/qualification-evaluations/points/qualification.original4b/`.
- Original deadline: Unix `1794391269.8995442`; first start `1794132069.8995442`. Recovery must retain these, preserve the same manifest, and fill only the missing slot.

## Cause-level CPU reproduction

Local Python3.10 submitter probe called `_worker_environment(integration_config)` with the existing private environment. For each required key it printed only `local_present=True, worker_present=False`, then failed an equality assertion. No values were printed or saved.

The exact worker-generated, pre-substitution native `config.toml` was read into `/data/ycfeng/tmp/qwen35-swe-native-constructor/config.toml`. Under the repaired interpreter and original native PYTHONPATH, the actual `RunCheckPipeline` was constructed first with both variables temporarily removed, then with their existing values restored in process memory. The first call reproduced the exact RuntimeError; the second loaded exactly one selected instance and passed. It did not invoke ACS, generate a trajectory or score a patch.

Interpreter: `/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/.venv/br-native-swe-py310-1008am/environment/bin/python` (Python3.10). Environment: `PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, `LOGURU_DIAGNOSE=NO`, `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `TMPDIR=/data/ycfeng/tmp`; PYTHONPATH is Miles, pinned SWE snapshot `/src`, reference worktree, StepAlign and Harbor `/src`, in that order. Native positive/negative constructor output is `/data/ycfeng/tmp/qwen35-swe-native-constructor-env-20261108.log`.

The subsequent private environment repair, explicit resume and native reruns are recorded below. Model/scorer behavior and the immutable scientific contract remain unchanged.

## Recovery and real trained-HF qualification: PASS

The submitter now requires and privately forwards both existing AK/SK values alongside the router aliases. The actual local handoff assertion passed. Values are not present in configuration files, receipts, command arguments or this report. Qualification/lifecycle regression evidence is in `test_report_2026-11-08_hf_qualification.md` (182 full-suite passes; final affected50 passes).

The original point was explicitly resumed only after all prior readers exited. An initial zero-GPU operator command used a nonexistent summary key and failed before mutation; its corrected command used the existing `missing_attempt_ids` interface. The successful resume preserved first start `1794132069.8995442` and absolute deadline `1794391269.8995442` and left the same400-slot manifest intact. See `evidence/qualification-original4b-resume.json` and the recovered admission receipt.

Native submissions used the same authenticated local StepMind shell and pinned image as the first attempt. Exact commands, with environment values omitted:

```bash
PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron \
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_swe_evaluation \
  --config task_memory/task_2026-11-08_qwen35_swe_full_r256/integration_config.json \
  --configuration task_memory/task_2026-11-08_qwen35_swe_full_r256/evaluation_qualification_config.json \
  --point qualification.original4b \
  --receipt task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/admission-eval-original4b-recovered-20261108.json \
  --qualification-attempt 'astropy__astropy-12907#attempt-0'

# The trained-HF invocation uses the same module/config and explicit attempt, plus:
--configuration task_memory/task_2026-11-08_qwen35_swe_full_r256/evaluation_hf_qualification_config.json
--point qualification.A-r256-smoke-HF3
--receipt task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/admission-eval-trained-HF3-qualification-20261108.json
--qualification-checkpoint /mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/integration/r256/student/A/exp-1108-172407-535512/hf/step_2
```

The actual invocations used absolute configuration/receipt paths from `/data/ycfeng`. GPU server interpreter: pinned `/opt/sglang/bin/python3`, Python3.12; native agent/grader interpreter: the verified `br-native-swe-py310-1008am` Python3.10.20. Both allocations were twoH200 workers admitted by the same policy/flock path; their original local launchers remained alive through terminal status.

| Point | Observed model | Weight version | Recorded requests | Native grader | Reader cleanup |
| --- | --- | --- | --- | --- | --- |
| `qualification.original4b` | `Qwen3_5ForConditionalGeneration`, original source | 0 | 93 | resolved;2 FAIL_TO_PASS and13 PASS_TO_PASS, no failures | All6 readers, including the failed first attempt, EXITED |
| `qualification.A-r256-smoke-HF3` | `Qwen3_5ForCausalLM`, actual trained export | 3 | 104 | resolved;2 FAIL_TO_PASS and13 PASS_TO_PASS, no failures | All3 readers EXITED |

Both agents ended with `exit_status=submitted`; patches existed and were successfully applied in the native grader. Grading completed at `2026-11-08T11:11:26.882598Z` and `2026-11-08T11:22:35.164373Z`, taking64.4746s and63.3494s respectively. These two checks validate the serving/template/tools/ACS/grader path, not a benchmark capability comparison.

The trained package identifies successful update3, native rollout2, checkpoint index2, weight version3, native attempted3/skipped0, run kind`smoke`. It contains426 tensors (402 BF16,24 F32), with tensor payload8,411,504,128 bytes. These are the actual package metadata values; the payload byte count is not the complete directory size.

All config/trajectory/grader artifact hashes and all197 recorded request-file hashes were independently recomputed from the cloud artifacts through read-only `ssh shai-ycfeng`, with a55-second remote timeout and30GiB address-space limit. The verified receipt is `evidence/native-swe-qualified-20261108.json`; it retains exact artifact paths/hashes and test counts. No cloud weights were copied locally. Actual requests did not override `max_tokens`; all recorded values were null, preserving the frozen reference request policy. Serving still declared context131072, enabled/preserved thinking and the expected Qwen parsers/template.

Both qualification ledgers intentionally remain INCOMPLETE, completed1/400, missing399, avg@4=null. Both models still exist, and all readers exited. The recovered original point retains its original deadline. This is not Ticket08's formal400-attempt baseline and is not permission to release qualification weights.

## Remaining acceptance work

- Actual cloud-filesystem lifecycle checks use the existing CPU failure-injection cases in an isolated fixture namespace. The first zero-GPU invocation failed during pytest setup because the new parent directory did not exist; no case reached its body. The corrected invocation creates only that parent before using a fresh job-scoped base. Results remain pending here.
- The automatic export notification/independent submit/drain integration has passed the recorded local tests; no formal HF50/100/150/200 notification has yet been emitted by a formal training cell.
- Formal baseline and four formal training cells remain pending. Ticket02 still needs capacity and actual-gradient acceptance.
