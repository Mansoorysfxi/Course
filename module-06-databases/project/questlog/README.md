# QuestLog — Module 06 (frontend + backend)

Per `RUNNING_PROJECT.md`, this folder is Module 05's finished `questlog/`
copied forward, with real PostgreSQL persistence added to the backend:

```
project/questlog/
├── frontend/   — Module 05's finished React + TypeScript + Tailwind + React Router app, copied
│                 forward UNCHANGED — see frontend/README.md, "What changed": nothing.
└── backend/    — Module 05's FastAPI backend, copied forward and given a real database layer
                  (SQLAlchemy 2.0 + Alembic + PostgreSQL) in place of its in-memory dict.
                  See backend/README.md for exactly what was added.
```

## Why two separate folders, not one merged project

Unchanged reasoning from Module 05: they are genuinely different projects
(different language, different package manager, different tooling), kept
as clear siblings the way a real full-stack repo almost always is laid out.

## How they relate

Exactly as in Module 05 — `frontend/` makes real HTTP requests to
`backend/`, which must be running separately on `http://localhost:8000`.
**What's different this module:** `backend/` now also needs a running
PostgreSQL server and an applied migration before it can serve a single
request — see [`lessons/00-setup.md`](../../lessons/00-setup.md) and
[`backend/README.md`](./backend/README.md)'s "Running this project" section
for the exact new steps (`alembic upgrade head` before `uvicorn`).

## Running both together

Three terminals this time (Postgres itself is usually a background
service, not something you keep a terminal open for, but is listed for
clarity):

**0 — PostgreSQL running** (as a Windows service or however
[`lessons/00-setup.md`](../../lessons/00-setup.md) had you install it — no
terminal needed if it's running as a service).

**Terminal 1 — backend:**
```bash
cd module-06-databases/project/questlog/backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Terminal 2 — frontend:**
```bash
cd module-06-databases/project/questlog/frontend
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). The Quest
Board should show a brief loading spinner, then five seeded quests — now
served from a real PostgreSQL table via `app/repository.py`, not an
in-memory Python `dict` that would have reset on every backend restart.
Restart the backend process (Ctrl+C, then `uvicorn app.main:app --reload`
again) and refresh the browser: unlike Module 05, your quests are still
there — that's the entire point of this module, made visible.

## What changed from Module 05, precisely

See [`backend/README.md`](./backend/README.md) for the full file-by-file
account. In short: `app/store.py` (an in-memory dict) was replaced by
`app/db_models.py` (SQLAlchemy ORM classes) + `app/database.py` (the async
engine/session) + `app/repository.py` (real queries), a new `alembic/`
folder was added with one migration, every route in `app/routers/quests.py`
gained `async` and a database-session parameter, and `requirements.txt`
gained `sqlalchemy[asyncio]`, `alembic`, and `asyncpg`. Every route's path,
method, status code, and JSON shape is byte-for-byte identical to Module
05 — `frontend/` required zero changes, confirmed in
`frontend/README.md`.

## Verified while writing this module

See this module's root [`README.md`](../../README.md) for the full, honest
account of what was verified against a real running PostgreSQL instance
versus hand-verified, including the specific routes and migration commands
that were actually exercised.
