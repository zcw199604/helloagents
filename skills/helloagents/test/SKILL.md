---
name: test
description: 显式测试命令；为指定模块或最近改动补充测试，记录 TDD 或 TDD-EXEMPT 证据，并复用现有 QA 门禁。
invocation: user
side_effects: may_write_code_and_docs
requires:
  - tdd
  - develop
completion_criteria: 测试范围、TDD 决策、验证结果和 schema v3 QA 证据均已记录；发现缺陷时未擅自扩大为生产修复。
---

# 测试命令

Trigger: ~test [scope]

**目标:** 提供明确、可追溯的测试补齐入口，而不是把测试工作隐藏在一般实现请求中。

## 范围与授权

- `scope` 指定文件、模块、行为或最近改动时，以该范围为准。
- 未提供 `scope` 时，优先从当前方案包或最近 Git 改动推导；仍无法确定时，按交互格式追问，不猜测测试目标。
- `~test` 需要命令确认。确认后创建或复用覆盖该范围的轻量方案包，并使用现有 `MODE_EXECUTION` 授权进入开发实施与 QA 门禁。
- 默认只新增或调整测试、测试数据、方案包和 QA 证据；测试暴露未实现或错误行为时，记录失败并转入常规方案设计，不自动修改生产代码。

## 执行流程

1. 读取 `tdd`，标记 `mandatory`、`recommended`、`exempt` 或 `uncertain` 分类。
2. 在轻量方案包的验证策略中写明目标行为、测试命令和 TDD 决策。
3. 新功能或可复现缺陷按 RED → GREEN → REFACTOR → VERIFY 执行；不得把测试直接通过的情况伪装成 RED。
4. 为已存在生产行为补充表征测试时，可标记 `TDD-EXEMPT`，但必须说明生产实现早于本次测试且记录替代验证。
5. 开发实施步骤7.5写入 schema v3 `qa-review.json` 的 `tdd` 对象，再按既有 QA 门禁处理。

## 完成门禁

- 测试目标和范围可复核。
- `decision=tdd` 时 RED 失败、GREEN/REFACTOR/VERIFY 通过的证据完整。
- `decision=exempt` 时 `TDD-EXEMPT` 原因和替代验证完整。
- 未在用户只要求测试时擅自修改生产行为。
