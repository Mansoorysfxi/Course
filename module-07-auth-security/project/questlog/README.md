# QuestLog — Module 07 (frontend + backend)

Per `RUNNING_PROJECT.md`, this folder is Module 06's finished `questlog/`
copied forward, with real signup/login/JWT authentication added:

```
project/questlog/
├── frontend/   — Module 06's finished React + TypeScript + Tailwind + React Router app, copied
│                 forward, now with a login/signup flow and a token attached to every request.
│                 See frontend/README.md, "What changed."
└── backend/    — Module 06's FastAPI backend, copied forward and given real password hashing,
                  JWT issuing/verification, and per-user quest ownership.
                  See backend/README.md for exactly what was added.
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
cd module-07-auth-security/project/questlog/backend
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
cd module-07-auth-security/project/questlog/frontend
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

## What changed from Module 06, precisely

See [`backend/README.md`](./backend/README.md) and
[`frontend/README.md`](./frontend/README.md) for the full file-by-file
accounts. In short: the backend gained `app/security.py` (password
hashing + JWT), a rewritten `app/config.py` (pydantic-settings, a real
`SECRET_KEY`), `app/routers/auth.py`, a `CurrentUser` dependency that
protects every quest route, and an `owner_id`-scoped `app/repository.py`;
the frontend gained an `AuthContext`, a login/signup UI, and a
`ProtectedRoute` wrapper. The quest data model itself (`types/quest.ts`,
`app/models.py`'s `Quest`) did not change at all.

## Verified while writing this module

See this module's root [`README.md`](../../README.md) for the full, honest
account of what was verified against a real running PostgreSQL instance
versus hand-verified.
