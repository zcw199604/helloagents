# Skills 模块

## 目的

维护 HelloAGENTS 的模块化 skill 体系，降低入口上下文负载，减少职责重叠，并保持 Codex/Claude 双端一致。

## 规范

### 轻量入口

`SKILL.md` 应优先保留:
- frontmatter 元数据
- 目标
- 触发条件或流程索引
- 职责边界
- 正反例
- 完成门禁

长模板、协议、输出样例和细则应移动到 `references/`。

### 索引矩阵

`skills/helloagents/SKILL_INDEX.md` 是 skill 职责、触发、输入输出和依赖的维护索引。新增或改名 skill 时必须同步更新。

### 审计

修改 skill 后运行:

```bash
python scripts/audit_skills.py
```

审计通过表示:
- 必需 frontmatter 字段齐全。
- `references/*.md` 引用存在。
- Codex/Claude skill 树内容一致。
- bootstrap 入口包含索引矩阵指针。

### 文档化追问

需求分析阶段遇到项目黑话、缩写、业务角色、状态名、流程名或命名分歧时，先追问术语含义、边界、反例和推荐命名。确认后的术语沉淀到 `wiki/glossary.md`。

### ADR 候选

方案设计阶段如果出现模块边界、接口契约、数据边界、依赖方向、命名体系或迁移策略取舍，应在 `how.md` 中记录 ADR 候选。没有实际取舍时，明确写明本次无 ADR 候选。

## 变更历史

| 日期 | 变更 |
|---|---|
| 2026-07-02 | 拆薄大型 skill、补索引矩阵、统一元数据、增加审计脚本 |
| 2026-07-02 | 吸收 grill-with-docs 核心机制：领域语言、文档化追问、ADR 候选 |
| 2026-07-02 | 修复交叉审查发现的高价值 P1/P2 规则冲突并增强审计脚本 |
