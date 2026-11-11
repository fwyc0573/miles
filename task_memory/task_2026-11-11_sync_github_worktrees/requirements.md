## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record the authorized GitHub worktree synchronization and its evidence. |

# Requirements

## [Original Request] 2026-11-11

> 检查当前2个worktree是否已经被同步到github repo，如果没有，do it

Synchronize the existing `agent-opd-h800-capacity` and `agent-opd-image` branches to their respective branches at `origin` (`https://github.com/fwyc0573/miles.git`). This worktree owns the `agent-opd-image` branch record. The explicit request authorizes ordinary commits and GitHub pushes for these worktrees.

Preserve the primary checkout and each branch's existing history. Keep the two requested branch identities; branch publication does not authorize merging either implementation into another branch or accepting unfinished native experiments.

Save outstanding source, configuration, task documentation, compact selected evidence, and the minimal pinned source needed by existing CPU tests. Preserve raw experiments, copied source trees and tool-local state on disk. The existing repository hook limits newly added files to1000KB; retain larger files locally and enumerate files omitted from this Git synchronization. This is a branch/source synchronization, with raw artifacts explicitly reported as outside the Git delivery.

Acceptance: each branch has an upstream, its local HEAD equals the live GitHub branch SHA, and it has no outstanding tracked changes or untracked project source/configuration/task-documentation files. Enumerated raw experiment/tool files may remain untracked. Record exact verification commands/results and limits. CPU validation must not be represented as native GPU or scientific acceptance.
