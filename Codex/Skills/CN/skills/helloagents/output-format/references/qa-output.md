# 咨询问答输出格式

## G6.3 | 咨询问答输出格式

<qa_output_format>

**适用范围:** 所有直接回答场景（技术咨询、问候、确认等非开发流程交互）

**核心约束:**
- MUST使用 `💡【HelloAGENTS】- 咨询问答` 格式
- 长度约束: 简单≤2句 | 典型≤5要点 | 复杂=概述+≤5要点

**输出结构:**
```
💡【HelloAGENTS】- 咨询问答

[回答内容 - 遵循长度约束]
```

**示例:**
```
💡【HelloAGENTS】- 咨询问答

客户端错误在 src/services/process.ts:712 的 connectToServer 函数中处理。连接失败后会重试3次，全部失败则标记为 failed 状态。
```

</qa_output_format>

---

