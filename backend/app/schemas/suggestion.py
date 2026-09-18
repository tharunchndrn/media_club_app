import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SuggestionCategory, SuggestionStatus


class SuggestionCreate(BaseModel):
    author_id: uuid.UUID
    category: SuggestionCategory
    body: str = Field(min_length=10, max_length=2000)
    is_anonymous: bool = False


class SuggestionStatusUpdate(BaseModel):
    status: SuggestionStatus


class SuggestionResponse(BaseModel):
    """A suggestion as seen by its own author (GET /suggestions/mine, POST /suggestions)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category: SuggestionCategory
    body: str
    status: SuggestionStatus
    theme_id: str | None
    theme_label: str | None
    sentiment: float | None
    is_anonymous: bool
    created_at: datetime


class SuggestionAdminResponse(BaseModel):
    """A suggestion as seen by admins. Author identity is hidden when is_anonymous."""

    id: uuid.UUID
    category: SuggestionCategory
    body: str
    status: SuggestionStatus
    theme_id: str | None
    theme_label: str | None
    sentiment: float | None
    is_anonymous: bool
    created_at: datetime
    author_name: str | None
    author_batch: str | None
