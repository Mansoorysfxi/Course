# QuestLog API — backend (Module 06)

The FastAPI backend, now backed by real **PostgreSQL** persistence via
**SQLAlchemy 2.0** (async) and **Alembic** migrations. Every quest now
survives a restart — the opposite of Module 05's `app/store.py`, which was a
plain Python `dict` that reset to nothing every time the process stopped.
See [`../../../lessons/06-sqlalchemy-with-fastapi.md`](../../../lessons/06-sqlalchemy-with-fastapi.md)
for exactly what changed and why, and
[`../../BRIEF.md`](../../BRIEF.md) for this module's full capstone brief.

## Stack (verified while writing this module, August 2026)

| Tool | Version | Source |
|---|---|---|
| FastAPI | 0.141.1 | unchanged from Module 05 |
| Uvicorn | 0.52.1 | unchanged from Module 05 |
| Pydantic | 2.13.4 | unchanged from Module 05 |
| PostgreSQL | 18.x (18.4 at time of writing) | `postgresql.org` release notes; PostgreSQL 19 is in beta, not yet stable — this course targets 18 |
| SQLAlchemy | 2.0.51 | `https://pypi.org/pypi/sqlalchemy/json` |
| Alembic | 1.19.0 | installed and confirmed via `pip install alembic` in this environment |
| asyncpg | 0.31.0 | `https://pypi.org/pypi/asyncpg/json` — the async PostgreSQL driver `postgresql+asyncpg://` URLs use |
| Python | 3.14.x | same interpreter set up in Module 01 |

## Project structure

```
app/
├── main.py            — creates FastAPI(), CORS middleware, lifespan-based startup seeding
├── config.py           — reads DATABASE_URL from the environment
├── database.py          — the async engine, session factory, declarative Base, get_db() dependency
├── db_models.py          — SQLAlchemy ORM classes: User, QuestLine, Quest (the real tables)
├── models.py              — Pydantic API models: Quest / QuestCreate / QuestUpdate / QuestLineStats (unchanged contract)
├── repository.py           — every real database query (replaces Module 05's store.py)
├── dependencies.py          — DbSession alias, get_quest_or_404
└── routers/
    └── quests.py              — every /api/quests route (same routes as Module 05, now async + DB-backed)
alembic/
├── env.py               — wires Alembic to this project's Base.metadata and DATABASE_URL
└── versions/
    └── ..._initial_schema_users_quest_lines_quests.py — the first migration
alembic.ini
requirements.txt
```

## Running this project

**1. Make sure PostgreSQL is running and the `questlog` database/user exist**
— see this module's [`lessons/00-setup.md`](../../../lessons/00-setup.md)
if you haven't done this yet.

**2. Create the venv and install dependencies:**

```bash
cd module-06-databases/project/questlog/backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

**3. Apply migrations (creates the actual tables — the app itself never does this):**

```bash
alembic upgrade head
```

**4. Run the API:**

```bash
uvicorn app.main:app --reload
```

On first startup, `seed_if_empty()` (see `app/repository.py`) inserts a
default user and five starter quests — but only into tables that already
exist, which is exactly why step 3 must happen before step 4.

Then visit `http://127.0.0.1:8000/docs`, or:

```bash
curl http://127.0.0.1:8000/api/quests
```

**To run this alongside the frontend** (`../frontend/`), see this module's
`lessons/00-setup.md`, Step 6 — two terminals, one running this backend on
port `8000`, one running `npm run dev` in `../frontend/` on port `5173`.
The frontend's API contract is byte-for-byte identical to Module 05's — it
needs no changes at all to work against this database-backed version.

## Routes

Identical paths, methods, and JSON shapes to Module 05 — only *how* each
route gets its data changed (real SQL instead of dict operations):

| Method | Path | Notes |
|---|---|---|
| `GET` | `/api/quests` | List quests. Optional query params: `done`, `priority`, `quest_line`. |
| `GET` | `/api/quests/stats` | Per-quest-line totals (`{questLine, total, done}`), computed with a real `GROUP BY`. |
| `GET` | `/api/quests/{quest_id}` | Get one quest. `404` if it doesn't exist. |
| `POST` | `/api/quests` | Create a quest. `201` on success. Creates a new `quest_lines` row automatically the first time a given quest line name is used. |
| `PATCH` | `/api/quests/{quest_id}` | Partially update a quest — only send the fields you're changing. |
| `DELETE` | `/api/quests/{quest_id}` | Delete a quest. `204` on success. |

## Testing it

Every route above was exercised with `curl` against a real, running
PostgreSQL instance while building this module — list, get, create
(including the get-or-create quest-line logic), update, delete, `/stats`,
and deliberate `404`/`422` cases. See
[`lessons/07-alembic-migrations.md`](../../../lessons/07-alembic-migrations.md)
and [`lessons/08-nosql-overview.md`](../../../lessons/08-nosql-overview.md)
for the surrounding concepts, and the module's own root `README.md` for the
exact, honest account of what was verified against a real database versus
what was hand-verified.
