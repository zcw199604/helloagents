# 子代理编排协议

## 1. 派发前检查

主代理派发前必须完成:

```yaml
检查清单:
  - 有完整方案包时读取 task.md/why.md/how.md；有轻量方案包时读取 task.md 元数据及相关约束；无方案包时从已授权请求或只读审查范围提取等价的目标、文件范围和验收标准
  - 已识别每个子任务的允许读取和写入范围；只读任务的 allowed_scope.write 为空
  - 已确认不同子代理的写入范围互斥
  - 已确认验证命令或验收标准
  - 已确认子任务不需要完整主会话上下文
  - 已确认用户未要求停止或等待确认
```

若任一检查失败，降级为主代理顺序执行。

协作不产生新的授权，也不要求补建方案包；无方案包的低/中风险任务和明确的只读审查均可按上述等价约束派发。

---

## 2. 子任务包格式

派发给每个子代理的任务必须包含:

```yaml
task_packet:
  id: 子任务编号
  goal: 单一明确目标
  context:
    - 必要需求摘要
    - 相关方案包片段（如有），否则使用已明确的请求范围与验收标准
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

## 3. 写入与冲突控制

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

## 4. 与多模型协作的关系

`multi_model` 偏审查，`hello-subagent` 偏任务编排。

```yaml
审查型子代理:
  - 默认只读
  - 可分析、审查、输出风险和 unified diff 建议
  - 不直接修改本地文件
  - 适用于 需求分析 / 方案设计 / 开发实施 的交叉验证

执行型子代理:
  - 仅在 开发实施 阶段使用
  - 必须有明确 allowed_scope.write
  - 完成后由主代理验收和集成
```

调用 `collaborating-with-claude`、`collaborating-with-codex`、`collaborating-with-gemini` 时，应保存 `SESSION_ID`；同一子任务的追问优先复用原会话。

---

## 5. 子代理返回要求

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

## 6. 主代理验收

主代理收到子代理结果后必须执行:

```yaml
验收步骤:
  - 检查状态是否 DONE/BLOCKED/FAILED
  - 检查 changed_files 是否越界
  - 检查多个子代理之间是否存在文件或接口冲突
  - 有 task.md 时更新任务完成状态；无方案包时对照派发目标和验收标准记录结果
  - 主代理核对实际变更与证据，按 verification-before-completion 判断是否需要补做验证
  - 汇总风险并决定是否继续、重派、顺序执行或询问用户
  - 仅由主代理按 kb 写入收益门禁同步必要知识；发布变化才更新 CHANGELOG，实际迁移方案包才更新 history 索引
```

子代理结果只能作为中间材料。最终结论以主代理核实的实际变更和有效证据为准，不能仅凭子代理的完成声明判断成功。

---

## 7. 失败回退

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
  - 有 task.md 时标记对应任务为 [X] 或 [?]；无方案包时在汇总中记录失败与影响
  - 判断是否影响后续任务
  - 按 develop Skill 的失败处理规则继续
```

禁止机械重复派发同一失败任务。

---

## 8. 输出约束

子代理输出不使用 HelloAGENTS 阶段完成模板。

用户可见输出由主代理统一生成，并必须继续遵循 output-format Skill 的 G6.1/G6.2/G6.3 格式规则。

---

## 9. 路径映射

本规则不得引入 `.helloagents/`、`requirements.md`、`plan.md`、`tasks.md` 等新体系。

实际存在方案包或知识库时使用以下路径；无方案包任务使用当前请求和派发摘要，不创建虚拟文件:

```yaml
需求依据: helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/why.md
实施方案: helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/how.md
任务清单: helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/task.md
执行归档: helloagents/<branch-name>/history/YYYY-MM/YYYYMMDDHHMM_<feature>/
知识库: helloagents/<branch-name>/CHANGELOG.md, helloagents/<branch-name>/project.md, helloagents/<branch-name>/wiki/*
```

---

## 10. 优先级

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

---
