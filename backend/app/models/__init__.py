"""Importing this package registers every table on Base.metadata.

Alembic's env.py relies on that, so never trim this list.
"""

from app.models.client import Client
from app.models.edit_request import EditRequest
from app.models.final import Final
from app.models.image import Image
from app.models.job import Job
from app.models.magic_link import MagicLink
from app.models.select import Select
from app.models.shoot import Shoot
from app.models.studio_user import StudioUser

__all__ = [
    "Client",
    "EditRequest",
    "Final",
    "Image",
    "Job",
    "MagicLink",
    "Select",
    "Shoot",
    "StudioUser",
]
