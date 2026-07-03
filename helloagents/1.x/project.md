# 项目技术约定

## 技术栈

- 文档主体为 Markdown，编码使用 UTF-8 无 BOM。
- 自动化脚本使用 Python 标准库优先，避免新增运行时依赖。
- Codex 与 Claude 两端 skill 内容保持镜像一致。

## 开发约定

- `SKILL.md` 作为轻量入口，保留触发条件、职责边界、正反例和完成门禁。
- 长模板、细则和协议下沉到同目录 `references/`。
- 新增或修改 skill 时同步更新 `skills/helloagents/SKILL_INDEX.md`。

## 验证约定

- 修改 skill 后运行 `python scripts/audit_skills.py`。
- 涉及安全规则、命令示例或脚本变更后运行 `python scripts/audit_safety.py`。
- `audit_safety.py` 默认仓库扫描必须覆盖脚本/配置文件中的危险命令、高风险发布/部署命令和常见密钥形态。
- 审计脚本必须保持只读，不创建、修改或删除仓库文件。
