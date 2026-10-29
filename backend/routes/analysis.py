import sys
import os
import uuid
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

# Ensure root path is accessible for src module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.database import get_db
from backend.models import AnalysisRecord, AnalysisAuditLog
from backend.schemas import BusinessAnalysisRequest, PaginatedRecordsResponse, AnalysisRecordSummary, AdoptStrategyPayload
from sqlalchemy.orm.attributes import flag_modified
from src.orchestrator import analyze_business
from src.preprocessing.preprocessor import InputValidationError, validate_and_format_input
from src.prediction.predictor import FeasibilityPredictor
from src.planning.planner import PersonalizedPlanGenerator
from src.explainability.explainer import format_feature_value_from_row

router = APIRouter(prefix="/api/business", tags=["Business Analysis"])

_shared_predictor = None

def get_shared_predictor():
    global _shared_predictor
    if _shared_predictor is None:
        _shared_predictor = FeasibilityPredictor()
    return _shared_predictor


def serialize_analysis_record(rec: AnalysisRecord) -> Dict[str, Any]:
    """
    Serializes an AnalysisRecord database entity into a clean summary dict.
    Extracts capital and customer counts safely from input_profile to eliminate NaN values.
    """
    in_prof = rec.input_profile or {}
    if isinstance(in_prof, str):
        try:
            in_prof = json.loads(in_prof)
        except Exception:
            in_prof = {}

    capital = float(in_prof.get("available_capital_lkr", 0.0))
    customers = int(in_prof.get("expected_customers_per_day", 0))

    b_name = getattr(rec, "business_name", None) or in_prof.get("business_name")
    stage = rec.business_stage
    stage_label = "New Startup" if stage == "new_startup" or "new" in str(stage).lower() else "Existing Business"

    return {
        "id": rec.id,
        "business_name": b_name,
        "business_stage": stage,
        "stage_label": stage_label,
        "business_category": rec.business_category,
        "district": rec.district,
        "feasibility_label": rec.feasibility_label,
        "predicted_label": rec.feasibility_label,
        "confidence_score": round(rec.confidence_score, 4),
        "confidence_percent": f"{(rec.confidence_score * 100):.1f}%",
        "available_capital_lkr": capital,
        "expected_customers_per_day": customers,
        "original_business_description": rec.original_business_description,
        "created_at": rec.created_at.isoformat() if rec.created_at else None
    }


@router.post("/analyze", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def analyze_sme_business(
    payload: BusinessAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Executes Component 1 End-to-End Business Analysis Pipeline:
    Preprocessing -> Prediction -> SHAP -> Strategy Generation -> TOPSIS -> What-If -> Plan -> Structured Profile.
    Persists original user description and extraction metadata for research traceability in database.
    """
    try:
        raw_input = payload.model_dump()
        structured_profile = analyze_business(raw_input)

        feasibility_data = structured_profile.get("feasibility_analysis", {})
        predicted_label = feasibility_data.get("predicted_label", "Conditionally Feasible")
        confidence_score = feasibility_data.get("confidence_score", 0.0)

        record_id = str(uuid.uuid4())
        structured_profile["metadata"]["record_id"] = record_id

        # Save record to Database with canonical business_stage
        canonical_stage = structured_profile.get("business_input", {}).get("business_stage", payload.business_stage)
        canonical_category = structured_profile.get("business_input", {}).get("business_category", payload.business_category)
        b_name = payload.business_name or raw_input.get("business_name") or structured_profile.get("business_input", {}).get("business_name")
        if b_name:
            structured_profile["business_name"] = b_name
            if "business_input" in structured_profile and isinstance(structured_profile["business_input"], dict):
                structured_profile["business_input"]["business_name"] = b_name

        record = AnalysisRecord(
            id=record_id,
            user_id=None,
            business_name=b_name,
            business_stage=canonical_stage,
            business_category=canonical_category,
            district=payload.district,
            feasibility_label=predicted_label,
            confidence_score=confidence_score,
            input_profile=structured_profile.get("business_input", raw_input),
            structured_profile=structured_profile,
            original_business_description=payload.original_business_description,
            extraction_metadata=payload.extraction_metadata
        )
        db.add(record)

        # Log audit trail event for creation
        audit_entry = AnalysisAuditLog(
            user_id=None,
            user_email="analyst@sme360.ai",
            record_id=record_id,
            action="created",
            business_name=b_name,
            business_category=record.business_category,
            district=record.district,
            result_label=predicted_label,
            result_score=confidence_score,
            inputs_snapshot=raw_input
        )
        db.add(audit_entry)

        db.commit()
        db.refresh(record)

        return structured_profile

    except (InputValidationError, ValueError) as ve:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business analysis failed: {str(e)}"
        )


@router.post("/simulate", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def simulate_sme_scenario(
    payload: BusinessAnalysisRequest,
    baseline_record_id: Optional[str] = Query(None, description="Optional baseline record ID to compute delta shifts against"),
    db: Session = Depends(get_db)
):
    """
    Dedicated What-If Scenario Simulation Endpoint:
    Executes input validation, feature preprocessing, and Random Forest feasibility inference.
    Computes multi-class probability deltas and viability index shifts against baseline state.
    
    CRITICAL ARCHITECTURAL GUARANTEES:
    - NEVER creates or persists an AnalysisRecord in the database.
    - NEVER creates or persists an AnalysisAuditLog entry.
    - NEVER mutates or overwrites any existing database records.
    """
    try:
        raw_input = payload.model_dump()
        input_df, cleaned_input = validate_and_format_input(raw_input)
        
        predictor = get_shared_predictor()
        feasibility_result = predictor.predict_feasibility(input_df)
        
        mod_probs = feasibility_result["probabilities"]
        mod_feasible = float(mod_probs.get("Feasible", 0.0))
        mod_cond = float(mod_probs.get("Conditionally Feasible", 0.0))
        mod_infeas = float(mod_probs.get("Infeasible", 0.0))
        # Viability Index = P(Feasible) + 0.5 * P(Conditionally Feasible)
        new_viability = round(mod_feasible + 0.5 * mod_cond, 4)
        
        # Retrieve baseline probabilities if baseline_record_id provided
        base_probs = {}
        if baseline_record_id:
            base_rec = db.query(AnalysisRecord).filter(AnalysisRecord.id == baseline_record_id).first()
            if base_rec and base_rec.structured_profile:
                prof = base_rec.structured_profile
                if isinstance(prof, str):
                    try:
                        prof = json.loads(prof)
                    except Exception:
                        prof = {}
                base_probs = prof.get("feasibility_analysis", {}).get("probabilities", {})

        # Fallback to extraction_metadata if baseline_probabilities passed directly
        if not base_probs and payload.extraction_metadata and isinstance(payload.extraction_metadata, dict):
            base_probs = payload.extraction_metadata.get("baseline_probabilities", {})

        deltas = {}
        viability_delta = 0.0
        base_viability = new_viability
        if base_probs:
            base_feasible = float(base_probs.get("Feasible", 0.0))
            base_cond = float(base_probs.get("Conditionally Feasible", 0.0))
            base_infeas = float(base_probs.get("Infeasible", 0.0))
            base_viability = round(base_feasible + 0.5 * base_cond, 4)
            deltas = {
                "Feasible": round(mod_feasible - base_feasible, 4),
                "Conditionally Feasible": round(mod_cond - base_cond, 4),
                "Infeasible": round(mod_infeas - base_infeas, 4)
            }
            viability_delta = round(new_viability - base_viability, 4)

        return {
            "status": "simulated",
            "is_simulation": True,
            "business_input": cleaned_input,
            "feasibility_analysis": {
                "predicted_label": feasibility_result["prediction"],
                "confidence_score": feasibility_result["confidence_score"],
                "probabilities": mod_probs
            },
            "prediction": feasibility_result["prediction"],
            "confidence_score": feasibility_result["confidence_score"],
            "probabilities": mod_probs,
            "probability_deltas": deltas,
            "base_viability_score": base_viability,
            "new_viability_score": new_viability,
            "viability_delta": viability_delta,
            "impact_summary": (
                f"Viability index: {base_viability:.1%} -> {new_viability:.1%} ({'+' if viability_delta >= 0 else ''}{viability_delta:.1%}). "
                f"Class shifts: Feasible ({'+' if deltas.get('Feasible', 0) >= 0 else ''}{deltas.get('Feasible', 0):.1%}), "
                f"Conditional ({'+' if deltas.get('Conditionally Feasible', 0) >= 0 else ''}{deltas.get('Conditionally Feasible', 0):.1%}), "
                f"Infeasible ({'+' if deltas.get('Infeasible', 0) >= 0 else ''}{deltas.get('Infeasible', 0):.1%})."
            ) if base_probs else "Simulation executed against updated scenario parameters."
        }
    except (InputValidationError, ValueError) as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario simulation failed: {str(e)}"
        )


@router.get("/records", response_model=PaginatedRecordsResponse)
def list_analysis_records(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Records per page"),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    stage: Optional[str] = Query(None, description="Filter by business stage ('all', 'new_startup', 'existing')"),
    category: Optional[str] = Query(None, description="Filter by business category"),
    district: Optional[str] = Query(None, description="Filter by Sri Lankan district"),
    result: Optional[str] = Query(None, description="Filter by feasibility result ('Feasible', 'Conditionally Feasible', 'Infeasible')"),
    search: Optional[str] = Query(None, description="Search term across category, district, and result"),
    sort: Optional[str] = Query("newest", description="Sort order: 'newest', 'highest_score', 'lowest_score', 'oldest'"),
    db: Session = Depends(get_db)
):
    """
    Lists paginated SME business analysis runs with total counts and numeric attributes.
    Eliminates NaN values by extracting capital and customer counts safely.
    Excludes soft-deleted records.
    """
    eff_limit = page_size if page_size is not None else limit
    offset = (page - 1) * eff_limit

    query = db.query(AnalysisRecord).filter(
        or_(AnalysisRecord.is_deleted == False, AnalysisRecord.is_deleted == None)
    )

    # Filter by stage
    if stage and stage.strip().lower() != "all":
        s = stage.strip().lower()
        if "new" in s:
            query = query.filter(AnalysisRecord.business_stage == "new_startup")
        elif "exist" in s:
            query = query.filter(AnalysisRecord.business_stage == "existing")

    # Filter by category
    if category and category.strip().lower() != "all":
        query = query.filter(AnalysisRecord.business_category == category.strip())

    # Filter by district
    if district and district.strip().lower() != "all":
        query = query.filter(func.lower(AnalysisRecord.district) == district.strip().lower())

    # Filter by feasibility result
    if result and result.strip().lower() != "all":
        query = query.filter(func.lower(AnalysisRecord.feasibility_label) == result.strip().lower())

    # Search filter
    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(AnalysisRecord.business_name).like(term),
                func.lower(AnalysisRecord.business_category).like(term),
                func.lower(AnalysisRecord.district).like(term),
                func.lower(AnalysisRecord.feasibility_label).like(term),
                func.lower(AnalysisRecord.original_business_description).like(term)
            )
        )

    # Total count from database
    total_count = query.count()

    # Sort
    if sort == "highest_score":
        query = query.order_by(AnalysisRecord.confidence_score.desc(), AnalysisRecord.created_at.desc())
    elif sort == "lowest_score":
        query = query.order_by(AnalysisRecord.confidence_score.asc(), AnalysisRecord.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(AnalysisRecord.created_at.asc())
    else:
        query = query.order_by(AnalysisRecord.created_at.desc())

    records = query.offset(offset).limit(eff_limit).all()
    items = [serialize_analysis_record(rec) for rec in records]

    return {
        "total_count": total_count,
        "page": page,
        "page_size": eff_limit,
        "items": items
    }


@router.get("/summary", response_model=Dict[str, Any])
def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    """
    Returns real aggregate metrics for Dashboard KPIs.
    Excludes soft-deleted records.
    """
    base_query = db.query(AnalysisRecord).filter(
        or_(AnalysisRecord.is_deleted == False, AnalysisRecord.is_deleted == None)
    )

    total_count = base_query.count()
    
    # Counts by feasibility outcome
    feasible_count = base_query.filter(AnalysisRecord.feasibility_label == "Feasible").count()
    cond_feasible_count = base_query.filter(AnalysisRecord.feasibility_label == "Conditionally Feasible").count()
    infeasible_count = base_query.filter(AnalysisRecord.feasibility_label == "Infeasible").count()

    feasible_rate = round((feasible_count / total_count * 100), 1) if total_count > 0 else 0.0

    # Top category
    top_cat_row = db.query(
        AnalysisRecord.business_category, func.count(AnalysisRecord.id).label("cnt")
    ).filter(
        or_(AnalysisRecord.is_deleted == False, AnalysisRecord.is_deleted == None)
    ).group_by(AnalysisRecord.business_category).order_by(func.count(AnalysisRecord.id).desc()).first()
    top_sector = top_cat_row[0] if top_cat_row else "Not provided"

    # Average capital
    cap_records = base_query.with_entities(AnalysisRecord.input_profile).all()
    cap_sum = 0.0
    cap_count = 0
    for r in cap_records:
        in_prof = r[0] or {}
        if isinstance(in_prof, str):
            try:
                in_prof = json.loads(in_prof)
            except Exception:
                in_prof = {}
        c = in_prof.get("available_capital_lkr")
        if c is not None:
            try:
                cap_sum += float(c)
                cap_count += 1
            except (ValueError, TypeError):
                pass
    avg_capital = round(cap_sum / cap_count, 2) if cap_count > 0 else 0.0

    # Latest record for 'Continue where you left off'
    latest = base_query.order_by(AnalysisRecord.created_at.desc()).first()
    latest_record = serialize_analysis_record(latest) if latest else None

    # Feasibility distribution for donut/pie chart
    feasibility_distribution = [
        {"name": "Feasible", "value": feasible_count, "color": "#22c55e"},
        {"name": "Conditional", "value": cond_feasible_count, "color": "#eab308"},
        {"name": "Infeasible", "value": infeasible_count, "color": "#ef4444"}
    ]

    # Sector distribution for bar chart
    sector_counts = db.query(
        AnalysisRecord.business_category, func.count(AnalysisRecord.id).label("count")
    ).filter(
        or_(AnalysisRecord.is_deleted == False, AnalysisRecord.is_deleted == None)
    )
    sector_data = [
        {"category": row[0], "count": row[1]} 
        for row in sector_counts.group_by(AnalysisRecord.business_category).all()
    ]

    # Recent activity timeline (by date)
    recent_runs = base_query.order_by(AnalysisRecord.created_at.asc()).limit(30).all()
    date_map = {}
    for r in recent_runs:
        if r.created_at:
            d_str = r.created_at.strftime("%b %d")
            date_map[d_str] = date_map.get(d_str, 0) + 1
    timeline_data = [{"date": k, "count": v} for k, v in date_map.items()]

    return {
        "total_analyses": total_count,
        "feasible_count": feasible_count,
        "conditionally_feasible_count": cond_feasible_count,
        "infeasible_count": infeasible_count,
        "feasible_rate": feasible_rate,
        "feasible_rate_pct": feasible_rate,
        "average_capital_lkr": avg_capital,
        "avg_capital_lkr": avg_capital,
        "top_sector": top_sector,
        "latest_record": latest_record,
        "feasibility_distribution": feasibility_distribution,
        "sector_distribution": sector_data,
        "timeline_data": timeline_data
    }


@router.get("/record/{record_id}", response_model=Dict[str, Any])
def get_analysis_record(
    record_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves a full structured profile JSON by Analysis Record ID.
    """
    rec = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not rec or rec.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record with ID '{record_id}' not found."
        )

    profile = dict(rec.structured_profile) if isinstance(rec.structured_profile, dict) else {}
    biz_name = rec.business_name or profile.get("business_name") or profile.get("business_input", {}).get("business_name")
    if biz_name:
        profile["business_name"] = biz_name
        if "business_input" in profile and isinstance(profile["business_input"], dict):
            profile["business_input"]["business_name"] = biz_name

    # Ensure explainability drivers have human-readable feature_value
    inp_row = profile.get("business_input") or rec.input_profile or {}
    if isinstance(inp_row, str):
        try:
            inp_row = json.loads(inp_row)
        except Exception:
            inp_row = {}
    if "explainability" in profile and isinstance(profile["explainability"], dict):
        for driver_key in ("positive_drivers", "negative_drivers"):
            drivers = profile["explainability"].get(driver_key, [])
            if isinstance(drivers, list):
                for d in drivers:
                    if isinstance(d, dict) and (not d.get("feature_value") or d.get("feature_value") == "N/A"):
                        d["feature_value"] = format_feature_value_from_row(
                            d.get("feature", ""), d.get("raw_feature", ""), inp_row
                        )

    # Ensure original_baseline is populated for comparison
    if "original_baseline" not in profile or not profile.get("original_baseline"):
        created_log = db.query(AnalysisAuditLog).filter(
            AnalysisAuditLog.record_id == record_id,
            AnalysisAuditLog.action == "created"
        ).order_by(AnalysisAuditLog.created_at.asc()).first()
        if created_log and created_log.inputs_snapshot:
            profile["original_baseline"] = {
                "business_input": created_log.inputs_snapshot,
                "confidence_score": created_log.result_score,
                "feasibility_label": created_log.result_label
            }

    return profile


@router.delete("/record/{record_id}", response_model=Dict[str, Any])
def delete_analysis_record(
    record_id: str,
    db: Session = Depends(get_db)
):
    """
    Soft-deletes an Analysis Record.
    """
    rec = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record with ID '{record_id}' not found."
        )

    rec.is_deleted = True

    # Audit log event for deletion
    audit_entry = AnalysisAuditLog(
        user_id=None,
        user_email="analyst@sme360.ai",
        record_id=record_id,
        action="deleted",
        business_category=rec.business_category,
        district=rec.district,
        result_label=rec.feasibility_label,
        result_score=rec.confidence_score
    )
    db.add(audit_entry)

    db.commit()
    return {"status": "deleted", "id": record_id}


@router.post("/record/{record_id}/restore", response_model=Dict[str, Any])
def restore_analysis_record(
    record_id: str,
    db: Session = Depends(get_db)
):
    """
    Restores a soft-deleted Analysis Record.
    """
    rec = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record with ID '{record_id}' not found."
        )

    rec.is_deleted = False

    # Audit log event for restoration
    audit_entry = AnalysisAuditLog(
        user_id=None,
        user_email="analyst@sme360.ai",
        record_id=record_id,
        action="restored",
        business_category=rec.business_category,
        district=rec.district,
        result_label=rec.feasibility_label,
        result_score=rec.confidence_score
    )
    db.add(audit_entry)

    db.commit()
    return {"status": "restored", "id": record_id}


@router.patch("/record/{record_id}/strategy", response_model=Dict[str, Any])
def adopt_strategic_recommendation(
    record_id: str,
    payload: AdoptStrategyPayload,
    db: Session = Depends(get_db)
):
    """
    Adopts a chosen strategic recommendation (HITL Decision Override).
    Dynamically recalculates the personalized business plan and action roadmap around the selected strategy,
    updating the structured profile in the database.
    """
    rec = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not rec or rec.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record with ID '{record_id}' not found."
        )

    prof = rec.structured_profile
    if isinstance(prof, str):
        try:
            prof = json.loads(prof)
        except Exception:
            prof = {}

    strat_recs = prof.get("strategic_recommendations", {})
    topsis = strat_recs.get("topsis_ranking", {})
    ranked = topsis.get("ranked_strategies", []) or strat_recs.get("candidate_strategies", [])

    # Find the target strategy
    chosen = next((s for s in ranked if s.get("strategy_id") == payload.strategy_id or s.get("strategy_name") == payload.strategy_id), None)
    if not chosen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Strategy '{payload.strategy_id}' not found among evaluated candidate strategies."
        )

    # Re-run plan generator with selected strategy
    planner = PersonalizedPlanGenerator()
    new_plan = planner.generate_plan(
        cleaned_input=prof.get("business_input", rec.input_profile or {}),
        feasibility_result=prof.get("feasibility_analysis", {}),
        shap_explanation=prof.get("explainability", {}),
        topsis_result=topsis,
        what_if_result=prof.get("scenario_analysis", {}).get("what_if_simulations", []),
        counterfactual=prof.get("scenario_analysis", {}).get("counterfactual_boundary", {}),
        selected_strategy_id=chosen.get("strategy_id")
    )

    # Save to profile
    prof["personalized_business_plan"] = new_plan
    if "strategic_recommendations" not in prof:
        prof["strategic_recommendations"] = {}
    prof["strategic_recommendations"]["selected_strategy_id"] = chosen.get("strategy_id")
    prof["strategic_recommendations"]["selected_strategy_name"] = chosen.get("strategy_name")

    rec.structured_profile = prof
    flag_modified(rec, "structured_profile")

    # Add audit log
    audit_entry = AnalysisAuditLog(
        user_id=None,
        user_email="analyst@sme360.ai",
        record_id=record_id,
        action="strategy_adopted",
        business_category=rec.business_category,
        district=rec.district,
        result_label=chosen.get("strategy_name"),
        result_score=chosen.get("topsis_score", 0.0)
    )
    db.add(audit_entry)

    db.commit()
    db.refresh(rec)

    return {
        "status": "success",
        "record_id": record_id,
        "selected_strategy_id": chosen.get("strategy_id"),
        "selected_strategy_name": chosen.get("strategy_name"),
        "personalized_business_plan": new_plan,
        "structured_profile": prof
    }


@router.post("/record/{record_id}/apply-scenario", response_model=Dict[str, Any])
def apply_scenario_to_business(
    record_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Applies a confirmed What-If simulation scenario to an official business record.
    Updates the business inputs, re-executes the complete research pipeline 
    (Random Forest Feasibility, SHAP Attribution, Contextual Strategies, TOPSIS Ranking, and Personalized Business Plan),
    and records an audit trail event.
    """
    rec = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not rec or rec.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis record with ID '{record_id}' not found."
        )

    try:
        # Retrieve existing input profile
        existing_input = dict(rec.input_profile) if isinstance(rec.input_profile, dict) else {}
        if not existing_input and rec.structured_profile:
            existing_input = rec.structured_profile.get("business_input", {})

        # Merge modified scenario parameters
        updated_input = {**existing_input}
        for key in ["available_capital_lkr", "monthly_budget_lkr", "expected_customers_per_day", "expected_price_lkr", "loan_amount_lkr"]:
            if key in payload and payload[key] is not None:
                updated_input[key] = payload[key]

        # Re-run complete pipeline with updated inputs
        new_structured_profile = analyze_business(updated_input)
        new_structured_profile["metadata"]["record_id"] = record_id

        feasibility_data = new_structured_profile.get("feasibility_analysis", {})
        new_label = feasibility_data.get("predicted_label", rec.feasibility_label)
        new_conf = feasibility_data.get("confidence_score", rec.confidence_score)

        # Preserve original intake baseline so comparison is never lost
        orig_bl = None
        if rec.structured_profile and isinstance(rec.structured_profile, dict):
            orig_bl = rec.structured_profile.get("original_baseline")
        if not orig_bl:
            created_log = db.query(AnalysisAuditLog).filter(
                AnalysisAuditLog.record_id == record_id,
                AnalysisAuditLog.action == "created"
            ).order_by(AnalysisAuditLog.created_at.asc()).first()
            if created_log and created_log.inputs_snapshot:
                orig_bl = {
                    "business_input": created_log.inputs_snapshot,
                    "confidence_score": created_log.result_score,
                    "feasibility_label": created_log.result_label
                }
            else:
                orig_bl = {
                    "business_input": dict(existing_input),
                    "confidence_score": rec.confidence_score,
                    "feasibility_label": rec.feasibility_label
                }
        new_structured_profile["original_baseline"] = orig_bl

        # Update database record
        rec.feasibility_label = new_label
        rec.confidence_score = new_conf
        rec.input_profile = updated_input
        rec.structured_profile = new_structured_profile
        flag_modified(rec, "input_profile")
        flag_modified(rec, "structured_profile")

        # Record audit trail event
        audit_entry = AnalysisAuditLog(
            user_id=None,
            user_email="analyst@sme360.ai",
            record_id=record_id,
            action="scenario_applied",
            business_name=rec.business_name,
            business_category=rec.business_category,
            district=rec.district,
            result_label=new_label,
            result_score=new_conf,
            inputs_snapshot=updated_input
        )
        db.add(audit_entry)

        db.commit()
        db.refresh(rec)

        return {
            "status": "success",
            "message": "Scenario successfully applied to business record and business plan updated.",
            "record_id": record_id,
            "structured_profile": new_structured_profile
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply scenario: {str(e)}"
        )


@router.get("/audit-logs", tags=["Audit"])
def get_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Retrieves chronological audit trail of business analysis creation, rerun, delete, and restore events.
    """
    query = db.query(AnalysisAuditLog)
    logs = query.order_by(AnalysisAuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "user_email": log.user_email or "analyst@sme360.ai",
            "record_id": log.record_id,
            "action": log.action,
            "business_category": log.business_category,
            "district": log.district,
            "result_label": log.result_label,
            "result_score": log.result_score,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]

