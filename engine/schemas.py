"""
Component 2 — Data Contract & Pydantic Schemas
Defines schemas for the incoming Profile from Component 1, rulebook obligations,
and the structured compliance response.

Includes canonical models:
- Evidence: {doc_id, page, quote, url}
- Rule: boolean rule tree using all/any with ops eq, in, gte, returning 'unknown' for missing facts
- Obligation: validated statutory obligation requiring evidence, effective_from, and reviewer_status when active
- BusinessProfile: profile representation with unknown defaults
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VALID_OPS: Set[str] = {"==", "!=", "in", ">=", "<", "eq", "gte"}
VALID_RULE_OPS: Set[str] = {"eq", "==", "in", "gte", ">=", "!=", "<", ">"}
VALID_LAYERS: Set[str] = {"common", "food", "clothing", "salon", "vehicle_parts"}


# ---------------------------------------------------------------------------
# 1. Canonical Evidence Model
# ---------------------------------------------------------------------------

class Evidence(BaseModel):
    """
    Statutory or regulatory legal source grounding.
    Schema: {doc_id, page, quote, url}
    """
    doc_id: str = Field(..., description="Unique document ID in statutory register")
    page: Optional[int] = Field(default=None, description="1-indexed source document page number")
    quote: str = Field(default="", description="Verbatim statutory or regulatory quote")
    url: Optional[str] = Field(default=None, description="Official public or archive source URL")

    model_config = ConfigDict(extra="ignore")


# ---------------------------------------------------------------------------
# 2. Canonical Rule Model (Three-Valued Kleene Logic: True, False, "unknown")
# ---------------------------------------------------------------------------

class Rule(BaseModel):
    """
    Executable deterministic 3-valued rule tree.
    Conditions use all/any with ops eq, in, gte, and 'unknown' for missing fields.
    """
    all: Optional[List[Rule]] = Field(default=None, alias="all_of", description="Conjunction of child rules (Kleene AND)")
    any: Optional[List[Rule]] = Field(default=None, alias="any_of", description="Disjunction of child rules (Kleene OR)")
    fact: Optional[str] = Field(default=None, description="Fact attribute path (e.g. 'business_type', 'location.province')")
    op: Optional[str] = Field(default=None, description="Comparison operator (eq, in, gte, ==, >=, !=, <)")
    value: Optional[Any] = Field(default=None, description="Target value for leaf condition comparison")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @model_validator(mode="after")
    def validate_rule(self) -> Rule:
        has_all = self.all is not None
        has_any = self.any is not None
        has_fact = self.fact is not None

        if not (has_all or has_any or has_fact):
            raise ValueError("Rule must specify at least one of: 'all', 'any', or a leaf condition with 'fact'")

        if has_fact:
            if not self.op:
                raise ValueError(f"Leaf condition for fact '{self.fact}' must specify an operator 'op'")
            norm_op = self.op.lower().strip()
            if norm_op not in VALID_RULE_OPS:
                raise ValueError(f"Operator '{self.op}' is invalid. Allowed operators: {sorted(list(VALID_RULE_OPS))}")

        return self

    def is_leaf(self) -> bool:
        return self.fact is not None and self.op is not None

    def evaluate(self, profile: Any) -> Tuple[Union[bool, str], Dict[str, Any], List[str]]:
        """
        Evaluates rule against a BusinessProfile or dictionary using Kleene 3VL.
        Returns:
            verdict: True, False, or 'unknown' (when missing fields are encountered)
            triggering_facts: dict of matched facts
            missing_facts: list of fact paths that were missing/None
        """
        # Leaf condition evaluation
        if self.is_leaf():
            fact_path = self.fact  # type: ignore[assignment]
            op = (self.op or "eq").lower().strip()
            target_val = self.value

            # Resolve fact from profile
            fact_val = None
            if hasattr(profile, "get_fact"):
                fact_val = profile.get_fact(fact_path)
            elif isinstance(profile, dict):
                fact_val = _resolve_dict_fact(profile, fact_path)
            elif hasattr(profile, fact_path):
                fact_val = getattr(profile, fact_path, None)

            # In Kleene logic: None/missing field evaluates to "unknown" (never False)
            if fact_val is None or fact_val == "unknown":
                return "unknown", {}, [fact_path]

            is_match = _compare_values(fact_val, op, target_val)
            if is_match:
                return True, {fact_path: fact_val}, []
            else:
                return False, {fact_path: fact_val}, []

        # Conjunction: all (Kleene AND)
        if self.all is not None:
            child_verdicts: List[Union[bool, str]] = []
            triggering: Dict[str, Any] = {}
            missing: List[str] = []

            for child in self.all:
                cv, ctrigs, cmiss = child.evaluate(profile)
                child_verdicts.append(cv)
                triggering.update(ctrigs)
                missing.extend(cmiss)

            # Kleene AND rules:
            # Any False -> False (False absorbs Unknown)
            # Else if any 'unknown' -> 'unknown'
            # Else -> True
            if False in child_verdicts:
                return False, triggering, []
            elif "unknown" in child_verdicts or None in child_verdicts:
                return "unknown", {}, sorted(list(set(missing)))
            else:
                return True, triggering, []

        # Disjunction: any (Kleene OR)
        if self.any is not None:
            child_verdicts = []
            triggering = {}
            missing = []

            for child in self.any:
                cv, ctrigs, cmiss = child.evaluate(profile)
                child_verdicts.append(cv)
                if cv is True:
                    triggering.update(ctrigs)
                missing.extend(cmiss)

            # Kleene OR rules:
            # Any True -> True (True absorbs Unknown)
            # Else if any 'unknown' -> 'unknown'
            # Else -> False
            if True in child_verdicts:
                return True, triggering, []
            elif "unknown" in child_verdicts or None in child_verdicts:
                return "unknown", {}, sorted(list(set(missing)))
            else:
                return False, triggering, []

        raise ValueError("Invalid rule node")


# ---------------------------------------------------------------------------
# 3. Canonical Obligation Model with Mandatory Active Rule Validators
# ---------------------------------------------------------------------------

class Obligation(BaseModel):
    """
    Statutory regulatory obligation requirement.
    Enforces that an active rule must have evidence, effective_from, and reviewer_status.
    Rejects loading otherwise.
    """
    id: str = Field(..., alias="obligation_id", description="Unique requirement ID (e.g. OBL-001)")
    name: str = Field(..., alias="title", description="Title or summary of obligation")
    authority: str = Field(..., description="Issuing or enforcing regulatory body")
    rule: Rule = Field(..., alias="conditions", description="Executable 3VL rule")
    evidence: Optional[Evidence] = Field(default=None, description="Legal statutory grounding")
    effective_from: Optional[str] = Field(default=None, description="Effective commencement date (YYYY-MM-DD)")
    reviewer_status: Optional[str] = Field(default=None, description="Review verification status (draft|verified)")
    status: Literal["active", "draft", "policy", "deprecated"] = Field(
        default="active", description="Rule operational status"
    )
    jurisdiction: Optional[str] = Field(default="Western Province", description="Governing geographic jurisdiction")
    layer: Optional[str] = Field(default="common", description="Sector layer (common, food, clothing, salon, vehicle_parts)")
    required_action: Optional[str] = Field(default=None, description="Action required by the business")
    documents_needed: List[str] = Field(default_factory=list, alias="required_documents", description="Checklist of documents")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @model_validator(mode="after")
    def validate_active_rule(self) -> Obligation:
        """
        Validator: An active rule must have evidence, effective_from, and reviewer_status.
        Reject loading otherwise.
        """
        if self.status == "active":
            # 1. Must have evidence
            if self.evidence is None:
                raise ValueError(
                    f"Active rule '{self.id}' rejected: 'evidence' is required for active obligations."
                )
            if not self.evidence.doc_id or not str(self.evidence.doc_id).strip():
                raise ValueError(
                    f"Active rule '{self.id}' rejected: evidence must include a non-empty 'doc_id'."
                )

            # 2. Must have effective_from
            if not self.effective_from or not str(self.effective_from).strip():
                raise ValueError(
                    f"Active rule '{self.id}' rejected: 'effective_from' date is required for active obligations."
                )

            # 3. Must have reviewer_status
            if not self.reviewer_status or not str(self.reviewer_status).strip():
                raise ValueError(
                    f"Active rule '{self.id}' rejected: 'reviewer_status' is required for active obligations."
                )

        return self


# ---------------------------------------------------------------------------
# 4. Canonical BusinessProfile Model (Three-Valued Defaults)
# ---------------------------------------------------------------------------

class BusinessProfile(BaseModel):
    """
    Business Profile schema representing known facts at evaluation time.
    Every conditional or sector-specific field defaults to None (UNKNOWN).
    Resolves missing fields as 'unknown' rather than False.
    """
    business_id: Optional[str] = Field(default=None, description="Business ID from Component 1")
    business_type: Optional[str] = Field(default=None, description="Target sector (food, clothing, salon, vehicle_parts)")
    sub_activity: List[str] = Field(default_factory=list, description="Sub-activities or category tags")
    location: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Location hierarchy")
    province: Optional[str] = Field(default=None, description="Province of operation (default: Western Province)")
    district: Optional[str] = Field(default=None, description="District (e.g. Colombo, Gampaha, Kalutara)")
    local_authority: Optional[str] = Field(default=None, description="Governing Municipal Council or Pradeshiya Sabha")
    legal_structure: Optional[str] = Field(default=None, description="Legal form (sole_proprietorship, partnership, private_limited)")
    legal_form: Optional[str] = Field(default=None, description="Alias for legal_structure")
    employee_count: Optional[int] = Field(default=None, ge=0, description="Hired staff count")
    employee_band: Optional[str] = Field(default=None, description="Employee band approximation")
    physical_premises: Optional[bool] = Field(default=None, description="Fixed physical commercial facility")
    has_physical_premises: Optional[bool] = Field(default=None, description="Alias for physical_premises")
    operates_kitchen: Optional[bool] = Field(default=None, description="Food: commercial kitchen on premises")
    handles_food: Optional[bool] = Field(default=None, description="Food: prepares or handles food")
    sells_alcohol: Optional[bool] = Field(default=None, description="Retails or serves alcoholic beverages")
    imports_goods: Optional[bool] = Field(default=None, description="Imports commercial products from abroad")
    is_importing: Optional[bool] = Field(default=None, description="Alias for imports_goods")
    handles_waste_oil_or_batteries: Optional[bool] = Field(default=None, description="Vehicle parts: hazardous waste")
    uses_chemicals_or_cosmetics: Optional[bool] = Field(default=None, description="Salon: chemical agents or cosmetics")
    is_manufacturing: Optional[bool] = Field(default=None, description="Manufactures or pre-packages goods")
    estimated_turnover_band: Optional[str] = Field(default=None, description="Turnover tier")
    turnover_lkr: Optional[float] = Field(default=None, description="Annual turnover in LKR")

    model_config = ConfigDict(extra="ignore")

    def get_fact(self, fact_path: str) -> Any:
        """
        Resolves fact values with dot notation, nested location fallback, and aliases.
        Returns 'unknown' (or None) for missing fields.
        """
        val = getattr(self, fact_path, None)
        if val is not None:
            return val

        # Dot-notation traversal
        parts = fact_path.split(".")
        curr: Any = self
        found = True
        for p in parts:
            if isinstance(curr, dict) and p in curr:
                curr = curr[p]
            elif hasattr(curr, p):
                curr = getattr(curr, p)
            else:
                found = False
                break
        if found and curr is not None:
            return curr

        # Sub-object leaf lookup inside location
        leaf = parts[-1]
        if isinstance(self.location, dict) and leaf in self.location:
            loc_val = self.location[leaf]
            if loc_val is not None:
                return loc_val

        # Aliases
        aliases = {
            "legal_structure": ["legal_form"],
            "legal_form": ["legal_structure"],
            "physical_premises": ["has_physical_premises"],
            "has_physical_premises": ["physical_premises"],
            "operates_kitchen": ["handles_food"],
            "handles_food": ["operates_kitchen"],
            "imports_goods": ["is_importing"],
            "is_importing": ["imports_goods"],
            "province": ["location.province"],
            "district": ["location.district"],
            "local_authority": ["location.local_authority"],
        }
        for alias in aliases.get(leaf, []):
            if hasattr(self, alias):
                aval = getattr(self, alias)
                if aval is not None:
                    return aval

        return None


# ---------------------------------------------------------------------------
# Helper comparison & fact resolution functions
# ---------------------------------------------------------------------------

def _compare_values(fact_val: Any, op: str, target_val: Any) -> bool:
    """Deterministically evaluates ops eq, in, gte, ==, >=, !=, <, >."""
    norm_op = op.lower().strip()

    if norm_op in ("eq", "=="):
        if isinstance(fact_val, str) and isinstance(target_val, str):
            return fact_val.strip().lower() == target_val.strip().lower()
        return fact_val == target_val

    elif norm_op == "in":
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

    elif norm_op in ("gte", ">="):
        try:
            return float(fact_val) >= float(target_val)
        except (ValueError, TypeError):
            return False

    elif norm_op == "!=":
        if isinstance(fact_val, str) and isinstance(target_val, str):
            return fact_val.strip().lower() != target_val.strip().lower()
        return fact_val != target_val

    elif norm_op == "<":
        try:
            return float(fact_val) < float(target_val)
        except (ValueError, TypeError):
            return False

    elif norm_op == ">":
        try:
            return float(fact_val) > float(target_val)
        except (ValueError, TypeError):
            return False

    else:
        raise ValueError(f"Unsupported comparison operator '{op}'")


def _resolve_dict_fact(d: Dict[str, Any], path: str) -> Any:
    if path in d:
        return d[path]
    parts = path.split(".")
    curr: Any = d
    for p in parts:
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        else:
            return None
    return curr


# ---------------------------------------------------------------------------
# Backward Compatibility Schemas (LocationSchema, BusinessProfileInput, etc.)
# ---------------------------------------------------------------------------

class LocationSchema(BaseModel):
    """Geographic jurisdiction within Sri Lanka (Component 2 scope: Western Province)."""
    province: str = Field(default="Western Province", description="Province of operation")
    district: Optional[str] = Field(default=None, description="District (e.g. Colombo, Gampaha, Kalutara)")
    local_authority: Optional[str] = Field(default=None, description="Governing Municipal Council or Pradeshiya Sabha")

    model_config = ConfigDict(extra="ignore")


class BusinessProfileInput(BaseModel):
    """Data contract received from Component 1."""
    business_id: str = Field(..., description="Unique business identifier generated by Component 1")
    business_type: Literal["food", "clothing", "salon", "vehicle_parts"] = Field(
        ..., description="Target business sector"
    )
    sub_activity: List[str] = Field(
        default_factory=list, description="Specific sub-activities (e.g. ['bakery', 'takeaway'])"
    )
    location: LocationSchema = Field(
        default_factory=LocationSchema, description="Location hierarchy (province, district, local authority)"
    )
    legal_structure: Literal["sole_proprietorship", "partnership", "private_limited"] = Field(
        ..., description="Ownership legal structure"
    )
    employee_count: int = Field(..., ge=0, description="Total number of hired staff")

    physical_premises: Optional[bool] = Field(default=None)
    operates_kitchen: Optional[bool] = Field(default=None)
    sells_alcohol: Optional[bool] = Field(default=None)
    imports_goods: Optional[bool] = Field(default=None)
    handles_waste_oil_or_batteries: Optional[bool] = Field(default=None)
    uses_chemicals_or_cosmetics: Optional[bool] = Field(default=None)
    estimated_turnover_band: Optional[str] = Field(default=None)

    model_config = ConfigDict(extra="ignore")


class LeafCondition(BaseModel):
    """Atomic condition comparing a fact path against a target value."""
    fact: str = Field(..., description="Fact path (supports dot notation, e.g. location.province)")
    op: Literal["==", "!=", "in", ">=", "<", "eq", "gte"] = Field(..., description="Comparison operator")
    value: Any = Field(..., description="Target reference value")


class RuleNode(BaseModel):
    """Recursive rule node supporting Kleene AND (all_of), OR (any_of), and leaf conditions."""
    all_of: Optional[List[RuleNode]] = Field(None, description="Conjunction of child rules (Kleene AND)")
    any_of: Optional[List[RuleNode]] = Field(None, description="Disjunction of child rules (Kleene OR)")
    fact: Optional[str] = Field(None, description="Fact attribute name for leaf condition")
    op: Optional[Literal["==", "!=", "in", ">=", "<", "eq", "gte"]] = Field(None, description="Comparison operator for leaf condition")
    value: Optional[Any] = Field(None, description="Target value for leaf condition")

    @model_validator(mode="after")
    def validate_node(self) -> RuleNode:
        has_all = self.all_of is not None
        has_any = self.any_of is not None
        has_fact = self.fact is not None

        if not (has_all or has_any or has_fact):
            raise ValueError("Rule node must specify at least one of: 'all_of', 'any_of', or 'fact'")

        if has_fact:
            if self.op is None:
                raise ValueError(f"Leaf condition for fact '{self.fact}' must specify 'op'")
            if self.op not in VALID_OPS:
                raise ValueError(f"Invalid op '{self.op}'. Allowed: {sorted(list(VALID_OPS))}")

        return self

    def is_leaf(self) -> bool:
        return self.fact is not None and self.op is not None


class ObligationSchema(BaseModel):
    """Schema for a single legal obligation in the rulebook."""
    obligation_id: str = Field(..., description="Unique obligation ID (e.g. OBL-COMMON-001)")
    title: str = Field(..., description="Title of the regulatory requirement")
    layer: Literal["common", "food", "clothing", "salon", "vehicle_parts"] = Field(
        ..., description="Regulatory layer"
    )
    authority: str = Field(..., description="Enforcing legal authority")
    source_id: str = Field(..., description="Source identifier in statutory register")
    source_paragraph: str = Field(..., description="Statute section or gazette citation")
    source_text: str = Field(..., description="Statutory or regulatory legal quote")
    documents_needed: List[str] = Field(default_factory=list, description="Prescribed application documents")
    rule: RuleNode = Field(..., description="Executable 3-valued boolean rule tree")

    actor: Optional[str] = Field(default="business_owner", description="Responsible actor")
    action: Optional[str] = Field(default="comply_with_statute", description="Required action")

    @field_validator("layer")
    @classmethod
    def validate_layer(cls, v: str) -> str:
        if v not in VALID_LAYERS:
            raise ValueError(f"Layer '{v}' is invalid. Allowed: {sorted(list(VALID_LAYERS))}")
        return v


class RulebookSchema(BaseModel):
    """Root container for list of obligations."""
    obligations: List[ObligationSchema]


class ObligationEvaluationResult(BaseModel):
    """Auditable result for a single evaluated obligation."""
    obligation_id: str
    title: str
    status: Literal["APPLICABLE", "NOT_APPLICABLE", "UNKNOWN"]
    layer: str
    authority: str
    triggering_facts: Dict[str, Any] = Field(default_factory=dict)
    missing_facts: List[str] = Field(default_factory=list)
    source_id: str
    source_paragraph: str
    source_text: str
    documents_needed: List[str] = Field(default_factory=list)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)


class SummaryCounts(BaseModel):
    applicable_count: int
    unknown_count: int
    not_applicable_count: int
    total_evaluated: int

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)


class GroupedObligations(BaseModel):
    applicable: List[ObligationEvaluationResult] = Field(default_factory=list)
    unknown: List[ObligationEvaluationResult] = Field(default_factory=list)
    not_applicable: List[ObligationEvaluationResult] = Field(default_factory=list)


class FollowUpQuestion(BaseModel):
    fact: str
    question: str
    question_en: Optional[str] = None
    question_si: Optional[str] = None
    type: Literal["boolean", "select", "number", "text"] = "boolean"
    options: List[Any] = Field(default_factory=list)

    def __init__(self, **data: Any):
        if "question" in data and "question_en" not in data:
            data["question_en"] = data["question"]
        elif "question_en" in data and "question" not in data:
            data["question"] = data["question_en"]
        super().__init__(**data)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)


class ComplianceEvaluationResponse(BaseModel):
    business_id: str
    business_type: str
    summary: SummaryCounts
    grouped_obligations: GroupedObligations
    obligations: List[ObligationEvaluationResult]
    follow_up_questions: List[FollowUpQuestion]
    disclaimer: str = (
        "This evaluation is preliminary decision-support generated deterministically "
        "using 3-valued Kleene rule logic. It does not constitute formal legal advice."
    )
