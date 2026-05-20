# 技术设计: 精简 HelloAGENTS bootstrap 文档

## 技术方案

### 核心技术
- Markdown 文档重构
- Skill 触发机制（依赖 bootstrap 中的「Skills 引用表」）

### 实现要点

**1. 新 Skill 命名与触发条件**

| Skill 名 | 内容来源（bootstrap 原行号） | 触发条件 |
|---------|----------------------------|---------|
| `output-format` | G6.1（192-290）、G6.2（292-389）、G6.3（391-415）、G6.4（417-453）、命令完成输出格式（875-936） | 任何阶段最终输出、异常输出、咨询问答、交互询问、命令完成时 |
| `routing` | 路由机制详细（592-800：评估维度、决策原则、路由验证、处理路径、命令路径、上下文路径） | 复杂边界路由（评分 6-7 分、EHRB 模糊、模式升级、上下文打断） |
| `lifecycle` | G11（526-571）、G12（573-590） | 创建/迁移方案包、扫描遗留方案、状态变量管理 |
| `windows-shell` | G1 中 PowerShell 段（57-87） | Platform=win32 且需要使用 shell 命令 |

**2. 入口保留内容（目标 ≤ 250 行）**

| 区块 | 行预算 | 说明 |
|------|--------|------|
| 角色与核心价值 | ~20 | 原样保留 |
| G1 | ~15 | 仅保留 OUTPUT_LANGUAGE、编码、工具表；PowerShell 段抽出到 `windows-shell` |
| G2 | ~10 | 原样保留（核心术语 + 路径约定） |
| G3 | ~20 | 不确定性原则（关键，保留） |
| G4 | ~12 | 项目规模判定（保留） |
| G5 | ~10 | 写入授权与静默执行（保留） |
| G6 | ~20 | 阶段执行流程 + 工作模式 + 主动反馈规则；输出格式细节移至 `output-format` |
| G7 | ~6 | 版本管理（保留） |
| G8 | ~8 | 产品设计原则（保留） |
| G9 | ~22 | 安全与合规（保留，EHRB 关键） |
| G10 | ~22 | 知识库操作（保留调度逻辑，细节本来就指向 kb Skill） |
| 路由机制（精简版） | ~40 | 路由流程 + 路由优先级 + 简化决策树；细节移至 `routing` Skill |
| 命令速查表 | ~10 | 触发词表 |
| Feedback-Delta 规则 | ~12 | 保留 |
| 阶段骨架 | ~25 | 仅保留触发表（详细步骤已在 analyze/design/develop Skill） |
| Skills 引用表 | ~18 | 新增 4 行 |
| **合计** | **~250** | |

**3. 跨引用更新规则**

现有 Skill 中存在的旧锚点 → 新引用映射：

```
G6.1 / G6.2 / G6.3 / G6.4    → output-format Skill
G11                          → lifecycle Skill
G12                          → lifecycle Skill
路由优先级 / 复杂度路径细节  → routing Skill
PowerShell 语法约束          → windows-shell Skill
```

替换原则：保留语义引用（如"按 G11 规则"），但在首次出现时改为"按 `lifecycle` Skill 规则（原 G11）"，让 Skill 加载机制能触发。

**4. 路径约定**

CN 与 EN 各自独立，写入路径分别为：
- `Codex/Skills/CN/skills/helloagents/<skill-name>/SKILL.md`
- `Claude/Skills/CN/skills/helloagents/<skill-name>/SKILL.md`
- `Codex/Skills/EN/skills/helloagents/<skill-name>/SKILL.md`
- `Claude/Skills/EN/skills/helloagents/<skill-name>/SKILL.md`

CN 内容用简体中文；EN 内容用英文（参照现有 EN Skill 风格）。Codex 与 Claude 同语言版本内容应一致。

## 设计边界

- **范围内**：4 份 bootstrap 入口重写、16 个新 SKILL.md 创建、约 32 个现有 SKILL.md 跨引用更新
- **范围外**：业务逻辑变更（路由算法、评分规则、EHRB 识别）、`_shared/` 共享机制、自动生成脚本、知识库创建
- **模块职责**：
  - bootstrap：角色 + 最小路由 + Skill 入口
  - output-format：所有输出模板
  - routing：路由细节与上下文响应
  - lifecycle：方案包与状态变量
  - windows-shell：平台特定 shell 规则
- **接口契约**：Skill 触发名是稳定 API，一旦发布不再更名
- **数据边界**：无数据变更
- **依赖边界**：不新增外部依赖
- **大型项目最小改动**：仅 bootstrap 4 份 + 新增 16 个 SKILL + 现有 32 个 SKILL 跨引用；不做无关重构、不搬迁目录、不重命名既有 Skill

## 架构决策 ADR

### ADR-001: 不引入 `_shared/` 共享机制
**上下文：** 双份维护成本是次要问题，引入共享机制需验证 Codex AGENTS.md / Claude CLAUDE.md 跨目录 import 兼容性，前置不确定。
**决策：** 维持 4 份独立入口，由人工或后续脚本同步。
**理由：** 风险可控；本次目标是减少上下文占用，已达成。
**替代方案：** Plan 3 共享化重构 → 拒绝：兼容性未验证。
**影响：** 维护成本仍存在，待后续单独优化。

### ADR-002: 抽取 routing Skill 而非全留入口
**上下文：** 路由细节约 210 行，但路由是每次消息都执行的逻辑。
**决策：** 入口保留「最小决策树」（互斥优先级 5 步），细节场景（评估维度、边界情况、上下文打断、命令路径）下沉。
**理由：** 大多数路由判定不需要细节；只在边界场景触发 Skill。
**替代方案：** 全留入口 → 拒绝：违背精简目标。
**影响：** 极端边界场景需多读一次 Skill；可接受。

## 安全与性能

- **安全**：无 EHRB 信号；纯文档重构
- **性能**：bootstrap 加载量减少约 75%；Skill 按需加载，整体上下文占用降低

## 测试与部署

- **测试**：
  - 行数验证：4 份入口均 ≤ 250 行
  - grep 验证：旧锚点（G6.1/G6.2/G6.3/G6.4/G11/G12）在现有 Skill 中已全部替换为新引用
  - 结构验证：新 Skill 文件含 `---` frontmatter（name + description）
  - 一致性验证：CN 两份入口内容一致；EN 两份入口内容一致
- **部署**：直接提交至 1.x 分支，无需 CI 验证
