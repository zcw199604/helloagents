#!/usr/bin/env python3
"""只读审计 HelloAGENTS skills 的元数据、引用和双端一致性。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    from scripts import eval_skills
except ModuleNotFoundError:  # 直接执行时 scripts/ 是首个模块搜索路径。
    import eval_skills


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT
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
MAX_BOOTSTRAP_LINES = 120
REFERENCE_PATTERN = re.compile(r"((?:\.\./)?(?:[A-Za-z0-9_-]+/)?references/[A-Za-z0-9_.\-/]+\.md)")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
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
    "~test",
}
TASK_METADATA_LABELS = ["执行模式", "涉及文件", "完成标准", "验证方式"]
BRIDGE_BUNDLES = {
    "collaborating-with-claude": ROOT / "scripts" / "claude_bridge.py",
    "collaborating-with-codex": ROOT / "scripts" / "codex_bridge.py",
    "collaborating-with-gemini": ROOT / "scripts" / "gemini_bridge.py",
}


def normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def relative_files(root: Path) -> dict[Path, Path]:
    base = root / SKILL_TREE
    return {
        path.relative_to(base): path
        for path in base.rglob("*")
        if path.is_file()
    }


def parse_frontmatter_strict(path: Path) -> tuple[dict[str, object], str, list[str]]:
    text = normalized_text(path)
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, text, [f"{path}: 缺少 frontmatter 起始分隔符"]
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text, [f"{path}: 缺少 frontmatter 结束分隔符"]
    fields: dict[str, object] = {}
    current_list: str | None = None
    for line_number, raw_line in enumerate(text[4:end].splitlines(), start=2):
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_list:
            value = line[4:].strip()
            if not value:
                errors.append(f"{path}:{line_number}: frontmatter 列表项不能为空")
                continue
            fields.setdefault(current_list, [])
            assert isinstance(fields[current_list], list)
            fields[current_list].append(value)
            continue
        if line.startswith(" "):
            errors.append(f"{path}:{line_number}: frontmatter 缩进无效")
            current_list = None
            continue
        if ":" not in line:
            errors.append(f"{path}:{line_number}: frontmatter 字段缺少冒号")
            current_list = None
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in fields:
            errors.append(f"{path}:{line_number}: frontmatter 重复字段 `{key}`")
            current_list = None
            continue
        current_list = None
        if value == "":
            fields[key] = []
            current_list = key
        elif value == "[]":
            fields[key] = []
        else:
            fields[key] = value
    unknown = set(fields) - REQUIRED_FRONTMATTER
    for key in sorted(unknown):
        errors.append(f"{path}: frontmatter 包含未知字段 `{key}`")
    return fields, text[end + 5 :], errors


def parse_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    fields, body, _ = parse_frontmatter_strict(path)
    return fields, body


def dependency_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    cycles: set[tuple[str, ...]] = set()
    visiting: list[str] = []
    visited: set[str] = set()

    def canonicalize(cycle: list[str]) -> tuple[str, ...]:
        body = cycle[:-1]
        rotations = [tuple(body[index:] + body[:index]) for index in range(len(body))]
        smallest = min(rotations)
        return smallest + (smallest[0],)

    def visit(node: str) -> None:
        if node in visiting:
            start = visiting.index(node)
            cycles.add(canonicalize(visiting[start:] + [node]))
            return
        if node in visited:
            return
        visiting.append(node)
        for dependency in graph.get(node, []):
            if dependency in graph:
                visit(dependency)
        visiting.pop()
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return [list(cycle) for cycle in sorted(cycles)]


def markdown_link_errors(path: Path) -> list[str]:
    text = re.sub(r"```[\s\S]*?```", "", normalized_text(path))
    errors: list[str] = []
    for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
        target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        if "<" in target or ">" in target:
            continue
        target_path = target.split("#", 1)[0]
        if target_path and not (path.parent / target_path).resolve().exists():
            errors.append(f"{path}: Markdown 链接不存在 {target}")
    return errors


def knowledge_markdown_link_errors(kb_root: Path, path: Path) -> list[str]:
    text = re.sub(r"```[\s\S]*?```", "", normalized_text(path))
    errors: list[str] = []
    for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
        target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        if "<" in target or ">" in target:
            continue
        target_path = target.split("#", 1)[0]
        resolved = (path.parent / target_path).resolve()
        if not target_path or resolved.exists():
            continue
        match = re.search(r"history/\d{4}-\d{2}/([^/]+)", resolved.as_posix())
        if match and (kb_root / "plan" / match.group(1)).exists():
            continue
        errors.append(f"{path}: Markdown 链接不存在 {target}")
    return errors


def plan_package_errors(package: Path) -> list[str]:
    errors: list[str] = []
    task = package / "task.md"
    if not task.exists() or not task.read_text(encoding="utf-8").strip():
        return [f"{package}: 缺少非空 task.md"]
    task_text = normalized_text(task)
    if "模式: 轻量迭代" in task_text:
        required = ["轻量方案包元数据", "范围摘要", "核心场景", "知识库同步", "ADR", "验证策略"]
        for field in required:
            if field not in task_text:
                errors.append(f"{task}: 轻量方案包缺少 `{field}`")
    else:
        for name in ["why.md", "how.md"]:
            target = package / name
            if not target.exists() or not target.read_text(encoding="utf-8").strip():
                errors.append(f"{package}: 缺少非空 {name}")
    return errors


def tdd_evidence_errors(path: Path, evidence: object) -> list[str]:
    prefix = f"{path}: tdd"
    if not isinstance(evidence, dict):
        return [f"{prefix} 必须是对象"]

    required = {"classification", "decision", "target_behaviors"}
    missing = required - set(evidence)
    if missing:
        return [f"{prefix} 缺少 {', '.join(sorted(missing))}"]

    errors: list[str] = []
    classification = evidence["classification"]
    decision = evidence["decision"]
    if classification not in {"mandatory", "recommended", "exempt", "uncertain"}:
        errors.append(f"{prefix}.classification 值无效 `{classification}`")
    if decision not in {"tdd", "exempt"}:
        errors.append(f"{prefix}.decision 值无效 `{decision}`")
    target_behaviors = evidence["target_behaviors"]
    if (
        not isinstance(target_behaviors, list)
        or not target_behaviors
        or not all(isinstance(item, str) and item.strip() for item in target_behaviors)
    ):
        errors.append(f"{prefix}.target_behaviors 必须是非空字符串列表")
    if errors:
        return errors

    if decision == "exempt":
        if classification == "mandatory":
            errors.append(f"{prefix}: mandatory 分类不得使用 exempt 决策")
        for field in ["exempt_reason", "alternative_verification"]:
            value = evidence.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}.{field} 必须是非空字符串")
        return errors

    if classification == "exempt":
        errors.append(f"{prefix}: exempt 分类必须使用 exempt 决策")
        return errors

    phase_expectations = {
        "red": "failed",
        "green": "passed",
        "refactor": "passed",
        "verify": "passed",
    }
    for phase, expected_result in phase_expectations.items():
        record = evidence.get(phase)
        if not isinstance(record, dict):
            errors.append(f"{prefix}.{phase} 必须是对象")
            continue
        for field in ["command", "summary"]:
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}.{phase}.{field} 必须是非空字符串")
        if record.get("result") != expected_result:
            errors.append(
                f"{prefix}.{phase}.result 必须是 `{expected_result}`"
            )
        if phase == "refactor" and not isinstance(record.get("performed"), bool):
            errors.append(f"{prefix}.refactor.performed 必须是布尔值")
    return errors


def qa_json_errors(path: Path) -> list[str]:
    try:
        payload = json.loads(normalized_text(path))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        return [f"{path}: qa-review.json 无效: {error}"]
    required = {
        "schema_version", "qa_mode", "scope", "outcome", "gate_status", "conclusion",
        "findings", "file_references", "commands", "task_verification",
    }
    if not isinstance(payload, dict):
        return [f"{path}: qa-review.json 根节点必须是对象"]
    errors: list[str] = []
    if payload.get("schema_version") == 1:
        legacy_required = {
            "schema_version", "qa_mode", "scope", "outcome", "conclusion",
            "findings", "file_references", "commands", "task_verification",
        }
        missing = legacy_required - set(payload)
        if missing:
            errors.append(f"{path}: qa-review.json v1 缺少 {', '.join(sorted(missing))}")
        if payload.get("qa_mode") not in {"standard", "deep"}:
            errors.append(f"{path}: qa_mode 值无效 `{payload.get('qa_mode')}`")
        if payload.get("outcome") not in {"clean", "findings"}:
            errors.append(f"{path}: outcome 值无效 `{payload.get('outcome')}`")
        for field in ["findings", "file_references", "commands", "task_verification"]:
            if not isinstance(payload.get(field), list):
                errors.append(f"{path}: {field} 必须是列表")
        return errors
    missing = required - set(payload)
    if missing:
        errors.append(f"{path}: qa-review.json 缺少 {', '.join(sorted(missing))}")
        return errors
    if payload["schema_version"] not in {2, 3}:
        errors.append(f"{path}: schema_version 必须是整数 2 或 3")
    for field in ["scope", "conclusion"]:
        if not isinstance(payload[field], str) or not payload[field].strip():
            errors.append(f"{path}: {field} 必须是非空字符串")
    enum_fields = {
        "qa_mode": {"standard", "deep"},
        "outcome": {"clean", "findings"},
        "gate_status": {"passed", "blocked", "risk_accepted"},
    }
    for field, allowed in enum_fields.items():
        if payload[field] not in allowed:
            errors.append(f"{path}: {field} 值无效 `{payload[field]}`")
    list_fields = ["findings", "file_references", "commands", "task_verification"]
    for field in list_fields:
        if not isinstance(payload[field], list):
            errors.append(f"{path}: {field} 必须是列表")
    if errors:
        return errors

    if payload["schema_version"] == 3:
        errors.extend(tdd_evidence_errors(path, payload.get("tdd")))

    if not payload["commands"]:
        errors.append(f"{path}: commands 至少包含一条实际验证或跳过说明")

    if not all(isinstance(item, str) and item.strip() for item in payload["file_references"]):
        errors.append(f"{path}: file_references 必须只含非空字符串")
    finding_required = {"severity", "status", "title", "evidence"}
    for index, finding in enumerate(payload["findings"]):
        if not isinstance(finding, dict) or not finding_required <= set(finding):
            errors.append(f"{path}: findings[{index}] 缺少 severity/status/title/evidence")
            continue
        if finding["severity"] not in {"P0", "P1", "P2"}:
            errors.append(f"{path}: findings[{index}].severity 值无效")
        if finding["status"] not in {"open", "resolved", "accepted"}:
            errors.append(f"{path}: findings[{index}].status 值无效")
        if finding["severity"] == "P0" and finding["status"] == "accepted":
            errors.append(f"{path}: P0 不允许标记为 accepted")
        for field in ["title", "evidence"]:
            if not isinstance(finding[field], str) or not finding[field].strip():
                errors.append(f"{path}: findings[{index}].{field} 必须是非空字符串")
    for field, required_fields, allowed_status in [
        ("commands", {"command", "result", "note"}, {"passed", "failed", "skipped"}),
        ("task_verification", {"task", "status", "evidence"}, {"passed", "failed", "skipped"}),
    ]:
        for index, item in enumerate(payload[field]):
            if not isinstance(item, dict) or not required_fields <= set(item):
                errors.append(f"{path}: {field}[{index}] 字段不完整")
                continue
            status_field = "result" if field == "commands" else "status"
            if item[status_field] not in allowed_status:
                errors.append(f"{path}: {field}[{index}].{status_field} 值无效")
            for text_field in required_fields - {status_field}:
                if not isinstance(item[text_field], str) or not item[text_field].strip():
                    errors.append(f"{path}: {field}[{index}].{text_field} 必须是非空字符串")

    blocking = any(
        item.get("severity") == "P0" and item.get("status") != "resolved"
        or item.get("severity") == "P1" and item.get("status") == "open"
        for item in payload["findings"] if isinstance(item, dict)
    )
    accepted = any(
        item.get("severity") == "P1" and item.get("status") == "accepted"
        for item in payload["findings"] if isinstance(item, dict)
    )
    expected_gate = "blocked" if blocking else "risk_accepted" if accepted else "passed"
    if payload["gate_status"] != expected_gate:
        errors.append(f"{path}: gate_status 应为 `{expected_gate}`")
    if payload["outcome"] == "clean" and payload["findings"]:
        errors.append(f"{path}: outcome=clean 时 findings 必须为空")

    task = path.parent / "task.md"
    if task.exists():
        completed = set(re.findall(r"^- \[√\]\s+(\d+(?:\.\d+)*)\b", normalized_text(task), re.MULTILINE))
        verified_entries = {
            item.get("task"): item
            for item in payload["task_verification"]
            if isinstance(item, dict) and isinstance(item.get("task"), str)
        }
        verified = [item.get("task") for item in payload["task_verification"] if isinstance(item, dict)]
        if len(verified) != len(set(verified)):
            errors.append(f"{path}: task_verification 存在重复 task")
        missing_tasks = completed - set(verified_entries)
        if missing_tasks:
            errors.append(f"{path}: task_verification 缺少已完成任务 {', '.join(sorted(missing_tasks))}")
        for task_id in sorted(completed & set(verified_entries)):
            if verified_entries[task_id].get("status") != "passed":
                errors.append(f"{path}: 已完成任务 {task_id} 的验证状态必须是 passed")
    return errors


def audit_knowledge_bases(base: Path | None = None) -> list[str]:
    errors: list[str] = []
    base = base or ROOT / "helloagents"
    if not base.exists():
        return errors
    roots: set[Path] = set()
    for path in base.rglob("*"):
        if not path.is_dir():
            continue
        if any((path / marker).exists() for marker in ["project.md", "CHANGELOG.md", "wiki", "history"]):
            roots.add(path)
    for kb_root in sorted(roots):
        core = [
            kb_root / "CHANGELOG.md",
            kb_root / "project.md",
            kb_root / "wiki" / "overview.md",
            kb_root / "wiki" / "arch.md",
            kb_root / "wiki" / "api.md",
            kb_root / "wiki" / "data.md",
            kb_root / "wiki" / "glossary.md",
            kb_root / "history" / "index.md",
        ]
        for path in core:
            if not path.exists():
                errors.append(f"{kb_root}: 知识库缺少 {path.relative_to(kb_root)}")
        for markdown in sorted(kb_root.rglob("*.md")):
            errors.extend(knowledge_markdown_link_errors(kb_root, markdown))
        plan = kb_root / "plan"
        if plan.exists():
            for package in sorted(path for path in plan.iterdir() if path.is_dir()):
                errors.extend(plan_package_errors(package))
        history = kb_root / "history"
        index_text = normalized_text(history / "index.md") if (history / "index.md").exists() else ""
        if history.exists():
            for month in sorted(path for path in history.iterdir() if path.is_dir()):
                for package in sorted(path for path in month.iterdir() if path.is_dir()):
                    errors.extend(plan_package_errors(package))
                    relative = package.relative_to(history).as_posix()
                    if relative not in index_text:
                        errors.append(f"{history / 'index.md'}: 缺少历史方案 {relative}")
                    qa = package / "qa-review.json"
                    if qa.exists():
                        errors.extend(qa_json_errors(qa))
    return errors


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
    dependency_graph: dict[str, list[str]] = {}
    if not index.exists():
        errors.append(f"缺少索引矩阵: {index}")
    else:
        indexed = index_skill_names(index)
        for missing in sorted(names - indexed):
            errors.append(f"{index}: 缺少 skill 索引项 `{missing}`")
        for stale in sorted(indexed - names):
            errors.append(f"{index}: 索引项 `{stale}` 没有对应 SKILL.md")

    for skill_path in sorted(skill_base.glob("*/SKILL.md")):
        fields, body, frontmatter_errors = parse_frontmatter_strict(skill_path)
        errors.extend(frontmatter_errors)
        missing = REQUIRED_FRONTMATTER - set(fields)
        if missing:
            errors.append(f"{skill_path}: frontmatter 缺少 {', '.join(sorted(missing))}")
            continue

        name = fields.get("name")
        if name != skill_path.parent.name:
            errors.append(f"{skill_path}: name `{name}` 必须等于目录名 `{skill_path.parent.name}`")
        for key in ["name", "description", "completion_criteria"]:
            value = fields.get(key)
            if not isinstance(value, str):
                errors.append(f"{skill_path}: frontmatter `{key}` 必须是字符串")
            elif not value.strip():
                errors.append(f"{skill_path}: frontmatter `{key}` 不能为空")
        if fields.get("invocation") not in VALID_INVOCATION:
            errors.append(f"{skill_path}: invocation 值无效 `{fields.get('invocation')}`")
        if fields.get("side_effects") not in VALID_SIDE_EFFECTS:
            errors.append(f"{skill_path}: side_effects 值无效 `{fields.get('side_effects')}`")
        requires = fields.get("requires")
        if not isinstance(requires, list):
            errors.append(f"{skill_path}: requires 必须是列表")
            requires = []
        elif not all(isinstance(dependency, str) and dependency.strip() for dependency in requires):
            errors.append(f"{skill_path}: requires 必须只含非空字符串")
            requires = [dependency for dependency in requires if isinstance(dependency, str) and dependency.strip()]
        if len(requires) != len(set(requires)):
            errors.append(f"{skill_path}: requires 不得包含重复项")
        if name in requires:
            errors.append(f"{skill_path}: requires 不得自依赖")
        dependency_graph[str(name)] = list(requires)
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
        errors.extend(markdown_link_errors(markdown_path))

    for cycle in dependency_cycles(dependency_graph):
        errors.append(f"{skill_base}: requires 依赖环: {' -> '.join(cycle)}")

    return errors, warnings


def audit_distributions() -> list[str]:
    errors: list[str] = []
    source_files = relative_files(SOURCE_ROOT)
    for label, root in [("Codex", CODEX_ROOT), ("Claude", CLAUDE_ROOT)]:
        generated_files = relative_files(root)
        source_keys = set(source_files)
        generated_keys = set(generated_files)
        for missing in sorted(source_keys - generated_keys):
            errors.append(f"{label} 分发缺少文件: {missing}")
        for extra in sorted(generated_keys - source_keys):
            errors.append(f"{label} 分发存在额外文件: {extra}")
        for rel in sorted(source_keys & generated_keys):
            if normalized_text(source_files[rel]) != normalized_text(generated_files[rel]):
                errors.append(f"{label} 分发与 canonical 源不一致: {rel}")

    return errors


def audit_bootstrap_pointer() -> list[str]:
    errors: list[str] = []
    expected = "skills/helloagents/SKILL_INDEX.md"
    for path in [CODEX_ROOT / "AGENTS.md", CLAUDE_ROOT / "CLAUDE.md"]:
        text = normalized_text(path)
        if expected not in text:
            errors.append(f"{path}: 缺少 SKILL_INDEX.md 指针")
        line_count = len(text.splitlines())
        if line_count > MAX_BOOTSTRAP_LINES:
            errors.append(
                f"{path}: bootstrap {line_count} 行，超过 {MAX_BOOTSTRAP_LINES} 行上限"
            )
    if normalized_text(CODEX_ROOT / "AGENTS.md") != normalized_text(CLAUDE_ROOT / "CLAUDE.md"):
        errors.append("Codex/Skills/CN/AGENTS.md 与 Claude/Skills/CN/CLAUDE.md 内容不一致")
    return errors


def require_text(path: Path, snippets: list[str], errors: list[str], label: str | None = None) -> None:
    text = normalized_text(path)
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{path}: 缺少语义约束 `{label or snippet}`")


def forbid_text(path: Path, snippets: list[str], errors: list[str]) -> None:
    text = normalized_text(path)
    for snippet in snippets:
        if snippet in text:
            errors.append(f"{path}: 包含禁止的语义 `{snippet}`")


def audit_bundled_bridges() -> list[str]:
    errors: list[str] = []
    for skill_name, source in BRIDGE_BUNDLES.items():
        source_text = normalized_text(source)
        for root in [SOURCE_ROOT, CODEX_ROOT, CLAUDE_ROOT]:
            bundled = root / SKILL_TREE / skill_name / "scripts" / "bridge.py"
            if not bundled.exists():
                errors.append(f"{bundled}: 缺少 bundled bridge")
            elif normalized_text(bundled) != source_text:
                errors.append(f"{bundled}: bundled bridge 与 {source} 不一致")
    return errors


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
    if "7.6" not in steps:
        errors.append(f"{path}: 缺少步骤7.6 唯一归档目标解析")
    step_positions = {
        match.group(1): match.start()
        for match in re.finditer(r"^### 步骤(\d+(?:\.\d+)?):", text, flags=re.MULTILINE)
    }
    if all(step in step_positions for step in ["7.5", "7.6", "8"]):
        if not step_positions["7.5"] < step_positions["7.6"] < step_positions["8"]:
            errors.append(f"{path}: 步骤顺序必须满足 7.5 < 7.6 < 8")
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
    codex_skill_base = SOURCE_ROOT / SKILL_TREE

    agents = CODEX_ROOT / "AGENTS.md"
    routing = codex_skill_base / "routing" / "SKILL.md"
    commands = codex_skill_base / "routing" / "references" / "commands-and-context.md"
    for path in [agents, routing, commands]:
        text = normalized_text(path)
        for command in sorted(COMMAND_ALIASES):
            if command not in text:
                errors.append(f"{path}: 命令别名 `{command}` 未同步")

    develop_count = extract_step_count(
        normalized_text(codex_skill_base / "develop" / "SKILL.md"),
        r"开发实施入口检查、(\d+)\s*步执行流程",
    )
    if develop_count is None:
        errors.append("开发实施步骤数语义审计失败: 未能解析 develop/SKILL.md")

    develop_entry = codex_skill_base / "develop" / "references" / "entry-and-steps.md"
    errors.extend(audit_entry_steps(develop_entry, develop_count))

    routing_decision = codex_skill_base / "routing" / "references" / "routing-decision.md"
    routing_paths = codex_skill_base / "routing" / "references" / "routing-paths.md"
    require_text(
        agents,
        ["自适应路由", "低风险", "中风险", "高风险", "普通 Bug", "文件数量只作为范围线索"],
        errors,
        "精简 bootstrap 风险路由",
    )
    forbid_text(agents, ["PENDING_INTERACTION", "WORKFLOW_ID", "<thinking>"], errors)
    require_text(
        routing_decision,
        ["风险等级: 低 | 中 | 高", "可逆性", "外部副作用", "公共契约", "数据迁移"],
        errors,
        "风险评估维度",
    )
    require_text(
        routing_paths,
        ["普通缺陷直接实施", "低风险小改动直接实施", "风险等级=高"],
        errors,
        "自适应路由路径",
    )
    forbid_text(routing_paths, ["文件≤2", "文件3-5", "文件>5"], errors)
    require_text(
        develop_entry,
        ["条件E - 用户明确授权的自适应开发", "EHRB=无", "自适应开发无方案包旁路"],
        errors,
        "自适应开发入口",
    )
    require_text(
        codex_skill_base / "analyze" / "references" / "code-analysis-and-output.md",
        ["自适应授权模式", "不设置 `DESIGN_CONFIRM`"],
        errors,
        "自适应分析阶段转换",
    )
    require_text(
        codex_skill_base / "design" / "references" / "output-and-transition.md",
        ["自适应授权模式", "不设置 `DEVELOPMENT_CONFIRM`"],
        errors,
        "自适应设计阶段转换",
    )

    index = codex_skill_base / "SKILL_INDEX.md"
    develop_index_match = re.search(r"^\|\s*`develop`\s*\|.+$", normalized_text(index), flags=re.MULTILINE)
    if not develop_index_match or "条件读取" not in develop_index_match.group(0):
        errors.append(f"{index}: develop 缺少自适应条件依赖说明")

    template = codex_skill_base / "templates" / "references" / "plan-package-templates.md"
    require_text(template, TASK_METADATA_LABELS, errors, "task.md 任务元数据")
    require_text(template, ["qa-review.json", "python scripts/audit_safety.py"], errors)
    errors.extend(audit_task_template_metadata(template))

    design = codex_skill_base / "design" / "references" / "detailed-planning.md"
    require_text(design, TASK_METADATA_LABELS + ["AFK", "HITL"], errors, "任务可验证性规则")

    qa_review = codex_skill_base / "qa-review" / "SKILL.md"
    require_text(
        qa_review,
        [
            "步骤7质量检查与测试完成后", "qa-review.json", "task_verification",
            '"schema_version": 3', '"tdd"', '"outcome": "clean"',
            '"gate_status": "passed"',
        ],
        errors,
    )
    require_text(develop_entry, ["读取 `qa-review` Skill", "qa-review.json", "P0 阻止归档", "P1 默认阻止归档", "P1 QA风险决策询问格式"], errors)

    test_skill = codex_skill_base / "test" / "SKILL.md"
    require_text(
        test_skill,
        ["Trigger: ~test [scope]", "TDD-EXEMPT", "qa-review.json"],
        errors,
        "测试命令契约",
    )

    lifecycle = codex_skill_base / "lifecycle" / "SKILL.md"
    transition = codex_skill_base / "develop" / "references" / "phase-transition.md"
    require_text(lifecycle, ["RESET_WORKFLOW_STATE", "AUTH_WORKFLOW_ID", "PENDING_INTERACTION", "RESOLVED_ARCHIVE_PATH", "no-clobber"], errors)
    require_text(transition, ["RESET_WORKFLOW_STATE", "步骤11.5", "no-clobber"], errors)
    forbid_text(lifecycle, ["同名覆盖"] , errors)
    forbid_text(develop_entry, ["强制覆盖"], errors)
    require_text(qa_review, ["轻量方案包元数据"], errors)
    require_text(codex_skill_base / "kb" / "references" / "knowledge-base-rules.md", ["轻量方案包元数据", "RESOLVED_ARCHIVE_PATH", "task.md#轻量方案包元数据"], errors)
    require_text(codex_skill_base / "hello-subagent" / "references" / "delegation-protocol.md", ["完整方案包", "轻量方案包"], errors)
    require_text(codex_skill_base / "multi_model" / "SKILL.md", ["外部数据门禁", "默认超时 600 秒", "P0 阻止归档"], errors)
    require_text(
        lifecycle,
        [
            "COMMAND_CONFIRM", "REQUIREMENT_INPUT", "SOLUTION_CHOICE", "SOLUTION_REDESIGN",
            "DESIGN_CONFIRM", "DEVELOPMENT_CONFIRM", "PACKAGE_CHOICE", "CONTEXT_CHOICE",
            "MM_REVIEW", "QUALITY_DECISION", "MM_ACCEPTANCE", "TEST_FAILURE_DECISION",
            "QA_RISK_DECISION", "PARTIAL_FAILURE_DECISION", "EHRB_CONFIRM",
        ],
        errors,
        "完整交互状态枚举",
    )
    interaction_contracts = {
        codex_skill_base / "analyze" / "references" / "requirement-assessment.md": ["PENDING_INTERACTION=REQUIREMENT_INPUT"],
        codex_skill_base / "analyze" / "references" / "code-analysis-and-output.md": ["PENDING_INTERACTION=DESIGN_CONFIRM"],
        codex_skill_base / "design" / "references" / "ideation.md": ["PENDING_INTERACTION=SOLUTION_CHOICE", "PENDING_INTERACTION=SOLUTION_REDESIGN"],
        codex_skill_base / "design" / "references" / "output-and-transition.md": ["PENDING_INTERACTION=MM_REVIEW", "PENDING_INTERACTION=DEVELOPMENT_CONFIRM"],
        develop_entry: ["PENDING_INTERACTION=PACKAGE_CHOICE", "PENDING_INTERACTION=TEST_FAILURE_DECISION", "PENDING_INTERACTION=QA_RISK_DECISION", "PENDING_INTERACTION=QUALITY_DECISION", "PENDING_INTERACTION=MM_ACCEPTANCE"],
        commands: ["PENDING_INTERACTION=COMMAND_CONFIRM", "PENDING_INTERACTION=CONTEXT_CHOICE", "TEST_FAILURE_DECISION` 消费序号", "MM_ACCEPTANCE` 消费序号", "QA_RISK_DECISION` 消费序号"],
        codex_skill_base / "output-format" / "references" / "exception-output.md": ["PENDING_INTERACTION=EHRB_CONFIRM", "PENDING_INTERACTION=PARTIAL_FAILURE_DECISION"],
    }
    for path, snippets in interaction_contracts.items():
        require_text(path, snippets, errors, "交互提示必须绑定等待态")

    safety = ROOT / "scripts" / "audit_safety.py"
    require_text(
        safety,
        ["DANGEROUS_PATTERNS", "HIGH_RISK_COMMAND_PATTERNS", "SECRET_PATTERNS", "scan_command_file", "TEXT_FILE_NAMES"],
        errors,
    )

    return errors


def audit_eval_cases() -> list[str]:
    path = ROOT / "evals" / "skill_routing_cases.json"
    cases, errors = eval_skills.read_collection(path, "cases")
    errors.extend(eval_skills.validate_cases(cases))
    errors.extend(eval_skills.validate_corpus(cases))
    return [f"{path}: {error}" for error in errors]


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    tree_errors, tree_warnings = audit_tree(SOURCE_ROOT)
    errors.extend(tree_errors)
    warnings.extend(tree_warnings)
    errors.extend(audit_distributions())
    errors.extend(audit_bootstrap_pointer())
    errors.extend(audit_bundled_bridges())
    errors.extend(audit_semantic_contracts())
    errors.extend(audit_eval_cases())
    errors.extend(audit_knowledge_bases())

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
