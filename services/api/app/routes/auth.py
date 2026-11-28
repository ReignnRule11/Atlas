from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedIdentity, get_current_identity
from app.core.owners import get_or_create_owner
from app.db.session import SessionLocal


router = APIRouter(prefix="/auth", tags=["authentication"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/me")
def authenticated_identity(
    identity: AuthenticatedIdentity = Depends(get_current_identity),
) -> dict[str, str]:
    return {"issuer": identity.issuer, "subject": identity.subject}


@router.get("/owner")
def authenticated_owner(
    identity: AuthenticatedIdentity = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    owner = get_or_create_owner(db, identity)
    return {"owner_id": str(owner.id)}
