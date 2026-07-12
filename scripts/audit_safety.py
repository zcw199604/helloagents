#!/usr/bin/env python3
"""只读安全审计：扫描危险命令、密钥形态和高风险依赖脚本。"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DANGEROUS_PATTERNS = [
    (re.compile(r"(sudo\s+)?rm\s+(-[A-Za-z]*f[A-Za-z]*\s+)?(-[A-Za-z]*r[A-Za-z]*\s+)?(/|~|\*)"), "递归删除关键路径"),
    (re.compile(r"(sudo\s+)?rm\s+(-[A-Za-z]*r[A-Za-z]*\s+)?(-[A-Za-z]*f[A-Za-z]*\s+)?(/|~|\*)"), "递归删除关键路径"),
    (re.compile(r"\bcmd(?:\.exe)?\s*/c\b", re.I), "嵌套 cmd 会绕过 PowerShell 安全规则"),
    (re.compile(r"\bStart-Process\s+cmd(?:\.exe)?\b", re.I), "嵌套 cmd 会绕过 PowerShell 安全规则"),
    (re.compile(r"git\s+push\s+(-f|--force)"), "强制推送风险高，必须明确分支与授权"),
    (re.compile(r"git\s+reset\s+--hard"), "硬重置会丢弃本地变更"),
    (re.compile(r"DROP\s+(DATABASE|TABLE|SCHEMA)", re.I), "数据库破坏性命令"),
    (re.compile(r"\bTRUNCATE(?:\s+TABLE)?\b", re.I), "表数据清空命令"),
    (re.compile(r"chmod\s+777"), "全局可写权限风险高"),
    (re.compile(r"\bmkfs\b"), "文件系统格式化命令"),
    (re.compile(r"dd\s+.*of=/dev/"), "直接写入设备"),
    (re.compile(r"FLUSHALL|FLUSHDB", re.I), "Redis 数据清空命令"),
]

HIGH_RISK_COMMAND_PATTERNS = [
    (re.compile(r"\bnpm\s+publish\b", re.I), "包发布命令"),
    (re.compile(r"\bgh\s+release\s+create\b", re.I), "发布 release 命令"),
    (re.compile(r"\bterraform\s+(apply|destroy)\b", re.I), "基础设施变更命令"),
    (re.compile(r"\b(kubectl|helm)\s+(apply|delete|upgrade|rollback|set|rollout)\b", re.I), "集群变更命令"),
    (re.compile(r"\b(prisma|drizzle-kit|sequelize-cli|typeorm)\b.*\b(migrate|migration)\b", re.I), "数据库迁移命令"),
    (re.compile(r"\b(vercel|wrangler|netlify|flyctl|fly)\b.*\b(deploy|publish)\b", re.I), "部署命令"),
]

SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "检测到 AWS Access Key ID"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "检测到 GitHub Personal Access Token"),
    (re.compile(r"github_pat_[A-Za-z0-9]{22}_[A-Za-z0-9]{59}"), "检测到 GitHub Fine-grained PAT"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "检测到 API secret key"),
    (re.compile(r"key-[A-Za-z0-9]{20,}"), "检测到 API key"),
    (re.compile(r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----"), "检测到私钥"),
    (re.compile(r"password\s*[:=]\s*[\"'][^\"']{4,}[\"']", re.I), "检测到硬编码密码"),
    (re.compile(r"secret\s*[:=]\s*[\"'][^\"']{4,}[\"']", re.I), "检测到硬编码密钥"),
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "检测到 Google API Key"),
    (re.compile(r"xox[bpras]-[0-9A-Za-z\-]+"), "检测到 Slack Token"),
    (re.compile(r"eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_.+/=]+"), "检测到 JWT token"),
    (re.compile(r"(postgres|mysql|mongodb(\+srv)?):\/\/[^:\s]+:[^@\s]+@", re.I), "检测到包含凭据的数据库连接串"),
    (re.compile(r"sk_live_[A-Za-z0-9]{24,}"), "检测到 Stripe Secret Key"),
    (re.compile(r"sk-ant-[A-Za-z0-9\-]{20,}"), "检测到 Anthropic API Key"),
]

TEXT_EXTENSIONS = {
    ".bash",
    ".cmd",
    ".env",
    ".js",
    ".json",
    ".mjs",
    ".md",
    ".npmrc",
    ".properties",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
    ".zsh",
}
TEXT_FILE_NAMES = {
    ".env",
    ".npmrc",
    "Dockerfile",
    "Jenkinsfile",
    "Makefile",
}
COMMAND_EXTENSIONS = {".bash", ".cmd", ".ps1", ".sh", ".yaml", ".yml", ".zsh"}
COMMAND_FILE_NAMES = {"Dockerfile", "Jenkinsfile", "Makefile"}
SHELL_FENCE_LANGUAGES = {"bash", "bat", "batch", "cmd", "console", "powershell", "ps1", "pwsh", "sh", "shell", "zsh"}
MAX_TEXT_BYTES = 1_000_000
SKIP_PARTS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def list_tracked_files(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        )
        return [root / line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return [
            path
            for path in root.rglob("*")
            if path.is_file() and not (set(path.relative_to(root).parts) & SKIP_PARTS)
        ]


def read_text(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in TEXT_FILE_NAMES:
        return None
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None
    except OSError:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def scan_patterns(text: str, patterns: list[tuple[re.Pattern[str], str]]) -> list[str]:
    return [reason for pattern, reason in patterns if pattern.search(text)]


def scan_command(command: str) -> list[str]:
    issues = scan_patterns(command, DANGEROUS_PATTERNS)
    issues.extend(scan_patterns(command, HIGH_RISK_COMMAND_PATTERNS))
    if re.search(r"\bpowershell(?:\.exe)?\b", command, re.I) and re.search(r"\s-Command\b", command, re.I):
        inline = re.split(r"\s-Command\b", command, flags=re.I)[-1]
        logical_lines = [part.strip() for part in re.split(r"[;\r\n]+", inline) if part.strip()]
        if len(logical_lines) > 3:
            issues.append("PowerShell 内联脚本超过 3 个逻辑行，请改用临时 .ps1 文件")
    file_ops = re.findall(r"\b(remove-item|move-item|copy-item|new-item|set-content|add-content|out-file|mkdir|cp|mv|rm|rmdir)\b", command, flags=re.I)
    if len(file_ops) > 1 and re.search(r"[;\r\n]", command):
        issues.append("单条 shell 命令串联多个文件操作，请拆成独立命令")
    return issues


def is_command_file(path: Path) -> bool:
    return path.suffix.lower() in COMMAND_EXTENSIONS or path.name in COMMAND_FILE_NAMES


def iter_effective_command_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("#", "//", "REM ", "rem ")):
            continue
        lines.append(line)
    return lines


def scan_command_file(path: Path, text: str) -> list[str]:
    if not is_command_file(path):
        return []
    issues: list[str] = []
    patterns = DANGEROUS_PATTERNS + HIGH_RISK_COMMAND_PATTERNS
    for line in iter_effective_command_lines(text):
        issues.extend(scan_patterns(line, patterns))
    return sorted(set(issues))


def scan_markdown_commands(path: Path, text: str) -> list[str]:
    if path.suffix.lower() != ".md":
        return []
    issues: list[str] = []
    fence_pattern = re.compile(
        r"^(?P<fence>`{3,}|~{3,})(?P<info>[^\r\n]*)\r?\n(?P<body>[\s\S]*?)^(?P=fence)\s*$",
        re.MULTILINE,
    )
    patterns = DANGEROUS_PATTERNS + HIGH_RISK_COMMAND_PATTERNS
    for match in fence_pattern.finditer(text):
        info = match.group("info").strip().split(maxsplit=1)
        if not info:
            continue
        language = info[0].lower()
        if language not in SHELL_FENCE_LANGUAGES:
            continue
        for line in iter_effective_command_lines(match.group("body")):
            issues.extend(scan_patterns(line, patterns))
    return sorted(set(issues))


def _call_name(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def _constant_command(node: ast.AST, constants: dict[str, str] | None = None) -> str | None:
    if isinstance(node, ast.Name) and constants is not None:
        return constants.get(node.id)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        values: list[str] = []
        for element in node.elts:
            if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
                return None
            values.append(element.value)
        return shlex.join(values)
    return None


def scan_python_commands(path: Path, text: str) -> list[str]:
    if path.suffix.lower() != ".py":
        return []
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return []
    process_calls = {
        "os.popen",
        "os.system",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "subprocess.Popen",
        "subprocess.run",
    }
    module_aliases = {"os": "os", "subprocess": "subprocess"}
    direct_calls: dict[str, str] = {}
    constants: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for imported in node.names:
                if imported.name in {"os", "subprocess"}:
                    module_aliases[imported.asname or imported.name] = imported.name
        elif isinstance(node, ast.ImportFrom) and node.module in {"os", "subprocess"}:
            for imported in node.names:
                direct_calls[imported.asname or imported.name] = f"{node.module}.{imported.name}"
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            command = _constant_command(value)
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if command is not None:
                for target in targets:
                    if isinstance(target, ast.Name):
                        constants[target.id] = command

    issues: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        call_name = _call_name(node.func)
        if call_name in direct_calls:
            call_name = direct_calls[call_name]
        elif "." in call_name:
            prefix, suffix = call_name.split(".", 1)
            if prefix in module_aliases:
                call_name = f"{module_aliases[prefix]}.{suffix}"
        if call_name not in process_calls:
            continue
        command = _constant_command(node.args[0], constants) if node.args else None
        if command is not None:
            issues.extend(scan_command(command))
        shell_keyword = next((keyword for keyword in node.keywords if keyword.arg == "shell"), None)
        if (
            shell_keyword
            and isinstance(shell_keyword.value, ast.Constant)
            and shell_keyword.value.value is True
            and command is None
        ):
            issues.append("Python 使用 shell=True 执行动态命令")
    return sorted(set(issues))


def scan_package_json(path: Path, text: str) -> list[str]:
    issues: list[str] = []
    if path.name != "package.json":
        return issues
    try:
        scripts = json.loads(text).get("scripts", {})
    except json.JSONDecodeError:
        issues.append("package.json 不是合法 JSON")
        return issues
    for name, command in scripts.items():
        for reason in scan_command(str(command)):
            issues.append(f"package.json 脚本 `{name}`: {reason}")
        if name in {"preinstall", "postinstall", "preuninstall"} and re.search(r"\b(curl|wget|bash|sh|eval|exec)\b", str(command), re.I):
            issues.append(f"package.json 生命周期脚本 `{name}` 调用潜在危险命令")
    return issues


def scan_repo(root: Path) -> list[str]:
    issues: list[str] = []
    for path in list_tracked_files(root):
        if not path.exists() or set(path.relative_to(root).parts) & SKIP_PARTS:
            continue
        text = read_text(path)
        if text is None:
            continue
        rel = path.relative_to(root)
        for reason in scan_patterns(text, SECRET_PATTERNS):
            issues.append(f"{rel}: {reason}")
        for reason in scan_command_file(path, text):
            issues.append(f"{rel}: {reason}")
        for reason in scan_markdown_commands(path, text):
            issues.append(f"{rel}: {reason}")
        for reason in scan_python_commands(path, text):
            issues.append(f"{rel}: {reason}")
        for reason in scan_package_json(path, text):
            issues.append(f"{rel}: {reason}")
    return issues


def self_test() -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "deploy.sh").write_text("npm publish\n", encoding="utf-8")
        (root / ".env").write_text("pass" + "word='hardcoded'\n", encoding="utf-8")
        (root / "README.md").write_text("```bash\nrm -rf /\n```\n", encoding="utf-8")
        (root / "danger.py").write_text(
            'import subprocess\nsubprocess.run(["git", "reset", "--hard"])\n',
            encoding="utf-8",
        )
        repo_issues = scan_repo(root)
    checks = {
        "dangerous": scan_command("cmd /c dir"),
        "high_risk": scan_command("npm publish"),
        "secret": scan_patterns("token='sk-" + "a" * 24 + "'", SECRET_PATTERNS),
        "repo_command": [issue for issue in repo_issues if "包发布命令" in issue],
        "repo_dotenv": [issue for issue in repo_issues if "硬编码密码" in issue],
        "repo_markdown": [issue for issue in repo_issues if "递归删除关键路径" in issue],
        "repo_python": [issue for issue in repo_issues if "硬重置" in issue],
    }
    return [name for name, result in checks.items() if not result]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit dangerous commands and secret-like content.")
    parser.add_argument("--command", help="scan a shell command string")
    parser.add_argument("--path", default=str(ROOT), help="repository path to scan")
    parser.add_argument("--self-test", action="store_true", help="run built-in pattern checks")
    args = parser.parse_args()

    if args.self_test:
        failures = self_test()
        if failures:
            print("SAFETY SELF-TEST FAILED:")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("safety self-test passed")
        return 0

    issues = scan_command(args.command) if args.command else scan_repo(Path(args.path).resolve())
    if issues:
        print("SAFETY ISSUES:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("safety audit passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
