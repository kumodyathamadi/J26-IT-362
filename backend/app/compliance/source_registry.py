"""
Component 2 — Source Registry Reader

Loads data/compliance/source_register.csv and provides fast look-ups
by source_id. Used by the engine to attach URL and retrieval date to
evidence chunks without touching the LLM.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parents[3]
_REGISTER_PATH = _REPO_ROOT / "data" / "compliance" / "source_register.csv"


@lru_cache(maxsize=1)
def _load_register() -> Dict[str, Dict[str, str]]:
    """Return a dict keyed by source_id."""
    if not _REGISTER_PATH.exists():
        return {}
    with open(_REGISTER_PATH, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return {row["source_id"]: row for row in reader}


def get_source_details(source_id: str) -> Dict[str, str]:
    """Return full row dict for a given source_id from source register."""
    register = _load_register()
    return register.get(source_id, {})


def get_source_url_and_date(source_id: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (url, retrieved_date) for a given source_id, or (None, None)."""
    row = get_source_details(source_id)
    url = row.get("url") or None
    retrieved_date = row.get("retrieved_date") or None
    return url, retrieved_date


def get_all_sources() -> list:
    """Return all rows from the source register as a list of dicts."""
    return list(_load_register().values())
