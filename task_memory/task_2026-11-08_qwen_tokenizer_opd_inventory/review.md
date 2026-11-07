# Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record targeted fact-check fixes and completed final research review. |

# Research review

## T1 factual check

- Reviewer: explore agent, `QWEN-TOKENIZER-T1-CHECK`, session `ses_e48facd00ffeXN0EgaGpbKYrbc`.
- Scope: `tokenizer_datasets.md`, `evidence/tokenizer-checks.json`, original four-model assets, local4B files, the four handbook documents, population excerpt and cited native code.
- Result: no conclusion-changing defect. Three corrections requested and applied: record actual manifest comparison fields; scope248320 to inspected4B HF config; remove unsupported attribution of separate Step/GLM/Qwen full-dataset runs to handbook examples.
- Additional limitation recorded: local population JSON is a field excerpt missing `qwen_tokenizer`, not the full cloud report.
- Verification: parent reread both manifests and4B HF config; all model paths correspond and config SHA matches the original4B receipt. Final phase reviewer accepted these corrections.

## Final phase review

- Reviewer: reviewer agent, `QWEN-TOKENIZER-FINAL-REVIEW`, session `ses_e48e753f2ffe4sWi0zH5uWLuXA`.
- Requirements: `requirements.md` and `plan.md`.
- Inspected artifacts: `findings.md`, `tokenizer_datasets.md`, `lark_records.md`, `steptron_records.md`, `evidence/tokenizer-checks.json`, `evidence/steptron-tokenizer-crosscheck.json`, `evidence/steptron-source-checks.json`, `evidence/lark-primary-excerpts.md`; sampled original asset/population/Lark records and1.5B experiment archive.
- Result: **No actionable factual or requirements-coverage findings.** Substantive deliverables satisfy the requested research scope.
- Confirmed boundaries: four-model equality versus cross-backend tokenizer equivalence/template differences; raw messages versus tokenized caches; plans/configs versus actual updates/diagnostics/final completion; historical Qwen3 versus current Qwen3.5.
- Limits: read-only review, no encoding rerun or platform query; unread Lark tables, newest remote refs, current cloud files and C/c3 final success remain unverified. Final status/archival edits are owned by the parent and checked separately.

No source code, training configuration, dataset, authentication or external record was changed by this investigation.
