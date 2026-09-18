import psycopg
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import get_settings

TEST_DB_NAME = "mediaclub_test"


def _admin_dsn() -> str:
    """libpq DSN for the maintenance database, derived from DATABASE_URL."""
    url = get_settings().database_url
    return url.replace("postgresql+psycopg://", "postgresql://").rsplit("/", 1)[0] + "/postgres"


def _test_url() -> str:
    url = get_settings().database_url
    return url.rsplit("/", 1)[0] + "/" + TEST_DB_NAME


@pytest.fixture(scope="session")
def test_database():
    """Drop and recreate mediaclub_test around the whole session."""
    with psycopg.connect(_admin_dsn(), autocommit=True) as conn:
        conn.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
        conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    yield _test_url()
    with psycopg.connect(_admin_dsn(), autocommit=True) as conn:
        conn.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')


@pytest.fixture(scope="session")
def engine(test_database):
    engine = create_engine(test_database, future=True)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(engine):
    """A session whose work is rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
