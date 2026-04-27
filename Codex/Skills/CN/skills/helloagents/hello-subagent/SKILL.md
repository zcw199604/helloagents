---
name: hello-subagent
description: 定义 HelloAGENTS 并行子代理编排规则。用于开发实施或多模型协作中，任务可拆分为多个独立、边界清晰、可验证的子任务时，指导主代理进行子代理派发、上下文裁剪、文件边界控制、结果汇总、失败回退和最终验收。
---

# 并行子代理编排规则

本 Skill 只增强 HelloAGENTS 现有流程，不新增阶段、命令或用户可见输出格式。

---

## 1. 角色边界

```yaml
主代理职责:
  - 控制 需求分析 → 方案设计 → 开发实施 阶段流程
  - 执行 EHRB 风险识别与用户确认
  - 维护方案包 task.md/why.md/how.md 与 history 生命周期
  - 拆分子任务、分配文件边界、跟踪子代理状态
  - 汇总子代理结果并完成最终集成
  - 运行验证、同步知识库、更新 CHANGELOG.md
  - 生成唯一的 HelloAGENTS 用户可见最终输出

子代理职责:
  - 只处理被派发的单一局部任务
  - 只读取必要上下文
  - 只修改明确授权的文件范围
  - 返回结构化结果、验证信息和风险说明
```

子代理不得自行推进 HelloAGENTS 阶段，不得迁移方案包，不得更新最终知识库状态，不得直接面向用户输出阶段完成总结。

---

## 2. 触发条件

仅当同时满足以下条件时启用子代理:

```yaml
必需条件:
  - 子任务数量 >= 2
  - 子任务之间无顺序依赖
  - 每个子任务可独立理解、独立验证
  - 文件写入范围不重叠
  - 共享接口、数据结构、状态边界清晰
  - 需求分析或方案设计已给出足够约束
  - 未确认的 EHRB 风险不存在
```

推荐场景:
- 多个独立模块并行实现
- 多个独立测试文件或故障域并行排查
- 前端、后端、测试、文档等边界明确的任务分片
- `task.md` 中存在多个互不依赖的任务组
- 多模型审查需要并行检查不同风险域

禁止场景:
- 微调模式或单文件小改动
- 需求仍模糊或架构决策未完成
- 多个子任务需要频繁修改同一文件
- 多个失败疑似同一根因
- 子任务存在明显前后置依赖
- 生产、权限、支付、破坏性操作等 EHRB 风险尚未确认

---

## 3. 派发前检查

主代理派发前必须完成:

```yaml
检查清单:
  - 已读取当前 task.md/why.md/how.md 中与子任务相关的约束
  - 已识别每个子任务的允许写入文件或目录
  - 已确认不同子代理的写入范围互斥
  - 已确认验证命令或验收标准
  - 已确认子任务不需要完整主会话上下文
  - 已确认用户未要求停止或等待确认
```

若任一检查失败，降级为主代理顺序执行。

---

## 4. 子任务包格式

派发给每个子代理的任务必须包含:

```yaml
task_packet:
  id: 子任务编号
  goal: 单一明确目标
  context:
    - 必要需求摘要
    - 相关方案包片段
    - 相关文件路径
  allowed_scope:
    read:
      - 允许读取的文件/目录
    write:
      - 允许修改的文件/目录
  forbidden_scope:
    - 禁止修改的文件/目录
    - 禁止变更的接口/行为
  verification:
    - 验证命令或人工验收标准
  output_contract:
    - status: DONE | BLOCKED | FAILED
    - summary: 完成内容摘要
    - changed_files: 修改文件清单
    - verification: 验证结果
    - risks: 风险或遗留问题
```

上下文必须最小化。不要把完整主会话、无关方案、无关历史讨论发送给子代理。

---

## 5. 写入与冲突控制

```yaml
并行写入规则:
  - 每个文件同一时间只能归属一个子代理
  - 同一核心接口、共享状态、公共类型、迁移脚本视为冲突域
  - 冲突域内任务必须顺序执行
  - 子代理不得修改 allowed_scope.write 之外的文件
  - 子代理不得回滚用户或其他子代理的改动
```

如果执行过程中发现文件边界重叠，立即停止继续并行派发，由主代理重新拆分或改为顺序执行。

---

## 6. 与多模型协作的关系

`multi_model` 偏审查，`hello-subagent` 偏任务编排。

```yaml
审查型子代理:
  - 默认只读
  - 可分析、审查、输出风险和 unified diff 建议
  - 不直接修改本地文件
  - 适用于 ANALYZE / DESIGN / DEVELOP 的交叉验证

执行型子代理:
  - 仅在 DEVELOP 阶段使用
  - 必须有明确 allowed_scope.write
  - 完成后由主代理验收和集成
```

调用 `collaborating-with-claude`、`collaborating-with-codex`、`collaborating-with-gemini` 时，应保存 `SESSION_ID`；同一子任务的追问优先复用原会话。

---

## 7. 子代理返回要求

子代理必须返回结构化摘要:

```yaml
status: DONE | BLOCKED | FAILED
summary:
  - 完成了什么
changed_files:
  - path
verification:
  - command: 执行的验证命令
    result: passed | failed | not_run
    note: 说明
risks:
  - 风险或遗留问题；无则写 none
next:
  - 建议主代理下一步；无则写 none
```

`BLOCKED` 必须说明阻塞原因，例如上下文不足、依赖未完成、文件冲突、环境不可用、需求不明确。

---

## 8. 主代理验收

主代理收到子代理结果后必须执行:

```yaml
验收步骤:
  - 检查状态是否 DONE/BLOCKED/FAILED
  - 检查 changed_files 是否越界
  - 检查多个子代理之间是否存在文件或接口冲突
  - 对照 task.md 更新任务完成状态
  - 运行必要验证命令或替代验证
  - 汇总风险并决定是否继续、重派、顺序执行或询问用户
  - 最终由主代理统一同步知识库、CHANGELOG.md、history/index.md
```

子代理结果只能作为中间材料。最终结论以主代理本地验证结果为准。

---

## 9. 失败回退

```yaml
BLOCKED 处理顺序:
  1. 判断是否上下文不足
  2. 判断是否任务拆分不合理
  3. 判断是否存在隐藏依赖或文件冲突
  4. 判断是否验证环境不可用
  5. 可补充上下文后重派一次
  6. 仍失败则降级为主代理顺序执行或询问用户

FAILED 处理:
  - 记录失败原因
  - 标记对应 task.md 任务为 [X] 或 [?]
  - 判断是否影响后续任务
  - 按 develop Skill 的失败处理规则继续
```

禁止机械重复派发同一失败任务。

---

## 10. 输出约束

子代理输出不使用 HelloAGENTS 阶段完成模板。

用户可见输出由主代理统一生成，并必须继续遵循 `AGENTS.md` 的 G6.1/G6.2/G6.3 格式规则。

---

## 11. 路径映射

本规则不得引入 `.helloagents/`、`requirements.md`、`plan.md`、`tasks.md` 等新体系。

统一使用当前 HelloAGENTS 路径:

```yaml
需求依据: plan/YYYYMMDDHHMM_<feature>/why.md
实施方案: plan/YYYYMMDDHHMM_<feature>/how.md
任务清单: plan/YYYYMMDDHHMM_<feature>/task.md
执行归档: history/YYYY-MM/YYYYMMDDHHMM_<feature>/
知识库: CHANGELOG.md, project.md, wiki/*
```

---

## 12. 优先级

```yaml
规则优先级:
  1. HelloAGENTS 主流程与路由规则
  2. EHRB 安全与用户确认
  3. 方案包生命周期
  4. 知识库同步规则
  5. TDD 与质量验证规则
  6. multi_model 审查规则
  7. hello-subagent 并行编排规则
```
