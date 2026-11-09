## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Accept Ticket01 in-place source audit and parity from the completed CPU job; refresh the upstream execution blocker. |

# In-place SWE-1003 source audit and execution readiness

## Run and evidence

- Configuration and exact launch command: `source_audit_config.json` and `test_report_2026-11-09_review_execution.md`, section In-place CPU RJob.
- Job: `exp-1109-031258-820360`; personal creator `i-fengyicheng`, 8 CPU, 0 GPU, 32000 Mi memory, pinned image and current-host NFS source verified by the admission receipt.
- Python 3.12.13, transformers 5.19.0, mounted environment `/data/ycfeng/envs/miles-agent-opd-cpu`; no conda activation. Query client: `/data/ycfeng/tmp/stepmind-env/bin/python`, Python 3.10.6, runbook section2 personal-auth/proxy initialization.
- At `2026-11-09T05:11:30Z`, direct personal `get_rjob_client()` queries confirmed job and exact replica `exp-1109-031258-820360-cfcd2084` both **Succeeded**. Job finish time: `2026-11-09T00:24:08Z` (08:24:08 HKT). The replica log includes `SWE1003_IN_PLACE_AUDIT_AND_PARITY_PASS`; no stop annotations. Filtered receipt: `evidence/source-audit-terminal-20261109.json`. A separate container exit-code field was not returned by this filtered inspection and is not claimed.
- Inputs remained in their approved posttrain directory; no dataset copy. Source manifest reports `COMPLETE` and `read_in_place=true`.

Artifacts under `evidence/source-audit-20261109/`:

1. `swe1003-source-manifest.json`: eight paths, hashes, sizes, mtimes and visual exclusions.
2. `swe1003-source-audit.json`: counts, schema, length statistics and both simulations.
3. `parity/input-parity.json`: exact executed argv and each check's result.
4. `parity/input-config.json` and `parity/input-source-manifest.json`: bound input identities and verified source bytes.

## Acceptance results

| Check | Expected / passing condition | Observed | Verdict |
| --- | --- | --- | --- |
| Source identity | All eight original files; manifest/audit identities and totals agree | 16,559,540,463 bytes; matching paths and SHA256, source manifest COMPLETE | PASS |
| Counts and exclusions | Record original, mask-eligible and native visual-filter populations separately | 9,254 conversations; 892,620 assistants; 878,783 loss-mask-eligible; exclude102 visual conversations /10,008 eligible turns; remaining9,152 conversations /868,775 eligible turns before length filtering | PASS |
| D26 distribution | Measure the eligible-turn median and report if clearly below81 | min5, median90, P90153, max355, mean94.9273 before length rejection; retain approved32×8 | PASS |
| Qwen length audit | Record actual configured128K rejection behavior | 5,311 conversations have overlength tails; 239,015/868,775 eligible turns rejected (27.5117%); longest-prompt median142,076 tokens | PASS, limitations below |
| M=1 native parity | First512 draws match one native source, remaining counts and normalized messages/tools | All512 match, all have tools; 16.2555s | PASS |
| M=32, block8 order | First2,048 draws ascend without duplicates; file-order admission; at most32 open; independent instances agree | Two identical sequences; maximum32 open; longest consecutive run8; remaining counts match | PASS |
| Construction / draw cost | Record measured CPU costs | 0.02146s construction/instance; 9.7180ms mean draw | RECORDED |
| Complete configured CPU workload | Source audit and parity outputs plus terminal success | Both artifacts complete; job/replica Succeeded; worker completion marker present | PASS |

The `parity/input-source-manifest.json` records eight locally verified files and16,559,540,463 bytes. Its `counts_independently_recomputed_in_this_check=false` is intentional: counts come from the full source audit, not a second count scan in parity.

## Measured scheduling behavior

Both simulations fill200 updates ×256 accepted turns =51,200 and have zero repeated turns, cursor epoch0. They model source order and length rejection only, not generation failures or optimizer success.

| Configuration | Raw draws / length rejections | Conversations | Update-span median / P90 / max | Conversations spanning at least11 updates |
| --- | --- | --- | --- | --- |
| 32×8 | 71,737 /20,537 | 745 | 7 /9 /12 | 17/745 (2.2819%) |
| 1×8 | 72,387 /21,187 | 735 | 1 /2 /2 | 0/735 |

The32×8 simulation covers a median25 conversations/update, not32 after filtering. A pre-length median90 does not imply that most conversations obtain a k=10 trend. The measured long-span fraction is not a measured trend fraction: no RKL baselines, successful optimizer updates or generation failure distribution exist in this CPU run. No scheduling/config change is made.

## Source metadata and limits

- All9,254 first messages **omit `preserve_thinking`**; all contain `reasoning_effort=null` and `tools`. The Qwen configuration explicitly supplies `preserve_thinking=true` and `enable_thinking=true`. Source metadata absence must not be reported as a true source flag; the requested disclosure is recorded here before any formal run.
- Native SWE instance/repository/commit identities remain unverified/null. Exact first-user text yields955 prompt groups, with zero missing proxies; these are not verified task identities. Consecutive32-conversation windows contain29–32 prompt groups (median32).
- Length totals use the existing bisection assumption that the preserving Qwen prompt prefix length is nondecreasing. The audit does not save the full post-length per-conversation distribution; it must not be invented from the pre-length median.
- Synthetic failure/exclusion/finished-report cases in parity remain synthetic. Real-source parity covers normalized messages/tools and ordering; it does not assert Step/Qwen token-ID or byte equality.

## Upstream gate, checked independently at05:10Z

Read-only task `profile-upstream-20261109` found `agent-opd` at `d8c27b75`; no newer capacity acceptance than the prior records. Latest attempted D12 bank `exp-1109-010244-280221`:227 valid,2 teacher HTTP400,27 generation-pending at1800.0097s, zero updates. Fixing the two teacher input errors alone would produce at most229, still below231. The OOM patch's historical run reached backward but was externally stopped without an optimizer ACK.

Thus Ticket01 is **done**, while D1/D22 still block merge and Ticket02/03 integration. The upstream task must resolve acquisition throughput and complete its representative256-slot native capacity acceptance, including two successful optimizer updates and second scoring. CPU audit success does not satisfy that gate. Upstream's rollout placement decision remains owned by `agent-opd`; no merge, new RJob or formal-cell launch was performed in this status refresh.

## Record verification

```bash
python3 tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll
git diff --check
```

Observed:21 documents,6 tickets,75 links,22 anchors, valid dependency order and arithmetic, zero errors; diff whitespace check PASS. No training code changed and no GPU test was run for this acceptance record.
