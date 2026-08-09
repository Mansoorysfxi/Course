# QuestLog (web) — frontend (Module 11 adds optional Sentry monitoring)

This is Module 07's finished, authenticated `questlog` frontend, carried
forward through Module 08 (Vitest + React Testing Library, 17 tests),
Module 09 (deployed manually, no code changes), Module 10 (containerized
— `Dockerfile`, `nginx.conf`, one `package.json` change moving two
Windows-only native-binding packages to `optionalDependencies` — see
[`../README.md`](../README.md)), and now Module 11, which adds exactly
one small, optional thing: Sentry error tracking, off by default —
`src/monitoring.ts` (new), a one-line added import in `src/main.tsx`,
two new env var type declarations in `src/vite-env.d.ts`, the
`@sentry/react` dependency in `package.json`, and two added `ARG`/`ENV`
pairs in `Dockerfile` so a real DSN can be baked in at build time when
this module's CI/CD pipeline builds a production image. **Every actual
page/component under `src/pages/`, `src/components/`, `src/context/`,
and `src/api/` is byte-for-byte unchanged since Module 08.** See
[`../../../lessons/06-monitoring-logging-and-error-tracking.md`](../../../../module-11-cicd-cloud-production/lessons/06-monitoring-logging-and-error-tracking.md)
for the full explanation. For the testing
material taught in Module 08, see
[`module-08-testing-and-quality/lessons/07-frontend-testing-with-vitest-and-rtl.md`](../../../../module-08-testing-and-quality/lessons/07-frontend-testing-with-vitest-and-rtl.md).

QuestLog is a personal quest (task) tracker with light RPG framing. This
is a React + TypeScript single-page app, built with Vite, styled with
Tailwind CSS, routed with React Router. Quest data is fetched from, and
persisted to, a real, separately-running FastAPI process — and, as of
this module, every request that touches quest data must carry a valid
JWT, or the backend rejects it outright.

## What's new in Module 08

- **`src/test-setup.ts` (new)** — Vitest's global test setup: extends
  `expect` with `@testing-library/jest-dom`'s matchers and calls
  `cleanup()` after every test.
- **`vite.config.ts`** — now imports `defineConfig` from `vitest/config`
  instead of plain `vite`, adding a `test` block (`environment: "jsdom"`,
  `setupFiles`).
- **`.prettierrc.json` / `.prettierignore` (new)**.
- **Four new test files** — see this README's top section.

## What's new in Module 11

- **`src/monitoring.ts` (new)** — calls `Sentry.init(...)` only if
  `import.meta.env.VITE_SENTRY_DSN` is actually set; a no-op import
  otherwise. See
  [`../../../lessons/06-monitoring-logging-and-error-tracking.md`](../../../../module-11-cicd-cloud-production/lessons/06-monitoring-logging-and-error-tracking.md).
- **`src/main.tsx`** — one added line: `import "./monitoring.ts";`, first,
  before anything else, so Sentry (if configured) is watching from the
  very first render.
- **`src/vite-env.d.ts`** — two added type declarations:
  `VITE_SENTRY_DSN`, `VITE_ENVIRONMENT`.
- **`package.json`** — one new dependency, `@sentry/react` (`^10.69.0`,
  verified via npm, August 2026).
- **`Dockerfile`** — two added `ARG`/`ENV` pairs so
  `VITE_SENTRY_DSN`/`VITE_ENVIRONMENT` can be passed as Docker build
  arguments (see `../.github/workflows/ci-cd.yml`'s `build-args:`), both
  defaulting to values that leave Sentry off if not overridden.

Everything below this point describes the application itself, unchanged
since Module 07.

## What changed from the Module 06 version (Module 07's own history, unchanged since)

- **`src/context/AuthContext.tsx`** — owns `user`/`loading`/`error`
  and exposes `login`, `signup`, `logout`. On first load, if a token is
  already sitting in `localStorage` from a previous visit, it calls
  `GET /api/auth/me` to find out whether it's still valid and restore
  `user` from the answer.
- **`src/api/authApi.ts` (new)** — `signup`, `login`, `fetchCurrentUser`,
  calling the backend's three new `/api/auth/*` routes.
- **`src/api/http.ts` (new)** — the shared `fetch()` plumbing
  (`request`/`requestForm`), extracted from Module 06's `questsApi.ts` so
  `authApi.ts` can reuse it too. Automatically attaches
  `Authorization: Bearer <token>` to every JSON request when a token is
  stored, and exports `UnauthorizedError` for a 401 specifically.
- **`src/api/questsApi.ts`** — unchanged in shape; now imports `request`
  from `http.ts` instead of defining its own private copy.
- **`src/context/QuestsContext.tsx`** — its fetch effect now checks
  `useAuth().user` first and does nothing (and clears `quests`) if
  there's no logged-in user; every request it makes is now implicitly
  authenticated via `http.ts`.
- **`src/components/ProtectedRoute.tsx` (new)** — redirects to `/login`
  if there's no logged-in user; wraps every quest-related route in
  `App.tsx`.
- **`src/pages/LoginPage.tsx` / `SignupPage.tsx` (new)**.
- **`src/components/Layout.tsx`** — shows the signed-in user's email and
  a "Log out" button.
- **`src/App.tsx` / `src/main.tsx`** — `/login` and `/signup` added as
  unprotected routes; `<AuthProvider>` now wraps `<QuestsProvider>`.

`types/quest.ts` and every component under `components/` other than
`Layout.tsx` are untouched — the quest domain model itself didn't change
at all this module; only _who_ can reach it did.

## Stack (verified while writing this module, August 2026)

| Tool         | Version  | Notes                                                                                     |
| ------------ | -------- | ----------------------------------------------------------------------------------------- |
| Node.js      | 24.x LTS | Installed in Module 03; Vite 8 requires 20.19+/22.12+.                                    |
| Vite         | 8.2.0    | Unchanged since Module 04.                                                                |
| React        | 19.2.x   | `react` + `react-dom`. Unchanged.                                                         |
| TypeScript   | 7.0.2    | Unchanged since Module 03.                                                                |
| Tailwind CSS | 4.3.3    | Via the `@tailwindcss/vite` plugin. Unchanged.                                            |
| React Router | 8.3.0    | `Navigate` (new use, in `ProtectedRoute.tsx`) is part of the same package already in use. |

No new npm packages were needed this module — everything above is
built on `fetch()`, `localStorage`, and React Router primitives already
in the project.

## Running this project

**The backend (`../backend/`) must be running first**, with a `.env`
containing a real `SECRET_KEY` — see
[`../backend/README.md`](../backend/README.md) and this module's
[`lessons/00-setup.md`](../../../lessons/00-setup.md).

```bash
cd module-11-cicd-cloud-production/project/questlog/frontend
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). You should
land on `/login` (redirected there automatically, since you're not
logged in yet). Log in with the seeded demo account
(`player@questlog.local` / `dragon-slayer-1` — see `../backend/README.md`)
or create your own via "Sign up."

Other scripts:

```bash
npm run build     # tsc -b && vite build -- type-checks and produces dist/
npm run preview   # serves the built dist/ locally, to sanity-check a real build
npm run lint       # oxlint (the linter create-vite scaffolds by default)
npm run test       # vitest run -- NEW in Module 08, expect: Tests  17 passed (17)
npm run format     # prettier --write . -- NEW in Module 08
```

## Project structure

```
src/
├── types/
│   ├── quest.ts               — the Quest domain model (unchanged)
│   └── auth.ts                — AuthUser / AuthToken (new)
├── api/
│   ├── http.ts                — shared fetch() plumbing + token storage (new)
│   ├── authApi.ts              — signup/login/fetchCurrentUser (new)
│   └── questsApi.ts            — quest CRUD calls (unchanged in shape)
├── context/
│   ├── AuthContext.tsx          — useAuth(); owns the logged-in user + token lifecycle (new)
│   └── QuestsContext.tsx         — useQuests(); now auth-gated
├── components/
│   ├── ProtectedRoute.tsx         — redirects to /login if not authenticated (new)
│   ├── Layout.tsx                  — now shows user email + logout
│   └── ...                          — unchanged (QuestCard, QuestForm, ...)
├── pages/
│   ├── LoginPage.tsx                — new
│   ├── SignupPage.tsx                — new
│   └── ...                            — unchanged (QuestListPage, NewQuestPage, ...)
├── App.tsx                             — route table, now with /login, /signup, ProtectedRoute
└── main.tsx                             — mounts <AuthProvider><QuestsProvider><App /></QuestsProvider></AuthProvider>
```

## What it does

- **`/login`** — email + password form; on success, stores the returned
  JWT and redirects to the Quest Board (or wherever you were headed).
- **`/signup`** — email + password form; creates an account, then logs
  it in immediately.
- **Quest Board (`/`)**, **New Quest (`/quests/new`)**, **Quest detail
  (`/quests/:id`)** — unchanged in behavior, now reachable only while
  logged in; each shows only _your_ quests.
- **Log out** — clears the stored token and returns to `/login`.
- **404 page** — for any unmatched route, reachable either way.

Every concept used to build this has a dedicated lesson — see the table
in [`../BRIEF.md`](../../BRIEF.md).
