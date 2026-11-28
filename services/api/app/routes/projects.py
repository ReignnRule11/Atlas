from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.domain.models import ProfessionalProfile, Project, Visibility
from app.routes.profiles import get_db, get_owner_id
from app.schemas.proof import ProjectCreate, ProjectRead, ProjectUpdate


router = APIRouter(prefix="/profiles/me/projects", tags=["projects"])


def _profile(db: Session, owner_id: UUID) -> ProfessionalProfile:
    profile = db.query(ProfessionalProfile).filter(ProfessionalProfile.owner_id == owner_id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def _project(db: Session, profile_id: UUID, project_id: UUID) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.profile_id == profile_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = _profile(db, owner_id)
    return db.query(Project).filter(Project.profile_id == profile.id).order_by(Project.created_at.desc()).all()


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = _profile(db, owner_id)
    project = Project(profile_id=profile.id, visibility=Visibility.PRIVATE, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: UUID, payload: ProjectUpdate, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = _profile(db, owner_id)
    project = _project(db, profile.id, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: UUID, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = _profile(db, owner_id)
    project = _project(db, profile.id, project_id)
    db.delete(project)
    db.commit()
