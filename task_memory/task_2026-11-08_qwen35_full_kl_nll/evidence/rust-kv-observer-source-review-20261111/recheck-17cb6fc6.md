## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Archive the independent Standards and Spec rechecks of the contention-oracle correction and receipt-preserving qualification routing. |

# Rust observer affected source recheck

## Scope and evidence

- Original task baseline: `20d0b3f4f24719afbb191fde5cb488e26367ed6c`.
- Original reviewed native candidate: `8683a032`; corrected candidate: `17cb6fc6`.
- Affected diff: `git diff 8683a032...17cb6fc6 --` the six paths in the immutable manifest.
- Immutable artifact: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/rust-kv-native-source-recheck-17cb6fc6-20261111/{manifest.json,changes.patch,commits.txt,files/}`.
- Scope: the Python native preparer, CPU probe, fast test module, preparation report, R3 resume configuration, and its source manifest. The unchanged Rust/adapter patch and collector were not reviewed again.

## Standards

Reviewer TaskID: `profile-rust-kv-native-source-standards-review-20261111`; session `ses_e368a5cf6ffeWSsoZ4ECXCatDi`.

**Original P2 CLOSED at source level; no new actionable defect or Nit.** `probe_rust_kv_observer.py:395–399` retains `Capture` and requires callback rows with no invalidations after the existing walk, join, and getter guards. Regression cases reject callback timeout and premature getter completion, and retain rejection of getter failure and a missing callback.

`sglang_rust_kv_observer.py:326–414` still checks source, ABI, ELF/hash, and command evidence. It removes only rejection based on an earlier final receipt's existence. The same finalizer writes beside the new qualification; the initial build path and failed-initial-qualification prerequisite are unchanged. The reviewer checked applicable repository rules and did not run tests or inspect R3 raw results.

## Spec

Reviewer TaskID: `profile-rust-kv-native-source-spec-review-20261111`; session `ses_e368a5cd0ffeZv0MtngyuGS6OB`.

**Original P2 CLOSED at source level; no new findings.** The retained capture and empty-invalidation assertion address `design_rust_kv_observer.md:65`: “CPU qualification must check the actual call topology for such concurrent core access.” Callback assertions converted into invalidations can no longer satisfy the previous false-PASS path.

The same receipt finalizer preserves prior R2 evidence and cannot publish a new PASS after a failed qualification. No production bridge, cache, lock, wait, stream, or mathematical behavior changed. The reviewer checked all six frozen paths and the current task requirements, plan, spec, tickets, and canonical designs; no commands or edits were performed.

## Verification limits

The preparation report records RED two failing subtests → GREEN 3/3 and 29/29 affected CPU/source checks with zero skips. Neither reviewer reran those checks. R3 platform success is separate from actual CPU semantic and container evidence acceptance.

These reviews grant no CUDA stream/payload, physical-index, 7955-row, all-16/6804 scoring, private GPU module-origin, all-TP, race, root-cause, performance, or formal-200 acceptance. The standalone GIL contrast artifact remains absent, arbitrary unscheduled Mutex reentry is unsupported, and the original bundled binary's source commit remains unverified. Earlier bounded R2 and CPP/WIT acceptance is preserved.

**Totals:** Standards: original P2 closed, zero new findings. Spec: original P2 closed, zero new findings. Actual R3 CPU evidence acceptance remains a separate primary decision.
