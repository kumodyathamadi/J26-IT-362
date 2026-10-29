"""
Component 2 — Rulebook Loader

Loads and validates obligations.yaml from data/compliance/rulebook/.
Raises clear errors if the file is missing or malformed.
This module is the ONLY place that reads the YAML; everything else imports
load_rulebook().
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import List

import yaml

from backend.app.compliance.schemas import ObligationRule, ObligationRulebook

# Resolve path relative to repo root so it works from any CWD
_REPO_ROOT = Path(__file__).resolve().parents[3]  # backend/app/compliance/ -> repo root
_RULEBOOK_PATH = _REPO_ROOT / "data" / "compliance" / "rulebook" / "obligations.yaml"


@lru_cache(maxsize=1)
def load_rulebook() -> ObligationRulebook:
    """
    Load, parse, and validate the obligations.yaml rulebook.
    Cached after first load — restart the process to pick up file changes.
    """
    if not _RULEBOOK_PATH.exists():
        raise FileNotFoundError(
            f"Obligations rulebook not found at {_RULEBOOK_PATH}. "
            "Run 'python scripts/compliance/register_source.py' to initialize data."
        )
    with open(_RULEBOOK_PATH, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    return ObligationRulebook.model_validate(raw)


def get_obligations() -> List[ObligationRule]:
    """Convenience accessor returning the flat list of obligation rules."""
    return load_rulebook().obligations
