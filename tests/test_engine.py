"""
Component 2 — Three-Valued Logic Rule Engine Unit Tests
Covers:
  - Test 1: Food business with complete details -> Common and Food obligations return APPLICABLE.
  - Test 2: Food business where 'operates_kitchen' is None -> Returns UNKNOWN with 'operates_kitchen' in missing_facts.
  - Test 3: Salon business -> Food obligations are ignored/NOT_APPLICABLE, Salon obligations evaluated.
  - Test 4: End-to-End FastAPI POST /api/compliance/evaluate endpoint validation.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from engine.schemas import BusinessProfileInput, LocationSchema
from engine.evaluate import evaluate_compliance, evaluate_obligation
from engine.loader import load_rulebook
from backend.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Test 1: Food business with complete details -> Common and Food return APPLICABLE
# ---------------------------------------------------------------------------
def test_food_business_complete_applicable():
    """
    Given a food business in Western Province with all facts known
    (physical premises, commercial kitchen, 3 employees, sole proprietorship),
    all applicable common and food obligations must evaluate to APPLICABLE.
    """
    profile = {
        "business_id": "BIZ-FOOD-001",
        "business_type": "food",
        "sub_activity": ["bakery", "pastry"],
        "location": {
            "province": "Western Province",
            "district": "Colombo",
            "local_authority": "Colombo Municipal Council",
        },
        "legal_structure": "sole_proprietorship",
        "employee_count": 3,
        "physical_premises": True,
        "operates_kitchen": True,
        "sells_alcohol": False,
        "imports_goods": False,
    }

    # Evaluate with layer filtering (common + food)
    results = evaluate_compliance(profile, filter_by_layer=True)

    status_by_id = {r["obligation_id"]: r["status"] for r in results}

    # Common obligations
    assert "OBL-COMMON-001" in status_by_id
    assert status_by_id["OBL-COMMON-001"] == "APPLICABLE"
    assert "OBL-COMMON-002" in status_by_id
    assert status_by_id["OBL-COMMON-002"] == "APPLICABLE"

    # Food obligations
    assert "OBL-FOOD-001" in status_by_id
    assert status_by_id["OBL-FOOD-001"] == "APPLICABLE"
    assert "OBL-FOOD-002" in status_by_id
    assert status_by_id["OBL-FOOD-002"] == "APPLICABLE"

    # Verify no missing facts for applicable obligations
    for r in results:
        if r["status"] == "APPLICABLE":
            assert len(r["missing_facts"]) == 0
            assert len(r["triggering_facts"]) > 0


# ---------------------------------------------------------------------------
# Test 2: Food business where operates_kitchen is None -> Returns UNKNOWN
# ---------------------------------------------------------------------------
def test_food_business_missing_operates_kitchen_unknown():
    """
    Given a food business profile where 'operates_kitchen' is None (Unknown),
    the Food Premises Hygiene Licence (OBL-FOOD-001) must evaluate to UNKNOWN,
    and 'operates_kitchen' must be reported in missing_facts.
    """
    profile = {
        "business_id": "BIZ-FOOD-002",
        "business_type": "food",
        "sub_activity": ["cafeteria"],
        "location": {
            "province": "Western Province",
            "district": "Colombo",
            "local_authority": "Colombo Municipal Council",
        },
        "legal_structure": "sole_proprietorship",
        "employee_count": 2,
        "physical_premises": True,
        "operates_kitchen": None,  # Missing fact -> Unknown in 3-valued Kleene logic
        "sells_alcohol": False,
        "imports_goods": False,
    }

    results = evaluate_compliance(profile, filter_by_layer=True)
    food_obl_1 = next(r for r in results if r["obligation_id"] == "OBL-FOOD-001")

    assert food_obl_1["status"] == "UNKNOWN"
    assert "operates_kitchen" in food_obl_1["missing_facts"]


# ---------------------------------------------------------------------------
# Test 3: Salon business -> Food obligations are ignored/NOT_APPLICABLE, Salon evaluated
# ---------------------------------------------------------------------------
def test_salon_business_filters_food_evaluates_salon():
    """
    Given a salon business profile:
    1. With filter_by_layer=True, Food obligations are ignored (not evaluated).
    2. Without layer filtering, Food obligations evaluate to NOT_APPLICABLE.
    3. The Salon obligation (OBL-SALON-001) evaluates to APPLICABLE when conditions met.
    """
    profile = {
        "business_id": "BIZ-SALON-001",
        "business_type": "salon",
        "sub_activity": ["hair_styling", "skin_care"],
        "location": {
            "province": "Western Province",
            "district": "Colombo",
            "local_authority": "Colombo Municipal Council",
        },
        "legal_structure": "sole_proprietorship",
        "employee_count": 2,
        "physical_premises": True,
        "uses_chemicals_or_cosmetics": True,
    }

    # 1. Scoped evaluation (layer filtering active)
    scoped_results = evaluate_compliance(profile, filter_by_layer=True)
    scoped_ids = [r["obligation_id"] for r in scoped_results]

    # Food obligations are ignored / excluded from scoped evaluation
    assert "OBL-FOOD-001" not in scoped_ids
    assert "OBL-FOOD-002" not in scoped_ids

    # Common and Salon obligations are evaluated
    assert "OBL-COMMON-001" in scoped_ids
    assert "OBL-SALON-001" in scoped_ids
    salon_obl = next(r for r in scoped_results if r["obligation_id"] == "OBL-SALON-001")
    assert salon_obl["status"] == "APPLICABLE"

    # 2. Unfiltered evaluation: Food obligations evaluate to NOT_APPLICABLE
    all_results = evaluate_compliance(profile, filter_by_layer=False)
    food_obl = next(r for r in all_results if r["obligation_id"] == "OBL-FOOD-001")
    assert food_obl["status"] == "NOT_APPLICABLE"


# ---------------------------------------------------------------------------
# Test 4: FastAPI Endpoint POST /api/compliance/evaluate
# ---------------------------------------------------------------------------
def test_api_compliance_evaluate_endpoint():
    """
    Tests the FastAPI REST endpoint directly with Component 1 profile payload.
    """
    payload = {
        "business_id": "BIZ-TEST-999",
        "business_type": "food",
        "sub_activity": ["restaurant"],
        "location": {
            "province": "Western Province",
            "district": "Colombo",
            "local_authority": "Colombo Municipal Council",
        },
        "legal_structure": "sole_proprietorship",
        "employee_count": 4,
        "physical_premises": True,
        "operates_kitchen": None,  # Triggers follow-up question
        "sells_alcohol": False,
        "imports_goods": False,
    }

    response = client.post("/api/compliance/evaluate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["business_id"] == "BIZ-TEST-999"
    assert data["business_type"] == "food"

    # Summary checks
    assert data["summary"]["applicable_count"] >= 3  # Common 1, Common 2, Food 2
    assert data["summary"]["unknown_count"] >= 1     # Food 1 (operates_kitchen is None)

    # Grouped obligations check
    assert len(data["grouped_obligations"]["applicable"]) >= 3
    assert len(data["grouped_obligations"]["unknown"]) >= 1

    # Follow-up question check
    questions = data["follow_up_questions"]
    assert len(questions) >= 1
    operates_kitchen_q = next((q for q in questions if q["fact"] == "operates_kitchen"), None)
    assert operates_kitchen_q is not None
    assert operates_kitchen_q["type"] == "boolean"
    assert len(operates_kitchen_q["question"]) > 0
