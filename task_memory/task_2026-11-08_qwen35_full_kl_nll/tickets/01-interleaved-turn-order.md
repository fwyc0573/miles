## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Close D34 from completed112K original-source audit/parity and terminal API receipt; distinguish current length/span limits from retained historical128K evidence. |
| 2026-11-09 | Reopen the length-policy slice forD34:112K inclusive prompt budget and16K completion within128K context; keep prior source evidence. |
| 2026-11-09 | Accept items5–6 from the completed real-source CPU audit,512 native parity draws and2,048 interleaved draws; retain32×8 and disclose measured length/span limits. |
| 2026-11-09 | Record the primary's running in-place CPU audit/parity job without claiming acceptance; separate exact-text proxy coverage from native SWE identity and ideal trend estimates. |
| 2026-11-08 | Draft the indexed turn order ticket. |
| 2026-11-08 | Rewrite for the interleaved turn order (D18). |
| 2026-11-08 | Rename the file from `01-indexed-turn-order.md`; documentation frozen. |
| 2026-11-08 | Done: all criteria verified on the real source copies ([test report](../test_report_2026-11-08_interleaved_turn_order.md)). |
| 2026-11-08 | Reopen for the SWE-1003 0913 data (D23–D27): selectable turn source, loss-masked training turns, visual exclusion, source audit, checks on the files in place. |
| 2026-11-08 | SWE-1003 items 1–4 verified locally ([test report](../test_report_2026-11-08_swe1003_turn_source.md)); items 5–6 wait for the CPU RJob. |

# 01: SWE 输入改用 Interleaved turn order

**What to build:** 在已提交的 `tests/manual/agent_opd/swe_inputs.py` 中实现 [spec S2](../spec.md#s2-数据源与-rollout-取数顺序d18d23d27)：用共享的 native cursor、M 个 native turn source 和 native block mixer 组成取数顺序，并报告 `remaining_turns` 和每个 bank 中取完的 conversation。turn source 按配置从表中选择，本 task 用 `loss_masked`（`MaskAwareSWETurnSource`），数据为原位读取的 SWE-1003 0913 文件。

**Blocked by:** 文档冻结；D23–D27 已写入 spec。

**Status:** done — D23–D27 historical128K source audit/parity retained ([historical report](../test_report_2026-11-09_source_audit.md)); D34 implementation, boundaries, actual native request construction and completed original-source112K audit/parity accepted ([current report](../test_report_2026-11-09_length_budgets.md#completed112k-original-source-audit)). D1/D22 remain separate prerequisites for02/03 integration; this is CPU input acceptance, not native capacity/trend acceptance.

### 已完成：interleaved 顺序（GLM 固定副本，turn source 为 `OnlineTrajectoryTurnSource`）

- [x] `SWEInputConfig` 新增 `swe_active_conversations`（默认 1）和 `swe_block_turns`（默认 8）。`NativeSWEDataSource` 改为由共享 cursor、M 个 `OnlineTrajectoryTurnSource` 和 `TurnBalancedTrajectoryBlockMixer` 组成，不保留旧的单 source 路径。identity 记录 M、block 和全局取数序号。
- [x] M = 1：现有 `check_swe_inputs.py` 的检查在真实固定副本上全部通过，且前 512 次取数的 uid 序列与单个 native `OnlineTrajectoryTurnSource` 直接发出的序列完全相同。
- [x] M = 32、block = 8：直接读取 mixer 的输出（不渲染），在真实固定副本上检查前 2,048 次取数（8 个 update 的量）：每个 conversation 内 turn 严格递增且不重复；conversation 按文件顺序进入；同时打开的不超过 32 个。记录每 256 次取数覆盖的 conversation 数、每个 conversation 的 turn 数分布，以及同一 conversation 连续取出的最长长度（预期为 8；native mixer 按各 source 已发的 turn 数平衡，若出现更长的连续段，记录原因）。
- [x] 用小型合成文件集核对 `remaining_turns` 和取完报告，覆盖只有一个 assistant turn 的 conversation，以及最后一个 turn 超长的 conversation。
- [x] 两个独立实例给出相同序列；记录构造和取数耗时，并写入测试报告。

### 已完成：SWE-1003 0913 数据（D23–D27）

These checks were accepted under the pre-D34 prompt policy. Source identities, native mask/visual policy and raw turn-order evidence remain retained; changed length behavior is accepted separately below.

- [x] 配置：`SWEInputConfig` 给出固定版本 Steptron 代码的根目录、所需模块的 sha256 和 turn source 名称，取代 `swe_native_loader_path` / `swe_native_loader_sha256`。turn source 表有两项：`loss_masked` → turn data 模块的 `MaskAwareSWETurnSource`，`all_assistants` → base loader 的 `OnlineTrajectoryTurnSource`；cursor 和 mixer 都来自 base loader。模块按 sha256 核对后以 Steptron 模块名注册。`loss_masked` 把源文件 manifest 的 `visual_source_item_indices` 作为 `excluded_source_item_indices` 传入。identity 记录 turn source 名称、各模块 sha256 和视觉排除名单的 sha256。
- [x] 渲染与 identity：工具定义取首条消息的 `tools`，没有时取 `tool_schemas`；`reasoning_effort` 不传入。每个 sample 的 source identity 新增 `source_assistant_turn_ordinal`、`context_masked_assistant_count` 和 `target_policy`。
- [x] 本地合成文件集检查 `loss_masked`：被 mask 的 assistant 留在前缀中且不是 turn；`t_id` 从 1 连续编号；视觉 conversation 和没有 training turn 的 conversation 被跳过；`remaining_turns` 只计 training turn；最后一个 training turn 超长时仍出现在取完报告中；`tool_schemas` 与 `tools` 渲染结果相同。
- [x] `all_assistants` 改用 f4522d45 的 base loader 后，`check_swe_inputs.py` 在本地 GLM 固定副本上的检查全部通过，序列和计数与上面已完成部分的证据相同。
- [x] 源数据审计（spec S2 数据源第 6 条）：`audit_swe1003_sources.py` 在 CPU RJob 中原位读取 8 个文件，不复制输入（D25）；验收实际 JSON 内容、源文件身份和 source manifest，不能只看 exit / PASS 字样。产物放入 `evidence/`，数字写入测试报告并更新 spec S2 的估算。native SWE instance / repository / commit identity 可缺失或未验证，须写 null / unverified；首条 user 内容的短 hash 只报 exact-text proxy 覆盖率、缺失与集中程度，不能把脚本 `task*` 字段当作已核验任务身份，也不能把 null 算作一个任务。模拟的 span coverage 与实际 baseline / trend coverage 分开；81 只作 D26 理想排程的反馈阈值，不是 trend 必要条件。中位数明显低于 81 时带着数字回来找用户；首条消息的 `preserve_thinking` 不为 true 时报告。实测中位数90；源首条消息均缺少该字段，Qwen配置显式为true；保留32×8，长度过滤和跨度限制见测试报告。
- [x] 原位真实数据检查（CPU RJob，`loss_masked`）：M = 1 时前 512 次取数的 uid 序列与单个 native `MaskAwareSWETurnSource`（相同排除名单）直接发出的序列完全相同，且这些 turn 渲染前的消息与 native `tokenize_swe_prefix` 的规范化结果（`s4_swe_turn_data_1001.py:60–67`）相同；M = 32、block = 8 时前 2,048 次取数满足上面相同的顺序性质；两个独立实例序列相同；记录构造和取数耗时。

### D34 length-policy revision

- [x] Use existing native prompt/response/context fields:114688 inclusive prompt tokens,16384 maximum completion tokens,131072 total context. Reject over-budget prompts before allocating slots, retaining native draw order and finished-conversation reporting; do not truncate messages.
- [x] Verify both prompt-boundary cases and the actual generation payload: exact112K accepted,+1 rejected, short and boundary prompts both capped at16K, total stays within128K. Existing mask/visual/order checks remain valid. See`test_report_2026-11-09_length_budgets.md`in the parent task directory.
- [x] Run the in-place CPU audit/parity with the updated config; inspect112K rejection/span figures and keep old128K outputs separately. Job/replica `exp-1109-154414-275606` Succeeded at11:47:11Z, confirmed by the primary's personal `get_rjob_client()` / API receipt at11:52:22Z. All8 source SHA/bytes/raw counts/visual exclusions match;512 native parity and2,048 interleaved raw draws PASS. Current112K rejects323,121/868,775 turns (37.1927%);32×8 simulation accepts51,200 from84,229 draws, covers869 conversations with span median5/P90 7/max9;0/869 span≥11 updates. Median23 conversations/update is not task coverage. Pre-length eligible median90 retains D26's32×8; post-length median absent/unverified. Native task identity stays UNVERIFIED/null and955 prompt groups remain proxies. Simulated spans do not verify runtime trend. Exact commands, environment, expected/actual values and limits are in the current report; historical128K artifacts remain unchanged.
