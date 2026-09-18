# NIBM KIC Media Club — Admin

React admin frontend for the Media Club platform (committee-facing). See
`../CLAUDE.md` (project spec) and `../docs/api-contract.md` (backend API
contract) for authoritative context.

## Stack

Vite + React 18 + TypeScript, TanStack Query, React Router, Tailwind CSS,
Axios with a JWT interceptor.

## Setup

```bash
npm install
cp .env.example .env   # adjust VITE_API_BASE_URL if the backend isn't on :8000
npm run dev
```

## Scripts

- `npm run dev` — start the dev server
- `npm run build` — type-check and build for production
- `npm run lint` — oxlint
- `npm run test -- --run` — run the Vitest suite once (non-interactive, used in CI)

## Notes / known gaps (see docs/api-contract.md)

- No "Themes view" — `POST /suggestions/analyse` and `GET /suggestions/themes`
  don't exist yet (pending the clustering engine).
- No photo reorder — only add (appends) and delete exist on the backend.
- No committee member edit — only add and delete exist; there is no
  `PATCH /committee/{id}`.
- Admin login is enforced client-side: any valid credentials get a JWT from
  `POST /auth/login` (it doesn't check role), so the app calls `GET /auth/me`
  after login and rejects non-admin accounts locally.
