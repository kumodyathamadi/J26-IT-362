"""
Component 2 — Deterministic Three-Valued Applicability Engine

Core design principle
---------------------
  The LLM may only *phrase* results; it must NEVER decide applicability.
  All applicability decisions are made by this module using pure Python
  logic against the obligation rulebook and the BusinessProfile.

Three-valued logic
------------------
  For every trigger condition in applies_if:
    - If the profile field is None  → the fact is UNKNOWN (never False)
    - If the condition is met       → True
    - If the condition is not met   → False

  Verdict rules:
    - ANY False trigger fact        → NOT_APPLICABLE
    - ANY UNKNOWN trigger fact      → UNKNOWN  (unless already NOT_APPLICABLE)
    - ALL True trigger facts        → check exceptions
      - Any unconfirmed exception   → CONDITIONAL
      - Otherwise                   → APPLICABLE
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from backend.app.compliance.schemas import (
    ApplicabilityStatus,
    BusinessProfile,
    ComplianceAnalysisResponse,
    EvidenceChunk,
    ObligationResult,
    ObligationRule,
    ReviewerStatus,
)
from backend.app.compliance.rulebook_loader import get_obligations
from backend.app.compliance.source_registry import get_source_details

logger = logging.getLogger(__name__)
_REPO_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Scope Guard Configuration
# ---------------------------------------------------------------------------
COVERED_AUTHORITIES = {
    "colombo municipal council",
    "kotte municipal council",
    "dehiwala-mount lavinia municipal council",
}
COVERED_JURISDICTIONS = {
    "colombo",
    "colombo district",
    "western province",
    "sri lanka (national)",
    "national",
}


def is_in_scope(profile: BusinessProfile) -> Tuple[bool, Optional[str]]:
    """
    Check if the profile's local_authority and jurisdiction are covered by verified rules.
    Returns (True, None) if in scope or unknown, or (False, reason) if out of scope.
    """
    if profile.local_authority:
        la = profile.local_authority.lower().strip()
        if not any(cov in la or la in cov for cov in COVERED_AUTHORITIES):
            return False, f"Local authority '{profile.local_authority}' is not yet covered by our verified rules."

    if profile.jurisdiction:
        jur = profile.jurisdiction.lower().strip()
        if not any(cov in jur or jur in cov for cov in COVERED_JURISDICTIONS):
            return False, f"Province/Jurisdiction '{profile.jurisdiction}' is not yet covered by our verified rules."

    return True, None


# ---------------------------------------------------------------------------
# Three-valued single-condition evaluators
# ---------------------------------------------------------------------------

TriVal = Optional[bool]  # True | False | None (unknown)


def _eval_business_type(
    required_types: List[str], profile: BusinessProfile
) -> Tuple[TriVal, Optional[str], Optional[str]]:
    """Returns (verdict, missing_field_or_None, false_reason_or_None)."""
    if profile.business_type is None:
        return None, "business_type", None
    is_match = profile.business_type.lower() in [t.lower() for t in required_types]
    if not is_match:
        return False, None, f"Business type '{profile.business_type}' is not in required sectors ({', '.join(required_types)})"
    return True, None, None


def _eval_bool_field(
    field_name: str, required_value: bool, profile: BusinessProfile
) -> Tuple[TriVal, Optional[str], Optional[str]]:
    val = getattr(profile, field_name, None)
    if val is None:
        return None, field_name, None
    if val != required_value:
        pretty = field_name.replace("_", " ").capitalize()
        return False, None, f"{pretty} = {val} (requires {required_value})"
    return True, None, None


def _eval_jurisdiction(
    allowed: List[str], profile: BusinessProfile
) -> Tuple[TriVal, Optional[str], Optional[str]]:
    if profile.jurisdiction is None and profile.local_authority is None:
        return None, "jurisdiction", None
    check_value = profile.jurisdiction or profile.local_authority or ""
    is_match = any(a.lower() in check_value.lower() or check_value.lower() in a.lower() for a in allowed)
    if not is_match:
        return False, None, f"Jurisdiction '{check_value}' not in {', '.join(allowed)}"
    return True, None, None


def _eval_local_authority(
    allowed: List[str], profile: BusinessProfile
) -> Tuple[TriVal, Optional[str], Optional[str]]:
    if profile.local_authority is None:
        return None, "local_authority", None
    is_match = any(a.lower() in profile.local_authority.lower() or profile.local_authority.lower() in a.lower() for a in allowed)
    if not is_match:
        return False, None, f"Local authority '{profile.local_authority}' not in {', '.join(allowed)}"
    return True, None, None


def _eval_employee_band_min(
    min_employees: int, profile: BusinessProfile
) -> Tuple[TriVal, Optional[str], Optional[str]]:
    """True if the band implies at least min_employees employees."""
    if profile.employee_band is None:
        return None, "employee_band", None
    band_val = str(profile.employee_band)
    if band_val == "0":
        if min_employees > 0:
            return False, None, "Employees = 0"
        return True, None, None
    # Any non-zero band means >= 1 employee
    return True, None, None


def _eval_legal_form(
    allowed_forms: List[str], profile: BusinessProfile
) -> Tuple[TriVal, Optional[str], Optional[str]]:
    if profile.legal_form is None:
        return None, "legal_form", None
    is_match = str(profile.legal_form).lower() in [f.lower() for f in allowed_forms]
    if not is_match:
        return False, None, f"Legal form '{profile.legal_form}' not in {', '.join(allowed_forms)}"
    return True, None, None


def _has_verified_quote(rule: ObligationRule) -> bool:
    quote = rule.evidence.quote.strip()
    page_number = rule.evidence.page
    if (
        rule.reviewer_status != ReviewerStatus.VERIFIED
        or not quote
        or page_number is None
        or any(not exception.confirmed for exception in rule.exceptions)
    ):
        return False

    processed_path = (
        _REPO_ROOT
        / "data"
        / "compliance"
        / "processed"
        / f"{rule.evidence.source_id}.json"
    )
    if not processed_path.is_file():
        return False
    try:
        document = json.loads(processed_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.warning(
            "Could not verify the configured quote for obligation %s: %s",
            rule.id,
            exc,
        )
        return False

    pages = document if isinstance(document, list) else document.get("pages", [])
    return any(
        page.get("page_number", page.get("page")) == page_number
        and quote in page.get("text", "")
        for page in pages
    )


# ---------------------------------------------------------------------------
# Rule evaluator
# ---------------------------------------------------------------------------

def evaluate_rule(
    rule: ObligationRule, profile: BusinessProfile
) -> Tuple[ApplicabilityStatus, Dict[str, Any], List[str], Optional[str]]:
    """
    Evaluate a single obligation rule against a BusinessProfile.

    Returns
    -------
    status : ApplicabilityStatus
    trigger_facts : dict mapping fact-name -> evaluated value
    missing_facts : list of profile field names that are None and needed
    reason : string explanation, especially for not_identified
    """
    applies_if = rule.applies_if
    trigger_facts: Dict[str, Any] = {}
    missing_facts: List[str] = []
    false_reasons: List[str] = []

    has_false = False
    has_unknown = False

    def _record(cond_name: str, verdict: TriVal, missing: Optional[str], f_reason: Optional[str]) -> None:
        nonlocal has_false, has_unknown
        trigger_facts[cond_name] = verdict
        if verdict is False:
            has_false = True
            if f_reason:
                false_reasons.append(f_reason)
        elif verdict is None:
            has_unknown = True
            if missing and missing not in missing_facts:
                missing_facts.append(missing)

    # --- business_type ---
    if "business_type" in applies_if:
        v, m, r = _eval_business_type(applies_if["business_type"], profile)
        _record("business_type", v, m, r)

    # --- boolean flags ---
    for bool_field in ("handles_food", "has_physical_premises", "is_manufacturing", "is_importing"):
        if bool_field in applies_if:
            required = applies_if[bool_field]
            if isinstance(required, bool):
                v, m, r = _eval_bool_field(bool_field, required, profile)
                _record(bool_field, v, m, r)

    # --- jurisdiction_matches ---
    if "jurisdiction_matches" in applies_if:
        v, m, r = _eval_jurisdiction(applies_if["jurisdiction_matches"], profile)
        _record("jurisdiction", v, m, r)

    # --- local_authority_matches ---
    if "local_authority_matches" in applies_if:
        v, m, r = _eval_local_authority(applies_if["local_authority_matches"], profile)
        _record("local_authority", v, m, r)

    # --- employee_band_min ---
    if "employee_band_min" in applies_if:
        v, m, r = _eval_employee_band_min(applies_if["employee_band_min"], profile)
        _record("employee_band", v, m, r)

    # --- legal_form_matches ---
    if "legal_form_matches" in applies_if:
        v, m, r = _eval_legal_form(applies_if["legal_form_matches"], profile)
        _record("legal_form", v, m, r)

    # --- Determine verdict ---
    if has_false:
        reason_str = "; ".join(false_reasons) if false_reasons else "Trigger criteria not met"
        return ApplicabilityStatus.NOT_IDENTIFIED, trigger_facts, missing_facts, reason_str
    if has_unknown:
        return ApplicabilityStatus.UNKNOWN, trigger_facts, missing_facts, f"Missing information: {', '.join(missing_facts)}"

    # All conditions True — check exceptions or draft status
    unresolved_exceptions = [
        exc for exc in rule.exceptions if not exc.confirmed
    ]
    if unresolved_exceptions:
        exc_descs = [e.description for e in unresolved_exceptions]
        return ApplicabilityStatus.CONDITIONAL, trigger_facts, missing_facts, f"Potential exception: {'; '.join(exc_descs)}"

    if rule.reviewer_status == ReviewerStatus.DRAFT and not (rule.evidence.quote and rule.evidence.quote.strip()):
        return ApplicabilityStatus.CONDITIONAL, trigger_facts, missing_facts, "Pending legal source quote verification (reviewer_status: draft)"

    return ApplicabilityStatus.APPLICABLE, trigger_facts, missing_facts, "All verified applicability criteria met"


# ---------------------------------------------------------------------------
# Full analysis
# ---------------------------------------------------------------------------

def analyze_compliance(profile: BusinessProfile) -> ComplianceAnalysisResponse:
    """
    Run the deterministic three-valued applicability engine over all
    obligations in the rulebook and return a structured result.

    The LLM must NOT be called here. All logic is deterministic.
    """
    in_scope, scope_reason = is_in_scope(profile)

    obligations = get_obligations()
    results: List[ObligationResult] = []
    covered_business_types = {
        value.lower()
        for rule in obligations
        for value in rule.applies_if.get("business_type", [])
    }
    unsupported_business_type = (
        profile.business_type is not None
        and profile.business_type.lower() not in covered_business_types
    )
    business_type_reason = (
        f"Business type '{profile.business_type}' is not covered by the current "
        "rulebook; no absence of obligations should be inferred."
        if unsupported_business_type
        else None
    )
    if unsupported_business_type:
        result = ObligationResult(
            id="SCOPE-001",
            name="Sector-specific requirements not assessed",
            status=ApplicabilityStatus.NOT_COVERED,
            reason=business_type_reason,
            trigger_facts={"business_type": profile.business_type},
            missing_facts=[],
            authority="Relevant Sri Lankan national and local authorities",
            jurisdiction=profile.jurisdiction or profile.local_authority or "Sri Lanka",
            required_action=(
                "Consult the relevant authorities; the current obligation rulebook "
                "does not cover this business sector."
            ),
            reviewer_status=ReviewerStatus.DRAFT,
            has_verified_source=False,
            evidence=[],
            caveat=(
                "This business type is not covered by the current rulebook. "
                "No conclusion about its legal obligations can be drawn."
            ),
        )
        summary = {status.value: 0 for status in ApplicabilityStatus}
        summary[result.status.value] = 1
        return ComplianceAnalysisResponse(
            business_profile=profile,
            summary=summary,
            obligations=[result],
        )

    for rule in obligations:
        if not in_scope and rule.jurisdiction != "Sri Lanka (National)":
            results.append(
                ObligationResult(
                    id=rule.id,
                    name=rule.name,
                    status=ApplicabilityStatus.NOT_COVERED,
                    reason=scope_reason or "Not yet covered - contact the authority",
                    trigger_facts={},
                    missing_facts=[],
                    authority=rule.authority,
                    jurisdiction=rule.jurisdiction,
                    required_action=rule.required_action.strip(),
                    reviewer_status=rule.reviewer_status,
                    has_verified_source=False,
                    evidence=[],
                    caveat="This area is not yet covered in our verified database. Please consult the local council directly.",
                )
            )
            continue

        status, trigger_facts, missing_facts, reason = evaluate_rule(rule, profile)

        # Build evidence from rulebook (source-grounded, not hallucinated)
        evidence_chunks: List[EvidenceChunk] = []
        has_verified_quote = _has_verified_quote(rule)

        if rule.evidence.source_id:
            src_info = get_source_details(rule.evidence.source_id)
            url = src_info.get("url") or None
            retrieved_date = src_info.get("retrieved_date") or None
            effective_date = src_info.get("effective_date") or None
            source_title = src_info.get("title") or None

            evidence_chunks.append(
                EvidenceChunk(
                    source_id=rule.evidence.source_id,
                    page=rule.evidence.page,
                    quote=rule.evidence.quote if has_verified_quote else "",
                    url=url,
                    retrieved_date=retrieved_date,
                    effective_date=effective_date,
                    source_title=source_title,
                    authority=rule.authority,
                    reviewer_status=rule.reviewer_status,
                )
            )

        results.append(
            ObligationResult(
                id=rule.id,
                name=rule.name,
                status=status,
                reason=reason,
                trigger_facts=trigger_facts,
                missing_facts=missing_facts,
                applicability_conditions=rule.applies_if,
                exceptions=rule.exceptions,
                authority=rule.authority,
                jurisdiction=rule.jurisdiction,
                required_action=rule.required_action.strip(),
                reviewer_status=rule.reviewer_status,
                has_verified_source=has_verified_quote,
                evidence=evidence_chunks,
            )
        )

    # Summary counts
    summary = {s.value: 0 for s in ApplicabilityStatus}
    for r in results:
        summary[r.status.value] += 1

    return ComplianceAnalysisResponse(
        business_profile=profile,
        summary=summary,
        obligations=results,
    )
