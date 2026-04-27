---
name: multi_model
description: 定义多模型协作在 ANALYZE/DESIGN/DEVELOP 各阶段的触发条件、执行规则和约束。多模型审查触发时读取本 Skill。
---

# 多模型协作分析与审查规则

本模块定义多模型协作在 ANALYZE / DESIGN / DEVELOP 以及命令路径（~plan/~exec）中的统一行为。

---

## 规则概述

```yaml
规则名称: 多模型协作分析与审查规则
适用范围:
  - ANALYZE: 项目上下文与技术风险交叉验证
  - DESIGN: 方案交叉评审与实施计划闸门
  - DEVELOP: 完成后一致性复核与风险分级
  - 命令路径: ~plan / ~exec 的多模型复核步骤
核心目标:
  - 降低单模型偏差风险
  - 在关键决策前完成交叉验证
  - 保证方案文档与代码实现可追溯一致
```

---

## 协作策略开关

```yaml
读取配置:
  - MULTI_MODEL_POLICY（BALANCED / STRICT）
  - SIMPLE_TASK_NO_COLLAB_CONFIRM（0 / 1）
  - PHASE2_HARD_STOP_CONFIRM（0 / 1）
  - FORCE_MM_LIGHTWEIGHT_MIN_FILES（整数，默认2）

BALANCED:
  - 按风险触发多模型协作
  - simple 任务默认可不协作

STRICT:
  - 默认启用多模型协作
  - simple 任务若跳过协作，按 SIMPLE_TASK_NO_COLLAB_CONFIRM 决定是否必须确认

强制升级联动:
  - 用户已确认启用多模型协作，且预估改动文件数 >= FORCE_MM_LIGHTWEIGHT_MIN_FILES 时：
    - R1 快速流程必须升级为 R2 简化流程
    - 进入 ANALYZE → DESIGN，确保生成/复核方案包

PHASE2_HARD_STOP_CONFIRM = 1:
  - DESIGN 阶段输出最终实施计划后，必须询问:
    "Shall I proceed with this plan? (Y/N)"
  - 未收到明确 Y 前，不得继续 DEVELOP 执行
```

---

## 与 hello-subagent 的边界

```yaml
关系定位:
  - multi_model 负责多模型分析/审查/验收
  - hello-subagent 负责并行子任务编排、上下文裁剪、文件边界和返回契约

触发联动:
  - 当多模型审查可拆分为多个独立风险域时:
    - 读取 `hello-subagent` Skill
    - 按其规则生成审查型子任务包
    - 审查型子代理保持只读，不直接修改本地文件

边界约束:
  - multi_model 的无写入原则优先于 hello-subagent 的执行型子代理规则
  - 多模型输出只能作为建议、风险报告或 unified diff
  - 最终采纳、代码修改、知识库同步仍由主代理执行
```

---

## 分阶段协作规则

### ANALYZE 阶段

```yaml
触发条件:
  - TASK_COMPLEXITY = complex
  - 或用户显式要求多模型交叉验证

执行:
  - 基于分析结果请求外部模型做风险交叉检查
  - 输出共识项与分歧项，分歧留待 DESIGN 阶段仲裁
```

### DESIGN 阶段（Phase2）

```yaml
目标:
  - 对候选方案进行交叉评估并收敛为实施计划

执行:
  - 主组合: claude + gemini
  - 冲突仲裁: codex（按需追加）
  - 输出 step-by-step 实施计划与关键风险

Hard Stop（可选）:
  - PHASE2_HARD_STOP_CONFIRM = 1 时强制 Y/N 闸门
```

### DEVELOP 阶段（Phase3/Phase4）

```yaml
目标:
  - 在编码实施前后进行一致性与风险复核

执行:
  - 原型建议仅作为参考，不直接落地
  - 本地改动后执行一致性复核:
    proposal/tasks 与代码实现对照

风险分级:
  - P0 / Must Fix: 安全漏洞、关键逻辑错误（阻断）
  - P1 / Should Fix: 质量与稳定性风险（警告）
  - P2 / Note: 优化建议（信息）
```

---

## 执行约束（CRITICAL）

```yaml
无写入原则:
  - 外部模型仅用于分析/审查，不直接修改本地文件
  - 提示词必须追加:
    "OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications."

会话连续性:
  - 首次调用保存 SESSION_ID
  - 同一审查链路优先复用 SESSION_ID

输出要求:
  - 协作模式（启用/未启用）
  - 调用摘要（模型、success、SESSION_ID）
  - 共识结论/冲突结论
  - 最终建议与下一步
```

---

## 失败回退

```yaml
单模型失败:
  - 记录失败原因
  - 使用其余模型继续
  - 输出"部分协作失败"

全部失败:
  - 回退本地单模型分析/审查
  - 输出警告并提示检查桥接工具可用性
```
