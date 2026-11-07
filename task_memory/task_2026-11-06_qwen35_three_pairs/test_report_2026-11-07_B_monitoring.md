## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Parent links subsequent independent final-HF PASS without changing this report's numerical-analysis scope. |
| 2026-11-07 | Extract six actual B monitoring checkpoints, verify reported denominators and weighted means, and distinguish sampled diagnostics from learning qualification. |

# B: actual six-checkpoint monitoring

Task ID: `QWEN-P3-B-MONITOR-CURVES`.

**Result:** the supplied completion inspector reports **D8 PASS at all six checkpoints**, including version 100. All 144 monitoring completions are present; all 26,728 original eligible completion tokens have finite decode, prefill and teacher comparisons. Monitoring TIS retention is 100% throughout. Sampled teacher/student differences are numerically smaller at the final checkpoint than baseline, but **convergence and capability improvement are not demonstrated**.

## Evidence and acceptance scope

Authoritative numerical input: [completion-inspection-B-exp-1107-173758-806531-2102.json](evidence/completion-inspection-B-exp-1107-173758-806531-2102.json), schema 1, supplied inspector task ID `QWEN-P2-NUMERIC-REPORT`. This is the completed H200 run `exp-1107-173758-806531`, Qwen3.5-4B student / Qwen3.5-35B-A3B frozen teacher. The recorded cloud run path is `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/B/exp-1107-173758-806531`; **no cloud path was accessed by this analysis**.

Criteria: [requirements.md](requirements.md), D8/D9/D12/D17, and [design.md](design.md), numerical acceptance and first training-effectiveness budget. Metric implementation references: `tests/manual/agent_opd/inspect_qwen35.py:288–360,449–483,522–611`.

| Requirement | Observed result | Qualification boundary |
| --- | --- | --- |
| D8 | Inspector PASS, six checkpoints; both comparisons and all three length strata below 0.03; no reported issues. | Local extraction/reduction cross-check, not independent replay of raw native artifacts or layer-level diagnosis. |
| D9 | 24 fixed prefixes × 6 checkpoints = 144 actual monitoring completions; 100 successful / 0 skipped updates; final publication version 100. | The report establishes update counters/publications, not an independent audit of all 800 training completions or their exclusion rules. |
| D12 | Inclusive `[0.5,2]` monitoring ratio check; 26,728/26,728 retained; D8 uses the original population. | Read-only monitoring retention does not independently prove training importance-weight application or distributed original-token normalization. |

### Exact restart accounting and coverage

D17 retains **one discarded historical B optimizer update and version 1 publication**, then authorizes **one fresh 100-update run from initial weights**. The new run succeeds 100 times and skips 0; historical B optimizer updates therefore total **1 + 100 = 101**, while the accepted new run's final version is **100**, not 101. Its version 0 is a fresh baseline, not a continuation of the discarded version 1. D9's new-run training budget is 800 completions, plus 144 held-out monitoring completions; neither failed sample attempts nor monitoring forwards add optimizer updates. The old discarded update is documented by D17, not remeasured here.

Each row below has the same 24 source UIDs, with 8 short / 8 medium / 8 long prefixes. The frozen prefix strata are `(0,32768]`, `(32768,65536]`, `(65536,122880]`. Token counts are completion targets, **not prefix lengths**.

| Successful updates / consumed version | Inspector rollout ID | Original eligible tokens | Short / medium / long tokens |
| --- | --- | --- | --- |
| 0, baseline | 0 | 4,828 | 635 /2,664 /1,529 |
| 20 | 19 | 4,185 | 717 /1,946 /1,522 |
| 40 | 39 | 4,793 | 650 /2,920 /1,223 |
| 60 | 59 | 3,986 | 579 /2,215 /1,192 |
| 80 | 79 | 4,675 | 1,026 /1,750 /1,899 |
| 100 | 99 | 4,261 | 958 /2,122 /1,181 |

The report's baseline rollout ID 0 and first training rollout ID 0 are different record types. Monitoring versions are established from consumed-version receipts; they are not inferred from rollout IDs. The new-run publication list has 100 entries with rollout IDs 0–99, successful-counter delta 1 each, and published versions 1–100.

## Teacher/student sampled-token curves

Here `d = log p_teacher - log q_student_decode`, `r = exp(d)`, `A = r*d-r+1`, and `B = r-1-d`. Tokens were sampled by the current student with temperature 1 / top-p 1 / top-k −1. A is the teacher-to-student directional form and B the student-to-teacher form under student sampling; these are **sample averages**, not exact full-vocabulary KL measurements. Prefill comparisons elsewhere also use these same decode-sampled tokens.

All means in the next table are original-token-weighted. `|d|` is a cross-model sampled logprob gap, not D8's same-student numerical error.

| Updates | Mean `|d|` | Short / medium / long mean `|d|` | Mean A | Mean B |
| --- | --- | --- | --- | --- |
| 0 | 0.238532 | 0.232578 /0.201024 /0.306356 | 0.113690 | 0.116514 |
| 20 | 0.213942 | 0.178000 /0.228472 /0.212295 | 0.403874 | 0.168733 |
| 40 | 0.168951 | 0.147067 /0.173692 /0.169262 | 0.091004 | 0.086758 |
| 60 | 0.178713 | 0.140293 /0.172016 /0.209819 | 0.100517 | 0.087627 |
| 80 | 0.169484 | 0.175621 /0.152068 /0.182217 | 0.110646 | 0.089796 |
| 100 | 0.171754 | 0.177050 /0.147229 /0.211526 | 0.091343 | 0.083570 |

Equal-prefix aggregation and completion-length changes provide a separate view; the ranges below describe heterogeneity, **not confidence intervals**.

| Updates | Equal-prefix mean `|d|` | Per-prefix mean `|d|` range | Mean completion tokens | Completion token range |
| --- | --- | --- | --- | --- |
| 0 | 0.231965 | 0.018615–0.399496 | 201.17 | 33–875 |
| 20 | 0.192914 | 0.010984–0.381088 | 174.38 | 32–723 |
| 40 | 0.179751 | 0.010102–0.515687 | 199.71 | 28–1,303 |
| 60 | 0.177454 | 0.009484–0.348058 | 166.08 | 53–775 |
| 80 | 0.158099 | 0.010841–0.324629 | 194.79 | 26–731 |
| 100 | 0.173553 | 0.009518–0.374682 | 177.54 | 26–646 |

Baseline→final, 19 of 24 matched prefixes have lower sampled mean absolute gaps and 5 have higher gaps; the mean paired change is −0.058412. Both global directional forms are lower at final than baseline, but A rises at update 20 and neither later curve decreases monotonically. These observations concern fresh, different completions on fixed prefixes, with changing token/length mixtures. No repeated-completion uncertainty estimate, group-aware confidence interval, task execution, correctness reward or capability benchmark is present; statistical significance and general learning improvement remain unqualified.

## Same-student mismatch and TIS

For D8/TIS, `d = log p_student_train - log q_student_inference`. Decode and same-token prefill remain separate. Every populated stratum at every checkpoint passes the declared 0.03 mean threshold; the largest stratum means are 0.014273 (decode, baseline long) and 0.013822 (prefill, baseline short).

| Updates | Decode mean `|d|` | Decode short / medium / long | Prefill mean `|d|` | Prefill short / medium / long |
| --- | --- | --- | --- | --- |
| 0 | 0.010981 | 0.012289 /0.008780 /0.014273 | 0.010793 | 0.013822 /0.008464 /0.013593 |
| 20 | 0.009085 | 0.009122 /0.008808 /0.009422 | 0.009773 | 0.009685 /0.009567 /0.010079 |
| 40 | 0.006710 | 0.006873 /0.006363 /0.007451 | 0.006725 | 0.007169 /0.006282 /0.007545 |
| 60 | 0.007609 | 0.007448 /0.007396 /0.008082 | 0.007299 | 0.008006 /0.006778 /0.007924 |
| 80 | 0.007076 | 0.007497 /0.005825 /0.008000 | 0.007050 | 0.007896 /0.005619 /0.007911 |
| 100 | 0.006872 | 0.007258 /0.006063 /0.008013 | 0.006802 | 0.007500 /0.005984 /0.007704 |

Tail errors remain visible; there is no accepted hard threshold for tails or K3 terms.

| Updates | Decode p95 /p99 /max | Prefill p95 /p99 /max | Monitoring decode-ratio enclosure | Retained /original |
| --- | --- | --- | --- | --- |
| 0 | 0.072115 /0.120530 /0.352969 | 0.073524 /0.119398 /0.299569 | [0.702599,1.423287] | 4,828/4,828 |
| 20 | 0.064346 /0.120116 /0.469255 | 0.069690 /0.117149 /0.236505 | [0.625468,1.598803] | 4,185/4,185 |
| 40 | 0.046127 /0.111387 /0.249888 | 0.047930 /0.112380 /0.249890 | [0.778888,1.283882] | 4,793/4,793 |
| 60 | 0.055470 /0.116290 /0.220543 | 0.053069 /0.116418 /0.234866 | [0.802083,1.246753] | 3,986/3,986 |
| 80 | 0.051222 /0.114378 /0.253771 | 0.051057 /0.113749 /0.249768 | [0.775869,1.288877] | 4,675/4,675 |
| 100 | 0.048949 /0.110695 /0.221943 | 0.047742 /0.109723 /0.234081 | [0.800961,1.248500] | 4,261/4,261 |

**Enclosure, not observed extrema:** the ratio interval is `exp([-max|d|,+max|d|])`, derived from each decode maximum absolute error. The supplied JSON retains only the five worst tokens per summary, not the complete ratio distribution; exact ratio means/quantiles/min/max cannot be reconstructed. All enclosure bounds lie inside inclusive `[0.5,2]`; the report separately records 100% measurable-token retention. These ratios are student-train/student-decode ratios, **not teacher/student ratios**.

The largest decode discrepancy is version 20, source UID `cd24a887eb3d3f1c0139415b3956d25a3c9fc1b95ec3af7fb56ffff34669cceb:424:168`, sample 15, response position 49 / absolute position 61,464, token 16: delta −0.4692549706, ratio 0.6254680869, retained. The largest prefill discrepancy is baseline, source UID `cd24a887eb3d3f1c0139415b3956d25a3c9fc1b95ec3af7fb56ffff34669cceb:306:158`, sample 11, response position 794 / absolute position 57,721, token 976: delta −0.2995694876, ratio 0.7411372208. The source report preserves additional tail-token coordinates.

Final same-student A/B means are 0.000243976 / 0.000245214 for decode and 0.000245546 / 0.000245083 for prefill. These are unclamped directional diagnostics; the extraction command below also emits all six checkpoints' values.

### Denominator and evidence limits

- All 144 rows have `expected_valid_tokens == response_tokens`; all 26,728 response positions are original eligible targets here. Decode, prefill and teacher finite comparison counts match this denominator. Prefix tokens are not counted; no survivor-token replacement is used.
- Across all checkpoints/strata, unknown denominators, zero-target samples, missing valid tokens, nonfinite valid tokens, nonfinite differences, nonfinite unclamped K3 terms, and missing/nonfinite masked positions are all 0. Sample and checkpoint issue lists are empty. The 144 rows are repeated measurements of 24 prefixes, not 144 independent inputs.
- Teacher identity/probability semantics are established by startup/launch contract and source (`full_vocabulary_log_softmax`), not per-response request fields, model revision or consumed teacher-version receipts. The source report explicitly marks that boundary; no stronger receipt is invented here.
- These monitoring curves neither reproduce every-step loss/gradient behavior nor audit training TIS numerator/denominator arithmetic. 100% retention on this population cannot test the distinction between original-token and survivor-token normalization.
- This analysis does not qualify HF reload. The parent subsequently records independent final-HF PASS in [the HF report](test_report_2026-11-07_hf_reload.md), job`exp-1107-211800-115424`. No HF source analysis, platform/GPU/SSH/cloud access, job control, delegation or new experiment was performed by this analysis owner. Only this report was added; shared task status documents remain parent-owned.

## Exact local extraction and verification

Environment: working directory `/data/ycfeng/sota-engine/miles`, Linux host, `python3` 3.10.6 (`main, Nov 14 2022, 16:10:14`, GCC 11.3.0); standard library only. No Torch/model load or new experiment is required.

The following read-only command extracts full-precision curves and validates coverage, update accounting, denominator counts and recomputed sample-weighted means/K3 values. It writes no file.

```bash
python3 - <<'PY'
import collections, json, math, pathlib, statistics, sys
p = pathlib.Path('task_memory/task_2026-11-06_qwen35_three_pairs/evidence/completion-inspection-B-exp-1107-173758-806531-2102.json')
d = json.loads(p.read_text())
strata = ('overall', 'short', 'medium', 'long')
families = ('decode', 'prefill', 'teacher_student_sampled_divergence')
invalid = ('unknown_denominator_samples', 'missing_or_nonfinite_tokens',
           'zero_target_samples', 'nonfinite_valid_tokens', 'nonfinite_unclamped_k3',
           'nonfinite_logprob_differences', 'nonfinite_masked_positions',
           'missing_valid_tokens', 'missing_masked_positions')
assert d['verdict'] == 'PASS' and not d['issues']
assert d['threshold'] == 0.03 and len(set(d['monitoring_uids'])) == 24
assert [c['rollout_id'] for c in d['checkpoints']] == [0, 19, 39, 59, 79, 99]
assert [c['consumed_weight_versions'] for c in d['checkpoints']] == [[str(i)] for i in range(0, 101, 20)]
w = d['weight_publication']
assert (w['successful_optimizer_updates'], w['skipped_optimizer_updates'],
        w['baseline_weight_version'], w['final_published_weight_version']) == (100, 0, 0, 100)
assert len(w['publications']) == 100
assert [(r['rollout_id'], r['published_version'], r['optimizer_counter_delta'])
        for r in w['publications']] == [(i, i + 1, 1) for i in range(100)]
curves = []
for c in d['checkpoints']:
    rows = c['samples']
    assert c['verdict'] == 'PASS' and not c['issues'] and len(rows) == 24
    assert {r['source_uid'] for r in rows} == set(d['monitoring_uids'])
    assert collections.Counter(r['stratum'] for r in rows) == {'short': 8, 'medium': 8, 'long': 8}
    assert all(not r['issues'] and not r['zero_target'] and
               r['expected_valid_tokens'] == r['response_tokens'] for r in rows)
    for name in families:
        for s in strata:
            r = c[name][s]
            assert not r['issues'] and all(r[f] == 0 for f in invalid)
            assert r['expected_valid_tokens'] == r['compared_finite_tokens']
            assert r['sample_count'] == (24 if s == 'overall' else 8)
            if name != 'teacher_student_sampled_divergence':
                assert r['verdict'] == 'PASS' and r['abs_mean'] <= d['threshold']
        n = c[name]['overall']['expected_valid_tokens']
        sample_name = 'teacher_student' if name == families[-1] else name
        for f in ('abs_mean', 'k3_r_d_minus_r_plus_1', 'k3_r_minus_1_minus_d'):
            value = lambda r: r[f] if f == 'abs_mean' else r[f]['mean']
            actual = math.fsum(value(r['comparisons'][sample_name]) * r['expected_valid_tokens'] for r in rows) / n
            assert math.isclose(value(c[name]['overall']), actual, rel_tol=1e-12, abs_tol=1e-12)
    t = c['tis']
    assert t['bounds_inclusive'] == [0.5, 2.0] and t['acceptance_uses_pre_tis_population']
    assert t['original_valid_tokens'] == t['measurable_tokens'] == t['retained_tokens']
    assert t['retained_fraction_of_measurable'] == 1.0
    prefix_values = [r['comparisons']['teacher_student']['abs_mean'] for r in rows]
    lengths = [r['response_tokens'] for r in rows]
    curves.append({'updates': int(c['consumed_weight_versions'][0]),
                   'rollout_id': c['rollout_id'], 'tis': t,
                   'metrics': {name: {s: {k: v for k, v in c[name][s].items()
                                         if k != 'worst_tokens'} for s in strata} for name in families},
                   'teacher_prefix_mean': statistics.mean(prefix_values),
                   'teacher_prefix_range': [min(prefix_values), max(prefix_values)],
                   'completion_mean': statistics.mean(lengths),
                   'completion_range': [min(lengths), max(lengths)],
                   'decode_ratio_enclosure': [math.exp(-c['decode']['overall']['abs_max']),
                                              math.exp(c['decode']['overall']['abs_max'])]})
assert sum(c['tis']['original_valid_tokens'] for c in d['checkpoints']) == 26728
b = {r['source_uid']: r['comparisons']['teacher_student']['abs_mean'] for r in d['checkpoints'][0]['samples']}
f = {r['source_uid']: r['comparisons']['teacher_student']['abs_mean'] for r in d['checkpoints'][-1]['samples']}
changes = [f[uid] - b[uid] for uid in b]
assert (sum(x < 0 for x in changes), sum(x > 0 for x in changes)) == (19, 5)
print('Python:', sys.version)
print(json.dumps({'curves': curves, 'paired_prefix_mean_change': statistics.mean(changes)}, indent=2))
print('PASS: six checkpoints,144 monitoring completions,26728 finite original tokens,100 new successful updates')
PY
```

Observed verification: **PASS** for all assertions above, including sample-weighted recomputation of absolute-gap and both K3 means across all six checkpoints and three comparison families. Reported table values are rounded only for display. Validation does not independently reconstruct token-level quantiles from the full raw population, since that population is not present in the supplied JSON.
