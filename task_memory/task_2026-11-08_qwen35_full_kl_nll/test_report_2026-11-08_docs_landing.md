## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record the document checks of the draft spec, plan and six tickets. |

# Test report — documentation landing

## Environment

- Worktree `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`, branch `agent-opd-image`, base `20d0b3f4`.
- `python3 --version`: Python 3.10.6 (system Python; no conda environment).

## Command

```bash
python3 /data/ycfeng/tmp/agent-opd-image/check_docs.py .   # run from this task directory
```

The script is reproduced at the end of this report.

## Expected and actual

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Local links in the 10 task documents and `GLOSSARY.md` resolve | 0 missing | 20 links, 0 missing | PASS |
| Heading anchors used by links exist (GitHub slug rule) | 0 missing | 4 anchors, 0 missing | PASS |
| Each ticket's **Blocked by** equals its row in the plan table | equal for 01–06 | equal | PASS |
| Ticket graph has no cycle | a topological order exists | `01, 02, 03, 04, 05, 06` | PASS |
| Every ticket has a **Status** line | 6/6 | 6/6 | PASS |
| Observations per cell = 200 × 256 | 51,200 | 51,200 | PASS |
| Observations for both cells | 102,400 | 102,400 | PASS |
| Fraction of positions drawn = 51,200 / 446,569 | 11.5% | 11.47% | PASS |
| Mean assistant positions per conversation = 446,569 / 4,992 | 89.5 | 89.46 | PASS |
| Appearances per conversation = 89.46 × 0.1147 | about 10 | 10.26 | PASS |
| Mean interval = 200 / 10.26 | about 19.5 updates | 19.50 | PASS |
| Profile memory = 51,200 rows × 40 bytes | about 2 MB | 2.05 MB | PASS |
| First 512 draws = 2 updates × 256 | 512 | 512 | PASS |

First run: one error, `count text not found: 约 10 个 update`. The checker searched for wording the spec does not use (the spec says "大约出现在 10 个 update 中"); the checker's search text was corrected, no document changed, and the rerun returned 0 errors.

## Separate fact check

The Q41 manifest `fresh-smoke-20261104a.json` (Steptron behavior-turn-replay task evidence) was read with Python: `status=smoke_prefix_ready`, seed 1234, 11 files, population count 446,569, 4,992 conversations, encoding "little-endian int64, row-major". These match spec S2 item 6.

## Limits

- Anchor slugs follow the GitHub rule as implemented in the script; other renderers may differ.
- The appearance and interval estimates ignore length rejection and failed turns; they are inferences, checked here only for arithmetic.
- No code or GPU behavior is verified in this phase.

## Checker script

```python
"""Check local links, anchors, the ticket graph and the counts of this task's documents."""
import re
import sys
import unicodedata
from pathlib import Path

task = Path(sys.argv[1]).resolve()
root = task.parents[1]
files = sorted(task.rglob("*.md")) + [root / "GLOSSARY.md"]
errors = []


def slug(heading):
    text = heading.strip().lower()
    kept = []
    for ch in text:
        cat = unicodedata.category(ch)
        if ch in " -" or cat[0] in "LMN" or cat == "Pc":
            kept.append(ch)
    return "".join(kept).replace(" ", "-")


def anchors(path):
    return {slug(m.group(2)) for m in re.finditer(r"^(#{1,6}) (.+)$", path.read_text(), re.M)}


links = 0
anchor_links = 0
for f in files:
    for m in re.finditer(r"\]\(([^)\s]+)\)", f.read_text()):
        target = m.group(1)
        if re.match(r"[a-z]+://", target):
            continue
        links += 1
        path, _, frag = target.partition("#")
        dest = (f.parent / path).resolve() if path else f
        if not dest.exists():
            errors.append(f"{f.relative_to(root)}: missing {target}")
            continue
        if frag:
            anchor_links += 1
            if frag not in anchors(dest):
                errors.append(f"{f.relative_to(root)}: missing anchor {target}")

# Ticket graph: plan table edges must equal each ticket's Blocked-by line.
plan = (task / "plan.md").read_text()
tickets = sorted((task / "tickets").glob("*.md"))
ids = [t.name[:2] for t in tickets]
plan_edges = {}
for m in re.finditer(r"^\| \[(\d\d)\]\(tickets/[^)]+\) \| [^|]+ \| ([^|]+) \|$", plan, re.M):
    plan_edges[m.group(1)] = set(re.findall(r"\b0\d\b", m.group(2)))
for t in tickets:
    body = t.read_text()
    line = re.search(r"^\*\*Blocked by:\*\* (.+)$", body, re.M).group(1)
    deps = set(re.findall(r"\b0\d\b", line))
    if deps != plan_edges.get(t.name[:2]):
        errors.append(f"{t.name}: blocked-by {sorted(deps)} != plan {sorted(plan_edges.get(t.name[:2], []))}")
    if not re.search(r"^\*\*Status:\*\* ", body, re.M):
        errors.append(f"{t.name}: no status")
if sorted(plan_edges) != ids:
    errors.append(f"plan tickets {sorted(plan_edges)} != files {ids}")

# Topological order exists (no cycle).
remaining = {k: set(v) for k, v in plan_edges.items()}
order = []
while remaining:
    ready = sorted(k for k, v in remaining.items() if not v - set(order))
    if not ready:
        errors.append(f"cycle among {sorted(remaining)}")
        break
    order.extend(ready)
    for k in ready:
        remaining.pop(k)

# Counts stated in the spec.
updates, turns, cells, population, conversations = 200, 256, 2, 446_569, 4_992
spec = (task / "spec.md").read_text()
per_cell = updates * turns
fraction = per_cell / population
mean_turns = population / conversations
appearances = mean_turns * fraction
facts = {
    "51,200": per_cell == 51_200,
    "102,400": per_cell * cells == 102_400,
    "11.5%": round(fraction * 100, 1) == 11.5,
    "89.5": round(mean_turns, 1) == 89.5,
    "10 个 update 中": round(appearances) == 10,
    "约 19.5": round(updates / appearances, 1) == 19.5,
    "约 2 MB": round(per_cell * 40 / 1e6) == 2,
    "前 512": 2 * turns == 512,
}
for text, ok in facts.items():
    if text not in spec and text not in (task / "tickets/01-indexed-turn-order.md").read_text():
        errors.append(f"count text not found: {text}")
    if not ok:
        errors.append(f"count mismatch: {text}")

print(f"files={len(files)} tickets={len(tickets)} links={links} anchors={anchor_links} order={order}")
print(f"per_cell={per_cell} total={per_cell * cells} fraction={fraction:.4f} mean_turns={mean_turns:.2f} "
      f"appearances={appearances:.2f} interval={updates / appearances:.2f}")
print("errors:", len(errors))
for e in errors:
    print(" ", e)
sys.exit(1 if errors else 0)
```
