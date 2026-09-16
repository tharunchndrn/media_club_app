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
        tables = set(inspect(engine).get_table_names())
        assert EXPECTED_TABLES <= tables
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
