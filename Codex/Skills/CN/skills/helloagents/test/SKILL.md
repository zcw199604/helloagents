---
name: test
description: 显式测试命令；为指定模块、行为或最近改动补充测试，并在摘要中记录 TDD 或 TDD-EXEMPT 依据。
invocation: user
side_effects: may_write_tests
requires:
  - tdd
completion_criteria: 测试范围、TDD 决策和验证结果已在摘要中记录；发现缺陷时未擅自扩大为生产修复。
---

# 测试命令

Trigger: ~test [scope]

**目标:** 提供明确的测试补齐入口。它是一次写入范围限于测试的普通改动，按 `develop` 默认流程执行，不创建方案包或 `qa-review.json`。

## 范围与授权

- `scope` 指定文件、模块、行为或最近改动时，以该范围为准。
- 未提供 `scope` 时，从最近的 Git 改动或当前任务推导；仍无法确定时追问，不猜测测试目标。
- 只新增或调整测试和测试数据。测试暴露未实现或错误的生产行为时，记录失败并报告，由用户决定是否修复；不自动修改生产代码。

## 执行流程

1. 读取 `tdd`，判定适用性。
2. 新功能或可复现缺陷按 RED → GREEN → REFACTOR → VERIFY 执行；不得把直接通过的测试当作 RED。
3. 为已存在的生产行为补表征测试时标记 `TDD-EXEMPT`，说明生产实现早于本次测试、无法构造真实 RED，并记录替代验证。
4. 运行新增测试和相关既有测试，按 `verification-before-completion` 核对后输出摘要。

用户同时要求结构化 QA 证据时，按 `qa-review` 的独立输出规则保存。

## 完成门禁

- 测试目标和范围可复核。
- 摘要包含 TDD 决策或 `TDD-EXEMPT` 原因、实际测试命令和结果。
- 未在用户只要求测试时修改生产行为。
