## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Verify native raw teacher-response diagnostics, close full-prefix identity finding, and record final 98-check combination. |

# Fixed-monitor teacher/student diagnostic

## Scope and evidence contract

D9/R5 requires measuring learning on the fixed prefixes. This offline diagnostic remains separate from D8's same-student numerical verdict. Modified files:

- `tests/manual/agent_opd/inspect_qwen35.py`
- `tests/fast/test_qwen35_monitoring.py`

The native eval dump precedes reward conversion. The reader now consumes the actual preserved `reward.teacher_response.meta_info.input_token_logprobs`, rather than assuming the later-derived `teacher_log_probs` exists. It checks complete input-token coverage and **all prefix/completion IDs**, including the first tuple whose logprob is `None`, then uses native `_trim_input_field` for response-only scoring. Prefix probabilities never enter the metrics. Original masks and missing/nonfinite counts remain visible; both existing unclamped K3 forms are reused.

An explicit `--teacher-ready` binds the head teacher's native readiness file and sibling `student-launch.json`: same job/pair/image, recorded output-root/pair/job, expected distinct teacher model, startup `model_info.model_path`, server argv and the sample's actual scoring URL. Missing/mismatched identity yields an incomplete diagnostic. Relocated copies without origin proof are not accepted as the recorded run.

Probability semantics are labeled **`source_and_launch_contract_derived`**. The exact task-pinned SGLang source `056f871a7ee8b4573832049011f0fdf52589cfd8` implements full-vocabulary input-token log-softmax; the actual task producer uses a deterministic prefill-only request. This is not a per-response request, kernel or teacher-weight-version receipt. No such missing fields are invented. Source reference: [native logprob processor](https://raw.githubusercontent.com/sgl-project/sglang/056f871a7ee8b4573832049011f0fdf52589cfd8/python/sglang/srt/layers/logprob_processor.py).

## CPU execution

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python 3.12.13. All files/caches remained in the approved local temporary root. The implementation agent's exact final command was:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest \
tests/fast/test_qwen35_monitoring.py tests/fast/test_qwen35_opd_launcher.py \
-q -p no:cacheprovider \
--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-teacher-prefix-combined-$(date +%s)-$$
```

The affected teacher run used the same modules with `-k teacher` and a separate temporary directory. Observed/reported results:

| Check | Expected | Result | Evidence owner |
| --- | --- | --- | --- |
| Parent integration before prefix repair | Reader/launcher regression pass | 96 passed, 22 warnings, 52.55 s | Parent; raw log `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-teacher-combined-20261107.log` |
| Prefix regression before repair | Placeholder/ordinary prefix corruption must invalidate the diagnostic | 2 failed, reproducing the missing identity check | Implementation agent |
| Teacher subset after repair | Valid raw producer path works; corruption is incomplete | 29 passed, 14.28 s | Implementation agent |
| Final complete reader + launcher | All existing/new cases pass together | 98 passed (55 reader + 43 launcher), 52.68 s | Implementation agent |
| Scoped diff whitespace | No malformed whitespace | PASS | Implementation agent and parent |

Fixtures invoke actual `qwen_alignment.score_teacher` and native `Sample.to_dict()`, preserving the real nested response layout. The new prefix regression changes exactly one ID at positions 0/1, leaves completion IDs intact, verifies teacher `INCOMPLETE`, and verifies D8 decode/prefill stay `PASS`. Native typed writer fixtures continue to cover publication/version/update evidence. No fixture is represented as a GPU/model result.

## Phase review

Implementation owner: `ses_e4e739140ffeErr0KEUsX8tYbe` (`QWEN-P2-TEACHER-DIAGNOSTIC`). Reviewer: `ses_e4e792d5affeGsj3IUWlUanlWV`. Inspected the two changed files, requirements/plan and actual producer/worker contracts; final frozen diff: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/QWEN-P2-TEACHER-DIAGNOSTIC.diff`.

The initial review found one P2: checking completion IDs alone could accept a teacher response conditioned on a different prefix. The implementation now validates the complete raw ID vector before slicing (`inspect_qwen35.py:437–443`); the focused regression is at `test_qwen35_monitoring.py:514–541`. Parent inspected these exact lines. Final reviewer closure: **P2 CLOSED; no remaining actionable finding in this phase**. The reviewer adopted the recorded CPU results and did not independently execute tests.

## Native use and limits

Run the existing inspector against the native personal-cloud run directory, its frozen `population.json`, and the matching local rendezvous file:

```bash
python -m tests.manual.agent_opd.inspect_qwen35 \
  --run-dir "$RUN_DIRECTORY" \
  --population-report "$FROZEN_POPULATION/population.json" \
  --teacher-ready "$SHARED_DIR/$RJOB_NAME/$PAIR/teacher-ready.json" \
  --report "$REPORT_JSON"
```

**CPU contract PASS; native confirmation unfinished.** These changes do not touch live generation/training producers, alter the three queued jobs, grant D8 acceptance, or demonstrate learning improvement. Baseline-only probes still lack the required updated/final publication evidence for complete D8 PASS. Actual results, successful-update counts and final text-HF reload remain pending.
