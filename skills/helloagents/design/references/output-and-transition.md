# 方案设计输出与阶段转换

## 方案设计 输出格式

⚠️ **CRITICAL - 强制要求:**
- ALWAYS使用 output-format Skill 的 G6.1 统一输出格式
- NEVER使用自由文本替代规范格式
- 输出前MUST验证格式完整性

严格调用 output-format Skill 的 G6.1 统一输出格式，填充以下数据：

1. **阶段名称:** `方案设计`
2. **阶段具体内容(≤5条要点):**
   - 📚 知识库状态
   - 📝 方案概要（复杂度、方案说明）
   - 📋 变更清单
   - 📊 任务清单概要
   - ⚠️ 风险评估（如检测到EHRB）
3. **文件变更清单:**
   - `helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/why.md`
   - `helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/how.md`
   - `helloagents/<branch-name>/plan/YYYYMMDDHHMM_<feature>/task.md`
4. **下一步建议:**
   - 交互确认模式: 输出多模型审查询问（见"多模型审查询问格式"）
   - 规划命令: 输出规划命令完成总结后停止；不输出多模型审查询问
   - 全授权命令: 直接进入开发实施，总结末尾追加多模型审查提示
5. **遗留方案提醒:**
   - 按 lifecycle Skill 的 G11 扫描 `helloagents/<branch-name>/plan/` 目录
   - 如检测到遗留方案包（排除本次创建的方案包），按 lifecycle Skill 的 G11 规则显示

### 多模型审查询问格式

输出前设置 `PENDING_INTERACTION=MM_REVIEW`。

```
❓【HelloAGENTS】- 多模型审查

方案包已生成: `[方案包路径]`
可调用 claude + gemini 对方案进行交叉评审，检验技术方案的合理性与潜在风险。

[1] 启动多模型审查 - 读取 `multi_model` Skill，按方案设计阶段规则执行
[2] 跳过 - 直接进行下一步

────
🔄 下一步: 请输入序号选择
```

---

## 阶段转换规则

```yaml
交互确认模式:
  - 在同一个阶段总结主模板的交互选项插槽中嵌入"多模型审查询问格式"，设置 `PENDING_INTERACTION=MM_REVIEW` 后等待用户选择
  - 用户选择 [1] 启动多模型审查:
      - 读取 `multi_model` Skill，按方案设计阶段协作规则执行
      - 输出审查结论（共识项、分歧项、最终建议）
      - 审查完成后进入后续阶段转换逻辑
  - 用户选择 [2] 跳过:
      - 进入后续阶段转换逻辑
  - 后续阶段转换逻辑:
      - 交互确认模式: 设置 `PENDING_INTERACTION=DEVELOPMENT_CONFIRM`，询问"是否进入开发实施?(是/否)"
        - 明确确认 → 进入开发实施
        - 明确拒绝 → 执行 RESET_WORKFLOW_STATE，流程终止
        - Feedback-Delta → 按Feedback-Delta规则处理
        - 其他输入 → 视为新的用户需求，按路由机制重新判定

规划命令:
  - 保存总结字段 → 执行 RESET_WORKFLOW_STATE → 输出整体总结并停止
  - 不输出多模型审查询问；总结末尾追加: "💡 多模型审查: 如需审查方案包，可在规划命令完成后单独触发"

自适应授权模式:
  - 用户原请求已明确授权低/中风险改动，且设计仅用于内部任务拆解或可恢复记录时，不设置 `DEVELOPMENT_CONFIRM`
  - 完成必要方案记录后连续进入开发实施；一旦风险升级为高或命中 EHRB，退出本模式并等待确认

推进模式:
  - 全授权命令: 完成方案设计 → 跳过多模型审查询问 → 立即静默进入开发实施
                最终总结可提示后续独立审查，但不得引用“规划命令完成后”

关键约束（以下任一情况可以进入开发实施）：
  1. 当前会话已创建完整方案包，且用户明确确认进入开发实施（含多模型审查后确认）
  2. 全授权命令(~auto等)触发且已完成方案设计
  3. 执行命令(~exec等)触发且 `helloagents/<branch-name>/plan/` 中存在方案包
  4. 用户原请求已明确授权低/中风险改动，EHRB=无，且无破坏性公共契约或真实数据迁移
```
