from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.professional_records import ExperienceCreate, ExperienceUpdate, SkillCreate


def test_skill_name_is_trimmed_and_nonempty():
    assert SkillCreate(name="  Python  ").name == "Python"
    with pytest.raises(ValidationError):
        SkillCreate(name="   ")


def test_experience_rejects_end_before_start():
    with pytest.raises(ValidationError):
        ExperienceCreate(
            organization="Atlas",
            role="Engineer",
            started_on=datetime(2025, 1, 1, tzinfo=timezone.utc),
            ended_on=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )


def test_experience_update_rejects_null_required_fields():
    with pytest.raises(ValidationError):
        ExperienceUpdate(role=None)
