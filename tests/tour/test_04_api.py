"""Tour 04 — FastAPI surface (routes), no live server needed.

Goal: see which HTTP endpoints exist and what they return, using TestClient.

- GET /health always works (no bootstrap needed).
- GET /v1/operations/dashboard and /v1/operations/evaluation need bootstrap.

Run:
    python -m pytest tests/tour/test_04_api.py -v -s
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
from fastapi.testclient import TestClient
from helpers import BOOTSTRAP_HINT, get_bootstrapped

from app.api.main import app


def test_health() -> None:
    client = TestClient(app)
    resp = client.get("/health")
    print("\n=== GET /health ===")
    print(f"  status_code = {resp.status_code}")
    print(f"  body        = {resp.json()}")
    assert resp.status_code == 200


def test_operations_endpoints() -> None:
    res = get_bootstrapped()
    if res is None:
        pytest.skip(BOOTSTRAP_HINT)
        return
    client = TestClient(app)
    for path in ("/v1/operations/dashboard", "/v1/operations/evaluation"):
        resp = client.get(path)
        print(f"\n=== GET {path} ===")
        print(f"  status_code   = {resp.status_code}")
        data = resp.json()
        print(f"  top-level keys = {list(data.keys())}")
        if path.endswith("dashboard"):
            print(f"  summary        = {data.get('summary')}")
        if path.endswith("evaluation"):
            print(f"  metrics        = {data.get('agent_evaluation', {}).get('metrics')}")


if __name__ == "__main__":
    client = TestClient(app)
    resp = client.get("/health")
    print("\n=== GET /health ===", resp.status_code, resp.json())
    res = get_bootstrapped()
    if res is None:
        print("(dashboard/evaluation skipped: bootstrap first)")
        raise SystemExit(0)
    for path in ("/v1/operations/dashboard", "/v1/operations/evaluation"):
        resp = client.get(path)
        print(f"\n=== GET {path} ===", resp.status_code, list(resp.json().keys()))
