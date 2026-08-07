# QuestLog — Module 09 (deployed to a real VPS, manually)

Per `RUNNING_PROJECT.md`, this folder is Module 08's finished, tested
`questlog/` copied forward **byte-for-byte unchanged** —
`backend/app/`, `frontend/src/`, both test suites, `ruff`/`prettier`/
`pre-commit` are all identical to Module 08's. **This module adds no
QuestLog feature, route, page, or database column at all** — it changes
only *where and how* this exact application runs. Everything new this
module lives in the new `deploy/` folder below, alongside the
application rather than inside it.

```
project/questlog/
├── frontend/                  — completely unchanged from Module 08
├── backend/                   — completely unchanged from Module 08
├── .pre-commit-config.yaml    — completely unchanged from Module 08
└── deploy/                    — NEW this module:
    ├── questlog-backend.service        — the real systemd unit file for the backend
    ├── nginx/questlog.conf              — the real Nginx reverse-proxy + static-serving config
    ├── backend.env.production.example    — production .env template (never commit a real one)
    └── DEPLOY_RUNBOOK.md                   — condensed, copy-paste-in-order deploy checklist
```

See [`../../lessons/07-deploying-questlog-part1-server-and-backend.md`](../../lessons/07-deploying-questlog-part1-server-and-backend.md)
and
[`../../lessons/08-deploying-questlog-part2-frontend-and-going-live.md`](../../lessons/08-deploying-questlog-part2-frontend-and-going-live.md)
for the full, explained capstone walkthrough these `deploy/` files
support, and [`../BRIEF.md`](../BRIEF.md) for this module's capstone
deliverables.

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
`POST /api/auth/login` — see [`lessons/00-setup.md`](../lessons/00-setup.md)
and both READMEs' "Running this project" sections for the exact steps.

## Running both together, locally (unchanged from Module 08)

**Terminal 1 — backend:**
```bash
cd module-09-linux-networking-servers/project/questlog/backend
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
cd module-09-linux-networking-servers/project/questlog/frontend
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

## Deploying this to a real server

This module's actual point is not running QuestLog locally (already
true since Module 04/05) — it's running this exact codebase on a real,
internet-reachable Ubuntu server, by hand. See `deploy/` in this same
folder and this module's
[`lessons/07-deploying-questlog-part1-server-and-backend.md`](../../lessons/07-deploying-questlog-part1-server-and-backend.md)
and
[`lessons/08-deploying-questlog-part2-frontend-and-going-live.md`](../../lessons/08-deploying-questlog-part2-frontend-and-going-live.md)
for the complete, explained walkthrough, and
[`../BRIEF.md`](../BRIEF.md) for this module's capstone deliverables.

## Inherited from Module 08, unchanged

Every number below was produced by Module 08 actually running the
command shown, not estimated — see that module's own `README.md` and
`project/BRIEF.md` for the full, honest account, including which parts
(the backend test database, specifically) deliberately use SQLite
instead of a real running PostgreSQL instance, and why
(`module-08-testing-and-quality/lessons/06-testing-with-a-database.md`).
None of this module's deployment work changed any of it.
