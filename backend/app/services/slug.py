import re
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Event

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.lower()).strip("-")


def unique_event_slug(db: Session, title: str) -> str:
    base = slugify(title) or "event"
    slug = base
    suffix = 1
    while db.scalar(select(Event).where(Event.slug == slug)) is not None:
        suffix += 1
        slug = f"{base}-{suffix}"
    return slug
