# Publication and same-version restoration receipt validation

## Modification History

| Date | Change |
| --- | --- |
| 2026-11-07 | Parent validates the real original B origin, closes the fixture-only pinned failure with89 passing checks and retains new formal-chain qualification as pending. |
| 2026-11-07 | Record QWEN-P3-PUBLICATION-RECEIPTS consumer repair, CPU red/green evidence, and native-runtime limits. |
| 2026-11-07 | Diagnose pinned shared-pytest fake-native lifetime failure and record fixture-only repair, minimal predecessor red/green, and retained real-process protections. |

## Scope and outcome

### Parent pinned closure

`exp-1107-125038-984696` passed the new `_origin` consumer on the original B baseline `native-prerequisites/student/B/exp-1107-055408-654957`; the selected genuine initial event is retained in [source/origin evidence](evidence/restore-source-exp-1107-125038-984696.json). Its combined suite passed133 checks; only the shared-interpreter fake-engine case below failed. The actual complete monitoring module and affected core checks passed.

After the fixture-only correction, pinned0-GPU job `exp-1107-130833-742234` ran the precise predecessor **followed by the full affected reload file in the same interpreter**:

```bash
CUDA_VISIBLE_DEVICES="" /opt/sglang/bin/python3 -B -m pytest \
  -p no:cacheprovider -o addopts='' -q \
  tests/fast/backends/megatron_utils/test_score_log_probs.py::test_gloo_tp_cp_and_dp_payload_mapping \
  tests/fast/test_qwen_reload.py
```

Expected: all checks pass while the shared tracker remains correctly owned; real isolation guards and whole-interpreter cleanup regressions remain active. Actual: **89 passed,22 warnings in66.59s**, exit0 and platform Succeeded. [Complete log](evidence/hf-test-isolation-exp-1107-130833-742234.log) contains no failed check or ignored exception. Python3.12.16, unchanged pinned Miles image; CUDA compatibility library and offline settings match the task's other pinned checks. This closes the test-isolation blocker without changing production behavior. A repaired formal run's actual restoration receipts and final HF artifacts have not yet been produced.

Task: **QWEN-P3-PUBLICATION-RECEIPTS**. Read requirements D8/D9 and the current P3 plan before implementation. Only receipt consumers, their two existing CPU test files, and this new report changed. No producer, RPC, event schema, training, dependency, platform, GPU, SSH, cloud or Git operation was performed. The parent-owned main reports and the existing ResourceTracker owner fix were preserved. `tests/fast/test_qwen_reload.py` still registers stage-b CPU at 60 seconds.

The reader now distinguishes the initial publication, planned rollout publications and same-version restorations. Restores never contribute to successful/skipped optimizer counts. The final HF reload remains bound to the planned rollout99 publication ID, including when a final restore follows it. Malformed or ambiguous receipts remain INCOMPLETE.

## Inspected producer contracts

| Source | Observed contract |
| --- | --- |
| `train.py:162,219-222` | The initial `update_weights` is awaited before baseline evaluation/generation dispatch. |
| `train.py:105-111` | Evaluation weight restoration calls the same full publication path with the default `rollout_id=None`. |
| `train.py:275-281` | A planned rollout is published with its actual rollout ID before that rollout's evaluation dispatch. |
| `miles/ray/train/group.py:467-503` | Every invocation receives a new native UUID and publishes candidate/version, trainer load epoch, target cells and worker incarnations. |
| `miles/ray/placement_group.py:317-359,380-385` | The publisher's UUID/load epoch/version connect to the checksum observation. Every out-of-loop `None` call uses `start_rollout_id - 1`, including restores; `-1` alone is not an initial-publication discriminator. |
| `miles/backends/megatron_utils/actor.py:1207-1215` | Same-version initialization/restoration must keep `rollout_id=None`; a non-None ID rotates the rollout/old-actor snapshots. No caller changed this behavior. |
| `miles/utils/audit_utils/event_analyzer/rules/inference_engine_weight_checksum_coverage.py:21-68` | Existing native coverage connects a publication to exactly one checksum, the same model/version/load epoch, and its exact cell/worker snapshot. |
| `miles/utils/audit_utils/event_analyzer/rules/inference_engine_weight_checksum_consistency.py:18-26` | Existing native consistency compares complete tensor-checksum dictionaries across engines. |

## Consumer changes and passing conditions

- `tests/manual/agent_opd/inspect_qwen35.py::_publication_receipts` is the shared classifier. It requires a complete, uniquely identified, fully published unnamed-actor chain within one load epoch; full native checksum coverage/consistency; matching checksum position/source/time; and nonempty full eligible tensor dictionaries.
- The first out-of-loop receipt is initial only within that complete ordered chain and before actor train attempts. Later `None` publications require the same counter, identical complete native tensor dictionaries, and no intervening unpublished actor attempt. Both changed bytes and unchanged-counter planned publications are checked; no norm-only comparison or checksum exclusions were introduced.
- Planned receipts must have consecutive explicit rollout IDs, their settled ordered actor attempts and counter delta zero or one. A skipped optimizer step still has its planned receipt. It cannot be relabeled as a restore.
- `_publication_checks` records restorations separately, counts only planned deltas and exposes `baseline_publication_id` and `final_planned_publication_id`. Existing same-version monitoring and updated-weight evidence gates remain.
- `probe_qwen35_text_reload.py::_origin` uses the shared classifier and the initial publisher's exact checksum ID, not uniqueness among all `-1`/version0 checksums. It still requires the actual fresh version-zero initial source.
- `qwen_reload.py` required no change: its existing final-origin consumer selects the last validated **planned** row and matches the exact ID/rollout99. Its full decoder identity gate, including derived `gemma_weight` buffers, is unchanged.
- Fixtures use the existing typed native writer. They include two initial restores and post-20/40/60/80/100 restores, skipped optimizer positions, final restore binding, wrong counter/load epoch/model/incarnation, changed complete tensor bytes, duplicate IDs, receipt/checksum ordering and a missing planned skipped-update receipt.

## Local environment

- Working directory: `/data/ycfeng/sota-engine/miles`.
- Python: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, CPython 3.12.13.
- Existing environment: PyTorch 2.8.0+cu128, Transformers 5.19.0, SGLang 0.5.23, psutil 7.2.2. No dependency changes.
- `CUDA_VISIBLE_DEVICES=''`, `HF_HUB_OFFLINE=1`, `PYTHONDONTWRITEBYTECODE=1`; no native GPU engine or model workload was launched.

## Exact verification commands and observations

### Red: planned-count receipt regression

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q --tb=line \
-o addopts='' -p no:cacheprovider \
--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-publication-red \
tests/fast/test_qwen35_monitoring.py::test_same_version_restores_do_not_count_as_planned_updates
```

Observed **1 failed, 0.31s**. Valid typed restores were rejected with `baseline_publication_missing_or_duplicate`, reproducing the reported consumer defect.

### Red: actual origin consumer boundaries

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q --tb=line \
-o addopts='' -p no:cacheprovider \
--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-publication-origin-red \
tests/fast/test_qwen_reload.py::test_baseline_origin_binds_initial_publication_not_later_version_zero_restore \
tests/fast/test_qwen_reload.py::test_final_reload_binds_planned_publication_before_final_restore
```

Observed **2 failed / 1 passed, 1.80s**. Initial origin rejected two valid version0/-1 observations; final reload rejected the valid final restore before loading. The deliberately corrupted final-restore case was already rejected.

### Affected modules after repair

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q --tb=line \
-o addopts='' -p no:cacheprovider \
--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-publication-affected \
tests/fast/test_qwen35_monitoring.py tests/fast/test_qwen_reload.py
```

Observed **152 passed, 101.42s**. This includes the existing ResourceTracker whole-interpreter exit regression and decoder-content/metric boundary checks. Warnings were existing SWIG/JIT/native quantization import/deprecated API and multiprocessing fork warnings; no failed check or ignored ResourceTracker exception occurred. Three additional publication fault variants were added after this whole-module run.

### Final focused green, including additional faults

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q --tb=line \
-o addopts='' -p no:cacheprovider \
--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-publication-final-focused \
tests/fast/test_qwen35_monitoring.py::test_same_version_restores_do_not_count_as_planned_updates \
tests/fast/test_qwen35_monitoring.py::test_malformed_restoration_provenance_cannot_pass \
tests/fast/test_qwen_reload.py::test_baseline_origin_binds_initial_publication_not_later_version_zero_restore \
tests/fast/test_qwen_reload.py::test_final_reload_binds_planned_publication_before_final_restore
```

Observed **16 passed, 2.54s**. Valid evidence produced **100 planned publications, 7 restores, 97 successful / 3 skipped optimizer updates**, with the final planned receipt still rollout99. These are deterministic fixture results, not measured training results. Final reload selected that ID, not the final restore ID. A changed final-restore `gemma_weight` failed before fresh-engine startup. All 12 malformed-provenance variants remained INCOMPLETE.

## Verification limits and remaining work

This slice verifies native typed-record consumption and CPU API boundaries only. No newly repaired real eval-restoration receipt chain or pinned Python/SGLang execution was read through the platform. Parent owns focused pinned receipt validation and actual training/final HF acceptance.

The classifier requires complete readable native receipt files and strictly ordered publication/checksum observations. Missing records, overlapping/ambiguous timestamps, a trainer reload, partial publication or an unpublished attempt do not receive a fallback. Existing records have no explicit restore-purpose field; classification is justified by inspected producer order and exact same-version native content/provenance, not merely by repeated version or `rollout_id=-1`. This does not independently authenticate or reconstruct wholly absent historical records.

Full eligible native checksums retain the existing native coverage limits (declared excluded position buffers). The actual text-HF validator's separate D13 vision/MTP exclusion scope and full decoder byte equality remain unchanged. No final artifact or formal training PASS is claimed here.

## Pinned combined-test fixture lifetime follow-up

### Observed failure and exact cause

Read local `evidence/restore-final-contracts-exp-1107-125038-984696.log`. Lines 16-37 show `test_final_reload_binds_planned_publication_before_final_restore[False]` rejected **before fake Engine startup** with `native_interpreter_not_isolated`. This is the correct production guard for a non-dedicated interpreter, not a new loader/publication defect. The log's original baseline-origin check passed. The parent's reported combined result was 133 PASS / 1 FAIL.

The failure was minimized to one actual predecessor:

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q --tb=line \
-o addopts='' -p no:cacheprovider \
--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-shared-lifetime-red \
tests/fast/backends/megatron_utils/test_score_log_probs.py::test_gloo_tp_cp_and_dp_payload_mapping \
'tests/fast/test_qwen_reload.py::test_final_reload_binds_planned_publication_before_final_restore[False]'
```

Observed **1 PASS / 1 FAIL, 17.36s**, with the identical isolation error. The predecessor at `test_score_log_probs.py:526-527` calls `torch.multiprocessing.spawn(..., nprocs=2, join=True)`.

A separate read-only process-status probe after that predecessor observed: pytest status 0; `multiprocessing.active_children() == []`; exactly one live child, PID **2145616**, status **sleeping**, argv ending `from multiprocessing.resource_tracker import main;main(12)`. This PID equaled the stdlib owner's `_pid`; its `_fd` was 13. Therefore workers were joined, while the normal shared-interpreter ResourceTracker remained alive. Neither an unjoined rank worker nor the fake Engine produced the offending child.

### Fixture-only repair and boundary

Only `tests/fast/test_qwen_reload.py` and this report changed in this follow-up. The fake Engine already had explicit synthetic bytes/logprobs and creates no processes; its fixture now also supplies an explicit empty **simulated process tree** for the duration of the existing native lifecycle context. The context's real configuration/checksum/lifecycle implementation and guard still execute. This fake tree does not claim that the actual pytest interpreter is isolated and never owns or controls earlier tests' children.

`test_native_shutdown_refuses_interpreter_with_preexisting_child` explicitly disables that simulated view and invokes the unchanged production context with the actual psutil module and a live direct child. The real terminal-child, multiprocessing-owner and isolated whole-interpreter ResourceTracker regressions do not use the fake process view. Stage-b 60-second registration is preserved. No production guard, shutdown, ResourceTracker owner, receipt consumer or parent core test changed; no tracker was stopped to make this suite pass.

A new existing-file regression creates a real live sibling while exercising the fake Engine and proves: final verification PASS, fake shutdown called, zero fake-owned children, and the sibling still alive. Before the fixture repair this failed with `native_interpreter_not_isolated` (**1 FAIL, 1.30s**):

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q --tb=line \
-o addopts='' -p no:cacheprovider \
--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-fake-scope-red \
tests/fast/test_qwen_reload.py::test_fake_native_process_tree_does_not_own_prior_pytest_children
```

Two intermediate test-fixture attempts kept the true guard INCOMPLETE but failed its specific assertion: replacing `psutil.Process` while invoking a real owner's `children()` broke the library's class/PID semantics and produced `corrupt_schema`. The final guard regression disables the replacement entirely rather than weakening its assertion or patching production. No debugging instrumentation remains.

### Final green evidence

Repeat of the exact minimized predecessor pair above, changing only basetemp to `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-shared-lifetime-green`: **2 PASS, 16.97s**. The normal stdlib tracker is allowed to remain owned by pytest; only the fake Engine's synthetic process contract changed.

```bash
HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 \
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest -q --tb=line \
-o addopts='' -p no:cacheprovider \
--basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-fake-scope-lifecycle-final \
tests/fast/test_qwen_reload.py::test_fake_native_process_tree_does_not_own_prior_pytest_children \
tests/fast/test_qwen_reload.py::test_native_shutdown_refuses_interpreter_with_preexisting_child \
tests/fast/test_qwen_reload.py::test_final_reload_binds_planned_publication_before_final_restore \
tests/fast/test_qwen_reload.py::test_real_terminal_children_are_reaped_without_touching_live_sibling \
tests/fast/test_qwen_reload.py::test_real_multiprocessing_child_is_joined_with_its_own_handle \
tests/fast/test_qwen_reload.py::test_resource_tracker_owner_and_whole_interpreter_exit
```

Observed **8 PASS, 24.18s**, covering valid/corrupt final restore, unrelated live child protection, the actual dedicated-interpreter refusal, direct-child reaping, multiprocessing join and live/terminal ResourceTracker normal interpreter exit. Existing SWIG/fork warnings remained; no ignored ResourceTracker exception occurred.

No combined full suite was rerun blindly. This uses local Python 3.12.13 and the existing CPU environment, not pinned Python 3.12.16. Parent still owns one affected pinned rerun, preferably the same two-test predecessor pair plus the focused lifecycle selectors. The C/source analysis is separate and was not changed or expanded.
