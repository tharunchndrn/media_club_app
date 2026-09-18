# NIBM KIC Media Club

A club platform with two audiences and one API: a Flutter app for students and a React admin for the committee, both thin consumers of a FastAPI backend. Full spec: [`CLAUDE.md`](CLAUDE.md).

## Architecture

```
Flutter (students)          React admin (committee)
        |                            |
        +-------------+--------------+
                      |
                FastAPI (REST, JWT)
                      |
         +------------+------------+
         |                         |
   PostgreSQL              Object storage (R2 / Cloudinary)
         |                         |
  Suggestion engine          CDN delivery
  (not yet built)
```

- **`backend/`** — Python 3.11, FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL. Auth (JWT, `student`/`admin` roles), events + photos, committee members, suggestions (submit/list/status). See [`docs/api-contract.md`](docs/api-contract.md) and [`docs/data-model.md`](docs/data-model.md).
- **`admin/`** — Vite + React 19 + TypeScript, TanStack Query, React Router, Tailwind CSS. See [`admin/README.md`](admin/README.md).
- **`client_app/`** — Flutter 3.x, Riverpod, Dio, go_router. See below for setup; no separate README yet.
- **`ml_eval/`** — reserved for the suggestion-clustering evaluation script. Not built yet (see "What's not built" below).

## What's not built yet

The suggestion **clustering engine** (TF-IDF + KMeans theme clustering, sentiment scoring, `POST /suggestions/analyse`, `GET /suggestions/themes`, the React "Themes view", and the `ml_eval/` evaluation script) is out of scope for this pass. Suggestion **submission** (student side) and the **suggestions inbox** with status changes (admin side) are fully built — suggestions just never get a `theme_id`/`theme_label`/`sentiment` yet.

Two contract gaps worth resolving before they're needed:
- No photo-reorder endpoint (`POST`/`DELETE` on `/events/{id}/photos` only — new photos append via `sort_order`).
- No committee-member edit endpoint (`POST`/`DELETE` on `/committee` only, no `PATCH`).

## Setup

### Backend

```bash
cd backend
docker compose up -d db          # Postgres on localhost:5433
cp .env.example .env             # already matches docker-compose defaults
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # Windows
alembic upgrade head
python seed.py                   # optional: admin@nibm.lk / adminpass123, a sample student, events, photos, committee, suggestions
python -m pytest                 # 76 tests
uvicorn app.main:app --reload    # http://localhost:8000, docs at /docs
```

### Admin

```bash
cd admin
npm install
cp .env.example .env             # VITE_API_BASE_URL, defaults to http://localhost:8000/api/v1
npm run dev
```

### Flutter client

```bash
cd client_app
flutter pub get
flutter test                     # 9 widget tests
flutter run                      # needs a device/emulator; API base URL is in lib/core/api_config.dart
                                  # (Android emulator: change localhost to 10.0.2.2, see the comment there)
```

## CI

`.github/workflows/ci.yml` runs three jobs on every push/PR: `backend` (pytest against a Postgres service container), `admin` (`npm ci`, lint, `vitest --run`), `client_app` (`flutter pub get`, `flutter test`).

## Deployment (free tier — not yet deployed)

Per CLAUDE.md section 12: Render free web service for the API (sleeps after 15 min idle), Supabase/Neon free Postgres (never Render's free Postgres — it expires after 30 days), Cloudflare R2 or Cloudinary for images, Vercel/Netlify/CF Pages for the admin, APK on GitHub Releases + Netlify web build for Flutter. `backend/Dockerfile` is ready for Render; the admin and Flutter builds are static-output and deploy as-is to their respective free hosts. None of the three are live yet — this is local-dev-verified only.
