# 任务清单: Skill 规则矛盾与遗留悬空清理

目录: `helloagents/1.x/plan/202607032233_skill_consistency_fixes/`

---

## 0. 方案边界确认
- [√] 0.1 确认本次仅覆盖审查第一、二部分共 9 项修复，第三部分打磨项不进入实现
  - 执行模式: AFK
  - 涉及文件: `why.md`, `how.md`, `task.md`
  - 完成标准: 范围内/范围外边界一致且无互相矛盾描述
  - 验证方式: 只读核对方案包三件套

## 1. 规则矛盾修复（审查第一部分）
- [√] 1.1 修复步骤13多模型验收契约为 "OUTPUT: Risk report only."
  - 执行模式: AFK
  - 涉及文件: `Claude/.../develop/references/entry-and-steps.md`
  - 完成标准: 步骤13不再出现 "Unified Diff Patch ONLY"，与 multi_model 审查契约一致
  - 验证方式: grep 核对
- [√] 1.2 修正 detailed-planning.md 步骤6适用模式，与 output-and-transition.md 对齐
  - 执行模式: AFK
  - 涉及文件: `Claude/.../design/references/detailed-planning.md`
  - 完成标准: 两文件对"规划命令是否输出多模型审查询问"口径一致（不输出）
  - 验证方式: 只读核对两文件
- [√] 1.3 清理 P1/P2/P3 阶段代号（5 个文件，保留 P0/P1/P2 风险分级）
  - 执行模式: AFK
  - 涉及文件: `entry-and-steps.md`, `standards-and-output.md`, `lifecycle/SKILL.md`, `requirement-assessment.md`, `code-analysis-and-output.md`
  - 完成标准: grep "P[123]阶段|P3 步骤|P1只读|P2方案设计|P2/P3方案包|p3_entry_gate" 无命中
  - 验证方式: grep 核对
- [√] 1.4 统一 CURRENT_PACKAGE 清理时机与 G12 引用
  - 执行模式: AFK
  - 涉及文件: `Claude/.../develop/references/phase-transition.md`
  - 完成标准: 清理时机为"迁移至 history/ 后"，引用条款为 G12
  - 验证方式: 只读核对与 lifecycle G12 一致
- [√] 1.5 轻量迭代简化方案包合法化（完整性例外+标注+步骤1识别+G2补注）
  - 执行模式: AFK
  - 涉及文件: `kb/references/knowledge-base-rules.md`, `routing/references/routing-paths.md`, `develop/references/entry-and-steps.md`, `Claude/Skills/CN/CLAUDE.md`, `Codex/Skills/CN/AGENTS.md`
  - 完成标准: 简化方案包有标注规则，完整性检查与步骤1扫描均有对应例外
  - 验证方式: 只读核对四处规则互相引用一致
- [√] 1.6 轻量迭代流程补 CHANGELOG 更新步骤
  - 执行模式: AFK
  - 涉及文件: `Claude/.../routing/references/routing-paths.md`
  - 完成标准: 动作流程包含 CHANGELOG.md 更新（按 G7），与输出模板一致
  - 验证方式: 只读核对

## 2. 遗留悬空清理（审查第二部分）
- [√] 2.1 multi_model 遗留清理（R1/R2、配置来源、TASK_COMPLEXITY、Phase/英文阶段名、Y/N 中文化）
  - 执行模式: AFK
  - 涉及文件: `Claude/.../multi_model/SKILL.md`
  - 完成标准: grep "R1|R2|Phase2|Phase3|Phase4|TASK_COMPLEXITY|Shall I proceed" 无命中；配置项均有默认值与来源说明
  - 验证方式: grep 核对
- [√] 2.2 delegation-protocol.md 章节重排为 1-10
  - 执行模式: AFK
  - 涉及文件: `Claude/.../hello-subagent/references/delegation-protocol.md`
  - 完成标准: 章节编号从 1 连续到 10
  - 验证方式: grep 章节标题核对
- [√] 2.3 模板与 qa-review 示例命令改为占位符+本仓库示例
  - 执行模式: AFK
  - 涉及文件: `templates/references/plan-package-templates.md`, `qa-review/SKILL.md`
  - 完成标准: 命令外层为占位符表述；`python scripts/audit_safety.py` 等契约字符串仍存在
  - 验证方式: `python scripts/audit_skills.py`

## 3. 镜像同步与安全检查
- [√] 3.1 将 Claude 树改动镜像同步至 Codex 树
  - 执行模式: AFK
  - 涉及文件: `Codex/Skills/CN/skills/helloagents/**`
  - 完成标准: 两树 skills 目录逐文件一致
  - 验证方式: `python scripts/audit_skills.py`（mirror 检查）
- [√] 3.2 执行安全检查（按 G9: 无敏感信息、无危险命令、无 EHRB）
  - 执行模式: AFK
  - 涉及文件: 本次改动文件
  - 完成标准: 未发现新增敏感信息、危险命令或未确认 EHRB 风险
  - 验证方式: `python scripts/audit_safety.py`

## 4. 文档更新
- [√] 4.1 同步知识库与 CHANGELOG.md（Unreleased 变更条目）
  - 执行模式: AFK
  - 涉及文件: `helloagents/1.x/CHANGELOG.md`, `helloagents/1.x/wiki/modules/skills.md`（如适用）
  - 完成标准: 知识库与规则事实一致且链接到本方案包
  - 验证方式: 只读核对知识库

## 5. 测试

### 5B. TDD-EXEMPT路径
- [√] 5B.1 TDD-EXEMPT: 纯文档规则变更，无运行时可观察行为；替代验证: `python scripts/audit_skills.py` + `python scripts/audit_safety.py` + 逐项 grep 核对
  - 执行模式: AFK
  - 涉及文件: 本次全部改动文件
  - 完成标准: 两个审计脚本通过，任务1.x/2.x 的 grep 核对全部通过
  - 验证方式: 运行两个审计脚本并记录结果
