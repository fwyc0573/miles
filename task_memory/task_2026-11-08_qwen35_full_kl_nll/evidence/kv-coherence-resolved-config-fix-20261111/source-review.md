## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record independent Standards/Spec source reviews and primary checksum verification for the resolved-config guard fix. |

# Resolved-config collector guard: fixed source review

Component: `initialize_runner`, its fast regression tests and the preparation report.
Base: `9da079197bcd97eeab2f2677f4854e49d46728b5`; three-file uncommitted candidate.
Frozen artifact: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/kv-coherence-resolved-config-review-20261111/` (`manifest.json`, `changes.patch`, `files/`).
Patch SHA256: `29ff01ef7e6cace7e3b157c42eb82e3f85eac84508543718d48c5b0aadb88b21`.
Exact file identities: [checksum-verification.json](checksum-verification.json).

## Standards

Reviewer task: `profile-kv-coherence-resolved-config-standards-review-20261111`; session `ses_e362a1fa9ffeFwS4ZZ7ueTP2HA`.
**No findings:** zero hard violations and zero actionable smell findings.
The two-line change reuses the existing `resolved_dict()` owner, retains all six expectations and independent allocator/topology guards, and adds no fallback or duplicate resolution policy. Generated-initializer tests are proportional and accurately described as CPU seams.

## Spec

Reviewer task: `profile-kv-coherence-resolved-config-spec-review-20261111`; session `ses_e362a1e7dffe9euOxRqbM3GA8C`.
**No findings.** Existing resolved configuration is read once and compared as a mapping. No raw mutation, flag, cache/kernel/stream/wait/synchronization/math/protocol change was found. Source manifests retain 35 identities and additional native pins; only the generated runtime hash changes.

## Integrity, verification and release boundary

Both reviewers were read-only and did not independently compute file hashes or rerun tests. Primary independently recomputed the frozen patch and all three file hashes, and confirmed current file bytes equal the reviewed snapshots: **PASS**, recorded in `checksum-verification.json`.

Recorded CPU verification: RED1 FAIL → GREEN1 PASS; 17 affected PASS; 69 composed PASS, zero skips. Primary also ran both controller dry-runs: `submitted=false`, four H800 each, identical allocation/environment/worker command except the new `admission-{A,B}-r2` output directory. Evidence: `../teacher-scoring-kv-coherence-probe-20261111/controller-dryrun-comparison-resolved-config-r2.json`.

Primary accepts the bounded CPU source fix. Updated native capture remains unverified: actual private module/ELF, OLD callback/stream, independent physical indices, 7,955 warm OLD rows, cold-zero coverage, all16/6,804 scoring reproduction with active capture and KV numerics still require the new bounded H800 diagnostic. Original A/B capture failures, accepted retained scoring controls, R3 CPU/WIT acceptance and formal04/05 HOLD remain unchanged. This is not a teacher warm-correctness or root-cause fix.
