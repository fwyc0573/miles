## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the indexed turn order ticket. |
| 2026-11-08 | Rewrite for the interleaved turn order (D18). |
| 2026-11-08 | Rename the file from `01-indexed-turn-order.md`; documentation frozen. |
| 2026-11-08 | Done: all criteria verified on the real source copies ([test report](../test_report_2026-11-08_interleaved_turn_order.md)). |

# 01: SWE 输入改用 Interleaved turn order

**What to build:** 在已提交的 `tests/manual/agent_opd/swe_inputs.py` 中实现 [spec S2](../spec.md#s2-rollout-取数顺序d18)：用共享的 native cursor、M 个 native turn source 和 native block mixer 组成取数顺序，并报告 `remaining_turns` 和每个 bank 中取完的 conversation。

**Blocked by:** 文档冻结。

**Status:** done

- [x] `SWEInputConfig` 新增 `swe_active_conversations`（默认 1）和 `swe_block_turns`（默认 8）。`NativeSWEDataSource` 改为由共享 cursor、M 个 `OnlineTrajectoryTurnSource` 和 `TurnBalancedTrajectoryBlockMixer` 组成，不保留旧的单 source 路径。identity 记录 M、block 和全局取数序号。
- [x] M = 1：现有 `check_swe_inputs.py` 的检查在真实固定副本上全部通过，且前 512 次取数的 uid 序列与单个 native `OnlineTrajectoryTurnSource` 直接发出的序列完全相同。
- [x] M = 32、block = 8：直接读取 mixer 的输出（不渲染），在真实固定副本上检查前 2,048 次取数（8 个 update 的量）：每个 conversation 内 turn 严格递增且不重复；conversation 按文件顺序进入；同时打开的不超过 32 个。记录每 256 次取数覆盖的 conversation 数、每个 conversation 的 turn 数分布，以及同一 conversation 连续取出的最长长度（预期为 8；native mixer 按各 source 已发的 turn 数平衡，若出现更长的连续段，记录原因）。
- [x] 用小型合成文件集核对 `remaining_turns` 和取完报告，覆盖只有一个 assistant turn 的 conversation，以及最后一个 turn 超长的 conversation。
- [x] 两个独立实例给出相同序列；记录构造和取数耗时，并写入测试报告。
