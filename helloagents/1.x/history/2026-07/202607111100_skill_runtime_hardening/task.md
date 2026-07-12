# 任务清单: Skill 运行时闭环加固

目录: `helloagents/1.x/plan/202607111100_skill_runtime_hardening/`

---

## 0. 方案边界确认
- [√] 0.1 确认范围覆盖审查结论且不写用户全局安装目录
  - 执行模式: AFK
  - 涉及文件: `why.md`, `how.md`, `task.md`
  - 完成标准: 范围内外与用户授权一致
  - 验证方式: 只读核对方案包

## 1. 审计测试 RED
- [√] 1.1 为危险 Markdown/Python 命令、依赖环和状态清理补失败测试
  - 执行模式: AFK
  - 涉及文件: `tests/test_audits.py`, `scripts/audit_skills.py`, `scripts/audit_safety.py`
  - 完成标准: 新测试在实现前因目标缺陷失败
  - 验证方式: `python -m unittest discover -s tests -v`

## 2. Skill 状态机与方案包
- [√] 2.1 修复授权清理、等待态、轻量方案包、P0 验收和 no-clobber 迁移
  - 执行模式: AFK
  - 涉及文件: `Codex/Skills/CN/skills/helloagents/{routing,develop,lifecycle,kb,qa-review,templates,output-format}/**`
  - 完成标准: 状态终态清理、轻量执行和归档不变量均可机器核对
  - 验证方式: 单元测试与 `python scripts/audit_skills.py`

## 3. 多模型和 bridge 安全
- [√] 3.1 增加数据出境门禁、宿主感知模型组合、默认 sandbox 和有界超时
  - 执行模式: AFK
  - 涉及文件: `Codex/Skills/CN/skills/helloagents/{multi_model,collaborating-*}/**`, `scripts/*_bridge.py`
  - 完成标准: 审查默认只读、有超时且 bridge 自包含
  - 验证方式: 单元测试、compile、`--help` 和 bundle 哈希检查

## 4. 分发与平台适配
- [√] 4.1 增加安装检查/同步工具，移除平台专属工具名并同步 Claude 镜像
  - 执行模式: AFK
  - 涉及文件: `scripts/manage_skills.py`, `Codex/Skills/CN/**`, `Claude/Skills/CN/**`
  - 完成标准: 双树在允许的平台中立契约下保持一致，安装漂移可检测
  - 验证方式: 双树 diff、安装 fixture、Skill 审计

## 5. 文档和 CI
- [√] 5.1 更新知识库、CHANGELOG 和跨平台 CI
  - 执行模式: AFK
  - 涉及文件: `.github/workflows/audit.yml`, `helloagents/1.x/{CHANGELOG.md,project.md,wiki/modules/skills.md}`
  - 完成标准: 维护者可复现全部验证且知识库反映新契约
  - 验证方式: 全量验证命令与文档核对

## 6. 复审与收口
- [√] 6.1 启动多个只读子代理独立审查修改并修复确认的问题
  - 执行模式: AFK
  - 涉及文件: 本方案范围内文件
  - 完成标准: 子代理无未处理 P0/P1，主代理复验通过
  - 验证方式: 子代理结构化报告 + 全量验证

## 7. 安全检查
- [√] 7.1 执行安全和一致性审计
  - 执行模式: AFK
  - 涉及文件: 本次全部变更
  - 完成标准: 无新增 secret、危险命令、未确认 EHRB 或镜像漂移
  - 验证方式: `python scripts/audit_safety.py` 与 `python scripts/audit_skills.py`

## 8. TDD
- [√] 8.1 RED → GREEN → REFACTOR → VERIFY
  - 执行模式: AFK
  - 涉及文件: `tests/**`, `scripts/**`, Skill 文档
  - 完成标准: RED 证据、实现通过、重构复测和最终验证完整
  - 验证方式: `python -m unittest discover -s tests -v`

## TDD 证据

- RED: 初始 10 个测试中 9 个按预期失败，覆盖危险命令漏检、依赖环、状态清理、轻量包、归档和 sandbox。
- GREEN: 实现及复审修复后 36 个测试通过，包含持续输出 deadline、leader 先退出后的进程树终止、畸形事件失败、安装回滚与嵌套知识库发现。
- REFACTOR: 将交互状态、QA gate、归档目标、轻量方案包元数据和 bridge 分发约束收敛到唯一职责模块。
- VERIFY: 三轮只读子代理复审已关闭全部仓库内 P0/P1；全量单元测试、Skill 审计、安全审计、compile、镜像比较和 bridge `--help` 通过。
