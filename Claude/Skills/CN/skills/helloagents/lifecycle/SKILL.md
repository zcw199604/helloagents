---
name: lifecycle
description: 方案包生命周期与状态变量管理；创建/迁移方案包、扫描遗留方案、状态变量切换时读取
invocation: model
side_effects: may_move_plan_packages
requires:
  - output-format
completion_criteria: 方案包状态、迁移位置、history 索引和遗留扫描均已完成。
---

# 方案包生命周期管理 - 详细规则

**适用范围:** 方案包创建（方案设计/轻量迭代）、迁移（开发实施 P3 步骤 12）、遗留扫描（阶段完成时）、状态变量管理。

---

## 职责边界

`lifecycle` 只负责方案包生命周期：创建路径、状态符号、迁移、遗留扫描、状态变量。

不由 `lifecycle` 负责的事项:
- 知识库内容质量、模块文档同步、ADR 内容维护 → 由 `kb` 负责
- 开发实施任务执行和质量验证 → 由 `develop` 负责
- 用户可见输出模板 → 由 `output-format` 负责

---

## G11 | 方案包生命周期

<plan_package_lifecycle>

**任务状态符号:**
- `[ ]` 待执行
- `[√]` 已完成
- `[X]` 执行失败
- `[-]` 已跳过
- `[?]` 待确认

**创建新方案包(处理同名冲突):**
```yaml
路径: helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/
冲突处理:
  1. 检查目录是否存在
  2. 不存在 → 直接创建
  3. 存在 → 使用版本后缀 _v2, _v3...
```

**已执行方案包(P3阶段强制迁移):**
```yaml
1. 更新task.md任务状态（使用上述任务状态符号）
2. 迁移至 helloagents/<branch-name>/history/YYYY-MM/（保持目录名，同名覆盖）
3. 更新 helloagents/<branch-name>/history/index.md
```

**遗留方案扫描:**
```yaml
触发时机（满足任一）:
  - 方案包创建后: 方案设计完成、规划命令完成、轻量迭代完成
  - 方案包迁移后: 开发实施完成、执行命令完成、全授权命令完成

扫描规则:
  - 扫描: helloagents/<branch-name>/plan/ 目录下所有方案包
  - 排除: 本次创建/执行的方案包
  - 条件: 检测到≥1个遗留方案包时才输出提示

输出格式:
  📦 遗留方案: 检测到 X 个未执行的方案包:
    - {方案包名称1}
    - {方案包名称2}
    ...
  是否需要迁移至历史记录?
```

</plan_package_lifecycle>

---

## G12 | 状态变量管理

```yaml
CREATED_PACKAGE: 方案设计阶段创建的方案包路径
  设置: 详细规划完成创建后
  清除: 开发实施步骤1读取后或流程终止

CURRENT_PACKAGE: 当前执行的方案包路径
  设置: 开发实施步骤1确定方案包后
  清除: 方案包迁移至 history/ 后

MODE_FULL_AUTH: 全授权命令激活状态
MODE_PLANNING: 规划命令激活状态
MODE_PLANNING_INTERACTIVE: 交互式规划激活状态
MODE_EXECUTION: 执行命令激活状态
```

---

## 正反例

**应触发:**
- 方案设计完成后创建 `helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/`。
- 开发实施完成后把方案包迁移到 `history/YYYY-MM/`。
- 阶段完成时扫描 `plan/` 中剩余未执行方案包。

**不应触发:**
- 只更新 `wiki/modules/*.md` 的内容；这是 `kb` 的职责。
- 只回答用户某个方案包字段含义；不需要迁移或扫描状态。

---

## 完成门禁

- 方案包路径符合 `helloagents/<branch-name>/plan|history/YYYY-MM/YYYYMMDDHHMM_<feature>/`。
- `task.md` 中每个任务都有 `[ ]`、`[√]`、`[X]`、`[-]` 或 `[?]` 状态。
- 迁移后 `history/index.md` 已更新。
- 遗留扫描已排除本次创建或执行的方案包。
