"""Tour 02 — Individual agents, run in isolation.

Goal: see each agent's input/output contract on its own. This is the best
place to set breakpoints *inside* each agent's run() method.

Requires bootstrap.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio

import pytest
from helpers import BOOTSTRAP_HINT, get_bootstrapped


async def _run_agents(container, cid):
    wf = container.workflow

    profile = await wf.sql_agent.get_profile(cid)
    benchmark = await wf.sql_agent.get_benchmark(profile.segment)
    print(f"\n=== SQLAgent ===\n  segment={profile.segment} benchmark={benchmark}")

    prediction = await wf.ml_agent.run(profile)
    print(f"\n=== MLAgent ===\n  churn={prediction.churn_probability:.3f} "
          f"band={prediction.risk_band}")

    knowledge = await wf.knowledge_agent.run(profile, prediction)
    print(f"\n=== KnowledgeAgent ===\n  hits={len(knowledge)} "
          + (knowledge[0].document if knowledge else "none"))

    recommendation = await wf.recommendation_agent.run(
        profile, prediction, benchmark, knowledge, []
    )
    print(f"\n=== RecommendationAgent ===\n  generated_by={recommendation.generated_by}")
    print(f"  requires_human_approval={recommendation.requires_human_approval}")
    for a in recommendation.actions:
        print(f"    P{a.priority} [{a.owner}] {a.action} (approval={a.approval_required})")
    print(f"  evidence count = {len(recommendation.evidence)}")

    review = await wf.reviewer_agent.run(profile, prediction, recommendation)
    print(f"\n=== ReviewerAgent ===\n  passed={review.passed} score={review.score:.2f}")
    for issue in review.issues:
        print(f"    - {issue}")

    report = await wf.report_agent.run(
        profile, prediction, benchmark, knowledge, recommendation, review
    )
    print(f"\n=== ReportAgent ===\n  markdown length = {len(report)} chars")
    print(report[:300])


def test_agents() -> None:
    res = get_bootstrapped()
    if res is None:
        pytest.skip(BOOTSTRAP_HINT)
        return
    asyncio.run(_run_agents(*res))


if __name__ == "__main__":
    res = get_bootstrapped()
    if res is None:
        raise SystemExit(BOOTSTRAP_HINT)
    asyncio.run(_run_agents(*res))
