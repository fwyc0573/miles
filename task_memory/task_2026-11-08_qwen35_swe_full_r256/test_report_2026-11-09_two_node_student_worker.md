## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Repair the monitoring fixture's missing required hardware label; record16 RED /123 integrated GREEN cases and refresh parent callback wiring status. |
| 2026-11-09 | Record T02-D13-MULTINODE-WORKER frontend implementation, RED/GREEN evidence, callback integration requirement and verification limits. |

# Two-node student worker frontend

## Outcome and scope

**PASS for the scoped CPU frontend checks; native capacity and optimizer acceptance remain unverified.** Task ID: `T02-D13-MULTINODE-WORKER`; session: `ses_e41449341ffeyPdv5aSUrf7Wud` (recorded by parent in `plan.md`). Branch: `agent-opd`. No commit, GPU/platform/auth/cloud/network operation, package installation, or edit to parent-owned launch/config/core/task records was performed.

The delegated request selected an isolated A/r256 18-H200 smoke, with two 8-GPU student replicas and one 2-GPU teacher. This frontend keeps the native training driver and `ExecuteTrainConfig` at one node / 8 GPUs. Scientific parameters and the expanded rollout argv/profile are parent-owned; their acceptance remains governed by `requirements.md` D13 and the later explicit delegated selection. This report does not amend those records.

Changed code:

- `tests/manual/agent_opd/run_qwen35_opd.py`: `--student-nodes` at line90; supervised completion at319; node cleanup at331; `_run` at349. Rank0 alone creates the shared run directories, prepares/submits the driver, and publishes `finished.json`. Rank1 waits for the existing bounded run/head rendezvous, prepares its own container, joins the native Ray worker path and remains alive through driver completion. Catchable cancellation publishes failure and preserves existing cleanup. Existing run records and preexisting local directories are not overwritten/deleted on failed initialization.
- `tests/manual/agent_opd/qwen35_pair_worker.py`: selected student node-count owner at92; CLI transport at128; child supervision at225; role wrapper at294. Allocation validates the configured count and existing local GPU shape. Two-node logs/receipts are rank-specific. Only rank0 publishes `student-finished.json`, so a helper exit cannot release the teacher. A reported peer failure cancels the current wrapper's own child using `_stop_child`.
- `tests/fast/test_qwen35_pair_worker.py`: new fixtures/cases at392–710, exercising the actual `_run`, `_run_student`, `_run_teacher`, `_start_ray`, `_check_cluster` and `_wait_file` ordering. GPU/Ray SDK/process-command boundaries are fixtures; two child-cancellation cases use real local CPU subprocesses, and one native cancellation case delivers a real SIGTERM to the test process's installed handler.
- Follow-up: `tests/fast/test_qwen35_monitoring.py:532` adds only explicit `"gpu_tag": "H200"` to `_write_teacher_ready`'s existing config fixture. No production or schema change was needed.

For two-node submission only, the head's `MILES_NODE_EXTERNAL_IP` is removed from job-wide env overrides. Each raylet already inherits its own prepared value. This follows `miles/utils/misc.py:123–132`; forwarding rank0's address would make the two nodes advertise one address. Single-node env behavior and inherited NCCL values remain unchanged.

## Environment and commands

Working directory for every command: `/data/ycfeng/sota-engine/miles`.

Python: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, **3.12.13**; pytest9.1.1, Torch2.11.0, Ray2.58.1, SGLang0.5.23. Existing venv, no conda activation or dependency changes. Pytest temporary files use the existing `/data/ycfeng/tmp/pytest-of-brainpp` placement.

For the commands below, these shell variables denote exact existing paths:

```bash
PY=/data/ycfeng/envs/miles-agent-opd-cpu/bin/python
E=task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence
```

Each RED selection was executed before its corresponding production change:

```bash
$PY -m pytest tests/fast/test_qwen35_pair_worker.py -k two_node_student --junitxml=$E/t02-d13-two-node-role-red.xml -q
$PY -m pytest tests/fast/test_qwen35_pair_worker.py -k two_node_native --junitxml=$E/t02-d13-two-node-native-red.xml -q
$PY -m pytest tests/fast/test_qwen35_pair_worker.py -k 'prepares_each_container or source_rejection or preexisting_directory or propagates_other_replica or peer_absent_teacher' --junitxml=$E/t02-d13-two-node-preflight-supervision-red.xml -q
$PY -m pytest tests/fast/test_qwen35_pair_worker.py -k command_transports_only_ray --junitxml=$E/t02-d13-two-node-transport-red.xml -q
$PY -m pytest tests/fast/test_qwen35_pair_worker.py -k existing_run_does_not_overwrite --junitxml=$E/t02-d13-two-node-existing-run-red.xml -q
$PY -m pytest tests/fast/test_qwen35_pair_worker.py -k allocates_ray_only --junitxml=$E/t02-d13-two-node-address-red.xml -q
```

| Selection | Expected / observed RED | GREEN evidence |
| --- | --- | --- |
| Role ownership and allocation | 4 failures: helper wrote global completion; student count was hardcoded1 | Same command with `role-green.xml`: 4 PASS |
| Actual native worker orchestration | 6 failures at the old one-student-node rejection | Same selection with `native-green.xml`: 6 PASS |
| Per-container preparation, supervision, local ownership | 6 FAIL / 1 PASS: absent callback contract3; destructive local cleanup1; unsupervised waits2; absent teacher readiness was already bounded | Same selection with `preflight-supervision-green.xml`: 7 PASS |
| CLI node transport | 1 FAIL: parsed node count stayed1 | Verified regression below includes PASS |
| Existing global run records | 1 FAIL: failed initialization overwrote existing `training.json` | Verified regression below includes PASS |
| Per-node advertised address | 1 FAIL: head address entered the two-node job env | Verified regression below includes PASS |

The callback REDs establish an absent interface, not a failed actual Megatron patch. The other failures expose actual frontend behavior through the agreed worker/role seams.

Focused intermediate run:

```bash
$PY -m pytest tests/fast/test_qwen35_pair_worker.py --junitxml=$E/t02-d13-two-node-worker-final.xml -q
```

Observed **54 PASS in1.18s** before the final existing-record regression was added. The final combined run includes all **55 worker cases**, including that regression and the address fix.

Final affected regression:

```bash
$PY -m pytest tests/fast/test_qwen35_pair_worker.py tests/fast/test_qwen35_opd_launcher.py tests/fast/test_swe_launcher.py -k 'not native_parser_accepts_sglang_and_custom_mis_flags' --junitxml=$E/t02-d13-two-node-regression-verified.xml -q
```

Expected: every selected frontend/launcher case passes; no native-capacity inference. Observed: **129 PASS / 12 SKIPPED / 1 DESELECTED in9.78s**, exit0. This includes parent-added expanded-profile checks present during execution; this subagent did not edit those tests/profile files.

The initial unfiltered run, recorded in `t02-d13-two-node-regression-first.xml`, had **120 PASS / 12 SKIPPED / 1 FAIL**. The existing CPU SGLang parser does not expose `--sglang-enable-prefill-weight-versions`, an unchanged flag in `_training_args`; the sole final deselection is exactly that test. The twelve existing scheduler/source fixtures require Megatron or an explicitly supplied read-only `MEGATRON_PATH`, absent in this CPU environment. No assertion was weakened and no dependency fallback was added.

Static checks:

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check tests/manual/agent_opd/run_qwen35_opd.py tests/manual/agent_opd/qwen35_pair_worker.py tests/fast/test_qwen35_pair_worker.py
$PY -c 'from pathlib import Path; paths=[Path(p) for p in ("tests/manual/agent_opd/run_qwen35_opd.py", "tests/manual/agent_opd/qwen35_pair_worker.py", "tests/fast/test_qwen35_pair_worker.py")]; [compile(p.read_bytes(), str(p), "exec") for p in paths]; print("COMPILE_PASS", len(paths), "files")'
git diff --check
```

Observed: Ruff0.14.7 **PASS** (existing top-level config deprecation only); compile **PASS,3 files**; diff check **PASS**, no whitespace errors. Compile writes no bytecode.

## Parent integration — source wiring complete

The reusable contract is now available:

```python
native._run(args, prepare_training=_prepare_training, prepare_node=_prepare_node)
```

The parent-owned `run_swe_opd.py:157–199`, inspected during the follow-up, now implements the required contract:

1. `_train` populates `args.student_nodes` from the selected allocation's existing `student.nodes`.
2. `_prepare_node(args, run, rank)` reuses `megatron_scoring_lifetime.prepare_source`; `_prepare_training` no longer patches driver-local source. `_run` calls the callback on every container **before that container joins Ray**; rank0's existing `_check_cluster` cannot pass before both prepared containers join.
3. The one-node archive remains `run/megatron_scoring_lifetime/source`; two nodes use `source/rank-{rank}`. The dependency root remains each container's `/root/Megatron-LM`, not a shared checkout.
4. The callback returns `{"megatron_scoring_lifetime": source_receipt}` when applicable. Native writes a rank-specific node receipt and merges rank0 fields into its existing launch receipt; `_prepare_training` only composes argv/driver receipt.

At the initial delivery, this wiring was pending. The follow-up source inspection now observes it implemented; the tests below run against the live integrated files. Actual pinned-image/source and multi-node GPU adoption remain **unverified**, not certified by source inspection or CPU tests.

## Follow-up — missing monitoring fixture hardware label

The parent's `/data/ycfeng/tmp/qwen35-swe-expanded-cpu-final-20261109.log` reports16 monitoring failures at `qwen35_pair_worker.py:137`, all `KeyError: 'gpu_tag'`. The selected existing tests reproduce exactly that symptom through `_write_teacher_ready -> worker._student_command`.

`gpu_tag` is genuinely consumed, not an unused newly copied role-config field:

- `qwen35_pair_worker._student_command:137` transports it as native `--gpu-type`; `run_qwen35_opd._parser` requires that argument, and `_run` passes it to the existing local `_gpu_devices` identity/count validation.
- `qwen35_pair_worker._allocation:104` also consumes the selected label for existing role-local GPU validation. Existing pair-worker tests exercise both H800 and H200 identities.
- `git show HEAD:tests/manual/agent_opd/qwen35_pair_worker.py` already contains both consumers. They were not introduced by the two-node patch. Removing the CLI field would break the supported native parser/qualification contract; substituting a fallback would silently weaken it.

The fixture called the actual command producer without supplying this existing required config input. The only follow-up code edit supplies `H200` explicitly as synthetic fixture data at `test_qwen35_monitoring.py:532`. No consumer, hardware fallback, accepted schema, monitoring assertion, topology, registration or source hook changed.

Commands use the same working directory, Python and `E` evidence prefix defined above:

```bash
$PY -m pytest tests/fast/test_qwen35_monitoring.py -k 'native_nested_teacher_response or teacher_prefix_token_corruption or teacher_faults_are_incomplete or teacher_masked_corruption' --junitxml=$E/t02-d13-two-node-monitoring-fixture-red.xml -q
$PY -m pytest tests/fast/test_qwen35_monitoring.py tests/fast/test_qwen35_pair_worker.py --junitxml=$E/t02-d13-two-node-monitoring-pair-integrated-green.xml -q
```

| Check | Expected | Observed |
| --- | --- | --- |
| Before fixture edit | Reproduce the16 reported `gpu_tag` failures | **16 FAIL /52 DESELECTED in3.80s**, exit1; every failure is the reported KeyError |
| After fixture edit, live integrated files | All monitoring and pair-worker cases pass, including the original16 | **123 PASS in48.79s**, exit0:68 monitoring +55 pair-worker; no skips or deselections |

Additional static checks:

```bash
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check tests/fast/test_qwen35_monitoring.py tests/manual/agent_opd/qwen35_pair_worker.py
/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check tests/manual/agent_opd/qwen35_pair_worker.py
$PY -c 'from pathlib import Path; paths=[Path(p) for p in ("tests/fast/test_qwen35_monitoring.py", "tests/manual/agent_opd/qwen35_pair_worker.py")]; [compile(p.read_bytes(), str(p), "exec") for p in paths]; print("COMPILE_PASS", len(paths), "files")'
git diff --check -- tests/fast/test_qwen35_monitoring.py tests/manual/agent_opd/qwen35_pair_worker.py task_memory/task_2026-11-08_qwen35_swe_full_r256/test_report_2026-11-09_two_node_student_worker.md
```

Observed: compile **PASS,2 files**; scoped diff check **PASS**; pair-worker Ruff **PASS**. Ruff over both files reports one **preexisting B008 at monitoring line114** (`positions=(None, *range(100))`), exit1. `git diff -- tests/fast/test_qwen35_monitoring.py` confirms only line532 changed; no new lint finding is reported. The unrelated default-expression lint issue is retained, not fixed or suppressed in this phase.

The known `test_native_parser_accepts_sglang_and_custom_mis_flags` limitation remains outside this follow-up. It was neither edited nor included in these two-file commands. The parent retains the installed SGLang0.5.23 versus intended image0.5.24 limitation and actual-image verification before launch. No GPU/platform/SSH/cloud/network operation, package change or commit was performed.

## Lifecycle bounds and limits

- Run/head/teacher readiness waits use the existing `startup_timeout` and `_wait_file`. Missing rendezvous fixtures finish at the configured3-second test deadline, with no driver submission.
- Catchable head failure/cancellation publishes native completion in `finally`. The helper observes failure at the next poll; wrapper supervision handles head-child failure even before native directories/completion exist, and uses the existing child SIGTERM/60-second SIGKILL cleanup. Both directions of real CPU child cancellation preserve rank0 completion ownership.
- Healthy training has no newly invented duration limit. The helper's running wait is supervised by the existing role wrapper; once the driver has completed, helper drain is bounded by the existing startup budget. No retry, detached process, independent cluster builder or second launcher was added.
- An uncatchable death of the **entire head wrapper/pod**, or loss of the shared lifecycle filesystem, cannot be detected from local peer files alone. Correct cancellation then depends on existing RJob critical-task/platform teardown. Parent must verify this native lifecycle; no platform-level proof or new crash detector is claimed.
- Per-container callback tests exercise the seam/order and isolated archive paths, not a real pinned-image/source qualification. No native Ray two-node cluster, eight running TP2 engines, long-context acquisition,231/256 threshold, actual scoring/backward, optimizer ACK, two bank uses, teacher lifetime, or GPU capacity was measured.

The scoped self-check and parent-record correction are in `evidence/t02-d13-two-node-checkpoint.md`. Ticket02 remains in progress; formal cells remain gated on actual runtime acceptance.
