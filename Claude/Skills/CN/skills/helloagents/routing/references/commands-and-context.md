# 命令路径与上下文响应

## 命令路径

<command_paths>

**全授权命令**: ~auto|~helloauto|~fa → 确认授权 → 需求分析→方案设计→开发实施 静默执行
**知识库命令**: ~init|~wiki → 确认授权 → 知识库初始化
**规划命令**: ~plan|~design → 选择全自动规划或交互式规划 → 需求分析→方案设计（交互式规划在方案构思处等待选择）
**执行命令**: ~exec|~run|~execute → 检查 helloagents/<branch-name>/plan/ 存在方案包 → 确认授权 → 开发实施
**测试命令**: ~test [scope] → 确认授权 → 解析测试范围 → 创建或复用轻量测试方案包 → 开发实施与 QA

### 通用确认响应机制

**适用范围:** 所有特殊命令的用户授权确认环节

输出询问前设置 `PENDING_INTERACTION=COMMAND_CONFIRM`，并记录待确认命令与当前 `WORKFLOW_ID`。确认只对同一工作流、同一待确认命令生效。

**授权询问格式:**
```
❓【HelloAGENTS】- 命令确认

即将执行 [命令名称]:
- 执行内容: [命令动作简述]
- 影响范围: [预估影响]

────
🔄 下一步: 确认执行? (是/取消)
```

**用户响应处理:**
```yaml
确认意图: 按命令类型设置状态变量后，执行命令定义的[确认后动作]
  全授权命令(~auto|~helloauto|~fa):
    - 先执行 RESET_WORKFLOW_STATE，生成新的 WORKFLOW_ID
    - 设置 MODE_FULL_AUTH=true
    - 设置 AUTH_WORKFLOW_ID=WORKFLOW_ID
    - 清除 MODE_EXECUTION/MODE_PLANNING/MODE_PLANNING_INTERACTIVE
    - 进入 需求分析→方案设计→开发实施 静默执行
  知识库命令(~init|~wiki):
    - 先执行 RESET_WORKFLOW_STATE，生成新的 WORKFLOW_ID
    - 清除 MODE_FULL_AUTH/MODE_EXECUTION/MODE_PLANNING/MODE_PLANNING_INTERACTIVE
    - 执行知识库初始化或重建
  执行命令(~exec|~run|~execute):
    - 先执行 RESET_WORKFLOW_STATE，生成新的 WORKFLOW_ID
    - 检查 `helloagents/<branch-name>/plan/` 存在合法完整或轻量方案包
    - 设置 MODE_EXECUTION=true
    - 设置 AUTH_WORKFLOW_ID=WORKFLOW_ID
    - 清除 MODE_FULL_AUTH/MODE_PLANNING/MODE_PLANNING_INTERACTIVE
    - 进入开发实施
  测试命令(~test):
    - 先执行 RESET_WORKFLOW_STATE，生成新的 WORKFLOW_ID
    - 解析显式 `scope`，或从当前方案包/最近改动确定范围；无法确定时设置 `PENDING_INTERACTION=REQUIREMENT_INPUT` 并追问
    - 创建或复用覆盖该范围的轻量方案包，在验证策略中记录 TDD 分类和测试目标
    - 设置 MODE_EXECUTION=true 与 AUTH_WORKFLOW_ID=WORKFLOW_ID
    - 清除 MODE_FULL_AUTH/MODE_PLANNING/MODE_PLANNING_INTERACTIVE
    - 读取 `test` Skill 后进入开发实施；默认只修改测试与证据，生产修复需另行明确授权
拒绝意图:
  - 执行 RESET_WORKFLOW_STATE
  - 输出"🚫 已取消[命令名称]命令。"
  - 如原始输入包含具体需求，询问是否按标准模式继续
其他输入: 再次询问确认
```

### 规划命令确认机制

**适用范围:** `~plan` / `~design` 规划命令。此格式覆盖通用授权询问格式。

```
❓【HelloAGENTS】- 命令确认

即将执行 规划命令:
- 执行内容: 需求分析 → 方案设计 → 创建方案包
- 影响范围: 只写入方案包和必要知识库文件，不修改业务代码

[1] 全自动规划（推荐） - 自动选择推荐方案并创建方案包
[2] 交互式规划 - 创建方案包前输出方案对比并等待选择
[3] 取消 - 取消规划命令

────
🔄 下一步: 请输入序号选择
```

**用户响应处理:**
```yaml
[1] 全自动规划:
  - 先执行 RESET_WORKFLOW_STATE，生成新的 WORKFLOW_ID
  - 设置 MODE_PLANNING=true
  - 设置 MODE_PLANNING_INTERACTIVE=false
  - 需求分析→方案设计 全程静默
[2] 交互式规划:
  - 先执行 RESET_WORKFLOW_STATE，生成新的 WORKFLOW_ID
  - 设置 MODE_PLANNING=true
  - 设置 MODE_PLANNING_INTERACTIVE=true
  - 需求分析静默执行，方案构思输出方案对比并等待用户选择
[3]/取消:
  - 执行 RESET_WORKFLOW_STATE
  - 输出取消格式
其他输入: 再次询问确认
```

### 命令速查表

| 命令 | 触发词 | 动作 |
|------|--------|------|
| 全授权 | `~auto` / `~helloauto` / `~fa` | 需求分析→方案设计→开发实施 静默执行 |
| 知识库 | `~init` / `~wiki` | 知识库初始化/重建 |
| 规划 | `~plan` / `~design` | 可选择全自动规划或交互式规划，执行到方案设计并创建方案包 |
| 执行 | `~exec` / `~run` / `~execute` | 开发实施 执行已有方案包 |
| 测试 | `~test [scope]` | 创建或复用轻量测试方案包，补测试并记录 TDD/豁免证据 |

</command_paths>

---

## 上下文路径

<context_paths>

**上下文状态判定:**
- 不从上一条文本猜测状态；以 `PENDING_INTERACTION` 为唯一判定依据。
- `REQUIREMENT_INPUT`: 需求评分不足追问。
- `SOLUTION_CHOICE`: 方案构思选择。
- `SOLUTION_REDESIGN`: 所有方案被拒绝后的重新构思/取消选择。
- `DESIGN_CONFIRM`: 需求分析后是否进入方案设计。
- `DEVELOPMENT_CONFIRM`: 方案设计后是否进入开发实施。
- `PACKAGE_CHOICE`: 多方案包选择。
- `MM_REVIEW`: 方案多模型审查选择。
- `QUALITY_DECISION`: 代码质量建议选择。
- `MM_ACCEPTANCE`: 归档前多模型验收选择。
- `TEST_FAILURE_DECISION`: 阻断性测试失败选择。
- `QA_RISK_DECISION`: P1 质量风险接受或返回修复选择。
- `PARTIAL_FAILURE_DECISION`: 非阻断任务部分失败后的继续或终止选择。
- `COMMAND_CONFIRM` / `EHRB_CONFIRM`: 命令或高风险确认。
- `CONTEXT_CHOICE`: 当前任务与新任务边界不清时的选择。

**追问响应**: `PENDING_INTERACTION=REQUIREMENT_INPUT` + 用户补充 → 清除等待态 → 重新评分
  - 用户补充边界/范围/成功标准只用于补足需求信息，不构成进入方案设计或开发实施的确认
  - 交互确认模式: 评分≥7分后必须输出需求分析总结并等待是否进入方案设计的确认
  - MODE_PLANNING=true: 可静默进入方案设计，但方案包生成后必须停止，不进入开发实施
  - MODE_FULL_AUTH=true: 可在方案设计完成并创建方案包后继续进入开发实施
**选择响应**: 根据 `SOLUTION_CHOICE` / `SOLUTION_REDESIGN` / `PACKAGE_CHOICE` / `CONTEXT_CHOICE` / `MM_REVIEW` / `QUALITY_DECISION` 消费序号；状态不匹配时不得套用
  - 方案构思选择: 仅进入详细规划并创建方案包，之后按方案设计阶段转换规则等待确认或停止
  - 开发实施多方案包选择: 仅在已满足开发实施入口硬门禁时有效
  - `TEST_FAILURE_DECISION` 消费序号: `[1]` 清除等待态后修复并重跑测试；`[2]` 执行 `RESET_WORKFLOW_STATE` 并终止。P0 不接受跳过。
  - `MM_ACCEPTANCE` 消费序号: `[1]` 清除等待态并启动只读多模型验收；`[2]` 清除等待态并执行主代理本地最终复核；`[3]` 重置状态并终止。
  - `QA_RISK_DECISION` 消费序号: `[1]` 清除等待态并返回修复；`[2]` 仅对 P1 记录明确风险接受并重算 gate；`[3]` 重置状态并终止。P0 不得进入此状态。
  - `PARTIAL_FAILURE_DECISION` 消费序号: `[1]` 清除等待态、记录非阻断失败后继续；`[2]` 重置状态并终止。
**确认响应**: 仅 `DESIGN_CONFIRM` / `DEVELOPMENT_CONFIRM` / `COMMAND_CONFIRM` / `EHRB_CONFIRM` 可消费确认；消费后立即清除等待态
  - 确认需求分析完成: 进入方案设计，不进入开发实施
  - 确认方案设计完成且明确同意开发: 才能进入开发实施
  - 其他确认不得越过方案设计或开发实施入口硬门禁
**反馈响应**: 上下文≠无 + 用户修改意见 → 按 Feedback-Delta 规则判定:
  - 重大变更: 输出"⚠️【HelloAGENTS】- 需求变更"提示后重回需求分析
  - 局部增量: 静默在当前阶段应用修改，完成后输出更新的阶段完成格式
**新需求响应**: 用户明确提出新需求 → 执行 `RESET_WORKFLOW_STATE`，生成新 `WORKFLOW_ID` 后重新路由

**上下文打断规则:**
- 特殊命令可打断上下文，但必须先终止旧等待态并重置旧授权
- 明确新需求（"另外"/"还有"/无关技术需求）→ 新需求响应
- 模糊边界 → 设置 `PENDING_INTERACTION=CONTEXT_CHOICE` 后输出上下文确认格式:
  ```
  ❓【HelloAGENTS】- 上下文确认

  检测到新输入，当前任务尚未完成。
  [1] 继续当前任务 - [当前任务简述]
  [2] 开始新任务 - [新任务简述]

  ────
  🔄 下一步: 请输入序号选择
  ```

</context_paths>
