"""
Component 2 — Deterministic Three-Valued Logic Rule Engine Test Suite
Tests cover:
  1. Applicable verdict
  2. Not applicable verdict
  3. Unknown due to missing fact
  4. Kleene AND logic (False short-circuit with Unknown)
  5. Kleene AND logic (Unknown when True + None)
  6. Kleene OR logic (True short-circuit with Unknown)
  7. Kleene OR logic (Unknown when False + None)
  8. Nested rules (AND inside OR / OR inside AND)
  9. Determinism (100 runs produce identical output)
 10. Schema validation failure (invalid operator)
 11. Schema validation failure (invalid layer)
 12. Schema validation failure (duplicate obligation ID)
 13. API analyse endpoint test (TestClient)
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
import pytest

from engine.schema import LeafCondition, ObligationSchema, RuleNode, RulebookSchema
from engine.loader import RulebookValidationError, load_rulebook
from engine.evaluate import (
    compare_leaf,
    eval_rule_node,
    evaluate_all,
    evaluate_obligation,
)
from engine.profile import SharedBusinessProfile
from engine.questions import generate_follow_up_questions


# ---------------------------------------------------------------------------
# Test 1: Applicable verdict
# ---------------------------------------------------------------------------
def test_applicable_verdict():
    profile = {
        "province": "Western Province",
        "has_physical_premises": True,
        "legal_form": "sole_proprietorship",
    }
    obligations = load_rulebook()
    common_obl = next(o for o in obligations if o.obligation_id == "OBL-COMMON-001")
    result = evaluate_obligation(common_obl, profile)

    assert result["status"] == "APPLICABLE"
    assert result["triggering_facts"]["province"] == "Western Province"
    assert result["triggering_facts"]["has_physical_premises"] is True
    assert len(result["missing_facts"]) == 0


# ---------------------------------------------------------------------------
# Test 2: Not applicable verdict
# ---------------------------------------------------------------------------
def test_not_applicable_verdict():
    profile = {
        "province": "Central Province",  # Out of scope for Western Province rule
        "has_physical_premises": True,
        "legal_form": "sole_proprietorship",
    }
    obligations = load_rulebook()
    common_obl = next(o for o in obligations if o.obligation_id == "OBL-COMMON-001")
    result = evaluate_obligation(common_obl, profile)

    assert result["status"] == "NOT_APPLICABLE"
    assert "province" in result["triggering_facts"]
    assert len(result["missing_facts"]) == 0


# ---------------------------------------------------------------------------
# Test 3: Unknown due to missing fact
# ---------------------------------------------------------------------------
def test_unknown_due_to_missing_fact():
    # has_physical_premises is None (missing)
    profile = {
        "province": "Western Province",
        "has_physical_premises": None,
        "legal_form": "sole_proprietorship",
    }
    obligations = load_rulebook()
    common_obl = next(o for o in obligations if o.obligation_id == "OBL-COMMON-001")
    result = evaluate_obligation(common_obl, profile)

    assert result["status"] == "UNKNOWN"
    assert "has_physical_premises" in result["missing_facts"]


# ---------------------------------------------------------------------------
# Test 4: Kleene AND logic (False short-circuit with Unknown)
# In Kleene logic: False AND None -> False
# ---------------------------------------------------------------------------
def test_and_logic_short_circuit_false():
    rule = RuleNode(
        all_of=[
            RuleNode(fact="province", op="==", value="Western Province"),
            RuleNode(fact="number_of_employees", op=">=", value=10),
        ]
    )
    # province is False, number_of_employees is None (Unknown)
    profile = {"province": "Southern Province", "number_of_employees": None}
    verdict, trigs, miss = eval_rule_node(rule, profile)

    assert verdict is False
    assert "province" in trigs


# ---------------------------------------------------------------------------
# Test 5: Kleene AND logic (Unknown when True + None)
# In Kleene logic: True AND None -> None (Unknown)
# ---------------------------------------------------------------------------
def test_and_logic_unknown():
    rule = RuleNode(
        all_of=[
            RuleNode(fact="province", op="==", value="Western Province"),
            RuleNode(fact="has_physical_premises", op="==", value=True),
        ]
    )
    profile = {"province": "Western Province", "has_physical_premises": None}
    verdict, trigs, miss = eval_rule_node(rule, profile)

    assert verdict is None
    assert "has_physical_premises" in miss


# ---------------------------------------------------------------------------
# Test 6: Kleene OR logic (True short-circuit with Unknown)
# In Kleene logic: True OR None -> True
# ---------------------------------------------------------------------------
def test_or_logic_short_circuit_true():
    rule = RuleNode(
        any_of=[
            RuleNode(fact="handles_food", op="==", value=True),
            RuleNode(fact="serves_cooked_food", op="==", value=True),
        ]
    )
    # handles_food is True, serves_cooked_food is None
    profile = {"handles_food": True, "serves_cooked_food": None}
    verdict, trigs, miss = eval_rule_node(rule, profile)

    assert verdict is True
    assert trigs.get("handles_food") is True


# ---------------------------------------------------------------------------
# Test 7: Kleene OR logic (Unknown when False + None)
# In Kleene logic: False OR None -> None (Unknown)
# ---------------------------------------------------------------------------
def test_or_logic_unknown():
    rule = RuleNode(
        any_of=[
            RuleNode(fact="handles_food", op="==", value=True),
            RuleNode(fact="serves_cooked_food", op="==", value=True),
        ]
    )
    # handles_food is False, serves_cooked_food is None
    profile = {"handles_food": False, "serves_cooked_food": None}
    verdict, trigs, miss = eval_rule_node(rule, profile)

    assert verdict is None
    assert "serves_cooked_food" in miss


# ---------------------------------------------------------------------------
# Test 8: Nested rules (AND inside OR and OR inside AND)
# ---------------------------------------------------------------------------
def test_nested_rules_and_or_mix():
    # Rule: (province == Western AND business_type == food) AND (handles_food == True OR serves_cooked_food == True)
    rule = RuleNode(
        all_of=[
            RuleNode(
                all_of=[
                    RuleNode(fact="province", op="==", value="Western Province"),
                    RuleNode(fact="business_type", op="==", value="food"),
                ]
            ),
            RuleNode(
                any_of=[
                    RuleNode(fact="handles_food", op="==", value=True),
                    RuleNode(fact="serves_cooked_food", op="==", value=True),
                ]
            ),
        ]
    )

    # Subcase A: Fully True
    prof_true = {
        "province": "Western Province",
        "business_type": "food",
        "handles_food": False,
        "serves_cooked_food": True,
    }
    v_a, _, _ = eval_rule_node(rule, prof_true)
    assert v_a is True

    # Subcase B: First branch False -> False
    prof_false = {
        "province": "Central Province",
        "business_type": "food",
        "handles_food": True,
        "serves_cooked_food": True,
    }
    v_b, _, _ = eval_rule_node(rule, prof_false)
    assert v_b is False

    # Subcase C: Second branch Unknown -> Unknown
    prof_unk = {
        "province": "Western Province",
        "business_type": "food",
        "handles_food": None,
        "serves_cooked_food": None,
    }
    v_c, _, miss_c = eval_rule_node(rule, prof_unk)
    assert v_c is None
    assert set(miss_c) == {"handles_food", "serves_cooked_food"}


# ---------------------------------------------------------------------------
# Test 9: Determinism (Same input must always give same output)
# ---------------------------------------------------------------------------
def test_determinism_same_input_same_output():
    profile = {
        "province": "Western Province",
        "business_type": "food",
        "handles_food": True,
        "has_physical_premises": True,
        "legal_form": "sole_proprietorship",
        "number_of_employees": 2,
    }
    first_run = evaluate_all(profile)

    for _ in range(100):
        run = evaluate_all(profile)
        assert run == first_run, "Rule engine evaluation produced non-deterministic variance!"


# ---------------------------------------------------------------------------
# Test 10: Schema validation failure (invalid operator)
# ---------------------------------------------------------------------------
def test_schema_validation_failure_invalid_op():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        bad_json = [
            {
                "obligation_id": "OBL-BAD-001",
                "title": "Bad Op Test",
                "actor": "owner",
                "action": "do something",
                "authority": "MOH",
                "source_id": "SRC-001",
                "source_paragraph": "sec 1",
                "source_text": "text",
                "documents_needed": [],
                "layer": "food",
                "rule": {
                    "fact": "business_type",
                    "op": "LIKE",  # Invalid operator
                    "value": "food",
                },
            }
        ]
        json.dump(bad_json, tmp)
        tmp_path = tmp.name

    with pytest.raises(RulebookValidationError) as exc_info:
        load_rulebook(tmp_path)
    assert "Schema validation error" in str(exc_info.value)
    Path(tmp_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Test 11: Schema validation failure (invalid layer)
# ---------------------------------------------------------------------------
def test_schema_validation_failure_invalid_layer():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        bad_json = [
            {
                "obligation_id": "OBL-BAD-002",
                "title": "Bad Layer Test",
                "actor": "owner",
                "action": "do something",
                "authority": "MOH",
                "source_id": "SRC-001",
                "source_paragraph": "sec 1",
                "source_text": "text",
                "documents_needed": [],
                "layer": "crypto_mining",  # Invalid layer
                "rule": {
                    "fact": "business_type",
                    "op": "==",
                    "value": "crypto",
                },
            }
        ]
        json.dump(bad_json, tmp)
        tmp_path = tmp.name

    with pytest.raises(RulebookValidationError) as exc_info:
        load_rulebook(tmp_path)
    assert "Schema validation error" in str(exc_info.value)
    Path(tmp_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Test 12: Schema validation failure (duplicate obligation ID)
# ---------------------------------------------------------------------------
def test_schema_validation_failure_duplicate_id():
    obligations_data = json.loads(Path("data/obligations.json").read_text(encoding="utf-8"))
    obligations_data.append(obligations_data[0])  # Duplicate first entry

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(obligations_data, tmp)
        tmp_path = tmp.name

    with pytest.raises(RulebookValidationError) as exc_info:
        load_rulebook(tmp_path)
    assert "Duplicate obligation_id detected" in str(exc_info.value)
    Path(tmp_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Test 13: Deterministic Follow-Up Question Generation (No LLM)
# ---------------------------------------------------------------------------
def test_deterministic_follow_up_questions():
    missing = ["handles_food", "turnover_band", "unknown_custom_fact"]
    questions = generate_follow_up_questions(missing)

    assert len(questions) == 3
    assert questions[0]["fact"] == "handles_food"
    assert "question_en" in questions[0]
    assert "question_si" in questions[0]
    assert questions[0]["type"] == "boolean"

    assert questions[1]["fact"] == "turnover_band"
    assert questions[1]["type"] == "select"
