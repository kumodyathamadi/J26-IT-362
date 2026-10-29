"""
Component 2 — Pydantic Schemas

BusinessProfile: represents everything known about a business at query time.
Every field is Optional; None means 'unknown' (three-valued logic).

ObligationRule: mirrors the YAML rulebook structure for in-memory use.

AnalysisResult: the deterministic applicability verdict per obligation.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ApplicabilityStatus(str, Enum):
    """Three-valued (plus conditional) applicability verdict."""
    APPLICABLE = "applicable"          # all trigger facts are True
    CONDITIONAL = "conditional"        # triggers true but >=1 exception unresolved or unverified conditions
    NOT_IDENTIFIED = "not_identified"  # not identified for this profile (with reason, e.g. Employees = 0)
    UNKNOWN = "unknown"                # insufficient facts; never defaults to False
    NOT_COVERED = "not_covered"        # selected authority/province is not yet covered by verified rules


class ReviewerStatus(str, Enum):
    DRAFT = "draft"
    VERIFIED = "verified"


class LegalForm(str, Enum):
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    PARTNERSHIP = "partnership"
    PRIVATE_LIMITED = "private_limited"
    OTHER = "other"


class EmployeeBand(str, Enum):
    NONE = "0"          # 0 employees
    MICRO = "1_9"       # 1–9
    SMALL = "10_49"     # 10–49
    MEDIUM = "50_plus"  # 50+


# ---------------------------------------------------------------------------
# Business Profile
# ---------------------------------------------------------------------------

class BusinessProfile(BaseModel):
    """
    Represents what is known about a business at query time.
    None on any field means the fact is UNKNOWN — it must never be treated as False.

    Compatible with Component 1 output via component1_mapper.map_from_component1().
    """
    # Core identity (no NIC / personal identifiers)
    business_type: Optional[str] = Field(
        None,
        description="Primary business type, e.g. 'bakery', 'restaurant', 'clothing_retail'",
    )
    activity: Optional[List[str]] = Field(
        None,
        description="List of business activities, e.g. ['food_preparation', 'retail_sales']",
    )
    local_authority: Optional[str] = Field(
        None,
        description="Local authority name, e.g. 'Colombo Municipal Council'",
    )
    handles_food: Optional[bool] = Field(
        None,
        description="True if the business prepares, handles, or sells food to the public.",
    )
    has_physical_premises: Optional[bool] = Field(
        None,
        description="True if the business operates from a fixed physical location.",
    )
    employee_band: Optional[EmployeeBand] = Field(
        None,
        description="Approximate number-of-employees band.",
    )
    is_manufacturing: Optional[bool] = Field(
        None,
        description="True if the business manufactures or packages goods.",
    )
    is_importing: Optional[bool] = Field(
        None,
        description="True if the business imports goods from outside Sri Lanka.",
    )
    legal_form: Optional[LegalForm] = Field(
        None,
        description="Legal entity form of the business.",
    )
    jurisdiction: Optional[str] = Field(
        None,
        description="Province or district, e.g. 'Western Province'",
    )

    model_config = ConfigDict(use_enum_values=True)


# ---------------------------------------------------------------------------
# Source / Evidence
# ---------------------------------------------------------------------------

class EvidenceRef(BaseModel):
    """Pointer to a verified legal quote in the source register."""
    source_id: str
    page: Optional[int] = None
    quote: str = ""   # empty = draft; non-empty = must appear verbatim in processed text


class ExceptionDef(BaseModel):
    description: str
    source_id: str
    confirmed: bool = False


# ---------------------------------------------------------------------------
# Obligation Rule (mirrors obligations.yaml)
# ---------------------------------------------------------------------------

class ObligationRule(BaseModel):
    id: str
    name: str
    actor: str
    authority: str
    jurisdiction: str
    required_action: str
    required_documents: List[str] = Field(
        default_factory=list,
        description="Checklist items reviewed for this obligation; empty when not established.",
    )
    applies_if: Dict[str, Any] = Field(default_factory=dict)
    exceptions: List[ExceptionDef] = Field(default_factory=list)
    evidence: EvidenceRef
    effective_from: str
    reviewer_status: ReviewerStatus = ReviewerStatus.DRAFT


class ObligationRulebook(BaseModel):
    obligations: List[ObligationRule]


# ---------------------------------------------------------------------------
# Analysis Result
# ---------------------------------------------------------------------------

class EvidenceChunk(BaseModel):
    """A retrieved evidence chunk (from the rulebook or retrieval layer)."""
    source_id: str
    page: Optional[int] = None
    quote: str
    url: Optional[str] = None
    retrieved_date: Optional[str] = None
    effective_date: Optional[str] = None
    source_title: Optional[str] = None
    authority: Optional[str] = None
    reviewer_status: ReviewerStatus = ReviewerStatus.DRAFT


class ObligationResult(BaseModel):
    """Applicability verdict for a single obligation."""
    id: str
    name: str
    status: ApplicabilityStatus
    reason: Optional[str] = Field(
        None,
        description="Explanation of verdict, required for not_identified (e.g. 'Employees = 0').",
    )
    trigger_facts: Dict[str, Any] = Field(
        default_factory=dict,
        description="Profile fields that drove the verdict.",
    )
    applicability_conditions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Declared rulebook conditions; these do not imply verified law.",
    )
    exceptions: List[ExceptionDef] = Field(
        default_factory=list,
        description="Documented exceptions and whether each has been reviewed.",
    )
    missing_facts: List[str] = Field(
        default_factory=list,
        description="Profile fields that are None and needed to resolve the verdict.",
    )
    authority: str
    jurisdiction: str
    required_action: str
    reviewer_status: ReviewerStatus = ReviewerStatus.DRAFT
    evidence: List[EvidenceChunk] = Field(default_factory=list)
    has_verified_source: bool = False
    caveat: str = (
        "Rule-based guidance with AI-phrased explanations. "
        "Not legal advice. Verify with the authority or a licensed practitioner."
    )


class ComplianceAnalysisResponse(BaseModel):
    """Full response from POST /compliance/analyze."""
    business_profile: BusinessProfile
    summary: Dict[str, int] = Field(
        default_factory=dict,
        description="Counts per ApplicabilityStatus value.",
    )
    obligations: List[ObligationResult]
    caveat: str = (
        "Rule-based guidance with AI-phrased explanations. "
        "Not legal advice. Verify with the authority or a licensed practitioner."
    )
