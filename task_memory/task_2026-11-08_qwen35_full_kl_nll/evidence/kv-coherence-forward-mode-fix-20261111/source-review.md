## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record both fixed-source review results and primary bounded CPU acceptance. |

# Forward-mode scope fix: fixed-source review

Component: the centralized EXTEND writer-observer scope in `Collector._targets()`.

The reviewed candidate is the selected three-file working-tree diff against `4b56d995ab2d1391a52d1c2333d1b9d8c60478ef`, not the entire task branch. The immutable review package is `/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-forward-mode-review-20261111/`. Its manifest and diff are retained locally as `review-manifest.json` and `reviewed-changes.patch` alongside this record. The preparation report is subsequently updated only to record these dispositions and driver results.

## Standards

Reviewer: native reviewer session `ses_e35f46424ffeD2bgM9p6f0ELo1`, TaskID `profile-kv-coherence-forward-mode-standards-review-20261111`.

**No findings.** The two production lines reuse the authoritative `ForwardMode.is_extend()` predicate before reading EXTEND-only lens. The regression follows the actual enum, generated runtime and context publication/restoration. All six malformed EXTEND variants and target-key consumption remain checked. The recorded final whole-file CPU runtime, 49 PASS in 19.77 seconds, meets the fast-test budget. No actionable documented-standard violation or code smell was identified.

## Spec

Reviewer: native reviewer session `ses_e35f46353ffe938i1L96qHKpIz`, TaskID `profile-kv-coherence-forward-mode-spec-review-20261111`.

**No findings.** The selected D40 correction keeps existing None-batch behavior, strict EXTEND validation, target selection, CPP keys, error isolation and physical/numeric drain gates. The report preserves RED, the initial budget miss, the unchanged fault assertions and final GREEN result. Supplied DECODE in the original-metadata replay is explicitly source/event inference, not a captured native enum.

## Primary acceptance and verification limits

Primary accepts this bounded **CPU/source fix only**. Both reviewers were read-only and did not rerun pytest or independently verify hashes. Primary closed the latter limitation in [checksum-verification.json](checksum-verification.json): all three frozen candidate hashes, the frozen diff and four owner checksum entries match; all 35 source identities and other manifest fields are unchanged except `runtime_sha256`; retained RCA replay/counts and the accepted R3 receipt are unchanged. No global 5,501/621-file rehash was performed.

CPU tests and driver dry-runs do not establish actual private-SO/observer-stream provenance, complete FRESH/OLD capture, independent 7955-row physical binding, KV numerics, a teacher correctness fix, or formal 200-update acceptance. The original failed r2 attempts and warm correctness failure remain preserved. Formal 04/05 remain HOLD.
