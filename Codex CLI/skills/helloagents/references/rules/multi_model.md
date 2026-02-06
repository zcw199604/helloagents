# 多模型协作分析与审查规则

本模块定义多模型协作在 EVALUATE / ANALYZE / DESIGN / DEVELOP 阶段的统一行为，覆盖方案分析、原型获取与编码实施。

---

## 规则概述

```yaml
规则名称: 多模型协作分析与审查规则
适用范围:
  - EVALUATE: 简单任务免协作判定与确认
  - ANALYZE: 项目上下文与技术风险交叉验证
  - DESIGN: Phase2 多模型协作分析（含 Hard Stop）
  - DEVELOP: Phase3 原型获取 + Phase4 编码实施 + 完成后审查
核心目标:
  - 降低单模型偏差风险
  - 在关键决策前完成交叉验证与冲突仲裁
  - 保障编码实施前后都有可追溯审查链路
```

---

## 协作策略开关

```yaml
读取配置:
  - MULTI_MODEL_POLICY（BALANCED / STRICT）
  - SIMPLE_TASK_NO_COLLAB_CONFIRM（0 / 1）
  - PHASE2_HARD_STOP_CONFIRM（0 / 1）

BALANCED:
  - 按风险触发多模型协作
  - 简单任务默认可不协作

STRICT:
  - 默认强制 Codex + Gemini 协作
  - 简单任务可申请免协作，但必须先暂停并获得用户明确许可

PHASE2_HARD_STOP_CONFIRM = 1:
  - Phase2 结束后必须输出最终实施计划（含适度伪代码）
  - 必须询问: **Shall I proceed with this plan? (Y/N)**
  - 未收到明确 Y 前，禁止进入 Phase3 与新增文件读取
```

---

## Workflow 分阶段规则

### Phase 2: 多模型协作分析（DESIGN）

```yaml
目标:
  - 基于用户原始需求生成可执行实施计划
  - 输出跨模型交叉验证后的最终方案

分发输入:
  - 必须使用用户原始需求（不带预设观点）
  - 向 Codex / Gemini 分发时，仅提供:
    - 入口文件路径（entry file）
    - 行号索引（row index）
  - 禁止粘贴大段 snippet 作为主上下文

方案迭代:
  - 要求模型提供多角度解决方案
  - 执行交叉验证，整合优劣势并迭代优化
  - 必须形成无明显逻辑漏洞的 step-by-step 实施计划

Hard Stop（阻断闸门）:
  - 输出最终实施计划（含适度伪代码）
  - 必须以加粗文本输出: **Shall I proceed with this plan? (Y/N)**
  - 立即停止，等待用户明确回复
  - 用户回复 Y 前，禁止进入 Phase3
  - 用户回复 Y 前，禁止新增文件读取工具调用
```

### Phase 3: 原型获取（DEVELOP 前置）

```yaml
Route A - 前端/UI/样式（Gemini 优先）:
  - 适用: CSS / React / Vue / 视觉与交互原型
  - 上下文预算: < 32k
  - 注意: Gemini 对后端逻辑结论需二次审视

Route B - 后端/逻辑/算法（Codex 优先）:
  - 适用: 业务逻辑、算法实现、调试推演
  - 利用 Codex 的逻辑与调试能力

通用约束:
  - 任何调用都必须在 PROMPT 明确要求 Unified Diff Patch ONLY
  - 严禁外部模型进行任何真实修改
```

### Phase 4: 编码实施（DEVELOP）

```yaml
执行准则:
  1. 逻辑重构:
     - 将 Phase3 原型视为“脏原型”
     - 必须重写为高可读、高可维护、企业发布级代码

  2. 注释规范:
     - 关键位置必须添加中文注释（说明原因、约束与风险点）
     - 非关键位置避免冗余注释，保持代码可读性

  3. 最小作用域:
     - 变更仅限需求范围
     - 强制审查副作用，并做针对性修正
```

---

## 执行约束（CRITICAL）

```yaml
无写入原则:
  - 外部模型对本地文件系统拥有零写入权限
  - 必须在 PROMPT 追加:
    "OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications."

调用策略:
  - 长时任务使用后台执行（Run in the background）
  - 不设置硬 timeout

会话连续性:
  - 首次响应返回 SESSION_ID 后必须保存
  - 后续同一协作链路调用优先复用 --SESSION_ID
```

---

## 模型选择策略

```yaml
默认组合:
  主分析/主审查模型: codex
  交叉验证模型: gemini
  冲突仲裁模型: claude（双模型冲突时触发）

可选组合:
  - codex + gemini
  - codex + claude
  - gemini + claude
  - codex + gemini + claude（高风险任务推荐）
```

---

## DEVELOP 阶段风险分级（完成后审查）

```yaml
审查结论分级:
  P0 / Must Fix（阻断性）:
    - 安全漏洞、严重逻辑缺陷、关键链路可用性风险

  P1 / Should Fix（警告性）:
    - 明显但可控的质量问题或稳定性风险

  P2 / Note（信息性）:
    - 优化建议或潜在改进点

处理原则:
  - 出现 P0: 交互模式需用户确认“修复/风险接受/终止”
  - AUTO_FULL/AUTO_PLAN 出现 P0: 打破静默，等待用户决策
```

---

## 失败回退规则

```yaml
单模型失败:
  - 记录失败原因
  - 使用其余模型继续归并
  - 在结果中标注"部分协作失败"

全部模型失败:
  - 回退到本地单模型分析/审查
  - 输出警告并提示用户检查 CLI 可用性

输出不完整:
  - 保留 SESSION_ID 以支持后续补充追问
  - 将缺失项纳入待确认清单
```

---

## 输出要求

```yaml
输出必须包含:
  - 协作模式: 已启用/未启用
  - 执行摘要: 模型名、success、SESSION_ID
  - 共识结论: 各模型一致项
  - 冲突结论: 分歧点与仲裁结果（如有）
  - 最终建议: 可执行的下一步行动

Phase2 附加输出:
  - 实施计划（step-by-step）
  - 适度伪代码
  - Hard Stop 问句（加粗）

DEVELOP 阶段附加输出:
  - 审查分级结果: P0/P1/P2
  - Must Fix 清单（如有）
  - 风险接受记录（如用户确认跳过 P0）
```
