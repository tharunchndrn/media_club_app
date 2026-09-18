import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import get_db
from app.main import app


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
        conn.execute(text("TRUNCATE TABLE users, committee_members CASCADE"))
        conn.commit()


def _create_member(client, **overrides):
    body = dict(name="Grace Hopper", position="President", academic_year="2025/2026")
    body.update(overrides)
    return client.post("/api/v1/committee", json=body)


def test_create_and_list_committee_members(client):
    _create_member(client)
    response = client.get("/api/v1/committee")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Grace Hopper"


def test_list_filters_by_year(client):
    _create_member(client, academic_year="2025/2026")
    _create_member(client, name="Ada Lovelace", academic_year="2024/2025")
    response = client.get("/api/v1/committee", params={"year": "2024/2025"})
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Ada Lovelace"


def test_list_years_returns_distinct_years_descending(client):
    _create_member(client, academic_year="2024/2025")
    _create_member(client, name="Ada Lovelace", academic_year="2025/2026")
    response = client.get("/api/v1/committee/years")
    assert response.json() == ["2025/2026", "2024/2025"]


def test_delete_committee_member(client):
    member = _create_member(client).json()
    response = client.delete(f"/api/v1/committee/{member['id']}")
    assert response.status_code == 204
    assert client.get("/api/v1/committee").json() == []


def test_delete_committee_member_404_for_unknown_id(client):
    response = client.delete(
        "/api/v1/committee/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
