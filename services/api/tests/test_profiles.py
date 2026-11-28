from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.domain.models import ProfessionalProfile, Visibility
from app.routes.profiles import create_my_profile, get_my_profile, update_my_profile
from app.schemas.profile import ProfileCreate, ProfileUpdate


def test_create_profile_defaults_private_and_trims_name():
    owner_id = uuid4()
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.refresh.side_effect = lambda profile: setattr(profile, "id", uuid4())

    profile = create_my_profile(ProfileCreate(display_name="  Atlas User  ", headline="Engineer"), owner_id, db)

    assert profile.display_name == "Atlas User"
    assert profile.owner_id == owner_id
    assert profile.visibility == Visibility.PRIVATE
    db.commit.assert_called_once()


def test_profile_creation_rejects_duplicate():
    owner_id = uuid4()
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = object()

    with pytest.raises(HTTPException) as error:
        create_my_profile(ProfileCreate(display_name="User"), owner_id, db)

    assert error.value.status_code == 409
    db.add.assert_not_called()


def test_profile_read_is_owner_scoped_and_not_found_when_absent():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as error:
        get_my_profile(uuid4(), db)

    assert error.value.status_code == 404


def test_profile_update_not_found_when_owner_has_no_profile():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as error:
        update_my_profile(ProfileUpdate(headline="New headline"), uuid4(), db)

    assert error.value.status_code == 404
