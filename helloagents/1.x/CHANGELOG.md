# Changelog

本文件记录项目所有重要变更。
格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- 新增 36 条 Skill 路由 eval 用例、`scripts/eval_skills.py` 数据校验与实际结果评分器，覆盖八类任务和确认误差指标
- 新增 `~test [scope]` 受控测试入口和 `test` Skill，支持轻量测试方案包、TDD 分类及默认不扩大为生产修复的边界
- 新增 QA schema v3 的结构化 `tdd` 证据与审计回归测试，校验 RED/GREEN/REFACTOR/VERIFY 或 TDD-EXEMPT 原因和替代验证
- 新增 `scripts/manage_skills.py`，支持只读安装漂移检查和带备份的原子安装
- 新增审计回归测试与 Windows/Linux GitHub Actions，覆盖状态机、轻量包、安全扫描、bridge 和分发契约
- collaborating Skill 内新增自包含 `scripts/bridge.py` bundled resource
- 新增 `qa-review` Skill，用于开发实施交付前记录 QA 证据、验证命令、阻断项分级和任务完成核对
- 新增 `scripts/audit_safety.py` 只读安全审计脚本，扫描危险命令、密钥形态和高风险依赖脚本
- 新增 `wiki/glossary.md` 领域语言文档，用于沉淀项目术语、同义词/禁用叫法和术语状态
- 新增 `skills/helloagents/SKILL_INDEX.md` 索引矩阵，集中记录 skill 职责、触发条件、输入输出、依赖和冲突域
- 新增 `scripts/audit_skills.py` 只读审计脚本，校验 frontmatter、reference 引用、Codex/Claude 镜像一致性、bootstrap 索引指针和关键语义契约
- 新增知识库最小文档: `project.md`、`wiki/overview.md`、`wiki/arch.md`、`wiki/api.md`、`wiki/data.md`、`wiki/modules/skills.md`
- 新增按需触发的 Skill: `output-format`、`routing`、`lifecycle`、`qa-review` 等；当前维护 Codex/Claude 两端 CN skill 镜像

### 变更
- Codex/Claude bootstrap 从 268 行精简到 120 行以内，只保留稳定原则、安全边界、自适应路由、命令入口和 Skill 索引
- 普通 Bug 与低/中风险小改动改为基于可逆性、外部副作用、公共契约、数据迁移、EHRB 和不确定性的自适应路由，用户明确授权后无需方案包或二次确认即可实施并验证
- develop、QA、KB 与 lifecycle 增加无方案包自适应分支，高风险/EHRB、破坏性契约和真实数据迁移仍保留方案确认门禁
- `qa-review.json` 新生成记录升级为 schema v3；`audit_skills.py` 保持 v1/v2 兼容并新增 TDD 证据门禁
- QA 证据升级为 schema v2，新增 P0/P1/P2 处置状态与 `gate_status`，P0 不可跳过、P1 必须显式接受风险后才能归档
- 归档路径在 KB/CHANGELOG 写链接前解析为 `RESOLVED_ARCHIVE_PATH`，并补齐 `~exec`、测试失败、多模型验收、部分失败等等待态消费路径
- bridge read-only 改用 Claude/Gemini 原生 plan 权限模式；持续输出不能绕过超时，超时终止进程树，非零退出和 fatal 事件始终判失败
- `manage_skills.py` 增加 bootstrap 文件名/仓库边界校验和 Skill+bootstrap 联合回滚；标准检查命令同时校验 bootstrap 漂移
- frontmatter 与 QA JSON 审计增加类型、枚举、任务覆盖校验；安全审计补充 `~~~` fence、变量常量传播和 subprocess 导入别名
- 命令授权改为绑定 `WORKFLOW_ID`，补齐全部等待交互态，并在所有终态统一执行 `RESET_WORKFLOW_STATE`
- 轻量方案包增加范围、核心场景、知识库同步、ADR 和验证策略元数据，develop/QA/KB 使用统一分支
- history 迁移改为 no-clobber；多模型验收移至归档前，P0/P1 阻止未闭环方案归档
- 多模型协作增加数据出境、secret/PII、宿主感知模型组合和工作区零写入门禁
- bridge 默认使用有界超时，Gemini 默认 sandbox，Claude read-only 禁止 Bash/Edit/Write，并保留 Windows 多行提示词
- Skill 审计增加严格 frontmatter、普通 Markdown 链接、依赖 DAG、bundled bridge 与关键状态不变量检查
- 安全审计增加 Markdown shell fenced block 和 Python AST 进程命令扫描
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
- ADR-005: 使用显式状态机和工作流标识替代跨任务隐式布尔授权
- ADR-006: bridge 作为 collaborating Skill bundled resource 自包含分发
