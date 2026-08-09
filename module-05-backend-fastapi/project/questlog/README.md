# QuestLog — Module 05 (frontend + backend)

Per `RUNNING_PROJECT.md`, this folder is where QuestLog's real backend
begins. It contains **two separate projects, side by side**:

```
project/questlog/
├── frontend/   — Module 04's finished React + TypeScript + Tailwind + React Router app, copied
│                 forward, with its mocked fetchQuests() swapped for real HTTP calls (see
│                 frontend/README.md for exactly what changed)
└── backend/    — a brand-new FastAPI backend, built in this module (see backend/README.md)
```

**Why two separate folders, not one merged project:** they are genuinely
different projects — different language (Python vs. TypeScript), different
package manager (`pip` vs. `npm`), different tooling, different venvs/
`node_modules`. Keeping them as clear siblings, each with its own
dependency file and its own README, mirrors how a real full-stack repo is
almost always laid out, and avoids ever mixing `pip install` and
`npm install` output into the same folder.

## How they relate

`frontend/` is a browser app that, once running, makes real HTTP requests
(via `fetch()`, in `frontend/src/api/questsApi.ts`) to `backend/`, which
must be running separately, on `http://localhost:8000`, for the frontend
to show real data instead of a permanent error banner. Neither project
knows anything about the other beyond that one HTTP contract (the exact
routes documented in `backend/README.md`) — this is precisely the
client/server separation Module 02 taught from first principles, now real.

## Running both together

Two terminals, per this module's [`lessons/00-setup.md`](../../lessons/00-setup.md), Step 6:

**Terminal 1 — backend:**
```bash
cd module-05-backend-fastapi/project/questlog/backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Terminal 2 — frontend:**
```bash
cd module-05-backend-fastapi/project/questlog/frontend
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). The Quest
Board should show a brief loading spinner, then five seeded quests —
now served by the FastAPI process in Terminal 1, not a hard-coded mock
array. Adding, editing, completing, and deleting quests all now make real
requests you can watch in Terminal 1's own logs (Uvicorn prints each
incoming request).

## What changed from Module 04, precisely

See [`frontend/README.md`](./frontend/README.md)'s own "What actually
changed" section for the exact file-by-file diff. In short: one new file
(`src/api/questsApi.ts`, replacing `src/api/fetchQuests.ts`), one file's
mutation functions made `async` (`src/context/QuestsContext.tsx`), and two
call sites updated to `await` them (`NewQuestPage.tsx`, `QuestDetailPage.tsx`).
Every component, every page's rendering logic, and the entire domain model
(`types/quest.ts`) are untouched.

## Verified while writing this module

- `backend/`: a real venv was created, `pip install -r requirements.txt`
  actually run, `uvicorn app.main:app --reload` actually started, and every
  route in `backend/README.md`'s table was actually exercised with `curl`
  (list, get, create, update, delete, stats, and a deliberate `404`/`422`).
- `frontend/`: `npm install` and `npm run build` were actually run against
  the updated codebase, with zero TypeScript errors.
- See this module's own root `README.md` for whether the two were also
  confirmed running simultaneously with a real browser round-trip, or only
  verified independently plus by careful reading — stated there plainly,
  not glossed over.
