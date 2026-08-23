---
name: design
description: 方案设计阶段详细规则；进入方案设计时读取；包含方案构思、任务拆解、风险评估、方案包创建。详细规则按需读取 references。
invocation: model
side_effects: may_write_plan
requires:
  - templates
  - lifecycle
  - output-format
completion_criteria: 已创建完整方案包 why.md/how.md/task.md，并给出可执行任务与验收标准。
---

# 方案设计

**目标:** 构思可行方案并制定详细执行计划，生成 `helloagents/<branch-name>/plan/` 下的方案包。

**前置条件:** 需求分析已完成且评分 ≥ 7 分；评分不足时返回需求分析追问。

---

## 流程

1. 方案构思：产出 2-3 个可比较方案，或在推进模式下选择保守可执行方案。
2. 详细规划：创建 `why.md`、`how.md`、`task.md`，并处理领域语言和 ADR 候选。
3. 阶段输出：按 `output-format` 输出方案设计完成摘要和遗留方案提示。

---

## Reference 选择

| 场景 | 读取文件 |
|---|---|
| 构思方案、风险评估、方案选择交互 | `references/ideation.md` |
| 创建方案包、任务拆解、TDD/子代理标注 | `references/detailed-planning.md` |
| 阶段完成输出、多模型审查询问、转换规则 | `references/output-and-transition.md` |

---

## 正反例

**应触发:**
- 需求分析评分达标后，用户确认继续设计。
- 用户输入 `~plan` 或 `~design`。
- 用户提出高风险新功能、重大重构、架构/技术取舍或明确要求比较方案。

**不应触发:**
- 用户只要求解释代码或回答事实问题。
- 用户要求执行已有方案包；应进入 `develop`。
- 需求评分 < 7 且缺少关键目标、范围或验收标准。
- 用户已明确授权低/中风险普通改动，且无需架构决策或方案持久化；可直接进入自适应开发。

---

## 完成门禁

- 方案包目录符合 `helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/`。
- `why.md` 说明背景、范围、影响、核心场景和风险。
- `how.md` 说明技术方案、边界、ADR 候选/结论、测试与部署。
- `task.md` 任务可执行、可验证，且标注 TDD 或 TDD-EXEMPT。
- 若需求分析存在领域语言候选，方案包已安排更新 `wiki/glossary.md`。
- 已按 `lifecycle` 扫描并提示遗留方案。
