# QuestLog (web) — Module 04 reference solution

This is the **Module 04 capstone reference solution** for the course's
running project. See [`../BRIEF.md`](../BRIEF.md) for the full assignment
this codebase satisfies, and the module's
[`README.md`](../../README.md) for how this fits into the course.

QuestLog is a personal quest (task) tracker with light RPG framing. This
version is a React + TypeScript single-page app, built with Vite, styled
with Tailwind CSS, routed with React Router, with all data held in React
state — there is **no real backend yet**. Module 05 adds one (FastAPI),
copying this exact codebase forward as its starting point.

## Stack (verified while writing this module, August 2026)

| Tool | Version | Notes |
|---|---|---|
| Node.js | 24.x LTS | Installed in Module 03; Vite 8 requires 20.19+/22.12+. |
| Vite | 8.2.0 | Scaffolded with `npm create vite@latest` (`react-ts` template). |
| React | 19.2.x | `react` + `react-dom`. |
| TypeScript | 7.0.2 | Same version verified in Module 03. |
| Tailwind CSS | 4.3.3 | Via the `@tailwindcss/vite` plugin — no `tailwind.config.js` needed. |
| React Router | 8.3.0 | Declarative mode; imports from the unified `react-router` package (`react-router-dom` no longer exists as of v8). |

## Running this project

```bash
cd module-04-react/project/questlog
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). See
[`lessons/00-setup.md`](../../lessons/00-setup.md) for the full,
from-scratch version of these steps and troubleshooting.

Other scripts:

```bash
npm run build     # tsc -b && vite build -- type-checks and produces dist/
npm run preview   # serves the built dist/ locally, to sanity-check a real build
npm run lint       # oxlint (the linter create-vite scaffolds by default)
```

**Verified while writing this module:** `npm install` and `npm run build`
were both actually run against this exact codebase, with zero TypeScript
errors and a successful production build (Tailwind's Vite plugin scanned
every component and emitted real utility CSS, confirming the styling is
wired up correctly, not just present in source).

## Project structure

```
src/
├── types/quest.ts            — the Quest domain model (Quest, Priority, NewQuestInput, QuestUpdate)
├── api/fetchQuests.ts        — the mocked async "backend" (Promise + setTimeout, can fail)
├── context/QuestsContext.tsx — the useQuests() custom hook; owns all quest state + CRUD
├── components/               — reusable, mostly presentational pieces (QuestCard, QuestForm, ...)
├── pages/                    — one component per route (QuestListPage, NewQuestPage, ...)
├── App.tsx                   — the route table
└── main.tsx                  — mounts <BrowserRouter><QuestsProvider><App /></QuestsProvider></BrowserRouter>
```

## What it does

- **Quest Board (`/`)** — lists all quests, with controls to filter by
  quest line/priority/done-status and sort by newest/priority/title.
  Shows a loading spinner while the mocked fetch is in flight, and a
  retryable error banner if it fails (it fails randomly ~15% of the time
  on its own, and can be forced via `fetchQuests({ forceError: true })`).
- **New Quest (`/quests/new`)** — a controlled form to add a quest.
- **Quest detail (`/quests/:id`)** — view a single quest, toggle done,
  edit it (reusing the same form component), or delete it (with a
  confirmation prompt).
- **404 page** — for any unmatched route.

Every one of these concepts has a dedicated lesson — see the table in
[`../BRIEF.md`](../BRIEF.md).
