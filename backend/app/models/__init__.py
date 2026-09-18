"""Importing this package registers every table on Base.metadata.

Alembic's env.py relies on that, so never trim this list.
"""

from app.models.committee_member import CommitteeMember
from app.models.event import Event
from app.models.photo import Photo
from app.models.suggestion import Suggestion
from app.models.user import User

__all__ = [
    "CommitteeMember",
    "Event",
    "Photo",
    "Suggestion",
    "User",
]
