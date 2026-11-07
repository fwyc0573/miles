# Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Archive completed tokenizer/dataset/Lark/Steptron research and verification limits. |

# Completion summary

## Overview

Completed the user's four-part investigation of current Qwen pair tokenizers, handbook dataset compatibility, accessible Lark OPD/MOPD records and existing Steptron branches. The investigation was read-only for source systems and model/data assets. Only this local research task directory was written.

## Results

1. The current four Qwen3.5 models in pairs A/B/C share identical original tokenizer/config/template assets. Their configured token vocabulary contains248077 entries; the inspected4B HF model output vocabulary dimension248320 is a separate value. Miles uses its fixed preserve-thinking template.
2. The handbook does not establish an additional native-Qwen3.5-tokenized historical corpus. Its source messages can be re-encoded; Miles already uses a frozen GLM-derived924-training/24-monitoring-prefix population.
3. Steptron `qwen35-opd-h200@b48739f615e9a933003859f7a948398320774af5` uses the same model pairs and a different55-JSON/9-group/482359-row mixture. The current local Steptron tokenizer matches Miles on the full token map, ordered BPE merges, added-token configuration and10 actual encodings despite JSON/template file differences.
4. Lark includes current Qwen3.5 plans, older Qwen ticket references, custom Qwen3 tokenizer rules and literature records naming DAPO-Math-17K. Steptron contains actual R1-Distill-Qwen/JustRL200-step records, Qwen3-8B configurations and Qwen3 medium data/replay records. The internal1.5B200-step experiment used a600-item specified math-trajectory slice, not an inferred DAPO corpus.

## Deliverables

All paths are under `task_memory/task_2026-11-08_qwen_tokenizer_opd_inventory/`:

- `findings.md`: Chinese synthesis and usable dataset/branch/source pointers.
- `tokenizer_datasets.md`: exact tokenizer identity, effective templates and handbook source classification.
- `lark_records.md`: accessible document/source inventory, dataset/config/result details and permission boundaries.
- `steptron_records.md`: fixed refs, precise configurations, dataset paths and recorded execution distinctions.
- `test_report_2026-11-08_research.md`: exact environment, reproducible checks and observed validation.
- `review.md`: targeted fact-check corrections and final no-findings phase review.
- `evidence/tokenizer-checks.json`, `evidence/steptron-tokenizer-crosscheck.json`, `evidence/steptron-source-checks.json`: compact parent verification receipts.
- `evidence/lark-read-receipts.json`, `evidence/lark-primary-excerpts.md`, `evidence/lark-sheet-permission.json`, `evidence/lark-checkpoint.md`: filtered source receipts and limitations.

## Observed validation

- Four-model asset checks and the documented core Python command: PASS.
- Current Steptron/Miles tokenizer check:248077 mappings and247587 ordered merge pairs agree;10/10 actual encodings agree; PASS.
- Fixed Steptron manifest/inventory:55 distinct paths,9groups,482359 records; c1/c2 seven/eight recorded update/sample-audit positions at256 samples each; PASS at archived-receipt scope.
- Lark:31 successful searches/28queries,15 distinct documents and the dataset-source image read; filtered receipts checked.
- Steptron:52local heads and8335remote-tracking refs enumerated; relevant fixed sources reviewed without fetching or switching branches.
- Factual-review corrections applied; final phase review returned no findings.
- Final document checks:12Markdown history tables,5JSON payloads and30local links PASS; documented tokenizer command executed successfully.

## Open coverage limits

Seven embedded Lark tables require missing spreadsheet-read scope; one referenced OPD Log was unavailable. Broad searches and remote-tracking refs are bounded/local views, not proof that no other company records exist. Cloud files and live job status were not rechecked. Historical Qwen tokenizer receipts do not establish compatibility with Qwen3.5. Miles C and Steptron c3 are not certified complete by this research. No new training, data conversion, dataset switch or optimizer update was performed.

No requested research subtask remains pending. Filling the above coverage limits would be additional scoped work.
