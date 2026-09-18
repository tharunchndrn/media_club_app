# API Contract — NIBM KIC Media Club

Base URL (dev): `http://localhost:8000`. All endpoints below are under `/api/v1` unless noted. `GET /health` (no prefix) returns `{"status": "ok"}`.

Auth: JWT bearer token (`Authorization: Bearer <token>`), obtained from `POST /auth/login`. Two roles: `student`, `admin`. Endpoints marked **admin** return `403` for a non-admin token and `401` for a missing/invalid token.

Errors: `{"detail": "..."}` with the HTTP status shown. Validation errors (422) return FastAPI's standard `{"detail": [...]}` array shape.

**Status: implemented vs planned.** Everything below is implemented and tested except `POST /suggestions/analyse` and `GET /suggestions/themes`, which depend on the suggestion-clustering engine (TF-IDF/KMeans) and are **not yet built**. Do not wire UI to those two until they exist.

---

## Auth

### `POST /auth/register`
Student self-registration only — there is no admin self-registration; admin accounts are provisioned directly in the database (see `backend/seed.py`).

Request:
```json
{
  "name": "Kasun Silva",
  "email": "kasun.silva@nibm.lk",
  "password": "studentpass123",
  "batch": "2023/2024",
  "student_id": "NIBM23001"
}
```
- `email` must end in `@nibm.lk` (422 otherwise)
- `password` min 8, max 128 chars
- `student_id` optional

Response `201`:
```json
{
  "id": "uuid",
  "name": "Kasun Silva",
  "email": "kasun.silva@nibm.lk",
  "role": "student",
  "batch": "2023/2024",
  "student_id": "NIBM23001",
  "created_at": "2026-09-17T15:27:51.310958Z"
}
```
`409` if the email is already registered.

### `POST /auth/login`
Request: `{"email": "...", "password": "..."}`
Response `200`: `{"access_token": "...", "token_type": "bearer"}`
`401` on wrong email/password.

### `GET /auth/me`
Requires auth. Response `200`: same `UserResponse` shape as register. `401` if missing/invalid token.

There is no logout endpoint — logout is client-side token discard (`flutter_secure_storage` clear / local storage clear).

---

## Events

### `GET /events?year=&status=`
Public. No `status` param → returns **published events only**. Pass `status=draft` (admin UI) to see drafts. `year` filters on `academic_year` (exact match, e.g. `"2025/2026"`). Sorted by `event_date` descending.

Response `200`, array of:
```json
{
  "id": "uuid",
  "title": "Inter-Batch Photowalk",
  "slug": "inter-batch-photowalk",
  "description": "...",
  "venue": "Main lawn",
  "event_date": "2026-10-15T09:00:00Z",
  "cover_image_url": "https://... or null",
  "status": "draft | published",
  "academic_year": "2025/2026",
  "created_at": "..."
}
```

### `GET /events/{id}`
Public. Same shape as above plus `"photos": [PhotoResponse, ...]` (see below), ordered by `sort_order`. `404` if not found.

### `POST /events` — admin
Request:
```json
{
  "title": "Inter-Batch Photowalk",
  "description": "...",
  "venue": "Main lawn",
  "event_date": "2026-10-15T09:00:00Z",
  "academic_year": "2025/2026",
  "cover_image_url": null,
  "status": "draft"
}
```
`slug` is generated server-side from `title` (never sent by the client); collisions get a numeric suffix. `status` defaults to `"draft"`. Response `201`, same shape as `GET /events` list item.

### `PATCH /events/{id}` — admin
Partial update — send only the fields to change (any subset of the `POST` body fields, all optional). Commonly used to toggle `status` (publish/draft) and to set `cover_image_url` (the admin's "set cover" action — pick one of the event's photo URLs and PATCH it in; there is no separate cover-flag column). Response `200`, same shape as list item. `404` if not found.

### `DELETE /events/{id}` — admin
`204`. Cascades to the event's photos. `404` if not found.

### `POST /events/{id}/photos` — admin
Request:
```json
{
  "image_url": "https://...",
  "thumb_url": "https://... or null",
  "caption": "... or null",
  "alt_text": "... or null",
  "sort_order": null
}
```
`image_url` is an external URL the admin pastes in (Cloudinary/R2/Drive) — there is no upload endpoint, no binary data ever touches this API. Omit `sort_order` to append to the end of the gallery. Response `201`:
```json
{
  "id": "uuid",
  "event_id": "uuid",
  "image_url": "...",
  "thumb_url": "... or null",
  "caption": "... or null",
  "alt_text": "... or null",
  "sort_order": 0
}
```

### `DELETE /events/{id}/photos/{photo_id}` — admin
`204`. `404` if the photo doesn't exist or doesn't belong to that event.

**Known gap:** CLAUDE.md's admin feature list mentions photo "reorder," but there is no reorder endpoint in the frozen surface — only add (which appends) and delete. If you need reorder in the admin UI, that requires adding an endpoint (e.g. `PATCH /events/{id}/photos/{photo_id}` with a `sort_order` body) — flag this rather than inventing an undocumented call.

---

## Committee

### `GET /committee?year=`
Public. `year` filters on `academic_year`. Sorted by `sort_order`.

Response `200`, array of:
```json
{
  "id": "uuid",
  "name": "Grace Hopper",
  "position": "President",
  "academic_year": "2025/2026",
  "photo_url": "https://... or null",
  "linkedin_url": "https://... or null",
  "sort_order": 0
}
```

### `GET /committee/years`
Public. Response `200`: `["2025/2026", "2024/2025", ...]` — distinct `academic_year` values, descending.

### `POST /committee` — admin
Request: same fields as the response minus `id` (`sort_order` optional, defaults `0`). Response `201`, same shape as list item.

### `DELETE /committee/{id}` — admin
`204`. `404` if not found.

---

## Suggestions

### `GET /suggestions/categories`
Public. Response `200`, the nine fixed values in this exact order:
```json
["event-idea", "coverage-request", "design-request", "workshop-request", "collaboration", "equipment", "feedback", "complaint", "other"]
```

### `POST /suggestions`
Requires auth (any role). `author`/name/batch come from the JWT — never sent in the body (CLAUDE.md decision: name/batch are never retyped on the form).

Request:
```json
{
  "category": "event-idea",
  "body": "Host an inter-batch quiz on photography basics.",
  "is_anonymous": false
}
```
`body` min 10, max 2000 chars (422 otherwise). Response `201`:
```json
{
  "id": "uuid",
  "category": "event-idea",
  "body": "...",
  "status": "new",
  "theme_id": null,
  "theme_label": null,
  "sentiment": null,
  "is_anonymous": false,
  "created_at": "..."
}
```
`theme_id`/`theme_label`/`sentiment` are always null until the (not-yet-built) clustering engine runs — never set by a client.

### `GET /suggestions/mine`
Requires auth. Returns only the caller's own suggestions (same shape as the `POST` response), newest first.

### `GET /suggestions?status=&theme_id=&batch=` — admin
All filters optional. Response `200`, array of:
```json
{
  "id": "uuid",
  "category": "event-idea",
  "body": "...",
  "status": "new",
  "theme_id": null,
  "theme_label": null,
  "sentiment": null,
  "is_anonymous": true,
  "created_at": "...",
  "author_name": null,
  "author_batch": null
}
```
When `is_anonymous` is `true`, `author_name` and `author_batch` are always `null` — anonymity is enforced server-side, not just hidden in the UI. (`batch` filtering still works server-side against the real author even for anonymous rows; it's just not echoed back.)

### `PATCH /suggestions/{id}` — admin
Request: `{"status": "reviewing"}` (one of `new`, `reviewing`, `planned`, `declined`). Response `200`, same shape as the admin list item. `404` if not found.

### Not yet implemented
- `POST /suggestions/analyse` — admin, re-runs the TF-IDF/KMeans clustering pipeline
- `GET /suggestions/themes` — admin, ranked theme list with drill-down

Both are pending the ML suggestion-engine build (`backend/app/ml/suggestion_engine.py`, not yet created). The React admin's "Themes view" should not be built until these exist.

---

## Enums (exact wire values)

- `UserRole`: `student`, `admin`
- `EventStatus`: `draft`, `published`
- `SuggestionCategory`: `event-idea`, `coverage-request`, `design-request`, `workshop-request`, `collaboration`, `equipment`, `feedback`, `complaint`, `other`
- `SuggestionStatus`: `new`, `reviewing`, `planned`, `declined`

## Conventions

- snake_case JSON keys throughout (map to camelCase in TS/Dart models client-side)
- Timestamps: UTC, ISO 8601 (e.g. `2026-09-17T15:27:51.310958Z`)
- UUIDs as strings
- No pagination yet on any list endpoint (v1 data volumes are small — a club, not a platform)
