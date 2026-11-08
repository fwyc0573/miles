## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Add the post-review revision check for the renumbered 08/09 graph; restore word spacing in earlier observations. |
| 2026-11-08 | Validate the final 17-document/nine-ticket draft, D1–D10, real dependency graph and baseline-inclusive budget; close the stale graph-check review finding. |
| 2026-11-08 | Record initial local document structure, link and budget checks; scientific decisions remain open. |

# Documentation validation

## Environment and scope

- Host workspace: `/data/ycfeng/sota-engine/miles`, branch `agent-opd`.
- Python: `python3 --version` → `Python 3.10.6`; no conda environment activated.
- Scope: local documentation only. Runtime, dataset equivalence, actual resource availability and benchmark capability are not tested here.
- Verification is for a **draft**, not an approval of the proposed scientific choices.

## Initial document check — PASS

Executed from the Miles workspace:

```bash
python3 - <<'PY'
from pathlib import Path
import re
root = Path('task_memory/task_2026-11-08_qwen35_swe_full_r256')
files = sorted(root.rglob('*.md'))
errors = []
links = 0
for p in files:
    text = p.read_text()
    if not text.startswith('## Modification History\n'):
        errors.append(f'{p}: missing modification history')
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
        if '://' in target or target.startswith('#'):
            continue
        path = target.split('#', 1)[0]
        links += 1
        if not (p.parent / path).exists():
            errors.append(f'{p}: broken link {target}')
tickets = sorted((root / 'tickets').glob('*.md'))
for p in tickets:
    text = p.read_text()
    for field in ('**What to build:**', '**Blocked by:**',
                  '**Status:** draft-blocked-docs', '- [ ]'):
        if field not in text:
            errors.append(f'{p}: missing {field}')
edges = {1: [], 2: [1], 3: [1], 4: [2, 3], 5: [2, 3],
         6: [2, 3], 7: [2, 3], 8: [4, 5, 6, 7]}
for node, blockers in edges.items():
    if any(b >= node for b in blockers):
        errors.append(f'non-topological edge at {node}')
print({'markdown_files': len(files), 'tickets': len(tickets),
       'local_links_checked': links, 'planned_updates': 4 * 200,
       'planned_hfs': 4 * 4,
       'benchmark_attempts_excluding_baseline': 4 * 4 * 100 * 4,
       'strict_256_presentations': 4 * 200 * 256,
       'strict_256_fresh_trajectories': 2 * (200 * 256 + 4 * 256),
       'errors': errors})
raise SystemExit(bool(errors))
PY
```

Observed before adding this report: **12 Markdown documents, 8 individual tickets, 16 checked local links, 0 errors**. Budget arithmetic: **800 updates, 16 HFs, 6,400 benchmark attempts excluding a possible baseline, 204,800 strict-256 presentations, 104,448 nominal fresh trajectories**.

The edge check verifies the proposed graph's topological ordering, not that the dependency choices have user approval. Required link targets exist; Markdown anchor resolution was not tested. Fresh-trajectory arithmetic is conditional on exact256 valid turns and does not establish unique prompts or successful runtime generation.

## Requirement coverage — draft inspection

| Original requirement | Spec owner | Tickets |
| --- | --- | --- |
| New docs task and prior Qwen foundation | S1, S8 | All; current documentation phase |
| Two teachers × full/r256 | S1, S2 | 02, 04–07 |
| GLM-5.2 SWE and default Steptron loading | S3 | 01 |
| 256 turns; 50 same-bank uses; 200 updates | S2, S4, S5 | 02, 04–07 |
| Learning rate 2e-6 | S4 | 02, 04–07 |
| HF-only every 50 updates in personal OSS | S6 | 03, 04–07 |
| Same SWE benchmark, 100 questions, avg@4 | S6 | 01, 03, 04–07 |
| Every-update KL and actual TIS tokens | S4 | 02, 04–08 |
| Finite rollout waiting/yield | S5 | 02, 03 |
| Asynchronous evaluation and timely deletion | S6 | 03, 04–07 |
| H200, non-preemptible, 56-GPU cap | S7 | 02–07 |

**Result:** every requested topic has an owner. Ticket numbers in this table use the initial eight-ticket numbering, in which 08 was the comparison. Protocol freeze remains pending because source-backed interview decisions have not yet been answered.

## Final pre-confirmation document check — PASS

The previous sections preserve the initial draft's observations. At this checkpoint D1–D10 are answered, ticket 09 (renumbered 08 after the post-freeze review) is present, and only whole-document confirmation remains. The old numeric-order test is superseded: the then-valid dependency `08←09` must pass a real DAG check.

Executed from the same Miles workspace, Python 3.10.6. The `expected` graph below encodes the numbering before the post-review swap; the current checker is in [Post-review revision check](#post-review-revision-check--pass).

```bash
python3 -B - <<'PY'
from pathlib import Path
import json, re, sys
root = Path('task_memory/task_2026-11-08_qwen35_swe_full_r256')
files = sorted(root.rglob('*.md'))
errors, links, anchors = [], 0, 0
for p in files:
    text = p.read_text()
    if not text.startswith('## Modification History\n'):
        errors.append(f'{p}: missing modification history')
    if any(line.rstrip() != line for line in text.splitlines()):
        errors.append(f'{p}: trailing whitespace')
    if sum(line.startswith('```') for line in text.splitlines()) % 2:
        errors.append(f'{p}: unpaired code fence')
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
        if '://' in target:
            continue
        name, _, anchor = target.partition('#')
        dest = p.parent / name if name else p
        links += 1
        if not dest.exists():
            errors.append(f'{p}: broken link {target}')
        elif anchor:
            headings = re.findall(r'^#{1,6}\s+(.+)$', dest.read_text(), re.M)
            slugs = {re.sub(r'[^\w -]', '', h.lower()).replace(' ', '-') for h in headings}
            anchors += 1
            if anchor not in slugs:
                errors.append(f'{p}: broken anchor {target}')
tickets = sorted((root / 'tickets').glob('*.md'))
edges = {}
for p in tickets:
    node = int(p.name[:2])
    text = p.read_text()
    for field in ('**What to build:**', '**Blocked by:**', '**Status:**', '- [ ]'):
        if field not in text:
            errors.append(f'{p}: missing {field}')
    line = next(line for line in text.splitlines() if line.startswith('**Blocked by:**'))
    edges[node] = sorted({int(n) for n in re.findall(r'\b(0[1-9])\b', line)})
expected = {1: [], 2: [1], 3: [1], 4: [2, 3], 5: [2, 3], 6: [2, 3], 7: [2, 3], 8: [4, 5, 6, 7, 9], 9: [1, 3]}
if edges != expected:
    errors.append(f'ticket graph mismatch: {edges}')
plan_edges = {}
for line in (root / 'plan.md').read_text().splitlines():
    match = re.match(r'\| \[(\d+)\]\(tickets/[^)]+\) \|.*\| ([^|]+) \|$', line)
    if match:
        plan_edges[int(match[1])] = sorted({int(n) for n in re.findall(r'\b(0[1-9])\b', match[2])})
if plan_edges != edges:
    errors.append(f'plan differs from tickets: {plan_edges}')
remaining, order = dict(edges), []
while remaining:
    ready = sorted(n for n, deps in remaining.items() if all(d in order for d in deps))
    if not ready:
        errors.append(f'cycle or missing dependency: {remaining}')
        break
    for n in ready:
        order.append(n)
        del remaining[n]
requirements = (root / 'requirements.md').read_text()
if set(re.findall(r'^### D(\d+)\b', requirements, re.M)) != {str(n) for n in range(1, 11)}:
    errors.append('expected D1-D10 actual answers')
print(json.dumps({'python': sys.version.split()[0], 'markdown_files': len(files), 'tickets': len(tickets), 'local_links': links, 'anchors': anchors, 'edges': edges, 'topological_order': order, 'successful_updates': 4 * 200, 'training_hfs': 4 * 4, 'benchmark_points': 4 * 4 + 1, 'logical_benchmark_attempts': (4 * 4 + 1) * 100 * 4, 'nominal_presentations': 4 * 200 * 256, 'nominal_new_trajectories': 2 * (200 * 256 + 4 * 256), 'errors': errors}, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
PY
```

Observed: exit 0; **17 Markdown files, 9 tickets, 25 local links, 1 anchor, 0 errors**. Parsed ticket edges exactly matched the plan. Valid topological order: `01,02,03,04,05,06,07,09,08`; no baseline→formal-cell blocking edge exists.

Budget calculations: **800 planned successful updates; 16 training HFs; 17 benchmark points; 6,800 logical attempts; 204,800 nominal presentations; 104,448 nominal new trajectories**. The last two assume 256 valid turns per bank and exclude failed requests. Early termination under D7 remains FAILED/INCOMPLETE, not a numerical exemption from completion criteria.

Additional coverage (ticket numbers updated to the post-review numbering): D1/D6 partial bank and timeout → 02/04–07; D2 exact pre-TIS statistic → 02/09; D3 research-based optimizer → 02; D4 dual binary TIS → 02; D5 remaining 128K → 01/02; D7 stop on zero TIS survivors → 02/04–07; D8 baseline → 08/09; D9 personal resource cap → 02/03/04–07/08; D10 bounded missing-slot recovery → 03/04–07/08.

Review remediation: the native loss chain was read directly (`objective.py`, `hub/opd.py`, `hub/losses.py`, `hub/math_utils.py`, argument defaults and zero-reward extraction). Spec S4 now states the detached-advantage PPO surrogate, separate current-scoring/behavior ratios and native effective flags; ticket 02 requires actual gradient validation. This is a documentation/source inspection result, not a performed GPU gradient test. The two new DOC-REVIEW P2 findings are closed by these source-backed edits and the corrected executable document check.

## Post-confirmation check — PASS

The user selected “确认冻结（推荐）”. After recording that answer and updating document/ticket states, executed the exact checker stored above:

```bash
python3 -B - <<'PY'
from pathlib import Path
report = Path('task_memory/task_2026-11-08_qwen35_swe_full_r256/test_report_2026-11-08_docs_landing.md').read_text()
section = report.split('## Final pre-confirmation document check — PASS', 1)[1]
script = section.split("python3 -B - <<'PY'\n", 1)[1].split('\nPY\n```', 1)[0]
exec(compile(script, 'document-validation', 'exec'))
PY
```

Observed again: exit 0, 17 Markdown files, 9 tickets, 25 local links, 1 anchor, 0 errors, identical valid DAG and budget totals. Re-read the complete final `requirements.md`; the recorded answers, explicit freeze and assigned acceptance owners are consistent. The index was empty before staging this documentation step; the inspected `GLOSSARY.md` diff contains only the three resolved terms. No runtime tests or GPU operations are represented by this PASS.

## Post-review revision check — PASS

The post-freeze Standards review asked for dependency-ordered ticket numbers. After renumbering (08 = shared baseline, 09 = final comparison), this checker replaces the previous one. Beyond the earlier checks it requires every blocker number to be lower than the blocked ticket, every ticket title number to match its file name, and every `tickets/NN-slug.md` mention in the task documents or `GLOSSARY.md` to resolve.

Executed from the Miles workspace, Python 3.10.6:

```bash
python3 -B - <<'PY'
from pathlib import Path
import json, re, sys
root = Path('task_memory/task_2026-11-08_qwen35_swe_full_r256')
files = sorted(root.rglob('*.md'))
errors, links, anchors = [], 0, 0
for p in files:
    text = p.read_text()
    if not text.startswith('## Modification History\n'):
        errors.append(f'{p}: missing modification history')
    if any(line.rstrip() != line for line in text.splitlines()):
        errors.append(f'{p}: trailing whitespace')
    if sum(line.startswith('```') for line in text.splitlines()) % 2:
        errors.append(f'{p}: unpaired code fence')
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
        if '://' in target:
            continue
        name, _, anchor = target.partition('#')
        dest = p.parent / name if name else p
        links += 1
        if not dest.exists():
            errors.append(f'{p}: broken link {target}')
        elif anchor:
            headings = re.findall(r'^#{1,6}\s+(.+)$', dest.read_text(), re.M)
            slugs = {re.sub(r'[^\w -]', '', h.lower()).replace(' ', '-') for h in headings}
            anchors += 1
            if anchor not in slugs:
                errors.append(f'{p}: broken anchor {target}')
for p in files + [Path('GLOSSARY.md')]:
    for mention in re.findall(r'tickets/(\d\d-[\w-]+\.md)', p.read_text()):
        if not (root / 'tickets' / mention).exists():
            errors.append(f'{p}: stale ticket path {mention}')
tickets = sorted((root / 'tickets').glob('*.md'))
edges = {}
for p in tickets:
    node = int(p.name[:2])
    text = p.read_text()
    for field in ('**What to build:**', '**Blocked by:**', '**Status:**', '- [ ]'):
        if field not in text:
            errors.append(f'{p}: missing {field}')
    title = next(line for line in text.splitlines() if line.startswith('# '))
    if not title.startswith(f'# {p.name[:2]}:'):
        errors.append(f'{p}: title number differs from file name')
    line = next(line for line in text.splitlines() if line.startswith('**Blocked by:**'))
    edges[node] = sorted({int(n) for n in re.findall(r'\b(0[1-9])\b', line)})
expected = {1: [], 2: [1], 3: [1], 4: [2, 3], 5: [2, 3], 6: [2, 3], 7: [2, 3], 8: [1, 3], 9: [4, 5, 6, 7, 8]}
if edges != expected:
    errors.append(f'ticket graph mismatch: {edges}')
if any(b >= n for n, deps in edges.items() for b in deps):
    errors.append('a ticket number does not follow its blockers')
plan_edges = {}
for line in (root / 'plan.md').read_text().splitlines():
    match = re.match(r'\| \[(\d+)\]\(tickets/[^)]+\) \|.*\| ([^|]+) \|$', line)
    if match:
        plan_edges[int(match[1])] = sorted({int(n) for n in re.findall(r'\b(0[1-9])\b', match[2])})
if plan_edges != edges:
    errors.append(f'plan differs from tickets: {plan_edges}')
remaining, order = dict(edges), []
while remaining:
    ready = sorted(n for n, deps in remaining.items() if all(d in order for d in deps))
    if not ready:
        errors.append(f'cycle or missing dependency: {remaining}')
        break
    for n in ready:
        order.append(n)
        del remaining[n]
requirements = (root / 'requirements.md').read_text()
if set(re.findall(r'^### D(\d+)\b', requirements, re.M)) != {str(n) for n in range(1, 11)}:
    errors.append('expected D1-D10 actual answers')
print(json.dumps({'python': sys.version.split()[0], 'markdown_files': len(files), 'tickets': len(tickets), 'local_links': links, 'anchors': anchors, 'edges': edges, 'topological_order': order, 'successful_updates': 4 * 200, 'training_hfs': 4 * 4, 'benchmark_points': 4 * 4 + 1, 'logical_benchmark_attempts': (4 * 4 + 1) * 100 * 4, 'nominal_presentations': 4 * 200 * 256, 'nominal_new_trajectories': 2 * (200 * 256 + 4 * 256), 'errors': errors}, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
PY
```

Observed: exit 0; **17 Markdown files, 9 tickets, 32 local links, 5 anchors, 0 errors**. The extra links and anchors are the new references to spec S4/`优化参数`, `review.md` and this section. Parsed ticket edges exactly match the plan, every blocker number is lower than its blocked ticket, and the topological order is `01,02,03,04,05,06,07,08,09`. A search for the old ticket file names (`08-four-cell`, `09-original`) and for the squashed words named in the review (`zerokeep`, `successfulupdates`) found no remaining match in the task directory. Budget totals are unchanged: 800 successful updates, 16 training HFs, 17 benchmark points, 6,800 logical attempts. This is a documentation check only; no runtime test or GPU operation is represented.
