# API 手册

本项目当前没有对外运行时 API。可执行接口主要是仓库脚本。

## 脚本

| 命令 | 类型 | 说明 |
|---|---|---|
| `python scripts/audit_skills.py` | 只读审计 | 校验 skill 元数据、reference 引用、Codex/Claude 镜像一致性和语义契约 |
| `python scripts/audit_safety.py` | 只读安全审计 | 扫描脚本/配置中的危险命令、高风险发布/部署命令、密钥形态和高风险依赖脚本 |
