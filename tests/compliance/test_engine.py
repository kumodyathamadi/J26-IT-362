"""
Component 2 — Applicability Engine Tests

Tests cover:
  1. All-blank profile returns ZERO Applicable or Not Identified results (all UNKNOWN or NOT_COVERED).
  2. For EACH of the 7 rules:
     - 1 test for TRUE / triggered condition
     - 1 test for FALSE condition (giving NOT_IDENTIFIED with reason)
     - 1 test for UNKNOWN condition (missing fact, never defaults to false)
  3. Reason string verification for NOT_IDENTIFIED (e.g. 'Employees = 0')
  4. Scope guard verification (e.g. Kandy / Central Province)
"""

import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.compliance.schemas import (
    ApplicabilityStatus,
    BusinessProfile,
    EmployeeBand,
    LegalForm,
)
from backend.app.compliance.engine import evaluate_rule, analyze_compliance, is_in_scope
from backend.app.compliance.rulebook_loader import get_obligations


@pytest.fixture
def empty_profile():
    """All-blank profile where every field is None."""
    return BusinessProfile()


@pytest.fixture
def all_obligations():
    return {o.id: o for o in get_obligations()}


# ---------------------------------------------------------------------------
# Requirement 1: All-blank profile must give ZERO Applicable results
# ---------------------------------------------------------------------------
def test_all_blank_profile_gives_zero_applicable(empty_profile):
    res = analyze_compliance(empty_profile)
    applicable_count = res.summary.get("applicable", 0)
    not_identified_count = res.summary.get("not_identified", 0)

    assert applicable_count == 0, f"Expected 0 applicable for all-blank profile, got {applicable_count}"
    assert not_identified_count == 0, f"Expected 0 not_identified for all-blank profile, got {not_identified_count}"
    # All obligations must be UNKNOWN
    for obl in res.obligations:
        assert obl.status == ApplicabilityStatus.UNKNOWN, (
            f"{obl.id} should be UNKNOWN on blank profile, got {obl.status}"
        )
        assert len(obl.missing_facts) > 0


# ---------------------------------------------------------------------------
# Requirement 2: Rule-by-rule True, False, and Unknown tests
# ---------------------------------------------------------------------------

# OBL-001: Business Name Registration
class TestOBL001BusinessNames:
    def test_true_condition(self, all_obligations):
        rule = all_obligations["OBL-001"]
        prof = BusinessProfile(
            business_type="bakery",
            has_physical_premises=True,
            jurisdiction="Western Province",
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        # Has unconfirmed exception (sole proprietors using full name), so CONDITIONAL
        assert status == ApplicabilityStatus.CONDITIONAL
        assert tf["business_type"] is True
        assert tf["has_physical_premises"] is True
        assert tf["jurisdiction"] is True

    def test_false_condition(self, all_obligations):
        rule = all_obligations["OBL-001"]
        prof = BusinessProfile(
            business_type="bakery",
            has_physical_premises=False,  # False trigger
            jurisdiction="Western Province",
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.NOT_IDENTIFIED
        assert "physical premises" in reason.lower()

    def test_unknown_condition(self, all_obligations):
        rule = all_obligations["OBL-001"]
        prof = BusinessProfile(
            business_type="bakery",
            has_physical_premises=True,
            # jurisdiction is None -> unknown
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.UNKNOWN
        assert "jurisdiction" in mf


# OBL-002: CMC Trade Licence
class TestOBL002TradeLicence:
    def test_true_condition(self, all_obligations):
        rule = all_obligations["OBL-002"]
        prof = BusinessProfile(
            business_type="bakery",
            has_physical_premises=True,
            local_authority="Colombo Municipal Council",
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        # Note: reviewer_status is draft and quote is empty, so CONDITIONAL pending quote
        assert status in (ApplicabilityStatus.APPLICABLE, ApplicabilityStatus.CONDITIONAL)
        assert tf["local_authority"] is True

    def test_false_condition(self, all_obligations):
        rule = all_obligations["OBL-002"]
        prof = BusinessProfile(
            business_type="bakery",
            has_physical_premises=False,
            local_authority="Colombo Municipal Council",
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.NOT_IDENTIFIED
        assert "physical premises" in reason.lower()

    def test_unknown_condition(self, all_obligations):
        rule = all_obligations["OBL-002"]
        prof = BusinessProfile(
            business_type="bakery",
            has_physical_premises=True,
            # local_authority is None
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.UNKNOWN
        assert "local_authority" in mf


# OBL-003: Food Hygiene Licence
class TestOBL003FoodHygiene:
    def test_true_condition(self, all_obligations):
        rule = all_obligations["OBL-003"]
        prof = BusinessProfile(
            business_type="bakery",
            handles_food=True,
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status in (ApplicabilityStatus.APPLICABLE, ApplicabilityStatus.CONDITIONAL)
        assert tf["handles_food"] is True

    def test_false_condition(self, all_obligations):
        rule = all_obligations["OBL-003"]
        prof = BusinessProfile(
            business_type="clothing_retail",  # not food business
            handles_food=False,
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.NOT_IDENTIFIED
        assert reason is not None

    def test_unknown_condition(self, all_obligations):
        rule = all_obligations["OBL-003"]
        prof = BusinessProfile(
            business_type="bakery",
            # handles_food is None
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.UNKNOWN
        assert "handles_food" in mf


# OBL-004: TIN Registration
class TestOBL004TINRegistration:
    def test_true_condition(self, all_obligations):
        rule = all_obligations["OBL-004"]
        prof = BusinessProfile(
            business_type="bakery",
            legal_form=LegalForm.SOLE_PROPRIETORSHIP,
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status in (ApplicabilityStatus.APPLICABLE, ApplicabilityStatus.CONDITIONAL)
        assert tf["legal_form"] is True

    def test_false_condition(self, all_obligations):
        rule = all_obligations["OBL-004"]
        prof = BusinessProfile(
            business_type="clothing_retail",
            legal_form=LegalForm.OTHER,
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.NOT_IDENTIFIED

    def test_unknown_condition(self, all_obligations):
        rule = all_obligations["OBL-004"]
        prof = BusinessProfile(
            business_type="bakery",
            # legal_form is None -> unknown
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.UNKNOWN
        assert "legal_form" in mf


# OBL-005: EPF Registration
class TestOBL005EPF:
    def test_true_condition(self, all_obligations):
        rule = all_obligations["OBL-005"]
        prof = BusinessProfile(
            business_type="bakery",
            employee_band=EmployeeBand.MICRO,  # 1-9
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        # Has family-only exception unconfirmed, so CONDITIONAL
        assert status == ApplicabilityStatus.CONDITIONAL
        assert tf["employee_band"] is True

    def test_false_condition(self, all_obligations):
        rule = all_obligations["OBL-005"]
        prof = BusinessProfile(
            business_type="bakery",
            employee_band=EmployeeBand.NONE,  # 0 employees
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.NOT_IDENTIFIED
        assert "Employees = 0" in reason

    def test_unknown_condition(self, all_obligations):
        rule = all_obligations["OBL-005"]
        prof = BusinessProfile(
            business_type="bakery",
            # employee_band is None
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.UNKNOWN
        assert "employee_band" in mf


# OBL-006: ETF Registration
class TestOBL006ETF:
    def test_true_condition(self, all_obligations):
        rule = all_obligations["OBL-006"]
        prof = BusinessProfile(
            business_type="bakery",
            employee_band=EmployeeBand.SMALL,
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status in (ApplicabilityStatus.APPLICABLE, ApplicabilityStatus.CONDITIONAL)

    def test_false_condition(self, all_obligations):
        rule = all_obligations["OBL-006"]
        prof = BusinessProfile(
            business_type="bakery",
            employee_band=EmployeeBand.NONE,
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.NOT_IDENTIFIED
        assert "Employees = 0" in reason

    def test_unknown_condition(self, all_obligations):
        rule = all_obligations["OBL-006"]
        prof = BusinessProfile(
            business_type="bakery",
            # employee_band is None
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.UNKNOWN
        assert "employee_band" in mf


# OBL-007: Food Labelling
class TestOBL007FoodLabelling:
    def test_true_condition(self, all_obligations):
        rule = all_obligations["OBL-007"]
        prof = BusinessProfile(
            business_type="bakery",
            is_manufacturing=True,
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        # Has unpackaged exception unconfirmed, so CONDITIONAL
        assert status == ApplicabilityStatus.CONDITIONAL

    def test_false_condition(self, all_obligations):
        rule = all_obligations["OBL-007"]
        prof = BusinessProfile(
            business_type="bakery",
            is_manufacturing=False,
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.NOT_IDENTIFIED

    def test_unknown_condition(self, all_obligations):
        rule = all_obligations["OBL-007"]
        prof = BusinessProfile(
            business_type="bakery",
            # is_manufacturing is None
        )
        status, tf, mf, reason = evaluate_rule(rule, prof)
        assert status == ApplicabilityStatus.UNKNOWN
        assert "is_manufacturing" in mf


# ---------------------------------------------------------------------------
# Requirement 5: Scope Guard tests
# ---------------------------------------------------------------------------
def test_scope_guard_out_of_scope_authority():
    prof = BusinessProfile(
        business_type="bakery",
        local_authority="Kandy Municipal Council",
        jurisdiction="Central Province",
    )
    in_scope, reason = is_in_scope(prof)
    assert in_scope is False
    assert "not yet covered" in reason.lower()

    res = analyze_compliance(prof)
    not_covered = [o for o in res.obligations if o.status == ApplicabilityStatus.NOT_COVERED]
    assert len(not_covered) > 0
