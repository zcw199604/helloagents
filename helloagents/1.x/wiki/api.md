# API 手册

本项目当前没有对外运行时 API。可执行接口主要是仓库脚本。

## 脚本

| 命令 | 类型 | 说明 |
|---|---|---|
| `python scripts/audit_skills.py` | 只读审计 | 校验严格 frontmatter、Markdown 链接、依赖 DAG、bundled bridge、双端镜像和状态/方案包语义契约 |
| `python scripts/audit_safety.py` | 只读安全审计 | 扫描命令文件、Markdown shell 块、Python 进程调用、发布/部署命令和密钥形态 |
| `python scripts/manage_skills.py --platform codex --target <path>/helloagents --bootstrap-target <path>/AGENTS.md --check` | 只读安装检查 | 比较仓库与安装副本及 bootstrap 的文件集合和 SHA-256；Claude 平台使用 `CLAUDE.md` |
| `python scripts/manage_skills.py --platform codex --target <path>/helloagents --bootstrap-target <path>/AGENTS.md --install` | 显式安装 | 校验目标边界，备份后联合安装 Skill 树与 bootstrap；任一步失败会回滚 Skill 树，且不会由常规审计自动触发 |
| `python -m unittest discover -s tests -v` | 回归测试 | 验证审计假阴性、状态清理、轻量包、no-clobber、sandbox 和安装备份 |
