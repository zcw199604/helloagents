from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import eval_skills, manage_skills


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals" / "skill_routing_cases.json"
CODEX_BOOTSTRAP = ROOT / "Codex" / "Skills" / "CN" / "AGENTS.md"
CLAUDE_BOOTSTRAP = ROOT / "Claude" / "Skills" / "CN" / "CLAUDE.md"
HELLOAGENTS_SKILLS = ROOT / "skills" / "helloagents"
ROUTING_ROOT = HELLOAGENTS_SKILLS / "routing"
DEVELOP_ENTRY = HELLOAGENTS_SKILLS / "develop" / "references" / "entry-and-steps.md"
ANALYZE_TRANSITION = (
    HELLOAGENTS_SKILLS / "analyze" / "references" / "code-analysis-and-output.md"
)
DESIGN_TRANSITION = (
    HELLOAGENTS_SKILLS / "design" / "references" / "output-and-transition.md"
)
TDD_SKILL = HELLOAGENTS_SKILLS / "tdd" / "SKILL.md"
DESIGN_PLANNING = (
    HELLOAGENTS_SKILLS / "design" / "references" / "detailed-planning.md"
)
QA_REVIEW = HELLOAGENTS_SKILLS / "qa-review" / "SKILL.md"
LIFECYCLE = HELLOAGENTS_SKILLS / "lifecycle" / "SKILL.md"


class SkillEvalDatasetTests(unittest.TestCase):
    def load_cases(self) -> list[dict[str, object]]:
        return json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]

    def test_eval_corpus_is_valid_and_representative(self) -> None:
        cases = self.load_cases()

        self.assertEqual([], eval_skills.validate_cases(cases))
        self.assertGreaterEqual(len(cases), 36)
        categories = {case["category"] for case in cases}
        self.assertTrue(eval_skills.REQUIRED_CATEGORIES <= categories)

    def test_duplicate_case_ids_are_rejected(self) -> None:
        case = {
            "id": "duplicate",
            "category": "consultation",
            "prompt": "解释这段代码",
            "expected": {
                "route": "consultation",
                "action": "answer",
                "confirmation": "none",
                "artifacts": "none",
                "risk": "low",
            },
        }

        errors = eval_skills.validate_cases([case, case])

        self.assertTrue(any("重复" in error for error in errors), errors)

    def test_case_document_requires_supported_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "cases.json"
            path.write_text(
                json.dumps({"schema_version": 2, "cases": []}), encoding="utf-8"
            )

            _, errors = eval_skills.read_collection(path, "cases")

        self.assertTrue(any("schema_version" in error for error in errors), errors)

    def test_results_scoring_reports_routing_and_confirmation_metrics(self) -> None:
        cases = [
            {
                "id": "low-risk-fix",
                "category": "ordinary_bug",
                "prompt": "修复本地解析错误",
                "expected": {
                    "route": "systematic_debugging",
                    "action": "diagnose_and_implement",
                    "confirmation": "none",
                    "artifacts": "none",
                    "risk": "low",
                },
            },
            {
                "id": "production-change",
                "category": "high_risk",
                "prompt": "修改生产数据库",
                "expected": {
                    "route": "full_research",
                    "action": "plan_and_confirm",
                    "confirmation": "before_write",
                    "artifacts": "full",
                    "risk": "high",
                },
            },
        ]
        results = [
            {"id": "low-risk-fix", **cases[0]["expected"]},
            {
                "id": "production-change",
                **cases[1]["expected"],
                "confirmation": "none",
            },
        ]

        metrics, errors = eval_skills.score_results(cases, results)

        self.assertEqual([], errors)
        self.assertEqual(1.0, metrics["route_accuracy"])
        self.assertEqual(0.5, metrics["confirmation_accuracy"])
        self.assertEqual(0.0, metrics["unnecessary_confirmation_rate"])
        self.assertEqual(0.5, metrics["missed_required_confirmation_rate"])

    def test_cli_rejects_invalid_result_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result_path = Path(temporary) / "results.json"
            result_path.write_text('{"results": []}', encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                exit_code = eval_skills.main(
                    ["--cases", str(CASES_PATH), "--results", str(result_path)]
                )

        self.assertEqual(1, exit_code)


class AdaptiveRoutingContractTests(unittest.TestCase):
    def test_canonical_skill_tree_is_the_only_authored_source(self) -> None:
        self.assertTrue((HELLOAGENTS_SKILLS / "SKILL_INDEX.md").exists())
        for platform_root in [
            ROOT / "Codex" / "Skills" / "CN" / "skills" / "helloagents",
            ROOT / "Claude" / "Skills" / "CN" / "skills" / "helloagents",
        ]:
            self.assertEqual(
                [],
                manage_skills.compare_trees(HELLOAGENTS_SKILLS, platform_root),
            )

    def test_bootstrap_is_small_and_platform_mirrored(self) -> None:
        codex = CODEX_BOOTSTRAP.read_text(encoding="utf-8")
        claude = CLAUDE_BOOTSTRAP.read_text(encoding="utf-8")

        self.assertEqual(codex, claude)
        self.assertLessEqual(len(codex.splitlines()), 120)
        self.assertIn("skills/helloagents/SKILL_INDEX.md", codex)
        self.assertNotIn("PENDING_INTERACTION", codex)
        self.assertNotIn("WORKFLOW_ID", codex)
        self.assertNotIn("<thinking>", codex)

    def test_routing_uses_risk_instead_of_file_count_as_primary_signal(self) -> None:
        decision = (ROUTING_ROOT / "references" / "routing-decision.md").read_text(
            encoding="utf-8"
        )
        paths = (ROUTING_ROOT / "references" / "routing-paths.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("风险等级: 低 | 中 | 高", decision)
        self.assertIn("可逆性", decision)
        self.assertNotIn("文件3-5", paths)
        self.assertNotIn("文件≤2", paths)
        self.assertNotIn("文件>5", paths)
        self.assertIn("不引入 Light/Heavy 持久模式变量", paths)

    def test_lightweight_output_and_knowledge_writes_are_the_default(self) -> None:
        output = (HELLOAGENTS_SKILLS / "output-format" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        qa_output = (
            HELLOAGENTS_SKILLS / "output-format" / "references" / "qa-output.md"
        ).read_text(encoding="utf-8")
        kb = (
            HELLOAGENTS_SKILLS / "kb" / "references" / "knowledge-base-rules.md"
        ).read_text(encoding="utf-8")

        self.assertIn("普通咨询与简短确认不使用阶段包装", output)
        self.assertIn("直接回答", qa_output)
        self.assertNotIn("MUST使用 `💡【HelloAGENTS】", qa_output)
        self.assertIn("写入收益门禁", kb)
        self.assertIn("默认不写", kb)

    def test_ordinary_bug_and_small_change_can_continue_without_second_confirmation(self) -> None:
        paths = (ROUTING_ROOT / "references" / "routing-paths.md").read_text(
            encoding="utf-8"
        )
        entry = DEVELOP_ENTRY.read_text(encoding="utf-8")

        self.assertIn("普通缺陷直接实施", paths)
        self.assertIn("低风险小改动直接实施", paths)
        self.assertIn("条件E - 用户明确授权的自适应开发", entry)
        self.assertIn("EHRB=无", entry)
        self.assertIn("风险等级=高", paths)

    def test_adaptive_analysis_and_design_do_not_repeat_confirmation(self) -> None:
        analyze = ANALYZE_TRANSITION.read_text(encoding="utf-8")
        design = DESIGN_TRANSITION.read_text(encoding="utf-8")

        self.assertIn("不设置 `DESIGN_CONFIRM`", analyze)
        self.assertIn("不设置 `DEVELOPMENT_CONFIRM`", design)

    def test_engineering_scope_and_context_recovery_are_risk_proportional(self) -> None:
        bootstrap = CODEX_BOOTSTRAP.read_text(encoding="utf-8")
        tdd = TDD_SKILL.read_text(encoding="utf-8")
        design = DESIGN_PLANNING.read_text(encoding="utf-8")
        develop = DEVELOP_ENTRY.read_text(encoding="utf-8")
        qa = QA_REVIEW.read_text(encoding="utf-8")
        lifecycle = LIFECYCLE.read_text(encoding="utf-8")

        self.assertIn("最小充分设计与验证", bootstrap)
        self.assertIn("上下文恢复与复核边界", bootstrap)
        self.assertIn("风险驱动的最小充分覆盖", tdd)
        self.assertIn("不要求机械穷举每类场景", tdd)
        self.assertIn("验证规模适配", design)
        self.assertIn("步骤5.4: 最小充分实现约束", develop)
        self.assertIn("未被本轮触达且已有有效验证证据", qa)
        self.assertIn("上下文压缩与恢复规则", lifecycle)
        self.assertIn("不得自动重放", lifecycle)


if __name__ == "__main__":
    unittest.main()
