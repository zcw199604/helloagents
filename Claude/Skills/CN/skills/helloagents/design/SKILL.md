---
name: design
description: 方案设计规则；高风险、架构取舍或用户明确要求规划时读取；包含方案构思、任务拆解、风险评估和方案包创建。详细规则按需读取 references。
invocation: model
side_effects: may_write_plan
requires:
  - templates
  - lifecycle
completion_criteria: 已创建合法方案包，任务可执行、可验证，并按授权进入实施或等待确认。
---

# 方案设计

**目标:** 构思可行方案并制定执行计划，生成 `helloagents/<branch-name>/plan/` 下的方案包。

**前置条件:** 目标、范围和成功标准已明确，不存在阻塞设计的业务缺口；事实不足时先只读调查，确需用户决定时才追问。

---

## 流程

1. **方案构思:** 存在实质的架构、技术或业务取舍时比较可行方案；路径明确时直接采用最小充分方案。
2. **详细规划:** 创建方案包，处理领域语言和 ADR 候选，完成自审。
3. **输出与后续:** 按授权进入实施、停止或等待确认，并提示遗留方案。

任务拆解要求：先列出将创建、修改和测试的文件及其职责，再拆成可独立验证的最小任务。每个任务包含执行模式、涉及文件、完成标准和验证方式，并标注 TDD 或 TDD-EXEMPT；不留 `TODO`、`TBD`、“补充适当处理”等占位描述，不把互相依赖的多个子系统混成一个任务。

---

## Reference 选择

| 场景 | 读取文件 |
|---|---|
| 是否需要比较方案、评估标准、方案选择 | `references/ideation.md` |
| 创建方案包、任务清单规则、ADR、自审 | `references/detailed-planning.md` |
| 设计完成后的输出和后续处理 | `references/output-and-transition.md` |

---

## 正反例

**应触发:**
- 用户输入 `~plan`、`~design` 或 `~auto`。
- 用户明确要求设计方案或比较方案，且目标、边界和成功标准已明确。
- 高风险新功能、重大重构、架构或技术取舍。

**不应触发:**
- 用户只要求解释代码或回答事实问题。
- 用户要求执行已有方案包；应进入 `develop`。
- 已有改动授权的低/中风险改动，且不需要架构决策或跨会话恢复；直接进入 `develop`。
- 缺少影响设计正确性的关键目标、范围或验收标准；先按 `analyze` 澄清。

---

## 完成门禁

- 方案包目录符合 `helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/`。
- 完整方案包: `why.md` 说明背景、范围、影响、核心场景和风险；`how.md` 说明技术方案、边界、ADR 和测试部署；轻量方案包的 `task.md` 元数据齐全。
- `task.md` 任务可执行、可验证，并标注 TDD 或 TDD-EXEMPT。
- 存在领域语言候选时，方案包已安排更新 `wiki/glossary.md`。
- 已按 `lifecycle` 扫描并提示遗留方案。
