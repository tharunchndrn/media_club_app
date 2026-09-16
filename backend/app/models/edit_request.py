import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Timestamps, UUIDPrimaryKey
from app.models.enums import EditStatus, pg_enum


class EditRequest(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "edit_requests"

    shoot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shoots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[EditStatus] = mapped_column(
        pg_enum(EditStatus, "edit_status"),
        nullable=False,
        default=EditStatus.OPEN,
        server_default=EditStatus.OPEN.value,
    )
    admin_note: Mapped[str | None] = mapped_column(Text)
