# HelloAGENTS Skill 索引矩阵

本文件用于维护者和主代理快速判断 skill 边界。执行具体流程时仍以各 `SKILL.md` 和其 `references/` 为准。

| Skill | 职责 | 触发条件 | 输入 | 输出 | 依赖 |
|---|---|---|---|---|---|
| `routing` | 判定用户消息处理路径 | 命令词、上下文确认、调试信号、复杂边界 | 用户消息、当前阶段状态 | 唯一路由或追问 | `output-format` |
| `analyze` | 需求完整性评分与现状分析 | 进入需求分析 | 用户需求、知识库、代码现状 | 评分、缺口、风险、下一阶段建议 | `kb`, `output-format` |
| `design` | 方案构思与方案包创建 | 需求评分 >= 7 或规划命令 | 需求分析结果、知识库 | `why.md`, `how.md`, `task.md` | `templates`, `lifecycle`, `output-format` |
| `develop` | 执行方案包并验证 | 用户确认、`~auto` 或 `~exec` | 方案包、代码库、知识库 | 代码/文档改动、验证结果、历史迁移 | `kb`, `lifecycle`, `output-format`, `qa-review` |
| `tdd` | 测试驱动质量门禁 | 新功能、Bug 修复、行为/API 变更 | 可观察行为、测试入口 | RED/GREEN/REFACTOR/VERIFY 证据 | 无（由阶段 Skill 按需读取） |
| `test` | 显式测试命令 | 用户输入 `~test [scope]` | 指定模块、行为或最近改动 | 测试范围、TDD 决策、QA 证据 | `tdd`, `develop` |
| `qa-review` | 统一质量审查与 QA 证据记录 | 开发实施验证完成、交付前收口 | 方案包、验证命令、任务完成状态 | `qa-review.json`、阻断项分级、验证摘要 | 无 |
| `kb` | 知识库创建、同步、审计、领域语言维护 | `~init`、知识库缺失、代码变更后同步、术语候选沉淀 | 代码事实、方案包场景、领域语言候选 | `project.md`, `wiki/*`, `wiki/glossary.md` 同步建议 | `templates` |
| `lifecycle` | 方案包状态、迁移、遗留扫描 | 方案包创建/执行/阶段完成 | 方案包路径、状态变量 | 迁移结果、history 索引、遗留列表 | `output-format` |
| `templates` | 模板选择入口 | 创建知识库、方案包、版本记录 | 目标文件类型 | 对应 reference 模板 | 无（纯资源入口） |
| `output-format` | 用户可见输出模板 | 阶段完成、异常、咨询、交互、命令完成 | 输出场景、变更清单、验证结果 | 规范化 HelloAGENTS 输出 | 无 |
| `hello-subagent` | 并行子代理编排 | >=2 个独立可验证子任务且写入互斥 | 子任务边界、验证标准 | 子任务包、汇总验收 | `output-format` |
| `multi_model` | 多模型审查与交叉验证 | 用户要求或高风险分析/设计/验收 | 方案、代码 diff、审查目标 | 共识/分歧、P0/P1/P2 风险 | 无（按宿主选择 `collaborating-*`） |
| `collaborating-with-claude` | 调用 Claude CLI | 需要 Claude 子进程 | 提示词、SESSION_ID | 结构化调用结果 | 无 |
| `collaborating-with-codex` | 调用 Codex CLI | 需要 Codex 子进程 | 提示词、SESSION_ID | 结构化调用结果 | 无 |
| `collaborating-with-gemini` | 调用 Gemini CLI | 需要 Gemini 子进程 | 提示词、SESSION_ID | 结构化调用结果 | 无 |

## 冲突域速查

- `kb` vs `lifecycle`: `kb` 管内容质量，`lifecycle` 管方案包移动与状态。
- `multi_model` vs `hello-subagent`: `multi_model` 管审查观点，`hello-subagent` 管任务编排。
- `develop` vs `output-format`: `develop` 管执行字段，`output-format` 管渲染模板。
- `develop` vs `qa-review`: `develop` 管执行和集成，`qa-review` 管交付前质量证据。
- `templates` vs 具体阶段 skill: `templates` 只提供模板，阶段 skill 决定何时创建和如何填充。

`requires` 仅表示加载前必须满足的硬依赖，必须形成 DAG；正文中的“读取某 Skill”表示条件性按需依赖，不得反向写入 `requires` 形成环。

## 维护门禁

- 新增 skill 必须补充本索引矩阵。
- 新增 frontmatter 字段必须同步更新审计脚本。
- `Codex/Skills/CN` 与 `Claude/Skills/CN` 的 skill 内容必须保持一致，除非显式记录平台差异。
