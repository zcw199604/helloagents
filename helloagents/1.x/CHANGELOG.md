# Changelog

本文件记录项目所有重要变更。
格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- 新增 `wiki/glossary.md` 领域语言文档，用于沉淀项目术语、同义词/禁用叫法和术语状态
- 新增 `skills/helloagents/SKILL_INDEX.md` 索引矩阵，集中记录 skill 职责、触发条件、输入输出、依赖和冲突域
- 新增 `scripts/audit_skills.py` 只读审计脚本，校验 frontmatter、reference 引用、Codex/Claude 镜像一致性和 bootstrap 索引指针
- 新增知识库最小文档: `project.md`、`wiki/overview.md`、`wiki/arch.md`、`wiki/api.md`、`wiki/data.md`、`wiki/modules/skills.md`
- 新增 4 个按需触发的 Skill: `output-format`（G6.1-G6.4 输出模板集合）、`routing`（路由细节）、`lifecycle`（G11/G12 方案包生命周期与状态变量）、`windows-shell`（Windows PowerShell 语法约束）；CN/EN × Codex/Claude 共 16 个 SKILL.md
- 在 4 份 bootstrap 入口的 Skills 引用表中新增上述 4 个 Skill

### 变更
- 修复多处高价值规则冲突: 标准开发必须经过轻量需求分析、系统化调试增加只读入口、`~plan` 自动规划不再被多模型询问打断、开发实施确认条件改为基于方案包状态、阻断性测试失败在所有模式下停止、开发实施前置读取 `how.md`
- 明确多模型审查输出契约，区分风险报告与 unified diff patch 建议
- 统一 ADR 数据模型，补齐 `状态` 字段并同步 `wiki/arch.md`、CHANGELOG 与历史方案包
- 增强 `scripts/audit_skills.py`，增加索引覆盖、frontmatter 值、依赖存在性、reference 内部链接、bootstrap 镜像和换行归一化校验
- 吸收 `grill-with-docs` 核心机制：需求分析增加领域语言识别和文档化追问，方案设计增加 ADR 候选识别，知识库同步增加术语表维护
- 将大型 `SKILL.md` 拆为轻量入口 + `references/` 渐进披露结构，覆盖 `templates`、`output-format`、`routing`、`develop`、`design`、`kb`、`hello-subagent`
- 为所有 HelloAGENTS skill 统一补充 `invocation`、`side_effects`、`requires`、`completion_criteria` 元数据
- 为 `routing`、`templates`、`output-format`、`develop`、`design`、`kb`、`lifecycle`、`multi_model`、`hello-subagent`、`tdd` 补充正反例或完成门禁
- 明确 `kb` 与 `lifecycle`、`multi_model` 与 `hello-subagent`、`develop` 与 `output-format` 的职责边界
- 重写 4 份 bootstrap 入口（`Codex/Skills/CN/AGENTS.md`、`Claude/Skills/CN/CLAUDE.md`、`Codex/Skills/EN/AGENTS.md`、`Claude/Skills/EN/CLAUDE.md`），由 1065 行精简至 266 行（约 75% 缩减），仅保留角色定义、最小路由决策树、阶段触发表、Skill 引用表与核心全局约束（G1-G12 简版）
- bootstrap 中 G6.1-G6.4 输出格式模板、G11 方案包生命周期、G12 状态变量、路由机制详细规则、Windows PowerShell 语法约束、命令完成输出格式全部下沉至对应新 Skill
- 明确现有 Skill 中的 G6/G11 跨引用指向 `output-format` / `lifecycle` Skill，避免精简入口后仍隐式依赖 bootstrap 内联锚点
- 收紧 `routing` Skill 的标准开发、完整研发和上下文响应规则，普通追问/方案选择/阶段确认只能推进到方案设计和方案包创建，进入开发实施必须满足显式确认、全授权命令或执行命令入口
- 收紧 `routing` Skill 的系统化调试出口与微调模式条件：调试类改动必须产出方案包，禁止从系统化调试降级到微调；微调模式条件新增"调试信号=无"硬门禁（4 份 routing/SKILL.md 同步对齐）

### 移除
- bootstrap 入口中移除上述已下沉的细节段落

### 架构决策
- ADR-001: 不引入 `_shared/` 共享机制，维持 4 份独立入口；解决双份维护问题留待后续优化
- ADR-002: 抽取 `routing` Skill 但 bootstrap 保留最小路由决策树，避免常驻读取
- ADR-003: 大型 `SKILL.md` 拆为轻量入口 + `references/`
- ADR-004: 吸收 `grill-with-docs` 机制而非新增独立流程
