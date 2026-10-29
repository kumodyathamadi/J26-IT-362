"""Tests for the Component 2 profile, guidance, retrieval, and API contracts."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api import component2_routes
from backend.app.compliance.guidance import build_obligation_output
from backend.app.compliance.engine import analyze_compliance
from backend.app.compliance.profile import BusinessContextRequest
from backend.app.compliance.retrieval import _lexical_search, retrieve_evidence
from backend.app.compliance.schemas import (
    ApplicabilityStatus,
    BusinessProfile,
    ComplianceAnalysisResponse,
    ObligationResult,
)
from backend.database import Base, get_db


def test_profile_aliases_and_normalization():
    request = BusinessContextRequest.model_validate(
        {
            "business_type": "Food",
            "ownership_structure": "Sole Proprietorship",
            "number_of_employees": 4,
            "province": "Western",
            "products_services": [" Bread ", "", "Cakes"],
        }
    )

    profile = request.to_rule_engine_profile()
    assert profile.business_type == "food_business"
    assert str(profile.legal_form) == "sole_proprietorship"
    assert str(profile.employee_band) == "1_9"
    assert profile.jurisdiction == "Western Province"
    assert request.to_business_context()["products_services"] == ["Bread", "Cakes"]
    assert request.to_business_context()["location"]["province"] == "Western Province"


def test_profile_context_normalizes_colombo_district_and_preserves_location_details():
    context = BusinessContextRequest(
        business_type="vehicle spare-parts, repair, and reselling businesses",
        location="Colombo 03",
        district="colombo district",
        province="western",
        local_authority="Colombo Municipal Council",
    ).to_business_context()

    assert context["business_type"] == "vehicle_parts_retail"
    assert context["sector"] == "vehicle_parts"
    assert context["location"] == {
        "address": "Colombo 03",
        "district": "Colombo",
        "province": "Western Province",
        "local_authority": "Colombo Municipal Council",
    }


def test_profile_rejects_negative_employee_count():
    with pytest.raises(ValueError):
        BusinessContextRequest(employees=-1)


def test_profile_validation_reports_missing_core_fields():
    request = BusinessContextRequest(business_type="bakery")
    assert request.missing_profile_fields() == [
        "location",
        "ownership",
        "employees",
        "products_services",
        "business_size",
    ]


def test_unsupported_sector_is_not_misreported_as_not_applicable():
    profile = BusinessContextRequest(
        business_type="clothing",
        province="Western Province",
        local_authority="Colombo Municipal Council",
    ).to_rule_engine_profile()

    analysis = analyze_compliance(profile)

    assert analysis.obligations
    assert all(
        item.status == ApplicabilityStatus.NOT_COVERED
        for item in analysis.obligations
    )


@pytest.mark.parametrize(
    ("business_type", "expected_sector"),
    [
        ("food", "food"),
        ("clothing", "clothing"),
        ("salon", "salon"),
        ("vehicle spare-parts, repair, and reselling businesses", "vehicle_parts"),
    ],
)
def test_target_sector_profiles_do_not_turn_draft_rules_into_legal_conclusions(
    business_type: str, expected_sector: str
):
    from backend.app.compliance.guidance import build_guidance

    request = BusinessContextRequest(
        business_type=business_type,
        district="Colombo",
        province="Western Province",
        local_authority="Colombo Municipal Council",
        ownership="sole_proprietorship",
        employees=3,
        products_services=["Representative products or services"],
        business_size="small",
        handles_food=business_type == "food",
        has_physical_premises=True,
    )
    context = request.to_business_context()
    analysis = analyze_compliance(request.to_rule_engine_profile())
    guidance = build_guidance(analysis.obligations, {})

    assert context["sector"] == expected_sector
    assert guidance
    assert all(item["classification"] == "Needs Verification" for item in guidance)
    assert all(item["has_verified_source"] is False for item in guidance)


def test_lexical_fallback_returns_draft_source_chunks(tmp_path: Path, monkeypatch):
    import backend.app.compliance.retrieval as retrieval

    (tmp_path / "food" / "sample.txt").parent.mkdir()
    (tmp_path / "food" / "sample.txt").write_text(
        "[PLACEHOLDER LEGAL TEXT]\nFood business hygiene requirements.",
        encoding="utf-8",
    )
    monkeypatch.setattr(retrieval, "_CORPUS_DIR", tmp_path)
    hits = _lexical_search("food hygiene requirements", top_k=1)

    assert len(hits) == 1
    assert hits[0]["metadata"]["reviewer_status"] == "draft"
    assert hits[0]["metadata"]["contains_placeholder"] is True
    assert hits[0]["metadata"]["corpus_file"] == "food/sample.txt"


def test_retriever_uses_disclosed_local_fallback(monkeypatch):
    import backend.app.compliance.retrieval as retrieval

    def unavailable_vector_search(query, top_k):
        raise ImportError("Vector packages are not installed")

    monkeypatch.setattr(retrieval, "_vector_search", unavailable_vector_search)
    result = retrieve_evidence("Western Province business names registration", top_k=3)

    assert result["mode"] == "lexical_fallback"
    assert result["evidence"]
    assert any(
        hit["metadata"]["source_id"] == "SL-WESTERNPROV-BUSINESSNAMES-1990"
        for hit in result["evidence"]
    )


def test_guidance_does_not_invent_document_checklist():
    result = ObligationResult(
        id="OBL-TEST",
        name="Example registration",
        status=ApplicabilityStatus.CONDITIONAL,
        authority="Example authority",
        jurisdiction="Sri Lanka",
        required_action="Apply for the relevant registration.",
    )
    output = build_obligation_output(result, [])

    assert output["classification"] == "Needs Verification"
    assert output["status"] == "NEEDS_VERIFICATION"
    assert output["required_documents"] == []
    assert output["documents_status"] == "not_listed"
    assert "confirm required documents" in output["documents_notice"].lower()
    assert output["evidence_source"] == []
    assert output["action"] == ""
    assert "verify this candidate requirement" in output["next_action"].lower()


def test_guidance_marks_unverified_document_checklist_as_draft():
    result = ObligationResult(
        id="OBL-TEST",
        name="Example registration",
        status=ApplicabilityStatus.CONDITIONAL,
        authority="Example authority",
        jurisdiction="Sri Lanka",
        required_action="Apply for the relevant registration.",
    )
    output = build_obligation_output(result, [], ["Example application form"])

    assert output["required_documents"] == ["Example application form"]
    assert output["documents_status"] == "draft_unverified"
    assert output["has_verified_source"] is False
    assert output["classification"] == "Needs Verification"
    assert output["action"] == ""
    assert "draft suggestions" in output["documents_notice"].lower()


def test_evaluate_endpoint_returns_guidance_and_persists_evaluation(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    def override_get_db():
        with TestSession() as session:
            yield session

    result = ObligationResult(
        id="OBL-TEST",
        name="Example food registration",
        status=ApplicabilityStatus.CONDITIONAL,
        reason="The source is awaiting verification.",
        authority="Example authority",
        jurisdiction="Western Province",
        required_action="Confirm the current registration requirement.",
    )
    monkeypatch.setattr(
        component2_routes,
        "analyze_compliance",
        lambda profile: ComplianceAnalysisResponse(
            business_profile=profile,
            summary={"conditional": 1},
            obligations=[result],
        ),
    )
    monkeypatch.setattr(
        component2_routes,
        "retrieve_evidence",
        lambda query, top_k: {
            "mode": "lexical_fallback",
            "evidence": [
                {
                    "score": 0.5,
                    "text": "[PLACEHOLDER LEGAL TEXT] example excerpt",
                    "metadata": {
                        "source_id": "SRC-TEST",
                        "source_title": "Example",
                        "authority": "Example authority",
                        "reviewer_status": "draft",
                        "contains_placeholder": True,
                        "url": "",
                    },
                }
            ],
        },
    )
    monkeypatch.setattr(
        component2_routes,
        "retrieve_legal_candidates",
        lambda query, top_k: {
            "mode": "lexical_legal_source_candidates",
            "evidence": [
                {
                    "score": 0.8,
                    "text": "Candidate source excerpt.",
                    "metadata": {
                        "source_id": "SL-C2-PDF-TEST",
                        "source_title": "Filename-derived title",
                        "authority": "",
                        "url": "",
                        "effective_date": "",
                        "page": 4,
                        "reviewer_status": "draft",
                        "verification_status": "needs_verification",
                        "title_is_filename_guess": True,
                        "contains_placeholder": False,
                    },
                }
            ],
        },
    )
    app = FastAPI()
    app.include_router(component2_routes.router)
    app.dependency_overrides[get_db] = override_get_db

    try:
        response = TestClient(app).post(
            "/api/v1/component2/evaluate",
            json={
                "business_type": "bakery",
                "province": "Western Province",
                "local_authority": "Colombo Municipal Council",
                "legal_form": "sole_proprietorship",
                "number_of_employees": 2,
                "products_services": ["Bread"],
                "business_size": "micro",
            },
        )
        with TestSession() as session:
            stored_count = session.query(
                component2_routes.ComplianceEvaluationRecord
            ).count()
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(test_engine)
        test_engine.dispose()

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["business_context"]["employees"] == 2
    assert payload["summary"]["unknown"] == 0
    assert payload["summary"]["needs_verification"] == 1
    assert payload["obligations"][0]["classification"] == "Needs Verification"
    assert payload["obligations"][0]["status"] == "NEEDS_VERIFICATION"
    assert payload["obligations"][0]["has_verified_source"] is False
    assert payload["source_discovery"][0]["page"] == 4
    assert payload["source_discovery"][0]["verification_status"] == "needs_verification"
    assert payload["source_discovery"][0]["title_is_filename_guess"] is True
    assert payload["evaluation_id"]
    assert payload["retrieval_mode"] == "lexical_fallback"
    assert stored_count == 1


def test_real_evaluate_endpoint_integrates_rulebook_retrieval_and_storage(monkeypatch):
    import backend.app.compliance.retrieval as retrieval

    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    def override_get_db():
        with TestSession() as session:
            yield session

    monkeypatch.setattr(
        retrieval,
        "_vector_search",
        lambda query, top_k: (_ for _ in ()).throw(
            ImportError("Use local lexical retrieval in this test")
        ),
    )
    app = FastAPI()
    app.include_router(component2_routes.router)
    app.dependency_overrides[get_db] = override_get_db

    try:
        response = TestClient(app).post(
            "/api/v1/component2/evaluate",
            json={
                "business_type": "bakery",
                "sector": "food",
                "location": "Colombo 03",
                "province": "Western Province",
                "district": "Colombo",
                "local_authority": "Colombo Municipal Council",
                "ownership": "sole_proprietorship",
                "employees": 4,
                "products_services": ["Bread", "Cakes"],
                "business_size": "small",
                "has_physical_premises": True,
                "handles_food": True,
                "is_manufacturing": True,
                "is_importing": False,
            },
        )
        with TestSession() as session:
            stored_count = session.query(
                component2_routes.ComplianceEvaluationRecord
            ).count()
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(test_engine)
        test_engine.dispose()

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["business_context"] == {
        "business_type": "bakery",
        "sector": "food",
        "location": {
            "address": "Colombo 03",
            "district": "Colombo",
            "province": "Western Province",
            "local_authority": "Colombo Municipal Council",
        },
        "ownership": "sole_proprietorship",
        "employees": 4,
        "products_services": ["Bread", "Cakes"],
        "activities": [],
        "business_size": "small",
        "premises": {"has_physical_premises": True},
        "operational_characteristics": {
            "handles_food": True,
            "is_manufacturing": True,
            "is_importing": False,
            "serves_cooked_food": None,
            "sells_alcohol": None,
            "uses_chemicals_or_cosmetics": None,
            "handles_waste_oil_or_batteries": None,
            "turnover_band": None,
        },
    }
    assert payload["retrieval_mode"] == "lexical_fallback"
    assert payload["summary"]["total"] == 7
    assert payload["summary"]["needs_verification"] == 7
    assert payload["summary"]["unknown"] == 0
    assert stored_count == 1

    business_name_rule = next(
        item for item in payload["obligations"] if item["obligation_id"] == "OBL-001"
    )
    assert business_name_rule["classification"] == "Needs Verification"
    assert business_name_rule["evidence_source"]
    assert business_name_rule["evidence_source"][0]["source_id"] == (
        "SL-WESTERNPROV-BUSINESSNAMES-1990"
    )
    assert business_name_rule["has_verified_source"] is False
