# Data Model — NIBM KIC Media Club

PostgreSQL, SQLAlchemy 2.x models, Alembic-managed. UUID primary keys throughout (native Postgres `UUID`, serialized as strings over the API). No BLOB columns anywhere — photo storage is metadata + external URL only.

## `users`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `name` | varchar(200) | |
| `email` | varchar(320) | unique, must end `@nibm.lk` (enforced at the API layer, not DB) |
| `password_hash` | varchar(255) | bcrypt |
| `role` | enum `user_role` | `student` \| `admin`, default `student` |
| `batch` | varchar(50) | required at registration |
| `student_id` | varchar(50) | optional |
| `created_at` | timestamptz | server default `now()` |

Admin accounts are provisioned directly (seed script / DB), never via self-registration.

## `events`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `title` | varchar(200) | |
| `slug` | varchar(220) | unique, server-generated from `title`, never client-supplied |
| `description` | text | |
| `venue` | varchar(200) | |
| `event_date` | timestamptz | |
| `cover_image_url` | varchar(500) | nullable — doubles as the "set cover" mechanism; no separate cover flag |
| `status` | enum `event_status` | `draft` \| `published`, default `draft` |
| `academic_year` | varchar(20) | indexed, e.g. `"2025/2026"` |
| `created_at` | timestamptz | server default `now()` |

`events.photos` — one-to-many, cascade delete.

## `photos`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `event_id` | UUID | FK → `events.id`, `ON DELETE CASCADE`, indexed |
| `image_url` | varchar(500) | external URL (Cloudinary/R2/Drive) — no binary data |
| `thumb_url` | varchar(500) | nullable |
| `caption` | varchar(300) | nullable |
| `alt_text` | varchar(300) | nullable |
| `sort_order` | integer | default `0`; new photos append (`max(sort_order) + 1`) |

## `committee_members`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `name` | varchar(200) | |
| `position` | varchar(150) | |
| `academic_year` | varchar(20) | indexed |
| `photo_url` | varchar(500) | nullable |
| `linkedin_url` | varchar(500) | nullable |
| `sort_order` | integer | default `0` |

No `updated_at`, no timestamps at all — matches CLAUDE.md's data model exactly (not an oversight).

## `suggestions`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `author_id` | UUID | FK → `users.id`, `ON DELETE CASCADE`, indexed |
| `category` | enum `suggestion_category` | the 9 fixed values (see below) |
| `body` | text | 10–2000 chars, enforced at the API layer |
| `status` | enum `suggestion_status` | `new` \| `reviewing` \| `planned` \| `declined`, default `new` |
| `theme_id` | varchar(50) | nullable, indexed — written only by the (not-yet-built) clustering run |
| `theme_label` | varchar(200) | nullable — ditto |
| `sentiment` | float | nullable — ditto |
| `is_anonymous` | boolean | default `false` |
| `created_at` | timestamptz | server default `now()` |

Anonymity: `author_id` is always stored (abuse control), but the API hides `author_name`/`author_batch` from every response when `is_anonymous` is true — enforced server-side in `app/routers/suggestions.py`, not just a UI convention.

## Enums (exact wire values)

- `user_role`: `student`, `admin`
- `event_status`: `draft`, `published`
- `suggestion_category`: `event-idea`, `coverage-request`, `design-request`, `workshop-request`, `collaboration`, `equipment`, `feedback`, `complaint`, `other`
- `suggestion_status`: `new`, `reviewing`, `planned`, `declined`

## Not yet in the schema

Nothing suggestion-clustering-related has landed yet: no `themes` table, no embedding/vector columns (the `pgvector` extension is available in the dev image but unused). `theme_id`/`theme_label`/`sentiment` on `suggestions` are the only hooks currently in place for that future work.
