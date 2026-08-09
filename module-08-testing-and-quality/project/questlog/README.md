# QuestLog — Module 08 (frontend + backend, now with a real test suite)

Per `RUNNING_PROJECT.md`, this folder is Module 07's finished,
authenticated `questlog/` copied forward. **QuestLog's own features are
unchanged this module** — no new route, page, or database column was
added. What's new: a real, passing backend test suite (`backend/tests/`,
31 tests), a real, passing frontend test suite
(`frontend/src/**/*.test.tsx`, 17 tests), `ruff` + `prettier` configured
and clean on both sides, and a working `.pre-commit-config.yaml`
(this folder) wiring all of it together automatically.

```
project/questlog/
├── frontend/                  — unchanged app code; NEW: Vitest + React Testing Library + 4 test files
├── backend/                   — unchanged app code; NEW: pytest + pytest-asyncio + httpx + 3 test files
└── .pre-commit-config.yaml    — NEW: runs ruff/prettier/oxlint/both test suites automatically on commit
```

## Why two separate folders, not one merged project

Unchanged reasoning from every prior module: they are genuinely different
projects (different language, different package manager, different
tooling), kept as clear siblings the way a real full-stack repo almost
always is laid out.

## How they relate

`frontend/` makes real HTTP requests to `backend/`, which must be running
separately on `http://localhost:8000`. **What's different this module:**
every request the frontend makes to `/api/quests/*` now carries an
`Authorization: Bearer <token>` header, obtained by first calling
`POST /api/auth/login` — see [`lessons/00-setup.md`](../../lessons/00-setup.md)
and both READMEs' "Running this project" sections for the exact steps.

## Running both together

**Terminal 1 — backend:**
```bash
cd module-08-testing-and-quality/project/questlog/backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste into .env's SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

**Terminal 2 — frontend:**
```bash
cd module-08-testing-and-quality/project/questlog/frontend
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). You should
land on `/login`. Log in with the seeded demo account
(`player@questlog.local` / `dragon-slayer-1`) or sign up your own. Either
way, the Quest Board should show only that account's quests — create a
second account (a private/incognito browser window is the easiest way to
be logged into two accounts at once) and confirm each account sees a
completely separate quest list, and that a quest's URL
(`/quests/<id>`) copied from one account's session shows a 404 when
opened while logged in as the other account.

## Running the real test suites

```bash
cd backend && python -m pytest -v          # expect: 31 passed
cd ../frontend && npm run test              # expect: Tests  17 passed (17)
```

See [`backend/README.md`](./backend/README.md) and
[`frontend/README.md`](./frontend/README.md) for exactly what's new since
Module 07 on each side, and this module's own
[`lessons/`](../../lessons/) for the full teaching material behind every
test file. The quest/auth application code itself
(`app/models.py`'s `Quest`, `types/quest.ts`, every route, every
component) is unchanged from Module 07 — only tests and tooling were
added.

## Verified while writing this module

Every number in this file was produced by actually running the command
shown, not estimated — see this module's root
[`README.md`](../../README.md) and `project/BRIEF.md` for the full, honest
account, including which parts (the backend test database, specifically)
deliberately use SQLite instead of a real running PostgreSQL instance,
and why (`lessons/06-testing-with-a-database.md`).
