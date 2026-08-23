# 开发实施代码规范与输出

## 代码规范要求

<code_standards>
**适用范围:** 开发实施阶段的所有代码改动

**规范要求:**
- **文件顶部注释:** 导入语句前，项目现有注释风格，1-3句话说明模块用途
- **所有代码注释:** 必须用{OUTPUT_LANGUAGE}生成
- **代码风格:** 遵循项目现有命名约定和格式规范
</code_standards>

---

## 开发实施输出

- 自适应低/中风险改动完成后，直接说明结果、关键文件、实际验证和剩余风险，不强制使用阶段标题或固定栏目。
- 正式命令、复杂方案包或需要交互时，使用 output-format 对应模板。
- 不重复输出内部阶段、需求评分、无变化的知识库状态或“不适用”占位项。

### 等待用户选择方案包时（步骤1多方案包）

```
❓【HelloAGENTS】- 开发实施

检测到多个方案包，请选择执行目标:

[1] YYYYMMDDHHMM_<feature1> - [概要描述]
[2] YYYYMMDDHHMM_<feature2> - [概要描述]
[3] YYYYMMDDHHMM_<feature3> - [概要描述]

────
🔄 下一步: 请输入方案包序号(1/2/3)
```

### 阶段完成时

严格调用 output-format Skill 的 G6.1 统一输出格式，填充以下数据：

1. **阶段名称:** `开发实施`
2. **阶段具体内容(≤5条要点):**
   - 📚 知识库状态
   - ✅ 执行结果: 任务数量和状态统计
   - 🔍 质量验证: 一致性审计、测试结果、QA证据
   - 💡 代码质量优化建议（如有）
   - 📦 迁移信息: 有方案包时报告归档路径；自适应无方案包时写“不适用”
3. **文件变更清单:**
   ```
   📁 变更:
     - {代码文件}
     - {知识库文件}
     - {如存在: helloagents/<branch-name>/history/YYYY-MM/YYYYMMDDHHMM_<feature>/qa-review.json}
     - {如实际更新: helloagents/<branch-name>/CHANGELOG.md}
     - {如实际迁移: helloagents/<branch-name>/history/index.md}
     ...
   ```
4. **下一步建议:**
   - 归档前多模型验收已在步骤11.5处理；完成总结只报告结果和剩余风险
5. **遗留方案提醒:** 按 lifecycle Skill 的 G11 扫描 `helloagents/<branch-name>/plan/` 目录，如有遗留方案包则显示

---
