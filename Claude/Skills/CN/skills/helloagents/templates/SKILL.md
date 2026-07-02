---
name: templates
description: 文档模板集合；创建 Wiki、方案包或版本记录时读取。主文件只负责选择模板类别，完整模板按需读取 references。
invocation: model
side_effects: read-only
requires:
  - kb
  - lifecycle
completion_criteria: 已选择正确模板引用文件，并按目标文件类型填充必要章节。
---

# 文档模板集合

**目标:** 为知识库、方案包和版本号解析提供模板入口。完整模板已下沉到 `references/`，避免每次创建文件都加载全部模板。

---

## 使用流程

1. 先判断要创建或更新的文件类型。
2. 按下表只读取对应 reference 文件。
3. 保留模板中的必需章节；删除与当前文件无关的占位说明。
4. 写入前确认路径仍在 `helloagents/<branch-name>/` 下。

---

## 模板索引

| 场景 | 读取文件 | 适用目标 |
|---|---|---|
| 知识库初始化或重建 | `references/knowledge-base-templates.md` | `CHANGELOG.md`, `project.md`, `wiki/*`, `history/index.md` |
| 创建方案包或迁移历史 | `references/plan-package-templates.md` | `plan/*/why.md`, `how.md`, `task.md`, `history/*/*` |
| 确定版本号 | `references/versioning.md` | `CHANGELOG.md` 版本段落 |

---

## 正反例

**应触发:**
- `~init` 需要创建 `project.md` 和 `wiki/overview.md`。
- 方案设计阶段需要创建 `why.md`、`how.md`、`task.md`。
- 开发实施完成后需要判断 CHANGELOG 版本号。

**不应触发:**
- 只读咨询，不创建或更新文件。
- 用户要求解释某个模板字段含义，此时可直接回答，不必加载完整模板。

---

## 完成门禁

- 已读取唯一相关的 reference 文件，而不是加载全部模板。
- 输出文件包含该类型的必需章节。
- 方案包文件包含可迁移到 history 的稳定结构。
- 未在 `helloagents/<branch-name>/` 之外创建知识库或方案文件。
