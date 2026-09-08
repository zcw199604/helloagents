# 知识库核心规则

## 知识库架构

**文件结构:**
```plaintext
helloagents/                       # HelloAGENTS 工作空间集合
└── <branch-name>/                 # 当前分支知识库根目录（SSOT）
    ├── CHANGELOG.md               # 版本历史（Keep a Changelog）
    ├── project.md                 # 技术约定
    ├── wiki/                      # 核心文档
    │   ├── overview.md            # 项目概述
    │   ├── arch.md                # 架构设计
    │   ├── api.md                 # API 手册
    │   ├── data.md                # 数据模型
    │   ├── glossary.md            # 领域语言/术语表
    │   └── modules/<module>.md
    ├── plan/                      # 变更工作区
    │   └── YYYYMMDDHHMM_<feature>/
    │       ├── why.md             # 变更提案
    │       ├── how.md             # 技术设计
    │       └── task.md            # 任务清单
    └── history/                   # 已完成变更归档
        ├── index.md
        └── YYYY-MM/YYYYMMDDHHMM_<feature>/
```

**路径约定:**
- 本规则集中 `helloagents/<branch-name>/` 表示当前分支对应的本地知识库根目录；`<branch-name>` 取当前 git 分支名或工作区别名
- 本规则集中 `plan/`、`wiki/`、`history/` 均指 `helloagents/<branch-name>/` 下的完整路径
- 所有知识库文件必须在 `helloagents/<branch-name>/` 目录下创建

---

## 核心术语详解

- **SSOT** (Single Source of Truth): 唯一真实来源（知识层面），指知识库
  - *注意:* 当SSOT与代码冲突时，SSOT视为"过时"，需依据代码（执行事实）进行更新
- **知识库**: 项目文档完整集合 (`CHANGELOG.md`, `project.md`, `wiki/*`, `history/index.md`)
- **EHRB** (Extreme High-Risk Behavior): 极度高风险行为
- **ADR** (Architecture Decision Record): 架构决策记录
- **MRE** (Minimal Reproducible Example): 最小可复现示例
- **方案包**: 完整方案单元
  - **目录结构**: `YYYYMMDDHHMM_<feature>/`
  - **必需文件**: `why.md` + `how.md` + `task.md`
  - **完整性检查**: 必需文件存在、非空、task.md至少1个任务项
  - **轻量迭代例外**: `task.md` 顶部标注 `模式: 轻量迭代` 的简化方案包仅含 `task.md`，按完整方案包处理（见 routing Skill 轻量迭代规则）
- **领域语言**: 项目内稳定使用的业务术语、缩写、角色、状态、流程名和禁用叫法，集中记录在 `wiki/glossary.md`

---

## 质量检查维度

1. **完整性**: 必需文件和章节是否存在
2. **格式**: Mermaid图表/Markdown格式是否正确
3. **一致性**: API签名/数据模型与代码是否一致
4. **安全**: 是否包含敏感信息（密钥/PII）

**问题分级:**
- **轻度**（可继续）: 缺失非关键文件、格式不规范、描述过时
- **重度**（需处理）: 核心文件缺失、内容严重脱节(>30%)、存在敏感信息

---

## 项目上下文获取策略

<context_acquisition_rules>
**步骤1: 先检查知识库（如存在）**
- 核心文件: `helloagents/<branch-name>/project.md`, `helloagents/<branch-name>/wiki/overview.md`, `helloagents/<branch-name>/wiki/arch.md`
- 按需选择: `helloagents/<branch-name>/wiki/glossary.md`, `helloagents/<branch-name>/wiki/modules/<module>.md`, `helloagents/<branch-name>/wiki/api.md`, `helloagents/<branch-name>/wiki/data.md`

**步骤2: 知识库不存在/信息不足 → 定向检查相关代码**
- 使用宿主平台的文件枚举能力获取结构（命令行环境优先 `rg --files`）
- 使用宿主平台的内容搜索能力定位信息（命令行环境优先 `rg`）
- 获取本次决策缺少的架构、技术栈、模块结构或约束；只有显式全库审计或初始化才扩大扫描。
</context_acquisition_rules>

---

## 知识库同步规则

<kb_sync_rules>
### 写入收益门禁

知识库默认不写。只有以下问题全部回答“是”时才更新：

1. 本次产生了代码无法直接表达的稳定事实、约定、架构原因、公共契约或领域语言吗？
2. 该信息会被未来任务复用，而不是本次进度、验证结果或完成声明吗？
3. 已有知识库中有明确的归属位置，且写入不会复制代码目录、普通依赖或实现细节吗？
4. 不写会使后续维护者作出错误判断，或现有条目已因本次变化而失真吗？

任一答案为“否”时跳过知识库写入；无需为了证明流程完成而记录“知识库同步不适用”。

**触发时机:** 通过写入收益门禁后，公共行为、架构、API、数据模型、领域语言或稳定技术约定变化才同步知识库。局部实现、一次性缺陷、测试、格式、注释、验证输出和任务流水账默认不写。

**自适应路径:** 无方案包的低/中风险改动默认不写；只有现有稳定知识因本次变化而失真时才最小更新对应条目，不创建整套知识库。

**步骤1 - 模块规范更新:**
- 完整方案包读取 `why.md` 的 **核心场景**；轻量方案包读取 `task.md` 的 **轻量方案包元数据** 中“范围摘要、核心场景、知识库同步”（均在迁移前读取）
- 提取需求和场景（需求需标注所属模块）
- 更新 `helloagents/<branch-name>/wiki/modules/<module>.md` 的 **规范** 章节
  - 不存在 → 追加
  - 已存在 → 更新
- 自适应无方案包路径仅修正因本次改动而失真的既有稳定规范；不从每个用户请求自动提炼新场景。

**步骤2 - 按变更类型更新:**
- API变更 → 更新 `helloagents/<branch-name>/wiki/api.md`
- 数据模型变更 → 更新 `helloagents/<branch-name>/wiki/data.md`
- 架构变更/新增模块 → 更新 `helloagents/<branch-name>/wiki/arch.md`
- 模块索引变更 → 更新 `helloagents/<branch-name>/wiki/overview.md`
- 技术约定变更 → 更新 `helloagents/<branch-name>/project.md`
- 领域语言候选/命名约定变更 → 更新 `helloagents/<branch-name>/wiki/glossary.md`

**步骤3 - ADR维护（如包含架构决策）:**
- 完整方案包从 `how.md` 提取 ADR；轻量方案包从“轻量方案包元数据”的 ADR 字段提取，值为“无”时不新增 ADR
- 在 `helloagents/<branch-name>/wiki/arch.md` 的 **重大架构决策** 表格中追加
- 所有归档链接使用 lifecycle 已解析的 `RESOLVED_ARCHIVE_PATH`，不得自行拼接无后缀路径。
- 完整方案包链接到 `{RESOLVED_ARCHIVE_PATH}/how.md#adr-xxx`；轻量方案包链接到 `{RESOLVED_ARCHIVE_PATH}/task.md#轻量方案包元数据`。
- 若步骤12原子复核发现目标被并发占用，先重算 `RESOLVED_ARCHIVE_PATH` 并同步修正本步骤写入的链接，再执行迁移。

**轻量方案包元数据约束:** 缺少范围摘要、核心场景、知识库同步、ADR 或验证策略任一字段时停止同步并报告方案包不完整，不得猜测缺失内容。

**步骤4 - 清理:**
- 只清理本次触达范围内已由代码证明过时的信息、废弃 API 或已删除模块，不做无关的全库整理

**步骤5 - 缺陷复盘（条件触发）:**
- 仅当缺陷根因非直觉、可能重复发生且预防规则会被未来任务复用时记录
- 一次性实现错误、测试已完整表达的回归和本次修复流水账默认不写

**步骤6 - 领域语言维护（如有）:**
- 来源: 需求分析阶段的领域语言候选、方案包 `why.md` 核心场景、代码命名或用户确认
- 写入 `wiki/glossary.md`，每条术语至少包含: 术语、定义、适用模块、来源
- 时机: 方案设计/开发实施阶段可写入时优先同步；需求分析只读阶段只记录候选，不直接写入
- 如果发现同义词或禁用叫法，写入同义词/禁用叫法字段，避免后续 agent 使用不一致称呼
- 如果术语仍未确认，标记为"待确认"，不得在代码命名中强制采用
</kb_sync_rules>

---

## 知识库缺失处理

<kb_missing_handler>
**STEP 1: 检查核心文件是否存在**
- `helloagents/<branch-name>/CHANGELOG.md`, `helloagents/<branch-name>/project.md`, `helloagents/<branch-name>/wiki/*.md`, `helloagents/<branch-name>/history/index.md`

**STEP 2: 知识库不存在**
按阶段处理:
```yaml
需求分析阶段:
  - 只标记问题，不创建知识库
  - 缺失影响当前判断时说明限制，不例行提示初始化

显式 ~init / ~wiki 命令:
  - 全面扫描代码库并创建完整知识库:
    - 根目录: `helloagents/<branch-name>/CHANGELOG.md`, `helloagents/<branch-name>/project.md`
    - `helloagents/<branch-name>/wiki/`: overview.md, arch.md, api.md, data.md, glossary.md
    - `helloagents/<branch-name>/wiki/modules/`: <module>.md（每个模块）
    - `helloagents/<branch-name>/history/index.md`
    - 按模块边界和可用上下文分批处理，避免单次加载整个大型项目

方案设计/开发实施阶段:
  - 知识库缺失不阻断分析、设计或实施
  - 仅在通过写入收益门禁且用户明确需要持久知识时，创建最小必要文件或提示使用 ~init

自适应无方案包路径:
  - 知识库缺失不阻断低/中风险实现
  - 默认不写、不提示、不自动创建；只有缺失知识会影响本次或后续正确决策时才提示使用 ~init
```

**STEP 3: 知识库存在**
```yaml
执行质量前置检查:
  重度问题 → 报告影响并定向核对；只在已授权重建时扩大扫描和写入，增量任务按写入收益门禁修正相关条目
  轻度问题 → 继续流程
```
</kb_missing_handler>

---
