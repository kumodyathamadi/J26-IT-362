"""
Tests for canonical Pydantic models: Obligation, Rule, Evidence, BusinessProfile.
Verifies:
- Evidence schema: {doc_id, page, quote, url}
- Rule schema: all/any conditions with ops eq, in, gte, returning 'unknown' for missing facts
- Active rule validation: rejects loading if evidence, effective_from, or reviewer_status is missing
- Draft rule flexibility: allows pending fields when status != 'active'
"""

import pytest
from pydantic import ValidationError

from schemas import (
    BusinessProfile,
    Evidence,
    Obligation,
    Rule,
)


class TestEvidenceModel:
    def test_valid_evidence(self):
        ev = Evidence(
            doc_id="LK-ACT-2007-07-EN",
            page=25,
            quote="Every private company must have at least one director.",
            url="https://drc.gov.lk/act-2007",
        )
        assert ev.doc_id == "LK-ACT-2007-07-EN"
        assert ev.page == 25
        assert "director" in ev.quote
        assert ev.url == "https://drc.gov.lk/act-2007"

    def test_minimal_evidence(self):
        ev = Evidence(doc_id="LK-ACT-1980-26-EN")
        assert ev.doc_id == "LK-ACT-1980-26-EN"
        assert ev.page is None
        assert ev.quote == ""
        assert ev.url is None

    def test_missing_doc_id_rejected(self):
        with pytest.raises(ValidationError):
            Evidence()


class TestRuleModelAnd3VLEvaluation:
    def test_leaf_operators_eq_in_gte(self):
        r_eq = Rule(fact="business_type", op="eq", value="food")
        r_in = Rule(fact="legal_structure", op="in", value=["sole_proprietorship", "partnership"])
        r_gte = Rule(fact="employee_count", op="gte", value=5)

        assert r_eq.is_leaf()
        assert r_in.is_leaf()
        assert r_gte.is_leaf()

    def test_missing_field_evaluates_to_unknown(self):
        rule = Rule(fact="operates_kitchen", op="eq", value=True)
        profile = BusinessProfile(business_type="food")  # operates_kitchen is None

        verdict, trigs, missing = rule.evaluate(profile)
        assert verdict == "unknown"
        assert "operates_kitchen" in missing

    def test_all_conditions_kleene_and(self):
        # Conjunction of two conditions
        rule = Rule(all=[
            Rule(fact="business_type", op="eq", value="food"),
            Rule(fact="operates_kitchen", op="eq", value=True),
        ])

        # 1. Both True -> True
        p_true = BusinessProfile(business_type="food", operates_kitchen=True)
        v, _, _ = rule.evaluate(p_true)
        assert v is True

        # 2. One False, one Unknown -> False (False absorbs Unknown in Kleene AND)
        p_false = BusinessProfile(business_type="clothing", operates_kitchen=None)
        v, _, _ = rule.evaluate(p_false)
        assert v is False

        # 3. One True, one Unknown -> Unknown
        p_unknown = BusinessProfile(business_type="food", operates_kitchen=None)
        v, _, miss = rule.evaluate(p_unknown)
        assert v == "unknown"
        assert "operates_kitchen" in miss

    def test_any_conditions_kleene_or(self):
        rule = Rule(any=[
            Rule(fact="sells_alcohol", op="eq", value=True),
            Rule(fact="operates_kitchen", op="eq", value=True),
        ])

        # 1. One True, one Unknown -> True (True absorbs Unknown in Kleene OR)
        p_true = BusinessProfile(sells_alcohol=True, operates_kitchen=None)
        v, _, _ = rule.evaluate(p_true)
        assert v is True

        # 2. Both False -> False
        p_false = BusinessProfile(sells_alcohol=False, operates_kitchen=False)
        v, _, _ = rule.evaluate(p_false)
        assert v is False

        # 3. One False, one Unknown -> Unknown
        p_unknown = BusinessProfile(sells_alcohol=False, operates_kitchen=None)
        v, _, miss = rule.evaluate(p_unknown)
        assert v == "unknown"

    def test_invalid_operator_rejected(self):
        with pytest.raises(ValidationError):
            Rule(fact="employee_count", op="invalid_op", value=5)


class TestObligationModelValidators:
    def test_valid_active_obligation_loaded(self):
        obl = Obligation(
            id="OBL-FOOD-001",
            name="CMC Food Premises Hygiene Licence",
            authority="Colombo Municipal Council",
            status="active",
            effective_from="1980-01-01",
            reviewer_status="verified",
            evidence=Evidence(
                doc_id="LK-ACT-1980-26-EN",
                page=12,
                quote="No person shall manufacture, prepare, preserve, package, store, or sell any food in an insanitary condition.",
            ),
            rule=Rule(fact="business_type", op="eq", value="food"),
        )
        assert obl.id == "OBL-FOOD-001"
        assert obl.status == "active"
        assert obl.evidence.doc_id == "LK-ACT-1980-26-EN"

    def test_active_rule_missing_evidence_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            Obligation(
                id="OBL-TEST-001",
                name="Test Obligation",
                authority="Test Authority",
                status="active",
                effective_from="2020-01-01",
                reviewer_status="verified",
                evidence=None,  # MISSING EVIDENCE ON ACTIVE RULE
                rule=Rule(fact="business_type", op="eq", value="food"),
            )
        assert "evidence" in str(exc_info.value).lower()

    def test_active_rule_missing_effective_from_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            Obligation(
                id="OBL-TEST-002",
                name="Test Obligation",
                authority="Test Authority",
                status="active",
                effective_from=None,  # MISSING EFFECTIVE_FROM ON ACTIVE RULE
                reviewer_status="verified",
                evidence=Evidence(doc_id="LK-ACT-2007-07-EN"),
                rule=Rule(fact="business_type", op="eq", value="food"),
            )
        assert "effective_from" in str(exc_info.value).lower()

    def test_active_rule_missing_reviewer_status_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            Obligation(
                id="OBL-TEST-003",
                name="Test Obligation",
                authority="Test Authority",
                status="active",
                effective_from="2020-01-01",
                reviewer_status="",  # EMPTY REVIEWER STATUS ON ACTIVE RULE
                evidence=Evidence(doc_id="LK-ACT-2007-07-EN"),
                rule=Rule(fact="business_type", op="eq", value="food"),
            )
        assert "reviewer_status" in str(exc_info.value).lower()

    def test_draft_rule_allows_pending_fields(self):
        # A draft rule should load even if evidence, effective_from or reviewer_status is pending
        obl_draft = Obligation(
            id="OBL-DRAFT-001",
            name="Upcoming Environmental Bylaw",
            authority="Western Provincial Council",
            status="draft",
            evidence=None,
            effective_from=None,
            reviewer_status="draft",
            rule=Rule(fact="business_type", op="eq", value="salon"),
        )
        assert obl_draft.status == "draft"
        assert obl_draft.evidence is None


class TestBusinessProfileModel:
    def test_default_fields_are_none_unknown(self):
        p = BusinessProfile()
        assert p.business_type is None
        assert p.operates_kitchen is None
        assert p.physical_premises is None
        assert p.employee_count is None

    def test_get_fact_resolution(self):
        p = BusinessProfile(
            business_type="salon",
            employee_count=3,
            location={"province": "Western Province", "district": "Colombo"},
        )
        assert p.get_fact("business_type") == "salon"
        assert p.get_fact("employee_count") == 3
        assert p.get_fact("location.province") == "Western Province"
        assert p.get_fact("location.district") == "Colombo"
        assert p.get_fact("physical_premises") is None  # Unknown
