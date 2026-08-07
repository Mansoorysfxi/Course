# QuestLog API — backend (Module 08: gains a real test suite)

This is Module 07's finished, authenticated FastAPI backend (real
signup/login/JWT auth, every quest route protected and owner-scoped),
copied forward unchanged. **This module adds a real, passing pytest test
suite** (`tests/` — 31 tests: `test_security.py`, `test_auth.py`,
`test_quests.py`), plus `ruff` for linting/formatting. See
[`../../../lessons/`](../../../lessons/) for this module's full teaching
material (especially
[`05-testing-fastapi-endpoints.md`](../../../lessons/05-testing-fastapi-endpoints.md)
and
[`06-testing-with-a-database.md`](../../../lessons/06-testing-with-a-database.md)),
and [`../../BRIEF.md`](../../BRIEF.md) for this module's complete
capstone brief. For the auth/JWT material itself (unchanged since
Module 07), see `module-07-auth-security/lessons/`.

## Running the tests

```bash
pip install -r requirements-dev.txt
python -m pytest -v          # expect: 31 passed
ruff check app tests          # expect: All checks passed!
ruff format --check app tests # expect: N files already formatted
```

## Stack (verified while writing this module, August 2026)

| Tool | Version | Source |
|---|---|---|
| FastAPI | 0.141.1 | unchanged from Module 06 |
| Uvicorn | 0.52.1 | unchanged from Module 06 |
| Pydantic | 2.13.4 | unchanged from Module 06 |
| PostgreSQL | 18.x (18.4 at time of writing) | unchanged from Module 06 |
| SQLAlchemy | 2.0.51 | unchanged from Module 06 |
| Alembic | 1.19.0 | unchanged from Module 06 |
| asyncpg | 0.31.0 | unchanged from Module 06 |
| **bcrypt** | **5.0.0** | `https://pypi.org/pypi/bcrypt/json` — password hashing, used directly (not via `passlib`, confirmed unmaintained — see lessons/00-setup.md's header for the full research) |
| **PyJWT** | **2.13.0** | `https://pypi.org/pypi/PyJWT/json` — JWT encode/decode (not `python-jose`, confirmed abandoned by FastAPI's own maintainers) |
| **pydantic-settings** | **2.14.2** | `https://pypi.org/pypi/pydantic-settings/json` — typed settings from environment variables / `.env` |
| **python-multipart** | **0.0.32** | `https://pypi.org/pypi/python-multipart/json` — required by FastAPI's `OAuth2PasswordRequestForm` (form-data parsing) |
| **email-validator** | **2.3.0** | `https://pypi.org/pypi/email-validator/json` — backs Pydantic's `EmailStr` |
| Python | 3.14.x | same interpreter set up in Module 01 |

## Project structure

```
app/
├── main.py            — creates FastAPI(), CORS middleware (settings-driven), lifespan seeding, includes auth + quests routers
├── config.py           — pydantic-settings Settings (DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, CORS_ORIGINS)
├── security.py           — NEW: hash_password/verify_password (bcrypt), create_access_token/decode_access_token (PyJWT)
├── database.py             — the async engine, session factory, declarative Base, get_db() dependency (unchanged)
├── db_models.py              — SQLAlchemy ORM classes: User (now with hashed_password), QuestLine, Quest
├── models.py                  — Pydantic API models, now including UserCreate / UserPublic / Token
├── repository.py                — every real database query, now with get_user_by_email/get_user_by_id/create_user, and every quest query scoped by owner_id
├── dependencies.py                — DbSession, NEW: oauth2_scheme, get_current_user, CurrentUser; get_quest_or_404 now owner-scoped
└── routers/
    ├── auth.py                       — NEW: POST /api/auth/signup, POST /api/auth/login, GET /api/auth/me
    └── quests.py                      — every /api/quests route, now requiring CurrentUser and owner-scoped
alembic/
└── versions/
    ├── ..._initial_schema_users_quest_lines_quests.py — Module 06's migration, unchanged
    └── ..._add_hashed_password_to_users.py              — NEW: adds users.hashed_password
.env.example            — NEW: template for the required .env (never commit the real .env)
requirements.txt
```

## Running this project

**1. PostgreSQL running, with a fresh `questlog` database** — this
module's [`lessons/00-setup.md`](../../../lessons/00-setup.md) has you
drop and recreate the database from Module 06, specifically so this
module's new "add a NOT NULL column" migration can stay simple (see that
migration file's own docstring for why).

**2. Create the venv, install dependencies, and configure `.env`:**

```bash
cd module-08-testing-and-quality/project/questlog/backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste the output into .env's SECRET_KEY
```

**3. Apply migrations:**

```bash
alembic upgrade head
```

**4. Run the API:**

```bash
uvicorn app.main:app --reload
```

On first startup, `seed_if_empty()` (see `app/repository.py`) creates one
demo account and five starter quests owned by it:

- Email: `player@questlog.local`
- Password: `dragon-slayer-1`

Then visit `http://127.0.0.1:8000/docs` — use the "Authorize" button
(fill in the demo credentials above) to try protected routes directly
from the interactive docs — or:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -d "username=player@questlog.local&password=dragon-slayer-1"
```

**To run this alongside the frontend** (`../frontend/`), see this
module's `lessons/00-setup.md` — two terminals, one running this backend
on port `8000`, one running `npm run dev` in `../frontend/` on port
`5173`.

## Routes

| Method | Path | Auth required? | Notes |
|---|---|---|---|
| `POST` | `/api/auth/signup` | No | Create an account. `201` with the new account (never a token). `400` if the email is already registered. |
| `POST` | `/api/auth/login` | No | Form-encoded (`username`=email, `password`). Returns `{"access_token", "token_type"}`. `401` on bad credentials. |
| `GET` | `/api/auth/me` | **Yes** | Returns the account the current token belongs to. |
| `GET` | `/api/quests` | **Yes** | List *your* quests. Optional query params: `done`, `priority`, `quest_line`. |
| `GET` | `/api/quests/stats` | **Yes** | Per-quest-line totals for *your* quests only. |
| `GET` | `/api/quests/{quest_id}` | **Yes** | `404` if it doesn't exist, or belongs to someone else — deliberately never `403`, see `app/repository.py`'s `get_quest` docstring. |
| `POST` | `/api/quests` | **Yes** | Creates a quest owned by the current user. |
| `PATCH` | `/api/quests/{quest_id}` | **Yes** | Only affects a quest you own. |
| `DELETE` | `/api/quests/{quest_id}` | **Yes** | Only affects a quest you own. |

Every "Yes" above means: no `Authorization: Bearer <token>` header, or an
invalid/expired one, gets a `401` before this backend's own route code
ever runs.

## Testing it

Module 07 exercised every route above by hand, with `curl` and FastAPI's
`/docs` "Authorize" flow, against a real, running PostgreSQL instance.
**This module (08) replaces that manual process with a real, automated
test suite** (`tests/` — 31 tests, all passing, run against a temporary
in-memory SQLite database, not the real Postgres instance — see
`lessons/06-testing-with-a-database.md` for exactly why and the honest
trade-off involved): signup, login (correct and incorrect credentials),
`/me`, and the full quest CRUD set, including the exact
"confirming a second account cannot see or modify the first account's
quests" check Module 07 did by hand, now checked automatically, every
time, in milliseconds. See the module's own root `README.md` and
`project/BRIEF.md` for the full, honest account of what was verified.
