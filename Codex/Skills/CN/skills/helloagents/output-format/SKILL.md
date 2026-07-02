---
name: output-format
description: 阶段输出/异常/咨询/交互/命令完成的格式模板集合；任何阶段最终输出或异常/咨询/交互/命令完成时读取。完整模板按输出类型从 references 按需读取。
invocation: model
side_effects: read-only
requires: []
completion_criteria: 已选定唯一输出类型，读取对应模板，并生成包含【HelloAGENTS】、状态符号、变更清单和下一步的规范输出。
---

# 输出格式

**目标:** 统一 HelloAGENTS 用户可见输出。主文件只做路由与门禁；完整模板位于 `references/`。

---

## 输出类型选择

| 输出场景 | 状态符号 | 读取文件 |
|---|---|---|
| 阶段完成、代码/文档改动完成 | ✅ / ⚠️ | `references/unified-output.md` |
| 错误、取消、安全警告、部分失败 | ❌ / 🚫 / ⚠️ | `references/exception-output.md` |
| 技术咨询、概念解释、只读分析 | 💡 | `references/qa-output.md` |
| 需要用户选择或确认 | ❓ / ⚠️ | `references/interactive-output.md` |
| `~auto` / `~plan` / `~exec` / `~init` 命令完成 | ✅ | `references/command-output.md` |

---

## 全局输出门禁

- 所有阶段最终输出必须包含 `【HelloAGENTS】`。
- 文件清单必须使用纵向列表；无变更时写 `📁 变更: 无`。
- 写入操作完成后必须说明改动内容、文件位置和验证结果。
- 其他 skill 不复制完整模板，只引用本 skill 的输出类型和填充字段。

---

## 正反例

**应触发:**
- 开发实施完成，需要列出变更文件和验证结果。
- 命令执行失败，需要按异常模板说明原因。
- 咨询问答需要直接回答并保持简短。

**不应触发:**
- 中间进度更新；使用简短自然语言即可。
- 内部推理或工具调用摘要；不输出模板。

---

## 完成门禁

- 已选择且只选择一个输出模板。
- 输出状态符号与场景匹配。
- 变更清单、验证结果、下一步三项齐全。
- 未把模板原文泄露为无关长篇内容。
