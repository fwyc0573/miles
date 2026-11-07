## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record tokenizer asset/manifest checks and primary-source research verification. |
| 2026-11-08 | Add Steptron fixed-receipt and local-runtime tokenizer crosschecks; record T1 factual-review corrections. |

# Research verification

## Tokenizer / current-dataset checks

Environment: local Python3.10.6, repository commit `35edf7f5dd9809292029c7e494645745843a11d8`; standard-library JSON/hashlib/pathlib only. No GPU/model loading or new cloud scan.

The initial inline reader used `launch.json['argv']` and failed with `KeyError: 'argv'`. Inspecting the actual receipt showed the correct field `training_argv`; the corrected read passed. No source receipt or runtime configuration was changed.

Reproducible core check from the Miles repository:

```bash
python3 -B - <<'PY'
import hashlib, json
from pathlib import Path
t = Path('task_memory/task_2026-11-06_qwen35_three_pairs')
a = json.loads((t / 'evidence/assets-exp-1106-233008-986003.json').read_text())
p = json.loads((t / 'evidence/population-exp-1106-233008-986003.json').read_text())
local = Path('/data/ycfeng/tmp/swe-model-pairs-20261103/Qwen/Qwen3.5-4B')
for name in ('tokenizer.json', 'tokenizer_config.json', 'chat_template.jinja'):
    digests = {rows[0]['metadata_sha256'][name] for rows in a['models'].values()}
    assert len(digests) == 1
    assert hashlib.sha256((local / name).read_bytes()).hexdigest() in digests
assert hashlib.sha256(Path(p['chat_template']['path']).read_bytes()).hexdigest() == p['chat_template']['sha256']
for pair, job in [('A', 'exp-1107-173758-712234'), ('B', 'exp-1107-173758-806531'), ('C', 'exp-1107-064200-013666')]:
    launch = json.loads((t / 'evidence/first-round/student' / pair / job / 'launch.json').read_text())
    argv = launch['training_argv']
    assert argv[argv.index('--prompt-data') + 1] == p['datasets']['train']['path']
    assert '--apply-chat-template' not in argv
print('PASS')
PY
```

Observed PASS in the expanded inspection and in a subsequent execution of the exact documented command; local Python reports3.10.6. The expanded check additionally matched current H800/H200 model paths, counted vocabulary entries/special IDs and wrote [tokenizer-checks.json](evidence/tokenizer-checks.json). Four actual model sources match on all three assets; configured vocabulary248077; base vocabulary248044; effective fixed template and both thinking options match the frozen population. C's inspected launch is explicitly historical, not qualification of the new pending run.

## Research evidence boundaries

- Handbook: all four existing resource-analysis documents inspected; historical measurements are identified as such, and original-generation tokenizer is not inferred from a dataset family name.
- Lark: agent receipt verification PASS for31 successful searches/28queries and15 distinct documents; parent read `lark_records.md` and all decisive primary excerpts. Current Qwen3.5 plans, old Qwen Ticket07 vs actual Step execution, custom Qwen3 special tokens, and DAPO-Math-17K literature-record distinctions match the excerpts. Seven sheets failed because `sheets:spreadsheet:read` is absent; one referenced OPD Log returned3380002. Existing user authentication is valid; no authentication change was made. Scope limits remain explicit in `lark_records.md`.
- Steptron:52 local heads and8335 remote-tracking refs enumerated; focused fixed-commit configuration/record reads and source provenance are documented in `steptron_records.md`. No fetch/checkout/live-job/cloud access. Parent independently matched all55 inventory paths to the fixed manifest,9groups,482359 recorded rows, and c1/c2 seven/eight scalar and sample-audit iterations with256 distinct samples per iteration. [Receipt](evidence/steptron-source-checks.json). Parent also read the archived1.5B math summary at `1e588c90...`:600-item source slice,H200/H800 each200steps and +8.73/+9.40pp recorded gains match the synthesis.
- Verification is documentary/source analysis. Existing A/B runtime acceptance is a cited prior result, not a new execution in this research.

## Steptron current-tokenizer crosscheck

Actual environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, Transformers5.19.0, tokenizers0.23.2. Local-only `AutoTokenizer.from_pretrained(..., local_files_only=True)`; no model loaded or GPU used.

Expected: full token→ID maps match after config-added tokens; BPE merge ordering and pipeline components agree; actual test strings encode identically. Distinct chat-template assets must remain explicitly identified.

Observed PASS:248077 mappings,247587 ordered merges, added-token configs and six other pipeline components agree;10/10 encodings match. Raw JSON model comparison first showed a difference in `merges`: legacy strings versus serialized two-item arrays. Normalizing this observed representation confirms equal ordered pairs, while raw added-token lists contain26 versus33 because the runtime save includes the seven config-added tokens. These representation differences explain why tokenizer JSON SHA alone differs. [Full receipt](evidence/steptron-tokenizer-crosscheck.json).

Reproduce the actual assertions using the recorded texts:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false CUDA_VISIBLE_DEVICES='' PYTHONNOUSERSITE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import json
from pathlib import Path
from transformers import AutoTokenizer
t = Path('task_memory/task_2026-11-08_qwen_tokenizer_opd_inventory')
r = json.loads((t / 'evidence/steptron-tokenizer-crosscheck.json').read_text())
source, runtime = Path(r['source']), Path(r['steptron_runtime'])
a = AutoTokenizer.from_pretrained(source, local_files_only=True)
b = AutoTokenizer.from_pretrained(runtime, local_files_only=True)
assert len(a) == len(b) == 248077 and a.get_vocab() == b.get_vocab()
ja = json.loads((source / 'tokenizer.json').read_bytes())
jb = json.loads((runtime / 'tokenizer.json').read_bytes())
assert {k:v for k,v in ja['model'].items() if k != 'merges'} == {k:v for k,v in jb['model'].items() if k != 'merges'}
assert len(ja['model']['merges']) == 247587
assert [x.split(' ') for x in ja['model']['merges']] == jb['model']['merges']
for key in ('normalizer', 'pre_tokenizer', 'post_processor', 'decoder', 'truncation', 'padding'):
    assert ja.get(key) == jb.get(key)
ca = json.loads((source / 'tokenizer_config.json').read_text())
cb = json.loads((runtime / 'tokenizer_config.json').read_text())
assert ca['added_tokens_decoder'] == cb['added_tokens_decoder']
assert len(r['sample_encodings']) == 10
for row in r['sample_encodings']:
    assert a.encode(row['text'], add_special_tokens=False) == b.encode(row['text'], add_special_tokens=False)
print('PASS')
PY
```

This is a current local-asset check; no claim of replaying every historical worker, model forward or full prompt-template rendering. The source files are outside this research's write scope and were not edited.

## Review corrections and document checks

`QWEN-TOKENIZER-T1-CHECK` found no conclusion-changing factual defect and identified three evidence/wording fixes, all applied:

1. Persist manifest paths and explicit model-source comparison results.
2. Attribute248320 specifically to the local4B HF `text_config.vocab_size`, whose full config SHA matches the actual-source4B receipt; do not assert a value reread from all four configs or a nonexistent training-manifest field.
3. Attribute actual Qwen re-rendering to this task rather than treating handbook format examples as separate historical full-dataset runs.

The local population JSON is now explicitly described as an excerpt missing `qwen_tokenizer`, sufficient for its retained counts/template/output hashes but not a byte-identical copy of the cloud population report.

Final document check PASS:12Markdown documents include Modification History; all5JSON payloads parse; all30local Markdown links resolve. The exact documented cross-backend command was also executed after documentation assembly and returned PASS. Final phase review in `review.md` found no actionable issue. No production tests were needed because only local research documents/evidence were written.
