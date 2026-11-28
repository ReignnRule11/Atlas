from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedIdentity
from app.domain.models import Owner


def get_or_create_owner(db: Session, identity: AuthenticatedIdentity) -> Owner:
    """Resolve a verified external identity to its stable Atlas owner record."""
    owner = (
        db.query(Owner)
        .filter(
            Owner.auth_provider == identity.issuer,
            Owner.auth_subject == identity.subject,
        )
        .first()
    )
    if owner is not None:
        return owner

    owner = Owner(auth_provider=identity.issuer, auth_subject=identity.subject)
    db.add(owner)
    try:
        db.commit()
    except IntegrityError:
        # A concurrent request may have created the same provider/subject pair.
        db.rollback()
        owner = (
            db.query(Owner)
            .filter(
                Owner.auth_provider == identity.issuer,
                Owner.auth_subject == identity.subject,
            )
            .first()
        )
        if owner is None:
            raise
        return owner

    db.refresh(owner)
    return owner
