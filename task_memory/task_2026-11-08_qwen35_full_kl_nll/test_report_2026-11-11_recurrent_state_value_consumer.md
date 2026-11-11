## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Prepare the scoped consumer/data integration, retain CPU contract failures and passing checks, and identify producer-schema/native limits. |

# Recurrent-state value consumer preparation

TaskID: `profile-recurrent-state-value-consumer-20261111`.

**Outcome:** consumer source preparation and affected contract checks PASS. Real producer integration and native capture/replay remain **UNVERIFIED**. Root remains **UNRESOLVED**, warm1/4 FAIL and formal HOLD. Existing `281e`/`e2`/`7ae` qualification is not reopened. No producer implementation inspection, native library/model/GPU/platform/auth/network action, delegation, staging or commit was performed.

## Deliverables and interface

- `tests/manual/agent_opd/probe_teacher_scoring.py`: `_config_input` carries the wrapper-owned selector; `_recurrent_workload` resolves each selected original index exactly once from the existing first4 fixture and calls the unchanged full-input payload mechanism. `_run` derives this workload once and passes named `recurrent_input_counts` and `recurrent_common_rows` to its **one existing** `coherence.prepare_source` call. Private-package -> FP32 -> metadata -> WIT -> native coherence preparation order and nested preflight receipts are retained.
- `task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_coherence_probe_config.json`: the sole new data field is `recurrent_sample_original_indices=[1693,1695]`. No CLI/env/feature/retention flag, engine setting, salt, header, request or flush is added.
- `_collect_runtime_metadata` uses its existing after-all16 drain. Only after original FULL binding/error-marker/join checks succeed does the recurrent consumer run. `_recurrent_cases` joins four actual full-input response RIDs to request/meta/completion source identities and their actual recorded cache flushes. `_recurrent_state` joins RID/P/extend/input count to existing layer-0 `gdn_snapshot_allocation` CPU metadata. Record order never determines source or phase.
- `runtime_metadata.json.recurrent_state` and `result.json.recurrent_state` carry a separate compact result, responding process/rank/state index and annotations. `joined` means provenance joined, **not** numerical/causal/formal acceptance. Consumer errors return only recurrent `UNVERIFIED`; original scoring/FULL statuses and completion vectors remain unchanged. The original independent native error-marker failure still fails its original gate.
- Producer `server_info.internal_states[].kv_coherence.recurrent_state` is retained verbatim, including comparisons, replay results, descriptors, coverage, errors and unavailable canonical-P fields. No metric recomputation or raw tensor arrays are introduced. Unequal state/control outputs do not become a root/fix inference.
- `tests/fast/test_teacher_scoring_probe.py`: proportional source/data/DI checks in the existing module, including all16/ten-flush preservation, reversed opaque record ordering, soft failure and unchanged native error-marker behavior.

## Observed data derivation

The existing manifest selects original fixture entries 1693,1694,1695,1696. Only the two data-selected entries reach the recurrent preparer:

| Original index | Actual full-input payload tokens | Continuation at existing P | Original position |
| --- | ---: | ---: | ---: |
| 1693 | 97365 | 7253 | 0 |
| 1695 | 98942 | 8192 | 2 |

Actual equal token prefix is 96631 tokens; subtracting existing `WINDOW_START=90112` gives 6519 common continuation rows. Source UIDs, selected order, fixture SHA and exact values are recorded in [static-validation.json](evidence/recurrent-state-value-preparation-20261111/consumer/static-validation.json). Lengths/common6519 are verification expectations, not new core literals. Reversing the selector reverses the data arguments but retains the actual common prefix. Missing/ambiguous original indices, equal provisional lengths, too-short inputs and unsupported common-prefix geometry are explicitly rejected before serving.

## Commands, environment and results

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`.

CPU interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13 / pytest9.1.1, no conda activation. Temporary files stay under `/data/ycfeng/tmp/opencode-v2-tmp/opencode`. No bytecode/cacheprovider or native/model/GPU work. Whole-module/broad closed suites were **not** rerun; these are affected selections, not a new whole-module timing claim.

Final affected selection:

```bash
timeout 60s env TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -p no:cacheprovider -k 'recurrent or coherence_required_dependencies or coherence_wrapper_opt_out or coherence_boolean_validation or coherence_numeric_predicates or kv_stream_witness_api_binding_order' --junitxml=task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/recurrent-state-value-preparation-20261111/consumer/pytest-r3.xml
```

PASS: **53 passed, 0 skipped, 228 deselected, 4 pre-existing warnings, 2.88s** pytest session time. [Log](evidence/recurrent-state-value-preparation-20261111/consumer/pytest-r3.log) / [JUnit](evidence/recurrent-state-value-preparation-20261111/consumer/pytest-r3.xml).

After adding explicit responding rank/state-index annotations, only the changed recurrent checks were repeated:

```bash
timeout 60s env TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_teacher_scoring_probe.py -q -p no:cacheprovider -k recurrent --junitxml=task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/recurrent-state-value-preparation-20261111/consumer/pytest-final.xml
```

PASS: **31 passed, 0 skipped, 250 deselected, 4 pre-existing warnings, 2.38s**. [Log](evidence/recurrent-state-value-preparation-20261111/consumer/pytest-final.log) / [JUnit](evidence/recurrent-state-value-preparation-20261111/consumer/pytest-final.xml). Both affected timings are below the existing 30-second fast-file budget; no registration change is made.

Passing conditions and actual results:

- Both selector orders use exactly two unchanged `_score_payload` calls; actual counts/common prefix match the table: PASS.
- Named preparer data reaches its existing real call site exactly once; mocked preparer/worker order, receipts and unchanged teacher argv are checked: PASS **interface only**.
- One initial existing server-info read, then all16 scoring requests/ten flushes, then one existing drain and four actual source/phase joins: PASS **mock lifecycle only**.
- Missing/duplicate/wrong RID, wrong phase/extend/process/common rows, absent descriptors/forward observation, partial paired comparisons/replays and metadata-only producer evidence yield recurrent `UNVERIFIED`; all16 scores and original FULL/scoring result remain retained: PASS.
- Canonical-P unavailable remains field-level unavailable; opaque unequal component/control metrics remain unchanged without a tolerance/root/fix verdict: PASS **fixture contract only**.
- The original independent native error-marker gate remains a failure, retains all16 score artifacts, and is not hidden by the recurrent consumer: PASS **injected marker only**.

Static validation uses `/usr/bin/python3`, Python3.10.6:

```bash
timeout 60s /usr/bin/python3 -B task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/recurrent-state-value-preparation-20261111/consumer/verify.py
git diff --check -- tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_teacher_scoring_probe.py task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_coherence_probe_config.json
```

PASS: both Python ASTs, strict config JSON, actual selected source counts/common-prefix verification and whitespace. Nine unchanged function ASTs match the committed baseline: `_parser`, `_payload`, `_scores`, `_comparison`, `_request`, `_benchmark`, `_native_observer_errors`, `_coherence_native_bindings`, `_coherence_states`. Exact hashes/values are in [static-validation.json](evidence/recurrent-state-value-preparation-20261111/consumer/static-validation.json); the command/script never reads the changing producer implementation.

## Retained unsuccessful checks

1. [First command](evidence/recurrent-state-value-preparation-20261111/consumer/command.json): 60 selected, 27 failed/33 passed, 0 skipped. Existing/new source-dependent checks imported the independently changing producer and encountered `sglang_kv_coherence.py:1009 SyntaxError: invalid syntax. Perhaps you forgot a comma?`. [Original log](evidence/recurrent-state-value-preparation-20261111/consumer/pytest.log) / [JUnit](evidence/recurrent-state-value-preparation-20261111/consumer/pytest.xml) remain intact. No producer read/fix or timing poll followed. A separate explicit **consumer contract fixture** then replaced producer/package execution only in the new tests; it is not a production fallback or producer qualification.
2. [Second command](evidence/recurrent-state-value-preparation-20261111/consumer/command-r2.json): 52 passed/1 failed. The phase fault was injected inside mocked HTTP readback, **after** the existing collector had already read request rows, so it did not affect the intended join input. This was a fixture boundary error, not evidence of a native phase bug. The injection moved to after benchmark/before readback; production behavior was unchanged. [Log](evidence/recurrent-state-value-preparation-20261111/consumer/pytest-r2.log) / [JUnit](evidence/recurrent-state-value-preparation-20261111/consumer/pytest-r2.xml) are retained.

## Hashes and pending producer confirmation

| Owned file | SHA256 |
| --- | --- |
| `tests/manual/agent_opd/probe_teacher_scoring.py` | `7a578a6c301d610f8a98fd21601ef574b29a6487edd6122ad07a6287f780cb9b` |
| `tests/fast/test_teacher_scoring_probe.py` | `2ba78eb18bf55c7dbcbbdbac867e8b8334df59920366596bcd1a2f742daad4e2` |
| `teacher_scoring_kv_coherence_probe_config.json` | `b1398fcc28c87e05002263ef04ccdef782dfcb815376a2faeb6a7991eef395b4` |

**Primary/producer confirmation still required:** record descriptors are currently required to be a nonempty object but their internal component schema is opaque. Comparisons consume `left_rid`, `right_rid`, integer `common_rows`; replays consume `rid`, nonempty string `kind` and status, with coverage of all four RIDs. Confirm actual replay-kind literals, the compared-RID field(s), descriptor/component-metric schema, and whether canonical-only unavailable comparisons have a different applicable `common_rows` shape. These unresolved internals are **not guessed, recomputed or parsed through aliases**. The mock `components` payload illustrates preservation only, not a negotiated native format. Joined provenance does not attest control count, metric validity, descriptor-internal tensor shape or replay fidelity.

Real producer preparation/readback integration, native capture/replay, canonical-P publication fidelity, actual descriptor/peak-memory/traffic measurements, all-TP coverage and causal/warm/formal correctness remain unexecuted or unverified. Primary owns joint acceptance and any later unchanged approved D40 native decision.

## 1. Planned completion

PASS 3; SKIPPED 1; TODO 1.

| Scoped subtask | Status | Evidence |
| --- | --- | --- |
| Resolve selector/data and wire existing preparer once | PASS | Actual fixture checks and injected preparation order/data assertions. |
| Independent after-all16 source/cache/forward join | PASS | Four reversed opaque RIDs, scoped failure cases, score/FULL preservation. |
| Affected CPU/AST/JSON/whitespace checks and evidence | PASS | 53 affected checks, final31 checks and static validation. |
| Confirm exact producer internals and real integration | TODO | Explicit schema points above; producer is independently owned. |
| Execute native/model/GPU/platform validation | SKIPPED | Outside this delegated CPU/source-only scope. |

## 2. Drift detection

Window: delegated consumer preparation through final CPU verification. Mainline: data derivation -> existing preparer/readback integration -> independent join -> affected checks -> producer contract confirmation. No execution drift.

| Pattern | Verdict | Evidence |
| --- | --- | --- |
| D1 Tooling polish | CLEAR | Existing module only; affected selections stop after verification. |
| D2 Retry loop | CLEAR | Producer import failure and phase-injection boundary failure were distinct diagnosed failures; retained evidence and one scoped correction each. |
| D3 Side quest | CLEAR | No producer/kernel/pool investigation or unrelated edits. |
| D4 Stalled frontier | CLEAR | Primary owns independent producer work; further delegation is expressly prohibited. |
| D5 Gold-plating | CLEAR | One data selector, existing source/preparer/drain, no production fallback/feature flag/framework. |
| D6 Analysis sprawl | CLEAR | Inspected seams led directly to the owned implementation and checks. |
| D7 Off-route | CLEAR | Closed qualification, original native gate, scientific payload/order and formal holds remain unchanged. |

S1–S6: no scoped plan/ticket defect; the latest explicit preparation delegation governs this slice, while primary-owned master documents retain their prior design-stage window. Attribution: none.

## 3. Route correction

Branch A for this delegated slice; do not edit master requirements/plan/design/tickets. Stop actions: none. Next: primary/producer confirms the exact opaque internal schema and accepts the joint interface. That confirmation may settle only interface consistency; any native measurement remains a separate primary-owned action under the unchanged approved experiment, not a closed-suite rerun or a new permission gate.

## 4. Three points to retain

1. Payload-derived97365/98942/common6519 data reaches the existing preparer once; these are not core constants or new scoring inputs.
2. Recurrent incompleteness is independent of healthy completed scoring/FULL; the original native error gate is unchanged.
3. CPU mocks prove only the consumer interface. Exact producer internals/native fidelity and the warm/root/formal outcome remain unresolved.
