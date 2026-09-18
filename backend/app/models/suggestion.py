import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAt, UUIDPrimaryKey
from app.models.enums import SuggestionCategory, SuggestionStatus, pg_enum

if TYPE_CHECKING:
    from app.models.user import User


class Suggestion(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "suggestions"

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[SuggestionCategory] = mapped_column(
        pg_enum(SuggestionCategory, "suggestion_category"),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SuggestionStatus] = mapped_column(
        pg_enum(SuggestionStatus, "suggestion_status"),
        nullable=False,
        default=SuggestionStatus.NEW,
        server_default=SuggestionStatus.NEW.value,
    )
    theme_id: Mapped[str | None] = mapped_column(String(50), index=True)
    theme_label: Mapped[str | None] = mapped_column(String(200))
    sentiment: Mapped[float | None] = mapped_column(Float)
    is_anonymous: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    author: Mapped["User"] = relationship(back_populates="suggestions")
