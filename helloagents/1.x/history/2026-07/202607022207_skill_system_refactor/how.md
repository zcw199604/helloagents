# 技术设计: skill_system_refactor

## 技术方案

- 使用 `references/` 对大型 skill 做渐进披露。
- 在 `SKILL_INDEX.md` 中集中维护职责、触发、输入输出和依赖。
- 在 `scripts/audit_skills.py` 中用 Python 标准库实现只读审计。
- 将 `grill-with-docs` 的机制融入现有三阶段：`analyze` 识别领域语言，`design` 记录 ADR 候选，`kb` 维护 `wiki/glossary.md`。

## 架构决策 ADR

### ADR-003: 大型 Skill 采用轻量入口 + references

- 背景: 多个 `SKILL.md` 超过 250 行，入口上下文负载偏高。
- 决策: 主 `SKILL.md` 保留执行必需信息，长模板和细则迁移到同目录 `references/`。
- 替代方案: 继续保留大型单文件入口；拒绝原因是上下文负载高且维护困难。
- 影响: skill 读取更快，维护时需要保持引用路径有效。
- 状态: 已采纳

### ADR-004: 吸收 grill-with-docs 机制而非新增独立流程

- 背景: HelloAGENTS 已有需求分析、方案设计和知识库同步流程，原样新增独立 `grill-with-docs` 会造成流程重叠。
- 决策: 将领域语言、文档化追问、ADR 候选识别分别并入 `analyze`、`kb`、`design`。
- 替代方案: 新增独立 `grill-with-docs` skill；拒绝原因是会与现有三阶段流程重叠。
- 影响: 保持三阶段流程不变，同时增强文档沉淀质量。
- 状态: 已采纳

## 测试与部署

- 运行 `python scripts/audit_skills.py`。
- 通过 `git diff --check` 检查空白问题。
