# 多模型协作分析与审查规则

本模块定义在需求评估、项目分析与开发实施阶段的多模型协作流程，基于 `codex_bridge.py`、`gemini_bridge.py`、`claude_bridge.py` 进行交叉验证、冲突仲裁与代码审查。

---

## 规则概述

```yaml
规则名称: 多模型协作分析与审查规则
适用范围:
  - EVALUATE: 简单任务免协作判定与确认
  - ANALYZE: 需求与技术方案交叉验证
  - DEVELOP: 代码完成后的多模型审查
核心目标:
  - 降低单模型偏差风险
  - 对关键结论执行交叉验证
  - 在冲突时提供可追溯仲裁依据
  - 在代码完成后执行风险分级审查
```

---

## 协作策略开关

```yaml
读取配置:
  - MULTI_MODEL_POLICY（BALANCED / STRICT）
  - SIMPLE_TASK_NO_COLLAB_CONFIRM（0 / 1）

BALANCED:
  - 按风险触发多模型协作
  - 简单任务默认可不协作

STRICT:
  - 默认强制 Codex + Gemini 协作
  - 简单任务可申请免协作，但必须先暂停并获得用户明确许可

简单任务免协作确认（STRICT）:
  触发条件: 判定为简单任务且拟跳过协作
  处理规则:
    - 立即暂停当前流程
    - 明确报告不协作原因
    - 等待用户确认后方可继续下一步
```

---

## 触发条件

```yaml
ANALYZE 阶段触发（满足任一）:
  - 用户明确要求: "多模型协作"、"交叉验证"、"复核结论"
  - 任务复杂度较高: 标准开发模式、跨模块影响、关键架构调整
  - 单模型结论不稳定: 关键判断存在冲突信号或置信度不足

DEVELOP 阶段触发（代码完成后，满足任一）:
  - 用户明确要求"完成后多模型审查"
  - 跨模块改动、核心链路改动、安全相关改动
  - 涉及鉴权、支付、权限、数据一致性等高风险逻辑

STRICT 模式额外规则:
  - 除简单任务且用户已同意免协作外，默认均触发多模型协作
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
  - 后续同一协作链路调用应优先复用 --SESSION_ID
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

## 执行流程

<multi_model_flow>
多模型协作推理过程:
1. 抽取统一目标和约束，构建共享 PROMPT
2. 对选定模型发起并行或串行请求
3. 收集结构化输出（结论、风险、建议、SESSION_ID）
4. 比对共识项与冲突项
5. 必要时触发第三模型仲裁
6. 归并为单一可执行结论
</multi_model_flow>

```yaml
步骤1 - 构建统一输入:
  ANALYZE 必含要素:
    - 任务目标
    - 影响范围
    - 已知约束
    - 期望输出格式（建议 JSON）

  DEVELOP（完成后审查）必含要素:
    - 代码变更摘要（文件/模块/关键函数）
    - 测试结果摘要（通过/失败/覆盖范围）
    - 风险关注点（安全、兼容性、性能、并发）
    - 审查输出格式（Must Fix / Should Fix / Note）

步骤2 - 调用桥接脚本:
  Codex: python -X utf8 "scripts/codex_bridge.py" --cd "<项目路径>" --PROMPT "<统一提示词+只读约束>"
  Gemini: python -X utf8 "scripts/gemini_bridge.py" --cd "<项目路径>" --PROMPT "<统一提示词+只读约束>"
  Claude: python -X utf8 "scripts/claude_bridge.py" --cd "<项目路径>" --PROMPT "<统一提示词+只读约束>"

步骤3 - 结果归并:
  对齐维度:
    - 事实判断（代码定位、依赖关系、接口定义）
    - 风险判断（安全/性能/兼容性）
    - 实施建议（改动路径、测试策略）

步骤4 - 冲突处理:
  无冲突:
    - 直接输出共识结论
  有冲突:
    - 标记冲突点
    - 触发 claude 仲裁（若未执行）
    - 输出仲裁结论与取舍理由
```

---

## DEVELOP 阶段风险分级（代码完成后）

```yaml
审查结论分级:
  P0 / Must Fix（阻断性）:
    - 安全漏洞、严重逻辑缺陷、关键链路可用性风险
    - 默认必须修复，未修复不得进入归档步骤

  P1 / Should Fix（警告性）:
    - 明显但可控的质量问题或稳定性风险
    - 可继续执行，但需在总结中记录

  P2 / Note（信息性）:
    - 优化建议或潜在改进点
    - 记录供后续迭代

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

## 模式适配

```yaml
INTERACTIVE:
  - BALANCED: 按触发条件决定是否启用
  - STRICT: 默认启用；简单任务免协作必须先确认
  - DEVELOP 阶段出现 P0 必须等待用户决策

AUTO_FULL / AUTO_PLAN:
  - BALANCED: 满足触发条件时自动执行默认组合（codex + gemini）
  - STRICT: 默认自动执行默认组合（codex + gemini）
  - 发现冲突时自动追加 claude 仲裁
  - DEVELOP 阶段出现 P0 打破静默
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

DEVELOP 阶段附加输出:
  - 审查分级结果: P0/P1/P2
  - Must Fix 清单（如有）
  - 风险接受记录（如用户确认跳过 P0）
```
