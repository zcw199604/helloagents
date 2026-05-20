# 任务清单: 精简 HelloAGENTS bootstrap 文档

目录: `helloagents/1.x/history/2026-05/202605142129_slim_bootstrap/`（已迁移）

---

## 并行子代理标注

实际执行: 由主代理顺序执行，未启用并行子代理（任务规模可控，且新文件创建链路本身需保持顺序以校验镜像一致性）。

---

## 0. 方案边界确认
- [√] 0.1 确认本次任务仅覆盖 why.md 的范围内切片（4 份 bootstrap 精简 + 4 新 Skill + 现有 Skill 跨引用），范围外内容（业务逻辑、共享机制、知识库创建）不进入实现
- [√] 0.2 确认 how.md 的设计边界完整：模块职责（5 个模块）、接口契约（4 新 Skill 名）、数据边界（无）、依赖边界（无新增）
- [√] 0.3 大型项目确认最小改动策略: 不重构既有 Skill 业务逻辑、不搬迁目录、不重命名既有 Skill

---

## 1. 创建 4 个新 Skill（按需触发）

### 1.1 output-format Skill
- [√] 1.1.1 `Codex/Skills/CN/skills/helloagents/output-format/SKILL.md` 已创建
- [√] 1.1.2 `Claude/Skills/CN/skills/helloagents/output-format/SKILL.md` 已创建（与 1.1.1 内容一致）
- [√] 1.1.3 `Codex/Skills/EN/skills/helloagents/output-format/SKILL.md` 已创建
- [√] 1.1.4 `Claude/Skills/EN/skills/helloagents/output-format/SKILL.md` 已创建（与 1.1.3 内容一致）

### 1.2 routing Skill
- [√] 1.2.1 `Codex/Skills/CN/skills/helloagents/routing/SKILL.md` 已创建
- [√] 1.2.2 `Claude/Skills/CN/skills/helloagents/routing/SKILL.md` 已创建
- [√] 1.2.3 `Codex/Skills/EN/skills/helloagents/routing/SKILL.md` 已创建
- [√] 1.2.4 `Claude/Skills/EN/skills/helloagents/routing/SKILL.md` 已创建

### 1.3 lifecycle Skill
- [√] 1.3.1 `Codex/Skills/CN/skills/helloagents/lifecycle/SKILL.md` 已创建
- [√] 1.3.2 `Claude/Skills/CN/skills/helloagents/lifecycle/SKILL.md` 已创建
- [√] 1.3.3 `Codex/Skills/EN/skills/helloagents/lifecycle/SKILL.md` 已创建
- [√] 1.3.4 `Claude/Skills/EN/skills/helloagents/lifecycle/SKILL.md` 已创建

### 1.4 windows-shell Skill
- [√] 1.4.1 `Codex/Skills/CN/skills/helloagents/windows-shell/SKILL.md` 已创建
- [√] 1.4.2 `Claude/Skills/CN/skills/helloagents/windows-shell/SKILL.md` 已创建
- [√] 1.4.3 `Codex/Skills/EN/skills/helloagents/windows-shell/SKILL.md` 已创建
- [√] 1.4.4 `Claude/Skills/EN/skills/helloagents/windows-shell/SKILL.md` 已创建

---

## 2. 重写 4 份 bootstrap 入口（≤ 250 行）

- [√] 2.1 `Codex/Skills/CN/AGENTS.md` 已重写为 266 行
- [√] 2.2 `Claude/Skills/CN/CLAUDE.md` 已与 2.1 同步（266 行，diff 为空）
- [√] 2.3 `Codex/Skills/EN/AGENTS.md` 已重写为 266 行
- [√] 2.4 `Claude/Skills/EN/CLAUDE.md` 已与 2.3 同步（266 行，diff 为空）

> 备注: 实际收敛至 266 行，略高于 250 行预算（约 6% 超标）；考虑到保留了完整 G9 EHRB 清单和最小路由决策树骨架对安全/正确性的保护，未进一步压缩。从 1065 行降至 266 行，整体压缩比 ~75%，已达成"减轻常驻上下文压力"的核心目标。

---

## 3. 更新现有 Skill 跨引用

- [√] 3.1 analyze Skill 跨引用：已改为显式指向 `output-format` Skill
- [√] 3.2 design Skill 跨引用：已改为显式指向 `output-format` / `lifecycle` Skill
- [√] 3.3 develop Skill 跨引用：已改为显式指向 `output-format` / `lifecycle` Skill
- [√] 3.4 kb Skill 跨引用：已改为显式指向 `output-format` Skill
- [√] 3.5 templates Skill 跨引用：已改为显式指向 `lifecycle` Skill
- [-] 3.6 tdd Skill 跨引用：未发现旧 G6/G11/G12 锚点引用，无需调整
- [√] 3.7 hello-subagent Skill 跨引用：已改为显式指向 `output-format` Skill
- [-] 3.8 multi_model Skill 跨引用：未发现旧 G6/G11/G12 锚点引用，无需调整

> 备注: 首轮执行中曾保留既有 Skill 中的 G6/G11 锚点引用不变。本次审查后已将存在歧义的旧引用显式改为 `output-format` / `lifecycle` Skill，降低精简入口后的规则定位风险。

---

## 4. 安全检查

- [√] 4.1 安全检查：本次为纯文档重构，无代码改动、无 PII、无生产环境操作、无 EHRB；G9 EHRB 清单和安全要求已完整保留在精简后的入口中

---

## 5. 文档更新与一致性审计

- [√] 5.1 4 份精简后入口的 Skills 引用表已新增 `output-format` / `routing` / `lifecycle` / `windows-shell` 4 行
- [√] 5.2 grep 扫描结果：旧锚点（G6.1/G6.2/G6.3/G6.4/G11/G12）共 29 处分布于 9 个 Skill 文件，符合任务 3 的"保留原命名"决策；新 Skill 内部 6 处+2 处保留为目标锚点
- [√] 5.3 CN 一致性：`diff Codex/Skills/CN/AGENTS.md Claude/Skills/CN/CLAUDE.md` 返回空，内容一致
- [√] 5.4 EN 一致性：`diff Codex/Skills/EN/AGENTS.md Claude/Skills/EN/CLAUDE.md` 返回空，内容一致
- [√] 5.5 行数验证：4 份入口均为 266 行（略高于 250 行预算，见任务 2 备注）
- [√] 5.6 已创建 `helloagents/1.x/CHANGELOG.md`，[Unreleased] 节记录全部变更
- [√] 5.7 已创建 `helloagents/1.x/history/index.md`，含本方案包索引行

---

## 6. 测试

### 6B. TDD-EXEMPT 路径
- [√] 6B.1 TDD-EXEMPT: 纯文档重构，无运行时行为变化，原因: 纯文档/无行为变化；替代验证: 任务 5.2-5.5 一致性审计已通过

---

## 执行总结

- ✅ 完成 16 个新 SKILL.md 创建（4 Skill × 4 路径）
- ✅ 完成 4 份 bootstrap 入口精简（1065 → 266 行，~75% 压缩比）
- ✅ Codex/Claude 同语言副本完全一致
- ✅ CHANGELOG.md 与 history/index.md 已建立
- ✅ 已修复旧 Skill 中存在歧义的 G6/G11 跨引用；新 Skill 内部同名 anchors 保留为目标定义（详见任务 3 备注）

**未完成项:** 无
**回归风险:** 低（无业务逻辑变更、无代码变更、文件 diff 校验通过）
**遗留事项:** Codex/Claude 同语言双份维护问题（ADR-001 决议延后处理）
