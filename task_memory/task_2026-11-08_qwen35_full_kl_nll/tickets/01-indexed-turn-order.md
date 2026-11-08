## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the indexed turn order ticket. |

# 01: SWE 输入改用 indexed turn order

**What to build:** 在已提交的 `tests/manual/agent_opd/swe_inputs.py` 中实现 [spec S2](../spec.md#s2-rollout-取数顺序d12)：按固定排列取 turns，并提供 profile 计算 `alive` 所需的剩余位置数。

**Blocked by:** 文档冻结。

**Status:** blocked — waiting for documentation freeze

- [ ] input config 新增取数顺序（现有的 `streaming` 保持默认；新增 `indexed`）及其 seed 字段。`indexed` 按 S2 建 population 和排列；现有 streaming 行为与检查结果不变。
- [ ] 在真实固定副本上，用 CPU 运行扩展后的 `check_swe_inputs.py`。记录 N 和 conversation 数（预期 446,569 / 4,992）、population 与排列的 sha256。源字节与 Q41 相同时，两个 sha256 应与 Q41 manifest 一致；不一致时记录差异和原因。
- [ ] 记录前 512 次取数（2 个 update）的 identity 序列和超长 rejection 计数；两个独立 cursor 给出相同序列；每个 turn 的 identity 带有排列位置。
- [ ] data source 提供每个 conversation 的剩余未取位置数；用小型合成文件集核对计数。
- [ ] 测量真实文件上建索引的耗时和内存，并写入测试报告。
