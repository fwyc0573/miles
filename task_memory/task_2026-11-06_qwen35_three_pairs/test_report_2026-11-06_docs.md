## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Verify latest preserve-all default, eight maintained documents, retained rendering evidence and source hashes. |
| 2026-11-06 | Record D8 acceptance and a reproducible identity audit supporting the proposed training/monitoring budget. |
| 2026-11-06 | Record D2 document validation and the local dataset-manifest metadata check. |
| 2026-11-06 | Add static verification for the user's Miles-only correction and the pending R3 decision. |
| 2026-11-06 | Record static document validation and its runtime limits. |

# Documentation validation

Scope: initial P0 checks and explicitly labeled later documentation/metadata checks. Environment: `/data/ycfeng/sota-engine/miles`, zsh, system Python 3.10.6. No conda environment, GPU process, framework import, cloud access or external publication was used by the checks in this report. Historical decision-state assertions below describe their execution time; requirements owns current decisions.

## Checks and observations

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Initial task documents | Raw request, plan, source evidence and progress exist. | Four task documents plus root GLOSSARY. | PASS |
| Local links | Every referenced local source/document exists. | 13 local links verified in the initial five documents. | PASS |
| Pair roles | Exactly the three requested student/teacher rows. | All three exact rows matched. | PASS |
| Decision state | Proposals remain unanswered; no hidden implementation approval. | Requirements explicitly records the pending framework and remaining decisions. | PASS |
| Document conventions | Task files start with Modification History; root glossary has no history table; no tickets or old CONTEXT file. | All checks passed. | PASS |
| Whitespace | No trailing whitespace or Git whitespace diagnostics. | All five initial documents passed. | PASS |
| GPU/model behavior | Requires actual native execution after interview. | Not run. | NOT RUN |

The first validator incorrectly required exit 0 from `git diff --no-index --check /dev/null <new-file>`. Git returned 1 with empty stdout/stderr because the new file differs from `/dev/null`; this was a validator error, not a document failure. The corrected command accepts 0 or 1 only when both diagnostic streams are empty. The same document checks then passed.

## Exact successful validation command

Executed from the repository root before this report and the progress self-check were appended:

```bash
python3 - <<'PY'
from pathlib import Path
import re
import subprocess
root = Path.cwd()
task = root / 'task_memory/task_2026-11-06_qwen35_three_pairs'
files = [task / name for name in ['requirements.md', 'plan.md', 'design.md', 'progress.md']] + [root / 'GLOSSARY.md']
links = 0
for path in files:
    content = path.read_text()
    assert content.endswith('\n') and not any(line.rstrip() != line for line in content.splitlines()), path
    assert content.startswith('## Modification History\n') if path.parent == task else 'Modification History' not in content
    for target in re.findall(r'\]\(([^)]+)\)', content):
        if target.startswith(('https://', 'http://', '#')):
            continue
        target = re.sub(r':\d+$', '', target)
        resolved = Path(target) if target.startswith('/') else path.parent / target
        assert resolved.exists(), (path, resolved)
        links += 1
    result = subprocess.run(['git', 'diff', '--no-index', '--check', '/dev/null', str(path)], text=True, capture_output=True)
    assert result.returncode in (0, 1) and not result.stdout and not result.stderr, (path, result)
req = (task / 'requirements.md').read_text()
for row in ['| A | Qwen3.5-4B | Qwen3.5-27B |', '| B | Qwen3.5-4B | Qwen3.5-35B-A3B |', '| C | Qwen3.5-27B | Qwen3.5-397B-A17B |']:
    assert row in req, row
assert '[Original Request]' in req and 'No answer recorded yet.' in req
assert not (task / 'tickets').exists()
assert not (root / 'CONTEXT.md').exists()
assert not (root / 'GLOSSARY-MAP.md').exists()
print(f'PASS: {len(files)} documents, {links} local links, 3 pair identities, draft decisions, glossary format, whitespace.')
print('Python:', subprocess.check_output(['python3', '--version'], text=True).strip())
print('GPU/runtime checks: NOT RUN (documentation milestone).')
PY
```

Output:

```text
PASS: 5 documents, 13 local links, 3 pair identities, draft decisions, glossary format, whitespace.
Python: Python 3.10.6
GPU/runtime checks: NOT RUN (documentation milestone).
```

## Verification limits

Source inspection establishes candidate reusable paths. It does not establish semantic equivalence of total-token loss, usable personal copies of the larger models, the runtime's 397B support, numerical acceptance, convergence, checkpoint completeness or reload success. The `check-progress` milestone record in progress.md checks task alignment only.

## Framework correction verification

Expected: current Miles is confirmed, the earlier verl wording is explicitly superseded, the Steptron implementation option is removed, and R3 remains pending. No executable source changed. Environment remains system Python 3.10.6.

```bash
python3 - <<'PY'
from pathlib import Path
import re
task = Path('task_memory/task_2026-11-06_qwen35_three_pairs')
req = (task / 'requirements.md').read_text()
design = (task / 'design.md').read_text()
plan = (task / 'plan.md').read_text()
assert '**Decision D1:** Implement, diagnose, repair and validate all three pairs in the current Miles repository.' in req
assert 'The corrected wording supersedes `verl`' in req
assert '**Framework — resolved:** current Miles only' in req
assert '**Route replay:**' in req and 'No answer recorded yet.' in req
assert 'If Steptron is selected' not in design
assert 'Miles is the provisional recommendation' not in design
assert 'current Miles implementation' in plan
links = 0
for path in sorted(task.glob('*.md')):
    text = path.read_text()
    assert text.startswith('## Modification History\n'), path
    assert all(line == line.rstrip() for line in text.splitlines()), path
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if target.startswith(('http://', 'https://', '#')):
            continue
        target = re.sub(r':\d+$', '', target)
        resolved = Path(target) if target.startswith('/') else path.parent / target
        assert resolved.exists(), (path, resolved)
        links += 1
print(f'PASS: Miles decision, superseded verl wording, pending R3, 5 task documents and {links} local links.')
PY
git diff --check
```

Actual result: PASS; 5 task documents and 15 local links. `git diff --check` emitted no diagnostics. This is documentation/source verification, not a GPU R3 test or acceptance of the proposed R3 exception. The progress self-check was refreshed to the D1 milestone, with the remaining interview as the next action.

## D2 verification iteration

The previous section records the historical D1 checkpoint. The user subsequently accepted the R3 interpretation as D2. Expected current state: D1/D2 confirmed, model matrix unchanged, workload proposal unanswered. Actual result: PASS; 5 task documents and 20 local links; no whitespace diagnostics. The progress self-check now points to workload selection. No GPU or cloud-source verification occurred.

Exact command, using the same Python 3.10.6 environment:

```bash
python3 - <<'PY'
from pathlib import Path
import re
task = Path('task_memory/task_2026-11-06_qwen35_three_pairs')
req = (task / 'requirements.md').read_text()
design = (task / 'design.md').read_text()
assert '**Decision D1:**' in req and '**Decision D2:**' in req
assert '**Route replay — resolved:**' in req
assert 'D2 confirms `N/A: dense student has no MoE routing decisions`' in design
assert '**Proposal, not a decision:**' in design
assert 'Await the user\'s interpretation before marking R3 resolved.' not in design
links = 0
for path in sorted(task.glob('*.md')):
    content = path.read_text()
    assert content.startswith('## Modification History\n') and content.endswith('\n'), path
    assert all(line == line.rstrip() for line in content.splitlines()), path
    for target in re.findall(r'\]\(([^)]+)\)', content):
        if target.startswith(('http://', 'https://', '#')):
            continue
        target = re.sub(r':\d+$', '', target)
        resolved = Path(target) if target.startswith('/') else path.parent / target
        assert resolved.exists(), (path, resolved)
        links += 1
print(f'PASS: D1/D2 confirmed; workload pending; 5 task documents; {links} local links.')
PY
git diff --check
```

Additional read-only observation: Python `json.loads` on the exact local source manifest linked in design.md returned 997,540 file bytes, 11 source-file entries and 256 training entries per source category. Its membership file exists and every listed source path has the personal codesign prefix. This is a local metadata observation; source-byte integrity, current cloud availability, actual Qwen lengths and generated category coverage remain unverified. Existing `prepare_glm5_2.py` checks source bytes and parent exclusions when executed; it was inspected, not run.

## D8 follow-up: source identity audit

The user confirmed the numerical acceptance proposal as D8. The next training-budget proposal remains unaccepted. This audit counts only local manifest identities to support that proposal:

```sh
python3 - <<'PY'
from pathlib import Path
import json
p=Path('/data/ycfeng/steptron/.worktrees/behavior-turn-replay-step3p6/task_memory/task_2026-10-25_swe_behavior_turn_replay/evidence/glm-replay-subsets-20261104.json')
d=json.loads(p.read_text()); rows=[r for b in d['categories'].values() for r in b['train']]
print(json.dumps({'entries':len(rows),'distinct_prompt_hashes':len({r['prompt_sha256'] for r in rows}),'distinct_source_turns':len({(r['file'],r['source_item_index'],r['assistant_turn_index']) for r in rows}),'distinct_conversations':len({(r['file'],r['source_item_index']) for r in rows}),'distinct_task_groups':len({r['group_id'] for r in rows})}))
PY
```

Exit status: `0`. Observed: `entries=1024`, `distinct_prompt_hashes=1024`, `distinct_source_turns=1024`, `distinct_conversations=311`, `distinct_task_groups=285`. Per-category sets contain 256 distinct prompts and 128 distinct conversations/task groups each. No cloud source bytes, current Qwen length eligibility or group semantics were validated. These counts do not establish 1,024 independent tasks.

Source reading additionally verified the native step outcome/valid-step/weight-version distinction, existing periodic evaluation and fresh sampled-token teacher scoring. The proposed 100 steps, eight training samples and 24 monitoring prefixes are new finite budget choices, not inferred approval or empirical convergence evidence. No new CPU framework tests were needed for these documentation and metadata checks; the preceding pytest collection failure remains open as recorded in the loss-semantics report.

## Latest D4 documentation and retained-evidence verification

Ran the following from `/data/ycfeng/sota-engine/miles` after recording the latest preserve-all default:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, json, re, sys
task = Path("task_memory/task_2026-11-06_qwen35_three_pairs")
req = (task / "requirements.md").read_text()
assert "**Decision D4, latest authoritative revision:**" in req
assert "后续出现真实 user 消息也不会触发剔除" in req
assert "**Decision D6" in req and "have no direct target loss" in req
assert all(value in req for value in ("131,072", "8,192", "122,880", "<= 0.03"))
assert "not yet accepted" in (task / "design.md").read_text()
files = sorted(task.glob("*.md"))
links = 0
for path in files:
    content = path.read_text()
    assert content.startswith("## Modification History\n") and content.endswith("\n"), path
    assert all(line == line.rstrip() for line in content.splitlines()), path
    for target in re.findall(r"\]\(([^)]+)\)", content):
        if target.startswith(("http://", "https://", "#")):
            continue
        target = re.sub(r":\d+$", "", target.split("#", 1)[0])
        resolved = Path(target) if target.startswith("/") else path.parent / target
        assert resolved.exists(), (path, resolved)
        links += 1
probe_dir = Path("/data/ycfeng/tmp/qwen35-three-pairs-format-kh3g82mp")
result = json.loads((task / "evidence/qwen-preserved-history-cpu.json").read_text())
assert result == json.loads((probe_dir / "preserved-history-results.json").read_text())
assert result["kwargs"]["preserve_thinking"] is True
assert len(result["actual_samples"]) == 4 and len(result["synthetic_cases"]) == 2
assert all(r["all_reasoning_retained"] for r in result["actual_samples"])
assert all(r["early_reasoning_retained"] and r["late_reasoning_retained"] and r["tokenize_paths_equal"] for r in result["synthetic_cases"])
assert hashlib.sha256(Path(result["template"]).read_bytes()).hexdigest() == result["template_sha256"]
assert hashlib.sha256((probe_dir / "verify_preserved_history.py").read_bytes()).hexdigest() == "054abfc159ebcb0a6daceac3b8c8b813b93a548dc05204648b75e52c3af2a732"
assert 100 * 8 == 800 and 6 * 24 == 144
print(f"PASS: Python {sys.version.split()[0]}; {len(files)} documents; {links} local links; latest D4/D6/D7/D8; preserved-history evidence and hashes; proposed-budget arithmetic.")
PY
git diff --check
```

Both commands exited `0`. Observed: Python `3.10.6`, eight maintained Markdown documents, 66 valid local links, latest D4/D6/D7/D8 assertions passed, retained/rerun preservation JSON equality and both source hashes passed. Proposed training/monitoring arithmetic passed; the proposal remains unaccepted. This is documentation and CPU evidence consistency, not native training qualification.

The first verification invocation used bare `python` and exited `127` because that executable is absent from the host PATH. Repeating the same read-only check with installed `python3` passed; no environment changes were made. The rendering probe itself used the explicit Python 3.12.13 environment documented in the format report.
