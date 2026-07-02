---
name: kb
description: 知识库管理完整规则；~init 命令、知识库缺失、知识库同步或一致性审计时读取。详细创建/同步规则按需读取 references。
invocation: model
side_effects: may_write_knowledge_base
requires:
  - templates
completion_criteria: 知识库存在性、质量、同步范围和一致性修正均已处理。
---

# 知识库管理

**目标:** 维护 `helloagents/<branch-name>/` 下的项目知识库，使文档反映代码事实和已执行方案。

---

## 职责边界

`kb` 只负责知识库内容本身：创建、读取、质量检查、同步、审计和过时信息清理。

不由 `kb` 负责的事项:
- 方案包状态符号、迁移算法、遗留扫描状态变量 → 由 `lifecycle` 负责
- 阶段最终输出模板 → 由 `output-format` 负责
- 开发实施步骤顺序和测试门禁 → 由 `develop` 负责

---

## Reference 选择

| 场景 | 读取文件 |
|---|---|
| 知识库架构、术语、质量检查、上下文获取、同步和缺失处理 | `references/knowledge-base-rules.md` |
| `~init` / `~wiki` 命令完成输出字段 | `references/init-output.md` |
| 具体文件模板 | `../templates/references/knowledge-base-templates.md` |

---

## 正反例

**应触发:**
- `~init` 或 `~wiki` 初始化/重建知识库。
- 代码或 skill 结构变化后同步 `project.md`、`wiki/*`、`CHANGELOG.md`。
- 发现知识库与代码事实冲突，需要修正文档。
- 需求分析产出领域语言候选，需要写入或修正 `wiki/glossary.md`。

**不应触发:**
- 只迁移方案包或扫描遗留方案；这是 `lifecycle`。
- 只选择阶段输出模板；这是 `output-format`。
- 只执行方案包任务；这是 `develop`。

---

## 完成门禁

- 必备知识库文件存在，或已按阶段规则记录缺失/创建。
- `wiki/glossary.md` 存在；若本次有领域语言候选，已写入或更新术语表。
- 代码变更涉及的模块、API、数据模型、架构或技术约定已同步。
- 知识库与代码冲突时，已按代码事实修正文档或记录例外原因。
- 未复制 `lifecycle` 的迁移算法；仅链接迁移后的历史记录。
