from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base


class Visibility(str, enum.Enum):
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PUBLIC = "public"


class EvidenceStatus(str, enum.Enum):
    SELF_REPORTED = "self_reported"
    PENDING_REVIEW = "pending_review"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Owner(Base):
    """Local Atlas owner mapped to an external identity-provider subject.

    Authentication credentials and sessions remain with the identity provider.
    """
    __tablename__ = "owners"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_provider: Mapped[str] = mapped_column(String(40), nullable=False)
    auth_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("auth_provider", "auth_subject", name="uq_owners_provider_subject"),
        CheckConstraint("length(auth_provider) > 0", name="ck_owners_provider_nonempty"),
        CheckConstraint("length(auth_subject) > 0", name="ck_owners_subject_nonempty"),
    )

    profile: Mapped[ProfessionalProfile | None] = relationship(back_populates="owner", cascade="all, delete-orphan", uselist=False)


class ProfessionalProfile(Base):
    __tablename__ = "professional_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("owners.id", ondelete="CASCADE"), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    headline: Mapped[str | None] = mapped_column(String(180))
    summary: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(160))
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility, values_callable=lambda values: [item.value for item in values], name="profile_visibility"), nullable=False, default=Visibility.PRIVATE, server_default=Visibility.PRIVATE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (CheckConstraint("length(display_name) > 0", name="ck_profile_display_name_nonempty"),)

    owner: Mapped[Owner] = relationship(back_populates="profile")
    skills: Mapped[list[Skill]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    experiences: Mapped[list[Experience]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    projects: Mapped[list[Project]] = relationship(back_populates="profile", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("professional_profiles.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    proficiency: Mapped[str | None] = mapped_column(String(40))
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="self_reported", server_default="self_reported")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("profile_id", "name", name="uq_skill_profile_name"),
        CheckConstraint("source IN ('self_reported', 'imported', 'assessed')", name="ck_skill_source"),
        CheckConstraint("length(name) > 0", name="ck_skill_name_nonempty"),
    )

    profile: Mapped[ProfessionalProfile] = relationship(back_populates="skills")


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("professional_profiles.id", ondelete="CASCADE"), nullable=False)
    organization: Mapped[str] = mapped_column(String(160), nullable=False)
    role: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    started_on: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_on: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("ended_on IS NULL OR started_on IS NULL OR ended_on >= started_on", name="ck_experience_date_order"),
        Index("ix_experiences_profile", "profile_id"),
    )

    profile: Mapped[ProfessionalProfile] = relationship(back_populates="experiences")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("professional_profiles.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    project_url: Mapped[str | None] = mapped_column(String(2048))
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility, values_callable=lambda values: [item.value for item in values], name="project_visibility"), nullable=False, default=Visibility.PRIVATE, server_default=Visibility.PRIVATE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (CheckConstraint("length(title) > 0", name="ck_project_title_nonempty"),)

    profile: Mapped[ProfessionalProfile] = relationship(back_populates="projects")
    evidence: Mapped[list[EvidenceItem]] = relationship(back_populates="project", cascade="all, delete-orphan")


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    evidence_url: Mapped[str | None] = mapped_column(String(2048))
    provenance: Mapped[str] = mapped_column(String(40), nullable=False, default="owner_submitted", server_default="owner_submitted")
    verification_status: Mapped[EvidenceStatus] = mapped_column(Enum(EvidenceStatus, values_callable=lambda values: [item.value for item in values], name="evidence_status"), nullable=False, default=EvidenceStatus.SELF_REPORTED, server_default=EvidenceStatus.SELF_REPORTED.value)
    verifier_owner_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("owners.id", ondelete="SET NULL"))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility, values_callable=lambda values: [item.value for item in values], name="evidence_visibility"), nullable=False, default=Visibility.PRIVATE, server_default=Visibility.PRIVATE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("length(title) > 0", name="ck_evidence_title_nonempty"),
        CheckConstraint("provenance IN ('owner_submitted', 'connected_source', 'third_party')", name="ck_evidence_provenance"),
        CheckConstraint(
            "(verification_status = 'verified' AND verifier_owner_id IS NOT NULL AND verified_at IS NOT NULL) OR "
            "(verification_status <> 'verified' AND verified_at IS NULL)",
            name="ck_verified_evidence_has_auditor",
        ),
        Index("ix_evidence_project", "project_id"),
        Index("ix_evidence_status", "verification_status"),
    )

    project: Mapped[Project] = relationship(back_populates="evidence")
