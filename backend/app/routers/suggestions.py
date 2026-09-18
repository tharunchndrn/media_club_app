import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import Suggestion, User
from app.models.enums import SuggestionCategory, SuggestionStatus
from app.schemas.suggestion import (
    SuggestionAdminResponse,
    SuggestionCreate,
    SuggestionResponse,
    SuggestionStatusUpdate,
)

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


def _to_admin_response(suggestion: Suggestion) -> SuggestionAdminResponse:
    return SuggestionAdminResponse(
        id=suggestion.id,
        category=suggestion.category,
        body=suggestion.body,
        status=suggestion.status,
        theme_id=suggestion.theme_id,
        theme_label=suggestion.theme_label,
        sentiment=suggestion.sentiment,
        is_anonymous=suggestion.is_anonymous,
        created_at=suggestion.created_at,
        author_name=None if suggestion.is_anonymous else suggestion.author.name,
        author_batch=None if suggestion.is_anonymous else suggestion.author.batch,
    )


@router.get("/categories", response_model=list[SuggestionCategory])
def list_categories() -> list[SuggestionCategory]:
    return list(SuggestionCategory)


@router.post("", response_model=SuggestionResponse, status_code=status.HTTP_201_CREATED)
def create_suggestion(
    body: SuggestionCreate,
    db: Session = Depends(get_db),
) -> Suggestion:
    author = db.get(User, body.author_id)
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    suggestion = Suggestion(
        author=author,
        category=body.category,
        body=body.body,
        is_anonymous=body.is_anonymous,
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion


@router.get("/mine", response_model=list[SuggestionResponse])
def list_my_suggestions(
    author_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
) -> list[Suggestion]:
    query = (
        select(Suggestion)
        .options(selectinload(Suggestion.author))
        .order_by(Suggestion.created_at.desc())
    )
    if author_id is not None:
        query = query.where(Suggestion.author_id == author_id)
    return list(db.scalars(query))


@router.get("", response_model=list[SuggestionAdminResponse])
def list_suggestions(
    status_: SuggestionStatus | None = Query(default=None, alias="status"),
    theme_id: str | None = None,
    batch: str | None = None,
    db: Session = Depends(get_db),
) -> list[SuggestionAdminResponse]:
    query = (
        select(Suggestion)
        .options(selectinload(Suggestion.author))
        .order_by(Suggestion.created_at.desc())
    )
    if status_ is not None:
        query = query.where(Suggestion.status == status_)
    if theme_id is not None:
        query = query.where(Suggestion.theme_id == theme_id)
    if batch is not None:
        query = query.join(User, Suggestion.author_id == User.id).where(User.batch == batch)
    suggestions = db.scalars(query)
    return [_to_admin_response(s) for s in suggestions]


@router.patch("/{suggestion_id}", response_model=SuggestionAdminResponse)
def update_suggestion_status(
    suggestion_id: uuid.UUID,
    body: SuggestionStatusUpdate,
    db: Session = Depends(get_db),
) -> SuggestionAdminResponse:
    suggestion = db.scalar(
        select(Suggestion)
        .where(Suggestion.id == suggestion_id)
        .options(selectinload(Suggestion.author))
    )
    if suggestion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")
    suggestion.status = body.status
    db.commit()
    db.refresh(suggestion)
    return _to_admin_response(suggestion)
