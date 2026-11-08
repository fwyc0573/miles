## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Draft the final report ticket. |

# 06: Profile 报告与归档

**What to build:** 根据保留的文件，按 [spec S9](../spec.md#s9-验证与交付) 生成两个 cell 的报告，并写 `summary.md`。

**Blocked by:** 04、05。

**Status:** blocked — waiting for 04 and 05

- [ ] 从 JSONL 文件重新计算并列出：update 1、10、50、100、150、200 处的宏观 KL/NLL，KL-best update，默认 k 下的 KL trend 和 recovery gap。
- [ ] 列出训练结束时的 profile 统计：出现过的 conversation 数、alive 数、trend 有定义的 conversation 数、conversation recovery gap 的分位数。
- [ ] 写明准确的云端路径、未验证的 update、观察到的局限，以及结论适用的范围（例如两个 cell 各只有一组 seed）。
