# Changelog

本文件记录项目所有重要变更。
格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- 新增 `qa-review` Skill，用于开发实施交付前记录 QA 证据、验证命令、阻断项分级和任务完成核对
- 新增 `scripts/audit_safety.py` 只读安全审计脚本，扫描危险命令、密钥形态和高风险依赖脚本
- 新增 `wiki/glossary.md` 领域语言文档，用于沉淀项目术语、同义词/禁用叫法和术语状态
- 新增 `skills/helloagents/SKILL_INDEX.md` 索引矩阵，集中记录 skill 职责、触发条件、输入输出、依赖和冲突域
- 新增 `scripts/audit_skills.py` 只读审计脚本，校验 frontmatter、reference 引用、Codex/Claude 镜像一致性、bootstrap 索引指针和关键语义契约
- 新增知识库最小文档: `project.md`、`wiki/overview.md`、`wiki/arch.md`、`wiki/api.md`、`wiki/data.md`、`wiki/modules/skills.md`
- 新增按需触发的 Skill: `output-format`、`routing`、`lifecycle`、`qa-review` 等；当前维护 Codex/Claude 两端 CN skill 镜像

### 变更
- 修复 skills 规则矛盾: 步骤13多模型验收统一为"Risk report only"契约、规划命令不再触发多模型审查询问（以 output-and-transition.md 为准）、轻量迭代简化方案包通过 `task.md` 顶部 `模式: 轻量迭代` 标注合法化（routing/kb/develop/G2 四处对齐）、轻量迭代流程补充 CHANGELOG 更新步骤、CURRENT_PACKAGE 清理时机修正为迁移后按 G12 清除
- 清理 skills 遗留悬空引用: P1/P2/P3 阶段代号统一改为中文阶段名（保留 P0/P1/P2 风险分级）、`p3_entry_gate` 改名 `develop_entry_gate`、multi_model 移除 R1/R2/Phase2-4/TASK_COMPLEXITY 旧术语并将 PHASE2_HARD_STOP_CONFIRM 更名为 DESIGN_HARD_STOP_CONFIRM（补默认值说明）、hello-subagent 委派协议章节重编号为 1-10、模板中本仓库专属审计命令泛化为占位符+本仓库示例
- 调整需求分析低分门禁: 移除“以现有需求继续”直接进入阶段B，改为用户明确要求时仅允许只读需求澄清勘察，勘察后重新评分
- 修复 skills 规则交接问题: 命令确认会设置 `MODE_FULL_AUTH`/`MODE_EXECUTION`，系统化调试只读入口可绕过方案包强制读取，知识库初始化纳入 `history/index.md`
- 修复 QA/安全审查吸收后的契约问题: `audit_safety.py` 默认仓库扫描覆盖脚本/配置中的危险命令，补扫 `.env`、`.npmrc`、`Dockerfile`、`Makefile` 等常见文本文件；`task.md` 的 TDD VERIFY 不再依赖 `qa-review.json`
- 增强 `scripts/audit_skills.py`，新增实际步骤标题、任务块元数据、`qa-review` 触发文案和 `SKILL_INDEX.md` 依赖列审计
- 吸收外部 main 的 QA 证据机制、任务可验证性字段和安全扫描规则，但保留本地 `why.md` + `how.md` + `task.md` 方案包结构
- `task.md` 模板要求每个可执行任务包含执行模式、涉及文件、完成标准和验证方式，支持 AFK/HITL 分工
- 开发实施步骤7后新增 QA 证据记录要求，方案包迁移时将 `qa-review.json` 一并归档
- 增强 `scripts/audit_skills.py`，新增命令别名同步、开发实施步骤数、任务元数据、QA 证据和安全审计脚本语义检查
- 修复多处高价值规则冲突: 标准开发必须经过轻量需求分析、系统化调试增加只读入口、`~plan` 自动规划不再被多模型询问打断、开发实施确认条件改为基于方案包状态、阻断性测试失败在所有模式下停止、开发实施前置读取 `how.md`
- 明确多模型审查输出契约，区分风险报告与 unified diff patch 建议
- 统一 ADR 数据模型，补齐 `状态` 字段并同步 `wiki/arch.md`、CHANGELOG 与历史方案包
- 增强 `scripts/audit_skills.py`，增加索引覆盖、frontmatter 值、依赖存在性、reference 内部链接、bootstrap 镜像和换行归一化校验
- 吸收 `grill-with-docs` 核心机制：需求分析增加领域语言识别和文档化追问，方案设计增加 ADR 候选识别，知识库同步增加术语表维护
- 将大型 `SKILL.md` 拆为轻量入口 + `references/` 渐进披露结构，覆盖 `templates`、`output-format`、`routing`、`develop`、`design`、`kb`、`hello-subagent`
- 为所有 HelloAGENTS skill 统一补充 `invocation`、`side_effects`、`requires`、`completion_criteria` 元数据
- 为 `routing`、`templates`、`output-format`、`develop`、`design`、`kb`、`lifecycle`、`multi_model`、`hello-subagent`、`tdd` 补充正反例或完成门禁
- 明确 `kb` 与 `lifecycle`、`multi_model` 与 `hello-subagent`、`develop` 与 `output-format` 的职责边界
- 重写 CN bootstrap 入口（`Codex/Skills/CN/AGENTS.md`、`Claude/Skills/CN/CLAUDE.md`），仅保留角色定义、最小路由决策树、阶段触发表、Skill 引用表与核心全局约束（G1-G12 简版）
- bootstrap 中 G6.1-G6.4 输出格式模板、G11 方案包生命周期、G12 状态变量、路由机制详细规则和命令完成输出格式下沉至对应 Skill
- 明确现有 Skill 中的 G6/G11 跨引用指向 `output-format` / `lifecycle` Skill，避免精简入口后仍隐式依赖 bootstrap 内联锚点
- 收紧 `routing` Skill 的标准开发、完整研发和上下文响应规则，普通追问/方案选择/阶段确认只能推进到方案设计和方案包创建，进入开发实施必须满足显式确认、全授权命令或执行命令入口
- 收紧 `routing` Skill 的系统化调试出口与微调模式条件：调试类改动必须产出方案包，禁止从系统化调试降级到微调；微调模式条件新增"调试信号=无"硬门禁（4 份 routing/SKILL.md 同步对齐）

### 移除
- bootstrap 入口中移除上述已下沉的细节段落
- 移除独立 EN skill set 和独立 `windows-shell` Skill 后，当前 CN 入口改由通用安全规则和 `audit_safety.py` 覆盖 PowerShell 风险检查

### 架构决策
- ADR-001: 不引入 `_shared/` 共享机制，维持 4 份独立入口；解决双份维护问题留待后续优化
- ADR-002: 抽取 `routing` Skill 但 bootstrap 保留最小路由决策树，避免常驻读取
- ADR-003: 大型 `SKILL.md` 拆为轻量入口 + `references/`
- ADR-004: 吸收 `grill-with-docs` 机制而非新增独立流程
