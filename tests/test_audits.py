from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from scripts import (
    audit_safety,
    audit_skills,
    claude_bridge,
    codex_bridge,
    gemini_bridge,
    manage_skills,
    sync_skills,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SKILLS = ROOT / "skills" / "helloagents"
CODEX_SKILLS = SOURCE_SKILLS


def write_skill(root: Path, name: str, requires: list[str], body: str = "") -> None:
    skill_dir = root / "skills" / "helloagents" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    requirements = "\n".join(f"  - {dependency}" for dependency in requires) or "[]"
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                f"name: {name}",
                f"description: {name} description",
                "invocation: model",
                "side_effects: read-only",
                "requires:" if requires else f"requires: {requirements}",
                requirements if requires else "",
                "completion_criteria: complete",
                "---",
                "",
                body,
            ]
        ),
        encoding="utf-8",
    )


def qa_payload_v3(tdd: dict[str, object] | None) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 3,
        "qa_mode": "standard",
        "scope": "TDD 证据契约",
        "outcome": "clean",
        "gate_status": "passed",
        "conclusion": "所有验证通过",
        "findings": [],
        "file_references": [],
        "commands": [
            {
                "command": "python -m unittest tests.test_audits",
                "result": "passed",
                "note": "TDD evidence contract verified",
            }
        ],
        "task_verification": [],
    }
    if tdd is not None:
        payload["tdd"] = tdd
    return payload


def complete_tdd_evidence() -> dict[str, object]:
    return {
        "classification": "mandatory",
        "decision": "tdd",
        "target_behaviors": ["拒绝缺失 TDD 证据的 QA 记录"],
        "red": {
            "command": "python -m unittest tests.test_audits",
            "result": "failed",
            "summary": "现有审计器尚未支持 schema v3",
        },
        "green": {
            "command": "python -m unittest tests.test_audits",
            "result": "passed",
            "summary": "新增 TDD 审计规则后通过",
        },
        "refactor": {
            "performed": False,
            "command": "python -m unittest tests.test_audits",
            "result": "passed",
            "summary": "校验逻辑保持最小且测试通过",
        },
        "verify": {
            "command": "python -m unittest discover -s tests -v",
            "result": "passed",
            "summary": "全量回归通过",
        },
    }


class SafetyAuditTests(unittest.TestCase):
    def test_scans_shell_commands_in_markdown_fences(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("```bash\nrm -rf /\n```\n", encoding="utf-8")

            issues = audit_safety.scan_repo(root)

        self.assertTrue(any("递归删除关键路径" in issue for issue in issues), issues)

    def test_scans_constant_python_subprocess_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "bad.py").write_text(
                'import subprocess\nsubprocess.run(["git", "reset", "--hard"])\n',
                encoding="utf-8",
            )

            issues = audit_safety.scan_repo(root)

        self.assertTrue(any("硬重置" in issue for issue in issues), issues)

    def test_plain_documentation_mentions_are_not_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("Never run rm -rf / in production.\n", encoding="utf-8")

            issues = audit_safety.scan_repo(root)

        self.assertEqual([], issues)

    def test_unlabelled_markdown_fence_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("```\nplain text\n```\n", encoding="utf-8")

            issues = audit_safety.scan_repo(root)

        self.assertEqual([], issues)

    def test_scans_tilde_shell_fences(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("~~~bash\nrm -rf /\n~~~\n", encoding="utf-8")

            issues = audit_safety.scan_repo(root)

        self.assertTrue(any("递归删除关键路径" in issue for issue in issues), issues)

    def test_scans_constant_variables_and_imported_subprocess_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "bad.py").write_text(
                "from subprocess import run\ncmd = ['git', 'reset', '--hard']\nrun(cmd)\n",
                encoding="utf-8",
            )

            issues = audit_safety.scan_repo(root)

        self.assertTrue(any("硬重置" in issue for issue in issues), issues)


class SkillStructureAuditTests(unittest.TestCase):
    def test_rejects_duplicate_frontmatter_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "alpha", [])
            skill = root / "skills" / "helloagents" / "alpha" / "SKILL.md"
            text = skill.read_text(encoding="utf-8").replace(
                "description: alpha description",
                "description: first\ndescription: second",
            )
            skill.write_text(text, encoding="utf-8")
            (root / "skills" / "helloagents" / "SKILL_INDEX.md").write_text(
                "| Skill | x |\n|---|---|\n| `alpha` | x |\n",
                encoding="utf-8",
            )

            errors, _ = audit_skills.audit_tree(root)

        self.assertTrue(any("重复字段" in error for error in errors), errors)

    def test_checks_general_markdown_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "alpha", [], "[missing](./missing.md)")
            (root / "skills" / "helloagents" / "SKILL_INDEX.md").write_text(
                "| Skill | x |\n|---|---|\n| `alpha` | x |\n",
                encoding="utf-8",
            )

            errors, _ = audit_skills.audit_tree(root)

        self.assertTrue(any("Markdown 链接不存在" in error for error in errors), errors)

    def test_rejects_requires_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "alpha", ["beta"])
            write_skill(root, "beta", ["alpha"])
            (root / "skills" / "helloagents" / "SKILL_INDEX.md").write_text(
                "| Skill | x |\n|---|---|\n| `alpha` | x |\n| `beta` | x |\n",
                encoding="utf-8",
            )

            errors, _ = audit_skills.audit_tree(root)

        self.assertTrue(any("依赖环" in error for error in errors), errors)

    def test_rejects_non_string_frontmatter_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "alpha", [])
            skill = root / "skills" / "helloagents" / "alpha" / "SKILL.md"
            text = skill.read_text(encoding="utf-8").replace(
                "description: alpha description",
                "description:\n  - invalid",
            )
            skill.write_text(text, encoding="utf-8")
            (root / "skills" / "helloagents" / "SKILL_INDEX.md").write_text(
                "| Skill | x |\n|---|---|\n| `alpha` | x |\n",
                encoding="utf-8",
            )

            errors, _ = audit_skills.audit_tree(root)

        self.assertTrue(any("description` 必须是字符串" in error for error in errors), errors)

    def test_rejects_invalid_qa_json_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "qa-review.json"
            path.write_text(
                '{"schema_version":"x","qa_mode":"invalid","scope":1,'
                '"outcome":"clean","gate_status":"passed","conclusion":"x",'
                '"findings":"none","file_references":[],"commands":{},"task_verification":[]}',
                encoding="utf-8",
            )

            errors = audit_skills.qa_json_errors(path)

        self.assertTrue(errors)

    def test_accepts_schema_v3_tdd_and_exempt_evidence(self) -> None:
        exemption = {
            "classification": "exempt",
            "decision": "exempt",
            "target_behaviors": ["为已实现行为补充表征测试"],
            "exempt_reason": "生产实现早于本次测试，无法构造真实 RED 阶段",
            "alternative_verification": "运行新增表征测试并记录结果",
        }
        with tempfile.TemporaryDirectory() as temporary:
            for index, evidence in enumerate([complete_tdd_evidence(), exemption]):
                path = Path(temporary) / f"qa-review-{index}.json"
                path.write_text(
                    json.dumps(qa_payload_v3(evidence), ensure_ascii=False),
                    encoding="utf-8",
                )

                self.assertEqual([], audit_skills.qa_json_errors(path))

    def test_rejects_missing_or_invalid_schema_v3_tdd_evidence(self) -> None:
        invalid_red = complete_tdd_evidence()
        invalid_red["red"] = {
            "command": "python -m unittest tests.test_audits",
            "result": "passed",
            "summary": "RED 不应提前通过",
        }
        cases = [
            (qa_payload_v3(None), "tdd"),
            (qa_payload_v3(invalid_red), "tdd.red.result"),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            for index, (payload, expected) in enumerate(cases):
                path = Path(temporary) / f"qa-review-{index}.json"
                path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

                errors = audit_skills.qa_json_errors(path)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_registers_test_command_and_skill(self) -> None:
        test_skill = CODEX_SKILLS / "test" / "SKILL.md"

        self.assertIn("~test", audit_skills.COMMAND_ALIASES)
        self.assertTrue(test_skill.exists())
        self.assertIn("Trigger: ~test [scope]", test_skill.read_text(encoding="utf-8"))

    def test_current_knowledge_base_contracts_are_valid(self) -> None:
        self.assertEqual([], audit_skills.audit_knowledge_bases())

    def test_current_semantic_contracts_are_valid(self) -> None:
        self.assertEqual([], audit_skills.audit_semantic_contracts())

    def test_discovers_nested_branch_knowledge_base(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary) / "helloagents"
            kb = base / "codex" / "feature"
            wiki = kb / "wiki"
            history = kb / "history"
            wiki.mkdir(parents=True)
            history.mkdir()
            (kb / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
            (kb / "project.md").write_text("# Project\n", encoding="utf-8")
            for name in ["overview.md", "arch.md", "api.md", "data.md", "glossary.md"]:
                (wiki / name).write_text(f"# {name}\n", encoding="utf-8")
            (history / "index.md").write_text("# History\n", encoding="utf-8")

            errors = audit_skills.audit_knowledge_bases(base)

        self.assertEqual([], errors)


class RuntimeContractTests(unittest.TestCase):
    def test_terminal_paths_reset_workflow_state(self) -> None:
        lifecycle = (CODEX_SKILLS / "lifecycle" / "SKILL.md").read_text(encoding="utf-8")
        transition = (
            CODEX_SKILLS / "develop" / "references" / "phase-transition.md"
        ).read_text(encoding="utf-8")

        self.assertIn("RESET_WORKFLOW_STATE", lifecycle)
        self.assertIn("RESET_WORKFLOW_STATE", transition)

    def test_lightweight_package_has_downstream_metadata_contract(self) -> None:
        qa = (CODEX_SKILLS / "qa-review" / "SKILL.md").read_text(encoding="utf-8")
        kb = (
            CODEX_SKILLS / "kb" / "references" / "knowledge-base-rules.md"
        ).read_text(encoding="utf-8")

        self.assertIn("轻量方案包元数据", qa)
        self.assertIn("轻量方案包元数据", kb)

    def test_history_migration_never_forces_overwrite(self) -> None:
        lifecycle = (CODEX_SKILLS / "lifecycle" / "SKILL.md").read_text(encoding="utf-8")
        entry = (
            CODEX_SKILLS / "develop" / "references" / "entry-and-steps.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn("同名覆盖", lifecycle)
        self.assertNotIn("强制覆盖", entry)
        self.assertIn("no-clobber", lifecycle)

    def test_qa_findings_have_an_executable_gate(self) -> None:
        qa = (CODEX_SKILLS / "qa-review" / "SKILL.md").read_text(encoding="utf-8")
        entry = (
            CODEX_SKILLS / "develop" / "references" / "entry-and-steps.md"
        ).read_text(encoding="utf-8")

        self.assertIn('"gate_status": "passed"', qa)
        self.assertIn("P0 阻止归档", entry)
        self.assertIn("P1 默认阻止归档", entry)

    def test_all_wait_states_have_consumers(self) -> None:
        context = (
            CODEX_SKILLS / "routing" / "references" / "commands-and-context.md"
        ).read_text(encoding="utf-8")
        entry = (
            CODEX_SKILLS / "develop" / "references" / "entry-and-steps.md"
        ).read_text(encoding="utf-8")

        self.assertIn("TEST_FAILURE_DECISION` 消费序号", context)
        self.assertIn("MM_ACCEPTANCE` 消费序号", context)
        self.assertIn("归档前多模型验收询问格式", entry)

    def test_archive_path_is_resolved_before_kb_links(self) -> None:
        lifecycle = (CODEX_SKILLS / "lifecycle" / "SKILL.md").read_text(encoding="utf-8")
        kb = (
            CODEX_SKILLS / "kb" / "references" / "knowledge-base-rules.md"
        ).read_text(encoding="utf-8")

        self.assertIn("RESOLVED_ARCHIVE_PATH", lifecycle)
        self.assertIn("RESOLVED_ARCHIVE_PATH", kb)
        self.assertIn("task.md#轻量方案包元数据", kb)

    def test_exec_and_subagents_accept_lightweight_packages(self) -> None:
        context = (
            CODEX_SKILLS / "routing" / "references" / "commands-and-context.md"
        ).read_text(encoding="utf-8")
        delegation = (
            CODEX_SKILLS / "hello-subagent" / "references" / "delegation-protocol.md"
        ).read_text(encoding="utf-8")

        self.assertIn("合法完整或轻量方案包", context)
        self.assertIn("轻量方案包", delegation)

    def test_gemini_bridge_defaults_to_sandbox(self) -> None:
        source = (ROOT / "scripts" / "gemini_bridge.py").read_text(encoding="utf-8")
        self.assertIn("default=True", source)

    def test_bundled_bridges_match_runtime_sources(self) -> None:
        self.assertEqual([], audit_skills.audit_bundled_bridges())

    def test_multiline_prompt_is_not_rewritten_on_windows(self) -> None:
        self.assertNotIn("windows_escape", (ROOT / "scripts" / "gemini_bridge.py").read_text(encoding="utf-8"))

    def test_bridge_timeout_terminates_process(self) -> None:
        output = list(
            codex_bridge.run_shell_command(
                [sys.executable, "-c", "import time; time.sleep(2)"],
                timeout=1,
            )
        )
        self.assertIn("__HELLOAGENTS_TIMEOUT__", output)

    def test_bridge_timeout_cannot_be_bypassed_by_continuous_output(self) -> None:
        start = time.monotonic()
        output = list(
            codex_bridge.run_shell_command(
                [
                    sys.executable,
                    "-u",
                    "-c",
                    "import time\nfor i in range(1000): print(i); time.sleep(.005)",
                ],
                timeout=0.05,
            )
        )

        self.assertLess(time.monotonic() - start, 1.0)
        self.assertIn("__HELLOAGENTS_TIMEOUT__", output)

    def test_bridge_timeout_terminates_child_process_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "child-survived.txt"
            child = (
                "import time; from pathlib import Path; time.sleep(.4); "
                f"Path({str(marker)!r}).write_text('survived', encoding='utf-8')"
            )
            parent = (
                "import subprocess,sys,time; "
                f"subprocess.Popen([sys.executable, '-c', {child!r}]); time.sleep(5)"
            )

            output = list(
                codex_bridge.run_shell_command([sys.executable, "-c", parent], timeout=0.05)
            )
            time.sleep(0.6)

            self.assertIn("__HELLOAGENTS_TIMEOUT__", output)
            self.assertFalse(marker.exists())

    def test_bridge_timeout_terminates_tree_after_parent_exits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "orphan-survived.txt"
            child = (
                "import time; from pathlib import Path; time.sleep(.4); "
                f"Path({str(marker)!r}).write_text('survived', encoding='utf-8')"
            )
            parent = (
                "import subprocess,sys; "
                f"subprocess.Popen([sys.executable, '-c', {child!r}])"
            )

            output = list(
                codex_bridge.run_shell_command([sys.executable, "-c", parent], timeout=0.05)
            )
            time.sleep(0.6)

            self.assertIn("__HELLOAGENTS_TIMEOUT__", output)
            self.assertFalse(marker.exists())

    def test_bridge_reports_nonzero_exit(self) -> None:
        output = list(
            codex_bridge.run_shell_command(
                [sys.executable, "-c", "print('partial'); raise SystemExit(3)"],
                timeout=5,
            )
        )
        self.assertIn("__HELLOAGENTS_EXIT_CODE__=3", output)

    def test_review_commands_use_real_read_only_modes(self) -> None:
        claude_cmd = ["claude"]
        claude_bridge._apply_permission_mode(claude_cmd, "read-only", False)
        self.assertIn("--permission-mode", claude_cmd)
        self.assertIn("plan", claude_cmd)
        self.assertIn("--safe-mode", claude_cmd)

        gemini_cmd = gemini_bridge.build_command(
            SimpleNamespace(PROMPT="review", sandbox=True, model="", SESSION_ID="")
        )
        self.assertIn("--approval-mode", gemini_cmd)
        self.assertIn("plan", gemini_cmd)

    def test_codex_command_uses_supported_dangerous_flag_and_repeated_images(self) -> None:
        command = codex_bridge.build_command(
            SimpleNamespace(
                sandbox="read-only",
                cd=".",
                image=["a.png", "b.png"],
                model="",
                profile="",
                yolo=True,
                skip_git_repo_check=True,
                SESSION_ID="",
                PROMPT="review",
            )
        )
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", command)
        self.assertNotIn("--yolo", command)
        self.assertEqual(2, command.count("--image"))

    def test_malformed_events_cannot_succeed_after_partial_output(self) -> None:
        cases = [
            (
                claude_bridge,
                [
                    '{"session_id":"s","type":"assistant","message":{"content":[{"type":"text","text":"partial"}]}}',
                    '{"type":"assistant","message":"invalid"}',
                ],
            ),
            (
                gemini_bridge,
                [
                    '{"session_id":"s","type":"message","role":"assistant","content":"partial"}',
                    '{"type":"message","role":"assistant","content":null}',
                ],
            ),
        ]
        for module, events in cases:
            with self.subTest(module=module.__name__):
                output = io.StringIO()
                argv = ["bridge", "--PROMPT", "review", "--cd", "."]
                with (
                    mock.patch.object(sys, "argv", argv),
                    mock.patch.object(module, "run_shell_command", return_value=iter(events)),
                    contextlib.redirect_stdout(output),
                ):
                    module.main()
                self.assertFalse(json.loads(output.getvalue())["success"])

    def test_bridge_preserves_multiline_argument(self) -> None:
        value = "line1\nline2\tvalue"
        output = list(
            codex_bridge.run_shell_command(
                [sys.executable, "-c", "import sys; print(repr(sys.argv[1]))", value],
                timeout=5,
            )
        )
        self.assertEqual([repr(value)], output)


class SkillInstallationTests(unittest.TestCase):
    def test_generated_distributions_match_canonical_source(self) -> None:
        self.assertEqual([], sync_skills.check())
        self.assertTrue(
            all(source == SOURCE_SKILLS for source, _ in manage_skills.PLATFORMS.values())
        )

    def test_compare_trees_reports_and_clears_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()
            (source / "SKILL.md").write_text("new", encoding="utf-8")
            (target / "SKILL.md").write_text("old", encoding="utf-8")

            self.assertEqual(["changed: SKILL.md"], manage_skills.compare_trees(source, target))
            backup = manage_skills.atomic_install(source, target)

            self.assertIsNotNone(backup)
            self.assertEqual("old", (backup / "SKILL.md").read_text(encoding="utf-8"))
            self.assertEqual([], manage_skills.compare_trees(source, target))

    def test_gemini_parser_help_exposes_safe_defaults(self) -> None:
        source = (ROOT / "scripts" / "gemini_bridge.py").read_text(encoding="utf-8")
        self.assertIn("BooleanOptionalAction", source)
        self.assertIn('default=600', source)

    def test_bootstrap_target_is_platform_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            invalid = root / "arbitrary.txt"
            with self.assertRaises(ValueError):
                manage_skills.validate_bootstrap_target("codex", invalid)

    def test_install_rolls_back_skill_tree_when_bootstrap_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            target = root / "installed" / "helloagents"
            source.mkdir()
            target.mkdir(parents=True)
            (source / "SKILL.md").write_text("new", encoding="utf-8")
            (target / "SKILL.md").write_text("old", encoding="utf-8")

            with mock.patch.object(manage_skills, "install_bootstrap", side_effect=OSError("boom")):
                with self.assertRaises(OSError):
                    manage_skills.install_transaction(
                        source,
                        target,
                        ROOT / "Codex" / "Skills" / "CN" / "AGENTS.md",
                        root / "AGENTS.md",
                    )

            self.assertEqual("old", (target / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
