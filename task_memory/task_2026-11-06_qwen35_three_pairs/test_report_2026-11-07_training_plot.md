## Modification History

| Date | Change |
| --- | --- |
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
