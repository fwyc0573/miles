## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record the already-executed unsalted native reproduction and a correctly scoped post-run red signal; distinguish artifact checking from native inference and retain the initial checker-schema error. |

# Unsalted teacher warm-correctness feedback

## Result

The existing unsalted A/B r3 native workload reproduces the teacher warm discrepancy. The correctly scoped post-run check below returns **FAIL / exit1 for both pairs**: cold full-versus-response equality is4/4; every checked warm relation is1/4. This is the expected red correctness signal, not an auxiliary collector failure.

The native driver has already executed the real inference path. The post-run command only reads its comparisons; it does not drive inference, establish a source-code regression seam, or prove any fix. The accepted local K/V numerical differences at `e2ab706a` are separate observations, not the warm green predicate.

## Existing native loop and bounded minimization

Task: `task_2026-11-08_qwen35_full_kl_nll`. Existing worker entry: `tests.manual.agent_opd.probe_teacher_scoring`; controller: `tests.manual.agent_opd.submit_teacher_scoring_probe`.

- Actual r3 jobs: A `exp-1111-194637-456465`, B `exp-1111-194636-897299`; both Succeeded with retained comparisons. Job success is not warm correctness.
- Existing config: `teacher_scoring_kv_coherence_probe_config.json`; sample manifest: `teacher_scoring_runtime_metadata_first4_manifest.json`. Each pair uses4 H800, one repetition,16 requests and10 flushes, without namespace salt.
- The actual historical controller commands are recorded at `test_report_2026-11-11_kv_coherence_r3_submission.md:25–26`; admission receipts retain their worker commands. These old output paths are read-only and must not be resubmitted or overwritten.
- Source owner `probe_teacher_scoring.py:253–259` constructs full and response-only requests from the same tokens. `:459–493` generates cache history: cold flushes before each sample/mode; warm flushes once per mode stream and preserves sample order. `:433–456` records comparisons; `:728` enforces the original first4/repetition0 coherence protocol.
- The four retained input/response lengths are97365/734,98312/246,98942/431,99074/290. Source-backed KV qualification uses sample1695's `[90112,98067)` overlap. No further reduction was executed. First4 is the smallest published and currently authorized diagnostic form, **not a demonstrated minimal reproduction in which every case is load-bearing**.

The reproduced native loop is deterministic at the observed comparison signature across the original runtime-metadata and r3 unsalted runs. Its business request span was reported by the read-only exploration as approximately91s/A and64.8s/B, with model load/allocation included in approximately10.3min/A and8.3min/B wall time. No timing measurement was rerun here, and these values are not a performance-cause verdict. The diagnosing-bugs fast-loop/minimization steps are therefore explicitly limited: native model/context cost and the fixed first4 qualification protocol prevent claiming a seconds-long or further-minimized native loop. A loaded-server replay or smaller protocol would need its own qualification; neither was introduced.

## Exact post-run command

Workspace: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`; `/usr/bin/python3`3.10.6, no conda activation. Timeout60s. Only eight small comparison records per pair are read; no Torch/SGLang/native import, new GPU run, auth/API/SSH/cloud action, raw K/V replay, source edit or test suite.

For a later approved fix run, the existing native driver must execute again into new output paths before applying the same unchanged comparison predicates to those outputs. Reading today's red archive again cannot validate a fix. Source/baseline verification assertions that intentionally expect warm1/4 are not green fix gates; the salted-namespace inspector is also not an unsalted green gate.

```bash
timeout 60s env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
import json
from pathlib import Path
root=Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/native')
failed=False
for pair in ('A','B'):
    rows=[json.loads(line) for line in (root/pair/f'admission-{pair}-r3/comparisons.jsonl').read_text().splitlines() if line]
    cold=[row for row in rows if row['phase']=='cold']
    warm=[row for row in rows if row['phase']=='warm_stream']
    assert len(cold)==len(warm)==4, 'The original first4 comparison population is required.'
    counts={
        'cold_full_vs_response_only':sum(row['full_vs_response_only']['values_exact'] is True for row in cold),
        'warm_full_vs_response_only':sum(row['full_vs_response_only']['values_exact'] is True for row in warm),
        'cold_full_vs_warm_full':sum(row['cold_reference']['cold_full_vs_warm_full']['values_exact'] is True for row in warm),
        'cold_response_only_vs_warm_response_only':sum(row['cold_reference']['cold_response_only_vs_warm_response_only']['values_exact'] is True for row in warm),
    }
    green=all(value==4 for value in counts.values())
    print(json.dumps({'pair':pair,'expected_exact_per_relation':4,'actual_exact':counts,'warm_correctness':'PASS' if green else 'FAIL'},sort_keys=True))
    failed |= not green
raise SystemExit(1 if failed else 0)
PY
```

## Expected and observed

| Predicate | Required green | Actual A | Actual B | Disposition |
| --- | --- | --- | --- | --- |
| Original population |4 cold and4 warm comparisons |4 /4 |4 /4 | PASS |
| Cold full versus response-only |4 exact |4 |4 | PASS |
| Warm full versus response-only |4 exact |1 |1 | FAIL |
| Cold full versus warm full |4 exact |1 |1 | FAIL |
| Cold response-only versus warm response-only |4 exact |1 |1 | FAIL |
| Checker exit |0 only when all relations are green |1, printed FAIL |1, printed FAIL | Expected red |

Initial attempt: **checker-schema FAIL before a correctness verdict**, `KeyError: 'cold_response_vs_warm_response'`. The initial checker used an abbreviated field name rather than the actual schema. `probe_teacher_scoring.py:442–447` shows the existing key is `cold_response_only_vs_warm_response_only`. The sole correction was that literal field lookup, with no fallback or source/runtime change. The corrected command above was then executed and printed the actual4/1/1/1 signature for each pair. The initial exception is not evidence of a native failure or a successful red-capable correctness check.

## Next causal work and limits

Four hypotheses were shown to the user before the subsequent read-only source investigation: FULL-to-OLD rebinding with a FRESH recurrent trajectory; erroneous live varlen checkpoint donor despite accepted equal-length FP32 operator tests; correct initial state but chunk/shape arithmetic divergence; earlier historic payload overwrite. The source investigator owns the actual FULL/recurrent handoff ledger and necessary distinguishing evidence. No cause is selected by this post-run check.

The accepted original physical/FRESH/source ordering/lifetime qualifications remain closed; no new raw-index/hash/paired-event/descriptor/allTP gate follows. Optional salted namespace is not adopted as a fix. No cache fallback, synchronization, epsilon, science change or source fix was made. Formal04/05 remain HOLD,06 requires each independent200-update result, and B does not wait for A200.
