import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import Event, Photo
from app.models.enums import EventStatus
from app.schemas.event import (
    EventCreate,
    EventDetail,
    EventSummary,
    EventUpdate,
    PhotoCreate,
    PhotoResponse,
)
from app.services.slug import unique_event_slug

router = APIRouter(prefix="/events", tags=["events"])


def _get_event_or_404(db: Session, event_id: uuid.UUID) -> Event:
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.get("", response_model=list[EventSummary])
def list_events(
    year: str | None = None,
    status_: EventStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[Event]:
    query = select(Event).order_by(Event.event_date.desc())
    query = query.where(Event.status == (status_ or EventStatus.PUBLISHED))
    if year is not None:
        query = query.where(Event.academic_year == year)
    return list(db.scalars(query))


@router.get("/{event_id}", response_model=EventDetail)
def get_event(event_id: uuid.UUID, db: Session = Depends(get_db)) -> Event:
    event = db.scalar(
        select(Event).where(Event.id == event_id).options(selectinload(Event.photos))
    )
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.post("", response_model=EventSummary, status_code=status.HTTP_201_CREATED)
def create_event(
    body: EventCreate,
    db: Session = Depends(get_db),
) -> Event:
    event = Event(
        title=body.title,
        slug=unique_event_slug(db, body.title),
        description=body.description,
        venue=body.venue,
        event_date=body.event_date,
        academic_year=body.academic_year,
        cover_image_url=body.cover_image_url,
        status=body.status,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.patch("/{event_id}", response_model=EventSummary)
def update_event(
    event_id: uuid.UUID,
    body: EventUpdate,
    db: Session = Depends(get_db),
) -> Event:
    event = _get_event_or_404(db, event_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    event = _get_event_or_404(db, event_id)
    db.delete(event)
    db.commit()


@router.post(
    "/{event_id}/photos", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED
)
def add_photo(
    event_id: uuid.UUID,
    body: PhotoCreate,
    db: Session = Depends(get_db),
) -> Photo:
    event = _get_event_or_404(db, event_id)
    sort_order = body.sort_order
    if sort_order is None:
        max_order = db.scalar(
            select(Photo.sort_order)
            .where(Photo.event_id == event.id)
            .order_by(Photo.sort_order.desc())
        )
        sort_order = 0 if max_order is None else max_order + 1
    photo = Photo(
        event=event,
        image_url=body.image_url,
        thumb_url=body.thumb_url,
        caption=body.caption,
        alt_text=body.alt_text,
        sort_order=sort_order,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.delete("/{event_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    event_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    photo = db.scalar(
        select(Photo).where(Photo.id == photo_id, Photo.event_id == event_id)
    )
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    db.delete(photo)
    db.commit()
