from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    proficiency: str | None = Field(default=None, max_length=40)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Skill name cannot be blank")
        return value

    @field_validator("proficiency")
    @classmethod
    def normalize_proficiency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class SkillRead(BaseModel):
    id: UUID
    name: str
    proficiency: str | None
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ExperienceCreate(BaseModel):
    organization: str = Field(min_length=1, max_length=160)
    role: str = Field(min_length=1, max_length=160)
    description: str | None = None
    started_on: datetime | None = None
    ended_on: datetime | None = None

    @field_validator("organization", "role")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

    @model_validator(mode="after")
    def validate_date_order(self):
        if self.started_on and self.ended_on and self.ended_on < self.started_on:
            raise ValueError("ended_on must be on or after started_on")
        return self


class ExperienceUpdate(BaseModel):
    organization: str | None = Field(default=None, min_length=1, max_length=160)
    role: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    started_on: datetime | None = None
    ended_on: datetime | None = None

    @field_validator("organization", "role")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("This field cannot be null")
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

    @model_validator(mode="after")
    def validate_date_order(self):
        values = self.model_dump(exclude_unset=True)
        start = values.get("started_on")
        end = values.get("ended_on")
        if start and end and end < start:
            raise ValueError("ended_on must be on or after started_on")
        return self


class ExperienceRead(BaseModel):
    id: UUID
    organization: str
    role: str
    description: str | None
    started_on: datetime | None
    ended_on: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
