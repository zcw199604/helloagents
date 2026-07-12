# 任务清单: TDD 混合执行与证据门禁

目录: `helloagents/1.x/plan/202607121222_tdd_hybrid_enforcement/`

## 0. 方案边界确认

- [√] 0.1 核对方案包的范围、schema 兼容策略和 ADR 一致
  - 执行模式: AFK
  - 涉及文件: `why.md`, `how.md`, `task.md`
  - 完成标准: 只覆盖测试入口、TDD 证据和审计门禁，未引入宿主运行时改造
  - 验证方式: 只读核对方案包三件套

## 1. 审计器 TDD RED

- [√] 1.1 RED: 为 schema v3 中缺失 `tdd`、非法 RED 结果和有效豁免添加 `qa_json_errors` 单元测试
  - 执行模式: AFK
  - 涉及文件: `tests/test_audits.py`
  - 完成标准: 新测试在现有审计器下失败，且失败原因是尚不支持 v3 TDD 契约
  - 验证方式: `python -m unittest tests.test_audits.SkillStructureAuditTests -v`

## 2. 审计器 TDD GREEN 与 REFACTOR

- [√] 2.1 GREEN: 扩展 `qa_json_errors`，兼容 v1/v2 并校验 schema v3 的完整 TDD 或豁免证据
  - 执行模式: AFK
  - 涉及文件: `scripts/audit_skills.py`
  - 完成标准: 任务1.1中的有效记录通过，缺失或非法证据被拒绝
  - 验证方式: `python -m unittest tests.test_audits.SkillStructureAuditTests -v`
- [√] 2.2 REFACTOR: 提取可复用的 TDD evidence 校验逻辑，保持现有 QA 结果和错误消息可读
  - 执行模式: AFK
  - 涉及文件: `scripts/audit_skills.py`
  - 完成标准: 校验逻辑无重复分支，现有 QA schema v2 测试继续通过
  - 验证方式: `python -m unittest discover -s tests -v`

## 3. 显式测试入口

- [√] 3.1 新增 `test` Skill，并在路由和 bootstrap 中注册 `~test [scope]`
  - 执行模式: AFK
  - 涉及文件: `Codex/Skills/CN/**`, `Claude/Skills/CN/**`
  - 完成标准: 用户可发现命令、明确范围、授权边界、与 `tdd`/`qa-review` 的衔接和生产代码限制
  - 验证方式: `python scripts/audit_skills.py`
- [√] 3.2 为 `~test` 命令和索引新增语义审计与回归断言
  - 执行模式: AFK
  - 涉及文件: `scripts/audit_skills.py`, `tests/test_audits.py`
  - 完成标准: 遗漏命令注册或 Skill 索引时审计/测试会失败
  - 验证方式: `python -m unittest discover -s tests -v`

## 4. TDD 证据文档化

- [√] 4.1 将 `qa-review` 模板更新为 schema v3，并说明 TDD/豁免字段约束
  - 执行模式: AFK
  - 涉及文件: `Codex/Skills/CN/**`, `Claude/Skills/CN/**`
  - 完成标准: 新生成 QA 证据可被审计器验证，旧 v1/v2 文件仍兼容
  - 验证方式: `python scripts/audit_skills.py`
- [√] 4.2 更新 `tdd`、方案模板和开发实施说明，使证据写入时机与 QA 步骤一致
  - 执行模式: AFK
  - 涉及文件: `Codex/Skills/CN/**`, `Claude/Skills/CN/**`
  - 完成标准: TDD 路径和 TDD-EXEMPT 路径均指向结构化 QA 证据
  - 验证方式: `python scripts/audit_skills.py`

## 5. 知识库与验证

- [√] 5.1 同步技能模块知识库、架构 ADR 和 CHANGELOG
  - 执行模式: AFK
  - 涉及文件: `helloagents/1.x/wiki/modules/skills.md`, `helloagents/1.x/wiki/arch.md`, `helloagents/1.x/CHANGELOG.md`
  - 完成标准: 文档反映 `~test`、schema v3 和 ADR-007
  - 验证方式: `python scripts/audit_skills.py`
- [√] 5.2 执行安全、技能审计和全量单元测试
  - 执行模式: AFK
  - 涉及文件: 本次改动文件
  - 完成标准: 所有命令通过，无新增安全问题
  - 验证方式: `python scripts/audit_safety.py`; `python scripts/audit_skills.py`; `python -m unittest discover -s tests -v`
