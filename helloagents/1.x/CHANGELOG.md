# Changelog

本文件记录项目所有重要变更。
格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/),
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- 新增 4 个按需触发的 Skill: `output-format`（G6.1-G6.4 输出模板集合）、`routing`（路由细节）、`lifecycle`（G11/G12 方案包生命周期与状态变量）、`windows-shell`（Windows PowerShell 语法约束）；CN/EN × Codex/Claude 共 16 个 SKILL.md
- 在 4 份 bootstrap 入口的 Skills 引用表中新增上述 4 个 Skill

### 变更
- 重写 4 份 bootstrap 入口（`Codex/Skills/CN/AGENTS.md`、`Claude/Skills/CN/CLAUDE.md`、`Codex/Skills/EN/AGENTS.md`、`Claude/Skills/EN/CLAUDE.md`），由 1065 行精简至 266 行（约 75% 缩减），仅保留角色定义、最小路由决策树、阶段触发表、Skill 引用表与核心全局约束（G1-G12 简版）
- bootstrap 中 G6.1-G6.4 输出格式模板、G11 方案包生命周期、G12 状态变量、路由机制详细规则、Windows PowerShell 语法约束、命令完成输出格式全部下沉至对应新 Skill
- 明确现有 Skill 中的 G6/G11 跨引用指向 `output-format` / `lifecycle` Skill，避免精简入口后仍隐式依赖 bootstrap 内联锚点

### 移除
- bootstrap 入口中移除上述已下沉的细节段落

### 架构决策
- ADR-001: 不引入 `_shared/` 共享机制，维持 4 份独立入口；解决双份维护问题留待后续优化
- ADR-002: 抽取 `routing` Skill 但 bootstrap 保留最小路由决策树，避免常驻读取
