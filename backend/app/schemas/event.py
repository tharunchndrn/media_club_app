import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EventStatus


class PhotoCreate(BaseModel):
    image_url: str = Field(min_length=1, max_length=500)
    thumb_url: str | None = Field(default=None, max_length=500)
    caption: str | None = Field(default=None, max_length=300)
    alt_text: str | None = Field(default=None, max_length=300)
    sort_order: int | None = None


class PhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_id: uuid.UUID
    image_url: str
    thumb_url: str | None
    caption: str | None
    alt_text: str | None
    sort_order: int


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    venue: str = Field(min_length=1, max_length=200)
    event_date: datetime
    academic_year: str = Field(min_length=1, max_length=20)
    cover_image_url: str | None = Field(default=None, max_length=500)
    status: EventStatus = EventStatus.DRAFT


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    venue: str | None = Field(default=None, min_length=1, max_length=200)
    event_date: datetime | None = None
    academic_year: str | None = Field(default=None, min_length=1, max_length=20)
    cover_image_url: str | None = Field(default=None, max_length=500)
    status: EventStatus | None = None


class EventSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str
    description: str
    venue: str
    event_date: datetime
    cover_image_url: str | None
    status: EventStatus
    academic_year: str
    created_at: datetime


class EventDetail(EventSummary):
    photos: list[PhotoResponse]
