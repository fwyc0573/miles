## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Verify selected terminal H800 receipts and archive delivery; correct review P3 and reference parent D35. |

# H800 Archive Closure Verification

Task ID: `profile-h800-archive-close-20261110`.
Worktree: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`.
Environment: Linux/zsh, `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python 3.12.13. Cached lint packages (Ruff 0.14.7, Black 24.3.0, isort 5.13.2) are reused from `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages`; no dependency install or network operation occurred.

## Scope and decision

Terminal capacity and both smoke cleanups were already completed on Nov9. This step verifies retained local evidence and commits selected owned artifacts only; it performs no platform/network/SSH/GPU operation, new test/framework work, further cleanup or parent merge.

Parent-only D35 is explicitly supplied by the primary's delegation: the user chose `采用 H800 结果`, adopted accepted H800 D34 capacity for parent full_kl_nll D1/D22 and approved primary-owned merge/T02/T03. Those follow-up operations are approved, not completed here. The parent requirements record owns D35; this task references it. Upstream old-D11 and the original Nov9 receipts are unchanged.

## Recorded terminal review and remediation

Reviewer TaskID: `profile-h800-terminal-acceptance-review-20261109`. The primary supplied **P3: stale current frontier in progress.md lines 36–38** and **No other findings**. The original reviewer response is not persisted in this preparation task; this is a record of the supplied result, not a new independent review.

Remediation: replace the stale startup/cleanup-pending frontier with completed native capacity/cleanup and approved, pending primary-owned parent integration; update requirements/plan/checkpoint/summary consistently. Preserve the Nov9 timeline as explicitly historical. Evidence and remaining verification limits are retained below.

## Exact scoped commands

Commands ran from the worktree above. Python `-B` prevents bytecode writes.

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B tests/manual/agent_opd/check_h800_capacity_evidence.py \
  task_memory/task_2026-11-09_profile_h800_preparation/evidence
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m ruff check --no-cache \
  tests/manual/agent_opd/check_h800_capacity_evidence.py
BLACK_CACHE_DIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode/black-cache-h800-archive-close \
  PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m black --check --diff \
  tests/manual/agent_opd/check_h800_capacity_evidence.py
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m isort --check-only --diff \
  tests/manual/agent_opd/check_h800_capacity_evidence.py
git diff --check
git diff --cached --check
```

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Existing offline checker | Terminal five replicas, two ACKs/bank visits, eight ranks with two ordered complete student passes, verified source/lifetime and text-only weight verdict | `PASS: retained terminal updates, bank visits, two student passes and text-only weight scope` | PASS |
| Ruff | No checker lint errors | All checks passed; existing pyproject `select`/`ignore` deprecation warning only | PASS |
| Black | No formatting change needed | One file would be left unchanged | PASS |
| isort | Imports already sorted | Exit 0, no output | PASS |
| Working-tree diff | No whitespace errors | `git diff --check`: exit 0, no output | PASS |
| Initial local credential scan | No literal reference credentials/private keys | 92 scoped changed/untracked files, two local personal references plus nine environment references; zero hits | PASS |
| Cleanup receipt consistency | Both recorded removals agree across inventory/backup/result | 167 + 412 files; 15325989 + 2136889910 = 2152215899 logical bytes | PASS |
| Staged diff | No whitespace errors | `git diff --cached --check`: exit 0, no output | PASS |
| Staged evidence/credential/size check | Exactly selected scope, all JSON parse, no literal credential/private key, each file below repository 1000 KiB added-file limit | 21 files, 12 JSON, zero hits against two local plus nine environment references, largest 104231 bytes | PASS |
| Local archive retention | Both recorded archives still exist at recorded lengths | 3911955 and 458427717 bytes observed by local stat; no extraction or repeated full hash scan | PASS |

The final staged check reads index blobs, not unchecked working-tree contents, and never prints credential values. Exact command:

```bash
python3 -B - <<'PY'
from pathlib import Path
import json, os, re, subprocess
names = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], text=True).splitlines()
assert len(names) == 21
credentials = [(Path('/data/ycfeng/tmp/brainctl-auth-i-fengyicheng') / name).read_bytes().strip()
               for name in ('accesskey_id', 'accesskey_secret')]
assert all(credentials)
credentials += [value.encode() for name, value in os.environ.items()
                if re.search(r'TOKEN|SECRET|PASSWORD|ACCESS_KEY|API_KEY', name, re.I) and len(value) >= 12]
hits = private_keys = parsed = 0
largest = 0
for name in names:
    content = subprocess.check_output(['git', 'show', f':{name}'])
    largest = max(largest, len(content))
    hits += int(any(value in content for value in credentials))
    private_keys += int(re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----', content) is not None)
    assert len(content) < 1000 * 1024 and b'\0' not in content
    if name.endswith('.json'):
        json.loads(content)
        parsed += 1
assert hits == private_keys == 0 and parsed == 12
print(f'PASS: staged_files={len(names)} parsed_json={parsed} literal_credential_hits={hits} private_key_hits={private_keys} largest_bytes={largest}; references=2 local + {len(credentials)-2} environment')
PY
```

The first one-off cleanup consistency check assumed both historical inventories used `logical_bytes` and raised `KeyError: 'logical_bytes'`. Inspection found the original receipt uses `total_bytes`/`total_files`, while the network-fixed receipt uses `logical_bytes`. The corrected local-only check reads each actual schema explicitly; no receipt, product behavior, archive or cloud output changed. Exact corrected command:

```bash
python3 -B - <<'PY'
from pathlib import Path
import json
root = Path('task_memory/task_2026-11-09_profile_h800_preparation/evidence')
def read(name):
    return json.loads((root / name).read_text())
a = read('cloud-cleanup-inventory-20261109.json')
b = read('cloud-cleanup-backup-20261109.json')
c = read('cloud-cleanup-result-20261109.json')
assert len(a['files']) == a['total_files'] == b['verified_files'] == c['deleted_files'] == 167
assert a['total_bytes'] == b['verified_logical_bytes'] == c['removed_logical_bytes'] == 15325989
assert b['status'] == c['status'] == 'PASS'
assert not c['cloud_root_exists_after'] and not c['shared_trash_touched'] and not c['source_assets_touched']
a = read('cloud-cleanup-network-fixed-inventory-20261109.json')
b = read('cloud-cleanup-network-fixed-backup-20261109.json')
c = read('cloud-cleanup-network-fixed-result-20261109.json')
assert len(a['files']) == b['file_count'] == c['removed_files'] == 412
assert a['logical_bytes'] == b['logical_bytes'] == c['removed_logical_bytes'] == 2136889910
assert b['status'] == c['status'] == 'PASS'
assert b['all_member_sizes_and_sha256_equal_inventory'] and c['all_cloud_files_reverified_before_unlink']
assert not c['root_exists_after'] and not c['remaining_task_roots']
print('PASS: retained cleanup receipts agree on 579 files / 2152215899 logical bytes; physical reclamation remains unverified')
PY
```

## Git evidence selection

Paths below are relative to `task_memory/task_2026-11-09_profile_h800_preparation/evidence/`. These selected JSON receipts support the reports and fixed-run checker without committing sample bodies, raw journals or full weight-event payloads:

- `admission-h800-network-fixed-20261109.terminal.json`
- `cloud-cleanup-network-fixed-backup-20261109.json`
- `cloud-cleanup-network-fixed-inventory-20261109.json`
- `cloud-cleanup-network-fixed-result-20261109.json`
- `h800-network-fixed-acquisition-progress-20261109.json`
- `h800-network-fixed-capacity-acceptance-20261109.json`
- `h800-network-fixed-initial-sync-20261109.json`
- `h800-network-fixed-initial-warning-classification-20261109.json`
- `h800-network-fixed-native-capacity-final-20261109.json`
- `h800-network-fixed-native-terminal-20261109.json`
- `h800-network-fixed-version-one-checksum-check-20261109.json`
- `h800-capacity-112k-network-fixed/r256/exp-1109-192340-580111/A/student-finished.json`: native return code 0; the rest of this nested directory is redundant local-only evidence.

Also selected, relative to the preparation task directory:

- `requirements.md`
- `plan.md`
- `progress.md`
- `checkpoint_2026-11-09_native_preflight.md`
- `summary.md`
- `test_report_2026-11-09_cloud_cleanup.md`
- `test_report_2026-11-09_network_fixed_prelaunch.md`
- `test_report_2026-11-10_h800_archive_close.md`

The sole Python deliverable is `tests/manual/agent_opd/check_h800_capacity_evidence.py`. Total selected scope: 21 files, including 12 JSON receipts. Staging is by an explicit file list, never bulk-add.

## Retained local-only artifacts

Both untracked nested trees were inspected: `evidence/h800-capacity-112k/` contains 34 small JSON files/76736 bytes; `evidence/h800-capacity-112k-network-fixed/` contains 34 small JSON files/40704 bytes. They contain launch/node/status/preflight receipts, not large raw logs. Only the successful run's 127-byte `student-finished.json` above is needed in Git; all other nested files remain untouched and untracked.

The following top-level captures remain untracked under `evidence/`, with no deletion or move:

- `h800-network-fixed-first-backward-context-20261109.json`
- `h800-network-fixed-first-optimizer-ack-20261109.json`
- `h800-network-fixed-first-runtime-20261109.json`
- `h800-network-fixed-first-scoring-memory-20261109.json`
- `h800-network-fixed-first-training-progress-20261109.json`
- `h800-network-fixed-version-one-weight-events-20261109.json` (3584896 bytes): complete native weight events, referenced by the committed checksum summary; raw equality is not recomputed by the offline checker.

Remaining untracked local evidence after selection: 73 files/3832196 bytes. These files are intentionally preserved, not pending cleanup or missing Git deliverables.

The full raw smoke archives remain at `/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-181120-274261-cloud-raw.tar.gz` (3911955 bytes) and `/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-192340-580111-cloud-raw.tar.gz` (458427717 bytes). Their Nov9 per-member hash verification and exact-root cleanup are recorded in `test_report_2026-11-09_cloud_cleanup.md`; this step does not repeat those cloud operations or extract archives. Retained raw logs remain in that same local directory.

## Verification limits

The checker validates small derived receipts, not original trajectory bodies or native tensor hashes. The raw checksum source remains local-only; Git alone cannot independently recompute that summary. Final process NIC/HCA values, whole-model equality/cryptographic publication provenance and physical OSS reclamation remain unverified. Scoring PyTorch allocation is not whole-device/backward peak memory. Two successful updates and the separate source simulation do not establish 200-update runtime trend coverage or formal-run acceptance. No parent merge/T02/T03 outcome is claimed.
