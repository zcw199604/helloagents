---
name: qa-review
description: 统一质量审查、验证命令、阻断修复建议和交付前 QA 证据记录。步骤7质量检查与测试完成后读取。
invocation: model
side_effects: may_write_plan
requires: []
completion_criteria: 已完成范围审查、验证命令记录、发现项分级与归档门禁判定，并在当前方案包中写入 qa-review.json 或记录无法写入原因。
---

# QA Review

**目标:** 将开发实施后的质量判断收敛为可复核证据，避免只用自然语言声明“已验证”。

---

## 适用场景

**应触发:**
- 步骤7质量检查与测试完成后。
- `~exec`、`~auto` 或交互确认模式准备报告完成前。
- 多模型验收前需要先形成主代理本地 QA 证据。

**不应触发:**
- 只读咨询、需求分析或方案设计尚未进入实现。
- 没有方案包且本轮没有代码/文档改动。

---

## 审查范围

至少覆盖:
- 需求覆盖: 完整方案包对照 `why.md` 核心场景；轻量方案包对照 `task.md` 的轻量方案包元数据和完成标准。
- 实现质量: 正确性、安全、可靠性、可维护性和最小改动边界。
- 验证证据: 记录实际运行的命令、结果摘要和未覆盖原因。
- 阻断项: 对失败测试、安全问题、关键逻辑错误给出文件定位和修复方向。

---

## QA 证据文件

默认写入当前方案包目录:

```text
helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/qa-review.json
```

如果方案包已迁移，则证据随方案包位于:

```text
helloagents/<branch-name>/history/YYYY-MM/YYYYMMDDHHMM_<feature>/qa-review.json
```

最小字段:

```json
{
  "schema_version": 3,
  "qa_mode": "standard",
  "scope": "本次方案包覆盖范围",
  "outcome": "clean",
  "gate_status": "passed",
  "conclusion": "验证结论摘要",
  "findings": [],
  "file_references": [],
  "commands": [
    {
      "command": "[本轮实际执行的验证命令]",
      "result": "passed",
      "note": "输出摘要"
    }
  ],
  "task_verification": [
    {
      "task": "1.1",
      "status": "passed",
      "evidence": "完成标准对应证据"
    }
  ],
  "tdd": {
    "classification": "mandatory",
    "decision": "tdd",
    "target_behaviors": ["本次新增的可观察行为"],
    "red": {"command": "[测试命令]", "result": "failed", "summary": "失败原因匹配目标行为"},
    "green": {"command": "[测试命令]", "result": "passed", "summary": "最小实现后通过"},
    "refactor": {"performed": false, "command": "[测试命令]", "result": "passed", "summary": "无需额外重构"},
    "verify": {"command": "[验证命令]", "result": "passed", "summary": "相关验证通过"}
  }
}
```

字段约束:
- `schema_version`: 新生成证据固定为 `3`；审计器继续读取历史 v1/v2。
- `qa_mode`: `standard` 或 `deep`。
- `outcome`: `clean` 或 `findings`。
- `gate_status`: `passed`、`blocked` 或 `risk_accepted`。
- `findings`: 每项必须包含 `severity` (`P0/P1/P2`)、`status` (`open/resolved/accepted`)、`title` 和 `evidence`；P0 不允许标记为 `accepted`。
- `commands`: 必须记录本轮实际执行的验证命令；无法执行时写明原因。
- `task_verification`: 对 `task.md` 中已标记完成的任务逐项核对。
- `tdd`: schema v3 必填。`classification` 为 `mandatory`、`recommended`、`exempt` 或 `uncertain`；`decision=tdd` 时必须记录 RED 失败与 GREEN/REFACTOR/VERIFY 通过；`decision=exempt` 时必须记录 `exempt_reason` 和 `alternative_verification`。`mandatory` 不得豁免。

### 可执行归档门禁

- 未解决 P0: `gate_status=blocked`，必须修复并重跑验证，禁止风险接受、迁移和成功总结。
- 未解决 P1: `gate_status=blocked`，设置 `PENDING_INTERACTION=QA_RISK_DECISION`；只有用户明确接受后才将该项标记为 `accepted` 并改为 `gate_status=risk_accepted`。
- 仅有 P2 或所有发现均已解决: `gate_status=passed`，可继续后续步骤。
- `outcome=clean` 时 `findings` 必须为空；任何发现均使用 `outcome=findings`。

### 轻量方案包元数据分支

当 `task.md` 顶部标注 `模式: 轻量迭代` 时:

- 从“轻量方案包元数据”的范围摘要和核心场景生成 `scope`，不得要求不存在的 `why.md`。
- 从知识库同步、ADR 和验证策略核对实现边界，不得要求不存在的 `how.md`。
- 安全检查、实际验证命令、findings 分级和 `task_verification` 与完整方案包保持同一门槛。
- 元数据缺失时将方案包判定为不完整并停止，不得静默降低 QA 标准。

---

## 完成门禁

- 已读取完整方案包三件套，或读取合法轻量方案包的 `task.md` 与轻量方案包元数据。
- 已运行可用验证命令，或记录无法运行的具体原因和替代验证。
- 已对阻断项、警告项和信息项做分级。
- 已按 P0/P1/P2 推导并执行 `gate_status`，不存在绕过的本地 QA 阻断项。
- 新生成的 schema v3 证据已写入可审计的 `tdd` 对象，或明确记录 TDD-EXEMPT 与替代验证。
- 已写入 `qa-review.json`，或因只读/无方案包等原因明确记录无法写入。
