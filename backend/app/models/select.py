import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.image import Image
    from app.models.shoot import Shoot


class Select(UUIDPrimaryKey, Base):
    """A client's heart on one image."""

    __tablename__ = "selects"

    shoot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shoots.id", ondelete="CASCADE"), nullable=False
    )
    image_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    shoot: Mapped["Shoot"] = relationship()
    image: Mapped["Image"] = relationship()
    client: Mapped["Client"] = relationship()

    __table_args__ = (
        UniqueConstraint("image_id", "client_id", name="uq_selects_image_client"),
    )
