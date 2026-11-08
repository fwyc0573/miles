## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record the document checks of the draft spec, plan and six tickets. |
| 2026-11-08 | Rerun after D18/D19: replace the random-order quantities with the interleaved-order quantities. |

# Test report — documentation landing

## Environment

- Worktree `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`, branch `agent-opd-image`, base `20d0b3f4`.
- `python3 --version`: Python 3.10.6 (system Python; no conda environment).

## Command

```bash
python3 /data/ycfeng/tmp/agent-opd-image/check_docs.py .   # run from this task directory
```

The current script is reproduced at the end of this report.

## Current run (after D18/D19)

Output: `files=12 tickets=6 links=21 anchors=5 order=['01', '02', '03', '04', '05', '06']`, `spans=[3, 11, 18, 58] conversations=564.6 trend_min_turns=81`, `errors: 0`, exit 0.

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Local links in the 11 task documents and `GLOSSARY.md` resolve | 0 missing | 21 links, 0 missing | PASS |
| Heading anchors used by links exist (GitHub slug rule) | 0 missing | 5 anchors, 0 missing | PASS |
| Each ticket's **Blocked by** equals its row in the plan table | equal for 01–06 | equal | PASS |
| Ticket graph has no cycle | a topological order exists | `01, 02, 03, 04, 05, 06` | PASS |
| Every ticket has a **Status** line | 6/6 | 6/6 | PASS |
| Observations per cell = 200 × 256 | 51,200 | 51,200 | PASS |
| Observations for both cells | 102,400 | 102,400 | PASS |
| Open conversations × block = slots per update | 32 × 8 = 256 | 256 | PASS |
| Updates spanned = ceil(n / 8) for n = 19, 81, 144, 464 | 3, 11, 18, 58 | 3, 11, 18, 58 | PASS |
| Conversations covered ≈ 51,200 / 90.69 (spec: about 550–580, of which about 32 partly drawn) | estimate within 550–580; the reused audit's 546 is below 580 | 564.6; 546 | PASS |
| Smallest turn count with a trend value at k = 10 (span ≥ 11) | 81 | 81 | PASS |
| Profile memory = 51,200 rows × 40 bytes | about 2 MB | 2.05 MB | PASS |
| Ticket 01 draw counts = 2 × 256 and 8 × 256 | 512 and 2,048 | 512 and 2,048 | PASS |

## Earlier run (before D12 was withdrawn)

The first draft passed the same link, anchor and graph checks (20 links, 4 anchors) and the random-order quantities (11.5%, 89.5, about 10 appearances, about 19.5 updates apart). Its first attempt had one checker error, `count text not found: 约 10 个 update`, caused by the checker's search text rather than the documents. Those quantities no longer appear in the spec.

The Q41 manifest `fresh-smoke-20261104a.json` was read with Python at that time: seed 1234, 11 files, 446,569 positions, 4,992 conversations, little-endian int64 encoding. It is no longer used.

## Limits

- Anchor slugs follow the GitHub rule as implemented in the script; other renderers may differ.
- The span, coverage and trend estimates use a 999-conversation sample and ignore length rejection, failed turns and the native mixer's balancing; they are inferences, checked here only for arithmetic.
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

# Counts stated in the spec and ticket 01.
import math
updates, turns, cells, open_conversations, block = 200, 256, 2, 32, 8
lengths = {"min": 19, "median": 81, "p90": 144, "max": 464}
mean_turns, audited_conversations = 90.69, 546
spec = (task / "spec.md").read_text()
ticket01 = (task / "tickets/01-indexed-turn-order.md").read_text()
per_cell = updates * turns
spans = [math.ceil(n / block) for n in lengths.values()]
conversations = per_cell / mean_turns
trend_min_turns = min(n for n in range(1, 1000) if math.ceil(n / block) >= 11)
facts = {
    "51,200": per_cell == 51_200,
    "102,400": per_cell * cells == 102_400,
    "M × block = 256": open_conversations * block == turns,
    "3、11、18、58": spans == [3, 11, 18, 58],
    "550–580": 550 <= conversations <= 580 and audited_conversations < 580,
    "不少于 81": trend_min_turns == 81,
    "约 2 MB": round(per_cell * 40 / 1e6) == 2,
    "前 512": 2 * turns == 512,
    "前 2,048 次取数（8 个 update 的量）": 8 * turns == 2_048,
}
for text, ok in facts.items():
    if text not in spec and text not in ticket01:
        errors.append(f"count text not found: {text}")
    if not ok:
        errors.append(f"count mismatch: {text}")

print(f"files={len(files)} tickets={len(tickets)} links={links} anchors={anchor_links} order={order}")
print(f"per_cell={per_cell} total={per_cell * cells} spans={spans} conversations={conversations:.1f} "
      f"trend_min_turns={trend_min_turns}")
print("errors:", len(errors))
for e in errors:
    print(" ", e)
sys.exit(1 if errors else 0)
```
