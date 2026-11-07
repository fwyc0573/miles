## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Complete native SGLang replacement and CPU contract verification; close the final-weight identity finding at implementation scope. |
| 2026-11-07 | Record initial checker results, pinned dtype loss, final-weight identity finding and native SGLang replacement scope. |

# Final text-HF reload verification

## Scope and current verdict

D13/R5 require the final updated text decoder, compatible configuration/tokenizer and actual text inference. Current verdict: **INCOMPLETE**. No final100-step artifact or full-model reload has yet passed. This standalone validator has no training control path.

## Initial implementation and local verification

The initial implementation added `tests/manual/agent_opd/qwen_reload.py` and `tests/fast/test_qwen_reload.py`. The owning agent reported **38 passed in8.93s** on Python3.12.13/torch2.11.0+cu130, using:

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q -o addopts='' \
  -p no:cacheprovider --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-reload-final \
  tests/fast/test_qwen_reload.py tests/fast/test_qwen_text_export.py \
  tests/fast/test_qwen35_monitoring.py::test_native_zigzag_cp_reassembles_token_positions_not_rank_order \
  tests/fast/test_qwen35_monitoring.py::test_unknown_cp_allgather_is_explicitly_incomplete
```

These tests cover actual tiny Transformers loading, forward/generation and injected faults. They include a successful rejection of mixed-dtype corruption;38 passing tests do not mean the default loader preserves the real checkpoint's FP32 parameters.

## Pinned dtype reproduction and failed auxiliary jobs

The pinned image uses Python3.12.16, torch2.14.1+cu130 and Transformers5.19.0. A tiny official text model was converted to BF16, its `A_log` set to FP32 `0.123456789`, saved with `save_pretrained`, read through safetensors and reloaded using `AutoModelForCausalLM.from_pretrained(..., local_files_only=True, dtype='auto')`.

Expected: identical saved/loaded dtype and values. Actual **FAIL**: saved `torch.float32`, value0.12345679104328156; loaded `torch.bfloat16`, value0.12353515625. Both native keep-FP32 lists are empty. Exact [pinned receipt](evidence/hf-dtype-exp-1107-065617-263305.json) was produced by `exp-1107-065617-263305`.

The first0-GPU job `exp-1107-065241-081272` failed while serializing the loader's set-valued policy attribute to JSON. The corrected command sorted those fields; its dtype probe completed. Its subsequent CPU pytest invocation of `test_qwen_reload.py test_qwen_text_export.py` produced **4 failed,15 passed,15 errors in8.74s**: installed CUDA-only convolution was selected for CPU fixture inputs. Logs are `evidence/hf-reload-runtime-<job>.log`. No actual full-model GPU reload occurred, and no more CPU forward retries are scheduled against that mismatched kernel setup.

Both jobs have8 successful RCA queries under `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-rca-hf-{runtime,dtype}-<job>/`, collected with the canonical failure collector, personal identity and exact incident windows22:52–22:54Z /22:56–22:59Z. They are auxiliary failures independent of A/B's later native backward OOM.

Source/probe analysis confirms that Transformers5.19's supported strict keep-FP32 class declaration can preserve the tiny package; a dtype dict is collapsed to the global dtype and post-load casting cannot restore rounded values. No library class policy, dependency patch or dtype relaxation has been adopted.

## Review finding and chosen native path

Reviewer `QWEN-P3-HF-RELOAD-REVIEW` found a P1 false-PASS path: final directory/rollout markers, package-internal tensor equality and<=0.03 sampled logprob agreement cannot prove that the HF files contain the final published weights. Native export completion carries no content-bound publication metadata. The replacement and regressions now close this finding at implementation scope; actual final artifact acceptance remains INCOMPLETE.

Existing `InferenceEngineWeightChecksumEvent` records provide full-byte checksums of native eligible engine tensors, bound to publication/load epoch/engine incarnation. The actual [B initial receipt](evidence/initial-engine-checksums-B-exp-1107-062459-796906.json) contains1416 entries over TP2, including vision weights and derived `gemma_weight` decoder buffers. Raw HF tensors have a different fused/sharded layout, so directly hashing safetensors cannot be compared to these engine hashes.

Use the **existing pinned SGLang text loader** at the original engine TP/configuration, then compare its native eligible decoder checksum dictionary with the final publication's dictionary. This reuses the actual HF-to-engine loader and FP32 `A_log` parameter policy. D13 excludes vision/MTP; all eligible decoder entries and derived decoder buffers remain checked. The fresh engine's own version is reported separately from the training publication version, whose connection is established by content equality. Retain package/schema/tokenizer validation, original fixed inputs/masks, numerical reporting and actual text generation.

No new hashing algorithm, partial-norm identity substitute or exporter metadata path is introduced. The superseded Transformers loading path was replaced in the same two files. Actual native text reload, checksum equality, full-length inference, cleanup and all three final artifacts remain to be verified by the parent on H800.

## Replacement verification and phase review

Implementation owner `QWEN-P3-HF-RELOAD-IMPLEMENT` supplied **63 passed /13.77s**, comprising40 reload tests and23 export/CP checks, using the earlier local command with basetemp `qwen-reload-native-contracts`. Package checks are real; native Engine/API boundary cases use fixtures. Exact initial namespace audit:1416 entries ->822 decoder entries and594 excluded vision entries;162 derived gemma buffers remain within decoder coverage. TP2 tied-head canonical naming is embedding.

Reviewer `QWEN-P3-HF-RELOAD-REVIEW` inspected the changed-file list (`qwen_reload.py`, `test_qwen_reload.py`), task records and native producer/loader/checksum sources. **Original P1 CLOSED; no new actionable finding.** Final checksums bind publication ID/version plus load epoch/cell/incarnation; pre/post-inference decoder dictionaries must match exactly. Stale packages below0.03, missing decoder keys, derived-buffer mismatch, TP mismatch and incomplete final receipts cannot pass. The review did not run tests or GPU work.

The report's image field is a configuration declaration; actual container provenance requires the parent's RJob API receipt. Registry support, actual FP32 decoder bytes, long input inference and subprocess cleanup still require native execution. No dependency or model-class policy patch is adopted.

Pinned registry prerequisite is now **PASS**: `exp-1107-075006-580618` resolves requested `Qwen3_5ForCausalLM` directly to `sglang.srt.models.qwen3_5_text.Qwen3_5ForCausalLM` on SGLang0.5.24.dev80+g056f871, without the Transformers fallback. Exact [runtime receipt](evidence/text-entry-exp-1107-075006-580618.json). All40 replacement reload tests pass in this image. The combined run's four failures are the previously known unchanged Transformers CPU-forward cases, as recorded in the [training report](test_report_2026-11-07_training.md); they do not represent native text loading. Full-model GPU reload and final artifact content equality remain outstanding.
