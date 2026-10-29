"""
Component 2 — Fixed Shared Business Profile Schema
Shared data contract between Component 1 (Intake/Feasibility) and Component 2 (Regulatory Rule Engine).
Every field is Optional and defaults to None (null), representing 'Unknown' in Kleene logic.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class SharedBusinessProfile(BaseModel):
    """
    Fixed business profile input schema.
    Every field defaults to None, which denotes an 'unknown' state
    requiring follow-up or triggering Kleene UNKNOWN evaluations.
    """
    # Core Fields
    business_type: Optional[Literal["food", "clothing", "salon", "vehicle_parts", "other"]] = Field(
        None,
        description="Primary business classification (food, clothing, salon, vehicle_parts)",
    )
    local_authority: Optional[str] = Field(
        None,
        description="Local authority jurisdiction (e.g. Colombo Municipal Council)",
    )
    legal_form: Optional[Literal["sole_proprietorship", "partnership", "private_limited", "other"]] = Field(
        None,
        description="Legal registration form / structure",
    )
    number_of_employees: Optional[int] = Field(
        None,
        description="Total number of hired staff/employees",
    )
    province: Optional[str] = Field(
        None,
        description="Province of operation (Scope: Western Province)",
    )
    handles_food: Optional[bool] = Field(
        None,
        description="Whether the business prepares, packages, handles or sells food",
    )
    has_physical_premises: Optional[bool] = Field(
        None,
        description="Whether business operates from a physical commercial facility/shop",
    )
    is_manufacturing: Optional[bool] = Field(
        None,
        description="Whether business engages in mechanical production or fabrication",
    )
    is_importing: Optional[bool] = Field(
        None,
        description="Whether business imports commercial goods from overseas",
    )

    # Conditional Fields
    serves_cooked_food: Optional[bool] = Field(
        None,
        description="Whether business serves cooked/hot food on premises (food sector)",
    )
    sells_alcohol: Optional[bool] = Field(
        None,
        description="Whether business sells or serves liquor/alcohol (food sector)",
    )
    uses_chemicals_or_cosmetics: Optional[bool] = Field(
        None,
        description="Whether salon uses chemical agents, hair dyes, bleaches (salon sector)",
    )
    handles_waste_oil_or_batteries: Optional[bool] = Field(
        None,
        description="Whether business handles used motor oil or spent batteries (vehicle_parts sector)",
    )
    turnover_band: Optional[str] = Field(
        None,
        description="Projected annual turnover band (under_1m, 1m_10m, 10m_50m, over_50m)",
    )

    model_config = ConfigDict(extra="ignore")


class ObligationResultSchema(BaseModel):
    obligation_id: str
    title: str
    status: Literal["APPLICABLE", "NOT_APPLICABLE", "UNKNOWN"]
    triggering_facts: Dict[str, Any]
    missing_facts: List[str]
    authority: str
    source_id: str
    source_paragraph: str
    source_text: str
    documents_needed: List[str]


class AnalysisSummarySchema(BaseModel):
    total: int
    applicable: int
    not_applicable: int
    unknown: int


class FollowUpQuestionSchema(BaseModel):
    fact: str
    question_en: str
    question_si: str
    type: str
    options: List[Any]


class ComplianceAnalysisOutput(BaseModel):
    summary: AnalysisSummarySchema
    obligations: List[ObligationResultSchema]
    follow_up_questions: List[FollowUpQuestionSchema]
    disclaimer: str = (
        "Guidance only, not legal advice. Decisions are determined by a "
        "deterministic rule engine. Always verify requirements with the official authority."
    )
