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
# The SWE-1003 training-turn distribution is pending the source audit (spec S2).
spec = (task / "spec.md").read_text()
ticket01 = (task / "tickets/01-interleaved-turn-order.md").read_text()
per_cell = updates * turns
trend_min_turns = min(n for n in range(1, 1000) if math.ceil(n / block) >= 11)
facts = {
    "51,200": per_cell == 51_200,
    "102,400": per_cell * cells == 102_400,
    "M × block = 256": open_conversations * block == turns,
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
print(f"per_cell={per_cell} total={per_cell * cells} trend_min_turns={trend_min_turns}")
print("errors:", len(errors))
for e in errors:
    print(" ", e)
sys.exit(1 if errors else 0)
