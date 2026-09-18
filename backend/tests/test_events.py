import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import get_db
from app.main import app

EVENT_DATE = "2026-10-15T09:00:00+00:00"


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
        conn.execute(text("TRUNCATE TABLE users, events, photos CASCADE"))
        conn.commit()


def _create_event(client, **overrides):
    body = dict(
        title="Inter-Batch Photowalk",
        description="A campus-wide photowalk.",
        venue="Main lawn",
        event_date=EVENT_DATE,
        academic_year="2025/2026",
    )
    body.update(overrides)
    return client.post("/api/v1/events", json=body)


def test_create_event_generates_a_slug_and_defaults_to_draft(client):
    response = _create_event(client)
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "inter-batch-photowalk"
    assert data["status"] == "draft"


def test_duplicate_titles_get_distinct_slugs(client):
    first = _create_event(client).json()
    second = _create_event(client).json()
    assert first["slug"] != second["slug"]


def test_list_events_defaults_to_published_only(client):
    _create_event(client, title="Draft Event")
    published = _create_event(client, title="Published Event", status="published")

    response = client.get("/api/v1/events")
    assert response.status_code == 200
    ids = [e["id"] for e in response.json()]
    assert published.json()["id"] in ids
    assert len(ids) == 1


def test_list_events_filters_by_year(client):
    _create_event(
        client, title="This Year", academic_year="2025/2026", status="published"
    )
    _create_event(
        client, title="Last Year", academic_year="2024/2025", status="published"
    )
    response = client.get("/api/v1/events", params={"year": "2024/2025"})
    data = response.json()
    assert len(data) == 1
    assert data[0]["academic_year"] == "2024/2025"


def test_list_events_can_request_draft_status_explicitly(client):
    _create_event(client, title="Draft One")
    response = client.get("/api/v1/events", params={"status": "draft"})
    assert len(response.json()) == 1


def test_get_event_returns_photos(client):
    event = _create_event(client).json()
    client.post(
        f"/api/v1/events/{event['id']}/photos",
        json={"image_url": "https://example.com/a.jpg"},
    )
    response = client.get(f"/api/v1/events/{event['id']}")
    assert response.status_code == 200
    assert len(response.json()["photos"]) == 1


def test_get_event_404_for_unknown_id(client):
    response = client.get("/api/v1/events/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_patch_event_updates_only_given_fields(client):
    event = _create_event(client).json()
    response = client.patch(
        f"/api/v1/events/{event['id']}",
        json={"status": "published"},
    )
    data = response.json()
    assert data["status"] == "published"
    assert data["title"] == event["title"]


def test_delete_event_removes_it_and_its_photos(client):
    event = _create_event(client).json()
    client.post(
        f"/api/v1/events/{event['id']}/photos",
        json={"image_url": "https://example.com/a.jpg"},
    )
    response = client.delete(f"/api/v1/events/{event['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/events/{event['id']}").status_code == 404


def test_add_photo_appends_sort_order(client):
    event = _create_event(client).json()
    first = client.post(
        f"/api/v1/events/{event['id']}/photos",
        json={"image_url": "https://example.com/a.jpg"},
    ).json()
    second = client.post(
        f"/api/v1/events/{event['id']}/photos",
        json={"image_url": "https://example.com/b.jpg"},
    ).json()
    assert first["sort_order"] == 0
    assert second["sort_order"] == 1


def test_delete_photo(client):
    event = _create_event(client).json()
    photo = client.post(
        f"/api/v1/events/{event['id']}/photos",
        json={"image_url": "https://example.com/a.jpg"},
    ).json()
    response = client.delete(
        f"/api/v1/events/{event['id']}/photos/{photo['id']}"
    )
    assert response.status_code == 204
    detail = client.get(f"/api/v1/events/{event['id']}").json()
    assert detail["photos"] == []
