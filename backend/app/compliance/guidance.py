"""Deterministic classification and source-aware registration guidance."""

from __future__ import annotations

from typing import Any, Dict, List

from backend.app.compliance.schemas import ApplicabilityStatus, ObligationResult


_CLASSIFICATION = {
    ApplicabilityStatus.APPLICABLE: "Mandatory",
    ApplicabilityStatus.CONDITIONAL: "Conditional",
    ApplicabilityStatus.UNKNOWN: "Conditional",
    ApplicabilityStatus.NOT_IDENTIFIED: "Not Applicable",
    ApplicabilityStatus.NOT_COVERED: "Needs Verification",
}


def classify_obligation(
    status: ApplicabilityStatus,
    has_verified_source: bool,
) -> str:
    """Keep unverified source evidence distinct from conditional profile facts."""
    if not has_verified_source:
        return "Needs Verification"
    return _CLASSIFICATION[status]


def build_obligation_output(
    result: ObligationResult,
    retrieved_evidence: List[Dict[str, Any]],
    required_documents: List[str] | None = None,
) -> Dict[str, Any]:
    candidates = sorted(
        retrieved_evidence,
        key=lambda item: float(item.get("score", 0.0)),
        reverse=True,
    )
    rule_source_id = result.evidence[0].source_id if result.evidence else None
    matched = [
        item
        for item in candidates
        if rule_source_id
        and item.get("metadata", {}).get("source_id") == rule_source_id
    ]
    evidence = matched[:2]
    evidence_sources = [
        {
            "source_id": item.get("metadata", {}).get("source_id"),
            "title": item.get("metadata", {}).get("source_title"),
            "authority": item.get("metadata", {}).get("authority"),
            "excerpt": item.get("text", ""),
            "url": item.get("metadata", {}).get("url") or None,
            "effective_date": item.get("metadata", {}).get("effective_date") or None,
            "retrieval_score": item.get("score"),
            "page": item.get("metadata", {}).get("page"),
            "section_reference": item.get("metadata", {}).get(
                "section_reference"
            ),
            "paragraph_number": item.get("metadata", {}).get(
                "paragraph_number"
            ),
            "file_type": item.get("metadata", {}).get("file_type"),
            "source_file": item.get("metadata", {}).get("corpus_file"),
            "reviewer_status": item.get("metadata", {}).get(
                "reviewer_status", "draft"
            ),
            "contains_placeholder": item.get("metadata", {}).get(
                "contains_placeholder", False
            ),
        }
        for item in evidence
    ]

    classification = classify_obligation(result.status, result.has_verified_source)
    needs_verification = classification == "Needs Verification"
    if needs_verification:
        steps = [
            "Verify the source document, applicable provision, authority, and "
            "current legal status before relying on this candidate requirement."
        ]
    else:
        steps = [result.required_action] if result.required_action else []
        steps.append(
            f"Contact {result.authority} to confirm the current application process, "
            "forms, fees, and supporting documents before filing."
        )
    if needs_verification:
        next_action = (
            "Verify this candidate requirement with an official Sri Lankan source "
            "and the responsible authority before taking action."
        )
    elif result.missing_facts:
        next_action = (
            "Complete the missing business-profile facts: "
            + ", ".join(result.missing_facts)
            + "."
        )
    elif result.status == ApplicabilityStatus.NOT_COVERED:
        next_action = (
            "Confirm the applicable requirements with the relevant local authority; "
            "this jurisdiction is not covered by the current rulebook."
        )
    elif result.status in (
        ApplicabilityStatus.CONDITIONAL,
        ApplicabilityStatus.UNKNOWN,
    ):
        next_action = (
            "Resolve the listed conditions and verify this draft guidance with "
            "the responsible authority."
        )
    else:
        next_action = (
            f"Confirm the current checklist with {result.authority} and begin "
            "the registration or licensing process."
        )

    source_reference = (
        {
            "source_id": result.evidence[0].source_id,
            "page": result.evidence[0].page,
            "quote": result.evidence[0].quote or None,
            "reviewer_status": result.reviewer_status.value,
        }
        if result.evidence
        else None
    )
    status_for_frontend = (
        "NEEDS_VERIFICATION"
        if needs_verification
        else {
            ApplicabilityStatus.APPLICABLE: "APPLICABLE",
            ApplicabilityStatus.NOT_IDENTIFIED: "NOT_APPLICABLE",
        }.get(result.status, "UNKNOWN")
    )
    priority = {
        "Mandatory": "high",
        "Conditional": "review",
        "Not Applicable": "none",
        "Needs Verification": "review",
    }[classification]
    document_checklist = required_documents or []
    documents_verified = (
        bool(document_checklist)
        and result.reviewer_status.value == "verified"
        and result.has_verified_source
    )

    return {
        "obligation_id": result.id,
        "obligation": result.name,
        "title": result.name,
        "classification": classification,
        "priority": priority,
        "status": status_for_frontend,
        "authority": result.authority,
        "jurisdiction": result.jurisdiction,
        "source_reference": source_reference,
        "source_id": (
            source_reference["source_id"] if source_reference else "not_registered"
        ),
        "source_paragraph": (
            str(source_reference["page"])
            if source_reference and source_reference["page"] is not None
            else "Reference not verified"
        ),
        "source_text": (
            evidence_sources[0]["excerpt"] if evidence_sources else ""
        ),
        "explanation": result.reason or "No explanation was supplied by the rule engine.",
        "action": result.required_action if not needs_verification else "",
        "triggering_facts": result.trigger_facts,
        "applicability_conditions": result.applicability_conditions,
        "exceptions": [
            exception.model_dump() for exception in result.exceptions
        ],
        "missing_facts": result.missing_facts,
        "required_documents": document_checklist,
        "documents_needed": document_checklist,
        "documents_status": (
            "verified" if documents_verified else
            "draft_unverified" if document_checklist else
            "not_listed"
        ),
        "documents_notice": None if documents_verified else (
            "These checklist items are draft suggestions, not verified legal "
            "requirements. Confirm the required documents directly with the authority."
            if document_checklist else
            "The current rulebook does not list a document checklist. Confirm "
            "required documents directly with the authority."
        ),
        "registration_steps": steps,
        "next_action": next_action,
        "evidence_source": evidence_sources,
        "verification_status": (
            "verified" if not needs_verification else "needs_verification"
        ),
        "has_verified_source": result.has_verified_source,
        "evidence_quality": (
            "verified_page_quote" if result.has_verified_source else "unverified_source"
        ),
    }


def build_guidance(
    obligations: List[ObligationResult],
    evidence_by_obligation: Dict[str, List[Dict[str, Any]]],
    documents_by_obligation: Dict[str, List[str]] | None = None,
) -> List[Dict[str, Any]]:
    """Produce guidance only for potential obligations, excluding clear non-applicability."""
    return [
        build_obligation_output(
            result,
            evidence_by_obligation.get(result.id, []),
            (documents_by_obligation or {}).get(result.id, []),
        )
        for result in obligations
        if result.status != ApplicabilityStatus.NOT_IDENTIFIED
        or not result.has_verified_source
    ]
