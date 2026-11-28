from fastapi import APIRouter, Depends

from app.core.auth import AuthenticatedIdentity, get_current_identity


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/me")
def authenticated_identity(
    identity: AuthenticatedIdentity = Depends(get_current_identity),
) -> dict[str, str]:
    return {"issuer": identity.issuer, "subject": identity.subject}
