# 变更提案: 精简 HelloAGENTS bootstrap 文档（激进重构）

## 需求背景

当前 4 份 bootstrap 文档（Codex/Claude × CN/EN）各 1065 行，每次会话被全量加载进上下文，挤占工作记忆且双份维护成本高。同时存在以下问题：

- **职责越界**：bootstrap 同时承担角色定义、全局规则、输出模板、路由细节、阶段骨架、命令完成格式 6 类内容，单文件过载。
- **重复内容**：G6.1-G6.4 输出模板（约 260 行）、G11/G12 方案包生命周期（约 64 行）、路由细节（约 210 行）等大块内容可下沉到按需触发的 Skill。
- **跨平台冗余**：Windows PowerShell 语法约束（约 30 行）应按平台触发，无需常驻入口。
- **维护漂移风险**：4 份文件需逐一同步，已观察到细微措辞漂移可能。

驱动因素：用户在前置咨询中明确要求评估并精简，并选择「方案 2 - 激进重构」（入口 ≤ 250 行 + 抽取 4 个新 Skill + 更新跨引用）。

## 变更内容

1. 新建 4 个按需触发的 Skill：`output-format`、`routing`、`lifecycle`、`windows-shell`
2. 将 G6.1-G6.4、G11、G12、路由机制详细规则、特殊命令完成输出格式、阶段骨架细节下沉到对应 Skill
3. 重写 4 份 bootstrap 入口至 ≤ 250 行，仅保留：角色定义、最小路由决策树、Skill 引用表、G1（精简）/G2/G3/G5/G9 等核心约束、阶段骨架触发表
4. 更新现有 Skills（analyze/design/develop/kb/templates/tdd/hello-subagent/multi_model）中对 G6/G10/G11/G12 的跨引用，指向新 Skill 路径
5. 在 Skill 引用表新增 4 个 Skill 条目

## 范围边界

- **范围内**：
  - `Codex/Skills/CN/AGENTS.md`、`Claude/Skills/CN/CLAUDE.md`、`Codex/Skills/EN/AGENTS.md`、`Claude/Skills/EN/CLAUDE.md` 4 份入口文档精简
  - 4 个新 Skill 文件创建（各 CN/EN × Codex/Claude = 4 副本，共 16 个 SKILL.md）
  - 现有 Skill 跨引用更新（analyze/design/develop/kb/templates/tdd/hello-subagent/multi_model，各 CN/EN × Codex/Claude）
- **范围外**：
  - 不修改 Skill 的功能内容，仅更新跨引用路径
  - 不引入 `_shared/` 共享文件机制（属于方案 3 共享化重构，已被否决）
  - 不重写阶段执行逻辑、路由决策算法、EHRB 识别规则等业务逻辑
- **拆分说明**：本次按"激进重构"一次性完成，不再拆分；若执行中发现影响过大可回退到方案 1（温和精简）。

## 影响范围

- **模块**：HelloAGENTS bootstrap 文档体系、Skills 注册体系
- **文件**：
  - 修改：4 份 bootstrap 入口
  - 新增：16 个 SKILL.md（4 新 Skill × 4 路径组合）
  - 更新跨引用：约 32 个现有 SKILL.md
- **API**：Skill 触发名（新增 `output-format` / `routing` / `lifecycle` / `windows-shell`）
- **数据**：无

## 核心场景

### 需求: 入口文档轻量化
**模块:** bootstrap

#### 场景: 会话启动加载 bootstrap
- 单份入口 ≤ 250 行
- 包含完整角色定义、路由决策树、Skill 引用表
- 不需要读取额外 Skill 即可完成基本路由判定

### 需求: 输出格式按需加载
**模块:** output-format Skill

#### 场景: 进入阶段完成 / 异常 / 咨询 / 交互输出时
- 触发读取 `output-format` Skill
- 提供 G6.1-G6.4 完整模板（统一输出、异常输出、咨询输出、交互输出）

### 需求: 路由细节按需加载
**模块:** routing Skill

#### 场景: 复杂边界路由判定（如评分边界、EHRB 模糊、模式升级）
- 触发读取 `routing` Skill
- 提供评估维度、决策原则、上下文响应规则、命令路径详细定义

### 需求: 方案包生命周期按需加载
**模块:** lifecycle Skill

#### 场景: 创建方案包 / 迁移方案包 / 扫描遗留方案
- 触发读取 `lifecycle` Skill
- 提供 G11 方案包生命周期规则、G12 状态变量管理

### 需求: 平台特定规则按需加载
**模块:** windows-shell Skill

#### 场景: Platform=win32 且需要使用 shell 命令
- 触发读取 `windows-shell` Skill
- 提供 PowerShell 编码规则与语法约束

### 需求: 跨引用一致性
**模块:** 现有 Skills

#### 场景: 代码改动后扫描旧锚点
- 检索 G6.1/G6.2/G6.3/G6.4/G11/G12 等旧锚点 → 替换为新 Skill 路径引用
- 验证无遗漏

## 风险评估

- **风险 1**：Skill 引用表新增 4 个 Skill，可能触发频率高，影响 Skill 调度优先级
  - **缓解**：明确每个新 Skill 的触发条件（仅在对应场景），避免常驻加载
- **风险 2**：现有 Skill 跨引用更新遗漏，导致旧锚点失效
  - **缓解**：用 grep 全局扫描 G6.1/G6.2/G11/G12 等关键词，确保 100% 覆盖
- **风险 3**：精简后入口缺少某些边界场景规则，导致路由判定退化
  - **缓解**：入口保留完整路由决策树骨架，复杂场景通过 routing Skill 提供详细规则
- **风险 4**：4 份入口仍需手工同步（本方案未解决双份维护问题）
  - **缓解**：在 task 5 加入一致性审计；后续可考虑用脚本生成
- **风险 5**：本仓库尚未建立 `helloagents/1.x/` 知识库
  - **缓解**：本方案属于元任务（修改 HelloAGENTS 自身），知识库创建延后至独立任务
