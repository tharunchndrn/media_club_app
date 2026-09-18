from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAt, UUIDPrimaryKey
from app.models.enums import EventStatus, pg_enum

if TYPE_CHECKING:
    from app.models.photo import Photo


class Event(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    venue: Mapped[str] = mapped_column(String(200), nullable=False)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[EventStatus] = mapped_column(
        pg_enum(EventStatus, "event_status"),
        nullable=False,
        default=EventStatus.DRAFT,
        server_default=EventStatus.DRAFT.value,
    )
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    photos: Mapped[list["Photo"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
        order_by="Photo.sort_order",
    )
