"""Tour 03 — End-to-end workflow.analyze.

Goal: the single most important test for understanding how the agents are
orchestrated. Set breakpoints at app/workflows/customer_retention.py:

    61  profile   = await self.sql_agent.get_profile(customer_id)
    70  prediction, benchmark = await asyncio.gather(...)   # ML + benchmark in parallel
    71  knowledge = await self.knowledge_agent.run(profile, prediction)
    72  recommendation = await self.recommendation_agent.run(...)
    75  review     = await self.reviewer_agent.run(...)
    76  report     = await self.report_agent.run(...)
    115 return AnalysisResponse(...)

Trace how data morphs: profile -> prediction -> knowledge -> recommendation
-> review -> report. Uses persist=False so it never writes to the DB.

Requires bootstrap.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio

import pytest
from helpers import BOOTSTRAP_HINT, get_bootstrapped


async def _run_e2e(container, cid):
    result = await container.workflow.analyze(
        cid, session_id="tour", create_ticket=False, persist=False
    )
    print("\n=== AnalysisResponse ===")
    print(f"  customer          = {result.customer.customer_id} ({result.customer.segment})")
    print(f"  prediction        = {result.prediction.risk_band} "
          f"(p={result.prediction.churn_probability:.3f})")
    print(f"  knowledge hits    = {len(result.knowledge)}")
    print(f"  recommendation    = by {result.recommendation.generated_by}, "
          f"actions={len(result.recommendation.actions)}, "
          f"approval={result.recommendation.requires_human_approval}")
    print(f"  review            = passed={result.review.passed} score={result.review.score:.2f}")
    print(f"  generation_mode   = {result.generation_mode}")
    print(f"  fallback_used     = {result.fallback_used}")
    print(f"  latency_ms        = {result.latency_ms:.1f}")
    print("\n--- report_markdown (first 400 chars) ---")
    print(result.report_markdown[:400])


def test_workflow_e2e() -> None:
    res = get_bootstrapped()
    if res is None:
        pytest.skip(BOOTSTRAP_HINT)
        return
    asyncio.run(_run_e2e(*res))


if __name__ == "__main__":
    res = get_bootstrapped()
    if res is None:
        raise SystemExit(BOOTSTRAP_HINT)
    asyncio.run(_run_e2e(*res))
