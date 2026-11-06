## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Add static verification for the user's Miles-only correction and the pending R3 decision. |
| 2026-11-06 | Record static document validation and its runtime limits. |

# Documentation validation

Scope: P0 only. Environment: `/data/ycfeng/sota-engine/miles`, zsh, system Python 3.10.6. No conda environment, GPU process, framework import, cloud access or external publication was used.

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
