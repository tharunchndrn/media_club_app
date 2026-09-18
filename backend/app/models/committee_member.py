from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKey


class CommitteeMember(UUIDPrimaryKey, Base):
    __tablename__ = "committee_members"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str] = mapped_column(String(150), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    photo_url: Mapped[str | None] = mapped_column(String(500))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
