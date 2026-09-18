"""Alembic round-trip and schema assertions.

These run against their own database, created and destroyed here, so they
never collide with the metadata.create_all schema used by test_models.py.
"""

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.core.config import get_settings

MIGRATION_DB_NAME = "mediaclub_migration_test"


def _admin_dsn() -> str:
    url = get_settings().database_url
    return url.replace("postgresql+psycopg://", "postgresql://").rsplit("/", 1)[0] + "/postgres"


@pytest.fixture(scope="module")
def migration_url():
    with psycopg.connect(_admin_dsn(), autocommit=True) as conn:
        conn.execute(f'DROP DATABASE IF EXISTS "{MIGRATION_DB_NAME}" WITH (FORCE)')
        conn.execute(f'CREATE DATABASE "{MIGRATION_DB_NAME}"')
    url = get_settings().database_url.rsplit("/", 1)[0] + "/" + MIGRATION_DB_NAME
    yield url
    with psycopg.connect(_admin_dsn(), autocommit=True) as conn:
        conn.execute(f'DROP DATABASE IF EXISTS "{MIGRATION_DB_NAME}" WITH (FORCE)')


@pytest.fixture(scope="module")
def alembic_config(migration_url):
    config = Config("alembic.ini")
    config.set_main_option("script_location", "alembic")
    config.set_main_option("sqlalchemy.url", migration_url)
    return config


EXPECTED_TABLES = {"users", "events", "photos", "committee_members", "suggestions"}

EXPECTED_ENUMS = {
    "event_status",
    "suggestion_category",
    "suggestion_status",
}

EXPECTED_COLUMNS = {
    "users": {
        "id", "name", "email", "batch",
        "student_id", "created_at",
    },
    "events": {
        "id", "title", "slug", "description", "venue", "event_date",
        "cover_image_url", "status", "academic_year", "created_at",
    },
    "photos": {
        "id", "event_id", "image_url", "thumb_url", "caption", "alt_text",
        "sort_order",
    },
    "committee_members": {
        "id", "name", "position", "academic_year", "photo_url",
        "linkedin_url", "sort_order",
    },
    "suggestions": {
        "id", "author_id", "category", "body", "status", "theme_id",
        "theme_label", "sentiment", "is_anonymous", "created_at",
    },
}


def test_upgrade_creates_every_table(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        tables = set(inspect(engine).get_table_names()) - {"alembic_version"}
        assert tables == EXPECTED_TABLES
    finally:
        engine.dispose()


def test_column_names_match_the_models_exactly(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        inspector = inspect(engine)
        for table, expected in EXPECTED_COLUMNS.items():
            actual = {c["name"] for c in inspector.get_columns(table)}
            assert actual == expected, f"{table}: {actual} != {expected}"
    finally:
        engine.dispose()


def test_upgrade_creates_every_enum_type(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        with engine.connect() as conn:
            found = set(
                conn.scalars(text("SELECT typname FROM pg_type WHERE typtype = 'e'")).all()
            )
        assert EXPECTED_ENUMS <= found
    finally:
        engine.dispose()


def test_users_email_and_events_slug_are_unique(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        inspector = inspect(engine)
        users_unique = [
            set(c["column_names"]) for c in inspector.get_unique_constraints("users")
        ]
        events_unique = [
            set(c["column_names"]) for c in inspector.get_unique_constraints("events")
        ]
        assert {"email"} in users_unique
        assert {"slug"} in events_unique
    finally:
        engine.dispose()


def test_photos_and_suggestions_have_indexed_foreign_keys(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        inspector = inspect(engine)
        photos_indexes = [set(ix["column_names"]) for ix in inspector.get_indexes("photos")]
        suggestions_indexes = [
            set(ix["column_names"]) for ix in inspector.get_indexes("suggestions")
        ]
        assert {"event_id"} in photos_indexes
        assert {"author_id"} in suggestions_indexes
    finally:
        engine.dispose()


def test_downgrade_leaves_an_empty_database(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")
    engine = create_engine(migration_url)
    try:
        tables = set(inspect(engine).get_table_names()) - {"alembic_version"}
        assert tables == set()
        with engine.connect() as conn:
            leftover = set(
                conn.scalars(text("SELECT typname FROM pg_type WHERE typtype = 'e'")).all()
            )
        assert leftover & EXPECTED_ENUMS == set()
    finally:
        engine.dispose()


def test_upgrade_works_again_after_downgrade(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        assert EXPECTED_TABLES <= set(inspect(engine).get_table_names())
    finally:
        engine.dispose()
