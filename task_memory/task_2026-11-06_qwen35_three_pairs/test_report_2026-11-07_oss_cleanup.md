## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Record the bounded authorized-root inventory and protected evidence; prepare exact obsolete loader-weight cleanup pending primary terminal-status receipts. |
| 2026-11-07 | Complete the storage-scope checkpoint; pause only deletion awaiting two loader terminal receipts, with no cloud bytes removed yet. |
| 2026-11-07 | Execute four identity-rechecked obsolete shard unlinks after exact Failed receipts; preserve all evidence, verify 15.668 GiB logical removal and 10.456 GiB remaining usage, and document physical-quota limits. |
| 2026-11-07 | Append read-only post-training inventory after A/B accepted final exports:33.664 GiB retained, both final packages protected, no newly eligible failed-run large artifact and zero additional deletion. |

# QWEN-P3-OSS-CLEANUP

## Scope and current result

The user explicitly authorized removal of obsolete task-generated codesign artifacts because storage was approaching capacity. This storage-only subtask has no GPU, StepMind, platform, authentication, job-stop, delegation, or Git operations.

- Authorized cloud root: `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs`.
- Authorized SSH view: `shai-ycfeng:/mnt/ws-jfs/ycfeng/miles-qwen35-three-pairs`.
- Protected jobs: A `exp-1107-173758-712234`, B `exp-1107-173758-806531`, C `exp-1107-150849-814926`.
- Protected frozen input: `population-exp-1106-233008-986003`.
- Preserve all initial acceptance, failed-run numerical/RCA, publication, and successful baseline-loader evidence. Do not inspect or modify other cloud roots, original model assets, or shared trash.

**PASS — four exact obsolete shard files were unlinked**, removing **16,823,117,792 logical bytes (15.668 GiB)** from the visible task namespace. Their reported allocated sizes sum to16,823,118,848 bytes; that is not a physical-quota reclamation claim. Remaining task usage is **11,226,739,944 logical bytes (10.456 GiB)**.

The preceding usage is the original10:03Z post-delete snapshot. The later read-only [post-training inventory](#post-training-inventory--2026-11-07-135421z) is appended below; original deletion history and metrics are unchanged.

D19 in [requirements.md](requirements.md) owns the explicit destructive authorization. The primary's [loader terminal receipt](evidence/oss-cleanup-loader-terminal.json) verifies both `exp-1107-083839-053284` and `exp-1107-093036-947852` are **Failed**, creator `i-fengyicheng`, with the expected native-text-loader display names. Only their two safetensors shards each were removed. All configuration, tokenizer, shard index, and export reports remain in cloud; original probe reports/logs remain locally. The accepted `text-loader-probe/exp-1107-100927-934443/model` remains complete. No further cleanup is pending.

## Inventory and evidence retention

The complete scan finished in **36.441 seconds**, inspecting **1,114 entries / 952 regular files**, with no symlink traversal, device-boundary traversal, or inspection errors. It used streaming `os.scandir`, a 55-second internal deadline, 100,000-entry limit, an 80-file largest-file heap, and a 30-GiB address-space ceiling. No tensor/model bytes were loaded.

| Directory | Logical bytes | GiB | Treatment |
| --- | ---: | ---: | --- |
| Entire authorized task | 27,844,513,085 | 25.932 | Measure again after cleanup; active outputs may grow. |
| `text-loader-probe` | 25,303,573,887 | 23.566 | Three copied initial 4B text models dominate usage; remove only obsolete shard files after terminal confirmation. |
| `first-round` | 995,682,977 | 0.927 | Retain all raw numerical, rollout, optimizer/publication, and RCA evidence, including terminal attempts. |
| `native-prerequisites` | 674,632,440 | 0.628 | Retain complete initial baseline acceptance chain. |
| `population-exp-1106-233008-986003` | 870,623,781 | 0.811 | Preserve all three frozen population files. |

The three loader copies have equal shard names/sizes and equal SHA256 values for `config.json`, `model.safetensors.index.json`, `qwen_text_export.json`, `tokenizer_config.json`, and `chat_template.jinja`. Their large shard contents were **not** hashed or claimed byte-identical. All shard files have `nlink=1`. The obsolete probes are superseded rather than accepted final student artifacts; their original local reports show `INCOMPLETE`. The successful later probe has `PASS` baseline content/inference evidence and remains untouched.

Existing local evidence retained without copying large cloud data:

- `evidence/text-loader-probe-exp-1107-083839-053284.json` and `.log`.
- `evidence/text-loader-probe-exp-1107-093036-947852.json` and `.log`.
- `evidence/text-loader-probe-exp-1107-100927-934443.json` and `.log`.
- Primary terminal-status receipts in `evidence/oss-cleanup-job-statuses.json`.
- Exact terminal loader receipts in `evidence/oss-cleanup-loader-terminal.json`.

No GPU memory snapshot dominates the authorized task root. Apart from the copied loader weights, the largest non-model artifact is the protected frozen `train.jsonl`; historical `.pt` score/rollout dumps are tens of MiB, not the high-value cleanup target.

## Exact execution and environment

Local inspection driver: `python3` **3.10.6**, no conda activation. Remote reader: Python **3.12.3**, GCC 13.3.0, no model imports.

All initial and post-delete SSH inspection commands used:

```text
timeout 60s ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng 'timeout 60s python3 -'
```

Python stdin supplied the exact authorized root and streaming no-follow walk, setting `resource.RLIMIT_AS = 30 * 1024**3` bytes. The local driver used `subprocess.run(..., timeout=65)`. The raw generated inventory is at `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-oss-inventory-20261107.json`; compact durable sizes and deletion receipts belong in `evidence/oss-cleanup-20261107.json`.

Deletion commands, in order:

```text
timeout 60s ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng 'timeout 60s python3 -'
timeout 60s ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng 'sudo -n timeout 60s python3 -'
```

The first command failed **before the first unlink**, with `PermissionError: [Errno 13] Permission denied` on the first listed shard. A scoped ownership check showed SSH euid/egid10250 and task/target directories owned by `root:root`, mode0755, with no write/execute access for that identity. The second command used noninteractive sudo for the **unchanged exact four operations**, without chmod/chown, recursive deletion, or trash access, and exited0. Each operation rechecked regular-file/device/root boundaries, size, allocated size, inode, `nlink=1`, and nanosecond mtime immediately before `os.unlink(path)`, then confirmed `not os.path.lexists(path)`. All four candidates were validated before the first unlink.

Both complete stdin Python sources, source SHA256 values, argument lists, pre-delete signatures, per-file receipts, return codes, and the original permission error are retained in [the manifest](evidence/oss-cleanup-20261107.json). Raw deletion logs are `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-oss-delete-20261107.jsonl` and `qwen-oss-delete-sudo-20261107.jsonl`; raw post-delete inventory is `qwen-oss-post-inventory-20261107.json` in the same directory. No separate task storage-cleanup mechanism was found; explicit four-file Python unlink avoids any recursive cleanup scope.

The backing mount exposed to this SSH session is **virtiofs** at `/mnt/ws-jfs`; it does not expose JuiceFS trash-retention policy. `statvfs` is shared-volume capacity, not a task-specific physical/quota receipt. At 09:55:17Z it reported 484,107,653,120 available bytes; at the end of inventory it reported 721,514,201,088 available bytes. The unrelated increase is not attributed to this cleanup, which had not deleted anything.

Immediately before successful deletion at10:01:46Z, available space was3,507,023,147,008 bytes; immediately afterward at10:01:50Z it was3,507,210,420,224 bytes, a187,273,216-byte increase. The final post-inventory reading was3,612,632,961,024 bytes. These shared readings **do not verify16.823 GB physical reclamation**. Concurrent operations, delayed accounting, and possible underlying trash retention cannot be separated through this mount. No shared `.trash` listing or purge was performed; no task-owned purge scope is claimed without evidence identifying it.

## Exact removed paths and results

Every path below is relative to the authorized task root; prepend `/mnt/ws-jfs/ycfeng/miles-qwen35-three-pairs/` for the exact executed SSH path, or `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/` for the cloud path.

| Exact relative target | Pre-delete logical bytes | Pre-delete allocated bytes | Result |
| --- | ---: | ---: | --- |
| `text-loader-probe/exp-1107-083839-053284/model/model.safetensors-00001-of-00002.safetensors` | 5,187,839,368 | 5,187,839,488 | Unlinked; absent |
| `text-loader-probe/exp-1107-083839-053284/model/model.safetensors-00002-of-00002.safetensors` | 3,223,719,528 | 3,223,719,936 | Unlinked; absent |
| `text-loader-probe/exp-1107-093036-947852/model/model.safetensors-00001-of-00002.safetensors` | 5,187,839,368 | 5,187,839,488 | Unlinked; absent |
| `text-loader-probe/exp-1107-093036-947852/model/model.safetensors-00002-of-00002.safetensors` | 3,223,719,528 | 3,223,719,936 | Unlinked; absent |

The two obsolete model directories are now retained **metadata-only remnants**, not loadable model artifacts. Their local historical reports remain `INCOMPLETE`; no accepted or final model was removed.

## Post-delete verification — PASS

One planned post-delete no-follow inventory completed in **55.495 seconds**, inspecting **1,138 entries / 968 regular files**, with no skipped symlink/device boundaries or inspection errors. All four deleted paths remain absent.

| Remaining directory | Logical bytes | Reported allocated bytes | Files |
| --- | ---: | ---: | ---: |
| Entire task | 11,226,739,944 | 11,226,927,616 | 968 |
| `first-round` | 1,201,027,628 | 1,201,147,904 | 668 |
| `native-prerequisites` | 674,632,440 | 674,692,608 | 271 |
| frozen population | 870,623,781 | 870,624,256 | 3 |
| `text-loader-probe` | 8,480,456,095 | 8,480,462,848 | 26 |

Observed task reduction is16,617,773,141 bytes, smaller than the exact16,823,117,792 bytes unlinked because `first-round` concurrently grew205,344,651 bytes. This growth is retained active output, not a cleanup failure.

- **29 protected immutable files** retain exact size/allocated-size/inode/nlink/mtime signatures and, for files under1 MiB, exact SHA256 values: frozen population, all selected metadata, and complete accepted loader.
- **Ten retained directory comparisons** have unchanged byte totals/file counts: complete `native-prerequisites`, population, accepted loader, and all seven confirmed terminal training attempts. All their raw numerical/RCA/publication data was retained.
- Current A/B student and teacher directories retained their exact inode identities. Pending C had no cloud student/teacher directory before or after deletion; none was removed.
- All **six local probe report/log SHA256 values** remain unchanged. No cloud data was copied into local storage.
- Only the four declared candidates were mutated. No platform/GPU/authentication/job-stop/Git/delegation operation or other-root/trash mutation occurred.

## Verification criteria

1. PASS only after exact eligible obsolete shard paths are removed and their pre-delete file sizes, identities, status provenance, operation, and post-delete absence are recorded.
2. Protected active job data, frozen population, accepted loader copy, raw historical baseline/RCA/publication data, and retained local reports/logs remain present and unchanged where immutable; growing active outputs may add data.
3. Remaining authorized task-root usage is measured with the same bounded no-follow inventory.
4. Distinguish bytes unlinked from the visible task namespace from physical quota reclamation. Never infer exact physical space release from a shared-volume free-space delta; never purge shared trash.

The completed durable manifest is [oss-cleanup-20261107.json](evidence/oss-cleanup-20261107.json), state `completed_logical_cleanup_physical_reclamation_unverified`. Existing terminal training attempts were deliberately retained: their combined usage is under one GiB and preserves unique RCA/publication data. The high-value cleanup is complete; stop further scans or deletion.

Local verification passed: before/after inventory arithmetic, four identity-rechecked unlink receipts and path absence, all29 protected signatures, all10 retained-directory comparisons, all six local evidence hashes, manifest JSON, and report Modification History. Physical quota reclamation remains **UNVERIFIED**, not a blocker to the verified scoped logical cleanup.

## 1. 规划完成情况

**汇总：** PASS 4｜BLOCKED/FAILED/SKIPPED 0｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| exact-root bounded inventory | PASS | Complete 36.441-second scan; 25.932 GiB, no skipped/error paths. |
| protected evidence / high-value target selection | PASS | All baseline/RCA chains and accepted loader retained; only four superseded shard files selected. |
| obsolete-byte removal | PASS | Two verified Failed jobs; four exact shards absent,15.668 GiB logical bytes unlinked. |
| post-delete verification and final manifest | PASS |10.456 GiB remaining; protected files/evidence intact; physical-quota limitation explicit. |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本 cleanup 分派至 post-delete 验证完成｜**当前前沿：** delegated cleanup 已完成；主 task 的 formal training 独立继续

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | Single bounded inventory; no generalized cleanup framework or extra tests. |
| D2 细节反复重试 | CLEAR | One permission failure diagnosed as root-owned0755 directories; unchanged exact sudo unlink then passed. |
| D3 支线问题修补 | CLEAR | Cleanup is explicitly requested; no unrelated repairs. |
| D4 可并行任务停滞 | CLEAR | Primary owns status checks; inventory and evidence preparation ran independently. |
| D5 超范围镀金 | CLEAR | Only the delegated report and small manifest are added. |
| D6 分析空转 | CLEAR | Inventory identified four files responsible for nearly all obsolete reclaimable bytes; stop expansion. |
| D7 路线违背 | CLEAR | No platform/GPU/auth/Git/delegation operations, no other cloud roots or shared trash. |

**文档检查：** 本 delegated cleanup 的 S1–S6 均未发现明显缺陷；主 task 的 training 状态由 primary 维护。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. 将 actual logical removal、remaining usage、report/manifest 路径返回 primary，结束本 cleanup。
2. 主 task 的 A/B/C formal training 并行继续；不把 shared physical-quota 未核验当作 job 操作或 trash purge 授权。

## 4. 最值得关注的 3 点

1. 四个旧 loader shard 已实际 unlink16,823,117,792 logical bytes，约15.668 GiB；task 剩余10.456 GiB。
2. 所有当前 A/B/C、frozen population、初始 acceptance/RCA/publication 和 accepted loader 保持保护；没有必要删除它们。
3. Shared virtiofs/statvfs 不能证明等量物理 quota 已回收；shared trash 未访问，且不在本 cleanup 范围。

## Post-training inventory — 2026-11-07 13:54:21Z

**PASS — read-only follow-up;33.664 GiB currently retained, no new eligible failed-run large artifact, zero newly deleted bytes.** The parent confirms A/B have normal terminal completion and accepted final `hf/step_99` packages; both distinct packages must remain. C `exp-1107-150849-814926` remains queued. Parent-provided completion/acceptance is provenance, not a platform query or new numerical qualification performed by this storage subtask.

The existing manifest has a new append-only `post_training_inventory` entry. All pre-existing fields, including the original four-path deletion, snapshots, totals, permission failure, execution source and physical-quota limitation, are preserved. The entry records a canonical SHA256 of the original manifest, exact new inspection command/source, package file metadata and current sizes.

| Retained path, relative to the authorized task root | Logical bytes | Reported allocated bytes | Files |
| --- | ---: | ---: | ---: |
| Entire task | 36,146,058,741 | 36,147,331,072 | 4,082 |
| `first-round` | 26,120,346,425 | 26,121,551,360 | 3,782 |
| `first-round/student/A/exp-1107-173758-712234` | 12,585,624,807 | 12,586,173,952 | 1,587 |
| `first-round/student/B/exp-1107-173758-806531` | 12,580,355,374 | 12,580,905,984 | 1,587 |
| `native-prerequisites` | 674,632,440 | 674,692,608 | 271 |
| `population-exp-1106-233008-986003` | 870,623,781 | 870,624,256 | 3 |
| `text-loader-probe` | 8,480,456,095 | 8,480,462,848 | 26 |

The final packages below are **included in**, not additional to, their respective accepted-run totals:

- **A:** `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/A/exp-1107-173758-712234/hf/step_99` —8,434,495,085 bytes (7.855 GiB),25 files, `.complete`, configuration and index present, all16 indexed safetensors shards present and nonempty.
- **B:** `/mnt/codesign-exp/ycfeng/miles-qwen35-three-pairs/first-round/student/B/exp-1107-173758-806531/hf/step_99` —8,434,495,085 bytes (7.855 GiB),25 files, `.complete`, configuration and index present, all16 indexed safetensors shards present and nonempty.

Equal package sizes do not establish equal weight contents and are **not** grounds to deduplicate the two accepted artifacts. Both packages and all accepted-run raw rollout, trajectory, train-data, loss-debug, dashboard and publication/event evidence remain protected.

### Inspection method and observed retention

The one SSH read-only command was unchanged from earlier inspection:

```text
timeout 60s ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng 'timeout 60s python3 -'
```

The remote Python3.12.3 process had euid10250, used a30-GiB address-space ceiling, and completed in **7.282 seconds**. It scanned only seven explicitly selected scopes under the exact authorized root: `first-round/student/{A,B,C}`, `first-round/teacher`, `native-prerequisites`, frozen population, and `text-loader-probe`. Separate streaming scans ran concurrently with52-second internal limits and100,000-entry caps each. No symlink/device boundary was followed; no inspection error or incomplete scope occurred. The authorized root's four immediate children exactly match the inventoried roots. No shared-volume/global scan, sudo, tensor loading, cloud copying or deletion occurred.

- All **35 selected historical/current student and teacher run identities** are unchanged; there is no new loader-copy directory.
- All **29 original protected file signatures**, all **10 retained baseline/RCA/publication/population/accepted-loader directory size/count comparisons**, and all **six local report/log SHA256 values** pass unchanged.
- The original **four deleted obsolete shards remain absent**. Existing metadata-only remnants are retained; there is no regenerated failed-copy weight artifact.
- Queued C has no student/teacher cloud directory yet, as in the original snapshot. All existing C historical evidence is retained; no C path was created or removed.
- Current usage grew24,919,318,797 bytes from the original post-delete snapshot, from protected accepted A/B outputs rather than a new failed-run identity. Those outputs are not cleanup candidates.
- **New eligible paths: none. New deleted files: none. New deleted bytes:0.** No further deletion is proposed or performed without parent terminal/protection confirmation.

### Limits

This verifies file presence, index/shard coverage, directory sizes and retained metadata signatures, **not** another HF content-hash/inference acceptance run. Large tensor contents were not read or hashed. A/B's accepted native reload evidence remains owned by the primary and [HF report](test_report_2026-11-07_hf_reload.md).

The read-only `statvfs` observation reported12,130,138,939,392 available bytes on the shared virtiofs-backed volume. It is not task-specific physical/quota evidence. Original physical quota reclamation remains **UNVERIFIED**, and zero additional deletion occurred. No shared trash was listed or modified. This follow-up is complete and non-blocking for A/B review and C scheduling.

### 1. 规划完成情况

**汇总：** PASS3｜BLOCKED/FAILED/SKIPPED0｜TODO0

| Follow-up subtask | Status | Evidence |
| --- | --- | --- |
| Narrow read-only current-usage inventory | PASS | Seven complete selected scopes,33.664 GiB retained. |
| Accepted packages/protected evidence and new-obsolete eligibility | PASS | Both separate final packages intact; unchanged historical identities/evidence; no new eligible artifact. |
| Append report/manifest without changing original deletion | PASS | Append-only inventory, original metrics preserved, zero new deletion and quota limits explicit. |

### 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** post-training follow-up分派至本次检查完成｜**当前前沿：** storage follow-up已完成；A/B review与C scheduling由primary独立推进

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 Tooling polish | CLEAR | One bounded read-only inspection; no cleanup framework or additional tests. |
| D2 Retry loop | CLEAR | Inspection passed once without retries. |
| D3 Side quest | CLEAR | Only the explicitly requested follow-up scopes/files. |
| D4 Stalled frontier | CLEAR | Non-blocking storage follow-up; no formal-run dependency added. |
| D5 Gold-plating | CLEAR | Append only to the two assigned artifacts. |
| D6 Analysis sprawl | CLEAR | No eligible new artifact found; stop after recording current usage. |
| D7 Off-route | CLEAR | No deletion/platform/GPU/auth/delegation/shared-trash operations. |

**文档检查：** delegated follow-up范围内S1–S6无明显缺陷；原有metrics是保留的历史snapshot，不用当前usage覆盖。
**归因：** 无。

### 3. 纠正建议

**分支：** A：scope合理，无需改变。
**需停止的偏离行为：** 无。
**接下去的路线：** 返回current usage、两份final保留检查、none eligible和quota limits；停止本follow-up，不阻塞A/B review或C scheduling。

### 4. 最值得关注的 3 点

1. 当前保留33.664 GiB；A/B各自accepted `hf/step_99`均完整保留。
2. 无新增明确可删除的failed-run大文件，本轮删除0 bytes。
3. 原四路径15.668 GiB logical deletion/history完整保留；physical quota仍未验证，shared trash未访问。
