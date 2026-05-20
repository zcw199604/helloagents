---
name: lifecycle
description: 方案包生命周期与状态变量管理；创建/迁移方案包、扫描遗留方案、状态变量切换时读取
---

# 方案包生命周期管理 - 详细规则

**适用范围:** 方案包创建（方案设计/轻量迭代）、迁移（开发实施 P3 步骤 12）、遗留扫描（阶段完成时）、状态变量管理。

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
