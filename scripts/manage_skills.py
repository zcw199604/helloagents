#!/usr/bin/env python3
"""Check or atomically install a HelloAGENTS platform skill tree."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_SOURCE = ROOT / "skills" / "helloagents"
PLATFORMS = {
    "codex": (SKILL_SOURCE, ROOT / "Codex" / "Skills" / "CN" / "AGENTS.md"),
    "claude": (SKILL_SOURCE, ROOT / "Claude" / "Skills" / "CN" / "CLAUDE.md"),
}
BOOTSTRAP_NAMES = {"codex": "AGENTS.md", "claude": "CLAUDE.md"}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def relative_files(root: Path) -> dict[Path, Path]:
    if not root.exists():
        return {}
    return {path.relative_to(root): path for path in root.rglob("*") if path.is_file()}


def compare_trees(source: Path, target: Path) -> list[str]:
    source_files = relative_files(source)
    target_files = relative_files(target)
    issues: list[str] = []
    for relative in sorted(source_files.keys() - target_files.keys()):
        issues.append(f"missing: {relative}")
    for relative in sorted(target_files.keys() - source_files.keys()):
        issues.append(f"extra: {relative}")
    for relative in sorted(source_files.keys() & target_files.keys()):
        if digest(source_files[relative]) != digest(target_files[relative]):
            issues.append(f"changed: {relative}")
    return issues


def atomic_install(source: Path, target: Path) -> Path | None:
    target.parent.mkdir(parents=True, exist_ok=True)
    staging_parent = Path(tempfile.mkdtemp(prefix="helloagents-install-", dir=target.parent))
    staged = staging_parent / target.name
    backup: Path | None = None
    try:
        shutil.copytree(source, staged)
        if target.exists():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup = target.with_name(f"{target.name}.backup.{timestamp}")
            suffix = 2
            while backup.exists():
                backup = target.with_name(f"{target.name}.backup.{timestamp}.v{suffix}")
                suffix += 1
            target.rename(backup)
        staged.rename(target)
    except Exception:
        if not target.exists() and backup and backup.exists():
            backup.rename(target)
        raise
    finally:
        shutil.rmtree(staging_parent, ignore_errors=True)
    return backup


def install_bootstrap(source: Path, target: Path) -> Path | None:
    target.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    if target.exists():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup = target.with_name(f"{target.name}.backup.{timestamp}")
        suffix = 2
        while backup.exists():
            backup = target.with_name(f"{target.name}.backup.{timestamp}.v{suffix}")
            suffix += 1
        shutil.copy2(target, backup)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    os.close(descriptor)
    Path(temporary_name).unlink()
    temporary = Path(temporary_name)
    shutil.copy2(source, temporary)
    temporary.replace(target)
    return backup


def validate_bootstrap_target(platform: str, target: Path) -> Path:
    resolved = target.expanduser().resolve()
    if resolved.name != BOOTSTRAP_NAMES[platform]:
        raise ValueError(f"bootstrap target for {platform} must be named {BOOTSTRAP_NAMES[platform]}")
    if (
        resolved == Path(resolved.anchor)
        or resolved.parent == Path(resolved.anchor)
        or ROOT in resolved.parents
        or resolved == ROOT
        or (resolved.exists() and resolved.is_dir())
    ):
        raise ValueError("bootstrap target must be a non-root file outside this repository")
    source = PLATFORMS[platform][1].resolve()
    if resolved == source:
        raise ValueError("bootstrap target must not be the repository source file")
    return resolved


def _restore_skill_install(target: Path, backup: Path | None) -> None:
    if target.exists():
        shutil.rmtree(target)
    if backup is not None and backup.exists():
        backup.rename(target)


def install_transaction(
    source: Path,
    target: Path,
    bootstrap_source: Path | None = None,
    bootstrap_target: Path | None = None,
) -> tuple[Path | None, Path | None]:
    skill_backup = atomic_install(source, target)
    bootstrap_backup: Path | None = None
    try:
        if bootstrap_source is not None and bootstrap_target is not None:
            bootstrap_backup = install_bootstrap(bootstrap_source, bootstrap_target)
    except Exception:
        _restore_skill_install(target, skill_backup)
        raise
    return skill_backup, bootstrap_backup


def main() -> int:
    parser = argparse.ArgumentParser(description="Check or install HelloAGENTS skills.")
    parser.add_argument("--platform", required=True, choices=sorted(PLATFORMS))
    parser.add_argument("--target", required=True, type=Path, help="Installed helloagents skill directory.")
    parser.add_argument("--bootstrap-target", type=Path, help="Optional AGENTS.md or CLAUDE.md destination.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="Compare source and installed files without writing.")
    action.add_argument("--install", action="store_true", help="Atomically install after backing up the existing target.")
    args = parser.parse_args()

    source, bootstrap = PLATFORMS[args.platform]
    target = args.target.expanduser().resolve()
    if target.name != "helloagents" or target == Path(target.anchor) or target.parent == Path(target.anchor):
        parser.error("--target must name a non-root 'helloagents' directory")
    if target == source.resolve() or ROOT in target.parents:
        parser.error("--target must be an installed directory outside this repository")
    bootstrap_target = None
    if args.bootstrap_target:
        try:
            bootstrap_target = validate_bootstrap_target(args.platform, args.bootstrap_target)
        except ValueError as error:
            parser.error(str(error))
    if args.check:
        issues = compare_trees(source, target)
        if bootstrap_target:
            if not bootstrap_target.exists():
                issues.append(f"missing bootstrap: {bootstrap_target}")
            elif digest(bootstrap) != digest(bootstrap_target):
                issues.append(f"changed bootstrap: {bootstrap_target}")
        if issues:
            print("installed skill drift detected:")
            for issue in issues:
                print(f"- {issue}")
            return 1
        print("installed skills match repository")
        return 0

    backup, bootstrap_backup = install_transaction(
        source,
        target,
        bootstrap if bootstrap_target else None,
        bootstrap_target,
    )
    print(f"installed: {target}")
    if backup:
        print(f"backup: {backup}")
    if bootstrap_backup:
        print(f"bootstrap backup: {bootstrap_backup}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
