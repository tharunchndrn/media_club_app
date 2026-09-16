import uuid

import pytest
from sqlalchemy import select as sa_select
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.models import Client, Image, Select, Shoot
from app.models.enums import ShootStatus, Verdict


@pytest.fixture(scope="session", autouse=True)
def schema(engine):
    """Task 4 tests run against metadata.create_all. Task 5 tests Alembic."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def _chain(db_session):
    client = Client(name="Ada Lovelace", email="ada@example.com")
    shoot = Shoot(client=client, title="Autumn session")
    image = Image(shoot=shoot, filename="DSC_0001.jpg", original_key="raw/0001.jpg")
    db_session.add(image)
    db_session.flush()
    return client, shoot, image


def test_defaults_are_applied(db_session):
    client, shoot, image = _chain(db_session)
    assert isinstance(shoot.id, uuid.UUID)
    assert shoot.status is ShootStatus.DRAFT
    assert shoot.downloads_enabled is False
    assert shoot.select_limit is None
    assert image.in_gallery is False
    assert image.ai_verdict is None
    assert image.admin_verdict is None
    assert image.ai_reasons == []


def test_created_at_is_populated_by_the_database(db_session):
    _, shoot, _ = _chain(db_session)
    db_session.refresh(shoot)
    assert shoot.created_at is not None
    assert shoot.created_at.tzinfo is not None


def test_verdict_roundtrips_as_lowercase_value(db_session):
    _, _, image = _chain(db_session)
    image.ai_verdict = Verdict.REJECT
    image.ai_reasons = ["blur", "eyes_closed"]
    db_session.flush()
    db_session.refresh(image)
    assert image.ai_verdict is Verdict.REJECT
    assert image.ai_reasons == ["blur", "eyes_closed"]


def test_a_client_cannot_select_the_same_image_twice(db_session):
    client, shoot, image = _chain(db_session)
    db_session.add(Select(shoot=shoot, image=image, client=client))
    db_session.flush()
    db_session.add(Select(shoot=shoot, image=image, client=client))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_deleting_a_shoot_cascades_to_its_images(db_session):
    _, shoot, _ = _chain(db_session)
    db_session.delete(shoot)
    db_session.flush()
    assert db_session.scalars(sa_select(Image)).all() == []
