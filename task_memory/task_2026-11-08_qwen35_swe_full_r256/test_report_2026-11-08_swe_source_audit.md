## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Add successful zero-GPU source-model inspection and independently observed terminal status. |
| 2026-11-08 | Record actual source/benchmark identity audit, parent checks, and lossless retained evidence. |

# Ticket 01: source and benchmark identity audit

## Scope and outcome

**PASS for this audit subtask; Ticket 01 remains in progress.** All 11 personal source copies match the recorded SHA256 values. The audit scanned 4,992 conversations and 446,569 assistant turns, totaling 3,356,482,428 source bytes. It compares source identities and text; it does not implement the training loader or prove model execution.

The selected benchmark is the first 100 IDs in the existing domain manifest, mapped into the original 500-row library. It contains 22 astropy and 78 django tasks. Selecting the library's first 100 rows would select a different set (18 shared IDs).

| Check | Passing condition | Observed | Result |
| --- | --- | --- | --- |
| Source copy integrity | All 11 SHA256 and recorded conversation/turn counts match | All matched | PASS |
| Benchmark identity | Library matches copy receipt; manifest and library contain the same 500 IDs | Both checks passed | PASS |
| Selected task payload | 100 manifest-ordered IDs map to the exact library payload | Parent recomputation equals saved payload | PASS |
| Three matching methods | Positive controls each detect one matching task | 3/3 detected | PASS |
| All-source text comparison | Complete coverage, with actual matches reported | 4,992 comparable conversations; 0 matches | PASS |
| Task-ID/base-commit comparison | Report missing identity explicitly | 0 structured task IDs/base commits; comparisons incomplete | LIMITED |
| Raw prefix accounting | Preserve original assistant-stream boundaries | 51,200 turns cover 546 conversations; 1,024 cover 11 | PASS, before token filtering |
| Lossless archive | Decompression reproduces exact JSON bytes | 3,604,097 bytes reproduced | PASS |

The full-source zero exact-text intersection implies zero for any subset of these conversations, including a length-filtered subset. It does not establish the number of eligible Qwen turns or rule out paraphrases, aliases, or semantic overlap. No observed match requires a change to the frozen data policy.

## Environment and execution

- Host CPU environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python **3.12.13**.
- Analysis script: `tests/manual/agent_opd/check_swe_benchmark_overlap.py`.
- Actual completed scan: **72.57527667004615 seconds** before writing the report. The initial 60-second command timed out; the completed command used a 180-second wall-clock limit after measuring parse cost. The user systemd bus was unavailable, so the run used the permitted plain-timeout fallback.
- Raw log: `/data/ycfeng/tmp/qwen35-swe-full-r256/benchmark-training-overlap.log`.

```bash
timeout 180s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python \
  tests/manual/agent_opd/check_swe_benchmark_overlap.py \
  --benchmark /data/ycfeng/tmp/qwen35-swe-full-r256/swe_bench2512_all_sorted.json \
  --benchmark-copy-receipt /data/ycfeng/tmp/qwen35-swe-full-r256/benchmark-COPY_COMPLETE.json \
  --manifest /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/task_memory/task_2026-10-01_step3p6_single_teacher_bounded_replay_h200/artifacts/readiness/domain_manifests_1009/swe/domain_manifest.json \
  --sources /data/ycfeng/tmp/qwen35-swe-full-r256/swe-sources-20261023 \
  --output task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/benchmark-training-overlap.json \
  > /data/ycfeng/tmp/qwen35-swe-full-r256/benchmark-training-overlap.log
```

The parent checked the exact script SHA256, reconstructed the 100 benchmark payloads from the saved input paths, recomputed all-source comparisons from the per-conversation identities, and ran one positive control for each matching method. All passed; the source files were not redundantly parsed again.

## Retained evidence

- Versioned, lossless complete report: `evidence/benchmark-training-overlap.json.gz` (**379,218 bytes**). It contains input identities, all 100 benchmark payloads, all 4,992 conversation identity rows, match lists, scope boundaries, commands and limitations.
- Decompressed JSON SHA256: `62a8d6198f555a198c3dd763c75c9fb65d430041ca99ab0e61506373e2e21d2f`.
- Gzip SHA256: `baa030bf3674722527cf6a55756b5a62696a489495d2f8c17c2a5944ac2e1945` (mtime zero).
- The uncompressed `evidence/benchmark-training-overlap.json` is retained locally for active consumers; the compressed archive preserves identical bytes within the repository's large-file limit.
- Script SHA256 at execution: `885c8ded9d09d786fe05e4377fe61de13c30dabc0a835fd5dbc59d0b62c8686d`.
- Benchmark library SHA256: `f57b0957c562726bbc0a8f452d1b573d354d78fd0916459d249150fa257bf124`.
- Ordered manifest SHA256: `b3a0d001a746119f0434d05b5e22e74ce5d5fcf9486958a183ee5e24329ea129`.
- Selected ordered-ID SHA256: `36394396b15746b75fbdfc1fbe8d74230161259a3dabf9d1ad824a1291140068`.

## Model-source revalidation — PASS

The parent submitted `exp-1108-144027-369537` through local StepMind Python `RJobBackend` with the existing H200 configuration's image and mounts. Requested resources were **8 CPUs, 64,000 MiB, 0 GPUs, one replica**, non-preemptible, `step_main`, positive tag H200. The API receipt confirms creator `i-fengyicheng`, local source mount `100.96.128.195:/data/ycfeng:/data/ycfeng`, and image `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`.

Actual worker: `gpu-h200-1161.lgcm.sh.istep.fun`, Python **3.12.16**. Executed CLI:

```bash
/opt/sglang/bin/python3 -u -B -m tests.manual.agent_opd.check_qwen_model_sources \
  --assets-receipt /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-06_qwen35_three_pairs/evidence/assets-exp-1106-233008-986003.json \
  --model Qwen3.5-4B --model Qwen3.5-27B --model Qwen3.5-35B-A3B \
  --report /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/model-sources-exp-1108-144027-369537.json
```

The script reuses the existing `_model_metadata` inspection. Passing requires each selected source's config/tokenizer/template/index hashes, tensor count and shard sizes to equal the historical qualified receipt, all indexed shards to exist, and the selected models to share identical tokenizer metadata.

| Model | Indexed tensors | Shards present | Identity comparison |
| --- | --- | --- | --- |
| Original Qwen3.5-4B snapshot | 738 | 2/2 | PASS |
| Qwen3.5-27B | 1,199 | 11/11 | PASS |
| Qwen3.5-35B-A3B | 1,811 | 14/14 | PASS |

Business receipt is `status=verified`, with no errors. The API independently reported **Succeeded**, default task succeeded=1, finish time `2026-11-08T06:47:37Z`. The local launcher remained alive until completion.

Evidence:
- `evidence/model-sources-exp-1108-144027-369537.json`: actual model paths, hashes and shard sizes.
- `evidence/model-source-platform-exp-1108-144027-369537.json`: initial creator/image/resource/source-mount verification.
- `evidence/model-source-terminal-exp-1108-144027-369537.json`: final platform/task status.
- Raw launcher log: `/data/ycfeng/tmp/qwen35-swe-model-sources-launch-20261108.log`.

This checks metadata and complete indexed shard presence/sizes; it does not hash full weight files or rerun previously accepted training/reloads.

## Remaining acceptance

Actual native-loader/Qwen-renderer parity, post-tokenization counts and consumable runtime configuration remain with Ticket 01. No GPU training, benchmark score, or source-model reload PASS is inferred from these audits.
