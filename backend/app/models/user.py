from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAt, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.suggestion import Suggestion


class User(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    batch: Mapped[str] = mapped_column(String(50), nullable=False)
    student_id: Mapped[str | None] = mapped_column(String(50))

    suggestions: Mapped[list["Suggestion"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
