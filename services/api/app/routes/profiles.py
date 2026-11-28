from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedIdentity, get_current_identity
from app.core.owners import get_or_create_owner
from app.db.session import SessionLocal
from app.domain.models import ProfessionalProfile, Visibility
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate


router = APIRouter(prefix="/profiles", tags=["profiles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_owner_id(
    identity: AuthenticatedIdentity = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> UUID:
    return get_or_create_owner(db, identity).id


@router.get("/me", response_model=ProfileRead)
def get_my_profile(owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = db.query(ProfessionalProfile).filter(ProfessionalProfile.owner_id == owner_id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/me", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
def create_my_profile(payload: ProfileCreate, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    existing = db.query(ProfessionalProfile).filter(ProfessionalProfile.owner_id == owner_id).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Profile already exists")
    profile = ProfessionalProfile(owner_id=owner_id, display_name=payload.display_name.strip(), headline=payload.headline, summary=payload.summary, location=payload.location, visibility=Visibility.PRIVATE)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.patch("/me", response_model=ProfileRead)
def update_my_profile(payload: ProfileUpdate, owner_id: UUID = Depends(get_owner_id), db: Session = Depends(get_db)):
    profile = db.query(ProfessionalProfile).filter(ProfessionalProfile.owner_id == owner_id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "display_name" and value is not None:
            value = value.strip()
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
