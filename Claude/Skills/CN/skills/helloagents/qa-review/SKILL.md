---
name: qa-review
description: 有方案包或用户要求结构化 QA 时，在步骤7质量检查与测试完成后审查范围、分级问题并记录验证证据。
invocation: model
side_effects: may_write_plan
requires: []
completion_criteria: 对需要结构化 QA 的任务完成范围审查、验证记录、发现项分级与归档门禁，并按方案包或独立输出位置保存证据。
---

# QA Review

**目标:** 将开发实施后的质量判断收敛为可复核证据，避免只用自然语言声明“已验证”。

---

## 适用场景

**应触发:**
- 当前任务存在完整/轻量方案包，或用户明确要求结构化 QA 证据，并已完成步骤7质量检查与测试。
- 满足上述条件后，在交付、归档或多模型验收前形成主代理本地 QA 证据。

**不应触发:**
- 普通只读咨询、需求分析或方案设计，且用户未要求结构化 QA。
- 没有方案包、本轮没有改动，且用户未要求结构化 QA。
- 自适应无方案包的低/中风险改动，且用户未要求结构化 QA；此类任务在最终摘要记录实际验证命令、结果和剩余风险。

---

## 审查范围

审查基线:
- 默认只审查本次变更、受影响契约、必要依赖和本轮新增证据；未被本轮触达且已有有效验证证据的既有代码不主动重复审查。
- 已完成的分析、审查和验证证据可以直接复用，不因上下文压缩、会话恢复或代理切换而重新执行；验证有效性统一按 `verification-before-completion` 判断。
- 仅当相关代码、依赖或环境已变化、证据缺失或失效、出现新的风险/故障信号，或用户明确要求时，才扩大到既有代码或重新验证；处于 Bug 修复任务中本身不要求重复已完成的有效验证。

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

用户明确要求结构化 QA 但没有方案包时，使用用户指定位置或项目已有约定；均未指定时在工作目录选择不覆盖现有文件的 `qa-review.json` 或带数字后缀的文件，不为保存证据补建方案包或迁移 history。此时 `task_verification` 对照已授权范围的成功标准。

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
      "command": "[实际执行或有效复用的验证命令]",
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
- `commands`: 记录实际执行或有效复用的验证命令，在 `note` 说明结果、复用来源及其有效依据；无法执行时写明原因。
- `task_verification`: 对 `task.md` 中已标记完成的任务逐项核对；独立 QA 对照用户授权范围的成功标准。
- `tdd`: schema v3 必填。`classification` 为 `mandatory`、`recommended`、`exempt` 或 `uncertain`；`decision=tdd` 时必须记录 RED 失败与 GREEN/REFACTOR/VERIFY 通过；`decision=exempt` 时必须记录 `exempt_reason` 和 `alternative_verification`。`mandatory` 不得豁免。

### 可执行归档门禁

- 未解决 P0: `gate_status=blocked`，必须修复并重跑验证，禁止风险接受、迁移和成功总结。
- 未解决 P1: `gate_status=blocked`，先在已有授权内修复并验证；需要额外决定或仍有剩余风险时设置 `PENDING_INTERACTION=QA_RISK_DECISION`，只有用户明确接受后才标记 `accepted` 并改为 `gate_status=risk_accepted`。
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

- 有方案包时已读取完整三件套，或合法轻量方案包的 `task.md` 与元数据；用户单独要求结构化 QA 时已核对授权范围与成功标准。
- 已运行可用验证命令，或记录无法运行的具体原因和替代验证。
- 审查范围限于本次变更、受影响契约和有新证据的既有路径；重复审查已有有效证据时已说明触发原因。
- 已对阻断项、警告项和信息项做分级。
- 已按 P0/P1/P2 推导并执行 `gate_status`，不存在绕过的本地 QA 阻断项。
- 新生成的 schema v3 证据已写入可审计的 `tdd` 对象，或明确记录 TDD-EXEMPT 与替代验证。
- 需要结构化 QA 时已按输出位置规则写入证据，或明确记录无法写入的具体原因。
- 自适应无方案包路径不以缺少 `qa-review.json` 视为失败，由 develop 最终摘要承担验证证据。
