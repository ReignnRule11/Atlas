from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.domain.models import EvidenceItem, EvidenceStatus, ProfessionalProfile, Project, Visibility
from app.routes.profiles import get_db, get_owner_id
from app.schemas.proof import EvidenceCreate, EvidenceRead


router = APIRouter(prefix="/profiles/me/projects/{project_id}/evidence", tags=["proof evidence"])


def _owned_project(db: Session, owner_id: UUID, project_id: UUID) -> Project:
    profile = db.query(ProfessionalProfile).filter(ProfessionalProfile.owner_id == owner_id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    project = db.query(Project).filter(Project.id == project_id, Project.profile_id == profile.id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=list[EvidenceRead])
def list_evidence(project_id: UUID, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    _owned_project(db, owner_id, project_id)
    return db.query(EvidenceItem).filter(EvidenceItem.project_id == project_id).order_by(EvidenceItem.created_at.desc()).all()


@router.post("", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED)
def add_evidence(project_id: UUID, payload: EvidenceCreate, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    _owned_project(db, owner_id, project_id)
    evidence = EvidenceItem(
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        evidence_url=payload.evidence_url,
        provenance="owner_submitted",
        verification_status=EvidenceStatus.SELF_REPORTED,
        visibility=Visibility.PRIVATE,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evidence(project_id: UUID, evidence_id: UUID, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    _owned_project(db, owner_id, project_id)
    evidence = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_id, EvidenceItem.project_id == project_id).first()
    if evidence is None:
        raise HTTPException(status_code=404, detail="Evidence not found")
    db.delete(evidence)
    db.commit()
