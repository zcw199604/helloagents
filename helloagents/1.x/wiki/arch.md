# 架构设计

## 总体架构

```mermaid
flowchart TD
  User["用户请求"] --> Bootstrap["AGENTS.md / CLAUDE.md"]
  Bootstrap --> SkillIndex["SKILL_INDEX.md"]
  Bootstrap --> Skill["按需 SKILL.md"]
  Skill --> References["references/*.md"]
  Skill --> Scripts["scripts/*.py"]
  Skill --> KB["helloagents/<branch>/wiki"]
```

## 核心原则

- Bootstrap 保持轻量，只保存全局规则、最小路由和 skill 引用表。
- `SKILL.md` 保持可快速加载，长内容通过 progressive disclosure 下沉。
- Codex 与 Claude 目录保持一致，通过只读审计脚本验证。

## 重大架构决策

| adr_id | title | date | status | affected_modules | details |
|--------|-------|------|--------|------------------|---------|
| ADR-001 | 不引入 `_shared/` 共享机制，维持多端入口 | 2026-05 | 已记录 | Bootstrap | [history/2026-05/202605142129_slim_bootstrap/how.md](../history/2026-05/202605142129_slim_bootstrap/how.md) |
| ADR-002 | 抽取 `routing` Skill 但 bootstrap 保留最小路由决策树 | 2026-05 | 已记录 | Bootstrap, routing | [history/2026-05/202605142129_slim_bootstrap/how.md](../history/2026-05/202605142129_slim_bootstrap/how.md) |
| ADR-003 | 大型 `SKILL.md` 拆为轻量入口 + `references/` | 2026-07 | 已采纳 | Skills | [history/2026-07/202607022207_skill_system_refactor/how.md](../history/2026-07/202607022207_skill_system_refactor/how.md) |
| ADR-004 | 吸收 grill-with-docs 机制而非新增独立流程 | 2026-07 | 已采纳 | analyze, design, kb | [history/2026-07/202607022207_skill_system_refactor/how.md](../history/2026-07/202607022207_skill_system_refactor/how.md) |
