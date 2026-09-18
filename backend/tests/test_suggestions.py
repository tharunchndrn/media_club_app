import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import User


@pytest.fixture(scope="module", autouse=True)
def schema(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(engine):
    def _get_db():
        session = Session(bind=engine, future=True)
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE users, suggestions CASCADE"))
        conn.commit()


def _make_user(engine, **overrides):
    defaults = dict(
        name="Kasun Silva",
        email="kasun.silva@nibm.lk",
        batch="2023/2024",
    )
    defaults.update(overrides)
    session = Session(bind=engine, future=True)
    user = User(**defaults)
    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()
    return user


@pytest.fixture
def student_user(client, engine):
    return _make_user(engine)


@pytest.fixture
def other_user(client, engine):
    return _make_user(engine, name="Other Student", email="other@nibm.lk", batch="2024/2025")


def test_list_categories_returns_the_nine_fixed_values(client):
    response = client.get("/api/v1/suggestions/categories")
    assert response.status_code == 200
    assert response.json() == [
        "event-idea",
        "coverage-request",
        "design-request",
        "workshop-request",
        "collaboration",
        "equipment",
        "feedback",
        "complaint",
        "other",
    ]


def test_create_suggestion_requires_a_known_author(client):
    response = client.post(
        "/api/v1/suggestions",
        json={
            "author_id": "00000000-0000-0000-0000-000000000000",
            "category": "event-idea",
            "body": "x" * 20,
        },
    )
    assert response.status_code == 404


def test_create_suggestion_rejects_body_shorter_than_ten_chars(client, student_user):
    response = client.post(
        "/api/v1/suggestions",
        json={"author_id": str(student_user.id), "category": "event-idea", "body": "too short"},
    )
    assert response.status_code == 422


def test_create_suggestion_rejects_body_longer_than_2000_chars(client, student_user):
    response = client.post(
        "/api/v1/suggestions",
        json={"author_id": str(student_user.id), "category": "event-idea", "body": "x" * 2001},
    )
    assert response.status_code == 422


def test_create_suggestion_defaults_to_new_status_and_not_anonymous(client, student_user):
    response = client.post(
        "/api/v1/suggestions",
        json={
            "author_id": str(student_user.id),
            "category": "event-idea",
            "body": "Host an inter-batch photo quiz.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "new"
    assert data["is_anonymous"] is False
    assert data["theme_id"] is None


def test_mine_only_returns_the_given_authors_suggestions(client, student_user, other_user):
    client.post(
        "/api/v1/suggestions",
        json={
            "author_id": str(student_user.id),
            "category": "event-idea",
            "body": "Host an inter-batch photo quiz.",
        },
    )
    client.post(
        "/api/v1/suggestions",
        json={
            "author_id": str(other_user.id),
            "category": "equipment",
            "body": "The tripod is wobbly, please replace it.",
        },
    )
    response = client.get("/api/v1/suggestions/mine", params={"author_id": str(student_user.id)})
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "event-idea"


def test_admin_list_hides_author_for_anonymous_suggestions(client, student_user):
    client.post(
        "/api/v1/suggestions",
        json={
            "author_id": str(student_user.id),
            "category": "complaint",
            "body": "The lab equipment booking process is unfair.",
            "is_anonymous": True,
        },
    )
    response = client.get("/api/v1/suggestions")
    data = response.json()
    assert len(data) == 1
    assert data[0]["is_anonymous"] is True
    assert data[0]["author_name"] is None
    assert data[0]["author_batch"] is None


def test_admin_list_shows_author_for_non_anonymous_suggestions(client, student_user):
    client.post(
        "/api/v1/suggestions",
        json={
            "author_id": str(student_user.id),
            "category": "feedback",
            "body": "Great event last week, more like this please.",
        },
    )
    response = client.get("/api/v1/suggestions")
    data = response.json()
    assert data[0]["author_name"] == "Kasun Silva"
    assert data[0]["author_batch"] == "2023/2024"


def test_admin_list_filters_by_status(client, student_user):
    created = client.post(
        "/api/v1/suggestions",
        json={
            "author_id": str(student_user.id),
            "category": "other",
            "body": "Some general feedback for the club.",
        },
    ).json()
    client.patch(
        f"/api/v1/suggestions/{created['id']}",
        json={"status": "reviewing"},
    )
    response = client.get("/api/v1/suggestions", params={"status": "reviewing"})
    assert len(response.json()) == 1

    response_new = client.get("/api/v1/suggestions", params={"status": "new"})
    assert response_new.json() == []


def test_admin_list_filters_by_batch(client, student_user, other_user):
    client.post(
        "/api/v1/suggestions",
        json={
            "author_id": str(student_user.id),
            "category": "other",
            "body": "Suggestion from the 2023 batch.",
        },
    )
    client.post(
        "/api/v1/suggestions",
        json={
            "author_id": str(other_user.id),
            "category": "other",
            "body": "Suggestion from the 2024 batch.",
        },
    )
    response = client.get("/api/v1/suggestions", params={"batch": "2024/2025"})
    data = response.json()
    assert len(data) == 1
    assert data[0]["author_batch"] == "2024/2025"


def test_update_status_404_for_unknown_id(client):
    response = client.patch(
        "/api/v1/suggestions/00000000-0000-0000-0000-000000000000",
        json={"status": "planned"},
    )
    assert response.status_code == 404
