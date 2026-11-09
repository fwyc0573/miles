## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Record T03-LOCAL-SUBMIT local adapter, CPU verification, CLI and runtime acceptance limits. |

## 1. 规划完成情况

**汇总：** PASS 3｜BLOCKED/FAILED/SKIPPED 1｜TODO 0

| 子任务 | 状态 | 简要依据 |
| --- | --- | --- |
| T03-LOCAL-SUBMIT：单点评测提交适配器 | PASS | 使用已有 admission policy、共享 flock 和原生 RJobBackend；始终一节点、两 GPU。 |
| T03-LOCAL-SUBMIT：worker 准备与接口连接 | PASS | 原子 receipt 发布、已有 bounded rendezvous、显式原始模型入队、qualification 参数传递、exec 原 worker。 |
| T03-LOCAL-SUBMIT：CPU 验证与交付记录 | PASS | 新增 27 项测试全部通过；连同已有 policy 测试共 37 项通过。 |
| T03 原生 GPU/SWE runtime 验收 | SKIPPED | 本子任务禁止平台、GPU、网络、云卷及凭证操作；仍由 parent 负责，不构成 Ticket03 完成。 |

Task ID: **T03-LOCAL-SUBMIT**。只新增以下文件，无 commit，无其他 owner 文件修改：

- `tests/manual/agent_opd/submit_swe_evaluation.py`
- `tests/fast/test_swe_evaluation_submission.py`
- 本报告。

**设计与安全决定：**

- 本地输入沿用 `integration_config.json` 的 image、mounts、creator、GPU tag、charged_group、local mount、共享准入锁和 policy；不另存准入上限。只有新鲜的 `policy_admission_snapshot` 结果决定 `preemptible`。
- 默认采用已有 A/teacher 角色的 16 CPU、128 GiB sizing。显式 `evaluation_resources` 是完整替代资源描述，字段为 `cpu_per_node`、`memory_gb_per_node`、`host_network`、`gang_start`；可声明 `nodes=1`、`gpus_per_node=2`，其他拓扑拒绝。没有新的硬件估算。
- 可选 `envs` 传递普通部署环境。`SR_USER_TOKEN` 与 `SESSION_ROUTER_USER_TOKEN` 只从进程环境继承；一方存在时补齐别名，两方不同则报错，不把 token 放进配置、receipt、stdout 或 argv。
- 提交只允许在配置的本地 mount root，并拒绝 RJob 内的嵌套提交。配置、receipt 和共享锁限定在本地 mount；evaluation artifact root 限制在个人 cloud namespace。
- `miles.utils` 在任何 StepMind import 之前加载，防止 StepMind 的 vendored 搜索路径影响 Miles package。CPU planning/help 不加载 StepMind 或 Ray。
- 本地 StepMind Python3.10 只读取已构造的配置；GPU 准备/原 worker 使用配置的 pinned-image Python3.12；原 worker 再启动已配置的 repaired SWE Python3.10。适配器不构造 native harness，不混合两套 binary site-packages。
- 新 receipt 的 `.pending` 文件独占创建。完整 JSON fsync 后通过不覆盖目标的 hard link 发布，再 fsync 所在目录；worker 复用 `rjob_warmup._wait_file`，截止时间取已有 server startup timeout，不增加无期限等待。
- receipt 绑定真实 backend 返回的 job name、point、两卡 allocation 和 admission 结果。worker 准备先校验实际 job/point/两卡 receipt，再调用已有 `validate_allocation`；原 worker 继续负责实际 replica/GPU/配置检查。
- `--original-source` 显式要求 worker 在挂载云卷上调用 `enqueue_baseline`，然后 exec 原 worker。没有本地 cloud 入队，没有假造 formal HF、native counters 或 weight identities。省略该参数时只消费 trainer 已入队的 point。
- 适配器不调用 resume，不恢复或重试任何 slot，不改写既有 point/receipt，不执行 grader，不复制或删除源权重。相同 baseline manifest 的原生幂等入队不会重置状态或 deadline。
- launcher 通过原生 `workers.wait()` 保持存活至终态；wait 异常不吞掉。原 worker 经 `execv` 替换准备进程，保留其数字退出码；backend 只提供 normalized terminal status，因此 launcher 不能假称已读到平台 worker 的具体数字退出码。非成功终态返回非零。

**验证环境：** Linux；工作目录 `/data/ycfeng/sota-engine/miles`。测试 Python 为 `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`，Python **3.12.13**、pytest **9.1.1**。本地 import/help 另用 `/data/ycfeng/tmp/stepmind-env/bin/python`，Python **3.10.6**。没有 conda 切换、依赖安装或真实认证读取。

| 检查 | 预期/通过条件 | 实测 | 结果 |
| --- | --- | --- | --- |
| 第一轮新文件测试 | 所有 adapter CPU cases 通过 | 25 passed，0.63 s | PASS |
| 第二轮加入真实 baseline API 与 exec 测试 | 本地 protected-source 不修改；真实 exec 保留 code 23 | 27 passed，1.03 s | PASS |
| 最终 adapter + 既有 policy suite | 新 27 + 既有 10，无真实平台调用 | 37 passed，0.91 s | PASS |
| D9 task-window fixtures | 62+2 非抢占；64+2 整份抢占；到期 personal 56+2 拒绝 | 全部通过；拒绝时无 backend submit | PASS |
| 并发准入 | API read 和 submit 期间竞争 LOCK_NB 失败；wait 期间锁已释放 | 全部通过 | PASS |
| Receipt/startup | final receipt 不暴露半写 JSON；已有 receipt 不覆盖；wait timeout 不启动 worker | 全部通过 | PASS |
| Token 通道 | 两个别名在 resource.envs；receipt/输出/command 不含 synthetic token | 全部通过 | PASS |
| Qualification/native handoff | 两个显式 task#attempt-N 保持顺序传递；enqueue 先于 exec | 全部通过 | PASS |
| 原始模型保护 | 真实 EvaluationStore enqueue_baseline 产生 owned=false/native_update=null；内容和 mtime 不变；不同 contract 拒绝覆盖 | 全部通过，仅本地 fixture 文件 | PASS |
| Cross-interpreter import/help | local3.10 import 成功；不导入 StepMind/Ray | `miles.utils` 来自本 checkout，两个 imported 标志均 False | PASS |
| Ruff / isort / Black / diff whitespace | 两个新增 Python 文件通过现有格式与静态检查 | 全部通过 | PASS |

测试仅使用 synthetic credentials、synthetic API objects、CPU fixtures 和本地临时文件。所有 fixture job IDs/commitments 都不是平台观测。没有 native score、attempt 完成数或 GPU availability 结论。

**精确验证命令：**

```bash
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_evaluation_submission.py -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-local-submit-first
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_evaluation_submission.py -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-local-submit-second
/data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -m pytest tests/fast/test_swe_evaluation_submission.py tests/fast/test_rjob_budget.py -q --basetemp=/data/ycfeng/tmp/opencode-v2-tmp/opencode/t03-local-submit-final
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/A53yPWq_nK1ZlBb3/bin/ruff check tests/manual/agent_opd/submit_swe_evaluation.py tests/fast/test_swe_evaluation_submission.py
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/YeSQ9F0UbXV9REOw/bin/isort --profile=black --line-length=119 --check-only tests/manual/agent_opd/submit_swe_evaluation.py tests/fast/test_swe_evaluation_submission.py
/data/ycfeng/tmp/opencode-v2-tmp/opencode/uv-cache/archive-v0/-kQQ6CPyKAABpsmE/bin/black --line-length 119 --check tests/manual/agent_opd/submit_swe_evaluation.py tests/fast/test_swe_evaluation_submission.py
/data/ycfeng/tmp/stepmind-env/bin/python -B -m tests.manual.agent_opd.submit_swe_evaluation --help
/data/ycfeng/tmp/stepmind-env/bin/python -B -c 'import sys; from tests.manual.agent_opd import submit_swe_evaluation; import miles.utils; print(sys.executable, sys.version.split()[0]); print("miles.utils", miles.utils.__file__); print("steptron_imported", "steptron" in sys.modules); print("ray_imported", "ray" in sys.modules)'
git diff --check
```

工具记录：首个通用 `python -c` 检查返回 `zsh:1: command not found: python`。随后确认 `/usr/bin/python3` 为3.10.6且无 pytest，改用已有 Miles CPU 环境；未安装新依赖。初次 Black/isort 检查发现新增代码格式问题，已修正并复检通过。剩余 warning 仅为既有 Swig deprecation 和 Ruff 旧配置键警告，无未解决测试错误。

## 2. 偏离检测

**结论：** 未偏移，正常推进。
**检测窗口：** T03-LOCAL-SUBMIT 委派至本次本地交付｜**当前前沿：** parent 的02/03 native integration；本子任务已完成。

| 模式 | 判定 | 依据 |
| --- | --- | --- |
| D1 工具打磨 | CLEAR | 新测试仅验证指定 submit/receipt/enqueue/exec 契约；验证通过后停止扩展。 |
| D2 细节反复重试 | CLEAR | 运行没有未解决功能失败；格式检查问题一次修正。 |
| D3 支线问题修补 | CLEAR | 只新增被委派的两份 Python 文件和报告。 |
| D4 可并行任务停滞 | CLEAR | parent 明确划分 worker/config/native owner；本子任务不进入其文件或平台操作。 |
| D5 超范围镀金 | CLEAR | 没有 watcher、scheduler、grader、自动 resume/retry 或新的硬件规则。 |
| D6 分析空转 | CLEAR | 源码调查落实为实际 adapter 和可执行测试。 |
| D7 路线违背 | CLEAR | 复用 spec S7/D9 policy；遵守 local-only 与禁止 commit 的委派边界。 |

**文档检查：** S1–S6 在本委派范围未发现明显缺陷。依据 `requirements.md` D9 amendment、D10、`plan.md` 当前前沿、Ticket03 和 parent 的 `progress.md`；没有把 CPU PASS 升格为 native Ticket03 PASS。
**归因：** 无。

## 3. 纠正建议

**分支：** A：spec/tickets 合理，无需改动。
**需停止的偏离行为：** 无。

**接下去的路线：**

1. parent 选择已构造的 evaluation 配置、明确的 point/attempt IDs 和新 receipt，先 dry-run，再在已有 personal-auth shell 中从 `/data/ycfeng` 调用适配器。以下 CLI 未在本子任务提交真实 job。
2. parent 验证实际 creator、host mount、两 GPU、receipt task annotation/preemption、worker startup 与 native SWE attempt；保持 launcher 存活到终态，检查持久结果/reader cleanup。该证据才支持 runtime acceptance。
3. 并行继续02训练验收；03 qualification 本地能力交付不阻塞其独立工作，也不允许越过正式04–08的前置验收。

**精确 CLI：** 在已按 handbook 初始化 personal auth 的本地 shell 使用；所有变量由 parent 选择，不能把下面的变量占位当成真实平台证据。

```bash
PYTHONPATH=/data/ycfeng/sota-engine/miles:/data/ycfeng/steptron \
/data/ycfeng/tmp/stepmind-env/bin/python -B -m tests.manual.agent_opd.submit_swe_evaluation \
  --config /data/ycfeng/sota-engine/miles/task_memory/task_2026-11-08_qwen35_swe_full_r256/integration_config.json \
  --configuration "$EVALUATION_CONFIG" --point "$QUALIFICATION_POINT" --receipt "$NEW_RECEIPT" \
  --original-source "$ORIGINAL_4B" \
  --qualification-attempt "${TASK_ID_1}#attempt-0" \
  --qualification-attempt "${TASK_ID_2}#attempt-3" \
  --dry-run
```

确认配置后省略 `--dry-run` 才实际提交。qualification 配置 root 必须是独立 `/qualification-evaluations` namespace，point 必须为 `qualification.<name>`，attempt 必须来自完整100×4 manifest；实际约束由既有 worker 验证。

正式原始模型 baseline 使用 parent 选择的 baseline point，保留 `--original-source`，省略所有 `--qualification-attempt`。trainer 已入队的 formal HF point 省略 `--original-source` 和 `--qualification-attempt`。所有模式都要求新的 receipt；发现 `.pending` 应由 parent 调查未完成提交，不自动覆盖或重提。

## 4. 最值得关注的 3 点

1. 本地交付完成，27项新增测试和10项已有 policy 测试通过；真实 GPU、native SWE 成绩及平台数字退出码尚未观测。
2. 原始模型只在 worker cloud mount 中借用 `enqueue_baseline`，不变造 formal HF；资格评测只转发显式 slot，结果与 deadline 仍由既有 store/worker 管理。
3. parent 仍需完成 native 配置构造、实际部署与终态/reader/业务输出验收。此适配器不替代 Ticket03 的真实 HF→SWE→cleanup 集成证据。
