## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Enable the verified Ticket03 profile path and confirm both final A/B launch command/config outputs; preserve native first-update acceptance. |
| 2026-11-10 | Correct the inherited formal bank_uses validation field after native-contract RED/GREEN; confirm full still uses200 distinct banks once each and record B teacher feasibility limits. |
| 2026-11-10 | Prepare the formal A/B configuration and verify dry-run resource and native argument output; profile integration remains pending. |

# Formal H800 configuration

## Scope and state

`formal_config.json` uses the merged launcher from `55fba827` with Ticket02`6129aefe`and Ticket03`15186817`, the accepted D34 source manifest, and the accepted H800 eight-engine topology. Ticket02 CPU implementation and Ticket03 integration now have recorded readiness. This configuration is a preparation artifact, not a launch receipt.

Both cells request 32 student/rollout GPUs plus a four-GPU teacher. The student, rollout geometry, image, ports, timeouts and numerical configuration match the accepted capacity configuration. B uses the explicitly permitted read-only Qwen3.5-35B-A3B model source. Completed read-only research `profile-formal-config-map-20261110` supports TP4 as a feasible initial layout: retained model assets total71,903,878,016 bytes (66.97GiB), or16.74GiB/rank atTP4; TP2/EP1 was previously exercised at128K on H200. Native H800 TP4/EP1 load time, peak memory and throughput remain unverified. Existing TP4 serving tests useEP4, so they do not directly validate this teacher path. Keep TP4/EP1 without adding a new EP launcher option. B admission follows A's real first successful update and inspection, with fresh resource admission; completion of A's200 updates is not required (specS8).

Intentional differences from the capacity run are: `formal`, 200 successful updates, `full` with one effective bank use, the parent branch's 32×8 loss-masked source interface, current 112K audit manifest, parent paths and GPU policy, separate formal output root, and no post-save hook. The shared formal validator requires the config field`bank_uses=50`; `ReplaySchedule` ignores that field for`full` and uses exactly one successful visit per bank. `save_interval=null` disables saving; the shared launcher still emits an unused HF destination. No evaluation configuration is supplied.

The SGLang YAML is reused directly from the consolidated preparation task: two colocated TP4 engines and six dedicated TP4 engines. The existing personal policy has an explicit null ceiling and an expired temporary window. Submission must still inspect the live inventory and bind a fresh admission receipt. No admission or platform operation occurred in this check.

## Commands and environment

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`.
Python: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python` (3.12.13).
Use the following commands for each `PAIR` in `A`, `B`:

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.submit_swe_opd \
  --config task_memory/task_2026-11-08_qwen35_full_kl_nll/formal_config.json \
  --pair "$PAIR" --protocol full \
  --receipt "/data/ycfeng/tmp/agent-opd-image/formal-${PAIR}-dry-run-unused.json" --dry-run
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.run_swe_opd \
  --config task_memory/task_2026-11-08_qwen35_full_kl_nll/formal_config.json \
  --pair "$PAIR" --protocol full --role train --dry-run
```

Retained command outputs: `/data/ycfeng/tmp/agent-opd-image/formal-{A,B}-{submit_swe_opd,run_swe_opd}-20261110.txt`.

## Observed results

- PASS: all four commands exit 0. Both submission objects have `submitted=false`, `requested_gpus=36`, four eight-GPU student replicas and one four-GPU teacher replica.
- PASS: source module SHA256 values match the two actual pinned local Steptron files; the A/B student configuration objects are equal.
- Initial argument-only PASS: `shlex.split` of both outputs confirmed21 valued flags, including`bank_uses=1`. That check did not execute`training_protocol` and missed the inherited formal guard. The initial outputs are retained as historical pre-correction evidence, not final readiness.
- PASS: neither output contains `--save-interval`, `--custom-megatron-post-save-hook-path` or `--swe-evaluation-configuration`.

### Formal-contract correction

The primary inspected`swe_replay.py:423–427` and reproduced the exact error for both A and B with the real`training_protocol`, using the existing CPU`_typed_swe_config`→`OrchestratorConfig`→`compute_custom_function_config` fixture path:

```text
bank_uses=1 → ValueError: Formal SWE runs require the frozen budget; shorter runs must be explicitly smoke
bank_uses=50 → driver.budget=200
```

The same Python3.12.13 invocation then executed real`ReplaySchedule('full', bank_uses=50, updates=200)` for200 successful commits. For both pairs, all `(bank,visit)` positions were exactly`[(0,1),...,(199,1)]`: no replay was introduced. The fixture validates the real post-parse configuration/driver path; it is not a GPU Megatron parser execution. `formal_config.json` was corrected to50, preserving full-mode semantics. The known CPU`deep_ep is not installed` warning did not affect these checks.

## Remaining acceptance

Ticket03`15186817`records201 affected CPU tests PASS, including real native custom-schema/view propagation and profile failure isolation. The final explicit profile object enables the path with trend_window10, baseline_updates10 and baseline_turns8. All four dry-run commands above were rerun after enabling it; each exited0. Current outputs are`/data/ycfeng/tmp/agent-opd-image/formal-profile-{A,B}-submission-20261110.json`and`formal-profile-{A,B}-native-argv-20261110.txt`. Both submissions remain`submitted=false`,36GPUs. `shlex.split`checks confirmed each of13 valued flags once (three profile lengths, bank_uses50, full, successful budget200, num_rollout200, seq/context131072, prompt114688, response16384, source32×8), exactly one`--swe-profile-enabled`, and no save-interval/post-save-hook/evaluation flags. The CPU dry-runs retain the known optional`deep_ep`warning.

These checks do not construct a full native worker, mount or rescan data, launch GPU work, or establish B's memory/throughput. A's first successful formal update supplies native per-turn/profile acceptance and the required inspection before B admission (D16); auxiliary profile failure is reported without becoming a training hard gate. Phase reviews and final admission are recorded separately; neither a configuration nor test counts alone establish native acceptance.

## Pre-formal sample lifecycle check

The`before-steptron-run`inspection reuses existing boundaries rather than adding instrumentation:

- `qwen_alignment._sample_attempt`/`generate`: source UID/group, sample and rollout IDs, lineage, request stage, timing, terminal status, exception type and generated weight versions. The native Ray worker logs and teacher endpoint provide worker attribution. The whole student HTTP retry chain, including retry sleep, is bounded by3600 seconds.
- `swe_replay.acquire_bank`: stable bank/slot/source identity, an absolute1800-second deadline, per-slot completion/invalid records and final membership/missing/pending sets. Invalid and pending slots partition missing slots; pending slots are not counted again as additional missing samples. Teacher stage records carry cell/attempt/bank/slot, model source/endpoint, timing and exception text. Successful teacher token alignment is retained in sample metadata.
- Sample exceptions and cancellation remain isolated to private sample copies. At sealing, outstanding tasks are cancelled and cannot publish into this or the next bank, including a coroutine that suppresses cancellation. Existing D6 minimum231 and native D7 handling remain authoritative. Evidence sink errors are soft and do not turn healthy collection into failure.
- Retry attempts remain separate from consumed slots. Native successful-update counters remain separate from skipped optimizer attempts. The profile acceptance will use actual bank membership, not assume256 valid observations on every update.

Exact local check (same repository and Python environment as above):

```bash
env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -q tests/fast/test_qwen35_sample_lifecycle.py::test_generation_deadline_cancels_and_drains_native_request tests/fast/test_qwen35_sample_lifecycle.py::test_repeated_503_responses_share_one_generation_deadline tests/fast/test_qwen35_sample_lifecycle.py::test_failed_attempt_does_not_prevent_a_later_successful_sample tests/fast/test_swe_replay.py::test_hung_late_invalid_collection_is_finite_and_slot_ordered tests/fast/test_swe_replay.py::test_acquisition_evidence_failure_is_soft tests/fast/test_swe_replay.py::test_teacher_request_and_validation_stage_receipts -o cache_dir=/data/ycfeng/tmp/agent-opd-image/formal-lifecycle-pytest --basetemp=/data/ycfeng/tmp/agent-opd-image/formal-lifecycle-tests
```

Observed: **16 passed in2.63s**,18 existing dependency/deprecation warnings. Assertions cover request cancellation/draining, repeated503 sharing one deadline, failure or timeout followed by a successful sample, late and invalid slot accounting, teacher success/error/cancelled terminal receipts, and sink failure isolation. Network/GPU calls are mocked; real asyncio deadlines, scheduling and lifecycle functions execute. This verifies preparation only. Formal failure counts and post-run sample RCA still depend on the actual jobs.
