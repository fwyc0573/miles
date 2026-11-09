## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record the isolated resource-preparation slice for parent task D33. |
| 2026-11-09 | Record the independently configured 128K context, 112K prompt and 16K response follow-up. |

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
