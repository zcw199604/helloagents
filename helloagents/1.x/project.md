# 项目技术约定

## 技术栈

- 文档主体为 Markdown，编码使用 UTF-8 无 BOM。
- 自动化脚本使用 Python 标准库优先，避免新增运行时依赖。
- Codex 与 Claude 两端 skill 内容保持镜像一致。
- collaborating Skill 必须从自身 `scripts/bridge.py` 调用 bridge，不依赖用户项目中的相对脚本路径。

## 开发约定

- `SKILL.md` 作为轻量入口，保留触发条件、职责边界、正反例和完成门禁。
- 长模板、细则和协议下沉到同目录 `references/`。
- 新增或修改 skill 时同步更新 `skills/helloagents/SKILL_INDEX.md`。
- `requires` 只表示硬依赖并必须形成 DAG；条件性 Skill 调用写在正文，不得制造反向依赖环。
- 命令授权必须绑定当前 `WORKFLOW_ID`，所有终态执行 `RESET_WORKFLOW_STATE`。
- 新生成的 QA 证据使用 schema v3；`tdd` 字段必须记录 RED/GREEN/REFACTOR/VERIFY 或 TDD-EXEMPT，未解决 P0/P1 仍必须通过可执行 `gate_status` 阻止归档。
- `~test [scope]` 是受控测试入口：默认只修改测试与证据，发现生产缺陷时转入常规方案设计，不自动扩大为修复。
- KB、history 索引、迁移和最终输出必须共同使用 lifecycle 解析的 `RESOLVED_ARCHIVE_PATH`。

## 验证约定

- 修改 skill 后运行 `python scripts/audit_skills.py`。
- 修改脚本或规则后运行 `python -m unittest discover -s tests -v`。
- 涉及安全规则、命令示例或脚本变更后运行 `python scripts/audit_safety.py`。
- `audit_safety.py` 默认仓库扫描必须覆盖命令脚本、Markdown shell fenced block、Python 常量/变量进程调用与导入别名、高风险发布/部署命令和常见密钥形态。
- 审计脚本必须保持只读，不创建、修改或删除仓库文件。
- 安装副本使用 `python scripts/manage_skills.py --platform <codex|claude> --target <skills-path>/helloagents --bootstrap-target <bootstrap-path> --check` 检测 Skill 与 bootstrap 漂移；只有显式 `--install` 才写入，且必须校验路径、先备份并支持失败回滚。
