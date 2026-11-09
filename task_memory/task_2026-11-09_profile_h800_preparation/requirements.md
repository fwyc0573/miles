## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record verified node-local NCCL correction and distinguish D34 H800 readiness from upstream's frozen D11 capacity acceptance. |
| 2026-11-09 | Record session-owned smoke and temporary cloud-artifact cleanup authorization. |
| 2026-11-09 | Record the isolated resource-preparation slice for parent task D33. |
| 2026-11-09 | Record the independently configured 128K context, 112K prompt and 16K response follow-up. |
| 2026-11-09 | Own the failed upstream synchronization prerequisite, D34 source-consumer correction and in-place native receipts before H800 capacity execution. |

# Requirements

## [Original Request] 2026-11-09

> 确认，允许在h800上继续执行（无gpu数量限制）

Parent task: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image/task_memory/task_2026-11-08_qwen35_full_kl_nll/requirements.md`, decision D33. Its source-input, scientific, formal-run and D1/D22 merge gates remain authoritative.

This worktree starts from upstream `c52991ac` to isolate H800 resource preparation from the active upstream H200 capacity job. It does not merge upstream into `agent-opd-image` or implement parent Ticket02/03.

The existing admission mechanism must represent an explicitly unlimited GPU allocation without inventing a large integer ceiling. Existing finite policies retain their behavior. All submissions still use personal Python RJobBackend, H800/codesign, local source mounts and personal cloud output paths. Other tasks' jobs remain untouched.

## [Original Request] Launcher Length Follow-up, 2026-11-09

> User NEW steering: Qwen3.5 train global_seq_length131072, rollout max_seq_len131072, prompt budget114688, completion max_tokens16384.
>
> Need wire existing native rollout_max_prompt_len and rollout_max_response_len from explicit launch config input, retain seq_length/sglang_context_length/rollout_max_context_len131072. Prefer input keys prompt_tokens and response_tokens alongside existing context_tokens; inspect for existing equivalent owner first. Validate positive limits/context compatibility once at config boundary, and require explicit new fields for updated recipes rather than invent literal defaults or duplicate knobs.
>
> Do not mutate archived configs or upstream main checkout; adapt affected test fixtures to explicitly represent their intended limits. Prove _training_args/native argv carries112K/16K independently of128K and contains no remaining context-sized response override. Existing Qwen35 100-update preparer is a separate historical workflow; do not change its constants without concrete caller need.
>
> If existing --dry-run path calls input constructor in parent branch, report pending integration; no runtime monkeypatch. Run affected existing CPU tests, record exact results/limits; no platform calls. Commit only your scoped files/docs (also include preparation requirements.md/plan.md created by primary in prior task; they belong to this scope).

Task ID: `profile-length-launcher-20261109`. The previous admission commit `1ae93261` is accepted for later review, not permission for parent integration or GPU operations.

### Explicit Scope and Config Contract

- Own `tests/manual/agent_opd/run_swe_opd.py`, directly affected existing launcher/argv test fixtures, and this preparation task's records. The primary owns the new H800 config and merge/submission.
- Do not copy or edit `swe_inputs.py`, its checker/audit, parent Ticket02/03, archived JSON configs, or the historical Qwen35 preparer/launcher constants.
- The launch JSON owns required positive integer `context_tokens`, `prompt_tokens`, and `response_tokens`. Their prompt/response sum must not exceed context. No missing-field defaults or alternative knobs are authorized.
- Native rollout prompt/response flags consume the corresponding explicit input values. Native training, SGLang and rollout context flags continue to consume `context_tokens`.

## Prerequisite repair and execution slice

The upstream attempt `exp-1109-144110-764758` failed before generation during initial weight publication. Within the parent's continuing D33/D34 execution authorization, this isolated branch owns the minimal mixed-engine session correction and the old native SWE source's prompt/completion budget consumer. Neither change implements the parent's per-turn profile hooks or merges upstream into the parent.

The prepared A/r256 capacity configuration requests36 H800/codesign: one8-GPU TP4/DP2 trainer colocated with twoTP4 engines, three additional8-GPU nodes providing six dedicatedTP4 engines, and a separate4-GPU TP4 teacher. Its acceptance remains at least231 of256 within1800 seconds, two successful optimizer ACKs, second-student scoring and two uses of the same bank. The original source sequence, mask policy, models, seeds and loss parameters remain the upstream prerequisite's contract; parent formal32×8 interleaving and200-update runs are separate gated work.

### Native retry coordination and contract boundary

As of2026-11-09T11:19Z, upstream `agent-opd` at`23b29f66` has approval for one original18-H200 session-repair rerun but no new submitted job or capacity acceptance. Its recorded source-length contract has not adopted parent D34. This task's36-H800 run verifies the parent's explicitly approved H800 and128K/112K/16K configuration; it is not acceptance of the unchanged upstream D11 contract. The two owners retain separate jobs and evidence. Neither task may infer the other's acceptance from submission, CPU tests or a result under different input budgets. Parent D1/D22 remain blocked until the upstream owner records acceptance under its authoritative contract; any later contract reconciliation requires an explicit recorded decision, not a relabeled receipt.

The first H800 failure's confirmed code defect is head-inherited NCCL environment serialization. Commit`cf98293a` removes that override while retaining node-local platform values and explicit existing deterministic/config controls. The next native attempt changes only the output identity/path fields in the H800 config; topology, source inputs, length budgets, seeds, loss, teacher envelope and native timeouts remain unchanged. All auxiliary environment/evidence checks are soft-only; missing inspection data is reported as unverified and cannot stop healthy training.

D25 is enforced by reading original posttrain sources in place. The existing genuine native baseline/visual/filter APIs must produce fresh receipts for those exact paths and metadata; existing receipts for copied sources must not be relabeled. D10 is enforced with the existing `save_interval=None` mechanism; no HF or evaluation is requested. The scoring observer remains soft-only, and all cloud writes remain under `/mnt/codesign-exp/ycfeng`.

## [Original Request] Cloud cleanup, 2026-11-09

> 及时清理本session中smoke、临时产物等残留在 codesign oss上的大文件，施放空间

Remove obsolete outputs of this session's terminal smoke and temporary jobs after retaining the evidence needed for diagnosis and acceptance. Verify exact ownership, terminal status, paths, and retained evidence first. Do not delete source models, source datasets, formal/evaluation artifacts, live-job inputs or outputs, another task's files, or the shared volume trash. Record deleted paths and measured logical bytes; do not equate unlinking with verified physical OSS reclamation.
