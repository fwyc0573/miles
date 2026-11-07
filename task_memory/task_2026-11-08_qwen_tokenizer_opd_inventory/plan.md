# Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Split independent primary-source investigations and define evidence-based acceptance. |

# Plan

Dependency graph: scope -> {T1 tokenizer/datasets, T2 Lark records, T3 Steptron branches} -> T4 synthesis/verification -> archive.

- T1: Parent checks the actual four-model tokenizer receipts, effective templates and handbook dataset provenance. Done when equality claims identify assets and evidence, and each handbook dataset is classified without guessing a tokenizer from its name.
- T2: Background research agent searches/reads accessible Lark records. Owns `lark_records.md` plus narrowly selected local evidence. Done when relevant Qwen OPD/MOPD records have links and explicit dataset/config/result fields, with query coverage and permission limits.
- T3: Background research agent inspects Steptron refs, Qwen experiment inheritance and recorded results. Owns `steptron_records.md` plus selected local evidence. Done when relevant records have branch/commit/path references, dataset and tokenizer fields, and configuration-versus-execution distinctions.
- T4: Parent reconciles differences, links the three source inventories in `findings.md`, verifies decisive evidence, runs a progress checkpoint and archives the investigation.

Verification uses source reads, scoped Git comparisons and JSON receipts; no GPU runs or new persistent test machinery. Preserve unrelated working-tree files and existing branch state. Read existing rules before writing local documents; every maintained task document includes Modification History.

Completion: T1/T2/T3/T4 are complete. See `findings.md` for the synthesis, `test_report_2026-11-08_research.md` for observed checks, and `review.md` for final no-findings phase review and coverage limits.
