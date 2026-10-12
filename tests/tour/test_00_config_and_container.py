"""Tour 00 — Configuration & Dependency Injection.

Goal: understand how the app is configured and how the 6 agents are wired
together by `ApplicationContainer`. This is the entry point of the tour.

Run:
    python -m pytest tests/tour/test_00_config_and_container.py -v -s
Or debug this file directly (it has a __main__ block).

No bootstrap required.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.config import get_settings


def _dump_settings() -> None:
    s = get_settings()
    print("\n=== Settings (selected) ===")
    for name in (
        "app_name", "environment", "agent_provider", "risk_high", "risk_medium",
        "database_path", "model_path", "model_metadata_path", "golden_dataset_path",
        "knowledge_dir", "retrieval_backend", "retrieval_top_k",
    ):
        print(f"  {name:24} = {getattr(s, name)}")


def test_settings_explained() -> None:
    """Print resolved configuration. No external deps, no bootstrap needed."""
    _dump_settings()
    assert get_settings() is get_settings()  # lru_cache singleton


def test_container_wiring() -> None:
    """Print how ApplicationContainer wires the 6 agents.

    Breakpoint suggestion: app/core/container.py:152 (workflow construction)
    and :128-142 (provider_status / deterministic fallback selection).
    """
    from app.core.container import get_container

    c = get_container()
    wf = c.workflow
    print("\n=== ApplicationContainer wiring ===")
    print(f"  generation_mode = {c.provider_status['generation_mode']}")
    print(f"  provider        = {c.provider_status['provider']}")
    print("  workflow agents (execution order):")
    for name in (
        "sql_agent", "ml_agent", "knowledge_agent",
        "recommendation_agent", "reviewer_agent", "report_agent",
    ):
        print(f"    - {name:22} -> {type(getattr(wf, name)).__name__}")
    print(f"  ml_service.ready = {c.ml_service.ready}")


if __name__ == "__main__":
    _dump_settings()
    from app.core.container import get_container

    c = get_container()
    wf = c.workflow
    print("\n=== ApplicationContainer wiring ===")
    print(f"  generation_mode = {c.provider_status['generation_mode']}")
    print("  workflow agents:")
    for name in (
        "sql_agent", "ml_agent", "knowledge_agent",
        "recommendation_agent", "reviewer_agent", "report_agent",
    ):
        print(f"    - {name:22} -> {type(getattr(wf, name)).__name__}")
