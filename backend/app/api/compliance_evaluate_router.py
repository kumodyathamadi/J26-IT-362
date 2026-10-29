"""
Component 2 — Regulatory Compliance Evaluation Router
Exposes:
  POST /api/compliance/evaluate

Receives the business profile JSON from Component 1, filters obligations
(Common + specific business_type layer), executes the 3-valued Kleene rule engine,
and returns an auditable, source-grounded compliance output.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Set

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi import APIRouter, HTTPException

from engine.schemas import (
    BusinessProfileInput,
    ComplianceEvaluationResponse,
    GroupedObligations,
    ObligationEvaluationResult,
    SummaryCounts,
)
from engine.evaluate import evaluate_obligation
from engine.loader import load_rulebook
from engine.questions import generate_follow_up_questions

router = APIRouter(
    prefix="/api/compliance",
    tags=["Component 2 — Legal & Regulatory Rule Engine"],
)


@router.post("/evaluate", response_model=ComplianceEvaluationResponse)
def evaluate_compliance_endpoint(
    profile: BusinessProfileInput,
) -> ComplianceEvaluationResponse:
    """
    Evaluate business profile received from Component 1 against legal obligations.

    Workflow:
      1. Validates incoming profile with Pydantic (all optional/conditional fields default to None / UNKNOWN).
      2. Scopes obligations: Common layer + specific sector layer matching profile.business_type.
      3. Deterministically executes 3-valued Kleene logic rules (zero LLM intervention).
      4. Aggregates results into summary metrics and status groupings (APPLICABLE, UNKNOWN, NOT_APPLICABLE).
      5. Generates deterministic bilingual follow-up questions for missing facts.
    """
    try:
        profile_dict = profile.model_dump()
        target_layers = {"common", profile.business_type}

        # Load authoritative rulebook
        all_obligations = load_rulebook()

        # Scope obligations to common + matching sector
        scoped_obligations = [o for o in all_obligations if o.layer in target_layers]

        evaluated_list: List[ObligationEvaluationResult] = []
        applicable_list: List[ObligationEvaluationResult] = []
        unknown_list: List[ObligationEvaluationResult] = []
        not_applicable_list: List[ObligationEvaluationResult] = []

        missing_facts_seen: Set[str] = set()
        missing_facts_to_ask: List[str] = []

        for obl in scoped_obligations:
            raw_res = evaluate_obligation(obl, profile_dict)
            model_res = ObligationEvaluationResult(**raw_res)
            evaluated_list.append(model_res)

            if model_res.status == "APPLICABLE":
                applicable_list.append(model_res)
            elif model_res.status == "NOT_APPLICABLE":
                not_applicable_list.append(model_res)
            else:  # UNKNOWN
                unknown_list.append(model_res)
                # Collect missing facts to generate follow-up questions
                for fact in model_res.missing_facts:
                    if fact not in missing_facts_seen:
                        missing_facts_seen.add(fact)
                        missing_facts_to_ask.append(fact)

        summary = SummaryCounts(
            applicable_count=len(applicable_list),
            unknown_count=len(unknown_list),
            not_applicable_count=len(not_applicable_list),
            total_evaluated=len(evaluated_list),
        )

        grouped = GroupedObligations(
            applicable=applicable_list,
            unknown=unknown_list,
            not_applicable=not_applicable_list,
        )

        follow_up_questions = generate_follow_up_questions(missing_facts_to_ask)

        return ComplianceEvaluationResponse(
            business_id=profile.business_id,
            business_type=profile.business_type,
            summary=summary,
            grouped_obligations=grouped,
            obligations=evaluated_list,
            follow_up_questions=follow_up_questions,
            disclaimer=(
                "This evaluation is preliminary decision-support generated deterministically "
                "using 3-valued Kleene rule logic. It does not constitute formal legal advice."
            ),
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Compliance evaluation error: {str(exc)}")
