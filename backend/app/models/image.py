import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKey
from app.models.enums import Verdict, pg_enum

if TYPE_CHECKING:
    from app.models.shoot import Shoot


class Image(UUIDPrimaryKey, Base):
    """One row per frame.

    Columns are grouped by the build step that fills them in. Everything
    below the storage group is null until the cull pipeline runs.
    """

    __tablename__ = "images"

    shoot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shoots.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Storage (step 3). Keys only - image bytes never pass through FastAPI.
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_key: Mapped[str] = mapped_column(String(500), nullable=False)
    web_key: Mapped[str | None] = mapped_column(String(500))
    thumb_key: Mapped[str | None] = mapped_column(String(500))
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    bytes: Mapped[int | None] = mapped_column(BigInteger)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Technical scores (step 4).
    blur_variance: Mapped[float | None] = mapped_column(Float)
    exposure_score: Mapped[float | None] = mapped_column(Float)
    eyes_closed: Mapped[bool | None] = mapped_column(Boolean)

    # AI verdict - written once by the pipeline, never updated.
    ai_verdict: Mapped[Verdict | None] = mapped_column(pg_enum(Verdict, "verdict"))
    ai_reasons: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)), nullable=False, server_default="{}", default=list
    )
    ai_score: Mapped[float | None] = mapped_column(Float)

    # Human verdict - set only on override.
    admin_verdict: Mapped[Verdict | None] = mapped_column(pg_enum(Verdict, "verdict"))
    admin_note: Mapped[str | None] = mapped_column(Text)

    # Gallery (step 6).
    in_gallery: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    gallery_order: Mapped[int | None] = mapped_column(Integer)

    shoot: Mapped["Shoot"] = relationship(back_populates="images", foreign_keys=[shoot_id])

    __table_args__ = (
        Index("ix_images_shoot_id", "shoot_id"),
        Index("ix_images_shoot_id_in_gallery", "shoot_id", "in_gallery"),
        Index("ix_images_shoot_id_ai_verdict", "shoot_id", "ai_verdict"),
    )
