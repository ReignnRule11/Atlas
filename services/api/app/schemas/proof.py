from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


def _validate_optional_url(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if not value.startswith(("https://", "http://")):
        raise ValueError("URL must use http:// or https://")
    return value


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None
    project_url: str | None = Field(default=None, max_length=2048)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Project title cannot be blank")
        return value

    @field_validator("project_url")
    @classmethod
    def validate_project_url(cls, value: str | None) -> str | None:
        return _validate_optional_url(value)


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    project_url: str | None = Field(default=None, max_length=2048)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Project title cannot be null")
        value = value.strip()
        if not value:
            raise ValueError("Project title cannot be blank")
        return value

    @field_validator("project_url")
    @classmethod
    def validate_project_url(cls, value: str | None) -> str | None:
        return _validate_optional_url(value)


class ProjectRead(BaseModel):
    id: UUID
    title: str
    description: str | None
    project_url: str | None
    visibility: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EvidenceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = None
    evidence_url: str | None = Field(default=None, max_length=2048)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Evidence title cannot be blank")
        return value

    @field_validator("evidence_url")
    @classmethod
    def validate_evidence_url(cls, value: str | None) -> str | None:
        return _validate_optional_url(value)


class EvidenceRead(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    description: str | None
    evidence_url: str | None
    provenance: str
    verification_status: str
    visibility: str
    created_at: datetime

    model_config = {"from_attributes": True}
