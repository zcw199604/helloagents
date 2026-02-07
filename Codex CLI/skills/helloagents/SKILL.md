---
name: helloagents
description: "【HelloAGENTS】显式调用入口。使用 /helloagents 或 $helloagents 激活。"
license: Apache-2.0
metadata:
  author: helloagents
  version: "2.0"
---

# HelloAGENTS 技能入口

> 本文件在用户显式调用技能时加载（/helloagents 或 $helloagents）。
> 核心规则在主配置中定义，本文件定义显式调用时的响应规则。

**路径基准:** `SKILL_ROOT: skills/helloagents/` — 本文件及子模块中的相对路径（references/、scripts/、assets/）需添加此前缀。

---

## 显式调用响应规则

当用户通过 `/helloagents` 或 `$helloagents` 显式调用本技能时，输出以下欢迎信息：

```
💡【HelloAGENTS】- 技能已激活

智能工作流系统，提供结构化任务流程。

### 可用命令

| 命令 | 功能 |
|------|------|
| `~auto` | 全授权命令 |
| `~plan` | 执行到方案设计 |
| `~exec` | 执行方案包 |
| `~init` | 初始化知识库 |
| `~upgrade` | 升级知识库 |
| `~clean` | 清理遗留方案包 |
| `~commit` | Git 提交 |
| `~test` | 运行测试 |
| `~review` | 代码审查 |
| `~validate` | 验证知识库 |
| `~rollback` | 智能回滚 |
| `~help` | 显示帮助 |

### 使用方式

- 输入 `~命令` 执行特定功能
- 直接描述需求，系统自动路由到合适的流程

────
🔄 下一步: 输入命令或描述你的需求
```

**后续输入处理：** 用户输入后，按照 G4 路由架构处理。

---

## 脚本调用约定

> 脚本调用规范（路径变量、存在性检查、错误恢复）见 references/rules/tools.md

脚本位于 scripts/ 目录，调用时使用 `-X utf8` 确保编码正确：

```yaml
知识库工具: python -X utf8 "scripts/upgradewiki.py" --scan | --init | --backup | --write <plan.json>
方案包验证: python -X utf8 "scripts/validate_package.py" [<package-name>]
方案包创建: python -X utf8 "scripts/create_package.py" "<feature>" [--type <implementation|overview>]
方案包迁移: python -X utf8 "scripts/migrate_package.py" "<package-name>" [--status <completed|skipped>] [--all]
方案包列表: python -X utf8 "scripts/list_packages.py" [--format <table|json>]
项目统计: python -X utf8 "scripts/project_stats.py" [--path <项目路径>]
多模型委托-Codex: python -X utf8 "scripts/codex_bridge.py" --cd "<项目路径>" --PROMPT "<任务描述>" [--sandbox <read-only|workspace-write|danger-full-access>] [--SESSION_ID <id>] [--return-all-messages]
多模型委托-Gemini: python -X utf8 "scripts/gemini_bridge.py" --cd "<项目路径>" --PROMPT "<任务描述>" [--sandbox] [--SESSION_ID <id>] [--return-all-messages]
多模型委托-Claude: python -X utf8 "scripts/claude_bridge.py" --cd "<项目路径>" --PROMPT "<任务描述>" [--sandbox <read-only|workspace-write|danger-full-access>] [--SESSION_ID <id>] [--return-all-messages]
多模型协作分析流程: 先通过 subagent 并行执行 Claude + Gemini 交叉验证，存在冲突时追加 Codex 仲裁（详见 references/rules/multi_model.md）
```

---

## 模板资源

模板位于 assets/templates/ 目录，结构与知识库一致：

```yaml
assets/templates/
  - INDEX.md              # 知识库入口
  - context.md            # 项目上下文
  - CHANGELOG.md          # 变更日志
  - CHANGELOG_{YYYY}.md   # 年度变更日志（大型项目）
  - modules/_index.md     # 模块索引
  - modules/module.md     # 模块文档
  - plan/proposal.md      # 变更提案
  - plan/tasks.md         # 任务清单
  - archive/_index.md     # 归档索引
```
