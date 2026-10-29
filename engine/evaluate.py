"""
Component 2 — Three-Valued Kleene Logic Rule Engine (engine.py)
Evaluates compliance obligations against a business profile using 3-valued Kleene logic.

Kleene Logic Rules (True, False, None):
- Kleene AND (all_of):
    - Any child is False -> False
    - Else if any child is None (Unknown) -> None
    - Else (all True) -> True
- Kleene OR (any_of):
    - Any child is True -> True
    - Else if any child is None (Unknown) -> None
    - Else (all False) -> False

Determinism:
Identical profile input will ALWAYS produce the exact same output.
Zero external calls, zero non-deterministic random state.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from engine.schemas import (
    BusinessProfileInput,
    ObligationSchema,
    RuleNode,
)
from engine.loader import load_rulebook

TriVal = Optional[bool]  # True | False | None (representing UNKNOWN in Kleene 3VL)


# ---------------------------------------------------------------------------
# Fact Resolution with Dot Notation & Semantic Aliases
# ---------------------------------------------------------------------------

def get_fact_value(profile: Dict[str, Any], fact_path: str) -> Any:
    """
    Resolves fact values from the business profile supporting:
      1. Direct key match (e.g. 'physical_premises' or 'location.province')
      2. Dot notation traversal (e.g. 'location.province' -> profile['location']['province'])
      3. Sub-object leaf lookup (e.g. 'province' -> look inside profile['location']['province'])
      4. Top-level fallback for nested paths (e.g. 'location.province' -> profile['province'])
      5. Semantic aliases (e.g. legal_structure <-> legal_form, employee_count <-> number_of_employees)
    """
    # 1. Direct key match
    if fact_path in profile:
        return profile[fact_path]

    parts = fact_path.split(".")

    # 2. Dot-notation traversal
    curr: Any = profile
    traversal_success = True
    for p in parts:
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        else:
            traversal_success = False
            break

    if traversal_success:
        return curr

    # 3. Leaf fallback in 'location' object
    leaf = parts[-1]
    if len(parts) == 1 and isinstance(profile.get("location"), dict):
        if leaf in profile["location"]:
            return profile["location"][leaf]

    # 4. Top-level fallback if fact_path was dotted
    if leaf in profile:
        return profile[leaf]

    # 5. Semantic alias bridge for Component 1 / Component 2 compatibility
    aliases = {
        "legal_structure": ["legal_form", "entity_type", "ownership"],
        "legal_form": ["legal_structure", "entity_type", "ownership"],
        "employee_count": ["number_of_employees", "employees", "employees_count"],
        "number_of_employees": ["employee_count", "employees", "employees_count"],
        "physical_premises": ["has_physical_premises"],
        "has_physical_premises": ["physical_premises"],
        "operates_kitchen": ["handles_food", "serves_cooked_food"],
        "handles_food": ["operates_kitchen"],
        "uses_chemicals_or_cosmetics": ["uses_chemicals"],
        "handles_waste_oil_or_batteries": ["handles_waste_oil", "handles_batteries"],
    }
    for alias in aliases.get(leaf, []):
        if alias in profile:
            return profile[alias]
        if isinstance(profile.get("location"), dict) and alias in profile["location"]:
            return profile["location"][alias]

    return None


# ---------------------------------------------------------------------------
# Atomic Condition Evaluation
# ---------------------------------------------------------------------------

def compare_leaf(fact_val: Any, op: str, target_val: Any) -> bool:
    """
    Deterministically evaluates an atomic comparison operator.
    Supports ==, !=, in, >=, <.
    """
    if op == "==":
        if isinstance(fact_val, str) and isinstance(target_val, str):
            return fact_val.strip().lower() == target_val.strip().lower()
        return fact_val == target_val

    elif op == "!=":
        if isinstance(fact_val, str) and isinstance(target_val, str):
            return fact_val.strip().lower() != target_val.strip().lower()
        return fact_val != target_val

    elif op == "in":
        if isinstance(target_val, (list, tuple, set)):
            if isinstance(fact_val, str):
                target_lower = {str(item).strip().lower() for item in target_val}
                return fact_val.strip().lower() in target_lower
            return fact_val in target_val
        elif isinstance(fact_val, (list, tuple, set)):
            if isinstance(target_val, str):
                fact_lower = {str(item).strip().lower() for item in fact_val}
                return target_val.strip().lower() in fact_lower
            return target_val in fact_val
        elif isinstance(target_val, str) and isinstance(fact_val, str):
            return fact_val.lower() in target_val.lower()
        return False

    elif op == ">=":
        try:
            return float(fact_val) >= float(target_val)
        except (ValueError, TypeError):
            return False

    elif op == "<":
        try:
            return float(fact_val) < float(target_val)
        except (ValueError, TypeError):
            return False

    else:
        raise ValueError(f"Unsupported comparison operator '{op}'")


# ---------------------------------------------------------------------------
# Recursive Kleene 3-Valued Logic Evaluator
# ---------------------------------------------------------------------------

def eval_rule_node(
    node: RuleNode,
    profile: Dict[str, Any]
) -> Tuple[TriVal, Dict[str, Any], List[str]]:
    """
    Recursively evaluates a RuleNode using three-valued Kleene logic.

    Returns:
        Tuple of:
          - TriVal verdict (True, False, or None for UNKNOWN)
          - triggering_facts dict (facts that contributed to the verdict)
          - missing_facts list (fact paths that evaluated to None / Unknown)
    """
    # 1. Atomic Leaf Condition
    if node.is_leaf():
        fact_name = node.fact  # type: ignore[assignment]
        op = node.op           # type: ignore[assignment]
        target_val = node.value

        fact_val = get_fact_value(profile, fact_name)

        # In Kleene logic: None represents an unknown state
        if fact_val is None:
            missing_list = [fact_name]
            leaf = fact_name.split(".")[-1]
            if leaf != fact_name:
                missing_list.append(leaf)

            aliases = {
                "physical_premises": ["has_physical_premises", "physical_premises"],
                "has_physical_premises": ["has_physical_premises", "physical_premises"],
                "legal_structure": ["legal_form", "legal_structure"],
                "legal_form": ["legal_form", "legal_structure"],
                "employee_count": ["number_of_employees", "employees", "employee_count"],
                "number_of_employees": ["number_of_employees", "employees", "employee_count"],
                "operates_kitchen": ["handles_food", "operates_kitchen"],
                "handles_food": ["operates_kitchen", "handles_food"],
            }
            for alias in aliases.get(leaf, []):
                if alias in profile and profile[alias] is None:
                    missing_list.append(alias)

            return None, {}, sorted(list(set(missing_list)))

        is_met = compare_leaf(fact_val, op, target_val)

        trigs: Dict[str, Any] = {fact_name: fact_val}
        leaf = fact_name.split(".")[-1]
        if leaf != fact_name:
            trigs[leaf] = fact_val

        aliases_map = {
            "physical_premises": ["has_physical_premises", "physical_premises"],
            "has_physical_premises": ["has_physical_premises", "physical_premises"],
            "legal_structure": ["legal_form", "legal_structure"],
            "legal_form": ["legal_form", "legal_structure"],
            "employee_count": ["number_of_employees", "employees", "employee_count"],
            "number_of_employees": ["number_of_employees", "employees", "employee_count"],
            "operates_kitchen": ["handles_food", "operates_kitchen"],
            "handles_food": ["operates_kitchen", "handles_food"],
        }
        for alias in aliases_map.get(leaf, []):
            if alias in profile:
                trigs[alias] = profile[alias]

        for k in profile.keys():
            if k == leaf or k == fact_name:
                trigs[k] = profile[k]

        if is_met:
            return True, trigs, []
        else:
            return False, trigs, []

    # 2. Conjunction (all_of / Kleene AND)
    if node.all_of is not None:
        child_verdicts: List[TriVal] = []
        all_triggering: Dict[str, Any] = {}
        all_missing: Set[str] = set()
        false_triggering: Dict[str, Any] = {}

        for child in node.all_of:
            v, trigs, miss = eval_rule_node(child, profile)
            child_verdicts.append(v)
            all_missing.update(miss)
            if v is True:
                all_triggering.update(trigs)
            elif v is False:
                false_triggering.update(trigs)

        # Kleene AND rules:
        # Any False -> False (absorbs Unknown)
        # Else if any None (Unknown) -> None
        # Else -> True
        if False in child_verdicts:
            return False, false_triggering, []
        elif None in child_verdicts:
            return None, {}, sorted(list(all_missing))
        else:
            return True, all_triggering, []

    # 3. Disjunction (any_of / Kleene OR)
    if node.any_of is not None:
        child_verdicts = []
        true_triggering: Dict[str, Any] = {}
        all_missing = set()
        all_false_trigs: Dict[str, Any] = {}

        for child in node.any_of:
            v, trigs, miss = eval_rule_node(child, profile)
            child_verdicts.append(v)
            all_missing.update(miss)
            if v is True:
                true_triggering.update(trigs)
            elif v is False:
                all_false_trigs.update(trigs)

        # Kleene OR rules:
        # Any True -> True (absorbs Unknown)
        # Else if any None (Unknown) -> None
        # Else -> False
        if True in child_verdicts:
            return True, true_triggering, []
        elif None in child_verdicts:
            return None, {}, sorted(list(all_missing))
        else:
            return False, all_false_trigs, []

    raise ValueError("Invalid RuleNode: neither leaf condition nor all_of/any_of defined.")


# ---------------------------------------------------------------------------
# Obligation & Compliance Evaluators
# ---------------------------------------------------------------------------

def evaluate_obligation(
    obligation: ObligationSchema,
    profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates a single ObligationSchema against a business profile.
    Produces deterministic output with status APPLICABLE, NOT_APPLICABLE, or UNKNOWN.
    """
    verdict, triggering_facts, missing_facts = eval_rule_node(obligation.rule, profile)

    if verdict is True:
        status = "APPLICABLE"
    elif verdict is False:
        status = "NOT_APPLICABLE"
    else:
        status = "UNKNOWN"

    return {
        "obligation_id": obligation.obligation_id,
        "title": obligation.title,
        "status": status,
        "layer": obligation.layer,
        "authority": obligation.authority,
        "triggering_facts": triggering_facts,
        "missing_facts": missing_facts,
        "source_id": obligation.source_id,
        "source_paragraph": obligation.source_paragraph,
        "source_text": obligation.source_text,
        "documents_needed": obligation.documents_needed,
    }


def evaluate_compliance(
    profile: Union[Dict[str, Any], BusinessProfileInput],
    obligations: Optional[List[ObligationSchema]] = None,
    filter_by_layer: bool = False,
) -> List[Dict[str, Any]]:
    """
    Evaluates obligations against a profile dictionary or BusinessProfileInput model.

    Args:
        profile: Dictionary or BusinessProfileInput from Component 1.
        obligations: Optional custom list of ObligationSchema. If None, loads from data/obligations.json.
        filter_by_layer: If True, only evaluates 'common' layer and the layer matching profile.business_type.

    Returns:
        List of evaluated obligation dictionaries with APPLICABLE, NOT_APPLICABLE, or UNKNOWN status.
    """
    if isinstance(profile, BusinessProfileInput):
        profile_dict = profile.model_dump()
    elif hasattr(profile, "model_dump"):
        profile_dict = profile.model_dump()
    else:
        profile_dict = dict(profile)

    if obligations is None:
        obligations = load_rulebook()

    # Layer filtering if requested
    if filter_by_layer:
        biz_type = profile_dict.get("business_type")
        target_layers = {"common"}
        if biz_type:
            target_layers.add(biz_type)
        obligations_to_eval = [o for o in obligations if o.layer in target_layers]
    else:
        obligations_to_eval = obligations

    results: List[Dict[str, Any]] = []
    for obl in obligations_to_eval:
        res = evaluate_obligation(obl, profile_dict)
        results.append(res)

    return results


# Backward compatibility alias
evaluate_all = evaluate_compliance
