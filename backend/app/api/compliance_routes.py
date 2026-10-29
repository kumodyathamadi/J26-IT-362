"""
Component 2 — Compliance API Routes

Endpoints:
  POST /compliance/analyze     — Run three-valued applicability engine
  GET  /compliance/obligations  — List all obligations from rulebook
  GET  /compliance/sources      — List all registered source documents

Design rule: The LLM may only *phrase* results; it NEVER decides applicability.
All decisions come from engine.analyze_compliance().
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from backend.app.compliance.schemas import (
    BusinessProfile,
    ComplianceAnalysisResponse,
)
from backend.app.compliance.engine import analyze_compliance
from backend.app.compliance.rulebook_loader import get_obligations
from backend.app.compliance.source_registry import get_all_sources
from backend.app.compliance.component1_mapper import map_from_component1

router = APIRouter(
    prefix="/compliance",
    tags=["Component 2 — Compliance"],
)


@router.post("/analyze", response_model=ComplianceAnalysisResponse)
async def analyze(
    profile: BusinessProfile,
) -> ComplianceAnalysisResponse:
    """
    Run deterministic three-valued applicability engine.

    Submit a BusinessProfile (all fields optional; None = unknown).
    Returns one ObligationResult per rulebook entry with status:
      applicable | conditional | not_applicable | unknown

    The LLM does NOT decide applicability. All logic is deterministic.
    """
    try:
        return analyze_compliance(profile)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Engine error: {exc}")


@router.post("/analyze/from-component1", response_model=ComplianceAnalysisResponse)
async def analyze_from_component1(
    c1_data: Dict[str, Any],
) -> ComplianceAnalysisResponse:
    """
    Accept Component 1's raw output dict and map it to a BusinessProfile
    before running the applicability engine.

    Allows seamless integration between Component 1 and Component 2
    without the frontend needing to know the mapping.
    """
    try:
        profile = map_from_component1(c1_data)
        return analyze_compliance(profile)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Mapping/engine error: {exc}")


@router.get("/obligations")
async def list_obligations() -> List[Dict[str, Any]]:
    """
    Return all obligations from the verified rulebook.
    Useful for browsing the full regulatory scope without submitting a profile.
    """
    try:
        obligations = get_obligations()
        return [
            {
                "id": o.id,
                "name": o.name,
                "authority": o.authority,
                "jurisdiction": o.jurisdiction,
                "required_action": o.required_action.strip(),
                "effective_from": o.effective_from,
                "reviewer_status": o.reviewer_status,
                "applies_to_types": o.applies_if.get("business_type", []),
            }
            for o in obligations
        ]
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/sources")
async def list_sources() -> List[Dict[str, Any]]:
    """
    Return all registered source documents from source_register.csv.
    Provides transparency: every legal source cited by the engine is listed here.
    """
    return get_all_sources()


@router.get("/sample-profiles/{profile_id}")
async def get_sample_profile(profile_id: str) -> Dict[str, Any]:
    """
    Return a demo sample profile from data/compliance/profiles/.
    Valid profile_id: clear_case, conditional_case, missing_info_case
    """
    import json
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[3]
    profile_path = repo_root / "data" / "compliance" / "profiles" / f"{profile_id}.json"
    if not profile_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample profile '{profile_id}' not found")
    with open(profile_path, encoding="utf-8") as f:
        return json.load(f)
