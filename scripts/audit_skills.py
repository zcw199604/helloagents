#!/usr/bin/env python3
"""只读审计 HelloAGENTS skills 的元数据、引用和双端一致性。"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_ROOT = ROOT / "Codex" / "Skills" / "CN"
CLAUDE_ROOT = ROOT / "Claude" / "Skills" / "CN"
SKILL_TREE = Path("skills") / "helloagents"
REQUIRED_FRONTMATTER = {
    "name",
    "description",
    "invocation",
    "side_effects",
    "requires",
    "completion_criteria",
}
MAX_SKILL_LINES = 220
REFERENCE_PATTERN = re.compile(r"((?:\.\./)?(?:[A-Za-z0-9_-]+/)?references/[A-Za-z0-9_.\-/]+\.md)")
VALID_INVOCATION = {"model", "user"}
VALID_SIDE_EFFECTS = {
    "read-only",
    "may_write_plan",
    "may_write_code_and_docs",
    "external_process",
    "may_spawn_subagents",
    "may_write_knowledge_base",
    "may_move_plan_packages",
    "may_write_tests",
}
COMMAND_ALIASES = {
    "~auto",
    "~helloauto",
    "~fa",
    "~init",
    "~wiki",
    "~plan",
    "~design",
    "~exec",
    "~run",
    "~execute",
}
TASK_METADATA_LABELS = ["执行模式", "涉及文件", "完成标准", "验证方式"]


def normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def relative_files(root: Path) -> dict[Path, Path]:
    base = root / SKILL_TREE
    return {
        path.relative_to(base): path
        for path in base.rglob("*")
        if path.is_file()
    }


def parse_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = normalized_text(path)
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fields: dict[str, object] = {}
    current_list: str | None = None
    for raw_line in text[4:end].splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_list:
            value = line[4:].strip()
            fields.setdefault(current_list, [])
            assert isinstance(fields[current_list], list)
            fields[current_list].append(value)
            continue
        if line.startswith(" ") or ":" not in line:
            current_list = None
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_list = None
        if value == "":
            fields[key] = []
            current_list = key
        elif value == "[]":
            fields[key] = []
        else:
            fields[key] = value
    return fields, text[end + 5 :]


def skill_names(root: Path) -> set[str]:
    return {path.parent.name for path in (root / SKILL_TREE).glob("*/SKILL.md")}


def index_skill_names(index: Path) -> set[str]:
    text = normalized_text(index)
    return set(re.findall(r"^\|\s*`([^`]+)`\s*\|", text, flags=re.MULTILINE))


def audit_tree(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_base = root / SKILL_TREE
    index = skill_base / "SKILL_INDEX.md"
    names = skill_names(root)
    if not index.exists():
        errors.append(f"缺少索引矩阵: {index}")
    else:
        indexed = index_skill_names(index)
        for missing in sorted(names - indexed):
            errors.append(f"{index}: 缺少 skill 索引项 `{missing}`")
        for stale in sorted(indexed - names):
            errors.append(f"{index}: 索引项 `{stale}` 没有对应 SKILL.md")

    for skill_path in sorted(skill_base.glob("*/SKILL.md")):
        fields, body = parse_frontmatter(skill_path)
        missing = REQUIRED_FRONTMATTER - set(fields)
        if missing:
            errors.append(f"{skill_path}: frontmatter 缺少 {', '.join(sorted(missing))}")
            continue

        name = fields.get("name")
        if name != skill_path.parent.name:
            errors.append(f"{skill_path}: name `{name}` 必须等于目录名 `{skill_path.parent.name}`")
        for key in ["description", "completion_criteria"]:
            if not str(fields.get(key, "")).strip():
                errors.append(f"{skill_path}: frontmatter `{key}` 不能为空")
        if fields.get("invocation") not in VALID_INVOCATION:
            errors.append(f"{skill_path}: invocation 值无效 `{fields.get('invocation')}`")
        if fields.get("side_effects") not in VALID_SIDE_EFFECTS:
            errors.append(f"{skill_path}: side_effects 值无效 `{fields.get('side_effects')}`")
        requires = fields.get("requires")
        if not isinstance(requires, list):
            errors.append(f"{skill_path}: requires 必须是列表")
            requires = []
        for dependency in requires:
            if dependency not in names:
                errors.append(f"{skill_path}: requires 指向不存在的 skill `{dependency}`")

        line_count = len(normalized_text(skill_path).splitlines())
        if line_count > MAX_SKILL_LINES:
            warnings.append(f"{skill_path}: SKILL.md {line_count} 行，建议继续拆薄")

    for markdown_path in sorted(skill_base.rglob("*.md")):
        for ref in REFERENCE_PATTERN.findall(normalized_text(markdown_path)):
            target = (markdown_path.parent / ref).resolve()
            if not target.exists():
                errors.append(f"{markdown_path}: 引用不存在 {ref}")

    return errors, warnings


def audit_mirror() -> list[str]:
    errors: list[str] = []
    codex_files = relative_files(CODEX_ROOT)
    claude_files = relative_files(CLAUDE_ROOT)
    codex_keys = set(codex_files)
    claude_keys = set(claude_files)

    for missing in sorted(codex_keys - claude_keys):
        errors.append(f"Claude 缺少文件: {missing}")
    for extra in sorted(claude_keys - codex_keys):
        errors.append(f"Claude 存在 Codex 没有的文件: {extra}")

    for rel in sorted(codex_keys & claude_keys):
        if normalized_text(codex_files[rel]) != normalized_text(claude_files[rel]):
            errors.append(f"Codex/Claude 内容不一致: {rel}")

    return errors


def audit_bootstrap_pointer() -> list[str]:
    errors: list[str] = []
    expected = "skills/helloagents/SKILL_INDEX.md"
    for path in [CODEX_ROOT / "AGENTS.md", CLAUDE_ROOT / "CLAUDE.md"]:
        if expected not in normalized_text(path):
            errors.append(f"{path}: 缺少 SKILL_INDEX.md 指针")
    if normalized_text(CODEX_ROOT / "AGENTS.md") != normalized_text(CLAUDE_ROOT / "CLAUDE.md"):
        errors.append("Codex/Skills/CN/AGENTS.md 与 Claude/Skills/CN/CLAUDE.md 内容不一致")
    return errors


def require_text(path: Path, snippets: list[str], errors: list[str], label: str | None = None) -> None:
    text = normalized_text(path)
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{path}: 缺少语义约束 `{label or snippet}`")


def extract_step_count(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text)
    if not match:
        return None
    return int(match.group(1))


def audit_entry_steps(path: Path, expected_count: int | None) -> list[str]:
    errors: list[str] = []
    text = normalized_text(path)
    steps = re.findall(r"^### 步骤(\d+(?:\.\d+)?):", text, flags=re.MULTILINE)
    main_steps = sorted({int(step) for step in steps if "." not in step})
    if expected_count is not None:
        expected = list(range(1, expected_count + 1))
        if main_steps != expected:
            errors.append(f"{path}: 实际步骤标题不完整，期望 {expected}，实际 {main_steps}")
    if "7.5" not in steps:
        errors.append(f"{path}: 缺少步骤7.5 QA 证据记录")
    return errors


def audit_task_template_metadata(path: Path) -> list[str]:
    errors: list[str] = []
    text = normalized_text(path)
    task_matches = list(re.finditer(r"^- \[ \] ([^\n]+)", text, flags=re.MULTILINE))
    for index, match in enumerate(task_matches):
        end = task_matches[index + 1].start() if index + 1 < len(task_matches) else len(text)
        block = text[match.start():end]
        for label in TASK_METADATA_LABELS:
            if f"- {label}:" not in block:
                errors.append(f"{path}: 任务 `{match.group(1)}` 缺少 `{label}`")
    verify_match = re.search(r"^- \[ \] 5A\.4 VERIFY:[\s\S]*?(?=^### 5B\.|^## |\Z)", text, flags=re.MULTILINE)
    if verify_match and "qa-review.json" in verify_match.group(0):
        errors.append(f"{path}: 5A.4 VERIFY 不应依赖 qa-review.json，QA 证据应由开发步骤7.5生成")
    return errors


def audit_semantic_contracts() -> list[str]:
    errors: list[str] = []
    codex_skill_base = CODEX_ROOT / SKILL_TREE

    agents = CODEX_ROOT / "AGENTS.md"
    routing = codex_skill_base / "routing" / "SKILL.md"
    commands = codex_skill_base / "routing" / "references" / "commands-and-context.md"
    for path in [agents, routing, commands]:
        text = normalized_text(path)
        for command in sorted(COMMAND_ALIASES):
            if command not in text:
                errors.append(f"{path}: 命令别名 `{command}` 未同步")

    bootstrap_count = extract_step_count(
        normalized_text(agents),
        r"\|\s*开发实施\s*\|\s*(\d+)\s*步执行",
    )
    develop_count = extract_step_count(
        normalized_text(codex_skill_base / "develop" / "SKILL.md"),
        r"开发实施入口检查、(\d+)\s*步执行流程",
    )
    if bootstrap_count is None or develop_count is None:
        errors.append("开发实施步骤数语义审计失败: 未能解析 bootstrap 或 develop/SKILL.md")
    elif bootstrap_count != develop_count:
        errors.append(f"开发实施步骤数不一致: bootstrap={bootstrap_count}, develop={develop_count}")

    develop_entry = codex_skill_base / "develop" / "references" / "entry-and-steps.md"
    errors.extend(audit_entry_steps(develop_entry, develop_count))

    index = codex_skill_base / "SKILL_INDEX.md"
    develop_index_match = re.search(r"^\|\s*`develop`\s*\|.+$", normalized_text(index), flags=re.MULTILINE)
    if not develop_index_match or "qa-review" not in develop_index_match.group(0):
        errors.append(f"{index}: develop 依赖列缺少 `qa-review`")

    template = codex_skill_base / "templates" / "references" / "plan-package-templates.md"
    require_text(template, TASK_METADATA_LABELS, errors, "task.md 任务元数据")
    require_text(template, ["qa-review.json", "python scripts/audit_safety.py"], errors)
    errors.extend(audit_task_template_metadata(template))

    design = codex_skill_base / "design" / "references" / "detailed-planning.md"
    require_text(design, TASK_METADATA_LABELS + ["AFK", "HITL"], errors, "任务可验证性规则")

    qa_review = codex_skill_base / "qa-review" / "SKILL.md"
    require_text(qa_review, ["步骤7质量检查与测试完成后", "qa-review.json", "task_verification", '"outcome": "clean"'], errors)
    require_text(develop_entry, ["读取 `qa-review` Skill", "qa-review.json"], errors)

    safety = ROOT / "scripts" / "audit_safety.py"
    require_text(
        safety,
        ["DANGEROUS_PATTERNS", "HIGH_RISK_COMMAND_PATTERNS", "SECRET_PATTERNS", "scan_command_file", "TEXT_FILE_NAMES"],
        errors,
    )

    return errors


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for root in [CODEX_ROOT, CLAUDE_ROOT]:
        tree_errors, tree_warnings = audit_tree(root)
        errors.extend(tree_errors)
        warnings.extend(tree_warnings)
    errors.extend(audit_mirror())
    errors.extend(audit_bootstrap_pointer())
    errors.extend(audit_semantic_contracts())

    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"- {warning}")
    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("skills audit passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
