"""
Component 2 — Data Contract & Pydantic Schemas (schemas.py)

Exports canonical Pydantic models:
- Obligation: statutory legal obligation enforcing evidence, effective_from, and reviewer_status when active
- Rule: boolean rule tree using all/any with ops eq, in, gte, returning 'unknown' for missing facts
- Evidence: {doc_id, page, quote, url}
- BusinessProfile: incoming profile with unknown defaults for all optional/sector facts
"""

from engine.schemas import (
    Evidence,
    Rule,
    Obligation,
    BusinessProfile,
    LocationSchema,
    BusinessProfileInput,
    LeafCondition,
    RuleNode,
    ObligationSchema,
    RulebookSchema,
    ObligationEvaluationResult,
    SummaryCounts,
    GroupedObligations,
    FollowUpQuestion,
    ComplianceEvaluationResponse,
    VALID_OPS,
    VALID_RULE_OPS,
    VALID_LAYERS,
)

__all__ = [
    "Evidence",
    "Rule",
    "Obligation",
    "BusinessProfile",
    "LocationSchema",
    "BusinessProfileInput",
    "LeafCondition",
    "RuleNode",
    "ObligationSchema",
    "RulebookSchema",
    "ObligationEvaluationResult",
    "SummaryCounts",
    "GroupedObligations",
    "FollowUpQuestion",
    "ComplianceEvaluationResponse",
    "VALID_OPS",
    "VALID_RULE_OPS",
    "VALID_LAYERS",
]
