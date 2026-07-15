# 变更历史索引

本文件记录所有已完成变更的索引，便于追溯和查询。

---

## 索引

| 时间戳 | 功能名称 | 类型 | 状态 | 方案包路径 |
|--------|----------|------|------|------------|
| 202607152110 | adaptive_skill_routing | 优化 | ✅已完成 | [2026-07/202607152110_adaptive_skill_routing](2026-07/202607152110_adaptive_skill_routing/) |
| 202607121222 | tdd_hybrid_enforcement | 新功能 | ✅已完成 | [2026-07/202607121222_tdd_hybrid_enforcement](2026-07/202607121222_tdd_hybrid_enforcement/) |
| 202607111100 | skill_runtime_hardening | 加固 | ✅已完成 | [2026-07/202607111100_skill_runtime_hardening](2026-07/202607111100_skill_runtime_hardening/) |
| 202607032233 | skill_consistency_fixes | 修复 | ✅已完成 | [2026-07/202607032233_skill_consistency_fixes](2026-07/202607032233_skill_consistency_fixes/) |
| 202607022207 | skill_system_refactor | 重构 | ✅已完成 | [2026-07/202607022207_skill_system_refactor](2026-07/202607022207_skill_system_refactor/) |
| 202605142129 | slim_bootstrap | 重构 | ✅已完成 | [2026-05/202605142129_slim_bootstrap](2026-05/202605142129_slim_bootstrap/) |

---

## 按月归档

### 2026-07

- [202607152110_adaptive_skill_routing](2026-07/202607152110_adaptive_skill_routing/) - 新增路由 eval 基线、精简 bootstrap，并让普通 Bug 与低/中风险小改动按自适应路径连续实施
- [202607121222_tdd_hybrid_enforcement](2026-07/202607121222_tdd_hybrid_enforcement/) - 新增 `~test` 测试入口、QA schema v3 TDD 证据与离线审计门禁
- [202607111100_skill_runtime_hardening](2026-07/202607111100_skill_runtime_hardening/) - 加固 Skill 状态机、QA/归档门禁、多模型 bridge、安装分发与审计回归，完成三轮并行只读复审
- [202607032233_skill_consistency_fixes](2026-07/202607032233_skill_consistency_fixes/) - 修复 skills 审查发现的 6 处规则矛盾与 3 处遗留悬空，同步 Codex 镜像
- [202607022207_skill_system_refactor](2026-07/202607022207_skill_system_refactor/) - 拆薄大型 skill，补索引矩阵、统一元数据、增加只读审计脚本

### 2026-05

- [202605142129_slim_bootstrap](2026-05/202605142129_slim_bootstrap/) - 精简 HelloAGENTS bootstrap 文档（激进重构），抽取 4 个按需 Skill，入口由 1065 行降至 266 行
