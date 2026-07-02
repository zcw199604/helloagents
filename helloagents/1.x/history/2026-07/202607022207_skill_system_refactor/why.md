# 变更提案: skill_system_refactor

## 需求背景

用户要求参考 `mattpocock/skills` 的组织方式，完成当前仓库 skills 的拆薄、索引、元数据、示例、职责去重和审计脚本建设。

## 变更内容

- 拆薄大型 `SKILL.md`，将长规则迁移到 `references/`。
- 增加 skill 索引矩阵。
- 统一 frontmatter 元数据。
- 增加正反例和完成门禁。
- 明确 `kb/lifecycle`、`multi_model/hello-subagent` 等职责边界。
- 增加只读审计脚本。
- 吸收 `grill-with-docs` 的核心机制：领域语言沉淀、文档化追问、ADR 候选识别。

## 范围边界

- 不引入新的第三方依赖。
- 不改变 HelloAGENTS 三阶段主流程。
- 不引入 `_shared/` 生成机制，本次继续保持 Codex/Claude 双端镜像。
