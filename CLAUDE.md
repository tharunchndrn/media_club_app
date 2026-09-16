# CLAUDE.md - Studio 006 Client Portal

## 1. What this project is

A photography client portal with AI-assisted culling.

- **Studio side (React admin):** upload a shoot, auto-cull it, review rejections, build a gallery, publish to the client, work the edit queue, deliver finals.
- **Client side (Flutter app):** open a magic link, browse their gallery, select favourites, request edits, download finals, track status.
- **Backend (Python/FastAPI):** the only place business logic lives. Both clients are thin consumers of one API.

The AI is not decoration. A model trained on the studio's own historical select/reject decisions ranks images and predicts which frames the photographer would keep.

## 2. Non-negotiable rules for the agent

1. **Do not write Flutter or React feature code.** The developer is learning both frameworks; generating that code defeats the purpose of the project. Allowed: explain concepts, review code the developer wrote, give a skeleton file with `// TODO:` markers and an explanation of what goes in each, debug an error the developer hit.
2. **Backend, ML, SQL, Docker, CI, and scripts** may be written in full.
3. **Freeze the API contract before frontend work starts.** Any change to it must be flagged loudly, because two clients consume it.
4. **No feature may be added that is not in section 6.** Suggest it, do not build it.
5. **Free-tier constraints in section 8 are hard limits**, not preferences.

## 3. Architecture

```
Flutter (client)            React admin (studio)
        |                            |
        +----------+-----------------+
                   |
             FastAPI (REST, JWT)
                   |
        +----------+----------+
        |                     |
   Postgres + pgvector    Object storage (R2)
        |                        |
   ML pipeline (background tasks) -> delivery CDN
```

Image bytes never pass through FastAPI. Clients upload directly to object storage using a pre-signed URL issued by the API.

## 4. Tech stack

**Backend**
- Python 3.11, FastAPI, Uvicorn
- SQLAlchemy 2.x + Alembic migrations
- Pydantic v2 for all request/response schemas
- PostgreSQL + pgvector
- OpenCV, Pillow for technical scoring
- PyTorch or ONNX Runtime for the aesthetic model
- `BackgroundTasks` for job processing (no Celery/Redis - see section 8)
- pytest

**Admin (React)**
- Vite + React 18 + TypeScript
- TanStack Query for server state
- React Router
- Tailwind CSS
- Axios

**Client (Flutter)**
- Flutter 3.x, Dart 3
- Riverpod for state
- Dio for HTTP
- go_router for navigation
- cached_network_image
- flutter_secure_storage for the session token

## 5. Repo structure

```
studio-portal/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/           # config, security, deps
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/v1/         # routers: auth, clients, shoots, images, selects, edits
│   │   ├── services/       # storage, email, job orchestration
│   │   └── ml/
│   │       ├── technical.py    # blur, exposure, eyes-closed
│   │       ├── dedupe.py       # embeddings + near-duplicate grouping
│   │       ├── aesthetic.py    # trained scorer
│   │       └── pipeline.py     # orchestration
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── admin/                  # React (Vite)
│   └── src/{api,components,pages,hooks,types}
├── client_app/             # Flutter
│   └── lib/{core,features,shared}
├── ml_training/            # notebooks + training scripts, not deployed
└── docs/
    ├── api-contract.md
    ├── data-model.md
    └── architecture.png
```

## 6. Scope - the complete feature list

**In scope (build these, nothing more)**

Backend
- Magic-link auth for clients, email+password for studio; JWT, two roles
- Clients CRUD, Shoots CRUD with status machine
- Pre-signed upload URLs, image records, thumbnail generation
- Cull job trigger, job status polling
- Gallery publish/unpublish, select limits, download permission
- Client selects, edit requests with notes and status
- Finals upload, delivery marking

React admin
- Login, client list, shoot list, shoot detail
- Bulk upload with progress
- Cull review screen: Keep / Rejected tabs, rejection reason per image, override
- Gallery builder: choose, reorder, cover, publish
- Edit-request worklist
- Finals upload, mark delivered
- Dashboard: shoots by stage, model agreement rate

Flutter client
- Magic-link entry, session storage
- Gallery grid, full-screen viewer with swipe
- Heart to select, respect select limit
- Request edit with a note
- AI-suggested badge, accept or override
- Downloads, delivery status

ML
- Technical scoring: Laplacian blur variance, exposure histogram, face landmark eyes-closed
- Near-duplicate grouping via embedding cosine similarity, best-of-burst
- Aesthetic scorer: pretrained backbone + fine-tuned head on the studio's select/reject history
- Evaluation script reporting precision/recall against held-out shoots

**Explicitly out of scope**
Payments, contracts, RAW processing, watermarking, multi-photographer accounts, video, mobile admin, push notifications, social publishing.

## 7. Conventions

- REST, plural nouns: `/api/v1/shoots/{id}/images`
- snake_case in JSON and Python; camelCase only inside TS/Dart models
- All responses wrapped in Pydantic schemas, never raw ORM objects
- Errors: `{ "detail": "...", "code": "..." }`, correct HTTP status
- UUID primary keys everywhere
- Timestamps UTC, ISO 8601
- Every migration through Alembic, no manual schema edits
- Commits: `feat(scope):`, `fix(scope):`, `docs(scope):`

## 8. Free-tier constraints (hard)

| Layer | Service | Limit that bites |
|---|---|---|
| Admin | Vercel / Netlify / CF Pages | none meaningful |
| Flutter | APK on GitHub Releases + web build on Netlify | none |
| API | Render free web service | sleeps after 15 min idle, ~1 min cold start, 750 instance-hours/month |
| DB | Supabase or Neon free Postgres | **never Render's free Postgres - it expires after 30 days** |
| Originals | Cloudflare R2 (10 GB, zero egress) | storage |
| Delivery | ImageKit or Cloudinary free tier | bandwidth |

Rules this forces:
- Never serve originals to a gallery. Generate a 1200px web version on upload and serve only that.
- Thumbnails generated once, cached hard, never on-the-fly.
- ML runs on upload only, never on view.
- No Celery, no Redis. `BackgroundTasks` + job status in Postgres. Document the Celery upgrade path in the README as a deliberate trade-off.
- Demo shoots capped at 200 images.

## 9. Commands

```bash
# backend
uvicorn app.main:app --reload
alembic revision --autogenerate -m "msg" && alembic upgrade head
pytest -q

# admin
npm run dev | npm run build

# flutter
flutter run
flutter build apk --release
flutter build web
```

## 10. Build order

1. Data model + migrations
2. Auth (both roles)
3. Upload + storage + thumbnails
4. Technical culling layer (rules only, no ML)
5. React admin: upload + cull review
6. Gallery publish + client auth
7. Flutter: gallery, viewer, selects
8. Edit requests + finals + delivery
9. Aesthetic model training + integration
10. Dockerise, CI, deploy all three, write docs

Backend before frontends. Contract frozen at step 3.

## 11. Definition of done

- All three pieces deployed and reachable by URL
- README with architecture diagram, API contract, setup steps
- pytest on backend, widget tests on at least three Flutter screens
- GitHub Actions running tests on push
- A measured model number: agreement rate against held-out shoots
