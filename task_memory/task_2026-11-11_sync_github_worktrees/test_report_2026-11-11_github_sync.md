## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record GitHub synchronization checks and the selected-content validation. |

# GitHub Worktree Synchronization Test Report

Date:2026-11-11, local timezone Asia/Hong_Kong. Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Git2.34.1; system Python `/usr/bin/python3`3.10.6, no conda activation. Image CPU test environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`3.12.13, pytest9.1.1, torch2.11.0+cu130, NumPy2.2.6, aiohttp3.14.3. No GPU operations.

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Worktree/remote inventory | Identify two requested branches and live refs | Two `.worktrees/` branches, origin=fwyc0573/miles; neither target ref exists remotely | PASS |
| Existing tracked scope | Preserve current project modifications | Capacity initially has0 tracked changes; image initially has14 tracked modifications and later task commits | PASS |
| Required pinned source | Retain exact prerequisites for existing CPU fixtures | Image selection includes57 required pinned source paths; none missing | PASS |
| Selected JSON/Python parse | JSON decodes and changed project Python parses under3.10 | No parse errors in static_checks.json | PASS |
| New-file limit | Every selected added file <=1024000 bytes | No oversized selected file | PASS |
| Strong credential/private-key patterns | No selected content matches private-key/GitHub token/AWS access-key signatures | No pattern hits | PASS, pattern coverage only |
| Selected content inventory | Preserve omitted raw content and record reasons | `9079` omitted files, `1228981986` bytes, inventory in omitted_files.json.gz | PASS |
| Tracked whitespace | `git diff --check` passes | Exit0 in image worktree | PASS |
| GitHub push/HEAD equality | Remote branch SHA equals local HEAD with upstream configured | Initial live remote/local 6db1d79af40fb40f9c510738ebe1c9d92dafb1aa with origin/agent-opd-image; final archive publication follows | PASS |

The initial untracked sizes were3,832,196 bytes for capacity and approximately1.25GB for image. A live task committed some source/docs during this inspection, so the inventory snapshot counts and final new-file counts need not match. The selection is explicit in selected_files.csv; files added by this sync's own record are included at staging time. Raw sample/event streams, large runtime traces, copied review/source trees and tool-local state are retained on disk. The compressed inventory contains paths/sizes/reasons, not artifact contents.

## Exact Git and Static Commands

```text
git worktree list --porcelain
git remote -v
git status --short --branch -uno
git diff --stat
git diff --cached --stat
git log -5 --format=%h
git submodule status
git fetch origin
git ls-remote --heads origin agent-opd-h800-capacity agent-opd-image agent-opd
git ls-files --others --exclude-standard -z
git diff --check
git rev-list --objects agent-opd-h800-capacity agent-opd-image --not --remotes=origin
git cat-file --batch-check=%(objecttype) %(objectsize) %(rest)
```

Inline `/usr/bin/python3` inspection scripts read every applicable Markdown rule, statuses, file sizes and the configured1000KB hook limit; inline existing CPU-environment Python imported the existing source manifests to select pinned dependencies. Inline system Python decoded selected JSON, parsed changed project Python with `ast.parse(..., feature_version=(3,10))`, and scanned selected bytes for strong credential signatures. Raw initial inventories and selected path lists are in `/data/ycfeng/tmp/sync-worktrees-20261111-agent-opd-image-initial.json` and `/data/ycfeng/tmp/sync-worktrees-20261111-agent-opd-image-selected.json`. No persistent test machinery was added.

Reachable unpublished history inspection:4,866 objects,2,804 blobs,102,267,675 logical blob bytes at that observation;0 blobs exceed100MiB. Twelve pre-existing history blobs exceed the current new-file hook limit but are already committed; no history rewrite or new large-file bypass was performed.

## CPU Validation

Image worktree command:

```bash
env TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_sglang_kv_coherence.py tests/fast/test_teacher_scoring_probe.py tests/fast/test_mamba_fp32_snapshot_probe.py -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/sync-worktrees-20261111-pytest --junitxml=task_memory/task_2026-11-11_sync_github_worktrees/pytest.xml
```

Expected:355 existing tests pass, with no native/GPU claim. Observed:354 passed,1 failed,0 skipped,4 warnings in33.66s. Failure: `test_coherence_serving_binding_consumes_actual_collector_receipt_cpu_only` raised `AttributeError: 'Collector' object has no attribute 'recurrent'`. The existing fixture bypasses the real constructor using `Collector.__new__`; the real constructor correctly initializes an unconfigured recurrent state. Restore that state in the fixture only; production behavior and assertions are unchanged.

Affected test rerun:

```bash
env TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py::test_coherence_serving_binding_consumes_actual_collector_receipt_cpu_only -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/sync-worktrees-20261111-fixture-pytest --junitxml=task_memory/task_2026-11-11_sync_github_worktrees/pytest_fixture.xml
```

Observed:1 passed,2 existing deprecation warnings in1.00s, exit0. The354 unaffected cases passed in the initial run; only the failed fixture test was rerun after its isolated fix. XML evidence is retained in the image worktree task directory. Capacity has no outstanding production code change to retest; its existing native acceptance is unaffected.

## Verification Limits

Branch publication is not scientific correctness, native CUDA capture, causal RCA completion, formal run approval or validation of every historical commit. No full repository/remote CI suite is claimed. Credential checking covers the named strong signatures rather than proving absence of every possible secret. Untracked raw artifacts remain local and explicitly enumerated.

## Cached Archive Whitespace

The first cached check found CRLF rows emitted by Python's CSV default; this task's inventories were normalized to LF. The image full cached check then flagged52 archived diff/patch/stdout/JUnit XML files. Diff context markers and historical failure trace spacing are original evidence, so they are preserved. Scoped validation excludes only these archive suffixes:

```text
git diff --cached --check -- . :(exclude)*.diff :(exclude)*.patch :(exclude)*.stdout :(exclude)*.xml
```

All staged source, configuration, Markdown and inventories remain in the check. This does not change archive contents or production behavior. Full diagnostic output is retained at `/data/ycfeng/tmp/sync-worktrees-20261111-image-cached-whitespace.txt`.

## Observed Publication

`git push --atomic --set-upstream origin agent-opd-h800-capacity agent-opd-image` created both branches; `git ls-remote --heads origin agent-opd-h800-capacity agent-opd-image` confirmed9f5a4bfe4e159d57894b8947a45ef667f9d7c4fd for capacity and6db1d79af40fb40f9c510738ebe1c9d92dafb1aa for image, equal to both local source HEADs. `git status --short -uno` was empty immediately after publication. During final record creation, the original image task changed6 Markdown files; include those small documentation changes and2 fresh JSON receipts in the final archive commit. Scoped `git diff --check` passed. No new production behavior or test case was introduced.

Final commands are `git push --atomic origin agent-opd-h800-capacity agent-opd-image`, `git ls-remote --heads origin agent-opd-h800-capacity agent-opd-image`, `git rev-parse HEAD`, `git rev-parse --abbrev-ref @{upstream}`, and `git status --short -uno`; final commit equality is checked and reported in the session after the archive commit.

## Concurrent New WIP Test

The original task added a direct producer/consumer test after the initial publication. Exact check:

```bash
env TMPDIR=/data/ycfeng/tmp PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py::test_recurrent_actual_generated_producer_receipt_joins_consumer_after_all16 -q -p no:cacheprovider --basetemp=/data/ycfeng/tmp/sync-worktrees-20261111-latest-test --junitxml=task_memory/task_2026-11-11_sync_github_worktrees/pytest_latest.xml
```

Expected: test completes its reduced CPU producer/consumer fixture. Actual:1 FAIL in3.01s, exit1; `metadata["rows"]` is a tuple and the new fixture calls `.extend`, raising `AttributeError` at test_teacher_scoring_probe.py:2409. Preserve this WIP test and failure XML; no current all-tests-green or native correctness claim is made. This test's implementation belongs to the ongoing original task.

At22:20:48+08 both committed HEADs still equaled live GitHub refs, but new tracked edits appeared in image. Save and push those latest edits with this report, then query live refs once more. Synchronization refers to the observed saved snapshot, not future writes by the continuing original task.
