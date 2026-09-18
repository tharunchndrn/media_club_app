import uuid

import pytest
from sqlalchemy import select as sa_select, text
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.models import CommitteeMember, Event, Photo, Suggestion, User
from app.models.enums import EventStatus, SuggestionCategory, SuggestionStatus


@pytest.fixture(scope="session", autouse=True)
def schema(engine):
    """Task 4 tests run against metadata.create_all. Task 6 tests Alembic."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def _user(db_session, **overrides):
    defaults = dict(
        name="Ada Lovelace",
        email="ada@nibm.lk",
        batch="2023/2024",
    )
    defaults.update(overrides)
    user = User(**defaults)
    db_session.add(user)
    db_session.flush()
    return user


def _event(db_session, **overrides):
    defaults = dict(
        title="Photowalk",
        slug="photowalk-2026",
        description="A campus photowalk.",
        venue="Main lawn",
        event_date="2026-10-01T09:00:00+00:00",
        academic_year="2025/2026",
    )
    defaults.update(overrides)
    event = Event(**defaults)
    db_session.add(event)
    db_session.flush()
    return event


def test_user_defaults_are_applied(db_session):
    user = _user(db_session)
    assert isinstance(user.id, uuid.UUID)
    assert user.student_id is None


def test_user_created_at_is_populated_by_the_database(db_session):
    user = _user(db_session)
    db_session.refresh(user)
    assert user.created_at is not None
    assert user.created_at.tzinfo is not None


def test_user_email_is_unique(db_session):
    _user(db_session, email="dup@nibm.lk")
    db_session.add(User(name="B", email="dup@nibm.lk", batch="2023/2024"))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_event_defaults_are_applied(db_session):
    event = _event(db_session)
    assert event.status is EventStatus.DRAFT
    assert event.cover_image_url is None


def test_event_slug_is_unique(db_session):
    _event(db_session, slug="dup-slug")
    db_session.add(
        Event(
            title="Other",
            slug="dup-slug",
            description="d",
            venue="v",
            event_date="2026-10-01T09:00:00+00:00",
            academic_year="2025/2026",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_deleting_an_event_cascades_to_its_photos(db_session):
    event = _event(db_session, slug="cascade-test")
    db_session.add(Photo(event=event, image_url="https://example.com/a.jpg"))
    db_session.flush()
    db_session.delete(event)
    db_session.flush()
    assert db_session.scalars(sa_select(Photo)).all() == []


def test_photo_defaults_are_applied(db_session):
    event = _event(db_session, slug="photo-defaults")
    photo = Photo(event=event, image_url="https://example.com/a.jpg")
    db_session.add(photo)
    db_session.flush()
    assert photo.sort_order == 0
    assert photo.thumb_url is None


def test_committee_member_defaults_are_applied(db_session):
    member = CommitteeMember(
        name="Grace Hopper",
        position="President",
        academic_year="2025/2026",
    )
    db_session.add(member)
    db_session.flush()
    assert member.sort_order == 0
    assert member.linkedin_url is None


def test_suggestion_defaults_are_applied(db_session):
    user = _user(db_session, email="author@nibm.lk")
    suggestion = Suggestion(
        author=user,
        category=SuggestionCategory.EVENT_IDEA,
        body="Host an inter-batch photo quiz next month.",
    )
    db_session.add(suggestion)
    db_session.flush()
    assert suggestion.status is SuggestionStatus.NEW
    assert suggestion.is_anonymous is False
    assert suggestion.theme_id is None
    assert suggestion.theme_label is None
    assert suggestion.sentiment is None


def test_suggestion_category_roundtrips_as_hyphenated_value(db_session):
    user = _user(db_session, email="author2@nibm.lk")
    suggestion = Suggestion(
        author=user,
        category=SuggestionCategory.COVERAGE_REQUEST,
        body="Please cover the inter-batch sports meet.",
    )
    db_session.add(suggestion)
    db_session.flush()
    db_session.refresh(suggestion)
    assert suggestion.category is SuggestionCategory.COVERAGE_REQUEST


def test_deleting_a_user_cascades_to_their_suggestions(db_session):
    user = _user(db_session, email="cascade2@nibm.lk")
    db_session.add(
        Suggestion(author=user, category=SuggestionCategory.OTHER, body="x" * 20)
    )
    db_session.flush()
    db_session.delete(user)
    db_session.flush()
    assert db_session.scalars(sa_select(Suggestion)).all() == []


def test_deleting_an_event_via_raw_sql_cascades_to_its_photos_at_the_db_level(db_session):
    event = _event(db_session, slug="raw-sql-cascade")
    photo = Photo(event=event, image_url="https://example.com/a.jpg")
    db_session.add(photo)
    db_session.flush()
    event_id = event.id
    db_session.execute(text("DELETE FROM events WHERE id = :id"), {"id": event_id})
    remaining = db_session.execute(
        text("SELECT id FROM photos WHERE event_id = :id"), {"id": event_id}
    ).all()
    assert remaining == []
