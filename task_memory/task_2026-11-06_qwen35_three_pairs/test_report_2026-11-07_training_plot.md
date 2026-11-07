## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Append B actual-run extraction, native counter/publication cross-check, unsmoothed plot and early/late-window assessment. |
| 2026-11-07 | Record direct verification of one/three-run plots and preservation of signed raw loss points. |

# Training-curve plotting verification

Scope: D9's final per-pair loss/gradient-norm curves. `tests/manual/agent_opd/plot_training_metrics.py` now accepts repeated `--report LABEL=PATH`, replacing its fixed two-model arguments. It creates two panels per input report and derives y limits from the original values, including negative OPD loss. It does not smooth, rescale or replace points, and no longer prints a hard-coded learning rate.

**Environment:** Python 3.10.6, Matplotlib 3.7.1, CPU/Agg backend. The source fixture `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen35-plot-verification.md` is explicitly marked synthetic and contains:

| Update | Loss | Gradient norm |
| --- | --- | --- |
| 1 | -0.5 | 0.2 |
| 2 | 0.15 | 0.1 |
| 3 | -0.3 | 0.15 |

Executed direct instrumentation:

```bash
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode MPLCONFIGDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen35-plot-cache python3 -B - <<'PY'
import json, runpy, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
root = Path('/data/ycfeng/tmp/opencode-v2-tmp/opencode')
source = root / 'qwen35-plot-verification.md'
original_save = Figure.savefig
captures = []
def inspect_save(figure, path, *args, **kwargs):
    for index, axis in enumerate(figure.axes):
        values = list(axis.lines[0].get_ydata())
        bottom, top = axis.get_ylim()
        assert bottom <= min(values) <= max(values) <= top
        assert list(axis.lines[0].get_xdata()) == [1, 2, 3]
        if index % 2 == 0:
            assert values == [-.5, .15, -.3] and bottom < 0
    original_save(figure, path, *args, **kwargs)
    captures.append({'panels': len(figure.axes), 'bytes': Path(path).stat().st_size})
Figure.savefig = inspect_save
for names in [('one synthetic',), ('A synthetic', 'B synthetic', 'C synthetic')]:
    reports = sum((['--report', f'{name}={source}'] for name in names), [])
    sys.argv = ['plot_training_metrics.py', *reports, '--output', str(root / f'qwen35-plot-{len(names)}.png')]
    runpy.run_module('tests.manual.agent_opd.plot_training_metrics', run_name='__main__')
    assert captures[-1]['panels'] == 2 * len(names)
print(json.dumps({'python': sys.version.split()[0], 'matplotlib': matplotlib.__version__, 'checks': captures}))
PY
```

| Case | Expected | Observed | Result |
| --- | --- | --- | --- |
| One report | Two panels, original x/y values in bounds | Two panels; `qwen35-plot-1.png`, 99,241 bytes | PASS |
| Three reports | Six panels, original x/y values in bounds | Six panels; `qwen35-plot-3.png`, 256,031 bytes | PASS |
| Signed objective | Negative losses visible and unchanged | `[-0.5, 0.15, -0.3]` preserved with negative lower limits | PASS |

Exit 0. Both selected PNGs were retained through the local cleanup follow-up. These are plotting fixtures, **not actual training metrics or learning evidence**. Actual per-step results and final three-pair curves remain pending native execution.

## B actual run — D14 every-step evidence

Task ID: `QWEN-P3-B-TRAINING-CURVES`. This section qualifies the completed H200 run `exp-1107-173758-806531`, Qwen3.5-4B student / Qwen3.5-35B-A3B frozen teacher, independently of the synthetic plotting checks above. The supplied settled stdout is `/data/ycfeng/tmp/opencode-v2-tmp/opencode/B-exp-1107-173758-806531-complete.log`; its recorded original cloud path is `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/B/exp-1107-173758-806531.log`. No cloud, platform, GPU, SSH or authentication operation was performed by this extraction owner, and training was not rerun.

Artifacts: [full-precision extracted records](evidence/B-training-steps.json), [plot-compatible scalar table](evidence/B-training-steps.md), and [actual 100-update PNG](evidence/B-training-curves.png). The JSON retains all recorded train, rollout, rollout-performance and training-performance scalar dictionaries, their rawlog line numbers, and the corresponding native publication IDs/counter deltas. It is derived evidence, not a replacement for native logs/events. Native counter evidence is [completion-inspection-B-exp-1107-173758-806531-2102.json](evidence/completion-inspection-B-exp-1107-173758-806531-2102.json), `weight_publication`; resolved CLI/launch provenance is [launch.json](evidence/first-round/student/B/exp-1107-173758-806531/launch.json).

### Metric meanings and limits

- `train/loss` is the recorded signed policy objective, not a capability score, cross-entropy, or exact KL. `train/pg_loss` equals it on all 100 updates; recorded entropy loss is zero. The source constructs the policy objective in `miles/backends/training_utils/loss/hub/losses.py:304–317,371–377` and OPD advantages in `miles/backends/training_utils/loss/hub/opd.py`. The resolved stdout says `calculate_per_token_loss=True`; `loss/objective.py:129–131,173–184,229–245` and `metrics/log_utils.py:466–517` own original-mask token counting and distributed scalar reduction. Fully masked samples have the native count-of-one convention. This source inspection identifies semantics; the scalar log alone does not independently replay distributed normalization.
- `train/grad_norm` is the global gradient L2 norm **before clipping**, supplied by `optimizer.step()` and passed unchanged to the logger (`miles/backends/megatron_utils/model.py:677–681,894–909`; `miles/backends/training_utils/metrics/log_utils.py:520–575`, explicit parameter contract at line 538). This is not a parameter-update norm. `model.py` increments the model-companion weight counter only after the successful optimizer return; `NORMAL` alone is not used as successful-update evidence.
- Recorded `train/pg_clipfrac` measures PPO objective clipping, not gradient clipping (`loss/hub/math_utils.py:255–278`; `loss/hub/losses.py:304–306`). It is zero on every step. The resolved native **gradient** clipping threshold is `clip_grad=1.0`, stdout line 195. All 100 pre-clipping norms exceed this threshold; gradient clipping is therefore **inferred to be active from the native norm/threshold contract**, not measured by a logged clipping coefficient, post-clipping norm or separate gradient-clipping fraction. Those quantities are absent and are not invented.
- Both recorded optimizer-group LRs, `train/lr-pg_0` and `train/lr-pg_1`, are exactly `2e-6` on all 100 steps. Recorded `train/mis_tis_mask_fraction_low/high` are zero throughout. These are TIS rejection metrics, not PPO clipping or gradient clipping; all other recorded TIS scalar values are retained without relabeling them as exact token counts or global ratio extrema.
- `rollout/num_training_samples=8` and `rollout/response_len/{mean,median,min,max}` are actual recorded generation metrics. The independently logged trainer `rollout/response_lengths` matches the recorded generation mean at every step. Generated response-token totals are **derived** as mean × 8; full-input-token totals similarly use `rollout/total_lengths` × 8 (`metrics/log_utils.py:185–187,255–263,269` logs non-tensor lengths by sum/count). These counts do not by themselves establish original loss-mask target counts or post-TIS survivor counts. Neither count is separately present in stdout. If exact per-step target/retained counts are required, the parent needs `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/B/exp-1107-173758-806531/rollout_data/{i}.pt`, `samples[*].tokens/response_length/loss_mask/weight_versions`, and the same run's `train_data/{i}_{rank}.pt`, `rollout_data.tokens/loss_masks/rollout_mask_sums/log_probs/rollout_log_probs/response_lengths/total_lengths/sample_indices`, plus `cp_rank/cp_size/qkv_format`, for accepted `i=0..99` and unique TP-source ranks `0,2,4,6`. The parent should verify actual field availability, original-mask counts and the declared TIS predicate before aggregation; no substitute counts are asserted here. Paths are confirmed by resolved stdout lines 1223–1224; payload owners are `miles/ray/rollout/debug_data.py:117–149` and `miles/backends/training_utils/metrics/train_dump.py:11–47`, called after training by `megatron_utils/actor.py:986`.

### Exact local extraction, cross-check and plotting command

Working directory `/data/ycfeng/sota-engine/miles`; system `/usr/bin/python3`, Python 3.10.6 (GCC 11.3.0), Matplotlib 3.7.1, CPU/Agg. No conda environment was activated and no model/runtime package was imported. This local analysis environment is not the formal training container. The existing plotter is unchanged.

The comparison windows are fixed here to **successful updates 1–20 and 81–100**, each 20 updates, matching the monitoring cadence and avoiding overlap. This is a retrospective first/last-window assessment of the settled run, not a claim that the windows were registered before training. Window means give each successful update equal weight; they are not pooled token-weighted means. Full-precision per-step signed losses are preserved; no smoothing, absolute-value transform, replacement, normalization or rescaling is applied to either plotted metric.

```bash
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode MPLCONFIGDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen35-plot-cache python3 -B - <<'PY'
import ast, collections, json, math, re, runpy, shlex, statistics, sys
from pathlib import Path
root = Path('task_memory/task_2026-11-06_qwen35_three_pairs')
raw = Path('/data/ycfeng/tmp/opencode-v2-tmp/opencode/B-exp-1107-173758-806531-complete.log')
inspection = root / 'evidence/completion-inspection-B-exp-1107-173758-806531-2102.json'
lines = raw.read_text().splitlines()
buckets = collections.defaultdict(lambda: collections.defaultdict(list))
events = collections.defaultdict(lambda: collections.defaultdict(list))
valid = collections.defaultdict(list)
config = {}
for number, original in enumerate(lines, 1):
    line = re.sub(r'\x1b\[[0-9;]*m', '', original)
    match = re.search(r' - (step|rollout|perf) (\d+): (\{.*\})$', line)
    if match:
        kind, step, literal = match.groups()
        metrics = ast.literal_eval(literal)
        if kind == 'step':
            if 'train/loss' not in metrics:
                continue
            kind = 'train'
        elif kind == 'perf':
            kind = 'rollout_perf' if 'rollout/num_training_samples' in metrics else 'train_perf'
        buckets[kind][int(step)].append((number, metrics))
    if 'audit op=event event=' in line:
        fields = dict(token.split('=', 1) for token in shlex.split(line.split('audit ', 1)[1]) if '=' in token)
        kind = fields['event']
        if kind in ('WeightUpdateResultEvent', 'TrainGroupStepEndEvent') and fields.get('rollout_id', '').isdigit():
            events[kind][int(fields['rollout_id'])].append((number, fields))
    match = re.search(r'train op=train_step rollout=(\d+) step=0 attempt=0 outcome=(\w+) valid_step=(\w+)', line)
    if match:
        valid[int(match[1])].append((number, match[2], match[3]))
    match = re.match(r'\s+(clip_grad|calculate_per_token_loss)\s+\.+\s+(\S+)\s*$', line)
    if match:
        config[match[1]] = {'raw_value': match[2], 'stdout_line': number}
assert config['clip_grad']['raw_value'] == '1.0'
assert config['calculate_per_token_loss']['raw_value'] == 'True'
w = json.loads(inspection.read_text())['weight_publication']
assert w['verdict'] == 'PASS' and not w['issues']
assert (w['successful_optimizer_updates'], w['skipped_optimizer_updates'],
        w['baseline_weight_version'], w['final_published_weight_version']) == (100, 0, 0, 100)
assert len(w['publications']) == 100
for kind in ('train', 'rollout', 'rollout_perf', 'train_perf'):
    assert sorted(buckets[kind]) == list(range(100)), kind
for kind in ('WeightUpdateResultEvent', 'TrainGroupStepEndEvent'):
    assert sorted(events[kind]) == list(range(100)), kind
assert sorted(valid) == list(range(100))
steps = []
for step, publication in enumerate(w['publications']):
    row = {'successful_update': step + 1, 'rollout_id': step, 'stdout_lines': {}}
    for kind in ('train', 'rollout', 'rollout_perf', 'train_perf'):
        records = buckets[kind][step]
        assert len(records) == (2 if kind == 'train' else 1), (kind, step)
        assert all(record[1] == records[0][1] for record in records)
        assert all(isinstance(v, (int, float)) and math.isfinite(v) for v in records[0][1].values())
        row[kind] = records[0][1]
        row['stdout_lines'][kind] = [record[0] for record in records]
    train, rollout, generation = row['train'], row['rollout'], row['rollout_perf']
    assert train['train/step'] == train['rollout/step'] == step
    assert train['train/loss'] == train['train/pg_loss'] and train['train/entropy_loss'] == 0
    assert train['train/grad_norm'] > 0
    assert train['train/lr-pg_0'] == train['train/lr-pg_1'] == 2e-6
    assert generation['rollout/num_training_samples'] == 8
    assert rollout['rollout/response_lengths'] == generation['rollout/response_len/mean']
    assert generation['rollout/weight_version/min'] == generation['rollout/weight_version/max'] == step
    assert generation['rollout/weight_version/prefill_min'] == generation['rollout/weight_version/prefill_max'] == step
    assert generation['rollout/weight_version/mixed_version_ratio'] == 0
    assert generation['rollout/weight_version/prefill_mixed_version_ratio'] == 0
    assert all(outcome == 'NORMAL' and flag == 'true' for _, outcome, flag in valid[step])
    row['stdout_lines']['valid_step'] = [record[0] for record in valid[step]]
    row['publication'] = publication
    assert (publication['rollout_id'], publication['candidate_version'],
            publication['published_version'], publication['optimizer_counter_delta']) == (step, step + 1, step + 1, 1)
    for kind in ('WeightUpdateResultEvent', 'TrainGroupStepEndEvent'):
        records = events[kind][step]
        assert len(records) == 1
        number, fields = records[0]
        row['stdout_lines'][kind] = [number]
        if kind == 'WeightUpdateResultEvent':
            assert int(fields['candidate_version']) == int(fields['published_version']) == step + 1
            assert fields['debug_weight_update_id'] == publication['debug_weight_update_id']
            assert not fields['failed_cell_ids'] and len(fields['updated_cell_ids'].split(',')) == 4
        else:
            assert fields['attempt'] == '0' and fields['role'] == 'actor'
            assert json.loads(fields['cell_outcomes']) == {'0': ['normal'] * 8}
    row['derived'] = {
        'generated_response_tokens': generation['rollout/response_len/mean'] * 8,
        'full_input_tokens': rollout['rollout/total_lengths'] * 8,
        'preclip_norm_above_native_threshold': train['train/grad_norm'] > float(config['clip_grad']['raw_value']),
    }
    assert all(float(row['derived'][key]).is_integer() for key in ('generated_response_tokens', 'full_input_tokens'))
    steps.append(row)
windows = {}
metrics = ('train/loss', 'train/grad_norm')
for label, start, end in (('early', 1, 20), ('late', 81, 100)):
    selected = steps[start - 1:end]
    window = {'successful_updates_inclusive': [start, end], 'count': len(selected)}
    for key in metrics:
        values = [row['train'][key] for row in selected]
        window[key] = {'mean': statistics.mean(values), 'median': statistics.median(values),
                       'sample_std': statistics.stdev(values), 'min': min(values), 'max': max(values)}
    window['generated_response_tokens'] = sum(row['derived']['generated_response_tokens'] for row in selected)
    window['mean_response_tokens_per_completion'] = window['generated_response_tokens'] / (20 * 8)
    window['mean_full_input_tokens_per_completion'] = statistics.mean(row['rollout']['rollout/total_lengths'] for row in selected)
    windows[label] = window
comparison = {key: {'late_minus_early_mean': windows['late'][key]['mean'] - windows['early'][key]['mean'],
                    'relative_mean_change': windows['late'][key]['mean'] / windows['early'][key]['mean'] - 1}
              for key in metrics}
summary = {
    'successful_updates': 100, 'skipped_updates': 0, 'training_completions': 800,
    'generated_response_tokens': sum(row['derived']['generated_response_tokens'] for row in steps),
    'full_input_tokens': sum(row['derived']['full_input_tokens'] for row in steps),
    'finite_recorded_scalars': True, 'preclip_norm_above_threshold_steps': sum(row['derived']['preclip_norm_above_native_threshold'] for row in steps),
    'metric_ranges': {key: [min(row['train'][key] for row in steps), max(row['train'][key] for row in steps)]
                      for key in metrics + ('train/pg_clipfrac', 'train/mis_tis_mask_fraction_low', 'train/mis_tis_mask_fraction_high')},
    'extrema_updates': {key: {'min': min(steps, key=lambda row: row['train'][key])['successful_update'],
                             'max': max(steps, key=lambda row: row['train'][key])['successful_update']} for key in metrics},
}
output = {'schema_version': 1, 'task_id': 'QWEN-P3-B-TRAINING-CURVES', 'run_id': 'exp-1107-173758-806531',
          'raw_stdout': str(raw), 'raw_stdout_bytes': raw.stat().st_size, 'raw_stdout_lines': len(lines),
          'native_inspection': str(inspection), 'resolved_native_config': config,
          'summary': summary, 'windows': windows, 'comparison': comparison, 'steps': steps,
          'limits': ['Original loss-mask token and post-TIS survivor counts are not separately recorded in stdout.',
                     'Gradient clipping activity is threshold-derived; coefficient/postclip norm are not recorded.',
                     'Update norms and independent raw tensor replay are not provided.',
                     'Window changes do not establish convergence or capability improvement.']}
json_path = root / 'evidence/B-training-steps.json'
md_path = root / 'evidence/B-training-steps.md'
png_path = root / 'evidence/B-training-curves.png'
json_path.write_text(json.dumps(output, indent=2, allow_nan=False) + '\n')
table = ['## Modification History', '', '| Date | Change |', '| --- | --- |',
         '| 2026-11-07 | Extract the completed B run\'s 100 signed loss/pre-clipping gradient-norm records. |', '',
         '# B actual training-step scalars', '', 'Task ID: `QWEN-P3-B-TRAINING-CURVES`.', '',
         'Run: `exp-1107-173758-806531`; Qwen3.5-4B student / Qwen3.5-35B-A3B frozen teacher.', '',
         'Generated by the exact command in [the training-plot report](../test_report_2026-11-07_training_plot.md#exact-local-extraction-cross-check-and-plotting-command).',
         'Source/counter/line references, LR, recorded clipping/TIS/token metrics and window statistics: [B-training-steps.json](B-training-steps.json).',
         'Update is the successful optimizer counter, matched to publication; raw stdout step IDs are zero-based.',
         'Values below preserve the recorded signed floats without smoothing; gradient norm is before clipping.', '',
         '| Update | Loss | Gradient norm |', '| --- | --- | --- |']
table.extend(f"| {row['successful_update']} | {row['train']['train/loss']!r} | {row['train']['train/grad_norm']!r} |" for row in steps)
md_path.write_text('\n'.join(table) + '\n')
from tests.manual.agent_opd.plot_training_metrics import read_training_metrics
updates, losses, norms = read_training_metrics(md_path)
assert updates == list(range(1, 101))
assert losses == [row['train']['train/loss'] for row in steps]
assert norms == [row['train']['train/grad_norm'] for row in steps]
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
save = Figure.savefig
captures = []
def inspect_save(figure, path, *args, **kwargs):
    assert len(figure.axes) == 2
    for axis, expected in zip(figure.axes, (losses, norms), strict=True):
        assert len(axis.lines) == 1
        assert list(axis.lines[0].get_xdata()) == updates
        assert list(axis.lines[0].get_ydata()) == expected
        low, high = axis.get_ylim()
        assert low <= min(expected) <= max(expected) <= high
    captures.append({'panels': 2, 'points_per_panel': 100, 'exact_x_y_match': True})
    save(figure, path, *args, **kwargs)
Figure.savefig = inspect_save
sys.argv = ['plot_training_metrics.py', '--report', f'B Qwen3.5-4B / 35B-A3B={md_path}', '--output', str(png_path)]
runpy.run_path('tests/manual/agent_opd/plot_training_metrics.py', run_name='__main__')
assert len(captures) == 1 and png_path.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
print(json.dumps({'python': sys.version, 'matplotlib': matplotlib.__version__, 'summary': summary,
                  'windows': windows, 'comparison': comparison, 'plot_check': captures[0],
                  'artifact_bytes': {str(p): p.stat().st_size for p in (json_path, md_path, png_path)}}, indent=2))
PY
```

### Observed validation and early/late comparison

**Every-step extraction and actual plotting: PASS.** The corrected exact command above exits 0. The initial instrumented execution also passed every scalar/plot check but emitted a `runpy` warning because the reader module was imported and then executed again with `run_module`; the final invocation uses the same unchanged file through `run_path` and removes that double-module-execution warning. No warning was suppressed and no training behavior changed.

| Check | Expected | Observed | Result |
| --- | --- | --- | --- |
| Actual loss/norm coverage | One unchanged scalar pair per successful update, 1–100 | 200 native train log lines form 100 exactly equal duplicate pairs; source steps 0–99; all recorded scalar dictionaries finite; every norm positive | PASS |
| Update/publication binding | Successful native counter delta 1 per accepted position, 0 skips; version chain 0→100 | 100 publication IDs agree with raw stdout; 100 `TrainGroupStepEndEvent` records, eight NORMAL ranks and attempt 0 each; explicit valid-step logs; inspector counter delta 1 each, 100 successful/0 skipped | PASS |
| Sample and consumed-version coverage | Eight accepted completions per update; decode/prefill version agrees with its optimizer input | 800 recorded training completions; every decode and prefill min/max equals the preceding version 0–99; mixed-version ratios zero | PASS |
| Recorded loss sign/range | Preserve source floats, including any negative values | Actual B losses are all positive, range 0.038783707034891625–0.13518331948812906; no absolute-value transform; minimum update 54, maximum update 11 | PASS |
| Gradient-norm evidence | Finite positive pre-clipping L2 norm per step | Range 5.504546642303467–27.27955436706543; minimum update 54, maximum update 40; all 100 above native threshold 1.0 | PASS; gradient-clipping activity inferred, not separately measured |
| Recorded LR / PPO clipping / TIS rejection | Retain actual native values and metric meanings | Both LRs 2e-6 throughout; PPO `pg_clipfrac=0`; TIS low/high mask fractions 0 throughout | PASS at recorded-scalar scope |
| Recorded generation token metrics | Match two producers and preserve lengths | Mean response lengths agree at all 100 steps; derived generated responses total 201,819 tokens; derived full inputs total 67,054,178 tokens | PASS at generation-length scope; exact target/retained counts not independently verified |
| Actual plot | Two panels with all 100 exact x/y points visible, no smoothing | Direct `Figure.savefig` inspection matches every x/y point to the rawlog-derived records and checks y limits; PNG 159,527 bytes | PASS |

The JSON and Markdown artifacts are 602,137 and 5,792 bytes respectively. First/last recorded loss is `0.06751072660405585` / `0.1091815921140828`; first/last norm is `8.028100967407227` / `8.230230331420898`. These endpoints and the extrema do not establish a trend by themselves.

| Metric | Early updates 1–20 | Late updates 81–100 | Late minus early mean |
| --- | --- | --- | --- |
| Signed loss mean | 0.09503196449625496 | 0.09451090890782819 | −0.000521055588426772 (−0.5483%) |
| Signed loss median | 0.08954321925441958 | 0.09429929844325823 | Not a mean comparison |
| Signed loss sample std | 0.022646379356746415 | 0.019011470643433333 | Descriptive dispersion, not uncertainty |
| Signed loss range | 0.053976882980669376–0.13518331948812906 | 0.0661633755144433–0.1246475909389345 | Overlapping ranges |
| Pre-clipping norm mean | 10.410051202774047 | 9.391944885253906 | −1.0181063175201412 (−9.7800%) |
| Pre-clipping norm median | 10.515270709991455 | 8.818060874938965 | Not a mean comparison |
| Pre-clipping norm sample std | 2.6365953126549475 | 3.141316106266618 | Descriptive dispersion, not uncertainty |
| Pre-clipping norm range | 6.017617225646973–15.537980079650879 | 5.830111503601074–18.38568115234375 | Overlapping ranges |
| Generated response tokens, 160 completions/window | 42,712 | 43,722 | +1,010 tokens |
| Mean response tokens/completion | 266.95 | 273.2625 | +6.3125 tokens |
| Mean full-input tokens/completion | 84,869.76875 | 83,924.2875 | −945.48125 tokens |

**Assessment:** late-window mean loss is only slightly lower while its median is higher; late-window mean norm is lower, but both curves fluctuate and their ranges overlap. Different source-prefix and freshly generated completion/token mixtures are used at successive updates. These equal-update window summaries, finite/nonzero gradients and actual weight publications establish that optimization occurred and provide its recorded behavior; they do not demonstrate convergence or capability improvement. Gradient clipping inferred at every step further separates pre-clipping norm movement from actual parameter-update magnitude, which is not logged here.

The independent [six-checkpoint monitoring report](test_report_2026-11-07_B_monitoring.md) records all D8 checkpoints PASS and baseline→final sampled teacher/student mean absolute gap `0.238532→0.171754`, with nonmonotonic intermediate values and different fresh completions. This supports a descriptive sampled diagnostic change, not a general learning claim. **Learning improvement is not demonstrated within the approved budget.** Final text-HF acceptance remains the independently verified result in [the HF report](test_report_2026-11-07_hf_reload.md); this extraction did not rerun or replace that qualification.

Local documentation check: `git diff --check -- task_memory/task_2026-11-06_qwen35_three_pairs/test_report_2026-11-07_training_plot.md` exits 0. The existing synthetic section is preserved as historical fixture evidence. Only this report and the three named B evidence artifacts belong to this extraction; production/plotter code, shared task status, HF reports and other agents' work are unchanged. The milestone self-check finds no mainline drift within this assigned slice: its actual-point extraction, plot and assessment are delivered; parent-owned review/status reconciliation is next, with the missing exact target/retained-token counts explicitly bounded above.
