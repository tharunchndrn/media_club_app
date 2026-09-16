# Studio 006 — Data Model and Backend Scaffold

Date: 2026-09-16
Status: approved
Covers: build order step 1 (data model + migrations), plus the backend scaffold and repo restructure that step 1 requires.

## 1. Goal

Stand up the repository in the shape CLAUDE.md section 5 describes, create the FastAPI backend skeleton, and define the complete database schema as Alembic migrations that apply and roll back cleanly against Postgres.

Out of scope for this spec: authentication logic, endpoints, storage integration, and any ML. Those are steps 2 onward. This spec defines the tables those steps will use, and nothing that consumes them.

## 2. Repo restructure

The repository currently holds an untouched `flutter create` scaffold at its root. It becomes a monorepo:

```
studio-portal/            (repo root, git init'd here)
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/           config, security, deps
│   │   ├── models/         SQLAlchemy models
│   │   ├── schemas/        Pydantic schemas
│   │   ├── api/v1/         routers
│   │   ├── services/       storage, email, job orchestration
│   │   └── ml/
│   ├── alembic/
│   ├── tests/
│   ├── docker-compose.yml
│   ├── .env.example
│   └── requirements.txt
├── client_app/           existing Flutter app, moved and renamed
├── admin/                empty until step 5
├── ml_training/
└── docs/
```

The Flutter app moves from the root into `client_app/` and its package is renamed from `flutter_application_1` to `studio_client`. Nothing is lost: the app is unmodified boilerplate. The root gains its own `.gitignore` covering Python, Node, and editor artifacts; the Flutter `.gitignore` travels with the app into `client_app/`.

## 3. Development environment

Postgres runs from `backend/docker-compose.yml` using the `pgvector/pgvector:pg16` image on `localhost:5432`. A natively installed Postgres is equally acceptable; the backend reads one `DATABASE_URL` and does not care which is behind it.

pgvector is **not** a prerequisite for this spec. The `embedding` column and its `CREATE EXTENSION vector` land in a separate, later migration (section 5.3), so steps 1 through 8 run against stock Postgres.

Python is 3.11. Step-1 dependencies are deliberately minimal:

```
fastapi, uvicorn[standard], sqlalchemy[asyncio], alembic,
psycopg[binary], pydantic, pydantic-settings, pytest, pytest-asyncio
```

OpenCV, Pillow, and the ML runtime arrive at steps 4 and 9. Keeping them out now keeps installs fast and the eventual Render image small, which matters under the section 8 free-tier limits.

## 4. Conventions applied

Every rule below comes from CLAUDE.md section 7 and is restated here so the migrations have a single reference:

- UUID primary keys on every table, generated application-side
- All timestamps `TIMESTAMPTZ`, stored UTC, serialized ISO 8601
- snake_case column names
- Every schema change through Alembic; no manual DDL
- Enums as native Postgres enum types, created and dropped by migration

## 5. Schema

### 5.1 Identity and access

**`studio_users`** — studio staff, email + password login.

| column | type | notes |
|---|---|---|
| `id` | uuid | PK |
| `email` | text | unique, lowercased on write |
| `password_hash` | text | bcrypt |
| `name` | text | |
| `is_active` | bool | default true |
| `created_at` / `updated_at` | timestamptz | |

**`clients`** — the studio's customers. Clients never have a password; they authenticate by magic link.

| column | type | notes |
|---|---|---|
| `id` | uuid | PK |
| `name` | text | |
| `email` | text | unique |
| `phone` | text | nullable |
| `notes` | text | nullable |
| `created_at` / `updated_at` | timestamptz | |

**`magic_links`** — single-use client login tokens.

| column | type | notes |
|---|---|---|
| `id` | uuid | PK |
| `client_id` | uuid | FK to clients, ON DELETE CASCADE |
| `token_hash` | text | sha256 of the emailed token; the raw token is never stored |
| `expires_at` | timestamptz | |
| `used_at` | timestamptz | nullable; non-null means spent |
| `created_at` | timestamptz | |

Index on `token_hash`. JWTs carry `sub` (uuid) and `role` (`studio` or `client`), which is how section 6's two roles are expressed without a shared users table.

### 5.2 Shoots

**`shoots`**

| column | type | notes |
|---|---|---|
| `id` | uuid | PK |
| `client_id` | uuid | FK to clients |
| `title` | text | |
| `shoot_date` | date | nullable |
| `status` | enum `shoot_status` | see 5.5 |
| `select_limit` | int | nullable; null means unlimited |
| `downloads_enabled` | bool | default false |
| `cover_image_id` | uuid | nullable, FK to images, ON DELETE SET NULL |
| `published_at` | timestamptz | nullable |
| `delivered_at` | timestamptz | nullable |
| `created_at` / `updated_at` | timestamptz | |

`cover_image_id` and `images.shoot_id` are mutually referential. The migration creates `shoots` first, then `images`, then adds the `cover_image_id` foreign key in a third step.

### 5.3 Images

One row per frame. Its columns fall into six groups that belong to different build steps; they are separated here so later steps can fill them in without touching the others.

**Storage (step 3)** — keys only. Image bytes never pass through FastAPI.

| column | type | notes |
|---|---|---|
| `id` | uuid | PK |
| `shoot_id` | uuid | FK to shoots, ON DELETE CASCADE |
| `filename` | text | original upload name |
| `original_key` | text | R2 object key |
| `web_key` | text | nullable; 1200px derivative, the only thing a gallery serves |
| `thumb_key` | text | nullable; generated once, cached hard |
| `width` / `height` | int | nullable until processed |
| `bytes` | bigint | nullable |
| `captured_at` | timestamptz | nullable, from EXIF |
| `uploaded_at` | timestamptz | |

**Technical scores (step 4)** — `blur_variance` float, `exposure_score` float, `eyes_closed` bool, all nullable until the cull runs.

**AI verdict — immutable.** Written once by the pipeline, never updated.

| column | type | notes |
|---|---|---|
| `ai_verdict` | enum `verdict` (`keep` or `reject`) | nullable before cull |
| `ai_reasons` | text[] | `blur`, `eyes_closed`, `exposure`, `duplicate` |
| `ai_score` | float | nullable |

**Human verdict.** `admin_verdict` (same enum, nullable) is set only on override; `admin_note` text is optional.

The effective verdict is `COALESCE(admin_verdict, ai_verdict)`. Model agreement rate is then one query with no audit table:

```sql
SELECT count(*) FILTER (
         WHERE admin_verdict IS NULL OR admin_verdict = ai_verdict
       )::float / count(*)
FROM images WHERE ai_verdict IS NOT NULL;
```

Keeping the AI's call immutable also means step 9's training set has its labels for free: `ai_verdict` is the prediction, the effective verdict is the ground truth.

**Gallery (step 6)** — `in_gallery` bool default false, `gallery_order` int nullable.

**Dedupe (step 9), added by a later migration** — `dupe_group_id` uuid nullable, `is_best_of_burst` bool default false, `embedding vector(512)` nullable. This migration, and only this one, runs `CREATE EXTENSION IF NOT EXISTS vector`.

Indexes: `(shoot_id)`, `(shoot_id, in_gallery)`, `(shoot_id, ai_verdict)`.

### 5.4 Jobs, selects, edits, finals

**`jobs`** — cull job status, polled by the admin. No Celery, no Redis; job state lives in Postgres per section 8.

`id`, `shoot_id` FK, `kind` enum (`cull`), `status` enum (`queued`, `running`, `succeeded`, `failed`), `progress_done` int, `progress_total` int, `error` text nullable, `started_at`, `finished_at`, `created_at`.

**`selects`** — a client's hearts. `id`, `shoot_id`, `image_id`, `client_id`, `created_at`, with a unique constraint on `(image_id, client_id)` so a double-tap cannot double-count against the select limit.

**`edit_requests`** — `id`, `shoot_id`, `image_id`, `client_id`, `note` text, `status` enum (`open`, `in_progress`, `done`, `rejected`), `admin_note` text nullable, `created_at`, `updated_at`.

**`finals`** — `id`, `shoot_id`, `image_id` nullable (a final need not map to one original), `key`, `filename`, `bytes`, `created_at`.

### 5.5 Shoot status machine

```
draft -> uploading -> culling -> culled -> published -> selects_done -> delivered
                                   ^___________|  (unpublish)
```

| state | meaning | entered by |
|---|---|---|
| `draft` | shoot created, nothing uploaded | create |
| `uploading` | presigned URLs issued | first upload URL request |
| `culling` | cull job running | cull trigger |
| `culled` | job finished, admin reviewing | job completion |
| `published` | client can see the gallery | publish |
| `selects_done` | client finished picking | client confirms selects |
| `delivered` | finals uploaded and marked | mark delivered |

`published -> culled` is the only backward transition, and it is what unpublish does.

The legal-transition table lives in `app/services/shoot_status.py` as a plain dict of `state -> frozenset(states)`, with a single `assert_transition(current, target)` helper. It is pure Python with no database dependency, so it is directly unit-testable. An illegal transition raises, and the API layer renders that as `409` with `{"detail": "...", "code": "invalid_transition"}` per section 7.

Guards beyond the transition table — for example, refusing to publish a shoot with zero gallery images — belong to the endpoints in later steps, not to this table.

## 6. Testing

pytest, run against a throwaway database created and dropped per session.

1. **Migration round-trip.** `alembic upgrade head` from empty, then `downgrade base`, then upgrade again. Catches missing enum drops and bad FK ordering, which is exactly where the `cover_image_id` cycle could bite.
2. **Schema assertions.** After `upgrade head`, reflect the database and assert every table, enum, unique constraint, and index in section 5 exists.
3. **Transition table.** Every legal transition passes; a representative set of illegal ones raises. Pure unit tests, no database.
4. **Model smoke test.** Insert a client, shoot, image, select chain through the SQLAlchemy models and read it back, confirming defaults, cascade deletes, and the `(image_id, client_id)` unique constraint.

## 7. Risks

- **pgvector availability.** Mitigated by deferring the vector column to its own migration; nothing before step 9 needs it.
- **The `shoots` / `images` FK cycle.** Mitigated by the three-step migration described in 5.2, and directly covered by test 1.
- **Contract freeze.** CLAUDE.md section 2 rule 3 freezes the API contract at step 3. This spec defines storage, not the contract, but the column names here become the JSON field names, so renaming a column after step 3 is a contract change and must be flagged loudly.

## 8. Definition of done for this step

- Repo restructured; `git log` shows the move as its own commit
- `docker compose up -d db` brings up Postgres
- `alembic upgrade head` creates the full schema on an empty database
- `alembic downgrade base` returns it to empty
- `pytest -q` passes in `backend/`
- `uvicorn app.main:app --reload` serves `/health`
