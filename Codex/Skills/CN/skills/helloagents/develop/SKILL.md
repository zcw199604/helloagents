---
name: develop
description: 开发实施阶段详细规则；进入开发实施或系统化调试时读取。完整入口、步骤、门禁和输出规则按需读取 references。
invocation: model
side_effects: may_write_code_and_docs
requires:
  - kb
  - lifecycle
  - output-format
  - qa-review
completion_criteria: 已执行方案包任务、完成验证、记录 QA 证据、同步知识库与 CHANGELOG，并按 lifecycle 迁移方案包或记录无法迁移原因。
---

# 开发实施

**目标:** 按方案包任务清单执行代码或文档改动，完成质量验证，同步知识库，并迁移已执行方案包。

---

## 前提

进入开发实施必须满足任一条件：
- 方案设计完成后用户明确确认。
- 全授权命令 `~auto` 激活，且 `AUTH_WORKFLOW_ID=WORKFLOW_ID`。
- 执行命令 `~exec` 激活，且 `AUTH_WORKFLOW_ID=WORKFLOW_ID`。
- 系统化调试模式命中且仍处于只读根因调查阶段。

若不满足，重新按 `routing` Skill 判定，不直接修改代码。

---

## Reference 选择

| 场景 | 读取文件 |
|---|---|
| 开发实施入口检查、13 步执行流程、调试门禁、测试门禁、迁移规则 | `references/entry-and-steps.md` |
| 代码规范、阶段完成输出填充字段 | `references/standards-and-output.md` |
| 阶段转换、异常后续处理 | `references/phase-transition.md` |

---

## 职责边界

- `develop` 管执行顺序、质量门禁和最终集成。
- `kb` 管知识库内容质量、创建、同步和一致性修正。
- `lifecycle` 管方案包状态符号、迁移算法、遗留方案扫描和状态变量。
- `output-format` 管用户可见输出模板；本 skill 只提供字段含义。
- `qa-review` 管交付前质量审查和 QA 证据文件。
- `hello-subagent` 只在任务可并行且写入范围互斥时编排子代理。

---

## 正反例

**应触发:**
- 用户确认执行刚完成的方案设计。
- 用户输入 `~exec` 执行已有方案包。
- `~auto` 已授权从分析、设计连续推进到实现。
- 用户报告测试失败、构建失败、运行异常或 flaky，需要先只读复现并定位根因。

**不应触发:**
- 用户只要求分析方案或比较技术路线。
- 没有方案包且用户未授权全流程推进，也未命中系统化调试只读入口。
- EHRB 风险无法规避且尚未确认。

---

## 完成门禁

- 已读取并执行完整方案包三件套，或合法轻量方案包的 `task.md` 与轻量方案包元数据。
- 所有任务标记为 `[√]`、`[X]`、`[-]` 或 `[?]`，非完成项有备注。
- 安全检查、相关测试或替代验证已执行并记录结果。
- 当前方案包已写入 `qa-review.json`，或记录无法写入原因。
- 知识库与 `CHANGELOG.md` 已同步，或记录缺失/无法同步原因。
- 已按 `lifecycle` 迁移方案包到 `history/`，或明确说明阻塞原因。
- 已执行 `RESET_WORKFLOW_STATE`，命令授权和等待态均未残留。
