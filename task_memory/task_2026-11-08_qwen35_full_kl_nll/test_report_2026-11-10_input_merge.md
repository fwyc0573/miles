## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Resolve the input merge in favor of the approved parent contract, adapt the native caller and test fixtures, and record scoped offline verification. |

# Input Merge Test Report

Task ID: `profile-input-merge-20261110`.

## Scope and Outcome

The merge was already in progress in `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`: parent `eee754bc` merging verified candidate `0e6e8b1e9298638fd72651869692a41cad703b71` under parent D35. This slice resolves only the input conflicts and directly owned callers/tests. The primary owns merge acceptance and the merge commit.

Owned paths:

- `tests/manual/agent_opd/swe_inputs.py`
- `tests/manual/agent_opd/check_swe_inputs.py`
- `tests/manual/agent_opd/run_swe_opd.py` — input argument wiring only
- `tests/fast/test_swe_launcher.py`
- `tests/fast/rollout/test_sample_max_response_len.py`
- This report

Both conflict files are byte-identical to their parent HEAD versions after resolution. Their pinned-module registry, manifest visual exclusions, native shared cursor/block mixer, explicit prompt/response limits, and finished-conversation reporting remain unchanged. The candidate single-loader/visual-receipt constructor is superseded; no compatibility constructor, production alias, or silent inference was introduced. Candidate replay, session and NCCL repairs are outside these edits and remain merged.

Only the two conflict files were passed to `git add --` to remove their unmerged index stages. They have no diff against HEAD, so they do not appear in the final scoped status output. The three adapted Python files retain unstaged changes on top of the merge's existing index entries; this report is untracked until the primary stages it. No commit, `git add -A`, archived-config edit, historical-evidence edit, full-source audit, platform/network/SSH/GPU operation, or dependency installation occurred.

## Exact Source Schema

`run_swe_opd._training_args` now requires the following explicit `config["inputs"]` fields and passes them to the existing registered `SWEInputConfig`:

| Input JSON field | Native custom config field | Type / contract |
| --- | --- | --- |
| `source_root` | `swe_source_root` | Source directory path |
| `source_manifest` | `swe_source_manifest` | COMPLETE manifest path; file bytes/SHA256 are verified by the existing constructor |
| `steptron_root` | `swe_steptron_root` | Root containing the pinned dotted-module paths |
| `module_sha256` | `swe_module_sha256` | JSON object: dotted module name to SHA256 |
| `turn_source` | `swe_turn_source` | Existing registry key: `all_assistants` or `loss_masked` |
| `active_conversations` | `swe_active_conversations` | Explicit native source count; parent formal value 32 |
| `block_turns` | `swe_block_turns` | Explicit native mixer block size; parent formal value 8 |
| `chat_template_path` | `chat_template_path` | Existing native rendering field |
| `chat_template_kwargs` | `apply_chat_template_kwargs` | Existing kwargs; preserve_thinking and enable_thinking must both be true |

Required module pins are selected by the existing `turn_source_pins` registry:

- `all_assistants`: `playground.baseline_new.mopd.online_turn_loader`.
- `loss_masked`: that base loader plus `playground.users.cj.opd.s4_swe_turn_data_1001`.
- `loss_masked` reads each manifest file's `visual_source_item_indices`; no separate constructor receipt replaces these exclusions.

The locally exercised pins were read from the existing parent `source_audit_config.json`: base loader `0c11561f33dacf1a15cd804dbd2f4feed4d1c33734bfaea7a416fdf1efaa740f`, turn data `8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980`, root `/data/ycfeng/steptron/.worktrees/reasoning-replay-f4522d451a9`.

Top-level `context_tokens`, `prompt_tokens`, and `response_tokens` still feed the existing native fields. D34 remains 131072 total context, 114688 inclusive prompt, and 16384 completion maximum. Prompt excess is rejected without consuming accepted slots or truncating history. The source requires a set, positive prompt limit smaller than context; requests use the smaller of completion maximum and remaining context.

The launcher no longer emits `swe_native_loader_path`, `swe_native_loader_sha256`, `swe_skip_masked_assistant_turns`, or `swe_visual_filter_receipt`. Missing new source fields raise a `KeyError` rather than deriving a replacement from old loader fields. Old archived recipes are intentionally not executable through this new source contract without an explicitly adapted caller/configuration. The primary owns the new formal configuration and other callers outside this slice.

## Fixture Changes and Verification Boundaries

The launcher tests adapt archived recipes only in memory: model/resource/training shapes remain available, while their input fixture explicitly supplies the new source fields. The registration test checks every source field, both registry kinds, 32x8 transport, and absence of the four superseded flags. Five missing-field cases prevent silent defaults/inference.

The response-length tests reuse `tests/fast/test_swe_input_limits.py::adapter_factory`, which supplies the parent's external pinned-module/source/mixer boundary and typed config. The redundant old injected-source implementation was removed. The real adapter, budget application, replay generation, Qwen generation hook, native request builder and reward path still execute. The external module protocol, token-count tokenizer, model I/O and student/teacher POST boundaries remain fixtures.

The remaining-context edge now uses explicit prompt limit 131071 rather than unsupported None. This is a boundary probe, not the formal D34 prompt limit. Existing None/invalid-limit rejection tests remain in `test_swe_input_limits.py`. Replay-to-request cases still cover prompt counts 4366, 114687, 114688, and 131071, completion budgets 16384/16384/16384/1, unchanged seed 1729, unchanged shared generation defaults, and total context at most 131072.

## Environment

- Linux; zsh commands run from the worktree above.
- Python `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, version 3.12.13; pytest 9.1.1; torch 2.11.0; SGLang 0.5.23; Transformers 5.19.0.
- Offline Ruff/Black/isort executables: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin`; import root set to the matching `packages` directory.
- Temporary fixtures/caches stay under `/data/ycfeng/tmp/opencode-v2-tmp/opencode`. No environment configuration was changed.

## CPU Tests

Exact commands:

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/test_swe_launcher.py tests/fast/rollout/test_sample_max_response_len.py tests/fast/test_swe_input_limits.py tests/fast/test_swe_input_pins.py tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_generate_endpoint_utils.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-input-merge-20261110-first
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/test_swe_launcher.py tests/fast/rollout/test_sample_max_response_len.py tests/fast/test_swe_input_limits.py tests/fast/test_swe_input_pins.py tests/fast/test_swe_replay.py tests/fast/rollout/generate_utils/test_generate_endpoint_utils.py --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-input-merge-20261110-final
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/test_swe_launcher.py::test_native_input_policy_reaches_registered_source_config --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-input-merge-source-schema-final
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m tests.manual.agent_opd.check_swe_inputs --help
```

| Check | Passing condition | Actual result | Verdict |
| --- | --- | --- | --- |
| First affected suite | Input registration, slot/length boundaries, pins, native replay budgets and existing payload checks pass | 139 passed, 20 warnings, 16.44s | PASS |
| Final affected suite after fixture import/format correction | Same acceptance, no owned-file test failure | 139 passed, 20 warnings, 16.21s | PASS |
| Final source registration check after replacing dynamic getattr in the assertion | Both registry kinds preserve every explicitly configured field | 2 passed, 20 warnings, 2.58s | PASS |
| Checker CLI | Required module/root/turn-source/mixer and three explicit budget arguments are available; no old loader/receipt options | Expected help printed, exit 0 | PASS |

Warnings were retained: SWIG and torch.jit deprecations, existing datetime.utcnow deprecation, CPU AWQ/GGUF limitations, and the interpreter-exit swigvarlink deprecation. No socket-opening or real HTTP test was selected.

## Existing Native Synthetic Checks

This direct execution reused the existing checker functions with genuine pinned CPU modules and the already-local Qwen tokenizer. Only synthetic source JSON was generated. It did not read original posttrain trajectories or repeat a source audit.

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import json, uuid
from pathlib import Path
from types import SimpleNamespace
from tests.manual.agent_opd import check_swe_inputs as check

repo = Path.cwd()
config = json.loads((repo / 'task_memory/task_2026-11-08_qwen35_full_kl_nll/source_audit_config.json').read_text())
root = Path('/data/ycfeng/tmp/opencode-v2-tmp/opencode') / ('profile-input-merge-native-' + uuid.uuid4().hex)
root.mkdir()
args = SimpleNamespace(
    source_root=root, source_manifest=root / 'COPY_COMPLETE.json',
    steptron_root=Path(config['steptron_root']), module_sha256=config['module_sha256'],
    turn_source='loss_masked', tokenizer=Path(config['tokenizer']),
    chat_template=repo / config['chat_template'],
    rollout_max_context_len=131072, rollout_max_prompt_len=114688, rollout_max_response_len=16384,
    temporary_root=root, active_conversations=32, block_turns=8, parity_draws=64, order_draws=512,
)
pins = {name: sha for kind in check.TURN_SOURCES for name, sha in check.turn_source_pins(kind, args.module_sha256).items()}
modules = check.load_pinned_modules(args.steptron_root, pins)
tokenizer = check.load_tokenizer(str(args.tokenizer), chat_template_path=str(args.chat_template), local_files_only=True)
results = {
    'length_rejection': check._length_rejection_check(args),
    'finished_report': check._finished_report_check(args),
    'loss_masked_fixture': check._loss_masked_fixture_check(args, modules, tokenizer),
}
conversations = [
    [message for ordinal in range(32) for message in (
        {'role': 'user', 'content': f'conversation {index}, question {ordinal}', 'loss_mask': 0},
        {'role': 'assistant', 'content': 'historical target', 'loss_mask': 1},
    )]
    for index in range(40)
]
population = check._fixture_population(root / 'native-order', [conversations[:20], conversations[20:]])
reference = check._native_reference(modules, args.turn_source, None)
results['single_source_parity'] = check._single_source_parity(args, modules, population, tokenizer, reference)
results['interleaved_order'] = check._interleaved_order(args, modules, population, tokenizer)
results['four_cursors'] = check._four_cursors(args, population, tokenizer)
args.source_root = Path(population.filelist[0]).parent
args.source_manifest = args.source_root / 'COPY_COMPLETE.json'
args.source_manifest.write_text(json.dumps(population.manifest, indent=2) + '\n')
results['configuration'] = check._configuration_check(args)
(root / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps({'fixture_root': str(root), 'statuses': {key: value['status'] for key,value in results.items()},
                  'single_source_draws': results['single_source_parity']['draws'],
                  'interleaved_draws': results['interleaved_order']['draws'],
                  'interleaved_active_conversations': results['interleaved_order']['active_conversations'],
                  'request_max_new_tokens': results['configuration']['native_request_max_new_tokens']}))
PY
```

Observed artifact: `/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-input-merge-native-9e02a5bfe0c24b1ea5f7539f3c4532c0/results.json`.

All seven functions returned PASS: exact length rejection/inclusive requests, finished report including a rejected last turn, native loss-mask/visual/tool/thinking behavior, 64 single-source parity draws, 512 actual native interleaved draws with 32x8, four independent cursors, and the ordinary typed registry factory. The constructed request uses max_new_tokens=16384. The length fixture records 114688+16384=131072 at equality; rejected turns consume zero accepted slots. Native modules and tokenizer were not replaced in this direct check. The deep_ep unavailable warning was retained.

## Static Checks and Baseline Limitations

```bash
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check --no-cache tests/manual/agent_opd/swe_inputs.py tests/manual/agent_opd/check_swe_inputs.py tests/manual/agent_opd/run_swe_opd.py tests/fast/test_swe_launcher.py tests/fast/rollout/test_sample_max_response_len.py
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check --no-cache tests/manual/agent_opd/check_swe_inputs.py tests/manual/agent_opd/run_swe_opd.py tests/fast/test_swe_launcher.py tests/fast/rollout/test_sample_max_response_len.py
git show HEAD:tests/manual/agent_opd/swe_inputs.py | PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/ruff check --no-cache --stdin-filename tests/manual/agent_opd/swe_inputs.py -
BLACK_CACHE_DIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode/black-cache-profile-input-merge PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/black --check --diff tests/fast/rollout/test_sample_max_response_len.py
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/isort --check-only --diff tests/manual/agent_opd/swe_inputs.py tests/manual/agent_opd/check_swe_inputs.py tests/manual/agent_opd/run_swe_opd.py tests/fast/test_swe_launcher.py tests/fast/rollout/test_sample_max_response_len.py
PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/isort --check-only --diff tests/manual/agent_opd/swe_inputs.py tests/manual/agent_opd/run_swe_opd.py tests/fast/test_swe_launcher.py tests/fast/rollout/test_sample_max_response_len.py
git show HEAD:tests/manual/agent_opd/check_swe_inputs.py | PYTHONPATH=/data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages /data/ycfeng/tmp/opencode-v2-tmp/opencode/qwen-review-lint/packages/bin/isort --check-only --diff --filename tests/manual/agent_opd/check_swe_inputs.py -
git diff --exit-code HEAD -- tests/manual/agent_opd/swe_inputs.py tests/manual/agent_opd/check_swe_inputs.py
git add -- tests/manual/agent_opd/swe_inputs.py tests/manual/agent_opd/check_swe_inputs.py
git diff --name-only --diff-filter=U
git diff --check -- tests/manual/agent_opd/swe_inputs.py tests/manual/agent_opd/check_swe_inputs.py tests/manual/agent_opd/run_swe_opd.py tests/fast/test_swe_launcher.py tests/fast/rollout/test_sample_max_response_len.py
```

- Initial Ruff found a new F811 from directly importing an otherwise-unused pytest fixture. Referencing the existing fixture through its module removed that diagnostic. Final four-file Ruff check passes. The unchanged source retains B905 at `swe_inputs.py:320`, reproduced on HEAD. No suppression or unrelated strict-zip edit was added.
- Black found one missing blank line in the new fixture wrapper; the scoped patch fixed it. Final response-length test-file check passes. No full-file Black pass is claimed for the other, already-unformatted files.
- isort passes for the source, native caller, and both adapted test files. The unchanged checker fails import sorting, with the identical diff reproduced from HEAD.
- Both conflict files exactly match HEAD; the unmerged file list is empty after staging them. Scoped whitespace checks pass.

Exact syntax/config-access verification:

```bash
PYTHONDONTWRITEBYTECODE=1 /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import subprocess
from pathlib import Path
from tools.lint_config_attribute_access import _violations
paths = ['tests/manual/agent_opd/swe_inputs.py', 'tests/manual/agent_opd/check_swe_inputs.py', 'tests/manual/agent_opd/run_swe_opd.py', 'tests/fast/test_swe_launcher.py', 'tests/fast/rollout/test_sample_max_response_len.py']
for index, name in enumerate(paths):
    path = Path(name)
    compile(path.read_text(), str(path), 'exec')
    issues = _violations(path)
    if index < 2:
        assert path.read_bytes() == subprocess.check_output(['git', 'show', f'HEAD:{name}'])
        assert len(issues) == [1, 4][index]
        print(name, 'compile PASS; unchanged HEAD diagnostics', issues)
    else:
        assert not issues
        print(name, 'compile/config access PASS')
PY
```

All five files compile. The first whole-scope config-access assertion stopped at the source's pre-existing dynamic module-class selection diagnostic. The completed check retains exactly five baseline diagnostics in the two byte-identical conflict files: source line260; checker lines396,397,646,649. A newly added dynamic getattr in the launcher test assertion was replaced with access to the typed config's model_dump; the three adapted files now have no config-access diagnostics. These baseline failures are recorded, not counted as lint passes.

## Separately Reproduced SGLang Parser Baseline

```bash
TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest -o addopts= -p no:cacheprovider -q tests/fast/test_qwen35_opd_launcher.py::test_native_parser_accepts_sglang_and_custom_mis_flags --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/profile-input-merge-sglang-baseline
```

Observed: 1 failed, 20 warnings, 3.94s. At `tests/fast/test_qwen35_opd_launcher.py:183`, the unknown flags have one extra item: `--sglang-enable-prefill-weight-versions`. This matches the independently recorded local SGLang-version limitation in `../task_2026-11-09_profile_h800_preparation/test_report_2026-11-09_node_local_network.md`. This slice changed neither that caller nor that test, did not remove the flag, and did not weaken its assertion. It is separate from the 139 passing affected checks and does not establish worker-image parser behavior.

## Remaining Work and Limits

The owned input resolution and checks are complete. The primary must inspect/stage the three adapted Python files and this report, accept the rest of the concurrent merge, record the actual merge commit, and create/verify the new formal configuration using the explicit schema above. Parent Ticket02 per-turn sums and Ticket03 integration were not implemented here. Other merged tests/callers that read historical single-loader configs were not changed or comprehensively executed in this slice; adapt their in-memory fixtures under their owners rather than adding production compatibility or changing archived configs.

These CPU checks do not repeat or replace the accepted original-source audit, verify platform deployment, execute real HTTP requests or optimizer updates, certify GPU capacity, or accept formal 200-update A/B profiles.

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| 两个 input 冲突按 parent contract 解决 | PASS | 文件逐字等于 HEAD，仅 stage 两个冲突路径；unmerged 列表为空。 |
| native input wiring 与 owned fixtures 接入 | PASS | 显式 source schema 和两种 registry key 验证通过；未添加兼容路径。 |
| scoped CPU/static 验证与交接报告 | PASS | 139 tests、七个 native 合成检查及最终两种 source 注册验证通过；baseline 限制单独记录。 |
| merge commit / T02 / T03 | SKIPPED | 本 slice 明确不执行；由 primary 在 merge 验收后继续。 |

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** 本次 merge-input delegation 开始至报告完成｜**当前前沿：** primary merge 验收与提交。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 复用现有 fixtures/checker；通过后停止，不重做 full-source audit。 |
| D2 细节反复重试 | CLEAR | 新增 import/format/dynamic-access 诊断分别一次定位修正；baseline 未反复试改。 |
| D3 支线问题修补 | CLEAR | SGLang parser 与旧 lint 只复现记录，没有产品修补。 |
| D4 可并行任务停滞 | CLEAR | primary 与其他 owners 的文件不在本 slice；独立检查并行执行。 |
| D5 超范围镀金 | CLEAR | 未添加新 constructor、兼容机制或测试文件。 |
| D6 分析空转 | CLEAR | 探索直接用于冲突选择、caller 编辑和验证。 |
| D7 路线违背 | CLEAR | 保留 parent registry/mask/length/finish contract，不提交或修改历史配置。 |

**文档检查：** S1–S4/S6 未发现本 slice 的缺陷；S5：parent plan.md:77 的“merge 未开始”文字尚未反映实际 in-progress merge，状态同步由 primary 执行。
**归因：** 无执行偏离；S5 为并行 merge 状态记录待同步。

## 3. 纠正建议

**分支：** B：同步 parent 的 merge 状态，不改变 agreed scope 或验收标准。

**文档更新（先执行）：**
1. `plan.md` 当前前沿与 `progress.md`：primary 记录本次实际 merge 状态，并在提交后写入真实 commit 与接入剩余项（可直接执行）。

**需停止的偏离行为：** 无。

**接下去的路线：**
1. primary 验收/提交 merge 与 explicit formal configuration → 完成标志：整合 commit 和配置证据已记录。
2. 按原 dependency graph 执行02 CPU-ready →03 integration；本 slice 停止继续扩展检查。

## 4. 最值得关注的 3 点

1. 两个冲突文件保留 parent 的已验收 contract；candidate native runtime fixes 没有被此 slice 改写。
2. 所有 owned CPU checks 通过；已知 SGLang/parser 与 lint baseline 不能误报为新 merge 回归或全量 lint PASS。
3. archived configs 保留旧 schema，不能静默兼容；新的 formal config、其他 callers 和最终 merge commit 由 primary 验收。
