# 技术设计: Skill 规则矛盾与遗留悬空清理

## 技术方案

### 核心技术
- Markdown 规则文件精确编辑（Edit 精确替换）
- `python scripts/audit_skills.py` 作为一致性回归门禁

### 实现要点
- 以 Claude 树为编辑主树，完成后将 `skills/helloagents` 整目录同步至 Codex 树，保证镜像审计通过
- 涉及 `audit_skills.py` 语义契约的字符串（`python scripts/audit_safety.py`、`python scripts/audit_skills.py`、`qa-review.json`、步骤标题、命令别名）一律保留原文，仅在其外层包占位符说明

## 设计边界

- **范围内:** 规则文本修正、术语替换、章节重排、两端 bootstrap 的 G2 补充说明
- **范围外:** skill 目录改名、audit 脚本新增门禁、collaborating-* 重构、脚本代码变更
- **模块职责:** 各修改遵循 SKILL_INDEX 冲突域划分，不跨 skill 复制规则，只修正引用
- **接口契约:** 不改变任何 skill 的 frontmatter 字段结构、命令别名、输出模板骨架
- **数据边界:** 无数据变更
- **依赖边界:** 不新增依赖
- **大型项目最小改动:** 仅触碰问题行及其最小上下文；不顺手重排无关章节、不统一无关措辞

## 修复映射（编号对应 why.md 变更内容）

| # | 文件（Claude 树，Codex 镜像同步） | 修改 |
|---|---|---|
| 1 | `develop/references/entry-and-steps.md` | 步骤13 契约改为 "OUTPUT: Risk report only." |
| 2 | `design/references/detailed-planning.md` | 步骤6 适用模式仅保留交互确认模式；补规划命令处理=跳过询问+总结末尾提示 |
| 3 | `develop/references/entry-and-steps.md`、`standards-and-output.md`、`lifecycle/SKILL.md`、`analyze/references/requirement-assessment.md`、`analyze/references/code-analysis-and-output.md` | P1/P2/P3 阶段代号→中文阶段名；`<p3_entry_gate>`→`<develop_entry_gate>`；保留 P0/P1/P2 风险分级 |
| 4 | `develop/references/phase-transition.md` | CURRENT_PACKAGE 清理时机改为"迁移至 history/ 后"，引用改为 G12 |
| 5 | `kb/references/knowledge-base-rules.md`（完整性检查例外）、`routing/references/routing-paths.md`（task.md 顶部标注）、`develop/references/entry-and-steps.md`（步骤1识别规则）、`CLAUDE.md`/`AGENTS.md`（G2 补注） | 轻量迭代简化方案包合法化 |
| 6 | `routing/references/routing-paths.md` | 轻量迭代步骤5改为"同步知识库并按 G7 更新 CHANGELOG.md" |
| 7 | `multi_model/SKILL.md` | R1/R2→微调/轻量迭代；配置项补默认值与会话级来源；TASK_COMPLEXITY→design 复杂度判定；Phase/英文阶段名→中文；Y/N 询问中文化；frontmatter description 同步 |
| 8 | `hello-subagent/references/delegation-protocol.md` | 章节 3-12 重排为 1-10 |
| 9 | `templates/references/plan-package-templates.md`（任务3.1/4.1 验证方式）、`qa-review/SKILL.md`（示例 command） | 占位符+本仓库示例，保留契约字符串 |

## 架构决策 ADR

本次无 ADR 候选（纯规则文本修正，无架构或命名取舍；R1/R2 等映射均还原既有语义）。

## 安全与性能

- **安全:** 无 EHRB；全部改动为仓库内 markdown，可通过 git 回滚
- **性能:** 不适用

## 测试与部署

- **测试:** TDD-EXEMPT（纯文档规则变更，无可观察运行时行为）；替代验证为 `python scripts/audit_skills.py` 与 `python scripts/audit_safety.py` 通过 + 逐项 grep 核对矛盾字符串已消除
- **部署:** 不适用；提醒用户后续自行同步全局 CLAUDE.md
