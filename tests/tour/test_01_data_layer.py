"""Tour 01 — Data layer: customer profile, ML prediction, knowledge retrieval.

Goal: see the raw inputs each agent consumes *before* the agent layer runs.
These three objects (CustomerProfile, PredictionResult, KnowledgeHit) are the
contracts that flow through the whole system.

Requires bootstrap (creates the DB, model, and golden dataset).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from helpers import BOOTSTRAP_HINT, get_bootstrapped
import pytest


def test_customer_profile() -> None:
    res = get_bootstrapped()
    if res is None:
        pytest.skip(BOOTSTRAP_HINT)
        return
    container, cid = res
    profile = container.customer_repository.get(cid)
    print(f"\n=== CustomerProfile({cid}) ===")
    for field, value in profile.model_dump().items():
        print(f"  {field:24} = {value}")


def test_ml_prediction() -> None:
    res = get_bootstrapped()
    if res is None:
        pytest.skip(BOOTSTRAP_HINT)
        return
    container, cid = res
    profile = container.customer_repository.get(cid)
    pred = container.ml_service.predict(profile)
    print(f"\n=== PredictionResult({cid}) ===")
    print(f"  churn_probability = {pred.churn_probability:.4f}")
    print(f"  risk_band         = {pred.risk_band}")
    print(f"  model_version     = {pred.model_version}")
    print("  top_drivers (highest impact first):")
    for d in pred.top_drivers:
        print(f"    - {d.feature:24} dir={d.direction:10} impact={d.probability_impact:.3f}")
        print(f"        {d.explanation}")


def test_knowledge_retrieval() -> None:
    res = get_bootstrapped()
    if res is None:
        pytest.skip(BOOTSTRAP_HINT)
        return
    container, cid = res
    profile = container.customer_repository.get(cid)
    hits = container.knowledge_service.search(f"{profile.segment} retention", top_k=3)
    print(f"\n=== KnowledgeHit (top {len(hits)}) ===")
    for h in hits:
        print(f"  [{h.score:.3f}] {h.document} / {h.section}")
        print(f"        {h.text[:90]}...")


if __name__ == "__main__":
    res = get_bootstrapped()
    if res is None:
        raise SystemExit(BOOTSTRAP_HINT)
    container, cid = res
    profile = container.customer_repository.get(cid)
    print(f"\n=== CustomerProfile({cid}) ===")
    for field, value in profile.model_dump().items():
        print(f"  {field:24} = {value}")
    pred = container.ml_service.predict(profile)
    print(f"\n=== PredictionResult({cid}) ===")
    print(f"  churn={pred.churn_probability:.4f} band={pred.risk_band}")
    hits = container.knowledge_service.search(f"{profile.segment} retention", top_k=3)
    print(f"\n=== KnowledgeHit (top {len(hits)}) ===")
    for h in hits:
        print(f"  [{h.score:.3f}] {h.document} / {h.section}")
