## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Verify and remove 412 files/2.14 GB from the successful H800 smoke; cumulative logical cleanup is 2.15 GB. |
| 2026-11-09 | Verify and remove obsolete cloud duplicates from the terminal session-owned H800 smoke. |

# Session Cloud Cleanup Verification

## First failed smoke: scope and result

**PASS:** removed 167 files / **15,325,989 logical bytes** from the terminal smoke root:

`/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/capacity-h800-112k-20261109`

The remote workspace exposes this root at `/mnt/ws-jfs/ycfeng/miles-qwen35-full-kl-nll/capacity-h800-112k-20261109`. The exact task-root inventory contained only this smoke. Its largest file was the 6,949,381-byte rank0 log; there were no generated model, checkpoint or dataset payloads. The job failed before weight publication or training. This session had no GB-scale output to reclaim.

User authorization is recorded in `requirements.md`, **Cloud cleanup**. Source assets, live/formal/evaluation outputs, other tasks and shared volume trash were excluded. No platform job was stopped or deleted.

## Preconditions and retained evidence

- Exact job: `exp-1109-181120-274261`; UID `8af62b65-5176-472a-bb2d-86ab35776203`; personal creator and source were already verified.
- Terminal readback: `evidence/h800-native-terminal-20261109.json`, Failed at10:29:35Z; all five replicas Failed/Stopped. The local launcher subsequently exited1.
- Inventory: `evidence/cloud-cleanup-inventory-20261109.json`; all167 regular files have exact relative paths, sizes, SHA256, UID and mtime. Symlinks and special files were rejected.
- Raw local backup: `/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-181120-274261-cloud-raw.tar.gz`, mode0600, **3,911,955 bytes**. SHA256 `14f5cb41073dab396a8f2d378f259a417de376fe75f943bd3956d1d2b537eb23`. This restricted raw archive is not staged in Git.
- Backup verification: `evidence/cloud-cleanup-backup-20261109.json`; each archived file matched the inventory size and SHA256, with no duplicate/extra/missing members. No archive members were extracted.
- The retained full head log `/data/ycfeng/tmp/agent-opd-image/h800-exp-1109-181120-274261-head.log` independently matches its cloud SHA256. Selected redacted first-failure lines are preserved in `evidence/h800-first-native-failure-20261109.json`; structured startup/terminal receipts remain in local task evidence.

## Commands and checks

Environment: local Linux/zsh invoking Python3 and `ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng`; remote identity explicitly checked as`i-fengyicheng`. This was a file operation on the mounted personal volume, not a remote RJob operation. It used no GPU, conda environment or dependency change.

Executed bounded inventories:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng \
  'test "$(id -un)" = i-fengyicheng && timeout 60s du -ab /mnt/ws-jfs/ycfeng/miles-qwen35-full-kl-nll/capacity-h800-112k-20261109'
ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng \
  'test "$(id -un)" = i-fengyicheng && timeout 60s du -b -d 2 /mnt/ws-jfs/ycfeng/miles-qwen35-full-kl-nll'
```

Executed archive transfer with local noclobber and umask077:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng \
  'test "$(id -un)" = i-fengyicheng && timeout 60s tar -czf - -C /mnt/ws-jfs/ycfeng/miles-qwen35-full-kl-nll/capacity-h800-112k-20261109 r256' \
  > /data/ycfeng/tmp/agent-opd-image/h800-exp-1109-181120-274261-cloud-raw.tar.gz
```

Local `python3 -B -` verification used `tarfile.open(..., 'r:gz')`, rejected non-directory/non-regular members, required exact manifest membership, then checked each member's byte length and `hashlib.sha256`. All167 files and15,325,989 bytes matched; the already retained head log matched too.

Cloud directories were root-owned0755 and not writable by the personal user. The authorized deletion therefore used **bounded `sudo -n python3 -B -c` only for the exact smoke root**. Before any unlink, the command rechecked the literal root and its resolved path, rejected symlinks/special files, required exact inventory membership and job-ID ownership in every relative path, and rehashed all167 files. It then called `Path.unlink()` on those exact files and `Path.rmdir()` on their now-empty directories. It did not run a broad recursive delete or touch the shared trash. The result receipt is `evidence/cloud-cleanup-result-20261109.json`.

Independent post-delete SSH/Python check inspected the exact parent directory: `remaining_children=[]`, `deleted_smoke_exists=false`.

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Terminal job binding | Exact failed job, no running replicas | Failed; five replicas Failed/Stopped | PASS |
| Inventory and backup equality | Every file retained with exact bytes/hash | 167/167;15,325,989 bytes | PASS |
| Pre-delete drift | No changed, extra, missing or linked file | Exact membership and hashes unchanged | PASS |
| Cloud deletion | Only scoped obsolete smoke outputs removed | 167 files; exact root absent | PASS |
| Independent post-check | No remaining task-root output | Parent empty | PASS |
| Source/shared/live outputs | Untouched | No paths outside exact smoke root modified | PASS |
| Physical OSS quota reclamation | Requires independent storage measurement | Not measured; shared trash untouched | UNVERIFIED |

## Limits and continuing work

The measured reduction is in visible logical file bytes. JuiceFS trash/garbage collection can delay physical OSS reclamation; no physical-capacity reduction is claimed. Raw diagnostics remain locally available. Cleanup does not itself accept capacity or authorize parent integration.

## Successful network-fixed smoke, 12:50Z

After `exp-1109-192340-580111`, UID `28536e46-208d-4635-b648-27c782a09c9b`, and all five replicas reached Succeeded, the native capacity verdict was independently checked. The exact output root `/mnt/codesign-exp/ycfeng/miles-qwen35-full-kl-nll/capacity-h800-112k-network-fixed-20261109` contained **412 files/2136889910 logical bytes**. Large files were the 594158701-byte bank journal, two 319318921-byte rollout dumps, two 276248662-byte trajectory journals and native training dumps. They are generated smoke artifacts, not source models/datasets or formal/evaluation outputs.

The same restricted transfer mechanism retained the complete root:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng \
  'test "$(id -un)" = i-fengyicheng && timeout 300s tar -C /mnt/ws-jfs/ycfeng/miles-qwen35-full-kl-nll/capacity-h800-112k-network-fixed-20261109 -czf - .' \
  > /data/ycfeng/tmp/agent-opd-image/h800-exp-1109-192340-580111-cloud-raw.tar.gz
```

The local shell used noclobber and umask077. Archive size is **458427717 bytes**, SHA256 `1bda816ef0f16138c3376c947a2031f88eb92e046b860f4dfba185b02f8bd1c5`. Python streaming verification requires exact member paths and lengths and rehashes each member; all 412 files match the inventory. Nothing was extracted. The first verifier mistakenly reopened a member per block and raised `tarfile.StreamError`; retaining one member stream fixed that verifier. No cloud deletion had occurred.

The entire cloud tree was rehashed against inventory before unlink. Ordinary unlink was denied before the first file: `student/A` was root:root mode0755. A separate read verified all 412 files remained and noninteractive sudo was available. The same literal-root, resolve-path, regular-file, membership, size/mtime and hash checks then ran through `timeout 60s sudo -n python3 -B -c`; only the verified files were unlinked and their empty directories removed. No chmod/chown or broader recursive delete was used. Removal finished at **12:50:11Z**. Independent personal-user SSH/Python readback confirms `remaining_children=[]` and the exact smoke root absent.

Receipts: `evidence/cloud-cleanup-network-fixed-{inventory,backup,result}-20261109.json`. Original bank, trajectories, training dumps, event checksums and logs remain in the complete local archive. Selected native capacity/terminal evidence remains in this task; the archive is not committed to Git.

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Terminal ownership | Same admitted UID; all replicas terminal | Succeeded; four student replicas and teacher | PASS |
| Complete local retention | Every file matches size/hash | 412/412, 2136889910 bytes | PASS |
| Pre-unlink drift | No linked, changed, extra or missing file | Exact membership, mtime/size and hashes unchanged | PASS |
| Authorized removal | Exact terminal smoke root only | 412 files removed; root absent | PASS |
| Independent readback | Task cloud parent empty | Empty | PASS |
| Protected content | Sources, other tasks, shared trash untouched | No modification outside exact root | PASS |
| Physical OSS reclamation | Storage-level measurement required | Not measured | UNVERIFIED |

**Cumulative session cleanup: 579 files/2152215899 logical bytes (2.15 GB decimal).** This is verified namespace reduction, not a claim that OSS garbage collection has reclaimed that physical capacity. Both raw archives remain under `/data/ycfeng/tmp/agent-opd-image`.
