# 变更提案: Skill 规则矛盾与遗留悬空清理

## 需求背景

对 `Claude/Skills/CN` 与 `Codex/Skills/CN` 的全量审查发现 9 处问题：6 处规则矛盾（会导致执行歧义）与 3 处重构遗留悬空（污染语义、影响可移植性）。这些问题多为历次瘦身重构（slim skills、remove EN set）后未同步清理的残留。

## 变更内容

1. 统一步骤13多模型验收的输出契约为 "OUTPUT: Risk report only."（与 `multi_model` 审查类契约一致）
2. 统一"规划命令不输出多模型审查询问"的口径（以 `output-and-transition.md` 为准修正 `detailed-planning.md`）
3. 清理 P1/P2/P3 阶段代号，统一替换为"需求分析/方案设计/开发实施"（不涉及 P0/P1/P2 风险分级）
4. 统一 CURRENT_PACKAGE 清理时机为"方案包迁移至 history/ 后"，修正错误的 G11 条款引用为 G12
5. 为轻量迭代"简化方案包"（仅 task.md）在方案包完整性定义与开发实施步骤1扫描中补充例外识别规则
6. 轻量迭代动作流程补充 CHANGELOG.md 更新步骤，使流程与输出模板一致
7. 清理 `multi_model` 遗留：R1/R2 术语映射为微调/轻量迭代、补充配置项默认值与来源说明、TASK_COMPLEXITY 改为引用 design 复杂度判定、Phase2/3/4 与 ANALYZE/DESIGN/DEVELOP 映射为中文阶段名、英文 Y/N 询问改为中文
8. `delegation-protocol.md` 章节从 3-12 重排为 1-10
9. 模板与 qa-review 示例中写死的本仓库脚本命令改为占位符+本仓库示例，保持 `audit_skills.py` 语义契约字符串不变

## 范围边界

- **范围内:** 上述 9 项，Claude 与 Codex 两树镜像同步，`CLAUDE.md`/`AGENTS.md` 中 G2 方案包定义补轻量迭代例外说明
- **范围外:** 第三部分打磨项（multi_model 命名下划线、collaborating-* 英文正文与去重、阻断性输出块位置、审计脚本加固）、用户全局 CLAUDE.md 的部署同步
- **拆分说明:** 打磨项风险低且部分涉及 skill 目录改名（影响触发），留作后续独立方案

## 影响范围

- **模块:** skills/helloagents（develop, design, lifecycle, kb, routing, analyze, multi_model, hello-subagent, qa-review, templates）+ 两端 bootstrap
- **文件:** 两树共约 15 个 markdown 文件（互为镜像）
- **API:** 无
- **数据:** 无

## 核心场景

### 需求: 消除执行歧义
**模块:** skills/helloagents
执行开发实施步骤13、规划命令、轻量迭代时，规则集内部不再出现互相矛盾的指令。

#### 场景: 多模型验收
主代理按步骤13发起验收时，提示词契约与 multi_model 的审查类契约一致（Risk report only）。

#### 场景: 轻量迭代残留包再执行
轻量迭代方案包滞留 plan/ 后执行 ~exec，步骤1能将其识别为合法简化方案包而非报"方案包不完整"。

### 需求: 清除悬空术语
**模块:** skills/helloagents
新会话模型仅凭当前规则集即可理解全部术语，无需旧版本知识（P1/P2/P3、R1/R2、Phase2/3/4 不再出现或均有映射）。

#### 场景: 分发到目标项目
task.md 模板与 qa-review 示例中的验证命令为占位符，不再诱导模型在无 scripts/ 的目标项目执行必然失败的命令。

## 风险评估

- **风险:** `audit_skills.py` 的语义契约审计依赖若干精确字符串（如 `python scripts/audit_safety.py`、步骤标题、命令别名），改动措辞可能使审计失败
- **缓解:** 修改采用"占位符+保留原字符串作为示例"策略；每项完成后运行 `python scripts/audit_skills.py` 验证
- **风险:** 两树镜像不同步
- **缓解:** Claude 树修改后整目录同步到 Codex 树，由审计脚本的 mirror 检查兜底
