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

## 开发实施 输出格式

⚠️ **CRITICAL - 强制要求:**
- ALWAYS使用 output-format Skill 的 G6.1 统一输出格式
- NEVER使用自由文本替代规范格式
- 输出前MUST验证格式完整性

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
   - 📦 迁移信息: 已迁移至 `helloagents/<branch-name>/history/YYYY-MM/YYYYMMDDHHMM_<feature>/`
3. **文件变更清单:**
   ```
   📁 变更:
     - {代码文件}
     - {知识库文件}
     - helloagents/<branch-name>/history/YYYY-MM/YYYYMMDDHHMM_<feature>/qa-review.json
     - helloagents/<branch-name>/CHANGELOG.md
     - helloagents/<branch-name>/history/index.md
     ...
   ```
4. **下一步建议:**
   - 交互确认模式/执行命令: 输出多模型验收询问（见步骤13"询问格式"）
   - 全授权命令: 总结末尾追加多模型验收提示
5. **遗留方案提醒:** 按 lifecycle Skill 的 G11 扫描 `helloagents/<branch-name>/plan/` 目录，如有遗留方案包则显示

---

