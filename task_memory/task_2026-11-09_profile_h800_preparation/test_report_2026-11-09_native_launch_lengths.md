## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record explicit native context/prompt/response launch validation and the pending input-side integration. |

# Native Launch Length Test Report

Task ID: `profile-length-launcher-20261109`.

## Environment and Scope

- Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-h800-capacity`; branch `agent-opd-h800-capacity`, follow-up based on accepted admission commit `1ae93261`.
- Interpreter: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`; Python 3.12.13, pytest 9.1.1, Linux; repository `pyproject.toml`. No Python/conda environment changes.
- Temporary test files: `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`.
- Code owner changed: `tests/manual/agent_opd/run_swe_opd.py`.
- Existing tests changed: `tests/fast/test_swe_launcher.py`, `tests/fast/test_swe_capacity.py`, `tests/fast/test_swe_native_gradients.py`, `tests/fast/test_megatron_scoring_lifetime.py`.
- No archived JSON config, parent input/checker/audit, historical Qwen35 preparer/launcher constant, main checkout, platform or RJob operation changed.

## Config Contract and Existing Owners

The native fields already exist in `miles/utils/args/configs/rollout.py`: `rollout_max_prompt_len` is the native prompt budget; `rollout_max_response_len` maps to SGLang `max_tokens`; `rollout_max_context_len` is the native context budget. The SWE launch JSON previously had only `context_tokens`, and the launcher incorrectly used it as the response limit. No alternative launch JSON owner was found.

The existing `_config` boundary now requires all three fields to be explicit positive JSON integers (not null, boolean or fractional values), and requires `prompt_tokens + response_tokens <= context_tokens`. Missing fields fail; no defaults or extra CLI knobs were added. `_training_args` directly consumes the validated inputs without repeating validation.

| Launch input | Requested value | Native emitted flag(s) | Observed value |
| --- | --- | --- | --- |
| `context_tokens` | 131072 | `--seq-length`, `--sglang-context-length`, `--rollout-max-context-len`, existing `--swe-context-tokens` | 131072 for each, exactly once |
| `prompt_tokens` | 114688 | `--rollout-max-prompt-len` | 114688, exactly once |
| `response_tokens` | 16384 | `--rollout-max-response-len` | 16384, exactly once |

The three context values preserve the native training sequence limit and rollout/SGLang context. The prompt and completion budgets are independent config inputs, not aliases for the context size. There is no remaining `--rollout-max-response-len 131072` override in the emitted argv.

## Exact Commands and Observed Results

Both pytest commands below ran from the working directory above. The first command was run once before implementation and once after it.

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_launcher.py -q -p no:cacheprovider
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m pytest tests/fast/test_swe_capacity.py tests/fast/test_swe_native_gradients.py tests/fast/test_megatron_scoring_lifetime.py -q -p no:cacheprovider -k 'combined_native_hook_registration_uses_real_generated_arguments or combined_native_hook_cli_registration_from_generated_argv or configuration_uses_existing_flag_carrier_without_recipe_edits or combined_cli_typed_before_log_prob_installs_without_swe_attempt or contrast_adds_only_observation_arguments'
git diff --check
```

| Run | Expected passing condition | Observed result | Verdict |
| --- | --- | --- | --- |
| Original launcher baseline | Existing unrelated launcher behaviors pass before the new contract | 29 passed, 20 warnings, 4.76 s | PASS |
| Updated launcher file | Original behaviors and new explicit length/argv/dry-run checks all pass | 53 passed, 20 warnings, 14.28 s | PASS |
| Directly affected argv/hook fixtures | Explicit prompt/response limits preserve existing CLI registration, probe configuration immutability and scoring-only contrasts | 7 passed, 40 deselected, 20 warnings, 3.58 s | PASS |
| Whitespace | No diff errors | Exit 0, no output | PASS |

The launcher file stays below the repository's 30-second implicit fast-test budget in this observed run. No broad suite or GPU test was run.

Warnings match the baseline: SWIG missing `__module__`, deprecated `datetime.utcnow` and TorchScript `script_method`, and CPU-only AWQ/GGUF availability warnings. A `swigvarlink` deprecation warning also appeared at interpreter shutdown. No warning was suppressed and no test failure remains.

## Decisive Test Evidence

- `test_length_config_requires_explicit_positive_integers`: 15 combinations (three fields × null/zero/negative/boolean/fractional value) raise the expected field-specific ValueError.
- `test_length_config_never_defaults_missing_limits`: all three omitted fields raise the expected ValueError rather than inheriting defaults.
- `test_prompt_and_response_budgets_must_fit_context`: 114688 + 16384 = 131072 accepts; increasing prompt by one rejects.
- `test_native_argv_separates_prompt_response_and_context_limits`: all four A/B × full/r256 recipes emit the table above; prompt/response/context/SGLang flags are accepted by the existing native `AllConfig` parser. `--seq-length` is also explicitly present with its required backend value; a full GPU/Megatron parse was not claimed.
- `test_worker_dry_run_emits_explicit_limits_without_native_execution`: an actual unmocked subprocess invokes the existing module with `--config <pytest fixture config path> --pair A --protocol full --role student --dry-run`; the fixture writes explicit limits and relocates local paths without editing the archived recipe. The subprocess exits 0, emits prompt 114688/response 16384 once, and no context-sized response override. This case took 9.45 s.
- Existing archive-based test fixtures now inject their explicit intended budgets only in memory. No test rewrites archived config files or changes the old 100-update preparer's 8192 response-token constants.

## Pending Integration and Verification Limits

- Local `_config` / `--dry-run` render launch arguments without constructing native SWE inputs; no source-constructor monkeypatch, fallback or bypass was used.
- This isolated branch still contains `swe_inputs.py:177–178`, which requires `rollout_max_response_len >= rollout_max_context_len`. The input/checker/audit owner is another agent. Full construction and generation with the new 16K cap require those changes to be integrated; this report makes no claim that the old constructor accepts the new argv.
- The named parent worktree had no `tests/manual/agent_opd/run_swe_opd.py` at the inspected path, so parent dry-run behavior was not verified or inferred. If its dry-run constructs inputs, that remains part of the primary's integration validation.
- The primary creates the new H800 launch configuration, verifies real business outputs and handles merge/submission under the parent task gates. No platform calls, GPU execution or parent Ticket02/03 integration occurred here.
- Concurrent unowned multi-node changes in `run_qwen35_opd.py` and `qwen35_pair_worker.py` were observed before staging, preserved and excluded from this slice's commit. Their inspected diff does not change the historical length constants or the tested length argv path; this report does not validate that separate lifecycle change.
