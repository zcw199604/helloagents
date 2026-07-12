# 特殊命令完成输出格式

## 特殊命令完成输出格式

**说明:** 所有命令完成输出严格遵循 G6.1 统一输出格式，以下定义各命令的阶段内容填充规则。

**全授权命令完成:**
```
✅【HelloAGENTS】- 全授权命令完成

- ✅ 执行路径: 需求分析 → 方案设计 → 开发实施
- 📊 执行结果: 需求评分X/10, 任务Y/Z完成
- 💡 关键决策: [决策摘要，如有]

────
📁 变更:
  - {代码文件}
  - {知识库文件}
  - {方案包文件}
  - helloagents/<branch-name>/CHANGELOG.md
  - helloagents/<branch-name>/history/...
  ...

🔄 下一步: 全授权命令已结束，随时准备接收新指令
📦 遗留方案: [按 lifecycle Skill 扫描显示]
```

**规划命令完成:**
```
✅【HelloAGENTS】- 规划命令完成

- ✅ 执行路径: 需求分析 → 方案设计
- 📋 需求分析: 评分X/10, [关键目标]
- 📝 方案规划: [方案类型], 任务数X

────
📁 变更:
  - helloagents/<branch-name>/plan/{方案包目录}/why.md
  - helloagents/<branch-name>/plan/{方案包目录}/how.md
  - helloagents/<branch-name>/plan/{方案包目录}/task.md
  - {规划期间实际创建或更新的知识库文件，如有}

🔄 下一步: 方案包已生成，如需执行请输入 ~exec
📦 遗留方案: [按 lifecycle Skill 扫描显示，如有]
```

**执行命令完成:**
```
✅【HelloAGENTS】- 执行命令完成

- ✅ 执行方案: [方案包名称]
- 📊 执行结果: 任务Y/Z完成
- 🔍 质量验证: [测试结果摘要]

────
📁 变更:
  - {代码文件}
  - {知识库文件}
  - helloagents/<branch-name>/CHANGELOG.md
  - helloagents/<branch-name>/history/...
  ...

🔄 下一步: 执行命令已结束，随时准备接收新指令
📦 遗留方案: [按 lifecycle Skill 扫描显示]
```

**测试命令完成:**
```
✅【HelloAGENTS】- 测试命令完成

- ✅ 测试范围: [模块/文件/行为]
- 🧪 TDD 决策: [tdd / TDD-EXEMPT]，证据已记录到 `qa-review.json`
- 🔍 验证结果: [测试命令与结果摘要]

────
📁 变更:
  - {测试文件}
  - {方案包与 QA 证据文件}
  - {知识库文件，如有}

🔄 下一步: [缺陷需修复时进入常规方案设计；否则测试交付已完成]
```

**知识库命令完成:** 格式见 kb Skill

