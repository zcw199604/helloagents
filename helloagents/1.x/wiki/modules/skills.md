# Skills 模块

## 目的

维护 HelloAGENTS 的模块化 skill 体系，降低入口上下文负载，减少职责重叠，并从 canonical 源生成 Codex/Claude 分发副本。

## 规范

### 自适应默认流程

- 普通自然语言改动请求按低/中/高风险路由，文件数量只作为范围和验证成本线索。
- 低风险直接实施；中风险先形成简短内部计划后连续实施；高风险先方案设计并在写入前确认。
- 用户明确要求修复普通 Bug 时，先复现与定位根因；低/中风险可直接补测试、最小修复和验证。
- 自适应无方案包路径不生成孤立 `qa-review.json` 或 history 记录，实际验证命令与结果写入最终摘要。
- EHRB、生产、真实数据、权限、支付、不可逆操作、破坏性公共契约和数据迁移仍保持高风险门禁。

- 风险等级是当前请求的动态判断，不引入 Light/Heavy 持久模式变量；出现新证据时直接升降风险路径。

### 输出与知识写入

- 普通咨询直接回答，自适应低/中风险路径的分析与内部设计默认静默连续执行。
- 正式命令、异常、高风险确认和多选交互才强制使用带 `【HelloAGENTS】` 的模板。
- 写入交付始终说明结果、关键文件、实际验证和剩余风险，但不强制固定栏目或无意义的下一步。
- 知识库默认不写；只有代码无法表达、未来会复用且缺失会导致错误判断的稳定信息才最小同步。

### Canonical 源与生成分发

- `skills/helloagents/` 是唯一手工维护的 Skill 源。
- `scripts/claude_bridge.py`、`scripts/codex_bridge.py`、`scripts/gemini_bridge.py` 是 bridge 权威源。
- `python scripts/sync_skills.py --write` 先刷新 canonical Skill 的 bundled bridge，再生成 Codex/Claude 分发树。
- `python scripts/sync_skills.py --check`、`audit_skills.py` 和 CI 共同阻止直接修改生成物或遗漏同步。

### 轻量入口

`SKILL.md` 应优先保留:
- frontmatter 元数据
- 目标
- 触发条件或流程索引
- 职责边界
- 正反例
- 完成门禁

长模板、协议、输出样例和细则应移动到 `references/`。

### 索引矩阵

`skills/helloagents/SKILL_INDEX.md` 是 skill 职责、触发、输入输出和依赖的维护索引。新增或改名 skill 时必须同步更新。

### 审计

修改 skill 后运行:

```bash
python scripts/sync_skills.py --write
python scripts/sync_skills.py --check
python scripts/audit_skills.py
```

### 行为 Eval

`evals/skill_routing_cases.json` 保存代表性提示及预期路由、动作、确认策略、过程产物和风险等级。当前基线至少覆盖咨询、微调、普通 Bug、小改动、中等变更、高风险、命令和上下文八类场景。

```bash
python scripts/eval_skills.py
python -m unittest tests.test_skill_evals -v
```

外部运行器可输出顶层包含 `results` 列表的 JSON，再使用 `python scripts/eval_skills.py --results <path>` 计算路由、动作、确认、产物和风险准确率，以及不必要确认率和漏确认率。

审计通过表示:
- frontmatter 字段、类型和重复键合法。
- `references/*.md` 及普通 Markdown 文件链接存在。
- `requires` 依赖图无环。
- canonical Skill 源与 Codex/Claude 生成分发树内容一致。
- canonical 和两端分发的 bundled bridge 与根脚本一致。
- bootstrap 入口包含索引矩阵指针。
- 命令别名、开发实施步骤数、任务元数据、QA 证据和安全审计脚本等语义契约一致。

涉及安全规则、命令示例或脚本变更时运行:

```bash
python scripts/audit_safety.py
```

安全审计覆盖:
- 脚本和配置文件中的危险 shell 命令、高风险发布/部署/迁移命令。
- Markdown 可执行 shell fenced block 和 Python 常量 subprocess/os 命令。
- 常见密钥、私钥、数据库连接串和 token 形态。
- `package.json` 中危险生命周期脚本。
- `.env`、`.npmrc`、`Dockerfile`、`Makefile`、`.properties` 等常见文本配置文件。

### QA 证据

`qa-review` Skill 在步骤7质量检查与测试完成后、交付前读取，用于在当前方案包中写入 `qa-review.json`。新记录使用 schema v3，并在 `tdd` 中保存分类、决策、目标行为和阶段结果；历史 v1/v2 记录继续可读。该文件记录:
- QA 模式、审查范围和结论。
- 实际运行的验证命令及结果。
- 阻断项、警告项和信息项。
- `task.md` 已完成任务的逐项核对证据。
- P0/P1/P2 的 `severity/status` 和可执行 `gate_status`；P0 不允许风险接受，P1 默认阻止归档。
- `decision=tdd` 时的 RED 失败、GREEN/REFACTOR/VERIFY 通过，或 `decision=exempt` 时的原因与替代验证。

### 显式测试入口

`~test [scope]` 读取 `test` Skill，为指定模块、行为或最近改动补齐测试。它会创建或复用轻量测试方案包，并复用现有开发实施和 QA 门禁。

- 默认只修改测试、测试数据、方案包和 QA 证据。
- 新功能或可复现缺陷走 TDD；已实现行为的表征测试必须以 `TDD-EXEMPT` 说明无法构造真实 RED 的原因。
- 测试发现生产缺陷时，记录失败并进入常规方案设计，不自动修改生产代码。

方案包迁移到 `history/` 时，`qa-review.json` 随方案包一起归档。

### 运行时状态与轻量方案包

- 特殊命令授权绑定 `WORKFLOW_ID`；成功、取消、错误和终止统一执行 `RESET_WORKFLOW_STATE`。
- 交互回复只由 `PENDING_INTERACTION` 消费一次，不再根据上一条文本猜测状态。
- 用户明确授权的低/中风险普通改动不需要方案包或二次确认；需要恢复执行或审计时仍可创建轻量方案包。
- 轻量方案包必须在 `task.md` 中包含范围、核心场景、知识库同步、ADR 和验证策略；QA 和 KB 使用该元数据分支。
- history 迁移采用 no-clobber，冲突时增加 `_v2/_v3`，禁止覆盖旧审计证据。
- no-clobber 目标在知识库写链接前保存为 `RESOLVED_ARCHIVE_PATH`，链接、索引、迁移与最终输出保持一致。

### 外部协作与分发

- 多模型调用前执行 secret/PII/商业敏感信息门禁，默认最小上下文和 sandbox/read-only。
- bridge 默认 600 秒超时，持续输出也受 deadline 限制；超时终止进程树，并作为 `collaborating-*` Skill bundled resource 分发。
- Claude/Gemini 审查使用原生 plan 权限模式；任何 fatal 事件或非零退出均不能因部分输出而视为成功。
- `manage_skills.py` 始终从 canonical Skill 源安装；`--check` 同时检测 Skill 与 bootstrap 漂移，`--install` 校验目标后联合安装，bootstrap 失败会回滚 Skill 树。

### 文档化追问

需求分析阶段遇到项目黑话、缩写、业务角色、状态名、流程名或命名分歧时，先追问术语含义、边界、反例和推荐命名。确认后的术语沉淀到 `wiki/glossary.md`。

### ADR 候选

方案设计阶段如果出现模块边界、接口契约、数据边界、依赖方向、命名体系或迁移策略取舍，应在 `how.md` 中记录 ADR 候选。没有实际取舍时，明确写明本次无 ADR 候选。

## 变更历史

| 日期 | 变更 |
|---|---|
| 2026-07-02 | 拆薄大型 skill、补索引矩阵、统一元数据、增加审计脚本 |
| 2026-07-02 | 吸收 grill-with-docs 核心机制：领域语言、文档化追问、ADR 候选 |
| 2026-07-02 | 修复交叉审查发现的高价值 P1/P2 规则冲突并增强审计脚本 |
| 2026-07-03 | 吸收外部 main 的 QA 证据、任务可验证性、语义审计和安全扫描机制 |
| 2026-07-03 | 修复命令模式变量、系统化调试只读入口和 `history/index.md` 初始化规则 |
| 2026-07-03 | 调整需求低分门禁，允许只读代码勘察澄清需求但禁止直接进入方案设计 |
| 2026-07-03 | 修复 6 处规则矛盾与 3 处遗留悬空: 统一验收输出契约、规划命令审查询问、轻量迭代方案包标注、中文阶段名替换 P1/P2/P3 代号、multi_model 旧术语清理、委派协议章节重编号 |
| 2026-07-11 | 加固状态授权、轻量包、归档、多模型安全和 bridge 分发，新增语义回归测试与跨平台 CI |
| 2026-07-11 | 吸收第二轮并行复审：补 QA 可执行门禁、归档路径解析、真实只读 bridge、进程树超时、安装联合回滚和严格 schema 审计 |
| 2026-07-15 | 新增 36 条路由 eval 基线与评分器，精简 bootstrap，并将普通 Bug/小改动切换为风险自适应路由 |
| 2026-08-23 | 收敛 canonical Skill 单一源与生成分发，减轻输出包装，并为知识库增加默认不写的收益门禁 |
