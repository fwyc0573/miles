## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record final consumer-only CPU, AST/scope, preservation, and checksum evidence. |

# Serving binding consumer verification

TaskID: `profile-kv-coherence-serving-binding-consumer-20261111`.

## Outcome and scope

**PASS: 83 focused CPU checks, zero skips; Python 3.10 AST/scope and scoped whitespace checks.** Base: `71c3560b84870d39179d5bd63a9c8ce67cf431ee`, which follows accepted code `eeaaa4f6`. No platform/authentication/GPU/native build/delegation/staging/commit operation or producer/full-join verification was performed.

Changed source:

- `tests/manual/agent_opd/probe_teacher_scoring.py:556`: one optional expected `native_observer` argument on the existing metadata readback helper; qualification runs only after all16 and the existing drain HTTP readback, before `_coherence_states` accepts summaries.
- `tests/manual/agent_opd/probe_teacher_scoring.py:599`: actual module path/SHA equals the prepared binary target/SHA; actual binding PID equals the capture PID; both factory/class booleans are exactly true; `binding_error` must exist and be null. Missing expected receipt/fields or actual identity fails with field-specific reasons. No `class_module == module` condition, staged-byte substitute, native import, CPU-library fallback, transport, or new flag.
- `tests/manual/agent_opd/probe_teacher_scoring.py:817`: main passes the unchanged preparer-returned native receipt only in the enabled branch, after scoring.
- `tests/fast/test_teacher_scoring_probe.py:642,910,942,1655`: reuse the lifecycle/mock HTTP and native metadata fixtures; add 23 table cases and two all16 missing-binding/expected-receipt failures. The synthetic class module intentionally differs from its extension-module label.

## Observed acceptance evidence

| Requirement | Expected | Observed | Result |
| --- | --- | --- | --- |
| Actual identity versus expected receipt | Exact path/SHA/PID and strict booleans; no missing evidence bypass | 23 accepted/failing table cases, with immutable original info/receipt and field-specific failures | PASS |
| Parent receipt wiring | Same native receipt object, retained verbatim | Existing lifecycle fixture checks object identity; source-preflight JSON remains equal | PASS |
| Only post-all16 qualification | Initial metadata-only binding may be null; no early gate | Initial existing GET retains null binding; qualifier sees 16 scores; existing GET counts `[0,16]` | PASS |
| Opt-out and controls | False/absent skips all coherence preparation and qualification | Existing import guard, native argv/payload equality, opt-out/shallow-merge and preparer order checks | PASS |
| Failure evidence preservation | All scores, prior records and original readback retained; no accepted summary | All16 score files and before-readback bytes preserved; `server_info` equals parsed original `response_text`; failed summaries empty; numerical acceptance null | PASS |
| Existing gates | Native invalidator marker, schema/RID/OLD/physical/checkpoint/fragments remain independent | Existing marker rejection and nine structural cases pass; `_coherence_states` and `_native_observer_errors` ASTs unchanged | PASS |
| Existing preparer chain | Reuse existing real source preparation, without native acceptance | `test_kv_stream_witness_real_preparers_join_before_runtime` passes; real clean-child package copy remains exercised | PASS |
| Minimal source scope | Only gate, drain call and expected receipt plumbing change | Whole normalized source AST equals baseline; all 27 other existing functions unchanged; scoped `git diff --check` clean | PASS |

All table/lifecycle binding observations are **synthetic CPU schema evidence**, not actual serving private-SO identity, native alias/GIL/thread/CUDA qualification, or numerical acceptance. The existing responding-DP coverage limitation is unchanged. Producer integration and any broader join/native qualification remain with the primary.

## Commands and environment

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`.

Observed runtime: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python 3.12.13, pytest 9.1.1; system AST verifier `/usr/bin/python3`, Python 3.10.6. No conda environment was activated. Temporary files use `/data/ycfeng/tmp/opencode-v2-tmp/opencode`; bytecode and pytest cache writes are disabled.

Final focused command (exit0; **83 PASS / 0 SKIP / 166 deselected / 6.05s**):

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q -p no:cacheprovider tests/fast/test_teacher_scoring_probe.py -k 'coherence_serving_binding or coherence_true_only or kv_stream_witness_api_binding or coherence_wrapper_opt_out or kv_stream_witness_probe_selection or kv_stream_witness_dependencies or kv_stream_witness_real_preparers_join_before_runtime or coherence_numeric_predicates or coherence_schema_joins or metadata_single_dp_without_controller or first4_16_requests_10_flushes_then_one_existing_endpoint_readback or kv_stream_witness_inherited_true_run' --junitxml=task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/kv-coherence-serving-binding-20261111/consumer/pytest.xml > task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/kv-coherence-serving-binding-20261111/consumer/pytest.log 2>&1
```

Exact executed AST/scope command: [scope-command.txt](scope-command.txt). It writes `scope.json` and `consumer.diff` exclusively; replay needs a fresh evidence output directory. Explicit whitespace command:

```bash
git diff --check -- tests/manual/agent_opd/probe_teacher_scoring.py tests/fast/test_teacher_scoring_probe.py
```

The initial focused command and 38-PASS result are recorded in [progress.md](progress.md); the final run includes those cases. Four pre-existing SWIG/datetime deprecation warnings are retained in [pytest.log](pytest.log). Individual test names and timings are retained in [pytest.xml](pytest.xml).

## Frozen hashes

| Artifact | SHA256 |
| --- | --- |
| `tests/manual/agent_opd/probe_teacher_scoring.py` | `19bf42be9802a9160dad9c80d4a7a2465c9af0c0c4fabf305283ce073bd812df` |
| `tests/fast/test_teacher_scoring_probe.py` | `9fccf667b7d55f300b5c20e4dc85577e0ab6227f27f7be8272b906d4f57ec57e` |
| `consumer.diff` | `6f01e3887576ae416854c0f9de51ef28436941b720cd97a18d2f9afbd768a655` |

Machine-readable source identities, baseline, changed/unchanged function lists, and scope limitations: [scope.json](scope.json). Primary owns review, producer integration, reporting outside this consumer directory, and any final commit.
