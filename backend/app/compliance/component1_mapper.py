"""
Component 2 — Component 1 Output Mapper

Documents the field mapping from Component 1's business profile output
to Component 2's BusinessProfile schema.

Component 1 expected output fields (from its feasibility analysis):
  - business_name: str                (ignored by C2 — no personal data)
  - sector: str                       → business_type
  - entity_type: str                  → legal_form
  - municipal_council: str            → local_authority
  - employees_count: int              → employee_band
  - annual_revenue_lkr: float         (ignored by C2 — not a trigger condition)
  - activities: List[str]             → activity
  - handles_food: Optional[bool]      → handles_food (direct)
  - has_physical_premises: Optional[bool] → has_physical_premises (direct)
  - is_manufacturing: Optional[bool]  → is_manufacturing (direct)
  - is_importing: Optional[bool]      → is_importing (direct)
  - jurisdiction: Optional[str]       → jurisdiction (direct)

All unmapped or unknown fields result in None (UNKNOWN) in the profile.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from backend.app.compliance.schemas import BusinessProfile, EmployeeBand, LegalForm

# ---------------------------------------------------------------------------
# Sector → business_type mapping
# ---------------------------------------------------------------------------
_SECTOR_MAP: Dict[str, str] = {
    "food": "food_business",
    "bakery": "bakery",
    "cake": "cake_shop",
    "sweets": "sweets_shop",
    "restaurant": "restaurant",
    "clothing": "clothing_retail",
    "saloon": "beauty_salon",
    "vehicle": "vehicle_parts_retail",
}

# ---------------------------------------------------------------------------
# Entity type → legal_form mapping
# ---------------------------------------------------------------------------
_ENTITY_TYPE_MAP: Dict[str, str] = {
    "sole proprietorship": LegalForm.SOLE_PROPRIETORSHIP,
    "partnership": LegalForm.PARTNERSHIP,
    "private limited": LegalForm.PRIVATE_LIMITED,
    "private limited company": LegalForm.PRIVATE_LIMITED,
}

# ---------------------------------------------------------------------------
# Employee count → EmployeeBand mapping
# ---------------------------------------------------------------------------
def _employees_to_band(count: Optional[int]) -> Optional[EmployeeBand]:
    if count is None:
        return None
    if count == 0:
        return EmployeeBand.NONE
    if count < 10:
        return EmployeeBand.MICRO
    if count < 50:
        return EmployeeBand.SMALL
    return EmployeeBand.MEDIUM


def map_from_component1(c1_data: Dict[str, Any]) -> BusinessProfile:
    """
    Convert a Component 1 business profile dict into a Component 2 BusinessProfile.

    Parameters
    ----------
    c1_data : dict
        The raw dict from Component 1's output (e.g. from the /evaluate endpoint
        request body or stored profile). Unknown keys are silently ignored.

    Returns
    -------
    BusinessProfile
        A BusinessProfile with all resolvable fields set; unknown facts are None.
    """
    sector = (c1_data.get("sector") or "").lower().strip()
    entity_type = (c1_data.get("entity_type") or "").lower().strip()

    return BusinessProfile(
        business_type=_SECTOR_MAP.get(sector),
        activity=c1_data.get("activities"),
        local_authority=c1_data.get("municipal_council"),
        handles_food=c1_data.get("handles_food"),
        has_physical_premises=c1_data.get("has_physical_premises"),
        employee_band=_employees_to_band(c1_data.get("employees_count")),
        is_manufacturing=c1_data.get("is_manufacturing"),
        is_importing=c1_data.get("is_importing"),
        legal_form=_ENTITY_TYPE_MAP.get(entity_type),
        jurisdiction=c1_data.get("jurisdiction"),
    )
