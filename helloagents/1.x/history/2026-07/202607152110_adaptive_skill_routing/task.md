# 任务清单: 自适应 Skill 路由与 Eval 基线

目录: `helloagents/1.x/plan/202607152110_adaptive_skill_routing/`

---

## 0. 方案边界确认

- [√] 0.1 核对方案包范围、风险与验证策略
  - 执行模式: AFK
  - 涉及文件: `why.md`, `how.md`, `task.md`
  - 完成标准: 三份文档覆盖同一需求切片且无未解释占位项
  - 验证方式: 只读核对方案包

## 1. Eval 基线

- [√] 1.1 RED: 添加 eval schema、覆盖、bootstrap 和路由行为回归测试
  - 执行模式: AFK
  - 涉及文件: `tests/test_skill_evals.py`, `tests/test_audits.py`
  - 完成标准: 新测试在实现前因缺少 eval 数据/脚本或旧路由语义而失败
  - 验证方式: `python -B -m unittest tests.test_skill_evals -v`
- [√] 1.2 GREEN: 实现 eval 用例集和校验/评分脚本
  - 执行模式: AFK
  - 涉及文件: `evals/skill_routing_cases.json`, `scripts/eval_skills.py`
  - 完成标准: eval 数据覆盖规定类别且脚本可校验和评分结构化结果
  - 验证方式: `python -B scripts/eval_skills.py`; `python -B -m unittest tests.test_skill_evals -v`

## 2. Bootstrap 与路由

- [√] 2.1 精简 Codex/Claude bootstrap 并保持镜像
  - 执行模式: AFK
  - 涉及文件: `Codex/Skills/CN/AGENTS.md`, `Claude/Skills/CN/CLAUDE.md`
  - 完成标准: 常驻入口保留稳定约束且行数显著低于当前 268 行
  - 验证方式: bootstrap 体量测试与 `python -B scripts/audit_skills.py`
- [√] 2.2 调整普通 Bug 和小改动路由及开发入口
  - 执行模式: AFK
  - 涉及文件: 双端 `routing/references/*.md`, 双端 `develop/SKILL.md`, 双端 `develop/references/entry-and-steps.md`
  - 完成标准: 明确低/中/高风险路径；普通 Bug 和低风险小改动不再强制方案包或二次确认；EHRB 门禁不变
  - 验证方式: 路由语义测试、Skill 审计与人工核对

## 3. 文档与验证

- [√] 3.1 同步审计契约和知识库
  - 执行模式: AFK
  - 涉及文件: `scripts/audit_skills.py`, `helloagents/1.x/project.md`, `helloagents/1.x/wiki/modules/skills.md`, `helloagents/1.x/wiki/arch.md`, `helloagents/1.x/CHANGELOG.md`
  - 完成标准: 文档反映 eval 与风险路由，ADR-008 可追溯到归档方案包
  - 验证方式: `python -B scripts/audit_skills.py`
- [√] 3.2 REFACTOR/VERIFY: 运行全量质量与安全验证并生成 QA 证据
  - 执行模式: AFK
  - 涉及文件: 本次全部改动文件、`qa-review.json`
  - 完成标准: 目标测试通过；已知既有失败与本次新增回归可区分；QA 证据完整
  - 验证方式: `python -B -m unittest discover -s tests -v`; `python -B scripts/audit_skills.py`; `python -B scripts/audit_safety.py`
