from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    headline: str | None = Field(default=None, max_length=180)
    summary: str | None = None
    location: str | None = Field(default=None, max_length=160)


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    headline: str | None = Field(default=None, max_length=180)
    summary: str | None = None
    location: str | None = Field(default=None, max_length=160)


class ProfileRead(BaseModel):
    id: UUID
    owner_id: UUID
    display_name: str
    headline: str | None
    summary: str | None
    location: str | None
    visibility: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}}
