from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.domain.models import Experience, ProfessionalProfile
from app.routes.profiles import get_db, get_owner_id
from app.schemas.professional_records import ExperienceCreate, ExperienceRead, ExperienceUpdate


router = APIRouter(prefix="/profiles/me/experiences", tags=["experience"])


def _profile(db: Session, owner_id: UUID) -> ProfessionalProfile:
    profile = db.query(ProfessionalProfile).filter(ProfessionalProfile.owner_id == owner_id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("", response_model=list[ExperienceRead])
def list_experiences(owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = _profile(db, owner_id)
    return db.query(Experience).filter(Experience.profile_id == profile.id).order_by(Experience.started_on.desc()).all()


@router.post("", response_model=ExperienceRead, status_code=status.HTTP_201_CREATED)
def add_experience(payload: ExperienceCreate, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = _profile(db, owner_id)
    experience = Experience(profile_id=profile.id, **payload.model_dump())
    db.add(experience)
    db.commit()
    db.refresh(experience)
    return experience


@router.patch("/{experience_id}", response_model=ExperienceRead)
def update_experience(experience_id: UUID, payload: ExperienceUpdate, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = _profile(db, owner_id)
    experience = db.query(Experience).filter(Experience.id == experience_id, Experience.profile_id == profile.id).first()
    if experience is None:
        raise HTTPException(status_code=404, detail="Experience not found")
    updates = payload.model_dump(exclude_unset=True)
    start = updates.get("started_on", experience.started_on)
    end = updates.get("ended_on", experience.ended_on)
    if start and end and end < start:
        raise HTTPException(status_code=422, detail="ended_on must be on or after started_on")
    for field, value in updates.items():
        setattr(experience, field, value)
    db.commit()
    db.refresh(experience)
    return experience


@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(experience_id: UUID, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = _profile(db, owner_id)
    experience = db.query(Experience).filter(Experience.id == experience_id, Experience.profile_id == profile.id).first()
    if experience is None:
        raise HTTPException(status_code=404, detail="Experience not found")
    db.delete(experience)
    db.commit()
