from app.db.base import Base
from app.domain.models import EvidenceItem, EvidenceStatus, Owner, ProfessionalProfile, Project, Skill, Visibility


def test_identity_and_proof_tables_are_registered():
    assert {
        "owners",
        "professional_profiles",
        "skills",
        "experiences",
        "projects",
        "evidence_items",
    }.issubset(Base.metadata.tables)


def test_profile_and_evidence_default_to_private_and_unverified():
    profile = ProfessionalProfile(owner_id=None, display_name="Example")
    evidence = EvidenceItem(project_id=None, title="Repository contribution")
    assert profile.visibility == Visibility.PRIVATE
    assert evidence.visibility == Visibility.PRIVATE
    assert evidence.verification_status == EvidenceStatus.SELF_REPORTED


def test_evidence_verification_requires_auditor_and_timestamp_constraint():
    constraints = {
        constraint.name
        for constraint in EvidenceItem.__table__.constraints
    }
    assert "ck_verified_evidence_has_auditor" in constraints


def test_owner_identity_is_unique_per_provider_subject():
    constraints = {
        constraint.name
        for constraint in Owner.__table__.constraints
    }
    assert "uq_owners_provider_subject" in constraints


def test_skills_are_attributed_to_a_profile_and_have_source_constraint():
    constraints = {
        constraint.name
        for constraint in Skill.__table__.constraints
    }
    assert "ck_skill_source" in constraints
    assert "uq_skill_profile_name" in constraints
