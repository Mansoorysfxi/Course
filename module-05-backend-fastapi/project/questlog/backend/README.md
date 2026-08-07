# QuestLog API — backend (Module 05)

The FastAPI backend built in this module. In-memory only (a Python `dict`
in `app/store.py`) -- every quest disappears when this process stops; that
is deliberate, see [`../../../lessons/08-building-the-questlog-api.md`](../../../lessons/08-building-the-questlog-api.md).
Module 06 adds real PostgreSQL persistence to this exact codebase.

## Stack (verified while writing this module, August 2026)

| Tool | Version | Source |
|---|---|---|
| FastAPI | 0.141.1 | `https://pypi.org/pypi/fastapi/json` |
| Uvicorn | 0.52.1 | `https://pypi.org/pypi/uvicorn/json` |
| Pydantic | 2.13.4 | `https://pypi.org/pypi/pydantic/json` (installed automatically as a FastAPI dependency; pinned explicitly too since this codebase imports it directly) |
| Python | 3.14.x | Same interpreter installed in Module 01 |

## Running this project

```bash
cd module-05-backend-fastapi/project/questlog/backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then visit `http://127.0.0.1:8000/docs`, or:

```bash
curl http://127.0.0.1:8000/api/quests
```

**To run this alongside the frontend** (`../frontend/`), see this module's
[`lessons/00-setup.md`](../../../lessons/00-setup.md), Step 6 — two
terminals, one running this backend on port `8000`, one running
`npm run dev` in `../frontend/` on port `5173`.

## Project structure

```
app/
├── main.py            — creates FastAPI(), CORS middleware, includes the router, seeds the store on startup
├── models.py           — Quest / QuestCreate / QuestUpdate / QuestLineStats Pydantic models (camelCase aliases matching the frontend)
├── store.py             — the in-memory "database": a dict, plus create/read/update/delete/stats functions
├── dependencies.py     — get_quest_or_404
└── routers/
    └── quests.py         — every /api/quests route
```

## Routes

| Method | Path | Notes |
|---|---|---|
| `GET` | `/api/quests` | List all quests. Optional query params: `done`, `priority`, `quest_line`. |
| `GET` | `/api/quests/stats` | Per-quest-line totals (`{questLine, total, done}`). |
| `GET` | `/api/quests/{quest_id}` | Get one quest. `404` if it doesn't exist. |
| `POST` | `/api/quests` | Create a quest. `201` on success. |
| `PATCH` | `/api/quests/{quest_id}` | Partially update a quest — only send the fields you're changing. |
| `DELETE` | `/api/quests/{quest_id}` | Delete a quest. `204` on success. |

## Testing it

Every route above was tested, while building this module, with both `curl`
and Swagger UI's "Try it out" (`/docs`) — see Lesson 08 for the exact
commands. A quick smoke test:

```bash
curl http://127.0.0.1:8000/api/quests
curl -i -X POST http://127.0.0.1:8000/api/quests \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Quest", "description": "...", "priority": "low", "questLine": "Testing"}'
```
