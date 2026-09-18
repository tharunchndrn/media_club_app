# CLAUDE.md - NIBM KIC Media Club App

## 1. What this project is

A club platform with two audiences and one API.

- **Students (Flutter app):** browse events, view past event galleries, see the committee by academic year, submit suggestions and requests, track what happened to them.
- **Committee (React admin):** manage events and photos, manage committee members per year, work the suggestions inbox, and read the AI-generated theme view.
- **Backend (Python/FastAPI):** the only place business logic lives. Both clients are thin consumers.

The AI layer is the suggestion engine: it clusters free-text student submissions into ranked themes, merges near-duplicates, and scores sentiment. It is a model you build and evaluate, not an LLM API call.

## 2. Scope lock

Anything not listed in section 3 is **v2**. Do not build it, do not scaffold it, do not add database columns for it. Explicitly deferred: blog, merchandise and orders, push notifications, content drafting, photo auto-tagging, attendance, chat, analytics beyond counts.

## 3. Features - the complete v1 list

### Student app (Flutter)
- Register with NIBM email, name, **batch**, optional student ID; login; logout
- Events feed: upcoming and past, filter by academic year
- Event detail: title, description, venue, date, photo gallery, full-screen viewer
- Committee page: members grouped by academic year, with position, photo, LinkedIn
- Submit a suggestion: category + free text, optional anonymous toggle
- My suggestions: list with status (new, reviewing, planned, declined)
- Profile: view own details

### Committee admin (React)
- Admin-only login
- Events: create, edit, delete, publish/draft toggle
- Photos per event: add by URL, reorder, set cover, delete
- Committee members: add, edit, delete, grouped by academic year
- Suggestions inbox: list, filter by category/status/theme/batch, change status
- **Themes view:** clustered themes ranked by volume, keywords, duplicate count, average sentiment, drill into member suggestions
- Dashboard: event count, suggestion count by status, recent activity

### AI - suggestion engine
- TF-IDF vectorisation, near-duplicate merging by cosine similarity, KMeans clustering
- Keyword-derived theme labels
- Sentiment score per suggestion and averaged per theme
- Re-runnable on demand from the admin; results persisted to the suggestion rows
- Evaluation script: hand-label a sample of suggestions with true themes, report clustering agreement. **This number goes on the CV.**

## 4. Decisions already made - do not reopen

| Decision | Ruling |
|---|---|
| Who posts events | Admins only. No multi-role committee permissions in v1. |
| Photo storage | Metadata in DB, files in object storage. **Never image BLOBs in the database.** |
| Photo upload in v1 | Admin pastes an external URL (Cloudinary/R2/Drive). Direct upload with pre-signed URLs is v2. |
| Name and batch on suggestions | Taken from the user profile, never retyped on the form. |
| Anonymous suggestions | Kept. `author_id` stored internally for abuse control, hidden in API responses and admin UI. |
| Auth | Email + password, JWT, two roles: `student`, `admin`. |
| AI scope | Suggestion clustering only. No LLM, no vision model. |

## 5. Suggestion categories (fixed enum)

```
event-idea         # "do a photowalk", "host an inter-batch quiz"
coverage-request   # asking media club to cover something
design-request     # posters, banners, certificates
workshop-request   # training in photography, editing, design
collaboration      # other clubs, societies, external parties
equipment          # gear, studio access, booking issues
feedback           # on club output or events
complaint          # service or conduct issues
other
```

Free text is required alongside the category, minimum 10 characters, maximum 2000. The clustering engine needs body text; the category alone is not enough signal.

## 6. Architecture

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
  (TF-IDF + KMeans)
```

## 7. Tech stack

**Backend**
- Python 3.11, FastAPI, Uvicorn
- SQLAlchemy 2.x, Alembic
- Pydantic v2 for every request and response
- PostgreSQL (SQLite acceptable for local dev only)
- scikit-learn, numpy for the suggestion engine
- python-jose (JWT), passlib[bcrypt]
- pytest

**Admin (React)**
- Vite + React 18 + TypeScript
- TanStack Query for server state
- React Router
- Tailwind CSS
- Axios with a JWT interceptor

**Student app (Flutter)**
- Flutter 3.x, Dart 3
- Riverpod for state
- Dio with a JWT interceptor
- go_router
- cached_network_image
- flutter_secure_storage

## 8. Data model

```
users(id, name, email, password_hash, role, batch, student_id, created_at)
events(id, title, slug, description, venue, event_date, cover_image_url,
       status, academic_year, created_at)
photos(id, event_id, image_url, thumb_url, caption, alt_text, sort_order)
committee_members(id, name, position, academic_year, photo_url,
                  linkedin_url, sort_order)
suggestions(id, author_id, category, body, status, theme_id, theme_label,
            sentiment, is_anonymous, created_at)
```

Notes:
- UUID string primary keys throughout
- `users.batch` is required at registration; suggestions inherit it through the author relation
- `suggestions.theme_id` and `theme_label` are written by the clustering run, never by a client
- `photos.image_url` is an external URL; the database stores no binary data

## 9. API surface

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/me

GET    /api/v1/events?year=&status=
GET    /api/v1/events/{id}
POST   /api/v1/events                      admin
PATCH  /api/v1/events/{id}                 admin
DELETE /api/v1/events/{id}                 admin
POST   /api/v1/events/{id}/photos          admin
DELETE /api/v1/events/{id}/photos/{pid}    admin

GET    /api/v1/committee?year=
GET    /api/v1/committee/years
POST   /api/v1/committee                   admin
DELETE /api/v1/committee/{id}              admin

GET    /api/v1/suggestions/categories
POST   /api/v1/suggestions
GET    /api/v1/suggestions/mine
GET    /api/v1/suggestions?status=&theme_id=&batch=   admin
PATCH  /api/v1/suggestions/{id}            admin
POST   /api/v1/suggestions/analyse         admin
GET    /api/v1/suggestions/themes          admin
```

**The contract freezes once the Flutter app starts.** Any change after that must be flagged loudly - two clients consume it.

## 10. Repo structure

```
mediaclub/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py, database.py, security.py
│   │   ├── models.py, schemas.py
│   │   ├── routers/   auth.py events.py committee.py suggestions.py
│   │   └── ml/        suggestion_engine.py
│   ├── alembic/
│   ├── tests/
│   ├── seed.py
│   ├── Dockerfile
│   └── requirements.txt
├── admin/          # Vite React TS
│   └── src/{api,components,pages,hooks,types}
├── client_app/     # Flutter
│   └── lib/{core,models,features/{auth,events,committee,suggestions}}
├── ml_eval/        # labelled sample + clustering evaluation script
└── docs/           # api-contract.md, data-model.md, architecture.png
```

## 11. Conventions

- REST, plural nouns, `/api/v1/` prefix
- snake_case in JSON and Python; camelCase only inside TS and Dart models
- Responses always through Pydantic schemas, never raw ORM objects
- Errors: `{"detail": "..."}` with correct HTTP status
- Timestamps UTC, ISO 8601
- All schema changes through Alembic
- Commits: `feat(scope):`, `fix(scope):`, `docs(scope):`

## 12. Deployment - free tier, hard constraints

| Layer | Service | Constraint |
|---|---|---|
| Admin | Vercel / Netlify / CF Pages | none meaningful |
| Flutter | APK on GitHub Releases + web build on Netlify | build both |
| API | Render free web service | sleeps after 15 min idle, ~1 min cold start |
| DB | Supabase or Neon free Postgres | **never Render free Postgres - it expires after 30 days** |
| Images | Cloudflare R2 or Cloudinary free tier | storage and bandwidth are the binding limits |

Rules this forces:
- No image bytes in Postgres, ever
- Serve web-size images and thumbnails, never originals
- Clustering runs on demand from the admin, never on every request
- No Celery or Redis; clustering is fast enough to run inline

## 13. Build order

1. Data model + migrations + seed script
2. Auth, both roles
3. Events + photos + committee endpoints
4. Suggestion submission + suggestion engine + themes endpoint
5. **Freeze API contract, write docs/api-contract.md**
6. React admin: login, events, photos, committee
7. React admin: suggestions inbox + themes view
8. Flutter: auth, events feed, event detail, gallery
9. Flutter: committee, suggestion submission, my suggestions
10. Tests, Dockerfile, CI, deploy all three, README

## 14. Definition of done

- All three deployed and reachable by URL
- README with architecture diagram, API contract, setup steps
- pytest on the backend, widget tests on at least three Flutter screens
- GitHub Actions running tests on push
- A measured clustering number from `ml_eval/`
- Documented free-tier trade-offs