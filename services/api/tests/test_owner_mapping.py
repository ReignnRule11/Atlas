from unittest.mock import MagicMock
from uuid import uuid4

from app.core.auth import AuthenticatedIdentity
from app.core.owners import get_or_create_owner
from app.domain.models import Owner


def test_existing_owner_is_returned_without_creating_duplicate():
    owner = Owner(id=uuid4(), auth_provider="https://issuer.example.test/", auth_subject="user-1")
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = owner

    result = get_or_create_owner(
        db,
        AuthenticatedIdentity(issuer="https://issuer.example.test/", subject="user-1"),
    )

    assert result is owner
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_new_owner_is_created_from_verified_issuer_and_subject():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.refresh.side_effect = lambda value: setattr(value, "id", uuid4())

    result = get_or_create_owner(
        db,
        AuthenticatedIdentity(issuer="https://issuer.example.test/", subject="user-2"),
    )

    assert result.auth_provider == "https://issuer.example.test/"
    assert result.auth_subject == "user-2"
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)
