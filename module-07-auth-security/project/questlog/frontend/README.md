# QuestLog (web) — frontend, gains real login in Module 07

This is Module 06's finished `questlog` frontend, copied forward and given
exactly the minimum a real multi-user app needs on the client side: a
login page, a signup page, a place to keep the JWT the backend now
issues, and protection on every page that shows quest data. See
[`../../BRIEF.md`](../../BRIEF.md) for the full capstone brief and
[`../backend/README.md`](../backend/README.md) for everything that
changed on the server side this module.

QuestLog is a personal quest (task) tracker with light RPG framing. This
is a React + TypeScript single-page app, built with Vite, styled with
Tailwind CSS, routed with React Router. Quest data is fetched from, and
persisted to, a real, separately-running FastAPI process — and, as of
this module, every request that touches quest data must carry a valid
JWT, or the backend rejects it outright.

## What changed from the Module 06 version

- **`src/context/AuthContext.tsx` (new)** — owns `user`/`loading`/`error`
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
at all this module; only *who* can reach it did.

## Stack (verified while writing this module, August 2026)

| Tool | Version | Notes |
|---|---|---|
| Node.js | 24.x LTS | Installed in Module 03; Vite 8 requires 20.19+/22.12+. |
| Vite | 8.2.0 | Unchanged since Module 04. |
| React | 19.2.x | `react` + `react-dom`. Unchanged. |
| TypeScript | 7.0.2 | Unchanged since Module 03. |
| Tailwind CSS | 4.3.3 | Via the `@tailwindcss/vite` plugin. Unchanged. |
| React Router | 8.3.0 | `Navigate` (new use, in `ProtectedRoute.tsx`) is part of the same package already in use. |

No new npm packages were needed this module — everything above is
built on `fetch()`, `localStorage`, and React Router primitives already
in the project.

## Running this project

**The backend (`../backend/`) must be running first**, with a `.env`
containing a real `SECRET_KEY` — see
[`../backend/README.md`](../backend/README.md) and this module's
[`lessons/00-setup.md`](../../../lessons/00-setup.md).

```bash
cd module-07-auth-security/project/questlog/frontend
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
  logged in; each shows only *your* quests.
- **Log out** — clears the stored token and returns to `/login`.
- **404 page** — for any unmatched route, reachable either way.

Every concept used to build this has a dedicated lesson — see the table
in [`../BRIEF.md`](../../BRIEF.md).
