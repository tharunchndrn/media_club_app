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

MIGRATION_DB_NAME = "studio_migration_test"


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


EXPECTED_TABLES = {
    "studio_users",
    "clients",
    "magic_links",
    "shoots",
    "images",
    "jobs",
    "selects",
    "edit_requests",
    "finals",
}

EXPECTED_ENUMS = {"shoot_status", "verdict", "job_kind", "job_status", "edit_status"}


def test_upgrade_creates_every_table(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        tables = set(inspect(engine).get_table_names()) - {"alembic_version"}
        assert tables == EXPECTED_TABLES
    finally:
        engine.dispose()


# Exact column set per table, taken from the SQLAlchemy models (not invented).
# This is the highest-value assertion this branch carries: these names freeze
# into the API contract at build step 3, and a rename after that is a
# coordinated breaking change across the React admin and the Flutter client.
EXPECTED_COLUMNS = {
    "studio_users": {
        "id", "email", "password_hash", "name", "is_active",
        "created_at", "updated_at",
    },
    "clients": {
        "id", "name", "email", "phone", "notes", "created_at", "updated_at",
    },
    "magic_links": {
        "id", "client_id", "token_hash", "expires_at", "used_at", "created_at",
    },
    "shoots": {
        "id", "client_id", "title", "shoot_date", "status", "select_limit",
        "downloads_enabled", "cover_image_id", "published_at", "delivered_at",
        "created_at", "updated_at",
    },
    "images": {
        "id", "shoot_id", "filename", "original_key", "web_key", "thumb_key",
        "width", "height", "bytes", "captured_at", "uploaded_at",
        "blur_variance", "exposure_score", "eyes_closed", "ai_verdict",
        "ai_reasons", "ai_score", "admin_verdict", "admin_note", "in_gallery",
        "gallery_order",
    },
    "jobs": {
        "id", "shoot_id", "kind", "status", "progress_done", "progress_total",
        "error", "started_at", "finished_at", "created_at",
    },
    "selects": {
        "id", "shoot_id", "image_id", "client_id", "created_at",
    },
    "edit_requests": {
        "id", "shoot_id", "image_id", "client_id", "note", "status",
        "admin_note", "created_at", "updated_at",
    },
    "finals": {
        "id", "shoot_id", "image_id", "key", "filename", "bytes", "created_at",
    },
}


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


def test_images_has_its_three_named_indexes(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        names = {ix["name"] for ix in inspect(engine).get_indexes("images")}
        assert {
            "ix_images_shoot_id",
            "ix_images_shoot_id_in_gallery",
            "ix_images_shoot_id_ai_verdict",
        } <= names
    finally:
        engine.dispose()


def test_magic_links_has_an_index_on_token_hash(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        indexed_columns = [
            set(ix["column_names"]) for ix in inspect(engine).get_indexes("magic_links")
        ]
        assert {"token_hash"} in indexed_columns
    finally:
        engine.dispose()


def test_clients_and_studio_users_have_a_unique_email(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        inspector = inspect(engine)
        clients_unique = [
            set(c["column_names"]) for c in inspector.get_unique_constraints("clients")
        ]
        studio_users_unique = [
            set(c["column_names"]) for c in inspector.get_unique_constraints("studio_users")
        ]
        assert {"email"} in clients_unique
        assert {"email"} in studio_users_unique
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


def test_selects_has_the_unique_constraint(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        constraints = inspect(engine).get_unique_constraints("selects")
        columns = [set(c["column_names"]) for c in constraints]
        assert {"image_id", "client_id"} in columns
    finally:
        engine.dispose()


def test_pgvector_is_not_required_yet(alembic_config, migration_url):
    command.upgrade(alembic_config, "head")
    engine = create_engine(migration_url)
    try:
        with engine.connect() as conn:
            installed = conn.scalars(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            ).all()
        assert installed == []
        assert "embedding" not in {c["name"] for c in inspect(engine).get_columns("images")}
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
