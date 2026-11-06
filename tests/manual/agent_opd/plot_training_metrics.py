"""Plot archived OPD loss and gradient norms without loading raw run artifacts.

The Markdown reports remain the authoritative scalar records. Rendering requires
Matplotlib and uses an isolated temporary cache that is removed on completion.

Example:
    python3 -B tests/manual/agent_opd/plot_training_metrics.py \
        --report GLM-4.7-Flash=task_memory/task_2026-11-05_agent_opd_warmup/test_report_2026-11-06_agent_opd_final.md \
        --report Qwen3.5-4B=task_memory/task_2026-11-05_agent_opd_warmup/test_report_2026-11-05_agent_opd_learning.md \
        --output /data/ycfeng/tmp/agent-opd-training-curves-20261106.png
"""

import argparse
import math
import os
import tempfile
from pathlib import Path


def read_training_metrics(report: Path) -> tuple[list[int], list[float], list[float]]:
    lines = report.read_text().splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("| Update | Loss | Gradient norm |")]
    if len(starts) != 1:
        raise ValueError(f"{report}: expected one update/loss/gradient table, found {len(starts)}")
    updates, losses, norms = [], [], []
    for line in lines[starts[0] + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        updates.append(int(cells[0]))
        losses.append(float(cells[1]))
        norms.append(float(cells[2]))
    if not updates or updates != list(range(1, len(updates) + 1)):
        raise ValueError(f"{report}: successful update numbers are missing or out of order")
    if not all(math.isfinite(value) for value in losses + norms):
        raise ValueError(f"{report}: a loss or gradient norm is non-finite")
    return updates, losses, norms


def _named_report(value: str) -> tuple[str, Path]:
    name, separator, path = value.partition("=")
    if not separator or not name or not path:
        raise argparse.ArgumentTypeError("Expected LABEL=REPORT_PATH")
    return name, Path(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=_named_report, action="append", required=True, metavar="LABEL=PATH")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runs = args.report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opd-plot-cache-", dir=args.output.parent) as cache:
        os.environ["MPLCONFIGDIR"] = cache
        # Defer this optional import until its cache has a task-owned location.
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.ticker import MaxNLocator

        fig, axes = plt.subplots(len(runs), 2, figsize=(11, 3.5 * len(runs)), layout="constrained", squeeze=False)
        fig.suptitle("Recorded OPD training metrics", fontsize=16)
        for row, (name, report) in enumerate(runs):
            updates, losses, norms = read_training_metrics(report)
            for column, (values, metric, color) in enumerate(
                ((losses, "Training loss", "#1769aa"), (norms, "Gradient L2 norm before clipping", "#ad4c17"))
            ):
                ax = axes[row, column]
                ax.plot(updates, values, marker="o", markersize=4, linewidth=1.5, color=color)
                ax.set_title(f"{name}: {len(updates)} successful updates")
                ax.set_xlabel("Successful optimizer update")
                ax.set_ylabel(metric)
                ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=10))
                ax.set_xlim(updates[0] - 0.25, updates[-1] + 0.25)
                ax.margins(y=0.2)
                ax.grid(alpha=0.25)
                peak = max(range(len(values)), key=values.__getitem__)
                ax.annotate(
                    f"Peak {values[peak]:.4g} at update {updates[peak]}",
                    xy=(updates[peak], values[peak]),
                    xytext=(0, 12),
                    textcoords="offset points",
                    ha="left" if peak == 0 else "right" if peak == len(values) - 1 else "center",
                    fontsize=9,
                )
            print(
                f"{name}: updates={len(updates)}, loss_first={losses[0]:.10g}, "
                f"loss_last={losses[-1]:.10g}, loss_min={min(losses):.10g}, "
                f"loss_max={max(losses):.10g}, norm_min={min(norms):.10g}, norm_max={max(norms):.10g}"
            )
        fig.supxlabel(
            "Unsmoothed recorded points; each panel has its own y-axis scale. "
            "Different sampled turns at each update.",
            fontsize=9,
        )
        fig.savefig(args.output, dpi=150)
        plt.close(fig)
    print(f"OPD_TRAINING_CURVES_WRITTEN {args.output} bytes={args.output.stat().st_size}")


if __name__ == "__main__":
    main()
