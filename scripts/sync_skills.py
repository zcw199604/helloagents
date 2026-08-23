#!/usr/bin/env python3
"""Generate platform skill distributions from the canonical skill source."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    from scripts.manage_skills import compare_trees, digest, relative_files
except ModuleNotFoundError:
    from manage_skills import compare_trees, digest, relative_files


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "helloagents"
DISTRIBUTIONS = [
    ROOT / "Codex" / "Skills" / "CN" / "skills" / "helloagents",
    ROOT / "Claude" / "Skills" / "CN" / "skills" / "helloagents",
]
BRIDGES = {
    Path("collaborating-with-claude/scripts/bridge.py"): ROOT / "scripts" / "claude_bridge.py",
    Path("collaborating-with-codex/scripts/bridge.py"): ROOT / "scripts" / "codex_bridge.py",
    Path("collaborating-with-gemini/scripts/bridge.py"): ROOT / "scripts" / "gemini_bridge.py",
}


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    shutil.copy2(source, temporary)
    temporary.replace(target)


def sync_tree(source: Path, target: Path) -> list[str]:
    changes = compare_trees(source, target)
    source_files = relative_files(source)
    target_files = relative_files(target)
    for relative, source_file in source_files.items():
        target_file = target / relative
        if not target_file.exists() or digest(source_file) != digest(target_file):
            copy_file(source_file, target_file)
    for relative in target_files.keys() - source_files.keys():
        (target / relative).unlink()
    for directory in sorted(
        (path for path in target.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        if not any(directory.iterdir()):
            directory.rmdir()
    return changes


def bridge_drift() -> list[str]:
    issues: list[str] = []
    for relative, source in BRIDGES.items():
        bundled = SOURCE / relative
        if not bundled.exists():
            issues.append(f"missing bridge: {relative}")
        elif digest(source) != digest(bundled):
            issues.append(f"changed bridge: {relative}")
    return issues


def refresh_bridges() -> list[str]:
    changes = bridge_drift()
    for relative, source in BRIDGES.items():
        copy_file(source, SOURCE / relative)
    return changes


def check() -> list[str]:
    issues = bridge_drift()
    for target in DISTRIBUTIONS:
        issues.extend(f"{target}: {issue}" for issue in compare_trees(SOURCE, target))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check or generate HelloAGENTS skill distributions.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="Report generated-file drift without writing.")
    action.add_argument("--write", action="store_true", help="Refresh bridges and platform distributions.")
    args = parser.parse_args(argv)

    if args.check:
        issues = check()
        if issues:
            print("skill distribution drift detected:")
            for issue in issues:
                print(f"- {issue}")
            return 1
        print("skill distributions match canonical source")
        return 0

    changes = refresh_bridges()
    for target in DISTRIBUTIONS:
        changes.extend(f"{target}: {item}" for item in sync_tree(SOURCE, target))
    print(f"skill distributions synchronized ({len(changes)} change(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
