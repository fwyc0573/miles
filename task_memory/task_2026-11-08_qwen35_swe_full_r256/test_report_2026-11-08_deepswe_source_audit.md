## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Complete the replacement-source streaming audit, field/count/overlap evidence, positive controls, and independent artifact validation. |

# DeepSWE Source and Benchmark Overlap Audit

Task ID: `T01-DEEPSWE-AUDIT`.

Status: **FACTUAL_SOURCE_AUDIT_COMPLETE_WITH_IDENTITY_LIMITS**. All eight actual DeepSWE files were scanned. No source population or overlap result is inferred from the previous GLM-5.2 audit. Task-ID/repo+commit overlap remains unverified because those identities are absent; this is not a non-contamination certificate or native-loader acceptance.

## Scope and Inputs

The user replaced all training sources with the eight ordered SWE-1003/0913 DeepSWE resolved trajectories after garble filtering and datapipe processing. The authoritative selection is [evidence/deepswe-source-selection.json](evidence/deepswe-source-selection.json).

Local input root:

```text
/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420
```

`COPY_COMPLETE.json` records eight files totaling **16,559,540,463 bytes**, their original source identities, and the approved local/personal-cloud copies. This audit independently hashed all eight local files: every byte count and SHA256 matched the verified source receipt. It scanned one conversation at a time in selection order and did not access the source platform or cloud copies. Original paths, local paths and all eight hashes are retained in the evidence JSON.

The benchmark remains the previous frozen selection: `benchmark.task_ids[:100]` from the existing 500-task manifest, mapped by `instance_id` into the native SWE library. The manifest order is not the library row order. Expected membership is 22 `astropy/astropy` and 78 `django/django` tasks.

- Native library: `/data/ycfeng/tmp/qwen35-swe-full-r256/swe_bench2512_all_sorted.json`.
- Library SHA256: `f57b0957c562726bbc0a8f452d1b573d354d78fd0916459d249150fa257bf124`.
- Ordered manifest: `/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/task_memory/task_2026-10-01_step3p6_single_teacher_bounded_replay_h200/artifacts/readiness/domain_manifests_1009/swe/domain_manifest.json`.
- Manifest SHA256: `b3a0d001a746119f0434d05b5e22e74ce5d5fcf9486958a183ee5e24329ea129`.
- Previous benchmark provenance: [evidence/benchmark-training-overlap.json](evidence/benchmark-training-overlap.json). Its GLM training findings are not reused as DeepSWE acceptance.

## Method

The existing script [check_swe_benchmark_overlap.py](../../tests/manual/agent_opd/check_swe_benchmark_overlap.py) was minimally generalized to consume approved selection/copy-receipt file order and stream the actual top-level JSON arrays. The observed DeepSWE schema remains a list of message dictionaries with `role`, `content`, and `meta`; it additionally carries `loss_mask`, structured `tool_calls`, `tool_call_id`, and `reasoning_content`. No shared loader, training implementation, evaluator, or benchmark selection was changed.

The audit records full conversation and assistant-position counts, field presence separately from nonempty values, assistant loss-mask distributions, structured thinking/tool/reply fields, raw response fields, and the original source turn order. Raw prefix coverage includes every `role=assistant` message, **including `loss_mask=0`**, before Qwen prompt rendering and length filtering.

Overlap methods:

1. Exact explicit `instance_id`/`task_id` values, excluding request and tool-call IDs.
2. Exact explicit repository plus `base_commit` strings.
3. SHA256 of UTF-8 encoded `" ".join(problem_statement.split())`, preserving case and punctuation. Source statements come from nonempty `<pr_description>` bodies, explicit structured fields, or `Task Description:` text in initial task context.

Comparable-identity coverage is reported for each method. GitHub repository URL mentions in initial task context are reported separately and are not promoted to authoritative task repository identity. Source conversations are not excluded or rewritten.

## Exact Execution

Working directory: `/data/ycfeng/sota-engine/miles`.

The user systemd bus is unavailable. `prlimit` imposes an inherited **30 GiB address-space hard limit**; `timeout` bounds the sequential scan to 1800 seconds. No giant source files are loaded in parallel.

Actual Python: **3.12.13**, `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`. The scan completed successfully; elapsed time before writing was **277.7003 s**, peak RSS **183,916 KiB (179.61 MiB)**, inherited soft/hard `RLIMIT_AS` **32,212,254,720 bytes** each.

```bash
prlimit --as=32212254720 -- timeout 1800s \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B \
  tests/manual/agent_opd/check_swe_benchmark_overlap.py \
  --task-id T01-DEEPSWE-AUDIT \
  --benchmark /data/ycfeng/tmp/qwen35-swe-full-r256/swe_bench2512_all_sorted.json \
  --benchmark-copy-receipt /data/ycfeng/tmp/qwen35-swe-full-r256/benchmark-COPY_COMPLETE.json \
  --manifest /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/task_memory/task_2026-10-01_step3p6_single_teacher_bounded_replay_h200/artifacts/readiness/domain_manifests_1009/swe/domain_manifest.json \
  --sources /data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-0913-exp-1108-205005-924420 \
  --source-selection task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/deepswe-source-selection.json \
  --output task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/deepswe-benchmark-training-overlap.json \
  > /data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-source-audit.log
```

## Validation

| Check | Expected passing condition | Actual | Status |
| --- | --- | --- | --- |
| Positive matching controls | One synthetic match for each of the three methods | 1 / 1 / 1 | PASS |
| Text normalization | Unicode whitespace collapses; case remains significant | Both checks passed | PASS |
| Request-ID exclusion | A request `id` equal to a benchmark ID is not a task identity | No task identity extracted | PASS |
| Streaming parser controls | Chunk-boundary fixture equals standard JSON; malformed/truncated inputs fail | All checks passed | PASS |
| Local input identities | All eight local hashes and byte counts equal the verified source receipt | 8/8; 16,559,540,463 bytes | PASS |
| Full source population | Exhaust all eight arrays and preserve selection/conversation/assistant-position order | 9,254 conversations; 892,620 raw assistant positions | PASS |
| Exact problem-text comparison | Compare all initial statements with the same fixed 100 tasks; retain all matches | 9,254/9,254 covered; zero matching tasks, conversations or pairs | PASS |
| Task-ID/repo+commit comparison | Report comparable-identity coverage and observed matches | Coverage 0; observed matches 0 in every scope | UNVERIFIED |
| Independent artifact reconstruction | Unchanged benchmark payloads; source order/counts; 511/9 raw prefixes; zero exact-text intersection; script identity | All checks passed; log below | PASS |

## Observed Results

Results and matching `(file name, zero-based conversation index)` identities are in [evidence/deepswe-benchmark-training-overlap.json](evidence/deepswe-benchmark-training-overlap.json). The 9,254 source identities use a compact column table; no trajectory contents are archived there. JSON size: **2,316,485 bytes**; SHA256: `75623c82a18a875c26310299e6dbbc3f13d582b9e005ba72d4ccce44a97866a0`.

### Source Population

Labels below abbreviate basenames; the evidence retains their exact ordered paths and hashes.

| Selection position | File label | Conversations | Raw assistant turns |
| --- | --- | ---: | ---: |
| 0 | `deepswe_32_swa_rl_part1` | 951 | 95,051 |
| 1 | `deepswe_32_swa_rl_part2` | 943 | 94,435 |
| 2 | `deepswe_32_swa_rl_part3` | 942 | 93,526 |
| 3 | `deepswe_32_swa_rl_part4` | 923 | 93,349 |
| 4 | `deepswe_8_test_swa_rl_part1 ... ds0p5` | 782 | 76,677 |
| 5 | `deepswe_8_test_swa_rl_part2` | 1,978 | 181,762 |
| 6 | `deepswe_8_test_swa_rl_part3` | 1,969 | 181,915 |
| 7 | `deepswe_8_test_swa_rl_1066_part2 ... ds0p5` | 766 | 75,905 |
| **Total** | **8 files** | **9,254** | **892,620** |

All conversations are lists of message dictionaries, and every message `content` is a string. Role counts: **9,254 system**, **9,255 user**, **892,620 assistant**, **955,242 tool**. There is one more user message than conversations; the audit preserves it rather than normalizing it away.

### Thinking, Tool and Reply Fields

| Observed field/property | Present | Nonempty / actual count |
| --- | ---: | ---: |
| System `tools` | 9,254 | 9,254 |
| Assistant `content` | 892,620 | 171,441 |
| Assistant `reasoning_content` | 564,759 | 564,759 |
| Assistant `tool_calls` | 892,620 | 892,619 messages; 964,496 calls |
| Tool `content` and `tool_call_id` | 955,242 each | 955,242 each |
| Assistant `meta.raw_response` | 892,620 | 892,620 dictionaries |
| Raw choice-message `content` | 892,620 | 171,441 |
| Raw choice-message `reasoning` / `reasoning_content` | 892,620 each | 564,759 each |
| Raw choice-message `tool_calls` | 892,620 | 892,619 |

All 964,496 structured calls carry `type`, `id`, and `function`; every function carries `name` and `arguments`. **One** assistant message has nonempty text without tool calls; this is a structural count, not a claim that only one trajectory has a terminal answer. No assistant content contained the checked inline markers `<think>`, `</think>`, `<tool_call>`, or `<tool_response>`; thinking/tool information is represented in separate fields.

Assistant `loss_mask`: **878,783 with 1**, **13,837 with 0**. Raw coverage includes both. The metadata keys found were `raw_response` (892,620), `masked_reason` (13,643), `masked_by` (13,643), `error` (584), and `completion_mask` (69). These counts do not substitute for the other agent's native normalization and eligibility checks.

### Task Identity and Overlap

Every conversation has one nonempty initial `<pr_description>`: **9,254 statements**, **964 distinct whitespace-normalized SHA256 values**. `Task Description:` occurrences: **0**. Explicit identity fields, initial instance-ID literals, and initial GitHub repository mentions: **0**. No task/repository/commit identity is inferred from API request IDs, tool calls or model labels.

| Scope | Conversations | instance-ID coverage / observed pairs | repo+commit coverage / observed pairs | Problem-text coverage / matching tasks / conversations / pairs |
| --- | ---: | --- | --- | --- |
| All sources | 9,254 | 0 / 0; unverified | 0 / 0; unverified | 9,254 / 0 / 0 / 0 |
| Raw first 51,200 assistant positions | 511 | 0 / 0; unverified | 0 / 0; unverified | 511 / 0 / 0 / 0 |
| Raw first 1,024 assistant positions | 9 | 0 / 0; unverified | 0 / 0; unverified | 9 / 0 / 0 / 0 |

The two raw prefixes both finish inside the first selected source:

- 51,200 positions reach zero-based conversation **510**, which starts at **51,180** and ends at **51,324** exclusive. Included whole conversations contain **51,324** positions; only 20 positions of the final conversation belong to the prefix.
- 1,024 positions reach zero-based conversation **8**, which starts at **1,005** and ends at **1,107** exclusive. Included whole conversations contain **1,107** positions; only 19 positions of the final conversation belong to the prefix.

Repository overlap has **zero observed names**, but **zero source repository-name coverage** in both the explicit-field and GitHub-mention methods. Actual repository overlap is therefore **unverified**, not established as zero. All matching-task/conversation lists are empty. No overlap is silently removed and no handling policy is chosen.

### Independent Artifact Verification

Command and output are bounded and contain no trajectory payloads:

```bash
prlimit --as=1073741824 -- timeout 60s \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY' \
  > /data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-artifact-validation.log
import hashlib
import json
from pathlib import Path

root = Path('task_memory/task_2026-11-08_qwen35_swe_full_r256')
report_path = root / 'evidence/deepswe-benchmark-training-overlap.json'
report = json.loads(report_path.read_text())
previous = json.loads((root / 'evidence/benchmark-training-overlap.json').read_text())
selection = json.loads((root / 'evidence/deepswe-source-selection.json').read_text())
inputs = report['inputs']['training_sources_in_consumption_order']
assert [row['original_path'] for row in inputs] == selection['paths']
assert len(inputs) == 8 and sum(row['bytes'] for row in inputs) == 16559540463
assert all(row['copy_receipt_sha256_match'] for row in inputs)
for key in ('benchmark_library', 'ordered_manifest'):
    assert report['inputs'][key]['sha256'] == previous['inputs'][key]['sha256']
assert report['benchmark_tasks'] == previous['benchmark_tasks']
assert len(report['benchmark_tasks']) == 100
encoded = report['training_conversation_identities']
rows = [dict(zip(encoded['columns'], values)) for values in encoded['rows']]
assert len(rows) == 9254
assert sum(row['assistant_turn_count'] for row in rows) == 892620
position = 0
for file_index, source in enumerate(inputs):
    file_rows = [row for row in rows if row['file_index'] == file_index]
    assert len(file_rows) == source['conversations']
    assert [row['conversation_index'] for row in file_rows] == list(range(source['conversations']))
    assert sum(row['assistant_turn_count'] for row in file_rows) == source['assistant_turns']
for row in rows:
    assert row['first_assistant_stream_index'] == position
    position += row['assistant_turn_count']
benchmark_hashes = {row['problem_statement_sha256'] for row in report['benchmark_tasks']}
for name, budget, expected_count in (
    ('all_conversations', None, 9254),
    ('first_51200_assistant_turns', 51200, 511),
    ('first_1024_assistant_turns', 1024, 9),
):
    included = rows if budget is None else [row for row in rows if row['assistant_turn_count'] and row['first_assistant_stream_index'] < budget]
    assert len(included) == expected_count
    scope = report['scopes'][name]
    assert scope['conversation_count'] == expected_count
    assert scope['last_conversation']['conversation_index'] == included[-1]['conversation_index']
    assert not benchmark_hashes.intersection({value for row in included for value in row['problem_statement_sha256']})
    for method in ('exact_instance_id', 'repo_and_base_commit', 'normalized_problem_statement_sha256'):
        result = scope['overlap'][method]
        assert result['matching_pair_count'] == len(result['matches']) == 0
    assert scope['overlap']['normalized_problem_statement_sha256']['conversations_with_comparable_identity'] == expected_count
    assert scope['overlap']['exact_instance_id']['conversations_with_comparable_identity'] == 0
    assert scope['overlap']['repo_and_base_commit']['conversations_with_comparable_identity'] == 0
counts = report['training_identity_counts']
assert counts['pr_description_count'] == 9254
assert len({value for row in rows for value in row['problem_statement_sha256']}) == 964
format_counts = counts['format_counts']
assert format_counts['loss_mask_by_role']['assistant.1'] + format_counts['loss_mask_by_role']['assistant.0'] == 892620
assert format_counts['raw_choice_message_nonempty_fields']['reasoning_content'] == format_counts['nonempty_fields_by_role']['assistant.reasoning_content'] == 564759
assert format_counts['raw_choice_message_nonempty_fields']['content'] == format_counts['nonempty_fields_by_role']['assistant.content'] == 171441
assert report['positive_controls']['status'] == 'PASS'
script = report['execution']['script']
assert hashlib.sha256(Path(script['path']).read_bytes()).hexdigest() == script['sha256']
assert report['execution']['rlimit_as_soft_hard_bytes'] == [32212254720, 32212254720]
assert report['execution']['peak_rss_kib'] * 1024 < 30 * 1024**3
print('PASS: eight approved inputs, 16,559,540,463 bytes, unchanged 100-task payloads, 9,254 conversations/892,620 turns, source order, 511/9 raw prefixes, all zero exact-text intersections, missing identity coverage, format consistency, positive controls, script identity and memory limit.')
print('evidence_sha256=' + hashlib.sha256(report_path.read_bytes()).hexdigest())
PY
```

Actual output: **PASS**. Log: `/data/ycfeng/tmp/qwen35-swe-full-r256/deepswe-artifact-validation.log`.

## Verification Limits

- This audit does not establish native loader parity or Qwen rendering/length eligibility; those are owned by the separate input-parity agent.
- Raw first-51,200 and first-1,024 assistant-position membership must not be called the effective eligible stream.
- Missing task/repository/commit fields leave the corresponding identity method unverified where coverage is absent. Zero observed matches alone cannot establish absence of overlap.
- Exact text matching does not detect paraphrases, aliases, translations, or edited copies; repository mentions can concern other projects.
- No GPU, platform, authentication, SSH, cloud write, training/evaluation mutation, commit, or overlap-handling decision is performed by this subtask.
