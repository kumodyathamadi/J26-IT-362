"""
Component 2 — Regulatory Compliance Analysis Endpoint
Exposes POST /api/analyse (and /api/analyze alias).
Deterministic rule execution with summary counts and bilingual follow-up questions.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi import APIRouter

from engine.profile import (
    ComplianceAnalysisOutput,
    SharedBusinessProfile,
)
from engine.evaluate import evaluate_all
from engine.questions import generate_follow_up_questions

router = APIRouter(prefix="/api", tags=["Component 2 — Regulatory Compliance Engine"])


@router.post("/analyse", response_model=ComplianceAnalysisOutput)
@router.post("/analyze", response_model=ComplianceAnalysisOutput)
def analyse_compliance(profile: SharedBusinessProfile) -> ComplianceAnalysisOutput:
    """
    Deterministic rule engine evaluation of business profile against compliance obligations.

    Input: Business profile JSON (all fields default to null/unknown).
    Output:
      - obligations list with statuses (APPLICABLE, NOT_APPLICABLE, UNKNOWN)
      - summary count per status
      - deterministic follow-up questions generated from missing facts (no LLM)
    """
    profile_dict = profile.model_dump()
    evaluated = evaluate_all(profile_dict)

    summary = {
        "total": len(evaluated),
        "applicable": sum(1 for o in evaluated if o["status"] == "APPLICABLE"),
        "not_applicable": sum(1 for o in evaluated if o["status"] == "NOT_APPLICABLE"),
        "unknown": sum(1 for o in evaluated if o["status"] == "UNKNOWN"),
    }

    # Aggregate missing facts strictly from obligations that are UNKNOWN
    missing_facts_collected: List[str] = []
    seen = set()
    for o in evaluated:
        if o["status"] == "UNKNOWN":
            for f in o.get("missing_facts", []):
                if f not in seen:
                    seen.add(f)
                    missing_facts_collected.append(f)

    follow_up_questions = generate_follow_up_questions(missing_facts_collected)

    return ComplianceAnalysisOutput(
        summary=summary,  # type: ignore[arg-type]
        obligations=evaluated,  # type: ignore[arg-type]
        follow_up_questions=follow_up_questions,  # type: ignore[arg-type]
    )
