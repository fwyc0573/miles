## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Prepare the formal A/B configuration and verify dry-run resource and native argument output; profile integration remains pending. |

# Formal H800 configuration

## Scope and state

`formal_config.json` uses the merged launcher from `55fba827`, the accepted D34 source manifest, and the accepted H800 eight-engine topology. It is a preparation artifact, not a launch receipt. Ticket02 CPU implementation and Ticket03 integration still precede submission.

Both cells request 32 student/rollout GPUs plus a four-GPU teacher. The student, rollout geometry, image, ports, timeouts and numerical configuration match the accepted capacity configuration. B uses the explicitly permitted read-only Qwen3.5-35B-A3B model source; its native H800 teacher memory and throughput remain unverified. The resource research subtask remains pending and may refine B before submission.

Intentional differences from the capacity run are: `formal`, 200 successful updates, `full` with one bank use, the parent branch's 32×8 loss-masked source interface, current 112K audit manifest, parent paths and GPU policy, separate formal output root, and no post-save hook. `save_interval=null` disables saving; the shared launcher still emits an unused HF destination. No evaluation configuration is supplied.

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
- PASS: `shlex.split` of both native argument outputs confirms each of 21 frozen valued flags occurs exactly once: 200 rollouts/successful updates, formal/full, one bank use, 256 slots, minimum fraction0.9, acquisition1800, source loss_masked/32/8, seq/context131072, prompt114688, response16384, TP4, rollout GPUs32, n1 and lr2e-6.
- PASS: neither output contains `--save-interval`, `--custom-megatron-post-save-hook-path` or `--swe-evaluation-configuration`.

## Remaining acceptance

Profile configuration and native consumption will be verified after Ticket03 integration. These dry-runs do not construct a full native worker, mount or rescan data, launch GPU work, or establish B's memory/throughput. A's first successful formal update supplies native per-turn/profile acceptance and the required inspection before B admission (D16); auxiliary profile failure is reported without becoming a training hard gate.
