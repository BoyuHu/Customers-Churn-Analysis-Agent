"""Tour 05 — Golden-dataset evaluation (the quality gate).

Goal: understand how `python -m scripts.run_evaluation` computes its metrics,
case by case, and how the gate thresholds are applied.

Requires bootstrap (golden dataset + trained model).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio

import pytest
from helpers import BOOTSTRAP_HINT, get_bootstrapped

from pipelines.evaluation.run_agent_eval import evaluate_agent, load_golden_cases


def test_single_golden_case() -> None:
    res = get_bootstrapped()
    if res is None:
        pytest.skip(BOOTSTRAP_HINT)
        return
    container, _ = res
    cases = load_golden_cases(container.settings.golden_dataset_path)
    case = cases[0]
    print(f"\n=== Golden case #{case['customer_id']} ===")
    print(f"  expected_risk_band       = {case['expected_risk_band']}")
    print(f"  required_action_keywords = {case['required_action_keywords']}")
    print(f"  expected_human_approval  = {case['expected_human_approval']}")

    result = asyncio.run(
        container.workflow.analyze(
            case["customer_id"], session_id="tour-eval",
            create_ticket=False, persist=False,
        )
    )
    action_text = " ".join(a.action.lower() for a in result.recommendation.actions)
    keyword_hits = [k for k in case["required_action_keywords"] if k.lower() in action_text]
    print("\n  Computed per-case metrics:")
    print(f"    risk_band_correct     = {result.prediction.risk_band == case['expected_risk_band']}")
    print(f"    keyword_coverage      = {len(keyword_hits)}/{len(case['required_action_keywords'])}")
    print(f"    review_passed         = {result.review.passed}")
    print(f"    has_evidence(>=2)     = {len(result.recommendation.evidence) >= 2}")
    print(f"    approval_alignment    = "
          f"{result.recommendation.requires_human_approval == case['expected_human_approval']}")


def test_full_evaluation_report() -> None:
    res = get_bootstrapped()
    if res is None:
        pytest.skip(BOOTSTRAP_HINT)
        return
    container, _ = res
    report = asyncio.run(
        evaluate_agent(
            container.workflow,
            container.settings.golden_dataset_path,
            container.settings.database_path.parent / "evaluations" / "agent_eval.json",
        )
    )
    print("\n=== Full evaluation metrics ===")
    for k, v in report["metrics"].items():
        print(f"  {k:28} = {v}")
    print("\n  Quality gate thresholds (scripts/run_evaluation.py):")
    print("    risk_band_accuracy >= 0.95 | mean_keyword_coverage >= 0.65")
    print("    review_pass_rate   >= 0.95 | evidence_rate        >= 1.0")


if __name__ == "__main__":
    res = get_bootstrapped()
    if res is None:
        raise SystemExit(BOOTSTRAP_HINT)
    test_single_golden_case()
    test_full_evaluation_report()
