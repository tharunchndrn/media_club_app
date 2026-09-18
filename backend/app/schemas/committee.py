import uuid

from pydantic import BaseModel, ConfigDict, Field


class CommitteeMemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=150)
    academic_year: str = Field(min_length=1, max_length=20)
    photo_url: str | None = Field(default=None, max_length=500)
    linkedin_url: str | None = Field(default=None, max_length=500)
    sort_order: int = 0


class CommitteeMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    position: str
    academic_year: str
    photo_url: str | None
    linkedin_url: str | None
    sort_order: int
