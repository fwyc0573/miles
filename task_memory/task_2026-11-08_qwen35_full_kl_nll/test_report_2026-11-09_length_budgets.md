## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Accept the completed original-source112K audit/parity and personal direct-API terminal receipt; record reconciled source counts, current length/span results and unverified runtime limits. |
| 2026-11-09 | Verify D34 input/request/audit changes and prepare the in-place112K source audit. |

# Qwen3.5 length budgets

## Contract and environment

D34: training `seq_length` and rollout `max_seq_len`/context131072, inclusive rendered-prompt budget114688, completion cap16384. Over-budget prompts are skipped before consuming slots; messages are not truncated. The native request cap is `min(response_limit, context_limit - prompt_tokens)`.

Worktree:`/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`; Python:`/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`,3.12.13; torch2.11.0, transformers5.19.0, pytest9.1.1. No conda change. The isolated upstream-based launcher change is committed as`8c9537bf` on`agent-opd-h800-capacity`, following admission change`1ae93261`; parent integration remains gated.

## Commands and observed results

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/fast/test_swe_input_limits.py tests/fast/test_swe_input_pins.py \
  tests/fast/rollout/test_sample_max_response_len.py tests/fast/rollout/test_sglang_opd_request_contract.py
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B tests/manual/agent_opd/submit_swe1003_audit.py \
  --config task_memory/task_2026-11-08_qwen35_full_kl_nll/source_audit_config.json --dry-run
python3 tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll
git diff --check
```

| Check | Expected | Observed | Verdict |
| --- | --- | --- | --- |
| Affected fast suite | Adapter, native request and sample cap contracts hold |33 passed in3.09s; existing SWIG/torch deprecations and CPU-only quantization warnings | PASS |
| Inclusive prompt boundary |114688 accepted,114689 skipped without allocating a slot | Accepted source draws0/2, slots0/1; rejected draw still reported as finished | PASS |
| Completion and total limits | Short/boundary prompts capped at16384; boundary total131072 | Actual native payload has114688+16384=131072; short prompt also16384 | PASS |
| Native input checks under new budgets | Existing source order/render/mask/finish behavior preserved | GLM512 native parity+2048 interleaved; SWE synthetic30+12 | PASS |
| Audit threshold independent of context | A prompt within context but above prompt cap rejects | Synthetic1568-token prefix rejects against1500 prompt cap while total context is2000; one overlength turn, native mask/visual counts correct | PASS |
| Audit bisection | Equal112K accepted,112K+1 rejected | Three boundary sequences return expected first-overlength ordinals | PASS |
| Audit/parity workflow integration | Both commands receive three explicit budgets | Synthetic16 parity+16 interleaved PASS; real-source dry-run carries131072/114688/16384 in both argv | PASS |
| Documentation and diff | Links/DAG/arithmetic valid; no whitespace errors | Before this report:22 documents,75 links,22 anchors,zero errors; diff clean | PASS |
| New real-source audit | Actual112K statistics and terminal success | Job/replica Succeeded, finish11:47:11Z; business JSONs and parity inspected below | PASS |

Durable receipts with exact CLI argv:

- `evidence/length-budget-glm-parity-20261109.json`
- `evidence/length-budget-swe-synthetic-parity-20261109.json`
- `evidence/length-budget-audit-synthetic-20261109.json` (includes synthetic audit and checker commands).

The audit agent's first cumulative verification command exceeded60 seconds; the same independent checks passed in one imported process under a120-second envelope. No runtime workaround was added. The synthetic receipt's outstanding old-D5-table note was subsequently fixed in`spec.md`.

## Runtime verification limits

The input and native request path is CPU-verified. The launcher's explicit `prompt_tokens` and `response_tokens` contract is separately verified by53 launcher tests and7 related tests in the isolated preparation worktree; see its`test_report_2026-11-09_native_launch_lengths.md`. These results do not prove a live H800 training run or replace the D1/D22 native capacity gate.

Prior audit output`evidence/source-audit-20261109/` remains the accepted pre-D34 source evidence at commit`2d695ba0`; its128K prompt-rejection and span statistics do not apply to112K. Updated`source_audit_config.json` writes only to`evidence/source-audit-112k-20261109/`, with separate temporary storage. Source files continue to be read in place from posttrain.

## Completed112K original-source audit

After committing the verified input/audit code as`438d25fc`, the primary submitted the existing CPU workflow using personal StepMind authentication and the runbook proxy setup:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B \
  /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/tests/manual/agent_opd/submit_swe1003_audit.py \
  --config /data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/source_audit_config.json
```

Environment:`STEPMIND_BACKEND=rjob`, `PYTHONPATH=/data/ycfeng/steptron`, `PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, local mount cwd`/data/ycfeng`. The submission launcher was`sh_1bf43bd8e0011S3o8uZqd0btZi`; raw log:`/data/ycfeng/tmp/agent-opd-image/source-audit-112k-launch-20261109.log`. Its launch-time lifetime is not a current running-job claim.

Filtered receipt`evidence/source-audit-112k-admission-20261109.json` confirms creator`i-fengyicheng`,8 CPU,32000Mi,0 GPU, pinned image, local NFS source`100.96.128.195:/data/ycfeng:/data/ycfeng`, codesign/posttrain volume mounts and worker startup withPython3.12.13/torch2.11.0+cu130/transformers5.19.0. Its `startup_lines` retain the exact executed audit command, including all four pinned-module hashes, Qwen kwargs,131072/114688/16384,32×8/1×8 and200×256. The exact executed checker argv is retained in `evidence/source-audit-112k-20261109/parity/input-parity.json`; neither command was rerun for this documentation acceptance.

At2026-11-09T11:52:22.402210Z, the primary's personal `get_rjob_client()` / direct API inspection confirmed job`exp-1109-154414-275606`, UID`6e08e161-435d-4195-bcd4-88d40d291eac`, and exact audit replica`exp-1109-154414-275606-cfcd2084` both **Succeeded**, with job finish2026-11-09T11:47:11Z. Receipt:`evidence/source-audit-112k-terminal-20261109.json`. The first read-only terminal attempt used the nonexistent `get_client` import and raised a local `ImportError` before any request; reading `steptron/utils/stepmind.py:744` identified `get_rjob_client` and fixed the method-name error. This was not an audit failure, platform failure or relaunch. No separate container exit code or terminal-log completion marker is claimed from this filtered terminal receipt.

### Current112K acceptance results

| Check | Expected / passing condition | Observed | Verdict |
| --- | --- | --- | --- |
| Original source identities | Eight files read in place; prior SHA/bytes and new manifest/audit/parity agree | All per-file paths, SHA256, bytes, mtimes, counts and visual indices match historical128K evidence;16,559,540,463 bytes; manifest COMPLETE/read_in_place=true | PASS |
| Population reconciliation | Separate original, masked, visual-excluded and pre-length eligible populations |9,254 conversations;892,620 assistants;878,783 eligible;13,837 masked;102 visual conversations/10,008 eligible turns excluded;9,152 trainable conversations/868,775 eligible turns before length filtering | PASS |
| D26 recorded criterion | Pre-length eligible-turn median reported against81 | min5/median90/P90153/max355/mean94.9273; retain32×8. Post-length per-conversation median is absent/unverified | PASS, no new blocker |
|112K rejection | Record new threshold, not inherited128K figures |6,257 conversations with overlength tails;323,121/868,775 eligible turns rejected,37.1927%;545,654 length-accepted turns; longest-prompt median142,076 tokens | PASS, bisection limit below |
| Native M=1 parity |512 raw draws match native uid, remaining counts and normalized messages/tools | All512 match;512 with tools;12.3784s | PASS |
| Native M=32/block8 order |2,048 raw draws, ascending/file order, no duplicates, at most32 open, independent instances agree | Two identical sequences;maximum32 open;longest consecutive run8;remaining counts match | PASS |
| Inclusive boundary / slots |114688 accepted;114689 skipped;rejection consumes no slot | Boundary fixture PASS;two rejected draws,zero consumed slots;114688+16384=131072 | PASS, synthetic boundary fixture |
| Actual native request | Real parser/config merge reaches existing request builder and16K cap | Qwen-rendered4,366-token prompt → `max_new_tokens=16384`;all three runtime limits exact | PASS, CPU request construction only |
| CPU cost | Record measured values, no throughput acceptance |0.019126s construction/instance;7.30894ms mean draw;source scan13,451.546s/51,833 renders | RECORDED |
| Terminal and business output | Exact personal job/replica terminal success plus inspected artifacts | Job/replica Succeeded;all five business JSONs parse;manifest/parity identities and totals reconcile | PASS |

Durable business artifacts under `evidence/source-audit-112k-20261109/`: `swe1003-source-audit.json`, `swe1003-source-manifest.json`, `parity/input-parity.json`, `parity/input-config.json`, `parity/input-source-manifest.json`. The parity manifest independently verifies eight file signatures/16,559,540,463 bytes; `counts_independently_recomputed_in_this_check=false` means its counts reuse the source audit, not a duplicate count scan.

### Current112K scheduling measurements and limits

Both CPU simulations fill200×256=51,200 length-accepted turns, with zero repeated turns and final cursor epoch0. They model native source/mixer order and length rejection, not rollout/teacher failures, TIS, optimizer skips or successful native updates.

| Configuration | Raw draws / length rejections | Conversations | Update-span median / P90 / max | Spanning≥11 updates | Conversations/update median |
| --- | --- | --- | --- | --- | --- |
|32×8 |84,229 /33,029 |869 |5 /7 /9 |0/869 |23 |
|1×8 |85,171 /33,971 |863 |1 /2 /2 |0/863 |5 |

These are conversation counts, not verified SWE task counts; `tasks_per_update=null`. Native SWE instance/repository/commit identity stays UNVERIFIED/null. There are955 exact first-user-text proxy groups,zero missing proxies; consecutive32-conversation windows contain29–32 groups,median32. Neither proxy grouping nor simulated spans establish native runtime trend coverage, and no most-conversation-trend claim is made.

All9,254 first messages omit `preserve_thinking` and carry `reasoning_effort=null`; both audit and input configuration explicitly set `preserve_thinking=true` and `enable_thinking=true`. This disclosure precedes formal execution and does not change rendering parameters.

Length rejection totals rely on the existing bisection assumption that preserving Qwen prompt-prefix length is nondecreasing in turn ordinal. The saved per-conversation eligible counts are **before** length rejection; the length-accepted per-conversation median is not retained and remains unverified. D26's recorded feedback criterion is the pre-length eligible median90≥81, not an invented post-length median criterion. Actual remaining-gap/trend values additionally require RKL observations, positive fixed baselines and successful-update references; none exist in this CPU audit. Real-source parity verifies normalized messages/tools/order, not Step/Qwen token-ID or prompt-byte equality; boundary, mask/visual and finished-report fault cases remain synthetic.

Historical128K output and its239,015 rejections/27.5117%,32×8 span7 and17/745 spanning≥11 remain unchanged in [the historical source report](test_report_2026-11-09_source_audit.md). D34 acceptance closes Ticket01's changed input slice only; it does not lift D1/D22, upstream frozen D11 capacity acceptance, parent02/03 integration or formal-cell gates.

## Documentation/evidence record verification

Local acceptance environment: current parent worktree, `python3`3.10.6, no conda change, no auth/network or platform operations. The JSON-only readback compares the five business files plus terminal receipt against historical audit signatures, sums per-file counts and verifies budgets, native parity fields, slot boundaries, actual request fields and both simulation arithmetic identities. It opens retained JSONs only, not original source files. All these checks passed; credential-pattern matches were zero across the six selected JSONs. Pattern scanning is not a proof that every possible secret format is absent.

The first one-off record assertion incorrectly treated `local_verified_files` as an integer8; it is a list of8 signatures. Inspecting that field's type and checking its length corrected the local record check. No business artifact, source, audit job or test machinery was changed.

Exact final local check commands (the retained checker and its original temporary counterpart were inspected before choosing arguments):

```bash
python3 -B tests/manual/agent_opd/check_profile_docs.py task_memory/task_2026-11-08_qwen35_full_kl_nll
cmp tests/manual/agent_opd/check_profile_docs.py /data/ycfeng/tmp/agent-opd-image/check_docs.py
git diff --check
```

Expected: local links/anchors/ticket DAG/arithmetic valid, checker byte-identical, no diff whitespace errors. Observed before the final record notes:24 documents,6 tickets,82 links,28 anchors,dependency order01→02→03→04→05→06,51,200 per cell/102,400 total/ideal threshold81,zero errors; `cmp` and `git diff --check` PASS. Final unchanged checks are recorded in `progress.md`. The document checker verifies recorded structure/arithmetic, not runtime acceptance.

Exact selected JSON syntax/credential-value check:

```bash
python3 -B - <<'PY'
import json, re, sys
from pathlib import Path
base = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence')
paths = sorted((base / 'source-audit-112k-20261109').rglob('*.json')) + [base / 'source-audit-112k-terminal-20261109.json']
keys = re.compile(r'(?i)^(?:(?:brainpp|aws)_(?:access_key(?:_id)?|secret(?:_access)?_key)|api[_-]?key|access[_-]?token|secret[_-]?key|password|authorization|cookie|credentials?)$')
values = re.compile(r'\bAKIA[A-Z0-9]{16}\b|\bsk-[A-Za-z0-9]{20,}\b')
for path in paths:
    raw = path.read_text()
    pending = [json.loads(raw)]
    assert not values.search(raw)
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            assert not any(keys.fullmatch(k) and v not in (None, '', {}, []) for k, v in item.items())
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
print(f'Python {sys.version.split()[0]}; JSON syntax PASS: {len(paths)} files; credential-value matches=0')
PY
```

Expected/observed: all6 selected JSONs parse, no nonempty known credential fields or matching key-value formats, no credential values printed; Python3.10.6, `JSON syntax PASS: 6 files; credential-value matches=0` — PASS. Only explicit credential-key patterns and common key-value formats are covered.
