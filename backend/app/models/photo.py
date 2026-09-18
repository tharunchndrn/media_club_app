import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.event import Event


class Photo(UUIDPrimaryKey, Base):
    __tablename__ = "photos"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumb_url: Mapped[str | None] = mapped_column(String(500))
    caption: Mapped[str | None] = mapped_column(String(300))
    alt_text: Mapped[str | None] = mapped_column(String(300))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    event: Mapped["Event"] = relationship(back_populates="photos")
