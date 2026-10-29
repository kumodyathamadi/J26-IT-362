"""Context-aware regulatory analysis and guidance API for Component 2."""

from __future__ import annotations

import logging
import os
import base64
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.compliance.engine import analyze_compliance
from backend.app.compliance.guidance import build_obligation_output, build_guidance
from backend.app.compliance.legal_sources import (
    LegalSourceIngestionResult,
    LegalSourceMetadata,
    LegalSourceInventory,
    PdfExtractionUnavailable,
    get_legal_source_inventory,
    ingest_legal_sources,
)
from backend.app.compliance.profile import BusinessContextRequest
from backend.app.compliance.retrieval import (
    retrieve_evidence,
    retrieve_legal_candidates,
)
from backend.app.compliance.rulebook_loader import get_obligations
from backend.database import get_db
from backend.models import ComplianceEvaluationRecord
from engine.questions import generate_follow_up_questions
from backend.app.compliance.action_predictor import (
    predict_action_roadmap,
    predict_action_for_rule,
    build_registration_guidance,
)
from backend.app.compliance.br_form_generator import generate_br_application_pdf
from backend.app.compliance.stage_form_generator import generate_stage_form_pdf
from backend.app.compliance.dossier_generator import generate_compliance_dossier_pdf
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/component2",
    tags=["Component 2 - Registration & Compliance"],
)


class Component2EvidenceSource(BaseModel):
    source_id: str
    title: Optional[str] = None
    authority: Optional[str] = None
    excerpt: str
    url: Optional[str] = None
    effective_date: Optional[str] = None
    retrieval_score: Optional[float] = None
    page: Optional[int] = None
    reviewer_status: str
    contains_placeholder: bool
    verification_status: Optional[str] = None
    title_is_filename_guess: bool = False
    section_reference: Optional[str] = None
    paragraph_number: Optional[int] = None
    file_type: Optional[str] = None
    source_file: Optional[str] = None
    action_guidance: Optional[Dict[str, Any]] = None


class Component2Obligation(BaseModel):
    obligation_id: str
    obligation: str
    title: str
    classification: Literal[
        "Mandatory", "Conditional", "Not Applicable", "Needs Verification"
    ]
    priority: Literal["high", "review", "none"]
    status: Literal[
        "APPLICABLE", "UNKNOWN", "NOT_APPLICABLE", "NEEDS_VERIFICATION"
    ]
    authority: str
    jurisdiction: str
    source_reference: Optional[Dict[str, Any]] = None
    source_id: str
    source_paragraph: str
    source_text: str
    explanation: str
    action: str
    triggering_facts: Dict[str, Any]
    applicability_conditions: Dict[str, Any]
    exceptions: List[Dict[str, Any]]
    missing_facts: List[str]
    required_documents: List[str]
    documents_needed: List[str]
    documents_status: str
    documents_notice: Optional[str] = None
    registration_steps: List[str]
    next_action: str
    evidence_source: List[Component2EvidenceSource]
    verification_status: str
    has_verified_source: bool


class Component2ProfileValidation(BaseModel):
    complete: bool
    missing_required_fields: List[str]
    note: str


class Component2EvaluationResponse(BaseModel):
    evaluation_id: str
    business_context: Dict[str, Any]
    profile_validation: Component2ProfileValidation
    summary: Dict[str, int]
    obligations: List[Component2Obligation]
    guidance: List[Component2Obligation]
    source_discovery: List[Component2EvidenceSource] = Field(default_factory=list)
    source_discovery_mode: str = "lexical_legal_source_candidates"
    action_roadmap: Optional[Dict[str, Any]] = None
    registration_guidance: Optional[Dict[str, Any]] = None
    follow_up_questions: List[Dict[str, Any]]
    retrieval_mode: str
    disclaimer: str = (
        "This is preliminary decision-support guidance, not legal advice. "
        "Applicability is determined by the rule engine, not by an LLM. "
        "The current corpus contains draft or placeholder material; verify all "
        "requirements with the responsible Sri Lankan authority."
    )


@router.get(
    "/sources",
    response_model=LegalSourceInventory,
    response_model_exclude={"sources": {"__all__": {"processed_text_path"}}},
)
def list_legal_source_inventory() -> LegalSourceInventory:
    """List discovered legal sources and their extraction/verification state."""
    try:
        return get_legal_source_inventory()
    except (OSError, ValueError) as exc:
        logger.exception("Could not read Component 2 legal-source inventory")
        raise HTTPException(
            status_code=503,
            detail="The legal-source inventory could not be read.",
        ) from exc


@router.post(
    "/sources/ingest",
    response_model=LegalSourceIngestionResult,
    response_model_exclude={"sources": {"__all__": {"processed_text_path"}}},
)
def ingest_legal_source_documents(
    force: bool = Query(
        default=False,
        description="Re-extract unchanged files when true.",
    ),
) -> LegalSourceIngestionResult:
    """Ingest configured PDF and TXT sources; originals are read-only."""
    try:
        return ingest_legal_sources(force=force)
    except PdfExtractionUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (OSError, ValueError) as exc:
        logger.exception("Could not ingest Component 2 legal sources")
        raise HTTPException(
            status_code=503,
            detail="Legal-source ingestion failed; inspect the server log for details.",
        ) from exc


@router.get(
    "/sources/{source_id}",
    response_model=LegalSourceMetadata,
    response_model_exclude={"processed_text_path"},
)
def get_legal_source(source_id: str) -> LegalSourceMetadata:
    """Return metadata and processing state for one inventoried source."""
    try:
        source = next(
            (
                item
                for item in get_legal_source_inventory().sources
                if item.source_id == source_id
            ),
            None,
        )
    except (OSError, ValueError) as exc:
        logger.exception("Could not read Component 2 legal-source inventory")
        raise HTTPException(
            status_code=503,
            detail="The legal-source inventory could not be read.",
        ) from exc
    if source is None:
        raise HTTPException(status_code=404, detail="Legal source not found.")
    return source


@router.get("/sources/{source_id}/evidence")
def get_legal_source_evidence(
    source_id: str,
    query: str = Query(min_length=1, max_length=500),
    limit: int = Query(default=5, ge=1, le=10),
) -> Dict[str, Any]:
    """Search extracted excerpts from one known source without opening file paths."""
    get_legal_source(source_id)
    try:
        result = retrieve_legal_candidates(query, top_k=limit, source_id=source_id)
    except (FileNotFoundError, RuntimeError) as exc:
        logger.exception("Could not retrieve evidence for source %s", source_id)
        raise HTTPException(
            status_code=503,
            detail="Evidence for this legal source is unavailable.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result


@router.post("/evaluate", response_model=Component2EvaluationResponse)
@router.post("/analyze", response_model=Component2EvaluationResponse, include_in_schema=False)
def evaluate_compliance(
    request: BusinessContextRequest,
    db: Session = Depends(get_db),
) -> Component2EvaluationResponse:
    """Normalize a business profile, classify rulebook obligations, retrieve evidence, and log."""
    context = request.to_business_context()
    missing_profile_fields = request.missing_profile_fields()
    try:
        analysis = analyze_compliance(request.to_rule_engine_profile())
        evidence_by_obligation: Dict[str, List[Dict[str, Any]]] = {}
        retrieval_modes = set()

        for result in analysis.obligations:
            query = " ".join(
                part
                for part in (
                    result.name,
                    result.required_action,
                    request.sector,
                    request.business_type,
                    " ".join(request.products_services),
                    " ".join(request.activities),
                    request.local_authority,
                    request.province,
                )
                if part
            )
            retrieved = retrieve_evidence(query, top_k=3)
            retrieval_modes.add(retrieved["mode"])
            evidence_by_obligation[result.id] = retrieved["evidence"]

        discovery_query = " ".join(
            part
            for part in (
                request.business_type,
                request.sector,
                request.district,
                request.province,
                request.local_authority,
                " ".join(request.products_services),
                " ".join(request.activities),
            )
            if part
        )
        candidate_result = (
            retrieve_legal_candidates(discovery_query, top_k=5)
            if discovery_query
            else {"evidence": []}
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (ImportError, RuntimeError) as exc:
        logger.exception("Component 2 retrieval is unavailable")
        raise HTTPException(
            status_code=503,
            detail=f"Regulatory evidence retrieval is unavailable: {exc}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    documents_by_obligation = {
        rule.id: rule.required_documents for rule in get_obligations()
    }
    obligation_outputs = [
        build_obligation_output(
            result,
            evidence_by_obligation.get(result.id, []),
            documents_by_obligation.get(result.id, []),
        )
        for result in analysis.obligations
    ]
    guidance_outputs = build_guidance(
        analysis.obligations, evidence_by_obligation, documents_by_obligation
    )
    source_discovery = [
        {
            "source_id": item["metadata"]["source_id"],
            "title": item["metadata"]["source_title"],
            "authority": item["metadata"]["authority"] or None,
            "excerpt": item["text"],
            "url": item["metadata"]["url"] or None,
            "effective_date": item["metadata"]["effective_date"] or None,
            "retrieval_score": item["score"],
            "page": item["metadata"].get("page"),
            "section_reference": item["metadata"].get("section_reference"),
            "paragraph_number": item["metadata"].get("paragraph_number"),
            "file_type": item["metadata"].get("file_type"),
            "source_file": item["metadata"].get("corpus_file"),
            "reviewer_status": item["metadata"]["reviewer_status"],
            "contains_placeholder": item["metadata"]["contains_placeholder"],
            "verification_status": item["metadata"]["verification_status"],
            "title_is_filename_guess": item["metadata"]["title_is_filename_guess"],
            "action_guidance": predict_action_for_rule(
                rule_title=item["metadata"].get("source_title") or "",
                source_id=item["metadata"].get("source_id") or "",
                excerpt=item.get("text") or "",
                business_context=context,
            ),
        }
        for item in candidate_result["evidence"]
    ]
    summary = {
        "total": len(obligation_outputs),
        "applicable": sum(
            result["classification"] == "Mandatory"
            for result in obligation_outputs
        ),
        "not_applicable": sum(
            result["classification"] == "Not Applicable"
            for result in obligation_outputs
        ),
        "unknown": sum(
            result["classification"] == "Conditional"
            for result in obligation_outputs
        ),
        "needs_verification": sum(
            result["classification"] == "Needs Verification"
            for result in obligation_outputs
        ),
    }

    missing_facts = list(
        dict.fromkeys(
            fact
            for result in analysis.obligations
            if result.missing_facts
            for fact in result.missing_facts
        )
    )
    action_roadmap = predict_action_roadmap(context)

    response_data = {
        "evaluation_id": "",
        "business_context": context,
        "profile_validation": {
            "complete": not missing_profile_fields,
            "missing_required_fields": missing_profile_fields,
            "note": (
                "Partial profiles are accepted; omitted facts remain unknown "
                "and may result in conditional classifications."
            ),
        },
        "summary": summary,
        "obligations": obligation_outputs,
        "guidance": guidance_outputs,
        "action_roadmap": action_roadmap,
        "registration_guidance": build_registration_guidance(context),
        "source_discovery": source_discovery,
        "source_discovery_mode": candidate_result.get(
            "mode", "lexical_legal_source_candidates"
        ),
        "follow_up_questions": generate_follow_up_questions(missing_facts),
        "retrieval_mode": (
            next(iter(retrieval_modes))
            if len(retrieval_modes) == 1
            else "mixed"
        ),
    }

    try:
        record = ComplianceEvaluationRecord(
            business_context=context,
            result=response_data,
            retrieval_mode=response_data["retrieval_mode"],
        )
        db.add(record)
        db.flush()
        response_data["evaluation_id"] = record.id
        record.result = response_data
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Could not persist Component 2 evaluation")
        raise HTTPException(
            status_code=503,
            detail="The compliance evaluation could not be recorded.",
        ) from exc

    return Component2EvaluationResponse.model_validate(response_data)


# ---------------------------------------------------------------------------
# Business / Growth Plan PDF Ingestion & Profile Extraction Endpoints
# ---------------------------------------------------------------------------

from backend.app.compliance.plan_pdf_extractor import (
    extract_text_from_pdf_bytes,
    extract_business_profile_from_text,
)

SAMPLE_PLANS_DIR = Path(__file__).resolve().parents[3] / "data" / "sample_plans"

SAMPLE_PLANS_METADATA = [
    {
        "id": "freshmart_grocery",
        "title": "FreshMart Grocery",
        "category": "Grocery / Mini-Mart",
        "sector": "food",
        "stage": "Existing Business",
        "location": "Colombo, Western Province",
        "strategy": "Online Ordering & Delivery Expansion",
        "filename": "FreshMart_Grocery_Business_Plan.pdf",
        "description": "Established grocery store executing multi-channel delivery and local expansion in Colombo.",
    },
    {
        "id": "trendy_style_clothing",
        "title": "Trendy Style Clothing Shop",
        "category": "Clothing / Garment",
        "sector": "clothing",
        "stage": "New Startup",
        "location": "Colombo, Western Province",
        "strategy": "Storefront + Home Delivery Model",
        "filename": "Trendy_Style_Clothing_Shop_Business_Plan.pdf",
        "description": "New fashion retail startup offering trendy clothing with storefront setup and WhatsApp delivery.",
    },
]


class Base64PdfRequest(BaseModel):
    filename: str = "business_plan.pdf"
    file_base64: str


class PdfExtractionResponse(BaseModel):
    success: bool
    filename: str
    pages_count: int
    is_scanned: bool
    ocr_used: bool
    character_count: int
    extracted_profile: Dict[str, Any]
    metadata: Dict[str, Any]
    raw_text_preview: str


@router.post("/extract-plan-pdf", response_model=PdfExtractionResponse)
async def extract_plan_pdf(file: UploadFile = File(...)) -> PdfExtractionResponse:
    """
    Step 2 & 3: Uploads a Business / Growth Plan PDF, extracts text (including OCR if scanned),
    and identifies a structured business profile for user confirmation in Component 2.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF document.")

    try:
        pdf_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read uploaded PDF file: {exc}")

    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded PDF file is empty.")

    try:
        full_text, pages, is_scanned, ocr_used = extract_text_from_pdf_bytes(pdf_bytes)
        result = extract_business_profile_from_text(full_text, file.filename)
    except Exception as exc:
        logger.exception("Failed to extract business profile from PDF")
        raise HTTPException(
            status_code=500, detail=f"Failed to process and extract PDF: {str(exc)}"
        )

    return PdfExtractionResponse(
        success=True,
        filename=file.filename,
        pages_count=len(pages),
        is_scanned=is_scanned,
        ocr_used=ocr_used,
        character_count=len(full_text),
        extracted_profile=result["profile"],
        metadata=result["metadata"],
        raw_text_preview=full_text[:800],
    )


@router.post("/extract-plan-base64", response_model=PdfExtractionResponse)
def extract_plan_base64(payload: Base64PdfRequest) -> PdfExtractionResponse:
    """
    Accepts base64 encoded PDF payload, extracts text and structured business profile.
    """
    try:
        # Strip data URL prefix if present
        raw_b64 = payload.file_base64
        if "base64," in raw_b64:
            raw_b64 = raw_b64.split("base64,")[1]
        pdf_bytes = base64.b64decode(raw_b64)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid base64 payload: {exc}")

    try:
        full_text, pages, is_scanned, ocr_used = extract_text_from_pdf_bytes(pdf_bytes)
        result = extract_business_profile_from_text(full_text, payload.filename)
    except Exception as exc:
        logger.exception("Failed to extract business profile from base64 PDF")
        raise HTTPException(
            status_code=500, detail=f"Failed to process and extract PDF: {str(exc)}"
        )

    return PdfExtractionResponse(
        success=True,
        filename=payload.filename,
        pages_count=len(pages),
        is_scanned=is_scanned,
        ocr_used=ocr_used,
        character_count=len(full_text),
        extracted_profile=result["profile"],
        metadata=result["metadata"],
        raw_text_preview=full_text[:800],
    )


@router.get("/sample-plans")
def list_sample_plans() -> List[Dict[str, Any]]:
    """Returns metadata for built-in sample business plan PDFs."""
    return SAMPLE_PLANS_METADATA


@router.get("/sample-plans/{sample_id}/download-pdf")
def download_sample_plan_pdf(sample_id: str) -> Response:
    """Downloads one of the built-in sample business plan PDFs."""
    match = next((item for item in SAMPLE_PLANS_METADATA if item["id"] == sample_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Sample business plan not found.")

    file_path = SAMPLE_PLANS_DIR / match["filename"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample PDF file not found on disk.")

    with open(file_path, "rb") as fh:
        pdf_bytes = fh.read()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{match["filename"]}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get("/sample-plans/{sample_id}/extract", response_model=PdfExtractionResponse)
def extract_sample_plan(sample_id: str) -> PdfExtractionResponse:
    """Directly extracts and returns the business profile from a sample PDF."""
    match = next((item for item in SAMPLE_PLANS_METADATA if item["id"] == sample_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Sample business plan not found.")

    file_path = SAMPLE_PLANS_DIR / match["filename"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample PDF file not found on disk.")

    with open(file_path, "rb") as fh:
        pdf_bytes = fh.read()

    full_text, pages, is_scanned, ocr_used = extract_text_from_pdf_bytes(pdf_bytes)
    result = extract_business_profile_from_text(full_text, match["filename"])

    return PdfExtractionResponse(
        success=True,
        filename=match["filename"],
        pages_count=len(pages),
        is_scanned=is_scanned,
        ocr_used=ocr_used,
        character_count=len(full_text),
        extracted_profile=result["profile"],
        metadata=result["metadata"],
        raw_text_preview=full_text[:800],
    )


class BrFormGenerationRequest(BaseModel):
    business_name: Optional[str] = "CEYLON GREEN ESSENTIALS"
    legal_form: Optional[str] = "sole_proprietorship"
    sector: Optional[str] = "Food Manufacturing & Processing"
    business_type: Optional[str] = None
    district: Optional[str] = "Gampaha"
    province: Optional[str] = "Western Province"
    local_authority: Optional[str] = None
    divisional_secretariat: Optional[str] = None
    grama_niladhari: Optional[str] = None
    address: Optional[str] = None
    activities: List[str] = Field(default_factory=list)
    products_services: List[str] = Field(default_factory=list)
    employee_count: Optional[int] = 15
    revenue: Optional[float] = 3500000.0
    initial_capital: Optional[float] = None
    owner_name: Optional[str] = "Dhananjaya Bandara"
    owner_nic: Optional[str] = "199415802345"
    phone: Optional[str] = "+94 77 123 4567"
    email: Optional[str] = "applicant.business@sme.lk"
    residence_address: Optional[str] = None
    commencement_date: Optional[str] = None


@router.post("/generate-br-form")
def generate_business_registration_form(payload: BrFormGenerationRequest) -> Response:
    """
    Generates an auto-filled Official Sri Lanka Business Registration (BR) Form (Form 1)
    as a downloadable PDF document based on user-provided or extracted business profile.
    """
    try:
        data = payload.model_dump()
        pdf_bytes = generate_br_application_pdf(data)
        safe_name = "".join(c for c in (payload.business_name or "Business") if c.isalnum() or c in ("-", "_")).strip()
        filename = f"BR_Application_Form1_{safe_name or 'Business'}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except Exception as exc:
        logger.exception("Failed to generate BR Application Form PDF: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to generate application form: {str(exc)}")


@router.post("/generate-stage-form")
def generate_stage_form_endpoint(payload: Dict[str, Any]) -> Response:
    """
    Generates an official Sri Lankan statutory registration form PDF
    tailored to the requested stage (1, 2, 3, 4, or 5).
    """
    try:
        stage = int(payload.get("stage", 1))
        pdf_bytes = generate_stage_form_pdf(stage, payload)
        b_name = payload.get("business_name", "Business")
        safe_name = "".join(c for c in b_name if c.isalnum() or c in ("-", "_")).strip() or "Business"

        filenames = {
            1: f"WP_BN_01_Name_Search_Clearance_{safe_name}.pdf",
            2: f"Grama_Niladhari_Report_{safe_name}.pdf",
            3: f"BR_Application_Form1_{safe_name}.pdf",
            4: f"Municipal_Trade_License_Application_{safe_name}.pdf",
            5: f"RAMIS_TIN_Labour_FormD_{safe_name}.pdf",
        }
        filename = filenames.get(stage, f"Stage_{stage}_Statutory_Form_{safe_name}.pdf")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except Exception as exc:
        logger.exception("Failed to generate stage form PDF: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to generate stage {payload.get('stage')} form: {str(exc)}")


@router.get("/generate-stage-form/download")
def download_stage_form_get(
    stage: int = Query(1, ge=1, le=5),
    business_name: str = "CEYLON ARTISAN BAKEHOUSE",
    district: str = "Colombo",
) -> Response:
    """GET endpoint to easily download or test stage-specific PDF forms."""
    sample_payload = {
        "stage": stage,
        "business_name": business_name,
        "district": district,
        "legal_form": "sole_proprietorship",
        "divisional_secretariat": f"{district} Divisional Secretariat",
        "grama_niladhari": f"{district} Central (GN Division 512)",
        "local_authority": f"{district} Municipal Council",
    }
    return generate_stage_form_endpoint(sample_payload)


@router.get("/sample-br-form/download")
def download_sample_br_form(
    business_name: str = "CEYLON GREEN ESSENTIALS",
    legal_form: str = "sole_proprietorship",
    district: str = "Gampaha",
) -> Response:
    """Downloads an official sample auto-filled Business Registration Form 1 PDF."""
    sample_data = {
        "business_name": business_name,
        "legal_form": legal_form,
        "district": district,
        "sector": "Food Manufacturing & Processing",
        "employee_count": 15,
        "revenue": 3500000.0,
    }
    pdf_bytes = generate_br_application_pdf(sample_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="Sample_BR_Form1_{district}.pdf"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get("/legal-documents/{document_query}")
def get_official_legal_document(document_query: str) -> FileResponse:
    """
    Retrieves and streams an authentic, official Sri Lankan legal statute,
    provincial gazette, or prescribed application form PDF from the legal corpus.
    """
    legal_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "compliance", "raw", "Component2_Legal_Sources")
    )
    query_clean = document_query.lower().replace("-", " ").replace("_", " ").replace(".pdf", "")
    
    canonical_map = {
        "wp_bn_1990": "Act-7-of-2007-English.pdf",
        "companies_act": "Act-7-of-2007-English.pdf",
        "food_act": "food_act_no26_1980_en.pdf",
        "food_policy": "National_Food_Safety_Policy.pdf",
        "environmental_act": "1.National_Environmental_Act_No._47_of_1980.pdf",
        "motor_traffic": "garaj_application_2023e.pdf",
        "cosmetics": "INFORMATION REQUIRED FOR REGISTRATION OF A COSMETIC..pdf",
        "data_protection": "Data Protection Act SL - English (2).pdf",
    }
    
    target_file = canonical_map.get(document_query.lower())

    matched_path = None
    for root, _, files in os.walk(legal_dir):
        for f in files:
            if not f.lower().endswith(".pdf"):
                continue
            if target_file and f.lower() == target_file.lower():
                matched_path = os.path.join(root, f)
                break
            f_clean = f.lower().replace("-", " ").replace("_", " ").replace(".pdf", "")
            if query_clean in f_clean or f_clean in query_clean:
                matched_path = os.path.join(root, f)
                break
        if matched_path:
            break

    if not matched_path or not os.path.exists(matched_path):
        default_path = os.path.join(legal_dir, "01_Common_Business_Registration", "Act-7-of-2007-English.pdf")
        if os.path.exists(default_path):
            matched_path = default_path
        else:
            raise HTTPException(status_code=404, detail="Legal document PDF not found.")

    filename = os.path.basename(matched_path)
    return FileResponse(
        path=matched_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.post("/download-compliance-dossier")
def download_compliance_dossier(payload: Dict[str, Any]) -> Response:
    """
    Generates and downloads the comprehensive, publication-grade SME Legal Compliance
    & Business Registration Guidance Dossier as an official PDF document.
    """
    try:
        pdf_bytes = generate_compliance_dossier_pdf(payload)
        district = payload.get("business_context", {}).get("district") or payload.get("registration_guidance", {}).get("district") or "Western_Province"
        filename = f"SME_Compliance_Registration_Dossier_{district}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except Exception as exc:
        logger.exception("Failed to generate compliance dossier PDF: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to generate compliance dossier: {str(exc)}")


