# Data Model and Backend Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the repo into the CLAUDE.md monorepo layout, stand up a FastAPI backend skeleton, and define the complete database schema as Alembic migrations that apply and roll back cleanly.

**Architecture:** One FastAPI app reading a single `DATABASE_URL`. SQLAlchemy 2.0 declarative models are the single source of schema truth; Alembic autogenerates migrations from them. The app uses an async engine, Alembic and the tests use a sync engine against the same URL string — psycopg3 supports both, so no second connection variable exists. The shoot status machine is a pure-Python transition table with no database dependency, so it is unit-testable on its own.

**Tech Stack:** Python 3.11 (`py -3.11` on this machine), FastAPI, SQLAlchemy 2.0, Alembic, psycopg3, Pydantic v2 + pydantic-settings, pytest, Docker (Postgres).

**Spec:** [docs/superpowers/specs/2026-09-16-data-model-and-backend-scaffold-design.md](../specs/2026-09-16-data-model-and-backend-scaffold-design.md)

## Global Constraints

These come from CLAUDE.md and apply to every task below.

- **Do not write Flutter or React feature code.** Task 1 moves and renames the existing Flutter scaffold; it changes config only and adds no Dart logic.
- UUID primary keys on every table, generated application-side via `uuid.uuid4`.
- All timestamps `TIMESTAMPTZ`, stored UTC.
- snake_case in Python and in JSON.
- All responses wrapped in Pydantic schemas, never raw ORM objects.
- Errors are `{"detail": "...", "code": "..."}` with a correct HTTP status.
- Every schema change goes through Alembic. No manual DDL, ever.
- No Celery, no Redis. Job state lives in Postgres.
- Commits: `feat(scope):`, `fix(scope):`, `chore(scope):`, `docs(scope):`.
- Python dependencies for this step are limited to: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `alembic`, `psycopg[binary]`, `pydantic`, `pydantic-settings`, `pytest`, `pytest-asyncio`, `httpx`. OpenCV, Pillow, and the ML runtime are out of scope until steps 4 and 9.
- pgvector is NOT used in this step. No `CREATE EXTENSION vector`, no `embedding` column.

---

### Task 1: Repo restructure

Move the existing Flutter scaffold into `client_app/`, create the remaining top-level directories, and give the repo root its own `.gitignore`.

**Files:**
- Move: everything Flutter at the repo root → `client_app/`
- Create: `.gitignore` (repo root, Python/Node/editor)
- Modify: `client_app/pubspec.yaml` (package name)
- Modify: `client_app/test/widget_test.dart` (import of the renamed package)
- Create: `backend/`, `admin/`, `ml_training/` (each with a `.gitkeep`)

**Interfaces:**
- Consumes: nothing.
- Produces: the directory layout every later task writes into. After this task, all backend paths in this plan are relative to `backend/`.

- [ ] **Step 1: Move the Flutter app with `git mv` so history follows**

```bash
cd "C:/Users/Taruni/Desktop/flutter test/flutter_application_1"
mkdir -p client_app
for p in .gitignore .metadata analysis_options.yaml pubspec.yaml pubspec.lock \
         flutter_application_1.iml android ios lib test; do
  git mv "$p" "client_app/$p"
done
mkdir -p backend admin ml_training
touch backend/.gitkeep admin/.gitkeep ml_training/.gitkeep
```

`README.md`, `CLAUDE.md`, `docs/`, `.idea/`, and `.dart_tool/` stay at the root. `.dart_tool/` is untracked build output — it can be left where it is or deleted; it regenerates.

- [ ] **Step 2: Verify the move left nothing Flutter at the root**

Run: `git status --short && ls`
Expected: `ls` shows only `CLAUDE.md README.md admin backend client_app docs ml_training` plus untracked `.dart_tool` / `.idea`. `git status` shows renames (`R`), not deletes-plus-adds.

- [ ] **Step 3: Write the root `.gitignore`**

Create `.gitignore` at the repo root. The Flutter `.gitignore` moved into `client_app/` and still covers Dart artifacts there.

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
venv/
*.egg-info/
.pytest_cache/
.mypy_cache/

# Environment
.env
.env.local

# Node (admin/, from step 5)
node_modules/
dist/

# Editors / OS
.idea/
.vscode/
.DS_Store
Thumbs.db

# Stray Flutter build output left at the old root
/.dart_tool/
```

- [ ] **Step 4: Rename the Dart package**

In `client_app/pubspec.yaml`, change the first line:

```yaml
name: studio_client
```

and update the description on the line below it:

```yaml
description: "Studio 006 client portal."
```

In `client_app/test/widget_test.dart`, change the package import:

```dart
import 'package:studio_client/main.dart';
```

Leave the Android `applicationId` and the iOS bundle identifier as they are. Changing those means renaming Kotlin package directories for no functional gain at this stage, and it is unrelated to the schema work this plan exists for.

- [ ] **Step 5: Confirm nothing else referenced the old package name**

Run: `grep -rn "flutter_application_1" client_app --include=*.dart --include=*.yaml`
Expected: no output. (Hits under `client_app/android/` and `client_app/ios/` are the deliberately-unchanged bundle identifiers and are fine; the grep above excludes them by file type.)

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore(repo): restructure into monorepo layout

Move the Flutter scaffold into client_app/ and rename its package to
studio_client. Add backend/, admin/, ml_training/ and a root .gitignore
covering Python, Node, and editor artifacts.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Backend scaffold and health endpoint

Dependencies, settings, a running FastAPI app with one endpoint, and the dev Postgres container.

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/docker-compose.yml`
- Create: `backend/app/__init__.py`, `backend/app/core/__init__.py`, `backend/app/schemas/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/schemas/health.py`
- Create: `backend/app/main.py`
- Create: `backend/pytest.ini`
- Test: `backend/tests/__init__.py`, `backend/tests/test_health.py`
- Delete: `backend/.gitkeep`

**Interfaces:**
- Consumes: the `backend/` directory from Task 1.
- Produces:
  - `app.core.config.Settings` with fields `database_url: str`, `environment: str`
  - `app.core.config.get_settings() -> Settings` (cached)
  - `app.main.app` — the `FastAPI` instance
  - `app.schemas.health.HealthResponse` with field `status: str`

- [ ] **Step 1: Create the virtual environment and dependency file**

Create `backend/requirements.txt`:

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
alembic==1.14.0
psycopg[binary]==3.2.3
pydantic==2.10.4
pydantic-settings==2.7.0
pytest==8.3.4
pytest-asyncio==0.25.0
httpx==0.28.1
```

Then:

```bash
cd backend
py -3.11 -m venv .venv
.venv/Scripts/python.exe -m pip install --upgrade pip
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Every later command in this plan uses `.venv/Scripts/python.exe -m <tool>` rather than a bare `pytest` or `alembic`, so it works whether or not the venv is activated in the current shell.

- [ ] **Step 2: Start Postgres**

Create `backend/docker-compose.yml`:

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    container_name: studio_db
    environment:
      POSTGRES_USER: studio
      POSTGRES_PASSWORD: studio
      POSTGRES_DB: studio
    ports:
      - "5432:5432"
    volumes:
      - studio_pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U studio -d studio"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  studio_pgdata:
```

The image ships pgvector, but this step does not enable the extension. It is chosen now only so that step 9 needs no container change.

Run: `docker compose up -d db`
Then: `docker compose ps`
Expected: `studio_db` listed as running/healthy.

If port 5432 is already taken by a natively installed Postgres, change the host side of the mapping to `"5433:5432"` and use `5433` in the URLs below.

- [ ] **Step 3: Write the settings module**

Create `backend/app/core/config.py`:

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend configuration, read from environment or backend/.env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://studio:studio@localhost:5432/studio"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

One URL serves both engines: `create_async_engine` and `create_engine` each pick the right psycopg3 mode from the same `postgresql+psycopg://` string.

Create `backend/.env.example`:

```
DATABASE_URL=postgresql+psycopg://studio:studio@localhost:5432/studio
ENVIRONMENT=development
```

Create empty `backend/app/__init__.py`, `backend/app/core/__init__.py`, `backend/app/schemas/__init__.py`.

- [ ] **Step 4: Write the failing test**

Create `backend/pytest.ini`:

```ini
[pytest]
testpaths = tests
pythonpath = .
asyncio_mode = auto
```

Create empty `backend/tests/__init__.py`, then `backend/tests/test_health.py`:

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 5: Run the test to verify it fails**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_health.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.main'`

- [ ] **Step 6: Write the health schema and the app**

Create `backend/app/schemas/health.py`:

```python
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
```

Create `backend/app/main.py`:

```python
from fastapi import FastAPI

from app.schemas.health import HealthResponse

app = FastAPI(title="Studio 006 API", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
```

The response goes through a Pydantic schema even though it is two words, because CLAUDE.md section 7 admits no exceptions and this is the file every later router is copied from.

- [ ] **Step 7: Run the test to verify it passes**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_health.py -v`
Expected: PASS

- [ ] **Step 8: Confirm the server actually serves**

Run: `cd backend && .venv/Scripts/python.exe -m uvicorn app.main:app --reload`
Open `http://127.0.0.1:8000/health`
Expected: `{"status":"ok"}`. Then stop the server with Ctrl+C.

- [ ] **Step 9: Commit**

```bash
rm backend/.gitkeep
git add backend .gitignore
git commit -m "feat(backend): scaffold FastAPI app with health endpoint

Adds pinned dependencies, pydantic-settings config reading a single
DATABASE_URL, a dev Postgres compose file, and /health behind a Pydantic
response schema.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Declarative base, mixins, and enums

The shared foundation every model in Task 4 inherits from.

**Files:**
- Create: `backend/app/db/__init__.py`, `backend/app/db/base.py`
- Create: `backend/app/models/__init__.py`, `backend/app/models/enums.py`
- Test: `backend/tests/test_enums.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `app.db.base.Base` — the SQLAlchemy `DeclarativeBase` subclass
  - `app.db.base.UUIDPrimaryKey` — mixin supplying `id: Mapped[uuid.UUID]`
  - `app.db.base.Timestamps` — mixin supplying `created_at` and `updated_at`, both `Mapped[datetime]`
  - `app.models.enums.ShootStatus`, `Verdict`, `JobKind`, `JobStatus`, `EditStatus` — all `str, enum.Enum`
  - `app.models.enums.pg_enum(python_enum, name)` — helper returning a configured SQLAlchemy `Enum`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_enums.py`:

```python
from app.models.enums import (
    EditStatus,
    JobKind,
    JobStatus,
    ShootStatus,
    Verdict,
    pg_enum,
)


def test_shoot_status_has_the_seven_spec_states():
    assert [s.value for s in ShootStatus] == [
        "draft",
        "uploading",
        "culling",
        "culled",
        "published",
        "selects_done",
        "delivered",
    ]


def test_verdict_values():
    assert [v.value for v in Verdict] == ["keep", "reject"]


def test_job_and_edit_enum_values():
    assert [k.value for k in JobKind] == ["cull"]
    assert [s.value for s in JobStatus] == [
        "queued",
        "running",
        "succeeded",
        "failed",
    ]
    assert [s.value for s in EditStatus] == [
        "open",
        "in_progress",
        "done",
        "rejected",
    ]


def test_pg_enum_stores_lowercase_values_not_member_names():
    column_type = pg_enum(Verdict, "verdict")
    assert column_type.name == "verdict"
    assert column_type.enums == ["keep", "reject"]
```

That last test is the one that matters. By default SQLAlchemy writes the *member name* (`KEEP`) into Postgres, not the value (`keep`). Since these values become JSON field values once the contract freezes at step 3, they must be the lowercase forms.

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_enums.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.models'`

- [ ] **Step 3: Write the enums**

Create empty `backend/app/models/__init__.py` (Task 4 fills it in), then `backend/app/models/enums.py`:

```python
import enum

from sqlalchemy import Enum as SAEnum


class ShootStatus(str, enum.Enum):
    DRAFT = "draft"
    UPLOADING = "uploading"
    CULLING = "culling"
    CULLED = "culled"
    PUBLISHED = "published"
    SELECTS_DONE = "selects_done"
    DELIVERED = "delivered"


class Verdict(str, enum.Enum):
    KEEP = "keep"
    REJECT = "reject"


class JobKind(str, enum.Enum):
    CULL = "cull"


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class EditStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    REJECTED = "rejected"


def pg_enum(python_enum: type[enum.Enum], name: str) -> SAEnum:
    """A native Postgres enum that stores values, not member names."""
    return SAEnum(
        python_enum,
        name=name,
        values_callable=lambda e: [member.value for member in e],
        native_enum=True,
    )
```

- [ ] **Step 4: Write the base and mixins**

Create empty `backend/app/db/__init__.py`, then `backend/app/db/base.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base. Alembic autogenerate reads Base.metadata."""


class UUIDPrimaryKey:
    """UUID primary key, generated application-side per CLAUDE.md section 7."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class Timestamps:
    """created_at / updated_at, both TIMESTAMPTZ, both database-driven."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_enums.py -v`
Expected: PASS, 4 tests

- [ ] **Step 6: Commit**

```bash
git add backend/app/db backend/app/models backend/tests/test_enums.py
git commit -m "feat(db): add declarative base, id/timestamp mixins, and enums

Enums use values_callable so Postgres stores lowercase values rather
than member names, which is what the frozen API contract will expose.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: SQLAlchemy models

All nine tables from spec section 5, one file per table.

**Files:**
- Create: `backend/app/models/studio_user.py`, `client.py`, `magic_link.py`, `shoot.py`, `image.py`, `job.py`, `select.py`, `edit_request.py`, `final.py`
- Modify: `backend/app/models/__init__.py`
- Test: `backend/tests/conftest.py`, `backend/tests/test_models.py`

**Interfaces:**
- Consumes: `Base`, `UUIDPrimaryKey`, `Timestamps` from `app.db.base`; all enums and `pg_enum` from `app.models.enums` (Task 3).
- Produces: model classes `StudioUser`, `Client`, `MagicLink`, `Shoot`, `Image`, `Job`, `Select`, `EditRequest`, `Final`, all importable from `app.models`. Task 5 autogenerates the migration from `Base.metadata` after importing `app.models`.
- Produces: pytest fixtures `engine` (session-scoped, sync `Engine` bound to a throwaway `studio_test` database) and `db_session` (function-scoped, rolled back).

- [ ] **Step 1: Write the test database fixtures**

Create `backend/tests/conftest.py`:

```python
import psycopg
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import get_settings

TEST_DB_NAME = "studio_test"


def _admin_dsn() -> str:
    """libpq DSN for the maintenance database, derived from DATABASE_URL."""
    url = get_settings().database_url
    return url.replace("postgresql+psycopg://", "postgresql://").rsplit("/", 1)[0] + "/postgres"


def _test_url() -> str:
    url = get_settings().database_url
    return url.rsplit("/", 1)[0] + "/" + TEST_DB_NAME


@pytest.fixture(scope="session")
def test_database():
    """Drop and recreate studio_test around the whole session."""
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
```

- [ ] **Step 2: Write the failing model test**

Create `backend/tests/test_models.py`:

```python
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
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_models.py -v`
Expected: FAIL — `ImportError: cannot import name 'Client' from 'app.models'`

- [ ] **Step 4: Write the identity models**

`backend/app/models/studio_user.py`:

```python
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Timestamps, UUIDPrimaryKey


class StudioUser(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "studio_users"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
```

`backend/app/models/client.py`:

```python
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, Timestamps, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.shoot import Shoot


class Client(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "clients"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)

    shoots: Mapped[list["Shoot"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan",
    )
```

`backend/app/models/magic_link.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKey


class MagicLink(UUIDPrimaryKey, Base):
    __tablename__ = "magic_links"

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
```

`MagicLink` deliberately skips the `Timestamps` mixin: a single-use token is never updated, only spent, so an `updated_at` column would be dead weight.

- [ ] **Step 5: Write the shoot model**

`backend/app/models/shoot.py`:

```python
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, Timestamps, UUIDPrimaryKey
from app.models.enums import ShootStatus, pg_enum

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.image import Image


class Shoot(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "shoots"

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    shoot_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[ShootStatus] = mapped_column(
        pg_enum(ShootStatus, "shoot_status"),
        nullable=False,
        default=ShootStatus.DRAFT,
        server_default=ShootStatus.DRAFT.value,
    )
    select_limit: Mapped[int | None] = mapped_column(Integer)
    downloads_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    cover_image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "images.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_shoots_cover_image_id",
        ),
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    client: Mapped["Client"] = relationship(back_populates="shoots")
    images: Mapped[list["Image"]] = relationship(
        back_populates="shoot",
        cascade="all, delete-orphan",
        foreign_keys="Image.shoot_id",
    )
```

`use_alter=True` on `cover_image_id` is what resolves the `shoots` ↔ `images` cycle the spec flags in section 5.2: SQLAlchemy emits both `CREATE TABLE`s first and adds this one foreign key afterwards with an `ALTER`, in both directions. `foreign_keys="Image.shoot_id"` is required on the `images` relationship because two foreign keys now join these tables, and without it SQLAlchemy cannot tell which one the relationship follows.

- [ ] **Step 6: Write the image model**

`backend/app/models/image.py`:

```python
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKey
from app.models.enums import Verdict, pg_enum

if TYPE_CHECKING:
    from app.models.shoot import Shoot


class Image(UUIDPrimaryKey, Base):
    """One row per frame.

    Columns are grouped by the build step that fills them in. Everything
    below the storage group is null until the cull pipeline runs.
    """

    __tablename__ = "images"

    shoot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shoots.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Storage (step 3). Keys only - image bytes never pass through FastAPI.
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_key: Mapped[str] = mapped_column(String(500), nullable=False)
    web_key: Mapped[str | None] = mapped_column(String(500))
    thumb_key: Mapped[str | None] = mapped_column(String(500))
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    bytes: Mapped[int | None] = mapped_column(BigInteger)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Technical scores (step 4).
    blur_variance: Mapped[float | None] = mapped_column(Float)
    exposure_score: Mapped[float | None] = mapped_column(Float)
    eyes_closed: Mapped[bool | None] = mapped_column(Boolean)

    # AI verdict - written once by the pipeline, never updated.
    ai_verdict: Mapped[Verdict | None] = mapped_column(pg_enum(Verdict, "verdict"))
    ai_reasons: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)), nullable=False, server_default="{}", default=list
    )
    ai_score: Mapped[float | None] = mapped_column(Float)

    # Human verdict - set only on override.
    admin_verdict: Mapped[Verdict | None] = mapped_column(pg_enum(Verdict, "verdict"))
    admin_note: Mapped[str | None] = mapped_column(Text)

    # Gallery (step 6).
    in_gallery: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    gallery_order: Mapped[int | None] = mapped_column(Integer)

    shoot: Mapped["Shoot"] = relationship(back_populates="images", foreign_keys=[shoot_id])

    __table_args__ = (
        Index("ix_images_shoot_id", "shoot_id"),
        Index("ix_images_shoot_id_in_gallery", "shoot_id", "in_gallery"),
        Index("ix_images_shoot_id_ai_verdict", "shoot_id", "ai_verdict"),
    )
```

Both `ai_verdict` and `admin_verdict` call `pg_enum(Verdict, "verdict")`, naming the same Postgres type. SQLAlchemy emits `CREATE TYPE verdict` once and reuses it — this is intended, not a duplicate.

The dedupe columns (`dupe_group_id`, `is_best_of_burst`, `embedding`) are deliberately absent. They arrive with pgvector in step 9.

- [ ] **Step 7: Write the job, select, edit request, and final models**

`backend/app/models/job.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKey
from app.models.enums import JobKind, JobStatus, pg_enum


class Job(UUIDPrimaryKey, Base):
    """Background job state. Lives in Postgres - no Celery, no Redis."""

    __tablename__ = "jobs"

    shoot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shoots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[JobKind] = mapped_column(pg_enum(JobKind, "job_kind"), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        pg_enum(JobStatus, "job_status"),
        nullable=False,
        default=JobStatus.QUEUED,
        server_default=JobStatus.QUEUED.value,
    )
    progress_done: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    progress_total: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    error: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

`backend/app/models/select.py`:

```python
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKey

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.image import Image
    from app.models.shoot import Shoot


class Select(UUIDPrimaryKey, Base):
    """A client's heart on one image."""

    __tablename__ = "selects"

    shoot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shoots.id", ondelete="CASCADE"), nullable=False
    )
    image_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    shoot: Mapped["Shoot"] = relationship()
    image: Mapped["Image"] = relationship()
    client: Mapped["Client"] = relationship()

    __table_args__ = (
        UniqueConstraint("image_id", "client_id", name="uq_selects_image_client"),
    )
```

The unique constraint is what stops a double-tap from counting twice against `select_limit`.

`backend/app/models/edit_request.py`:

```python
import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Timestamps, UUIDPrimaryKey
from app.models.enums import EditStatus, pg_enum


class EditRequest(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "edit_requests"

    shoot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shoots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[EditStatus] = mapped_column(
        pg_enum(EditStatus, "edit_status"),
        nullable=False,
        default=EditStatus.OPEN,
        server_default=EditStatus.OPEN.value,
    )
    admin_note: Mapped[str | None] = mapped_column(Text)
```

`backend/app/models/final.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKey


class Final(UUIDPrimaryKey, Base):
    """A delivered file. image_id is nullable - a final need not map to
    exactly one original."""

    __tablename__ = "finals"

    shoot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shoots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("images.id", ondelete="SET NULL")
    )
    key: Mapped[str] = mapped_column(String(500), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    bytes: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

- [ ] **Step 8: Export every model from the package**

Replace `backend/app/models/__init__.py`:

```python
"""Importing this package registers every table on Base.metadata.

Alembic's env.py relies on that, so never trim this list.
"""

from app.models.client import Client
from app.models.edit_request import EditRequest
from app.models.final import Final
from app.models.image import Image
from app.models.job import Job
from app.models.magic_link import MagicLink
from app.models.select import Select
from app.models.shoot import Shoot
from app.models.studio_user import StudioUser

__all__ = [
    "Client",
    "EditRequest",
    "Final",
    "Image",
    "Job",
    "MagicLink",
    "Select",
    "Shoot",
    "StudioUser",
]
```

- [ ] **Step 9: Run the tests to verify they pass**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/ -v`
Expected: PASS, all tests including the five in `test_models.py`

If `test_deleting_a_shoot_cascades_to_its_images` fails, the ORM-level `cascade="all, delete-orphan"` is not reaching the flush — confirm `Shoot.images` carries both `cascade=` and `foreign_keys=`, since the `cover_image_id` ambiguity silently breaks relationship configuration.

- [ ] **Step 10: Commit**

```bash
git add backend/app/models backend/tests
git commit -m "feat(db): add all nine SQLAlchemy models

One file per table. The shoots/images foreign-key cycle is resolved with
use_alter on cover_image_id, so both tables are created before either FK
is added.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Alembic and the initial migration

**Files:**
- Create: `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/script.py.mako`, `backend/alembic/versions/<hash>_initial_schema.py`
- Test: `backend/tests/test_migrations.py`

**Interfaces:**
- Consumes: `Base` from `app.db.base` and the model registrations from `app.models` (Task 4).
- Produces: a migration reachable as `head`, applied with `alembic upgrade head` and reversed with `alembic downgrade base`.

- [ ] **Step 1: Initialize Alembic**

Run: `cd backend && .venv/Scripts/python.exe -m alembic init alembic`
Expected: creates `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, `alembic/versions/`.

- [ ] **Step 2: Point Alembic at the settings and the metadata**

In `backend/alembic.ini`, find the `sqlalchemy.url` line and blank it out — the URL comes from `Settings`, so it is never duplicated in a checked-in file:

```ini
sqlalchemy.url =
```

Replace the configuration block near the top of `backend/alembic/env.py` (keep the file's existing `run_migrations_offline` / `run_migrations_online` functions and the trailing dispatch):

```python
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.db.base import Base
import app.models  # noqa: F401  - registers every table on Base.metadata

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
```

The `import app.models` line is load-bearing: without it `Base.metadata` is empty and autogenerate produces a migration that drops every table.

- [ ] **Step 3: Autogenerate the initial migration**

```bash
cd backend
docker compose up -d db
.venv/Scripts/python.exe -m alembic revision --autogenerate -m "initial schema"
```

- [ ] **Step 4: Read the generated migration before trusting it**

Open the new file in `backend/alembic/versions/`. Check, in order:

1. `op.create_table("shoots", ...)` and `op.create_table("images", ...)` both appear, and the `fk_shoots_cover_image_id` constraint is added by a separate `op.create_foreign_key(...)` call *after* both tables — not inline. If it is inline, `use_alter=True` is missing from the model; fix Task 4 step 5 and regenerate.
2. `downgrade()` drops the tables and also drops every enum type. Autogenerate frequently omits enum drops. If `shoot_status`, `verdict`, `job_kind`, `job_status`, or `edit_status` is not dropped, add to the end of `downgrade()`:

```python
    for enum_name in ("edit_status", "job_status", "job_kind", "verdict", "shoot_status"):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
```

3. There is no `CREATE EXTENSION vector` and no `embedding` column. If either appears, something from step 9 leaked in.

- [ ] **Step 5: Write the failing round-trip test**

Create `backend/tests/test_migrations.py`:

```python
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
```

`test_downgrade_leaves_an_empty_database` and `test_upgrade_works_again_after_downgrade` are the two that earn their keep. A migration that cannot be re-run after a downgrade is the standard symptom of an undropped enum type, and it only ever bites when someone is already mid-rollback.

- [ ] **Step 6: Run the migration tests**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_migrations.py -v`
Expected: PASS, 6 tests. If the downgrade tests fail on leftover enum types, apply the fix from step 4 item 2 and rerun.

- [ ] **Step 7: Verify the whole suite together**

Run: `cd backend && .venv/Scripts/python.exe -m pytest -q`
Expected: all tests pass.

- [ ] **Step 8: Apply the migration to the real dev database**

Run: `cd backend && .venv/Scripts/python.exe -m alembic upgrade head`
Then: `.venv/Scripts/python.exe -m alembic current`
Expected: prints the revision hash with `(head)`.

- [ ] **Step 9: Commit**

```bash
git add backend/alembic.ini backend/alembic backend/tests/test_migrations.py
git commit -m "feat(db): add Alembic and the initial schema migration

Migration round-trips: upgrade head, downgrade base, upgrade again, with
enum types dropped on the way down so the second upgrade succeeds.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Shoot status transition table

**Files:**
- Create: `backend/app/services/__init__.py`, `backend/app/services/shoot_status.py`
- Test: `backend/tests/test_shoot_status.py`

**Interfaces:**
- Consumes: `ShootStatus` from `app.models.enums` (Task 3).
- Produces:
  - `LEGAL_TRANSITIONS: dict[ShootStatus, frozenset[ShootStatus]]`
  - `InvalidTransition(Exception)` with attributes `current`, `target`, and class attribute `code = "invalid_transition"`
  - `assert_transition(current: ShootStatus, target: ShootStatus) -> None`

  Step 2's routers will catch `InvalidTransition` and render it as `409 {"detail": str(exc), "code": exc.code}`.

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_shoot_status.py`:

```python
import pytest

from app.models.enums import ShootStatus
from app.services.shoot_status import (
    LEGAL_TRANSITIONS,
    InvalidTransition,
    assert_transition,
)

FORWARD_PATH = [
    (ShootStatus.DRAFT, ShootStatus.UPLOADING),
    (ShootStatus.UPLOADING, ShootStatus.CULLING),
    (ShootStatus.CULLING, ShootStatus.CULLED),
    (ShootStatus.CULLED, ShootStatus.PUBLISHED),
    (ShootStatus.PUBLISHED, ShootStatus.SELECTS_DONE),
    (ShootStatus.SELECTS_DONE, ShootStatus.DELIVERED),
]


@pytest.mark.parametrize(("current", "target"), FORWARD_PATH)
def test_every_forward_step_is_legal(current, target):
    assert_transition(current, target)


def test_unpublish_is_the_only_backward_move():
    assert_transition(ShootStatus.PUBLISHED, ShootStatus.CULLED)
    backward = [
        (ShootStatus.CULLED, ShootStatus.CULLING),
        (ShootStatus.SELECTS_DONE, ShootStatus.PUBLISHED),
        (ShootStatus.DELIVERED, ShootStatus.SELECTS_DONE),
        (ShootStatus.UPLOADING, ShootStatus.DRAFT),
    ]
    for current, target in backward:
        with pytest.raises(InvalidTransition):
            assert_transition(current, target)


def test_stages_cannot_be_skipped():
    with pytest.raises(InvalidTransition):
        assert_transition(ShootStatus.DRAFT, ShootStatus.PUBLISHED)
    with pytest.raises(InvalidTransition):
        assert_transition(ShootStatus.CULLED, ShootStatus.DELIVERED)


def test_delivered_is_terminal():
    for target in ShootStatus:
        with pytest.raises(InvalidTransition):
            assert_transition(ShootStatus.DELIVERED, target)


def test_a_shoot_cannot_transition_to_its_own_state():
    for status in ShootStatus:
        with pytest.raises(InvalidTransition):
            assert_transition(status, status)


def test_the_exception_carries_the_api_error_code():
    with pytest.raises(InvalidTransition) as exc_info:
        assert_transition(ShootStatus.DRAFT, ShootStatus.DELIVERED)
    assert exc_info.value.code == "invalid_transition"
    assert exc_info.value.current is ShootStatus.DRAFT
    assert exc_info.value.target is ShootStatus.DELIVERED
    assert "draft" in str(exc_info.value)
    assert "delivered" in str(exc_info.value)


def test_every_state_appears_in_the_table():
    assert set(LEGAL_TRANSITIONS) == set(ShootStatus)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_shoot_status.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services'`

- [ ] **Step 3: Write the transition table**

Create empty `backend/app/services/__init__.py`, then `backend/app/services/shoot_status.py`:

```python
"""The shoot status machine.

    draft -> uploading -> culling -> culled -> published
          -> selects_done -> delivered
                               ^
    published -> culled is unpublish, the only backward move.

Pure Python with no database dependency, so it is unit-testable on its
own. Guards that need to read data - refusing to publish a shoot with an
empty gallery, for instance - belong in the routers, not here.
"""

from app.models.enums import ShootStatus

LEGAL_TRANSITIONS: dict[ShootStatus, frozenset[ShootStatus]] = {
    ShootStatus.DRAFT: frozenset({ShootStatus.UPLOADING}),
    ShootStatus.UPLOADING: frozenset({ShootStatus.CULLING}),
    ShootStatus.CULLING: frozenset({ShootStatus.CULLED}),
    ShootStatus.CULLED: frozenset({ShootStatus.PUBLISHED}),
    ShootStatus.PUBLISHED: frozenset({ShootStatus.SELECTS_DONE, ShootStatus.CULLED}),
    ShootStatus.SELECTS_DONE: frozenset({ShootStatus.DELIVERED}),
    ShootStatus.DELIVERED: frozenset(),
}


class InvalidTransition(Exception):
    """Raised when a shoot is asked to move to a state it cannot reach.

    Routers render this as 409 with the `code` below, per CLAUDE.md
    section 7.
    """

    code = "invalid_transition"

    def __init__(self, current: ShootStatus, target: ShootStatus) -> None:
        self.current = current
        self.target = target
        super().__init__(
            f"A shoot cannot move from {current.value} to {target.value}."
        )


def assert_transition(current: ShootStatus, target: ShootStatus) -> None:
    """Raise InvalidTransition unless current -> target is allowed."""
    if target not in LEGAL_TRANSITIONS[current]:
        raise InvalidTransition(current, target)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_shoot_status.py -v`
Expected: PASS, 12 tests (6 parametrized + 6 others)

- [ ] **Step 5: Run the full suite**

Run: `cd backend && .venv/Scripts/python.exe -m pytest -q`
Expected: every test passes.

- [ ] **Step 6: Commit**

```bash
git add backend/app/services backend/tests/test_shoot_status.py
git commit -m "feat(shoots): add the status transition table

Seven states, strictly forward except published -> culled (unpublish).
Pure Python, no database dependency. InvalidTransition carries the
invalid_transition error code the routers will render as 409.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Verification: definition of done

Run every one of these and confirm the output before calling step 1 complete.

```bash
cd backend
docker compose up -d db                                  # Postgres is up
.venv/Scripts/python.exe -m alembic upgrade head         # schema applies
.venv/Scripts/python.exe -m alembic downgrade base       # and reverses
.venv/Scripts/python.exe -m alembic upgrade head         # and reapplies
.venv/Scripts/python.exe -m pytest -q                    # all tests pass
.venv/Scripts/python.exe -m uvicorn app.main:app --reload  # /health serves
```

And from the repo root, `git log --oneline` shows the restructure as its own commit, distinct from the backend work.

## What this step does NOT deliver

Stated so the next session does not assume otherwise: no authentication, no endpoints beyond `/health`, no storage integration, no thumbnails, no ML, no pgvector. Those are build steps 2 through 9. The API contract is not frozen yet — it freezes at step 3, and from that point on every column name here is contract surface.
