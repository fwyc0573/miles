## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Direct actual producer receipt to unmocked consumer contract regression passed24 cases/1.01s; source is CPU-ready for fixed reviews, with no native/GPU acceptance. |
| 2026-11-11 | Producer delivered54 CPU PASS/19.35s; two-file composed run303 PASS/0 SKIP/34.27s. A single direct producer-output/consumer-input regression remains pending before freezing reviews. |
| 2026-11-11 | Consumer delivered 83 focused CPU PASS, zero SKIP, with after-all16 identity checks and artifact preservation; producer and joined verification remain pending. |
| 2026-11-11 | Record the missing serving-process binding identity and the selected minimal producer/consumer CPU work; native execution remains unstarted. |

# KV coherence serving binding identity

## Scope and acceptance

The current CPU scope adds the serving-process Rust module identity that the existing native qualification already requires. It is ordinary D40 diagnostic work within tickets 04/05, not a new model benchmark, new native build, or a teacher correctness fix. The earlier EXTEND-scope fix `eeaaa4f6`, its 49 passing CPU tests, both fixed reviews and the records commit `71c3560b` remain accepted.

The gain is a direct join between the native instance used for insertion and the expected private artifact. Existing preparation verifies copied bytes and private package resolution; it does not identify the extension actually used by the serving process. The added receipt makes the original artifact-identity criterion verifiable before paying for another H800 capture attempt. It adds no serving decision, env/argv flag, RPC, tensor copy, stream probe, tree walk, CUDA operation, wait or lock.

## Read-only readiness findings

Inspector: native explore session `ses_e35e0581affeqUCQ0k47BKNb3I`, TaskID `profile-kv-coherence-native-receipt-readiness-20261111`. Two bounded source/receipt inspections completed; no source edits, tests, native execution, authentication or platform operation were performed by the inspector.

| Check | Observed result | Verdict |
| --- | --- | --- |
| Existing inline OLD/scheduler witness | `Collector.insert` and inline callback record the OS thread and Torch S; callbacks require equality. The unconditional drain includes the serving PID. Retained A r2 shows PID/thread 340 and S 1320513136 for both OLD fragments. | PASS for existing receipt capability; r2 capture itself remains unverified. |
| Serving module identity | At `eeaaa4f6`, `prepare_package.serving_native_origin_sha` is a literal PENDING string; drain has no loaded module identity. Source hashes and post-copy verification only bind staged bytes. | Missing capability; no unchanged successful r3 could clear this gate. |
| Existing actual-instance hook | The injected `checkpoint_into_tree` call passes `self.tree_core` into `Collector.insert` immediately before the real insertion. The collector is initialized after pool finalization. | PASS for an existing reachable receipt seam. |
| Native class/module relation | The pinned adapter holds the loaded `extension.bindings` module in class attribute `_bindings`; its `_binding` instance is constructed through `_binding_class()`. PyO3 classes do not specify a Python module annotation. | Use module-export object identity and factory-class identity; do not gate on class `__module__` text. |

Sources inspected include `tests/manual/agent_opd/{sglang_kv_coherence.py,sglang_rust_kv_observer.py,probe_teacher_scoring.py}`, the retained native adapter/extension/Rust binding sources and selected r2 `preload.json`/`runtime_metadata.json`. The existing serving readback is `server_info.internal_states[i].kv_coherence`; this is not an all-TP gather.

## Selected implementation and dependencies

1. **Producer:** `sglang_kv_coherence.py` and its existing fast test file. Capture the actual extension module file, SHA256 and size, module/class labels, serving PID, and the two class-object ties once at the top of `Collector.insert`, before the selected-bank early return. Cache success or diagnostic failure. Emit identity and a precise binding error through the existing unconditional drain. Missing/error identity refuses the requested numeric drain without raising into serving.
2. **Consumer, in parallel:** `probe_teacher_scoring.py` and its existing fast test file. Pass the unchanged native preparation receipt to the existing post-loop metadata check. On the existing after-all16 drain only, require actual path/SHA to match `native_observer.binary_target`/`compiled_sha256`, identity PID to match the drain PID, and both class ties to be exactly True. Initial metadata snapshots and the opt-out path remain unchanged. Preserve the raw readback and all 16 score artifacts on rejection.
3. **Joined validation and fixed reviews:** execute the affected composed source/preparation/readback checks, verify selected source/R3 identities, then review Standards and Spec against one frozen diff. Primary acceptance, commit and existing driver dry-runs follow. Only then decide the already-authorized bounded native qualification.

The expected artifact is already identified by the accepted R3 observer receipt: receipt-file SHA256 `91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7`; observer binary SHA256 `0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba`. These are distinct hashes. The native helper, adapter overlay, libraries, compile/qualification inputs and old receipts must remain unchanged.

No adapter-initialization overlay is added: the current insert hook already receives the actual instance, while another adapter rewrite would complicate the pinned native preparer's repeat-preparation contract without supplying additional evidence. No dev/inode/mtime fingerprint, build-id, `/proc` map reader, loader-mode default, source collection or new runtime expected-SHA transport is needed.

## Verification status

| Phase | Expected result | Actual result |
| --- | --- | --- |
| Readiness and seam investigation | Identify a concrete missing receipt and an existing instance-bearing hook. | PASS, as above. |
| Producer CPU regression | One-time capture before RID selection; real file hash; exact exported/factory class ties; isolated failure; all existing EXTEND fault cases retained; whole-file fast budget under 30 seconds. | PASS:5 affected cases/1.90s; whole existing module54 PASS/19.35s/0 SKIP, run once by producer. |
| Consumer CPU regression | Reject missing/path/SHA/PID/class/error mismatches after all16; retain initial/opt-out behavior and artifacts. | PASS: 83 focused cases, zero SKIP, 166 deselected, 6.05 seconds; task `profile-kv-coherence-serving-binding-consumer-20261111`. Producer integration not executed. |
| Composed source/RPC binding, fixed review and driver | Existing chain/pins preserved; no missing-evidence skip counted as acceptance; unchanged H800 allocation/argv except new output. | Two-file run303 PASS/0 SKIP/34.27s, then24 direct-contract/table cases PASS/0 SKIP/1.01s. Fixed review and final driver remain PENDING. |
| Actual serving native identity, active all16 vectors, physical 7955 and KV | Obtain separate native verdicts before interpreting any KV number. | NOT RUN; r3 GPU submission has not occurred. |

### Consumer delivery

The consumer changed only `tests/manual/agent_opd/probe_teacher_scoring.py` and `tests/fast/test_teacher_scoring_probe.py`. It passes the original native receipt to the existing readback helper; `_coherence_native_bindings` runs after all16 and the existing drain readback, before `_coherence_states` accepts summaries. The initial snapshot has no identity gate. A rejected identity retains all16 score files, earlier artifacts, parsed `server_info` and the exact response text, with no accepted summary. All27 other existing probe functions, including the structural/numeric and native invalidation-marker checks, are unchanged in the recorded normalized AST comparison.

Environment: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13 / pytest9.1.1; `/usr/bin/python3`, Python3.10.6 for AST/scope. No conda activation or native extension execution. Exact command and test names/timings are in [the consumer report](evidence/kv-coherence-serving-binding-20261111/consumer/test_report_2026-11-11_consumer_serving_binding.md#commands-and-environment), [pytest.log](evidence/kv-coherence-serving-binding-20261111/consumer/pytest.log) and [pytest.xml](evidence/kv-coherence-serving-binding-20261111/consumer/pytest.xml). The focused command uses `timeout 60s`, `-B`, `-p no:cacheprovider`, the existing teacher-probe fast file and its selected binding/controls cases. Four pre-existing SWIG/datetime warnings remain in the log. Scoped `git diff --check` and Python3.10 AST checks PASS.

Recorded source SHA256: probe `19bf42be9802a9160dad9c80d4a7a2465c9af0c0c4fabf305283ce073bd812df`; teacher fast test `9fccf667b7d55f300b5c20e4dc85577e0ab6227f27f7be8272b906d4f57ec57e`. [scope.json](evidence/kv-coherence-serving-binding-20261111/consumer/scope.json) records exact changed functions; [artifact_hashes.json](evidence/kv-coherence-serving-binding-20261111/consumer/artifact_hashes.json) identifies the retained evidence. The consumer did not stage or commit. Primary inspected the decisive gate and main wiring; fixed review and composed producer/runtime qualification remain pending.

### Producer and composed delivery

Producer commands/environment and the source-DI identity comparison are retained in [producer.md](evidence/kv-coherence-serving-binding-20261111/producer/producer.md). Python3.12.13/pytest9.1.1 ran5 affected cases in1.90s and the whole existing module once:54 PASS,0 SKIP,19.35s, below the30-second per-file budget. A fake class/module graph backed by real CPU file bytes checks capture before bank selection, canonical path/SHA/size, both object ties, one-shot success/failure caching and refusal before physical/metric reads. PyO3 `class_module="builtins"` remains accepted through object ties. All six malformed EXTEND variants and12 error assertions remain. Binding errors are retained as a precise string with an existing global diagnostic error, never raised into serving.

Producer source SHA256 is `6be5ef8642f33512fb463f30040247750b472716289eba0c139cb65e5d005721`; its fast test SHA256 is `16c5b496eb28f91feec390993d98e9abb282c2fd9d6c011b5b10f56f07b0d78c`. Generated runtime SHA256 is `7ed5b5fb56ef736afee2c9e9aefa7543a779e53f18b3cf3cf7c0943618816308`. The35 source and additional native pins, private-package/source composition, native helper, libraries and selected R3 receipt remain unchanged. The producer's inspection initially assumed a non-retained `cpu-source-di/after/` directory and received FileNotFoundError; its corrected read-only check uses the actual generated source and retained SHA. This was not a source, build or native failure.

Primary then ran both affected fast files together using the complete retained-source override. Exact argv/environment/cwd are in [joined/command.json](evidence/kv-coherence-serving-binding-20261111/joined/command.json); [pytest.log](evidence/kv-coherence-serving-binding-20261111/joined/pytest.log) and [pytest.xml](evidence/kv-coherence-serving-binding-20261111/joined/pytest.xml) record303 PASS,0 SKIP,4 pre-existing warnings,34.27s, exit0. This duration is for two files together, not the single-file budget. The command uses `timeout 60s`, the same CPU interpreter, `-B`, `-p no:cacheprovider` and `MILES_PINNED_SGLANG_SOURCE` pointing to the5501-file archive; it performs no native/GPU execution.

The two-file run covers existing real source preparation and mocked runtime/readback, but its positive HTTP fixtures construct identity fields directly. One additional bounded contract regression now passes: actual `Collector.insert` for a nonselected request produces a metadata-only `drain(False)` receipt, which is passed directly to the unmocked consumer checker. Its real CPU file hash/size, PID and both exported/factory class-object ties are asserted. This uses a fake native class/module, not a native ABI claim. Exact command/log/scope are in [consumer/direct-producer-join](evidence/kv-coherence-serving-binding-20261111/consumer/direct-producer-join); [result.json](evidence/kv-coherence-serving-binding-20261111/consumer/direct-producer-join/result.json) records24 PASS/0 SKIP/1.01s, consisting of one new direct case and the23 existing table cases, run once. The probe and producer code did not change during this follow-up. Current teacher-fast-test SHA256 is `584db1ee77830dfcea8df37a247a52d36b1b6373ff8eb5127c14c934dd2aefad`; the earlier consumer hash remains historical. No full304-case rerun or304-case joined result is claimed.

Primary also checked [joined/summary.json](evidence/kv-coherence-serving-binding-20261111/joined/summary.json) against JUnit XML:303 cases,0 failures/errors/skips; summed testcase times21.373s for54 collector cases and11.664s for249 teacher-probe cases. Source is now CPU-ready to freeze for fixed Standards/Spec review. Previous49-test acceptance is not acceptance of this new receipt, and none of these CPU results establishes actual serving private-SO or CUDA qualification.

## Limits

The SHA describes the file at the loaded module's resolved path, tied to the actual native class and serving PID. It is not an independent hash of mapped ELF pages. Its bounded interpretation relies on the fresh job-owned private package, verified artifact staging and the absence of a post-import file writer; hostile file replacement is not a supported scenario. Mock class/real-file CPU tests cannot prove native PyO3 ABI, serving module loading or CUDA execution.

Actual callback S/thread equality is already supplied by the existing receipt; its accepted scope is not expanded to all TP ranks. Original bundled-binary source commit and unsupported arbitrary Mutex reentry remain unchanged limitations, not new build blockers. Original r1/r2 capture failures, both accepted r2 controls, warm correctness failure, scientific settings and formal 04/05 HOLD remain preserved. Ticket06 still requires each independent cell's real 200 successful updates; B does not wait on A200.
