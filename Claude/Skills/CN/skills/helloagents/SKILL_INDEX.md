# HelloAGENTS Skill 索引矩阵

本文件用于维护者和主代理快速判断 skill 边界。执行具体流程时仍以各 `SKILL.md` 和其 `references/` 为准。

| Skill | 职责 | 触发条件 | 输入 | 输出 | 依赖 |
|---|---|---|---|---|---|
| `routing` | 命令处理、上下文响应和风险边界判定 | 命令词、等待项回复、风险或授权边界不清 | 用户消息、流程状态、风险因子 | 唯一处理路径或追问 | 无 |
| `analyze` | 需求缺口澄清与现状分析 | 关键需求缺口或用户要求现状分析 | 用户需求、相关文档与代码 | 目标、成功标准、缺口、风险；条件读取 `kb` | 无 |
| `design` | 方案构思与方案包创建 | 明确规划请求、`~plan`/`~auto`，或高风险与架构决策 | 需求分析结果、知识库 | 完整方案包 `why.md`, `how.md`, `task.md`，或轻量 `task.md` | `templates`, `lifecycle` |
| `develop` | 授权范围内的实施、调试与验证 | 改动授权、`~auto`、`~exec`、设计后确认或故障诊断 | 用户请求或方案包、代码库 | 代码/文档改动与验证摘要；有方案包时条件读取 `kb`、`lifecycle`、`qa-review` | 无 |
| `tdd` | 测试驱动质量规则 | 新功能、Bug 修复、行为/API 变更 | 可观察行为、测试入口 | RED/GREEN/REFACTOR/VERIFY 证据或 TDD-EXEMPT | 无 |
| `test` | 显式测试命令 | 用户输入 `~test [scope]` | 指定模块、行为或最近改动 | 测试与验证摘要 | `tdd` |
| `qa-review` | 结构化 QA 证据与归档门禁 | 有方案包或用户要求结构化 QA，验证后准备交付 | 方案包、验证命令、任务完成状态 | `qa-review.json`、P0/P1/P2 门禁 | 无 |
| `verification-before-completion` | 核对完成声明与有效验证证据 | 准备声明完成、修复或验证通过 | 当前变更状态、验证命令和结果 | 证据有效性、准确结论或剩余限制 | 无 |
| `kb` | 知识库创建、同步、审计、领域语言维护 | `~init`、稳定项目知识变化、术语候选沉淀 | 代码事实、方案包场景、领域语言候选 | `project.md`, `wiki/*` 的必要同步；实际创建时条件读取 `templates` | 无 |
| `lifecycle` | 方案包状态、迁移、遗留扫描和流程状态 | 实际创建/执行方案包，或需要记录命令授权与等待项 | 方案包路径、流程状态 | 迁移结果、history 索引、遗留列表 | 无 |
| `templates` | 模板选择入口 | 创建知识库、方案包、版本记录 | 目标文件类型 | 对应 reference 模板 | 无（纯资源入口） |
| `output-format` | 命令完成、异常和交互输出模板 | 命令完成、异常、需要用户选择或确认 | 输出场景、关键变更、验证结果 | 规范模板 | 无 |
| `hello-subagent` | 并行子代理编排 | >=2 个独立可验证子任务且写入互斥 | 子任务边界、验证标准 | 子任务包、汇总验收 | 无 |
| `multi_model` | 多模型审查与交叉验证 | 用户要求，或高风险分析/设计/验收确有独立审查收益 | 方案、代码 diff、审查目标 | 共识/分歧、P0/P1/P2 风险 | 无（按宿主选择 `collaborating-*`） |
| `collaborating-with-claude` | 调用 Claude CLI | 需要 Claude 子进程 | 提示词、SESSION_ID | 结构化调用结果 | 无 |
| `collaborating-with-codex` | 调用 Codex CLI | 需要 Codex 子进程 | 提示词、SESSION_ID | 结构化调用结果 | 无 |
| `collaborating-with-gemini` | 调用 Gemini CLI | 需要 Gemini 子进程 | 提示词、SESSION_ID | 结构化调用结果 | 无 |

## 单一定义

以下规则各只在一处定义，其他 Skill 只引用，不复述:

| 规则 | 定义位置 |
|---|---|
| 写入入口（何时可以改动） | `develop/SKILL.md` 的“入口” |
| 风险三级与处理路径 | `routing/references/risk-and-paths.md` |
| 命令行为与确认条件 | `routing/references/commands-and-context.md` |
| 系统化调试 | `develop/references/debugging.md` |
| P0/P1/P2 归档门禁 | `qa-review/SKILL.md` |
| 证据有效性与复用 | `verification-before-completion/SKILL.md` |
| 流程状态与方案包迁移 | `lifecycle/SKILL.md` |
| 知识库写入收益门禁 | `kb/references/knowledge-base-rules.md` |
| 交互与完成模板 | `output-format/references/` |

## 冲突域速查

- `kb` vs `lifecycle`: `kb` 管内容质量，`lifecycle` 管方案包移动与流程状态。
- `multi_model` vs `hello-subagent`: `multi_model` 管审查观点，`hello-subagent` 管任务编排。
- `develop` vs `qa-review`: `develop` 管执行和验证，`qa-review` 管方案包的结构化质量证据。
- `verification-before-completion` vs `tdd`/`qa-review`: 前者统一判断证据有效性和结论范围，后两者分别管理测试方法和结构化记录；不各自要求重复运行命令。
- `templates` vs 具体阶段 skill: `templates` 只提供模板，阶段 skill 决定何时创建和如何填充。

`requires` 仅表示加载前必须满足的硬依赖，必须形成 DAG；正文中的“读取某 Skill”表示条件性按需依赖，不得反向写入 `requires` 形成环。

## 维护门禁

- `skills/helloagents/` 是唯一手工维护的 Skill 源；禁止直接修改 Codex/Claude 分发树。
- 修改 canonical Skill 或根 bridge 后运行 `python scripts/sync_skills.py --write`，并用 `--check` 确认无漂移。
- 新增 skill 必须补充本索引矩阵。
- 新增 frontmatter 字段必须同步更新审计脚本。
- `Codex/Skills/CN/skills/helloagents` 与 `Claude/Skills/CN/skills/helloagents` 是生成分发副本，必须与 canonical 源完全一致。
