"""Validated input contract and normalization for Component 2 business profiles."""

from __future__ import annotations

from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from backend.app.compliance.schemas import (
    BusinessProfile,
    EmployeeBand,
    LegalForm,
)


_BUSINESS_TYPE_ALIASES = {
    "food": "food_business",
    "food and beverage": "food_business",
    "food & beverage": "food_business",
    "grocery": "food_business",
    "grocery / mini-mart": "food_business",
    "grocery / mini mart": "food_business",
    "mini-mart": "food_business",
    "minimart": "food_business",
    "clothing": "clothing_retail",
    "clothing / garment": "clothing_retail",
    "garment": "clothing_retail",
    "apparel": "clothing_retail",
    "salon": "beauty_salon",
    "salon / beauty": "beauty_salon",
    "saloon": "beauty_salon",
    "vehicle": "vehicle_parts_retail",
    "vehicle_parts": "vehicle_parts_retail",
    "vehicle parts": "vehicle_parts_retail",
    "vehicle repair": "vehicle_parts_retail",
    "vehicle spare parts": "vehicle_parts_retail",
    "vehicle spare-parts, repair, and reselling businesses": "vehicle_parts_retail",
    "vehicle spare parts, repair, and reselling businesses": "vehicle_parts_retail",
    "vehicle parts, repair, and reselling": "vehicle_parts_retail",
}
_SECTOR_ALIASES = {
    "food and beverage": "food",
    "food & beverage": "food",
    "grocery": "food",
    "grocery / mini-mart": "food",
    "grocery / mini mart": "food",
    "mini-mart": "food",
    "minimart": "food",
    "clothing / garment": "clothing",
    "garment": "clothing",
    "apparel": "clothing",
    "salon / beauty": "salon",
    "saloon": "salon",
    "vehicle": "vehicle_parts",
    "vehicle parts": "vehicle_parts",
    "vehicle repair": "vehicle_parts",
    "vehicle spare parts": "vehicle_parts",
    "vehicle spare-parts, repair, and reselling businesses": "vehicle_parts",
    "vehicle spare parts, repair, and reselling businesses": "vehicle_parts",
    "vehicle parts, repair, and reselling": "vehicle_parts",
}

_LEGAL_FORM_ALIASES = {
    "sole proprietorship": LegalForm.SOLE_PROPRIETORSHIP,
    "sole proprietor": LegalForm.SOLE_PROPRIETORSHIP,
    "sole_proprietorship": LegalForm.SOLE_PROPRIETORSHIP,
    "partnership": LegalForm.PARTNERSHIP,
    "private limited": LegalForm.PRIVATE_LIMITED,
    "private limited company": LegalForm.PRIVATE_LIMITED,
    "private_limited": LegalForm.PRIVATE_LIMITED,
    "pvt ltd": LegalForm.PRIVATE_LIMITED,
    "other": LegalForm.OTHER,
}


def _normalize_province(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    stripped = value.strip()
    return (
        "Western Province"
        if stripped.casefold() in {"western", "western province"}
        else stripped
    )


def _normalize_district(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    stripped = value.strip()
    suffix = " district"
    canonical = (
        stripped[: -len(suffix)].strip()
        if stripped.casefold().endswith(suffix)
        else stripped
    )
    if canonical.casefold() == "colombo":
        return "Colombo"
    return canonical


class BusinessContextRequest(BaseModel):
    """API input. Omitted facts remain unknown rather than being inferred as false."""

    business_type: Optional[str] = None
    sector: Optional[str] = None
    location: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    local_authority: Optional[str] = None
    ownership: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("ownership", "ownership_structure", "legal_form"),
    )
    employees: Optional[int] = Field(
        default=None,
        ge=0,
        validation_alias=AliasChoices(
            "employees", "employees_count", "number_of_employees"
        ),
    )
    products_services: List[str] = Field(default_factory=list, max_length=40)
    business_size: Optional[str] = None
    activities: List[str] = Field(default_factory=list, max_length=40)
    handles_food: Optional[bool] = None
    has_physical_premises: Optional[bool] = None
    is_manufacturing: Optional[bool] = None
    is_importing: Optional[bool] = None
    serves_cooked_food: Optional[bool] = None
    sells_alcohol: Optional[bool] = None
    uses_chemicals_or_cosmetics: Optional[bool] = None
    handles_waste_oil_or_batteries: Optional[bool] = None
    turnover_band: Optional[str] = None

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    @field_validator("products_services", "activities")
    @classmethod
    def normalize_string_lists(cls, values: List[str]) -> List[str]:
        return [value.strip() for value in values if value and value.strip()]

    def to_business_context(self) -> dict:
        """Return the stable, machine-readable profile shape requested by the API."""
        raw_type = (self.business_type or self.sector or "").strip()
        normalized_type = _BUSINESS_TYPE_ALIASES.get(
            raw_type.lower(), raw_type.lower() or None
        )
        raw_sector = (self.sector or "").strip().lower()
        normalized_sector = _SECTOR_ALIASES.get(raw_sector, raw_sector or None)
        if normalized_sector is None:
            normalized_sector = {
                "food_business": "food",
                "bakery": "food",
                "cake_shop": "food",
                "sweets_shop": "food",
                "restaurant": "food",
                "clothing_retail": "clothing",
                "beauty_salon": "salon",
                "vehicle_parts_retail": "vehicle_parts",
            }.get(normalized_type)
        normalized_ownership = (self.ownership or "").strip().lower()
        ownership_value = _LEGAL_FORM_ALIASES.get(normalized_ownership)
        province = _normalize_province(self.province)
        district = _normalize_district(self.district)
        return {
            "business_type": normalized_type,
            "sector": normalized_sector,
            "location": {
                "address": self.location,
                "district": district,
                "province": province,
                "local_authority": self.local_authority,
            },
            "ownership": (
                ownership_value.value if ownership_value else normalized_ownership or None
            ),
            "employees": self.employees,
            "products_services": self.products_services,
            "activities": self.activities,
            "business_size": self.business_size.lower() if self.business_size else None,
            "premises": {"has_physical_premises": self.has_physical_premises},
            "operational_characteristics": {
                "handles_food": self.handles_food,
                "is_manufacturing": self.is_manufacturing,
                "is_importing": self.is_importing,
                "serves_cooked_food": self.serves_cooked_food,
                "sells_alcohol": self.sells_alcohol,
                "uses_chemicals_or_cosmetics": self.uses_chemicals_or_cosmetics,
                "handles_waste_oil_or_batteries": self.handles_waste_oil_or_batteries,
                "turnover_band": self.turnover_band,
            },
        }

    def missing_profile_fields(self) -> List[str]:
        """List core facts that are still needed for a complete assessment."""
        missing: List[str] = []
        if not (self.business_type or self.sector):
            missing.append("business_type_or_sector")
        if not (
            self.location
            or self.province
            or self.district
            or self.local_authority
        ):
            missing.append("location")
        if not self.ownership:
            missing.append("ownership")
        if self.employees is None:
            missing.append("employees")
        if not self.products_services and not self.activities:
            missing.append("products_services")
        if not self.business_size:
            missing.append("business_size")
        return missing

    def to_rule_engine_profile(self) -> BusinessProfile:
        """Normalize the rich API profile to the deterministic rule-engine contract."""
        raw_type = (self.business_type or self.sector or "").strip()
        normalized_type = _BUSINESS_TYPE_ALIASES.get(raw_type.lower(), raw_type.lower())
        legal_form = _LEGAL_FORM_ALIASES.get((self.ownership or "").lower())
        employee_band = _employee_count_to_band(self.employees)
        jurisdiction = _normalize_province(self.province) or _normalize_district(
            self.district
        )

        return BusinessProfile(
            business_type=normalized_type or None,
            activity=self.activities or self.products_services or None,
            local_authority=self.local_authority,
            handles_food=self.handles_food,
            has_physical_premises=self.has_physical_premises,
            employee_band=employee_band,
            is_manufacturing=self.is_manufacturing,
            is_importing=self.is_importing,
            legal_form=legal_form,
            jurisdiction=jurisdiction,
        )


def _employee_count_to_band(count: Optional[int]) -> Optional[EmployeeBand]:
    if count is None:
        return None
    if count == 0:
        return EmployeeBand.NONE
    if count < 10:
        return EmployeeBand.MICRO
    if count < 50:
        return EmployeeBand.SMALL
    return EmployeeBand.MEDIUM
