from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.models import ProfessionalProfile, Skill
from app.routes.profiles import get_db, get_owner_id
from app.schemas.professional_records import SkillCreate, SkillRead


router = APIRouter(prefix="/profiles/me/skills", tags=["skills"])


def _profile(db: Session, owner_id: UUID) -> ProfessionalProfile:
    profile = db.query(ProfessionalProfile).filter(ProfessionalProfile.owner_id == owner_id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("", response_model=list[SkillRead])
def list_skills(owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = _profile(db, owner_id)
    return db.query(Skill).filter(Skill.profile_id == profile.id).order_by(Skill.created_at.asc()).all()


@router.post("", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
def add_skill(payload: SkillCreate, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = _profile(db, owner_id)
    skill = Skill(profile_id=profile.id, name=payload.name, proficiency=payload.proficiency, source="self_reported")
    db.add(skill)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Skill already exists on this profile") from exc
    db.refresh(skill)
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_id: UUID, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = _profile(db, owner_id)
    skill = db.query(Skill).filter(Skill.id == skill_id, Skill.profile_id == profile.id).first()
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
