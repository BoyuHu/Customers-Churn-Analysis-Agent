"""Shared helpers for the project "tour" tests.

These let each tour test run after bootstrap, or skip gracefully with a clear
hint so a fresh checkout's `pytest -q` never breaks.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json

from app.core.container import get_container


def first_customer_id() -> str | None:
    """Return a customer id to drive the tour.

    Prefers the golden dataset (stable across runs), falls back to the first
    id in the operational DB. Returns None when nothing is available yet.
    """
    container = get_container()
    golden = container.settings.golden_dataset_path
    if golden.exists():
        for line in golden.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    return json.loads(line)["customer_id"]
                except json.JSONDecodeError:
                    continue
    ids = container.customer_repository.list_ids(limit=1)
    return ids[0] if ids else None


def get_bootstrapped():
    """Return (container, customer_id) when data exists, else None."""
    container = get_container()
    cid = first_customer_id()
    return (container, cid) if cid is not None else None


BOOTSTRAP_HINT = "Bootstrap first: python -m scripts.bootstrap --rows 1200 --max-iter 1000"
