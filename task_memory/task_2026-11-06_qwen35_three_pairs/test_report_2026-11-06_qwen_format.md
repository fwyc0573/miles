## Modification History

| Date | Change |
| --- | --- |
| 2026-11-06 | Revalidate preserve_thinking=True as the latest default across user boundaries; preserve prior native-mode checks as override evidence and retain completion-only loss. |
| 2026-11-06 | Verify the authoritative last-real-user rule on three boundary cases and four actual histories; record completion-only mask and colocated transport source evidence. |
| 2026-11-06 | Record that existing preserve_thinking=false still retains later history and cannot satisfy the new complete keep/drop control alone. |
| 2026-11-06 | Verify Miles' existing Qwen3.5 fixed template retains historical reasoning under D4. |
| 2026-11-06 | Verify four real local GLM history snapshots against the Qwen template and distinguish synthetic history-policy evidence. |

# Qwen input-format verification

## Result and scope

PASS for the scoped CPU format checks: four raw histories reproduce the expected tool-argument type failure; the existing Miles normalization makes all four render and tokenize successfully. Two constructed multi-user cases verify the published template's old-reasoning omission behavior. This is not full-corpus validation, actual OSS asset verification, student generation, teacher scoring, loss-mask validation or train/inference numerical qualification.

The source consists of historical local snapshots, not a fresh cloud read. Public template/config files were read from official Hugging Face model repositories. No weights were loaded and no GPU jobs were submitted. Business source text and token arrays are not copied into this report or its retained JSON evidence.

Current policy: latest D4 selects `preserve_thinking=True` on Miles' fixed Qwen template by default, including across later real user messages. D6 remains completion-only loss. Earlier false-mode results below describe the previous default and remain useful override/control evidence; they are not the current trajectory-prefix setting.

## Inputs and environment

- Repository: `/data/ycfeng/sota-engine/miles`, branch `agent-opd`; code at `9df78a87` before this documentation update.
- Python: `/data/ycfeng/envs/openmopd-py312/bin/python`, version `3.12.13`.
- Libraries: `transformers 4.57.6`, `tokenizers 0.22.2`, `jinja2 3.1.6`.
- Local source: `/data/ycfeng/tmp/swe-model-pairs-20261103/source-turns.json`; SHA256 `212427f96d8c4b6f164939c3d2e6b7f7676ada8d559c024041623887c6984337`.
- Local tokenizer: `/data/ycfeng/tmp/swe-model-pairs-20261103/Qwen/Qwen3.5-4B`; loaded with `local_files_only=True`. The loaded backend's `pre_tokenizer` equals the published JSON; no automatic regex change was observed.
- Fresh public small-file cache: `/data/ycfeng/tmp/qwen35-three-pairs-format-kh3g82mp`.
- Actual normalization: [Miles normalize_tool_arguments](/data/ycfeng/sota-engine/miles/examples/agentic_opd/glm_turns.py:25), imported through `runpy` without changing production code.

The four official revisions checked are:

| Model | Pinned template |
| --- | --- |
| Qwen3.5-4B | [851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a](https://huggingface.co/Qwen/Qwen3.5-4B/blob/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a/chat_template.jinja) |
| Qwen3.5-27B | [fc05daec18b0a78c049392ed2e771dde82bdf654](https://huggingface.co/Qwen/Qwen3.5-27B/blob/fc05daec18b0a78c049392ed2e771dde82bdf654/chat_template.jinja) |
| Qwen3.5-35B-A3B | [59d61f3ce65a6d9863b86d2e96597125219dc754](https://huggingface.co/Qwen/Qwen3.5-35B-A3B/blob/59d61f3ce65a6d9863b86d2e96597125219dc754/chat_template.jinja) |
| Qwen3.5-397B-A17B | [8472618112abcbd45acbcdc58436aff4233c23f7](https://huggingface.co/Qwen/Qwen3.5-397B-A17B/blob/8472618112abcbd45acbcdc58436aff4233c23f7/chat_template.jinja) |

All four downloaded templates are 7,756 bytes with SHA256 `a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715`. Their downloaded `tokenizer_config.json` files are 16,710 bytes with SHA256 `316230d6a809701f4db5ea8f8fc862bc3a6f3229c937c174e674ff3ca0a64ac8`.

All four official `tokenizer.json` LFS metadata records identify a 12,807,982-byte object with SHA256 `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42`. The existing local tokenizer's actual bytes match this digest. Four new tokenizer payloads were not downloaded. Actual OSS copies and engine tokenizer settings remain unverified; shared model-family labels alone are insufficient.

## Command and retained evidence

The one-off inspection script resides in local temporary storage, not in the training path. SHA256: `d731a725fbcf8983e87a845a25e96634f95d0bb37a7c56b122a8df650006a0cc`.

```sh
timeout 60s /data/ycfeng/envs/openmopd-py312/bin/python /data/ycfeng/tmp/qwen35-three-pairs-format-kh3g82mp/verify_format.py
```

Exit status: `0`. Sanitized results, source identities, public metadata and per-sample checks are retained in [qwen-format-cpu.json](evidence/qwen-format-cpu.json). The temporary output was `/data/ycfeng/tmp/qwen35-three-pairs-format-kh3g82mp/format-results.json`.

Documentation verification: `git diff --check` passed. An inline Python check passed for five maintained documents, 25 local links, D1–D3, the original user question and four retained result rows. The `check-progress` self-check in progress.md found no drift; the interview remains incomplete and no runtime acceptance is implied.

## Expected and observed results

| Check | Expected | Observed | Status |
| --- | --- | --- | --- |
| Raw GLM tool arguments | JSON strings are not accepted by the Qwen template's mapping iteration. | 4/4 fail with `TypeError: Can only get item pairs from a mapping.` | PASS: failure reproduced |
| Existing Miles normalization | Parse JSON strings into objects on a copy; retain parameter values. | 389 string-valued calls across the four histories normalize successfully; parameter objects match JSON values; original histories are unchanged. Counts overlap across historical contexts and are not unique-event counts. | PASS |
| Native Qwen rendering | Normalized structured roles, reasoning and tools render without an exception. | 4/4 histories render. | PASS |
| Token boundary preparation | `apply_chat_template(tokenize=True)` equals render followed by `encode(add_special_tokens=False)`. | All four histories match in both thinking and no-thinking generation modes. | PASS |
| Generation suffix | Thinking: `<\|im_start\|>assistant\n<think>\n`; no-thinking: the same assistant start with an empty closed thinking block. | Both expected suffixes match for all four histories. | PASS |
| Actual history reasoning | All nonempty assistant reasoning is retained for these single-user histories. | 83, 59, 57 and 56 reasoning spans, respectively, appear in rendered text. These are overlapping history counts. | PASS |
| Constructed multi-user case | Earlier reasoning is omitted; reasoning after the latest real user request remains. | Default and `clear_thinking=False` both omit the early marker and keep the late marker. | PASS |
| Official tokenizer assets | Public template/config bytes agree; actual local tokenizer digest matches public metadata. | All four match the hashes above. | PASS, public assets only |

The raw failure is an expected negative control, not an unresolved production regression. It demonstrates why a source normalization step is required. Neither this error nor its repair establishes a model architecture gap.

| Historical target category | History messages | Real user messages | JSON-string argument calls | Prompt tokens, thinking | Prompt tokens, no-thinking |
| --- | ---: | ---: | ---: | ---: | ---: |
| control_and_thinking | 242 | 1 | 128 | 86,669 | 86,671 |
| control_only | 181 | 1 | 90 | 97,254 | 97,256 |
| thinking_only | 175 | 1 | 87 | 95,907 | 95,909 |
| neither | 169 | 1 | 84 | 93,256 | 93,258 |

These categories describe historical targets; they are not labels of future student outputs. All four histories end in a tool response and have three declared tools. A separate local inspection of their system content found none of the checked markers (`<|assistant|>`, `<arg_key>`, `<arg_value>`, `[gMASK]`, `<sop>`, `<|im_start|>`, `<tool_call>`); this is a narrow marker check, not an exhaustive semantic-content audit.

## Interpretation and remaining work

1. Normalize the structured message copy and render it with the actual Qwen template in the existing Miles preparation path. There is no need to overwrite or offline-convert the full original corpus. Do not reuse a GLM-rendered prompt or GLM token IDs.
2. The published Qwen template omits reasoning before the last real user query. `clear_thinking=False` is not a supported override in this template. Latest D4 selects preservation across user boundaries instead: use Miles' existing fixed template with `preserve_thinking=True`, retaining the existing parameter as user control. The earlier native false-mode selection is superseded as the default; no all-history keep/drop transformation is needed.
3. The observed 86,669–97,254-token prompts are not a feasible-run selection. Recount the actual selected population using Qwen, reserve response tokens, measure reasoning omissions and decide lengths before launch. Do not truncate the source silently or reuse old GLM length budgets.
4. Keep generated token IDs intact through Miles training and teacher scoring. The existing [Qwen scorer](/data/ycfeng/sota-engine/miles/tests/manual/agent_opd/qwen_alignment.py:99) passes `sample.tokens` through the native scoring payload and checks returned completion IDs. Its old teacher label/workload must be replaced when implementing the accepted matrix. This code reading is not a successful scoring run.
5. Before GPU qualification, verify actual OSS/runtime template and tokenizer identities, selected-source completeness and exclusions, generation thinking mode, target masks/EOS, context limits and native input IDs. CPU formatting success does not settle numerical consistency or training effectiveness.

## Preserve-all capability — selected by latest D4

Current code already contains `Qwen35TITOTokenizer.FIXED_TEMPLATE`, resolved through `resolve_fixed_chat_template("qwen35")`, with `qwen3.5_fixed.jinja` and `preserve_thinking=True`. The template's SHA256 is `ca447731ed457cb460b7522ea9edb986d52e4ea62c5d8482365146592d69b1b9`. A source comparison found two behavioral differences from the pinned official file: the explicit preservation condition and removal of the no-user-query exception for incremental rendering. The task's real prefixes all contain user messages. No replacement template was written.

Exact CPU command, with the same Python and library environment as above:

```sh
timeout 60s /data/ycfeng/envs/openmopd-py312/bin/python /data/ycfeng/tmp/qwen35-three-pairs-format-kh3g82mp/verify_preserved_history.py
```

Probe SHA256: `054abfc159ebcb0a6daceac3b8c8b813b93a548dc05204648b75e52c3af2a732`. Exit status: `0`. Retained results: [qwen-preserved-history-cpu.json](evidence/qwen-preserved-history-cpu.json).

| Check | Expected | Observed | Status |
| --- | --- | --- | --- |
| Four actual single-user histories | Every nonempty reasoning span remains; renders agree with the native template on these unaffected histories. | 4/4 PASS; counts 83, 59, 57 and 56 retained; rendered text is byte-identical to native. | PASS |
| Constructed multi-user history | Reasoning before and after the final real user request remains with `preserve_thinking=True`. | Both spans retained for thinking and no-thinking generation modes. | PASS |
| Tokenization of fixed-template prefixes | Direct template tokenization equals render-then-encode without added special tokens. | Both modes match; constructed prefix lengths 65 and 67 tokens. | PASS |
| Loss semantics | Report current response-only mask boundary without claiming history has direct loss. | `_prepare_loss_masks` prepends prompt zeros; `sft_loss_function` also consumes designated response segments. | Source observation, not runtime qualification |

The current task preparation/launcher has not yet been wired to the selected template settings. This check proves the existing preserve-all capability, now selected by latest D4; it does not prove runtime acceptance. D6 resolves supervision as completion-only; no historical-token objective is needed.

## Earlier switch interpretation — superseded by the precise user rule

The user subsequently required a controllable history-inclusion switch. A focused CPU rendering check used two real-user messages with `EARLY_REASONING` in the first assistant and `LATE_REASONING` in the second, applying the existing fixed template directly:

```python
for value in [True, False]:
    text = tokenizer.apply_chat_template(
        messages, chat_template=fixed_template, preserve_thinking=value,
        tokenize=False, add_generation_prompt=True,
    )
    print(value, "EARLY_REASONING" in text, "LATE_REASONING" in text)
```

Observed: `True True True`, then `False False True`. Thus the existing boolean controls native old-turn omission, not complete inclusion/exclusion of all historical reasoning. The named Qwen TITO adapter also forces `preserve_thinking=True` for append-only sessions. The earlier proposal for a separate all-history keep/drop control was broader than the user's subsequently clarified rule and is superseded. Latest D4 selects the true setting by default; false remains an explicit native-rule override. Task launcher wiring remains pending. D6 separately fixes completion-only loss.

## Previous D4/D6 verification: native history boundary and completion-only target

The user selected temporary colocation, the native last-real-user reasoning rule and completion-only supervision. The same Python/tokenizer environment above was used for this focused CPU command:

```sh
timeout 60s /data/ycfeng/envs/openmopd-py312/bin/python /data/ycfeng/tmp/qwen35-three-pairs-format-kh3g82mp/verify_native_history_boundary.py
```

Script SHA256: `642d89f558739a7d7b7f06233152554186c4c9831c13b267ed2f0f63e2ca2106`. Exit status: `0`. Retained sanitized results: [qwen-native-history-boundary-cpu.json](evidence/qwen-native-history-boundary-cpu.json). Temporary output: `/data/ycfeng/tmp/qwen35-three-pairs-format-kh3g82mp/native-history-boundary-results.json`.

| Case | Expected reasoning in prefix | Observed | Prompt tokens | Status |
| --- | --- | --- | ---: | --- |
| User requests parser fix, assistant thinks/calls tests, tool returns failure | Keep the historical assistant reasoning after the real user. | Retained. | 86 | PASS |
| Add a new real user request to modify README | Remove reasoning before that new user message. | Omitted. | 79 | PASS |
| Represent the test result as a user-role tool-response wrapper | Keep reasoning; the wrapper is not a real user query. | Retained. | 84 | PASS |
| Four actual single-user local histories | Keep every after-user reasoning span. | 83, 59, 57 and 56 spans retained; all four agree with native rendering. | Previously recorded above | PASS |

In all three constructed cases, native rendering equals Miles' fixed-template rendering with `preserve_thinking=False`. Both tokenization routes match, the prefix ends with the expected assistant/open-thinking marker, and the illustrative future completion reasoning is absent from the prefix. Explicit `preserve_thinking=True` retains the old reasoning in all three, confirming that the existing setting remains controllable. These are constructed rendering cases, not model-generated outputs or proof of a loss tensor.

Source inspection separately confirmed:

- Miles `_prepare_loss_masks` in `miles/backends/training_utils/data/rollout.py` pads response-length masks with prompt zeros, matching the latest completion-only requirement. Actual shifted targets, EOS/padding, TIS application and token normalization still require native execution.
- The referenced Steptron `step_fixed_completion.py` identifies real-user boundaries excluding wrapped tools and represents prompt/completion mask segments separately. Its rejection of lost earlier reasoning is a fixed-completion preservation guard; it is not imported into this task. The worktree's GLM utility uses `clear_thinking=False`, which is not a Qwen template argument with the same effect.
- Miles `get_weight_transfer_protocol` in `miles/backends/training_utils/weight_update/protocol.py` selects CUDA IPC when colocated. Current D5 therefore records IPC as the transport to verify and original NCCL qualification as deferred. No worker transfer was executed.

This check verified the then-selected native serialization and target-boundary design. The false-mode result is retained after the default change. It does not qualify full-corpus preparation, actual OSS copies, GPU generation, teacher scoring, TIS, numerical agreement, learning or HF export.

Final documentation check: `git diff --check` exited 0. An inline `python3` check (3.10.6) passed for six maintained document headers, 47 local links, the latest raw request, the three expected history-presence values `[True, False, True]`, all four retained actual-history results and the recorded probe script SHA256. These checks validate document/evidence consistency only. The pre-existing Git index lock remains untouched; this documentation update is saved in the worktree and is not committed.

## Latest D4 default: preserve_thinking=True — CPU revalidation PASS

Reran the existing `verify_preserved_history.py` command above after the user changed the default. Exit status: `0`; the script and fixed-template hashes are unchanged. The result equals the retained [qwen-preserved-history-cpu.json](evidence/qwen-preserved-history-cpu.json). Both constructed multi-user cases retain early and late reasoning (65 and 67 tokens for the two fresh-generation modes), and both tokenization routes match. Four actual single-user histories retain 83/59/57/56 reasoning spans and remain equal to their previous renders. This revalidation did not load a model or execute a loss.

Source verification found concrete matching defaults in the referenced Steptron worktree: `PreserveThinkingMultiTurnChatTemplate._get_preserve_thinking` and `_tokenize`, the `Step4Tokenizer_V0_0528_PreserveThinking` documentation and dataset message conversion default to true. Miles `Qwen35TITOTokenizer.FIXED_TEMPLATE` already registers the fixed Qwen template with the same true setting. These are input-default observations, not a replay of a historical Steptron run. The Steptron SFT loss rules do not change this task's explicit D6 prefix-zero/completion-only target.

Multi-user task prefixes must be recounted under the latest default before selection; the four single-user fixtures alone do not establish full-population lengths. D7's total/response limits and no-prefix-truncation requirement remain in force, and all consumers must share the same selected-policy IDs.
