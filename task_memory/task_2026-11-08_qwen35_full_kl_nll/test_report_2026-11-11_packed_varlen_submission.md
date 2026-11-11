## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record the two authorized true-packed operator admissions and initial API identity checks; retain execution and numerical acceptance as pending. |

# True-packed operator submission

**Submitted under the existing D40 authorization. The initial API snapshot shows both jobs Pending; neither physical GPU execution nor native numerical acceptance is claimed.** This is a synthetic operator diagnostic, not an actual teacher-scoring/value-witness run or formal training.

## Resources and identity

| Pair | Actual RJob | Initial API phase | Declared resource |
| --- | --- | --- | --- |
| A | `exp-1111-221303-584851` | Pending | H800/codesign,1 replica,GPU1,CPU8,memory64000Mi,non-preemptible |
| B | `exp-1111-221303-041018` | Pending | Same |

Both exact job records confirm creator `i-fengyicheng`, image `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`, and declared local NFS `100.96.128.195:/data/ycfeng:/data/ycfeng`. Config/probe/preparer SHA256s match the live files from accepted source archive `4acfa47e`. Actual worker mount use, device type/count, container termination and native values remain pending. The admission inventory reports personal committed GPU74 before B and75 before A, with no personal ceiling; no other listed jobs were inspected or controlled.

Evidence: [A admission](evidence/packed-varlen-preparation-20261111/admission-A-r1.json), [B admission](evidence/packed-varlen-preparation-20261111/admission-B-r1.json), [A initial API](evidence/packed-varlen-preparation-20261111/initial-platform-A-r1.json), [B initial API](evidence/packed-varlen-preparation-20261111/initial-platform-B-r1.json). Actual API memory is64000Mi; do not substitute65536Mi when checking platform identity.

## Exact entry and environment

Host: `kun-workspace-vgen2`; working directory `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`; local Python `/data/ycfeng/tmp/stepmind-env/bin/python`,3.10.6. Personal credentials are loaded only into process environment by the authenticated handbook recipe; no credential values are retained. `STEPMIND_BACKEND=rjob`, `PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`, and `PYTHONPATH` contains this worktree before `/data/ycfeng/steptron`.

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B /data/ycfeng/tmp/opencode-v2-tmp/opencode/submit-packed-varlen-20261111.py --pair A --config task_memory/task_2026-11-08_qwen35_full_kl_nll/mamba_snapshot_packed_prefix_A_config.json --receipt task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/packed-varlen-preparation-20261111/admission-A-r1.json
/data/ycfeng/tmp/stepmind-env/bin/python -u -B /data/ycfeng/tmp/opencode-v2-tmp/opencode/submit-packed-varlen-20261111.py --pair B --config task_memory/task_2026-11-08_qwen35_full_kl_nll/mamba_snapshot_packed_prefix_B_config.json --receipt task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/packed-varlen-preparation-20261111/admission-B-r1.json
```

The admitted `worker_command` is retained unchanged in each admission. It calls `/opt/sglang/bin/python3 -u -B -m tests.manual.agent_opd.probe_mamba_fp32_snapshots` with its corresponding config, pinned image and fresh `native/{A,B}/<jobID>` output, under the existing3600s timeout plus90s termination grace. Worker-local temporary storage owns intermediate tensors/cache; persistent output is compact evidence. Both processes use the local Python `RJobBackend`, the existing policy/lock, and dynamically declared personal cloud and authorized read-only source volumes. No remote submitter or alternate backend is used.

Local launcher IDs: A `sh_1caf464fa001A3O9xR35hWeGcD`, B `sh_1caf4650c001MpUYnmz2Ir8cwk`. Keep them alive until native termination; do not repeat submission, stop either job because the other fails, or substitute a GPU type while queued.

## Passing conditions and current limits

Observed **PASS, admission-only:** personal creator, declared image/tag/resource/one-replica/local source, non-preemptible policy and three source identities. Dry-run/CPU7/source reviews are archived at [source acceptance](evidence/packed-varlen-preparation-20261111/source-review.md), not native results.

Still **UNVERIFIED:** actual H800 device/count, worker Python/Torch/Triton versions, compiled packed specialization, container exit/restarts, exact own-prefix and cross-length tensor/state metrics, and native memory measurements. When the launchers finish, inspect the actual verdict/logs/source receipts and owner-bound platform record before interpreting any result. Preserve failed checks rather than auto-retry. Synthetic success cannot establish actual1693/1695 inputs/state equality, canonical-P join, a causal fix or warm correctness. Existing281e/e2/7ae, warm1/4 FAIL, formal04/05 HOLD,06 each200 and B's no-A200 edge remain unchanged.
