import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from backend.database import Base


def generate_uuid():
    return str(uuid.uuid4())


# Portable JSON column type (uses PostgreSQL JSONB on Postgres, standard JSON elsewhere)
PortableJSON = JSON().with_variant(JSONB, 'postgresql')


class User(Base):
    """
    User Entity for authentication and SME profile ownership.
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    business_profiles: Mapped[List["BusinessProfile"]] = relationship("BusinessProfile", back_populates="owner")


class BusinessProfile(Base):
    """
    SME Business Profile Entity representing registered enterprise parameters.
    """
    __tablename__ = "business_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id"), nullable=True, index=True)
    business_name: Mapped[str] = mapped_column(String, nullable=False)
    business_stage: Mapped[str] = mapped_column(String, nullable=False, index=True)
    business_category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    district: Mapped[str] = mapped_column(String, nullable=False, index=True)
    location_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner: Mapped[Optional["User"]] = relationship("User", back_populates="business_profiles")
    analysis_records: Mapped[List["AnalysisRecord"]] = relationship("AnalysisRecord", back_populates="business_profile")


class AnalysisRecord(Base):
    """
    Database Entity storing historical SME feasibility analysis runs and structured profile outputs.
    Leverages PostgreSQL JSONB columns for structured ML, SHAP, TOPSIS, and Plan outputs.
    Stores original natural language description & extraction metadata for research traceability.
    """
    __tablename__ = "analysis_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id"), nullable=True, index=True)
    business_profile_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("business_profiles.id"), nullable=True, index=True)
    business_name: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    
    business_stage: Mapped[str] = mapped_column(String, nullable=False, index=True)
    business_category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    district: Mapped[str] = mapped_column(String, nullable=False, index=True)
    feasibility_label: Mapped[str] = mapped_column(String, nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Traceability attributes
    original_business_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extraction_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(PortableJSON, nullable=True)

    # Structured JSON / JSONB columns for research pipeline artifacts
    input_profile: Mapped[Dict[str, Any]] = mapped_column(PortableJSON, nullable=False)
    structured_profile: Mapped[Dict[str, Any]] = mapped_column(PortableJSON, nullable=False)
    
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True, index=True)

    business_profile: Mapped[Optional["BusinessProfile"]] = relationship("BusinessProfile", back_populates="analysis_records")


class AnalysisAuditLog(Base):
    """
    Audit log tracking analysis lifecycle events: created, edited, rerun, deleted, restored.
    Stores timestamp, actor, inputs snapshot, and outcome for regulatory & research traceability.
    """
    __tablename__ = "analysis_audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    user_email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    record_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String, nullable=False, index=True)  # 'created', 'rerun', 'edited', 'deleted', 'restored'
    business_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    business_category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    result_label: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    result_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    inputs_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(PortableJSON, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

