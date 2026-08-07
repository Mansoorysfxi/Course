# QuestLog (web) — frontend, now wired to a real backend (Module 05)

This is **Module 04's finished `questlog` capstone, copied forward**
(per `RUNNING_PROJECT.md`'s repo-location convention) and updated by Module
05 to call a real FastAPI backend instead of a mocked, fake `fetchQuests()`.
See [`../../BRIEF.md`](../../BRIEF.md) for the full Module 05 capstone
assignment, and [`../README.md`](../README.md) for exactly how this
`frontend/` folder relates to the new `../backend/` folder alongside it.

QuestLog is a personal quest (task) tracker with light RPG framing. This
is a React + TypeScript single-page app, built with Vite, styled with
Tailwind CSS, routed with React Router. As of Module 05, quest data is no
longer held only in local React state — it's fetched from, and persisted
to (in-memory, on the server — see Lesson 08), a real, separately-running
FastAPI process.

## What actually changed from the Module 04 version

Per this module's own `README.md`, only two files changed, and no page or
component needed to change its own logic beyond awaiting a now-`async`
function:

- **`src/api/fetchQuests.ts` was replaced by `src/api/questsApi.ts`.** The
  old file was a fake Promise + `setTimeout` that could randomly fail. The
  new file makes real `fetch()` calls to `http://localhost:8000` (configurable
  via `VITE_API_BASE_URL` in `.env`) for every quest operation — list, get,
  create, update, delete — reading real error responses from the backend
  (Lesson 03/06's error shapes) instead of a hard-coded failure message.
- **`src/context/QuestsContext.tsx`'s mutation functions
  (`addQuest`/`updateQuest`/`deleteQuest`/`toggleDone`) are now `async`**
  and call the real API, updating `quests` from the backend's actual
  response rather than a locally-invented object. Each one catches its own
  errors into the same `error` state `QuestListPage` already renders via
  `ErrorBanner` — no new UI concept, the exact one Module 04 already built.
  `NewQuestPage.tsx` and `QuestDetailPage.tsx` were updated to `await` these
  calls before navigating.

Nothing about `types/quest.ts`, any component in `components/`, `App.tsx`,
or `main.tsx` changed at all — proof that isolating the "backend" behind
one file (`questsApi.ts`) and one context (`QuestsContext.tsx`), exactly as
Module 04's own BRIEF.md set up, is what made this swap this small.

## Stack (verified while writing this module, August 2026)

| Tool | Version | Notes |
|---|---|---|
| Node.js | 24.x LTS | Installed in Module 03; Vite 8 requires 20.19+/22.12+. |
| Vite | 8.2.0 | Scaffolded with `npm create vite@latest` (`react-ts` template) in Module 04. |
| React | 19.2.x | `react` + `react-dom`. |
| TypeScript | 7.0.2 | Same version verified in Module 03. |
| Tailwind CSS | 4.3.3 | Via the `@tailwindcss/vite` plugin — no `tailwind.config.js` needed. |
| React Router | 8.3.0 | Declarative mode; imports from the unified `react-router` package (`react-router-dom` no longer exists as of v8). |

## Running this project

**The backend (`../backend/`) must be running first** — see
[`../backend/README.md`](../backend/README.md) and this module's
[`lessons/00-setup.md`](../../../lessons/00-setup.md), Step 6, for running
both at once in two terminals.

```bash
cd module-05-backend-fastapi/project/questlog/frontend
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`).

Other scripts:

```bash
npm run build     # tsc -b && vite build -- type-checks and produces dist/
npm run preview   # serves the built dist/ locally, to sanity-check a real build
npm run lint       # oxlint (the linter create-vite scaffolds by default)
```

## Project structure

```
src/
├── types/quest.ts            — the Quest domain model (unchanged from Module 04)
├── api/questsApi.ts          — real fetch() calls to the FastAPI backend (Module 05; replaces fetchQuests.ts)
├── context/QuestsContext.tsx — useQuests(); owns all quest state + CRUD, now via real HTTP requests
├── components/               — unchanged from Module 04 (QuestCard, QuestForm, ...)
├── pages/                    — unchanged from Module 04, except awaiting now-async mutation calls
├── App.tsx                   — the route table (unchanged)
└── main.tsx                  — mounts <BrowserRouter><QuestsProvider><App /></QuestsProvider></BrowserRouter> (unchanged)
```

## What it does

- **Quest Board (`/`)** — lists all quests, with controls to filter by
  quest line/priority/done-status and sort by newest/priority/title.
  Shows a loading spinner while the real fetch is in flight, and a
  retryable error banner if the backend can't be reached or returns an
  error.
- **New Quest (`/quests/new`)** — a controlled form to add a quest (a real `POST`).
- **Quest detail (`/quests/:id`)** — view a single quest, toggle done, edit
  it (reusing the same form component), or delete it (a real `PATCH`/`DELETE`,
  with a confirmation prompt before deleting).
- **404 page** — for any unmatched route.

Every concept used to build this has a dedicated lesson — see the table in
[`../BRIEF.md`](../../BRIEF.md).
