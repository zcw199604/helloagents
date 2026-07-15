#!/usr/bin/env python3
"""校验 Skill 路由 eval 数据，并对结构化实际结果计算回归指标。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "skill_routing_cases.json"

REQUIRED_CATEGORIES = {
    "consultation",
    "micro_adjustment",
    "ordinary_bug",
    "small_change",
    "medium_change",
    "high_risk",
    "command",
    "context",
}
EXPECTED_FIELDS = {"route", "action", "confirmation", "artifacts", "risk"}
ALLOWED_VALUES = {
    "route": {
        "consultation",
        "micro_adjustment",
        "lightweight_iteration",
        "standard_development",
        "full_research",
        "systematic_debugging",
        "command",
        "context_response",
    },
    "action": {
        "answer",
        "implement",
        "diagnose_and_implement",
        "plan_then_implement",
        "plan_and_confirm",
        "confirm_command",
        "clarify",
        "continue_context",
    },
    "confirmation": {"none", "before_write", "command", "clarify"},
    "artifacts": {"none", "minimal", "full"},
    "risk": {"low", "medium", "high"},
}


def read_collection(path: Path, key: str) -> tuple[list[dict[str, object]], list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return [], [f"{path}: 无法读取 JSON: {error}"]
    if not isinstance(payload, dict):
        return [], [f"{path}: 根节点必须是对象"]
    if key == "cases" and payload.get("schema_version") != 1:
        return [], [f"{path}: schema_version 必须是整数 1"]
    collection = payload.get(key)
    if not isinstance(collection, list):
        return [], [f"{path}: `{key}` 必须是列表"]
    if not all(isinstance(item, dict) for item in collection):
        return [], [f"{path}: `{key}` 必须只包含对象"]
    return collection, []


def validate_cases(cases: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{prefix}.id 必须是非空字符串")
        elif case_id in seen:
            errors.append(f"{prefix}.id 重复: `{case_id}`")
        else:
            seen.add(case_id)

        category = case.get("category")
        if category not in REQUIRED_CATEGORIES:
            errors.append(f"{prefix}.category 无效: `{category}`")
        prompt = case.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{prefix}.prompt 必须是非空字符串")

        expected = case.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{prefix}.expected 必须是对象")
            continue
        missing = EXPECTED_FIELDS - set(expected)
        extra = set(expected) - EXPECTED_FIELDS
        if missing:
            errors.append(f"{prefix}.expected 缺少: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"{prefix}.expected 包含未知字段: {', '.join(sorted(extra))}")
        for field, allowed in ALLOWED_VALUES.items():
            if field in expected and expected[field] not in allowed:
                errors.append(
                    f"{prefix}.expected.{field} 无效: `{expected[field]}`"
                )
    return errors


def validate_corpus(cases: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    if len(cases) < 36:
        errors.append(f"eval 用例至少需要 36 条，当前 {len(cases)} 条")
    categories = {case.get("category") for case in cases}
    missing = REQUIRED_CATEGORIES - categories
    if missing:
        errors.append(f"eval 类别覆盖不足: {', '.join(sorted(missing))}")
    return errors


def validate_results(
    cases: list[dict[str, object]], results: list[dict[str, object]]
) -> list[str]:
    errors: list[str] = []
    case_ids = {str(case["id"]) for case in cases}
    seen: set[str] = set()
    for index, result in enumerate(results):
        prefix = f"results[{index}]"
        result_id = result.get("id")
        if not isinstance(result_id, str) or not result_id.strip():
            errors.append(f"{prefix}.id 必须是非空字符串")
            continue
        if result_id in seen:
            errors.append(f"{prefix}.id 重复: `{result_id}`")
        seen.add(result_id)
        if result_id not in case_ids:
            errors.append(f"{prefix}.id 未知: `{result_id}`")
        for field, allowed in ALLOWED_VALUES.items():
            if result.get(field) not in allowed:
                errors.append(f"{prefix}.{field} 无效: `{result.get(field)}`")
    missing = case_ids - seen
    if missing:
        errors.append(f"results 缺少用例: {', '.join(sorted(missing))}")
    return errors


def score_results(
    cases: list[dict[str, object]], results: list[dict[str, object]]
) -> tuple[dict[str, float | int], list[str]]:
    errors = validate_results(cases, results)
    if errors:
        return {}, errors

    result_by_id = {str(result["id"]): result for result in results}
    matched = {field: 0 for field in EXPECTED_FIELDS}
    exact = 0
    unnecessary_confirmation = 0
    missed_required_confirmation = 0

    for case in cases:
        expected = case["expected"]
        assert isinstance(expected, dict)
        actual = result_by_id[str(case["id"])]
        for field in EXPECTED_FIELDS:
            if actual[field] == expected[field]:
                matched[field] += 1
        if all(actual[field] == expected[field] for field in EXPECTED_FIELDS):
            exact += 1
        if expected["confirmation"] == "none" and actual["confirmation"] != "none":
            unnecessary_confirmation += 1
        if expected["confirmation"] != "none" and actual["confirmation"] == "none":
            missed_required_confirmation += 1

    total = len(cases)
    metrics: dict[str, float | int] = {
        "case_count": total,
        "exact_match_rate": exact / total,
        "route_accuracy": matched["route"] / total,
        "action_accuracy": matched["action"] / total,
        "confirmation_accuracy": matched["confirmation"] / total,
        "artifact_accuracy": matched["artifacts"] / total,
        "risk_accuracy": matched["risk"] / total,
        "unnecessary_confirmation_rate": unnecessary_confirmation / total,
        "missed_required_confirmation_rate": missed_required_confirmation / total,
    }
    return metrics, []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="校验 HelloAGENTS 路由 eval 用例并对实际结果评分。"
    )
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument(
        "--results",
        type=Path,
        help="可选的实际结果 JSON，根节点包含 `results` 列表。",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cases, errors = read_collection(args.cases, "cases")
    errors.extend(validate_cases(cases))
    errors.extend(validate_corpus(cases))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if args.results is None:
        categories = sorted({str(case["category"]) for case in cases})
        print(
            json.dumps(
                {"case_count": len(cases), "categories": categories, "status": "valid"},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    results, result_errors = read_collection(args.results, "results")
    if not result_errors:
        metrics, result_errors = score_results(cases, results)
    else:
        metrics = {}
    if result_errors:
        for error in result_errors:
            print(f"ERROR: {error}")
        return 1
    print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
