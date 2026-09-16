import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, Timestamps, UUIDPrimaryKey
from app.models.enums import ShootStatus, pg_enum

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.image import Image


class Shoot(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "shoots"

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    shoot_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[ShootStatus] = mapped_column(
        pg_enum(ShootStatus, "shoot_status"),
        nullable=False,
        default=ShootStatus.DRAFT,
        server_default=ShootStatus.DRAFT.value,
    )
    select_limit: Mapped[int | None] = mapped_column(Integer)
    downloads_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    cover_image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "images.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_shoots_cover_image_id",
        ),
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    client: Mapped["Client"] = relationship(back_populates="shoots")
    images: Mapped[list["Image"]] = relationship(
        back_populates="shoot",
        cascade="all, delete-orphan",
        foreign_keys="Image.shoot_id",
    )
