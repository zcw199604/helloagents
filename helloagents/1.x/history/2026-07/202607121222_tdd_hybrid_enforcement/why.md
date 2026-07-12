# 变更提案: TDD 混合执行与证据门禁

## 需求背景

当前 1.x 已在需求分析、方案设计和开发实施中定义 TDD 适用性、`TDD-EXEMPT` 和 RED/GREEN/REFACTOR/VERIFY 流程，但 `qa-review.json` 未结构化保存这些证据，`audit_skills.py` 也无法拒绝缺失证据的新增 QA 记录。同时，用户没有一个专门补测目标模块的显式命令入口。

## 变更内容

1. 新增 `~test [scope]` 测试命令与对应 `test` Skill，提供受控的测试补齐入口。
2. 将新写入的 QA 证据升级为 schema v3，加入结构化 `tdd` 字段。
3. 扩展审计器和回归测试，校验 TDD 阶段证据或豁免原因。
4. 同步 Codex/Claude 双端规则、方案模板和知识库。

## 范围边界

- **范围内:** 中文双端 Skill、路由/命令说明、QA 模板、TDD 规则、Python 审计器及其单元测试、知识库。
- **范围外:** 新增第三方依赖、改写宿主 CLI 运行时、迁移历史 schema v1/v2 的现有 QA 文件、自动修复生产缺陷。
- **拆分说明:** 命令入口、证据契约和审计验证共享同一交付闭环，作为一个可验证切片实施。

## 影响范围

- **模块:** skills、routing、qa-review、templates、audit_skills、knowledge base。
- **文件:** Codex/Claude 双端 Skill 树、`scripts/audit_skills.py`、`tests/test_audits.py`、`helloagents/1.x/wiki/*`。
- **API:** `qa-review.json` 新增 schema v3 契约；v1/v2 保持只读兼容。
- **数据:** 无外部数据变更。

## 核心场景

### 需求: 显式补测入口
**模块:** routing / test

#### 场景: 用户输入 `~test path/to/module`
路由识别测试命令，读取 `test` 与 `tdd` Skill，限定目标范围并按现有执行授权与 QA 规则形成测试交付。
- 不擅自扩大为生产代码修复。
- 缺少范围时要求用户补充或使用最近改动。

### 需求: 可审计的 TDD 证据
**模块:** qa-review / audit_skills

#### 场景: 新功能或 Bug 修复完成 QA
QA 证据以 schema v3 写入 `tdd` 对象，记录分类、决策、目标行为和 RED/GREEN/REFACTOR/VERIFY 结果。
- `decision=tdd` 时 RED 必须失败，其他阶段必须通过。
- `decision=exempt` 时必须记录豁免理由和替代验证。

### 需求: 历史兼容
**模块:** audit_skills

#### 场景: 审计已有归档方案
schema v1/v2 的 QA 证据继续按旧规则验证；只有 schema v3 启用新的 TDD 字段门禁。
- 历史归档不因本次升级失效。

## 风险评估

- **风险:** `~test` 与现有 `~exec` 授权路径语义冲突。
  **缓解:** 明确它创建或使用轻量测试方案包，并复用现有执行授权和 QA 门禁。
- **风险:** schema 升级误伤历史 QA 文件。
  **缓解:** 审计器显式保留 v1/v2 分支，仅对 v3 强制 `tdd` 契约。
- **风险:** 证据字段增加代理负担。
  **缓解:** 统一写入现有 `qa-review.json`，并给出最小模板与豁免路径。
