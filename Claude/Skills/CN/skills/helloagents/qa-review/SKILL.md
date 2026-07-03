---
name: qa-review
description: 统一质量审查、验证命令、阻断修复建议和交付前 QA 证据记录。步骤7质量检查与测试完成后读取。
invocation: model
side_effects: may_write_plan
requires: []
completion_criteria: 已完成范围审查、验证命令记录、阻断项分级，并在当前方案包中写入 qa-review.json 或记录无法写入原因。
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
- 需求覆盖: 对照 `why.md` 核心场景和 `task.md` 完成标准。
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
  "schema_version": 1,
  "qa_mode": "standard",
  "scope": "本次方案包覆盖范围",
  "outcome": "clean",
  "conclusion": "验证结论摘要",
  "findings": [],
  "file_references": [],
  "commands": [
    {
      "command": "python scripts/audit_skills.py",
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
  ]
}
```

字段约束:
- `qa_mode`: `standard` 或 `deep`。
- `outcome`: `clean` 或 `findings`。
- `commands`: 必须记录本轮实际执行的验证命令；无法执行时写明原因。
- `task_verification`: 对 `task.md` 中已标记完成的任务逐项核对。

---

## 完成门禁

- 已读取 `why.md`、`how.md`、`task.md` 中与本轮实现相关的范围和任务。
- 已运行可用验证命令，或记录无法运行的具体原因和替代验证。
- 已对阻断项、警告项和信息项做分级。
- 已写入 `qa-review.json`，或因只读/无方案包等原因明确记录无法写入。
