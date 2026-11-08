## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Parent accepts Ticket01 after inspecting its six criteria, source/model receipts, actual parity and recorded limitations. |
| 2026-11-08 | Correct the parent-observed launcher field mismatch; verify construction from native RolloutConfig without injected tokenizer/population. |
| 2026-11-08 | Record T01-inputs implementation, actual native/Qwen parity and independent cursor verification. |

# Native SWE inputs — T01-inputs

## Outcome and scope

**PASS for Ticket01, accepted by the parent.** The parent inspected the six ticket criteria, adapter source and actual evidence, including the separately completed three-model identity and benchmark-overlap investigations. No GPU/platform operations, cloud writes, shared task-document edits, qualification-file edits or commits were performed by the input subagent. This acceptance does not establish GPU training or throughput.

The adapter directly executes the verified bytes of the standalone Steptron loader, with module registration before execution. It does not copy the native scanner/sampler. The native source owns source-file order, conversation order, assistant-turn order, empty-assistant skipping and epoch wrapping. The SWE-only source uses `domain=reasoning`, `source_group=swe`, `source_load_path=None` and `source_load_safetensors=None`; no shuffle, deduplication, status filter, task split or fixed-population sampling is added.

Native role/content conversion is compared against the actual recipe's `convert_to_chatml_with_tool`, extracted with AST so unrelated GPU imports are not required. The original assistant target is excluded and replaced by the native generation placeholder. Metadata history retains historical reasoning, JSON-string function arguments, tool-call IDs and replies. Only rendering inputs use the existing `normalize_tool_arguments` utility.

## Deliverables

- `tests/manual/agent_opd/swe_inputs.py`: `SWEInputConfig`, `NativeSWEDataSource` and reusable native-module/source-population/normalization/rendering/identity functions.
- `tests/manual/agent_opd/check_swe_inputs.py`: executable actual-source parity and boundary CLI, including real Qwen lengths, actual overlength rejection, native configuration merging and generation-budget application.
- [evidence/input-source-manifest.json](evidence/input-source-manifest.json): complete original copy manifest, independently verified local file hashes/bytes, and parent model-source receipt reference.
- [evidence/input-config.json](evidence/input-config.json): effective source, code, tokenizer, fixed-template and length configuration.
- [evidence/input-parity.json](evidence/input-parity.json): exact native identities, selected target boundaries, message hashes, token lengths/hashes and assertions.
- [evidence/input-checkpoint.md](evidence/input-checkpoint.md): read-only scope checkpoint.

## API and configuration contract

The actual Miles `CustomFunctionConfig` validator, `RolloutConfig.model_validate`, `load_function` and `compute_custom_function_config(rollout, rollout.data_source_path)` were exercised. The existing `make_rollout_config` fixture obtains real parser defaults and constructs the typed configuration received by the rollout executor; the adapter is then instantiated without an injected tokenizer or source population. Set:

```yaml
data_source_path:
  path: tests.manual.agent_opd.swe_inputs.NativeSWEDataSource
  config:
    swe_source_root: <directory containing the eleven source JSONs>
    swe_source_manifest: <COPY_COMPLETE.json>
    swe_native_loader_path: <standalone native loader Python file>
    swe_native_loader_sha256: ffd9bb314c2ad5be44c52e2bd11684b51204aaa82b63e298d557b9834becacc8
```

`SWEInputConfig` owns only those four custom fields and exposes their corresponding `--swe-*` CLI arguments. Existing launch fields own `hf_checkpoint`, `chat_template_path`, `apply_chat_template_kwargs`, `rollout_max_context_len`, `rollout_max_response_len`, and `n_samples_per_prompt`. This task uses the original 4B tokenizer, `qwen3.5_fixed.jinja`, both thinking kwargs `true`, `rollout_max_context_len=131072`, `rollout_max_response_len=131072`, and `n_samples_per_prompt=1`. The adapter rejects an unset/nonpositive context limit or a run-wide response cap smaller than that limit, rather than retaining the obsolete 8192-token cap. There is **no `--max-seq-len` launch flag**: only `Sample.max_seq_len` uses that name. The parent separately sets native training `seq_length=131072`; the adapter does not introduce another owner for the rollout context limit.

`get_samples(n)` returns `list[list[Sample]]`, one sample per accepted native turn. Rejections advance native `source_row_index` but not Miles `index`/`group_index`. Each instance owns a separate cursor. Returned `Sample.max_response_len` is `rollout_max_context_len - prompt_token_count`; the existing Miles `apply_sample_max_response_len` was tested to send this budget. `Sample.max_seq_len` carries that native context limit. Prompt history is never truncated.

Existing Qwen generation receives `metadata.source.{uid,group_id,category,prompt_token_count,prompt_sha256}`, plus `history`, `tools`, `thinking_enabled`, `chat_template_kwargs` and `native_ground_truth`. UID is the existing qualification format `file_sha256:source_item_index:assistant_turn_index`; epoch and cumulative native source ordinal distinguish repeated presentations. File hashes are computed once during source construction, not per sample; per-sample prompt token hashes preserve the existing Qwen validation contract.

`save(directory)` writes only `native_swe_inputs.json`, explicitly marked `resume_supported=false`. `load(directory)` raises `NotImplementedError`; HF-only exports cannot restore native cursor, replay, optimizer or RNG state. Native state loading in the parity CLI is only test-cursor positioning, not an approved training-restore API.

## Exact successful command

Working directory: `/data/ycfeng/sota-engine/miles`. Local Python: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, **3.12.13**; Transformers **5.19.0**; Torch import check **2.11.0+cu130**, CPU-only checks. No conda environment activation was used.

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -m tests.manual.agent_opd.check_swe_inputs \
  --source-root /data/ycfeng/tmp/qwen35-swe-full-r256/swe-sources-20261023 \
  --source-manifest /data/ycfeng/tmp/qwen35-swe-full-r256/swe-sources-20261023/COPY_COMPLETE.json \
  --native-loader /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/playground/users/wyx/MOPD/step3p6_mopd_online_turn_loader_0710.py \
  --native-loader-sha256 ffd9bb314c2ad5be44c52e2bd11684b51204aaa82b63e298d557b9834becacc8 \
  --native-recipe /data/ycfeng/steptron/.worktrees/step3p6-replay-v1/playground/users/wyx/MOPD/step3p6_mopd_turn_5experts_fullyasync_tis_no_kl_0710_h200.py \
  --tokenizer /data/ycfeng/tmp/swe-model-pairs-20261103/Qwen/Qwen3.5-4B \
  --chat-template miles/utils/chat_template_utils/templates/qwen3.5_fixed.jinja \
  --rollout-max-context-len 131072 \
  --temporary-root /data/ycfeng/tmp/qwen35-swe-full-r256 \
  --output-root task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence \
  --model-source-receipt task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/model-sources-exp-1108-144027-369537.json \
  > /data/ycfeng/tmp/qwen35-swe-full-r256/input-parity.log 2>&1
```

Exit **0**, reported `status=PASS`, seven representative first-conversation prefixes checked. Raw log and regression fixtures remain under the temporary root; durable selected evidence is linked above.

The initial identical command prefixed with `systemd-run --user --scope -p MemoryMax=30G` failed before Python ran: **`Failed to connect to bus: No such file or directory`**. The permitted `timeout 60s` fallback was used; the 30 GiB cgroup cap was unavailable, so no applied memory cap is claimed. All successful checks completed within that timeout.

## Assertions and actual values

| Check | Expected / passing condition | Observed | Result |
| --- | --- | --- | --- |
| Eleven source files | Each local SHA256 and byte count equals its copy-manifest entry, in manifest/native recipe order | All eleven match; **3,356,482,428 bytes** | PASS |
| Native code | Execute only bytes with the configured SHA256 | `ffd9bb31…becacc8`; actual recipe content SHA256 `09f6040b…de551` | PASS |
| Source count provenance | Preserve source counts without claiming all prefixes were encoded | Manifest reports **4,992 conversations / 446,569 raw assistant turns**; no full Qwen population scan performed | PASS |
| Native prefix and conversion | Original messages before selected target and native converted messages equal the adapter stages | Seven first-conversation targets; first target index **2**, ordinal **1**, conversation has **313 messages** | PASS |
| Actual Qwen prompt parity | Accepted sample UID, native ground truth, history, prompt string and token hash equal the independent native-conversion/render oracle | Five eligible representative first-conversation prefixes; full matches | PASS |
| Historical tools/thinking | Keep all nonempty historical reasoning and tool function names, schemas, replies and message IDs | Up to **114 reasoning messages / 155 tool calls / 155 tool replies**, **3 tools**; no target is leaked into its prompt | PASS |
| Actual long-prefix skip | Reject the final oversized turn, consume no generation slot, advance to the next original conversation | Source ordinal **155** rejected at **181,478 tokens**; next accepted ordinal **156**, conversation **1**, target index **2**, **1,350 tokens**, Miles sample index **5** | PASS |
| Exact length boundary | Reject `prompt_length == max_seq_len`; skip only offending turns | Character-count fault injection verifies equality rejection; source ordinals **0,3** accepted as slots **0,1** after two rejects | PASS |
| Conversation/file/EOF boundaries | Same native and adapted messages/order; UID repeats with a new epoch | Two-file fixtures made from actual excerpts; six rows with epochs **0,0,0,0,1,1**; two empty-assistant skips | PASS |
| Four independent cursors | Same start UID, advancing one must not move the others | Counts after advancing only the first: **2,1,1,1**; all other successors agree | PASS |
| Framework config/request budget | Real custom config merge, loader dispatch and native max-response application succeed | First actual prompt **1,547** tokens; request `max_new_tokens=129525` | PASS |
| Training restore | Clearly reject unsupported restore | `NotImplementedError`, preserved error in parity JSON | PASS |
| Parent model receipt linkage | Verified receipt's tokenizer JSON/config hashes equal local encoding assets for all three models | All three match; original-model/teacher revalidation is complete, parent-owned | PASS |

Representative first-conversation lengths:

| Assistant ordinal / target index | Qwen prompt tokens | Eligibility at 131072 | Remaining generation tokens |
| --- | ---: | --- | ---: |
| 1 / 2 | 1547 | eligible | 129525 |
| 2 / 4 | 2221 | eligible | 128851 |
| 8 / 16 | 28111 | eligible | 102961 |
| 32 / 64 | 72857 | eligible | 58215 |
| 64 / 128 | 107274 | eligible | 23798 |
| 100 / 200 | 146694 | reject | not generated |
| 156 / 312 | 181478 | reject | not generated |

## Source and model-specific differences

The tokenizer JSON SHA256 is `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42`; the effective fixed template SHA256 is `ca447731ed457cb460b7522ea9edb986d52e4ea62c5d8482365146592d69b1b9`. All three parent-verified original model sources have identical tokenizer JSON/config assets; this receipt is referenced rather than duplicated or rescanned.

The native Step template caller **does not pass `system.tools`**. Qwen explicitly passes them using its existing Qwen contract, normalizes JSON-string function arguments only for rendering, and uses the existing fixed Qwen XML tool syntax and thinking suffix. The task requires message/turn semantic parity, not Step/Qwen prompt bytes or token IDs to match. Qwen's real length rejects remain model-specific and observable.

The parent-owned overlap audit is already complete: [evidence/benchmark-training-overlap.json.gz](evidence/benchmark-training-overlap.json.gz) retains the all-source check, with zero normalized exact problem-text matches. Semantic nonoverlap remains unproven; no new data-policy change was made here.

## Additional checks and limitations

The first configuration probe used an extensible `ImmutableNamespace` containing `max_seq_len`; it did not prove native launcher compatibility. The parent observed that the actual launcher provides `rollout_max_context_len` and `seq_length`, with no parsed `max_seq_len`. The adapter and CLI were corrected to consume only `rollout_max_context_len`, with no compatibility fallback; the superseding typed `RolloutConfig` check asserts that the nonexistent field is absent from both the native schema and merged configuration. This checks the real construction path, not full GPU launch execution.

Python source `compile(...)` on both new modules returned **PASS**; the final parity command above used the actual configuration schema and native generation-budget utility. `python -m ruff check tests/manual/agent_opd/swe_inputs.py tests/manual/agent_opd/check_swe_inputs.py` could not run because the CPU environment has **`No module named ruff`**; Black and isort are also absent. No formatter/linter PASS is claimed.

Only selected actual raw prefixes were Qwen encoded: the seven listed first-conversation prefixes plus the actual next-conversation prefix used by the long-rejection check. Boundary checks use explicit short regression fixtures and do not represent a full-epoch scan. Global Qwen-eligible turn counts, full/r256 formal consumption and GPU generation/training behavior are not established by these CPU checks; Ticket02 owns native consumption and capacity. Default native epoch wrapping supplies the required presentation budget without introducing a custom sampler or a once-only pool. The external native module and source JSON paths must be mounted/readable in the runtime. Model source revalidation and overlap investigation are **complete**, with semantic-nonoverlap limitations retained.
